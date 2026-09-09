# Learner Hypothesis Ledger

## Status

**M7A contract freeze.**

This document freezes the initial production boundary for M7 — Learner Hypothesis
Ledger. It authorizes no production implementation by itself.

M7 is the first milestone allowed to reason across multiple qualified position-local M6
assessments. Its job is not to turn local discrepancies into permanent weakness labels.
Its job is to maintain participant-specific, evidence-backed, revisable hypotheses whose
support, contradiction, context, uncertainty, alternatives, and history remain
inspectable.

The governing escalation is:

```text
qualified position-local M6 evidence
        ↓
explicit hypothesis/evidence mapping
        ↓
versioned cross-position assessment policy
        ↓
participant-specific recurrence assessment
        ↓
append-only hypothesis history
```

with the hard boundary:

```text
local discrepancy
!= recurring pattern
!= causal cognitive mechanism
!= permanent learner trait
!= pedagogical prescription
```

## Why M7 exists

M1-M6 can now establish objective chess evidence, freeze participant-reported evidence,
and produce bounded position-local Reasoning Discrepancy assessments. M6 deliberately
stops before recurrence.

The next product risk is therefore aggregation error. Without an explicit M7 boundary,
a system could make invalid jumps such as:

```text
one candidate omission
→ recurring candidate-generation weakness

several engine mistakes
→ same cognitive cause

successful M4 control
→ contradiction of a learner weakness

no_supported_discrepancy
→ proof that a weakness disappeared

repeated local pattern
→ causal psychological trait
```

M7 exists to prevent those collapses while still allowing useful longitudinal learner
hypotheses to emerge from traceable evidence.

## Source authorities

M7A is informed by, but does not rewrite:

- `docs/architecture/reasoning-discrepancy.md`;
- `docs/architecture/m6-qualification.md`;
- `docs/decisions/0005-reasoning-discrepancy-contract.md`;
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/recurrence-policy.md`;
- `docs/product/chess-mentor-engine-repository-build-plan.md`;
- `docs/product/repository-build-status.md`.

Pilot 004 remains a frozen research authority. Its recurrence policy requires more than
one independent position, traceable common structure, comparable reasoning evidence,
review of controls and contradictory cases, and consideration of alternatives. It also
requires later batches to test candidate hypotheses rather than merely elaborate them,
and explicitly allows hypotheses to disappear.

The older repository build plan likewise proposes an evidence-backed, revisable
hypothesis/contradiction ledger with support, contradiction, context, competing
explanations, evidence strength, and revision history.

M7A adapts those ideas conservatively into a production evidence contract. Research
terminology is not automatically promoted into universal learner categories.

## Governing principle

> **A learner hypothesis is a revisable participant-specific inference over qualified
> cross-position evidence, not a fact about hidden cognition.**

The production distinction is:

```text
M6 local assertion
!= M7 hypothesis-evidence link
!= M7 recurrence assessment
!= causal explanation
!= pedagogy
```

M7 may say that a bounded descriptive pattern is supported under an exact policy and
exact evidence set. It may not claim that the system has directly observed the
participant's internal cognitive mechanism.

## Initial production boundary

M7 consumes qualified M6 records and produces only participant-specific hypothesis
ledger records.

Conceptually:

```text
ReasoningDiscrepancyAssessment[]
+ ReasoningDiscrepancyAssertion[]
+ exact upstream M4/M5/M6 provenance
        ↓
LearnerHypothesis
        ↓
HypothesisRevision[]
+ HypothesisLifecycleEvent[]
        ↓
HypothesisEvidenceLink[]
        ↓
HypothesisAssessmentPolicy
        ↓
HypothesisAssessment[]
        ↓
