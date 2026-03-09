"""
Antiloop Simulation Engine
==========================

v4 simulation engine: FSM entities under anti-loop pressure.

Each entity is an FSMNode with bounded memory. When loop pressure exceeds
a threshold, the entity acts externally. Two modes:

- **Spawn model** (tree-only): stressed entities spawn children.
  Parent-child edges only. Tests M1 in isolation.

- **LPAN model** (full): stressed entities wire laterally to existing
  entities AND spawn new ones. All entities share an environment
  (Section 2.2 of v4). Tests the full axiom set.

Stepping is vectorized with numpy for performance at scale (10k+ nodes).
GPU acceleration via CuPy is used when available.
"""

import time

import networkx as nx
import numpy as np

# Try to use CuPy for GPU-accelerated table lookups.
# CUDA_PATH must be set BEFORE importing cupy (it caches at import time).
import os
if not os.environ.get("CUDA_PATH"):
    try:
        import nvidia.cuda_nvrtc
        os.environ["CUDA_PATH"] = nvidia.cuda_nvrtc.__path__[0]
    except (ImportError, IndexError, AttributeError):
        pass

try:
    import cupy as cp
    # Validate CuPy can actually compile kernels (not just import)
    _ = cp.arange(2)
    HAS_CUDA = True
except Exception:
    cp = None
    HAS_CUDA = False


class SpawnModel:
    """Vectorized spawn model engine.

    Stores all node data in flat numpy arrays for batch stepping.
    Transition tables are stacked into a single 3D array so that
    all nodes can be stepped in one indexed operation.

    When mem_bits_range is provided, each entity gets a random memory
    size drawn uniformly from [mem_bits_range[0], mem_bits_range[1]].
    Tables are allocated at the max size; smaller entities use a subset.
    """

    def __init__(self, mem_bits, max_nodes, seed=42, mem_bits_range=None,
                 lateral_wiring=False):
        self.mem_bits = mem_bits
        self.config_space = 2 ** mem_bits  # max config space (for allocation)
        self.max_nodes = max_nodes
        self.rng = np.random.default_rng(seed)
        self.mem_bits_range = mem_bits_range  # None = uniform, (lo, hi) = variable
        self.lateral_wiring = lateral_wiring

        # Pre-allocate arrays for max_nodes
        C = self.config_space
        self.tables = np.zeros((max_nodes, C, C), dtype=np.int32)
        self.configs = np.zeros(max_nodes, dtype=np.int32)
        self.visited_counts = np.zeros(max_nodes, dtype=np.int32)
        self.visited_sets = [None] * max_nodes  # set per node for exact tracking
        self.effective_sets = [None] * max_nodes  # set of (config, hash) pairs
        self.looped = np.zeros(max_nodes, dtype=bool)  # True if effective state revisited
        self.birth_steps = np.zeros(max_nodes, dtype=np.int32)
        # Per-node config space (all same if mem_bits_range is None)
        self.node_config_spaces = np.full(max_nodes, C, dtype=np.int32)
        self.node_mem_bits = np.full(max_nodes, mem_bits, dtype=np.int32)

        # Graph
        self.G = nx.Graph()
        self.n_nodes = 0

        # Adjacency stored as parent array for tree structure
        self.parent = np.full(max_nodes, -1, dtype=np.int32)
        # Children list per node (tree edges only)
        self.children = [[] for _ in range(max_nodes)]
        # Neighbor sets for fast hash computation (includes lateral edges)
        self._neighbor_sets = [set() for _ in range(max_nodes)]

        # GPU arrays (lazily initialized)
        self._gpu_tables = None
        self._use_gpu = False

        # Add the first node
        self._add_node(parent_id=-1, step=0)

    def _add_node(self, parent_id, step):
        """Add a blank child node."""
        nid = self.n_nodes

        # Determine this node's memory size
        if self.mem_bits_range is not None:
            lo, hi = self.mem_bits_range
            node_bits = int(self.rng.integers(lo, hi + 1))
        else:
            node_bits = self.mem_bits
        node_C = 2 ** node_bits
        self.node_config_spaces[nid] = node_C
        self.node_mem_bits[nid] = node_bits

        # Fill table within node's config space (rest stays zero)
        C = self.config_space  # max allocation size
        tbl = np.zeros((C, C), dtype=np.int32)
        tbl[:node_C, :node_C] = self.rng.integers(0, node_C,
                                                   size=(node_C, node_C),
                                                   dtype=np.int32)
        self.tables[nid] = tbl
        self.configs[nid] = self.rng.integers(0, node_C)
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
            self._neighbor_sets[parent_id].add(nid)
            self._neighbor_sets[nid].add(parent_id)

        self.n_nodes += 1
        self._gpu_tables = None  # invalidate GPU cache
        return nid

    def add_lateral_edge(self, nid):
        """Add an edge from nid to a random non-neighbor. Returns target or None."""
        current = self._neighbor_sets[nid] | {nid}
        candidates = [n for n in range(self.n_nodes) if n not in current]
        if not candidates:
            return None
        target = int(self.rng.choice(candidates))
        self.G.add_edge(nid, target)
        self._neighbor_sets[nid].add(target)
        self._neighbor_sets[target].add(nid)
        return target

    def _init_gpu(self):
        """Upload transition tables to GPU."""
        if HAS_CUDA and self.n_nodes >= 500:  # only worth it at scale
            try:
                self._gpu_tables = cp.asarray(self.tables[:self.n_nodes])
                self._use_gpu = True
            except Exception:
                self._gpu_tables = None
                self._use_gpu = False
        else:
            self._use_gpu = False

    def step_all(self):
        """Step all nodes in one vectorized operation."""
        N = self.n_nodes
        ncs = self.node_config_spaces[:N]

        # Compute input hash for each node: XOR of neighbor configs
        hashes = np.zeros(N, dtype=np.int32)
        for nid in range(N):
            h = 0
            for nb in self._neighbor_sets[nid]:
                h ^= self.configs[nb]
            hashes[nid] = h % ncs[nid]

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
            elif self.visited_counts[nid] / self.node_config_spaces[nid] > pressure_threshold:
                stressed.append(nid)
        return stressed


