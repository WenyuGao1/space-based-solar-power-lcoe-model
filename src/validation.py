"""Validation checks for model inputs and generated outputs."""

from __future__ import annotations

from pathlib import Path
import math

from .model import calculate_lcoe
from .parameters import Parameter


REQUIRED_PARAMETERS = {
    "delivered_capacity_mw",
    "end_to_end_efficiency",
    "capacity_factor",
    "system_lifetime_years",
    "wacc",
    "specific_mass_kg_per_kw_space_power",
    "space_hardware_cost_gbp_per_w_space",
    "wireless_power_transmission_cost_gbp_per_w_space",
    "launch_cost_gbp_per_kg",
    "orbit_transfer_cost_gbp_per_kg",
    "in_orbit_assembly_cost_gbp_per_kg",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "programme_margin_pct",
    "replacement_refurbishment_pct_capex_per_year",
    "fixed_opex_pct_capex_per_year",
    "variable_opex_gbp_per_mwh",
}


def validate_parameters(params: dict[str, Parameter]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_PARAMETERS.difference(params)
    if missing:
        errors.append(f"Missing required parameters: {', '.join(sorted(missing))}")
    for parameter in params.values():
        if parameter.min_value > parameter.max_value:
            errors.append(f"{parameter.name} has min greater than max.")
        if not (parameter.min_value <= parameter.reference_value <= parameter.max_value):
            errors.append(f"{parameter.name} reference value is outside the explored range.")
        if parameter.improvement_direction not in {"lower", "higher"}:
            errors.append(f"{parameter.name} has invalid improvement direction.")
    return errors


def validate_reference_case(reference: dict[str, float]) -> list[str]:
    errors: list[str] = []
    if not 0.0 < reference["end_to_end_efficiency"] <= 1.0:
        errors.append("End-to-end efficiency must be in (0, 1].")
    if not 0.0 < reference["capacity_factor"] <= 1.0:
        errors.append("Capacity factor must be in (0, 1].")
    if reference["system_lifetime_years"] <= 0:
        errors.append("System lifetime must be positive.")
    try:
        result = calculate_lcoe(reference)
        if not math.isfinite(result.lcoe_gbp_per_mwh) or result.lcoe_gbp_per_mwh <= 0:
            errors.append("Reference LCOE is not positive.")
        if not math.isclose(
            result.initial_capex_gbp,
            result.pre_margin_capex_gbp + result.programme_margin_gbp,
            rel_tol=1e-12,
        ):
            errors.append("Initial CAPEX does not reconcile to pre-margin CAPEX plus programme margin.")
        annual_cost_check = (
            result.annualized_capex_gbp
            + result.fixed_opex_gbp_per_year
            + result.replacement_refurbishment_gbp_per_year
            + result.variable_opex_gbp_per_year
        )
        if not math.isclose(result.annual_total_cost_gbp, annual_cost_check, rel_tol=1e-12):
            errors.append("Annual total cost does not reconcile to its components.")
    except Exception as exc:  # pragma: no cover - defensive validation
        errors.append(f"Reference case failed: {exc}")
    return errors


def validate_raw_workbooks(paths: list[str | Path]) -> list[str]:
    """Reject failed-download JSON or HTML files carrying an .xlsx extension."""
    errors: list[str] = []
    for path_like in paths:
        path = Path(path_like)
        if not path.exists():
            errors.append(f"Missing raw workbook: {path}")
            continue
        with path.open("rb") as handle:
            signature = handle.read(4)
        if signature != b"PK\x03\x04":
            errors.append(f"Raw workbook is not a valid XLSX ZIP container: {path}")
    return errors


def validate_outputs(paths: list[str | Path]) -> list[str]:
    errors: list[str] = []
    for path_like in paths:
        path = Path(path_like)
        if not path.exists():
            errors.append(f"Missing output: {path}")
        elif path.is_file() and path.stat().st_size == 0:
            errors.append(f"Output is empty: {path}")
    return errors
