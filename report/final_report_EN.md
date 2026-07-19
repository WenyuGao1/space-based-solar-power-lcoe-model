# UK Space-Based Solar Power Cost-Condition Map

Report subtitle: A reproducible threshold assessment for UK decision screening — not a deployment forecast

Evidence status: source registry reviewed to 2026-07-19; selected official DESNZ benchmark cells are machine-reconciled.

Version: v1.2

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

The short answer is: **the reference configuration is expensive, but the project is useful because it reveals the conditions behind that result.** At the study-authored reference point, grid-connection-point LCOE is **£429/MWh**. This is a normalization anchor, not a forecast or preferred design.

Table 1. Study-defined cost lines and their meaning

| Cost line | Use in this project | Decision meaning and limitation |
| --- | --- | --- |
| £150/MWh | Broad study-defined screening line | A model diagnostic, not an official UK threshold |
| £100–120/MWh | Study-defined screen for a potential firm or near-firm role | Triggers deeper engineering, finance and system-value work |
| £80/MWh | Overlap with the selected system-adjusted comparator | Still not a market-competitiveness conclusion |
| £60/MWh | Stringent stress test | No tested one-way input reaches it; coupled cases remain exploratory |

The strongest one-way result is specific mass, **within this model boundary and the selected ranges, with every other input held at its reference value**. The limiting values are 1.28, 0.88 and 0.62 kg/kW-space for £150, £120 and £100/MWh respectively. No one-way specific-mass value in the explored range reaches £80 or £60/MWh.

Launch cost alone is not sufficient: even at the favourable explored bound of £20/kg, LCOE remains about £204/MWh. Raising end-to-end efficiency alone to 35% leaves about £188/MWh. The model therefore points to testing multiple coupled combinations across mass, launch, space hardware, assembly, finance, efficiency and delivered energy; it does not prove that every variable must move.

The contribution is **not greater forecasting accuracy**. It is a transparent and reproducible answer to a narrower question: *what cost and performance conditions would have to hold, inside a stated model, before SBSP enters selected UK decision regions?*

## 2. Research question and distinctive contribution

The representative SBSP studies reviewed here evaluate named architectures, future deployment cases, lifecycle impacts or system pathways. This project complements them with continuous one-way and coupled parameter frontiers. It therefore makes assumptions, conditional thresholds and failure-to-reach results directly auditable.

Table 2. Relationship to selected existing SBSP studies

| Study | Primary analysis | Reported context | Relationship to this project |
| --- | --- | --- | --- |
| UK SBSP Phase 2 economic study (2021) | architecture and future scenario study | £35-79/MWh (p10-p90) with p50 about £50/MWh in 2018 prices; 2 GW CASSIOPeiA; 30-year life; 20% hurdle; 2040 commissioning case | Provides architecture and scenario context; this project instead exposes continuous model-conditional cost thresholds. |
| UK small-scale SBSP study (completed 2025; published 2026) | architecture, pathways and system-value study | 2024 GBP: £335-595/MWh (2030), £154-249/MWh (2035), £87-129/MWh (2040) | Provides a current external consistency check and architecture-specific drivers; this project adds an auditable parameter-space map. |
| NASA OTPS assessment (2024) | lifecycle cost and emissions assessment | FY2022 USD: $610/$1,590 per MWh baseline for RD1/RD2; $30/$80 per MWh under combined favourable assumptions | Shows a roughly 20-fold lifecycle-cost difference between NASA's selected baseline and favourable-combination cases; no NASA value is imported into this model. |
| This project (v1.2) | reproducible continuous cost-condition assessment | £429/MWh study-authored reference anchor; root-solved conditional lines at £150/120/100/80/60 per MWh | Distinctive contribution: traceable inputs, continuous one-way and coupled frontiers, bilingual outputs and executable tests. |

The project's publishable advantage is specific:

