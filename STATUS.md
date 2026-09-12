# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-11  
**Release identity:** `chess-mentor-engine==1.0.0`  
**Contiguous numbered baseline:** M1–M34 qualified  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7  
**Qualified post-M34 packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46  
**V1 local consumer:** PR #94 — `cme-local-tutor`  
**V1 authority reconciliation:** PR #95

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority,
[`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)
for the local tutor path, and
[`docs/runbooks/v1-release-distribution-qualification.md`](docs/runbooks/v1-release-distribution-qualification.md)
for the Version 1.0 distribution gate.

## Current V1 state

```text
V1 Package 1 — Local Tutor Vertical Slice                  INTEGRATED
V1 Package 2 — Architecture / Authority Documentation     INTEGRATED
V1 Package 3 — Release Candidate / Distribution           CURRENT RELEASE GATE
```

The repository now has a coherent authority-separated learner/tutor architecture and a
single local composition path:

```text
M7/M7C + M9 + M10 + M11 + optional K7
-> M36 -> M39 -> M40
-> M43 / M41 / M42
-> M44

exact M18 queue + exact M44 view + optional exact M42 plan(s)
-> cme-local-tutor
-> M45 mentor queue
-> explicit selection + capture consent
-> M23 -> persisted M8 checkpoint
-> M46 next-action proposal
-> existing M8 commands remain execution/exposure authority
```

## Version 1.0 distribution contract

Package and runtime version authorities are synchronized at `1.0.0`.

Expected built artifacts:

```text
dist/chess_mentor_engine-1.0.0-py3-none-any.whl
dist/chess_mentor_engine-1.0.0.tar.gz
```

The independent `release-distribution` CI job must:

```text
build wheel + sdist
-> validate release version, console entry points, and packaged data
-> create a fresh virtual environment
-> install the built wheel with --no-index --no-deps
-> smoke every promised installed command with --help
-> verify installed metadata and packaged type/JSON assets
```

Focused rejection tests cover wrong release version, missing promised entry points,
missing wheel package data, and missing sdist package data.

## Durable authority boundaries

```text
objective chess truth != participant evidence != learner inference
K7 ontology projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping or selection
M42 transfer plan != M10 transfer evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis or intervention selection
M46 tutor proposal != M8 execution / exposure authority
V1 local composition != new chess / learner / pedagogy / outcome authority
M45 rank one != implicit user consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
repository release qualification != hosted-product approval
```

## Version 1.0 terminal condition

A commit may be called `VERSION_1_REPOSITORY_READY` only when all of these pass on that
candidate:

```text
full pytest including rejection tests
Ruff
compileall over src/tests/tools
independent Stockfish integration
release-distribution wheel/sdist + clean-install witness
```

Once those gates pass for the `1.0.0` candidate, there are no additional
repository-resolvable Version 1.0 packages in the queue. Publication, deployment,
production QA, real-user validation, and empirical tutoring research remain separate
from repository readiness.

Do not substitute M35, M37, M38, K8, M47, hosted infrastructure, multi-tenancy, mobile,
gamification, or generic provider expansion for the terminal V1 repository gate.
