# M6 — Reasoning Discrepancy

## Status

**M6A — Reasoning Discrepancy contract is frozen. M6 implementation has not started.**

M1–M4 provide qualified objective chess evidence and M5 provides qualified
participant-reported decision evidence. M6 is the first production layer authorized to
compare those evidence domains. It remains position-local and evidence-bound.

The central boundary is:

```text
qualified objective evidence
+ qualified Player Decision Evidence
        ↓
position-local Reasoning Discrepancy assessment
```

and the claim ceiling is:

```text
local discrepancy
!= unreported cognition
!= causal cognitive mechanism
!= recurrence
!= stable learner weakness
!= learner hypothesis
!= pedagogical prescription
```

M7 remains unauthorized until M6 is fully qualified.

## Definition

A production **Reasoning Discrepancy** is a traceable, position-local assessment that
one or more aspects of a participant's frozen report conflict with, or do not
explicitly report, information that a versioned M6 assessment policy treats as relevant
given qualified objective evidence.

That definition is deliberately narrower than a cognitive diagnosis.

For example:

```text
engine candidate e2e4 absent from explicit candidate list
```

may support the fact:

```text
OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED
```

It does **not** by itself support:

```text
player never considered e2e4
player failed to generate e2e4
player has tunnel vision
player has a candidate-generation weakness
```

The last claims require evidence that M6 does not possess, and recurrence/stable
learner claims belong to M7 or later.

## Authority model

M6 preserves all upstream authority boundaries rather than collapsing them into a
single diagnosis object.

### Deterministic chess authority

Qualified M1/M2 evidence remains authoritative for facts such as:

- canonical position identity and FEN;
- move legality;
- deterministic board features in the qualified M2 feature surface;
- canonical game/position provenance.

### Engine-evidence authority

Qualified M3 evidence remains provenance-bound engine judgment, not deterministic
chess truth.

M6 must preserve distinctions such as:

```text
illegal move under chess rules
!= move outside engine top-N

forced tablebase fact
!= one engine principal variation
```

An M6 relation to engine evidence must cite the exact `PositionAnalysis` or downstream
M4 evidence it uses. It must not silently turn an engine PV into a unique forced line.

### Objective decision authority

Qualified M4 remains authoritative for:

- `DecisionComparison`;
- `SelectionSignal`;
- `DiagnosticCandidate`;
- `SelectionPolicy` / selection decision;
- `DiagnosticCandidateBatch`;
- their exact provenance and compatibility semantics.

M6 may cite these records. It must not rewrite their objective meaning into learner
psychology.

### Participant authority

Qualified M5 remains authoritative for what the participant explicitly submitted and
for the information state under which it was submitted.

Participant authority includes exact frozen evidence such as:

- raw response text;
- explicitly selected move;
- explicitly submitted candidate moves;
- explicitly submitted expected reply/continuation;
- stated objective or plan;
- stated uncertainty;
- explicitly submitted confidence;
- prompt/stage identity;
- freeze timing;
- exposure/instrument-awareness/deviation provenance.

A participant report remains evidence about the report, not objective chess truth.

### Deterministic M6 comparison authority

Deterministic M6 code may compare **explicit structured participant values** with exact
qualified objective evidence and emit typed relation facts.

It may not infer semantic content from free text.

### Analyst/model coding authority

Semantic interpretation that is not mechanically entailed by the explicit structured
values and qualified objective records is separate coding.

Examples include:

- extracting an implied candidate from prose;
- deciding that a sentence expresses a particular plan;
- judging that a board feature is strategically `critical`;
- judging that a rationale is incomplete;
- interpreting an explanation as position evaluation;
- deciding that two differently worded ideas mean the same thing.

Such coding is derived evidence. It must cite its source records, preserve coder/model
provenance, and never overwrite M5 participant evidence or deterministic M6 facts.

## Initial semantic records

Exact Python naming may evolve during implementation, but M6A freezes the following
semantic records.

### `ReasoningDiscrepancyContext`

