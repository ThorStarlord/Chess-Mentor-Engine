# ADR 0003 — Diagnostic Position Selection Contract

## Status

Accepted for M4A. Implementation is not authorized by this ADR alone.

## Context

M1 through M3 establish a qualified evidence substrate:

```text
canonical chess state
→ deterministic chess features
→ provenance-bound engine evidence
```

The next product problem is selection, not diagnosis. A game corpus can contain many
positions, but asking the learner about every move is impractical. Ranking only by
centipawn loss would also structurally bias evidence collection toward failures and
would confuse objective severity with diagnostic value.

The repository therefore needs a bounded contract for deciding which positions are
eligible for later evidence gathering without inferring why the player chose a move.

## Decision

M4 will be an evidence-acquisition layer with this separation:

```text
DecisionComparison
→ SelectionSignal[]
→ SelectionPolicy
→ DiagnosticCandidate
→ DiagnosticCandidateBatch
```

Each layer is independently inspectable and must preserve provenance.

## Decision 1 — Selection is not learner diagnosis

A selected position means only that it satisfied an explicit selection policy using
traceable objective evidence.

M4 must not emit claims such as:

- `poor calculation`;
- `missed opponent resource`;
- `tunnel vision`;
- `weak strategy`;
- `needs tactics training`.

Those claims require player evidence and later learning-inference/pedagogy contracts.

## Decision 2 — Played-move comparison remains derived

M3 `PositionAnalysis` continues to describe one root position only.

M4 derives played-move comparison from either:

1. the played move's root MultiPV line, when present; or
2. a compatible analysis of the canonical child position after the actual played move.

M4 must not add `evaluation_before`, `evaluation_after`, or centipawn-loss fields to a
single M3 root-analysis record.

## Decision 3 — Canonical game history owns the played move

The played move used by M4 must come from qualified canonical game history.

An unrelated annotation, model-generated move, or manually supplied move cannot
silently become the authoritative played decision.

The canonical child position must be replay-consistent with that move.

## Decision 4 — Direct quantitative comparison requires one analysis regime

The initial M4 implementation may calculate ordered or numeric severity only from
compatible engine evidence.

The comparison regime includes:

```text
provider name/version/protocol
engine name/version
available binary SHA-256
engine artifacts
normalized engine options
search-limit kind/value
MultiPV
supervisor timeout
```

Required root/child analysis conditions must match except for source position
identity.

If the regime differs materially, the comparison is recorded as incompatible rather
than normalized heuristically.

This intentionally conservative rule may be revisited only through a later ADR.

## Decision 5 — Complete exact evidence is the initial comparison authority

The initial M4 comparison layer treats:

- `complete` + exact evaluation as comparable;
- `partial` analysis as valid evidence but insufficient for severity comparison;
- `AnalysisFailure` as failure, never as empty success;
- lower/upper-bound scores as bound-limited, not exact.

M4 does not initially implement interval arithmetic for bounded scores.

## Decision 6 — White-perspective evidence becomes mover-relative only as a derived view

M3's stored score perspective remains White.

For exact centipawn comparisons:

```text
white mover value = white score
black mover value = -white score
```

The signed move delta is:

```text
best mover value - played mover value
```

The delta must not be clamped to zero.

If a follow-up analysis makes the played move appear stronger than root rank 1, M4
preserves an engine-evidence inversion rather than rewriting history.

## Decision 7 — Mate remains semantic, never a centipawn sentinel

M4 inherits M3's `winner + plies_to_mate` representation.

For exact mate evidence:

- forced mate for the mover outranks non-mate centipawn evaluation;
- non-mate centipawn evaluation outranks forced mate for the opponent;
- when the mover wins in both lines, fewer plies to mate is preferred;
- when the mover loses in both lines, more plies to mate is preferred.

Mate transitions produce categorical relations, not fake centipawn deltas.

## Decision 8 — Terminal child outcomes come from deterministic chess rules

M3 terminal analyses contain no candidate evaluation.

If the played move reaches a terminal child, M4 derives the terminal board outcome
from the qualified rules substrate. It must not invent an engine score for checkmate,
stalemate, or another supported terminal draw state.

## Decision 9 — SelectionSignal is objective and reconstructable

