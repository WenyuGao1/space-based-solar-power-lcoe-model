"""Chinese-language plots for the SBSP assessment."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("tmp/mpl").resolve()))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import PercentFormatter
import numpy as np

from .analysis import TARGET_LCOE_GBP_PER_MWH, contour_grid
from .model import calculate_lcoe
from .parameters import Parameter


FIGURE_DPI = 180
GENERATION_BAND = (55, 113)
SYSTEM_ADJUSTED_RENEWABLE_BAND = (45, 87)
DECISION_BAND = (80, 120)

PARAMETER_ZH = {
    "Delivered grid capacity": "并网交付容量",
    "End-to-end efficiency": "端到端效率",
    "Capacity factor / availability": "容量因子/可用率",
    "System lifetime": "系统寿命",
    "WACC / discount rate": "加权平均资本成本/折现率",
    "Specific mass": "比质量",
    "Space hardware cost": "空间段硬件成本",
    "Wireless power transmission cost": "无线输电硬件成本",
    "Launch cost": "发射成本",
    "Orbit transfer cost": "轨道转移成本",
    "In-orbit assembly and deployment cost": "在轨组装与部署成本",
    "Rectenna CAPEX": "整流天线资本开支",
    "Grid connection cost": "并网成本",
    "Programme margin / contingency": "项目裕度/预备费",
    "Replacement and refurbishment allowance": "更换与翻新预留",
    "Fixed OPEX": "固定运维成本",
    "Variable OPEX": "可变运维成本",
}

TECHNOLOGY_ZH = {
    "Large-scale solar": "大型太阳能",
    "Onshore wind": "陆上风电",
    "Fixed offshore wind": "固定式海上风电",
    "Floating offshore wind": "漂浮式海上风电",
    "Gas CCGT high load factor": "高负荷率燃气联合循环",
    "Gas with CCUS high load factor": "高负荷率燃气CCUS",
    "Gas with CCUS mid load factor": "中负荷率燃气CCUS",
    "Nuclear Hinkley Point C public contract marker": "Hinkley Point C核电合同价格参考",
    "Battery storage": "电池储能",
    "Long-duration storage": "长时储能",
    "High-renewable system-adjusted band": "高可再生电力系统调整区间",
}

UNIT_ZH = {
    "MW": "MW",
    "fraction": "比例",
    "years": "年",
    "kg/kW-space": "kg/kW-空间端",
    "GBP/kg": "英镑/kg",
    "GBP/kg to staging orbit": "英镑/kg至中转轨道",
    "GBP/W-space": "英镑/W-空间端",
    "GBP/W-delivered": "英镑/W-交付端",
    "GBP/kW-delivered": "英镑/kW-交付端",
    "fraction/year": "比例/年",
    "GBP/MWh": "英镑/MWh",
}


def _configure_chinese_font() -> None:
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            font_name = font_manager.FontProperties(fname=str(path)).get_name()
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.sans-serif"] = [font_name]
            plt.rcParams["axes.unicode_minus"] = False
            return
    plt.rcParams["axes.unicode_minus"] = False


_configure_chinese_font()


def _zh_parameter(display_name: str) -> str:
    return PARAMETER_ZH.get(display_name, display_name)


def _zh_unit(unit: str) -> str:
    return UNIT_ZH.get(unit, unit)


def _setup_ax(title: str, ylabel: str = "SBSP平准化电力成本（英镑/MWh）") -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    ax.set_title(title, fontsize=12, weight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(True, color="#d7dde5", linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)
    return fig, ax


def _add_bands(ax: plt.Axes, *, show_targets: bool = True) -> None:
    ax.axhspan(*GENERATION_BAND, color="#7f8c8d", alpha=0.16, label="DESNZ发电成本区间")
    ax.axhspan(*SYSTEM_ADJUSTED_RENEWABLE_BAND, color="#2e8b57", alpha=0.13, label="BEIS系统调整区间")
    if show_targets:
        for target in (150, 120, 100, 80, 60):
            ax.axhline(target, color="#34495e", linewidth=0.7, linestyle="--", alpha=0.35)


def _format_fraction_axis(ax: plt.Axes, parameter: Parameter) -> None:
    if parameter.unit in {"fraction", "fraction/year"}:
        ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))


def _reference_lcoe_on_curve(rows: list[dict[str, object]], reference_value: float) -> float:
    ordered = sorted(rows, key=lambda row: float(row["value"]))
    x = np.array([float(row["value"]) for row in ordered])
    y = np.array([float(row["lcoe_gbp_per_mwh"]) for row in ordered])
    return float(np.interp(reference_value, x, y))


def plot_sensitivity_curve_zh(
    rows: list[dict[str, object]],
    parameter: Parameter,
    output_path: str | Path,
) -> None:
    """绘制完整诊断范围，并在真实参考值上标记参考点。"""
    if not rows:
        return
    parameter_name = _zh_parameter(parameter.display_name)
    unit = _zh_unit(parameter.unit)
    x = np.array([float(row["value"]) for row in rows])
    y = np.array([float(row["lcoe_gbp_per_mwh"]) for row in rows])
    fig, ax = _setup_ax(f"SBSP平准化成本与{parameter_name}")
    _add_bands(ax)
    ax.plot(x, y, color="#0b5cad", linewidth=2.4)
    ref_y = _reference_lcoe_on_curve(rows, parameter.reference_value)
    ax.scatter(
        [parameter.reference_value],
        [ref_y],
        color="#d1495b",
        edgecolor="white",
        linewidth=0.8,
        s=45,
        zorder=5,
        label="参考点",
    )
    ax.set_xlabel(f"{parameter_name}（{unit}）")
    ax.set_ylim(bottom=0, top=max(180, float(np.nanmax(y)) * 1.05))
    _format_fraction_axis(ax, parameter)
    ax.legend(loc="upper right", fontsize=8, frameon=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_sensitivity_curve_zoom_zh(
    rows: list[dict[str, object]],
    parameter: Parameter,
    output_path: str | Path,
    y_max: float = 230.0,
) -> None:
    """同时裁剪横纵轴，只保留最接近决策成本区间的曲线。"""
    if not rows:
        return
    parameter_name = _zh_parameter(parameter.display_name)
    unit = _zh_unit(parameter.unit)
    x = np.array([float(row["value"]) for row in rows])
    y = np.array([float(row["lcoe_gbp_per_mwh"]) for row in rows])
    visible = y <= y_max * 1.08
    if not np.any(visible):
        visible[np.argsort(y)[: max(5, len(y) // 8)]] = True
    x_visible = x[visible]
    span = max(float(np.ptp(x_visible)), (float(np.max(x)) - float(np.min(x))) * 0.02)
    x_low = max(float(np.min(x)), float(np.min(x_visible)) - span * 0.12)
    x_high = min(float(np.max(x)), float(np.max(x_visible)) + span * 0.12)

    fig, ax = _setup_ax(f"{parameter_name}：决策成本区间放大")
    _add_bands(ax)
    ax.plot(x, y, color="#0b5cad", linewidth=2.4)
    ax.set_xlabel(f"{parameter_name}（{unit}）")
    ax.set_xlim(x_low, x_high)
    ax.set_ylim(bottom=40, top=y_max)
    _format_fraction_axis(ax, parameter)
    ax.legend(loc="upper right", fontsize=8, frameon=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_specific_mass_threshold_focus_zh(
    rows: list[dict[str, object]],
    thresholds: list[dict[str, object]],
    output_path: str | Path,
) -> None:
    specific_rows = [row for row in rows if row["parameter"] == "specific_mass_kg_per_kw_space_power"]
    threshold_rows = [
        row
        for row in thresholds
        if row["parameter"] == "specific_mass_kg_per_kw_space_power"
        and int(row["target_lcoe_gbp_per_mwh"]) in {150, 120, 100}
        and row["threshold_value"] not in (None, "")
    ]
    if not specific_rows or not threshold_rows:
        return

    x = np.array([float(row["value"]) for row in specific_rows])
    y = np.array([float(row["lcoe_gbp_per_mwh"]) for row in specific_rows])
    fig, ax = _setup_ax("比质量在英国决策成本区间附近的门槛")
    ax.plot(x, y, color="#0b5cad", linewidth=2.8)
    colors = {150: "#d1495b", 120: "#e07a2f", 100: "#2e8b57"}
    for row in sorted(threshold_rows, key=lambda item: int(item["target_lcoe_gbp_per_mwh"]), reverse=True):
        target = int(row["target_lcoe_gbp_per_mwh"])
        value = float(row["threshold_value"])
        ax.axhline(target, color=colors[target], linestyle="--", linewidth=1.0, alpha=0.65)
        ax.scatter([value], [target], color=colors[target], edgecolor="white", linewidth=0.8, s=52, zorder=5)
        ax.annotate(
            f"{target}英镑/MWh：{value:.2f} kg/kW",
            xy=(value, target),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=8,
            color=colors[target],
        )
    ax.set_xlim(0.48, 1.48)
    ax.set_ylim(85, 165)
    ax.set_xlabel("比质量（kg/kW-空间端）")
    ax.text(
        0.98,
        0.05,
        "参考点：5.0 kg/kW-空间端、429英镑/MWh（图外）",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color="#5d6d7e",
    )
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_contour_zh(
    reference: dict[str, float],
    x_parameter: Parameter,
    y_parameter: Parameter,
    output_path: str | Path,
) -> None:
    x, y, z = contour_grid(reference, x_parameter, y_parameter, x_points=90, y_points=90)
    fig, ax = plt.subplots(figsize=(8.3, 5.8), constrained_layout=True)
    levels = [40, 60, 80, 100, 120, 150, 200, 300, 450, 650]
    filled = ax.contourf(x, y, z, levels=levels, cmap="viridis_r", extend="max")
    contours = ax.contour(x, y, z, levels=[60, 80, 100, 120, 150], colors="white", linewidths=1.0)
    ax.clabel(contours, fmt="%d", fontsize=8)
    x_name = _zh_parameter(x_parameter.display_name)
    y_name = _zh_parameter(y_parameter.display_name)
    ax.set_title(f"{x_name}与{y_name}的成本等值线", fontsize=12, weight="bold")
    ax.set_xlabel(f"{x_name}（{_zh_unit(x_parameter.unit)}）")
    ax.set_ylabel(f"{y_name}（{_zh_unit(y_parameter.unit)}）")
    if x_parameter.unit in {"fraction", "fraction/year"}:
        ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    if y_parameter.unit in {"fraction", "fraction/year"}:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    cbar = fig.colorbar(filled, ax=ax)
    cbar.set_label("SBSP平准化电力成本（英镑/MWh）")
    ax.grid(True, color="white", alpha=0.18)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_contour_zoom_zh(
    reference: dict[str, float],
    x_parameter: Parameter,
    y_parameter: Parameter,
    output_path: str | Path,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
) -> None:
    x_values = np.linspace(x_range[0], x_range[1], 100)
    y_values = np.linspace(y_range[0], y_range[1], 100)
    z = np.zeros((len(y_values), len(x_values)))
    for yi, y_value in enumerate(y_values):
        for xi, x_value in enumerate(x_values):
            case = dict(reference)
            case[x_parameter.name] = float(x_value)
            case[y_parameter.name] = float(y_value)
            z[yi, xi] = calculate_lcoe(case).lcoe_gbp_per_mwh

    focused = np.ma.masked_greater(z, 220)
    cmap = matplotlib.colormaps["viridis_r"].copy()
    cmap.set_bad("#e7ebef")
    levels = [40, 60, 80, 100, 120, 150, 180, 220]
    fig, ax = plt.subplots(figsize=(8.3, 5.8), constrained_layout=True)
    ax.set_facecolor("#e7ebef")
    filled = ax.contourf(x_values, y_values, focused, levels=levels, cmap=cmap, extend="min")
    contours = ax.contour(x_values, y_values, z, levels=[80, 100, 120, 150], colors="white", linewidths=1.2)
    ax.clabel(contours, fmt="%d", fontsize=8)
    x_name = _zh_parameter(x_parameter.display_name)
    y_name = _zh_parameter(y_parameter.display_name)
    ax.set_title("发射成本与效率：决策成本等值线", fontsize=12, weight="bold")
    ax.set_xlabel(f"{x_name}（{_zh_unit(x_parameter.unit)}）")
    ax.set_ylabel(f"{y_name}（{_zh_unit(y_parameter.unit)}）")
    if y_parameter.unit in {"fraction", "fraction/year"}:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    cbar = fig.colorbar(filled, ax=ax, ticks=[60, 80, 100, 120, 150, 180, 220])
    cbar.set_label("SBSP平准化电力成本（英镑/MWh）")
    ax.text(
        0.98,
        0.04,
        "灰色区域：高于220英镑/MWh",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color="#5d6d7e",
    )
    ax.grid(True, color="white", alpha=0.18)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_uk_benchmarks_zh(
    generation_rows: list[dict[str, object]],
    system_rows: list[dict[str, object]],
    output_path: str | Path,
) -> None:
    selected = [
        "Large-scale solar",
        "Onshore wind",
        "Fixed offshore wind",
        "Floating offshore wind",
        "Gas with CCUS high load factor",
        "Nuclear Hinkley Point C public contract marker",
    ]
    by_name = {str(row["technology"]): row for row in generation_rows}
    records: list[tuple[str, float, float, float, str]] = []
    for name in selected:
        row = by_name.get(name)
        if not row or row["value_mid_gbp_per_mwh"] in (None, ""):
            continue
        records.append(
            (
                TECHNOLOGY_ZH.get(name, name),
                float(row["value_low_gbp_per_mwh"]),
                float(row["value_mid_gbp_per_mwh"]),
                float(row["value_high_gbp_per_mwh"]),
                "contract" if "Nuclear" in name else "generation",
            )
        )
    system_match = [row for row in system_rows if row["technology"] == "High-renewable system-adjusted band"]
    if system_match:
        row = system_match[0]
        records.append(
            (
                "高可再生电力系统调整区间",
                float(row["value_low_gbp_per_mwh"]),
                float(row["value_mid_gbp_per_mwh"]),
                float(row["value_high_gbp_per_mwh"]),
                "system",
            )
        )

    labels = [record[0] for record in records]
    y_positions = np.arange(len(records))
    fig, ax = plt.subplots(figsize=(8.5, 5.3))
    fig.subplots_adjust(left=0.27, right=0.98, top=0.90, bottom=0.17)
    ax.axvspan(*DECISION_BAND, color="#d7e8f5", alpha=0.55, label="SBSP决策区间")
    ax.axvline(150, color="#d1495b", linestyle="--", linewidth=1.2, label="150英镑/MWh筛选上限")
    color_map = {"generation": "#5878a8", "system": "#2e8b57", "contract": "#9b6a33"}
    for y_pos, (_, low, mid, high, kind) in zip(y_positions, records):
        color = color_map[kind]
        ax.hlines(y_pos, low, high, color=color, linewidth=5, alpha=0.8)
        ax.scatter(mid, y_pos, color=color, edgecolor="white", linewidth=0.8, s=48, zorder=4)
        label = f"{low:.0f}-{high:.0f}" if abs(high - low) > 0.5 else f"{mid:.1f}"
        ax.text(high + 2, y_pos, label, va="center", fontsize=8, color="#34495e")
    ax.set_yticks(y_positions, labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(35, 165)
    ax.set_xlabel("成本基准（英镑/MWh）")
    ax.set_title("英国电力成本基准与SBSP决策区间", fontsize=12, weight="bold")
    ax.grid(axis="x", color="#d7dde5", linewidth=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8, frameon=True)
    fig.text(
        0.01,
        0.01,
        "DESNZ为2024年实际英镑；BEIS系统调整值为2018年实际英镑；Hinkley Point C为2012年名义合同价格。",
        fontsize=7,
        color="#5d6d7e",
    )
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_break_even_frontier_zh(rows: list[dict[str, object]], output_path: str | Path) -> None:
    efficiencies = sorted({float(row["end_to_end_efficiency"]) for row in rows})
    targets = TARGET_LCOE_GBP_PER_MWH
    matrix = np.full((len(efficiencies), len(targets)), np.nan)
    for yi, efficiency in enumerate(efficiencies):
        for xi, target in enumerate(targets):
            match = [
                row
                for row in rows
                if float(row["end_to_end_efficiency"]) == efficiency
                and int(row["target_lcoe_gbp_per_mwh"]) == target
            ]
            if match and match[0]["max_launch_cost_gbp_per_kg"] not in (None, ""):
                matrix[yi, xi] = float(match[0]["max_launch_cost_gbp_per_kg"])

    cmap = matplotlib.colormaps["YlGnBu"].copy()
    cmap.set_bad("#e9eef3")
    fig, ax = plt.subplots(figsize=(8.5, 4.2), constrained_layout=True)
    ax.imshow(matrix, cmap=cmap, vmin=20, vmax=max(320, float(np.nanmax(matrix))), aspect="auto")
    ax.set_title("达到各LCOE目标所允许的最高发射成本", fontsize=12, weight="bold")
    ax.set_xticks(np.arange(len(targets)), [str(target) for target in targets])
    ax.set_xlabel("SBSP目标LCOE（英镑/MWh）")
    ax.set_yticks(np.arange(len(efficiencies)), [f"{value:.0%}" for value in efficiencies])
    ax.set_ylabel("端到端效率")
    for yi in range(len(efficiencies)):
        for xi in range(len(targets)):
            value = matrix[yi, xi]
            label = "-" if np.isnan(value) else f"{value:.0f}英镑/kg"
            color = "#34495e" if np.isnan(value) or value < 190 else "white"
            ax.text(xi, yi, label, ha="center", va="center", fontsize=8, color=color)
    ax.set_xticks(np.arange(-0.5, len(targets), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(efficiencies), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.text(0.01, 0.01, "破折号表示在20-5,000英镑/kg发射成本探索范围内没有解。", fontsize=7, color="#5d6d7e")
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_combined_progress_frontier_zh(rows: list[dict[str, object]], output_path: str | Path) -> None:
    feasible_rows = [row for row in rows if row["status"] == "feasible"]
    if not feasible_rows:
        return
    targets = np.array([float(row["target_lcoe_gbp_per_mwh"]) for row in feasible_rows])
    movement = np.array([float(row["progress_fraction"]) * 100.0 for row in feasible_rows])
    order = np.argsort(targets)[::-1]
    targets = targets[order]
    movement = movement[order]

    fig, ax = _setup_ax(
        "达到各LCOE目标所需的模型内联合改善幅度",
        ylabel="从参考值向有利边界移动的归一化幅度（%）",
    )
    ax.axvspan(*DECISION_BAND, color="#d7e8f5", alpha=0.55, label="80-120英镑/MWh决策区间")
    ax.axvline(150, color="#d1495b", linestyle="--", linewidth=1.0, label="150英镑/MWh筛选上限")
    ax.plot(targets, movement, color="#6f4e9b", marker="o", linewidth=2.4)
    ax.set_xlabel("SBSP目标LCOE（英镑/MWh）")
    ax.set_ylim(0, min(100, max(movement) * 1.25))
    ax.invert_xaxis()
    for x_value, y_value in zip(targets, movement):
        ax.text(x_value, y_value + 1.5, f"{y_value:.0f}%", ha="center", fontsize=8, color="#3f2d5c")
    ax.legend(loc="upper left", fontsize=8, frameon=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_one_way_lcoe_floors_zh(rows: list[dict[str, object]], output_path: str | Path) -> None:
    ordered = sorted(rows, key=lambda row: float(row["best_lcoe_gbp_per_mwh"]))
    labels = [_zh_parameter(str(row["display_name"])) for row in ordered]
    best = np.array([float(row["best_lcoe_gbp_per_mwh"]) for row in ordered])
    reference = np.array([float(row["reference_lcoe_gbp_per_mwh"]) for row in ordered])
    y_positions = np.arange(len(ordered))

    fig, ax = plt.subplots(figsize=(8.8, 5.8), constrained_layout=True)
    ax.axvspan(*SYSTEM_ADJUSTED_RENEWABLE_BAND, color="#2e8b57", alpha=0.11, label="BEIS系统调整区间")
    ax.axvspan(*DECISION_BAND, color="#d7e8f5", alpha=0.55, label="80-120英镑/MWh决策区间")
    ax.axvline(150, color="#d1495b", linestyle="--", linewidth=1.2, label="150英镑/MWh筛选上限")
    ax.hlines(y_positions, best, reference, color="#aab7c4", linewidth=2.0)
    colors = ["#2e8b57" if value <= 150 else "#0b5cad" if value <= 220 else "#7f8c8d" for value in best]
    ax.scatter(best, y_positions, c=colors, s=48, zorder=4)
    for x_value, y_value in zip(best, y_positions):
        ax.text(x_value + 5, y_value, f"{x_value:.0f}", va="center", fontsize=8, color="#34495e")
    ax.axvline(reference[0], color="#5d6d7e", linewidth=1.0, alpha=0.7)
    ax.text(
        reference[0] - 3,
        0.98,
        f"参考点{reference[0]:.0f}",
        transform=ax.get_xaxis_transform(),
        ha="right",
        va="top",
        fontsize=8,
        color="#5d6d7e",
    )
    ax.set_yticks(y_positions, labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(40, 455)
    ax.set_xlabel("探索范围内的最佳一维LCOE（英镑/MWh）")
    ax.set_title("只有比质量能够单独通过150英镑/MWh筛选线", fontsize=12, weight="bold")
    ax.grid(axis="x", color="#d7dde5", linewidth=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_one_way_threshold_matrix_zh(rows: list[dict[str, object]], output_path: str | Path) -> None:
    drivers: list[str] = []
    for row in rows:
        name = _zh_parameter(str(row["display_name"]))
        if name not in drivers:
            drivers.append(name)
    targets = TARGET_LCOE_GBP_PER_MWH
    matrix = np.zeros((len(drivers), len(targets)))
    best_lcoe = np.zeros((len(drivers), len(targets)))
    for yi, driver in enumerate(drivers):
        for xi, target in enumerate(targets):
            match = [
                row
                for row in rows
                if _zh_parameter(str(row["display_name"])) == driver and int(row["target_lcoe_gbp_per_mwh"]) == target
            ]
            if match:
                matrix[yi, xi] = 1.0 if str(match[0]["feasible"]).lower() == "true" or match[0]["feasible"] is True else 0.0
                best_lcoe[yi, xi] = float(match[0]["best_lcoe_in_range_gbp_per_mwh"])
    fig, ax = plt.subplots(figsize=(8.8, 5.8), constrained_layout=True)
    ax.imshow(matrix, cmap=matplotlib.colors.ListedColormap(["#e9eef3", "#2e8b57"]), vmin=0, vmax=1, aspect="auto")
    ax.set_title("单一变量能否达到SBSP LCOE目标", fontsize=12, weight="bold")
    ax.set_xticks(np.arange(len(targets)), [str(target) for target in targets])
    ax.set_xlabel("目标LCOE（英镑/MWh）")
    ax.set_yticks(np.arange(len(drivers)), drivers, fontsize=8)
    for yi in range(len(drivers)):
        for xi in range(len(targets)):
            label = "可达" if matrix[yi, xi] else f"不可达\n最佳{best_lcoe[yi, xi]:.0f}"
            color = "white" if matrix[yi, xi] else "#34495e"
            ax.text(xi, yi, label, ha="center", va="center", fontsize=7, color=color)
    ax.set_xticks(np.arange(-0.5, len(targets), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(drivers), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


def plot_cost_component_waterfall_zh(reference: dict[str, float], output_path: str | Path) -> None:
    result = calculate_lcoe(reference)
    annual_energy = result.annual_delivered_mwh
    values = [
        result.annualized_capex_gbp / annual_energy,
        result.fixed_opex_gbp_per_year / annual_energy,
        result.replacement_refurbishment_gbp_per_year / annual_energy,
        result.variable_opex_gbp_per_year / annual_energy,
    ]
    labels = ["年化CAPEX", "固定运维", "更换与翻新", "可变运维"]
    colors = ["#4c78a8", "#72b7b2", "#f58518", "#54a24b"]
    total = sum(values)

    fig, ax = plt.subplots(figsize=(8.5, 3.8), constrained_layout=True)
    ax.axvspan(*DECISION_BAND, color="#d7e8f5", alpha=0.55, label="80-120英镑/MWh决策区间")
    ax.axvline(150, color="#d1495b", linestyle="--", linewidth=1.2, label="150英镑/MWh筛选上限")
    left = 0.0
    for label, value, color in zip(labels, values, colors):
        ax.barh([0], [value], left=left, height=0.48, color=color, label=label)
        share = value / total * 100.0
        if value >= 20:
            ax.text(left + value / 2.0, 0, f"{value:.0f}\n{share:.0f}%", ha="center", va="center", fontsize=8, color="white")
        left += value
    ax.text(total + 5, 0, f"合计{total:.0f}", va="center", fontsize=9, weight="bold", color="#243447")
    ax.set_xlim(0, total * 1.12)
    ax.set_yticks([])
    ax.set_xlabel("并网交付LCOE构成（英镑/MWh）")
    ax.set_title(f"参考LCOE为{total:.0f}英镑/MWh，年化CAPEX占{values[0] / total:.0%}", fontsize=12, weight="bold")
    ax.grid(axis="x", color="#d7dde5", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3, fontsize=8, frameon=False)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)
