# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M6B deterministic reasoning-evidence comparison qualification  
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

M6 — Reasoning Discrepancy                      IN PROGRESS
  M6A — Reasoning Discrepancy contract          FROZEN
  M6B — Deterministic comparison facts          QUALIFIED
  M6C — Coded local discrepancy assessment      NOT STARTED / NEXT
  M6Q — Full M6 qualification                   NOT STARTED

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

M5 is qualified under the frozen M5A contract and ADR 0004.

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

## M6 Reasoning Discrepancy boundary and current implementation

M6A remains frozen by:

- `docs/architecture/reasoning-discrepancy.md`;
- `docs/decisions/0005-reasoning-discrepancy-contract.md`.

M6 is the first production layer authorized to compare qualified objective evidence
with qualified participant-reported evidence. Its scope remains local to one selected
position / evidence context.

The governing boundary remains:

```text
qualified objective evidence
+ qualified Player Decision Evidence
→ position-local Reasoning Discrepancy assessment
```

while preserving:

```text
local discrepancy
!= unreported cognition
!= causal cognitive mechanism
!= recurrence
!= stable learner weakness
!= learner hypothesis
!= pedagogical prescription
```

### M6A frozen semantic split

M6A separates five semantic records:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
ReasoningCoding
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

The central production distinction remains:

```text
deterministic comparison fact
!= analyst/model semantic coding
```

The hard anti-overclaiming rules remain:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

and:

```text
missing dimension
→ not_observed
→ not a discrepancy by default
```

and:

```text
partial / bounded / incompatible objective evidence
→ not_comparable for the affected relation
```

Engine judgment remains distinguishable from deterministic chess truth. Divergence
from one engine PV is not automatically an error when multiple legal/comparable lines
may exist.

### M6B qualified deterministic comparison facts

M6B is qualified and implements the first two frozen semantic records needed for the
deterministic layer:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
```

The production implementation lives in:

```text
src/chess_mentor_engine/learning/
```

M6B binds the local context to the exact M4 `DiagnosticCandidate`, optional
`DiagnosticCandidateBatch`, `DecisionComparison`, retained selection signals, optional
M2 features/M3 analyses, and exact frozen M5 pre-reveal evidence. It preserves the
M5 measurement condition as `clean`, `instrument_aware_clean`, `deviating`, or
`contaminated` rather than normalizing the evidence history.

The qualified deterministic fact families are:

```text
REPORTED_SELECTED_MOVE_RELATION
EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION
EXPECTED_REPLY_RELATION
EXPECTED_CONTINUATION_RELATION
```

with descriptive relations:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

Key conservative semantics are now executable rather than merely contractual:

```text
engine rank-1 absent from explicit structured candidate list
→ not_explicitly_reported
→ NOT "never considered" or "failed candidate generation"

legal expected reply/continuation differs from one non-forced engine PV
→ not_comparable
→ NOT automatic conflict

illegal move/reply/continuation under deterministic chess rules
→ conflict under deterministic chess authority

missing structured dimension
→ not_observed

missing/mismatched comparable engine evidence
→ not_comparable or explicit rejection
```

M6B never parses `raw_response`. The raw response remains part of the cited M5 evidence
identity so M6C may later add separate coded interpretation without rewriting the
participant evidence or deterministic M6B fact.

See `docs/architecture/reasoning-discrepancy-facts.md` for exact implementation and
qualification provenance.

### Research boundary

Pilot 004's discrepancy taxonomy informed M6A, but its research codes remain historical
research authority rather than universal product learner categories. In particular,
its `strong candidate not generated` wording remains conservatively represented at the
production evidence boundary as `not_explicitly_reported` unless later coded evidence
supports a stronger local claim.

Pilot 004's recurrence policy remains outside M6. Cross-position recurrence, controls
and contradictions across positions, competing explanations, and learner hypotheses
belong to M7.

## Current authorized next task

> **M6C — coded local discrepancy assessment only.**

M6C may implement the remaining position-local interpretation surface frozen by M6A:

- immutable human/model `ReasoningCoding` with exact source/coder/rubric provenance;
- `ReasoningDiscrepancyAssertion` records that cite M6B facts and/or explicit coding;
- versioned local assessment policy;
- `ReasoningDiscrepancyAssessment` with `discrepancy_supported`,
  `no_supported_discrepancy`, `unclear`, and `unscorable` status;
- explicit measurement-condition handling.

M6C must **not**:

- overwrite or reinterpret M5 participant evidence as participant truth;
- mutate deterministic M6B facts;
- promote omitted report content into hidden cognition without explicit coded evidence;
- aggregate across positions;
- infer recurrence;
- create or confirm stable learner weaknesses;
- create the M7 Learner Hypothesis Ledger;
- prescribe training or claim pedagogical effectiveness.

M6Q remains not started. M7 remains unauthorized until M6Q is qualified.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a fully qualified Diagnostic Position Selection milestone;
- qualified objective `DecisionComparison`, `SelectionSignal`, `SelectionPolicy`, and
  `DiagnosticCandidateBatch` evidence;
- a fully qualified M5 Player Decision Evidence milestone;
- a frozen M6A production contract for position-local Reasoning Discrepancy;
- a qualified M6B deterministic context/fact layer for exact structured M4/M5
  comparison evidence.

M6B may report evidence facts such as:

- an explicitly structured selected move matches a cited engine rank-1 move;
- the canonical played move conflicts with the cited qualified M4 comparison;
- an engine rank-1 move was not explicitly present in the participant's structured
  candidate list;
- a structured participant move/reply/continuation is ambiguous or illegal;
- an expected reply/continuation matches the cited engine PV;
- a legal reply/continuation differs from one non-forced PV and is therefore not
  comparable under the initial M6B rule;
- a requested dimension was not observed;
- exact comparable objective evidence was unavailable;
- the cited M5 measurement condition was clean, instrument-aware, deviating, or
  contaminated.

The repository may **not** yet claim that:

- raw participant prose has been authoritatively interpreted under a qualified M6
  coding layer;
- an omitted move was never considered, recognized, or generated;
- a local coded Reasoning Discrepancy assertion/assessment is qualified;
- it knows the causal reason why a player chose a move;
- recurrence or a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5 is fully qualified. M6A is frozen. **M6B deterministic comparison facts is
qualified. M6C coded local discrepancy assessment is the only next authorized
implementation slice.** M6Q has not started. M7 remains unauthorized. Do not advance
from a local M6 assessment into recurrence, learner diagnosis, or pedagogy.
