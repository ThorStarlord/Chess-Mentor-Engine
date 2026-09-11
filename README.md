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

The contiguous numbered milestone series remains qualified through **M34**. Additional
qualified work includes:

- **K0–K7** Chess Knowledge Ontology;
- **M36** deterministic learner-state read model;
- **M39** hypothesis evidence synthesis;
- **M40** teaching-priority / next-session proposal;
- **M43** contradiction/control evidence acquisition;
- **M41** ontology-aware intervention matching;
- **M44** learner-progress local reference surface.

The numbering is intentionally non-contiguous. M35, M37, M38, and M42 are not implied
to be implemented.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

The product targets a problem ordinary engine analysis does not solve by itself:

```text
What is objectively happening on the board?
What did this player actually notice, consider, and expect?
What recurring learner hypothesis is currently supported or contradicted?
Why does CME currently believe that?
What evidence would challenge or narrow the belief?
What kind of learning action should happen next?
Which training artifacts are plausible candidates without pretending they are proven?
Did later evidence support transfer without pretending that proves mastery?
```

## Qualified learner-intelligence path

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
        |
        +-- challenge/control/collect --> M43 evidence candidates
        |
        +-- teach concept ------------> M41 intervention candidates
        |
        `------------------------------> M44 learner-progress presentation
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

M40 remains proposal-only. M43 prepares evidence candidates, M41 prepares intervention
candidates, and M44 presents exact qualified sources. None of those layers silently
executes the action, changes M7C recurrence state, exercises M9 selection authority,
or creates M10 outcome evidence.

## Chess Knowledge Ontology

K0–K7 supplies a typed semantic bridge between board evidence and tutoring consumers:

```text
concept definition
!= concept assertion in a position/move
!= participant perception
!= learner inference
```

It contains tactical motifs, position features, strategic principles, evaluation
factors, plans, pedagogy metadata, a Lichess crosswalk, provenance-bound assertions,
conservative detectors, optional M19 coaching context, and an M7C-preserving learner
projection.

The ontology is now **shared product infrastructure, not the primary workstream**.
Do not open a generic K8 merely to make the ontology larger. Extend it only when a
concrete consumer exposes a semantic distinction K0–K7 cannot represent safely, and
qualify that minimum extension with the requesting consumer.

M41 and M44 both qualified without any ontology schema/data expansion.

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
M44 rendering != learner inference
M40 transfer-test proposal != M10 transfer evidence
successful evidence case != mastery
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

M36/M39/M40/M41/M43/M44 remain Python API and/or deterministic local-reference
surfaces. They add no production CLI command.

## Latest Python surfaces

### M36 learner-state read model

```python
from chess_mentor_engine.longitudinal import build_learner_state_read_model
```

### M39 / M40 learner intelligence

```python
from chess_mentor_engine.learner_intelligence import (
    build_hypothesis_evidence_synthesis,
    build_default_next_session_policy,
    build_next_session_plan,
)
```

### M43 evidence acquisition

```python
from chess_mentor_engine.learner_intelligence import (
    build_default_evidence_acquisition_policy,
    build_evidence_acquisition_plan,
)
```

### M41 intervention matching

```python
from chess_mentor_engine.learner_intelligence import (
    define_intervention_semantic_profile,
    build_default_intervention_matching_policy,
    build_intervention_candidate_set,
)
```

### M44 learner-progress reference surface

```python
from chess_mentor_engine.learner_intelligence import (
    build_learner_progress_view,
    build_learner_progress_reference_surface,
)
```

## Qualification

Latest focused suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
python -m pytest tests/test_m41_intervention_matching.py -rs
python -m pytest tests/test_m43_evidence_acquisition.py -rs
python -m pytest tests/test_m44_learner_progress_reference.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`docs/runbooks/m41-m44-tutor-decision-loop.md`](docs/runbooks/m41-m44-tutor-decision-loop.md)
for the latest restart and qualification path.

## Next product direction

The strongest next sequence is now:

```text
M42  bounded near/far transfer and retest planning
 ->
M45  batch recent games -> mentor queue
 ->
M46  adaptive Socratic tutoring
```

M35/M37 should be pulled forward only by a concrete consumer/operator blocker. M38
must not become a second recurrence engine; reuse M7C.

## Productization boundary

The repository has strong local evidence, semantic, learner-intelligence, decision,
candidate-preparation, and reference-presentation contracts. It still does not
establish production authentication, privacy/security approval, hosted multi-user
persistence, production provider/retry policy, production frontend quality, causal
learner diagnosis, intervention-caused improvement, mastery, or empirical tutoring
efficacy.
