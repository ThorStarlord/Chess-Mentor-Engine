from __future__ import annotations

from pathlib import Path

import pytest

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisRequest,
    CentipawnEvaluation,
    MateEvaluation,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import CanonicalPosition

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BLACK_START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
MATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"


def _position(fen: str, position_id: str = "pos-uci") -> CanonicalPosition:
    return CanonicalPosition(
        position_id=position_id,
        game_id="game-uci",
        ply_index=0,
        move_number=1,
        side_to_move="white" if " w " in fen else "black",
        fen=fen,
        last_move_uci=None,
        last_move_san=None,
    )


def _request(
    *,
    multipv: int = 1,
    kind: str = "depth",
    value: int = 12,
    timeout_ms: int | None = 1_000,
) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit(kind, value),
        supervisor_timeout_ms=timeout_ms,
    )


def _write_fake_engine(
    tmp_path: Path,
    *,
    info_lines: tuple[str, ...] = (),
    bestmove: str | None = "e2e4",
    advertise_multipv: bool = True,
    advertise_threads: bool = True,
    sleep_seconds: float = 0.0,
    exit_on_go: bool = False,
    expected_go: str | None = None,
) -> str:
    path = tmp_path / "fake-uci-engine"
    script = f'''#!/usr/bin/env python3
import sys
import time

INFO_LINES = {info_lines!r}
BESTMOVE = {bestmove!r}
ADVERTISE_MULTIPV = {advertise_multipv!r}
ADVERTISE_THREADS = {advertise_threads!r}
SLEEP_SECONDS = {sleep_seconds!r}
EXIT_ON_GO = {exit_on_go!r}
EXPECTED_GO = {expected_go!r}

for raw in sys.stdin:
    command = raw.strip()
    if command == "uci":
        print("id name FakeFish 1.0", flush=True)
        print("id author Chess Mentor Tests", flush=True)
        if ADVERTISE_MULTIPV:
            print("option name MultiPV type spin default 1 min 1 max 8", flush=True)
        if ADVERTISE_THREADS:
            print("option name Threads type spin default 1 min 1 max 8", flush=True)
        print("uciok", flush=True)
    elif command == "isready":
        print("readyok", flush=True)
    elif command.startswith("go "):
        if EXPECTED_GO is not None and command != EXPECTED_GO:
            print("bestmove (none)", flush=True)
            continue
        if EXIT_ON_GO:
            sys.exit(7)
        for item in INFO_LINES:
            print(item, flush=True)
        if SLEEP_SECONDS:
            time.sleep(SLEEP_SECONDS)
        if BESTMOVE is not None:
            print("bestmove " + BESTMOVE, flush=True)
    elif command == "quit":
        break
'''
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def test_uci_provider_returns_complete_multipv_with_provenance(
    tmp_path: Path,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            (
                "info depth 12 seldepth 16 multipv 1 score cp 31 nodes 1234 "
                "nps 5000 hashfull 10 tbhits 0 time 20 pv e2e4 e7e5 g1f3"
            ),
            (
                "info depth 12 multipv 2 score cp 24 nodes 1234 time 20 "
                "pv d2d4 d7d5 c1f4"
            ),
        ),
        bestmove="e2e4",
    )
    provider = UciAnalysisProvider(
        executable,
        engine_options=(("Threads", "1"),),
    )

    outcome = provider.analyze(_position(START_FEN), _request(multipv=2))

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "complete"
    assert outcome.best_move == "e2e4"
    assert len(outcome.lines) == 2
    assert outcome.metrics.depth == 12
    assert outcome.metrics.nodes == 1234
    assert outcome.provenance.protocol == "uci"
    assert outcome.provenance.engine_name == "FakeFish 1.0"
    assert outcome.provenance.engine_author == "Chess Mentor Tests"
    assert outcome.provenance.binary_sha256
    assert ("MultiPV", "2") in outcome.provenance.engine_options
    assert ("Threads", "1") in outcome.provenance.engine_options
    assert outcome.request_fingerprint
    assert outcome.result_fingerprint


def test_uci_centipawn_score_is_normalized_to_white_perspective(
    tmp_path: Path,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 8 score cp 50 pv e7e5 e2e4",
        ),
        bestmove="e7e5",
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(BLACK_START_FEN),
        _request(value=8),
    )

    assert isinstance(outcome, PositionAnalysis)
    evaluation = outcome.lines[0].evaluation
    assert isinstance(evaluation, CentipawnEvaluation)
    assert evaluation.centipawns == -50


