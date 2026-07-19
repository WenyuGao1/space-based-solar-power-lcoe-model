"""Generate the English v1.2 analytical report and automated verification note."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .model import LCOEResult, calculate_lcoe
from .parameters import Parameter


REPORT_VERSION = "1.2"
EVIDENCE_REVIEW_DATE = "2026-07-19"

CORE_PARAMETER_NAMES = [
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

PARAMETER_ROLES_EN = {
    "delivered_capacity_mw": "Scale anchor; most unit costs scale with capacity",
    "end_to_end_efficiency": "Sets required space-side power and therefore mass",
    "capacity_factor": "Delivered-energy proxy combining availability and constraints",
    "specific_mass_kg_per_kw_space_power": "Scales launch, transfer and assembly together",
    "launch_cost_gbp_per_kg": "Transport-cost lever to the model-defined staging orbit",
    "space_hardware_cost_gbp_per_w_space": "Orbital manufacturing-cost lever",
    "in_orbit_assembly_cost_gbp_per_kg": "Mass-scaled deployment allowance",
    "wacc": "Real project discount-rate proxy used in capital recovery",
    "system_lifetime_years": "Period over which capital is recovered",
}

CAPEX_LABELS_EN = {
    "space_segment_capex": "Space-segment hardware",
    "wireless_power_transmission": "Wireless-power hardware",
    "launch": "Launch",
    "orbit_transfer": "Orbit transfer",
    "in_orbit_assembly": "In-orbit assembly and deployment",
    "rectenna": "Rectenna",
    "grid_connection": "Grid connection",
}


@dataclass(frozen=True)
class ReportFacts:
    result: LCOEResult
    mass_thresholds: dict[int, float | None]
    best_lcoe: dict[str, float]
    combined_rows: dict[int, dict[str, object]]
    generation_band: tuple[float, float]
    mature_generation_band: tuple[float, float]
    system_adjusted_band: tuple[float, float]
    capex_share: float
    parameter_count: int
    target_count: int


def markdown_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    rendered = [[str(cell).replace("|", "/") for cell in row] for row in rows]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rendered)
    return "\n".join(lines)


def figure(title: str, path: str, interpretation: str) -> str:
    return f"![{title}]({path})\n\n**Interpretation.** {interpretation}"


def _as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _numeric_band(rows: list[dict[str, object]]) -> tuple[float, float]:
    lows = [float(row["value_low_gbp_per_mwh"]) for row in rows if row.get("value_low_gbp_per_mwh") not in (None, "")]
    highs = [float(row["value_high_gbp_per_mwh"]) for row in rows if row.get("value_high_gbp_per_mwh") not in (None, "")]
    if not lows or not highs:
        raise ValueError("Cannot derive a benchmark band from empty values.")
    return min(lows), max(highs)


def format_cost_range(low: float, high: float) -> str:
    """Format a point or interval without discarding meaningful half pounds."""

    if abs(high - low) < 1e-9:
        decimals = 0 if float(low).is_integer() else 1
        return f"£{low:.{decimals}f}/MWh"
    low_decimals = 0 if float(low).is_integer() else 1
    high_decimals = 0 if float(high).is_integer() else 1
    return f"£{low:.{low_decimals}f}–{high:.{high_decimals}f}/MWh"


def derive_report_facts(
    reference: dict[str, float],
    thresholds: list[dict[str, object]],
    importance: list[dict[str, object]],
    combined_frontier: list[dict[str, object]],
    generation_rows: list[dict[str, object]],
    system_rows: list[dict[str, object]],
) -> ReportFacts:
    result = calculate_lcoe(reference)
    mass_thresholds = {
        int(row["target_lcoe_gbp_per_mwh"]): (
            None if row["threshold_value"] in (None, "") else float(row["threshold_value"])
        )
        for row in thresholds
        if row["parameter"] == "specific_mass_kg_per_kw_space_power"
    }
    best_lcoe = {
        str(row["parameter"]): float(row["best_lcoe_gbp_per_mwh"])
        for row in importance
    }
    combined_rows = {
        int(row["target_lcoe_gbp_per_mwh"]): row
        for row in combined_frontier
    }
    included = [row for row in generation_rows if _as_bool(row.get("include_in_bands"))]
    mature = [row for row in included if row["technology"] != "Floating offshore wind"]
    system_selected = [row for row in system_rows if row["technology"] == "High-renewable system-adjusted band"]
    if not system_selected:
        raise ValueError("Missing high-renewable system-adjusted benchmark row.")
    system_band = _numeric_band(system_selected)
    parameter_count = len({str(row["parameter"]) for row in thresholds})
    target_count = len({int(row["target_lcoe_gbp_per_mwh"]) for row in thresholds})
    return ReportFacts(
        result=result,
        mass_thresholds=mass_thresholds,
        best_lcoe=best_lcoe,
        combined_rows=combined_rows,
        generation_band=_numeric_band(included),
        mature_generation_band=_numeric_band(mature),
        system_adjusted_band=system_band,
        capex_share=result.annualized_capex_gbp / result.annual_total_cost_gbp,
        parameter_count=parameter_count,
        target_count=target_count,
    )


def format_parameter_value(parameter: Parameter) -> str:
    value = parameter.reference_value
    if parameter.unit in {"fraction", "fraction/year"}:
        return f"{value:.1%}"
    if parameter.unit == "kg/kW-space":
        return f"{value:.2f} {parameter.unit}"
    if parameter.unit in {"GBP/W-space", "GBP/W-delivered"}:
        return f"£{value:.2f}/{parameter.unit.split('/', 1)[1]}"
    if parameter.unit.startswith("GBP/"):
        return f"£{value:,.0f}/{parameter.unit.split('/', 1)[1]}"
    if parameter.unit == "MW":
        return f"{value:,.0f} MW"
    if parameter.unit == "years":
        return f"{value:,.0f} years"
    return f"{value:g} {parameter.unit}"


def threshold_summary_rows(thresholds: list[dict[str, object]], targets: tuple[int, ...] = (150, 120, 100, 80, 60)) -> list[list[object]]:
    by_parameter: dict[str, dict[int, dict[str, object]]] = {}
    order: list[str] = []
    for row in thresholds:
        name = str(row["parameter"])
        if name not in by_parameter:
            by_parameter[name] = {}
            order.append(name)
        by_parameter[name][int(row["target_lcoe_gbp_per_mwh"])] = row
    output: list[list[object]] = []
    for name in order:
        sample = next(iter(by_parameter[name].values()))
        row_values: list[object] = [sample["display_name"], sample["unit"]]
        for target in targets:
            threshold = by_parameter[name].get(target, {}).get("threshold_value")
            row_values.append("—" if threshold in (None, "") else f"{float(threshold):.2f}")
        output.append(row_values)
    return output


def source_registry_rows(source_rows: list[dict[str, str]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in source_rows:
        url = row["url"] if row["url"].startswith("http") else f"../{row['url']}"
        rows.append(
            [
                row["source_id"],
                f"[{row['title']}]({url})",
                row["organization"],
                row["role"],
            ]
        )
    return rows


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
    source_rows: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
    assumption_rows: list[dict[str, str]],
    external_study_rows: list[dict[str, str]],
) -> None:
    facts = derive_report_facts(
        reference,
        thresholds,
        importance,
        combined_frontier,
        generation_rows,
        system_rows,
    )
    result = facts.result

    core_rows = [
        [params[name].display_name, format_parameter_value(params[name]), PARAMETER_ROLES_EN[name]]
        for name in CORE_PARAMETER_NAMES
    ]
    capex_rows = [
        [CAPEX_LABELS_EN.get(name, name), f"£{value / 1e9:.2f}bn"]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_rows.extend(
        [
            ["Pre-margin subtotal", f"£{result.pre_margin_capex_gbp / 1e9:.2f}bn"],
            ["Programme margin", f"£{result.programme_margin_gbp / 1e9:.2f}bn"],
            ["Initial CAPEX", f"£{result.initial_capex_gbp / 1e9:.2f}bn"],
        ]
    )

    decision_rows = [
        ["£150/MWh", "Broad study-defined screening line", "A model diagnostic, not an official UK threshold"],
        ["£100–120/MWh", "Study-defined screen for a potential firm or near-firm role", "Triggers deeper engineering, finance and system-value work"],
        ["£80/MWh", "Overlap with the selected system-adjusted comparator", "Still not a market-competitiveness conclusion"],
        ["£60/MWh", "Stringent stress test", "No tested one-way input reaches it; coupled cases remain exploratory"],
    ]

    benchmark_rows: list[list[object]] = []
    for row in generation_rows:
        if row.get("value_low_gbp_per_mwh") in (None, ""):
            continue
        benchmark_rows.append(
            [
                row["technology"],
                format_cost_range(
                    float(row["value_low_gbp_per_mwh"]),
                    float(row["value_high_gbp_per_mwh"]),
                ),
                row["price_basis"],
                row["value_type"],
            ]
        )
    system_band_row = next(row for row in system_rows if row["technology"] == "High-renewable system-adjusted band")
    benchmark_rows.append(
        [
            system_band_row["technology"],
            format_cost_range(
                float(system_band_row["value_low_gbp_per_mwh"]),
                float(system_band_row["value_high_gbp_per_mwh"]),
            ),
            system_band_row["price_basis"],
            "Indicative enhanced-LCOE envelope",
        ]
    )

    mass_150 = facts.mass_thresholds[150]
    mass_120 = facts.mass_thresholds[120]
    mass_100 = facts.mass_thresholds[100]
    if mass_150 is None or mass_120 is None or mass_100 is None:
        raise ValueError("Expected specific-mass thresholds are unavailable.")

    selected_frontier_rows = []
    for row in frontier:
        efficiency = float(row["end_to_end_efficiency"])
        target = int(row["target_lcoe_gbp_per_mwh"])
        if efficiency not in {0.25, 0.30, 0.35} or target not in {150, 120, 100}:
            continue
        launch_value = row["max_launch_cost_gbp_per_kg"]
        selected_frontier_rows.append(
            [
                f"{efficiency:.0%}",
                f"£{target}/MWh",
                "not reached" if launch_value in (None, "") else f"£{float(launch_value):.1f}/kg or lower",
            ]
        )

    combined_rows = []
    for target in sorted(facts.combined_rows, reverse=True):
        row = facts.combined_rows[target]
        if row.get("status") != "feasible":
            combined_rows.append([f"£{target}/MWh", "not reached", "—", "—", "—", "—"])
            continue
        combined_rows.append(
            [
                f"£{target}/MWh",
                f"{float(row['progress_fraction']):.1%}",
                f"£{float(row['launch_cost_gbp_per_kg']):.0f}/kg",
                f"{float(row['specific_mass_kg_per_kw_space_power']):.2f} kg/kW-space",
                f"{float(row['end_to_end_efficiency']):.1%}",
                f"{float(row['wacc']):.2%}",
            ]
        )

    external_rows = [
        [
            row["study_label"],
            row["analysis_type"],
            row["reported_cost_context"],
            row["relationship_to_this_project"],
        ]
        for row in external_study_rows
    ]
    evidence_table_rows = [
        [
            row["parameter_or_claim"],
            f"{row['evidence_role']} / {row['source_id']}",
            row["locator"],
            row["numeric_context"],
            row["limitations"],
        ]
        for row in evidence_rows
    ]
    assumption_table_rows = [
        [row["assumption_id"], row["area"], row["assumption"], row["limitation"]]
        for row in assumption_rows
    ]

    alt_pathways = len({str(row["pathway"]) for row in alternative_frontiers})
    report = f"""# UK Space-Based Solar Power Cost-Condition Map

