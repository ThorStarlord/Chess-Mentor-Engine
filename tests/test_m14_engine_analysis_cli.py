"""M14 engine-backed CLI qualification and rejection coverage."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

import chess_mentor_engine.cli as cli_module
from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisRequest,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.cli import build_parser, main
from chess_mentor_engine.storage import LocalArtifactStore

SIMPLE_PGN = """[Event "M14 fixture"]
[White "Ada"]
[Black "Grace"]
[Result "*"]

1. e4 e5 *
"""

MATE_PGN = """[Event "M14 mate fixture"]
[White "Ada"]
[Black "Grace"]
[Result "0-1"]

1. f3 e5 2. g4 Qh4# 0-1
"""


def _pgn(tmp_path: Path, text: str = SIMPLE_PGN) -> Path:
    path = tmp_path / "game.pgn"
    path.write_text(text, encoding="utf-8")
    return path


def _invoke(capsys, *argv: str):
    code = main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _positions(text: str = SIMPLE_PGN):
    return ingest_pgn(text.encode("utf-8")).games[0].positions


def _write_fake_engine(
    tmp_path: Path,
    plans: dict[str, tuple[tuple[str, ...], str | None]],
    *,
    identities: tuple[str, ...] = ("FakeFish 1.0",),
) -> str:
    path = tmp_path / "fake-uci-engine"
    counter = tmp_path / "engine-counter.txt"
    script = f'''#!/usr/bin/env python3
from pathlib import Path
import sys

PLANS = {plans!r}
IDENTITIES = {identities!r}
COUNTER = Path({str(counter)!r})
current_fen = None

for raw in sys.stdin:
    command = raw.strip()
    if command == "uci":
        try:
            index = int(COUNTER.read_text())
        except (FileNotFoundError, ValueError):
            index = 0
        COUNTER.write_text(str(index + 1))
        identity = IDENTITIES[min(index, len(IDENTITIES) - 1)]
        print("id name " + identity, flush=True)
        print("id author Chess Mentor Tests", flush=True)
        print("option name MultiPV type spin default 1 min 1 max 8", flush=True)
        print("option name Threads type spin default 1 min 1 max 8", flush=True)
        print("uciok", flush=True)
    elif command == "isready":
        print("readyok", flush=True)
    elif command.startswith("position fen "):
        current_fen = command[len("position fen "):]
    elif command.startswith("go "):
        info_lines, bestmove = PLANS.get(current_fen, ((), None))
        for item in info_lines:
            print(item, flush=True)
        if bestmove is not None:
            print("bestmove " + bestmove, flush=True)
    elif command == "quit":
        break
'''
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def _analyze_args(path: Path, engine: str, *, ply: int = 0, multipv: int = 2):
    return (
        "analyze",
        str(path),
        "--ply-index",
        str(ply),
        "--engine",
        engine,
        "--depth",
        "8",
        "--multipv",
        str(multipv),
    )


def test_analyze_uses_native_root_multipv_comparison(tmp_path, capsys) -> None:
    path = _pgn(tmp_path)
    root = _positions()[0].fen
    engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                (
                    "info depth 8 multipv 1 score cp 40 pv d2d4 d7d5",
                    "info depth 8 multipv 2 score cp 10 pv e2e4 e7e5",
                ),
                "d2d4",
            )
        },
    )

    code, payload, error = _invoke(capsys, *_analyze_args(path, engine))

    assert code == 0 and error == ""
    package = payload["package"]
    assert package["schema_version"] == "m14.engine-analysis-cli.v1"
    assert package["root_analysis"]["outcome_type"] == "position_analysis"
    assert package["played_child_analysis"] is None
    comparison = package["decision_comparison"]
    assert comparison["played_evaluation_source"] == "root_multipv"
    assert comparison["best_move_uci"] == "d2d4"
    assert comparison["played_move_uci"] == "e2e4"
    assert comparison["exact_centipawn_delta_for_mover"] == 30
    assert payload["archive_ref"] is None


def test_analyze_reanalyzes_child_when_played_move_is_outside_multipv(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    positions = _positions()
    engine = _write_fake_engine(
        tmp_path,
        {
            positions[0].fen: (
                ("info depth 8 score cp 40 pv d2d4 d7d5",),
                "d2d4",
            ),
            positions[1].fen: (
                ("info depth 8 score cp 20 pv e7e5 g1f3",),
                "e7e5",
            ),
        },
    )

    code, payload, error = _invoke(
        capsys, *_analyze_args(path, engine, multipv=1)
    )

    assert code == 0 and error == ""
    package = payload["package"]
    assert package["played_child_analysis"]["outcome_type"] == "position_analysis"
    comparison = package["decision_comparison"]
    assert comparison["played_evaluation_source"] == "child_reanalysis"
    assert comparison["compatibility"] == "compatible"
    assert comparison["exact_centipawn_delta_for_mover"] == 60


def test_black_to_move_keeps_white_scores_but_mover_relative_loss(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    root = _positions()[1].fen
    engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                (
                    "info depth 8 multipv 1 score cp 50 pv c7c5 g1f3",
                    "info depth 8 multipv 2 score cp 20 pv e7e5 g1f3",
                ),
                "c7c5",
            )
        },
    )

    code, payload, error = _invoke(
        capsys, *_analyze_args(path, engine, ply=1)
    )

    assert code == 0 and error == ""
    comparison = payload["package"]["decision_comparison"]
    assert comparison["side_to_move"] == "black"
    assert comparison["best_evaluation"]["centipawns"] == -50
    assert comparison["played_evaluation"]["centipawns"] == -20
    assert comparison["exact_centipawn_delta_for_mover"] == 30


def test_mate_remains_symbolic_in_cli_package(tmp_path, capsys) -> None:
    path = _pgn(tmp_path, MATE_PGN)
    root = _positions(MATE_PGN)[3].fen
    engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                ("info depth 8 score mate 1 pv d8h4",),
                "d8h4",
            )
        },
    )

    code, payload, error = _invoke(
        capsys, *_analyze_args(path, engine, ply=3, multipv=1)
    )

    assert code == 0 and error == ""
    comparison = payload["package"]["decision_comparison"]
    assert comparison["best_evaluation"] == {
        "kind": "mate",
        "perspective": "white",
        "winner": "black",
        "plies_to_mate": 1,
        "bound": "exact",
    }
    assert comparison["mate_relation"] == "forced_mate_preserved"
    assert comparison["exact_centipawn_delta_for_mover"] is None


def test_bound_limited_and_partial_evidence_are_not_forced_to_numeric_loss(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    root = _positions()[0].fen
    bound_engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                (
                    "info depth 8 multipv 1 score cp 40 lowerbound pv d2d4 d7d5",
                    "info depth 8 multipv 2 score cp 10 pv e2e4 e7e5",
                ),
                "d2d4",
            )
        },
    )
    code, payload, error = _invoke(capsys, *_analyze_args(path, bound_engine))
    assert code == 0 and error == ""
    comparison = payload["package"]["decision_comparison"]
    assert comparison["comparison_kind"] == "bound_limited"
    assert comparison["exact_centipawn_delta_for_mover"] is None

    partial_dir = tmp_path / "partial"
    partial_dir.mkdir()
    partial_engine = _write_fake_engine(
        partial_dir,
        {
            root: (
                ("info depth 8 multipv 1 score cp 40 pv d2d4 d7d5",),
                "d2d4",
            )
        },
    )
    code, payload, error = _invoke(capsys, *_analyze_args(path, partial_engine))
    assert code == 0 and error == ""
    assert payload["package"]["root_analysis"]["record"]["status"] == "partial"
    comparison = payload["package"]["decision_comparison"]
    assert comparison["comparison_kind"] == "partial_evidence"
    assert comparison["exact_centipawn_delta_for_mover"] is None


def test_incompatible_child_engine_identity_stays_incomparable(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    positions = _positions()
    engine = _write_fake_engine(
        tmp_path,
        {
            positions[0].fen: (
                ("info depth 8 score cp 40 pv d2d4 d7d5",),
                "d2d4",
            ),
            positions[1].fen: (
                ("info depth 8 score cp 20 pv e7e5 g1f3",),
                "e7e5",
            ),
        },
        identities=("FakeFish A", "FakeFish B"),
    )

    code, payload, error = _invoke(
        capsys, *_analyze_args(path, engine, multipv=1)
    )

    assert code == 0 and error == ""
    comparison = payload["package"]["decision_comparison"]
    assert comparison["comparison_kind"] == "incompatible_analysis_regime"
    assert comparison["compatibility"] == "incompatible"
    assert comparison["exact_centipawn_delta_for_mover"] is None


def test_invalid_engine_multipv_and_missing_engine_fail_without_json(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    root = _positions()[0].fen
    bad_engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                ("info depth 8 multipv 0 score cp 10 pv e2e4 e7e5",),
                "e2e4",
            )
        },
    )

    code, payload, error = _invoke(
        capsys, *_analyze_args(path, bad_engine, multipv=1)
    )
    assert code == 2 and payload is None
    assert "INVALID_ENGINE_OUTPUT" in error

    missing = tmp_path / "missing-engine"
    code, payload, error = _invoke(
        capsys, *_analyze_args(path, str(missing), multipv=1)
    )
    assert code == 2 and payload is None
    assert "ENGINE_NOT_FOUND" in error


def test_analysis_target_mismatch_is_rejected_before_output(
    tmp_path, capsys, monkeypatch
) -> None:
    path = _pgn(tmp_path)
    position = _positions()[0]
    engine = _write_fake_engine(
        tmp_path,
        {
            position.fen: (
                (
                    "info depth 8 multipv 1 score cp 40 pv d2d4 d7d5",
                    "info depth 8 multipv 2 score cp 10 pv e2e4 e7e5",
                ),
                "d2d4",
            )
        },
    )
    request = AnalysisRequest(
        multipv=2,
        search_limit=AnalysisLimit("depth", 8),
        supervisor_timeout_ms=10_000,
    )
    native = UciAnalysisProvider(engine).analyze(position, request)
    assert isinstance(native, PositionAnalysis)
    mismatched = replace(native, position_id="wrong-position")

    class MismatchedProvider:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def analyze(self, position, request):
            return mismatched

    monkeypatch.setattr(cli_module, "UciAnalysisProvider", MismatchedProvider)
    code, payload, error = _invoke(capsys, *_analyze_args(path, engine))
    assert code == 2 and payload is None
    assert "root analysis" in error


def test_optional_archive_is_existing_db_scoped_and_idempotent(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    root = _positions()[0].fen
    engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                (
                    "info depth 8 multipv 1 score cp 40 pv d2d4 d7d5",
                    "info depth 8 multipv 2 score cp 10 pv e2e4 e7e5",
                ),
                "d2d4",
            )
        },
    )
    db = tmp_path / "evidence.sqlite"
    store = LocalArtifactStore(db)
    argv = _analyze_args(path, engine) + (
        "--db",
        str(db),
        "--participant",
        "P01",
    )

    first = _invoke(capsys, *argv)
    second = _invoke(capsys, *argv)
    assert first == second
    code, payload, error = first
    assert code == 0 and error == ""
    assert payload["archive_ref"]["kind"] == "m14.analysis-package.v1"
    refs = store.list_refs(participant_id="P01")
    assert len(refs) == 1
    assert refs[0].to_dict() == payload["archive_ref"]
    stored = store.get(refs[0], participant_id="P01")
    assert stored.payload == payload["package"]
    assert all("tutor" not in ref.kind and "learner" not in ref.kind for ref in refs)


def test_archive_scope_and_terminal_position_fail_before_side_effects(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    root = _positions()[0].fen
    engine = _write_fake_engine(
        tmp_path,
        {
            root: (
                (
                    "info depth 8 multipv 1 score cp 40 pv d2d4 d7d5",
                    "info depth 8 multipv 2 score cp 10 pv e2e4 e7e5",
                ),
                "d2d4",
            )
        },
    )
    missing_db = tmp_path / "missing.sqlite"
    code, payload, error = _invoke(
        capsys,
        *_analyze_args(path, engine),
        "--db",
        str(missing_db),
        "--participant",
        "P01",
    )
    assert code == 2 and payload is None
    assert "does not exist" in error
    assert not missing_db.exists()

    code, payload, error = _invoke(
        capsys,
        *_analyze_args(path, engine, ply=2),
    )
    assert code == 2 and payload is None
    assert "no canonical played move" in error


def test_parser_rejects_invalid_analysis_configuration() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(
            [
                "analyze",
                "game.pgn",
                "--ply-index",
                "0",
                "--engine",
                "stockfish",
                "--multipv",
                "0",
            ]
        )
    assert exc.value.code == 2

    with pytest.raises(SystemExit) as exc:
        parser.parse_args(
            [
                "analyze",
                "game.pgn",
                "--ply-index",
                "0",
                "--engine",
                "stockfish",
                "--engine-option",
                "MultiPV=4",
            ]
        )
    assert exc.value.code == 2
