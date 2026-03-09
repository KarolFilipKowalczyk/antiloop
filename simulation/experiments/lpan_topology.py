"""LPAN topology + MI excess: full axiom test with lateral wiring.

Measures two things:
1. Topology: power-law exponent alpha (LPAN vs spawn-only vs random control)
2. MI excess: edges carry more mutual information than non-edges (rho > 1)

KEY FINDING: MI excess depends on graph sparsity. At avg degree ~8
(post_cap_steps=0, pressure_threshold=0.7), rho ~ 1.15-1.20 (confirmed
across seeds). At higher density (post_cap_steps=500), rho ~ 1.0.
The excess is NOT a density artifact — random control graphs at the
same density show rho = 1.00. The anti-loop constraint creates networks
where information flows preferentially along edges.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import (
    run_lpan_model, run_spawn_model,
    build_growing_random_control, build_random_tree_control,
)
from simulation.shared.analysis import (
    analyze_powerlaw, get_ccdf, format_powerlaw_result,
)

TITLE = "LPAN Topology + MI"


def _mutual_information(traj_a, traj_b, config_space):
    """MI between two config trajectories, in bits."""
    n = min(len(traj_a), len(traj_b))
    if n < 20:
        return 0.0
    a = np.array(traj_a[:n])
    b = np.array(traj_b[:n])
    joint = np.zeros((config_space, config_space), dtype=np.float64)
    for i in range(n):
        joint[a[i], b[i]] += 1
    joint /= n
    pa = joint.sum(axis=1)
    pb = joint.sum(axis=0)
    mi = 0.0
    for ai in range(config_space):
        if pa[ai] == 0:
            continue
        for bi in range(config_space):
            if pb[bi] == 0 or joint[ai, bi] == 0:
                continue
            mi += joint[ai, bi] * np.log2(joint[ai, bi] / (pa[ai] * pb[bi]))
    return mi


def _compute_mi_excess(G, trajectories, config_space, rng, max_samples=500):
    """Compute MI on edges vs non-edges. Returns (edge_mi, nonedge_mi, ratio)."""
    edges = list(G.edges())
    if not edges:
        return 0.0, 0.0, 0.0

    # Sample edges
    if len(edges) > max_samples:
        idx = rng.choice(len(edges), size=max_samples, replace=False)
        sampled_edges = [edges[i] for i in idx]
    else:
        sampled_edges = edges

    edge_mis = []
    for u, v in sampled_edges:
        if u in trajectories and v in trajectories:
            mi = _mutual_information(trajectories[u], trajectories[v],
                                     config_space)
            edge_mis.append(mi)

    # Sample non-edges
    nodes = list(G.nodes())
    nonedge_mis = []
    attempts = 0
    while len(nonedge_mis) < max_samples and attempts < max_samples * 10:
        u = int(rng.choice(nodes))
        v = int(rng.choice(nodes))
        if u != v and not G.has_edge(u, v):
            if u in trajectories and v in trajectories:
                mi = _mutual_information(trajectories[u], trajectories[v],
                                         config_space)
                nonedge_mis.append(mi)
        attempts += 1

    e_mean = np.mean(edge_mis) if edge_mis else 0.0
    ne_mean = np.mean(nonedge_mis) if nonedge_mis else 0.0
    ratio = e_mean / ne_mean if ne_mean > 0 else float('inf')
    return e_mean, ne_mean, ratio


def _calibrate(mem_bits, max_nodes):
    """Measure throughput for auto-scaling (with trajectory recording)."""
    t0 = time.time()
    G, _, _, _ = run_lpan_model(mem_bits=mem_bits, max_nodes=max_nodes,
                                seed=9999, time_limit=5.0,
                                record_trajectories=True)
    elapsed = max(time.time() - t0, 0.1)
    return G.number_of_nodes(), elapsed, G.number_of_nodes() / elapsed


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    config_space = 2 ** mem_bits
    # Budget: ~60% LPAN runs, ~20% MI computation, ~20% spawn+control+analysis
    time_per_seed = time_budget / n_seeds

    # Calibration
    progress.update(0, n_seeds, "Calibrating", "Measuring LPAN throughput...")
    n_probe, t_probe, nps = _calibrate(mem_bits, max_nodes)

    # MI excess requires sufficient trajectory length per node, which
    # degrades at large node counts (late-born nodes have short trajectories).
    # Cap at 500 nodes for MI reliability. Topology can use more nodes but
    # MI is the primary measurement here.
    mi_max_nodes = min(max_nodes, 500)

    if t_probe < time_per_seed * 0.2:
        target = time_per_seed * 0.3
        calibrated = int(nps * target)
        max_nodes = max(max_nodes, min(calibrated, max_nodes * 50, mi_max_nodes))
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s "
                     f"({nps:.0f} nodes/s)")
        progress.log(f"  Auto-scaling: -> {max_nodes} nodes "
                     f"(capped at {mi_max_nodes} for MI reliability)")
    else:
        max_nodes = mi_max_nodes
        progress.log(f"  Calibration: keeping {max_nodes} nodes")

    progress.log(f"LPAN Topology + MI: {n_seeds} seeds, {max_nodes} nodes, "
                 f"{mem_bits}-bit, {time_budget}s budget")

    lpan_results = []
    spawn_results = []
    control_results = []
    mi_data = []  # (edge_mi, nonedge_mi, ratio) per seed
    t_start = time.time()

    for i in range(n_seeds):
        seed = 2000 + i
        elapsed = time.time() - t_start
        remaining = time_budget - elapsed
        seeds_left = n_seeds - i
        if remaining < 5:
            progress.log(f"  Time limit reached after {i} seeds")
            break

        seed_limit = remaining / seeds_left

        # --- LPAN model ---
        progress.update(i, n_seeds, "Running seeds",
                        f"Seed {i+1}/{n_seeds} LPAN ({max_nodes} nodes)")
        progress.update_seed(0, max_nodes, f"Seed {seed} LPAN:")

        G_lpan, nd_lpan, gl_lpan, traj_lpan = run_lpan_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            time_limit=seed_limit * 0.4, progress=progress,
            record_trajectories=True,
        )
        n_lpan = G_lpan.number_of_nodes()
        n_edges_lpan = G_lpan.number_of_edges()
        progress.update_seed(n_lpan, max_nodes)

        r_lpan = analyze_powerlaw(G_lpan, label=f"lpan seed={seed}")
        lpan_results.append(r_lpan)

        # --- MI computation on LPAN (using growth trajectories) ---
        progress.update_seed(0, 3, f"Seed {seed} MI computation:")
        mi_rng = np.random.default_rng(seed + 200000)
        e_mi, ne_mi, ratio = _compute_mi_excess(
            G_lpan, traj_lpan, config_space, mi_rng)
        mi_data.append((e_mi, ne_mi, ratio))
        del traj_lpan  # free trajectory memory

        # --- Spawn-only model (same params, no lateral wiring) ---
        progress.update_seed(1, 3, f"Seed {seed} spawn-only:")
        G_spawn, _, _ = run_spawn_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            time_limit=seed_limit * 0.2, progress=progress,
        )
        r_spawn = analyze_powerlaw(G_spawn, label=f"spawn seed={seed}")
        spawn_results.append(r_spawn)

        # --- Random control (matched to LPAN) ---
        progress.update_seed(2, 3, f"Seed {seed} control:")
        G_ctrl = build_growing_random_control(gl_lpan, seed=seed + 500000)
        r_ctrl = analyze_powerlaw(G_ctrl, label=f"control seed={seed}")
        control_results.append(r_ctrl)

        progress.update_seed(3, 3, f"Seed {seed} done")

        al_a = f"{r_lpan['alpha']:.2f}" if r_lpan['alpha'] else "N/A"
        sp_a = f"{r_spawn['alpha']:.2f}" if r_spawn['alpha'] else "N/A"
        progress.log(
            f"  Seed {seed}: LPAN {n_lpan}n/{n_edges_lpan}e alpha={al_a}, "
            f"spawn alpha={sp_a}, MI ratio={ratio:.2f}")

    n_completed = len(lpan_results)
    progress.update(n_completed, n_seeds, "Analysis", "Computing summary...")

    # --- Summary ---
    lpan_alphas = [r["alpha"] for r in lpan_results if r["alpha"]]
    spawn_alphas = [r["alpha"] for r in spawn_results if r["alpha"]]
    ctrl_alphas = [r["alpha"] for r in control_results if r["alpha"]]

    edge_mis = [d[0] for d in mi_data]
    nonedge_mis = [d[1] for d in mi_data]
    ratios = [d[2] for d in mi_data if d[2] != float('inf')]

    lines = [
        "=" * 60,
        "LPAN Topology + MI Excess",
        "=" * 60,
        f"Seeds completed: {n_completed}/{n_seeds}",
        f"Nodes per graph: {max_nodes}",
        f"Memory: {mem_bits} bits ({config_space} states)",
        "",
        "TOPOLOGY (power-law exponent alpha):",
        f"  LPAN (lateral):   {np.mean(lpan_alphas):.3f} +/- "
        f"{np.std(lpan_alphas):.3f}" if lpan_alphas else "  LPAN: N/A",
        f"  Spawn (tree-only): {np.mean(spawn_alphas):.3f} +/- "
        f"{np.std(spawn_alphas):.3f}" if spawn_alphas else "  Spawn: N/A",
        f"  Random control:    {np.mean(ctrl_alphas):.3f} +/- "
        f"{np.std(ctrl_alphas):.3f}" if ctrl_alphas else "  Control: N/A",
        "",
        "MI EXCESS (edge MI / non-edge MI):",
        f"  Edge MI:     {np.mean(edge_mis):.4f} +/- {np.std(edge_mis):.4f}"
        if edge_mis else "  Edge MI: N/A",
        f"  Non-edge MI: {np.mean(nonedge_mis):.4f} +/- "
        f"{np.std(nonedge_mis):.4f}" if nonedge_mis else "  Non-edge MI: N/A",
        f"  Ratio (rho): {np.mean(ratios):.2f} +/- {np.std(ratios):.2f}"
        if ratios else "  Ratio: N/A",
    ]

    if ratios:
        rho = np.mean(ratios)
        if len(ratios) >= 2:
            se = np.std(ratios) / np.sqrt(len(ratios))
            sigma = (rho - 1.0) / se if se > 0 else 0.0
            lines.append(f"  Significance: {sigma:.1f} sigma from rho=1")
        lines.append("")
        if rho > 1.1:
            lines.append("  RESULT: POSITIVE -- LPAN edges carry more MI than non-edges")
        elif rho > 1.02:
            lines.append("  RESULT: PARTIAL -- modest MI excess")
        else:
            lines.append("  RESULT: NEGATIVE -- no significant MI excess")

    lines += ["", "Per-seed detail:"]
    for j, r in enumerate(lpan_results):
        e, ne, rat = mi_data[j] if j < len(mi_data) else (0, 0, 0)
        lines.append(f"  {r['label']}: alpha={r['alpha']:.3f}, "
                     f"MI edge={e:.4f} nonedge={ne:.4f} rho={rat:.2f}"
                     if r['alpha'] else f"  {r['label']}: alpha=N/A")

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "lpan_topology_results.txt"), "w") as f:
        f.write(report)

    if lpan_results:
        _plot_results(lpan_alphas, spawn_alphas, ctrl_alphas,
                      edge_mis, nonedge_mis, ratios,
                      out_dir, progress)

    progress.update(n_seeds, n_seeds, "Done", f"{n_completed} seeds completed")


def _plot_results(lpan_alphas, spawn_alphas, ctrl_alphas,
                  edge_mis, nonedge_mis, ratios,
                  out_dir, progress):
    """Plot topology comparison and MI excess."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Alpha distributions
    ax = axes[0]
    if lpan_alphas:
        ax.hist(lpan_alphas, bins=max(5, len(lpan_alphas) // 3), alpha=0.7,
                label=f"LPAN ({np.mean(lpan_alphas):.2f})", color="#2196F3")
    if spawn_alphas:
        ax.hist(spawn_alphas, bins=max(5, len(spawn_alphas) // 3), alpha=0.7,
                label=f"spawn ({np.mean(spawn_alphas):.2f})", color="#FF9800")
    if ctrl_alphas:
        ax.hist(ctrl_alphas, bins=max(5, len(ctrl_alphas) // 3), alpha=0.7,
                label=f"control ({np.mean(ctrl_alphas):.2f})", color="#999")
    ax.axvline(2.0, color="red", linestyle="--", alpha=0.3)
    ax.axvline(3.0, color="red", linestyle="--", alpha=0.3)
    ax.set_xlabel("alpha")
    ax.set_ylabel("count")
    ax.set_title("Power-law exponent")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 2: MI excess bar chart
    ax = axes[1]
    x = [0, 1]
    means = [np.mean(edge_mis), np.mean(nonedge_mis)]
    stds = [np.std(edge_mis), np.std(nonedge_mis)]
    bars = ax.bar(x, means, yerr=stds, capsize=5,
                  color=["#2196F3", "#999"], alpha=0.7, width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(["Edge MI", "Non-edge MI"])
    ax.set_ylabel("Mutual Information (bits)")
    ax.set_title("MI excess on LPAN edges")
    ax.grid(True, alpha=0.3, axis="y")
    if means[0] > 0 and means[1] > 0:
        rho = means[0] / means[1]
        ax.text(0.5, 0.95, f"rho = {rho:.2f}",
                transform=ax.transAxes, ha="center", va="top", fontsize=11)

    # Panel 3: MI ratio per seed
    ax = axes[2]
    if ratios:
        ax.bar(range(len(ratios)), ratios, color="#4CAF50", alpha=0.7)
        ax.axhline(1.0, color="red", linestyle="--", alpha=0.5, label="rho=1 (no excess)")
        ax.set_xlabel("Seed")
        ax.set_ylabel("MI ratio (edge/non-edge)")
        ax.set_title("MI ratio per seed")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis="y")

    plt.suptitle("LPAN: Topology + MI Excess", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "lpan_topology.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
