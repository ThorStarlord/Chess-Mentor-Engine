"""M27 execution ledger and mechanical fidelity qualification for M26 runs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    EXECUTION_SCHEMA_VERSION,
    MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION,
    MODEL_COACHING_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_REQUEST_SCHEMA_VERSION,
)
from chess_mentor_engine.feedback import FEEDBACK_SCHEMA_VERSION
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import (
    M18_QUEUE_KIND,
    M21_AUTH_KIND,
    M21_LAUNCH_KIND,
    M26_SCHEMA_VERSION,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    StoredArtifact,
    prepare_artifact,
)
from chess_mentor_engine.storage.tutor import SESSION_KIND

M27_SCHEMA_VERSION = "m27.reviewed-coaching-execution-ledger.v1"

_RUN_KEYS = {
    "schema_version",
    "participant_id",
    "source_session_ref",
    "source_tutor_state",
    "source_lineage",
    "grounded_feedback_ref",
    "model_coaching_ref",
    "model_evaluation_ref",
    "coach_review_ref",
    "execution_refs",
    "claim_scope",
    "authority_boundary",
    "run_id",
    "fingerprint",
}
_REVIEW_KEYS = {
    "schema_version",
    "section_order",
    "separation_contract",
    "source_fingerprints",
    "objective_evidence",
    "diagnostic_selection",
    "participant_authority",
    "tutor_state",
    "deterministic_grounding",
    "model_coaching",
    "model_evaluation",
    "read_model_id",
    "fingerprint",
}
_EXECUTION_KEYS = {
    "schema_version",
    "role",
    "endpoint",
    "request_ref",
    "execution_policy",
    "status",
    "response_ref",
    "failure",
    "claim_scope",
    "authority_boundary",
    "execution_id",
    "fingerprint",
}
_FIDELITY_CHECKS = (
    "m26_content_identity",
    "m26_dependency_closure",
    "m25_content_identity",
    "m25_source_fingerprints",
    "m18_m21_selection_lineage",
    "m8_source_checkpoint_preservation",
    "m16_grounding_preservation",
    "m19_optional_coaching_preservation",
    "m20_optional_evaluation_preservation",
    "m24_request_response_binding",
)


class ReviewedCoachingLedgerError(ValueError):
    """M27 cannot establish exact mechanical lineage for the requested M26 runs."""


@dataclass(frozen=True, slots=True)
class ReviewedCoachingExecutionLedgerResult:
    """One persisted M27 ledger and its exact M26 dependencies."""

    ledger_record: dict[str, Any]
    ledger_ref: ArtifactRef
    run_refs: tuple[ArtifactRef, ...]


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise ReviewedCoachingLedgerError(f"{label} shape mismatch")
    return value


def _text(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ReviewedCoachingLedgerError(f"{label} must be a non-empty string")
    return value


def _native_identity(
    record: dict[str, Any],
    *,
    schema_version: str,
    id_key: str,
    prefix: str,
    label: str,
) -> None:
    if record.get("schema_version") != schema_version:
        raise ReviewedCoachingLedgerError(f"{label} schema mismatch")
    fingerprint = _text(record.get("fingerprint"), f"{label} fingerprint")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {id_key, "fingerprint"}
    }
    expected = _fingerprint(payload)
    if fingerprint != expected:
        raise ReviewedCoachingLedgerError(f"{label} fingerprint mismatch")
    if record.get(id_key) != f"{prefix}_{expected[:20]}":
        raise ReviewedCoachingLedgerError(f"{label} identity mismatch")


def _record_ref(
    record: dict[str, Any],
    *,
    id_key: str,
) -> dict[str, str]:
    return {
        "schema_version": record["schema_version"],
        id_key: record[id_key],
        "fingerprint": record["fingerprint"],
    }


def _find_ref(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    kind: str,
    artifact_id: str,
) -> ArtifactRef:
    matches = tuple(
        ref
        for ref in store.list_refs(participant_id=participant_id, kind=kind)
        if ref.artifact_id == artifact_id
    )
    if len(matches) != 1:
        raise ReviewedCoachingLedgerError(
            f"expected exactly one {kind} artifact named {artifact_id}"
        )
    return matches[0]


def _dependency(
    artifact: StoredArtifact,
    *,
    kind: str,
    label: str,
) -> ArtifactRef:
    matches = tuple(ref for ref in artifact.dependencies if ref.kind == kind)
    if len(matches) != 1:
        raise ReviewedCoachingLedgerError(
            f"{label} must resolve exactly one {kind} dependency"
        )
    return matches[0]


def _dependency_optional(
    artifact: StoredArtifact,
    *,
    kind: str,
    label: str,
) -> ArtifactRef | None:
    matches = tuple(ref for ref in artifact.dependencies if ref.kind == kind)
    if len(matches) > 1:
        raise ReviewedCoachingLedgerError(
            f"{label} resolves more than one {kind} dependency"
        )
    return None if not matches else matches[0]


def _artifact_ref_matches_record(
    ref: ArtifactRef,
    record: dict[str, Any],
    *,
    id_key: str,
    label: str,
) -> None:
    if ref.artifact_id != record.get(id_key):
        raise ReviewedCoachingLedgerError(f"{label} storage identity mismatch")


def _validate_run_record(
    artifact: StoredArtifact,
    *,
    participant_id: str,
) -> dict[str, Any]:
    run = _strict(artifact.payload, _RUN_KEYS, "M26 run")
    _native_identity(
        run,
        schema_version=M26_SCHEMA_VERSION,
        id_key="run_id",
        prefix="reviewed_coaching_run",
        label="M26 run",
    )
    _artifact_ref_matches_record(
        artifact.ref,
        run,
        id_key="run_id",
        label="M26 run",
    )
    if run["participant_id"] != participant_id:
        raise ReviewedCoachingLedgerError("M26 participant scope mismatch")
    if run["claim_scope"] != "repository_local_reviewed_coaching_orchestration":
        raise ReviewedCoachingLedgerError("M26 claim scope mismatch")
    boundary = run["authority_boundary"]
    expected = {
        "advances_tutor_state": False,
        "creates_objective_chess_facts": False,
        "creates_learner_hypotheses": False,
        "selects_training": False,
        "establishes_model_output_truth": False,
        "chooses_production_provider": False,
    }
    if boundary != expected:
        raise ReviewedCoachingLedgerError("M26 authority boundary drifted")
    if type(run["execution_refs"]) is not list:
        raise ReviewedCoachingLedgerError("M26 execution refs must be an array")
    return run


def _validate_review_identity(
    artifact: StoredArtifact,
) -> dict[str, Any]:
    review = _strict(artifact.payload, _REVIEW_KEYS, "M25 read model")
    _native_identity(
        review,
        schema_version=COACH_REVIEW_SCHEMA_VERSION,
        id_key="read_model_id",
        prefix="coach_review",
        label="M25 read model",
    )
    _artifact_ref_matches_record(
        artifact.ref,
        review,
        id_key="read_model_id",
        label="M25 read model",
    )
    return review


def _validate_request_artifact(
    artifact: StoredArtifact,
    *,
    role: str,
    request_ref: dict[str, Any],
) -> dict[str, Any]:
    request = artifact.payload
    if role == "model_coach_provider":
        schema = MODEL_COACHING_REQUEST_SCHEMA_VERSION
        prefix = "model_coaching_request"
    else:
        schema = MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION
        prefix = "model_coaching_evaluation_request"
    _native_identity(
        request,
        schema_version=schema,
        id_key="request_id",
        prefix=prefix,
        label=f"{role} request",
    )
    _artifact_ref_matches_record(
        artifact.ref,
        request,
        id_key="request_id",
        label=f"{role} request",
    )
    expected = {
        "request_id": request["request_id"],
        "fingerprint": request["fingerprint"],
        "created_at": request["created_at"],
    }
    if request_ref != expected:
        raise ReviewedCoachingLedgerError(
            f"{role} execution request reference mismatch"
        )
    return request


def _validate_execution_identity(record: dict[str, Any], *, label: str) -> None:
    _strict(record, _EXECUTION_KEYS, label)
    _native_identity(
        record,
        schema_version=EXECUTION_SCHEMA_VERSION,
        id_key="execution_id",
        prefix="m24_execution",
        label=label,
    )
    if record["claim_scope"] != "external_execution_conformance_only":
        raise ReviewedCoachingLedgerError(f"{label} claim scope mismatch")
    policy = record["execution_policy"]
    if type(policy) is not dict:
        raise ReviewedCoachingLedgerError(f"{label} execution policy is invalid")
    if policy.get("automatic_retry") is not False:
        raise ReviewedCoachingLedgerError(
            f"{label} must not claim automatic retry"
        )
    attempt = policy.get("attempt_number")
    timeout = policy.get("timeout_ms")
    if type(attempt) is not int or attempt <= 0:
        raise ReviewedCoachingLedgerError(f"{label} attempt number is invalid")
    if type(timeout) is not int or timeout <= 0:
        raise ReviewedCoachingLedgerError(f"{label} timeout is invalid")
    if record["status"] != "succeeded":
        raise ReviewedCoachingLedgerError(
            f"successful M26 run contains failed {label}"
        )
    if record["failure"] is not None:
        raise ReviewedCoachingLedgerError(
            f"successful {label} must not retain a failure payload"
        )
    if type(record["response_ref"]) is not dict:
        raise ReviewedCoachingLedgerError(
            f"successful {label} must retain a response reference"
        )


def _validate_provider_binding(
    execution: dict[str, Any],
    *,
    request: dict[str, Any],
    coaching: dict[str, Any] | None,
) -> None:
    if coaching is None:
        raise ReviewedCoachingLedgerError(
            "provider execution requires persisted M19 coaching"
        )
    if coaching.get("schema_version") != MODEL_COACHING_RECORD_SCHEMA_VERSION:
        raise ReviewedCoachingLedgerError("M19 coaching schema mismatch")
    _native_identity(
        coaching,
        schema_version=MODEL_COACHING_RECORD_SCHEMA_VERSION,
        id_key="coaching_id",
        prefix="model_coaching",
        label="M19 coaching",
    )
    if coaching["request_id"] != request["request_id"]:
        raise ReviewedCoachingLedgerError("M24/M19 request identity mismatch")
    if coaching["request_fingerprint"] != request["fingerprint"]:
        raise ReviewedCoachingLedgerError("M24/M19 request fingerprint mismatch")

    response = execution["response_ref"]
    endpoint = execution["endpoint"]
    provenance = coaching["model_provenance"]
    if response.get("result_type") != "model_coaching_generation":
        raise ReviewedCoachingLedgerError("provider response type mismatch")
    expected = {
        "provider_id": provenance["provider_id"],
        "model_id": provenance["model_id"],
        "model_version": provenance["model_version"],
        "run_id": provenance["run_id"],
        "generated_at": coaching["created_at"],
    }
    for key, value in expected.items():
        if response.get(key) != value:
            raise ReviewedCoachingLedgerError(
                f"provider response {key} differs from M19 coaching"
            )
    for key in ("provider_id", "model_id", "model_version"):
        if endpoint.get(key) != expected[key]:
            raise ReviewedCoachingLedgerError(
                f"provider endpoint {key} differs from M19 coaching"
            )
    _text(response.get("fingerprint"), "provider response fingerprint")


def _validate_evaluator_binding(
    execution: dict[str, Any],
    *,
    request: dict[str, Any],
    evaluation: dict[str, Any] | None,
) -> None:
    if evaluation is None:
        raise ReviewedCoachingLedgerError(
            "evaluator execution requires persisted M20 evaluation"
        )
    _native_identity(
        evaluation,
        schema_version=MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
        id_key="evaluation_id",
        prefix="model_coaching_evaluation",
        label="M20 evaluation",
    )
    if evaluation["evaluation_request_id"] != request["request_id"]:
        raise ReviewedCoachingLedgerError("M24/M20 request identity mismatch")
    if evaluation["evaluation_request_fingerprint"] != request["fingerprint"]:
        raise ReviewedCoachingLedgerError("M24/M20 request fingerprint mismatch")
    if evaluation["truth_status"] != "not_established_by_m20_evaluation":
        raise ReviewedCoachingLedgerError("M20 truth-status boundary drifted")

    response = execution["response_ref"]
    endpoint = execution["endpoint"]
    provenance = evaluation["evaluator_provenance"]
    if response.get("result_type") != "model_coaching_evaluation_generation":
        raise ReviewedCoachingLedgerError("evaluator response type mismatch")
    expected = {
        "evaluator_kind": provenance["kind"],
        "evaluator_id": provenance["evaluator_id"],
        "evaluator_version": provenance["evaluator_version"],
        "run_id": provenance["run_id"],
        "generated_at": evaluation["created_at"],
    }
    for key, value in expected.items():
        if response.get(key) != value:
            raise ReviewedCoachingLedgerError(
                f"evaluator response {key} differs from M20 evaluation"
            )
    for key in ("evaluator_kind", "evaluator_id", "evaluator_version"):
        if endpoint.get(key) != expected[key]:
            raise ReviewedCoachingLedgerError(
                f"evaluator endpoint {key} differs from M20 evaluation"
            )
    _text(response.get("fingerprint"), "evaluator response fingerprint")


def _validate_execution(
    store: LocalArtifactStore,
    artifact: StoredArtifact,
    *,
    participant_id: str,
    coaching: dict[str, Any] | None,
    evaluation: dict[str, Any] | None,
) -> dict[str, Any]:
    record = artifact.payload
    label = "M24 execution"
    _validate_execution_identity(record, label=label)
    _artifact_ref_matches_record(
        artifact.ref,
        record,
        id_key="execution_id",
        label=label,
    )
    role = record["role"]
    if role not in {"model_coach_provider", "model_coaching_evaluator"}:
        raise ReviewedCoachingLedgerError("unsupported M24 execution role")
    request_kind = (
        MODEL_COACHING_REQUEST_SCHEMA_VERSION
        if role == "model_coach_provider"
        else MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION
    )
    if len(artifact.dependencies) != 1:
        raise ReviewedCoachingLedgerError(
            "M24 execution must retain exactly one request dependency"
        )
    request_dependency = _dependency(
        artifact,
        kind=request_kind,
        label="M24 execution",
    )
    request_artifact = store.get(
        request_dependency,
        participant_id=participant_id,
    )
    request = _validate_request_artifact(
        request_artifact,
        role=role,
        request_ref=record["request_ref"],
    )
    if role == "model_coach_provider":
        _validate_provider_binding(
            record,
            request=request,
            coaching=coaching,
        )
    else:
        _validate_evaluator_binding(
            record,
            request=request,
            evaluation=evaluation,
        )
    return {
        "execution_ref": artifact.ref.to_dict(),
        "execution_id": record["execution_id"],
        "fingerprint": record["fingerprint"],
        "role": role,
        "status": record["status"],
        "endpoint": record["endpoint"],
        "request_ref": record["request_ref"],
        "response_ref": record["response_ref"],
        "attempt_number": record["execution_policy"]["attempt_number"],
        "timeout_ms": record["execution_policy"]["timeout_ms"],
        "automatic_retry": False,
    }


def _source_artifacts(
    store: LocalArtifactStore,
    review_artifact: StoredArtifact,
    *,
    participant_id: str,
) -> dict[str, StoredArtifact | None]:
    kinds = (
        M18_QUEUE_KIND,
        M21_AUTH_KIND,
        M21_LAUNCH_KIND,
        SESSION_KIND,
        FEEDBACK_SCHEMA_VERSION,
    )
    sources: dict[str, StoredArtifact | None] = {}
    for kind in kinds:
        ref = _dependency(
            review_artifact,
            kind=kind,
            label="M25 read model",
        )
        sources[kind] = store.get(ref, participant_id=participant_id)
    for kind in (
        MODEL_COACHING_RECORD_SCHEMA_VERSION,
        MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
    ):
        ref = _dependency_optional(
            review_artifact,
            kind=kind,
            label="M25 read model",
        )
        sources[kind] = (
            None if ref is None else store.get(ref, participant_id=participant_id)
        )
    expected_count = 5 + sum(
        1
        for kind in (
            MODEL_COACHING_RECORD_SCHEMA_VERSION,
            MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
        )
        if sources[kind] is not None
    )
    if len(review_artifact.dependencies) != expected_count:
        raise ReviewedCoachingLedgerError(
            "M25 read-model dependency set contains unexpected artifacts"
        )
    return sources


def _validate_review_sources(
    review: dict[str, Any],
    run: dict[str, Any],
    sources: dict[str, StoredArtifact | None],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    queue_artifact = sources[M18_QUEUE_KIND]
    auth_artifact = sources[M21_AUTH_KIND]
    launch_artifact = sources[M21_LAUNCH_KIND]
    session_artifact = sources[SESSION_KIND]
    feedback_artifact = sources[FEEDBACK_SCHEMA_VERSION]
    assert queue_artifact is not None
    assert auth_artifact is not None
    assert launch_artifact is not None
    assert session_artifact is not None
    assert feedback_artifact is not None

    lineage = run["source_lineage"]
    expected_lineage = {
        "diagnostic_queue_ref": queue_artifact.ref.to_dict(),
        "authorization_ref": auth_artifact.ref.to_dict(),
        "launch_ref": launch_artifact.ref.to_dict(),
    }
    if lineage != expected_lineage:
        raise ReviewedCoachingLedgerError("M26 source lineage differs from M25")
    if run["source_session_ref"] != session_artifact.ref.to_dict():
        raise ReviewedCoachingLedgerError("M26/M25 source session reference mismatch")

    authority = review["participant_authority"]
    if type(authority) is not dict:
        raise ReviewedCoachingLedgerError("M25 participant authority is missing")
    if authority.get("authorization") != auth_artifact.payload:
        raise ReviewedCoachingLedgerError("M25/M21 authorization content drifted")
    if authority.get("launch") != launch_artifact.payload:
        raise ReviewedCoachingLedgerError("M25/M21 launch content drifted")

    selection = review["diagnostic_selection"]
    if type(selection) is not dict:
        raise ReviewedCoachingLedgerError("M25 diagnostic selection is missing")
    candidate = selection.get("candidate")
    queue = queue_artifact.payload
    batch = queue.get("batch")
    if type(candidate) is not dict or type(batch) is not dict:
        raise ReviewedCoachingLedgerError("M18 diagnostic content is invalid")
    launch = launch_artifact.payload
    candidate_ref = launch.get("candidate_ref")
    if type(candidate_ref) is not dict:
        raise ReviewedCoachingLedgerError("M21 candidate reference is invalid")
    matches = [
        item
        for item in batch.get("candidates", [])
        if type(item) is dict
        and item.get("candidate_id") == candidate_ref.get("candidate_id")
    ]
    if len(matches) != 1 or candidate != matches[0]:
        raise ReviewedCoachingLedgerError("M25/M18 candidate content drifted")
    expected_batch_ref = {
        "batch_id": batch.get("batch_id"),
        "fingerprint": _fingerprint(batch),
    }
    if selection.get("batch_ref") != expected_batch_ref:
        raise ReviewedCoachingLedgerError("M25/M18 batch reference drifted")

    tutor_state = review["tutor_state"]
    if type(tutor_state) is not dict:
        raise ReviewedCoachingLedgerError("M25 tutor state is missing")
    projected_state = {
        key: tutor_state.get(key)
        for key in ("tutor_session_id", "snapshot_fingerprint", "state")
    }
    if projected_state != run["source_tutor_state"]:
        raise ReviewedCoachingLedgerError("M25/M26 tutor state drifted")

    feedback = feedback_artifact.payload
    _native_identity(
        feedback,
        schema_version=FEEDBACK_SCHEMA_VERSION,
        id_key="feedback_id",
        prefix="grounded_feedback",
        label="M16 feedback",
    )
    if review["deterministic_grounding"] != feedback:
        raise ReviewedCoachingLedgerError("M25/M16 grounding content drifted")
    if run["grounded_feedback_ref"] != _record_ref(
        feedback,
        id_key="feedback_id",
    ):
        raise ReviewedCoachingLedgerError("M26/M16 grounding reference drifted")

    coaching_artifact = sources[MODEL_COACHING_RECORD_SCHEMA_VERSION]
    evaluation_artifact = sources[
        MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION
    ]
    coaching = None if coaching_artifact is None else coaching_artifact.payload
    evaluation = None if evaluation_artifact is None else evaluation_artifact.payload

    if coaching is None:
        if (
            review["model_coaching"] is not None
            or run["model_coaching_ref"] is not None
        ):
            raise ReviewedCoachingLedgerError("M19 optionality drifted")
    else:
        _native_identity(
            coaching,
            schema_version=MODEL_COACHING_RECORD_SCHEMA_VERSION,
            id_key="coaching_id",
            prefix="model_coaching",
            label="M19 coaching",
        )
        if review["model_coaching"] != coaching:
            raise ReviewedCoachingLedgerError("M25/M19 coaching content drifted")
        if run["model_coaching_ref"] != _record_ref(
            coaching,
            id_key="coaching_id",
        ):
            raise ReviewedCoachingLedgerError("M26/M19 coaching reference drifted")

    if evaluation is None:
        if (
            review["model_evaluation"] is not None
            or run["model_evaluation_ref"] is not None
        ):
            raise ReviewedCoachingLedgerError("M20 optionality drifted")
    else:
        _native_identity(
            evaluation,
            schema_version=MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
            id_key="evaluation_id",
            prefix="model_coaching_evaluation",
            label="M20 evaluation",
        )
        if review["model_evaluation"] != evaluation:
            raise ReviewedCoachingLedgerError("M25/M20 evaluation content drifted")
        if run["model_evaluation_ref"] != _record_ref(
            evaluation,
            id_key="evaluation_id",
        ):
            raise ReviewedCoachingLedgerError("M26/M20 evaluation reference drifted")
        if evaluation["truth_status"] != "not_established_by_m20_evaluation":
            raise ReviewedCoachingLedgerError("M20 truth-status boundary drifted")

    source_fingerprints = review["source_fingerprints"]
    expected_fingerprints = {
        "objective_evidence": _fingerprint(review["objective_evidence"]),
        "diagnostic_candidate": _fingerprint(candidate),
        "diagnostic_batch": _fingerprint(batch),
        "authorization": auth_artifact.payload["fingerprint"],
        "launch": launch_artifact.payload["fingerprint"],
        "tutor_state": _fingerprint(run["source_tutor_state"]),
        "deterministic_grounding": feedback["fingerprint"],
        "model_coaching": None if coaching is None else coaching["fingerprint"],
        "model_evaluation": (
            None if evaluation is None else evaluation["fingerprint"]
        ),
    }
    if source_fingerprints != expected_fingerprints:
        raise ReviewedCoachingLedgerError("M25 source fingerprints drifted")
    return coaching, evaluation


def _run_entry(
    store: LocalArtifactStore,
    artifact: StoredArtifact,
    *,
    participant_id: str,
) -> dict[str, Any]:
    run = _validate_run_record(artifact, participant_id=participant_id)
    session_dependency = _dependency(
        artifact,
        kind=SESSION_KIND,
        label="M26 run",
    )
    if session_dependency.to_dict() != run["source_session_ref"]:
        raise ReviewedCoachingLedgerError("M26 session dependency drifted")

    review_dependency = _dependency(
        artifact,
        kind=COACH_REVIEW_SCHEMA_VERSION,
        label="M26 run",
    )
    review_artifact = store.get(
        review_dependency,
        participant_id=participant_id,
    )
    review = _validate_review_identity(review_artifact)
    if run["coach_review_ref"] != _record_ref(
        review,
        id_key="read_model_id",
    ):
        raise ReviewedCoachingLedgerError("M26/M25 review reference drifted")

    sources = _source_artifacts(
        store,
        review_artifact,
        participant_id=participant_id,
    )
    coaching, evaluation = _validate_review_sources(review, run, sources)

    execution_refs = run["execution_refs"]
    stored_execution_refs = tuple(
        ref for ref in artifact.dependencies if ref.kind == EXECUTION_SCHEMA_VERSION
    )
    if len(stored_execution_refs) != len(execution_refs):
        raise ReviewedCoachingLedgerError("M26 execution dependency count drifted")
    expected_dependency_count = 2 + len(stored_execution_refs)
    if len(artifact.dependencies) != expected_dependency_count:
        raise ReviewedCoachingLedgerError(
            "M26 run dependency set contains unexpected artifacts"
        )

    execution_entries: list[dict[str, Any]] = []
    roles: list[str] = []
    for execution_ref in execution_refs:
        if type(execution_ref) is not dict:
            raise ReviewedCoachingLedgerError("M26 execution reference is invalid")
        execution_id = _text(
            execution_ref.get("execution_id"),
            "M26 execution id",
        )
        matches = tuple(
            ref for ref in stored_execution_refs if ref.artifact_id == execution_id
        )
        if len(matches) != 1:
            raise ReviewedCoachingLedgerError(
                "M26 execution reference does not resolve one dependency"
            )
        execution_artifact = store.get(matches[0], participant_id=participant_id)
        record = execution_artifact.payload
        if execution_ref != _record_ref(record, id_key="execution_id"):
            raise ReviewedCoachingLedgerError("M26/M24 execution reference drifted")
        entry = _validate_execution(
            store,
            execution_artifact,
            participant_id=participant_id,
            coaching=coaching,
            evaluation=evaluation,
        )
        execution_entries.append(entry)
        roles.append(entry["role"])

    allowed_roles = (
        (),
        ("model_coach_provider",),
        ("model_coach_provider", "model_coaching_evaluator"),
    )
    if tuple(roles) not in allowed_roles:
        raise ReviewedCoachingLedgerError("M26 execution role sequence is invalid")
    if bool(coaching) != bool(roles):
        raise ReviewedCoachingLedgerError("M19/M24 execution presence drifted")
    if bool(evaluation) != (len(roles) == 2):
        raise ReviewedCoachingLedgerError("M20/M24 evaluator presence drifted")

    fidelity_payload = {
        "run_fingerprint": run["fingerprint"],
        "read_model_fingerprint": review["fingerprint"],
        "source_fingerprints": review["source_fingerprints"],
        "execution_fingerprints": [
            entry["fingerprint"] for entry in execution_entries
        ],
    }
    return {
        "run_ref": artifact.ref.to_dict(),
        "run_id": run["run_id"],
        "source_session_ref": run["source_session_ref"],
        "coach_review_ref": review_dependency.to_dict(),
        "fidelity": {
            "status": "mechanically_verified",
            "signature": _fingerprint(fidelity_payload),
            "checks": list(_FIDELITY_CHECKS),
        },
        "execution_count": len(execution_entries),
        "executions": execution_entries,
    }


def build_reviewed_coaching_execution_ledger(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    run_artifact_ids: tuple[str, ...] | None = None,
) -> ReviewedCoachingExecutionLedgerResult:
    """Verify selected M26 runs and persist a content-addressed M27 ledger."""
    if not participant_id:
        raise ReviewedCoachingLedgerError("participant_id must not be empty")
    available = store.list_refs(
        participant_id=participant_id,
        kind=M26_SCHEMA_VERSION,
    )
    by_id = {ref.artifact_id: ref for ref in available}
    if run_artifact_ids is None:
        selected = tuple(by_id.values())
    else:
        if not run_artifact_ids:
            raise ReviewedCoachingLedgerError("run_artifact_ids must not be empty")
        if len(set(run_artifact_ids)) != len(run_artifact_ids):
            raise ReviewedCoachingLedgerError("run_artifact_ids must be unique")
        missing = tuple(item for item in run_artifact_ids if item not in by_id)
        if missing:
            raise ReviewedCoachingLedgerError(
                f"M26 run artifact not found: {missing[0]}"
            )
        selected = tuple(by_id[item] for item in run_artifact_ids)
    if not selected:
        raise ReviewedCoachingLedgerError("no M26 runs exist for participant")

    selected = tuple(sorted(selected, key=lambda ref: ref.artifact_id))
    entries = [
        _run_entry(
            store,
            store.get(ref, participant_id=participant_id),
            participant_id=participant_id,
        )
        for ref in selected
    ]
    execution_count = sum(entry["execution_count"] for entry in entries)
    provider_count = sum(
        1
        for entry in entries
        for execution in entry["executions"]
        if execution["role"] == "model_coach_provider"
    )
    evaluator_count = sum(
        1
        for entry in entries
        for execution in entry["executions"]
        if execution["role"] == "model_coaching_evaluator"
    )
    deterministic_only = sum(
        1 for entry in entries if entry["execution_count"] == 0
    )

    payload: dict[str, Any] = {
        "schema_version": M27_SCHEMA_VERSION,
        "participant_id": participant_id,
        "run_count": len(entries),
        "runs": entries,
        "summary": {
            "mechanically_verified_runs": len(entries),
            "deterministic_only_runs": deterministic_only,
            "execution_count": execution_count,
            "provider_execution_count": provider_count,
            "evaluator_execution_count": evaluator_count,
        },
        "privacy_contract": {
            "copies_request_payloads": False,
            "copies_model_rendered_content": False,
            "copies_evaluator_rationales": False,
            "copies_participant_response_content": False,
            "retains_content_addressed_references": True,
            "retains_transport_neutral_endpoint_identity": True,
        },
        "fidelity_scope": (
            "mechanical_identity_dependency_and_projection_preservation_only"
        ),
        "claim_scope": "repository_local_execution_ledger_and_fidelity",
        "authority_boundary": {
            "executes_external_calls": False,
            "chooses_production_provider": False,
            "retries_execution": False,
            "creates_objective_chess_facts": False,
            "establishes_model_output_truth": False,
            "claims_pedagogical_quality": False,
        },
    }
    fingerprint = _fingerprint(payload)
    ledger = {
        **payload,
        "ledger_id": f"reviewed_coaching_ledger_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }
    write = ArtifactWrite(
        M27_SCHEMA_VERSION,
        ledger["ledger_id"],
        participant_id,
        ledger,
        selected,
    )
    ledger_ref = prepare_artifact(write)[0]
    store.put_many((write,))
    return ReviewedCoachingExecutionLedgerResult(
        ledger_record=ledger,
        ledger_ref=ledger_ref,
        run_refs=selected,
    )
