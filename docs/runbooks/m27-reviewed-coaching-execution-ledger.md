# M27 — Reviewed-Coaching Execution Ledger & Fidelity Qualification

M27 is a repository-only observability layer over already-persisted M26
reviewed-coaching runs. It does not execute an engine, model provider, evaluator,
network transport, retry, deployment, or learner-state transition.

## Purpose

M26 can persist a reviewed-coaching chain from one replay-verified M8 `compared`
checkpoint through M16 grounding, optional M19/M20 model/evaluator records via M24,
and M25 review. M27 verifies the persisted closure and writes a compact execution
ledger suitable for local inspection and later application observability.

The qualified chain is:

```text
M26 run
├─ exact M8 source checkpoint
├─ exact M25 read model
│  ├─ M18 diagnostic queue
│  ├─ M21 authorization
│  ├─ M21 launch
│  ├─ M8 checkpoint
│  ├─ M16 deterministic grounding
│  ├─ optional M19 coaching
│  └─ optional M20 evaluation
└─ zero, one, or two M24 execution records
   ├─ optional M19 provider execution -> exact M19 request
   └─ optional M20 evaluator execution -> exact M20 evaluation request
```

## Fidelity claim

`mechanically_verified` means only that M27 verified content identities,
fingerprints, dependency closure, progressive optionality, request/response binding,
and M25 projection preservation against exact persisted artifacts.

It does **not** mean:

- the engine evaluation is universally correct;
- model-authored coaching is semantically correct, safe, or pedagogically effective;
- an evaluator verdict establishes objective truth;
- a production provider, transport, credential flow, timeout, retry, or cost policy is
  approved;
- a user interface has correct disclosure, accessibility, localization, or usability.

M20's `truth_status = not_established_by_m20_evaluation` is preserved as a hard
boundary.

## Privacy boundary

The M27 ledger copies only content-addressed references and transport-neutral
execution metadata needed for mechanical observability. It does not copy:

```text
request payloads
model rendered coaching content
evaluator rationale text
participant raw or structured response content
```

It may retain provider/model/evaluator endpoint identity, request IDs/fingerprints,
execution IDs/fingerprints, run IDs, timestamps already present in M24 response
references, timeout policy, and attempt number.

The local SQLite database remains plaintext local storage; M27 is not an encryption,
authentication, authorization, retention, or secrets-management system.

## CLI

After installing the package in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Qualify all persisted M26 runs for one participant:

```bash
cme-reviewed-coaching-ledger \
  --db ./artifacts.sqlite3 \
  --participant P01
```

Qualify an explicit subset by repeating `--run-id`:

```bash
cme-reviewed-coaching-ledger \
  --db ./artifacts.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_aaaaaaaaaaaaaaaaaaaa \
  --run-id reviewed_coaching_run_bbbbbbbbbbbbbbbbbbbb
```

Input order does not affect ledger identity. Selected runs are ordered by M26 run ID.
Repeated identical invocation is content-idempotent.

## Fail-closed conditions

M27 rejects, among other cases:

- missing or duplicate requested M26 run IDs;
- M26 native identity, participant, claim-scope, or authority-boundary drift;
- unexpected M26 or M25 dependency structure;
- disagreement between M26 source refs and exact M25 dependencies;
- M18/M21 candidate, batch, authorization, or launch drift;
- M8 source checkpoint drift between M26 and M25;
- M16/M19/M20 content or source-fingerprint drift in M25;
- an M20 record that promotes evaluator output to objective truth;
- M24 execution identity/request dependency drift;
- successful M26 runs containing failed M24 execution records;
- any M24 execution that claims automatic retry;
- provider response identity that disagrees with bound M19 provenance;
- evaluator response identity that disagrees with bound M20 provenance.

No M27 artifact is written when qualification fails.

## Qualification

Focused package suite:

```bash
python -m pytest tests/test_m27_reviewed_coaching_execution_ledger.py -q
```

Relevant regression:

```bash
python -m pytest \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py -q
```

Full native gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Independent engine witness remains the existing CI Stockfish job. A skipped local
Stockfish suite is not treated as an independent-engine pass.

## Authority boundary

M27 is an execution ledger and mechanical verifier. It creates no chess facts,
learner hypotheses, training decisions, tutor transitions, model prose, evaluator
judgments, retry decisions, provider selection, production credentials, or
pedagogical-quality claims.
