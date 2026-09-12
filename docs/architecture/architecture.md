# Architecture: implemented boundaries through M34 + K0-K7 + M36/M39/M40/M41/M42/M43/M44/M45/M46 + V1 local composition

This document describes the currently implemented architectural boundaries. The moving implementation authority is [`../product/repository-build-status.md`](../product/repository-build-status.md).

## Architectural thesis

Chess Mentor Engine is not one inference pipeline. It is a set of authority-separated layers connected by content-addressed provenance.

```text
objective chess evidence
!= participant evidence
!= learner inference
!= pedagogical applicability / selection
!= outcome / transfer evidence
!= chess semantic context
!= model-authored language
!= evaluator judgment
!= action proposal
!= candidate preparation
!= presentation
!= orchestration composition
```

Composition may bind exact artifacts from several layers, but it does not inherit the authority of those layers.

## Current high-level graph

```text
                         OBJECTIVE CHESS
                 M1-M4 / M14-M18 / M15
          canonical board, features, engine evidence
                              |
                              v
                       PARTICIPANT EVIDENCE
                        M5 / M8 / M23
                              |
                              v
                     POSITION-LOCAL INFERENCE
                              M6
                              |
                              v
                   LEARNER HYPOTHESIS AUTHORITY
                         M7 / M7C
                              |
              +---------------+----------------+
              |                                |
              v                                v
       PEDAGOGY / OUTCOMES                CHESS SEMANTICS
       M9 intervention selection          K0-K7 ontology
       M10 bounded outcome evidence       assertions/detectors
       M11 longitudinal state             M19 sidecar / K7 projection
              |                                |
              +---------------+----------------+
                              |
                              v
                       M36 READ MODEL
                              |
                              v
                       M39 SYNTHESIS
                              |
                              v
                       M40 PROPOSAL
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
 M43 EVIDENCE CANDIDATES  M41 INTERVENTION   M42 TRANSFER /
                          CANDIDATES          RETEST PLAN
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                    M44 REFERENCE VIEW

EXACT M18 QUEUE + EXACT M44 VIEW + OPTIONAL EXACT M42 PLAN(S)
                              |
                              v
                   V1 LOCAL COMPOSITION
                     `cme-local-tutor`
                              |
                              v
                      M45 MENTOR QUEUE
                              |
                              v
             explicit selection + capture consent
                              |
                              v
                   M23 -> persisted M8
                              |
                              v
                    M46 ACTION PROPOSAL
                              |
                              v
           existing M8 EXECUTION / EXPOSURE authority
```

The model/review execution chain remains separately authority-bounded:

```text
M15 evaluation presentation + M6/M7 evidence
-> M16 deterministic mentor grounding
-> optional M19 provenance-bound model request/prose
-> optional M20 evaluator judgment
-> M21-M24 orchestration/provider seams
-> M25-M30 review/persistence/navigation
-> M31 execution-envelope preflight
-> M32 delivery fidelity
-> M33 deterministic feedback trace
-> M34 hermetic recovery reconciliation
```

## M7 / M7C remains learner-recurrence authority

M7 represents participant-specific hypotheses and revision lineage. M7C owns qualified recurrence/contradiction assessment over exact evidence units.

```text
one M6 discrepancy != recurrence
ontology occurrence != recurrence
M43 candidate != M7C relation
M39 explanation != M7C classification
```

## M9 remains intervention-selection authority

M41 is a semantic candidate layer before M9 authority.

```text
M41 eligible candidate != M9 applicable
M41 rank one != M9 selected
M9 selected != effective
```

## M10 remains outcome / transfer authority

M42 is implemented as bounded transfer/retest planning. It binds exact M40/M9 identities, explicit candidate provenance, semantic relation, surface variation, freshness/exposure rules, and M10-compatible reuse keys.

```text
M42 planned retest != completed retest
completed retest != successful transfer
successful transfer != mastery
```

M42 does not create M10 evidence.

## K0-K7 semantic architecture

The ontology provides stable concepts and explanatory semantics while preserving:

```text
concept definition
!= concept assertion
!= participant perception
!= learner inference
```

There is no generic K8 roadmap item merely to make the ontology larger. Any extension must be pulled by a concrete consumer distinction K0-K7 cannot represent safely.

