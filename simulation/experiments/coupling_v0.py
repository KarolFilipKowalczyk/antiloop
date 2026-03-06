"""
Coupling vs Graph Size - Extrapolation to infinity
Fixed work budget: ~500k transitions per measurement
No growth, no spawning - pure measurement on fixed graphs
"""
import numpy as np
from collections import defaultdict
import time

class Node:
    def __init__(self, cs, rng):
        self.cs = cs
        self.config = rng.integers(0, cs)
        self.table = rng.integers(0, cs, size=(cs, cs))

def measure(num_nodes, mem_bits, avg_degree, seed=42):
    rng = np.random.default_rng(seed)
    cs = 2 ** mem_bits
    
    # Build sparse random graph with target avg degree
    nbs = defaultdict(list)
    for i in range(num_nodes):
        nbs[i]  # ensure exists
    
    # Ring base
    for i in range(num_nodes):
        j = (i + 1) % num_nodes
        nbs[i].append(j)
        nbs[j].append(i)
    
    # Add random edges to reach target degree
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
    
    # Convert to arrays for speed
    nb_arrays = {i: np.array(nbs[i], dtype=np.int32) for i in range(num_nodes)}
    
    nodes = [Node(cs, rng) for _ in range(num_nodes)]
    
    # Fixed work budget: ~500k transitions
    steps = max(20, min(500, 500000 // num_nodes))
    
    total = 0
    changed = 0
    
    for step in range(steps):
        for nid in range(num_nodes):
            node = nodes[nid]
            # Isolated result
            iso = node.table[node.config, 0]
            # Actual with neighbors
            h = 0
            for nb_id in nb_arrays[nid]:
                h ^= nodes[nb_id].config
            h = h % cs
            actual = node.table[node.config, h]
            node.config = actual
            
            total += 1
            if actual != iso:
                changed += 1
    
    return changed / total if total > 0 else 0

# ============================================================
print("COUPLING vs GRAPH SIZE (extrapolation to infinity)")
print("=" * 60)
print(f"Memory: 4-bit (16 configs), Avg degree: 4, XOR hash")
print(f"Work budget: ~500k transitions per measurement")
print()

sizes = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
mem = 4

print(f"{'Nodes':>8} {'Coupling':>10} {'1/Coupling':>10} {'Time':>8}")
print("-" * 40)

data_n = []
data_c = []

for n in sizes:
    t0 = time.time()
    # Average over 3 seeds
    couplings = []
    for s in [42, 123, 456]:
        c = measure(n, mem, avg_degree=4, seed=s)
        couplings.append(c)
    avg_c = np.mean(couplings)
    elapsed = time.time() - t0
    inv = 1/avg_c if avg_c > 0 else float('inf')
    print(f"{n:>8} {avg_c:>10.6f} {inv:>10.4f} {elapsed:>7.1f}s")
    data_n.append(n)
    data_c.append(avg_c)

print()

# Now fit curves and extrapolate
data_n = np.array(data_n, dtype=float)
data_c = np.array(data_c, dtype=float)
data_inv = 1.0 / data_c

print("CURVE FITTING: 1/coupling as function of N")
print("-" * 60)

# Try: 1/coupling = a + b/N (converges to a as N->inf)
# Linear regression on 1/coupling vs 1/N
inv_n = 1.0 / data_n
A = np.vstack([np.ones_like(inv_n), inv_n]).T
result1 = np.linalg.lstsq(A, data_inv, rcond=None)
a_lin, b_lin = result1[0]
residuals1 = np.sum((data_inv - (a_lin + b_lin * inv_n))**2)
print(f"  Model: 1/c = a + b/N")
print(f"  a = {a_lin:.6f}, b = {b_lin:.4f}")
print(f"  Limit as N→∞: 1/coupling → {a_lin:.6f}")
print(f"  Residual: {residuals1:.6f}")
print()

# Try: 1/coupling = a + b/sqrt(N)
sqrt_inv_n = 1.0 / np.sqrt(data_n)
A2 = np.vstack([np.ones_like(sqrt_inv_n), sqrt_inv_n]).T
result2 = np.linalg.lstsq(A2, data_inv, rcond=None)
a_sq, b_sq = result2[0]
residuals2 = np.sum((data_inv - (a_sq + b_sq * sqrt_inv_n))**2)
print(f"  Model: 1/c = a + b/√N")
print(f"  a = {a_sq:.6f}, b = {b_sq:.4f}")
print(f"  Limit as N→∞: 1/coupling → {a_sq:.6f}")
print(f"  Residual: {residuals2:.6f}")
print()

# Try: 1/coupling = a + b*log(N)
log_n = np.log(data_n)
A3 = np.vstack([np.ones_like(log_n), log_n]).T
result3 = np.linalg.lstsq(A3, data_inv, rcond=None)
a_log, b_log = result3[0]
residuals3 = np.sum((data_inv - (a_log + b_log * log_n))**2)
print(f"  Model: 1/c = a + b*ln(N)")
print(f"  a = {a_log:.6f}, b = {b_log:.4f}")
print(f"  At N=10^80: 1/coupling → {a_log + b_log * np.log(1e80):.4f}")
print(f"  Residual: {residuals3:.6f}")
print()

# Try: coupling = a + b/N^c (power law approach to limit)
# Use log-linear fit on (coupling - guess_limit) vs log(N)
# Try with different limit guesses
print("POWER LAW SCAN: coupling = L + b*N^(-c)")
print("-" * 60)
best_fit = None
best_res = float('inf')
for L_guess in np.arange(0.5, 1.0, 0.01):
    delta = data_c - L_guess
    if np.any(delta <= 0):
        continue
    log_delta = np.log(delta)
    log_N = np.log(data_n)
    A4 = np.vstack([np.ones_like(log_N), log_N]).T
    r4 = np.linalg.lstsq(A4, log_delta, rcond=None)
    pred = r4[0][0] + r4[0][1] * log_N
    res = np.sum((log_delta - pred)**2)
    if res < best_res:
        best_res = res
        best_fit = (L_guess, np.exp(r4[0][0]), r4[0][1], res)

if best_fit:
    L, b, c, res = best_fit
    print(f"  Best fit: coupling = {L:.4f} + {b:.4f} * N^({c:.4f})")
    print(f"  Limit as N→∞: coupling → {L:.6f}")
    print(f"  1/Limit → {1/L:.6f}")
    print(f"  Residual: {res:.6f}")

print()
print("=" * 60)
print("COMPARISON TO KNOWN CONSTANTS")
print("=" * 60)
limits = [a_lin, a_sq]
for i, (name, lim) in enumerate([
    ("a + b/N", a_lin),
    ("a + b/√N", a_sq),
]):
    inv_lim = 1/lim if lim > 0 else float('inf')
    # Don't extrapolate log model - it diverges
    print(f"  {name}: limit = {lim:.6f}, 1/limit = {inv_lim:.4f}")

if best_fit:
    print(f"  Power law: limit = {best_fit[0]:.6f}, 1/limit = {1/best_fit[0]:.4f}")

print()
print(f"  Known constants for comparison:")
print(f"    1/α (fine structure) = 137.036")
print(f"    1/e                  = 0.368")
print(f"    1/π                  = 0.318")
print(f"    ln(2)                = 0.693")
print(f"    1/2                  = 0.500")
print(f"    (cs-1)/cs = 15/16   = 0.938  (for 4-bit)")
print()
print("NOTE: If coupling → (cs-1)/cs, it means 'fraction of")
print("inputs that differ from zero', which is trivial. This")
print("would mean coupling is an artifact of the hash function,")
print("not an emergent constant of the graph dynamics.")
