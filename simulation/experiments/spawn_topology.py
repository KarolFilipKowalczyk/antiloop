"""O4: Scale-free topology test for v4 spawn model (CSN + Broido-Clauset)."""

import os
import time

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe from threads
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import run_spawn_model, build_random_tree_control
from simulation.shared.analysis import (
    analyze_powerlaw, get_ccdf, format_powerlaw_result,
)

TITLE = "O4 Spawn Topology"


def _calibrate(mem_bits, max_nodes, progress):
    """Run a quick probe to measure throughput and auto-scale max_nodes.

    Runs a short simulation (max 5s or max_nodes, whichever comes first),
    measures nodes/second, and returns the calibrated max_nodes that would
    fill the target time per seed.
    """
    probe_limit = 5.0  # seconds
    t0 = time.time()
    G, nodes, growth_log = run_spawn_model(
        mem_bits=mem_bits, max_nodes=max_nodes, seed=9999,
        time_limit=probe_limit,
    )
    elapsed = time.time() - t0
    n_reached = G.number_of_nodes()

    if elapsed < 0.1:
        # Too fast to measure — extrapolate conservatively
        nodes_per_sec = n_reached / 0.1
    else:
        nodes_per_sec = n_reached / elapsed

    return n_reached, elapsed, nodes_per_sec


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    time_per_seed = time_budget / n_seeds

    # Calibration: if default max_nodes finishes too fast, scale up
    progress.update(0, n_seeds, "Calibrating", "Measuring throughput...")
    n_probe, t_probe, nps = _calibrate(mem_bits, max_nodes, progress)

    if t_probe < time_per_seed * 0.5:
        # Simulation finishes in less than half the budget — scale up
        # Target: fill 80% of per-seed budget (leave margin for analysis)
        target_time = time_per_seed * 0.8
        calibrated_nodes = int(nps * target_time)
        # At least the requested max_nodes, at most 100x
        calibrated_nodes = max(max_nodes, min(calibrated_nodes, max_nodes * 100))
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s "
                     f"({nps:.0f} nodes/s)")
        progress.log(f"  Auto-scaling: {max_nodes} -> {calibrated_nodes} nodes "
                     f"(target {target_time:.0f}s/seed)")
        max_nodes = calibrated_nodes
    else:
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s — "
                     f"keeping {max_nodes} nodes")

    progress.log(f"O4 Spawn Topology: {n_seeds} seeds, {max_nodes} nodes, "
                 f"{mem_bits}-bit FSM, {time_budget}s budget ({time_per_seed:.0f}s/seed)")

    all_antiloop = []
    all_control = []
    t_start = time.time()

    for i in range(n_seeds):
        seed = 1000 + i
        elapsed = time.time() - t_start
        remaining = time_budget - elapsed
        seeds_left = n_seeds - i
        if remaining < 5:
            progress.log(f"  Time limit reached after {i} seeds")
            break

        # Distribute remaining time evenly across remaining seeds
        seed_limit = remaining / seeds_left
        progress.update(i, n_seeds, "Running seeds",
                        f"Seed {i+1}/{n_seeds} ({max_nodes} nodes, {seed_limit:.0f}s budget)")

        # Antiloop spawn model
        G, nodes, growth_log = run_spawn_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            time_limit=seed_limit * 0.9,  # leave 10% for analysis
        )
        n_final = G.number_of_nodes()

        # Random tree control (same size)
        G_ctrl = build_random_tree_control(n_final, seed=seed + 500000)

        # CSN analysis
        r_al = analyze_powerlaw(G, label=f"antiloop seed={seed}")
        r_ctrl = analyze_powerlaw(G_ctrl, label=f"control seed={seed}")

        all_antiloop.append(r_al)
        all_control.append(r_ctrl)

        progress.log(f"  Seed {seed}: {n_final} nodes, "
                     f"alpha={r_al['alpha']:.3f}" if r_al['alpha'] else
                     f"  Seed {seed}: {n_final} nodes, alpha=N/A")

    n_completed = len(all_antiloop)
    progress.update(n_completed, n_seeds, "Analysis", "Computing summary...")

    # Summary statistics
    al_alphas = [r["alpha"] for r in all_antiloop if r["alpha"] is not None]
    ctrl_alphas = [r["alpha"] for r in all_control if r["alpha"] is not None]

    al_vs_exp = sum(1 for r in all_antiloop
                    if r.get("vs_exp") and r["vs_exp"]["R"] > 0)
    al_vs_ln = sum(1 for r in all_antiloop
                   if r.get("vs_lognormal") and r["vs_lognormal"]["R"] > 0)
    al_vs_se = sum(1 for r in all_antiloop
                   if r.get("vs_stretched_exp") and r["vs_stretched_exp"]["R"] > 0)

    lines = [
        "=" * 60,
        "O4: Spawn Model Topology — Scale-Free Test",
        "=" * 60,
        f"Seeds completed: {n_completed}/{n_seeds}",
        f"Nodes per graph: {max_nodes}",
        f"Memory: {mem_bits} bits ({2**mem_bits} states)",
        "",
        "ANTILOOP SPAWN MODEL:",
        f"  alpha = {np.mean(al_alphas):.3f} +/- {np.std(al_alphas):.3f}"
        if al_alphas else "  alpha = N/A",
        f"  range: [{min(al_alphas):.3f}, {max(al_alphas):.3f}]"
        if al_alphas else "",
        f"  power_law > exponential:          {al_vs_exp}/{n_completed}",
        f"  power_law > lognormal:            {al_vs_ln}/{n_completed}",
        f"  power_law > stretched_exponential: {al_vs_se}/{n_completed}",
        "",
        "RANDOM TREE CONTROL:",
        f"  alpha = {np.mean(ctrl_alphas):.3f} +/- {np.std(ctrl_alphas):.3f}"
        if ctrl_alphas else "  alpha = N/A",
        "",
        "Per-seed detail:",
    ]

    for r in all_antiloop:
        lines.append(format_powerlaw_result(r))
    lines.append("")
    for r in all_control:
        lines.append(format_powerlaw_result(r))

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    # Save report
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "spawn_topology_results.txt"), "w") as f:
        f.write(report)

    # Plot degree distributions (last seed)
    if all_antiloop:
        _plot_ccdf(all_antiloop, all_control, out_dir, progress)

    progress.update(n_seeds, n_seeds, "Done",
                    f"{n_completed} seeds completed")


