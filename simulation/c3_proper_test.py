"""
Proper C3 Test: Scale-Free Topology from Anti-Loop Constraint
=============================================================

Addresses all known flaws in the preliminary test (topology_simulation.py):
  1. Growing random graph control (not static Erdős-Rényi)
  2. Clauset-Shalizi-Newman power-law test (via `powerlaw` package)
  3. 30 seeds per condition
  4. Sensitivity analysis: hash function, loop pressure threshold, spawn probability
  5. Separates growth-phase topology from edge-only-at-cap phase

Usage:
    python simulation/c3_proper_test.py              # full run (30 seeds, ~20 min)
    python simulation/c3_proper_test.py --quick       # quick test (3 seeds, ~2 min)

Outputs:
    simulation/results/c3_degree_distributions.png
    simulation/results/c3_powerlaw_fits.png
    simulation/results/c3_sensitivity.png
    simulation/results/c3_results.txt
"""

import argparse
import os
import sys
import time
import warnings
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import powerlaw

# Suppress powerlaw's noisy warnings — we check fit quality ourselves
warnings.filterwarnings("ignore", module="powerlaw")

# ============================================================
# FSM Node
# ============================================================

HASH_XOR = "xor"
HASH_SUM = "sum"
HASH_PRODUCT = "product"


class FSMNode:
    __slots__ = ("config_space", "config", "visited", "table")

    def __init__(self, mem_bits, rng):
        self.config_space = 2 ** mem_bits
        self.config = rng.integers(0, self.config_space)
        self.visited = {self.config}
        self.table = rng.integers(0, self.config_space,
                                  size=(self.config_space, self.config_space))

    @property
    def pressure(self):
        return len(self.visited) / self.config_space

    def step(self, nb_configs, hash_fn):
        h = _compute_hash(nb_configs, hash_fn) % self.config_space
        self.config = self.table[self.config, h]
        self.visited.add(self.config)


def _compute_hash(configs, hash_fn):
    if not configs:
        return 0
    if hash_fn == HASH_XOR:
        h = 0
        for c in configs:
            h ^= c
        return h
    elif hash_fn == HASH_SUM:
        return sum(configs)
    elif hash_fn == HASH_PRODUCT:
        h = 1
        for c in configs:
            h = (h * (c + 1)) & 0xFFFFFFFF  # +1 avoids zero; mask prevents overflow
        return h
    raise ValueError(f"Unknown hash function: {hash_fn}")


# ============================================================
# Growth log: records (step, n_nodes, n_edges) for control matching
# ============================================================

@dataclass
class GrowthLog:
    steps: list = field(default_factory=list)
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)

    def record(self, step, n_nodes, n_edges):
        self.steps.append(step)
        self.nodes.append(n_nodes)
        self.edges.append(n_edges)


# ============================================================
# Anti-loop simulation
# ============================================================

