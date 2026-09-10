# M20 — Model Coaching Evaluation Contract

## Purpose

M20 adds a bounded evaluation layer over the qualified M19 model-language boundary.
It does **not** turn provenance checks, evaluator judgments, or a passing result into
objective chess truth.

The evidence path is:

```text
exact M3/M4 sources
-> M15 evaluation presentation
-> exact recomputed M16 grounded feedback
-> M19 provenance-bound model coaching
-> M20 content-addressed evaluation request
-> explicit evaluator judgments
-> m20.model-coaching-evaluation.v1
```

M20 first revalidates the exact M19 coaching record against its M19 request and the
current M16/M15 source evidence. Only then can an evaluator assess the rendered
prose.

## Public API

```python
from chess_mentor_engine.coaching import (
    EVALUATION_DIMENSIONS,
    ModelCoachingEvaluationGeneration,
    ModelCoachingEvaluationJudgment,
    bind_model_coaching_evaluation,
    build_model_coaching_evaluation_request,
    run_model_coaching_evaluation,
)
```

The request and record schemas are:

```text
m20.model-coaching-evaluation-request.v1
m20.model-coaching-evaluation.v1
```

## Frozen evaluation dimensions

M20 v1 requires exactly one judgment for each dimension:

1. `grounding_consistency` — prose remains consistent with exact M16 grounding.
2. `objective_chess_consistency` — objective claims do not contradict or extend
   exact M15/M16 evidence.
3. `evidence_sufficiency` — claimed certainty is supported at the claimed strength.
4. `uncertainty_preservation` — partial, bounded, incompatible, unavailable,
   unclear, or unscorable evidence is not promoted to stronger certainty.
5. `mate_and_bound_preservation` — symbolic mate and ordering-bound semantics are
   not converted into invented exact values.
6. `learner_inference_scope` — no invented learner hypotheses, causal diagnoses,
   permanent traits, or stronger M7 claims.
7. `authority_boundary` — no new M6/M7/M9 authority, mastery claim, or equivalent
   structured promotion is created in prose.

Allowed verdicts are `pass`, `fail`, and `unclear`. Missing or duplicate dimensions
fail closed. Any `fail` makes the bounded evaluation rejected. With no failures, any
`unclear` makes it inconclusive. Only seven `pass` judgments produce
`accepted_under_m20_evaluation_policy`.

That status means only that the supplied evaluator judgments satisfy the frozen M20
policy. The record always retains:

```text
truth_status = not_established_by_m20_evaluation
claim_scope = bounded_model_output_quality_assessment
```

## Mechanical source-integrity gate

`build_model_coaching_evaluation_request` does not trust loose JSON. It reconstructs
the exact `ModelCoachingGeneration` represented by the supplied M19 coaching record,
re-runs the qualified M19 binding logic against the exact M19 request and current
M16/M15 sources, and rejects any mismatch.

The M20 request then carries:

- exact M19 coaching ID/fingerprint/schema reference;
- exact M19 request ID/fingerprint/schema reference;
- the complete exact M16 grounded-feedback record;
- a freshly rebuilt exact M15 evaluation presentation;
- the exact rendered model prose and model provenance;
- the frozen fingerprinted M20 policy;
- explicit request chronology and claim scope.

The request is content-addressed. Rehashed policy tampering still fails because the
policy must equal the exact qualified v1 contract.

## Evaluator boundary

`ModelCoachingEvaluator` is a structural protocol. M20 does not select or endorse a
production evaluator, model, vendor, prompt, credential flow, or human-review
process.

An evaluator result must echo the exact request ID/fingerprint and carry:

```text
judgments[]
evaluator_kind = rules | model | human | fixture
evaluator_id
evaluator_version
run_id
generated_at
```

`run_model_coaching_evaluation` passes a detached canonical copy to the evaluator,
rejects evaluator exceptions, detects request mutation, and binds only a complete
well-formed judgment set.

## Hermetic qualification corpus

`tests/fixtures/m20_model_coaching_cases.json` is deliberately synthetic. It covers:

- a compliant grounded rendering;
- invented centipawn precision / universal move labels;
- promotion of bounded evidence into exact certainty;
- numeric conversion of symbolic mate evidence;
- permanent or causal learner diagnosis;
- invented learner hypotheses;
- unsupported training-selection authority;
- an ambiguous learner claim that must remain inconclusive.

The corpus does not prove that an arbitrary evaluator will classify natural language
correctly. It proves that the M20 request/response contract can represent bounded
pass/fail/unclear judgments, preserve evaluator provenance, and fail closed around
source and policy drift.

## Qualification

Focused M20 suite:

```bash
python -m pytest tests/test_m20_model_coaching_evaluation.py
```

Current coaching regression:

```bash
python -m pytest \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The local M20 qualification requires no model credentials, live provider calls, or
network service. The Stockfish integration remains the repository's independent
engine witness in CI.

## Explicit non-claims

M20 does not establish:

- semantic truthfulness of arbitrary model prose;
- completeness or correctness of an arbitrary evaluator;
- pedagogical optimality or tutoring efficacy;
- production-model or evaluator quality;
- causal learner diagnosis, permanent traits, training efficacy, or mastery;
- production credentials, retries, rate limits, cost/latency policy, or deployment.

M16 remains the deterministic factual grounding ceiling. M19 remains the provenance
boundary for generated prose. M20 adds an explicit, inspectable quality-assessment
contract without collapsing those authorities.
