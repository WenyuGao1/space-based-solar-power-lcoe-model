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
from src.utils import read_csv_dicts, write_csv_dicts  # noqa: E402
from src.validation import (  # noqa: E402
    validate_analysis_results,
    validate_csv_structure,
    validate_generated_csv_outputs,
    validate_markdown_images,
    validate_official_generation_extract,
    validate_outputs,
    validate_parameters,
    validate_pdf_documents,
    validate_png_images,
    validate_raw_workbooks,
    validate_reference_case,
    validate_report_content,
    validate_source_integrity,
)


PARAMETER_PATH = ROOT / "data/sbsp_parameters.csv"
GENERATION_PATH = ROOT / "data/uk_generation_costs.csv"
SYSTEM_PATH = ROOT / "data/uk_system_adjusted_costs.csv"
ASSUMPTION_PATH = ROOT / "data/assumptions.csv"
SOURCE_REGISTRY_PATH = ROOT / "data/source_registry.csv"
PARAMETER_EVIDENCE_PATH = ROOT / "data/parameter_evidence.csv"
EXTERNAL_STUDIES_PATH = ROOT / "data/external_sbsp_studies.csv"
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
    "wireless_power_transmission_cost_gbp_per_w_space": "lcoe_vs_wireless_power_cost.png",
    "end_to_end_efficiency": "lcoe_vs_end_to_end_efficiency.png",
    "wacc": "lcoe_vs_wacc.png",
    "rectenna_cost_gbp_per_w_delivered": "lcoe_vs_rectenna_cost.png",
    "grid_connection_cost_gbp_per_kw_delivered": "lcoe_vs_grid_connection_cost.png",
    "system_lifetime_years": "lcoe_vs_system_lifetime.png",
    "capacity_factor": "lcoe_vs_capacity_factor.png",
    "in_orbit_assembly_cost_gbp_per_kg": "lcoe_vs_in_orbit_assembly.png",
    "orbit_transfer_cost_gbp_per_kg": "lcoe_vs_orbit_transfer_cost.png",
    "programme_margin_pct": "lcoe_vs_programme_margin.png",
    "replacement_refurbishment_pct_capex_per_year": "lcoe_vs_replacement_refurbishment.png",
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
    input_csvs = [
        ASSUMPTION_PATH,
        EXTERNAL_STUDIES_PATH,
        PARAMETER_EVIDENCE_PATH,
        PARAMETER_PATH,
        SOURCE_REGISTRY_PATH,
        GENERATION_PATH,
        SYSTEM_PATH,
    ]
    preflight_errors = validate_csv_structure(input_csvs)
    if preflight_errors:
        for error in preflight_errors:
            print(f"PREFLIGHT ERROR: {error}")
        return 1

    params = load_parameters(PARAMETER_PATH)
    reference = reference_values(params)
    generation_rows = numeric_benchmark_rows(GENERATION_PATH)
    system_rows = numeric_benchmark_rows(SYSTEM_PATH)
    assumption_rows = read_csv_dicts(ASSUMPTION_PATH)
    source_rows = read_csv_dicts(SOURCE_REGISTRY_PATH)
    evidence_rows = read_csv_dicts(PARAMETER_EVIDENCE_PATH)
    external_study_rows = read_csv_dicts(EXTERNAL_STUDIES_PATH)

    validation_errors = []
    validation_errors.extend(validate_parameters(params))
    validation_errors.extend(validate_reference_case(reference))
    validation_errors.extend(validate_raw_workbooks(RAW_WORKBOOKS))
    validation_errors.extend(
        validate_source_integrity(
            SOURCE_REGISTRY_PATH,
            [
                ASSUMPTION_PATH,
                EXTERNAL_STUDIES_PATH,
                PARAMETER_EVIDENCE_PATH,
                PARAMETER_PATH,
                GENERATION_PATH,
                SYSTEM_PATH,
            ],
        )
    )
    validation_errors.extend(
        validate_official_generation_extract(
            ROOT / "data/raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
            GENERATION_PATH,
        )
    )
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

    analysis_errors = validate_analysis_results(
        reference,
        params,
        SENSITIVITY_PARAMETERS,
        thresholds,
        frontier,
        combined_frontier,
        alternative_frontiers,
    )
    if analysis_errors:
        for error in analysis_errors:
            print(f"ANALYSIS VALIDATION ERROR: {error}")
        return 1

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
        source_rows,
        evidence_rows,
        assumption_rows,
        external_study_rows,
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
        source_rows,
        evidence_rows,
        assumption_rows,
        external_study_rows,
    )
    pdf_en_built, pdf_en_message = _try_build_pdf(
        "final_report_EN.md",
        "final_report_EN.pdf",
        "UK Space-Based Solar Power Cost-Condition Map",
    )
    pdf_zh_built, pdf_zh_message = _try_build_pdf(
        "final_report_zh.md",
        "final_report_zh.pdf",
        "英国空间太阳能成本条件图",
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
    generated_csv_errors = validate_generated_csv_outputs(
        [
            {
                "path": PROCESSED_DIR / "reference_lcoe.csv",
                "row_count": 19,
                "required_columns": ["metric", "value"],
                "key_columns": ["metric"],
            },
            {
                "path": PROCESSED_DIR / "sensitivity_curves.csv",
                "row_count": len(SENSITIVITY_PARAMETERS) * 101,
                "required_columns": ["parameter", "value", "lcoe_gbp_per_mwh"],
                "key_columns": ["parameter", "value"],
            },
            {
                "path": PROCESSED_DIR / "thresholds_one_way.csv",
                "row_count": len(SENSITIVITY_PARAMETERS) * 5,
                "required_columns": [
                    "parameter",
                    "target_lcoe_gbp_per_mwh",
                    "threshold_value",
                    "lcoe_at_threshold_gbp_per_mwh",
                    "solution_method",
                    "status",
                ],
                "key_columns": ["parameter", "target_lcoe_gbp_per_mwh"],
            },
            {
                "path": PROCESSED_DIR / "one_way_feasibility_matrix.csv",
                "row_count": len(SENSITIVITY_PARAMETERS) * 5,
                "required_columns": ["parameter", "target_lcoe_gbp_per_mwh", "feasible"],
                "key_columns": ["parameter", "target_lcoe_gbp_per_mwh"],
            },
            {
                "path": PROCESSED_DIR / "cost_driver_importance.csv",
                "row_count": len(SENSITIVITY_PARAMETERS),
                "required_columns": ["parameter", "lcoe_reduction_gbp_per_mwh"],
                "key_columns": ["parameter"],
            },
            {
                "path": PROCESSED_DIR / "contour_grids.csv",
                "row_count": 3 * 60 * 60,
                "required_columns": ["x_parameter", "x_value", "y_parameter", "y_value", "lcoe_gbp_per_mwh"],
                "key_columns": ["x_parameter", "x_value", "y_parameter", "y_value"],
            },
            {
                "path": PROCESSED_DIR / "launch_efficiency_frontier.csv",
                "row_count": 4 * 5,
                "required_columns": ["end_to_end_efficiency", "target_lcoe_gbp_per_mwh", "status"],
                "key_columns": ["end_to_end_efficiency", "target_lcoe_gbp_per_mwh"],
            },
            {
                "path": PROCESSED_DIR / "combined_improvement_frontier.csv",
                "row_count": 5,
                "required_columns": ["target_lcoe_gbp_per_mwh", "progress_fraction", "status"],
                "key_columns": ["target_lcoe_gbp_per_mwh"],
            },
            {
                "path": PROCESSED_DIR / "alternative_combined_pathways.csv",
                "row_count": 3 * 5,
                "required_columns": ["pathway", "target_lcoe_gbp_per_mwh", "progress_fraction", "status"],
                "key_columns": ["pathway", "target_lcoe_gbp_per_mwh"],
            },
        ]
    )
    png_paths = [path for path in expected_outputs if path.suffix.lower() == ".png"]
    png_errors = validate_png_images(png_paths)
    markdown_image_errors = validate_markdown_images(
        [REPORT_DIR / "final_report_EN.md", REPORT_DIR / "final_report_zh.md"],
        expected_count=7,
    )

    shared_tokens = ["v1.2", f"£{reference_rows[0]['value']:.0f}/MWh"]
    shared_tokens.extend(
        f"{float(row['threshold_value']):.2f}"
        for row in thresholds
        if row["parameter"] == "specific_mass_kg_per_kw_space_power"
        and int(row["target_lcoe_gbp_per_mwh"]) in {150, 120, 100}
        and row["threshold_value"] not in (None, "")
    )
    shared_tokens.extend(
        f"{float(row['progress_fraction']):.1%}"
        for row in combined_frontier
        if row.get("progress_fraction") not in (None, "")
    )
    report_errors = validate_report_content(
        [REPORT_DIR / "final_report_EN.md", REPORT_DIR / "final_report_zh.md"],
        shared_tokens,
    )
    pdf_paths = []
    if pdf_en_built:
        pdf_paths.append(REPORT_DIR / "final_report_EN.pdf")
    if pdf_zh_built:
        pdf_paths.append(REPORT_DIR / "final_report_zh.pdf")
    pdf_errors = validate_pdf_documents(
        pdf_paths,
        required_text_tokens=["429", "v1.2"],
    ) if len(pdf_paths) == 2 else [
        "Both bilingual PDFs were not generated."
    ]

    all_release_errors = [
        *output_errors,
        *generated_csv_errors,
        *png_errors,
        *markdown_image_errors,
        *report_errors,
        *pdf_errors,
    ]
    category_results = [
        {
            "category": "Numerical model",
            "status": "PASS" if not analysis_errors else "FAIL",
            "evidence": "Reference CAPEX and annual-cost identities reconcile; root-solved thresholds are written with their target residuals.",
        },
        {
            "category": "Input data structure",
            "status": "PASS" if not preflight_errors and not validation_errors else "FAIL",
            "evidence": "CSV record lengths, headers, required parameter bounds and official XLSX parseability were checked.",
        },
        {
            "category": "Source and benchmark traceability",
            "status": "PASS" if not validation_errors else "FAIL",
            "evidence": "Source foreign keys resolve; exact SBSP inputs are study-authored; selected DESNZ 2025 cells reconcile to the benchmark CSV.",
        },
        {
            "category": "Bilingual numerical parity",
            "status": "PASS" if not report_errors else "FAIL",
            "evidence": "Both Markdown reports contain the shared version, reference LCOE, mass thresholds and coupled-frontier percentages.",
        },
        {
            "category": "Output completeness",
            "status": "PASS" if not output_errors and not generated_csv_errors and not png_errors and not markdown_image_errors else "FAIL",
            "evidence": f"Checked {len(expected_outputs)} expected files, generated CSV row/schema invariants, decodable PNGs and seven resolved main figures per report.",
        },
        {
            "category": "PDF structure",
            "status": "PASS" if not pdf_errors else "FAIL",
            "evidence": "Both PDFs were parsed, checked for a minimum page count and checked for extractable text.",
        },
    ]
    build_verification_note(
        REPORT_DIR / "verification_note.md",
        category_results=category_results,
        warnings=[
            "Actual orbital mass, assembly cost, replacement rate and end-to-end efficiency remain architecture-dependent.",
            "BEIS 2018-real-GBP system-adjusted values and DESNZ 2024-real-GBP generation values are disclosed but not price-normalised.",
            "System value requires a full GB power-system model and is not monetised here.",
            "PDF visual quality is verified separately during release review; the pipeline checks structure and extractable content.",
            *all_release_errors,
        ],
        commands=[
            "python -m unittest discover -s tests -v",
            "python analysis/run_full_analysis.py",
        ],
    )

    verification_errors = validate_outputs([REPORT_DIR / "verification_note.md"])
    all_release_errors.extend(verification_errors)
    if all_release_errors:
        for error in all_release_errors:
            print(f"RELEASE VALIDATION ERROR: {error}")
        return 1

    print(f"Reference SBSP LCOE: {reference_rows[0]['value']:.2f} GBP/MWh")
    print(pdf_en_message)
    print(pdf_zh_message)
    print("Full analysis complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
