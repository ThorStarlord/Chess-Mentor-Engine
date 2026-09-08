# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M4C SelectionSignal + DiagnosticCandidate qualification  
**Relationship to roadmap:** this file complements
`chess-mentor-engine-repository-build-plan.md`. The roadmap preserves the conceptual
sequence and historical planning rationale; this file is the authority for which
milestones are actually qualified, frozen, implemented, or not started.

## Why this file exists

The original repository build plan intentionally preserved early planning language.
Its later sections still describe M1 as the recommended next implementation target,
which is now historical rather than current. Rewriting the whole planning artifact
would risk erasing useful design provenance.

Therefore:

```text
conceptual sequence / historical rationale
→ chess-mentor-engine-repository-build-plan.md

current implementation status
→ repository-build-status.md + CONTEXT.md

ratified technical decisions
→ docs/decisions/*.md

implemented technical boundaries
→ docs/architecture/*.md
```

If the roadmap's time-sensitive `Current recommendation` conflicts with this file,
this file and `CONTEXT.md` govern current status.

## Current milestone board

```text
M1 — Trustworthy Chess Evidence Substrate       QUALIFIED
M2 — Deterministic Chess Feature Extraction     QUALIFIED
M3 — Engine Evidence                            QUALIFIED
  M3A — Engine Evidence Contract                FROZEN
  M3B — Precomputed provider                    QUALIFIED
  M3C — External UCI provider                   QUALIFIED

M4 — Diagnostic Position Selection              IN PROGRESS
  M4A — Selection contract                      FROZEN
  M4B — DecisionComparison                      QUALIFIED
  M4C — SelectionSignal + DiagnosticCandidate   QUALIFIED
  M4D — SelectionPolicy + CandidateBatch        NOT STARTED
  M4Q — Full M4 qualification                   NOT STARTED

M5 — Player Decision Evidence                   NOT STARTED
M6 — Reasoning Discrepancy                      NOT STARTED
M7 — Learner Hypothesis Ledger                  NOT STARTED
M8 — Evidence-aware Tutor Session               NOT STARTED
M9 — Training Interventions                     NOT STARTED
M10 — Transfer / Mastery Evidence               NOT STARTED
M11 — Longitudinal Learner State                NOT STARTED
M12+ — CLI/UI/richer LLM productization         NOT STARTED
```

## Qualified evidence chain

The repository currently has this qualified objective evidence path:

```text
PGN
→ CanonicalGame
→ CanonicalPosition
→ PositionContextPacket
→ PositionFeaturePacket
→ PositionAnalysis
→ DecisionComparison
→ SelectionSignal[]
→ DiagnosticCandidate record
```

The final step is deliberately a record boundary rather than policy execution.
M4C can record a `DiagnosticCandidate` only when the caller supplies an opaque
selection-policy identity and the exact eligibility signal IDs. M4D will own the
versioned policy that actually decides eligibility and constructs bounded batches.

Qualified M4C can:

- validate that M2/M3 evidence matches the M4B root decision;
- derive stable, provenance-rich objective `SelectionSignal` records;
- preserve successful rank-1 decisions as first-class evidence;
- preserve exact mover-relative centipawn deltas and engine inversions;
- preserve symbolic mate relations;
- preserve raw exact top-candidate separation without applying a close-choice
  threshold;
- derive best/played move check/capture/quiet properties from qualified M2 features;
- preserve the objective fact that the root side is in check;
- suppress ordered engine-derived signals when the root M3 analysis is partial;
- record a stable `DiagnosticCandidate` with explicit policy identity and exact
  eligibility-signal provenance.

See `docs/architecture/selection-signals-and-candidates.md` for the M4C
implementation and qualification record.

M4C does **not** execute a selection policy or produce a candidate batch.

## Current authorized next task

> **M4D — implement versioned `SelectionPolicy` + `DiagnosticCandidateBatch` only.**

M4D may introduce deterministic policy mechanics such as:

- requested batch size;
- allowed/excluded objective signal kinds;
- explicit centipawn tolerances/bands;
- a versioned `MULTIPV_CLOSE_CHOICE` threshold over M4C's raw separation signal;
- quotas by objective signal family;
- per-game maximums;
- minimum successful/control count;
- deterministic near-duplicate suppression once the rule is precisely defined;
- deterministic tie-breaking;
- explicit exclusions and quota shortfalls;
- stable `DiagnosticCandidateBatch` identity and provenance.

M4D must preserve the frozen M4A distinction:

```text
objective candidate selection
!= learner diagnosis
!= pedagogical ranking
```

M4D must not introduce:

- player reasoning capture;
- cognitive or learner diagnosis;
- universal `blunder`/`mistake`/`inaccuracy` thresholds as product truth;
- LLM ranking;
- pedagogical-value claims;
- learner hypotheses;
- Pilot 004 mutation.

## Stop condition after M4D

After M4D implementation and qualification, stop and review the complete bounded
selection surface before M4Q.

The intended sequence remains:

```text
M4A contract                         FROZEN
→ M4B comparison                     QUALIFIED
→ M4C signals/candidate record       QUALIFIED
→ STOP / REVIEW
→ M4D policy + bounded batches       NEXT
→ STOP / REVIEW
→ M4Q full M4 qualification
→ STOP
→ M5 Player Decision Evidence
```

M4 overall remains **IN PROGRESS**, not qualified. M5 remains unauthorized until M4Q.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a frozen Diagnostic Position Selection contract;
- a qualified provenance-rich objective `DecisionComparison` layer;
- a qualified transparent objective `SelectionSignal` layer;
- a qualified immutable `DiagnosticCandidate` recording boundary with explicit policy
  identity and eligibility-signal provenance.

It may **not** yet claim that it can:

- execute the complete diagnostic-position selection policy;
- produce qualified bounded candidate/control batches;
- identify the best teaching opportunity;
- explain why a player chose a move;
- diagnose a learner weakness;
- establish recurrence;
- recommend effective training;
- demonstrate transfer or mastery.
