# The Lazy Universe

**What One Rule Builds When It Has No Choice**

Karol Kowalczyk · March 2026 · Working Paper v4.0

---

## Abstract

One rule — don't repeat — and three structural assumptions: something exists, it's deterministic with finite memory, and it can spawn. This paper traces what such a system must build to keep obeying that rule, and finds that the answer looks like a universe.

The entity runs out of states and must create something external. Creating a child creates a connection. Connections flood the entity with more input than it can track, and we prove that poor tracking leads to faster looping — so internal encoding must become hierarchical. Hierarchical encoding eventually fills up too, and the only external act is to spawn again. This cycle of three pigeonhole arguments repeats at every scale. Hierarchy, reproduction, and structure all fall out.

Within this framework, what we call matter is the set of encodings shared by many entities — consensus. What we call mind is the part that belongs to one entity alone. The universe computes only what some entity is actively encoding: a lazy reality where detail exists only where the rule demands it. We propose an experiment — within the model — that can distinguish "unbuilt" from merely "unobserved."

Simulation produces heavy-tailed topology (α ≈ 2.05 at 44k nodes, lognormal-like rather than strict power-law per Broido-Clauset testing), mutual information excess on edges (ρ ≈ 1.15, 29σ), three growth phases with a sharp phase transition between expansion and plateau (confirmed, not gradual as originally predicted), and a power-law distribution of encoding-sharing.

---

## 1. The Rule

A finite deterministic system must eventually revisit a state. This is the pigeonhole principle. It is not controversial.

Now add one constraint: **it may not.**

That is the rule. The rest of this paper is bookkeeping — tracing what a system must build, step by step, to keep obeying it.

Four assumptions frame the problem:

**A1. Something exists.** One entity. Finite states. Deterministic: each state leads to exactly one next state, determined by the entity's current state and its environment.

**A2. The anti-loop rule.** The entity must not revisit a state it has already been in.

**A3. Bounded memory.** The entity cannot grow its own state space.

**A4. The entity can spawn.** It can create a new entity external to itself.

A1 and A2 create the tension. A finite deterministic system *must* loop (pigeonhole), but *may not* (the rule). A3 closes the easy escape — you cannot dodge loops by expanding your own memory. A4 is the one assumed capability: the entity can produce something new. Just that. Everything else in the paper — connection, encoding, hierarchy — is derived.

Why spawning? Because a solitary entity in an empty universe that must act externally has nothing to observe, nothing to connect to, nothing to modify. The only external act available when nothing else exists is to create something. A4 is not a choice from a menu. It is what "act externally" means when you are alone.

---

## 2. What the Rule Forces

Each step below is a classical theorem, a derivation from A1–A4, or flagged as an assumption.

### 2.1 The Entity Must Spawn

One entity. Capacity C. It visits all C states and is full. The anti-loop rule says: find a new state. Internal expansion is blocked (A3). Nothing else exists — there is nothing to observe. The only operation available is A4. The entity spawns.

*Status: derived from A1–A4 by elimination.*

### 2.2 Spawning Creates a Connection

The parent spawns a child. Now the child exists in the parent's environment. By A1, the parent's next state is determined by its current state *and its environment*. The environment has changed — there is a new entity in it. Therefore the parent's trajectory changes.

This is what a connection is: the child's existence affects the parent's subsequent states. It is not a separate operation. It is a side effect of spawning.

For this to work, the parent must not be sealed off from its environment. But we already know it cannot be sealed: a sealed entity with bounded memory under the anti-loop rule is simply impossible — it loops, full stop, contradicting A2. So the parent's transition function takes environment as input. The child is now in the environment. The connection exists.

*Status: derived from A1 (transition function depends on environment), A2 (sealed entities are impossible), and A4.*

### 2.3 Connections Create an Impossible Problem

An entity with k connections, each carrying a signal with s possible values, faces s^k possible input patterns. This grows exponentially with the number of connections. The entity's internal capacity is bounded. When s^k exceeds the capacity, multiple distinct input patterns must land on the same internal state (pigeonhole). The entity cannot tell them apart. It is blind to differences that its own connections are delivering.

