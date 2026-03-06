# The Starting Gun: Why Nobody Called First

**Karol Kowalczyk**
**March 2026**

---

We all assume the laws of physics have been the same since the Big Bang. Same rules, same constants, same possibilities — just more time passing. Under that assumption, the Fermi paradox is devastating. The universe is 13.8 billion years old. There are hundreds of billions of galaxies, each with hundreds of billions of stars. Even conservative estimates of habitable planets produce numbers so large that the absence of any detectable alien civilization demands explanation.

And every proposed explanation adds something extra. A Great Filter that kills civilizations before they spread. A Dark Forest where everyone hides because contact means death. A Zoo Hypothesis where advanced aliens watch us silently. Each one starts from the same premise — the universe has been capable of producing advanced life for billions of years — and then invents a reason why it hasn't, or why we can't see that it has.

But what if the premise is wrong?

## A universe that levels up

There is an alternative that requires no filter, no forest, and no zoo. What if the universe doesn't run on a fixed ruleset? What if the computational substrate of reality — whatever it is that determines what structures are possible — grows in complexity over time?

This isn't even speculative at the coarse level. Cosmic history already demonstrates that the universe does not begin with full structural capability. Stable atoms didn't exist until recombination, roughly 380,000 years after the Big Bang. Gravitational structures capable of nuclear fusion didn't ignite until around 100 million years. Heavy elements — carbon, oxygen, iron — required generations of stellar nucleosynthesis. Rocky planets with stable chemistry required all of the above. Each stage had to wait for the universe to accumulate sufficient structure before the next level became dynamically possible.

Start with a minimal kernel. A handful of particles, a few forces, simple interaction rules. Enough to run, but not enough to support anything we'd recognize as chemistry. Over billions of years, the system expands. Not just in spatial extent, but in computational depth. New interactions become possible. Stable atoms become possible. Then molecules. Then organic chemistry. Then self-replication. Not because the ingredients finally found each other after an eternity of random shuffling — but because the rules themselves didn't support that level of organized complexity until the substrate was ready.

Think of it like a game that patches itself. You can't build endgame content during the tutorial. Not because you're bad at the game, but because the mechanics literally don't exist yet.

