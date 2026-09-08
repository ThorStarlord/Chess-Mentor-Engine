# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M5A Player Decision Evidence contract freeze  
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

M5 — Player Decision Evidence                   IN PROGRESS
  M5A — Player Decision Evidence contract       FROZEN
  M5B — Immutable evidence model                NOT STARTED / NEXT
  M5C — Capture/freeze state machine            NOT STARTED
  M5Q — Full M5 qualification                   NOT STARTED

M6 — Reasoning Discrepancy                      NOT STARTED / UNAUTHORIZED
M7 — Learner Hypothesis Ledger                  NOT STARTED
M8 — Evidence-aware Tutor Session               NOT STARTED
M9 — Training Interventions                     NOT STARTED
M10 — Transfer / Mastery Evidence               NOT STARTED
M11 — Longitudinal Learner State                NOT STARTED
M12+ — CLI/UI/richer LLM productization         NOT STARTED
```

## Qualified objective evidence chain

The repository has this qualified objective evidence-acquisition path through M4:

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

## Frozen M5A boundary

M5A freezes the first production boundary for direct Player Decision Evidence. It is
informed by the preserved Pilot 003/004 research instruments without rewriting those
artifacts or treating their prompts as universal product truth.

The frozen authority split is:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

The intended production evidence path is:

```text
DiagnosticCandidate
+ CanonicalPosition / PositionContextPacket
→ PlayerDecisionContext
→ PromptPresentation
→ PlayerResponseEvidence
→ EvidenceFreeze
→ optional later pre-reveal stage(s)
→ ObjectiveEvidenceReveal
```

The contract requires:

- verbatim preservation of raw participant language;
- explicit separation of participant-authored structured input from inferred coding;
- versioned prompt definitions and actual presentation provenance;
- separate minimal, probe, post-reveal, and recollection evidence states;
- first-class immutable freeze events;
- explicit objective-evidence reveal timing;
- exposure and instrument-awareness provenance;
- append-only corrections/amendments;
- preservation of ambiguous or illegal reported moves rather than silent correction;
- preservation of contaminated/deviating evidence with explicit provenance;
- no Reasoning Discrepancy, learner diagnosis, or pedagogy inside M5.

See `docs/architecture/player-decision-evidence.md` and ADR 0004.

M5A freezes the contract only. No M5 production entity or runtime state machine has
been implemented yet.

## Current authorized next task

> **M5B — immutable Player Decision Evidence model only.**

M5B should implement deterministic records/serialization/identity for:

```text
PlayerDecisionContext
PromptDefinition
PromptPresentation
PlayerResponseEvidence
ExposureEvent
EvidenceFreeze
ObjectiveEvidenceReveal
```

M5B must not implement the interactive capture/freeze state machine, Reasoning
Discrepancy, recurrence, learner hypotheses, tutoring, or pedagogy.

After M5B qualification, stop and review the evidence model before authorizing M5C.
M6 remains unauthorized until full M5Q qualification.

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
  controls, quotas, caps, exclusions, and visible shortfalls;
- a frozen M5A Player Decision Evidence production contract.

It may **not** claim that:

- M5 Player Decision Evidence is implemented or qualified;
- it knows why a player chose a move;
- a player report is objective chess truth;
- a selected position demonstrates a stable learner weakness;
- an omitted move was never considered;
- a reported explanation is the causal reason the move was chosen;
- a control contradicts a learner hypothesis;
- recurrence has been established;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5A is frozen. M5 production implementation has not started. M5B is the only next
authorized implementation slice. Do not advance into M5C or M6 from the design
contract alone.
