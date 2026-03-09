"""
Spawn Model Engine
==================

v4 spawn model: pure parent-child tree growth under anti-loop pressure.

Each entity is an FSMNode with bounded memory. When loop pressure exceeds
a threshold, the entity spawns a child. The child starts blank (new random
transition table, own state space). Only parent-child edges exist — no
lateral wiring.

Stepping is vectorized with numpy for performance at scale (10k+ nodes).
GPU acceleration via CuPy is used when available.
"""

import time

import networkx as nx
import numpy as np

# Try to use CuPy for GPU-accelerated table lookups
try:
    import cupy as cp
    HAS_CUDA = True
except ImportError:
    cp = None
    HAS_CUDA = False


class SpawnModel:
    """Vectorized spawn model engine.

    Stores all node data in flat numpy arrays for batch stepping.
    Transition tables are stacked into a single 3D array so that
    all nodes can be stepped in one indexed operation.
    """

    def __init__(self, mem_bits, max_nodes, seed=42):
        self.mem_bits = mem_bits
        self.config_space = 2 ** mem_bits
        self.max_nodes = max_nodes
        self.rng = np.random.default_rng(seed)

        # Pre-allocate arrays for max_nodes
        C = self.config_space
        self.tables = np.zeros((max_nodes, C, C), dtype=np.int32)
        self.configs = np.zeros(max_nodes, dtype=np.int32)
        self.visited_counts = np.zeros(max_nodes, dtype=np.int32)
        self.visited_sets = [None] * max_nodes  # set per node for exact tracking
        self.effective_sets = [None] * max_nodes  # set of (config, hash) pairs
        self.looped = np.zeros(max_nodes, dtype=bool)  # True if effective state revisited
        self.birth_steps = np.zeros(max_nodes, dtype=np.int32)

        # Graph (tree)
        self.G = nx.Graph()
        self.n_nodes = 0

        # Adjacency stored as parent array for tree structure
        self.parent = np.full(max_nodes, -1, dtype=np.int32)
        # Children list per node for computing input hash
        self.children = [[] for _ in range(max_nodes)]

        # GPU arrays (lazily initialized)
        self._gpu_tables = None
        self._use_gpu = False

        # Add the first node
        self._add_node(parent_id=-1, step=0)

    def _add_node(self, parent_id, step):
        """Add a blank child node."""
        nid = self.n_nodes
        C = self.config_space

        self.tables[nid] = self.rng.integers(0, C, size=(C, C), dtype=np.int32)
        self.configs[nid] = self.rng.integers(0, C)
        self.visited_sets[nid] = {int(self.configs[nid])}
        self.effective_sets[nid] = set()
        self.looped[nid] = False
        self.visited_counts[nid] = 1
        self.birth_steps[nid] = step

        self.G.add_node(nid)
        if parent_id >= 0:
            self.G.add_edge(parent_id, nid)
            self.parent[nid] = parent_id
            self.children[parent_id].append(nid)

        self.n_nodes += 1
        self._gpu_tables = None  # invalidate GPU cache
        return nid

    def _init_gpu(self):
        """Upload transition tables to GPU."""
        if HAS_CUDA and self.n_nodes >= 500:  # only worth it at scale
            try:
                self._gpu_tables = cp.asarray(self.tables[:self.n_nodes])
                self._use_gpu = True
            except Exception:
                self._use_gpu = False
        else:
            self._use_gpu = False

    def step_all(self):
        """Step all nodes in one vectorized operation."""
        N = self.n_nodes
        C = self.config_space

        # Compute input hash for each node: XOR of neighbor configs
        hashes = np.zeros(N, dtype=np.int32)
        for nid in range(N):
            h = 0
            p = self.parent[nid]
            if p >= 0:
                h ^= self.configs[p]
            for child in self.children[nid]:
                h ^= self.configs[child]
            hashes[nid] = h % C

        # Batch table lookup: new_config[i] = tables[i, configs[i], hashes[i]]
        cur = self.configs[:N]
        if self._use_gpu and self._gpu_tables is not None:
            cur_gpu = cp.asarray(cur)
            h_gpu = cp.asarray(hashes)
            new_gpu = self._gpu_tables[cp.arange(N), cur_gpu, h_gpu]
            new_configs = cp.asnumpy(new_gpu)
        else:
            new_configs = self.tables[np.arange(N), cur, hashes]

        # Check for effective state revisits BEFORE updating configs
        for nid in range(N):
            eff = (int(self.configs[nid]), int(hashes[nid]))
            if eff in self.effective_sets[nid]:
                self.looped[nid] = True
            else:
                self.effective_sets[nid].add(eff)

        # Update configs and visited sets
        self.configs[:N] = new_configs
        for nid in range(N):
            c = int(new_configs[nid])
            s = self.visited_sets[nid]
            if c not in s:
                s.add(c)
                self.visited_counts[nid] = len(s)

    def get_stressed(self, pressure_threshold):
        """Return list of node IDs that should spawn.

        A node spawns if:
        - It has no connections (sealed entity, forced by A2), OR
        - It has looped (effective state revisited — the v4 definition), OR
        - Its pressure exceeds threshold (approaching saturation)
        """
        N = self.n_nodes
        stressed = []
        for nid in range(N):
            if self.G.degree(nid) == 0:
                stressed.append(nid)
            elif self.looped[nid]:
                stressed.append(nid)
                # Reset loop flag and effective set after spawning
                # (new child changes the input landscape)
                self.looped[nid] = False
                self.effective_sets[nid] = set()
            elif self.visited_counts[nid] / self.config_space > pressure_threshold:
                stressed.append(nid)
        return stressed


