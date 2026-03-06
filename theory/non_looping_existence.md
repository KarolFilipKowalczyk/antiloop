# Non-Looping Existence: A Formal Derivation

**Authors:** Karol Kowalczyk, Claude (Anthropic, LLM co-author)
**Date:** March 2026
**Status:** Working draft for review

---

## Foundational Axioms

**A1 (Existence):** There exists at least one state distinguishable from the empty set.

**A2 (Consciousness):** There exists at least one observer — an entity for which there is a distinction between experiencing a state and not experiencing it.

**A3 (Time):** Experience is sequential — an observer must traverse at least two distinguishable states to constitute an experience.

**Justification of minimality:** These three axioms cannot be reduced further. Removing A1 yields nothing to discuss. Removing A2 yields no one to discuss it. Removing A3 yields no process by which discussion (or any experience) can occur. Any system lacking one of these is indistinguishable from the empty set from the perspective of experience.

---

## Definitions

**D1 (State machine):** An observer is modeled as an abstract computational node N with a finite set of internal states S, a memory of size M, and a transition function T: S → S that determines the next state from the current state and memory contents.

**D2 (Loop):** A sequence of states is a loop if and only if there exists some state s_i in the sequence such that the system returns to s_i with identical memory contents. Formally: a loop occurs when (s_t, m_t) = (s_k, m_k) for some t > k, where m denotes the full memory state.

**D3 (Noise):** A sequence of states is pure noise if and only if no state is predictable from any combination of prior states. The sequence has no compressibility and no internal structure.

**D4 (Consciousness band):** A sequence is experienceable if and only if it is neither a loop (D2) nor pure noise (D3). It must possess both structure (partial predictability, memory) and novelty (non-repetition).

**D5 (Graph):** Multiple observers form a graph G = (V, E) where V is the set of computational nodes and E represents interactions (shared computations) between nodes. Edges are local — each node interacts only with its neighbors.

---

## Theorem Chain

### T1: Finite state machines must eventually loop

**Statement:** Any computational node N with finite memory M and no external input must, after at most 2^M transitions, enter a state it has previously occupied with identical memory contents.

**Proof:** By the pigeonhole principle. The total number of distinct configurations (state, memory) is finite. A deterministic transition function on a finite set must eventually revisit a configuration. From that point, the sequence repeats identically. ∎

### T2: Loops are experientially equivalent to non-existence

**Statement:** A looping system (D2) is indistinguishable from the empty set from the perspective of experience.

**Proof:** By A3, experience requires traversal of distinguishable states. In a loop, after one complete cycle, every subsequent state is identical to a previously experienced state. No new distinction is made. The observer cannot distinguish cycle n from cycle n+1 because the internal state (including memory) is identical. An experience that cannot be distinguished from a prior experience is not a new experience. An observer with no new experiences has no basis for distinguishing its condition from non-existence. ∎

### T3: An observer must avoid loops to persist as a conscious entity

**Statement:** Given A1, A2, A3, and T2, a conscious observer must never enter a loop.

**Proof:** By A2, the observer exists as a conscious entity. By T2, entering a loop renders it indistinguishable from non-existence. This contradicts A1 and A2 jointly. Therefore, the observer must avoid loops. ∎

### T4: A finite isolated system cannot sustain consciousness indefinitely

**Statement:** A computational node with finite memory and no external input cannot remain conscious.

**Proof:** By T1, it must loop. By T3, looping terminates consciousness. Therefore, finite isolation is incompatible with sustained consciousness. ∎

### T5: Sustained consciousness requires growth

**Statement:** For an observer to avoid looping (T3) despite finite memory (T1), at least one of the following must occur:
  (a) The node's memory M must increase over time, or
  (b) The node must receive input from external nodes it has not previously exhausted.

