# M21 — Diagnostic Candidate → Tutor Session Orchestration

## Purpose

M21 closes the bounded workflow gap between an exact M18-selected diagnostic
candidate and the existing M5/M8 participant-evidence tutor loop.

The bridge is intentionally narrow:

```text
M18 DiagnosticCandidateBatch
+ exact selected DiagnosticCandidate
        ↓
explicit participant candidate choice
+ separate explicit capture consent
        ↓
m21.candidate-tutor-authorization.v1
        ↓
exact canonical game + root position
        ↓
M5 PlayerDecisionContext
        ↓
M8 TutorSession(state = selected)
        ↓
m21.candidate-tutor-launch.v1
```

M21 does not run an engine, choose a diagnostic candidate, expose objective
selection rationale, collect a participant response, create an M6 discrepancy,
create or revise an M7 learner hypothesis, select M9 training, or generate mentor
feedback.

## Public API

```python
from chess_mentor_engine.tutoring import (
    record_candidate_tutor_authorization,
    start_candidate_tutor_session,
)

authorization = record_candidate_tutor_authorization(
    participant_id="P01",
    candidate=candidate,
    batch=batch,
    selection_decision="selected",
    capture_consent="granted",
    recorded_at="2026-09-10T10:00:00-03:00",
)

context, session, launch = start_candidate_tutor_session(
    authorization=authorization,
    candidate=candidate,
    batch=batch,
    game=canonical_game,
    position=canonical_root_position,
    capture_protocol=capture_protocol,
    created_at="2026-09-10T10:01:00-03:00",
)
```

The authorization and launch schemas are:

```text
m21.candidate-tutor-authorization.v1
m21.candidate-tutor-launch.v1
```

## Explicit selection and consent

Candidate choice and evidence-capture consent are separate fields.

Allowed candidate decisions:

```text
selected
declined
```

Allowed capture-consent decisions:

```text
granted
declined
```

A tutor session starts only for `selected + granted`. `selected + declined` is a
valid authorization record but cannot start M5/M8 capture. `declined + granted` is
invalid because capture consent cannot authorize a candidate the participant did
not select.

The authorization record is participant-authored and content-addressed. Recording
it creates no M5 capture state and no M8 tutor state by itself.

## Exact M18 binding

M21 does not accept an arbitrary object that merely repeats a candidate ID.
Before authorization or launch it verifies:

1. every retained M4 selection signal still has its content-addressed signal ID;
2. the candidate ID still matches the exact M4 candidate identity payload;
3. the M18 batch ID still matches its deterministic batch identity payload;
4. the candidate policy equals the batch policy;
5. the candidate is exactly equal to the unique selected batch member with that ID;
6. the candidate remains present in the batch source-candidate set;
7. authorization fingerprints exactly bind the full candidate and batch payloads.

This rejects same-ID signal/content drift as well as candidate, batch, or
authorization tampering.

## Canonical game and position binding

The bridge accepts the exact canonical `CanonicalGame` and root
`CanonicalPosition`, not a caller-authored `PositionContextPacket`.

Before creating M5 state, M21 verifies that:

- candidate game and position IDs match the supplied canonical records;
- the supplied position exactly equals `game.positions[position.ply_index]`;
- candidate source SHA and game semantic fingerprint match the canonical game;
- candidate root/played ply provenance matches the canonical root;
- candidate child-position provenance matches the canonical child.

M21 then derives the `PositionContextPacket` itself with the qualified deterministic
M1 context builder. This prevents altered board/display context from being injected
through the orchestration boundary.

## M5/M8 handoff

After successful authorization and canonical binding, M21 calls the existing
qualified producers:

```text
record_player_decision_context
start_tutor_session
```

The generated M5 `session_id` is derived from the exact authorization ID, so repeated
execution with identical inputs is deterministic.

The M21 bridge stops immediately after M8 starts. The resulting tutor session must
still be:

```text
state = selected
position_presentation = None
comparison = None
hypothesis_context = None
explanation = None
```

The caller must continue with the existing M8 sequence beginning with
`present_tutor_position`.

## Pre-reveal information boundary

M21 authorization contains only participant identity, exact candidate/batch
references, the explicit choice/consent decisions, chronology, and claim scope. It
does not serialize M18 selection signals or engine-derived selection rationale into
the authorization record.

Applications should therefore collect candidate choice without revealing engine
scores, selection rationale, expected discrepancies, or other objective evidence
that would violate the M5/M8 pre-reveal measurement boundary. If an application
exposes such information, that exposure must be handled under the existing M5
contamination/deviation semantics rather than treated as clean pre-reveal capture.

M21 software qualification cannot prove what an external UI actually showed the
participant.

## Launch provenance and authority ceiling

The content-addressed launch record binds:

- exact authorization ID/fingerprint;
- exact candidate ID/full-payload fingerprint;
- exact batch ID/full-payload fingerprint;
- exact M5 PlayerDecisionContext ID/fingerprint;
- exact initial M8 TutorSession ID/snapshot fingerprint/state;
- launch chronology.

Its claim scope is:

```text
participant_authorized_candidate_to_tutor_start
```

The launch record explicitly states that M21 created only:

```text
m5_player_decision_context
m8_tutor_session_selected
```

and did not create M6 reasoning-discrepancy authority, M7 learner-hypothesis
authority, M9 training selection, M10 outcome claims, M11 longitudinal mutation,
or mentor explanation authority.

## Rejection coverage

Focused suite:

```bash
python -m pytest tests/test_m21_diagnostic_candidate_tutor_orchestration.py
```

It covers:

- deterministic participant authorization;
- authorization without implicit M5/M8 side effects;
- exact authorized M5/M8 launch;
- deterministic launch identity;
- explicit no-M6/M7/training authority boundary;
- selected candidate without capture consent;
- declined candidate;
- invalid declined + granted consent combination;
- same-ID selection-signal content drift;
- candidate identity/provenance drift;
- batch identity drift;
- rehashed authorization source drift;
- authorization fingerprint tampering;
- canonical-game semantic mismatch;
- noncanonical position copies;
- launch chronology violations;
- invalid M8 capture protocols.

Full repository gate remains:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The first three commands are repository-only. The independent Stockfish witness is
provided by pull-request CI. M21 itself performs no live model/provider calls and
requires no production credentials.

## Explicit non-claims

M21 does not establish or automate:

- which candidate a participant ought to study;
- a causal cognitive diagnosis or permanent learner trait;
- M6 discrepancy derivation;
- M7 hypothesis creation, revision, or recurrence;
- M9 training eligibility or selection;
- model coaching or model-output evaluation;
- tutoring effectiveness, transfer, or mastery;
- correctness of external UI disclosure/consent behavior;
- authentication, hosted persistence, deployment, or production QA.

M21 is orchestration, not inference. It makes the handoff from selected diagnostic
evidence into the existing participant-evidence workflow explicit, inspectable, and
fail-closed.
