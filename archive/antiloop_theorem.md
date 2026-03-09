# The Anti-Loop Theorem

**Why Well-Connected Nodes Get Slower, Not Faster**

Karol Kowalczyk · March 2026 · Working Paper

---

## Abstract

Every major network growth model — from Barabási-Albert to Dorogovtsev-Mendes — must assume or impose how node activity changes with connectivity. Preferential attachment assumes the rich get richer. Aging models impose deceleration as a tunable parameter. This paper derives deceleration from first principles.

We model network nodes as finite deterministic automata under one constraint: no state may be revisited (the anti-loop rule). We prove the **anti-loop theorem**: an automaton's ability to avoid repeating states scales linearly with how well it encodes its inputs. Specifically, an automaton with C internal states and encoding quality D must revisit an effective state within C × D + 1 steps. Flat encoding gives D = C regardless of connectivity. Hierarchical encoding gives D = C^k, where k is the number of connections. The gap is exponential.

The consequence is immediate: well-connected nodes with hierarchical encoding take exponentially longer to exhaust their state spaces, and therefore reproduce slower. This is anti-preferential attachment — derived, not assumed. Dorogovtsev and Mendes (2000) had to impose aging as a parameter τ^(-α) to get deceleration. Amaral, Scala, Barthélémy and Stanley (2000) had to impose connection costs. The anti-loop theorem gets it for free.

Simulation confirms two zero-parameter predictions: entity lifetime follows a Rayleigh distribution with CV = 0.523 (measured: 0.524 ± 0.014), and log(inter-spawn interval) grows linearly with degree at slope log(C)/2 (measured: 1.75, predicted: 2.08, R² = 0.99). When hierarchical encoding drives a growing network, it produces α ≈ 1.97 — closer to empirical networks than flat encoding (α ≈ 2.88) or standard preferential attachment (α ≈ 3.0).

---

## 1. The Problem

Real networks have degree exponents near α ≈ 2. The Barabási-Albert model, which assumes new nodes preferentially attach to high-degree nodes, produces α = 3. Something must slow down well-connected nodes to produce heavier tails.

Dorogovtsev and Mendes (2000) solved this by multiplying the attachment probability by an aging factor τ^(-α), where τ is the node's age. As the aging parameter increases, the degree exponent drops from 3 toward 2. But the aging is imposed — a parameter chosen to fit the data.

Amaral, Scala, Barthélémy and Stanley (2000) took a different route: connection costs and capacity constraints. Nodes that accumulate too many connections stop accepting new ones. This produces truncated power laws. Again, the constraint is external.

Both approaches work. Neither explains *why* connectivity should be costly. They describe the deceleration; they do not derive it.

This paper provides the derivation. If a node is a finite automaton under a no-repeat constraint, then its encoding quality determines how long it can avoid repeating a state. Better-connected nodes with hierarchical encoding live longer — and therefore reproduce slower. Deceleration is not a parameter. It is a theorem.

---

## 2. Setup

Three assumptions and one mechanism.

**A1 (Existence).** Each node is a finite deterministic automaton: a finite set of C states, a transition function δ: S × I → S (where I is the set of possible inputs), and an initial state s₀.

**A2 (Anti-loop).** The automaton's trajectory visits each state at most once.

**A3 (Boundedness).** C is finite and cannot increase.

**M1 (Spawn).** When an automaton has exhausted its ability to avoid repeating states, it may create a new automaton whose output becomes part of the parent's input.

A1–A3 are mathematical constraints. M1 is a mechanism — the only assumed capability. Everything else is derived.

A1 is standard: finite automata are the simplest model of computation with memory. A2 is the constraint that creates all the pressure — without it, the automaton simply cycles forever. A3 prevents the trivial escape of growing your own state space. M1 is what remains when internal options are exhausted: produce something external.

Spawning creates a connection: the child's output enters the parent's input set. This is not a separate assumption — it follows from A1 (the transition function depends on environment) and the child now being part of that environment.

---

## 3. The Anti-Loop Theorem

### 3.1 Effective State Space

An automaton's trajectory — the sequence of states it visits — is determined step by step by the combination of its internal state and its perceived input. Call this the **effective state**. If the automaton has C internal states and can distinguish D input patterns, it has at most C × D effective states.

After C × D + 1 steps, the automaton must revisit an effective state (pigeonhole). Same internal state, same perceived input, deterministic transition → same successor. The automaton loops.

### 3.2 Encoding Quality

