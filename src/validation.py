"""Release validation for the v2.0 model and generated artefacts."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import re
import zipfile

from .model import calculate_lcoe
from .parameters import Parameter


REQUIRED_PARAMETERS = {
    "delivered_capacity_mw", "solar_conversion_efficiency", "dc_to_rf_efficiency",
    "transmission_efficiency", "rectenna_conversion_efficiency", "grid_conversion_efficiency",
    "capacity_factor", "operating_lifetime_years", "real_discount_rate",
    "construction_duration_years", "annual_output_degradation_fraction",
    "system_specific_mass_kg_per_kw_delivered", "space_generation_hardware_cost_gbp_per_w_dc",
    "transmitter_cost_gbp_per_w_rf_emitted", "launch_cost_gbp_per_kg_to_staging_orbit",
    "launch_price_gbp_per_flight", "effective_payload_kg_per_flight", "payload_utilisation_fraction",
    "orbit_transfer_cost_gbp_per_kg_final_hardware",
    "in_orbit_assembly_cost_gbp_per_kg_operational_hardware",
    "rectenna_cost_gbp_per_w_delivered", "grid_connection_cost_gbp_per_kw_delivered",
    "programme_contingency_fraction", "space_hardware_replacement_rate_per_year",
    "ground_hardware_replacement_rate_per_year",
    "fixed_opex_fraction_of_eligible_assets_per_year", "variable_opex_gbp_per_mwh",
    "decommissioning_cost_fraction_initial_capex", "residual_value_fraction_initial_capex",
}

PARAMETER_COLUMNS = [
    "parameter", "display_name", "display_name_zh", "unit", "reference_value", "min_value",
    "max_value", "improvement_direction", "source_type", "source_id", "price_year",
    "denominator_definition", "denominator_definition_zh", "notes", "notes_zh",
]


def validate_parameters(params: dict[str, Parameter]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_PARAMETERS - set(params)
    if missing:
        errors.append(f"Missing required parameters: {', '.join(sorted(missing))}")
    fraction_tokens = ("efficiency", "fraction", "capacity_factor", "payload_utilisation", "replacement_rate", "opex_fraction")
    strictly_positive = {"delivered_capacity_mw", "operating_lifetime_years", "system_specific_mass_kg_per_kw_delivered", "effective_payload_kg_per_flight"}
    for item in params.values():
        if not all(math.isfinite(value) for value in (item.min_value, item.reference_value, item.max_value)):
            errors.append(f"{item.name} contains a non-finite value.")
        if not item.min_value <= item.reference_value <= item.max_value:
            errors.append(f"{item.name} reference value is outside its range.")
        if item.improvement_direction not in {"lower", "higher"}:
            errors.append(f"{item.name} has an invalid improvement direction.")
        if any(token in item.name for token in fraction_tokens):
            if item.min_value < 0 or item.max_value > 1:
                errors.append(f"{item.name} fraction range must lie in [0, 1].")
        elif item.name == "real_discount_rate" and (item.min_value < 0 or item.max_value >= 1):
            errors.append("real_discount_rate must lie in [0, 1).")
        elif item.name in strictly_positive and item.min_value <= 0:
            errors.append(f"{item.name} must be strictly positive.")
        elif item.min_value < 0:
            errors.append(f"{item.name} cannot be negative.")
        for label, value in (("source type", item.source_type), ("source id", item.source_id),
                             ("denominator", item.denominator_definition), ("limitation", item.notes),
                             ("Chinese denominator", item.denominator_definition_zh), ("Chinese limitation", item.notes_zh)):
            if not value:
                errors.append(f"{item.name} is missing {label} metadata.")
    return errors


def validate_reference_case(reference: dict[str, float]) -> list[str]:
    errors: list[str] = []
    try:
        result = calculate_lcoe(reference)
        if not math.isfinite(result.lcoe_gbp_per_mwh) or result.lcoe_gbp_per_mwh <= 0:
            errors.append("Reference LCOE is not positive and finite.")
        if not math.isclose(result.initial_capex_gbp, result.pre_contingency_capex_gbp + result.programme_contingency_gbp, rel_tol=1e-12):
            errors.append("Initial CAPEX does not reconcile.")
        if not math.isclose(sum(result.lifecycle_cost_components_pv_gbp.values()), result.discounted_lifetime_cost_gbp, rel_tol=1e-12):
            errors.append("Discounted lifecycle cost does not reconcile.")
        if not math.isclose(math.prod(reference[name] for name in (
            "solar_conversion_efficiency", "dc_to_rf_efficiency", "transmission_efficiency",
            "rectenna_conversion_efficiency", "grid_conversion_efficiency")), result.end_to_end_efficiency, rel_tol=1e-12):
            errors.append("Computed end-to-end efficiency does not reconcile.")
    except Exception as exc:
        errors.append(f"Reference case failed: {exc}")
    return errors


def validate_analysis_results(reference: dict[str, float], params: dict[str, Parameter], sensitivity_parameter_names: list[str], thresholds: list[dict[str, object]], launch_frontier: list[dict[str, object]], combined_frontier: list[dict[str, object]], alternative_frontiers: list[dict[str, object]], tolerance: float = 1e-6) -> list[str]:
    errors: list[str] = []
    for name in sensitivity_parameter_names:
        parameter = params[name]
        case = dict(reference)
        favourable = parameter.min_value if parameter.improvement_direction == "lower" else parameter.max_value
        case[name] = favourable
        if calculate_lcoe(case).lcoe_gbp_per_mwh > calculate_lcoe(reference).lcoe_gbp_per_mwh + tolerance:
            errors.append(f"Favourable one-way bound raises LCOE: {name}")
    for row in thresholds:
        value = row.get("threshold_value")
        if value in (None, ""):
            continue
        parameter = params[str(row["parameter"])]
        if not parameter.min_value <= float(value) <= parameter.max_value:
            errors.append(f"Threshold outside bounds: {parameter.name}")
    for group, label in ((combined_frontier, "combined"), (alternative_frontiers, "alternative")):
        for row in group:
            progress = row.get("progress_fraction")
            if progress not in (None, "") and not 0 <= float(progress) <= 1:
                errors.append(f"Invalid {label} progress fraction.")
    for row in launch_frontier:
        if row.get("status") == "feasible" and row.get("max_launch_cost_gbp_per_kg_to_staging_orbit") is None:
            errors.append("Feasible launch frontier has no threshold.")
    return errors


def validate_raw_workbooks(paths: list[str | Path]) -> list[str]:
    errors: list[str] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            errors.append(f"Missing workbook: {path}")
        elif not zipfile.is_zipfile(path):
            errors.append(f"Invalid XLSX container: {path}")
    return errors


def validate_csv_structure(paths: list[str | Path]) -> list[str]:
    errors: list[str] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            errors.append(f"Missing CSV: {path}")
            continue
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                if not reader.fieldnames:
                    errors.append(f"CSV has no header: {path}")
                if path.name == "sbsp_parameters.csv" and reader.fieldnames != PARAMETER_COLUMNS:
                    errors.append(f"Parameter CSV schema mismatch: {path}")
                if not rows:
                    errors.append(f"CSV has no records: {path}")
                for index, row in enumerate(rows, 2):
                    if None in row:
                        errors.append(f"CSV row has extra fields: {path}:{index}")
        except Exception as exc:
            errors.append(f"Could not parse CSV {path}: {exc}")
    return errors


def validate_source_integrity(source_registry_path: str | Path, linked_paths: list[str | Path]) -> list[str]:
    with Path(source_registry_path).open(newline="", encoding="utf-8-sig") as handle:
        source_ids = {row["source_id"].strip() for row in csv.DictReader(handle)}
    errors: list[str] = []
    for raw in linked_paths:
        path = Path(raw)
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for index, row in enumerate(csv.DictReader(handle), 2):
                source_id = (row.get("source_id") or "").strip()
                if source_id and source_id not in source_ids:
                    errors.append(f"Unknown source_id {source_id} at {path}:{index}")
    return errors


def validate_official_generation_extract(workbook_path: str | Path, csv_path: str | Path) -> list[str]:
    errors = validate_raw_workbooks([workbook_path])
    if not Path(csv_path).exists():
        errors.append(f"Missing official generation extract: {csv_path}")
    else:
        with Path(csv_path).open(newline="", encoding="utf-8-sig") as handle:
            for index, row in enumerate(csv.DictReader(handle), 2):
                for column in ("value_low_gbp_per_mwh", "value_mid_gbp_per_mwh", "value_high_gbp_per_mwh"):
                    value = (row.get(column) or "").strip()
                    if value:
                        try:
                            float(value)
                        except ValueError:
                            errors.append(f"Non-numeric official benchmark at {csv_path}:{index}:{column}")
    return errors


def validate_outputs(paths: list[str | Path]) -> list[str]:
    return [f"Missing or empty output: {Path(raw)}" for raw in paths if not Path(raw).exists() or Path(raw).stat().st_size == 0]


def validate_generated_csv_outputs(specifications: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for spec in specifications:
        path = Path(spec["path"])
        if not path.exists():
            errors.append(f"Missing generated CSV: {path}")
            continue
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fields = set(reader.fieldnames or [])
        expected = int(spec["row_count"])
        if len(rows) != expected:
            errors.append(f"Unexpected row count in {path}: {len(rows)} != {expected}")
        missing = set(spec.get("required_columns", [])) - fields
        if missing:
            errors.append(f"Missing columns in {path}: {sorted(missing)}")
        keys = list(spec.get("key_columns", []))
        if keys and len({tuple(row.get(key, "") for key in keys) for row in rows}) != len(rows):
            errors.append(f"Duplicate generated keys in {path}")
    return errors


def validate_png_images(paths: list[str | Path], minimum_width: int = 600, minimum_height: int = 350) -> list[str]:
    errors: list[str] = []
    try:
        from PIL import Image
    except ImportError:
        return ["Pillow is unavailable for PNG validation."]
    for raw in paths:
        path = Path(raw)
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.width < minimum_width or image.height < minimum_height:
                    errors.append(f"PNG is too small: {path}")
        except Exception as exc:
            errors.append(f"Invalid PNG {path}: {exc}")
    return errors


def validate_markdown_images(report_paths: list[str | Path], expected_count: int = 4) -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for raw in report_paths:
        path = Path(raw)
        text = path.read_text(encoding="utf-8")
        links = pattern.findall(text)
        if len(links) < expected_count:
            errors.append(f"Too few report images in {path}: {len(links)}")
        for link in links:
            if not (path.parent / link).resolve().exists():
                errors.append(f"Broken image link in {path}: {link}")
    return errors


def validate_report_content(report_paths: list[str | Path], shared_tokens: list[str]) -> list[str]:
    errors: list[str] = []
    for raw in report_paths:
        text = Path(raw).read_text(encoding="utf-8")
        for token in shared_tokens:
            if token not in text:
                errors.append(f"Missing shared report token {token!r} in {raw}")
    return errors


def validate_pdf_documents(paths: list[str | Path], required_text_tokens: list[str] | None = None) -> list[str]:
    errors: list[str] = []
    try:
        from pypdf import PdfReader
    except ImportError:
        return ["pypdf is unavailable for PDF validation."]
    for raw in paths:
        path = Path(raw)
        try:
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if len(reader.pages) < 2:
                errors.append(f"PDF has too few pages: {path}")
            for glyph in ("■", "□", "�"):
                if glyph in text:
                    errors.append(f"PDF contains an invalid replacement glyph {glyph!r}: {path}")
            for token in required_text_tokens or []:
                if token not in text:
                    errors.append(f"PDF missing token {token!r}: {path}")
        except Exception as exc:
            errors.append(f"Invalid PDF {path}: {exc}")
    return errors
