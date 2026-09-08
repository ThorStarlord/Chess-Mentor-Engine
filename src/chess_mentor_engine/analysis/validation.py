"""Shared legality validation for normalized engine candidate lines."""

from __future__ import annotations

from chess_mentor_engine.chess._core import Board, Move

from .model import CandidateLine


def _find_legal_move(board: Board, uci: str) -> Move | None:
    for move in board.legal_moves():
        if move.uci() == uci:
            return move
    return None


def expected_candidate_count(fen: str, multipv: int) -> int:
    """Return the maximum complete MultiPV line count for one root position."""
    board = Board.from_fen(fen)
    return min(multipv, len(board.legal_moves()))


def validate_candidate_lines(
    fen: str,
    lines: tuple[CandidateLine, ...],
) -> None:
    """Validate ranks, legal roots, uniqueness, and full PV replay."""
    board = Board.from_fen(fen)
    legal_root_moves = {move.uci() for move in board.legal_moves()}

    expected_ranks = tuple(range(1, len(lines) + 1))
    actual_ranks = tuple(line.rank for line in lines)
    if actual_ranks != expected_ranks:
        raise ValueError("candidate ranks must be contiguous starting at 1")

    seen_roots: set[str] = set()
    for line in lines:
        if line.root_move_uci not in legal_root_moves:
            raise ValueError(f"illegal candidate root move: {line.root_move_uci}")
        if line.root_move_uci in seen_roots:
            raise ValueError("candidate root moves must be unique")
        seen_roots.add(line.root_move_uci)
        validate_pv(fen, line)


def validate_pv(fen: str, line: CandidateLine) -> None:
    """Replay one complete PV and reject the first illegal move."""
    if not line.pv_uci:
        return

    board = Board.from_fen(fen)
    for uci in line.pv_uci:
        move = _find_legal_move(board, uci)
        if move is None:
            raise ValueError(f"illegal PV move {uci!r} after {board.fen()}")
        board.push(move)
