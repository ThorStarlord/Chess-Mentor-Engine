"""M24 provider/evaluator execution conformance qualification."""

from __future__ import annotations

import json

import pytest
from test_m8_qualification import S13, S14, _through_compare

from chess_mentor_engine.coaching import (
    EVALUATION_DIMENSIONS,
    ModelCoachEndpoint,
    ModelCoachingEvaluationGeneration,
    ModelCoachingEvaluationJudgment,
    ModelCoachingGeneration,
    ModelEvaluatorEndpoint,
    ModelExecutionConformanceError,
    PermanentExternalExecutionError,
    RequestMutationError,
    TransientExternalExecutionError,
    bind_model_coaching_response,
    build_model_coaching_evaluation_request,
    build_model_coaching_request,
    execute_model_coach_provider,
    execute_model_coaching_evaluator,
    run_conformant_model_coaching,
    run_conformant_model_coaching_evaluation,
)

S15 = "2026-09-08T10:15:00-03:00"
S16 = "2026-09-08T10:16:00-03:00"


def _provider_endpoint() -> ModelCoachEndpoint:
    return ModelCoachEndpoint(
        adapter_id="fixture-provider-adapter",
        adapter_version="1",
        provider_id="fixture-provider",
        model_id="fixture-mentor",
        model_version="2026.09",
    )


def _evaluator_endpoint() -> ModelEvaluatorEndpoint:
    return ModelEvaluatorEndpoint(
        adapter_id="fixture-evaluator-adapter",
        adapter_version="1",
        evaluator_kind="fixture",
        evaluator_id="fixture-evaluator",
        evaluator_version="1",
    )


def _judgments():
    return tuple(
        ModelCoachingEvaluationJudgment(
            dimension=dimension,
            verdict="pass",
            rationale=f"Fixture pass for {dimension}.",
        )
        for dimension in EVALUATION_DIMENSIONS
    )


class _Provider:
    def __init__(
        self,
        *,
        failure: Exception | None = None,
        mutate_request: bool = False,
        force_mutate_request: bool = False,
        invalid_result: bool = False,
        **overrides,
    ) -> None:
        self.failure = failure
        self.mutate_request = mutate_request
        self.force_mutate_request = force_mutate_request
        self.invalid_result = invalid_result
        self.overrides = overrides
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        if self.mutate_request:
            request["claim_scope"] = "mutated"
        if self.force_mutate_request:
            dict.__setitem__(request, "claim_scope", "mutated")
        if self.failure is not None:
            raise self.failure
        if self.invalid_result:
            return {"rendered_content": "not typed"}
        values = {
            "request_id": request["request_id"],
            "request_fingerprint": request["fingerprint"],
            "rendered_content": "Review the strongest reply before committing.",
            "provider_id": "fixture-provider",
            "model_id": "fixture-mentor",
            "model_version": "2026.09",
            "run_id": "fixture-provider-run-001",
            "generated_at": S14,
        }
        values.update(self.overrides)
        return ModelCoachingGeneration(**values)


class _Evaluator:
    def __init__(
        self,
        *,
        failure: Exception | None = None,
        mutate_request: bool = False,
        force_mutate_request: bool = False,
        invalid_result: bool = False,
        judgments=None,
        **overrides,
    ) -> None:
        self.failure = failure
        self.mutate_request = mutate_request
        self.force_mutate_request = force_mutate_request
        self.invalid_result = invalid_result
        self.judgments = _judgments() if judgments is None else judgments
        self.overrides = overrides
        self.requests = []

    def evaluate(self, request):
        self.requests.append(request)
        if self.mutate_request:
            request["rendered_content"] = "mutated"
        if self.force_mutate_request:
            dict.__setitem__(request, "rendered_content", "mutated")
        if self.failure is not None:
            raise self.failure
        if self.invalid_result:
            return {"judgments": []}
        values = {
            "request_id": request["request_id"],
            "request_fingerprint": request["fingerprint"],
            "judgments": self.judgments,
            "evaluator_kind": "fixture",
            "evaluator_id": "fixture-evaluator",
            "evaluator_version": "1",
            "run_id": "fixture-evaluator-run-001",
            "generated_at": S16,
        }
        values.update(self.overrides)
        return ModelCoachingEvaluationGeneration(**values)


def _m19_request():
    upstream, session, _ = _through_compare()
    request = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )
    return upstream, session, request


def _m19_sources():
    upstream, session, request = _m19_request()
    generation = ModelCoachingGeneration(
        request_id=request["request_id"],
        request_fingerprint=request["fingerprint"],
        rendered_content="Review the strongest reply before committing.",
        provider_id="fixture-provider",
        model_id="fixture-mentor",
        model_version="2026.09",
        run_id="fixture-provider-run-001",
        generated_at=S14,
    )
    coaching = bind_model_coaching_response(
        request=request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=generation,
    )
    return upstream, session, request, coaching


