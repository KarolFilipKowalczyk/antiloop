"""Universality test: does alpha ~ 2.0 depend on the specific hash function?

Addresses the critique: "If alpha only works for polynomial hashing, you have
a simulation, not a result."

Tests three hierarchical encodings that all give D_eff = C^k:
  1. Polynomial: h = (h * C + input_i) % D_eff
  2. FNV-like:   h = ((h XOR input_i) * 16777619) % D_eff
  3. Additive:   h = (h + input_i * (i+1)) % D_eff  (position-weighted)

Plus flat (XOR) as control.

For each encoding: grow network to max_nodes, run CSN goodness-of-fit,
plot log-log degree distribution with fitted power law.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from simulation.shared.engine import SpawnModel
from simulation.shared.analysis import (
    analyze_powerlaw, format_powerlaw_result, get_ccdf,
)

TITLE = "Universality of alpha ~ 2.0 Across Encodings"


def _run_model(mem_bits, max_nodes, seed, time_limit, encoding, hash_type):
    """Run spawn model with a specific encoding and hash type."""
    model = SpawnModel(mem_bits, max_nodes, seed, encoding=encoding)
    model._hash_type = hash_type  # store for use in step_all override
    t_start = time.time()
    growth_log = [(0, 1)]

    for step in range(1, 500000):
        if time_limit and (time.time() - t_start) > time_limit:
            break

        # Custom step_all with different hash functions
        _step_all_custom(model, hash_type)

        if model.n_nodes < max_nodes:
            for nid in range(model.n_nodes):
                if model.looped[nid]:
                    degree = len(model._neighbor_sets[nid])
                    interval = step - int(model.last_spawn_step[nid])
                    model.spawn_events.append((nid, step, degree, interval))
                    model.last_spawn_step[nid] = step

                    model._add_node(parent_id=nid, step=step)
                    model.looped[nid] = False
                    model.effective_sets[nid] = set()
                    if model.n_nodes >= max_nodes:
                        break

        growth_log.append((step, model.n_nodes))
        if model.n_nodes >= max_nodes:
            break

    return model.G, model.n_nodes, growth_log, model.spawn_events


def _step_all_custom(model, hash_type):
    """Step all nodes with a specific hash function."""
    N = model.n_nodes
    ncs = model.node_config_spaces[:N]

    hashes = np.zeros(N, dtype=np.int64)

    if hash_type == 'flat':
        for nid in range(N):
            h = 0
            for nb in model._neighbor_sets[nid]:
                h ^= model.configs[nb]
            hashes[nid] = h % ncs[nid]
    elif hash_type == 'polynomial':
        for nid in range(N):
            C_nid = int(ncs[nid])
            D_eff = model._get_d_eff(nid)
            h = 0
            for nb in sorted(model._neighbor_sets[nid]):
                h = (h * C_nid + int(model.configs[nb])) % D_eff
            hashes[nid] = h
    elif hash_type == 'fnv':
        for nid in range(N):
            D_eff = model._get_d_eff(nid)
            h = 2166136261  # FNV offset basis
            for nb in sorted(model._neighbor_sets[nid]):
                h = ((h ^ int(model.configs[nb])) * 16777619) % D_eff
            hashes[nid] = h
    elif hash_type == 'additive':
        for nid in range(N):
            D_eff = model._get_d_eff(nid)
            h = 0
            for i, nb in enumerate(sorted(model._neighbor_sets[nid])):
                h = (h + int(model.configs[nb]) * (i + 1)) % D_eff
            hashes[nid] = h

    # Table lookup
    cur = model.configs[:N]
    if hash_type != 'flat':
        new_configs = np.zeros(N, dtype=np.int32)
        for nid in range(N):
            new_configs[nid] = model._table_lookup(
                nid, int(cur[nid]), int(hashes[nid]))
    else:
        new_configs = model.tables[np.arange(N), cur, hashes.astype(np.int32)]

    # Check for effective state revisits
    for nid in range(N):
        eff = (int(model.configs[nid]), int(hashes[nid]))
        if eff in model.effective_sets[nid]:
            model.looped[nid] = True
        else:
            model.effective_sets[nid].add(eff)

    # Update configs and visited sets
    model.configs[:N] = new_configs
    for nid in range(N):
        c = int(new_configs[nid])
        if c not in model.visited_sets[nid]:
            model.visited_sets[nid].add(c)
            model.visited_counts[nid] += 1


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    C = 2 ** mem_bits
    D_max = min(C ** 2, 4096)
    t_start = time.time()

    hash_types = [
        ('flat', 'flat', '#999999'),
        ('polynomial', 'hierarchical', '#2196F3'),
        ('fnv', 'hierarchical', '#4CAF50'),
        ('additive', 'hierarchical', '#FF9800'),
    ]

    progress.log("Universality of alpha ~ 2.0 Across Encodings")
    progress.log("=" * 55)
    progress.log(f"  C={C}, D_max={D_max}, target={max_nodes} nodes")
    progress.log(f"  {n_seeds} seeds, {time_budget}s budget")
    progress.log(f"  Hash types: {[h[0] for h in hash_types]}")
    progress.log("")

    per_run = time_budget / max(n_seeds * len(hash_types), 1)

    # === Run all models ===
    results = {ht[0]: [] for ht in hash_types}

    total_runs = n_seeds * len(hash_types)
    run_idx = 0

    for i in range(n_seeds):
        if time.time() - t_start > time_budget * 0.90:
            break
        seed = 40000 + i

        for ht_name, encoding, color in hash_types:
            if time.time() - t_start > time_budget * 0.90:
                break
            run_idx += 1
            progress.update(run_idx, total_runs, ht_name, f"seed {i+1}")
            progress.update_seed(0, max_nodes)

            G, n, gl, spawn_events = _run_model(
                mem_bits, max_nodes, seed, time_limit=per_run,
                encoding=encoding, hash_type=ht_name)

            results[ht_name].append({
                'G': G, 'n': n, 'gl': gl, 'seed': seed,
                'spawn_events': spawn_events,
            })
            progress.log(f"  {ht_name:12s} seed {seed}: {n}n in {gl[-1][0]} steps")

    # === Analysis ===
    progress.log("")
    progress.log("=" * 55)
    progress.log("ANALYSIS")
    progress.log("=" * 55)

    all_alphas = {}
    all_csn = {}

    for ht_name, encoding, color in hash_types:
        alphas = []
        progress.log(f"\n  {ht_name.upper()}:")

        for d in results[ht_name]:
            if d['n'] < 50:
                continue
            r = analyze_powerlaw(d['G'], label=f"{ht_name} s={d['seed']}")
            alphas.append(r['alpha'])
            progress.log(format_powerlaw_result(r))

        if alphas:
            mean_a = np.mean(alphas)
            std_a = np.std(alphas) if len(alphas) > 1 else 0
            all_alphas[ht_name] = (mean_a, std_a, len(alphas))
            progress.log(f"  MEAN alpha = {mean_a:.3f} ± {std_a:.3f} ({len(alphas)} seeds)")

    # Inter-spawn intervals
    progress.log(f"\n  INTER-SPAWN INTERVALS:")
    for ht_name, encoding, color in hash_types:
        all_events = []
        for d in results[ht_name]:
            all_events.extend(d['spawn_events'])
        if not all_events:
            continue

        by_degree = {}
        for nid, step, degree, interval in all_events:
            if interval > 0:
                by_degree.setdefault(degree, []).append(interval)

        progress.log(f"    {ht_name}:")
        degs = sorted(by_degree.keys())[:6]
        for deg in degs:
            intervals = by_degree[deg]
            if len(intervals) >= 3:
                progress.log(
                    f"      deg={deg}: mean={np.mean(intervals):.1f} "
                    f"(n={len(intervals)})")

    # Summary table
    progress.log(f"\n  SUMMARY:")
    progress.log(f"    {'Hash':<14s} {'alpha mean':>8s} {'alpha std':>8s} {'seeds':>6s}")
    progress.log(f"    {'-'*40}")
    for ht_name in ['flat', 'polynomial', 'fnv', 'additive']:
        if ht_name in all_alphas:
            m, s, n = all_alphas[ht_name]
            progress.log(f"    {ht_name:<14s} {m:>8.3f} {s:>8.3f} {n:>6d}")

    # Check universality
    hier_alphas = [all_alphas[k][0] for k in ['polynomial', 'fnv', 'additive']
                   if k in all_alphas]
    if len(hier_alphas) >= 2:
        spread = max(hier_alphas) - min(hier_alphas)
        progress.log(f"\n  UNIVERSALITY: spread across hierarchical encodings = {spread:.3f}")
        if spread < 0.1:
            progress.log(f"  alpha ~ {np.mean(hier_alphas):.3f} is ROBUST across encodings")
        else:
            progress.log(f"  alpha varies — result is encoding-dependent")

    # === Plot ===
    os.makedirs(out_dir, exist_ok=True)
    _plot_results(results, hash_types, C, D_max, max_nodes, out_dir, progress)

    progress.update(1, 1, "Done", "Complete")


def _plot_results(results, hash_types, C, D_max, max_nodes, out_dir, progress):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Growth curves
    ax = axes[0, 0]
    for ht_name, encoding, color in hash_types:
        for d in results[ht_name]:
            steps, nodes = zip(*d['gl'])
            ax.plot(steps, nodes, color=color, alpha=0.4, linewidth=1)
        ax.plot([], [], color=color, label=ht_name, linewidth=2)
    ax.set_xlabel("Step")
    ax.set_ylabel("Nodes")
    ax.set_title("Growth curves")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 2: Log-log degree distributions (CCDF)
    ax = axes[0, 1]
    for ht_name, encoding, color in hash_types:
        for d in results[ht_name][:1]:  # first seed only for clarity
            if d['n'] >= 50:
                degs, ccdf = get_ccdf(d['G'])
                ax.loglog(degs, ccdf, 'o-', color=color, alpha=0.7,
                          markersize=4, linewidth=1, label=ht_name)
    # Reference slopes
    x_ref = np.array([1, 100])
    ax.loglog(x_ref, 0.5 * x_ref ** (-1.0), 'k--', alpha=0.3, label='alpha=2')
    ax.loglog(x_ref, 0.5 * x_ref ** (-1.9), 'k:', alpha=0.3, label='alpha=2.9')
    ax.set_xlabel("Degree")
    ax.set_ylabel("P(X ≥ x)")
    ax.set_title("Degree CCDF (log-log)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 3: Inter-spawn interval vs degree
    ax = axes[1, 0]
    for ht_name, encoding, color in hash_types:
        all_events = []
        for d in results[ht_name]:
            all_events.extend(d['spawn_events'])
        if not all_events:
            continue
        by_degree = {}
        for nid, step, degree, interval in all_events:
            if interval > 0:
                by_degree.setdefault(degree, []).append(interval)
        degs = sorted(by_degree.keys())
        means = [np.mean(by_degree[d]) for d in degs if len(by_degree[d]) >= 5]
        degs = [d for d in degs if len(by_degree[d]) >= 5]
        if degs:
            ax.semilogy(degs, means, 'o-', color=color, label=ht_name,
                        markersize=5, linewidth=1.5)
    ax.set_xlabel("Degree at spawn")
    ax.set_ylabel("Mean inter-spawn interval (log)")
    ax.set_title("Interval vs degree")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: Alpha distribution across seeds
    ax = axes[1, 1]
    positions = []
    labels = []
    for idx, (ht_name, encoding, color) in enumerate(hash_types):
        alphas = []
        for d in results[ht_name]:
            if d['n'] >= 50:
                r = analyze_powerlaw(d['G'])
                if r['alpha'] is not None:
                    alphas.append(r['alpha'])
        if alphas:
            positions.append(idx)
            labels.append(ht_name)
            ax.scatter([idx] * len(alphas), alphas, color=color, s=40,
                       alpha=0.7, zorder=3)
            ax.errorbar(idx, np.mean(alphas), yerr=np.std(alphas) if len(alphas) > 1 else 0,
                        color=color, capsize=5, capthick=2, linewidth=2, zorder=4)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("alpha (power-law exponent)")
    ax.set_title("alpha across seeds and encodings")
    ax.axhline(y=2.0, color='k', linestyle='--', alpha=0.3, label='alpha=2')
    ax.axhline(y=3.0, color='k', linestyle=':', alpha=0.3, label='alpha=3 (BA)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle(
        f"Universality Test: alpha across encodings (C={C}, {max_nodes} nodes)",
        fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(out_dir, "universality.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
