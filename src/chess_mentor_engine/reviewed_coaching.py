"""M26 local operator from a persisted compared tutor checkpoint to M25 review."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    PositionAnalysis,
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    EXECUTION_SCHEMA_VERSION,
    MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION,
    MODEL_COACHING_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_REQUEST_SCHEMA_VERSION,
    ModelCoachEndpoint,
    ModelCoachingEvaluationGeneration,
    ModelCoachingEvaluator,
    ModelCoachingGeneration,
    ModelCoachProvider,
    ModelEvaluatorEndpoint,
    bind_model_coaching_evaluation,
    bind_model_coaching_response,
    build_model_coaching_evaluation_request,
    build_model_coaching_request,
    execute_model_coach_provider,
    execute_model_coaching_evaluator,
)
from chess_mentor_engine.feedback import (
    FEEDBACK_SCHEMA_VERSION,
    compose_grounded_mentor_feedback,
)
from chess_mentor_engine.presentation import build_evaluation_presentation
from chess_mentor_engine.review import (
    COACH_REVIEW_SCHEMA_VERSION,
    build_coach_review_read_model,
)
from chess_mentor_engine.selection import DecisionComparison
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    load_tutor_session,
    prepare_artifact,
)
from chess_mentor_engine.storage.codec import decode_record
from chess_mentor_engine.storage.tutor import SESSION_KIND

M18_QUEUE_KIND = "m18.diagnostic-analysis-queue.v1"
M21_AUTH_KIND = "m21.candidate-tutor-authorization.v1"
M21_LAUNCH_KIND = "m21.candidate-tutor-launch.v1"
M26_SCHEMA_VERSION = "m26.persistent-reviewed-coaching-run.v1"

_QUEUE_KEYS = {
    "schema_version",
    "source",
    "analysis_request",
    "selection_policy",
    "policy_fingerprint",
    "analysis_summary",
    "source_pool",
    "batch",
}
_SOURCE_POOL_KEYS = {
    "ply_index",
    "position_id",
    "side_to_move",
    "played_move_uci",
    "root_analysis",
    "played_child_analysis",
    "decision_comparison",
    "signals",
    "selection",
}
_ANALYSIS_KEYS = {
    "position_id",
    "fen",
    "request_fingerprint",
    "result_fingerprint",
    "status",
    "request",
    "provenance",
    "lines",
    "metrics",
    "termination",
}
_FAILURE_KEYS = {
    "position_id",
    "fen",
    "request_fingerprint",
    "code",
    "message",
}
_COMPARISON_KEYS = {
    "comparison_id",
    "position_id",
    "game_id",
    "played_move_uci",
    "side_to_move",
    "root_analysis_ref",
    "played_evaluation_source",
    "played_analysis_ref",
    "played_root_line_rank",
    "best_move_uci",
    "best_evaluation",
    "played_evaluation",
    "compatibility",
    "comparison_kind",
    "preference",
    "exact_centipawn_delta_for_mover",
    "mate_relation",
    "terminal_outcome",
    "policy",
    "provenance",
    "detail",
}


class PersistentReviewedCoachingError(ValueError):
    """M26 cannot preserve its persisted evidence and authority boundaries."""

    def __init__(
        self,
        message: str,
        *,
        execution_record: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.execution_record = execution_record


@dataclass(frozen=True, slots=True)
class PersistentReviewedCoachingResult:
    """Persisted output references plus the resulting M25 read model."""

    run_record: dict[str, Any]
    run_ref: ArtifactRef
    read_model: dict[str, Any]
    read_model_ref: ArtifactRef
    feedback_ref: ArtifactRef
    model_request_ref: ArtifactRef | None
    provider_execution_ref: ArtifactRef | None
    model_coaching_ref: ArtifactRef | None
    evaluation_request_ref: ArtifactRef | None
    evaluator_execution_ref: ArtifactRef | None
    model_evaluation_ref: ArtifactRef | None


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise PersistentReviewedCoachingError(f"{label} shape mismatch")
    return value


def _one_dependency(
    dependencies: tuple[ArtifactRef, ...],
    *,
    kind: str,
    label: str,
) -> ArtifactRef:
    matches = tuple(item for item in dependencies if item.kind == kind)
    if len(matches) != 1:
        raise PersistentReviewedCoachingError(
            f"{label} must resolve exactly one {kind} dependency"
        )
    return matches[0]


def _find_session_ref(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    artifact_id: str,
) -> ArtifactRef:
    matches = tuple(
        ref
        for ref in store.list_refs(participant_id=participant_id, kind=SESSION_KIND)
        if ref.artifact_id == artifact_id
    )
    if len(matches) != 1:
        raise PersistentReviewedCoachingError(
            "source tutor checkpoint must identify exactly one persisted M8 artifact"
        )
    return matches[0]


def _load_lineage(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    session_ref: ArtifactRef,
) -> tuple[
    dict[str, Any],
    ArtifactRef,
    dict[str, Any],
    ArtifactRef,
    dict[str, Any],
    ArtifactRef,
]:
    session_artifact = store.get(session_ref, participant_id=participant_id)
    launch_ref = _one_dependency(
        session_artifact.dependencies,
        kind=M21_LAUNCH_KIND,
        label="persisted tutor checkpoint",
    )
    launch_artifact = store.get(launch_ref, participant_id=participant_id)
    launch = launch_artifact.payload
    if launch_ref.artifact_id != launch.get("launch_id"):
        raise PersistentReviewedCoachingError(
            "M21 launch storage identity differs from native identity"
        )

    auth_ref = _one_dependency(
        launch_artifact.dependencies,
        kind=M21_AUTH_KIND,
        label="M21 launch",
    )
    auth_artifact = store.get(auth_ref, participant_id=participant_id)
    authorization = auth_artifact.payload
    if auth_ref.artifact_id != authorization.get("authorization_id"):
        raise PersistentReviewedCoachingError(
            "M21 authorization storage identity differs from native identity"
        )

    queue_ref = _one_dependency(
        auth_artifact.dependencies,
        kind=M18_QUEUE_KIND,
        label="M21 authorization",
    )
    queue_artifact = store.get(queue_ref, participant_id=participant_id)
    queue = _strict(queue_artifact.payload, _QUEUE_KEYS, "M18 diagnostic queue")
    if queue["schema_version"] != M18_QUEUE_KIND:
        raise PersistentReviewedCoachingError("M18 diagnostic queue schema mismatch")
    expected_queue_id = f"diagnostic_queue_{_fingerprint(queue)[:20]}"
    if queue_ref.artifact_id != expected_queue_id:
        raise PersistentReviewedCoachingError(
            "M18 queue storage identity does not match exact queue content"
        )
    return queue, queue_ref, authorization, auth_ref, launch, launch_ref


def _evaluation_wire(value: Any, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise PersistentReviewedCoachingError(f"{label} must be an object")
    kind = value.get("kind")
    if value.get("perspective") != "white":
        raise PersistentReviewedCoachingError(
            f"{label} must preserve canonical White perspective"
        )
    if kind == "centipawn":
        data = _strict(
            value,
            {"kind", "perspective", "centipawns", "bound"},
            label,
        )
        return {"centipawns": data["centipawns"], "bound": data["bound"]}
    if kind == "mate":
        data = _strict(
            value,
            {"kind", "perspective", "winner", "plies_to_mate", "bound"},
            label,
        )
        return {
            "winner": data["winner"],
            "plies_to_mate": data["plies_to_mate"],
            "bound": data["bound"],
        }
    raise PersistentReviewedCoachingError(f"{label} has unsupported evaluation kind")


def _analysis_outcome(value: Any, label: str) -> PositionAnalysis | AnalysisFailure:
    data = _strict(
        value,
        {"outcome_type", "record"},
        f"{label} envelope",
    )
    outcome_type = data["outcome_type"]
    record = data["record"]
    if outcome_type == "analysis_failure":
        failure = _strict(record, _FAILURE_KEYS, label)
        return decode_record(failure, AnalysisFailure)
    if outcome_type != "position_analysis":
        raise PersistentReviewedCoachingError(f"{label} outcome type is invalid")

    raw = _strict(record, _ANALYSIS_KEYS, label)
    wire = dict(raw)
    lines = raw["lines"]
    if type(lines) is not list:
        raise PersistentReviewedCoachingError(f"{label} lines must be an array")
    wire_lines: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        item = _strict(
            line,
            {"rank", "root_move_uci", "evaluation", "pv_uci"},
            f"{label} line {index}",
        )
        wire_lines.append(
            {
                **item,
                "evaluation": _evaluation_wire(
                    item["evaluation"],
                    f"{label} line {index} evaluation",
                ),
            }
        )
    wire["lines"] = wire_lines
    analysis = decode_record(wire, PositionAnalysis)
    expected_request = analysis_request_fingerprint(
        fen=analysis.fen,
        request=analysis.request,
        provenance=analysis.provenance,
    )
    if analysis.request_fingerprint != expected_request:
        raise PersistentReviewedCoachingError(
            f"{label} request fingerprint mismatch"
        )
    if analysis.result_fingerprint != analysis_result_fingerprint(analysis):
        raise PersistentReviewedCoachingError(
            f"{label} result fingerprint mismatch"
        )
    return analysis


def _optional_analysis(
    value: Any,
    label: str,
) -> PositionAnalysis | AnalysisFailure | None:
    if value is None:
        return None
    return _analysis_outcome(value, label)


def _decision_comparison(value: Any) -> DecisionComparison:
    raw = _strict(value, _COMPARISON_KEYS, "M4 decision comparison")
    wire = dict(raw)
    for key in ("best_evaluation", "played_evaluation"):
        if raw[key] is not None:
            wire[key] = _evaluation_wire(raw[key], f"M4 {key}")
    comparison = decode_record(wire, DecisionComparison)
    expected_id = (
        "comparison_"
        + _fingerprint(comparison.to_dict(include_comparison_id=False))[:20]
    )
    if comparison.comparison_id != expected_id:
        raise PersistentReviewedCoachingError(
            "M4 decision comparison identity mismatch"
        )
    return comparison


def _source_records(
    queue: dict[str, Any],
    *,
    launch: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    PositionAnalysis,
    PositionAnalysis | AnalysisFailure | None,
    DecisionComparison,
]:
    candidate_ref = launch.get("candidate_ref")
    batch_ref = launch.get("batch_ref")
    if type(candidate_ref) is not dict or type(batch_ref) is not dict:
        raise PersistentReviewedCoachingError(
            "M21 launch source references are invalid"
        )

    batch = queue["batch"]
    if type(batch) is not dict or batch.get("batch_id") != batch_ref.get("batch_id"):
        raise PersistentReviewedCoachingError("M18/M21 diagnostic batch mismatch")
    if batch_ref.get("fingerprint") != _fingerprint(batch):
        raise PersistentReviewedCoachingError(
            "M21 diagnostic batch fingerprint mismatch"
        )

    candidates = batch.get("candidates")
    if type(candidates) is not list:
        raise PersistentReviewedCoachingError("M18 diagnostic candidates are invalid")
    matches = [
        item
        for item in candidates
        if (
            type(item) is dict
            and item.get("candidate_id") == candidate_ref.get("candidate_id")
        )
    ]
    if len(matches) != 1:
        raise PersistentReviewedCoachingError(
            "M21 candidate must resolve exactly one M18 batch member"
        )
    candidate = matches[0]
    if candidate_ref.get("fingerprint") != _fingerprint(candidate):
        raise PersistentReviewedCoachingError("M21 candidate fingerprint mismatch")

    pool = queue["source_pool"]
    if type(pool) is not list:
        raise PersistentReviewedCoachingError("M18 source pool must be an array")
    entries = []
    for index, value in enumerate(pool):
        entry = _strict(value, _SOURCE_POOL_KEYS, f"M18 source pool entry {index}")
        comparison = entry["decision_comparison"]
        if (
            type(comparison) is dict
            and comparison.get("comparison_id") == candidate.get("comparison_id")
            and entry["position_id"] == candidate.get("position_id")
        ):
            entries.append(entry)
    if len(entries) != 1:
        raise PersistentReviewedCoachingError(
            "M18 candidate must resolve exactly one objective source-pool entry"
        )
    entry = entries[0]
    root = _analysis_outcome(entry["root_analysis"], "M3 root analysis")
    if not isinstance(root, PositionAnalysis):
        raise PersistentReviewedCoachingError(
            "reviewed coaching requires retained M3 root analysis evidence"
        )
    played = _optional_analysis(entry["played_child_analysis"], "M3 played analysis")
    comparison = _decision_comparison(entry["decision_comparison"])
    return candidate, batch, root, played, comparison


def _validate_session_source_binding(
    *,
    session: Any,
    candidate: dict[str, Any],
    batch: dict[str, Any],
    launch: dict[str, Any],
) -> None:
    if session.state != "compared" or session.explanation is not None:
        raise PersistentReviewedCoachingError(
            "reviewed coaching requires an unexplained replay-verified compared session"
        )
    launch_session = launch.get("tutor_session_ref")
    if type(launch_session) is not dict:
        raise PersistentReviewedCoachingError("M21 launch tutor reference is invalid")
    if launch_session.get("tutor_session_id") != session.tutor_session_id:
        raise PersistentReviewedCoachingError("M21/M8 tutor session identity mismatch")

    context = session.capture_session.context
    candidate_ref = context.diagnostic_candidate_ref
    batch_ref = context.diagnostic_batch_ref
    if candidate_ref is None or batch_ref is None:
        raise PersistentReviewedCoachingError(
            "persisted M8 context is missing M18 diagnostic source references"
        )
    if (
        candidate_ref.ref_id != candidate["candidate_id"]
        or candidate_ref.fingerprint != _fingerprint(candidate)
    ):
        raise PersistentReviewedCoachingError(
            "persisted M8 candidate reference differs from M18/M21 lineage"
        )
    if (
        batch_ref.ref_id != batch["batch_id"]
        or batch_ref.fingerprint != _fingerprint(batch)
    ):
        raise PersistentReviewedCoachingError(
            "persisted M8 batch reference differs from M18/M21 lineage"
        )


def _execution_or_raise(outcome: Any, label: str) -> Any:
    if outcome.succeeded and outcome.generation is not None:
        return outcome.generation
    failure = outcome.record.get("failure") or {}
    kind = failure.get("kind", "unknown")
    detail = failure.get("detail", "execution failed")
    raise PersistentReviewedCoachingError(
        f"{label} failed [{kind}]: {detail}",
        execution_record=outcome.record,
    )


def _artifact_write(
    kind: str,
    artifact_id: str,
    participant_id: str,
    payload: dict[str, Any],
    dependencies: tuple[ArtifactRef, ...],
) -> tuple[ArtifactWrite, ArtifactRef]:
    write = ArtifactWrite(
        kind,
        artifact_id,
        participant_id,
        payload,
        dependencies,
    )
    return write, prepare_artifact(write)[0]


def _record_ref(record: dict[str, Any], id_key: str) -> dict[str, str]:
    return {
        "schema_version": record["schema_version"],
        id_key: record[id_key],
        "fingerprint": record["fingerprint"],
    }


def run_persistent_reviewed_coaching(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    session_artifact_id: str,
    grounding_created_at: str,
    provider: ModelCoachProvider | None = None,
    provider_endpoint: ModelCoachEndpoint | None = None,
    evaluator: ModelCoachingEvaluator | None = None,
    evaluator_endpoint: ModelEvaluatorEndpoint | None = None,
    evaluation_request_created_at: str | None = None,
    timeout_ms: int = 10_000,
    attempt_number: int = 1,
) -> PersistentReviewedCoachingResult:
    """Build and atomically persist reviewed coaching without advancing M8 state."""
    if not participant_id or not session_artifact_id:
        raise PersistentReviewedCoachingError(
            "participant and session artifact identity must not be empty"
        )
    if (provider is None) != (provider_endpoint is None):
        raise PersistentReviewedCoachingError(
            "provider and provider_endpoint must be supplied together"
        )
    if (evaluator is None) != (evaluator_endpoint is None):
        raise PersistentReviewedCoachingError(
            "evaluator and evaluator_endpoint must be supplied together"
        )
    if evaluator is not None and provider is None:
        raise PersistentReviewedCoachingError(
            "M20 evaluator execution requires M19 model coaching"
        )
    if evaluator is not None and evaluation_request_created_at is None:
        raise PersistentReviewedCoachingError(
            "evaluation_request_created_at is required with an evaluator"
        )
    if evaluator is None and evaluation_request_created_at is not None:
        raise PersistentReviewedCoachingError(
            "evaluation_request_created_at requires an evaluator"
        )

    session_ref = _find_session_ref(
        store,
        participant_id=participant_id,
        artifact_id=session_artifact_id,
    )
    recovered = load_tutor_session(store, session_ref, participant_id=participant_id)
    session = recovered.session
    (
        queue,
        queue_ref,
        authorization,
        auth_ref,
        launch,
        launch_ref,
    ) = _load_lineage(
        store,
        participant_id=participant_id,
        session_ref=session_ref,
    )
    candidate, batch, root_analysis, played_analysis, comparison = _source_records(
        queue,
        launch=launch,
    )
    _validate_session_source_binding(
        session=session,
        candidate=candidate,
        batch=batch,
        launch=launch,
    )

    presentation = build_evaluation_presentation(
        root_analysis=root_analysis,
        comparison=comparison,
        played_analysis=played_analysis,
    )

    model_request: dict[str, Any] | None = None
    provider_execution: dict[str, Any] | None = None
    coaching: dict[str, Any] | None = None
    evaluation_request: dict[str, Any] | None = None
    evaluator_execution: dict[str, Any] | None = None
    model_evaluation: dict[str, Any] | None = None

    if provider is None:
        feedback = compose_grounded_mentor_feedback(
            session=session,
            root_analysis=root_analysis,
            decision_comparison=comparison,
            played_analysis=played_analysis,
            created_at=grounding_created_at,
        )
    else:
        assert provider_endpoint is not None
        model_request = build_model_coaching_request(
            session=session,
            root_analysis=root_analysis,
            decision_comparison=comparison,
            played_analysis=played_analysis,
            created_at=grounding_created_at,
        )
        feedback = model_request["grounded_feedback"]
        provider_outcome = execute_model_coach_provider(
            provider=provider,
            request=model_request,
            endpoint=provider_endpoint,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
        )
        generation = _execution_or_raise(provider_outcome, "M24 model provider")
        if not isinstance(generation, ModelCoachingGeneration):
            raise PersistentReviewedCoachingError(
                "M24 provider returned the wrong generation type"
            )
        provider_execution = provider_outcome.record
        coaching = bind_model_coaching_response(
            request=model_request,
            session=session,
            root_analysis=root_analysis,
            decision_comparison=comparison,
            played_analysis=played_analysis,
            generation=generation,
        )

    if evaluator is not None:
        assert evaluator_endpoint is not None
        assert evaluation_request_created_at is not None
        assert model_request is not None
        assert coaching is not None
        evaluation_request = build_model_coaching_evaluation_request(
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=root_analysis,
            decision_comparison=comparison,
            played_analysis=played_analysis,
            created_at=evaluation_request_created_at,
        )
        evaluator_outcome = execute_model_coaching_evaluator(
            evaluator=evaluator,
            request=evaluation_request,
            endpoint=evaluator_endpoint,
            timeout_ms=timeout_ms,
            attempt_number=attempt_number,
        )
        evaluation_generation = _execution_or_raise(
            evaluator_outcome,
            "M24 model evaluator",
        )
        if not isinstance(
            evaluation_generation,
            ModelCoachingEvaluationGeneration,
        ):
            raise PersistentReviewedCoachingError(
                "M24 evaluator returned the wrong generation type"
            )
        evaluator_execution = evaluator_outcome.record
        model_evaluation = bind_model_coaching_evaluation(
            request=evaluation_request,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=root_analysis,
            decision_comparison=comparison,
            played_analysis=played_analysis,
            generation=evaluation_generation,
        )

    tutor_state = {
        "tutor_session_id": session.tutor_session_id,
        "snapshot_fingerprint": session.snapshot_fingerprint,
        "state": session.state,
    }
    read_model = build_coach_review_read_model(
        evaluation_presentation=presentation,
        diagnostic_candidate=candidate,
        diagnostic_batch=batch,
        authorization=authorization,
        launch=launch,
        tutor_state=tutor_state,
        grounded_feedback=feedback,
        model_coaching=coaching,
        model_evaluation=model_evaluation,
    )

    writes: list[ArtifactWrite] = []
    feedback_write, feedback_ref = _artifact_write(
        FEEDBACK_SCHEMA_VERSION,
        feedback["feedback_id"],
        participant_id,
        feedback,
        (session_ref, queue_ref),
    )
    writes.append(feedback_write)

    model_request_ref = None
    provider_execution_ref = None
    model_coaching_ref = None
    if model_request is not None:
        model_request_write, model_request_ref = _artifact_write(
            MODEL_COACHING_REQUEST_SCHEMA_VERSION,
            model_request["request_id"],
            participant_id,
            model_request,
            (session_ref, feedback_ref),
        )
        writes.append(model_request_write)
        assert provider_execution is not None
        provider_write, provider_execution_ref = _artifact_write(
            EXECUTION_SCHEMA_VERSION,
            provider_execution["execution_id"],
            participant_id,
            provider_execution,
            (model_request_ref,),
        )
        writes.append(provider_write)
        assert coaching is not None
        coaching_write, model_coaching_ref = _artifact_write(
            MODEL_COACHING_RECORD_SCHEMA_VERSION,
            coaching["coaching_id"],
            participant_id,
            coaching,
            (model_request_ref, provider_execution_ref),
        )
        writes.append(coaching_write)

    evaluation_request_ref = None
    evaluator_execution_ref = None
    model_evaluation_ref = None
    if evaluation_request is not None:
        assert model_request_ref is not None
        assert model_coaching_ref is not None
        evaluation_request_write, evaluation_request_ref = _artifact_write(
            MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION,
            evaluation_request["request_id"],
            participant_id,
            evaluation_request,
            (model_request_ref, model_coaching_ref),
        )
        writes.append(evaluation_request_write)
        assert evaluator_execution is not None
        evaluator_write, evaluator_execution_ref = _artifact_write(
            EXECUTION_SCHEMA_VERSION,
            evaluator_execution["execution_id"],
            participant_id,
            evaluator_execution,
            (evaluation_request_ref,),
        )
        writes.append(evaluator_write)
        assert model_evaluation is not None
        evaluation_write, model_evaluation_ref = _artifact_write(
            MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
            model_evaluation["evaluation_id"],
            participant_id,
            model_evaluation,
            (
                evaluation_request_ref,
                evaluator_execution_ref,
                model_coaching_ref,
            ),
        )
        writes.append(evaluation_write)

    review_dependencies = [
        queue_ref,
        auth_ref,
        launch_ref,
        session_ref,
        feedback_ref,
    ]
    if model_coaching_ref is not None:
        review_dependencies.append(model_coaching_ref)
    if model_evaluation_ref is not None:
        review_dependencies.append(model_evaluation_ref)
    review_write, read_model_ref = _artifact_write(
        COACH_REVIEW_SCHEMA_VERSION,
        read_model["read_model_id"],
        participant_id,
        read_model,
        tuple(review_dependencies),
    )
    writes.append(review_write)

    run_payload: dict[str, Any] = {
        "schema_version": M26_SCHEMA_VERSION,
        "participant_id": participant_id,
        "source_session_ref": session_ref.to_dict(),
        "source_tutor_state": tutor_state,
        "source_lineage": {
            "diagnostic_queue_ref": queue_ref.to_dict(),
            "authorization_ref": auth_ref.to_dict(),
            "launch_ref": launch_ref.to_dict(),
        },
        "grounded_feedback_ref": _record_ref(
            feedback,
            "feedback_id",
        ),
        "model_coaching_ref": (
            None if coaching is None else _record_ref(coaching, "coaching_id")
        ),
        "model_evaluation_ref": (
            None
            if model_evaluation is None
            else _record_ref(model_evaluation, "evaluation_id")
        ),
        "coach_review_ref": _record_ref(read_model, "read_model_id"),
        "execution_refs": [
            _record_ref(record, "execution_id")
            for record in (provider_execution, evaluator_execution)
            if record is not None
        ],
        "claim_scope": "repository_local_reviewed_coaching_orchestration",
        "authority_boundary": {
            "advances_tutor_state": False,
            "creates_objective_chess_facts": False,
            "creates_learner_hypotheses": False,
            "selects_training": False,
            "establishes_model_output_truth": False,
            "chooses_production_provider": False,
        },
    }
    run_fingerprint = _fingerprint(run_payload)
    run_record = {
        **run_payload,
        "run_id": f"reviewed_coaching_run_{run_fingerprint[:20]}",
        "fingerprint": run_fingerprint,
    }
    run_dependencies = [session_ref, read_model_ref]
    if provider_execution_ref is not None:
        run_dependencies.append(provider_execution_ref)
    if evaluator_execution_ref is not None:
        run_dependencies.append(evaluator_execution_ref)
    run_write, run_ref = _artifact_write(
        M26_SCHEMA_VERSION,
        run_record["run_id"],
        participant_id,
        run_record,
        tuple(run_dependencies),
    )
    writes.append(run_write)

    store.put_many(tuple(writes))
    return PersistentReviewedCoachingResult(
        run_record=run_record,
        run_ref=run_ref,
        read_model=read_model,
        read_model_ref=read_model_ref,
        feedback_ref=feedback_ref,
        model_request_ref=model_request_ref,
        provider_execution_ref=provider_execution_ref,
        model_coaching_ref=model_coaching_ref,
        evaluation_request_ref=evaluation_request_ref,
        evaluator_execution_ref=evaluator_execution_ref,
        model_evaluation_ref=model_evaluation_ref,
    )
