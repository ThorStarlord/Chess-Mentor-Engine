# M4D — SelectionPolicy and DiagnosticCandidateBatch

## Status

**M4D — SelectionPolicy + DiagnosticCandidateBatch is implemented and qualified. M4Q has not started. M4 overall is not yet qualified.**

This record documents the implemented M4D boundary and its qualification evidence.
The frozen selection contract remains ADR 0003 and
`docs/architecture/diagnostic-position-selection.md`; this record does not reopen or
weaken that contract.

## Purpose

M4D answers one bounded evidence-acquisition question:

> Given qualified M4C objective signals, which decisions satisfy an explicit versioned
> selection policy, and how can those eligible decisions be assembled into a bounded,
> reproducible candidate/control batch without hiding exclusions or shortfalls?

```text
DecisionComparison
+ SelectionSignal[]
        |
        v
SelectionPolicy
        |
        v
SelectionDecision
        |
        v
DiagnosticCandidate
        |
        v
DiagnosticCandidateBatch
```

M4D does not infer player psychology, rank pedagogical value, or capture player
reasoning.

## Public implementation

M4D extends `chess_mentor_engine.selection` with:

```text
SelectionQuota
SelectionPolicy
SelectionRuleMatch
SelectionDecision
PolicySelectionResult
SelectionPolicyError
apply_selection_policy

BatchExclusion
QuotaOutcome
DiagnosticCandidateBatch
DiagnosticCandidateBatchError
build_diagnostic_candidate_batch
```

## Versioned policy semantics

`SelectionPolicy` contains explicit configuration rather than universal chess labels.
The qualified surface includes:

```text
policy_id
version
requested_size
candidate_min_cp_delta
control_max_cp_delta
close_choice_max_cp
candidate_mate_relations
include_rank1_controls
excluded_signal_kinds
minimum_controls
maximum_per_game
quotas
```

Thresholds in this object mean only that a named policy uses those values. They do
not establish universal definitions of `blunder`, `mistake`, `inaccuracy`, or
pedagogical importance.

The policy exposes two different identities:

```text
SelectionPolicyIdentity = policy_id + version
policy fingerprint       = SHA-256 over the complete canonical policy configuration
```

Batch construction requires both to match the decisions it consumes. Therefore a
caller cannot silently change thresholds or quotas while retaining the same ID/version
and reuse earlier policy decisions as though they came from the same configuration.

Changing policy values changes the fingerprint; changing the version changes both the
policy identity and downstream candidate/batch identity.

## Inspectable eligibility decisions

`apply_selection_policy` validates that every supplied M4C signal belongs to the same
M4B decision. It returns a `SelectionDecision` containing:

```text
position/game/comparison identity
policy identity
policy fingerprint
eligible flag
role: candidate | control | excluded
matched rules
eligibility signal IDs
exclusion reasons
```

Every `SelectionRuleMatch` retains:

```text
rule_id
source signal_id
signal kind
observed raw value
operator
configured threshold/value
```

This makes threshold-bearing selection reconstructable rather than hiding policy
judgment inside a candidate label.

## Candidate rules

The qualified v1 mechanics can select candidates from:

- exact mover-relative centipawn delta at or above a configured threshold;
- symbolic mate relations explicitly named by policy;
- M4C raw `TOP_CANDIDATE_SEPARATION` at or below a configured close-choice threshold.

The close-choice rule is deliberately M4D policy interpretation. M4C still owns only
the raw exact separation and does not claim that a universal notion of `close` exists.

Configured objective signal kinds may hard-exclude an otherwise eligible position.
For example, a policy may exclude `ENGINE_EVIDENCE_INVERSION` rather than silently
normalizing it into ordinary severity.

## Successful/control sampling

M4D can classify objectively successful or low-severity decisions as operational
controls under policy, including:

- `PLAYED_EQUALS_RANK_1` evidence;
- non-negative exact centipawn delta at or below a configured control threshold.

Within M4, `control` means a deliberately sampled objectively successful or
low-severity decision. It does **not** mean contradiction of a learner hypothesis;
that stronger interpretation requires later player and learner evidence.

Candidate rules take precedence when a decision satisfies both candidate and control
rules. The resulting role is retained explicitly.

## Deterministic batch construction

`build_diagnostic_candidate_batch` consumes only `PolicySelectionResult` records from
the exact same policy identity and policy fingerprint.

The qualified algorithm:

1. canonicalizes source order deterministically;
2. attempts to satisfy the configured minimum control count;
3. attempts to satisfy quota minimums in deterministic signal-kind order;
4. fills remaining capacity in deterministic source order;
5. enforces requested batch size;
6. enforces per-game maximums;
7. enforces quota maximums;
8. records all non-selected source decisions and their reasons;
9. records size, control, and quota shortfalls instead of weakening policy;
10. fingerprints the complete source/result state into a stable batch identity.

