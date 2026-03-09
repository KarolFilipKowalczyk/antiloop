# CLAUDE.md — Project Instructions for Claude Code

## What is antiloop?

A short paper deriving node deceleration in network growth from finite automata under a no-repeat constraint. The project name is a bilingual pun: antiloop / antylopa (Polish for antelope). Logo: a geometric running antelope whose trail never crosses itself.

## The anti-loop theorem

**A1 (Existence).** Each node is a finite deterministic automaton with C states and a transition function δ: S × I → S.

**A2 (Anti-loop).** The trajectory visits each state at most once.

**A3 (Boundedness).** C is finite and cannot increase.

**M1 (Spawn).** When the automaton exhausts its trajectory, it may create a new automaton whose output becomes part of the parent's input.

**The theorem:** An automaton with C states and encoding quality D must revisit an effective state within C × D + 1 steps (pigeonhole). Flat encoding: D = C regardless of connectivity. Hierarchical encoding: D = C^k. The gap is exponential.

**The consequence:** Well-connected nodes reproduce slower. This is anti-preferential attachment — derived, not assumed. Dorogovtsev-Mendes (2000) imposed deceleration as a parameter. This theorem derives it.

## Key results

- Hierarchical network: α = 1.976 ± 0.002 (10 seeds, 1000 nodes) vs flat α = 2.90
- Isolated entity: 34x lifetime ratio at k=3 (hierarchical vs flat)
- Entity lifetime CV = 0.524 ± 0.014 (predicted: 0.523, Rayleigh invariant)
- Inter-spawn intervals constant under flat, 3x jump per degree under hierarchical

## Repository structure

```
antiloop/
├── CLAUDE.md                    ← you are here
├── README.md
├── paper/
│   └── antiloop_short.md        — the paper (authoritative)
├── simulation/
│   ├── run.py                   — experiment runner
│   ├── experiments/             — three experiments
│   │   ├── birthday_prediction.py
│   │   ├── hierarchical_encoding.py
│   │   └── hierarchical_network.py
│   └── shared/                  — engine and utilities
├── open_problems.md             — O1–O3
├── archive/                     — all historical material
└── logo/                        — the antylope
```

## Style and discipline

- Prefer clarity over impressiveness.
- Report negative results honestly.
- Keep disclaimers prominent.
- Do not use "must" in a dynamical sense when you mean a characterization sense.

## Technical stack

- Python: numpy, networkx, matplotlib, scipy, powerlaw
- Experiment runner: `python -m simulation.run <name> [--quick|--long|--scale N]`
- Experiments auto-discover from `simulation/experiments/` (need `TITLE` + `run()`)
- GUI progress window shown when available

## Key references

- Dorogovtsev & Mendes (2000): Evolution of networks with aging of sites
- Amaral, Scala, Barthélémy & Stanley (2000): Classes of small-world networks
- Barabási & Albert (1999): Emergence of scaling in random networks
- Broido & Clauset (2019): Scale-free networks are rare
- Clauset, Shalizi & Newman (2009): Power-law distributions in empirical data
- Kim & Montenegro (2008): A birthday paradox for Markov chains

## Contact

Karol Kowalczyk — co-founder of AIRON Games, github.com/KarolFilipKowalczyk
