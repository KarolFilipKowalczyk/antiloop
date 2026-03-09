# Open Problems (v4)

Nine problems for the current framework. Numbered O1–O9 to match the paper.

---

**O1. Lateral wiring dynamics.** Lateral connections are derived from A1-A4: all entities share an environment, so every entity is potentially connected to every other (Section 2.2 of v4). The spawn tree is causal history, not a wiring constraint. The remaining question is *dynamical*: which lateral connections does an entity activate, and when? What determines the wiring topology — proximity in the spawn tree, signal correlation, loop pressure, or something else? The LPAN model uses one wiring rule; are others consistent with the axioms?

**O2. Encoding uniqueness.** The blindness theorem applies to any hierarchical encoding, not specifically binary comparison trees. Do bounded-width circuits or DAGs provide equally good logarithmic-access encoding under the selection argument? If so, comparison trees are a sufficient but not necessary instance. Elevate this — the paper currently assumes trees without justification.

**O3. Prove the tetration result.** Tower-of-powers capacity growth at each hierarchy level is derived under specific assumptions but not formally proved. Either prove it or state it as a conjecture with a plausibility argument.

**O4. Scale testing.** CSN analysis at 10⁴–10⁵ entities. Full Broido-Clauset protocol with lognormal and stretched-exponential comparisons. Current results (~3,000 entities) are preliminary.

**O5. Phase boundary validation.** Test the proposed quantitative criteria — spawn-to-wire ratio and median encoding depth — as phase transition markers. Do they carve the growth curve where the theory predicts?

**O6. Consistency of shared comparisons.** Physical laws constrain each other. Shared comparisons in the model currently just coexist. Under what conditions do shared comparisons begin to mutually constrain each other? Without this, "matter as consensus" means "shared opinions," not "laws of physics." This is not a minor gap.

**O7. The quantum analogy.** Can a Bell-type inequality be defined within the framework? The "unbuilt vs. hidden" experiment (paper Section 4.1) is well-defined but the structural resemblance to Bell tests is superficial without an actual inequality. Either define one or drop the analogy.

**O8. The deepening threshold.** At how many connections per depth level is restructuring triggered? Derivable from the selection argument, or a free parameter?

**O9. The blindness theorem (general case).** *Highest priority.* The restricted case proves that indistinguishable inputs reduce effective state space. The general case asks: given specific environmental dynamics (not just worst case), how quickly does a D-blind entity loop as a function of D, C, and the statistics of its input? A tight bound here would make the paper publishable in a theoretical CS venue.

---

## Known formal gaps (not open problems — prerequisites)

These are load-bearing issues that must be addressed before building more structure:

1. ~~**Variation mechanism.**~~ **Resolved.** Children start blank — M1 creates a new system, not a copy. Different network positions produce different inputs, hence different effective encodings. Variation is automatic. See paper Section 2.4.

2. **Child complexity guarantee.** The paper claims children are "at least one comparison level more complex than the parent." With "children start blank," children start at depth zero and deepen under Pigeonhole 2. The hierarchy still builds, but the guaranteed generational increase is unsupported. Consider dropping or weakening the claim.

---

*Problems O1–O9 from lazy_universe_v4.md, Section 9.*