- Every exact model input is classified as a **study-authored exploratory assumption**; literature values are kept in a separate evidence map.
- Thresholds are solved by high-precision monotonic bisection rather than read from a coarse plotting grid.
- The analysis reports both attainable and unattainable one-way targets across 16 variables and 5 study-defined cost lines.
- Coupled frontiers and 3 alternative parameter slices show that the answer is not a single-variable launch-cost story.
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

The £429/MWh reference anchor lies inside the 2026-published official small-scale study's reported £335–595/MWh 2030 band. This is a useful consistency observation, **not validation**, because scale, architecture, orbit, scenario year, financing and cost boundaries differ.

## 5. Reference anchor and cost structure

Table 3. Core reference inputs

| Parameter | Reference value | Role in the model |
| --- | --- | --- |
| Delivered grid capacity | 2,000 MW | Scale anchor; most unit costs scale with capacity |
| End-to-end efficiency | 15.0% | Sets required space-side power and therefore mass |
| Delivered capacity factor (model proxy) | 90.0% | Delivered-energy proxy combining availability and constraints |
| Specific mass | 5.00 kg/kW-space | Scales launch, transfer and assembly together |
| Launch cost | £500/kg to staging orbit | Transport-cost lever to the model-defined staging orbit |
| Space hardware cost | £0.40/W-space | Orbital manufacturing-cost lever |
| In-orbit assembly and deployment cost | £200/kg | Mass-scaled deployment allowance |
| Real project discount-rate proxy | 6.5% | Real project discount-rate proxy used in capital recovery |
| System lifetime | 30 years | Period over which capital is recovered |

The 2.0 GW delivered-capacity anchor requires 13.33 GW of space-side power and **66.67 million kg** of orbital hardware, or about 66,667 tonnes. Both units are shown to make the mass scale unambiguous.

Table 4. Reference initial CAPEX reconciliation

| Component | Cost |
| --- | --- |
| Launch | £33.33bn |
| In-orbit assembly and deployment | £13.33bn |
| Orbit transfer | £6.67bn |
| Space-segment hardware | £5.33bn |
| Wireless-power hardware | £1.33bn |
| Rectenna | £0.30bn |
| Grid connection | £0.20bn |
| Pre-margin subtotal | £60.50bn |
| Programme margin | £12.10bn |
| Initial CAPEX | £72.60bn |

![Figure 1. Reference LCOE components](../figures/reference_lcoe_components.png)

**Interpretation.** Annualised CAPEX contributes about 82% of annual reference cost. The result is therefore especially sensitive to physical scale and capital recovery.

The reference point produces 15.768 million MWh/year, £72.6bn initial CAPEX and £6.77bn annualised total cost. These figures reconcile exactly in the generated model outputs.

<!-- PAGEBREAK -->

## 6. UK comparator landscape

![Figure 2. UK electricity cost comparators](../figures/uk_electricity_cost_benchmark_comparison.png)

**Interpretation.** The figure shows the generation-only rows flagged for the headline band, plus the Hinkley contract marker and the historical system-adjusted band. The plotted generation rows span about £55–£153/MWh; excluding the floating-offshore FOAK row gives £55–£113/MWh.

Table 5. Comparator definitions from the structured data

| Comparator | Reported value | Price basis | Metric type |
| --- | --- | --- | --- |
| Large-scale solar | £55–60/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Onshore wind | £57–58/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Fixed offshore wind | £98–103/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Floating offshore wind | £125–153/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Gas CCGT high load factor | £111–113/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Gas with CCUS high load factor | £104–105/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Gas with CCUS mid load factor | £181/MWh | 2024 real GBP | DESNZ 2025 Annex A 2030-2035 range |
| Nuclear Hinkley Point C public contract marker | £92.5/MWh | 2012 real-price terms (CPI-indexed) | 35-year Contract for Difference strike-price marker |
| High-renewable system-adjusted band | £45–87/MWh | 2018 real GBP | Indicative enhanced-LCOE envelope |

The Hinkley Point C £92.50/MWh marker is a 35-year CfD strike price stated in 2012 prices and CPI-indexed; it is not a generic nuclear LCOE. The BEIS enhanced-LCOE range of £45–£87/MWh is in 2018 real GBP, whereas the DESNZ generation rows are in 2024 real GBP. No false-precision price conversion is applied.

