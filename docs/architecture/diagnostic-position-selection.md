# M4 — Diagnostic Position Selection

## Status

**M4A — Diagnostic Position Selection contract is frozen. Implementation has not started.**

This document defines the evidence and selection boundary that M4 implementations
must satisfy. It does not authorize player-reasoning inference, learner diagnosis,
pedagogical ranking, or LLM-based selection.

M1, M2, and M3 remain the qualified upstream evidence substrate.

## Problem

A game can contain dozens of legal decisions, and a game corpus can contain
thousands. Engine analysis can identify objective move quality, but the largest
engine loss is not automatically the most informative decision to ask a learner
about.

M4 therefore answers a deliberately narrower question:

> Which objectively characterized decisions are eligible to become bounded,
> inspectable evidence-gathering candidates?

M4 does **not** answer:

> Why did the player make this decision?

That question requires Player Decision Evidence and later learning-inference
milestones.

```text
objective severity
!= diagnostic information value
!= learner diagnosis
!= pedagogical value
```

## Boundary

M4 is downstream of the qualified chess-truth and engine-evidence layers:

```text
CanonicalGame / CanonicalPosition
+ PositionContextPacket
+ PositionFeaturePacket
+ PositionAnalysis
        |
        v
DecisionComparison
        |
        v
SelectionSignal[]
        |
        v
SelectionPolicy
        |
        v
DiagnosticCandidate
        |
        v
DiagnosticCandidateBatch
```

The layers have distinct authority:

- `DecisionComparison` describes an objective comparison between a played decision
  and engine evidence.
- `SelectionSignal` describes a transparent objective property relevant to candidate
  eligibility.
- `SelectionPolicy` decides which signals and quotas matter for one selection task.
- `DiagnosticCandidate` records why a position was selected under a specific policy.
- `DiagnosticCandidateBatch` records the bounded set, controls, exclusions, and
  shortfalls produced by that policy.

No layer may silently promote selection into a claim about learner psychology.

## Decision-point eligibility

A position is eligible for M4 decision comparison only when all of the following are
traceable:

1. the root `CanonicalPosition` belongs to a `CanonicalGame`;
2. the game contains an actual played move from that root position;
3. the canonical child position after the played move is available and replayable;
4. root and played-move evidence can be tied to explicit M3 analysis records;
5. required engine evidence satisfies the compatibility and completion rules below.

A terminal root position is not a decision point and cannot become a move-selection
candidate.

The first M4 implementation must derive the played move from canonical game history,
not from an unrelated annotation field.

## DecisionComparison

`DecisionComparison` is a derived record. It does not mutate or extend
`PositionAnalysis` with cross-position fields.

Conceptually it must preserve at least:

```yaml
comparison_id:
position_id:
game_id:
played_move_uci:
side_to_move:

root_analysis_ref:
played_evaluation_source:
played_analysis_ref: optional
played_root_line_rank: optional

best_move_uci:
best_evaluation:
played_evaluation:

compatibility:
comparison_kind:
preference:
exact_centipawn_delta_for_mover: optional
mate_relation: optional

provenance:
```

The exact field names may evolve during implementation, but the authority separation
and comparison semantics in this document are frozen.

## Played-move evaluation sources

M4 may obtain the played-move evaluation in two ways.

### Root MultiPV line

If the played move is present among the root `PositionAnalysis.lines`, its line
evaluation may be used directly.

The comparison must retain the line rank and root result fingerprint.

### Compatible child reanalysis

If the played move is not present in root MultiPV, M4 may use the rank-1 evaluation
from the canonical child position after the played move.

This is a comparison between two separate engine observations and must retain both
result fingerprints.

The child position must be the canonical consequence of the actual played move. M4
must not construct an arbitrary FEN supplied independently of game provenance.

## Analysis compatibility

M4 must not calculate a quantitative move-loss value by comparing materially
different engine regimes.

For the initial qualified implementation, two analyses are directly compatible only
when they share the same analysis regime except for source position identity.