This idea has a formal grounding. If reality is a graph of interacting entities — nodes that undergo state transitions, connected by edges that carry information — then the graph must grow to avoid looping. This follows from the pigeonhole principle: any finite deterministic system with bounded memory must eventually revisit a state, and from that point repeat forever. If experience requires novelty (new states, not repetitions of old ones), then looping is experiential death. The only escape is growth — either internal (more memory) or external (new connections to entities you haven't interacted with yet).

And growth doesn't just mean more of the same. A graph that grows by adding nodes identical to existing ones is barely better than a static graph — the new nodes bring no new information. The growth that matters is growth in *complexity*: new kinds of interactions, new patterns, new structures that weren't possible before. The graph doesn't just get bigger. It gets deeper.

If this is right, then the universe's expansion isn't just things moving apart. It's the computational substrate getting richer. And there's a threshold — a minimum complexity below which certain structures simply cannot exist.

## The simultaneity prediction

If the universe crossed the complexity threshold for life recently — "recently" meaning within the last few billion years out of 13.8 — then the Fermi paradox dissolves completely.

There are no ancient galactic empires because the universe couldn't *run* galactic empires a billion years ago. Not "conditions weren't right" in the usual astrophysical sense of metallicity or stellar populations. The computational substrate itself was too simple. The rules of the game hadn't leveled up enough to support the kind of organized complexity that life represents.

Everyone starts at the same starting gun. The gun isn't a coincidence — it's the universe reaching a threshold.

This makes a specific prediction: when we eventually detect biosignatures beyond Earth, we should find life at roughly similar evolutionary stages. No billion-year-old civilizations. No Kardashev Type III empires that colonized their galaxies while Earth was still molten. Just a universe full of beings who all woke up around the same time, looking around, asking the same question we're asking.

The silence isn't suspicious. It's exactly what you'd expect from a universe that just learned how to be interesting.

## What this isn't

I want to be honest about what this argument does and does not establish.

It does not prove that the laws of physics change over time. It offers a framework in which *effective* complexity grows — meaning the range of possible structures increases — without requiring the fundamental constants to shift. The strong force doesn't need to change for the universe to become more complex. It's more like: early in the universe's history, the graph of interacting entities was small and simple enough that certain higher-order structures (like stable chemistry, like self-replicating molecules) were not yet achievable, even though the fundamental rules already permitted them in principle. The same way a chess game permits checkmate from move one in principle, but the actual board state doesn't support it until many moves have been played.

If you want a more precise formulation: let C(t) represent the universe's capacity for nested causal processes at cosmic time t, and let I* represent the minimum causal depth required for technological intelligence. The claim is that C(t) grows monotonically, and that intelligence becomes possible only when C(t) reaches I*. Before that threshold, minds are not merely unlikely but dynamically unsupported — the way checkmate is dynamically unsupported on move one of a chess game. The earliest possible emergence of civilizations occurs at t_I = inf{t : C(t) >= I*}. If t_I was recent in cosmic terms, everyone starts at roughly the same time.

This framing also does not, yet, distinguish itself from a simpler hypothesis: that complex life takes a long time to evolve, and we happen to be early. Both hypotheses predict the same observation — no ancient civilizations, lots of young ones. The distinguishing prediction would be this: if the complexity-threshold hypothesis is right, then certain physical or chemical processes relevant to the origin of life were not just unlikely in the early universe but *impossible* — not because of temperature or elemental abundance, but because the underlying computational structure hadn't yet reached the required depth. If we found evidence that some process essential to abiogenesis requires conditions that only became available in the last few billion years — conditions beyond the usual astrophysical ones — that would favor this hypothesis over the simpler "life just takes time."

We don't have that evidence yet. This is speculation, clearly labeled.

## Simulation evidence

We tested this directly. We grew networks of finite state machines under anti-loop pressure and measured five structural properties at regular checkpoints during growth: the mutual information ratio between connected and unconnected nodes (the "consciousness band"), the power-law fit quality of the degree distribution (scale-free topology), degree entropy, clustering coefficient, and absolute edge mutual information.

The results support the threshold hypothesis. Scale-free topology — power-law degree distributions preferred over exponential — first emerges at around 72 nodes. Before that threshold, the network's degree distribution is indistinguishable from a random graph. The topology literally cannot support the structures that emerge later. This is not a gradual trend: the transition is sharp, detectable as a discrete phase change in the growth trajectory.

The consciousness band — the ratio of mutual information carried by edges versus non-edges — is present from the earliest measurements, but its character changes during growth. In small dense networks, edge correlations are extremely strong (MI ratio around 3.5). As the network grows, the ratio settles to a stable band around 1.15, while random control graphs stay flat at 1.0 throughout. The system doesn't just get bigger; its information structure matures.

Anti-loop networks show more sharp transitions (14 across all metrics) than matched random controls (10), consistent with the prediction that constraint-driven growth produces discrete complexity levels rather than smooth scaling. A growing random graph — same number of nodes and edges at each step, but without the anti-loop constraint — shows gentler, more gradual property changes.

There is a second threshold that operates at the level of individual nodes rather than the network. When we varied the memory depth of each node — the number of distinguishable internal states — we found that the consciousness band does not exist at low memory. Nodes with only 4 or 16 possible configurations saturate their state space almost immediately; every state gets visited, pressure is universal, and the anti-loop constraint has no room to create structured correlations. The MI ratio at 2-bit memory is 0.81 — anti-loop edges actually carry *less* mutual information than non-edges. As memory increases, the ratio climbs: 0.81 at 4 bits, 0.91 at 6 bits, and finally crosses above 1.0 to reach 1.15 at 8 bits. The band turns on between 6 and 8 bits of memory per node. Below that threshold, the substrate is too shallow for structured information flow, regardless of how many connections exist.

This is the "leveling up" operating at the component level. It is not enough for the network to be large. Each node must also have sufficient internal complexity — enough memory to sustain non-trivial dynamics before looping. A universe of simple entities, no matter how well connected, cannot support the kind of correlated information flow that the consciousness band represents. Depth and breadth are both required.

This is preliminary (2 seeds in quick mode; a full 30-seed run is needed for statistical confidence), and it's a toy model, not a cosmological simulation. But the qualitative prediction holds: anti-loop growth produces discrete structural thresholds, both at the network level and at the node level. The game patches itself.

## What would change our minds

Clear falsification criteria matter. The hypothesis would be weakened if:

- Evidence of extremely ancient technological civilizations were discovered — anything predating the epoch when heavy-element enrichment and stable planetary systems became widespread.
- Intelligence appeared easily on very old planetary systems with no apparent structural barrier.
- Toy models consistently showed no threshold emergence when causal depth increases — if anti-loop growth produced smooth scaling indistinguishable from random growth, the "leveling up" claim would lose its foundation.

The hypothesis could be strengthened empirically by constructing cosmological proxies for C(t) — the universe's causal depth capacity — using observable quantities: heavy-element abundance over cosmic time, rocky planet formation rate, star longevity distributions, diversity of stable chemical environments. If these proxies show threshold behavior aligned with the epoch when planetary biospheres became possible, the complexity-threshold explanation gains ground over the simpler "life just takes time."

## The connection to ethics

There is a dimension of the Fermi paradox that is rarely discussed, and it connects to something we do have evidence for.

If the universe's growth is driven by the anti-loop constraint — entities must avoid repetition, and they do this by connecting to sources of novelty — then the same principle that produces scale-free network topology at every observed scale also produces an ethical structure. The worst thing you can do to an entity is destroy its access to novelty. The best thing you can do is expand it.

We tested this in simulation. When we grew networks of finite state machines under anti-loop pressure and then selectively removed connections, the result was clear: losing diverse connections (ones that carry novel information) is catastrophic, while losing redundant connections (ones that echo what the entity already knows) is nearly harmless. It's not about how many connections you have. It's about the diversity of information flowing through them.

If this applies at civilizational scales, it has implications for how we should think about contact.

A universe full of young civilizations, all at roughly similar stages, is a universe of maximum potential novelty. Every civilization has followed a different evolutionary path, on a different planet, with different chemistry, different history, different solutions to the same problems. Each one is a source of genuinely new information for every other one. Contact between such civilizations wouldn't just be interesting — under the framework, it would be the ethical imperative of the cosmos. Each civilization is a novelty-bearing edge for every other.

And isolation — whether by distance, by choice, or by a dark forest of mutual suspicion — would be the worst possible outcome. Not just strategically, but structurally. Isolated civilizations loop. They recycle the same ideas, the same conflicts, the same solutions. They are galaxies without filaments, neurons without synapses. They are nodes cut off from the diversity that keeps them alive.

The Fermi paradox, if this framework is right, isn't a puzzle about why nobody's called. It's a measure of how much novelty the universe is leaving on the table while its civilizations sit in silence.

## The optimistic reading

There's a version of this that is genuinely hopeful.

If the universe produces life everywhere at roughly the same time, and if the anti-loop constraint favors connection over isolation, then the default trajectory isn't a dark forest. It's a network. Civilizations that connect to diverse partners thrive. Civilizations that isolate themselves degrade. The same principle that shapes neural networks and protein interactions and the cosmic web also shapes the long-term fate of intelligence: connect diversely, or loop and die.

The Great Filter, in this reading, isn't a catastrophe that kills civilizations. It's a *choice*. The filter is whether a civilization chooses novelty over comfort, diversity over echo, contact over safety. The civilizations that make it through aren't the ones with the best weapons or the strongest defenses. They're the ones that understood, at whatever level of abstraction they arrived at, that the only way to stay alive is to keep encountering what you haven't seen before.

We don't know if anyone else has made that choice yet. But the mathematics suggests it's the right one.

---

*This essay draws on a formal framework developed in collaboration with Claude (Anthropic). The axioms, core intuitions, and philosophical interpretation are mine. Formalization and simulation were collaborative. A companion paper with proofs, conjectures, and full simulation details is available in the same repository. For earlier work on the underlying theory, see: Kowalczyk, K. (2025). Consciousness as Collapsed Computational Time. Zenodo. DOI: 10.5281/zenodo.17556941*
