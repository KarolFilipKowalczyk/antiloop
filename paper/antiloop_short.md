# Anti-Preferential Attachment from Finite Automata

**Why well-connected nodes get slower: a derivation from bounded memory**

Karol Kowalczyk · March 2026

---

## Abstract

Network growth models require assumptions about how node activity changes with connectivity. Preferential attachment assumes well-connected nodes attract more connections. Aging models (Dorogovtsev & Mendes, 2000) impose deceleration as a parameter. We derive deceleration instead. If nodes are finite automata under a no-repeat constraint, then encoding quality determines effective state space, and well-connected nodes with hierarchical encoding take exponentially longer to exhaust their states. The central result: under polynomial hashing, the inter-spawn interval increases 8.9x from degree 1 to degree 2 (10 seeds, 1000 nodes, C = 256). Under flat encoding, intervals are constant across all degrees. A random-spawning control — same hierarchical encoding but spawning at fixed probability instead of on loop detection — also shows constant intervals (alpha = 2.86), confirming that deceleration requires both hierarchical encoding and the anti-loop constraint. The degree of deceleration tracks encoding quality: stronger encodings produce more deceleration (polynomial 8.9x, FNV 7.8x, additive 1.4x per degree step). The resulting degree distributions are heavier-tailed than flat encoding, though not strict power laws (lognormal fits better in all cases per Clauset-Shalizi-Newman testing).

---

## 1. Setup

Each node is a finite deterministic automaton with C internal states, receiving input from k connections. The automaton may not revisit a state (the anti-loop rule). When it exhausts its trajectory, it spawns a new automaton, creating a connection.

The automaton's **encoding** is a preprocessing step that maps s^k possible input patterns to D distinguishable categories before they enter the transition function. The **effective state space** is C × D: the automaton can occupy C internal states, each paired with D perceived inputs. After C × D + 1 steps, it must revisit an effective state (pigeonhole), and the deterministic transition function forces a loop.

The full model is a finite automaton with a preprocessing stage — equivalently, a Mealy machine with structured input. The encoding is not part of the automaton's transition function; it determines how raw inputs are compressed before the automaton processes them. Different encodings on the same automaton produce different effective state spaces and therefore different loop times.

---

## 2. The Anti-Loop Theorem

**Theorem.** An automaton with C states and encoding quality D must revisit an effective state within C × D + 1 steps.

*Proof.* Pigeonhole on C × D effective states. ∎

**Flat encoding** (e.g., XOR hash): D = C regardless of the number of connections k. Adding connections does not increase the effective state space.

**Hierarchical encoding** (e.g., polynomial hash): D = C^k. Each connection multiplies the number of distinguishable input patterns by C.

Under stochastic inputs, the birthday paradox gives expected lifetime sqrt(pi*C*D/2). For flat encoding this is O(C), independent of k. For hierarchical encoding this is O(C^((k+1)/2)), exponential in k.

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

Lifetime CV = 0.524 +/- 0.014 across C = 16-128 (predicted: 0.523, the Rayleigh invariant).

### 3.2 Growing network: inter-spawn intervals

This is the central test. The anti-loop theorem predicts that under hierarchical encoding, inter-spawn intervals should increase with degree. Under flat encoding, they should be constant.

Spawn model, C = 256, 1000 nodes, 10 seeds. Four encoding functions tested, plus a random-spawning control:

**Inter-spawn interval at degree 1 vs degree 2:**

| Encoding | Interval deg=1 | Interval deg=2 | Ratio | Growth speed |
|---|---|---|---|---|
| Flat (XOR) | 267 | 260 | **1.0x** | baseline |
| Polynomial | 309 | 2743 | **8.9x** | 3.8x slower |
| FNV | 307 | 2388 | **7.8x** | 3.7x slower |
| Additive | 278 | 394 | **1.4x** | 1.3x slower |
| Random control | 129 | 127 | **1.0x** | -- |

Under flat encoding, intervals are constant across all degrees (slope = -0.004). Under polynomial and FNV hashing, intervals jump sharply at degree 2 — well-connected nodes reproduce dramatically slower. Under additive hashing, the jump is smaller. The additive hash is weaker because addition is more collision-prone than multiplication: distinct input vectors (e.g., [1,2] and [2,1] weighted by position) can produce the same sum, reducing the effective number of distinguishable patterns below C^k.

