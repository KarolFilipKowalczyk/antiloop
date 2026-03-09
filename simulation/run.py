"""
Antiloop Experiment Runner
==========================

Unified entry point for all antiloop experiments.

Usage:
    python -m simulation.run c3_topology
    python -m simulation.run coupling --quick
    python -m simulation.run blindness --seeds 5 --time 120

Any .py file in simulation/experiments/ that has a run() function
and a TITLE string is a valid experiment. No registration needed.
GUI progress window is shown when available (falls back to headless).

Common flags (passed to every experiment, each takes what it needs):
    --quick     60s,  3 seeds  (20s/seed)
    (default)   300s, 10 seeds (30s/seed)
    --long      900s, 30 seeds (30s/seed, publishable)
    --time N    Override time budget (seconds)
    --seeds N   Override number of random seeds
    --nodes N   Max nodes per graph
    --mem N     FSM memory bits
"""

import argparse
import importlib
import os
import sys

# Ensure project root is on path so 'simulation' package is importable
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _discover_experiments():
    """Find all experiment modules in simulation/experiments/."""
    exp_dir = os.path.join(os.path.dirname(__file__), "experiments")
    experiments = {}
    for fname in sorted(os.listdir(exp_dir)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        name = fname[:-3]  # strip .py
        module_path = f"simulation.experiments.{name}"
        try:
            mod = importlib.import_module(module_path)
        except Exception:
            continue
        if hasattr(mod, "run") and callable(mod.run):
            title = getattr(mod, "TITLE", name)
            doc = (mod.__doc__ or "").strip().split("\n")[0]
            experiments[name] = {
                "module": mod,
                "title": title,
                "description": doc,
            }
    return experiments


def main():
    experiments = _discover_experiments()

    parser = argparse.ArgumentParser(
        description="Antiloop experiment runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Experiments:\n" + "\n".join(
            f"  {name:<24} {info['description']}"
            for name, info in experiments.items()
        ) if experiments else "No experiments found.",
    )
    parser.add_argument("experiment", choices=list(experiments.keys()),
                        help="Which experiment to run")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test (60s, 3 seeds)")
    parser.add_argument("--long", action="store_true",
                        help="Publishable run (900s, 30 seeds)")
    parser.add_argument("--seeds", type=int, default=None,
                        help="Number of random seeds")
    parser.add_argument("--nodes", type=int, default=500,
                        help="Max nodes per graph (default: 500)")
    parser.add_argument("--mem", type=int, default=8,
                        help="FSM memory bits (default: 8)")
    parser.add_argument("--time", type=int, default=None,
                        help="Time budget in seconds (default: 60/300/900)")

    args = parser.parse_args()

    exp = experiments[args.experiment]
    exp_mod = exp["module"]
    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)

    # Presets: quick=60s/3seeds, normal=300s/10seeds, long=900s/30seeds
    if args.quick:
        default_seeds, default_time = 3, 60
    elif getattr(args, 'long'):
        default_seeds, default_time = 30, 900
    else:
        default_seeds, default_time = 10, 300

    # Uniform kwargs — every experiment gets the same dict,
    # each takes what it needs via **_ in its signature.
    kwargs = {
        "out_dir": out_dir,
        "n_seeds": args.seeds or default_seeds,
        "max_nodes": args.nodes,
        "mem_bits": args.mem,
        "time_budget": args.time or default_time,
    }

    try:
        from simulation.gui import run_with_gui
        run_with_gui(exp_mod.run, title=exp["title"], **kwargs)
    except Exception:
        # GUI unavailable (headless system, no display, etc.) — run without it
        from simulation.gui import run_headless
        run_headless(exp_mod.run, **kwargs)


if __name__ == "__main__":
    main()
