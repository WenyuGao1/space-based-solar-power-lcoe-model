"""Simplified-Chinese report entry point sharing the v2.0 numerical payload."""

from __future__ import annotations

from pathlib import Path

from .reporting import _report


def build_markdown_report_zh(output_path: str | Path, reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows) -> None:
    Path(output_path).write_text(_report("zh", reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows), encoding="utf-8")
