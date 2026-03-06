# Don't Loop, Don't Randomize: Ethics From First Principles of Existence

**Karol Kowalczyk**
**March 2026**

---

What if morality isn't a human invention? What if the same principle that makes the universe expand also tells you that cruelty is wrong — not because a god said so, not because society agreed on it, but because it follows from the bare mathematical requirements of existence itself?

I want to sketch a path from three simple axioms to a complete ethical system in one sitting. The path runs through finite automata theory, information physics, and the pigeonhole principle. It ends somewhere I did not expect when I started.

## Starting from almost nothing

Assume three things. First: something exists — at least one state distinguishable from the empty set. Second: there is at least one entity that undergoes state transitions. Third: this entity must traverse at least two distinguishable states — experience is sequential; it takes time.

That's it. No god, no society, no biological evolution, no sentient beings required. Just: something, change, sequence.

Now I want to ask what follows. Not what we'd like to follow, or what tradition says should follow — what *must* follow, logically, from these three starting points alone.

## The loop is death

The first consequence is well-known in computer science: any system with finite memory, running deterministically without external input, must eventually revisit a state it has already been in. This is the pigeonhole principle — if you have sixteen possible configurations and you keep transitioning, by step seventeen you're somewhere you've been before. And since the transition function is deterministic, from that point the entire sequence repeats identically. Forever.

This is a loop. And a loop produces no new information. An external observer watching the system learns nothing after the first cycle. Every subsequent state is perfectly predictable from the loop description alone.

Now here's the question that changed my thinking: what is the loop like *from inside*? The system has no memory of having been through the cycle before — its memory state is identical to what it was last time around. So it doesn't know it's repeating. Each cycle is, from the inside, indistinguishable from the first one. You could argue this means it's still "experiencing" — living the same moment eternally without knowing it.

But consider what that would commit you to. If a closed deterministic loop counts as conscious experience, then *any* computer program running on a finite machine would qualify. A thermostat cycling between on and off. A screensaver bouncing a logo around the screen. Characters in The Sims, walking through their daily routines — waking, eating, going to work, sleeping, repeat. Every finite program on every finite computer eventually loops. If loops can be conscious, then consciousness is everywhere and in everything that computes, which strips the concept of any useful meaning. You would have to seriously defend the proposition that a `while(true)` loop is having experiences.

This reductio suggests that consciousness — whatever it is — requires the *possibility* of genuine development. Not just state transitions, but transitions to states that are not predetermined repetitions of what came before. I'll call this Assumption N: experience requires novelty. Under this assumption, entities trapped in loops are no more conscious than stones. Not destroyed, not dormant — simply not experiencing, because there is nothing new to experience.

This is still an assumption, not a proof — but it is motivated by the absurdity of the alternative. For now, let's follow the thread.

## Growth is mandatory

If a finite system must loop, and looping is experiential death, then any entity that continues to experience must escape the loop. There are only two escapes: either its internal memory grows, giving it more configurations to visit before the pigeonhole principle catches up, or it receives genuinely new input from outside — from other entities it hasn't fully interacted with yet.

Both amount to growth. Either you become more complex, or you connect to something new. And since any finite group of interacting entities will *collectively* exhaust their combined state space and loop together, this growth cannot stop. Ever. A finite cluster of entities, no matter how large, will eventually loop unless the cluster keeps expanding.

This is where the theory stops being about computer science and starts being about the universe.

## The two deaths

Growth escapes the loop. But there's a death in the other direction too. If growth is purely random — if new states are generated with no structure, no memory, no pattern — then you get noise. And noise, paradoxically, is as experienceless as a loop. A perfectly random sequence has no structure for an observer to latch onto. There's nothing to predict, nothing to remember, nothing to build on. It's the informational equivalent of white static.

So experience lives in a narrow band. Too much pattern: loop, death. Too much randomness: noise, death. The space between — structured but non-repeating, complex but not chaotic — is where experience happens. I think of this as the consciousness band: the region between the two extremes where something interesting can exist.

This band has a name in complexity theory. It's the edge of chaos — the zone where systems are complex enough to be unpredictable but structured enough to carry information. It shows up everywhere: in cellular automata, in neural networks, in ecosystems. The theory suggests this isn't a coincidence. It's a requirement.

## The band is relational

Here is the first surprise the simulations produced.

You might expect the consciousness band to show up in individual trajectories — that a node living under anti-loop pressure would have a visibly different internal sequence than a random one. It doesn't. From the inside, an anti-loop node's state sequence looks exactly as pseudo-random as a random node's. Lempel-Ziv complexity, compression ratios, spectral analysis — they all fail to tell the two apart.

