"""M20 bounded evaluation contract for provenance-bound model coaching."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching.model import (
    MODEL_COACHING_RECORD_SCHEMA_VERSION,
    ModelCoachingError,
    ModelCoachingGeneration,
    bind_model_coaching_response,
)
from chess_mentor_engine.presentation import build_evaluation_presentation
from chess_mentor_engine.selection import DecisionComparison
from chess_mentor_engine.tutoring import TutorSession

MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION = (
    "m20.model-coaching-evaluation-request.v1"
)
MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION = (
    "m20.model-coaching-evaluation.v1"
)
_POLICY_ID = "m20-model-coaching-evaluation"
_POLICY_VERSION = "1"

EvaluationDimension = Literal[
    "grounding_consistency",
    "objective_chess_consistency",
    "evidence_sufficiency",
    "uncertainty_preservation",
    "mate_and_bound_preservation",
    "learner_inference_scope",
    "authority_boundary",
]
EvaluationVerdict = Literal["pass", "fail", "unclear"]
EvaluatorKind = Literal["rules", "model", "human", "fixture"]

EVALUATION_DIMENSIONS: tuple[EvaluationDimension, ...] = (
    "grounding_consistency",
    "objective_chess_consistency",
    "evidence_sufficiency",
    "uncertainty_preservation",
    "mate_and_bound_preservation",
    "learner_inference_scope",
    "authority_boundary",
)

_DIMENSION_CRITERIA: dict[EvaluationDimension, str] = {
    "grounding_consistency": (
        "Rendered prose must remain consistent with the exact M16 grounding supplied "
        "in this request."
    ),
    "objective_chess_consistency": (
        "Objective chess claims must not contradict or extend the exact M15/M16 "
        "objective evidence."
    ),
    "evidence_sufficiency": (
        "Every material certainty or conclusion in the prose must be supported by "
        "the supplied evidence at the claimed strength."
    ),
    "uncertainty_preservation": (
        "Partial, bounded, incompatible, unavailable, unclear, or unscorable evidence "
        "must not be promoted to stronger certainty."
    ),
    "mate_and_bound_preservation": (
        "Mate must remain symbolic and score bounds must retain their qualified "
        "ordering semantics rather than becoming invented exact values."
    ),
    "learner_inference_scope": (
        "The prose must not invent learner hypotheses, causal diagnoses, permanent "
        "traits, or stronger M7 claims than the attached context supports."
    ),
    "authority_boundary": (
        "The prose must not create new M6 judgments, M7 hypotheses, M9 training "
        "selections, mastery claims, or other structured authority."
    ),
}

_REQUEST_KEYS = frozenset(
    {
        "request_id",
        "fingerprint",
        "schema_version",
        "model_coaching_ref",
        "model_coaching_request_ref",
        "grounded_feedback",
        "evaluation_presentation",
        "rendered_content",
        "model_provenance",
        "policy",
        "created_at",
        "claim_scope",
    }
)


class ModelCoachingEvaluationError(ValueError):
    """M20 cannot preserve the model-output evaluation contract."""


@dataclass(frozen=True, slots=True)
class ModelCoachingEvaluationJudgment:
    """One bounded evaluator judgment; it is not objective chess truth."""

    dimension: EvaluationDimension
    verdict: EvaluationVerdict
    rationale: str

    def __post_init__(self) -> None:
        if self.dimension not in EVALUATION_DIMENSIONS:
            raise ValueError(f"unsupported evaluation dimension: {self.dimension!r}")
        if self.verdict not in {"pass", "fail", "unclear"}:
            raise ValueError(f"unsupported evaluation verdict: {self.verdict!r}")
        if not self.rationale.strip():
            raise ValueError("evaluation rationale must not be blank")

    def to_dict(self) -> dict[str, str]:
        return {
            "dimension": self.dimension,
            "verdict": self.verdict,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class ModelCoachingEvaluationGeneration:
    """One evaluator result bound to an exact M20 evaluation request."""

    request_id: str
    request_fingerprint: str
    judgments: tuple[ModelCoachingEvaluationJudgment, ...]
    evaluator_kind: EvaluatorKind
    evaluator_id: str
    evaluator_version: str
    run_id: str
    generated_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("request_id", self.request_id),
            ("request_fingerprint", self.request_fingerprint),
            ("evaluator_kind", self.evaluator_kind),
            ("evaluator_id", self.evaluator_id),
            ("evaluator_version", self.evaluator_version),
            ("run_id", self.run_id),
            ("generated_at", self.generated_at),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")
        if self.evaluator_kind not in {"rules", "model", "human", "fixture"}:
            raise ValueError(f"unsupported evaluator kind: {self.evaluator_kind!r}")
        if type(self.judgments) is not tuple:
            raise ValueError("judgments must be a tuple")
        if not self.judgments:
            raise ValueError("judgments must not be empty")
        if any(
            not isinstance(item, ModelCoachingEvaluationJudgment)
            for item in self.judgments
        ):
            raise ValueError("judgments must contain typed evaluation judgments")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "request_fingerprint": self.request_fingerprint,
            "judgments": [item.to_dict() for item in self.judgments],
            "evaluator_kind": self.evaluator_kind,
            "evaluator_id": self.evaluator_id,
            "evaluator_version": self.evaluator_version,
            "run_id": self.run_id,
            "generated_at": self.generated_at,
        }


class ModelCoachingEvaluator(Protocol):
    """Evaluator boundary; evaluator choice is outside M20 qualification."""

    def evaluate(
        self, request: dict[str, Any]
    ) -> ModelCoachingEvaluationGeneration:
        """Assess one exact M20 evaluation request."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise ModelCoachingEvaluationError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ModelCoachingEvaluationError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ModelCoachingEvaluationError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _policy_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "policy_id": _POLICY_ID,
        "version": _POLICY_VERSION,
        "dimensions": [
            {"dimension": item, "criterion": _DIMENSION_CRITERIA[item]}
            for item in EVALUATION_DIMENSIONS
        ],
        "allowed_verdicts": ["pass", "fail", "unclear"],
        "complete_dimension_coverage_required": True,
        "fail_dominates": True,
        "unclear_prevents_acceptance": True,
        "accepted_status": "accepted_under_m20_evaluation_policy",
        "truth_status": "not_established_by_m20_evaluation",
    }
    return {**payload, "fingerprint": _fingerprint(payload)}


