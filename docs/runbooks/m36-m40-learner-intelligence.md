# M36 / M39 / M40 Learner Intelligence — Runbook

**Program:** post-M34 learner-intelligence milestone  
**Qualified packages:** M36, M39, M40  
**Implementation PRs:** #82, #83, #84  
**Post-feature baseline:** `a10cdd36925af9a09a4e10c56fa7913bddba0f44`

This is the consolidated restart and qualification path for the qualified
M36/M39/M40 learner-intelligence chain. M35, M37, and M38 are not implied to be
implemented.

## 1. Authority model

Preserve these boundaries before changing the program:

```text
M7C recurrence classification
!=
M36 current-state read model
!=
M39 evidence synthesis
!=
M40 next-action proposal
```

And:

```text
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M40 TEACH_CONCEPT != M9 intervention selection
M40 ASSIGN_PRACTICE != M10 practice evidence
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
M40 WAIT_FOR_REAL_GAME_EVIDENCE != mastery
transparent M40 policy != empirically optimal pedagogy
```

M7/M7C, M9, M10, and M11 remain authoritative for hypothesis/recurrence,
intervention selection, bounded outcome evidence, and longitudinal learner state.

## 2. Package map

| Package | PR | Purpose |
| --- | --- | --- |
| M36 | #82 | Deterministic current participant learner-state read model over M7/M9/M10/M11 + optional K7. |
| M39 | #83 | Deterministic explanation of one exact current M7C hypothesis assessment, including contradiction/control evidence and gaps. |
| M40 | #84 | Transparent ranked next-action proposal over active M36/M39 state under a versioned heuristic policy. |

## 3. M36 public API

```python
from chess_mentor_engine.longitudinal import (
    build_learner_state_read_model,
    validate_learner_state_read_model,
)
```

Typical inputs:

```text
one exact M11 LearnerStateSnapshot
exact current M7 HypothesisRevision records
optional M9 InterventionSelectionDecision records
optional K7 HypothesisKnowledgeProjection records
created_at
```

Output schema:

```text
m36.learner-state-read-model.v1
```

Per current hypothesis it may expose:

- exact hypothesis/current revision identity;
- statement and scope;
- unresolved alternatives;
- lifecycle state;
- current M7C status + exact assessment ref;
- M10 outcome dimensions;
- M9 selection/intervention refs;
- optional K7 concept IDs and semantic-coverage counts.

### M36 rejection expectations

M36 should fail closed for:

- missing current revisions;
- stale revision identity/fingerprint;
- extra non-current revisions;
- cross-participant M9 decisions;
- M9 decisions for non-current revisions;
- duplicate or non-current K7 projections;
- K7 projection/revision mismatch;
- tampered deterministic rebuilds.

It does not mutate M7/M11 or create M9 decisions.

## 4. M39 public API

```python
from chess_mentor_engine.learner_intelligence import (
    build_hypothesis_evidence_synthesis,
    validate_hypothesis_evidence_synthesis,
)
```

Required inputs:

```text
participant_id
exact current M36 LearnerStateReadModel
exact current M7 HypothesisRevision
exact M7C HypothesisAssessment referenced by M36
optional exact K7 HypothesisKnowledgeProjection referenced by M36
created_at
```

Output schema:

```text
m39.hypothesis-evidence-synthesis.v1
```

M39 preserves:

- M36, M7 revision, M7C assessment, and M7C policy identities;
- M7C status + status reasons;
- eligible/excluded/support/independent-support/contradiction/counterexample/
  context-exception/unclear/mixed counts;
- every recurrence-unit relation verbatim;
- source games/positions and evidence-link references;
- contradiction/counterexample/competing-explanation review refs/states;
- optional K7 concept context per covered recurrence unit;
- explicit evidence gaps;
- bounded future-change conditions.

### M39 rejection expectations

Fail closed for:

- participant mismatch;
- non-current revision;
- M7C assessment/revision mismatch;
- M36/M7C assessment ID/fingerprint/status drift;
- cross-participant recurrence units;
- missing K7 projection when M36 references one;
- supplied K7 projection absent from M36;
- K7/M7C or K7/revision identity drift;
- tampered rebuild output.

M39 never recalculates recurrence; M7C remains authoritative.

## 5. M40 public API

```python
from chess_mentor_engine.learner_intelligence import (
    build_default_next_session_policy,
    build_next_session_plan,
    validate_next_session_plan,
    validate_next_session_policy,
)
```

Input contract:

```text
exact M36 LearnerStateReadModel
exact M39 synthesis for each assessed active hypothesis
versioned NextSessionPolicy
created_at
```

Plan schema:

```text
m40.next-session-plan.v1
```

Policy schema:

```text
m40.next-session-policy.v1
```

### Bounded action vocabulary

```text
COLLECT_NEW_EVIDENCE
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
TEACH_CONCEPT
ASSIGN_PRACTICE
RUN_NEAR_TRANSFER_TEST
RUN_FAR_TRANSFER_TEST
WAIT_FOR_REAL_GAME_EVIDENCE
```

### Default action priorities

```text
PRESENT_CONTROL              100
CHALLENGE_HYPOTHESIS          95
RUN_FAR_TRANSFER_TEST         90
RUN_NEAR_TRANSFER_TEST        85
ASSIGN_PRACTICE               80
TEACH_CONCEPT                  75
COLLECT_NEW_EVIDENCE           70
WAIT_FOR_REAL_GAME_EVIDENCE    60
```

The ranking is an explicit policy contract, not an empirically validated universal
pedagogy.

