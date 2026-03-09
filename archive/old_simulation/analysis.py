"""
Antiloop Analysis Tools
=======================

Shared analysis functions for all antiloop experiments:
  - Power-law degree distribution testing (Clauset-Shalizi-Newman)
  - CCDF computation for log-log plotting
  - Result formatting
"""

import warnings

import numpy as np

# Suppress powerlaw's noisy internal warnings
warnings.filterwarnings("ignore", module="powerlaw")
import powerlaw


def analyze_powerlaw(G, label=""):
    """Apply Clauset-Shalizi-Newman power-law test to a graph's degree distribution.

    Returns dict with alpha, xmin, sigma, n_tail, and comparison results
    against exponential and lognormal alternatives.
    """
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    degrees = degrees[degrees >= 1]

    if len(degrees) < 30:
        return {"label": label, "alpha": None, "xmin": None, "sigma": None,
                "n_tail": 0, "vs_exp": None, "vs_lognormal": None}

    fit = powerlaw.Fit(degrees, discrete=True, verbose=False)

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


def get_ccdf(G):
    """Compute complementary CDF of degree distribution for log-log plotting.

    Returns:
        unique_degrees: sorted list of unique degree values
        ccdf: P(K >= k) for each unique degree
    """
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    unique = sorted(set(degrees))
    ccdf = [sum(1 for x in degrees if x >= d) / n for d in unique]
    return unique, ccdf


def format_powerlaw_result(r):
    """Format a single power-law analysis result as a readable string."""
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
