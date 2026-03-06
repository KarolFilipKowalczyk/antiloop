"""
C3 Topology Experiment: Scale-Free Networks from Anti-Loop Constraint
=====================================================================

Tests whether the anti-loop constraint produces scale-free degree distributions.

Addresses all known flaws from the preliminary test:
  1. Growing random graph control (not static Erdos-Renyi)
  2. Clauset-Shalizi-Newman power-law test
  3. Multiple seeds with statistical summary
  4. Sensitivity analysis: hash function, pressure threshold, spawn probability
  5. Growth phase vs cap phase separation

Time-budgeted: calibrates steps/second on the first run, then fits
as many seeds as possible within the given time budget.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from simulation.engine import (
    HASH_XOR, HASH_SUM, HASH_PRODUCT,
    run_antiloop, build_growing_random_control,
)
from simulation.analysis import analyze_powerlaw, get_ccdf, format_powerlaw_result

TITLE = "C3 Scale-Free Topology"


def _calibrate(mem_bits, max_nodes):
    """Time a single run_antiloop call to estimate seconds per run."""
    t0 = time.time()
    run_antiloop(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3
    )
    return time.time() - t0


def run(n_seeds=30, max_nodes=500, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Run the full C3 experiment.

    Args:
        time_budget: total wall-clock seconds. Calibrates on the first
            run, then allocates seeds across parts to fit the budget.
            Default 300s (5 min).
    """

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
    log("PROPER C3 TEST: Scale-Free Topology from Anti-Loop Constraint")
    log("=" * 70)

    # ----------------------------------------------------------
    # Calibration
    # ----------------------------------------------------------
    log("Calibrating...")
    sec_per_run = _calibrate(mem_bits, max_nodes)
    log(f"  {sec_per_run:.2f}s per run (nodes={max_nodes}, mem={mem_bits}-bit)")

    # Budget allocation:
    #   Part 1: n_seeds runs (antiloop) + n_seeds runs (control) = 2*n_seeds
    #   Part 2: 3 hash * sens_seeds + 5 thresh * sens_seeds + 5 spawn * sens_seeds = 13*sens_seeds
    #   Part 3: sens_seeds runs
    #   Total = 2*n_seeds + 14*sens_seeds runs
    # Reserve 10% for plotting/analysis
    available = time_budget * 0.90
    total_runs_needed = 2 * n_seeds + 14 * min(10, n_seeds)
    time_needed = total_runs_needed * sec_per_run

    if time_needed > available:
        # Scale down seeds to fit
        # Solve: 2*s + 14*min(10,s) <= available/sec_per_run
        max_runs = available / sec_per_run
        # Try with sens_seeds = min(10, n_seeds)
        # If n_seeds <= 10: total = 2*s + 14*s = 16*s, so s = max_runs/16
        # If n_seeds > 10: total = 2*s + 140, so s = (max_runs-140)/2
        if n_seeds <= 10:
            n_seeds = max(2, int(max_runs / 16))
        else:
            n_seeds = max(2, int((max_runs - 140) / 2))
            if n_seeds <= 10:
                n_seeds = max(2, int(max_runs / 16))

    sens_seeds = min(10, n_seeds)
    total_runs = 2 * n_seeds + 14 * sens_seeds
    estimated_time = total_runs * sec_per_run

    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}  |  Sensitivity seeds: {sens_seeds}")
    log(f"  Estimated: {total_runs} runs x {sec_per_run:.2f}s = {estimated_time:.0f}s")
    log()

    # Progress tracking
    total_work = total_runs
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    seeds = list(range(n_seeds))

    # ----------------------------------------------------------
    # Part 1: Anti-loop vs growing random control
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 1: Anti-loop vs growing random graph control")
    log("-" * 70)

    antiloop_alphas = []
    control_alphas = []
    antiloop_results = []
    control_results = []
    example_antiloop_G = None
    example_control_G = None

    t0_total = time.time()

    for i, seed in enumerate(seeds):
        t0 = time.time()

        G_growth, G_final, glog, _ = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )

        G_ctrl = build_growing_random_control(glog, seed=seed + 10000)

        r_al = analyze_powerlaw(G_final, f"antiloop_seed{seed}")
        r_ct = analyze_powerlaw(G_ctrl, f"control_seed{seed}")

        if r_al["alpha"] is not None:
            antiloop_alphas.append(r_al["alpha"])
            antiloop_results.append(r_al)
        if r_ct["alpha"] is not None:
            control_alphas.append(r_ct["alpha"])
            control_results.append(r_ct)

        elapsed = time.time() - t0
        al_a = f"{r_al['alpha']:.2f}" if r_al["alpha"] else "N/A"
        ct_a = f"{r_ct['alpha']:.2f}" if r_ct["alpha"] else "N/A"
        log(f"  seed {seed:>2}: antiloop alpha={al_a}  control alpha={ct_a}  "
            f"({elapsed:.1f}s)")

        step("Part 1: Anti-loop vs control",
             f"Seed {i+1}/{n_seeds}  |  alpha={al_a}")

        if i == 0:
            example_antiloop_G = G_final
            example_control_G = G_ctrl

    total_time = time.time() - t0_total
    log()

    if antiloop_alphas:
        al_arr = np.array(antiloop_alphas)
        log(f"Anti-loop alpha:  mean={al_arr.mean():.3f}  "
            f"std={al_arr.std():.3f}  "
            f"range=[{al_arr.min():.3f}, {al_arr.max():.3f}]")
    if control_alphas:
        ct_arr = np.array(control_alphas)
        log(f"Control alpha:    mean={ct_arr.mean():.3f}  "
            f"std={ct_arr.std():.3f}  "
            f"range=[{ct_arr.min():.3f}, {ct_arr.max():.3f}]")

    ba_G = nx.barabasi_albert_graph(max_nodes, 3, seed=42)
    r_ba = analyze_powerlaw(ba_G, "barabasi_albert")
    if r_ba["alpha"] is not None:
        log(f"BA reference:     alpha={r_ba['alpha']:.3f}")

    log(f"\nPart 1 time: {total_time:.1f}s")
    log()

    if antiloop_results:
        log("Detailed power-law analysis (seed 0):")
        log(format_powerlaw_result(antiloop_results[0]))
        log(format_powerlaw_result(control_results[0]))
        log(format_powerlaw_result(r_ba))
        log()

    # ----------------------------------------------------------
    # Part 2: Sensitivity analysis
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 2: Sensitivity analysis")
    log("-" * 70)

    sensitivity_results = {}
    sens_list = seeds[:sens_seeds]

    # 2a: Hash function
    log("\n  Hash function sensitivity:")
    for hf in [HASH_XOR, HASH_SUM, HASH_PRODUCT]:
        alphas = []
        for seed in sens_list:
            _, G, _, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=hf, pressure_threshold=0.7, spawn_prob=0.3
            )
            r = analyze_powerlaw(G, f"hash_{hf}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
            step("Part 2: Sensitivity — hash function", f"hash={hf}")
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"hash_{hf}"] = arr
        if len(arr):
            log(f"    {hf:>8}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    {hf:>8}: insufficient data")

    # 2b: Pressure threshold
    log("\n  Pressure threshold sensitivity:")
    for thresh in [0.5, 0.6, 0.7, 0.8, 0.9]:
        alphas = []
        for seed in sens_list:
            _, G, _, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=thresh,
                spawn_prob=0.3
            )
            r = analyze_powerlaw(G, f"thresh_{thresh}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
            step("Part 2: Sensitivity — pressure threshold", f"threshold={thresh}")
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"thresh_{thresh}"] = arr
        if len(arr):
            log(f"    thresh={thresh}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    thresh={thresh}: insufficient data")

    # 2c: Spawn probability
    log("\n  Spawn probability sensitivity:")
    for sp in [0.1, 0.2, 0.3, 0.5, 0.7]:
        alphas = []
        for seed in sens_list:
            _, G, _, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
                spawn_prob=sp
            )
            r = analyze_powerlaw(G, f"spawn_{sp}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
            step("Part 2: Sensitivity — spawn probability", f"spawn={sp}")
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"spawn_{sp}"] = arr
        if len(arr):
            log(f"    spawn={sp}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    spawn={sp}: insufficient data")

    log()

    # ----------------------------------------------------------
    # Part 3: Growth phase vs cap phase
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 3: Growth phase vs cap phase topology")
    log("-" * 70)

    growth_alphas = []
    cap_alphas = []
    for seed in sens_list:
        G_growth, G_final, _, _ = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )
        r_gr = analyze_powerlaw(G_growth, f"growth_s{seed}")
        r_cp = analyze_powerlaw(G_final, f"cap_s{seed}")
        if r_gr["alpha"] is not None:
            growth_alphas.append(r_gr["alpha"])
        if r_cp["alpha"] is not None:
            cap_alphas.append(r_cp["alpha"])
        step("Part 3: Growth vs cap phase", f"seed {seed}")

    if growth_alphas:
        g_arr = np.array(growth_alphas)
        log(f"  Growth phase:  alpha={g_arr.mean():.3f} +/- {g_arr.std():.3f}")
    if cap_alphas:
        c_arr = np.array(cap_alphas)
        log(f"  Cap phase:     alpha={c_arr.mean():.3f} +/- {c_arr.std():.3f}")
    log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------

    # Plot 1: Degree distributions
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("C3 Test: Degree Distributions (CCDF, log-log)", fontweight="bold")

    for ax, G, label, color in [
        (axes[0], example_antiloop_G, "Anti-loop", "tab:blue"),
        (axes[1], example_control_G, "Growing random control", "tab:gray"),
        (axes[2], ba_G, "Barabasi-Albert reference", "tab:red"),
    ]:
        k, ccdf = get_ccdf(G)
        ax.loglog(k, ccdf, "o-", markersize=3, color=color)
        ax.set_xlabel("Degree k")
        ax.set_ylabel("P(K >= k)")
        ax.set_title(label)
        ax.grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_degree_distributions.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 2: Alpha distributions
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    fig.suptitle("C3 Test: Power-Law Exponent Distribution", fontweight="bold")

    if antiloop_alphas:
        ax.hist(antiloop_alphas, bins=15, alpha=0.6, label="Anti-loop", color="tab:blue")
    if control_alphas:
        ax.hist(control_alphas, bins=15, alpha=0.6, label="Growing random control",
                color="tab:gray")
    if r_ba["alpha"]:
        ax.axvline(r_ba["alpha"], color="tab:red", linestyle="--",
                   label=f"BA ref (alpha={r_ba['alpha']:.2f})")
    ax.axvspan(2, 3, alpha=0.1, color="green", label="Classic scale-free range")
    ax.set_xlabel("alpha")
    ax.set_ylabel("Count")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_powerlaw_fits.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 3: Sensitivity
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("C3 Test: Sensitivity Analysis", fontweight="bold")

    # Hash function
    ax = axes[0]
    labels, means, stds = [], [], []
    for hf in [HASH_XOR, HASH_SUM, HASH_PRODUCT]:
        arr = sensitivity_results.get(f"hash_{hf}", np.array([]))
        if len(arr):
            labels.append(hf)
            means.append(arr.mean())
            stds.append(arr.std())
    if labels:
        ax.bar(labels, means, yerr=stds, capsize=5, color="tab:blue", alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Hash function")
    ax.grid(True, alpha=0.3)

    # Pressure threshold
    ax = axes[1]
    labels, means, stds = [], [], []
    for thresh in [0.5, 0.6, 0.7, 0.8, 0.9]:
        arr = sensitivity_results.get(f"thresh_{thresh}", np.array([]))
        if len(arr):
            labels.append(str(thresh))
            means.append(arr.mean())
            stds.append(arr.std())
    if labels:
        ax.bar(labels, means, yerr=stds, capsize=5, color="tab:orange", alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Loop pressure threshold")
    ax.grid(True, alpha=0.3)

    # Spawn probability
    ax = axes[2]
    labels, means, stds = [], [], []
    for sp in [0.1, 0.2, 0.3, 0.5, 0.7]:
        arr = sensitivity_results.get(f"spawn_{sp}", np.array([]))
        if len(arr):
            labels.append(str(sp))
            means.append(arr.mean())
            stds.append(arr.std())
    if labels:
        ax.bar(labels, means, yerr=stds, capsize=5, color="tab:green", alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Spawn probability")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_sensitivity.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)

    if antiloop_alphas and control_alphas:
        al_mean = np.mean(antiloop_alphas)
        ct_mean = np.mean(control_alphas)

        in_range = 2.0 <= al_mean <= 3.0
        different = abs(al_mean - ct_mean) > 0.3

        n_pl_preferred = sum(
            1 for r in antiloop_results
            if r["vs_exp"] and r["vs_exp"]["R"] > 0 and r["vs_exp"]["p"] < 0.05
        )
        frac_preferred = n_pl_preferred / len(antiloop_results) if antiloop_results else 0

        log(f"Anti-loop mean alpha:  {al_mean:.3f}  (scale-free range: 2-3)")
        log(f"Control mean alpha:    {ct_mean:.3f}")
        log(f"Power law preferred over exponential: "
            f"{n_pl_preferred}/{len(antiloop_results)} "
            f"({frac_preferred*100:.0f}%) of anti-loop runs")
        log()

        if in_range and frac_preferred > 0.5:
            log("RESULT: POSITIVE — Anti-loop constraint produces scale-free-like")
            log("degree distributions with alpha in the classic range.")
            if not different:
                log("WARNING: Control also shows similar alpha. The effect may be")
                log("driven by the growth process, not the anti-loop constraint.")
        else:
            log("RESULT: NEGATIVE or INCONCLUSIVE — Anti-loop constraint does not")
            log("reliably produce classic scale-free topology at this scale.")

        hash_vals = [sensitivity_results.get(f"hash_{h}", np.array([]))
                     for h in [HASH_XOR, HASH_SUM, HASH_PRODUCT]]
        hash_means = [a.mean() for a in hash_vals if len(a)]
        if len(hash_means) >= 2:
            spread = max(hash_means) - min(hash_means)
            if spread > 0.5:
                log(f"\nWARNING: Hash function changes alpha by {spread:.2f}.")
                log("Result is hash-dependent.")
            else:
                log(f"\nHash function robustness: alpha spread = {spread:.2f} (OK)")
    else:
        log("INSUFFICIENT DATA — could not compute verdict.")

    log()

    with open(os.path.join(out_dir, "c3_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
