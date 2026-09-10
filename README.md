# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective
chess evidence, participant evidence, learner inference, tutoring, and pedagogy in
separate provenance-bearing layers.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Current product surface

The repository now has both Python APIs and an installed local `cme` command.
The current bounded product path is:

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound UCI engine analysis
-> objective played-move comparison
-> deterministic evaluation presentation
-> frozen participant decision evidence
-> position-local reasoning discrepancy
-> participant-specific learner hypothesis
-> controlled persistent tutoring
-> grounded session-local mentor feedback
-> explicit training selection
-> bounded outcome / transfer evidence
-> append-only longitudinal learner state
```

Each arrow remains an authority boundary. Qualified software behavior is not proof
of a causal cognitive diagnosis, permanent learner trait, effective intervention,
mastery, or empirical tutoring value.

Use [current build status](docs/product/repository-build-status.md) as the concise
status authority and [CONTEXT.md](CONTEXT.md) for contributor orientation. Historical
M1-M10 setup and research protocols remain in the
[post-M10 runbook](docs/runbooks/post-m10-milestone-runbook.md) and linked ADRs.

## Implemented milestones

| Surface | What is available |
| --- | --- |
| M1-M4 | Canonical game/position evidence, deterministic chess features, normalized engine evidence, played-decision comparison, and bounded diagnostic selection. |
| M5-M7 | Frozen participant evidence, reasoning discrepancies, and append-only participant-specific hypothesis ledgers with challenge/contradiction evidence. |
| M8-M10 | Evidence-aware tutoring, explicit intervention selection, and separate practice/near/far/real-game outcome evidence. |
| M11 | Append-only longitudinal learner state bound to exact current M7 revisions and optional same-revision M10 evidence. |
| M12 | Read-only local `cme` evidence CLI for PGN inspection, position packets, and verified artifact inspection. |
| M13 | Persistent replay-verified `cme tutor ...` workflow over the qualified M8 state machine. |
| M14 | Engine-backed `cme analyze` workflow over qualified M3/M4 contracts, with optional immutable participant-scoped package archival. |
| M15 | Deterministic evaluation presentation projection with explicit perspective, mate/bound/partial semantics, PVs, engine identity, and exact evidence references. |
| M16 | Deterministic grounded mentor-feedback composition over exact M15/M6 and optional complete active-current M7 evidence, with native M8 explanation recording. |
| M17 | Opt-in `cme analyze --with-presentation` bridge that sends exact M14/M3/M4 records through M15 without changing the M14 archive contract. |

The UCI provider remains version `0.2`: Black-root score bounds are normalized into
White evaluation ordering, explicit invalid MultiPV ranks fail closed, mate remains
symbolic, and engine provenance is preserved. Historical `0.1` evidence is not
rewritten.

## Install

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cme --help
```

Stockfish or another UCI engine is an explicitly supplied external executable; no
engine binary is bundled.

## CLI

### Inspect games and deterministic position context

```bash
cme games inspect games.pgn
cme games inspect games.pgn --full
cme position packet games.pgn --game-index 0 --ply-index 12
```

`position packet` remains engine-free. See the
[M12 runbook](docs/runbooks/m12-local-evidence-cli.md).

### Run bounded engine analysis

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000
```

M14 runs the exact canonical root through the qualified M3 UCI provider and emits
the native M4 played-decision comparison. If the played move lies outside a
complete root MultiPV, the exact canonical child is reanalyzed under the same
request. Regime drift remains `incompatible_analysis_regime`; bounded, partial,
mate, terminal, and failure states are not coerced into fake centipawn precision.

M17 can project those exact in-memory records through M15 in the same CLI request:

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --with-presentation
```

The opt-in response adds a top-level `presentation` with schema
`m15.evaluation-presentation.v1`. M15 revalidates the exact M3/M4 relationship and
fails closed on evidence drift. Without `--with-presentation`, the M14 response is
unchanged.

Optional archival requires an **existing** local artifact database and an explicit
participant scope:

```bash
cme analyze games.pgn \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --db ./mentor.sqlite3 \
  --participant P01
```

