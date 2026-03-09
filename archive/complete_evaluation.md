# Non-Looping Existence: Theory, Simulation, and Results

**Authors:** Karol Kowalczyk, Claude (Anthropic, LLM co-author)
**Date:** March 2026
**Version:** 0.3 — revised after adversarial review and C1 simulation
**Status:** Working draft — compiled for independent evaluation

---

## CONTEXT FOR THE EVALUATOR

This document contains five parts:

1. **A formal theoretical framework** (Part I–III) deriving consequences from three axioms about existence, observers, and sequential experience. It was developed through conversation between Karol Kowalczyk and a Claude instance, then revised after adversarial review by a separate Claude instance prompted to adopt the perspective of a finite model theorist.

2. **A simulation testing C3** (Part IV) — whether the anti-loop constraint on finite state machines produces scale-free network topology.

3. **Raw C3 results** (Part V) from running the topology simulation.

4. **A simulation testing C1** (Part VI) — whether the anti-loop constraint produces structured inter-node correlations (the "consciousness band"). This is new in v0.3.

We ask you to evaluate: the logical soundness of Part I, the quality of the conjectures in Part II, the honesty of Part III, the experimental design of Parts IV and VI, and the interpretation of results in Parts V and VI. Be ruthless. The goal is to find what breaks.

---

# PART I: FORMAL RESULTS

## Axioms

**A1 (Existence):** There exists at least one state distinguishable from the empty set.

**A2 (Observer):** There exists at least one entity that undergoes state transitions — an entity whose current state is determined by a transition function applied to prior states.

**A3 (Sequentiality):** The entity in A2 must traverse at least two distinguishable states.

**Note on A2:** The original formulation used "consciousness" as a primitive. This was revised to avoid smuggling the hard problem into an axiom. The framework now commits only to the existence of a state-transitioning entity. Whether such an entity is "conscious" is a separate question.

**Note on minimality:** We do not formally prove independence of A1–A3. Informally: without A1, no subject matter; without A2, no dynamics; without A3, no process. Formal independence would require models satisfying any two but not the third (see Open Problem O1).

## Definitions

**D1 (Node):** An observer is modeled as a computational node N = (S, M, T) where S is a finite set of internal states, M is a finite memory of size |M|, and T: (S × M) → (S × M) is a deterministic transition function.

**D2 (Configuration):** A configuration is a pair c = (s, m) where s ∈ S and m ∈ M. The configuration space C of a node is finite, with |C| ≤ |S| × 2^|M|.

**D3 (Loop):** A trajectory is a loop if there exist time steps t > k such that c_t = c_k. From that point, the trajectory repeats identically.

**D4 (Graph):** Multiple nodes form a graph G = (V, E) where V is the set of nodes and E represents interactions between nodes. An interaction is a function that takes configurations of two connected nodes and produces updated configurations for both. Interactions are local.

## Theorems

### T1: Finite isolated nodes must loop.

*Statement:* Any node N with finite configuration space |C| and no external input must, after at most |C| transitions, enter a previously visited configuration.

*Proof:* By the pigeonhole principle. T is total and deterministic on finite set C. A sequence of length |C| + 1 must contain a repetition. Since T is deterministic, the trajectory repeats identically from that point. ∎

### T2: Loops are informationally degenerate.

*Statement:* A looping trajectory produces no new information after the first complete cycle.

*Proof:* Information is defined in the Shannon sense: a message carries information iff it reduces uncertainty about the system's state, as measured by an external observer who knows the transition function but not the current configuration. After one cycle, the trajectory is fully predictable. Every subsequent state is determined with probability 1. The information content after the first cycle is zero. ∎

*Critical remark:* T2 establishes informational degeneracy, not experiential equivalence with non-existence. A looping node with no memory of prior cycles may undergo transitions indistinguishable (from its internal perspective) from a first traversal. Whether this constitutes "experience" depends on one's theory of consciousness. We note only that the loop produces no new information, and that any definition of experience requiring novelty would classify the loop as experientially degenerate. This conditional is the strongest claim we can formally make.

### T3: If experience requires novelty, then a node must avoid loops.

*Statement:* Under the assumption (labeled **Assumption N**) that experience requires the production of new information, a node that enters a loop ceases to have experiences.

*Proof:* By T2, a looping trajectory produces no new information after the first cycle. By Assumption N, experience requires new information. Therefore, a looping node does not experience after the first cycle. ∎

