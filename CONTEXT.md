# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Latest runbook:**
> [`docs/runbooks/m41-m44-tutor-decision-loop.md`](docs/runbooks/m41-m44-tutor-decision-loop.md)

## Product and authority

Chess Mentor Engine converts objective chess evidence into participant-specific
learning support while keeping different kinds of truth in different authority
layers.

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
How may M44 present all of that without inventing new claims?
```

## Current implementation boundary

The contiguous milestone sequence remains qualified through **M34**. Additional
qualified work includes:

- Chess Knowledge Ontology **K0–K7**;
- **M36** deterministic learner-state read model;
- **M39** hypothesis evidence synthesis;
- **M40** teaching-priority / next-session proposal;
- **M43** contradiction/control evidence acquisition;
- **M41** ontology-aware intervention matching;
- **M44** learner-progress local reference surface.

M35, M37, M38, and M42 remain unimplemented labels. Later-numbered qualified work
does not imply those milestones exist.

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
          +-----------+-----------+
          |                       |
          v                       v
   M43 EVIDENCE              M41 TRAINING
   CANDIDATES                CANDIDATES
          |                       |
          +-----------+-----------+
                      |
                      v
                M44 REFERENCE VIEW
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

A tactic such as `tactic.fork` may be mechanically present while the participant
understood it perfectly. A learner discrepancy may also concern search process rather
than the surface motif.

K7 attaches typed chess context to already-classified M7C recurrence units and
preserves M7C relations verbatim. It does not become recurrence authority.

### Product-pulled ontology rule

The ontology is now a shared dependency, not a destination. Do not create a generic
K8 merely to increase vocabulary, relationships, detectors, or pedagogy metadata.

Use this sequence:

```text
consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> design the minimum ontology extension
-> add rejection tests
-> consume X in the requesting feature
-> qualify ontology + consumer together
```

M41 and M44 both shipped without ontology schema/data changes. That is desirable: a
mature substrate should often support product work without changing itself.

## M36 / M39 / M40 mental model

M36 answers:

> What does current qualified repository evidence say about this participant now?

M39 answers:

> Why is this current learner hypothesis at its current M7C status, what challenges
> it, and what evidence remains missing?

M40 asks:

> Which *kind* of learner-facing action should be proposed next under an explicit
> versioned policy?

Its action vocabulary is:

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

M36 is read-only, M39 does not recalculate recurrence, and M40 is proposal-only.

## M43 mental model

M43 is a consumer of M40 evidence-oriented actions:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

It may:

- preserve already-classified M7C contradiction/counterexample/context-exception
  material for presentation;
- inspect an explicitly supplied participant-local M7B candidate pool;
- rank additional links as **potential** contradiction/counterexample/context/
  evidence candidates;
- prefer independent/new contexts under a transparent policy;
- expose explicit gaps when nothing eligible is available.

It may not convert a candidate into a new M7C relation.

```text
M43 candidate != M7C contradiction
successful case != mastery
ranked first != objectively best evidence
```

## M41 mental model

M41 consumes an exact M40 `TEACH_CONCEPT` proposal and exact M39 concept context.
It uses:

- the exact K0–K7 ontology snapshot;
- the exact M9 intervention registry;
- explicit content-addressed semantic profiles for intervention versions;
- a transparent matching policy.

A semantic profile may state target/reinforced/contraindicated concepts and training
modes. M41 deliberately does **not** parse M9 training prose to manufacture semantic
mappings.

Candidate states are:

```text
eligible_candidate
possible_candidate
insufficient_information
ineligible
```

Multiple eligible candidates remain multiple candidates.

```text
M41 candidate != M9 applicability mapping
M41 rank != M9 selection
pedagogy prerequisite != learner deficiency/mastery
```

## M44 mental model

M44 is presentation, not inference.

It composes exact M36/M39/M40 state and optional exact M43/M41 artifacts into:

```text
m44.learner-progress-view.v1
-> m44.learner-progress-reference-surface.v1
```

The view may expose:

- M40 priority order;
- current hypothesis/status and source evidence;
- support, contradiction, counterexamples, context exceptions;
- ontology concept names and instructional recognition questions;
- M9/M10 training and transfer state;
- M39 evidence gaps and change conditions;
- M43 evidence candidates;
- M41 intervention candidates;
- M40 next-action reasons and blocking uncertainty.

Missing optional M43/M41 information is rendered as unavailable/not supplied, not as
negative evidence.

The HTML renderer is static and escaped, validates the exact view first, and creates
no learner or execution authority. It is a **local reference surface**, not a
production browser/accessibility/usability claim.

## Authority owners contributors must preserve

### Objective chess

`chess/`, M3/M4, and M15 own canonical board state, legal actions, deterministic
features, engine evidence, score/bound/mate semantics, and objective selection
contracts. They do not own learner psychology.

### Participant evidence

M5/M8 capture and freeze participant-reported reasoning under explicit exposure
boundaries. Participant self-report is evidence, not chess truth.

### Learning inference

M6 remains position-local. M7/M7C own participant-specific hypothesis lifecycle,
recurrence status, support/challenge/contradiction evidence, and review policy.

### Training and outcomes

M9 owns explicit intervention applicability/selection. M10 owns bounded
outcome/transfer evidence. M11 derives append-only longitudinal learner state.

### Chess semantics

K0–K7 own ontology identities, semantics, provenance-bound assertions, conservative
detector outputs, and qualified sidecar/projection contracts. They do not own M7C,
M9, or learner-state mutation.

### Learner intelligence and candidate preparation

M36 reads current state. M39 explains current evidence. M40 proposes an action. M43
prepares evidence candidates. M41 prepares intervention candidates. M44 presents those
qualified layers. None silently inherits upstream mutation/selection/execution
authority.

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
M44 rendering != learner inference
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
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
2. identify the existing authority owner before adding a subsystem;
3. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or
   `EXTERNAL_AUTHORITY`;
4. define explicit inputs/outputs, claim ceiling, and forbidden authority changes;
5. implement the smallest bounded contract;
6. include positive and rejection/near-miss cases;
7. merge only the exact final head that passes full pytest, Ruff, compileall, and the
   independent Stockfish job;
8. reconcile current documentation after feature packages merge.

## Likely next architecture work

The next product-pulled sequence is now:

```text
M40 RUN_NEAR_TRANSFER_TEST / RUN_FAR_TRANSFER_TEST
    -> M42 bounded transfer/retest planning

bounded recent participant games
    -> M45 mentor queue using learner relevance, contradiction value,
       transfer value, uncertainty, novelty, and objective importance

M36/M39/M40 + K0-K7 + later M41/M42/M43 context
    -> M46 adaptive Socratic tutor
```

M35/M37 should move only if a concrete consumer/operator blocker requires them. M38
must not become a second recurrence engine; reuse M7C.
