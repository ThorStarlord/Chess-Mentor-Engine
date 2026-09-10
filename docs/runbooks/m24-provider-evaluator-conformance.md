# M24 — Provider / Evaluator Execution Conformance

## Purpose

M24 adds a provider-neutral execution boundary around the already-qualified M19
`ModelCoachProvider` and M20 `ModelCoachingEvaluator` protocols.

It does **not** choose a production provider, evaluator, model, vendor, retry policy,
credential flow, or deployment architecture. It classifies execution behavior and
preserves exact provenance while leaving chess, learner, training, and semantic-truth
authority where M16/M19/M20 already define it.

The intended path is:

```text
M16 grounding
-> M19 request
-> M24 immutable provider execution
-> M19 bind/record
-> M20 evaluation request
-> M24 immutable evaluator execution
-> M20 bind/evaluate
```

## Public API

```python
from chess_mentor_engine.coaching import (
    ModelCoachEndpoint,
    ModelEvaluatorEndpoint,
    PermanentExternalExecutionError,
    TransientExternalExecutionError,
    execute_model_coach_provider,
    execute_model_coaching_evaluator,
    run_conformant_model_coaching,
    run_conformant_model_coaching_evaluation,
)
```

The execution-record schema is:

```text
m24.provider-evaluator-execution.v1
```

## Detached immutable requests

M24 canonicalizes each M19 or M20 request into a detached JSON copy and then freezes
all nested dictionaries and lists before handing the copy to an external adapter.

Normal mutation attempts fail immediately with `RequestMutationError`. M24 also
compares the adapter-visible request against the source request after the call, so an
adapter that deliberately bypasses ordinary mutators is still rejected as
`request_mutation`.

The source M19/M20 request is never handed to the adapter by reference.

## Endpoint identity

Provider execution requires an explicit `ModelCoachEndpoint`:

```text
adapter_id
adapter_version
provider_id
model_id
model_version
```

Evaluator execution requires an explicit `ModelEvaluatorEndpoint`:

```text
adapter_id
adapter_version
evaluator_kind
evaluator_id
evaluator_version
```

A returned generation must echo the exact request ID/fingerprint and match the
configured endpoint identity. Drift is classified as `identity_mismatch`; M24 does
not silently accept whatever provider/model/evaluator identity a runtime happens to
return.

## Failure taxonomy

M24 produces one explicit execution failure kind:

- `invalid_request` — the supplied request chronology cannot be interpreted safely;
- `request_mutation` — the adapter attempted to alter its detached request;
- `timeout` — the adapter reports Python `TimeoutError`;
- `transient` — the adapter reports `TransientExternalExecutionError`;
- `permanent` — the adapter reports `PermanentExternalExecutionError`, or an unknown
  exception reaches the boundary;
- `malformed_response` — the adapter does not return the required typed M19/M20
  generation, returns blank M19 prose, or returns incomplete/duplicate M20 dimensions;
- `identity_mismatch` — request echo or configured provider/model/evaluator identity
  does not match;
- `chronology_violation` — result time is invalid, timezone-free, or predates its
  request.

Only `timeout` and `transient` are marked `retryable=true` in the execution record.
M24 performs **no automatic retry**.

Unknown exceptions default to `permanent`. This is deliberately fail-closed: a future
vendor adapter must explicitly translate vendor-specific retryable failures into the
neutral transient marker rather than receiving implicit retry authority.

## Timeout boundary

`timeout_ms` is an explicit execution-policy field and is retained in provenance.
The existing M19/M20 protocols are synchronous and expose only `generate(request)` or
`evaluate(request)`, so M24 does not start background threads or attempt unsafe
cross-platform preemption.

A concrete future adapter is responsible for enforcing its vendor/client timeout and
reporting timeout expiry as `TimeoutError`. That external transport implementation is
deferred. M24 qualifies the classification and provenance behavior without making a
claim that arbitrary synchronous code can be forcibly interrupted.

## Deterministic execution provenance

Every success or failure produces a content-addressed M24 record containing:

```text
schema_version
role
endpoint
request_ref
execution_policy
status
response_ref | failure
claim_scope
authority_boundary
execution_id
fingerprint
```

No wall-clock timestamp is invented by M24. Success provenance uses the exact
provider/evaluator generation time already supplied by the typed result. Failure
records are derived from the exact request, endpoint, declared timeout/attempt, and
observed classified failure.

Repeating the same hermetic execution inputs and result produces the same execution
record and fingerprint.

## Conformant runners

`run_conformant_model_coaching` builds the normal M19 request, executes the provider
through M24, and only after successful conformance invokes the existing M19
`record_model_coaching_response` binder.

`run_conformant_model_coaching_evaluation` builds the normal M20 request, executes the
evaluator through M24, and only after successful conformance invokes the existing M20
`bind_model_coaching_evaluation` binder.

The original M19/M20 primitives remain available and unchanged. M24 is the qualified
execution surface for future external adapters; it does not rewrite the semantic
contracts they already enforce.

## Authority ceiling

Every M24 execution record explicitly says that the layer may classify execution but
may not:

- create objective chess facts;
- create or strengthen learner hypotheses;
- select training;
- establish semantic truth of model prose.

A successful provider execution means only that the configured endpoint returned a
well-formed, identity-bound, chronologically valid M19 generation. A successful
evaluator execution means only that the configured endpoint returned a well-formed,
identity-bound, complete M20 judgment generation.

M19 and M20 remain responsible for their existing downstream binding and bounded
qualification semantics.

## Hermetic qualification

Focused M24 suite:

```bash
python -m pytest tests/test_m24_provider_conformance.py
```

Regression around the wrapped contracts:

```bash
python -m pytest \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m24_provider_conformance.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The M24 tests use fake providers and evaluators only. They qualify:

- detached deep-frozen request behavior;
- ordinary and forced mutation rejection;
- timeout/transient/permanent classification;
- fail-closed unknown-exception behavior;
- malformed provider/evaluator results;
- request-echo and endpoint-identity mismatch;
- chronology rejection;
- complete/unique M20 dimensions;
- deterministic success and failure records;
- no automatic retry;
- successful handoff back into the existing M19/M20 binders.

## Deferred external authority

M24 deliberately leaves the following outside repository qualification:

- selection of any production LLM or evaluator vendor;
- real API credentials or paid-service calls;
- vendor SDK installation;
- live retry/backoff/rate-limit tuning;
- production timeout values and latency SLOs;
- cost budgets and billing controls;
- privacy/security approval for transmitted user data;
- semantic or pedagogical quality claims for any live model/evaluator;
- deployment, hosted observability, or production incident policy.

Those decisions can be made later against this stable conformance boundary without
embedding vendor semantics into M19/M20.