This is Pigeonhole 2.

### 2.4 Blindness Leads Back to Looping

This is the critical step. Being blind does not directly violate A2 — the anti-loop rule constrains the sequence of states, not the entity's awareness. But blindness reduces the entity's ability to avoid loops. Here is why.

An entity's trajectory — the sequence of states it visits — is determined step by step by the combination of its internal state and its perceived input. Call this combination the **effective state**. The entity has C internal states and can distinguish D input patterns. So it has at most C × D effective states. After C × D + 1 steps, it must revisit an effective state (pigeonhole). Same internal state, same perceived input. The transition function is deterministic. The successor is the same as last time. The entity loops.

Now compare encoding quality:

With **no connections** (D = 1): effective states = C. The entity loops within C steps. This is just the original problem.

With **flat encoding** (D = C): effective states = C². Connections helped, but only quadratically.

With **hierarchical encoding** of depth d (D = 2^d): effective states = C × 2^d. Exponentially better. Still finite, still subject to pigeonhole — but the fuse is incomparably longer.

With **perfect encoding** (D = s^k): effective states = C × s^k. Maximum possible benefit from connections.

The ratio tells the story. A flat encoder gets C² effective states out of connections that could have provided C × s^k. It is wasting a factor of s^k / C. When k is even moderately large, this is an astronomically shorter fuse.

**Theorem (restricted blindness).** Let E be an entity with C internal states and k connections each carrying s-valued signals. If E's encoding distinguishes D < s^k input patterns, then E must revisit an effective state within C × D + 1 steps. An entity with the same memory and connections but encoding D' > D patterns lasts at least C × D' + 1 steps. The loop-avoidance benefit of connections scales linearly with encoding quality.

*Proof.* The effective state space has size C × D. The trajectory through effective states is deterministic. By the pigeonhole principle, a revisit occurs within C × D + 1 steps. A revisited effective state — same internal state, same perceived input — produces the same successor, initiating a loop. An entity distinguishing D' > D patterns has a strictly larger effective state space and therefore a strictly longer minimum trajectory before forced revisit. ∎

The consequence: hierarchical encoding is not an operation that the entity "chooses." It is a selection effect. Any entity whose encoding is flat exhausts its effective states almost immediately and is forced to spawn while still shallow and simple. Entities with hierarchical encodings last exponentially longer. Over time, the surviving population is dominated by hierarchical encoders — not because anyone chose it, but because those are the ones that last.

**Where the variation comes from.** Selection requires variation — some entities must have flat encoding and others hierarchical. M1 provides this without any additional mechanism. A spawned child is a *new* finite deterministic system (A1), not a copy of the parent. The child starts blank: its own state space, its own transition function, no inherited encoding. Since different children occupy different positions in the network, they receive different inputs and develop different effective encodings. The effective number of input distinctions D_eff depends on how the child's transition function responds to the inputs it actually receives. Variation across the population is automatic — it comes from network position diversity, not from mutation or randomness.

*Status: the selection argument is now complete. The blindness theorem provides the fitness landscape (higher D_eff → longer trajectory). M1 provides the variation (children are new systems in diverse positions). No additional mechanism is required.*

*Status: the theorem is proved for the worst case. The general case — exact bounds as a function of environmental dynamics, not just worst case — is open (O9). But the worst case is sufficient: flat encoding is strictly worse than hierarchical encoding by a factor that grows exponentially with the number of connections. This makes restructuring not merely advantageous but, for any entity with nontrivial connectivity, practically inevitable.*

### 2.5 The Encoding Saturates

Under A3, the hierarchical encoding cannot deepen forever. It has a maximum depth d_max set by the memory bound. The entity keeps spawning under loop pressure (2.1), which keeps creating connections (2.2), which keeps growing the input space. Eventually s^k exceeds 2^d_max. The encoding is overwhelmed — again.

