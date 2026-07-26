"""Compact, release-grade analytical figures for the v2.0 model."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

from .analysis import contour_grid
from .model import calculate_lcoe
from .parameters import Parameter


COLORS = {"teal": "#0f766e", "cyan": "#42a5a0", "ink": "#253b3a", "amber": "#c8842f", "red": "#b85748", "grid": "#dfe8e6"}
TARGETS = [60, 80, 100, 120, 150]


def _finish(fig, path: str | Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _reference_lcoe_on_curve(rows: list[dict[str, object]], reference_value: float) -> float:
    return float(min(rows, key=lambda row: abs(float(row["value"]) - reference_value))["lcoe_gbp_per_mwh"])


def _target_lines(ax) -> None:
    for target in TARGETS:
        ax.axhline(target, color=COLORS["grid"], linewidth=0.8, zorder=0)


def plot_sensitivity_curve(rows: list[dict[str, object]], parameter: Parameter, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    x = [float(row["value"]) for row in rows]
    y = [float(row["lcoe_gbp_per_mwh"]) for row in rows]
    _target_lines(ax)
    ax.plot(x, y, color=COLORS["teal"], linewidth=2.6)
    ref = _reference_lcoe_on_curve(rows, parameter.reference_value)
    ax.scatter([parameter.reference_value], [ref], s=55, color=COLORS["amber"], zorder=4, label="Reference")
    ax.set(title=f"One-way sensitivity: {parameter.display_name}", xlabel=f"{parameter.display_name} ({parameter.unit})", ylabel="Conditional DCF LCOE (2024 real GBP/MWh)")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.7)
    ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_sensitivity_curve_zoom(rows, parameter, output_path) -> None:
    plot_sensitivity_curve(rows, parameter, output_path)


def plot_contour(reference: dict[str, float], x_parameter: Parameter, y_parameter: Parameter, output_path: str | Path) -> None:
    xs, ys, z = contour_grid(reference, x_parameter, y_parameter, 70, 70)
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    mesh = ax.contourf(xs, ys, z, levels=24, cmap="YlGnBu_r")
    levels = [value for value in TARGETS if np.nanmin(z) <= value <= np.nanmax(z)]
    if levels:
        lines = ax.contour(xs, ys, z, levels=levels, colors=COLORS["ink"], linewidths=0.9)
        ax.clabel(lines, fmt=lambda value: f"£{value:.0f}", fontsize=8)
    fig.colorbar(mesh, ax=ax, label="2024 real GBP/MWh")
    ax.scatter([x_parameter.reference_value], [y_parameter.reference_value], color=COLORS["amber"], s=50, label="Reference")
    ax.set(title="Conditional LCOE interaction", xlabel=f"{x_parameter.display_name} ({x_parameter.unit})", ylabel=f"{y_parameter.display_name} ({y_parameter.unit})")
    ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_contour_zoom(reference, x_parameter, y_parameter, output_path, x_range=None, y_range=None) -> None:
    plot_contour(reference, x_parameter, y_parameter, output_path)


def plot_uk_benchmarks(generation_rows: list[dict[str, object]], system_rows: list[dict[str, object]], output_path: str | Path) -> None:
    rows = [row for row in generation_rows if str(row.get("include_in_bands", "")).lower() in {"yes", "true", "1"}][:7]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    labels = [str(row["technology"]) for row in rows]
    lows = [float(row["value_low_gbp_per_mwh"] or row["value_mid_gbp_per_mwh"]) for row in rows]
    highs = [float(row["value_high_gbp_per_mwh"] or row["value_mid_gbp_per_mwh"]) for row in rows]
    y = np.arange(len(rows))
    ax.barh(y, [high - low for low, high in zip(lows, highs)], left=lows, color=COLORS["cyan"], alpha=.85)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set(title="UK generation-cost context (not like-for-like SBSP targets)", xlabel="2024 real GBP/MWh")
    ax.grid(axis="x", color=COLORS["grid"])
    _finish(fig, output_path)


def plot_break_even_frontier(rows: list[dict[str, object]], output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    for target in sorted({float(row["target_lcoe_gbp_per_mwh"]) for row in rows}):
        subset = [row for row in rows if float(row["target_lcoe_gbp_per_mwh"]) == target and row.get("max_launch_cost_gbp_per_kg_to_staging_orbit") not in (None, "")]
        if subset:
            ax.plot([100 * float(row["end_to_end_efficiency"]) for row in subset], [float(row["max_launch_cost_gbp_per_kg_to_staging_orbit"]) for row in subset], marker="o", label=f"£{target:.0f}/MWh")
    ax.set(title="Launch-cost threshold at computed chain efficiencies", xlabel="Computed end-to-end efficiency (%)", ylabel="Maximum launch cost to staging orbit (2024 real GBP/kg)")
    ax.grid(color=COLORS["grid"])
    ax.legend(frameon=False, ncol=2)
    _finish(fig, output_path)


def plot_combined_progress_frontier(rows: list[dict[str, object]], output_path: str | Path) -> None:
    available = [row for row in rows if row.get("progress_fraction") not in (None, "")]
    fig, ax = plt.subplots(figsize=(9.5, 5.3))
    ax.plot([float(row["target_lcoe_gbp_per_mwh"]) for row in available], [100 * float(row["progress_fraction"]) for row in available], marker="o", linewidth=2.5, color=COLORS["teal"])
    ax.set(title="Equal-fraction mathematical interpolation (not a roadmap)", xlabel="Target LCOE (2024 real GBP/MWh)", ylabel="Movement toward favourable bounds (%)")
    ax.invert_xaxis()
    ax.grid(color=COLORS["grid"])
    _finish(fig, output_path)


def plot_cost_component_waterfall(reference: dict[str, float], output_path: str | Path) -> None:
    result = calculate_lcoe(reference)
    components = sorted(result.lifecycle_cost_components_pv_gbp.items(), key=lambda item: abs(item[1]), reverse=True)
    fig, ax = plt.subplots(figsize=(10, 5.7))
    labels = [name.replace("_", " ").title() for name, _ in components]
    values = [value / result.discounted_lifetime_energy_mwh for _, value in components]
    colors = [COLORS["red"] if value < 0 else COLORS["teal"] for value in values]
    ax.barh(np.arange(len(values)), values, color=colors)
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.invert_yaxis()
    ax.set(title="Reference DCF LCOE components", xlabel="2024 real GBP/MWh (discounted cost / discounted energy)")
    ax.grid(axis="x", color=COLORS["grid"])
    _finish(fig, output_path)


def plot_one_way_lcoe_floors(rows: list[dict[str, object]], output_path: str | Path) -> None:
    shown = rows[:12]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    y = np.arange(len(shown))
    ax.barh(y, [float(row["best_lcoe_gbp_per_mwh"]) for row in shown], color=COLORS["teal"])
    ax.set_yticks(y, [str(row["display_name"]) for row in shown])
    ax.invert_yaxis()
    ax.axvline(150, color=COLORS["amber"], linestyle="--", label="£150 screen")
    ax.set(title="Best one-way LCOE within each explored range", xlabel="2024 real GBP/MWh")
    ax.grid(axis="x", color=COLORS["grid"])
    ax.legend(frameon=False)
    _finish(fig, output_path)


def plot_specific_mass_threshold_focus(sensitivity_rows: list[dict[str, object]], thresholds: list[dict[str, object]], output_path: str | Path) -> None:
    rows = [row for row in sensitivity_rows if row["parameter"] == "system_specific_mass_kg_per_kw_delivered"]
    parameter = Parameter("system_specific_mass_kg_per_kw_delivered", "System specific mass", "系统比质量", "kg/kW-delivered", 5, .5, 10, "lower", "", "", "", "", "", "", "")
    plot_sensitivity_curve(rows, parameter, output_path)


def plot_one_way_threshold_matrix(rows: list[dict[str, object]], output_path: str | Path) -> None:
    names = list(dict.fromkeys(str(row["display_name"]) for row in rows))
    targets = sorted({float(row["target_lcoe_gbp_per_mwh"]) for row in rows})
    matrix = np.zeros((len(names), len(targets)))
    for row in rows:
        matrix[names.index(str(row["display_name"]))][targets.index(float(row["target_lcoe_gbp_per_mwh"]))] = 1 if row["feasible"] else 0
    fig, ax = plt.subplots(figsize=(9.5, 8))
    ax.imshow(matrix, aspect="auto", cmap="GnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(targets)), [f"£{value:.0f}" for value in targets])
    ax.set_yticks(range(len(names)), names)
    ax.set(title="One-way target feasibility", xlabel="Target (2024 real GBP/MWh)")
    _finish(fig, output_path)
