"""M23 diagnostic-to-persistent-tutor operator qualification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_reasoning_discrepancy_facts import (
    PGN,
    T0,
    T1,
    _a1_prompt,
    _a2_prompt,
    _protocol,
    _upstream,
)

from chess_mentor_engine.candidate_tutor_cli import (
    M18_QUEUE_KIND,
    M21_AUTH_KIND,
    M21_LAUNCH_KIND,
)
from chess_mentor_engine.candidate_tutor_cli import main as candidate_main
from chess_mentor_engine.cli import main as cme_main
from chess_mentor_engine.selection import SelectionPolicy, apply_selection_policy
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
)
from chess_mentor_engine.storage.codec import encode_record
from chess_mentor_engine.storage.tutor import PROMPT_KIND, SESSION_KIND


def _prompts():
    return _a1_prompt(), _a2_prompt()


def _json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return path


def _record(path: Path, value) -> Path:
    return _json(path, encode_record(value))


def _records(path: Path, values) -> Path:
    return _json(path, [encode_record(value) for value in values])


def _policy() -> SelectionPolicy:
    return SelectionPolicy(
        policy_id="m6b-selection",
        version="1",
        requested_size=1,
        candidate_min_cp_delta=40,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        include_rank1_controls=True,
        minimum_controls=0,
        maximum_per_game=1,
    )


def _queue() -> dict:
    upstream = _upstream()
    policy = _policy()
    selection = apply_selection_policy(
        comparison=upstream.comparison,
        signals=upstream.signals,
        policy=policy,
    )
    assert selection.candidate == upstream.candidate
    assert policy.fingerprint == upstream.batch.policy_fingerprint
    return {
        "schema_version": "m18.diagnostic-analysis-queue.v1",
        "source": {
            "source_sha256": upstream.game.provenance.source_sha256,
            "game_id": upstream.game.game_id,
            "game_index": 0,
            "start_ply": 0,
            "end_ply": 0,
            "position_count": 1,
        },
        "analysis_request": upstream.analysis.request.to_dict(),
        "selection_policy": policy.to_dict(),
        "policy_fingerprint": policy.fingerprint,
        "analysis_summary": {
            "root_failure_count": 0,
            "partial_root_count": 0,
            "incompatible_comparison_count": 0,
        },
        "source_pool": [
            {
                "ply_index": upstream.position.ply_index,
                "position_id": upstream.position.position_id,
                "side_to_move": upstream.position.side_to_move,
                "played_move_uci": upstream.game.moves_uci[upstream.position.ply_index],
                "root_analysis": {
                    "outcome_type": "position_analysis",
                    "record": upstream.analysis.to_dict(),
                },
                "played_child_analysis": None,
                "decision_comparison": upstream.comparison.to_dict(),
                "signals": [item.to_dict() for item in upstream.signals],
                "selection": selection.to_dict(),
            }
        ],
        "batch": upstream.batch.to_dict(),
    }


def _write_inputs(
    tmp_path: Path,
    *,
    queue: dict | None = None,
    pgn: str = PGN,
    prompts=None,
) -> tuple[Path, Path, Path, Path]:
    pgn_path = tmp_path / "game.pgn"
    pgn_path.write_text(pgn, encoding="utf-8")
    queue_value = _queue() if queue is None else queue
    queue_path = _json(tmp_path / "diagnostic.json", queue_value)
    protocol_path = _record(tmp_path / "protocol.json", _protocol())
    prompt_path = _records(
        tmp_path / "prompts.json", _prompts() if prompts is None else prompts
    )
    return pgn_path, queue_path, protocol_path, prompt_path


def _args(
    tmp_path: Path,
    db: Path,
    *,
    queue: dict | None = None,
    pgn: str = PGN,
    prompts=None,
    candidate_id: str | None = None,
    selection_decision: str = "selected",
    capture_consent: str = "granted",
    create_db: bool = False,
) -> tuple[str, ...]:
    upstream = _upstream()
    pgn_path, queue_path, protocol_path, prompt_path = _write_inputs(
        tmp_path,
        queue=queue,
        pgn=pgn,
        prompts=prompts,
    )
    argv = [
        str(pgn_path),
        "--diagnostic-json",
        str(queue_path),
        "--candidate-id",
        upstream.candidate.candidate_id if candidate_id is None else candidate_id,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--protocol-json",
        str(protocol_path),
        "--prompts-json",
        str(prompt_path),
        "--selection-decision",
        selection_decision,
        "--capture-consent",
        capture_consent,
        "--recorded-at",
        T0,
        "--created-at",
        T1,
    ]
    if create_db:
        argv.append("--create-db")
    return tuple(argv)


def _invoke(main, capsys, *argv: str):
    code = main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _ref(payload: dict) -> ArtifactRef:
    return ArtifactRef(**payload)


def test_operator_bridge_persists_exact_lineage_and_hands_off_to_m13(
    tmp_path, capsys
) -> None:
    db = tmp_path / "mentor.sqlite3"

    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db),
    )
    assert code == 2 and hidden is None and "--create-db" in error
    assert not db.exists()

    code, payload, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, create_db=True),
    )
    assert code == 0 and error == ""
    assert payload["state"] == "selected"
    assert payload["verified_replay"] is True
    assert payload["created_db"] is True

    store = LocalArtifactStore(db)
    queue_ref = _ref(payload["diagnostic_queue_ref"])
    auth_ref = _ref(payload["authorization_ref"])
    launch_ref = _ref(payload["launch_ref"])
    session_ref = _ref(payload["ref"])

    assert queue_ref.kind == M18_QUEUE_KIND
    assert auth_ref.kind == M21_AUTH_KIND
    assert launch_ref.kind == M21_LAUNCH_KIND
    assert session_ref.kind == SESSION_KIND
    assert store.get(auth_ref, participant_id="P01").dependencies == (queue_ref,)
    assert store.get(launch_ref, participant_id="P01").dependencies == (auth_ref,)

    session_dependencies = store.get(
        session_ref, participant_id="P01"
    ).dependencies
    assert launch_ref in session_dependencies
    assert sum(item.kind == PROMPT_KIND for item in session_dependencies) == 2

    recovered = load_tutor_session(store, session_ref, participant_id="P01")
    upstream = _upstream()
    assert recovered.session.state == "selected"
    candidate_ref = recovered.session.capture_session.context.diagnostic_candidate_ref
    assert candidate_ref.ref_id == upstream.candidate.candidate_id
    assert recovered.session.capture_session.context.diagnostic_batch_ref is not None
    assert recovered.session.capture_session.context.diagnostic_batch_ref.ref_id == (
        upstream.batch.batch_id
    )
    assert recovered.session.comparison is None
    assert recovered.session.hypothesis_context is None
    assert recovered.session.explanation is None

    code, status, error = _invoke(
        cme_main,
        capsys,
        "tutor",
        "status",
        "--db",
        str(db),
        "--participant",
        "P01",
        session_ref.artifact_id,
    )
    assert code == 0 and error == ""
    assert status["verified_replay"] is True
    assert status["state"] == "selected"

    kinds = tuple(ref.kind for ref in store.list_refs(participant_id="P01"))
    assert M18_QUEUE_KIND in kinds
    assert M21_AUTH_KIND in kinds
    assert M21_LAUNCH_KIND in kinds
    assert SESSION_KIND in kinds
    assert not any(kind.startswith("m6.") for kind in kinds)
    assert not any(kind.startswith("m7.") for kind in kinds)
    assert not any(kind.startswith("m9.") for kind in kinds)


def test_operator_bridge_is_idempotent_for_identical_inputs(tmp_path, capsys) -> None:
    db = tmp_path / "mentor.sqlite3"
    code, first, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, create_db=True),
    )
    assert code == 0 and error == ""
    count = len(LocalArtifactStore(db).list_refs(participant_id="P01"))

    code, second, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db),
    )
    assert code == 0 and error == ""
    assert second["created_db"] is False
    assert second["ref"] == first["ref"]
    assert second["authorization_ref"] == first["authorization_ref"]
    assert second["launch_ref"] == first["launch_ref"]
    assert len(LocalArtifactStore(db).list_refs(participant_id="P01")) == count


@pytest.mark.parametrize(
    ("selection_decision", "capture_consent", "message"),
    (
        ("declined", "declined", "explicit candidate selection"),
        ("selected", "declined", "explicit capture consent"),
        ("declined", "granted", "cannot be granted for a declined candidate"),
    ),
)
def test_declined_authority_never_creates_partial_persistence(
    tmp_path,
    capsys,
    selection_decision,
    capture_consent,
    message,
) -> None:
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(
            tmp_path,
            db,
            selection_decision=selection_decision,
            capture_consent=capture_consent,
            create_db=True,
        ),
    )
    assert code == 2 and hidden is None and message in error
    assert not db.exists()


def test_source_pool_semantic_drift_is_rejected_before_persistence(
    tmp_path, capsys
) -> None:
    queue = _queue()
    queue["source_pool"][0]["selection"]["decision"]["role"] = "control"
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, queue=queue, create_db=True),
    )
    assert code == 2 and hidden is None
    assert "source_pool selection payloads" in error
    assert not db.exists()


def test_candidate_source_drift_is_rejected_before_persistence(
    tmp_path, capsys
) -> None:
    queue = _queue()
    queue["batch"]["candidates"][0]["signals"][0]["detail"] = "tampered"
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, queue=queue, create_db=True),
    )
    assert code == 2 and hidden is None
    assert "diagnostic batch candidate content drifted from source_pool" in error
    assert not db.exists()


def test_policy_drift_is_rejected_before_persistence(tmp_path, capsys) -> None:
    queue = _queue()
    queue["selection_policy"]["candidate_min_cp_delta"] = 999
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, queue=queue, create_db=True),
    )
    assert code == 2 and hidden is None
    assert "selection policy fingerprint mismatch" in error
    assert not db.exists()


def test_wrong_pgn_source_is_rejected_before_persistence(tmp_path, capsys) -> None:
    db = tmp_path / "mentor.sqlite3"
    changed_pgn = PGN.replace("M6B deterministic facts", "Different source")
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, pgn=changed_pgn, create_db=True),
    )
    assert code == 2 and hidden is None
    assert "PGN source does not match" in error
    assert not db.exists()


def test_missing_candidate_is_rejected_before_persistence(tmp_path, capsys) -> None:
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(tmp_path, db, candidate_id="candidate_missing", create_db=True),
    )
    assert code == 2 and hidden is None
    assert "exactly one selected M18 batch candidate" in error
    assert not db.exists()


def test_prompt_dependency_mismatch_is_rejected_before_db_creation(
    tmp_path, capsys
) -> None:
    db = tmp_path / "mentor.sqlite3"
    code, hidden, error = _invoke(
        candidate_main,
        capsys,
        *_args(
            tmp_path,
            db,
            prompts=(_a1_prompt(),),
            create_db=True,
        ),
    )
    assert code == 2 and hidden is None
    assert "prompt definitions" in error
    assert not db.exists()
