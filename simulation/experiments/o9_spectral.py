"""
O9 Spectral Analysis: 1/f Noise in Anti-Loop Trajectories
==========================================================

Tests whether anti-loop node state trajectories exhibit 1/f (pink noise)
power spectra at intermediate "temperatures" (randomness levels).

Prediction (from C1 consciousness band):
  - Temperature 0 (deterministic): periodic/loopy -> steep PSD slope (high beta)
  - Temperature 1 (pure noise): white noise -> flat PSD (beta ~ 0)
  - Intermediate temperature: 1/f pink noise (beta ~ 1) = consciousness band

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

from simulation.engine import run_antiloop, FSMNode, compute_hash, HASH_XOR

TITLE = "O9 Power Spectral Density"

DEFAULT_TEMPERATURES = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]


# ============================================================
# PSD computation
# ============================================================

def _get_device():
    if HAS_TORCH and torch.cuda.is_available():
        return torch.device("cuda")
    return None


def compute_psd_gpu(trajectories_array, device):
    """Compute average PSD across nodes using GPU FFT.

    Args:
        trajectories_array: numpy array (n_nodes, n_steps), float
        device: torch.device

    Returns:
        freqs: frequency bins (numpy)
        avg_psd: average PSD across nodes (numpy)
    """
    t = torch.tensor(trajectories_array, dtype=torch.float32, device=device)
    t = t - t.mean(dim=1, keepdim=True)  # center
    fft = torch.fft.rfft(t, dim=1)
    psd = (fft.abs() ** 2).cpu().numpy()
    avg_psd = psd.mean(axis=0)

    n_steps = trajectories_array.shape[1]
    freqs = np.fft.rfftfreq(n_steps)
    return freqs, avg_psd


def compute_psd_cpu(trajectories_array):
    """Compute average PSD across nodes using numpy FFT.

    Args:
        trajectories_array: numpy array (n_nodes, n_steps), float

    Returns:
        freqs: frequency bins (numpy)
        avg_psd: average PSD across nodes (numpy)
    """
    centered = trajectories_array - trajectories_array.mean(axis=1, keepdims=True)
    fft = np.fft.rfft(centered, axis=1)
    psd = np.abs(fft) ** 2
    avg_psd = psd.mean(axis=0)

    n_steps = trajectories_array.shape[1]
    freqs = np.fft.rfftfreq(n_steps)
    return freqs, avg_psd


def compute_psd(trajectories_array, device=None):
    """Compute PSD using GPU if available, else CPU."""
    if device is not None:
        return compute_psd_gpu(trajectories_array, device)
    return compute_psd_cpu(trajectories_array)


def fit_beta(freqs, psd):
    """Fit spectral exponent beta from PSD: PSD ~ f^(-beta).

    Fits log(PSD) vs log(f) using linear regression,
    excluding DC (f=0) and the highest frequencies (noisy).

    Returns:
        beta: spectral exponent (positive = falling spectrum)
        r_squared: goodness of fit
    """
    # Exclude DC component and top 10% of frequencies
    mask = freqs > 0
    f = freqs[mask]
    p = psd[mask]

    # Exclude zero-power bins and top 10%
    n_keep = max(5, int(len(f) * 0.9))
    f = f[:n_keep]
    p = p[:n_keep]

    valid = p > 0
    if valid.sum() < 5:
        return 0.0, 0.0

    log_f = np.log10(f[valid])
    log_p = np.log10(p[valid])

    # Linear regression: log_p = -beta * log_f + const
    coeffs = np.polyfit(log_f, log_p, 1)
    slope = coeffs[0]
    beta = -slope  # PSD ~ f^(-beta), so log(PSD) = -beta*log(f) + c

    # R-squared
    predicted = np.polyval(coeffs, log_f)
    ss_res = np.sum((log_p - predicted) ** 2)
    ss_tot = np.sum((log_p - log_p.mean()) ** 2)
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return beta, r_sq


# ============================================================
# Validation: synthetic signals with known beta
# ============================================================

def generate_colored_noise(beta, n_samples, rng):
    """Generate noise with a specified spectral exponent.

    PSD ~ f^(-beta): beta=0 -> white, beta=1 -> pink, beta=2 -> brown.
    """
    freqs = np.fft.rfftfreq(n_samples)
    freqs[0] = 1.0  # avoid division by zero at DC

    # Shape spectrum
    amplitudes = freqs ** (-beta / 2.0)
    phases = rng.uniform(0, 2 * np.pi, size=len(freqs))
    spectrum = amplitudes * np.exp(1j * phases)
    spectrum[0] = 0  # zero DC

    signal = np.fft.irfft(spectrum, n=n_samples)
    return signal


def validate_fitting(log, device, n_samples=2000):
    """Verify that our beta fitting procedure recovers known exponents."""
    log("Validation: fitting procedure on synthetic signals")
    rng = np.random.default_rng(42)

    for true_beta in [0.0, 0.5, 1.0, 1.5, 2.0]:
        # Generate multiple synthetic signals, compute average PSD
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
# Trajectory extraction helpers
# ============================================================

def trajectories_to_array(trajectories_dict):
    """Convert trajectories dict to numpy array (n_nodes, n_steps).

    Only includes nodes present for the full trajectory length.
    """
    if not trajectories_dict:
        return np.array([])

    max_len = max(len(v) for v in trajectories_dict.values())
    full = {k: v for k, v in trajectories_dict.items() if len(v) == max_len}
    if not full:
        return np.array([])

    arr = np.array(list(full.values()), dtype=np.float64)
    return arr


def trajectories_to_novelty(trajectories_dict):
    """Convert trajectories to novelty signal: 1 = new state, 0 = revisit.

    This captures the recurrence structure that the anti-loop constraint
    directly shapes. At temperature 0, novelty starts high and drops as
    config space fills. At temperature 1, novelty is random.
    """
    if not trajectories_dict:
        return np.array([])

    max_len = max(len(v) for v in trajectories_dict.values())
    full = {k: v for k, v in trajectories_dict.items() if len(v) == max_len}
    if not full:
        return np.array([])

    result = []
    for configs in full.values():
        seen = set()
        novelty = []
        for c in configs:
            novelty.append(1.0 if c not in seen else 0.0)
            seen.add(c)
        result.append(novelty)

    return np.array(result, dtype=np.float64)


def trajectories_to_delta(trajectories_dict):
    """Convert trajectories to state-change signal: abs(config[t] - config[t-1]).

    Captures the magnitude of state transitions. Periodic orbits produce
    periodic delta signals (high beta). Random transitions produce white
    noise deltas (low beta). Structured exploration should be in between.
    """
    if not trajectories_dict:
        return np.array([])

    max_len = max(len(v) for v in trajectories_dict.values())
    full = {k: v for k, v in trajectories_dict.items() if len(v) == max_len}
    if not full:
        return np.array([])

    result = []
    for configs in full.values():
        arr = np.array(configs, dtype=np.float64)
        delta = np.abs(np.diff(arr))
        result.append(delta)

    return np.array(result, dtype=np.float64)


# ============================================================
# Main experiment
# ============================================================

def run(n_seeds=10, max_nodes=200, mem_bits=8, n_steps=2000,
        temperatures=None, out_dir=None, progress=None):
    """Run the O9 spectral analysis experiment.

    Grows anti-loop graphs, then runs them at various temperatures
    while recording trajectories. Computes PSD and fits spectral
    exponent beta at each temperature.
    """

    if temperatures is None:
        temperatures = DEFAULT_TEMPERATURES
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    output_lines = []
    total_work = len(temperatures) * n_seeds
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

    log("=" * 70)
    log("O9: Power Spectral Density of Anti-Loop Trajectories")
    log("=" * 70)
    log(f"Seeds: {n_seeds}  |  Nodes: {max_nodes}  |  Memory: {mem_bits}-bit  |  Steps: {n_steps}")
    log(f"Temperatures: {temperatures}")
    log(f"Device: {device if device else 'CPU (numpy)'}")
    log()

    # ----------------------------------------------------------
    # Validation
    # ----------------------------------------------------------
    validate_fitting(log, device, n_samples=n_steps)

    # ----------------------------------------------------------
    # Main sweep: temperature x seeds
    # Three signal types tested:
    #   raw:     config value (integer state)
    #   delta:   |config[t] - config[t-1]| (transition magnitude)
    #   novelty: 1 if new state, 0 if revisit (recurrence structure)
    # ----------------------------------------------------------
    log("-" * 70)
    log("TEMPERATURE SWEEP")
    log("-" * 70)

    signal_types = ["raw", "delta", "novelty"]
    # results[signal_type][temp] = list of (beta, r_sq)
    results = {s: {t: [] for t in temperatures} for s in signal_types}
    example_psds = {}  # for plotting: {temp: (freqs, psd, beta)} using best signal

    seeds = list(range(n_seeds))
    t0_total = time.time()

    for temp in temperatures:
        for i, seed in enumerate(seeds):
            t0 = time.time()

            # Phase 1: grow the graph (deterministic, no recording)
            _, G_final, _, _ = run_antiloop(
                mem_bits=mem_bits, max_nodes=max_nodes, initial_n=10,
                seed=seed, hash_fn=HASH_XOR, pressure_threshold=0.7,
                spawn_prob=0.3, max_steps=10000,
                record_trajectories=False, temperature=0.0
            )

            # Phase 2: run the grown graph at temperature, recording trajectories
            rng = np.random.default_rng(seed + 50000)
            nodes = {nid: FSMNode(mem_bits, rng) for nid in G_final.nodes()}
            node_list = list(G_final.nodes())
            trajectories = {nid: [nodes[nid].config] for nid in node_list}

            for _ in range(n_steps):
                for nid in node_list:
                    nb = [nodes[n].config for n in G_final.neighbors(nid)]
                    nodes[nid].step(nb, HASH_XOR, temperature=temp, rng=rng)
                for nid in node_list:
                    trajectories[nid].append(nodes[nid].config)

            # Analyze all three signal types
            arrays = {
                "raw": trajectories_to_array(trajectories),
                "delta": trajectories_to_delta(trajectories),
                "novelty": trajectories_to_novelty(trajectories),
            }

            betas_this = {}
            for sig_type in signal_types:
                arr = arrays[sig_type]
                if arr.size == 0 or arr.shape[1] < 10:
                    continue
                freqs, avg_psd = compute_psd(arr, device)
                beta, r_sq = fit_beta(freqs, avg_psd)
                results[sig_type][temp].append((beta, r_sq))
                betas_this[sig_type] = beta

                if i == 0 and sig_type == "delta":
                    example_psds[temp] = (freqs, avg_psd, beta)

            elapsed = time.time() - t0
            beta_strs = "  ".join(f"{s}={betas_this.get(s, 0):.2f}" for s in signal_types)
            step(f"Temperature {temp:.2f}",
                 f"seed {i+1}/{n_seeds}  |  {beta_strs}  ({elapsed:.1f}s)")

        # Summary for this temperature
        parts = []
        for sig_type in signal_types:
            betas = [b for b, _ in results[sig_type][temp]]
            if betas:
                b_arr = np.array(betas)
                parts.append(f"{sig_type}={b_arr.mean():.3f}+/-{b_arr.std():.3f}")
        log(f"  temp={temp:.2f}:  {'  '.join(parts)}")

    total_time = time.time() - t0_total
    log(f"\nTotal time: {total_time:.1f}s")
    log()

    # ----------------------------------------------------------
    # Summary table (per signal type)
    # ----------------------------------------------------------
    # Collect means/stds for the best signal type (most structure)
    summary = {}  # signal_type -> {temps, means, stds}

    for sig_type in signal_types:
        log("-" * 70)
        log(f"SUMMARY: {sig_type} signal")
        log("-" * 70)
        log(f"{'Temperature':>12} {'beta_mean':>10} {'beta_std':>10} {'R^2_mean':>10}")
        log("-" * 45)

        means, stds, valid = [], [], []
        for temp in temperatures:
            betas = [b for b, _ in results[sig_type][temp]]
            r_sqs = [r for _, r in results[sig_type][temp]]
            if betas:
                b_mean = np.mean(betas)
                b_std = np.std(betas)
                r_mean = np.mean(r_sqs)
                log(f"{temp:>12.2f} {b_mean:>10.3f} {b_std:>10.3f} {r_mean:>10.3f}")
                means.append(b_mean)
                stds.append(b_std)
                valid.append(temp)

        summary[sig_type] = {"temps": valid, "means": means, "stds": stds}
        log()

    # ----------------------------------------------------------
    # Plots
    # ----------------------------------------------------------

    # Plot 1: Beta vs temperature for all signal types
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fig.suptitle("O9: Spectral Exponent vs Temperature", fontweight="bold")

    colors_sig = {"raw": "tab:gray", "delta": "tab:blue", "novelty": "tab:green"}
    for sig_type in signal_types:
        s = summary[sig_type]
        if s["temps"]:
            ax.errorbar(s["temps"], s["means"], yerr=s["stds"], fmt="o-",
                        capsize=5, color=colors_sig[sig_type], linewidth=2,
                        markersize=6, label=f"{sig_type} signal")

    ax.axhline(y=1.0, color="tab:red", linestyle="--", alpha=0.7,
               label="beta = 1 (1/f pink noise)")
    ax.axhline(y=0.0, color="black", linestyle=":", alpha=0.3,
               label="beta = 0 (white noise)")
    ax.set_xlabel("Temperature (randomness)")
    ax.set_ylabel("Spectral exponent beta")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "o9_beta_vs_temperature.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 2: Example PSDs (delta signal) at different temperatures
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    fig.suptitle("O9: Power Spectral Density (delta signal) at Different Temperatures",
                 fontweight="bold")

    if example_psds:
        colors = plt.cm.coolwarm(np.linspace(0, 1, len(example_psds)))
        for (temp, (freqs, psd, beta)), color in zip(sorted(example_psds.items()), colors):
            mask = freqs > 0
            ax.loglog(freqs[mask], psd[mask], "-", alpha=0.8, color=color,
                      label=f"T={temp:.2f} (beta={beta:.2f})")

    ax.set_xlabel("Frequency")
    ax.set_ylabel("Power Spectral Density")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which="both")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "o9_example_psds.png"),
                dpi=150, bbox_inches="tight")
    plt.close()

    # ----------------------------------------------------------
    # Verdict (use signal type with most variation in beta)
    # ----------------------------------------------------------
    log("=" * 70)
    log("VERDICT")
    log("=" * 70)

    # Pick signal type with largest beta range across temperatures
    best_sig = None
    best_range = 0
    for sig_type in signal_types:
        s = summary[sig_type]
        if len(s["means"]) >= 3:
            r = max(s["means"]) - min(s["means"])
            log(f"  {sig_type}: beta range = [{min(s['means']):.3f}, {max(s['means']):.3f}]  "
                f"(spread = {r:.3f})")
            if r > best_range:
                best_range = r
                best_sig = sig_type

    log()

    if best_sig:
        s = summary[best_sig]
        means_arr = np.array(s["means"])
        temps_arr = np.array(s["temps"])

        log(f"Best signal type: {best_sig} (largest spectral variation)")
        log()

        # Find temperature closest to beta=1
        dist_to_one = np.abs(means_arr - 1.0)
        best_idx = np.argmin(dist_to_one)
        best_temp = temps_arr[best_idx]
        best_beta = means_arr[best_idx]

        log(f"Closest to beta=1:  T={best_temp:.2f}  beta={best_beta:.3f}")
        log()

        # Check for monotonic trend
        is_decreasing = all(means_arr[i] >= means_arr[i+1] - 0.1
                           for i in range(len(means_arr) - 1))

        at_extreme = best_idx == 0 or best_idx == len(means_arr) - 1
        crosses_one = means_arr[0] > 1.0 and means_arr[-1] < 1.0

        if crosses_one and not at_extreme:
            log("RESULT: POSITIVE — Beta crosses 1.0 at intermediate temperature.")
            log(f"1/f (pink noise) emerges at T ~ {best_temp:.2f}, between")
            log("deterministic order and pure randomness.")
            log("This is consistent with the C1 consciousness band prediction.")
        elif crosses_one:
            log("RESULT: PARTIAL — Beta crosses 1.0 but at boundary temperature.")
            log("The trend is consistent with C1 but the crossing point")
            log("needs finer temperature resolution to confirm.")
        elif is_decreasing and best_range > 0.3:
            log("RESULT: MONOTONIC — Beta decreases with temperature.")
            log(f"Range: [{means_arr[-1]:.2f}, {means_arr[0]:.2f}]")
            if means_arr[0] < 1.0:
                log("Beta is always below 1.0 — trajectories lack long-range")
                log("temporal correlations at this scale.")
            else:
                log("Beta is always above 1.0 — trajectories are more ordered")
                log("than 1/f at all temperatures tested.")
        elif best_range < 0.05:
            log("RESULT: NEGATIVE — No spectral structure detected.")
            log("Beta is flat across temperatures. The anti-loop constraint")
            log("does not produce measurable spectral signatures at this scale.")
        else:
            log("RESULT: INCONCLUSIVE — Some variation in beta but no clear")
            log("monotonic trend or 1/f crossing point.")
    else:
        log("INSUFFICIENT DATA — could not compute verdict.")

    log()

    # Save text results
    with open(os.path.join(out_dir, "o9_results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    log(f"Results saved to {out_dir}/")
