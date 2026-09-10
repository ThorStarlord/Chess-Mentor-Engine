"""M19 provider-neutral model coaching over the qualified M16 grounding boundary."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.feedback import (
    FEEDBACK_SCHEMA_VERSION,
    GroundedFeedbackError,
    compose_grounded_mentor_feedback,
)
from chess_mentor_engine.selection import DecisionComparison
from chess_mentor_engine.tutoring import (
    TutorExplanation,
    TutorExplanationProvenance,
    TutorSession,
    TutorSessionError,
    record_tutor_explanation,
)

MODEL_COACHING_REQUEST_SCHEMA_VERSION = "m19.model-coaching-request.v1"
MODEL_COACHING_RECORD_SCHEMA_VERSION = "m19.provenance-bound-mentor-coaching.v1"
_INSTRUCTION_ID = "m19-provenance-bound-mentor-coaching"
_INSTRUCTION_VERSION = "1"

_REQUEST_KEYS = frozenset(
    {
        "request_id",
        "fingerprint",
        "schema_version",
        "tutor_session_id",
        "tutor_snapshot_fingerprint",
        "tutor_comparison_id",
        "tutor_comparison_fingerprint",
        "hypothesis_context_id",
        "hypothesis_context_fingerprint",
        "grounded_feedback",
        "instruction",
        "created_at",
        "claim_scope",
    }
)


class ModelCoachingError(ValueError):
    """M19 cannot preserve the model-coaching grounding contract."""


@dataclass(frozen=True, slots=True)
class ModelCoachingGeneration:
    """One provider result explicitly bound to an exact M19 request."""

    request_id: str
    request_fingerprint: str
    rendered_content: str
    provider_id: str
    model_id: str
    model_version: str
    run_id: str
    generated_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("request_id", self.request_id),
            ("request_fingerprint", self.request_fingerprint),
            ("rendered_content", self.rendered_content),
            ("provider_id", self.provider_id),
            ("model_id", self.model_id),
            ("model_version", self.model_version),
            ("run_id", self.run_id),
            ("generated_at", self.generated_at),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "request_id": self.request_id,
            "request_fingerprint": self.request_fingerprint,
            "rendered_content": self.rendered_content,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "run_id": self.run_id,
            "generated_at": self.generated_at,
        }


class ModelCoachProvider(Protocol):
    """Provider boundary; transport and vendor choice remain outside M19."""

    def generate(self, request: dict[str, Any]) -> ModelCoachingGeneration:
        """Generate prose for one exact M19 request."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise ModelCoachingError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ModelCoachingError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ModelCoachingError("timestamp must include an explicit timezone")
    return parsed


def _instruction_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "instruction_id": _INSTRUCTION_ID,
        "version": _INSTRUCTION_VERSION,
        "source_schema_version": FEEDBACK_SCHEMA_VERSION,
        "model_role": "language_renderer_only",
        "allowed_responsibilities": [
            "human_readable_chess_explanation",
            "socratic_reflection",
            "evidence_and_uncertainty_explanation",
        ],
        "forbidden_authority_changes": [
            "new_objective_chess_facts",
            "new_m6_reasoning_judgments",
            "new_m7_learner_hypotheses",
            "m9_training_selection",
            "causal_or_mastery_claims",
        ],
        "non_exact_score_rule": "preserve_non_exact_evidence",
        "mate_rule": "keep_symbolic_mate",
        "output_contract": "plain_prose_only",
    }
    return {**payload, "fingerprint": _fingerprint(payload)}


