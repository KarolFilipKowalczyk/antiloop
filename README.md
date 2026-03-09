# antiloop

<p align="center">
  <img src="logo/antiloop_logo.svg" alt="antiloop logo" width="600"/>
</p>

**Deriving node deceleration in network growth from finite automata under a no-repeat constraint.**

---

## The anti-loop theorem

An automaton with C states and encoding quality D must revisit an effective state within C × D + 1 steps (pigeonhole). Flat encoding gives D = C regardless of connectivity. Hierarchical encoding gives D = C^k. Under spawning-on-loop, well-connected nodes reproduce exponentially slower. This is anti-preferential attachment — derived, not assumed.

## Central result

Inter-spawn intervals jump **8.9x** from degree 1 to degree 2 under polynomial hashing (10 seeds, 1000 nodes, C=256). Under flat encoding, intervals are constant. A random-spawning control (same encoding, fixed-probability spawn) also shows constant intervals — proving deceleration requires the anti-loop constraint. Three hash functions tested; result is robust (spread < 0.1).

Paper: [`paper/antiloop_short.md`](paper/antiloop_short.md)

## Running experiments

```bash
pip install numpy networkx matplotlib scipy powerlaw

python -m simulation.run universality --scale 0        # smoke test
python -m simulation.run universality                   # 10 seeds, 1000 nodes
python -m simulation.run hierarchical_network           # flat vs hierarchical
python -m simulation.run birthday_prediction            # isolated automaton
```

## License

CC BY 4.0 · Karol Kowalczyk & Claude (Anthropic)
