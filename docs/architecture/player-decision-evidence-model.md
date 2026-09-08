# M5B — Immutable Player Decision Evidence Model

## Status

**M5B — Immutable Player Decision Evidence Model is qualified. M5C has not started.**

M5B implements only the deterministic immutable record/identity layer frozen by
`docs/architecture/player-decision-evidence.md` and ADR 0004. It does not implement
the interactive capture/freeze state machine, reveal gating, append-only amendment
transitions, Reasoning Discrepancy, learner inference, LLM interpretation, or
pedagogy.

## Qualified boundary

The implemented package is:

```text
src/chess_mentor_engine/evidence/
├── __init__.py
├── model.py
└── records.py
```

The qualified record surface is:

```text
PlayerDecisionContext
PromptDefinition
PromptPresentation
PlayerResponseEvidence
ExposureEvent
EvidenceFreeze
ObjectiveEvidenceReveal
```

Supporting immutable value types include:

```text
EvidenceReference
ParticipantMove
ParticipantStructuredResponse
NumericRating
```

The implemented evidence relationship is still deliberately non-inferential:

```text
qualified M4/canonical evidence
        |
        v
PlayerDecisionContext
        |
        +--> PromptDefinition
        |
        v
PromptPresentation
        |
        v
PlayerResponseEvidence
        |
        v
EvidenceFreeze

ExposureEvent -----------------> presentation information-state provenance
ObjectiveEvidenceReveal --------> later objective-evidence visibility provenance
```

M5B can represent these records. It does not yet enforce a runtime sequence among
them; sequencing belongs to M5C.

## Authority separation preserved

M5B preserves the M5A authority split:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

`PlayerResponseEvidence.raw_response` preserves free text exactly as submitted.
`ParticipantStructuredResponse` contains only participant-authored structured values.
M5B performs no prose extraction and introduces no analyst/model-coding record.

A participant-authored move remains participant evidence. It can be represented as:

- deterministically normalized when the submitted interaction is unambiguous;
- ambiguous or unresolved when it is not;
- legal, illegal-for-position, or not-assessed when legality is known or unknown.

An illegal or ambiguous report is preserved rather than repaired into a plausible
legal answer.

## Upstream provenance binding

`record_player_decision_context(...)` requires matching qualified upstream evidence:

```text
CanonicalPosition
PositionContextPacket
DiagnosticCandidate
optional DiagnosticCandidateBatch
```

It rejects mismatched position/game identities, and an optional batch reference is
accepted only when the selected candidate is actually present in that batch under the
same selection-policy identity.

The resulting context retains stable references/fingerprints to the upstream
candidate, optional batch, and position-context packet. Participant/session identity
and a timezone-aware creation timestamp are also part of context identity.

## Prompt provenance

`PromptDefinition` is content-addressed over material prompt conditions, including:

```text
name
version
stage kind
interaction class
ordered prompt content
ordered response schema
normalized provenance
```

Changing material wording, order, version, stage, response constraints, or provenance
changes prompt identity.

`PromptPresentation` separately records what was actually rendered, its content
fingerprint, presentation time, stage identity, position-context reference, and the
set of prior exposure-event IDs available before presentation.

This preserves the distinction:

```text
prompt definition
!= actual presentation
```

## Exposure and instrument awareness

`ExposureEvent` represents the provenance categories frozen by M5A, including position
context, later-stage prompts, engine evidence, selection rationale, expected
 discrepancy, prior reports, external analysis, facilitator hints, and explicit
instrument awareness.

Instrument awareness is never inferred from prompt stage. It is represented only by
an explicit `INSTRUMENT_AWARENESS_RECORDED` event with one of:

```text
known_aware
known_unaware
unknown
```

This preserves the Pilot 004 lesson that a minimal prompt does not prove probe-naive
cognition.

## Response and freeze authority

The implementation makes one clarification to the conceptual M5A schema while
preserving its semantics:

> **`EvidenceFreeze` is the sole freeze authority.**

`PlayerResponseEvidence` is an immutable value from creation and stores submission
provenance, but it does not duplicate a `frozen_at` field. `EvidenceFreeze` separately
binds:

```text
context
stage
response ID
exact response fingerprint
freeze timestamp
```

This avoids two independent freeze authorities that could disagree. M5C will later
own the transition rule that determines when a freeze is required and whether a later
stage/reveal is permitted.

M5B already enforces the local invariant that a freeze timestamp cannot precede the
response submission timestamp.

