# Product principles

> **Implementation status authority:** [`repository-build-status.md`](repository-build-status.md)  
> **Product hypothesis:** [`product-definition.md`](product-definition.md)  
> **Future planning:** [`chess-mentor-engine-repository-build-plan.md`](chess-mentor-engine-repository-build-plan.md)

These principles guide product and architecture decisions. They do not themselves
claim that a capability is implemented or qualified.

### Evidence before diagnosis

Do not label a player with a persistent weakness from a single mistake when longitudinal evidence is required.

### Objective chess truth should come from objective tools

Do not ask an LLM to substitute for chess-engine or tablebase truth where deterministic tools are appropriate.

### Hypothesis is not fact

Distinguish player-declared belief, system hypothesis, evidence-supported diagnosis, and demonstrated competency.

### Teach the player, not merely the position

Position analysis is evidence for tutoring, not necessarily the final product.

### Recurrence matters

Repeated decision patterns are more pedagogically important than isolated centipawn loss.

### Pedagogy may differ from engine optimization

The best teaching intervention is not always simply showing the engine's top move.

### Persistent learning state must remain inspectable

The learner should eventually be able to understand why the system believes something about them.

### Progressive disclosure

Expose only the amount of chess and learner-model complexity useful for the current decision.

### Preserve provenance

Important diagnoses and progression claims should eventually be traceable to evidence.

### Avoid premature architecture

Do not create domain abstractions merely because they sound plausible.
