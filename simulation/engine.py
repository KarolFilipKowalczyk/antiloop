"""
Antiloop Simulation Engine
==========================

Shared core for all antiloop experiments:
  - FSMNode: finite state machine node with loop pressure tracking
  - Hash functions: XOR, SUM, PRODUCT
  - Graph initialization (ring topology)
  - Anti-loop growth simulation
  - Growing random graph control (matched growth trajectory)
"""

from dataclasses import dataclass, field

import networkx as nx
import numpy as np

# ============================================================
# Hash functions
# ============================================================

HASH_XOR = "xor"
HASH_SUM = "sum"
HASH_PRODUCT = "product"


def compute_hash(configs, hash_fn=HASH_XOR):
    """Compute aggregate hash of neighbor configurations."""
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
# FSM Node
# ============================================================

class FSMNode:
    """Finite state machine node with loop pressure tracking.

    Each node has a configuration space of 2^mem_bits states, a current
    configuration, a set of visited configurations (for pressure), and a
    deterministic transition table indexed by (current_config, input_hash).
    """
    __slots__ = ("config_space", "config", "visited", "table")

    def __init__(self, mem_bits, rng):
        self.config_space = 2 ** mem_bits
        self.config = rng.integers(0, self.config_space)
        self.visited = {self.config}
        self.table = rng.integers(0, self.config_space,
                                  size=(self.config_space, self.config_space))

    @property
    def pressure(self):
        """Loop pressure: fraction of config space already visited."""
        return len(self.visited) / self.config_space

    def step(self, nb_configs, hash_fn=HASH_XOR):
        """Transition based on neighbor configurations."""
        h = compute_hash(nb_configs, hash_fn) % self.config_space
        self.config = self.table[self.config, h]
        self.visited.add(self.config)


# ============================================================
# Growth log
# ============================================================

@dataclass
class GrowthLog:
    """Records (step, n_nodes, n_edges) trajectory for control matching."""
    steps: list = field(default_factory=list)
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)

    def record(self, step, n_nodes, n_edges):
        self.steps.append(step)
        self.nodes.append(n_nodes)
        self.edges.append(n_edges)


# ============================================================
# Graph initialization
# ============================================================

def init_ring_graph(n, mem_bits, rng):
    """Create a ring graph of n FSMNodes.

    Returns:
        G: networkx.Graph
        nodes: dict mapping node_id -> FSMNode
    """
    G = nx.Graph()
    nodes = {}
    for i in range(n):
        G.add_node(i)
        nodes[i] = FSMNode(mem_bits, rng)
    for i in range(n):
        G.add_edge(i, (i + 1) % n)
    return G, nodes


# ============================================================
# Anti-loop growth simulation
# ============================================================

def run_antiloop(mem_bits, max_nodes, initial_n=10, seed=42,
                 hash_fn=HASH_XOR, pressure_threshold=0.7,
                 spawn_prob=0.3, max_stressed_per_step=5,
                 max_steps=10000, record_trajectories=False):
    """Run anti-loop graph growth.

    Args:
        mem_bits: FSM memory size (2^mem_bits configurations per node)
        max_nodes: cap on graph size
        initial_n: starting ring size
        seed: random seed
        hash_fn: HASH_XOR, HASH_SUM, or HASH_PRODUCT
        pressure_threshold: loop pressure above which a node is "stressed"
        spawn_prob: probability a stressed node spawns a new node (below cap)
        max_stressed_per_step: limit on stressed-node actions per step
        max_steps: hard step limit
        record_trajectories: if True, record per-node config at each step

    Returns:
        G_growth: graph snapshot when node cap is first reached
        G_final: graph after additional edge-only steps at cap
        growth_log: GrowthLog trajectory
        trajectories: dict[node_id -> list[config]] if record_trajectories, else None
    """
    rng = np.random.default_rng(seed)
    G, nodes = init_ring_graph(initial_n, mem_bits, rng)

    next_id = initial_n
    growth_log = GrowthLog()
    growth_log.record(0, G.number_of_nodes(), G.number_of_edges())

    trajectories = {} if record_trajectories else None
    if record_trajectories:
        for nid in G.nodes():
            trajectories[nid] = [nodes[nid].config]

    G_growth = None  # snapshot when we first hit cap

    for step in range(1, max_steps + 1):
        # All nodes step
        node_list = list(G.nodes())
        for nid in node_list:
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb, hash_fn)

        if record_trajectories:
            for nid in node_list:
                if nid in trajectories:
                    trajectories[nid].append(nodes[nid].config)

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
                target = rng.choice(candidates)
                G.add_edge(nid, target)

                if not at_cap and rng.random() < spawn_prob:
                    if G.number_of_nodes() < max_nodes:
                        G.add_node(next_id)
                        nodes[next_id] = FSMNode(mem_bits, rng)
                        G.add_edge(nid, next_id)
                        if record_trajectories:
                            trajectories[next_id] = [nodes[next_id].config]
                        next_id += 1
                        if G.number_of_nodes() >= max_nodes:
                            at_cap = True
                            if G_growth is None:
                                G_growth = G.copy()

            elif not at_cap:
                G.add_node(next_id)
                nodes[next_id] = FSMNode(mem_bits, rng)
                G.add_edge(nid, next_id)
                if record_trajectories:
                    trajectories[next_id] = [nodes[next_id].config]
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

    return G_growth, G, growth_log, trajectories


# ============================================================
# Growing random graph control
# ============================================================

def build_growing_random_control(growth_log, seed):
    """Build a control graph matching the anti-loop growth trajectory.

    Same number of nodes and edges at each step, but without any
    anti-loop dynamics. Nodes attach randomly.
    """
    rng = np.random.default_rng(seed)

    n_nodes_seq = growth_log.nodes
    n_edges_seq = growth_log.edges

    G = nx.Graph()
    initial_n = n_nodes_seq[0]
    for i in range(initial_n):
        G.add_node(i)
    for i in range(initial_n):
        G.add_edge(i, (i + 1) % initial_n)

    next_id = initial_n

    for t in range(1, len(n_nodes_seq)):
        target_nodes = n_nodes_seq[t]
        target_edges = n_edges_seq[t]

        while G.number_of_nodes() < target_nodes:
            G.add_node(next_id)
            if G.number_of_nodes() > 1:
                target_node = rng.choice(list(G.nodes()))
                G.add_edge(next_id, target_node)
            next_id += 1

        attempts = 0
        while G.number_of_edges() < target_edges and attempts < 500:
            attempts += 1
            node_list = list(G.nodes())
            u = rng.choice(node_list)
            v = rng.choice(node_list)
            if u != v and not G.has_edge(u, v):
                G.add_edge(u, v)

    return G