## M36 / M39 / M40 — read, explain, propose

- **M36** composes exact current M7/M7C, M9, M10, M11 and optional K7 information into a participant-scoped read model. No mutation authority.
- **M39** binds the exact current hypothesis evidence and explains support, contradiction, exceptions, gaps, and conditions without reclassifying recurrence.
- **M40** applies an explicit versioned policy and proposes one next action. Its authority is `proposal_only`.

## M43 / M41 / M42 — prepare candidates, do not promote them

- **M43** prepares contradiction/control/evidence candidates without turning them into M7C relations.
- **M41** prepares ontology-aware intervention candidates without exercising M9 selection.
- **M42** prepares bounded transfer/retest plans without creating M10 outcomes.

## M44 — learner-progress reference presentation

M44 validates exact source identities and renders deterministic local reference presentation. Missing optional layers remain missing rather than becoming negative evidence.

```text
presentation composition != presentation rendering != learner inference
```

It does not establish production browser/device/accessibility/usability quality.

## M45 — participant-scoped mentor priority

M45 binds an exact participant-agnostic diagnostic batch to explicit participant scope and ranks a bounded queue with separate, inspectable learner/challenge/transfer/uncertainty/objective/novelty/semantic-diversity dimensions.

```text
M45 priority != learner hypothesis
M45 rank one != M9 selection
M45 rank one != empirically optimal review order
```

## M46 — adaptive Socratic action proposal

M46 consumes exact M8 session state and exact qualified context and proposes a bounded next tutoring action.

```text
M46 proposal != M8 execution
```

Before M8 baseline freeze it cannot expose adaptive help or objective reveal. Assisted responses and post-reveal reflections remain separate evidence classes. Transfer tutoring requires the exact current M42 plan.

Every proposal records a proposal-only execution ceiling and does not establish mastery.

## V1 local tutor composition

`cme-local-tutor start|next` is a composition layer over existing authorities:

```text
exact M18 queue
+ exact M44 view
+ optional exact M42 plans
-> M45 queue
-> explicit operator selection + capture consent
-> M23 authorization/persistence
-> persisted M8 checkpoint
-> M46 proposal
```

It then points the operator back to existing `cme tutor` transitions for actual M8 execution/exposure.

The composition layer:

- is content-addressed and deterministic;
- validates exact identity/fingerprint relationships;
- fails closed on tamper/participant/queue/session drift;
- does not treat M45 rank one as consent;
- does not convert M46 proposal into execution;
- does not convert M42 plan into M10 evidence;
- owns no new chess truth, learner inference, pedagogy selection, outcome, or mastery authority.

## Core invariants

```text
objective chess truth != participant evidence != learner inference
one discrepancy != recurrence != causal trait
concept occurrence != participant perception / learner weakness
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation
M39 synthesis != M7C recurrence authority
M40 proposal != execution
M43 candidate != M7C contradiction/refutation
M41 candidate != M9 applicability mapping / selection
M42 plan != M10 transfer evidence
M44 rendering != learner inference
M45 priority != learner diagnosis / M9 selection
M46 proposal != M8 execution / exposure
V1 composition != upstream authority
M45 rank one != implicit consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
```

## Current non-goals

The implemented architecture does not establish:

- causal cognitive diagnosis/permanent learner traits;
- complete automatic chess-concept detection;
- automatic learner-state mutation from ontology/model outputs;
- intervention efficacy or optimal pedagogy;
- transfer/mastery from plans or practice alone;
- production UI/accessibility/usability quality;
- hosted auth/multi-tenancy/persistence readiness;
- production privacy/security/compliance posture;
- production provider retry/cost/secrets authority.

## Version 1.0 architecture boundary

The architecture/product-consumption gap identified for V1 is now integrated. The remaining repository V1 task is release/distribution qualification, not another architecture layer:

```text
synchronize release identity/version
-> build distributable artifact
-> clean-install in a fresh environment
-> smoke installed commands and package data
-> preserve full repository + Stockfish qualification
```

M35/M37/M38/K8/M47 and hosted-product work remain conditional, optional, post-V1, or external-authority concerns unless a fresh repository audit proves otherwise.