An automaton with k connections, each carrying s-valued signals, faces s^k possible input patterns. Its encoding — how it maps those s^k patterns to internal distinctions — determines D, the number it can actually tell apart.

**Flat encoding** (e.g., XOR hash): D = C, regardless of k. Adding connections does not help. The automaton gets more input but extracts no more information from it.

**Hierarchical encoding** (e.g., polynomial hash of depth k): D = min(C^k, D_max). Each additional connection multiplies the number of distinguishable patterns by C. The automaton extracts exponentially more information from its connections.

### 3.3 The Theorem

**Anti-Loop Theorem.** Let E be a finite deterministic automaton with C internal states and k connections each carrying s-valued signals. If E's encoding distinguishes D < s^k input patterns, then E must revisit an effective state within C × D + 1 steps. An automaton with the same memory and connections but encoding quality D' > D has a strictly longer minimum trajectory.

*Proof.* The effective state space has size C × D. The trajectory through effective states is deterministic. By the pigeonhole principle, a revisit occurs within C × D + 1 steps. A revisited effective state — same internal state, same perceived input — produces the same successor, initiating a loop. An automaton distinguishing D' > D patterns has a strictly larger effective state space and therefore a strictly longer minimum trajectory before forced revisit. ∎

### 3.4 The Quantitative Prediction

Under stochastic inputs, the birthday paradox applies to the effective state space. The expected time to first collision in a space of size N is √(πN/2). For an automaton with effective state space C × D:

- **Expected lifetime** = √(π · C · D / 2)
- **CV of lifetime** = √((4−π)/π) ≈ 0.523 (the Rayleigh invariant)

For flat encoding (D = C): lifetime ∝ C, independent of degree.

For hierarchical encoding (D = C^k): lifetime ∝ C^((k+1)/2). Taking the logarithm:

**log(lifetime) = ((k+1)/2) · log(C) + const**

This is linear in k with slope log(C)/2. The slope depends only on memory size — zero free parameters.

### 3.5 Why This Matters for Networks

Under M1, an automaton that loops must spawn. A longer lifetime means a longer interval between spawns. Therefore:

- Flat-encoding automata reproduce at a constant rate regardless of connectivity.
- Hierarchical-encoding automata reproduce exponentially slower as they gain connections.

This is anti-preferential attachment. Well-connected nodes are *penalized*, not rewarded. The deceleration is not imposed — it is a direct consequence of the anti-loop theorem applied to automata that reproduce under loop pressure.

### 3.6 Selection for Hierarchical Encoding

The anti-loop theorem provides the fitness landscape: higher D → longer trajectory → more time before forced reproduction. M1 provides the variation: each child is a new automaton with its own transition function, occupying a different network position and receiving different inputs. Different positions produce different effective encodings.

Flat encoders exhaust their effective states quickly and spawn while still shallow. Hierarchical encoders last exponentially longer. Over time, the population is dominated by hierarchical encoders — not by choice, but because those are the ones that persist.

This is a selection effect, not an optimization. No entity "decides" to encode hierarchically. The anti-loop theorem simply ensures that flat encoders are replaced faster.

---

## 4. The Pigeonhole Cascade

The anti-loop theorem is the engine. Here is the machine it drives.

**Step 1: Must spawn.** A solitary automaton with C states under A2 exhausts its trajectory in C steps. With A3 blocking internal growth and nothing else existing, M1 is the only option. It spawns.

**Step 2: Connections create exponential input.** Spawning creates a connection (Section 2). With k connections carrying s-valued signals: s^k input patterns. Exponential in k.

**Step 3: Flat encoding fails.** By the anti-loop theorem, a flat encoder (D = C) has effective state space C². With s^k patterns arriving and only C² effective states, it loops in O(C) steps regardless of connections. It has gained nothing from its connectivity.

**Step 4: Hierarchical encoding survives.** A hierarchical encoder (D = C^k) has effective state space C^(k+1). It survives exponentially longer. Selection (Section 3.6) favors it.

**Step 5: Hierarchical encoding saturates.** Under A3, encoding depth has a maximum d_max set by the memory bound. As connections keep growing (each spawn adds one), eventually s^k exceeds C^(d_max). The encoding is overwhelmed.

**Step 6: Must spawn again.** Same logic as Step 1. The cycle repeats at the next level.

Three pigeonhole arguments — (1) finite states force spawning, (2) exponential input defeats flat encoding, (3) bounded encoding depth is eventually overwhelmed — cycling at every scale. This produces hierarchy, reproduction, and structure. None assumed.

