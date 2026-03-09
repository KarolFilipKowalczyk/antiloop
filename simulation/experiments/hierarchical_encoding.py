"""Hierarchical encoding: the blindness theorem in simulation.

Tests the core prediction of the blindness theorem: entities with
hierarchical encoding live LONGER as their degree increases, because
they can distinguish more input patterns. Flat encoding (XOR) gives
constant lifetime regardless of degree.

PREDICTION (from blindness theorem):
  Flat encoding:   D_eff = C for all k.  Lifetime ~ C*sqrt(2).
  Hierarchical:    D_eff = min(C^k, D_max).  Lifetime ~ sqrt(2*C*D_eff).

  log(lifetime) should increase LINEARLY with degree k under
  hierarchical encoding, with slope ~ log(C)/2 per connection.

  Under flat encoding, log(lifetime) is CONSTANT.

WHY THIS MATTERS:
  This is the opposite of preferential attachment. In PA, high-degree
  nodes attract MORE connections (rich get richer). In anti-loop with
  hierarchical encoding, high-degree nodes live LONGER (rich get SLOWER).
  Both produce heavy-tailed topology, but the mechanism is different and
  the inter-spawn interval scaling is a unique, falsifiable signature.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

TITLE = "Hierarchical Encoding (Blindness Theorem)"


def _measure_lifetime_flat(C, k_neighbors, rng, max_steps=None):
    """Entity with flat (XOR) encoding. D_eff = C for all k."""
    D_eff = C
    if max_steps is None:
        max_steps = C * D_eff * 5

    table = rng.integers(0, C, size=(C, D_eff), dtype=np.int32)
    config = int(rng.integers(0, C))

    nb_tables = rng.integers(0, C, size=(max(k_neighbors, 1), C, C),
                             dtype=np.int32)
    nb_configs = rng.integers(0, C, size=max(k_neighbors, 1),
                              dtype=np.int32)

    effective_set = set()

    for step in range(max_steps):
        if k_neighbors == 0:
            h = 0
        else:
            h = 0
            for i in range(k_neighbors):
                h ^= int(nb_configs[i])
            h = h % C

        eff = (config, h)
        if eff in effective_set:
            return step
        effective_set.add(eff)

        new_config = int(table[config, h])
        for i in range(k_neighbors):
            nb_input = config % C
            nb_configs[i] = int(nb_tables[i, nb_configs[i], nb_input])
        config = new_config

    return max_steps


def _measure_lifetime_hierarchical(C, k_neighbors, D_max, rng,
                                    max_steps=None):
    """Entity with hierarchical encoding. D_eff = min(C^k, D_max).

    The transition table is C x D_eff. The hash function uses
    polynomial folding (non-commutative) to distinguish up to D_eff
    input patterns. Each new connection MULTIPLIES the distinguishable
    pattern count by C (up to D_max).

    This models the comparison tree from the blindness theorem:
    each connection adds log2(C) bits of input discrimination.
    """
    if k_neighbors == 0:
        D_eff = 1
    else:
        D_eff = min(C ** k_neighbors, D_max)

    if max_steps is None:
        max_steps = int(np.sqrt(2 * C * D_eff) * 8) + 100

    table = rng.integers(0, C, size=(C, D_eff), dtype=np.int32)
    config = int(rng.integers(0, C))

    nb_tables = rng.integers(0, C, size=(max(k_neighbors, 1), C, C),
                             dtype=np.int32)
    nb_configs = rng.integers(0, C, size=max(k_neighbors, 1),
                              dtype=np.int32)

    effective_set = set()

    for step in range(max_steps):
        if k_neighbors == 0:
            h = 0
        else:
            h = 0
            for i in range(k_neighbors):
                h = (h * C + int(nb_configs[i])) % D_eff
            # Use a prime multiplier mixing step for better distribution
            h = (h * 2654435761) % D_eff  # Knuth's golden ratio hash

        eff = (config, h)
        if eff in effective_set:
            return step
        effective_set.add(eff)

        new_config = int(table[config, h])
        for i in range(k_neighbors):
            nb_input = config % C
            nb_configs[i] = int(nb_tables[i, nb_configs[i], nb_input])
        config = new_config

    return max_steps


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    C = 2 ** mem_bits
    t_start = time.time()

    # D_max caps the hierarchical table width (memory constraint)
    # Use C^3 or 65536, whichever is smaller — allows k=3 data point
    D_max = min(C ** 3, 65536)

    progress.log("Hierarchical Encoding: Blindness Theorem Test")
    progress.log("=" * 55)
    progress.log(f"  C = {C} ({mem_bits}-bit memory)")
    progress.log(f"  D_max = {D_max} (table width cap)")
    progress.log("")
    progress.log("PREDICTION:")
    progress.log(f"  Flat (XOR):        lifetime ~ {C * 1.41:.0f} for all k")
    progress.log(f"  Hierarchical:      lifetime ~ sqrt(2*C*C^k), "
                 f"growing with k")
    progress.log(f"  log(lifetime) slope ~ log({C})/2 = "
                 f"{np.log(C)/2:.3f} per connection")
    progress.log("")

    # Test degrees
    k_values = [0, 1, 2, 3]
    # Add k=4 only if D_max can accommodate it
    if C ** 4 <= D_max:
        k_values.append(4)

    n_trials = max(100, n_seeds * 30)

    # Limit trials for high-D_eff cases (they take longer)
    def trials_for_k(k):
        d = min(C ** k if k > 0 else 1, D_max)
        if d > 4096:
            return max(30, n_trials // 5)
        return n_trials

    progress.log(f"PART 1: Isolated Entity Lifetime vs Degree")
    progress.log(f"  {n_trials} trials per (encoding, k) pair")
    progress.log(f"  Degrees tested: {k_values}")
    progress.log("")

    flat_results = {}     # k -> list of lifetimes
    hier_results = {}     # k -> list of lifetimes

    total_work = len(k_values) * 2
    work_done = 0

    for k in k_values:
        if time.time() - t_start > time_budget * 0.85:
            break

        D_eff_k = min(C ** k if k > 0 else 1, D_max)
        pred_flat = np.sqrt(2 * C * C) if k > 0 else np.sqrt(2 * C)
        pred_hier = np.sqrt(2 * C * D_eff_k)
        nt = trials_for_k(k)

        # Flat encoding
        progress.update(work_done, total_work, "Flat", f"k={k}")
        flat_lives = []
        for trial in range(nt):
            if time.time() - t_start > time_budget * 0.4:
                break
            rng = np.random.default_rng(50000 + k * 10000 + trial)
            life = _measure_lifetime_flat(C, k, rng)
            flat_lives.append(life)
        flat_results[k] = np.array(flat_lives, dtype=np.float64)
        work_done += 1

        if flat_lives:
            progress.log(
                f"  Flat    k={k}: mean={np.mean(flat_lives):7.1f} "
                f"(pred={pred_flat:.0f}), n={len(flat_lives)}")

        # Hierarchical encoding
        progress.update(work_done, total_work, "Hierarchical", f"k={k}")
        hier_lives = []
        for trial in range(nt):
            if time.time() - t_start > time_budget * 0.85:
                break
            rng = np.random.default_rng(60000 + k * 10000 + trial)
            life = _measure_lifetime_hierarchical(C, k, D_max, rng)
            hier_lives.append(life)
        hier_results[k] = np.array(hier_lives, dtype=np.float64)
        work_done += 1

        if hier_lives:
            progress.log(
                f"  Hier    k={k}: mean={np.mean(hier_lives):7.1f} "
                f"(pred={pred_hier:.0f}), D_eff={D_eff_k}, "
                f"n={len(hier_lives)}")

    # === Analysis ===
    progress.log("")
    progress.log("=" * 60)
    progress.log("RESULTS")
    progress.log("=" * 60)

    progress.log("")
    progress.log(f"  {'k':>3} | {'Flat mean':>10} | {'Hier mean':>10} | "
                 f"{'D_eff':>8} | {'Pred hier':>10} | {'Ratio':>6}")
    progress.log("  " + "-" * 60)

    for k in k_values:
        if k not in flat_results or k not in hier_results:
            continue
        if len(flat_results[k]) == 0 or len(hier_results[k]) == 0:
            continue

        D_eff_k = min(C ** k if k > 0 else 1, D_max)
        pred = np.sqrt(2 * C * D_eff_k)
        fm = np.mean(flat_results[k])
        hm = np.mean(hier_results[k])
        ratio = hm / fm if fm > 0 else 0

        progress.log(
            f"  {k:3d} | {fm:10.1f} | {hm:10.1f} | "
            f"{D_eff_k:8d} | {pred:10.1f} | {ratio:6.2f}x")

    # Fit log(lifetime) vs k for hierarchical
    hier_ks = []
    hier_log_means = []
    for k in k_values:
        if k in hier_results and len(hier_results[k]) > 0 and k > 0:
            hier_ks.append(k)
            hier_log_means.append(np.log(np.mean(hier_results[k])))

    if len(hier_ks) >= 2:
        slope, intercept, r, p, se = stats.linregress(
            hier_ks, hier_log_means)
        pred_slope = np.log(C) / 2
        progress.log("")
        progress.log(f"  log(lifetime) vs k (hierarchical):")
        progress.log(f"    Measured slope: {slope:.3f}")
        progress.log(f"    Predicted slope (log(C)/2): {pred_slope:.3f}")
        progress.log(f"    Ratio: {slope/pred_slope:.3f}")
        progress.log(f"    R^2: {r**2:.4f}")
    else:
        slope = None
        pred_slope = np.log(C) / 2

    # Flat encoding slope (should be ~0)
    flat_ks = []
    flat_log_means = []
    for k in k_values:
        if k in flat_results and len(flat_results[k]) > 0 and k > 0:
            flat_ks.append(k)
            flat_log_means.append(np.log(np.mean(flat_results[k])))

    if len(flat_ks) >= 2:
        f_slope, f_int, f_r, f_p, f_se = stats.linregress(
            flat_ks, flat_log_means)
        progress.log(f"  log(lifetime) vs k (flat):")
        progress.log(f"    Measured slope: {f_slope:.3f} (should be ~0)")
        progress.log(f"    R^2: {f_r**2:.4f}")

    progress.log("")
    progress.log("INTERPRETATION:")
    progress.log("  Under hierarchical encoding, each new connection")
    progress.log("  MULTIPLIES the distinguishable input space by C.")
    progress.log("  Birthday paradox on larger space -> longer lifetime.")
    progress.log("  This is the blindness theorem: better encoding ->")
    progress.log("  slower looping -> longer survival.")
    progress.log("")
    progress.log("  Under flat encoding (XOR), all input patterns are")
    progress.log("  folded into C buckets regardless of degree.")
    progress.log("  Lifetime is constant. The entity is BLIND to the")
    progress.log("  information its connections provide.")
    progress.log("")
    progress.log("  UNIQUE PREDICTION: log(inter-spawn interval) grows")
    progress.log("  linearly with degree. Slope = log(C)/2.")
    progress.log("  No other growth model predicts this.")

    # Write report
    os.makedirs(out_dir, exist_ok=True)
    # ... (abbreviated for now)

    _plot_results(flat_results, hier_results, k_values, C, D_max,
                  slope, pred_slope, out_dir, progress)

    progress.update(1, 1, "Done", "Complete")


def _plot_results(flat_results, hier_results, k_values, C, D_max,
                  slope, pred_slope, out_dir, progress):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: Lifetime vs degree (linear scale)
    ax = axes[0]
    flat_means = []
    hier_means = []
    flat_stds = []
    hier_stds = []
    ks_plot = []

    for k in k_values:
        if k in flat_results and k in hier_results:
            if len(flat_results[k]) > 0 and len(hier_results[k]) > 0:
                ks_plot.append(k)
                flat_means.append(np.mean(flat_results[k]))
                hier_means.append(np.mean(hier_results[k]))
                flat_stds.append(np.std(flat_results[k]))
                hier_stds.append(np.std(hier_results[k]))

    if ks_plot:
        ax.errorbar(ks_plot, flat_means, yerr=flat_stds, fmt='s-',
                     color='#999', capsize=5, label='Flat (XOR)', linewidth=2)
        ax.errorbar(ks_plot, hier_means, yerr=hier_stds, fmt='o-',
                     color='#2196F3', capsize=5, label='Hierarchical',
                     linewidth=2)
        # Theoretical curve
        theory_k = np.array(ks_plot, dtype=float)
        theory_d = [min(C ** k if k > 0 else 1, D_max) for k in ks_plot]
        theory_life = [np.sqrt(2 * C * d) for d in theory_d]
        ax.plot(ks_plot, theory_life, 'r--', linewidth=1.5,
                label='Predicted (hier)', alpha=0.7)

    ax.set_xlabel("Degree (k neighbors)")
    ax.set_ylabel("Mean lifetime (steps)")
    ax.set_title("Lifetime vs degree")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 2: Same but log scale (should be linear for hierarchical)
    ax = axes[1]
    if ks_plot:
        ax.semilogy(ks_plot, flat_means, 's-', color='#999',
                     label='Flat (XOR)', linewidth=2, markersize=8)
        ax.semilogy(ks_plot, hier_means, 'o-', color='#2196F3',
                     label='Hierarchical', linewidth=2, markersize=8)
        ax.semilogy(ks_plot, theory_life, 'r--', linewidth=1.5,
                     label='Predicted', alpha=0.7)

        if slope is not None:
            ax.text(0.05, 0.95,
                    f"Hier slope: {slope:.3f}\n"
                    f"Predicted: {pred_slope:.3f}",
                    transform=ax.transAxes, fontsize=9, va='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel("Degree (k neighbors)")
    ax.set_ylabel("Mean lifetime (log scale)")
    ax.set_title("Log lifetime vs degree (should be linear)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 3: Lifetime distributions at k=1 and k=2
    ax = axes[2]
    for k, color, ls in [(1, '#999', '-'), (2, '#2196F3', '-')]:
        if k in hier_results and len(hier_results[k]) > 0:
            D_eff = min(C ** k, D_max)
            sigma = np.sqrt(C * D_eff)
            data = hier_results[k] / sigma  # normalize
            ax.hist(data, bins=30, density=True, alpha=0.4, color=color,
                    label=f'Hier k={k} (D_eff={D_eff})')
        if k in flat_results and len(flat_results[k]) > 0:
            data = flat_results[k] / C  # normalize by C
            ax.hist(data, bins=30, density=True, alpha=0.3, color='gray',
                    label=f'Flat k={k}' if k == 1 else None,
                    linestyle='--')

    # Rayleigh overlay
    x = np.linspace(0, 3, 200)
    ax.plot(x, x * np.exp(-x**2 / 2), 'k-', linewidth=2,
            label='Rayleigh(1)')

    ax.set_xlabel("Lifetime / sigma")
    ax.set_ylabel("Density")
    ax.set_title("Distribution shape (both Rayleigh)")
    ax.set_xlim(0, 3)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.suptitle(
        f"Blindness Theorem: Hierarchical vs Flat Encoding (C={C})",
        fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(out_dir, "hierarchical_encoding.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
