# 0009 - Outcome and transfer evidence contract

**Status:** Accepted for the bounded M10 implementation  
**Scope:** Feature 3 of the post-M9 execution queue

## Context

M9 chooses an exact intervention under a participant-specific applicability
mapping. Selection does not establish completion, effectiveness, transfer, or
mastery. The authorized next feature introduces outcome evidence, not a new
learner-state model, an autonomous coach, or a universal mastery score.

## Decision

The `evaluation` package owns an explicit observational chain:

```text
exact selected M9 decision + exact intervention/exercises
+ versioned outcome criterion/rubric, contexts, minima, delay, authorship
-> EvaluationPlan
-> frozen EvaluationAttempt history
-> documented PracticeCompletion
-> provenance-bearing OutcomeObservation history
-> deterministic OutcomeAssessment under the original plan
```

A plan is created no earlier than the selected M9 decision and outcome policy.
Every attempt must start after the plan is declared. Definitions from an
ineligible/unclear selection cannot be promoted by this layer. The bridge checks
selection, intervention, and nested exercise native fingerprints independently.
It retains the exact M7 hypothesis revision referenced by M9, but does not reassess
that hypothesis or change its authority lifecycle.

### Completion and outcome are different records

An attempt retains raw participant/source evidence and a bounded capture interval.
Its completion evidence must match the exact M9 exercise completion-field schema.
A practice completion cites a nonempty set of completed practice attempts. It
records that block, not compliance with free-text dosage advice and not success.

An outcome is an explicit human/model/deterministic judgment under the policy's
exact scoring-rubric fingerprint. Source references, rationale, actor/version,
instruction fingerprint, and run identity are mandatory. No score is extracted
from raw prose or inferred from completion. Results are `criterion_met`,
`criterion_not_met`, `unclear`, or `unscorable`.

### Evidence dimensions do not imply each other

Practice, near transfer, far transfer, and real-game transfer are separate
dimensions. Context assignment and exposure declarations are authored judgments,
not an implicit classifier. A matching source-game reference is mandatory for
real-game attempts; their independence units use actual game IDs, not arbitrary
session labels. Other dimensions use session IDs.

Transfer needs documented earlier practice, the explicitly configured delay,
unassisted completion, no feedback before or at freeze, and an explicit
`unexposed` declaration with exposure references and a declared history scope.
Unknown exposure or assistance is not treated as clean evidence.

M10 also scans all supplied attempts, including unsuccessful/incomplete practice,
for earlier exposure to the same board/side/castling/en-passant state. FEN clocks,
source game IDs, and position IDs cannot manufacture novelty. Reattempts cannot
erase earlier failures; simultaneous duplicates are excluded together. This is
exact-state reuse detection, not semantic near-duplicate detection.

### Conservative aggregation

Each eligible position contributes at most one outcome unit. Multiple agreeing
coders do not increase the sample size; disagreement produces an unclear unit.
All original observations remain in the ledger. Minimum positions, independent
sessions/games, and post-practice delay are explicit versioned policy parameters,
not universally validated learning thresholds.

The per-dimension result is `insufficient`, `supported`, `not_supported`, `mixed`,
or `unclear`. Counts and exact included/excluded attempt references remain
inspectable even when there is insufficient evidence. Missing scoring evidence is
not success. Every assessment binds the complete supplied ledger fingerprint.

### Claim ceiling

`Supported` means that all eligible observed units met the declared criterion
under the supplied protocol and exposure scope. It does not establish that
instruction caused improvement. `causal_effect` and `mastery` remain
`not_established`, including when all transfer dimensions are supported.
There is no automatic hypothesis revision; M11 remains outside this feature.

## Consequences and compatibility

All M10 records are immutable, version-1 content-addressed values. Append operations
return new ledgers; retries are idempotent, and an attempt occurrence cannot be
rewritten. New information changes a new assessment, never a historical one.

M1-M9, existing provider versions, and the M8 workflow/storage schemas are unchanged.
The existing generic artifact store can archive M10 JSON and declared dependencies.
Typed M10 loading/migration is not added, and storage checksums do not certify
scientific truth or complete external exposure history. An operator must provide
the complete known ledger for the declared scope and preserve original sources.

Qualification is in `tests/test_outcome_evidence.py` and
`tests/test_m10_qualification.py`. Synthetic evidence qualifies software behavior,
not real learner improvement or intervention efficacy.
