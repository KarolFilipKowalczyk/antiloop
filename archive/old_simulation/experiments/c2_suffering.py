"""
C2 Suffering: Does Edge Removal Contract Relational State Space?
================================================================

Tests conjecture C2: suffering = state-space contraction.

Key insight from C1: consciousness is RELATIONAL, not individual.
Therefore suffering should be measured relationally: total MI across
all original neighbors, not unique configs visited by one node.

Design:
  1. Grow anti-loop graph
  2. Create FSM nodes ONCE per seed (same transition tables for all conditions)
  3. For each removal fraction (0%, 25%, 50%, 75%, 100%), copy the graph,
     remove edges from target node, run dynamics with SAME initial state
  4. Measure:
     - Total relational MI = sum of MI(target, neighbor_i) over ALL original neighbors
     - Per-remaining-edge MI = avg MI with still-connected neighbors
     - Per-removed-edge MI = avg MI with disconnected former neighbors
     - Unique configs visited (secondary, T1 confirmation)

Prediction: total MI drops proportionally with edge removal (gradual).
Per-remaining-edge MI stays flat (resilience). Per-removed-edge MI drops
(direct connection matters). Unique configs are threshold (T1).
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

TITLE = "C2 Suffering (Edge Loss)"


def run_dynamics_and_measure(target, original_neighbors, removed_set,
                             G, node_templates, steps, seed,
                             config_space, hash_fn=HASH_XOR):
    """Run dynamics and measure relational MI for target node.

    Returns dict with:
      total_mi: sum of MI(target, nb) over ALL original neighbors
      remaining_mi: avg MI with still-connected neighbors
      removed_mi: avg MI with disconnected former neighbors
      unique_configs: how many unique configs target visited
      novelty_curve: cumulative unique configs over time
    """
    rng = np.random.default_rng(seed)
    nodes = {}
    for nid in G.nodes():
        if nid in node_templates:
            cs, cfg, tbl = node_templates[nid]
            node = FSMNode.__new__(FSMNode)
            node.config_space = cs
            node.config = cfg
            node.visited = {cfg}
            node.table = tbl.copy()
            nodes[nid] = node
        else:
            nodes[nid] = FSMNode(8, rng)

    trajectories = {nid: [nodes[nid].config] for nid in G.nodes()}
    novelty_curve = []

    for _ in range(steps):
        for nid in G.nodes():
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn, rng=rng)
            trajectories[nid].append(nodes[nid].config)
        novelty_curve.append(len(nodes[target].visited))

    # Compute MI with each original neighbor
    remaining_mis = []
    removed_mis = []
    total_mi = 0.0

    for nb in original_neighbors:
        if nb in trajectories and target in trajectories:
            mi = mutual_information(trajectories[target], trajectories[nb], config_space)
            total_mi += mi
            if nb in removed_set:
                removed_mis.append(mi)
            else:
                remaining_mis.append(mi)

    return {
        "total_mi": total_mi,
        "remaining_mi": np.mean(remaining_mis) if remaining_mis else 0.0,
        "removed_mi": np.mean(removed_mis) if removed_mis else 0.0,
        "n_remaining": len(remaining_mis),
        "n_removed": len(removed_mis),
        "unique_configs": novelty_curve[-1] if novelty_curve else 0,
        "novelty_curve": novelty_curve,
        "pressure": nodes[target].pressure,
    }


def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Test C2: does edge removal reduce total relational MI?"""
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    config_space = 2 ** mem_bits
    dyn_steps = 500
    removal_fracs = [0.0, 0.25, 0.50, 0.75, 1.0]
    output_lines = []

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    log("=" * 70)
    log("C2 SUFFERING: Does edge removal contract RELATIONAL state space?")
    log("=" * 70)
    log("Primary measure: total MI = sum of MI(target, each original neighbor)")
    log("Prediction: total MI drops proportionally, per-edge MI stays flat")
    log()

    # ----------------------------------------------------------
    # Calibration
    # ----------------------------------------------------------
    log("Calibrating...")
    t0 = time.time()
    _, G_cal, _, _ = run_antiloop(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3
    )
    rng_cal = np.random.default_rng(9999)
    templates_cal = {}
    for nid in G_cal.nodes():
        n = FSMNode(mem_bits, rng_cal)
        templates_cal[nid] = (n.config_space, n.config, n.table)
    hub_cal = max(G_cal.nodes(), key=lambda n: G_cal.degree(n))
    orig_nb_cal = list(G_cal.neighbors(hub_cal))
    # Time: growth + 2 targets * 5 fracs = 11 dynamics runs
    for _ in range(11):
        run_dynamics_and_measure(hub_cal, orig_nb_cal, set(), G_cal,
                                templates_cal, dyn_steps, seed=9999,
                                config_space=config_space)
    sec_per_seed = time.time() - t0

    available = time_budget * 0.85
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  {sec_per_seed:.2f}s per seed")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit  |  Dynamics: {dyn_steps} steps")
    log()

    total_work = n_seeds * (1 + 2 * len(removal_fracs))
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    # Storage per removal fraction
    hub_data = {f: {"total_mi": [], "remaining_mi": [], "removed_mi": [],
                     "unique": [], "pressure": []} for f in removal_fracs}
    leaf_data = {f: {"total_mi": [], "remaining_mi": [], "removed_mi": [],
                      "unique": [], "pressure": []} for f in removal_fracs}

    hub_degrees = []
    leaf_degrees = []
    example_hub_curves = {}
    example_leaf_curves = {}

    for seed_idx in range(n_seeds):
        seed = seed_idx
        log(f"--- Seed {seed_idx} ---")

        _, G, _, _ = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )
        step("Growth", f"Seed {seed_idx+1}/{n_seeds}")

        rng_nodes = np.random.default_rng(seed + 40000)
        templates = {}
        for nid in G.nodes():
            n = FSMNode(mem_bits, rng_nodes)
            templates[nid] = (n.config_space, n.config, n.table)

        degrees = dict(G.degree())
        sorted_nodes = sorted(degrees.keys(), key=lambda n: degrees[n])
        leaf = None
        for n in sorted_nodes:
            if degrees[n] >= 4:
                leaf = n
                break
        hub = sorted_nodes[-1]
        if leaf is None:
            leaf = sorted_nodes[len(sorted_nodes) // 4]

        hub_degrees.append(degrees[hub])
        leaf_degrees.append(degrees[leaf])
        log(f"  Hub: node {hub} (degree {degrees[hub]})")
        log(f"  Leaf: node {leaf} (degree {degrees[leaf]})")

        for target_name, target, data, ex_curves in [
            ("Hub", hub, hub_data, example_hub_curves),
            ("Leaf", leaf, leaf_data, example_leaf_curves),
        ]:
            original_edges = list(G.edges(target))
            original_neighbors = [v if u == target else u for u, v in original_edges]
            rng_rm = np.random.default_rng(seed + 50000)

            for frac in removal_fracs:
                G_damaged = G.copy()
                n_remove = int(len(original_edges) * frac)

                removed_neighbors = set()
                if n_remove > 0:
                    to_remove = rng_rm.choice(
                        len(original_edges), size=min(n_remove, len(original_edges)),
                        replace=False
                    )
                    for idx in to_remove:
                        u, v = original_edges[idx]
                        nb = v if u == target else u
                        removed_neighbors.add(nb)
                        if G_damaged.has_edge(u, v):
                            G_damaged.remove_edge(u, v)

                result = run_dynamics_and_measure(
                    target, original_neighbors, removed_neighbors,
                    G_damaged, templates, dyn_steps,
                    seed=seed + 60000, config_space=config_space
                )

                data[frac]["total_mi"].append(result["total_mi"])
                data[frac]["remaining_mi"].append(result["remaining_mi"])
                data[frac]["removed_mi"].append(result["removed_mi"])
                data[frac]["unique"].append(result["unique_configs"])
                data[frac]["pressure"].append(result["pressure"])

                if seed_idx == 0:
                    ex_curves[frac] = result["novelty_curve"]

                step(f"{target_name} {frac:.0%} removed",
                     f"total_MI={result['total_mi']:.1f}")

            # Log summary for this target
            mi0 = data[0.0]["total_mi"][-1]
            log(f"  {target_name}: " + "  ".join(
                f"{f:.0%}->{data[f]['total_mi'][-1]:.0f}"
                for f in removal_fracs) + f"  (baseline={mi0:.0f})")

        log()

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    log("=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log()
    log(f"  Hub degrees: mean={np.mean(hub_degrees):.1f}  "
        f"range=[{min(hub_degrees)}, {max(hub_degrees)}]")
    log(f"  Leaf degrees: mean={np.mean(leaf_degrees):.1f}  "
        f"range=[{min(leaf_degrees)}, {max(leaf_degrees)}]")
    log()

    log(f"  {'Frac':>6}  {'Hub TotalMI':>12}  {'Hub PerEdge':>12}  {'Hub Removed':>12}  "
        f"{'Leaf TotalMI':>13}  {'Leaf PerEdge':>13}")
    log(f"  {'-'*80}")

    for frac in removal_fracs:
        ht = np.mean(hub_data[frac]["total_mi"])
        hr = np.mean(hub_data[frac]["remaining_mi"])
        hx = np.mean(hub_data[frac]["removed_mi"])
        lt = np.mean(leaf_data[frac]["total_mi"])
        lr = np.mean(leaf_data[frac]["remaining_mi"])
        log(f"  {frac:>5.0%}  {ht:>12.1f}  {hr:>12.4f}  {hx:>12.4f}  "
            f"{lt:>13.1f}  {lr:>13.4f}")

    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    # Total MI drop
    hub_t0 = np.mean(hub_data[0.0]["total_mi"])
    hub_t75 = np.mean(hub_data[0.75]["total_mi"])
    hub_t100 = np.mean(hub_data[1.0]["total_mi"])
    leaf_t0 = np.mean(leaf_data[0.0]["total_mi"])
    leaf_t75 = np.mean(leaf_data[0.75]["total_mi"])
    leaf_t100 = np.mean(leaf_data[1.0]["total_mi"])

    hub_drop_75 = (hub_t0 - hub_t75) / hub_t0 * 100 if hub_t0 > 0 else 0
    hub_drop_100 = (hub_t0 - hub_t100) / hub_t0 * 100 if hub_t0 > 0 else 0
    leaf_drop_75 = (leaf_t0 - leaf_t75) / leaf_t0 * 100 if leaf_t0 > 0 else 0
    leaf_drop_100 = (leaf_t0 - leaf_t100) / leaf_t0 * 100 if leaf_t0 > 0 else 0

    log("  TOTAL RELATIONAL MI (primary measure):")
    log(f"    Hub:  {hub_t0:.1f} -> {hub_t75:.1f} -> {hub_t100:.1f}  "
        f"({hub_drop_75:.1f}% at 75%, {hub_drop_100:.1f}% at 100%)")
    log(f"    Leaf: {leaf_t0:.1f} -> {leaf_t75:.1f} -> {leaf_t100:.1f}  "
        f"({leaf_drop_75:.1f}% at 75%, {leaf_drop_100:.1f}% at 100%)")
    log()

    # Per-edge MI (remaining)
    hub_r0 = np.mean(hub_data[0.0]["remaining_mi"])
    hub_r75 = np.mean(hub_data[0.75]["remaining_mi"])
    leaf_r0 = np.mean(leaf_data[0.0]["remaining_mi"])
    leaf_r75 = np.mean(leaf_data[0.75]["remaining_mi"])

    log("  PER-REMAINING-EDGE MI (resilience check):")
    log(f"    Hub:  {hub_r0:.4f} -> {hub_r75:.4f}  "
        f"({'stable' if abs(hub_r0 - hub_r75) < 0.1 else 'changed'})")
    log(f"    Leaf: {leaf_r0:.4f} -> {leaf_r75:.4f}  "
        f"({'stable' if abs(leaf_r0 - leaf_r75) < 0.1 else 'changed'})")
    log()

    # Per-removed-edge MI
    hub_x25 = np.mean(hub_data[0.25]["removed_mi"])
    hub_x75 = np.mean(hub_data[0.75]["removed_mi"])
    leaf_x25 = np.mean(leaf_data[0.25]["removed_mi"])
    leaf_x75 = np.mean(leaf_data[0.75]["removed_mi"])

    log("  PER-REMOVED-EDGE MI (does cutting an edge reduce correlation?):")
    log(f"    Hub intact edge MI:  {hub_r0:.4f}")
    log(f"    Hub removed edge MI: {hub_x75:.4f}  "
        f"(drop={hub_r0 - hub_x75:.4f})")
    log(f"    Leaf intact edge MI:  {leaf_r0:.4f}")
    log(f"    Leaf removed edge MI: {leaf_x75:.4f}  "
        f"(drop={leaf_r0 - leaf_x75:.4f})")
    log()

    # Monotonicity of total MI
    hub_monotonic = all(
        np.mean(hub_data[removal_fracs[i]]["total_mi"]) >=
        np.mean(hub_data[removal_fracs[i+1]]["total_mi"])
        for i in range(len(removal_fracs) - 1)
    )
    leaf_monotonic = all(
        np.mean(leaf_data[removal_fracs[i]]["total_mi"]) >=
        np.mean(leaf_data[removal_fracs[i+1]]["total_mi"])
        for i in range(len(removal_fracs) - 1)
    )

    gradual = hub_drop_75 > 20 and leaf_drop_75 > 20
    removed_drops = hub_x75 < hub_r0 - 0.05

    if gradual and hub_monotonic and leaf_monotonic:
        log("RESULT: POSITIVE -- Edge removal causes GRADUAL relational contraction.")
        log(f"  Total MI drops monotonically: hub={hub_monotonic}, leaf={leaf_monotonic}")
        log(f"  75% removal -> {hub_drop_75:.0f}% hub MI loss, {leaf_drop_75:.0f}% leaf MI loss")
        if removed_drops:
            log("  Removed edges show lower MI than intact edges (direct correlation matters).")
        log("  C2 (suffering = relational state-space contraction) is SUPPORTED.")
    elif gradual:
        log("RESULT: MOSTLY POSITIVE -- Total MI drops substantially but not perfectly monotonic.")
        log(f"  75% removal -> {hub_drop_75:.0f}% hub MI loss, {leaf_drop_75:.0f}% leaf MI loss")
    else:
        log("RESULT: NEGATIVE -- Edge removal does not cause gradual relational contraction.")

    log()

    # Secondary: unique configs (T1 confirmation)
    hub_u0 = np.mean(hub_data[0.0]["unique"])
    hub_u100 = np.mean(hub_data[1.0]["unique"])
    log(f"  T1 confirmation: hub unique configs {hub_u0:.0f} -> {hub_u100:.0f} at isolation "
        f"({(hub_u0 - hub_u100)/hub_u0*100:.0f}% drop)")
    log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("C2 Suffering: Edge Removal and Relational State-Space Contraction",
                 fontweight="bold")

    fracs_pct = [f * 100 for f in removal_fracs]

    # Top-left: TOTAL MI vs removal fraction (THE KEY PLOT)
    ax = axes[0, 0]
    hub_totals = [np.mean(hub_data[f]["total_mi"]) for f in removal_fracs]
    hub_t_std = [np.std(hub_data[f]["total_mi"]) for f in removal_fracs]
    leaf_totals = [np.mean(leaf_data[f]["total_mi"]) for f in removal_fracs]
    leaf_t_std = [np.std(leaf_data[f]["total_mi"]) for f in removal_fracs]

    # Ideal proportional line
    hub_ideal = [hub_totals[0] * (1 - f) for f in removal_fracs]
    leaf_ideal = [leaf_totals[0] * (1 - f) for f in removal_fracs]

    ax.errorbar(fracs_pct, hub_totals, yerr=hub_t_std, marker="o", capsize=4,
                label=f"Hub (deg~{np.mean(hub_degrees):.0f})", color="tab:red")
    ax.errorbar(fracs_pct, leaf_totals, yerr=leaf_t_std, marker="s", capsize=4,
                label=f"Leaf (deg~{np.mean(leaf_degrees):.0f})", color="tab:blue")
    ax.plot(fracs_pct, hub_ideal, "--", color="tab:red", alpha=0.3, label="Hub ideal (proportional)")
    ax.plot(fracs_pct, leaf_ideal, "--", color="tab:blue", alpha=0.3, label="Leaf ideal (proportional)")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("Total relational MI (bits)")
    ax.set_title("Total MI vs edge removal (KEY MEASURE)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Top-right: Per-edge MI (remaining vs removed)
    ax = axes[0, 1]
    fracs_mid = [f * 100 for f in removal_fracs[1:-1]]  # 25%, 50%, 75%
    hub_remaining = [np.mean(hub_data[f]["remaining_mi"]) for f in removal_fracs[:-1]]
    hub_removed = [np.mean(hub_data[f]["removed_mi"]) for f in removal_fracs[1:-1]]
    leaf_remaining = [np.mean(leaf_data[f]["remaining_mi"]) for f in removal_fracs[:-1]]
    leaf_removed = [np.mean(leaf_data[f]["removed_mi"]) for f in removal_fracs[1:-1]]

    fracs_no100 = [f * 100 for f in removal_fracs[:-1]]
    ax.plot(fracs_no100, hub_remaining, "o-", color="tab:red", label="Hub remaining edges")
    ax.plot(fracs_mid, hub_removed, "x--", color="tab:red", alpha=0.6, label="Hub removed edges")
    ax.plot(fracs_no100, leaf_remaining, "s-", color="tab:blue", label="Leaf remaining edges")
    ax.plot(fracs_mid, leaf_removed, "x--", color="tab:blue", alpha=0.6, label="Leaf removed edges")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("Per-edge MI (bits)")
    ax.set_title("Remaining vs removed edge MI")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Bottom-left: Novelty curve (hub)
    ax = axes[1, 0]
    if example_hub_curves:
        for frac in removal_fracs:
            if frac in example_hub_curves:
                ax.plot(example_hub_curves[frac], label=f"{frac:.0%} removed", alpha=0.8)
        ax.set_xlabel("Step")
        ax.set_ylabel("Cumulative unique configs (hub)")
        ax.set_title("Hub state-space exploration (T1 check)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Bottom-right: Novelty curve (leaf)
    ax = axes[1, 1]
    if example_leaf_curves:
        for frac in removal_fracs:
            if frac in example_leaf_curves:
                ax.plot(example_leaf_curves[frac], label=f"{frac:.0%} removed", alpha=0.8)
        ax.set_xlabel("Step")
        ax.set_ylabel("Cumulative unique configs (leaf)")
        ax.set_title("Leaf state-space exploration (T1 check)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c2_suffering.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    with open(os.path.join(out_dir, "c2_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
