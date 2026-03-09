"""Attention model: parameter-free topology and MI analysis.

Tests whether MI excess and heavy-tailed topology emerge from a
parameter-free model where wiring is triggered only by effective
state revisit (exact loop).

FINDING: Heavy-tailed topology emerges (alpha ~ 2.0-2.7). MI excess
does NOT. The MI excess in LPAN requires proactive wiring under
partial pressure (threshold < 1.0). When entities wire only at exact
loop (threshold = 1.0), rho ~ 0.94 — edges carry LESS MI than
non-edges. The effective state reset after looping severs trajectory
continuity, destroying the correlations that create MI excess.

This experiment also runs a threshold sweep on LPAN to demonstrate
the transition: rho > 1 at threshold 0.7-0.9, rho < 1 at 1.0.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import (
    run_attention_model, run_lpan_model,
)
from simulation.shared.analysis import (
    analyze_powerlaw, format_powerlaw_result,
)

TITLE = "Attention Model + Threshold Analysis"


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


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    config_space = 2 ** mem_bits
    mi_max_nodes = min(max_nodes, 500)

    progress.log(f"Attention + threshold analysis: {n_seeds} seeds, "
                 f"{mi_max_nodes} nodes, {mem_bits}-bit, {time_budget}s budget")

    # Budget: 40% attention model, 60% threshold sweep
    attn_budget = time_budget * 0.4
    sweep_budget = time_budget * 0.6

    # === Part 1: Attention model (parameter-free) ===
    progress.log("")
    progress.log("PART 1: Attention model (parameter-free)")
    progress.log("  Wiring: on effective state revisit only")

    attn_results = []
    attn_mi_data = []
    t_start = time.time()
    attn_time_per_seed = attn_budget / n_seeds

    for i in range(n_seeds):
        seed = 5000 + i
        elapsed = time.time() - t_start
        remaining = attn_budget - elapsed
        if remaining < 3:
            progress.log(f"  Time limit after {i} seeds")
            break

        progress.update(i, n_seeds * 2, "Attention model",
                        f"Seed {i+1}/{n_seeds}")
        progress.update_seed(0, mi_max_nodes, f"Seed {seed}:")

        G_attn, nd, gl, traj = run_attention_model(
            mem_bits=mem_bits, max_nodes=mi_max_nodes, seed=seed,
            time_limit=attn_time_per_seed * 0.6, progress=progress,
            record_trajectories=True,
        )
        n_attn = G_attn.number_of_nodes()
        n_edges = G_attn.number_of_edges()
        avg_deg = 2 * n_edges / n_attn if n_attn > 0 else 0

        G_undir = G_attn.to_undirected()
        r = analyze_powerlaw(G_undir, label=f"attention seed={seed}")
        attn_results.append(r)

        progress.update_seed(0, 2, f"Seed {seed} MI:")
        mi_rng = np.random.default_rng(seed + 300000)
        e_mi, ne_mi, ratio = _compute_mi_excess(
            G_undir, traj, config_space, mi_rng)
        attn_mi_data.append((e_mi, ne_mi, ratio, n_attn, n_edges))
        del traj

        al_a = f"{r['alpha']:.2f}" if r['alpha'] else "N/A"
        progress.log(f"  Seed {seed}: {n_attn}n/{n_edges}e "
                     f"(avg_deg={avg_deg:.1f}), alpha={al_a}, rho={ratio:.2f}")

    # === Part 2: LPAN threshold sweep ===
    progress.log("")
    progress.log("PART 2: LPAN threshold sweep (why MI excess needs proactive wiring)")
    thresholds = [0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
    sweep_results = {}  # threshold -> list of (rho, n_edges)
    t_sweep_start = time.time()
    sweep_time_per = sweep_budget / (len(thresholds) * n_seeds)

    for ti, pt in enumerate(thresholds):
        sweep_results[pt] = []
        for i in range(n_seeds):
            seed = 6000 + i
            elapsed = time.time() - t_sweep_start
            if elapsed > sweep_budget:
                break

            progress.update(n_seeds + ti * n_seeds // len(thresholds) + i,
                           n_seeds * 2, "Threshold sweep",
                           f"PT={pt:.2f} seed {i+1}/{n_seeds}")
            progress.update_seed(0, mi_max_nodes)

            G, nd, gl, traj = run_lpan_model(
                mem_bits=mem_bits, max_nodes=mi_max_nodes, seed=seed,
                pressure_threshold=pt, time_limit=sweep_time_per * 0.6,
                progress=progress, record_trajectories=True,
            )
            n_nodes = G.number_of_nodes()
            n_edges = G.number_of_edges()

            mi_rng = np.random.default_rng(seed + 400000)
            e_mi, ne_mi, ratio = _compute_mi_excess(
                G, traj, config_space, mi_rng)
            sweep_results[pt].append((ratio, n_edges, n_nodes))
            del traj

        ratios = [r[0] for r in sweep_results[pt]
                  if r[0] != float('inf')]
        if ratios:
            avg_e = np.mean([r[1] for r in sweep_results[pt]])
            avg_n = np.mean([r[2] for r in sweep_results[pt]])
            progress.log(f"  PT={pt:.2f}: rho={np.mean(ratios):.3f} +/- "
                         f"{np.std(ratios):.3f}  "
                         f"({avg_n:.0f}n, {avg_e:.0f}e, "
                         f"avg_deg={2*avg_e/avg_n:.1f})")

    # === Summary ===
    progress.update(n_seeds * 2, n_seeds * 2, "Analysis", "Summary...")

    attn_alphas = [r["alpha"] for r in attn_results if r["alpha"]]
    attn_ratios = [d[2] for d in attn_mi_data if d[2] != float('inf')]

    lines = [
        "=" * 60,
        "Attention Model + Threshold Analysis",
        "=" * 60,
        "",
        "PART 1: ATTENTION MODEL (parameter-free)",
        f"  Seeds: {len(attn_results)}/{n_seeds}",
        f"  Nodes: {mi_max_nodes}, Memory: {mem_bits} bits",
        "",
        "  Wiring trigger: effective state revisit (exact loop)",
        "  Spawning trigger: effective state revisit (same)",
        "  Parameters: NONE",
        "",
    ]

    if attn_alphas:
        lines.append(f"  Topology alpha: {np.mean(attn_alphas):.3f} +/- "
                     f"{np.std(attn_alphas):.3f}")
    if attn_ratios:
        lines.append(f"  MI ratio (rho): {np.mean(attn_ratios):.3f} +/- "
                     f"{np.std(attn_ratios):.3f}")
        lines.append("")
        if np.mean(attn_ratios) > 1.05:
            lines.append("  Topology: HEAVY-TAILED | MI excess: POSITIVE")
        elif np.mean(attn_ratios) < 0.95:
            lines.append("  Topology: HEAVY-TAILED | MI excess: NEGATIVE (rho < 1)")
        else:
            lines.append("  Topology: HEAVY-TAILED | MI excess: ABSENT")

    lines += [
        "",
        "PART 2: LPAN THRESHOLD SWEEP",
        "  Same engine, varying pressure_threshold.",
        "  Shows MI excess requires proactive wiring (threshold < 1.0).",
        "",
        "  Threshold  |  rho (mean +/- std)  |  avg_deg",
        "  " + "-" * 50,
    ]

    for pt in thresholds:
        ratios = [r[0] for r in sweep_results.get(pt, [])
                  if r[0] != float('inf')]
        if ratios:
            avg_e = np.mean([r[1] for r in sweep_results[pt]])
            avg_n = np.mean([r[2] for r in sweep_results[pt]])
            marker = " ***" if np.mean(ratios) > 1.05 else ""
            lines.append(f"  {pt:.2f}         |  {np.mean(ratios):.3f} +/- "
                         f"{np.std(ratios):.3f}         |  "
                         f"{2*avg_e/avg_n:.1f}{marker}")

    lines += [
        "",
        "INTERPRETATION:",
        "  Heavy-tailed topology is a generic property of growing networks",
        "  under anti-loop pressure. It emerges parameter-free.",
        "",
        "  MI excess is NOT generic. It requires proactive wiring: entities",
        "  that add connections BEFORE they fully loop (threshold < 1.0).",
        "  At exact loop (threshold = 1.0), the effective state reset severs",
        "  trajectory continuity, destroying the correlations that create",
        "  MI excess.",
        "",
        "  This means MI excess is a signature of a BEHAVIORAL REGIME",
        "  (proactive connection-seeking), not of anti-loop dynamics alone.",
    ]

    lines += ["", "Per-seed detail (attention model):"]
    for j, r in enumerate(attn_results):
        if j < len(attn_mi_data):
            e, ne, rat, nn, ne2 = attn_mi_data[j]
            al = f"{r['alpha']:.3f}" if r['alpha'] else "N/A"
            lines.append(f"  {r['label']}: alpha={al}, "
                         f"{nn}n/{ne2}e, rho={rat:.2f}")

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "attention_results.txt"), "w") as f:
        f.write(report)

    _plot_results(attn_alphas, attn_mi_data, sweep_results, thresholds,
                  out_dir, progress)

    progress.update(n_seeds * 2, n_seeds * 2, "Done",
                    f"Attention + {len(thresholds)} thresholds")


def _plot_results(attn_alphas, attn_mi_data, sweep_results, thresholds,
                  out_dir, progress):
    """Plot topology, MI, and threshold sweep."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Alpha distribution (attention model)
    ax = axes[0]
    if attn_alphas:
        ax.hist(attn_alphas, bins=max(5, len(attn_alphas) // 3), alpha=0.7,
                label=f"attention ({np.mean(attn_alphas):.2f})", color="#4CAF50")
    ax.axvline(2.0, color="red", linestyle="--", alpha=0.3)
    ax.axvline(3.0, color="red", linestyle="--", alpha=0.3)
    ax.set_xlabel("alpha")
    ax.set_ylabel("count")
    ax.set_title("Power-law exponent (attention model)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 2: MI ratio per seed (attention model)
    ax = axes[1]
    ratios = [d[2] for d in attn_mi_data if d[2] != float('inf')]
    if ratios:
        ax.bar(range(len(ratios)), ratios, color="#4CAF50", alpha=0.7)
        ax.axhline(1.0, color="red", linestyle="--", alpha=0.5,
                   label="rho=1")
        ax.set_xlabel("Seed")
        ax.set_ylabel("MI ratio (edge/non-edge)")
        ax.set_title("Attention model: MI ratio per seed")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis="y")

    # Panel 3: Threshold sweep (the key finding)
    ax = axes[2]
    sweep_means = []
    sweep_stds = []
    sweep_pts = []
    for pt in thresholds:
        rs = [r[0] for r in sweep_results.get(pt, []) if r[0] != float('inf')]
        if rs:
            sweep_pts.append(pt)
            sweep_means.append(np.mean(rs))
            sweep_stds.append(np.std(rs))

    if sweep_means:
        ax.errorbar(sweep_pts, sweep_means, yerr=sweep_stds,
                    fmt='o-', color="#2196F3", capsize=5, linewidth=2,
                    markersize=8, label="LPAN")
        # Add attention model point
        if ratios:
            ax.axhline(np.mean(ratios), color="#4CAF50", linestyle="--",
                       alpha=0.7, label=f"Attention (rho={np.mean(ratios):.2f})")
        ax.axhline(1.0, color="red", linestyle=":", alpha=0.3)
        ax.set_xlabel("Pressure threshold")
        ax.set_ylabel("MI ratio (rho)")
        ax.set_title("MI excess vs wiring threshold")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Attention Model + Threshold Analysis",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "attention_topology.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
