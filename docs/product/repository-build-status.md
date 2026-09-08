# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M4D SelectionPolicy + DiagnosticCandidateBatch qualification  
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
  M4D — SelectionPolicy + CandidateBatch        QUALIFIED
  M4Q — Full M4 qualification                   NOT STARTED / NEXT

M5 — Player Decision Evidence                   NOT STARTED / UNAUTHORIZED
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
→ SelectionPolicy
→ SelectionDecision / DiagnosticCandidate
→ DiagnosticCandidateBatch
```

M4D now supplies the deterministic policy execution that M4C intentionally left
external. Qualified M4D can:

- evaluate qualified M4C signals under an explicit policy ID/version and full policy
  fingerprint;
- retain the raw observed value, operator, configured threshold, and source signal for
  each matched rule;
- interpret M4C raw top-candidate separation under a versioned close-choice threshold;
- select symbolic mate relations without centipawn sentinels;
- classify rank-1 and configured low-severity decisions as operational controls;
- construct reproducible bounded candidate/control batches;
- enforce requested size, per-game caps, quota minima/maxima, and minimum controls;
- retain source-pool identity and deterministic ordering;
- record policy exclusions and visible size/control/quota shortfalls instead of
  silently weakening constraints;
- reject policy-configuration drift even when policy ID/version are reused.

See `docs/architecture/selection-policy-and-batches.md` for the M4D implementation
and qualification record.

M4D does **not** make M4 overall qualified. Full M4 coherence remains an M4Q gate.

## Current authorized next task

> **M4Q — full M4 qualification and bounded-selection surface review only.**

M4Q should primarily prove the complete path:

```text
M4A frozen contract
→ M4B DecisionComparison
→ M4C SelectionSignal / DiagnosticCandidate
→ M4D SelectionPolicy / DiagnosticCandidateBatch
```

M4Q should verify end-to-end provenance, deterministic replay, stable identities,
policy-version sensitivity, successful/control sampling, visible exclusions and
shortfalls, and the M4 claim ceiling. It should not introduce Player Decision Evidence
or learner diagnosis merely to make the qualification richer.

M5 remains unauthorized until M4Q is qualified.

## Required stop before M4Q execution

M4D qualification is a deliberate stop/review boundary. Before starting M4Q, inspect
the complete M4 surface and verify:

- every selected position can explain why it was selected;
- every exclusion has reconstructable policy evidence;
- policy thresholds remain policy rather than universal chess truth;
- successful controls are first-class rather than error-only sampling;
- shortfalls cannot be hidden;
- input reordering cannot change a deterministic batch;
- no learner-psychology or pedagogical-value label has entered M4.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a frozen Diagnostic Position Selection contract;
- a qualified objective `DecisionComparison` layer;
- a qualified transparent objective `SelectionSignal` layer;
- a qualified immutable `DiagnosticCandidate` recording boundary;
- qualified versioned deterministic `SelectionPolicy` execution;
- qualified reproducible bounded `DiagnosticCandidateBatch` construction with
  controls, quotas, caps, exclusions, and visible shortfalls.

It may **not** yet claim that:

- M4 Diagnostic Position Selection as a whole is qualified;
- a selected position is the best teaching opportunity;
- a control contradicts a learner hypothesis;
- it knows why a player chose a move;
- it can diagnose a learner weakness or recurrence;
- it can recommend effective training;
- it has demonstrated transfer or mastery.