---

## 5. Simulation

### 5.1 Isolated Entity: Lifetime Distribution

C = 16, 32, 64, 128. Single automaton with 1, 2, and 5 neighbors supplying random inputs. 10,000 trials per condition.

| Prediction | Measured |
|---|---|
| CV = 0.523 | 0.524 ± 0.014 |
| Mean = 1.253C | Confirmed (all KS tests pass, p > 0.06) |
| Independent of neighbor count | Confirmed across k = 1, 2, 5 |

The lifetime distribution is Rayleigh. Poisson-timed models give CV = 1.0. Deterministic timers give CV = 0. The anti-loop model gives 0.523 — with no free parameters.

### 5.2 Isolated Entity: Blindness Theorem

C = 64. Single automaton with k = 1, 2, 3 neighbors. Flat (XOR hash, D = C) vs hierarchical (polynomial hash, D = min(C^k, D_max)).

| k | Flat lifetime | Hierarchical lifetime | Ratio |
|---|---|---|---|
| 1 | ~80 | ~80 | 1x |
| 2 | ~80 | ~643 | 8x |
| 3 | ~80 | ~2641 | 34x |

Log(lifetime) vs degree: measured slope = 1.75, predicted log(C)/2 = 2.08 (84% match), R² = 0.99.

Flat encoding: lifetime constant across all degrees. The connections are wasted.

### 5.3 Growing Network

Spawn model with 300 nodes, C = 256, 3 seeds. Flat vs hierarchical encoding.

| Metric | Flat | Hierarchical |
|---|---|---|
| Degree exponent α | 2.88 | **1.97** |
| Growth speed | baseline | 1.8x slower |
| Interval deg=1 → deg=2 | 1.0x | **2.9x** |
| Inter-spawn slope vs degree | −0.01 | **+0.27** |

Under flat encoding, inter-spawn intervals are constant across degrees — exactly as the anti-loop theorem predicts (D = C, no degree dependence). Under hierarchical encoding, intervals increase sharply with degree — anti-preferential attachment.

The hierarchical α ≈ 1.97 is closer to empirical networks than flat (α ≈ 2.88), standard preferential attachment (α ≈ 3.0), or the Dorogovtsev-Mendes model at its default aging parameter.

### 5.4 Additional Results

**Heavy-tailed topology at scale.** Tree-depth spawn model at 44k nodes (30 seeds): α ≈ 2.05 ± 0.02. Better fit by lognormal than strict power-law at large scale, consistent with Broido & Clauset (2019). Random tree control: α ≈ 2.85.

**MI excess on edges.** LPAN model (lateral wiring under loop pressure): edges carry ~15% more mutual information than non-edges (ρ ≈ 1.15, 92σ). Absent under parameter-free attention wiring (ρ ≈ 0.98) — MI excess requires proactive wiring, not just anti-loop dynamics. An honest negative result.

**Three growth phases.** Expansion → transition → plateau, confirmed 10/10 seeds. Phase 2 width scales as √C with memory size, becoming an extended era at large C.

---

## 6. Related Work

**Dorogovtsev & Mendes (2000).** Multiply preferential attachment by aging factor τ^(-α). Degree exponent γ increases from 2 to ∞ as aging parameter goes from 0 to 1. The mechanism is a free parameter — aging is imposed, not derived from node properties. The anti-loop theorem derives the same deceleration from encoding quality.

**Amaral, Scala, Barthélémy & Stanley (2000).** Add connection costs or capacity constraints to produce truncated power laws. Again, the constraint is external. The anti-loop theorem makes connectivity costly endogenously: more connections → larger effective state space to explore → longer time to loop.

**Barabási & Albert (1999).** Preferential attachment produces α = 3. The mechanism assumes connectivity is a benefit (more links attract more links). The anti-loop theorem shows that under bounded memory with no-repeat constraints, connectivity is a cost. The two mechanisms predict opposite dynamics.

**Kim & Montenegro (2008).** Birthday paradox for Markov chains: collision in Θ(√|S|) steps. They apply this to Pollard's Rho algorithm for discrete logarithm. We apply the same mathematics to effective state spaces of finite automata, yielding the Rayleigh lifetime prediction (CV = 0.523) and the degree-dependent interval scaling.

**Kauffman (2000).** Autonomous agents as self-reproducing systems that perform work cycles. Philosophical overlap — reproduction emerges from constraints — but no finite-state formalism, no encoding quality argument, no topology predictions.

---

## 7. The Derivation Chain