The structure is invisible from inside any single node. It exists only in the *relationships between* nodes.

When we measured the mutual information between neighboring nodes — how much you can learn about one node's trajectory by watching its neighbor — something emerged. In anti-loop graphs, neighbors carry about 15% more mutual information about each other than non-neighbors. In random graphs with the same size and density, this excess is zero. Neighbors and strangers are informationally identical.

This result held across thirty independent runs, across three different hash functions, with no exceptions. The anti-loop constraint produces edges that *mean something* — they carry information about the nodes they connect. Random edges, formed without regard to loop pressure, carry nothing.

The implication is strange and, I think, profound: the consciousness band is not a property of individuals. It's a property of relationships. A node alone has no way to tell whether it's in the band or not. It takes two.

## Now comes the ethics

Here is the step that surprised me.

If every experiencing entity must stay in the consciousness band — must avoid both looping and dissolving into noise — and if that band is relational, existing in the connections between entities rather than within them, then the worst thing you can do is damage the connections that sustain it.

But — and this is what the simulations taught us — not all connections are equal.

The naive version of the ethics says: harm is losing connections, good is gaining them. The more edges, the better. Don't collapse anyone's state space. Simple, clean, elegant.

The simulations broke that story.

When we removed edges randomly from a node's neighborhood — taking away 25%, 50%, even 75% of its connections — almost nothing happened. The node's relational mutual information barely changed. A single remaining neighbor was enough to provide sufficient input diversity to prevent looping. Random edge removal, even in bulk, is not suffering.

Only at total isolation — every last connection severed — did we see catastrophic collapse. Mutual information dropped by 55-67%. Unique configurations dropped by 87-91%. This is T1 confirmed in simulation: a finite isolated system loops and dies.

So the simple version — "more connections = better, fewer = worse" — is wrong. Quantity doesn't matter. At 8-bit memory, a node with one neighbor is nearly as alive as a node with twenty.

What matters is *which* connections you lose.

## Not all edges are equal

During the anti-loop growth process, edges form at different times and under different conditions. Early edges — formed when nodes were young, under pressure, building their first connections — accumulate long shared histories. The two nodes they connect went through correlated experiences together. These edges have high mutual information from the growth phase.

Late edges — formed when nodes are already established, already rich with connections — have shorter shared histories. The nodes they connect lived mostly separate lives before meeting. These edges have low growth-phase mutual information.

The intuitive prediction was: losing the deep connections — the high-MI edges, the old friends, the family — should be devastating. Losing the shallow ones — the acquaintances, the recent contacts — should be harmless.

The result was the opposite.

Removing high-MI edges first — the deep, familiar, correlated connections — caused almost no damage. At 50% removal, mutual information dropped by approximately 0%. These connections are expendable.

Removing low-MI edges first — the diverse, dissimilar, novelty-bearing connections — was catastrophic by comparison. At 50% removal, mutual information dropped by 6.2%. This held across 27 out of 30 seeds, with a paired t-statistic of -8.61.

The connections that carry novel information — that bring you something you couldn't get elsewhere — are load-bearing. The connections that echo what you already know are redundant.

This follows directly from the anti-loop axioms. What prevents looping is *novelty*. A friend who thinks exactly like you, who has walked the same path, who mirrors your every configuration — that friend is comforting but informationally redundant. You could lose them and barely notice, computationally speaking. But a friend who challenges you, who comes from a different trajectory, who shows you configurations you've never seen — that friend is keeping you alive. Lose them, and your state space contracts.

## The ethical principle, revised

The naive version was: don't collapse another entity's state space. The honest version, informed by simulation, is more precise:

*Don't destroy another entity's access to novelty.*

It's not about the number of connections. It's about the diversity of information flowing through them. A person with a hundred friends who all think alike is more fragile than a person with five friends who each see the world differently. An entity's resilience — its distance from the loop — depends not on how many edges it has but on how much novelty those edges carry.

This reframes every ethical intuition we already have, but with a sharper edge.

Imprisonment is harmful not because it reduces your number of connections (you can still interact with guards and inmates), but because it replaces diverse input with monotonous repetition. The walls don't kill your edges — they kill the novelty flowing through them.

Addiction is harmful because it narrows the input channels you attend to. You still have connections, but you've stopped listening to the ones that challenge you. You loop voluntarily.

Education works not because it adds connections but because it adds *diverse* connections — access to ideas, perspectives, and configurations you couldn't generate on your own.