HypothesisLedgerSnapshot
```

M7 does **not** own:

- new chess truth;
- new engine analysis;
- participant-response capture;
- position-local discrepancy derivation;
- causal cognitive diagnosis;
- intervention selection;
- tutoring dialogue;
- transfer/mastery claims;
- persistent database architecture;
- UI;
- live model invocation.

## Authority split

M7 must preserve the authorities already qualified upstream:

```text
deterministic chess fact
!= provenance-bound engine judgment
!= M4 selection/control role
!= M5 participant self-report
!= M6 deterministic discrepancy fact
!= M6 human/model coding
!= M6 position-local assertion
!= M7 hypothesis evidence mapping
!= M7 recurrence assessment
```

A downstream hypothesis record must cite exact upstream identities rather than flatten
all evidence into one text summary.

## Descriptive hypothesis claim ceiling

The initial M7 hypothesis surface is **descriptive and evidence-mappable**.

A hypothesis should be expressible in a form such as:

> For participant P01, in explicitly defined context C, qualified pre-reveal evidence
> tends to show local discrepancy pattern D.

A production M7 hypothesis must be:

- participant-specific;
- falsifiable by future evidence;
- linked to one or more explicit M6 discrepancy/assertion dimensions;
- bounded by explicit context or an explicitly broad context;
- compatible with the measurement conditions permitted by its assessment policy;
- revisable and retireable;
- non-causal under the initial M7 contract.

Examples that exceed the initial M7 claim ceiling include:

```text
P01 has tunnel vision.
P01 has weak working memory.
P01 ignores tactics because of overconfidence.
P01 is a poor calculator.
```

Those phrases collapse descriptive recurrence into hidden psychological mechanism or
stable trait.

A safer production statement is closer to:

```text
Across the evidence units admitted by policy HAP-1, P01 repeatedly did not explicitly
report the opponent's strongest forcing reply in context C.
```

Even that statement remains policy- and evidence-bound.

## Core records

M7A freezes the following semantic records.

### 1. `LearnerHypothesis`

Stable identity for one participant-specific hypothesis lineage.

Conceptually:

```yaml
hypothesis_id:
participant_id:
origin_proposal_fingerprint:
created_at:
origin_provenance:
fingerprint:
```

The stable identity does not mutate when the hypothesis wording or scope is revised.
The initial proposal fingerprint and origin provenance create the lineage without
requiring a circular reference to a revision that itself cites `hypothesis_id`.
Material wording/scope changes are represented through append-only revisions.

### 2. `HypothesisRevision`

Append-only version of the hypothesis proposition and scope.

Conceptually:

```yaml
revision_id:
hypothesis_id:
revision_number:
statement:
claim_kind: descriptive_pattern
scope_definition:
context_definition_refs:
competing_hypothesis_refs:
unresolved_alternative_notes:
parent_revision_ref:
revision_reason:
author_provenance:
created_at:
fingerprint:
```

Initial `claim_kind` is frozen to `descriptive_pattern`.

A revision may narrow, broaden, clarify, or otherwise revise the proposition, but it
must preserve lineage and the prior revision. It must never rewrite historical evidence
links or assessments.

Revision 1 has no parent revision. Later revisions cite the exact prior revision they
supersede within the same lineage.

If a new proposition is materially different rather than a genuine revision of the same
lineage, it should receive a new `hypothesis_id`.

### 3. `HypothesisLifecycleEvent`

Append-only authority event for hypothesis lineage state.

Conceptually:

```yaml
lifecycle_event_id:
hypothesis_id:
kind: retired | superseded
superseding_hypothesis_ref:
reason:
author_provenance:
created_at:
fingerprint:
```

A newly created hypothesis is `active` by default. A `retired` event changes current
authority state to retired. A `superseded` event changes current authority state to
superseded and cites the replacing hypothesis lineage.

M7A does not freeze an automatic reactivation rule. If future evidence requires such a
transition, it needs an explicit versioned extension rather than mutating old events.

Lifecycle events are authority history, not evidence-strength judgments. A hypothesis
may be contradicted or unclear while still active until an explicit lifecycle event is
recorded.

### 4. `HypothesisEvidenceLink`

Explicit relation between one hypothesis revision and one qualified M6 evidence unit.

Conceptually:

```yaml
link_id:
hypothesis_revision_ref:
participant_id:
reasoning_context_ref:
assessment_ref:
assertion_refs:
source_position_id:
source_game_id:
relation:
context_refs:
measurement_condition:
basis_kind:
mapping_policy_or_coding_ref:
created_at:
fingerprint:
```

Initial `relation` values are:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
```

`basis_kind` distinguishes at minimum:

```text
deterministic_mapping
coded_mapping
```

A mapping is itself derived evidence. M7 must not pretend that every M6 assertion
supports or contradicts every hypothesis automatically.

If semantic interpretation is required to map an M6 record into a hypothesis relation,
that interpretation must retain human/model/rubric/run provenance rather than being
hidden inside the ledger.

### 5. `HypothesisAssessmentPolicy`

Versioned material policy for cross-position recurrence assessment.

Conceptually:

