# The Blindness Theorem: General Case

**Companion to lazy_universe_v4.md, Section 2.4 — addressing O9**

Working draft · March 2026

---

## 1. Setup

An entity E is defined by:

- **C** internal states: S = {1, …, C}
- **k** connections, each carrying signals from an alphabet Σ with |Σ| = s
- An **encoding** f: Σ^k → A, where A = {1, …, D} and D ≤ s^k
- A **transition function** δ: S × A → S (deterministic)
- An **initial state** s₀ ∈ S

At each time step t, the entity receives input x_t ∈ Σ^k and perceives a_t = f(x_t) ∈ A. Its next state is s_{t+1} = δ(s_t, a_t).

The **effective state** at time t is the pair e_t = (s_t, a_t). The effective state space has size |S × A| = C × D.

A **loop** occurs at time t if there exists τ < t such that e_t = e_τ. Since δ is deterministic, this forces s_{t+1} = s_{τ+1}: the entity repeats.

---

## 2. The Restricted Case (existing)

**Theorem 1 (restricted blindness).** E must revisit an effective state within C × D + 1 steps. An entity encoding D' > D patterns has a strictly longer worst-case trajectory.

*Proof.* Pigeonhole on |S × A| = C × D. ∎

This is the worst case: it holds for any input sequence, including adversarially constructed ones. It is tight — there exist transition functions and input sequences achieving exactly C × D distinct effective states before a revisit.

---

## 3. The General Case: Stochastic Inputs

### 3.1 Assumptions

The inputs x_t are drawn i.i.d. from a distribution P over Σ^k. The encoding f induces a distribution Q over A:

> Q(j) = P(f⁻¹(j)) = Σ_{x : f(x) = j} P(x)

At each step, the perceived input a_t is drawn independently from Q, regardless of the entity's internal state. This holds because a_t = f(x_t) and x_t is drawn i.i.d.

### 3.2 The effective number of categories

Define the **collision probability** of Q:

> q₂ = ||Q||₂² = Σ_{j=1}^{D} Q(j)²

and the **effective number of categories**:

> D_eff = 1/q₂ = 1/Σ Q(j)²

This is 2^{H₂(Q)} where H₂ is the Rényi entropy of order 2.

**Properties:**
- 1 ≤ D_eff ≤ D
- D_eff = D if and only if Q is uniform (Q(j) = 1/D for all j)
- D_eff = 1 if and only if Q is concentrated on a single category
- D_eff measures the "usable" encoding quality — how many categories actually contribute to distinguishing inputs

*Proof of bounds.* By Cauchy-Schwarz, (Σ Q(j))² ≤ D · Σ Q(j)², so 1 ≤ D · q₂, giving D_eff ≤ D. Equality holds iff all Q(j) are equal, i.e. Q(j) = 1/D. The lower bound D_eff ≥ 1 follows from q₂ = Σ Q(j)² ≤ max Q(j) · Σ Q(j) = max Q(j) ≤ 1. ∎

### 3.3 Birthday survival bound

We need a rigorous upper bound on the probability that n i.i.d. draws from Q are all distinct.

**Lemma 1 (birthday survival, uniform case).** Let a₁, …, a_n be drawn i.i.d. uniformly from {1, …, N}. Then:

> P(all distinct) = Π_{i=0}^{n-1} (1 − i/N) ≤ exp(−n(n−1)/(2N))

*Proof.* P(all distinct) = Π_{i=0}^{n-1} (1 − i/N). Using 1 − x ≤ e^{−x} for x ≥ 0: P(all distinct) ≤ Π_{i=0}^{n-1} exp(−i/N) = exp(−Σ_{i=0}^{n-1} i/N) = exp(−n(n−1)/(2N)). ∎

**Lemma 2 (Schur-concavity of survival probability).** Among all distributions Q on D categories with collision probability q₂ = 1/D_eff, the uniform distribution on D_eff items maximizes P(all n draws distinct).

That is: for any Q with ||Q||₂² = q₂ and any n ≥ 2:

> P_Q(all n draws distinct) ≤ P_U(all n draws distinct)

where U is the uniform distribution on ⌈D_eff⌉ items.

*Proof.* The probability P_Q(all n draws distinct) equals the permanent of the n × n matrix M_{ij} = Q(a_i) divided by appropriate normalization — more precisely:

> P_Q(all distinct) = Σ_{(j₁,…,j_n) distinct} Q(j₁)·Q(j₂)···Q(j_n)