Binds one local assessment attempt to exact upstream objective and participant evidence.

Conceptually:

```yaml
reasoning_context_id:
participant_id:
player_decision_context_ref:
position_id:
game_id:
diagnostic_candidate_ref:
diagnostic_batch_ref: optional
capture_session_ref:
assessment_stage_refs:
player_response_refs:
evidence_freeze_refs:
prompt_presentation_refs:
exposure_refs:
protocol_deviation_refs:
position_feature_packet_ref: optional
position_analysis_refs:
decision_comparison_ref:
selection_signal_refs:
measurement_condition:
created_at:
```

Every primary participant response used for an initial pre-reveal M6 assessment must
be frozen M5 evidence.

### `DiscrepancyFact`

A deterministic relation between explicit participant evidence and qualified objective
evidence.

Conceptually:

```yaml
fact_id:
reasoning_context_id:
stage_id:
kind:
participant_evidence_refs:
objective_evidence_refs:
relation:
participant_value:
objective_value:
comparison_provenance:
fingerprint:
```

Initial relation values are:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

These relation values are intentionally descriptive rather than psychological.

Initial fact families may include:

```text
REPORTED_SELECTED_MOVE_RELATION
EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION
EXPECTED_REPLY_RELATION
EXPECTED_CONTINUATION_RELATION
REPORTED_POSITION_EVALUATION_RELATION     # only when explicit/codable input exists
```

A fact family is available only when the required participant field and compatible
objective evidence exist. Missing evidence produces `not_observed` or
`not_comparable`; it must not be converted into a discrepancy by default.

### `ReasoningCoding`

Append-only semantic coding supplied by a human analyst or model.

Conceptually:

```yaml
coding_id:
reasoning_context_id:
coding_kind:
code:
statement:
source_player_evidence_refs:
source_objective_evidence_refs:
source_fact_refs:
coder_kind: human | model
coder_id:
coder_version:
rubric_or_instruction_fingerprint:
confidence: optional
uncertainty_note: optional
created_at:
fingerprint:
```

Different coders or model runs may disagree. M6 preserves those coding records rather
than applying last-write-wins mutation.

The initial implementation need not invoke an LLM. Precomputed or human-supplied
coding may be used to qualify the record boundary before any live model integration.

### `ReasoningDiscrepancyAssertion`

One position-local discrepancy assertion supported by exact facts and/or coding.

Conceptually:

```yaml
assertion_id:
reasoning_context_id:
code:
statement:
stage_refs:
supporting_fact_refs:
supporting_coding_refs:
contradictory_evidence_refs:
basis_kind: deterministic | coded | mixed
claim_scope: position_local
fingerprint:
```

No assertion may omit its supporting evidence references.

### `ReasoningDiscrepancyAssessment`

The immutable assessment bundle for one M6 context under one versioned policy.

Conceptually:

```yaml
assessment_id:
reasoning_context_id:
assessment_policy_ref:
status:
assertion_refs:
fact_refs:
coding_refs:
contradictory_evidence_refs:
measurement_condition:
created_at:
fingerprint:
```

Initial status values are:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

`no_supported_discrepancy` means only:

> No local discrepancy was supported within the dimensions actually observed and
> assessable under this policy.

It does **not** mean complete reasoning, correct cognition, mastery, or absence of a
learner weakness.

## Versioned assessment policy

M6 assessments must cite a material, versioned policy rather than embedding hidden
thresholds or changing interpretation rules invisibly.

Conceptually:

```yaml
assessment_policy_id:
version:
eligible_stage_kinds:
allowed_measurement_conditions:
required_objective_evidence:
permitted_fact_kinds:
permitted_discrepancy_codes:
coding_requirements:
thresholds_or_parameters:
claim_scope: position_local
fingerprint:
```

Changing a material threshold, eligible stage, contamination rule, taxonomy, coding
requirement, or objective-evidence requirement creates a different policy fingerprint.