def run_antiloop(mem_bits, max_nodes, initial_n, seed,
                 hash_fn=HASH_XOR, pressure_threshold=0.7,
                 spawn_prob=0.3, max_stressed_per_step=5,
                 max_steps=10000):
    """
    Run anti-loop graph growth and return:
      - G_growth: graph snapshot at the end of the growth phase
      - G_final: graph after edge-only-at-cap phase
      - growth_log: (step, nodes, edges) trajectory for control matching
    """
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    nodes = {}

    # Initialize ring
    for i in range(initial_n):
        G.add_node(i)
        nodes[i] = FSMNode(mem_bits, rng)
    for i in range(initial_n):
        G.add_edge(i, (i + 1) % initial_n)

    next_id = initial_n
    growth_log = GrowthLog()
    growth_log.record(0, G.number_of_nodes(), G.number_of_edges())

    G_growth = None  # snapshot when we first hit cap

    for step in range(1, max_steps + 1):
        # All nodes step
        node_list = list(G.nodes())
        for nid in node_list:
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn)

        # Find stressed nodes
        stressed = [n for n in node_list if nodes[n].pressure > pressure_threshold]
        if not stressed:
            growth_log.record(step, G.number_of_nodes(), G.number_of_edges())
            continue

        acted = rng.choice(stressed,
                           size=min(max_stressed_per_step, len(stressed)),
                           replace=False)

        at_cap = G.number_of_nodes() >= max_nodes

        # Snapshot the growth phase
        if at_cap and G_growth is None:
            G_growth = G.copy()

        for nid in acted:
            current_nb = set(G.neighbors(nid)) | {nid}
            candidates = [n for n in G.nodes() if n not in current_nb]

            if candidates:
                # Connect to existing node (random choice — strategy doesn't
                # matter for proper test, we test the constraint itself)
                target = rng.choice(candidates)
                G.add_edge(nid, target)

                # Spawn new node if below cap
                if not at_cap and rng.random() < spawn_prob:
                    if G.number_of_nodes() < max_nodes:
                        G.add_node(next_id)
                        nodes[next_id] = FSMNode(mem_bits, rng)
                        G.add_edge(nid, next_id)
                        next_id += 1
                        if G.number_of_nodes() >= max_nodes:
                            at_cap = True
                            if G_growth is None:
                                G_growth = G.copy()

            elif not at_cap:
                # No candidates — must spawn
                G.add_node(next_id)
                nodes[next_id] = FSMNode(mem_bits, rng)
                G.add_edge(nid, next_id)
                next_id += 1
                if G.number_of_nodes() >= max_nodes:
                    at_cap = True
                    if G_growth is None:
                        G_growth = G.copy()

        growth_log.record(step, G.number_of_nodes(), G.number_of_edges())

        # Stop early if at cap and we've run enough edge-only steps
        if at_cap and (step - growth_log.steps[0]) > 500:
            break

    if G_growth is None:
        G_growth = G.copy()

    return G_growth, G, growth_log


# ============================================================
# Growing random graph control
# ============================================================

def build_growing_random_control(growth_log, seed):
    """
    Build a control graph that matches the anti-loop growth trajectory
    (same number of nodes and edges at each step) but without any
    anti-loop dynamics. Nodes are added over time with random attachment.
    """
    rng = np.random.default_rng(seed)

    # Get deltas
    n_nodes_seq = growth_log.nodes
    n_edges_seq = growth_log.edges

    G = nx.Graph()
    # Start with the same initial ring
    initial_n = n_nodes_seq[0]
    for i in range(initial_n):
        G.add_node(i)
    for i in range(initial_n):
        G.add_edge(i, (i + 1) % initial_n)

    next_id = initial_n

    for t in range(1, len(n_nodes_seq)):
        target_nodes = n_nodes_seq[t]
        target_edges = n_edges_seq[t]

        # Add nodes
        while G.number_of_nodes() < target_nodes:
            G.add_node(next_id)
            # Attach to a random existing node
            if G.number_of_nodes() > 1:
                target_node = rng.choice(list(G.nodes()))
                G.add_edge(next_id, target_node)
            next_id += 1

        # Add edges to match count (random attachment, no preferential)
        attempts = 0
        while G.number_of_edges() < target_edges and attempts < 500:
            attempts += 1
            node_list = list(G.nodes())
            u = rng.choice(node_list)
            v = rng.choice(node_list)
            if u != v and not G.has_edge(u, v):
                G.add_edge(u, v)

    return G


# ============================================================
# Analysis
# ============================================================

