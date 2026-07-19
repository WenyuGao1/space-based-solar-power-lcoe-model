"""Sensitivity, threshold and contour analysis for the SBSP model."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np

from .model import calculate_lcoe
from .parameters import Parameter


SENSITIVITY_PARAMETERS = [
    "launch_cost_gbp_per_kg",
    "specific_mass_kg_per_kw_space_power",
    "space_hardware_cost_gbp_per_w_space",
    "wireless_power_transmission_cost_gbp_per_w_space",
    "end_to_end_efficiency",
    "wacc",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "system_lifetime_years",
    "capacity_factor",
    "in_orbit_assembly_cost_gbp_per_kg",
    "orbit_transfer_cost_gbp_per_kg",
    "programme_margin_pct",
    "replacement_refurbishment_pct_capex_per_year",
    "fixed_opex_pct_capex_per_year",
    "variable_opex_gbp_per_mwh",
]

TARGET_LCOE_GBP_PER_MWH = [150, 120, 100, 80, 60]

COMBINED_FRONTIER_PARAMETERS = [
    "launch_cost_gbp_per_kg",
    "specific_mass_kg_per_kw_space_power",
    "space_hardware_cost_gbp_per_w_space",
    "wireless_power_transmission_cost_gbp_per_w_space",
    "in_orbit_assembly_cost_gbp_per_kg",
    "orbit_transfer_cost_gbp_per_kg",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "programme_margin_pct",
    "replacement_refurbishment_pct_capex_per_year",
    "fixed_opex_pct_capex_per_year",
    "variable_opex_gbp_per_mwh",
    "end_to_end_efficiency",
    "capacity_factor",
    "system_lifetime_years",
    "wacc",
]

ALTERNATIVE_PATHWAY_DEFINITIONS = [
    {
        "pathway": "high_efficiency_slice",
        "display_name": "High-efficiency parameter slice",
        "description": "End-to-end efficiency is held at 30 percent while the remaining bottlenecks move by an equal fraction toward their favourable bounds.",
        "fixed_values": {"end_to_end_efficiency": 0.30},
    },
    {
        "pathway": "low_mass_architecture_slice",
        "display_name": "Low-mass architecture slice",
        "description": "Specific mass is held at 1.0 kg/kW-space while other bottlenecks move by an equal fraction toward their favourable bounds.",
        "fixed_values": {"specific_mass_kg_per_kw_space_power": 1.00},
    },
    {
        "pathway": "infrastructure_finance_slice",
        "display_name": "Infrastructure-finance slice",
        "description": "WACC is held at 3.5 percent, lifetime at 45 years and capacity factor at 95 percent while physical bottlenecks move by an equal fraction.",
        "fixed_values": {"wacc": 0.035, "system_lifetime_years": 45.0, "capacity_factor": 0.95},
    },
]


def sensitivity_curve(
    reference: dict[str, float],
    parameter: Parameter,
    points: int = 101,
) -> list[dict[str, float | str]]:
    values = np.linspace(parameter.min_value, parameter.max_value, points)
    rows: list[dict[str, float | str]] = []
    for value in values:
        case = dict(reference)
        case[parameter.name] = float(value)
        result = calculate_lcoe(case)
        rows.append(
            {
                "parameter": parameter.name,
                "display_name": parameter.display_name,
                "unit": parameter.unit,
                "value": float(value),
                "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh,
            }
        )
    return rows


def all_sensitivity_curves(
    reference: dict[str, float],
    params: dict[str, Parameter],
    points: int = 101,
) -> dict[str, list[dict[str, float | str]]]:
    return {
        name: sensitivity_curve(reference, params[name], points=points)
        for name in SENSITIVITY_PARAMETERS
        if name in params
    }


def one_way_thresholds(
    reference: dict[str, float],
    params: dict[str, Parameter],
    targets: list[int] | None = None,
    points: int = 2001,
) -> list[dict[str, object]]:
    """Solve high-precision monotonic one-way thresholds with bisection.

    ``points`` is retained for API compatibility with earlier releases but is no
    longer used.  Returning a root-solved threshold avoids presenting the
    resolution of an arbitrary sampling grid as numerical precision.
    """

    _ = points
    targets = TARGET_LCOE_GBP_PER_MWH if targets is None else targets
    rows: list[dict[str, object]] = []
    reference_lcoe = calculate_lcoe(reference).lcoe_gbp_per_mwh
    for name in SENSITIVITY_PARAMETERS:
        parameter = params[name]
        favourable_value = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
        favourable_case = dict(reference)
        favourable_case[name] = favourable_value
        feasible_min = calculate_lcoe(favourable_case).lcoe_gbp_per_mwh
        for target in targets:
            threshold_value, threshold_lcoe = _solve_monotonic_threshold(
                reference,
                parameter,
                target,
            )
            if threshold_value is None:
                status = "not reached within explored one-way range"
            elif parameter.improvement_direction == "lower":
                status = "maximum value meeting target"
            else:
                status = "minimum value meeting target"
            rows.append(
                {
                    "parameter": name,
                    "display_name": parameter.display_name,
                    "unit": parameter.unit,
                    "target_lcoe_gbp_per_mwh": target,
                    "threshold_value": threshold_value,
                    "reference_value": parameter.reference_value,
                    "reference_lcoe_gbp_per_mwh": reference_lcoe,
                    "best_lcoe_in_range_gbp_per_mwh": feasible_min,
                    "lcoe_at_threshold_gbp_per_mwh": threshold_lcoe,
                    "solution_method": "monotonic bisection",
                    "status": status,
                }
            )
    return rows


def _solve_monotonic_threshold(
    reference: dict[str, float],
    parameter: Parameter,
    target_lcoe_gbp_per_mwh: float,
    iterations: int = 80,
) -> tuple[float | None, float | None]:
    """Return the limiting feasible value and its LCOE for one monotonic input."""

    def lcoe_at(value: float) -> float:
        case = dict(reference)
        case[parameter.name] = float(value)
        return calculate_lcoe(case).lcoe_gbp_per_mwh

    low = float(parameter.min_value)
    high = float(parameter.max_value)
    low_lcoe = lcoe_at(low)
    high_lcoe = lcoe_at(high)

    if parameter.improvement_direction == "lower":
        # Low values are favourable. Find the largest feasible value.
        if low_lcoe > target_lcoe_gbp_per_mwh:
            return None, None
        if high_lcoe <= target_lcoe_gbp_per_mwh:
            return high, high_lcoe
        for _ in range(iterations):
            mid = (low + high) / 2.0
            if lcoe_at(mid) <= target_lcoe_gbp_per_mwh:
                low = mid
            else:
                high = mid
        return low, lcoe_at(low)

    # High values are favourable. Find the smallest feasible value.
    if high_lcoe > target_lcoe_gbp_per_mwh:
        return None, None
    if low_lcoe <= target_lcoe_gbp_per_mwh:
        return low, low_lcoe
    for _ in range(iterations):
        mid = (low + high) / 2.0
        if lcoe_at(mid) <= target_lcoe_gbp_per_mwh:
            high = mid
        else:
            low = mid
    return high, lcoe_at(high)


def cost_driver_importance(reference: dict[str, float], params: dict[str, Parameter]) -> list[dict[str, object]]:
    reference_lcoe = calculate_lcoe(reference).lcoe_gbp_per_mwh
    rows: list[dict[str, object]] = []
    for name in SENSITIVITY_PARAMETERS:
        parameter = params[name]
        best_value = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
        case = dict(reference)
        case[name] = best_value
        best_lcoe = calculate_lcoe(case).lcoe_gbp_per_mwh
        rows.append(
            {
                "parameter": name,
                "display_name": parameter.display_name,
                "unit": parameter.unit,
                "reference_value": parameter.reference_value,
                "best_value_in_range": best_value,
                "reference_lcoe_gbp_per_mwh": reference_lcoe,
                "best_lcoe_gbp_per_mwh": best_lcoe,
                "lcoe_reduction_gbp_per_mwh": reference_lcoe - best_lcoe,
            }
        )
    rows.sort(key=lambda row: float(row["lcoe_reduction_gbp_per_mwh"]), reverse=True)
    return rows


def contour_grid(
    reference: dict[str, float],
    x_parameter: Parameter,
    y_parameter: Parameter,
    x_points: int = 80,
    y_points: int = 80,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_values = np.linspace(x_parameter.min_value, x_parameter.max_value, x_points)
    y_values = np.linspace(y_parameter.min_value, y_parameter.max_value, y_points)
    z = np.zeros((len(y_values), len(x_values)))
    for yi, y_value in enumerate(y_values):
        for xi, x_value in enumerate(x_values):
            case = dict(reference)
            case[x_parameter.name] = float(x_value)
            case[y_parameter.name] = float(y_value)
            z[yi, xi] = calculate_lcoe(case).lcoe_gbp_per_mwh
    return x_values, y_values, z


def contour_rows(
    reference: dict[str, float],
    x_parameter: Parameter,
    y_parameter: Parameter,
    x_points: int = 80,
    y_points: int = 80,
) -> list[dict[str, object]]:
    x_values, y_values, z = contour_grid(reference, x_parameter, y_parameter, x_points, y_points)
    rows: list[dict[str, object]] = []
    for yi, y_value in enumerate(y_values):
        for xi, x_value in enumerate(x_values):
            rows.append(
                {
                    "x_parameter": x_parameter.name,
                    "x_value": float(x_value),
                    "y_parameter": y_parameter.name,
                    "y_value": float(y_value),
                    "lcoe_gbp_per_mwh": float(z[yi, xi]),
                }
            )
    return rows


def launch_efficiency_frontier(
    reference: dict[str, float],
    params: dict[str, Parameter],
    target_values: list[int] | None = None,
    efficiencies: list[float] | None = None,
) -> list[dict[str, object]]:
    target_values = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    efficiencies = [0.20, 0.25, 0.30, 0.35] if efficiencies is None else efficiencies
    launch_param = params["launch_cost_gbp_per_kg"]
    rows: list[dict[str, object]] = []
    for efficiency in efficiencies:
        for target in target_values:
            efficiency_case = dict(reference)
            efficiency_case["end_to_end_efficiency"] = efficiency
            threshold, threshold_lcoe = _solve_monotonic_threshold(
                efficiency_case,
                launch_param,
                target,
            )
            rows.append(
                {
                    "end_to_end_efficiency": efficiency,
                    "target_lcoe_gbp_per_mwh": target,
                    "max_launch_cost_gbp_per_kg": threshold,
                    "lcoe_at_threshold_gbp_per_mwh": threshold_lcoe,
                    "solution_method": "monotonic bisection",
                    "status": "feasible" if threshold is not None else "not feasible within explored launch range",
                }
            )
    return rows


def _interpolate_improvement(reference_value: float, parameter: Parameter, progress: float) -> float:
    if parameter.improvement_direction == "lower":
        return reference_value + progress * (parameter.min_value - reference_value)
    return reference_value + progress * (parameter.max_value - reference_value)


def combined_improvement_frontier(
    reference: dict[str, float],
    params: dict[str, Parameter],
    target_values: list[int] | None = None,
) -> list[dict[str, object]]:
    """Find the smallest equal-fraction improvement across bottlenecks for each target.

    This is a mathematical frontier, not a deployment scenario. It moves each key
    cost or performance bottleneck from its reference value toward the favourable
    end of its explored range by the same fraction and solves for the first point
    where each LCOE target is reached.
    """

    target_values = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    rows: list[dict[str, object]] = []

    def case_at(progress: float) -> dict[str, float]:
        case = dict(reference)
        for name in COMBINED_FRONTIER_PARAMETERS:
            case[name] = _interpolate_improvement(reference[name], params[name], progress)
        return case

    for target in target_values:
        baseline_case = case_at(0.0)
        baseline_result = calculate_lcoe(baseline_case)
        if baseline_result.lcoe_gbp_per_mwh <= target:
            row: dict[str, object] = {
                "target_lcoe_gbp_per_mwh": target,
                "progress_fraction": 0.0,
                "lcoe_gbp_per_mwh": baseline_result.lcoe_gbp_per_mwh,
                "status": "already feasible at baseline",
            }
            for name in COMBINED_FRONTIER_PARAMETERS:
                row[name] = baseline_case[name]
            rows.append(row)
            continue
        if calculate_lcoe(case_at(1.0)).lcoe_gbp_per_mwh > target:
            rows.append({"target_lcoe_gbp_per_mwh": target, "progress_fraction": None, "status": "not feasible within explored combined range"})
            continue
        low = 0.0
        high = 1.0
        for _ in range(60):
            mid = (low + high) / 2.0
            if calculate_lcoe(case_at(mid)).lcoe_gbp_per_mwh <= target:
                high = mid
            else:
                low = mid
        case = case_at(high)
        result = calculate_lcoe(case)
        row: dict[str, object] = {
            "target_lcoe_gbp_per_mwh": target,
            "progress_fraction": high,
            "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh,
            "status": "feasible",
        }
        for name in COMBINED_FRONTIER_PARAMETERS:
            row[name] = case[name]
        rows.append(row)
    return rows


def alternative_combined_pathways(
    reference: dict[str, float],
    params: dict[str, Parameter],
    target_values: list[int] | None = None,
) -> list[dict[str, object]]:
    """Solve illustrative parameter-space slices around different bottleneck emphases.

    These pathways are not scenarios or predictions. Each one fixes a small number
    of variables to a transparent value and then finds the equal-fraction movement
    needed across the remaining bottlenecks to hit each LCOE target.
    """

    target_values = TARGET_LCOE_GBP_PER_MWH if target_values is None else target_values
    rows: list[dict[str, object]] = []

    for definition in ALTERNATIVE_PATHWAY_DEFINITIONS:
        fixed_values = dict(definition["fixed_values"])
        moving_parameters = [name for name in COMBINED_FRONTIER_PARAMETERS if name not in fixed_values]

        def case_at(progress: float) -> dict[str, float]:
            case = dict(reference)
            case.update({name: float(value) for name, value in fixed_values.items()})
            for name in moving_parameters:
                case[name] = _interpolate_improvement(reference[name], params[name], progress)
            return case

        for target in target_values:
            baseline_case = case_at(0.0)
            baseline_result = calculate_lcoe(baseline_case)
            if baseline_result.lcoe_gbp_per_mwh <= target:
                row: dict[str, object] = {
                    "pathway": definition["pathway"],
                    "display_name": definition["display_name"],
                    "description": definition["description"],
                    "target_lcoe_gbp_per_mwh": target,
                    "progress_fraction": 0.0,
                    "lcoe_gbp_per_mwh": baseline_result.lcoe_gbp_per_mwh,
                    "status": "already feasible at slice baseline",
                }
                for name in COMBINED_FRONTIER_PARAMETERS:
                    row[name] = baseline_case[name]
                rows.append(row)
                continue
            if calculate_lcoe(case_at(1.0)).lcoe_gbp_per_mwh > target:
                rows.append(
                    {
                        "pathway": definition["pathway"],
                        "display_name": definition["display_name"],
                        "description": definition["description"],
                        "target_lcoe_gbp_per_mwh": target,
                        "progress_fraction": None,
                        "status": "not feasible within explored combined range",
                    }
                )
                continue
            low = 0.0
            high = 1.0
            for _ in range(60):
                mid = (low + high) / 2.0
                if calculate_lcoe(case_at(mid)).lcoe_gbp_per_mwh <= target:
                    high = mid
                else:
                    low = mid
            case = case_at(high)
            result = calculate_lcoe(case)
            row: dict[str, object] = {
                "pathway": definition["pathway"],
                "display_name": definition["display_name"],
                "description": definition["description"],
                "target_lcoe_gbp_per_mwh": target,
                "progress_fraction": high,
                "lcoe_gbp_per_mwh": result.lcoe_gbp_per_mwh,
                "status": "feasible",
            }
            for name in COMBINED_FRONTIER_PARAMETERS:
                row[name] = case[name]
            rows.append(row)
    return rows


def one_way_feasibility_matrix(thresholds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in thresholds:
        rows.append(
            {
                "parameter": row["parameter"],
                "display_name": row["display_name"],
                "target_lcoe_gbp_per_mwh": row["target_lcoe_gbp_per_mwh"],
                "feasible": row["threshold_value"] not in (None, ""),
                "best_lcoe_in_range_gbp_per_mwh": row["best_lcoe_in_range_gbp_per_mwh"],
                "threshold_value": row["threshold_value"],
            }
        )
    return rows


def reference_result_rows(reference: dict[str, float]) -> list[dict[str, object]]:
    result = calculate_lcoe(reference)
    rows: list[dict[str, object]] = [
        {"metric": "lcoe_gbp_per_mwh", "value": result.lcoe_gbp_per_mwh},
        {"metric": "annual_delivered_mwh", "value": result.annual_delivered_mwh},
        {"metric": "annual_total_cost_gbp", "value": result.annual_total_cost_gbp},
        {"metric": "initial_capex_gbp", "value": result.initial_capex_gbp},
        {"metric": "pre_margin_capex_gbp", "value": result.pre_margin_capex_gbp},
        {"metric": "programme_margin_gbp", "value": result.programme_margin_gbp},
        {"metric": "required_space_power_kw", "value": result.required_space_power_kw},
        {"metric": "orbital_mass_kg", "value": result.orbital_mass_kg},
        {"metric": "annualized_capex_gbp", "value": result.annualized_capex_gbp},
        {"metric": "fixed_opex_gbp_per_year", "value": result.fixed_opex_gbp_per_year},
        {"metric": "replacement_refurbishment_gbp_per_year", "value": result.replacement_refurbishment_gbp_per_year},
        {"metric": "variable_opex_gbp_per_year", "value": result.variable_opex_gbp_per_year},
    ]
    for name, value in result.capex_components_gbp.items():
        rows.append({"metric": f"capex_{name}_gbp", "value": value})
    return rows


def result_as_dict(reference: dict[str, float]) -> dict[str, object]:
    result = calculate_lcoe(reference)
    payload = asdict(result)
    payload["capex_components_gbp"] = dict(result.capex_components_gbp)
    return payload
