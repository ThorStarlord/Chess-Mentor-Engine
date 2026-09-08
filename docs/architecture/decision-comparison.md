# M4B — DecisionComparison

## Status

**M4B — DecisionComparison is implemented and qualified. M4C SelectionSignal and DiagnosticCandidate have not started. M4 overall is not yet qualified.**

This document records the implemented M4B boundary and qualification evidence.
The frozen selection semantics remain defined by
`docs/architecture/diagnostic-position-selection.md` and ADR 0003; this document does
not reopen or weaken that contract.

The M4A contract document is intentionally preserved as the frozen contract artifact.
Its time-sensitive status sentence describes the state at contract freeze. Current
milestone status is governed by this implementation record,
`docs/product/repository-build-status.md`, and `CONTEXT.md`.

## Purpose

M4B answers one bounded objective question:

> Given the move actually played in canonical game history and qualified M3 engine
> evidence, what objective comparison can Chess Mentor Engine preserve without
> manufacturing player-psychology or pedagogical claims?

M4B does not select diagnostic candidates. It does not infer why a player moved, and
it does not decide whether a position is a good lesson.

```text
canonical played decision
+ qualified engine evidence
        ↓
DecisionComparison
```

The next M4 layer may derive transparent selection signals from this record, but that
work is outside M4B.

## Public implementation

M4B introduces `chess_mentor_engine.selection` with the following public surface:

```text
AnalysisEvidenceRef
DecisionComparison
DecisionComparisonPolicy
DecisionProvenance
DecisionComparisonError
DEFAULT_COMPARISON_POLICY
compare_played_decision
```

The first comparison-only policy is deliberately narrow:

```text
policy_id = m4b-exact-comparison
version = 1
exact_cp_tolerance = 0
```

The tolerance is configuration attached to the comparison identity. It is not a
universal definition of `mistake`, `inaccuracy`, or `blunder`, and it is not M4D
batch-selection policy.

## Canonical played-move authority

The played move is derived only from `CanonicalGame.moves_uci` at the supplied root
position's canonical ply index.

M4B verifies all of the following before comparing evidence:

1. the supplied position belongs to the supplied canonical game;
2. the position identity/FEN matches the canonical root at that ply;
3. a canonical played move exists;
4. the canonical child position exists;
5. the child's `last_move_uci` matches the canonical played move;
6. the recorded played move is independently legal from the root FEN;
7. independently replaying that move produces the canonical child FEN exactly.

The independent replay check was added during final contract review before merge. It
prevents a corrupted child record from passing merely because its metadata repeats
the same move string.

```text
recorded child metadata
!= sufficient provenance proof

legal replay to exact child FEN
= required M4B provenance proof
```

## Engine evidence sources

M4B supports the two sources authorized by M4A.

### Root MultiPV

If the played move is present in the root `PositionAnalysis.lines`, its root-line
evaluation is used directly and M4B preserves:

- the root result fingerprint;
- the played line rank;
- `played_evaluation_source = root_multipv`;
- `compatibility = same_root_analysis`.

### Child reanalysis

If the played move is outside root MultiPV, a child-position M3 outcome may be
supplied. It must target the canonical child position/FEN exactly.

For complete child analysis, M4B uses the child's rank-1 evaluation only when root and
child analysis regimes are compatible.

The compatibility key preserves the conservative M4A rule and includes:

```text
provider name/version/protocol
engine name/version
binary SHA-256
engine artifact identities
engine options
search-limit kind/value
MultiPV
supervisor timeout
```

A material mismatch produces:

```text
incompatible_analysis_regime
```

rather than a numeric severity estimate.

## Conservative evidence states

M4B preserves evidence insufficiency instead of coercing every M3 outcome into a move
loss.

### AnalysisFailure

A root or child `AnalysisFailure` remains explicit and cannot become a move-quality
number.

### Partial analysis

Partial root/child evidence becomes:

```text
partial_evidence
```

and remains incomparable for initial severity.

### Bound-limited evaluation

If either ordered score is `lower` or `upper` rather than `exact`, the comparison
becomes:

```text
bound_limited
```

No interval arithmetic or fake exactness is introduced.

## Exact centipawn comparison

M3 keeps evaluations from a fixed White perspective. M4B derives a mover-relative
value without changing the stored M3 evidence:

```text
white mover value = white-perspective centipawns
black mover value = -white-perspective centipawns
```

For exact centipawn evidence:

```text
exact_centipawn_delta_for_mover
    = best mover value - played mover value
```

The signed delta is retained.

- delta above policy tolerance → `worse_for_mover`;
- delta within policy tolerance → `approximately_equal_under_policy`;
- negative delta → `engine_evidence_inversion`.

A negative delta is not clamped to zero. It records disagreement/inversion between
engine observations or ranked lines that downstream code must preserve.

## Mate-aware symbolic comparison

M4B preserves M3's semantic mate representation:

```text
winner + plies_to_mate
```

It never converts mate into a large centipawn sentinel.

For exact evidence:

- forced mate for mover outranks any centipawn evaluation;
- any centipawn evaluation outranks forced mate against mover;
- among mates won by mover, fewer plies is better;
- among mates lost by mover, more plies is better.