Report subtitle: A reproducible threshold assessment for UK decision screening — not a deployment forecast

Evidence status: source registry reviewed to {EVIDENCE_REVIEW_DATE}; selected official DESNZ benchmark cells are machine-reconciled.

Version: v{REPORT_VERSION}

Prepared as: a bilingual, executable techno-economic research artifact.

Disclaimer: this report identifies model-conditional cost requirements. It does not demonstrate engineering feasibility, predict a commissioning year, estimate an investment return or recommend an investment.

<!-- PAGEBREAK -->

## Contents

- 1. Executive answer
- 2. Research question and distinctive contribution
- 3. Scope, accounting boundary and method
- 4. Evidence quality and source discipline
- 5. Reference anchor and cost structure
- 6. UK comparator landscape
- 7. One-way conditional thresholds
- 8. Coupled cost-condition frontiers
- 9. Interpretation for UK decisions
- 10. Limitations, robustness and non-claims
- 11. Conclusion
- Appendices A–C. Audit tables, sources and assumptions

<!-- PAGEBREAK -->

## 1. Executive answer

The short answer is: **the reference configuration is expensive, but the project is useful because it reveals the conditions behind that result.** At the study-authored reference point, grid-connection-point LCOE is **£{result.lcoe_gbp_per_mwh:.0f}/MWh**. This is a normalization anchor, not a forecast or preferred design.