def analyze_degree_distribution(G, label=""):
    """
    Apply Clauset-Shalizi-Newman power-law test.
    Returns dict with alpha, xmin, p_value, comparison to alternatives.
    """
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    degrees = degrees[degrees >= 1]

    if len(degrees) < 30:
        return {"label": label, "alpha": None, "xmin": None, "p": None,
                "n_tail": 0, "vs_exp": None, "vs_lognormal": None}

    fit = powerlaw.Fit(degrees, discrete=True, verbose=False)

    # Compare power law vs alternatives
    R_exp, p_exp = fit.distribution_compare("power_law", "exponential",
                                            normalized_ratio=True)
    R_ln, p_ln = fit.distribution_compare("power_law", "lognormal",
                                          normalized_ratio=True)

    n_tail = int(np.sum(degrees >= fit.xmin))

    return {
        "label": label,
        "alpha": fit.alpha,
        "xmin": fit.xmin,
        "sigma": fit.sigma,
        "n_tail": n_tail,
        "vs_exp": {"R": R_exp, "p": p_exp},
        "vs_lognormal": {"R": R_ln, "p": p_ln},
    }


def format_result(r):
    """Format a single analysis result as a string."""
    if r["alpha"] is None:
        return f"  {r['label']}: insufficient data"

    lines = [
        f"  {r['label']}:",
        f"    alpha = {r['alpha']:.3f} +/- {r['sigma']:.3f}  "
        f"(xmin = {r['xmin']:.0f}, n_tail = {r['n_tail']})",
    ]

    vs_exp = r["vs_exp"]
    direction = "power_law BETTER" if vs_exp["R"] > 0 else "exponential BETTER"
    sig = "***" if vs_exp["p"] < 0.01 else ("**" if vs_exp["p"] < 0.05 else "ns")
    lines.append(f"    vs exponential:  R={vs_exp['R']:+.3f}  p={vs_exp['p']:.4f}  "
                 f"{direction} {sig}")

    vs_ln = r["vs_lognormal"]
    direction = "power_law BETTER" if vs_ln["R"] > 0 else "lognormal BETTER"
    sig = "***" if vs_ln["p"] < 0.01 else ("**" if vs_ln["p"] < 0.05 else "ns")
    lines.append(f"    vs lognormal:    R={vs_ln['R']:+.3f}  p={vs_ln['p']:.4f}  "
                 f"{direction} {sig}")

    return "\n".join(lines)


# ============================================================
# Main experiment
# ============================================================

