# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, participant self-report, analyst/model interpretation, model-output
evaluation, tutoring, and pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
```

The third question is a product hypothesis, not a claim that the system has
established a causal cognitive mechanism.

Use [current build status](docs/product/repository-build-status.md) as the moving
implementation/qualification authority and [STATUS.md](STATUS.md) as the completed
M20–M22 milestone handoff. Historical details remain in feature PRs, architecture
records, ADRs, runbooks, and Git history. Frozen research protocols and pilot
artifacts are not superseded by software qualification.

## Current implementation

The bounded evidence stack is qualified through M22:

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
- **M19:** provider-neutral model-language rendering over a content-addressed
  request containing exact recomputed M16 grounding plus a fingerprinted authority
  ceiling. Accepted prose is recorded through M8 with explicit model provenance.
- **M20:** content-addressed model-output evaluation over exact M16/M19 sources with
  seven frozen quality dimensions, evaluator provenance, pass/fail/unclear verdicts,
  and an explicit `truth_status = not_established_by_m20_evaluation` ceiling.
- **M21:** participant-authorized orchestration from one exact selected M18 candidate
  into native M5 decision context and an initial M8 tutor session, with candidate
  selection and capture consent represented separately.
- **M22:** hermetic end-to-end fidelity qualification across M3/M4 -> M15 -> M16 ->
  M19 -> M20 for exact, bounded, mate, partial, unavailable, compatible,
  incompatible, and failed evidence regimes. M22 introduces no runtime authority.

Recent promotion sequence:

```text
M19 Provenance-Bound Mentor Coaching            MERGED - PR #51
M20 Model Coaching Evaluation Contract          MERGED - PR #53
M21 Candidate-to-Tutor Orchestration            MERGED - PR #54
M22 End-to-End Evaluation Fidelity Matrix       MERGED - PR #55
```

M22 qualified at exact head
`10e7dac9ef0b6ebafce9b5d307ec99e1fd254ca5` in CI run `34484791539`: 648
native tests passed with 8 intentional external-engine skips, Ruff passed, and the
independent Stockfish witness passed 8/8. It merged as
`7f59c6add7ffe042d8c2b65d6273867673b6d74b`.

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
must preserve canonical White evaluation, reverse ordering bounds when perspective
reverses, keep mate symbolic, preserve fingerprints/provenance, and fail closed on
evidence drift. M17 exposes this exact projector from the M14 CLI.

**Feedback-composition authority:** M16 may turn already-qualified M15/M6 and
optional complete active-current M7 evidence into deterministic session-local
feedback. It verifies exact M3/M4 references already bound into the tutor session,
preserves every M6 assertion and attached active M7 revision, and keeps non-exact
objective evidence non-exact. M16 does not invoke a model.

**Model-language authority:** M19 may ask an external provider to render prose from
an exact content-addressed M16 grounding request. The provider result contains only
request identity/fingerprint echo, prose, provider/model identity, run ID, and
chronology. It cannot replace M3/M4/M6/M7/M9 structured authority through the M19
contract. M19 records `request_bound_not_semantically_verified` explicitly.

**Model-output-evaluation authority:** M20 may record a complete set of bounded
pass/fail/unclear judgments against a frozen seven-dimension policy after
mechanically revalidating the exact M16/M19 source chain. Evaluator provenance is
preserved. M20 acceptance does not make evaluator judgments objective chess truth;
records retain `truth_status = not_established_by_m20_evaluation`.

**Candidate-to-session orchestration authority:** M21 may record explicit
participant candidate selection and capture consent, verify exact M18 candidate/batch
and canonical-game provenance, derive deterministic position context, and create
only M5 decision context plus initial M8 `state=selected`. M21 cannot choose a
candidate, create M6/M7 inference, select training, or generate coaching.

**Participant-evidence authority:** raw/frozen player responses and exposure state
remain distinct from objective engine evidence. Diagnostic rationale shown before
capture can contaminate the M5/M8 pre-reveal measurement boundary; M21 software
qualification does not prove what an external UI actually displayed.

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

**Cross-layer qualification authority:** M22 tests whether already-qualified source
semantics survive covered layer boundaries. Its matrix is regression evidence, not
an alternate chess evaluator and not production/pedagogical validation.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
M21 orchestration != learner inference
M22 fidelity qualification != production/pedagogical validation
```

