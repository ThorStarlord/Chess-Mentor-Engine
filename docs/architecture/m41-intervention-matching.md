# M41 — Ontology-Aware Intervention Matching

## Purpose

M41 gives an exact M40 `TEACH_CONCEPT` proposal a deterministic candidate-matching
consumer. It combines current M39 concept context, the qualified Chess Knowledge
Ontology, explicit semantic profiles for registered M9 interventions, and a versioned
matching policy.

M41 answers:

> Which registered interventions are explicit semantic candidates for this exact
> teaching need?

It deliberately does **not** answer:

> Which intervention has M9 selected, or which intervention will work best?

## Inputs

M41 binds:

- one exact `NextSessionPlan`;
- one exact contained `NextSessionActionCandidate` whose action is `TEACH_CONCEPT`;
- the exact M39 `HypothesisEvidenceSynthesis` referenced by that proposal;
- one exact `OntologyRegistry` snapshot/fingerprint;
- one exact M9 `InterventionRegistry`;
- zero or more exact `InterventionSemanticProfile` sidecars;
- one versioned `InterventionMatchingPolicy`.

The proposal and synthesis must agree exactly on participant, current hypothesis
revision, M39 identity, and concept IDs.

## Semantic profile sidecar

M9 intervention definitions intentionally contain inspectable training content without
ontology IDs. M41 does not alter that qualified M9 schema and does not infer ontology
semantics by parsing `title`, `target_behavior`, `rationale`, or exercise prose.

Instead, an `InterventionSemanticProfile` explicitly binds one exact M9 intervention
version to:

```text
target_concept_ids
reinforce_concept_ids
contraindicated_concept_ids
training_modes
```

The profile is content-addressed, binds the exact ontology fingerprint, and carries
human/model/template-compatible `TrainingContentProvenance`.

This keeps the distinction:

```text
training content text
!= ontology semantic profile
!= participant-specific M9 applicability judgment
!= M9 selection
!= intervention efficacy
```

## Existing ontology is sufficient for v1

M41 v1 uses existing K0–K7 concept IDs and existing `PedagogyMetadata`, especially:

```text
prerequisites
training_modes
recognition_questions
common_misconceptions
learner_band
```

No generic K8 or ontology schema expansion is needed for M41 v1. Future ontology
changes must be pulled by a concrete consumer case that cannot be represented by the
current schema and must be qualified together with that consumer.

## Matching statuses

M41 emits one candidate record for every exact registered intervention:

```text
eligible_candidate
    explicit target-concept overlap

possible_candidate
    reinforcement or pedagogy training-mode overlap without exact target overlap

insufficient_information
    no exact semantic profile was supplied

ineligible
    explicit contraindication or no explicit semantic overlap
```

Missing profiles are not repaired with free-text similarity. The result records an
explicit matching gap instead.

## Prerequisites

Ontology prerequisites associated with the current target concepts are exposed as
`unverified_prerequisites`.

That name is deliberate:

```text
concept has pedagogical prerequisite X
!= participant lacks X
!= participant has mastered X
```

M41 v1 does not have authority to infer learner prerequisite state.

## Ranking policy

The default content-addressed policy orders candidates by:

1. match status (`eligible`, `possible`, `insufficient`, `ineligible`);
2. exact target-concept overlap;
3. ontology training-mode overlap;
4. reinforcement overlap;
5. stable intervention key.

This ordering is transparent product policy, not a learned score and not empirical
proof of optimal pedagogy.

Multiple eligible candidates remain multiple eligible candidates. M41 does not choose
one merely because a stable ranking exists.

## Handoff to M9

The intended authority chain is:

```text
M39 evidence synthesis
+ M40 TEACH_CONCEPT proposal
+ K0-K7 concept/pedagogy semantics
+ explicit M41 semantic profiles
+ M9 intervention registry
        |
        v
M41 candidate set
        |
        v
explicit participant-specific M9 applicability mapping
        |
        v
existing M9 selection policy
```

M41 may reduce the search burden for authoring an M9 applicability mapping. It does
not create that mapping or exercise M9 selection authority in v1.

## Authority ceiling

M41 output carries:

```text
selection_authority = not_exercised
efficacy = not_established
mastery = not_established
```

Preserve:

```text
M41 eligible candidate != M9 applicable mapping
M41 rank 1 != M9 selected intervention
M41 candidate != effective intervention
pedagogy prerequisite != learner deficiency
concept overlap != causal diagnosis
```

## Failure-closed behavior

M41 rejects:

- a proposal not contained in the exact M40 plan;
- non-`TEACH_CONCEPT` M40 actions;
- missing/drifted M39 proposal identity;
- participant or current-revision mismatch;
- proposal/M39 concept-context drift;
- malformed or tampered M9 intervention/registry identities;
- duplicate semantic profiles for one intervention;
- profiles for interventions outside the exact M9 registry;
- profile/intervention identity drift;
- ontology/profile fingerprint or concept-ID drift;
- policy/profile/candidate-set replay tampering.

## Non-goals

M41 v1 does not:

- rewrite M9 definitions;
- infer mappings from free text;
- create participant-specific M9 applicability judgments;
- select an intervention;
- mutate M7/M11;
- establish intervention efficacy, learning, transfer, or mastery;
- call a model/provider;
- expand the ontology merely for completeness.
