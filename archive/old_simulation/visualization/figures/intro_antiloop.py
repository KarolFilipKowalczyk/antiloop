"""
Intro: How the Anti-Loop Rule Works
====================================

A 4-panel story showing the core mechanism:
1. A tiny network with finite state space
2. Pressure builds as states are used up
3. Growth escapes the loop
4. The one rule and what it produces
"""

import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

from simulation.engine import FSMNode, compute_hash, HASH_XOR
from visualization.style import (
    apply_style, PRESSURE_CMAP, ANTILOOP_BLUE, GROWTH_GREEN,
    DANGER_RED, CONTROL_GRAY, BG_LIGHT, TEXT_DARK, text_panel,
)

TITLE = "Intro: How the Anti-Loop Rule Works"

# Use 2-bit memory (4 states) so state space is small enough to draw
MEM_BITS = 2
CONFIG_SPACE = 2 ** MEM_BITS


def _make_ring(n, seed=42):
    """Create a ring graph with FSM nodes."""
    rng = np.random.default_rng(seed)
    G = nx.cycle_graph(n)
    nodes = {i: FSMNode(MEM_BITS, rng) for i in range(n)}
    return G, nodes, rng


def _step_all(G, nodes, rng, hash_fn=HASH_XOR):
    """Advance all nodes one step."""
    for nid in G.nodes():
        nb_configs = [nodes[n].config for n in G.neighbors(nid)]
        nodes[nid].step(nb_configs, hash_fn, rng=rng)


def _draw_state_bar(ax, node, nid, x, y, bar_w=0.12, bar_h=0.015):
    """Draw a compact state-space bar for one node.

    Shows a horizontal bar: filled portion = visited fraction,
    colored by pressure.
    """
    frac = node.pressure
    color = PRESSURE_CMAP(frac)

    # Background
    bg = mpatches.FancyBboxPatch(
        (x, y), bar_w, bar_h,
        boxstyle="round,pad=0.002",
        facecolor="#E5E7EB", edgecolor=CONTROL_GRAY, linewidth=0.5,
        transform=ax.transAxes, clip_on=False,
    )
    ax.add_patch(bg)

    # Fill
    if frac > 0:
        fill = mpatches.FancyBboxPatch(
            (x, y), bar_w * frac, bar_h,
            boxstyle="round,pad=0.002",
            facecolor=color, edgecolor="none",
            transform=ax.transAxes, clip_on=False,
        )
        ax.add_patch(fill)

    # Label
    ax.text(x + bar_w + 0.01, y + bar_h / 2, f"{frac:.0%}",
            fontsize=7, ha="left", va="center", color=TEXT_DARK,
            transform=ax.transAxes)


def _draw_graph(ax, G, nodes, layout, title, annotation=None):
    """Draw the graph with pressure-colored nodes."""
    nodelist = list(G.nodes())
    colors = [PRESSURE_CMAP(nodes[n].pressure) for n in nodelist]

    nx.draw_networkx_edges(G, layout, ax=ax, alpha=0.5, edge_color=CONTROL_GRAY, width=1.2)
    nx.draw_networkx_nodes(G, layout, ax=ax, nodelist=nodelist, node_color=colors,
                           node_size=280, edgecolors="#374151", linewidths=1)
    labels = {n: str(nodes[n].config) for n in nodelist}
    nx.draw_networkx_labels(G, layout, labels, ax=ax, font_size=8,
                            font_color="white", font_weight="bold")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.axis("off")

    if annotation:
        ax.text(0.5, -0.02, annotation, transform=ax.transAxes,
                fontsize=10, ha="center", va="top", style="italic",
                color="#4B5563")


