# M46 — Adaptive Socratic Tutor

M46 is a deterministic **next-pedagogical-action proposal** layered over the existing M8 tutor-session lifecycle and current learner-intelligence context.

## Purpose

The product question is:

> Given the exact tutor-session exposure state and the current learner/tutor plan, what bounded question, hint, reveal, reflection, or no-op should be proposed next?

M46 does not execute tutoring actions. M8 remains the authority for capture, freeze, objective reveal, comparison, explanation, and completion transitions.

```text
M8 exact tutor-session snapshot
+ M44 exact learner-progress view
+ optional exact M45 mentor-queue item
+ optional exact M42 transfer plan
+ versioned M46 pedagogical policy
-> m46.adaptive-tutor-proposal.v1
-> existing M8 execution boundary
```

## Critical exposure invariant

M46 preserves the evidence distinction:

```text
unassisted baseline response
!= assisted follow-up response
!= post-reveal reflection
```

Before M8 reaches `frozen`, M46 v1 proposes only `CONTINUE_BASELINE_CAPTURE`. It does not inject a hint, concept cue, tactical relation, or engine reveal into the pre-reveal measurement window.

After baseline evidence is frozen, M46 may propose an assisted action or objective reveal according to the current learner action. After objective evidence has already been revealed, new responses are explicitly labeled `post_reveal_reflection` rather than baseline evidence.

## Bounded action vocabulary

The v1 public vocabulary includes:

```text
CONTINUE_BASELINE_CAPTURE
ASK_CANDIDATE_MOVES
ASK_THREATS
ASK_DEFENDER_ROLE
ASK_EVALUATION_FACTORS
ASK_PLAN
GIVE_MINIMAL_HINT
GIVE_CONCEPT_HINT
GIVE_DIRECTIONAL_HINT
REVEAL_TACTICAL_RELATION
REVEAL_ENGINE_LINE
ASK_REFLECTION
NO_FURTHER_ACTION
```

Not every action is selected by the default v1 policy. The vocabulary is explicit so later policy revisions can add bounded behavior without changing the authority model.

## Default v1 routing

### Before M8 freeze

```text
selected / presented / capturing
-> CONTINUE_BASELINE_CAPTURE
```

Adaptive intervention remains blocked until the qualified M8 capture protocol has frozen all planned pre-reveal evidence.

### Frozen learner evidence

- `COLLECT_NEW_EVIDENCE`, `CHALLENGE_HYPOTHESIS`, or `PRESENT_CONTROL` -> `REVEAL_ENGINE_LINE` under the existing M8 reveal boundary;
- `TEACH_CONCEPT` + available ontology recognition question -> `GIVE_CONCEPT_HINT` using the exact recognition cue already present in M44/K0-K7;
- `TEACH_CONCEPT` without a recognition question -> `GIVE_MINIMAL_HINT`;
- `ASSIGN_PRACTICE` -> `GIVE_MINIMAL_HINT`;
- near/far transfer action -> require an exact selected M42 plan, then `GIVE_MINIMAL_HINT`;
- `WAIT_FOR_REAL_GAME_EVIDENCE` -> `NO_FURTHER_ACTION` because a tutor session cannot manufacture real-game evidence.

### After objective reveal

`revealed`, `compared`, and `explained` states may propose `ASK_REFLECTION`. The response class is explicitly `post_reveal_reflection`.

### Completed session

`completed -> NO_FURTHER_ACTION`.

## Model-language boundary

M46 v1 is deterministic and records:

```text
execution_authority = proposal_only
model_language = not_generated
mastery = not_established
```

The default templates and ontology recognition questions are deterministic source material, not model-authored prose.

K6/M19 model-language integration is deliberately **not** added merely because the capability exists. If a later concrete consumer requires fluent rendering of one exact M46 action, it may bind the already-qualified deterministic action/context into K6/M19 while preserving M16/M19/M20 authority boundaries.

## M45 mentor-queue context

An M45 queue/item is optional context. If supplied, M46 validates:

- exact queue identity;
- participant identity;
- item membership in that queue;
- exact game/position match with the current M8 tutor session;
- selected hypothesis compatibility when the queue item is hypothesis-scoped.

M45 priority does not grant M46 execution authority.

## M42 transfer context

For M40 near/far-transfer intent, an exact M42 plan is required before M46 proposes a transfer tutoring hint. M46 validates participant, hypothesis, current revision, M40 plan identity, and exact selected position against the M8 tutor position.

```text
M42 planned position != M10 transfer outcome
M46 hint != completed transfer test
```

## Ontology policy

M46 v1 reuses existing K0-K7 recognition questions already projected into M44. No generic K8 ontology expansion is required.

The product-pulled ontology rule remains:

```text
concrete tutor consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum ontology extension
-> qualify ontology + consumer together
```

## Rejection cases

M46 fails closed for:

- tampered M8 tutor-session snapshot;
- participant mismatch between M8 and M44;
- selected hypothesis missing from M44;
- M45 queue supplied without its exact item, or vice versa;
- M45 queue/item identity or position mismatch;
- M42 plan identity, participant, hypothesis, revision, M40-plan, or position mismatch;
- transfer action without an exact M42 plan;
- tampered M46 policy or replayed proposal.

Most importantly, M46 never bypasses M8's clean pre-reveal capture boundary.