```yaml
assessment_policy_id:
version:
eligible_m6_statuses:
eligible_discrepancy_codes:
allowed_measurement_conditions:
m6_policy_compatibility_rule:
stage_compatibility_rule:
context_match_rule:
recurrence_unit_rule:
independence_rule:
minimum_independent_supports_for_candidate:
minimum_independent_supports_for_supported:
required_contradiction_review:
required_counterexample_review:
required_competing_explanation_review:
contradiction_rule:
claim_scope: participant_specific_cross_position
fingerprint:
```

Every material threshold or interpretation rule belongs to the policy. M7A freezes no
universal number of games beyond the hard principle that recurrence requires more than
one distinct qualifying position.

`minimum_independent_supports_for_candidate` therefore cannot be less than two.

The policy may impose stricter requirements for `supported_recurrence`.

### 6. `HypothesisAssessment`

Immutable assessment of one exact hypothesis revision under one exact policy and exact
frozen evidence-link set.

Conceptually:

```yaml
hypothesis_assessment_id:
hypothesis_revision_ref:
assessment_policy_ref:
status:
support_link_refs:
contradiction_link_refs:
successful_counterexample_link_refs:
context_exception_link_refs:
unclear_link_refs:
recurrence_unit_ids:
independence_unit_ids:
source_position_ids:
source_game_ids:
measurement_conditions:
competing_explanation_review:
evidence_summary:
created_at:
fingerprint:
```

Initial status vocabulary is:

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

These are **assessment states**, not permanent learner labels.

### 7. `HypothesisLedgerSnapshot`

Immutable derived view of the current hypothesis ledger state.

Conceptually:

```yaml
snapshot_id:
participant_id:
entries:
  - hypothesis_ref:
    current_revision_ref:
    latest_assessment_ref:
    authority_lifecycle_state: active | retired | superseded
    latest_lifecycle_event_ref:
created_at:
fingerprint:
```

The snapshot does not replace the underlying append-only records. It is rebuildable
from hypothesis identities, revisions, evidence links, assessments, and lifecycle
events.

## Evidence relation semantics

### `supports`

The cited M6 evidence is relevant to the exact hypothesis revision and is consistent
with the proposition under the mapping rule/coding.

Support from one position is still local evidence. It is not recurrence by itself.

### `contradicts`

The cited M6 evidence is relevant to the same hypothesis scope and conflicts with the
proposition under the explicit mapping rule/coding.

A contradiction is not deleted because later support appears.

### `successful_counterexample`

The participant produced objectively successful behavior **and** the exact
hypothesis-relevant dimension was observed and assessable in a context where the
hypothesis would have predicted the discrepancy.

This relation is deliberately stricter than M4's operational `control` role.

### `context_exception`

The evidence is relevant enough to refine hypothesis scope but indicates that the
pattern may not apply in a specific context.

An exception may motivate a narrower future hypothesis revision. It is not silently
converted into support or contradiction.

### `unclear`

The evidence may be relevant, but material ambiguity, coding disagreement, incompatible
measurement conditions, or insufficient comparability prevents a stronger relation.

`unclear` evidence is preserved and must not be counted as support simply to satisfy a
threshold.

## M4 controls are not M7 contradictions

This remains a hard cross-milestone rule:

```text
M4 operational control
!= M7 successful counterexample
!= M7 contradiction
```

M4's control role only says that a position was sampled as an objectively
successful/low-severity decision under the selection policy.

To become M7 hypothesis evidence, the position must pass through qualified M5/M6 and be
mapped to the exact hypothesis-relevant dimension.

A successful move can still contain a local reasoning discrepancy, as M6Q already
proved.

Therefore no M7 policy may infer contradiction from `control_candidate_id` alone.

## `no_supported_discrepancy` is not automatically negative hypothesis evidence

M6's `no_supported_discrepancy` means only that no permitted local discrepancy was
supported within dimensions actually observed and assessable under that M6 policy.

Therefore:

```text
M6 no_supported_discrepancy
!= M7 contradiction
!= M7 successful counterexample
```

A `no_supported_discrepancy` assessment can become counterevidence only when M7 can show
that:

1. the hypothesis-relevant dimension was actually observed;
2. the evidence was assessable and comparable;
3. the position satisfies the hypothesis context;
4. the M7 mapping policy explicitly defines the negative relation;
5. measurement/stage compatibility rules permit comparison.

If the relevant dimension was `not_observed`, `not_comparable`, `unclear`, or
`unscorable`, M7 must not manufacture a counterexample.

## Recurrence unit and double-count prevention

The initial recurrence unit is one canonical participant-position evidence unit.

At minimum:

```text
same participant + same canonical position_id
→ one recurrence unit
```

