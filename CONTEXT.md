# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, participant self-report, analyst/model interpretation, tutoring, and
pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
```

The third question is a product hypothesis, not a claim that the system has
established a causal cognitive mechanism.

Use [current build status](docs/product/repository-build-status.md) as the moving
implementation/qualification authority. Historical milestone details remain in
architecture records, ADRs, runbooks, and Git history. Frozen research protocols
and pilot artifacts are not superseded by software qualification.

## Current implementation

The bounded evidence stack now extends through the M19 candidate:

- **M1-M4:** canonical PGN/game/position provenance, deterministic chess context and
  features, normalized UCI evidence, objective played-decision comparison, and
  bounded diagnostic candidate selection.
- **M5-M7:** frozen participant decision evidence, position-local discrepancy facts
  and assessments, participant-specific descriptive learner hypotheses,
  contradiction/challenge evidence, recurrence policies, and append-only lifecycle.
- **M8-M10:** controlled evidence-aware tutoring, explicit hypothesis/intervention
  applicability and conservative training selection, then separate
  practice/near/far/real-game outcome evidence.
- **M11:** append-only longitudinal learner state bound to exact current M7
  revisions and optional same-revision M10 evidence.
- **M12:** installed read-only `cme` surface for deterministic PGN inspection,
  engine-free position packets, and verified participant-scoped artifact reads.
- **M13:** persistent `cme tutor ...` workflow. Every write verifies and replays the
  exact prior M8 checkpoint, applies one existing state transition, and appends a
  successor checkpoint.
- **M14:** bounded `cme analyze` workflow over qualified M3/M4 contracts with
  optional participant-scoped archival of the exact analysis package.
- **M15:** deterministic presentation projection over exact M3/M4 records with
  explicit score perspective, bound direction, symbolic mate, evidence quality,
  engine provenance, PVs, and evidence references.
- **M16:** deterministic grounded mentor-feedback composition after an exact M8/M6
  comparison, optionally retaining complete active-current M7 context. M16 remains
  the deterministic factual grounding ceiling for mentor language.
- **M17:** opt-in `cme analyze --with-presentation` bridge from exact in-memory M14
  analysis/comparison records through M15 without changing the M14 archive.
- **M18:** `cme diagnose`, which analyzes an explicit played-ply window and applies
  an explicit versioned M4 selection policy to produce an auditable deterministic
  candidate/control batch.
- **M19 candidate:** provider-neutral model-language rendering over a content-
  addressed request that contains the exact recomputed M16 grounding and a
  fingerprinted authority ceiling. Accepted prose is recorded through the existing
  M8 explanation transition with explicit model provenance.

Recent promotion sequence:

```text
M16 Grounded Mentor Feedback Composer  MERGED - PR #48
M17 Analysis-to-Presentation Bridge    MERGED - PR #49
M18 Diagnostic Move-Analysis Queue     MERGED - PR #50
M19 Provenance-Bound Mentor Coaching   CURRENT CANDIDATE - PR #51
```

M18 qualified at exact head
`65297abd366bf092a60ed4fa202e2e51bb1950cd` in CI run `34436086912`: 589
native tests passed with 8 intentional external-engine skips, Ruff passed, and the
independent Stockfish witness passed 8/8. It merged as
`00bab82dc963bff005c9753b498f1e50a8c513d4`. PR #51 and Git history are the
authority for M19 candidate-head qualification and eventual merge provenance.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board
state, legal actions, exact source provenance, and qualified low-level features.
Engine providers supply versioned evaluation/PV evidence with explicit
partial/bounded/failure states. M4 comparisons preserve mate, terminal, inversion,
and compatibility semantics instead of manufacturing a universal human-readable
score.

**Diagnostic-selection authority:** M4D owns explicit versioned policy application
and deterministic candidate/control batching. M18 orchestrates that existing
contract over a selected game window. M18 does not redefine thresholds, pad
shortfalls, or promote failed/partial/incompatible evidence into exact scores.

**Presentation authority:** M15 may project exact M3/M4 evidence into an explicit
read model, including a decision-mover score view and evidence-quality labels. It
must preserve the canonical White evaluation, reverse ordering bounds when the
perspective reverses, keep mate symbolic, preserve fingerprints/provenance, and
fail closed on evidence drift. M17 exposes this exact projector from the M14 CLI.

**Feedback-composition authority:** M16 may turn already-qualified M15/M6 and
optional complete active-current M7 evidence into deterministic session-local
feedback. It verifies exact M3/M4 references already bound into the tutor session,
preserves every M6 assertion and every attached active M7 revision, and keeps
non-exact objective evidence non-exact. M16 does not invoke a model.

**Model-language authority:** M19 may ask an external provider to render prose from
an exact content-addressed M16 grounding request. The provider result contains only
request identity/fingerprint echo, prose, provider/model identity, run ID, and
chronology. It cannot replace M3/M4/M6/M7/M9 structured authority through the M19
contract. Provenance binding does not prove that arbitrary model prose is correct;
M19 records `request_bound_not_semantically_verified` explicitly.

**Participant-evidence authority:** raw/frozen player responses and their exposure
state remain distinct from objective engine evidence. Later structured coding does
not silently replace raw self-report.

**Learning-inference authority:** M6/M7 describe bounded position discrepancies and
participant-specific recurring hypotheses. Recurrence is not a causal cognitive
mechanism, permanent trait, or automatic training eligibility.

**Pedagogy/outcome authority:** M9 selects only through explicit versioned
applicability rules. M10 measures bounded outcome/transfer evidence under a
predeclared protocol. Practice completion, successful exercise performance,
transfer, causality, and mastery remain different claims.

**Application/persistence authority:** deterministic code owns sequencing, exact
identities, participant scope, integrity checking, replay, and append-only storage.
Checksums are integrity mechanisms, not signatures; participant filtering is not
authentication.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
request provenance != semantic correctness of model prose
```

