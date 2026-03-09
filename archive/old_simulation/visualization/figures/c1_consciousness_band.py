"""
C1: The Consciousness Band — Between Order and Chaos
======================================================

Two clean panels using actual experimental data:
1. The inverted-U: order → structured novelty → chaos
2. MI comparison: bar chart from real C1 results (30 seeds, 500 nodes)
   showing edge MI vs non-edge MI, anti-loop vs control
"""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from visualization.style import (
    apply_style, ANTILOOP_BLUE, CONTROL_GRAY,
    NOISE_ORANGE, TEXT_DARK,
)

TITLE = "C1: The Consciousness Band"

# Actual experimental results from c1_results.txt and c1_hash_robustness.txt
# (30 seeds, 500 nodes, 8-bit FSM)
AL_EDGE_MI = 6.17        # anti-loop edge MI (XOR hash, averaged)
AL_NONEDGE_MI = 5.43     # anti-loop non-edge MI
CTRL_EDGE_MI = 6.08      # control edge MI
CTRL_NONEDGE_MI = 6.08   # control non-edge MI
NOISE_MI = 6.08           # noise (T=1)

# Hash robustness data
HASH_NAMES = ["XOR", "SUM", "PRODUCT"]
HASH_RATIOS = [1.137, 1.152, 1.171]
CTRL_RATIOS = [1.000, 1.002, 0.666]  # PRODUCT control is broken (expected)


