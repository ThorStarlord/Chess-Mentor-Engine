"""M25 deterministic coach-review projection over qualified repository records."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    EVALUATION_DIMENSIONS,
    MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_RECORD_SCHEMA_VERSION,
)
from chess_mentor_engine.feedback import FEEDBACK_SCHEMA_VERSION
from chess_mentor_engine.presentation import PRESENTATION_SCHEMA_VERSION
from chess_mentor_engine.tutoring import (
    CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION,
    CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION,
)

COACH_REVIEW_SCHEMA_VERSION = "m25.coach-review-read-model.v1"

_ALLOWED_TUTOR_STATES = {
    "selected",
    "presented",
    "capturing",
    "frozen",
    "revealed",
    "compared",
    "explained",
    "completed",
}
_ALLOWED_EVALUATION_STATUSES = {
    "accepted_under_m20_evaluation_policy",
    "rejected_under_m20_evaluation_policy",
    "inconclusive_under_m20_evaluation_policy",
}
_PRESENTATION_KEYS = {
    "schema_version",
    "subject",
    "score_semantics",
    "root_analysis",
    "played_child_analysis",
    "comparison",
    "evidence_refs",
}
_SCORE_SEMANTICS = {
    "canonical_engine_perspective": "white",
    "display_perspective": "decision_mover",
    "centipawn_unit": "centipawns",
    "mate_representation": "winner_and_plies_to_mate",
    "bound_semantics": "ordering_bound_in_display_perspective",
}
_CANDIDATE_KEYS = {
    "candidate_id",
    "position_id",
    "game_id",
    "comparison_id",
    "selection_policy",
    "signals",
    "eligibility_signal_ids",
    "provenance",
}
_SIGNAL_KEYS = {
    "signal_id",
    "kind",
    "position_id",
    "game_id",
    "comparison_id",
    "schema_version",
    "raw_value",
    "evidence",
    "detail",
}
_BATCH_KEYS = {
    "batch_id",
    "selection_policy",
    "policy_fingerprint",
    "requested_size",
    "actual_size",
    "candidates",
    "control_candidate_ids",
    "source_pool_count",
    "source_candidate_ids",
    "source_pool_fingerprint",
    "quota_outcomes",
    "exclusions",
    "shortfall",
    "control_shortfall",
}
_AUTHORIZATION_KEYS = {
    "schema_version",
    "participant_id",
    "candidate_id",
    "candidate_fingerprint",
    "batch_id",
    "batch_fingerprint",
    "selection_decision",
    "capture_consent",
    "actor_kind",
    "recorded_at",
    "claim_scope",
    "authorization_id",
    "fingerprint",
}
_LAUNCH_KEYS = {
    "schema_version",
    "authorization_ref",
    "candidate_ref",
    "batch_ref",
    "player_decision_context_ref",
    "tutor_session_ref",
    "created_at",
    "claim_scope",
    "authority_boundary",
    "launch_id",
    "fingerprint",
}
_TUTOR_STATE_KEYS = {
    "tutor_session_id",
    "snapshot_fingerprint",
    "state",
}
_FEEDBACK_KEYS = {
    "schema_version",
    "tutor_session_id",
    "tutor_comparison_id",
    "tutor_comparison_fingerprint",
    "hypothesis_context_id",
    "hypothesis_context_fingerprint",
    "evaluation_presentation",
    "policy",
    "sections",
    "rendered_content",
    "created_at",
    "claim_scope",
    "feedback_id",
    "fingerprint",
}
_COACHING_KEYS = {
    "schema_version",
    "request_id",
    "request_fingerprint",
    "grounded_feedback_ref",
    "tutor_session_id",
    "source_tutor_snapshot_fingerprint",
    "tutor_comparison_id",
    "tutor_comparison_fingerprint",
    "hypothesis_context_id",
    "hypothesis_context_fingerprint",
    "model_provenance",
    "rendered_content",
    "created_at",
    "claim_scope",
    "grounding_status",
    "coaching_id",
    "fingerprint",
}
_EVALUATION_KEYS = {
    "schema_version",
    "evaluation_request_id",
    "evaluation_request_fingerprint",
    "model_coaching_ref",
    "model_coaching_request_ref",
    "grounded_feedback_ref",
    "policy_ref",
    "source_integrity",
    "judgments",
    "qualification_status",
    "evaluator_provenance",
    "created_at",
    "claim_scope",
    "truth_status",
    "evaluation_id",
    "fingerprint",
}
_BUNDLE_KEYS = {
    "evaluation_presentation",
    "diagnostic_candidate",
    "diagnostic_batch",
    "authorization",
    "launch",
    "tutor_state",
    "grounded_feedback",
    "model_coaching",
    "model_evaluation",
}


class CoachReviewReadModelError(ValueError):
    """M25 cannot project the supplied records without crossing authority layers."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


