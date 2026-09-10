# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective
chess evidence, participant evidence, learner inference, tutoring, model-authored
language, and pedagogy in separate provenance-bearing layers.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Current product surface

The current bounded product path is:

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound UCI engine analysis
-> objective played-move comparison
-> deterministic diagnostic candidate/control selection
-> deterministic evaluation presentation
-> frozen participant decision evidence
-> position-local reasoning discrepancy
-> participant-specific learner hypothesis
-> controlled persistent tutoring
-> deterministic grounded session-local mentor feedback
-> provenance-bound model language rendering
-> explicit training selection
-> bounded outcome / transfer evidence
-> append-only longitudinal learner state
```

Each arrow remains an authority boundary. Qualified software behavior is not proof
of a causal cognitive diagnosis, permanent learner trait, effective intervention,
mastery, model correctness, or empirical tutoring value.

Use [current build status](docs/product/repository-build-status.md) as the moving
implementation authority, [STATUS.md](STATUS.md) as the completed M17–M19 milestone
handoff, and [CONTEXT.md](CONTEXT.md) for contributor orientation.

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
| M15 | Deterministic evaluation presentation with explicit perspective, mate/bound/partial semantics, PVs, engine identity, and exact evidence references. |
| M16 | Deterministic grounded mentor-feedback composition over exact M15/M6 and optional complete active-current M7 evidence. |
| M17 | Qualified/merged opt-in `cme analyze --with-presentation` bridge over exact in-memory M14/M3/M4 records (PR #49). |
| M18 | Qualified/merged `cme diagnose` workflow for bounded engine analysis plus explicit versioned M4 candidate/control selection (PR #50). |
| M19 | Qualified/merged provider-neutral model-language rendering bound to exact recomputed M16 grounding and explicit model provenance (PR #51). |

The UCI provider remains version `0.2`: Black-root score bounds are normalized into
White evaluation ordering, invalid MultiPV ranks fail closed, mate remains symbolic,
and engine provenance is preserved.

## M17–M19 milestone handoff

The completed milestone is summarized in [STATUS.md](STATUS.md). The two new CLI
entry points used by the milestone are:

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --with-presentation

cme diagnose games.pgn \
  --game-index 0 \
  --start-ply 0 \
  --end-ply 30 \
  --policy ./selection-policy.json \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3
```

M19 is intentionally a Python API rather than a new CLI command. Its focused
qualification suite is included in the milestone regression set:

```bash
python -m pytest tests/test_m17_analysis_presentation_bridge.py
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
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
the native M4 played-decision comparison. If a complete root MultiPV omits the
played move, the exact canonical child is reanalyzed under the same request/provider
configuration. Partial, bounded, mate, terminal, incompatible, and failure states
are preserved rather than coerced into fake centipawn precision.

M17 can project those exact in-memory records through M15 in the same request:

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --with-presentation
```

Optional archival requires an **existing** local artifact database and an explicit
participant scope. Even with `--with-presentation`, the archive stores only
`m14.analysis-package.v1`; projection is built before archival.

See the [M14 runbook](docs/runbooks/m14-engine-analysis-cli.md) and
[M17 runbook](docs/runbooks/m17-analysis-presentation-bridge.md).

### Build a diagnostic move-analysis queue

M18 analyzes a selected game over an explicit inclusive played-ply range and applies
an explicit versioned M4 `SelectionPolicy`:

```bash
cme diagnose games.pgn \
  --game-index 0 \
  --start-ply 0 \
  --end-ply 30 \
  --policy ./selection-policy.json \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3
```

The output contains both the complete auditable source pool and the native
deterministic `DiagnosticCandidateBatch`, including controls, exclusions, quotas,
policy/source fingerprints, and shortfalls. The CLI does not embed universal
`inaccuracy`, `mistake`, or `blunder` thresholds.

See the [M18 runbook](docs/runbooks/m18-diagnostic-analysis-queue.md).

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

Every mutation loads and replay-verifies an exact prior checkpoint, applies one
native transition, then writes a successor checkpoint. `cme tutor explain` records
explicitly authored text and provenance; it is not an automatic M16/M19 model call.

See the [M13 runbook](docs/runbooks/m13-persistent-tutor-cli.md).

## Python APIs

Important package boundaries include:

- `chess_mentor_engine.analysis` — normalized M3 engine evidence;
- `chess_mentor_engine.selection` — M4 comparison and diagnostic selection;
- `chess_mentor_engine.presentation` — M15 deterministic evaluation projection;
- `chess_mentor_engine.feedback` — M16 deterministic grounded mentor feedback;
- `chess_mentor_engine.coaching` — M19 provider-neutral model-language boundary;
- `chess_mentor_engine.evidence` — participant evidence;
- `chess_mentor_engine.learning` — M6 reasoning discrepancy and M7 hypothesis records;
- `chess_mentor_engine.tutoring` — M8 state machine;
- `chess_mentor_engine.training` — M9 intervention registry/selection;
- `chess_mentor_engine.evaluation` — M10 outcome and transfer evidence;
- `chess_mentor_engine.longitudinal` — M11 learner state;
- `chess_mentor_engine.storage` — local immutable artifacts and verified replay.

### Project engine evidence for display

