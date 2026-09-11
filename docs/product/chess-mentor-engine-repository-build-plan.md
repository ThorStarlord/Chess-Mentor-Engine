# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:**
> [`repository-build-status.md`](repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture:** [`../architecture/architecture.md`](../architecture/architecture.md)

**Status:** planning history plus future candidate roadmap.  
**Authority:** this document does not create an approved queue or production claim.

## 1. Product direction

Chess Mentor Engine should become a persistent chess tutor that learns from a
participant's games and reasoning evidence rather than a generic engine-analysis
wrapper.

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

The repository now has enough qualified infrastructure to make the middle of that
chain inspectable, contradiction-aware, policy-driven, and locally presentable.

## 2. Current implementation state

The contiguous numbered milestone series remains qualified through **M34**.
Additional qualified work includes:

```text
K0-K7  Chess Knowledge Ontology program
M36    Deterministic Learner-State Read Model
M39    Hypothesis Evidence Synthesizer
M40    Teaching-Priority / Next-Session Planner
M43    Contradiction / Control Evidence Acquisition
M41    Ontology-Aware Intervention Matching
M44    Learner Progress Reference Surface
```

M35, M37, M38, and M42 remain unimplemented candidate labels. Later-numbered
qualified packages do not imply those candidates were completed or reserved.

## 3. What changed through M44

The strongest qualified learner-intelligence path is now:

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
        |
        +-- teach concept ------------> M41 intervention candidates
        |
        `------------------------------> M44 learner-progress presentation
```

This is a meaningful transition from evidence storage toward an inspectable tutoring
decision loop.

## 4. Durable authority principles

### Chess truth is not learner psychology

Engine evidence can establish bounded chess facts/evaluations. It cannot by itself
establish what the participant thought or why they made a decision.

### Participant self-report is evidence, not objective truth

Captured reasoning may be incomplete or reconstructed and remains distinct from
engine analysis.

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

K7 adds typed context to already-classified M7C units. It does not decide the relation
between a chess concept and a learner hypothesis.

### Derived learner-intelligence layers remain derived

```text
M36 read model != learner-state mutation
M39 synthesis != M7C assessment
M40 proposal != action execution
M43 candidate != M7C contradiction/refutation
M41 candidate != M9 applicability mapping or selection
M44 presentation != learner inference
```

### Intervention and outcome authorities remain separate

```text
M40 TEACH_CONCEPT != M9 intervention selection
M41 candidate != M9 selection
M40 ASSIGN_PRACTICE != M10 practice evidence
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
scheduled/completed retest != successful transfer
successful transfer != mastery
```

### Transparent policy is not validated pedagogy

M40, M41, and M43 policies are explicit product heuristics. Mechanical qualification
proves determinism and authority preservation, not empirical optimality.

## 5. Product-pulled ontology policy

The Chess Knowledge Ontology is now a shared semantic substrate rather than an
independent expansion program.

**Do not create a generic K8** merely to add more vocabulary, detectors,
relationships, or pedagogy metadata.

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

M41 and M44 both shipped without ontology schema/data changes. That is evidence that
K0–K7 is already sufficiently expressive for meaningful product work.

### Ontology changes that are not product-pulled

Do not prioritize:

- adding every tactical motif because it exists in chess literature;
- adding every strategic principle before a consumer needs it;
- adding heuristic detectors merely to increase coverage percentage;
- adding semantic-distance or similarity frameworks before a concrete consumer
  requires them;
- rewriting M6/M7/M7C around ontology labels;
- automatically wiring K6 into every M19/provider path.

## 6. Implemented M40 consumer seams

### M43 — evidence acquisition

M43 now consumes:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

It may preserve already-classified M7C challenge/control cases for presentation and
rank additional exact-current participant-local M7B links as **potential** evidence
for future review/reassessment.

It does not run M7C or change learner state.

### M41 — intervention matching

M41 now consumes:

```text
TEACH_CONCEPT
```

It uses exact ontology concepts/pedagogy, explicit semantic-profile sidecars, and the
exact M9 intervention registry to return candidate interventions. It deliberately does
not infer semantics from intervention prose and does not create an M9 applicability
mapping or selection decision.

### M44 — learner progress reference surface

M44 presents exact M36/M39/M40 state and optional exact M43/M41 artifacts in a
content-addressed local reference experience. It makes uncertainty and authority
boundaries visible rather than smoothing them into a generic “AI coach” statement.

## 7. Highest-priority next candidate — M42 transfer / retest planning

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`

**Pulled by:** M40 `RUN_NEAR_TRANSFER_TEST` and `RUN_FAR_TRANSFER_TEST`.

### Product question

> Given an exact current learner hypothesis and selected intervention, what bounded
> test should be run next to gather near- or far-transfer evidence?

### Proposed inputs

```text
exact M36 learner state
exact M39 synthesis
exact M40 transfer-test proposal
exact current M9 intervention-selection decision
exact intervention/exercise definitions
current M10 evidence state
optional K0-K7 semantic context
versioned M42 planning policy
```

### Proposed output

```text
m42.transfer-retest-plan.v1
```

Possible fields:

```text
participant_id
hypothesis_revision_ref
intervention_selection_ref
m40_proposal_ref
transfer_kind              near | far
measurement_target
candidate_position_refs[]
exposure_constraints
freshness_constraints
selection_reasons[]
blocking_uncertainty[]
policy_ref
created_at
plan_authority = planning_only
```

### Core rules

- near transfer should test the same underlying skill with controlled surface
  variation rather than merely replaying the exact practice item;
- far transfer should require materially different surface/context features while
  preserving a defensible connection to the target skill;
- previously exposed positions must not silently count as fresh evidence;
- position/test planning remains separate from M10 outcome evidence;
- a scheduled or completed test does not establish transfer;
- no universal optimal retest timing should be claimed without external evidence.

### Ontology use

Use existing concept IDs, relationships, and pedagogy where they help express what is
held stable versus varied across near/far transfer.

Only extend the ontology if M42 produces a concrete semantic need that K0–K7 cannot
represent safely.

### Required rejection cases

At minimum:

- non-transfer M40 action;
- cross-participant source;
- stale hypothesis/intervention identity;
- no selected M9 intervention when required;
- mixed/unclear M9 state;
- exact practice-position replay incorrectly labeled fresh transfer;
- far-transfer candidate that is merely a near duplicate;
- plan treated as M10 success/mastery;
- tampered policy/source fingerprint;
- no eligible test position -> explicit no-plan/gap result.

### Candidate exit criterion

An exact M40 transfer proposal can yield a deterministic provenance-complete near/far
retest plan while actual result/transfer authority remains in M10.

## 8. Next candidate after M42 — M45 batch games -> mentor queue

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`

### Product question

> I played a bounded batch of recent games. Which moments deserve my attention now?

### Why this matters

A persistent tutor should not require the participant to inspect every engine mistake.
M45 should turn recent games into a small review/mentor queue based on learning value.

### Proposed ranking dimensions

Use explicit transparent dimensions such as:

```text
objective chess importance
learner-hypothesis relevance
contradiction / control value
transfer-test value
uncertainty reduction
novelty / independence
semantic diversity
recency where policy says it matters
```

Do not reduce the queue to centipawn-loss sorting.

### Authority boundary

M45 proposes review priority. It does not:

- create an M7 hypothesis from engine loss;
- reclassify M7C;
- claim a concept is a weakness because it appears in a position;
- select an M9 intervention;
- establish transfer/mastery.

### Likely consumers

M45 should reuse:

```text
M3/M4 objective importance
M5/M6 participant reasoning/discrepancy where available
M7/M7C current learner state
K7 semantic context
M39 uncertainty / contradictions
M40 action intent
M43 information-value candidates
M42 transfer needs
```

### Candidate exit criterion

A bounded recent-game batch yields a small deterministic participant-scoped mentor
queue whose ranking is explainable and traceable to qualified source evidence.

## 9. Next candidate after M45 — M46 adaptive Socratic tutor

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION` first; external model usefulness
remains a separate authority gate.

### Product question

> Given what CME currently knows and what action it wants to take, what should the
> tutor ask/reveal next without destroying the measurement opportunity?

### Proposed inputs

```text
exact current learner state (M36)
exact hypothesis evidence (M39)
exact next-action intent (M40)
optional M41 intervention candidate / exact M9 selected intervention
optional M42 retest plan
optional M43 challenge/control candidate
K0-K7 concept definitions + recognition questions
objective chess evidence
participant exposure state
versioned pedagogical-action policy
```

### Bounded pedagogical action vocabulary

A first version should likely distinguish actions such as:

```text
ASK_CANDIDATE_MOVES
ASK_THREATS
ASK_DEFENDER_ROLE
ASK_EVALUATION_FACTORS
ASK_PLAN
GIVE_MINIMAL_HINT
GIVE_CONCEPT_HINT
GIVE_DIRECTIONAL_HINT
REVEAL_TACTICAL_RELATION
REVEAL_ENGINE_LINE
ASK_REFLECTION
```

The exact vocabulary should be designed from existing M8/M16 exposure constraints,
not invented independently.

### Critical pre-reveal invariant

```text
unassisted participant response
!= response after concept hint
!= response after tactical reveal
!= response after engine line
```

M46 must preserve the evidence boundary so tutoring does not contaminate later claims
about what the participant independently recognized.

### Model integration

Use deterministic evidence/context first. Model-authored language remains downstream
of the exact bounded tutoring action and existing M19/M20 authority boundaries.
K6 may become useful here if the consumer demonstrates a real need for ontology-rich
model context.

### Candidate exit criterion

A hermetic tutor session can choose bounded question/hint/reveal actions from exact
learner/tutoring state while preserving exposure measurement and deterministic source
traceability.

## 10. Later candidate — M47 bounded multi-session study plan

After M42/M45/M46, consider composing several M40-style actions into a revisable
short-horizon study plan.

Desired properties:

- bounded horizon;
- explicit current rationale;
- append-preserved revisions;
- contradiction/retest checkpoints;
- no claim that the schedule is empirically optimal;
- no mastery promotion without M10/learner-state evidence.

## 11. Lower-priority candidates still available

### M35 — operator exposure

M32/M33 and newer M36-M44 artifacts may receive CLI/operator exposure when a concrete
consumer requires it. Do not prioritize command count for its own sake.

### M37 — cross-surface consumer regression

A future production frontend may need repository-owned fixture contracts spanning
review and learner-intelligence surfaces. Pull this forward only when compatibility is
the active blocker.

### M38 — recurrence candidate mining

Do **not** implement M38 as a second recurrence engine. If the label is ever reused,
it should mean M7C-aware grouping/candidate discovery that proposes material for M7C
or human review while preserving existing recurrence authority.

## 12. Signature product opportunity

The strongest differentiating experience remains explainable learner beliefs:

```text
WHY DO YOU BELIEVE THIS ABOUT ME?
M36 current state
-> M39 exact evidence synthesis
-> M7C support / contradiction / counterexamples
-> K7 chess concepts
-> participant reasoning
-> objective source positions
```

and:

```text
WHAT WOULD CHANGE YOUR MIND?
M39 gaps/change conditions
-> M40 challenge/control proposal
-> M43 evidence acquisition
```

and now:

```text
WHAT SHOULD I DO NEXT?
M40 teaching proposal
-> M41 candidate interventions
-> M9 explicit applicability/selection
-> future M42 retest planning
```

M44 is the first coherent local surface capable of presenting these layers together.

## 13. Productization to defer

Do not prioritize these ahead of a compelling closed local tutoring loop unless a
concrete requirement changes the order:

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

Production frontend, provider, privacy/security, authentication, hosted persistence,
retry/idempotency, and empirical tutoring-effectiveness claims remain external/human
authority boundaries.

## 14. Phase-gate discipline

Before every future package:

1. reconcile live `main`;
2. identify the concrete product/correctness problem;
3. identify the existing authority owner;
4. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or
   `EXTERNAL_AUTHORITY`;
5. define exact inputs, outputs, claim ceiling, and forbidden authority changes;
6. ask whether K0–K7 already expresses the semantic need before changing ontology;
7. implement the smallest bounded consumer contract;
8. include negative/near-miss/tamper tests;
9. run full pytest, Ruff, compileall, and independent Stockfish on the exact PR head;
10. merge only that qualified exact head;
11. reconcile documentation after the feature queue closes.

## 15. Recommended next queue

Subject to a fresh live-main audit, the strongest next milestone is:

```text
[ ] M42 — Transfer / Retest Planning
    REPOSITORY_ONLY / HERMETIC_VALIDATION

[ ] M45 — Batch Games -> Mentor Queue
    REPOSITORY_ONLY / HERMETIC_VALIDATION

[ ] M46 — Adaptive Socratic Tutor
    REPOSITORY_ONLY / HERMETIC_VALIDATION first
```

The guiding development rule is:

> **Build the mentor. Extend the ontology only when the mentor proves an extension is needed.**