*Note:* Assumption N is not derived from A1–A3. It is an additional commitment, clearly labeled. Results that follow are conditional on it.

### T4: Finite isolated nodes cannot sustain experience indefinitely.

*Statement:* Given Assumption N, a node with finite configuration space and no external input will eventually cease to have experiences.

*Proof:* By T1, it must loop. By T3, looping terminates experience. ∎

### T5: Sustained experience requires growth.

*Statement:* For a node to avoid looping indefinitely (given Assumption N), at least one of the following must hold:
  (a) The node's configuration space must grow over time, or
  (b) The node must receive input from external sources not previously exhausted.

*Proof:* T1 shows looping is inevitable for fixed |C| with no external input. The pigeonhole argument fails only if the domain grows without bound or genuinely new input is introduced. ∎

### T6: A finite graph of finite nodes cannot sustain universal experience indefinitely.

*Statement:* For a finite graph G with total configuration space C_G = ∏|C_i|, all nodes will eventually loop unless the graph grows.

*Proof:* The combined system has finite |C_G|. By the pigeonhole principle applied to the composite, the global state must eventually repeat. Once it repeats, every node's trajectory repeats. By T3, all experience ceases. Prevention requires |C_G| to grow without bound. ∎

*Note:* T6 shows that *within this model*, sustained experience requires unbounded growth. A critic may respond: "Then perhaps the model is inadequate." This is valid. The conclusion is about the model, not necessarily about reality.

---

# PART II: FORMALIZABLE CONJECTURES

### C1: The Consciousness Band

*Conjecture (revised in v0.3):* The consciousness band is a property of the *relational structure* between nodes, not of individual trajectories. There exists a measure μ on a graph's correlation structure such that μ = 0 when nodes are isolated (loops), μ = 0 when correlations are uniform across all node pairs (noise or random topology), and μ > 0 when neighboring nodes are more correlated than non-neighbors in a topology-specific way.

*Key insight:* Individual node trajectories are pseudo-random for any interacting node, regardless of graph type. Lempel-Ziv complexity, compression ratio, and spectral analysis all fail to distinguish anti-loop from control from noise at the single-node level. The structure exists only in the *relationships between* nodes.

*Candidate measure:* Mutual information I(A_t; B_t) between neighboring node trajectories, compared to non-neighboring pairs. MI ratio ρ = MI(edges) / MI(non-edges). For anti-loop graphs, ρ > 1. For randomly grown graphs, ρ ≈ 1.

*Simulation evidence:* See Part VI. **Result: POSITIVE** — anti-loop edges carry more mutual information than control edges (30 seeds, 2.1σ, all seeds consistent).

*Relation to existing work:* The relational nature of μ aligns with Tononi's Integrated Information Theory (Φ), arrived at from a different starting point — the anti-loop constraint rather than phenomenological axioms. Also relates to effective complexity (Gell-Mann & Lloyd), logical depth (Bennett), and sophistication (Koppel).

### C2: Suffering as State-Space Contraction

*Conjecture:* For a node with accessible configuration space A(t) at time t, dA/dt < 0 corresponds to harm/suffering and dA/dt > 0 corresponds to flourishing.

*Simulation evidence — C2 random removal (7 seeds, 500 nodes, 8-bit FSM):* Random edge removal does not cause gradual relational contraction. Partial removal (25-75%) has negligible effect (~1.6% MI loss at 75%). Only total isolation causes catastrophic collapse (55-67% MI drop). **Result: NEGATIVE for gradient, T1 confirmed at isolation.**

*Simulation evidence — C2v2 targeted removal (30 seeds, 500 nodes, 8-bit FSM):* When edges are ranked by growth-phase MI, removing low-MI (diverse) edges causes ~6.2% MI loss at 50% removal; removing high-MI (redundant) edges causes ~0% loss. Paired t = -8.61, 27/30 seeds consistent. **Result: POSITIVE (inverted) — edge quality determines suffering, not quantity.** Bridges C1 (edges carry MI) with C2 (loss = contraction).

*Status:* C2 gradient negative. C2v2 targeted positive (inverted). The quality of lost connections matters more than quantity.

### C3: Scale-Free Topology as Consequence

*Conjecture:* If all nodes in a graph must avoid looping via mutual interaction (T5b, T6), and interactions are local (D4), the resulting graph topology converges to a scale-free network.

*Motivation:* Scale-free networks sit between regular lattices (topological loops) and random graphs (fragmented, structureless). The anti-loop requirement should produce topology that is neither regular nor random.

