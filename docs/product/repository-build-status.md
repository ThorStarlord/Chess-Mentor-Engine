# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M6A Reasoning Discrepancy contract freeze  
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
  M6B — Deterministic comparison facts          NOT STARTED / NEXT
  M6C — Coded local discrepancy assessment      NOT STARTED
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

## Frozen M6 Reasoning Discrepancy boundary

M6A is now frozen by:

- `docs/architecture/reasoning-discrepancy.md`;
- `docs/decisions/0005-reasoning-discrepancy-contract.md`.

M6 is the first production layer authorized to compare qualified objective evidence
with qualified participant-reported evidence. Its scope remains local to one selected
position / evidence context.

The governing boundary is:

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

M6A separates five semantic records:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
ReasoningCoding
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

The most important production distinction is:

```text
deterministic comparison fact
!= analyst/model semantic coding
```

Deterministic M6 facts may compare explicit structured M5 values with exact qualified
objective evidence. They may emit only descriptive relations such as:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

They may not parse free text or infer hidden cognition.

Semantic interpretations from prose or judgments such as `critical feature`, `strong
candidate` outside an exact upstream rule, or `incomplete rationale` require immutable
human/model `ReasoningCoding` provenance.

### Hard anti-overclaiming rules

M6A freezes:

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
from one engine PV is not automatically an error when multiple lines may be valid or
comparable.

### Conservative initial discrepancy taxonomy

The frozen production codes are:

```text
OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED
STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED
EXPECTED_OPPONENT_REPLY_CONFLICT
EXPECTED_CONTINUATION_CONFLICT
REPORTED_RESULTING_EVALUATION_CONFLICT
STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE
CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE
OTHER_LOCAL_DISCREPANCY
```

Assessment statuses are separately:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

`no_supported_discrepancy` is dimension-bounded. It is not a claim that all reasoning
was observed or correct.

### Stage and measurement-condition rules

The initial primary M6 evidence surface is frozen pre-reveal M5:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
```

A1 and A2 remain separate. Post-reveal reflection and historical recollection may be
supplemental/contradictory evidence but cannot be silently promoted backward into
pre-reveal evidence.

M6 also preserves measurement condition:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

Instrument awareness alone is not contamination. Deviating/contaminated evidence may
be analyzed only under an explicit assessment policy that allows it, and the condition
must remain attached.

### Research boundary

Pilot 004's discrepancy taxonomy informed M6A, but its research codes remain historical
research authority rather than universal product learner categories. In particular,
its `strong candidate not generated` wording is conservatively adapted to `strong
objective candidate not explicitly reported` because production M5 does not read
unreported cognition.

Pilot 004's recurrence policy remains outside M6. Cross-position recurrence, controls
and contradictions across positions, competing explanations, and learner hypotheses
belong to M7.

## Current authorized next task

> **M6B — deterministic reasoning-evidence comparisons only.**

M6B may implement:

- `ReasoningDiscrepancyContext` binding;
- deterministic `DiscrepancyFact` derivation from explicit structured M5 evidence and
  qualified objective evidence;
- exact provenance/fingerprints;
- `match`, `conflict`, `not_explicitly_reported`, `ambiguous`, `not_observed`, and
  `not_comparable` relation semantics.

M6B must **not**:

- parse free text;
- invoke an LLM;
- emit stable cognitive labels;
- aggregate across positions;
- infer recurrence;
- create learner hypotheses;
- prescribe training;
- implement pedagogy.

M6C and M6Q remain not started. M7 remains unauthorized.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a fully qualified Diagnostic Position Selection milestone;
- qualified objective `DecisionComparison`, `SelectionSignal`, `SelectionPolicy`, and
  `DiagnosticCandidateBatch` evidence;
- a fully qualified M5 Player Decision Evidence milestone;
- a frozen M6A production contract for position-local Reasoning Discrepancy.

M5 may report evidence facts such as:

- what move/candidates/reply/plan/confidence the participant explicitly submitted;
- what raw response was frozen and when;
- whether objective evidence was revealed before or after required freezes;
- what information exposure or instrument-awareness provenance existed;
- whether a protocol deviation or later amendment occurred;
- whether a response belongs to a pre-reveal or post-reveal stage;
- whether an ambiguous or illegal reported move was preserved without repair.

The frozen M6A contract may define how future M6 records must behave, but **no
production M6 discrepancy implementation is qualified yet**.

The repository may **not** yet claim that:

- a production `ReasoningDiscrepancy` has been emitted under a qualified M6 runtime;
- it knows why a player chose a move;
- a participant report is objective chess truth;
- an omitted move was never considered;
- an omitted move was never generated internally;
- a reported explanation is the causal reason the move was chosen;
- recurrence or a stable learner weakness exists;
- a control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- an intervention is warranted or effective;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5 is fully qualified. M6A is frozen. **M6B deterministic comparison facts is the only
next authorized implementation slice.** M6C, M6Q, and M7 have not started. Do not
advance from a local comparison fact into recurrence, learner diagnosis, or pedagogy.
