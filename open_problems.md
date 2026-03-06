# Open Problems

A living document. Updated as problems are resolved or new ones emerge.

---

**O1 (Independence of axioms):** Construct models satisfying any two of A1–A3 but not the third.

**O2 (Status of Assumption N):** Can Assumption N (experience requires novelty) be derived from A1–A3, or is it irreducibly independent? If independent, what alternative assumptions yield interesting frameworks?

**O3 (Formalization of the consciousness band):** The MI ratio ρ = MI(edges)/MI(non-edges) is a candidate measure for the consciousness band. Simulation evidence (30 seeds, 500 nodes, 8-bit FSM): anti-loop ρ = 1.15, control ρ = 1.00, 2.1σ separation, 30/30 seeds consistent. Remaining work:
- Prove ρ = 1 for random graphs analytically
- Test robustness across hash functions (SUM, PRODUCT) — XOR is commutative and self-inverse, results may be hash-dependent
- Determine whether ρ is observer-independent
- Relate to Tononi's Φ formally
- Measure ρ during growth (does it increase over time? → connection to S1)
- Per-edge MI vs endpoint degree (does MI concentrate at hubs? → connection to C3)
- **Status: preliminary simulation evidence POSITIVE (v0.3)**

**O4 (T2 refinement):** Characterize the experiential status of a looping observer with no memory of prior cycles. Engage with philosophical literature on personal identity, temporal experience, and the "eternal present" objection.

**O5 (Scale-free conjecture — proper test):**
- Replace Erdős–Rényi control with growing random graph (matched growth rate, no anti-loop dynamics)
- Apply Clauset–Shalizi–Newman method for power-law testing
- Run 30+ seeds per condition for confidence intervals
- Sensitivity analysis across: loop pressure threshold, spawn probability, hash function, initial topology
- Separate growth phase from edge-only-at-cap phase
- **Status: preliminary evidence positive, proper test pending. Growing random control now implemented in engine.py.**

**O6 (Force derivation):** Derive at least one quantitative physical law from graph dynamics under anti-loop constraints, even in a toy model.

**O7 (Fermi distinguishability):** Identify an observation that would distinguish S5 (complexity threshold) from the standard "life takes time" explanation.

**O8 (Energy-resistance relationship):** Formalize the observation that disrupting smaller (lower-M) systems releases disproportionately more energy. Does this follow from the framework?

**O9 (1/f critical exponent):** v1 tested per-node config trajectories with uniform temperature injection. Result: NEGATIVE — β flat across all temperatures. Three problems identified: (1) wrong observable (per-node configs are metrically meaningless), (2) wrong phase (measured post-growth instead of during growth), (3) wrong noise model (uniform random destroys all structure). v2 should measure graph-level observables (novelty rate, mean pressure, degree entropy, MI over time) during growth.
- **Status: v1 NEGATIVE, v2 planned**

**O10 (Coupling constants at scale):** The naive coupling ratio (neighbor influence fraction) is a combinatorial artifact of the XOR hash (~0.879), not an emergent constant. Find the correct quantity to measure — likely geometric (how interaction probability falls off with graph distance) rather than local. Requires much larger simulations.
- **Status: NEGATIVE — coupling ratio is hash artifact**

**O11 (Distributed consciousness — hub removal):** Formalize the notion of consciousness distributed across multiple nodes. When a hub node is removed, what happens to the MI correlation structure? Prediction: hub removal causes catastrophic MI collapse (analogous to dementia), random node removal causes graceful degradation (analogous to normal aging). Connection to dementia, grief, cultural stagnation.

**O12 (Sleep and dreams):** Formalize partial graph disconnection (sleep) and untethered internal traversal (dreaming). Predict measurable differences between sleep stages in terms of edge activity.

**O13 (Quantum entanglement as minimum connectivity):** Can it be shown that quantum correlations provide an irreducible floor of graph connectivity that prevents full graph fragmentation? What role does decoherence play in edge strength?

**O14 (C1–C3 bridge):** If anti-loop produces both scale-free topology (C3) and topology-specific MI correlations (C1), are these the same phenomenon? Do hub edges carry more MI than leaf edges? Does the MI ratio predict degree distribution? A positive result would unify the two major conjectures.

**O15 (C1 temporal evolution):** Does the MI ratio ρ increase during the growth phase? If so, this directly supports S1 (time = complexity growth). Measure ρ at intervals during run_antiloop and plot ρ(t).

**O16 (C2 — suffering as edge loss):** Systematically remove edges from a node. Does MI with remaining neighbors drop? Does loop pressure rise? Does this map onto C2 (suffering = state-space contraction)?

**O17 (Memory scaling):** Run C1 across mem_bits = 2, 4, 6, 8, 10, 12. At 2 bits, nodes loop in 4 steps (no band possible). At 12 bits, nodes almost never loop (no pressure). The consciousness band should be widest at some intermediate memory size.

---

*Problems O1–O8 added during the founding conversation, March 6, 2026.*
*Problems O9–O13 added during simulation development, March 6, 2026.*
*Problems O14–O17 added after C1 simulation results, March 6, 2026.*
