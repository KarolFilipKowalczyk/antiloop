"""
C1 Hash Robustness: Does the MI result hold across hash functions?
==================================================================

The C1 consciousness band experiment used XOR hash only. XOR is
commutative and self-inverse -- neighbor order doesn't matter and
duplicate configs cancel. This is a strong structural assumption.

This experiment runs C1 with XOR, SUM, and PRODUCT hash functions.
If the MI ratio (edge MI / non-edge MI) is consistent across all
three, the result is robust. If it's XOR-specific, it's an artifact.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.engine import (
    HASH_XOR, HASH_SUM, HASH_PRODUCT,
    run_antiloop, build_growing_random_control,
)
from simulation.experiments.c1_complexity import (
    edge_mi, nonedge_mi, run_dynamics_on_graph,
)

TITLE = "C1 Hash Robustness"

HASH_FUNCTIONS = [
    (HASH_XOR, "XOR"),
    (HASH_SUM, "SUM"),
    (HASH_PRODUCT, "PRODUCT"),
]


def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        out_dir=None, progress=None, **_):
    """Test C1 MI result across XOR, SUM, and PRODUCT hash functions."""
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
    log("C1 HASH ROBUSTNESS: MI across XOR, SUM, PRODUCT")
    log("=" * 70)
    log(f"Question: Is the C1 MI result hash-dependent or hash-independent?")
    log()

    # ----------------------------------------------------------
    # Calibration -- full pipeline for ONE hash function, then x3
    # ----------------------------------------------------------
    log("Calibrating (full pipeline x1 hash)...")
    cal_rng = np.random.default_rng(99999)
    cal_nodes = min(max_nodes, 100)

    t0 = time.time()
    _, G_cal, glog_cal, traj_cal = run_antiloop(
        mem_bits=mem_bits, max_nodes=cal_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, record_trajectories=True
    )
    n_steps_cal = max(len(v) for v in traj_cal.values())
    edge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
    nonedge_mi(G_cal, traj_cal, config_space, rng=cal_rng)
    G_ctrl_cal = build_growing_random_control(glog_cal, seed=99998)
    ctrl_traj_cal = run_dynamics_on_graph(G_ctrl_cal, mem_bits, steps=n_steps_cal, seed=99997)
    edge_mi(G_ctrl_cal, ctrl_traj_cal, config_space, rng=cal_rng)
    nonedge_mi(G_ctrl_cal, ctrl_traj_cal, config_space, rng=cal_rng)
    sec_per_seed_one_hash = time.time() - t0

    # Scale to max_nodes and multiply by 3 hash functions
    scale_factor = (max_nodes / cal_nodes) ** 2.0 if max_nodes > cal_nodes else 1.0
    sec_per_seed = sec_per_seed_one_hash * scale_factor * len(HASH_FUNCTIONS)

    available = time_budget * 0.85
    max_seeds = max(2, int(available / sec_per_seed))
    n_seeds = min(n_seeds, max_seeds)

    log(f"  {sec_per_seed_one_hash:.2f}s @ {cal_nodes} nodes x1 hash -> "
        f"{sec_per_seed:.1f}s estimated @ {max_nodes} nodes x{len(HASH_FUNCTIONS)} hashes")
    log(f"  Budget: {time_budget}s  |  Seeds: {n_seeds}")
    log(f"  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit ({config_space} configs)")
    log()

    # 3 hashes * n_seeds * 2 phases (antiloop MI + control MI) = total work
    total_work = len(HASH_FUNCTIONS) * n_seeds * 2
    work_done = 0

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    # Storage: {hash_name: {"al_edge": [...], "al_nonedge": [...], "ct_edge": [...], ...}}
    results = {}
    for _, hname in HASH_FUNCTIONS:
        results[hname] = {
            "al_edge": [], "al_nonedge": [],
            "ct_edge": [], "ct_nonedge": [],
        }

    for seed_idx in range(n_seeds):
        seed = seed_idx
        log(f"--- Seed {seed_idx} ---")

        for hash_fn, hname in HASH_FUNCTIONS:
            rng = np.random.default_rng(seed + 99999)

            # Anti-loop growth
            t0 = time.time()
            _, G, glog, traj = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=hash_fn, pressure_threshold=0.7,
                spawn_prob=0.3, record_trajectories=True
            )
            n_steps = max(len(v) for v in traj.values())

            al_e, al_e_std, al_e_n = edge_mi(G, traj, config_space, rng=rng)
            al_ne, _, _ = nonedge_mi(G, traj, config_space, rng=rng)
            results[hname]["al_edge"].append(al_e)
            results[hname]["al_nonedge"].append(al_ne)
            step(f"{hname} anti-loop", f"Seed {seed_idx+1}/{n_seeds}")

            # Control
            G_ctrl = build_growing_random_control(glog, seed=seed + 10000)
            ctrl_traj = run_dynamics_on_graph(
                G_ctrl, mem_bits, steps=n_steps, seed=seed + 20000,
                hash_fn=hash_fn
            )
            ct_e, _, _ = edge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
            ct_ne, _, _ = nonedge_mi(G_ctrl, ctrl_traj, config_space, rng=rng)
            results[hname]["ct_edge"].append(ct_e)
            results[hname]["ct_nonedge"].append(ct_ne)
            elapsed = time.time() - t0
            step(f"{hname} control", f"edge={ct_e:.4f}")

            ratio = al_e / al_ne if al_ne > 0 else float('inf')
            log(f"  {hname:>8}: AL edge={al_e:.4f} nonedge={al_ne:.4f} "
                f"ratio={ratio:.3f}x  |  CT edge={ct_e:.4f} nonedge={ct_ne:.4f}  ({elapsed:.1f}s)")

        log()

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    log("=" * 70)
    log("SUMMARY")
    log("=" * 70)
    log()
    log(f"  {'Hash':>10}  {'AL Edge':>9}  {'AL Non-E':>9}  {'Ratio':>7}  "
        f"{'CT Edge':>9}  {'CT Non-E':>9}  {'CT Ratio':>9}  {'AL-CT':>7}")
    log(f"  {'-'*78}")

    hash_ratios = {}
    for _, hname in HASH_FUNCTIONS:
        r = results[hname]
        al_e = np.mean(r["al_edge"])
        al_ne = np.mean(r["al_nonedge"])
        ct_e = np.mean(r["ct_edge"])
        ct_ne = np.mean(r["ct_nonedge"])
        al_ratio = al_e / al_ne if al_ne > 0 else float('inf')
        ct_ratio = ct_e / ct_ne if ct_ne > 0 else float('inf')
        diff_sigma = (al_e - ct_e) / max(np.std(r["al_edge"]), 0.0001)
        hash_ratios[hname] = al_ratio

        log(f"  {hname:>10}  {al_e:>9.4f}  {al_ne:>9.4f}  {al_ratio:>6.3f}x  "
            f"{ct_e:>9.4f}  {ct_ne:>9.4f}  {ct_ratio:>8.3f}x  {diff_sigma:>6.1f}s")

    log()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)
    log()

    all_positive = all(r > 1.05 for r in hash_ratios.values())
    ratios_close = max(hash_ratios.values()) - min(hash_ratios.values()) < 0.1

    for _, hname in HASH_FUNCTIONS:
        r = results[hname]
        al_e_arr = np.array(r["al_edge"])
        ct_e_arr = np.array(r["ct_edge"])
        stronger = al_e_arr.mean() > ct_e_arr.mean()
        diff = (al_e_arr.mean() - ct_e_arr.mean()) / max(al_e_arr.std(), 0.0001)
        log(f"  {hname:>10}: ratio={hash_ratios[hname]:.3f}x  "
            f"AL vs CT: {diff:.1f}s  {'PASS' if stronger and hash_ratios[hname] > 1.05 else 'FAIL'}")

    log()

    if all_positive and ratios_close:
        log("RESULT: ROBUST -- The MI result holds across all hash functions.")
        log(f"  Ratios: {', '.join(f'{h}={hash_ratios[h]:.3f}' for _, h in HASH_FUNCTIONS)}")
        log("  The consciousness band is NOT a hash artifact.")
    elif all_positive:
        log("RESULT: POSITIVE BUT VARIABLE -- All hashes show the effect,")
        log("  but the magnitude varies. The phenomenon is real but hash-sensitive.")
        log(f"  Ratios: {', '.join(f'{h}={hash_ratios[h]:.3f}' for _, h in HASH_FUNCTIONS)}")
    else:
        passing = [h for _, h in HASH_FUNCTIONS if hash_ratios[h] > 1.05]
        failing = [h for _, h in HASH_FUNCTIONS if hash_ratios[h] <= 1.05]
        log(f"RESULT: HASH-DEPENDENT -- Effect present for {', '.join(passing)}")
        log(f"  but NOT for {', '.join(failing)}. The C1 result may be an artifact")
        log(f"  of the {passing[0] if passing else '???'} hash function's properties.")

    log()

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("C1 Hash Robustness: MI ratio across hash functions",
                 fontweight="bold")

    # Left: MI ratio per hash
    ax = axes[0]
    x = range(len(HASH_FUNCTIONS))
    ratios = [hash_ratios[h] for _, h in HASH_FUNCTIONS]
    colors = ["tab:blue", "tab:green", "tab:purple"]
    ax.bar(x, ratios, color=colors, alpha=0.7)
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="No effect (ratio=1)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([h for _, h in HASH_FUNCTIONS])
    ax.set_ylabel("MI ratio (edge / non-edge)")
    ax.set_title("Anti-loop MI ratio by hash function")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    # Right: AL vs CT edge MI per hash
    ax = axes[1]
    width = 0.35
    al_means = [np.mean(results[h]["al_edge"]) for _, h in HASH_FUNCTIONS]
    ct_means = [np.mean(results[h]["ct_edge"]) for _, h in HASH_FUNCTIONS]
    al_stds = [np.std(results[h]["al_edge"]) for _, h in HASH_FUNCTIONS]
    ct_stds = [np.std(results[h]["ct_edge"]) for _, h in HASH_FUNCTIONS]
    x_pos = np.arange(len(HASH_FUNCTIONS))
    ax.bar(x_pos - width/2, al_means, width, yerr=al_stds, capsize=4,
           label="Anti-loop", color="tab:blue", alpha=0.7)
    ax.bar(x_pos + width/2, ct_means, width, yerr=ct_stds, capsize=4,
           label="Control", color="tab:orange", alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([h for _, h in HASH_FUNCTIONS])
    ax.set_ylabel("Edge MI (bits)")
    ax.set_title("Anti-loop vs Control edge MI")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c1_hash_robustness.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    with open(os.path.join(out_dir, "c1_hash_robustness.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
