"""CLI adapter for the V1 local tutor vertical slice.

The command composes M18 -> M45 -> M23/M8 -> M46 without acquiring any authority
owned by those contracts. Existing ``cme tutor`` transitions remain M8 execution
and exposure authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, TypeVar

from chess_mentor_engine.candidate_tutor_cli import (
    M18_QUEUE_KIND,
    CandidateTutorCliError,
    _run as _run_candidate_tutor,
    _validate_queue,
)
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    LearnerProgressView,
    TransferRetestPlan,
    build_default_mentor_queue_policy,
)
from chess_mentor_engine.local_tutor import (
    LocalTutorWorkflowError,
    _resolve_hypothesis_id,
    build_local_tutor_workflow,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
)
from chess_mentor_engine.storage.codec import decode_record
from chess_mentor_engine.storage.tutor import SESSION_KIND
from chess_mentor_engine.tutoring import (
    CandidateTutorOrchestrationError,
    build_default_adaptive_tutor_policy,
)

T = TypeVar("T")
LOCAL_TUTOR_START_SCHEMA_VERSION = "v1.local-tutor-start.v1"
LOCAL_TUTOR_NEXT_SCHEMA_VERSION = "v1.local-tutor-next.v1"


class LocalTutorCliError(ValueError):
    """The local V1 consumer cannot preserve its required exact source contracts."""


def _positive(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return parsed


def _json_value(path_value: str) -> Any:
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        raise LocalTutorCliError(f"JSON file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _record_file(path_value: str, schema: type[T], *, label: str) -> T:
    value = _json_value(path_value)
    if type(value) is not dict:
        raise LocalTutorCliError(f"{label} must be a JSON object")
    return decode_record(value, schema)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _batch_source_ref(queue: dict[str, Any]) -> EvidenceSynthesisReference:
    fingerprint = _digest(queue)
    return EvidenceSynthesisReference(
        M18_QUEUE_KIND,
        f"diagnostic_queue_{fingerprint[:20]}",
        fingerprint,
    )


def _load_inputs(args: argparse.Namespace):
    try:
        queue, _, batch = _validate_queue(_json_value(args.diagnostic_json))
    except CandidateTutorCliError as exc:
        raise LocalTutorCliError(str(exc)) from exc
    view = _record_file(
        args.learner_progress_json,
        LearnerProgressView,
        label="M44 learner-progress view",
    )
    plans = tuple(
        _record_file(path, TransferRetestPlan, label="M42 transfer plan")
        for path in args.transfer_plan_json
    )
    if view.participant_id != args.participant:
        raise LocalTutorCliError(
            "M44 learner-progress participant does not match CLI participant scope"
        )
    return queue, batch, view, plans


def _policies(args: argparse.Namespace):
    return (
        build_default_mentor_queue_policy(
            requested_size=args.queue_size,
            maximum_per_game=args.maximum_per_game,
        ),
        build_default_adaptive_tutor_policy(),
    )


def _preview(args: argparse.Namespace, queue, batch, view, plans):
    queue_policy, adaptive_policy = _policies(args)
    try:
        snapshot = build_local_tutor_workflow(
            participant_id=args.participant,
            diagnostic_batch=batch,
            batch_source_refs=(_batch_source_ref(queue),),
            learner_progress_view=view,
            transfer_plans=plans,
            queue_policy=queue_policy,
            adaptive_tutor_policy=adaptive_policy,
            created_at=args.created_at,
            hypothesis_id=args.hypothesis_id,
        )
        resolved_hypothesis_id = _resolve_hypothesis_id(
            view=view,
            item=snapshot.active_item,
            requested_hypothesis_id=args.hypothesis_id,
        )
    except LocalTutorWorkflowError as exc:
        raise LocalTutorCliError(str(exc)) from exc

    # Fail before persistence if multiple exact plans would make the future
    # M8/M46 active transfer context ambiguous.
    matching_transfers = tuple(
        plan
        for plan in plans
        if plan.hypothesis_id == resolved_hypothesis_id
        and plan.selected_candidate is not None
        and plan.selected_candidate.position.game_id == snapshot.active_item.game_id
        and (
            plan.selected_candidate.position.position_id
            == snapshot.active_item.position_id
        )
    )
    if len(matching_transfers) > 1:
        raise LocalTutorCliError(
            "multiple exact M42 transfer plans match the proposed rank-one review item"
        )
    return snapshot, queue_policy, adaptive_policy


def _load_session(
    *,
    db_value: str,
    participant_id: str,
    artifact_id: str,
):
    path = Path(db_value).expanduser()
    if not path.exists() or not path.is_file():
        raise LocalTutorCliError(f"artifact database does not exist: {path}")
    store = LocalArtifactStore(path)
    matches = tuple(
        ref
        for ref in store.list_refs(
            participant_id=participant_id,
            kind=SESSION_KIND,
        )
        if ref.artifact_id == artifact_id
    )
    if not matches:
        raise LocalTutorCliError(
            "tutor session artifact not found in the exact participant scope"
        )
    if len(matches) != 1:
        raise LocalTutorCliError("tutor session artifact identity is ambiguous")
    ref = matches[0]
    recovered = load_tutor_session(store, ref, participant_id=participant_id)
    return ref, recovered.session


def _cmd_local_tutor_start(args: argparse.Namespace) -> dict[str, Any]:
    queue, batch, view, plans = _load_inputs(args)
    preview, queue_policy, adaptive_policy = _preview(
        args,
        queue,
        batch,
        view,
        plans,
    )
    selected_candidate_id = preview.active_item.diagnostic_candidate_ref.ref_id
    bridge_args = argparse.Namespace(
        pgn=args.pgn,
        diagnostic_json=args.diagnostic_json,
        candidate_id=selected_candidate_id,
        db=args.db,
        participant=args.participant,
        protocol_json=args.protocol_json,
        prompts_json=args.prompts_json,
        selection_decision=args.selection_decision,
        capture_consent=args.capture_consent,
        recorded_at=args.recorded_at,
        created_at=args.created_at,
        create_db=args.create_db,
    )
    try:
        launch = _run_candidate_tutor(bridge_args)
    except (CandidateTutorCliError, CandidateTutorOrchestrationError) as exc:
        raise LocalTutorCliError(str(exc)) from exc

    session_ref = ArtifactRef(**launch["ref"])
    store = LocalArtifactStore(Path(args.db).expanduser())
    recovered = load_tutor_session(
        store,
        session_ref,
        participant_id=args.participant,
    )
    snapshot = build_local_tutor_workflow(
        participant_id=args.participant,
        diagnostic_batch=batch,
        batch_source_refs=(_batch_source_ref(queue),),
        learner_progress_view=view,
        transfer_plans=plans,
        queue_policy=queue_policy,
        adaptive_tutor_policy=adaptive_policy,
        created_at=args.created_at,
        tutor_session=recovered.session,
        hypothesis_id=args.hypothesis_id,
    )
    return {
        "schema_version": LOCAL_TUTOR_START_SCHEMA_VERSION,
        "workflow": snapshot.to_dict(),
        "launch": launch,
        "verified_replay": True,
        "execution_authority": "M8_existing_tutor_commands",
    }


def _cmd_local_tutor_next(args: argparse.Namespace) -> dict[str, Any]:
    queue, batch, view, plans = _load_inputs(args)
    queue_policy, adaptive_policy = _policies(args)
    session_ref, session = _load_session(
        db_value=args.db,
        participant_id=args.participant,
        artifact_id=args.session_artifact_id,
    )
    snapshot = build_local_tutor_workflow(
        participant_id=args.participant,
        diagnostic_batch=batch,
        batch_source_refs=(_batch_source_ref(queue),),
        learner_progress_view=view,
        transfer_plans=plans,
        queue_policy=queue_policy,
        adaptive_tutor_policy=adaptive_policy,
        created_at=args.created_at,
        tutor_session=session,
        hypothesis_id=args.hypothesis_id,
    )
    return {
        "schema_version": LOCAL_TUTOR_NEXT_SCHEMA_VERSION,
        "workflow": snapshot.to_dict(),
        "session_ref": session_ref.to_dict(),
        "verified_replay": True,
        "execution_authority": "M8_existing_tutor_commands",
    }


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--diagnostic-json",
        required=True,
        help="Exact M18 diagnostic-analysis queue JSON.",
    )
    parser.add_argument(
        "--learner-progress-json",
        required=True,
        help="Structural JSON for the exact M44 LearnerProgressView.",
    )
    parser.add_argument(
        "--transfer-plan-json",
        action="append",
        default=[],
        help="Optional structural JSON for an exact M42 transfer plan; repeatable.",
    )
    parser.add_argument("--participant", required=True)
    parser.add_argument(
        "--queue-size",
        type=_positive,
        default=5,
        help="Requested bounded M45 queue size; default 5.",
    )
    parser.add_argument(
        "--maximum-per-game",
        type=_positive,
        default=2,
        help="M45 maximum queue items per game; default 2.",
    )
    parser.add_argument(
        "--hypothesis-id",
        help=(
            "Required only when exact M44/M45 context does not identify one "
            "hypothesis."
        ),
    )
    parser.add_argument(
        "--created-at",
        required=True,
        help="Timezone-aware timestamp for deterministic M45/M46 composition.",
    )
