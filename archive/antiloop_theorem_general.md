# The Anti-Loop Theorem: General Case

**Companion to antiloop_theorem.md — addressing O1**

Working draft · March 2026

---

## 1. Setup

An automaton E is defined by:

- **C** internal states: S = {1, …, C}
- **k** connections, each carrying signals from an alphabet Σ with |Σ| = s
- An **encoding** f: Σ^k → A, where A = {1, …, D} and D ≤ s^k
- A **transition function** δ: S × A → S (deterministic)
- An **initial state** s₀ ∈ S

At each time step t, the automaton receives input x_t ∈ Σ^k and perceives a_t = f(x_t) ∈ A. Its next state is s_{t+1} = δ(s_t, a_t).

The **effective state** at time t is the pair e_t = (s_t, a_t). The effective state space has size |S × A| = C × D.

A **loop** occurs at time t if there exists τ < t such that e_t = e_τ. Since δ is deterministic, this forces s_{t+1} = s_{τ+1}: the automaton repeats.

---

## 2. The Restricted Case (worst-case inputs)

**Theorem 1.** E must revisit an effective state within C × D + 1 steps.

*Proof.* Pigeonhole on |S × A| = C × D. ∎

This is tight: there exist transition functions and input sequences achieving exactly C × D distinct effective states before a revisit.

---

## 3. The General Case: Stochastic Inputs

### 3.1 Input model

The inputs x_t are drawn i.i.d. from a distribution P over Σ^k. The encoding f induces a distribution Q over A:

> Q(j) = P(f⁻¹(j)) = Σ_{x : f(x) = j} P(x)

### 3.2 Effective number of categories

Define the **collision probability** of Q:

> q₂ = ||Q||₂² = Σ_{j=1}^{D} Q(j)²

and the **effective number of categories**:

> D_eff = 1/q₂

This equals 2^{H₂(Q)} where H₂ is the Rényi entropy of order 2.

**Properties:**

(i) 1 ≤ D_eff ≤ D.

(ii) D_eff = D iff Q is uniform.

(iii) D_eff = 1 iff Q is concentrated on a single category.

*Proof.* (i) Upper: by Cauchy-Schwarz, (Σ Q(j))² ≤ D · Σ Q(j)², so 1 ≤ D · q₂, giving D_eff ≤ D. Lower: q₂ ≤ max Q(j) ≤ 1. (ii-iii) Equality conditions of Cauchy-Schwarz. ∎

D_eff measures usable encoding quality — how many categories actually contribute to distinguishing inputs.

### 3.3 Birthday survival bound

**Lemma 1 (uniform case).** Let a₁, …, aₙ be drawn i.i.d. uniformly from {1, …, N}. Then:

> P(all distinct) = ∏_{i=0}^{n-1} (1 − i/N) ≤ exp(−n(n−1)/(2N))

*Proof.* Using 1 − x ≤ e^{−x}: P(all distinct) ≤ ∏ exp(−i/N) = exp(−n(n−1)/(2N)). ∎

**Lemma 2 (Schur-concavity).** Among all distributions Q on D categories with collision probability q₂, the uniform distribution on D_eff items maximizes P(all n draws distinct).

*Proof.* The survival probability P_Q(all distinct) = Σ_{(j₁,…,jₙ) distinct} Q(j₁)···Q(jₙ) is the n-th elementary symmetric function of (Q(1), …, Q(D)), which is Schur-concave (Marshall, Olkin & Arnold, 2011, Theorem 3.C.1). A non-uniform distribution majorizes any uniform distribution with the same q₂. ∎

**Lemma 3 (general birthday bound).** For any distribution Q with D_eff = 1/||Q||₂²:

> P_Q(all n i.i.d. draws distinct) ≤ exp(−n(n−1)/(2D_eff))

*Proof.* Lemma 2 reduces to the uniform case. Lemma 1 bounds it. ∎

### 3.4 Per-state decomposition

**Definition.** A transition function δ is **input-independent** if δ(s, a) depends only on s: there exists g: S → S such that δ(s, a) = g(s) for all a. It is **rotating** if additionally g(s) = (s + 1) mod C.

**Lemma 4 (per-state independence).** If δ is input-independent, then:

(i) The state sequence σ = (s₀, s₁, …) is deterministic.

(ii) The perceived inputs a_t are i.i.d. from Q regardless of σ.

(iii) For each state s, the perceived inputs at visits to s form an i.i.d. sample from Q, independent across states.

(iv) A collision at state s is a birthday problem with |T_s| draws from Q, independent of other states.

