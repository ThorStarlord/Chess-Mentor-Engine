# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert objective chess evidence into individualized teaching decisions without collapsing chess truth, participant self-report, learner inference, tutoring, model-authored language, model-output evaluation, review presentation, execution mechanics, and pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
What did deterministic grounding say versus what a model rendered?
What execution/review mechanics were verified versus what still requires human/external authority?
```

The learner-model questions remain bounded product hypotheses, not claims that the system has established causal cognitive mechanisms.

Use [current build status](docs/product/repository-build-status.md) as the moving implementation/qualification authority, [STATUS.md](STATUS.md) as the completed M29–M31 milestone handoff, and [the M29–M31 runbook](docs/runbooks/m29-m31-milestone-runbook.md) for restart and qualification commands.

## Current implementation

The bounded stack is qualified through M31:

- **M1–M4:** canonical PGN/game/position provenance, deterministic chess context/features, normalized UCI evidence, objective played-decision comparison, and bounded diagnostic selection.
- **M5–M7:** frozen participant decision evidence, position-local discrepancy facts/assessments, participant-specific descriptive learner hypotheses, contradiction/challenge evidence, recurrence policies, and append-only lifecycle.
- **M8–M11:** controlled evidence-aware tutoring, explicit intervention applicability/selection, bounded practice/transfer outcome evidence, and append-only longitudinal learner state.
- **M12–M14:** local evidence/artifact inspection, replay-verified persistent tutor transitions, and bounded engine-backed analysis.
- **M15:** deterministic evaluation presentation with explicit White and decision-mover perspectives, bounds, symbolic mate, evidence quality, PVs, engine provenance, and exact references.
- **M16:** deterministic grounded mentor feedback over exact M15/M6 and optional complete active-current M7 evidence. M16 remains the deterministic factual grounding ceiling for mentor language.
- **M17:** opt-in `cme analyze --with-presentation` bridge over exact in-memory M14 records through M15.
- **M18:** `cme diagnose`, which analyzes an explicit played-ply window and applies an explicit versioned M4 selection policy to produce an auditable candidate/control batch.
- **M19:** provider-neutral model-language rendering over an exact content-addressed M16 grounding request. Accepted prose remains request-bound rather than semantically proven.
- **M20:** bounded model-output evaluation over exact M16/M19 sources with seven frozen dimensions and `truth_status = not_established_by_m20_evaluation`.
- **M21–M23:** explicit participant candidate selection + separate capture consent, exact M18-to-M5/M8 orchestration, and installed `cme-candidate-tutor` persistence/replay bridge.
- **M22:** hermetic cross-layer fidelity qualification across exact, bounded, mate, partial, unavailable, compatible, incompatible, and failed evidence regimes.
- **M24:** provider/evaluator execution conformance with detached immutable requests, explicit endpoint identity, deterministic execution provenance, and fail-closed failure classification. No vendor or automatic retry policy is selected.
- **M25:** content-addressed authority-separated coach-review read model plus local `cme-coach-review` inspection.
- **M26:** persistent reviewed-coaching operator from an exact replay-verified `compared` M8 checkpoint through M16, optional M19/M20 via M24-compatible application adapters, M25 assembly, and atomic append-only persistence.
- **M27:** privacy-bounded execution ledger and mechanical fidelity verification for persisted M26 runs.
- **M28:** deterministic static semantic HTML reference surface over a strict M25 read model; not a production UI.
- **M29:** installed `cme-persisted-coach-review-reference` bridge that starts from a persisted M26 run or M25 review, requires M27 verification, and renders the persisted M25 payload through M28 without a hand-built bundle.
- **M30:** installed `cme-participant-review` list/show/export tooling plus content-addressed participant review package manifests. Summary navigation excludes source payloads/model prose/evaluator rationale/participant responses/HTML unless exact content is explicitly requested.
- **M31:** hermetic synthetic-canary privacy and manual-retry-history preflight around M24/M26/M27. It accepts only `CME_TEST_CANARY_*` markers, preserves `automatic_retry=false`, validates but never executes retry histories, and stores only summary-safe evidence.

Recent promotion sequence:

```text
M26 Persistent Reviewed-Coaching Operator                MERGED - PR #61
M27 Reviewed-Coaching Execution Ledger                  MERGED - PR #62
M28 Local Coach-Review Reference Surface                MERGED - PR #63
M29 Persisted Review -> Reference Surface Bridge        MERGED - PR #65
M30 Participant-Scoped Review Package & Navigation      MERGED - PR #66
M31 Execution-Envelope Privacy & Retry Preflight        MERGED - PR #67
```

M31 qualified at exact head `9a82f72af93215756818b991bd3d922144cf6ca2` in CI run `34546266117`: 774 native tests passed with 8 intentional external-engine skips, Ruff passed, and the independent Stockfish job passed. It merged as `6bd84881204e543f4cfe8906aa7cc15e894fc794`.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board state, legal actions, exact source provenance, and qualified low-level features. Engine providers supply versioned evaluation/PV evidence with explicit partial/bounded/failure states. M4/M15 preserve mate, terminal, inversion, bound, and compatibility semantics instead of manufacturing universal move-quality labels.

**Diagnostic-selection authority:** M4 owns explicit versioned selection policy and deterministic candidate/control batching. M18 orchestrates that contract over a game window. Neither M18 nor M23 silently chooses a candidate for the participant.

**Participant-authorization authority:** M21 records candidate selection and capture consent as distinct participant decisions. M23 operationalizes and persists that exact contract; it does not infer consent or learner state.

**Participant-evidence authority:** raw/frozen player responses and exposure state remain distinct from engine evidence. Diagnostic rationale shown before capture can contaminate the M5/M8 pre-reveal measurement boundary. Software qualification does not prove what a future UI displayed to a participant.

**Presentation authority:** M15 projects exact M3/M4 evidence without changing its semantics. M25 organizes already-qualified layers into a read model. M28 renders that read model. M29/M30 bridge, navigate, and export those exact artifacts. None may reinterpret objective evidence or turn model prose into facts.

**Learning-inference authority:** M6/M7 describe bounded position-local discrepancies and participant-specific recurring hypotheses. Recurrence is not a causal cognitive mechanism, permanent trait, or automatic training eligibility.

**Feedback-composition authority:** M16 turns already-qualified M15/M6 and optional complete active-current M7 evidence into deterministic session-local feedback. It does not invoke a model and remains the factual grounding ceiling.

**Model-language authority:** M19 may ask a provider to render prose from the exact M16 request. Provenance establishes which request reached which model run; it does not establish semantic correctness, safety, or pedagogical effectiveness.

**Execution-conformance authority:** M24 classifies one adapter invocation, enforces detached requests/endpoint identity, and always records `automatic_retry=false`. M31 may validate synthetic-canary leakage and an already-supplied manual retry history. Neither chooses a production vendor, executes retries, approves secrets handling, or establishes semantic truth.

**Model-output-evaluation authority:** M20 records bounded pass/fail/unclear judgments under its frozen policy. M20 acceptance is not objective chess truth. M25/M28/M30 must preserve that distinction.

**Persistence/review authority:** M26 atomically persists reviewed-coaching outputs without advancing M8. M27 verifies exact persisted mechanics. M29 resolves persisted review chains. M30 provides participant-scoped navigation/export. Participant scoping is an integrity boundary, not hosted authentication.

**Pedagogy/outcome authority:** M9 selects only through explicit versioned applicability rules. M10 measures bounded outcome/transfer evidence under a predeclared protocol. Practice completion, successful performance, transfer, causality, and mastery remain different claims.

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
M24 execution conformance != vendor approval or retry authority
M25 read model != production UI or new evidence authority
M27 mechanically_verified != semantic truth
M28 static reference surface != production UI/accessibility/usability approval
M29 persisted bridge != new review/evidence authority
M30 participant navigation != authentication or privacy approval
M31 retry-history validation != retry execution or production retry policy
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
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

`cme position packet` remains deterministic and engine-free. `cme analyze` and `cme diagnose` require an explicit external UCI executable or PATH name. M18 also requires an explicit JSON M4 `SelectionPolicy`.

M29 consumes an existing local artifact DB plus an exact participant-scoped M26 run or M25 review and writes a new M28 HTML file after M27 verification.

M30 lists/shows/exports participant-scoped review artifacts. Summary navigation is intentionally content-minimal; exact payloads require `--include-content` and export directories are non-overwriting.

M31 remains a Python API. Its principal surface is:

```python
from chess_mentor_engine.execution_envelope_preflight import (
    build_execution_envelope_preflight,
)
```

M31 accepts only synthetic canaries. Never pass production credentials to it.

M13's `cme tutor explain` remains an explicit-input explanation transition. M26 does not silently replace that command with M16/M19/M20 generation or advance M8 state.

## Development and qualification

Focused current milestone suites:

```bash
python -m pytest tests/test_m29_persisted_review_reference_bridge.py -rs
python -m pytest tests/test_m30_participant_review_package_navigation.py -rs
python -m pytest tests/test_m31_execution_envelope_preflight.py -rs
```

The repository merge gate is:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not a successful independent-engine witness. Pull-request CI remains the merge authority. No standalone static Python type checker is configured.

See the consolidated [M29–M31 milestone runbook](docs/runbooks/m29-m31-milestone-runbook.md).

## Current claim ceiling and stop boundary

The repository can preserve longitudinal evidence history, expose qualified local analysis/tutor surfaces, create diagnostic queues, persist an explicitly authorized diagnostic candidate into M5/M8, compose deterministic grounded feedback, execute application-owned provider/evaluator adapters through a neutral conformance seam, record bounded model-output evaluation, persist and mechanically verify reviewed coaching, deterministically render persisted review state, navigate/export participant-scoped review packages, and validate hermetic synthetic-canary/manual-retry histories. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatic M7/M11 mutation from tutoring, analysis, or model coaching;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary evaluator;
- a production LLM/evaluator provider, credential/transport/retry architecture, or provider-quality claim;
- production privacy/security approval or live secret-management correctness;
- correct participant disclosure/consent behavior in an external UI;
- production UI usability, accessibility, localization, browser/device compatibility, or visual correctness;
- hosted authentication/authorization, multi-user production persistence, observability, deployment readiness, or empirical tutoring efficacy.

The completed M29–M31 queue ends here. Future work should begin with a fresh live-main audit and a new bounded package queue rather than treating the handoff recommendations as pre-approved implementation authority.