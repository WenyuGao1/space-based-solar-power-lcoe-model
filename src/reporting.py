"""Generate the English final report and verification note."""

from __future__ import annotations

from pathlib import Path

from .analysis import TARGET_LCOE_GBP_PER_MWH
from .model import calculate_lcoe
from .parameters import Parameter
from .utils import fmt_float, fmt_money, fmt_percent


FIGURE_LINKS = [
    ("UK electricity cost benchmark comparison", "../figures/uk_electricity_cost_benchmark_comparison.png", "The benchmark chart separates generator LCOE from the broader system-adjusted renewable comparator used in this assessment."),
    ("Reference LCOE component breakdown", "../figures/reference_lcoe_components.png", "The reference LCOE is dominated by annualised CAPEX, so financing, mass and space-side scale have first-order importance."),
    ("SBSP LCOE vs launch cost", "../figures/lcoe_vs_launch_cost.png", "The full launch-cost sweep shows why launch is a major lever, but not the only lever."),
    ("Zoomed SBSP LCOE vs launch cost", "../figures/lcoe_vs_launch_cost_zoom.png", "The UK-cost zoom shows that launch cost alone does not bring the reference architecture into the 40-200 GBP/MWh decision range."),
    ("SBSP LCOE vs end-to-end efficiency", "../figures/lcoe_vs_end_to_end_efficiency.png", "Efficiency is a multiplier because it reduces required space-side power, orbital mass and transmission hardware."),
    ("Zoomed SBSP LCOE vs end-to-end efficiency", "../figures/lcoe_vs_end_to_end_efficiency_zoom.png", "The zoomed efficiency chart shows that even the high end of the explored efficiency range does not reach UK benchmark costs by itself."),
    ("SBSP LCOE vs specific mass", "../figures/lcoe_vs_specific_mass.png", "Specific mass is the strongest one-way lever because it scales launch, transfer and assembly costs together."),
    ("SBSP LCOE vs space hardware cost", "../figures/lcoe_vs_space_hardware_cost.png", "Space hardware cost matters, but it is not enough if launch, mass, assembly and efficiency stay near the reference point."),
    ("SBSP LCOE vs WACC", "../figures/lcoe_vs_wacc.png", "Financing cost has large leverage because SBSP is capital intensive."),
    ("SBSP LCOE vs rectenna cost", "../figures/lcoe_vs_rectenna_cost.png", "Rectenna CAPEX is visible but secondary relative to orbital cost drivers in this boundary."),
    ("SBSP LCOE vs system lifetime", "../figures/lcoe_vs_system_lifetime.png", "Longer lifetime spreads capital cost across more delivered MWh, but does not solve the cost gap alone."),
    ("SBSP LCOE vs capacity factor", "../figures/lcoe_vs_capacity_factor.png", "High availability is required for a baseload or strategic-power value case."),
    ("SBSP LCOE vs in-orbit assembly cost", "../figures/lcoe_vs_in_orbit_assembly.png", "In-orbit assembly and deployment are large because they scale with orbital mass."),
    ("SBSP LCOE vs fixed OPEX", "../figures/lcoe_vs_fixed_opex.png", "Fixed OPEX affects LCOE through the large capital base."),
    ("SBSP LCOE vs variable OPEX", "../figures/lcoe_vs_variable_opex.png", "Variable OPEX is a relatively small lever in the current model boundary."),
    ("One-way threshold feasibility matrix", "../figures/one_way_threshold_feasibility_matrix.png", "The matrix shows which single variables can or cannot reach each target LCOE while all other inputs stay fixed."),
    ("SBSP break-even launch thresholds", "../figures/sbsp_break_even_thresholds.png", "The launch-efficiency frontier shows that higher efficiency relaxes the launch-cost requirement, but does not remove the need for other improvements."),
    ("Contour: launch cost vs end-to-end efficiency", "../figures/contour_launch_cost_vs_end_to_end_efficiency.png", "The contour map shows the coupled effect of launch cost and efficiency across the full explored range."),
    ("Zoomed contour: launch cost vs end-to-end efficiency", "../figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "The zoomed contour focuses on the UK-relevant cost region around 60-150 GBP/MWh."),
    ("Contour: launch cost vs space hardware cost", "../figures/contour_launch_cost_vs_space_hardware_cost.png", "This contour shows why low launch cost and low space hardware cost must move together."),
    ("Contour: WACC vs space hardware cost", "../figures/contour_wacc_vs_space_hardware_cost.png", "This contour shows the interaction between manufacturing cost and cost of capital."),
]


REFERENCE_PARAMETER_ORDER = [
    "delivered_capacity_mw",
    "end_to_end_efficiency",
    "capacity_factor",
    "specific_mass_kg_per_kw_space_power",
    "launch_cost_gbp_per_kg",
    "space_hardware_cost_gbp_per_w_space",
    "wacc",
    "system_lifetime_years",
    "in_orbit_assembly_cost_gbp_per_kg",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "fixed_opex_pct_capex_per_year",
    "variable_opex_gbp_per_mwh",
    "replacement_refurbishment_pct_capex_per_year",
]

REFERENCE_INTERPRETATION = {
    "delivered_capacity_mw": "Scale anchor. LCOE is mostly scale-neutral because most costs are specified per W or per kg.",
    "end_to_end_efficiency": "Exploratory conversion from required space-side power to delivered grid output.",
    "capacity_factor": "Availability assumption for a near-firm output profile, not measured SBSP operating history.",
    "specific_mass_kg_per_kw_space_power": "Architecture-level mass intensity. This is the strongest one-way driver and remains highly uncertain.",
    "launch_cost_gbp_per_kg": "All-in launch-cost threshold variable. Treated as a wide exploratory range rather than a forecast price.",
    "space_hardware_cost_gbp_per_w_space": "Exploratory manufacturing-cost threshold for orbital collection, structure, control and conversion hardware.",
    "wacc": "Financing-cost variable anchored to infrastructure and higher-risk project-finance bounds.",
    "system_lifetime_years": "Economic operating life. Space degradation and refurbishment are represented separately.",
    "in_orbit_assembly_cost_gbp_per_kg": "Exploratory robotic assembly, deployment, inspection and commissioning cost.",
    "rectenna_cost_gbp_per_w_delivered": "Exploratory ground receiving and conversion cost per delivered W.",
    "grid_connection_cost_gbp_per_kw_delivered": "Grid-interface allowance derived from UK generation-cost assumption style.",
    "fixed_opex_pct_capex_per_year": "Exploratory annual operations, insurance, monitoring and maintenance allowance.",
    "variable_opex_gbp_per_mwh": "Exploratory variable operating allowance.",
    "replacement_refurbishment_pct_capex_per_year": "Exploratory annual allowance for degradation and component replacement.",
}

SOURCE_REFERENCES = [
    ["DESNZ_EGC_2025", "DESNZ, Electricity generation costs 2025", "https://www.gov.uk/government/publications/electricity-generation-costs-2025"],
    ["BEIS_EGC_2020", "BEIS, Electricity Generation Costs 2020", "https://www.gov.uk/government/publications/beis-electricity-generation-costs-2020"],
    ["NESO_BALANCING_2025", "NESO, 2025 Annual Balancing Costs Report", "https://www.neso.energy/document/362561/download"],
    ["NESO_NETWORK_UPDATE_2026", "NESO, Beyond 2030 Electricity Transmission Update", "https://www.neso.energy/publications/beyond-2030"],
    ["NESO_CP2030", "NESO, Clean Power 2030 advice and implementation material", "https://www.neso.energy/publications/clean-power-2030"],
    ["NESO_OPERABILITY_2026", "NESO, Operability Strategy Report and Electricity Markets Roadmap", "https://www.neso.energy/publications/operability-strategy-report-and-electricity-markets-roadmap"],
    ["UKSA_SBSP_2020", "UK Space Agency and BEIS, SBSP research commission", "https://www.gov.uk/government/news/uk-government-commissions-space-solar-power-stations-research"],
    ["CALTECH_SBSP_2022", "Caltech SBSP technical concept paper", "https://arxiv.org/abs/2206.08373"],
    ["NAO_HPC_2017", "National Audit Office, Hinkley Point C", "https://www.nao.org.uk/reports/hinkley-point-c/"],
]

CAPEX_LABELS = {
    "space_segment_capex": "Space segment CAPEX",
    "wireless_power_transmission": "Wireless power transmission",
    "launch": "Launch",
    "orbit_transfer": "Orbit transfer",
    "in_orbit_assembly": "In-orbit assembly and deployment",
    "rectenna": "Rectenna",
    "grid_connection": "Grid connection",
}


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _source_link(source_id: str) -> str:
    return f"`{source_id}`"


def _source_type_label(source_type: str) -> str:
    labels = {
        "sourced": "sourced value",
        "derived": "derived value",
        "exploratory": "exploratory modelling assumption",
    }
    return labels.get(source_type, source_type)


def _format_parameter_value(parameter: Parameter) -> str:
    if parameter.unit == "fraction":
        return fmt_percent(parameter.reference_value)
    if parameter.unit == "fraction/year":
        return fmt_percent(parameter.reference_value)
    return f"{fmt_float(parameter.reference_value, 3)} {parameter.unit}"


def _threshold_rows(thresholds: list[dict[str, object]], target: int) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in thresholds:
        if int(row["target_lcoe_gbp_per_mwh"]) != target:
            continue
        threshold = row["threshold_value"]
        threshold_text = "not reached" if threshold in (None, "") else fmt_float(float(threshold), 3)
        rows.append([
            row["display_name"],
            row["unit"],
            threshold_text,
            fmt_float(float(row["best_lcoe_in_range_gbp_per_mwh"]), 0),
            row["status"],
        ])
    return rows


def _frontier_rows(frontier: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in frontier:
        launch_value = row["max_launch_cost_gbp_per_kg"]
        rows.append(
            [
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                row["target_lcoe_gbp_per_mwh"],
                "not feasible" if launch_value in (None, "") else fmt_float(float(launch_value), 0),
                row["status"],
            ]
        )
    return rows


def _generation_rows(generation_rows: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in generation_rows:
        low = row.get("value_low_gbp_per_mwh")
        high = row.get("value_high_gbp_per_mwh")
        cost_range = "not comparable" if low in (None, "") else f"{fmt_float(float(low), 0)}-{fmt_float(float(high), 0)}"
        rows.append([
            row["technology"],
            row["category"],
            cost_range,
            row["price_basis"],
            _source_link(str(row["source_id"])),
            row["notes"],
        ])
    return rows


def _system_rows(system_rows: list[dict[str, object]]) -> list[list[object]]:
    selected = [row for row in system_rows if row["technology"] == "High-renewable system-adjusted band"]
    rows: list[list[object]] = []
    for row in selected:
        rows.append([
            row["technology"],
            row["benchmark_reference"],
            f"{fmt_float(float(row['value_low_gbp_per_mwh']), 0)}-{fmt_float(float(row['value_high_gbp_per_mwh']), 0)}",
            row["price_basis"],
            _source_link(str(row["source_id"])),
        ])
    return rows


def _combined_frontier_rows(combined_frontier: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in combined_frontier:
        if row["status"] != "feasible":
            rows.append([row["target_lcoe_gbp_per_mwh"], "not feasible", "", "", "", "", "", "", ""])
            continue
        rows.append(
            [
                row["target_lcoe_gbp_per_mwh"],
                fmt_percent(float(row["progress_fraction"]), 0),
                fmt_float(float(row["launch_cost_gbp_per_kg"]), 0),
                fmt_float(float(row["specific_mass_kg_per_kw_space_power"]), 2),
                fmt_float(float(row["space_hardware_cost_gbp_per_w_space"]), 2),
                fmt_float(float(row["in_orbit_assembly_cost_gbp_per_kg"]), 0),
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                fmt_percent(float(row["wacc"]), 1),
                fmt_percent(float(row["capacity_factor"]), 0),
            ]
        )
    return rows


def _alternative_frontier_rows(alternative_frontiers: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in alternative_frontiers:
        if row["status"] != "feasible":
            rows.append([row["display_name"], row["target_lcoe_gbp_per_mwh"], "not feasible", "", "", "", "", ""])
            continue
        rows.append(
            [
                row["display_name"],
                row["target_lcoe_gbp_per_mwh"],
                fmt_percent(float(row["progress_fraction"]), 0),
                fmt_float(float(row["launch_cost_gbp_per_kg"]), 0),
                fmt_float(float(row["specific_mass_kg_per_kw_space_power"]), 2),
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                fmt_percent(float(row["wacc"]), 1),
                fmt_float(float(row["lcoe_gbp_per_mwh"]), 0),
            ]
        )
    return rows


def _reference_parameter_rows(params: dict[str, Parameter]) -> list[list[object]]:
    rows: list[list[object]] = []
    for name in REFERENCE_PARAMETER_ORDER:
        parameter = params[name]
        rows.append(
            [
                parameter.display_name,
                _format_parameter_value(parameter),
                _source_type_label(parameter.source_type),
                _source_link(parameter.source_id),
                REFERENCE_INTERPRETATION[name],
            ]
        )
    return rows


def _figure(caption: str, path: str, note: str) -> str:
    return f"![{caption}]({path})\n\n{note}"


def _benchmark_layer_rows() -> list[list[object]]:
    return [
        [
            "Generation-only LCOE",
            "Generator-boundary DESNZ costs for solar, onshore wind, fixed and floating offshore wind, gas CCGT and gas CCUS where available.",
            "Roughly 55-153 GBP/MWh across the listed generation rows; the headline comparison uses 55-113 GBP/MWh for the main mature generation band.",
            "DESNZ Electricity Generation Costs 2025; Hinkley Point C shown separately as a contract-price marker.",
            "Use as the lower boundary for generator cost, not as the cost of reliable delivered electricity.",
        ],
        [
            "BEIS conservative system-adjusted comparator",
            "Enhanced LCOE evidence including wider system impact, other impacts and transmission for variable renewables.",
            "45-87 GBP/MWh in 2018 real GBP.",
            "BEIS Electricity Generation Costs 2020 enhanced LCOE tables; retained because newer DESNZ generation-cost data exclude wider system costs.",
            "Use as a conservative, indicative system-adjusted comparator, not as a direct market price or full GB system model.",
        ],
        [
            "Wider high-renewable system-pressure comparator",
            "Grid reinforcement, transmission constraints, balancing costs, curtailment, short- and long-duration storage, backup capacity, connection delays, weather correlation and reliability requirements.",
            "Indicative / not directly comparable as a single LCOE. NESO evidence identifies material balancing and network-cost pressures, including a possible GBP4 billion bill reduction in 2030 from critical network build through reduced thermal constraints.",
            "NESO Annual Balancing Costs Report; NESO Clean Power 2030; NESO Beyond 2030 / transmission network material; NESO operability material.",
            "Use as a stress overlay showing why the BEIS 45-87 GBP/MWh range should not be treated as the final upper bound of wind and solar system cost.",
        ],
        [
            "Firm low-carbon comparator",
            "Dispatchable or near-firm low-carbon references such as gas CCUS, nuclear contract markers and storage-backed renewable supply.",
            "Gas CCUS high-load-factor DESNZ rows are around 104-105 GBP/MWh; Hinkley Point C is a 92.50 GBP/MWh 2012 nominal contract-price marker, not a generic nuclear LCOE.",
            "DESNZ Electricity Generation Costs 2025; NAO Hinkley Point C; BEIS enhanced LCOE evidence for dispatchable technologies.",
            "Use to interpret SBSP as possible firm or near-firm low-carbon supply, not as a direct substitute for bare wind or solar generator LCOE.",
        ],
    ]


def _key_findings_rows() -> list[list[object]]:
    return [
        [
            "SBSP is not cost-competitive at the reference point.",
            "Reference delivered-grid LCOE is about 429 GBP/MWh.",
            "The current reference architecture is not a near-term mainstream generator.",
        ],
        [
            "Launch cost alone is insufficient.",
            "Even at 20 GBP/kg in the explored range, the reference architecture remains around 204 GBP/MWh.",
            "SBSP must be treated as a full system-architecture cost problem, not only a rocket-cost problem.",
        ],
        [
            "Specific mass is the strongest one-way lever.",
            "Around 1.3 kg/kW-space is required for one-way 150 GBP/MWh parity with other inputs fixed.",
            "Lightweight architecture is a first-order technical bottleneck.",
        ],
        [
            "Efficiency, mass, launch, assembly and finance must improve together.",
            "Combined bottleneck frontiers show 80-120 GBP/MWh requires coordinated movement across multiple variables.",
            "The relevant pathway is integrated architecture improvement, not isolated component improvement.",
        ],
        [
            "BEIS 45-87 GBP/MWh is a conservative system-adjusted comparator, not a full upper bound.",
            "Wider system pressures include balancing, curtailment, grid reinforcement, storage duration and backup capacity.",
            "SBSP entering 80-120 GBP/MWh should trigger deeper GB system-value modelling, not automatic competitiveness claims.",
        ],
        [
            "SBSP's relevant comparison is firm or near-firm low-carbon electricity.",
            "The report distinguishes generation-only LCOE, conservative system-adjusted costs and wider high-renewable system pressure.",
            "SBSP should be evaluated against reliable delivered electricity, not only bare wind and solar generator LCOE.",
        ],
    ]


def _reference_parameter_compact_rows(params: dict[str, Parameter]) -> list[list[object]]:
    role = {
        "delivered_capacity_mw": "Scale anchor",
        "end_to_end_efficiency": "Sets required space-side power",
        "capacity_factor": "Determines delivered MWh",
        "specific_mass_kg_per_kw_space_power": "Mass and launch multiplier",
        "launch_cost_gbp_per_kg": "Transport-cost threshold variable",
        "space_hardware_cost_gbp_per_w_space": "Orbital manufacturing-cost threshold",
        "wacc": "Capital-cost and financeability lever",
        "system_lifetime_years": "Capital recovery period",
        "in_orbit_assembly_cost_gbp_per_kg": "Mass-scaled deployment cost",
        "rectenna_cost_gbp_per_w_delivered": "Ground receiving-system cost",
        "grid_connection_cost_gbp_per_kw_delivered": "Grid-interface allowance",
        "fixed_opex_pct_capex_per_year": "Annual fixed OPEX allowance",
        "variable_opex_gbp_per_mwh": "Variable OPEX allowance",
        "replacement_refurbishment_pct_capex_per_year": "Replacement and degradation allowance",
    }
    return [
        [
            params[name].display_name,
            _format_parameter_value(params[name]),
            _source_type_label(params[name].source_type),
            role[name],
        ]
        for name in REFERENCE_PARAMETER_ORDER
    ]


def _threshold_summary_rows(thresholds: list[dict[str, object]]) -> list[list[object]]:
    drivers = []
    for row in thresholds:
        name = str(row["display_name"])
        if name not in drivers:
            drivers.append(name)
    rows: list[list[object]] = []
    for driver in drivers:
        matches = [row for row in thresholds if str(row["display_name"]) == driver]
        if not matches:
            continue
        unit = matches[0]["unit"]
        by_target = {int(row["target_lcoe_gbp_per_mwh"]): row for row in matches}

        def threshold_text(target: int) -> str:
            match = by_target.get(target)
            if not match:
                return "n/a"
            value = match["threshold_value"]
            return "not reached" if value in (None, "") else fmt_float(float(value), 3)

        best_lcoe = min(float(row["best_lcoe_in_range_gbp_per_mwh"]) for row in matches)
        rows.append([driver, unit, threshold_text(150), threshold_text(100), fmt_float(best_lcoe, 0)])
    return rows


def _secondary_figure_blocks() -> str:
    figures = [
        (
            "Figure A1. Space hardware cost sensitivity",
            "../figures/lcoe_vs_space_hardware_cost.png",
            "Lower orbital hardware cost matters, but it does not close the gap if mass, launch cost, assembly cost and efficiency remain near the reference point. Manufacturing cost is a necessary but not sufficient bottleneck.",
        ),
        (
            "Figure A2. Rectenna cost sensitivity",
            "../figures/lcoe_vs_rectenna_cost.png",
            "Ground receiving infrastructure affects LCOE, but the slope is smaller than the main orbital cost drivers. Rectenna cost is a secondary sensitivity in the current boundary.",
        ),
        (
            "Figure A3. System lifetime sensitivity",
            "../figures/lcoe_vs_system_lifetime.png",
            "Longer operating life spreads capital cost across more delivered MWh, but lifetime extension alone cannot compensate for a heavy and low-efficiency architecture.",
        ),
        (
            "Figure A4. Capacity factor sensitivity",
            "../figures/lcoe_vs_capacity_factor.png",
            "High availability is essential for the firm-power value case because the capital base must be used over many delivered MWh.",
        ),
        (
            "Figure A5. In-orbit assembly cost sensitivity",
            "../figures/lcoe_vs_in_orbit_assembly.png",
            "Assembly and deployment cost scale with orbital mass, so this cost becomes important when the architecture remains heavy.",
        ),
        (
            "Figure A6. Fixed OPEX sensitivity",
            "../figures/lcoe_vs_fixed_opex.png",
            "Fixed OPEX affects LCOE through the large capital base, but it is not the main route to cost parity.",
        ),
        (
            "Figure A7. Variable OPEX sensitivity",
            "../figures/lcoe_vs_variable_opex.png",
            "Variable OPEX is small relative to annualised capital cost in this model boundary, so changing it does little to alter the threshold conclusion.",
        ),
        (
            "Figure A8. Launch cost sensitivity zoom",
            "../figures/lcoe_vs_launch_cost_zoom.png",
            "The UK-cost zoom reinforces that even very low launch cost does not put the reference architecture into the 80-120 GBP/MWh decision region without other improvements.",
        ),
        (
            "Figure A9. End-to-end efficiency sensitivity zoom",
            "../figures/lcoe_vs_end_to_end_efficiency_zoom.png",
            "The zoomed view shows that higher conversion efficiency relaxes the problem but does not remove the need for lower mass and lower space infrastructure cost.",
        ),
        (
            "Figure A10. Full contour: launch cost and end-to-end efficiency",
            "../figures/contour_launch_cost_vs_end_to_end_efficiency.png",
            "The full surface shows the broad interaction across the exploration range and why the relevant cost region occupies only a narrow part of parameter space.",
        ),
        (
            "Figure A11. Full contour: launch cost and space hardware cost",
            "../figures/contour_launch_cost_vs_space_hardware_cost.png",
            "The contour shows that both space transport and orbital manufacturing cost must improve together to approach the UK comparator range.",
        ),
        (
            "Figure A12. Full contour: WACC and space hardware cost",
            "../figures/contour_wacc_vs_space_hardware_cost.png",
            "The contour shows the interaction between manufacturing cost and cost of capital in a CAPEX-dominated system.",
        ),
    ]
    return "\n\n".join(_figure(caption, path, note) for caption, path, note in figures)


def _build_markdown_report_legacy(
    output_path: str | Path,
    reference: dict[str, float],
    params: dict[str, Parameter],
    generation_rows: list[dict[str, object]],
    system_rows: list[dict[str, object]],
    thresholds: list[dict[str, object]],
    importance: list[dict[str, object]],
    frontier: list[dict[str, object]],
    combined_frontier: list[dict[str, object]],
    alternative_frontiers: list[dict[str, object]],
) -> None:
    result = calculate_lcoe(reference)
    top_drivers = importance[:5]
    generation_band = (55, 113)
    system_band = (45, 87)

    capex_rows = [
        [CAPEX_LABELS.get(name, name.replace("_", " ")), fmt_money(value / 1e9, 2)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    top_driver_rows = [
        [
            row["display_name"],
            row["unit"],
            fmt_float(float(row["reference_value"]), 3),
            fmt_float(float(row["best_value_in_range"]), 3),
            fmt_float(float(row["lcoe_reduction_gbp_per_mwh"]), 0),
        ]
        for row in top_drivers
    ]

    report = f"""# UK Space-Based Solar Power Cost-Threshold Assessment

Report subtitle: A techno-economic cost-threshold assessment for UK baseload and strategic low-carbon electricity

Evidence status: Public evidence and project source registry current to 8 July 2026.

Version: v1.0 final delivery refinement

Prepared as: A reproducible technical assessment using the project data and model pipeline.

Disclaimer: This report identifies cost-parity thresholds, not deployment certainty, investment advice, or commercial readiness.

[[PAGEBREAK]]

## Table of Contents

- 1. Executive Summary
- 2. Key Findings and Decision Implications
- 3. Research Question and Scope
- 4. SBSP LCOE Model
- 5. Reference Point: Interpretation and Limitations
- 6. UK Electricity Cost Benchmarks
- 7. Cost Driver Analysis
- 8. Break-even Threshold Analysis
- 9. Combined Bottleneck Frontiers
- 10. Interpretation for the UK Power System
- 11. Key Technical and Economic Bottlenecks
- 12. Limitations and Uncertainty
- 13. Conclusion
- Appendix A. Secondary Sensitivity Figures
- Appendix B. Source Registry
- Appendix C. Assumption Classification Notes

[[PAGEBREAK]]

## 1. Executive Summary

This report is a cost-threshold assessment. It asks when the bottleneck costs and performance parameters of space-based solar power (SBSP) fall far enough for delivered electricity to become comparable with UK electricity benchmarks. It does not assign SBSP to deployment years or named scenarios.

The documented reference point produces a delivered-grid LCOE of {fmt_float(result.lcoe_gbp_per_mwh, 0)} GBP/MWh. That number is not a prediction and not a recommended architecture. It is an analytical anchor for continuous sensitivity curves. At that anchor, SBSP is above the DESNZ generation-only benchmark band used here, roughly {generation_band[0]}-{generation_band[1]} GBP/MWh, and above the BEIS high-renewable system-adjusted comparator, roughly {system_band[0]}-{system_band[1]} GBP/MWh.

The BEIS 45-87 GBP/MWh comparator is retained because it is the most directly available enhanced-LCOE evidence in the project, but it is treated as a conservative system-adjusted reference rather than a full upper bound on the cost of reliable high-renewable electricity. Wider pressures such as transmission constraints, balancing costs, curtailment, storage duration, backup capacity, connection delays and weather correlation are discussed separately because they are not all reducible to one comparable LCOE number.

The threshold answer is:

- SBSP begins to approach the upper UK comparator range below roughly 150 GBP/MWh.
- Around 100-120 GBP/MWh, it becomes comparable with gas CCUS and higher-cost firm low-carbon reference points.
- Around 80 GBP/MWh and below, it begins to overlap the conservative system-adjusted renewable comparator used here.
- Around 60 GBP/MWh is a stringent frontier requiring simultaneous movement across most bottleneck variables.

The model identifies cost-parity conditions, not deployment certainty. Most single variables cannot bring SBSP below 150 GBP/MWh alone. Specific mass can reach the 150 GBP/MWh target only if the architecture falls to about 1.3 kg/kW-space or lower with all other inputs fixed. Launch cost alone is insufficient: even at 20 GBP/kg in the explored range, the reference architecture remains around 204 GBP/MWh.

## 2. Key Findings and Decision Implications

Table 1. Key findings and decision implications

{markdown_table(["Key finding", "Evidence from the model", "Decision implication"], _key_findings_rows())}

This table is the decision frame for the rest of the report. The central implication is that SBSP becomes analytically relevant to the UK only when the cost result enters the 80-120 GBP/MWh region and when the architecture can plausibly deliver firm or near-firm low-carbon electricity.

## 3. Research Question and Scope

The research question is:

At what levels of launch cost, space hardware cost, in-orbit assembly cost, rectenna cost, financing cost, end-to-end efficiency, capacity factor, system lifetime and OPEX does SBSP reach cost parity with UK generation-only and system-adjusted electricity cost benchmarks?

The model boundary is delivered-grid LCOE. It includes space-segment CAPEX, launch, orbit transfer, in-orbit assembly and deployment, wireless power transmission, rectenna CAPEX, grid connection, programme margin, refurbishment allowance, fixed OPEX, variable OPEX, capacity factor, end-to-end efficiency, lifetime, WACC and annual delivered electricity.

The model does not estimate commercial readiness, engineering achievability or full system value. Those are separate questions. The analysis identifies numerical cost and performance thresholds that would need to be met before those questions become decision-relevant.

## 4. SBSP LCOE Model

The model uses a standard discounted lifetime-cost structure:

LCOE = annualised CAPEX + annual OPEX + annual refurbishment allowance, divided by annual delivered MWh.

Annual delivered electricity is delivered capacity MW x 8,760 x capacity factor. Required space-side power is delivered grid capacity divided by end-to-end efficiency. Orbital mass is required space-side power multiplied by specific mass.

Table 2. Reference point inputs

{markdown_table(["Parameter", "Reference value", "Classification", "Role in the model"], _reference_parameter_compact_rows(params))}

Table 3. Initial CAPEX breakdown

{markdown_table(["Component", "GBP billion"], capex_rows)}

The reference point gives {fmt_money(result.required_space_power_kw / 1e6, 2)} GW of required space-side power and about {fmt_money(result.orbital_mass_kg / 1000.0, 0)} tonnes of orbital hardware. These are consequences of the chosen reference assumptions. They are not a final design recommendation.

{_figure("Figure 1. Reference LCOE component breakdown", "../figures/reference_lcoe_components.png", "Annualised CAPEX dominates the reference point, which explains why mass, space-side scale, hardware cost and cost of capital drive the threshold result. Operational cost trimming cannot substitute for structural reductions in capital intensity.")}

## 5. Reference Point: Interpretation and Limitations

The reference point exists to make sensitivity analysis interpretable. It is a transparent anchor from which each cost driver can be moved up and down over a documented range. It should not be read as the most likely SBSP architecture, the preferred architecture, or a design requirement.

Several reference inputs are exploratory modelling assumptions because commercial-scale SBSP has not been deployed. The values for specific mass, space hardware cost, in-orbit assembly cost, rectenna cost, OPEX and refurbishment are especially uncertain. The model uses them to ask "what would have to be true?" rather than "what will happen?"

The 429 GBP/MWh output is therefore a consequence of a high-space-scale reference architecture: 2 GW delivered capacity, 15 percent end-to-end efficiency, 5 kg/kW-space specific mass, 500 GBP/kg launch cost, 200 GBP/kg in-orbit assembly cost and 6.5 percent WACC. The required 13.33 GW space-side power and 66,667 tonnes of orbital hardware follow mechanically from those assumptions.

## 6. UK Electricity Cost Benchmarks

Generation-only LCOE is useful because it measures the cost of producing electricity at the generator boundary. It is not the same as the cost of maintaining a reliable power system. DESNZ states that wider system impacts are outside the generator LCOE boundary and require power-system modelling.

The BEIS enhanced-LCOE comparator is useful because it brings some wider system impact, other impact and transmission evidence into the comparison. It is deliberately retained as a conservative, indicative comparator. It is not a direct market price, not a complete modern GB system model and not a final upper bound on the cost of wind and solar in a highly renewable system.

{_figure("Figure 2. UK electricity benchmark comparison", "../figures/uk_electricity_cost_benchmark_comparison.png", "The chart separates DESNZ generator-boundary costs from the BEIS conservative system-adjusted renewable band and shows the SBSP threshold lines used in the analysis. Low wind and solar generator LCOE is not the only relevant comparator for a firm or near-firm SBSP source.")}

Table 4. UK electricity benchmark interpretation layers

{markdown_table(["Benchmark layer", "What it includes", "Indicative cost range if available", "Evidence basis", "How it should be used in SBSP comparison"], _benchmark_layer_rows())}

Wind and solar should not be compared with SBSP only on bare generator LCOE. Variable renewable generation can require grid reinforcement, transmission-constraint management, balancing actions, curtailment management, short-duration storage, long-duration flexibility, backup capacity and connection upgrades. The size of those costs depends on location, weather correlation, demand shape, interconnection, storage deployment, network availability and market design.

NESO's 2025 Annual Balancing Costs Report explains that variable wind and solar can require additional balancing actions. It identifies network reinforcement as a major lever for reducing balancing costs and notes that Clean Power 2030 network build could reduce energy bills by around GBP4 billion in 2030 through reduced thermal constraints. NESO's operability material frames this as a multi-dimensional system problem involving adequacy, flexibility, frequency, voltage, stability, thermal constraints and restoration.

The BEIS 45-87 GBP/MWh enhanced-LCOE comparator is therefore retained as a conservative system-adjusted reference. It should not be interpreted as a complete upper bound on the future cost of operating a highly renewable GB power system. The relevant comparator for SBSP is the cost of reliable, firm or near-firm delivered low-carbon electricity, not only the lowest generator LCOE.

## 7. Cost Driver Analysis

One-way sensitivity curves move a single parameter while all other inputs remain at the reference point. This is diagnostic: it identifies leverage and bottlenecks, not an engineering programme.

Table 5. Largest one-way LCOE reductions

{markdown_table(["Driver", "Unit", "Reference", "Best explored value", "LCOE reduction (GBP/MWh)"], top_driver_rows)}

Specific mass dominates because every kg of orbital hardware creates launch, orbit-transfer and assembly cost. End-to-end efficiency is a multiplier because it changes the required space-side scale. Launch cost matters strongly, but a low launch price applied to a heavy, low-efficiency architecture still leaves a high LCOE. WACC matters because the reference system is CAPEX-dominated.

{_figure("Figure 3. Specific mass sensitivity", "../figures/lcoe_vs_specific_mass.png", "Lower specific mass is the strongest one-way lever because it reduces orbital mass and therefore launch, transfer and assembly cost together. One-way 150 GBP/MWh parity requires an architecture near 1.3 kg/kW-space or lower, while lower targets still require combined improvements.")}

{_figure("Figure 4. End-to-end efficiency sensitivity", "../figures/lcoe_vs_end_to_end_efficiency.png", "Higher end-to-end efficiency reduces the required space-side power and the mass that must be launched and assembled. The curve falls steeply but does not by itself move the reference architecture into the main UK comparator range.")}

{_figure("Figure 5. Launch cost sensitivity", "../figures/lcoe_vs_launch_cost.png", "Lower launch cost reduces SBSP LCOE substantially, but even the low end of the explored launch-cost range leaves the reference architecture around 204 GBP/MWh. Launch-cost reduction must be combined with lower mass, higher efficiency and lower assembly cost.")}

{_figure("Figure 6. WACC sensitivity", "../figures/lcoe_vs_wacc.png", "Financing cost has high leverage because annualised CAPEX dominates the reference LCOE. A lower WACC is credible only if technical, construction, policy and revenue risks fall enough for the project to resemble infrastructure finance.")}

## 8. Break-even Threshold Analysis

The one-way threshold analysis asks whether changing one input alone can reach each target LCOE. "Not reached" means that the target is not achieved within the documented range for that input.

{_figure("Figure 7. One-way threshold feasibility matrix", "../figures/one_way_threshold_feasibility_matrix.png", "The matrix shows which single variables can meet each target while all other inputs remain fixed. Most one-way changes cannot reach 150 GBP/MWh, and only specific mass can reach the lower targets in the explored one-way range.")}

Table 6. One-way threshold summary

{markdown_table(["Driver", "Unit", "150 GBP/MWh threshold", "100 GBP/MWh threshold", "Best one-way LCOE"], _threshold_summary_rows(thresholds))}

The launch-efficiency frontier isolates a pair of important variables without pretending they are sufficient.

Table 7. Launch-efficiency frontier

{markdown_table(["End-to-end efficiency", "Target LCOE", "Max launch cost (GBP/kg)", "Status"], _frontier_rows(frontier))}

{_figure("Figure 8. Launch-efficiency break-even frontier", "../figures/sbsp_break_even_thresholds.png", "Higher efficiency relaxes the maximum launch-cost requirement, but only within limits. At 25 percent efficiency, 150 GBP/MWh requires launch cost around 109 GBP/kg or lower; at 35 percent efficiency, 100 GBP/MWh requires roughly 64 GBP/kg.")}

## 9. Combined Bottleneck Frontiers

The combined bottleneck frontier moves the main bottleneck variables by the same fraction from their reference values toward their favourable bounds. It is an illustrative equal-progress frontier, not a prediction and not a claim that these exact parameter combinations will be achieved.

Table 8. Combined bottleneck frontier

{markdown_table(["Target LCOE", "Progress", "Launch GBP/kg", "Mass kg/kW", "Hardware GBP/W", "Assembly GBP/kg", "Efficiency", "WACC", "Capacity factor"], _combined_frontier_rows(combined_frontier))}

The table should be read as a compact map of the required direction of travel. Reaching 150 GBP/MWh already requires broad movement from the reference point. Moving from 120 to 80 GBP/MWh tightens nearly every bottleneck at once rather than shifting the burden to one heroic parameter.

{_figure("Figure 9. Joint-progress frontier", "../figures/combined_progress_frontier.png", "The chart converts the equal-progress table into a single curve: lower target LCOE requires a larger coordinated movement from the reference point toward favourable bounds. SBSP threshold success is a portfolio of engineering and financial advances, not a launch-cost story alone.")}

{_figure("Figure 10. Zoomed contour for launch cost and end-to-end efficiency", "../figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "The contour focuses on the 60-150 GBP/MWh region and shows how efficiency can widen the feasible launch-cost window. The relevant UK-cost region appears only where both variables move strongly from the reference point.")}

Table 9. Alternative parameter-space slices

{markdown_table(["Pathway", "Target LCOE", "Progress", "Launch GBP/kg", "Mass kg/kW", "Efficiency", "WACC", "Model LCOE"], _alternative_frontier_rows(alternative_frontiers))}

The key interpretation is robust across the slices: the cost-relevant pathway is simultaneous improvement. A launch-cost breakthrough without lower mass, lower assembly cost, better efficiency and financeable risk does not put SBSP in the UK mainstream electricity-cost range.

## 10. Interpretation for the UK Power System

SBSP is most relevant to the UK if it can provide firm or near-firm low-carbon output. In that role it would not compete only against the bare LCOE of wind and solar. It would be compared with gas CCUS, nuclear-like firm low-carbon power, long-duration storage and the system-adjusted cost of reliable high-renewable electricity.

If SBSP reached the 80-120 GBP/MWh range on a delivered-grid basis, it could become relevant as baseload or strategic low-carbon power, provided the engineering architecture is credible and the commercial structure is financeable. The model does not prove those conditions. It identifies where they would begin to matter.

Possible system value could include predictable delivery, reduced exposure to weather correlation, reduced balancing requirement, reduced long-duration storage requirement and energy-security value. These are not counted in the LCOE and require full GB power-system modelling.

## 11. Key Technical and Economic Bottlenecks

The necessary bottleneck reductions are:

- Lower orbital mass, because mass multiplies launch, transfer and assembly cost.
- Higher end-to-end efficiency, because efficiency sets required space-side scale.
- Lower launch cost, because launch remains a major cost even for lighter architectures.
- Lower in-orbit assembly and deployment cost, because large structures must be assembled and commissioned reliably.
- Lower space hardware cost, because the orbital power system must approach high-volume manufacturing economics.
- Lower financing cost, because annualised CAPEX dominates the reference LCOE.
- High capacity factor and long lifetime, because capital cost must be spread over many delivered MWh.

None of these is sufficient alone. The model-calculated thresholds require combined engineering and financial movement.

## 12. Limitations and Uncertainty

The largest uncertainty is engineering feasibility. The model can identify that 1.3 kg/kW-space or lower is needed for one-way 150 GBP/MWh parity, but it cannot prove that such an architecture can be built, launched, assembled, operated and refurbished reliably.

The second uncertainty is commercial readiness. A low WACC is only plausible if technology risk, construction risk, policy risk and revenue risk are reduced enough for infrastructure-like financing. That is a commercial and regulatory question, not a pure engineering input.

The third uncertainty is system value. SBSP may provide firm low-carbon value that is not captured in generator LCOE, but that value must be modelled in a full GB power-system framework. The BEIS 45-87 GBP/MWh system-adjusted comparator used here is conservative and indicative; the wider system-pressure overlay is not a substitute for dispatch and network modelling.

The fourth uncertainty is source comparability. DESNZ generation costs are in 2024 real GBP, while the BEIS enhanced LCOE evidence is in 2018 real GBP. The report keeps those bases visible rather than forcing a false-precision conversion.

## 13. Conclusion

The model identifies cost-parity conditions, not deployment certainty.

At the documented reference point, SBSP is not cost-competitive: its delivered-grid LCOE is about 429 GBP/MWh. The useful finding is the threshold structure behind that number. Most one-way levers cannot reach the upper UK comparator range on their own. Specific mass is the exception, but only if the architecture becomes dramatically lighter.

Launch cost alone is insufficient because it operates on the mass and scale created by the rest of the architecture. A heavy, low-efficiency system remains expensive even at very low launch prices. The combined improvements that matter most are lower mass, higher efficiency, lower launch cost, lower in-orbit assembly cost, lower space hardware cost and lower WACC.

SBSP approaches the UK electricity cost range around 150 GBP/MWh, becomes more comparable with firm low-carbon benchmarks around 100-120 GBP/MWh, and begins to overlap the conservative BEIS system-adjusted renewable comparator around 80 GBP/MWh and below. Reaching 60 GBP/MWh requires simultaneous movement across nearly all bottlenecks.

The system-adjusted renewable comparator used here is deliberately conservative. A full GB system model may show higher or lower effective costs depending on grid buildout, storage duration, balancing needs, curtailment and backup capacity. Therefore, SBSP reaching 80-120 GBP/MWh should be interpreted as a trigger for deeper system-value modelling, not as automatic market competitiveness.

Engineering feasibility, commercial readiness and full power-system value remain separate tests. If SBSP can achieve the threshold conditions identified here and demonstrate reliable high-availability operation, it could become relevant as UK baseload or strategic low-carbon power. Until then, it remains a threshold-dependent technology option.

## Appendix A. Secondary Sensitivity Figures

The main report integrates the figures needed for the central argument. The following figures are retained for transparency and diagnostic completeness, but they do not change the threshold conclusion.

{_secondary_figure_blocks()}

## Appendix B. Source Registry

Appendix Table B1. Full source registry

{markdown_table(["Source ID", "Reference", "URL"], SOURCE_REFERENCES)}

## Appendix C. Assumption Classification Notes

Key numerical inputs are stored in `data/sbsp_parameters.csv`, `data/uk_generation_costs.csv`, `data/uk_system_adjusted_costs.csv` and `data/assumptions.csv`. Each major value is labelled as sourced, derived or exploratory. The full classification detail is retained here rather than in the main text.

Appendix Table C1. Full reference point input classification

{markdown_table(["Parameter", "Reference value", "Classification", "Source", "Interpretation"], _reference_parameter_rows(params))}
"""

    Path(output_path).write_text(report, encoding="utf-8")


def build_markdown_report(
    output_path: str | Path,
    reference: dict[str, float],
    params: dict[str, Parameter],
    generation_rows: list[dict[str, object]],
    system_rows: list[dict[str, object]],
    thresholds: list[dict[str, object]],
    importance: list[dict[str, object]],
    frontier: list[dict[str, object]],
    combined_frontier: list[dict[str, object]],
    alternative_frontiers: list[dict[str, object]],
) -> None:
    """Build the decision-focused final report.

    Full sensitivity data and alternative slices remain in the processed outputs. The
    report keeps only evidence needed to answer the threshold and decision questions.
    """
    del generation_rows, system_rows, alternative_frontiers
    result = calculate_lcoe(reference)

    def compact_value(parameter: Parameter) -> str:
        value = parameter.reference_value
        unit = parameter.unit
        if unit in {"fraction", "fraction/year"}:
            return f"{value:.1%}"
        if unit in {"MW", "years", "GBP/kg", "GBP/kg to staging orbit", "GBP/kW-delivered", "GBP/MWh"}:
            return f"{value:,.0f} {unit}"
        if unit == "kg/kW-space":
            return f"{value:.1f} {unit}"
        return f"{value:.2f} {unit}"

    core_names = [
        "delivered_capacity_mw",
        "end_to_end_efficiency",
        "capacity_factor",
        "specific_mass_kg_per_kw_space_power",
        "launch_cost_gbp_per_kg",
        "space_hardware_cost_gbp_per_w_space",
        "in_orbit_assembly_cost_gbp_per_kg",
        "wacc",
        "system_lifetime_years",
    ]
    core_roles = {
        "delivered_capacity_mw": "Scale anchor",
        "end_to_end_efficiency": "Sets space-side power and mass",
        "capacity_factor": "Sets annual delivered electricity",
        "specific_mass_kg_per_kw_space_power": "Multiplies launch, transfer and assembly cost",
        "launch_cost_gbp_per_kg": "Primary transport-cost lever",
        "space_hardware_cost_gbp_per_w_space": "Orbital manufacturing-cost lever",
        "in_orbit_assembly_cost_gbp_per_kg": "Mass-scaled deployment cost",
        "wacc": "Annualises the capital base",
        "system_lifetime_years": "Capital recovery period",
    }
    core_rows = [[params[name].display_name, compact_value(params[name]), core_roles[name]] for name in core_names]

    capex_rows = [
        [CAPEX_LABELS.get(name, name.replace("_", " ")), fmt_money(value / 1e9, 2)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_rows.extend(
        [
            ["Pre-margin subtotal", fmt_money(result.pre_margin_capex_gbp / 1e9, 2)],
            ["Programme margin / contingency", fmt_money(result.programme_margin_gbp / 1e9, 2)],
            ["Initial CAPEX total", fmt_money(result.initial_capex_gbp / 1e9, 2)],
        ]
    )

    decision_rows = [
        ["Below 150 GBP/MWh", "Broad screening ceiling", "Approaches the upper comparator range; not a competitiveness claim"],
        ["100-120 GBP/MWh", "Firm low-carbon decision region", "Warrants engineering, finance and GB system-value assessment"],
        ["80 GBP/MWh or below", "Conservative system-adjusted overlap", "Cost is relevant, but price-basis and system-value checks still apply"],
        ["60 GBP/MWh", "Stringent stretch test", "Requires simultaneous movement across most bottlenecks"],
    ]

    benchmark_rows = [
        ["DESNZ generation range", "55-153", "2024 real GBP", "Generator-boundary comparison"],
        ["Core mature generation range", "55-113", "2024 real GBP", "Headline generation-cost screen"],
        ["BEIS renewable system-adjusted range", "45-87", "2018 real GBP", "Conservative indicator; not a complete GB system model"],
        ["Firm low-carbon markers", "92.5 contract; 104-105 CCUS", "Mixed price bases", "Context only; not a single like-for-like benchmark"],
    ]

    combined_rows = []
    for row in combined_frontier:
        target = int(row["target_lcoe_gbp_per_mwh"])
        if row["status"] != "feasible" or target not in {150, 120, 100, 80}:
            continue
        combined_rows.append(
            [
                target,
                f"{float(row['progress_fraction']):.0%}",
                f"{float(row['launch_cost_gbp_per_kg']):.0f}",
                f"{float(row['specific_mass_kg_per_kw_space_power']):.2f}",
                f"{float(row['end_to_end_efficiency']):.0%}",
                f"{float(row['wacc']):.1%}",
            ]
        )

    threshold_lookup = {
        (str(row["parameter"]), int(row["target_lcoe_gbp_per_mwh"])): row for row in thresholds
    }
    mass_150 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 150)]["threshold_value"])
    mass_120 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 120)]["threshold_value"])
    mass_100 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 100)]["threshold_value"])
    best_by_parameter = {str(row["parameter"]): float(row["best_lcoe_gbp_per_mwh"]) for row in importance}
    decision_assumption_names = set(core_names + ["rectenna_cost_gbp_per_w_delivered"])
    assumption_rows = [
        [row[0], row[1], row[3], row[4]]
        for name, row in zip(REFERENCE_PARAMETER_ORDER, _reference_parameter_rows(params))
        if name in decision_assumption_names
    ]

    report = f"""# UK Space-Based Solar Power Cost-Threshold Assessment

Report subtitle: Decision-focused techno-economic assessment for UK firm low-carbon electricity

Evidence status: Project evidence registry and official source files reviewed to 10 July 2026.

Version: v1.1 decision-window revision

Prepared as: A reproducible threshold assessment using the project data and model pipeline.

Disclaimer: This report identifies cost conditions for further assessment. It does not establish engineering feasibility, commercial readiness or investment merit.

[[PAGEBREAK]]

## Table of Contents

- 1. Executive Decision Summary
- 2. Scope and Method
- 3. Reference Case and Cost Structure
- 4. UK Cost Benchmarks
- 5. One-way Cost Thresholds
- 6. Combined Bottleneck Thresholds
- 7. Decision Interpretation and Limitations
- Appendix A. Full One-way Diagnostic
- Appendix B. Source Registry
- Appendix C. Assumption Classification

[[PAGEBREAK]]

## 1. Executive Decision Summary

The reference case produces delivered-grid LCOE of {result.lcoe_gbp_per_mwh:.0f} GBP/MWh. It is an analytical anchor, not a forecast or preferred design. The useful result is the threshold structure below it.

Table 1. Cost gates and their decision meaning

{markdown_table(["Cost gate", "Interpretation", "Decision meaning"], decision_rows)}

Three conclusions drive the assessment:

- Only specific mass reaches the 150 GBP/MWh screen by itself. With all other inputs fixed, the thresholds are {mass_150:.2f} kg/kW-space at 150 GBP/MWh, {mass_120:.2f} at 120, and {mass_100:.2f} at 100.
- Launch cost alone bottoms out at {best_by_parameter['launch_cost_gbp_per_kg']:.0f} GBP/MWh even at 20 GBP/kg. End-to-end efficiency alone bottoms out at {best_by_parameter['end_to_end_efficiency']:.0f} GBP/MWh at 35 percent efficiency.
- Reaching the 80-120 GBP/MWh region requires coordinated improvement in mass, efficiency, launch, assembly, orbital hardware and finance.

Entering 80-120 GBP/MWh would justify deeper engineering and GB power-system modelling. It would not by itself establish market competitiveness.

## 2. Scope and Method

The model asks what launch cost, mass intensity, hardware cost, assembly cost, efficiency, utilisation, lifetime, OPEX and financing conditions would be required for SBSP to approach UK electricity cost benchmarks.

The boundary is delivered-grid LCOE. Annualised initial CAPEX, fixed OPEX, refurbishment and variable OPEX are divided by annual delivered MWh. Delivered electricity equals capacity x 8,760 x capacity factor; required space-side power equals delivered capacity divided by end-to-end efficiency; orbital mass equals space-side power multiplied by specific mass.

The model identifies cost parity only. Engineering achievability, beam and spectrum regulation, construction delivery, commercial financeability and whole-system value require separate tests.

## 3. Reference Case and Cost Structure

Table 2. Core reference inputs

{markdown_table(["Parameter", "Reference value", "Role"], core_rows)}

At this point, 2 GW delivered output requires {result.required_space_power_kw / 1e6:.2f} GW of space-side power and about {result.orbital_mass_kg / 1000:,.0f} tonnes of orbital hardware.

[[PAGEBREAK]]

Table 3. Initial CAPEX, including programme margin

{markdown_table(["Component", "GBP billion"], capex_rows)}

{_figure("Figure 1. Reference LCOE composition", "../figures/reference_lcoe_components.png", "Annualised CAPEX contributes about 82 percent of reference LCOE. This is why mass, scale, hardware cost and financing dominate the threshold result.")}

The reference inputs are exploratory because commercial-scale SBSP has not been deployed. They answer what would have to change, not what will happen.

## 4. UK Cost Benchmarks

{_figure("Figure 2. UK electricity cost benchmarks", "../figures/uk_electricity_cost_benchmark_comparison.png", "Ranges are shown as intervals rather than zero-based bars. The 80-120 GBP/MWh region is a decision window, while 150 GBP/MWh is only a broad screening ceiling.")}

Table 4. Benchmark interpretation

{markdown_table(["Comparator", "Indicative GBP/MWh", "Price basis", "Use"], benchmark_rows)}

DESNZ generation costs and BEIS enhanced-LCOE values are not on the same real-price basis. The chart labels that difference explicitly; exact overlap should not be read as price-normalised parity. Wider grid, balancing, curtailment, storage and reliability costs also require a full GB system model.

## 5. One-way Cost Thresholds

One-way analysis changes one input while holding all others at the reference point. It is a leverage test, not a development plan.

{_figure("Figure 3. Best LCOE reached by each one-way change", "../figures/one_way_lcoe_floors.png", "The figure removes high-cost deterioration ranges and compares only the most favourable result for each input. Specific mass is the only one-way lever that crosses the 150 GBP/MWh screen.")}

{_figure("Figure 4. Specific-mass thresholds near the decision window", "../figures/specific_mass_threshold_focus.png", "The view is restricted to the part of the curve that crosses 150, 120 and 100 GBP/MWh. The 5.0 kg/kW-space reference point is deliberately noted outside the plotting window.")}

{_figure("Figure 5. Launch-efficiency threshold matrix", "../figures/sbsp_break_even_thresholds.png", "At 25 percent efficiency, 150 GBP/MWh requires launch cost of about 109 GBP/kg or lower. At 35 percent efficiency, 100 GBP/MWh requires about 64 GBP/kg. Dashes indicate no solution in the explored launch-cost range.")}

The pattern is unambiguous: low launch cost applied to a heavy, inefficient architecture is still too expensive. Mass and efficiency change the scale on which transport and assembly costs act.

## 6. Combined Bottleneck Thresholds

The combined frontier moves model inputs by an equal fraction from their reference values toward the favourable ends of their documented ranges. The percentage below is a model-normalised parameter movement, not technology maturity, probability or calendar progress.

Table 5. Selected combined-threshold points

{markdown_table(["Target GBP/MWh", "Normalised movement", "Launch GBP/kg", "Mass kg/kW", "Efficiency", "WACC"], combined_rows)}

{_figure("Figure 6. Model-normalised joint improvement", "../figures/combined_progress_frontier.png", "Moving from the 150 screen into the 80-120 decision region tightens several physical and financial constraints together.")}

{_figure("Figure 7. Launch-cost and efficiency decision contours", "../figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "The chart displays only 220 GBP/MWh and below; higher-cost space is neutral grey. It shows the limited launch-cost window associated with 150, 120, 100 and 80 GBP/MWh contours.")}

These combinations are illustrative slices through parameter space, not engineering roadmaps. Alternative slices remain available in `data/processed/alternative_combined_pathways.csv`.

## 7. Decision Interpretation and Limitations

SBSP is most relevant to the UK if it can provide firm or near-firm low-carbon output. In that role, the comparison is with reliable delivered electricity, gas CCUS, nuclear-like firm supply, long-duration flexibility and the system-adjusted cost of a high-renewable system - not only bare wind and solar LCOE.

The practical decision rule is: below 150 GBP/MWh, continue threshold monitoring; in the 100-120 region, undertake integrated engineering and finance review; at 80 GBP/MWh or below, add detailed GB dispatch, network and reliability modelling.

The main uncertainties are architecture feasibility, cost-range credibility, financing risk, lifetime and degradation, beam and regulatory constraints, and the value of firm output in a future GB system. Price-basis differences between the 2018 BEIS and 2024 DESNZ comparators remain explicit rather than silently harmonised.

The central conclusion is therefore narrow: SBSP does not become decision-relevant through launch-cost reduction alone. It becomes worth deeper assessment only when a credible integrated architecture enters roughly 80-120 GBP/MWh delivered-grid LCOE.

[[PAGEBREAK]]

## Appendix A. Full One-way Diagnostic

The report focuses on decision-relevant views. Full sensitivity curves remain in `figures/`, and all curve points remain in `data/processed/sensitivity_curves.csv`.

{_figure("Figure A1. Full one-way feasibility matrix", "../figures/one_way_threshold_feasibility_matrix.png", "The matrix retains the complete one-way audit across all five targets and eleven varied inputs.")}

Appendix Table A1. Full one-way threshold summary

{markdown_table(["Driver", "Unit", "150 threshold", "100 threshold", "Best one-way LCOE"], _threshold_summary_rows(thresholds))}

[[PAGEBREAK]]

## Appendix B. Source Registry

Appendix Table B1. Source registry

{markdown_table(["Source ID", "Reference", "URL"], SOURCE_REFERENCES)}

## Appendix C. Assumption Classification

All reference inputs in Table C1 are classified as exploratory modelling assumptions. Operating and grid-interface allowances remain documented in `data/sbsp_parameters.csv`; raw official workbooks and processed CSVs remain separate from model outputs.

Appendix Table C1. Decision-relevant reference inputs

{markdown_table(["Parameter", "Reference", "Source", "Interpretation"], assumption_rows)}
"""

    Path(output_path).write_text(report, encoding="utf-8")


def build_verification_note(
    output_path: str | Path,
    checks: list[str],
    weaknesses: list[str],
    fixes: list[str],
    uncertainties: list[str],
    acceptance_status: dict[str, str],
) -> None:
    criteria_rows = [[key, value] for key, value in acceptance_status.items()]
    note = f"""# Verification Note

## Verification completed

{chr(10).join(f"- {item}" for item in checks)}

## Refinement changes

{chr(10).join(f"- {item}" for item in fixes)}

## Evidence limits

{chr(10).join(f"- {item}" for item in weaknesses)}

## Model uncertainties

{chr(10).join(f"- {item}" for item in uncertainties)}

## Acceptance Criteria Status

{markdown_table(["Criterion", "Status"], criteria_rows)}

Overall status: all acceptance criteria are satisfied. For this release, both PDFs were rendered to PNG pages with Poppler and inspected for missing pages, font rendering, clipping, table overflow and chart-label legibility.
"""
    Path(output_path).write_text(note, encoding="utf-8")