Multiple local discrepancy assertions, multiple coders, repeated assessments, or A1/A2
records for the same canonical position do not become multiple recurrence instances.
They may enrich or complicate that one evidence unit, but they cannot inflate recurrence
counts.

Every `HypothesisAssessmentPolicy` must additionally state an independence rule.

M7A does not claim statistical independence merely because two positions have different
IDs. The initial qualification policy is expected to use a conservative rule such as
`distinct_game_id` for independent support counting, but that rule remains explicit,
versioned policy rather than universal chess truth.

## Common structure and context

Pilot 004 requires traceable common structure. M7 must not implement recurrence by
opaque resemblance.

This is prohibited:

```text
"these positions feel similar"
→ same weakness
```

Common structure must be supported by one of:

- exact upstream deterministic M2/M4/M6 attributes;
- an explicit versioned context rule over those attributes;
- separate provenance-bound human/model context coding.

M7A does not authorize embedding similarity, latent clustering, or unconstrained LLM
semantic grouping as evidence of common structure.

A `context_definition_ref` is material to the hypothesis revision and assessment. If the
meaning of the context changes materially, the hypothesis must be revised or assessed
under a new context/policy identity.

## Comparable reasoning evidence

Cross-position aggregation must preserve M5/M6 measurement boundaries.

An M7 policy must explicitly govern compatibility across at least:

- M6 assessment-policy fingerprints or declared compatible policy families;
- discrepancy/assertion codes;
- participant-evidence stages such as A1 versus A2;
- measurement conditions;
- objective-evidence compatibility already embedded upstream;
- context definitions.

Different M6 policies, stages, or measurement conditions are not silently normalized
into one homogeneous sample.

A policy may permit a bounded mixed set, but the exact compatibility rule and retained
conditions must remain inspectable.

## Measurement condition remains attached

M7 preserves upstream measurement states such as:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

Instrument awareness alone still does not equal contamination.

A versioned M7 assessment policy may include or exclude deviating/contaminated evidence,
but it must never erase the condition to manufacture a cleaner recurrence history.

## Assessment status semantics

### `insufficient`

The available evidence cannot support a recurrence assessment under the exact policy.
Examples include too few assessable units, incompatible policy/stage evidence, or no
qualified hypothesis-relevant links.

### `isolated`

Exactly one qualifying supporting recurrence unit exists under the policy.

This is useful evidence, but explicitly **not recurrence**.

### `candidate_recurrence`

At least two qualifying independent supporting units exist and common structure is
traceable, but one or more stronger support gates remain open.

Candidate recurrence is an instruction to test the hypothesis, not to elaborate it as
if already true.

### `supported_recurrence`

The exact versioned policy's support threshold and required review gates are met,
including explicit consideration of contradiction/counterexamples and competing
explanations as required by that policy.

This means only that a bounded participant-specific **descriptive recurrence hypothesis**
is supported under that evidence and policy.

It does not establish a hidden cognitive cause or permanent trait.

### `contradicted`

The policy's contradiction rule is met by relevant comparable evidence.

Historical support remains preserved. Contradiction does not rewrite the past.

### `unclear`

Material unresolved evidence/coding disagreement or incompatible interpretations prevent
a stronger current conclusion.

M7 must not resolve `unclear` by selecting whichever coding produces the preferred
hypothesis state.

## Recurrence status is not authority lifecycle

M7 freezes two separate axes.

### Evidence/recurrence assessment

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

### Authority lifecycle

```text
active
retired
superseded
```

A hypothesis may be `active + contradicted`, for example, while the team decides whether
to retire it or gather more evidence.

Retirement is an explicit append-only `HypothesisLifecycleEvent`. It must not delete
historical support, contradiction, or prior assessments.

`superseded` means an explicit lifecycle event names a later hypothesis lineage that
replaces the old one for current use while preserving both histories.

## Evidence summary instead of a universal weakness score

M7A freezes no global weakness score and no universal learner-confidence scalar.

A current assessment should expose structured evidence such as:

```text
independent support count
support position IDs
support game IDs
contradiction count
successful counterexample count
context exception count
unclear count
measurement conditions represented
policy identity
context identity
```

If a later policy introduces a strength label or calibrated probability, that label must
be separately defined, versioned, and validated. It is not part of the initial M7A
contract.

## Competing explanations are first-class review obligations

Pilot 004 requires consideration of alternatives.

A hypothesis revision may therefore cite competing hypothesis lineages or preserve
provenance-bound unresolved alternative notes.

