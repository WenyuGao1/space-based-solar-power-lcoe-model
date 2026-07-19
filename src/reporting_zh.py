"""Generate the Chinese v1.2 analytical report from the shared report facts."""

from __future__ import annotations

from pathlib import Path

from .parameters import Parameter
from .reporting import (
    CORE_PARAMETER_NAMES,
    EVIDENCE_REVIEW_DATE,
    REPORT_VERSION,
    derive_report_facts,
    format_cost_range,
    markdown_table,
    threshold_summary_rows,
)


PARAMETER_LABELS_ZH = {
    "delivered_capacity_mw": "并网交付容量",
    "end_to_end_efficiency": "端到端效率",
    "capacity_factor": "交付容量因子（模型代理变量）",
    "specific_mass_kg_per_kw_space_power": "整套轨道系统比质量",
    "launch_cost_gbp_per_kg": "发射成本",
    "space_hardware_cost_gbp_per_w_space": "空间段硬件成本",
    "wireless_power_transmission_cost_gbp_per_w_space": "无线输电硬件成本",
    "in_orbit_assembly_cost_gbp_per_kg": "在轨组装与部署成本",
    "orbit_transfer_cost_gbp_per_kg": "轨道转移成本",
    "rectenna_cost_gbp_per_w_delivered": "整流天线资本开支",
    "grid_connection_cost_gbp_per_kw_delivered": "并网成本",
    "programme_margin_pct": "项目裕度/预备费",
    "replacement_refurbishment_pct_capex_per_year": "更换与翻新预留",
    "fixed_opex_pct_capex_per_year": "固定运维",
    "variable_opex_gbp_per_mwh": "可变运维",
    "wacc": "实际项目贴现率代理变量",
    "system_lifetime_years": "系统经济寿命",
}

PARAMETER_ROLES_ZH = {
    "delivered_capacity_mw": "规模锚点；多数单位成本随容量线性变化",
    "end_to_end_efficiency": "决定所需空间端功率以及相应质量",
    "capacity_factor": "综合可用率、停机和运行约束的交付电量代理变量",
    "specific_mass_kg_per_kw_space_power": "同时放大发射、轨道转移和组装成本",
    "launch_cost_gbp_per_kg": "到模型所定义中转轨道的运输成本杠杆",
    "space_hardware_cost_gbp_per_w_space": "轨道硬件制造成本杠杆",
    "in_orbit_assembly_cost_gbp_per_kg": "随轨道质量缩放的部署成本预留",
    "wacc": "用于资本回收计算的实际项目贴现率代理变量",
    "system_lifetime_years": "资本成本摊销期限",
}

CAPEX_LABELS_ZH = {
    "space_segment_capex": "空间段硬件",
    "wireless_power_transmission": "无线输电硬件",
    "launch": "发射",
    "orbit_transfer": "轨道转移",
    "in_orbit_assembly": "在轨组装与部署",
    "rectenna": "整流天线",
    "grid_connection": "本地并网",
}

SOURCE_ROLE_ZH = {
    "UK generation benchmark source": "英国发电成本基准",
    "UK generation benchmark input workbook": "英国发电成本基准输入工作簿",
    "Supplementary UK benchmark source": "英国补充基准",
    "System-adjusted benchmark source": "系统调整成本基准",
    "Market context": "市场背景",
    "System-cost evidence": "系统成本证据",
    "Historical SBSP context": "历史背景",
    "External SBSP study": "外部空间太阳能研究",
    "External SBSP study landing page": "外部空间太阳能研究入口",
    "External SBSP economic study": "外部空间太阳能经济研究",
    "External SBSP input evidence": "外部空间太阳能输入证据",
    "SBSP technical context": "空间太阳能技术背景",
    "Nuclear benchmark context": "核电基准背景",
    "Model assumption source": "本项目假设来源",
}

