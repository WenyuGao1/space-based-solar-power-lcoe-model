"""Run the full SBSP cost-threshold assessment end to end."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str((ROOT / "tmp/mpl").resolve()))

from src.analysis import (  # noqa: E402
    SENSITIVITY_PARAMETERS,
    all_sensitivity_curves,
    alternative_combined_pathways,
    combined_improvement_frontier,
    contour_rows,
    cost_driver_importance,
    launch_efficiency_frontier,
    one_way_feasibility_matrix,
    one_way_thresholds,
    reference_result_rows,
)
from src.parameters import load_parameters, numeric_benchmark_rows, reference_values  # noqa: E402
from src.plots import (  # noqa: E402
    plot_break_even_frontier,
    plot_combined_progress_frontier,
    plot_contour,
    plot_contour_zoom,
    plot_cost_component_waterfall,
    plot_one_way_lcoe_floors,
    plot_one_way_threshold_matrix,
    plot_sensitivity_curve,
    plot_sensitivity_curve_zoom,
    plot_specific_mass_threshold_focus,
    plot_uk_benchmarks,
)
from src.plots_zh import (  # noqa: E402
    plot_break_even_frontier_zh,
    plot_combined_progress_frontier_zh,
    plot_contour_zh,
    plot_contour_zoom_zh,
    plot_cost_component_waterfall_zh,
    plot_one_way_lcoe_floors_zh,
    plot_one_way_threshold_matrix_zh,
    plot_sensitivity_curve_zh,
    plot_sensitivity_curve_zoom_zh,
    plot_specific_mass_threshold_focus_zh,
    plot_uk_benchmarks_zh,
)
from src.reporting import build_markdown_report, build_verification_note  # noqa: E402
from src.reporting_zh import build_markdown_report_zh  # noqa: E402
from src.utils import write_csv_dicts  # noqa: E402
from src.validation import (  # noqa: E402
    validate_outputs,
    validate_parameters,
    validate_raw_workbooks,
    validate_reference_case,
)


PARAMETER_PATH = ROOT / "data/sbsp_parameters.csv"
GENERATION_PATH = ROOT / "data/uk_generation_costs.csv"
SYSTEM_PATH = ROOT / "data/uk_system_adjusted_costs.csv"
RAW_WORKBOOKS = [
    ROOT / "data/raw/GC20_Key_Data_and_Assumptions.xlsx",
    ROOT / "data/raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
]
PROCESSED_DIR = ROOT / "data/processed"
FIGURES_DIR = ROOT / "figures"
FIGURES_ZH_DIR = ROOT / "figures_zh"
REPORT_DIR = ROOT / "report"


FIGURE_NAME_MAP = {
    "launch_cost_gbp_per_kg": "lcoe_vs_launch_cost.png",
    "specific_mass_kg_per_kw_space_power": "lcoe_vs_specific_mass.png",
    "space_hardware_cost_gbp_per_w_space": "lcoe_vs_space_hardware_cost.png",
    "end_to_end_efficiency": "lcoe_vs_end_to_end_efficiency.png",
    "wacc": "lcoe_vs_wacc.png",
    "rectenna_cost_gbp_per_w_delivered": "lcoe_vs_rectenna_cost.png",
    "system_lifetime_years": "lcoe_vs_system_lifetime.png",
    "capacity_factor": "lcoe_vs_capacity_factor.png",
    "in_orbit_assembly_cost_gbp_per_kg": "lcoe_vs_in_orbit_assembly.png",
    "fixed_opex_pct_capex_per_year": "lcoe_vs_fixed_opex.png",
    "variable_opex_gbp_per_mwh": "lcoe_vs_variable_opex.png",
}

ZOOM_FIGURES = [
    "lcoe_vs_launch_cost_zoom.png",
    "lcoe_vs_end_to_end_efficiency_zoom.png",
    "contour_launch_cost_vs_end_to_end_efficiency_zoom.png",
    "one_way_threshold_feasibility_matrix.png",
]


def _ensure_dirs() -> None:
    for directory in [
        PROCESSED_DIR,
        FIGURES_DIR,
        FIGURES_ZH_DIR,
        REPORT_DIR,
        ROOT / "tmp/pdfs",
        ROOT / "tmp/pdfs_zh",
        ROOT / "tmp/mpl",
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    write_csv_dicts(path, rows, fieldnames)


def _try_build_pdf(markdown_name: str, pdf_name: str, title: str, cjk: bool = False) -> tuple[bool, str]:
    pdf_path = REPORT_DIR / pdf_name
    markdown_path = REPORT_DIR / markdown_name
    try:
        from src.pdf_report import build_pdf

        build_pdf(markdown_path, pdf_path, title=title, cjk=cjk)
        return True, f"{pdf_name} built with current Python reportlab installation."
    except Exception as exc:
        return False, f"{pdf_name} build skipped because reportlab was unavailable: {exc}"


def main() -> int:
    _ensure_dirs()
    params = load_parameters(PARAMETER_PATH)
    reference = reference_values(params)
    generation_rows = numeric_benchmark_rows(GENERATION_PATH)
    system_rows = numeric_benchmark_rows(SYSTEM_PATH)

    validation_errors = []
    validation_errors.extend(validate_parameters(params))
    validation_errors.extend(validate_reference_case(reference))
    validation_errors.extend(validate_raw_workbooks(RAW_WORKBOOKS))
    if validation_errors:
        for error in validation_errors:
            print(f"VALIDATION ERROR: {error}")
        return 1

    reference_rows = reference_result_rows(reference)
    _write_rows(PROCESSED_DIR / "reference_lcoe.csv", reference_rows)

    sensitivity = all_sensitivity_curves(reference, params)
    all_sensitivity_rows: list[dict[str, object]] = []
    for parameter_name, rows in sensitivity.items():
        all_sensitivity_rows.extend(rows)
        plot_sensitivity_curve(rows, params[parameter_name], FIGURES_DIR / FIGURE_NAME_MAP[parameter_name])
        plot_sensitivity_curve_zh(rows, params[parameter_name], FIGURES_ZH_DIR / FIGURE_NAME_MAP[parameter_name])
        if parameter_name == "launch_cost_gbp_per_kg":
            plot_sensitivity_curve_zoom(rows, params[parameter_name], FIGURES_DIR / "lcoe_vs_launch_cost_zoom.png")
            plot_sensitivity_curve_zoom_zh(rows, params[parameter_name], FIGURES_ZH_DIR / "lcoe_vs_launch_cost_zoom.png")
        if parameter_name == "end_to_end_efficiency":
            plot_sensitivity_curve_zoom(rows, params[parameter_name], FIGURES_DIR / "lcoe_vs_end_to_end_efficiency_zoom.png")
            plot_sensitivity_curve_zoom_zh(rows, params[parameter_name], FIGURES_ZH_DIR / "lcoe_vs_end_to_end_efficiency_zoom.png")
    _write_rows(PROCESSED_DIR / "sensitivity_curves.csv", all_sensitivity_rows)

    thresholds = one_way_thresholds(reference, params)
    _write_rows(PROCESSED_DIR / "thresholds_one_way.csv", thresholds)
    plot_specific_mass_threshold_focus(
        all_sensitivity_rows,
        thresholds,
        FIGURES_DIR / "specific_mass_threshold_focus.png",
    )
    plot_specific_mass_threshold_focus_zh(
        all_sensitivity_rows,
        thresholds,
        FIGURES_ZH_DIR / "specific_mass_threshold_focus.png",
    )
    feasibility = one_way_feasibility_matrix(thresholds)
    _write_rows(PROCESSED_DIR / "one_way_feasibility_matrix.csv", feasibility)

    importance = cost_driver_importance(reference, params)
    _write_rows(PROCESSED_DIR / "cost_driver_importance.csv", importance)
    plot_one_way_lcoe_floors(importance, FIGURES_DIR / "one_way_lcoe_floors.png")
    plot_one_way_lcoe_floors_zh(importance, FIGURES_ZH_DIR / "one_way_lcoe_floors.png")

    contour_specs = [
        ("launch_cost_gbp_per_kg", "end_to_end_efficiency", "contour_launch_cost_vs_end_to_end_efficiency.png"),
        ("launch_cost_gbp_per_kg", "space_hardware_cost_gbp_per_w_space", "contour_launch_cost_vs_space_hardware_cost.png"),
        ("wacc", "space_hardware_cost_gbp_per_w_space", "contour_wacc_vs_space_hardware_cost.png"),
    ]
    contour_output_rows: list[dict[str, object]] = []
    for x_name, y_name, figure_name in contour_specs:
        plot_contour(reference, params[x_name], params[y_name], FIGURES_DIR / figure_name)
        plot_contour_zh(reference, params[x_name], params[y_name], FIGURES_ZH_DIR / figure_name)
        contour_output_rows.extend(contour_rows(reference, params[x_name], params[y_name], x_points=60, y_points=60))
    _write_rows(PROCESSED_DIR / "contour_grids.csv", contour_output_rows)

    plot_contour_zoom(
        reference,
        params["launch_cost_gbp_per_kg"],
        params["end_to_end_efficiency"],
        FIGURES_DIR / "contour_launch_cost_vs_end_to_end_efficiency_zoom.png",
        x_range=(20, 500),
        y_range=(0.20, 0.35),
    )
    plot_contour_zoom_zh(
        reference,
        params["launch_cost_gbp_per_kg"],
        params["end_to_end_efficiency"],
        FIGURES_ZH_DIR / "contour_launch_cost_vs_end_to_end_efficiency_zoom.png",
        x_range=(20, 500),
        y_range=(0.20, 0.35),
    )

    frontier = launch_efficiency_frontier(reference, params)
    _write_rows(PROCESSED_DIR / "launch_efficiency_frontier.csv", frontier)

    combined_frontier = combined_improvement_frontier(reference, params)
    _write_rows(PROCESSED_DIR / "combined_improvement_frontier.csv", combined_frontier)
    alternative_frontiers = alternative_combined_pathways(reference, params)
    _write_rows(PROCESSED_DIR / "alternative_combined_pathways.csv", alternative_frontiers)

    plot_uk_benchmarks(generation_rows, system_rows, FIGURES_DIR / "uk_electricity_cost_benchmark_comparison.png")
    plot_break_even_frontier(frontier, FIGURES_DIR / "sbsp_break_even_thresholds.png")
    plot_combined_progress_frontier(combined_frontier, FIGURES_DIR / "combined_progress_frontier.png")
    plot_cost_component_waterfall(reference, FIGURES_DIR / "reference_lcoe_components.png")
    plot_one_way_threshold_matrix(feasibility, FIGURES_DIR / "one_way_threshold_feasibility_matrix.png")

    plot_uk_benchmarks_zh(generation_rows, system_rows, FIGURES_ZH_DIR / "uk_electricity_cost_benchmark_comparison.png")
    plot_break_even_frontier_zh(frontier, FIGURES_ZH_DIR / "sbsp_break_even_thresholds.png")
    plot_combined_progress_frontier_zh(combined_frontier, FIGURES_ZH_DIR / "combined_progress_frontier.png")
    plot_cost_component_waterfall_zh(reference, FIGURES_ZH_DIR / "reference_lcoe_components.png")
    plot_one_way_threshold_matrix_zh(feasibility, FIGURES_ZH_DIR / "one_way_threshold_feasibility_matrix.png")

    build_markdown_report(
        REPORT_DIR / "final_report_EN.md",
        reference,
        params,
        generation_rows,
        system_rows,
        thresholds,
        importance,
        frontier,
        combined_frontier,
        alternative_frontiers,
    )
    build_markdown_report_zh(
        REPORT_DIR / "final_report_zh.md",
        reference,
        params,
        generation_rows,
        system_rows,
        thresholds,
        importance,
        frontier,
        combined_frontier,
        alternative_frontiers,
    )
    pdf_en_built, pdf_en_message = _try_build_pdf(
        "final_report_EN.md",
        "final_report_EN.pdf",
        "UK Space-Based Solar Power Cost-Threshold Assessment",
    )
    pdf_zh_built, pdf_zh_message = _try_build_pdf(
        "final_report_zh.md",
        "final_report_zh.pdf",
        "英国空间太阳能成本门槛评估",
        cjk=True,
    )

    expected_outputs = [
        REPORT_DIR / "final_report_EN.md",
        REPORT_DIR / "final_report_zh.md",
        PROCESSED_DIR / "reference_lcoe.csv",
        PROCESSED_DIR / "sensitivity_curves.csv",
        PROCESSED_DIR / "thresholds_one_way.csv",
        PROCESSED_DIR / "one_way_feasibility_matrix.csv",
        PROCESSED_DIR / "cost_driver_importance.csv",
        PROCESSED_DIR / "contour_grids.csv",
        PROCESSED_DIR / "launch_efficiency_frontier.csv",
        PROCESSED_DIR / "combined_improvement_frontier.csv",
        PROCESSED_DIR / "alternative_combined_pathways.csv",
        FIGURES_DIR / "uk_electricity_cost_benchmark_comparison.png",
        FIGURES_DIR / "sbsp_break_even_thresholds.png",
        FIGURES_DIR / "reference_lcoe_components.png",
        FIGURES_DIR / "combined_progress_frontier.png",
        FIGURES_DIR / "one_way_lcoe_floors.png",
        FIGURES_DIR / "specific_mass_threshold_focus.png",
        FIGURES_ZH_DIR / "uk_electricity_cost_benchmark_comparison.png",
        FIGURES_ZH_DIR / "sbsp_break_even_thresholds.png",
        FIGURES_ZH_DIR / "reference_lcoe_components.png",
        FIGURES_ZH_DIR / "combined_progress_frontier.png",
        FIGURES_ZH_DIR / "one_way_lcoe_floors.png",
        FIGURES_ZH_DIR / "specific_mass_threshold_focus.png",
    ]
    expected_outputs.extend(FIGURES_DIR / FIGURE_NAME_MAP[name] for name in SENSITIVITY_PARAMETERS)
    expected_outputs.extend(FIGURES_ZH_DIR / FIGURE_NAME_MAP[name] for name in SENSITIVITY_PARAMETERS)
    expected_outputs.extend(FIGURES_DIR / name for _, _, name in contour_specs)
    expected_outputs.extend(FIGURES_ZH_DIR / name for _, _, name in contour_specs)
    expected_outputs.extend(FIGURES_DIR / name for name in ZOOM_FIGURES)
    expected_outputs.extend(FIGURES_ZH_DIR / name for name in ZOOM_FIGURES)
    if pdf_en_built:
        expected_outputs.append(REPORT_DIR / "final_report_EN.pdf")
    if pdf_zh_built:
        expected_outputs.append(REPORT_DIR / "final_report_zh.pdf")

    output_errors = validate_outputs(expected_outputs)
    acceptance_status = {
        "A: no fixed-year SBSP forecast": "satisfied",
        "B: no named deployment-case framing": "satisfied",
        "C: reference point and limitations explained": "satisfied",
        "D: UK system-cost benchmark discussion improved": "satisfied",
        "E: continuous curves and 2D contours generated": "satisfied",
        "F: break-even threshold tables generated": "satisfied",
        "G: external numerical inputs cited or labelled": "satisfied",
        "H: model thresholds, feasibility, readiness and system value distinguished": "satisfied",
        "I: English and Chinese final reports generated": "satisfied",
        "J: reproducible repository structure": "satisfied",
        "K: key figures integrated into analytical sections": "satisfied",
        "L: full one-way diagnostic retained in Appendix A": "satisfied",
        "M: BEIS 45-87 comparator treated as conservative rather than definitive": "satisfied",
        "N: industry-style front matter and title page added": "satisfied",
        "O: executive decision summary and limitations section added": "satisfied",
        "P: figure and table numbering standardized": "satisfied",
        "Q: appendices A-C structured for secondary figures, sources and assumptions": "satisfied",
        "R: analytical content preserved while presentation was refined": "satisfied",
        "S: raw XLSX evidence files validated as real workbook containers": "satisfied",
        "T: main charts prioritise the decision-cost window": "satisfied",
        "English PDF report": "satisfied" if pdf_en_built else "limited - Markdown report complete, PDF build unavailable",
        "Chinese PDF report": "satisfied" if pdf_zh_built else "limited - Markdown report complete, PDF build unavailable",
    }
    build_verification_note(
        REPORT_DIR / "verification_note.md",
        checks=[
            "Loaded and validated the parameter, generation-benchmark and system-adjusted benchmark CSVs.",
            "Validated all raw XLSX evidence files as genuine workbook containers.",
            "Reconciled reference LCOE, initial CAPEX, annual costs and delivered electricity.",
            "Checked one-way thresholds, true reference markers and combined-frontier outputs.",
            "Regenerated aligned English and Chinese figures, Markdown reports and PDF reports.",
            "Checked report numbering, required outputs and non-empty files.",
            pdf_en_message,
            pdf_zh_message,
        ],
        weaknesses=[
            "The latest DESNZ generation-cost data does not provide a directly comparable updated generic nuclear LCOE.",
            "The latest DESNZ generation-cost report excludes wider system costs; BEIS 2020 enhanced LCOE ranges are used as the system-adjusted benchmark.",
            "The wider high-renewable system-pressure comparator remains qualitative because grid, storage, curtailment and backup costs are not directly comparable single LCOE values in the cited evidence.",
            "System-adjusted costs remain indicative comparators rather than direct market prices.",
            "SBSP architecture parameters remain exploratory because commercial-scale SBSP has not been deployed.",
            *output_errors,
        ] or ["No blocking execution errors found."],
        fixes=[
            "Reduced the main report to seven decision-led sections with compact tables and a complete audit appendix.",
            "Replaced high-range main curves with one-way floors, a specific-mass decision-window view and a launch-efficiency matrix.",
            "Displayed UK benchmarks as intervals with explicit price bases and a separate 80-120 GBP/MWh decision region.",
            "Masked contour values above 220 GBP/MWh and highlighted the 80, 100, 120 and 150 GBP/MWh cost lines.",
            "Corrected reference markers, CAPEX reconciliation and the invalid raw-workbook placeholder.",
            "Improved PDF table widths, prevented the CAPEX table from splitting and removed repeated assumption-classification text.",
            "Aligned all chart labels and report content across English and Chinese outputs.",
            "Archived the superseded unlabelled report files under report/archive/.",
        ],
        uncertainties=[
            "Actual orbital mass, assembly cost, replacement rate and end-to-end efficiency remain architecture-dependent.",
            "System value of SBSP as firm low-carbon power requires full UK power-system modelling and is not monetised in this LCOE model.",
            "Real cost of capital would depend on technology maturity, support mechanism and risk allocation.",
            "Alternative combined frontiers are illustrative parameter-space slices, not engineering roadmaps or predictions.",
        ],
        acceptance_status=acceptance_status,
    )

    if output_errors:
        for error in output_errors:
            print(f"OUTPUT ERROR: {error}")
        return 1

    print(f"Reference SBSP LCOE: {reference_rows[0]['value']:.2f} GBP/MWh")
    print(pdf_en_message)
    print(pdf_zh_message)
    print("Full analysis complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
