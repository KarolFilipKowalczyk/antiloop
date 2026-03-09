"""
Shared styling for antiloop educational visualizations.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import numpy as np

# ============================================================
# Color palette
# ============================================================

ANTILOOP_BLUE = "#2563EB"
CONTROL_GRAY = "#9CA3AF"
DANGER_RED = "#DC2626"
GROWTH_GREEN = "#16A34A"
NOISE_ORANGE = "#F59E0B"
BG_LIGHT = "#F9FAFB"
TEXT_DARK = "#1F2937"

# Pressure colormap: green (low) → yellow → red (high)
PRESSURE_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "pressure", [GROWTH_GREEN, "#FDE047", DANGER_RED]
)


def apply_style():
    """Set matplotlib defaults for clean educational figures."""
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "legend.framealpha": 0.9,
        "legend.edgecolor": "#D1D5DB",
        "grid.alpha": 0.25,
    })


def pressure_colors(nodes_dict):
    """Return list of colors for nodes based on their loop pressure."""
    pressures = [nodes_dict[nid].pressure for nid in sorted(nodes_dict)]
    return [PRESSURE_CMAP(p) for p in pressures]


def draw_graph_state(ax, G, nodes_dict=None, layout=None,
                     node_colors=None, node_size=300,
                     highlight_nodes=None, highlight_edges=None,
                     removed_edges=None, edge_alpha=0.4,
                     title="", show_labels=True):
    """Draw a networkx graph with optional pressure coloring and highlights.

    Args:
        ax: matplotlib axes
        G: networkx graph
        nodes_dict: {nid: FSMNode} — used for pressure colors if node_colors is None
        layout: precomputed pos dict (spring layout computed if None)
        node_colors: explicit color list/array (overrides pressure coloring)
        node_size: base node size (scalar or per-node array)
        highlight_nodes: set of node ids to draw with thick border
        highlight_edges: set of (u,v) tuples to draw thick
        removed_edges: set of (u,v) tuples to draw as dashed gray
        edge_alpha: alpha for normal edges
        title: axes title
        show_labels: whether to show node state labels inside nodes
    Returns:
        layout dict (so caller can reuse it)
    """
    if layout is None:
        layout = nx.spring_layout(G, seed=42, k=1.5 / max(1, len(G)) ** 0.5)

    nodelist = list(G.nodes())
    if node_colors is None and nodes_dict is not None:
        colors = [PRESSURE_CMAP(nodes_dict[n].pressure) if n in nodes_dict
                  else CONTROL_GRAY for n in nodelist]
    elif node_colors is not None:
        colors = node_colors
    else:
        colors = ANTILOOP_BLUE

    # Draw edges
    normal_edges = [e for e in G.edges() if not (
        highlight_edges and (e in highlight_edges or (e[1], e[0]) in highlight_edges)
    )]
    nx.draw_networkx_edges(G, layout, ax=ax, edgelist=normal_edges,
                           alpha=edge_alpha, edge_color="#9CA3AF", width=1)

    if highlight_edges:
        hl = [(u, v) for u, v in G.edges()
              if (u, v) in highlight_edges or (v, u) in highlight_edges]
        nx.draw_networkx_edges(G, layout, ax=ax, edgelist=hl,
                               alpha=0.8, edge_color=ANTILOOP_BLUE, width=2.5)

    if removed_edges:
        nx.draw_networkx_edges(G, layout, ax=ax, edgelist=list(removed_edges),
                               alpha=0.35, edge_color=DANGER_RED,
                               width=1, style="dashed")

    # Draw nodes
    edgecolors = ["black" if (highlight_nodes and n in highlight_nodes)
                  else "#6B7280" for n in nodelist]
    linewidths = [2.5 if (highlight_nodes and n in highlight_nodes)
                  else 0.5 for n in nodelist]
    nx.draw_networkx_nodes(G, layout, ax=ax, nodelist=nodelist, node_color=colors,
                           node_size=node_size, edgecolors=edgecolors,
                           linewidths=linewidths)

    if show_labels and nodes_dict:
        labels = {n: str(nodes_dict[n].config) if n in nodes_dict else ""
                  for n in nodelist}
        nx.draw_networkx_labels(G, layout, labels, ax=ax, font_size=7,
                                font_color="white", font_weight="bold")

    ax.set_title(title)
    ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.1)
    ax.set_ylim(ax.get_ylim()[0] - 0.1, ax.get_ylim()[1] + 0.1)
    ax.set_aspect("equal")
    ax.axis("off")
    return layout


def draw_state_space_bar(ax, node, x, y, width=0.8, height=0.15, label=None):
    """Draw a small horizontal bar showing visited/total states for a node.

    Used in the intro figure to show how state space fills up.
    """
    total = node.config_space
    visited = len(node.visited)
    frac = visited / total

    # Background (total)
    ax.barh(y, width, height=height, left=x, color="#E5E7EB",
            edgecolor="#9CA3AF", linewidth=0.5)
    # Fill (visited)
    ax.barh(y, width * frac, height=height, left=x,
            color=PRESSURE_CMAP(frac), edgecolor="none")

    if label:
        ax.text(x + width + 0.05, y, label, fontsize=7, va="center")


def add_annotation(ax, text, xy, xytext, fontsize=10):
    """Add annotation with arrow."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fontsize,
                arrowprops=dict(arrowstyle="->", color="#6B7280", lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7",
                          edgecolor="#F59E0B", alpha=0.9),
                ha="center", va="center")


def text_panel(ax, lines, fontsize=13):
    """Turn an axes into a clean text-only panel."""
    ax.axis("off")
    text = "\n".join(lines)
    ax.text(0.5, 0.5, text, transform=ax.transAxes,
            fontsize=fontsize, ha="center", va="center",
            family="monospace", linespacing=1.8,
            bbox=dict(boxstyle="round,pad=0.8", facecolor=BG_LIGHT,
                      edgecolor="#D1D5DB", linewidth=1))