This is Pigeonhole 3. The same crisis that forced hierarchical encoding now exceeds what hierarchical encoding can handle.

Could the entity manage the problem differently? In principle, if disconnection were available, the entity could drop some connections to reduce input complexity. But disconnection is a retreat — it shrinks the pool of new states available for loop avoidance. The entity would saturate again with fewer resources. And disconnection is not in A4 anyway. The only external operation is spawn.

### 2.6 The Entity Spawns Again

The anti-loop rule still applies. Internal expansion is blocked (A3). The encoding is maxed out (2.5). The only operation is A4: spawn. The child is a new finite deterministic system — it starts blank, with its own state space and its own transition function, not a copy of the parent. It receives input from the parent through the connection that spawning creates (2.2). From the parent's perspective, the child compresses a region of the parent's input space and feeds back one digestible channel.

The child exists because the parent had no other way to keep obeying the rule.

*Status: derived from A3, A4, and the exhaustion of alternatives.*

### 2.7 The Cycle Repeats

The child is a finite deterministic entity with bounded memory, subject to A2. It must spawn (2.1), which creates connections (2.2), which creates exponential input (2.3), which forces hierarchical encoding (2.4), which eventually saturates (2.5), which forces spawning again (2.6). Three pigeonhole arguments, cycling at every level.

Each level's capacity grows as a tower of powers. At level L: s^(k^L). Each level takes incomprehensibly longer to saturate than the one below. A being at level L experiences levels 0 through L−1 as ancient, fully resolved structure — what it would call its body. Level L is its current exploration — its lifetime. Level L+1 is something it will never see completed.

*Status: structural recursion. Formal proof of the tetration result is pending (O3).*

---

## 3. What the Anti-Loop Rule Produces

The cycle above, driven entirely by the rule, produces the following. None of it was assumed.

### 3.1 Hierarchy

Entities exist at multiple depths. Shallow ones make few comparisons, saturate fast, spawn quickly. Deep ones make many comparisons, fill slowly, dominate the later phases. Every entity is simultaneously a whole (its own encoding, its own trajectory) and a part (a component of something larger). There is no privileged level.

### 3.2 Heavy-Tailed Topology

Older entities have more children (they have been spawning longer) and more connections (every spawn creates one). Degree is proportional to age. This produces a heavy-tailed degree distribution — the same pattern found in the internet, social networks, and biological systems.

In simulation: α ≈ 2.05 at 44k nodes (tree-depth spawn model, Clauset-Shalizi-Newman methodology). The degree distribution is heavy-tailed and hub-dominated; at large scale it is better fit by lognormal than strict power-law, consistent with Broido & Clauset (2019) findings for most real-world networks. Random tree control shows α ≈ 2.85 with no heavy tail — the separation is unambiguous. The mechanism is not assumed. It falls out of the spawning rule.

*Note on the wiring rule: every connection in the base model is a parent-child link created by spawning. Lateral connections — wiring to entities you didn't spawn — could emerge if signals propagate through the existing tree. Whether lateral wiring needs a separate mechanism or follows from signal propagation is open (O1).*

### 3.3 Three Growth Phases

The anti-loop rule produces three phases from a single mechanism as average encoding depth increases.

**Phase 1: Expansion.** Entities are shallow. They fill fast. They spawn fast. The dominant activity is reproduction. The universe grows rapidly.

**Phase 2: Transition.** The spawn rate peaks and collapses. This is not a gradual deceleration — simulation shows it is a near-discontinuous phase transition lasting only ~15 steps (uniform memory) or ~10 steps (variable memory) out of hundreds. Once the tree is deep enough that new children face sufficient input diversity, all nodes saturate within a few steps of each other. The original prediction of "continuous deceleration" was wrong; the transition is sharp.

**Phase 3: Structure.** Spawning has stopped. Most entities are still exploring their state spaces. In the pure tree model, this phase is static. In models with lateral wiring, the dominant activity would be forming new connections under continuing loop pressure.

