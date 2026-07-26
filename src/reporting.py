"""Bilingual Markdown report generation for the v2.0 methodology."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .model import calculate_lcoe
from .parameters import Parameter


VERSION = "v2.0"


def _money(value: float) -> str:
    return f"£{value / 1e9:,.2f}bn"


def _table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    values = [[str(cell) for cell in row] for row in rows]
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(row) + " |" for row in values),
    ])


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
    mass_source = next(item for item in evidence_rows if item["parameter_or_claim"] == "system_specific_mass_kg_per_kw_delivered" and item["source_id"] == "DESNZ_SBSP_2025")
    feasible = [row for row in thresholds if row.get("threshold_value") not in (None, "") and float(row["target_lcoe_gbp_per_mwh"]) < result.lcoe_gbp_per_mwh]
    top = importance[:8]
    combined = [row for row in combined_frontier if row.get("progress_fraction") not in (None, "")]
    if language == "zh":
        title = "英国空间太阳能成本条件评估"
        warning = "**这是条件情景结果，不是商业预测、报价、官方英国目标或经济可行性证明。**"
        executive = f"参考情景的条件性电网交付 DCF LCOE 为 **£{result.lcoe_gbp_per_mwh:.2f}/MWh**（2024年实际英镑）。模型从2 GW并网交流功率向上游反推五级能量链，计算端到端效率为 **{result.end_to_end_efficiency:.2%}**，轨道硬件质量为 **{result.orbital_mass_kg / 1e6:.2f}百万kg**，需要 **{result.required_launches:,}** 次等效发射。"
        sections = {
            "scope": "范围与结论",
            "migration": "v1.x 至 v2.0 迁移说明",
            "chain": "分阶段能量链",
            "finance": "贴现现金流边界",
            "costs": "参考成本构成",
            "analysis": "条件敏感性与阈值",
            "evidence": "参数证据与限制",
            "method": "公式、边界与验证",
            "limits": "仍然存在的限制",
        }
        stage_labels = {"incident_solar_power_w": "入射太阳功率", "space_dc_bus_power_w": "空间直流母线", "emitted_rf_power_w": "射频发射", "incident_rf_power_w": "整流天线入射射频", "rectenna_dc_power_w": "整流天线直流输出", "delivered_grid_ac_power_w": "并网交流交付"}
        capex_headers = ["资本开支项目", "2024年实际英镑"]
        lifecycle_headers = ["生命周期项目", "贴现现值", "LCOE贡献"]
        driver_headers = ["参数", "有利边界下LCOE", "降低幅度"]
        parameter_headers = ["参数", "参考值", "范围", "来源", "分母/边界", "限制"]
        migration_text = f"v1.x 把一个本应按交付功率定义的1.5 kg/kW数值乘以“交付功率/效率”，从而重复除以效率。在2 GW、20%效率示例中，旧公式得到 **15,000,000 kg（15,000吨）**；正确公式得到 **3,000,000 kg（3,000吨）**。在其余v2输入相同的对比计算中，错误质量边界对应 **£{old_example.lcoe_gbp_per_mwh:.2f}/MWh**，正确边界对应 **£{new_example.lcoe_gbp_per_mwh:.2f}/MWh**。因此历史v1.x阈值与v2.0不可直接比较。"
        source_note = f"DESNZ/Frazer-Nash报告把架构比功率定义为地面交付功率/轨道质量；0.67 kW-交付/kg 的倒数为 **{1/0.67:.4f} kg/kW-交付**。报告位置：{mass_source['locator']}。这些数值取决于架构，且部分来自未经独立验证的厂商声明。"
    else:
        title = "UK Space-Based Solar Power Cost-Condition Assessment"
        warning = "**This is a conditional scenario result, not a commercial forecast, quotation, official UK target or proof of economic viability.**"
        executive = f"The reference scenario gives a conditional delivered-grid DCF LCOE of **£{result.lcoe_gbp_per_mwh:.2f}/MWh** in 2024 real GBP. Working backwards from 2 GW AC at the grid boundary, the five-stage chain computes an end-to-end efficiency of **{result.end_to_end_efficiency:.2%}**, orbital hardware mass of **{result.orbital_mass_kg / 1e6:.2f} million kg**, and **{result.required_launches:,}** equivalent launches."
        sections = {"scope": "Scope and answer", "migration": "Migration from v1.x to v2.0", "chain": "Stage-resolved energy chain", "finance": "Discounted-cash-flow boundary", "costs": "Reference cost structure", "analysis": "Conditional sensitivities and thresholds", "evidence": "Parameter evidence and limitations", "method": "Formulae, boundaries and validation", "limits": "Remaining limitations"}
        stage_labels = {"incident_solar_power_w": "Incident solar", "space_dc_bus_power_w": "Space DC bus", "emitted_rf_power_w": "Emitted RF", "incident_rf_power_w": "RF incident on rectenna", "rectenna_dc_power_w": "Rectenna DC output", "delivered_grid_ac_power_w": "Grid-delivered AC"}
        capex_headers = ["CAPEX component", "2024 real GBP"]
        lifecycle_headers = ["Lifecycle component", "Discounted PV", "LCOE contribution"]
        driver_headers = ["Parameter", "LCOE at favourable bound", "Reduction"]
        parameter_headers = ["Parameter", "Reference", "Range", "Source", "Denominator / boundary", "Limitation"]
        migration_text = f"v1.x multiplied a 1.5 kg/kW value that should have been delivered-power-normalised by 'delivered power / efficiency', dividing by efficiency a second time. For 2 GW at 20% efficiency, the old expression gives **15,000,000 kg (15,000 tonnes)**; the corrected expression gives **3,000,000 kg (3,000 tonnes)**. With all other v2 comparison inputs identical, the erroneous mass boundary gives **£{old_example.lcoe_gbp_per_mwh:.2f}/MWh**, versus **£{new_example.lcoe_gbp_per_mwh:.2f}/MWh** on the corrected boundary. Historical v1.x thresholds are therefore not directly comparable with v2.0."
        source_note = f"The DESNZ/Frazer-Nash report defines architecture specific power as ground-delivered power per orbital mass. The reciprocal of 0.67 kW-delivered/kg is **{1/0.67:.4f} kg/kW-delivered** ({mass_source['locator']}). Values remain architecture-specific and may include manufacturer claims that were not independently verified."

    stage_rows = [[stage_labels[name], f"{value / 1e9:,.2f} GW"] for name, value in result.energy_chain_power_w.items()]
    capex_labels_zh = {"space_generation_hardware": "空间发电硬件", "wireless_power_transmitter": "射频发射硬件", "launch_to_staging_orbit": "发射至集结轨道", "orbit_transfer_to_operational_orbit": "转移至运行轨道", "in_orbit_assembly_and_deployment": "在轨组装与部署", "rectenna": "整流天线", "grid_connection": "并网连接"}
    lifecycle_labels_zh = {"initial_construction": "初始建设", "fixed_opex": "固定运维", "variable_opex": "可变运维", "space_hardware_replacement": "空间硬件更换", "ground_hardware_replacement": "地面硬件更换", "decommissioning": "退役", "residual_value": "残值"}
    capex_rows = [[capex_labels_zh[name] if language == "zh" else name.replace("_", " ").title(), _money(value)] for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)]
    capex_rows += [["Programme contingency" if language == "en" else "项目预备费", _money(result.programme_contingency_gbp)], ["Initial CAPEX" if language == "en" else "初始资本开支", _money(result.initial_capex_gbp)]]
    lifecycle_rows = [[lifecycle_labels_zh[name] if language == "zh" else name.replace("_", " ").title(), _money(value), f"£{value / result.discounted_lifetime_energy_mwh:,.2f}/MWh"] for name, value in sorted(result.lifecycle_cost_components_pv_gbp.items(), key=lambda item: abs(item[1]), reverse=True)]
    driver_rows = [[params[str(row["parameter"])].display_name_zh if language == "zh" else row["display_name"], f"£{float(row['best_lcoe_gbp_per_mwh']):.1f}/MWh", f"£{float(row['lcoe_reduction_gbp_per_mwh']):.1f}/MWh"] for row in top]
    parameter_rows = [[parameter.display_name_zh if language == "zh" else parameter.display_name, f"{parameter.reference_value:g} {parameter.unit}", f"{parameter.min_value:g}–{parameter.max_value:g}", f"{parameter.source_type} / {parameter.source_id}", parameter.denominator_definition_zh if language == "zh" else parameter.denominator_definition, parameter.notes_zh if language == "zh" else parameter.notes] for parameter in params.values()]

    if language == "zh":
        financial_text = f"主指标采用 LCOE = Σ(Cₜ/(1+r)ᵗ) / Σ(Eₜ/(1+r)ᵗ)。估值基准是建设开始t=0；默认4年建设支出为等额份额，调试完成后的首个运行年现金流位于t=5。运行寿命为{reference['operating_lifetime_years']:.0f}年，首年交付电量为{result.first_year_delivered_mwh/1e6:.2f} TWh，年均交付电量为{result.average_annual_delivered_mwh/1e6:.2f} TWh。贴现生命周期成本为{_money(result.discounted_lifetime_cost_gbp)}，贴现电量为{result.discounted_lifetime_energy_mwh/1e6:.2f}百万MWh。简单CRF对账指标为£{result.crf_reconciliation_lcoe_gbp_per_mwh:.2f}/MWh，仅作次要核对。"
        boundary_text = f"发射计价模式：按kg且只计至集结轨道。集结轨道：{result.staging_orbit}。运行轨道：{result.operational_orbit}。转移代理必须覆盖转移器、推进剂、补给任务、运行和载荷性能惩罚。"
        method_text = "质量公式：轨道质量 = 交付容量(kW) × kg/kW-交付。硬件成本分别按空间直流母线W、射频发射W、交付W或交付kW计价，边界互斥。空间更换成本包含硬件及相关发射、转移和组装；地面更换仅含整流天线和并网。固定运维基数不含预备费、初始发射、转移和组装。"
        computed_label = "计算所得端到端效率"
        frontier_note = "等比例前沿只是一种数学插值工具，不是成熟度评分、概率、预测、进度表或工程路线图。"
        combined_headers = ["目标", "等比例移动", "计算所得链路效率"]
        evidence_intro = "以下每个面向用户的数值输入都包含来源类型、来源编号、相关价格年份、分母定义和限制说明。"
        profile_note = f"默认建设支出曲线为 `{list(result.construction_spend_profile)}`，合计100%。项目预备费只应用于初始资本开支一次。期末退役是成本，残值是在运行寿命结束时的抵扣。"
        test_note = "测试覆盖比质量倒数换算、2 GW / 0.67 kW/kg回归、不重复除以效率、全部六级功率、额定成本分配、发射模式互斥、发射次数取整、更换基数、建设支出份额、DCF/CRF收敛、零贴现率、无效输入、Python/浏览器一致性、中英数值一致性、历史质量标识移除及完整重建。"
        generated_note = f"由可执行模型生成。价格年份：2024年实际英镑。估值基准：{result.valuation_base}。"
        chart_lifecycle, chart_floors, chart_mass, chart_combined = "参考情景生命周期LCOE构成", "单变量成本下限", "比质量敏感性", "等比例数学插值"
        limit_items = ["没有天线面积、频率、波束几何、旁瓣、功率密度、土地、天气或安全约束的物理设计。", "没有飞行器清单、结构载荷、热控、辐射、故障、备件、离散更换任务或详细发射排程。", "没有税务、通胀、融资分层、学习曲线或架构参数相关性。", "没有英国电力系统调度、网络增强、平衡、容量价值或市场收入模型。", "探索范围不是概率分布；不输出P10/P50/P90。"]
    else:
        financial_text = f"The headline uses LCOE = Σ(Cₜ/(1+r)ᵗ) / Σ(Eₜ/(1+r)ᵗ). The valuation base is start of construction at t=0; four equal construction shares are spent before commissioning, and the first operating-year cash flow is at t=5. The operating life is {reference['operating_lifetime_years']:.0f} years. First-year energy is {result.first_year_delivered_mwh/1e6:.2f} TWh and lifetime-average annual energy is {result.average_annual_delivered_mwh/1e6:.2f} TWh. Discounted lifecycle cost is {_money(result.discounted_lifetime_cost_gbp)} and discounted energy is {result.discounted_lifetime_energy_mwh/1e6:.2f} million MWh. The simple CRF reconciliation is £{result.crf_reconciliation_lcoe_gbp_per_mwh:.2f}/MWh and is secondary only."
        boundary_text = f"Launch pricing mode: per kg, to staging orbit only. Staging orbit: {result.staging_orbit}. Operational orbit: {result.operational_orbit}. The transfer proxy must cover transfer vehicle, propellant, refuelling missions, operations and payload-performance penalty."
        method_text = "Mass is orbital mass = delivered capacity (kW) × kg/kW-delivered. Hardware costs are rated independently at space-DC-bus W, emitted-RF W, delivered W or delivered kW, with mutually exclusive boundaries. Space replacement includes hardware plus associated launch, transfer and assembly; ground replacement includes only rectenna and grid. Fixed O&M excludes contingency, initial launch, transfer and assembly."
        computed_label = "Computed end-to-end efficiency"
        frontier_note = "The equal-fraction frontier is a mathematical interpolation device, not a readiness score, probability, forecast, schedule or engineering roadmap."
        combined_headers = ["Target", "Equal-fraction movement", "Computed chain efficiency"]
        evidence_intro = "Every user-facing numerical input below carries source type, source ID, price year where relevant, denominator and limitation metadata."
        profile_note = f"The default construction profile is `{list(result.construction_spend_profile)}` and sums to 100%. Programme contingency is applied once to initial CAPEX. Terminal decommissioning is a cost and residual value is a credit at the end of operating life."
        test_note = "The test suite checks reciprocal mass conversion, the 2 GW / 0.67 kW/kg regression, no second efficiency division, all six stage powers, rated-cost assignment, launch-mode exclusivity, launch rounding, replacement bases, construction shares, DCF/CRF convergence, zero-rate handling, invalid inputs, Python/browser parity, bilingual parity, removal of the historical mass identifier and full regeneration."
        generated_note = f"Generated from the executable model. Price year: 2024 real GBP. Valuation base: {result.valuation_base}."
        chart_lifecycle, chart_floors, chart_mass, chart_combined = "Reference lifecycle LCOE components", "One-way floors", "Mass sensitivity", "Combined interpolation"
        limit_items = ["No physical design of antenna area, frequency, beam geometry, sidelobes, power density, land, weather or safety constraints.", "No vehicle manifest, structural load, thermal, radiation, failure, spares, discrete replacement mission or detailed launch schedule.", "No tax, inflation, financing tranches, learning curves or architecture-parameter correlations.", "No GB dispatch, network reinforcement, balancing, capacity value or market-revenue model.", "Exploration bounds are not probability distributions; no P10/P50/P90 labels are produced."]

    target_summary = ", ".join(f"£{float(row['target_lcoe_gbp_per_mwh']):.0f}: {(params[str(row['parameter'])].display_name_zh if language == 'zh' else row['display_name'])}={float(row['threshold_value']):.4g}" for row in feasible[:8]) or ("探索边界内没有单变量达到目标。" if language == "zh" else "No one-way target reached within explored bounds.")
    combined_rows = [[f"£{float(row['target_lcoe_gbp_per_mwh']):.0f}/MWh", f"{float(row['progress_fraction']):.1%}", f"{float(row['computed_end_to_end_efficiency']):.2%}"] for row in combined]
    text = f"""# {title} — {VERSION}