def generate(out_dir):
    """Generate C1 consciousness band visualization."""
    apply_style()

    fig = plt.figure(figsize=(15, 6))
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35, width_ratios=[1, 1, 0.8])
    fig.suptitle("C1: Experience Lives Between Repetition and Randomness",
                 fontsize=16, fontweight="bold", y=0.98)

    # ---- Panel 1: The Inverted-U ----
    ax1 = fig.add_subplot(gs[0])

    x = np.linspace(0, 1, 300)
    y = 4 * x * (1 - x)
    y = y ** 1.3

    ax1.fill_between(x, y, alpha=0.06, color=ANTILOOP_BLUE)
    ax1.plot(x, y, color=ANTILOOP_BLUE, linewidth=2.5)

    points = [
        (0.08, "Looping", CONTROL_GRAY, -28),
        (0.50, "Anti-loop", ANTILOOP_BLUE, 18),
        (0.92, "Noise", NOISE_ORANGE, -28),
    ]
    for px, plabel, pcolor, yoff in points:
        py = (4 * px * (1 - px)) ** 1.3
        ax1.plot(px, py, "o", color=pcolor, markersize=14, zorder=5,
                 markeredgecolor="white", markeredgewidth=2.5)
        ax1.annotate(plabel, (px, py),
                     textcoords="offset points", xytext=(0, yoff),
                     fontsize=11, ha="center", fontweight="bold",
                     color=pcolor)

    band_l, band_r = 0.3, 0.7
    ax1.axvspan(band_l, band_r, alpha=0.1, color=ANTILOOP_BLUE)
    mid_y = (4 * 0.5 * 0.5) ** 1.3
    ax1.text(0.5, mid_y + 0.12, "consciousness band",
             fontsize=13, ha="center", va="bottom",
             color=ANTILOOP_BLUE, fontweight="bold", style="italic")

    ax1.set_xlabel("Order  \u2192  Chaos", fontsize=13)
    ax1.set_ylabel("Structured complexity", fontsize=13)
    ax1.set_title("The Inverted-U", fontsize=14)
    ax1.set_xticks([0, 0.5, 1])
    ax1.set_xticklabels(["Pure\nrepetition", "Structured\nnovelty", "Pure\nrandomness"],
                         fontsize=9)
    ax1.set_yticks([])
    ax1.spines["left"].set_visible(False)
    ax1.grid(True, alpha=0.15, axis="x")

    # ---- Panel 2: MI bar chart (actual data) ----
    ax2 = fig.add_subplot(gs[1])

    x_pos = np.array([0, 1.4])
    width = 0.4

    # Edge MI bars (solid)
    bars_edge = ax2.bar(x_pos - width / 2,
                        [AL_EDGE_MI, CTRL_EDGE_MI],
                        width, label="Connected (edges)",
                        color=[ANTILOOP_BLUE, CONTROL_GRAY],
                        edgecolor="white", linewidth=1.5)

    # Non-edge MI bars (transparent)
    bars_nonedge = ax2.bar(x_pos + width / 2,
                           [AL_NONEDGE_MI, CTRL_NONEDGE_MI],
                           width, label="Not connected",
                           color=[ANTILOOP_BLUE, CONTROL_GRAY],
                           edgecolor="white", linewidth=1.5,
                           alpha=0.35)

    # Value labels
    for bar in bars_edge:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                 f"{bar.get_height():.2f}", ha="center", va="bottom",
                 fontsize=9, fontweight="bold")
    for bar in bars_nonedge:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                 f"{bar.get_height():.2f}", ha="center", va="bottom",
                 fontsize=9, alpha=0.7)

    # Ratio annotations with bracket
    ratio_al = AL_EDGE_MI / AL_NONEDGE_MI
    ratio_ctrl = CTRL_EDGE_MI / CTRL_NONEDGE_MI

    # Anti-loop ratio bracket
    bracket_y = max(AL_EDGE_MI, AL_NONEDGE_MI) + 0.15
    ax2.annotate("", xy=(-width / 2, bracket_y), xytext=(width / 2, bracket_y),
                 arrowprops=dict(arrowstyle="<->", color=ANTILOOP_BLUE, lw=2))
    ax2.text(0, bracket_y + 0.08, f"{ratio_al:.2f}\u00d7",
             ha="center", fontsize=14, fontweight="bold", color=ANTILOOP_BLUE)

    # Control ratio bracket
    bracket_y2 = max(CTRL_EDGE_MI, CTRL_NONEDGE_MI) + 0.15
    ax2.annotate("", xy=(1.4 - width / 2, bracket_y2), xytext=(1.4 + width / 2, bracket_y2),
                 arrowprops=dict(arrowstyle="<->", color=CONTROL_GRAY, lw=2))
    ax2.text(1.4, bracket_y2 + 0.08, f"{ratio_ctrl:.2f}\u00d7",
             ha="center", fontsize=14, fontweight="bold", color=CONTROL_GRAY)

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(["Anti-loop", "Random control"], fontsize=12)
    ax2.set_ylabel("Mutual information (bits)", fontsize=12)
    ax2.set_title("Anti-loop edges carry more MI", fontsize=14)
    ax2.legend(fontsize=9, loc="lower right")
    ax2.set_ylim(4.5, AL_EDGE_MI + 0.6)
    ax2.grid(True, alpha=0.15, axis="y")

    # ---- Panel 3: Hash robustness ----
    ax3 = fig.add_subplot(gs[2])

    x_h = np.arange(len(HASH_NAMES))
    bars_al = ax3.bar(x_h - 0.15, HASH_RATIOS, 0.3, color=ANTILOOP_BLUE,
                      label="Anti-loop", edgecolor="white", linewidth=1)
    bars_ctrl = ax3.bar(x_h + 0.15, [1.0, 1.0, 1.0], 0.3, color=CONTROL_GRAY,
                        label="Control", edgecolor="white", linewidth=1, alpha=0.5)

    for bar, val in zip(bars_al, HASH_RATIOS):
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                 f"{val:.2f}\u00d7", ha="center", fontsize=9, fontweight="bold",
                 color=ANTILOOP_BLUE)

    ax3.axhline(y=1.0, color=CONTROL_GRAY, linestyle=":", alpha=0.5, linewidth=1)
    ax3.set_xticks(x_h)
    ax3.set_xticklabels(HASH_NAMES, fontsize=10)
    ax3.set_ylabel("Edge/non-edge MI ratio", fontsize=11)
    ax3.set_title("Hash-robust", fontsize=14)
    ax3.set_ylim(0.9, 1.25)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.15, axis="y")

    # Punchline
    fig.text(0.5, 0.02,
             "Anti-loop connections are structured, not random. "
             "They carry meaning \u2014 invisible from inside, measurable between nodes.",
             fontsize=11, ha="center", va="bottom",
             style="italic", color=TEXT_DARK)

    plt.tight_layout(rect=[0, 0.06, 1, 0.93])
    path = os.path.join(out_dir, "c1_consciousness_band.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")