def run_spawn_model(mem_bits, max_nodes, seed=42,
                    pressure_threshold=0.4, max_steps=50000,
                    time_limit=None, progress=None,
                    stop_at_max=True, mem_bits_range=None):
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
        stop_at_max: if False, keep stepping after max_nodes (for phase observation)
        mem_bits_range: tuple (lo, hi) for variable memory per entity, or None for uniform

    Returns:
        G: networkx.Graph (the spawn tree)
        nodes_data: dict with birth_steps, visited_counts, config_space, parent, node_mem_bits
        growth_log: list of (step, n_nodes) tuples
    """
    model = SpawnModel(mem_bits, max_nodes, seed, mem_bits_range=mem_bits_range)
    t_start = time.time()

    growth_log = [(0, 1)]
    t_last_update = t_start

    for step in range(1, max_steps + 1):
        now = time.time()
        if time_limit and (now - t_start) > time_limit:
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

        # Update progress at ~10 Hz (every 100ms)
        if progress and (time.time() - t_last_update) >= 0.1:
            progress.update_seed(min(n_now, max_nodes), max_nodes)
            t_last_update = time.time()

        if n_now >= max_nodes:
            if stop_at_max:
                break
            else:
                # Pad growth_log with plateau entries without expensive stepping.
                # The FSM dynamics after saturation produce no new structure.
                plateau_steps = max(step * 2, 200) - step
                for ps in range(1, plateau_steps + 1):
                    growth_log.append((step + ps, n_now))
                break

    nodes_data = {
        "birth_steps": model.birth_steps[:model.n_nodes].copy(),
        "visited_counts": model.visited_counts[:model.n_nodes].copy(),
        "config_space": model.config_space,
        "parent": model.parent[:model.n_nodes].copy(),
        "node_mem_bits": model.node_mem_bits[:model.n_nodes].copy(),
    }

    return model.G, nodes_data, growth_log


def run_lpan_model(mem_bits, max_nodes, seed=42,
                   pressure_threshold=0.7, max_steps=50000,
                   time_limit=None, progress=None,
                   spawn_prob=0.3, post_cap_steps=0,
                   max_wire_per_step=5, mem_bits_range=None,
                   record_trajectories=False):
    """Run LPAN model: growth with lateral wiring under anti-loop pressure.

    All entities share an environment (Section 2.2). Stressed entities
    wire laterally to existing non-neighbors AND sometimes spawn new
    entities.

    DENSITY AND MI EXCESS: The MI excess (edges carry more mutual
    information than non-edges) depends on graph sparsity. At avg
    degree ~8 (post_cap_steps=0), rho ~ 1.15-1.20. At avg degree ~17
    (post_cap_steps=500), rho ~ 1.0 — the excess vanishes because
    non-edges are too close in a dense graph. The default post_cap_steps=0
    produces the sparse regime where MI excess is observable.

    Args:
        mem_bits: FSM memory size (2^mem_bits states per node)
        max_nodes: stop spawning at this count
        seed: random seed
        pressure_threshold: pressure above which a node acts (0.7 matches
            original LPAN; lower values produce earlier/more frequent wiring)
        max_steps: hard step limit
        time_limit: wall-clock seconds limit (None = no limit)
        progress: Progress object for GUI updates (optional)
        spawn_prob: probability a stressed node also spawns (in addition
            to wiring). 0.3 = 30% chance per stressed node per step.
        post_cap_steps: steps to keep running after max_nodes for edge-only
            dynamics. Default 0: all wiring happens during growth. Higher
            values produce denser graphs where MI excess diminishes.
        max_wire_per_step: max stressed nodes that can act per step (5
            matches original LPAN)
        mem_bits_range: tuple (lo, hi) for variable memory, or None for uniform
        record_trajectories: if True, record per-node config at each step
            (needed for MI computation; uses O(nodes * steps) memory)

    Returns:
        G: networkx.Graph (with lateral edges)
        nodes_data: dict with birth_steps, visited_counts, config_space, parent, node_mem_bits
        growth_log: list of (step, n_nodes, n_edges) tuples
        trajectories: dict[node_id -> list[config]] if record_trajectories, else None
    """
    model = SpawnModel(mem_bits, max_nodes, seed,
                       mem_bits_range=mem_bits_range, lateral_wiring=True)
    t_start = time.time()

    growth_log = [(0, 1, 0)]
    t_last_update = t_start
    cap_step = None  # step when we first hit max_nodes
    trajectories = {0: [int(model.configs[0])]} if record_trajectories else None

    for step in range(1, max_steps + 1):
        now = time.time()
        if time_limit and (now - t_start) > time_limit:
            break

        # Stop after enough post-cap steps
        if cap_step is not None and (step - cap_step) >= post_cap_steps:
            break

        # Step all nodes
        model.step_all()

        # Record trajectories
        if record_trajectories:
            for nid in range(model.n_nodes):
                if nid in trajectories:
                    trajectories[nid].append(int(model.configs[nid]))

        # Find stressed nodes, sample subset
        at_cap = model.n_nodes >= max_nodes
        stressed = model.get_stressed(pressure_threshold)
        if len(stressed) > max_wire_per_step:
            stressed = list(model.rng.choice(
                stressed, size=max_wire_per_step, replace=False))

        for nid in stressed:
            # Always try lateral wiring
            model.add_lateral_edge(nid)

            # Sometimes also spawn (only if below cap)
            if not at_cap and model.rng.random() < spawn_prob:
                if model.n_nodes < max_nodes:
                    new_id = model._add_node(parent_id=nid, step=step)
                    if record_trajectories:
                        trajectories[new_id] = [int(model.configs[new_id])]
                    if model.n_nodes >= max_nodes:
                        at_cap = True
                        cap_step = step

        # Try GPU when we cross the threshold
        if model.n_nodes >= 500 and not model._use_gpu:
            model._init_gpu()

        n_now = model.n_nodes
        n_edges = model.G.number_of_edges()
        growth_log.append((step, n_now, n_edges))

        if at_cap and cap_step is None:
            cap_step = step

        # Update progress at ~10 Hz
        if progress and (time.time() - t_last_update) >= 0.1:
            if cap_step is not None:
                # Post-cap: show wiring progress
                wire_done = step - cap_step
                progress.update_seed(wire_done, post_cap_steps,
                                     f"Wiring ({n_edges} edges):")
            else:
                progress.update_seed(min(n_now, max_nodes), max_nodes)
            t_last_update = time.time()

    nodes_data = {
        "birth_steps": model.birth_steps[:model.n_nodes].copy(),
        "visited_counts": model.visited_counts[:model.n_nodes].copy(),
        "config_space": model.config_space,
        "parent": model.parent[:model.n_nodes].copy(),
        "node_mem_bits": model.node_mem_bits[:model.n_nodes].copy(),
    }

    return model.G, nodes_data, growth_log, trajectories


def build_growing_random_control(growth_log, seed):
    """Build a control graph matching the LPAN growth trajectory.

    Same number of nodes and edges at each step, but without
    anti-loop dynamics. Nodes and edges attach randomly.
    """
    rng = np.random.default_rng(seed)

    # Find final state
    final_nodes = growth_log[-1][1]
    final_edges = growth_log[-1][2] if len(growth_log[-1]) > 2 else final_nodes - 1

    G = nx.Graph()
    G.add_node(0)

    # Add nodes
    for i in range(1, final_nodes):
        G.add_node(i)
        parent = rng.integers(0, i)
        G.add_edge(i, parent)

    # Add remaining edges randomly
    attempts = 0
    while G.number_of_edges() < final_edges and attempts < final_edges * 10:
        attempts += 1
        u = int(rng.integers(0, final_nodes))
        v = int(rng.integers(0, final_nodes))
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v)

    return G


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
