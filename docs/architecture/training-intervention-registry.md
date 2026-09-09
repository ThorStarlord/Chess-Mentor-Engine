# M9 — Training Intervention Registry

**Status:** qualified  
**Contract:** ADR 0008  
**Production package:** `src/chess_mentor_engine/training/`

## Purpose

M9 is the first production layer allowed to turn qualified participant-specific
learner evidence into an explicit training-selection decision.

The qualified boundary is:

```text
current active M7 hypothesis revision
+ latest supported_recurrence status
+ versioned intervention registry
+ explicit human/model applicability mapping
+ conservative M9 selection policy
→ selected / ineligible / unclear
```

This is intentionally narrower than a curriculum engine and intentionally weaker than
an effectiveness claim.

## Package surface

```text
chess_mentor_engine.training
├── model.py
│   ├── TrainingContentProvenance
│   ├── InterventionMappingProvenance
│   ├── ExerciseDefinition
│   ├── TrainingInterventionDefinition
│   ├── TrainingInterventionRef
│   ├── InterventionRegistry
│   ├── HypothesisInterventionMapping
│   ├── HypothesisInterventionMappingRef
│   ├── InterventionSelectionPolicy
│   ├── InterventionSelectionPolicyRef
│   └── InterventionSelectionDecision
└── registry.py
    ├── define_exercise
    ├── define_training_intervention
    ├── build_intervention_registry
    ├── record_hypothesis_intervention_mapping
    ├── define_intervention_selection_policy
    └── select_training_intervention
```

## Authority model

M9 preserves the repository's accumulated authority separation:

```text
objective chess evidence
!= participant self-report
!= M6 local discrepancy
!= M7 descriptive recurrence
!= M9 pedagogical applicability judgment
!= M9 deterministic selection decision
!= intervention effect
!= learning / transfer / mastery
```

### Exercise / intervention definition authority

Exercise and intervention content may be authored by a human, model, or template, but
it must carry exact author/version/instruction/run provenance.

Definitions are content-addressed and versioned. Earlier definitions remain auditable
after later revisions.

### Applicability authority

The bridge from one exact M7 hypothesis revision to one exact registered intervention
is never inferred from free-text similarity inside M9.

It is an explicit `HypothesisInterventionMapping` with:

```text
applicable | not_applicable | unclear
```

plus human/model provenance, rationale, uncertainty, and timestamp.

That mapping is pedagogical judgment. It is not chess truth, participant evidence, or
M7 recurrence evidence.

### Selection authority

`InterventionSelectionPolicy` is deterministic application logic.

M9 v1 requires:

- exact participant match;
- exact current M7 revision;
- active hypothesis lifecycle;
- latest M7 assessment status `supported_recurrence`;
- exact registry membership;
- exact applicability-mapping identity;
- one and only one applicable mapping.

The result is `selected`, `ineligible`, or `unclear`.

## Why the registry is separate from selection

A registry answers:

> What bounded training artifacts exist, in which exact versions?

A mapping answers:

> Does this exact participant-specific hypothesis plausibly map to this artifact?

A selection decision answers:

> Under this exact M9 policy and current M7 state, may one intervention be selected?

Keeping those questions separate prevents an intervention definition from smuggling in
eligibility and prevents eligibility from smuggling in effectiveness.

## Exercise semantics

`ExerciseDefinition` stores inspectable practice instructions and the evidence schema
needed to record completion.

The initial source vocabulary is:

```text
historical_position
fresh_position
mixed
```

A completion-evidence schema may describe submitted candidates, replies, explanations,
or other bounded outputs. It does not by itself define success, learning, transfer, or
mastery.

## Deterministic identities

M9 uses the repository-wide canonical JSON + SHA-256 pattern.

Material inputs determine identities for:

- exercises;
- intervention definitions;
- registry snapshots;
- hypothesis/intervention mappings;
- selection policy fingerprints;
- selection decisions.

Registry ordering and mapping ordering are canonicalized where order is not semantic.
Exercise ordering inside an intervention remains material because it may represent an
intended practice sequence.

## Failure-closed selection

The initial policy deliberately avoids ranking heuristics.

```text
supported active current hypothesis
+ one applicable mapping
→ selected

supported active current hypothesis
+ multiple applicable mappings
→ unclear

supported active current hypothesis
+ unclear mapping only
→ unclear

supported active current hypothesis
+ no applicable mapping
→ ineligible

anything below supported_recurrence / inactive / stale / unassessed
→ ineligible
```

Cross-participant mappings, stale or forged fingerprints, and mappings to definitions
outside the exact registry are rejected rather than converted into a decision.

## Focused qualification contract

`tests/test_m9_qualification.py` covers:

1. deterministic exercise identity and material versioning;
2. deterministic registry ordering and duplicate-key rejection;
3. required uncertainty provenance for unclear applicability;
4. successful supported-active-current single-mapping selection;
5. isolated recurrence remaining ineligible;
6. missing current M7 assessment remaining ineligible;
7. retired hypotheses remaining ineligible;
8. stale revisions remaining ineligible;
9. unclear applicability remaining unclear;
10. multiple applicable interventions remaining unclear rather than ranked;
11. unregistered intervention substitution rejection;
12. cross-participant mapping rejection;
13. mapping-order deterministic replay;
14. material policy-version identity;
15. upstream boundary fingerprint tamper rejection;
16. absence of effect/learning/transfer/mastery authority in selection state.

The first complete implementation head was:

```text
ff89457eed84a6ecf582095e9363837e175fe6ac
```

GitHub Actions run `34329397446` qualified that implementation with:

```text
336 passed
8 intentional external-engine skips in the normal suite
16 / 16 focused M9 qualification tests passed
Ruff PASS
external Stockfish integration PASS
```

The full repository suite and external Stockfish witness remain the regression gates.

## Claim ceiling after M9

The repository may now claim that it can:

- define inspectable versioned exercises and training interventions;
- freeze an immutable registry snapshot;
- record explicit participant-specific hypothesis/intervention applicability with
  human/model provenance;
- deterministically select at most one registered intervention when an exact active
  current M7 hypothesis has `supported_recurrence` status under the cited M9 policy;
- return `ineligible` or `unclear` instead of inventing a prescription;
- replay the same M9 selection from the same exact inputs.

The repository may **not** yet claim:

- the selected intervention is optimal or best;
- the intervention is effective;
- exercise completion caused behavioral change;
- a post-training difference was caused by the intervention;
- learning, transfer, or mastery occurred;
- longitudinal learner state has been established.

Those claims require later evidence, beginning with M10 Transfer / Mastery Evidence.