```python
from chess_mentor_engine.presentation import build_evaluation_presentation

view = build_evaluation_presentation(
    root_analysis=root_analysis,
    comparison=decision_comparison,
    played_analysis=played_child_analysis,
)
```

M15 consumes already-qualified M3/M4 records; it does not run an engine or define
move-quality labels. See the
[M15 runbook](docs/runbooks/m15-evaluation-presentation.md).

### Compose deterministic grounded mentor feedback

```python
from chess_mentor_engine.feedback import (
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)

feedback = compose_grounded_mentor_feedback(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    created_at="2026-09-10T10:13:00-03:00",
)
```

M16 recomputes the qualified M15 projection, verifies exact M3/M4 binding into the
M6 tutor context/reveal, preserves every M6 assertion, optionally preserves every
attached active-current M7 revision, and keeps non-exact evidence non-exact. M16 is
template-driven and remains the deterministic factual grounding ceiling.

See the [M16 runbook](docs/runbooks/m16-grounded-mentor-feedback.md).

### Bind model-authored mentor language to exact grounding

M19 is provider-neutral. First build the exact request:

```python
from chess_mentor_engine.coaching import (
    ModelCoachingGeneration,
    build_model_coaching_request,
    record_model_coaching_response,
)

request = build_model_coaching_request(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    created_at="2026-09-10T10:13:00-03:00",
)
```

The request contains the complete recomputed `m16.grounded-mentor-feedback.v1`
record plus a content-addressed M19 instruction ceiling. The model role is limited
to language rendering, Socratic reflection, and explanation of existing evidence
and uncertainty.

After an application invokes its chosen provider, bind the result:

```python
generation = ModelCoachingGeneration(
    request_id=request["request_id"],
    request_fingerprint=request["fingerprint"],
    rendered_content=model_text,
    provider_id="provider-name",
    model_id="model-name",
    model_version="provider-version",
    run_id="provider-run-id",
    generated_at="2026-09-10T10:14:00-03:00",
)

updated, explanation, coaching = record_model_coaching_response(
    request=request,
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    generation=generation,
)
```

The accepted M8 explanation records `actor_kind=model`, provider/model identity,
model version, provider run ID, and the exact M19 instruction fingerprint. The M19
record explicitly says `request_bound_not_semantically_verified`: provenance proves
which grounding reached which model run, not that arbitrary model prose is
factually correct or pedagogically effective.

`run_model_coaching` is also available for applications that implement the
`ModelCoachProvider` protocol. M19 deliberately does **not** freeze a production
provider, SDK, credentials flow, transport, retry policy, or model-quality claim.

See the
[M19 runbook](docs/runbooks/m19-provenance-bound-model-coaching.md).

## Validation

Focused current product-surface qualification:

```bash
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
python -m pytest tests/test_m16_grounded_mentor_feedback.py
python -m pytest tests/test_m17_analysis_presentation_bridge.py
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
```

Full pull-request merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`. Skipped integration tests are
not an independent engine pass. `python -m compileall -q src tests` is also useful
as a local syntax check. No standalone Python static type checker is configured.

## Claim ceiling

The repository can connect objective chess evidence, frozen player evidence,
bounded learner hypotheses, tutoring state, diagnostic selection, deterministic
grounded feedback, model-request provenance, training/outcome evidence, and
longitudinal history. It still does **not** establish:

- causal cognitive mechanisms or permanent learner traits;
- intervention-caused improvement or automatic mastery;
- universal chess-evaluation or move-quality thresholds;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from analysis, tutoring, or model coaching;
- a production LLM provider or production provider infrastructure;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M16 remains the deterministic factual grounding ceiling. M19 adds provenance-bound
model-language integration without collapsing engine analysis, participant evidence,
learner hypotheses, and authored language into one opaque authority.

## Documentation map

- [Milestone handoff](STATUS.md) — completed M17–M19 package summary, qualification evidence, operations, and next priorities.
- [Current build status](docs/product/repository-build-status.md) — moving milestone and qualification authority.
- [CONTEXT.md](CONTEXT.md) — contributor orientation and authority boundaries.
- [M13 persistent tutor CLI](docs/runbooks/m13-persistent-tutor-cli.md) — replay-verified tutor workflow.
- [M14 engine analysis CLI](docs/runbooks/m14-engine-analysis-cli.md) — objective engine-backed analysis package.
- [M15 evaluation presentation](docs/runbooks/m15-evaluation-presentation.md) — deterministic display projection.
- [M16 grounded mentor feedback](docs/runbooks/m16-grounded-mentor-feedback.md) — deterministic evidence-bound feedback.
- [M17 analysis presentation bridge](docs/runbooks/m17-analysis-presentation-bridge.md) — opt-in analysis projection.
- [M18 diagnostic analysis queue](docs/runbooks/m18-diagnostic-analysis-queue.md) — bounded deterministic diagnostic batching.
- [M19 provenance-bound model coaching](docs/runbooks/m19-provenance-bound-model-coaching.md) — provider-neutral model-language boundary.
- [Decision records](docs/decisions/README.md) — normative bounded contracts.
- [Product build plan](docs/product/chess-mentor-engine-repository-build-plan.md) — planning history and broader direction.
