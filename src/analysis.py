"""Sensitivity, threshold and scenario analysis for the v2.0 SBSP model."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np

from .model import calculate_lcoe
from .parameters import Parameter


# These are the numerical inputs that affect LCOE in the default per-kg mode.
# Scale is deliberately excluded, as are per-flight diagnostics that do not
# change per-kg launch CAPEX.  The computed end-to-end efficiency is not an input.
SENSITIVITY_PARAMETERS = [
    "solar_conversion_efficiency",
    "dc_to_rf_efficiency",
    "transmission_efficiency",
    "rectenna_conversion_efficiency",
    "grid_conversion_efficiency",
    "capacity_factor",
    "operating_lifetime_years",
    "real_discount_rate",
    "construction_duration_years",
    "annual_output_degradation_fraction",
    "system_specific_mass_kg_per_kw_delivered",
    "space_generation_hardware_cost_gbp_per_w_dc",
    "transmitter_cost_gbp_per_w_rf_emitted",
    "launch_cost_gbp_per_kg_to_staging_orbit",
    "orbit_transfer_cost_gbp_per_kg_final_hardware",
    "in_orbit_assembly_cost_gbp_per_kg_operational_hardware",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "programme_contingency_fraction",
    "space_hardware_replacement_rate_per_year",
    "ground_hardware_replacement_rate_per_year",
    "fixed_opex_fraction_of_eligible_assets_per_year",
    "variable_opex_gbp_per_mwh",
    "decommissioning_cost_fraction_initial_capex",
    "residual_value_fraction_initial_capex",
]

TARGET_LCOE_GBP_PER_MWH = [150, 120, 100, 80, 60]

COMBINED_FRONTIER_PARAMETERS = list(SENSITIVITY_PARAMETERS)

ALTERNATIVE_PATHWAY_DEFINITIONS = [
    {
        "pathway": "source_metric_mass_slice",
        "display_name": "Delivered-specific-mass slice",
        "description": "System specific mass is fixed at 1/0.67 kg/kW-delivered; other inputs move by an equal model-normalised fraction.",
        "fixed_values": {"system_specific_mass_kg_per_kw_delivered": 1.0 / 0.67},
    },
    {
        "pathway": "high_conversion_slice",
        "display_name": "Higher-conversion slice",
        "description": "Selected conversion stages are fixed at transparent high values; other inputs move by an equal model-normalised fraction.",
        "fixed_values": {
            "solar_conversion_efficiency": 0.42,
            "dc_to_rf_efficiency": 0.80,
            "rectenna_conversion_efficiency": 0.80,
        },
    },
    {
        "pathway": "infrastructure_finance_slice",
        "display_name": "Infrastructure-finance slice",
        "description": "Real discount rate is fixed at 3.5%, lifetime at 45 years and capacity factor at 95%; other inputs move equally toward their favourable bounds.",
        "fixed_values": {
            "real_discount_rate": 0.035,
            "operating_lifetime_years": 45.0,
            "capacity_factor": 0.95,
        },
    },
]


def sensitivity_curve(reference: dict[str, float], parameter: Parameter, points: int = 101) -> list[dict[str, float | str]]:
    values = np.linspace(parameter.min_value, parameter.max_value, points)
    rows: list[dict[str, float | str]] = []
    for value in values:
        if parameter.name in {"operating_lifetime_years", "construction_duration_years"}:
            value = float(round(value))
        case = dict(reference)
        case[parameter.name] = float(value)
        result = calculate_lcoe(case)
        rows.append({
            "parameter": parameter.name,
            "display_name": parameter.display_name,
            "unit": parameter.unit,
            "value": float(value),
            "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh,
        })
    return rows


def all_sensitivity_curves(reference: dict[str, float], params: dict[str, Parameter], points: int = 101) -> dict[str, list[dict[str, float | str]]]:
    return {name: sensitivity_curve(reference, params[name], points) for name in SENSITIVITY_PARAMETERS}


def _solve_monotonic_threshold(reference: dict[str, float], parameter: Parameter, target: float, iterations: int = 80) -> tuple[float | None, float | None]:
    def at(value: float) -> float:
        case = dict(reference)
        case[parameter.name] = value
        return calculate_lcoe(case).lcoe_gbp_per_mwh

    if parameter.name in {"operating_lifetime_years", "construction_duration_years"}:
        candidates = [float(value) for value in range(int(parameter.min_value), int(parameter.max_value) + 1)]
        feasible = [(value, at(value)) for value in candidates if at(value) <= target]
        if not feasible:
            return None, None
        return (max(feasible) if parameter.improvement_direction == "lower" else min(feasible))

    low, high = float(parameter.min_value), float(parameter.max_value)
    low_lcoe, high_lcoe = at(low), at(high)
    if parameter.improvement_direction == "lower":
        if low_lcoe > target:
            return None, None
        if high_lcoe <= target:
            return high, high_lcoe
        for _ in range(iterations):
            mid = (low + high) / 2
            if at(mid) <= target:
                low = mid
            else:
                high = mid
        return low, at(low)
    if high_lcoe > target:
        return None, None
    if low_lcoe <= target:
        return low, low_lcoe
    for _ in range(iterations):
        mid = (low + high) / 2
        if at(mid) <= target:
            high = mid
        else:
            low = mid
    return high, at(high)


def one_way_thresholds(reference: dict[str, float], params: dict[str, Parameter], targets: list[int] | None = None, points: int = 2001) -> list[dict[str, object]]:
    del points
    targets = TARGET_LCOE_GBP_PER_MWH if targets is None else targets
    reference_lcoe = calculate_lcoe(reference).lcoe_gbp_per_mwh
    rows: list[dict[str, object]] = []
    for name in SENSITIVITY_PARAMETERS:
        parameter = params[name]
        favourable = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
        best_case = dict(reference)
        best_case[name] = favourable
        best_lcoe = calculate_lcoe(best_case).lcoe_gbp_per_mwh
        for target in targets:
            value, solved = _solve_monotonic_threshold(reference, parameter, target)
            rows.append({
                "parameter": name,
                "display_name": parameter.display_name,
                "unit": parameter.unit,
                "target_lcoe_gbp_per_mwh": target,
                "threshold_value": value,
                "reference_value": parameter.reference_value,
                "reference_lcoe_gbp_per_mwh": reference_lcoe,
                "best_lcoe_in_range_gbp_per_mwh": best_lcoe,
                "lcoe_at_threshold_gbp_per_mwh": solved,
                "solution_method": "monotonic bisection",
                "status": "not reached within explored one-way range" if value is None else "limiting value meeting target",
            })
    return rows


def cost_driver_importance(reference: dict[str, float], params: dict[str, Parameter]) -> list[dict[str, object]]:
    baseline = calculate_lcoe(reference).lcoe_gbp_per_mwh
    rows: list[dict[str, object]] = []
    for name in SENSITIVITY_PARAMETERS:
        parameter = params[name]
        best = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
        case = dict(reference)
        case[name] = best
        best_lcoe = calculate_lcoe(case).lcoe_gbp_per_mwh
        rows.append({
            "parameter": name,
            "display_name": parameter.display_name,
            "unit": parameter.unit,
            "reference_value": parameter.reference_value,
            "best_value_in_range": best,
            "reference_lcoe_gbp_per_mwh": baseline,
            "best_lcoe_gbp_per_mwh": best_lcoe,
            "lcoe_reduction_gbp_per_mwh": baseline - best_lcoe,
        })
    return sorted(rows, key=lambda row: float(row["lcoe_reduction_gbp_per_mwh"]), reverse=True)


def contour_grid(reference: dict[str, float], x_parameter: Parameter, y_parameter: Parameter, x_points: int = 80, y_points: int = 80) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs = np.linspace(x_parameter.min_value, x_parameter.max_value, x_points)
    ys = np.linspace(y_parameter.min_value, y_parameter.max_value, y_points)
    z = np.zeros((len(ys), len(xs)))
    for yi, y in enumerate(ys):
        for xi, x in enumerate(xs):
            case = dict(reference)
            case[x_parameter.name] = float(x)
            case[y_parameter.name] = float(y)
            z[yi, xi] = calculate_lcoe(case).lcoe_gbp_per_mwh
    return xs, ys, z


def contour_rows(reference: dict[str, float], x_parameter: Parameter, y_parameter: Parameter, x_points: int = 80, y_points: int = 80) -> list[dict[str, object]]:
    xs, ys, z = contour_grid(reference, x_parameter, y_parameter, x_points, y_points)
    return [{
        "x_parameter": x_parameter.name,
        "x_value": float(x),
        "y_parameter": y_parameter.name,
        "y_value": float(y),
        "lcoe_gbp_per_mwh": float(z[yi, xi]),
    } for yi, y in enumerate(ys) for xi, x in enumerate(xs)]


def launch_efficiency_frontier(reference: dict[str, float], params: dict[str, Parameter], target_values: list[int] | None = None, efficiencies: list[float] | None = None) -> list[dict[str, object]]:
    """Launch threshold at selected *computed* chain efficiencies.

    The requested total efficiency is implemented by solving the solar-stage
    input with all other stage efficiencies fixed.  It is never an independent
    end-to-end model input.
    """
    targets = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    totals = [0.12, 0.15, 0.18, 0.19] if efficiencies is None else efficiencies
    launch = params["launch_cost_gbp_per_kg_to_staging_orbit"]
    other_product = (
        reference["dc_to_rf_efficiency"] * reference["transmission_efficiency"]
        * reference["rectenna_conversion_efficiency"] * reference["grid_conversion_efficiency"]
    )
    rows: list[dict[str, object]] = []
    for total in totals:
        solar = total / other_product
        for target in targets:
            if not params["solar_conversion_efficiency"].min_value <= solar <= params["solar_conversion_efficiency"].max_value:
                rows.append({
                    "end_to_end_efficiency": total,
                    "solar_conversion_efficiency": solar,
                    "target_lcoe_gbp_per_mwh": target,
                    "max_launch_cost_gbp_per_kg_to_staging_orbit": None,
                    "lcoe_at_threshold_gbp_per_mwh": None,
                    "solution_method": "derived solar stage plus monotonic bisection",
                    "status": "computed efficiency outside explored stage bounds",
                })
                continue
            case = dict(reference)
            case["solar_conversion_efficiency"] = solar
            value, solved = _solve_monotonic_threshold(case, launch, target)
            rows.append({
                "end_to_end_efficiency": total,
                "solar_conversion_efficiency": solar,
                "target_lcoe_gbp_per_mwh": target,
                "max_launch_cost_gbp_per_kg_to_staging_orbit": value,
                "lcoe_at_threshold_gbp_per_mwh": solved,
                "solution_method": "derived solar stage plus monotonic bisection",
                "status": "feasible" if value is not None else "not feasible within explored launch range",
            })
    return rows


def _interpolate(reference_value: float, parameter: Parameter, progress: float) -> float:
    bound = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
    value = reference_value + progress * (bound - reference_value)
    if parameter.name in {"operating_lifetime_years", "construction_duration_years"}:
        return float(round(value))
    return value


def _coupled_frontier(reference: dict[str, float], params: dict[str, Parameter], targets: list[int], fixed: dict[str, float] | None = None) -> list[dict[str, object]]:
    fixed = fixed or {}
    moving = [name for name in COMBINED_FRONTIER_PARAMETERS if name not in fixed]

    def case_at(progress: float) -> dict[str, float]:
        case = dict(reference)
        case.update(fixed)
        for name in moving:
            case[name] = _interpolate(reference[name], params[name], progress)
        return case

    rows: list[dict[str, object]] = []
    for target in targets:
        baseline = case_at(0)
        if calculate_lcoe(baseline).lcoe_gbp_per_mwh <= target:
            progress, status = 0.0, "already feasible at slice baseline"
        elif calculate_lcoe(case_at(1)).lcoe_gbp_per_mwh > target:
            rows.append({"target_lcoe_gbp_per_mwh": target, "progress_fraction": None, "status": "not feasible within explored combined range"})
            continue
        else:
            low, high = 0.0, 1.0
            for _ in range(70):
                mid = (low + high) / 2
                if calculate_lcoe(case_at(mid)).lcoe_gbp_per_mwh <= target:
                    high = mid
                else:
                    low = mid
            progress, status = high, "feasible"
        case = case_at(progress)
        result = calculate_lcoe(case)
        row: dict[str, object] = {
            "target_lcoe_gbp_per_mwh": target,
            "progress_fraction": progress,
            "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh,
            "computed_end_to_end_efficiency": result.end_to_end_efficiency,
            "status": status,
        }
        row.update({name: case[name] for name in COMBINED_FRONTIER_PARAMETERS})
        rows.append(row)
    return rows


def combined_improvement_frontier(reference: dict[str, float], params: dict[str, Parameter], target_values: list[int] | None = None) -> list[dict[str, object]]:
    """Equal-fraction mathematical interpolation, not a forecast or roadmap."""
    targets = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    return _coupled_frontier(reference, params, targets)


def alternative_combined_pathways(reference: dict[str, float], params: dict[str, Parameter], target_values: list[int] | None = None) -> list[dict[str, object]]:
    targets = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    rows: list[dict[str, object]] = []
    for definition in ALTERNATIVE_PATHWAY_DEFINITIONS:
        for row in _coupled_frontier(reference, params, targets, dict(definition["fixed_values"])):
            rows.append({
                "pathway": definition["pathway"],
                "display_name": definition["display_name"],
                "description": definition["description"],
                **row,
            })
    return rows


def one_way_feasibility_matrix(thresholds: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "parameter": row["parameter"],
        "display_name": row["display_name"],
        "target_lcoe_gbp_per_mwh": row["target_lcoe_gbp_per_mwh"],
        "feasible": row["threshold_value"] not in (None, ""),
        "best_lcoe_in_range_gbp_per_mwh": row["best_lcoe_in_range_gbp_per_mwh"],
        "threshold_value": row["threshold_value"],
    } for row in thresholds]


def reference_result_rows(reference: dict[str, float]) -> list[dict[str, object]]:
    result = calculate_lcoe(reference)
    rows: list[dict[str, object]] = [
        {"metric": "conditional_dcf_lcoe_gbp_per_mwh", "value": result.lcoe_gbp_per_mwh},
        {"metric": "crf_reconciliation_lcoe_gbp_per_mwh", "value": result.crf_reconciliation_lcoe_gbp_per_mwh},
        {"metric": "computed_end_to_end_efficiency", "value": result.end_to_end_efficiency},
        {"metric": "orbital_mass_kg", "value": result.orbital_mass_kg},
        {"metric": "required_launches", "value": result.required_launches},
        {"metric": "initial_capex_gbp", "value": result.initial_capex_gbp},
        {"metric": "pre_contingency_capex_gbp", "value": result.pre_contingency_capex_gbp},
        {"metric": "programme_contingency_gbp", "value": result.programme_contingency_gbp},
        {"metric": "discounted_lifetime_cost_gbp", "value": result.discounted_lifetime_cost_gbp},
        {"metric": "discounted_lifetime_energy_mwh", "value": result.discounted_lifetime_energy_mwh},
        {"metric": "first_year_delivered_mwh", "value": result.first_year_delivered_mwh},
        {"metric": "average_annual_delivered_mwh", "value": result.average_annual_delivered_mwh},
    ]
    rows.extend({"metric": name, "value": value} for name, value in result.energy_chain_power_w.items())
    rows.extend({"metric": f"capex_{name}_gbp", "value": value} for name, value in result.capex_components_gbp.items())
    rows.extend({"metric": f"pv_{name}_gbp", "value": value} for name, value in result.lifecycle_cost_components_pv_gbp.items())
    return rows


def result_as_dict(reference: dict[str, float]) -> dict[str, object]:
    return asdict(calculate_lcoe(reference))
