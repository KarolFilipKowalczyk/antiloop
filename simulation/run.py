"""
Antiloop Experiment Runner
==========================

Unified entry point for all antiloop experiments.

Usage:
    python -m simulation.run c3 --quick --gui
    python -m simulation.run coupling
    python -m simulation.run o9 --quick --gui
    python -m simulation.run c3 --seeds 30 --nodes 500 --mem 8

Available experiments:
    c3        Scale-free topology test (O5)
    coupling  Coupling constant measurement (negative result)
    o9        Graph-level spectral analysis (O9v2)
"""

import argparse
import os
import sys

# Ensure project root is on path so 'simulation' package is importable
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


EXPERIMENTS = {
    "c3": {
        "module": "simulation.experiments.c3_topology",
        "title": "C3 Scale-Free Topology",
        "description": "Test whether anti-loop constraint produces scale-free networks (O5)",
    },
    "coupling": {
        "module": "simulation.experiments.coupling",
        "title": "Coupling Constant",
        "description": "Measure coupling ratio vs graph size (known negative result)",
    },
    "o9": {
        "module": "simulation.experiments.o9_spectral",
        "title": "O9v2 Spectral Analysis",
        "description": "Test 1/f spectrum of graph-level observables (O9v2)",
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="Antiloop experiment runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Experiments:\n" + "\n".join(
            f"  {name:<12} {info['description']}"
            for name, info in EXPERIMENTS.items()
        ),
    )
    parser.add_argument("experiment", choices=list(EXPERIMENTS.keys()),
                        help="Which experiment to run")
    parser.add_argument("--gui", action="store_true",
                        help="Show progress window")
    parser.add_argument("--quick", action="store_true",
                        help="Quick test with fewer seeds")
    parser.add_argument("--seeds", type=int, default=None,
                        help="Number of random seeds")
    parser.add_argument("--nodes", type=int, default=500,
                        help="Max nodes per graph (default: 500)")
    parser.add_argument("--mem", type=int, default=8,
                        help="FSM memory bits (default: 8)")
    parser.add_argument("--time", type=int, default=None,
                        help="Time budget in seconds (default: 60 quick, 300 full)")

    args = parser.parse_args()

    exp_info = EXPERIMENTS[args.experiment]
    exp_mod = __import__(exp_info["module"], fromlist=["run"])

    out_dir = os.path.join(os.path.dirname(__file__), "results")

    # Build kwargs based on experiment
    kwargs = {"out_dir": out_dir}

    if args.experiment == "c3":
        n_seeds = args.seeds or (3 if args.quick else 30)
        kwargs["n_seeds"] = n_seeds
        kwargs["max_nodes"] = args.nodes
        kwargs["mem_bits"] = args.mem
    elif args.experiment == "coupling":
        kwargs["mem_bits"] = args.mem
    elif args.experiment == "o9":
        n_seeds = args.seeds or (3 if args.quick else 10)
        kwargs["n_seeds"] = n_seeds
        kwargs["max_nodes"] = min(args.nodes, 200)
        kwargs["mem_bits"] = args.mem
        kwargs["time_budget"] = args.time or (60 if args.quick else 300)

    if args.gui:
        from simulation.gui import run_with_gui
        run_with_gui(exp_mod.run, title=exp_info["title"], **kwargs)
    else:
        from simulation.gui import run_headless
        run_headless(exp_mod.run, **kwargs)


if __name__ == "__main__":
    main()