A selection signal records a concrete property such as:

- played move equals/differs from rank 1;
- exact centipawn delta;
- mate relation;
- top-candidate separation;
- close MultiPV choice;
- best/played move is check, capture, or quiet;
- root side is in check;
- engine-evidence inversion.

A signal must cite the underlying evidence and retain the raw value behind any
threshold decision.

Subjective chess or cognitive labels are not part of the initial signal taxonomy.

## Decision 10 — Thresholds and quotas belong to versioned policy

M4 does not freeze universal centipawn thresholds for `blunder`, `mistake`, or
`inaccuracy`.

Thresholds, tolerances, quotas, per-game caps, minimum control counts, and deterministic
tie-break rules belong to `SelectionPolicy` configuration.

Changing policy values creates a new policy identity/version and does not rewrite
prior candidate records.

## Decision 11 — Successful controls are first-class

The selector must be capable of selecting objectively successful decisions, including
rank-1 and policy-equivalent moves.

This prevents later learner inference from operating on an error-only sample.

Within M4, `control` means a deliberately sampled objectively successful or
low-severity decision. It does not yet mean contradiction of a particular learner
hypothesis.

## Decision 12 — Batch shortfalls remain visible

`DiagnosticCandidateBatch` must record the requested size, actual selected set,
controls, quotas, exclusions, and any shortfall.

If the source pool cannot satisfy policy constraints, the selector returns the
shortfall. It must not silently pad the batch with positions that failed the policy.

## Decision 13 — Initial selection is deterministic and LLM-free

M4's first qualified path uses deterministic evidence and versioned policies.

LLM ranking, embeddings, free-form motif classification, and pedagogical judgment are
deferred until later evidence and evaluation contracts justify them.

## Decision 14 — M4 claim ceiling

M4 may eventually claim only that it can derive objective decision comparisons and
select bounded candidate/control sets under transparent policies.

It may not claim:

- player cognitive cause;
- stable weakness;
- recurrence;
- best pedagogical opportunity;
- intervention eligibility;
- learning or mastery.

## Consequences

### Positive

- move-selection rationale remains inspectable;
- M3 engine evidence is not mutated into cross-position records;
- mate semantics remain sound;
- analysis provenance compatibility is explicit;
- error-only sampling is avoided;
- later Player Decision Evidence receives a bounded, auditable position set;
- policy changes can be compared without rewriting evidence.

### Costs

- some positions will remain incomparable under conservative evidence rules;
- child reanalysis may require additional engine work;
- MultiPV/search policy must be controlled more carefully;
- M4 will initially miss subjective high-value positions that a human coach might
  notice;
- deterministic control and diversity rules may require several iterations.

These costs are preferable to silently manufacturing diagnostic certainty.

## Alternatives considered

### Sort all moves by centipawn loss

Rejected as the architecture. Centipawn loss is useful evidence but does not define
diagnostic value and would bias sampling toward failures.

### Let an LLM choose interesting positions from PGN + engine output

Rejected for the initial milestone. It would collapse evidence generation, selection,
and interpretation into one opaque step before evaluation infrastructure exists.

### Store played-move loss directly in PositionAnalysis

Rejected because M3 intentionally scopes one analysis record to one root position.
Cross-position comparison belongs to M4.

### Convert mate to a large centipawn number

Rejected because M3 froze mate as a distinct semantic type.

### Treat partial or bound scores as exact

Rejected because it would overstate M3 evidence.

### Select only errors

Rejected because later inference requires successful/control evidence to resist
confirmation bias.

## Implementation sequence authorized by this ADR

This ADR authorizes planning for the following bounded sequence, but each step still
requires implementation qualification:

```text
M4B DecisionComparison
→ M4C SelectionSignal + DiagnosticCandidate
→ M4D SelectionPolicy + DiagnosticCandidateBatch
→ M4Q full M4 qualification
```

M5 Player Decision Evidence is not authorized until M4Q is qualified.

## Related records

- `docs/architecture/diagnostic-position-selection.md`
- `docs/architecture/engine-evidence.md`
- `docs/decisions/0002-engine-evidence-contract.md`
- `docs/product/chess-mentor-engine-repository-build-plan.md`
- `docs/product/repository-build-status.md`
