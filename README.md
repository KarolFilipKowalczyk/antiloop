# antiloop

<p align="center">
  <img src="logo/antiloop_logo.svg" alt="antiloop logo" width="600"/>
</p>

**A minimal formal framework that derives hierarchy, reproduction, and heavy-tailed topology from three axioms and one modeling choice.**

---

## The framework (v4)

Three axioms constrain a finite deterministic system:

- **A1 (Existence).** A finite set of states, a deterministic transition function, an initial state.
- **A2 (Anti-loop).** The trajectory visits each state at most once.
- **A3 (Boundedness).** The state space is finite and cannot increase.

One modeling choice provides a mechanism:

- **M1 (Spawn).** When all trajectories are exhausted, the system may create a new finite deterministic system whose output becomes part of the parent's input.

## What falls out

Three pigeonhole arguments cycle at every scale:

1. Bounded memory under anti-loop → must spawn (Pigeonhole 1)
2. Spawning creates connections → exponential input → flat encoding fails (Pigeonhole 2, **blindness theorem**)
3. Hierarchical encoding saturates under growing connections → must spawn again (Pigeonhole 3)

This produces hierarchy, reproduction, heavy-tailed topology, and lazy evaluation — none of it assumed.

## The blindness theorem

The key formal result. An entity distinguishing D < s^k input patterns from k connections must revisit an effective state within C × D + 1 steps (worst case). Under stochastic inputs, expected loop time is Θ(√(C · D_eff)) where D_eff = 1/Σ Q(j)² measures encoding quality. Hierarchical encoding is exponentially better than flat encoding in both cases. See `paper/blindness_theorem_general.md` for the general case proof.

## Simulation results

- **Heavy-tailed topology:** spawn model α ≈ 2.05 at 44k nodes (30 seeds). Heavy-tailed and hub-dominated, better fit by lognormal than pure power-law at large scale — consistent with Broido & Clauset (2019). Random tree control: α ≈ 2.85 (massive separation). LPAN model: α ≈ 2.47 (30 seeds, CSN confirmed at small scale).
- **MI excess on edges:** ρ ≈ 1.15 (29σ over 30 seeds) — anti-loop edges carry more mutual information than non-edges
- **Three growth phases:** expansion -> transition -> plateau, confirmed 10/10 seeds. At 8-bit memory, Phase 2 is sharp (~16 steps). Phase 2 width scales as ~sqrt(C) with memory size (O5c), becoming an extended era at larger configuration spaces.

## What the model does NOT claim

It is not physics — no force laws, no constants, no dimensions. It is not a consciousness explanation. It is not the only model that could produce these features. The target is structural isomorphism, not strong isomorphism. See Section 10 of the paper for full disclaimers.

## Running experiments

```bash
pip install numpy networkx matplotlib scipy powerlaw

python -m simulation.run <experiment> --scale 0   # 15s,  1 seed  (smoke test)
python -m simulation.run <experiment> --quick      # 60s,  3 seeds
python -m simulation.run <experiment>              # 300s, 10 seeds (default)
python -m simulation.run <experiment> --long       # 900s, 30 seeds (publishable)
python -m simulation.run <experiment> --scale 4    # 3600s, 30 seeds, 2k nodes, 10-bit (deep)
```

Scale presets control time, seeds, nodes, and mem_bits together. Individual flags (`--time`, `--seeds`, `--nodes`, `--mem`) override any preset. Experiments auto-discover from `simulation/experiments/`. GUI progress window with CUDA detection is shown when available.

## Repository structure

```
antiloop/
├── paper/
│   ├── lazy_universe_v4.md             — the current paper (authoritative)
│   └── blindness_theorem_general.md    — O9 general case proof
├── simulation/
│   ├── run.py                          — experiment runner (--quick/--long)
│   ├── gui.py                          — progress window
│   ├── experiments/                    — auto-discovered experiments
│   └── shared/                         — common utilities
├── open_problems.md                    — O1–O9 for v4
├── archive/                            — historical material
└── logo/                               — the antylope
```

## Authors

**Karol Kowalczyk** — axioms, core intuitions, philosophical interpretation
**Claude** (Anthropic) — formalization, simulation, adversarial review

## License

CC BY 4.0
