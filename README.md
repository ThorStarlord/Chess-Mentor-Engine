# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective chess evidence, participant evidence, learner inference, tutoring policy, model-authored language, evaluator judgment, and pedagogy in separate provenance-bearing layers.

> **Current implementation authority:** [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **V1 local-consumer runbook:** [`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)  
> **Post-V1 product-use runbook:** [`docs/runbooks/post-v1-local-product-use-observation.md`](docs/runbooks/post-v1-local-product-use-observation.md)

## Current implementation boundary

The historical Version 1.0 repository boundary is qualified through M34 plus K0-K7, M36, M39, M40, M41, M42, M43, M44, M45, M46, the V1 local tutor composition, and the `1.0.0` release/distribution contract.

M35, M37, and M38 remain unimplemented labels. K8 and M47 are not active programs merely because more development is possible.

The first post-V1 package is now integrated on `main` through PR #98. It is intentionally smaller than "tutor validation":

```text
selected exact M8 checkpoint
-> guided local baseline capture
-> exact M8 baseline freeze
-> immutable descriptive product-use observations
-> explicit participant self-report
-> deterministic participant-scoped report
```

Its claim ceiling is:

```text
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

Real repeated learner use remains external evidence. The repository does not call this package proof that CME works pedagogically.

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

The V1 local composition remains:

```text
exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 transfer plan(s)
        |
        v
M45 mentor queue
        |
        v
explicit selection + capture consent
        |
        v
M23 -> persisted M8 checkpoint
        |
        v
M46 next-action proposal
        |
        v
existing M8 commands remain execution/exposure authority
```

The integrated post-V1 guided `review` surface reuses existing M8 transitions and deliberately stops at baseline freeze. It does not reveal objective evidence, generate M46, or execute M46. An operator may separately invoke `cme-local-tutor next` to inspect the current M46 proposal.

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
post-V1 product-use observation != learner inference / tutor efficacy / mastery
M45 rank one != implicit consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
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

`1.0.0` is the historical qualified V1 release identity. Current post-V1 development uses `1.1.0.dev0`; CI derives the expected artifact identity from `pyproject.toml` and clean-installs the built wheel. This does not imply that a `1.1.0` release has been approved or published.

Stockfish or another UCI engine is an explicitly supplied external executable; no engine binary is bundled with the package.

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

The local tutor exposes:

```text
cme-local-tutor start      V1 composition and explicit authorization
cme-local-tutor next       replay exact M8 state and emit current M46 proposal
cme-local-tutor review     guide an already-selected M8 checkpoint to baseline freeze
cme-local-tutor feedback   record bounded participant self-report
cme-local-tutor report     summarize descriptive participant-scoped observations
```

## Local product-use path

After `start` returns an exact selected M8 checkpoint and the exact position packet is available:

```bash
cme-local-tutor review \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --position-json position-context.json \
  '<selected-session-artifact-id>'
```

Afterward, the existing `next` command may be used to inspect the M46 proposal for the frozen checkpoint. The guided review itself does not generate or execute it.

Record bounded self-report:

```bash
cme-local-tutor feedback \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --review-relevance 4 \
  --workflow-clarity 3 \
  --would-review-again 5 \
  --note "Useful position; setup still feels technical." \
  '<session-artifact-id>'
```

Summarize observations:

```bash
cme-local-tutor report --db ./mentor.sqlite3 --participant P01
```

See the post-V1 product-use runbook for the complete boundary and sequence.

## Qualification

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The independent `release-distribution` job additionally builds wheel + sdist, validates version/entry-points/package data, clean-installs the wheel with `--no-index --no-deps`, smokes the installed commands, and checks installed metadata/assets.

PR #98 final head `35dc40e08fd2b0e006f644b0a0846fef2edb51aa` and merge commit `a28b6b528e2bb823d9e4dfaa50da40f57760c7f5` both passed the repository-defined gates.

## Version and productization boundaries

`VERSION_1_REPOSITORY_READY` remains the historical V1 claim for the integrated 1.0.0 lineage. The post-V1 product-use observation package is integrated but does not establish real-user usefulness or tutoring efficacy.

The repository still does not establish production authentication, privacy/security approval, hosted multi-user persistence, production provider/retry policy, production frontend quality, causal learner diagnosis, intervention-caused improvement, mastery, or empirical tutoring efficacy.

The next useful evidence should come from repeated local use, not automatic architecture expansion.
