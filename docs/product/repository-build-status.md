# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M4A Diagnostic Position Selection contract freeze  
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
  M4B — DecisionComparison                      NOT STARTED
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

The repository currently has a qualified objective evidence substrate:

```text
PGN
→ CanonicalGame
→ CanonicalPosition
→ PositionContextPacket
→ PositionFeaturePacket
→ PositionAnalysis
```

M4A now freezes how later code may derive objective decision comparisons and select
bounded evidence-gathering candidates from that substrate.

M4A does **not** implement the selector.

## Current authorized next task

> **M4B — implement `DecisionComparison` only.**

M4B must implement the frozen rules in ADR 0003 and
`docs/architecture/diagnostic-position-selection.md`, including:

- authoritative played-move provenance from canonical game history;
- compatible root/child engine-evidence pairing;
- exact centipawn comparison from mover perspective;
- mate-aware symbolic comparison without centipawn sentinels;
- terminal child outcome handling;
- partial/failure/bound evidence preservation;
- engine-evidence inversion preservation;
- deterministic comparison identity and serialization.

M4B must **not** implement:

- batch selection;
- learner reasoning capture;
- cognitive diagnosis;
- LLM ranking;
- pedagogy;
- learner hypotheses.

## Stop condition after M4B

After M4B implementation and qualification, stop and review the comparison evidence
before starting M4C.

The intended sequence remains:

```text
M4A contract
→ M4B comparison
→ M4C signals/candidates
→ M4D bounded batches/controls
→ M4Q qualification
→ STOP
→ M5 Player Decision Evidence
```

## Current claim ceiling

The repository may currently claim that it has qualified deterministic chess state,
qualified deterministic board features, and qualified provenance-bound engine
evidence.

After M4A it may additionally claim that the Diagnostic Position Selection **contract
is frozen**.

It may not yet claim that it can:

- select diagnostic positions in production;
- explain why a player chose a move;
- diagnose a learner weakness;
- establish recurrence;
- recommend effective training;
- demonstrate transfer or mastery.
