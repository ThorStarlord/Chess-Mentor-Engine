# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-11  
**Current main authority baseline:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`  
**Contiguous numbered baseline:** M1–M34 qualified  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7  
**Qualified post-M34 learner-intelligence packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46  
**Integrated V1 local-consumer package:** PR #94 — `cme-local-tutor`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority and
[`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)
for the latest local-consumer restart/qualification path.

## Current V1 state

The repository has a coherent authority-separated backend and an integrated local tutor composition surface. Version 1.0 is **not yet release-qualified** because distribution identity/artifact qualification remains pending.

```text
V1 Package 1 — Local Tutor Vertical Slice                  INTEGRATED
V1 Package 2 — Architecture / Authority Documentation     THIS RECONCILIATION
V1 Package 3 — Release Candidate / Distribution           PENDING
```

Do not infer that a pending release package means another learner-intelligence subsystem is missing.

## Strongest qualified learner/tutor chain

```text
M7 / M7C learner hypothesis + recurrence / contradiction authority
+ M9 intervention applicability / selection authority
+ M10 bounded practice / near / far / real-game outcome evidence
+ M11 longitudinal learner state
+ optional K7 typed chess semantics
        |
        v
M36 deterministic learner-state read model
        |
        v
M39 exact hypothesis evidence synthesis
        |
        v
M40 ranked next-session action proposal
        |
        +-- evidence need --> M43 acquisition candidates
        +-- teaching need --> M41 intervention candidates
        +-- transfer need --> M42 bounded transfer/retest plan
        `-- explanation ----> M44 learner-progress reference surface

exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 transfer plan(s)
        |
        v
V1 LOCAL TUTOR COMPOSITION (`cme-local-tutor`)
        |
        v
M45 participant-scoped mentor queue
        |
        v
explicit operator selection + capture consent
        |
        v
M23 persistence/authorization bridge -> exact persisted M8 checkpoint
        |
        v
M46 proposed next Socratic action
        |
        v
existing `cme tutor` commands remain M8 execution / exposure authority
        |
        v
later M10 outcome evidence and M11 longitudinal state
```

The V1 local composition layer is orchestration-only. It does not create a second learner model, silently select an intervention, execute tutoring, establish transfer, or claim mastery.

## V1 local tutor integration provenance

**PR:** #94  
**Final head:** `9867105509e0f243a7823066d626abe1cad40148`  
**Merge commit:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`  
**PR CI run:** `34642933193`

Exact-candidate qualification:

```text
948 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish integration: 8 passed
```

Focused V1 tests include positive workflow coverage plus tamper, participant-drift, queue/session-drift, declined-selection/consent, and authority-edge rejection cases.

## Durable authority boundaries

Preserve all of these:

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 ontology projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping or selection
M42 transfer plan != M10 transfer evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis or intervention selection
M46 tutor proposal != M8 tutoring execution / exposure authority
V1 local composition != new chess / learner / pedagogy / outcome authority
M45 rank one != implicit user consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
```

## Current operational surfaces

Installed operator commands include:

```text
cme
cme-local-tutor
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

`cme-local-tutor start|next` composes exact already-qualified artifacts and persisted M8 state. Actual M8 tutoring transitions still use the existing `cme tutor ...` commands.

M36/M39/M40/M41/M42/M43/M44/M45/M46 remain deterministic Python APIs and/or local reference surfaces. The V1 composition does not create a hosted runtime or production frontend.

## Current claim ceiling

The repository can mechanically establish deterministic local composition, provenance/identity checks, authority preservation, engine-to-consumer evaluation fidelity, and hermetic workflow behavior.

It still cannot mechanically establish:

- real participant usefulness or approval;
- production browser/device/accessibility/usability quality;
- empirically effective or optimal tutoring policy;
- intervention-caused learning or mastery;
- production privacy/security/compliance posture;
- hosted authentication or multi-tenancy readiness;
- production provider retry/cost/secrets operations.

## Remaining Version 1.0 repository blocker

The next required V1 package is **Release Candidate & Distribution Qualification**. It must reconcile package identity/version, build a distributable artifact, clean-install that artifact, smoke the promised installed commands/package data, and add the clean-install witness to release qualification while preserving the existing full repository gate.

Until that package is qualified, do not claim `VERSION_1_REPOSITORY_READY`.

M35, M37, M38, K8, M47, hosted deployment, multi-tenancy, mobile, gamification, generic provider expansion, and empirical tutoring research are not substitutes for this remaining V1 release task.
