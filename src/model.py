"""Stage-resolved delivered-grid LCOE model for space-based solar power.

All monetary values are real 2024 GBP.  The discounted-cash-flow valuation
base is the start of construction (t=0).  The public mass metric is normalised
to grid-delivered capacity, so it is never divided by efficiency a second time.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence


HOURS_PER_YEAR = 8760.0
PRICE_YEAR = 2024
VALUATION_BASE = "start of construction (t=0)"
DEFAULT_STAGING_ORBIT = "LEO staging orbit (service boundary; altitude architecture-dependent)"
DEFAULT_OPERATIONAL_ORBIT = "High Earth orbit (HEO; final orbit architecture-dependent)"


@dataclass(frozen=True)
class LCOEResult:
    lcoe_gbp_per_mwh: float
    crf_reconciliation_lcoe_gbp_per_mwh: float
    end_to_end_efficiency: float
    energy_chain_power_w: dict[str, float]
    orbital_mass_kg: float
    required_launches: int
    launch_pricing_mode: str
    initial_capex_gbp: float
    pre_contingency_capex_gbp: float
    programme_contingency_gbp: float
    capex_components_gbp: dict[str, float]
    discounted_lifetime_cost_gbp: float
    discounted_lifetime_energy_mwh: float
    lifecycle_cost_components_pv_gbp: dict[str, float]
    first_year_delivered_mwh: float
    average_annual_delivered_mwh: float
    fixed_opex_eligible_asset_base_gbp: float
    space_replacement_eligible_cost_base_gbp: float
    ground_replacement_eligible_cost_base_gbp: float
    annual_fixed_opex_gbp: float
    annual_space_replacement_gbp: float
    annual_ground_replacement_gbp: float
    first_year_variable_opex_gbp: float
    construction_spend_profile: tuple[float, ...]
    cash_flow_rows: tuple[dict[str, float | str], ...]
    price_year: int
    valuation_base: str
    staging_orbit: str
    operational_orbit: str


def specific_mass_from_specific_power(specific_power_kw_delivered_per_kg: float) -> float:
    """Convert kW-delivered/kg to kg/kW-delivered."""

    if not math.isfinite(specific_power_kw_delivered_per_kg) or specific_power_kw_delivered_per_kg <= 0:
        raise ValueError("Specific power must be finite and strictly positive.")
    return 1.0 / specific_power_kw_delivered_per_kg


def specific_power_from_specific_mass(specific_mass_kg_per_kw_delivered: float) -> float:
    """Convert kg/kW-delivered to kW-delivered/kg."""

    if not math.isfinite(specific_mass_kg_per_kw_delivered) or specific_mass_kg_per_kw_delivered <= 0:
        raise ValueError("Specific mass must be finite and strictly positive.")
    return 1.0 / specific_mass_kg_per_kw_delivered


def capital_recovery_factor(rate: float, years: float) -> float:
    if years <= 0:
        raise ValueError("Operating lifetime must be positive.")
    if rate <= -1.0:
        raise ValueError("Discount rate must be greater than -100%.")
    if abs(rate) < 1e-12:
        return 1.0 / years
    growth = (1.0 + rate) ** years
    return rate * growth / (growth - 1.0)


def validate_construction_spend_profile(
    shares: Sequence[float],
    construction_duration_years: int,
) -> tuple[float, ...]:
    """Validate a construction-spend profile expressed as fractions of CAPEX."""

    if construction_duration_years < 0:
        raise ValueError("Construction duration cannot be negative.")
    profile = tuple(float(value) for value in shares)
    expected_length = construction_duration_years if construction_duration_years > 0 else 0
    if len(profile) != expected_length:
        raise ValueError(
            "Construction-spend profile length must equal construction duration "
            f"({len(profile)} != {expected_length})."
        )
    if any(not math.isfinite(value) or value < 0.0 for value in profile):
        raise ValueError("Construction-spend shares must be finite and non-negative.")
    expected_sum = 1.0 if construction_duration_years > 0 else 0.0
    if not math.isclose(sum(profile), expected_sum, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("Construction-spend shares must sum to 100%.")
    return profile


def equal_construction_spend_profile(construction_duration_years: int) -> tuple[float, ...]:
    if construction_duration_years < 0:
        raise ValueError("Construction duration cannot be negative.")
    if construction_duration_years == 0:
        return ()
    share = 1.0 / construction_duration_years
    return validate_construction_spend_profile(
        [share] * construction_duration_years,
        construction_duration_years,
    )


def _required_float(parameters: Mapping[str, object], name: str) -> float:
    try:
        value = float(parameters[name])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid model input: {name}") from exc
    if not math.isfinite(value):
        raise ValueError(f"Model input must be finite: {name}")
    return value


def _validate_fraction(name: str, value: float, *, allow_zero: bool = False) -> None:
    lower_ok = value >= 0.0 if allow_zero else value > 0.0
    if not lower_ok or value > 1.0:
        interval = "[0, 1]" if allow_zero else "(0, 1]"
        raise ValueError(f"{name} must lie in {interval}.")


def _discount(value: float, rate: float, year: int) -> float:
    return value / ((1.0 + rate) ** year)


def calculate_lcoe(
    parameters: Mapping[str, object],
    *,
    construction_spend_profile: Sequence[float] | None = None,
    launch_pricing_mode: str | None = None,
) -> LCOEResult:
    """Calculate conditional delivered-grid LCOE using explicit discounted cash flow.

    Construction spending occurs at t=0..construction_duration-1.  The first
    operating year is discounted at t=construction_duration+1 (or t=1 for
    instantaneous construction).  All annual operating values are real.
    """

    delivered_capacity_mw = _required_float(parameters, "delivered_capacity_mw")
    capacity_factor = _required_float(parameters, "capacity_factor")
    lifetime_raw = _required_float(parameters, "operating_lifetime_years")
    construction_raw = _required_float(parameters, "construction_duration_years")
    discount_rate = _required_float(parameters, "real_discount_rate")
    degradation = _required_float(parameters, "annual_output_degradation_fraction")

    if delivered_capacity_mw <= 0:
        raise ValueError("Delivered grid capacity must be positive.")
    _validate_fraction("Capacity factor", capacity_factor)
    _validate_fraction("Annual output degradation", degradation, allow_zero=True)
    if degradation >= 1.0:
        raise ValueError("Annual output degradation must be below 100%.")
    if discount_rate < 0.0 or discount_rate >= 1.0:
        raise ValueError("Real discount rate must lie in [0, 1).")
    if not lifetime_raw.is_integer() or lifetime_raw <= 0:
        raise ValueError("Operating lifetime must be a positive whole number of years.")
    if not construction_raw.is_integer() or construction_raw < 0:
        raise ValueError("Construction duration must be a non-negative whole number of years.")
    operating_lifetime_years = int(lifetime_raw)
    construction_duration_years = int(construction_raw)

    efficiency_names = (
        "solar_conversion_efficiency",
        "dc_to_rf_efficiency",
        "transmission_efficiency",
        "rectenna_conversion_efficiency",
        "grid_conversion_efficiency",
    )
    efficiencies = {name: _required_float(parameters, name) for name in efficiency_names}
    for name, value in efficiencies.items():
        _validate_fraction(name, value)
    end_to_end_efficiency = math.prod(efficiencies.values())

    delivered_grid_power_w = delivered_capacity_mw * 1_000_000.0
    delivered_grid_power_kw = delivered_capacity_mw * 1000.0
    rectenna_dc_power_w = delivered_grid_power_w / efficiencies["grid_conversion_efficiency"]
    incident_rf_power_w = rectenna_dc_power_w / efficiencies["rectenna_conversion_efficiency"]
    emitted_rf_power_w = incident_rf_power_w / efficiencies["transmission_efficiency"]
    space_dc_bus_power_w = emitted_rf_power_w / efficiencies["dc_to_rf_efficiency"]
    incident_solar_power_w = space_dc_bus_power_w / efficiencies["solar_conversion_efficiency"]
    energy_chain = {
        "incident_solar_power_w": incident_solar_power_w,
        "space_dc_bus_power_w": space_dc_bus_power_w,
        "emitted_rf_power_w": emitted_rf_power_w,
        "incident_rf_power_w": incident_rf_power_w,
        "rectenna_dc_power_w": rectenna_dc_power_w,
        "delivered_grid_ac_power_w": delivered_grid_power_w,
    }

    specific_mass = _required_float(parameters, "system_specific_mass_kg_per_kw_delivered")
    if specific_mass <= 0:
        raise ValueError("Delivered-power-normalised system specific mass must be positive.")
    orbital_mass_kg = delivered_grid_power_kw * specific_mass

    effective_payload = _required_float(parameters, "effective_payload_kg_per_flight")
    payload_utilisation = _required_float(parameters, "payload_utilisation_fraction")
    if effective_payload <= 0:
        raise ValueError("Effective payload per flight must be positive.")
    _validate_fraction("Payload utilisation fraction", payload_utilisation)
    usable_payload_per_flight = effective_payload * payload_utilisation
    required_launches = math.ceil(orbital_mass_kg / usable_payload_per_flight)

    mode = str(
        launch_pricing_mode
        if launch_pricing_mode is not None
        else parameters.get("launch_pricing_mode", "per_kg")
    )
    if mode not in {"per_kg", "per_flight"}:
        raise ValueError("Launch pricing mode must be 'per_kg' or 'per_flight'.")
    launch_cost_per_kg = _required_float(parameters, "launch_cost_gbp_per_kg_to_staging_orbit")
    launch_price_per_flight = _required_float(parameters, "launch_price_gbp_per_flight")
    if launch_cost_per_kg < 0 or launch_price_per_flight < 0:
        raise ValueError("Launch prices cannot be negative.")
    launch_capex = (
        orbital_mass_kg * launch_cost_per_kg
        if mode == "per_kg"
        else required_launches * launch_price_per_flight
    )

    cost_input_names = (
        "space_generation_hardware_cost_gbp_per_w_dc",
        "transmitter_cost_gbp_per_w_rf_emitted",
        "orbit_transfer_cost_gbp_per_kg_final_hardware",
        "in_orbit_assembly_cost_gbp_per_kg_operational_hardware",
        "rectenna_cost_gbp_per_w_delivered",
        "grid_connection_cost_gbp_per_kw_delivered",
        "variable_opex_gbp_per_mwh",
    )
    costs = {name: _required_float(parameters, name) for name in cost_input_names}
    if any(value < 0 for value in costs.values()):
        raise ValueError("Cost inputs cannot be negative.")

    capex_components = {
        "space_generation_hardware": costs["space_generation_hardware_cost_gbp_per_w_dc"] * space_dc_bus_power_w,
        "wireless_power_transmitter": costs["transmitter_cost_gbp_per_w_rf_emitted"] * emitted_rf_power_w,
        "launch_to_staging_orbit": launch_capex,
        "orbit_transfer_to_operational_orbit": costs["orbit_transfer_cost_gbp_per_kg_final_hardware"] * orbital_mass_kg,
        "in_orbit_assembly_and_deployment": costs["in_orbit_assembly_cost_gbp_per_kg_operational_hardware"] * orbital_mass_kg,
        "rectenna": costs["rectenna_cost_gbp_per_w_delivered"] * delivered_grid_power_w,
        "grid_connection": costs["grid_connection_cost_gbp_per_kw_delivered"] * delivered_grid_power_kw,
    }
    pre_contingency_capex = sum(capex_components.values())
    contingency_fraction = _required_float(parameters, "programme_contingency_fraction")
    _validate_fraction("Programme contingency fraction", contingency_fraction, allow_zero=True)
    programme_contingency = contingency_fraction * pre_contingency_capex
    initial_capex = pre_contingency_capex + programme_contingency

    space_replacement_rate = _required_float(parameters, "space_hardware_replacement_rate_per_year")
    ground_replacement_rate = _required_float(parameters, "ground_hardware_replacement_rate_per_year")
    fixed_opex_fraction = _required_float(parameters, "fixed_opex_fraction_of_eligible_assets_per_year")
    decommissioning_fraction = _required_float(parameters, "decommissioning_cost_fraction_initial_capex")
    residual_fraction = _required_float(parameters, "residual_value_fraction_initial_capex")
    for name, value in (
        ("Space replacement rate", space_replacement_rate),
        ("Ground replacement rate", ground_replacement_rate),
        ("Fixed O&M rate", fixed_opex_fraction),
        ("Decommissioning fraction", decommissioning_fraction),
        ("Residual value fraction", residual_fraction),
    ):
        _validate_fraction(name, value, allow_zero=True)

    fixed_opex_eligible_base = (
        capex_components["space_generation_hardware"]
        + capex_components["wireless_power_transmitter"]
        + capex_components["rectenna"]
        + capex_components["grid_connection"]
    )
    space_replacement_eligible_base = (
        capex_components["space_generation_hardware"]
        + capex_components["wireless_power_transmitter"]
        + capex_components["launch_to_staging_orbit"]
        + capex_components["orbit_transfer_to_operational_orbit"]
        + capex_components["in_orbit_assembly_and_deployment"]
    )
    ground_replacement_eligible_base = (
        capex_components["rectenna"] + capex_components["grid_connection"]
    )
    annual_fixed_opex = fixed_opex_fraction * fixed_opex_eligible_base
    annual_space_replacement = space_replacement_rate * space_replacement_eligible_base
    annual_ground_replacement = ground_replacement_rate * ground_replacement_eligible_base

    profile = (
        equal_construction_spend_profile(construction_duration_years)
        if construction_spend_profile is None
        else validate_construction_spend_profile(
            construction_spend_profile,
            construction_duration_years,
        )
    )

    lifecycle_pv = {
        "initial_construction": 0.0,
        "fixed_opex": 0.0,
        "variable_opex": 0.0,
        "space_hardware_replacement": 0.0,
        "ground_hardware_replacement": 0.0,
        "decommissioning": 0.0,
        "residual_value": 0.0,
    }
    cash_flow_rows: list[dict[str, float | str]] = []
    if construction_duration_years == 0:
        lifecycle_pv["initial_construction"] = initial_capex
        cash_flow_rows.append(
            {
                "year": 0.0,
                "phase": "construction",
                "real_cost_gbp": initial_capex,
                "delivered_energy_mwh": 0.0,
                "discounted_cost_gbp": initial_capex,
                "discounted_energy_mwh": 0.0,
            }
        )
    else:
        for year, share in enumerate(profile):
            cost = initial_capex * share
            discounted_cost = _discount(cost, discount_rate, year)
            lifecycle_pv["initial_construction"] += discounted_cost
            cash_flow_rows.append(
                {
                    "year": float(year),
                    "phase": "construction",
                    "real_cost_gbp": cost,
                    "delivered_energy_mwh": 0.0,
                    "discounted_cost_gbp": discounted_cost,
                    "discounted_energy_mwh": 0.0,
                }
            )

    first_year_delivered_mwh = delivered_capacity_mw * HOURS_PER_YEAR * capacity_factor
    discounted_energy = 0.0
    undiscounted_energy = 0.0
    first_year_variable_opex = costs["variable_opex_gbp_per_mwh"] * first_year_delivered_mwh
    for operating_year in range(1, operating_lifetime_years + 1):
        year = construction_duration_years + operating_year
        delivered_mwh = first_year_delivered_mwh * ((1.0 - degradation) ** (operating_year - 1))
        variable_opex = costs["variable_opex_gbp_per_mwh"] * delivered_mwh
        real_cost = annual_fixed_opex + annual_space_replacement + annual_ground_replacement + variable_opex
        discounted_fixed = _discount(annual_fixed_opex, discount_rate, year)
        discounted_variable = _discount(variable_opex, discount_rate, year)
        discounted_space_replacement = _discount(annual_space_replacement, discount_rate, year)
        discounted_ground_replacement = _discount(annual_ground_replacement, discount_rate, year)
        discounted_cost = (
            discounted_fixed
            + discounted_variable
            + discounted_space_replacement
            + discounted_ground_replacement
        )
        discounted_year_energy = _discount(delivered_mwh, discount_rate, year)
        lifecycle_pv["fixed_opex"] += discounted_fixed
        lifecycle_pv["variable_opex"] += discounted_variable
        lifecycle_pv["space_hardware_replacement"] += discounted_space_replacement
        lifecycle_pv["ground_hardware_replacement"] += discounted_ground_replacement
        discounted_energy += discounted_year_energy
        undiscounted_energy += delivered_mwh
        cash_flow_rows.append(
            {
                "year": float(year),
                "phase": "operation",
                "real_cost_gbp": real_cost,
                "delivered_energy_mwh": delivered_mwh,
                "discounted_cost_gbp": discounted_cost,
                "discounted_energy_mwh": discounted_year_energy,
            }
        )

    terminal_year = construction_duration_years + operating_lifetime_years
    decommissioning_cost = decommissioning_fraction * initial_capex
    residual_value = residual_fraction * initial_capex
    lifecycle_pv["decommissioning"] = _discount(decommissioning_cost, discount_rate, terminal_year)
    lifecycle_pv["residual_value"] = -_discount(residual_value, discount_rate, terminal_year)
    if cash_flow_rows:
        terminal_net = decommissioning_cost - residual_value
        if terminal_net:
            cash_flow_rows.append(
                {
                    "year": float(terminal_year),
                    "phase": "terminal",
                    "real_cost_gbp": terminal_net,
                    "delivered_energy_mwh": 0.0,
                    "discounted_cost_gbp": _discount(terminal_net, discount_rate, terminal_year),
                    "discounted_energy_mwh": 0.0,
                }
            )

    discounted_lifetime_cost = sum(lifecycle_pv.values())
    if discounted_energy <= 0:
        raise ValueError("Discounted lifetime energy must be positive.")
    lcoe = discounted_lifetime_cost / discounted_energy

    crf_annualized_capex = initial_capex * capital_recovery_factor(
        discount_rate,
        operating_lifetime_years,
    )
    crf_reconciliation_lcoe = (
        crf_annualized_capex
        + annual_fixed_opex
        + annual_space_replacement
        + annual_ground_replacement
        + first_year_variable_opex
    ) / first_year_delivered_mwh

    return LCOEResult(
        lcoe_gbp_per_mwh=lcoe,
        crf_reconciliation_lcoe_gbp_per_mwh=crf_reconciliation_lcoe,
        end_to_end_efficiency=end_to_end_efficiency,
        energy_chain_power_w=energy_chain,
        orbital_mass_kg=orbital_mass_kg,
        required_launches=required_launches,
        launch_pricing_mode=mode,
        initial_capex_gbp=initial_capex,
        pre_contingency_capex_gbp=pre_contingency_capex,
        programme_contingency_gbp=programme_contingency,
        capex_components_gbp=capex_components,
        discounted_lifetime_cost_gbp=discounted_lifetime_cost,
        discounted_lifetime_energy_mwh=discounted_energy,
        lifecycle_cost_components_pv_gbp=lifecycle_pv,
        first_year_delivered_mwh=first_year_delivered_mwh,
        average_annual_delivered_mwh=undiscounted_energy / operating_lifetime_years,
        fixed_opex_eligible_asset_base_gbp=fixed_opex_eligible_base,
        space_replacement_eligible_cost_base_gbp=space_replacement_eligible_base,
        ground_replacement_eligible_cost_base_gbp=ground_replacement_eligible_base,
        annual_fixed_opex_gbp=annual_fixed_opex,
        annual_space_replacement_gbp=annual_space_replacement,
        annual_ground_replacement_gbp=annual_ground_replacement,
        first_year_variable_opex_gbp=first_year_variable_opex,
        construction_spend_profile=profile,
        cash_flow_rows=tuple(cash_flow_rows),
        price_year=PRICE_YEAR,
        valuation_base=VALUATION_BASE,
        staging_orbit=str(parameters.get("staging_orbit", DEFAULT_STAGING_ORBIT)),
        operational_orbit=str(parameters.get("operational_orbit", DEFAULT_OPERATIONAL_ORBIT)),
    )


def with_overrides(parameters: Mapping[str, object], **overrides: object) -> dict[str, object]:
    updated = dict(parameters)
    updated.update(overrides)
    return updated
