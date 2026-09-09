# M10 - Outcome and transfer evidence

## Responsibility and public API

The implementation follows [ADR 0009](../decisions/0009-outcome-transfer-evidence-contract.md).
It adds no dependencies outside the Python standard library.

| Record | Responsibility |
| --- | --- |
| `OutcomePolicy` | Exact criterion/rubric, transfer contexts, sample minima and delay |
| `EvaluationPlan` | Authored bridge to selected M9 intervention, exercises and M7 revision |
| `EvaluationAttempt` | Frozen raw evidence, completion fields, timing and exposure conditions |
| `PracticeCompletion` | Documented completed practice block; not proof of success |
| `OutcomeObservation` | Explicit scored judgment and source/actor/rubric provenance |
| `OutcomeLedger` | Immutable complete supplied history for one plan |
| `OutcomeAssessment` | Deterministic per-dimension evidence and visible exclusions |

Construct an explicit `OutcomePolicy`, then use `define_evaluation_plan`,
`reference_outcome_position`, `append_evaluation_attempt`,
`record_practice_completion`, `record_outcome_observation`, and
`assess_outcome_evidence`. `validate_outcome_ledger` rechecks structure, ownership,
exact references, exercise schema, scoring rubric, and chronology at consuming
boundaries. `reference` produces a native M10 content reference.

## Identity and immutability

`ContentRecord` calculates native identities from canonical JSON containing
`schema_version = "1"`, the record kind, and immutable dataclass fields.
Fields use typed records, tuples, and scalars; mutable lists, wrong literals, and
bool-as-integer policy values are rejected. Full fingerprints accompany shortened
human-readable IDs. Arrays that represent append history preserve order.

A plan binds original native M9 hashes; it does not reinterpret a storage envelope
hash as a native evidence hash. The M9 exercise completion schema is retained in
an `ExerciseBinding`. A later intervention/policy version needs a new plan and
new evidence; existing attempts cannot silently be rescored under that version.

## State and chronology

The ledger is append-oriented, not a mutable numeric learner score. Attempts have
an occurrence key, raw response/source, start/freeze/record timestamps and optional
observed feedback time. A same-content retry is idempotent; changing a frozen
occurrence is rejected. Practice completion must follow recording of its exact
practice inputs. Observation must follow recording of its exact frozen attempt.
Assessment cannot predate any supplied evidence.

For imported real-game evidence, use original decision/capture times and real
source references. The plan must already exist at the original decision time.
Do not backdate a new plan to make a previously studied game a prospective test.
The software validates recorded times and relationships; it cannot authenticate
an operator's account of events.

## Eligibility and assessment

Transfer requires an explicit completion anchor. An attempt must start strictly
after it and meet the policy's minimum delay, even when the configured delay is
zero. Exclusions cover incomplete attempts, assistance/unknown assistance, early
feedback, known/unknown prior exposure, absent practice, delay failures and reuse.

Exact-state reuse is based on the first four canonical Standard FEN fields. It is
independent of move clocks or import IDs. Repeats after any earlier supplied
attempt are excluded. Equal-time duplicates are all excluded. The declared
exposure history must cover relevant evidence outside this ledger; a missing
record is not an automatic claim of novelty.

For each dimension, minimum independent positions and sessions/games are checked
before a support result. Practice uses one eligible independent observation as
its minimum; transfer minima come from the policy. Missing scores, unscorable
results or coder disagreement yield uncertainty rather than support. When the
minimum is satisfied and all units are scored, all successes give `supported`,
all failures `not_supported`, and a mixture `mixed`. Counts concern independent
attempt units, not raw coder votes. The source ledger retains every coder's result.

Near/far/game outcomes do not imply one another. Even a fully supported set of
transfer dimensions does not set mastery, causal effectiveness, or learner state.

## Qualification and limitations

`test_outcome_evidence.py` isolates M10 with explicit fixture upstream references.
`test_m10_qualification.py` uses actual M9 definition/mapping/selection producers,
M1 PGN positions, and the existing SQLite store. Its M7 input is the existing M9
synthetic fixture, not a newly executed empirical learner study.

Tests cover all dimensions and result states, repeated/clock-shifted positions,
independence minima, equal-time duplicates, delayed assessment, exposure and
assistance uncertainty, coder conflict, missing scores, frozen-history conflicts,
policy/version materiality, malformed native M9 inputs, provenance mismatch,
public exports, deterministic rebuild and generic archival round trips.

The store integration preserves generic M10 JSON and a declared ledger dependency;
it does not add typed M10 recovery or certify complete transitive upstream sources.
Clinical/educational efficacy, calibrated thresholds, semantic novelty, automatic
mastery, M11 longitudinal state, CLI/UI and autonomous training remain unclaimed.

See [the operational runbook](../runbooks/m10-outcome-transfer-evidence.md).
