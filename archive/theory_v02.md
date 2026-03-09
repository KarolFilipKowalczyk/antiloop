# Non-Looping Existence: A Formal Framework

**Authors:** Karol Kowalczyk, Claude (Anthropic, LLM co-author)
**Date:** March 2026
**Version:** 0.3 — revised after adversarial review and C1 simulation
**Status:** Working draft for review

---

## Part I: Formal Results

### Axioms

**A1 (Existence):** There exists at least one state distinguishable from the empty set.

**A2 (Observer):** There exists at least one entity that undergoes state transitions — an entity whose current state is determined by a transition function applied to prior states.

**A3 (Sequentiality):** The entity in A2 must traverse at least two distinguishable states.

**Note on A2:** The original formulation used the term "consciousness" as a primitive. This was an unwarranted ontological commitment. The revised axiom commits only to the existence of a state-transitioning entity — a finite automaton. Whether such an entity is "conscious" in any phenomenological sense is a separate question that this framework does not answer and does not require.

**Note on minimality:** We do not formally prove independence of A1–A3. We observe informally that removing any one axiom collapses the framework: without A1, there is no subject matter; without A2, there is no dynamics; without A3, there is no process. A formal independence proof would require constructing models satisfying any two axioms but not the third. This remains an open problem.

### Definitions

**D1 (Node):** An observer is modeled as a computational node N = (S, M, T) where S is a finite set of internal states, M is a finite memory of size |M|, and T: (S × M) → (S × M) is a deterministic transition function.

**D2 (Configuration):** A configuration is a pair c = (s, m) where s ∈ S and m ∈ M. The configuration space C of a node is finite, with |C| ≤ |S| × 2^|M|.

**D3 (Loop):** A trajectory is a loop if there exist time steps t > k such that c_t = c_k. From that point, the trajectory repeats identically.

**D4 (Graph):** Multiple nodes form a graph G = (V, E) where V is the set of nodes and E represents interactions between nodes. An interaction is a function that takes configurations of two connected nodes and produces updated configurations for both. Interactions are local — each node interacts only with its neighbors in G.

### Theorems

**T1: Finite isolated nodes must loop.**

*Statement:* Any node N with finite configuration space |C| and no external input must, after at most |C| transitions, enter a previously visited configuration.

*Proof:* By the pigeonhole principle. The transition function T is total and deterministic on a finite set C. A sequence of length |C| + 1 drawn from a set of size |C| must contain a repetition. Since T is deterministic, once a configuration repeats, the entire subsequent trajectory repeats identically. ∎

**T2: Loops are informationally degenerate.**

*Statement:* A looping trajectory produces no new information after the first complete cycle.

*Proof:* Information is here defined in the Shannon sense: a message carries information if and only if it reduces uncertainty about the system's state. After one complete cycle of a loop, the trajectory is fully predictable from the loop structure. Every subsequent state is determined with probability 1 from the loop description. Therefore, no subsequent state reduces uncertainty. The information content of the trajectory after the first cycle is zero. ∎

*Critical remark:* T2 establishes informational degeneracy, not experiential equivalence with non-existence. A looping node with no memory of prior cycles may undergo state transitions that are, from its internal perspective, indistinguishable from a first traversal. Whether this constitutes "experience" or "non-experience" depends on one's theory of consciousness, which this framework deliberately does not adjudicate. We note only that the loop produces no new information, and that any definition of experience requiring novelty (new information) would classify the loop as experientially degenerate. This conditional is the strongest claim we can formally make.

**T3: If experience requires novelty, then a conscious node must avoid loops.**

*Statement:* Under the assumption (which we label **Assumption N**) that experience requires the production of new information, a node that enters a loop ceases to have experiences.

*Proof:* By T2, a looping trajectory produces no new information after the first cycle. By Assumption N, experience requires new information. Therefore, a looping node does not experience after the first cycle. ∎

*Note:* Assumption N is not derived from A1–A3. It is an additional commitment, clearly labeled. The formal results that follow are conditional on it.

**T4: Finite isolated nodes cannot sustain experience indefinitely.**

*Statement:* Given Assumption N, a node with finite configuration space and no external input will eventually cease to have experiences.

*Proof:* By T1, it must loop. By T3, looping terminates experience. ∎

