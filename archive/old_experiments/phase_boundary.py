"""O5: Phase boundary validation — three growth phases from anti-loop dynamics."""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import run_spawn_model

TITLE = "O5 Phase Boundaries"


def _calibrate(mem_bits, max_nodes, progress):
    """Measure throughput and auto-scale max_nodes to fill time budget."""
    probe_limit = 5.0
    t0 = time.time()
    G, nodes, growth_log = run_spawn_model(
        mem_bits=mem_bits, max_nodes=max_nodes, seed=9999,
        time_limit=probe_limit,
    )
    elapsed = time.time() - t0
    n_reached = G.number_of_nodes()
    nodes_per_sec = n_reached / max(elapsed, 0.1)
    return n_reached, elapsed, nodes_per_sec


def compute_depths(parent, n_nodes):
    """Compute tree depth for each node from the parent array."""
    depths = np.zeros(n_nodes, dtype=np.int32)
    for nid in range(1, n_nodes):
        chain = []
        p = nid
        while p > 0 and depths[p] == 0:
            chain.append(p)
            p = parent[p]
        d = depths[p] + 1
        for node in reversed(chain):
            depths[node] = d
            d += 1
    return depths


def analyze_phases(growth_log, birth_steps, depths, n_nodes):
    """Analyze growth curve, spawn rate, and depth evolution."""
    steps = np.array([s for s, _ in growth_log])
    nodes = np.array([n for _, n in growth_log])
    total_steps = len(steps)

    # Spawn rate per step
    spawns = np.diff(nodes)
    spawn_steps = steps[1:]

    # Smoothing window: adaptive, 2% of total steps, min 10
    window = max(10, total_steps // 50)
    kernel = np.ones(window) / window
    smoothed_spawns = np.convolve(spawns, kernel, mode="same")

    # Per-capita spawn rate
    nodes_at_spawn = nodes[1:].astype(float)
    nodes_at_spawn = np.maximum(nodes_at_spawn, 1)
    per_capita = smoothed_spawns / nodes_at_spawn

    # Phase 1->2 boundary: peak spawn rate
    p12_idx = np.argmax(smoothed_spawns)
    p12_step = int(spawn_steps[p12_idx])

    # Phase 2->3 boundary: per-capita rate drops below 1/N
    # i.e., less than 1 spawn per step on average
    threshold = 1.0 / nodes_at_spawn
    p23_idx = None
    for i in range(p12_idx + 1, len(per_capita)):
        if per_capita[i] < threshold[i]:
            p23_idx = i
            break
    p23_step = int(spawn_steps[p23_idx]) if p23_idx is not None else None

    # Median depth over time (sampled at 200 points)
    n_samples = min(200, total_steps)
    sample_indices = np.linspace(0, total_steps - 1, n_samples, dtype=int)
    sample_steps = steps[sample_indices]
    median_depths = np.zeros(n_samples)
    for i, t in enumerate(sample_steps):
        mask = birth_steps <= t
        if mask.any():
            median_depths[i] = np.median(depths[mask])

    # Depth distribution snapshots at 5 time points
    snapshot_fracs = [0.1, 0.3, 0.5, 0.7, 0.9]
    snapshots = []
    for frac in snapshot_fracs:
        t = steps[int(frac * (total_steps - 1))]
        mask = birth_steps <= t
        if mask.any():
            snapshots.append((frac, t, depths[mask].copy()))
        else:
            snapshots.append((frac, t, np.array([0])))

    return {
        "steps": steps,
        "nodes": nodes,
        "spawn_steps": spawn_steps,
        "spawns": spawns,
        "smoothed_spawns": smoothed_spawns,
        "per_capita": per_capita,
        "p12_step": p12_step,
        "p12_idx": p12_idx,
        "p23_step": p23_step,
        "p23_idx": p23_idx,
        "sample_steps": sample_steps,
        "median_depths": median_depths,
        "snapshots": snapshots,
        "max_depth": int(depths.max()) if len(depths) > 0 else 0,
        "final_median_depth": float(np.median(depths)),
        "window": window,
    }


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    time_per_seed = time_budget / n_seeds

    # Calibration
    progress.update(0, n_seeds, "Calibrating", "Measuring throughput...")
    n_probe, t_probe, nps = _calibrate(mem_bits, max_nodes, progress)

    # For phase boundary detection, we need growth + plateau.
    # Target: fill ~40% of seed budget with growth, leave ~60% for plateau/Phase 3.
    if t_probe < time_per_seed * 0.3:
        target_time = time_per_seed * 0.4
        calibrated_nodes = int(nps * target_time)
        calibrated_nodes = max(max_nodes, min(calibrated_nodes, max_nodes * 50))
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s "
                     f"({nps:.0f} nodes/s)")
        progress.log(f"  Auto-scaling: {max_nodes} -> {calibrated_nodes} nodes "
                     f"(target {target_time:.0f}s growth + {time_per_seed - target_time:.0f}s plateau)")
        max_nodes = calibrated_nodes
    else:
        progress.log(f"  Calibration: {n_probe} nodes in {t_probe:.1f}s -- "
                     f"keeping {max_nodes} nodes")

    progress.log(f"O5 Phase Boundaries: {n_seeds} seeds, {max_nodes} nodes, "
                 f"{mem_bits}-bit FSM, {time_budget}s budget ({time_per_seed:.0f}s/seed)")

    all_results = []
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
        progress.update(i, n_seeds, "Running seeds",
                        f"Seed {i+1}/{n_seeds} ({max_nodes} nodes, {seed_limit:.0f}s budget)")
        progress.update_seed(0, max_nodes, f"Seed {seed}:")

        G, nodes_data, growth_log = run_spawn_model(
            mem_bits=mem_bits, max_nodes=max_nodes, seed=seed,
            time_limit=seed_limit * 0.9,
            max_steps=500000,
            stop_at_max=False,
            progress=progress,
        )
        n_final = G.number_of_nodes()
        progress.update_seed(n_final, max_nodes)

        # Compute depths and analyze phases
        depths = compute_depths(nodes_data["parent"], n_final)
        result = analyze_phases(
            growth_log, nodes_data["birth_steps"], depths, n_final,
        )
        result["seed"] = seed
        result["n_final"] = n_final
        all_results.append(result)

        p23_str = str(result["p23_step"]) if result["p23_step"] else "not reached"
        progress.log(f"  Seed {seed}: {n_final} nodes, "
                     f"P1->P2 @ step {result['p12_step']}, "
                     f"P2->P3 @ step {p23_str}, "
                     f"max depth {result['max_depth']}")

    n_completed = len(all_results)
    progress.update(n_completed, n_seeds, "Analysis", "Generating report...")

    # Summary
    p12_steps = [r["p12_step"] for r in all_results]
    p23_steps = [r["p23_step"] for r in all_results if r["p23_step"] is not None]
    max_depths = [r["max_depth"] for r in all_results]
    final_medians = [r["final_median_depth"] for r in all_results]
    total_steps_list = [len(r["steps"]) for r in all_results]

    # Normalize boundaries to fraction of total steps
    p12_fracs = [r["p12_step"] / max(len(r["steps"]), 1) for r in all_results]
    p23_fracs = [r["p23_step"] / max(len(r["steps"]), 1)
                 for r in all_results if r["p23_step"] is not None]

    lines = [
        "=" * 60,
        "O5: Phase Boundary Validation",
        "=" * 60,
        f"Seeds completed: {n_completed}/{n_seeds}",
        f"Nodes per graph: {max_nodes}",
        f"Memory: {mem_bits} bits ({2**mem_bits} states)",
        "",
        "PHASE BOUNDARIES:",
        f"  P1->P2 (peak spawn rate):",
        f"    step:     {np.mean(p12_steps):.0f} +/- {np.std(p12_steps):.0f}",
        f"    fraction: {np.mean(p12_fracs):.3f} +/- {np.std(p12_fracs):.3f}",
        f"  P2->P3 (per-capita rate < 1/N):",
    ]
    if p23_fracs:
        lines += [
            f"    step:     {np.mean(p23_steps):.0f} +/- {np.std(p23_steps):.0f}",
            f"    fraction: {np.mean(p23_fracs):.3f} +/- {np.std(p23_fracs):.3f}",
            f"    reached:  {len(p23_steps)}/{n_completed} seeds",
        ]
    else:
        lines.append("    not reached in any seed")

    lines += [
        "",
        "DEPTH STATISTICS:",
        f"  Max tree depth:    {np.mean(max_depths):.1f} +/- {np.std(max_depths):.1f}",
        f"  Final median depth: {np.mean(final_medians):.2f} +/- {np.std(final_medians):.2f}",
        "",
        "THREE-PHASE PATTERN:",
    ]

    # Assess whether three phases are present
    has_three = len(p23_steps) > 0
    if has_three:
        lines.append(f"  CONFIRMED in {len(p23_steps)}/{n_completed} seeds")
        lines.append(f"  Phase 1 (expansion):    steps 0 -- {np.mean(p12_steps):.0f}")
        lines.append(f"  Phase 2 (deceleration): steps {np.mean(p12_steps):.0f} -- {np.mean(p23_steps):.0f}")
        lines.append(f"  Phase 3 (structure):    steps {np.mean(p23_steps):.0f}+")
    else:
        lines.append("  NOT OBSERVED -- simulation may need more steps or smaller max_nodes")

    lines += ["", "Per-seed detail:"]
    for r in all_results:
        p23_str = str(r["p23_step"]) if r["p23_step"] else "N/A"
        lines.append(f"  seed={r['seed']}: {r['n_final']} nodes, "
                     f"P12={r['p12_step']}, P23={p23_str}, "
                     f"max_depth={r['max_depth']}, "
                     f"median_depth={r['final_median_depth']:.1f}")

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "phase_boundary_results.txt"), "w") as f:
        f.write(report)

    if all_results:
        _plot_phases(all_results, out_dir, progress)

    progress.update(n_seeds, n_seeds, "Done", f"{n_completed} seeds completed")


