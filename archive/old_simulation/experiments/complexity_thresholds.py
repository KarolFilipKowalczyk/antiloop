"""
Complexity Thresholds: The Universe That Levels Up
===================================================

Unified experiment bridging O7 (Fermi distinguishability), O14 (C1-C3 bridge),
and O15 (C1 temporal evolution).

Core question: do structural properties of anti-loop networks emerge at
discrete thresholds during growth, or gradually?

If the anti-loop constraint produces sharp phase transitions -- moments where
new structural properties "turn on" -- this directly supports the Fermi essay's
claim that the universe "levels up" and couldn't support complex structures
until crossing specific complexity thresholds.

Measures tracked at regular checkpoints during growth:
  1. MI ratio rho = edge_MI / nonedge_MI  (C1 consciousness band)
  2. Power-law fit quality R (C3 scale-free topology)
  3. Degree entropy (structural diversity)
  4. Mean clustering coefficient (module formation)
  5. Edge MI (absolute mutual information per edge)

KEY DESIGN: MI is computed from actual growth-phase trajectories accumulated
during the anti-loop simulation, NOT from short post-hoc dynamics on frozen
snapshots. The consciousness band emerges from causal history, so measuring
it requires the real trajectory data.

Control: growing random graph with matched trajectory, dynamics run for the
same number of steps as the anti-loop growth phase.

Prediction: anti-loop shows step-function-like jumps at critical sizes;
control shows smooth, gradual curves.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from scipy import stats

from simulation.engine import (
    HASH_XOR, FSMNode, GrowthLog,
    init_ring_graph, build_growing_random_control,
)
from simulation.experiments.c1_complexity import (
    mutual_information, edge_mi, nonedge_mi, run_dynamics_on_graph,
)
from simulation.analysis import analyze_powerlaw

TITLE = "Complexity Thresholds"


# ------------------------------------------------------------------
# Anti-loop growth with trajectory recording and checkpoints
# ------------------------------------------------------------------

def run_antiloop_checkpointed(mem_bits, max_nodes, checkpoints, initial_n=10,
                              seed=42, hash_fn=HASH_XOR, pressure_threshold=0.7,
                              spawn_prob=0.3, max_stressed_per_step=5,
                              max_steps=10000):
    """Run anti-loop growth, recording trajectories and snapshotting at checkpoints.

    Args:
        checkpoints: sorted list of node counts at which to snapshot

    Returns:
        snapshots: dict[n_nodes -> (nx.Graph copy, dict of trajectories up to that point)]
        G_final: final graph
        growth_log: GrowthLog for control matching
        trajectories: dict[node_id -> list[config]] (full trajectories)
        total_steps: number of simulation steps run
    """
    rng = np.random.default_rng(seed)
    G, nodes = init_ring_graph(initial_n, mem_bits, rng)

    next_id = initial_n
    growth_log = GrowthLog()
    growth_log.record(0, G.number_of_nodes(), G.number_of_edges())

    # Record trajectories from the start
    trajectories = {}
    for nid in G.nodes():
        trajectories[nid] = [nodes[nid].config]

    snapshots = {}
    # Capture initial size if it's a checkpoint
    if G.number_of_nodes() in set(checkpoints):
        snapshots[G.number_of_nodes()] = (
            G.copy(),
            {nid: list(traj) for nid, traj in trajectories.items()}
        )

    at_cap = False

    for step_num in range(1, max_steps + 1):
        # All nodes step
        node_list = list(G.nodes())
        for nid in node_list:
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn)

        # Record trajectories
        for nid in node_list:
            if nid in trajectories:
                trajectories[nid].append(nodes[nid].config)

        # Find stressed nodes
        stressed = [n for n in node_list if nodes[n].pressure > pressure_threshold]
        if not stressed:
            growth_log.record(step_num, G.number_of_nodes(), G.number_of_edges())
            continue

        acted = rng.choice(stressed,
                           size=min(max_stressed_per_step, len(stressed)),
                           replace=False)

        if G.number_of_nodes() >= max_nodes:
            at_cap = True

        prev_n = G.number_of_nodes()

        for nid in acted:
            current_nb = set(G.neighbors(nid)) | {nid}
            candidates = [n for n in G.nodes() if n not in current_nb]

            if candidates:
                target = rng.choice(candidates)
                G.add_edge(nid, target)

                if not at_cap and rng.random() < spawn_prob:
                    if G.number_of_nodes() < max_nodes:
                        G.add_node(next_id)
                        nodes[next_id] = FSMNode(mem_bits, rng)
                        G.add_edge(nid, next_id)
                        trajectories[next_id] = [nodes[next_id].config]
                        next_id += 1
                        if G.number_of_nodes() >= max_nodes:
                            at_cap = True

            elif not at_cap:
                G.add_node(next_id)
                nodes[next_id] = FSMNode(mem_bits, rng)
                G.add_edge(nid, next_id)
                trajectories[next_id] = [nodes[next_id].config]
                next_id += 1
                if G.number_of_nodes() >= max_nodes:
                    at_cap = True

        growth_log.record(step_num, G.number_of_nodes(), G.number_of_edges())

        # Snapshot at checkpoints (only when we first cross each threshold)
        cur_n = G.number_of_nodes()
        if cur_n > prev_n:
            for cp in checkpoints:
                if cp not in snapshots and cur_n >= cp:
                    # Deep-copy trajectories up to this point
                    traj_snap = {nid: list(traj)
                                 for nid, traj in trajectories.items()}
                    snapshots[cp] = (G.copy(), traj_snap)

        # Stop if at cap and enough edge-only steps
        if at_cap and (step_num - growth_log.steps[0]) > 500:
            break

    return snapshots, G, growth_log, trajectories, step_num


# ------------------------------------------------------------------
# Checkpoint measurements
# ------------------------------------------------------------------

def measure_graph_properties(G, config_space):
    """Measure topology-only properties (no MI). Fast."""
    n_nodes = G.number_of_nodes()
    result = {"n_nodes": n_nodes, "n_edges": G.number_of_edges()}

    # Degree entropy
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    if len(degrees) > 0 and degrees.sum() > 0:
        p = np.bincount(degrees.astype(int))
        p = p[p > 0] / p.sum()
        result["degree_entropy"] = -np.sum(p * np.log2(p))
    else:
        result["degree_entropy"] = 0.0

    # Clustering
    result["clustering"] = nx.average_clustering(G) if n_nodes >= 3 else 0.0

    # Power-law R
    if n_nodes >= 50:
        pl = analyze_powerlaw(G, label="checkpoint")
        if pl["alpha"] is not None and pl["vs_exp"] is not None:
            result["powerlaw_R"] = pl["vs_exp"]["R"]
        else:
            result["powerlaw_R"] = 0.0
    else:
        result["powerlaw_R"] = 0.0

    return result


def measure_mi_from_trajectories(G, trajectories, config_space, rng,
                                 mi_samples=150):
    """Compute MI ratio from pre-recorded trajectories.

    Uses the actual growth-phase trajectories, not post-hoc dynamics.
    Only considers nodes that exist in both G and trajectories, and only
    edges where both endpoints have sufficient trajectory length.
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    if n_nodes < 30 or n_edges < 10:
        return {"mi_ratio": 1.0, "edge_mi": 0.0, "nonedge_mi": 0.0}

    e_mean, _, _ = edge_mi(G, trajectories, config_space,
                           max_edges=mi_samples, rng=rng)
    ne_mean, _, _ = nonedge_mi(G, trajectories, config_space,
                               n_samples=mi_samples, rng=rng)

    if ne_mean > 0:
        ratio = e_mean / ne_mean
    else:
        ratio = 1.0

    return {"mi_ratio": ratio, "edge_mi": e_mean, "nonedge_mi": ne_mean}