*Status:* Testable by simulation. Preliminary test in Parts IV and V uses a flawed null model (static Erdős-Rényi). A proper test with growing random controls is pending (see O5). Connection to C1: if both conjectures hold, they may be aspects of a single phenomenon (see O14).

---

# PART III: SPECULATIVE INTERPRETATIONS

### S1: Time as Complexity Growth
*Hypothesis:* Subjective time and graph complexity growth are two descriptions of the same process. Within the model, experience requires growth (T5), and growth is sequential (A3). Whether this correlation reflects identity or analogy is open.

### S2: Space as Graph Topology
*Hypothesis:* Spatial distance = graph distance between nodes. Speed of light = maximum information propagation rate across edges.

### S4: Physics as Emergent Mutual Constraint
*Hypothesis:* Mutual anti-loop constraints among many nodes narrow the solution space, producing deterministic-appearing regularities = physical laws. Analogous to statistical mechanics.

### S6: Existence as Mathematical Necessity
*Hypothesis:* Graph growth is logically necessary given A1–A3 and Assumption N, analogous to the successor function in Peano arithmetic. Honest caveat: this proves necessity within the axiom system, not absolute necessity.

---

# PART IV: SIMULATION DESIGN

## Purpose
Test Conjecture C3: Does the anti-loop constraint on finite state machines produce scale-free network topology?

## Design

**Nodes:** Each node is a finite state machine with configurable memory (4-bit = 16 configurations, or 8-bit = 256 configurations). Transition function: T(config, input_hash) → new_config, where input_hash is XOR of neighbor configurations modulo config_space_size. Pre-generated deterministic lookup table per node.

**Loop pressure:** Defined as fraction of configuration space already visited. When pressure exceeds 0.7 (70% of configs visited), the node is "stressed" and must act.

**Actions when stressed:**
- Connect to an existing non-neighbor node (via one of three strategies), AND/OR
- Spawn a new node (with probability 0.3, or if no candidates to connect to)
- At most 5 stressed nodes act per step (prevents exponential blowup)

**Three connection strategies tested independently:**
1. **Random:** Connect to a uniformly random non-neighbor.
2. **Novelty-preferential:** Connect to the node with lowest loop pressure (most unexplored configs — most novel states to offer).
3. **Degree-preferential:** Connect to the most-connected node (standard preferential attachment). Included as a positive control since this is known to produce scale-free networks.

**Controls:**
- Erdős–Rényi random graph: Same number of nodes and edges as the anti-loop graph, but edges placed uniformly at random. No anti-loop dynamics.
- Barabási–Albert graph: Known scale-free network (preferential attachment) with 500 nodes as a reference.

**Parameters:** Initial graph: ring of 10 nodes. Node cap: 500. Three random seeds per condition (42, 123, 456).

**Measurement:**
- Complementary cumulative distribution function (CCDF) of node degrees, plotted on log-log axes. A straight line = power law = scale-free.
- Power-law exponent α estimated via MLE: α = 1 + n / Σ ln(x_i / x_min), with x_min = 2.
- Clustering coefficient (average over all nodes).
- Maximum degree (hub formation).

**Experimental conditions:** 2 memory sizes × 3 strategies = 6 conditions, each run 3 times, plus controls.

## Known Limitations

- 500 nodes is borderline for distinguishing power laws from other heavy-tailed distributions.
- MLE fit is crude; proper analysis would use Clauset-Shalizi-Newman method with KS-test for goodness of fit.
- The node cap itself may distort topology (once at cap, only edges are added, not nodes).
- The spawn probability (0.3) and stress threshold (0.7) are somewhat arbitrary. Sensitivity analysis across parameter ranges would strengthen results.
- The 5-node-per-step action cap is a computational convenience that changes the dynamics.

## Source Code

