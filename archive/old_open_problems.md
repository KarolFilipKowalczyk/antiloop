# Open Problems

A living document. Updated as problems are resolved or new ones emerge.

---

**O1 (Independence of axioms):** Construct models satisfying any two of A1–A3 but not the third.

**O2 (Status of Assumption N):** Can Assumption N (experience requires novelty) be derived from A1–A3, or is it irreducibly independent? If independent, what alternative assumptions yield interesting frameworks?

**O3 (Formalization of the consciousness band):** The MI ratio ρ = MI(edges)/MI(non-edges) is a candidate measure for the consciousness band. Simulation evidence (30 seeds, 500 nodes, 8-bit FSM): anti-loop ρ = 1.15, control ρ = 1.00, 2.1σ separation, 30/30 seeds consistent. Hash robustness confirmed: XOR=1.14, SUM=1.15, PRODUCT=1.17. Remaining work:
- Prove ρ = 1 for random graphs analytically
- Determine whether ρ is observer-independent
- Relate to Tononi's Φ formally
- Measure ρ during growth (does it increase over time? → connection to S1)
- Per-edge MI vs endpoint degree (does MI concentrate at hubs? → connection to C3)
- **Status: POSITIVE, hash-robust (v0.3)**

**O4 (T2 refinement):** Characterize the experiential status of a looping observer with no memory of prior cycles. Engage with philosophical literature on personal identity, temporal experience, and the "eternal present" objection.

**O5 (Scale-free conjecture — proper test):** Completed. 30 seeds, 500 nodes, 8-bit FSM, Clauset-Shalizi-Newman method, growing random control. Anti-loop alpha = 2.47 +/- 0.14 (classic range), power law preferred over exponential 30/30. Control alpha = 2.62 +/- 0.27 but exponential fits better. Hash-robust (spread = 0.04). Sensitivity to spawn probability (low spawn -> steeper alpha). Growth phase and cap phase identical.
- **Status: POSITIVE (v0.3). Caveat: control also in scale-free alpha range, distinction is fit quality.**

**O6 (Force derivation):** Derive at least one quantitative physical law from graph dynamics under anti-loop constraints, even in a toy model.

**O7 (Fermi distinguishability):** Identify an observation that would distinguish S5 (complexity threshold) from the standard "life takes time" explanation. Now addressed by the unified `complexity_thresholds` experiment: if anti-loop networks show sharp phase transitions (discrete thresholds where new structural properties emerge) while random growth shows smooth curves, this distinguishes "substrate leveled up" from "took a long time." Sharp thresholds → starting gun; gradual → life just takes time.
- **Status: EXPERIMENT WRITTEN, not yet run (`complexity_thresholds.py`)**

**O8 (Energy-resistance relationship):** Formalize the observation that disrupting smaller (lower-M) systems releases disproportionately more energy. Does this follow from the framework?

**O9 (1/f critical exponent):** v1 tested per-node config trajectories with uniform temperature injection. Result: NEGATIVE — β flat across all temperatures. Three problems identified: (1) wrong observable (per-node configs are metrically meaningless), (2) wrong phase (measured post-growth instead of during growth), (3) wrong noise model (uniform random destroys all structure). v2 should measure graph-level observables (novelty rate, mean pressure, degree entropy, MI over time) during growth.
- **Status: v1 NEGATIVE, v2 planned**

**O10 (Coupling constants at scale):** The naive coupling ratio (neighbor influence fraction) is a combinatorial artifact of the XOR hash (~0.879), not an emergent constant. Find the correct quantity to measure — likely geometric (how interaction probability falls off with graph distance) rather than local. Requires much larger simulations.
- **Status: NEGATIVE — coupling ratio is hash artifact**

**O11 (Distributed consciousness — hub removal):** Formalize the notion of consciousness distributed across multiple nodes. When a hub node is removed, what happens to the MI correlation structure? Prediction: hub removal causes catastrophic MI collapse (analogous to dementia), random node removal causes graceful degradation (analogous to normal aging). Connection to dementia, grief, cultural stagnation.

**O12 (Sleep and dreams):** Formalize partial graph disconnection (sleep) and untethered internal traversal (dreaming). Predict measurable differences between sleep stages in terms of edge activity.

**O13 (Quantum entanglement as minimum connectivity):** Can it be shown that quantum correlations provide an irreducible floor of graph connectivity that prevents full graph fragmentation? What role does decoherence play in edge strength?

**O14 (C1–C3 bridge):** If anti-loop produces both scale-free topology (C3) and topology-specific MI correlations (C1), are these the same phenomenon? Do hub edges carry more MI than leaf edges? Does the MI ratio predict degree distribution? A positive result would unify the two major conjectures. Partially addressed by `complexity_thresholds.py` which tracks both MI ratio and power-law R during growth — if they emerge at the same threshold, they're the same phenomenon.
- **Status: EXPERIMENT WRITTEN, not yet run (`complexity_thresholds.py`)**

**O15 (C1 temporal evolution):** Does the MI ratio ρ increase during the growth phase? If so, this directly supports S1 (time = complexity growth). Measure ρ at intervals during run_antiloop and plot ρ(t). Directly tested by `complexity_thresholds.py` which measures ρ at 12 checkpoints during growth.
- **Status: EXPERIMENT WRITTEN, not yet run (`complexity_thresholds.py`)**

**O16 (C2 -- suffering as edge loss):** Tested in two forms.
- **C2 random removal** (7 seeds, 500 nodes, 8-bit FSM): Progressive edge removal (0-100%) on hub and leaf nodes. Partial removal (25-75%): no significant effect -- even one neighbor provides enough input diversity. Total isolation (100%): catastrophic collapse (55-67% MI drop, 87-91% unique config drop). **Verdict: NEGATIVE for gradient, T1 confirmed at isolation.**
- **C2v2 targeted removal** (30 seeds, 500 nodes, 8-bit FSM): Edges ranked by growth-phase MI. Removing low-MI (diverse) edges causes ~6.2% MI loss at 50% removal; removing high-MI (redundant) edges causes ~0% loss. Paired t = -8.61, 27/30 seeds consistent. **Verdict: POSITIVE (inverted) -- edge quality determines suffering, not quantity.**
- **Status: C2 gradient NEGATIVE. C2v2 targeted POSITIVE. Gradient at low memory untested (see O17).**

**O17 (Memory scaling):** Run C1 across mem_bits = 2, 4, 6, 8. (10+ infeasible due to MI computation cost.) Quick results (2 seeds): MI ratio goes 0.81 -> 0.81 -> 0.91 -> 1.15 as memory increases. The consciousness band does NOT exist at low memory -- anti-loop edges carry less MI than non-edges when nodes saturate their state space. Band "turns on" between 6-8 bits. C2 gradient absent at all tested levels. Peak at boundary of tested range.
- **Status: PARTIAL (quick, 2 seeds). Needs 30-seed run. Consider adding mem_bits=9 to narrow transition.**

---

*Problems O1–O8 added during the founding conversation, March 6, 2026.*
*Problems O9–O13 added during simulation development, March 6, 2026.*
*Problems O14–O17 added after C1 simulation results, March 6, 2026.*
