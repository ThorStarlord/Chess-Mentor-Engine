"""M13 controlled persistent CLI over the qualified M8 tutor state machine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, TypeVar

from chess_mentor_engine.chess import PositionContextPacket
from chess_mentor_engine.evidence import (
    CaptureProtocol,
    EvidenceReference,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    PromptDefinition,
)
from chess_mentor_engine.learning import (
    HypothesisLedgerSnapshot,
    HypothesisRevision,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
    ReasoningDiscrepancyContext,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.storage.codec import decode_record
from chess_mentor_engine.storage.tutor import PROMPT_KIND, SESSION_KIND
from chess_mentor_engine.tutoring import (
    TutorExplanationProvenance,
    TutorSession,
    attach_tutor_hypothesis_context,
    capture_tutor_response,
    complete_tutor_session,
    freeze_tutor_response,
    present_tutor_capture_stage,
    present_tutor_position,
    record_tutor_explanation,
    record_tutor_reasoning_comparison,
    reveal_tutor_objective_evidence,
    start_tutor_session,
)

T = TypeVar("T")


class TutorCliError(ValueError):
    """A persistent tutor CLI operation cannot be completed safely."""


def _json_value(path_value: str) -> Any:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise TutorCliError(f"JSON file does not exist: {path}")
    if not path.is_file():
        raise TutorCliError(f"JSON path is not a file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _text_file(path_value: str) -> str:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise TutorCliError(f"text file does not exist: {path}")
    if not path.is_file():
        raise TutorCliError(f"text path is not a file: {path}")
    value = path.read_text(encoding="utf-8")
    if not value.strip():
        raise TutorCliError("text file must not be empty")
    return value


def _record_value(value: Any, schema: type[T], *, label: str) -> T:
    if type(value) is not dict:
        raise TutorCliError(f"{label} must be a JSON object")
    return decode_record(value, schema)


def _record_file(path_value: str, schema: type[T], *, label: str) -> T:
    return _record_value(_json_value(path_value), schema, label=label)


def _record_list(path_value: str, schema: type[T], *, label: str) -> tuple[T, ...]:
    value = _json_value(path_value)
    if type(value) is not list:
        raise TutorCliError(f"{label} must be a JSON array")
    return tuple(
        _record_value(item, schema, label=f"{label}[{index}]")
        for index, item in enumerate(value)
    )


def _strict_object(value: Any, keys: set[str], *, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        expected = ", ".join(sorted(keys))
        raise TutorCliError(f"{label} must contain exactly: {expected}")
    return value


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise TutorCliError(f"artifact database does not exist: {path}")
    if not path.is_file():
        raise TutorCliError(f"artifact database path is not a file: {path}")
    return LocalArtifactStore(path)


def _start_store(
    path_value: str, *, create_db: bool
) -> tuple[LocalArtifactStore, bool]:
    path = Path(path_value).expanduser()
    if path.exists():
        if not path.is_file():
            raise TutorCliError(f"artifact database path is not a file: {path}")
        return LocalArtifactStore(path), False
    if not create_db:
        raise TutorCliError(
            "artifact database does not exist; pass --create-db to create it explicitly"
        )
    return LocalArtifactStore(path), True


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
    if not matches:
        raise TutorCliError("tutor session artifact not found in participant scope")
    if len(matches) != 1:
        raise TutorCliError("tutor session artifact identity is unexpectedly ambiguous")
    return matches[0]


def _load_checkpoint(args: argparse.Namespace):
    store = _existing_store(args.db)
    ref = _find_session_ref(
        store,
        participant_id=args.participant,
        artifact_id=args.session_artifact_id,
    )
    recovered = load_tutor_session(store, ref, participant_id=args.participant)
    stored = store.get(ref, participant_id=args.participant)
    retained_dependencies = tuple(
        dependency
        for dependency in stored.dependencies
        if dependency.kind != PROMPT_KIND
    )
    return store, ref, recovered, retained_dependencies


def _session_payload(
    session: TutorSession,
    ref: ArtifactRef,
    *,
    previous_ref: ArtifactRef | None = None,
    created_db: bool | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "participant_id": session.capture_session.context.participant_id,
        "tutor_session_id": session.tutor_session_id,
        "state": session.state,
        "snapshot_fingerprint": session.snapshot_fingerprint,
        "event_count": len(session.events),
        "completed_at": session.completed_at,
        "ref": ref.to_dict(),
    }
    if previous_ref is not None:
        result["previous_ref"] = previous_ref.to_dict()
    if created_db is not None:
        result["created_db"] = created_db
    return result


def _save_transition(args: argparse.Namespace, transition) -> dict[str, Any]:
    store, previous_ref, recovered, retained = _load_checkpoint(args)
    updated = transition(recovered.session, recovered.prompts)
    if type(updated) is tuple:
        updated = updated[0]
    if not isinstance(updated, TutorSession):
        raise TutorCliError("tutor transition did not return a TutorSession")
    new_ref = save_tutor_session(
        store,
        updated,
        prompts=recovered.prompts,
        dependencies=retained,
    )
    return _session_payload(updated, new_ref, previous_ref=previous_ref)


def _cmd_tutor_start(args: argparse.Namespace) -> dict[str, Any]:
    context = _record_file(
        args.context_json, PlayerDecisionContext, label="player decision context"
    )
    protocol = _record_file(
        args.protocol_json, CaptureProtocol, label="capture protocol"
    )
    prompts = _record_list(
        args.prompts_json, PromptDefinition, label="prompt definitions"
    )
    dependencies: tuple[ArtifactRef, ...] = ()
    if args.dependencies_json is not None:
        dependencies = _record_list(
            args.dependencies_json, ArtifactRef, label="artifact dependencies"
        )
    if context.participant_id != args.participant:
        raise TutorCliError("context participant does not match CLI participant scope")
    if any(item.participant_id != args.participant for item in dependencies):
        raise TutorCliError(
            "dependency participant does not match CLI participant scope"
        )
    store, created = _start_store(args.db, create_db=args.create_db)
    session = start_tutor_session(
        context=context,
        capture_protocol=protocol,
        created_at=args.created_at,
    )
    ref = save_tutor_session(
        store,
        session,
        prompts=prompts,
        dependencies=dependencies,
    )
    return _session_payload(session, ref, created_db=created)


def _cmd_tutor_status(args: argparse.Namespace) -> dict[str, Any]:
    _, ref, recovered, _ = _load_checkpoint(args)
    payload = _session_payload(recovered.session, ref)
    payload["prompt_count"] = len(recovered.prompts)
    payload["verified_replay"] = True
    return payload


def _cmd_tutor_present_position(args: argparse.Namespace) -> dict[str, Any]:
    packet = _record_file(
        args.packet_json, PositionContextPacket, label="position context packet"
    )
    return _save_transition(
        args,
        lambda session, prompts: present_tutor_position(
            session,
            position_context=packet,
            shown_at=args.shown_at,
        ),
    )


def _cmd_tutor_present_stage(args: argparse.Namespace) -> dict[str, Any]:
    def transition(session: TutorSession, prompts: tuple[PromptDefinition, ...]):
        stages = tuple(
            stage
            for stage in session.capture_session.protocol.stages
            if stage.stage_id == args.stage_id
        )
        if len(stages) != 1:
            raise TutorCliError("stage is not defined exactly once by the protocol")
        prompt_id = stages[0].prompt_definition_id
        matches = tuple(
            prompt for prompt in prompts if prompt.prompt_definition_id == prompt_id
        )
        if len(matches) != 1:
            raise TutorCliError("planned prompt is not available exactly once")
        return present_tutor_capture_stage(
            session,
            stage_id=args.stage_id,
            prompt=matches[0],
            shown_at=args.shown_at,
        )

    return _save_transition(args, transition)


def _cmd_tutor_respond(args: argparse.Namespace) -> dict[str, Any]:
    structured = None
    if args.structured_json is not None:
        structured = _record_file(
            args.structured_json,
            ParticipantStructuredResponse,
            label="structured participant response",
        )
    return _save_transition(
        args,
        lambda session, prompts: capture_tutor_response(
            session,
            stage_id=args.stage_id,
            raw_response=args.response,
            structured_response=structured,
            submitted_at=args.submitted_at,
        ),
    )


def _cmd_tutor_freeze(args: argparse.Namespace) -> dict[str, Any]:
    return _save_transition(
        args,
        lambda session, prompts: freeze_tutor_response(
            session,
            stage_id=args.stage_id,
            frozen_at=args.frozen_at,
        ),
    )


def _evidence_ref(value: Any, *, label: str) -> EvidenceReference:
    return _record_value(value, EvidenceReference, label=label)


def _cmd_tutor_reveal(args: argparse.Namespace) -> dict[str, Any]:
    bundle = _strict_object(
        _json_value(args.bundle_json),
        {
            "rendered_content",
            "position_analysis_refs",
            "decision_comparison_ref",
            "selection_signal_refs",
        },
        label="objective reveal bundle",
    )
    if type(bundle["rendered_content"]) is not str:
        raise TutorCliError("rendered_content must be a string")
    for field in ("position_analysis_refs", "selection_signal_refs"):
        if type(bundle[field]) is not list:
            raise TutorCliError(f"{field} must be a JSON array")
    position_refs = tuple(
        _evidence_ref(item, label=f"position_analysis_refs[{index}]")
        for index, item in enumerate(bundle["position_analysis_refs"])
    )
    selection_refs = tuple(
        _evidence_ref(item, label=f"selection_signal_refs[{index}]")
        for index, item in enumerate(bundle["selection_signal_refs"])
    )
    decision_value = bundle["decision_comparison_ref"]
    decision_ref = (
        None
        if decision_value is None
        else _evidence_ref(decision_value, label="decision_comparison_ref")
    )
    return _save_transition(
        args,
        lambda session, prompts: reveal_tutor_objective_evidence(
            session,
            revealed_at=args.revealed_at,
            rendered_content=bundle["rendered_content"],
            position_analysis_refs=position_refs,
            decision_comparison_ref=decision_ref,
            selection_signal_refs=selection_refs,
        ),
    )


def _cmd_tutor_compare(args: argparse.Namespace) -> dict[str, Any]:
    bundle = _strict_object(
        _json_value(args.bundle_json),
        {"reasoning_context", "assessment", "assertions"},
        label="reasoning comparison bundle",
    )
    if type(bundle["assertions"]) is not list:
        raise TutorCliError("assertions must be a JSON array")
    context = _record_value(
        bundle["reasoning_context"],
        ReasoningDiscrepancyContext,
        label="reasoning_context",
    )
    assessment = _record_value(
        bundle["assessment"],
        ReasoningDiscrepancyAssessment,
        label="assessment",
    )
    assertions = tuple(
        _record_value(
            item,
            ReasoningDiscrepancyAssertion,
            label=f"assertions[{index}]",
        )
        for index, item in enumerate(bundle["assertions"])
    )
    return _save_transition(
        args,
        lambda session, prompts: record_tutor_reasoning_comparison(
            session,
            reasoning_context=context,
            assessment=assessment,
            assertions=assertions,
            recorded_at=args.recorded_at,
        ),
    )


def _cmd_tutor_attach_hypothesis(args: argparse.Namespace) -> dict[str, Any]:
    bundle = _strict_object(
        _json_value(args.bundle_json),
        {"ledger_snapshot", "active_revisions"},
        label="hypothesis context bundle",
    )
    if type(bundle["active_revisions"]) is not list:
        raise TutorCliError("active_revisions must be a JSON array")
    snapshot = _record_value(
        bundle["ledger_snapshot"],
        HypothesisLedgerSnapshot,
        label="ledger_snapshot",
    )
    revisions = tuple(
        _record_value(
            item,
            HypothesisRevision,
            label=f"active_revisions[{index}]",
        )
        for index, item in enumerate(bundle["active_revisions"])
    )
    return _save_transition(
        args,
        lambda session, prompts: attach_tutor_hypothesis_context(
            session,
            ledger_snapshot=snapshot,
            active_revisions=revisions,
            attached_at=args.attached_at,
        ),
    )


def _cmd_tutor_explain(args: argparse.Namespace) -> dict[str, Any]:
    provenance = _record_file(
        args.provenance_json,
        TutorExplanationProvenance,
        label="explanation provenance",
    )
    content = _text_file(args.content_file)
    return _save_transition(
        args,
        lambda session, prompts: record_tutor_explanation(
            session,
            rendered_content=content,
            provenance=provenance,
            created_at=args.created_at,
        ),
    )


def _cmd_tutor_complete(args: argparse.Namespace) -> dict[str, Any]:
    return _save_transition(
        args,
        lambda session, prompts: complete_tutor_session(
            session,
            completed_at=args.completed_at,
        ),
    )


def _add_scope(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", required=True, help="SQLite artifact database.")
    parser.add_argument(
        "--participant", required=True, help="Exact participant scope identifier."
    )


def _add_checkpoint(parser: argparse.ArgumentParser) -> None:
    _add_scope(parser)
    parser.add_argument(
        "session_artifact_id",
        help="Exact m8.tutor-session.v1 artifact_id for the prior snapshot.",
    )


def add_tutor_commands(surfaces) -> None:
    tutor = surfaces.add_parser(
        "tutor",
        help=(
            "Persist and advance verified M8 tutor sessions without generating content."
        ),
    )
    commands = tutor.add_subparsers(dest="tutor_command", required=True)

    start = commands.add_parser(
        "start", help="Start and persist an exact typed M8 session checkpoint."
    )
    _add_scope(start)
    start.add_argument("--context-json", required=True)
    start.add_argument("--protocol-json", required=True)
    start.add_argument("--prompts-json", required=True)
    start.add_argument("--dependencies-json")
    start.add_argument("--created-at", required=True)
    start.add_argument(
        "--create-db",
        action="store_true",
        help="Explicitly permit creation of a missing artifact database.",
    )
    start.set_defaults(handler=_cmd_tutor_start)

    status = commands.add_parser(
        "status", help="Replay-verify and report one stored tutor checkpoint."
    )
    _add_checkpoint(status)
    status.set_defaults(handler=_cmd_tutor_status)

    present_position = commands.add_parser(
        "present-position", help="Present an exact typed position packet."
    )
    _add_checkpoint(present_position)
    present_position.add_argument("--packet-json", required=True)
    present_position.add_argument("--shown-at", required=True)
    present_position.set_defaults(handler=_cmd_tutor_present_position)

    present_stage = commands.add_parser(
        "present-stage", help="Present the protocol-bound stored prompt for one stage."
    )
    _add_checkpoint(present_stage)
    present_stage.add_argument("--stage-id", required=True)
    present_stage.add_argument("--shown-at", required=True)
    present_stage.set_defaults(handler=_cmd_tutor_present_stage)

    respond = commands.add_parser(
        "respond", help="Append participant-authored response evidence."
    )
    _add_checkpoint(respond)
    respond.add_argument("--stage-id", required=True)
    respond.add_argument("--response", required=True)
    respond.add_argument("--structured-json")
    respond.add_argument("--submitted-at", required=True)
    respond.set_defaults(handler=_cmd_tutor_respond)

    freeze = commands.add_parser(
        "freeze", help="Freeze the exact participant response for one stage."
    )
    _add_checkpoint(freeze)
    freeze.add_argument("--stage-id", required=True)
    freeze.add_argument("--frozen-at", required=True)
    freeze.set_defaults(handler=_cmd_tutor_freeze)

    reveal = commands.add_parser(
        "reveal", help="Reveal explicitly supplied objective evidence after freeze."
    )
    _add_checkpoint(reveal)
    reveal.add_argument("--bundle-json", required=True)
    reveal.add_argument("--revealed-at", required=True)
    reveal.set_defaults(handler=_cmd_tutor_reveal)

    compare = commands.add_parser(
        "compare", help="Attach an exact precomputed M6 comparison bundle."
    )
    _add_checkpoint(compare)
    compare.add_argument("--bundle-json", required=True)
    compare.add_argument("--recorded-at", required=True)
    compare.set_defaults(handler=_cmd_tutor_compare)

    hypothesis = commands.add_parser(
        "attach-hypothesis",
        help="Attach complete active-current M7 context after comparison.",
    )
    _add_checkpoint(hypothesis)
    hypothesis.add_argument("--bundle-json", required=True)
    hypothesis.add_argument("--attached-at", required=True)
    hypothesis.set_defaults(handler=_cmd_tutor_attach_hypothesis)

    explain = commands.add_parser(
        "explain", help="Persist explicitly authored explanation text with provenance."
    )
    _add_checkpoint(explain)
    explain.add_argument("--content-file", required=True)
    explain.add_argument("--provenance-json", required=True)
    explain.add_argument("--created-at", required=True)
    explain.set_defaults(handler=_cmd_tutor_explain)

    complete = commands.add_parser(
        "complete", help="Complete an explained M8 session without rewriting history."
    )
    _add_checkpoint(complete)
    complete.add_argument("--completed-at", required=True)
    complete.set_defaults(handler=_cmd_tutor_complete)
