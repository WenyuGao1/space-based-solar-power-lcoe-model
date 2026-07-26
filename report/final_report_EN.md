# UK Space-Based Solar Power Cost-Condition Assessment — v2.0

**This is a conditional scenario result, not a commercial forecast, quotation, official UK target or proof of economic viability.**

## Scope and answer

The reference scenario gives a conditional delivered-grid DCF LCOE of **£86.03/MWh** in 2024 real GBP. Working backwards from 2 GW AC at the grid boundary, the five-stage chain computes an end-to-end efficiency of **14.98%**, orbital hardware mass of **10.00 million kg**, and **118** equivalent launches.

Launch pricing mode: per kg, to staging orbit only. Staging orbit: LEO staging orbit (service boundary; altitude architecture-dependent). Operational orbit: High Earth orbit (HEO; final orbit architecture-dependent). The transfer proxy must cover transfer vehicle, propellant, refuelling missions, operations and payload-performance penalty.

## Migration from v1.x to v2.0

v1.x multiplied a 1.5 kg/kW value that should have been delivered-power-normalised by 'delivered power / efficiency', dividing by efficiency a second time. For 2 GW at 20% efficiency, the old expression gives **15,000,000 kg (15,000 tonnes)**; the corrected expression gives **3,000,000 kg (3,000 tonnes)**. With all other v2 comparison inputs identical, the erroneous mass boundary gives **£116.45/MWh**, versus **£43.45/MWh** on the corrected boundary. Historical v1.x thresholds are therefore not directly comparable with v2.0.

The DESNZ/Frazer-Nash report defines architecture specific power as ground-delivered power per orbital mass. The reciprocal of 0.67 kW-delivered/kg is **1.4925 kg/kW-delivered** (Table 1, PDF pp.11-12; reference-design selection p.13). Values remain architecture-specific and may include manufacturer claims that were not independently verified.

## Stage-resolved energy chain

| Stage | Rated power |
| --- | --- |
| Incident solar | 13.35 GW |
| Space DC bus | 4.67 GW |
| Emitted RF | 3.27 GW |
| RF incident on rectenna | 3.21 GW |
| Rectenna DC output | 2.08 GW |
| Grid-delivered AC | 2.00 GW |

Computed end-to-end efficiency: **14.9822%**.

## Discounted-cash-flow boundary

The headline uses LCOE = Σ(Cₜ/(1+r)ᵗ) / Σ(Eₜ/(1+r)ᵗ). The valuation base is start of construction at t=0; four equal construction shares are spent before commissioning, and the first operating-year cash flow is at t=5. The operating life is 30 years. First-year energy is 15.77 TWh and lifetime-average annual energy is 14.68 TWh. Discounted lifecycle cost is £13.10bn and discounted energy is 152.32 million MWh. The simple CRF reconciliation is £71.02/MWh and is secondary only.

## Reference cost structure

| CAPEX component | 2024 real GBP |
| --- | --- |
| Launch To Staging Orbit | £5.00bn |
| In Orbit Assembly And Deployment | £2.00bn |
| Space Generation Hardware | £1.87bn |
| Orbit Transfer To Operational Orbit | £1.00bn |
| Wireless Power Transmitter | £0.33bn |
| Rectenna | £0.30bn |
| Grid Connection | £0.20bn |
| Programme contingency | £2.14bn |
| Initial CAPEX | £12.84bn |

| Lifecycle component | Discounted PV | LCOE contribution |
| --- | --- | --- |
| Initial Construction | £11.71bn | £76.86/MWh |
| Space Hardware Replacement | £0.62bn | £4.08/MWh |
| Variable Opex | £0.46bn | £3.00/MWh |
| Fixed Opex | £0.27bn | £1.80/MWh |
| Decommissioning | £0.03bn | £0.20/MWh |
| Ground Hardware Replacement | £0.02bn | £0.10/MWh |
| Residual Value | £-0.00bn | £-0.00/MWh |

![Reference lifecycle LCOE components](../figures/reference_lcoe_components.png)

## Conditional sensitivities and thresholds

| Parameter | LCOE at favourable bound | Reduction |
| --- | --- | --- |
| System specific mass | £31.3/MWh | £54.7/MWh |
| Launch service cost to staging orbit | £49.5/MWh | £36.5/MWh |
| Real project discount rate | £56.9/MWh | £29.1/MWh |
| In-orbit assembly and deployment cost | £70.8/MWh | £15.2/MWh |
| Space-generation hardware cost | £72.5/MWh | £13.5/MWh |
| Initial programme contingency | £73.2/MWh | £12.8/MWh |
| Construction duration | £74.7/MWh | £11.4/MWh |
| Staging-to-operational-orbit transfer cost | £78.4/MWh | £7.6/MWh |

£80: Delivered capacity factor=0.9705, £80: Operating lifetime after commissioning=43, £80: Real project discount rate=0.05853, £60: Real project discount rate=0.03423, £80: Construction duration=1, £80: System specific mass=4.504, £60: System specific mass=2.861, £80: Space-generation hardware cost=0.244