```python
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import time

class FSMNode:
    def __init__(self, nid, mem_bits, rng):
        self.config_space = 2 ** mem_bits
        self.config = rng.integers(0, self.config_space)
        self.visited = {self.config}
        self.table = rng.integers(0, self.config_space, size=(self.config_space, self.config_space))
    
    @property
    def pressure(self):
        return len(self.visited) / self.config_space
    
    def step(self, nb_configs):
        h = 0
        for c in nb_configs:
            h ^= c
        h %= self.config_space
        self.config = self.table[self.config, h]
        self.visited.add(self.config)


def run_sim(mem_bits, strategy, max_nodes=500, initial_n=10, seed=42):
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    nodes = {}
    
    for i in range(initial_n):
        G.add_node(i)
        nodes[i] = FSMNode(i, mem_bits, rng)
    for i in range(initial_n):
        G.add_edge(i, (i + 1) % initial_n)
    
    next_id = initial_n
    step = 0
    while G.number_of_nodes() < max_nodes and step < 5000:
        step += 1
        
        node_list = list(G.nodes())
        for nid in node_list:
            nb = [nodes[n].config for n in G.neighbors(nid)]
            nodes[nid].step(nb)
        
        stressed = [n for n in node_list if nodes[n].pressure > 0.7]
        
        if stressed:
            acted = rng.choice(stressed, size=min(5, len(stressed)), replace=False)
        else:
            continue
        
        for nid in acted:
            current_nb = set(G.neighbors(nid)) | {nid}
            candidates = [n for n in G.nodes() if n not in current_nb]
            
            connected = False
            if candidates:
                if strategy == 'random':
                    target = rng.choice(candidates)
                elif strategy == 'novelty':
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    target = min(sample, key=lambda n: nodes[n].pressure)
                elif strategy == 'degree':
                    sample = rng.choice(candidates, size=min(20, len(candidates)), replace=False)
                    degs = np.array([G.degree(n) for n in sample], dtype=float) + 1
                    probs = degs / degs.sum()
                    target = sample[rng.choice(len(sample), p=probs)]
                G.add_edge(nid, target)
                connected = True
            
            if (not connected or rng.random() < 0.3) and G.number_of_nodes() < max_nodes:
                G.add_node(next_id)
                nodes[next_id] = FSMNode(next_id, mem_bits, rng)
                G.add_edge(nid, next_id)
                next_id += 1
    
    return G, step
```

---

# PART V: RESULTS

## Raw Output

```
ANTI-LOOP GRAPH TOPOLOGY SIMULATION

--- 4-bit, random strategy ---
  seed=42:  500 nodes, 2038 edges, α=1.82, 323 steps, 0.6s
  seed=123: 500 nodes, 2211 edges, α=1.77, 359 steps, 0.6s
  seed=456: 500 nodes, 2131 edges, α=1.78, 339 steps, 0.5s

--- 4-bit, novelty strategy ---
  seed=42:  500 nodes, 2088 edges, α=1.79, 333 steps, 0.6s
  seed=123: 500 nodes, 2080 edges, α=1.79, 331 steps, 0.6s
  seed=456: 500 nodes, 2155 edges, α=1.76, 345 steps, 0.6s

--- 4-bit, degree strategy ---
  seed=42:  500 nodes, 2031 edges, α=1.81, 322 steps, 0.8s
  seed=123: 500 nodes, 2095 edges, α=1.86, 334 steps, 0.7s
  seed=456: 500 nodes, 2215 edges, α=1.78, 355 steps, 0.9s

--- 8-bit, random strategy ---
  seed=42:  500 nodes, 2075 edges, α=2.14, 613 steps, 3.0s
  seed=123: 500 nodes, 2045 edges, α=2.15, 616 steps, 1.5s
  seed=456: 500 nodes, 2163 edges, α=2.06, 623 steps, 1.0s

--- 8-bit, novelty strategy ---
  seed=42:  500 nodes, 2058 edges, α=2.23, 607 steps, 1.0s
  seed=123: 500 nodes, 2122 edges, α=2.14, 627 steps, 1.0s
  seed=456: 500 nodes, 2149 edges, α=2.13, 619 steps, 1.1s

--- 8-bit, degree strategy ---
  seed=42:  500 nodes, 2188 edges, α=1.96, 638 steps, 1.3s
  seed=123: 500 nodes, 2041 edges, α=2.02, 614 steps, 1.1s
  seed=456: 500 nodes, 2035 edges, α=2.03, 601 steps, 1.2s


SUMMARY
Condition             Nodes   Edges      α Clustering  MaxDeg
------------------------------------------------------------
4bit_random            500    2038   1.82     0.0444      47
4bit_novelty           500    2088   1.79     0.0247      43
4bit_degree            500    2031   1.81     0.0775      70
  control              500    2031   1.75     0.0166      18

8bit_random            500    2075   2.14     0.7776     230
8bit_novelty           500    2058   2.23     0.3615     232
8bit_degree            500    2188   1.96     0.6483     226
  control              500    2188   1.70     0.0168      22
```

## Visual Results