EVIDENCE_ROLE_ZH = {
    "contextual range": "背景范围",
    "external consistency check": "外部一致性核对",
    "technical context": "技术背景",
    "external comparison": "外部比较",
    "financing context": "融资背景",
    "scope qualification": "适用范围限定",
    "system context": "系统价值背景",
    "benchmark definition": "基准定义",
}

UNIT_LABELS_ZH = {
    "fraction": "比例",
    "fraction/year": "占CAPEX比例/年",
    "years": "年",
    "kg/kW-space": "kg/kW-空间端",
    "GBP/kg": "英镑/kg",
    "GBP/kg to staging orbit": "英镑/kg至中转轨道",
    "GBP/W-space": "英镑/W-空间端",
    "GBP/W-delivered": "英镑/W-交付端",
    "GBP/kW-delivered": "英镑/kW-交付端",
    "GBP/MWh": "英镑/MWh",
}

TECHNOLOGY_LABELS_ZH = {
    "Large-scale solar": "大型光伏",
    "Onshore wind": "陆上风电",
    "Fixed offshore wind": "固定式海上风电",
    "Floating offshore wind": "浮式海上风电",
    "Gas CCGT high load factor": "高负荷率燃气联合循环",
    "Gas with CCUS high load factor": "高负荷率燃气CCUS",
    "Gas with CCUS mid load factor": "中负荷率燃气CCUS",
    "Nuclear Hinkley Point C public contract marker": "Hinkley Point C核电公开合同价格点",
}

PRICE_BASIS_ZH = {
    "2024 real GBP": "2024年实际英镑",
    "2012 real-price terms (CPI-indexed)": "以2012年价格表述并按CPI调整",
    "2018 real GBP": "2018年实际英镑",
}

VALUE_TYPE_ZH = {
    "DESNZ 2025 Annex A 2030-2035 range": "DESNZ 2025附录A的2030–2035年区间",
    "Contract for Difference strike-price marker": "差价合约执行价背景点",
    "35-year Contract for Difference strike-price marker": "35年差价合约执行价背景点",
}

ASSUMPTION_ZH = {
    "A1": ("分析定位", "本研究是成本条件评估，不给出空间太阳能投产年份预测。", "外部资料中的年份不被移植为本项目情景。"),
    "A2": ("单位与价格口径", "模型财务输入和输出均按2024年实际英镑解释，LCOE统计到并网连接点。", "其他价格基年的外部数据只明确标注，不做隐含换算。"),
    "A3": ("效率边界", "固定并网容量时，端到端效率通过改变所需空间端功率进入模型。", "所有子系统损耗被合并为一个连续变量。"),
    "A4": ("质量边界", "比质量作用于完整空间端功率规模。", "未拆分阵列、结构和发射天线等子系统质量。"),
    "A5": ("项目裕度", "项目裕度施加于全部裕度前初始资本开支。", "未单独估算业主成本、建设期保险和首台套开发成本。"),
    "A6": ("翻新", "更换与翻新按初始资本开支的年度比例计提。", "未优化大修周期。"),
    "A7": ("系统成本", "系统调整参照采用BEIS 2020增强LCOE范围。", "属于2018年实际英镑下的情景性指示区间。"),
    "A8": ("核电", "核电只保留公开合同价格背景点。", "它不是通用核电LCOE，也不与2024年实际价格直接同口径。"),
    "A9": ("条件门槛", "所谓必要条件只在本模型、会计边界和参数范围内成立。", "替代架构、联动变化或遗漏的系统价值都可能改变门槛。"),
    "A10": ("外部比较", "外部空间太阳能成本用于背景和一致性核对，不作为本模型验证。", "架构、轨道、价格年份、融资和成本边界存在实质差异。"),
    "A11": ("贴现率", "变量wacc实际实现为资本回收公式中的实际项目贴现率代理变量。", "不能视作定义完整的企业税前或税后WACC。"),
    "A12": ("交付边界", "模型终点是并网连接点，容量因子综合可用率、停机和运行限制。", "不含下游输电扩建、平衡、储能、可靠性服务和系统价值。"),
}


