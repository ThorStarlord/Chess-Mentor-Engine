# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective chess
evidence, participant evidence, learner inference, tutoring policy, model-authored
language, evaluator judgment, and pedagogy in separate provenance-bearing layers.

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Roadmap:**
> [`docs/product/chess-mentor-engine-repository-build-plan.md`](docs/product/chess-mentor-engine-repository-build-plan.md)

## Current implementation boundary

The contiguous numbered milestone series remains qualified through **M34**. The
repository also has the qualified **K0–K7 Chess Knowledge Ontology** program and the
non-contiguous post-M34 learner-intelligence packages **M36, M39, and M40**.

M35, M37, and M38 remain planning labels; later-numbered qualified packages do not
imply those candidates were implemented.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

The product is aimed at a problem ordinary engine analysis does not solve by itself:

```text
What is objectively happening on the board?
What did this player actually notice, consider, and expect?
What recurring learner hypothesis is currently supported or contradicted?
What should happen next: gather evidence, challenge the hypothesis, teach, practice,
or test transfer?
Did later evidence support transfer without pretending that proves mastery?
```

The repository therefore treats chess truth, participant evidence, learner inference,
and pedagogical decisions as different authorities.

## Qualified learner-intelligence path

The current evidence and semantic substrate now reaches a deterministic planning
proposal:

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

optional K0-K7 typed chess-knowledge semantics
        |
        v
M36 deterministic learner-state read model
        |
        v
M39 exact hypothesis evidence synthesis
        |
        v
M40 transparent next-session action proposal
```

M40 currently proposes one of:

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

The proposal has no execution authority. It does not mutate M7/M11, replace M9,
create M10 evidence, start a tutor session, or call a model/provider.

## Chess Knowledge Ontology

The K0–K7 program supplies a typed semantic bridge between board evidence and
coaching consumers:

```text
concept definition
!=
concept assertion in a position/move
!=
learner inference about a participant
```

It contains tactical motifs, position features, strategic principles, evaluation
factors, plans, pedagogy metadata, a Lichess crosswalk, provenance-bound assertions,
conservative detectors, optional M19 coaching context, and an M7C-preserving learner
projection.

A registered concept is not automatically detectable, and a detected concept is not
proof that the participant noticed or misunderstood it.

## Core authority rules

Preserve these boundaries:

```text
objective chess truth != participant self-report != learner inference
one discrepancy != recurrence != causal learner trait
concept occurrence != participant perception or learner weakness
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M40 action proposal != M9 intervention selection
M40 transfer-test proposal != M10 transfer evidence
WAIT_FOR_REAL_GAME_EVIDENCE != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model-authored language
M20 evaluator acceptance != objective chess truth
```

## Install

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cme --help
```

Stockfish or another UCI engine is an explicitly supplied external executable; no
engine binary is bundled with the package.

## Installed commands

```text
cme
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

M36/M39/M40 currently remain Python API / deterministic-hermetic surfaces. They add
no new production CLI command.

## Latest Python surfaces

### M36 learner-state read model

```python
from chess_mentor_engine.longitudinal import build_learner_state_read_model
```

M36 composes exact current M7/M9/M10/M11 evidence plus optional K7 context into one
content-addressed participant read model.

### M39 hypothesis evidence synthesis

```python
from chess_mentor_engine.learner_intelligence import (
    build_hypothesis_evidence_synthesis,
)
```

M39 explains the exact current M7C evidence for one current learner hypothesis,
including contradictions, counterexamples, context exceptions, evidence gaps, and
optional K7 concepts.

### M40 next-session planner

```python
from chess_mentor_engine.learner_intelligence import (
    build_default_next_session_policy,
    build_next_session_plan,
)
```

M40 ranks transparent next-action proposals under an explicit versioned policy.

## Qualification

Latest focused suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`docs/runbooks/m36-m40-learner-intelligence.md`](docs/runbooks/m36-m40-learner-intelligence.md)
for the latest restart and qualification path.

## Productization boundary

The repository has strong local evidence, semantic, learner-intelligence, and
planning contracts. It still does not establish production authentication,
privacy/security approval, hosted multi-user persistence, production provider/retry
policy, production frontend quality, causal learner diagnosis, intervention-caused
improvement, mastery, or empirical tutoring efficacy.