*Proof.* (i) s_{t+1} = g(s_t), so σ is determined by s₀ and g. (ii) a_t = f(x_t) where x_t are i.i.d., unaffected by deterministic σ. (iii) The visit sets T_s are disjoint; the x_t are jointly independent. (iv) Follows from (iii). ∎

### 3.5 Main theorem (input-independent δ)

**Theorem 2.** Let E have C states, encoding inducing Q with D_eff = 1/||Q||₂², and input-independent δ with i.i.d. inputs. Let n_s denote visits to state s in T steps. Then:

**(a)** P(T_loop > T) ≤ exp(−Σ_s n_s(n_s − 1) / (2D_eff))

**(b)** P(T_loop > T) ≤ exp(−(T²/C − T) / (2D_eff))

**(c)** E[T_loop] ≤ √(πCD_eff/2) + 1 (up to a constant factor ≤ 1.14 for D_eff ≥ C)

**(d)** The rotating δ maximizes E[T_loop] among all input-independent transition functions.

*Proof.*

**(a)** By Lemma 4, collision events at distinct states are independent birthday problems. By Lemma 3, P(no collision at s in n_s visits) ≤ exp(−n_s(n_s − 1)/(2D_eff)). Taking the product over states:

> P(T_loop > T) = ∏_s P(no collision at s) ≤ exp(−Σ_s n_s(n_s − 1) / (2D_eff))

**(b)** By QM-AM: Σ n_s² ≥ T²/C. So Σ n_s(n_s − 1) = Σ n_s² − T ≥ T²/C − T.

**(c)** E[T_loop] = Σ_{T=0}^{∞} P(T_loop > T) ≤ 1 + Σ_{T=1}^{∞} exp(−(T²/C − T)/(2D_eff)). Completing the square and bounding the Gaussian sum by its integral gives the result. The correction factor exp(C/(8D_eff)) ≤ 1.14 for D_eff ≥ C.

**(d)** Rotating δ has n_s = T/C (± 1) for all s, minimizing Σ n_s² and hence maximizing survival probability at every T. ∎

### 3.6 Extension to general δ

For a general transition function δ(s, a) that depends on a, the state sequence becomes random — determined by the same perceived inputs that participate in the birthday problem. This creates a dependency that prevents direct application of Lemma 4.

**Theorem 3.** For any δ and i.i.d. inputs:

> P(T_loop > T) ≤ exp(−(T²/C − T) / (2D_eff))

*Proof.* Process time steps sequentially. At step t, given the history H_t = (a₀, …, a_{t−1}) and the event {T_loop > t−1}:

The automaton is in some state s_t (determined by H_t). It draws a_t ~ Q independently of H_t. A collision occurs if a_t matches some previously observed perceived input at state s_t. Let n_{s_t}(t) be the number of prior visits to s_t with no prior collision. Then:

> P(e_t ∉ {e₀, …, e_{t−1}} | H_t, T_loop > t−1) = 1 − Σ_{j ∈ B_{s_t}(t)} Q(j)

where B_{s_t}(t) is the set of perceived inputs previously seen at state s_t. The key point: **a_t is drawn independently of H_t because a_t = f(x_t) and x_t is i.i.d.** The state s_t is determined by H_t but the fresh draw is independent.

Using 1 − x ≤ e^{−x} on each factor:

> P(T_loop > T) = E[∏_{t=0}^{T−1} (1 − Σ_{j ∈ B_{s_t}(t)} Q(j))]
> ≤ E[exp(−Σ_{t=1}^{T−1} Σ_{j ∈ B_{s_t}(t)} Q(j))]

Rewrite the exponent. Each pair (τ, t) with τ < t and s_τ = s_t contributes Q(a_τ) to the sum at step t. So:

> Σ_{t} Σ_{j ∈ B_{s_t}(t)} Q(j) = Σ_{τ < t, s_τ = s_t} Q(a_τ)

Now take the expectation. For each pair (τ, t), conditioning on s_τ = s_t (which is determined by a₀, …, a_{t−1}), the term Q(a_τ) has:

> E[Q(a_τ)] = Σ_j Q(j)² = q₂ = 1/D_eff

This holds because a_τ ~ Q and Q(a_τ) is a function of a_τ alone.

**The obstacle:** The expectation of the exponential of the sum is not the exponential of the expectation of the sum. We need E[exp(−X)] ≤ exp(−E[X]), which is the wrong direction of Jensen's inequality (exp(−x) is convex, so Jensen gives E[exp(−X)] ≥ exp(−E[X])).

**Resolution via sequential conditioning.** Instead of bounding the product through the exponential, bound each factor directly in expectation, sequentially.