Table 1. Study-defined cost lines and their meaning

{markdown_table(["Cost line", "Use in this project", "Decision meaning and limitation"], decision_rows)}

The strongest one-way result is specific mass, **within this model boundary and the selected ranges, with every other input held at its reference value**. The limiting values are {mass_150:.2f}, {mass_120:.2f} and {mass_100:.2f} kg/kW-space for £150, £120 and £100/MWh respectively. No one-way specific-mass value in the explored range reaches £80 or £60/MWh.

Launch cost alone is not sufficient: even at the favourable explored bound of £{params['launch_cost_gbp_per_kg'].min_value:.0f}/kg, LCOE remains about £{facts.best_lcoe['launch_cost_gbp_per_kg']:.0f}/MWh. Raising end-to-end efficiency alone to {params['end_to_end_efficiency'].max_value:.0%} leaves about £{facts.best_lcoe['end_to_end_efficiency']:.0f}/MWh. The model therefore points to testing multiple coupled combinations across mass, launch, space hardware, assembly, finance, efficiency and delivered energy; it does not prove that every variable must move.

The contribution is **not greater forecasting accuracy**. It is a transparent and reproducible answer to a narrower question: *what cost and performance conditions would have to hold, inside a stated model, before SBSP enters selected UK decision regions?*