`competing_explanations_review` in `HypothesisAssessment` records what alternatives were
considered under the policy.

Important:

```text
competing explanation recorded
!= competing explanation refuted
```

and:

```text
supported recurrence
!= causal explanation selected
```

The initial M7 contract can support a descriptive recurring pattern while causal
interpretation remains unresolved.

## Candidate generation versus testing

M7 preserves Pilot 004's asymmetry:

```text
early evidence may generate a hypothesis candidate
later evidence should test it
```

Once a candidate hypothesis exists, future evidence collection/assessment must actively
admit:

- supporting cases;
- contradictory cases;
- successful counterexamples;
- context-specific exceptions;
- unclear cases.

A ledger that only searches for additional support is not qualified M7 behavior.

M7A does not implement the future position-acquisition strategy itself, but the M7Q
qualification corpus must demonstrate that the ledger can ingest all these evidence
relations without deleting or suppressing them.

## Revision semantics

Hypotheses are revisable without destructive mutation.

Examples:

```text
broad candidate
→ narrower context-bounded revision

candidate recurrence
→ later contradiction
→ retirement

supported recurrence
→ successful counterexamples
→ revised scope or later retirement

new evidence reveals distinct pattern
→ new hypothesis lineage
```

A revision must cite its parent, reason, and author/model provenance.

Historical assessments continue to reference the exact earlier revision they assessed.
A later revision cannot retroactively change what an earlier assessment meant.

Lifecycle changes are separate append-only events rather than statement revisions.

## Identity and reproducibility

All material M7 identities must bind exact inputs.

At minimum:

```text
participant identity
hypothesis lineage and exact revision
exact M6 context/assessment/assertion refs
evidence-link relation and mapping provenance
context-definition refs
measurement conditions
assessment-policy fingerprint
support/contradiction/counterexample/exception/unclear refs
recurrence and independence unit identities
assessment status
lifecycle event history for derived authority state
```

If human/model coding creates an evidence link or context mapping, its nondeterminism is
isolated in an immutable coding/mapping record.

Given identical frozen upstream records, evidence links, hypothesis revision, lifecycle
events, and assessment policy, final assessment and ledger-snapshot
serialization/fingerprints should be deterministic.

## Historical evidence is append-only

M7 must not:

- rewrite M6 assessments when a hypothesis changes;
- remove contradictory evidence because a hypothesis remains useful;
- delete support when a hypothesis is later contradicted;
- mutate an old hypothesis statement in place;
- overwrite one coder's mapping with another coder's mapping;
- rewrite or delete lifecycle events;
- collapse a superseded hypothesis into its replacement.

Current state is derived from preserved history.

## Research compatibility

Pilot 004's frozen recurrence policy remains a research artifact, not a production data
file to mutate.

M7A preserves its key methodological requirements:

```text
more than one independent position
traceable common structure
comparable reasoning evidence
controls and contradictory cases
competing explanations
future testing rather than support-only elaboration
hypotheses may disappear
```

The production contract tightens two boundaries beyond the short research document:

1. M4 controls are not automatically contradictions/counterexamples;
2. M6 `no_supported_discrepancy` is not automatically negative evidence unless the exact
   hypothesis-relevant dimension was observed and comparable.

These tightenings preserve the research intent while preventing cross-layer authority
collapse.

## What M7 may eventually claim after full qualification

M7 may eventually make bounded statements such as:

- one participant-specific descriptive hypothesis has only isolated support;
- the same explicitly defined discrepancy pattern appears across multiple independent
  positions satisfying an explicit context rule;
- recurrence is a candidate but stronger review gates remain open;
- recurrence is supported under an exact versioned M7 policy;
- relevant contradictory evidence exists;
- relevant successful counterexamples exist;
- the hypothesis appears context-specific;
- material coding disagreement makes the current state unclear;
- a hypothesis was revised, retired, or superseded while preserving history.

## Claims prohibited in M7

M7 must not claim merely from recurrence evidence that:

- an unreported idea was never considered;
- a descriptive recurring pattern is a directly observed cognitive mechanism;
- a recurring pattern is a permanent personality/ability trait;
- a causal explanation has been proved;
- a learner has mastered or eliminated the pattern;
- a hypothesis is `training eligible` merely because it is supported;
- a particular intervention should be prescribed;
- an intervention is effective;
- tutoring caused improvement;
- learning, transfer, or mastery occurred.

Those remain M8-M11 and/or separate validation concerns.

