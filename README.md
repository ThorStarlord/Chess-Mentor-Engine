# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective chess
evidence, participant evidence, learner inference, tutoring policy, model-authored
language, evaluator judgment, and pedagogy in separate provenance-bearing layers.

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Roadmap:** [`docs/product/chess-mentor-engine-repository-build-plan.md`](docs/product/chess-mentor-engine-repository-build-plan.md)  
> **V1 release runbook:** [`docs/runbooks/v1-release-distribution-qualification.md`](docs/runbooks/v1-release-distribution-qualification.md)  
> **Local-consumer runbook:** [`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)

## Current implementation boundary

The contiguous numbered milestone series remains qualified through **M34**. Additional
qualified work includes:

- **K0–K7** Chess Knowledge Ontology;
- **M36** deterministic learner-state read model;
- **M39** hypothesis evidence synthesis;
- **M40** teaching-priority / next-session proposal;
- **M43** contradiction/control evidence acquisition;
- **M41** ontology-aware intervention matching;
- **M42** bounded transfer / retest planning;
- **M44** learner-progress local reference surface;
- **M45** participant-scoped batch mentor queue;
- **M46** adaptive Socratic tutor action policy;
- **V1 local tutor composition** via installed `cme-local-tutor start|next`;
- **V1 release identity and distribution qualification** for package version `1.0.0`.

The numbering is intentionally non-contiguous. **M35, M37, and M38 are not implied to
be implemented.** K8 is not an active ontology program.

Version 1.0 repository readiness is commit-scoped: the current candidate must pass the
full source gate, the independent Stockfish job, and the `release-distribution` clean
artifact/install job. Publishing or production deployment is not part of that claim.

## Product thesis

The product targets a problem ordinary engine analysis does not solve by itself:

```text
What is objectively happening on the board?
What did this player actually notice, consider, and expect?
What recurring learner hypothesis is currently supported or contradicted?
Why does CME currently believe that?
What evidence would challenge or narrow the belief?
What kind of learning action should happen next?
Which recent positions deserve attention for this learner now?
What should the tutor ask, hint, reveal, or reflect on next without contaminating
  the measurement opportunity?
Did later evidence support transfer without pretending that proves mastery?
```

## Qualified learner/tutor architecture

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> diagnostic selection
-> captured participant reasoning
-> M6 position-local discrepancy
-> M7 / M7C learner hypothesis + recurrence / contradiction evidence
-> M9 explicit intervention selection
-> M10 bounded practice / near / far / real-game evidence
-> M11 longitudinal learner state

optional K0-K7 typed chess semantics
        |
        v
M36 read model -> M39 synthesis -> M40 next-session proposal
        |
        +-- challenge/control/collect --> M43 evidence candidates
        +-- teach concept ------------> M41 intervention candidates
        +-- transfer test ------------> M42 transfer/retest plan
        `------------------------------> M44 learner-progress view
```

The integrated V1 local tutor composition is:

```text
exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 transfer plan(s)
        |
        v
cme-local-tutor
        |
        v
M45 mentor queue
        |
        v
explicit operator selection + capture consent
        |
        v
M23 -> persisted M8 checkpoint
        |
        v
M46 next-action proposal
        |
        v
existing cme tutor commands remain M8 execution/exposure authority
```

This composition does not duplicate learner inference, M9 selection, M10 outcomes, M8
execution, or mastery authority.

## Core authority rules

```text
objective chess truth != participant self-report != learner inference
one discrepancy != recurrence != causal learner trait
concept occurrence != participant perception or learner weakness
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping or selection
M42 transfer plan != M10 transfer evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis or intervention selection
M46 tutor proposal != M8 tutoring execution / exposure authority
V1 local composition != new inference / selection / outcome authority
M45 rank one != implicit consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model-authored language
M20 evaluator acceptance != objective chess truth
```

## Install

Use Python 3.11 or newer for development:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cme --help
cme-local-tutor --help
```

The editable install is a development surface, not the V1 release witness. The
repository separately builds and clean-installs the `1.0.0` wheel under the
`release-distribution` CI job. See the V1 release runbook for the exact commands.

Stockfish or another UCI engine is an explicitly supplied external executable; no
engine binary is bundled with the package.

## Installed commands

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

The principal `cme` command includes:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
```

`cme-local-tutor start|next` is the V1 local composition surface. It consumes exact
already-qualified structural artifacts and persisted M8 state; it does not replace the
existing commands that create those authorities.

## V1 local tutor example

Start a bounded review only after explicit selection and capture consent:

```bash
cme-local-tutor start game.pgn \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --protocol-json capture-protocol.json \
  --prompts-json prompts.json \
  --selection-decision selected \
  --capture-consent granted \
  --recorded-at 2026-09-11T18:00:00-03:00 \
  --created-at 2026-09-11T18:01:00-03:00 \
  --create-db
```

Continue after persisted M8 transitions with:

```bash
cme-local-tutor next \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-11T18:10:00-03:00 \
  '<current-session-artifact-id>'
```

See the local-consumer runbook for exact artifact and authority requirements.

## Qualification

Focused local-consumer and release suites:

```bash
python -m pytest tests/test_v1_local_tutor_workflow.py -rs
python -m pytest tests/test_v1_local_tutor_authority_edges.py -rs
python -m pytest tests/test_v1_release_distribution.py -rs
python -m pytest tests/test_package.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The independent `release-distribution` job additionally:

```text
builds wheel + sdist
-> validates version / entry points / packaged data
-> installs the wheel into a fresh virtual environment with --no-index --no-deps
-> smokes all promised installed commands
-> verifies installed metadata and packaged JSON/type-marker assets
```

A commit may be called `VERSION_1_REPOSITORY_READY` only when these source, Stockfish,
and release-distribution gates all pass for that candidate.

## Version 1.0 boundary

The release-distribution package is the final repository-resolvable V1 package. Do not
invent M47, generic ontology expansion, hosted infrastructure, or other optional work as
a prerequisite once the current candidate satisfies the defined gates.

Publishing artifacts, deploying services, production security/privacy approval,
real-participant usability, and empirical tutoring efficacy remain external-authority or
post-V1 concerns.

## Productization boundary

The repository has strong local evidence, semantic, learner-intelligence,
review-priority, controlled-tutoring, evaluation-fidelity, local-composition, and
release-artifact contracts. It still does not establish production authentication,
privacy/security approval, hosted multi-user persistence, production provider/retry
policy, production frontend quality, causal learner diagnosis, intervention-caused
improvement, mastery, or empirical tutoring efficacy.