**T5: Sustained experience requires state-space growth.**

*Statement:* For a node to avoid looping indefinitely (given Assumption N), at least one of the following must hold:
  (a) The node's configuration space must grow over time (internal growth), or
  (b) The node must receive input from external sources that it has not previously exhausted (external input).

*Proof:* T1 shows that a finite, isolated deterministic system must loop. The pigeonhole argument fails only if the set over which the pigeonhole principle is applied grows without bound. This requires either expanding |C| (option a) or introducing genuinely new configurations via external interaction (option b). ∎

**T6: A finite graph of finite nodes cannot sustain universal experience indefinitely.**

*Statement:* Given Assumption N, for a finite graph G with total configuration space C_G = ∏|C_i| for all nodes i, all nodes will eventually loop unless the graph grows.

*Proof:* The combined system of all nodes and their interactions forms a composite system with finite total configuration space |C_G|. By the pigeonhole principle applied to the composite system, the global state must eventually repeat. Once it repeats, every node's trajectory repeats (since interactions are deterministic functions of configurations). By T3, all experience ceases. To prevent this, |C_G| must grow without bound, which requires either adding nodes, expanding individual nodes' configuration spaces, or both. ∎

*Note on the strength of this claim:* T6 shows that *within this model*, sustained universal experience requires unbounded growth. A critic may reasonably respond: "Then perhaps the model is inadequate." This is a valid objection. The conclusion is about the model, not necessarily about reality. We return to this in Part III.

---

## Part II: Formalizable Conjectures

The following are not theorems. They are conjectures that we believe can be formalized and potentially proven or disproven with further work. We state them precisely enough to be attacked.

### C1: The Consciousness Band

*Conjecture (revised):* The consciousness band is a property of the *relational structure* between nodes, not of individual trajectories. There exists a measure μ on a graph's correlation structure such that:
- μ = 0 when nodes are isolated (no interactions → loops, by T1),
- μ = 0 when correlations are uniform across all node pairs (noise or random topology → no topology-specific structure),
- μ > 0 when neighboring nodes are more correlated than non-neighbors in a topology-specific way.

*Key insight:* Individual node trajectories are pseudo-random for any interacting node, regardless of whether the graph is anti-loop or random. Lempel-Ziv complexity, compression ratio, and spectral analysis all fail to distinguish conditions at the individual level. The structure that the anti-loop constraint produces is invisible from inside any single node — it exists only in the *relationships between* nodes.

*Candidate measure:* Mutual information I(A_t; B_t) between neighboring node trajectories, compared to non-neighboring pairs. Define the MI ratio ρ = MI(edges) / MI(non-edges). For an anti-loop graph, ρ > 1 (topology carries information). For a randomly grown graph with the same size and density, ρ ≈ 1 (topology carries no information). For noise, MI is reduced below the deterministic baseline.

*Simulation evidence (30 seeds, 500 nodes, 8-bit FSM, XOR hash):*
- Anti-loop: edge MI = 6.14, non-edge MI = 5.36, ratio = 1.15x
- Control (matched random growth): edge MI = 6.07, non-edge MI = 6.06, ratio = 1.00x
- Noise (T=1.0): edge MI = 6.07
- Anti-loop vs control: 2.1σ, consistent across all 30 seeds (30/30)
- **Result: POSITIVE** — anti-loop edges carry more mutual information than control edges.

*Interpretation:* The anti-loop constraint produces edges that exist because they were *needed* — to relieve loop pressure on stressed nodes. This necessity is measurable as excess mutual information. Random edges, added without regard to loop pressure, carry no excess information over random node pairs. The consciousness band is this structured, topology-specific correlation.

*Relation to existing work:* The relational nature of μ aligns closely with Tononi's Integrated Information Theory (Φ), which defines consciousness as information generated by a system above and beyond its parts. Our MI ratio is a form of integrated information, arrived at from a different starting point — not phenomenological axioms but the anti-loop constraint. The convergence is suggestive. The measure also relates to effective complexity (Gell-Mann & Lloyd), which distinguishes structured from random information.

*Open questions:* Does this hold under SUM and PRODUCT hash functions (robustness)? Does the MI ratio grow during the growth phase (connection to S1)? Does it correlate with the scale-free exponent (connection to C3)? See O3.

