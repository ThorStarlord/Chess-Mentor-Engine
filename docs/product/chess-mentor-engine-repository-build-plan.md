# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:** [`repository-build-status.md`](repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture:** [`../architecture/architecture.md`](../architecture/architecture.md)  
> **Latest local-consumer runbook:** [`../runbooks/v1-local-tutor-vertical-slice.md`](../runbooks/v1-local-tutor-vertical-slice.md)

**Status:** planning history plus bounded Version 1.0 queue.  
**Authority:** this document does not create production/empirical claims.

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

## 2. Current implementation state

The contiguous numbered milestone series is qualified through **M34**. Additional qualified work includes K0-K7 and M36/M39/M40/M41/M42/M43/M44/M45/M46.

The previously identified V1 product-consumption gap is now addressed by the integrated local tutor vertical slice:

```text
exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 plan(s)
-> cme-local-tutor
-> M45 mentor queue
-> explicit selection + capture consent
-> M23 -> persisted M8 checkpoint
-> M46 bounded proposal
-> existing cme tutor commands for actual M8 execution/exposure
```

The local layer is composition-only and adds no learner, selection, outcome, or mastery authority.

## 3. Durable authority principles

```text
chess truth != participant self-report != learner inference
one M6 discrepancy != M7C recurrence != causal trait
concept definition/assertion != participant perception != learner weakness
M36/M39 derived state != learner-state mutation
M40 proposal != execution
M43 candidate != M7C relation
M41 candidate != M9 selection
M42 plan != M10 outcome evidence
M44 presentation != learner inference
M45 priority != learner diagnosis / M9 selection
M46 proposal != M8 execution / exposure
V1 composition != upstream authority
M45 rank one != implicit consent
unassisted baseline != assisted response != post-reveal reflection
successful evidence case != mastery
transparent policy != empirically optimal pedagogy
```

## 4. Product-pulled ontology policy

The Chess Knowledge Ontology is a shared semantic substrate rather than an independent expansion program. Do not create a generic K8 merely to add vocabulary, detectors, relationships, or pedagogy metadata.

Use this sequence instead:

```text
consumer needs semantic distinction X
-> verify K0-K7 cannot represent X safely
-> write the concrete failing consumer case
-> design the minimum extension
-> add validation/rejection tests
-> consume the extension in the requesting feature
-> qualify ontology + consumer together
```

## 5. Completed V1 Package 1 — local tutor vertical slice

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`  
**PR:** #94  
**Final head:** `9867105509e0f243a7823066d626abe1cad40148`  
**Merge commit:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`

Package 1 added:

- content-addressed `LocalTutorWorkflowSnapshot` composition;
- installed `cme-local-tutor start|next`;
- exact M45 ranking before explicit selection/consent;
- existing M23/M8 persistence and replay;
- exact M46 proposal without execution;
- optional exact M42 transfer-plan context;
- positive, tamper, drift, declined-authority, and authority-edge tests.

Qualification on the exact candidate head: **948 passed, 8 intentional regular-job Stockfish skips, Ruff PASS, compileall PASS, independent Stockfish 8/8.**

## 6. V1 Package 2 — architecture and authority reconciliation

This document set is the V1 authority-reconciliation package. Its purpose is to ensure the repository describes the already-integrated local consumer rather than continuing to describe M42/M45/M46 or the consumer as future work.

Required documentation invariants:

- architecture graph includes M42, M45, M46, and V1 local composition as implemented;
- README/STATUS/CONTEXT/build status list `cme-local-tutor` as installed/current;
- latest runbook points at `v1-local-tutor-vertical-slice.md`;
- no document promotes M45 rank to learner diagnosis/consent;
- no document promotes M46 proposal to M8 execution;
- no document promotes M42 plan to M10 outcome;
- release qualification remains pending rather than being conflated with architecture completeness.

After this reconciliation merges, Package 2 is complete and Package 3 is the only remaining repository-resolvable V1 package from the current audit.

## 7. NEXT pending V1 package — Release Candidate & Distribution Qualification

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`

### Goal

Prove that the repository can be distributed and clean-installed as the Version 1.0 candidate without relying on an editable source checkout.

### Required work

```text
synchronize package/repository release identity
-> build wheel/sdist
-> create fresh isolated environment
-> install built artifact, not editable source
-> smoke promised command entry points
-> verify packaged ontology/data assets
-> verify import/version identity
-> retain full pytest/Ruff/compileall/independent Stockfish gate
```

### Acceptance boundary

Repository V1 readiness may be claimed only when the exact release candidate passes both:

1. the existing source-tree qualification gate; and
2. clean distribution/install/smoke qualification from built artifacts.

Actual publication to PyPI, hosted deployment, production credentials, and production external-service operation are not required for repository-qualified V1.

## 8. Post-V1 / conditional candidates

These are **not** substitutes for the pending release package:

- M35 generic operator exposure;
- M37 cross-surface consumer compatibility work unless a concrete blocker appears;
- M38 recurrence candidate mining if it would duplicate M7C;
- generic K8 expansion;
- M47 bounded multi-session study plan;
- cloud deployment, multi-tenancy, payments, social/community features, mobile apps;
- generic opening database/puzzle platform/rating prediction/gamification work;
- generic provider abstraction unrelated to a demonstrated provider need.

M47 may become useful after V1 if multi-session composition is the demonstrated product bottleneck, but it is not required to qualify the current repository architecture or local V1 workflow.

## 9. Phase-gate discipline

Before every package:

1. reconcile live `main`;
2. identify the concrete product/correctness problem;
3. identify the existing authority owner;
4. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
5. define exact inputs, outputs, claim ceiling, and forbidden authority changes;
6. reuse existing authority systems before adding a subsystem;
7. include negative/near-miss/tamper tests where code behavior changes;
8. run full pytest, Ruff, compileall, and independent Stockfish on the exact PR head;
9. merge only that qualified exact head;
10. reconcile documentation when feature state changes.

## 10. Current V1 queue

```text
[x] Package 1 — Qualify & Integrate V1 Local Tutor Vertical Slice
[x] Package 2 — Reconcile V1 Architecture & Repository Authorities
[ ] Package 3 — V1 Release Candidate & Distribution Qualification
```

The guiding rule is:

> **Finish qualifying the product we have before adding another backend abstraction.**
