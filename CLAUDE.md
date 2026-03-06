# CLAUDE.md — Project context for Claude Code

## What is antiloop?

A formal framework deriving consciousness, ethics, and network topology from three axioms and one constraint: **don't loop, don't randomize**.

Core insight: any finite deterministic system must eventually repeat (pigeonhole principle). If experience requires novelty, repetition is experiential death. The only escape is growth. This single constraint — avoid loops while maintaining structure — produces scale-free networks, a complete ethical system, and speculative interpretations of time, space, and physical forces.

## Project origin

Developed through conversation between Karol Kowalczyk and Claude (Anthropic) on March 6, 2026. The axioms, core intuitions, and philosophical interpretation are Karol's. Formalization and simulation were collaborative. Adversarial review was performed by a separate Claude instance role-playing a finite model theorist (Prof. Jerzy Tyszkiewicz, MIMUW).

## Repository structure

```
antiloop/
├── CLAUDE.md                          ← you are here
├── README.md                          
├── logo/
│   └── antiloop_logo.svg              — the antylope
├── theory/
│   ├── non_looping_existence_v02.md   — formal paper (CURRENT VERSION)
│   ├── non_looping_existence.md       — v0.1 (historical, pre-review)
│   └── complete_evaluation_package.md — theory + simulation + results for review
├── essays/
│   ├── ethics_essay.md                — accessible essay (English)
│   ├── esej_etyka_pl.md              — accessible essay (Polish)
│   └── fermi_post_draft.md           — forum post: Fermi paradox dissolution
├── simulation/
│   ├── engine.py                      — shared core: FSMNode, hash functions, run_antiloop, controls
│   ├── gui.py                         — ANTILOOP GUI progress window (always on)
│   ├── run.py                         — unified entry point, auto-discovers experiments
│   ├── experiments/
│   │   ├── c1_complexity.py           — C1 consciousness band (inter-node MI) ✓ POSITIVE
│   │   ├── c3_topology.py             — C3 scale-free topology ✓ POSITIVE (needs proper test)
│   │   ├── coupling.py                — coupling constant test ✗ NEGATIVE
│   │   └── o9_spectral.py             — O9 1/f spectral analysis ✗ NEGATIVE (v1, v2 planned)
│   └── results/                       — plots and raw output
└── open_problems.md                   — O1–O13, living document
```

## Theory summary

### Axioms
- **A1 (Existence):** At least one state distinguishable from the empty set exists.
- **A2 (Observer):** At least one state-transitioning entity exists.
- **A3 (Sequentiality):** The entity must traverse at least two distinguishable states.
- **Assumption N:** Experience requires novelty (new information). This is clearly labeled as an additional assumption, not derived from A1–A3.

### Theorem chain (T1–T6)
T1: Finite isolated systems must loop (pigeonhole). T2: Loops are informationally degenerate. T3: If Assumption N, looping = no experience. T4: Finite isolation cannot sustain experience. T5: Growth is required (internal or relational). T6: Growth must be unbounded for any finite graph.

### Key conjectures
- **C1 (Consciousness band):** A measure μ exists that is zero for loops, zero for pure noise, positive in between. Relates to effective complexity (Gell-Mann & Lloyd).
- **C3 (Scale-free topology):** Anti-loop constraint produces scale-free networks. **Preliminary simulation evidence supports this.**

### Speculative interpretations (honestly labeled)
S1: Time = complexity growth. S2: Space = graph topology. S4: Physics = emergent mutual constraint. S6: Existence is mathematically necessary (within the axiom system).

### Ethics
One rule: don't collapse another entity's state space. Harm = state-space contraction (loops or noise). Good = state-space expansion. Maps cleanly onto all recognized forms of harm and flourishing.

## Simulation status

### Topology experiment (C3) — POSITIVE
- 500-node graphs, 4-bit and 8-bit FSM memory, three connection strategies
- 8-bit results: α ≈ 2.0–2.2 (classic scale-free range), strategy-independent
- Max degree 10x controls, clustering 20–45x controls
- **Known flaws:** wrong null model (static Erdős-Rényi instead of growing random graph), crude MLE fit, node cap distortion, only 3 seeds

### Coupling experiment — NEGATIVE
- Measured fraction of transitions where neighbors changed outcome
- Converges to ~0.879 by N=50, independent of graph size
- This is a combinatorial artifact of the hash function, not an emergent constant
- 1/137 is not found at this level of measurement