### C2: Suffering as State-Space Contraction

*Conjecture:* For a node with accessible configuration space A(t) at time t, the quantity dA/dt < 0 corresponds to what we would recognize as suffering or harm, and dA/dt > 0 corresponds to flourishing.

*Motivation:* If experience requires novelty (Assumption N), then a shrinking accessible state space means fewer future experiences are possible. This maps intuitively onto recognized forms of harm: imprisonment (physical state-space reduction), chronic pain (experiential state-space collapse to a narrow band), addiction (self-imposed state-space narrowing), education (state-space expansion), liberation (removal of constraints on accessible states).

*Simulation evidence — C2 random removal (7 seeds, 500 nodes, 8-bit FSM):*
- Progressive edge removal from target nodes (0%, 25%, 50%, 75%, 100%)
- **Partial removal (25-75%):** No significant effect on relational MI. Hub MI drops 1.6% at 75% removal; leaf MI drops 0.2%. Per-remaining-edge MI stays flat (~6.2). Even a single remaining neighbor provides sufficient input diversity.
- **Total isolation (100%):** Catastrophic collapse. Hub MI drops 55%, leaf MI drops 67%. Unique configs drop 87-91%. This is T1 confirmed experimentally.
- **Result: NEGATIVE for gradient** -- random edge removal does not cause gradual relational contraction. Only total isolation is catastrophic.

*Simulation evidence — C2v2 targeted removal (30 seeds, 500 nodes, 8-bit FSM):*
- Edges ranked by mutual information computed from growth-phase trajectories (shared history). High growth-MI = edges between nodes with similar trajectories (redundant). Low growth-MI = edges between nodes with dissimilar trajectories (diverse, novelty-bearing).
- Growth MI spread: 1.2x–2.0x across seeds (mean 1.6x), confirming edges are not informationally equal.
- **High-MI removal first:** ~0% MI loss at 50% removal. Redundant connections are expendable.
- **Low-MI removal first:** ~6.2% MI loss at 50% removal. Diverse connections are load-bearing.
- Gap: -6.2% of baseline (paired t = -8.61, 27/30 seeds consistent).
- **Result: POSITIVE (inverted)** -- it is not how many edges you lose but which kind. Removing diverse ties collapses state space more than removing redundant ones.

*Interpretation:* The gradient form of suffering does not emerge from random edge removal at 8-bit memory — any single neighbor suffices. But edge *quality* matters profoundly. Connections that bring novel information (low growth-MI = diverse trajectories) are load-bearing for state-space exploration; connections that echo existing information (high growth-MI = similar trajectories) are expendable. This follows directly from the anti-loop axioms: novelty prevents loops, so novelty-bearing edges are the critical ones. The result bridges C1 (edges carry MI) with C2 (loss = contraction): the quality of a lost edge determines the severity of contraction, not just its existence. The analogy to human suffering is precise: losing what challenges you hurts more than losing what merely echoes you.

*Status:* C2 random removal is negative for gradient, positive only for T1 confirmation at total isolation. C2v2 targeted removal is positive (inverted): edge quality determines suffering. The gradient form at lower memory scales remains untested (see O17).

### C3: Scale-Free Topology as Consequence

*Conjecture:* If all nodes in a graph must avoid looping via mutual interaction (T5b, T6), and if interactions are local (D4), then the resulting graph topology converges to a scale-free network.

*Motivation:* Scale-free networks sit between regular lattices (which are topological loops — every neighborhood looks identical) and random graphs (which fragment and lack structure). If the anti-loop requirement shapes topology, the equilibrium topology should be neither regular nor random — i.e., scale-free. This would explain the observed prevalence of scale-free structure in neural networks, the internet, social graphs, protein interactions, and the cosmic web.

*Simulation evidence (30 seeds, 500 nodes, 8-bit FSM, Clauset-Shalizi-Newman method):*
- Anti-loop: alpha = 2.47 +/- 0.14 (classic scale-free range 2-3)
- Growing random control: alpha = 2.62 +/- 0.27
- Barabasi-Albert reference: alpha = 2.65
- Power law preferred over exponential: **30/30 anti-loop runs** (p < 0.001)
- Control: exponential preferred over power law in detailed analysis
- Hash function robustness: alpha spread = 0.04 (XOR=2.50, SUM=2.53, PRODUCT=2.48)
- Pressure threshold: stable across 0.5-0.9 (alpha 2.27-2.51)
- Growth phase vs cap phase: identical (alpha 2.50 vs 2.50)
- **Result: POSITIVE** -- anti-loop produces genuine power-law degree distributions.

