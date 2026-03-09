# Anti-Preferential Attachment from Finite Automata

**Why well-connected nodes get slower: a derivation from bounded memory**

Karol Kowalczyk · March 2026

---

## Abstract

Network growth models require assumptions about how node activity changes with connectivity. Preferential attachment assumes well-connected nodes attract more connections. Aging models (Dorogovtsev & Mendes, 2000) impose deceleration as a parameter. We derive deceleration instead. If nodes are finite automata under a no-repeat constraint, then encoding quality determines effective state space, and well-connected nodes with hierarchical encoding take exponentially longer to exhaust their states. This produces anti-preferential attachment — connectivity as cost, not benefit — yielding degree exponents α = 1.92–2.02 across three different hierarchical hash functions (10 seeds each, 1000 nodes), closer to empirical networks than standard preferential attachment (α = 3). The exponent tracks encoding quality: stronger hashes produce more deceleration and lower α.

---

## 1. Setup

Each node is a finite deterministic automaton with C internal states, receiving input from k connections. The automaton may not revisit a state (the anti-loop rule). When it exhausts its trajectory, it spawns a new automaton, creating a connection.

The automaton's **encoding** maps s^k possible input patterns to D distinguishable categories. The **effective state space** is C × D: the automaton can occupy C internal states, each paired with D perceived inputs. After C × D + 1 steps, it must revisit an effective state (pigeonhole), and the deterministic transition function forces a loop.

---

## 2. The Anti-Loop Theorem

**Theorem.** An automaton with C states and encoding quality D must revisit an effective state within C × D + 1 steps.

*Proof.* Pigeonhole on C × D effective states. ∎

**Flat encoding** (e.g., XOR hash): D = C regardless of the number of connections k. Adding connections does not increase the effective state space.

**Hierarchical encoding** (e.g., polynomial hash): D = C^k. Each connection multiplies the number of distinguishable input patterns by C.

Under stochastic inputs, the birthday paradox gives expected lifetime √(πCD/2). For flat encoding this is O(C), independent of k. For hierarchical encoding this is O(C^((k+1)/2)), exponential in k.

**Consequence for networks.** Under spawning-on-loop, lifetime equals inter-spawn interval. Flat-encoding nodes reproduce at constant rate. Hierarchical-encoding nodes reproduce exponentially slower as they gain connections. This is anti-preferential attachment — derived from the theorem, not assumed.

---

## 3. Simulation

### 3.1 Isolated automaton

C = 64, k = 1, 2, 3 neighbors, 10,000 trials per condition.

| k | Flat lifetime | Hierarchical lifetime | Ratio |
|---|---|---|---|
| 1 | ~80 | ~80 | 1x |
| 2 | ~80 | ~643 | 8x |
| 3 | ~80 | ~2641 | 34x |

log(lifetime) vs k: slope = 1.75, predicted log(C)/2 = 2.08, R² = 0.99.

Lifetime CV = 0.524 ± 0.014 across C = 16–128 (predicted: 0.523, the Rayleigh invariant).

### 3.2 Growing network

Spawn model, C = 256, 1000 nodes, 10 seeds. Flat (XOR) vs hierarchical (polynomial hash).

| Metric | Flat encoding | Hierarchical encoding |
|---|---|---|
| Degree exponent α | 2.90 ± 0.04 | **1.920 ± 0.002** |
| Inter-spawn interval slope vs degree | −0.004 (constant) | **+0.18 (increasing)** |
| Interval ratio deg=1 → deg=2 | 1.0x | **8.8x** |
| Growth speed | baseline | 1.9x slower |

Hierarchical encoding produces a heavier tail because reproduction concentrates at low-degree nodes. High-degree nodes are penalized by their own connectivity.

### 3.3 Universality across encodings

Does α depend on the specific hash function, or is it a property of any hierarchical encoding? Three hierarchical hash functions tested (10 seeds, 1000 nodes, C = 256, full Clauset-Shalizi-Newman analysis):

| Hash function | D_eff scaling | α mean ± std |
|---|---|---|
| Flat (XOR) | C (constant) | 2.869 ± 0.021 |
| Polynomial | C^k (strong) | **1.920 ± 0.002** |
| FNV | C^k (strong) | **1.923 ± 0.002** |
| Additive (position-weighted) | < C^k (weak) | **2.018 ± 0.003** |

The two strong hashes (polynomial and FNV) produce nearly identical exponents. The weaker additive hash produces a slightly higher α — less deceleration, heavier-but-less-heavy tail. The exponent tracks encoding quality, as the theorem predicts: stronger encoding → larger D_eff → more deceleration → lower α.

CSN comparison: in all cases, lognormal and stretched-exponential fit better than strict power law (all R < 0, p < 0.001). The distributions are heavy-tailed but not pure power laws, consistent with Broido & Clauset (2019).

Inter-spawn intervals confirm the mechanism: flat encoding gives constant intervals across degrees (~265). Polynomial hash gives 8.8x jump from deg=1 to deg=2. FNV gives 7.7x. Additive gives only 1.4x — matching the α ordering.

---

## 4. Comparison to Existing Models

| Model | Deceleration mechanism | α | Derived or imposed? |
|---|---|---|---|
| Barabási-Albert (1999) | None (rich get richer) | 3.0 | — |
| Dorogovtsev-Mendes (2000) | Aging parameter τ^(-α) | tunable | Imposed |
| Amaral-Stanley (2000) | Connection costs/capacity | truncated | Imposed |
| **This paper** | Encoding quality (anti-loop theorem) | **1.92–2.02** | **Derived** |

The anti-loop theorem provides the mechanism that aging models assume. The deceleration is not a parameter — it is a consequence of finite memory under a no-repeat constraint.

---

## 5. Limitations

The theorem is elementary (one-line pigeonhole proof). The novelty is the application to network growth: pointing the pigeonhole at encoding quality × connectivity and observing that it produces anti-preferential attachment.

The network-level result (10 seeds, 1000 nodes, CSN tested) is stable across three hash functions but moderate scale. Larger testing (10⁴–10⁵ nodes) would strengthen the claim. CSN analysis shows lognormal beats strict power law in all cases — the distributions are heavy-tailed, not pure power laws.

The general case — tight bounds under input-dependent transition functions and correlated inputs — is open.

The model does not claim to replace preferential attachment. Both mechanisms may operate in real networks. The contribution is showing that deceleration can be derived rather than assumed.

---

## References

Amaral, L.A.N., Scala, A., Barthélémy, M. & Stanley, H.E. (2000). Classes of small-world networks. *PNAS*, 97(21), 11149–11152.

Barabási, A.-L. & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509–512.

Broido, A.D. & Clauset, A. (2019). Scale-free networks are rare. *Nature Communications*, 10, 1017.

Dorogovtsev, S.N. & Mendes, J.F.F. (2000). Evolution of networks with aging of sites. *Physical Review E*, 62(2), 1842–1845.

Kim, J.H. & Montenegro, R. (2008). A birthday paradox for Markov chains. *Annals of Applied Probability*, 20(2), 495–521.
