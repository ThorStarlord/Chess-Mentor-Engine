# M8 — Evidence-Aware Tutor Session

**Status:** qualified implementation  
**Contract:** [ADR 0007](../decisions/0007-evidence-aware-tutor-session-contract.md)  
**Production package:** `src/chess_mentor_engine/tutoring/`

## Purpose

M8 turns the already-qualified evidence stack into one bounded, replayable interaction.
It does not create a new diagnostic theory or training policy. Its job is to make the
order in which information is shown to the player an executable product invariant.

The implemented path is:

```text
qualified M4 selected position
+ M5 PlayerDecisionContext
+ versioned M5 CaptureProtocol
        ↓
TutorSession(selected)
        ↓
exact M1 PositionContextPacket presentation
        ↓
M5 minimal response
        ↓
optional M5 standardized probe
        ↓
all planned pre-reveal responses frozen
        ↓
M5 objective-evidence reveal
        ↓
exact qualified M6 context + assessment + assertions
        ↓
optional complete active-current M7 ledger context
        ↓
provenance-bearing session-local explanation
        ↓
TutorSession(completed)
```

## Production surface

`chess_mentor_engine.tutoring` exports:

```text
TutorSession
TutorSessionEvent
TutorPositionPresentation
TutorComparison
TutorHypothesisContext
TutorExplanation
TutorExplanationProvenance
TutorSessionError

start_tutor_session
present_tutor_position
present_tutor_capture_stage
capture_tutor_response
freeze_tutor_response
reveal_tutor_objective_evidence
record_tutor_reasoning_comparison
attach_tutor_hypothesis_context
record_tutor_explanation
complete_tutor_session
```

## State machine

The bounded M8 v1 state vocabulary is:

```text
selected
presented
capturing
frozen
revealed
compared
explained
completed
```

Each transition appends a `TutorSessionEvent` with:

```text
sequence
kind
from_state
to_state
occurred_at
artifact_id
artifact_fingerprint
```

The event sequence is contiguous and the final event's `to_state` must equal the
snapshot's current `state`.

## Session identity and replay

A tutor-session lineage is content-addressed from:

- workflow version;
- exact M5 `PlayerDecisionContext` ID;
- exact M5 capture-protocol ID/fingerprint.

Each immutable session snapshot has a separate `snapshot_fingerprint` derived from the
complete canonical serialized state.

Identical event/artifact sequences replay to identical session snapshots.

## Pre-reveal boundary

M8 v1 accepts only:

```text
MINIMAL_RESPONSE
```

or:

```text
MINIMAL_RESPONSE
→ STANDARDIZED_PROBE
```

Both are pre-reveal. Their permitted interaction classes are observation and
diagnostic probing respectively.

The implementation explicitly rejects a pre-reveal prompt marked
`tutoring_intervention`.

## Deterministic position presentation

`present_tutor_position` requires the exact `PositionContextPacket` already referenced
by the M5 context. The packet fingerprint is revalidated before display.

The built-in v1 renderer exposes only deterministic orientation:

```text
move number + side to move
FEN
ASCII board
```

It has no parameter through which engine analysis, M4 selection rationale, M6
assertions, or M7 hypotheses can enter the pre-reveal position surface.

Presentation is also recorded as M5 `POSITION_CONTEXT_SHOWN` exposure provenance.

## Participant evidence remains M5-owned

M8 delegates prompt presentation, response capture, freeze, exposure tracking, and
objective reveal to the qualified M5 state machine.

Therefore:

- raw response remains participant-authored M5 evidence;
- structured response remains explicit participant input;
- freezes remain M5 freeze authority;
- objective reveal remains M5 reveal authority;
- M8 cannot rewrite earlier responses after reveal.

M8 enters `frozen` only after every planned pre-reveal stage is frozen.

## M6 comparison binding

A comparison cannot be attached before objective reveal.

M8 revalidates the exact M6:

```text
ReasoningDiscrepancyContext
ReasoningDiscrepancyAssessment
ReasoningDiscrepancyAssertion[]
```

The M6 context must cite the **current revealed M8 capture snapshot**, including the
exact `capture_session_id` and `snapshot_fingerprint`.

This prevents a stale pre-reveal M6 context from being attached after reveal.

M8 also checks assessment/assertion identity, policy consistency, participant,
position/game identity, and chronology. It does not create a stronger discrepancy
claim than M6 already produced.

## M7 learner context binding

M7 context is optional. When supplied, M8 requires:

```text
exact HypothesisLedgerSnapshot
+ every active entry's exact current HypothesisRevision
```

The snapshot and revision content-addressed identities are revalidated.

This is deliberately stronger than accepting a list of convenient hypotheses: the
caller cannot omit an active current hypothesis merely because it conflicts with the
story an explanation wants to tell.

Retired/superseded lineage history remains preserved inside the M7 snapshot and is not
reclassified by M8.

## Explanation provenance

M8 explanation text is stored only after comparison and includes:

```text
exact TutorComparison ID/fingerprint
optional exact TutorHypothesisContext ID/fingerprint
actor kind: human | model | template
actor ID/version
instruction fingerprint
run ID
timestamp
rendered text
```

Its claim scope is fixed to:

```text
session_local_evidence_explanation
```

This means M8 can prove **what explanation was shown from what evidence context**. It
does not prove that the explanation was pedagogically optimal or effective.

## Qualification suite

`tests/test_m8_qualification.py` exercises the complete bounded feature surface.

The focused cases prove:

1. deterministic session creation with no accidental reveal;
2. deterministic position-only presentation;
3. rejection of a packet not bound to the M5 context;
4. rejection of pre-reveal tutoring-intervention prompts;
5. reveal blocked until all planned freezes exist;
6. immutable prior session snapshots;
7. comparison blocked before objective reveal;
8. M6 comparison must cite the exact final revealed capture snapshot;
9. M7 context must include every active current ledger revision;
10. explanation is post-comparison and provenance-bearing;
11. the full workflow reaches `completed` in the frozen event order;
12. identical full-session replay is deterministic;
13. serialized M8 state contains no M9 training/intervention/mastery authority.

The suite is run inside the repository's normal CI together with all prior M1–M7 tests,
Ruff, and the independent external Stockfish integration witness.

## Claim ceiling after M8

The repository may now claim that it can deterministically orchestrate a bounded local
tutor session in which:

- the exact selected position is presented without engine/diagnostic leakage;
- player reasoning evidence is captured and frozen before reveal;
- qualified objective evidence is revealed afterward;
- exact M6 discrepancy evidence is attached only to the matching final evidence state;
- complete current M7 hypothesis context can be attached without cherry-picking;
- an explanation can be recorded with exact author/evidence provenance;
- the complete interaction is immutable and replayable.

M8 still does **not** establish:

- which learner hypotheses are training-eligible;
- which intervention should be selected;
- that an exercise is appropriate;
- that an explanation or intervention is effective;
- learning;
- transfer;
- mastery.

Those claims remain outside M8. M9 is the next layer allowed to define explicit
training-intervention records and selection policy.
