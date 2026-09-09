# ADR 0006 — Learner Hypothesis Ledger Contract

## Status

Accepted for M7A. Production implementation is not authorized by this ADR alone.

## Context

M6 is fully qualified and deliberately stops at one selected position. It can establish
position-local discrepancy facts, provenance-bound human/model coding, conservative
local assertions, and a bounded local assessment without claiming recurrence.

The next product risk is cross-position aggregation. The system now has enough local
evidence that an unconstrained implementation could easily overclaim:

```text
one local mismatch
→ recurring learner weakness

several similar-looking positions
→ same pattern

M4 control
→ contradiction

M6 no_supported_discrepancy
→ proof of improvement

repeated descriptive pattern
→ causal cognitive trait
```

Pilot 004's frozen recurrence policy requires more than one independent position,
traceable common structure, comparable reasoning evidence, review of controls and
contradictory cases, and consideration of alternatives. It also requires later batches
to test candidate hypotheses rather than merely elaborate them and explicitly allows
hypotheses to disappear.

The repository build plan likewise calls for an evidence-backed, revisable participant-
specific hypothesis/contradiction ledger with support, contradiction, context,
competing explanations, evidence strength, and revision history.

M7 must preserve those methodological commitments without collapsing evidence into a
static weakness score, causal diagnosis, or pedagogy.

## Decision

M7 will maintain participant-specific, append-only learner hypotheses over qualified
cross-position M6 evidence.

The governing boundary is:

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

with:

```text
local discrepancy
!= recurring pattern
!= causal cognitive mechanism
!= permanent learner trait
!= pedagogical prescription
```

## Decision 1 — Initial M7 hypotheses are descriptive, not causal

The initial production hypothesis kind is:

```text
descriptive_pattern
```

A hypothesis must be participant-specific, falsifiable by future evidence,
evidence-mappable, context-bounded, and revisable.

M7 may support a statement that a bounded discrepancy pattern recurs under an exact
policy. It may not infer hidden psychological mechanisms such as `tunnel vision`,
`weak working memory`, or `overconfidence` merely from recurrence.

## Decision 2 — M7 preserves all upstream authority domains

M7 must keep separate:

```text
deterministic chess fact
!= engine judgment
!= M4 selection/control role
!= M5 participant report
!= M6 deterministic fact
!= M6 semantic coding
!= M6 local assertion
!= M7 evidence mapping
!= M7 recurrence assessment
```

Every M7 evidence relation must cite exact qualified upstream identities.

## Decision 3 — Hypothesis identity, revision, and lifecycle are separate

`LearnerHypothesis` provides stable lineage identity from participant identity plus an
origin proposal fingerprint/provenance. It does not depend on a circular reference to
its first revision.

Material changes to statement or scope are represented by append-only
`HypothesisRevision` records. Earlier revisions remain immutable.

Authority changes are represented separately through append-only
`HypothesisLifecycleEvent` records. A new hypothesis is active by default; retirement
or supersession is an explicit event. Supersession cites the replacing hypothesis
lineage.

If a proposition is materially different rather than a genuine refinement of the same
lineage, it receives a new hypothesis identity.

## Decision 4 — Evidence mapping is an explicit derived record

M7 introduces immutable `HypothesisEvidenceLink` records.

