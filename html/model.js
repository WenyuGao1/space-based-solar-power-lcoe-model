(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.SBSPModel = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const HOURS = 8760;

  function specificMassFromSpecificPower(value) {
    value = Number(value);
    if (!Number.isFinite(value) || value <= 0) throw new Error('Specific power must be positive.');
    return 1 / value;
  }

  function specificPowerFromSpecificMass(value) {
    value = Number(value);
    if (!Number.isFinite(value) || value <= 0) throw new Error('Specific mass must be positive.');
    return 1 / value;
  }

  function capitalRecoveryFactor(rate, years) {
    if (years <= 0) throw new Error('Lifetime must be positive.');
    if (rate <= -1) throw new Error('Rate must be above -100%.');
    if (Math.abs(rate) < 1e-12) return 1 / years;
    const growth = Math.pow(1 + rate, years);
    return rate * growth / (growth - 1);
  }

  function validateSpendProfile(shares, duration) {
    if (!Number.isInteger(duration) || duration < 0) throw new Error('Construction duration must be a non-negative integer.');
    if (!Array.isArray(shares) || shares.length !== duration) throw new Error('Construction shares must match duration.');
    if (shares.some(v => !Number.isFinite(Number(v)) || Number(v) < 0)) throw new Error('Invalid construction share.');
    const expected = duration ? 1 : 0;
    if (Math.abs(shares.reduce((a, b) => a + Number(b), 0) - expected) > 1e-10) throw new Error('Construction shares must sum to 100%.');
    return shares.map(Number);
  }

  function calculateLcoe(input, options) {
    const p = Object.assign({}, input);
    options = options || {};
    const required = name => {
      const value = Number(p[name]);
      if (!Number.isFinite(value)) throw new Error('Missing or invalid input: ' + name);
      return value;
    };
    const fraction = (name, allowZero) => {
      const value = required(name);
      if ((allowZero ? value < 0 : value <= 0) || value > 1) throw new Error(name + ' must be a valid fraction.');
      return value;
    };

    const deliveredMw = required('delivered_capacity_mw');
    const capacityFactor = fraction('capacity_factor', false);
    const lifetime = required('operating_lifetime_years');
    const duration = required('construction_duration_years');
    const rate = required('real_discount_rate');
    const degradation = fraction('annual_output_degradation_fraction', true);
    if (deliveredMw <= 0 || !Number.isInteger(lifetime) || lifetime <= 0 || !Number.isInteger(duration) || duration < 0 || rate < 0 || rate >= 1 || degradation >= 1) throw new Error('Invalid scale, time or finance input.');

    const etaSolar = fraction('solar_conversion_efficiency', false);
    const etaDcRf = fraction('dc_to_rf_efficiency', false);
    const etaTx = fraction('transmission_efficiency', false);
    const etaRect = fraction('rectenna_conversion_efficiency', false);
    const etaGrid = fraction('grid_conversion_efficiency', false);
    const endToEnd = etaSolar * etaDcRf * etaTx * etaRect * etaGrid;
    const deliveredW = deliveredMw * 1e6;
    const deliveredKw = deliveredMw * 1000;
    const rectennaDcW = deliveredW / etaGrid;
    const incidentRfW = rectennaDcW / etaRect;
    const emittedRfW = incidentRfW / etaTx;
    const spaceDcW = emittedRfW / etaDcRf;
    const solarW = spaceDcW / etaSolar;
    const energyChain = {
      incident_solar_power_w: solarW,
      space_dc_bus_power_w: spaceDcW,
      emitted_rf_power_w: emittedRfW,
      incident_rf_power_w: incidentRfW,
      rectenna_dc_power_w: rectennaDcW,
      delivered_grid_ac_power_w: deliveredW
    };

    const massIntensity = required('system_specific_mass_kg_per_kw_delivered');
    if (massIntensity <= 0) throw new Error('Specific mass must be positive.');
    const orbitalMass = deliveredKw * massIntensity;
    const effectivePayload = required('effective_payload_kg_per_flight');
    const utilisation = fraction('payload_utilisation_fraction', false);
    if (effectivePayload <= 0) throw new Error('Payload must be positive.');
    const requiredLaunches = Math.ceil(orbitalMass / (effectivePayload * utilisation));
    const mode = options.launchPricingMode || p.launch_pricing_mode || 'per_kg';
    if (mode !== 'per_kg' && mode !== 'per_flight') throw new Error('Invalid launch pricing mode.');
    const perKg = required('launch_cost_gbp_per_kg_to_staging_orbit');
    const perFlight = required('launch_price_gbp_per_flight');
    if (perKg < 0 || perFlight < 0) throw new Error('Launch price cannot be negative.');
    const launch = mode === 'per_kg' ? orbitalMass * perKg : requiredLaunches * perFlight;

    const nonnegative = name => { const value = required(name); if (value < 0) throw new Error(name + ' cannot be negative.'); return value; };
    const capex = {
      space_generation_hardware: nonnegative('space_generation_hardware_cost_gbp_per_w_dc') * spaceDcW,
      wireless_power_transmitter: nonnegative('transmitter_cost_gbp_per_w_rf_emitted') * emittedRfW,
      launch_to_staging_orbit: launch,
      orbit_transfer_to_operational_orbit: nonnegative('orbit_transfer_cost_gbp_per_kg_final_hardware') * orbitalMass,
      in_orbit_assembly_and_deployment: nonnegative('in_orbit_assembly_cost_gbp_per_kg_operational_hardware') * orbitalMass,
      rectenna: nonnegative('rectenna_cost_gbp_per_w_delivered') * deliveredW,
      grid_connection: nonnegative('grid_connection_cost_gbp_per_kw_delivered') * deliveredKw
    };
    const preContingency = Object.values(capex).reduce((a, b) => a + b, 0);
    const contingency = fraction('programme_contingency_fraction', true) * preContingency;
    const initialCapex = preContingency + contingency;
    const fixedBase = capex.space_generation_hardware + capex.wireless_power_transmitter + capex.rectenna + capex.grid_connection;
    const spaceBase = capex.space_generation_hardware + capex.wireless_power_transmitter + capex.launch_to_staging_orbit + capex.orbit_transfer_to_operational_orbit + capex.in_orbit_assembly_and_deployment;
    const groundBase = capex.rectenna + capex.grid_connection;
    const annualFixed = fraction('fixed_opex_fraction_of_eligible_assets_per_year', true) * fixedBase;
    const annualSpace = fraction('space_hardware_replacement_rate_per_year', true) * spaceBase;
    const annualGround = fraction('ground_hardware_replacement_rate_per_year', true) * groundBase;
    const variableRate = nonnegative('variable_opex_gbp_per_mwh');
    const decommissionFraction = fraction('decommissioning_cost_fraction_initial_capex', true);
    const residualFraction = fraction('residual_value_fraction_initial_capex', true);
    const profile = options.constructionSpendProfile !== undefined ? validateSpendProfile(options.constructionSpendProfile, duration) : (duration ? Array(duration).fill(1 / duration) : []);
    const discount = (value, year) => value / Math.pow(1 + rate, year);
    const lifecycle = { initial_construction: 0, fixed_opex: 0, variable_opex: 0, space_hardware_replacement: 0, ground_hardware_replacement: 0, decommissioning: 0, residual_value: 0 };
    if (!duration) lifecycle.initial_construction = initialCapex;
    else profile.forEach((share, year) => { lifecycle.initial_construction += discount(initialCapex * share, year); });
    const firstYearEnergy = deliveredMw * HOURS * capacityFactor;
    let discountedEnergy = 0;
    let undiscountedEnergy = 0;
    for (let operatingYear = 1; operatingYear <= lifetime; operatingYear++) {
      const year = duration + operatingYear;
      const energy = firstYearEnergy * Math.pow(1 - degradation, operatingYear - 1);
      const variable = variableRate * energy;
      lifecycle.fixed_opex += discount(annualFixed, year);
      lifecycle.variable_opex += discount(variable, year);
      lifecycle.space_hardware_replacement += discount(annualSpace, year);
      lifecycle.ground_hardware_replacement += discount(annualGround, year);
      discountedEnergy += discount(energy, year);
      undiscountedEnergy += energy;
    }
    const terminalYear = duration + lifetime;
    lifecycle.decommissioning = discount(decommissionFraction * initialCapex, terminalYear);
    lifecycle.residual_value = -discount(residualFraction * initialCapex, terminalYear);
    const discountedCost = Object.values(lifecycle).reduce((a, b) => a + b, 0);
    const lcoe = discountedCost / discountedEnergy;
    const crfLcoe = (initialCapex * capitalRecoveryFactor(rate, lifetime) + annualFixed + annualSpace + annualGround + variableRate * firstYearEnergy) / firstYearEnergy;
    return {
      lcoe_gbp_per_mwh: lcoe,
      crf_reconciliation_lcoe_gbp_per_mwh: crfLcoe,
      end_to_end_efficiency: endToEnd,
      energy_chain_power_w: energyChain,
      orbital_mass_kg: orbitalMass,
      required_launches: requiredLaunches,
      launch_pricing_mode: mode,
      initial_capex_gbp: initialCapex,
      pre_contingency_capex_gbp: preContingency,
      programme_contingency_gbp: contingency,
      capex_components_gbp: capex,
      discounted_lifetime_cost_gbp: discountedCost,
      discounted_lifetime_energy_mwh: discountedEnergy,
      lifecycle_cost_components_pv_gbp: lifecycle,
      first_year_delivered_mwh: firstYearEnergy,
      average_annual_delivered_mwh: undiscountedEnergy / lifetime,
      fixed_opex_eligible_asset_base_gbp: fixedBase,
      space_replacement_eligible_cost_base_gbp: spaceBase,
      ground_replacement_eligible_cost_base_gbp: groundBase,
      annual_fixed_opex_gbp: annualFixed,
      annual_space_replacement_gbp: annualSpace,
      annual_ground_replacement_gbp: annualGround,
      first_year_variable_opex_gbp: variableRate * firstYearEnergy,
      construction_spend_profile: profile
    };
  }

  return { calculateLcoe, capitalRecoveryFactor, validateSpendProfile, specificMassFromSpecificPower, specificPowerFromSpecificMass };
}));