Figure 2 uses the six generation-only rows marked for the headline band. Table 5 additionally retains the £181/MWh mid-load-factor gas-CCUS sensitivity, but it is excluded from the figure and headline band to avoid counting two utilisation cases for the same technology as separate headline comparators.

Consequently, overlap with a chart band is a screening result only. Wholesale prices, contract prices, generator LCOE and system-adjusted costs are different metrics.

## 7. One-way conditional thresholds

![Figure 3. Best LCOE attainable one variable at a time](../figures/one_way_lcoe_floors.png)

**Interpretation.** Within the selected one-way ranges, only whole-architecture specific mass crosses the £150/MWh study line. This ranking is range-dependent and is not universal across architectures.

![Figure 4. Specific-mass thresholds in the decision window](../figures/specific_mass_threshold_focus.png)

**Interpretation.** With all other reference inputs fixed, the model requires at most 1.28, 0.88 and 0.62 kg/kW-space for £150, £120 and £100/MWh. These are conditional mathematical requirements, not proven engineering targets.

Table 6. Complete one-way threshold audit

| Input | Unit | £150 | £120 | £100 | £80 | £60 |
| --- | --- | --- | --- | --- | --- | --- |
| Launch cost | GBP/kg to staging orbit | — | — | — | — | — |
| Specific mass | kg/kW-space | 1.28 | 0.88 | 0.62 | — | — |
| Space hardware cost | GBP/W-space | — | — | — | — | — |
| Wireless power transmission cost | GBP/W-space | — | — | — | — | — |
| End-to-end efficiency | fraction | — | — | — | — | — |
| Real project discount-rate proxy | fraction | — | — | — | — | — |
| Rectenna CAPEX | GBP/W-delivered | — | — | — | — | — |
| Grid connection cost | GBP/kW-delivered | — | — | — | — | — |
| System lifetime | years | — | — | — | — | — |
| Delivered capacity factor (model proxy) | fraction | — | — | — | — | — |
| In-orbit assembly and deployment cost | GBP/kg | — | — | — | — | — |
| Orbit transfer cost | GBP/kg | — | — | — | — | — |
| Programme margin / contingency | fraction | — | — | — | — | — |
| Replacement and refurbishment allowance | fraction/year | — | — | — | — | — |
| Fixed OPEX | fraction/year | — | — | — | — | — |
| Variable OPEX | GBP/MWh | — | — | — | — | — |

An em dash means that no value reaches the target inside the tested one-way bound; it does not mean physical impossibility outside that bound.

The result does not mean that specific mass is the only necessary condition. It means only that, under the reference assumptions and selected one-way bounds, it is the sole individual variable able to cross £150/MWh. In a coupled design, low mass is not sufficient for every target, and other architectures may rank drivers differently. The official small-scale study published in 2026, for example, attributes 55.5–64.0% of its own LCOE variance to launch assumptions.

## 8. Coupled cost-condition frontiers

![Figure 5. Launch-cost and efficiency frontier](../figures/sbsp_break_even_thresholds.png)

**Interpretation.** Higher efficiency relaxes the launch-cost condition, but many cells remain unattainable when the remaining reference inputs are fixed. Values are root-solved inside the recorded launch-cost bounds.

Table 7. Selected launch-cost limits with all other inputs fixed

| End-to-end efficiency | Target | Maximum launch cost |
| --- | --- | --- |
| 25% | £150/MWh | £109.1/kg or lower |
| 25% | £120/MWh | not reached |
| 25% | £100/MWh | not reached |
| 30% | £150/MWh | £210.9/kg or lower |
| 30% | £120/MWh | £83.2/kg or lower |
| 30% | £100/MWh | not reached |
| 35% | £150/MWh | £312.8/kg or lower |
| 35% | £120/MWh | £163.7/kg or lower |
| 35% | £100/MWh | £64.4/kg or lower |