## 2. Research question and distinctive contribution

The representative SBSP studies reviewed here evaluate named architectures, future deployment cases, lifecycle impacts or system pathways. This project complements them with continuous one-way and coupled parameter frontiers. It therefore makes assumptions, conditional thresholds and failure-to-reach results directly auditable.

Table 2. Relationship to selected existing SBSP studies

{markdown_table(["Study", "Primary analysis", "Reported context", "Relationship to this project"], external_rows)}

The project's publishable advantage is specific:

- Every exact model input is classified as a **study-authored exploratory assumption**; literature values are kept in a separate evidence map.
- Thresholds are solved by high-precision monotonic bisection rather than read from a coarse plotting grid.
- The analysis reports both attainable and unattainable one-way targets across {facts.parameter_count} variables and {facts.target_count} study-defined cost lines.
- Coupled frontiers and {alt_pathways} alternative parameter slices show that the answer is not a single-variable launch-cost story.
- Source files, processed outputs, figures, English and Chinese reports and automated checks are regenerated by one command.

These features make the analysis **more transparent for threshold questions**, not universally more accurate than architecture-specific studies.

## 3. Scope, accounting boundary and method

The model ends at the **grid connection point**. It includes space hardware, wireless-power hardware, launch, orbit transfer, in-orbit assembly, rectenna, local grid connection, programme margin, capital recovery, fixed OPEX, refurbishment and variable OPEX. It excludes downstream transmission reinforcement, balancing, storage, curtailment, reliability services, taxes, decommissioning cost, revenue design and monetised system value.

All model financial inputs are interpreted in 2024 real GBP. The `wacc` variable is a **real project discount-rate proxy** used in the capital-recovery factor; tax, inflation and financing tranches are outside the model. The delivered capacity factor is also a proxy combining availability, outages and operational constraints; it is not an observed SBSP availability statistic.

