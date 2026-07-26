from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from src.analysis import SENSITIVITY_PARAMETERS, combined_improvement_frontier, one_way_thresholds
from src.model import (
    calculate_lcoe, specific_mass_from_specific_power,
    specific_power_from_specific_mass, validate_construction_spend_profile,
)
from src.parameters import load_parameters, reference_values
from src.validation import validate_parameters, validate_reference_case
from src.web_payload import build_web_payload
from src.utils import write_csv_dicts


ROOT = Path(__file__).resolve().parents[1]
OBSOLETE_IDENTIFIER = "specific_mass_kg_per_kw_" + "space_power"


class V2ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.params = load_parameters(ROOT / "data/sbsp_parameters.csv")
        cls.reference = reference_values(cls.params)

    def test_01_specific_power_reciprocal(self) -> None:
        self.assertAlmostEqual(specific_mass_from_specific_power(0.67), 1.4925373134328357)
        self.assertAlmostEqual(specific_power_from_specific_mass(1 / 0.67), 0.67)

    def test_02_two_gw_mass_regression(self) -> None:
        case = dict(self.reference)
        case["system_specific_mass_kg_per_kw_delivered"] = 1 / 0.67
        result = calculate_lcoe(case)
        self.assertAlmostEqual(result.orbital_mass_kg, 2_000_000 / 0.67, delta=1e-6)
        self.assertAlmostEqual(result.orbital_mass_kg / 1000, 2985.0746268656717, places=9)

    def test_03_mass_is_not_divided_by_efficiency(self) -> None:
        masses = []
        for solar in (0.2, 0.35, 0.8):
            case = dict(self.reference)
            case["solar_conversion_efficiency"] = solar
            case["system_specific_mass_kg_per_kw_delivered"] = 1.5
            masses.append(calculate_lcoe(case).orbital_mass_kg)
        self.assertEqual(masses, [3_000_000.0, 3_000_000.0, 3_000_000.0])

    def test_04_computed_efficiency_is_product_of_five_stages(self) -> None:
        result = calculate_lcoe(self.reference)
        expected = math.prod(self.reference[name] for name in (
            "solar_conversion_efficiency", "dc_to_rf_efficiency", "transmission_efficiency",
            "rectenna_conversion_efficiency", "grid_conversion_efficiency",
        ))
        self.assertAlmostEqual(result.end_to_end_efficiency, expected, places=15)
        self.assertNotIn("end_to_end_efficiency", self.params)

    def test_05_backward_stage_power_calculation(self) -> None:
        r = calculate_lcoe(self.reference)
        e = r.energy_chain_power_w
        self.assertAlmostEqual(e["delivered_grid_ac_power_w"], 2e9)
        self.assertAlmostEqual(e["rectenna_dc_power_w"] * self.reference["grid_conversion_efficiency"], e["delivered_grid_ac_power_w"])
        self.assertAlmostEqual(e["incident_rf_power_w"] * self.reference["rectenna_conversion_efficiency"], e["rectenna_dc_power_w"])
        self.assertAlmostEqual(e["emitted_rf_power_w"] * self.reference["transmission_efficiency"], e["incident_rf_power_w"])
        self.assertAlmostEqual(e["space_dc_bus_power_w"] * self.reference["dc_to_rf_efficiency"], e["emitted_rf_power_w"])
        self.assertAlmostEqual(e["incident_solar_power_w"] * self.reference["solar_conversion_efficiency"], e["space_dc_bus_power_w"])

    def test_06_hardware_costs_use_their_rated_stages(self) -> None:
        r = calculate_lcoe(self.reference)
        e, c = r.energy_chain_power_w, r.capex_components_gbp
        self.assertAlmostEqual(c["space_generation_hardware"], self.reference["space_generation_hardware_cost_gbp_per_w_dc"] * e["space_dc_bus_power_w"])
        self.assertAlmostEqual(c["wireless_power_transmitter"], self.reference["transmitter_cost_gbp_per_w_rf_emitted"] * e["emitted_rf_power_w"])
        self.assertAlmostEqual(c["rectenna"], self.reference["rectenna_cost_gbp_per_w_delivered"] * e["delivered_grid_ac_power_w"])
        self.assertAlmostEqual(c["grid_connection"], self.reference["grid_connection_cost_gbp_per_kw_delivered"] * self.reference["delivered_capacity_mw"] * 1000)

    def test_07_launch_pricing_modes_are_mutually_exclusive(self) -> None:
        per_kg = calculate_lcoe(self.reference, launch_pricing_mode="per_kg")
        per_flight = calculate_lcoe(self.reference, launch_pricing_mode="per_flight")
        expected_kg = per_kg.orbital_mass_kg * self.reference["launch_cost_gbp_per_kg_to_staging_orbit"]
        expected_flight = per_flight.required_launches * self.reference["launch_price_gbp_per_flight"]
        self.assertEqual(per_kg.capex_components_gbp["launch_to_staging_orbit"], expected_kg)
        self.assertEqual(per_flight.capex_components_gbp["launch_to_staging_orbit"], expected_flight)
        self.assertNotEqual(per_kg.capex_components_gbp["launch_to_staging_orbit"], expected_kg + expected_flight)
        with self.assertRaises(ValueError):
            calculate_lcoe(self.reference, launch_pricing_mode="both")

    def test_08_launch_count_rounds_up(self) -> None:
        case = dict(self.reference)
        case["delivered_capacity_mw"] = 1
        case["system_specific_mass_kg_per_kw_delivered"] = 85.001
        case["effective_payload_kg_per_flight"] = 100_000
        case["payload_utilisation_fraction"] = 0.85
        self.assertEqual(calculate_lcoe(case).required_launches, 2)

    def test_09_component_specific_replacement_boundaries(self) -> None:
        r = calculate_lcoe(self.reference)
        c = r.capex_components_gbp
        expected_space = sum(c[name] for name in (
            "space_generation_hardware", "wireless_power_transmitter", "launch_to_staging_orbit",
            "orbit_transfer_to_operational_orbit", "in_orbit_assembly_and_deployment",
        ))
        expected_ground = c["rectenna"] + c["grid_connection"]
        expected_fixed = c["space_generation_hardware"] + c["wireless_power_transmitter"] + expected_ground
        self.assertEqual(r.space_replacement_eligible_cost_base_gbp, expected_space)
        self.assertEqual(r.ground_replacement_eligible_cost_base_gbp, expected_ground)
        self.assertEqual(r.fixed_opex_eligible_asset_base_gbp, expected_fixed)
        self.assertNotIn(r.programme_contingency_gbp, (expected_space, expected_ground, expected_fixed))

    def test_10_construction_profile_must_sum_to_one(self) -> None:
        self.assertEqual(validate_construction_spend_profile([.25] * 4, 4), (.25, .25, .25, .25))
        with self.assertRaises(ValueError):
            validate_construction_spend_profile([.2] * 4, 4)
        with self.assertRaises(ValueError):
            calculate_lcoe(self.reference, construction_spend_profile=[.3, .3, .3, .05])

    def test_11_dcf_and_crf_converge_in_limiting_case(self) -> None:
        case = dict(self.reference)
        case.update({
            "construction_duration_years": 0, "annual_output_degradation_fraction": 0,
            "decommissioning_cost_fraction_initial_capex": 0, "residual_value_fraction_initial_capex": 0,
        })
        r = calculate_lcoe(case)
        self.assertAlmostEqual(r.lcoe_gbp_per_mwh, r.crf_reconciliation_lcoe_gbp_per_mwh, places=10)

    def test_12_zero_rate_handling(self) -> None:
        case = dict(self.reference)
        case.update({
            "construction_duration_years": 0, "real_discount_rate": 0,
            "annual_output_degradation_fraction": 0, "decommissioning_cost_fraction_initial_capex": 0,
            "residual_value_fraction_initial_capex": 0,
        })
        r = calculate_lcoe(case)
        self.assertTrue(math.isfinite(r.lcoe_gbp_per_mwh))
        self.assertAlmostEqual(r.lcoe_gbp_per_mwh, r.crf_reconciliation_lcoe_gbp_per_mwh, places=10)

    def test_13_invalid_inputs_are_rejected(self) -> None:
        for name, value in (("solar_conversion_efficiency", 0), ("capacity_factor", 1.1), ("operating_lifetime_years", 0), ("real_discount_rate", 1)):
            case = dict(self.reference); case[name] = value
            with self.subTest(name=name), self.assertRaises(ValueError):
                calculate_lcoe(case)

    def test_14_python_and_browser_calculations_match(self) -> None:
        bundled_node = Path("/Users/robot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
        node = shutil.which("node") or (str(bundled_node) if bundled_node.exists() else None)
        self.assertIsNotNone(node, "Node.js is required for browser-parity testing.")
        script = "const fs=require('fs');const m=require('./html/model.js');const p=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(m.calculateLcoe(p)));"
        completed = subprocess.run([node, "-e", script], cwd=ROOT, input=json.dumps(self.reference), text=True, capture_output=True, check=True)
        browser = json.loads(completed.stdout)
        python = calculate_lcoe(self.reference)
        for key, value in (("lcoe_gbp_per_mwh", python.lcoe_gbp_per_mwh), ("end_to_end_efficiency", python.end_to_end_efficiency), ("orbital_mass_kg", python.orbital_mass_kg), ("discounted_lifetime_cost_gbp", python.discounted_lifetime_cost_gbp), ("discounted_lifetime_energy_mwh", python.discounted_lifetime_energy_mwh)):
            self.assertAlmostEqual(browser[key], value, delta=max(1e-8, abs(value) * 1e-12), msg=key)

    def test_15_bilingual_payload_has_numerical_parity(self) -> None:
        with self.subTest("metadata"):
            for parameter in self.params.values():
                self.assertTrue(parameter.display_name)
                self.assertTrue(parameter.display_name_zh)
                self.assertTrue(parameter.denominator_definition)
                self.assertTrue(parameter.denominator_definition_zh)
                self.assertTrue(parameter.notes)
                self.assertTrue(parameter.notes_zh)
        self.assertEqual(validate_parameters(self.params), [])
        self.assertEqual(validate_reference_case(self.reference), [])

    def test_16_obsolete_mass_identifier_absent_from_active_outputs(self) -> None:
        active = [ROOT / "src", ROOT / "analysis", ROOT / "html", ROOT / "report", ROOT / "data/processed", ROOT / "data/sbsp_parameters.csv", ROOT / "data/parameter_evidence.csv", ROOT / "README.md"]
        hits = []
        for item in active:
            paths = item.rglob("*") if item.is_dir() else [item]
            for path in paths:
                if path.is_file() and path.suffix.lower() in {".py", ".js", ".html", ".md", ".csv", ".txt"}:
                    if OBSOLETE_IDENTIFIER in path.read_text(encoding="utf-8", errors="ignore"):
                        hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_17_full_generation_pipeline(self) -> None:
        completed = subprocess.run([sys.executable, "analysis/run_full_analysis.py"], cwd=ROOT, text=True, capture_output=True, timeout=240)
        self.assertEqual(completed.returncode, 0, completed.stdout + "\n" + completed.stderr)
        for path in (
            ROOT / "html/model_data.js", ROOT / "report/final_report_EN.md",
            ROOT / "report/final_report_zh.md", ROOT / "report/verification_note.md",
            ROOT / "data/processed/reference_cash_flow.csv", ROOT / "data/processed/reference_energy_chain.csv",
        ):
            self.assertTrue(path.exists() and path.stat().st_size > 0, path)

    def test_18_generated_csv_float_serialisation_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stable.csv"
            write_csv_dicts(path, [
                {"metric": "macos", "value": 210.5766723490313},
                {"metric": "linux", "value": 210.57667234903133},
            ], ["metric", "value"])
            self.assertEqual(path.read_text(encoding="utf-8"), (
                "metric,value\n"
                "macos,210.576672349031\n"
                "linux,210.576672349031\n"
            ))

    def test_19_reports_distinguish_assumptions_from_external_evidence(self) -> None:
        reports = {
            "en": (ROOT / "report/final_report_EN.md").read_text(encoding="utf-8"),
            "zh": (ROOT / "report/final_report_zh.md").read_text(encoding="utf-8"),
        }
        for language, report in reports.items():
            with self.subTest(language=language):
                self.assertLessEqual(report.count("ASSUMPTION_THIS_STUDY"), 1)
                for source_id in (
                    "DESNZ_SBSP_2025", "UK_SBSP_2021_PHASE2", "UK_SBSP_2021_ANNEX_B",
                    "NASA_OTPS_SBSP_2024", "CALTECH_SBSP_2022",
                    "DESNZ_EGC_2025_ANNEX_A", "BEIS_EGC_2020",
                ):
                    self.assertIn(source_id, report)
                self.assertIn("https://", report)

    def test_20_html_preserves_responsive_interactive_cost_map(self) -> None:
        html = (ROOT / "html/index.html").read_text(encoding="utf-8")
        for token in (
            "SBSPModel.calculateLcoe",
            "benchmark-card-leaders",
            "input[type=\"range\"]::-webkit-slider-runnable-track",
            "@media (max-width:820px)",
            ".workspace { display:block;",
            "Stage-resolved energy chain",
            "Discounted lifecycle-cost present value",
            "scenario-compare",
            "mix-stack",
            "impact-point best",
            "programme_contingency:result.programme_contingency_gbp",
        ):
            self.assertIn(token, html)
        self.assertNotIn("BASELINE_LCOE = 429", html)


if __name__ == "__main__":
    unittest.main()