def _dict(value: Any, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise CoachReviewReadModelError(f"{label} must be an object")
    return value


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    data = _dict(value, label)
    if set(data) != keys:
        raise CoachReviewReadModelError(f"{label} shape mismatch")
    return data


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise CoachReviewReadModelError(f"{label} must be a non-empty string")
    return value


def _validate_content_identity(
    record: dict[str, Any],
    *,
    id_key: str,
    prefix: str,
    label: str,
) -> None:
    fingerprint = _nonempty(record.get("fingerprint"), f"{label} fingerprint")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {id_key, "fingerprint"}
    }
    expected = _fingerprint(payload)
    if fingerprint != expected:
        raise CoachReviewReadModelError(f"{label} fingerprint mismatch")
    if record.get(id_key) != f"{prefix}_{expected[:20]}":
        raise CoachReviewReadModelError(f"{label} identity mismatch")


def _validate_presentation(value: Any) -> dict[str, Any]:
    presentation = _strict(value, _PRESENTATION_KEYS, "M15 presentation")
    if presentation["schema_version"] != PRESENTATION_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M15 presentation schema mismatch")
    if presentation["score_semantics"] != _SCORE_SEMANTICS:
        raise CoachReviewReadModelError("M15 score semantics drifted")
    subject = _dict(presentation["subject"], "M15 subject")
    comparison = _dict(presentation["comparison"], "M15 comparison")
    for key in ("game_id", "position_id", "side_to_move", "played_move_uci"):
        _nonempty(subject.get(key), f"M15 subject {key}")
    _nonempty(comparison.get("comparison_id"), "M15 comparison id")
    quality = comparison.get("evidence_quality")
    if quality not in {"exact", "bounded", "partial", "incompatible", "unavailable"}:
        raise CoachReviewReadModelError("M15 comparison evidence quality is invalid")
    if quality != "exact" and comparison.get("exact_centipawn_delta_for_mover") is not None:
        raise CoachReviewReadModelError(
            "non-exact M15 evidence exposed an exact centipawn delta"
        )
    for key in ("best_evaluation", "played_evaluation"):
        evaluation = comparison.get(key)
        if evaluation is None:
            continue
        data = _dict(evaluation, f"M15 {key}")
        if data.get("kind") == "mate" and "centipawns" in data:
            raise CoachReviewReadModelError(
                "M15 symbolic mate evidence must not expose centipawns"
            )
    return presentation


def _validate_signal(signal: Any) -> dict[str, Any]:
    data = _strict(signal, _SIGNAL_KEYS, "M18 selection signal")
    payload = {
        key: data[key]
        for key in (
            "kind",
            "position_id",
            "game_id",
            "comparison_id",
            "schema_version",
            "raw_value",
            "evidence",
            "detail",
        )
    }
    if data["signal_id"] != f"signal_{_fingerprint(payload)[:20]}":
        raise CoachReviewReadModelError("M18 selection signal identity mismatch")
    return data