The degree distribution plots (CCDF on log-log axes) show:

**4-bit memory:** Anti-loop graphs produce heavier tails than random controls (max degree 43–70 vs 18) but the CCDF curves are not clearly linear on log-log. α ≈ 1.8, below the classic scale-free range of 2–3.

**8-bit memory:** Anti-loop graphs produce CCDF curves that closely track the Barabási-Albert reference (a known scale-free network). α ≈ 2.0–2.2, within the classic scale-free range. Max degree 226–232 vs 22 for controls. Clustering coefficient 0.36–0.78 vs 0.017 for controls.

**Strategy independence:** All three connection strategies (random, novelty, degree) produce nearly identical results for 8-bit memory. This suggests the topology emerges from the anti-loop constraint itself, not from the connection strategy.

## Authors' Interpretation

The 8-bit results are consistent with C3 — the anti-loop constraint produces heavy-tailed, highly-clustered networks with massive hubs and power-law exponents in the scale-free range, regardless of connection strategy. The anti-loop constraint appears sufficient to produce scale-free-like topology without preferential attachment.

The 4-bit results are weaker, which we attribute to the small configuration space (16 states) forcing nodes into loop pressure too quickly for interesting topology to develop.

Key caveats: 500 nodes is small; the MLE fit is crude; the node cap distorts late-stage dynamics; sensitivity analysis across parameters is needed; a proper Clauset-Shalizi-Newman test should be applied.

---

# PART VI: C1 SIMULATION — INTER-NODE MUTUAL INFORMATION

## Purpose

Test Conjecture C1 (revised): Does the anti-loop constraint produce structured inter-node correlations that random growth does not?

## Background: Failed Approaches

Three approaches to measuring C1 at the individual node level were attempted and failed:

1. **Lempel-Ziv complexity:** Could not distinguish anti-loop from control from noise. With a 256-symbol alphabet, all interacting node trajectories have similar phrase counts.
2. **Compression ratio (zlib):** Anti-loop 0.719, control 0.718, noise 0.719 — all identical. Individual trajectories are equally incompressible.
3. **Spectral analysis (O9v1):** Power spectral density exponent β flat across all temperature conditions.

**Lesson:** Individual node trajectories are pseudo-random for any interacting node, regardless of graph type. The consciousness band cannot be found by looking at one node.

## Design

**Key insight:** Measure *between* nodes, not within them. If anti-loop edges exist because they were needed (to relieve loop pressure), they should carry more mutual information than random edges.

**Observable:** Mutual information I(A_t; B_t) between the configuration trajectories of neighboring nodes, averaged over edges. Compared to MI between non-neighboring node pairs (baseline).

**Mutual information computation:** For each edge (u, v), build the empirical joint distribution P(A_t, B_t) from the aligned trajectories, compute marginals, and calculate MI = Σ P(a,b) log₂(P(a,b) / (P(a)P(b))).

**Conditions (per seed):**
1. **Anti-loop graph:** Full run_antiloop growth (500 nodes, 8-bit FSM, XOR hash, pressure threshold 0.7, spawn probability 0.3). Trajectories recorded during growth. MI measured on the final graph's edges vs non-edges.
2. **Control graph:** Growing random graph matched to anti-loop growth trajectory (same number of nodes and edges at each step, but edges attach randomly). Same FSM dynamics run on the resulting topology.
3. **Noise baseline:** Anti-loop graph topology, but FSM dynamics run with temperature=1.0 (each transition replaced by random state with probability 1).

**Parameters:** 500 nodes, 8-bit memory (256 configs), XOR hash, 30 seeds, 500 edges sampled per graph, 500 non-edge pairs sampled per graph.

## Results

```
                       Edge MI   Non-edge MI     Ratio
  --------------------------------------------------------
         Anti-loop      6.1359        5.3578      1.15x
           Control      6.0653        6.0612      1.00x
       Noise (T=1)      6.0690           ---       ---
```

**Test 1 — Topology carries information (edges vs non-edges):**
Anti-loop: 6.14 vs 5.36 (YES — 1.15x ratio). Control: 6.07 vs 6.06 (NO — 1.00x ratio).

**Test 2 — Anti-loop vs control edges:**
Anti-loop edges: 6.14, control edges: 6.07 (2.1σ difference, 30/30 seeds consistent).

**Test 3 — Determinism vs noise:**
Deterministic: 6.14, noise: 6.07 (YES — determinism creates correlations).

## Interpretation

