"""
Analysis Tools
==============

Power-law degree distribution testing (Clauset-Shalizi-Newman method)
with lognormal and stretched-exponential comparisons (Broido-Clauset).
"""

import warnings

import numpy as np

warnings.filterwarnings("ignore", module="powerlaw")
import powerlaw


def analyze_powerlaw(G, label=""):
    """Apply CSN power-law test to a graph's degree distribution.

    Returns dict with alpha, xmin, sigma, n_tail, and comparison results
    against exponential, lognormal, and stretched exponential.
    """
    degrees = np.array([d for _, d in G.degree()], dtype=float)
    degrees = degrees[degrees >= 1]

    if len(degrees) < 30:
        return {"label": label, "alpha": None, "xmin": None, "sigma": None,
                "n_tail": 0, "vs_exp": None, "vs_lognormal": None,
                "vs_stretched_exp": None}

    try:
        fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
    except Exception:
        return {"label": label, "alpha": None, "xmin": None, "sigma": None,
                "n_tail": 0, "vs_exp": None, "vs_lognormal": None,
                "vs_stretched_exp": None}

    def _safe_compare(dist1, dist2):
        try:
            return fit.distribution_compare(dist1, dist2,
                                            normalized_ratio=True)
        except Exception:
            return (0.0, 1.0)

    R_exp, p_exp = _safe_compare("power_law", "exponential")
    R_ln, p_ln = _safe_compare("power_law", "lognormal")
    R_se, p_se = _safe_compare("power_law", "stretched_exponential")

    n_tail = int(np.sum(degrees >= fit.xmin))

    return {
        "label": label,
        "alpha": fit.alpha,
        "xmin": fit.xmin,
        "sigma": fit.sigma,
        "n_tail": n_tail,
        "vs_exp": {"R": R_exp, "p": p_exp},
        "vs_lognormal": {"R": R_ln, "p": p_ln},
        "vs_stretched_exp": {"R": R_se, "p": p_se},
    }


def get_ccdf(G):
    """Compute complementary CDF of degree distribution for log-log plotting."""
    degrees = sorted([d for _, d in G.degree()])
    n = len(degrees)
    unique = sorted(set(degrees))
    ccdf = [sum(1 for x in degrees if x >= d) / n for d in unique]
    return unique, ccdf


def format_comparison(name, comp):
    """Format a single distribution comparison."""
    direction = "power_law BETTER" if comp["R"] > 0 else f"{name} BETTER"
    sig = "***" if comp["p"] < 0.01 else ("**" if comp["p"] < 0.05 else "ns")
    return f"    vs {name:<20s} R={comp['R']:+.3f}  p={comp['p']:.4f}  {direction} {sig}"


def format_powerlaw_result(r):
    """Format a power-law analysis result as a readable string."""
    if r["alpha"] is None:
        return f"  {r['label']}: insufficient data"

    lines = [
        f"  {r['label']}:",
        f"    alpha = {r['alpha']:.3f} +/- {r['sigma']:.3f}  "
        f"(xmin = {r['xmin']:.0f}, n_tail = {r['n_tail']})",
    ]
    for name, key in [("exponential", "vs_exp"),
                      ("lognormal", "vs_lognormal"),
                      ("stretched_exponential", "vs_stretched_exp")]:
        if r.get(key):
            lines.append(format_comparison(name, r[key]))
    return "\n".join(lines)