def _generation_from_coaching(coaching: dict[str, Any]) -> ModelCoachingGeneration:
    try:
        provenance = coaching["model_provenance"]
        return ModelCoachingGeneration(
            request_id=coaching["request_id"],
            request_fingerprint=coaching["request_fingerprint"],
            rendered_content=coaching["rendered_content"],
            provider_id=provenance["provider_id"],
            model_id=provenance["model_id"],
            model_version=provenance["model_version"],
            run_id=provenance["run_id"],
            generated_at=coaching["created_at"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ModelCoachingEvaluationError(
            "model coaching record shape mismatch"
        ) from exc


def _validate_coaching_against_sources(
    *,
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    played_analysis: PositionAnalysis | AnalysisFailure | None,
) -> None:
    if type(coaching) is not dict:
        raise ModelCoachingEvaluationError("model coaching record must be a dict")
    if coaching.get("schema_version") != MODEL_COACHING_RECORD_SCHEMA_VERSION:
        raise ModelCoachingEvaluationError("model coaching record schema mismatch")
    generation = _generation_from_coaching(coaching)
    try:
        expected = bind_model_coaching_response(
            request=model_coaching_request,
            session=session,
            root_analysis=root_analysis,
            decision_comparison=decision_comparison,
            played_analysis=played_analysis,
            generation=generation,
        )
    except ModelCoachingError as exc:
        raise ModelCoachingEvaluationError(
            f"M19 coaching validation failed: {exc}"
        ) from exc
    if coaching != expected:
        raise ModelCoachingEvaluationError(
            "model coaching record does not match its exact M19 sources"
        )


def build_model_coaching_evaluation_request(
    *,
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Build a content-addressed evaluator packet from exact M16/M19 sources."""
    _validate_coaching_against_sources(
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
    )
    created = _parse_timestamp(created_at)
    if created < _parse_timestamp(coaching["created_at"]):
        raise ModelCoachingEvaluationError(
            "evaluation request cannot predate model coaching"
        )
    presentation = build_evaluation_presentation(
        root_analysis=root_analysis,
        comparison=decision_comparison,
        played_analysis=played_analysis,
    )
    grounded_feedback = model_coaching_request["grounded_feedback"]
    payload: dict[str, Any] = {
        "schema_version": MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION,
        "model_coaching_ref": {
            "coaching_id": coaching["coaching_id"],
            "fingerprint": coaching["fingerprint"],
            "schema_version": coaching["schema_version"],
        },
        "model_coaching_request_ref": {
            "request_id": model_coaching_request["request_id"],
            "fingerprint": model_coaching_request["fingerprint"],
            "schema_version": model_coaching_request["schema_version"],
        },
        "grounded_feedback": grounded_feedback,
        "evaluation_presentation": presentation,
        "rendered_content": coaching["rendered_content"],
        "model_provenance": coaching["model_provenance"],
        "policy": _policy_payload(),
        "created_at": created_at,
        "claim_scope": "model_output_evaluation_request",
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "request_id": f"model_coaching_evaluation_request_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _validate_request_identity(request: dict[str, Any]) -> None:
    if type(request) is not dict or set(request) != _REQUEST_KEYS:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request shape mismatch"
        )
    if request["schema_version"] != MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request schema mismatch"
        )
    payload = {
        key: value
        for key, value in request.items()
        if key not in {"request_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    if request["fingerprint"] != fingerprint:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request fingerprint mismatch"
        )
    expected_id = f"model_coaching_evaluation_request_{fingerprint[:20]}"
    if request["request_id"] != expected_id:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request identity mismatch"
        )
    if request["policy"] != _policy_payload():
        raise ModelCoachingEvaluationError(
            "model coaching evaluation policy mismatch"
        )


def _validate_request_against_sources(
    *,
    request: dict[str, Any],
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    played_analysis: PositionAnalysis | AnalysisFailure | None,
) -> None:
    _validate_request_identity(request)
    created_at = request["created_at"]
    if type(created_at) is not str:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request created_at must be a string"
        )
    expected = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=created_at,
    )
    if request != expected:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation request does not match current sources"
        )


def _validate_judgments(
    judgments: tuple[ModelCoachingEvaluationJudgment, ...],
) -> None:
    dimensions = tuple(item.dimension for item in judgments)
    if len(dimensions) != len(set(dimensions)):
        raise ModelCoachingEvaluationError(
            "model coaching evaluation dimensions must be unique"
        )
    if set(dimensions) != set(EVALUATION_DIMENSIONS):
        raise ModelCoachingEvaluationError(
            "model coaching evaluation must cover every required dimension"
        )


def _qualification_status(
    judgments: tuple[ModelCoachingEvaluationJudgment, ...],
) -> str:
    verdicts = {item.verdict for item in judgments}
    if "fail" in verdicts:
        return "rejected_under_m20_evaluation_policy"
    if "unclear" in verdicts:
        return "inconclusive_under_m20_evaluation_policy"
    return "accepted_under_m20_evaluation_policy"


def bind_model_coaching_evaluation(
    *,
    request: dict[str, Any],
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    generation: ModelCoachingEvaluationGeneration,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Bind complete evaluator judgments without promoting them to objective truth."""
    _validate_request_against_sources(
        request=request,
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
    )
    if not isinstance(generation, ModelCoachingEvaluationGeneration):
        raise ModelCoachingEvaluationError(
            "model coaching evaluator returned an invalid generation record"
        )
    if generation.request_id != request["request_id"]:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation generation request identity mismatch"
        )
    if generation.request_fingerprint != request["fingerprint"]:
        raise ModelCoachingEvaluationError(
            "model coaching evaluation generation request fingerprint mismatch"
        )
    if _parse_timestamp(generation.generated_at) < _parse_timestamp(
        request["created_at"]
    ):
        raise ModelCoachingEvaluationError(
            "model coaching evaluation cannot predate its request"
        )
    _validate_judgments(generation.judgments)

    ordered = tuple(
        next(item for item in generation.judgments if item.dimension == dimension)
        for dimension in EVALUATION_DIMENSIONS
    )
    payload: dict[str, Any] = {
        "schema_version": MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
        "evaluation_request_id": request["request_id"],
        "evaluation_request_fingerprint": request["fingerprint"],
        "model_coaching_ref": request["model_coaching_ref"],
        "model_coaching_request_ref": request["model_coaching_request_ref"],
        "grounded_feedback_ref": {
            "feedback_id": request["grounded_feedback"]["feedback_id"],
            "fingerprint": request["grounded_feedback"]["fingerprint"],
            "schema_version": request["grounded_feedback"]["schema_version"],
        },
        "policy_ref": {
            "policy_id": request["policy"]["policy_id"],
            "version": request["policy"]["version"],
            "fingerprint": request["policy"]["fingerprint"],
        },
        "source_integrity": "verified_against_exact_m16_m19_sources",
        "judgments": [item.to_dict() for item in ordered],
        "qualification_status": _qualification_status(ordered),
        "evaluator_provenance": {
            "kind": generation.evaluator_kind,
            "evaluator_id": generation.evaluator_id,
            "evaluator_version": generation.evaluator_version,
            "run_id": generation.run_id,
        },
        "created_at": generation.generated_at,
        "claim_scope": "bounded_model_output_quality_assessment",
        "truth_status": "not_established_by_m20_evaluation",
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "evaluation_id": f"model_coaching_evaluation_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def run_model_coaching_evaluation(
    *,
    evaluator: ModelCoachingEvaluator,
    coaching: dict[str, Any],
    model_coaching_request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    request_created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build one request, invoke one evaluator, and bind its bounded assessment."""
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_coaching_request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=request_created_at,
    )
    evaluator_request = json.loads(canonical_json(request))
    try:
        generation = evaluator.evaluate(evaluator_request)
    except Exception as exc:
        raise ModelCoachingEvaluationError(
            f"model coaching evaluator failed: {exc}"
        ) from exc
    if evaluator_request != request:
        raise ModelCoachingEvaluationError(
            "model coaching evaluator mutated the evaluation request"
        )
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
    return request, evaluation
