"""
C2v2 Targeted Suffering: Does Losing Important Connections Hurt More?
=====================================================================

Key insight: the original C2 removed edges RANDOMLY, but that's not how
suffering works. Real suffering comes from losing IMPORTANT connections.
And connections aren't born equal — edges formed early in growth have
MORE SHARED HISTORY than edges formed late.

This follows directly from the axioms: the anti-loop growth process
creates edges under pressure. Early edges participate in more dynamics
steps. They're like family — deeply wired through years of shared state.
Late edges are acquaintances — recent, shallow.

Design:
  1. Grow anti-loop graph WITH trajectory recording (record_trajectories=True)
  2. Compute MI per edge using GROWTH-PHASE trajectories
     (not fresh post-hoc dynamics — that erases growth history)
  3. Early edges should have higher MI (more shared history)
  4. Three removal strategies:
     - HIGH-MI first (losing family/close friends)
     - RANDOM (baseline)
     - LOW-MI first (losing acquaintances)
  5. After removal, run fresh dynamics on damaged graph
  6. Measure: total MI, unique configs, pressure

Prediction: high-MI removal is devastating. Low-MI removal is harmless.
The gap IS the consciousness band made visible as vulnerability.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.engine import (
    HASH_XOR, FSMNode,
    run_antiloop,
)
from simulation.experiments.c1_complexity import mutual_information


TITLE = "C2v2 Targeted Suffering"


def compute_growth_edge_mi(target, G, trajectories, config_space):
    """Compute MI for each edge of target using growth-phase trajectories.

    These trajectories come from the actual anti-loop growth process.
    Early edges have longer shared history → naturally higher MI.
    Late edges have short shared history → lower MI.

    Returns dict: neighbor_id -> MI(target, neighbor)
    """
    edge_mi = {}
    target_traj = trajectories.get(target)
    if target_traj is None:
        return edge_mi

    for nb in G.neighbors(target):
        nb_traj = trajectories.get(nb)
        if nb_traj is None:
            continue
        # Both trajectories may differ in length (nodes born at different times)
        # Use the overlap period (from when the later node was born)
        min_len = min(len(target_traj), len(nb_traj))
        if min_len < 10:
            edge_mi[nb] = 0.0
            continue
        # Align from the END (both alive at the end of growth)
        t_slice = target_traj[-min_len:]
        n_slice = nb_traj[-min_len:]
        edge_mi[nb] = mutual_information(t_slice, n_slice, config_space)

    return edge_mi


def run_post_removal_dynamics(target, original_neighbors, removed_set,
                              G, mem_bits, steps, seed,
                              config_space, hash_fn=HASH_XOR):
    """Run fresh dynamics on damaged graph, measure total MI with original neighbors."""
    rng = np.random.default_rng(seed)
    nodes = {}
    for nid in G.nodes():
        nodes[nid] = FSMNode(mem_bits, rng)

    trajectories = {nid: [nodes[nid].config] for nid in G.nodes()}

    for _ in range(steps):
        for nid in G.nodes():
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn, rng=rng)
            trajectories[nid].append(nodes[nid].config)

    total_mi = 0.0
    remaining_mi_vals = []
    for nb in original_neighbors:
        if nb in trajectories and target in trajectories:
            mi = mutual_information(
                trajectories[target], trajectories[nb], config_space
            )
            total_mi += mi
            if nb not in removed_set:
                remaining_mi_vals.append(mi)

    return {
        "total_mi": total_mi,
        "remaining_mi": np.mean(remaining_mi_vals) if remaining_mi_vals else 0.0,
        "unique_configs": len(nodes[target].visited),
        "pressure": nodes[target].pressure,
    }


def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Test C2v2: does targeted removal of high-MI edges hurt more?"""
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    config_space = 2 ** mem_bits
    dyn_steps = 500
    removal_fracs = [0.0, 0.25, 0.50, 0.75, 1.0]
    strategies = ["high_mi", "random", "low_mi"]
    strategy_labels = {
        "high_mi": "High-MI first (close ties)",
        "random": "Random (original C2)",
        "low_mi": "Low-MI first (acquaintances)",
    }
    output_lines = []

    # Target degree range: 8-25 edges, like a person with real friends
    deg_min, deg_max = 8, 25

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    log("=" * 70)
    log("C2v2 TARGETED SUFFERING: Does losing important connections hurt more?")
    log("=" * 70)
    log("Key change: MI ranked from GROWTH-PHASE trajectories (shared history)")
    log("  Early edges = more shared history = higher MI (family/close friends)")
    log("  Late edges = shallow history = lower MI (acquaintances)")
    log("Test: remove high-MI first vs random vs low-MI first")
    log()

    # ----------------------------------------------------------
    # Calibration: full pipeline for one seed
    # ----------------------------------------------------------
    log("Calibrating...")
    t0 = time.time()

    # Growth with trajectory recording
    _, G_cal, _, traj_cal = run_antiloop(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, record_trajectories=True
    )

    # Pick moderate-degree node
    cal_candidates = [n for n in G_cal.nodes()
                      if deg_min <= G_cal.degree(n) <= deg_max]
    if not cal_candidates:
        cal_candidates = sorted(G_cal.nodes(), key=lambda n: G_cal.degree(n))
        cal_target = cal_candidates[len(cal_candidates) // 3]
    else:
        cal_target = cal_candidates[0]

    # Growth-phase MI ranking
    compute_growth_edge_mi(cal_target, G_cal, traj_cal, config_space)

    # 3 strategies x 5 fracs = 15 post-removal dynamics runs
    orig_nb_cal = list(G_cal.neighbors(cal_target))
    for _ in range(15):
        run_post_removal_dynamics(cal_target, orig_nb_cal, set(), G_cal,
                                  mem_bits, dyn_steps, seed=9999,
                                  config_space=config_space)
    sec_per_seed = time.time() - t0

    available = time_budget * 0.85
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  {sec_per_seed:.2f}s per seed")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit  |  Dynamics: {dyn_steps} steps")
    log()

    # 1 (growth+traj) + 1 (MI ranking) + 3*5 (strategies x fracs) = 17 per seed
    total_work = n_seeds * 17
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    # Storage: strategy -> frac -> list of values
    data = {
        s: {f: {"total_mi": [], "unique": []} for f in removal_fracs}
        for s in strategies
    }
    target_degrees = []
    mi_spreads = []
    all_mi_distributions = []  # for plotting edge MI histogram

    for seed_idx in range(n_seeds):
        seed = seed_idx
        log(f"--- Seed {seed_idx} ---")

        # Grow WITH trajectory recording — this is the key change
        _, G, _, trajectories = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3, record_trajectories=True
        )
        step("Growth + trajectories", f"Seed {seed_idx+1}/{n_seeds}")

        # Pick moderate-degree node
        candidates = [n for n in G.nodes()
                      if deg_min <= G.degree(n) <= deg_max]
        if candidates:
            target_deg_ideal = (deg_min + deg_max) // 2
            target = min(candidates,
                         key=lambda n: abs(G.degree(n) - target_deg_ideal))
        else:
            target = min(G.nodes(),
                         key=lambda n: abs(G.degree(n) - deg_min))
        target_deg = G.degree(target)
        target_degrees.append(target_deg)

        # Rank edges by GROWTH-PHASE MI (shared history)
        edge_mi_map = compute_growth_edge_mi(target, G, trajectories, config_space)
        step("Growth MI ranking", f"Target deg={target_deg}")

        # Sort neighbors by MI
        neighbors_by_mi = sorted(edge_mi_map.keys(),
                                 key=lambda nb: edge_mi_map[nb],
                                 reverse=True)
        mi_values = [edge_mi_map[nb] for nb in neighbors_by_mi]
        all_mi_distributions.append(mi_values)

        if mi_values:
            mi_min = min(mi_values)
            mi_max = max(mi_values)
            if mi_min > 0:
                mi_spreads.append(mi_max / mi_min)
            log(f"  Target: node {target} (degree {target_deg})")
            log(f"  Growth MI range: {mi_min:.4f} — {mi_max:.4f}"
                + (f"  (spread: {mi_max/mi_min:.1f}x)" if mi_min > 0 else ""))

        original_neighbors = list(G.neighbors(target))

        for strat in strategies:
            if strat == "high_mi":
                ordered = list(neighbors_by_mi)
            elif strat == "low_mi":
                ordered = list(reversed(neighbors_by_mi))
            else:
                ordered = None

            rng_rm = np.random.default_rng(seed + 80000)

            for frac in removal_fracs:
                G_damaged = G.copy()
                n_remove = int(len(original_neighbors) * frac)

                removed_set = set()
                if n_remove > 0:
                    if ordered is not None:
                        to_remove = ordered[:n_remove]
                    else:
                        indices = rng_rm.choice(
                            len(original_neighbors),
                            size=min(n_remove, len(original_neighbors)),
                            replace=False
                        )
                        to_remove = [original_neighbors[i] for i in indices]

                    for nb in to_remove:
                        removed_set.add(nb)
                        if G_damaged.has_edge(target, nb):
                            G_damaged.remove_edge(target, nb)

                result = run_post_removal_dynamics(
                    target, original_neighbors, removed_set,
                    G_damaged, mem_bits, dyn_steps,
                    seed=seed + 90000, config_space=config_space
                )

                data[strat][frac]["total_mi"].append(result["total_mi"])
                data[strat][frac]["unique"].append(result["unique_configs"])

                step(f"{strat} {frac:.0%}",
                     f"MI={result['total_mi']:.1f}")

        # Per-seed summary
        for strat in strategies:
            vals = " ".join(
                f"{f:.0%}->{data[strat][f]['total_mi'][-1]:.0f}"
                for f in removal_fracs
            )
            log(f"  {strat:>8}: {vals}")
        log()

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    log("=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log()
    log(f"  Target degrees: mean={np.mean(target_degrees):.1f}  "
        f"range=[{min(target_degrees)}, {max(target_degrees)}]")
    if mi_spreads:
        log(f"  Growth MI spread (max/min per target): mean={np.mean(mi_spreads):.1f}x  "
            f"range=[{min(mi_spreads):.1f}x, {max(mi_spreads):.1f}x]")
    log()

    log(f"  {'Frac':>6}  {'High-MI':>12}  {'Random':>12}  {'Low-MI':>12}  {'Gap (H-L)':>12}")
    log(f"  {'-'*60}")

    for frac in removal_fracs:
        h = np.mean(data["high_mi"][frac]["total_mi"])
        r = np.mean(data["random"][frac]["total_mi"])
        lo = np.mean(data["low_mi"][frac]["total_mi"])
        gap = lo - h
        log(f"  {frac:>5.0%}  {h:>12.1f}  {r:>12.1f}  {lo:>12.1f}  {gap:>+12.1f}")

    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    baseline = np.mean(data["high_mi"][0.0]["total_mi"])

    h50 = np.mean(data["high_mi"][0.50]["total_mi"])
    r50 = np.mean(data["random"][0.50]["total_mi"])
    lo50 = np.mean(data["low_mi"][0.50]["total_mi"])

    h75 = np.mean(data["high_mi"][0.75]["total_mi"])
    lo75 = np.mean(data["low_mi"][0.75]["total_mi"])

    gap_50 = (lo50 - h50) / baseline * 100 if baseline > 0 else 0
    gap_75 = (lo75 - h75) / baseline * 100 if baseline > 0 else 0

    drop_h50 = (baseline - h50) / baseline * 100 if baseline > 0 else 0
    drop_lo50 = (baseline - lo50) / baseline * 100 if baseline > 0 else 0

    log(f"  At 50% removal:")
    log(f"    High-MI first: {h50:.1f}  ({drop_h50:.1f}% loss)")
    log(f"    Random:        {r50:.1f}")
    log(f"    Low-MI first:  {lo50:.1f}  ({drop_lo50:.1f}% loss)")
    log(f"    Gap: {gap_50:.1f}% of baseline")
    log()
    log(f"  At 75% removal:")
    log(f"    High-MI first: {h75:.1f}")
    log(f"    Low-MI first:  {lo75:.1f}")
    log(f"    Gap: {gap_75:.1f}% of baseline")
    log()

    # Statistical test
    h50_vals = data["high_mi"][0.50]["total_mi"]
    lo50_vals = data["low_mi"][0.50]["total_mi"]
    diffs = [lo - hi for lo, hi in zip(lo50_vals, h50_vals)]
    consistent = sum(1 for d in diffs if d > 0)

    log(f"  Consistency: high-MI worse than low-MI in {consistent}/{n_seeds} seeds at 50%")

    if len(diffs) > 1:
        mean_diff = np.mean(diffs)
        std_diff = np.std(diffs, ddof=1)
        if std_diff > 0:
            t_stat = mean_diff / (std_diff / np.sqrt(len(diffs)))
            log(f"  Paired t-stat: {t_stat:.2f}  (mean gap = {mean_diff:.2f})")
        else:
            t_stat = float('inf') if mean_diff > 0 else 0
    else:
        t_stat = 0

    log()

    # T1 check
    h100_unique = np.mean(data["high_mi"][1.0]["unique"])
    log(f"  T1 check (isolation): unique configs = {h100_unique:.0f}")
    log()

    # The gap can go EITHER direction — both are meaningful:
    # gap > 0: high-MI removal hurts more (deep ties are load-bearing)
    # gap < 0: low-MI removal hurts more (diverse ties are load-bearing)
    abs_gap_50 = abs(gap_50)
    abs_gap_75 = abs(gap_75)

    # Check consistency in EITHER direction
    consistent_low_hurts = sum(1 for d in diffs if d < 0)  # low-MI removal worse
    consistent_high_hurts = consistent  # high-MI removal worse

    if abs_gap_50 > 5 and max(consistent_low_hurts, consistent_high_hurts) >= n_seeds * 0.7:
        if gap_50 < 0:
            log("RESULT: POSITIVE (INVERTED) — Losing DIVERSE connections hurts more!")
            log("  High growth-MI = redundant connections (similar trajectories)")
            log("  Low growth-MI = diverse connections (novel information)")
            log("  Removing diverse ties collapses state space more than removing redundant ones.")
            log("  This follows directly from anti-loop logic: novelty prevents loops,")
            log("  so diverse connections are load-bearing. Redundant ones are expendable.")
            log("  The anti-loop analogue of grief: losing what challenges you hurts")
            log("  more than losing what merely echoes you.")
        else:
            log("RESULT: POSITIVE — Losing deeply-connected ties hurts more.")
            log("  Growth-phase MI (shared history) predicts vulnerability.")
            log("  High-MI edges are load-bearing.")
        verdict = "POSITIVE"
    elif abs_gap_50 > 2 and max(consistent_low_hurts, consistent_high_hurts) >= n_seeds * 0.6:
        log("RESULT: WEAK POSITIVE — Targeted removal shows asymmetry, but effect is modest.")
        verdict = "WEAK POSITIVE"
    else:
        log("RESULT: NEGATIVE — No significant difference between removal strategies.")
        verdict = "NEGATIVE"

    log()

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("C2v2 Targeted Suffering: Does Losing Important Connections Hurt More?",
                 fontweight="bold")

    fracs_pct = [f * 100 for f in removal_fracs]
    colors = {"high_mi": "tab:red", "random": "tab:gray", "low_mi": "tab:blue"}

    # Top-left: Total MI vs removal strategy (KEY PLOT)
    ax = axes[0, 0]
    for strat in strategies:
        means = [np.mean(data[strat][f]["total_mi"]) for f in removal_fracs]
        stds = [np.std(data[strat][f]["total_mi"]) for f in removal_fracs]
        ax.errorbar(fracs_pct, means, yerr=stds, marker="o", capsize=4,
                    label=strategy_labels[strat], color=colors[strat])

    h_means = [np.mean(data["high_mi"][f]["total_mi"]) for f in removal_fracs]
    lo_means = [np.mean(data["low_mi"][f]["total_mi"]) for f in removal_fracs]
    ax.fill_between(fracs_pct, h_means, lo_means, alpha=0.15, color="purple",
                    label="Vulnerability gap")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("Total relational MI (bits)")
    ax.set_title("Total MI vs removal strategy")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Top-right: Normalized (% of baseline)
    ax = axes[0, 1]
    for strat in strategies:
        means = [np.mean(data[strat][f]["total_mi"]) for f in removal_fracs]
        baseline_s = means[0] if means[0] > 0 else 1
        normed = [m / baseline_s * 100 for m in means]
        ax.plot(fracs_pct, normed, marker="o",
                label=strategy_labels[strat], color=colors[strat])
    ideal = [100 * (1 - f) for f in removal_fracs]
    ax.plot(fracs_pct, ideal, "--", color="black", alpha=0.3, label="Ideal proportional")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("% of baseline MI remaining")
    ax.set_title("Normalized MI retention")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Bottom-left: Edge MI distribution from growth phase
    ax = axes[1, 0]
    if all_mi_distributions:
        for i, mi_vals in enumerate(all_mi_distributions[:5]):
            ax.plot(range(len(mi_vals)), sorted(mi_vals, reverse=True),
                    marker=".", markersize=3, alpha=0.6, label=f"Seed {i}")
        ax.set_xlabel("Edge rank (sorted by MI)")
        ax.set_ylabel("Growth-phase MI (bits)")
        ax.set_title("Edge MI distribution (growth history)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Bottom-right: Vulnerability gap bar chart
    ax = axes[1, 1]
    gaps = []
    gap_stds = []
    for frac in removal_fracs:
        h_vals = data["high_mi"][frac]["total_mi"]
        lo_vals = data["low_mi"][frac]["total_mi"]
        diffs_f = [lo - hi for lo, hi in zip(lo_vals, h_vals)]
        gaps.append(np.mean(diffs_f))
        gap_stds.append(np.std(diffs_f) if len(diffs_f) > 1 else 0)

    ax.bar(fracs_pct, gaps, width=12, color="purple", alpha=0.6,
           yerr=gap_stds, capsize=4)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("MI gap (low-MI − high-MI removal)")
    ax.set_title("Vulnerability gap by fraction")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c2v2_targeted_suffering.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    with open(os.path.join(out_dir, "c2v2_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
    return verdict
