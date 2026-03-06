"""
Coupling Constant Experiment
=============================

Measures the fraction of transitions where neighbors change the outcome,
as a function of graph size. Tests whether this ratio converges to
a non-trivial constant.

Result: NEGATIVE. Converges to ~(cs-1)/cs, a combinatorial artifact
of the XOR hash function, not an emergent constant.
"""

import os
import time
from collections import defaultdict

import numpy as np

from simulation.engine import FSMNode, compute_hash, HASH_XOR

TITLE = "Coupling Constant"


def measure(num_nodes, mem_bits, avg_degree, seed=42, hash_fn=HASH_XOR):
    """Measure coupling ratio on a fixed graph.

    Coupling = fraction of transitions where the neighbor-influenced
    result differs from the isolated (zero-input) result.
    """
    rng = np.random.default_rng(seed)
    cs = 2 ** mem_bits

    # Build sparse random graph with target avg degree
    nbs = defaultdict(list)
    for i in range(num_nodes):
        nbs[i]

    # Ring base
    for i in range(num_nodes):
        j = (i + 1) % num_nodes
        nbs[i].append(j)
        nbs[j].append(i)

    # Random edges to reach target degree
    target_edges = int(num_nodes * avg_degree / 2)
    current_edges = num_nodes
    attempts = 0
    while current_edges < target_edges and attempts < target_edges * 5:
        a = rng.integers(0, num_nodes)
        b = rng.integers(0, num_nodes)
        if a != b:
            nbs[a].append(b)
            nbs[b].append(a)
            current_edges += 1
        attempts += 1

    nb_arrays = {i: np.array(nbs[i], dtype=np.int32) for i in range(num_nodes)}

    nodes = [FSMNode(mem_bits, rng) for _ in range(num_nodes)]

    # Fixed work budget: ~500k transitions
    steps = max(20, min(500, 500000 // num_nodes))

    total = 0
    changed = 0

    for s in range(steps):
        for nid in range(num_nodes):
            node = nodes[nid]
            iso = node.table[node.config, 0]
            h = compute_hash([nodes[nb].config for nb in nb_arrays[nid]], hash_fn)
            h = h % cs
            actual = node.table[node.config, h]
            node.config = actual

            total += 1
            if actual != iso:
                changed += 1

    return changed / total if total > 0 else 0


def run(mem_bits=4, out_dir=None, progress=None):
    """Run the coupling constant experiment."""

    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    output_lines = []
    sizes = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    total_work = len(sizes)
    work_done = 0

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    log("COUPLING vs GRAPH SIZE (extrapolation to infinity)")
    log("=" * 60)
    log(f"Memory: {mem_bits}-bit ({2**mem_bits} configs), Avg degree: 4, XOR hash")
    log(f"Work budget: ~500k transitions per measurement")
    log()
    log(f"{'Nodes':>8} {'Coupling':>10} {'1/Coupling':>10} {'Time':>8}")
    log("-" * 40)

    data_n = []
    data_c = []

    for n in sizes:
        t0 = time.time()
        couplings = []
        for s in [42, 123, 456]:
            c = measure(n, mem_bits, avg_degree=4, seed=s)
            couplings.append(c)
        avg_c = np.mean(couplings)
        elapsed = time.time() - t0
        inv = 1 / avg_c if avg_c > 0 else float("inf")
        log(f"{n:>8} {avg_c:>10.6f} {inv:>10.4f} {elapsed:>7.1f}s")
        data_n.append(n)
        data_c.append(avg_c)

        work_done += 1
        if progress:
            progress.update(work_done, total_work, "Measuring coupling", f"N={n}")

    log()

    data_n = np.array(data_n, dtype=float)
    data_c = np.array(data_c, dtype=float)
    data_inv = 1.0 / data_c

    log("CURVE FITTING: 1/coupling as function of N")
    log("-" * 60)

    # 1/coupling = a + b/N
    inv_n = 1.0 / data_n
    A = np.vstack([np.ones_like(inv_n), inv_n]).T
    result1 = np.linalg.lstsq(A, data_inv, rcond=None)
    a_lin, b_lin = result1[0]
    residuals1 = np.sum((data_inv - (a_lin + b_lin * inv_n)) ** 2)
    log(f"  Model: 1/c = a + b/N")
    log(f"  a = {a_lin:.6f}, b = {b_lin:.4f}")
    log(f"  Limit as N->inf: 1/coupling -> {a_lin:.6f}")
    log(f"  Residual: {residuals1:.6f}")
    log()

    # 1/coupling = a + b/sqrt(N)
    sqrt_inv_n = 1.0 / np.sqrt(data_n)
    A2 = np.vstack([np.ones_like(sqrt_inv_n), sqrt_inv_n]).T
    result2 = np.linalg.lstsq(A2, data_inv, rcond=None)
    a_sq, b_sq = result2[0]
    residuals2 = np.sum((data_inv - (a_sq + b_sq * sqrt_inv_n)) ** 2)
    log(f"  Model: 1/c = a + b/sqrt(N)")
    log(f"  a = {a_sq:.6f}, b = {b_sq:.4f}")
    log(f"  Limit as N->inf: 1/coupling -> {a_sq:.6f}")
    log(f"  Residual: {residuals2:.6f}")
    log()

    # Power law scan
    log("POWER LAW SCAN: coupling = L + b*N^(-c)")
    log("-" * 60)
    best_fit = None
    best_res = float("inf")
    for L_guess in np.arange(0.5, 1.0, 0.01):
        delta = data_c - L_guess
        if np.any(delta <= 0):
            continue
        log_delta = np.log(delta)
        log_N = np.log(data_n)
        A4 = np.vstack([np.ones_like(log_N), log_N]).T
        r4 = np.linalg.lstsq(A4, log_delta, rcond=None)
        pred = r4[0][0] + r4[0][1] * log_N
        res = np.sum((log_delta - pred) ** 2)
        if res < best_res:
            best_res = res
            best_fit = (L_guess, np.exp(r4[0][0]), r4[0][1], res)

    if best_fit:
        L, b, c, res = best_fit
        log(f"  Best fit: coupling = {L:.4f} + {b:.4f} * N^({c:.4f})")
        log(f"  Limit as N->inf: coupling -> {L:.6f}")
        log(f"  1/Limit -> {1/L:.6f}")
        log(f"  Residual: {res:.6f}")

    log()
    log("=" * 60)
    log("COMPARISON TO KNOWN CONSTANTS")
    log("=" * 60)
    for name, lim in [("a + b/N", a_lin), ("a + b/sqrt(N)", a_sq)]:
        inv_lim = 1 / lim if lim > 0 else float("inf")
        log(f"  {name}: limit = {lim:.6f}, 1/limit = {inv_lim:.4f}")

    if best_fit:
        log(f"  Power law: limit = {best_fit[0]:.6f}, 1/limit = {1/best_fit[0]:.4f}")

    cs = 2 ** mem_bits
    log()
    log(f"  (cs-1)/cs = {cs-1}/{cs} = {(cs-1)/cs:.3f}  (for {mem_bits}-bit)")
    log()
    log("NOTE: If coupling -> (cs-1)/cs, it means 'fraction of")
    log("inputs that differ from zero', which is trivial. This")
    log("would mean coupling is an artifact of the hash function,")
    log("not an emergent constant of the graph dynamics.")

    with open(os.path.join(out_dir, "coupling_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"\nResults saved to {out_dir}/")
