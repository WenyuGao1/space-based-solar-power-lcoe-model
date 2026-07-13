"""Generate the Chinese final report."""

from __future__ import annotations

from pathlib import Path

from .model import calculate_lcoe
from .parameters import Parameter
from .plots_zh import PARAMETER_ZH, TECHNOLOGY_ZH, UNIT_ZH
from .reporting import SOURCE_REFERENCES
from .utils import fmt_float, fmt_money, fmt_percent


FIGURE_LINKS_ZH = [
    ("英国电力成本基准对比", "../figures_zh/uk_electricity_cost_benchmark_comparison.png", "该图区分裸发电成本和本报告使用的系统调整后新能源成本参照。"),
    ("参考点LCOE构成", "../figures_zh/reference_lcoe_components.png", "参考点LCOE主要由年化CAPEX驱动, 因此融资、质量和空间端规模是一阶因素。"),
    ("SBSP平准化度电成本与发射成本", "../figures_zh/lcoe_vs_launch_cost.png", "完整发射成本扫描显示发射成本是重要杠杆, 但不是唯一杠杆。"),
    ("SBSP平准化度电成本与发射成本: 放大图", "../figures_zh/lcoe_vs_launch_cost_zoom.png", "英国成本区间放大图显示, 在探索范围内仅降低发射成本不能使参考架构进入40-200英镑/MWh决策区间。"),
    ("SBSP平准化度电成本与端到端效率", "../figures_zh/lcoe_vs_end_to_end_efficiency.png", "端到端效率是乘数, 因为它降低所需空间端功率、轨道质量和传输硬件规模。"),
    ("SBSP平准化度电成本与端到端效率: 放大图", "../figures_zh/lcoe_vs_end_to_end_efficiency_zoom.png", "放大图显示, 即使效率达到探索范围高端, 单独提高效率也不能达到英国基准成本。"),
    ("SBSP平准化度电成本与比质量", "../figures_zh/lcoe_vs_specific_mass.png", "比质量是最强的一维杠杆, 因为它同时放大发射、转移和组装成本。"),
    ("SBSP平准化度电成本与空间段硬件成本", "../figures_zh/lcoe_vs_space_hardware_cost.png", "空间段硬件成本很重要, 但如果发射、质量、组装和效率仍接近参考点, 它不能单独解决成本差距。"),
    ("SBSP平准化度电成本与WACC", "../figures_zh/lcoe_vs_wacc.png", "由于空间太阳能发电系统资本密集, 融资成本具有较大杠杆作用。"),
    ("SBSP平准化度电成本与整流天线成本", "../figures_zh/lcoe_vs_rectenna_cost.png", "整流天线CAPEX有影响, 但在当前边界中相对轨道端成本驱动因素属于次要项。"),
    ("SBSP平准化度电成本与系统寿命", "../figures_zh/lcoe_vs_system_lifetime.png", "更长寿命可把资本成本摊薄到更多交付MWh上, 但不能单独弥合成本差距。"),
    ("SBSP平准化度电成本与容量因子", "../figures_zh/lcoe_vs_capacity_factor.png", "高可用率是基荷或战略性低碳电力价值主张的前提。"),
    ("SBSP平准化度电成本与在轨组装成本", "../figures_zh/lcoe_vs_in_orbit_assembly.png", "在轨组装与部署成本较大, 因为它随轨道质量缩放。"),
    ("SBSP平准化度电成本与固定运维成本", "../figures_zh/lcoe_vs_fixed_opex.png", "固定运维成本通过巨大的资本基数影响LCOE。"),
    ("SBSP平准化度电成本与可变运维成本", "../figures_zh/lcoe_vs_variable_opex.png", "可变运维成本在当前模型边界中是较小杠杆。"),
    ("一维门槛可达性矩阵", "../figures_zh/one_way_threshold_feasibility_matrix.png", "该矩阵显示在其他输入固定时, 哪些单一变量能够或不能达到各目标LCOE。"),
    ("SBSP盈亏平衡发射成本门槛", "../figures_zh/sbsp_break_even_thresholds.png", "发射-效率前沿显示, 更高效率会放宽发射成本要求, 但不会消除其他改进的必要性。"),
    ("等值线: 发射成本与端到端效率", "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency.png", "该等值线图显示发射成本和效率在完整探索范围内的耦合作用。"),
    ("等值线放大图: 发射成本与端到端效率", "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "放大图聚焦60-150英镑/MWh附近的英国相关成本区间。"),
    ("等值线: 发射成本与空间段硬件成本", "../figures_zh/contour_launch_cost_vs_space_hardware_cost.png", "该图显示低发射成本和低空间段硬件成本需要共同出现。"),
    ("等值线: WACC与空间段硬件成本", "../figures_zh/contour_wacc_vs_space_hardware_cost.png", "该图显示制造成本与资本成本之间的交互作用。"),
]

REFERENCE_PARAMETER_ORDER = [
    "delivered_capacity_mw",
    "end_to_end_efficiency",
    "capacity_factor",
    "specific_mass_kg_per_kw_space_power",
    "launch_cost_gbp_per_kg",
    "space_hardware_cost_gbp_per_w_space",
    "wacc",
    "system_lifetime_years",
    "in_orbit_assembly_cost_gbp_per_kg",
    "rectenna_cost_gbp_per_w_delivered",
    "grid_connection_cost_gbp_per_kw_delivered",
    "fixed_opex_pct_capex_per_year",
    "variable_opex_gbp_per_mwh",
    "replacement_refurbishment_pct_capex_per_year",
]

REFERENCE_INTERPRETATION_ZH = {
    "delivered_capacity_mw": "规模锚点。由于大多数成本按W或kg计, LCOE对规模大体中性。",
    "end_to_end_efficiency": "从空间端所需功率到并网交付功率的探索性转换假设。",
    "capacity_factor": "近稳定输出的可用率假设, 不是SBSP运行历史观测值。",
    "specific_mass_kg_per_kw_space_power": "架构层面的质量强度, 是最强的一维驱动因素之一, 不确定性很高。",
    "launch_cost_gbp_per_kg": "全口径发射成本门槛变量, 作为宽范围探索变量而不是预测价格。",
    "space_hardware_cost_gbp_per_w_space": "轨道端采集、结构、控制和转换硬件的探索性制造成本门槛。",
    "wacc": "融资成本变量, 覆盖基础设施融资到较高风险项目融资的范围。",
    "system_lifetime_years": "经济运行寿命。空间环境退化和翻新通过另一项预留表示。",
    "in_orbit_assembly_cost_gbp_per_kg": "机器人组装、部署、检查和调试成本的探索性假设。",
    "rectenna_cost_gbp_per_w_delivered": "地面接收和转换系统按交付W计的探索性成本。",
    "grid_connection_cost_gbp_per_kw_delivered": "按英国发电成本假设口径设置的并网接口预留。",
    "fixed_opex_pct_capex_per_year": "年度运营、保险、监测和维护的探索性预留。",
    "variable_opex_gbp_per_mwh": "按交付MWh计的探索性可变运维成本。",
    "replacement_refurbishment_pct_capex_per_year": "退化和部件更换的年度探索性预留。",
}

CATEGORY_ZH = {
    "generation-only": "裸发电成本",
    "contract-price marker": "合同价格参考",
    "storage-cost marker": "储能成本参考",
}

PRICE_BASIS_ZH = {
    "2024 real GBP": "2024年实际英镑",
    "2018 real GBP": "2018年实际英镑",
    "2012 nominal GBP": "2012年名义英镑",
    "mixed": "口径不一",
}

STATUS_ZH = {
    "not reached within explored one-way range": "在探索的一维范围内未达到",
    "maximum value meeting target": "满足目标的最高值",
    "minimum value meeting target": "满足目标的最低值",
    "feasible": "可行",
    "not feasible within explored launch range": "在探索的发射成本范围内不可行",
    "not feasible within explored combined range": "在探索的组合范围内不可行",
}

GENERATION_NOTE_ZH = {
    "Large-scale solar": "DESNZ 2025附录A中的LCOE总成本区间。作为当前官方发电成本基准使用。",
    "Onshore wind": "DESNZ 2025附录A中的LCOE总成本区间。",
    "Fixed offshore wind": "DESNZ 2025附录A中的LCOE总成本区间。",
    "Floating offshore wind": "漂浮式海上风电成熟度较低, 此处保留为高成本参照。",
    "Gas CCGT high load factor": "DESNZ附录A中93%负荷率燃气联合循环LCOE。脱碳电力系统中的实际负荷率可能更低。",
    "Gas with CCUS high load factor": "DESNZ附录A中900 MW、88%负荷率燃气CCUS LCOE。",
    "Gas with CCUS mid load factor": "用于显示较低利用小时的敏感性, 不纳入主基准区间。",
    "Nuclear Hinkley Point C public contract marker": "不是通用核电LCOE, 也不是2024年实际价格。由于近期DESNZ报告未发布可直接比较的通用核电LCOE, 这里只作公共合同价格参考。",
    "Battery storage": "储能不是发电LCOE。BEIS 2020说明, 储能假设不能与发电机LCOE直接比较。",
    "Long-duration storage": "作为系统成本类别保留, 不作为裸发电成本平价基准。",
}

SOURCE_REFERENCE_TITLE_ZH = {
    "DESNZ_EGC_2025": "DESNZ《2025年发电成本》",
    "BEIS_EGC_2020": "BEIS《2020年发电成本》",
    "NESO_BALANCING_2025": "NESO《2025年度平衡成本报告》",
    "NESO_NETWORK_UPDATE_2026": "NESO《2030年以后输电网络更新》",
    "NESO_CP2030": "NESO《清洁电力2030建议及实施资料》",
    "NESO_OPERABILITY_2026": "NESO《可运行性战略报告与电力市场路线图》",
    "UKSA_SBSP_2020": "英国航天局和BEIS空间太阳能研究委托",
    "CALTECH_SBSP_2022": "加州理工空间太阳能技术概念论文",
    "NAO_HPC_2017": "英国国家审计署《欣克利角C》",
}


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def _source_link(source_id: str) -> str:
    return f"`{source_id}`"


def _source_reference_rows_zh() -> list[list[object]]:
    return [
        [source_id, SOURCE_REFERENCE_TITLE_ZH.get(source_id, title), url]
        for source_id, title, url in SOURCE_REFERENCES
    ]


def _zh_parameter(display_name: str) -> str:
    return PARAMETER_ZH.get(display_name, display_name)


def _zh_unit(unit: str) -> str:
    return UNIT_ZH.get(unit, unit)


def _source_type_label(source_type: str) -> str:
    labels = {
        "sourced": "来源值",
        "derived": "派生值",
        "exploratory": "探索性建模假设",
    }
    return labels.get(source_type, source_type)


def _status_zh(status: object) -> str:
    return STATUS_ZH.get(str(status), str(status))


def _format_parameter_value(parameter: Parameter) -> str:
    if parameter.unit == "fraction":
        return fmt_percent(parameter.reference_value)
    if parameter.unit == "fraction/year":
        return fmt_percent(parameter.reference_value)
    return f"{fmt_float(parameter.reference_value, 3)} {_zh_unit(parameter.unit)}"


def _reference_parameter_rows(params: dict[str, Parameter]) -> list[list[object]]:
    rows: list[list[object]] = []
    for name in REFERENCE_PARAMETER_ORDER:
        parameter = params[name]
        rows.append(
            [
                _zh_parameter(parameter.display_name),
                _format_parameter_value(parameter),
                _source_type_label(parameter.source_type),
                _source_link(parameter.source_id),
                REFERENCE_INTERPRETATION_ZH[name],
            ]
        )
    return rows


def _threshold_rows(thresholds: list[dict[str, object]], target: int) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in thresholds:
        if int(row["target_lcoe_gbp_per_mwh"]) != target:
            continue
        threshold = row["threshold_value"]
        threshold_text = "未达到" if threshold in (None, "") else fmt_float(float(threshold), 3)
        rows.append([
            _zh_parameter(str(row["display_name"])),
            _zh_unit(str(row["unit"])),
            threshold_text,
            fmt_float(float(row["best_lcoe_in_range_gbp_per_mwh"]), 0),
            _status_zh(row["status"]),
        ])
    return rows


def _frontier_rows(frontier: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in frontier:
        launch_value = row["max_launch_cost_gbp_per_kg"]
        rows.append(
            [
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                row["target_lcoe_gbp_per_mwh"],
                "不可行" if launch_value in (None, "") else fmt_float(float(launch_value), 0),
                _status_zh(row["status"]),
            ]
        )
    return rows


def _generation_rows(generation_rows: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in generation_rows:
        low = row.get("value_low_gbp_per_mwh")
        high = row.get("value_high_gbp_per_mwh")
        cost_range = "不可直接比较" if low in (None, "") else f"{fmt_float(float(low), 0)}-{fmt_float(float(high), 0)}"
        technology = str(row["technology"])
        rows.append([
            TECHNOLOGY_ZH.get(technology, technology),
            CATEGORY_ZH.get(str(row["category"]), str(row["category"])),
            cost_range,
            PRICE_BASIS_ZH.get(str(row["price_basis"]), str(row["price_basis"])),
            _source_link(str(row["source_id"])),
            GENERATION_NOTE_ZH.get(technology, str(row["notes"])),
        ])
    return rows


def _system_rows(system_rows: list[dict[str, object]]) -> list[list[object]]:
    selected = [row for row in system_rows if row["technology"] == "High-renewable system-adjusted band"]
    rows: list[list[object]] = []
    for row in selected:
        rows.append([
            TECHNOLOGY_ZH.get(str(row["technology"]), str(row["technology"])),
            "合并区间",
            f"{fmt_float(float(row['value_low_gbp_per_mwh']), 0)}-{fmt_float(float(row['value_high_gbp_per_mwh']), 0)}",
            PRICE_BASIS_ZH.get(str(row["price_basis"]), str(row["price_basis"])),
            _source_link(str(row["source_id"])),
        ])
    return rows


def _combined_frontier_rows(combined_frontier: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for row in combined_frontier:
        if row["status"] != "feasible":
            rows.append([row["target_lcoe_gbp_per_mwh"], "不可行", "", "", "", "", "", "", ""])
            continue
        rows.append(
            [
                row["target_lcoe_gbp_per_mwh"],
                fmt_percent(float(row["progress_fraction"]), 0),
                fmt_float(float(row["launch_cost_gbp_per_kg"]), 0),
                fmt_float(float(row["specific_mass_kg_per_kw_space_power"]), 2),
                fmt_float(float(row["space_hardware_cost_gbp_per_w_space"]), 2),
                fmt_float(float(row["in_orbit_assembly_cost_gbp_per_kg"]), 0),
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                fmt_percent(float(row["wacc"]), 1),
                fmt_percent(float(row["capacity_factor"]), 0),
            ]
        )
    return rows


def _alternative_frontier_rows(alternative_frontiers: list[dict[str, object]]) -> list[list[object]]:
    pathway_names = {
        "High-efficiency parameter slice": "高效率参数切片",
        "Low-mass architecture slice": "低质量架构切片",
        "Infrastructure-finance slice": "基础设施融资切片",
    }
    rows: list[list[object]] = []
    for row in alternative_frontiers:
        name = pathway_names.get(str(row["display_name"]), str(row["display_name"]))
        if row["status"] != "feasible":
            rows.append([name, row["target_lcoe_gbp_per_mwh"], "不可行", "", "", "", "", ""])
            continue
        rows.append(
            [
                name,
                row["target_lcoe_gbp_per_mwh"],
                fmt_percent(float(row["progress_fraction"]), 0),
                fmt_float(float(row["launch_cost_gbp_per_kg"]), 0),
                fmt_float(float(row["specific_mass_kg_per_kw_space_power"]), 2),
                fmt_percent(float(row["end_to_end_efficiency"]), 0),
                fmt_percent(float(row["wacc"]), 1),
                fmt_float(float(row["lcoe_gbp_per_mwh"]), 0),
            ]
        )
    return rows


def _figure(caption: str, path: str, note: str) -> str:
    return f"![{caption}]({path})\n\n{note}"


def _benchmark_layer_rows_zh() -> list[list[object]]:
    return [
        [
            "裸发电 LCOE",
            "DESNZ发电机边界成本, 包括太阳能、陆上风电、固定式和漂浮式海上风电、燃气联合循环、燃气CCUS等有可用数据的技术。",
            "列示发电技术约55-153英镑/MWh; 主文比较使用55-113英镑/MWh作为较成熟发电技术的核心区间。",
            "DESNZ《2025年发电成本》; Hinkley Point C单独作为合同价格参考。",
            "作为发电机成本下界使用, 不等同于可靠供电成本。",
        ],
        [
            "BEIS保守系统调整基准",
            "BEIS增强LCOE证据, 包含更广义系统影响、其他影响和输电影响。",
            "45-87英镑/MWh, 2018年实际英镑。",
            "BEIS《2020年发电成本》增强LCOE表; 由于较新的DESNZ发电成本不包含更广义系统成本, 本报告保留该证据。",
            "作为保守的指示性系统调整基准使用, 不是直接市场价格, 也不是完整英国电力系统模型。",
        ],
        [
            "更广义的高比例新能源系统压力",
            "电网加固、输电约束、平衡成本、弃电、短时和长时储能、备用容量、接入延迟、天气相关性和可靠性要求。",
            "指示性 / 不可直接归并为单一LCOE。NESO证据显示平衡和电网成本压力具有实质性, 其中关键电网建设可通过减少热约束在2030年降低约40亿英镑能源账单成本。",
            "NESO年度平衡成本报告、NESO清洁电力2030、NESO 2030年以后输电网络资料和NESO可运行性资料。",
            "作为系统压力叠加层使用, 说明BEIS 45-87英镑/MWh不应被视为风电和太阳能系统成本的最终上限。",
        ],
        [
            "稳定低碳电源比较对象",
            "可调度或接近稳定的低碳参照, 如燃气CCUS、核电合同价格参考、储能支撑的新能源供电。",
            "DESNZ高负荷率燃气CCUS约104-105英镑/MWh; Hinkley Point C为92.50英镑/MWh的2012年名义合同价格参考, 不是通用核电LCOE。",
            "DESNZ《2025年发电成本》、英国国家审计署《欣克利角C》、BEIS增强LCOE证据。",
            "用于解释空间太阳能作为接近基荷或准基荷低碳电源的可比区间, 而不是直接替代裸风电或太阳能LCOE。",
        ],
    ]


def _key_findings_rows_zh() -> list[list[object]]:
    return [
        [
            "参考点下空间太阳能尚不具备成本竞争力。",
            "参考点并网交付LCOE约为429英镑/MWh。",
            "当前参考架构不应被视为近期主流发电机组。",
        ],
        [
            "仅降低发射成本不足够。",
            "即使发射成本降至探索范围低端20英镑/kg, 参考架构仍约为204英镑/MWh。",
            "空间太阳能必须作为完整系统架构成本问题处理, 不能只作为火箭成本问题处理。",
        ],
        [
            "比质量是最强的一维杠杆。",
            "在其他输入固定时, 达到150英镑/MWh一维平价需要约1.3 kg/kW-空间端。",
            "轻量化架构是一阶技术瓶颈。",
        ],
        [
            "效率、质量、发射、组装和融资必须同步改善。",
            "综合瓶颈前沿显示, 80-120英镑/MWh需要多个变量协调移动。",
            "相关路径是集成架构改进, 不是孤立部件优化。",
        ],
        [
            "BEIS 45-87英镑/MWh是保守系统调整基准, 不是完整上限。",
            "更广义系统压力包括平衡、弃电、电网加固、储能时长和备用容量。",
            "空间太阳能进入80-120英镑/MWh应触发更深入的英国系统价值建模, 而不是自动竞争力判断。",
        ],
        [
            "空间太阳能的相关比较对象是稳定或准稳定低碳电力。",
            "报告区分裸发电LCOE、保守系统调整成本和更广义高比例新能源系统压力。",
            "空间太阳能应与可靠交付电力比较, 而不只是与风电和太阳能发电机LCOE比较。",
        ],
    ]


def _reference_parameter_compact_rows_zh(params: dict[str, Parameter]) -> list[list[object]]:
    role = {
        "delivered_capacity_mw": "规模锚点",
        "end_to_end_efficiency": "决定所需空间端功率",
        "capacity_factor": "决定年交付电量",
        "specific_mass_kg_per_kw_space_power": "质量和发射成本乘数",
        "launch_cost_gbp_per_kg": "运输成本门槛变量",
        "space_hardware_cost_gbp_per_w_space": "轨道制造成本门槛",
        "wacc": "资本成本和融资可行性杠杆",
        "system_lifetime_years": "资本回收周期",
        "in_orbit_assembly_cost_gbp_per_kg": "随质量缩放的部署成本",
        "rectenna_cost_gbp_per_w_delivered": "地面接收系统成本",
        "grid_connection_cost_gbp_per_kw_delivered": "并网接口预留",
        "fixed_opex_pct_capex_per_year": "年度固定运维预留",
        "variable_opex_gbp_per_mwh": "可变运维预留",
        "replacement_refurbishment_pct_capex_per_year": "替换和退化预留",
    }
    return [
        [
            _zh_parameter(params[name].display_name),
            _format_parameter_value(params[name]),
            _source_type_label(params[name].source_type),
            role[name],
        ]
        for name in REFERENCE_PARAMETER_ORDER
    ]


def _threshold_summary_rows_zh(thresholds: list[dict[str, object]]) -> list[list[object]]:
    drivers = []
    for row in thresholds:
        name = str(row["display_name"])
        if name not in drivers:
            drivers.append(name)
    rows: list[list[object]] = []
    for driver in drivers:
        matches = [row for row in thresholds if str(row["display_name"]) == driver]
        if not matches:
            continue
        unit = _zh_unit(str(matches[0]["unit"]))
        by_target = {int(row["target_lcoe_gbp_per_mwh"]): row for row in matches}

        def threshold_text(target: int) -> str:
            match = by_target.get(target)
            if not match:
                return "不适用"
            value = match["threshold_value"]
            return "未达到" if value in (None, "") else fmt_float(float(value), 3)

        best_lcoe = min(float(row["best_lcoe_in_range_gbp_per_mwh"]) for row in matches)
        rows.append([_zh_parameter(driver), unit, threshold_text(150), threshold_text(100), fmt_float(best_lcoe, 0)])
    return rows


def _secondary_figure_blocks_zh() -> str:
    figures = [
        (
            "图A1. 空间段硬件成本敏感性",
            "../figures_zh/lcoe_vs_space_hardware_cost.png",
            "降低轨道硬件成本有明显作用, 但如果质量、发射成本、组装成本和效率仍接近参考点, 仍不足以弥合成本差距。制造成本是必要瓶颈, 但不是充分条件。",
        ),
        (
            "图A2. 整流天线成本敏感性",
            "../figures_zh/lcoe_vs_rectenna_cost.png",
            "地面接收基础设施会影响LCOE, 但斜率小于主要轨道端成本驱动因素, 因此在当前边界内属于次要敏感性。",
        ),
        (
            "图A3. 系统寿命敏感性",
            "../figures_zh/lcoe_vs_system_lifetime.png",
            "更长运行寿命可以把资本成本摊薄到更多交付MWh上, 但单独延寿不能补偿重而低效的架构。",
        ),
        (
            "图A4. 容量因子敏感性",
            "../figures_zh/lcoe_vs_capacity_factor.png",
            "高可用率是稳定供电价值主张的前提, 因为巨大的资本基数必须通过大量交付电量摊薄。",
        ),
        (
            "图A5. 在轨组装成本敏感性",
            "../figures_zh/lcoe_vs_in_orbit_assembly.png",
            "在轨组装和部署成本随轨道质量缩放, 因此当架构仍然较重时, 该成本项会变得重要。",
        ),
        (
            "图A6. 固定运维成本敏感性",
            "../figures_zh/lcoe_vs_fixed_opex.png",
            "固定运维通过巨大的资本基数影响LCOE, 但不是实现平价的主要路径。",
        ),
        (
            "图A7. 可变运维成本敏感性",
            "../figures_zh/lcoe_vs_variable_opex.png",
            "在当前模型边界内, 可变运维成本相对年化资本成本较小, 因而对门槛结论影响有限。",
        ),
        (
            "图A8. 发射成本敏感性放大图",
            "../figures_zh/lcoe_vs_launch_cost_zoom.png",
            "英国成本区间放大视角进一步显示, 即使发射成本极低, 参考架构如果缺少其他改进, 仍难以进入80-120英镑/MWh决策区间。",
        ),
        (
            "图A9. 端到端效率敏感性放大图",
            "../figures_zh/lcoe_vs_end_to_end_efficiency_zoom.png",
            "放大图显示更高转换效率能够缓解成本问题, 但不能替代更低质量和更低空间基础设施成本。",
        ),
        (
            "图A10. 完整等值线: 发射成本与端到端效率",
            "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency.png",
            "完整曲面显示探索范围内的广义交互, 并说明与英国成本相关的区域只占参数空间的一小部分。",
        ),
        (
            "图A11. 完整等值线: 发射成本与空间段硬件成本",
            "../figures_zh/contour_launch_cost_vs_space_hardware_cost.png",
            "该图显示空间运输和轨道制造成本需要共同下降, 才能接近英国参照区间。",
        ),
        (
            "图A12. 完整等值线: WACC与空间段硬件成本",
            "../figures_zh/contour_wacc_vs_space_hardware_cost.png",
            "该图显示制造成本和资本成本在资本密集型系统中的交互作用。",
        ),
    ]
    return "\n\n".join(_figure(caption, path, note) for caption, path, note in figures)


def _build_markdown_report_zh_legacy(
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
) -> None:
    result = calculate_lcoe(reference)
    top_drivers = importance[:5]
    generation_band = (55, 113)
    system_band = (45, 87)

    capex_rows = [
        [name.replace("_", " "), fmt_money(value / 1e9, 2)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_name_zh = {
        "space_segment_capex": "空间段CAPEX",
        "wireless_power_transmission": "无线输电硬件",
        "launch": "发射",
        "orbit_transfer": "轨道转移",
        "in_orbit_assembly": "在轨组装与部署",
        "rectenna": "整流天线",
        "grid_connection": "并网",
    }
    capex_rows = [
        [capex_name_zh.get(name, name.replace("_", " ")), fmt_money(value / 1e9, 2)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    top_driver_rows = [
        [
            _zh_parameter(str(row["display_name"])),
            _zh_unit(str(row["unit"])),
            fmt_float(float(row["reference_value"]), 3),
            fmt_float(float(row["best_value_in_range"]), 3),
            fmt_float(float(row["lcoe_reduction_gbp_per_mwh"]), 0),
        ]
        for row in top_drivers
    ]

    report = f"""# 英国空间太阳能成本门槛评估

副标题：面向英国基荷与战略低碳电力的技术经济成本门槛评估

证据状态：公开证据和项目来源登记表更新至2026年7月8日。

版本号：v1.0 最终交付版式精修

说明：作为可复现技术评估报告编制, 使用本项目数据和模型流水线。

免责声明：本报告识别成本平价门槛，不代表部署确定性、投资建议或商业成熟度判断。

[[PAGEBREAK]]

## 目录

- 1. 执行摘要
- 2. 关键发现与决策含义
- 3. 研究问题与范围
- 4. 空间太阳能 LCOE 模型
- 5. 参考点：解释与局限
- 6. 英国电力成本基准
- 7. 成本驱动因素分析
- 8. 盈亏平衡门槛分析
- 9. 综合瓶颈前沿
- 10. 对英国电力系统的意义
- 11. 关键技术与经济瓶颈
- 12. 局限性与不确定性
- 13. 结论
- 附录 A. 次要敏感性图表
- 附录 B. 来源登记表
- 附录 C. 假设分类说明

[[PAGEBREAK]]

## 1. 执行摘要

本报告是成本门槛评估。它研究空间太阳能发电系统(SBSP)的关键成本和性能瓶颈下降到什么水平时, 并网交付电力成本才会与英国电力成本基准具有可比性。报告不引入部署年份预测, 也不使用命名情景。

记录的参考点给出的并网交付平准化度电成本（LCOE）为{fmt_float(result.lcoe_gbp_per_mwh, 0)}英镑/MWh。这个数值不是预测, 也不是推荐架构。它是连续敏感性曲线的分析锚点。在该锚点上, SBSP高于本报告采用的DESNZ裸发电成本基准区间, 约{generation_band[0]}-{generation_band[1]}英镑/MWh; 也高于BEIS高新能源系统调整后参照区间, 约{system_band[0]}-{system_band[1]}英镑/MWh。

BEIS 45-87英镑/MWh比较值予以保留, 因为它是本项目中最直接可用的增强LCOE证据。但本报告把它视为保守的系统调整基准, 而不是可靠高比例新能源电力成本的完整上限。输电约束、平衡成本、弃电、储能时长、备用容量、接入延迟和天气相关性等更广义压力单独讨论, 因为它们不能全部被压缩为一个可直接比较的LCOE数字。

门槛答案是:

- 当SBSP低于约150英镑/MWh时, 开始接近英国参照区间上沿。
- 在约100-120英镑/MWh时, 它与燃气CCUS和较高成本稳定低碳参照点更具可比性。
- 在约80英镑/MWh及以下时, 它开始与本报告使用的保守系统调整后新能源参照区间重叠。
- 约60英镑/MWh是严格前沿, 需要多数瓶颈变量同时改善。

模型识别的是成本平价条件, 不是部署确定性。多数单一变量不能单独把SBSP降至150英镑/MWh以下。比质量是例外, 但只有在其他输入固定时架构质量强度降至约1.3 kg/kW-空间端或更低才可达到150英镑/MWh。发射成本单独下降不足够: 即使在探索范围内降至20英镑/kg, 参考架构仍约为204英镑/MWh。

## 2. 关键发现与决策含义

表1. 关键发现与决策含义

{markdown_table(["关键发现", "模型证据", "决策含义"], _key_findings_rows_zh())}

该表构成本报告的决策阅读框架。核心含义是, 只有当空间太阳能进入80-120英镑/MWh区间, 且架构能够可信地提供稳定或准稳定低碳电力时, 它才对英国具备进一步系统价值建模意义。

## 3. 研究问题与范围

研究问题是:

在什么发射成本、空间段硬件成本、在轨组装成本、整流天线成本、融资成本、端到端效率、容量因子、系统寿命和运维成本水平下, SBSP能够与英国裸发电成本和系统调整后电力成本基准达到平价?

模型边界是并网交付LCOE。它包括空间段CAPEX、发射、轨道转移、在轨组装与部署、无线电力传输、整流天线CAPEX、并网成本、项目裕度、翻新预留、固定运维、可变运维、容量因子、端到端效率、寿命、WACC和年交付电量。

模型不估计商业成熟度、工程可实现性或完整系统价值。这些是独立问题。本分析识别的是在这些问题具备决策意义之前必须达到的数值成本和性能门槛。

## 4. 空间太阳能 LCOE 模型

模型采用标准折现全寿命成本结构:

LCOE = 年化CAPEX + 年运维成本 + 年翻新预留, 再除以年交付MWh。

年交付电量为并网交付容量MW x 8,760 x 容量因子。所需空间端功率为并网交付容量除以端到端效率。轨道质量为所需空间端功率乘以比质量。

表2. 参考点输入

{markdown_table(["参数", "参考值", "分类", "在模型中的作用"], _reference_parameter_compact_rows_zh(params))}

表3. 初始CAPEX分解

{markdown_table(["组成部分", "十亿英镑"], capex_rows)}

参考点给出{fmt_money(result.required_space_power_kw / 1e6, 2)} GW所需空间端功率和约{fmt_money(result.orbital_mass_kg / 1000.0, 0)}吨轨道硬件。这些数值是所选参考假设的结果, 不是最终设计建议。

{_figure("图1. 参考点LCOE构成", "../figures_zh/reference_lcoe_components.png", "年化CAPEX主导参考点成本, 因而质量、空间端规模、硬件成本和资本成本决定门槛结果。运维成本微调不能替代资本强度的结构性下降。")}

## 5. 参考点：解释与局限

参考点的作用是让敏感性分析可解释。它是透明的分析锚点, 从这个锚点出发, 每个成本驱动因素可以在记录范围内上下移动。它不应被理解为最可能的SBSP架构、优选架构或设计要求。

由于商业规模SBSP尚未部署, 多个参考输入属于探索性建模假设。比质量、空间段硬件成本、在轨组装成本、整流天线成本、运维成本和翻新预留尤其不确定。模型使用这些值是为了回答“需要什么条件成立”, 而不是“未来一定会发生什么”。

429英镑/MWh输出来自一个空间端规模较大的参考架构: 2 GW并网交付容量、15%端到端效率、5 kg/kW-空间端比质量、500英镑/kg发射成本、200英镑/kg在轨组装成本和6.5% WACC。13.33 GW所需空间端功率和66,667吨轨道硬件是这些假设的机械结果。

## 6. 英国电力成本基准

裸发电LCOE有用, 因为它衡量发电机边界内生产电力的成本。但它不等于维持可靠电力系统的成本。DESNZ说明, 更广义系统影响不包含在发电机LCOE边界内, 需要电力系统建模。

BEIS增强LCOE基准有用, 因为它把部分更广义系统影响、其他影响和输电影响纳入比较。本报告保留它作为保守的指示性比较对象。它不是直接市场价格, 不是完整的现代英国电力系统模型, 也不是风电和太阳能在高比例新能源系统中成本的最终上限。

{_figure("图2. 英国电力成本基准对比", "../figures_zh/uk_electricity_cost_benchmark_comparison.png", "该图把DESNZ发电机边界成本与BEIS保守系统调整后新能源区间分开, 并标出本分析使用的SBSP门槛线。对接近基荷或准基荷SBSP而言, 最低风电和太阳能裸LCOE不是唯一相关比较对象。")}

表4. 英国电力成本基准解释层级

{markdown_table(["基准层级", "包含内容", "可用指示性成本区间", "证据基础", "在SBSP比较中的使用方式"], _benchmark_layer_rows_zh())}

不能只用裸发电LCOE把风电、太阳能和SBSP比较。可变新能源可能需要电网加固、输电约束管理、平衡调度、弃电管理、短时储能、长时灵活性、备用容量和接入升级。这些成本大小取决于地理位置、天气相关性、需求形状、互联、储能部署、电网可用性和市场设计。

NESO 2025年度平衡成本报告说明, 可变风电和太阳能可能需要额外平衡行动。该报告把电网加固识别为降低平衡成本的重要杠杆, 并指出Clean Power 2030网络建设可通过减少热约束在2030年降低约40亿英镑能源账单成本。NESO可运行性资料还把这一问题描述为涵盖充裕性、灵活性、频率、电压、稳定性、热约束和恢复能力的多维系统问题。

因此, 本报告保留BEIS 45-87英镑/MWh增强LCOE比较值, 将其作为保守的系统调整基准。它不应被解释为未来英国高比例新能源电力系统运行成本的完整上限。对SBSP而言, 相关比较对象是可靠、稳定或接近稳定的低碳交付电力成本, 而不只是最低发电机LCOE。

## 7. 成本驱动因素分析

一维敏感性曲线在其他输入保持参考点不变时移动单一参数。这是一种诊断方法: 它识别杠杆和瓶颈, 不是工程实施计划。

表5. 最大一维LCOE降幅

{markdown_table(["驱动因素", "单位", "参考值", "最佳探索值", "LCOE降低(英镑/MWh)"], top_driver_rows)}

比质量占主导, 因为每一kg轨道硬件都会带来发射、轨道转移和组装成本。端到端效率是乘数, 因为它改变所需空间端规模。发射成本很重要, 但低发射价格如果作用在重而低效的架构上, LCOE仍然较高。WACC重要, 因为参考系统由资本开支主导。

{_figure("图3. 比质量敏感性", "../figures_zh/lcoe_vs_specific_mass.png", "降低比质量是最强的一维杠杆, 因为它同时降低轨道质量以及相关的发射、转移和组装成本。单变量达到150英镑/MWh需要约1.3 kg/kW-空间端或更低的架构; 更低目标仍需要组合改善。")}

{_figure("图4. 端到端效率敏感性", "../figures_zh/lcoe_vs_end_to_end_efficiency.png", "更高端到端效率会降低所需空间端功率和需要发射、组装的质量。曲线下降明显, 但单独提高效率仍不能把参考架构带入主要英国参照区间。")}

{_figure("图5. 发射成本敏感性", "../figures_zh/lcoe_vs_launch_cost.png", "降低发射成本可以显著降低SBSP LCOE, 但即使达到探索范围低端, 参考架构仍约为204英镑/MWh。发射成本下降必须与更低质量、更高效率和更低组装成本结合。")}

{_figure("图6. WACC敏感性", "../figures_zh/lcoe_vs_wacc.png", "由于年化CAPEX主导参考LCOE, 资本成本具有很高杠杆作用。只有当技术、建设、政策和收入风险下降到足以支持基础设施式融资时, 较低WACC才具有合理性。")}

## 8. 盈亏平衡门槛分析

一维门槛分析询问: 单独改变一个输入能否达到每个目标LCOE。“未达到”表示在该输入记录的探索范围内无法达到目标。

{_figure("图7. 一维门槛可达性矩阵", "../figures_zh/one_way_threshold_feasibility_matrix.png", "该矩阵显示在其他输入固定时, 哪些单一变量能够达到各目标。大多数单变量变化不能达到150英镑/MWh; 在探索的一维范围内, 只有比质量能够达到更低目标。")}

表6. 一维门槛汇总

{markdown_table(["驱动因素", "单位", "150英镑/MWh门槛", "100英镑/MWh门槛", "最佳一维LCOE"], _threshold_summary_rows_zh(thresholds))}

发射-效率前沿隔离出两个重要变量, 但并不暗示它们已经足够。

表7. 发射-效率前沿

{markdown_table(["端到端效率", "目标LCOE", "最高发射成本(英镑/kg)", "状态"], _frontier_rows(frontier))}

{_figure("图8. 发射-效率盈亏平衡前沿", "../figures_zh/sbsp_break_even_thresholds.png", "更高效率会放宽最高发射成本要求, 但放宽幅度有限。在25%效率下, 达到150英镑/MWh需要约109英镑/kg或更低的发射成本; 在35%效率下, 100英镑/MWh也需要约64英镑/kg。")}

## 9. 综合瓶颈前沿

综合瓶颈前沿把主要瓶颈变量按相同百分比从参考值推向有利边界。它是说明性的等进度前沿, 不是预测, 也不是声称这些精确参数组合一定会实现。

表8. 综合瓶颈前沿

{markdown_table(["目标LCOE", "进度", "发射英镑/kg", "质量kg/kW", "硬件英镑/W", "组装英镑/kg", "效率", "WACC", "容量因子"], _combined_frontier_rows(combined_frontier))}

这张表应被理解为所需变化方向的压缩地图。达到150英镑/MWh已经要求参考点出现广泛移动。从120降到80英镑/MWh时, 几乎每个瓶颈都同步收紧, 而不是把压力转移给某一个极端参数。

{_figure("图9. 联合进度前沿", "../figures_zh/combined_progress_frontier.png", "该图把等进度表转化为单条曲线: 目标LCOE越低, 从参考点向有利边界移动的协调幅度越大。SBSP门槛成功取决于一组工程和金融进步, 而不是单独的发射成本故事。")}

{_figure("图10. 发射成本与端到端效率放大等值线", "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "该图聚焦60-150英镑/MWh区间, 显示效率提高如何扩大可接受发射成本窗口。与英国成本相关的区域只在两个变量均显著偏离参考点时出现。")}

表9. 替代参数空间切片

{markdown_table(["路径", "目标LCOE", "进度", "发射英镑/kg", "质量kg/kW", "效率", "WACC", "模型LCOE"], _alternative_frontier_rows(alternative_frontiers))}

各切片的关键解释一致: 成本相关路径是同步改善。只有发射成本突破, 而没有更低质量、更低组装成本、更好效率和可融资风险结构, 不能把SBSP放入英国主流电力成本区间。

## 10. 对英国电力系统的意义

如果空间太阳能能够提供稳定或近稳定低碳输出, 它对英国最相关。在这种角色下, 它不只是与风电和太阳能的裸LCOE竞争, 而是与燃气CCUS、类似核电的稳定低碳电源、长时储能以及高比例新能源系统中可靠供电成本比较。

如果SBSP在并网交付口径下达到80-120英镑/MWh区间, 并且工程架构可信、商业结构可融资, 它可能作为基荷或战略性低碳电力具备相关性。模型并不能证明这些条件, 只识别这些条件开始具有决策意义的成本区域。

潜在系统价值可能包括可预测交付、降低对天气相关性的暴露、降低平衡需求、降低长时储能需求以及能源安全价值。这些收益没有计入LCOE, 需要完整英国电力系统建模。

## 11. 关键技术与经济瓶颈

必要瓶颈下降项包括:

- 更低轨道质量, 因为质量会放大发射、转移和组装成本。
- 更高端到端效率, 因为效率决定所需空间端规模。
- 更低发射成本, 因为即使架构变轻, 发射仍是主要成本。
- 更低在轨组装与部署成本, 因为大型结构必须可靠组装和调试。
- 更低空间段硬件成本, 因为轨道电力系统必须接近大规模制造经济性。
- 更低融资成本, 因为参考LCOE主要由年化CAPEX支配。
- 高容量因子和长寿命, 因为资本成本必须摊薄到大量交付MWh上。

这些因素没有任何一个单独充分。模型计算的门槛要求工程和金融条件同步移动。

## 12. 局限性与不确定性

最大不确定性是工程可实现性。模型可以识别一维达到150英镑/MWh需要约1.3 kg/kW-空间端或更低, 但不能证明这种架构能够被建造、发射、组装、运行和翻新。

第二个不确定性是商业成熟度。低WACC只有在技术风险、建设风险、政策风险和收入风险足够降低后才可能接近基础设施融资水平。这是商业和监管问题, 不是纯工程输入。

第三个不确定性是系统价值。SBSP可能提供发电机LCOE未捕捉的稳定低碳价值, 但这种价值必须在完整英国电力系统框架中建模。本报告使用的BEIS 45-87英镑/MWh系统调整基准是保守且指示性的; 更广义系统压力叠加层不能替代调度和电网模型。

第四个不确定性是来源可比性。DESNZ发电成本为2024年实际英镑, BEIS增强LCOE证据为2018年实际英镑。本报告保留这些价格口径, 而不是进行虚假精确的换算。

## 13. 结论

模型识别的是成本平价条件, 不是部署确定性。

在记录的参考点上, SBSP不具备成本竞争力: 并网交付LCOE约为429英镑/MWh。有用的发现是这个数值背后的门槛结构。多数一维杠杆不能单独达到英国参照区间上沿。比质量是例外, 但前提是架构显著变轻。

发射成本单独下降不足够, 因为它作用于其他架构参数决定的质量和规模。重而低效的系统即使使用很低发射价格, 仍然昂贵。最重要的组合改善是更低质量、更高效率、更低发射成本、更低在轨组装成本、更低空间段硬件成本和更低WACC。

SBSP在约150英镑/MWh附近开始接近英国电力成本区间; 在约100-120英镑/MWh时更接近稳定低碳基准; 在约80英镑/MWh及以下时开始与保守BEIS系统调整后新能源参照区间重叠。达到60英镑/MWh需要几乎所有瓶颈同步移动。

本报告采用的 BEIS 45-87 英镑/MWh 系统调整基准应被视为保守的指示性比较，而不是英国高比例新能源系统成本的完整上限。空间太阳能若进入 80-120 英镑/MWh 区间，并不意味着自动具备商业竞争力，而是意味着它值得进入更深入的英国电力系统价值建模。

工程可实现性、商业成熟度和完整电力系统价值仍是独立检验。如果SBSP能够达到本报告识别的门槛条件, 并展示可靠高可用运行, 它可能成为英国基荷或战略性低碳电力选项。在此之前, 它仍是取决于门槛的技术选项。

## 附录 A. 次要敏感性图表

主报告已把支撑核心论证所需的图表嵌入相应分析段落。以下图表保留用于透明性和诊断完整性, 但不改变门槛结论。

{_secondary_figure_blocks_zh()}

## 附录 B. 来源登记表

附录表B1. 完整来源登记表

{markdown_table(["来源ID", "参考资料", "URL"], _source_reference_rows_zh())}

## 附录 C. 假设分类说明

关键数值输入存放在`data/sbsp_parameters.csv`、`data/uk_generation_costs.csv`、`data/uk_system_adjusted_costs.csv`和`data/assumptions.csv`。每个主要数值都标注为来源值、派生值或探索性取值。完整分类细节保留在本附录中, 而不是放在主文流程里。

附录表C1. 完整参考点输入分类

{markdown_table(["参数", "参考值", "分类", "来源", "解释"], _reference_parameter_rows(params))}
"""

    Path(output_path).write_text(report, encoding="utf-8")


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
) -> None:
    """生成面向决策问题的精简中文版报告。"""
    del generation_rows, system_rows, frontier, alternative_frontiers
    result = calculate_lcoe(reference)

    def compact_value(parameter: Parameter) -> str:
        value = parameter.reference_value
        unit = parameter.unit
        if unit in {"fraction", "fraction/year"}:
            return f"{value:.1%}"
        if unit in {"MW", "years", "GBP/kg", "GBP/kg to staging orbit", "GBP/kW-delivered", "GBP/MWh"}:
            return f"{value:,.0f} {_zh_unit(unit)}"
        if unit == "kg/kW-space":
            return f"{value:.1f} {_zh_unit(unit)}"
        return f"{value:.2f} {_zh_unit(unit)}"

    core_names = [
        "delivered_capacity_mw",
        "end_to_end_efficiency",
        "capacity_factor",
        "specific_mass_kg_per_kw_space_power",
        "launch_cost_gbp_per_kg",
        "space_hardware_cost_gbp_per_w_space",
        "in_orbit_assembly_cost_gbp_per_kg",
        "wacc",
        "system_lifetime_years",
    ]
    core_roles = {
        "delivered_capacity_mw": "规模锚点",
        "end_to_end_efficiency": "决定空间端功率和质量",
        "capacity_factor": "决定年交付电量",
        "specific_mass_kg_per_kw_space_power": "同时放大发射、转移和组装成本",
        "launch_cost_gbp_per_kg": "主要运输成本杠杆",
        "space_hardware_cost_gbp_per_w_space": "轨道制造成本杠杆",
        "in_orbit_assembly_cost_gbp_per_kg": "随质量缩放的部署成本",
        "wacc": "决定资本开支年化水平",
        "system_lifetime_years": "资本回收周期",
    }
    core_rows = [
        [_zh_parameter(params[name].display_name), compact_value(params[name]), core_roles[name]] for name in core_names
    ]

    capex_name_zh = {
        "space_segment_capex": "空间段CAPEX",
        "wireless_power_transmission": "无线输电硬件",
        "launch": "发射",
        "orbit_transfer": "轨道转移",
        "in_orbit_assembly": "在轨组装与部署",
        "rectenna": "整流天线",
        "grid_connection": "并网",
    }
    capex_rows = [
        [capex_name_zh.get(name, name.replace("_", " ")), fmt_money(value / 1e9, 2)]
        for name, value in sorted(result.capex_components_gbp.items(), key=lambda item: item[1], reverse=True)
    ]
    capex_rows.extend(
        [
            ["项目裕度前小计", fmt_money(result.pre_margin_capex_gbp / 1e9, 2)],
            ["项目裕度/预备费", fmt_money(result.programme_margin_gbp / 1e9, 2)],
            ["初始CAPEX总额", fmt_money(result.initial_capex_gbp / 1e9, 2)],
        ]
    )

    decision_rows = [
        ["低于150英镑/MWh", "宽口径筛选上限", "接近较高成本参照，但不代表具备竞争力"],
        ["100-120英镑/MWh", "稳定低碳电力决策区间", "应启动工程、融资和英国系统价值评估"],
        ["80英镑/MWh及以下", "保守系统调整区间开始重叠", "成本具有相关性，但仍须校核价格口径和系统价值"],
        ["60英镑/MWh", "严格延伸目标", "需要多数瓶颈同步改善"],
    ]

    benchmark_rows = [
        ["DESNZ发电成本区间", "55-153", "2024年实际英镑", "发电机边界比较"],
        ["成熟发电技术核心区间", "55-113", "2024年实际英镑", "主文发电成本筛选线"],
        ["BEIS新能源系统调整区间", "45-87", "2018年实际英镑", "保守指示值，不是完整英国系统模型"],
        ["稳定低碳参照点", "92.5合同价；104-105燃气CCUS", "价格口径不一", "仅用于背景解释，不能视为单一同口径基准"],
    ]

    combined_rows = []
    for row in combined_frontier:
        target = int(row["target_lcoe_gbp_per_mwh"])
        if row["status"] != "feasible" or target not in {150, 120, 100, 80}:
            continue
        combined_rows.append(
            [
                target,
                f"{float(row['progress_fraction']):.0%}",
                f"{float(row['launch_cost_gbp_per_kg']):.0f}",
                f"{float(row['specific_mass_kg_per_kw_space_power']):.2f}",
                f"{float(row['end_to_end_efficiency']):.0%}",
                f"{float(row['wacc']):.1%}",
            ]
        )

    threshold_lookup = {
        (str(row["parameter"]), int(row["target_lcoe_gbp_per_mwh"])): row for row in thresholds
    }
    mass_150 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 150)]["threshold_value"])
    mass_120 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 120)]["threshold_value"])
    mass_100 = float(threshold_lookup[("specific_mass_kg_per_kw_space_power", 100)]["threshold_value"])
    best_by_parameter = {str(row["parameter"]): float(row["best_lcoe_gbp_per_mwh"]) for row in importance}
    decision_assumption_names = set(core_names + ["rectenna_cost_gbp_per_w_delivered"])
    assumption_rows = [
        [row[0], row[1], row[3], row[4]]
        for name, row in zip(REFERENCE_PARAMETER_ORDER, _reference_parameter_rows(params))
        if name in decision_assumption_names
    ]

    report = f"""# 英国空间太阳能成本门槛评估

副标题：面向英国稳定低碳电力的决策型技术经济评估

证据状态：项目证据登记表和官方来源文件复核至2026年7月10日。

版本号：v1.1 决策窗口修订版

说明：使用本项目数据与模型流水线生成的可复现成本门槛评估。

免责声明：本报告识别进入进一步评估的成本条件，不证明工程可行性、商业成熟度或投资价值。

[[PAGEBREAK]]

## 目录

- 1. 执行决策摘要
- 2. 范围与方法
- 3. 参考点与成本结构
- 4. 英国成本基准
- 5. 一维成本门槛
- 6. 综合瓶颈门槛
- 7. 决策含义与局限
- 附录A. 完整一维诊断
- 附录B. 来源登记表
- 附录C. 假设分类

[[PAGEBREAK]]

## 1. 执行决策摘要

参考点的并网交付LCOE为{result.lcoe_gbp_per_mwh:.0f}英镑/MWh。它是分析锚点，不是预测或优选设计。真正有用的结果是其下方的成本门槛结构。

表1. 成本门槛及其决策含义

{markdown_table(["成本门槛", "解释", "决策含义"], decision_rows)}

本评估有三项核心发现：

- 只有比质量能够单独通过150英镑/MWh筛选线。在其他输入固定时，150、120和100英镑/MWh分别要求约{mass_150:.2f}、{mass_120:.2f}和{mass_100:.2f} kg/kW-空间端。
- 发射成本即使降至20英镑/kg，最佳一维结果仍为{best_by_parameter['launch_cost_gbp_per_kg']:.0f}英镑/MWh；端到端效率提高至35%时，最佳一维结果仍为{best_by_parameter['end_to_end_efficiency']:.0f}英镑/MWh。
- 进入80-120英镑/MWh区间，需要质量、效率、发射、组装、轨道硬件和融资条件共同改善。

空间太阳能进入80-120英镑/MWh，只意味着值得开展更深入的工程和英国电力系统建模，不意味着自动具备市场竞争力。

## 2. 范围与方法

模型研究发射成本、质量强度、硬件成本、在轨组装成本、效率、利用率、寿命、运维和融资条件降到什么水平时，空间太阳能可以接近英国电力成本基准。

模型边界为并网交付LCOE。年化初始CAPEX、固定运维、翻新预留和可变运维之和除以年交付MWh。年交付电量等于并网容量乘以8,760小时和容量因子；所需空间端功率等于并网容量除以端到端效率；轨道质量等于空间端功率乘以比质量。

模型只识别成本平价。工程可实现性、波束与频谱监管、建设交付、商业融资和完整系统价值均需要独立检验。

## 3. 参考点与成本结构

表2. 核心参考输入

{markdown_table(["参数", "参考值", "作用"], core_rows)}

在该参考点下，2 GW并网交付容量需要{result.required_space_power_kw / 1e6:.2f} GW空间端功率和约{result.orbital_mass_kg / 1000:,.0f}吨轨道硬件。

[[PAGEBREAK]]

表3. 包含项目裕度的初始CAPEX

{markdown_table(["组成部分", "十亿英镑"], capex_rows)}

{_figure("图1. 参考点LCOE构成", "../figures_zh/reference_lcoe_components.png", "年化CAPEX约占参考LCOE的82%。因此，质量、空间端规模、硬件成本和融资条件决定主要门槛。")}

由于商业规模空间太阳能尚未部署，这些输入属于探索性假设。它们用于回答“什么条件必须改变”，而不是预测未来一定发生什么。

## 4. 英国成本基准

{_figure("图2. 英国电力成本基准", "../figures_zh/uk_electricity_cost_benchmark_comparison.png", "图中使用区间线而不是从零起点的柱形。80-120英镑/MWh是决策窗口，150英镑/MWh只是宽口径筛选上限。")}

表4. 基准解释

{markdown_table(["比较对象", "指示性英镑/MWh", "价格口径", "用途"], benchmark_rows)}

DESNZ发电成本与BEIS增强LCOE不属于同一实际价格基年。图中明确标注这一差异，因此区间重叠不能被理解为已完成价格归一化的精确平价。电网、平衡、弃电、储能和可靠性成本还需要完整英国电力系统模型。

## 5. 一维成本门槛

一维分析只改变一个输入，其余输入保持参考值。它用于识别杠杆，不是技术开发计划。

{_figure("图3. 各一维变量能够达到的最低LCOE", "../figures_zh/one_way_lcoe_floors.png", "该图删除了高成本恶化区间，只比较各输入向有利边界移动后的最佳结果。只有比质量能够单独通过150英镑/MWh筛选线。")}

{_figure("图4. 比质量在决策窗口附近的门槛", "../figures_zh/specific_mass_threshold_focus.png", "图中只保留穿越150、120和100英镑/MWh的曲线部分，并明确注明5.0 kg/kW-空间端参考点位于视窗之外。")}

{_figure("图5. 发射成本—效率门槛矩阵", "../figures_zh/sbsp_break_even_thresholds.png", "端到端效率为25%时，150英镑/MWh要求发射成本约109英镑/kg或更低；效率为35%时，100英镑/MWh要求约64英镑/kg。破折号表示探索范围内没有解。")}

结果很明确：低发射价格作用于重而低效的架构时，系统仍然过于昂贵。质量和效率决定发射与组装成本所作用的系统规模。

## 6. 综合瓶颈门槛

综合前沿把模型输入从参考值按相同比例推向其记录范围内的有利边界。下表的百分比是模型内归一化参数移动量，不代表技术成熟度、实现概率或日历进度。

表5. 选定综合门槛点

{markdown_table(["目标英镑/MWh", "归一化移动量", "发射英镑/kg", "质量kg/kW", "效率", "WACC"], combined_rows)}

{_figure("图6. 模型内联合改善幅度", "../figures_zh/combined_progress_frontier.png", "从150英镑/MWh筛选线上移到80-120英镑/MWh决策区间，需要多项物理和金融约束同时收紧。")}

{_figure("图7. 发射成本与效率的决策等值线", "../figures_zh/contour_launch_cost_vs_end_to_end_efficiency_zoom.png", "图中只显示220英镑/MWh及以下区域，更高成本空间统一置灰，并突出150、120、100和80英镑/MWh等值线。")}

这些组合只是参数空间切片，不是工程路线图。替代切片仍保留在`data/processed/alternative_combined_pathways.csv`中。

## 7. 决策含义与局限

如果空间太阳能能够提供稳定或近稳定低碳输出，它在英国的相关比较对象应是可靠交付电力、燃气CCUS、类似核电的稳定供给、长时灵活性以及高比例新能源系统的调整后成本，而不只是风电和太阳能的裸发电LCOE。

可执行的决策规则是：低于150英镑/MWh时继续跟踪关键门槛；进入100-120英镑/MWh时开展集成工程与融资评估；达到80英镑/MWh及以下时，增加英国调度、电网和可靠性建模。

主要不确定性包括架构可实现性、成本范围可信度、融资风险、寿命与退化、波束与监管约束，以及稳定输出在未来英国系统中的价值。2018年BEIS与2024年DESNZ价格基年不同，报告继续明确保留这一差异，而不进行隐含换算。

核心结论可以压缩为一句话：空间太阳能不会仅靠降低发射成本进入决策范围；只有可信的集成架构进入约80-120英镑/MWh并网交付LCOE时，才值得开展下一层级评估。

[[PAGEBREAK]]

## 附录A. 完整一维诊断

主报告只展示决策相关视图。完整敏感性曲线仍保留在`figures_zh/`，全部曲线点保留在`data/processed/sensitivity_curves.csv`。

{_figure("图A1. 完整一维可达性矩阵", "../figures_zh/one_way_threshold_feasibility_matrix.png", "该矩阵保留五个成本目标和十一个变化输入的完整一维审计。")}

附录表A1. 完整一维门槛汇总

{markdown_table(["驱动因素", "单位", "150门槛", "100门槛", "最佳一维LCOE"], _threshold_summary_rows_zh(thresholds))}

[[PAGEBREAK]]

## 附录B. 来源登记表

附录表B1. 来源登记表

{markdown_table(["来源ID", "参考资料", "URL"], _source_reference_rows_zh())}

## 附录C. 假设分类

表C1中的参考输入均归类为探索性建模假设。运维及并网接口预留仍完整记录在`data/sbsp_parameters.csv`；官方原始工作簿、整理后CSV和模型输出分别保存，便于追溯。

附录表C1. 决策相关参考输入

{markdown_table(["参数", "参考值", "来源", "解释"], assumption_rows)}
"""

    Path(output_path).write_text(report, encoding="utf-8")
