"""Bilingual Markdown report generation for the v2.0 methodology."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .model import calculate_lcoe
from .parameters import Parameter


VERSION = "v2.0"
AUTHOR = "Wenyu Gao"
REPORT_DATE_EN = "28 July 2026"
REPORT_DATE_ZH = "2026年7月28日"
EVIDENCE_DATE_EN = "19 July 2026"
EVIDENCE_DATE_ZH = "2026年7月19日"
REPOSITORY_URL = "https://github.com/WenyuGao1/space-based-solar-power-lcoe-model"
EXPLORER_URL = "https://wenyugao1.github.io/space-based-solar-power-lcoe-model/html/"


def _money(value: float) -> str:
    billions = value / 1e9
    if abs(billions) < 0.005:
        billions = 0.0
    return f"£{billions:,.2f}bn"


def _table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    values = [[str(cell) for cell in row] for row in rows]
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(row) + " |" for row in values),
    ])


def _display_unit(unit: str, language: str) -> str:
    if language != "zh":
        return unit
    return {
        "MW-delivered AC": "MW并网交流交付",
        "fraction": "比例",
        "years": "年",
        "fraction/year": "比例/年",
        "kg/kW-delivered": "kg/kW-交付",
        "GBP/W-DC": "英镑/W-直流",
        "GBP/W-RF emitted": "英镑/W-射频发射",
        "GBP/kg to staging orbit": "英镑/kg（至集结轨道）",
        "GBP/flight": "英镑/次",
        "kg/flight": "kg/次",
        "GBP/kg final hardware": "英镑/kg（最终硬件）",
        "GBP/kg operational hardware": "英镑/kg（运行硬件）",
        "GBP/W-delivered AC": "英镑/W-交流交付",
        "GBP/kW-delivered AC": "英镑/kW-交流交付",
        "fraction of pre-contingency initial CAPEX": "初始资本开支（预备费前）比例",
        "GBP/MWh delivered": "英镑/MWh交付",
        "fraction of initial CAPEX": "初始资本开支比例",
    }.get(unit, unit)


def _claim_label(language: str, key: str, params: dict[str, Parameter]) -> str:
    if key in params:
        parameter = params[key]
        return parameter.display_name_zh if language == "zh" else parameter.display_name
    labels = {
        "system_lifetime_years": ("Operating lifetime", "系统运行寿命"),
        "computed_end_to_end_efficiency": ("Computed end-to-end efficiency", "计算所得端到端效率"),
        "fixed_opex_pct_capex_per_year": ("Fixed O&M", "固定运维"),
        "reference_case_lcoe": ("Reference-case LCOE", "参考情景LCOE"),
        "competitive_cost_claim": ("Published low-cost scenarios", "外部低成本情景"),
        "architecture_dependence": ("Architecture dependence", "架构依赖性"),
        "launch_cost_importance": ("Importance of launch cost", "发射成本重要性"),
        "system_value": ("Power-system value", "电力系统价值"),
        "system_adjusted_comparison": ("System-adjusted comparison", "系统调整成本比较"),
    }
    return labels.get(key, (key.replace("_", " ").capitalize(), key))[1 if language == "zh" else 0]


def _evidence_map_rows(
    language: str,
    evidence_rows: list[dict[str, str]],
    params: dict[str, Parameter],
) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in evidence_rows:
        claim = _claim_label(language, row["parameter_or_claim"], params)
        role = row["evidence_role_zh"] if language == "zh" else row["evidence_role"]
        source = f"{row['source_id']} · {row['locator']}"
        supported = row["supported_evidence_zh"] if language == "zh" else row["supported_evidence"]
        numeric = row["numeric_context_zh"] if language == "zh" else row["numeric_context"]
        limitation = row["limitations_zh"] if language == "zh" else row["limitations"]
        interpretation = (
            f"{supported} 数值背景：{numeric}。可比性限制：{limitation}"
            if language == "zh"
            else f"{supported} Numeric context: {numeric}. Comparability limit: {limitation}"
        )
        rows.append([claim, role, source, interpretation])
    return rows


def _format_threshold_value(parameter: Parameter, value: float, language: str) -> str:
    name = parameter.name
    if parameter.unit == "fraction" or "fraction" in parameter.unit:
        formatted = f"{value:.2%}"
    elif parameter.unit == "years":
        formatted = f"{value:,.0f} {'年' if language == 'zh' else ('year' if round(value) == 1 else 'years')}"
    elif parameter.unit.startswith("GBP/"):
        precision = 0 if abs(value) >= 100 else (1 if abs(value) >= 1 else 3)
        unit = parameter.unit.removeprefix("GBP/")
        if language == "zh":
            unit = {
                "kg to staging orbit": "kg（至集结轨道）",
                "W-DC": "W-直流",
            }.get(unit, unit)
        formatted = f"£{value:,.{precision}f}/{unit}"
    else:
        unit = parameter.unit
        if language == "zh" and name == "system_specific_mass_kg_per_kw_delivered":
            unit = "kg/kW-交付"
        formatted = f"{value:,.3g} {unit}"
    condition = "不高于" if language == "zh" and parameter.improvement_direction == "lower" else None
    if language == "zh" and parameter.improvement_direction == "higher":
        condition = "不低于"
    if language == "en":
        condition = "at or below" if parameter.improvement_direction == "lower" else "at or above"
    return f"{condition} {formatted}"


def _selected_threshold_rows(
    language: str,
    thresholds: list[dict[str, object]],
    params: dict[str, Parameter],
) -> list[list[str]]:
    selected = [
        "system_specific_mass_kg_per_kw_delivered",
        "launch_cost_gbp_per_kg_to_staging_orbit",
        "real_discount_rate",
        "space_generation_hardware_cost_gbp_per_w_dc",
        "construction_duration_years",
    ]
    lookup = {
        (str(row["parameter"]), float(row["target_lcoe_gbp_per_mwh"])): row
        for row in thresholds
    }
    rows: list[list[str]] = []
    for target in (80.0, 60.0):
        for name in selected:
            row = lookup.get((name, target))
            if not row or row.get("threshold_value") in (None, ""):
                continue
            parameter = params[name]
            rows.append([
                f"£{target:.0f}/MWh",
                parameter.display_name_zh if language == "zh" else parameter.display_name,
                _format_threshold_value(parameter, float(row["threshold_value"]), language),
            ])
    return rows


def _external_study_rows(
    language: str,
    external_studies: list[dict[str, str]],
) -> list[list[str]]:
    by_id = {row["source_id"]: row for row in external_studies}
    selected = ["UK_SBSP_2021_PHASE2", "DESNZ_SBSP_2025", "NASA_OTPS_SBSP_2024"]
    if language == "en":
        labels = {
            "UK_SBSP_2021_PHASE2": "UK SBSP Phase 2 (2021)",
            "DESNZ_SBSP_2025": "DESNZ small-scale SBSP study (published 2026)",
            "NASA_OTPS_SBSP_2024": "NASA OTPS assessment (2024)",
        }
        contexts = {
            "UK_SBSP_2021_PHASE2": "£35-79/MWh (p10-p90), with p50 about £50/MWh in 2018 prices for a 2040 commissioning case.",
            "DESNZ_SBSP_2025": "2024 GBP: £335-595/MWh (2030), £154-249/MWh (2035), and £87-129/MWh (2040).",
            "NASA_OTPS_SBSP_2024": "FY2022 USD: $610/$1,590 per MWh baseline cases and $30/$80 per MWh under combined favourable assumptions.",
        }
        readings = {
            "UK_SBSP_2021_PHASE2": "Architecture and future-scenario context. Different maturity, financing, price basis and cost boundary prevent direct comparison.",
            "DESNZ_SBSP_2025": "Current UK architecture and system-value context. Different scale, orbit, procurement and hurdle rates mean band overlap is not validation.",
            "NASA_OTPS_SBSP_2024": "Shows the importance of combined favourable assumptions. No NASA cost value is imported into this model.",
        }
    else:
        labels = {
            "UK_SBSP_2021_PHASE2": "英国SBSP第二阶段研究（2021）",
            "DESNZ_SBSP_2025": "DESNZ小规模SBSP研究（2026年发布）",
            "NASA_OTPS_SBSP_2024": "NASA OTPS评估（2024）",
        }
        contexts = {
            "UK_SBSP_2021_PHASE2": "2018年价格：£35-79/MWh（p10-p90），p50约£50/MWh；2040年投运情景。",
            "DESNZ_SBSP_2025": "2024年英镑：2030年£335-595/MWh、2035年£154-249/MWh、2040年£87-129/MWh。",
            "NASA_OTPS_SBSP_2024": "2022财年美元：基准情景$610/$1,590每MWh；组合有利假设下$30/$80每MWh。",
        }
        readings = {
            "UK_SBSP_2021_PHASE2": "提供架构与未来情景背景；成熟度、融资、价格与成本边界不同，不能直接比较。",
            "DESNZ_SBSP_2025": "提供当前英国架构与系统价值背景；规模、轨道、采购和门槛收益率不同，区间重叠不构成验证。",
            "NASA_OTPS_SBSP_2024": "说明组合有利假设的重要性；本模型没有直接采用NASA成本值。",
        }
    return [[labels[source_id], contexts[source_id], readings[source_id]] for source_id in selected if source_id in by_id]


def _reference_entries(
    language: str,
    source_rows: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
) -> str:
    cited_ids = {row["source_id"] for row in evidence_rows}
    cited = [row for row in source_rows if row["source_id"] in cited_ids]
    entries: list[str] = []
    for row in cited:
        published = row.get("publication_date") or row.get("document_year") or "n.d."
        accessed = row.get("accessed_date") or "n/a"
        if language == "zh":
            entries.append(
                f"- **{row['source_id']}** — {row['organization']}（{published}）。"
                f"[{row['title']}]({row['url']})。本报告用途：{row['role']}。访问日期：{accessed}。"
            )
        else:
            entries.append(
                f"- **{row['source_id']}** — {row['organization']} ({published}). "
                f"[{row['title']}]({row['url']}). Role in this report: {row['role']}. Accessed {accessed}."
            )
    return "\n".join(entries)


def _comparison_cases(reference: dict[str, float]) -> tuple[object, object]:
    # Make the five-stage chain equal exactly 20% by solving the solar stage.
    case = dict(reference)
    other = (case["dc_to_rf_efficiency"] * case["transmission_efficiency"]
             * case["rectenna_conversion_efficiency"] * case["grid_conversion_efficiency"])
    case["solar_conversion_efficiency"] = 0.20 / other
    case["system_specific_mass_kg_per_kw_delivered"] = 1.5
    corrected = calculate_lcoe(case)
    # The historical error divided the delivered-basis mass by efficiency again.
    legacy_equivalent = dict(case)
    legacy_equivalent["system_specific_mass_kg_per_kw_delivered"] = 1.5 / 0.20
    old = calculate_lcoe(legacy_equivalent)
    return old, corrected


def _report(
    language: str,
    reference: dict[str, float],
    params: dict[str, Parameter],
    generation_rows: list[dict[str, object]],
    system_rows: list[dict[str, object]],
    thresholds: list[dict[str, object]],
    importance: list[dict[str, object]],
    frontier: list[dict[str, object]],
    combined_frontier: list[dict[str, object]],
    alternative_frontiers: list[dict[str, object]],
    source_rows: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
    assumption_rows: list[dict[str, str]],
    external_study_rows: list[dict[str, str]],
) -> str:
    result = calculate_lcoe(reference)
    old_example, new_example = _comparison_cases(reference)
    mass_source = next(
        item for item in evidence_rows
        if item["parameter_or_claim"] == "system_specific_mass_kg_per_kw_delivered"
        and item["source_id"] == "DESNZ_SBSP_2025"
    )
    top = importance[:8]
    combined = [row for row in combined_frontier if row.get("progress_fraction") not in (None, "")]
    importance_by_parameter = {str(row["parameter"]): row for row in importance}
    mass_floor = float(importance_by_parameter["system_specific_mass_kg_per_kw_delivered"]["best_lcoe_gbp_per_mwh"])
    launch_floor = float(importance_by_parameter["launch_cost_gbp_per_kg_to_staging_orbit"]["best_lcoe_gbp_per_mwh"])
    finance_floor = float(importance_by_parameter["real_discount_rate"]["best_lcoe_gbp_per_mwh"])
    initial_construction_lcoe = (
        result.lifecycle_cost_components_pv_gbp["initial_construction"]
        / result.discounted_lifetime_energy_mwh
    )

    stage_labels_en = {
        "incident_solar_power_w": "Incident solar power",
        "space_dc_bus_power_w": "Space DC-bus output",
        "emitted_rf_power_w": "Emitted RF power",
        "incident_rf_power_w": "RF power incident on rectenna",
        "rectenna_dc_power_w": "Rectenna DC output",
        "delivered_grid_ac_power_w": "Grid-delivered AC power",
    }
    stage_labels_zh = {
        "incident_solar_power_w": "入射太阳功率",
        "space_dc_bus_power_w": "空间直流母线输出",
        "emitted_rf_power_w": "射频发射功率",
        "incident_rf_power_w": "整流天线入射射频功率",
        "rectenna_dc_power_w": "整流天线直流输出",
        "delivered_grid_ac_power_w": "并网交流交付功率",
    }
    capex_labels_en = {
        "space_generation_hardware": "Space-generation hardware",
        "wireless_power_transmitter": "RF transmitter hardware",
        "launch_to_staging_orbit": "Launch to staging orbit",
        "orbit_transfer_to_operational_orbit": "Transfer to operational orbit",
        "in_orbit_assembly_and_deployment": "In-orbit assembly and deployment",
        "rectenna": "Rectenna",
        "grid_connection": "Grid connection",
    }
    capex_labels_zh = {
        "space_generation_hardware": "空间发电硬件",
        "wireless_power_transmitter": "射频发射硬件",
        "launch_to_staging_orbit": "发射至集结轨道",
        "orbit_transfer_to_operational_orbit": "转移至运行轨道",
        "in_orbit_assembly_and_deployment": "在轨组装与部署",
        "rectenna": "整流天线",
        "grid_connection": "并网连接",
    }
    lifecycle_labels_en = {
        "initial_construction": "Initial construction",
        "fixed_opex": "Fixed O&M",
        "variable_opex": "Variable O&M",
        "space_hardware_replacement": "Space-hardware replacement",
        "ground_hardware_replacement": "Ground-hardware replacement",
        "decommissioning": "Decommissioning",
        "residual_value": "Residual value",
    }
    lifecycle_labels_zh = {
        "initial_construction": "初始建设",
        "fixed_opex": "固定运维",
        "variable_opex": "可变运维",
        "space_hardware_replacement": "空间硬件更换",
        "ground_hardware_replacement": "地面硬件更换",
        "decommissioning": "退役",
        "residual_value": "残值",
    }
    stage_labels = stage_labels_zh if language == "zh" else stage_labels_en
    capex_labels = capex_labels_zh if language == "zh" else capex_labels_en
    lifecycle_labels = lifecycle_labels_zh if language == "zh" else lifecycle_labels_en
    stage_rows = [
        [stage_labels[name], f"{value / 1e9:,.2f} GW"]
        for name, value in result.energy_chain_power_w.items()
    ]
    capex_rows = [
        [capex_labels[name], _money(value)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_rows += [
        ["项目预备费" if language == "zh" else "Programme contingency", _money(result.programme_contingency_gbp)],
        ["初始资本开支合计" if language == "zh" else "Total initial CAPEX", _money(result.initial_capex_gbp)],
    ]
    lifecycle_rows = [
        [
            lifecycle_labels[name],
            _money(value),
            f"£{(0.0 if abs(value / result.discounted_lifetime_energy_mwh) < 0.005 else value / result.discounted_lifetime_energy_mwh):,.2f}/MWh",
        ]
        for name, value in sorted(
            result.lifecycle_cost_components_pv_gbp.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
    ]
    driver_rows = [
        [
            params[str(row["parameter"])].display_name_zh if language == "zh" else str(row["display_name"]),
            f"£{float(row['best_lcoe_gbp_per_mwh']):.1f}/MWh",
            f"£{float(row['lcoe_reduction_gbp_per_mwh']):.1f}/MWh",
        ]
        for row in top
    ]
    parameter_rows = [
        [
            parameter.display_name_zh if language == "zh" else parameter.display_name,
            f"{parameter.reference_value:g} {_display_unit(parameter.unit, language)}",
            f"{parameter.min_value:g}-{parameter.max_value:g}",
            parameter.denominator_definition_zh if language == "zh" else parameter.denominator_definition,
            parameter.notes_zh if language == "zh" else parameter.notes,
        ]
        for parameter in params.values()
    ]
    threshold_rows = _selected_threshold_rows(language, thresholds, params)
    evidence_map_rows = _evidence_map_rows(language, evidence_rows, params)
    external_comparison_rows = _external_study_rows(language, external_study_rows)
    reference_entries = _reference_entries(language, source_rows, evidence_rows)
    combined_rows = [
        [
            f"£{float(row['target_lcoe_gbp_per_mwh']):.0f}/MWh",
            f"{float(row['progress_fraction']):.1%}",
            f"{float(row['computed_end_to_end_efficiency']):.2%}",
        ]
        for row in combined
    ]

    figure_root = "figures_zh" if language == "zh" else "figures"

    if language == "zh":
        title = "英国空间太阳能成本条件评估"
        subtitle = "基于明确技术与财务假设的并网交付平准化电力成本阈值分析"
        disclaimer = "这是条件情景结果，不是商业预测、报价、英国官方目标或经济可行性证明。"
        executive = (
            f"本报告独立评估：在一组明确、可调整且可审计的假设下，2 GW英国并网空间太阳能系统的平准化电力成本可达到什么水平，以及哪些变量最能改变结果。参考情景得到 **£{result.lcoe_gbp_per_mwh:.2f}/MWh**（2024年实际英镑）。该结果由贴现生命周期成本 **{_money(result.discounted_lifetime_cost_gbp)}** 除以贴现交付电量 **{result.discounted_lifetime_energy_mwh / 1e6:.2f}百万MWh** 得到。"
        )
        summary_items = [
            f"参考情景假设2 GW并网交流交付、{result.end_to_end_efficiency:.2%}端到端效率、{result.orbital_mass_kg / 1e6:.2f}百万kg（{result.orbital_mass_kg / 1000:,.0f}吨）轨道硬件和{result.required_launches:,}次等效发射。",
            f"贴现初始建设贡献约 **£{initial_construction_lcoe:.2f}/MWh**，是£{result.lcoe_gbp_per_mwh:.2f}/MWh参考结果的主要组成。",
            f"在各自探索范围内，系统比质量、至集结轨道发射成本和实际贴现率的单变量有利边界分别把LCOE降至 **£{mass_floor:.1f}、£{launch_floor:.1f}和£{finance_floor:.1f}/MWh**。这些是边界敏感性，不是联合可实现方案。",
            "英国和NASA研究同样显示，成本结果高度依赖架构、发射、融资与组合有利假设；由于系统边界不同，外部区间只能用于背景与一致性检查，不能验证本模型的£86.03/MWh。",
        ]
        question_text = "研究问题是：在不把情景结果误写成预测的前提下，哪些技术、部署、生命周期和融资条件能够让SBSP进入本研究定义的£80-120/MWh讨论区间？£80、£100、£120和£150/MWh均为分析筛选线，不是英国官方目标。"
        boundary_text = f"系统边界从并网点2 GW交流功率向上游反推至入射太阳功率。发射按kg计价且只覆盖至集结轨道；集结轨道为LEO服务边界，最终运行轨道为架构相关的高地球轨道。轨道转移代理必须覆盖转移器、推进剂、补给任务、运行和载荷性能惩罚。"
        core_headers = ["核心定义或假设", "参考情景", "解释"]
        core_rows = [
            ["交付容量", "2.00 GW AC", "并网连接点的额定交流功率"],
            ["价格口径", "2024年实际英镑", "全部模型财务输入与输出"],
            ["交付容量因子", f"{reference['capacity_factor']:.0%}", "可用率、停运和运行约束的合并代理"],
            ["运行寿命", f"{reference['operating_lifetime_years']:.0f}年", "调试完成后的完整运行年"],
            ["实际贴现率", f"{reference['real_discount_rate']:.1%}", "从建设开始t=0贴现"],
            ["系统比质量", f"{reference['system_specific_mass_kg_per_kw_delivered']:.1f} kg/kW-交付", "每kW并网交付功率对应的整套轨道硬件质量"],
            ["发射成本", f"£{reference['launch_cost_gbp_per_kg_to_staging_orbit']:,.0f}/kg", "仅至集结轨道"],
        ]
        financial_text = f"主指标采用 `LCOE = [sum_t C_t / (1+r)^t] / [sum_t E_t / (1+r)^t]`。估值基准为建设开始t=0；4年建设支出采用相等份额，调试完成后的首个运行年现金流位于t=5。运行寿命为{reference['operating_lifetime_years']:.0f}年，首年交付电量为{result.first_year_delivered_mwh / 1e6:.2f} TWh，寿命期年均交付电量为{result.average_annual_delivered_mwh / 1e6:.2f} TWh。简单CRF对账结果为£{result.crf_reconciliation_lcoe_gbp_per_mwh:.2f}/MWh，仅作次要核对，因为它不复制完整建设期时点。"
        method_text = "轨道质量 = 交付容量(kW) x kg/kW-交付；不会再除以链路效率。空间发电、射频发射、整流天线和并网成本分别按各自额定功率边界计价，避免把同一功率或成本重复计算。空间更换包含相应硬件、发射、转移和组装；地面更换只包含整流天线和并网。固定运维基数不含预备费、初始发射、转移和组装。"
        profile_note = f"默认建设支出曲线为 `{list(result.construction_spend_profile)}`，合计100%。项目预备费只对初始资本开支计提一次。期末退役作为成本，残值在运行寿命结束时抵扣。"
        cost_interpretation = f"贴现初始建设贡献 **£{initial_construction_lcoe:.2f}/MWh**，因此参考结果对初始资本开支、建设时点和融资条件特别敏感。其余生命周期项目不能忽略，但不会改变“前期资本密集”这一主导结构。"
        threshold_intro = "下表列出最具决策意义的单变量阈值：每一行只改变一个参数，其余输入保持参考值。它回答“单独需要到什么水平”，而不声称该水平能够按某一时间表实现。"
        frontier_note = f"参考情景已经低于£150、£120和£100/MWh，因此这些目标在等比例表中显示0.0%移动。£80和£60/MWh需要沿全部有利边界进行数学插值；该前沿不是成熟度、概率、预测、进度表或工程路线图。"
        mass_note = "比质量同时作用于发射、轨道转移、在轨组装和后续空间更换，因此其影响并不等同于单纯减少某一项硬件采购成本。图中的线性趋势来自当前按kg计价边界；真实任务还会受到离散发射次数、结构和运载器集成约束。"
        evidence_intro = "本报告没有把外部研究中的情景数字直接写成本模型默认值。29项默认值均为本研究设定的探索性假设；外部资料只承担技术背景、范围启发、定义核对或一致性比较角色。"
        evidence_interpretation = "这些研究的结果跨度很大，恰好说明SBSP成本不能脱离架构、成熟度、融资和系统边界讨论。本模型的不同之处是公开连续参数阈值、成本分母和可执行计算，而不是声称比固定年份的架构研究更有预测力。"
        test_note = "自动化验证覆盖：比功率与比质量倒数换算、2 GW质量回归、不重复除以效率、六级功率、额定成本分配、发射模式互斥、发射次数取整、更换基数、建设支出份额、DCF/CRF收敛、零贴现率、无效输入、Python与浏览器一致性、中英数值一致性及完整重建。"
        limit_items = [
            "没有天线面积、频率、波束几何、旁瓣、功率密度、土地、天气或安全约束的物理设计。",
            "没有飞行器清单、结构载荷、热控、辐射、故障、备件、离散更换任务或详细发射排程。",
            "没有税务、通胀、融资分层、学习曲线或架构参数相关性。",
            "没有英国电力系统调度、网络增强、平衡、容量价值或市场收入模型。",
            "探索范围不是概率分布，因此不输出P10/P50/P90，也不能把单变量有利边界同时视为最可能发生。",
        ]
        conclusion_text = f"在本研究边界内，参考情景的 **£{result.lcoe_gbp_per_mwh:.2f}/MWh** 已进入研究定义的£80-120/MWh讨论区间，并低于£100/MWh筛选线。模型还表明，在其余假设保持参考值时，仅降低至集结轨道发射成本就可以跨越£80或£60/MWh阈值；但这是一项条件敏感性结论，不等于对运载器成熟度、项目工期、系统安全或融资可得性的预测。更稳健的表述是：SBSP存在可量化的低成本条件空间，而这些条件是否能够在同一可建造架构中同时成立，仍需工程与融资证据。"
        next_steps = [
            "用具体架构的物料清单、结构裕度和地面交付比功率替换探索性系统比质量。",
            "建立离散发射清单、轨道转移与补给方案，并核对按kg价格是否代表可采购服务。",
            "加入波束、整流天线、土地、安全、天气和电网接入的物理及监管约束。",
            "把贴现率、建设延误、失效与更换设为相关概率变量，形成P10/P50/P90结果。",
        ]
        migration_text = f"v1.x把一个本应按交付功率定义的1.5 kg/kW数值乘以“交付功率/效率”，从而重复除以效率。在2 GW、20%效率示例中，旧公式得到 **15,000,000 kg（15,000吨）**，正确公式得到 **3,000,000 kg（3,000吨）**。在其余v2输入相同的对比计算中，错误质量边界对应 **£{old_example.lcoe_gbp_per_mwh:.2f}/MWh**，正确边界对应 **£{new_example.lcoe_gbp_per_mwh:.2f}/MWh**。因此历史v1.x阈值与v2.0不可直接比较。"
        source_note = f"DESNZ/Frazer-Nash报告把架构比功率定义为地面交付功率/轨道质量；0.67 kW-交付/kg的倒数为 **{1 / 0.67:.4f} kg/kW-交付**（{mass_source['locator']}）。数值仍取决于架构，且部分来自未经独立验证的厂商声明。"
        reference_intro = "`ASSUMPTION_THIS_STUDY` 是项目内部假设记录，不是外部文献。以下列表只收录证据映射实际引用的外部资料，并按来源编号去重。"
        generated_note = "由可执行模型生成。价格年份：2024年实际英镑。估值基准：建设开始（t=0）。"
        section_labels = {
            "summary": "技术摘要",
            "scope": "研究问题、范围与核心定义",
            "chain": "从2 GW并网交付反推分阶段能量链",
            "method": "贴现现金流与成本边界",
            "costs": "参考成本由前期建设主导",
            "drivers": "比质量、发射与融资是最强单变量驱动",
            "thresholds": "单变量阈值说明进入目标区间所需条件",
            "external": "与已发表SBSP研究的关系",
            "validation": "验证、不确定性与剩余限制",
            "conclusion": "结论与下一步",
            "appendix_parameters": "附录A：完整参数登记表",
            "appendix_evidence": "附录B：外部证据映射",
            "appendix_version": "附录C：方法纠正与版本记录",
            "references": "参考文献",
        }
        headers = {
            "stage": ["阶段", "额定功率"],
            "capex": ["资本开支项目", "2024年实际英镑"],
            "lifecycle": ["生命周期项目", "贴现现值", "LCOE贡献"],
            "drivers": ["参数", "有利边界下LCOE", "相对参考情景降低"],
            "thresholds": ["目标LCOE", "单变量", "达到目标的条件"],
            "combined": ["目标", "等比例移动", "计算所得链路效率"],
            "external": ["研究", "公开成本背景", "与本模型一起阅读时的限制"],
            "parameters": ["参数", "参考值", "探索范围", "分母/边界", "限制"],
            "evidence": ["参数/论断", "证据角色", "外部来源与位置", "证据背景及可比性限制"],
        }
        chart_labels = ["参考情景生命周期LCOE构成", "单变量有利边界下的LCOE", "系统比质量敏感性", "等比例组合插值"]
        metadata = [
            f"副标题：{subtitle}",
            f"作者：{AUTHOR}",
            f"版本号：{VERSION}",
            f"报告日期：{REPORT_DATE_ZH}",
            f"证据截止日期：{EVIDENCE_DATE_ZH}",
            f"项目仓库：[{REPOSITORY_URL}]({REPOSITORY_URL})",
            f"交互模型：[{EXPLORER_URL}]({EXPLORER_URL})",
            f"建议引用：Gao, W. (2026). 英国空间太阳能成本条件评估, {VERSION}。",
            f"免责声明：{disclaimer}",
        ]
    else:
        title = "UK Space-Based Solar Power Cost-Condition Assessment"
        subtitle = "Delivered-grid LCOE thresholds under explicit technical and financial assumptions"
        disclaimer = "This is a conditional scenario result, not a commercial forecast, quotation, official UK target or proof of economic viability."
        executive = (
            f"This standalone report asks what a 2 GW grid-delivered UK space-based solar power system could cost under explicit, adjustable and auditable assumptions, and which variables most change that result. The reference scenario produces a conditional DCF LCOE of **£{result.lcoe_gbp_per_mwh:.2f}/MWh** in 2024 real GBP. It reconciles discounted lifecycle cost of **{_money(result.discounted_lifetime_cost_gbp)}** with **{result.discounted_lifetime_energy_mwh / 1e6:.2f} million MWh** of discounted delivered energy."
        )
        summary_items = [
            f"The reference case assumes 2 GW grid-delivered AC, {result.end_to_end_efficiency:.2%} end-to-end efficiency, {result.orbital_mass_kg / 1e6:.2f} million kg ({result.orbital_mass_kg / 1000:,.0f} tonnes) of orbital hardware and {result.required_launches:,} equivalent launches.",
            f"Discounted initial construction contributes about **£{initial_construction_lcoe:.2f}/MWh** and dominates the £{result.lcoe_gbp_per_mwh:.2f}/MWh result.",
            f"Within their separate explored ranges, favourable bounds for system specific mass, launch cost to staging orbit and the real discount rate reduce LCOE to **£{mass_floor:.1f}, £{launch_floor:.1f} and £{finance_floor:.1f}/MWh**, respectively. These are boundary sensitivities, not a jointly achievable design.",
            "UK and NASA studies likewise show strong dependence on architecture, launch, finance and combined favourable assumptions. Different system boundaries mean their cost ranges provide context and consistency checks, not validation of this model's £86.03/MWh result.",
        ]
        question_text = "The research question is: without presenting a scenario as a forecast, which technical, deployment, lifecycle and financing conditions move SBSP into this study's £80-120/MWh discussion region? The £80, £100, £120 and £150/MWh lines are analytical screens, not official UK targets."
        boundary_text = f"The system boundary works upstream from 2 GW AC at the grid connection point to incident solar power. Launch is priced per kg and covers staging orbit only. The staging service boundary is LEO; the final operational orbit is architecture-dependent high Earth orbit. The transfer proxy must cover the transfer vehicle, propellant, refuelling missions, operations and payload-performance penalty."
        core_headers = ["Core definition or assumption", "Reference case", "Interpretation"]
        core_rows = [
            ["Delivered capacity", "2.00 GW AC", "Rated AC power at the grid connection point"],
            ["Price basis", "2024 real GBP", "All model financial inputs and outputs"],
            ["Delivered capacity factor", f"{reference['capacity_factor']:.0%}", "Combined proxy for availability, outages and operating constraints"],
            ["Operating life", f"{reference['operating_lifetime_years']:.0f} years", "Full operating years after commissioning"],
            ["Real discount rate", f"{reference['real_discount_rate']:.1%}", "Discounted from start of construction at t=0"],
            ["System specific mass", f"{reference['system_specific_mass_kg_per_kw_delivered']:.1f} kg/kW-delivered", "Complete orbital hardware per kW delivered to the grid"],
            ["Launch cost", f"£{reference['launch_cost_gbp_per_kg_to_staging_orbit']:,.0f}/kg", "To staging orbit only"],
        ]
        financial_text = f"The headline metric is `LCOE = [sum_t C_t / (1+r)^t] / [sum_t E_t / (1+r)^t]`. The valuation base is start of construction at t=0. Four equal construction shares are spent before commissioning, and the first operating-year cash flow is at t=5. Operating life is {reference['operating_lifetime_years']:.0f} years; first-year delivered energy is {result.first_year_delivered_mwh / 1e6:.2f} TWh and lifetime-average annual delivered energy is {result.average_annual_delivered_mwh / 1e6:.2f} TWh. The simple CRF reconciliation is £{result.crf_reconciliation_lcoe_gbp_per_mwh:.2f}/MWh and is secondary because it does not reproduce the full construction timing."
        method_text = "Orbital mass equals delivered capacity (kW) x kg/kW-delivered; it is not divided by chain efficiency again. Space generation, RF transmission, rectenna and grid costs are assigned to their own rated-power denominators so that the same power or cost is not counted twice. Space replacement includes related hardware, launch, transfer and assembly; ground replacement includes rectenna and grid only. Fixed O&M excludes contingency, initial launch, transfer and assembly."
        profile_note = f"The default construction profile is `{list(result.construction_spend_profile)}` and sums to 100%. Programme contingency is applied once to initial CAPEX. Terminal decommissioning is a cost; residual value is credited at the end of operating life."
        cost_interpretation = f"Discounted initial construction contributes **£{initial_construction_lcoe:.2f}/MWh**, so the reference result is particularly exposed to upfront CAPEX, construction timing and finance. Other lifecycle items remain material but do not change the predominantly capital-intensive cost structure."
        threshold_intro = "The table reports the most decision-useful one-way thresholds. Each row changes one parameter while all other inputs remain at their reference values. It answers 'how far would this input alone need to move?' without claiming that the condition is achievable on a schedule."
        frontier_note = f"The reference case is already below £150, £120 and £100/MWh, so those targets show 0.0% movement in the equal-fraction table. The £80 and £60/MWh cases interpolate all parameters towards favourable bounds. This frontier is not a readiness score, probability, forecast, schedule or engineering roadmap."
        mass_note = "Specific mass affects launch, orbit transfer, in-orbit assembly and subsequent space replacement together; it is not equivalent to reducing a single hardware purchase cost. The plotted linearity follows the current per-kg boundary. A real mission would also face discrete launch counts, structural constraints and vehicle-integration limits."
        evidence_intro = "The report does not convert published scenarios into default model inputs. All 29 defaults are study-authored exploratory assumptions. External evidence provides technical context, range inspiration, definition checks or consistency comparisons only."
        evidence_interpretation = "The wide published range is itself evidence that SBSP cost cannot be discussed independently of architecture, maturity, finance and system boundary. This project's contribution is to expose continuous parameter thresholds, cost denominators and executable calculations, not to claim greater predictive accuracy than fixed-year architecture studies."
        test_note = "Automated validation covers reciprocal specific-power/specific-mass conversion, the 2 GW mass regression, no second efficiency division, all six power stages, rated-cost assignment, launch-mode exclusivity, launch rounding, replacement bases, construction shares, DCF/CRF convergence, zero-rate handling, invalid inputs, Python/browser parity, bilingual numerical parity and full regeneration."
        limit_items = [
            "No physical design of antenna area, frequency, beam geometry, sidelobes, power density, land, weather or safety constraints.",
            "No vehicle manifest, structural load, thermal, radiation, failure, spares, discrete replacement mission or detailed launch schedule.",
            "No tax, inflation, financing tranches, learning curves or architecture-parameter correlations.",
            "No GB dispatch, network reinforcement, balancing, capacity value or market-revenue model.",
            "Exploration bounds are not probability distributions; no P10/P50/P90 labels are produced, and favourable one-way bounds should not be treated as jointly most likely.",
        ]
        conclusion_text = f"Within this study boundary, the reference result of **£{result.lcoe_gbp_per_mwh:.2f}/MWh** sits inside the study-defined £80-120/MWh discussion region and below the £100/MWh screen. The model also shows that, with every other assumption held at its reference value, launch cost to staging orbit alone can cross the £80 or £60/MWh thresholds. That is a conditional sensitivity result, not a forecast of launch-vehicle maturity, project schedule, system safety or finance availability. The defensible conclusion is that SBSP has a quantifiable low-cost condition space; whether those conditions can coexist in one buildable architecture remains an engineering and finance question."
        next_steps = [
            "Replace exploratory system specific mass with an architecture-specific bill of materials, structural margin and grid-delivered specific power.",
            "Build a discrete launch manifest and orbit-transfer/refuelling plan, then test whether the per-kg price represents a procurable service.",
            "Add physical and regulatory constraints for beam design, rectenna, land, safety, weather and grid connection.",
            "Model discount rate, delay, failure and replacement as correlated uncertainties to produce P10/P50/P90 results.",
        ]
        migration_text = f"v1.x multiplied a 1.5 kg/kW value that should have been delivered-power-normalised by 'delivered power / efficiency', dividing by efficiency a second time. For 2 GW at 20% efficiency, the old expression gives **15,000,000 kg (15,000 tonnes)**; the corrected expression gives **3,000,000 kg (3,000 tonnes)**. With all other v2 comparison inputs identical, the erroneous mass boundary gives **£{old_example.lcoe_gbp_per_mwh:.2f}/MWh**, versus **£{new_example.lcoe_gbp_per_mwh:.2f}/MWh** on the corrected boundary. Historical v1.x thresholds are therefore not directly comparable with v2.0."
        source_note = f"The DESNZ/Frazer-Nash report defines architecture specific power as ground-delivered power per orbital mass. The reciprocal of 0.67 kW-delivered/kg is **{1 / 0.67:.4f} kg/kW-delivered** ({mass_source['locator']}). Values remain architecture-specific and may include manufacturer claims that were not independently verified."
        reference_intro = "`ASSUMPTION_THIS_STUDY` is the project's internal assumption record, not an external publication. The bibliography lists only external sources actually used in the evidence map, deduplicated by source ID."
        generated_note = f"Generated from the executable model. Price year: 2024 real GBP. Valuation base: {result.valuation_base}."
        section_labels = {
            "summary": "Technical summary",
            "scope": "Research question, scope and core definitions",
            "chain": "The stage-resolved chain required for 2 GW grid delivery",
            "method": "Discounted-cash-flow and cost boundaries",
            "costs": "Upfront construction dominates the reference cost",
            "drivers": "Specific mass, launch and finance are the strongest one-way drivers",
            "thresholds": "One-way thresholds quantify entry into lower-cost regions",
            "external": "Relationship to published SBSP studies",
            "validation": "Validation, uncertainty and remaining limitations",
            "conclusion": "Conclusion and next steps",
            "appendix_parameters": "Appendix A: Full parameter register",
            "appendix_evidence": "Appendix B: External evidence map",
            "appendix_version": "Appendix C: Methodological correction and version history",
            "references": "References",
        }
        headers = {
            "stage": ["Stage", "Rated power"],
            "capex": ["CAPEX component", "2024 real GBP"],
            "lifecycle": ["Lifecycle component", "Discounted present value", "LCOE contribution"],
            "drivers": ["Parameter", "LCOE at favourable bound", "Reduction from reference"],
            "thresholds": ["Target LCOE", "One-way parameter", "Condition that reaches target"],
            "combined": ["Target", "Equal-fraction movement", "Computed chain efficiency"],
            "external": ["Study", "Published cost context", "How to read it alongside this model"],
            "parameters": ["Parameter", "Reference", "Explored range", "Denominator / boundary", "Limitation"],
            "evidence": ["Parameter / claim", "Evidence role", "External source and locator", "Evidence context and comparability limit"],
        }
        chart_labels = ["Reference lifecycle LCOE components", "One-way LCOE at favourable bounds", "System specific-mass sensitivity", "Equal-fraction combined interpolation"]
        metadata = [
            f"Report subtitle: {subtitle}",
            f"Author: {AUTHOR}",
            f"Version: {VERSION}",
            f"Report date: {REPORT_DATE_EN}",
            f"Evidence reviewed through: {EVIDENCE_DATE_EN}",
            f"Repository: [{REPOSITORY_URL}]({REPOSITORY_URL})",
            f"Interactive model: [{EXPLORER_URL}]({EXPLORER_URL})",
            f"Recommended citation: Gao, W. (2026). UK Space-Based Solar Power Cost-Condition Assessment, {VERSION}.",
            f"Disclaimer: {disclaimer}",
        ]

    summary_bullets = "\n".join(f"- {item}" for item in summary_items)
    limit_bullets = "\n".join(f"- {item}" for item in limit_items)
    next_step_bullets = "\n".join(f"- {item}" for item in next_steps)
    metadata_text = "\n\n".join(metadata)

    text = f"""# {title} - {VERSION}