![Figure 6. Equal-fraction coupled frontier](../figures/combined_progress_frontier.png)

**Interpretation.** Lower target LCOEs on the x-axis correspond to larger normalized movements on the y-axis. The y-axis is a mathematical interpolation index, not an implementation timeline.

Table 8. Coupled equal-fraction index and selected parameter values

| Target | Normalized movement | Launch | Specific mass | Efficiency | Real discount proxy |
| --- | --- | --- | --- | --- | --- |
| £150/MWh | 26.5% | £373/kg | 3.81 kg/kW-space | 20.3% | 5.57% |
| £120/MWh | 31.8% | £347/kg | 3.57 kg/kW-space | 21.4% | 5.39% |
| £100/MWh | 36.1% | £327/kg | 3.38 kg/kW-space | 22.2% | 5.24% |
| £80/MWh | 41.1% | £303/kg | 3.15 kg/kW-space | 23.2% | 5.06% |
| £60/MWh | 47.4% | £272/kg | 2.87 kg/kW-space | 24.5% | 4.84% |

![Figure 7. Launch cost × efficiency decision contour](../figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png)

**Interpretation.** The two-variable contour makes interaction visible, but it still fixes every unplotted input at the reference point. It must not be read as a complete design feasibility map.

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

At the study-authored reference point, SBSP LCOE is approximately £429/MWh at the grid connection point. Lower launch cost by itself does not close the gap. Within the selected one-way ranges, a very low whole-architecture specific mass is the only individual lever that reaches £150/MWh, and it still cannot reach £80/MWh alone.

The central conclusion is therefore narrower and conditional: **lower launch cost or higher efficiency alone is insufficient at the tested bounds; no single tested one-way change reaches £80 or £60/MWh, so some coupled improvement is required for those lines.** The analysis does not prove that every listed variable must improve, or that its equal-fraction path is unique. It also does not prove that any engineering or commercial combination can be achieved.

The project's value is the clarity of that conditional statement and the audit trail behind it.

<!-- PAGEBREAK -->

## Appendix A. Evidence-to-claim map

Table A1. Contextual evidence and its limitations