The deterministic fallback order uses game ID, canonical root ply, and candidate ID.
Shuffling input order does not change the resulting batch.

## Batch provenance and shortfalls

`DiagnosticCandidateBatch` retains:

```text
batch_id
selection policy identity
policy fingerprint
requested size
actual size
selected candidates
control candidate IDs
source pool count
source candidate IDs
source-pool fingerprint
quota outcomes
exclusions
size shortfall
control shortfall
```

`QuotaOutcome` independently records minimum, maximum, selected count, and quota
shortfall for each configured objective signal family.

If policy constraints cannot be satisfied, M4D exposes the failure of the requested
composition. It never pads the batch with a position that failed eligibility.

Examples of explicit non-selection evidence include:

```text
no_eligibility_rule_matched
excluded_signal_kind:<kind>
maximum_per_game
quota_maximum:<kind>
batch_capacity
not_selected_under_deterministic_order
```

## Near-duplicate suppression is deferred

The current qualified M4D surface does not implement a chess-position similarity or
near-duplicate heuristic. A vague similarity rule would introduce an unqualified
subjective proxy. Per-game caps provide a deterministic diversity constraint for v1.
A future similarity rule requires a precise versioned definition before admission.

## Qualification evidence

### Exact qualified implementation candidate

```text
3f927ef94dea85fbb801a52c25421960e8c189d0
```

### Exact-head CI

GitHub Actions run:

```text
34215835793
```

Result:

```text
97 passed
8 intentionally skipped external-engine tests
Ruff PASS
external Stockfish integration PASS
```

The exact-head suite includes M4D policy/batch boundary tests plus a deterministic
end-to-end precomputed qualification corpus.

### Deterministic M1→M4D corpus

The qualification corpus executes:

```text
PGN
→ CanonicalGame / CanonicalPosition
→ PositionFeaturePacket
→ precomputed PositionAnalysis
→ DecisionComparison
→ SelectionSignal[]
→ SelectionPolicy
→ SelectionDecision / DiagnosticCandidate
→ DiagnosticCandidateBatch
```

It contains at least:

- a successful rank-1 control;
- a clear exact-centipawn deviation candidate;
- a symbolic forced-mate candidate.

Reversing source-result order produces the identical batch. The corpus also verifies
control and mate quota satisfaction and stable source-pool provenance.

### Superseded qualification attempts

The first M4D candidate failed because a test built a batch from the same policy
ID/version with a different configuration. The implementation's policy-fingerprint
guard correctly rejected that drift; the test was fixed rather than weakening the
guard.

A later candidate passed all behavioral tests but failed Ruff on two line-length
findings. Those formatting defects were fixed and the final exact candidate above
requalified from scratch.

### Implementation merge

```text
3c0b2edb6d21f3a94f52977b65a00534b5218651
```

The merge is tree-identical to the exact qualified implementation candidate: comparing
the two commits produced no changed files.

### Post-merge CI

GitHub Actions run on the exact implementation merge:

```text
34215921952
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M4D — SELECTIONPOLICY + DIAGNOSTICCANDIDATEBATCH: QUALIFIED**

The qualified claim is deliberately bounded:

> Chess Mentor Engine can deterministically evaluate objective M4C signals under
> explicit versioned selection policies and construct reproducible bounded
> candidate/control batches with inspectable eligibility, policy/config provenance,
> quotas, per-game caps, exclusions, and visible size/control/quota shortfalls,
> without inferring learner psychology or pedagogical value.

## Explicitly not implemented

M4D does not implement:

- universal `blunder` / `mistake` / `inaccuracy` truth;
- learner or cognitive diagnosis;
- Player Decision Evidence;
- Reasoning Discrepancy;
- recurrence or learner hypotheses;
- LLM selection or ranking;
- pedagogical-value scoring;
- interventions or mastery;
- near-duplicate similarity heuristics;
- Pilot 004 mutation.

## Next authorized boundary

M4D closes the implementation slices defined by ADR 0003, but **M4 overall is still
not qualified**.

The only next authorized task is:

> **M4Q — full M4 qualification and bounded-selection surface review.**

M4Q should primarily qualify the complete M4A→M4D evidence-acquisition path rather
than add learner-facing features. M5 Player Decision Evidence remains unauthorized
until M4Q passes.

## Governing principle

> A policy threshold is not chess truth. A control is not a contradiction of a learner
> hypothesis. A selected batch is not a lesson plan. M4D makes bounded evidence
> acquisition explicit and reproducible.