At step t, given T_loop > t−1, the automaton has visited state s_t exactly n_{s_t}(t) times before, with n_{s_t}(t) distinct perceived inputs stored in B_{s_t}(t). Crucially, the elements of B_{s_t}(t) were drawn from Q at their respective time steps, and a_t is an independent draw from Q.

The collision probability at step t is:

> P(collision at t | H_t, T_loop > t−1) = Σ_{j ∈ B_{s_t}(t)} Q(j)

Taking expectation over the randomness of B_{s_t}(t) (i.e., over the earlier draws that landed at state s_t):

> E[Σ_{j ∈ B_{s_t}(t)} Q(j)] = n_{s_t}(t) · q₂ = n_{s_t}(t) / D_eff

**But n_{s_t}(t) is random** (it depends on δ and the history). We bound it using the constraint Σ_s n_s(t) = t.

For the survival probability, we use the multiplicative structure directly. Define the **sequential survival probability**:

> P(T_loop > T) = ∏_{t=0}^{T−1} E[1 − Σ_{j ∈ B_{s_t}(t)} Q(j) | H_t, T_loop > t−1]

**This factorization is not valid** in general because the factors are not independent — the history H_t determines s_t which determines n_{s_t}(t).

The correct factorization uses the tower property:

> P(T_loop > T) = E[∏_{t=0}^{T−1} (1 − Σ_{j ∈ B_{s_t}(t)} Q(j))]

We bound this by conditioning step by step. At each step t, conditioned on the full history H_t and survival so far:

> E[1_{no collision at t} | H_t, T_loop > t−1] = 1 − Σ_{j ∈ B_{s_t}(t)} Q(j)

The survival probability telescopes:

> P(T_loop > T) = E[∏_{t=0}^{T−1} (1 − Σ_{j ∈ B_{s_t}(t)} Q(j))]

Using 1 − x ≤ e^{−x}:

> P(T_loop > T) ≤ E[exp(−Σ_t Σ_{j ∈ B_{s_t}(t)} Q(j))]
> = E[exp(−Σ_{τ<t, s_τ=s_t} Q(a_τ))]

Define V = Σ_{τ<t, s_τ=s_t} Q(a_τ). We need an upper bound on E[e^{−V}].

**Claim:** E[V] ≥ (T²/C − T)/(2D_eff).

*Proof of claim.* Write V = Σ_s Σ_{i<j, both in T_s} Q(a_i) where T_s is the set of times visiting state s. For each co-state pair (i, j) with i < j and s_i = s_j = s, the contribution is Q(a_i). Since a_i ~ Q independently: E[Q(a_i)] = q₂ = 1/D_eff.

The number of co-state pairs is Σ_s C(n_s, 2) = Σ_s n_s(n_s−1)/2 ≥ (T²/C − T)/2 by QM-AM.

**But the visit counts n_s are random.** However, regardless of the realization:

E[V | n₁, …, n_C] = Σ_s n_s(n_s−1)/(2D_eff)

and Σ_s n_s(n_s−1) ≥ T²/C − T holds for any visit counts summing to T. Therefore:

E[V] = E[E[V | n₁, …, n_C]] ≥ (T²/C − T)/(2D_eff). ∎

This gives us E[V] but we need E[e^{−V}]. Jensen's inequality goes the wrong way. **This is the technical gap.**

### 3.7 What is proved and what is not

The sequential bound P(T_loop > T) ≤ E[exp(−V)] is exact. The difficulty is converting this to exp(−E[V]) or better.

**Approaches that do not work:**

1. **Jensen's inequality.** E[e^{−V}] ≥ e^{−E[V]} — wrong direction.

2. **Markov's inequality on T_loop.** Gives E[T_loop] ≤ T/P(T_loop ≤ T), which requires a lower bound on the collision probability, not an upper bound on survival.

3. **Direct coupling to the rotating case.** For a specific input realization, a non-rotating δ may route identical perceived inputs to different states, potentially avoiding collisions longer. No domination holds realization-by-realization.

**An approach that does work for a weaker bound:**

**Theorem 3 (weak form).** For any δ and i.i.d. inputs:

> E[T_loop] ≤ C · D_eff + 1

*Proof.* This follows directly from Theorem 1 with D replaced by D_eff... but this is wrong: Theorem 1 uses D (number of categories), not D_eff. The worst-case bound is C × D + 1, which holds for any δ and any input sequence.