The calculation is:

- annual delivered energy = delivered capacity × 8,760 hours × delivered capacity factor;
- required space power = delivered grid capacity ÷ end-to-end efficiency;
- orbital mass = required space power × whole-architecture specific mass;
- initial CAPEX = summed component CAPEX × (1 + programme margin);
- LCOE = (annualised CAPEX + fixed OPEX + refurbishment + variable OPEX) ÷ annual delivered MWh.

A one-way threshold changes one input and fixes all others. A coupled equal-fraction frontier moves selected inputs from the reference point toward their favourable recorded bounds by the same normalized fraction. That fraction is a mathematical index, **not technology readiness, probability, calendar progress or a unique roadmap**.

## 4. Evidence quality and source discipline

The evidence system separates three concepts:

- **Direct input:** an exact value used in the model. All SBSP reference values and ranges are study-authored assumptions.
- **Contextual evidence:** published metrics showing plausible scales or important drivers without being treated as equivalent definitions.
- **External comparison:** results from a different architecture or boundary, used to test narrative consistency rather than validate this model.

The withdrawn 2020 UK Space Agency press release is retained only as programme history. It supplies no numerical input. Caltech's 160 g/m² areal density is not converted into whole-system kg/kW-space. Likewise, the official small-scale study completed in 2025 and published in 2026 supplies only external context: its specific power, hurdle rates and high-Earth-orbit launch estimates use different definitions.

The £{result.lcoe_gbp_per_mwh:.0f}/MWh reference anchor lies inside the 2026-published official small-scale study's reported £335–595/MWh 2030 band. This is a useful consistency observation, **not validation**, because scale, architecture, orbit, scenario year, financing and cost boundaries differ.

## 5. Reference anchor and cost structure

Table 3. Core reference inputs

{markdown_table(["Parameter", "Reference value", "Role in the model"], core_rows)}

The {reference['delivered_capacity_mw'] / 1000:.1f} GW delivered-capacity anchor requires {result.required_space_power_kw / 1e6:.2f} GW of space-side power and **{result.orbital_mass_kg / 1e6:.2f} million kg** of orbital hardware, or about {result.orbital_mass_kg / 1000:,.0f} tonnes. Both units are shown to make the mass scale unambiguous.

Table 4. Reference initial CAPEX reconciliation

{markdown_table(["Component", "Cost"], capex_rows)}

{figure("Figure 1. Reference LCOE components", "../figures/reference_lcoe_components.png", f"Annualised CAPEX contributes about {facts.capex_share:.0%} of annual reference cost. The result is therefore especially sensitive to physical scale and capital recovery.")}

The reference point produces {result.annual_delivered_mwh / 1e6:.3f} million MWh/year, £{result.initial_capex_gbp / 1e9:.1f}bn initial CAPEX and £{result.annual_total_cost_gbp / 1e9:.2f}bn annualised total cost. These figures reconcile exactly in the generated model outputs.

<!-- PAGEBREAK -->

## 6. UK comparator landscape

{figure("Figure 2. UK electricity cost comparators", "../figures/uk_electricity_cost_benchmark_comparison.png", f"The figure shows the generation-only rows flagged for the headline band, plus the Hinkley contract marker and the historical system-adjusted band. The plotted generation rows span about £{facts.generation_band[0]:.0f}–£{facts.generation_band[1]:.0f}/MWh; excluding the floating-offshore FOAK row gives £{facts.mature_generation_band[0]:.0f}–£{facts.mature_generation_band[1]:.0f}/MWh.")}

Table 5. Comparator definitions from the structured data

{markdown_table(["Comparator", "Reported value", "Price basis", "Metric type"], benchmark_rows)}

The Hinkley Point C £92.50/MWh marker is a 35-year CfD strike price stated in 2012 prices and CPI-indexed; it is not a generic nuclear LCOE. The BEIS enhanced-LCOE range of £{facts.system_adjusted_band[0]:.0f}–£{facts.system_adjusted_band[1]:.0f}/MWh is in 2018 real GBP, whereas the DESNZ generation rows are in 2024 real GBP. No false-precision price conversion is applied.

