# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:** [`repository-build-status.md`](repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture:** [`../architecture/architecture.md`](../architecture/architecture.md)  
> **V1 post-milestone runbook:** [`../runbooks/v1-post-milestone-handoff.md`](../runbooks/v1-post-milestone-handoff.md)  
> **Local-consumer runbook:** [`../runbooks/v1-local-tutor-vertical-slice.md`](../runbooks/v1-local-tutor-vertical-slice.md)  
> **Release-distribution runbook:** [`../runbooks/v1-release-distribution-qualification.md`](../runbooks/v1-release-distribution-qualification.md)

**Status:** Version 1.0 queue complete; historical plan plus post-V1 phase-gate policy.  
**Authority:** this document does not create production/empirical claims.

## 1. Product direction

Chess Mentor Engine is a persistent chess tutor that learns from a participant's games
and reasoning evidence rather than acting as a generic engine-analysis wrapper.

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

The contiguous numbered milestone series is qualified through **M34**. Additional
qualified work includes K0-K7 and M36/M39/M40/M41/M42/M43/M44/M45/M46.
Version 1.0 adds the integrated local tutor composition and a qualified `1.0.0`
release/distribution contract.

Current main authority is merge commit
`8e3abf063b2af7d09a46495f5e35c85c86d58f01` from PR #96.

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
M45 priority != learner diagnosis / implicit consent
M46 proposal != M8 execution / exposure
V1 composition != upstream authority
successful evidence case != mastery
repository release qualification != hosted-product approval
```

## 4. Product-pulled ontology policy

The Chess Knowledge Ontology remains a shared semantic substrate rather than an
independent expansion program. Do not create a generic K8 merely to add vocabulary,
detectors, relationships, or pedagogy metadata.

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

## 5. Completed V1 Package 1 — Local Tutor Vertical Slice

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`  
**PR:** #94  
**Final head:** `9867105509e0f243a7823066d626abe1cad40148`  
**Merge commit:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`

Package 1 integrated:

- content-addressed local tutor composition;
- installed `cme-local-tutor start|next`;
- exact M45 ranking before explicit selection/consent;
- existing M23/M8 persistence and replay;
- exact M46 proposal without execution;
- optional exact M42 transfer-plan context;
- positive, tamper, drift, declined-authority, and authority-edge tests.

## 6. Completed V1 Package 2 — Architecture & Authority Reconciliation

**Zone:** `REPOSITORY_ONLY`  
**PR:** #95  
**Final head:** `f12758c52de3e13468774d13c324510d48e6d7d7`  
**Merge commit:** `c41fda2f1c3c2002a4c960270b38ef3cce1ad144`

Package 2 reconciled repository authorities with the already-integrated local consumer
and preserved the claim/authority boundaries around M42, M45, M46, M8, M9, M10, and
learner inference.

## 7. Completed V1 Package 3 — Release Candidate & Distribution Qualification

**Zone:** `REPOSITORY_ONLY / HERMETIC_VALIDATION`  
**PR:** #96  
**Branch:** `work/v1-release-distribution`  
**Final head:** `4b5512a1b5d67ad0df43000898b5d371701d832c`  
**Merge commit:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`

Package 3 proved that the repository can be distributed and clean-installed as the
Version 1.0 candidate without relying on an editable source checkout:

```text
synchronize package/runtime identity at 1.0.0
-> build wheel + sdist
-> validate version / console-script / package-data contract
-> create fresh isolated environment
-> install built wheel with --no-index --no-deps
-> smoke installed commands
-> verify installed ontology/data/type-marker assets
-> preserve full pytest/Ruff/compileall/independent Stockfish gate
```

The exact final candidate passed PR CI run `34673791962`. The merged main commit passed
post-merge run `34673834249` with `test-and-lint`, `release-distribution`, and
`stockfish-integration` all green.

## 8. Version 1.0 terminal state

The bounded Version 1.0 queue is complete:

```text
[x] Package 1 — Qualify & Integrate V1 Local Tutor Vertical Slice
[x] Package 2 — Reconcile V1 Architecture & Repository Authorities
[x] Package 3 — V1 Release Candidate & Distribution Qualification
```

Current repository status:

```text
STATUS: VERSION_1_REPOSITORY_READY
```

Actual publication, hosted deployment, production credentials, production QA, security
or privacy approval, participant usefulness, and empirical tutoring efficacy are outside
the repository-qualified V1 claim.

## 9. Post-V1 / conditional candidates

No item below is automatically the next package. Each requires a demonstrated product
or operational need:

- M35 generic operator exposure;
- M37 cross-surface consumer compatibility work when a concrete incompatibility exists;
- M38 recurrence candidate mining only if it would not duplicate M7C authority;
- product-pulled K8 semantic extension;
- M47 bounded multi-session study plan if multi-session composition becomes a proven
  product bottleneck;
- hosted deployment, auth, multi-tenancy, privacy/security, payments, or mobile work;
- opening database, puzzle platform, rating prediction, gamification, or social features;
- provider abstraction tied to a demonstrated provider requirement;
- release publication/tagging automation if the owner chooses public distribution.

## 10. Next-milestone phase-gate discipline

Before creating any post-V1 package:

1. reconcile live `main` and this handoff;
2. name the concrete product, distribution, validation, or operational problem;
3. identify the existing authority owner;
4. classify work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
5. define exact inputs, outputs, claim ceiling, and forbidden authority changes;
6. reuse existing authority systems before adding a subsystem;
7. include negative/near-miss/tamper tests where behavior changes;
8. run the full source gate and any relevant independent witnesses on the exact PR head;
9. merge only the exact qualified head;
10. reconcile `STATUS.md`, build status, plan, and runbooks when milestone state changes.

The guiding rule remains:

> **Let demonstrated product need create the next package; do not let unused milestone
> numbers create work.**
