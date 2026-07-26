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

Default-value status identifies who set the number; it does not relabel contextual literature as a direct numerical source. All 29 defaults are study-authored exploratory assumptions. External studies are used only as technical context, range inspiration or consistency checks where boundaries are comparable.

| Parameter | Reference | Range | Denominator / boundary | Limitation |
| --- | --- | --- | --- | --- |
| Delivered grid capacity | 2000 MW-delivered AC | 500–5000 | AC power at the grid connection point | Scale input; the simplified model is nearly scale-neutral. |
| Solar-to-DC conversion efficiency | 0.35 fraction | 0.2–0.45 | Incident solar power to space DC-bus output | Architecture-dependent exploratory value; not an independently verified flight-system value. |
| DC-to-RF efficiency | 0.7 fraction | 0.4–0.85 | Space DC-bus input to emitted RF power | Excludes propagation and rectenna conversion losses. |
| RF transmission efficiency | 0.98 fraction | 0.85–0.995 | Emitted RF power to RF incident on the rectenna | Simplified beam-capture proxy; beam geometry sidelobes weather and safety constraints are not explicitly modelled. |
| Rectenna RF-to-DC efficiency | 0.65 fraction | 0.4–0.85 | Incident RF power at rectenna to rectenna DC output | Exploratory system-average conversion proxy. |
| DC-to-grid AC efficiency | 0.96 fraction | 0.9–0.99 | Rectenna DC output to AC at the grid connection point | Includes simplified inversion and local electrical losses only. |
| Delivered capacity factor | 0.9 fraction | 0.6–0.98 | Annual AC energy divided by rated delivered AC capacity times 8760 | Combines availability outages and operating constraints; not a measured forecast. |
| Operating lifetime after commissioning | 30 years | 15–45 | Full operating years after commissioning | Engineering retirement and economic life are simplified into one duration. |
| Real project discount rate | 0.065 fraction | 0.03–0.2 | Discounting from start of construction t=0 | Not an observed SBSP WACC; tax financing tranches and inflation are excluded. |
| Construction duration | 4 years | 0–8 | Years from valuation base to commissioning | Default uses equal annual spend shares; project-specific scheduling is not represented. |
| Annual delivered-output degradation | 0.005 fraction/year | 0–0.03 | Year-on-year reduction in delivered AC energy after the first operating year | Simplified fleet-average degradation proxy. |
| System specific mass | 5 kg/kW-delivered | 0.5–10 | Complete operational orbital hardware mass per kW delivered AC at the grid boundary | Delivered-power basis; never divide by efficiency again. Published values can be architecture-specific or manufacturer-claimed. |
| Space-generation hardware cost | 0.4 GBP/W-DC | 0.05–5 | Space DC-bus rated output excluding RF transmitter hardware | Includes collection structure conversion and DC conditioning only; boundary is mutually exclusive with transmitter cost. |
| RF transmitter hardware cost | 0.1 GBP/W-RF emitted | 0.02–1 | Emitted RF rated power excluding generation and DC-bus hardware | Includes only DC-to-RF and aperture hardware; no generation hardware is counted here. |
| Launch service cost to staging orbit | 500 GBP/kg to staging orbit | 20–5000 | Operational orbital hardware mass delivered to the defined LEO staging boundary | Not a GEO delivery quotation; procurement cadence integration and destination materially affect price. |
| Launch price per flight | 1e+08 GBP/flight | 1e+07–3e+08 | One mutually exclusive launch flight to the staging orbit | Used only when per-flight mode is active; never added to per-kg launch cost. |
| Effective payload per flight | 100000 kg/flight | 20000–250000 | Maximum manifested hardware mass reaching the staging orbit per flight | Vehicle and orbit dependent; used for launch-count diagnostics in both modes. |
| Payload utilisation | 0.85 fraction | 0.5–1 | Average used fraction of effective payload capability | Does not model packaging volume schedule or rideshare constraints. |
| Staging-to-operational-orbit transfer cost | 100 GBP/kg final hardware | 0–3000 | Final operational hardware moved from staging orbit to operational orbit | Must cover transfer vehicle propellant refuelling missions operations and payload penalty; a low value does not prove cheap HEO delivery. |
| In-orbit assembly and deployment cost | 200 GBP/kg operational hardware | 0–3000 | Operational orbital hardware assembled deployed and commissioned | Exploratory allowance; robotic operations inspection spares and commissioning are bundled. |
| Rectenna cost | 0.15 GBP/W-delivered AC | 0.02–1 | Rated AC power delivered at the grid boundary | Bundled proxy; antenna area frequency beam geometry sidelobes power-density land weather and safety are not explicit. |
| Grid connection cost | 100 GBP/kW-delivered AC | 20–300 | Rated AC power at the grid connection point | Simplified local connection allowance; wider transmission reinforcement is excluded. |
| Initial programme contingency | 0.2 fraction of pre-contingency initial CAPEX | 0–0.5 | Applied once to pre-contingency initial construction CAPEX | Not applied recursively to annual O&M or replacement allowances. |
| Space-hardware replacement rate | 0.006 fraction/year | 0–0.03 | Fraction of eligible space hardware plus associated launch transfer and assembly cost replaced each year | Simplified annual equivalent rather than discrete failure and logistics scheduling. |
| Ground-hardware replacement rate | 0.003 fraction/year | 0–0.02 | Fraction of eligible rectenna and grid cost replaced each year | Does not model component-specific replacement intervals. |
| Fixed O&M rate | 0.01 fraction/year | 0.002–0.05 | Applied to generation transmitter rectenna and grid assets only | Excludes contingency initial launch transfer and assembly from its base. |
| Variable O&M | 3 GBP/MWh delivered | 0–20 | Each MWh of AC energy delivered at the grid boundary | Exploratory allowance; market charges and downstream system costs are excluded. |
| Terminal decommissioning cost | 0.02 fraction of initial CAPEX | 0–0.2 | Applied at the end of operating life to initial CAPEX | Timing and disposal obligations are simplified. |
| Terminal residual value | 0 fraction of initial CAPEX | 0–0.2 | Credit at end of operating life relative to initial CAPEX | No default credit; salvage markets and liabilities are uncertain. |

