"""
O9v2 Spectral Analysis: Graph-Level Observables
=================================================

Revised O9 experiment. Tests whether anti-loop growth dynamics produce
1/f (pink noise) power spectra in graph-level collective observables.

O9v1 failed because:
  1. Per-node config values are arbitrary integers (metrically meaningless)
  2. Analysis was done post-growth on a frozen graph (discarding the interesting dynamics)
  3. Uniform random noise is too crude

O9v2 fixes:
  - Measures graph-level observables DURING growth (novelty rate, pressure, edges, entropy)
  - Uses mathematically natural noise (table mutation, neighbor dropout)
  - Compares anti-loop to growing random control

Uses GPU (PyTorch CUDA) for batch FFT when available.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from simulation.engine import (
    FSMNode, compute_hash, init_ring_graph, GrowthLog, HASH_XOR,
    run_antiloop,
)

TITLE = "O9v2 Spectral Analysis"

OBSERVABLE_NAMES = [
    "global_novelty_rate",
    "mean_pressure",
    "pressure_variance",
    "edge_rate",
    "degree_entropy",
]

NOISE_CONDITIONS = [
    {"name": "none",          "noise_type": "none",        "noise_rate": 0.0},
    {"name": "temp_0.1",      "noise_type": "temperature", "noise_rate": 0.1},
    {"name": "temp_0.5",      "noise_type": "temperature", "noise_rate": 0.5},
    {"name": "mutation_0.01", "noise_type": "mutation",    "noise_rate": 0.01},
    {"name": "mutation_0.1",  "noise_type": "mutation",    "noise_rate": 0.1},
    {"name": "dropout_0.1",   "noise_type": "dropout",     "noise_rate": 0.1},
    {"name": "dropout_0.3",   "noise_type": "dropout",     "noise_rate": 0.3},
]


# ============================================================
# PSD computation (reused from O9v1)
# ============================================================

def _get_device():
    if HAS_TORCH and torch.cuda.is_available():
        return torch.device("cuda")
    return None


def compute_psd_gpu(signal_array, device):
    """Compute PSD using GPU FFT.

    Args:
        signal_array: numpy array (n_signals, n_steps) or (1, n_steps)
        device: torch.device
    """
    t = torch.tensor(signal_array, dtype=torch.float32, device=device)
    t = t - t.mean(dim=1, keepdim=True)
    fft = torch.fft.rfft(t, dim=1)
    psd = (fft.abs() ** 2).cpu().numpy()
    avg_psd = psd.mean(axis=0)
    freqs = np.fft.rfftfreq(signal_array.shape[1])
    return freqs, avg_psd


def compute_psd_cpu(signal_array):
    """Compute PSD using numpy FFT."""
    centered = signal_array - signal_array.mean(axis=1, keepdims=True)
    fft = np.fft.rfft(centered, axis=1)
    psd = np.abs(fft) ** 2
    avg_psd = psd.mean(axis=0)
    freqs = np.fft.rfftfreq(signal_array.shape[1])
    return freqs, avg_psd


def compute_psd(signal_array, device=None):
    """Compute PSD using GPU if available, else CPU."""
    if device is not None:
        return compute_psd_gpu(signal_array, device)
    return compute_psd_cpu(signal_array)


def fit_beta(freqs, psd):
    """Fit spectral exponent: PSD ~ f^(-beta).

    Returns (beta, r_squared).
    """
    mask = freqs > 0
    f = freqs[mask]
    p = psd[mask]

    n_keep = max(5, int(len(f) * 0.9))
    f = f[:n_keep]
    p = p[:n_keep]

    valid = p > 0
    if valid.sum() < 5:
        return 0.0, 0.0

    log_f = np.log10(f[valid])
    log_p = np.log10(p[valid])

    coeffs = np.polyfit(log_f, log_p, 1)
    beta = -coeffs[0]

    predicted = np.polyval(coeffs, log_f)
    ss_res = np.sum((log_p - predicted) ** 2)
    ss_tot = np.sum((log_p - log_p.mean()) ** 2)
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return beta, r_sq


# ============================================================
# Validation
# ============================================================

def generate_colored_noise(beta, n_samples, rng):
    """Generate noise with known spectral exponent."""
    freqs = np.fft.rfftfreq(n_samples)
    freqs[0] = 1.0
    amplitudes = freqs ** (-beta / 2.0)
    phases = rng.uniform(0, 2 * np.pi, size=len(freqs))
    spectrum = amplitudes * np.exp(1j * phases)
    spectrum[0] = 0
    return np.fft.irfft(spectrum, n=n_samples)


def validate_fitting(log, device, n_samples=5000):
    """Verify fitting recovers known exponents."""
    log("Validation: fitting procedure on synthetic signals")
    rng = np.random.default_rng(42)

    for true_beta in [0.0, 0.5, 1.0, 1.5, 2.0]:
        signals = np.array([generate_colored_noise(true_beta, n_samples, rng)
                            for _ in range(100)])
        freqs, avg_psd = compute_psd(signals, device)
        measured_beta, r_sq = fit_beta(freqs, avg_psd)
        err = abs(measured_beta - true_beta)
        status = "OK" if err < 0.15 else "WARN"
        log(f"  true beta={true_beta:.1f}  measured={measured_beta:.2f}  "
            f"R^2={r_sq:.3f}  err={err:.2f}  [{status}]")

    log()


# ============================================================
# Noise models
# ============================================================

def apply_table_mutation(nodes, mutation_rate, rng):
    """Mutate random transition table entries.

    For each node, with probability mutation_rate, pick a random
    (config, input) entry and replace the output with a random value.
    Structural noise: the rules change, not the state.
    """
    for node in nodes.values():
        if rng.random() < mutation_rate:
            row = rng.integers(0, node.config_space)
            col = rng.integers(0, node.config_space)
            node.table[row, col] = rng.integers(0, node.config_space)


def compute_hash_with_dropout(nb_configs, hash_fn, dropout_rate, rng):
    """Compute hash with independent neighbor dropout.

    Each neighbor is excluded with probability dropout_rate.
    Topology noise: the node doesn't hear all its neighbors.
    """
    if not nb_configs:
        return 0
    kept = [c for c in nb_configs if rng.random() >= dropout_rate]
    if not kept:
        return 0
    return compute_hash(kept, hash_fn)


# ============================================================
# Observable recorder
# ============================================================

def compute_degree_entropy(G):
    """Shannon entropy of the degree distribution."""
    degrees = np.array([d for _, d in G.degree()], dtype=int)
    if len(degrees) == 0:
        return 0.0
    counts = np.bincount(degrees)
    counts = counts[counts > 0]
    probs = counts / counts.sum()
    return -np.sum(probs * np.log2(probs))


class ObservableRecorder:
    """Records graph-level observables at each step."""

    def __init__(self):
        self.global_novelty_rate = []
        self.mean_pressure = []
        self.pressure_variance = []
        self.edge_rate = []
        self.degree_entropy = []

    def record(self, G, nodes, prev_visited_counts, edges_added):
        """Record all observables for this timestep."""
        n_novel = 0
        n_total = 0
        for nid, node in nodes.items():
            if nid in prev_visited_counts:
                if len(node.visited) > prev_visited_counts[nid]:
                    n_novel += 1
                n_total += 1
        self.global_novelty_rate.append(n_novel / max(n_total, 1))

        pressures = np.array([node.pressure for node in nodes.values()])
        self.mean_pressure.append(float(pressures.mean()))
        self.pressure_variance.append(float(pressures.var()))

        self.edge_rate.append(float(edges_added))
        self.degree_entropy.append(compute_degree_entropy(G))

    def to_arrays(self):
        return {
            "global_novelty_rate": np.array(self.global_novelty_rate),
            "mean_pressure": np.array(self.mean_pressure),
            "pressure_variance": np.array(self.pressure_variance),
            "edge_rate": np.array(self.edge_rate),
            "degree_entropy": np.array(self.degree_entropy),
        }


# ============================================================
# Detrending
# ============================================================

def detrend_signal(ts):
    """Remove linear trend from time series."""
    n = len(ts)
    if n < 3:
        return ts
    x = np.arange(n, dtype=float)
    coeffs = np.polyfit(x, ts, 1)
    return ts - np.polyval(coeffs, x)


# ============================================================
# Core simulation with observable recording
# ============================================================

def run_antiloop_with_observables(
    mem_bits, max_nodes, initial_n, seed, hash_fn,
    pressure_threshold, spawn_prob, max_stressed_per_step,
    max_steps=None, time_budget=None,
    noise_type="none", noise_rate=0.0
):
    """Run anti-loop growth recording graph-level observables.

    Reimplements engine.run_antiloop growth logic with:
    - Observable recording at every step
    - Support for mutation and dropout noise
    - Time-budgeted or step-limited run

    Either max_steps or time_budget must be provided.
    If time_budget is set, runs as many steps as fit in that many seconds.

    Returns (G, growth_log, observables_dict).
    """
    if max_steps is None and time_budget is None:
        max_steps = 5000

    rng = np.random.default_rng(seed)
    G, nodes = init_ring_graph(initial_n, mem_bits, rng)

    next_id = initial_n
    growth_log = GrowthLog()
    growth_log.record(0, G.number_of_nodes(), G.number_of_edges())
    recorder = ObservableRecorder()

    t_start = time.time()
    step_num = 0
    while True:
        step_num += 1
        if max_steps is not None and step_num > max_steps:
            break
        if time_budget is not None and step_num > 1:
            if time.time() - t_start >= time_budget:
                break
        prev_visited = {nid: len(nodes[nid].visited) for nid in G.nodes()}

        # Table mutation noise (before stepping)
        if noise_type == "mutation" and noise_rate > 0:
            apply_table_mutation(nodes, noise_rate, rng)

        # All nodes step
        node_list = list(G.nodes())
        for nid in node_list:
            nb_configs = [nodes[n].config for n in G.neighbors(nid)]

            if noise_type == "dropout" and noise_rate > 0:
                h = compute_hash_with_dropout(
                    nb_configs, hash_fn, noise_rate, rng
                ) % nodes[nid].config_space
                new_config = nodes[nid].table[nodes[nid].config, h]
                nodes[nid].config = new_config
                nodes[nid].visited.add(new_config)
            elif noise_type == "temperature" and noise_rate > 0:
                nodes[nid].step(nb_configs, hash_fn,
                                temperature=noise_rate, rng=rng)
            else:
                nodes[nid].step(nb_configs, hash_fn)

        # Growth logic (matches engine.run_antiloop)
        edges_before = G.number_of_edges()

        stressed = [n for n in node_list if nodes[n].pressure > pressure_threshold]
        if stressed:
            acted = rng.choice(
                stressed,
                size=min(max_stressed_per_step, len(stressed)),
                replace=False
            )
            at_cap = G.number_of_nodes() >= max_nodes

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
                            prev_visited[next_id] = 0
                            next_id += 1
                            if G.number_of_nodes() >= max_nodes:
                                at_cap = True
                elif not at_cap:
                    G.add_node(next_id)
                    nodes[next_id] = FSMNode(mem_bits, rng)
                    G.add_edge(nid, next_id)
                    prev_visited[next_id] = 0
                    next_id += 1
                    if G.number_of_nodes() >= max_nodes:
                        at_cap = True

        edges_added = G.number_of_edges() - edges_before

        recorder.record(G, nodes, prev_visited, edges_added)
        growth_log.record(step_num, G.number_of_nodes(), G.number_of_edges())

    return G, growth_log, recorder.to_arrays()


# ============================================================
# Control: growing random graph with observables
# ============================================================

def run_growing_random_with_observables(
    growth_log, seed, mem_bits, hash_fn=HASH_XOR,
    noise_type="none", noise_rate=0.0
):
    """Growing random graph with matched trajectory, collecting observables.

    Same node/edge counts as anti-loop at each step, but edges attach
    randomly. FSM nodes run on the topology for comparable measurement.
    """
    rng = np.random.default_rng(seed)

    initial_n = growth_log.nodes[0]
    G, nodes = init_ring_graph(initial_n, mem_bits, rng)
    next_id = initial_n
    recorder = ObservableRecorder()
    n_steps = len(growth_log.steps) - 1

    for t in range(1, n_steps + 1):
        prev_visited = {nid: len(nodes[nid].visited) for nid in G.nodes()}

        if noise_type == "mutation" and noise_rate > 0:
            apply_table_mutation(nodes, noise_rate, rng)

        node_list = list(G.nodes())
        for nid in node_list:
            nb_configs = [nodes[n].config for n in G.neighbors(nid)]
            if noise_type == "dropout" and noise_rate > 0:
                h = compute_hash_with_dropout(
                    nb_configs, hash_fn, noise_rate, rng
                ) % nodes[nid].config_space
                new_config = nodes[nid].table[nodes[nid].config, h]
                nodes[nid].config = new_config
                nodes[nid].visited.add(new_config)
            elif noise_type == "temperature" and noise_rate > 0:
                nodes[nid].step(nb_configs, hash_fn,
                                temperature=noise_rate, rng=rng)
            else:
                nodes[nid].step(nb_configs, hash_fn)

        # Match growth trajectory randomly
        edges_before = G.number_of_edges()

        if t < len(growth_log.nodes):
            target_nodes = growth_log.nodes[t]
            target_edges = growth_log.edges[t]

            while G.number_of_nodes() < target_nodes:
                G.add_node(next_id)
                nodes[next_id] = FSMNode(mem_bits, rng)
                if G.number_of_nodes() > 1:
                    target_node = rng.choice(list(G.nodes()))
                    G.add_edge(next_id, target_node)
                prev_visited[next_id] = 0
                next_id += 1

            attempts = 0
            while G.number_of_edges() < target_edges and attempts < 500:
                attempts += 1
                nl = list(G.nodes())
                u = rng.choice(nl)
                v = rng.choice(nl)
                if u != v and not G.has_edge(u, v):
                    G.add_edge(u, v)

        edges_added = G.number_of_edges() - edges_before
        recorder.record(G, nodes, prev_visited, edges_added)

    return recorder.to_arrays()


# ============================================================
# Consistency check
# ============================================================

def check_consistency(log, mem_bits, max_nodes, max_steps, seed=42):
    """Verify growth matches engine.run_antiloop with same parameters."""
    log("Consistency check: comparing growth trajectories...")

    _, _, engine_log, _ = run_antiloop(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, max_stressed_per_step=5,
        max_steps=max_steps, record_trajectories=False, temperature=0.0
    )

    _, our_log, _ = run_antiloop_with_observables(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, max_stressed_per_step=5,
        max_steps=max_steps, noise_type="none", noise_rate=0.0
    )

    # Compare growth logs (truncate to shorter)
    n = min(len(engine_log.nodes), len(our_log.nodes))
    nodes_match = engine_log.nodes[:n] == our_log.nodes[:n]
    edges_match = engine_log.edges[:n] == our_log.edges[:n]

    if nodes_match and edges_match:
        log(f"  PASS: growth trajectories match ({n} steps)")
    else:
        # Find first divergence
        for i in range(n):
            if engine_log.nodes[i] != our_log.nodes[i] or engine_log.edges[i] != our_log.edges[i]:
                log(f"  FAIL: diverged at step {i}: engine=({engine_log.nodes[i]},{engine_log.edges[i]}) "
                    f"vs ours=({our_log.nodes[i]},{our_log.edges[i]})")
                break
    log()


# ============================================================
# Main experiment
# ============================================================

def run(n_seeds=10, max_nodes=200, mem_bits=8, time_budget=300,
        noise_conditions=None, out_dir=None, progress=None):
    """Run the O9v2 spectral analysis experiment.

    Args:
        time_budget: total wall-clock seconds for the experiment.
            The first run calibrates steps/second, then all subsequent
            runs use the calibrated step count. Default 300s (5 min).
    """

    if noise_conditions is None:
        noise_conditions = NOISE_CONDITIONS
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    output_lines = []
    total_work = len(noise_conditions) * n_seeds
    work_done = 0
    device = _get_device()

    def step(phase, status):
        nonlocal work_done
        work_done += 1
        if progress:
            progress.update(work_done, total_work, phase, status)

    def log(msg=""):
        output_lines.append(msg)
        if progress:
            progress.log(msg)
        else:
            print(msg)

    # ----------------------------------------------------------
    # Calibration: run one antiloop sim with time budget to find
    # how many steps we can do per unit of time, then fix step
    # count for all remaining runs.
    # ----------------------------------------------------------
    n_runs = len(noise_conditions) * n_seeds  # antiloop runs (control reuses growth_log length)
    # Reserve 10% of budget for validation, consistency, plotting
    sim_budget = time_budget * 0.90
    # Each "work unit" = 1 antiloop run + 1 control run (~2x time of antiloop alone)
    time_per_antiloop = sim_budget / (n_runs * 2.0)
    time_per_antiloop = max(time_per_antiloop, 1.0)  # at least 1 second

    log("=" * 70)
    log("O9v2: Graph-Level Spectral Analysis of Anti-Loop Growth")
    log("=" * 70)
    log(f"Seeds: {n_seeds}  |  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit")
    log(f"Time budget: {time_budget}s  |  Per-run budget: {time_per_antiloop:.1f}s")
    log(f"Noise conditions: {[nc['name'] for nc in noise_conditions]}")
    log(f"Observables: {OBSERVABLE_NAMES}")
    log(f"Device: {device if device else 'CPU (numpy)'}")
    log()

    # Calibration run: time-budgeted first run to discover step count
    log("Calibrating steps/second...")
    t_cal = time.time()
    _, cal_log, _ = run_antiloop_with_observables(
        mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
        seed=999, hash_fn=HASH_XOR, pressure_threshold=0.7,
        spawn_prob=0.3, max_stressed_per_step=5,
        time_budget=time_per_antiloop,
        noise_type="none", noise_rate=0.0
    )
    cal_elapsed = time.time() - t_cal
    cal_steps = len(cal_log.steps) - 1
    steps_per_sec = cal_steps / max(cal_elapsed, 0.01)
    # Use calibrated step count for all runs (consistent across conditions)
    max_steps = max(100, cal_steps)
    log(f"  {cal_steps} steps in {cal_elapsed:.1f}s ({steps_per_sec:.0f} steps/s)")
    log(f"  Using {max_steps} steps for all runs")
    log()

    # ----------------------------------------------------------
    # Validation
    # ----------------------------------------------------------
    validate_fitting(log, device, n_samples=max(max_steps, 500))

    # ----------------------------------------------------------
    # Consistency check (use small step count to be fast)
    # ----------------------------------------------------------
    check_consistency(log, mem_bits, max_nodes, max_steps=min(max_steps, 500))

    # ----------------------------------------------------------
    # Main sweep: noise_condition x seeds
    # ----------------------------------------------------------
    log("-" * 70)
    log("SWEEP: noise conditions x seeds")
    log("-" * 70)

    # results[noise_name][obs_name] = list of (beta, r_sq) across seeds
    # detrended_results[...] = same but with linear detrending
    results = {nc["name"]: {obs: [] for obs in OBSERVABLE_NAMES}
               for nc in noise_conditions}
    detrended_results = {nc["name"]: {obs: [] for obs in OBSERVABLE_NAMES}
                         for nc in noise_conditions}
    ctrl_results = {nc["name"]: {obs: [] for obs in OBSERVABLE_NAMES}
                    for nc in noise_conditions}
    ctrl_detrended = {nc["name"]: {obs: [] for obs in OBSERVABLE_NAMES}
                      for nc in noise_conditions}

    example_timeseries = None
    example_psds = {}
    t0_total = time.time()

    for nc in noise_conditions:
        nc_name = nc["name"]
        for i in range(n_seeds):
            seed = i
            t0 = time.time()

            # Anti-loop run (fixed step count from calibration)
            G, growth_log, observables = run_antiloop_with_observables(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
                spawn_prob=0.3, max_stressed_per_step=5,
                max_steps=max_steps,
                noise_type=nc["noise_type"], noise_rate=nc["noise_rate"]
            )

            # Control run (follows growth_log length)
            ctrl_observables = run_growing_random_with_observables(
                growth_log, seed=seed + 10000, mem_bits=mem_bits,
                noise_type=nc["noise_type"], noise_rate=nc["noise_rate"]
            )

            # Compute PSD for each observable
            for obs_name in OBSERVABLE_NAMES:
                ts = observables[obs_name]
                if len(ts) < 50:
                    continue

                arr = ts.reshape(1, -1).astype(np.float64)

                # Raw PSD
                freqs, avg_psd = compute_psd(arr, device)
                beta, r_sq = fit_beta(freqs, avg_psd)
                results[nc_name][obs_name].append((beta, r_sq))

                # Detrended PSD
                dt_arr = detrend_signal(ts).reshape(1, -1)
                dt_freqs, dt_psd = compute_psd(dt_arr, device)
                dt_beta, dt_r_sq = fit_beta(dt_freqs, dt_psd)
                detrended_results[nc_name][obs_name].append((dt_beta, dt_r_sq))

                # Control
                ctrl_ts = ctrl_observables.get(obs_name)
                if ctrl_ts is not None and len(ctrl_ts) >= 50:
                    min_len = min(len(ts), len(ctrl_ts))
                    c_arr = ctrl_ts[:min_len].reshape(1, -1).astype(np.float64)
                    c_freqs, c_psd = compute_psd(c_arr, device)
                    c_beta, c_r_sq = fit_beta(c_freqs, c_psd)
                    ctrl_results[nc_name][obs_name].append((c_beta, c_r_sq))

                    c_dt_arr = detrend_signal(ctrl_ts[:min_len]).reshape(1, -1)
                    c_dt_freqs, c_dt_psd = compute_psd(c_dt_arr, device)
                    c_dt_beta, c_dt_r_sq = fit_beta(c_dt_freqs, c_dt_psd)
                    ctrl_detrended[nc_name][obs_name].append((c_dt_beta, c_dt_r_sq))

                    # Save example data for plotting
                    if nc_name == "none" and i == 0:
                        example_psds[obs_name] = {
                            "antiloop": (freqs, avg_psd, beta),
                            "control": (c_freqs, c_psd, c_beta),
                        }

            # Save example timeseries (no-noise, seed 0)
            if nc_name == "none" and i == 0:
                example_timeseries = observables

            elapsed = time.time() - t0
            step(f"Noise: {nc_name}",
                 f"seed {i+1}/{n_seeds} ({elapsed:.1f}s)")

        # Per-condition summary line
        parts = []
        for obs_name in OBSERVABLE_NAMES:
            betas = [b for b, _ in detrended_results[nc_name][obs_name]]
            if betas:
                parts.append(f"{obs_name[:8]}={np.mean(betas):.2f}")
        log(f"  {nc_name}: " + "  ".join(parts))

    total_time = time.time() - t0_total
    log(f"\nTotal time: {total_time:.1f}s")
    log()

    # ----------------------------------------------------------
    # Summary tables
    # ----------------------------------------------------------
    for label, res in [("ANTI-LOOP (detrended)", detrended_results),
                       ("CONTROL (detrended)", ctrl_detrended)]:
        log("-" * 70)
        log(f"SUMMARY: {label}")
        log("-" * 70)

        # Header
        header = f"{'Noise':>14}"
        for obs in OBSERVABLE_NAMES:
            header += f"  {obs[:12]:>12}"
        log(header)
        log("-" * (14 + 14 * len(OBSERVABLE_NAMES)))

        for nc in noise_conditions:
            row = f"{nc['name']:>14}"
            for obs in OBSERVABLE_NAMES:
                betas = [b for b, _ in res[nc["name"]][obs]]
                if betas:
                    row += f"  {np.mean(betas):>5.2f}+/-{np.std(betas):.2f}"
                else:
                    row += f"  {'N/A':>12}"
            log(row)
        log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------

    # Plot 1: Beta by observable (grouped bars, anti-loop vs control)
    fig, axes = plt.subplots(len(OBSERVABLE_NAMES), 1, figsize=(12, 3 * len(OBSERVABLE_NAMES)),
                             sharex=True)
    fig.suptitle("O9v2: Spectral Exponent by Observable and Noise Condition",
                 fontweight="bold", fontsize=13)

    nc_names = [nc["name"] for nc in noise_conditions]
    x = np.arange(len(nc_names))
    bar_width = 0.35

    for idx, obs in enumerate(OBSERVABLE_NAMES):
        ax = axes[idx]

        # Anti-loop betas
        al_means = []
        al_stds = []
        for nc_name in nc_names:
            betas = [b for b, _ in detrended_results[nc_name][obs]]
            al_means.append(np.mean(betas) if betas else 0)
            al_stds.append(np.std(betas) if betas else 0)

        # Control betas
        ct_means = []
        ct_stds = []
        for nc_name in nc_names:
            betas = [b for b, _ in ctrl_detrended[nc_name][obs]]
            ct_means.append(np.mean(betas) if betas else 0)
            ct_stds.append(np.std(betas) if betas else 0)

        ax.bar(x - bar_width / 2, al_means, bar_width, yerr=al_stds,
               color="tab:blue", alpha=0.8, capsize=3, label="Anti-loop")
        ax.bar(x + bar_width / 2, ct_means, bar_width, yerr=ct_stds,
               color="tab:gray", alpha=0.6, capsize=3, label="Control")

        ax.axhline(y=1.0, color="tab:red", linestyle="--", alpha=0.5)
        ax.axhline(y=0.0, color="black", linestyle=":", alpha=0.3)
        ax.set_ylabel("beta")
        ax.set_title(obs, fontsize=10)
        ax.grid(True, alpha=0.2)
        if idx == 0:
            ax.legend(fontsize=8)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(nc_names, rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "o9v2_beta_by_observable.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 2: Example time series (no-noise, seed 0)
    if example_timeseries is not None:
        fig, axes = plt.subplots(len(OBSERVABLE_NAMES), 1,
                                 figsize=(12, 2.5 * len(OBSERVABLE_NAMES)),
                                 sharex=True)
        fig.suptitle("O9v2: Observable Time Series (no noise, seed 0)",
                     fontweight="bold", fontsize=13)

        for idx, obs in enumerate(OBSERVABLE_NAMES):
            ax = axes[idx]
            ts = example_timeseries[obs]
            ax.plot(ts, linewidth=0.5, color="tab:blue", alpha=0.8)
            ax.set_ylabel(obs[:15], fontsize=9)
            ax.grid(True, alpha=0.2)

        axes[-1].set_xlabel("Step")
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "o9v2_example_timeseries.png"),
                    dpi=150, bbox_inches="tight")
        plt.close()

    # Plot 3: PSD comparison (most interesting observable)
    if example_psds:
        # Pick observable with beta closest to 1
        best_obs = None
        best_dist = float("inf")
        for obs, data in example_psds.items():
            dist = abs(data["antiloop"][2] - 1.0)
            if dist < best_dist:
                best_dist = dist
                best_obs = obs

        if best_obs:
            fig, ax = plt.subplots(1, 1, figsize=(8, 5))
            al_data = example_psds[best_obs]["antiloop"]
            ct_data = example_psds[best_obs]["control"]

            mask_al = al_data[0] > 0
            mask_ct = ct_data[0] > 0

            ax.loglog(al_data[0][mask_al], al_data[1][mask_al], "-",
                      color="tab:blue", alpha=0.8, linewidth=1.5,
                      label=f"Anti-loop (beta={al_data[2]:.2f})")
            ax.loglog(ct_data[0][mask_ct], ct_data[1][mask_ct], "-",
                      color="tab:gray", alpha=0.6, linewidth=1.5,
                      label=f"Control (beta={ct_data[2]:.2f})")

            # Reference slopes
            f_ref = np.logspace(-3, -0.5, 50)
            for ref_beta, ls, lbl in [(0, ":", "white"), (1, "--", "1/f"), (2, "-.", "1/f^2")]:
                scale = al_data[1][mask_al][len(al_data[1][mask_al]) // 4]
                f_mid = al_data[0][mask_al][len(al_data[0][mask_al]) // 4]
                ref_psd = scale * (f_ref / f_mid) ** (-ref_beta)
                ax.loglog(f_ref, ref_psd, ls, color="tab:red", alpha=0.3,
                          label=f"beta={ref_beta} ({lbl})")

            ax.set_xlabel("Frequency")
            ax.set_ylabel("Power Spectral Density")
            ax.set_title(f"O9v2: PSD Comparison — {best_obs}", fontweight="bold")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.2, which="both")

            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, "o9v2_psd_comparison.png"),
                        dpi=150, bbox_inches="tight")
            plt.close()

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)

    best_finding = None
    best_score = -1  # higher = more interesting

    for obs in OBSERVABLE_NAMES:
        log(f"\n  {obs}:")
        for nc in noise_conditions:
            nc_name = nc["name"]
            al_betas = [b for b, _ in detrended_results[nc_name][obs]]
            ct_betas = [b for b, _ in ctrl_detrended[nc_name][obs]]

            if not al_betas:
                continue

            al_mean = np.mean(al_betas)
            ct_mean = np.mean(ct_betas) if ct_betas else 0
            diff = abs(al_mean - ct_mean)

            log(f"    {nc_name:>14}: antiloop={al_mean:.3f}  control={ct_mean:.3f}  "
                f"diff={diff:.3f}")

            # Score: how close to beta=1 AND how different from control
            dist_to_one = abs(al_mean - 1.0)
            score = diff - dist_to_one  # high diff, low dist_to_one = good

            if score > best_score:
                best_score = score
                best_finding = {
                    "obs": obs, "noise": nc_name,
                    "al_beta": al_mean, "ct_beta": ct_mean, "diff": diff,
                }

    log()

    if best_finding:
        bf = best_finding
        al_beta = bf["al_beta"]
        diff = bf["diff"]

        if 0.7 <= al_beta <= 1.3 and diff > 0.3:
            log(f"RESULT: POSITIVE — 1/f spectrum detected!")
            log(f"  Observable: {bf['obs']}")
            log(f"  Noise condition: {bf['noise']}")
            log(f"  Anti-loop beta: {al_beta:.3f}  (target: 1.0)")
            log(f"  Control beta: {bf['ct_beta']:.3f}")
            log(f"  Difference: {diff:.3f}")
            log("  Anti-loop growth produces structured temporal correlations")
            log("  consistent with 1/f noise, distinct from random growth control.")
        elif al_beta > 0.3 and diff > 0.3:
            log(f"RESULT: PARTIAL — Structured spectrum but not 1/f")
            log(f"  Observable: {bf['obs']}")
            log(f"  Anti-loop beta: {al_beta:.3f}  Control: {bf['ct_beta']:.3f}")
            log(f"  Spectral structure present and different from control,")
            log(f"  but beta not near 1.0.")
        elif al_beta > 0.3 and diff <= 0.3:
            log(f"RESULT: GROWTH ARTIFACT — Spectrum matches control")
            log(f"  Observable: {bf['obs']}")
            log(f"  Anti-loop beta: {al_beta:.3f}  Control: {bf['ct_beta']:.3f}")
            log(f"  Spectral structure present but identical to random growth.")
            log(f"  Not specific to anti-loop dynamics.")
        else:
            log("RESULT: NEGATIVE — No spectral structure detected.")
            log(f"  Best observable: {bf['obs']}")
            log(f"  Anti-loop beta: {al_beta:.3f}  Control: {bf['ct_beta']:.3f}")
            log("  Graph-level observables do not exhibit structured spectral")
            log("  signatures at this scale.")

    log()

    # Save text results
    with open(os.path.join(out_dir, "o9v2_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
