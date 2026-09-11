# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Latest runbook:**
> [`docs/runbooks/m42-m46-learner-tutor-loop.md`](docs/runbooks/m42-m46-learner-tutor-loop.md)

## Product and authority

Chess Mentor Engine converts objective chess evidence into participant-specific learning support while keeping different kinds of truth in different authority layers.

Keep these questions separate:

```text
What is objectively happening on the board?
What did the participant report noticing, considering, and expecting?
What position-local discrepancy is supported?
What participant-specific recurrence/hypothesis does M7C currently support or reject?
What intervention has M9 actually selected?
What bounded practice/transfer evidence does M10 record?
What does M11 currently project longitudinally?
What chess concepts are present under K0-K7 authority?
What can M36/M39 derive without changing those sources?
What action may M40 propose without executing it?
Which evidence may M43 suggest inspecting without reclassifying M7C?
Which interventions may M41 suggest without exercising M9 selection?
What transfer/retest may M42 plan without creating an M10 outcome?
How may M44 present all of that without inventing new claims?
Which recent review moments may M45 prioritize without diagnosing the learner?
What may M46 ask/hint/reveal next without bypassing the M8 exposure lifecycle?
```

## Current implementation boundary

The contiguous milestone sequence remains qualified through **M34**. Additional qualified work includes:

```text
K0-K7  Chess Knowledge Ontology
M36    Deterministic Learner-State Read Model
M39    Hypothesis Evidence Synthesis
M40    Teaching-Priority / Next-Session Proposal
M43    Contradiction / Control Evidence Acquisition
M41    Ontology-Aware Intervention Matching
M42    Bounded Transfer / Retest Planning
M44    Learner Progress Reference Surface + Transfer Plan Presentation
M45    Participant-Scoped Batch Mentor Queue
M46    Adaptive Socratic Tutor Action Policy
```

M35, M37, and M38 remain unimplemented labels. K8 is not an active program.

## Current authority graph

```text
OBJECTIVE CHESS
M1-M4 / M14-M18
canonical position, deterministic features, engine evidence, selection
        |
        v
PARTICIPANT EVIDENCE
M5 / M8 / M21 / M23
captured reasoning and exposure/consent boundaries
        |
        v
LEARNER INFERENCE
M6 position-local discrepancy
        |
        v
M7 / M7C participant-specific hypothesis, recurrence, contradiction
        |
        +------------------------------+
        |                              |
        v                              v
TRAINING / OUTCOMES                CHESS SEMANTICS
M9 intervention selection          K0-K7 ontology/assertions/detectors
M10 bounded outcome evidence       + optional M7C-preserving projection
M11 longitudinal learner state     |
        |                           |
        +-------------+-------------+
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
          +-----------+------------+-------------+
          |                        |             |
          v                        v             v
   M43 EVIDENCE              M41 TRAINING    M42 TRANSFER
   CANDIDATES                CANDIDATES      PLAN
          |                        |             |
          +-----------+------------+-------------+
                      |
                      v
                M44 REFERENCE VIEW

M4D DIAGNOSTIC BATCH + PARTICIPANT SCOPE
                      |
                      v
                M45 MENTOR QUEUE
                      |
                      v
                M8 TUTOR LIFECYCLE
            + optional M44/M45/M42 context
                      |
                      v
                M46 ACTION PROPOSAL
                      |
                      v
                M8 EXECUTION / EXPOSURE
```

Separately, the deterministic feedback/model/review path remains:

```text
M15 presentation + M6/M7
-> M16 deterministic mentor grounding
-> optional M19 model request/prose
-> optional M20 evaluator judgment
-> M24 execution seam
-> M25-M30 review/persistence/navigation
-> M32 consumer fidelity
-> M33 deterministic trace
-> optional M31/M34 safety/recovery surfaces
```

The learner-intelligence path does not silently rewrite that model/review chain.

## Chess Knowledge Ontology mental model

K0–K7 provides stable chess semantics, not learner psychology.

```text
concept definition
!= position/move assertion
!= participant perception
!= learner hypothesis
```

K7 attaches typed chess context to already-classified M7C recurrence units and preserves M7C relations verbatim. It does not become recurrence authority.

### Product-pulled ontology rule

The ontology is a shared dependency, not a destination. M41/M42/M44/M45/M46 all qualified without a generic K8.

```text
consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> design the minimum ontology extension
-> add rejection tests
-> consume X in the requesting feature
-> qualify ontology + consumer together
```

## Learner-intelligence mental model

### M36

> What does current qualified repository evidence say about this participant now?

Read-only. No learner-state mutation.

### M39

> Why is this learner hypothesis at its current M7C status, what challenges it, and what evidence remains missing?

Source-traceable synthesis. No recurrence reclassification.

### M40

> Which kind of learner-facing action should be proposed next under an explicit versioned policy?