def build_model_coaching_request(
    *,
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Build the exact structured grounding packet sent to a model provider."""
    try:
        feedback = compose_grounded_mentor_feedback(
            session=session,
            root_analysis=root_analysis,
            decision_comparison=decision_comparison,
            played_analysis=played_analysis,
            created_at=created_at,
        )
    except GroundedFeedbackError as exc:
        raise ModelCoachingError(
            f"M16 grounded feedback rejected coaching evidence: {exc}"
        ) from exc

    comparison = session.comparison
    assert comparison is not None
    context = session.hypothesis_context
    payload: dict[str, Any] = {
        "schema_version": MODEL_COACHING_REQUEST_SCHEMA_VERSION,
        "tutor_session_id": session.tutor_session_id,
        "tutor_snapshot_fingerprint": session.snapshot_fingerprint,
        "tutor_comparison_id": comparison.comparison_id,
        "tutor_comparison_fingerprint": comparison.fingerprint,
        "hypothesis_context_id": None if context is None else context.context_id,
        "hypothesis_context_fingerprint": (
            None if context is None else context.fingerprint
        ),
        "grounded_feedback": feedback,
        "instruction": _instruction_payload(),
        "created_at": created_at,
        "claim_scope": "model_language_rendering_request",
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "request_id": f"model_coaching_request_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _validate_request_identity(request: dict[str, Any]) -> None:
    if type(request) is not dict or set(request) != _REQUEST_KEYS:
        raise ModelCoachingError("model coaching request shape mismatch")
    if request["schema_version"] != MODEL_COACHING_REQUEST_SCHEMA_VERSION:
        raise ModelCoachingError("model coaching request schema mismatch")
    payload = {
        key: value
        for key, value in request.items()
        if key not in {"request_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    if request["fingerprint"] != fingerprint:
        raise ModelCoachingError("model coaching request fingerprint mismatch")
    expected_id = f"model_coaching_request_{fingerprint[:20]}"
    if request["request_id"] != expected_id:
        raise ModelCoachingError("model coaching request identity mismatch")
    if request["instruction"] != _instruction_payload():
        raise ModelCoachingError("model coaching instruction contract mismatch")


def _validate_request_against_sources(
    *,
    request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    played_analysis: PositionAnalysis | AnalysisFailure | None,
) -> None:
    _validate_request_identity(request)
    created_at = request["created_at"]
    if type(created_at) is not str:
        raise ModelCoachingError("model coaching request created_at must be a string")
    expected = build_model_coaching_request(
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=created_at,
    )
    if request != expected:
        raise ModelCoachingError(
            "model coaching request does not match current grounded evidence"
        )


def bind_model_coaching_response(
    *,
    request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    generation: ModelCoachingGeneration,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Bind model prose to exact M16 grounding without granting new fact authority."""
    _validate_request_against_sources(
        request=request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
    )
    if not isinstance(generation, ModelCoachingGeneration):
        raise ModelCoachingError("model provider returned an invalid generation record")
    if generation.request_id != request["request_id"]:
        raise ModelCoachingError("model generation request identity mismatch")
    if generation.request_fingerprint != request["fingerprint"]:
        raise ModelCoachingError("model generation request fingerprint mismatch")
    if not generation.rendered_content.strip():
        raise ModelCoachingError("model generation content must not be blank")
    if _parse_timestamp(generation.generated_at) < _parse_timestamp(
        request["created_at"]
    ):
        raise ModelCoachingError(
            "model generation cannot predate its grounding request"
        )

    feedback = request["grounded_feedback"]
    payload: dict[str, Any] = {
        "schema_version": MODEL_COACHING_RECORD_SCHEMA_VERSION,
        "request_id": request["request_id"],
        "request_fingerprint": request["fingerprint"],
        "grounded_feedback_ref": {
            "schema_version": feedback["schema_version"],
            "feedback_id": feedback["feedback_id"],
            "fingerprint": feedback["fingerprint"],
            "claim_scope": feedback["claim_scope"],
        },
        "tutor_session_id": session.tutor_session_id,
        "source_tutor_snapshot_fingerprint": session.snapshot_fingerprint,
        "tutor_comparison_id": request["tutor_comparison_id"],
        "tutor_comparison_fingerprint": request["tutor_comparison_fingerprint"],
        "hypothesis_context_id": request["hypothesis_context_id"],
        "hypothesis_context_fingerprint": request[
            "hypothesis_context_fingerprint"
        ],
        "model_provenance": {
            "provider_id": generation.provider_id,
            "model_id": generation.model_id,
            "model_version": generation.model_version,
            "run_id": generation.run_id,
        },
        "rendered_content": generation.rendered_content,
        "created_at": generation.generated_at,
        "claim_scope": "session_local_model_rendering",
        "grounding_status": "request_bound_not_semantically_verified",
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "coaching_id": f"model_coaching_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def record_model_coaching_response(
    *,
    request: dict[str, Any],
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    generation: ModelCoachingGeneration,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> tuple[TutorSession, TutorExplanation, dict[str, Any]]:
    """Record exact request-bound model prose through the qualified M8 transition."""
    coaching = bind_model_coaching_response(
        request=request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        generation=generation,
    )
    provenance = TutorExplanationProvenance(
        actor_kind="model",
        actor_id=f"{generation.provider_id}:{generation.model_id}",
        actor_version=generation.model_version,
        instruction_fingerprint=request["instruction"]["fingerprint"],
        run_id=generation.run_id,
    )
    try:
        updated, explanation = record_tutor_explanation(
            session,
            rendered_content=generation.rendered_content,
            provenance=provenance,
            created_at=generation.generated_at,
        )
    except TutorSessionError as exc:
        raise ModelCoachingError(
            f"M8 explanation transition rejected model coaching: {exc}"
        ) from exc
    return updated, explanation, coaching


def run_model_coaching(
    *,
    provider: ModelCoachProvider,
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    request_created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> tuple[TutorSession, TutorExplanation, dict[str, Any], dict[str, Any]]:
    """Build grounding, invoke one provider, validate, and record one M8 explanation."""
    request = build_model_coaching_request(
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=request_created_at,
    )
    provider_request = json.loads(canonical_json(request))
    try:
        generation = provider.generate(provider_request)
    except Exception as exc:
        raise ModelCoachingError(f"model provider failed: {exc}") from exc
    if provider_request != request:
        raise ModelCoachingError("model provider mutated the coaching request")
    updated, explanation, coaching = record_model_coaching_response(
        request=request,
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        generation=generation,
    )
    return updated, explanation, request, coaching
