# Verification Note

Version: v1.2

Evidence review date: 2026-07-19

Overall automated status: **PASS**

Table 1. Verification categories

| Category | Status | Evidence |
| --- | --- | --- |
| Numerical model | PASS | Reference CAPEX and annual-cost identities reconcile; root-solved thresholds are written with their target residuals. |
| Input data structure | PASS | CSV record lengths, headers, required parameter bounds and official XLSX parseability were checked. |
| Source and benchmark traceability | PASS | Source foreign keys resolve; exact SBSP inputs are study-authored; selected DESNZ 2025 cells reconcile to the benchmark CSV. |
| Bilingual numerical parity | PASS | Both Markdown reports contain the shared version, reference LCOE, mass thresholds and coupled-frontier percentages. |
| Output completeness | PASS | Checked 71 expected files, generated CSV row/schema invariants, decodable PNGs and seven resolved main figures per report. |
| PDF structure | PASS | Both PDFs were parsed, checked for a minimum page count and checked for extractable text. |

## Known warnings and residual uncertainty

- Actual orbital mass, assembly cost, replacement rate and end-to-end efficiency remain architecture-dependent.
- BEIS 2018-real-GBP system-adjusted values and DESNZ 2024-real-GBP generation values are disclosed but not price-normalised.
- System value requires a full GB power-system model and is not monetised here.
- PDF visual quality is verified separately during release review; the pipeline checks structure and extractable content.

## Reproduction commands

- `python -m unittest discover -s tests -v`
- `python analysis/run_full_analysis.py`

## Interpretation

`PASS` means the recorded automated checks completed for the current generated files. It does not prove engineering feasibility or eliminate judgement in exploratory ranges. PDF structural checks confirm that documents can be opened and contain the expected pages and text; visual release QA remains a separate human inspection step.
