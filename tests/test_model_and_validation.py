from __future__ import annotations

from pathlib import Path
import unittest

from src.analysis import SENSITIVITY_PARAMETERS, one_way_thresholds, sensitivity_curve
from src.model import calculate_lcoe
from src.parameters import load_parameters, reference_values
from src.plots import _reference_lcoe_on_curve
from src.validation import validate_raw_workbooks, validate_reference_case


ROOT = Path(__file__).resolve().parents[1]


class ModelAndEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.params = load_parameters(ROOT / "data/sbsp_parameters.csv")
        cls.reference = reference_values(cls.params)

    def test_reference_case_reconciles(self) -> None:
        self.assertEqual(validate_reference_case(self.reference), [])
        result = calculate_lcoe(self.reference)
        self.assertAlmostEqual(result.lcoe_gbp_per_mwh, 429.25078050818814, places=6)
        self.assertAlmostEqual(result.initial_capex_gbp, 72.6e9, delta=1.0)

    def test_specific_mass_thresholds_are_stable(self) -> None:
        rows = one_way_thresholds(self.reference, self.params, targets=[150, 120, 100])
        matches = {
            int(row["target_lcoe_gbp_per_mwh"]): float(row["threshold_value"])
            for row in rows
            if row["parameter"] == "specific_mass_kg_per_kw_space_power"
        }
        self.assertAlmostEqual(matches[150], 1.283, places=3)
        self.assertAlmostEqual(matches[120], 0.88425, places=5)
        self.assertAlmostEqual(matches[100], 0.616, places=3)

    def test_curve_reference_markers_use_reference_values(self) -> None:
        reference_lcoe = calculate_lcoe(self.reference).lcoe_gbp_per_mwh
        for name in SENSITIVITY_PARAMETERS:
            parameter = self.params[name]
            rows = sensitivity_curve(self.reference, parameter, points=101)
            plotted_reference = _reference_lcoe_on_curve(rows, parameter.reference_value)
            self.assertAlmostEqual(plotted_reference, reference_lcoe, delta=0.25, msg=name)

    def test_raw_workbooks_are_valid_xlsx_containers(self) -> None:
        paths = [
            ROOT / "data/raw/GC20_Key_Data_and_Assumptions.xlsx",
            ROOT / "data/raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
        ]
        self.assertEqual(validate_raw_workbooks(paths), [])


if __name__ == "__main__":
    unittest.main()
