# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, participant self-report, learner inference, tutoring, model-authored
language, model-output evaluation, and pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
```

The third question remains a bounded product hypothesis, not a claim that the system
has established a causal cognitive mechanism.

Use [current build status](docs/product/repository-build-status.md) as the moving
implementation/qualification authority and [STATUS.md](STATUS.md) as the completed
M23–M25 milestone handoff. Historical detail remains in feature PRs, architecture
records, ADRs, runbooks, Git history, and frozen research artifacts.

## Current implementation

The bounded stack is qualified through M25:

- **M1–M4:** canonical PGN/game/position provenance, deterministic chess context and
  features, normalized UCI evidence, objective played-decision comparison, and
  bounded diagnostic candidate selection.
- **M5–M7:** frozen participant decision evidence, position-local discrepancy facts
  and assessments, participant-specific descriptive learner hypotheses,
  contradiction/challenge evidence, recurrence policies, and append-only lifecycle.
- **M8–M10:** controlled evidence-aware tutoring, explicit hypothesis/intervention
  applicability and conservative training selection, then separate
  practice/near/far/real-game outcome evidence.
- **M11:** append-only longitudinal learner state bound to exact current M7 revisions
  and optional same-revision M10 evidence.
- **M12–M14:** local evidence/artifact inspection, replay-verified persistent tutor
  transitions, and bounded engine-backed analysis.
- **M15:** deterministic evaluation presentation with explicit White and
  decision-mover perspectives, bounds, symbolic mate, evidence quality, PVs, engine
  provenance, and exact references.
- **M16:** deterministic grounded session-local mentor feedback over exact M15/M6 and
  optional complete active-current M7 evidence. M16 remains the deterministic factual
  grounding ceiling for mentor language.
- **M17:** opt-in `cme analyze --with-presentation` bridge over exact in-memory M14
  records through M15.
- **M18:** `cme diagnose`, which analyzes an explicit played-ply window and applies an
  explicit versioned M4 selection policy to produce an auditable candidate/control
  batch.
- **M19:** provider-neutral model-language rendering over an exact content-addressed
  M16 grounding request. Accepted prose remains
  `request_bound_not_semantically_verified`.
- **M20:** bounded model-output evaluation over exact M16/M19 sources with seven
  frozen dimensions and
  `truth_status = not_established_by_m20_evaluation`.
- **M21:** explicit participant candidate selection + separate capture consent,
  followed by exact M18-to-M5/M8 orchestration into only initial M8 `state=selected`.
- **M22:** hermetic cross-layer fidelity qualification for exact, bounded, mate,
  partial, unavailable, compatible, incompatible, and failed evidence regimes.
- **M23:** installed `cme-candidate-tutor` operator that closes the local seam from an
  exact M18 queue through native M21 into atomic M5/M8 persistence and verified M13
  replay. The former “M21 has no persistent CLI bridge” gap is closed.
- **M24:** provider/evaluator execution conformance around M19/M20 with detached
  immutable requests, explicit endpoint identity, deterministic execution provenance,
  and fail-closed failure classification. No vendor or retry policy is selected.
- **M25:** content-addressed authority-separated coach-review read model plus local
  `cme-coach-review` inspection. It preserves already-qualified layers rather than
  creating new evidence or a production interface.

Recent promotion sequence:

```text
M22 End-to-End Evaluation Fidelity Matrix       MERGED - PR #55
M23 Diagnostic-to-Persistent-Tutor Bridge       MERGED - PR #57
M24 Provider / Evaluator Execution Conformance  MERGED - PR #58
M25 Coach Review Read Model                     MERGED - PR #59
```

M25 qualified at exact head
`9927171cb5f09bf0274d0e2c36e9ab736a90baee` in CI run `34502823382`: 709 native
tests passed with 8 intentional external-engine skips, Ruff passed, and the separate
Stockfish integration job passed. It merged as
`13db09f7cf4c066c49988875e89760ce204c2515`.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board
state, legal actions, exact source provenance, and qualified low-level features.
Engine providers supply versioned evaluation/PV evidence with explicit
partial/bounded/failure states. M4/M15 preserve mate, terminal, inversion, bound, and
compatibility semantics instead of manufacturing a universal human-readable score.

**Diagnostic-selection authority:** M4 owns explicit versioned selection policy and
deterministic candidate/control batching. M18 orchestrates that contract over a game
window. Neither M18 nor M23 silently chooses a candidate for the participant.

**Participant-authorization authority:** M21 records candidate selection and
capture-consent as distinct participant decisions. M23 operationalizes and persists
that exact contract; it does not infer consent, infer a PGN identity mapping, or grant
learner-inference authority.

**Participant-evidence authority:** raw/frozen player responses and exposure state
remain distinct from engine evidence. Diagnostic rationale shown before capture can
contaminate the M5/M8 pre-reveal measurement boundary. Software qualification does
not prove what a future UI displayed to a participant.

**Presentation authority:** M15 projects exact M3/M4 evidence without changing its
semantics. M25 may copy that already-qualified presentation into an application read
model, but M25 cannot reinterpret scores or merge objective evidence with model prose.

**Learning-inference authority:** M6/M7 describe bounded position-local discrepancies
and participant-specific recurring hypotheses. Recurrence is not a causal cognitive
mechanism, permanent trait, or automatic training eligibility.

**Feedback-composition authority:** M16 turns already-qualified M15/M6 and optional
complete active-current M7 evidence into deterministic session-local feedback. It
does not invoke a model and remains the factual grounding ceiling.

**Model-language authority:** M19 may ask a provider to render prose from the exact
M16 request. Provenance establishes which request reached which model run; it does
not establish semantic correctness, safety, or pedagogical effectiveness.

**Execution-conformance authority:** M24 may normalize execution behavior around
M19/M20, enforce detached requests and endpoint identity, and classify failures. It
cannot choose a vendor, grant automatic retry authority, create chess/learner facts,
or establish semantic truth.

**Model-output-evaluation authority:** M20 may record bounded pass/fail/unclear
judgments under its seven-dimension policy. M20 acceptance is not objective chess
truth. M25 preserves that distinction rather than flattening evaluation into facts.

**Pedagogy/outcome authority:** M9 selects only through explicit versioned
applicability rules. M10 measures bounded outcome/transfer evidence under a
predeclared protocol. Practice completion, successful performance, transfer,
causality, and mastery remain different claims.

**Application/persistence authority:** deterministic code owns sequencing, exact
identities, participant scope, integrity checking, replay, and append-only local
storage. M23 adds an atomic operator bridge; checksums remain integrity mechanisms,
not signatures, and participant filtering is not authentication.

**Application read-model authority:** M25 organizes exact source records for a future
UI under frozen section boundaries. Missing downstream layers remain `null`; M25 does
not synthesize evidence or make production-UX claims.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != learner inference
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
participant selection != capture consent
M23 operator/persistence != M6/M7/M9 authority
M24 execution conformance != vendor approval or semantic truth
M25 read model != production UI or new evidence authority
```