def _figure(title: str, path: str, interpretation: str) -> str:
    return f"![{title}]({path})\n\n**解读。** {interpretation}"


def _format_parameter(parameter: Parameter) -> str:
    value = parameter.reference_value
    if parameter.unit in {"fraction", "fraction/year"}:
        return f"{value:.1%}"
    if parameter.unit == "kg/kW-space":
        return f"{value:.2f} kg/kW-空间端"
    if parameter.unit == "GBP/W-space":
        return f"£{value:.2f}/W-空间端"
    if parameter.unit == "GBP/W-delivered":
        return f"£{value:.2f}/W-交付"
    if parameter.unit == "GBP/kg to staging orbit":
        return f"£{value:,.0f}/kg（至中转轨道）"
    if parameter.unit.startswith("GBP/"):
        return f"£{value:,.0f}/{parameter.unit.split('/', 1)[1]}"
    if parameter.unit == "MW":
        return f"{value:,.0f} MW"
    if parameter.unit == "years":
        return f"{value:,.0f} 年"
    return f"{value:g} {parameter.unit}"


def _threshold_rows_zh(thresholds: list[dict[str, object]]) -> list[list[object]]:
    rows = threshold_summary_rows(thresholds)
    result: list[list[object]] = []
    name_by_display = {
        params_display: PARAMETER_LABELS_ZH.get(parameter, params_display)
        for parameter, params_display in [
            (str(row["parameter"]), str(row["display_name"])) for row in thresholds
        ]
    }
    for row in rows:
        result.append(
            [
                name_by_display.get(str(row[0]), row[0]),
                UNIT_LABELS_ZH.get(str(row[1]), row[1]),
                *row[2:],
            ]
        )
    return result


