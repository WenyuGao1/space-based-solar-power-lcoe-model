"""Load and expose model parameters from structured CSV files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .utils import parse_float, read_csv_dicts


@dataclass(frozen=True)
class Parameter:
    name: str
    display_name: str
    display_name_zh: str
    unit: str
    reference_value: float
    min_value: float
    max_value: float
    improvement_direction: str
    source_type: str
    source_id: str
    price_year: str
    denominator_definition: str
    denominator_definition_zh: str
    notes: str
    notes_zh: str


def load_parameters(path: str | Path) -> dict[str, Parameter]:
    params: dict[str, Parameter] = {}
    for row in read_csv_dicts(path):
        name = row["parameter"].strip()
        params[name] = Parameter(
            name=name,
            display_name=row["display_name"].strip(),
            display_name_zh=row["display_name_zh"].strip(),
            unit=row["unit"].strip(),
            reference_value=float(row["reference_value"]),
            min_value=float(row["min_value"]),
            max_value=float(row["max_value"]),
            improvement_direction=row["improvement_direction"].strip().lower(),
            source_type=row["source_type"].strip(),
            source_id=row["source_id"].strip(),
            price_year=row["price_year"].strip(),
            denominator_definition=row["denominator_definition"].strip(),
            denominator_definition_zh=row["denominator_definition_zh"].strip(),
            notes=row["notes"].strip(),
            notes_zh=row["notes_zh"].strip(),
        )
    return params


def reference_values(params: dict[str, Parameter]) -> dict[str, float]:
    return {name: parameter.reference_value for name, parameter in params.items()}


def parameter_ranges(params: dict[str, Parameter]) -> dict[str, tuple[float, float]]:
    return {name: (parameter.min_value, parameter.max_value) for name, parameter in params.items()}


def numeric_benchmark_rows(path: str | Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in read_csv_dicts(path):
        parsed = dict(row)
        for key in ("value_low_gbp_per_mwh", "value_mid_gbp_per_mwh", "value_high_gbp_per_mwh"):
            parsed[key] = parse_float(row.get(key))
        rows.append(parsed)
    return rows