Proposal-only. It does not execute the action.

### M43

> Which already-classified or potential participant-local evidence should be inspected to challenge, control, or extend current evidence?

Candidate-only. It does not turn a candidate into an M7C relation.

### M41

> Which explicit M9 intervention versions are semantic candidates for the current M40 teaching need?

Candidate-only. M9 remains applicability/selection authority.

### M42

> Which bounded near/far transfer position should be used to gather future evidence?

Planning-only. M10 remains attempt/observation/outcome/transfer authority. Exact practice reuse and stale/exposed candidates fail closed.

### M44

> How can current learner evidence, uncertainty, next action, candidates, and transfer plan be presented without adding inference?

Local reference presentation only. Missing optional information remains missing rather than becoming negative evidence.

### M45

> Which bounded recent diagnostic moments deserve review attention given current learner context?

Review-priority proposal only. Ranking uses transparent dimensions rather than raw CP loss alone and does not create a learner diagnosis.

### M46

> Given exact M8 session state and exact learner context, what bounded tutoring action should be proposed next without destroying the measurement opportunity?

M46 preserves this invariant:

```text
unassisted pre-reveal response
!= assisted response after a hint
!= post-reveal reflection
```

Before the M8 baseline is frozen, M46 can only propose continuing baseline capture. After freeze it may propose bounded hints or objective reveal according to exact learner intent; transfer tutoring requires an exact M42 plan. M8 remains execution/exposure/capture/reveal authority.

Every M46 proposal records:

```text
execution_authority = proposal_only
model_language = not_generated
mastery = not_established
```

## Authority owners contributors must preserve

### Objective chess

`chess/`, M3/M4, and M15 own canonical board state, legal actions, deterministic features, engine evidence, score/bound/mate semantics, and objective selection contracts. They do not own learner psychology.

### Participant evidence

M5/M8 capture and freeze participant-reported reasoning under explicit exposure boundaries. Participant self-report is evidence, not chess truth.

### Learning inference

M6 remains position-local. M7/M7C own participant-specific hypothesis lifecycle, recurrence status, support/challenge/contradiction evidence, and review policy.

### Training and outcomes

M9 owns explicit intervention applicability/selection. M10 owns bounded outcome/transfer evidence. M11 derives append-only longitudinal learner state.

### Chess semantics

K0–K7 own ontology identities, semantics, provenance-bound assertions, conservative detector outputs, and qualified sidecar/projection contracts. They do not own M7C, M9, or learner-state mutation.

### Learner intelligence and tutor proposals

M36 reads current state. M39 explains evidence. M40 proposes an action. M43 prepares evidence candidates. M41 prepares intervention candidates. M42 prepares transfer/retest plans. M44 presents qualified layers. M45 ranks bounded review candidates. M46 proposes bounded tutor actions. None inherits upstream mutation/selection/outcome/execution authority.

## Contracts to preserve

```text
objective chess truth != participant evidence != learner inference
one M6 discrepancy != recurrence != causal trait
concept occurrence != participant perception or learner weakness
K7 semantic coverage missing != concept absent
K7 projection != M7C recurrence authority
M36 read model != learner-state mutation
M39 evidence synthesis != M7C assessment
M40 action proposal != action execution
M43 candidate != M7C contradiction/refutation
M41 candidate != M9 applicability mapping or selection
M42 plan != M10 outcome evidence
M44 rendering != learner inference
M45 queue priority != learner diagnosis or M9 selection
M46 tutor proposal != M8 execution / exposure authority
assisted follow-up != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
M9 selected intervention != effective intervention
practice completion != transfer
transparent policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Qualification discipline

For any future package:

1. reconcile live `main`;
2. identify the concrete product/correctness problem and existing authority owner;
3. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
4. define exact inputs/outputs, claim ceiling, and forbidden authority changes;
5. reuse existing authority systems before adding a new subsystem;
6. include positive and rejection/near-miss/tamper cases;
7. merge only the exact final head that passes full pytest, Ruff, compileall, and the independent Stockfish job;
8. reconcile current documentation after feature packages merge.

## Next architecture decision

The M42/M45/M46 backend sequence is complete. The next milestone should be pulled by the product, not milestone numbering.

Strongest alternatives:

```text
A. concrete end-to-end local consumer
   recent games -> M45 queue -> M8/M46 tutoring -> reflection -> M42/M10 retest

B. M47 bounded multi-session study plan
   only if composition across several sessions is the current product bottleneck
```

Prefer the local end-to-end consumer when the current issue is that the qualified backend is difficult to experience as one workflow. Choose M47 only when multi-session orchestration is demonstrably the missing capability.

M35/M37 should move only if a concrete consumer/operator blocker requires them. M38 must not become a second recurrence engine; reuse M7C. K8 remains product-pulled.