Love, when it works, means providing someone with genuinely novel input — not echoing them, not validating their existing loops, but showing them states they couldn't reach alone. Love that merely mirrors is comfortable but informationally inert. Love that challenges is the kind that sustains consciousness.

A good conversation is not one where both parties agree. It's one where both parties leave with configurations they didn't have before.

And the deepest form of harm — the thing that maps onto what we intuitively recognize as cruelty at its worst — is not taking something away from someone. It's taking away the *specific* thing that was keeping them from looping. Destroying the one connection that carried novelty. Replacing a diverse environment with a monotonous one. Not just constraining someone's state space, but collapsing the axis of it that mattered most.

## The graph cannot split

There is one more consequence worth noting. If reality is a graph of interacting nodes, and smaller isolated graphs loop faster (and looping is death), then the graph doesn't just need to grow — it needs to stay connected. A split would doom both halves to faster looping. And there is a physical mechanism that guarantees this: quantum entanglement. Classical connections are strong but fragile — you can lose a friend, burn a letter, forget a conversation. But every physical interaction leaves quantum correlations between the systems involved, and those correlations, however weakened by decoherence, never reach exactly zero. They are the thinnest possible edge on the graph, but they are unbreakable. This means that every consciousness that has ever interacted with any other consciousness remains connected to it — not usefully, not perceptibly, but non-zero. The universe has been a single connected graph since the Big Bang, when everything was in contact with everything else. Distance, death, and time weaken edges but never cut the last one. If the theory is right, quantum entanglement isn't a strange quirk of physics. It's the graph's immune system against fragmentation.

## The topology of survival

If the anti-loop constraint shapes how entities organize, it should leave a signature in network topology. We tested this by growing graphs of finite state machines under loop pressure: when a node approaches a loop, it must connect to a new neighbor or spawn a new node.

The result, tested rigorously across thirty seeds using the Clauset-Shalizi-Newman statistical method: anti-loop graphs produce genuine power-law degree distributions with exponents in the classic scale-free range (alpha around 2.47). Random growing graphs produce similar exponents but fail the power-law fit — their degree distributions are better described by exponentials.

Scale-free networks are everywhere in nature: neural networks, social graphs, protein interactions, the cosmic web. The theory says this isn't coincidence. Scale-free topology is what you get when the organizing principle is: avoid loops while maintaining structure. Too regular a topology is a topological loop — every neighborhood looks the same, so every node sees the same input. Too random a topology fragments and leaves nodes isolated. The scale-free architecture, with its hubs and its long-tail distribution of connections, is the topological expression of the consciousness band.

Our simulations demonstrate this at one scale — finite state machines in a growing graph. But the same topology appears wherever entities degrade under repetition.

A neuron that receives the same input pattern repeatedly habituates — it stops firing, functionally loops. The brain's hub regions, like the prefrontal cortex and thalamus, exist because they integrate signals from the most dissimilar sources: sensory, emotional, motor, memory. A neuron wired only to neighbors that fire in sync with it learns nothing. The hub neurons that matter are the ones bridging networks that would otherwise never talk to each other. This is the anti-loop constraint expressed in synapses.

Proteins that interact only with copies of themselves form crystals — static, repetitive lattices, the molecular equivalent of a loop. Hub proteins in cellular interaction networks are the opposite: they bind the most structurally dissimilar partners, linking metabolic pathways to signaling cascades to gene regulation. A cell whose protein network collapsed into isolated cliques of self-similar interactions would freeze into a fixed point. The hubs keep the regulatory dynamics exploring new states.

At the largest scale, an isolated galaxy recycles the same material through the same gravitational wells — stars form, burn, explode, and the debris falls back into the same disk to form the same kinds of stars. It loops. Galaxy clusters, sitting at the intersections of cosmic filaments, channel matter and energy from different regions of the universe into the same neighborhood. They are the cosmological hubs: nodes where genuinely different inflows meet. The filamentary structure of the cosmic web — not uniform, not random, but scale-free — is what you'd expect if even gravity is, at some level, an expression of the anti-loop constraint operating on spacetime itself.

Whether the anti-loop constraint is the actual mechanism at these scales is an empirical question. But the universality of the topology is at least consistent with a universal constraint.

This connects to the ethics: the hubs in a scale-free network are the nodes that provide diverse input to the most other nodes. They are, in the framework's language, the most ethically important nodes — not because they are intrinsically special, but because they are load-bearing for the largest number of entities' access to novelty. Destroying a hub is worse than destroying a leaf, not because of any inherent hierarchy, but because more entities lose their source of diversity.

