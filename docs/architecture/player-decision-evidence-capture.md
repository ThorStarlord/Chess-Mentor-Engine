# M5C — Player Decision Evidence Capture/Freeze State Machine

## Status

**M5C — Player Decision Evidence Capture/Freeze State Machine is qualified. M5Q has not started. M6 remains unauthorized.**

M5C implements only the deterministic interaction-sequencing layer around the qualified M5B immutable evidence records. It does not declare M5 as a whole qualified and does not implement Reasoning Discrepancy, recurrence, learner hypotheses, tutoring decisions, pedagogy, transfer, or mastery.

## Qualified boundary

The M5C implementation adds:

```text
src/chess_mentor_engine/evidence/capture.py
```

and exposes the bounded API through:

```text
src/chess_mentor_engine/evidence/__init__.py
```

with focused qualification coverage in:

```text
tests/test_player_evidence_capture.py
```

The qualified transition surface is:

```text
CaptureStageSpec
CaptureProtocol
EvidenceCaptureSession
ProtocolDeviation
EvidenceAmendment

define_capture_protocol(...)
start_capture_session(...)
present_capture_stage(...)
capture_stage_response(...)
freeze_stage_response(...)
record_capture_exposure(...)
record_capture_deviation(...)
append_evidence_amendment(...)
reveal_objective_evidence(...)
```

## Capture architecture

M5C composes the M5B records rather than replacing them:

```text
CaptureProtocol
+ PlayerDecisionContext
        |
        v
EvidenceCaptureSession snapshot
        |
        v
PromptPresentation
        |
        v
PlayerResponseEvidence
        |
        v
EvidenceFreeze
        |
        +--> optional later pre-reveal stage(s)
        |
        v
ObjectiveEvidenceReveal
        |
        +--> optional post-reveal stage(s)

ExposureEvent ---------> information-state provenance
ProtocolDeviation -----> sequence / contamination provenance
EvidenceAmendment -----> append-only clarification of frozen evidence
```

Every transition returns a new immutable `EvidenceCaptureSession` snapshot. Earlier snapshots and the underlying M5B records are not mutated.

## Versioned capture protocol

`CaptureProtocol` gives stage sequencing material identity. It pins:

```text
protocol name
protocol version
ordered stage IDs
stage kinds
prompt-definition IDs
stage phase: pre_reveal | post_reveal
```

Material protocol changes therefore produce a different protocol fingerprint and ID.

A protocol must contain at least one pre-reveal stage. Pre-reveal stages cannot appear after post-reveal stages in the protocol definition.

This keeps stage order and prompt identity explicit rather than allowing the runtime to infer an experiment shape from prompt text.

## Strict rejection versus evidence preservation

The M5A contract requires clean protocols to reject invalid transitions while preserving real-world deviations rather than erasing evidence. M5C implements this through two explicit modes:

```text
violation_mode = "reject"
→ reject a transition that would violate the clean protocol

violation_mode = "preserve"
→ keep the evidence
→ append ProtocolDeviation
→ derive contamination from the deviation ledger
```

Preservation mode does not relabel deviating evidence as clean. It makes the deviation auditable.

The initial deviation surface includes:

```text
STAGE_OUT_OF_ORDER
STAGE_PRESENTED_BEFORE_PRIOR_FREEZE
POST_REVEAL_STAGE_BEFORE_REVEAL
PRE_REVEAL_STAGE_AFTER_REVEAL
OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES
INTERVENTION_LIKE_PROMPT
PROHIBITED_PRE_REVEAL_EXPOSURE
TIMESTAMP_ORDER_VIOLATION
OTHER
```

`EvidenceCaptureSession.contaminated` is derived from append-only deviations whose `contaminates_pre_reveal` value is true. There is no independently mutable clean/dirty flag.

## Stage-order and freeze gates

For a clean two-stage pre-reveal protocol, M5C enforces:

```text
A1 prompt presented
→ A1 response captured
→ A1 frozen
→ A2 prompt presented
→ A2 response captured
→ A2 frozen
→ objective evidence revealed
```

