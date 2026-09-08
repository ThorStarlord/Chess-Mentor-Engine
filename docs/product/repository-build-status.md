# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M4Q full Diagnostic Position Selection qualification  
**Relationship to roadmap:** this file complements
`chess-mentor-engine-repository-build-plan.md`. The roadmap preserves the conceptual
sequence and historical planning rationale; this file is the authority for which
milestones are actually qualified, frozen, implemented, authorized, or not started.

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

implemented technical boundaries / qualification records
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

M4 — Diagnostic Position Selection              QUALIFIED
  M4A — Selection contract                      FROZEN
  M4B — DecisionComparison                      QUALIFIED
  M4C — SelectionSignal + DiagnosticCandidate   QUALIFIED
  M4D — SelectionPolicy + CandidateBatch        QUALIFIED
  M4Q — Full M4 qualification                   QUALIFIED

M5 — Player Decision Evidence                   NOT STARTED / AUTHORIZED NEXT
M6 — Reasoning Discrepancy                      NOT STARTED / UNAUTHORIZED
M7 — Learner Hypothesis Ledger                  NOT STARTED
M8 — Evidence-aware Tutor Session               NOT STARTED
M9 — Training Interventions                     NOT STARTED
M10 — Transfer / Mastery Evidence               NOT STARTED
M11 — Longitudinal Learner State                NOT STARTED
M12+ — CLI/UI/richer LLM productization         NOT STARTED
```

## Qualified objective evidence chain

The repository now has this qualified objective evidence-acquisition path:

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

M4 as a whole is qualified under the frozen ADR 0003 claim ceiling. It can derive
transparent, provenance-rich objective decision comparisons and use versioned
deterministic policies to select bounded candidate sets containing both potentially
informative decisions and successful controls.

M4 qualification proves, among other things:

- canonical played-move provenance and compatible objective engine comparison;
- mover-relative exact centipawn comparison without hiding engine-evidence inversion;
- symbolic mate and terminal semantics without fake centipawn sentinels;
- conservative preservation of partial, bound, failure, and incompatible evidence;
- transparent objective selection signals with reconstructable evidence references;
- explicit versioned policy thresholds rather than universal chess labels;
- operational successful controls rather than error-only sampling;
- deterministic candidate/control batches with quotas, per-game caps, exclusions,
  source-pool provenance, and visible shortfalls;
- policy-version sensitivity without rewriting upstream objective evidence;
- absence of learner-psychology, LLM-ranking, and pedagogical-effectiveness claims.

M4Q freezes all 12 qualification categories required by M4A, including the prior
research board-context FEN, custom-FEN and promotion decisions, quiet/control cases,
close/separated MultiPV choices, and forced-mate cases. It also qualifies terminal,
partial, bound, failure, inversion, incompatible-analysis, deterministic replay,
policy-version, exclusion, and deliberate-shortfall behavior.

See:

- `docs/architecture/diagnostic-position-selection.md` — frozen M4A contract;
- `docs/architecture/decision-comparison.md` — M4B implementation record;
- `docs/architecture/selection-signals-and-candidates.md` — M4C record;
- `docs/architecture/selection-policy-and-batches.md` — M4D record;
- `docs/architecture/m4-qualification.md` — full M4Q qualification record.

## Current authorized next task

> **M5 — Player Decision Evidence contract/design gate only.**

M5 crosses the product from objective chess evidence into direct evidence about what
the player actually thought. The next work should therefore freeze the Player Decision
Evidence boundary before production implementation.

The M5 design gate should preserve at least these distinctions:

```text
objective chess truth
!= player self-report
!= analyst/model inference
!= learner diagnosis
```

It should also reconcile the production evidence schema with the already-preserved
research instrument boundaries without rewriting Pilot 001–004 evidence or exposure
state.

M5 is **authorized but not started**. M6 and later learner-inference/pedagogy
milestones remain unauthorized until their preceding evidence gates are qualified.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a frozen and fully qualified Diagnostic Position Selection milestone;
- qualified objective `DecisionComparison`;
- qualified transparent objective `SelectionSignal` derivation;
- qualified immutable `DiagnosticCandidate` provenance;
- qualified versioned deterministic `SelectionPolicy` execution;
- qualified reproducible bounded `DiagnosticCandidateBatch` construction with
  controls, quotas, caps, exclusions, and visible shortfalls.

It may **not** claim that:

- it knows why a player chose a move;
- a selected position demonstrates a stable learner weakness;
- a selected position is the best teaching opportunity;
- centipawn loss measures cognitive severity;
- a control contradicts a learner hypothesis;
- recurrence has been established;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M4 is closed and qualified. M5 is the next authorized milestone, but no M5
implementation has begun in this status state. Do not advance into M6 learner
inference or later pedagogy from M4 evidence alone.
