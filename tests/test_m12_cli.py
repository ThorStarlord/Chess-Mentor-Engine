"""M12 CLI qualification: useful read-only surface with fail-closed boundaries."""

from __future__ import annotations

import json
import sqlite3
from importlib.metadata import entry_points

import pytest

from chess_mentor_engine.chess import build_position_context, ingest_pgn
from chess_mentor_engine.cli import build_parser, main
from chess_mentor_engine.storage import LocalArtifactStore

PGN = """[Event \"CLI fixture\"]
[White \"Ada\"]
[Black \"Grace\"]
[Result \"*\"]

1. e4 e5 2. Nf3 Nc6 *
"""


def _pgn(tmp_path):
    path = tmp_path / "games.pgn"
    path.write_text(PGN, encoding="utf-8")
    return path


def _invoke(capsys, *argv: str):
    code = main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def test_games_inspect_is_deterministic_and_defaults_to_bounded_summary(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    first = _invoke(capsys, "games", "inspect", str(path))
    second = _invoke(capsys, "games", "inspect", str(path))
    assert first == second
    code, payload, error = first
    assert code == 0 and error == ""
    assert payload["game_count"] == 1
    assert payload["games"][0]["white"] == "Ada"
    assert payload["games"][0]["black"] == "Grace"
    assert payload["games"][0]["mainline_move_count"] == 4
    assert "positions" not in payload["games"][0]


def test_games_inspect_full_is_native_m1_payload(tmp_path, capsys) -> None:
    path = _pgn(tmp_path)
    code, payload, error = _invoke(
        capsys, "games", "inspect", str(path), "--full"
    )
    assert code == 0 and error == ""
    assert payload == ingest_pgn(path.read_bytes()).to_dict()


def test_position_packet_matches_native_engine_free_context(tmp_path, capsys) -> None:
    path = _pgn(tmp_path)
    code, payload, error = _invoke(
        capsys,
        "position",
        "packet",
        str(path),
        "--game-index",
        "0",
        "--ply-index",
        "2",
    )
    result = ingest_pgn(path.read_bytes())
    expected = build_position_context(result.games[0], result.games[0].positions[2])
    assert code == 0 and error == ""
    assert payload == expected.to_dict()
    assert "engine" not in json.dumps(payload).lower()


def test_artifact_list_show_and_verify_use_verified_participant_scope(
    tmp_path, capsys
) -> None:
    db = tmp_path / "evidence.sqlite"
    store = LocalArtifactStore(db)
    ref = store.put(
        kind="outcome_assessment",
        artifact_id="assessment-1",
        participant_id="P01",
        payload={"status": "supported", "causal_effect": "not_established"},
    )

    code, listed, error = _invoke(
        capsys,
        "artifacts",
        "list",
        "--db",
        str(db),
        "--participant",
        "P01",
    )
    assert code == 0 and error == ""
    assert listed["artifact_count"] == 1
    assert listed["artifacts"] == [ref.to_dict()]

    code, shown, error = _invoke(
        capsys,
        "artifacts",
        "show",
        "--db",
        str(db),
        "--participant",
        "P01",
        "--kind",
        "outcome_assessment",
        "assessment-1",
    )
    assert code == 0 and error == ""
    assert shown["ref"] == ref.to_dict()
    assert shown["payload"]["causal_effect"] == "not_established"

    code, verified, error = _invoke(
        capsys,
        "artifacts",
        "verify",
        "--db",
        str(db),
        "--participant",
        "P01",
    )
    assert code == 0 and error == ""
    assert verified == {
        "participant_id": "P01",
        "verified": True,
        "artifact_count": 1,
        "kind_counts": {"outcome_assessment": 1},
    }


def test_missing_database_is_rejected_without_creating_one(tmp_path, capsys) -> None:
    db = tmp_path / "missing.sqlite"
    code, payload, error = _invoke(
        capsys,
        "artifacts",
        "list",
        "--db",
        str(db),
        "--participant",
        "P01",
    )
    assert code == 2 and payload is None
    assert "does not exist" in error
    assert not db.exists()


def test_artifact_show_does_not_cross_participant_scope(tmp_path, capsys) -> None:
    db = tmp_path / "evidence.sqlite"
    store = LocalArtifactStore(db)
    store.put(
        kind="private_evidence",
        artifact_id="evidence-1",
        participant_id="P01",
        payload={"secret": "P01 only"},
    )

    code, payload, error = _invoke(
        capsys,
        "artifacts",
        "show",
        "--db",
        str(db),
        "--participant",
        "P02",
        "--kind",
        "private_evidence",
        "evidence-1",
    )
    assert code == 2 and payload is None
    assert "not found" in error
    assert "P01 only" not in error


def test_corrupt_artifact_database_fails_closed(tmp_path, capsys) -> None:
    db = tmp_path / "evidence.sqlite"
    store = LocalArtifactStore(db)
    ref = store.put(
        kind="evidence",
        artifact_id="evidence-1",
        participant_id="P01",
        payload={"value": 1},
    )
    with sqlite3.connect(db) as connection:
        connection.execute(
            "UPDATE artifacts SET envelope=? WHERE digest=?",
            ("{}", ref.digest),
        )

    code, payload, error = _invoke(
        capsys,
        "artifacts",
        "verify",
        "--db",
        str(db),
        "--participant",
        "P01",
    )
    assert code == 2 and payload is None
    assert "error:" in error


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (("position", "packet", "{pgn}", "--ply-index", "99"), "ply index"),
        (("position", "packet", "{pgn}", "--game-index", "8", "--ply-index", "0"), "game index"),
    ],
)
def test_out_of_range_position_requests_are_rejected(
    tmp_path, capsys, argv, message
) -> None:
    path = _pgn(tmp_path)
    values = tuple(str(path) if item == "{pgn}" else item for item in argv)
    code, payload, error = _invoke(capsys, *values)
    assert code == 2 and payload is None
    assert message in error


def test_invalid_pgn_is_rejected_without_partial_json(tmp_path, capsys) -> None:
    path = tmp_path / "invalid.pgn"
    path.write_text('[Result "*"]\n\n1. definitely-not-san *', encoding="utf-8")
    code, payload, error = _invoke(capsys, "games", "inspect", str(path))
    assert code == 2 and payload is None
    assert "error:" in error


def test_parser_rejects_negative_indices() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(
            ["position", "packet", "games.pgn", "--ply-index", "-1"]
        )
    assert exc.value.code == 2


def test_installed_console_entry_point_is_declared() -> None:
    matches = entry_points(group="console_scripts", name="cme")
    assert any(item.value == "chess_mentor_engine.cli:main" for item in matches)