**Phase boundary criteria (tested).** Two measurables, confirmed by simulation (O5, 10 seeds, 25k nodes):

*Peak spawn rate:* Phase 1 ends when the smoothed spawn rate reaches its maximum. This occurs at ~49% of the simulation timeline, remarkably stable across seeds (± 2 steps). The spawn rate then drops to zero within ~16 steps.

*Per-capita spawn rate:* Phase 2 ends when per-capita spawn rate drops below 1/N. This occurs at ~51% of the timeline. The brevity of Phase 2 (~16 steps between boundaries) confirms it is a transition, not an era.

*Median tree depth:* Rises in discrete jumps (0 → 1 → 2 → 3), stabilizing at 3 for 8-bit FSM. Max tree depth reaches 5. These are consistent across seeds.

**Variable memory test (O5b).** To test whether the sharp Phase 2 is an artifact of uniform memory (all entities having identical 256-state FSMs), we ran the same experiment with variable memory (4-8 bit per entity, 16-256 states). Result: Phase 2 becomes *shorter* (10 steps vs 15), not more gradual. The sharp transition is fundamental to the model dynamics, not an artifact of homogeneity.

### 3.4 Reproduction

Every entity reproduces. This is not natural selection. It is not an optimization. It is Pigeonhole 3: a saturated encoding in bounded memory has no other move under A4. The child starts blank — a new system with its own transition function — and deepens its encoding under the same loop pressure that forced the parent to spawn. Each generation does not inherit complexity; it builds its own, driven by the inputs available at its network position.

### 3.5 Edges That Carry Information

In the LPAN simulation model, edges carry about 15% more mutual information than non-edges (ρ ≈ 1.15, 29σ over 30 seeds). This signature does not appear in random graphs, preferential-attachment graphs, or spawn-only topologies.

This is the measurable fingerprint of the anti-loop rule. Each edge exists because a specific entity needed that specific connection to avoid repeating itself. Connections formed for dynamic reasons carry information by construction. Connections formed for random or geometric reasons do not.

---

## 4. The Lazy Universe

Here is where the anti-loop rule produces something strange.

Resolution — how finely an entity carves up its environment — exists only where a comparison is being made. If no entity is encoding at a given resolution, that resolution is not low-quality or blurry. It is uncomputed. It does not exist.

The anti-loop rule demands only that each entity can distinguish enough of its input to avoid revisiting a state. It does not demand that the rest of reality be detailed. So it isn't.

Think of a distant star. From the perspective of an entity that distinguishes only wavelength and brightness, that star is three numbers. Not 10^57 atoms. The atomic structure is there only if some entity is comparing at that depth — because some entity needed that depth to obey the rule.

This is the lazy universe: one that computes exactly as much as the anti-loop rule requires, and nothing more. Unobserved structure is not hidden. It is unbuilt.

This is not a claim that reality is imaginary. The entities are real. The comparisons are real. But the resolution at which reality is detailed depends on what is comparing. The universe is efficient not by design but because the rule generates only as much structure as it needs and stops.

Game engines work the same way — they do not render what the camera is not looking at. Whether quantum mechanics works the same way is an open question (O7). But within the model, the distinction between "unbuilt" and "hidden" is not metaphysical. It is testable.

### 4.1 Testing "Unbuilt" vs. "Hidden"

The claim that unresolved structure is unbuilt rather than hidden sounds philosophical. It is not. Within the model, it makes a specific prediction.

**Setup.** Two clusters of entities, A and B, that are not connected to each other. Both are connected to a distant region R that neither cluster currently encodes at high resolution — R is unresolved from both perspectives.

**Experiment.** At the same time step, both clusters independently begin encoding region R — building new comparisons about it from their own input sources.

**Prediction under "unbuilt."** R has no structure until someone encodes it. Clusters A and B are building their encodings independently, from different input paths. Their initial encodings of R should *disagree* — they are constructing resolution, not discovering it. Agreement emerges later, as their encodings propagate through shared connections and converge toward consensus.

