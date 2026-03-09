"""O5b: Phase boundaries with variable memory — does variation produce gradual Phase 2?"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import run_spawn_model
from simulation.experiments.phase_boundary import compute_depths, analyze_phases

TITLE = "O5b Variable Memory Phases"


def _calibrate(mem_bits, max_nodes):
    """Measure throughput for auto-scaling."""
    t0 = time.time()
    G, _, _ = run_spawn_model(mem_bits=mem_bits, max_nodes=max_nodes,
                              seed=9999, time_limit=5.0)
    elapsed = max(time.time() - t0, 0.1)
    return G.number_of_nodes(), elapsed, G.number_of_nodes() / elapsed


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    time_per_seed = time_budget / n_seeds
    # Each seed runs two models (uniform + variable), so halve the budget
    time_per_run = time_per_seed / 2

    # Calibration
    progress.update(0, n_seeds, "Calibrating", "Measuring throughput...")
    n_probe, t_probe, nps = _calibrate(mem_bits, max_nodes)

    if t_probe < time_per_run * 0.3:
        target_time = time_per_run * 0.4
        calibrated = int(nps * target_time)
        max_nodes = max(max_nodes, min(calibrated, max_nodes * 50))
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s "
                     f"({nps:.0f} nodes/s)")
        progress.log(f"  Auto-scaling: -> {max_nodes} nodes "
                     f"(target {target_time:.0f}s growth)")
    else:
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s")

    # Variable memory range: vary below mem_bits (some entities smaller)
    # Allocation stays at 2^mem_bits — no memory explosion
    lo = max(4, mem_bits - 4)
    hi = mem_bits
    progress.log(f"O5b: {n_seeds} seeds, {max_nodes} nodes, "
                 f"uniform={mem_bits}-bit vs variable={lo}-{hi}-bit")

    uniform_results = []
    variable_results = []
    t_start = time.time()

    for i in range(n_seeds):
        seed = 3000 + i
        elapsed = time.time() - t_start
        remaining = time_budget - elapsed
        seeds_left = n_seeds - i
        if remaining < 5:
            progress.log(f"  Time limit reached after {i} seeds")
            break

        seed_limit = remaining / seeds_left

        # Overall tracks 2 runs per seed (uniform + variable)
        run_idx = i * 2
        total_runs = n_seeds * 2

        # Uniform memory
        progress.update(run_idx, total_runs, "Running seeds",
                        f"Seed {i+1}/{n_seeds} uniform ({mem_bits}-bit)")
        progress.update_seed(0, max_nodes, f"Seed {seed} uniform:")
        G_u, nd_u, gl_u = run_spawn_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            time_limit=seed_limit * 0.45, stop_at_max=False, progress=progress,
        )
        n_u = G_u.number_of_nodes()
        progress.update_seed(n_u, max_nodes)
        depths_u = compute_depths(nd_u["parent"], n_u)
        r_u = analyze_phases(gl_u, nd_u["birth_steps"], depths_u, n_u)
        r_u["seed"] = seed
        r_u["n_final"] = n_u
        uniform_results.append(r_u)

        # Variable memory
        progress.update(run_idx + 1, total_runs, "Running seeds",
                        f"Seed {i+1}/{n_seeds} variable ({lo}-{hi}-bit)")
        progress.update_seed(0, max_nodes, f"Seed {seed} variable:")
        G_v, nd_v, gl_v = run_spawn_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            mem_bits_range=(lo, hi),
            time_limit=seed_limit * 0.45, stop_at_max=False, progress=progress,
        )
        n_v = G_v.number_of_nodes()
        progress.update_seed(n_v, max_nodes)
        depths_v = compute_depths(nd_v["parent"], n_v)
        r_v = analyze_phases(gl_v, nd_v["birth_steps"], depths_v, n_v)
        r_v["seed"] = seed
        r_v["n_final"] = n_v
        r_v["mem_distribution"] = nd_v["node_mem_bits"]
        variable_results.append(r_v)

        p2_u = r_u["p23_step"] or "N/A"
        p2_v = r_v["p23_step"] or "N/A"
        progress.log(f"  Seed {seed}: uniform P12={r_u['p12_step']} P23={p2_u}, "
                     f"variable P12={r_v['p12_step']} P23={p2_v}")

    n_completed = len(uniform_results)
    progress.update(n_completed, n_seeds, "Analysis", "Generating report...")

    # Compute Phase 2 duration (P23 - P12)
    u_p2_durations = [r["p23_step"] - r["p12_step"]
                      for r in uniform_results if r["p23_step"] is not None]
    v_p2_durations = [r["p23_step"] - r["p12_step"]
                      for r in variable_results if r["p23_step"] is not None]

    lines = [
        "=" * 60,
        "O5b: Variable Memory — Phase 2 Graduality Test",
        "=" * 60,
        f"Seeds completed: {n_completed}/{n_seeds}",
        f"Nodes per graph: {max_nodes}",
        f"Uniform: {mem_bits}-bit ({2**mem_bits} states)",
        f"Variable: {lo}-{hi}-bit ({2**lo}-{2**hi} states)",
        "",
        "PHASE 2 DURATION (steps between P1->P2 and P2->P3):",
        f"  Uniform:  {np.mean(u_p2_durations):.1f} +/- {np.std(u_p2_durations):.1f}"
        if u_p2_durations else "  Uniform:  P3 not reached",
        f"  Variable: {np.mean(v_p2_durations):.1f} +/- {np.std(v_p2_durations):.1f}"
        if v_p2_durations else "  Variable: P3 not reached",
        "",
    ]

    if u_p2_durations and v_p2_durations:
        ratio = np.mean(v_p2_durations) / max(np.mean(u_p2_durations), 1)
        lines.append(f"  Ratio (variable/uniform): {ratio:.2f}x")
        if ratio > 2:
            lines.append("  RESULT: Variable memory DOES produce more gradual Phase 2")
        elif ratio > 1.2:
            lines.append("  RESULT: Modest effect — variable memory slightly extends Phase 2")
        else:
            lines.append("  RESULT: No significant effect — Phase 2 remains sharp")

    lines += ["", "DEPTH STATISTICS:"]
    u_depths = [r["max_depth"] for r in uniform_results]
    v_depths = [r["max_depth"] for r in variable_results]
    lines.append(f"  Uniform  max depth: {np.mean(u_depths):.1f} +/- {np.std(u_depths):.1f}")
    lines.append(f"  Variable max depth: {np.mean(v_depths):.1f} +/- {np.std(v_depths):.1f}")

    lines += ["", "Per-seed detail:"]
    for r_u, r_v in zip(uniform_results, variable_results):
        p23_u = r_u["p23_step"] or "N/A"
        p23_v = r_v["p23_step"] or "N/A"
        lines.append(f"  seed={r_u['seed']}: "
                     f"uniform({r_u['n_final']}n P12={r_u['p12_step']} P23={p23_u}) "
                     f"variable({r_v['n_final']}n P12={r_v['p12_step']} P23={p23_v})")

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "phase_variable_mem_results.txt"), "w") as f:
        f.write(report)

    if uniform_results and variable_results:
        _plot_comparison(uniform_results, variable_results, mem_bits, lo, hi,
                         out_dir, progress)

    progress.update(n_completed * 2, n_seeds * 2, "Done",
                    f"{n_completed} seeds completed")


def _plot_comparison(u_results, v_results, mem_bits, lo, hi, out_dir, progress):
    """Plot uniform vs variable memory phase comparison."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Growth curves — uniform vs variable overlaid
    ax = axes[0, 0]
    for r in u_results:
        total = len(r["steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["nodes"], alpha=0.4, color="#2196F3", linewidth=0.8)
    for r in v_results:
        total = len(r["steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["nodes"], alpha=0.4, color="#FF5722", linewidth=0.8)
    # Dummy lines for legend
    ax.plot([], [], color="#2196F3", label=f"uniform ({mem_bits}-bit)")
    ax.plot([], [], color="#FF5722", label=f"variable ({lo}-{hi}-bit)")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Node count")
    ax.set_title("Growth curves")
    ax.legend(fontsize=9)

    # Panel 2: Spawn rate comparison
    ax = axes[0, 1]
    for r in u_results:
        total = len(r["spawn_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["smoothed_spawns"], alpha=0.4, color="#2196F3", linewidth=0.8)
    for r in v_results:
        total = len(r["spawn_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["smoothed_spawns"], alpha=0.4, color="#FF5722", linewidth=0.8)
    ax.plot([], [], color="#2196F3", label="uniform")
    ax.plot([], [], color="#FF5722", label="variable")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Spawns/step (smoothed)")
    ax.set_title("Spawn rate")
    ax.legend(fontsize=9)

    # Panel 3: Median depth comparison
    ax = axes[1, 0]
    for r in u_results:
        total = len(r["sample_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["median_depths"], alpha=0.4, color="#2196F3", linewidth=0.8)
    for r in v_results:
        total = len(r["sample_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["median_depths"], alpha=0.4, color="#FF5722", linewidth=0.8)
    ax.plot([], [], color="#2196F3", label="uniform")
    ax.plot([], [], color="#FF5722", label="variable")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Median tree depth")
    ax.set_title("Median depth evolution")
    ax.legend(fontsize=9)

    # Panel 4: Phase 2 duration comparison (bar chart)
    ax = axes[1, 1]
    u_dur = [r["p23_step"] - r["p12_step"]
             for r in u_results if r["p23_step"] is not None]
    v_dur = [r["p23_step"] - r["p12_step"]
             for r in v_results if r["p23_step"] is not None]
    x = [0, 1]
    heights = [np.mean(u_dur) if u_dur else 0, np.mean(v_dur) if v_dur else 0]
    errs = [np.std(u_dur) if u_dur else 0, np.std(v_dur) if v_dur else 0]
    bars = ax.bar(x, heights, yerr=errs, color=["#2196F3", "#FF5722"],
                  capsize=5, width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"uniform\n({mem_bits}-bit)", f"variable\n({lo}-{hi}-bit)"])
    ax.set_ylabel("Phase 2 duration (steps)")
    ax.set_title("Phase 2 graduality")
    for bar, h in zip(bars, heights):
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + max(errs) * 0.1,
                    f"{h:.0f}", ha="center", va="bottom", fontsize=10)

    plt.suptitle("O5b: Uniform vs Variable Memory", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "phase_variable_mem.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
