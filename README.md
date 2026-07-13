# UK Space-Based Solar Power Cost-Threshold Assessment

This repository is a reproducible techno-economic assessment of when space-based solar power (SBSP) could become comparable with UK electricity cost benchmarks.

Unlike a fixed-year deployment forecast, this project asks a threshold question: **what technical and financial conditions would be required for delivered-grid SBSP to reach 150, 120, 100, 80 or 60 GBP/MWh?** It treats launch cost, orbital mass, space hardware cost, in-orbit assembly cost, rectenna cost, financing cost, end-to-end efficiency, capacity factor, lifetime and OPEX as explicit model inputs.

[Read the English report](report/final_report_EN.md) · [English PDF](report/final_report_EN.pdf) · [阅读中文报告](report/final_report_zh.md) · [中文 PDF](report/final_report_zh.pdf)

![Combined SBSP cost-improvement frontier](figures/combined_progress_frontier.png)

## Headline Results

- The analytical reference point is 429 GBP/MWh. It is a sensitivity anchor, not a forecast or preferred design.
- Specific mass is the only single input that reaches the 150 GBP/MWh screening line within its explored one-way range.
- Reducing launch cost alone to 20 GBP/kg still leaves the model at about 204 GBP/MWh; increasing end-to-end efficiency alone to 35% leaves it at about 188 GBP/MWh.
- Reaching the 80-120 GBP/MWh decision range requires simultaneous progress in mass, efficiency, launch, assembly, orbital hardware and financing conditions.

## What This Adds

Existing SBSP studies commonly assess named architectures or future deployment scenarios. This repository complements that work with an architecture-parameterised, continuous threshold view:

- it reports the value at which individual inputs cross decision-relevant LCOE targets;
- it maps interacting parameters with two-dimensional cost contours;
- it calculates equal-fraction and alternative combined-improvement frontiers;
- it keeps assumptions, source metadata, processed results, reports and validation tests together in a public, executable workflow.

The results are **model-conditional thresholds**, not universal engineering requirements. The project does not claim greater forecasting accuracy than architecture-specific or whole-system studies.

## Repository Structure

- `data/`: structured assumptions, benchmark data, source registry, raw official workbooks and processed model outputs.
- `src/`: model, parameter loading, sensitivity analysis, plotting, reporting, PDF generation and validation modules.
- `analysis/run_full_analysis.py`: end-to-end runner for processed data, English figures, Chinese figures and both final reports.
- `figures/`: English-labelled final figures.
- `figures_zh/`: Chinese-labelled final figures.
- `report/`: current English and Chinese reports and verification note.
- `tmp/`: local scratch space for plotting and PDF rendering.

## Reproduce the Analysis

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the full pipeline:

```bash
python3 analysis/run_full_analysis.py
```

Run the numerical and evidence checks:

```bash
python3 -m unittest discover -s tests -v
```

The runner regenerates:

- `data/processed/reference_lcoe.csv`
- `data/processed/sensitivity_curves.csv`
- `data/processed/thresholds_one_way.csv`
- `data/processed/one_way_feasibility_matrix.csv`
- `data/processed/cost_driver_importance.csv`
- `data/processed/contour_grids.csv`
- `data/processed/launch_efficiency_frontier.csv`
- `data/processed/combined_improvement_frontier.csv`
- `data/processed/alternative_combined_pathways.csv`
- all English figures in `figures/`
- all Chinese figures in `figures_zh/`
- `report/final_report_EN.md`
- `report/final_report_EN.pdf`
- `report/final_report_zh.md`
- `report/final_report_zh.pdf`
- `report/verification_note.md`

The main reports are decision-focused: the core sections use compact tables and charts cropped around the 80-150 GBP/MWh decision range. Full-range sensitivity diagnostics remain in the appendices and figure folders for traceability.

GitHub Actions runs both the test suite and complete generation pipeline on every push and pull request and validates that all expected outputs are created.

## Model Boundary

The delivered-grid SBSP model includes:

- space segment CAPEX;
- launch cost;
- orbit transfer cost;
- in-orbit assembly and deployment;
- wireless power transmission hardware;
- rectenna CAPEX;
- grid connection;
- programme margin and contingency;
- replacement and refurbishment allowance;
- fixed OPEX;
- variable OPEX;
- capacity factor and availability;
- end-to-end efficiency;
- system lifetime;
- WACC;
- annual delivered electricity.

The main output unit is GBP/MWh delivered to the grid.

## UK Benchmark Treatment

The repository separates:

- generation-only UK electricity cost benchmarks in `data/uk_generation_costs.csv`;
- system-adjusted renewable cost benchmarks in `data/uk_system_adjusted_costs.csv`.

Generation-only LCOE measures generator-boundary cost. It excludes grid reinforcement, balancing, curtailment, backup capacity, storage, long-duration flexibility and other reliability costs.

System-adjusted costs are broader comparators. They are not direct market prices and should not be read as precise forecasts. They are used to understand when SBSP might become relevant against the additional cost of maintaining reliability in high-renewable power systems.

## Key Limitations

Commercial-scale SBSP has not been deployed, so many architecture parameters are exploratory threshold assumptions. The reference point is an analytical anchor for sensitivity curves, not a final design recommendation.

The model identifies cost-parity conditions. It does not prove engineering feasibility, commercial readiness or full GB power-system value. Those require separate engineering demonstration, financeability assessment and whole-system modelling.

## Data, Sources and Licensing

Every external source is listed in [`data/source_registry.csv`](data/source_registry.csv), and the data layout is explained in [`data/README.md`](data/README.md). Third-party workbooks retain their original terms; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Original code and project-authored documentation are released under the [MIT License](LICENSE).
