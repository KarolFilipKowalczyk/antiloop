"""
O17 Memory Scaling: The Consciousness Band Sweet Spot
=====================================================

At what memory size does the consciousness band peak?

At mem_bits=2 (4 configs), nodes loop in at most 4 steps. There's barely
any state space to explore, so loop pressure is immediate and universal.
The anti-loop constraint has no room to create structured correlations.

At high mem_bits, nodes almost never loop -- they have so much state space
that pressure rarely triggers. Without pressure, there's no growth, and
without growth, there's no anti-loop topology to distinguish from random.

The consciousness band should be widest at some intermediate memory size
where pressure is real but the state space is rich enough for structure.

Additionally, at low memory, the C2 suffering gradient (absent at
mem_bits=8) might emerge -- nodes with tiny state spaces are fragile,
so even partial edge loss could cause measurable MI degradation.

Memory levels: [2, 4, 6, 8]
Skip 10+ -- MI computation at config_space=1024 is too slow (8MB per
joint histogram, thousands of calls per seed). Skip 12 entirely --
transition table is 133MB per node.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from simulation.engine import (
    HASH_XOR, run_antiloop, build_growing_random_control,
)
from simulation.experiments.c1_complexity import (
    mutual_information, edge_mi, nonedge_mi, run_dynamics_on_graph,
)

TITLE = "O17 Memory Scaling"


# ------------------------------------------------------------------
# C2 gradient test (low memory only)
# ------------------------------------------------------------------

def test_c2_gradient(G, trajectories, config_space, mem_bits, rng,
                     fractions=(0.25, 0.50, 0.75)):
    """Test whether partial edge removal causes gradual MI loss.

    At low memory, nodes are fragile -- the C2 gradient missing at
    mem_bits=8 might emerge here.

    Picks a moderate-degree node and removes fractions of its edges,
    then runs fresh dynamics and measures MI with remaining neighbors.

    Returns dict of {fraction: mi_loss_ratio} where 1.0 = no loss.
    """
    # Find a moderate-degree node (near median degree)
    degrees = dict(G.degree())
    sorted_nodes = sorted(degrees.keys(), key=lambda n: degrees[n])
    target = sorted_nodes[len(sorted_nodes) // 2]
    neighbors = list(G.neighbors(target))

    if len(neighbors) < 4:
        return None  # not enough edges to test

    # Baseline MI: target vs each neighbor from growth trajectories
    baseline_mis = []
    for nb in neighbors:
        if target in trajectories and nb in trajectories:
            mi = mutual_information(trajectories[target], trajectories[nb],
                                    config_space)
            baseline_mis.append(mi)
    if not baseline_mis:
        return None
    baseline_mean = np.mean(baseline_mis)
    if baseline_mean < 1e-6:
        return None

    results = {}
    for frac in fractions:
        n_remove = max(1, int(len(neighbors) * frac))
        remove_set = set(rng.choice(neighbors, size=n_remove, replace=False))
        remaining = [nb for nb in neighbors if nb not in remove_set]

        if not remaining:
            results[frac] = 0.0
            continue

        # Copy graph, remove edges
        G_damaged = G.copy()
        for nb in remove_set:
            if G_damaged.has_edge(target, nb):
                G_damaged.remove_edge(target, nb)

        # Run fresh dynamics on damaged graph
        n_steps = max(len(v) for v in trajectories.values())
        seed_val = hash(f"{target}_{frac}") % (2**31)
        damaged_traj = run_dynamics_on_graph(G_damaged, mem_bits,
                                             steps=n_steps,
                                             seed=seed_val)

        # Measure MI with remaining neighbors
        post_mis = []
        for nb in remaining:
            if target in damaged_traj and nb in damaged_traj:
                mi = mutual_information(damaged_traj[target],
                                        damaged_traj[nb],
                                        config_space)
                post_mis.append(mi)

        if post_mis:
            results[frac] = np.mean(post_mis) / baseline_mean
        else:
            results[frac] = 0.0

    return results


# ------------------------------------------------------------------
# Main experiment
# ------------------------------------------------------------------

def run(n_seeds=30, max_nodes=500, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Run the O17 memory scaling experiment."""
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    output_lines = []

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    log("=" * 70)
    log("O17: MEMORY SCALING -- The Consciousness Band Sweet Spot")
    log("=" * 70)
    log("At what memory size does the MI ratio peak?")
    log()

    mem_levels = [2, 4, 6, 8]
    nodes_for = {2: max_nodes, 4: max_nodes, 6: max_nodes, 8: max_nodes}

    log(f"Memory levels: {mem_levels}")
    log(f"Max nodes: {nodes_for}")
    log()

    # ----------------------------------------------------------
    # Calibration: time FULL pipeline at each memory level
    # ----------------------------------------------------------
    log("Calibrating each memory level...")
    cal_times = {}
    for mb in mem_levels:
        cal_nodes = min(nodes_for[mb], 80)
        config_space = 2 ** mb
        cal_rng = np.random.default_rng(99999)

        t0 = time.time()
        # Growth + trajectories
        _, G_cal, glog_cal, traj_cal = run_antiloop(
            mem_bits=mb, max_nodes=cal_nodes, initial_n=10,
            seed=999, hash_fn=HASH_XOR, record_trajectories=True
        )
        n_steps_cal = max(len(v) for v in traj_cal.values())
        # MI on anti-loop
        edge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
        nonedge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
        # Control + dynamics + MI
        G_ctrl_cal = build_growing_random_control(glog_cal, seed=99998)
        ctrl_traj = run_dynamics_on_graph(G_ctrl_cal, mb,
                                          steps=n_steps_cal, seed=99997)
        edge_mi(G_ctrl_cal, ctrl_traj, config_space, rng=cal_rng)
        nonedge_mi(G_ctrl_cal, ctrl_traj, config_space, rng=cal_rng)
        # C2 test (if low memory)
        if mb <= 4:
            test_c2_gradient(G_cal, traj_cal, config_space, mb, rng=cal_rng)

        sec_cal = time.time() - t0
        # Scale from cal_nodes to target nodes
        target_nodes = nodes_for[mb]
        scale = (target_nodes / cal_nodes) ** 2.0 if target_nodes > cal_nodes else 1.0
        cal_times[mb] = sec_cal * scale
        log(f"  mem_bits={mb:2d}: {sec_cal:.2f}s @ {cal_nodes} nodes -> "
            f"{cal_times[mb]:.1f}s estimated @ {target_nodes} nodes")

    total_estimated = sum(cal_times.values())
    available = time_budget * 0.80
    # Distribute seeds proportionally: more seeds to cheap levels
    if total_estimated > 0:
        seeds_per_level = {}
        for mb in mem_levels:
            budget_share = available / len(mem_levels)
            seeds_this = max(2, int(budget_share / max(cal_times[mb], 0.1)))
            seeds_per_level[mb] = min(n_seeds, seeds_this)
    else:
        seeds_per_level = {mb: min(n_seeds, 3) for mb in mem_levels}

    log()
    log(f"  Budget: {time_budget}s  |  Seeds per level: {seeds_per_level}")
    log()

    # ----------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------
    # Storage
    results = {}  # results[mb] = dict of lists
    for mb in mem_levels:
        results[mb] = {
            "al_edge_mi": [], "al_nonedge_mi": [], "al_ratio": [],
            "ct_edge_mi": [], "ct_nonedge_mi": [], "ct_ratio": [],
            "growth_steps": [], "mean_pressure": [],
            "c2_gradient": [],  # list of dicts (only for mb <= 4)
        }

    total_work = sum(seeds_per_level[mb] * 3 for mb in mem_levels)
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    for mb in mem_levels:
        config_space = 2 ** mb
        target_nodes = nodes_for[mb]
        n_seeds_level = seeds_per_level[mb]

        log(f"=== mem_bits={mb} (config_space={config_space}, "
            f"nodes={target_nodes}, seeds={n_seeds_level}) ===")

        for seed_idx in range(n_seeds_level):
            seed = seed_idx
            rng = np.random.default_rng(seed + 77777)

            # Anti-loop growth
            G_growth, G_final, glog, traj_al = run_antiloop(
                mem_bits=mb, max_nodes=target_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, record_trajectories=True
            )
            n_steps = max(len(v) for v in traj_al.values())
            step("Growth", f"mem={mb}, seed {seed_idx + 1}/{n_seeds_level}")

            # MI on anti-loop
            al_e, _, _ = edge_mi(G_final, traj_al, config_space, rng=rng)
            al_ne, _, _ = nonedge_mi(G_final, traj_al, config_space, rng=rng)
            al_r = al_e / al_ne if al_ne > 0 else 1.0
            step("Anti-loop MI", f"mem={mb}, ratio={al_r:.3f}")

            # Control
            G_ctrl = build_growing_random_control(glog, seed=seed + 10000)
            ctrl_traj = run_dynamics_on_graph(G_ctrl, mb, steps=n_steps,
                                              seed=seed + 20000)
            ct_e, _, _ = edge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
            ct_ne, _, _ = nonedge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
            ct_r = ct_e / ct_ne if ct_ne > 0 else 1.0
            step("Control MI", f"mem={mb}, ratio={ct_r:.3f}")

            # Mean pressure
            pressures = []
            for nid in G_final.nodes():
                # Pressure = len(visited) / config_space
                # We don't have live FSMNodes, but can estimate from trajectories
                if nid in traj_al:
                    unique_configs = len(set(traj_al[nid]))
                    pressures.append(unique_configs / config_space)
            mean_p = np.mean(pressures) if pressures else 0.0

            results[mb]["al_edge_mi"].append(al_e)
            results[mb]["al_nonedge_mi"].append(al_ne)
            results[mb]["al_ratio"].append(al_r)
            results[mb]["ct_edge_mi"].append(ct_e)
            results[mb]["ct_nonedge_mi"].append(ct_ne)
            results[mb]["ct_ratio"].append(ct_r)
            results[mb]["growth_steps"].append(n_steps)
            results[mb]["mean_pressure"].append(mean_p)

            # C2 gradient test (low memory only)
            if mb <= 4:
                c2 = test_c2_gradient(G_final, traj_al, config_space, mb,
                                       rng=rng)
                if c2 is not None:
                    results[mb]["c2_gradient"].append(c2)

            log(f"  Seed {seed_idx}: AL ratio={al_r:.3f} "
                f"CT ratio={ct_r:.3f} pressure={mean_p:.3f} "
                f"steps={n_steps}")

        log()

    # ----------------------------------------------------------
    # Analysis
    # ----------------------------------------------------------
    log("=" * 70)
    log("ANALYSIS")
    log("=" * 70)
    log()

    log(f"  {'mem_bits':>8}  {'AL ratio':>10}  {'CT ratio':>10}  "
        f"{'Gap':>8}  {'Pressure':>10}  {'Steps':>8}  {'Seeds':>6}")
    log(f"  {'-' * 72}")

    peak_mb = None
    peak_ratio = 0.0

    for mb in mem_levels:
        al_r = np.array(results[mb]["al_ratio"])
        ct_r = np.array(results[mb]["ct_ratio"])
        pressures = np.array(results[mb]["mean_pressure"])
        steps = np.array(results[mb]["growth_steps"])

        mean_al = al_r.mean()
        mean_ct = ct_r.mean()
        gap = mean_al - mean_ct

        log(f"  {mb:>8}  {mean_al:>10.3f}  {mean_ct:>10.3f}  "
            f"{gap:>8.3f}  {pressures.mean():>10.3f}  "
            f"{steps.mean():>8.0f}  {len(al_r):>6}")

        if gap > peak_ratio:
            peak_ratio = gap
            peak_mb = mb

    log()
    if peak_mb is not None:
        log(f"  Peak MI ratio gap at mem_bits = {peak_mb} "
            f"(gap = {peak_ratio:.3f})")
    log()

    # C2 gradient results
    c2_tested = [mb for mb in mem_levels if results[mb]["c2_gradient"]]
    if c2_tested:
        log("  C2 Gradient Test (low memory):")
        for mb in c2_tested:
            gradients = results[mb]["c2_gradient"]
            # Average across seeds for each fraction
            fracs = sorted(gradients[0].keys())
            log(f"    mem_bits={mb}:")
            for frac in fracs:
                vals = [g[frac] for g in gradients if frac in g]
                mean_val = np.mean(vals)
                log(f"      {frac:.0%} removed: MI retention = "
                    f"{mean_val:.3f} ({(1 - mean_val):.1%} loss)")
            # Check for gradient
            vals_25 = [g.get(0.25, 1.0) for g in gradients]
            vals_75 = [g.get(0.75, 1.0) for g in gradients]
            if np.mean(vals_25) > np.mean(vals_75) + 0.01:
                log(f"      -> GRADIENT DETECTED: more removal = more loss")
            else:
                log(f"      -> No gradient (same as C2 at mem_bits=8)")
        log()

    # Statistical test: is the peak significantly above neighbors?
    log("  Statistical tests:")
    for mb in mem_levels:
        al_r = np.array(results[mb]["al_ratio"])
        ct_r = np.array(results[mb]["ct_ratio"])
        if len(al_r) >= 2 and len(ct_r) >= 2:
            t_stat, p_val = stats.ttest_ind(al_r, ct_r)
            consistent = np.sum(al_r.mean() > ct_r)
            log(f"    mem_bits={mb}: AL={al_r.mean():.3f} vs CT={ct_r.mean():.3f}"
                f"  t={t_stat:.2f}, p={p_val:.4f}")
    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    # Check for inverted-U pattern
    al_means = [np.mean(results[mb]["al_ratio"]) for mb in mem_levels]
    ct_means = [np.mean(results[mb]["ct_ratio"]) for mb in mem_levels]
    gaps = [a - c for a, c in zip(al_means, ct_means)]

    # Is there a peak in the middle?
    if len(gaps) >= 3:
        max_idx = np.argmax(gaps)
        is_interior = 0 < max_idx < len(gaps) - 1
        has_peak = gaps[max_idx] > 0.02  # meaningful gap

        if is_interior and has_peak:
            log(f"RESULT: POSITIVE -- Consciousness band peaks at "
                f"mem_bits={mem_levels[max_idx]}.")
            log(f"  Peak gap: {gaps[max_idx]:.3f} "
                f"(AL={al_means[max_idx]:.3f} vs CT={ct_means[max_idx]:.3f})")
            log(f"  Low memory ({mem_levels[0]}): gap={gaps[0]:.3f} "
                f"-- {'no band' if gaps[0] < 0.02 else 'band present'}")
            log(f"  High memory ({mem_levels[-1]}): gap={gaps[-1]:.3f} "
                f"-- {'no band' if gaps[-1] < 0.02 else 'band present'}")
            log("  The consciousness band requires intermediate memory:")
            log("  enough state space for structure, enough pressure for growth.")
        elif has_peak and max_idx == 0:
            log(f"RESULT: PARTIAL -- Band strongest at lowest tested memory "
                f"(mem_bits={mem_levels[0]}).")
            log("  Consider testing even lower memory if possible.")
        elif has_peak and max_idx == len(gaps) - 1:
            log(f"RESULT: PARTIAL -- Band strongest at highest tested memory "
                f"(mem_bits={mem_levels[-1]}).")
            log("  The peak may be beyond our tested range.")
        else:
            log("RESULT: NEGATIVE -- No clear peak in consciousness band "
                "across memory levels.")
            log(f"  Gaps: {[(mb, f'{g:.3f}') for mb, g in zip(mem_levels, gaps)]}")
    else:
        log("RESULT: INCONCLUSIVE -- Not enough memory levels tested.")

    # C2 verdict
    if c2_tested:
        for mb in c2_tested:
            gradients = results[mb]["c2_gradient"]
            if gradients:
                vals_25 = [g.get(0.25, 1.0) for g in gradients]
                vals_75 = [g.get(0.75, 1.0) for g in gradients]
                if np.mean(vals_25) > np.mean(vals_75) + 0.02:
                    log(f"  C2 at mem_bits={mb}: GRADIENT FOUND -- "
                        "partial edge loss causes proportional MI degradation.")
                else:
                    log(f"  C2 at mem_bits={mb}: No gradient -- "
                        "same binary behavior as mem_bits=8.")
    log()

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    n_plots = 4 if c2_tested else 3
    fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5))
    fig.suptitle("O17: Memory Scaling -- Consciousness Band Sweet Spot",
                 fontweight="bold", fontsize=13)

    # Plot 1: MI ratio vs mem_bits
    ax = axes[0]
    al_m = [np.mean(results[mb]["al_ratio"]) for mb in mem_levels]
    al_s = [np.std(results[mb]["al_ratio"]) for mb in mem_levels]
    ct_m = [np.mean(results[mb]["ct_ratio"]) for mb in mem_levels]
    ct_s = [np.std(results[mb]["ct_ratio"]) for mb in mem_levels]

    x = np.arange(len(mem_levels))
    w = 0.35
    ax.bar(x - w / 2, al_m, w, yerr=al_s, capsize=4,
           label="Anti-loop", color="tab:blue", alpha=0.7)
    ax.bar(x + w / 2, ct_m, w, yerr=ct_s, capsize=4,
           label="Control", color="tab:red", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(mb) for mb in mem_levels])
    ax.set_xlabel("mem_bits")
    ax.set_ylabel("MI ratio (edge / non-edge)")
    ax.set_title("Consciousness Band vs Memory")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # Plot 2: Edge MI and non-edge MI
    ax = axes[1]
    al_e_m = [np.mean(results[mb]["al_edge_mi"]) for mb in mem_levels]
    al_ne_m = [np.mean(results[mb]["al_nonedge_mi"]) for mb in mem_levels]
    ax.plot(mem_levels, al_e_m, "b-o", label="Edge MI (anti-loop)", linewidth=2)
    ax.plot(mem_levels, al_ne_m, "b--s", label="Non-edge MI (anti-loop)",
            linewidth=1.5, alpha=0.7)
    ct_e_m = [np.mean(results[mb]["ct_edge_mi"]) for mb in mem_levels]
    ct_ne_m = [np.mean(results[mb]["ct_nonedge_mi"]) for mb in mem_levels]
    ax.plot(mem_levels, ct_e_m, "r-o", label="Edge MI (control)", linewidth=1.5)
    ax.plot(mem_levels, ct_ne_m, "r--s", label="Non-edge MI (control)",
            linewidth=1, alpha=0.7)
    ax.set_xlabel("mem_bits")
    ax.set_ylabel("MI (bits)")
    ax.set_title("Edge vs Non-edge MI")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Plot 3: Growth metrics
    ax = axes[2]
    pressures_m = [np.mean(results[mb]["mean_pressure"]) for mb in mem_levels]
    pressures_s = [np.std(results[mb]["mean_pressure"]) for mb in mem_levels]
    ax.bar(x, pressures_m, 0.6, yerr=pressures_s, capsize=4,
           color="tab:green", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([str(mb) for mb in mem_levels])
    ax.set_xlabel("mem_bits")
    ax.set_ylabel("Mean pressure (visited / config_space)")
    ax.set_title("Loop Pressure vs Memory")
    ax.grid(True, alpha=0.3, axis="y")

    # Plot 4: C2 gradient (if tested)
    if c2_tested and len(axes) > 3:
        ax = axes[3]
        for mb in c2_tested:
            gradients = results[mb]["c2_gradient"]
            if gradients:
                fracs = sorted(gradients[0].keys())
                means = [np.mean([g[f] for g in gradients if f in g])
                         for f in fracs]
                ax.plot([f * 100 for f in fracs], means,
                        "-o", label=f"mem_bits={mb}", linewidth=2)
        ax.set_xlabel("% edges removed")
        ax.set_ylabel("MI retention (1.0 = no loss)")
        ax.set_title("C2 Gradient (Low Memory)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "memory_scaling.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------
    with open(os.path.join(out_dir, "memory_scaling_results.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