The equal-fraction frontier is a mathematical interpolation device, not a readiness score, probability, forecast, schedule or engineering roadmap.

| Target | Equal-fraction movement | Computed chain efficiency |
| --- | --- | --- |
| £150/MWh | 0.0% | 14.98% |
| £120/MWh | 0.0% | 14.98% |
| £100/MWh | 0.0% | 14.98% |
| £80/MWh | 2.9% | 15.36% |
| £60/MWh | 12.5% | 16.64% |

![One-way floors](../figures/one_way_lcoe_floors.png)

![Mass sensitivity](../figures/specific_mass_threshold_focus.png)

![Combined interpolation](../figures/combined_progress_frontier.png)

## Parameter evidence and limitations

Every user-facing numerical input below carries source type, source ID, price year where relevant, denominator and limitation metadata.

| Parameter | Reference | Range | Source | Denominator / boundary | Limitation |
| --- | --- | --- | --- | --- | --- |
| Delivered grid capacity | 2000 MW-delivered AC | 500–5000 | exploratory / ASSUMPTION_THIS_STUDY | AC power at the grid connection point | Scale input; the simplified model is nearly scale-neutral. |
| Solar-to-DC conversion efficiency | 0.35 fraction | 0.2–0.45 | exploratory / ASSUMPTION_THIS_STUDY | Incident solar power to space DC-bus output | Architecture-dependent exploratory value; not an independently verified flight-system value. |
| DC-to-RF efficiency | 0.7 fraction | 0.4–0.85 | exploratory / ASSUMPTION_THIS_STUDY | Space DC-bus input to emitted RF power | Excludes propagation and rectenna conversion losses. |
| RF transmission efficiency | 0.98 fraction | 0.85–0.995 | exploratory / ASSUMPTION_THIS_STUDY | Emitted RF power to RF incident on the rectenna | Simplified beam-capture proxy; beam geometry sidelobes weather and safety constraints are not explicitly modelled. |
| Rectenna RF-to-DC efficiency | 0.65 fraction | 0.4–0.85 | exploratory / ASSUMPTION_THIS_STUDY | Incident RF power at rectenna to rectenna DC output | Exploratory system-average conversion proxy. |
| DC-to-grid AC efficiency | 0.96 fraction | 0.9–0.99 | exploratory / ASSUMPTION_THIS_STUDY | Rectenna DC output to AC at the grid connection point | Includes simplified inversion and local electrical losses only. |
| Delivered capacity factor | 0.9 fraction | 0.6–0.98 | exploratory / ASSUMPTION_THIS_STUDY | Annual AC energy divided by rated delivered AC capacity times 8760 | Combines availability outages and operating constraints; not a measured forecast. |
| Operating lifetime after commissioning | 30 years | 15–45 | exploratory / ASSUMPTION_THIS_STUDY | Full operating years after commissioning | Engineering retirement and economic life are simplified into one duration. |
| Real project discount rate | 0.065 fraction | 0.03–0.2 | exploratory / ASSUMPTION_THIS_STUDY | Discounting from start of construction t=0 | Not an observed SBSP WACC; tax financing tranches and inflation are excluded. |
| Construction duration | 4 years | 0–8 | exploratory / ASSUMPTION_THIS_STUDY | Years from valuation base to commissioning | Default uses equal annual spend shares; project-specific scheduling is not represented. |
| Annual delivered-output degradation | 0.005 fraction/year | 0–0.03 | exploratory / ASSUMPTION_THIS_STUDY | Year-on-year reduction in delivered AC energy after the first operating year | Simplified fleet-average degradation proxy. |
| System specific mass | 5 kg/kW-delivered | 0.5–10 | exploratory / ASSUMPTION_THIS_STUDY | Complete operational orbital hardware mass per kW delivered AC at the grid boundary | Delivered-power basis; never divide by efficiency again. Published values can be architecture-specific or manufacturer-claimed. |
| Space-generation hardware cost | 0.4 GBP/W-DC | 0.05–5 | exploratory / ASSUMPTION_THIS_STUDY | Space DC-bus rated output excluding RF transmitter hardware | Includes collection structure conversion and DC conditioning only; boundary is mutually exclusive with transmitter cost. |
| RF transmitter hardware cost | 0.1 GBP/W-RF emitted | 0.02–1 | exploratory / ASSUMPTION_THIS_STUDY | Emitted RF rated power excluding generation and DC-bus hardware | Includes only DC-to-RF and aperture hardware; no generation hardware is counted here. |
| Launch service cost to staging orbit | 500 GBP/kg to staging orbit | 20–5000 | exploratory / ASSUMPTION_THIS_STUDY | Operational orbital hardware mass delivered to the defined LEO staging boundary | Not a GEO delivery quotation; procurement cadence integration and destination materially affect price. |
| Launch price per flight | 1e+08 GBP/flight | 1e+07–3e+08 | exploratory / ASSUMPTION_THIS_STUDY | One mutually exclusive launch flight to the staging orbit | Used only when per-flight mode is active; never added to per-kg launch cost. |
| Effective payload per flight | 100000 kg/flight | 20000–250000 | exploratory / ASSUMPTION_THIS_STUDY | Maximum manifested hardware mass reaching the staging orbit per flight | Vehicle and orbit dependent; used for launch-count diagnostics in both modes. |
| Payload utilisation | 0.85 fraction | 0.5–1 | exploratory / ASSUMPTION_THIS_STUDY | Average used fraction of effective payload capability | Does not model packaging volume schedule or rideshare constraints. |
| Staging-to-operational-orbit transfer cost | 100 GBP/kg final hardware | 0–3000 | exploratory / ASSUMPTION_THIS_STUDY | Final operational hardware moved from staging orbit to operational orbit | Must cover transfer vehicle propellant refuelling missions operations and payload penalty; a low value does not prove cheap HEO delivery. |
| In-orbit assembly and deployment cost | 200 GBP/kg operational hardware | 0–3000 | exploratory / ASSUMPTION_THIS_STUDY | Operational orbital hardware assembled deployed and commissioned | Exploratory allowance; robotic operations inspection spares and commissioning are bundled. |
| Rectenna cost | 0.15 GBP/W-delivered AC | 0.02–1 | exploratory / ASSUMPTION_THIS_STUDY | Rated AC power delivered at the grid boundary | Bundled proxy; antenna area frequency beam geometry sidelobes power-density land weather and safety are not explicit. |
| Grid connection cost | 100 GBP/kW-delivered AC | 20–300 | exploratory / ASSUMPTION_THIS_STUDY | Rated AC power at the grid connection point | Simplified local connection allowance; wider transmission reinforcement is excluded. |
| Initial programme contingency | 0.2 fraction of pre-contingency initial CAPEX | 0–0.5 | exploratory / ASSUMPTION_THIS_STUDY | Applied once to pre-contingency initial construction CAPEX | Not applied recursively to annual O&M or replacement allowances. |
| Space-hardware replacement rate | 0.006 fraction/year | 0–0.03 | exploratory / ASSUMPTION_THIS_STUDY | Fraction of eligible space hardware plus associated launch transfer and assembly cost replaced each year | Simplified annual equivalent rather than discrete failure and logistics scheduling. |
| Ground-hardware replacement rate | 0.003 fraction/year | 0–0.02 | exploratory / ASSUMPTION_THIS_STUDY | Fraction of eligible rectenna and grid cost replaced each year | Does not model component-specific replacement intervals. |
| Fixed O&M rate | 0.01 fraction/year | 0.002–0.05 | exploratory / ASSUMPTION_THIS_STUDY | Applied to generation transmitter rectenna and grid assets only | Excludes contingency initial launch transfer and assembly from its base. |
| Variable O&M | 3 GBP/MWh delivered | 0–20 | exploratory / ASSUMPTION_THIS_STUDY | Each MWh of AC energy delivered at the grid boundary | Exploratory allowance; market charges and downstream system costs are excluded. |
| Terminal decommissioning cost | 0.02 fraction of initial CAPEX | 0–0.2 | exploratory / ASSUMPTION_THIS_STUDY | Applied at the end of operating life to initial CAPEX | Timing and disposal obligations are simplified. |
| Terminal residual value | 0 fraction of initial CAPEX | 0–0.2 | exploratory / ASSUMPTION_THIS_STUDY | Credit at end of operating life relative to initial CAPEX | No default credit; salvage markets and liabilities are uncertain. |

