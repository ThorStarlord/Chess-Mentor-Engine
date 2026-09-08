"""Deterministic, engine-free Position Context Packets."""

from __future__ import annotations

from ._core import FILES, Board, square_name
from .model import (
    CanonicalGame,
    CanonicalPosition,
    MaterialSide,
    MaterialSummary,
    PieceGroup,
    PositionContextPacket,
)

_PIECE_ORDER = (
    ("King", "k"),
    ("Queen", "q"),
    ("Rook", "r"),
    ("Bishop", "b"),
    ("Knight", "n"),
    ("Pawn", "p"),
)


def build_position_context(
    game: CanonicalGame, position: CanonicalPosition
) -> PositionContextPacket:
    if position.game_id != game.game_id:
        raise ValueError("position does not belong to supplied game")
    board = Board.from_fen(position.fen)
    return PositionContextPacket(
        position_id=position.position_id,
        game_id=position.game_id,
        ply_index=position.ply_index,
        move_number=position.move_number,
        side_to_move=position.side_to_move,
        fen=position.fen,
        board_ascii=_board_ascii(board),
        piece_map=_piece_map(board),
        material_summary=_material_summary(board),
        provenance=game.provenance,
    )


def _board_ascii(board: Board) -> str:
    lines: list[str] = []
    for rank in range(7, -1, -1):
        cells = [board.squares[rank * 8 + file_index] or "." for file_index in range(8)]
        lines.append(f"{rank + 1}  " + " ".join(cells))
    lines.append("   " + " ".join(FILES))
    return "\n".join(lines)


def _piece_map(board: Board) -> tuple[PieceGroup, ...]:
    groups: list[PieceGroup] = []
    for color in ("white", "black"):
        for name, symbol in _PIECE_ORDER:
            wanted = symbol.upper() if color == "white" else symbol
            squares = tuple(
                square_name(index)
                for index, piece in enumerate(board.squares)
                if piece == wanted
            )
            if squares:
                groups.append(PieceGroup(color=color, piece=name, squares=squares))
    return tuple(groups)


def _material_summary(board: Board) -> MaterialSummary:
    def side(color: str) -> MaterialSide:
        def count(symbol: str) -> int:
            wanted = symbol.upper() if color == "white" else symbol
            return sum(piece == wanted for piece in board.squares)

        return MaterialSide(
            queen=count("q"),
            rook=count("r"),
            bishop=count("b"),
            knight=count("n"),
            pawn=count("p"),
        )

    return MaterialSummary(white=side("white"), black=side("black"))
