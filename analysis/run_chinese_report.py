"""Compatibility runner for regenerating the Chinese report.

The final project keeps English and Chinese outputs aligned, so this wrapper
delegates to the full end-to-end pipeline.
"""

from __future__ import annotations

from run_full_analysis import main


if __name__ == "__main__":
    raise SystemExit(main())