Figure 2 uses the six generation-only rows marked for the headline band. Table 5 additionally retains the £181/MWh mid-load-factor gas-CCUS sensitivity, but it is excluded from the figure and headline band to avoid counting two utilisation cases for the same technology as separate headline comparators.

Consequently, overlap with a chart band is a screening result only. Wholesale prices, contract prices, generator LCOE and system-adjusted costs are different metrics.

## 7. One-way conditional thresholds

{figure("Figure 3. Best LCOE attainable one variable at a time", "../figures/one_way_lcoe_floors.png", "Within the selected one-way ranges, only whole-architecture specific mass crosses the £150/MWh study line. This ranking is range-dependent and is not universal across architectures.")}

{figure("Figure 4. Specific-mass thresholds in the decision window", "../figures/specific_mass_threshold_focus.png", f"With all other reference inputs fixed, the model requires at most {mass_150:.2f}, {mass_120:.2f} and {mass_100:.2f} kg/kW-space for £150, £120 and £100/MWh. These are conditional mathematical requirements, not proven engineering targets.")}

Table 6. Complete one-way threshold audit

{markdown_table(["Input", "Unit", "£150", "£120", "£100", "£80", "£60"], threshold_summary_rows(thresholds))}

An em dash means that no value reaches the target inside the tested one-way bound; it does not mean physical impossibility outside that bound.

The result does not mean that specific mass is the only necessary condition. It means only that, under the reference assumptions and selected one-way bounds, it is the sole individual variable able to cross £150/MWh. In a coupled design, low mass is not sufficient for every target, and other architectures may rank drivers differently. The official small-scale study published in 2026, for example, attributes 55.5–64.0% of its own LCOE variance to launch assumptions.

## 8. Coupled cost-condition frontiers

{figure("Figure 5. Launch-cost and efficiency frontier", "../figures/sbsp_break_even_thresholds.png", "Higher efficiency relaxes the launch-cost condition, but many cells remain unattainable when the remaining reference inputs are fixed. Values are root-solved inside the recorded launch-cost bounds.")}

Table 7. Selected launch-cost limits with all other inputs fixed

{markdown_table(["End-to-end efficiency", "Target", "Maximum launch cost"], selected_frontier_rows)}

{figure("Figure 6. Equal-fraction coupled frontier", "../figures/combined_progress_frontier.png", "Lower target LCOEs on the x-axis correspond to larger normalized movements on the y-axis. The y-axis is a mathematical interpolation index, not an implementation timeline.")}

Table 8. Coupled equal-fraction index and selected parameter values

{markdown_table(["Target", "Normalized movement", "Launch", "Specific mass", "Efficiency", "Real discount proxy"], combined_rows)}

