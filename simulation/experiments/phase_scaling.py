"""O5c: Phase 2 width scaling — does the transition sharpen or widen with memory?"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import run_spawn_model
from simulation.experiments.phase_boundary import compute_depths, analyze_phases

TITLE = "O5c Phase 2 Scaling"


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    # Test across a range of mem_bits values
    mem_bits_list = [4, 5, 6, 7, 8, 9, 10]
    total_runs = len(mem_bits_list) * n_seeds
    time_per_run = time_budget / total_runs

    progress.log(f"O5c Phase 2 Scaling: {n_seeds} seeds x {len(mem_bits_list)} mem_bits, "
                 f"{time_budget}s budget ({time_per_run:.1f}s/run)")

    # Calibrate at the largest mem_bits (slowest)
    progress.update(0, total_runs, "Calibrating",
                    f"Probing at {mem_bits_list[-1]}-bit...")
    t0 = time.time()
    G_probe, _, _ = run_spawn_model(
        mem_bits=mem_bits_list[-1], max_nodes=max_nodes,
        seed=9999, time_limit=5.0,
    )
    t_probe = max(time.time() - t0, 0.1)
    nps = G_probe.number_of_nodes() / t_probe

    if t_probe < time_per_run * 0.3:
        target = time_per_run * 0.4
        calibrated = int(nps * target)
        max_nodes = max(max_nodes, min(calibrated, max_nodes * 50))
        progress.log(f"  Calibration: {G_probe.number_of_nodes()} nodes in {t_probe:.1f}s "
                     f"({nps:.0f} nodes/s)")
        progress.log(f"  Auto-scaling: -> {max_nodes} nodes")
    else:
        progress.log(f"  Calibration: keeping {max_nodes} nodes")

    all_data = {}  # mem_bits -> list of result dicts
    t_start = time.time()
    run_idx = 0

    for mb in mem_bits_list:
        all_data[mb] = []
        for i in range(n_seeds):
            seed = 4000 + i
            elapsed = time.time() - t_start
            remaining = time_budget - elapsed
            if remaining < 3:
                progress.log(f"  Time limit reached at {mb}-bit seed {i}")
                break

            run_limit = remaining / max(total_runs - run_idx, 1)
            progress.update(run_idx, total_runs, "Running",
                            f"{mb}-bit seed {i+1}/{n_seeds} ({run_limit:.0f}s)")
            progress.update_seed(0, max_nodes, f"{mb}-bit seed {seed}:")

            G, nd, gl = run_spawn_model(
                mem_bits=mb, max_nodes=max_nodes, seed=seed,
                time_limit=run_limit * 0.9,
                stop_at_max=False, progress=progress,
            )
            n_final = G.number_of_nodes()
            progress.update_seed(n_final, max_nodes)

            depths = compute_depths(nd["parent"], n_final)
            result = analyze_phases(gl, nd["birth_steps"], depths, n_final)
            result["seed"] = seed
            result["n_final"] = n_final
            result["mem_bits"] = mb
            all_data[mb].append(result)

            run_idx += 1

    progress.update(run_idx, total_runs, "Analysis", "Computing summary...")

    # Extract Phase 2 widths
    lines = [
        "=" * 60,
        "O5c: Phase 2 Width Scaling with Memory",
        "=" * 60,
        f"Nodes per graph: {max_nodes}",
        f"Seeds per mem_bits: {n_seeds}",
        "",
        f"{'mem_bits':>8} {'C':>6} {'P2 width':>10} {'P12 step':>10} "
        f"{'P23 step':>10} {'max_depth':>10} {'n_seeds':>8}",
        "-" * 70,
    ]

    scaling_mb = []
    scaling_width = []
    scaling_width_std = []
    scaling_p12 = []
    scaling_depth = []

    for mb in mem_bits_list:
        results = all_data.get(mb, [])
        if not results:
            continue

        widths = [r["p23_step"] - r["p12_step"]
                  for r in results if r["p23_step"] is not None]
        p12s = [r["p12_step"] for r in results]
        p23s = [r["p23_step"] for r in results if r["p23_step"] is not None]
        max_depths = [r["max_depth"] for r in results]

        C = 2 ** mb
        n_done = len(results)

        if widths:
            w_mean = np.mean(widths)
            w_std = np.std(widths)
            scaling_mb.append(mb)
            scaling_width.append(w_mean)
            scaling_width_std.append(w_std)
            scaling_p12.append(np.mean(p12s))
            scaling_depth.append(np.mean(max_depths))

            lines.append(
                f"{mb:>8} {C:>6} {w_mean:>8.1f}+-{w_std:<4.1f} "
                f"{np.mean(p12s):>10.0f} {np.mean(p23s):>10.0f} "
                f"{np.mean(max_depths):>10.1f} {n_done:>8}"
            )
        else:
            lines.append(f"{mb:>8} {C:>6}   {'P3 N/A':>10} "
                         f"{np.mean(p12s):>10.0f} {'N/A':>10} "
                         f"{np.mean(max_depths):>10.1f} {n_done:>8}")

    lines += [""]

    # Trend analysis
    if len(scaling_mb) >= 3:
        # Fit log-log: width ~ C^beta
        log_C = np.log2([2**m for m in scaling_mb])
        log_w = np.log2(scaling_width)
        coeffs = np.polyfit(log_C, log_w, 1)
        beta = coeffs[0]

        lines.append("SCALING ANALYSIS:")
        lines.append(f"  Phase 2 width ~ C^beta, beta = {beta:.3f}")
        if beta > 0.1:
            lines.append(f"  WIDENS with memory (beta > 0): "
                         f"Phase 2 becomes an era at large C")
        elif beta < -0.1:
            lines.append(f"  SHARPENS with memory (beta < 0): "
                         f"true discontinuous transition in the limit")
        else:
            lines.append(f"  CONSTANT width (beta ~ 0): "
                         f"Phase 2 width independent of memory size")

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "phase_scaling_results.txt"), "w") as f:
        f.write(report)

    if scaling_mb:
        _plot_scaling(all_data, mem_bits_list, scaling_mb, scaling_width,
                      scaling_width_std, scaling_p12, scaling_depth,
                      out_dir, progress)

    progress.update(total_runs, total_runs, "Done", "Complete")


def _plot_scaling(all_data, mem_bits_list, scaling_mb, scaling_width,
                  scaling_width_std, scaling_p12, scaling_depth,
                  out_dir, progress):
    """Plot Phase 2 width scaling."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    C_vals = [2**m for m in scaling_mb]

    # Panel 1: Phase 2 width vs config space (log-log)
    ax = axes[0, 0]
    ax.errorbar(C_vals, scaling_width, yerr=scaling_width_std,
                fmt="o-", color="#2196F3", capsize=4, markersize=6)
    ax.set_xscale("log", base=2)
    if min(scaling_width) > 0:
        ax.set_yscale("log", base=2)
    ax.set_xlabel("Config space C = 2^mem_bits")
    ax.set_ylabel("Phase 2 width (steps)")
    ax.set_title("Phase 2 width scaling")
    ax.grid(True, alpha=0.3)
    # Fit line
    if len(scaling_mb) >= 3:
        log_C = np.log2(C_vals)
        log_w = np.log2(scaling_width)
        coeffs = np.polyfit(log_C, log_w, 1)
        fit_C = np.array([min(C_vals), max(C_vals)])
        fit_w = 2 ** np.polyval(coeffs, np.log2(fit_C))
        ax.plot(fit_C, fit_w, "--", color="red", alpha=0.6,
                label=f"slope = {coeffs[0]:.2f}")
        ax.legend()

    # Panel 2: Growth curves for each mem_bits (one seed each)
    ax = axes[0, 1]
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(mem_bits_list)))
    for mb, color in zip(mem_bits_list, colors):
        results = all_data.get(mb, [])
        if results:
            r = results[0]
            total = len(r["steps"])
            frac = np.linspace(0, 1, total)
            ax.plot(frac, r["nodes"], color=color, alpha=0.8,
                    label=f"{mb}-bit", linewidth=1.2)
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Node count")
    ax.set_title("Growth curves by memory size")
    ax.legend(fontsize=7, ncol=2)

    # Panel 3: Spawn rate for each mem_bits (one seed)
    ax = axes[1, 0]
    for mb, color in zip(mem_bits_list, colors):
        results = all_data.get(mb, [])
        if results:
            r = results[0]
            total = len(r["spawn_steps"])
            frac = np.linspace(0, 1, total)
            ax.plot(frac, r["smoothed_spawns"], color=color, alpha=0.8,
                    label=f"{mb}-bit", linewidth=1.2)
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Spawns/step (smoothed)")
    ax.set_title("Spawn rate by memory size")
    ax.legend(fontsize=7, ncol=2)

    # Panel 4: Max depth and P12 step vs mem_bits
    ax = axes[1, 1]
    ax2 = ax.twinx()
    ax.bar([m - 0.15 for m in scaling_mb], scaling_depth, width=0.3,
           color="#4CAF50", alpha=0.7, label="max depth")
    ax2.bar([m + 0.15 for m in scaling_mb], scaling_p12, width=0.3,
            color="#FF9800", alpha=0.7, label="P12 step")
    ax.set_xlabel("mem_bits")
    ax.set_ylabel("Max tree depth", color="#4CAF50")
    ax2.set_ylabel("P1->P2 step", color="#FF9800")
    ax.set_title("Depth and transition timing")
    ax.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)

    plt.suptitle("O5c: Phase 2 Width Scaling with Memory",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "phase_scaling.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
