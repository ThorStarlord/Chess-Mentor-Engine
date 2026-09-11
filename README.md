# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective
chess evidence, participant evidence, learner inference, tutoring, model-authored
language, model-output evaluation, review mechanics, and pedagogy in separate
provenance-bearing layers.

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
>  
> **Latest completed milestone handoff:** [`STATUS.md`](STATUS.md)  
> **Contributor orientation:** [`CONTEXT.md`](CONTEXT.md)  
> **Architecture map:**
> [`docs/architecture/architecture.md`](docs/architecture/architecture.md)

**Current implementation boundary:** M34 — Hermetic Reviewed-Coaching Recovery
Reconciliation. M1–M34 are qualified; M32–M34 are the latest completed milestone.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

Chess software is already strong at answering whether a move is objectively good
or bad. Chess Mentor Engine is aimed at the harder longitudinal problem:

```text
What is objectively happening on the board?
What did this player actually notice, consider, and expect?
What recurring explanation is currently supported strongly enough to affect teaching?
What should the player practice next?
Did that learning transfer into later play?
```

The repository therefore treats evidence, inference, model language, evaluator
judgment, and pedagogy as different authorities. A convincing model explanation is
not promoted into chess truth, and repeated errors are not automatically promoted
into permanent cognitive traits.

## Current bounded product path

The qualified repository path now reaches from deterministic chess evidence through
persistent reviewed coaching, participant review delivery, provenance tracing, and
hermetic recovery planning:

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound UCI engine analysis
-> objective played-move comparison / bounded diagnostic selection
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

Not every application must invoke every optional downstream layer. Every arrow is
still an authority boundary.

## Capability map

| Milestones | Qualified capability |
| --- | --- |
| M1–M4 | Canonical games/positions, deterministic chess context/features, normalized engine evidence, played-decision comparison, and explicit diagnostic selection. |
| M5–M7 | Frozen participant evidence, position-local reasoning discrepancy, participant-specific learner hypotheses, recurrence, challenge, and contradiction evidence. |
| M8–M11 | Evidence-aware tutor state, explicit intervention selection, bounded practice/transfer outcome evidence, and append-only longitudinal learner state. |
| M12–M18 | Evidence/artifact CLI, persistent tutor CLI, engine-backed analysis, deterministic presentation/feedback, analysis-presentation bridge, and diagnostic queue. |
| M19–M22 | Provenance-bound model coaching, bounded model-output evaluation, participant-authorized candidate launch, and hermetic cross-layer fidelity qualification. |
| M23–M27 | Diagnostic-to-persistent-tutor operator, provider/evaluator execution conformance, coach-review read model, persistent reviewed coaching, and mechanical execution ledger. |
| M28–M31 | Deterministic local review surface, persisted-review bridge, participant-scoped navigation/export, and hermetic privacy/manual-retry preflight. |
| M32–M34 | Machine-consumer review-delivery fidelity, deterministic mentor-feedback traceability, and hermetic reviewed-coaching recovery reconciliation. |

See the moving
[`repository-build-status.md`](docs/product/repository-build-status.md) for exact PR,
qualification, and current-boundary details.

## Core authority rules

The implementation is built around these separations:

```text
objective chess truth != participant self-report != learner inference
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != deterministic mentor feedback
M16 deterministic grounding != M19 model-authored language
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
participant candidate selection != capture consent
M27 mechanically_verified != semantic truth or pedagogical quality
M30 participant scoping != authentication
M32 consumer fidelity != production UI correctness
M33 deterministic traceability != model or pedagogical truth
M34 resume eligibility != retry authorization or retry execution
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

## Installed operator commands

The package currently installs:

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

The principal `cme` command exposes:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
```

M31–M34 are primarily Python API / hermetic validation surfaces. M32–M34 did not
introduce new production CLI commands.

### Inspect deterministic game and position evidence

```bash
cme games inspect games.pgn
cme games inspect games.pgn --full
cme position packet games.pgn --game-index 0 --ply-index 12
```

`position packet` remains engine-free.

### Run bounded engine analysis

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000 \
  --with-presentation
```

M14/M17 run the canonical position through the qualified M3/M4 engine evidence
contracts and optionally project the exact in-memory records through M15. Partial,
bounded, mate, terminal, incompatible, and failed states remain explicit rather
than being coerced into fake centipawn precision.

### Build a diagnostic analysis queue

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

The M18 output retains the complete auditable source pool plus the deterministic
candidate/control batch, exclusions, quotas, policy/source fingerprints, and
shortfalls. The repository does not define universal `inaccuracy`, `mistake`, or
`blunder` thresholds.

### Inspect verified local artifacts

```bash
cme artifacts list --db ./mentor.sqlite3 --participant P01
cme artifacts show --db ./mentor.sqlite3 --participant P01 --kind KIND ARTIFACT_ID
cme artifacts verify --db ./mentor.sqlite3 --participant P01
```

Participant scoping is an integrity boundary, not authentication. Protect the local
plaintext database.

### Run persistent tutor checkpoints

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

Every mutation replay-verifies the exact prior checkpoint, applies one native M8
transition, and writes an append-only successor checkpoint.

### Reviewed-coaching and review surfaces

Use the installed dedicated commands for the post-M23 operator path:

```text
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

The reviewed-coaching commands do not select a production model/evaluator provider
for the application. Network execution occurs only through explicitly supplied
M24-compatible application adapters.

See the milestone runbooks under [`docs/runbooks/`](docs/runbooks/) for exact
operator arguments and artifact contracts.

## Important Python boundaries

