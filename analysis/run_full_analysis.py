"""Regenerate the complete v2.0 SBSP assessment."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp/mpl"))
os.environ.setdefault("MPLBACKEND", "Agg")

from src.analysis import (  # noqa: E402
    SENSITIVITY_PARAMETERS, all_sensitivity_curves, alternative_combined_pathways,
    combined_improvement_frontier, contour_rows, cost_driver_importance,
    launch_efficiency_frontier, one_way_feasibility_matrix, one_way_thresholds,
    reference_result_rows,
)
from src.model import calculate_lcoe  # noqa: E402
from src.parameters import load_parameters, numeric_benchmark_rows, reference_values  # noqa: E402
from src.plots import (  # noqa: E402
    plot_break_even_frontier, plot_combined_progress_frontier, plot_contour,
    plot_cost_component_waterfall, plot_one_way_lcoe_floors,
    plot_one_way_threshold_matrix, plot_sensitivity_curve,
    plot_specific_mass_threshold_focus, plot_uk_benchmarks,
)
from src.plots_zh import (  # noqa: E402
    plot_break_even_frontier_zh, plot_combined_progress_frontier_zh, plot_contour_zh,
    plot_cost_component_waterfall_zh, plot_one_way_lcoe_floors_zh,
    plot_one_way_threshold_matrix_zh, plot_sensitivity_curve_zh,
    plot_specific_mass_threshold_focus_zh, plot_uk_benchmarks_zh,
)
from src.reporting import build_markdown_report, build_verification_note  # noqa: E402
from src.reporting_zh import build_markdown_report_zh  # noqa: E402
from src.utils import read_csv_dicts, write_csv_dicts  # noqa: E402
from src.validation import (  # noqa: E402
    validate_analysis_results, validate_csv_structure, validate_generated_csv_outputs,
    validate_markdown_images, validate_official_generation_extract, validate_outputs,
    validate_parameters, validate_pdf_documents, validate_png_images,
    validate_raw_workbooks, validate_reference_case, validate_report_content,
    validate_source_integrity,
)
from src.web_payload import build_web_payload  # noqa: E402


DATA = ROOT / "data"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "figures"
FIGURES_ZH = ROOT / "figures_zh"
REPORT = ROOT / "report"
PARAMETERS = DATA / "sbsp_parameters.csv"


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if rows:
        write_csv_dicts(path, rows, list(rows[0]))


def try_pdf(markdown: str, pdf: str, title: str, cjk: bool = False) -> tuple[bool, str]:
    try:
        from src.pdf_report import build_pdf
        build_pdf(REPORT / markdown, REPORT / pdf, title=title, cjk=cjk)
        return True, f"Generated {pdf}."
    except Exception as exc:
        return False, f"Could not generate {pdf}: {exc}"


def main() -> int:
    for directory in (PROCESSED, FIGURES, FIGURES_ZH, REPORT, ROOT / "tmp/mpl", ROOT / "tmp/pdfs", ROOT / "tmp/pdfs_zh"):
        directory.mkdir(parents=True, exist_ok=True)

    input_csvs = [DATA / name for name in (
        "assumptions.csv", "external_sbsp_studies.csv", "model_configuration.csv", "parameter_evidence.csv",
        "sbsp_parameters.csv", "source_registry.csv", "uk_generation_costs.csv",
        "uk_system_adjusted_costs.csv",
    )]
    errors = validate_csv_structure(input_csvs)
    params = load_parameters(PARAMETERS)
    reference = reference_values(params)
    errors += validate_parameters(params)
    errors += validate_reference_case(reference)
    errors += validate_raw_workbooks([
        DATA / "raw/GC20_Key_Data_and_Assumptions.xlsx",
        DATA / "raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx",
    ])
    errors += validate_source_integrity(DATA / "source_registry.csv", input_csvs[:-1])
    errors += validate_official_generation_extract(DATA / "raw/annex-a-additional-estimates-and-key-assumptions-2025.xlsx", DATA / "uk_generation_costs.csv")
    if errors:
        for error in errors:
            print(f"PREFLIGHT ERROR: {error}")
        return 1

    generation = numeric_benchmark_rows(DATA / "uk_generation_costs.csv")
    system = numeric_benchmark_rows(DATA / "uk_system_adjusted_costs.csv")
    assumptions = read_csv_dicts(DATA / "assumptions.csv")
    configuration = read_csv_dicts(DATA / "model_configuration.csv")
    sources = read_csv_dicts(DATA / "source_registry.csv")
    evidence = read_csv_dicts(DATA / "parameter_evidence.csv")
    studies = read_csv_dicts(DATA / "external_sbsp_studies.csv")
    result = calculate_lcoe(reference)

    reference_rows = reference_result_rows(reference)
    write_rows(PROCESSED / "reference_lcoe.csv", reference_rows)
    write_rows(PROCESSED / "reference_energy_chain.csv", [
        {"stage": name, "power_w": value, "power_gw": value / 1e9}
        for name, value in result.energy_chain_power_w.items()
    ])
    write_rows(PROCESSED / "reference_cash_flow.csv", [dict(row) for row in result.cash_flow_rows])

    sensitivities = all_sensitivity_curves(reference, params, points=101)
    sensitivity_rows = [row for rows in sensitivities.values() for row in rows]
    write_rows(PROCESSED / "sensitivity_curves.csv", sensitivity_rows)
    sensitivity_figures: list[Path] = []
    for name, rows in sensitivities.items():
        en = FIGURES / f"lcoe_vs_{name}.png"
        zh = FIGURES_ZH / f"lcoe_vs_{name}.png"
        plot_sensitivity_curve(rows, params[name], en)
        plot_sensitivity_curve_zh(rows, params[name], zh)
        sensitivity_figures.extend([en, zh])

    thresholds = one_way_thresholds(reference, params)
    feasibility = one_way_feasibility_matrix(thresholds)
    importance = cost_driver_importance(reference, params)
    write_rows(PROCESSED / "thresholds_one_way.csv", thresholds)
    write_rows(PROCESSED / "one_way_feasibility_matrix.csv", feasibility)
    write_rows(PROCESSED / "cost_driver_importance.csv", importance)

    contour_specs = [
        ("launch_cost_gbp_per_kg_to_staging_orbit", "system_specific_mass_kg_per_kw_delivered", "contour_launch_vs_delivered_mass.png"),
        ("launch_cost_gbp_per_kg_to_staging_orbit", "solar_conversion_efficiency", "contour_launch_vs_solar_conversion.png"),
        ("real_discount_rate", "space_generation_hardware_cost_gbp_per_w_dc", "contour_discount_vs_generation_cost.png"),
    ]
    contour_output: list[dict[str, object]] = []
    contour_figures: list[Path] = []
    for x, y, name in contour_specs:
        en, zh = FIGURES / name, FIGURES_ZH / name
        plot_contour(reference, params[x], params[y], en)
        plot_contour_zh(reference, params[x], params[y], zh)
        contour_output += contour_rows(reference, params[x], params[y], 45, 45)
        contour_figures.extend([en, zh])
    write_rows(PROCESSED / "contour_grids.csv", contour_output)

    frontier = launch_efficiency_frontier(reference, params)
    combined = combined_improvement_frontier(reference, params)
    alternatives = alternative_combined_pathways(reference, params)
    write_rows(PROCESSED / "launch_efficiency_frontier.csv", frontier)
    write_rows(PROCESSED / "combined_improvement_frontier.csv", combined)
    write_rows(PROCESSED / "alternative_combined_pathways.csv", alternatives)
    write_rows(PROCESSED / "scenario_comparison.csv", [{
        "scenario": "reference" if index == 0 else f"illustrative_combination_to_{int(row['target_lcoe_gbp_per_mwh'])}",
        "source_type": "exploratory" if index == 0 else "mathematical_interpolation",
        "source_id": "ASSUMPTION_THIS_STUDY",
        "price_year": "2024 real GBP",
        "denominator_definition": "parameter-specific boundaries documented in sbsp_parameters.csv",
        "limitation": "not a forecast roadmap probability or engineering design",
        "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh if index == 0 else row.get("lcoe_gbp_per_mwh"),
        "progress_fraction": 0 if index == 0 else row.get("progress_fraction"),
    } for index, row in enumerate([{"target_lcoe_gbp_per_mwh": 0}, *combined])])

    analysis_errors = validate_analysis_results(reference, params, SENSITIVITY_PARAMETERS, thresholds, frontier, combined, alternatives)
    if analysis_errors:
        for error in analysis_errors:
            print(f"ANALYSIS ERROR: {error}")
        return 1

    main_figures = [
        FIGURES / "reference_lcoe_components.png", FIGURES / "one_way_lcoe_floors.png",
        FIGURES / "specific_mass_threshold_focus.png", FIGURES / "combined_progress_frontier.png",
        FIGURES / "uk_electricity_cost_benchmark_comparison.png", FIGURES / "sbsp_break_even_thresholds.png",
        FIGURES / "one_way_threshold_feasibility_matrix.png",
        FIGURES_ZH / "reference_lcoe_components.png", FIGURES_ZH / "one_way_lcoe_floors.png",
        FIGURES_ZH / "specific_mass_threshold_focus.png", FIGURES_ZH / "combined_progress_frontier.png",
        FIGURES_ZH / "uk_electricity_cost_benchmark_comparison.png", FIGURES_ZH / "sbsp_break_even_thresholds.png",
        FIGURES_ZH / "one_way_threshold_feasibility_matrix.png",
    ]
    plot_cost_component_waterfall(reference, main_figures[0]); plot_cost_component_waterfall_zh(reference, main_figures[7])
    plot_one_way_lcoe_floors(importance, main_figures[1]); plot_one_way_lcoe_floors_zh(importance, main_figures[8])
    plot_specific_mass_threshold_focus(sensitivity_rows, thresholds, main_figures[2]); plot_specific_mass_threshold_focus_zh(sensitivity_rows, thresholds, main_figures[9])
    plot_combined_progress_frontier(combined, main_figures[3]); plot_combined_progress_frontier_zh(combined, main_figures[10])
    plot_uk_benchmarks(generation, system, main_figures[4]); plot_uk_benchmarks_zh(generation, system, main_figures[11])
    plot_break_even_frontier(frontier, main_figures[5]); plot_break_even_frontier_zh(frontier, main_figures[12])
    plot_one_way_threshold_matrix(feasibility, main_figures[6]); plot_one_way_threshold_matrix_zh(feasibility, main_figures[13])

    build_web_payload(ROOT / "html/model_data.js", params, combined, configuration)
    build_markdown_report(REPORT / "final_report_EN.md", reference, params, generation, system, thresholds, importance, frontier, combined, alternatives, sources, evidence, assumptions, studies)
    build_markdown_report_zh(REPORT / "final_report_zh.md", reference, params, generation, system, thresholds, importance, frontier, combined, alternatives, sources, evidence, assumptions, studies)
    pdf_en, message_en = try_pdf("final_report_EN.md", "final_report_EN.pdf", "UK SBSP Cost-Condition Assessment v2.0")
    pdf_zh, message_zh = try_pdf("final_report_zh.md", "final_report_zh.pdf", "英国空间太阳能成本条件评估 v2.0", cjk=True)

    expected = [
        PROCESSED / name for name in (
            "reference_lcoe.csv", "reference_energy_chain.csv", "reference_cash_flow.csv",
            "sensitivity_curves.csv", "thresholds_one_way.csv", "one_way_feasibility_matrix.csv",
            "cost_driver_importance.csv", "contour_grids.csv", "launch_efficiency_frontier.csv",
            "combined_improvement_frontier.csv", "alternative_combined_pathways.csv", "scenario_comparison.csv",
        )
    ] + sensitivity_figures + contour_figures + main_figures + [
        ROOT / "html/model_data.js", REPORT / "final_report_EN.md", REPORT / "final_report_zh.md",
    ]
    if pdf_en: expected.append(REPORT / "final_report_EN.pdf")
    if pdf_zh: expected.append(REPORT / "final_report_zh.pdf")
    release_errors = validate_outputs(expected)
    release_errors += validate_generated_csv_outputs([
        {"path": PROCESSED / "reference_lcoe.csv", "row_count": len(reference_rows), "required_columns": ["metric", "value"], "key_columns": ["metric"]},
        {"path": PROCESSED / "reference_energy_chain.csv", "row_count": 6, "required_columns": ["stage", "power_w"], "key_columns": ["stage"]},
        {"path": PROCESSED / "reference_cash_flow.csv", "row_count": len(result.cash_flow_rows), "required_columns": ["year", "phase", "discounted_cost_gbp", "discounted_energy_mwh"], "key_columns": ["year", "phase"]},
        {"path": PROCESSED / "sensitivity_curves.csv", "row_count": len(SENSITIVITY_PARAMETERS) * 101, "required_columns": ["parameter", "value", "lcoe_gbp_per_mwh"]},
        {"path": PROCESSED / "thresholds_one_way.csv", "row_count": len(SENSITIVITY_PARAMETERS) * 5, "required_columns": ["parameter", "target_lcoe_gbp_per_mwh", "status"], "key_columns": ["parameter", "target_lcoe_gbp_per_mwh"]},
        {"path": PROCESSED / "contour_grids.csv", "row_count": len(contour_specs) * 45 * 45, "required_columns": ["x_parameter", "y_parameter", "lcoe_gbp_per_mwh"]},
    ])
    release_errors += validate_png_images(sensitivity_figures + contour_figures + main_figures)
    release_errors += validate_markdown_images([REPORT / "final_report_EN.md", REPORT / "final_report_zh.md"], expected_count=4)
    shared = [
        "v2.0", f"£{result.lcoe_gbp_per_mwh:.2f}/MWh", f"{result.end_to_end_efficiency:.4%}",
        "DESNZ_SBSP_2025", "NASA_OTPS_SBSP_2024",
    ]
    release_errors += validate_report_content([REPORT / "final_report_EN.md", REPORT / "final_report_zh.md"], shared)
    pdf_errors: list[str] = []
    if pdf_en and pdf_zh:
        pdf_errors = validate_pdf_documents([REPORT / "final_report_EN.pdf", REPORT / "final_report_zh.pdf"], ["v2.0"])
    else:
        pdf_errors = ["Both bilingual PDFs were not generated."]
    release_errors += pdf_errors

    categories = [
        {"category": "Numerical model", "status": "PASS" if not analysis_errors else "FAIL", "evidence": "Stage powers, delivered-basis mass, DCF, launch and replacement boundaries reconciled."},
        {"category": "Input metadata", "status": "PASS" if not errors else "FAIL", "evidence": "Every parameter has bilingual source, denominator and limitation metadata."},
        {"category": "Bilingual parity", "status": "PASS" if not validate_report_content([REPORT / "final_report_EN.md", REPORT / "final_report_zh.md"], shared) else "FAIL", "evidence": "English and Chinese reports share version, reference LCOE and computed efficiency."},
        {"category": "Generated artefacts", "status": "PASS" if not release_errors else "FAIL", "evidence": f"Checked {len(expected)} output files plus CSV, PNG, Markdown and PDF structure."},
    ]
    build_verification_note(REPORT / "verification_note.md", categories, [
        "This is a scenario result, not a commercial forecast.",
        "The rectenna proxy does not explicitly model beam geometry, land, weather, safety or power-density constraints.",
        "Architecture inputs may be dependent; exploration bounds are not probability distributions.",
        *release_errors,
    ], ["python -m unittest discover -s tests -v", "python analysis/run_full_analysis.py"])
    if release_errors:
        for error in release_errors:
            print(f"RELEASE ERROR: {error}")
        return 1
    print(f"Reference conditional DCF LCOE: {result.lcoe_gbp_per_mwh:.2f} GBP/MWh")
    print(f"Reference orbital mass: {result.orbital_mass_kg / 1000:,.0f} tonnes")
    print(message_en); print(message_zh); print("Full v2.0 analysis complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
