# M45 — Batch Games -> Mentor Queue

M45 turns an exact bounded M4D diagnostic candidate batch into a small participant-scoped **review-priority proposal** using existing learner, contradiction/control, transfer, semantic, and objective evidence.

## Purpose

The product question is:

> Given a bounded recent game batch, which moments deserve this participant's attention now?

M45 is intentionally not another engine selector or learner model.

```text
M4D diagnostic candidate batch
+ explicit participant batch-scope binding
+ exact M44 learner-progress view
+ optional exact M42 transfer/retest plans
+ versioned M45 queue policy
-> m45.mentor-queue.v1
```

## Participant binding

M4D's diagnostic batch is participant-agnostic objective-selection evidence. M45 therefore requires an explicit content-addressed `m45.mentor-queue-batch-scope.v1` that binds:

- one participant ID;
- the exact M4D batch ID and digest;
- the exact game set represented by that batch;
- explicit provenance refs establishing the participant-local batch scope.

M45 does not infer participant ownership from engine evidence.

## Ranking dimensions

Each queue item exposes separate ordinal dimensions in `0..3` rather than a hidden scalar score:

- M40 action alignment;
- contradiction/control value;
- transfer value;
- learner relevance;
- uncertainty-reduction value;
- bounded objective importance;
- novelty/independence;
- semantic diversity.

These are transparent product-policy ordinals, not calibrated probabilities or empirically optimal teaching weights.

The default ranking is lexicographic and deliberately places learner-decision value ahead of ordinary objective importance. A useful contradiction/control or current transfer candidate can therefore outrank a larger centipawn-loss-only position.

Objective importance is derived only from already-qualified M4C signals. M45 does not recompute engine evaluation or sort directly by centipawn magnitude.

## Composition rules

M45 may link an M4D candidate to:

- exact M44 M7C evidence units at the same game/position;
- exact M44 M43 acquisition candidates at the same game/position;
- exact M42 eligible or selected transfer candidates at the same game/position.

Concept IDs are descriptive context from those exact qualified sources. Concept occurrence never becomes a learner-weakness claim.

The queue policy also enforces a bounded maximum per game and may prefer previously unrepresented concept context among otherwise equally ranked candidates.

## Authority boundary

Every M45 queue records:

```text
decision_authority = review_priority_proposal_only
learner_effect = not_established
mastery = not_established
```

Preserve:

```text
M45 queue rank != objective chess severity
M45 queue rank != M7/M7C learner inference
M45 queue item != M9 intervention selection
M45 transfer relevance != M10 transfer outcome
concept occurrence != participant weakness
review priority != execution authority
```

## Rejection cases

M45 fails closed for:

- batch-scope/M4D batch identity drift;
- participant mismatch between scope and M44;
- tampered M44 view identity;
- tampered or cross-participant M42 plan;
- M42 plan bound to another M40 plan/revision;
- duplicate transfer-plan identities;
- tampered queue policy;
- tampered replayed queue.

An objective-only M4D candidate remains eligible for the queue when no learner-specific linkage exists, but it is explicitly represented with zero learner relevance rather than being converted into a learner claim.

## Ontology policy

M45 consumes concept IDs already carried by M44/M43/M42. It does not need a new ontology schema or generic K8 expansion. Extend the ontology only if a concrete downstream queue requirement proves K0-K7 cannot represent a needed distinction safely.
