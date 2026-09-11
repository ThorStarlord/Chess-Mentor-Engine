# M31 — Hermetic Execution-Envelope Privacy & Retry Preflight

M31 adds a deterministic, fake-adapter/application-owned preflight around the existing M24/M26 execution seam. It validates synthetic canary privacy, manual retry-history legality, and persisted artifact cleanliness without selecting a production provider, handling live credentials, or executing retries.

## Boundary

M31 is HERMETIC_VALIDATION only.

It does not:

- accept or store production credentials;
- call live providers or evaluators;
- execute retries;
- grant automatic retry authority;
- choose timeout/backoff/rate-limit policy for production;
- deploy infrastructure;
- establish model-output truth or tutoring efficacy;
- establish privacy/security approval.

The existing authorities remain unchanged:

```text
M24 classifies one adapter invocation and records automatic_retry=false
M26 persists one successful application-selected execution per role
M27 verifies persisted execution mechanics
M31 validates synthetic-canary privacy + manual retry-history legality
```

## Synthetic canary contract

M31 accepts only markers beginning with:

```text
CME_TEST_CANARY_
```

The suffix must contain at least eight non-space characters. This is deliberate: M31 is a hermetic validation surface, not a live-secret scanner. Real API keys, tokens, passwords, or production credentials are outside this package and must not be supplied to M31.

A successful M31 preflight stores only the number of canaries tested. It never persists their values.

## Retry-plan contract

M31 validates retry history; it never performs a retry.

For each persisted M24 role selected by the M26 run:

- attempt history must begin at attempt 1 and be contiguous;
- all attempts must preserve the exact endpoint, request reference, and timeout;
- every M24 record must preserve `automatic_retry=false`;
- a later attempt is legal only when the previous attempt failed with M24 `timeout` or `transient` classification and `retryable=true`;
- a retry after permanent, malformed, identity, chronology, request-mutation, or invalid-request failure is rejected;
- no attempt may follow a successful attempt;
- the final attempt must be the exact M24 execution persisted by M26;
- attempt count must not exceed the declared bounded `max_attempts` plan.

A passing report therefore proves only that an already-supplied history is compatible with a manual retry plan. It does not authorize or execute that plan.

## Persisted privacy scan

Before M31 creates any preflight artifact, it scans the full persisted dependency closure rooted at the selected M26 run for every supplied synthetic canary. That closure includes the M25 review and any persisted M19/M20/M24 artifacts reachable from M26.

Only after that scan passes does M31 build the exact one-run M27 mechanical ledger. It then scans the combined M26 + M27 closure again.

If a canary is found in either:

- an in-memory M24 attempt-history record, including failure detail; or
- the persisted M26/M27/review dependency closure,

M31 fails closed and does not persist an M31 report. Error text identifies the failed boundary but does not echo the canary value.

## Persisted report

A passing report is stored as:

```text
m31.execution-envelope-privacy-retry-preflight.v1
```

The report is content-addressed and depends on the exact M26 run and M27 ledger. It contains only:

- exact M26/M27/M24 artifact references;
- bounded retry-history summaries (`attempt_number`, status, failure kind, retryable flag);
- declared `max_attempts`;
- synthetic-canary count and scan status;
- hermetic and authority-boundary declarations.

It does not copy:

- canary values;
- failure detail strings;
- request payloads;
- model-rendered coaching;
- evaluator rationales;
- participant responses.

## Qualification

Focused M31 suite:

```bash
python -m pytest tests/test_m31_execution_envelope_preflight.py -rs
```

Principal execution-envelope regression:

```bash
python -m pytest \
  tests/test_m24_provider_conformance.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m31_execution_envelope_preflight.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The repository CI additionally runs the independent Stockfish witness on the exact candidate head.

## Positive hermetic scenarios

The M31 suite qualifies:

- provider and evaluator single-attempt success histories;
- a fake provider holding a synthetic canary out-of-band without leaking it into persisted outputs;
- timeout failure followed by an explicitly represented successful manual attempt;
- transient/rate-limit-style failure followed by an explicitly represented successful manual attempt;
- content-idempotent repeated preflight construction.

## Negative / rejection scenarios

The M31 suite rejects:

- real-secret-like values that do not use the synthetic canary prefix;
- canary leakage in failed-attempt detail;
- canary leakage in successfully persisted model content / M25 review closure;
- forged `automatic_retry=true` execution records;
- retry after a permanent failure;
- non-contiguous attempt histories;
- histories that exceed the bounded retry plan;
- missing provider/evaluator histories for persisted M26 roles;
- cross-participant run selection.

## Claim ceiling

A passing M31 artifact establishes only that the supplied hermetic M24 history and the exact persisted M26/M27/review closure satisfy the bounded synthetic-canary and manual-retry preflight contract.

It does not prove that a production vendor redacts secrets, that live transport is safe, that a real credential-management system is correct, that retry/backoff/rate-limit policies are operationally appropriate, that costs are bounded, or that provider/evaluator outputs are semantically correct.