Even when `--with-presentation` is used, optional archival stores only the exact
`m14.analysis-package.v1` payload. The presentation is a derived response and is
built before archival so projection failure cannot leave a storage side effect.
See the [M14 runbook](docs/runbooks/m14-engine-analysis-cli.md) and
[M17 runbook](docs/runbooks/m17-analysis-presentation-bridge.md).

### Inspect verified local artifacts

```bash
cme artifacts list --db ./mentor.sqlite3 --participant P01
cme artifacts show --db ./mentor.sqlite3 --participant P01 --kind KIND ARTIFACT_ID
cme artifacts verify --db ./mentor.sqlite3 --participant P01
```

Participant scoping is not authentication. Protect the plaintext database.

### Run persistent tutor checkpoints

M13 exposes controlled append-only commands over M8:

```text
cme tutor start
cme tutor status
cme tutor present-position
cme tutor present-stage
cme tutor respond
cme tutor freeze
cme tutor reveal
cme tutor compare
cme tutor attach-hypothesis
cme tutor explain
cme tutor complete
```

Every mutation loads and verifies an exact prior checkpoint, replay-validates M8,
applies one native transition, then writes a successor checkpoint. It does not
generate engine evidence, M6 assessments, M7 hypotheses, explanation prose,
training decisions, or automatic M11 mutations. See the
[M13 runbook](docs/runbooks/m13-persistent-tutor-cli.md).

M15 remains a Python API and is also exposed as an opt-in projection from
`cme analyze` through M17. M16 remains a Python API rather than a new CLI command.
The existing `cme tutor explain` command remains the explicit-input M13 surface.

## Python APIs

The CLI does not replace the domain APIs. Important package boundaries remain:

- `chess_mentor_engine.analysis` — normalized M3 engine evidence;
- `chess_mentor_engine.selection` — M4 comparison and diagnostic selection;
- `chess_mentor_engine.presentation` — M15 deterministic evaluation presentation;
- `chess_mentor_engine.feedback` — M16 grounded session-local mentor feedback;
- `chess_mentor_engine.evidence` — participant evidence;
- `chess_mentor_engine.learning` — M6 reasoning discrepancy and M7 hypothesis records;
- `chess_mentor_engine.tutoring` — M8 state machine;
- `chess_mentor_engine.training` — M9 intervention registry/selection;
- `chess_mentor_engine.evaluation` — M10 outcome and transfer evidence;
- `chess_mentor_engine.longitudinal` — M11 longitudinal learner state;
- `chess_mentor_engine.storage` — local immutable artifacts and verified replay.

### Project engine evidence for display

M15 consumes already-qualified M3/M4 records; it does not run an engine:

```python
from chess_mentor_engine.presentation import build_evaluation_presentation

view = build_evaluation_presentation(
    root_analysis=root_analysis,
    comparison=decision_comparison,
    played_analysis=played_child_analysis,  # optional
)
```

The `m15.evaluation-presentation.v1` projection retains the canonical White engine
view and an explicit original decision-mover view. Black mover projection negates
centipawns and reverses lower/upper ordering bounds. Mate remains symbolic as
winner + plies-to-mate. Partial, bounded, incompatible, failed, terminal, or empty
evidence stays visibly non-exact rather than receiving a fabricated numeric score.
Ranked UCI PVs, engine provenance, fingerprints, and M4 evidence references are
preserved.

M15 intentionally does not round centipawns into pawn floats, localize score
strings, convert PVs to SAN, or invent `inaccuracy`, `mistake`, or `blunder`
thresholds. See the
[M15 runbook](docs/runbooks/m15-evaluation-presentation.md).

### Compose grounded mentor feedback

M16 composes deterministic feedback only after the M8 tutor session has an exact
M6 comparison. Optional M7 context must be the complete active-current context
already attached to the session:

```python
from chess_mentor_engine.feedback import (
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)

feedback = compose_grounded_mentor_feedback(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,  # optional
    created_at="2026-09-09T10:13:00-03:00",
)

updated, explanation, feedback = record_grounded_mentor_feedback(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    created_at="2026-09-09T10:13:00-03:00",
)
```