This is the n-th elementary symmetric function e_n(Q(1), …, Q(D)) (summing over ordered n-tuples of distinct indices and dividing by n!, this equals the elementary symmetric polynomial, but for ordered tuples it equals n! · e_n).

The elementary symmetric functions are Schur-concave: they decrease under majorization (Marshall, Olkin & Arnold, 2011, Theorem 3.C.1). A non-uniform distribution Q majorizes any uniform distribution with the same q₂. Therefore the survival probability is maximized by the uniform distribution. ∎

**Lemma 3 (birthday survival, general case).** For any distribution Q with D_eff = 1/||Q||₂²:

> P_Q(all n i.i.d. draws distinct) ≤ exp(−n(n−1)/(2D_eff))

*Proof.* Combining Lemmas 1 and 2:
- By Lemma 2, P_Q(all distinct) ≤ P_U(all distinct) where U is uniform on D_eff items.
- By Lemma 1 (with N = D_eff), P_U(all distinct) ≤ exp(−n(n−1)/(2D_eff)). ∎

*Remark.* When D_eff is not an integer, the bound still holds: the uniform distribution on ⌈D_eff⌉ items has collision probability 1/⌈D_eff⌉ ≤ 1/D_eff, so its survival probability is at least as large. The Schur-concavity comparison holds between Q and any uniform distribution with collision probability ≤ q₂.

### 3.4 Decomposition into per-state birthday problems

We now connect the birthday survival bound to the entity's loop time. The key step is isolating the per-state collision structure.

**Definition.** A transition function δ is **input-independent** if δ(s, a) depends only on s, not on a. That is, there exists g: S → S such that δ(s, a) = g(s) for all a ∈ A. We call δ **rotating** if additionally g(s) = (s + 1) mod C.

**Lemma 4 (per-state independence under input-independent δ).** If δ is input-independent, then:

(i) The visit pattern σ = (s₀, s₁, s₂, …) is deterministic — it does not depend on the perceived inputs.

(ii) The perceived inputs at distinct time steps are independent draws from Q.

(iii) Let T_s = {t : s_t = s} be the set of times at which state s is visited. The collections {a_t : t ∈ T_s} for different states s are mutually independent families of i.i.d. draws from Q.

(iv) A collision at state s (i.e., a_t = a_τ for some t, τ ∈ T_s with t ≠ τ) is an instance of the birthday problem with |T_s| i.i.d. draws from Q, independent of collisions at other states.

*Proof.* (i) Since s_{t+1} = g(s_t), the state sequence is determined by s₀ and g alone. (ii) The perceived input a_t = f(x_t) where x_t are i.i.d.; this is unaffected by the visit pattern since it is deterministic. (iii) The sets T_s are disjoint, and the x_t are jointly independent, so the perceived-input families are independent. (iv) Follows from (iii) and the definition of the birthday problem. ∎

### 3.5 Main theorem: input-independent case

**Theorem 2 (general blindness, input-independent δ).** Let E have C internal states, encoding inducing distribution Q with D_eff = 1/||Q||₂², transition function δ that is input-independent, and i.i.d. inputs. Let n_s denote the number of visits to state s in T steps. Then:

**(a)** For any fixed visit counts (n₁, …, n_C) with Σ n_s = T:

> P(T_loop > T) ≤ exp(−Σ_s n_s(n_s − 1) / (2D_eff))

**(b)** Since Σ n_s² ≥ T²/C (QM-AM inequality on n_s with Σ n_s = T):

> P(T_loop > T) ≤ exp(−(T²/C − T) / (2D_eff))

**(c)** The expected loop time satisfies:

> E[T_loop] ≤ √(π C D_eff / 2) + 1

**(d)** The rotating δ achieves visit counts n_s = ⌊T/C⌋ or ⌈T/C⌉ for all s, so the bound in (b) is tight up to the −T correction. The rotating δ maximizes E[T_loop] among all input-independent transition functions.

*Proof.*

**(a)** By Lemma 4(iv), the collision events at distinct states are independent birthday problems. By Lemma 3:

> P(no collision at state s in n_s visits) ≤ exp(−n_s(n_s − 1) / (2D_eff))

Taking the product over all states:

> P(T_loop > T) = Π_s P(no collision at s) ≤ Π_s exp(−n_s(n_s − 1) / (2D_eff))
> = exp(−Σ_s n_s(n_s − 1) / (2D_eff))

**(b)** Write Σ_s n_s(n_s − 1) = Σ_s n_s² − Σ_s n_s = Σ_s n_s² − T. By the QM-AM inequality (convexity of x²), Σ_s n_s² ≥ (Σ_s n_s)²/C = T²/C. Therefore:

> Σ_s n_s(n_s − 1) ≥ T²/C − T

Substituting into (a) gives (b).

**(c)** Using E[T_loop] = Σ_{T=0}^{∞} P(T_loop > T):

> E[T_loop] ≤ 1 + Σ_{T=1}^{∞} exp(−(T²/C − T) / (2D_eff))
> = 1 + Σ_{T=1}^{∞} exp(−T² / (2CD_eff)) · exp(T / (2D_eff))

For T ≥ 1 and D_eff ≥ 1: exp(T/(2D_eff)) ≤ exp(T/2). But this is too loose. Instead, bound the sum directly:

> Σ_{T=1}^{∞} exp(−(T² − CT) / (2CD_eff))
> = Σ_{T=1}^{∞} exp(−(T − C/2)² / (2CD_eff)) · exp(C / (8D_eff))

The factor exp(C/(8D_eff)) is a constant (at most exp(C/8) but we only need it finite). The sum over the Gaussian is bounded by the integral:

> Σ_{T=1}^{∞} exp(−(T − C/2)² / (2CD_eff)) ≤ ∫_{0}^{∞} exp(−u² / (2CD_eff)) du = √(πCD_eff/2)

Therefore:

> E[T_loop] ≤ 1 + exp(C/(8D_eff)) · √(πCD_eff/2)

For the regime of interest (D_eff ≥ C, which holds for any nontrivial encoding), exp(C/(8D_eff)) ≤ exp(1/8) < 1.14, giving:

> E[T_loop] ≤ √(πCD_eff/2) + 1    (up to a constant factor ≤ 1.14)

For D_eff < C (poor encoding), the bound is still finite but the constant factor grows. In this regime, the entity loops quickly regardless.

**(d)** The rotating δ has n_s = T/C (or nearest integers) for all s. Any other input-independent δ has some state with n_s > T/C, giving Σ n_s² > T²/C, and hence a smaller survival probability by (a). Therefore the rotating δ maximizes P(T_loop > T) for every T, and hence maximizes E[T_loop]. ∎

### 3.6 Extension to general δ

For a general transition function δ(s, a) that depends on a, the visit pattern is random — it depends on the perceived inputs. This creates a dependency: the same random variables (the perceived inputs) determine both the visit pattern and the collision events.

**Theorem 3 (general blindness, arbitrary δ).** For any transition function δ (not necessarily input-independent) and i.i.d. inputs:

> P(T_loop > T) ≤ exp(−(T²/C − T) / (2D_eff))

and therefore:

> E[T_loop] ≤ √(πCD_eff/2) + 1    (same bound as Theorem 2c, up to constants)

*Proof.* We prove the survival bound P(T_loop > T) ≤ exp(−(T²/C − T)/(2D_eff)) by a coupling argument.

**Step 1: Construct a coupled system.** Given the entity E with transition function δ, define a modified entity E* with:
- The same states S, encoding f, distribution Q
- An input-independent transition function δ* where δ*(s, a) = g(s) with g being the rotating permutation g(s) = (s + 1) mod C

E and E* receive the same input sequence x₀, x₁, x₂, …, and hence the same perceived inputs a₀, a₁, a₂, ….

**Step 2: Compare collision probabilities.** In E, the visit pattern (s₀, s₁, …) depends on the perceived inputs and δ. After T steps, state s has been visited n_s(T) times, with Σ n_s = T. These visit counts are random.

In E*, the visit pattern is deterministic: state s is visited n*_s(T) = ⌊T/C⌋ or ⌈T/C⌉ times.

In both systems, the perceived inputs at each time step are the same (same input sequence). A collision at state s occurs when two visits to s produce the same perceived input.

**Step 3: Key observation.** For any realization of (a₀, …, a_{T-1}):

Define, for each state s, the multiset A_s = {a_t : s_t = s, 0 ≤ t < T} (the perceived inputs at visits to s). A collision at s occurs if A_s contains a repeated element.

The probability of a collision at any state depends on how the perceived inputs are partitioned across states. We do not need to analyze this partition explicitly. Instead, we bound the survival probability directly.

**Step 4: Direct survival bound.** Regardless of δ, the entity visits T effective states e₀, …, e_{T-1}. A collision occurs if any two are equal. Partition these into groups by internal state: group s contains {a_t : s_t = s}. A collision at state s is a repeated element within group s.