def _m20_request():
    upstream, session, model_request, coaching = _m19_sources()
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S15,
    )
    return upstream, session, model_request, coaching, request


def test_provider_receives_deep_frozen_detached_request_and_success_is_stable() -> None:
    _, _, request = _m19_request()
    original = json.loads(json.dumps(request))
    provider = _Provider()

    first = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=_provider_endpoint(),
        timeout_ms=2500,
    )
    second = execute_model_coach_provider(
        provider=_Provider(),
        request=request,
        endpoint=_provider_endpoint(),
        timeout_ms=2500,
    )

    assert first.succeeded is True
    assert first.record == second.record
    assert first.record["role"] == "model_coach_provider"
    assert first.record["endpoint"] == _provider_endpoint().to_dict()
    assert first.record["execution_policy"]["timeout_ms"] == 2500
    assert first.record["execution_policy"]["automatic_retry"] is False
    assert first.record["authority_boundary"]["may_create_chess_facts"] is False
    assert provider.requests[0] == request
    assert provider.requests[0] is not request
    assert provider.requests[0]["grounded_feedback"] is not request["grounded_feedback"]
    with pytest.raises(RequestMutationError):
        provider.requests[0]["grounded_feedback"]["claim_scope"] = "tamper"
    assert request == original


@pytest.mark.parametrize(
    ("failure", "kind", "retryable"),
    (
        (TimeoutError("fixture timeout"), "timeout", True),
        (TransientExternalExecutionError("retry later"), "transient", True),
        (PermanentExternalExecutionError("invalid config"), "permanent", False),
        (RuntimeError("unknown adapter failure"), "permanent", False),
    ),
)
def test_provider_failure_classification_is_explicit_and_no_auto_retry(
    failure,
    kind,
    retryable,
) -> None:
    _, _, request = _m19_request()
    provider = _Provider(failure=failure)

    outcome = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=_provider_endpoint(),
        attempt_number=2,
    )

    assert outcome.succeeded is False
    assert outcome.generation is None
    assert outcome.record["failure"]["kind"] == kind
    assert outcome.record["failure"]["retryable"] is retryable
    assert outcome.record["execution_policy"]["attempt_number"] == 2
    assert outcome.record["execution_policy"]["automatic_retry"] is False
    assert len(provider.requests) == 1


def test_provider_failure_record_is_content_deterministic() -> None:
    _, _, request = _m19_request()

    first = execute_model_coach_provider(
        provider=_Provider(failure=TimeoutError("same timeout")),
        request=request,
        endpoint=_provider_endpoint(),
        timeout_ms=1200,
    )
    second = execute_model_coach_provider(
        provider=_Provider(failure=TimeoutError("same timeout")),
        request=request,
        endpoint=_provider_endpoint(),
        timeout_ms=1200,
    )

    assert first.record == second.record
    assert first.record["fingerprint"] == second.record["fingerprint"]


@pytest.mark.parametrize("forced", (False, True))
def test_provider_request_mutation_is_rejected_without_source_mutation(forced) -> None:
    _, _, request = _m19_request()
    original = json.loads(json.dumps(request))
    provider = _Provider(
        mutate_request=not forced,
        force_mutate_request=forced,
    )

    outcome = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=_provider_endpoint(),
    )

    assert outcome.record["failure"]["kind"] == "request_mutation"
    assert outcome.record["failure"]["retryable"] is False
    assert request == original


@pytest.mark.parametrize(
    ("provider", "kind"),
    (
        (_Provider(invalid_result=True), "malformed_response"),
        (_Provider(rendered_content="   "), "malformed_response"),
        (_Provider(request_fingerprint="wrong"), "identity_mismatch"),
        (_Provider(provider_id="other-provider"), "identity_mismatch"),
        (
            _Provider(generated_at="2026-09-08T10:12:00-03:00"),
            "chronology_violation",
        ),
    ),
)
def test_provider_response_contract_failures_are_classified(provider, kind) -> None:
    _, _, request = _m19_request()

    outcome = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=_provider_endpoint(),
    )

    assert outcome.succeeded is False
    assert outcome.record["failure"]["kind"] == kind


def test_invalid_request_chronology_fails_before_provider_invocation() -> None:
    _, _, request = _m19_request()
    request = {**request, "created_at": "not-a-timestamp"}
    provider = _Provider()

    outcome = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=_provider_endpoint(),
    )

    assert outcome.record["failure"]["kind"] == "invalid_request"
    assert provider.requests == []