The `m16.grounded-mentor-feedback.v1` record contains evidence-bound objective,
reasoning, optional learner-context, and reflection sections. Every M6 assertion is
preserved. Every attached active M7 revision is retained and framed as descriptive
hypothesis context rather than causal diagnosis. Non-exact M15 evidence never
becomes a fabricated exact centipawn loss.

`record_grounded_mentor_feedback` uses the existing qualified M8 explanation
transition and records explicit template provenance. M16 v1 does not invoke an LLM,
create new M6/M7 judgments, select M9 training, mutate M11, or claim coaching
efficacy. See the
[M16 runbook](docs/runbooks/m16-grounded-mentor-feedback.md).

See the [M11 runbook](docs/runbooks/m11-longitudinal-learner-state.md) for longitudinal
operation and qualification.

## Validation

Focused current product-surface qualification:

```bash
python -m pytest tests/test_m11_qualification.py
python -m pytest tests/test_m12_cli.py
python -m pytest tests/test_m13_persistent_tutor_cli.py
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
python -m pytest tests/test_m16_grounded_mentor_feedback.py
python -m pytest tests/test_m17_analysis_presentation_bridge.py
```

Related engine/comparison contracts:

```bash
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
python -m pytest tests/test_decision_comparison.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final command requires `STOCKFISH_EXECUTABLE`. Skipped integration tests are
not an independent engine pass. CI runs the native test/lint job and an independent
Stockfish job. No standalone Python static type checker is currently configured;
tests, Ruff, imports, and syntax compilation must not be reported as a type-checker
pass.

## Claim ceiling and next product boundary

The repository can preserve and connect objective chess evidence, frozen player
evidence, bounded learner hypotheses, tutoring state, intervention/outcome evidence,
longitudinal history, deterministic display semantics, and deterministic grounded
session-local feedback. M12-M14 expose a usable local CLI over selected qualified
capabilities, and M17 now carries exact M14 analysis/comparison evidence directly
through the M15 UI-safe presentation contract. M16 remains the downstream grounded
feedback API.

It still does **not** establish:

- causal cognitive mechanisms or permanent learner traits;
- intervention-caused improvement or automatic mastery;
- universal chess-evaluation or move-quality thresholds;
- model/LLM-generated free-form coaching quality;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from a tutor session;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

Any future model-backed coaching or user-interface layer must preserve the exact M16
grounding contract rather than collapsing engine analysis, participant evidence,
learner hypotheses, and authored language into one opaque authority.

## Documentation map

- [Current build status](docs/product/repository-build-status.md) — current milestone and qualification authority.
- [CONTEXT.md](CONTEXT.md) — contributor orientation and authority boundaries.
- [M11 longitudinal state](docs/runbooks/m11-longitudinal-learner-state.md) — longitudinal operation and qualification.
- [M12 local evidence CLI](docs/runbooks/m12-local-evidence-cli.md) — read-only CLI surface.
- [M13 persistent tutor CLI](docs/runbooks/m13-persistent-tutor-cli.md) — replay-verified tutor workflow.
- [M14 engine analysis CLI](docs/runbooks/m14-engine-analysis-cli.md) — objective engine-backed analysis package.
- [M15 evaluation presentation](docs/runbooks/m15-evaluation-presentation.md) — deterministic UI-safe evidence projection.
- [M16 grounded mentor feedback](docs/runbooks/m16-grounded-mentor-feedback.md) — deterministic evidence-bound feedback composition.
- [M17 analysis presentation bridge](docs/runbooks/m17-analysis-presentation-bridge.md) — opt-in CLI projection over exact M14/M3/M4 records.
- [Architecture overview](docs/architecture/architecture.md) — earlier layer map and historical implementation boundary.
- [Decision records](docs/decisions/README.md) — normative bounded contracts.
- [Product build plan](docs/product/chess-mentor-engine-repository-build-plan.md) — planning history and broader product direction.