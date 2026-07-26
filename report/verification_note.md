# v2.0 Verification Note

| Category | Status | Evidence |
| --- | --- | --- |
| Numerical model | PASS | Stage powers, delivered-basis mass, DCF, launch and replacement boundaries reconciled. |
| Input metadata | PASS | Every parameter has bilingual source, denominator and limitation metadata. |
| Bilingual parity | PASS | English and Chinese reports share version, reference LCOE and computed efficiency. |
| Generated artefacts | PASS | Checked 87 output files plus CSV, PNG, Markdown and PDF structure. |

## Warnings

- This is a scenario result, not a commercial forecast.
- The rectenna proxy does not explicitly model beam geometry, land, weather, safety or power-density constraints.
- Architecture inputs may be dependent; exploration bounds are not probability distributions.

## Commands

```bash
python -m unittest discover -s tests -v
python analysis/run_full_analysis.py
```
