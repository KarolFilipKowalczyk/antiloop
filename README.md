# antiloop

<p align="center">
  <img src="logo/antiloop_logo.svg" alt="antiloop logo" width="600"/>
</p>

**A minimal formal framework that derives hierarchy, reproduction, and scale-free topology from three axioms and one modeling choice.**

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

This produces hierarchy, reproduction, scale-free topology, and lazy evaluation — none of it assumed.

## The blindness theorem

The key formal result. An entity distinguishing D < s^k input patterns from k connections must revisit an effective state within C × D + 1 steps. Hierarchical encoding is exponentially better than flat encoding. This makes restructuring practically inevitable, not chosen. Proved for worst case; general case is open (O9).

## Simulation results

- **Scale-free topology:** α ≈ 2.18 (spawn model), α ≈ 2.47 (LPAN model, 30 seeds, CSN confirmed)
- **MI excess on edges:** ρ ≈ 1.15 (29σ over 30 seeds) — anti-loop edges carry more mutual information than non-edges
- **Three growth phases:** expansion → deceleration → structure, emerging from depth distribution

## What the model does NOT claim

It is not physics — no force laws, no constants, no dimensions. It is not a consciousness explanation. It is not the only model that could produce these features. The target is structural isomorphism, not strong isomorphism. See Section 10 of the paper for full disclaimers.

## Repository structure

```
antiloop/
├── paper/lazy_universe_v4.md   — the current paper (authoritative)
├── open_problems.md            — O1–O9 for v4
├── archive/                    — historical material (v01/v02 theory, essays, old simulations)
└── logo/                       — the antylope
```

## Authors

**Karol Kowalczyk** — axioms, core intuitions, philosophical interpretation
**Claude** (Anthropic) — formalization, simulation, adversarial review

## License

CC BY 4.0
