# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** full M5 Player Decision Evidence qualification  
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

M5 — Player Decision Evidence                   QUALIFIED
  M5A — Player Decision Evidence contract       FROZEN
  M5B — Immutable evidence model                QUALIFIED
  M5C — Capture/freeze state machine            QUALIFIED
  M5Q — Full M5 qualification                   QUALIFIED

M6 — Reasoning Discrepancy                      NOT STARTED / AUTHORIZED NEXT
M7 — Learner Hypothesis Ledger                  NOT STARTED / UNAUTHORIZED
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

M4 as a whole is qualified under the frozen ADR 0003 contract. It can derive
transparent, provenance-rich objective decision comparisons and use versioned
deterministic policies to select bounded candidate sets containing both potentially
informative decisions and successful controls.

See:

- `docs/architecture/diagnostic-position-selection.md`;
- `docs/architecture/decision-comparison.md`;
- `docs/architecture/selection-signals-and-candidates.md`;
- `docs/architecture/selection-policy-and-batches.md`;
- `docs/architecture/m4-qualification.md`.

## Qualified M5 Player Decision Evidence

M5 is now qualified under the frozen M5A contract and ADR 0004.

The authority split remains:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

The qualified production evidence path is:

```text
qualified M4 selected position / candidate / batch
→ PlayerDecisionContext
→ versioned PromptDefinition / PromptPresentation
→ PlayerResponseEvidence
→ EvidenceFreeze
→ optional later pre-reveal stage(s)
→ ExposureEvent / ProtocolDeviation as applicable
→ ObjectiveEvidenceReveal
→ optional post-reveal evidence
```

### M5B immutable model

M5B qualifies the immutable record/identity layer for:

```text
PlayerDecisionContext
PromptDefinition
PromptPresentation
PlayerResponseEvidence
ExposureEvent
EvidenceFreeze
ObjectiveEvidenceReveal
```

Raw participant language is preserved verbatim. Structured participant values contain
only explicitly submitted values, ambiguous and illegal reported moves remain
representable without silent repair, prompt wording/version/rendering is provenance,
and `EvidenceFreeze` is the sole freeze authority for an exact response fingerprint.

### M5C capture/freeze sequencing

M5C qualifies deterministic interaction sequencing through a versioned
`CaptureProtocol` and immutable append-only `EvidenceCaptureSession` snapshots.
Clean runs enforce required prior freezes and objective-reveal gates. Real-world
protocol deviations may instead be preserved with explicit `ProtocolDeviation`
provenance. Exposure/instrument-awareness state remains auditable, amendments cite
rather than rewrite frozen evidence, and pre-reveal evidence remains separate from
post-reveal reflection.

### M5Q full qualification

M5Q qualifies the whole M5A claim surface with a frozen corpus covering:

```text
clean minimal-only capture
clean minimal + standardized-probe capture
instrument-aware provenance
contaminated exposure
early later-stage presentation
early objective reveal
append-only amendment
ambiguous reported move
illegal reported move
post-reveal reflection
deterministic replay / identity
historical Pilot 003/004 artifact preservation
```

The qualification path starts from a real deterministic M1→M4 selected control and
binds M5 context to the selected candidate and batch before capture begins. The corpus
also reproduces the exact frozen Pilot 003 A1 prompt and six A2 questions while
preserving the research instruments as immutable historical authorities rather than
universal product prompt truth.

See:

- `docs/architecture/player-decision-evidence.md` — M5A contract;
- `docs/architecture/player-decision-evidence-model.md` — M5B record;
- `docs/architecture/player-decision-evidence-capture.md` — M5C record;
- `docs/architecture/m5-qualification.md` — full M5Q qualification;
- `docs/decisions/0004-player-decision-evidence-contract.md` — ADR 0004.

## Current authorized next task

> **M6 — Reasoning Discrepancy contract/design gate only.**

M5 now gives the repository qualified objective chess evidence plus qualified
participant-reported evidence under auditable information-state provenance. M6 is the
first milestone authorized to define a local traceable difference between those two
evidence domains.

The next task should therefore freeze the M6 contract before implementation. At
minimum it must define:

```text
qualified objective evidence refs
+ qualified player-evidence refs
→ local Reasoning Discrepancy candidate
```

while preserving:

```text
local discrepancy
!= recurrence
!= stable learner weakness
!= causal cognitive trait
!= learner hypothesis
!= pedagogical prescription
```

The M6 design must explicitly separate participant authority, analyst/model coding,
and deterministic comparison facts; retain uncertainty/uncodability; require traceable
evidence references; and prevent missing/ambiguous self-report from being silently
interpreted as evidence that a move was never considered.

**M6 implementation has not started.** M7 remains unauthorized.

## Current claim ceiling

The repository may now claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a fully qualified Diagnostic Position Selection milestone;
- qualified objective `DecisionComparison`, `SelectionSignal`, `SelectionPolicy`, and
  `DiagnosticCandidateBatch` evidence;
- a frozen M5A Player Decision Evidence production contract;
- a qualified M5B immutable Player Decision Evidence record/identity layer;
- a qualified M5C capture/freeze sequencing layer with reveal gates,
  exposure/deviation provenance, and append-only amendments;
- a fully qualified M5 Player Decision Evidence milestone across the frozen M5Q
  corpus.

M5 may report evidence facts such as:

- what move/candidates/reply/plan/confidence the participant explicitly submitted;
- what raw response was frozen and when;
- whether objective evidence was revealed before or after required freezes;
- what information exposure or instrument-awareness provenance existed;
- whether a protocol deviation or later amendment occurred;
- whether a response belongs to a pre-reveal or post-reveal stage;
- whether an ambiguous or illegal reported move was preserved without repair.

The repository may **not** yet claim that:

- it knows why a player chose a move;
- a participant report is objective chess truth;
- an omitted move was never considered;
- a reported explanation is the causal reason the move was chosen;
- a Reasoning Discrepancy has been established under a production M6 contract;
- recurrence or a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5A is frozen; M5B, M5C, and M5Q are qualified; **M5 as a whole is qualified**.
M6 Reasoning Discrepancy is authorized next, but its production contract and
implementation have not started. The next bounded task is the **M6 contract/design
gate**, not learner diagnosis or pedagogy.
