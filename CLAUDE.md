# CLAUDE.md — Project Instructions for Claude Code

## What is antiloop?

A minimal formal framework that derives hierarchy, reproduction, scale-free topology, and lazy evaluation from three axioms and one modeling choice. The project name is a bilingual pun: antiloop / antylopa (Polish for antelope). Logo: a geometric running antelope whose trail never crosses itself.

**The project has gone through multiple versions.** Old material (T1–T6, consciousness bands, Assumption N) has been archived. The current state of the theory is in `paper/lazy_universe_v4.md`.

## Current axioms (v4 — authoritative)

**Axiom 1 (Existence).** There exists a finite deterministic system — a set of states S, a transition function δ: S × I → S where I is the set of possible inputs, and an initial state s₀.

**Axiom 2 (Anti-loop).** The system's trajectory (s₀, s₁, s₂, …) visits each state at most once.

**Axiom 3 (Boundedness).** |S| is finite and cannot increase.

**Modeling choice M1 (Spawn).** When the system has exhausted all trajectories available within its current input set, it may create a new finite deterministic system (child) whose output becomes part of the parent's input set.

A1–A3 are mathematical constraints. M1 is a mechanism. Keep them separate. This allows exploring alternative mechanisms (merging, pruning, interference) without changing the axioms.

## What the axioms produce

From A1–A3 alone (provable):
- Trajectory length ≤ |S| (pigeonhole)
- k connections with s-valued signals → s^k input patterns (combinatorics)
- Hierarchical encoding gives exponentially more effective states than flat encoding (blindness theorem, proved for worst case)

From A1–A3 + M1 (derived):
- Spawning is forced when effective states are exhausted
- Each spawn creates a connection (input channel)
- Three-pigeonhole cycle produces hierarchy
- Degree ∝ age → heavy-tailed topology
- Lazy evaluation: only active comparisons contribute to loop avoidance
- Consensus: shared comparisons → matter; unique comparisons → mind

## The four design goals

The axiom set is designed to satisfy four criteria:
1. **Big-bang expansion** from a single node — one entity spawns, children spawn, rapid early growth decelerates
2. **Finite state machines as beings** — entities are finite deterministic systems with bounded memory under anti-loop constraint
3. **Reproduction** — forced by Pigeonhole 3 (saturated encoding + bounded memory + only spawn available)
4. **Structural isomorphism to the universe** — hierarchy, heavy-tailed topology, three growth phases, lazy evaluation, consensus vs. private information. NOT quantitative physics (no force laws, no constants, no dimensions). The target is structural isomorphism, not strong isomorphism.

## Three contributions (keep separate)

The project contains three distinct contributions that should be treated as separate potential publications:

**Contribution A: The LPAN model (empirical, publishable now).** FSM nodes on growing graphs, edges formed under loop pressure, MI excess as measurable signature. Key results: ρ ≈ 1.15 (29σ), α ≈ 2.47 (CSN confirmed, 30 seeds). Stands alone as network science. Does not require comparison trees or lazy evaluation.

**Contribution B: The v4 framework (theoretical, needs more formal work).** Pigeonhole cascade, blindness theorem, comparison trees, lazy evaluation, matter as consensus. The formal core is the blindness theorem. Everything else is interpretation or simulation illustration. Needs: general-case blindness theorem (O9), variation mechanism for encoding, tetration proof (O3).

**Contribution C: Philosophical interpretation (speculative, keep in margins).** Consciousness requires novelty, ethics as state-space dynamics, Fermi paradox. This is where the project started. It has been correctly pushed to the margins by adversarial review. Keep it there. Blog posts or companion essays, explicitly labeled as speculation.

**Do not combine these into one document.** This has been the source of almost every structural problem in the project's history.

## Repository structure

```
antiloop/
├── CLAUDE.md                    ← you are here
├── README.md                    — v4 framework overview
├── paper/
│   ├── lazy_universe_v4.md      — the current paper (authoritative)
│   └── blindness_theorem_general.md — O9 general case proof
├── simulation/
│   ├── gui.py                   — tkinter progress window (visible-if-possible)
│   ├── run.py                   — unified experiment runner with time budgets
│   ├── experiments/             — auto-discovered experiments (TITLE + run())
│   ├── shared/                  — common utilities, CSN testing, plotting
│   └── results/                 — output plots and data
├── open_problems.md             — O1–O9 from v4 paper
├── archive/
│   ├── theory_v01.md            — original T1–T6 framework (historical)
│   ├── theory_v02.md            — post-adversarial-review (historical)
│   ├── complete_evaluation.md   — historical
│   ├── essays/                  — ethics, Fermi (historical)
│   ├── old_open_problems.md     — O1–O17 from early versions
│   └── old_simulation/          — original LPAN engine, experiments, results, visualization
└── logo/                        — the antylope
```

## Cleanup tasks (completed)

All six cleanup tasks have been completed:

1. ✓ Old material archived (`theory/`, `essays/` → `archive/`)
2. ✓ v4 paper in `paper/lazy_universe_v4.md`
3. ✓ README.md rewritten around v4 framework
4. ✓ `open_problems.md` rewritten with O1–O9 from v4
5. ✓ Old simulation code moved to `archive/old_simulation/`
6. ✓ No new simulation code written — old LPAN simulations preserved in archive

**O9 is the highest priority open problem.** The restricted-case blindness theorem is the strongest formal contribution. Extending it to environment-dependent dynamics would make the paper publishable in a theoretical CS venue.