**Prediction under "hidden."** R has definite structure that A and B are merely uncovering. Their encodings should agree *from the start*, because they are reading the same pre-existing reality.

The measurable: **initial inter-cluster agreement on newly encoded features, tracked over time.**

If agreement starts low and converges → consistent with "unbuilt."
If agreement is high from the first step → consistent with "hidden."

This is testable in simulation. It has a structural resemblance to Bell tests: two independent observers, a shared target, correlation as the measurable. Whether an analogue of Bell's inequality can be defined within the framework — a bound that "hidden" structure must obey and "unbuilt" structure can violate — is open (O7). But the experiment itself is well-defined and could be run today.

---

## 5. Matter Is Consensus. Mind Is What's Left Over.

*This section is interpretive. It offers one way to read the formal structure of Sections 2–4. The formal results do not depend on it.*

Each entity has an encoding — a tree of comparisons. When two connected entities share a comparison — both make the same yes-or-no split on the same input feature — that comparison is functionally stable for both: neither entity's behavior with respect to that feature changes when the other is active. It is a fact they agree on, in the specific sense that their encodings produce the same output for it.

When many entities share the same comparison, it becomes something like what we call a physical law: a distinction that nearly everyone makes. Not because it was imposed from outside, but because the comparison is old and has spread through the network under the same loop pressure that built everything else.

In simulation, a network of encoding trees that share comparisons with neighbors produces a characteristic distribution. A small number of ancient comparisons spread to the majority of entities — **fundamental structure**, the distinctions nearly everyone makes. A larger number are shared regionally — **local structure**, analogous to chemistry or geology. About 46% of comparisons remain unique to one entity — **subjectivity**, the part of the encoding that belongs to you alone.

For comparison, a random-diffusion process on the same network topology produces a more uniform distribution. The heavy tail — a few comparisons shared very widely, many shared by no one — is a feature of the model's depth-dependent dynamics, not just the network shape.

The distribution of sharing follows a power law. Deeper entities have a higher fraction of shared comparisons (96% at depth 7 vs. 100% at depth 1), which makes sense: deepening mostly happens by learning existing distinctions from neighbors, not by inventing new ones.

Here is the interpretive leap — flagged as such.

If you accept the framework, then the *stability* of what we call matter is the number of entities sharing a comparison. Physics feels solid because the comparisons that constitute it are shared by nearly everything. A rock feels solid because every entity nearby makes the same distinctions about it. Subjective experience feels private because those comparisons are shared by no one.

This does not yet explain why shared comparisons should *constrain* each other the way physical laws do, rather than merely coexisting (O6). But the pattern is suggestive. The same rule that forces structure, hierarchy, and reproduction also produces a natural spectrum from "everyone agrees" to "only I see this." The matter-mind distinction, in this reading, is not two kinds of stuff. It is a measure of how widely a comparison has spread.

And the anti-loop rule produced all of it.

---

## 6. Simulation Results

All claims in Sections 3–5 are supported by simulation. Code and data are in the accompanying repository.

**Heavy-tailed topology.** Tree-depth spawn model at 44k nodes (30 seeds, auto-calibrated, CUDA-accelerated): α ≈ 2.05 ± 0.02. Power-law beats exponential (30/30 seeds at 500 nodes; 2–3/3 at 44k nodes), but lognormal and stretched exponential beat strict power-law at large scale (p < 0.0001). This is expected: Broido & Clauset (2019) found most real-world "scale-free" networks fail strict CSN testing at sufficient sample size. The scientifically precise claim is that antiloop produces a heavy-tailed, hub-dominated degree distribution near α ≈ 2 — sharply distinct from random trees (α ≈ 2.85, all alternatives beat power-law 30/30). LPAN model with lateral wiring: α ≈ 2.47 (30 seeds, small scale).

**Mutual information excess.** LPAN edges carry about 15% more mutual information than non-edges (ρ ≈ 1.15). This is 29 standard deviations from zero over 30 seeds. Tested against three null models — random graphs, preferential-attachment graphs, and spawn-only topologies. None show the effect. The excess is specific to edges formed under loop pressure.

