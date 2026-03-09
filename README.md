# antiloop

<p align="center">
  <img src="logo/antiloop_logo.svg" alt="antiloop logo" width="600"/>
</p>

**A sufficient condition for degree-dependent deceleration in network growth from finite automata under a no-repeat constraint.**

---

## The idea

Nodes are Mealy machines with encoding functions that compress neighbor inputs. Under a no-repeat constraint (no revisiting effective states), the encoding's discriminability determines how long a node runs before it must spawn. Hierarchical encoding (D = C^k) makes well-connected nodes slower. Flat encoding (D = C) does not. The state-space bound is pigeonhole; the application to network growth is the contribution.

## Central result

A random-spawning control — hierarchical encoding but fixed-probability spawn instead of loop detection — shows constant intervals across all degrees (alpha = 2.86). The same encoding with loop-triggered spawning shows intervals jumping **8.9x** from degree 1 to degree 2. This isolates the no-repeat constraint as the necessary mechanism. Three hash functions tested; result is robust. Distributions are not strict power laws (lognormal fits better per CSN testing).

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