M4B records symbolic relations including:

```text
forced_mate_preserved
forced_mate_missed
forced_mate_allowed
forced_mate_escaped
forced_mate_missed_and_allowed
mate_distance_improved
mate_distance_worsened
forced_mate_completed
engine_evidence_inversion
```

No mate/cp comparison produces `exact_centipawn_delta_for_mover`.

## Terminal child outcomes

A played move may itself end the game. Because M3 terminal analyses have no candidate
score, M4B derives the terminal child state from the qualified chess-rules substrate.

The implemented M4B surface distinguishes:

```text
checkmate
stalemate
```

and uses `comparison_kind = terminal_relation` rather than inventing a numeric score.

Examples covered by qualification include:

- a played mate-in-one that completes the root forced mate;
- a played stalemate that discards a root forced mate.

An optional supplied child `PositionAnalysis` for a deterministic terminal child must
itself be terminal; otherwise M4B rejects the inconsistent evidence.

## Stable evidence references and identity

`DecisionComparison` preserves references to root and, when applicable, played-child
M3 evidence, including:

- position ID;
- FEN;
- request fingerprint;
- result fingerprint when one exists;
- M3 status;
- failure code when the outcome is a failure.

`DecisionProvenance` additionally preserves:

- source PGN SHA-256;
- semantic game fingerprint;
- root ply index;
- played-move index;
- canonical child position ID.

The comparison ID is derived from SHA-256 over deterministic canonical JSON of the
complete normalized comparison payload excluding the ID itself:

```text
comparison_<first 20 hex characters>
```

Therefore changing material evidence or the comparison-policy identity changes the
comparison identity rather than rewriting prior evidence.

## Implemented comparison outcomes

M4B can preserve the M4A result classes relevant to the comparison layer:

```text
approximately_equal_under_policy
worse_for_mover
engine_evidence_inversion
incompatible_analysis_regime
partial_evidence
bound_limited
terminal_relation
incomparable
```

`better_for_mover` remains part of the frozen M4 contract but is not synthesized to
hide engine-evidence inversion. When the played evidence appears objectively better
than the root rank-1 evidence under the same comparison semantics, M4B intentionally
uses `engine_evidence_inversion`.

## Qualification record

### Exact qualified candidate

```text
1315a3fc14547c739ea3721fa7dc3a868c422fa0
```

### Merge commit

```text
10111c716ce7cc5cea0766ae0b8f738ddf555112
```

The merge commit is tree-identical to the exact qualified candidate: comparing the
candidate with the merge commit produced no changed files.

### Exact-head CI evidence

On the qualified candidate:

```text
68 passed
8 intentionally skipped external-engine tests
Ruff PASS
external Stockfish integration job PASS
```

The 17 M4B-focused tests cover:

1. White mover exact centipawn comparison;
2. Black mover perspective reversal;
3. explicit comparison tolerance;
4. child reanalysis when the played move is outside root MultiPV;
5. incompatible root/child analysis regimes;
6. partial evidence;
7. bound-limited evidence;
8. child analysis failure;
9. engine-evidence inversion;
10. symbolic forced-mate miss;
11. symbolic forced-mate allowance;
12. deterministic terminal checkmate;
13. deterministic terminal stalemate;
14. wrong child-analysis target rejection;
15. root analysis failure preservation;
16. independent canonical-child replay integrity;
17. deterministic and policy-sensitive comparison identity.

The tests use synthetic PGN/FEN fixtures only; no private P01 PGN was committed.

### Post-merge evidence

After merge, both repository CI jobs passed again on the merge commit:

```text
test-and-lint PASS
stockfish-integration PASS
```

M1-M3 therefore remained green through M4B promotion.

## Qualification verdict

> **M4B — DECISIONCOMPARISON: QUALIFIED**

The qualified claim is deliberately bounded:

> Chess Mentor Engine can derive a deterministic, provenance-rich objective
> comparison between a canonical played decision and compatible M3 engine evidence,
> while preserving exact-score limits, mate semantics, terminal outcomes, failures,
> incompatible regimes, and engine-evidence inversions.

M4B does **not** establish that the repository can select diagnostic positions. That
requires M4C/M4D/M4Q.

## Explicitly not implemented

M4B does not implement:

- `SelectionSignal` generation;
- `DiagnosticCandidate` generation;
- M4D `SelectionPolicy` batch logic;
- candidate quotas or controls;
- diagnostic position selection in production;
- player-response capture;
- learner-psychology inference;
- Reasoning Discrepancy;
- learner hypotheses;
- LLM ranking;
- pedagogy;
- transfer/mastery;
- Pilot 004 mutation.

## Next authorized step

> **M4C — implement transparent `SelectionSignal` + `DiagnosticCandidate` only, then
> stop before M4D batch policy.**

M4C must consume qualified M4B records without reinterpreting incomparable evidence
as exact severity and without introducing learner-psychology or pedagogical labels.

## Governing principle

> M4B does not decide which position should be taught. It proves what objective
> evidence can be preserved about the decision that was actually played.