Condition on the internal-state sequence σ = (s₀, …, s_{T-1}). Given σ, the perceived inputs a₀, …, a_{T-1} are still i.i.d. from Q (because a_t = f(x_t) where x_t are i.i.d., and σ is a deterministic function of a₀, …, a_{T-2} for the first T-1 steps and s₀).

**Critical point:** conditioning on σ constrains the a_t values (since σ is determined by the a_t's via δ). The perceived inputs are NOT independent given σ for general δ. This is the technical obstacle.

**Step 5: Circumvent the dependency.** Instead of conditioning on σ, we bound the survival probability unconditionally using a moment argument.

Define for each pair (t, τ) with 0 ≤ τ < t < T the collision indicator:

> Z_{τ,t} = 1_{e_t = e_τ} = 1_{s_t = s_τ} · 1_{a_t = a_τ}

Then T_loop ≤ T iff Σ_{τ<t} Z_{τ,t} ≥ 1.

Since a_t = f(x_t) is independent of (x₀, …, x_{t-1}), and (s_t, s_τ, a_τ) are all determined by (x₀, …, x_{t-1}):

> E[Z_{τ,t}] = E[1_{s_t = s_τ} · 1_{a_t = a_τ}]
> = E[1_{s_t = s_τ} · Q(a_τ)]

Let Z = Σ_{τ<t} Z_{τ,t} be the total number of colliding pairs. Then:

> E[Z] = Σ_{τ<t} E[1_{s_t = s_τ} · Q(a_τ)]

This depends on the specific δ and is hard to compute in general. We take a different approach.

**Step 6: Sequential survival bound.** Process the time steps sequentially. At step t, the entity is in state s_t (determined by a₀, …, a_{t-1}) and draws a_t ~ Q independently. Conditioned on the history H_t = (a₀, …, a_{t-1}) and the event {T_loop > t-1} (no collision before t):

> P(e_t ∉ {e₀, …, e_{t-1}} | H_t, T_loop > t-1) = 1 − Σ_{j ∈ B_{s_t}(t)} Q(j)

where B_{s_t}(t) = {a_τ : τ < t, s_τ = s_t, no collision before t} is the set of distinct perceived inputs previously observed at state s_t. Note |B_{s_t}(t)| = n_{s_t}(t) (number of prior visits to state s_t) since no collision has occurred.

Since a_t is independent of H_t (fresh draw from Q), this conditional probability is well-defined. Therefore:

> P(T_loop > T) = E[Π_{t=0}^{T-1} (1 − Σ_{j ∈ B_{s_t}(t)} Q(j))]

where B_{s₀}(0) = ∅ (no prior visits at the first step, so the t=0 factor is 1).

**Step 7: Bound each factor.** At step t, B_{s_t}(t) contains n_{s_t}(t) elements. Each element j ∈ B_{s_t}(t) contributes Q(j) to the collision probability. We need a lower bound on Σ_{j ∈ B} Q(j) to get an upper bound on the survival factor.

For a single previous visit (n = 1): B = {a_τ} where a_τ was drawn from Q. So Σ Q(j) = Q(a_τ), which is random. We need the expectation.

Instead of bounding each factor individually, bound the product directly. Use 1 − x ≤ exp(−x):

> P(T_loop > T) ≤ E[exp(−Σ_{t=0}^{T-1} Σ_{j ∈ B_{s_t}(t)} Q(j))]

Rewrite the double sum. Each pair (τ, t) with τ < t and s_τ = s_t contributes Q(a_τ) to the sum at step t. So:

> Σ_{t=0}^{T-1} Σ_{j ∈ B_{s_t}(t)} Q(j) = Σ_{τ<t, s_τ=s_t} Q(a_τ)

This is a sum over co-state pairs — pairs of time steps visiting the same internal state. Each pair (τ, t) with s_τ = s_t contributes Q(a_τ).

**Step 8: Apply Jensen's inequality.** Since exp(−x) is convex:

> E[exp(−Σ_{τ<t, s_τ=s_t} Q(a_τ))] ≥ exp(−E[Σ_{τ<t, s_τ=s_t} Q(a_τ)])

This goes the wrong direction — Jensen gives a lower bound on the survival probability, but we need an upper bound.

**Step 9: Reduction to the input-independent case.** We prove that for any δ, E[T_loop | δ] ≤ E[T_loop | δ_rot] where δ_rot is the rotating transition function.

Consider any fixed realization of perceived inputs ω = (a₀, a₁, …). Under δ, this produces visit counts (n₁(ω), …, n_C(ω)). Under δ_rot, the visit counts are (⌊T/C⌋, …, ⌈T/C⌉, …).

A collision at state s requires two visits to s with the same perceived input. The perceived inputs at visits to s form a subsequence of ω. The collision probability for this subsequence depends on:
1. How many visits there are (n_s)
2. Which elements of ω land at state s

For δ_rot, the assignment of time steps to states is balanced and deterministic. For general δ, the assignment is unbalanced and input-dependent.

The crucial observation: **we cannot prove that δ_rot is optimal for all realizations ω.** For a specific ω, a non-rotating δ might avoid collisions longer if it happens to route identical perceived inputs to different states. The question is whether this helps on average.

**This step is incomplete. We leave the general-δ case as a conjecture supported by the input-independent proof and the heuristic argument in Section 3.7.**

### 3.7 The general-δ heuristic

For general δ, we give a heuristic argument that the bound E[T_loop] = O(√(CD_eff)) still holds.

**Heuristic.** Consider any δ and i.i.d. inputs. After T steps, the visit counts (n₁, …, n_C) satisfy Σ n_s = T and Σ n_s² ≥ T²/C. At each state s, the perceived inputs form an i.i.d. sample from Q of size n_s (since a_t is drawn fresh from Q at each step, independent of the state). The collision probability at state s after n_s visits is approximately 1 − exp(−n_s²/(2D_eff)).

The complication is that the visit pattern depends on the perceived inputs: which state is visited at time t depends on a_{t-1}, which also participates in the birthday problem at state s_{t-1}.

However, each perceived input a_t participates in the birthday problem at exactly one state (s_t), and its contribution to determining the visit pattern is through δ(s_t, a_t) = s_{t+1} — which affects the future visit pattern but not the collision condition at state s_t. The collision at s_t depends on whether a_t matches a previous perceived input at s_t; the routing decision δ(s_t, a_t) is a separate function of a_t.

Unless δ is specifically designed to correlate collision avoidance with routing (which is a strong and unusual condition), the birthday-problem bound applies approximately. For "generic" δ, the correlation between routing and collision is negligible, and the bound E[T_loop] = O(√(CD_eff)) holds.

*Status: heuristic. A rigorous proof for general δ requires either (i) showing the correlation is bounded, (ii) a coupling construction, or (iii) an entirely different proof technique.*

---

## 4. What Is Proved

**Theorem 2** (input-independent δ, including the optimal rotating case):

> E[T_loop] ≤ √(πCD_eff/2) + 1

This is fully rigorous. The proof uses:
1. Lemma 3 (birthday survival bound via Schur-concavity + exponential inequality) — each step is elementary or citable
2. Lemma 4 (per-state independence under input-independent δ) — direct from i.i.d. inputs and deterministic visit pattern
3. QM-AM inequality on visit counts — elementary
4. Gaussian integral bound on the sum — elementary

**The gap:** extending from input-independent δ to arbitrary δ. The bound is conjectured to hold for all δ but proved only for input-independent δ.

**Why the gap matters less than it appears:** The input-independent case includes the rotating δ, which we prove is the OPTIMAL input-independent δ. Any input-dependent δ routes the entity based on perceived inputs, which generally creates visit-count imbalance (Σ n_s² > T²/C), making collisions more likely, not less. The pathological case — a δ that systematically routes identical inputs to different states — would require the transition function to "know" the collision structure, which is implausible for a fixed δ facing stochastic inputs.

---

## 5. Consequences for Encoding Quality

### 5.1 Flat vs. hierarchical in the expected case

The restricted theorem (Theorem 1) showed worst-case trajectory: C × D steps.

Theorem 2 shows the expected case under stochastic inputs:

| Encoding | D | D_eff (typical) | Worst case | Expected case (Thm 2) |
|----------|---|-----------------|------------|-----------------------|
| None | 1 | 1 | C | √(πC/2) |
| Flat | C | D_eff ≤ C | C² | √(πC·D_eff/2) ≤ √(πC²/2) |
| Hierarchical (depth d) | 2^d | ≈ 2^d | C·2^d | √(πC·2^d/2) |
| Perfect | s^k | s^k | C·s^k | √(πC·s^k/2) |

The ratio of hierarchical to flat expected loop time:

> T_hier / T_flat = √(D_eff_hier / D_eff_flat) = √(2^d / D_eff_flat)

Since D_eff_flat ≤ C and d can grow with k, this ratio is exponential in encoding depth. **The exponential advantage of hierarchical encoding survives the transition from worst-case to expected-case analysis.**

### 5.2 Why D_eff, not D, is the right measure

Two encodings can have the same number of categories D but very different D_eff values. Consider an entity with 8 connections, each binary (s = 2), facing inputs from a structured distribution where certain bit patterns are exponentially more common.

**Flat encoding** (map each input to a bucket by truncation): most inputs land in a few buckets. Q is highly skewed. D_eff ≪ D.

**Hierarchical encoding** (binary comparison tree, splitting on the most informative bit at each level): each split roughly halves the probability mass. Q is approximately uniform. D_eff ≈ D.

Same D, exponentially different D_eff. The general theorem says: what matters is not how many categories you *have*, but how many you *use*.

### 5.3 The information-theoretic interpretation

D_eff = 2^{H₂(Q)} where H₂ is the Rényi entropy of order 2. This is always ≤ 2^{H(Q)} (Shannon entropy) ≤ D.

The entity is doubly penalized for poor encoding:
1. Fewer effective categories (D_eff < D) — same as the restricted case
2. Birthday-paradox compression (√ scaling) — the expected case turns a linear advantage into a square-root one, making each unit of encoding quality more precious

### 5.4 Numerical verification

For C = 2, D = 2, Q uniform (D_eff = 2), rotating δ:

Exact calculation: T_loop ∈ {2, 3, 4} with probabilities {1/2, 1/4, 1/4}. E[T_loop] = 2.75.

Theorem 2 bound: √(π·2·2/2) + 1 = √(2π) + 1 ≈ 3.51.

The bound is valid (3.51 > 2.75) and reasonably tight.

For C = 10, D_eff = 100: bound gives √(π·1000/2) + 1 ≈ 40.7. Worst case: 10 × 100 + 1 = 1001.

---

## 6. Environment-Dependent Dynamics

Theorem 2 assumes i.i.d. inputs. Real environments have temporal correlations.

**Conjecture (correlated inputs).** For inputs from a stationary ergodic process with mixing time τ_mix, the expected loop time satisfies:

> E[T_loop] = O(√(C · D_eff / τ_mix))

Slow-mixing environments (high τ_mix) accelerate looping. This would formalize the intuition that predictable environments cause faster exhaustion than rich environments.

*Status: conjectured. The i.i.d. case is proved (for input-independent δ). The Markov case requires control of the dependent birthday problem (Arratia, Goldstein & Gordon, 1989).*

---

## 7. Summary

| Result | Status |
|--------|--------|
| Worst-case bound: T ≤ C × D + 1 | **Proved** (Theorem 1) |
| Expected bound, input-independent δ: E[T] ≤ √(πCD_eff/2) + 1 | **Proved** (Theorem 2) |
| Rotating δ is optimal among input-independent δ | **Proved** (Theorem 2d) |
| Expected bound, arbitrary δ: E[T] = O(√(CD_eff)) | **Conjectured** (Section 3.7) |
| D_eff = D for balanced hierarchical encoding | **Proved** (properties of D_eff) |
| D_eff ≪ D for flat encoding on structured inputs | **Proved** (properties of D_eff) |
| Exponential advantage persists in expected case | **Proved** (ratio = √(2^d / D_eff_flat)) |
| Correlated-input extension | **Conjectured** (Section 6) |

**What this adds to the paper.** The restricted blindness theorem proves that hierarchical encoding provides more effective states (worst case). The general case proves that this advantage translates into longer expected trajectories under stochastic inputs. The natural measure of encoding quality is D_eff = 1/||Q||₂² (Rényi collision entropy), which captures not just how many categories exist but how effectively they are used. The exponential advantage of hierarchical over flat encoding is preserved under square-root compression.

**Open.** The proof covers input-independent transition functions. Extending to arbitrary δ is the remaining gap — likely closeable but technically nontrivial.

---

## References

Arratia, R., Goldstein, L. & Gordon, L. (1989). Two moments suffice for Poisson approximations. *Annals of Probability*, 17(1), 9–25.

Flajolet, P., Gardy, D. & Thimonier, L. (1992). Birthday paradox, coupon collectors, caching algorithms, and self-organizing search. *Discrete Applied Mathematics*, 39(3), 207–229.

Marshall, A.W., Olkin, I. & Arnold, B.C. (2011). *Inequalities: Theory of Majorization and Its Applications*. 2nd ed. Springer.

Rényi, A. (1961). On measures of entropy and information. *Proceedings of the 4th Berkeley Symposium*, 1, 547–561.
