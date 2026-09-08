# M4C — SelectionSignal and DiagnosticCandidate

## Status

**M4C — SelectionSignal and DiagnosticCandidate is implemented and qualified. M4D has not started. M4 overall is not yet qualified.**

This document records the implemented M4C boundary and its qualification evidence.
The frozen selection semantics remain defined by
`docs/architecture/diagnostic-position-selection.md` and ADR 0003. This record does
not reopen or weaken that contract.

## Purpose

M4C answers a bounded evidence-acquisition question:

> Which transparent objective properties can be reconstructed from one qualified
> M4B `DecisionComparison` and its matching M2/M3 evidence, and how can a later
> selection policy preserve the exact reasons a decision became eligible?

M4C does not execute selection policy, rank a batch, infer learner psychology, or
choose pedagogy.

```text
DecisionComparison
+ PositionFeaturePacket
+ matching root PositionAnalysis
        |
        v
SelectionSignal[]
        |
        v
DiagnosticCandidate record
```

The final arrow is record construction only: the caller must supply an opaque
selection-policy identity and the exact signal IDs that caused eligibility. M4D owns
policy execution.

## Public implementation

M4C extends `chess_mentor_engine.selection` with:

```text
SelectionEvidenceRef
SelectionSignal
SelectionPolicyIdentity
DiagnosticCandidate
SelectionSignalError
DiagnosticCandidateError
SIGNAL_SCHEMA_VERSION
build_selection_signals
record_diagnostic_candidate
```

`SelectionPolicyIdentity` is deliberately opaque in M4C. It contains only a policy ID
and version. It does not contain thresholds, quotas, per-game caps, control rules,
tie-breaking, or batch logic.

## Implemented signal taxonomy

The initial deterministic signal surface is:

```text
PLAYED_EQUALS_RANK_1
PLAYED_DIFFERS_FROM_RANK_1
EXACT_CP_DELTA
MATE_RELATION
TOP_CANDIDATE_SEPARATION
BEST_MOVE_IS_CHECK
BEST_MOVE_IS_CAPTURE
BEST_MOVE_IS_QUIET
PLAYED_MOVE_IS_CHECK
PLAYED_MOVE_IS_CAPTURE
PLAYED_MOVE_IS_QUIET
ROOT_SIDE_IS_IN_CHECK
ENGINE_EVIDENCE_INVERSION
```

These are evidence properties, not learner traits.

### Deliberately deferred signal

`MULTIPV_CLOSE_CHOICE` is not emitted by M4C because "close" requires a threshold.
That threshold belongs to versioned M4D `SelectionPolicy`, not deterministic product
truth.

M4C instead preserves the raw exact-centipawn top-candidate separation when available.
A later policy may decide whether that raw value satisfies a versioned close-choice
rule.

## Evidence matching

`build_selection_signals` requires all supplied evidence to target the same root
decision already cited by M4B.

The M2 `PositionFeaturePacket` must match:

```text
position_id
game_id
ply_index
side_to_move
FEN
```

The M3 root analysis must match the M4B evidence reference by:

```text
position_id
FEN
request fingerprint
status
result fingerprint, when present
failure code, when applicable
```

M4C rejects mismatched evidence rather than silently combining unrelated records.

Each `SelectionSignal` cites stable `SelectionEvidenceRef` records for the evidence it
uses. Feature packets are fingerprinted with SHA-256 over deterministic canonical JSON;
M3 analysis references retain their frozen request/result fingerprints; M4B comparison
identity is retained explicitly.

## Complete versus partial engine evidence

M4C preserves the conservative M4A completion boundary.

Ordered engine-derived signals require complete root analysis. Therefore a partial
M3 result does not emit:

```text
PLAYED_EQUALS_RANK_1
PLAYED_DIFFERS_FROM_RANK_1
BEST_MOVE_IS_CHECK
BEST_MOVE_IS_CAPTURE
BEST_MOVE_IS_QUIET
TOP_CANDIDATE_SEPARATION
EXACT_CP_DELTA
```

when the corresponding M4B comparison cannot support exact ordered evidence.

Deterministic board facts that do not depend on completed engine ordering may still be
preserved. For example, a partial engine result does not erase the objective fact that
the canonical played move was a quiet legal move or that the root side was in check.

```text
incomplete engine ordering
!= missing deterministic board geometry
```

## Exact centipawn and mate signals

`EXACT_CP_DELTA` reuses the signed mover-relative delta already qualified by M4B. M4C
does not recompute or clamp it.

A negative delta remains evidence of `ENGINE_EVIDENCE_INVERSION` rather than being
rewritten to zero.

Mate remains symbolic. `MATE_RELATION` preserves M4B relations such as forced mate
preserved, missed, allowed, escaped, completed, or mate-distance change. M4C never
converts mate to a centipawn sentinel.

## Top-candidate separation

When the root analysis is complete and the first two candidate evaluations are both
exact centipawn scores, M4C may emit `TOP_CANDIDATE_SEPARATION` with:

```text
rank_1_move_uci
rank_2_move_uci
exact_centipawn_separation_for_mover
```

The value is mover-relative for both White and Black and is retained raw. No M4C
threshold says whether the separation is large, small, close, important, or
pedagogically valuable.

## Move-shape signals

M4C reconstructs best/played move shape from the qualified M2 legal-move feature
packet.

A move may be both a check and a capture. `QUIET` means neither check nor capture; it
is not a strategic or pedagogical label.