M14 owns the engine-backed evidence package. M15 owns only a deterministic
projection of exact M3/M4 records. M17 exposes that projection from the same M14
analysis path. M18 orchestrates the existing qualified M4 diagnostic-selection
contracts. M16 owns deterministic grounded composition from exact objective records
plus existing M6/M7 evidence. M19 adds model-authored language without granting the
model new structured evidence authority.

## CLI and API boundaries

The project is a Python 3.11+ package with an installed `cme` command. Current
bounded commands include:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
```

`cme position packet` remains deterministic and engine-free. `cme analyze` and
`cme diagnose` require an explicit external UCI executable or PATH name. M18 also
requires an explicit JSON M4 `SelectionPolicy`.

M17 adds an opt-in presentation projection to the existing analysis command:

```text
cme analyze ... --with-presentation
```

Optional M14 archival still stores only `m14.analysis-package.v1`.

M15, M16, and M19 remain Python APIs:

```python
from chess_mentor_engine.presentation import build_evaluation_presentation
from chess_mentor_engine.feedback import (
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)
from chess_mentor_engine.coaching import (
    ModelCoachingGeneration,
    build_model_coaching_request,
    bind_model_coaching_response,
    record_model_coaching_response,
    run_model_coaching,
)
```

M19 deliberately does not freeze a production LLM provider or transport. An
application may implement `ModelCoachProvider` or perform the request/generation
steps separately. The exact request and accepted result stay provider-neutral.

M13's `cme tutor explain` command remains an explicit-input explanation surface; it
is not silently replaced by M16 or M19.

## Development and qualification

The repository merge gate is exercised by pull-request CI:

```bash
python -m pytest -rs
python -m ruff check .
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`; skipped external-engine tests
are not a successful witness. Repository documentation also recommends
`python -m compileall -q src tests` as a local syntax check. No standalone static
Python type checker is configured.

Focused current surface suites include:

```bash
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
python -m pytest tests/test_m16_grounded_mentor_feedback.py
python -m pytest tests/test_m17_analysis_presentation_bridge.py
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
```

## Current claim ceiling and stop boundary

The repository can preserve a longitudinal evidence history, expose qualified local
analysis/tutor surfaces, produce deterministic diagnostic queues, project exact
engine evidence for display, compose deterministic grounded feedback, and bind
model-authored language to exact grounding/instruction/model provenance. It still
does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatic M7/M11 mutation from tutoring, analysis, or model coaching;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- a production LLM provider, credentials/transport/retry architecture, or provider
  quality claim;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M16 remains the deterministic factual grounding ceiling. M19 proves provenance-
bound model-language integration, not model quality.

## Research and product hypotheses

The broader product hypothesis remains a persistent tutor that learns from a
player's decision evidence over time and chooses bounded practice based on
inspectable support, contradiction, and outcomes. Implemented software contracts do
not settle the full production architecture or validate tutoring benefit.

See [product discovery](docs/product/product-discovery.md),
[product definition](docs/product/product-definition.md), the frozen research
artifacts under `docs/research/`, and the
[repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md).
