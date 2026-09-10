"""M24 provider/evaluator execution conformance without semantic authority expansion."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.selection import DecisionComparison
from chess_mentor_engine.tutoring import TutorExplanation, TutorSession

from .evaluation import (
    EVALUATION_DIMENSIONS,
    ModelCoachingEvaluationGeneration,
    ModelCoachingEvaluator,
    bind_model_coaching_evaluation,
    build_model_coaching_evaluation_request,
)
from .model import (
    ModelCoachingGeneration,
    ModelCoachProvider,
    build_model_coaching_request,
    record_model_coaching_response,
)

EXECUTION_SCHEMA_VERSION = "m24.provider-evaluator-execution.v1"
ExecutionRole: TypeAlias = Literal[
    "model_coach_provider",
    "model_coaching_evaluator",
]
ExecutionFailureKind: TypeAlias = Literal[
    "invalid_request",
    "request_mutation",
    "timeout",
    "transient",
    "permanent",
    "malformed_response",
    "identity_mismatch",
    "chronology_violation",
]
EvaluatorKind: TypeAlias = Literal["rules", "model", "human", "fixture"]


class RequestMutationError(TypeError):
    """An external adapter attempted to mutate its detached M24 request."""


class TransientExternalExecutionError(RuntimeError):
    """Adapter-neutral marker for a retryable external execution failure."""


class PermanentExternalExecutionError(RuntimeError):
    """Adapter-neutral marker for a non-retryable external execution failure."""


class ModelExecutionConformanceError(ValueError):
    """A conformant M24 execution could not yield a usable generation."""

    def __init__(self, message: str, *, record: dict[str, Any]) -> None:
        super().__init__(message)
        self.record = record


class _FrozenDict(dict):
    def _deny(self, *args: object, **kwargs: object) -> None:
        raise RequestMutationError("external adapter attempted to mutate request")

    __setitem__ = _deny
    __delitem__ = _deny
    clear = _deny
    pop = _deny
    popitem = _deny
    setdefault = _deny
    update = _deny
    __ior__ = _deny


class _FrozenList(list):
    def _deny(self, *args: object, **kwargs: object) -> None:
        raise RequestMutationError("external adapter attempted to mutate request")

    __setitem__ = _deny
    __delitem__ = _deny
    append = _deny
    clear = _deny
    extend = _deny
    insert = _deny
    pop = _deny
    remove = _deny
    reverse = _deny
    sort = _deny
    __iadd__ = _deny
    __imul__ = _deny


@dataclass(frozen=True, slots=True)
class ModelCoachEndpoint:
    """Expected identity of one configured M19 provider/model adapter."""

    adapter_id: str
    adapter_version: str
    provider_id: str
    model_id: str
    model_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("adapter_id", self.adapter_id),
            ("adapter_version", self.adapter_version),
            ("provider_id", self.provider_id),
            ("model_id", self.model_id),
            ("model_version", self.model_version),
        ):
            _require_text(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
        }


@dataclass(frozen=True, slots=True)
class ModelEvaluatorEndpoint:
    """Expected identity of one configured M20 evaluator adapter."""

    adapter_id: str
    adapter_version: str
    evaluator_kind: EvaluatorKind
    evaluator_id: str
    evaluator_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("adapter_id", self.adapter_id),
            ("adapter_version", self.adapter_version),
            ("evaluator_id", self.evaluator_id),
            ("evaluator_version", self.evaluator_version),
        ):
            _require_text(name, value)
        if self.evaluator_kind not in {"rules", "model", "human", "fixture"}:
            raise ValueError(f"unsupported evaluator kind: {self.evaluator_kind!r}")

    def to_dict(self) -> dict[str, str]:
        return {
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "evaluator_kind": self.evaluator_kind,
            "evaluator_id": self.evaluator_id,
            "evaluator_version": self.evaluator_version,
        }


Generation: TypeAlias = ModelCoachingGeneration | ModelCoachingEvaluationGeneration


@dataclass(frozen=True, slots=True)
class ConformanceExecutionOutcome:
    """One content-addressed M24 execution record plus an optional typed result."""

    record: dict[str, Any]
    generation: Generation | None

    @property
    def succeeded(self) -> bool:
        return self.record["status"] == "succeeded"


def _require_text(name: str, value: object) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _freeze(value: object) -> object:
    if type(value) is dict:
        return _FrozenDict({key: _freeze(item) for key, item in value.items()})
    if type(value) is list:
        return _FrozenList(_freeze(item) for item in value)
    return value


def _thaw(value: object) -> object:
    if isinstance(value, dict):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_thaw(item) for item in value]
    return value


def _detached_frozen_request(request: dict[str, Any]) -> dict[str, Any]:
    detached = json.loads(canonical_json(request))
    frozen = _freeze(detached)
    assert isinstance(frozen, dict)
    return frozen


def _parse_timestamp(value: object) -> datetime:
    if type(value) is not str or not value:
        raise ValueError("timestamp must be a nonempty string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include an explicit timezone")
    return parsed


def _request_ref(request: dict[str, Any]) -> dict[str, str]:
    for key in ("request_id", "fingerprint", "created_at"):
        if key not in request:
            raise ValueError(f"request is missing {key}")
    _require_text("request_id", request["request_id"])
    _require_text("request fingerprint", request["fingerprint"])
    _require_text("request created_at", request["created_at"])
    return {
        "request_id": request["request_id"],
        "fingerprint": request["fingerprint"],
        "created_at": request["created_at"],
    }


def _validate_invocation(*, timeout_ms: int, attempt_number: int) -> None:
    if type(timeout_ms) is not int or timeout_ms <= 0:
        raise ValueError("timeout_ms must be a positive integer")
    if type(attempt_number) is not int or attempt_number <= 0:
        raise ValueError("attempt_number must be a positive integer")


def _failure_payload(
    kind: ExecutionFailureKind,
    *,
    detail: str,
    exception: Exception | None = None,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "retryable": kind in {"timeout", "transient"},
        "exception_type": None if exception is None else type(exception).__name__,
        "detail": detail,
    }


def _record(
    *,
    role: ExecutionRole,
    endpoint: dict[str, str],
    request: dict[str, Any],
    timeout_ms: int,
    attempt_number: int,
    response_ref: dict[str, Any] | None,
    failure: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": EXECUTION_SCHEMA_VERSION,
        "role": role,
        "endpoint": endpoint,
        "request_ref": _request_ref(request),
        "execution_policy": {
            "timeout_ms": timeout_ms,
            "attempt_number": attempt_number,
            "automatic_retry": False,
            "timeout_enforcement": "adapter_reported",
            "unknown_exception_disposition": "permanent",
        },
        "status": "succeeded" if failure is None else "failed",
        "response_ref": response_ref,
        "failure": failure,
        "claim_scope": "external_execution_conformance_only",
        "authority_boundary": {
            "may_classify_execution": True,
            "may_create_chess_facts": False,
            "may_create_learner_hypotheses": False,
            "may_select_training": False,
            "may_establish_model_output_truth": False,
        },
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "execution_id": f"m24_execution_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _failed_outcome(
    *,
    role: ExecutionRole,
    endpoint: dict[str, str],
    request: dict[str, Any],
    timeout_ms: int,
    attempt_number: int,
    kind: ExecutionFailureKind,
    detail: str,
    exception: Exception | None = None,
) -> ConformanceExecutionOutcome:
    return ConformanceExecutionOutcome(
        record=_record(
            role=role,
            endpoint=endpoint,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            response_ref=None,
            failure=_failure_payload(kind, detail=detail, exception=exception),
        ),
        generation=None,
    )


def _provider_response_ref(generation: ModelCoachingGeneration) -> dict[str, Any]:
    return {
        "result_type": "model_coaching_generation",
        "fingerprint": _fingerprint(generation.to_dict()),
        "provider_id": generation.provider_id,
        "model_id": generation.model_id,
        "model_version": generation.model_version,
        "run_id": generation.run_id,
        "generated_at": generation.generated_at,
    }


def _evaluator_response_ref(
    generation: ModelCoachingEvaluationGeneration,
) -> dict[str, Any]:
    return {
        "result_type": "model_coaching_evaluation_generation",
        "fingerprint": _fingerprint(generation.to_dict()),
        "evaluator_kind": generation.evaluator_kind,
        "evaluator_id": generation.evaluator_id,
        "evaluator_version": generation.evaluator_version,
        "run_id": generation.run_id,
        "generated_at": generation.generated_at,
    }


def _provider_result_failure(
    *,
    generation: object,
    request: dict[str, Any],
    endpoint: ModelCoachEndpoint,
) -> tuple[ExecutionFailureKind, str] | None:
    if not isinstance(generation, ModelCoachingGeneration):
        return "malformed_response", "provider returned a non-M19 generation record"
    if (
        generation.request_id != request["request_id"]
        or generation.request_fingerprint != request["fingerprint"]
    ):
        return "identity_mismatch", "provider generation request echo mismatch"
    actual_identity = (
        generation.provider_id,
        generation.model_id,
        generation.model_version,
    )
    expected_identity = (
        endpoint.provider_id,
        endpoint.model_id,
        endpoint.model_version,
    )
    if actual_identity != expected_identity:
        return "identity_mismatch", "provider/model identity differs from endpoint"
    if not generation.rendered_content.strip():
        return "malformed_response", "provider generation content is blank"
    try:
        request_time = _parse_timestamp(request["created_at"])
        generated_time = _parse_timestamp(generation.generated_at)
    except ValueError as exc:
        return "chronology_violation", str(exc)
    if generated_time < request_time:
        return "chronology_violation", "provider generation predates its request"
    return None


def _evaluator_result_failure(
    *,
    generation: object,
    request: dict[str, Any],
    endpoint: ModelEvaluatorEndpoint,
) -> tuple[ExecutionFailureKind, str] | None:
    if not isinstance(generation, ModelCoachingEvaluationGeneration):
        return "malformed_response", "evaluator returned a non-M20 generation record"
    if (
        generation.request_id != request["request_id"]
        or generation.request_fingerprint != request["fingerprint"]
    ):
        return "identity_mismatch", "evaluator generation request echo mismatch"
    actual_identity = (
        generation.evaluator_kind,
        generation.evaluator_id,
        generation.evaluator_version,
    )
    expected_identity = (
        endpoint.evaluator_kind,
        endpoint.evaluator_id,
        endpoint.evaluator_version,
    )
    if actual_identity != expected_identity:
        return "identity_mismatch", "evaluator identity differs from endpoint"
    dimensions = tuple(item.dimension for item in generation.judgments)
    if len(dimensions) != len(set(dimensions)):
        return "malformed_response", "evaluator dimensions are duplicated"
    if set(dimensions) != set(EVALUATION_DIMENSIONS):
        return "malformed_response", "evaluator omitted a required dimension"
    try:
        request_time = _parse_timestamp(request["created_at"])
        generated_time = _parse_timestamp(generation.generated_at)
    except ValueError as exc:
        return "chronology_violation", str(exc)
    if generated_time < request_time:
        return "chronology_violation", "evaluator generation predates its request"
    return None


def _exception_failure_kind(exc: Exception) -> ExecutionFailureKind:
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, TransientExternalExecutionError):
        return "transient"
    if isinstance(exc, PermanentExternalExecutionError):
        return "permanent"
    return "permanent"


def execute_model_coach_provider(
    *,
    provider: ModelCoachProvider,
    request: dict[str, Any],
    endpoint: ModelCoachEndpoint,
    timeout_ms: int = 10_000,
    attempt_number: int = 1,
) -> ConformanceExecutionOutcome:
    """Invoke M19 through one immutable request and classify execution failure."""
    _validate_invocation(timeout_ms=timeout_ms, attempt_number=attempt_number)
    endpoint_payload = endpoint.to_dict()
    _request_ref(request)
    try:
        _parse_timestamp(request["created_at"])
    except ValueError as exc:
        return _failed_outcome(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="invalid_request",
            detail=str(exc),
            exception=exc,
        )
    provider_request = _detached_frozen_request(request)
    try:
        generation = provider.generate(provider_request)
    except RequestMutationError as exc:
        return _failed_outcome(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="request_mutation",
            detail=str(exc),
            exception=exc,
        )
    except Exception as exc:
        if _thaw(provider_request) != request:
            return _failed_outcome(
                role="model_coach_provider",
                endpoint=endpoint_payload,
                request=request,
                timeout_ms=timeout_ms,
                attempt_number=attempt_number,
                kind="request_mutation",
                detail="provider mutated request before failing",
                exception=exc,
            )
        kind = _exception_failure_kind(exc)
        return _failed_outcome(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind=kind,
            detail=str(exc),
            exception=exc,
        )
    if _thaw(provider_request) != request:
        return _failed_outcome(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="request_mutation",
            detail="provider mutated its detached request",
        )
    failure = _provider_result_failure(
        generation=generation,
        request=request,
        endpoint=endpoint,
    )
    if failure is not None:
        return _failed_outcome(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind=failure[0],
            detail=failure[1],
        )
    assert isinstance(generation, ModelCoachingGeneration)
    return ConformanceExecutionOutcome(
        record=_record(
            role="model_coach_provider",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            response_ref=_provider_response_ref(generation),
            failure=None,
        ),
        generation=generation,
    )


def execute_model_coaching_evaluator(
    *,
    evaluator: ModelCoachingEvaluator,
    request: dict[str, Any],
    endpoint: ModelEvaluatorEndpoint,
    timeout_ms: int = 10_000,
    attempt_number: int = 1,
) -> ConformanceExecutionOutcome:
    """Invoke M20 through one immutable request and classify execution failure."""
    _validate_invocation(timeout_ms=timeout_ms, attempt_number=attempt_number)
    endpoint_payload = endpoint.to_dict()
    _request_ref(request)
    try:
        _parse_timestamp(request["created_at"])
    except ValueError as exc:
        return _failed_outcome(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="invalid_request",
            detail=str(exc),
            exception=exc,
        )
    evaluator_request = _detached_frozen_request(request)
    try:
        generation = evaluator.evaluate(evaluator_request)
    except RequestMutationError as exc:
        return _failed_outcome(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="request_mutation",
            detail=str(exc),
            exception=exc,
        )
    except Exception as exc:
        if _thaw(evaluator_request) != request:
            return _failed_outcome(
                role="model_coaching_evaluator",
                endpoint=endpoint_payload,
                request=request,
                timeout_ms=timeout_ms,
                attempt_number=attempt_number,
                kind="request_mutation",
                detail="evaluator mutated request before failing",
                exception=exc,
            )
        kind = _exception_failure_kind(exc)
        return _failed_outcome(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind=kind,
            detail=str(exc),
            exception=exc,
        )
    if _thaw(evaluator_request) != request:
        return _failed_outcome(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind="request_mutation",
            detail="evaluator mutated its detached request",
        )
    failure = _evaluator_result_failure(
        generation=generation,
        request=request,
        endpoint=endpoint,
    )
    if failure is not None:
        return _failed_outcome(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            kind=failure[0],
            detail=failure[1],
        )
    assert isinstance(generation, ModelCoachingEvaluationGeneration)
    return ConformanceExecutionOutcome(
        record=_record(
            role="model_coaching_evaluator",
            endpoint=endpoint_payload,
            request=request,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
            response_ref=_evaluator_response_ref(generation),
            failure=None,
        ),
        generation=generation,
    )


def _require_generation(
    outcome: ConformanceExecutionOutcome,
    *,
    role: ExecutionRole,
) -> Generation:
    if outcome.generation is not None:
        return outcome.generation
    failure = outcome.record["failure"]
    assert failure is not None
    raise ModelExecutionConformanceError(
        f"{role} execution failed [{failure['kind']}]: {failure['detail']}",
        record=outcome.record,
    )


def run_conformant_model_coaching(
    *,
    provider: ModelCoachProvider,
    endpoint: ModelCoachEndpoint,
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    request_created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
    timeout_ms: int = 10_000,
    attempt_number: int = 1,
) -> tuple[
    TutorSession,
    TutorExplanation,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Run M19 through M24 execution classification and the existing M19 binder."""
    request = build_model_coaching_request(
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=request_created_at,
    )
    outcome = execute_model_coach_provider(
        provider=provider,
        request=request,
        endpoint=endpoint,
        timeout_ms=timeout_ms,
        attempt_number=attempt_number,
    )
    generation = _require_generation(outcome, role="model_coach_provider")
    assert isinstance(generation, ModelCoachingGeneration)
    updated, explanation, coaching = record_model_coaching_response(
        request=request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        generation=generation,
    )
    return updated, explanation, request, coaching, outcome.record


def run_conformant_model_coaching_evaluation(
    *,
    evaluator: ModelCoachingEvaluator,
    endpoint: ModelEvaluatorEndpoint,
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    request_created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
    timeout_ms: int = 10_000,
    attempt_number: int = 1,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Run M20 through M24 execution classification and the existing M20 binder."""
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=request_created_at,
    )
    outcome = execute_model_coaching_evaluator(
        evaluator=evaluator,
        request=request,
        endpoint=endpoint,
        timeout_ms=timeout_ms,
        attempt_number=attempt_number,
    )
    generation = _require_generation(outcome, role="model_coaching_evaluator")
    assert isinstance(generation, ModelCoachingEvaluationGeneration)
    evaluation = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        generation=generation,
    )
    return request, evaluation, outcome.record