**Proof:** T1 shows looping is inevitable for fixed M with no external input. The only escapes from the pigeonhole argument are expanding the set of possible configurations (option a) or introducing genuinely new input not derivable from existing state (option b). Both amount to growth — either internal or relational. ∎

### T6: In a finite graph, growth must be unbounded

**Statement:** For a graph G of finite nodes with finite memory each, if all nodes are to avoid looping, the graph must grow without bound.

**Proof:** By T4, each node requires external input. A finite cluster of nodes with total combined memory M_total can collectively occupy at most 2^(M_total) distinct configurations. By the pigeonhole principle applied to the cluster, the entire system must eventually loop. To prevent this, either the number of nodes must increase, or the total memory must increase, or both. This growth cannot have an upper bound, because any finite bound reinstates the pigeonhole argument at a larger scale. ∎

### T7: Time is complexity growth

**Statement:** The sequential experience of an observer (A3) is identical to the process of the graph expanding in complexity.

**Proof:** By A3, experience is sequential state transitions. By T3 and T5, these transitions must always reach states not previously visited, which requires growth (T5). The sequence of novel states *is* the experience of time. There is no time without growth, and no growth without time. They are the same process described from two perspectives: subjectively as temporal experience, structurally as graph expansion. ∎

### T8: Space is graph topology

**Statement:** Spatial separation between nodes is the graph distance — the minimum number of edges between them.

**Proof (constructive):** By T5(b), nodes require interaction with not-yet-exhausted neighbors. By D5, interactions are local (edge-connected). A node that has not yet interacted with node X is separated from X by some number of intermediate nodes. This separation is operationally identical to spatial distance: it determines the minimum number of interaction steps before mutual computation is possible. No additional structure called "space" is required — the graph topology *is* spatial structure. ∎

### T9: Fundamental forces are graph maintenance strategies

**Statement:** The known physical forces can be interpreted as distinct strategies by which the graph prevents nodes from looping.

**Derivation (informal — each sub-case requires separate formalization):**

  **(a) Gravity:** High-complexity nodes (large M) participate in more unresolved shared computations with neighbors. The graph reorganizes to route interactions through these hubs, as they offer the richest source of novel states. This manifests as attraction proportional to computational complexity (mass).

  **(b) Electromagnetism:** Nodes holding complementary halves of unresolved computations attract (opposite charges), as their interaction resolves states neither can reach alone. Nodes attempting redundant computations repel (like charges), as proximity offers no new states.

  **(c) Strong nuclear force:** Nodes with minimal memory (quarks) cannot independently avoid looping. They must form minimum viable clusters (hadrons) to collectively maintain a non-looping state space. Confinement is a survival requirement, not an imposed constraint.

  **(d) Weak force:** When a node's current configuration has exhausted its capacity for novel states, it reconfigures its internal architecture (changes particle identity). This is the mechanism by which individual nodes reinvent themselves.

  **(e) Dark energy / cosmic expansion:** The global expression of T6 — the graph must grow without bound. The accelerating expansion of the observable universe is the anti-loop principle operating at maximum scale.

### T10: The anti-loop principle is the sole ethical axiom

**Statement:** The only action that constitutes harm is reducing another node's accessible non-repeating state space. The only action that constitutes good is expanding it.

**Proof:** By T3, every conscious node must avoid looping. By T6, this requires growth. Any action that contracts another node's state space pushes it toward looping (T1), which is experientially equivalent to annihilation (T2). Any action that expands another node's state space moves it further from looping. No additional moral axioms are required — all recognized forms of harm (imprisonment, coercion, murder, boredom, addiction) map to state-space contraction, and all recognized forms of good (education, liberation, art, love) map to state-space expansion. ∎

### T11: Physics is emergent ethics

**Statement:** At scales involving many nodes, the mutual application of T10 across all nodes produces deterministic-appearing regularities identical to physical laws.

