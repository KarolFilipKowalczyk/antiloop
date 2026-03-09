"""
Antiloop Experiment Runner
==========================

Unified entry point for all antiloop experiments.

Usage:
    python -m simulation.run spawn_topology
    python -m simulation.run phase_boundary --quick
    python -m simulation.run spawn_topology --scale 3

Any .py file in simulation/experiments/ that has a run() function
and a TITLE string is a valid experiment. No registration needed.
GUI progress window is shown when available (falls back to headless).

Scale presets (controls time, seeds, nodes, and mem_bits together):
    --scale 0   15s,  1 seed,   200 nodes, 6-bit  (smoke test)
    --scale 1   60s,  3 seeds,  500 nodes, 8-bit  (quick)
    --scale 2   300s, 10 seeds, 500 nodes, 8-bit  (normal, default)
    --scale 3   900s, 30 seeds, 500 nodes, 8-bit  (publishable)
    --scale 4   3600s, 30 seeds, 2000 nodes, 10-bit (deep)

Individual overrides (--time, --seeds, --nodes, --mem) take priority.
Legacy flags --quick and --long map to --scale 1 and --scale 3.
"""

import argparse
import importlib
import os
import sys

# Ensure project root is on path so 'simulation' package is importable
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Scale presets: (time_budget, n_seeds, max_nodes, mem_bits)
SCALE_PRESETS = {
    0: (15,   1,   200,  6),   # smoke test
    1: (60,   3,   500,  8),   # quick
    2: (300,  10,  500,  8),   # normal (default)
    3: (900,  30,  500,  8),   # publishable
    4: (3600, 30,  2000, 10),  # deep
}


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

    scale_help = "\n".join(
        f"    {k}: {v[0]:>4}s, {v[1]:>2} seeds, {v[2]:>4} nodes, {v[3]}-bit"
        for k, v in SCALE_PRESETS.items()
    )

    parser = argparse.ArgumentParser(
        description="Antiloop experiment runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Scale presets:\n{scale_help}\n\n"
            "Experiments:\n" + "\n".join(
                f"  {name:<24} {info['description']}"
                for name, info in experiments.items()
            )
        ) if experiments else "No experiments found.",
    )
    parser.add_argument("experiment", choices=list(experiments.keys()),
                        help="Which experiment to run")
    parser.add_argument("--scale", type=int, default=None,
                        help="Scale preset 0-4 (default: 2)")
    parser.add_argument("--quick", action="store_true",
                        help="Shorthand for --scale 1")
    parser.add_argument("--long", action="store_true",
                        help="Shorthand for --scale 3")
    parser.add_argument("--seeds", type=int, default=None,
                        help="Override number of random seeds")
    parser.add_argument("--nodes", type=int, default=None,
                        help="Override max nodes per graph")
    parser.add_argument("--mem", type=int, default=None,
                        help="Override FSM memory bits")
    parser.add_argument("--time", type=int, default=None,
                        help="Override time budget (seconds)")

    args = parser.parse_args()

    # Resolve scale level
    if args.scale is not None:
        scale = args.scale
    elif args.quick:
        scale = 1
    elif getattr(args, 'long'):
        scale = 3
    else:
        scale = 2

    scale = max(0, min(scale, max(SCALE_PRESETS.keys())))
    default_time, default_seeds, default_nodes, default_mem = SCALE_PRESETS[scale]

    exp = experiments[args.experiment]
    exp_mod = exp["module"]
    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)

    # Individual overrides take priority over scale preset
    kwargs = {
        "out_dir": out_dir,
        "n_seeds": args.seeds if args.seeds is not None else default_seeds,
        "max_nodes": args.nodes if args.nodes is not None else default_nodes,
        "mem_bits": args.mem if args.mem is not None else default_mem,
        "time_budget": args.time if args.time is not None else default_time,
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