M6A freezes no universal centipawn threshold and no global `reasoning severity` scalar.
Objective magnitudes already available from M3/M4 may be cited as evidence, but they
must not silently become universal cognitive-severity labels.

## Evidence-stage boundary

The initial production M6 target is frozen **pre-reveal** M5 evidence:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
```

A1 and A2 remain separate evidence states.

M6 must not merge them into one reconstructed narrative. A discrepancy assertion must
cite the exact stage(s) that support it.

If an assessment intentionally compares stages, it must preserve the distinction:

```text
A1 report
!= A2 report
```

A probe-induced change is evidence about a stage change. It is not automatically a
cognitive correction or a successful intervention.

`POST_REVEAL_REFLECTION` and `ORIGINAL_GAME_RECOLLECTION` may be preserved as
supplemental or contradictory evidence, but the initial M6 contract does not permit
them to be silently promoted into pre-reveal reasoning evidence.

## Measurement condition

M6 must derive and preserve the M5 measurement condition relevant to the assessment.
At minimum the contract distinguishes:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

Instrument awareness alone does not imply contamination.

A contaminated or deviating sequence may still be analyzed when an explicit versioned
assessment policy allows it, but the condition must remain attached to the result.
M6 must never manufacture a clean history by discarding the exposure/deviation
provenance.

## Absence semantics

This is a hard M6 rule:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

Even when a standardized prompt asks for other moves seriously considered, absence
from the submitted answer supports at most a stage- and prompt-specific statement such
as:

> The move was not explicitly included in the participant's response to this candidate
> elicitation prompt.

It does not prove the move never occurred internally.

Therefore the Pilot 004 research code `strong candidate not generated` is **not**
adopted verbatim as an initial production M6 claim. The conservative production form
is `strong objective candidate not explicitly reported`, with the exact basis for
`strong` itself cited or coded.

## Objective relevance is not automatically deterministic

M2 can deterministically say that a feature exists. M3 can provide engine judgments.
M4 can say why a decision was selected under a versioned policy.

Those records do not automatically prove that a particular feature is the uniquely
`critical` feature a human had to notice.

Accordingly:

```text
feature exists
!= feature is critical

engine rank 1
!= only reasonable move
```

Terms such as `critical`, `strong`, `strategically necessary`, or `rationale incomplete`
require either a precise upstream deterministic contract or explicit `ReasoningCoding`
provenance.

## Initial conservative discrepancy taxonomy

The Pilot 004 research taxonomy is informative but remains a research artifact. M6A
adapts it into conservative production codes that describe evidence relations rather
than hidden cognition.

Initial codes are:

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

The following are assessment statuses, not discrepancy codes:

```text
no_supported_discrepancy
unclear
unscorable
```

### Code-specific cautions

`OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED`

- requires exact objective feature evidence;
- if `relevant` or `critical` is not deterministically defined upstream, that relevance
  requires coding provenance;
- does not mean the participant failed to perceive the feature.

`STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED`

- requires an exact engine/M4 basis for the candidate and any threshold or ranking rule;
- absence means absence from the explicit report only;
- it does not mean candidate-generation failure.

`EXPECTED_OPPONENT_REPLY_CONFLICT`

- compares an explicitly reported expected reply with a cited objective/engine
  reference;
- if multiple replies are objectively/engine-comparable, the policy must not declare a
  conflict merely because the participant chose a different valid alternative;
- one engine PV must not be treated as unique forced truth without supporting evidence.

`EXPECTED_CONTINUATION_CONFLICT`

- requires a sufficiently comparable objective reference;
- illegal or impossible participant continuations may be identified deterministically;
- divergence from one non-forced PV is not automatically an error.

`REPORTED_RESULTING_EVALUATION_CONFLICT`

- applies only when the participant explicitly submitted an evaluative judgment or a
  separately provenance-bound coding extracts one;
- engine evaluation remains engine judgment unless a stronger deterministic authority
  exists.

`STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE`

- requires a participant-stated target/plan plus evidence that no executable
  realization was explicitly reported;
- it does not mean the participant was incapable of generating one.

`CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE`

- demonstrates why move correctness and reasoning completeness are separate;
- `incomplete` is coding unless a structured rubric makes it deterministic;
- it must never be promoted to a stable weakness from one position.

## Correct move and incorrect move are not reasoning verdicts

M6 freezes both directions:

```text
correct / rank-1 move
!= complete reasoning