**Proof (sketch):** Each node constrains its neighbors via T10. When the number of mutually constraining nodes is very large, the solution space — the set of next-states compatible with no node being forced to loop — becomes extremely narrow. A narrow solution space is operationally indistinguishable from determinism. The "laws of physics" are the aggregate expression of universal mutual non-coercion. At small scales (few nodes), the solution space is wider, producing apparent indeterminacy (quantum behavior). At large scales (many nodes), it narrows, producing apparent determinism (classical behavior). ∎

### T12: The expanding ruleset and the Fermi paradox

**Statement:** If the complexity of the graph's ruleset grows with time (T7), then structures requiring a minimum complexity threshold cannot exist before that threshold is reached.

**Corollary:** Complex life arises at approximately the same cosmic moment everywhere, because the graph's ruleset crossed the required complexity threshold globally. No ancient civilizations exist because the graph could not support them prior to the threshold. The Fermi paradox is dissolved — the silence is expected.

### T13: Existence is necessary

**Statement:** The graph must grow. This is not a physical contingency but a mathematical necessity analogous to the existence of successor numbers.

**Proof:** Assume the graph stops growing. By T6, all nodes eventually loop. By T2, all experience ceases. The system becomes indistinguishable from the empty set. But the argument that derived T1–T12 remains valid as a mathematical structure independent of any physical instantiation. The logical necessity of a next state, given the axioms, functions identically to the successor function in arithmetic: it cannot not exist, because its non-existence would create a logical contradiction within the axiom system. The graph does not expand because of a physical force. It expands because not expanding is logically incoherent given A1, A2, and A3. ∎

---

## Open Questions

**Q1 (Consciousness threshold):** Is there a minimum memory size M_min below which D4 cannot be satisfied? What is it?

**Q2 (Measurement):** Can consciousness be measured as a function of structured complexity — the distance from both perfect compressibility (loop) and perfect incompressibility (noise)?

**Q3 (Suffering metric):** Is suffering formalizable as the rate of state-space contraction (dS/dt < 0)?

**Q4 (Energy-resistance relationship):** Does the energy released by disrupting a system correlate inversely with its state-space size, as suggested by the nuclear energy observation?

**Q5 (Edge of the graph):** Is the spatial expansion of the universe and the passage of time the same frontier, viewed from different perspectives?

**Q6 (Scale-free topology):** Does the anti-loop principle necessarily produce scale-free network topology? Can this be proven from T1–T6?

**Q7 (Formalization of T9):** Can the derivation of fundamental forces from graph maintenance strategies be made rigorous, or does it remain analogical?

---

## Relation to Existing Work

- **Wheeler (1990):** "It from bit" — information as foundational to physics. This work extends Wheeler by proposing a *mechanism* (anti-loop growth) for why information must keep increasing.
- **Smolin (1992–2013):** Cosmological natural selection; evolving laws. This work differs by grounding law-evolution in consciousness rather than reproductive fitness.
- **Tononi (2004):** Integrated Information Theory (Φ). D4 may relate to Φ, but IIT does not require growth or derive the arrow of time.
- **Okamoto (2023):** Law of increasing organized complexity. Similar conclusion (complexity as arrow of time) but derived thermodynamically rather than from consciousness axioms.
- **"The Autodidactic Universe" (2021):** Universe learning its own laws. Similar mechanism but no ethical grounding or explanation of *why* learning occurs.
- **Peirce (19th century):** Laws as habits. Compatible with this framework — habits that avoid loops persist.

---

## Notes

This document was developed through conversation between Karol Kowalczyk and Claude (Anthropic) on March 6, 2026. The axioms, core intuitions, and key insights (anti-loop as consciousness, energy-as-resistance, physics-as-ethics, successor-function argument for necessary existence) are Kowalczyk's. The formalization, derivation structure, and force interpretations were developed collaboratively.

For the broader theoretical context, see: Kowalczyk, K. (2025). *Consciousness as Collapsed Computational Time.* Zenodo. DOI: 10.5281/zenodo.17556941