def _plot_phases(all_results, out_dir, progress):
    """Generate 4-panel phase boundary plot."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Growth curves (all seeds overlaid)
    ax = axes[0, 0]
    for r in all_results:
        total = len(r["steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["nodes"], alpha=0.4, color="#2196F3", linewidth=0.8)
    # Mark mean phase boundaries
    p12_fracs = [r["p12_step"] / max(len(r["steps"]), 1) for r in all_results]
    ax.axvline(np.mean(p12_fracs), color="orange", linestyle="--",
               label=f"P1->P2 ({np.mean(p12_fracs):.2f})")
    p23_fracs = [r["p23_step"] / max(len(r["steps"]), 1)
                 for r in all_results if r["p23_step"] is not None]
    if p23_fracs:
        ax.axvline(np.mean(p23_fracs), color="red", linestyle="--",
                   label=f"P2->P3 ({np.mean(p23_fracs):.2f})")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Node count")
    ax.set_title("Growth curves")
    ax.legend(fontsize=8)

    # Panel 2: Spawn rate over time
    ax = axes[0, 1]
    for r in all_results:
        total = len(r["spawn_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["smoothed_spawns"], alpha=0.4, color="#4CAF50", linewidth=0.8)
    ax.axvline(np.mean(p12_fracs), color="orange", linestyle="--")
    if p23_fracs:
        ax.axvline(np.mean(p23_fracs), color="red", linestyle="--")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Spawns/step (smoothed)")
    ax.set_title("Spawn rate")

    # Panel 3: Median depth over time
    ax = axes[1, 0]
    for r in all_results:
        total = len(r["sample_steps"])
        frac = np.linspace(0, 1, total)
        ax.plot(frac, r["median_depths"], alpha=0.4, color="#FF9800", linewidth=0.8)
    ax.axvline(np.mean(p12_fracs), color="orange", linestyle="--")
    if p23_fracs:
        ax.axvline(np.mean(p23_fracs), color="red", linestyle="--")
    ax.set_xlabel("Normalized step")
    ax.set_ylabel("Median tree depth")
    ax.set_title("Median depth evolution")

    # Panel 4: Depth distribution snapshots (last seed)
    ax = axes[1, 1]
    last = all_results[-1]
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(last["snapshots"])))
    for (frac, t, d), color in zip(last["snapshots"], colors):
        if len(d) > 1:
            bins = np.arange(0, d.max() + 2) - 0.5
            ax.hist(d, bins=bins, alpha=0.5, color=color,
                    label=f"t={frac:.0%}", density=True)
    ax.set_xlabel("Tree depth")
    ax.set_ylabel("Density")
    ax.set_title("Depth distribution snapshots")
    ax.legend(fontsize=8)

    plt.suptitle("O5: Phase Boundary Validation", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "phase_boundary.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
