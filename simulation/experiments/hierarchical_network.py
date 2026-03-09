"""Hierarchical encoding in a growing network.

Runs the spawn model with hierarchical encoding (D_eff grows with
degree) and compares against flat encoding (XOR, D_eff = C).

KEY QUESTION: What topology emerges when well-connected entities
reproduce SLOWER (hierarchical) vs at constant rate (flat)?

PREDICTIONS:
  - Hierarchical: natural deceleration as entities gain connections.
    First spawn fast (degree 1, D_eff=C), subsequent spawns slow
    (degree 2+, D_eff=C^2+). Should produce different alpha and
    degree distribution than flat.
  - Flat: all entities spawn at same rate regardless of degree.
    Growth is pure exponential until max_nodes.
  - Inter-spawn intervals: flat = constant ~C*sqrt(2);
    hierarchical = increases with degree (blindness theorem).
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from simulation.shared.engine import (
    run_hierarchical_model, SpawnModel,
)
from simulation.shared.analysis import (
    analyze_powerlaw, format_powerlaw_result,
)

TITLE = "Hierarchical Network Growth"


def _run_flat_model(mem_bits, max_nodes, seed, time_limit):
    """Run flat (XOR) spawn model with loop-only triggering."""
    model = SpawnModel(mem_bits, max_nodes, seed, encoding='flat')
    t_start = time.time()
    growth_log = [(0, 1)]

    for step in range(1, 200000):
        if time_limit and (time.time() - t_start) > time_limit:
            break
        model.step_all()

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

    nodes_data = {
        "birth_steps": model.birth_steps[:model.n_nodes].copy(),
        "config_space": model.config_space,
        "parent": model.parent[:model.n_nodes].copy(),
        "spawn_events": model.spawn_events,
    }
    return model.G, nodes_data, growth_log


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    C = 2 ** mem_bits
    D_max = min(C ** 2, 4096)
    target = max_nodes
    t_start = time.time()

    progress.log("Hierarchical Network Growth")
    progress.log("=" * 50)
    progress.log(f"  C={C}, D_max={D_max}, target={target} nodes")
    progress.log(f"  {n_seeds} seeds, {time_budget}s budget")
    progress.log("")

    per_seed = time_budget / max(n_seeds * 2, 1)

    # === Run both models ===
    flat_data = []
    hier_data = []

    for i in range(n_seeds):
        if time.time() - t_start > time_budget * 0.85:
            break
        seed = 30000 + i

        # Flat model
        progress.update(i * 2, n_seeds * 2, "Flat", f"seed {i+1}")
        progress.update_seed(0, target)
        G_f, nd_f, gl_f = _run_flat_model(
            mem_bits, target, seed, time_limit=per_seed)
        n_f = G_f.number_of_nodes()
        steps_f = gl_f[-1][0]
        flat_data.append({
            'G': G_f, 'nd': nd_f, 'gl': gl_f,
            'n': n_f, 'steps': steps_f, 'seed': seed,
            'spawn_events': nd_f['spawn_events'],
        })
        progress.log(f"  Flat  seed {seed}: {n_f}n in {steps_f} steps")

        # Hierarchical model
        progress.update(i * 2 + 1, n_seeds * 2, "Hier", f"seed {i+1}")
        progress.update_seed(0, target)
        G_h, nd_h, gl_h = run_hierarchical_model(
            mem_bits, target, seed, time_limit=per_seed, D_max=D_max)
        n_h = G_h.number_of_nodes()
        steps_h = gl_h[-1][0]
        hier_data.append({
            'G': G_h, 'nd': nd_h, 'gl': gl_h,
            'n': n_h, 'steps': steps_h, 'seed': seed,
            'spawn_events': nd_h['spawn_events'],
        })
        progress.log(f"  Hier  seed {seed}: {n_h}n in {steps_h} steps")

    # === Analysis ===
    progress.log("")
    progress.log("=" * 50)
    progress.log("ANALYSIS")
    progress.log("=" * 50)

    # Growth speed
    flat_steps = [d['steps'] for d in flat_data if d['n'] >= target]
    hier_steps = [d['steps'] for d in hier_data if d['n'] >= target]
    if flat_steps:
        progress.log(f"\n  Growth to {target} nodes:")
        progress.log(f"    Flat:  {np.mean(flat_steps):.0f} steps")
    if hier_steps:
        progress.log(f"    Hier:  {np.mean(hier_steps):.0f} steps")
    if flat_steps and hier_steps:
        progress.log(f"    Ratio: {np.mean(hier_steps)/np.mean(flat_steps):.1f}x slower")

    # Topology
    progress.log(f"\n  Topology (power-law alpha):")
    flat_alphas = []
    hier_alphas = []
    for d in flat_data:
        if d['n'] >= 20:
            r = analyze_powerlaw(d['G'], label=f"flat s={d['seed']}")
            flat_alphas.append(r['alpha'])
            progress.log(f"    Flat  s={d['seed']}: alpha={r['alpha']:.3f}")
    for d in hier_data:
        if d['n'] >= 20:
            r = analyze_powerlaw(d['G'], label=f"hier s={d['seed']}")
            hier_alphas.append(r['alpha'])
            progress.log(f"    Hier  s={d['seed']}: alpha={r['alpha']:.3f}")

    if flat_alphas:
        progress.log(f"    Flat  mean alpha: {np.mean(flat_alphas):.3f}")
    if hier_alphas:
        progress.log(f"    Hier  mean alpha: {np.mean(hier_alphas):.3f}")

    # Inter-spawn intervals vs degree
    progress.log(f"\n  Inter-spawn intervals vs degree:")

    for label, data_list in [("Flat", flat_data), ("Hier", hier_data)]:
        all_events = []
        for d in data_list:
            all_events.extend(d['spawn_events'])
        if not all_events:
            continue

        # Group by degree
        by_degree = {}
        for nid, step, degree, interval in all_events:
            if interval > 0:
                by_degree.setdefault(degree, []).append(interval)

        progress.log(f"    {label}:")
        degs = sorted(by_degree.keys())[:8]
        for deg in degs:
            intervals = by_degree[deg]
            if len(intervals) >= 3:
                progress.log(
                    f"      deg={deg}: mean={np.mean(intervals):.1f} "
                    f"(n={len(intervals)})")

        # Fit log(interval) vs degree
        fit_degs = []
        fit_means = []
        for deg in sorted(by_degree.keys()):
            if len(by_degree[deg]) >= 3 and deg > 0:
                fit_degs.append(deg)
                fit_means.append(np.log(np.mean(by_degree[deg])))
        if len(fit_degs) >= 2:
            slope, _, r, _, _ = stats.linregress(fit_degs, fit_means)
            progress.log(
                f"      log(interval) slope: {slope:.3f}, "
                f"R^2={r**2:.3f}")

    # Summary
    progress.log(f"\n  INTERPRETATION:")
    if hier_steps and flat_steps:
        progress.log(
            f"    Hierarchical is ~{np.mean(hier_steps)/np.mean(flat_steps):.1f}x "
            f"slower to reach {target} nodes.")
    progress.log(
        f"    Well-connected entities reproduce slower (blindness theorem).")
    progress.log(
        f"    This is the opposite of preferential attachment.")

    # === Plot ===
    os.makedirs(out_dir, exist_ok=True)
    _plot_results(flat_data, hier_data, target, C, D_max, out_dir, progress)

    progress.update(1, 1, "Done", "Complete")


def _plot_results(flat_data, hier_data, target, C, D_max, out_dir, progress):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Growth curves
    ax = axes[0, 0]
    for d in flat_data:
        steps, nodes = zip(*d['gl'])
        ax.plot(steps, nodes, color='#999', alpha=0.5, linewidth=1)
    for d in hier_data:
        steps, nodes = zip(*d['gl'])
        ax.plot(steps, nodes, color='#2196F3', alpha=0.5, linewidth=1)
    ax.plot([], [], color='#999', label='Flat')
    ax.plot([], [], color='#2196F3', label='Hierarchical')
    ax.set_xlabel("Step")
    ax.set_ylabel("Nodes")
    ax.set_title("Growth curves")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 2: Degree distributions
    ax = axes[0, 1]
    for d in flat_data[:1]:
        degs = [d['G'].degree(n) for n in d['G'].nodes()]
        if degs:
            vals, counts = np.unique(degs, return_counts=True)
            ax.scatter(vals, counts, color='#999', alpha=0.7, s=20,
                       label='Flat')
    for d in hier_data[:1]:
        degs = [d['G'].degree(n) for n in d['G'].nodes()]
        if degs:
            vals, counts = np.unique(degs, return_counts=True)
            ax.scatter(vals, counts, color='#2196F3', alpha=0.7, s=20,
                       label='Hierarchical')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Degree")
    ax.set_ylabel("Count")
    ax.set_title("Degree distribution")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: Inter-spawn interval vs degree
    ax = axes[1, 0]
    for label, data_list, color in [("Flat", flat_data, '#999'),
                                     ("Hier", hier_data, '#2196F3')]:
        all_events = []
        for d in data_list:
            all_events.extend(d['spawn_events'])
        if not all_events:
            continue
        by_degree = {}
        for nid, step, degree, interval in all_events:
            if interval > 0:
                by_degree.setdefault(degree, []).append(interval)
        degs = sorted(by_degree.keys())
        means = [np.mean(by_degree[d]) for d in degs if len(by_degree[d]) >= 3]
        degs = [d for d in degs if len(by_degree[d]) >= 3]
        if degs:
            ax.semilogy(degs, means, 'o-', color=color, label=label,
                        markersize=6, linewidth=1.5)

    ax.set_xlabel("Degree at spawn")
    ax.set_ylabel("Mean inter-spawn interval (log)")
    ax.set_title("Interval vs degree (should diverge)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: Children per entity distribution
    ax = axes[1, 1]
    for label, data_list, color in [("Flat", flat_data, '#999'),
                                     ("Hier", hier_data, '#2196F3')]:
        for d in data_list[:1]:
            parent_arr = d['nd']['parent']
            n = len(parent_arr)
            children_count = np.zeros(n, dtype=int)
            for p in parent_arr:
                if p >= 0:
                    children_count[p] += 1
            vals, counts = np.unique(children_count, return_counts=True)
            ax.bar(vals + (0.2 if label == "Hier" else -0.2), counts,
                   width=0.4, color=color, alpha=0.7, label=label)
    ax.set_xlabel("Children per entity")
    ax.set_ylabel("Count")
    ax.set_title("Fertility distribution")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle(
        f"Hierarchical vs Flat Network Growth (C={C}, D_max={D_max})",
        fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(out_dir, "hierarchical_network.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
