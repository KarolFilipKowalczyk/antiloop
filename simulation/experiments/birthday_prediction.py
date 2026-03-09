"""Birthday paradox prediction: zero-parameter quantitative test.

The anti-loop axiom (A2) applied to finite deterministic systems (A1)
with bounded memory (A3) produces specific, parameter-free predictions:

  Entity lifetime ~ Rayleigh(sigma=C)
  Mean lifetime   = C * sqrt(pi/2) ~ 1.253 * C
  CV of lifetime  = sqrt((4-pi)/pi) ~ 0.523
  Growth rate     = sqrt(2/pi) / C  ~ 0.798 / C

These follow from the birthday paradox on C^2 effective states
(config x hash). No tunable parameters.

WHY THIS IS UNIQUE: Every other network growth model (preferential
attachment, random trees, Barabasi-Albert) treats growth rate as a
FREE PARAMETER. Anti-loop DERIVES it from entity memory size C.
The prediction growth_rate * C = sqrt(2/pi) is falsifiable and
specific to anti-loop dynamics.

COMPARISON:
  Poisson spawning:       CV = 1.000 (exponential distribution)
  Deterministic spawning: CV = 0.000
  Anti-loop prediction:   CV = 0.523 (Rayleigh distribution)
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

TITLE = "Birthday Paradox Prediction"

# Theoretical constants (zero free parameters)
PRED_MEAN_COEFF = np.sqrt(np.pi / 2)    # ~ 1.2533
PRED_CV = np.sqrt((4 - np.pi) / np.pi)  # ~ 0.5227
PRED_RATE_COEFF = np.sqrt(2 / np.pi)    # ~ 0.7979


def _measure_lifetime(C, n_neighbors, rng, max_steps=None):
    """Run one isolated FSM entity until effective state revisit.

    Entity has C states, receives XOR hash of n_neighbors FSM outputs.
    Returns steps until first (config, hash) collision.
    """
    if max_steps is None:
        max_steps = C * C * 5

    table = rng.integers(0, C, size=(C, C), dtype=np.int32)
    config = int(rng.integers(0, C))

    # Neighbors are independent FSMs (simulate environment)
    nb_tables = rng.integers(0, C, size=(n_neighbors, C, C), dtype=np.int32)
    nb_configs = rng.integers(0, C, size=n_neighbors, dtype=np.int32)

    effective_set = set()

    for step in range(max_steps):
        h = 0
        for i in range(n_neighbors):
            h ^= int(nb_configs[i])
        h = h % C

        eff = (config, h)
        if eff in effective_set:
            return step
        effective_set.add(eff)

        new_config = int(table[config, h])
        for i in range(n_neighbors):
            nb_input = config % C
            nb_configs[i] = int(nb_tables[i, nb_configs[i], nb_input])
        config = new_config

    return max_steps


def _rayleigh_cdf(x, sigma):
    return 1 - np.exp(-x**2 / (2 * sigma**2))


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    C_default = 2 ** mem_bits
    t_start = time.time()

    progress.log("Birthday Paradox Prediction Test")
    progress.log("=" * 55)
    progress.log("")
    progress.log("ZERO-PARAMETER PREDICTIONS (derived from axioms):")
    progress.log(f"  Mean lifetime / C = sqrt(pi/2) = {PRED_MEAN_COEFF:.4f}")
    progress.log(f"  CV of lifetime    = sqrt((4-pi)/pi) = {PRED_CV:.4f}")
    progress.log(f"  Growth rate * C   = sqrt(2/pi) = {PRED_RATE_COEFF:.4f}")
    progress.log("")

    # --- Part 1: Entity Lifetime Distribution ---
    c_values = [16, 32, 64]
    if mem_bits >= 7:
        c_values.append(128)
    if mem_bits >= 9:
        c_values.append(256)

    n_trials = max(300, n_seeds * 60)
    n_neighbors_list = [1, 2, 5]  # test independence from neighbor count

    progress.log("PART 1: Isolated Entity Lifetimes")
    progress.log(f"  {n_trials} trials per (C, n_neighbors) pair")
    progress.log(f"  Neighbor counts: {n_neighbors_list}")
    progress.log("")

    all_results = {}
    step_idx = 0
    total_steps = len(c_values) * len(n_neighbors_list)

    for C in c_values:
        all_results[C] = {}
        for n_nb in n_neighbors_list:
            if time.time() - t_start > time_budget * 0.5:
                break

            progress.update(step_idx, total_steps + len(c_values),
                            "Lifetime", f"C={C}, {n_nb} neighbors")
            step_idx += 1

            lifetimes = []
            for trial in range(n_trials):
                rng = np.random.default_rng(10000 * C + 1000 * n_nb + trial)
                life = _measure_lifetime(C, n_nb, rng)
                lifetimes.append(life)

            lifetimes = np.array(lifetimes, dtype=np.float64)
            mean = np.mean(lifetimes)
            std = np.std(lifetimes)
            cv = std / mean if mean > 0 else 0

            # KS test against Rayleigh(sigma=C)
            ks_stat, ks_p = stats.kstest(
                lifetimes, lambda x: _rayleigh_cdf(x, C))

            all_results[C][n_nb] = {
                'lifetimes': lifetimes,
                'mean': mean,
                'std': std,
                'cv': cv,
                'ks_stat': ks_stat,
                'ks_p': ks_p,
            }

            progress.log(
                f"  C={C:4d}, nb={n_nb}: "
                f"mean={mean:.1f} (pred={C*PRED_MEAN_COEFF:.1f}), "
                f"CV={cv:.3f} (pred={PRED_CV:.3f}), "
                f"KS p={ks_p:.3f}")

    # --- Part 2: Network Growth Rate ---
    progress.log("")
    progress.log("PART 2: Network Growth Rate (loop-only spawning)")
    progress.log("  Pure anti-loop: entities spawn ONLY at effective state revisit")
    progress.log("")

    from simulation.shared.engine import SpawnModel

    growth_results = {}

    for ci, C in enumerate(c_values):
        if C not in all_results or not all_results[C]:
            continue
        if time.time() - t_start > time_budget * 0.85:
            break

        bits = int(np.log2(C))
        target_nodes = min(max_nodes, 300)
        progress.update(step_idx, total_steps + len(c_values),
                        "Growth rate", f"C={C}")
        step_idx += 1

        rates = []
        growth_logs = []

        for seed_i in range(min(n_seeds, 5)):
            if time.time() - t_start > time_budget * 0.85:
                break

            model = SpawnModel(bits, target_nodes, seed=20000 + ci * 100 + seed_i)
            log = [(0, 1)]

            for step in range(1, 100000):
                if time.time() - t_start > time_budget * 0.85:
                    break
                model.step_all()

                # Pure loop-triggered spawning only
                if model.n_nodes < target_nodes:
                    for nid in range(model.n_nodes):
                        if model.looped[nid]:
                            model._add_node(parent_id=nid, step=step)
                            model.looped[nid] = False
                            model.effective_sets[nid] = set()
                            if model.n_nodes >= target_nodes:
                                break

                log.append((step, model.n_nodes))
                if model.n_nodes >= target_nodes:
                    break

            growth_logs.append(log)

            # Fit exponential to early growth phase (2 to 50% of target)
            log_data = [(s, np.log(n)) for s, n in log
                        if 2 <= n <= target_nodes * 0.5]
            if len(log_data) >= 10:
                steps_arr = np.array([d[0] for d in log_data])
                logn_arr = np.array([d[1] for d in log_data])
                slope, intercept, r, p, se = stats.linregress(steps_arr, logn_arr)
                if r > 0.95:  # good exponential fit
                    rates.append(slope)

        if rates:
            mean_rate = np.mean(rates)
            pred_rate = PRED_RATE_COEFF / C
            product = mean_rate * C
            growth_results[C] = {
                'rates': rates,
                'mean_rate': mean_rate,
                'pred_rate': pred_rate,
                'product': product,
                'growth_logs': growth_logs,
            }
            progress.log(
                f"  C={C:4d}: rate={mean_rate:.6f} "
                f"(pred={pred_rate:.6f}), "
                f"rate*C={product:.4f} (pred={PRED_RATE_COEFF:.4f})")

    # --- Summary ---
    progress.log("")
    progress.log("=" * 60)
    progress.log("RESULTS SUMMARY")
    progress.log("=" * 60)

    # Aggregate lifetime results (using n_nb=2 as canonical)
    progress.log("")
    progress.log("Entity lifetimes (n_neighbors=2):")
    progress.log(f"  {'C':>6} | {'mean/C':>8} | {'pred':>8} | "
                 f"{'CV':>6} | {'pred':>6} | {'KS p':>6}")
    progress.log("  " + "-" * 55)

    canonical_cvs = []
    canonical_ratios = []

    for C in c_values:
        if C not in all_results or 2 not in all_results[C]:
            continue
        r = all_results[C][2]
        ratio = r['mean'] / C
        canonical_cvs.append(r['cv'])
        canonical_ratios.append(ratio)
        progress.log(
            f"  {C:6d} | {ratio:8.4f} | {PRED_MEAN_COEFF:8.4f} | "
            f"{r['cv']:6.4f} | {PRED_CV:6.4f} | {r['ks_p']:6.3f}")

    progress.log("")
    progress.log("Independence from neighbor count:")
    progress.log(f"  {'C':>6} | {'nb=1 CV':>8} | {'nb=2 CV':>8} | {'nb=5 CV':>8}")
    progress.log("  " + "-" * 42)

    for C in c_values:
        if C not in all_results:
            continue
        cvs = []
        for n_nb in n_neighbors_list:
            if n_nb in all_results[C]:
                cvs.append(f"{all_results[C][n_nb]['cv']:8.4f}")
            else:
                cvs.append("     N/A")
        progress.log(f"  {C:6d} | {' | '.join(cvs)}")

    progress.log("")
    progress.log("Growth rate (loop-only spawn model):")
    if growth_results:
        progress.log(f"  {'C':>6} | {'rate*C':>8} | {'predicted':>9}")
        progress.log("  " + "-" * 30)
        products = []
        for C in c_values:
            if C in growth_results:
                p = growth_results[C]['product']
                products.append(p)
                progress.log(
                    f"  {C:6d} | {p:8.4f} | {PRED_RATE_COEFF:9.4f}")
        if products:
            progress.log(
                f"\n  Mean rate*C = {np.mean(products):.4f} +/- "
                f"{np.std(products):.4f} (predicted: {PRED_RATE_COEFF:.4f})")

    progress.log("")
    progress.log("NULL MODEL COMPARISON:")
    progress.log(f"  Poisson (exponential):    CV = 1.000")
    progress.log(f"  Deterministic (fixed):    CV = 0.000")
    progress.log(f"  Anti-loop (Rayleigh):     CV = {PRED_CV:.3f}")
    if canonical_cvs:
        progress.log(
            f"  Measured:                 CV = {np.mean(canonical_cvs):.3f} "
            f"+/- {np.std(canonical_cvs):.3f}")

    progress.log("")
    progress.log("INTERPRETATION:")
    progress.log("  The anti-loop axiom determines entity lifetime distribution")
    progress.log("  with ZERO free parameters. The Rayleigh distribution and its")
    progress.log("  specific CV ~ 0.523 distinguish anti-loop from all models")
    progress.log("  based on Poisson timing (CV=1) or fixed timers (CV=0).")
    progress.log("")
    progress.log("  Consequence for network growth: growth rate is NOT a free")
    progress.log("  parameter. It equals sqrt(2/pi)/C, derived entirely from")
    progress.log("  entity memory size. No other growth model makes this claim.")

    # --- Write report ---
    os.makedirs(out_dir, exist_ok=True)

    lines = [
        "=" * 60,
        "Birthday Paradox Prediction: Zero-Parameter Test",
        "=" * 60,
        "",
        "PREDICTIONS (derived from A1+A2+A3, zero free parameters):",
        f"  Mean lifetime / C = sqrt(pi/2) = {PRED_MEAN_COEFF:.4f}",
        f"  CV of lifetime    = sqrt((4-pi)/pi) = {PRED_CV:.4f}",
        f"  Growth rate * C   = sqrt(2/pi) = {PRED_RATE_COEFF:.4f}",
        "",
    ]
    if canonical_cvs:
        lines += [
            "RESULTS:",
            f"  Measured mean/C: {np.mean(canonical_ratios):.4f} "
            f"+/- {np.std(canonical_ratios):.4f}",
            f"  Measured CV: {np.mean(canonical_cvs):.4f} "
            f"+/- {np.std(canonical_cvs):.4f}",
        ]
    if growth_results:
        products = [growth_results[C]['product'] for C in growth_results]
        lines.append(
            f"  Measured rate*C: {np.mean(products):.4f} "
            f"+/- {np.std(products):.4f}")
    lines += [
        "",
        "Null models: Poisson CV=1.000, Deterministic CV=0.000",
        f"Anti-loop prediction: CV={PRED_CV:.3f}",
    ]

    report = "\n".join(lines)
    with open(os.path.join(out_dir, "birthday_prediction_results.txt"), "w") as f:
        f.write(report)

    # --- Plot ---
    _plot_results(all_results, growth_results, c_values, n_neighbors_list,
                  out_dir, progress)

    progress.update(1, 1, "Done", "Complete")


def _plot_results(all_results, growth_results, c_values, n_neighbors_list,
                  out_dir, progress):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Lifetime distributions normalized by C, with Rayleigh overlay
    ax = axes[0, 0]
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(c_values)))
    x_ray = np.linspace(0, 3, 200)
    rayleigh_pdf = x_ray * np.exp(-x_ray**2 / 2)  # Rayleigh(sigma=1) pdf

    for i, C in enumerate(c_values):
        if C not in all_results or 2 not in all_results[C]:
            continue
        lifetimes = all_results[C][2]['lifetimes'] / C  # normalize by C
        ax.hist(lifetimes, bins=30, density=True, alpha=0.4,
                color=colors[i], label=f"C={C}")

    ax.plot(x_ray, rayleigh_pdf, 'k-', linewidth=2, label="Rayleigh(1)")
    ax.set_xlabel("Lifetime / C")
    ax.set_ylabel("Density")
    ax.set_title("Lifetime distribution (normalized by C)")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 3)
    ax.grid(True, alpha=0.3)

    # Panel 2: CV vs C (should be flat at 0.523)
    ax = axes[0, 1]
    for n_nb in n_neighbors_list:
        cvs = []
        cs = []
        for C in c_values:
            if C in all_results and n_nb in all_results[C]:
                cvs.append(all_results[C][n_nb]['cv'])
                cs.append(C)
        if cvs:
            ax.plot(cs, cvs, 'o-', label=f"nb={n_nb}", markersize=8)

    ax.axhline(PRED_CV, color='red', linestyle='--', linewidth=2,
               label=f"Predicted: {PRED_CV:.3f}")
    ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5,
               label="Poisson: 1.000")
    ax.set_xlabel("C (config space)")
    ax.set_ylabel("CV of lifetime")
    ax.set_title("Coefficient of variation (should be constant)")
    ax.set_xscale('log', base=2)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 3: Mean lifetime / C vs C (should be flat at sqrt(pi/2))
    ax = axes[1, 0]
    for n_nb in n_neighbors_list:
        ratios = []
        cs = []
        for C in c_values:
            if C in all_results and n_nb in all_results[C]:
                ratios.append(all_results[C][n_nb]['mean'] / C)
                cs.append(C)
        if ratios:
            ax.plot(cs, ratios, 'o-', label=f"nb={n_nb}", markersize=8)

    ax.axhline(PRED_MEAN_COEFF, color='red', linestyle='--', linewidth=2,
               label=f"Predicted: {PRED_MEAN_COEFF:.3f}")
    ax.set_xlabel("C (config space)")
    ax.set_ylabel("Mean lifetime / C")
    ax.set_title("Mean lifetime scaling (should be constant)")
    ax.set_xscale('log', base=2)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 4: Growth rate * C vs C (should be flat at sqrt(2/pi))
    ax = axes[1, 1]
    if growth_results:
        cs = sorted(growth_results.keys())
        products = [growth_results[C]['product'] for C in cs]
        ax.plot(cs, products, 'o-', color='#2196F3', markersize=10,
                linewidth=2, label="Measured")
        ax.axhline(PRED_RATE_COEFF, color='red', linestyle='--', linewidth=2,
                   label=f"Predicted: {PRED_RATE_COEFF:.3f}")
        ax.set_xlabel("C (config space)")
        ax.set_ylabel("Growth rate * C")
        ax.set_title("Growth rate scaling (should be constant)")
        ax.set_xscale('log', base=2)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Growth rate not measured\n(time limit)",
                ha='center', va='center', transform=ax.transAxes)

    plt.suptitle("Birthday Paradox Prediction: Zero-Parameter Test",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(out_dir, "birthday_prediction.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