| # | Claim | Status |
|---|-------|--------|
| 1 | Finite + deterministic → must loop | Classical (pigeonhole) |
| 2 | A loop produces no new states | Classical (determinism) |
| 3 | Solitary automaton under A2 + A3 → must spawn (M1) | Derived by elimination |
| 4 | Spawning creates connections | Derived from A1 (environment in transition function) |
| 5 | k connections → s^k input patterns | Combinatorics |
| 6 | Flat encoding fails under exponential input | Anti-loop theorem (proved) |
| 7 | Encoding quality D determines effective state space C×D | Anti-loop theorem (proved) |
| 8 | Hierarchical encoding is a selection effect | Derived from 6–7 + variation from M1 |
| 9 | Finite encoding + growing connections → overwhelmed | Pigeonhole 3 |
| 10 | Cycle repeats → hierarchy | Structural recursion |
| 11 | Entity lifetime ~ Rayleigh(C), CV = 0.523 | Derived (birthday paradox on C×D); confirmed |
| 12 | log(lifetime) linear in degree, slope = log(C)/2 | Derived (anti-loop theorem + birthday paradox); confirmed (R²=0.99) |
| 13 | Network-level: hierarchical → α ≈ 2.0 | Simulation (3 seeds; flat α≈2.88 vs hier α≈1.97) |
| 14 | Heavy-tailed topology at scale (α ≈ 2.05) | Simulation (30 seeds, 44k nodes) |

Steps 1–2 are classical. Steps 3–5 are derived. Steps 6–8 are the anti-loop theorem and its consequences (proved for worst case; general case open). Step 9 closes the cycle. Steps 11–14 are confirmed by simulation.

---

## 8. Open Problems

**O1 (General case).** The anti-loop theorem is proved for worst-case inputs. The general case — tight bounds as a function of input statistics — would make hierarchical encoding quantifiably inevitable, not just favored. This is the highest-priority open problem.

**O2 (Encoding uniqueness).** The theorem proves flat encoding fails. Does it uniquely favor binary comparison trees, or do other logarithmic-access encodings survive equally?

**O3 (Scale testing).** CSN analysis at 10⁴–10⁵ nodes. Full Broido-Clauset protocol. The current α ≈ 1.97 for hierarchical encoding is from 3 seeds at 300 nodes — preliminary.

**O4 (Tetration).** Tower-of-powers capacity growth at each hierarchy level. Derived but not formally proved.

**O5 (Lateral wiring).** Which lateral connections does an automaton activate, and when? The LPAN model uses loop pressure. Is this unique?

---

## 9. What This Paper Does Not Claim

**It does not claim the universe is made of automata.** The model produces universe-like structure. Whether reality satisfies A1–A3 is empirical.

**It does not claim spawning is the only mechanism.** It claims spawning suffices. Merging, pruning, or interference might produce similar or different structures.

**It does not claim to replace preferential attachment.** Preferential attachment describes a real phenomenon in some networks. The anti-loop theorem describes a different mechanism that produces a different exponent. Both may operate simultaneously.

**It does not prove the encoding must be a tree.** It proves flat encoding fails. Hierarchical encoding survives. The specific structure (binary trees, DAGs, bounded-width circuits) is open (O2).

---

## References

Amaral, L.A.N., Scala, A., Barthélémy, M. & Stanley, H.E. (2000). Classes of small-world networks. *Proceedings of the National Academy of Sciences*, 97(21), 11149–11152.

Barabási, A.-L. & Albert, R. (1999). Emergence of scaling in random networks. *Science*, 286(5439), 509–512.

Broido, A.D. & Clauset, A. (2019). Scale-free networks are rare. *Nature Communications*, 10, 1017.

Clauset, A., Shalizi, C.R. & Newman, M.E.J. (2009). Power-law distributions in empirical data. *SIAM Review*, 51(4), 661–703.

Dorogovtsev, S.N. & Mendes, J.F.F. (2000). Evolution of networks with aging of sites. *Physical Review E*, 62(2), 1842–1845.

Kauffman, S.A. (2000). *Investigations*. Oxford University Press.

Kim, J.H. & Montenegro, R. (2008). A birthday paradox for Markov chains, with an optimal bound for collision in the Pollard Rho algorithm for discrete logarithm. *Annals of Applied Probability*, 20(2), 495–521.

Krapivsky, P.L., Redner, S. & Leyvraz, F. (2000). Connectivity of growing random networks. *Physical Review Letters*, 85(21), 4629.
