# Pedagogical Metadata — CKO v1

Pedagogical metadata makes a chess concept teachable without turning the ontology
into learner-state authority.

## Optional metadata

A concept may define:

```text
prerequisites
recognition questions
common misconceptions
training modes
learner band
```

For example, `tactic.deflection` can carry a recognition question such as:

> Which opposing piece is performing a critical defensive job?

The question is instructional metadata. It is not evidence that a particular learner
failed to identify that defender.

## Learner bands are heuristic

Labels such as `foundational_to_intermediate` or `intermediate` are curriculum aids,
not objective Elo laws. They must not be interpreted as claims that all players in a
rating band have or lack the concept.

## Prerequisites are teaching dependencies

A prerequisite means that a concept is usually easier to teach when another concept
is available. It does not create a causal cognitive model of the learner.

Future examples may include:

```text
tactic.deflection
    prerequisite: defender identification

evaluation.pawn_structure
    prerequisite: isolated/doubled/passed pawn features

plan.create_second_weakness
    prerequisite: stable weakness recognition
```

## Recognition cues versus detector rules

Pedagogical recognition questions are for people. Detector implementations require
separate, testable rules and explicit authority classes.

The ontology must not turn a sentence such as “look for loose pieces” directly into
a deterministic detector without a separate contract defining exactly what “loose”
means computationally.

## Connection to M9/M10

Pedagogical metadata can later help an intervention-matching system propose suitable
M9 interventions. It does not select them automatically.

The intended chain remains:

```text
qualified learner evidence
        ↓
supported teaching need
        ↓
ontology concept + pedagogy metadata
        ↓
candidate intervention
        ↓
M9 applicability / selection authority
        ↓
M10 practice and transfer evidence
```

## Anti-shortcut rule

Never infer:

```text
position contains tactic.fork
-> learner needs fork training
```

The player may have seen the fork, rejected it correctly, or made an unrelated
mistake. Participant reasoning and recurrence evidence remain necessary before the
concept can legitimately shape personalized training.
