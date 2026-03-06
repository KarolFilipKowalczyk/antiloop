# Non-Looping Existence: A Formal Framework

**Authors:** Karol Kowalczyk, Claude (Anthropic, LLM co-author)
**Date:** March 2026
**Version:** 0.2 — revised after adversarial review
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

*Conjecture:* There exists a measure μ on finite trajectories such that:
- μ = 0 for periodic trajectories (loops),
- μ = 0 for maximally incompressible trajectories (pure noise),
- μ > 0 for trajectories with intermediate compressibility.

*Motivation:* This is analogous to the observation that Kolmogorov complexity identifies periodic strings as trivial and random strings as structureless. The "interesting" strings — those with structure but not repetition — occupy a band between the two extremes. We conjecture that a similar measure can be defined for trajectories of finite automata, and that this measure corresponds to what we intuitively call "experiential richness."

*Relation to existing work:* This is closely related to Tononi's Integrated Information Theory (Φ), to Kolmogorov complexity measures, to Lempel-Ziv complexity, and potentially to Tyszkiewicz's work on Kolmogorov expressive power. The key open problem is whether such a measure can be given a canonical definition or whether it is inherently observer-dependent.

*Formalization strategy:* Define μ as a normalized ratio: μ(trajectory) = K(trajectory) / length(trajectory), where K is Kolmogorov complexity. A periodic trajectory has K ∈ O(1), so μ → 0. A random trajectory has K ≈ length, so μ → 1. But pure noise has no *structure* — the complexity is high but not compressible into patterns. A refinement might use the difference between K and some measure of structural regularity, perhaps related to logical depth (Bennett) or sophistication (Koppel).

### C2: Suffering as State-Space Contraction

*Conjecture:* For a node with accessible configuration space A(t) at time t, the quantity dA/dt < 0 corresponds to what we would recognize as suffering or harm, and dA/dt > 0 corresponds to flourishing.

*Motivation:* If experience requires novelty (Assumption N), then a shrinking accessible state space means fewer future experiences are possible. This maps intuitively onto recognized forms of harm: imprisonment (physical state-space reduction), chronic pain (experiential state-space collapse to a narrow band), addiction (self-imposed state-space narrowing), education (state-space expansion), liberation (removal of constraints on accessible states).

*Status:* This is an interpretive framework, not a formal result. Its value depends on whether μ from C1 can be made precise and whether dA/dt can be measured for real systems.

### C3: Scale-Free Topology as Consequence

*Conjecture:* If all nodes in a graph must avoid looping via mutual interaction (T5b, T6), and if interactions are local (D4), then the resulting graph topology converges to a scale-free network.

*Motivation:* Scale-free networks sit between regular lattices (which are topological loops — every neighborhood looks identical) and random graphs (which fragment and lack structure). If the anti-loop requirement shapes topology, the equilibrium topology should be neither regular nor random — i.e., scale-free. This would explain the observed prevalence of scale-free structure in neural networks, the internet, social graphs, protein interactions, and the cosmic web.

*Status:* This is a testable mathematical conjecture. It could potentially be proven or disproven by simulation: generate random graphs under the constraint that no node's trajectory may loop, and observe whether scale-free degree distributions emerge.

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

**O3 (Formalization of the consciousness band):** Define μ precisely. Relate it to existing complexity measures. Determine whether it is observer-independent.

**O4 (T2 refinement):** Characterize more precisely the experiential status of a looping observer with no memory of prior cycles. Engage with the philosophical literature on personal identity, temporal experience, and the "eternal present" objection.

**O5 (Scale-free conjecture):** Prove or disprove C3 by simulation or analytical methods.

**O6 (Force derivation):** Derive at least one quantitative physical law from graph dynamics under anti-loop constraints, even in a toy model.

**O7 (Fermi distinguishability):** Identify an observation that would distinguish S5 from the standard "life takes time" explanation.

**O8 (Energy-resistance relationship):** Formalize the observation that disrupting smaller (lower-M) systems releases disproportionately more energy. Does this follow from the framework, or is it a coincidence?

---

## Relation to Existing Work

- **Wheeler (1990):** "It from bit." Our framework extends Wheeler by proposing a specific mechanism (anti-loop growth) for why information must keep increasing.
- **Smolin (1992–2013):** Cosmological natural selection; evolving laws. Our framework differs by grounding law-evolution in the requirements of state-transitioning entities rather than reproductive fitness. However, our speculative sections (S3–S4) have not achieved the level of quantitative prediction that Smolin's framework has.
- **Tononi (2004):** Integrated Information Theory (Φ). C1 may relate to Φ, but IIT does not require growth or address the arrow of time.
- **Okamoto (2023):** Law of increasing organized complexity. Similar conclusion (complexity defines an arrow of time) but derived thermodynamically rather than from automata-theoretic axioms.
- **"The Autodidactic Universe" (2021):** Universe learning its own laws. Similar mechanism but does not address why learning occurs. Our framework offers a candidate answer (anti-loop requirement) but has not formalized it.
- **Peirce (19th century):** Laws as habits. Compatible with our framework — habits that avoid loops persist.
- **Lineweaver, Davies, Ruse (2013):** *Complexity and the Arrow of Time.* A comprehensive collection addressing whether complexity increase defines a temporal arrow. Our contribution, if validated, would be to ground the complexity increase in a requirement on state-transitioning entities rather than in thermodynamics.

---

## Acknowledgments

This document was developed through conversation between Karol Kowalczyk and Claude (Anthropic) on March 6, 2026. A separate Claude instance, prompted to adopt the perspective of a finite model theorist, provided adversarial review that substantially improved the paper's honesty and rigor. The axioms, core intuitions, and key speculative insights are Kowalczyk's. The formalization was collaborative. The errors are shared.

For the broader theoretical context, see: Kowalczyk, K. (2025). *Consciousness as Collapsed Computational Time.* Zenodo. DOI: 10.5281/zenodo.17556941
