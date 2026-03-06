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
│   └── fermi_post_draft.md           — forum post: Fermi paradox dissolution
├── simulation/
│   ├── engine.py                      — shared core: FSMNode, hash functions, run_antiloop, controls
│   ├── gui.py                         — ANTILOOP GUI progress window (always on)
│   ├── run.py                         — unified entry point, auto-discovers experiments
│   ├── experiments/
│   │   ├── c1_complexity.py           — C1 consciousness band (inter-node MI) ✓ POSITIVE
│   │   ├── c1_hash_robustness.py      — C1 hash robustness (XOR/SUM/PRODUCT) ✓ ROBUST
│   │   ├── c2_suffering.py            — C2 suffering (edge loss) ✓ THRESHOLD POSITIVE
│   │   ├── c2_targeted_suffering.py   — C2v2 targeted suffering (MI-ranked removal) ✓ POSITIVE (inverted)
│   │   ├── c3_topology.py             — C3 scale-free topology ✓ POSITIVE (30 seeds, CSN)
│   │   ├── coupling.py                — coupling constant test ✗ NEGATIVE
│   │   └── o9_spectral.py             — O9 1/f spectral analysis ✗ NEGATIVE (v1, v2 planned)
│   └── results/                       — plots and raw output
└── open_problems.md                   — O1–O17, living document
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
- **C1 (Consciousness band):** Inter-node MI ratio ρ = MI(edges)/MI(non-edges). Anti-loop ρ = 1.15, control ρ = 1.00. **POSITIVE (30 seeds, 2.1σ, hash-robust).**
- **C2 (Suffering):** Random edge removal = no gradual contraction. **NEGATIVE for gradient**, T1 confirmed at total isolation (55-67% MI drop, 87-91% unique config drop).
- **C2v2 (Targeted suffering):** Removing diverse (low growth-MI) connections hurts more than removing redundant (high growth-MI) ones. **POSITIVE (inverted, 30 seeds, 27/30 consistent, t=-8.61).** Follows from anti-loop logic: novelty-bearing edges are load-bearing.
- **C3 (Scale-free topology):** Anti-loop produces alpha = 2.47 (classic range), power law preferred 30/30. **POSITIVE (CSN method, growing random control).**

### Speculative interpretations (honestly labeled)
S1: Time = complexity growth. S2: Space = graph topology. S4: Physics = emergent mutual constraint. S6: Existence is mathematically necessary (within the axiom system).

### Ethics
One rule: don't collapse another entity's state space. Harm = state-space contraction (loops or noise). Good = state-space expansion. Maps cleanly onto all recognized forms of harm and flourishing.

## Simulation status

### C1 Consciousness band — POSITIVE
- 30 seeds, 500 nodes, 8-bit FSM, XOR hash
- MI ratio ρ = 1.15 (anti-loop) vs 1.00 (control), 2.1σ, 30/30 consistent
- Hash robustness: XOR=1.14, SUM=1.15, PRODUCT=1.17 (all pass)

### C2 Suffering (random edge loss) — NEGATIVE (gradient), T1 CONFIRMED
- 7 seeds, 500 nodes, 8-bit FSM, progressive edge removal
- Partial removal (25-75%): no significant effect (1.6% hub MI loss at 75%)
- Per-remaining-edge MI stays flat (~6.2) — no gradual contraction
- Total isolation (100%): catastrophic (55-67% MI drop, 87-91% unique config drop)
- Verdict: NEGATIVE for gradient suffering. T1 confirmed at isolation.

### C3 Scale-free topology — POSITIVE
- 30 seeds, 500 nodes, 8-bit FSM, Clauset-Shalizi-Newman method
- Anti-loop alpha = 2.47 +/- 0.14 (classic scale-free 2-3)
- Power law preferred over exponential: 30/30 runs
- Control alpha = 2.62 +/- 0.27 but exponential fits better
- Hash-robust (spread = 0.04), insensitive to pressure threshold
- Caveat: control also in scale-free alpha range; distinction is fit quality

### C2v2 Targeted suffering — POSITIVE (inverted)
- 30 seeds, 500 nodes, 8-bit FSM, moderate-degree targets (deg ~16)
- MI ranked from GROWTH-PHASE trajectories (not fresh post-hoc dynamics)
- Growth MI spread: 1.2-2.0x (mean 1.6x; early edges have more shared history)
- Key finding: removing LOW growth-MI (diverse) edges hurts MORE
  - High-MI removal: 98.6 MI at 50% removal (~0% loss)
  - Low-MI removal: 92.5 MI at 50% removal (6.2% loss)
  - Gap: -6.2% of baseline, t=-8.61, 27/30 consistent
- Interpretation: high growth-MI = redundant (similar trajectories, expendable)
  low growth-MI = diverse (novel information, load-bearing)
- This follows directly from anti-loop axioms: novelty prevents loops,
  so connections that bring novel information are the critical ones
- Previous C2 (random removal) missed this because it treated all edges as equal
- Bridges C1 (edges carry MI) with C2 (loss = contraction): the QUALITY of lost
  edge matters, not just the quantity

### Coupling experiment — NEGATIVE
- Measured fraction of transitions where neighbors changed outcome
- Converges to ~0.879 by N=50, independent of graph size
- This is a combinatorial artifact of the hash function, not an emergent constant

## Priority work (what to build next)

### 1. C1-C3 bridge (O14)
- Do hub edges carry more MI than leaf edges?
- Does MI ratio predict degree distribution?
- Would unify the two major positive results

### 2. C1 temporal evolution (O15)
- Measure MI ratio during growth phase
- Does it increase over time? Connection to S1 (time = complexity growth)

### 3. Memory scaling (O17)
- Run C1 and C2 across mem_bits = 2, 4, 6, 8, 10, 12
- Find the memory sweet spot for consciousness band
- Test whether C2 gradient emerges at low memory

### 4. O9v2 spectral analysis
- Graph-level observables during growth (not per-node post-growth)
- Mathematically natural noise models (mutation, dropout)
- Test for 1/f signatures

### 5. Distributed consciousness (O11)
- Hub removal vs random node removal
- Catastrophic MI collapse vs graceful degradation

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