The compatibility key must include:

```text
provider name/version/protocol
engine name/version
the available engine binary SHA-256
engine artifact identities
normalized engine options
AnalysisRequest.search_limit kind/value
AnalysisRequest.multipv
AnalysisRequest.supervisor_timeout_ms
```

This conservative rule intentionally treats the complete `AnalysisRequest` as part
of the comparison regime. A later ADR may weaken the rule if empirical evidence
supports a narrower compatibility key.

If required provenance is missing or materially different, M4 records the comparison
as incompatible instead of manufacturing a severity score.

```text
same chess position semantics
!= compatible engine-analysis regime
```

## Completion and score-bound policy

The initial M4 comparison layer is deliberately conservative.

### Complete evidence

Quantitative or ordered move-quality comparison requires complete M3 evidence.

### Partial evidence

A partial analysis remains valid M3 evidence but is not sufficient for the initial
M4 severity comparison. M4 may preserve it as an exclusion/rationale record.

### AnalysisFailure

An `AnalysisFailure` cannot be converted into a move-quality judgment.

### Exact scores

Only `bound == "exact"` scores participate in the initial ordered comparison rules.

### Lower/upper bounds

`lower` and `upper` engine scores remain evidence, but M4 initially records them as
bound-limited/incomparable for severity ranking. It must not silently treat them as
exact values.

A later explicit extension may add interval-aware comparison.

## Fixed mover perspective

M3 stores evaluations from a fixed White perspective. M4 derives mover-relative
preference without changing the stored engine evidence.

For exact centipawn values:

```text
white mover value = white-perspective centipawns
black mover value = -white-perspective centipawns
```

For two exact centipawn evaluations:

```text
exact_centipawn_delta_for_mover
    = best candidate mover value - played move mover value
```

The signed delta must be preserved. Do not clamp negative values to zero.

If a follow-up analysis makes the played move appear better than the root rank-1
candidate, M4 records an engine-evidence inversion. It must not relabel rank 1 or
silently rewrite the evidence to make the delta non-negative.

## Mate-aware comparison

M3 deliberately represents mate as `winner + plies_to_mate`; M4 preserves that
semantic type.

M4 must never encode mate as a fake centipawn sentinel such as `+100000`.

For exact evaluations, mover preference follows these symbolic rules:

1. a forced mate for the mover is better than any non-mate centipawn evaluation;
2. any non-mate centipawn evaluation is better than a forced mate for the opponent;
3. when both evaluations are forced mates won by the mover, fewer plies to mate is
   preferred;
4. when both evaluations are forced mates won by the opponent, more plies to mate is
   preferred;
5. mate and centipawn comparisons do not produce a centipawn delta.

M4 must retain a categorical `mate_relation` or equivalent, sufficient to distinguish
at least:

- forced mate preserved;
- forced mate missed;
- forced mate allowed;
- forced mate escaped or evidence inversion;
- mate distance improved/worsened;
- incomparable bound-limited mate evidence.

The exact user-facing wording is deferred.

## Terminal child positions

M3 terminal analyses contain no candidate lines and therefore no engine score.

When an actual played move reaches a terminal child position, M4 must derive the
terminal board outcome from the qualified chess-rules substrate rather than invent an
engine evaluation.

At minimum the implementation must distinguish:

```text
checkmate
stalemate / non-checkmate terminal draw when supported
```

A terminal outcome may participate in categorical comparison, but never by assigning
a fabricated centipawn number.

## Comparison result classes

The initial implementation must be able to preserve at least these outcomes:

```text
better_for_mover
approximately_equal_under_policy
worse_for_mover
engine_evidence_inversion
incompatible_analysis_regime
partial_evidence
bound_limited
terminal_relation
incomparable
```

`approximately_equal_under_policy` is not a universal chess constant. Its tolerance
must come from a versioned `SelectionPolicy` or comparison policy configuration.

## SelectionSignal

A `SelectionSignal` is a transparent, reconstructable property of one decision. It
is not a learner trait or pedagogical label.

