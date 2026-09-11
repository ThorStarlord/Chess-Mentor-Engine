# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:**
> [`repository-build-status.md`](repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture:** [`../architecture/architecture.md`](../architecture/architecture.md)  
> **Latest restart runbook:** [`../runbooks/m42-m46-learner-tutor-loop.md`](../runbooks/m42-m46-learner-tutor-loop.md)

**Status:** planning history plus future candidate roadmap.  
**Authority:** this document does not create an approved queue or production claim.

## 1. Product direction

Chess Mentor Engine should become a persistent chess tutor that learns from a participant's games and reasoning evidence rather than a generic engine-analysis wrapper.

The durable learning chain is:

```text
objective chess evidence
-> participant decision evidence
-> position-local reasoning discrepancy
-> contradiction-tested learner hypothesis
-> explicit teaching decision
-> bounded intervention/practice
-> near/far/real-game transfer evidence
-> revised longitudinal learner state
```

The repository now has enough qualified backend structure to make this loop inspectable, contradiction-aware, policy-driven, locally presentable, review-prioritized, transfer-aware, and capable of proposing bounded tutoring actions while preserving measurement boundaries.

## 2. Current implementation state

The contiguous numbered milestone series remains qualified through **M34**. Additional qualified work includes:

```text
K0-K7  Chess Knowledge Ontology program
M36    Deterministic Learner-State Read Model
M39    Hypothesis Evidence Synthesizer
M40    Teaching-Priority / Next-Session Planner
M43    Contradiction / Control Evidence Acquisition
M41    Ontology-Aware Intervention Matching
M42    Bounded Transfer / Retest Planning
M44    Learner Progress Reference Surface + Transfer Plan Presentation
M45    Participant-Scoped Batch Mentor Queue
M46    Adaptive Socratic Tutor Action Policy
```

M35, M37, and M38 remain unimplemented candidate labels. Later-numbered qualified packages do not imply those candidates are completed or reserved. K8 is not an active ontology program.

## 3. What changed through M46

The strongest qualified learner/tutor path is now:

```text
M7/M7C participant-specific learner hypothesis authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal learner state
+ optional K7 chess semantic context
        |
        v
M36
"What does current qualified evidence say about this participant?"
        |
        v
M39
"Why is this hypothesis at its current status, what challenges it,
 and what evidence is missing?"
        |
        v
M40
"What kind of learning action should be proposed next?"
        |
        +-- challenge/control/collect --> M43 evidence candidates
        +-- teach concept ------------> M41 intervention candidates
        +-- near/far transfer --------> M42 transfer/retest plan
        `------------------------------> M44 learner-progress presentation

M4D bounded diagnostic batch + explicit participant scope
        |
        v
M45
"Which moments deserve attention now?"
        |
        v
M8 controlled tutor lifecycle + optional M44/M45/M42 context
        |
        v
M46
"What bounded question, hint, reveal, or reflection should happen next?"
        |
        v
M8 remains actual execution / exposure / capture / reveal authority
```

This is a meaningful transition from evidence storage toward an inspectable and mechanically coherent tutoring loop.

## 4. Durable authority principles

### Chess truth is not learner psychology

Engine evidence can establish bounded chess facts/evaluations. It cannot by itself establish what the participant thought or why they made a decision.

### Participant self-report is evidence, not objective truth

Captured reasoning may be incomplete or reconstructed and remains distinct from engine analysis.

### Local discrepancy is not recurrence

```text
one M6 discrepancy
!= M7C recurrence
!= causal learner trait
```

M7C remains the participant-specific recurrence/contradiction authority.

### Ontology semantics do not create learner authority

```text
concept definition
!= concept assertion
!= participant perception
!= learner inference
```

K7 adds typed context to already-classified M7C units. It does not decide the relation between a chess concept and a learner hypothesis.

### Derived learner-intelligence layers remain derived

```text
M36 read model != learner-state mutation
M39 synthesis != M7C assessment
M40 proposal != action execution
M43 candidate != M7C contradiction/refutation
M41 candidate != M9 applicability mapping or selection
M42 plan != M10 outcome evidence
M44 presentation != learner inference
M45 mentor priority != learner diagnosis or M9 selection
M46 tutor proposal != M8 tutoring execution / exposure authority
```

### Measurement must survive tutoring

```text
unassisted pre-reveal response
!= assisted response after a hint
!= post-reveal reflection
```

M46 must never erase these distinctions. M8 remains the source of truth for capture/exposure transitions.

### Intervention and outcome authorities remain separate

```text
M40 TEACH_CONCEPT != M9 intervention selection
M41 candidate != M9 selection
M40 ASSIGN_PRACTICE != M10 practice evidence
M42 transfer plan != M10 transfer evidence
scheduled/completed retest != successful transfer
successful transfer != mastery
```

### Transparent policy is not validated pedagogy

M40–M46 policies are explicit product heuristics. Mechanical qualification proves determinism and authority preservation, not empirical optimality.

## 5. Product-pulled ontology policy

The Chess Knowledge Ontology is a shared semantic substrate rather than an independent expansion program.

**Do not create a generic K8** merely to add more vocabulary, detectors, relationships, or pedagogy metadata.

Use this sequence instead:

```text
consumer feature needs semantic distinction X
-> verify K0-K7 cannot represent X safely
-> write the concrete failing consumer case
-> design the minimum ontology extension
-> add ontology validation/rejection tests
-> consume the extension in the requesting feature
-> qualify ontology + consumer together
```

M41, M42, M44, M45, and M46 all shipped without a generic ontology expansion. That is evidence that K0–K7 is already sufficiently expressive for meaningful product work.

Do not prioritize ontology coverage percentage, generic semantic-distance frameworks, automatic K6 wiring, or rewriting M6/M7/M7C around ontology labels without a concrete consumer need.

## 6. Implemented M40 consumer seams

### M43 — evidence acquisition

Consumes `CHALLENGE_HYPOTHESIS`, `PRESENT_CONTROL`, and `COLLECT_NEW_EVIDENCE` and returns already-classified or potential evidence candidates without re-running M7C.

### M41 — intervention matching

Consumes `TEACH_CONCEPT` and returns exact M9 intervention-version candidates using explicit ontology semantic profiles without exercising M9 selection authority.

### M42 — transfer/retest planning

Consumes `RUN_NEAR_TRANSFER_TEST` / `RUN_FAR_TRANSFER_TEST` and creates a bounded provenance-complete plan. Exact practice reuse, stale selection identity, exposure/freshness violations, and near/far mismatches fail closed. Actual transfer remains M10 authority.

### M44 — learner progress reference surface

Presents exact M36/M39/M40 plus optional M43/M41 and additive M42 transfer-plan context. It is local reference presentation only.

### M45 — participant-scoped mentor queue

Binds a participant-agnostic M4D batch to explicit participant-local provenance and ranks a bounded queue using transparent learner/challenge/transfer/uncertainty/objective/novelty/semantic-diversity dimensions. It does not create learner claims from engine loss.

### M46 — adaptive Socratic tutor action proposal

Consumes exact M8 session state plus exact learner context and proposes one bounded tutoring action. Before M8 baseline freeze it can only continue baseline capture. After freeze it may propose hints or reveal under explicit policy. Transfer tutoring requires an exact M42 plan. Post-reveal responses are reflection, never reclassified as baseline evidence.

## 7. Current product bottleneck question

The previous roadmap sequence:

```text
M42 -> M45 -> M46
```

is complete.

The next milestone should therefore begin with a **fresh product audit**, not automatic continuation to the next number.

The core question is now:

> Is the repository's biggest remaining gap another backend planning abstraction, or is it that the already-qualified learner/tutor loop is not yet easy to experience as one coherent local product workflow?

Default bias: prefer exposing and exercising existing qualified capability before adding another backend authority-neutral layer.

## 8. Leading direction A — concrete end-to-end local consumer

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION` first.

**Preferred default when:** the product is difficult to exercise end to end despite strong backend contracts.

### Product question

> Can a local user move from recent games to a prioritized learning moment, complete a measurement-safe tutoring interaction, understand why it was selected, and reach a clearly planned retest without manually stitching Python APIs together?

### Target flow

```text
bounded recent games
-> M4D diagnostic candidates
-> explicit participant scope
-> M45 mentor queue
-> select one review moment
-> M8 clean pre-reveal capture
-> M46 bounded next tutor action
-> objective reveal / reflection under M8 authority
-> M36/M39/M40/M44 explanation context
-> M42 transfer/retest plan when warranted
-> later M10 outcome evidence
```

### Candidate implementation shapes

Fresh audit should choose the smallest concrete consumer, for example:

- one local CLI workflow or command group;
- one deterministic local reference application/page;
- one fixture-backed demo runner that produces a complete review package;
- one application service that composes existing contracts without becoming a new inference authority.

Do not build all of these at once.

### Required properties

- no duplicate learner model;
- no bypass of M8 pre-reveal capture;
- no hidden M9 intervention selection;
- no M42 plan treated as M10 success;
- explicit source IDs/fingerprints at orchestration boundaries;
- actionable failure messages for missing/stale artifacts;
- deterministic hermetic fixture path;
- one clear “first value” experience.

### Candidate exit criterion

A fresh local environment can exercise one coherent participant flow from bounded game evidence to mentor queue to controlled tutoring and, when appropriate, a transfer plan without manual artifact surgery or authority drift.

## 9. Leading direction B — M47 bounded multi-session study plan

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`.

**Promote only when:** the actual product bottleneck is composition of several already-qualified actions across sessions.

### Product question

> Given current learner evidence and explicit action candidates, what short revisable sequence of evidence collection, teaching, practice, and retest should be proposed across several sessions?

### Desired properties

```text
bounded horizon
explicit current rationale per step
exact source/action/intervention/transfer refs
append-preserved plan revisions
contradiction/evidence checkpoints
transfer/retest checkpoints
clear completion vs evidence distinction
no empirical optimality claim
no automatic mastery promotion
```

### Non-goals

- long-horizon curriculum generation detached from current evidence;
- automatic M7/M11 mutation;
- automatic M9 intervention selection unless existing M9 authority is explicitly exercised;
- converting scheduled retests into transfer evidence;
- generic calendar/productivity infrastructure;
- claiming the plan is optimal or effective.

### Candidate exit criterion

Several already-qualified M40/M41/M42 actions can be composed into a bounded, content-addressed, revisable study-plan proposal without creating new learner, selection, outcome, or mastery authority.

## 10. Lower-priority candidates still available

### M35 — operator exposure

Newer learner-intelligence artifacts may receive CLI/operator exposure when a concrete consumer requires it. Do not prioritize command count for its own sake. Direction A may satisfy the real need without reviving M35 as a generic infrastructure project.

### M37 — cross-surface consumer regression

A future production frontend may need repository-owned fixture contracts spanning review and learner-intelligence surfaces. Pull this forward only when compatibility is the active blocker.

### M38 — recurrence candidate mining

Do **not** implement M38 as a second recurrence engine. If the label is ever reused, it should mean M7C-aware grouping/candidate discovery that proposes material for M7C or human review while preserving existing recurrence authority.

## 11. Signature product opportunities now available

### Why do you believe this about me?

```text
M36 current state
-> M39 exact evidence synthesis
-> M7C support / contradiction / counterexamples
-> K7 chess concepts
-> participant reasoning
-> objective source positions
```

### What would change your mind?

```text
M39 gaps/change conditions
-> M40 challenge/control proposal
-> M43 evidence acquisition
```

### What should I do next?

```text
M40 teaching proposal
-> M41 intervention candidates
-> M9 explicit selection
-> M42 retest planning after practice when warranted
```

### Which moments should we review?

```text
bounded diagnostic batch
-> M45 participant scope + learner-aware review priority
```

### What should the tutor do now?

```text
M8 exposure state
+ M44 learner context
+ optional M45 queue item / M42 transfer plan
-> M46 action proposal
-> M8 actual transition
```

These questions are more product-differentiating than simply adding more engine annotations.

## 12. Productization to defer

Do not prioritize these ahead of a compelling closed local tutoring experience unless a concrete requirement changes the order:

- cloud deployment for its own sake;
- multi-tenancy before a real multi-user requirement;
- payments/subscriptions;
- social/community features;
- mobile apps;
- broad opening databases;
- generic puzzle platform;
- rating prediction;
- gamification;
- generic provider abstraction unrelated to a current provider need;
- production UI polish before the local tutoring loop is functionally coherent.

Production frontend, provider, privacy/security, authentication, hosted persistence, retry/idempotency, and empirical tutoring-effectiveness claims remain external/human authority boundaries.

## 13. Phase-gate discipline

Before every future package:

1. reconcile live `main`;
2. identify the concrete product/correctness problem;
3. identify the existing authority owner;
4. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
5. define exact inputs, outputs, claim ceiling, and forbidden authority changes;
6. ask whether existing M7C/M8/M9/M10/K0-K7 contracts already solve the authority problem;
7. ask whether the need is a consumer/orchestration gap rather than another backend abstraction;
8. implement the smallest bounded contract;
9. include negative/near-miss/tamper tests;
10. run full pytest, Ruff, compileall, and independent Stockfish on the exact PR head;
11. merge only that qualified exact head;
12. reconcile documentation after the feature queue closes.

## 14. Recommended next decision

Subject to a fresh live-main audit:

```text
FIRST: determine whether the active bottleneck is product consumption or
       multi-session composition.

Preferred default:
[ ] Concrete end-to-end local consumer
    REPOSITORY_ONLY / HERMETIC_VALIDATION

Conditional alternative:
[ ] M47 — Bounded Multi-Session Study Plan
    only if multi-session action composition is the demonstrated bottleneck
```

The guiding development rule is:

> **Use the learner/tutor loop we have built. Add new backend structure only when a concrete product need proves it is missing.**