## M7 implementation sequence

### M7A — contract freeze

This document plus ADR 0006 freeze the Learner Hypothesis Ledger boundary.

Status after M7A:

> **M7A CONTRACT FROZEN — M7B IMPLEMENTATION NOT STARTED**

### M7B — immutable hypothesis/evidence ledger

Implement only:

- stable `LearnerHypothesis` identity;
- append-only `HypothesisRevision`;
- immutable `HypothesisLifecycleEvent` authority history;
- immutable `HypothesisEvidenceLink`;
- exact upstream M6 provenance binding;
- explicit support/contradiction/counterexample/exception/unclear relations;
- deterministic identities/fingerprints.

Initial M7B qualification may use precomputed or human-supplied mapping/coding records.
It must not yet infer recurrence status automatically unless that behavior is separately
implemented under M7C.

### M7C — recurrence assessment and derived ledger state

Implement:

- `HypothesisAssessmentPolicy`;
- recurrence-unit and independence accounting;
- policy/stage/measurement compatibility rules;
- context matching under exact rule/coding provenance;
- deterministic aggregation of frozen evidence links;
- `HypothesisAssessment` statuses;
- structured evidence summaries;
- deterministic `HypothesisLedgerSnapshot` derivation including lifecycle state.

M7C must not add pedagogy or intervention eligibility.

### M7Q — full M7 qualification

Qualify the complete M7A claim surface across M7B + M7C.

The corpus must include at least:

```text
one supporting position → isolated, not recurrence
repeated assessment/coding of one position → no double counting
two distinct positions but independence rule not met → no recurrence inflation
multiple independent supports with common structure → candidate recurrence
policy-qualified support + contradiction/counterexample review → supported recurrence
relevant contradiction retained
successful counterexample retained
irrelevant M4 control → not automatic counterevidence
M6 no_supported_discrepancy with unobserved dimension → not counterexample
context-specific exception → scope evidence, not silent deletion
unclear/unscorable M6 evidence → no manufactured support
A1/A2 stage incompatibility unless policy explicitly permits it
mixed measurement conditions preserved and policy-gated
incompatible M6 assessment-policy families preserved as incompatible unless declared
competing explanation review recorded without claiming causal resolution
hypothesis revision preserves old evidence/assessments
retirement event preserves history
supersession event preserves both hypothesis lineages
deterministic replay / fingerprint identity
no training-eligibility or pedagogy claims
historical Pilot 003/004 artifacts remain unchanged
```

## Qualification gates

M7 may be declared qualified only when all applicable gates pass:

```text
qualified M6 provenance preserved
participant identity is exact and never mixed across hypotheses
one canonical position cannot inflate recurrence through multiple assertions/coders
recurrence requires more than one distinct qualifying position
independence rule is explicit and versioned
common structure is traceable, not opaque similarity
M6 policy/stage/measurement compatibility is explicit
M4 control role is never automatic contradiction/counterexample
M6 no_supported_discrepancy is never automatic negative evidence
missing/unobserved/unscorable evidence is not manufactured into counterevidence
support, contradiction, successful counterexamples, exceptions, and unclear evidence coexist
competing explanations are reviewed without pretending they were refuted
recurrence assessment status is separate from authority lifecycle
no universal weakness/confidence scalar
hypothesis revisions are append-only
lifecycle events are append-only and reconstruct current authority state
retirement/supersession preserve history
no causal cognitive claim
no pedagogical prescription or intervention efficacy claim
historical research artifacts remain unchanged
pytest passes
Ruff passes
exact candidate-head CI passes
merge is tree-identical to the qualified head
post-merge CI passes
```

## Explicitly deferred

M7A does not implement or freeze:

- causal cognitive-mechanism inference;
- permanent learner-trait ontology;
- automatic LLM hypothesis generation;
- embedding/semantic-cluster similarity;
- intervention eligibility;
- tutoring-session behavior;
- exercise selection;
- learning/transfer/mastery state;
- global numeric weakness score;
- calibrated probabilistic learner model;
- database/event-store technology;
- web or CLI presentation.

## M7A claim ceiling

Freezing M7A does **not** itself authorize the repository to claim recurrence or a
supported learner hypothesis.

After M7A alone, the repository may claim only that it has frozen an explicit contract
for how future M7 implementation must preserve participant-specific cross-position
support, contradiction, counterexamples, context, uncertainty, alternatives, revision,
lifecycle history, and reproducibility.

M7 production claims begin only after the relevant implementation slice is separately
qualified.