def _validate_candidate(
    value: Any,
    presentation: dict[str, Any],
) -> dict[str, Any]:
    candidate = _strict(value, _CANDIDATE_KEYS, "M18 diagnostic candidate")
    signals = candidate["signals"]
    if type(signals) is not list or not signals:
        raise CoachReviewReadModelError("M18 diagnostic candidate signals are invalid")
    for signal in signals:
        _validate_signal(signal)
    payload = {
        "position_id": candidate["position_id"],
        "game_id": candidate["game_id"],
        "comparison_id": candidate["comparison_id"],
        "selection_policy": candidate["selection_policy"],
        "signal_ids": [item["signal_id"] for item in signals],
        "eligibility_signal_ids": candidate["eligibility_signal_ids"],
        "provenance": candidate["provenance"],
    }
    expected_id = f"candidate_{_fingerprint(payload)[:20]}"
    if candidate["candidate_id"] != expected_id:
        raise CoachReviewReadModelError("M18 diagnostic candidate identity mismatch")
    subject = presentation["subject"]
    comparison = presentation["comparison"]
    if candidate["game_id"] != subject["game_id"]:
        raise CoachReviewReadModelError("M18/M15 game identity mismatch")
    if candidate["position_id"] != subject["position_id"]:
        raise CoachReviewReadModelError("M18/M15 position identity mismatch")
    if candidate["comparison_id"] != comparison["comparison_id"]:
        raise CoachReviewReadModelError("M18/M15 comparison identity mismatch")
    return candidate


