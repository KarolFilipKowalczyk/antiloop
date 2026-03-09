"""
C3: How the Anti-Loop Rule Produces Scale-Free Networks
=========================================================

Shows:
1. Top row: 3 growth snapshots (10 → 30 → 50 nodes) — big enough to read
2. Bottom-left: Degree distribution CCDF (log-log) with clean axis labels
3. Bottom-right: Final network with hubs labeled, node size ∝ degree
"""

import os

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx
import numpy as np

from simulation.engine import (
    FSMNode, HASH_XOR, init_ring_graph,
    build_growing_random_control, GrowthLog,
)
from simulation.analysis import get_ccdf
from visualization.style import (
    apply_style, PRESSURE_CMAP, ANTILOOP_BLUE, CONTROL_GRAY,
    GROWTH_GREEN, DANGER_RED, TEXT_DARK,
)

TITLE = "C3: From Ring to Scale-Free"

MEM_BITS = 4
MAX_NODES = 50
PRESSURE_THRESHOLD = 0.7
SPAWN_PROB = 0.3
SEED = 7


def _run_antiloop_with_snapshots(snapshot_sizes):
    """Run anti-loop growth capturing graph snapshots at specific sizes."""
    rng = np.random.default_rng(SEED)
    G, nodes = init_ring_graph(10, MEM_BITS, rng)
    growth_log = GrowthLog()
    growth_log.record(0, G.number_of_nodes(), G.number_of_edges())

    snapshots = []
    snap_pressures = []
    captured = set()

    if G.number_of_nodes() >= snapshot_sizes[0]:
        snapshots.append(G.copy())
        snap_pressures.append({n: nodes[n].pressure for n in G.nodes()})
        captured.add(snapshot_sizes[0])

    step = 0
    max_steps = 5000
    edge_only_steps = 0
    at_cap = False

    while step < max_steps:
        step += 1
        for nid in list(G.nodes()):
            nb_configs = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb_configs, HASH_XOR, rng=rng)

        stressed = [n for n in G.nodes() if nodes[n].pressure > PRESSURE_THRESHOLD]
        if stressed:
            rng.shuffle(stressed)
            for nid in stressed[:5]:
                if G.number_of_nodes() < MAX_NODES:
                    if rng.random() < SPAWN_PROB:
                        new_id = max(G.nodes()) + 1
                        G.add_node(new_id)
                        G.add_edge(nid, new_id)
                        nodes[new_id] = FSMNode(MEM_BITS, rng)
                    else:
                        non_nb = [n for n in G.nodes()
                                  if n != nid and not G.has_edge(nid, n)]
                        if non_nb:
                            target = rng.choice(non_nb)
                            G.add_edge(nid, target)
                else:
                    non_nb = [n for n in G.nodes()
                              if n != nid and not G.has_edge(nid, n)]
                    if non_nb:
                        target = rng.choice(non_nb)
                        G.add_edge(nid, target)

        growth_log.record(step, G.number_of_nodes(), G.number_of_edges())

        nn = G.number_of_nodes()
        for sz in snapshot_sizes:
            if sz not in captured and nn >= sz:
                snapshots.append(G.copy())
                snap_pressures.append({n: nodes[n].pressure for n in G.nodes()})
                captured.add(sz)

        if nn >= MAX_NODES:
            if not at_cap:
                at_cap = True
                edge_only_steps = 0
            edge_only_steps += 1
            if edge_only_steps >= 200:
                break

    if len(snapshots) < len(snapshot_sizes):
        snapshots.append(G.copy())
        snap_pressures.append({n: nodes[n].pressure for n in G.nodes()})

    return snapshots, snap_pressures, G, nodes, growth_log


