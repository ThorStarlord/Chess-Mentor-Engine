# M5Q — Full Player Decision Evidence Qualification

## Status

**M5 — Player Decision Evidence is qualified. M5Q is qualified. M6 Reasoning Discrepancy is authorized next but has not started.**

This record qualifies the complete M5A Player Decision Evidence claim surface across the M5B immutable record model and M5C capture/freeze state machine. It adds no Reasoning Discrepancy, recurrence, learner hypothesis, tutoring, pedagogy, transfer, or mastery semantics.

## Qualified path

The qualified evidence path is:

```text
qualified M4 selected position / candidate / batch
        ↓
PlayerDecisionContext
        ↓
versioned PromptDefinition / PromptPresentation
        ↓
PlayerResponseEvidence
        ↓
EvidenceFreeze
        ↓
optional later pre-reveal stage(s)
        ↓
ExposureEvent / ProtocolDeviation as applicable
        ↓
ObjectiveEvidenceReveal
        ↓
optional post-reveal evidence
```

The central authority split remains:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

## Qualification corpus

M5Q freezes its qualification manifest at:

```text
tests/fixtures/m5q_player_evidence_corpus.json
```

and executes the whole-surface tests in:

```text
tests/test_m5_qualification.py
```

The frozen required cases are:

```text
clean_minimal_only
clean_two_stage
instrument_aware
contaminated_exposure
early_later_stage
early_objective_reveal
append_only_amendment
ambiguous_reported_move
illegal_reported_move
post_reveal_reflection
deterministic_replay
research_artifact_preservation
```

The corpus also freezes the exact Pilot 003 Stage A prompt and all six Stage B prompts so production compatibility is tested against the historical instrument without redefining that instrument as universal product truth.

## Upstream integration

M5Q does not start from a hand-written orphan response. Its qualification helper constructs a real deterministic upstream evidence chain:

```text
PGN
→ CanonicalGame / CanonicalPosition
→ PositionContextPacket / PositionFeaturePacket
→ precomputed PositionAnalysis
→ DecisionComparison
→ SelectionSignal[]
→ SelectionPolicy
→ eligible M4 control candidate
→ DiagnosticCandidateBatch
→ PlayerDecisionContext
```

The selected position is therefore bound to qualified M1–M4 identities before M5 capture begins.

## Clean minimal-only evidence

M5Q verifies a complete minimal-only path:

```text
A1 prompt
→ A1 participant response
→ A1 EvidenceFreeze
→ objective reveal
```

The raw participant text is preserved byte-for-byte as submitted, participant-authored structured input remains separate, the freeze binds the exact response fingerprint, and the clean run remains uncontaminated.

## Clean two-stage Pilot-003-style evidence

M5Q reproduces the frozen clean order:

```text
A1 minimal prompt
→ A1 response
→ A1 freeze
→ A2 standardized probe
→ A2 response
→ A2 freeze
→ objective reveal
```

A1 and A2 remain separate records. The exact frozen Stage A wording and the six Stage B questions are represented by distinct versioned prompt definitions. The A2 structured response contains only explicitly supplied participant values such as candidate moves, expected reply/continuation, stated objective, uncertainty, and confidence.

The qualification claim is evidence-preservation only. It does not claim that A1 is probe-naive cognition, that A2 is pedagogically beneficial, or that the participant's explanation is causal.

## Instrument-aware provenance

M5Q verifies the Pilot 004 boundary:

```text
minimal prompt
!= proof of probe-naive cognition
```

An explicit `INSTRUMENT_AWARENESS_RECORDED` exposure with `known_aware` survives in the presentation's prior information state without automatically marking the session contaminated.

## Contaminated and deviating evidence

M5Q verifies that prohibited pre-reveal exposure is preserved rather than erased. A facilitator hint produces:

```text
ExposureEvent(FACILITATOR_HINT)
+ ProtocolDeviation(PROHIBITED_PRE_REVEAL_EXPOSURE)
→ contaminated session
```

The response can still be captured and frozen, and later analysis can decide whether to exclude the affected evidence. M5 itself does not manufacture a clean history.

M5Q also verifies preservation of:

- an A2/later pre-reveal prompt shown before the required A1 freeze;
- objective evidence revealed before required pre-reveal freezes.

Those sequences remain auditable through explicit deviations and exposure provenance.

## Append-only amendments

M5Q verifies that a later participant clarification creates an `EvidenceAmendment` that cites the original response and freeze. The original response text and fingerprint remain unchanged.

```text
original frozen response
!= later amendment
```

## Ambiguous and illegal reported moves

M5Q verifies both required non-repair cases:

```text
ambiguous participant move
→ remains ambiguous
→ no guessed UCI move

illegal participant-reported move
→ submitted value preserved
→ legality marked illegal_for_position
→ no silent correction
```

These remain participant evidence rather than objective move truth.

## Post-reveal evidence separation

M5Q verifies that post-reveal reflection is a separate `POST_REVEAL_REFLECTION` response and that the presentation's information state contains the prior `ENGINE_EVIDENCE_SHOWN` exposure. It never overwrites or merges backward into A1/A2 pre-reveal evidence.

## Deterministic replay

Replaying an identical clean capture sequence over identical upstream evidence produces the same:

```text
capture_session_id
snapshot_fingerprint
canonical serialized session state
```

This qualifies deterministic evidence identity without claiming deterministic human cognition.

## Research-artifact preservation

The M5Q manifest freezes seven Git blob identities and verifies the checked-out bytes remain identical:

```text
FPV-PILOT-003/pilot-protocol.md
FPV-PILOT-003/reasoning-instrument.md
FPV-PILOT-003/evidence-schema.md
FPV-PILOT-003/information-boundary.md
FPV-PILOT-003/contamination-policy.md
FPV-PILOT-004/pilot-protocol.md
FPV-PILOT-004/reasoning-instrument.md
```

The qualification therefore proves that M5 production work did not silently rewrite the frozen research instruments used to motivate the boundary.

## Superseded qualification attempt

The first qualification head was:

```text
48f34222caade4a9590ba904dbe974ebda3d34b7
```

Its behavioral suite passed completely:

```text
156 passed
8 intentionally skipped external-engine tests
all 14 M5Q tests passed
```

Ruff found only three line-length violations in `tests/test_m5_qualification.py`. No production code or qualification semantics changed. The replacement head wrapped those lines and requalified from scratch.

## Exact qualification evidence

### Exact qualified M5Q candidate

```text
7610e30959f53a79b83400dae49438062d11515d
```

PR #22 changed exactly:

```text
tests/fixtures/m5q_player_evidence_corpus.json
tests/test_m5_qualification.py
```

No production source, frozen M5A contract, ADR 0004, research artifact, M6 code, learner-diagnosis code, tutoring code, or pedagogy code changed.

### Exact-head CI

GitHub Actions run:

```text
34289884971
```

Result:

```text
156 passed
8 intentionally skipped external-engine tests in the normal suite
14 M5Q-focused tests passed
Ruff PASS
external Stockfish integration PASS
```

### Qualification merge

```text
78d40118e5999e004b52a11efe7767f072021e32
```

The merge is tree-identical to the exact qualified candidate. Comparing candidate to merge produced zero changed files.

### Post-merge CI

GitHub Actions run:

```text
34289969816
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M5 — PLAYER DECISION EVIDENCE: QUALIFIED**

The qualified claim is intentionally narrow:

> Chess Mentor Engine can capture and preserve provenance-rich player decision evidence tied to a qualified selected chess position, including versioned prompt identity, raw and explicit structured participant response, immutable freeze timing, exposure/instrument-awareness state, preserved protocol deviations, append-only amendments, objective-evidence reveal timing, post-reveal separation, and deterministic evidence identity.

## What M5 may now claim

M5 may report evidence facts such as:

- the participant explicitly chose or reported move X in a specific stage;
- the participant explicitly listed candidate moves or an expected reply;
- a specific raw response was frozen before objective reveal;
- a later standardized probe preceded a changed submitted answer;
- the participant was known to be instrument-aware;
- a prohibited exposure occurred before required freezes;
- an amendment was submitted after the original evidence was frozen;
- a post-reveal reflection occurred after engine evidence was exposed;
- an ambiguous or illegal reported move was preserved without silent repair.

## Claims still prohibited

M5 qualification does **not** establish that:

- a participant report is objectively correct or complete;
- an omitted move was never considered;
- a reported explanation caused the move choice;
- the player has tunnel vision, poor calculation, weak planning, or any other Reasoning Discrepancy;
- a local discrepancy recurs;
- a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- a selected position is pedagogically valuable;
- probing or tutoring caused learning;
- an intervention is warranted or effective;
- transfer or mastery occurred.

Those claims require M6 or later evidence contracts.

## Next authorized boundary

M5 is now complete at its intended boundary. The next milestone is:

> **M6 — Reasoning Discrepancy, contract/design gate first.**

M6 may now be planned, but implementation should not begin by inventing cognitive labels. The next bounded task should freeze what counts as a local, traceable discrepancy between qualified objective chess demands/consequences and qualified player-reported evidence, including explicit evidence references, uncertainty, analyst/model coding authority, and a strict separation between one local discrepancy and recurrence/stable learner weakness.

M6 implementation has not started.
