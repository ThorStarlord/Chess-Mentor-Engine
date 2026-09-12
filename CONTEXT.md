# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Latest runbook:** [`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)

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
How may the V1 local consumer compose those exact artifacts without acquiring their authority?
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
M44    Learner Progress Reference Surface
M45    Participant-Scoped Batch Mentor Queue
M46    Adaptive Socratic Tutor Action Policy
V1     Local Tutor Composition (`cme-local-tutor`)
```

M35, M37, and M38 remain unimplemented labels. K8 is not an active program. The remaining repository blocker for Version 1.0 is release/distribution qualification, not another learner-intelligence layer.

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
M6 -> M7 / M7C
        |
        +------------------------------+
        |                              |
        v                              v
TRAINING / OUTCOMES                CHESS SEMANTICS
M9 intervention selection          K0-K7 ontology/assertions/detectors
M10 bounded outcome evidence       + optional M7C-preserving projection
M11 longitudinal learner state
        |                              |
        +---------------+--------------+
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
          |             |             |
          v             v             v
    M43 EVIDENCE   M41 TRAINING   M42 TRANSFER
     CANDIDATES     CANDIDATES      PLAN
          |             |             |
          +-------------+-------------+
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
             M23 -> persisted M8 checkpoint
                        |
                        v
                 M46 ACTION PROPOSAL
                        |
                        v
       existing M8 EXECUTION / EXPOSURE commands
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

K0-K7 own ontology identities, semantics, provenance-bound assertions, conservative detector outputs, and qualified sidecar/projection contracts. They do not own M7C, M9, or learner-state mutation.

### Learner intelligence and tutor proposals

M36 reads current state. M39 explains evidence. M40 proposes an action. M43 prepares evidence candidates. M41 prepares intervention candidates. M42 prepares transfer/retest plans. M44 presents qualified layers. M45 ranks bounded review candidates. M46 proposes bounded tutor actions. None inherits upstream mutation/selection/outcome/execution authority.

### V1 local composition

`cme-local-tutor` is composition-only. It validates and combines exact already-qualified artifacts, uses M45 rank one only as a review proposal, requires explicit selection and capture consent, persists through the existing M23/M8 path, and surfaces an M46 proposal. It does not execute the M46 action or mint new chess/learner/outcome authority.

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
V1 composition != new learner / selection / outcome authority
M45 rank one != implicit consent
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

For any package:

1. reconcile live `main`;
2. identify the concrete product/correctness problem and existing authority owner;
3. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
4. define exact inputs/outputs, claim ceiling, and forbidden authority changes;
5. reuse existing authority systems before adding a subsystem;
6. include positive and rejection/near-miss/tamper cases;
7. merge only the exact final head that passes full pytest, Ruff, compileall, and the independent Stockfish job;
8. reconcile current documentation after feature packages merge.

## Current Version 1.0 decision

The local composition gap is closed by PR #94. The next required V1 package is **Release Candidate & Distribution Qualification**:

```text
current package identity/version
-> build wheel/sdist
-> clean fresh-environment install
-> smoke promised commands and package data
-> preserve full pytest/Ruff/compileall/Stockfish gate
-> repository-qualified V1 candidate
```

Do not substitute M35/M37/M38/K8/M47 or hosted-product work for this release task. Those are optional/conditional or external-authority work after the repository V1 boundary is qualified.