The first implementation may support objective signals such as:

```text
PLAYED_EQUALS_RANK_1
PLAYED_DIFFERS_FROM_RANK_1
EXACT_CP_DELTA
MATE_RELATION
TOP_CANDIDATE_SEPARATION
MULTIPV_CLOSE_CHOICE
BEST_MOVE_IS_CHECK
BEST_MOVE_IS_CAPTURE
BEST_MOVE_IS_QUIET
PLAYED_MOVE_IS_CHECK
PLAYED_MOVE_IS_CAPTURE
PLAYED_MOVE_IS_QUIET
ROOT_SIDE_IS_IN_CHECK
ENGINE_EVIDENCE_INVERSION
```

Threshold-bearing signals must retain the raw underlying value and the policy
threshold/version that caused the signal to fire.

M4A does **not** freeze universal centipawn thresholds for words such as `blunder`,
`mistake`, or `inaccuracy`.

## Interpretive labels explicitly excluded from M4

M4 must not emit selection signals such as:

```text
poor calculation
failed candidate generation
missed opponent resource
tunnel vision
bad planning
weak strategic understanding
needs tactics training
high-value teaching moment
```

Those labels require player evidence, analyst/model inference, pedagogy, or a later
validated contract.

Even familiar chess labels such as `prophylactic decision`, `strategic plan choice`,
or `defensive resource` must not be promoted to deterministic M4 signal kinds until
an objective definition is separately frozen.

## SelectionPolicy

Selection policy is separate from evidence generation.

A versioned `SelectionPolicy` may define:

- requested batch size;
- allowed/excluded signal kinds;
- centipawn tolerances and bands;
- quotas by signal family;
- per-game maximums;
- minimum control count;
- near-duplicate suppression rules;
- deterministic tie-breaking;
- whether incompatible/partial/bound evidence is excluded or surfaced separately.

Thresholds belong to policy configuration rather than hard-coded product truth.

Changing a threshold or quota creates a new policy identity/version. It does not
rewrite prior candidates.

## DiagnosticCandidate

`DiagnosticCandidate` means:

> This position was selected as eligible for evidence gathering under this explicit
> policy and these objective signals.

It does **not** mean:

> This position proves a learner weakness or is definitely valuable pedagogy.

Each candidate must be able to answer:

```text
Why was this position eligible?
Which exact M1/M2/M3 evidence supports the signals?
Which selection policy selected it?
What evidence was excluded or incomparable?
```

Candidate identity must be stable for the same position, evidence references, signal
set, and selection-policy identity.

## Successful/control decisions are first-class

M4 must be able to select objectively successful decisions, including positions where
the played move equals engine rank 1 or is policy-equivalent to the preferred engine
choice.

This is required because later learner hypotheses must be able to encounter evidence
that does **not** fit an apparent weakness pattern.

Within M4, a `control` role means a deliberately sampled objectively successful or
low-severity decision. It does not yet mean contradiction of a specific learner
hypothesis.

```text
error-only sampling
=> structurally biased learner evidence
```

## DiagnosticCandidateBatch

A batch is a bounded, provenance-rich selection result.

Conceptually it preserves:

```yaml
batch_id:
policy_id:
source_game_ids:
requested_count:
selected_candidate_ids:
control_candidate_ids:
selection_counts_by_signal:
excluded_positions:
shortfall:
tie_break_record:
provenance:
```

The initial implementation must be deterministic for the same candidate pool,
evidence, and policy.

If the pool cannot satisfy a requested quota, the batch must report the shortfall.
It must not silently pad the batch with positions that failed the policy.

## Near-duplicate suppression

A batch should not be dominated by repeated manifestations of essentially the same
game moment.

The initial policy mechanism must at least support deterministic per-game caps and
may support position/ply-distance suppression once a precise rule is implemented.

Semantic similarity based on embeddings or LLM judgment is deferred.

## Candidate generation is not final pedagogical ranking

M4 is an evidence-acquisition layer.

