"""Small CSV and formatting helpers used across the project."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence


def read_csv_dicts(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_dicts(path: str | Path, rows: Iterable[Mapping[str, object]], fieldnames: Sequence[str]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def parse_float(value: object, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        if text.startswith("<"):
            try:
                return float(text[1:].strip()) / 2.0
            except ValueError:
                return default
        return default


def fmt_money(value: float | None, decimals: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{decimals}f}"


def fmt_float(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}"


def fmt_percent(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * value:.{decimals}f}%"
