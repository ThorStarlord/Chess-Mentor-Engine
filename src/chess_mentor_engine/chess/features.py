"""Deterministic, engine-free chess features for M2."""

from __future__ import annotations

from ._core import (
    BISHOP_DIRS,
    KING_STEPS,
    KNIGHT_STEPS,
    ROOK_DIRS,
    Board,
    color_of,
    square_name,
)
from .feature_model import (
    AbsolutePin,
    PieceDefense,
    PositionFeaturePacket,
    SquareAttackRelation,
)
from .model import CanonicalPosition

_PIECE_NAMES = {
    "k": "King",
    "q": "Queen",
    "r": "Rook",
    "b": "Bishop",
    "n": "Knight",
    "p": "Pawn",
}


def build_position_features(position: CanonicalPosition) -> PositionFeaturePacket:
    """Derive the bounded M2 feature packet from one canonical position."""
    board = Board.from_fen(position.fen)
    legal = sorted(board.legal_moves(), key=lambda move: move.uci())
    legal_moves = tuple(move.uci() for move in legal)
    legal_checks = tuple(
        move.uci() for move in legal if _move_gives_check(board, move)
    )
    legal_captures = tuple(
        move.uci() for move in legal if _move_is_capture(board, move)
    )
    square_attacks = tuple(_square_attack_relation(board, square) for square in range(64))
    piece_defenders = tuple(_piece_defenses(board))
    absolute_pins = tuple(_absolute_pins(board))
    return PositionFeaturePacket(
        position_id=position.position_id,
        game_id=position.game_id,
        ply_index=position.ply_index,
        side_to_move=position.side_to_move,
        fen=position.fen,
        legal_moves=legal_moves,
        legal_checks=legal_checks,
        legal_captures=legal_captures,
        square_attacks=square_attacks,
        piece_defenders=piece_defenders,
        absolute_pins=absolute_pins,
    )


def _move_is_capture(board: Board, move) -> bool:
    piece = board.squares[move.from_square]
    if piece is None:
        return False
    if board.squares[move.to_square] is not None:
        return True
    return (
        piece.lower() == "p"
        and board.ep_square == move.to_square
        and move.from_square % 8 != move.to_square % 8
    )


def _move_gives_check(board: Board, move) -> bool:
    clone = board.copy()
    clone.push(move)
    return clone.is_in_check(clone.turn)


def _square_attack_relation(board: Board, square: int) -> SquareAttackRelation:
    return SquareAttackRelation(
        square=square_name(square),
        white_attackers=_attacker_names(board, square, "white"),
        black_attackers=_attacker_names(board, square, "black"),
    )


def _attacker_names(board: Board, square: int, color: str) -> tuple[str, ...]:
    return tuple(square_name(source) for source in _attacker_squares(board, square, color))


def _attacker_squares(board: Board, square: int, color: str) -> tuple[int, ...]:
    attackers: list[int] = []
    file_index, rank = square % 8, square // 8

    pawn = "P" if color == "white" else "p"
    source_rank = rank - 1 if color == "white" else rank + 1
    if 0 <= source_rank < 8:
        for source_file in (file_index - 1, file_index + 1):
            if not 0 <= source_file < 8:
                continue
            source = source_rank * 8 + source_file
            if board.squares[source] == pawn:
                attackers.append(source)

    knight = "N" if color == "white" else "n"
    for df, dr in KNIGHT_STEPS:
        source_file, source_rank = file_index + df, rank + dr
        if not (0 <= source_file < 8 and 0 <= source_rank < 8):
            continue
        source = source_rank * 8 + source_file
        if board.squares[source] == knight:
            attackers.append(source)

    king = "K" if color == "white" else "k"
    for df, dr in KING_STEPS:
        source_file, source_rank = file_index + df, rank + dr
        if not (0 <= source_file < 8 and 0 <= source_rank < 8):
            continue
        source = source_rank * 8 + source_file
        if board.squares[source] == king:
            attackers.append(source)

    bishop_attackers = {"B", "Q"} if color == "white" else {"b", "q"}
    rook_attackers = {"R", "Q"} if color == "white" else {"r", "q"}
    for directions, allowed in (
        (BISHOP_DIRS, bishop_attackers),
        (ROOK_DIRS, rook_attackers),
    ):
        for df, dr in directions:
            source_file, source_rank = file_index + df, rank + dr
            while 0 <= source_file < 8 and 0 <= source_rank < 8:
                source = source_rank * 8 + source_file
                piece = board.squares[source]
                if piece is not None:
                    if piece in allowed:
                        attackers.append(source)
                    break
                source_file += df
                source_rank += dr

    return tuple(sorted(attackers))


def _piece_defenses(board: Board):
    for square, piece in enumerate(board.squares):
        if piece is None:
            continue
        color = color_of(piece)
        yield PieceDefense(
            color=color,
            piece=_PIECE_NAMES[piece.lower()],
            square=square_name(square),
            defenders=_attacker_names(board, square, color),
        )


def _absolute_pins(board: Board) -> list[AbsolutePin]:
    pins: list[AbsolutePin] = []
    for color in ("white", "black"):
        king_square = board._king_square(color)
        if king_square is None:
            continue
        king_file, king_rank = king_square % 8, king_square // 8
        for directions, compatible in (
            (BISHOP_DIRS, {"b", "q"}),
            (ROOK_DIRS, {"r", "q"}),
        ):
            for df, dr in directions:
                file_index, rank = king_file + df, king_rank + dr
                blocker: int | None = None
                while 0 <= file_index < 8 and 0 <= rank < 8:
                    square = rank * 8 + file_index
                    piece = board.squares[square]
                    if piece is not None:
                        if blocker is None:
                            if color_of(piece) != color:
                                break
                            blocker = square
                        else:
                            if color_of(piece) != color and piece.lower() in compatible:
                                pins.append(
                                    AbsolutePin(
                                        color=color,
                                        pinned_square=square_name(blocker),
                                        king_square=square_name(king_square),
                                        attacker_square=square_name(square),
                                    )
                                )
                            break
                    file_index += df
                    rank += dr
    return sorted(
        pins,
        key=lambda pin: (
            0 if pin.color == "white" else 1,
            pin.pinned_square,
            pin.attacker_square,
        ),
    )