{metadata_text}

## {section_labels['summary']}

{executive}

{summary_bullets}

<!-- PAGEBREAK -->

## {section_labels['scope']}

{question_text}

{boundary_text}

{_table(core_headers, core_rows)}

## {section_labels['chain']}

{_table(headers['stage'], stage_rows)}

{'计算所得端到端效率' if language == 'zh' else 'Computed end-to-end efficiency'}: **{result.end_to_end_efficiency:.4%}**.

## {section_labels['method']}

{financial_text}

{method_text}

{profile_note}

## {section_labels['costs']}

{_table(headers['capex'], capex_rows)}

{_table(headers['lifecycle'], lifecycle_rows)}

![{chart_labels[0]}](../{figure_root}/reference_lcoe_components.png)

{cost_interpretation}

## {section_labels['drivers']}

{_table(headers['drivers'], driver_rows)}

![{chart_labels[1]}](../{figure_root}/one_way_lcoe_floors.png)

{'每根柱表示只把该参数移动到有利探索边界时的LCOE；其余输入保持参考值。较低的柱表示更强的单变量影响，而不是更高的实现概率。' if language == 'zh' else 'Each bar moves one parameter to its favourable explored bound while every other input remains at reference. A lower bar indicates a stronger one-way effect, not a higher probability of achievement.'}

