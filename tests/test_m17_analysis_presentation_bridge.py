"""M17 M14-to-M15 CLI bridge qualification and rejection coverage."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import chess_mentor_engine.cli as cli_module
from chess_mentor_engine.analysis import AnalysisLimit, AnalysisRequest, PositionAnalysis
from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.cli import main
from chess_mentor_engine.selection import compare_played_decision
from chess_mentor_engine.storage import LocalArtifactStore

SIMPLE_PGN = """[Event "M17 fixture"]
[White "Ada"]
[Black "Grace"]
[Result "*"]

1. e4 e5 *
"""

MATE_PGN = """[Event "M17 mate fixture"]
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


def _game(text: str = SIMPLE_PGN):
    return ingest_pgn(text.encode("utf-8")).games[0]


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


def _argv(
    path: Path,
    engine: str,
    *,
    ply: int = 0,
    multipv: int = 2,
) -> tuple[str, ...]:
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
        "--with-presentation",
    )


def test_bridge_emits_exact_m15_projection_and_preserves_m14_archive(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    game = _game()
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[0].fen: (
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

    code, payload, error = _invoke(
        capsys,
        *_argv(path, engine),
        "--db",
        str(db),
        "--participant",
        "P01",
    )

    assert code == 0 and error == ""
    package = payload["package"]
    presentation = payload["presentation"]
    assert package["schema_version"] == "m14.engine-analysis-cli.v1"
    assert presentation["schema_version"] == "m15.evaluation-presentation.v1"
    assert presentation["comparison"]["exact_centipawn_delta_for_mover"] == 30
    assert presentation["comparison"]["comparison_id"] == (
        package["decision_comparison"]["comparison_id"]
    )
    root_record = package["root_analysis"]["record"]
    assert presentation["root_analysis"]["request_fingerprint"] == (
        root_record["request_fingerprint"]
    )
    assert presentation["root_analysis"]["result_fingerprint"] == (
        root_record["result_fingerprint"]
    )
    assert presentation["evidence_refs"]["root_analysis"] == (
        package["decision_comparison"]["root_analysis_ref"]
    )

    refs = store.list_refs(participant_id="P01")
    assert len(refs) == 1
    stored = store.get(refs[0], participant_id="P01")
    assert stored.payload == package
    assert "presentation" not in stored.payload


def test_bridge_projects_black_perspective_and_reverses_bound(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    game = _game()
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[1].fen: (
                (
                    "info depth 8 multipv 1 score cp 50 upperbound pv c7c5 g1f3",
                    "info depth 8 multipv 2 score cp 20 pv e7e5 g1f3",
                ),
                "c7c5",
            )
        },
    )

    code, payload, error = _invoke(capsys, *_argv(path, engine, ply=1))

    assert code == 0 and error == ""
    comparison = payload["presentation"]["comparison"]
    best = comparison["best_evaluation"]
    assert best["white"] == {"centipawns": -50, "bound": "lower"}
    assert best["decision_mover"] == {
        "side": "black",
        "centipawns": 50,
        "bound": "upper",
    }
    assert comparison["evidence_quality"] == "bounded"
    assert comparison["exact_centipawn_delta_for_mover"] is None


def test_bridge_keeps_mate_symbolic(tmp_path, capsys) -> None:
    path = _pgn(tmp_path, MATE_PGN)
    game = _game(MATE_PGN)
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[3].fen: (
                ("info depth 8 score mate 1 pv d8h4",),
                "d8h4",
            )
        },
    )

    code, payload, error = _invoke(
        capsys, *_argv(path, engine, ply=3, multipv=1)
    )

    assert code == 0 and error == ""
    evaluation = payload["presentation"]["comparison"]["best_evaluation"]
    assert evaluation["kind"] == "mate"
    assert evaluation["winner"] == "black"
    assert evaluation["plies_to_mate"] == 1
    assert "centipawns" not in evaluation
    assert payload["presentation"]["comparison"]["mate_relation"] == (
        "forced_mate_completed"
    )


def test_bridge_preserves_child_incompatibility_without_fake_loss(
    tmp_path, capsys
) -> None:
    path = _pgn(tmp_path)
    game = _game()
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[0].fen: (
                ("info depth 8 score cp 40 pv d2d4 d7d5",),
                "d2d4",
            ),
            game.positions[1].fen: (
                ("info depth 8 score cp 20 pv e7e5 g1f3",),
                "e7e5",
            ),
        },
        identities=("FakeFish A", "FakeFish B"),
    )

    code, payload, error = _invoke(
        capsys, *_argv(path, engine, multipv=1)
    )

    assert code == 0 and error == ""
    presentation = payload["presentation"]
    assert presentation["played_child_analysis"] is not None
    comparison = presentation["comparison"]
    assert comparison["comparison_kind"] == "incompatible_analysis_regime"
    assert comparison["evidence_quality"] == "incompatible"
    assert comparison["exact_centipawn_delta_for_mover"] is None


def test_bridge_rejects_tampered_comparison_before_archive(
    tmp_path, capsys, monkeypatch
) -> None:
    path = _pgn(tmp_path)
    game = _game()
    position = game.positions[0]
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
    root = cli_module.UciAnalysisProvider(engine).analyze(position, request)
    assert isinstance(root, PositionAnalysis)
    native = compare_played_decision(
        game=game,
        position=position,
        root_analysis=root,
    )
    tampered = replace(native, best_move_uci="a2a3")

    monkeypatch.setattr(
        cli_module,
        "compare_played_decision",
        lambda **kwargs: tampered,
    )
    db = tmp_path / "evidence.sqlite"
    store = LocalArtifactStore(db)

    code, payload, error = _invoke(
        capsys,
        *_argv(path, engine),
        "--db",
        str(db),
        "--participant",
        "P01",
    )

    assert code == 2 and payload is None
    assert "comparison best move mismatch" in error
    assert store.list_refs(participant_id="P01") == ()
