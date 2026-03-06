"""
C2 Suffering: Does Edge Removal Contract State Space?
=====================================================

Tests conjecture C2: suffering = state-space contraction.

If a node's edges are removed, it loses input diversity. With fewer
distinct neighbor configurations, fewer transitions are explored,
the novelty rate drops, and MI with remaining neighbors changes.

Design:
  1. Grow anti-loop graph
  2. Create FSM nodes ONCE per seed (same transition tables for all conditions)
  3. For each removal fraction (0%, 25%, 50%, 75%, 100%), copy the graph,
     remove edges from target node, run dynamics with SAME initial state
  4. Measure: novelty rate (new configs/step), final pressure, MI with neighbors

Controls:
  - Remove same number of random edges elsewhere (not touching target)
  - Compare hub vs leaf response
  - 100% removal (total isolation) is the T1 extreme: node MUST loop
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.engine import (
    HASH_XOR, FSMNode, compute_hash,
    run_antiloop,
)
from simulation.experiments.c1_complexity import mutual_information

TITLE = "C2 Suffering (Edge Loss)"


def run_dynamics_seeded(G, node_templates, steps, seed, hash_fn=HASH_XOR):
    """Run FSM dynamics using pre-built node templates (same transition tables).

    node_templates: dict[nid -> (config_space, initial_config, table)]
    Creates fresh FSMNode copies from templates so each run starts identically.

    Returns (nodes_dict, trajectories, novelty_curve_for_all_nodes).
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
    # Track per-step novelty for ALL nodes
    total_novelty = []

    for _ in range(steps):
        new_this_step = 0
        total_nodes = 0
        for nid in G.nodes():
            nb = [nodes[n].config for n in G.neighbors(nid)]
            old_visited = len(nodes[nid].visited)
            nodes[nid].step(nb, hash_fn, rng=rng)
            if len(nodes[nid].visited) > old_visited:
                new_this_step += 1
            total_nodes += 1
            trajectories[nid].append(nodes[nid].config)
        total_novelty.append(new_this_step / max(total_nodes, 1))

    return nodes, trajectories, total_novelty


