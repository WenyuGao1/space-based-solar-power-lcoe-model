from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.analysis import (
    SENSITIVITY_PARAMETERS,
    alternative_combined_pathways,
    combined_improvement_frontier,
    cost_driver_importance,
    launch_efficiency_frontier,
    one_way_thresholds,
    sensitivity_curve,
)
from src.model import calculate_lcoe
from src.parameters import load_parameters, numeric_benchmark_rows, reference_values
from src.plots import _reference_lcoe_on_curve
from src.reporting import build_markdown_report
from src.reporting_zh import build_markdown_report_zh
from src.utils import read_csv_dicts
from src.validation import (
    validate_analysis_results,
    validate_csv_structure,
    validate_markdown_images,
    validate_official_generation_extract,
    validate_parameters,
    validate_pdf_documents,
    validate_raw_workbooks,
    validate_reference_case,
    validate_source_integrity,
)


ROOT = Path(__file__).resolve().parents[1]


class ModelAndEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.params = load_parameters(ROOT / "data/sbsp_parameters.csv")
        cls.reference = reference_values(cls.params)
        cls.thresholds = one_way_thresholds(cls.reference, cls.params)
        cls.importance = cost_driver_importance(cls.reference, cls.params)
        cls.launch_frontier = launch_efficiency_frontier(cls.reference, cls.params)
        cls.combined_frontier = combined_improvement_frontier(cls.reference, cls.params)
        cls.alternative_frontiers = alternative_combined_pathways(cls.reference, cls.params)
        cls.generation_rows = numeric_benchmark_rows(ROOT / "data/uk_generation_costs.csv")
        cls.system_rows = numeric_benchmark_rows(ROOT / "data/uk_system_adjusted_costs.csv")
        cls.source_rows = read_csv_dicts(ROOT / "data/source_registry.csv")
        cls.evidence_rows = read_csv_dicts(ROOT / "data/parameter_evidence.csv")
        cls.assumption_rows = read_csv_dicts(ROOT / "data/assumptions.csv")
        cls.external_study_rows = read_csv_dicts(ROOT / "data/external_sbsp_studies.csv")

    def test_reference_case_reconciles(self) -> None:
        self.assertEqual(validate_parameters(self.params), [])
        self.assertEqual(validate_reference_case(self.reference), [])
        result = calculate_lcoe(self.reference)
        self.assertAlmostEqual(result.lcoe_gbp_per_mwh, 429.25078050818814, places=6)
        self.assertAlmostEqual(result.initial_capex_gbp, 72.6e9, delta=1.0)

    def test_specific_mass_thresholds_are_root_solved(self) -> None:
        rows = one_way_thresholds(self.reference, self.params, targets=[150, 120, 100])
        matches = {
            int(row["target_lcoe_gbp_per_mwh"]): row
            for row in rows
            if row["parameter"] == "specific_mass_kg_per_kw_space_power"
        }
        expected = {
            150: 1.2841698053748107,
            120: 0.8849769879513801,
            100: 0.6188484430024261,
        }
        for target, expected_threshold in expected.items():
            threshold = float(matches[target]["threshold_value"])
            self.assertAlmostEqual(threshold, expected_threshold, places=11)
            case = dict(self.reference)
            case["specific_mass_kg_per_kw_space_power"] = threshold
            self.assertAlmostEqual(calculate_lcoe(case).lcoe_gbp_per_mwh, target, places=9)
            self.assertEqual(matches[target]["solution_method"], "monotonic bisection")

    def test_specific_mass_lower_targets_are_not_reached_one_way(self) -> None:
        rows = one_way_thresholds(self.reference, self.params, targets=[80, 60])
        mass_rows = [
            row
            for row in rows
            if row["parameter"] == "specific_mass_kg_per_kw_space_power"
        ]
        self.assertEqual([row["threshold_value"] for row in mass_rows], [None, None])

    def test_explicit_empty_target_lists_remain_empty(self) -> None:
        self.assertEqual(one_way_thresholds(self.reference, self.params, targets=[]), [])
        self.assertEqual(launch_efficiency_frontier(self.reference, self.params, target_values=[]), [])
        self.assertEqual(launch_efficiency_frontier(self.reference, self.params, efficiencies=[]), [])

    def test_one_way_scope_is_every_non_scale_input(self) -> None:
        self.assertEqual(set(SENSITIVITY_PARAMETERS), set(self.params) - {"delivered_capacity_mw"})
        self.assertEqual(len(SENSITIVITY_PARAMETERS), 16)

    def test_delivered_capacity_is_scale_neutral(self) -> None:
        lcoes = []
        for capacity in (500.0, 2000.0, 5000.0):
            case = dict(self.reference)
            case["delivered_capacity_mw"] = capacity
            lcoes.append(calculate_lcoe(case).lcoe_gbp_per_mwh)
        self.assertAlmostEqual(lcoes[0], lcoes[1], places=10)
        self.assertAlmostEqual(lcoes[1], lcoes[2], places=10)

    def test_launch_efficiency_frontier_is_root_solved(self) -> None:
        rows = launch_efficiency_frontier(
            self.reference,
            self.params,
            target_values=[150, 100],
            efficiencies=[0.25, 0.35],
        )
        keyed = {
            (float(row["end_to_end_efficiency"]), int(row["target_lcoe_gbp_per_mwh"])): row
            for row in rows
        }
        expected = {
            (0.25, 150): 109.11194811142602,
            (0.35, 100): 64.3700853913591,
        }
        for key, expected_threshold in expected.items():
            row = keyed[key]
            threshold = float(row["max_launch_cost_gbp_per_kg"])
            self.assertAlmostEqual(threshold, expected_threshold, places=7)
            case = dict(self.reference)
            case["end_to_end_efficiency"] = key[0]
            case["launch_cost_gbp_per_kg"] = threshold
            self.assertAlmostEqual(calculate_lcoe(case).lcoe_gbp_per_mwh, key[1], places=9)

    def test_curve_reference_markers_use_reference_values(self) -> None:
        reference_lcoe = calculate_lcoe(self.reference).lcoe_gbp_per_mwh
        for name in SENSITIVITY_PARAMETERS:
            parameter = self.params[name]
            rows = sensitivity_curve(self.reference, parameter, points=101)
            plotted_reference = _reference_lcoe_on_curve(rows, parameter.reference_value)
            self.assertAlmostEqual(plotted_reference, reference_lcoe, delta=0.25, msg=name)

    def test_all_frontiers_and_one_way_roots_validate(self) -> None:
        self.assertEqual(
            validate_analysis_results(
                self.reference,
                self.params,
                SENSITIVITY_PARAMETERS,
                self.thresholds,
                self.launch_frontier,
                self.combined_frontier,
                self.alternative_frontiers,
            ),
            [],
        )

    def test_only_specific_mass_crosses_150_one_way(self) -> None:
        feasible = {
            str(row["parameter"])
            for row in self.thresholds
            if int(row["target_lcoe_gbp_per_mwh"]) == 150
            and row["threshold_value"] not in (None, "")
        }
        self.assertEqual(feasible, {"specific_mass_kg_per_kw_space_power"})

    def test_low_mass_slice_discloses_baseline_feasibility(self) -> None:
        row = next(
            row
            for row in self.alternative_frontiers
            if row["pathway"] == "low_mass_architecture_slice"
            and int(row["target_lcoe_gbp_per_mwh"]) == 150
        )
        self.assertEqual(row["status"], "already feasible at slice baseline")
        self.assertEqual(float(row["progress_fraction"]), 0.0)
        self.assertLessEqual(float(row["lcoe_gbp_per_mwh"]), 150.0)

    def test_raw_workbooks_are_valid_xlsx_containers(self) -> None:
        paths = [
            ROOT / "data/raw/GC20_Key_Data_and_Assumptions.xlsx",
            ROOT / "data/raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
        ]
        self.assertEqual(validate_raw_workbooks(paths), [])

    def test_official_generation_extract_reconciles_to_cells(self) -> None:
        self.assertEqual(
            validate_official_generation_extract(
                ROOT / "data/raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
                ROOT / "data/uk_generation_costs.csv",
            ),
            [],
        )

    def test_input_csvs_have_consistent_records(self) -> None:
        paths = [
            ROOT / "data/assumptions.csv",
            ROOT / "data/external_sbsp_studies.csv",
            ROOT / "data/parameter_evidence.csv",
            ROOT / "data/sbsp_parameters.csv",
            ROOT / "data/source_registry.csv",
            ROOT / "data/uk_generation_costs.csv",
            ROOT / "data/uk_system_adjusted_costs.csv",
        ]
        self.assertEqual(validate_csv_structure(paths), [])

    def test_all_source_links_resolve_to_registry(self) -> None:
        self.assertEqual(
            validate_source_integrity(
                ROOT / "data/source_registry.csv",
                [
                    ROOT / "data/assumptions.csv",
                    ROOT / "data/external_sbsp_studies.csv",
                    ROOT / "data/parameter_evidence.csv",
                    ROOT / "data/sbsp_parameters.csv",
                    ROOT / "data/uk_generation_costs.csv",
                    ROOT / "data/uk_system_adjusted_costs.csv",
                ],
            ),
            [],
        )

    def test_evidence_rows_disclose_limitations(self) -> None:
        with (ROOT / "data/parameter_evidence.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            self.assertTrue(row["evidence_role"].strip())
            self.assertTrue(row["limitations"].strip())
            self.assertTrue(row["evidence_role_zh"].strip())
            self.assertTrue(row["limitations_zh"].strip())

    def test_generated_reports_match_current_generator(self) -> None:
        with TemporaryDirectory() as temp_dir:
            en_path = Path(temp_dir) / "final_report_EN.md"
            zh_path = Path(temp_dir) / "final_report_zh.md"
            shared_args = (
                self.reference,
                self.params,
                self.generation_rows,
                self.system_rows,
                self.thresholds,
                self.importance,
                self.launch_frontier,
                self.combined_frontier,
                self.alternative_frontiers,
                self.source_rows,
                self.evidence_rows,
                self.assumption_rows,
                self.external_study_rows,
            )
            build_markdown_report(en_path, *shared_args)
            build_markdown_report_zh(zh_path, *shared_args)
            self.assertEqual(en_path.read_text(encoding="utf-8"), (ROOT / "report/final_report_EN.md").read_text(encoding="utf-8"))
            self.assertEqual(zh_path.read_text(encoding="utf-8"), (ROOT / "report/final_report_zh.md").read_text(encoding="utf-8"))

    def test_bilingual_reports_have_full_shared_structure(self) -> None:
        report_paths = [ROOT / "report/final_report_EN.md", ROOT / "report/final_report_zh.md"]
        self.assertEqual(validate_markdown_images(report_paths, expected_count=7), [])
        texts = [path.read_text(encoding="utf-8") for path in report_paths]
        for text in texts:
            for token in ("v1.2", "£429/MWh", "1.28", "0.88", "0.62", "26.5%", "31.8%", "36.1%", "41.1%", "47.4%"):
                self.assertIn(token, text)
            for source in self.source_rows:
                self.assertIn(source["source_id"], text)
            for locator in {row["locator"] for row in self.evidence_rows}:
                self.assertIn(locator, text)

    def test_markdown_reports_do_not_expose_internal_pagebreak_markers(self) -> None:
        for report_name in ("final_report_EN.md", "final_report_zh.md"):
            with self.subTest(report=report_name):
                text = (ROOT / "report" / report_name).read_text(encoding="utf-8")
                self.assertNotIn(
                    "[[PAGEBREAK]]",
                    text,
                    "Internal PDF layout markers must not be visible in GitHub Markdown.",
                )

    def test_chinese_report_table_2_is_localized_and_preserves_metric_caveat(self) -> None:
        text = (ROOT / "report/final_report_zh.md").read_text(encoding="utf-8")
        table_start = "表2. 本项目与所选既有空间太阳能研究的关系"
        table_end = "本项目可以公开说明的优势是："
        self.assertIn(table_start, text)
        self.assertIn(table_end, text)
        table_2 = text.split(table_start, 1)[1].split(table_end, 1)[0]

        retired_english_phrases = (
            "with a central/about",
            "30-year life",
            "20% hurdle",
            "commissioning case",
            "2024 GBP:",
            "FY2022 USD:",
            "per MWh baseline",
            "under combined favourable assumptions",
            "study-authored reference anchor",
            "root-solved conditional lines",
        )
        for phrase in retired_english_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, table_2)

        for study_label in (
            "英国空间太阳能二阶段经济研究（2021）",
            "英国小规模空间太阳能研究（2025年完成、2026年发布）",
            "NASA OTPS评估（2024）",
            "本项目（v1.2）",
        ):
            self.assertIn(study_label, table_2)

        comparison_paragraphs = [
            paragraph
            for paragraph in text.split("\n\n")
            if all(token in paragraph for token in ("批发", "合同", "LCOE", "系统调整"))
        ]
        self.assertTrue(
            comparison_paragraphs,
            "The Chinese report must identify the unlike electricity-cost metrics being compared.",
        )
        self.assertTrue(
            any(
                any(
                    warning in paragraph
                    for warning in ("不能直接比较", "不可直接比较", "不应直接比较", "不能直接等同", "不可直接等同")
                )
                for paragraph in comparison_paragraphs
            ),
            "The Chinese report must state that unlike cost metrics cannot be compared directly.",
        )

    def test_release_source_metadata_and_annex_a_links_are_exact(self) -> None:
        sources = {row["source_id"]: row for row in self.source_rows}
        expected_sources = {
            "DESNZ_EGC_2025": {
                "title": "Electricity generation costs 2025",
                "document_year": "2025",
                "publication_date": "2026-01-14",
                "landing_page_last_updated": "2026-03-18",
                "accessed_date": "2026-07-19",
            },
            "DESNZ_EGC_2025_ANNEX_A": {
                "title": "Annex A: Additional estimates and key assumptions 2025",
                "document_year": "2025",
                "publication_date": "2026-01-14",
                "document_revision_date": "2026-03-18",
                "accessed_date": "2026-07-19",
            },
            "UK_SBSP_2021_PHASE2": {
                "title": "Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility",
                "document_year": "2021",
                "publication_date": "2021-04-23",
                "document_revision_date": "2021-04-23",
                "accessed_date": "2026-07-19",
            },
            "UK_SBSP_2021_ANNEX_B": {
                "title": "Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility – Annex B: Input Data Sources",
                "document_year": "2021",
                "publication_date": "2021-04-23",
                "document_revision_date": "2021-04-23",
                "accessed_date": "2026-07-19",
            },
            "DESNZ_SBSP_2025": {
                "title": "Feasibility of Small-Scale Space Based Solar Power (SBSP) Systems for Early Market Adoption",
                "document_year": "2025",
                "publication_date": "2026-02-13",
                "accessed_date": "2026-07-19",
            },
            "NASA_OTPS_SBSP_2024": {
                "title": "Space Based Solar Power",
                "document_year": "2024",
                "publication_date": "2024-01-11",
                "accessed_date": "2026-07-19",
            },
            "CALTECH_SBSP_2022": {
                "title": "A Lightweight Space-based Solar Power Generation and Transmission Satellite",
                "document_year": "2022",
                "publication_date": "2022-06-16",
                "document_revision_date": "2022-07-20",
                "accessed_date": "2026-07-19",
            },
            "NAO_HPC_2017": {
                "title": "Hinkley Point C",
                "document_year": "2017",
                "publication_date": "2017-06-23",
                "accessed_date": "2026-07-19",
            },
        }
        for source_id, expected_fields in expected_sources.items():
            self.assertIn(source_id, sources)
            for field, expected_value in expected_fields.items():
                with self.subTest(source_id=source_id, field=field):
                    self.assertEqual(sources[source_id][field], expected_value)

        annex_a_technologies = {
            "Large-scale solar",
            "Onshore wind",
            "Fixed offshore wind",
            "Floating offshore wind",
            "Gas CCGT high load factor",
            "Gas with CCUS high load factor",
            "Gas with CCUS mid load factor",
        }
        with (ROOT / "data/uk_generation_costs.csv").open(newline="", encoding="utf-8") as handle:
            generation_rows = list(csv.DictReader(handle))
        annex_rows = [row for row in generation_rows if row["technology"] in annex_a_technologies]
        self.assertEqual({row["technology"] for row in annex_rows}, annex_a_technologies)
        for row in annex_rows:
            with self.subTest(technology=row["technology"]):
                self.assertEqual(row["source_id"], "DESNZ_EGC_2025_ANNEX_A")
                self.assertEqual(row["value_type"], "DESNZ 2025 Annex A 2030-2035 range")

    def test_key_evidence_locators_and_limitations_are_exact(self) -> None:
        evidence = {
            (row["parameter_or_claim"], row["source_id"]): row
            for row in self.evidence_rows
        }
        expected = {
            ("end_to_end_efficiency", "DESNZ_SBSP_2025"): (
                "Table 1, PDF pp.11-12; reference-design selection p.13",
                "The report states that major values are manufacturer-claimed, not independently verified; missing values are inferred and definitions may differ.",
                "原报告说明主要数值来自厂商声称、未经独立验证；缺失值含推断且定义可能不同。",
            ),
            ("capacity_factor", "DESNZ_SBSP_2025"): (
                "Table 3, PDF p.16",
                "Rectenna utilization is not equivalent to this model's delivered capacity factor; the 90% value remains a study assumption.",
                "整流天线利用率不等同于本模型交付容量因子；90%仍是研究假设。",
            ),
            ("launch_cost_gbp_per_kg", "DESNZ_SBSP_2025"): (
                "Table 12 p.37; Tables 27-28 pp.71-73",
                "Destination orbit, scenario year, vehicle, procurement and service boundary differ; although both are stated in 2024 GBP, the model's £500/kg reference is not taken from this table.",
                "目的轨道、情景年份、运载器、采购和服务边界不同；尽管两者均以2024年英镑表述，本模型£500/kg参考值并非取自该表。",
            ),
            ("wacc", "DESNZ_EGC_2025_ANNEX_A"): (
                "Technical and Cost Assumptions, row 38",
                "This is not an observed SBSP WACC and does not specify this model's tax or financing structure.",
                "这不是实测空间太阳能WACC，也不定义本模型税务或融资结构。",
            ),
            ("competitive_cost_claim", "UK_SBSP_2021_PHASE2"): (
                "Executive summary p.3; assumptions pp.18-19; Figure 5 p.22 and Table 4 p.23",
                "Architecture, learning, commissioning year, financing and price basis differ; values are not ranked as like-for-like forecasts.",
                "架构、学习、投产年份、融资和价格口径不同；不能按同口径预测直接排序。",
            ),
            ("launch_cost_importance", "DESNZ_SBSP_2025"): (
                "Table 14, PDF p.38",
                "This project may rank specific mass first within its own one-way ranges; neither ranking is universal.",
                "本项目在自身一维范围内可能把比质量排第一；两种排名都不是普遍规律。",
            ),
            ("system_value", "DESNZ_SBSP_2025"): (
                "executive summary, PDF pp.3-4",
                "The present model does not monetize whole-system value; £21/MWh is not subtracted from project LCOE.",
                "本模型不把全系统价值货币化，也不从项目LCOE中扣除£21/MWh。",
            ),
        }
        for key, (locator, limitation, limitation_zh) in expected.items():
            self.assertIn(key, evidence)
            with self.subTest(parameter_or_claim=key[0], source_id=key[1]):
                self.assertEqual(evidence[key]["locator"], locator)
                self.assertEqual(evidence[key]["limitations"], limitation)
                self.assertEqual(evidence[key]["limitations_zh"], limitation_zh)

    def test_readme_avoids_retired_overclaims(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        retired_claims = (
            "mass, efficiency, assembly, hardware and finance must improve together",
            "Reaching the decision range requires coordinated progress",
            "which parameter combinations are required to cross a chosen delivered-cost line?",
            "The model identifies **cost-parity conditions under its stated assumptions**",
            "Strongest single lever",
            "Broad screening ceiling",
        )
        for claim in retired_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, readme)

        for required_qualification in (
            "Study-defined decision region",
            "conditional cost requirements under its stated assumptions and explored ranges",
            "does **not** claim greater forecasting accuracy, universal necessary conditions",
            "inside a stated model and parameter range",
        ):
            self.assertIn(required_qualification, readme)

    def test_release_pdfs_have_metadata_text_and_figures(self) -> None:
        self.assertEqual(
            validate_pdf_documents(
                [ROOT / "report/final_report_EN.pdf", ROOT / "report/final_report_zh.pdf"],
                required_text_tokens=["429", "v1.2"],
            ),
            [],
        )

    def test_citation_metadata_matches_report_release(self) -> None:
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn('title: "UK Space-Based Solar Power Cost-Condition Map"', citation)
        self.assertIn('version: "1.2"', citation)
        self.assertIn("date-released: 2026-07-19", citation)


if __name__ == "__main__":
    unittest.main()
