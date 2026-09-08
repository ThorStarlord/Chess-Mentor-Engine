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

RESEARCH_FEN = "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22"
MATE_IN_ONE_FEN = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"


def _stockfish_path() -> str:
    path = os.environ.get("STOCKFISH_EXECUTABLE")
    if not path:
        pytest.skip("STOCKFISH_EXECUTABLE is not configured")
    return path


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


def test_stockfish_analyzes_research_position_with_multipv() -> None:
    provider = UciAnalysisProvider(
        _stockfish_path(),
        engine_options=(("Threads", "1"), ("Hash", "16")),
    )
    request = AnalysisRequest(
        multipv=2,
        search_limit=AnalysisLimit("depth", 8),
        supervisor_timeout_ms=10_000,
    )

    outcome = provider.analyze(
        _position(RESEARCH_FEN, "research-context-position"),
        request,
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
    provider = UciAnalysisProvider(
        _stockfish_path(),
        engine_options=(("Threads", "1"), ("Hash", "16")),
    )
    request = AnalysisRequest(
        multipv=1,
        search_limit=AnalysisLimit("depth", 6),
        supervisor_timeout_ms=10_000,
    )

    outcome = provider.analyze(
        _position(MATE_IN_ONE_FEN, "stockfish-mate-position"),
        request,
    )

    assert isinstance(outcome, PositionAnalysis)
    evaluation = outcome.lines[0].evaluation
    assert isinstance(evaluation, MateEvaluation)
    assert evaluation.winner == "white"
    assert evaluation.plies_to_mate == 1