def generate(out_dir):
    """Generate C3 scale-free visualization."""
    apply_style()

    snapshot_sizes = [10, 30, MAX_NODES]
    snapshots, snap_pressures, G_final, nodes_final, growth_log = \
        _run_antiloop_with_snapshots(snapshot_sizes)

    G_ctrl = build_growing_random_control(growth_log, seed=SEED + 1000)
    layout_full = nx.spring_layout(G_final, seed=42, k=1.2 / MAX_NODES ** 0.4)

    # ---- Figure layout: 2 rows ----
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3,
                           height_ratios=[1, 1.2])

    fig.suptitle("C3: The Anti-Loop Rule Produces Scale-Free Networks",
                 fontsize=17, fontweight="bold", y=0.98)

    # ---- Top row: 3 growth snapshots ----
    stage_labels = [
        f"Start: {snapshot_sizes[0]} nodes",
        f"Growing: {snapshot_sizes[1]} nodes",
        f"Final: {snapshot_sizes[2]} nodes",
    ]

    for i in range(min(3, len(snapshots))):
        ax = fig.add_subplot(gs[0, i])
        snap = snapshots[i]
        pressures = snap_pressures[i]

        pos = {n: layout_full[n] for n in snap.nodes() if n in layout_full}
        if not pos:
            pos = nx.spring_layout(snap, seed=42)

        nodelist = [n for n in snap.nodes() if n in pos]
        colors = [PRESSURE_CMAP(pressures.get(n, 0.5)) for n in nodelist]
        degrees = dict(snap.degree())
        sizes = [30 + 150 * (degrees.get(n, 1) / max(degrees.values(), default=1))
                 for n in nodelist]

        nx.draw_networkx_edges(snap, pos, ax=ax, alpha=0.3,
                               edge_color=CONTROL_GRAY, width=0.8)
        nx.draw_networkx_nodes(snap, pos, ax=ax, nodelist=nodelist,
                               node_color=colors, node_size=sizes,
                               edgecolors="#374151", linewidths=0.5)

        ax.set_title(stage_labels[i], fontsize=12, fontweight="bold")
        ax.axis("off")

    # ---- Bottom-left: Degree distribution CCDF ----
    ax_ccdf = fig.add_subplot(gs[1, :2])

    deg_al, ccdf_al = get_ccdf(G_final)
    deg_ctrl, ccdf_ctrl = get_ccdf(G_ctrl)

    ax_ccdf.loglog(deg_al, ccdf_al, "o-", color=ANTILOOP_BLUE,
                   markersize=6, linewidth=2, label="Anti-loop", alpha=0.9)
    ax_ccdf.loglog(deg_ctrl, ccdf_ctrl, "s--", color=CONTROL_GRAY,
                   markersize=5, linewidth=1.5, label="Random (matched growth)",
                   alpha=0.7)

    # Power-law reference
    x_ref = np.linspace(max(deg_al[0], 1), deg_al[-1], 50)
    y_ref = (x_ref / x_ref[0]) ** -1.5
    y_ref *= ccdf_al[0]
    ax_ccdf.loglog(x_ref, y_ref, ":", color=DANGER_RED, alpha=0.5,
                   linewidth=1.5, label="Power law reference (\u03b1 \u2248 2.5)")

    ax_ccdf.set_xlabel("Degree (k)", fontsize=13)
    ax_ccdf.set_ylabel("P(K \u2265 k)", fontsize=13)
    ax_ccdf.set_title("Degree Distribution: Straight Line = Power Law", fontsize=14)
    ax_ccdf.legend(fontsize=10, loc="lower left")
    ax_ccdf.grid(True, alpha=0.2, which="both")

    # Clean integer tick labels — no scientific notation
    from matplotlib.ticker import ScalarFormatter, MaxNLocator
    for axis in [ax_ccdf.xaxis, ax_ccdf.yaxis]:
        axis.set_major_formatter(ScalarFormatter())
        axis.get_major_formatter().set_scientific(False)
        axis.get_major_formatter().set_useOffset(False)

    # ---- Bottom-right: Final network, node size ∝ degree ----
    ax_hub = fig.add_subplot(gs[1, 2])

    degrees = dict(G_final.degree())
    max_deg = max(degrees.values())
    sizes = [40 + 500 * (degrees[n] / max_deg) ** 1.5 for n in G_final.nodes()]
    colors = [PRESSURE_CMAP(nodes_final[n].pressure) for n in G_final.nodes()]

    nx.draw_networkx_edges(G_final, layout_full, ax=ax_hub,
                           alpha=0.12, edge_color=CONTROL_GRAY, width=0.5)
    nx.draw_networkx_nodes(G_final, layout_full, ax=ax_hub,
                           node_color=colors, node_size=sizes,
                           edgecolors="#374151", linewidths=0.3)

    # Label top 3 hubs
    top_hubs = sorted(degrees, key=degrees.get, reverse=True)[:3]
    for h in top_hubs:
        x, y = layout_full[h]
        ax_hub.annotate(f"deg={degrees[h]}", (x, y),
                        textcoords="offset points", xytext=(12, 12),
                        fontsize=9, color=TEXT_DARK, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="#6B7280", lw=1))

    ax_hub.set_title("Hubs Emerge Naturally", fontsize=14)
    ax_hub.axis("off")

    ax_hub.text(0.5, -0.08,
                "A few nodes become highly connected \u2014\n"
                "the same pattern found in brains, the internet,\n"
                "and social networks.",
                transform=ax_hub.transAxes, fontsize=10, ha="center",
                va="top", style="italic", color="#4B5563")

    path = os.path.join(out_dir, "c3_scalefree.png")
    plt.savefig(path)
    plt.close()
    print(f"  Saved: {path}")
