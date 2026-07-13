"""Delivered-grid LCOE model for space-based solar power."""

from __future__ import annotations

from dataclasses import dataclass


HOURS_PER_YEAR = 8760.0


@dataclass(frozen=True)
class LCOEResult:
    lcoe_gbp_per_mwh: float
    annual_delivered_mwh: float
    annual_total_cost_gbp: float
    initial_capex_gbp: float
    pre_margin_capex_gbp: float
    programme_margin_gbp: float
    required_space_power_kw: float
    orbital_mass_kg: float
    annualized_capex_gbp: float
    fixed_opex_gbp_per_year: float
    replacement_refurbishment_gbp_per_year: float
    variable_opex_gbp_per_year: float
    capex_components_gbp: dict[str, float]


def capital_recovery_factor(rate: float, years: float) -> float:
    if years <= 0:
        raise ValueError("System lifetime must be positive.")
    if abs(rate) < 1e-12:
        return 1.0 / years
    growth = (1.0 + rate) ** years
    return rate * growth / (growth - 1.0)


def calculate_lcoe(parameters: dict[str, float]) -> LCOEResult:
    delivered_capacity_mw = parameters["delivered_capacity_mw"]
    delivered_capacity_kw = delivered_capacity_mw * 1000.0
    delivered_capacity_w = delivered_capacity_kw * 1000.0
    efficiency = parameters["end_to_end_efficiency"]
    capacity_factor = parameters["capacity_factor"]
    lifetime = parameters["system_lifetime_years"]
    wacc = parameters["wacc"]

    required_space_power_kw = delivered_capacity_kw / efficiency
    required_space_power_w = required_space_power_kw * 1000.0
    orbital_mass_kg = required_space_power_kw * parameters["specific_mass_kg_per_kw_space_power"]

    components = {
        "space_segment_capex": parameters["space_hardware_cost_gbp_per_w_space"] * required_space_power_w,
        "wireless_power_transmission": parameters["wireless_power_transmission_cost_gbp_per_w_space"] * required_space_power_w,
        "launch": parameters["launch_cost_gbp_per_kg"] * orbital_mass_kg,
        "orbit_transfer": parameters["orbit_transfer_cost_gbp_per_kg"] * orbital_mass_kg,
        "in_orbit_assembly": parameters["in_orbit_assembly_cost_gbp_per_kg"] * orbital_mass_kg,
        "rectenna": parameters["rectenna_cost_gbp_per_w_delivered"] * delivered_capacity_w,
        "grid_connection": parameters["grid_connection_cost_gbp_per_kw_delivered"] * delivered_capacity_kw,
    }
    pre_margin_capex = sum(components.values())
    programme_margin = parameters["programme_margin_pct"] * pre_margin_capex
    initial_capex = pre_margin_capex + programme_margin

    annual_delivered_mwh = delivered_capacity_mw * HOURS_PER_YEAR * capacity_factor
    annualized_capex = initial_capex * capital_recovery_factor(wacc, lifetime)
    fixed_opex = parameters["fixed_opex_pct_capex_per_year"] * initial_capex
    replacement_refurbishment = parameters["replacement_refurbishment_pct_capex_per_year"] * initial_capex
    variable_opex = parameters["variable_opex_gbp_per_mwh"] * annual_delivered_mwh
    annual_total_cost = annualized_capex + fixed_opex + replacement_refurbishment + variable_opex

    return LCOEResult(
        lcoe_gbp_per_mwh=annual_total_cost / annual_delivered_mwh,
        annual_delivered_mwh=annual_delivered_mwh,
        annual_total_cost_gbp=annual_total_cost,
        initial_capex_gbp=initial_capex,
        pre_margin_capex_gbp=pre_margin_capex,
        programme_margin_gbp=programme_margin,
        required_space_power_kw=required_space_power_kw,
        orbital_mass_kg=orbital_mass_kg,
        annualized_capex_gbp=annualized_capex,
        fixed_opex_gbp_per_year=fixed_opex,
        replacement_refurbishment_gbp_per_year=replacement_refurbishment,
        variable_opex_gbp_per_year=variable_opex,
        capex_components_gbp=components,
    )


def with_overrides(parameters: dict[str, float], **overrides: float) -> dict[str, float]:
    updated = dict(parameters)
    updated.update(overrides)
    return updated