inferior move
!= necessarily incorrect self-understanding
```

A successful M4 control can still expose a local reasoning discrepancy. Conversely, a
player may explicitly understand an objective downside yet intentionally choose an
inferior move; the objective move loss alone does not establish a reasoning mismatch.

M6 therefore evaluates the report against evidence, not merely the final move against
engine rank.

## Missing and ambiguous evidence

M6 must prefer explicit uncertainty to manufactured conclusions.

Examples:

```text
minimal-only prompt did not ask for opponent reply
→ expected-reply dimension = not_observed
→ not a discrepancy

reported move ambiguous
→ preserve ambiguity
→ do not guess a move to create a discrepancy

objective analysis partial / bounded / incompatible
→ affected comparison = not_comparable
→ assessment may become unclear or unscorable
```

M6 must not reward itself for filling gaps in either participant or objective evidence.

## Coding disagreement

Human/model coding is append-only evidence, not mutable truth.

If two coders materially disagree:

```text
coding A
!= coding B
```

Both records remain available. A versioned adjudication policy may later decide how to
use disagreement, but without such a policy M6 must not silently choose the more
convenient coding.

Material unresolved coding disagreement may force the affected assertion or assessment
to `unclear`.

## Identity and reproducibility

M6 identity must bind all material inputs.

At minimum:

```text
canonical position / M4 selected-decision identity
M5 player-decision context
exact response/freeze/prompt/exposure/deviation refs
exact objective evidence refs
exact deterministic fact refs
exact coding refs
assessment-policy fingerprint
result status / assertions
```

If model/human coding is used, coding nondeterminism is isolated in the immutable
coding record. Given identical frozen input records, coding records, and assessment
policy, the final assessment serialization/fingerprint should be deterministic.

## Research compatibility

Pilot 003 already freezes the principle that raw participant language, analyst coding,
and objective chess evidence must remain separate. It also treats `UNCLEAR` and
uncodable responses as valid outcomes.

Pilot 004 defines a research Reasoning Discrepancy as a traceable mismatch between
P01's reported pre-engine reasoning and an objectively relevant demand or consequence
of the position. Its candidate research codes include feature, candidate, opponent
reply, continuation, resulting evaluation, plan-to-move, incomplete rationale,
no-discrepancy, unclear, and emergent cases.

M6A preserves that research intent while tightening production wording around
unobserved cognition. It does **not** mutate Pilot 003/004 files and does not promote
research codes into universal learner categories.

Pilot 004's recurrence policy remains outside M6. It requires multiple independent
positions, common structure, comparable evidence, controls/contradictions, and competing
explanations. Those are M7 concerns.

## What M6 may eventually claim

After full qualification, M6 may make position-local statements such as:

- the participant explicitly expected reply X, while the cited qualified objective
  evidence favored or established Y under the stated authority;
- engine candidate X was not explicitly included in the participant's candidate report
  at stage A2;
- the participant's explicitly reported continuation conflicts with a cited forced or
  sufficiently comparable objective continuation;
- a feature judged relevant under an explicit rule/coding was not explicitly present in
  the frozen report;
- no supported local discrepancy was found in the dimensions actually observed;
- the evidence is unclear or unscorable under the current policy.

## Claims prohibited in M6

M6 must not claim from a position-local assessment that:

- an unreported idea was never considered;
- the player failed to generate an unreported move;
- a reported explanation is the causal mechanism of the move choice;
- the player has tunnel vision, poor calculation, weak planning, or a stable trait;
- a local discrepancy recurs;
- a control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- an intervention should be prescribed;
- an intervention is effective;
- learning, transfer, or mastery occurred.

Those require M7+ and/or separate validation.

## Implementation sequence

### M6A — contract freeze

This document plus ADR 0005 freeze the Reasoning Discrepancy boundary.

Status after M6A:

> **M6A CONTRACT FROZEN — M6B IMPLEMENTATION NOT STARTED**

### M6B — deterministic reasoning-evidence comparisons

Implement only:

- `ReasoningDiscrepancyContext` binding;
- deterministic `DiscrepancyFact` derivation from explicit structured M5 evidence and
  qualified objective evidence;
- `match` / `conflict` / `not_explicitly_reported` / `ambiguous` / `not_observed` /
  `not_comparable` semantics;
- exact provenance and deterministic fingerprints.

Do not parse free text, run an LLM, or emit learner/cognitive claims.

### M6C — coded local discrepancy assessment

Implement immutable `ReasoningCoding`, `ReasoningDiscrepancyAssertion`, versioned
assessment policy, and `ReasoningDiscrepancyAssessment` records.

Initial qualification may use precomputed or human-supplied coding. Live model
integration is not required to qualify the evidence boundary.

### M6Q — full M6 qualification

Qualify the complete M6 claim surface, including at least:

```text
accurate reasoning / no supported discrepancy
successful move with incomplete reported rationale
objective candidate absent from explicit candidate report
expected opponent reply conflict
expected continuation conflict
minimal-only missing dimension → not_observed
ambiguous report → no guessed discrepancy
illegal/impossible continuation when deterministically provable
instrument-aware clean evidence
contaminated/deviating evidence with condition preserved
post-reveal evidence not promoted backward
partial/bounded/incompatible objective evidence → not_comparable
multiple coding records / disagreement
absence-from-report anti-overclaiming
successful M4 control with possible local discrepancy
deterministic replay / fingerprint identity
historical research-artifact preservation
```

M7 remains unauthorized until M6Q passes, exact-head CI passes, the qualified candidate
is merged without tree drift, post-merge CI passes, and repository status authority is
explicitly reconciled.

## Qualification gates

M6 may be declared qualified only when all applicable gates pass:

```text
qualified M4/M5 provenance preserved
frozen participant response required for primary pre-reveal assessment
deterministic facts use explicit structured participant values only
raw free text is never silently parsed into participant truth
engine judgment remains distinguishable from deterministic chess truth
absence-from-report never becomes absence-from-cognition
missing dimensions become not_observed, not discrepancies
ambiguous evidence remains ambiguous
incompatible objective evidence remains not_comparable
A1/A2 remain stage-distinct
post-reveal/recollection evidence is not promoted backward
measurement condition / contamination provenance preserved
coding is append-only and cites source evidence
coding disagreement is not overwritten
no-supported-discrepancy claim is dimension-bounded
no recurrence or stable learner weakness
no causal cognitive trait
no pedagogical prescription or efficacy claim
historical research artifacts remain unchanged
pytest passes
Ruff passes
exact candidate-head CI passes
post-merge CI passes
```

## Explicitly deferred

M6A does not implement or freeze:

- recurrence thresholds or recurrence state;
- cross-position aggregation;
- learner-hypothesis lifecycle;
- stable weakness labels;
- causal cognitive diagnosis;
- contradiction/support accounting across positions;
- training eligibility;
- intervention selection;
- tutoring dialogue;
- pedagogical effectiveness;
- transfer/mastery;
- a universal discrepancy severity score;
- production LLM invocation;
- persistence/database/UI architecture.

These remain later milestones.

## Related records

- `docs/architecture/m5-qualification.md`
- `docs/architecture/player-decision-evidence.md`
- `docs/architecture/diagnostic-position-selection.md`
- `docs/decisions/0004-player-decision-evidence-contract.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/evidence-schema.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/discrepancy-taxonomy.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/recurrence-policy.md`
- `docs/product/repository-build-status.md`