## {section_labels['thresholds']}

{threshold_intro}

{_table(headers['thresholds'], threshold_rows)}

{_table(headers['combined'], combined_rows)}

{frontier_note}

![{chart_labels[2]}](../{figure_root}/specific_mass_threshold_focus.png)

{mass_note}

![{chart_labels[3]}](../{figure_root}/combined_progress_frontier.png)

## {section_labels['external']}

{evidence_intro}

{_table(headers['external'], external_comparison_rows)}

{evidence_interpretation}

## {section_labels['validation']}

{test_note}

{limit_bullets}

{generated_note}

## {section_labels['conclusion']}

{conclusion_text}

{'优先开展以下工作：' if language == 'zh' else 'Priority next steps:'}

{next_step_bullets}

<!-- PAGEBREAK -->

## {section_labels['appendix_parameters']}

{'该登记表保留全部29项默认值、探索范围、成本或功率分母及局限，供复核使用。正文结论不应脱离这些边界解释。' if language == 'zh' else 'This register preserves all 29 defaults, explored ranges, cost or power denominators and limitations for audit. The main findings should not be interpreted outside these boundaries.'}

{_table(headers['parameters'], parameter_rows)}

## {section_labels['appendix_evidence']}

{'下表把参数与论断连接到可核查的外部证据，并给出文档位置和可比性限制。除非明确标注，文献数值没有直接替换模型默认值。' if language == 'zh' else 'The table links parameters and claims to auditable external evidence, with document locators and comparability limits. Unless explicitly stated, published values do not replace model defaults.'}

{_table(headers['evidence'], evidence_map_rows)}

## {section_labels['appendix_version']}

{migration_text}

{source_note}

<!-- PAGEBREAK -->

## {section_labels['references']}

{reference_intro}

{reference_entries}
"""
    return text


def build_markdown_report(output_path: str | Path, reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows) -> None:
    Path(output_path).write_text(_report("en", reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows), encoding="utf-8")


def build_verification_note(output_path: str | Path, category_results: list[dict[str, str]], warnings: list[str], commands: list[str]) -> None:
    body = ["# v2.0 Verification Note", "", _table(["Category", "Status", "Evidence"], [[row["category"], row["status"], row["evidence"]] for row in category_results]), "", "## Warnings", ""]
    body.extend(f"- {warning}" for warning in warnings)
    body += ["", "## Commands", "", "```bash", *commands, "```", ""]
    Path(output_path).write_text("\n".join(body), encoding="utf-8")