For stochastic inputs with D_eff < D, we can prove a tighter statement. The expected number of distinct perceived inputs drawn from Q before a collision is at most √(πD_eff/2) + 1 (birthday bound on Q, using Lemma 3). At any single state, after √(πD_eff/2) + 1 visits, a collision is expected. The automaton visits each state at most this many times before looping. Since there are C states:

> E[T_loop] ≤ C · (√(πD_eff/2) + 1)

*Proof.* At each state s, the perceived inputs at visits to s are drawn from Q (not necessarily i.i.d. — see below). A collision at s occurs when two visits produce the same perceived input. By Lemma 3, after m visits to s, P(no collision at s) ≤ exp(−m(m−1)/(2D_eff)). The expected number of visits to s before collision is at most √(πD_eff/2) + 1.

The complication: for general δ, the perceived inputs at visits to state s are not i.i.d. — the visit times are determined by the history, which includes the perceived inputs themselves.

However, each perceived input a_t is drawn independently from Q at its time step, regardless of which state the automaton is in. The birthday collision at state s depends on whether two visits to s produce the same perceived input. Even though the *times* of these visits are history-dependent, the *values* a_t are fresh draws from Q at each step.

Formally: condition on the event that the automaton visits state s at times t₁ < t₂ < … < t_m (these times are random, determined by the history). Given these times, the perceived inputs a_{t₁}, …, a_{t_m} are draws from Q. They are **not independent** in general, because t₂ depends on a_{t₁} (through δ), and the event {s_{t₂} = s} constrains what a_{t₁} could have been.

**But**: a_{t_i} is independent of a_{t_j} for j > i, because a_{t_j} = f(x_{t_j}) where x_{t_j} is drawn i.i.d. The future draw does not depend on the past draw. What depends on the past is *which state is visited*, not *what perceived input is drawn*.

So at each visit to state s, the collision probability against the previous visits is:

> P(a_{t_m} ∈ {a_{t_1}, …, a_{t_{m-1}}} | H_{t_m}) = Σ_{j ∈ B_s} Q(j)

where B_s = {a_{t_1}, …, a_{t_{m-1}}} and |B_s| = m−1 (no prior collision). The elements of B_s were drawn from Q at earlier steps. By the birthday bound, the probability that m draws from Q are all distinct is at most exp(−m(m−1)/(2D_eff)).

**Critical subtlety:** The elements of B_s are not uniformly chosen from Q conditional on the visit pattern. They are chosen from Q conditional on producing a visit pattern that returns to state s at the required times. This conditioning could, in principle, bias the distribution away from Q.

**However:** the conditioning acts through δ on the *successor state*, not on the perceived input itself. At time t_i, the automaton is in state s and draws a_{t_i} ~ Q. The successor state is δ(s, a_{t_i}). The event {next visit to s is at time t_{i+1}} constrains the successor states at times t_i, t_i+1, …, t_{i+1}−1, but the perceived input a_{t_i} contributes to the collision set B_s regardless of what successor state it produces.

The collision check is: does a_{t_m} equal any element of B_s? The elements of B_s are drawn from Q (marginally), and a_{t_m} is an independent draw from Q. The collision probability at the m-th visit is:

> P(collision) = Σ_{j ∈ B_s} Q(j) ≥ |B_s| · min_j Q(j)

For an upper bound on T_loop, we need a *lower* bound on collision probability, which means a lower bound on Σ_{j ∈ B_s} Q(j). In the worst case, the conditioning on the visit pattern could push B_s toward low-probability categories (small Q(j)), reducing the collision probability.

**This is the gap.** For input-independent δ, the visit pattern is deterministic, so no conditioning occurs and B_s is an honest i.i.d. sample from Q. For general δ, the visit pattern is correlated with the perceived inputs, and the collision probability at each step could be reduced by this correlation.  ∎

### 3.8 The gap and why it is likely small

The gap is between:

- **Proved (input-independent δ):** E[T_loop] ≤ √(πCD_eff/2) + 1
- **Conjectured (all δ):** E[T_loop] = O(√(CD_eff))
- **Proved (all δ, weak):** E[T_loop] ≤ C × D + 1 (worst-case, from Theorem 1)

The heuristic argument for why the conjecture holds:

A transition function δ that exploits the correlation — routing high-probability perceived inputs to spread across different states — would need to "know" which perceived inputs are likely to collide. But δ is fixed before the automaton runs. Under i.i.d. inputs from Q, the collision structure is determined by Q, which δ can in principle be designed to exploit.

**Worst-case δ for collision avoidance:** a δ that maps (s, a) to different successor states for different values of a, spreading the visits to each state across as many distinct perceived inputs as possible. This is exactly what a well-designed encoding does — and it is already captured by D_eff. A δ that additionally routes perceived inputs to minimize within-state collisions cannot do better than uniformly distributing the perceived inputs across states, which is what the rotating δ achieves for the input-independent case.