@pytest.mark.parametrize(
    ("fen", "score", "pv", "bestmove", "winner", "plies"),
    [
        (START_FEN, 2, "e2e4 e7e5", "e2e4", "white", 3),
        (BLACK_START_FEN, -2, "e7e5 e2e4", "e7e5", "white", 4),
    ],
)
def test_uci_mate_score_normalizes_moves_to_winner_and_plies(
    tmp_path: Path,
    fen: str,
    score: int,
    pv: str,
    bestmove: str,
    winner: str,
    plies: int,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(f"info depth 8 score mate {score} pv {pv}",),
        bestmove=bestmove,
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(fen),
        _request(value=8),
    )

    assert isinstance(outcome, PositionAnalysis)
    evaluation = outcome.lines[0].evaluation
    assert isinstance(evaluation, MateEvaluation)
    assert evaluation.winner == winner
    assert evaluation.plies_to_mate == plies


def test_uci_score_bound_is_preserved(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 7 score cp 22 lowerbound pv e2e4 e7e5",
        ),
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(value=7),
    )

    assert isinstance(outcome, PositionAnalysis)
    evaluation = outcome.lines[0].evaluation
    assert isinstance(evaluation, CentipawnEvaluation)
    assert evaluation.bound == "lower"


def test_missing_uci_executable_is_explicit_failure(tmp_path: Path) -> None:
    missing = str(tmp_path / "does-not-exist")

    outcome = UciAnalysisProvider(missing).analyze(
        _position(START_FEN),
        _request(),
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "ENGINE_NOT_FOUND"
    assert outcome.request_fingerprint


def test_multipv_request_requires_advertised_option(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        advertise_multipv=False,
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(multipv=2),
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "UNSUPPORTED_REQUEST"


def test_configured_option_must_be_advertised(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        advertise_threads=False,
    )

    outcome = UciAnalysisProvider(
        executable,
        engine_options=(("Threads", "1"),),
    ).analyze(_position(START_FEN), _request())

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "UNSUPPORTED_REQUEST"


def test_timeout_retains_valid_partial_evidence(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 4 score cp 15 nodes 100 pv e2e4 e7e5",
        ),
        sleep_seconds=1.0,
    )
    provider = UciAnalysisProvider(
        executable,
        stop_grace_ms=50,
    )

    outcome = provider.analyze(
        _position(START_FEN),
        _request(timeout_ms=50),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "partial"
    assert outcome.best_move == "e2e4"
    assert outcome.termination.reason == "timeout"


def test_engine_crash_without_evidence_is_explicit_failure(
    tmp_path: Path,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        exit_on_go=True,
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(),
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "ENGINE_CRASHED"


def test_illegal_uci_pv_is_invalid_engine_output(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 8 score cp 20 pv e2e4 e7e5 e1e3",
        ),
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(value=8),
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "INVALID_ENGINE_OUTPUT"
    assert "illegal PV move" in outcome.message


def test_bestmove_must_agree_with_rank_one(tmp_path: Path) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 8 score cp 20 pv e2e4 e7e5",
        ),
        bestmove="d2d4",
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(value=8),
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "INVALID_ENGINE_OUTPUT"
    assert "bestmove disagrees" in outcome.message


def test_terminal_position_is_detected_without_engine_search(
    tmp_path: Path,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        bestmove=None,
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(MATE_FEN, "mate-root"),
        _request(),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "terminal"
    assert outcome.lines == ()
    assert outcome.termination.reason == "terminal_position"


@pytest.mark.parametrize(
    ("kind", "value", "expected_go"),
    [
        ("depth", 9, "go depth 9"),
        ("nodes", 321, "go nodes 321"),
        ("movetime_ms", 75, "go movetime 75"),
    ],
)
def test_search_limit_maps_to_uci_go_command(
    tmp_path: Path,
    kind: str,
    value: int,
    expected_go: str,
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(
            "info depth 4 score cp 10 pv e2e4 e7e5",
        ),
        expected_go=expected_go,
    )

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN),
        _request(kind=kind, value=value),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.best_move == "e2e4"
