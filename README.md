<div align="center">

# UK Space-Based Solar Power Cost-Condition Map

### A reproducible, bilingual map of the model conditions under which SBSP enters study-defined UK cost regions

[![Tests](https://github.com/WenyuGao1/uk-sbsp-cost-threshold-assessment/actions/workflows/tests.yml/badge.svg)](https://github.com/WenyuGao1/uk-sbsp-cost-threshold-assessment/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-2E8B57.svg)](LICENSE)
[![Reproducible](https://img.shields.io/badge/Analysis-Reproducible-6f42c1.svg)](analysis/run_full_analysis.py)
[![Reports](https://img.shields.io/badge/Reports-English%20%7C%20中文-0A66C2.svg)](report/)
[![Interactive explorer](https://img.shields.io/badge/Interactive%20Explorer-Open%20Tool-0F766E.svg)](https://wenyugao1.github.io/uk-sbsp-cost-threshold-assessment/)

[Open interactive explorer](https://wenyugao1.github.io/uk-sbsp-cost-threshold-assessment/) · [English report](report/final_report_EN.md) · [English PDF](report/final_report_EN.pdf) · [中文报告](report/final_report_zh.md) · [中文 PDF](report/final_report_zh.pdf) · [Verification note](report/verification_note.md)

</div>

---

## Interactive Cost Explorer

> **[Launch the bilingual interactive SBSP cost explorer →](https://wenyugao1.github.io/uk-sbsp-cost-threshold-assessment/)**

Adjust technical, deployment, financing and operating assumptions to see how delivered-grid LCOE, annualised cost composition, initial CAPEX allocation and study-defined cost thresholds change in real time. The explorer is an interactive companion to the reports: it exposes the model assumptions but does not turn them into a deployment forecast or investment recommendation.

[View the standalone HTML source](html/index.html) · [Read the English methodology](report/final_report_EN.md) · [阅读中文报告](report/final_report_zh.md)

---

This project asks a deliberately different question from a fixed-year deployment forecast:

> **Within a stated grid-connection-point model, what technical and financial conditions would be required for space-based solar power (SBSP) to reach the study-defined lines of 150, 120, 100, 80 or 60 GBP/MWh?**

The model treats launch cost, specific mass, orbital hardware, in-orbit assembly, wireless transmission, rectenna cost, financing, end-to-end efficiency, availability, lifetime and OPEX as explicit inputs. It then calculates one-way thresholds, interacting-parameter contours and combined-improvement frontiers.

![Combined SBSP cost-improvement frontier](figures/combined_progress_frontier.png)

## At a Glance

| Item | Result |
| --- | --- |
| Analytical reference point | **429 GBP/MWh** delivered-grid LCOE |
| Study-defined decision region | **80-120 GBP/MWh** |
| Study-defined broad screening line | **150 GBP/MWh** |
| Strongest one-way lever within selected ranges | **Whole-architecture specific mass** |
| Main finding | Lower launch cost alone is insufficient; only specific mass crosses the 150-100 GBP/MWh lines one-way, while the 80-60 GBP/MWh lines need some coupled improvement within the tested ranges |
| Project format | Interactive bilingual explorer, open model, structured assumptions, processed outputs, English/Chinese charts and reports, automated tests |

The 429 GBP/MWh reference point is an analytical anchor for sensitivity analysis. It is **not** a forecast, preferred architecture, investment case or claim about a future deployment year.

## What Is Distinctive About This Assessment?

The contribution is not that previous SBSP studies lack cost or sensitivity analysis. Several major studies already examine architecture costs, uncertainty and power-system value. This repository adds a complementary **continuous, model-conditional threshold view**.

| Dimension | Typical architecture/scenario study | This repository |
| --- | --- | --- |
| Primary question | What might a named design cost in a future deployment scenario? | What parameter conditions are required to cross a defined cost target? |
| Architecture treatment | Usually tied to one or more specified system designs | Parameterised model that exposes architecture-driving variables directly |
| Time treatment | Often organised around 2030, 2040 or 2050 cases | No fixed-year cost forecast |
| Main output | Scenario LCOE, uncertainty, roadmap or system value | Root-solved one-way thresholds, LCOE floors, 2D contours and combined-improvement frontiers |
| Auditability | Method and selected assumptions published in a report | Code, assumptions, sources, processed results, charts, reports and tests in one executable repository |
| Communication | Usually one report language | Aligned English and Chinese reports and figures |

This makes the project especially useful for:

- identifying which assumptions actually control the result;
- testing alternative launch, mass, efficiency or financing assumptions;
- separating a cost-screening result from engineering feasibility and market readiness;
- showing why an apparently attractive improvement in one input may fail at whole-system level;
- providing a transparent starting point for a later architecture-specific or GB power-system study.

It does **not** claim greater forecasting accuracy, universal necessary conditions or priority over detailed engineering and whole-system studies. Its advantage is transparency, reproducibility and numerical resolution around the threshold question.

## Key Results

### 1. The reference case is dominated by capital-intensive orbital deployment

<table>
  <tr>
    <td width="50%"><img src="figures/reference_lcoe_components.png" alt="Reference LCOE components"></td>
    <td width="50%"><img src="figures/uk_electricity_cost_benchmark_comparison.png" alt="UK electricity cost benchmarks"></td>
  </tr>
  <tr>
    <td><b>Reference cost structure.</b> Annualised CAPEX contributes about 82% of the 429 GBP/MWh reference LCOE.</td>
    <td><b>Decision context.</b> The model separates generation-only benchmarks from broader system-adjusted comparisons.</td>
  </tr>
</table>

At the reference point, a 2 GW grid-delivered system requires approximately 13.33 GW of space-side power and 66,667 tonnes of orbital hardware. Launch, orbit transfer and in-orbit assembly therefore scale together.

### 2. Most single-variable improvements do not cross the screening line

<table>
  <tr>
    <td width="50%"><img src="figures/one_way_lcoe_floors.png" alt="Best LCOE reached by each one-way change"></td>
    <td width="50%"><img src="figures/specific_mass_threshold_focus.png" alt="Specific mass thresholds near the decision window"></td>
  </tr>
  <tr>
    <td><b>One-way limits.</b> Within the selected ranges and with all other inputs fixed, only specific mass reaches the study-defined 150 GBP/MWh line.</td>
    <td><b>Conditional mass thresholds.</b> Specific mass must be no higher than about 1.28, 0.88 and 0.62 kg/kW-space to reach 150, 120 and 100 GBP/MWh respectively, with other inputs fixed.</td>
  </tr>
</table>

| One-way change | Best explored value | Resulting LCOE |
| --- | ---: | ---: |
| Specific mass | 0.5 kg/kW-space | **91 GBP/MWh** |
| End-to-end efficiency | 35% | **188 GBP/MWh** |
| Launch cost | 20 GBP/kg | **204 GBP/MWh** |
| WACC | 3% | **312 GBP/MWh** |
| In-orbit assembly | 0 GBP/kg | **335 GBP/MWh** |

The key point is structural: reducing the price per launched kilogram does not remove the cost of having to launch, transfer and assemble a heavy, low-efficiency architecture.

### 3. Launch cost only becomes decisive when efficiency and mass are credible

<table>
  <tr>
    <td width="50%"><img src="figures/sbsp_break_even_thresholds.png" alt="Launch cost and efficiency threshold matrix"></td>
    <td width="50%"><img src="figures/contour_launch_cost_vs_end_to_end_efficiency_zoom.png" alt="Launch cost and efficiency decision contours"></td>
  </tr>
  <tr>
    <td><b>Threshold matrix.</b> At 25% efficiency, the 150 GBP/MWh target requires launch cost of roughly 109 GBP/kg or less. At 35% efficiency, 100 GBP/MWh requires about 64 GBP/kg.</td>
    <td><b>Continuous interaction.</b> The contour view shows that cheap launch applied to an inefficient architecture still leaves high delivered costs.</td>
  </tr>
</table>

### 4. Lower targets increasingly favour coordinated progress

![Model-normalised joint improvement needed for each target](figures/combined_progress_frontier.png)

The combined frontier moves the principal physical and financial bottlenecks by an equal fraction from their reference values toward their favourable explored bounds. It is a mathematical comparison device, not a technology-readiness score or development schedule.

| Target LCOE | Model-normalised joint movement | Illustrative launch cost | Specific mass | Efficiency | WACC |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 150 GBP/MWh | 26.5% | 373 GBP/kg | 3.81 kg/kW-space | 20.3% | 5.57% |
| 120 GBP/MWh | 31.8% | 347 GBP/kg | 3.57 kg/kW-space | 21.4% | 5.39% |
| 100 GBP/MWh | 36.1% | 327 GBP/kg | 3.38 kg/kW-space | 22.2% | 5.24% |
| 80 GBP/MWh | 41.1% | 303 GBP/kg | 3.15 kg/kW-space | 23.2% | 5.06% |
| 60 GBP/MWh | 47.4% | 272 GBP/kg | 2.87 kg/kW-space | 24.5% | 4.84% |

These values must be read together with the simultaneous changes in orbital hardware, assembly, transfer, rectenna, grid connection, availability, lifetime, margins and OPEX recorded in [`combined_improvement_frontier.csv`](data/processed/combined_improvement_frontier.csv).

## Model Logic

The principal relationships are deliberately compact and inspectable:

```text
required space-side power = delivered grid power / end-to-end efficiency

orbital mass = required space-side power × specific mass

annual delivered electricity = delivered capacity × 8,760 × capacity factor

annual total cost = annualised CAPEX
                  + fixed OPEX
                  + replacement/refurbishment allowance
                  + variable OPEX

delivered-grid LCOE = annual total cost / annual delivered electricity
```

Initial CAPEX includes the space segment, wireless power transmission, launch, orbit transfer, in-orbit assembly, rectenna, grid connection and programme margin. The implementation is in [`src/model.py`](src/model.py); threshold and contour methods are in [`src/analysis.py`](src/analysis.py).

## Reproduce the Analysis

```bash
git clone https://github.com/WenyuGao1/uk-sbsp-cost-threshold-assessment.git
cd uk-sbsp-cost-threshold-assessment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analysis/run_full_analysis.py
python -m unittest discover -s tests -v
```

The full runner regenerates all processed CSVs, English and Chinese figures, Markdown reports, PDF reports and the verification note. GitHub Actions repeats both the numerical tests and full generation pipeline on every push and pull request.

## Repository Guide

| Path | Purpose |
| --- | --- |
| [`data/sbsp_parameters.csv`](data/sbsp_parameters.csv) | Study-authored reference values, explored ranges and directions of improvement |
| [`data/parameter_evidence.csv`](data/parameter_evidence.csv) | External evidence mapped to claims, with explicit comparability limitations |
| [`data/external_sbsp_studies.csv`](data/external_sbsp_studies.csv) | Structured comparison with selected UK and NASA SBSP studies |
| [`data/source_registry.csv`](data/source_registry.csv) | External source metadata, URLs and analytical roles |
| [`data/raw/`](data/raw/) | Official UK source workbooks retained for traceability |
| [`data/processed/`](data/processed/) | Reproducible model outputs and threshold tables |
| [`src/model.py`](src/model.py) | Delivered-grid LCOE calculation |
| [`src/analysis.py`](src/analysis.py) | Sensitivities, thresholds, contours and combined frontiers |
| [`figures/`](figures/) | English-labelled analytical figures |
| [`figures_zh/`](figures_zh/) | Chinese-labelled analytical figures |
| [`html/index.html`](html/index.html) | Standalone bilingual interactive cost explorer |
| [`report/`](report/) | Final English and Chinese reports, PDFs and verification note |
| [`tests/`](tests/) | Numerical reconciliation and evidence-file checks |

## Evidence and Quality Controls

- Parameter reference values must remain inside their explored ranges.
- Initial CAPEX and annual cost components are reconciled numerically.
- The reference LCOE and high-precision specific-mass and launch-efficiency roots are regression-tested against target residuals.
- Raw `.xlsx` files must parse as workbooks; selected DESNZ 2025 source cells are reconciled directly to the benchmark CSV.
- CSV record structure and every `source_id` foreign key are validated.
- Figure reference markers are checked against the true analytical reference case.
- Expected reports, tables and figures must exist and be non-empty.
- Both final PDFs are structurally checked by the pipeline and rendered page by page for release review of clipping, table overflow, fonts and chart labels.

See the generated [`verification_note.md`](report/verification_note.md) for the current release checks and evidence limitations.

## UK Benchmark Treatment

The repository deliberately separates:

- **generation-only LCOE**, which measures cost at the generator boundary; and
- **system-adjusted comparison ranges**, which provide broader but still indicative context for balancing, curtailment, networks, flexibility and reliability.

The project does not silently treat benchmarks with different real-price bases as perfectly comparable. It also does not claim that an SBSP LCOE inside the 80-120 GBP/MWh region automatically creates market competitiveness.

## Relationship to Existing SBSP Studies

This repository is designed to complement, not replace, larger architecture and system studies:

- The [2021 UK Government / Frazer-Nash assessment](https://www.gov.uk/government/publications/space-based-solar-power-de-risking-the-pathway-to-net-zero) examined engineering feasibility, economics, risks and a possible UK development pathway.
- The [DESNZ small-scale SBSP study](https://assets.publishing.service.gov.uk/media/698f167c7da91680ad7f43ad/SBSP-enabled-pathways-to-net-zero-final-report-raf036-2425.pdf) assessed an early-market minimum viable product, uncertainty, financing support and GB energy-system benefits.
- The [NASA OTPS assessment](https://www.nasa.gov/organizations/otps/space-based-solar-power-report/) compared conceptual SBSP lifecycle cost and emissions with terrestrial alternatives.

Those studies provide architecture, deployment, policy and system context. This project contributes a public, bilingual and executable way to ask: **inside a stated model and parameter range, which combinations cross a chosen delivered-cost line?**

## Scope and Limitations

Commercial-scale SBSP has not been deployed. Many architecture parameters are therefore exploratory rather than observed commercial data.

The model identifies **conditional cost requirements under its stated assumptions and explored ranges**. It does not prove:

- engineering feasibility or technology readiness;
- safe and regulator-approved wireless power transmission;
- construction delivery or commercial financeability;
- frequency, beam, spectrum, land-use or public-acceptance compliance;
- the complete value of firm low-carbon power in the future GB system;
- investment attractiveness or a future electricity price.

Those questions require architecture-specific engineering, demonstration, financing and whole-system modelling.

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). If you reuse the model or figures, please cite the repository and preserve the distinction between model-conditional thresholds and real-world engineering requirements.

## Licence and Third-Party Material

Original code and project-authored documentation are released under the [MIT License](LICENSE). External workbooks and source material retain their original terms; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