A later pre-reveal stage cannot be presented cleanly while an earlier required stage remains unfrozen.

A response requires an existing presentation for the same planned stage, and one planned stage cannot silently receive multiple mutable replacement responses.

A freeze requires the captured response and can occur only once for the stage. The freeze continues to use the M5B `EvidenceFreeze` record as the sole freeze authority.

## Objective-evidence reveal gate

`reveal_objective_evidence(...)` checks the protocol's complete pre-reveal stage set.

In strict mode:

```text
missing required pre-reveal freeze
→ objective reveal rejected
```

In preservation mode:

```text
early objective reveal
→ reveal evidence retained
→ OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES recorded
→ session marked contaminated through deviation provenance
```

A successful objective reveal also appends an `ENGINE_EVIDENCE_SHOWN` exposure event. Later presentations therefore inherit explicit evidence that objective engine information was already available.

M5C records evidence visibility and sequence validity only. It does not interpret what the objective evidence means about the player's cognition.

## Pre-reveal and post-reveal separation

Protocol stages explicitly carry a `pre_reveal` or `post_reveal` phase.

A post-reveal stage is rejected before objective evidence exists in strict mode. Conversely, a pre-reveal stage presented after objective reveal is rejected or preserved with explicit deviation provenance.

This prevents post-engine reflection from silently becoming pre-engine reasoning evidence.

## Exposure and instrument-awareness handling

M5C preserves M5A's rule:

```text
instrument awareness
!= automatic contamination
```

An explicit `INSTRUMENT_AWARENESS_RECORDED` event remains provenance. It does not by itself imply that the evidence is invalid or clean.

The initial pre-reveal prohibited-exposure set is:

```text
ENGINE_EVIDENCE_SHOWN
SELECTION_RATIONALE_SHOWN
EXPECTED_DISCREPANCY_SHOWN
PRIOR_REPORT_SHOWN
EXTERNAL_ANALYSIS_REPORTED
FACILITATOR_HINT
```

When one of these occurs before required pre-reveal freezes are complete, M5C preserves the `ExposureEvent` and appends `PROHIBITED_PRE_REVEAL_EXPOSURE` rather than deleting the evidence.

## Observation, probing, and intervention boundary

M5C preserves the M5A separation:

```text
observation
!= diagnostic probing
!= tutoring intervention
```

A prompt whose interaction class is `tutoring_intervention` is outside the clean initial pre-reveal capture boundary. Strict mode rejects its presentation. Preservation mode retains the presentation while recording `INTERVENTION_LIKE_PROMPT`.

This is provenance about interaction conditions, not an evaluation of whether the intervention is pedagogically effective.

## Append-only amendments

`EvidenceAmendment` implements the frozen M5A correction rule without mutating participant evidence.

An amendment requires:

```text
original PlayerResponseEvidence
+ original EvidenceFreeze
+ new participant-authored clarification
+ amendment submission timestamp
+ explicit reason
```

The original response and response fingerprint remain unchanged. An amendment cannot claim a timestamp earlier than the original freeze.

This preserves the distinction:

```text
original frozen evidence
!= later clarification
```

## Timestamp provenance

M5C retains timezone-aware timestamp validation and adds transition-order checks for presentation, response, amendment, and reveal events.

A timestamp-order violation can be rejected or, where preservation is appropriate, retained with `TIMESTAMP_ORDER_VIOLATION`. M5C does not silently rewrite timestamps to make a sequence appear clean.

## Deterministic session snapshots

`EvidenceCaptureSession` is a frozen dataclass. Its snapshot fingerprint is derived from canonical serialization of the full current ledger state, including:

```text
context
capture protocol
presentations
responses
freezes
exposures
amendments
deviations
objective reveal
```

Replaying an identical event sequence over identical upstream evidence produces the same capture-session identity and snapshot fingerprint.

## Focused qualification tests

`tests/test_player_evidence_capture.py` contains 20 M5C-focused tests covering:

1. deterministic/material capture-protocol identity;
2. rejection of a pre-reveal protocol stage ordered after a post-reveal stage;
3. clean minimal-only response/freeze/reveal path;
4. clean two-stage requirement for A1 freeze before A2;
5. preservation of early A2 with explicit deviation;
6. strict reveal blocking until every required pre-reveal freeze exists;
7. preservation of early objective reveal with explicit deviation;
8. post-reveal stage blocked before reveal and allowed afterward;
9. preservation of a pre-reveal stage presented after early reveal;
10. response requires presentation and remains unique per planned stage;
11. timestamp-order violation preserved without rewriting source timestamps;
12. freeze requires a response and cannot repeat;
13. prohibited pre-reveal exposure preserved and marked contaminating;
14. instrument awareness preserved without automatic contamination;
15. intervention-like prompt rejected or preserved as deviation;
16. amendment requires frozen original and never replaces it;
17. amendment timestamp cannot precede original freeze;
18. explicit manual deviation can be non-contaminating when warranted;
19. deterministic capture-session replay/snapshot identity;
20. frozen session and transition-record immutability.

## Superseded qualification attempt

The first PR candidate was:

```text
6dbaa5d095856d25dce5ad32051dac68876c795a
```

Its behavioral suite passed completely:

```text
142 passed
8 intentionally skipped external-engine tests in the normal suite
all 20 M5C tests passed
```

Ruff found only five E501 line-length violations in `capture.py`. No behavioral contract was weakened or changed. A style-only replacement head wrapped those lines and requalified from scratch.

## Exact qualification evidence

### Exact qualified M5C candidate

```text
bf26496818aa175db840061370f2e9b40d5f3b3b
```

PR #20 changed exactly:

```text
src/chess_mentor_engine/evidence/__init__.py
src/chess_mentor_engine/evidence/capture.py
tests/test_player_evidence_capture.py
```

No M5Q, M6, learner-diagnosis, tutoring, pedagogy, or research-artifact file was changed.

### Exact-head CI

GitHub Actions run:

```text
34236607661
```

Result:

```text
142 passed
8 intentionally skipped external-engine tests in the normal suite
20 M5C-focused tests passed
Ruff PASS
external Stockfish integration PASS
```

### Implementation merge

```text
dd550744126a167dae2cffb3adaf82f768276f1c
```

The merge is tree-identical to the exact qualified M5C candidate. Comparing the candidate to the merge produced zero changed files.

### Post-merge CI

GitHub Actions run:

```text
34236711506
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M5C — CAPTURE/FREEZE STATE MACHINE: QUALIFIED**

The qualified claim is intentionally narrow:

> Chess Mentor Engine can deterministically sequence provenance-rich Player Decision Evidence capture around the qualified M5B records, enforce clean pre-reveal freeze gates, preserve deviating/contaminated interactions with append-only provenance, retain explicit exposure state, and append clarifications without rewriting frozen participant evidence.

## Claims still prohibited

M5C qualification does **not** establish that:

- M5 Player Decision Evidence as a whole is qualified;
- every M5A qualification category has been exercised as one complete corpus;
- a participant report is objectively correct or causally complete;
- an omitted move was never considered;
- a reported explanation caused the move choice;
- a `Reasoning Discrepancy` exists;
- recurrence or a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- an intervention is warranted or effective;
- learning, transfer, or mastery occurred.

## Next authorized boundary

The only next milestone slice is:

> **M5Q — full M5 qualification.**

M5Q should qualify the complete M5 evidence-capture claim across the frozen M5A categories, including clean minimal-only and two-stage runs, instrument-aware provenance, contaminated/deviating runs, amendments, ambiguous/illegal moves, post-reveal evidence, deterministic replay, and preservation of historical research artifacts.

M5Q is a qualification milestone, not authorization to implement M6 semantics.

M6 Reasoning Discrepancy remains unauthorized until M5Q passes and the M5 claim ceiling is explicitly reconciled.
