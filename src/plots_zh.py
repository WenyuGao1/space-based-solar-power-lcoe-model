"""Simplified-Chinese analytical figures with numerical parity to English."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

from .analysis import contour_grid
from .model import calculate_lcoe
from .parameters import Parameter
from .plots import COLORS, TARGETS, _finish, _reference_lcoe_on_curve


def _font() -> None:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
    ):
        path = Path(candidate)
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            name = font_manager.FontProperties(fname=str(path)).get_name()
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["font.family"] = "sans-serif"
            break
    plt.rcParams["axes.unicode_minus"] = False


_font()

ID_ZH = {
    "system_specific_mass_kg_per_kw_delivered": "系统比质量",
    "launch_cost_gbp_per_kg_to_staging_orbit": "至集结轨道发射成本",
    "real_discount_rate": "实际项目贴现率",
    "in_orbit_assembly_cost_gbp_per_kg_operational_hardware": "在轨组装与部署成本",
    "space_generation_hardware_cost_gbp_per_w_dc": "空间发电硬件成本",
    "programme_contingency_fraction": "初始项目预备费",
    "construction_duration_years": "建设期",
    "orbit_transfer_cost_gbp_per_kg_final_hardware": "集结至运行轨道转移成本",
    "capacity_factor": "交付容量因子",
    "operating_lifetime_years": "投运后运行寿命",
    "rectenna_conversion_efficiency": "整流天线转换效率",
    "space_hardware_replacement_rate_per_year": "空间硬件更换率",
    "annual_output_degradation_fraction": "年度交付出力衰减",
    "variable_opex_gbp_per_mwh": "可变运维",
    "dc_to_rf_efficiency": "直流至射频效率",
    "transmitter_cost_gbp_per_w_rf_emitted": "射频发射硬件成本",
    "rectenna_cost_gbp_per_w_delivered": "整流天线成本",
    "residual_value_fraction_initial_capex": "期末残值",
    "fixed_opex_fraction_of_eligible_assets_per_year": "固定运维率",
    "grid_connection_cost_gbp_per_kw_delivered": "并网成本",
    "grid_conversion_efficiency": "直流至并网交流效率",
    "transmission_efficiency": "射频传输效率",
    "decommissioning_cost_fraction_initial_capex": "期末退役成本",
    "ground_hardware_replacement_rate_per_year": "地面硬件更换率",
    "solar_conversion_efficiency": "太阳能至直流转换效率",
}

TECH_ZH = {
    "Large-scale solar": "大型光伏", "Onshore wind": "陆上风电",
    "Fixed offshore wind": "固定式海上风电", "Floating offshore wind": "漂浮式海上风电",
    "Gas CCGT high load factor": "高负荷率燃气联合循环",
    "Gas with CCUS high load factor": "高负荷率燃气CCUS",
    "Gas with CCUS mid load factor": "中负荷率燃气CCUS",
}


def _targets(ax) -> None:
    for target in TARGETS:
        ax.axhline(target, color=COLORS["grid"], linewidth=.8, zorder=0)


def plot_sensitivity_curve_zh(rows, parameter: Parameter, output_path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    x = [float(row["value"]) for row in rows]
    y = [float(row["lcoe_gbp_per_mwh"]) for row in rows]
    _targets(ax)
    ax.plot(x, y, color=COLORS["teal"], linewidth=2.6)
    reference = _reference_lcoe_on_curve(rows, parameter.reference_value)
    ax.scatter([parameter.reference_value], [reference], s=55, color=COLORS["amber"], label="参考情景")
    ax.set(title=f"单变量敏感性：{parameter.display_name_zh}", xlabel=f"{parameter.display_name_zh}（{parameter.unit}）", ylabel="条件性DCF LCOE（2024年实际英镑/MWh）")
    ax.grid(axis="x", color=COLORS["grid"])
    ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_sensitivity_curve_zoom_zh(rows, parameter, output_path):
    plot_sensitivity_curve_zh(rows, parameter, output_path)


def plot_contour_zh(reference, x_parameter: Parameter, y_parameter: Parameter, output_path):
    xs, ys, z = contour_grid(reference, x_parameter, y_parameter, 70, 70)
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    mesh = ax.contourf(xs, ys, z, levels=24, cmap="YlGnBu_r")
    levels = [value for value in TARGETS if np.nanmin(z) <= value <= np.nanmax(z)]
    if levels:
        lines = ax.contour(xs, ys, z, levels=levels, colors=COLORS["ink"], linewidths=.9)
        ax.clabel(lines, fmt=lambda value: f"£{value:.0f}", fontsize=8)
    fig.colorbar(mesh, ax=ax, label="2024年实际英镑/MWh")
    ax.scatter([x_parameter.reference_value], [y_parameter.reference_value], color=COLORS["amber"], s=50, label="参考情景")
    ax.set(title="条件性LCOE参数交互", xlabel=f"{x_parameter.display_name_zh}（{x_parameter.unit}）", ylabel=f"{y_parameter.display_name_zh}（{y_parameter.unit}）")
    ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_contour_zoom_zh(reference, x_parameter, y_parameter, output_path, x_range=None, y_range=None):
    plot_contour_zh(reference, x_parameter, y_parameter, output_path)


def plot_uk_benchmarks_zh(generation_rows, system_rows, output_path):
    rows = [row for row in generation_rows if str(row.get("include_in_bands", "")).lower() in {"yes", "true", "1"}][:7]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    labels = [TECH_ZH.get(str(row["technology"]), str(row["technology"])) for row in rows]
    lows = [float(row["value_low_gbp_per_mwh"] or row["value_mid_gbp_per_mwh"]) for row in rows]
    highs = [float(row["value_high_gbp_per_mwh"] or row["value_mid_gbp_per_mwh"]) for row in rows]
    y = np.arange(len(rows))
    ax.barh(y, [high-low for low, high in zip(lows, highs)], left=lows, color=COLORS["cyan"])
    ax.set_yticks(y, labels); ax.invert_yaxis()
    ax.set(title="英国发电成本背景（不能与SBSP目标直接等同）", xlabel="2024年实际英镑/MWh")
    ax.grid(axis="x", color=COLORS["grid"])
    _finish(fig, output_path)


def plot_break_even_frontier_zh(rows, output_path):
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    for target in sorted({float(row["target_lcoe_gbp_per_mwh"]) for row in rows}):
        subset = [row for row in rows if float(row["target_lcoe_gbp_per_mwh"]) == target and row.get("max_launch_cost_gbp_per_kg_to_staging_orbit") not in (None, "")]
        if subset:
            ax.plot([100*float(row["end_to_end_efficiency"]) for row in subset], [float(row["max_launch_cost_gbp_per_kg_to_staging_orbit"]) for row in subset], marker="o", label=f"£{target:.0f}/MWh")
    ax.set(title="计算所得链路效率下的发射成本阈值", xlabel="计算所得端到端效率（%）", ylabel="至集结轨道最高发射成本（2024年实际英镑/kg）")
    ax.grid(color=COLORS["grid"]); ax.legend(frameon=False, ncol=2)
    _finish(fig, output_path)


def plot_combined_progress_frontier_zh(rows, output_path):
    available = [row for row in rows if row.get("progress_fraction") not in (None, "")]
    fig, ax = plt.subplots(figsize=(9.5, 5.3))
    ax.plot([float(row["target_lcoe_gbp_per_mwh"]) for row in available], [100*float(row["progress_fraction"]) for row in available], marker="o", linewidth=2.5, color=COLORS["teal"])
    ax.set(title="等比例数学插值（不是路线图）", xlabel="目标LCOE（2024年实际英镑/MWh）", ylabel="向有利边界移动（%）")
    ax.invert_xaxis(); ax.grid(color=COLORS["grid"])
    _finish(fig, output_path)


def plot_cost_component_waterfall_zh(reference, output_path):
    result = calculate_lcoe(reference)
    labels = {"initial_construction":"初始建设", "fixed_opex":"固定运维", "variable_opex":"可变运维", "space_hardware_replacement":"空间硬件更换", "ground_hardware_replacement":"地面硬件更换", "decommissioning":"退役", "residual_value":"残值"}
    components = sorted(result.lifecycle_cost_components_pv_gbp.items(), key=lambda item: abs(item[1]), reverse=True)
    fig, ax = plt.subplots(figsize=(10, 5.7))
    values = [value/result.discounted_lifetime_energy_mwh for _, value in components]
    ax.barh(np.arange(len(values)), values, color=[COLORS["red"] if value < 0 else COLORS["teal"] for value in values])
    ax.set_yticks(np.arange(len(values)), [labels[name] for name, _ in components]); ax.invert_yaxis()
    ax.set(title="参考情景DCF LCOE构成", xlabel="2024年实际英镑/MWh（贴现成本/贴现电量）")
    ax.grid(axis="x", color=COLORS["grid"])
    _finish(fig, output_path)


def plot_one_way_lcoe_floors_zh(rows, output_path):
    shown = rows[:12]
    fig, ax = plt.subplots(figsize=(10, 6.2)); y = np.arange(len(shown))
    ax.barh(y, [float(row["best_lcoe_gbp_per_mwh"]) for row in shown], color=COLORS["teal"])
    ax.set_yticks(y, [ID_ZH.get(str(row["parameter"]), str(row["display_name"])) for row in shown]); ax.invert_yaxis()
    ax.axvline(150, color=COLORS["amber"], linestyle="--", label="£150筛选线")
    ax.set(title="各探索范围内可达到的最低单变量LCOE", xlabel="2024年实际英镑/MWh")
    ax.grid(axis="x", color=COLORS["grid"]); ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_specific_mass_threshold_focus_zh(rows, thresholds, output_path):
    subset = [row for row in rows if row["parameter"] == "system_specific_mass_kg_per_kw_delivered"]
    parameter = Parameter("system_specific_mass_kg_per_kw_delivered", "System specific mass", "系统比质量", "kg/kW-delivered", 5, .5, 10, "lower", "", "", "", "", "", "", "")
    plot_sensitivity_curve_zh(subset, parameter, output_path)


def plot_one_way_threshold_matrix_zh(rows, output_path):
    ids = list(dict.fromkeys(str(row["parameter"]) for row in rows))
    targets = sorted({float(row["target_lcoe_gbp_per_mwh"]) for row in rows})
    matrix = np.zeros((len(ids), len(targets)))
    for row in rows:
        matrix[ids.index(str(row["parameter"]))][targets.index(float(row["target_lcoe_gbp_per_mwh"]))] = 1 if row["feasible"] else 0
    fig, ax = plt.subplots(figsize=(9.5, 8)); ax.imshow(matrix, aspect="auto", cmap="GnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(targets)), [f"£{value:.0f}" for value in targets]); ax.set_yticks(range(len(ids)), [ID_ZH.get(name, name) for name in ids])
    ax.set(title="单变量目标可达性", xlabel="目标（2024年实际英镑/MWh）")
    _finish(fig, output_path)