def run_spawn_model(mem_bits, max_nodes, seed=42,
                    pressure_threshold=0.4, max_steps=50000,
                    time_limit=None, progress=None):
    """Run v4 spawn model: tree growth under anti-loop pressure.

    Starts from a single entity. Stressed entities spawn children.
    Only parent-child edges. No lateral wiring.

    Args:
        mem_bits: FSM memory size (2^mem_bits states per node)
        max_nodes: stop spawning at this count
        seed: random seed
        pressure_threshold: pressure above which a node spawns
        max_steps: hard step limit
        time_limit: wall-clock seconds limit (None = no limit)
        progress: Progress object for GUI updates (optional)

    Returns:
        G: networkx.Graph (the spawn tree)
        nodes_data: dict with birth_steps, visited_counts, config_space
        growth_log: list of (step, n_nodes) tuples
    """
    model = SpawnModel(mem_bits, max_nodes, seed)
    t_start = time.time()

    growth_log = [(0, 1)]

    for step in range(1, max_steps + 1):
        if time_limit and (time.time() - t_start) > time_limit:
            break

        # Step all nodes
        model.step_all()

        # Spawn children for stressed nodes
        if model.n_nodes < max_nodes:
            stressed = model.get_stressed(pressure_threshold)
            for nid in stressed:
                if model.n_nodes >= max_nodes:
                    break
                model._add_node(parent_id=nid, step=step)

            # Try GPU when we cross the threshold
            if model.n_nodes >= 500 and not model._use_gpu:
                model._init_gpu()

        n_now = model.n_nodes
        growth_log.append((step, n_now))

        if progress and step % 20 == 0:
            elapsed = time.time() - t_start
            progress.update(
                min(n_now, max_nodes), max_nodes,
                "Growing", f"step {step}, {n_now} nodes, {elapsed:.0f}s"
            )

        if n_now >= max_nodes:
            break

    nodes_data = {
        "birth_steps": model.birth_steps[:model.n_nodes].copy(),
        "visited_counts": model.visited_counts[:model.n_nodes].copy(),
        "config_space": model.config_space,
    }

    return model.G, nodes_data, growth_log


def build_random_tree_control(n_nodes, seed):
    """Build a random tree with the same number of nodes.

    Each new node attaches to a uniformly random existing node.
    This is the null model: same tree structure, no anti-loop dynamics.
    """
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    G.add_node(0)

    for i in range(1, n_nodes):
        parent = rng.integers(0, i)
        G.add_node(i)
        G.add_edge(i, parent)

    return G