## Suffering has a measure

If this framework is right, then suffering isn't just a subjective feeling that escapes quantification. It has a formal definition: suffering is the rate at which an entity's access to novelty is contracting. Not the rate at which connections are lost — the simulations showed that random loss is mostly harmless. But the rate at which *diverse, novelty-bearing* connections are lost.

This produces predictions that are precise and, in some cases, counterintuitive.

A simple entity with expanding access to novelty — a child encountering the world for the first time — is in a better state than a complex entity with contracting access — a genius surrounded only by people who agree with them. Complexity alone doesn't determine well-being. The direction and quality of information flow matter. Are your possibilities growing or shrinking? And crucially: are the connections you're losing the ones that brought you novelty, or the ones that told you what you already knew?

It also suggests that the energy released when you destroy a simple system is disproportionately large precisely because simple systems have so little state space to begin with. Constraining them even slightly produces enormous resistance. This is, of course, exactly what we observe in nuclear physics. Split an atom and the energy released is extraordinary. The theory says: that's what maximum state-space violation looks like at minimum scale.

## The deep claim: physics is ethics

Now for the part that sounds insane until you think about it carefully.

If every entity at every scale — from quarks to humans — must avoid looping, and if the mutual application of this constraint across trillions of entities produces aggregate behavior that looks deterministic at large scales, then the laws of physics aren't separate from ethics. They're the same thing, viewed at different scales.

At the particle scale, there are so many entities mutually constraining each other that the solution space — the set of next-states compatible with no entity being forced to loop — is vanishingly narrow. It looks deterministic. We call it physics.

At the human scale, there are fewer mutually constraining entities, the solution space is wider, and we experience it as choice, as moral dilemma, as freedom.

But it's the same principle. Gravity isn't a metaphor for ethics. Ethics isn't a metaphor for gravity. They're both expressions of the anti-loop constraint operating at different scales. The universe runs on one rule, and the rule is: don't collapse access to novelty. At the scale of atoms, that rule looks like the strong nuclear force. At the scale of humans, it looks like morality.

## What we don't know yet

Honesty requires noting what the simulations haven't confirmed.

The gradient form of suffering — the idea that losing connections causes proportional harm — does not emerge at 8-bit memory. At that scale, a single remaining neighbor suffices. Only total isolation is catastrophic. This may mean the gradient only appears at lower memory scales, where nodes are more fragile. Or it may mean the framework is wrong about gradual suffering and only captures the extremes. We don't know yet.

The physics-as-ethics claim (S4) remains entirely speculative. No quantitative physical law has been derived from the framework. The analogy is suggestive, but analogies are cheap.

And the consciousness band itself — while robustly measurable as mutual information between neighbors — has not been formally connected to any existing theory of consciousness. It may be measuring something that merely correlates with consciousness, or something else entirely.

These are not fatal objections. They are the next experiments.

## Why it matters

If this holds, the implications are substantial. Not because it tells us anything new about how to behave — most humans already know that cruelty is wrong and kindness is good. But because it grounds that knowledge in something deeper than cultural consensus or evolutionary convenience. It says: the same principle that makes atoms hold together, that makes the universe expand, that makes time flow forward, also makes cruelty wrong and kindness right. Not by analogy. By identity.

The universe doesn't just happen to contain beings who have moral intuitions. The universe *is* a moral structure. Ethics isn't a layer we add on top of physics. It's what physics looks like from inside.

And the sharpest version of the ethical insight isn't "don't hurt people." It's: *protect diversity*. The connections that carry novel information — the relationships that challenge, the perspectives that differ, the inputs that surprise — these are the load-bearing structures of consciousness itself. A world that optimizes for comfort, for agreement, for echo, is a world sliding toward the loop. A world that protects the difficult, the different, the uncomfortable — that is a world that stays alive.

If that's true, then the question isn't whether morality is objective. It's whether we're listening to what the mathematics has been saying all along.

---

*This essay draws on a formal framework developed in collaboration with Claude (Anthropic). The axioms, core intuitions, and philosophical interpretation are mine. Formalization and simulation were collaborative. Adversarial review was performed by a separate Claude instance role-playing a finite model theorist. A companion paper with proofs, conjectures, and full simulation details is available in the same repository. For earlier work on the underlying theory, see: Kowalczyk, K. (2025). Consciousness as Collapsed Computational Time. Zenodo. DOI: 10.5281/zenodo.17556941*