## Known formal gaps (address before new features)

These are load-bearing problems. Do not build more structure on top of them.

1. ~~**Variation mechanism.**~~ **Resolved.** Children start blank — M1 creates a new system, not a copy. Different network positions → different inputs → different effective encodings. Variation is automatic. Added to paper Section 2.4.

2. **Child complexity guarantee.** v4 claims the child is "at least one comparison level more complex than the parent." This is stated but not proved. With "children start blank," children start at depth zero and deepen under Pigeonhole 2. The hierarchy still builds, but the claim about guaranteed generational increase is unsupported. Consider dropping or weakening the claim in Section 3.4.

3. **Tetration proof (O3).** Tower-of-powers capacity growth is derived under specific assumptions but not formally proved. "Derived but not proved" means "conjectured with a plausibility argument." Say that.

4. **Encoding uniqueness (O2).** The paper assumes comparison trees. Bounded-width circuits or DAGs could also provide logarithmic-access encoding. The blindness theorem applies to any hierarchical encoding, not specifically trees. Elevate this.

5. **Mutual constraint of shared comparisons (O6).** Physical laws constrain each other. Shared comparisons in the model merely coexist. Without mutual constraint, "matter as consensus" means "shared opinions," not "laws of physics." This is not a minor gap.

## Derivation chain status (be honest)

Classify every claim into exactly one of three tiers:

**Tier 1 — Proved:**
- Finite + deterministic → must loop (pigeonhole, classical)
- A loop produces no new states (determinism, classical)
- Solitary entity under A2 + A3 → must spawn via M1 (elimination)
- Spawning creates a connection (A1: environment in transition function)
- Connections → exponential input space (combinatorics)
- Flat encoding fails under exponential input (Pigeonhole 2)
- Blindness theorem, restricted case: indistinguishable inputs reduce effective state space (proved)

**Tier 2 — Conditionally derived (follows if specific assumptions hold):**
- Hierarchical encoding is a selection effect (variation from M1: children start blank, network position diversity)
- Finite encoding + growing connections → overwhelmed (Pigeonhole 3)
- Cycle repeats → hierarchy (structural recursion, depends on Tier 2 items above)
- Capacity grows by tetration (formal proof pending, O3)

**Tier 3 — Conjectured with simulation support:**
- Heavy-tailed topology (α ≈ 2.05 spawn model at 44k nodes, lognormal-like per Broido-Clauset; α ≈ 2.47 LPAN)
- Three growth phases with sharp Phase 2 transition (O5 confirmed 10/10 seeds; O5b variable memory confirms sharpness is fundamental)
- Edges carry MI excess (ρ ≈ 1.15, 29σ, LPAN model)
- Shared encodings → consensus structure (simulation)

**Never label a Tier 2 or Tier 3 claim as "derived" without qualification.**

## Style and discipline

- This project walks the line between formal mathematics and speculative interpretation. The key discipline is never confusing the two.
- A clean negative result is worth more than a hand-wavy positive one. The coupling constant experiment and the C2 gradient experiment are in the archive for a reason.
- When writing for this project, prefer clarity over impressiveness.
- The "What This Paper Does Not Claim" section is the paper's best feature after the blindness theorem. Keep disclaimers prominent.
- Do not use the word "must" in a dynamical sense ("the entity must restructure") when you mean it in a characterization sense ("any non-repeating trajectory through this space has this property"). The model has no agents. It has constraints on trajectories.
- Drop or substantially weaken the Bell test analogy (Section 4.1 of v4) until an actual inequality is defined. The structural resemblance is superficial without one.

## Technical stack

- Python: numpy, networkx, matplotlib, scipy, powerlaw
- `powerlaw` package for Clauset-Shalizi-Newman testing (`pip install powerlaw`)
- Experiment runner: `python -m simulation.run <name> [--quick|--long]`
  - `--quick`: 60s, 3 seeds (20s/seed) — smoke test
  - default: 300s, 10 seeds (30s/seed) — development
  - `--long`: 900s, 30 seeds (30s/seed) — publishable
  - `--seeds N --time N`: manual override
- Experiments auto-discover from `simulation/experiments/` (need `TITLE` + `run()`)
- GUI progress window shown when available, falls back to headless
- Always include proper controls and null models
- Report negative results honestly

## Key references

- Clauset, Shalizi & Newman (2009): Power-law distributions in empirical data
- Broido & Clauset (2019): Scale-free networks are rare
- Krapivsky, Redner & Leyvraz (2000): Connectivity of growing random networks
- Myhill (1957): Finite automata and the representation of events
- Nerode (1958): Linear automaton transformations
- Cover & Thomas (2006): Elements of Information Theory
- Shannon (1948): A mathematical theory of communication
- Kauffman (2000): Investigations
- Tononi (2004): An information integration theory of consciousness

## Priority work order

1. ~~**Repo cleanup** (tasks 1–6)~~ — done
2. ~~**Prove the blindness theorem, general case (O9)**~~ — proved for input-independent δ; general δ conjectured (see `paper/blindness_theorem_general.md`)
3. ~~**Address the variation mechanism gap**~~ — resolved: children start blank, variation from network position diversity
4. **Scale testing (O4)** — CSN at 10⁴–10⁵ entities
5. **Phase boundary validation (O5)** — test spawn-to-wire ratio and median encoding depth
6. Everything else

## Contact

Karol Kowalczyk — co-founder of AIRON Games, github.com/KarolFilipKowalczyk
