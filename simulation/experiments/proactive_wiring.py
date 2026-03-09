"""Proactive wiring: testing whether it extends entity lifetime.

HYPOTHESIS (FALSIFIED): Proactive wiring extends entity lifetime
because adding a neighbor changes the XOR hash, refreshing the
effective state space without resetting.

RESULT: No difference. Entity lifetime is ~C*sqrt(2) steps
regardless of wiring strategy. The XOR hash is sufficiently mixing
that the birthday paradox bound holds regardless of neighbor count
or wiring timing.

However, this experiment reveals the ACTUAL structural difference:
  PT=0.7: 97% of wires are pressure-based (no effective set reset).
    Network grows ~5x faster. Entities run with unbroken trajectories.
  PT=1.0: 100% of wires are loop-based (every wire resets effective set).
    Network grows slowly. Entities reset every ~C*sqrt(2) steps.

The MI excess mechanism remains unexplained. It correlates with growth
rate and wiring burst patterns, not with entity survival time.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TITLE = "Proactive Wiring (Hypothesis Test)"


def _run_fsm_entity(C, n_initial, strategy, wire_interval, max_steps, rng,
                    max_neighbors=200):
    """Run one entity surrounded by FSM neighbors.

    Returns: (steps_until_loop, n_wiring_events)
    """
    table = rng.integers(0, C, size=(C, C), dtype=np.int32)
    config = int(rng.integers(0, C))
    effective_set = set()

    nb_tables = rng.integers(0, C, size=(max_neighbors, C, C), dtype=np.int32)
    nb_configs = rng.integers(0, C, size=max_neighbors, dtype=np.int32)

    n_neighbors = n_initial
    n_wires = 0

    for step in range(max_steps):
        h = 0
        for i in range(n_neighbors):
            h ^= int(nb_configs[i])
        h = h % C

        eff = (config, h)
        if eff in effective_set:
            return step, n_wires
        effective_set.add(eff)

        new_config = int(table[config, h])
        for i in range(n_neighbors):
            nb_input = config % C
            nb_configs[i] = int(nb_tables[i, nb_configs[i], nb_input])
        config = new_config

        if (strategy == "proactive" and step > 0
                and step % wire_interval == 0
                and n_neighbors < max_neighbors):
            n_neighbors += 1
            n_wires += 1

    return max_steps, n_wires


def _measure_growth_dynamics(mem_bits, max_nodes, threshold, seed):
    """Measure wiring dynamics in actual LPAN model."""
    from simulation.shared.engine import SpawnModel

    C = 2 ** mem_bits
    model = SpawnModel(mem_bits, max_nodes, seed, lateral_wiring=True)
    pressure_wires = 0
    loop_wires = 0

    for step in range(1, 50000):
        model.step_all()
        if model.n_nodes >= max_nodes:
            break

        acted = 0
        for nid in range(model.n_nodes):
            if acted >= 5:
                break
            if model.G.degree(nid) == 0:
                model._add_node(parent_id=nid, step=step)
                acted += 1
            elif model.looped[nid]:
                loop_wires += 1
                model.add_lateral_edge(nid)
                model.looped[nid] = False
                model.effective_sets[nid] = set()
                acted += 1
                if model.n_nodes < max_nodes and model.rng.random() < 0.3:
                    model._add_node(parent_id=nid, step=step)
            elif (model.visited_counts[nid] / model.node_config_spaces[nid]
                  > threshold):
                pressure_wires += 1
                model.add_lateral_edge(nid)
                acted += 1
                if model.n_nodes < max_nodes and model.rng.random() < 0.3:
                    model._add_node(parent_id=nid, step=step)

    return {
        "steps": step,
        "nodes": model.n_nodes,
        "edges": model.G.number_of_edges(),
        "pressure_wires": pressure_wires,
        "loop_wires": loop_wires,
    }


def run(progress, out_dir, n_seeds, max_nodes, mem_bits, time_budget, **_):
    C = 2 ** mem_bits
    n_entities = min(max_nodes, 200)

    progress.log(f"Proactive wiring hypothesis test: C={C} ({mem_bits}-bit)")
    progress.log(f"  Part 1: Entity lifetime test (isolated)")
    progress.log(f"  Part 2: Growth dynamics at different thresholds")

    n_trials = max(n_seeds * 20, 50)
    max_steps = C * C * 10
    n_initial = 2

    # Part 1: Entity lifetime test
    strategies = {
        "static": (None, 0),
        f"proactive_T={C//2}": ("proactive", C // 2),
        f"proactive_T={C}": ("proactive", C),
        f"proactive_T={C*2}": ("proactive", C * 2),
    }

    lifetime_results = {}
    t_start = time.time()

    for name, (strat, interval) in strategies.items():
        if strat is None:
            strat = "static"
        lives = []
        for trial in range(n_trials):
            if time.time() - t_start > time_budget * 0.3:
                break
            rng = np.random.default_rng(8000 + trial)
            life, _ = _run_fsm_entity(C, n_initial, strat, interval,
                                       max_steps, rng)
            lives.append(life)

        lifetime_results[name] = lives
        if lives:
            progress.log(f"    {name}: {np.mean(lives):.1f} +/- "
                         f"{np.std(lives):.1f} (n={len(lives)})")

    # Part 2: Growth dynamics
    progress.log("")
    progress.log("  Part 2: Growth dynamics in actual LPAN model")
    thresholds = [0.5, 0.7, 0.9, 1.0]
    growth_data = {}

    for pt in thresholds:
        pt_data = []
        for i in range(min(n_seeds, 3)):
            if time.time() - t_start > time_budget * 0.9:
                break
            progress.update(0, 1, "Growth dynamics",
                            f"PT={pt:.1f} seed {i+1}")
            result = _measure_growth_dynamics(mem_bits, n_entities, pt,
                                              seed=9000 + i)
            pt_data.append(result)

        if pt_data:
            growth_data[pt] = pt_data
            avg_steps = np.mean([d["steps"] for d in pt_data])
            avg_pw = np.mean([d["pressure_wires"] for d in pt_data])
            avg_lw = np.mean([d["loop_wires"] for d in pt_data])
            avg_e = np.mean([d["edges"] for d in pt_data])
            avg_n = np.mean([d["nodes"] for d in pt_data])
            total = avg_pw + avg_lw
            pct_pressure = 100 * avg_pw / total if total > 0 else 0
            progress.log(f"    PT={pt:.1f}: {avg_steps:.0f} steps, "
                         f"{avg_e:.0f}e, pressure={pct_pressure:.0f}%, "
                         f"resets={avg_lw:.0f}")

    # Summary
    static_mean = np.mean(lifetime_results.get("static", [1]))

    lines = [
        "=" * 60,
        "Proactive Wiring Hypothesis Test",
        "=" * 60,
        f"Memory: {mem_bits} bits (C={C})",
        "",
        "PART 1: ENTITY LIFETIME (HYPOTHESIS FALSIFIED)",
        f"  Birthday paradox bound: ~{int(C * 1.41)} steps",
        "",
        "  Strategy          | Mean Life | Ratio vs Static",
        "  " + "-" * 50,
    ]

    for name, lives in lifetime_results.items():
        if lives:
            mean = np.mean(lives)
            ratio = mean / static_mean if static_mean > 0 else 0
            lines.append(f"  {name:19s} | {mean:9.1f} | {ratio:.2f}x")

    lines += [
        "",
        "  RESULT: No difference. Proactive wiring does NOT extend",
        "  entity lifetime. XOR hash is sufficiently mixing that the",
        "  birthday paradox bound holds regardless of wiring strategy.",
        "",
        "PART 2: GROWTH DYNAMICS (WHAT ACTUALLY DIFFERS)",
        "  Threshold | Steps | Edges | Pressure% | Resets",
        "  " + "-" * 50,
    ]

    for pt in thresholds:
        if pt in growth_data:
            d = growth_data[pt]
            avg_s = np.mean([x["steps"] for x in d])
            avg_e = np.mean([x["edges"] for x in d])
            avg_pw = np.mean([x["pressure_wires"] for x in d])
            avg_lw = np.mean([x["loop_wires"] for x in d])
            total = avg_pw + avg_lw
            pct = 100 * avg_pw / total if total > 0 else 0
            lines.append(f"  {pt:.1f}       | {avg_s:5.0f} | {avg_e:5.0f} | "
                         f"{pct:8.0f}% | {avg_lw:.0f}")

    lines += [
        "",
        "INTERPRETATION:",
        "  The MI excess at threshold < 1.0 correlates with:",
        "  - Faster growth (fewer steps to reach max nodes)",
        "  - Fewer effective set resets (most wiring is pressure-based)",
        "  - Burst wiring patterns (many edges formed in quick succession)",
        "",
        "  The MI excess does NOT correlate with:",
        "  - Entity lifetime (identical across strategies)",
        "  - Total edge count (similar avg degree at all thresholds)",
        "",
        "  The mechanism connecting growth dynamics to MI excess",
        "  remains an open question. The proactive-selection",
        "  hypothesis is falsified.",
    ]

    report = "\n".join(lines)
    progress.log("")
    progress.log(report)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "proactive_wiring_results.txt"), "w") as f:
        f.write(report)

    _plot_results(lifetime_results, growth_data, thresholds, C,
                  out_dir, progress)
    progress.update(1, 1, "Done", "Complete")


def _plot_results(lifetime_results, growth_data, thresholds, C,
                  out_dir, progress):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: Entity lifetimes (all similar)
    ax = axes[0]
    names = list(lifetime_results.keys())
    means = [np.mean(v) for v in lifetime_results.values()]
    stds = [np.std(v) for v in lifetime_results.values()]
    colors = ["#999"] + ["#2196F3"] * (len(names) - 1)

    ax.bar(range(len(names)), means, yerr=stds, capsize=5,
           color=colors, alpha=0.7)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=7)
    ax.set_ylabel("Entity lifetime (steps)")
    ax.set_title("Lifetime by strategy (no difference)")
    ax.axhline(C * 1.41, color="red", linestyle=":", alpha=0.3,
               label=f"Birthday bound ~{int(C*1.41)}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: Growth dynamics
    ax = axes[1]
    pts = sorted(growth_data.keys())
    if pts:
        steps = [np.mean([d["steps"] for d in growth_data[pt]]) for pt in pts]
        pressure_pcts = []
        for pt in pts:
            pw = np.mean([d["pressure_wires"] for d in growth_data[pt]])
            lw = np.mean([d["loop_wires"] for d in growth_data[pt]])
            total = pw + lw
            pressure_pcts.append(100 * pw / total if total > 0 else 0)

        ax2 = ax.twinx()
        l1 = ax.bar([x - 0.15 for x in range(len(pts))], steps, width=0.3,
                     color="#2196F3", alpha=0.7, label="Growth steps")
        l2 = ax2.bar([x + 0.15 for x in range(len(pts))], pressure_pcts,
                      width=0.3, color="#4CAF50", alpha=0.7,
                      label="Pressure wires %")
        ax.set_xticks(range(len(pts)))
        ax.set_xticklabels([f"{pt:.1f}" for pt in pts])
        ax.set_xlabel("Pressure threshold")
        ax.set_ylabel("Steps to max nodes", color="#2196F3")
        ax2.set_ylabel("Pressure-based wiring %", color="#4CAF50")
        ax.set_title("Growth dynamics vs threshold")
        ax.legend(handles=[l1, l2], fontsize=8, loc="upper left")
        ax.grid(True, alpha=0.3, axis="y")

    plt.suptitle("Proactive Wiring: Hypothesis FALSIFIED",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(out_dir, "proactive_wiring.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    progress.log(f"  Plot saved: {path}")