| Parameter or claim | Evidence role / source | Locator | Published context | Applicability limit |
| --- | --- | --- | --- | --- |
| delivered_capacity_mw | external precedent / UK_SBSP_2021_PHASE2 | PDF pp.18-19 | 2 GW CASSIOPeiA case | The same number is used here as a study scale anchor, not as evidence that this architecture is preferred. |
| system_lifetime_years | external precedent / UK_SBSP_2021_PHASE2 | PDF pp.18-19 | 30 years; the later small-scale study uses 15 years | Lifetime remains architecture-dependent and the model does not demonstrate survivability or refurbishment feasibility. |
| end_to_end_efficiency | technical context / CALTECH_SBSP_2022 | abstract | 7-14% end-to-end efficiency | Concept and subsystem boundaries differ; this does not directly set the model's 15% reference value. |
| end_to_end_efficiency | source-inspired assumption / UK_SBSP_2021_ANNEX_B | PDF p.4 | approximately 14.85-24.39% from independent factor products | The 15% reference is still a project assumption; multiplying independent extrema is not a probability distribution or validated integrated design. |
| end_to_end_efficiency | external consistency check / DESNZ_SBSP_2025 | Table 1, PDF pp.11-12; reference-design selection p.13 | 11.7-19.9%; selected Space Solar small-scale reference design 14.9% | The report states that major values are manufacturer-claimed, not independently verified; missing values are inferred and definitions may differ. |
| capacity_factor | scope qualification / DESNZ_SBSP_2025 | Table 3, PDF p.16 | HEO: UK rectenna 95.7%, satellite average 53.9%; circular LEO: satellite average 20.1%, UK rectenna 21.5% | Rectenna utilization is not equivalent to this model's delivered capacity factor; the 90% value remains a study assumption. |
| specific_mass_kg_per_kw_space_power | technical context / CALTECH_SBSP_2022 | abstract | 160 g/m2 areal density | Areal density cannot be converted to whole-system kg/kW-space without power density and complete subsystem boundaries. |
| specific_mass_kg_per_kw_space_power | external consistency check / DESNZ_SBSP_2025 | Table 1, PDF pp.11-12; reference-design selection p.13 | 0.15-0.67 kW/kg; selected Space Solar small-scale reference design 0.58 kW/kg | Values are architecture-specific and partly manufacturer-claimed; inverse conversion is not imported as the model's whole-system specific mass. |
| launch_cost_gbp_per_kg | external range / UK_SBSP_2021_ANNEX_B | PDF p.5 and p.11 | £358-2,410/kg | Orbit, procurement, price year and service boundary differ from the model-defined staging-orbit variable. |
| launch_cost_gbp_per_kg | external comparison / DESNZ_SBSP_2025 | Table 12 p.37; Tables 27-28 pp.71-73 | central HEO £1,647/1,400/1,153 per kg; optimistic £1,188/1,008/827 for 2030/35/40 | Destination orbit, scenario year, vehicle, procurement and service boundary differ; although both are stated in 2024 GBP, the model's £500/kg reference is not taken from this table. |
| launch_cost_gbp_per_kg | external precedent / NASA_OTPS_SBSP_2024 | PDF p.10 | nominal $500/kg; $425/kg after a 15% quantity discount | FY2022 USD, US procurement and architecture boundaries differ; no currency conversion or direct input transfer is made. |
| wacc | financing context / DESNZ_SBSP_2025 | Table 12 p.37; Table 26 pp.68-69 | 20%/13.2%/9.06% scenario hurdles; 14.9%, 9.8%, 6.75%, 4.83% investor-class cases | Hurdle rate is not identical to WACC; this model's 6.5% real discount proxy remains study-authored. |
| wacc | source-inspired assumption / DESNZ_EGC_2025_ANNEX_A | Technical and Cost Assumptions, row 38 | 6.5% for large solar and onshore wind | This is not an observed SBSP WACC and does not specify this model's tax or financing structure. |
| grid_connection_cost_gbp_per_kw_delivered | source-inspired assumption / DESNZ_SBSP_2025 | PDF p.70 | £0.15m/MW = £150/kW | The model uses £100/kW as its own simplified allowance; scope and site conditions may differ. |
| fixed_opex_pct_capex_per_year | source-inspired assumption / UK_SBSP_2021_ANNEX_B | Table B1, PDF p.4 | triangular lower/mode/upper values of 0.8%/1.9%/4.7% | Definitions and cost bases vary; the model's 1% of CAPEX per year remains a study assumption. |
| reference_case_lcoe | external consistency check / DESNZ_SBSP_2025 | executive summary, PDF pp.3-4 | 2024 GBP: £335-595/MWh (2030), £154-249 (2035), £87-129 (2040) | This is not validation: scale, architecture, orbit, scenario year, financing and accounting boundaries differ. |
| competitive_cost_claim | external comparison / UK_SBSP_2021_PHASE2 | Executive summary p.3; assumptions pp.18-19; Figure 5 p.22 and Table 4 p.23 | £35-79/MWh (p10-p90), p50 about £50/MWh, 2018 prices; 2 GW; 30 years; 20% hurdle | Architecture, learning, commissioning year, financing and price basis differ; values are not ranked as like-for-like forecasts. |
| architecture_dependence | external comparison / NASA_OTPS_SBSP_2024 | executive summary pp.3-4; pp.7-10 | FY2022 USD: $610/$1,590 per MWh baseline; $30/$80 per MWh favourable combination | US architectures, service profiles, currency and lifecycle boundary differ; no NASA value is imported into this model. |
| launch_cost_importance | scope qualification / DESNZ_SBSP_2025 | Table 14, PDF p.38 | 55.5%/62.9%/64.0% for 2030/35/40 | This project may rank specific mass first within its own one-way ranges; neither ranking is universal. |
| system_value | system context / DESNZ_SBSP_2025 | executive summary, PDF pp.3-4 | adjusting for system benefits reduces LCOE by £21/MWh in all cases | The present model does not monetize whole-system value; £21/MWh is not subtracted from project LCOE. |
| system_adjusted_comparison | benchmark definition / BEIS_EGC_2020 | Tables 7.1-7.3 | transcribed ranges stored in uk_system_adjusted_costs.csv | 2018 real GBP and scenario-specific; indicative only and not directly harmonised with the model's 2024 real GBP basis. |

