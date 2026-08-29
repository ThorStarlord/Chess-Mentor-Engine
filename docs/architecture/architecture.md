# Architecture hypothesis

> **Status: architectural hypothesis - not yet frozen**

Chess Mentor Engine may eventually use a flow like this:

```text
Game ingestion
        ↓
Chess analysis
        ↓
Evidence extraction
        ↓
Learner modeling
        ↓
Pedagogical diagnosis
        ↓
Learning planning
        ↓
Practice / interaction
        ↓
Evaluation
        ↓
Learner-state update
```

This is a direction for discovery, not a committed implementation plan.

## Tentative system split

1. **Deterministic chess layer.** Legal moves, board states, engine analysis, tablebase results, and other objective chess evidence.
2. **Learner-state and application layer.** Provenance, history, evidence aggregation, progress state, and persistence rules.
3. **Model-assisted tutoring layer.** Explanations, Socratic interaction, misconception hypotheses, lesson framing, and adaptive presentation.

The boundaries and ownership of these responsibilities need validation.

## Candidate future concepts

Game, Position, Move Decision, Chess Evidence, Player, Learner Profile, Skill or Concept, Mistake Pattern, Misconception Hypothesis, Diagnosis, Learning Goal, Intervention, Exercise, Attempt, Mastery Evidence, Review, and Provenance are candidate concepts for future domain work.

These are discovery candidates. Their inclusion here does not establish them as production domain objects.

One possible future conceptual hierarchy is:

```text
Chess Knowledge
Learner Model
Learning Plan
Practice
Instruction
```

This hierarchy should not be copied mechanically from another system or accepted without domain modeling.

