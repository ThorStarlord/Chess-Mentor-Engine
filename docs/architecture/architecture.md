# Architecture: implemented boundaries through M34 + K0–K7 + M36/M39/M40/M41/M43/M44

This document describes the currently implemented architectural boundaries. The
moving implementation authority is
[`../product/repository-build-status.md`](../product/repository-build-status.md).

## Architectural thesis

Chess Mentor Engine is not one inference pipeline. It is a set of authority-separated
layers connected by content-addressed provenance.

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
```

The architecture is intentionally conservative about promotion between those layers.

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
                +-------------+-------------+
                |                           |
                v                           v
       M43 EVIDENCE CANDIDATES     M41 INTERVENTION CANDIDATES
                |                           |
                +-------------+-------------+
                              |
                              v
                    M44 REFERENCE VIEW
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

M36-M44 do not silently rewrite that path.

## M7 / M7C remains learner-recurrence authority

M7 represents participant-specific hypotheses and their revision lineage. M7C owns the
qualified recurrence/contradiction assessment over exact evidence units.

Preserve:

```text
one M6 discrepancy != recurrence
ontology occurrence != recurrence
M43 candidate != M7C relation
M39 explanation != M7C classification
```

M43 can select already-classified controls for presentation or rank additional M7B
links as **potential** review/reassessment candidates. Only the existing M7C/human
review path may establish the recurrence relation under its own contract.

## M9 remains intervention-selection authority

M9 separates:

```text
registered intervention definition
!= participant-specific applicability mapping
!= deterministic selection decision
!= intervention effect
```

M41 adds a semantic candidate layer before that authority. Exact
`InterventionSemanticProfile` sidecars bind an M9 intervention version to ontology
concept targeting/reinforcement/contraindication and training modes.

M41 deliberately does not parse training prose to create a mapping.

```text
M41 eligible_candidate != M9 applicable
M41 rank 1 != M9 selected
M9 selected != effective
```

## M10 remains outcome / transfer authority

M10 owns bounded practice, near-transfer, far-transfer, and real-game evidence. M40
may propose a transfer test, but a proposal is not evidence.

Future M42 may create a bounded test plan, but it must preserve:

```text
scheduled retest != completed retest
completed retest != successful transfer
successful transfer != mastery
```

## K0–K7 semantic architecture

The ontology provides stable concepts and explanatory semantics while preserving:

```text
concept definition
!= concept assertion
!= participant perception
!= learner inference
```

K0–K7 includes:

- versioned stable concept identities;
- tactical motifs, position features, principles, evaluation factors, plans, and
  pedagogy metadata;
- Lichess compatibility mappings without importing Lichess as universal truth;
- provenance-bound position/move assertions;
- conservative deterministic detectors;
- an opt-in M19 model-context sidecar;
- an M7C-preserving learner semantic projection.

### Product-pulled ontology rule

There is no generic K8 roadmap item merely to make the ontology larger.

```text
consumer needs semantic distinction X
-> verify current ontology cannot safely express X
-> add minimum semantic extension
-> add ontology rejection tests
-> use X in the consumer
-> qualify both together
```

M41 and M44 required no ontology schema/data expansion, demonstrating that K0–K7 is
already a useful stable substrate.

## M36 — current learner-state read model

M36 composes exact current M7/M7C, M9, M10, M11 and optional K7 information into a
participant-scoped content-addressed read model.

It has no mutation authority.

## M39 — exact evidence explanation

M39 binds an exact M36 state to the exact current M7 revision/M7C assessment and
preserves support, contradiction, successful-counterexample, context-exception,
unclear/mixed evidence, source refs, optional K7 concepts, gaps, and bounded conditions
that could alter a future assessment.

It explains existing evidence; it does not recalculate recurrence.

## M40 — transparent next-action proposal

M40 applies a versioned explicit policy over M36/M39 and proposes one action class:

```text
COLLECT_NEW_EVIDENCE
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
TEACH_CONCEPT
ASSIGN_PRACTICE
RUN_NEAR_TRANSFER_TEST
RUN_FAR_TRANSFER_TEST
WAIT_FOR_REAL_GAME_EVIDENCE
```

Its authority is `proposal_only`.

M40 is now the routing seam for downstream product work rather than downstream
features independently inventing their own learner-intelligence policy.

## M43 — contradiction/control evidence acquisition

M43 consumes only the evidence-oriented M40 actions:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

It binds the exact M40 proposal, exact M39 synthesis when required, an explicit pool
of exact-current participant-local M7B evidence links, and a versioned ranking policy.

Output candidate kinds distinguish current M7C classifications from potential new
review material.

Its claim ceiling is:

```text
decision_authority = candidate_only
m7c_effect = not_established
mastery = not_established
```

M43 introduces no persistence/search backend and no second recurrence engine.

## M41 — ontology-aware intervention matching

M41 consumes an exact `TEACH_CONCEPT` proposal and exact M39 concept context. It binds
the exact ontology snapshot, exact M9 intervention registry, explicit semantic-profile
sidecars, and an explicit matching policy.

It returns:

```text
eligible_candidate
possible_candidate
insufficient_information
ineligible
```

Ontology pedagogical prerequisites are carried as **unverified prerequisites**. M41
cannot infer whether the learner has or lacks them.

Its claim ceiling is:

```text
selection_authority = not_exercised
efficacy = not_established
mastery = not_established
```

## M44 — learner progress reference presentation

M44 is split into two implementation modules:

```text
progress_model.py
    exact source validation + deterministic presentation model

progress_render.py
    escaped static HTML rendering from an already-built exact view
```

This physical separation reinforces:

```text
presentation composition != presentation rendering != learner inference
```

M44 requires the exact M39 synthesis set referenced by M40, validates optional M43 and
M41 artifacts against the same participant/revision/plan/proposal identities, resolves
ontology display semantics under the exact ontology fingerprint, and preserves M40
priority order.

Optional missing M43/M41 layers are shown as unavailable/not supplied instead of
negative evidence.

The HTML surface:

- is static and deterministic;
- escapes source-controlled text;
- loads no scripts/network resources;
- is content-addressed;
- claims local reference presentation only.

It does not establish production browser/device/accessibility/usability quality.

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
M41 candidate != M9 applicability mapping
M41 rank != M9 selection
M44 rendering != learner inference
M40 transfer proposal != M10 transfer evidence
successful evidence case != mastery
transparent policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
```

## Current non-goals

The implemented architecture does not establish:

- causal cognitive diagnosis/permanent learner traits;
- complete automatic chess-concept detection;
- automatic learner-state mutation from ontology or model outputs;
- intervention efficacy or optimal pedagogy;
- transfer/mastery from plans or practice alone;
- production UI/accessibility/usability quality;
- hosted auth/multi-tenancy/persistence readiness;
- production privacy/security/compliance posture;
- production provider retry/cost/secrets authority.

## Next product-pulled seams

The strongest next architecture sequence is:

```text
M40 RUN_NEAR_TRANSFER_TEST / RUN_FAR_TRANSFER_TEST
-> M42 bounded transfer/retest plan
-> actual bounded result
-> existing M10 evidence authority

bounded recent participant games
-> M45 mentor queue using objective importance + learner relevance +
   contradiction value + transfer value + uncertainty + novelty

M36/M39/M40 + K0-K7 + M41/M42/M43
-> M46 adaptive Socratic tutoring under explicit pedagogical action boundaries
```

M35/M37 remain available only when concrete operator/consumer needs pull them forward.
M38 must never duplicate M7C recurrence authority.