def generate(out_dir):
    """Generate the intro figure."""
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle("How the Anti-Loop Rule Works",
                 fontsize=20, fontweight="bold", y=0.97)

    # ---- Panel 1: A tiny network ----
    ax = axes[0, 0]
    G, nodes, rng = _make_ring(8, seed=42)
    layout = nx.circular_layout(G)
    _draw_graph(ax, G, nodes, layout,
                "1. A tiny network",
                "Each node has 4 possible states.\n"
                "It remembers which ones it has visited.")

    # Draw pressure bars below graph
    sorted_nids = sorted(nodes.keys())
    bar_x = 0.3
    bar_y_start = 0.02
    for i, nid in enumerate(sorted_nids):
        _draw_state_bar(ax, nodes[nid], nid,
                        bar_x, bar_y_start - i * 0.025)

    # ---- Panel 2: Pressure builds ----
    ax = axes[0, 1]
    G2, nodes2, rng2 = _make_ring(8, seed=42)
    for _ in range(20):
        _step_all(G2, nodes2, rng2)
    layout2 = nx.circular_layout(G2)
    pressures = [nodes2[n].pressure for n in G2.nodes()]
    avg_p = np.mean(pressures)
    _draw_graph(ax, G2, nodes2, layout2,
                "2. Pressure builds",
                f"After 20 steps, average pressure = {avg_p:.0%}.\n"
                "Most states used up \u2014 a loop is coming!")

    for i, nid in enumerate(sorted(nodes2.keys())):
        _draw_state_bar(ax, nodes2[nid], nid,
                        bar_x, bar_y_start - i * 0.025)

    # ---- Panel 3: Growth escapes the loop ----
    ax = axes[1, 0]
    G3 = G2.copy()
    nodes3 = {}
    for nid in G2.nodes():
        n = FSMNode.__new__(FSMNode)
        n.config_space = nodes2[nid].config_space
        n.config = nodes2[nid].config
        n.visited = nodes2[nid].visited.copy()
        n.table = nodes2[nid].table.copy()
        nodes3[nid] = n
    rng3 = np.random.default_rng(123)

    stressed = max(nodes3.keys(), key=lambda n: nodes3[n].pressure)
    new_id = max(G3.nodes()) + 1
    G3.add_node(new_id)
    G3.add_edge(stressed, new_id)
    nodes3[new_id] = FSMNode(MEM_BITS, rng3)

    new_id2 = new_id + 1
    second_stressed = sorted(nodes3.keys(), key=lambda n: nodes3[n].pressure)[-2]
    G3.add_node(new_id2)
    G3.add_edge(second_stressed, new_id2)
    nodes3[new_id2] = FSMNode(MEM_BITS, rng3)

    for _ in range(5):
        _step_all(G3, nodes3, rng3)

    layout3 = nx.spring_layout(G3, seed=42, k=1.8)

    nodelist = list(G3.nodes())
    colors = []
    sizes = []
    for n in nodelist:
        if n in (new_id, new_id2):
            colors.append(GROWTH_GREEN)
            sizes.append(350)
        else:
            colors.append(PRESSURE_CMAP(nodes3[n].pressure))
            sizes.append(280)

    new_edges = {(stressed, new_id), (second_stressed, new_id2)}
    old_edges = [e for e in G3.edges() if e not in new_edges and (e[1], e[0]) not in new_edges]
    new_edge_list = [e for e in G3.edges() if e in new_edges or (e[1], e[0]) in new_edges]

    nx.draw_networkx_edges(G3, layout3, ax=ax, edgelist=old_edges,
                           alpha=0.4, edge_color=CONTROL_GRAY, width=1.5)
    nx.draw_networkx_edges(G3, layout3, ax=ax, edgelist=new_edge_list,
                           alpha=0.9, edge_color=GROWTH_GREEN, width=3.5)
    nx.draw_networkx_nodes(G3, layout3, ax=ax, nodelist=nodelist, node_color=colors,
                           node_size=sizes, edgecolors="#374151", linewidths=1)
    labels = {n: str(nodes3[n].config) for n in nodelist}
    nx.draw_networkx_labels(G3, layout3, labels, ax=ax, font_size=8,
                            font_color="white", font_weight="bold")

    ax.set_title("3. Growth escapes the loop", fontsize=14, fontweight="bold", pad=12)
    ax.axis("off")
    ax.text(0.5, -0.02,
            "Stressed nodes reach out. New connections provide\n"
            "fresh input, opening paths to unvisited states.",
            transform=ax.transAxes, fontsize=10, ha="center", va="top",
            style="italic", color="#4B5563")

    # ---- Panel 4: The rule ----
    ax = axes[1, 1]
    text_panel(ax, [
        "THE RULE",
        "",
        "If a node is about to loop,",
        "it grows a new connection.",
        "",
        "This single rule produces:",
        "",
        "  \u2022 Scale-free networks    (C3)",
        "  \u2022 Meaningful correlations (C1)",
        "  \u2022 A definition of harm   (C2)",
    ], fontsize=13)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    path = os.path.join(out_dir, "intro_antiloop.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")