The deceleration tracks encoding quality, as the theorem predicts: stronger encoding -> larger D_eff -> more deceleration. This is not a free parameter — it is a consequence of the hash function's ability to distinguish input patterns.

**Random-spawning control.** The random control uses polynomial (hierarchical) encoding but spawns with fixed probability per node per step instead of on loop detection. Result: intervals are constant across all degrees (~129), and the degree distribution matches flat encoding (alpha = 2.86). This confirms that deceleration requires *both* hierarchical encoding *and* loop-triggered spawning. The anti-loop constraint is essential — encoding quality alone is not sufficient.

### 3.3 Growing network: degree distributions

The deceleration produces heavier-tailed degree distributions. Full Clauset-Shalizi-Newman analysis (10 seeds, 1000 nodes, C = 256):

| Encoding | Fitted alpha | xmin | Tail fraction | PL vs lognormal |
|---|---|---|---|---|
| Flat (XOR) | 2.87 +/- 0.02 | 2 | 50% | Lognormal better (R = -4.6) |
| Polynomial | 1.92 +/- 0.00 | 1 | 100% | Lognormal better (R = -27) |
| FNV | 1.92 +/- 0.00 | 1 | 100% | Lognormal better (R = -27) |
| Additive | 2.02 +/- 0.00 | 1 | 100% | Lognormal better (R = -13) |

**Important caveat:** In all conditions — including flat — lognormal fits better than power law. The distributions are heavy-tailed but not strict power laws. The fitted alpha values characterize the shape of the full distribution, not a power-law tail. At 1000 nodes with maximum degree ~20, there is insufficient range for reliable power-law claims. The alpha values are reported for comparison across conditions, not as evidence of power-law behavior.

The ordering is robust: polynomial and FNV produce the heaviest tails (alpha ~ 1.92), additive is intermediate (2.02), flat is lightest (2.87). This ordering matches the inter-spawn interval ratios exactly.

---

## 4. Comparison to Existing Models

| Model | Deceleration mechanism | Derived or imposed? |
|---|---|---|
| Barabasi-Albert (1999) | None (rich get richer) | -- |
| Dorogovtsev-Mendes (2000) | Aging parameter tau^(-a) | Imposed |
| Amaral-Stanley (2000) | Connection costs/capacity | Imposed |
| **This paper** | Encoding quality (anti-loop theorem) | **Derived** |

The anti-loop theorem provides the mechanism that aging models assume. The deceleration is not a parameter — it is a consequence of finite memory under a no-repeat constraint. The degree of deceleration is determined by encoding quality, which is itself a property of the hash function mapping inputs to distinguishable categories.

---

## 5. Limitations

The theorem is elementary (one-line pigeonhole proof). The novelty is the application to network growth: pointing the pigeonhole at encoding quality x connectivity and observing that it produces anti-preferential attachment.

The model is a finite automaton with a preprocessing stage, not a pure finite automaton. A more rigorous formulation would characterize which classes of transition functions (without external preprocessing) correspond to "flat" vs "hierarchical" effective state spaces.

The simulation is at moderate scale (1000 nodes). The degree distributions are not power laws — they are heavy-tailed, with lognormal fitting better in all cases. The alpha values are shape parameters for comparison, not evidence of power-law scaling. Larger simulations (10^4-10^5 nodes) would clarify the distributional form.

The general case — tight bounds under input-dependent transition functions and correlated inputs — is open.

The model does not claim to replace preferential attachment. Both mechanisms may operate in real networks. The contribution is showing that deceleration can be derived rather than assumed.

---

## References

Amaral, L.A.N., Scala, A., Barthelemy, M. & Stanley, H.E. (2000). Classes of small-world networks. *PNAS*, 97(21), 11149-11152.

Barabasi, A.-L. & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509-512.

Broido, A.D. & Clauset, A. (2019). Scale-free networks are rare. *Nature Communications*, 10, 1017.

Clauset, A., Shalizi, C.R. & Newman, M.E.J. (2009). Power-law distributions in empirical data. *SIAM Review*, 51(4), 661-703.

Dorogovtsev, S.N. & Mendes, J.F.F. (2000). Evolution of networks with aging of sites. *Physical Review E*, 62(2), 1842-1845.

Kim, J.H. & Montenegro, R. (2008). A birthday paradox for Markov chains. *Annals of Applied Probability*, 20(2), 495-521.