Initial relations are:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
```

The mapping itself must distinguish deterministic rule-based mapping from semantic
human/model coding. Semantic mapping retains coder/model/rubric/run provenance.

M7 must not assume that every M6 discrepancy automatically supports a particular
hypothesis.

## Decision 5 — One canonical participant-position is one recurrence unit

Multiple assertions, coders, stages, or repeated assessments for the same participant
and canonical `position_id` may enrich the evidence but must not become multiple
recurrence instances.

This prevents double counting.

Every recurrence assessment policy must additionally define an independence rule.
M7A does not claim statistical independence merely from distinct position IDs.

## Decision 6 — Recurrence requires more than one distinct qualifying position

No policy may classify one position as recurrence.

At minimum:

```text
candidate recurrence
→ at least two qualifying distinct positions
```

The exact stronger threshold for `supported_recurrence` is versioned policy, not
universal product truth.

## Decision 7 — Independence is explicit policy

`HypothesisAssessmentPolicy` must state how supporting units count as independent.

The initial qualification policy is expected to use a conservative basis such as
distinct game IDs, but the contract does not equate that proxy with formal statistical
independence.

Changing the independence rule changes policy identity.

## Decision 8 — Common structure must be traceable

M7 must not use opaque resemblance as recurrence evidence.

Common structure must come from:

- exact upstream deterministic attributes;
- an explicit versioned context rule; or
- provenance-bound human/model context coding.

Embedding similarity, latent clustering, or unconstrained LLM grouping is not
authorized as initial M7 recurrence authority.

## Decision 9 — Cross-position comparability is explicit

The M7 assessment policy must govern compatibility across at least:

- M6 assessment-policy fingerprints or declared compatible families;
- discrepancy/assertion codes;
- participant-evidence stages;
- measurement conditions;
- context definitions.

Different policy/stage/measurement regimes are not silently normalized into one sample.

## Decision 10 — Measurement conditions remain attached

M7 preserves upstream states such as:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

A versioned policy may include or exclude deviating/contaminated evidence, but it may
not erase the condition.

## Decision 11 — M4 control is not automatic M7 counterevidence

This is a hard rule:

```text
M4 operational control
!= M7 contradiction
!= M7 successful counterexample
```

A control can become M7 counterevidence only after qualified M5/M6 evidence shows that
the exact hypothesis-relevant dimension was observed and assessable in a matching
context and an explicit M7 mapping rule/coding links it accordingly.

## Decision 12 — M6 no-supported-discrepancy is not automatic negative evidence

This is also a hard rule:

```text
M6 no_supported_discrepancy
!= M7 contradiction
!= M7 successful counterexample
```

It can become counterevidence only when the hypothesis-relevant dimension was observed,
assessable, comparable, context-matching, and explicitly mapped under the M7 policy.

`not_observed`, `not_comparable`, `unclear`, and `unscorable` must never be converted
into negative evidence merely to satisfy a recurrence test.

## Decision 13 — Support and challenge evidence coexist

M7 must preserve simultaneously:

```text
support
contradiction
successful counterexamples
context exceptions
unclear evidence
```

Later support does not delete contradiction. Later contradiction does not delete
historical support.

A qualified ledger is therefore not a support-only collection.

## Decision 14 — Candidate hypotheses must be tested, not merely elaborated

Once a candidate exists, subsequent assessment must admit evidence that could weaken or
retire it.

M7Q must demonstrate ingestion of support, contradiction, successful counterexamples,
context exceptions, and unclear cases.

A search process that only adds support cannot qualify the M7 contract.

## Decision 15 — Competing explanations are first-class review obligations

A hypothesis revision may cite competing hypotheses or provenance-bound unresolved
alternative notes.

An assessment records whether required alternative review occurred.

This distinction is frozen:

```text
alternative considered
!= alternative refuted
```

and:

```text
supported recurrence
!= causal explanation selected
```

## Decision 16 — Recurrence assessment and authority lifecycle are separate axes

Initial recurrence assessment statuses are:

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

Authority lifecycle is separately:

```text
active
retired
superseded
```

A hypothesis may remain active while contradicted or unclear. Retirement/supersession
is explicit append-only `HypothesisLifecycleEvent` history, not an automatic destructive
mutation.

M7A does not freeze an automatic reactivation rule. A future reactivation transition
would require an explicit versioned extension.

## Decision 17 — Assessment status meanings are narrow

`insufficient` means the exact policy lacks enough qualified/comparable evidence.

`isolated` means one qualifying supporting recurrence unit exists and explicitly is not
recurrence.

`candidate_recurrence` means at least two independent qualifying supports with
traceable common structure exist but stronger policy gates remain open.

`supported_recurrence` means the exact support threshold and required challenge/
alternative review gates are satisfied.

`contradicted` means the exact contradiction rule is met.

`unclear` preserves material unresolved evidence/coding disagreement.

None is a permanent learner label or causal diagnosis.

## Decision 18 — No universal weakness/confidence scalar

M7A freezes no global learner weakness score and no universal confidence scalar.

`HypothesisAssessment` instead exposes structured evidence counts/refs, source positions
and games, measurement conditions, policy identity, and context identity.

Any future calibrated strength/probability must be separately defined and validated.

## Decision 19 — Hypothesis assessments are versioned and material

Every final cross-position assessment cites a versioned `HypothesisAssessmentPolicy`
that fixes material rules including recurrence thresholds, independence, context
matching, measurement/stage compatibility, contradiction handling, and required review
obligations.

Changing a material rule changes policy fingerprint and therefore assessment identity.

## Decision 20 — M7 outputs append-only evidence-bound records

The initial semantic record set is:

```text
LearnerHypothesis
HypothesisRevision
HypothesisLifecycleEvent
HypothesisEvidenceLink
HypothesisAssessmentPolicy
HypothesisAssessment
HypothesisLedgerSnapshot
```

Current state is derived from immutable history. A ledger snapshot contains per-
hypothesis entries binding current revision, latest assessment, current authority
lifecycle state, and latest lifecycle-event reference.

A later revision, assessment, retirement, or supersession may not rewrite prior M6
records, prior evidence links, prior revisions, prior lifecycle events, or prior
assessments.

## Decision 21 — Nondeterministic semantic work is isolated

Human/model hypothesis wording, context coding, or evidence mapping may be
nondeterministic.

Such work must be frozen in immutable provenance-bound records.

Given identical frozen upstream evidence, hypothesis revision, evidence links, lifecycle
events, and assessment policy, the assessment and ledger snapshot should serialize/
fingerprint deterministically.

Live model invocation is not required for initial M7 qualification.

## Decision 22 — M7 is not pedagogy

M7 must not infer:

```text
training eligible
needs tactics training
practice candidate generation
assign intervention X
```

from supported recurrence alone.

M8 tutoring behavior and M9 intervention selection require their own boundaries.

## Decision 23 — M7 does not establish learning or mastery

A later absence of a discrepancy may weaken or contradict a hypothesis under a proper
policy, but M7 must not call that improvement, learning, transfer, competency, or
mastery.

Those require M10/M11 and separate evidence.

## Decision 24 — Research artifacts remain immutable historical authorities

Pilot 004's recurrence policy informs M7A but remains unchanged.

M7A preserves its principles while tightening two production boundaries:

1. M4 controls require an explicit M7 evidence mapping before they become
   counterexamples/contradictions;
2. M6 `no_supported_discrepancy` requires observed, comparable, hypothesis-relevant
   evidence before it becomes counterevidence.

These tightenings prevent authority collapse without changing the research artifact.

## Decision 25 — M7 implementation proceeds in bounded slices

The authorized sequence after M7A is:

```text
M7B immutable hypothesis/evidence ledger
→ M7C recurrence assessment + derived ledger state
→ M7Q full M7 qualification
```

### M7B

Implement stable hypothesis identity, append-only revisions, append-only lifecycle
events, evidence links, mapping provenance, and deterministic identities only.

Initial qualification may use precomputed/human-supplied semantic mappings.

### M7C

Implement versioned cross-position assessment policy, recurrence/independence
accounting, compatibility/context rules, assessment states, evidence summaries, and
derived snapshots including lifecycle state.

### M7Q

Qualify the complete claim surface including isolated evidence, double-count prevention,
independence, common structure, support, contradiction, successful counterexamples,
context exceptions, unclear evidence, competing explanations, revision, retirement,
supersession, deterministic replay, and research-artifact preservation.

M8 remains unauthorized until M7Q passes, the exact qualified head is merged without
tree drift, post-merge CI passes, and repository status authority is reconciled.

## Consequences

### Positive

- recurrence becomes inspectable rather than rhetorical;
- local M6 evidence remains distinguishable from learner-level inference;
- successful controls and no-discrepancy cases cannot become false counterevidence;
- hypotheses can weaken, narrow, disappear, retire, or be superseded without rewriting
  history;
- contradiction and competing explanations remain visible;
- future tutoring receives explicit hypothesis state rather than mutable weakness labels.

### Costs

- M7 requires several records instead of one `weakness` field;
- many candidate hypotheses will remain isolated, insufficient, or unclear;
- semantic mapping/context coding requires provenance;
- exact recurrence thresholds remain policy-specific rather than convenient universal
  constants;
- pedagogy and learning claims remain unavailable.

These costs are preferable to manufacturing stable learner diagnoses from weak or
incomparable evidence.

## Alternatives considered

### Maintain one mutable weakness score per category

Rejected. It destroys provenance, hides contradiction, and conflates evidence with
interpretation.

### Count every M6 assertion as an independent recurrence observation

Rejected. Multiple assertions/coders/stages on one position would inflate recurrence.

### Treat every M4 control as contradiction

Rejected. M4 control is an objective sampling role, not a hypothesis relation.

### Treat every M6 no-supported-discrepancy result as contradiction

Rejected. The hypothesis-relevant dimension may never have been observed or comparable.

### Use semantic similarity to cluster discrepancies automatically

Rejected for the initial contract. Common structure must be explicit and traceable.

### Promote supported recurrence directly to causal learner trait

Rejected. Descriptive recurrence does not establish mechanism or permanence.

### Add training eligibility to the M7 lifecycle

Rejected. The historical roadmap included `Training Eligible`, `Improving`, and
`Competency Candidate` in an early candidate lifecycle, but the current qualified
milestone sequence separates learner hypotheses, tutoring, interventions, transfer, and
longitudinal mastery. Those later concepts remain outside M7.

### Rewrite a hypothesis in place as evidence changes

Rejected. Revisions and lifecycle actions are append-only and historical assessments
must retain their original meaning.

### Encode lifecycle state only inside snapshots

Rejected. Current lifecycle state would not be reconstructable from append-only
history. `HypothesisLifecycleEvent` is first-class evidence/authority history, while the
snapshot is only a derived view.

## Related records

- `docs/architecture/learner-hypothesis-ledger.md`
- `docs/architecture/reasoning-discrepancy.md`
- `docs/architecture/m6-qualification.md`
- `docs/decisions/0005-reasoning-discrepancy-contract.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/recurrence-policy.md`
- `docs/product/chess-mentor-engine-repository-build-plan.md`
- `docs/product/repository-build-status.md`
