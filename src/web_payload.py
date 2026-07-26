"""Generate the browser's bilingual model-data payload from canonical CSV data."""

from __future__ import annotations

import json
from pathlib import Path

from .parameters import Parameter


def build_web_payload(output_path: str | Path, params: dict[str, Parameter], combined_frontier: list[dict[str, object]], configuration_rows: list[dict[str, str]] | None = None) -> None:
    parameter_rows = []
    for item in params.values():
        span = item.max_value - item.min_value
        if "fraction" in item.unit:
            step = 0.001
            fmt = "percent"
        elif item.name in {"operating_lifetime_years", "construction_duration_years"}:
            step = 1
            fmt = "integer"
        elif span >= 10_000_000:
            step = 1_000_000
            fmt = "money"
        elif span >= 1000:
            step = 10
            fmt = "number"
        elif span >= 10:
            step = 0.1
            fmt = "number"
        else:
            step = 0.01
            fmt = "number"
        parameter_rows.append({
            "id": item.name,
            "label": {"en": item.display_name, "zh": item.display_name_zh},
            "unit": item.unit,
            "min": item.min_value,
            "max": item.max_value,
            "step": step,
            "base": item.reference_value,
            "direction": item.improvement_direction,
            "format": fmt,
            "sourceType": item.source_type,
            "sourceId": item.source_id,
            "priceYear": item.price_year,
            "denominator": {"en": item.denominator_definition, "zh": item.denominator_definition_zh},
            "limitation": {"en": item.notes, "zh": item.notes_zh},
        })
    reference = {name: item.reference_value for name, item in params.items()}
    scenarios = [{
        "id": "reference",
        "label": {"en": "Reference", "zh": "参考情景"},
        "description": {"en": "Study-authored analytical anchor", "zh": "研究自定的分析锚点"},
        "sourceType": "exploratory",
        "sourceId": "ASSUMPTION_THIS_STUDY",
        "priceYear": "2024 real GBP",
        "denominator": {"en": "Uses the parameter-specific boundaries shown in each tooltip", "zh": "采用各参数提示中显示的特定边界"},
        "limitation": {"en": "Not a forecast or preferred architecture", "zh": "不是预测或优选架构"},
        "values": reference,
    }]
    for row in combined_frontier:
        if row.get("progress_fraction") in (None, "") or float(row["progress_fraction"]) <= 0:
            continue
        target = int(float(row["target_lcoe_gbp_per_mwh"]))
        values = dict(reference)
        for name in params:
            if name in row:
                values[name] = float(row[name])
        scenarios.append({
            "id": f"illustrative_{target}",
            "label": {"en": f"Illustrative combination to £{target}/MWh", "zh": f"£{target}/MWh示意参数组合"},
            "shortLabel": {"en": f"Illustrative £{target}", "zh": f"示意 £{target}"},
            "description": {"en": "Equal-fraction mathematical interpolation toward favourable exploration bounds", "zh": "向有利探索边界进行等比例数学插值"},
            "sourceType": "mathematical_interpolation",
            "sourceId": "ASSUMPTION_THIS_STUDY",
            "priceYear": "2024 real GBP",
            "denominator": {"en": "Parameter-specific model boundaries", "zh": "各参数特定模型边界"},
            "limitation": {"en": "Not a roadmap, probability, forecast or engineering design", "zh": "不是路线图、概率、预测或工程设计"},
            "values": values,
        })
    configuration = {row["configuration_key"]: row for row in (configuration_rows or [])}
    payload = {
        "version": "v2.0",
        "priceYear": int(configuration.get("price_year", {}).get("value", 2024)),
        "valuationBase": configuration.get("valuation_base", {}).get("value", "start of construction (t=0)"),
        "stagingOrbit": configuration.get("staging_orbit", {}).get("value", "LEO staging orbit (service boundary; altitude architecture-dependent)"),
        "operationalOrbit": configuration.get("operational_orbit", {}).get("value", "High Earth orbit (HEO; final orbit architecture-dependent)"),
        "launchPricingMode": configuration.get("launch_pricing_mode", {}).get("value", "per_kg"),
        "parameters": parameter_rows,
        "scenarios": scenarios,
        "configuration": configuration,
    }
    script = "(function(root,factory){if(typeof module==='object'&&module.exports){module.exports=factory();}else{root.SBSP_MODEL_DATA=factory();}})(typeof self!=='undefined'?self:this,function(){return " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";});\n"
    Path(output_path).write_text(script, encoding="utf-8")