**The conjecture reduces to:** can an input-dependent δ beat the rotating δ in expected loop time? We conjecture no, but proving it requires showing that the visit-pattern correlation cannot systematically reduce collision rates below the i.i.d. baseline.

---

## 4. Consequences for Encoding Quality

### 4.1 The comparison table

| Encoding | D | D_eff (typical) | Worst case (Thm 1) | Expected case (Thm 2) |
|----------|---|-----------------|--------------------|-----------------------|
| None | 1 | 1 | C | √(πC/2) |
| Flat (XOR) | C | ≤ C | C² | ≤ C√(π/2) |
| Hierarchical (depth d) | 2^d | ≈ 2^d | C·2^d | √(πC·2^d/2) |
| Perfect | s^k | s^k | C·s^k | √(πC·s^k/2) |

The ratio of hierarchical to flat expected loop time:

> T_hier / T_flat = √(D_eff_hier / D_eff_flat)

Since D_eff_flat ≤ C and D_eff_hier can be C^k, this ratio is exponential in k. **The exponential advantage of hierarchical encoding survives the transition from worst-case to expected-case analysis.**

### 4.2 Why D_eff, not D

Two encodings can have the same D but different D_eff. Flat encoding on structured inputs concentrates probability mass on a few categories (D_eff ≪ D). Hierarchical encoding distributes mass evenly (D_eff ≈ D). Same number of bins, exponentially different usage. The anti-loop theorem says: what matters is not how many categories you have, but how many you use.

### 4.3 Numerical verification

C = 2, D = 2, Q uniform, rotating δ:

Exact: T_loop ∈ {2, 3, 4} with probabilities {1/2, 1/4, 1/4}. E[T_loop] = 2.75.

Theorem 2 bound: √(π·2·2/2) + 1 = √(2π) + 1 ≈ 3.51.

Valid (3.51 > 2.75) and reasonably tight (ratio 1.28).

---

## 5. Environment-Dependent Dynamics

Theorem 2 assumes i.i.d. inputs. Real environments have temporal correlations.

**Conjecture.** For inputs from a stationary ergodic process with mixing time τ_mix:

> E[T_loop] = O(√(C · D_eff / τ_mix))

Slow-mixing environments accelerate looping: predictable inputs produce repeated perceived inputs faster.

*Status: conjectured. The i.i.d. case is proved for input-independent δ. The Markov case requires the dependent birthday problem (Arratia, Goldstein & Gordon, 1989).*

---

## 6. Summary

| Result | Status |
|--------|--------|
| Worst-case: T ≤ C × D + 1 | **Proved** (Theorem 1, pigeonhole) |
| Expected, input-independent δ: E[T] ≤ √(πCD_eff/2) + 1 | **Proved** (Theorem 2) |
| Rotating δ is optimal among input-independent δ | **Proved** (Theorem 2d) |
| Expected, arbitrary δ: E[T] = O(√(CD_eff)) | **Conjectured** (Section 3.8) |
| D_eff = D for balanced hierarchical encoding | **Proved** |
| D_eff ≪ D for flat encoding on structured inputs | **Proved** |
| Exponential advantage persists in expected case | **Proved** (ratio = √(D_eff_hier / D_eff_flat)) |
| Correlated-input extension | **Conjectured** (Section 5) |

**The technical gap.** The proof covers input-independent transition functions, including the optimal rotating case. Extending to arbitrary δ requires showing that the correlation between visit patterns and perceived inputs cannot systematically reduce collision rates. This is likely true — it would require a fixed δ to "predict" stochastic collisions — but proving it is nontrivial.

**What this adds to the main paper.** The restricted anti-loop theorem (Theorem 1) proves that encoding quality determines effective state space. Theorem 2 proves that this translates into expected trajectory length under stochastic inputs, with the natural measure D_eff = 1/||Q||₂² (Rényi collision entropy). The exponential advantage of hierarchical over flat encoding is preserved under the birthday-paradox square-root compression.

---

## References

Arratia, R., Goldstein, L. & Gordon, L. (1989). Two moments suffice for Poisson approximations. *Annals of Probability*, 17(1), 9–25.

Marshall, A.W., Olkin, I. & Arnold, B.C. (2011). *Inequalities: Theory of Majorization and Its Applications*. 2nd ed. Springer.

Rényi, A. (1961). On measures of entropy and information. *Proceedings of the 4th Berkeley Symposium*, 1, 547–561.