M14 owns the engine-backed evidence package. M15 owns only deterministic projection
of exact M3/M4 records. M17 exposes that projection from the same M14 analysis path.
M18 orchestrates qualified M4 diagnostic selection. M16 owns deterministic grounded
composition from exact objective records plus existing M6/M7 evidence. M19 adds
model-authored language without granting new structured evidence authority. M20 adds
inspectable evaluator judgments without promoting them to truth. M21 connects exact
selected evidence to the existing participant-evidence tutor path without creating
new inference. M22 qualifies covered end-to-end fidelity invariants.

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

M17 adds:

```text
cme analyze ... --with-presentation
```

Optional M14 archival still stores only `m14.analysis-package.v1`.

M15, M16, M19, M20, and M21 remain Python APIs. M20–M22 introduced no new CLI
command.

Key newer APIs:

```python
from chess_mentor_engine.coaching import (
    build_model_coaching_request,
    bind_model_coaching_response,
    build_model_coaching_evaluation_request,
    bind_model_coaching_evaluation,
    run_model_coaching_evaluation,
)
from chess_mentor_engine.tutoring import (
    record_candidate_tutor_authorization,
    start_candidate_tutor_session,
)
```

M19 deliberately does not freeze a production LLM provider or transport. M20 does
not freeze a production evaluator. An application may implement the provider
protocols while exact requests/results remain provider-neutral.

M13's `cme tutor explain` command remains an explicit-input explanation surface; it
is not silently replaced by M16/M19/M20. M21 currently has no CLI bridge into the
persistent M13 workflow.

## Development and qualification

The repository merge gate is exercised by pull-request CI:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`; skipped external-engine tests
are not a successful independent witness. No standalone static Python type checker
is configured.

Focused current milestone suites:

```bash
python -m pytest tests/test_m20_model_coaching_evaluation.py
python -m pytest tests/test_m21_diagnostic_candidate_tutor_orchestration.py
python -m pytest tests/test_m22_end_to_end_evaluation_fidelity.py
```

For the full mentor/evaluation lineage:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py
```

## Current claim ceiling and stop boundary

The repository can preserve longitudinal evidence history, expose qualified local
analysis/tutor surfaces, produce diagnostic queues, project exact engine evidence,
compose deterministic grounded feedback, bind model-authored language to exact
provenance, record bounded evaluator judgments, launch an explicitly selected
candidate into M5/M8, and qualify covered cross-layer fidelity. It still does
**not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatic M7/M11 mutation from tutoring, analysis, or model coaching;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, credentials/transport/retry architecture, or
  provider quality claim;
- correct participant disclosure/consent behavior in an external UI;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M16 remains the deterministic factual grounding ceiling. M19 proves provenance-bound
model-language integration, not model quality. M20 records bounded evaluation, not
truth. M21 is orchestration, not inference. M22 is regression qualification, not
production validation.

The completed M20–M22 milestone and recommended next priorities are recorded in
[STATUS.md](STATUS.md). A future milestone should re-audit live `main` before
creating a new package queue.

## Research and product hypotheses

The broader product hypothesis remains a persistent tutor that learns from a
player's decision evidence over time and chooses bounded practice based on
inspectable support, contradiction, and outcomes. Implemented software contracts do
not settle the full production architecture or validate tutoring benefit.

See [product discovery](docs/product/product-discovery.md),
[product definition](docs/product/product-definition.md), the frozen research
artifacts under `docs/research/`, and the
[repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md).