### Default within-hypothesis routing

```text
no M7C status
    -> COLLECT_NEW_EVIDENCE

insufficient / isolated / candidate_recurrence
    -> COLLECT_NEW_EVIDENCE

unclear
    -> CHALLENGE_HYPOTHESIS

contradicted
    -> PRESENT_CONTROL

supported_recurrence + no contradiction/counterexample/context-exception evidence
    -> CHALLENGE_HYPOTHESIS

supported_recurrence + unresolved alternatives
    -> CHALLENGE_HYPOTHESIS

supported_recurrence + no M9 selection
    -> TEACH_CONCEPT

supported_recurrence + mixed M9 state
    -> COLLECT_NEW_EVIDENCE

selected M9 intervention + practice not supported
    -> ASSIGN_PRACTICE

practice supported + near transfer not supported
    -> RUN_NEAR_TRANSFER_TEST

near transfer supported + far transfer not supported
    -> RUN_FAR_TRANSFER_TEST

far transfer supported
    -> WAIT_FOR_REAL_GAME_EVIDENCE
```

Even when current real-game transfer is supported, M40 does not infer mastery.

### M40 rejection expectations

Fail closed for:

- policy fingerprint drift;
- duplicate syntheses per revision;
- missing M39 synthesis for an assessed active hypothesis;
- synthesis participant mismatch;
- synthesis/current-revision mismatch;
- synthesis/read-model identity drift;
- synthesis/M36 M7C status or assessment mismatch;
- synthesis supplied for a hypothesis with no current M7C status;
- extra synthesis for a retired/superseded/unreferenced revision;
- duplicate M10 outcome dimensions;
- no active hypothesis;
- tampered plan rebuild.

## 6. Content-addressed chain

A normal derived chain should preserve exact identity:

```text
M11 snapshot
   |
   v
M36 read_model_id + fingerprint
   |
   + exact M7C assessment
   + exact K7 projection when present
   v
M39 synthesis_id + fingerprint
   |
   + exact M40 policy fingerprint
   v
M40 plan_id + fingerprint
```

If a current revision, M7C assessment, K7 projection, M36 read model, M39 synthesis,
or M40 policy changes, downstream identity must change or validation must reject the
mismatch.

## 7. Focused qualification

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
```

## 8. Full merge gate

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Independent engine witness:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite in ordinary pytest is not the independent-engine pass.
Pull-request CI is the merge authority.

## 9. Qualification provenance

### M36 / PR #82

```text
final head: 8632a743fda30b4262e9007e9e48c79ca8d9283f
merge:      d4631a8094d11454346e6703ec9dab0f06fedbb8
CI run:     34599051912
result:     full pytest + Ruff + compile + Stockfish PASS
```

### M39 / PR #83

```text
final head: 6d5a8954170129c920fbc9b09be27ab0f6315a72
merge:      43ecdaa00a0d2abdf72d1f0f88f4254cd86f05dd
CI run:     34599807350
result:     871 passed, 8 regular-job skips; Ruff/compile/Stockfish PASS
```

The first M39 candidate passed functional tests and Stockfish but Ruff found three
line-length defects. Only the formatting defects were repaired; the amended exact
head above was fully re-qualified before merge.

### M40 / PR #84

```text
final head: 78f3658a9e8ef7643c3a6e1f06f62bf2e674574b
merge:      a10cdd36925af9a09a4e10c56fa7913bddba0f44
CI run:     34600739442
result:     889 passed, 8 regular-job skips; Ruff/compile/Stockfish PASS
```

The first M40 candidate passed functional tests and Stockfish but Ruff found style
issues. The style-only repair was fully re-qualified on the final exact head before
merge.

## 10. Safe extension rules

When extending M36:

- add only information derivable from qualified current sources;
- preserve participant/current-revision identity;
- do not turn the read model into a mutation surface.

When extending M39:

- preserve every M7C relation verbatim;
- represent missing semantic coverage as missing evidence, never concept absence;
- do not add a second recurrence score/status authority.

When extending M40:

- add/change action rules through explicit policy revisions;
- keep proposal and execution separate;
- never manufacture upstream M9/M10/M11 state to satisfy a desired route;
- preserve inspectable reasons and blocking uncertainty;
- treat policy priorities as heuristics until empirical evidence justifies stronger
  claims.

## 11. Restart checklist

1. Confirm live `main` and recent merges.
2. Read `STATUS.md`, `CONTEXT.md`, `docs/product/repository-build-status.md`, and
   `docs/architecture/architecture.md`.
3. Run the focused M36/M39/M40 suites.
4. Run the full repository gate and independent Stockfish witness.
5. Verify M35/M37/M38 have not been accidentally treated as implemented.
6. Preserve M7C/M9/M10/M11 authority boundaries.
7. If building an M40 consumer, bind it to the exact plan/action identity and define
   separately what authority the consumer gains.
8. Reconcile current docs after any new qualified package.

## 12. Likely next consumers

```text
M40 CHALLENGE_HYPOTHESIS / PRESENT_CONTROL
    -> M43 candidate contradiction/control evidence acquisition

M40 TEACH_CONCEPT
    -> M41 candidate intervention matching

M40 RUN_NEAR_TRANSFER_TEST / RUN_FAR_TRANSFER_TEST
    -> M42 candidate transfer/retest scheduler

M36 + M39 + M40
    -> M44 candidate learner-progress surface
```

These are planning candidates, not approved work. Begin the next milestone with a
fresh live-main audit.
