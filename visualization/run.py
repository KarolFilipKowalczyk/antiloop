"""
Antiloop Educational Visualizations
====================================

Generate explanatory figures showing how the anti-loop mechanism works.

Usage:
    python -m visualization.run               # generate all figures
    python -m visualization.run intro         # generate one figure
    python -m visualization.run --list        # list available figures
"""

import importlib
import os
import sys

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
DEFAULT_OUT = os.path.join(os.path.dirname(__file__), "output")


def discover_figures():
    """Auto-discover figure modules in figures/ directory."""
    figures = {}
    for fname in sorted(os.listdir(FIGURES_DIR)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        mod_name = fname[:-3]
        try:
            mod = importlib.import_module(f"visualization.figures.{mod_name}")
            if hasattr(mod, "TITLE") and hasattr(mod, "generate"):
                figures[mod_name] = mod
        except Exception as e:
            print(f"  Warning: could not load {mod_name}: {e}")
    return figures


def main():
    os.makedirs(DEFAULT_OUT, exist_ok=True)
    figures = discover_figures()

    if not figures:
        print("No figures found in visualization/figures/")
        return

    args = sys.argv[1:]

    if "--list" in args:
        print("Available figures:")
        for name, mod in figures.items():
            print(f"  {name:30s}  {mod.TITLE}")
        return

    # Filter to requested figures, or run all
    if args:
        selected = {}
        for arg in args:
            if arg in figures:
                selected[arg] = figures[arg]
            else:
                # Try partial match
                matches = [k for k in figures if arg in k]
                if len(matches) == 1:
                    selected[matches[0]] = figures[matches[0]]
                elif matches:
                    print(f"Ambiguous '{arg}': {matches}")
                    return
                else:
                    print(f"Unknown figure '{arg}'. Use --list to see available.")
                    return
        figures = selected

    print(f"Generating {len(figures)} figure(s)...\n")
    for name, mod in figures.items():
        print(f"[{mod.TITLE}]")
        try:
            mod.generate(DEFAULT_OUT)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
        print()

    print("Done.")


if __name__ == "__main__":
    main()