```text
candidate generation
!= pedagogical ranking
```

M4 may rank candidates under explicit objective policies, but it may not claim that
rank 1 is the best lesson for the learner. That requires downstream player evidence,
learner inference, and pedagogy.

## M4 implementation sequence

### M4A — contract freeze

This document and ADR 0003 freeze the selection semantics before implementation.

Status after this step:

> **M4A CONTRACT FROZEN — IMPLEMENTATION NOT STARTED**

### M4B — DecisionComparison

Implement:

- played-move provenance;
- compatible root/child analysis pairing;
- exact centipawn comparison;
- mate-aware symbolic comparison;
- terminal child outcomes;
- explicit incomparable/inversion states;
- deterministic comparison serialization/identity.

Do not implement batch ranking yet.

### M4C — SelectionSignal + DiagnosticCandidate

Implement the first transparent objective signal set and candidate provenance.

Do not add player reasoning or LLM-derived signal kinds.

### M4D — SelectionPolicy + DiagnosticCandidateBatch

Implement bounded deterministic batch selection, quotas, controls, exclusions,
shortfalls, and deterministic tie-breaking.

### M4Q — qualification

M4 becomes qualified only after the complete bounded selection path is tested and the
exact qualified head passes repository CI.

## Qualification corpus

Before M4Q, freeze exact fixtures covering at least:

1. obvious large exact-centipawn loss;
2. quiet engine-preferred move;
3. side-to-move in check / defensive decision;
4. multiple close engine candidates;
5. clearly separated top candidate;
6. forced mate missed;
7. forced mate allowed;
8. correct rank-1 played move;
9. correct quiet/control decision;
10. custom-FEN decision;
11. promotion decision;
12. prior research board-context position:

```text
r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22
```

The implementation may add fixtures, but it must not remove required categories merely
because they expose a defect.

Frozen research artifacts remain immutable. M4 qualification must not retroactively
rewrite Pilot 001–004 position-selection evidence or participant exposure state.

## Qualification gates

M4 may be declared qualified only when all applicable gates pass:

```text
DecisionComparison contract implemented
played-move provenance preserved
analysis-regime compatibility enforced
exact cp comparison tested for both mover colors
mate-aware comparison tested
terminal child behavior tested
partial/failure/bound evidence does not masquerade as exact severity
engine-evidence inversion preserved
transparent SelectionSignals implemented
successful/control decisions selectable
versioned SelectionPolicy implemented
bounded deterministic batch generation implemented
quota shortfalls explicit
selection rationale reconstructable
no learner-psychology claims
no LLM dependency
no pedagogical-effectiveness claims
M1-M3 suites remain green
precomputed/fake-engine fixtures pass
external Stockfish qualification witness passes where applicable
pytest passes
Ruff passes
exact candidate-head CI passes
post-merge CI passes
```

## Claim ceiling

A qualified M4 may claim:

> Chess Mentor Engine can derive transparent, provenance-rich objective decision
> comparisons and use versioned deterministic policies to select bounded candidate
> sets containing both potentially informative decisions and successful controls.

M4 may **not** claim:

- why the player made a move;
- that a selected position demonstrates a stable learner weakness;
- that a selected position is definitely the best teaching opportunity;
- that a centipawn loss measures cognitive severity;
- that recurrence has been established;
- that an intervention is warranted;
- that learning occurred.

Those claims require later evidence layers.

## Explicitly deferred

M4A does not freeze or implement:

- universal `blunder`/`mistake`/`inaccuracy` thresholds;
- subjective strategic/tactical motif taxonomy;
- LLM-based position ranking;
- embedding similarity;
- player-response capture;
- Reasoning Discrepancy;
- learner hypotheses;
- contradiction against a specific learner hypothesis;
- training selection;
- transfer/mastery;
- persistent learner state;
- UI presentation.

## Governing principle

> Diagnostic selection is not diagnosis. M4 chooses where to gather evidence; it
> does not decide what is wrong with the learner.