{warning}

## {sections['scope']}

{executive}

{boundary_text}

## {sections['migration']}

{migration_text}

{source_note}

## {sections['chain']}

{_table(['Stage' if language == 'en' else '阶段', 'Rated power' if language == 'en' else '额定功率'], stage_rows)}

{computed_label}: **{result.end_to_end_efficiency:.4%}**.

## {sections['finance']}

{financial_text}

## {sections['costs']}

{_table(capex_headers, capex_rows)}

{_table(lifecycle_headers, lifecycle_rows)}

![{chart_lifecycle}](../{'figures_zh' if language == 'zh' else 'figures'}/reference_lcoe_components.png)

## {sections['analysis']}

{_table(driver_headers, driver_rows)}

{target_summary}

{frontier_note}

{_table(combined_headers, combined_rows)}

![{chart_floors}](../{'figures_zh' if language == 'zh' else 'figures'}/one_way_lcoe_floors.png)

![{chart_mass}](../{'figures_zh' if language == 'zh' else 'figures'}/specific_mass_threshold_focus.png)

![{chart_combined}](../{'figures_zh' if language == 'zh' else 'figures'}/combined_progress_frontier.png)

## {sections['evidence']}

{evidence_intro}

{_table(parameter_headers, parameter_rows)}

## {sections['method']}

{method_text}

{profile_note}

{test_note}

## {sections['limits']}

"""
    text += "\n".join(f"- {item}" for item in limit_items)
    text += f"\n\n{generated_note}\n"
    return text


def build_markdown_report(output_path: str | Path, reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows) -> None:
    Path(output_path).write_text(_report("en", reference, params, generation_rows, system_rows, thresholds, importance, frontier, combined_frontier, alternative_frontiers, source_rows, evidence_rows, assumption_rows, external_study_rows), encoding="utf-8")


def build_verification_note(output_path: str | Path, category_results: list[dict[str, str]], warnings: list[str], commands: list[str]) -> None:
    body = ["# v2.0 Verification Note", "", _table(["Category", "Status", "Evidence"], [[row["category"], row["status"], row["evidence"]] for row in category_results]), "", "## Warnings", ""]
    body.extend(f"- {warning}" for warning in warnings)
    body += ["", "## Commands", "", "```bash", *commands, "```", ""]
    Path(output_path).write_text("\n".join(body), encoding="utf-8")