# ------------------------------------------------------------------
# Sharpness detection
# ------------------------------------------------------------------

def detect_transitions(values, sizes, window=3):
    """Detect sharp transitions in a metric series.

    Returns list of (size, magnitude) where magnitude = local derivative
    normalized by overall range.
    """
    if len(values) < 2 * window + 1:
        return []

    values = np.array(values, dtype=float)
    overall_range = values.max() - values.min()
    if overall_range < 1e-10:
        return []

    transitions = []
    for i in range(window, len(values) - window):
        before = np.mean(values[i - window:i])
        after = np.mean(values[i:i + window])
        magnitude = abs(after - before) / overall_range
        if magnitude > 0.15:  # >15% of total range in one step
            transitions.append((sizes[i], magnitude))

    return transitions


# ------------------------------------------------------------------
# Main experiment
# ------------------------------------------------------------------

def run(n_seeds=30, max_nodes=500, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Run the complexity thresholds experiment."""
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    config_space = 2 ** mem_bits
    output_lines = []

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    log("=" * 70)
    log("COMPLEXITY THRESHOLDS: The Universe That Levels Up")
    log("=" * 70)
    log("Do structural properties emerge at sharp thresholds or gradually?")
    log("MI measured from actual growth trajectories (not post-hoc dynamics).")
    log("Bridges O7 (Fermi), O14 (C1-C3), O15 (temporal evolution)")
    log()

    # Checkpoint sizes
    n_checkpoints = 12
    cp_min = 30
    cp_step = max(1, (max_nodes - cp_min) // (n_checkpoints - 1))
    checkpoints = list(range(cp_min, max_nodes + 1, cp_step))
    if checkpoints[-1] != max_nodes:
        checkpoints.append(max_nodes)
    log(f"Checkpoints: {checkpoints}")
    log()

    # ----------------------------------------------------------
    # Calibration
    # ----------------------------------------------------------
    log("Calibrating (full pipeline: growth + MI + control)...")
    cal_nodes = min(max_nodes, 150)
    cal_cps = [cp for cp in checkpoints if cp <= cal_nodes]
    if not cal_cps or cal_cps[-1] != cal_nodes:
        cal_cps.append(cal_nodes)

    t0 = time.time()
    cal_rng = np.random.default_rng(99999)

    # Anti-loop with trajectory recording
    snaps, G_cal, glog_cal, traj_cal, cal_steps = run_antiloop_checkpointed(
        mem_bits=mem_bits, max_nodes=cal_nodes, checkpoints=cal_cps,
        seed=999, hash_fn=HASH_XOR
    )
    # Measure at 2 checkpoints
    for cp_size in [cal_cps[0], cal_cps[-1]]:
        if cp_size in snaps:
            G_snap, traj_snap = snaps[cp_size]
            measure_graph_properties(G_snap, config_space)
            measure_mi_from_trajectories(G_snap, traj_snap, config_space,
                                         rng=cal_rng, mi_samples=100)

    # Control: dynamics on final control graph
    G_ctrl_cal = build_growing_random_control(glog_cal, seed=99998)
    ctrl_traj_cal = run_dynamics_on_graph(G_ctrl_cal, mem_bits,
                                          steps=cal_steps, seed=99997)
    measure_graph_properties(G_ctrl_cal, config_space)
    measure_mi_from_trajectories(G_ctrl_cal, ctrl_traj_cal, config_space,
                                 rng=cal_rng, mi_samples=100)

    sec_per_seed_cal = time.time() - t0

    # Scale
    n_cp_ratio = len(checkpoints) / max(len(cal_cps), 1)
    size_ratio = (max_nodes / cal_nodes) ** 1.5 if max_nodes > cal_nodes else 1.0
    sec_per_seed = sec_per_seed_cal * n_cp_ratio * size_ratio

    available = time_budget * 0.80
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  Calibration: {sec_per_seed_cal:.2f}s @ {cal_nodes} nodes, "
        f"{len(cal_cps)} checkpoints")
    log(f"  Estimated: {sec_per_seed:.1f}s/seed @ {max_nodes} nodes, "
        f"{len(checkpoints)} checkpoints")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit ({config_space} configs)")
    log()

    mi_samples = 150

    # ----------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------
    metric_names = ["mi_ratio", "powerlaw_R", "degree_entropy",
                    "clustering", "edge_mi"]
    al_data = {m: [] for m in metric_names}
    ctrl_data = {m: [] for m in metric_names}

    total_work = n_seeds * (len(checkpoints) + 3)  # growth + checkpoints + ctrl
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    for seed_idx in range(n_seeds):
        seed = seed_idx
        rng = np.random.default_rng(seed + 77777)
        log(f"--- Seed {seed_idx} ---")
        t_seed = time.time()

        # Anti-loop growth with trajectory recording
        snapshots, G_final, glog, full_traj, n_steps = run_antiloop_checkpointed(
            mem_bits=mem_bits, max_nodes=max_nodes, checkpoints=checkpoints,
            seed=seed, hash_fn=HASH_XOR
        )
        step("Growth", f"Seed {seed_idx + 1}/{n_seeds}")

        # Measure at each checkpoint using real growth trajectories
        al_seed = {m: [] for m in metric_names}
        for cp in checkpoints:
            if cp in snapshots:
                G_snap, traj_snap = snapshots[cp]
            else:
                G_snap, traj_snap = G_final, full_traj

            # Graph properties (fast)
            gprops = measure_graph_properties(G_snap, config_space)

            # MI from actual growth trajectories
            mi_props = measure_mi_from_trajectories(
                G_snap, traj_snap, config_space, rng=rng,
                mi_samples=mi_samples
            )

            for m in ["powerlaw_R", "degree_entropy", "clustering"]:
                al_seed[m].append(gprops[m])
            al_seed["mi_ratio"].append(mi_props["mi_ratio"])
            al_seed["edge_mi"].append(mi_props["edge_mi"])

            step("Checkpoint", f"Seed {seed_idx + 1}, N={cp}")

        for m in metric_names:
            al_data[m].append(al_seed[m])

        # Control: build matched-growth random graph, run dynamics for
        # same number of steps as anti-loop, then measure at each size
        G_ctrl = build_growing_random_control(glog, seed=seed + 10000)
        ctrl_traj = run_dynamics_on_graph(G_ctrl, mem_bits, steps=n_steps,
                                          seed=seed + 20000)
        step("Control dynamics", f"Seed {seed_idx + 1}/{n_seeds}")

        ctrl_seed = {m: [] for m in metric_names}
        for cp in checkpoints:
            # Subgraph the control to checkpoint size
            if cp < G_ctrl.number_of_nodes():
                ctrl_nodes_list = list(G_ctrl.nodes())[:cp]
                G_sub = G_ctrl.subgraph(ctrl_nodes_list).copy()
                # Filter trajectories to subgraph nodes
                sub_traj = {nid: ctrl_traj[nid] for nid in ctrl_nodes_list
                            if nid in ctrl_traj}
            else:
                G_sub = G_ctrl
                sub_traj = ctrl_traj

            gprops = measure_graph_properties(G_sub, config_space)
            mi_props = measure_mi_from_trajectories(
                G_sub, sub_traj, config_space, rng=rng,
                mi_samples=mi_samples
            )

            for m in ["powerlaw_R", "degree_entropy", "clustering"]:
                ctrl_seed[m].append(gprops[m])
            ctrl_seed["mi_ratio"].append(mi_props["mi_ratio"])
            ctrl_seed["edge_mi"].append(mi_props["edge_mi"])

        for m in metric_names:
            ctrl_data[m].append(ctrl_seed[m])

        elapsed = time.time() - t_seed
        log(f"  Final MI ratio: {al_seed['mi_ratio'][-1]:.3f} "
            f"(ctrl: {ctrl_seed['mi_ratio'][-1]:.3f})  [{elapsed:.1f}s]")

    # ----------------------------------------------------------
    # Analysis
    # ----------------------------------------------------------
    log()
    log("=" * 70)
    log("ANALYSIS")
    log("=" * 70)
    log()

    al_arr = {m: np.array(al_data[m]) for m in metric_names}
    ctrl_arr = {m: np.array(ctrl_data[m]) for m in metric_names}
    cp_arr = np.array(checkpoints)

    al_mean = {m: al_arr[m].mean(axis=0) for m in metric_names}
    al_std = {m: al_arr[m].std(axis=0) for m in metric_names}
    ctrl_mean = {m: ctrl_arr[m].mean(axis=0) for m in metric_names}
    ctrl_std = {m: ctrl_arr[m].std(axis=0) for m in metric_names}

    for m in metric_names:
        log(f"  {m}:")
        log(f"    Anti-loop: {al_mean[m][0]:.3f} -> {al_mean[m][-1]:.3f}")
        log(f"    Control:   {ctrl_mean[m][0]:.3f} -> {ctrl_mean[m][-1]:.3f}")

        transitions = detect_transitions(al_mean[m], checkpoints)
        if transitions:
            log(f"    Sharp transitions (anti-loop): "
                f"{[(s, f'{mag:.0%}') for s, mag in transitions]}")
        else:
            log(f"    No sharp transitions detected (anti-loop)")

        ctrl_transitions = detect_transitions(ctrl_mean[m], checkpoints)
        if ctrl_transitions:
            log(f"    Sharp transitions (control): "
                f"{[(s, f'{mag:.0%}') for s, mag in ctrl_transitions]}")
        else:
            log(f"    No sharp transitions detected (control)")
        log()

    # Sharpness comparison
    al_total_transitions = 0
    ctrl_total_transitions = 0
    for m in metric_names:
        al_total_transitions += len(detect_transitions(al_mean[m], checkpoints))
        ctrl_total_transitions += len(detect_transitions(ctrl_mean[m], checkpoints))

    log(f"  Total sharp transitions across all metrics:")
    log(f"    Anti-loop: {al_total_transitions}")
    log(f"    Control:   {ctrl_total_transitions}")
    log()

    # MI ratio divergence
    mi_divergence_size = None
    for i, cp in enumerate(checkpoints):
        if al_mean["mi_ratio"][i] > 1.05:
            mi_divergence_size = cp
            break

    if mi_divergence_size:
        log(f"  MI ratio first exceeds 1.05 at N = {mi_divergence_size}")
    else:
        log(f"  MI ratio never exceeds 1.05 (no consciousness band emergence)")

    # Scale-free emergence
    sf_emergence_size = None
    for i, cp in enumerate(checkpoints):
        if al_mean["powerlaw_R"][i] > 0:
            sf_emergence_size = cp
            break

    if sf_emergence_size:
        log(f"  Power-law preferred (R > 0) first at N = {sf_emergence_size}")
    else:
        log(f"  Power-law never preferred over exponential")
    log()

    # Final checkpoint t-test
    al_final = al_arr["mi_ratio"][:, -1]
    ctrl_final = ctrl_arr["mi_ratio"][:, -1]
    t_stat, p_val = stats.ttest_rel(al_final, ctrl_final)
    consistent = np.sum(al_final > ctrl_final)

    log(f"  Final MI ratio: anti-loop={al_final.mean():.3f}+/-{al_final.std():.3f}"
        f"  control={ctrl_final.mean():.3f}+/-{ctrl_final.std():.3f}")
    log(f"  Paired t={t_stat:.2f}, p={p_val:.4f}, "
        f"consistent={consistent}/{n_seeds}")

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log()
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    has_mi_emergence = mi_divergence_size is not None
    has_sf_emergence = sf_emergence_size is not None
    al_sharper = al_total_transitions > ctrl_total_transitions
    mi_significant = p_val < 0.05 and t_stat > 0

    if has_mi_emergence and has_sf_emergence and al_sharper:
        log("RESULT: POSITIVE -- Complexity thresholds confirmed.")
        log(f"  The consciousness band (MI ratio > 1.05) emerges at "
            f"N ~ {mi_divergence_size}.")
        if sf_emergence_size:
            log(f"  Scale-free topology (R > 0) emerges at "
                f"N ~ {sf_emergence_size}.")
        log(f"  Anti-loop shows {al_total_transitions} sharp transitions "
            f"vs {ctrl_total_transitions} in control.")
        log("  Structural properties turn on at discrete thresholds,")
        log("  directly supporting the 'universe that levels up' hypothesis.")
    elif has_mi_emergence or has_sf_emergence:
        log("RESULT: PARTIAL -- Some thresholds detected but not all metrics.")
        if has_mi_emergence:
            log(f"  MI ratio emergence at N ~ {mi_divergence_size}.")
        if has_sf_emergence:
            log(f"  Scale-free emergence at N ~ {sf_emergence_size}.")
        if not al_sharper:
            log("  Control shows similar or more transitions -- thresholds may")
            log("  not be specific to anti-loop constraint.")
    else:
        log("RESULT: NEGATIVE -- No clear complexity thresholds found.")
        log("  Properties either emerge gradually or don't emerge at all.")
        log("  The 'universe that levels up' claim lacks simulation support.")

    if mi_significant:
        log(f"  C1 temporal confirmation: MI ratio grows during development")
        log(f"  (O15 positive, paired t={t_stat:.2f})")
    log()

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Complexity Thresholds: The Universe That Levels Up",
                 fontweight="bold", fontsize=14)

    plot_configs = [
        ("mi_ratio", "MI Ratio (C1)", "rho = edge MI / non-edge MI"),
        ("powerlaw_R", "Power-Law R (C3)", "R > 0 = scale-free preferred"),
        ("degree_entropy", "Degree Entropy", "H(degree distribution) in bits"),
        ("clustering", "Clustering Coefficient", "Mean local clustering"),
        ("edge_mi", "Edge MI", "Mean mutual information per edge (bits)"),
    ]

    for idx, (metric, title, ylabel) in enumerate(plot_configs):
        ax = axes[idx // 3][idx % 3]

        ax.plot(cp_arr, al_mean[metric], "b-o", markersize=4,
                label="Anti-loop", linewidth=2)
        ax.fill_between(cp_arr,
                         al_mean[metric] - al_std[metric],
                         al_mean[metric] + al_std[metric],
                         alpha=0.15, color="blue")

        ax.plot(cp_arr, ctrl_mean[metric], "r--s", markersize=4,
                label="Control", linewidth=1.5)
        ax.fill_between(cp_arr,
                         ctrl_mean[metric] - ctrl_std[metric],
                         ctrl_mean[metric] + ctrl_std[metric],
                         alpha=0.15, color="red")

        transitions = detect_transitions(al_mean[metric], checkpoints)
        for size, mag in transitions:
            ax.axvline(x=size, color="blue", alpha=0.3, linestyle=":")

        ax.set_xlabel("Network Size (nodes)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Bottom-right: threshold map
    ax = axes[1][2]
    ax.set_xlim(0, max_nodes * 1.1)
    ax.set_ylim(-0.5, len(metric_names) - 0.5)
    ax.set_yticks(range(len(metric_names)))
    ax.set_yticklabels([pc[1] for pc in plot_configs])
    ax.set_xlabel("Network Size (nodes)")
    ax.set_title("Threshold Map")

    for i, (metric, title, _) in enumerate(plot_configs):
        transitions = detect_transitions(al_mean[metric], checkpoints)
        for size, mag in transitions:
            ax.plot(size, i, "b^", markersize=8 + mag * 20, alpha=0.7)
        ctrl_trans = detect_transitions(ctrl_mean[metric], checkpoints)
        for size, mag in ctrl_trans:
            ax.plot(size, i, "rv", markersize=6 + mag * 15, alpha=0.5)

    ax.plot([], [], "b^", markersize=10, label="Anti-loop transition")
    ax.plot([], [], "rv", markersize=8, label="Control transition")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "complexity_thresholds.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------
    with open(os.path.join(out_dir, "complexity_thresholds_results.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    np.savez(os.path.join(out_dir, "complexity_thresholds_data.npz"),
             checkpoints=cp_arr,
             **{f"al_{m}": al_arr[m] for m in metric_names},
             **{f"ctrl_{m}": ctrl_arr[m] for m in metric_names})

    log(f"Results saved to {out_dir}/")