**Three phases (O5).** Population growth shows rapid expansion, a sharp transition (~16 steps), and a long plateau. Confirmed in 10/10 seeds at 25k nodes. Phase boundaries are remarkably stable across seeds (± 2 steps). The originally predicted "gradual deceleration" is wrong — Phase 2 is a near-discontinuous phase transition. Variable memory (O5b, 4-8 bit per entity) makes the transition *sharper*, not more gradual, confirming this is fundamental to the dynamics.

**Consensus formation.** The most-shared comparison reaches ~11% of entities at step 50. About 46% of comparisons remain unique to one entity. Sharing follows a power law. A random-diffusion null model on the same topology produces a more uniform distribution, confirming that the heavy tail comes from depth-dependent dynamics. Deeper entities share more (96% at depth 7).

---

## 7. The Derivation Chain

| # | Claim | Status |
|---|-------|--------|
| 1 | Finite + deterministic → must loop | Classical (pigeonhole) |
| 2 | A loop produces no new states | Classical (determinism) |
| 3 | Solitary entity under A2 + A3 → must spawn (A4) | Derived by elimination |
| 4 | Spawning creates a connection | Derived from A1 (environment in transition function) |
| 5 | Connections → exponential input space | Combinatorics |
| 6 | Flat encoding fails under exponential input | Pigeonhole 2 |
| 7 | Indistinguishable inputs reduce effective state space, accelerating loop pressure | Proved (restricted case; general case = O9) |
| 8 | Hierarchical encoding is a selection effect: flat encoders loop too fast to persist | Derived from 6–7; variation from M1 (children start blank, network position diversity) |
| 9 | Finite encoding + growing connections → overwhelmed | Pigeonhole 3 |
| 10 | Spawning is the only external operation (A4) | Axiom |
| 11 | Cycle repeats → hierarchy | Structural recursion |
| 12 | Capacity grows by tetration | Derived (formal proof pending, O3) |
| 13 | Heavy-tailed topology (α ≈ 2.05, lognormal-like at scale) | Simulation (30 seeds, 44k nodes, Broido-Clauset) |
| 14 | Three phases (sharp transition, not gradual) | Simulation (O5, 10 seeds, 25k nodes; O5b variable memory confirms) |
| 15 | Edges carry MI excess | Simulation (ρ ≈ 1.15, 29σ) |
| 16 | Shared encodings → consensus structure | Simulation |

Steps 1–2 are classical. Steps 3–4 are derived from the axioms. Steps 5–9 are derived, with Step 7 proved in the restricted case. Steps 10 is an axiom. Steps 11–12 are derived (tetration proof pending). Steps 13–16 are confirmed by simulation.

---

## 8. Why Spawning

The derivation assumes one external operation: spawn. This section explains why.

A sealed entity — one whose transition function depends only on its own internal state — with bounded memory under the anti-loop rule is impossible. It has C states, it must visit each at most once, it loops after at most C steps. Contradiction. So the entity must be open to its environment: its transition function must depend on something external.

But what can an entity *do* to something external? In an empty universe — which is where we start — there is nothing to observe, nothing to modify, nothing to connect to. The only act that makes sense when nothing else exists is to create something. That is what A4 says.

This has a natural information-theoretic reading. Spawning is a *write* operation: the entity produces something new in the environment. The connection that spawning creates (Section 2.2) is a *read* operation: the parent observes the child's output. Restructuring (Section 2.4) is *compression*: the entity organizes its internal encoding to handle more input. Write, read, compress. These are the three elementary operations of a channel interacting with a noisy environment — and they are not three axioms. They are one axiom (write/spawn) and two consequences (read/connect from spawning, compress/restructure from selection pressure).

Other operations are conceivable. An entity could merge with another, or prune an existing connection, or directly modify another entity's state. The framework does not rule these out — it simply does not include them. Whether adding operations changes the qualitative results is unexplored (O1).

