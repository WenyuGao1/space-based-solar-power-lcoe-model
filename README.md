<div align="center">

# UK Space-Based Solar Power Cost-Condition Assessment

### v2.0 · stage-resolved engineering boundaries · explicit discounted cash flow · bilingual explorer

[![Tests](https://github.com/WenyuGao1/uk-sbsp-cost-threshold-assessment/actions/workflows/tests.yml/badge.svg)](https://github.com/WenyuGao1/uk-sbsp-cost-threshold-assessment/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-2E8B57.svg)](LICENSE)
[![Interactive explorer](https://img.shields.io/badge/Interactive%20Explorer-Open-0F766E.svg)](https://wenyugao1.github.io/uk-sbsp-cost-threshold-assessment/)

[Open the interactive explorer](https://wenyugao1.github.io/uk-sbsp-cost-threshold-assessment/) · [English report](report/final_report_EN.md) · [中文报告](report/final_report_zh.md) · [Verification note](report/verification_note.md)

</div>

---

> **This repository is a transparent scenario and cost-threshold assessment. Its outputs are not commercial forecasts, quotations, official UK targets or proof that SBSP is economically viable.**

## What v2.0 answers

The project calculates a **conditional delivered-grid LCOE** for space-based solar power and shows how that result changes when technical, deployment, financing and operating assumptions move. It is designed to make the accounting boundary inspectable, not to predict a guaranteed deployment cost or date.

At the study-authored reference point:

| Metric | v2.0 reference result |
| --- | ---: |
| Conditional DCF LCOE | **£86.03/MWh** |
| Delivered capacity | **2.00 GW AC** |
| Computed end-to-end efficiency | **14.98%** |
| Orbital hardware mass | **10.00 million kg / 10,000 tonnes** |
| Equivalent launches | **118** at 85 t usable payload per flight |
| Initial CAPEX | **£12.84bn** |
| Discounted lifetime cost | **£13.10bn** |
| Discounted lifetime energy | **152.32 million MWh** |
| Price and valuation basis | **2024 real GBP; start of construction t=0** |

These numbers are an analytical anchor. Several inputs are exploratory, architecture-dependent and potentially correlated.

## Primary accounting correction

The DESNZ/Frazer-Nash small-scale SBSP report defines architecture specific power as power delivered to the ground per unit orbital mass. v2.0 therefore uses:

```text
system specific mass (kg/kW-delivered) = 1 / specific power (kW-delivered/kg)

orbital mass (kg)
  = delivered grid capacity (kW)
  × system specific mass (kg/kW-delivered)
```

The mass expression is **not divided by end-to-end efficiency again**.

For the requested regression:

```text
2,000,000 kW / 0.67 kW-delivered per kg
  = 2,985,075 kg
  ≈ 2,985 tonnes
```

The v1.x implementation could treat 1.5 kg/kW as delivered-power-normalised and still multiply it by delivered power divided by 20% efficiency. That produced 15,000 tonnes rather than the corrected 3,000 tonnes. Historical v1.x results and thresholds are therefore not directly comparable with v2.0.

## Stage-resolved energy chain

The independent whole-chain efficiency control has been removed. Five stage efficiencies are inputs and the total is their computed product:

```text
incident solar
  → space DC bus
  → emitted RF
  → RF incident on rectenna
  → rectenna DC output
  → grid-delivered AC
```

For a fixed delivered-grid output, the model works backwards through those stages. Hardware costs have exclusive rated-power boundaries:

| Cost input | Denominator |
| --- | --- |
| Space-generation hardware | W at the space DC bus; excludes RF transmitter hardware |
| RF transmitter hardware | W RF emitted; excludes generation and DC-bus hardware |
| Rectenna proxy | W AC delivered at the grid boundary |
| Grid connection | kW AC delivered at the grid boundary |

The rectenna value remains a bundled proxy. It does not explicitly model antenna area, frequency, beam geometry, sidelobes, power-density constraints, land, weather or safety.

## Launch and orbit boundary

Launch and orbit transfer are separate:

1. launch service to an architecture-dependent **LEO staging boundary**; and
2. incremental transfer to an architecture-dependent **high-Earth operational orbit**.

The explorer supports mutually exclusive per-kilogram and per-flight pricing. Both modes show payload utilisation and integer launch-count diagnostics. The transfer proxy must cover transfer vehicles, propellant, refuelling missions, operations and payload-performance penalties; a low staging-orbit price plus a small transfer allowance is not evidence of a low final-orbit delivery price.

## Explicit discounted-cash-flow LCOE

The headline metric is now:

```text
LCOE = Σ(Cₜ / (1+r)ᵗ) / Σ(Eₜ / (1+r)ᵗ)
```

The model supports construction duration and validated spend shares, operating life after commissioning, real discount rate, capacity factor, annual output degradation, fixed and variable O&M, separate space and ground replacement rates, decommissioning cost and residual value.

Programme contingency is applied once to initial construction CAPEX. Fixed O&M excludes contingency, initial launch, transfer and assembly from its eligible base. Space-hardware replacement includes proportional replacement hardware plus associated launch, transfer and assembly; ground replacement applies only to rectenna and grid assets. A simple CRF result remains only as a reconciliation metric.

![Reference DCF LCOE components](figures/reference_lcoe_components.png)

## Conditional sensitivity results

Within the selected exploration ranges, the strongest one-way reductions at the reference point are:

| One-way favourable bound | Conditional LCOE | Reduction |
| --- | ---: | ---: |
| System specific mass: 0.5 kg/kW-delivered | £31.28/MWh | £54.75/MWh |
| Launch to staging orbit: £20/kg | £49.53/MWh | £36.50/MWh |
| Real discount rate: 3% | £56.95/MWh | £29.08/MWh |
| In-orbit assembly: £0/kg | £70.82/MWh | £15.21/MWh |
| Space-generation hardware: £0.05/W-DC | £72.51/MWh | £13.52/MWh |

![Best one-way LCOE within each explored range](figures/one_way_lcoe_floors.png)

The equal-fraction combined frontier is retained only as a **mathematical interpolation device**. It is not a readiness score, probability, forecast, development schedule or engineering roadmap. Target-labelled web presets are called “illustrative combinations” and are shown only when movement from the reference case is actually required.

![Equal-fraction mathematical interpolation](figures/combined_progress_frontier.png)

## Evidence treatment

Every user-facing numerical input has:

- source type and source identifier;
- price year where relevant;
- explicit denominator or service boundary;
- an English and Simplified-Chinese limitation statement.

Study-authored values remain labelled as exploratory. Published manufacturer claims are not silently converted into verified engineering facts. The parameter metadata are in [data/sbsp_parameters.csv](data/sbsp_parameters.csv), supporting evidence is in [data/parameter_evidence.csv](data/parameter_evidence.csv), and the source registry is in [data/source_registry.csv](data/source_registry.csv).

## Reproduce the assessment

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analysis/run_full_analysis.py
.venv/bin/python -m unittest discover -s tests -v
```

The full runner regenerates model payloads, processed CSV files, English and Chinese reports, figures, PDFs and the verification note. The tests include Python/browser numerical parity.

## Repository guide

| Path | Purpose |
| --- | --- |
| [html/index.html](html/index.html) | Responsive bilingual interactive explorer |
| [html/model.js](html/model.js) | Browser implementation of the canonical calculation |
| [html/model_data.js](html/model_data.js) | Generated bilingual parameters and illustrative combinations |
| [src/model.py](src/model.py) | Canonical stage-resolved DCF model |
| [src/analysis.py](src/analysis.py) | Sensitivities, thresholds, contours and mathematical interpolation |
| [data/sbsp_parameters.csv](data/sbsp_parameters.csv) | Canonical input values, bounds and evidence metadata |
| [data/processed/reference_energy_chain.csv](data/processed/reference_energy_chain.csv) | Six stage powers for the reference case |
| [data/processed/reference_cash_flow.csv](data/processed/reference_cash_flow.csv) | Auditable reference DCF rows |
| [report/final_report_EN.md](report/final_report_EN.md) | Generated English technical report |
| [report/final_report_zh.md](report/final_report_zh.md) | Generated Chinese technical report |
| [tests/test_model_and_validation.py](tests/test_model_and_validation.py) | Numerical, parity and regeneration tests |

## Remaining limitations

- No complete satellite, rectenna or transfer-vehicle engineering design.
- No explicit beam geometry, land, safety, spectrum or environmental model.
- No discrete failure, spares, logistics or launch-manifest optimisation.
- No tax, inflation, financing tranches, learning curves or correlated uncertainty distributions.
- No GB dispatch, balancing, network reinforcement, capacity-value or market-revenue model.

For those reasons, even a low conditional LCOE is not a commercial forecast or a conclusion that the architecture is buildable, financeable or system-optimal.