## Formulae, boundaries and validation

Mass is orbital mass = delivered capacity (kW) × kg/kW-delivered. Hardware costs are rated independently at space-DC-bus W, emitted-RF W, delivered W or delivered kW, with mutually exclusive boundaries. Space replacement includes hardware plus associated launch, transfer and assembly; ground replacement includes only rectenna and grid. Fixed O&M excludes contingency, initial launch, transfer and assembly.

The default construction profile is `[0.25, 0.25, 0.25, 0.25]` and sums to 100%. Programme contingency is applied once to initial CAPEX. Terminal decommissioning is a cost and residual value is a credit at the end of operating life.

The test suite checks reciprocal mass conversion, the 2 GW / 0.67 kW/kg regression, no second efficiency division, all six stage powers, rated-cost assignment, launch-mode exclusivity, launch rounding, replacement bases, construction shares, DCF/CRF convergence, zero-rate handling, invalid inputs, Python/browser parity, bilingual parity, removal of the historical mass identifier and full regeneration.

## Remaining limitations

- No physical design of antenna area, frequency, beam geometry, sidelobes, power density, land, weather or safety constraints.
- No vehicle manifest, structural load, thermal, radiation, failure, spares, discrete replacement mission or detailed launch schedule.
- No tax, inflation, financing tranches, learning curves or architecture-parameter correlations.
- No GB dispatch, network reinforcement, balancing, capacity value or market-revenue model.
- Exploration bounds are not probability distributions; no P10/P50/P90 labels are produced.

Generated from the executable model. Price year: 2024 real GBP. Valuation base: start of construction (t=0).
