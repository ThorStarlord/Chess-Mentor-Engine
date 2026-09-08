# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M4B DecisionComparison qualification  
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
  M4C — SelectionSignal + DiagnosticCandidate   NOT STARTED
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
```

M4A freezes how objective comparisons and later selection must preserve authority
boundaries. M4B now implements and qualifies the comparison step only.

Qualified M4B can:

- derive the actual played move from canonical game history;
- independently replay that move to the canonical child FEN;
- use root MultiPV or compatible child reanalysis;
- compare exact centipawn evidence from mover perspective for both colors;
- preserve mate symbolically rather than as a fake centipawn sentinel;
- derive checkmate/stalemate terminal child outcomes from qualified chess rules;
- preserve partial, failed, bound-limited, incompatible, and engine-inversion states;
- produce stable provenance-rich comparison identity.

See `docs/architecture/decision-comparison.md` for the implementation and
qualification record.

M4B does **not** select diagnostic positions.

## Current authorized next task

> **M4C — implement transparent `SelectionSignal` + `DiagnosticCandidate` only.**

M4C must consume qualified M4B comparison evidence and the already-qualified M1-M3
substrate while preserving the frozen M4A distinctions.

Initial M4C work may implement objective signals such as:

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

M4C must not introduce:

- player reasoning capture;
- cognitive or learner diagnosis;
- generic `blunder`/`mistake` thresholds as product truth;
- LLM ranking;
- pedagogical-value claims;
- batch quotas, controls, or M4D candidate-batch policy;
- learner hypotheses;
- Pilot 004 mutation.

## Stop condition after M4C

After M4C implementation and qualification, stop and inspect the signal/candidate
surface before authorizing M4D.

The intended sequence remains:

```text
M4A contract
→ M4B comparison                QUALIFIED
→ M4C signals/candidates         NEXT
→ STOP / REVIEW
→ M4D bounded batches/controls
→ M4Q qualification
→ STOP
→ M5 Player Decision Evidence
```

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a frozen Diagnostic Position Selection contract;
- a qualified provenance-rich objective `DecisionComparison` layer.

It may **not** yet claim that it can:

- select diagnostic positions in production;
- identify the best teaching opportunity;
- explain why a player chose a move;
- diagnose a learner weakness;
- establish recurrence;
- recommend effective training;
- demonstrate transfer or mastery.
