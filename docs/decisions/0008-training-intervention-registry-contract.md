# ADR 0008 — Training Intervention Registry Contract

**Status:** Accepted for M9  
**Scope:** bounded participant-specific intervention definition, mapping, and selection  
**Supersedes:** none

## Context

M8 qualified a clean evidence-aware tutoring-session boundary but explicitly stopped
before training eligibility, intervention IDs, exercise definitions, curriculum
selection, or effectiveness claims.

Pilot 004 provides the relevant research constraint:

```text
supported recurrence across independent positions
+ challenge review
+ pedagogical actionability
+ participant-specific relevance
→ may become eligible for a later intervention

eligibility / selection
!= intervention effectiveness
```

M9 must therefore introduce real training-intervention records without collapsing the
qualified M7 learner-hypothesis boundary into an automatic prescription or collapsing
a prescription into evidence of learning.

## Decision 1 — Exercise definitions are explicit, versioned content

M9 introduces `ExerciseDefinition` with:

- stable exercise key and material version;
- inspectable instructions;
- position-source rule (`historical_position`, `fresh_position`, or `mixed`);
- expected response schema;
- completion-evidence schema;
- optional duration hint;
- human/model/template authorship provenance;
- content-addressed identity.

Completion evidence describes what was submitted or completed. It does not define
transfer, mastery, or intervention effectiveness.

## Decision 2 — Intervention definitions compose exercises

`TrainingInterventionDefinition` contains:

- stable intervention key and material version;
- target observable behavior;
- pedagogical rationale;
- one or more exact versioned exercises;
- dosage guidance;
- explicit exclusion notes;
- content authorship provenance.

An intervention definition is a prescription artifact, not a claim that the
prescription is effective or optimal.

## Decision 3 — The registry is an immutable versioned snapshot

`InterventionRegistry` contains exactly one current definition per intervention key.
The registry is canonically ordered and content-addressed.

Changing an exercise, intervention, registry membership, or material version changes
identity rather than silently rewriting earlier selections.

## Decision 4 — M7 recurrence does not directly select training

M9 requires an explicit `HypothesisInterventionMapping` between:

```text
exact participant-specific M7 HypothesisRevision
→ exact registered TrainingInterventionDefinition
```

The mapping records one of:

```text
applicable
not_applicable
unclear
```

and carries human/model provenance, rationale, uncertainty notes, and timestamp.

This mapping is the explicit pedagogical judgment boundary. M9 does not infer
pedagogical actionability directly from free-text hypothesis wording.

## Decision 5 — Initial eligibility policy is deliberately conservative

The initial `InterventionSelectionPolicy` requires:

```text
current M7 revision
+ active hypothesis lifecycle
+ latest M7 status == supported_recurrence
+ exact registered mapping evidence
```

No `isolated`, `candidate_recurrence`, `contradicted`, or `unclear` M7 hypothesis may
be selected under M9 v1.

The policy claim scope is fixed to:

```text
participant_specific_intervention_selection
```

## Decision 6 — One applicable mapping may be selected; ambiguity is preserved

The initial deterministic selection rule is:

```text
exactly one applicable mapping
→ selected

more than one applicable mapping
→ unclear

no applicable mapping + at least one unclear mapping
→ unclear

no applicable mapping
→ ineligible
```

M9 does not invent a ranking score or call one intervention "best" when multiple
applicable interventions remain.

## Decision 7 — Upstream current-state provenance is revalidated

Selection revalidates:

- exact M7 `HypothesisLedgerSnapshot` identity/fingerprint;
- exact `HypothesisRevision` identity/fingerprint;
- participant identity;
- current-revision correspondence;
- active/retired/superseded lifecycle state;
- latest current M7 assessment reference/status;
- exact registry identity/fingerprint;
- exact intervention/exercise identities;
- exact applicability-mapping identities;
- chronology.

Hash-consistent but unrelated or cross-participant substitutions are rejected.

## Decision 8 — M9 selection is not an outcome record

`InterventionSelectionDecision` records only:

- exact participant and M7 current-state provenance;
- exact registry and policy identity;
- all considered mapping refs;
- `selected`, `ineligible`, or `unclear`;
- optional selected intervention ref;
- deterministic reasons;
- timestamp.

It does not contain:

- intervention outcome;
- pre/post improvement score;
- causal effect estimate;
- learning state;
- transfer state;
- mastery state.

## Decision 9 — M10 owns transfer / mastery evidence

A later milestone may evaluate a selected intervention against fresh evidence.
That future boundary must preserve:

```text
selection made
!= intervention completed
!= behavior changed
!= intervention caused change
!= transfer
!= mastery
```

M9 does not pre-authorize those claims.

## Consequences

### Positive

- training content becomes versioned and inspectable;
- descriptive learner evidence and pedagogical judgment remain separate;
- participant-specific applicability has explicit provenance;
- deterministic selection can fail closed instead of guessing;
- multiple plausible interventions remain visible as uncertainty;
- M10 can later evaluate intervention results from a clean provenance boundary.

### Costs

- supported recurrence alone is intentionally insufficient for selection;
- intervention authors must define exercises and mapping rationale explicitly;
- the initial policy does not rank multiple applicable interventions;
- M9 establishes no intervention-effectiveness evidence.

## Rejected alternatives

### Automatically prescribe from `supported_recurrence`

Rejected because recurrence is a descriptive M7 result, not a pedagogical mapping.

### Let a model choose any free-form exercise at selection time

Rejected because the selected artifact would not have stable versioned identity or an
inspectable registry provenance chain.

### Rank multiple mappings with an opaque model score

Rejected for M9 v1 because it would introduce an unqualified curriculum-ranking claim.

### Treat exercise completion as learning

Rejected because completion evidence, behavioral change, transfer, and mastery are
different claims and belong to later validation layers.