## Priority work (what to build next)

### 1. Proper C3 test (HIGHEST PRIORITY)
- Replace Erdős-Rényi control with **growing random graph** (matched growth rate, no anti-loop dynamics)
- Apply **Clauset-Shalizi-Newman** method (use `powerlaw` Python package)
- Run **30+ seeds** per condition
- Sensitivity analysis: loop pressure threshold, spawn probability, hash function (XOR vs SUM vs PRODUCT), initial topology
- Separate growth-phase topology from edge-only-at-cap-phase topology
- Target: publishable result or honest falsification

### 2. 1/f analysis (O9)
- Measure power spectral density of node state trajectories
- Vary "temperature" (controlled randomness injection)
- Test whether β = 1 corresponds to maximum structured complexity
- Compare to known 1/f signatures in neural data

### 3. Formalize C1 (O3)
- Implement effective complexity measure on trajectories
- Compare to Kolmogorov complexity, Lempel-Ziv, Tononi's Φ
- Test whether the consciousness band has a canonical definition

### 4. Distributed consciousness simulation (O11)
- Model hub removal from a stable graph
- Measure degradation of distributed representations
- Compare edge-loss-rate effects to known dementia progression patterns

## Technical notes

### Python environment
- numpy, networkx, matplotlib for simulation
- `powerlaw` package needed for Clauset-Shalizi-Newman test (`pip install powerlaw`)
- scipy for curve fitting and statistical tests

### Simulation design principles
- Every design choice must follow from the axioms, not from what we hope to find
- Always include proper controls — wrong null models waste everyone's time
- Report negative results honestly — the coupling experiment is in the repo for a reason
- Cap node count to prevent exponential blowup (nodes under loop pressure spawn aggressively)
- Limit stressed-node actions per step (max 5) to control growth rate
- Use multiple random seeds (minimum 30 for publishable results)

### Time budget calibration (IMPORTANT)
Every experiment must respect its `time_budget` parameter. The calibration must measure the **full per-seed pipeline**, not just one component. For example, if a seed involves growth + MI computation + control + analysis, calibrate ALL of those together. A common bug is calibrating only the cheapest step (e.g., graph growth) and underestimating the total by 10-20x. After writing calibration code, verify that the experiment actually finishes within its budget by running with `--quick` and checking wall-clock time.

### GUI rule
Always run experiments with GUI. The `--nogui` flag has been removed. All experiments display a progress window showing phase, progress bar, and log output. If the system doesn't support GUI (headless, no display), the runner falls back to headless mode automatically. Never add a `--nogui` flag — the fallback handles it.

### FSM node design
- Node = (config_space, current_config, visited_set, transition_table)
- Transition: T(config, input_hash) → new_config
- Input hash: XOR of neighbor configs mod config_space (but test alternatives — this choice has hidden consequences, XOR is commutative and self-inverse)
- Loop pressure: |visited| / |config_space|, threshold typically 0.7

### Hash function warning
XOR hash is commutative and self-inverse, meaning neighbor order doesn't matter and duplicate configs cancel. This is a strong structural assumption. Always test with at least SUM and PRODUCT alternatives to check whether results are hash-dependent.

## Style and tone

- This project walks the line between formal mathematics and philosophical speculation. The key discipline is **never confusing the two**.
- Everything in Part I (T1–T6) must be rigorous. Everything in Part III (S1–S6) must be honestly labeled as speculation. Part II (C1–C3) is the active research frontier.
- When writing for this project, prefer clarity over impressiveness. A clean negative result is worth more than a hand-wavy positive one.
- The project has both English and Polish audiences. Karol may work in either language.

## Key references

- Wheeler (1990): "It from bit"
- Smolin (1992–2013): Cosmological natural selection, evolving laws
- Tononi (2004): Integrated Information Theory (Φ)
- Gell-Mann & Lloyd (2004): Effective complexity
- Clauset, Shalizi & Newman (2009): Power-law distributions in empirical data
- Barabási & Albert (1999): Scale-free networks
- Okamoto (2023): Law of increasing organized complexity (arXiv:2302.07123)
- Kowalczyk (2025): Consciousness as Collapsed Computational Time (DOI: 10.5281/zenodo.17556941)

## Contact

Karol Kowalczyk — co-founder of AIRON Games, github.com/KarolFilipKowalczyk