def _plot_ccdf(all_antiloop, all_control, out_dir, progress):
    """Plot CCDF comparison between antiloop and control."""
    # Re-run last seed to get graphs for plotting
    # (we don't store graphs to save memory at scale)
    last_al = all_antiloop[-1]
    last_ctrl = all_control[-1]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot alpha distribution across seeds
    ax = axes[0]
    al_alphas = [r["alpha"] for r in all_antiloop if r["alpha"]]
    ctrl_alphas = [r["alpha"] for r in all_control if r["alpha"]]
    if al_alphas:
        ax.hist(al_alphas, bins=max(5, len(al_alphas) // 3), alpha=0.7,
                label=f"antiloop (mean={np.mean(al_alphas):.2f})", color="#2196F3")
    if ctrl_alphas:
        ax.hist(ctrl_alphas, bins=max(5, len(ctrl_alphas) // 3), alpha=0.7,
                label=f"control (mean={np.mean(ctrl_alphas):.2f})", color="#999")
    ax.set_xlabel("alpha")
    ax.set_ylabel("count")
    ax.set_title("Power-law exponent distribution")
    ax.legend()
    ax.axvline(2.0, color="red", linestyle="--", alpha=0.5, label="alpha=2")
    ax.axvline(3.0, color="red", linestyle="--", alpha=0.5)

    # Summary text
    ax = axes[1]
    ax.axis("off")
    n = len(all_antiloop)
    al_vs_exp = sum(1 for r in all_antiloop
                    if r.get("vs_exp") and r["vs_exp"]["R"] > 0)
    al_vs_ln = sum(1 for r in all_antiloop
                   if r.get("vs_lognormal") and r["vs_lognormal"]["R"] > 0)
    al_vs_se = sum(1 for r in all_antiloop
                   if r.get("vs_stretched_exp") and r["vs_stretched_exp"]["R"] > 0)
    summary = (
        f"Spawn Model Topology (O4)\n"
        f"{'─' * 35}\n"
        f"Seeds: {n}\n"
        f"\n"
        f"Antiloop alpha: {np.mean(al_alphas):.3f} ± {np.std(al_alphas):.3f}\n"
        f"Control alpha:  {np.mean(ctrl_alphas):.3f} ± {np.std(ctrl_alphas):.3f}\n"
        f"\n"
        f"PL > exponential:   {al_vs_exp}/{n}\n"
        f"PL > lognormal:     {al_vs_ln}/{n}\n"
        f"PL > stretched exp: {al_vs_se}/{n}\n"
    ) if al_alphas else "No valid results"
    ax.text(0.1, 0.5, summary, transform=ax.transAxes, fontsize=11,
            verticalalignment="center", fontfamily="monospace")

    plt.tight_layout()
    path = os.path.join(out_dir, "spawn_topology.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
