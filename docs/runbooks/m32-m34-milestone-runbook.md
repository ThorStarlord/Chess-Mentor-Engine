# M32–M34 Milestone Runbook

This runbook is the restart and qualification guide for the completed M32–M34 milestone:

```text
M32 Persisted Review Delivery Fidelity Contract
M33 Deterministic Mentor-Feedback Trace Surface
M34 Hermetic Reviewed-Coaching Recovery Reconciliation
```

The milestone is complete. These instructions are for verification, maintenance, debugging, and future-milestone reconciliation. They are not an instruction to automatically start new feature work.

## Baseline

Completed feature baseline:

```text
M32 merge: ae4bbe7c925855df9082c41bd46b4fea7d930bc8  PR #69
M33 merge: 4eadb996b8c4036c793515d2457fe363c81cb40d  PR #70
M34 merge: 9e896bf955de24acaf6dc5d0503147eaaae3c1e4  PR #71
```

Before relying on these hashes, always fetch current `main` and read:

```text
STATUS.md
docs/product/repository-build-status.md
CONTEXT.md
```

## Install and local test environment

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

No production credential, hosted service, model provider, evaluator provider, deployment target, or live retry service is required for M32–M34 qualification.

## Runtime surface

M32–M34 introduced **no new production CLI command**. They are repository-local Python API / validation surfaces layered over the existing persisted review and reviewed-coaching contracts.

### M32 API

```python
from chess_mentor_engine.review_delivery import (
    build_persisted_review_delivery_bundle,
    validate_persisted_review_delivery_bundle,
    validate_review_delivery_bundle,
)
```

M32 consumes one exact participant-scoped persisted M30 package and produces the versioned machine-readable contract:

```text
m32.persisted-review-delivery-fidelity.v1
```

The contract preserves explicit authority labels, exact source identities, White-versus-decision-mover semantics, mate/bound/partial/unavailable states, comparison state, child-analysis state, and deterministic ordering. It must not reinterpret score semantics or promote M19/M20 output into objective evidence.

### M33 API

```python
from chess_mentor_engine.mentor_feedback_trace import (
    build_persisted_mentor_feedback_trace_surface,
    validate_mentor_feedback_trace_surface,
    validate_persisted_mentor_feedback_trace_surface,
)
```

M33 produces:

```text
m33.deterministic-mentor-feedback-trace.v1
```

It hashes each substantive deterministic M16 component and binds it to exact M15, M6, or optional M7 source provenance. M19 model prose and M20 evaluator judgments remain separate presence/fingerprint metadata and are never valid deterministic source authority.

### M34 API

```python
from chess_mentor_engine.execution_recovery_reconciliation import (
    build_reviewed_coaching_recovery_reconciliation,
    validate_reviewed_coaching_recovery_plan,
    validate_persisted_reviewed_coaching_recovery_plan,
)
```

M34 produces:

```text
m34.reviewed-coaching-recovery-reconciliation.v1
```

It reconciles supplied synthetic M24 multi-attempt histories against one already-persisted mechanically verified M26 target. A plan may report `complete` or `resume_eligible`; `resume_eligible` requires manual external authority and uses `full_m26_orchestration` restart scope. The API does not execute or authorize a retry.

## Focused milestone qualification

Run each package suite independently when changing one of the M32–M34 contracts:

```bash
python -m pytest tests/test_m32_persisted_review_delivery_fidelity.py -rs
python -m pytest tests/test_m33_deterministic_mentor_feedback_trace.py -rs
python -m pytest tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

The final package qualifications recorded during milestone delivery were:

```text
M32: 16 focused tests passed
M33: 12 focused tests passed
M34: 15 focused tests passed
```

## Principal regression chain

Use this when a change can affect the persisted review, consumer-fidelity, deterministic-feedback provenance, or reviewed-coaching execution seams:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py \
  tests/test_m30_participant_review_package_navigation.py \
  tests/test_m31_execution_envelope_preflight.py \
  tests/test_m32_persisted_review_delivery_fidelity.py \
  tests/test_m33_deterministic_mentor_feedback_trace.py \
  tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

## Full repository merge gate

Every future PR that changes these contracts should run:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The milestone's final full-suite evidence was:

```text
M32 candidate: 790 passed, 8 intentional external-engine skips
M33 candidate: 802 passed, 8 intentional external-engine skips
M34 candidate: 817 passed, 8 intentional external-engine skips
```

A regular full pytest run intentionally skips the external Stockfish integration tests when `STOCKFISH_EXECUTABLE` is unavailable. Those skips are not an independent-engine pass.

## Independent Stockfish witness

Provide a local Stockfish executable explicitly:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The exact final candidates for M32, M33, and M34 each passed all 8 independent Stockfish integration tests.

## Package-specific rejection expectations

### M32

Fail closed on at least:

- White/decision-mover perspective drift;
- bound loss or inversion;
- symbolic mate converted to centipawns;
- exact centipawn deltas invented for non-exact comparisons;
- MultiPV ordering/rank drift;
- source-fingerprint or source-reference substitution;
- forged authority labels;
- participant-scope drift.

### M33

Fail closed on at least:

- M16/M15, M16/M6, or M16/M7 identity/fingerprint drift;
- missing deterministic components;
- changed component hashes;
- same-authority source-pointer substitution;
- M6 source-fingerprint substitution;
- M19/M20 authority promotion;
- cross-participant references or forged M30 package selection.

### M34

Fail closed on at least:

- permanent or otherwise non-retryable failure followed by a later attempt;
- duplicate or non-contiguous attempt numbers;
- endpoint/request/timeout drift from the persisted target;
- forged `automatic_retry=true`;
- wrong final provider/evaluator execution;
- cross-run request substitution;
- stale M25/M20 source fingerprints;
- participant-scope violations.

A retryable partial history may become `resume_eligible`, but that state is a repository-local reconciliation result only. It is not permission to perform an external call.

## Claim and authority boundaries

Preserve the following invariants during maintenance:

```text
M15/M16 deterministic evidence != M19 model-authored prose
M20 evaluator acceptance != objective chess truth
M27 mechanical fidelity != semantic truth
M30 participant scope != authentication
M32 machine-consumer fidelity != production UI correctness
M33 deterministic provenance != pedagogical correctness
M34 resume eligibility != retry authority
M34 recovery reconciliation != external-side-effect idempotency
```

Do not add production credentials to fixtures. Do not call live model/evaluator services as part of M32–M34 qualification. Do not convert browser/device/a11y/usability review, privacy/security approval, provider selection, live retry/backoff policy, or pedagogical evaluation into repository-owned assertions.

## Pending human / external gates

Still outside repository authority:

- production frontend adoption and browser/device/a11y/localization/usability QA for M28/M30/M32-facing consumers;
- end-user consent/disclosure review;
- production model and evaluator provider selection;
- credential handling, privacy/security review, transmission and retention policy;
- live timeout/retry/backoff/rate-limit behavior, latency/cost budgets, billing and incident policy;
- external-side-effect idempotency and real recovery correctness;
- semantic safety/correctness/pedagogical quality of arbitrary model coaching;
- evaluator completeness and production calibration;
- empirical tutoring efficacy;
- hosted auth, tenancy, observability, persistence operations, and deployment.

## Restart checklist for the next milestone

1. Fetch live `main` and recent commits.
2. Read `STATUS.md`, `docs/product/repository-build-status.md`, and `CONTEXT.md`.
3. Re-run the focused M32–M34 suites.
4. Run the full pytest/Ruff/compile gate.
5. Run Stockfish independently; do not count skips as success.
6. Audit whether M32/M33 operator exposure, a cross-surface consumer regression package, or external adoption/human QA is now the true bottleneck.
7. Classify proposed work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY` before implementation.
8. Establish a fresh bounded package queue. Do not automatically continue the recommendations in `STATUS.md`.

## References

- [`STATUS.md`](../../STATUS.md)
- [`repository-build-status.md`](../product/repository-build-status.md)
- [`M32 runbook`](m32-persisted-review-delivery-fidelity.md)
- [`M33 runbook`](m33-deterministic-mentor-feedback-trace.md)
- [`M34 runbook`](m34-reviewed-coaching-recovery-reconciliation.md)
- PR #69 — M32
- PR #70 — M33
- PR #71 — M34
