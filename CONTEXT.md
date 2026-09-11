# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
>  
> **Latest completed milestone handoff:** [`STATUS.md`](STATUS.md)  
> **Repository overview:** [`README.md`](README.md)  
> **Architecture map:**
> [`docs/architecture/architecture.md`](docs/architecture/architecture.md)

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, participant self-report, learner inference, tutoring, deterministic
feedback, model-authored language, model-output evaluation, review mechanics, and
pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
What did deterministic grounding say versus what a model rendered?
What execution/review mechanics were verified versus what still requires human/external authority?
What later evidence supports practice success, transfer, or longitudinal change?
```

Learner-model conclusions remain bounded product hypotheses, not claims that the
system has established causal cognitive mechanisms.

## Current implementation boundary

The repository is qualified through **M34 — Hermetic Reviewed-Coaching Recovery
Reconciliation**. The latest completed milestone is M32–M34.

Use `docs/product/repository-build-status.md` for the moving implementation boundary
and exact promotion evidence. Use `STATUS.md` for the completed M32–M34 handoff and
`docs/runbooks/m32-m34-milestone-runbook.md` for restart and qualification commands.

### Capability sequence

- **M1–M4:** canonical PGN/game/position provenance, deterministic chess
  context/features, normalized UCI evidence, objective played-decision comparison,
  and bounded diagnostic selection.
- **M5–M7:** frozen participant decision evidence, position-local discrepancy facts
  and assessments, participant-specific learner hypotheses, contradiction/challenge
  evidence, recurrence policies, and append-only hypothesis lifecycle.
- **M8–M11:** controlled evidence-aware tutoring, explicit intervention
  applicability/selection, bounded practice/transfer evidence, and append-only
  longitudinal learner state.
- **M12–M18:** local evidence/artifact inspection, replay-verified persistent tutor
  transitions, engine-backed analysis, deterministic evaluation presentation,
  grounded mentor feedback, analysis-to-presentation bridging, and diagnostic move
  analysis queues.
- **M19–M22:** provider-neutral model-language rendering, bounded model-output
  evaluation, participant-authorized candidate-to-tutor launch, and hermetic
  cross-layer fidelity qualification.
- **M23–M27:** installed diagnostic-to-persistent-tutor bridging, provider/evaluator
  execution conformance, authority-separated coach review, persistent reviewed
  coaching, and a mechanically verified execution ledger.
- **M28–M31:** deterministic local review rendering, persisted-review bridging,
  participant-scoped package/navigation/export, and hermetic synthetic-canary/manual
  retry-history preflight.
- **M32:** persisted review delivery fidelity for exact machine consumers.
- **M33:** deterministic M16 mentor-feedback traceability to exact M15/M6/optional M7
  sources.
- **M34:** hermetic reconciliation of supplied synthetic multi-attempt M24 histories
  against an already-persisted mechanically verified M26 target.

## Current operational path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> M15 deterministic evaluation presentation
-> M18 diagnostic candidate batch
-> explicit participant candidate selection + separate capture consent
-> M23 cme-candidate-tutor
-> M21 authorization / launch
-> exact M5 PlayerDecisionContext
-> persisted replay-verifiable M8 state=selected
-> M13 tutor capture / freeze / reveal / compare workflow
-> position-local M6 discrepancy + optional bounded M7 context
-> replay-verified persisted M8 state=compared
-> M26 reviewed-coaching operator
   -> M16 deterministic grounded feedback
   -> optional M19 request / M24 provider execution / M19 coaching
   -> optional M20 request / M24 evaluator execution / M20 bounded evaluation
   -> M25 authority-separated coach-review read model
   -> atomic append-only M26 run lineage
-> M27 mechanical reviewed-coaching execution ledger
-> M29 persisted review -> M28 deterministic reference surface
-> M30 participant-scoped review package / navigation / export
-> M32 machine-readable persisted review delivery bundle
-> M33 deterministic M16 mentor-feedback trace
-> optional M31 synthetic-canary/manual-retry preflight
-> optional M34 hermetic multi-attempt recovery reconciliation
-> explicit M9 training applicability / selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

Not every application invokes every optional downstream layer. Every arrow remains an
authority boundary.

## Separation of responsibilities

### Objective chess authority

`chess/`, M3 engine evidence, M4 comparison/selection, and M15 presentation own
canonical board state, legal actions, exact source provenance, qualified low-level
features, normalized engine judgments, and score/perspective semantics. Mate,
bounds, partial results, unavailable states, terminal states, and compatibility
states are preserved rather than coerced into fake precision.

Objective chess authority does not establish player cognition, learner traits, or
pedagogical effectiveness.

### Diagnostic-selection authority

M4 owns explicit versioned selection policy and deterministic candidate/control
batching. M18 orchestrates that policy over a selected game interval. Neither M18
nor M23 silently selects a candidate for the participant.

### Participant-authorization authority

M21 records candidate selection and capture consent as distinct participant
decisions. M23 operationalizes and persists that exact contract. Candidate selection
is never evidence-capture consent.

### Participant-evidence authority

M5 raw/frozen player responses and exposure state remain distinct from engine
analysis. Diagnostic rationale revealed before capture may contaminate the pre-reveal
measurement boundary; repository qualification does not prove what a future user
interface displayed at a given moment.

### Learning-inference authority

M6 describes position-local discrepancies. M7 represents bounded
participant-specific recurring hypotheses with support, contradiction, challenge,
provenance, and lifecycle. Recurrence is not a causal cognitive mechanism, permanent
trait, or automatic training eligibility decision.

### Tutor-state authority

M8 owns controlled capture/freeze/reveal/comparison/explanation transitions. M13
persists and replay-verifies those transitions. Completing or comparing an M8
session does not automatically mutate M7/M11 or select M9 training.

### Training/outcome authority

M9 selects interventions only through explicit applicability rules. M10 records
predeclared bounded outcome/transfer evidence. Practice completion, successful
performance, near transfer, far transfer, real-game transfer, causality, and mastery
remain separate claims. M11 derives longitudinal learner state from exact current
hypothesis revisions and eligible evidence.

### Deterministic feedback authority

M16 composes deterministic session-local mentor feedback from exact M15/M6 and
optional complete active-current M7 evidence. It does not invoke a model and remains
the deterministic factual grounding ceiling.

### Model-language authority

M19 may ask an application-supplied provider to render prose from the exact M16
request. Provenance establishes which request reached which model run; it does not
establish semantic correctness, safety, or pedagogical effectiveness.

### Model-output evaluation authority

M20 records bounded `pass` / `fail` / `unclear` judgments under a frozen evaluation
policy. M20 acceptance is not objective chess truth and does not turn evaluator
rationale into deterministic evidence.

### Execution-conformance authority

M24 classifies one application-owned provider/evaluator adapter invocation, binds
endpoint/request identity, and records deterministic execution provenance.
Production vendor selection, automatic retry/backoff policy, credentials, privacy
approval, cost controls, and latency SLOs remain external decisions.

M31 can validate synthetic canaries and already-supplied manual retry histories. It
never executes a retry and accepts only test canary material.

### Persistence/review authority

M25 assembles an authority-separated coach-review read model. M26 atomically persists
reviewed-coaching outputs without advancing M8. M27 mechanically verifies the exact
persisted execution chain. M28 deterministically renders M25. M29 resolves persisted
review chains. M30 provides participant-scoped navigation/export.

Participant scoping is an integrity boundary, not hosted authentication.

### Consumer-delivery authority

M32 builds `m32.persisted-review-delivery-fidelity.v1` from one exact
participant-scoped M30 package. It preserves content order, explicit authority
labels, score perspective, symbolic mate, bounds, partial/unavailable semantics,
comparison state, child-analysis state, and exact source fingerprints.

M32 proves repository-local consumer fidelity, not browser/device correctness,
accessibility, usability, or production frontend quality.

### Deterministic trace authority

M33 builds `m33.deterministic-mentor-feedback-trace.v1` over exact persisted M16
feedback. Every substantive deterministic component is represented by stable
identity, ordinal, content hash, source authority, source pointer, and source fields.
M19/M20 remain separate presence/fingerprint metadata and cannot become deterministic
source authority.

M33 establishes traceability, not semantic truth or pedagogical correctness.

### Recovery-reconciliation authority

M34 builds `m34.reviewed-coaching-recovery-reconciliation.v1` from supplied synthetic
M24 multi-attempt histories and one already-persisted mechanically verified M26
target. It may classify the history as `complete` or `resume_eligible`; retryable
partial failures use full-M26 restart scope.

M34 never executes or authorizes retry and does not establish external-side-effect
idempotency or production recovery correctness.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != learner inference
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
M16 deterministic grounding != M19 model prose
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
participant candidate selection != capture consent
M23 operator/persistence != M6/M7/M9 authority
M24 execution conformance != vendor approval or retry authority
M25 read model != production UI or new evidence authority
M27 mechanically_verified != semantic truth
M28 static reference surface != production UI/accessibility/usability approval
M29 persisted bridge != new review/evidence authority
M30 participant navigation != authentication or privacy approval
M31 retry-history validation != retry execution or production retry policy
M32 machine-consumer fidelity != production UI quality or model truth
M33 deterministic traceability != model/evaluator authority
M34 resume eligibility != retry authorization, execution, or side-effect idempotency
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

`cme position packet` is deterministic and engine-free. `cme analyze` and
`cme diagnose` require an explicitly supplied UCI executable or PATH name. M18 also
requires an explicit versioned JSON selection policy.

M31–M34 are Python API / hermetic qualification surfaces. M32–M34 introduced no new
production CLI commands.

## Development and qualification

Focused latest-milestone suites:

```bash
python -m pytest tests/test_m32_persisted_review_delivery_fidelity.py -rs
python -m pytest tests/test_m33_deterministic_mentor_feedback_trace.py -rs
python -m pytest tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