## Appendix B. Source registry

Table B1. Sources used by the project

| Source ID | Reference | Organisation | Role |
| --- | --- | --- | --- |
| DESNZ_EGC_2025 | [Electricity generation costs 2025](https://www.gov.uk/government/publications/electricity-generation-costs-2025) | Department for Energy Security and Net Zero | UK generation benchmark source |
| DESNZ_EGC_2025_ANNEX_A | [Annex A: Additional estimates and key assumptions 2025](https://assets.publishing.service.gov.uk/media/69d8efec96c86b7513170229/annex-a-additional-estimates-and-key-assumptions-2025.xlsx) | Department for Energy Security and Net Zero | UK generation benchmark input workbook |
| DESNZ_EGC_2023 | [Electricity generation costs 2023](https://www.gov.uk/government/publications/electricity-generation-costs-2023) | Department for Energy Security and Net Zero | Supplementary UK benchmark source |
| BEIS_EGC_2020 | [BEIS Electricity Generation Costs (2020)](https://www.gov.uk/government/publications/beis-electricity-generation-costs-2020) | Department for Business, Energy and Industrial Strategy | System-adjusted benchmark source |
| OFGEM_WHOLESALE | [Wholesale market indicators](https://www.ofgem.gov.uk/energy-data-and-research/data-portal/wholesale-market-indicators) | Ofgem | Market context |
| NESO_BALANCING_2025 | [2025 Annual Balancing Costs Report](https://www.neso.energy/document/362561/download) | National Energy System Operator | System-cost evidence |
| NESO_NETWORK_UPDATE_2026 | [Beyond 2030 - Electricity Transmission Update](https://www.neso.energy/publications/beyond-2030) | National Energy System Operator | System-cost evidence |
| NESO_CP2030 | [Advice on achieving clean power by 2030](https://www.neso.energy/document/346651/download) | National Energy System Operator | System-cost evidence |
| NESO_OPERABILITY_2026 | [Operability Strategy Report and Electricity Markets Roadmap](https://www.neso.energy/publications/operability-strategy-report-and-electricity-markets-roadmap) | National Energy System Operator | System-cost evidence |
| UKSA_SBSP_2020 | [UK government commissions space solar power stations research](https://www.gov.uk/government/news/uk-government-commissions-space-solar-power-stations-research) | UK Space Agency and BEIS | Historical SBSP context |
| UK_SBSP_2021 | [Space based solar power: de-risking the pathway to net zero](https://www.gov.uk/government/publications/space-based-solar-power-de-risking-the-pathway-to-net-zero) | Department for Business, Energy and Industrial Strategy | External SBSP study landing page |
| UK_SBSP_2021_PHASE2 | [Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility](https://www.fnc.co.uk/media/ae2eadpi/fnc-004456-51624r-phase-2-economic-feasibility-issue-1-1.pdf) | Frazer-Nash Consultancy for BEIS | External SBSP economic study |
| UK_SBSP_2021_ANNEX_B | [Space Based Solar Power as a Contributor to Net Zero — Phase 2: Economic Feasibility – Annex B: Input Data Sources](https://www.fnc.co.uk/media/jfhdqus0/fnc-004456-51624r-phase-2-annex-b-input-data-sources.pdf) | Frazer-Nash Consultancy for BEIS | External SBSP input evidence |
| DESNZ_SBSP_2025 | [Feasibility of Small-Scale Space Based Solar Power (SBSP) Systems for Early Market Adoption](https://assets.publishing.service.gov.uk/media/698f167c7da91680ad7f43ad/SBSP-enabled-pathways-to-net-zero-final-report-raf036-2425.pdf) | Frazer-Nash Consultancy; Space Solar Engineering Ltd; Imperial College London for DESNZ | External SBSP study |
| NASA_OTPS_SBSP_2024 | [Space Based Solar Power](https://ntrs.nasa.gov/citations/20230018600) | NASA Office of Technology, Policy, and Strategy | External SBSP study |
| CALTECH_SBSP_2022 | [A Lightweight Space-based Solar Power Generation and Transmission Satellite](https://arxiv.org/abs/2206.08373) | Caltech Space Solar Power Project | SBSP technical context |
| CALTECH_WPT_2024 | [Wireless Power Transfer in Space using Flexible, Lightweight, Coherent Arrays](https://arxiv.org/abs/2401.15267) | Caltech Space Solar Power Project | SBSP technical context |
| NAO_HPC_2017 | [Hinkley Point C](https://www.nao.org.uk/reports/hinkley-point-c/) | National Audit Office | Nuclear benchmark context |
| ASSUMPTION_THIS_STUDY | [Exploratory SBSP cost-condition model assumptions](../report/final_report_EN.md) | This project | Model assumption source |

## Appendix C. Assumptions and boundary register

Table C1. Explicit analytical assumptions

| ID | Area | Assumption | Limitation |
| --- | --- | --- | --- |
| A1 | Analytical framing | This is a cost-threshold assessment. No SBSP result is expressed as a deployment-year forecast. | Official UK benchmarks may contain source publication years or commissioning references, but they are not used as SBSP scenarios. |
| A2 | Unit and price convention | All model financial inputs and outputs are interpreted in 2024 real GBP and LCOE is reported in GBP/MWh at the grid connection point. | Some external benchmarks use different real-price bases; these are labelled rather than silently harmonised. |
| A3 | Efficiency boundary | End-to-end efficiency is applied by increasing required space-side power capacity for a fixed delivered-grid capacity. | This simplifies subsystem losses into one continuous variable. |
| A4 | Mass boundary | Specific mass is applied per kW of required space-side power capacity. | Architecture-specific mass allocation between arrays, structures and transmitters is not modelled. |
| A5 | Contingency | Programme margin is applied to all pre-margin CAPEX categories. | The model does not separately estimate owner costs, insurance during construction or first-of-a-kind programme development. |
| A6 | Refurbishment | Replacement and refurbishment are modelled as an annual allowance based on initial CAPEX. | Periodic major replacement timing is not explicitly optimised. |
| A7 | System costs | Renewable system-adjusted benchmarks use BEIS enhanced LCOE ranges from 2020 because the latest DESNZ 2025 LCOE report says wider system costs require full system modelling. | Values are in 2018 real GBP and should be treated as indicative ranges. |
| A8 | Nuclear | Nuclear is represented only by a public contract-price marker because recent DESNZ reports do not publish an updated generic nuclear LCOE. | Not directly comparable with 2024 real generation LCOE. |
| A9 | Conditional thresholds | A threshold is necessary only within this model, its accounting boundary and the stated parameter ranges; it is not a universal engineering requirement. | Alternative architectures, coupled parameter changes or omitted system value can move the threshold. |
| A10 | External comparisons | Published SBSP cost estimates are used as context and consistency checks, not as validation or direct substitutes for this model's inputs. | Architectures, orbit destinations, price years, financing and cost boundaries differ materially across studies. |
| A11 | Discount rate | The parameter named wacc is implemented as a real project discount-rate proxy in the capital-recovery factor; taxes, inflation and financing tranches are not modelled. | It should not be read as a fully specified observed pre-tax or post-tax corporate WACC. |
| A12 | Delivered-energy boundary | The model ends at the grid connection point and uses a delivered capacity-factor proxy that combines availability, outages and operating constraints. | Downstream transmission reinforcement, balancing, storage, reliability services, curtailment and monetised system value are excluded. |

Machine-readable inputs and all complete sensitivity curves are retained under `data/`; the full English figure set is under `figures/`; exact generated thresholds are under `data/processed/`.