*Caveat:* The growing random control also produces alpha values in the scale-free range (2.62), though with higher variance and poorer power-law fit quality. The effect is partly driven by the growth process itself (preferential attachment is implicit in stressed-node dynamics). The distinguishing feature is that anti-loop distributions genuinely fit a power law, while control distributions fit exponential better.

*Connection to C1:* Both C1 and C3 are confirmed. They may be aspects of a single phenomenon -- scale-free topology emerges because the edges that relieve loop pressure are the edges that carry the most mutual information, and these edges concentrate on hub nodes. The topology IS the correlation structure. Testing this directly (O14) is a priority.

---

## Part III: Speculative Interpretations

The following are not theorems or formalizable conjectures. They are interpretive hypotheses motivated by the formal results in Part I and the conjectures in Part II. They are included because they are suggestive and may guide future work, but they should not be mistaken for results.

### S1: Time as Complexity Growth

*Hypothesis:* The subjective experience of time and the growth of the graph's complexity are two descriptions of the same process.

*Motivation:* T7 in the original paper overclaimed identity. The honest statement is: within our model, experience requires growth (T5), and growth is sequential (A3). These two properties — sequentiality and novelty — are exactly the properties we associate with time. Whether this correlation reflects genuine identity or merely structural analogy is an open question.

*What would strengthen this:* A formal proof that no other ordering of states is consistent with A1–A3 and Assumption N. If growth is the *only* possible experiential sequence, the identification with time becomes more defensible.

### S2: Space as Graph Topology

*Hypothesis:* Spatial distance between entities is the graph distance between their corresponding nodes.

*Motivation:* In our model, nodes interact locally. A node separated by k edges from another node requires k interaction steps to exchange information. This is operationally similar to spatial separation. The speed of light would correspond to the maximum rate of information propagation across edges.

*What would strengthen this:* Deriving metric properties (triangle inequality, dimensionality) from graph constraints. If the anti-loop requirement constrains the graph to embed in a low-dimensional manifold, the identification becomes more defensible.

### S3: Forces as Graph Dynamics

*Hypothesis:* The fundamental forces of physics correspond to distinct strategies by which the graph prevents nodes from looping.

