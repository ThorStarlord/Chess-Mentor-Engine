"""V1 local tutor vertical-slice composition and rejection tests."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from test_m23_diagnostic_to_persistent_tutor_cli import _queue
from test_m45_batch_mentor_queue import _challenge_view
from test_reasoning_discrepancy_facts import (
    PGN,
    T0,
    T1,
    _a1_prompt,
    _a2_prompt,
    _protocol,
    _upstream,
)

from chess_mentor_engine.candidate_tutor_cli import _validate_queue
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    build_default_mentor_queue_policy,
)
from chess_mentor_engine.local_tutor import (
    LocalTutorWorkflowError,
    build_local_tutor_workflow,
    validate_local_tutor_workflow,
)
from chess_mentor_engine.local_tutor_entry import main as local_main
from chess_mentor_engine.storage import LocalArtifactStore
from chess_mentor_engine.storage.codec import encode_record
from chess_mentor_engine.storage.tutor import SESSION_KIND
from chess_mentor_engine.tutoring import (
    build_default_adaptive_tutor_policy,
    record_candidate_tutor_authorization,
    start_candidate_tutor_session,
)

CREATED_AT = "2026-09-11T19:00:00-03:00"


def _sources():
    upstream = _upstream()
    view = _challenge_view(
        upstream.candidate.game_id,
        upstream.candidate.position_id,
    )
    return upstream, view


def _source_refs():
    return (
        EvidenceSynthesisReference(
            "m18.diagnostic-analysis-queue.v1",
            "diagnostic-queue-fixture",
            "diagnostic-queue-fixture-fingerprint",
        ),
    )


def _build(*, participant_id: str = "P01", session=None, view=None):
    upstream, default_view = _sources()
    learner_view = default_view if view is None else view
    queue_policy = build_default_mentor_queue_policy(
        requested_size=1,
        maximum_per_game=1,
    )
    adaptive_policy = build_default_adaptive_tutor_policy()
    snapshot = build_local_tutor_workflow(
        participant_id=participant_id,
        diagnostic_batch=upstream.batch,
        batch_source_refs=_source_refs(),
        learner_progress_view=learner_view,
        queue_policy=queue_policy,
        adaptive_tutor_policy=adaptive_policy,
        created_at=CREATED_AT,
        tutor_session=session,
    )
    return snapshot, queue_policy, adaptive_policy


def _selected_session():
    upstream = _upstream()
    authorization = record_candidate_tutor_authorization(
        participant_id="P01",
        candidate=upstream.candidate,
        batch=upstream.batch,
        selection_decision="selected",
        capture_consent="granted",
        recorded_at=T0,
    )
    _, session, _ = start_candidate_tutor_session(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=T1,
    )
    return session


def test_v1_preview_selects_m45_rank_one_without_claiming_execution() -> None:
    snapshot, queue_policy, adaptive_policy = _build()
    upstream, view = _sources()

    assert snapshot.stage == "review_ready"
    assert snapshot.next_action == "START_SELECTED_REVIEW"
    assert snapshot.active_item.rank == 1
    assert snapshot.active_item.position_id == upstream.candidate.position_id
    assert snapshot.active_item.review_authority == "proposal_only"
    assert snapshot.tutor_session_ref is None
    assert snapshot.adaptive_tutor_proposal is None
    assert snapshot.orchestration_authority == "composition_only"
    assert snapshot.learner_effect == "not_established"
    assert snapshot.mastery == "not_established"

    validate_local_tutor_workflow(
        snapshot,
        diagnostic_batch=upstream.batch,
        batch_source_refs=_source_refs(),
        learner_progress_view=view,
        queue_policy=queue_policy,
        adaptive_tutor_policy=adaptive_policy,
    )


def test_v1_selected_session_preserves_m8_baseline_before_any_adaptive_help() -> None:
    snapshot, _, _ = _build(session=_selected_session())
    proposal = snapshot.adaptive_tutor_proposal

    assert snapshot.stage == "baseline_capture"
    assert snapshot.next_action == "CONTINUE_BASELINE_CAPTURE"
    assert proposal is not None
    assert proposal.action == "CONTINUE_BASELINE_CAPTURE"
    assert proposal.rendered_prompt is None
    assert proposal.exposure_effect == "none"
    assert proposal.response_evidence_class == "baseline_unassisted"
    assert proposal.execution_authority == "proposal_only"
    assert proposal.model_language == "not_generated"
    assert proposal.mastery == "not_established"


def test_v1_rejects_participant_scope_drift() -> None:
    with pytest.raises(
        LocalTutorWorkflowError,
        match="learner-progress participant mismatch",
    ):
        _build(participant_id="P02")


def test_v1_rejects_tampered_m44_view() -> None:
    _, view = _sources()
    with pytest.raises(ValueError, match="learner-progress view fingerprint mismatch"):
        _build(view=replace(view, fingerprint="tampered"))


def test_v1_rejects_active_m8_position_outside_exact_m45_queue() -> None:
    session = _selected_session()
    context = session.capture_session.context
    drifted_context = replace(context, position_id="position-outside-m45")
    drifted_capture = replace(session.capture_session, context=drifted_context)
    drifted_session = replace(session, capture_session=drifted_capture)

    with pytest.raises(
        LocalTutorWorkflowError,
        match="not present exactly once in the M45 queue",
    ):
        _build(session=drifted_session)


def _json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return path


def _write_cli_inputs(tmp_path: Path, *, tamper_view: bool = False):
    raw_queue = _queue()
    _, _, batch = _validate_queue(raw_queue)
    candidate = batch.candidates[0]
    view = _challenge_view(candidate.game_id, candidate.position_id)
    view_record = encode_record(view)
    if tamper_view:
        view_record["fingerprint"] = "tampered"

    pgn_path = tmp_path / "game.pgn"
    pgn_path.write_text(PGN, encoding="utf-8")
    queue_path = _json(tmp_path / "diagnostic.json", raw_queue)
    view_path = _json(tmp_path / "learner-progress.json", view_record)
    protocol_path = _json(tmp_path / "protocol.json", encode_record(_protocol()))
    prompts_path = _json(
        tmp_path / "prompts.json",
        [encode_record(_a1_prompt()), encode_record(_a2_prompt())],
    )
    return pgn_path, queue_path, view_path, protocol_path, prompts_path, candidate


def _invoke(capsys, *argv: str):
    code = local_main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _start_args(
    tmp_path: Path,
    db: Path,
    *,
    selection_decision: str = "selected",
    capture_consent: str = "granted",
    tamper_view: bool = False,
):
    pgn, queue, view, protocol, prompts, candidate = _write_cli_inputs(
        tmp_path,
        tamper_view=tamper_view,
    )
    return (
        (
            "start",
            str(pgn),
            "--diagnostic-json",
            str(queue),
            "--learner-progress-json",
            str(view),
            "--participant",
            "P01",
            "--queue-size",
            "1",
            "--maximum-per-game",
            "1",
            "--created-at",
            T1,
            "--db",
            str(db),
            "--protocol-json",
            str(protocol),
            "--prompts-json",
            str(prompts),
            "--selection-decision",
            selection_decision,
            "--capture-consent",
            capture_consent,
            "--recorded-at",
            T0,
            "--create-db",
        ),
        (queue, view),
        candidate,
    )


def test_v1_cli_starts_rank_one_review_and_replays_same_m8_checkpoint(
    tmp_path,
    capsys,
) -> None:
    db = tmp_path / "mentor.sqlite3"
    start_args, (queue_path, view_path), candidate = _start_args(tmp_path, db)

    code, payload, error = _invoke(capsys, *start_args)
    assert code == 0 and error == ""
    workflow = payload["workflow"]
    launch = payload["launch"]
    assert workflow["stage"] == "baseline_capture"
    assert workflow["next_action"] == "CONTINUE_BASELINE_CAPTURE"
    assert workflow["active_item"]["diagnostic_candidate_ref"]["ref_id"] == (
        candidate.candidate_id
    )
    assert launch["candidate_id"] == candidate.candidate_id
    assert launch["state"] == "selected"
    assert payload["verified_replay"] is True
    assert payload["execution_authority"] == "M8_existing_tutor_commands"

    store = LocalArtifactStore(db)
    kinds = tuple(ref.kind for ref in store.list_refs(participant_id="P01"))
    assert SESSION_KIND in kinds
    assert not any(kind.startswith("m6.") for kind in kinds)
    assert not any(kind.startswith("m7.") for kind in kinds)
    assert not any(kind.startswith("m9.") for kind in kinds)

    code, next_payload, error = _invoke(
        capsys,
        "next",
        "--diagnostic-json",
        str(queue_path),
        "--learner-progress-json",
        str(view_path),
        "--participant",
        "P01",
        "--queue-size",
        "1",
        "--maximum-per-game",
        "1",
        "--created-at",
        T1,
        "--db",
        str(db),
        launch["ref"]["artifact_id"],
    )
    assert code == 0 and error == ""
    assert next_payload["verified_replay"] is True
    assert next_payload["workflow"] == workflow


def test_v1_cli_declined_selection_creates_no_database(tmp_path, capsys) -> None:
    db = tmp_path / "mentor.sqlite3"
    args, _, _ = _start_args(
        tmp_path,
        db,
        selection_decision="declined",
        capture_consent="declined",
    )

    code, payload, error = _invoke(capsys, *args)
    assert code == 2
    assert payload is None
    assert "explicit candidate selection" in error
    assert not db.exists()


def test_v1_cli_rejects_tampered_view_before_database_creation(
    tmp_path,
    capsys,
) -> None:
    db = tmp_path / "mentor.sqlite3"
    args, _, _ = _start_args(tmp_path, db, tamper_view=True)

    code, payload, error = _invoke(capsys, *args)
    assert code == 2
    assert payload is None
    assert "learner-progress view fingerprint mismatch" in error
    assert not db.exists()
