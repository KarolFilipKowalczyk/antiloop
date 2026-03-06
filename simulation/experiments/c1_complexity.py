"""
C1 Consciousness Band: Correlations Between Node Trajectories
=============================================================

Tests whether anti-loop graphs produce stronger inter-node correlations
than control graphs. The "consciousness band" isn't in individual
trajectories (those look pseudo-random) — it's in the RELATIONSHIPS.

Determinism means same cause -> same effect. If node A affects node B
via a deterministic transition table, their trajectories are correlated.
Anti-loop edges exist because they were NEEDED (to prevent loops).
Random edges are arbitrary. So anti-loop edges should carry more
mutual information.

Measure: mutual information I(A_t; B_t) between neighboring node
trajectories, averaged over all edges. Compare anti-loop vs control.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.engine import (
    HASH_XOR, FSMNode, compute_hash,
    run_antiloop, build_growing_random_control,
)

TITLE = "C1 Consciousness Band"


# ------------------------------------------------------------------
# Mutual information
# ------------------------------------------------------------------

def mutual_information(traj_a, traj_b, config_space):
    """Mutual information I(A;B) between two trajectories.

    Uses empirical joint and marginal distributions.
    Returns value in bits.
    """
    n = min(len(traj_a), len(traj_b))
    if n < 10:
        return 0.0

    a = np.array(traj_a[:n])
    b = np.array(traj_b[:n])

    # Joint histogram
    joint = np.zeros((config_space, config_space), dtype=np.float64)
    for i in range(n):
        joint[a[i], b[i]] += 1
    joint /= n

    # Marginals
    pa = joint.sum(axis=1)
    pb = joint.sum(axis=0)

    # MI = sum p(a,b) * log2(p(a,b) / (p(a)*p(b)))
    mi = 0.0
    for ai in range(config_space):
        if pa[ai] == 0:
            continue
        for bi in range(config_space):
            if pb[bi] == 0 or joint[ai, bi] == 0:
                continue
            mi += joint[ai, bi] * np.log2(joint[ai, bi] / (pa[ai] * pb[bi]))

    return mi


def edge_mi(G, trajectories, config_space, max_edges=500, rng=None):
    """Average mutual information across edges of G.

    Samples up to max_edges edges for speed.
    Returns (mean_mi, std_mi, n_edges).
    """
    edges = list(G.edges())
    if not edges:
        return 0.0, 0.0, 0

    if len(edges) > max_edges and rng is not None:
        idx = rng.choice(len(edges), size=max_edges, replace=False)
        edges = [edges[i] for i in idx]

    mis = []
    for u, v in edges:
        if u in trajectories and v in trajectories:
            mi = mutual_information(trajectories[u], trajectories[v], config_space)
            mis.append(mi)

    if not mis:
        return 0.0, 0.0, 0
    arr = np.array(mis)
    return arr.mean(), arr.std(), len(arr)


def nonedge_mi(G, trajectories, config_space, n_samples=500, rng=None):
    """Average MI between NON-neighboring nodes (baseline).

    If correlations are topology-specific, non-edges should have lower MI.
    """
    nodes = list(G.nodes())
    if len(nodes) < 2:
        return 0.0, 0.0, 0

    mis = []
    attempts = 0
    while len(mis) < n_samples and attempts < n_samples * 10:
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v and not G.has_edge(u, v):
            if u in trajectories and v in trajectories:
                mi = mutual_information(trajectories[u], trajectories[v], config_space)
                mis.append(mi)
        attempts += 1

    if not mis:
        return 0.0, 0.0, 0
    arr = np.array(mis)
    return arr.mean(), arr.std(), len(arr)


# ------------------------------------------------------------------
# Run FSM dynamics on a fixed graph
# ------------------------------------------------------------------

def run_dynamics_on_graph(G, mem_bits, steps, seed, hash_fn=HASH_XOR,
                          temperature=0.0):
    """Run FSM dynamics on a fixed graph and record trajectories."""
    rng = np.random.default_rng(seed)
    nodes = {}
    for nid in G.nodes():
        nodes[nid] = FSMNode(mem_bits, rng)

    trajectories = {nid: [nodes[nid].config] for nid in G.nodes()}

    for _ in range(steps):
        for nid in G.nodes():
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn, temperature=temperature, rng=rng)
            trajectories[nid].append(nodes[nid].config)

    return trajectories


# ------------------------------------------------------------------
# Main experiment
# ------------------------------------------------------------------

def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Run the C1 consciousness band experiment via inter-node MI."""
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
    log("C1: Consciousness Band — Inter-Node Correlations")
    log("=" * 70)
    log(f"Measure: mutual information I(A_t; B_t) between neighbor trajectories")
    log(f"  Anti-loop edges exist because they were needed (to avoid loops).")
    log(f"  Control edges are random. Anti-loop should carry more MI.")
    log()

    # ----------------------------------------------------------
    # Calibration — time the FULL per-seed pipeline, not just growth
    # ----------------------------------------------------------
    log("Calibrating (full pipeline: growth + control + MI)...")
    cal_rng = np.random.default_rng(99999)
    cal_nodes = min(max_nodes, 100)  # smaller graph for speed

    t0 = time.time()
    # 1. Anti-loop growth with trajectories
    _, G_cal, glog_cal, traj_cal = run_antiloop(
        mem_bits=mem_bits, max_nodes=cal_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, record_trajectories=True
    )
    n_steps_cal = max(len(v) for v in traj_cal.values())
    # 2. MI on anti-loop edges + non-edges
    edge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
    nonedge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
    # 3. Control graph + dynamics + MI
    G_ctrl_cal = build_growing_random_control(glog_cal, seed=99998)
    ctrl_traj_cal = run_dynamics_on_graph(G_ctrl_cal, mem_bits, steps=n_steps_cal, seed=99997)
    edge_mi(G_ctrl_cal, ctrl_traj_cal, config_space, rng=cal_rng)
    nonedge_mi(G_ctrl_cal, ctrl_traj_cal, config_space, rng=cal_rng)
    # 4. Noise dynamics + MI
    noise_traj_cal = run_dynamics_on_graph(G_cal, mem_bits, steps=n_steps_cal, seed=99996, temperature=1.0)
    edge_mi(G_cal, noise_traj_cal, config_space, rng=cal_rng)
    sec_per_seed_cal = time.time() - t0

    # Scale calibration from cal_nodes to max_nodes.
    # MI cost ~ O(edges * config_space^2), edges ~ O(nodes), so roughly linear in nodes.
    # Growth cost ~ O(nodes * steps). Be conservative: scale by (max_nodes/cal_nodes)^1.5
    scale_factor = (max_nodes / cal_nodes) ** 1.5 if max_nodes > cal_nodes else 1.0
    sec_per_seed = sec_per_seed_cal * scale_factor

    available = time_budget * 0.85
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  Calibration: {sec_per_seed_cal:.2f}s @ {cal_nodes} nodes → "
        f"{sec_per_seed:.1f}s estimated @ {max_nodes} nodes")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit ({config_space} configs)")
    log()

    total_work = n_seeds * 4
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    # Storage
    al_edge_mi = []
    al_nonedge_mi = []
    ct_edge_mi = []
    ct_nonedge_mi = []
    noise_edge_mi = []

    for seed_idx in range(n_seeds):
        seed = seed_idx
        rng = np.random.default_rng(seed + 99999)
        log(f"--- Seed {seed_idx} ---")

        # 1. Anti-loop graph with trajectories
        t0 = time.time()
        _, G_final, glog, traj_al = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3, record_trajectories=True
        )
        n_steps = max(len(v) for v in traj_al.values())
        elapsed = time.time() - t0
        step("Anti-loop growth", f"Seed {seed_idx+1}/{n_seeds}")

        # MI on anti-loop edges
        t0 = time.time()
        al_e_mean, al_e_std, al_e_n = edge_mi(G_final, traj_al, config_space, rng=rng)
        al_ne_mean, al_ne_std, al_ne_n = nonedge_mi(G_final, traj_al, config_space, rng=rng)
        al_edge_mi.append(al_e_mean)
        al_nonedge_mi.append(al_ne_mean)
        elapsed_mi = time.time() - t0
        step("Anti-loop MI", f"edge={al_e_mean:.4f} nonedge={al_ne_mean:.4f}")

        log(f"  Anti-loop: edge MI={al_e_mean:.4f}+/-{al_e_std:.4f} ({al_e_n} edges)  "
            f"non-edge MI={al_ne_mean:.4f}  ({elapsed + elapsed_mi:.1f}s)")

        # 2. Control graph with FSM dynamics
        t0 = time.time()
        G_ctrl = build_growing_random_control(glog, seed=seed + 10000)
        ctrl_traj = run_dynamics_on_graph(
            G_ctrl, mem_bits, steps=n_steps, seed=seed + 20000
        )
        ct_e_mean, ct_e_std, ct_e_n = edge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
        ct_ne_mean, ct_ne_std, ct_ne_n = nonedge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
        ct_edge_mi.append(ct_e_mean)
        ct_nonedge_mi.append(ct_ne_mean)
        elapsed = time.time() - t0
        step("Control MI", f"edge={ct_e_mean:.4f} nonedge={ct_ne_mean:.4f}")

        log(f"  Control:   edge MI={ct_e_mean:.4f}+/-{ct_e_std:.4f} ({ct_e_n} edges)  "
            f"non-edge MI={ct_ne_mean:.4f}  ({elapsed:.1f}s)")

        # 3. Noise baseline (T=1 on anti-loop graph)
        t0 = time.time()
        noise_traj = run_dynamics_on_graph(
            G_final, mem_bits, steps=n_steps, seed=seed + 40000,
            temperature=1.0
        )
        ns_e_mean, _, _ = edge_mi(G_final, noise_traj, config_space, rng=rng)
        noise_edge_mi.append(ns_e_mean)
        elapsed = time.time() - t0
        step("Noise MI", f"edge={ns_e_mean:.4f}")

        log(f"  Noise:     edge MI={ns_e_mean:.4f}  ({elapsed:.1f}s)")
        log()

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    log("=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log()

    al_e = np.array(al_edge_mi)
    al_ne = np.array(al_nonedge_mi)
    ct_e = np.array(ct_edge_mi)
    ct_ne = np.array(ct_nonedge_mi)
    ns_e = np.array(noise_edge_mi)

    log(f"  {'':>20}  {'Edge MI':>10}  {'Non-edge MI':>12}  {'Ratio':>8}")
    log(f"  {'-'*56}")
    al_ratio = al_e.mean() / al_ne.mean() if al_ne.mean() > 0 else float('inf')
    ct_ratio = ct_e.mean() / ct_ne.mean() if ct_ne.mean() > 0 else float('inf')
    log(f"  {'Anti-loop':>20}  {al_e.mean():>10.4f}  {al_ne.mean():>12.4f}  {al_ratio:>8.2f}x")
    log(f"  {'Control':>20}  {ct_e.mean():>10.4f}  {ct_ne.mean():>12.4f}  {ct_ratio:>8.2f}x")
    log(f"  {'Noise (T=1)':>20}  {ns_e.mean():>10.4f}  {'---':>12}  {'---':>8}")
    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    # Key tests:
    # 1. Do edges carry more MI than non-edges? (topology matters)
    # 2. Do anti-loop edges carry more MI than control edges?
    # 3. Is noise MI lower than deterministic MI?

    edges_matter = al_e.mean() > al_ne.mean() * 1.1
    al_stronger = al_e.mean() > ct_e.mean()
    noise_lower = ns_e.mean() < al_e.mean()
    al_vs_ct_diff = (al_e.mean() - ct_e.mean()) / max(al_e.std(), 0.0001)

    log(f"  1. Edges vs non-edges (topology carries information):")
    log(f"     Anti-loop: {al_e.mean():.4f} vs {al_ne.mean():.4f}  "
        f"({'YES' if edges_matter else 'NO'} — {al_ratio:.1f}x)")
    log()
    log(f"  2. Anti-loop vs control edges (constraint shapes correlations):")
    log(f"     Anti-loop: {al_e.mean():.4f}  Control: {ct_e.mean():.4f}  "
        f"diff={al_vs_ct_diff:.1f} sigma")
    log(f"     {'ANTI-LOOP STRONGER' if al_stronger else 'CONTROL STRONGER OR EQUAL'}")
    log()
    log(f"  3. Deterministic vs noise (determinism creates correlations):")
    log(f"     Deterministic: {al_e.mean():.4f}  Noise: {ns_e.mean():.4f}  "
        f"({'YES' if noise_lower else 'NO'})")
    log()

    if edges_matter and noise_lower:
        if al_stronger and al_vs_ct_diff > 1.0:
            log("RESULT: POSITIVE — Anti-loop edges carry more mutual information")
            log("  than control edges. The constraint creates structured correlations")
            log("  that are neither trivial (loops) nor absent (noise).")
            log("  This is the consciousness band: deterministic structure > random topology.")
        elif al_stronger:
            log("RESULT: PARTIAL — Anti-loop edges are slightly stronger but not")
            log(f"  significantly so ({al_vs_ct_diff:.1f} sigma). Topology carries")
            log("  information, and determinism creates correlations, but the")
            log("  anti-loop constraint doesn't add much beyond random growth.")
        else:
            log("RESULT: PARTIAL — Topology and determinism matter, but control")
            log("  edges are as strong as anti-loop edges. The correlation structure")
            log("  comes from graph dynamics in general, not the anti-loop constraint.")
    else:
        log("RESULT: NEGATIVE — Cannot confirm the consciousness band via MI.")

    log()

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("C1: Consciousness Band — Inter-Node Mutual Information",
                 fontweight="bold")

    # Left: bar chart of edge MI
    ax = axes[0]
    x = [0, 1, 2]
    means = [al_e.mean(), ct_e.mean(), ns_e.mean()]
    stds = [al_e.std(), ct_e.std(), ns_e.std()]
    colors = ["tab:blue", "tab:orange", "tab:red"]
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=colors, alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(["Anti-loop", "Control", "Noise (T=1)"])
    ax.set_ylabel("Mean Edge MI (bits)")
    ax.set_title("Mutual information per edge")
    ax.grid(True, alpha=0.3, axis="y")

    # Right: edge vs non-edge comparison
    ax = axes[1]
    x = [0, 1]
    width = 0.35
    ax.bar([xi - width/2 for xi in x], [al_e.mean(), ct_e.mean()],
           width, label="Edge MI", color=["tab:blue", "tab:orange"], alpha=0.7)
    ax.bar([xi + width/2 for xi in x], [al_ne.mean(), ct_ne.mean()],
           width, label="Non-edge MI", color=["tab:blue", "tab:orange"], alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(["Anti-loop", "Control"])
    ax.set_ylabel("MI (bits)")
    ax.set_title("Edge vs non-edge MI")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c1_complexity.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    with open(os.path.join(out_dir, "c1_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