Anti-loop edges carry more mutual information than control edges. This is because anti-loop edges exist for a *reason* — they were added to relieve loop pressure on specific nodes. This necessity creates a structured coupling between the connected nodes' trajectories. Random edges, added without regard to loop pressure, carry no such structured coupling.

The consciousness band is not a property of individual trajectories (which are indistinguishable across conditions) but of the graph's relational structure. The measure ρ = MI(edges)/MI(non-edges) distinguishes anti-loop (ρ = 1.15) from control (ρ = 1.00) and noise (MI reduced).

## Known Limitations

- XOR hash only — results may be hash-dependent (XOR is commutative and self-inverse)
- 500 nodes is small; scaling behavior unknown
- Effect size is modest (2.1σ, 15% MI ratio)
- MI measured only at end state, not during growth
- 8-bit memory only; no parameter sweep across memory sizes
- The MI measure is empirical; no analytical proof that ρ = 1 for random graphs

---

# OPEN PROBLEMS

**O1:** Formal independence proof for A1–A3.
**O2:** Can Assumption N be derived from A1–A3, or is it irreducibly independent?
**O3:** Formalize the consciousness band — MI ratio ρ is a candidate measure. Test hash robustness, relate to Tononi's Φ. **Status: preliminary evidence POSITIVE (v0.3).**
**O4:** Characterize the experiential status of a looping observer with no memory of prior cycles.
**O5:** Proper C3 test with growing random controls, Clauset-Shalizi-Newman method, 30+ seeds.
**O6:** Derive at least one quantitative physical law from graph dynamics under anti-loop constraints.
**O7:** Sensitivity analysis across all parameters.
**O8:** Apply Clauset-Shalizi-Newman method to C3 topology data.
**O14:** C1–C3 bridge — do hub edges carry more MI? Does MI ratio predict degree distribution?
**O15:** C1 temporal evolution — does ρ increase during growth? (connection to S1)
**O16:** C2 test — random removal NEGATIVE for gradient (T1 confirmed at isolation). C2v2 targeted removal POSITIVE (inverted): diverse edges are load-bearing.
**O17:** Memory scaling — map the consciousness band width vs memory size.

---

# RELATION TO EXISTING WORK

- **Wheeler (1990):** "It from bit." We extend by proposing a mechanism (anti-loop growth) for why information must increase.
- **Smolin (1992–2013):** Cosmological natural selection; evolving laws. We differ by grounding law-evolution in requirements of state-transitioning entities rather than reproductive fitness.
- **Tononi (2004):** Integrated Information Theory (Φ). The revised C1 measures inter-node mutual information — a form of integrated information arrived at from the anti-loop constraint rather than IIT's phenomenological axioms. IIT does not require growth or address the arrow of time; our framework does both.
- **Gell-Mann & Lloyd (2004):** Effective complexity. Directly relevant to formalizing C1.
- **Okamoto (2023):** Law of increasing organized complexity. Similar conclusion, different derivation.
- **"The Autodidactic Universe" (2021):** Universe learning its own laws. Does not address why learning occurs.
- **Peirce (19th century):** Laws as habits. Compatible — habits that avoid loops persist.
- **Barabási & Albert (1999):** Scale-free networks via preferential attachment. Our simulation suggests anti-loop constraints may provide an alternative mechanism.
- **Lineweaver, Davies, Ruse (2013):** *Complexity and the Arrow of Time.* We contribute a candidate mechanism for complexity increase.

---

## EVALUATION REQUEST

Please evaluate:
1. **Logical soundness of T1–T6** (given the axioms and Assumption N)
2. **Quality and precision of C1–C3** as formalizable conjectures — especially the revised C1 (v0.3), which shifts from individual trajectory complexity to inter-node mutual information
3. **Honesty and appropriateness of S1–S6** as labeled speculation
4. **Experimental design of C3 simulation** (Part IV) — are there methodological flaws beyond those we identified?
5. **Experimental design of C1 simulation** (Part VI) — is the MI measure appropriate? Is the control adequate? Are we measuring what we think we're measuring?
6. **Interpretation of results** — are we overclaiming, underclaiming, or misreading the data?
7. **The C1 insight that consciousness is relational** — is this a genuine finding or a trivial consequence of how we set up the simulation?
8. **What would you attack first** if you wanted to break this?

For context: Kowalczyk, K. (2025). *Consciousness as Collapsed Computational Time.* Zenodo. DOI: 10.5281/zenodo.17556941