Full repository merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not an independent-engine pass. Pull-request CI remains
the merge authority. No standalone static Python type checker is configured.

## Documentation discipline

The active documentation hierarchy is intentional:

```text
README.md
  product overview / usage / navigation

CONTEXT.md
  contributor reasoning model and invariants

docs/product/repository-build-status.md
  canonical moving implementation + qualification status

STATUS.md
  latest completed milestone handoff

docs/architecture/architecture.md
  current high-level implemented architecture

docs/product/chess-mentor-engine-repository-build-plan.md
  planning history + future candidates, never an approved queue by itself

docs/decisions/ and docs/runbooks/
  historical decisions, contracts, qualification, and operating detail
```

Do not rewrite historical ADRs/runbooks merely because later milestones exist.
Instead, keep active navigation/current-state documents aligned and point to the
historical artifact when detailed provenance is needed.

## Current claim ceiling and stop boundary

The repository can preserve longitudinal evidence history, expose qualified local
analysis/tutor surfaces, create diagnostic queues, persist an explicitly authorized
diagnostic candidate into M5/M8, compose deterministic grounded feedback, execute
application-owned provider/evaluator adapters through a neutral conformance seam,
record bounded model-output evaluation, persist and mechanically verify reviewed
coaching, deterministically render and deliver persisted review state, navigate and
export participant-scoped review packages, trace deterministic feedback to exact
sources, and reconcile synthetic retry histories against persisted targets.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatic M7/M11 mutation from tutoring, analysis, or model coaching;
- semantic correctness, safety, or pedagogical optimality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary evaluator;
- a production LLM/evaluator provider, credential/transport/retry architecture, or
  provider-quality claim;
- external-side-effect idempotency or production recovery correctness;
- production privacy/security approval or live secret-management correctness;
- correct participant disclosure/consent behavior in an external UI;
- production UI usability, accessibility, localization, browser/device
  compatibility, or visual correctness;
- hosted authentication/authorization, multi-user production persistence,
  observability, deployment readiness, or empirical tutoring efficacy.

The completed M32–M34 queue ends here. Future work starts with a fresh live-`main`
audit and an explicitly approved bounded package queue; handoff recommendations are
not self-authorizing implementation instructions.