def _validate_batch(
    value: Any,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    batch = _strict(value, _BATCH_KEYS, "M18 diagnostic batch")
    candidates = batch["candidates"]
    if type(candidates) is not list:
        raise CoachReviewReadModelError("M18 diagnostic batch candidates are invalid")
    matches = [item for item in candidates if item == candidate]
    if len(matches) != 1:
        raise CoachReviewReadModelError(
            "M18 candidate is not exactly represented in diagnostic batch"
        )
    if candidate["candidate_id"] not in batch["source_candidate_ids"]:
        raise CoachReviewReadModelError(
            "M18 candidate is absent from batch source candidate ids"
        )
    payload = {
        "selection_policy": batch["selection_policy"],
        "policy_fingerprint": batch["policy_fingerprint"],
        "requested_size": batch["requested_size"],
        "candidate_ids": [item["candidate_id"] for item in candidates],
        "control_candidate_ids": batch["control_candidate_ids"],
        "source_candidate_ids": batch["source_candidate_ids"],
        "source_pool_fingerprint": batch["source_pool_fingerprint"],
        "quota_outcomes": batch["quota_outcomes"],
        "exclusions": batch["exclusions"],
        "shortfall": batch["shortfall"],
        "control_shortfall": batch["control_shortfall"],
    }
    if batch["batch_id"] != f"batch_{_fingerprint(payload)[:20]}":
        raise CoachReviewReadModelError("M18 diagnostic batch identity mismatch")
    return batch


def _validate_authorization(
    value: Any,
    *,
    candidate: dict[str, Any],
    batch: dict[str, Any],
) -> dict[str, Any]:
    authorization = _strict(
        value,
        _AUTHORIZATION_KEYS,
        "M21 candidate authorization",
    )
    if (
        authorization["schema_version"]
        != CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION
    ):
        raise CoachReviewReadModelError("M21 authorization schema mismatch")
    if authorization["actor_kind"] != "participant":
        raise CoachReviewReadModelError("M21 authorization is not participant-authored")
    if authorization["selection_decision"] != "selected":
        raise CoachReviewReadModelError("M21 candidate was not selected")
    if authorization["capture_consent"] != "granted":
        raise CoachReviewReadModelError("M21 capture consent was not granted")
    if authorization["claim_scope"] != "participant_candidate_and_capture_authorization":
        raise CoachReviewReadModelError("M21 authorization claim scope mismatch")
    if authorization["candidate_id"] != candidate["candidate_id"]:
        raise CoachReviewReadModelError("M21 authorization candidate mismatch")
    if authorization["candidate_fingerprint"] != _fingerprint(candidate):
        raise CoachReviewReadModelError("M21 authorization candidate fingerprint mismatch")
    if authorization["batch_id"] != batch["batch_id"]:
        raise CoachReviewReadModelError("M21 authorization batch mismatch")
    if authorization["batch_fingerprint"] != _fingerprint(batch):
        raise CoachReviewReadModelError("M21 authorization batch fingerprint mismatch")
    _validate_content_identity(
        authorization,
        id_key="authorization_id",
        prefix="candidate_tutor_auth",
        label="M21 authorization",
    )
    return authorization


def _validate_launch(
    value: Any,
    *,
    authorization: dict[str, Any],
    candidate: dict[str, Any],
    batch: dict[str, Any],
) -> dict[str, Any]:
    launch = _strict(value, _LAUNCH_KEYS, "M21 candidate launch")
    if launch["schema_version"] != CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M21 launch schema mismatch")
    if launch["claim_scope"] != "participant_authorized_candidate_to_tutor_start":
        raise CoachReviewReadModelError("M21 launch claim scope mismatch")
    if launch["authorization_ref"] != {
        "authorization_id": authorization["authorization_id"],
        "fingerprint": authorization["fingerprint"],
    }:
        raise CoachReviewReadModelError("M21 launch authorization reference mismatch")
    if launch["candidate_ref"] != {
        "candidate_id": candidate["candidate_id"],
        "fingerprint": _fingerprint(candidate),
    }:
        raise CoachReviewReadModelError("M21 launch candidate reference mismatch")
    if launch["batch_ref"] != {
        "batch_id": batch["batch_id"],
        "fingerprint": _fingerprint(batch),
    }:
        raise CoachReviewReadModelError("M21 launch batch reference mismatch")
    tutor_ref = _dict(launch["tutor_session_ref"], "M21 launch tutor reference")
    if tutor_ref.get("state") != "selected":
        raise CoachReviewReadModelError("M21 launch must reference selected M8 state")
    _validate_content_identity(
        launch,
        id_key="launch_id",
        prefix="candidate_tutor_launch",
        label="M21 launch",
    )
    return launch


def _validate_tutor_state(
    value: Any,
    *,
    launch: dict[str, Any] | None,
) -> dict[str, Any]:
    state = _strict(value, _TUTOR_STATE_KEYS, "M8 tutor state")
    _nonempty(state["tutor_session_id"], "M8 tutor session id")
    _nonempty(state["snapshot_fingerprint"], "M8 snapshot fingerprint")
    if state["state"] not in _ALLOWED_TUTOR_STATES:
        raise CoachReviewReadModelError("M8 tutor state is invalid")
    if launch is not None:
        launch_ref = launch["tutor_session_ref"]
        if state["tutor_session_id"] != launch_ref["tutor_session_id"]:
            raise CoachReviewReadModelError("M21/M8 tutor session identity mismatch")
    return state


def _validate_feedback_policy(feedback: dict[str, Any]) -> None:
    policy = _dict(feedback["policy"], "M16 policy")
    fingerprint = _nonempty(policy.get("fingerprint"), "M16 policy fingerprint")
    payload = {key: value for key, value in policy.items() if key != "fingerprint"}
    if fingerprint != _fingerprint(payload):
        raise CoachReviewReadModelError("M16 policy fingerprint mismatch")


def _validate_feedback(
    value: Any,
    *,
    presentation: dict[str, Any],
    tutor_state: dict[str, Any] | None,
) -> dict[str, Any]:
    feedback = _strict(value, _FEEDBACK_KEYS, "M16 grounded feedback")
    if feedback["schema_version"] != FEEDBACK_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M16 grounded feedback schema mismatch")
    if feedback["claim_scope"] != "session_local_grounded_feedback":
        raise CoachReviewReadModelError("M16 grounded feedback claim scope mismatch")
    _validate_content_identity(
        feedback,
        id_key="feedback_id",
        prefix="grounded_feedback",
        label="M16 grounded feedback",
    )
    _validate_feedback_policy(feedback)
    reference = _dict(
        feedback["evaluation_presentation"],
        "M16 evaluation presentation reference",
    )
    if reference.get("schema_version") != PRESENTATION_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M16/M15 presentation schema mismatch")
    if reference.get("fingerprint") != _fingerprint(presentation):
        raise CoachReviewReadModelError("M16/M15 presentation fingerprint mismatch")
    if (
        reference.get("decision_comparison_id")
        != presentation["comparison"]["comparison_id"]
    ):
        raise CoachReviewReadModelError("M16/M15 decision comparison mismatch")
    if tutor_state is not None and (
        feedback["tutor_session_id"] != tutor_state["tutor_session_id"]
    ):
        raise CoachReviewReadModelError("M16/M8 tutor session identity mismatch")
    sections = feedback["sections"]
    if type(sections) is not list or not sections:
        raise CoachReviewReadModelError("M16 grounded feedback sections are invalid")
    kinds = [item.get("kind") for item in sections if type(item) is dict]
    if len(kinds) != len(sections) or len(kinds) != len(set(kinds)):
        raise CoachReviewReadModelError("M16 grounded feedback sections are malformed")
    if "objective" not in kinds or "reasoning" not in kinds or "reflection" not in kinds:
        raise CoachReviewReadModelError("M16 required feedback sections are missing")
    return feedback


def _validate_coaching(
    value: Any,
    *,
    feedback: dict[str, Any],
    tutor_state: dict[str, Any] | None,
) -> dict[str, Any]:
    coaching = _strict(value, _COACHING_KEYS, "M19 model coaching")
    if coaching["schema_version"] != MODEL_COACHING_RECORD_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M19 coaching schema mismatch")
    if coaching["claim_scope"] != "session_local_model_rendering":
        raise CoachReviewReadModelError("M19 coaching claim scope mismatch")
    if coaching["grounding_status"] != "request_bound_not_semantically_verified":
        raise CoachReviewReadModelError("M19 grounding status mismatch")
    _validate_content_identity(
        coaching,
        id_key="coaching_id",
        prefix="model_coaching",
        label="M19 model coaching",
    )
    expected_feedback_ref = {
        "schema_version": feedback["schema_version"],
        "feedback_id": feedback["feedback_id"],
        "fingerprint": feedback["fingerprint"],
        "claim_scope": feedback["claim_scope"],
    }
    if coaching["grounded_feedback_ref"] != expected_feedback_ref:
        raise CoachReviewReadModelError("M19/M16 grounded feedback reference mismatch")
    if coaching["tutor_session_id"] != feedback["tutor_session_id"]:
        raise CoachReviewReadModelError("M19/M16 tutor session identity mismatch")
    if tutor_state is not None and (
        coaching["tutor_session_id"] != tutor_state["tutor_session_id"]
    ):
        raise CoachReviewReadModelError("M19/M8 tutor session identity mismatch")
    _nonempty(coaching["rendered_content"], "M19 rendered coaching content")
    return coaching


def _expected_qualification(judgments: list[dict[str, Any]]) -> str:
    verdicts = {item["verdict"] for item in judgments}
    if "fail" in verdicts:
        return "rejected_under_m20_evaluation_policy"
    if "unclear" in verdicts:
        return "inconclusive_under_m20_evaluation_policy"
    return "accepted_under_m20_evaluation_policy"


def _validate_evaluation(
    value: Any,
    *,
    feedback: dict[str, Any],
    coaching: dict[str, Any],
) -> dict[str, Any]:
    evaluation = _strict(value, _EVALUATION_KEYS, "M20 model evaluation")
    if evaluation["schema_version"] != MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION:
        raise CoachReviewReadModelError("M20 evaluation schema mismatch")
    if evaluation["source_integrity"] != "verified_against_exact_m16_m19_sources":
        raise CoachReviewReadModelError("M20 source integrity status mismatch")
    if evaluation["claim_scope"] != "bounded_model_output_quality_assessment":
        raise CoachReviewReadModelError("M20 evaluation claim scope mismatch")
    if evaluation["truth_status"] != "not_established_by_m20_evaluation":
        raise CoachReviewReadModelError("M20 evaluation truth status mismatch")
    if evaluation["qualification_status"] not in _ALLOWED_EVALUATION_STATUSES:
        raise CoachReviewReadModelError("M20 evaluation qualification status is invalid")
    _validate_content_identity(
        evaluation,
        id_key="evaluation_id",
        prefix="model_coaching_evaluation",
        label="M20 model evaluation",
    )
    if evaluation["model_coaching_ref"] != {
        "coaching_id": coaching["coaching_id"],
        "fingerprint": coaching["fingerprint"],
        "schema_version": coaching["schema_version"],
    }:
        raise CoachReviewReadModelError("M20/M19 coaching reference mismatch")
    if evaluation["grounded_feedback_ref"] != {
        "feedback_id": feedback["feedback_id"],
        "fingerprint": feedback["fingerprint"],
        "schema_version": feedback["schema_version"],
    }:
        raise CoachReviewReadModelError("M20/M16 feedback reference mismatch")
    judgments = evaluation["judgments"]
    if type(judgments) is not list:
        raise CoachReviewReadModelError("M20 judgments must be an array")
    dimensions = []
    for judgment in judgments:
        item = _dict(judgment, "M20 judgment")
        if set(item) != {"dimension", "verdict", "rationale"}:
            raise CoachReviewReadModelError("M20 judgment shape mismatch")
        dimensions.append(item["dimension"])
        if item["verdict"] not in {"pass", "fail", "unclear"}:
            raise CoachReviewReadModelError("M20 judgment verdict is invalid")
        _nonempty(item["rationale"], "M20 judgment rationale")
    if len(dimensions) != len(set(dimensions)):
        raise CoachReviewReadModelError("M20 judgment dimensions are duplicated")
    if set(dimensions) != set(EVALUATION_DIMENSIONS):
        raise CoachReviewReadModelError("M20 judgment dimensions are incomplete")
    if evaluation["qualification_status"] != _expected_qualification(judgments):
        raise CoachReviewReadModelError("M20 qualification status contradicts judgments")
    return evaluation


def build_coach_review_read_model(
    *,
    evaluation_presentation: dict[str, Any],
    diagnostic_candidate: dict[str, Any] | None = None,
    diagnostic_batch: dict[str, Any] | None = None,
    authorization: dict[str, Any] | None = None,
    launch: dict[str, Any] | None = None,
    tutor_state: dict[str, Any] | None = None,
    grounded_feedback: dict[str, Any] | None = None,
    model_coaching: dict[str, Any] | None = None,
    model_evaluation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one UI-facing projection without reinterpreting source semantics."""
    presentation = _validate_presentation(evaluation_presentation)

    if (diagnostic_candidate is None) != (diagnostic_batch is None):
        raise CoachReviewReadModelError(
            "M18 candidate and batch must be supplied together"
        )
    if authorization is not None and diagnostic_candidate is None:
        raise CoachReviewReadModelError("M21 authorization requires M18 selection")
    if launch is not None and authorization is None:
        raise CoachReviewReadModelError("M21 launch requires authorization")
    if tutor_state is not None and launch is None:
        raise CoachReviewReadModelError("M8 tutor state requires M21 launch")
    if model_coaching is not None and grounded_feedback is None:
        raise CoachReviewReadModelError("M19 coaching requires M16 grounding")
    if model_evaluation is not None and model_coaching is None:
        raise CoachReviewReadModelError("M20 evaluation requires M19 coaching")

    candidate = None
    batch = None
    authorization_record = None
    launch_record = None
    tutor_state_record = None
    feedback = None
    coaching = None
    evaluation = None

    if diagnostic_candidate is not None:
        candidate = _validate_candidate(diagnostic_candidate, presentation)
        assert diagnostic_batch is not None
        batch = _validate_batch(diagnostic_batch, candidate)
    if authorization is not None:
        assert candidate is not None and batch is not None
        authorization_record = _validate_authorization(
            authorization,
            candidate=candidate,
            batch=batch,
        )
    if launch is not None:
        assert authorization_record is not None
        assert candidate is not None and batch is not None
        launch_record = _validate_launch(
            launch,
            authorization=authorization_record,
            candidate=candidate,
            batch=batch,
        )
    if tutor_state is not None:
        tutor_state_record = _validate_tutor_state(
            tutor_state,
            launch=launch_record,
        )
    if grounded_feedback is not None:
        feedback = _validate_feedback(
            grounded_feedback,
            presentation=presentation,
            tutor_state=tutor_state_record,
        )
    if model_coaching is not None:
        assert feedback is not None
        coaching = _validate_coaching(
            model_coaching,
            feedback=feedback,
            tutor_state=tutor_state_record,
        )
    if model_evaluation is not None:
        assert feedback is not None and coaching is not None
        evaluation = _validate_evaluation(
            model_evaluation,
            feedback=feedback,
            coaching=coaching,
        )

    source_fingerprints = {
        "objective_evidence": _fingerprint(presentation),
        "diagnostic_candidate": None if candidate is None else _fingerprint(candidate),
        "diagnostic_batch": None if batch is None else _fingerprint(batch),
        "authorization": (
            None if authorization_record is None else authorization_record["fingerprint"]
        ),
        "launch": None if launch_record is None else launch_record["fingerprint"],
        "tutor_state": (
            None if tutor_state_record is None else _fingerprint(tutor_state_record)
        ),
        "deterministic_grounding": None if feedback is None else feedback["fingerprint"],
        "model_coaching": None if coaching is None else coaching["fingerprint"],
        "model_evaluation": None if evaluation is None else evaluation["fingerprint"],
    }
    payload = {
        "schema_version": COACH_REVIEW_SCHEMA_VERSION,
        "section_order": [
            "objective_evidence",
            "diagnostic_selection",
            "participant_authority",
            "tutor_state",
            "deterministic_grounding",
            "model_coaching",
            "model_evaluation",
        ],
        "separation_contract": {
            "objective_chess_source": "objective_evidence",
            "score_semantics_source": "objective_evidence.score_semantics",
            "diagnostic_selection_source": "diagnostic_selection",
            "participant_authority_source": "participant_authority",
            "workflow_state_source": "tutor_state",
            "deterministic_feedback_source": "deterministic_grounding",
            "model_language_source": "model_coaching",
            "bounded_quality_assessment_source": "model_evaluation",
            "model_evaluation_truth_status": "not_established_by_m20_evaluation",
        },
        "source_fingerprints": source_fingerprints,
        "objective_evidence": _copy(presentation),
        "diagnostic_selection": (
            None
            if candidate is None or batch is None
            else {
                "claim_scope": "m18_diagnostic_selection_evidence",
                "candidate": _copy(candidate),
                "batch_ref": {
                    "batch_id": batch["batch_id"],
                    "fingerprint": _fingerprint(batch),
                },
            }
        ),
        "participant_authority": (
            None
            if authorization_record is None or launch_record is None
            else {
                "claim_scope": "participant_authorized_tutor_start",
                "authorization": _copy(authorization_record),
                "launch": _copy(launch_record),
            }
        ),
        "tutor_state": (
            None
            if tutor_state_record is None
            else {
                **_copy(tutor_state_record),
                "claim_scope": "m8_workflow_state",
            }
        ),
        "deterministic_grounding": None if feedback is None else _copy(feedback),
        "model_coaching": None if coaching is None else _copy(coaching),
        "model_evaluation": None if evaluation is None else _copy(evaluation),
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "read_model_id": f"coach_review_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def build_coach_review_read_model_from_bundle(value: Any) -> dict[str, Any]:
    """Build M25 from the strict JSON bundle used by the inspection CLI."""
    bundle = _strict(value, _BUNDLE_KEYS, "M25 input bundle")
    return build_coach_review_read_model(**bundle)
