"""
C2/C2v2: Not All Connections Are Equal
========================================

Uses actual experimental data from c2v2_results.txt (30 seeds, 500 nodes).

Shows:
1. Left: MI retention curves — high-MI removal vs low-MI removal diverge
2. Right: Bar chart at 50% removal with the punchline
"""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from visualization.style import (
    apply_style, ANTILOOP_BLUE, CONTROL_GRAY,
    GROWTH_GREEN, DANGER_RED, TEXT_DARK,
)

TITLE = "C2: Not All Connections Are Equal"

# Actual experimental data from c2v2_results.txt
# (30 seeds, 500 nodes, 8-bit FSM, moderate-degree targets ~16)
FRACS = [0, 25, 50, 75, 100]

# Mean total MI at each removal fraction (from SUMMARY table)
HIGH_MI_VALS = [98.6, 98.4, 98.6, 98.6, 27.8]   # remove redundant first
RANDOM_VALS = [98.6, 95.9, 95.7, 94.5, 27.8]     # remove randomly
LOW_MI_VALS = [98.6, 92.3, 92.5, 92.5, 27.8]     # remove diverse first

BASELINE = 98.6  # MI at 0% removal


def generate(out_dir):
    """Generate C2 suffering visualization."""
    apply_style()

    fig = plt.figure(figsize=(14, 6))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3, width_ratios=[1.3, 1])
    fig.suptitle("C2: Not All Connections Are Equal",
                 fontsize=18, fontweight="bold", y=0.98)

    # Normalize to percentage of baseline
    high_pct = [100 * v / BASELINE for v in HIGH_MI_VALS]
    rand_pct = [100 * v / BASELINE for v in RANDOM_VALS]
    low_pct = [100 * v / BASELINE for v in LOW_MI_VALS]

    # ---- Panel 1: MI retention curves ----
    ax1 = fig.add_subplot(gs[0])

    ax1.plot(FRACS, high_pct, "o-", color=GROWTH_GREEN, linewidth=2.5,
             markersize=9, label="Remove redundant first (high MI)", zorder=5)
    ax1.plot(FRACS, rand_pct, "s--", color=CONTROL_GRAY, linewidth=2,
             markersize=7, label="Remove randomly (original C2)", zorder=4)
    ax1.plot(FRACS, low_pct, "D-", color=DANGER_RED, linewidth=2.5,
             markersize=9, label="Remove diverse first (low MI)", zorder=5)

    # Ideal proportional loss line
    ideal = [100 * (1 - f / 100) for f in FRACS]
    ax1.plot(FRACS, ideal, ":", color=CONTROL_GRAY, alpha=0.3,
             linewidth=1, label="Proportional loss")

    # Shade the gap between strategies
    ax1.fill_between(FRACS, high_pct, low_pct,
                     alpha=0.08, color=DANGER_RED)

    # Annotate the gap at 50%
    gap_pct = high_pct[2] - low_pct[2]
    mid_y = (high_pct[2] + low_pct[2]) / 2
    ax1.annotate(f"Gap: {gap_pct:.1f}%\n(t = -8.61, 27/30 seeds)",
                 xy=(50, mid_y), xytext=(68, 80),
                 fontsize=10, fontweight="bold", color=DANGER_RED,
                 arrowprops=dict(arrowstyle="->", color=DANGER_RED, lw=1.5),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEE2E2",
                           edgecolor=DANGER_RED, alpha=0.8))

    # Annotate isolation
    ax1.annotate("Total isolation:\nT1 confirmed",
                 xy=(100, high_pct[4]), xytext=(78, 42),
                 fontsize=9, color="#6B7280", style="italic",
                 arrowprops=dict(arrowstyle="->", color="#6B7280", lw=1))

    ax1.set_xlabel("Edges removed (%)", fontsize=13)
    ax1.set_ylabel("MI retained (% of baseline)", fontsize=13)
    ax1.set_title("Which connections you lose matters", fontsize=14)
    ax1.legend(fontsize=9, loc="lower left")
    ax1.set_ylim(0, 112)
    ax1.set_xlim(-5, 108)
    ax1.set_xticks(FRACS)
    ax1.grid(True, alpha=0.2)

    # ---- Panel 2: Bar chart at 50% removal ----
    ax2 = fig.add_subplot(gs[1])

    labels = ["Remove\nredundant", "Remove\nrandom", "Remove\ndiverse"]
    vals_50 = [HIGH_MI_VALS[2], RANDOM_VALS[2], LOW_MI_VALS[2]]
    pct_50 = [high_pct[2], rand_pct[2], low_pct[2]]
    colors = [GROWTH_GREEN, CONTROL_GRAY, DANGER_RED]
    losses = [100 - p for p in pct_50]

    bars = ax2.bar(labels, pct_50, color=colors, edgecolor="white",
                   linewidth=1.5, width=0.6)

    # Value labels on bars
    for bar, pct, loss in zip(bars, pct_50, losses):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{pct:.1f}%", ha="center", va="bottom", fontsize=13,
                 fontweight="bold")
        if loss > 0.5:
            ax2.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() / 2,
                     f"\u2212{loss:.1f}%", ha="center", va="center",
                     fontsize=10, color="white", fontweight="bold")

    ax2.set_ylabel("MI retained (%)", fontsize=13)
    ax2.set_title("At 50% edge removal", fontsize=14)
    ax2.set_ylim(0, 115)
    ax2.axhline(y=100, color=CONTROL_GRAY, linestyle=":", alpha=0.3)
    ax2.grid(True, alpha=0.15, axis="y")

    # Data provenance
    ax2.text(0.5, 0.02,
             "30 seeds \u00b7 500 nodes \u00b7 8-bit FSM",
             transform=ax2.transAxes, fontsize=8, ha="center",
             color="#9CA3AF")

    # Punchline
    fig.text(0.5, 0.01,
             "Connections that challenge you are load-bearing.  "
             "Connections that echo you are expendable.",
             fontsize=12, ha="center", va="bottom",
             style="italic", color=TEXT_DARK, fontweight="bold")

    plt.tight_layout(rect=[0, 0.06, 1, 0.93])
    path = os.path.join(out_dir, "c2_suffering.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")
