# M16 — Grounded mentor feedback composer

## Scope

M16 is a deterministic composition layer over already-qualified evidence:

```text
M3 engine evidence
+ M4 DecisionComparison
        ↓
M15 evaluation presentation

M8 TutorSession(compared)
+ exact M6 assessment/assertions
+ optional complete active-current M7 context
        ↓
compose_grounded_mentor_feedback
        ↓
m16.grounded-mentor-feedback.v1
        ↓
optional record_grounded_mentor_feedback
        ↓
existing M8 TutorExplanation transition
```

M16 does not run an engine, create a new M6 diagnosis, revise M7, select M9
training, mutate M11 longitudinal state, invoke an LLM, or claim tutoring efficacy.
Its first production surface is a versioned deterministic template composer with
strict evidence binding.

## Public API

```python
from chess_mentor_engine.feedback import (
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)

feedback = compose_grounded_mentor_feedback(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,  # optional
    created_at="2026-09-09T10:13:00-03:00",
)

updated_session, explanation, feedback = record_grounded_mentor_feedback(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    created_at="2026-09-09T10:13:00-03:00",
)
```

The schema version is:

```text
m16.grounded-mentor-feedback.v1
```

## Evidence binding

M16 does not accept a loose presentation JSON document and trust it. Before
composition it verifies:

1. the tutor session is exactly in `compared` state and has no existing explanation;
2. the TutorComparison content-addressed fingerprint and identity are valid;
3. optional TutorHypothesisContext and every active revision retain valid exact
   fingerprints and identities;
4. the supplied M4 DecisionComparison ID/fingerprint exactly matches the M6
   `decision_comparison_ref` already bound into the tutor comparison;
5. supplied root/played M3 analyses are among the exact analysis references already
   bound into the M6 reasoning context;
6. the objective reveal exposed the same exact M4 comparison and root analysis;
7. any supplied played-child PositionAnalysis was also exposed by that reveal;
8. feedback chronology does not predate the comparison or attached M7 context.

Only after those checks does M16 call the qualified M15 projection API again. If M15
rejects the M3/M4 relationship, M16 fails closed rather than composing prose from
inconsistent evidence.

## Feedback sections

The v1 template emits four bounded section kinds.

### Objective

The objective section derives only from M15/M4 semantics.

For exact comparable centipawn evidence it may state the exact mover-relative
centipawn difference. For bounded, partial, incompatible, or unavailable evidence it
explicitly says that no exact centipawn loss is claimed. Mate remains symbolic and
is never converted into an arbitrary centipawn sentinel.

M16 does not introduce `inaccuracy`, `mistake`, `blunder`, or other universal
move-quality thresholds.

### Reasoning

The reasoning section preserves the M6 assessment status and **every** qualified M6
assertion in the TutorComparison. It does not cherry-pick an assertion to make a
cleaner story.

The claim stays position-local. `unclear` and `unscorable` remain explicit, and a
non-clean measurement condition is shown rather than silently ignored.

### Learner context

This section appears only when a complete active-current M7 TutorHypothesisContext
is attached. Every active revision is included with its statement and scope.
Unresolved alternative notes and competing-hypothesis references remain visible.

The section explicitly describes M7 records as descriptive hypotheses, not causal
cognitive diagnoses or permanent learner traits.

### Reflection

M16 maps qualified M6 discrepancy codes to deterministic reflection questions. The
questions ask the learner to reconsider candidates, replies, continuations, or
missing rationale.

A reflection prompt is not an M9 intervention selection or training assignment.
M16 creates no intervention registry state and claims no learning effect.

## Identity and provenance

The feedback record contains:

```text
feedback_id
fingerprint
schema_version
exact tutor comparison ID/fingerprint
optional exact hypothesis-context ID/fingerprint
M15 presentation schema + fingerprint
versioned M16 policy + policy fingerprint
evidence references for every section
rendered content
created_at
claim_scope = session_local_grounded_feedback
```

`record_grounded_mentor_feedback` reuses the existing M8
`record_tutor_explanation` transition. The recorded M8 explanation provenance is:

```text
actor_kind = template
actor_id = m16-grounded-feedback
actor_version = 1
instruction_fingerprint = exact M16 policy fingerprint
run_id = feedback_id
```

The existing M8 TutorExplanation remains the state-machine authority for what
explanation was recorded in the session. The richer M16 feedback record is the
composition/provenance artifact returned to the caller.

## LLM boundary

M16 v1 deliberately does **not** call a model. A future model-backed surface may use
this contract as the grounding boundary, but model output must not silently replace
M6/M7 authority or weaken exact evidence references.

Therefore M16 qualification proves deterministic grounded composition, not model
quality, natural-language optimality, or empirical coaching benefit.

## Rejection coverage

Focused M16 suite:

```bash
python -m pytest tests/test_m16_grounded_mentor_feedback.py
```

It covers:

- deterministic exact feedback and exact evidence refs;
- preservation of every M6 assertion;
- recording through the native M8 explanation transition;
- complete active-current M7 context with explicit claim ceiling;
- reflection questions without training/intervention/mastery state;
- rejection before comparison;
- rejection of drifted M4 evidence;
- rejection of M3 analysis not bound into M6;
- rejection of objective analysis not exposed during reveal;
- rejection of tampered M7 context;
- rejection of feedback that predates its evidence context.

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`; skips are not an independent
engine pass. Pull-request CI is the merge gate.

## Boundaries

M16 explicitly does **not** implement:

- LLM/model invocation or free-form generative coaching;
- new engine analysis or evaluation semantics;
- automatic M6 discrepancy creation;
- automatic M7 hypothesis creation/revision;
- M9 intervention selection or training assignment;
- M10 efficacy inference or mastery claims;
- automatic M11 longitudinal mutation;
- web/desktop UI;
- authentication or hosted multi-user services;
- empirical tutoring-efficacy claims.
