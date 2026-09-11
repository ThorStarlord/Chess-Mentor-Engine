# M36 — Deterministic Learner-State Read Model

M36 is a participant-scoped, content-addressed read model over already-qualified
learner evidence. It exists to answer the operational question:

> What does the repository currently know about this participant?

It does not create a new learner authority.

## Inputs

M36 may combine:

- one exact M11 `LearnerStateSnapshot`;
- the exact current M7 `HypothesisRevision` for every M11 trajectory;
- zero or more M9 `InterventionSelectionDecision` records for those exact current
  revisions;
- zero or more K7 `HypothesisKnowledgeProjection` sidecars for those exact current
  revisions.

## Output

`m36.learner-state-read-model.v1` preserves, per current hypothesis:

- stable hypothesis/revision identity;
- current hypothesis statement and scope;
- unresolved alternative notes;
- M7C status and exact assessment reference when present;
- M11 lifecycle state;
- current M10 practice / near-transfer / far-transfer / real-game status;
- exact M9 selection decision references and selected intervention definitions;
- optional K7 concept IDs plus covered/uncovered recurrence-unit counts.

The read model is deterministic for identical inputs and `created_at`, and carries an
exact source M11 snapshot reference.

## Authority boundary

```text
M7/M7C learner inference
+ M9 intervention selection
+ M10 outcome evidence
+ M11 longitudinal projection
+ optional K7 chess semantics
        |
        v
M36 deterministic read model
```

M36 does **not**:

- create, revise, retire, or reactivate an M7 hypothesis;
- reclassify M7C recurrence evidence;
- select a new M9 intervention;
- convert M10 evidence into mastery or causality;
- infer participant cognition from ontology concepts;
- turn a K7 concept occurrence into a learner weakness;
- write to M11.

The core invariant remains:

```text
read model != learner-state mutation authority
```

## Rejection behavior

Construction fails closed for:

- missing or stale current M7 revisions;
- extra non-current revisions;
- M9 decisions for a different participant or non-current revision;
- duplicate M9 decision IDs;
- duplicate K7 projections for the same current revision;
- K7 projections bound to a different revision;
- non-current K7 projection inputs;
- malformed timestamps or tampered rebuilt output.

## Qualification

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Pull-request CI plus the independent Stockfish job remains the merge authority.