### External evidence map (not direct model inputs)

The table links parameters and claims to auditable external evidence, including document locators and comparability limits. Unless explicitly stated, these published values do not replace the model defaults.

| Parameter / claim | Evidence role | External source and locator | Evidence context and comparability limit |
| --- | --- | --- | --- |
| Delivered Capacity Mw | external precedent | UK_SBSP_2021_PHASE2 · PDF pp.18-19 | The 2021 architecture-specific case uses a 2 GW delivered plant. Numeric context: 2 GW CASSIOPeiA case. Comparability limit: The same number is used here as a study scale anchor, not as evidence that this architecture is preferred. |
| System Lifetime Years | external precedent | UK_SBSP_2021_PHASE2 · PDF pp.18-19 | The 2021 utility-scale economic case uses a 30-year operating life. Numeric context: 30 years; the later small-scale study uses 15 years. Comparability limit: Lifetime remains architecture-dependent and the model does not demonstrate survivability or refurbishment feasibility. |
| Computed End To End Efficiency | technical context | CALTECH_SBSP_2022 · abstract | A lightweight modular concept reports substantial full-chain losses. Numeric context: 7-14% end-to-end efficiency. Comparability limit: Concept and subsystem boundaries differ; this is a consistency check on the computed output rather than a model input. |
| Computed End To End Efficiency | source-inspired assumption | UK_SBSP_2021_ANNEX_B · PDF p.4 | Products of reported component efficiencies provide context for a stage-resolved chain. Numeric context: approximately 14.85-24.39% from independent factor products. Comparability limit: Independent extrema do not define a probability distribution or a validated integrated design. |
| Computed End To End Efficiency | external consistency check | DESNZ_SBSP_2025 · Table 1, PDF pp.11-12; reference-design selection p.13 | The official small-scale study reports architecture-level total-efficiency cases. Numeric context: 11.7-19.9%; selected Space Solar small-scale reference design 14.9%. Comparability limit: Major values may be manufacturer-claimed or inferred and definitions may differ. |
| Capacity Factor | scope qualification | DESNZ_SBSP_2025 · Table 3, PDF p.16 | The official study demonstrates that utilization varies materially by orbit and by the measured boundary. Numeric context: HEO: UK rectenna 95.7%, satellite average 53.9%; circular LEO: satellite average 20.1%, UK rectenna 21.5%. Comparability limit: Rectenna utilization is not equivalent to this model's delivered capacity factor; the 90% value remains a study assumption. |
| System Specific Mass Kg Per Kw Delivered | technical context | CALTECH_SBSP_2022 · abstract | Lightweight structures are central to proposed modular SBSP architectures. Numeric context: 160 g/m2 areal density. Comparability limit: Areal density cannot be converted to whole-system kg/kW-delivered without a complete delivered-power and subsystem boundary. |
| System Specific Mass Kg Per Kw Delivered | external consistency check | DESNZ_SBSP_2025 · Table 1, PDF pp.11-12; reference-design selection p.13 | Architecture specific power is ground-delivered power per unit orbital mass; its reciprocal is kg/kW-delivered. Numeric context: 0.15-0.67 kW-delivered/kg; 0.67 converts to 1.4925 kg/kW-delivered. Comparability limit: Architecture-specific values are partly manufacturer-claimed; conversion does not verify engineering readiness and the model default remains exploratory. |
| Launch Cost Gbp Per Kg To Staging Orbit | external range | UK_SBSP_2021_ANNEX_B · PDF p.5 and p.11 | The 2021 input review uses a broad architecture-specific spacelift range. Numeric context: £358-2,410/kg. Comparability limit: Orbit procurement price year and service boundary differ from this staging-orbit variable. |
| Launch Cost Gbp Per Kg To Staging Orbit | external comparison | DESNZ_SBSP_2025 · Table 12 p.37; Tables 27-28 pp.71-73 | Launch cost is a dominant driver in the official small-scale cases. Numeric context: central HEO £1,647/1,400/1,153 per kg; optimistic £1,188/1,008/827 for 2030/35/40. Comparability limit: HEO delivery is not comparable to a staging-orbit service plus an exploratory transfer proxy. |
| Launch Cost Gbp Per Kg To Staging Orbit | external precedent | NASA_OTPS_SBSP_2024 · PDF p.10 | NASA's favourable combined case includes a low launch-price assumption. Numeric context: nominal $500/kg; $425/kg after a 15% quantity discount. Comparability limit: FY2022 USD US procurement and architecture boundaries differ; no direct input transfer is made. |
| Real Discount Rate | financing context | DESNZ_SBSP_2025 · Table 12 p.37; Table 26 pp.68-69 | Published SBSP cases use real pre-tax hurdle rates that decline with maturity and investor class. Numeric context: 20%/13.2%/9.06% scenario hurdles; investor cases 14.9% to 4.83%. Comparability limit: Hurdle rate is not identical to a project discount rate; 6.5% remains study-authored. |
| Real Discount Rate | source-inspired assumption | DESNZ_EGC_2025_ANNEX_A · Technical and Cost Assumptions, row 38 | A 6.5% hurdle-rate input appears for selected mature terrestrial generators. Numeric context: 6.5% for large solar and onshore wind. Comparability limit: This is not an observed SBSP rate and does not specify tax or financing structure. |
| Grid Connection Cost Gbp Per Kw Delivered | source-inspired assumption | DESNZ_SBSP_2025 · PDF p.70 | The small-scale study provides a direct grid-infrastructure allowance per MW. Numeric context: £0.15m/MW = £150/kW. Comparability limit: The model uses £100/kW as its own simplified allowance; scope and site conditions may differ. |
| Fixed Opex Pct Capex Per Year | source-inspired assumption | UK_SBSP_2021_ANNEX_B · Table B1, PDF p.4 | Annex B uses a triangular O&M factor derived from terrestrial generation technologies. Numeric context: triangular lower/mode/upper values of 0.8%/1.9%/4.7%. Comparability limit: Definitions and cost bases vary; the model's 1% of CAPEX per year remains a study assumption. |
| Reference Case Lcoe | external consistency check | DESNZ_SBSP_2025 · executive summary, PDF pp.3-4 | The project anchor lies inside one published early small-scale band. Numeric context: 2024 GBP: £335-595/MWh (2030), £154-249 (2035), £87-129 (2040). Comparability limit: This is not validation: scale, architecture, orbit, scenario year, financing and accounting boundaries differ. |
| Competitive Cost Claim | external comparison | UK_SBSP_2021_PHASE2 · Executive summary p.3; assumptions pp.18-19; Figure 5 p.22 and Table 4 p.23 | The earlier UK architecture study reports a much lower future case. Numeric context: £35-79/MWh (p10-p90), p50 about £50/MWh, 2018 prices; 2 GW; 30 years; 20% hurdle. Comparability limit: Architecture, learning, commissioning year, financing and price basis differ; values are not ranked as like-for-like forecasts. |
| Architecture Dependence | external comparison | NASA_OTPS_SBSP_2024 · executive summary pp.3-4; pp.7-10 | NASA's selected baseline and favourable-combination cases differ in lifecycle cost by roughly a factor of 20. Numeric context: FY2022 USD: $610/$1,590 per MWh baseline; $30/$80 per MWh favourable combination. Comparability limit: US architectures, service profiles, currency and lifecycle boundary differ; no NASA value is imported into this model. |
| Launch Cost Importance | scope qualification | DESNZ_SBSP_2025 · Table 14, PDF p.38 | The official small-scale study attributes most of its LCOE variance to launch assumptions. Numeric context: 55.5%/62.9%/64.0% for 2030/35/40. Comparability limit: This project may rank specific mass first within its own one-way ranges; neither ranking is universal. |
| System Value | system context | DESNZ_SBSP_2025 · executive summary, PDF pp.3-4 | The official system cases reduce each reported LCOE by the same system-benefit adjustment. Numeric context: adjusting for system benefits reduces LCOE by £21/MWh in all cases. Comparability limit: The present model does not monetize whole-system value; £21/MWh is not subtracted from project LCOE. |
| System Adjusted Comparison | benchmark definition | BEIS_EGC_2020 · Tables 7.1-7.3 | Enhanced LCOE illustrates that wider system impacts can alter technology comparisons. Numeric context: transcribed ranges stored in uk_system_adjusted_costs.csv. Comparability limit: 2018 real GBP and scenario-specific; indicative only and not directly harmonised with the model's 2024 real GBP basis. |

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

