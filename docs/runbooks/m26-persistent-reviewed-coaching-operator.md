# M26 Persistent Reviewed-Coaching Operator

M26 closes the repository-local seam between a replay-verified M13 `compared`
checkpoint and the qualified M16/M19/M20/M24/M25 review contracts.

It does **not** add chess, learner-inference, training, provider-selection, or
pedagogical authority. It also does not advance the M8 tutor session. The existing
`cme tutor explain` command remains the explicit persisted explanation transition.

## Deterministic local command

The installed repository-only command invokes no chess engine and no model provider:

```bash
cme-reviewed-coaching \
  '<tutor-session-id>:<snapshot-fingerprint>' \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-10T15:00:00-03:00
```

The selected checkpoint must already be a replay-verifiable M13 `compared` session
whose retained dependencies resolve exactly through the M23/M21 lineage:

```text
M8 compared checkpoint
-> M21 launch
-> M21 authorization
-> M18 diagnostic queue
```

The operator reconstructs the exact retained M3/M4 evidence from the M18 queue,
rebuilds M15, composes deterministic M16 grounding, assembles M25, and atomically
persists those outputs plus the M26 run record. The source tutor checkpoint remains
`compared` and unexplained.

## Optional provider/evaluator seam

`run_persistent_reviewed_coaching(...)` also accepts explicit M24-compatible provider
and evaluator adapters plus exact endpoint identities. This Python API is the
integration seam for hermetic fakes and future application-owned adapters.

When a provider is supplied, M26 builds the native M19 request, executes it through
M24's immutable request boundary, then uses the non-mutating M19 binder. When an
evaluator is also supplied, M26 likewise builds M20, executes through M24, and binds
the bounded M20 result. It deliberately does not use the M24 convenience runners
that record an M8 explanation.

A provider/evaluator failure is returned as a classified M24 execution record on the
raised M26 error, but no partial M26 output chain is persisted. M26 grants no
automatic retry authority.

## Persistence lineage

Successful outputs are append-only, content-addressed local artifacts. Depending on
which optional layers were invoked, they include:

```text
M16 grounded feedback
M19 model request
M24 provider execution
M19 provenance-bound coaching
M20 evaluation request
M24 evaluator execution
M20 bounded evaluation
M25 coach-review read model
M26 orchestration run
```

The whole output set is prepared first and committed through one atomic artifact
batch. Identical invocations are content-idempotent; divergent content under the
same immutable identity fails through the existing storage contract.

## Qualification

Focused M26 qualification:

```bash
python -m pytest tests/test_m26_persistent_reviewed_coaching.py
```

Related regression surface:

```bash
python -m pytest \
  tests/test_m13_persistent_tutor_cli.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py
```

Full repository gate remains:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not an independent engine pass.

## Deferred external authority

M26 does not select a production model/evaluator vendor, handle real credentials,
perform live calls, define retry/backoff policy, approve privacy/data transmission,
claim arbitrary model/evaluator semantic correctness, certify user-facing disclosure
or UX, or establish tutoring efficacy.