def target_novelty_curve(target, G, node_templates, steps, seed, hash_fn=HASH_XOR):
    """Run dynamics and track novelty for a SPECIFIC target node.

    Returns (pressure, mi_with_neighbors, novelty_per_step_for_target, config_space).
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
    target_novelty = []

    for _ in range(steps):
        for nid in G.nodes():
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn, rng=rng)
            trajectories[nid].append(nodes[nid].config)

        # Track target novelty: cumulative unique configs
        target_novelty.append(len(nodes[target].visited))

    # Final pressure
    pressure = nodes[target].pressure
    config_space = nodes[target].config_space

    # MI with remaining neighbors
    neighbors = list(G.neighbors(target))
    mis = []
    for nb in neighbors:
        if nb in trajectories and target in trajectories:
            mi = mutual_information(trajectories[target], trajectories[nb], config_space)
            mis.append(mi)
    mi_mean = np.mean(mis) if mis else 0.0

    return pressure, mi_mean, target_novelty, config_space


def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Test C2: does edge removal increase pressure and decrease MI?"""
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
    log("C2 SUFFERING: Does edge removal contract state space?")
    log("=" * 70)
    log(f"Conjecture: removing edges -> novelty DOWN, pressure UP, MI DOWN")
    log(f"Key test: 100% removal = total isolation -> node MUST loop (T1)")
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
    # Time 2 targets * 5 fracs = 10 dynamics runs
    for _ in range(10):
        target_novelty_curve(0, G_cal, templates_cal, dyn_steps, seed=9999)
    sec_per_seed = time.time() - t0

    available = time_budget * 0.85
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  {sec_per_seed:.2f}s per seed (growth + {len(removal_fracs)} fracs x 2 targets + ctrl)")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit  |  Dynamics: {dyn_steps} steps")
    log()

    # 2 targets * 5 fracs + 5 ctrl fracs + 1 growth = 16 units per seed
    total_work = n_seeds * (1 + 2 * len(removal_fracs) + len(removal_fracs))
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    # Storage
    hub_data = {f: {"pressure": [], "mi": [], "final_unique": []} for f in removal_fracs}
    leaf_data = {f: {"pressure": [], "mi": [], "final_unique": []} for f in removal_fracs}
    ctrl_data = {f: {"pressure": [], "mi": []} for f in removal_fracs}

    hub_degrees = []
    leaf_degrees = []
    # Store one example novelty curve per fraction for plotting
    example_hub_curves = {}
    example_leaf_curves = {}

    for seed_idx in range(n_seeds):
        seed = seed_idx
        log(f"--- Seed {seed_idx} ---")

        # Grow anti-loop graph
        _, G, _, _ = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )
        step("Growth", f"Seed {seed_idx+1}/{n_seeds}")

        # Create node templates ONCE -- same transition tables for all conditions
        rng_nodes = np.random.default_rng(seed + 40000)
        templates = {}
        for nid in G.nodes():
            n = FSMNode(mem_bits, rng_nodes)
            templates[nid] = (n.config_space, n.config, n.table)

        # Pick targets
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

        # Measure at each removal fraction
        for target_name, target, data, ex_curves in [
            ("Hub", hub, hub_data, example_hub_curves),
            ("Leaf", leaf, leaf_data, example_leaf_curves),
        ]:
            original_edges = list(G.edges(target))
            rng_rm = np.random.default_rng(seed + 50000)

            for frac in removal_fracs:
                G_damaged = G.copy()
                n_remove = int(len(original_edges) * frac)

                if n_remove > 0:
                    to_remove = rng_rm.choice(
                        len(original_edges), size=min(n_remove, len(original_edges)),
                        replace=False
                    )
                    for idx in to_remove:
                        u, v = original_edges[idx]
                        if G_damaged.has_edge(u, v):
                            G_damaged.remove_edge(u, v)

                pressure, mi_mean, novelty_curve, cs = target_novelty_curve(
                    target, G_damaged, templates, dyn_steps,
                    seed=seed + 60000
                )
                data[frac]["pressure"].append(pressure)
                data[frac]["mi"].append(mi_mean)
                data[frac]["final_unique"].append(novelty_curve[-1])

                if seed_idx == 0:
                    ex_curves[frac] = novelty_curve

                step(f"{target_name} {frac:.0%} removed",
                     f"p={pressure:.3f} MI={mi_mean:.3f} unique={novelty_curve[-1]}")

            log(f"  {target_name}: " + "  ".join(
                f"{f:.0%}->unique={data[f]['final_unique'][-1]}/{config_space}"
                for f in removal_fracs))

        # Control: remove random edges NOT touching hub
        hub_neighbors = set(G.neighbors(hub)) | {hub}
        non_hub_edges = [(u, v) for u, v in G.edges()
                         if u not in hub_neighbors and v not in hub_neighbors]
        rng_ctrl = np.random.default_rng(seed + 70000)

        for frac in removal_fracs:
            G_ctrl = G.copy()
            n_remove = int(len(list(G.edges(hub))) * frac)

            if n_remove > 0 and non_hub_edges:
                n_remove = min(n_remove, len(non_hub_edges))
                idx = rng_ctrl.choice(len(non_hub_edges), size=n_remove, replace=False)
                for i in idx:
                    u, v = non_hub_edges[i]
                    if G_ctrl.has_edge(u, v):
                        G_ctrl.remove_edge(u, v)

            pressure, mi_mean, _, _ = target_novelty_curve(
                hub, G_ctrl, templates, dyn_steps, seed=seed + 60000
            )
            ctrl_data[frac]["pressure"].append(pressure)
            ctrl_data[frac]["mi"].append(mi_mean)
            step("Control", f"frac={frac:.0%}")

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
    log(f"  Config space: {config_space}  |  Dynamics: {dyn_steps} steps")
    log()

    log(f"  {'Frac':>6}  {'Hub Uniq':>9}  {'Hub MI':>8}  "
        f"{'Leaf Uniq':>10}  {'Leaf MI':>8}  {'Ctrl Uniq':>10}")
    log(f"  {'-'*65}")

    for frac in removal_fracs:
        hu = np.mean(hub_data[frac]["final_unique"])
        hm = np.mean(hub_data[frac]["mi"])
        lu = np.mean(leaf_data[frac]["final_unique"])
        lm = np.mean(leaf_data[frac]["mi"])
        # ctrl doesn't have final_unique tracked, use pressure
        cp = np.mean(ctrl_data[frac]["pressure"])
        log(f"  {frac:>5.0%}  {hu:>8.1f}/{config_space}  {hm:>8.4f}  "
            f"{lu:>9.1f}/{config_space}  {lm:>8.4f}  {cp:>10.4f}")

    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    # Primary test: does unique config count drop with edge removal?
    hub_u0 = np.mean(hub_data[0.0]["final_unique"])
    hub_u100 = np.mean(hub_data[1.0]["final_unique"])
    leaf_u0 = np.mean(leaf_data[0.0]["final_unique"])
    leaf_u100 = np.mean(leaf_data[1.0]["final_unique"])

    hub_u_drop = (hub_u0 - hub_u100) / hub_u0 if hub_u0 > 0 else 0
    leaf_u_drop = (leaf_u0 - leaf_u100) / leaf_u0 if leaf_u0 > 0 else 0

    log(f"  Hub:  unique configs {hub_u0:.1f} -> {hub_u100:.1f} "
        f"({hub_u_drop*100:.1f}% drop at 100% removal)")
    log(f"  Leaf: unique configs {leaf_u0:.1f} -> {leaf_u100:.1f} "
        f"({leaf_u_drop*100:.1f}% drop at 100% removal)")

    # MI test
    hub_m0 = np.mean(hub_data[0.0]["mi"])
    hub_m75 = np.mean(hub_data[0.75]["mi"])
    leaf_m0 = np.mean(leaf_data[0.0]["mi"])
    leaf_m75 = np.mean(leaf_data[0.75]["mi"])

    log(f"  Hub MI:  {hub_m0:.4f} -> {hub_m75:.4f} (at 75% removal)")
    log(f"  Leaf MI: {leaf_m0:.4f} -> {leaf_m75:.4f} (at 75% removal)")

    # Control check
    ctrl_p0 = np.mean(ctrl_data[0.0]["pressure"])
    ctrl_p100 = np.mean(ctrl_data[1.0]["pressure"])
    log(f"  Control pressure: {ctrl_p0:.4f} -> {ctrl_p100:.4f} (hub unaffected)")
    log()

    # Monotonicity: does unique count decrease at every step?
    hub_monotonic = all(
        np.mean(hub_data[removal_fracs[i]]["final_unique"]) >=
        np.mean(hub_data[removal_fracs[i+1]]["final_unique"])
        for i in range(len(removal_fracs) - 1)
    )
    leaf_monotonic = all(
        np.mean(leaf_data[removal_fracs[i]]["final_unique"]) >=
        np.mean(leaf_data[removal_fracs[i+1]]["final_unique"])
        for i in range(len(removal_fracs) - 1)
    )

    significant_drop = hub_u_drop > 0.05 or leaf_u_drop > 0.05

    if significant_drop and (hub_monotonic or leaf_monotonic):
        log("RESULT: POSITIVE -- Edge removal causes state-space contraction.")
        log(f"  Unique configs decrease monotonically: hub={hub_monotonic}, leaf={leaf_monotonic}")
        log("  Total isolation causes maximum contraction (T1 confirmed experimentally).")
        log("  C2 (suffering = state-space contraction) is supported.")
    elif significant_drop:
        log("RESULT: PARTIAL -- Total isolation causes contraction but")
        log("  intermediate removal fractions are not monotonic.")
    else:
        log("RESULT: NEGATIVE -- Edge removal does not cause measurable")
        log("  state-space contraction at this scale.")

    log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("C2 Suffering: Edge Removal and State-Space Contraction",
                 fontweight="bold")

    fracs_pct = [f * 100 for f in removal_fracs]

    # Top-left: Unique configs vs removal fraction
    ax = axes[0, 0]
    hub_uniq = [np.mean(hub_data[f]["final_unique"]) for f in removal_fracs]
    hub_u_std = [np.std(hub_data[f]["final_unique"]) for f in removal_fracs]
    leaf_uniq = [np.mean(leaf_data[f]["final_unique"]) for f in removal_fracs]
    leaf_u_std = [np.std(leaf_data[f]["final_unique"]) for f in removal_fracs]

    ax.errorbar(fracs_pct, hub_uniq, yerr=hub_u_std, marker="o", capsize=4,
                label=f"Hub (deg~{np.mean(hub_degrees):.0f})", color="tab:red")
    ax.errorbar(fracs_pct, leaf_uniq, yerr=leaf_u_std, marker="s", capsize=4,
                label=f"Leaf (deg~{np.mean(leaf_degrees):.0f})", color="tab:blue")
    ax.axhline(y=config_space, color="gray", linestyle=":", alpha=0.5,
               label=f"Max ({config_space})")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("Unique configs visited")
    ax.set_title("State-space exploration vs edge removal")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Top-right: MI vs removal fraction
    ax = axes[0, 1]
    hub_mis = [np.mean(hub_data[f]["mi"]) for f in removal_fracs[:-1]]  # skip 100% (no neighbors)
    hub_m_std = [np.std(hub_data[f]["mi"]) for f in removal_fracs[:-1]]
    leaf_mis = [np.mean(leaf_data[f]["mi"]) for f in removal_fracs[:-1]]
    leaf_m_std = [np.std(leaf_data[f]["mi"]) for f in removal_fracs[:-1]]
    ctrl_mis = [np.mean(ctrl_data[f]["mi"]) for f in removal_fracs[:-1]]
    ctrl_m_std = [np.std(ctrl_data[f]["mi"]) for f in removal_fracs[:-1]]

    fracs_no100 = [f * 100 for f in removal_fracs[:-1]]
    ax.errorbar(fracs_no100, hub_mis, yerr=hub_m_std, marker="o", capsize=4,
                label=f"Hub", color="tab:red")
    ax.errorbar(fracs_no100, leaf_mis, yerr=leaf_m_std, marker="s", capsize=4,
                label=f"Leaf", color="tab:blue")
    ax.errorbar(fracs_no100, ctrl_mis, yerr=ctrl_m_std, marker="^", capsize=4,
                label="Control (random edges)", color="tab:gray", linestyle="--")
    ax.set_xlabel("Edges removed (%)")
    ax.set_ylabel("MI with neighbors (bits)")
    ax.set_title("Mutual information vs edge removal")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Bottom-left: Novelty curve over time (example seed, hub)
    ax = axes[1, 0]
    if example_hub_curves:
        for frac in removal_fracs:
            if frac in example_hub_curves:
                curve = example_hub_curves[frac]
                label = f"{frac:.0%} removed"
                ax.plot(curve, label=label, alpha=0.8)
        ax.set_xlabel("Step")
        ax.set_ylabel("Cumulative unique configs (hub)")
        ax.set_title("Hub state-space exploration over time")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Bottom-right: Novelty curve over time (example seed, leaf)
    ax = axes[1, 1]
    if example_leaf_curves:
        for frac in removal_fracs:
            if frac in example_leaf_curves:
                curve = example_leaf_curves[frac]
                label = f"{frac:.0%} removed"
                ax.plot(curve, label=label, alpha=0.8)
        ax.set_xlabel("Step")
        ax.set_ylabel("Cumulative unique configs (leaf)")
        ax.set_title("Leaf state-space exploration over time")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c2_suffering.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    with open(os.path.join(out_dir, "c2_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