<!-- PAGEBREAK -->

## References

`ASSUMPTION_THIS_STUDY` is the project's internal assumption record, not an external publication. The bibliography below lists only external sources actually used in the evidence map, deduplicated by source ID.

- **DESNZ_EGC_2025_ANNEX_A** — Department for Energy Security and Net Zero (2026-01-14). [Annex A: Additional estimates and key assumptions 2025](https://assets.publishing.service.gov.uk/media/69d8efec96c86b7513170229/annex-a-additional-estimates-and-key-assumptions-2025.xlsx). Role in this report: UK generation benchmark input workbook. Accessed 2026-07-19.
- **BEIS_EGC_2020** — Department for Business, Energy and Industrial Strategy (2020-08-24). [BEIS Electricity Generation Costs (2020)](https://www.gov.uk/government/publications/beis-electricity-generation-costs-2020). Role in this report: System-adjusted benchmark source. Accessed 2026-07-19.
- **UK_SBSP_2021_PHASE2** — Frazer-Nash Consultancy for BEIS (2021-04-23). [Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility](https://www.fnc.co.uk/media/ae2eadpi/fnc-004456-51624r-phase-2-economic-feasibility-issue-1-1.pdf). Role in this report: External SBSP economic study. Accessed 2026-07-19.
- **UK_SBSP_2021_ANNEX_B** — Frazer-Nash Consultancy for BEIS (2021-04-23). [Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility – Annex B: Input Data Sources](https://www.fnc.co.uk/media/jfhdqus0/fnc-004456-51624r-phase-2-annex-b-input-data-sources.pdf). Role in this report: External SBSP input evidence. Accessed 2026-07-19.
- **DESNZ_SBSP_2025** — Frazer-Nash Consultancy; Space Solar Engineering Ltd; Imperial College London for DESNZ (2026-02-13). [Feasibility of Small-Scale Space Based Solar Power (SBSP) Systems for Early Market Adoption](https://assets.publishing.service.gov.uk/media/698f167c7da91680ad7f43ad/SBSP-enabled-pathways-to-net-zero-final-report-raf036-2425.pdf). Role in this report: External SBSP study. Accessed 2026-07-19.
- **NASA_OTPS_SBSP_2024** — NASA Office of Technology, Policy, and Strategy (2024-01-11). [Space Based Solar Power](https://ntrs.nasa.gov/citations/20230018600). Role in this report: External SBSP study. Accessed 2026-07-19.
- **CALTECH_SBSP_2022** — Caltech Space Solar Power Project (2022-06-16). [A Lightweight Space-based Solar Power Generation and Transmission Satellite](https://arxiv.org/abs/2206.08373). Role in this report: SBSP technical context. Accessed 2026-07-19.