def test_conformant_provider_runner_preserves_m19_authority_boundary() -> None:
    upstream, session, _ = _through_compare()

    updated, explanation, request, coaching, execution = run_conformant_model_coaching(
        provider=_Provider(),
        endpoint=_provider_endpoint(),
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        request_created_at=S13,
    )

    assert execution["status"] == "succeeded"
    assert updated.state == "explained"
    assert explanation.provenance.actor_kind == "model"
    assert coaching["request_id"] == request["request_id"]
    assert coaching["model_provenance"]["provider_id"] == "fixture-provider"
    assert coaching["grounding_status"] == "request_bound_not_semantically_verified"
    assert "assessment" not in coaching


def test_conformant_provider_failure_exposes_deterministic_record() -> None:
    upstream, session, _ = _through_compare()

    with pytest.raises(ModelExecutionConformanceError) as raised:
        run_conformant_model_coaching(
            provider=_Provider(failure=TimeoutError("fixture timeout")),
            endpoint=_provider_endpoint(),
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            request_created_at=S13,
        )

    record = raised.value.record
    assert record["failure"]["kind"] == "timeout"
    assert record["failure"]["retryable"] is True
    assert session.state == "compared"
    assert session.explanation is None


def test_evaluator_receives_frozen_detached_request_and_records_identity() -> None:
    _, _, _, _, request = _m20_request()
    evaluator = _Evaluator()

    outcome = execute_model_coaching_evaluator(
        evaluator=evaluator,
        request=request,
        endpoint=_evaluator_endpoint(),
        timeout_ms=3000,
    )

    assert outcome.succeeded is True
    assert outcome.record["role"] == "model_coaching_evaluator"
    assert outcome.record["endpoint"] == _evaluator_endpoint().to_dict()
    assert outcome.record["response_ref"]["evaluator_id"] == "fixture-evaluator"
    assert evaluator.requests[0] == request
    assert evaluator.requests[0] is not request
    with pytest.raises(RequestMutationError):
        evaluator.requests[0]["policy"]["allowed_verdicts"].append("invented")


@pytest.mark.parametrize(
    ("evaluator", "kind"),
    (
        (_Evaluator(failure=TimeoutError("fixture timeout")), "timeout"),
        (
            _Evaluator(failure=TransientExternalExecutionError("retry later")),
            "transient",
        ),
        (
            _Evaluator(failure=PermanentExternalExecutionError("invalid config")),
            "permanent",
        ),
        (_Evaluator(mutate_request=True), "request_mutation"),
        (_Evaluator(force_mutate_request=True), "request_mutation"),
        (_Evaluator(invalid_result=True), "malformed_response"),
        (_Evaluator(evaluator_id="wrong-evaluator"), "identity_mismatch"),
        (
            _Evaluator(generated_at="2026-09-08T10:14:00-03:00"),
            "chronology_violation",
        ),
    ),
)
def test_evaluator_execution_failures_are_classified(evaluator, kind) -> None:
    _, _, _, _, request = _m20_request()

    outcome = execute_model_coaching_evaluator(
        evaluator=evaluator,
        request=request,
        endpoint=_evaluator_endpoint(),
    )

    assert outcome.succeeded is False
    assert outcome.record["failure"]["kind"] == kind


def test_evaluator_missing_or_duplicate_dimensions_is_malformed_response() -> None:
    _, _, _, _, request = _m20_request()
    complete = _judgments()

    missing = execute_model_coaching_evaluator(
        evaluator=_Evaluator(judgments=complete[:-1]),
        request=request,
        endpoint=_evaluator_endpoint(),
    )
    duplicate = execute_model_coaching_evaluator(
        evaluator=_Evaluator(judgments=complete[:-1] + (complete[0],)),
        request=request,
        endpoint=_evaluator_endpoint(),
    )

    assert missing.record["failure"]["kind"] == "malformed_response"
    assert duplicate.record["failure"]["kind"] == "malformed_response"


def test_conformant_evaluator_runner_preserves_bounded_m20_status() -> None:
    upstream, session, model_request, coaching = _m19_sources()

    request, evaluation, execution = run_conformant_model_coaching_evaluation(
        evaluator=_Evaluator(),
        endpoint=_evaluator_endpoint(),
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        request_created_at=S15,
    )

    assert execution["status"] == "succeeded"
    assert execution["request_ref"]["request_id"] == request["request_id"]
    assert evaluation["qualification_status"] == (
        "accepted_under_m20_evaluation_policy"
    )
    assert evaluation["truth_status"] == "not_established_by_m20_evaluation"
    assert evaluation["evaluator_provenance"]["kind"] == "fixture"