Principal package/domain surfaces include:

- `chess_mentor_engine.chess` — canonical chess state, provenance, context, and
  deterministic chess features;
- `chess_mentor_engine.analysis` — normalized provenance-bound M3 engine evidence;
- `chess_mentor_engine.selection` — M4 comparison and diagnostic selection;
- `chess_mentor_engine.evidence` — participant evidence;
- `chess_mentor_engine.learning` — M6 discrepancy and M7 learner hypotheses;
- `chess_mentor_engine.tutoring` — M8 state machine and M21 orchestration;
- `chess_mentor_engine.training` — M9 intervention registry/selection;
- `chess_mentor_engine.evaluation` — M10 outcome and transfer evidence;
- `chess_mentor_engine.longitudinal` — M11 learner state;
- `chess_mentor_engine.presentation` — M15 deterministic evaluation projection;
- `chess_mentor_engine.feedback` — M16 deterministic grounded mentor feedback;
- `chess_mentor_engine.coaching` — M19 model language and M20 evaluation contracts;
- `chess_mentor_engine.storage` — immutable local artifacts and verified replay;
- `chess_mentor_engine.review_delivery` — M32 exact machine-consumer review bundle;
- `chess_mentor_engine.mentor_feedback_trace` — M33 deterministic M16 provenance
  trace;
- `chess_mentor_engine.execution_recovery_reconciliation` — M34 hermetic recovery
  reconciliation plan.

M16 remains the deterministic factual grounding ceiling. M19 may render model prose
from that grounding, but request binding does not establish semantic correctness.
M20 records bounded evaluator judgments without converting them into objective truth.

## Latest milestone: M32–M34

### M32 — Persisted Review Delivery Fidelity

`m32.persisted-review-delivery-fidelity.v1` projects one exact participant-scoped
M30 package into a stable machine-consumer contract. It preserves explicit authority
labels, source ordering/fingerprints, White-versus-decision-mover perspective,
symbolic mate, bounds, partial/unavailable states, comparison state, and
child-analysis status.

### M33 — Deterministic Mentor-Feedback Trace

`m33.deterministic-mentor-feedback-trace.v1` binds every substantive deterministic
M16 feedback component to stable identity, ordinal, content hash, source authority,
source pointer, and source fields. M19/M20 remain separate presence/fingerprint
metadata and cannot become deterministic source authority.

### M34 — Reviewed-Coaching Recovery Reconciliation

`m34.reviewed-coaching-recovery-reconciliation.v1` reconciles supplied synthetic M24
multi-attempt histories against one already-persisted, mechanically verified M26
target. It may classify a history as `complete` or `resume_eligible`, but it never
executes or authorizes a retry and does not establish external-side-effect
idempotency.

See [`STATUS.md`](STATUS.md) and the
[M32–M34 milestone runbook](docs/runbooks/m32-m34-milestone-runbook.md).

## Validation

Focused latest-milestone qualification:

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

Pull-request CI is the merge authority. The Stockfish witness requires an actual
external executable; a skipped integration suite is not an independent-engine pass.
No standalone Python static type checker is configured.

## Documentation authority

Active documentation has deliberately different jobs:

| Document | Responsibility |
| --- | --- |
| `README.md` | Product overview, installation, operational entry points, and navigation. |
| `CONTEXT.md` | Contributor reasoning model, invariants, and current cross-layer boundaries. |
| `docs/product/repository-build-status.md` | **Canonical moving implementation and qualification status.** |
| `STATUS.md` | Completed latest-milestone handoff; historical once a later milestone replaces it. |
| `docs/architecture/architecture.md` | Current high-level implemented architecture and authority map. |
| `docs/product/chess-mentor-engine-repository-build-plan.md` | Planning history plus future candidate directions; not an approved work queue. |
| `docs/decisions/` | Ratified historical architectural decisions. |
| `docs/runbooks/` | Milestone/operator qualification and restart procedures. |

When narrative documents disagree about what is currently implemented, use
`docs/product/repository-build-status.md` as the status authority and then reconcile
the stale document rather than silently choosing a second source of truth.

## Current claim ceiling

The repository has qualified deterministic chess/evidence contracts, persistent
bounded tutor state, an operational diagnostic-to-persistent-tutor bridge,
provider-neutral execution conformance, authority-separated review, atomic
persistent reviewed coaching, privacy-bounded mechanical execution verification,
deterministic persisted review rendering/navigation, a machine-readable consumer
fidelity contract, deterministic mentor-feedback provenance tracing, and hermetic
reviewed-coaching recovery reconciliation.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection, intervention-caused improvement, or
  automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator vendor, credential flow, transport policy, automatic
  retry/backoff policy, latency/cost budget, or secrets architecture;
- external-side-effect idempotency or production recovery correctness;
- production privacy/security approval;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, visual correctness, or
  browser/device compatibility;
- hosted authentication/authorization, multi-user production persistence,
  observability, or deployment readiness;
- empirical tutoring efficacy.

## What comes next

M32–M34 are complete. Future implementation must begin with a fresh audit of live
`main` and a newly approved bounded work-package queue. The current handoff suggests,
but does not pre-authorize:

1. operator exposure for M32 delivery and M33 trace artifacts;
2. a hermetic cross-surface consumer regression contract across M30/M32/M33;
3. an explicit external-adoption and human-QA plan for frontend/provider/privacy/
   security/retry decisions.

See
[`docs/product/chess-mentor-engine-repository-build-plan.md`](docs/product/chess-mentor-engine-repository-build-plan.md)
for the planning view.