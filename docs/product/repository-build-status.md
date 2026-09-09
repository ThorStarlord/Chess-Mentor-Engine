# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M6C coded local Reasoning Discrepancy assessment qualification  
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
  M6C — Coded local discrepancy assessment      QUALIFIED
  M6Q — Full M6 qualification                   NOT STARTED / NEXT

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

Key conservative semantics are executable:

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
identity so M6C can add separate coded interpretation without rewriting the participant
evidence or deterministic M6B fact.

See `docs/architecture/reasoning-discrepancy-facts.md` for exact implementation and
qualification provenance.

### M6C qualified coded local assessment

M6C is qualified and implements the remaining position-local interpretation records
frozen by M6A:

```text
ReasoningCoding
ReasoningAssessmentPolicy
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

The authority split is explicit:

```text
M5 participant evidence
!= M6B deterministic fact
!= M6C human/model coding
!= M6C supported local assertion
```

`ReasoningCoding` is append-only derived evidence with exact player/objective/fact
references, coder kind (`human` or `model`), coder/run identity/version,
rubric/instruction fingerprint, optional confidence/uncertainty, timestamp, and
content-addressed identity. Different coders/runs may disagree; M6C preserves rather
than overwrites that disagreement.

`ReasoningAssessmentPolicy` is versioned and material. It binds eligible pre-reveal
stage kinds, allowed measurement conditions, required objective evidence, permitted
fact kinds/codes, coding requirements, supported parameters, and `position_local`
claim scope. Material policy changes therefore change assessment identity.

Initial deterministic assertion support is intentionally narrow:

```text
engine-rank1 candidate not explicitly reported
+ policy strong_candidate_basis=engine_rank1
→ STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED

EXPECTED_REPLY_RELATION + conflict
→ EXPECTED_OPPONENT_REPLY_CONFLICT

EXPECTED_CONTINUATION_RELATION + conflict
→ EXPECTED_CONTINUATION_CONFLICT
```

Intrinsically semantic codes such as feature relevance, resulting-evaluation conflict,
stated target without executable realization, incomplete rationale, and
`OTHER_LOCAL_DISCREPANCY` require explicit coding provenance. Correct-move/incomplete-
rationale additionally requires a matching deterministic selected-move fact, producing
a mixed assertion rather than allowing coding to manufacture move correctness.

M6C emits only:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

`no_supported_discrepancy` is dimension-bounded. `not_observed` alone cannot become a
negative result. Material same-code/same-stage coding disagreement is preserved as
uncertainty rather than last-write-wins. A1 and A2 remain distinct evidence stages, so
an A1/A2 change is not silently labeled a correction or intervention effect.

Deviating/contaminated evidence is scorable only under an exact policy that explicitly
allows its measurement condition, and the condition remains attached.

The final implementation also revalidates embedded coding/player/objective/fact/stage
provenance at assessment time. Recomputing a record's own hash after substituting
unrelated evidence does not make that record acceptable.

See `docs/architecture/reasoning-discrepancy-assessment.md` for exact implementation,
superseded-candidate, qualification, merge, and post-merge provenance.

### Research boundary

Pilot 004's discrepancy taxonomy informed M6A, but its research codes remain historical
research authority rather than universal product learner categories. In particular,
its `strong candidate not generated` wording remains conservatively represented at the
production evidence boundary as `not_explicitly_reported` unless explicit coded local
evidence supports a stronger permitted position-local claim.

Pilot 004's recurrence policy remains outside M6. Cross-position recurrence, controls
and contradictions across positions, competing explanations, and learner hypotheses
belong to M7.

## Current authorized next task

> **M6Q — full Reasoning Discrepancy qualification only.**

M6Q may build the bounded qualification corpus/harness needed to prove the complete
frozen M6A surface across the already implemented M6B + M6C layers, including:

- deterministic-versus-coded authority separation;
- deterministic, coded, and mixed assertion paths;
- all four assessment statuses;
- missing/ambiguous/incompatible evidence behavior;
- A1/A2 stage separation;
- clean/instrument-aware/deviating/contaminated measurement conditions;
- coder disagreement and contradiction preservation;
- exact provenance and deterministic replay/identity;
- full M1→M6 regression and external Stockfish witness;
- the M6 position-local claim ceiling.

M6Q must **not**:

- add cross-position recurrence semantics;
- aggregate local assertions into stable learner weaknesses;
- infer causal cognitive traits;
- create or confirm the M7 Learner Hypothesis Ledger;
- turn controls into hypothesis support/contradiction accounting;
- prescribe training;
- claim pedagogical effectiveness, learning, transfer, or mastery.

M7 remains unauthorized until M6Q itself is qualified, merged from the exact qualified
head, passes post-merge CI, and the status authorities are reconciled.

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
  comparison evidence;
- a qualified M6C coded position-local interpretation/assessment layer with explicit
  policy, provenance, uncertainty, contradiction, and measurement-condition handling.

M6B/M6C may report or preserve local evidence/assessment statements such as:

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
- a human/model coder supported, contradicted, or marked unclear one permitted local
  discrepancy code under exact source/rubric provenance;
- a permitted local assertion is supported under an exact versioned assessment policy;
- no supported discrepancy exists **within the assessed dimensions**;
- the local assessment is unclear or unscorable;
- the exact M5 measurement condition remains clean, instrument-aware, deviating, or
  contaminated.

The repository may **not** yet claim that:

- an omitted move was never considered, recognized, or generated;
- a coder/model judgment is objective chess truth;
- a local coded label establishes a stable learner trait;
- it knows the causal reason why a player chose a move;
- recurrence or a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5 is fully qualified. M6A is frozen. **M6B deterministic comparison facts and M6C
coded local discrepancy assessment are qualified. M6Q full M6 qualification is the
only next authorized slice.** M7 remains unauthorized. Do not advance from a local M6
assessment into recurrence, learner diagnosis, or pedagogy before M6Q closes the full
M6 qualification boundary.