A different formulation — possibly cleaner — would skip dynamics entirely and ask: what structural properties must the class of all finite deterministic non-repeating systems have? That is a characterization question rather than a story about what entities "do." Whether it produces the same results is open.

---

## 9. Open Problems

**O1. Lateral wiring.** Every connection in the base model is a parent-child link. Do lateral connections (wiring to non-offspring) require a separate mechanism, or do they emerge from signal propagation through the spawn tree? If separate, can they be derived from A4 or do they require a fifth axiom?

**O2. Encoding uniqueness.** Does the selection argument (Section 2.4) uniquely favor binary comparison trees, or do other logarithmic-access encodings survive equally well?

**O3. Prove the tetration result.** Formally prove tower-of-powers capacity growth at each hierarchy level.

**O4. Scale testing.** CSN analysis at 10^4–10^5 entities. Full Broido-Clauset protocol with lognormal and stretched-exponential comparisons.

**O5. Phase boundary validation.** Test the spawn-to-wire ratio and median encoding depth as quantitative criteria for phase transitions. Do they carve the growth curve where the theory predicts?

**O6. Consistency of shared comparisons.** Physical laws constrain each other. Shared comparisons in the model currently just coexist. Under what conditions do shared comparisons begin to constrain each other?

**O7. The quantum analogy.** The lazy universe computes only what is being compared. Quantum mechanics assigns definite properties only to measured systems. The "unbuilt vs. hidden" experiment (Section 4.1) is a first step. Can a Bell-type inequality be defined within the framework?

**O8. The deepening threshold.** At how many connections per depth level is restructuring triggered? Derivable from the selection argument, or free parameter?

**O9. The blindness theorem (general case).** The restricted case (Section 2.4) proves that indistinguishable inputs reduce effective state space. The general case asks: given specific environmental dynamics (not just worst case), how quickly does a D-blind entity loop as a function of D, C, and the statistics of its input? A tight bound here would make hierarchical encoding not just favored but quantifiably inevitable.

---

## 10. What This Paper Does Not Claim

**It does not claim the universe is this system.** The model is a minimal architecture that produces universe-like features. Whether the physical universe satisfies A1–A4 is empirical.

**It does not claim spawning is the only possible operation.** It claims spawning is the only operation needed. Other operations (merging, pruning, interference) might produce different or similar structures. The claims are conditional on A4.

**It does not prove the encoding must be a binary tree.** It proves flat encoding fails catastrophically (the blindness theorem) and shows that hierarchical encoding survives. Binary trees are the simplest instance.

**It does not claim matter is illusory.** It offers a reading of matter as consensus among encoders. The rock is real. The claim is about what "real" consists of.

**It does not prove "unbuilt."** It proposes a testable experiment (Section 4.1) that can distinguish "unbuilt" from "hidden" within the model. The experiment has not yet been run.

**It does not yet have large-scale validation.** Simulations are preliminary at ~3,000 entities. They illustrate the framework. They do not yet constitute rigorous evidence at the scale the claims require.

**It does not claim to be the only model.** The anti-loop rule is sufficient. It may not be unique.

---

## References

Broido, A.D. & Clauset, A. (2019). Scale-free networks are rare. *Nature Communications*, 10, 1017.

Carayol, A. & Nicaud, C. (2012). Distribution of the number of accessible states in random automata. *STACS 2012*.

Clauset, A., Shalizi, C.R. & Newman, M.E.J. (2009). Power-law distributions in empirical data. *SIAM Review*, 51(4), 661–703.

Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory*. 2nd ed. Wiley.

Kauffman, S.A. (2000). *Investigations*. Oxford University Press.

Krapivsky, P.L., Redner, S. & Leyvraz, F. (2000). Connectivity of growing random networks. *Physical Review Letters*, 85(21), 4629.

Myhill, J. (1957). Finite automata and the representation of events. *WADD TR-57-624*, 112–137.

Nerode, A. (1958). Linear automaton transformations. *Proceedings of the AMS*, 9, 541–544.

Shannon, C.E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
