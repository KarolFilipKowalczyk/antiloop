# antiloop

<p align="center">
  <img src="logo/antiloop_logo.svg" alt="antiloop logo" width="600"/>
</p>

**Deriving node deceleration in network growth from finite automata under a no-repeat constraint.**

---

## The anti-loop theorem

If network nodes are finite automata that may not revisit a state, then encoding quality determines effective state space. An automaton with C states and encoding quality D must revisit an effective state within C × D + 1 steps (pigeonhole). Flat encoding gives D = C regardless of connectivity. Hierarchical encoding gives D = C^k, where k is the number of connections.

**Consequence:** well-connected nodes with hierarchical encoding take exponentially longer to exhaust their states, and therefore reproduce slower. This is anti-preferential attachment — derived, not assumed. Dorogovtsev & Mendes (2000) imposed deceleration as a parameter. Amaral, Scala, Barthélémy & Stanley (2000) imposed connection costs. The anti-loop theorem derives it.

## Simulation results

- **Growing network (10 seeds, 1000 nodes, C=256):** hierarchical encoding produces α = 1.976 ± 0.002 vs flat α = 2.90 ± 0.04. Inter-spawn intervals constant under flat, 3x jump per degree under hierarchical.
- **Isolated entity (C=64):** flat lifetime ~80 at all degrees. Hierarchical: 80/643/2641 at k=1/2/3 (34x ratio). log(lifetime) slope = 1.75, predicted log(C)/2 = 2.08, R² = 0.99.
- **Entity lifetime:** CV = 0.524 ± 0.014 (predicted: 0.523, the Rayleigh invariant). Zero free parameters.

## What this does NOT claim

It does not claim the universe is made of automata. It does not replace preferential attachment — both mechanisms may operate. The contribution is showing that deceleration can be derived rather than assumed.

## Running experiments

```bash
pip install numpy networkx matplotlib scipy powerlaw

python -m simulation.run hierarchical_network --scale 0   # 15s, smoke test
python -m simulation.run hierarchical_network --quick      # 60s, 3 seeds
python -m simulation.run hierarchical_network              # 300s, 10 seeds
python -m simulation.run hierarchical_network --long       # 900s, 30 seeds
```

Available experiments: `hierarchical_network`, `hierarchical_encoding`, `birthday_prediction`.

## Repository structure

```
antiloop/
├── paper/
│   └── antiloop_short.md          — the paper
├── simulation/
│   ├── run.py                     — experiment runner
│   ├── experiments/               — three experiments
│   └── shared/                    — engine and utilities
├── archive/                       — historical material (v1–v4 papers, old experiments)
└── logo/                          — the antylope
```

## Authors

**Karol Kowalczyk** — axioms, core intuitions
**Claude** (Anthropic) — formalization, simulation

## License

CC BY 4.0
