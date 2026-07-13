# Verification Note

## Verification completed

- Loaded and validated the parameter, generation-benchmark and system-adjusted benchmark CSVs.
- Validated all raw XLSX evidence files as genuine workbook containers.
- Reconciled reference LCOE, initial CAPEX, annual costs and delivered electricity.
- Checked one-way thresholds, true reference markers and combined-frontier outputs.
- Regenerated aligned English and Chinese figures, Markdown reports and PDF reports.
- Checked report numbering, required outputs and non-empty files.
- final_report_EN.pdf built with current Python reportlab installation.
- final_report_zh.pdf built with current Python reportlab installation.

## Refinement changes

- Reduced the main report to seven decision-led sections with compact tables and a complete audit appendix.
- Replaced high-range main curves with one-way floors, a specific-mass decision-window view and a launch-efficiency matrix.
- Displayed UK benchmarks as intervals with explicit price bases and a separate 80-120 GBP/MWh decision region.
- Masked contour values above 220 GBP/MWh and highlighted the 80, 100, 120 and 150 GBP/MWh cost lines.
- Corrected reference markers, CAPEX reconciliation and the invalid raw-workbook placeholder.
- Improved PDF table widths, prevented the CAPEX table from splitting and removed repeated assumption-classification text.
- Aligned all chart labels and report content across English and Chinese outputs.
- Archived the superseded unlabelled report files under report/archive/.

## Evidence limits

- The latest DESNZ generation-cost data does not provide a directly comparable updated generic nuclear LCOE.
- The latest DESNZ generation-cost report excludes wider system costs; BEIS 2020 enhanced LCOE ranges are used as the system-adjusted benchmark.
- The wider high-renewable system-pressure comparator remains qualitative because grid, storage, curtailment and backup costs are not directly comparable single LCOE values in the cited evidence.
- System-adjusted costs remain indicative comparators rather than direct market prices.
- SBSP architecture parameters remain exploratory because commercial-scale SBSP has not been deployed.

## Model uncertainties

- Actual orbital mass, assembly cost, replacement rate and end-to-end efficiency remain architecture-dependent.
- System value of SBSP as firm low-carbon power requires full UK power-system modelling and is not monetised in this LCOE model.
- Real cost of capital would depend on technology maturity, support mechanism and risk allocation.
- Alternative combined frontiers are illustrative parameter-space slices, not engineering roadmaps or predictions.

## Acceptance Criteria Status

| Criterion | Status |
| --- | --- |
| A: no fixed-year SBSP forecast | satisfied |
| B: no named deployment-case framing | satisfied |
| C: reference point and limitations explained | satisfied |
| D: UK system-cost benchmark discussion improved | satisfied |
| E: continuous curves and 2D contours generated | satisfied |
| F: break-even threshold tables generated | satisfied |
| G: external numerical inputs cited or labelled | satisfied |
| H: model thresholds, feasibility, readiness and system value distinguished | satisfied |
| I: English and Chinese final reports generated | satisfied |
| J: reproducible repository structure | satisfied |
| K: key figures integrated into analytical sections | satisfied |
| L: full one-way diagnostic retained in Appendix A | satisfied |
| M: BEIS 45-87 comparator treated as conservative rather than definitive | satisfied |
| N: industry-style front matter and title page added | satisfied |
| O: executive decision summary and limitations section added | satisfied |
| P: figure and table numbering standardized | satisfied |
| Q: appendices A-C structured for secondary figures, sources and assumptions | satisfied |
| R: analytical content preserved while presentation was refined | satisfied |
| S: raw XLSX evidence files validated as real workbook containers | satisfied |
| T: main charts prioritise the decision-cost window | satisfied |
| English PDF report | satisfied |
| Chinese PDF report | satisfied |

Overall status: all acceptance criteria are satisfied. For this release, both PDFs were rendered to PNG pages with Poppler and inspected for missing pages, font rendering, clipping, table overflow and chart-label legibility.