def build_markdown_report_zh(
    output_path: str | Path,
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
) -> None:
    facts = derive_report_facts(
        reference,
        thresholds,
        importance,
        combined_frontier,
        generation_rows,
        system_rows,
    )
    result = facts.result

    core_rows = [
        [PARAMETER_LABELS_ZH[name], _format_parameter(params[name]), PARAMETER_ROLES_ZH[name]]
        for name in CORE_PARAMETER_NAMES
    ]
    capex_rows = [
        [CAPEX_LABELS_ZH.get(name, name), f"£{value / 1e9:.2f}bn"]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_rows.extend(
        [
            ["项目裕度前小计", f"£{result.pre_margin_capex_gbp / 1e9:.2f}bn"],
            ["项目裕度", f"£{result.programme_margin_gbp / 1e9:.2f}bn"],
            ["初始资本开支", f"£{result.initial_capex_gbp / 1e9:.2f}bn"],
        ]
    )

    decision_rows = [
        ["£150/MWh", "本研究定义的宽口径筛选线", "不是英国官方门槛"],
        ["£100–120/MWh", "用于筛选潜在稳定或近稳定电源角色的研究定义区间", "进入更深入工程、融资与系统价值评估"],
        ["£80/MWh", "与所选系统调整参照开始重叠", "仍不等于具备市场竞争力"],
        ["£60/MWh", "严格压力测试", "测试的一维输入均未达到；联合案例仍属探索性"],
    ]

    benchmark_rows: list[list[object]] = []
    for row in generation_rows:
        if row.get("value_low_gbp_per_mwh") in (None, ""):
            continue
        benchmark_rows.append(
            [
                TECHNOLOGY_LABELS_ZH.get(str(row["technology"]), row["technology"]),
                format_cost_range(
                    float(row["value_low_gbp_per_mwh"]),
                    float(row["value_high_gbp_per_mwh"]),
                ),
                PRICE_BASIS_ZH.get(str(row["price_basis"]), row["price_basis"]),
                VALUE_TYPE_ZH.get(str(row["value_type"]), row["value_type"]),
            ]
        )
    system_row = next(row for row in system_rows if row["technology"] == "High-renewable system-adjusted band")
    benchmark_rows.append(
        [
            "高比例新能源系统调整区间",
            format_cost_range(
                float(system_row["value_low_gbp_per_mwh"]),
                float(system_row["value_high_gbp_per_mwh"]),
            ),
            "2018年实际英镑",
            "指示性增强LCOE包络",
        ]
    )

    mass_150 = facts.mass_thresholds[150]
    mass_120 = facts.mass_thresholds[120]
    mass_100 = facts.mass_thresholds[100]
    if mass_150 is None or mass_120 is None or mass_100 is None:
        raise ValueError("缺少预期的比质量门槛。")

    frontier_rows = []
    for row in frontier:
        efficiency = float(row["end_to_end_efficiency"])
        target = int(row["target_lcoe_gbp_per_mwh"])
        if efficiency not in {0.25, 0.30, 0.35} or target not in {150, 120, 100}:
            continue
        launch_value = row["max_launch_cost_gbp_per_kg"]
        frontier_rows.append(
            [
                f"{efficiency:.0%}",
                f"£{target}/MWh",
                "探索范围内未达到" if launch_value in (None, "") else f"不高于£{float(launch_value):.1f}/kg",
            ]
        )

    combined_rows = []
    for target in sorted(facts.combined_rows, reverse=True):
        row = facts.combined_rows[target]
        if row.get("status") != "feasible":
            combined_rows.append([f"£{target}/MWh", "未达到", "—", "—", "—", "—"])
            continue
        combined_rows.append(
            [
                f"£{target}/MWh",
                f"{float(row['progress_fraction']):.1%}",
                f"£{float(row['launch_cost_gbp_per_kg']):.0f}/kg",
                f"{float(row['specific_mass_kg_per_kw_space_power']):.2f} kg/kW-空间端",
                f"{float(row['end_to_end_efficiency']):.1%}",
                f"{float(row['wacc']):.2%}",
            ]
        )

    external_zh = {
        "UK_SBSP_2021_PHASE2": (
            "英国空间太阳能二阶段经济研究（2021）",
            "架构与未来情景研究",
            "2018年价格：£35–79/MWh，中央估计约£50/MWh；2 GW CASSIOPeiA、30年寿命、20%门槛收益率、2040投运情景",
            "提供架构和情景背景；本项目补充连续的模型条件门槛",
        ),
        "DESNZ_SBSP_2025": (
            "英国小规模空间太阳能研究（2025年完成、2026年发布）",
            "架构、路径与系统价值研究",
            "2024年实际英镑：2030年£335–595/MWh、2035年£154–249/MWh、2040年£87–129/MWh",
            "提供当前外部一致性核对和具体架构驱动因素；本项目增加可审计的参数空间图",
        ),
        "NASA_OTPS_SBSP_2024": (
            "NASA OTPS评估（2024）",
            "全生命周期成本与排放评估",
            "FY2022美元：RD1/RD2基线分别为$610/$1,590/MWh；组合有利假设下为$30/$80/MWh",
            "说明在NASA所选案例中，架构与组合假设可使生命周期成本变化约20倍；NASA数值未导入本模型",
        ),
        "ASSUMPTION_THIS_STUDY": (
            "本项目（v1.2）",
            "可复现连续成本条件分析",
            "本研究自定参考锚点£429/MWh；以数值求根得到£150/120/100/80/60每MWh条件线",
            "独特贡献是可追溯、可执行、中英双语的条件图，而不是更准预测",
        ),
    }
    external_rows = []
    for row in external_study_rows:
        labels = external_zh.get(row["source_id"])
        if labels is None:
            raise ValueError(f"缺少外部研究中文映射: {row['source_id']}")
        external_rows.append([labels[0], labels[1], labels[2], labels[3]])

    evidence_rows_zh = [
        [
            row["parameter_or_claim_zh"],
            f"{row['evidence_role_zh']} / {row['source_id']}",
            row["locator"],
            row["numeric_context_zh"],
            row["limitations_zh"],
        ]
        for row in evidence_rows
    ]
    source_rows_zh = [
        [
            row["source_id"],
            f"[{row['title']}]({row['url'] if row['url'].startswith('http') else '../report/final_report_zh.md'})",
            row["organization"],
            SOURCE_ROLE_ZH.get(row["role"], row["role"]),
        ]
        for row in source_rows
    ]
    assumptions_zh = []
    for row in assumption_rows:
        translated = ASSUMPTION_ZH.get(row["assumption_id"])
        if translated is None:
            assumptions_zh.append([row["assumption_id"], row["area"], row["assumption"], row["limitation"]])
        else:
            assumptions_zh.append([row["assumption_id"], *translated])

    alt_pathways = len({str(row["pathway"]) for row in alternative_frontiers})
    report = f"""# 英国空间太阳能成本条件图

副标题：面向英国决策筛选的可复现门槛评估——不是部署预测

证据状态：来源登记表复核至{EVIDENCE_REVIEW_DATE}；已对选定的官方DESNZ基准单元格进行程序对账。

版本号：v{REPORT_VERSION}

说明：中英文内容由同一组结构化数据和模型结果生成。

免责声明：本报告识别模型条件下的成本要求，不证明工程可实现性，不预测投产年份，不估算投资回报，也不构成投资建议。

<!-- PAGEBREAK -->

## 目录

- 1. 执行结论
- 2. 研究问题与本项目的特殊贡献
- 3. 范围、会计边界与方法
- 4. 证据质量与来源纪律
- 5. 参考锚点与成本结构
- 6. 英国成本参照
- 7. 一维条件门槛
- 8. 联合成本条件前沿
- 9. 对英国决策的含义
- 10. 局限、稳健性与不作出的主张
- 11. 结论
- 附录A–C：证据、来源与假设审计表

<!-- PAGEBREAK -->

## 1. 执行结论

最通俗的结论是：**参考配置很贵，但本项目的价值在于把“为什么贵、要改变到什么程度”算清楚。** 在本研究自定的参考点上，并网连接点LCOE为**£{result.lcoe_gbp_per_mwh:.0f}/MWh**。它只是统一比较用的锚点，不是预测，也不是推荐方案。

表1. 本研究定义的成本线及其含义

{markdown_table(["成本线", "本项目中的用途", "决策含义与限制"], decision_rows)}

在本模型边界和所选范围内、其余输入全部固定时，比质量是最强的一维杠杆。达到£150、£120和£100/MWh时，整套轨道系统比质量分别不能高于{mass_150:.2f}、{mass_120:.2f}和{mass_100:.2f} kg/kW-空间端。探索范围内，单独改变比质量仍达不到£80或£60/MWh。

仅降低发射成本并不够：即使降到探索下界£{params['launch_cost_gbp_per_kg'].min_value:.0f}/kg，LCOE仍约为£{facts.best_lcoe['launch_cost_gbp_per_kg']:.0f}/MWh。仅把端到端效率提高到{params['end_to_end_efficiency'].max_value:.0%}，LCOE仍约为£{facts.best_lcoe['end_to_end_efficiency']:.0f}/MWh。因此，应测试质量、发射、空间硬件、组装、融资、效率和交付电量之间的多种联动组合；本模型没有证明每个变量都必须改变。

本项目的贡献**不是预测得更准**，而是更透明、可复现地回答一个更窄的问题：在明确写出的模型里，空间太阳能进入英国相关决策区间，需要满足什么成本与性能条件？

## 2. 研究问题与本项目的特殊贡献

本报告审阅的代表性研究主要评估具体架构、未来年份情景、生命周期影响或系统路径。本项目与它们互补：用连续的一维和联合参数前沿，直接显示达到与达不到的条件，并把假设、来源和计算过程完整公开。

表2. 本项目与所选既有空间太阳能研究的关系

{markdown_table(["研究", "主要分析类型", "公开成本背景", "与本项目的关系"], external_rows)}

本项目可以公开说明的优势是：

- 所有精确模型输入都归类为**本研究自定的探索性假设**；外部文献数值单独放在证据对应表中。
- 门槛采用高精度单调二分求根，不再把绘图网格精度误当成数值精度。
- 对{facts.parameter_count}个变量和{facts.target_count}条研究自定成本线，同时报告“能达到”和“范围内达不到”的结果。
- 联合前沿和{alt_pathways}条替代参数切片说明，这不是只靠发射成本的故事。
- 数据、模型、图表、中英文报告和自动检查可以用一条命令重新生成。

因此，本项目对于“成本条件是什么”这个问题更透明，但不能声称普遍比具体架构研究更准确。

## 3. 范围、会计边界与方法

模型终点是**并网连接点**。模型包含空间硬件、无线输电硬件、发射、轨道转移、在轨组装、整流天线、本地并网、项目裕度、资本回收、固定运维、翻新和可变运维；不包含下游输电扩建、平衡、储能、弃电、可靠性服务、税务、退役成本、收入机制和已货币化的系统价值。

全部模型财务输入按2024年实际英镑解释。变量`wacc`实际是资本回收公式中的**实际项目贴现率代理变量**；税务、通胀和融资分层不在模型内。容量因子也是交付电量代理变量，综合可用率、停机和运行约束，并不是空间太阳能的实测可用率。

计算关系为：

- 年交付电量 = 并网容量 × 8,760小时 × 交付容量因子；
- 所需空间端功率 = 并网容量 ÷ 端到端效率；
- 轨道质量 = 空间端功率 × 整套架构比质量；
- 初始资本开支 = 各项资本开支之和 ×（1 + 项目裕度）；
- LCOE =（年化资本开支 + 固定运维 + 翻新 + 可变运维）÷ 年交付MWh。

一维门槛每次只改变一个输入。联合等比例前沿把所选输入从参考点按同一归一化比例推向各自有利边界。这个比例只是数学指标，**不代表技术成熟度、成功概率、日历进度或唯一工程路线图**。

## 4. 证据质量与来源纪律

本项目严格区分三类证据：精确模型输入、只说明数量级或驱动因素的背景证据，以及边界不同的外部研究比较。所有空间太阳能参考值和范围都是本研究自定假设。

已撤回的2020年英国航天局新闻稿只保留为项目历史，不提供任何模型数值。Caltech直接报告的160 g/m²面密度不能转换成完整架构kg/kW-空间端。2025年完成、2026年发布的英国官方小规模研究中的比功率、门槛收益率和高地球轨道发射成本也只作背景，因为定义不同。

本项目£{result.lcoe_gbp_per_mwh:.0f}/MWh参考锚点落在该2026年发布研究公开的2030年£335–595/MWh区间内。这只是有用的一致性观察，**不是验证**：两者的规模、架构、轨道、情景年份、融资和成本边界均不同。

## 5. 参考锚点与成本结构

表3. 核心参考输入

{markdown_table(["参数", "参考值", "在模型中的作用"], core_rows)}

{reference['delivered_capacity_mw'] / 1000:.1f} GW并网交付容量对应{result.required_space_power_kw / 1e6:.2f} GW空间端功率和{result.orbital_mass_kg / 1e6:.2f}百万kg轨道质量，即约{result.orbital_mass_kg / 1000:,.0f}吨。

表4. 参考点初始资本开支对账

{markdown_table(["组成", "成本"], capex_rows)}

{_figure("图1. 参考点LCOE构成", "../figures_zh/reference_lcoe_components.png", f"年化资本开支约占参考年成本的{facts.capex_share:.0%}，因此物理规模和资本回收条件尤其重要。")}

参考点年交付{result.annual_delivered_mwh / 1e6:.3f}百万MWh，初始资本开支£{result.initial_capex_gbp / 1e9:.1f}bn，年化总成本£{result.annual_total_cost_gbp / 1e9:.2f}bn；这些数值在模型输出中精确对账。

<!-- PAGEBREAK -->

## 6. 英国成本参照

{_figure("图2. 英国电力成本参照", "../figures_zh/uk_electricity_cost_benchmark_comparison.png", f"图中展示纳入标题区间的发电成本行，并另列Hinkley合同价格点和历史系统调整区间。所绘发电成本行约覆盖£{facts.generation_band[0]:.0f}–£{facts.generation_band[1]:.0f}/MWh；排除浮式海风首台套行后为£{facts.mature_generation_band[0]:.0f}–£{facts.mature_generation_band[1]:.0f}/MWh。")}

表5. 结构化数据中的参照定义

{markdown_table(["参照对象", "公开数值", "价格口径", "指标类型"], benchmark_rows)}

Hinkley Point C的£92.50/MWh是以2012年价格表述并按CPI调整的35年差价合约执行价，不是通用核电LCOE。BEIS增强LCOE的£{facts.system_adjusted_band[0]:.0f}–£{facts.system_adjusted_band[1]:.0f}/MWh采用2018年实际英镑，而DESNZ发电成本采用2024年实际英镑。本报告不进行虚假精确的价格换算。

图2使用六条被标记为标题区间的发电成本行。表5另外保留£181/MWh的中负荷率燃气CCUS敏感性值，但为避免把同一技术的两个利用率案例当作两个标题参照，该行不进入图2或标题区间。

因此，与图中区间重叠只能作为筛选结果。批发电价、合同价格、发电侧LCOE和系统调整成本是不同指标，不能直接比较，也不能视为同口径指标。

## 7. 一维条件门槛

{_figure("图3. 每次只改善一个变量时的最低LCOE", "../figures_zh/one_way_lcoe_floors.png", "在所选一维范围内，只有完整架构比质量穿过£150/MWh研究线。该排名取决于范围和参考点，不是跨架构的普遍规律。")}

{_figure("图4. 决策窗口中的比质量门槛", "../figures_zh/specific_mass_threshold_focus.png", f"其余参考输入固定时，£150、£120和£100/MWh分别要求不高于{mass_150:.2f}、{mass_120:.2f}和{mass_100:.2f} kg/kW-空间端。这是数学条件，不是已证实可实现的工程指标。")}

表6. 完整一维门槛审计

{markdown_table(["输入", "单位", "£150", "£120", "£100", "£80", "£60"], _threshold_rows_zh(thresholds))}

破折号表示在测试的一维边界内没有解，并不表示边界以外在物理上不可能。

这个结果并不表示“只有比质量是必要条件”。它只表示：在本参考点和所选一维边界内，比质量是唯一能单独越过£150/MWh的变量；在联合设计中，低质量并不足以达到每一条成本线。2026年发布的英国官方小规模研究在自身架构中把55.5%–64.0%的LCOE方差归因于发射假设，进一步说明驱动因素排名不是普遍规律。

## 8. 联合成本条件前沿

{_figure("图5. 发射成本—效率门槛", "../figures_zh/sbsp_break_even_thresholds.png", "更高效率会放宽发射成本条件，但在其他输入保持参考值时，多个组合仍无法达到目标。表中数值在记录的发射范围内求根得到。")}

表7. 其他输入固定时的发射成本上限

{markdown_table(["端到端效率", "目标", "最大发射成本"], frontier_rows)}

{_figure("图6. 联合等比例前沿", "../figures_zh/combined_progress_frontier.png", "横轴上的目标LCOE越低，纵轴所需的归一化移动量越大。纵轴是数学插值指标，不是实施时间线。")}

表8. 联合等比例指标与部分参数值

{markdown_table(["目标", "归一化移动量", "发射", "比质量", "效率", "实际贴现率代理"], combined_rows)}

{_figure("图7. 发射成本×效率决策等值线", "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "二维图能够显示相互作用，但所有未画出的输入仍固定在参考点，因此不能当作完整工程可行性地图。")}

等比例结果只是透明的数学指标之一。替代切片表明，高效率、低质量或类似基础设施的融资条件都会改变前沿；没有任何一条被宣称为唯一或必要路线。

## 9. 对英国决策的含义

- 高于£150/MWh时，模型仍在宽口径研究筛选线之外，应先寻找能够同时改变多个主要驱动因素的集成架构证据。
- 达到£100–120/MWh时，可信集成设计才值得进入详细工程、融资和英国调度/电网分析。
- 达到£80/MWh及以下时，与所选历史系统调整区间的重叠更有参考意义，但价格基年与遗漏系统效应仍阻止直接市场结论。
- 稳定低碳电力的价值必须在完整英国电力系统模型中检验，不能随意从电站LCOE中扣除。

2026年发布的英国官方小规模研究在每个案例中采用£21/MWh系统收益调整。本报告没有扣除这项数值，因为架构和系统模型边界不同。

## 10. 局限、稳健性与不作出的主张

本项目最强的稳健性来自可追溯性：官方2025发电成本单元格直接与保存的工作簿核对；来源ID进行外键检查；输入CSV进行结构检查；模型会计关系可以对账；门槛根也反算至对应目标LCOE。

主要局限包括：

- 未评估波束安全、频谱、热控、退化、空间碎片、部署与维护等工程可行性；
- 参数范围较宽且部分来自研究判断，驱动因素排名取决于这些范围；
- 未建模相关性、建设时序、学习曲线、概率不确定性和完整税务/融资结构；
- 并网连接点边界不含下游电网、平衡、储能、弃电、可靠性和市场影响；
- 参照价格基年只披露，未统一换算；
- 外部空间太阳能研究不是同口径验证数据集。

本项目不声称首次做门槛分析，不声称发现跨架构普遍必要条件，也不声称给出更准确的部署预测。可以成立的特殊之处是：它提供一张公开可执行、中英双语、来源纪律明确的成本条件图。

## 11. 结论

本研究参考点的并网连接点LCOE约为£{result.lcoe_gbp_per_mwh:.0f}/MWh。只降低发射成本不能弥合差距。在所选一维范围内，极低的完整架构比质量是唯一能单独达到£150/MWh的杠杆，但它单独仍达不到£80/MWh。

因此，核心结论必须写得更窄：**在测试边界内，单独降低发射成本或提高效率不足；没有任何一个测试的一维变化能够达到£80或£60/MWh，因此这两条成本线需要某种联动改善。** 本分析没有证明每一个变量都必须改善，也没有证明等比例路径是唯一方案，更不证明任何工程或商业组合一定能够实现。

本项目的价值，是把这句话及其证据链讲清楚并做到可复核。

<!-- PAGEBREAK -->

## 附录A. 证据—主张对应表

表A1. 背景证据及其限制

{markdown_table(["参数或主张", "证据作用/来源", "定位", "公开数值背景", "适用限制"], evidence_rows_zh)}

## 附录B. 来源登记表

表B1. 本项目使用的来源

{markdown_table(["来源ID", "资料", "机构", "作用"], source_rows_zh)}

## 附录C. 假设与边界登记表

表C1. 明确写出的分析假设

{markdown_table(["ID", "领域", "假设", "限制"], assumptions_zh)}

机器可读输入和完整敏感性曲线保留在`data/`；中文版完整图集在`figures_zh/`；高精度门槛输出在`data/processed/`。
"""

    Path(output_path).write_text(report, encoding="utf-8")