{figure("Figure 7. Launch cost × efficiency decision contour", "../figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "The two-variable contour makes interaction visible, but it still fixes every unplotted input at the reference point. It must not be read as a complete design feasibility map.")}

The equal-fraction results are one transparent index among many possible paths. The generated alternative slices show that high efficiency, low mass or infrastructure-like finance can each reshape the frontier. None is presented as the unique or necessary roadmap.

## 9. Interpretation for UK decisions

The practical reading is sequential:

- Above £150/MWh, the model remains outside its broad study-defined screening line; research should focus on whether integrated architecture evidence can change several major drivers together.
- At £100–120/MWh, a credible integrated design would justify detailed engineering, financing and GB dispatch/network analysis.
- At £80/MWh or below, cost overlap with the selected historical system-adjusted band becomes more relevant, but differing price bases and omitted system effects still prevent a market conclusion.
- Any claim of firm low-carbon value must be tested in a full GB power-system model rather than subtracted informally from plant LCOE.

The official small-scale study published in 2026 reports a £21/MWh system-benefit adjustment in each of its cases. This report does not subtract that figure because the architecture and system-model boundary differ.

## 10. Limitations, robustness and non-claims

The strongest robustness feature is traceability: official 2025 generation-cost cells are checked directly against the stored workbook; source IDs are foreign-key validated; input CSVs are structurally validated; model accounting reconciles; and threshold roots are tested against their target LCOEs.

The principal limitations are:

- Architecture feasibility is not assessed: beam safety, spectrum, thermal control, degradation, debris risk, deployment and maintainability require engineering models and demonstrations.
- Parameter ranges are deliberately broad and partly judgmental; driver rankings depend on those ranges and the reference point.
- Correlations, construction schedules, learning curves, probabilistic uncertainty and tax/financing structure are not modelled.
- The grid-connection-point boundary omits downstream network, balancing, storage, curtailment, reliability and market effects.
- Comparator price bases are disclosed but not harmonised.
- External SBSP studies are not like-for-like validation datasets.

This project does **not** claim to be the first threshold analysis, to discover universal necessary conditions, or to produce a more accurate deployment forecast. Its defensible special feature is an openly executable, bilingual and source-disciplined cost-condition map.

## 11. Conclusion

At the study-authored reference point, SBSP LCOE is approximately £{result.lcoe_gbp_per_mwh:.0f}/MWh at the grid connection point. Lower launch cost by itself does not close the gap. Within the selected one-way ranges, a very low whole-architecture specific mass is the only individual lever that reaches £150/MWh, and it still cannot reach £80/MWh alone.

The central conclusion is therefore narrower and conditional: **lower launch cost or higher efficiency alone is insufficient at the tested bounds; no single tested one-way change reaches £80 or £60/MWh, so some coupled improvement is required for those lines.** The analysis does not prove that every listed variable must improve, or that its equal-fraction path is unique. It also does not prove that any engineering or commercial combination can be achieved.

The project's value is the clarity of that conditional statement and the audit trail behind it.

<!-- PAGEBREAK -->

## Appendix A. Evidence-to-claim map

Table A1. Contextual evidence and its limitations

{markdown_table(["Parameter or claim", "Evidence role / source", "Locator", "Published context", "Applicability limit"], evidence_table_rows)}

## Appendix B. Source registry

Table B1. Sources used by the project

{markdown_table(["Source ID", "Reference", "Organisation", "Role"], source_registry_rows(source_rows))}

## Appendix C. Assumptions and boundary register

Table C1. Explicit analytical assumptions

{markdown_table(["ID", "Area", "Assumption", "Limitation"], assumption_table_rows)}

Machine-readable inputs and all complete sensitivity curves are retained under `data/`; the full English figure set is under `figures/`; exact generated thresholds are under `data/processed/`.
"""

    Path(output_path).write_text(report, encoding="utf-8")


def build_verification_note(
    output_path: str | Path,
    category_results: list[dict[str, str]],
    warnings: list[str],
    commands: list[str],
) -> None:
    """Write an evidence-based automated verification record without overclaiming."""

    normalized = [str(row.get("status", "FAIL")).upper() for row in category_results]
    if any(status == "FAIL" for status in normalized):
        overall = "FAIL"
    elif any(status == "WARN" for status in normalized):
        overall = "PASS WITH WARNINGS"
    else:
        overall = "PASS"
    rows = [[row["category"], row["status"].upper(), row["evidence"]] for row in category_results]
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) or "- None recorded."
    command_lines = "\n".join(f"- `{command}`" for command in commands)
    note = f"""# Verification Note

Version: v{REPORT_VERSION}

Evidence review date: {EVIDENCE_REVIEW_DATE}

Overall automated status: **{overall}**

Table 1. Verification categories

{markdown_table(["Category", "Status", "Evidence"], rows)}

## Known warnings and residual uncertainty

{warning_lines}

## Reproduction commands

{command_lines}

## Interpretation

`PASS` means the recorded automated checks completed for the current generated files. It does not prove engineering feasibility or eliminate judgement in exploratory ranges. PDF structural checks confirm that documents can be opened and contain the expected pages and text; visual release QA remains a separate human inspection step.
"""
    Path(output_path).write_text(note, encoding="utf-8")