`ROOT_SIDE_IS_IN_CHECK` is a deterministic board-state fact.

## Successful decisions remain first-class

If the actual played move equals engine rank 1 under eligible complete evidence, M4C
emits `PLAYED_EQUALS_RANK_1` and may preserve a zero exact-centipawn delta.

M4C does not call that record a control. Control sampling and minimum-control policy
belong to M4D. The successful evidence is simply available so M4D does not have to
operate on an error-only pool.

## Stable signal identity

A `SelectionSignal` ID is derived from SHA-256 over deterministic canonical JSON of:

```text
signal kind
position/game/comparison identity
signal schema version
raw value
evidence references
detail
```

The ID format is:

```text
signal_<first 20 hexadecimal characters>
```

Changing material evidence changes signal identity instead of rewriting prior signal
meaning.

## DiagnosticCandidate is a record, not a selector

`record_diagnostic_candidate` requires:

```text
qualified DecisionComparison
SelectionSignal[]
SelectionPolicyIdentity
eligibility_signal_ids[]
```

It validates that all retained signals belong to the same position, game, and M4B
comparison and that every eligibility signal ID references a retained signal.

M4C does not decide which signals qualify. The caller supplies the eligibility result.
M4D will later own the deterministic policy that produces that result.

Candidate identity is stable over:

```text
position/game/comparison identity
selection-policy identity
signal ID set
eligibility signal ID set
M4B decision provenance
```

Signal ordering does not change candidate identity. Changing policy version does.

```text
DiagnosticCandidate
!= policy execution
!= batch selection
!= lesson recommendation
```

## Explicitly excluded labels

M4C does not emit:

```text
poor calculation
missed opponent resource
tunnel vision
bad planning
weak strategic understanding
needs tactics training
high-value teaching moment
```

Those require player evidence, later inference, or pedagogy.

## Qualification record

### Exact qualified implementation candidate

```text
8658a7b9922693e1806e47fd75285dc7b9effc9d
```

### Implementation merge

```text
5ccb9fd524c6863028b0d8373a7fd2ac01da2105
```

The implementation merge is tree-identical to the exact qualified candidate: comparing
candidate and merge commit produced no changed files.

### Exact-head CI

On the exact candidate:

```text
85 passed
8 intentionally skipped external-engine tests
Ruff PASS
external Stockfish integration PASS
```

The M4C-focused corpus contains 17 tests covering signal determinism, successful
rank-1 evidence, move shape, root check, Black mover perspective, mate semantics,
engine inversion, evidence matching, stable candidate identity, policy-sensitive
candidate identity, anti-psychology boundaries, and the partial-evidence boundary.

The initial M4C head was not qualified because Ruff failed. That candidate was
superseded, the lint defects were fixed, the partial-evidence contract was tightened,
and the exact candidate above requalified from scratch.

### Post-merge qualification evidence

The implementation merge's `test-and-lint` job passed. Its first external Stockfish
job did not report a chess-test failure but became operationally stalled inside the
Ubuntu package-install step before the external chess tests ran.

The stalled job was not counted as a pass.

A docs-only qualification branch was then created directly from the tree-identical
implementation merge without changing product code. Exact witness head:

```text
2667b9ef00bc47483a128e8b38bc81c49c941d1d
```

CI run:

```text
34209881796
```

On that direct post-merge descendant:

```text
test-and-lint PASS
external Stockfish integration PASS
```

This replacement witness tests the same M4C product tree while making the infrastructure
stall explicit rather than pretending the original job succeeded.

The final documentation reconciliation head must also pass repository CI before this
record is promoted to `main`.

## Qualification verdict

> **M4C — SELECTIONSIGNAL + DIAGNOSTICCANDIDATE: QUALIFIED**

The qualified claim is deliberately bounded:

> Chess Mentor Engine can derive deterministic, provenance-rich objective selection
> signals from qualified M2/M3/M4B evidence and can record a stable
> `DiagnosticCandidate` with explicit policy identity and eligibility-signal
> provenance, without executing batch policy or inferring learner psychology.

M4C does **not** establish that the repository can execute a selection policy or
produce bounded candidate/control batches. Those require M4D and M4Q.

## Explicitly not implemented

M4C does not implement:

- versioned `SelectionPolicy` execution;
- universal blunder/mistake/inaccuracy thresholds;
- `MULTIPV_CLOSE_CHOICE` threshold evaluation;
- requested batch size;
- quotas;
- per-game caps;
- control sampling;
- near-duplicate suppression;
- deterministic batch tie-breaking;
- exclusions/shortfalls;
- `DiagnosticCandidateBatch`;
- player-response capture;
- Reasoning Discrepancy;
- learner hypotheses;
- LLM ranking;
- pedagogy;
- transfer/mastery;
- Pilot 004 mutation.

## Next authorized boundary

> **M4D — implement versioned `SelectionPolicy` + `DiagnosticCandidateBatch` only.**

M4D must consume qualified M4C evidence without inventing learner-psychology or
pedagogical labels. It may introduce explicit thresholds, quotas, successful-control
sampling, per-game caps, deterministic tie-breaking, exclusions, and shortfalls under
a versioned policy.

After M4D implementation and qualification, stop again before M4Q review.

M4 overall remains unqualified until M4D and M4Q close their gates. M5 remains
unauthorized until M4Q.

## Governing principle

> A selection signal is not a learner diagnosis. A DiagnosticCandidate is not a
> lesson recommendation. M4C makes future selection reasons inspectable.