## CLI and API boundaries

The project is a Python 3.11+ package. Installed commands include:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
```

`cme position packet` remains deterministic and engine-free. `cme analyze` and
`cme diagnose` require an explicit external UCI executable or PATH name. M18 also
requires an explicit JSON M4 `SelectionPolicy`.

M23 adds `cme-candidate-tutor`; it consumes an exact M18 diagnostic JSON document,
exact PGN, explicit participant selection/consent, capture protocol/prompts, and a
local artifact DB. It invokes no model and no engine.

M25 adds `cme-coach-review`; it reads a strict local M25 bundle and produces the
content-addressed authority-separated read model. It performs no engine/provider
calls and no persistence mutation.

M24 remains a Python API. Key execution surfaces include:

```python
from chess_mentor_engine.coaching import (
    ModelCoachEndpoint,
    ModelEvaluatorEndpoint,
    execute_model_coach_provider,
    execute_model_coaching_evaluator,
    run_conformant_model_coaching,
    run_conformant_model_coaching_evaluation,
)
```

The original M19/M20 build/bind APIs remain available. A future application may
implement neutral adapters against M24 while live credentials/vendor choices remain
external.

M13's `cme tutor explain` remains an explicit-input explanation transition. M23 does
not silently replace that command with M16/M19/M20 generation.

## Development and qualification

Focused current milestone suites:

```bash
python -m pytest tests/test_m23_diagnostic_to_persistent_tutor_cli.py
python -m pytest tests/test_m24_provider_conformance.py
python -m pytest tests/test_m25_coach_review_read_model.py
```

The repository merge gate is:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not a successful independent-engine witness. Pull-
request CI remains the merge authority. No standalone static Python type checker is
configured.

See the consolidated
[M23–M25 milestone runbook](docs/runbooks/m23-m25-milestone-runbook.md).

## Current claim ceiling and stop boundary

The repository can preserve longitudinal evidence history, expose qualified local
analysis/tutor surfaces, create diagnostic queues, persist an explicitly authorized
diagnostic candidate into M5/M8, compose deterministic grounded feedback, execute
provider/evaluator adapters through a neutral conformance seam, record bounded model
output evaluation, and project those exact layers into an application-facing review
model. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatic M7/M11 mutation from tutoring, analysis, or model coaching;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary evaluator;
- a production LLM/evaluator provider, credential/transport/retry architecture, or
  provider-quality claim;
- correct participant disclosure/consent behavior in an external UI;
- production UI usability, accessibility, localization, or visual correctness;
- hosted authentication/authorization, multi-user persistence, production
  observability, or deployment readiness;
- empirical tutoring efficacy.

The completed M23–M25 milestone, qualification evidence, deferred human/external
gates, and recommended next directions are recorded in [STATUS.md](STATUS.md). A
future milestone should re-audit live `main` before creating a new package queue.

## Research and product hypotheses

The broader product hypothesis remains a persistent tutor that learns from a
player's decision evidence over time and chooses bounded practice based on
inspectable support, contradiction, and outcomes. Implemented software contracts do
not settle the full production architecture or validate tutoring benefit.

See [product discovery](docs/product/product-discovery.md),
[product definition](docs/product/product-definition.md), the frozen research
artifacts under `docs/research/`, and the
[repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md).
