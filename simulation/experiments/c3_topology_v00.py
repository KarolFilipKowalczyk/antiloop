"""
Non-Looping Existence: Graph Topology Simulation
Fixed version: caps node count at 500 to prevent exponential blowup.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import time

class FSMNode:
    def __init__(self, nid, mem_bits, rng):
        self.config_space = 2 ** mem_bits
        self.config = rng.integers(0, self.config_space)
        self.visited = {self.config}
        self.table = rng.integers(0, self.config_space, size=(self.config_space, self.config_space))
    
    @property
    def pressure(self):
        return len(self.visited) / self.config_space
    
    def step(self, nb_configs):
        h = 0
        for c in nb_configs:
            h ^= c
        h %= self.config_space
        self.config = self.table[self.config, h]
        self.visited.add(self.config)


def run_sim(mem_bits, strategy, max_nodes=500, initial_n=10, seed=42):
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    nodes = {}
    
    for i in range(initial_n):
        G.add_node(i)
        nodes[i] = FSMNode(i, mem_bits, rng)
    for i in range(initial_n):
        G.add_edge(i, (i + 1) % initial_n)
    
    next_id = initial_n
    
    # Run until we hit max_nodes
    step = 0
    while G.number_of_nodes() < max_nodes and step < 5000:
        step += 1
        
        # All nodes step
        node_list = list(G.nodes())
        for nid in node_list:
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb)
        
        # Find stressed nodes
        stressed = [n for n in node_list if nodes[n].pressure > 0.7]
        
        # Limit actions per step to prevent blowup
        if stressed:
            acted = rng.choice(stressed, size=min(5, len(stressed)), replace=False)
        else:
            continue
        
        for nid in acted:
            current_nb = set(G.neighbors(nid)) | {nid}
            candidates = [n for n in G.nodes() if n not in current_nb]
            
            connected = False
            if candidates and G.number_of_nodes() >= max_nodes:
                # At cap: only connect, don't spawn
                if strategy == 'random':
                    target = rng.choice(candidates)
                elif strategy == 'novelty':
                    # Sample to avoid iterating all candidates
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    target = min(sample, key=lambda n: nodes[n].pressure)
                elif strategy == 'degree':
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    degs = np.array([G.degree(n) for n in sample], dtype=float) + 1
                    probs = degs / degs.sum()
                    target = sample[rng.choice(len(sample), p=probs)]
                G.add_edge(nid, target)
                connected = True
            elif candidates:
                # Below cap: connect + maybe spawn
                if strategy == 'random':
                    target = rng.choice(candidates)
                elif strategy == 'novelty':
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    target = min(sample, key=lambda n: nodes[n].pressure)
                elif strategy == 'degree':
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    degs = np.array([G.degree(n) for n in sample], dtype=float) + 1
                    probs = degs / degs.sum()
                    target = sample[rng.choice(len(sample), p=probs)]
                G.add_edge(nid, target)
                connected = True
                
                # Spawn with probability
                if rng.random() < 0.3 and G.number_of_nodes() < max_nodes:
                    G.add_node(next_id)
                    nodes[next_id] = FSMNode(next_id, mem_bits, rng)
                    G.add_edge(nid, next_id)
                    next_id += 1
            
            elif G.number_of_nodes() < max_nodes:
                # No candidates to connect to, must spawn
                G.add_node(next_id)
                nodes[next_id] = FSMNode(next_id, mem_bits, rng)
                G.add_edge(nid, next_id)
                next_id += 1
    
    return G, step


def get_ccdf(G):
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    unique = sorted(set(degrees))
    ccdf = [sum(1 for x in degrees if x >= d) / n for d in unique]
    return unique, ccdf


def fit_alpha(G):
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    degrees = degrees[degrees >= 2]
    if len(degrees) < 10:
        return None
    xmin = 2
    alpha = 1 + len(degrees) / np.sum(np.log(degrees / xmin))
    return alpha


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("ANTI-LOOP GRAPH TOPOLOGY SIMULATION")
print("=" * 60)
print()

strategies = ['random', 'novelty', 'degree']
mem_sizes = [4, 8]
seeds = [42, 123, 456]
MAX_NODES = 500

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(
    'Anti-Loop Graph Growth: Degree Distribution (CCDF, log-log)\n'
    'Straight line = power law = scale-free',
    fontsize=13, fontweight='bold'
)

for row, mem in enumerate(mem_sizes):
    for col, strat in enumerate(strategies):
        ax = axes[row, col]
        print(f"--- {mem}-bit, {strat} strategy ---")
        
        for si, seed in enumerate(seeds):
            t0 = time.time()
            G, steps = run_sim(mem, strat, max_nodes=MAX_NODES, seed=seed)
            elapsed = time.time() - t0
            
            alpha = fit_alpha(G)
            k, ccdf = get_ccdf(G)
            
            a_str = f'{alpha:.2f}' if alpha else 'N/A'
            print(f"  seed={seed}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
                  f"α={a_str}, {steps} steps, {elapsed:.1f}s")
            
            ax.loglog(k, ccdf, 'o-', markersize=3, alpha=0.7,
                     label=f'Anti-loop (α={a_str})')
        
        # One control
        ctrl = nx.gnm_random_graph(MAX_NODES, G.number_of_edges(), seed=42)
        ck, cccdf = get_ccdf(ctrl)
        c_alpha = fit_alpha(ctrl)
        ca_str = f'{c_alpha:.2f}' if c_alpha else 'N/A'
        ax.loglog(ck, cccdf, 's--', markersize=2, alpha=0.4, color='gray',
                 label=f'Random control (α={ca_str})')
        
        # Also Barabasi-Albert as scale-free reference
        ba = nx.barabasi_albert_graph(MAX_NODES, 3, seed=42)
        bk, bccdf = get_ccdf(ba)
        ba_alpha = fit_alpha(ba)
        ba_str = f'{ba_alpha:.2f}' if ba_alpha else 'N/A'
        ax.loglog(bk, bccdf, '^--', markersize=2, alpha=0.4, color='red',
                 label=f'Barabási-Albert ref (α={ba_str})')
        
        ax.set_xlabel('Degree k')
        ax.set_ylabel('P(K ≥ k)')
        ax.set_title(f'{mem}-bit | {strat}')
        ax.legend(fontsize=6.5)
        ax.grid(True, alpha=0.3, which='both')
        print()

plt.tight_layout()
out_path = '/home/claude/results.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"Saved: {out_path}")

# Summary table
print()
print("=" * 60)
print("SUMMARY")
print(f"{'Condition':<20} {'Nodes':>6} {'Edges':>7} {'α':>6} {'Clustering':>10} {'MaxDeg':>7}")
print("-" * 60)

for mem in mem_sizes:
    for strat in strategies:
        G, _ = run_sim(mem, strat, max_nodes=MAX_NODES, seed=42)
        alpha = fit_alpha(G)
        clust = nx.average_clustering(G)
        max_d = max(d for _, d in G.degree())
        a_str = f'{alpha:.2f}' if alpha else 'N/A'
        print(f"{mem}bit_{strat:<12} {G.number_of_nodes():>6} {G.number_of_edges():>7} {a_str:>6} {clust:>10.4f} {max_d:>7}")
    
    # Control line
    ctrl = nx.gnm_random_graph(MAX_NODES, G.number_of_edges(), seed=42)
    c_a = fit_alpha(ctrl)
    c_cl = nx.average_clustering(ctrl)
    c_md = max(d for _, d in ctrl.degree())
    ca_str = f'{c_a:.2f}' if c_a else 'N/A'
    print(f"  control        {ctrl.number_of_nodes():>6} {ctrl.number_of_edges():>7} {ca_str:>6} {c_cl:>10.4f} {c_md:>7}")
    print()

print("α ∈ [2,3] = classic scale-free")
print("Compare anti-loop clustering & max degree vs control")
print("If anti-loop >> control on these metrics: constraint shapes topology")
