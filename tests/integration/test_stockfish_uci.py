from __future__ import annotations

import os

import pytest

from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisRequest,
    MateEvaluation,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import CanonicalPosition

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
RESEARCH_FEN = "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22"
QUIET_FEN = "rnbq1rk1/ppppppbp/5np1/8/8/5NP1/PPPPPPBP/RNBQ1RK1 w - - 6 5"
CHECK_FEN = "4k3/8/8/8/8/8/4R3/4K3 b - - 0 1"
CUSTOM_FEN = "8/8/8/8/8/2k5/8/K7 w - - 0 42"
PROMOTION_FEN = "7k/P7/8/8/8/8/8/7K w - - 0 1"
MATE_IN_ONE_FEN = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"
CHECKMATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"


def _stockfish_path() -> str:
    path = os.environ.get("STOCKFISH_EXECUTABLE")
    if not path:
        pytest.skip("STOCKFISH_EXECUTABLE is not configured")
    return path


def _provider() -> UciAnalysisProvider:
    return UciAnalysisProvider(
        _stockfish_path(),
        engine_options=(("Threads", "1"), ("Hash", "16")),
    )


def _position(fen: str, position_id: str) -> CanonicalPosition:
    return CanonicalPosition(
        position_id=position_id,
        game_id="stockfish-qualification",
        ply_index=0,
        move_number=1,
        side_to_move="white" if " w " in fen else "black",
        fen=fen,
        last_move_uci=None,
        last_move_san=None,
    )


def _depth_request(*, multipv: int = 1, depth: int = 8) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit("depth", depth),
        supervisor_timeout_ms=10_000,
    )


def test_stockfish_analyzes_research_position_with_multipv() -> None:
    outcome = _provider().analyze(
        _position(RESEARCH_FEN, "research-context-position"),
        _depth_request(multipv=2),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "complete"
    assert len(outcome.lines) == 2
    assert outcome.best_move == outcome.lines[0].root_move_uci
    assert all(line.pv_uci for line in outcome.lines)
    assert outcome.provenance.protocol == "uci"
    assert "stockfish" in outcome.provenance.engine_name.casefold()
    assert outcome.provenance.binary_sha256
    assert outcome.metrics.depth is not None
    assert outcome.metrics.nodes is not None


def test_stockfish_forced_mate_normalizes_to_white_winner_and_one_ply() -> None:
    outcome = _provider().analyze(
        _position(MATE_IN_ONE_FEN, "stockfish-mate-position"),
        _depth_request(depth=6),
    )

    assert isinstance(outcome, PositionAnalysis)
    evaluation = outcome.lines[0].evaluation
    assert isinstance(evaluation, MateEvaluation)
    assert evaluation.winner == "white"
    assert evaluation.plies_to_mate == 1


@pytest.mark.parametrize(
    ("position_id", "fen"),
    [
        ("standard-start", START_FEN),
        ("quiet-positional", QUIET_FEN),
        ("side-to-move-in-check", CHECK_FEN),
        ("custom-fen", CUSTOM_FEN),
        ("promotion", PROMOTION_FEN),
    ],
)
def test_stockfish_qualification_corpus_returns_legal_complete_analysis(
    position_id: str,
    fen: str,
) -> None:
    outcome = _provider().analyze(
        _position(fen, position_id),
        _depth_request(depth=6),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "complete"
    assert outcome.best_move is not None
    assert len(outcome.lines) == 1
    assert outcome.lines[0].pv_uci
    assert outcome.provenance.binary_sha256


def test_stockfish_terminal_checkmate_is_normalized_without_candidate_move() -> None:
    outcome = _provider().analyze(
        _position(CHECKMATE_FEN, "terminal-checkmate"),
        _depth_request(depth=6),
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "terminal"
    assert outcome.best_move is None
    assert outcome.lines == ()
    assert outcome.termination.reason == "terminal_position"