def run_experiment(n_seeds, max_nodes, mem_bits, out_dir):
    """Run the full C3 experiment."""

    os.makedirs(out_dir, exist_ok=True)
    output_lines = []

    def log(msg=""):
        print(msg)
        output_lines.append(msg)

    log("=" * 70)
    log("PROPER C3 TEST: Scale-Free Topology from Anti-Loop Constraint")
    log("=" * 70)
    log(f"Seeds: {n_seeds}  |  Max nodes: {max_nodes}  |  Memory: {mem_bits}-bit")
    log()

    seeds = list(range(n_seeds))

    # ----------------------------------------------------------
    # Part 1: Main comparison (anti-loop vs growing random control)
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 1: Anti-loop vs growing random graph control")
    log("-" * 70)

    antiloop_alphas = []
    control_alphas = []
    antiloop_results = []
    control_results = []
    example_antiloop_G = None
    example_control_G = None
    example_ba_G = None

    t0_total = time.time()

    for i, seed in enumerate(seeds):
        t0 = time.time()

        # Anti-loop
        G_growth, G_final, glog = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )

        # Growing random control matched to same trajectory
        G_ctrl = build_growing_random_control(glog, seed=seed + 10000)

        r_al = analyze_degree_distribution(G_final, f"antiloop_seed{seed}")
        r_ct = analyze_degree_distribution(G_ctrl, f"control_seed{seed}")

        if r_al["alpha"] is not None:
            antiloop_alphas.append(r_al["alpha"])
            antiloop_results.append(r_al)
        if r_ct["alpha"] is not None:
            control_alphas.append(r_ct["alpha"])
            control_results.append(r_ct)

        elapsed = time.time() - t0
        al_a = f"{r_al['alpha']:.2f}" if r_al["alpha"] else "N/A"
        ct_a = f"{r_ct['alpha']:.2f}" if r_ct["alpha"] else "N/A"
        log(f"  seed {seed:>2}: antiloop alpha={al_a}  control alpha={ct_a}  "
            f"({elapsed:.1f}s)")

        if i == 0:
            example_antiloop_G = G_final
            example_control_G = G_ctrl

    total_time = time.time() - t0_total
    log()

    # Summary statistics
    if antiloop_alphas:
        al_arr = np.array(antiloop_alphas)
        log(f"Anti-loop alpha:  mean={al_arr.mean():.3f}  "
            f"std={al_arr.std():.3f}  "
            f"range=[{al_arr.min():.3f}, {al_arr.max():.3f}]")
    if control_alphas:
        ct_arr = np.array(control_alphas)
        log(f"Control alpha:    mean={ct_arr.mean():.3f}  "
            f"std={ct_arr.std():.3f}  "
            f"range=[{ct_arr.min():.3f}, {ct_arr.max():.3f}]")

    # Barabasi-Albert reference
    ba_G = nx.barabasi_albert_graph(max_nodes, 3, seed=42)
    r_ba = analyze_degree_distribution(ba_G, "barabasi_albert")
    if r_ba["alpha"] is not None:
        log(f"BA reference:     alpha={r_ba['alpha']:.3f}")
    example_ba_G = ba_G

    log(f"\nTotal time: {total_time:.1f}s")
    log()

    # Detailed results for first seed
    if antiloop_results:
        log("Detailed power-law analysis (seed 0):")
        log(format_result(antiloop_results[0]))
        log(format_result(control_results[0]))
        log(format_result(r_ba))
        log()

    # ----------------------------------------------------------
    # Part 2: Sensitivity analysis
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 2: Sensitivity analysis")
    log("-" * 70)

    sensitivity_results = {}

    # 2a: Hash function
    log("\n  Hash function sensitivity:")
    for hf in [HASH_XOR, HASH_SUM, HASH_PRODUCT]:
        alphas = []
        for seed in seeds[:min(10, n_seeds)]:  # use fewer seeds for sensitivity
            _, G, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=hf, pressure_threshold=0.7, spawn_prob=0.3
            )
            r = analyze_degree_distribution(G, f"hash_{hf}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"hash_{hf}"] = arr
        if len(arr):
            log(f"    {hf:>8}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    {hf:>8}: insufficient data")

    # 2b: Pressure threshold
    log("\n  Pressure threshold sensitivity:")
    for thresh in [0.5, 0.6, 0.7, 0.8, 0.9]:
        alphas = []
        for seed in seeds[:min(10, n_seeds)]:
            _, G, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=thresh,
                spawn_prob=0.3
            )
            r = analyze_degree_distribution(G, f"thresh_{thresh}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"thresh_{thresh}"] = arr
        if len(arr):
            log(f"    thresh={thresh}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    thresh={thresh}: insufficient data")

    # 2c: Spawn probability
    log("\n  Spawn probability sensitivity:")
    for sp in [0.1, 0.2, 0.3, 0.5, 0.7]:
        alphas = []
        for seed in seeds[:min(10, n_seeds)]:
            _, G, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
                spawn_prob=sp
            )
            r = analyze_degree_distribution(G, f"spawn_{sp}_s{seed}")
            if r["alpha"] is not None:
                alphas.append(r["alpha"])
        arr = np.array(alphas) if alphas else np.array([])
        sensitivity_results[f"spawn_{sp}"] = arr
        if len(arr):
            log(f"    spawn={sp}: alpha={arr.mean():.3f} +/- {arr.std():.3f}  (n={len(arr)})")
        else:
            log(f"    spawn={sp}: insufficient data")

    log()

    # ----------------------------------------------------------
    # Part 3: Growth phase vs cap phase
    # ----------------------------------------------------------
    log("-" * 70)
    log("PART 3: Growth phase vs cap phase topology")
    log("-" * 70)

    growth_alphas = []
    cap_alphas = []
    for seed in seeds[:min(10, n_seeds)]:
        G_growth, G_final, _ = run_antiloop(
            mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
            seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
            spawn_prob=0.3
        )
        r_gr = analyze_degree_distribution(G_growth, f"growth_s{seed}")
        r_cp = analyze_degree_distribution(G_final, f"cap_s{seed}")
        if r_gr["alpha"] is not None:
            growth_alphas.append(r_gr["alpha"])
        if r_cp["alpha"] is not None:
            cap_alphas.append(r_cp["alpha"])

    if growth_alphas:
        g_arr = np.array(growth_alphas)
        log(f"  Growth phase:  alpha={g_arr.mean():.3f} +/- {g_arr.std():.3f}")
    if cap_alphas:
        c_arr = np.array(cap_alphas)
        log(f"  Cap phase:     alpha={c_arr.mean():.3f} +/- {c_arr.std():.3f}")
    log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------

    # Plot 1: Degree distributions (example, seed 0)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("C3 Test: Degree Distributions (CCDF, log-log)", fontweight="bold")

    for ax, G, label, color in [
        (axes[0], example_antiloop_G, "Anti-loop", "tab:blue"),
        (axes[1], example_control_G, "Growing random control", "tab:gray"),
        (axes[2], example_ba_G, "Barabasi-Albert reference", "tab:red"),
    ]:
        degrees = sorted([d for _, d in G.degree()])
        n = len(degrees)
        unique = sorted(set(degrees))
        ccdf = [sum(1 for x in degrees if x >= d) / n for d in unique]
        ax.loglog(unique, ccdf, "o-", markersize=3, color=color)
        ax.set_xlabel("Degree k")
        ax.set_ylabel("P(K >= k)")
        ax.set_title(label)
        ax.grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_degree_distributions.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 2: Alpha distributions across seeds
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    fig.suptitle("C3 Test: Power-Law Exponent Distribution", fontweight="bold")

    if antiloop_alphas:
        ax.hist(antiloop_alphas, bins=15, alpha=0.6, label="Anti-loop", color="tab:blue")
    if control_alphas:
        ax.hist(control_alphas, bins=15, alpha=0.6, label="Growing random control",
                color="tab:gray")
    if r_ba["alpha"]:
        ax.axvline(r_ba["alpha"], color="tab:red", linestyle="--",
                   label=f"BA ref (alpha={r_ba['alpha']:.2f})")
    ax.axvspan(2, 3, alpha=0.1, color="green", label="Classic scale-free range")
    ax.set_xlabel("alpha")
    ax.set_ylabel("Count")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_powerlaw_fits.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 3: Sensitivity
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("C3 Test: Sensitivity Analysis", fontweight="bold")

    # Hash function
    ax = axes[0]
    hash_labels = []
    hash_means = []
    hash_stds = []
    for hf in [HASH_XOR, HASH_SUM, HASH_PRODUCT]:
        arr = sensitivity_results.get(f"hash_{hf}", np.array([]))
        if len(arr):
            hash_labels.append(hf)
            hash_means.append(arr.mean())
            hash_stds.append(arr.std())
    if hash_labels:
        ax.bar(hash_labels, hash_means, yerr=hash_stds, capsize=5, color="tab:blue",
               alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Hash function")
    ax.grid(True, alpha=0.3)

    # Pressure threshold
    ax = axes[1]
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
    t_means = []
    t_stds = []
    t_labels = []
    for thresh in thresholds:
        arr = sensitivity_results.get(f"thresh_{thresh}", np.array([]))
        if len(arr):
            t_labels.append(str(thresh))
            t_means.append(arr.mean())
            t_stds.append(arr.std())
    if t_labels:
        ax.bar(t_labels, t_means, yerr=t_stds, capsize=5, color="tab:orange",
               alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Loop pressure threshold")
    ax.grid(True, alpha=0.3)

    # Spawn probability
    ax = axes[2]
    spawns = [0.1, 0.2, 0.3, 0.5, 0.7]
    s_means = []
    s_stds = []
    s_labels = []
    for sp in spawns:
        arr = sensitivity_results.get(f"spawn_{sp}", np.array([]))
        if len(arr):
            s_labels.append(str(sp))
            s_means.append(arr.mean())
            s_stds.append(arr.std())
    if s_labels:
        ax.bar(s_labels, s_means, yerr=s_stds, capsize=5, color="tab:green",
               alpha=0.7)
        ax.axhspan(2, 3, alpha=0.1, color="green")
    ax.set_ylabel("alpha")
    ax.set_title("Spawn probability")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "c3_sensitivity.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)

    if antiloop_alphas and control_alphas:
        al_mean = np.mean(antiloop_alphas)
        ct_mean = np.mean(control_alphas)

        in_range = 2.0 <= al_mean <= 3.0
        different = abs(al_mean - ct_mean) > 0.3

        # Check how many antiloop runs had power law preferred over exponential
        n_pl_preferred = sum(
            1 for r in antiloop_results
            if r["vs_exp"] and r["vs_exp"]["R"] > 0 and r["vs_exp"]["p"] < 0.05
        )
        frac_preferred = n_pl_preferred / len(antiloop_results) if antiloop_results else 0

        log(f"Anti-loop mean alpha:  {al_mean:.3f}  (scale-free range: 2-3)")
        log(f"Control mean alpha:    {ct_mean:.3f}")
        log(f"Power law preferred over exponential: "
            f"{n_pl_preferred}/{len(antiloop_results)} "
            f"({frac_preferred*100:.0f}%) of anti-loop runs")
        log()

        if in_range and frac_preferred > 0.5:
            log("RESULT: POSITIVE — Anti-loop constraint produces scale-free-like")
            log("degree distributions with alpha in the classic range.")
            if not different:
                log("WARNING: Control also shows similar alpha. The effect may be")
                log("driven by the growth process, not the anti-loop constraint.")
        else:
            log("RESULT: NEGATIVE or INCONCLUSIVE — Anti-loop constraint does not")
            log("reliably produce classic scale-free topology at this scale.")

        # Hash sensitivity check
        hash_vals = [sensitivity_results.get(f"hash_{h}", np.array([]))
                     for h in [HASH_XOR, HASH_SUM, HASH_PRODUCT]]
        hash_means = [a.mean() for a in hash_vals if len(a)]
        if len(hash_means) >= 2:
            spread = max(hash_means) - min(hash_means)
            if spread > 0.5:
                log(f"\nWARNING: Hash function changes alpha by {spread:.2f}.")
                log("Result is hash-dependent — the specific symmetry of the hash")
                log("matters, not just the anti-loop constraint alone.")
            else:
                log(f"\nHash function robustness: alpha spread = {spread:.2f} (OK)")
    else:
        log("INSUFFICIENT DATA — could not compute verdict.")

    log()

    # Save text results
    with open(os.path.join(out_dir, "c3_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proper C3 scale-free topology test")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test with 3 seeds (for validation)")
    parser.add_argument("--seeds", type=int, default=None,
                        help="Number of seeds (default: 30, or 3 with --quick)")
    parser.add_argument("--nodes", type=int, default=500,
                        help="Max nodes per graph (default: 500)")
    parser.add_argument("--mem", type=int, default=8,
                        help="FSM memory bits (default: 8)")
    args = parser.parse_args()

    n_seeds = args.seeds or (3 if args.quick else 30)
    out_dir = os.path.join(os.path.dirname(__file__), "results")

    run_experiment(n_seeds=n_seeds, max_nodes=args.nodes,
                   mem_bits=args.mem, out_dir=out_dir)