## Objective reveal record

`ObjectiveEvidenceReveal` can retain references to qualified objective evidence:

```text
PositionAnalysis[]
DecisionComparison
SelectionSignal[]
```

along with exact rendered content/fingerprint and reveal time.

M5B intentionally does **not** decide whether the reveal occurred at a valid point in
the interaction sequence. That gate belongs to M5C. A reveal record is evidence about
what became visible and when; it is not proof that the interaction remained clean.

## Deterministic identity and serialization

All M5B domain records are frozen dataclasses with deterministic `to_dict()`
serialization. Material record identities are SHA-256-derived from canonical JSON.

Ordering that is semantically irrelevant is normalized before identity construction,
for example prompt/exposure metadata key order and prior exposure-event sets.
Ordering that is materially meaningful, such as prompt question order and structured
candidate/continuation order, is preserved.

Timestamps accepted by builders must be valid ISO-compatible values with an explicit
timezone offset.

## Focused qualification tests

`tests/test_player_evidence_model.py` contains 16 M5B-focused tests covering:

1. deterministic context identity and M4 candidate binding;
2. participant/session sensitivity;
3. candidate/position mismatch rejection;
4. optional batch provenance;
5. prompt wording/order/version identity;
6. canonical prompt-provenance ordering;
7. explicit instrument-awareness provenance;
8. canonical exposure-detail ordering;
9. exact presentation rendering and prior-exposure state;
10. verbatim raw-response preservation;
11. illegal and ambiguous participant move representation;
12. separate freeze authority bound to the exact response fingerprint;
13. freeze-before-submission rejection;
14. immutable objective-reveal provenance without M5C gating;
15. frozen dataclass immutability;
16. timezone-aware timestamp enforcement.

## Superseded qualification attempts

The first implementation candidate exposed a test-fixture ordering error. The test
intended to exercise candidate/position mismatch but supplied a position-context packet
for the old position, so the earlier packet-integrity guard correctly rejected it.
The fixture was corrected; production validation was not weakened.

A later candidate passed all behavioral tests but failed Ruff on line length. Only
formatting was changed, and the replacement exact head requalified from scratch.

## Exact qualification evidence

### Exact qualified M5B candidate

```text
549d1d82ed0d096a13a7b78d0f52f4389c857bba
```

PR #18 changed exactly:

```text
src/chess_mentor_engine/evidence/__init__.py
src/chess_mentor_engine/evidence/model.py
src/chess_mentor_engine/evidence/records.py
tests/test_player_evidence_model.py
```

No M5C/M6 file or behavior was added.

### Exact-head CI

GitHub Actions run:

```text
34225427259
```

Result:

```text
122 passed
8 intentionally skipped external-engine tests in the normal suite
Ruff PASS
external Stockfish integration PASS
```

### Implementation merge

```text
4df30d327fcf042b4dca3a2e000dfb45499295e7
```

The merge is tree-identical to the exact qualified M5B candidate: comparing the two
commits produced zero changed files.

### Post-merge CI

GitHub Actions run:

```text
34226047486
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M5B — IMMUTABLE PLAYER DECISION EVIDENCE MODEL: QUALIFIED**

The qualified claim is intentionally narrow:

> Chess Mentor Engine has a deterministic immutable record/identity layer for
> provenance-rich Player Decision Evidence tied to qualified selected positions,
> including prompt/presentation provenance, verbatim participant response evidence,
> exposure state, separate freeze evidence, and objective-reveal evidence.

## Claims still prohibited

M5B qualification does **not** establish that:

- the complete M5 capture workflow is qualified;
- stage order is enforced at runtime;
- objective evidence reveal is gated by required freezes;
- append-only amendment/deviation transitions are implemented;
- a player report is objectively correct;
- an omitted move was never considered;
- a reported explanation caused the chosen move;
- a Reasoning Discrepancy exists;
- a stable learner weakness or recurrence exists;
- an intervention is warranted or effective;
- learning, transfer, or mastery occurred.

## Next authorized boundary

The only next implementation slice is:

> **M5C — capture/freeze state machine.**

M5C should implement deterministic stage ordering, presentation/capture/freeze
transitions, objective-reveal gating, append-only amendments, and explicit
deviation/exposure handling. It must not implement M6 Reasoning Discrepancy.

M5 as a whole remains in progress until M5Q qualifies the complete Player Decision
Evidence path.
