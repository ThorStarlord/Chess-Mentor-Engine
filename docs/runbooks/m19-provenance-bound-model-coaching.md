# M19 — Provenance-Bound Mentor Coaching

## Purpose

M19 introduces the first model-authored mentor-language boundary without promoting
the model into a new chess, learner-inference, or pedagogy authority.

It answers one bounded integration question:

> How can an external model render more natural mentor language from the exact
> qualified M16 grounding record while preserving request identity, evidence
> provenance, model provenance, chronology, and the existing M8 explanation state
> transition?

The production model provider and transport remain deliberately unfrozen.

## Evidence path

M19 consumes the existing qualified boundary rather than rebuilding it:

```text
M3 engine evidence
+ M4 DecisionComparison
+ M8 TutorSession(compared)
+ exact M6 comparison/assertions
+ optional complete active-current M7 context
        |
        v
M16 compose_grounded_mentor_feedback
        |
        v
m16.grounded-mentor-feedback.v1
        |
        v
M19 content-addressed model request
        |
        v
external ModelCoachProvider
        |
        v
request-bound model prose
        |
        v
existing M8 record_tutor_explanation(actor_kind=model)
```

M19 never accepts model-supplied replacement M3, M4, M6, M7, or M9 records.

## Public API

```python
from chess_mentor_engine.coaching import (
    ModelCoachingGeneration,
    build_model_coaching_request,
    record_model_coaching_response,
    run_model_coaching,
)
```

The request schema is:

```text
m19.model-coaching-request.v1
```

The accepted coaching-record schema is:

```text
m19.provenance-bound-mentor-coaching.v1
```

## Build a request

```python
request = build_model_coaching_request(
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,  # optional
    created_at="2026-09-10T10:13:00-03:00",
)
```

Before the request exists, M19 calls the qualified M16 composer again. Therefore the
same M16 checks still apply: exact tutor comparison identity, exact M3/M4 binding,
objective-reveal exposure, complete attached M7 context, M15 consistency, and
chronology.

The resulting request retains:

```text
request_id
fingerprint
exact tutor session snapshot fingerprint
exact tutor comparison ID/fingerprint
optional exact M7 context ID/fingerprint
complete m16.grounded-mentor-feedback.v1 record
fingerprinted M19 instruction contract
created_at
claim_scope = model_language_rendering_request
```

The request is content-addressed. Changing the M16 grounding, tutor snapshot,
instruction contract, or request chronology changes its fingerprint and identity.

## Instruction / authority ceiling

The v1 instruction contract describes the model role as:

```text
language_renderer_only
```

Allowed responsibilities are limited to:

- human-readable chess explanation;
- Socratic reflection;
- explanation of already-qualified evidence and uncertainty.

The request explicitly denies authority to create:

- new objective chess facts;
- new M6 reasoning judgments;
- new M7 learner hypotheses;
- M9 training selections;
- causal learner diagnoses or mastery claims.

It also requires non-exact evidence to remain non-exact and mate evidence to remain
symbolic.

## Provider boundary

M19 defines the structural `ModelCoachProvider` protocol:

```python
class ModelCoachProvider:
    def generate(self, request):
        return ModelCoachingGeneration(...)
```

A provider result contains only:

```text
request_id
request_fingerprint
rendered_content
provider_id
model_id
model_version
run_id
generated_at
```

The provider cannot return replacement structured chess or learner records through
the M19 generation type.

`run_model_coaching` gives the provider a detached canonical copy of the exact
request. Mutation of that request by the provider is detected and rejected.

M19 does not choose OpenAI, Anthropic, a local model, or any other production
provider. Provider credentials, retries, rate limits, transport, and deployment
policy remain outside this milestone.

## Bind and record model prose

An application may call the two phases separately:

```python
generation = ModelCoachingGeneration(
    request_id=request["request_id"],
    request_fingerprint=request["fingerprint"],
    rendered_content=model_text,
    provider_id="provider-name",
    model_id="model-name",
    model_version="provider-version",
    run_id="provider-run-id",
    generated_at="2026-09-10T10:14:00-03:00",
)

updated, explanation, coaching = record_model_coaching_response(
    request=request,
    session=compared_tutor_session,
    root_analysis=root_analysis,
    decision_comparison=decision_comparison,
    played_analysis=played_child_analysis,
    generation=generation,
)
```

Or the application may call `run_model_coaching` with a provider object to build the
request, invoke exactly one provider call, validate the result, and record the
explanation.

Before recording, M19:

1. verifies the request shape, schema, fingerprint, and content-addressed ID;
2. verifies the instruction object is the exact qualified M19 v1 contract;
3. recomputes the M16 grounding from the supplied current source records;
4. requires the complete request to match that recomputed grounding;
5. requires the provider result to echo the exact request ID/fingerprint;
6. rejects blank prose;
7. rejects a generation timestamp earlier than the grounding request;
8. records only through the existing M8 explanation transition.

The M8 explanation provenance is:

```text
actor_kind = model
actor_id = <provider_id>:<model_id>
actor_version = <model_version>
instruction_fingerprint = exact M19 instruction fingerprint
run_id = provider run ID
```

Earlier M3/M4/M6/M7 records are not rewritten.

## Semantic model-quality boundary

M19 proves **provenance binding, not semantic truthfulness**.

The accepted coaching record therefore includes:

```text
grounding_status = request_bound_not_semantically_verified
claim_scope = session_local_model_rendering
```

A model can still produce poor wording or unsupported prose. M19 does not pretend a
checksum, request echo, or typed provider record can solve hallucination detection.
Future model-output evaluation may assess chess consistency, evidence sufficiency,
overclaiming, and pedagogical quality, but that is a separate qualification layer.

The deterministic M16 record remains the factual grounding ceiling.

## Rejection coverage

Focused M19 suite:

```bash
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
```

It covers:

- deterministic request identity and exact M16 grounding;
- preservation of complete attached M7 context through M16;
- successful model-provenance recording through M8;
- wrong request ID/fingerprint echo rejection;
- rehashed instruction-contract tampering rejection;
- objective-evidence drift rejection;
- blank and predating generation rejection;
- provider exception rejection;
- provider request-mutation rejection;
- invalid provider-result type rejection.

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`; skipped external-engine tests are
not an independent engine pass. Pull-request CI remains the merge gate.

## Boundaries

M19 explicitly does **not** implement:

- a production LLM vendor SDK or API transport;
- automatic semantic verification of model prose;
- new engine analysis or score semantics;
- automatic M6 discrepancy generation;
- automatic M7 hypothesis creation/revision;
- M9 intervention selection or lesson assignment;
- M10 causal-effect or mastery claims;
- M11 longitudinal-state mutation;
- a new persistence authority outside M8;
- web/desktop UI, authentication, or hosted multi-user services;
- empirical tutoring-efficacy claims.