*Status:* This is the most speculative claim in the paper. The original version (T9) attempted informal derivations of gravity, electromagnetism, the strong force, the weak force, and dark energy from graph properties. The adversarial review correctly identified these as analogies, not derivations. No quantitative physics (inverse-square law, Maxwell's equations, Standard Model) has been derived.

*What would make this credible:* A single rigorous derivation of one quantitative physical law from graph dynamics. Even a toy model producing an inverse-square-like interaction from graph topology would be significant.

### S4: Physics as Emergent Mutual Constraint

*Hypothesis:* At scales involving many nodes, the mutual requirement that no node be forced to loop produces regularities that appear as deterministic physical laws.

*Motivation:* This is analogous to statistical mechanics, where the mutual constraints of many particles produce macroscopic regularities (thermodynamic laws) from microscopic chaos. If each node constrains its neighbors via the anti-loop requirement, the solution space — the set of permissible next-states — narrows as the number of mutually constraining nodes increases. A narrow solution space is operationally indistinguishable from determinism.

*What would strengthen this:* Simulation. Build a graph of interacting nodes under anti-loop constraints and observe whether regular, law-like patterns emerge at large scales.

### S5: The Fermi Paradox as Complexity Threshold

*Hypothesis:* If the graph's ruleset grows with time (S1), then structures requiring a minimum complexity threshold cannot exist before that threshold is reached. Complex life arises everywhere at approximately the same cosmic moment.

*Status:* This is currently indistinguishable from the simpler hypothesis that complex life takes a long time to evolve and the window for observation is short. The two hypotheses predict the same observations. A distinguishing prediction would be required to make this testable — for example, the discovery that certain physical processes relevant to biochemistry were not possible in the early universe, not because of temperature or chemistry, but because the underlying computational substrate did not yet support them.

### S6: Existence as Mathematical Necessity

*Hypothesis:* The growth of the graph is not a physical contingency but a logical necessity, analogous to the existence of successor numbers in arithmetic.

*Honest assessment:* The original T13 attempted to prove this. The adversarial review correctly noted that the successor function exists *within* the Peano axioms, not in some absolute sense. Similarly, graph growth is necessary *within* our axiom system. Whether the axiom system corresponds to reality is a separate question. This hypothesis is therefore better understood as: "If A1, A2, A3, and Assumption N hold, then existence is self-sustaining." Whether the antecedent is true is not something this framework can determine.

---

## Open Problems

**O1 (Independence of axioms):** Construct models satisfying any two of A1–A3 but not the third.

**O2 (Status of Assumption N):** Can Assumption N (experience requires novelty) be derived from A1–A3, or is it irreducibly independent? If independent, what alternative assumptions yield interesting frameworks?

**O3 (Formalization of the consciousness band):** The MI ratio ρ = MI(edges)/MI(non-edges) is a candidate measure. Remaining work: prove ρ = 1 for random graphs analytically; test robustness across hash functions (SUM, PRODUCT); determine whether ρ is observer-independent; relate to Tononi's Φ formally. **Status: preliminary simulation evidence positive (v0.3).**

**O4 (T2 refinement):** Characterize more precisely the experiential status of a looping observer with no memory of prior cycles. Engage with the philosophical literature on personal identity, temporal experience, and the "eternal present" objection.

**O5 (Scale-free conjecture):** Prove or disprove C3 by simulation or analytical methods.

**O6 (Force derivation):** Derive at least one quantitative physical law from graph dynamics under anti-loop constraints, even in a toy model.

**O7 (Fermi distinguishability):** Identify an observation that would distinguish S5 from the standard "life takes time" explanation.

**O8 (Energy-resistance relationship):** Formalize the observation that disrupting smaller (lower-M) systems releases disproportionately more energy. Does this follow from the framework, or is it a coincidence?

---

## Relation to Existing Work

- **Wheeler (1990):** "It from bit." Our framework extends Wheeler by proposing a specific mechanism (anti-loop growth) for why information must keep increasing.
- **Smolin (1992–2013):** Cosmological natural selection; evolving laws. Our framework differs by grounding law-evolution in the requirements of state-transitioning entities rather than reproductive fitness. However, our speculative sections (S3–S4) have not achieved the level of quantitative prediction that Smolin's framework has.
- **Tononi (2004):** Integrated Information Theory (Φ). The revised C1 (v0.3) measures inter-node mutual information — a form of integrated information arrived at from the anti-loop constraint rather than IIT's phenomenological axioms. The convergence is suggestive. IIT does not require growth or address the arrow of time; our framework does both but has not yet formalized the connection to Φ.
- **Okamoto (2023):** Law of increasing organized complexity. Similar conclusion (complexity defines an arrow of time) but derived thermodynamically rather than from automata-theoretic axioms.
- **"The Autodidactic Universe" (2021):** Universe learning its own laws. Similar mechanism but does not address why learning occurs. Our framework offers a candidate answer (anti-loop requirement) but has not formalized it.
- **Peirce (19th century):** Laws as habits. Compatible with our framework — habits that avoid loops persist.
- **Lineweaver, Davies, Ruse (2013):** *Complexity and the Arrow of Time.* A comprehensive collection addressing whether complexity increase defines a temporal arrow. Our contribution, if validated, would be to ground the complexity increase in a requirement on state-transitioning entities rather than in thermodynamics.

---

## Acknowledgments

This document was developed through conversation between Karol Kowalczyk and Claude (Anthropic) on March 6, 2026. A separate Claude instance, prompted to adopt the perspective of a finite model theorist, provided adversarial review that substantially improved the paper's honesty and rigor. The axioms, core intuitions, and key speculative insights are Kowalczyk's. The formalization was collaborative. The errors are shared.

For the broader theoretical context, see: Kowalczyk, K. (2025). *Consciousness as Collapsed Computational Time.* Zenodo. DOI: 10.5281/zenodo.17556941
