"""Private Standard-chess replay core for the M1 evidence substrate.

The core implements the rules needed to replay Standard chess, including custom
FEN starts. Public M1 records do not expose these objects, so a mature rules
library can replace this implementation later without changing evidence contracts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import FenError, PgnError

FILES = "abcdefgh"
RANKS = "12345678"
STANDARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PROMOTIONS = "qrbn"
KNIGHT_STEPS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
KING_STEPS = ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1))
BISHOP_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def square_name(square: int) -> str:
    return FILES[square % 8] + RANKS[square // 8]


def parse_square(name: str) -> int:
    if len(name) != 2 or name[0] not in FILES or name[1] not in RANKS:
        raise FenError(f"invalid square: {name!r}")
    return FILES.index(name[0]) + 8 * RANKS.index(name[1])


def color_of(piece: str) -> str:
    return "white" if piece.isupper() else "black"


def opposite(color: str) -> str:
    return "black" if color == "white" else "white"


@dataclass(frozen=True, slots=True)
class Move:
    from_square: int
    to_square: int
    promotion: str | None = None

    def uci(self) -> str:
        suffix = self.promotion or ""
        return f"{square_name(self.from_square)}{square_name(self.to_square)}{suffix}"


class Board:
    def __init__(
        self,
        squares: list[str | None],
        turn: str,
        castling: str,
        ep_square: int | None,
        halfmove_clock: int,
        fullmove_number: int,
    ) -> None:
        self.squares = squares
        self.turn = turn
        self.castling = "".join(ch for ch in "KQkq" if ch in castling)
        self.ep_square = ep_square
        self.halfmove_clock = halfmove_clock
        self.fullmove_number = fullmove_number

    @classmethod
    def from_fen(cls, fen: str) -> Board:
        parts = fen.strip().split()
        if len(parts) != 6:
            raise FenError("FEN must contain six fields")
        placement, active, castling, ep, halfmove, fullmove = parts
        ranks = placement.split("/")
        if len(ranks) != 8:
            raise FenError("FEN piece placement must contain eight ranks")
        squares: list[str | None] = [None] * 64
        allowed = set("pnbrqkPNBRQK")
        for fen_rank_index, token in enumerate(ranks):
            board_rank = 7 - fen_rank_index
            file_index = 0
            for ch in token:
                if ch.isdigit():
                    count = int(ch)
                    if not 1 <= count <= 8:
                        raise FenError("invalid empty-square count in FEN")
                    file_index += count
                elif ch in allowed:
                    if file_index >= 8:
                        raise FenError("too many squares in FEN rank")
                    squares[board_rank * 8 + file_index] = ch
                    file_index += 1
                else:
                    raise FenError(f"invalid FEN piece token: {ch!r}")
            if file_index != 8:
                raise FenError("FEN rank does not contain exactly eight squares")
        if active not in {"w", "b"}:
            raise FenError("invalid active-color field")
        if castling != "-" and (
            not castling or any(ch not in "KQkq" for ch in castling)
        ):
            raise FenError("invalid castling field")
        ep_square = None if ep == "-" else parse_square(ep)
        try:
            halfmove_clock = int(halfmove)
            fullmove_number = int(fullmove)
        except ValueError as exc:
            raise FenError("invalid FEN move counters") from exc
        if halfmove_clock < 0 or fullmove_number < 1:
            raise FenError("invalid FEN move counters")
        board = cls(
            squares=squares,
            turn="white" if active == "w" else "black",
            castling="" if castling == "-" else castling,
            ep_square=ep_square,
            halfmove_clock=halfmove_clock,
            fullmove_number=fullmove_number,
        )
        if board._king_square("white") is None or board._king_square("black") is None:
            raise FenError("FEN must contain both kings")
        return board

    def copy(self) -> Board:
        return Board(
            self.squares.copy(),
            self.turn,
            self.castling,
            self.ep_square,
            self.halfmove_clock,
            self.fullmove_number,
        )

    def fen(self) -> str:
        rank_tokens: list[str] = []
        for rank in range(7, -1, -1):
            token = ""
            empties = 0
            for file_index in range(8):
                piece = self.squares[rank * 8 + file_index]
                if piece is None:
                    empties += 1
                else:
                    if empties:
                        token += str(empties)
                        empties = 0
                    token += piece
            if empties:
                token += str(empties)
            rank_tokens.append(token)
        active = "w" if self.turn == "white" else "b"
        castling = self.castling or "-"
        ep = "-" if self.ep_square is None else square_name(self.ep_square)
        return (
            f"{'/'.join(rank_tokens)} {active} {castling} {ep} "
            f"{self.halfmove_clock} {self.fullmove_number}"
        )

    def _king_square(self, color: str) -> int | None:
        king = "K" if color == "white" else "k"
        try:
            return self.squares.index(king)
        except ValueError:
            return None

    def is_square_attacked(self, square: int, by_color: str) -> bool:
        file_index, rank = square % 8, square // 8
        pawn = "P" if by_color == "white" else "p"
        pawn_rank_delta = -1 if by_color == "white" else 1
        source_rank = rank + pawn_rank_delta
        if 0 <= source_rank < 8:
            for source_file in (file_index - 1, file_index + 1):
                if (
                    0 <= source_file < 8
                    and self.squares[source_rank * 8 + source_file] == pawn
                ):
                    return True
        knight = "N" if by_color == "white" else "n"
        for df, dr in KNIGHT_STEPS:
            sf, sr = file_index + df, rank + dr
            if 0 <= sf < 8 and 0 <= sr < 8 and self.squares[sr * 8 + sf] == knight:
                return True
        king = "K" if by_color == "white" else "k"
        for df, dr in KING_STEPS:
            sf, sr = file_index + df, rank + dr
            if 0 <= sf < 8 and 0 <= sr < 8 and self.squares[sr * 8 + sf] == king:
                return True
        bishop = {"B", "Q"} if by_color == "white" else {"b", "q"}
        rook = {"R", "Q"} if by_color == "white" else {"r", "q"}
        for directions, attackers in ((BISHOP_DIRS, bishop), (ROOK_DIRS, rook)):
            for df, dr in directions:
                sf, sr = file_index + df, rank + dr
                while 0 <= sf < 8 and 0 <= sr < 8:
                    piece = self.squares[sr * 8 + sf]
                    if piece is not None:
                        if piece in attackers:
                            return True
                        break
                    sf += df
                    sr += dr
        return False

    def is_in_check(self, color: str) -> bool:
        king_square = self._king_square(color)
        if king_square is None:
            return True
        return self.is_square_attacked(king_square, opposite(color))

    def _yield_pawn_moves(self, square: int, piece: str):
        color = color_of(piece)
        file_index, rank = square % 8, square // 8
        direction = 1 if color == "white" else -1
        start_rank = 1 if color == "white" else 6
        promotion_rank = 7 if color == "white" else 0
        one_rank = rank + direction
        if 0 <= one_rank < 8:
            one = one_rank * 8 + file_index
            if self.squares[one] is None:
                if one_rank == promotion_rank:
                    for promotion in PROMOTIONS:
                        yield Move(square, one, promotion)
                else:
                    yield Move(square, one)
                    if rank == start_rank:
                        two_rank = rank + 2 * direction
                        two = two_rank * 8 + file_index
                        if self.squares[two] is None:
                            yield Move(square, two)
        for target_file in (file_index - 1, file_index + 1):
            target_rank = rank + direction
            if not (0 <= target_file < 8 and 0 <= target_rank < 8):
                continue
            target = target_rank * 8 + target_file
            target_piece = self.squares[target]
            is_enemy = target_piece is not None and color_of(target_piece) != color
            is_ep = self.ep_square == target and target_piece is None
            if is_enemy or is_ep:
                if target_rank == promotion_rank:
                    for promotion in PROMOTIONS:
                        yield Move(square, target, promotion)
                else:
                    yield Move(square, target)

    def _yield_step_moves(self, square: int, piece: str, steps):
        color = color_of(piece)
        file_index, rank = square % 8, square // 8
        for df, dr in steps:
            target_file, target_rank = file_index + df, rank + dr
            if not (0 <= target_file < 8 and 0 <= target_rank < 8):
                continue
            target = target_rank * 8 + target_file
            target_piece = self.squares[target]
            if target_piece is None or color_of(target_piece) != color:
                yield Move(square, target)

    def _yield_ray_moves(self, square: int, piece: str, directions):
        color = color_of(piece)
        file_index, rank = square % 8, square // 8
        for df, dr in directions:
            target_file, target_rank = file_index + df, rank + dr
            while 0 <= target_file < 8 and 0 <= target_rank < 8:
                target = target_rank * 8 + target_file
                target_piece = self.squares[target]
                if target_piece is None:
                    yield Move(square, target)
                else:
                    if color_of(target_piece) != color:
                        yield Move(square, target)
                    break
                target_file += df
                target_rank += dr

    def _yield_castles(self, color: str):
        if self.is_in_check(color):
            return
        if color == "white":
            king_sq, king_piece = parse_square("e1"), "K"
            rook_piece = "R"
            options = (
                ("K", "h1", ("f1", "g1"), ("f1", "g1"), "g1"),
                ("Q", "a1", ("d1", "c1", "b1"), ("d1", "c1"), "c1"),
            )
        else:
            king_sq, king_piece = parse_square("e8"), "k"
            rook_piece = "r"
            options = (
                ("k", "h8", ("f8", "g8"), ("f8", "g8"), "g8"),
                ("q", "a8", ("d8", "c8", "b8"), ("d8", "c8"), "c8"),
            )
        if self.squares[king_sq] != king_piece:
            return
        for right, rook_name, empty_names, safe_names, target_name in options:
            if right not in self.castling:
                continue
            rook_sq = parse_square(rook_name)
            if self.squares[rook_sq] != rook_piece:
                continue
            if any(
                self.squares[parse_square(name)] is not None
                for name in empty_names
            ):
                continue
            if any(
                self.is_square_attacked(parse_square(name), opposite(color))
                for name in safe_names
            ):
                continue
            yield Move(king_sq, parse_square(target_name))

    def pseudo_legal_moves(self):
        for square, piece in enumerate(self.squares):
            if piece is None or color_of(piece) != self.turn:
                continue
            kind = piece.lower()
            if kind == "p":
                yield from self._yield_pawn_moves(square, piece)
            elif kind == "n":
                yield from self._yield_step_moves(square, piece, KNIGHT_STEPS)
            elif kind == "b":
                yield from self._yield_ray_moves(square, piece, BISHOP_DIRS)
            elif kind == "r":
                yield from self._yield_ray_moves(square, piece, ROOK_DIRS)
            elif kind == "q":
                yield from self._yield_ray_moves(square, piece, BISHOP_DIRS + ROOK_DIRS)
            elif kind == "k":
                yield from self._yield_step_moves(square, piece, KING_STEPS)
                yield from self._yield_castles(self.turn)

    def legal_moves(self) -> list[Move]:
        color = self.turn
        result: list[Move] = []
        for move in self.pseudo_legal_moves():
            clone = self.copy()
            clone.push(move)
            if not clone.is_in_check(color):
                result.append(move)
        return result

    def _is_castling_move(self, move: Move, piece: str) -> bool:
        file_delta = abs((move.to_square % 8) - (move.from_square % 8))
        return piece.lower() == "k" and file_delta == 2

    def _is_en_passant(self, move: Move, piece: str) -> bool:
        return (
            piece.lower() == "p"
            and self.ep_square == move.to_square
            and self.squares[move.to_square] is None
            and move.from_square % 8 != move.to_square % 8
        )

    def push(self, move: Move) -> None:
        piece = self.squares[move.from_square]
        if piece is None or color_of(piece) != self.turn:
            raise PgnError(
                f"illegal move {move.uci()}: no side-to-move piece on source square"
            )
        target_piece = self.squares[move.to_square]
        is_capture = target_piece is not None
        is_ep = self._is_en_passant(move, piece)
        is_castling = self._is_castling_move(move, piece)
        if is_ep:
            capture_square = (
                move.to_square - 8
                if self.turn == "white"
                else move.to_square + 8
            )
            target_piece = self.squares[capture_square]
            self.squares[capture_square] = None
            is_capture = True
        self.squares[move.from_square] = None
        placed = piece
        if move.promotion is not None:
            if piece.lower() != "p" or move.promotion not in PROMOTIONS:
                raise PgnError("invalid promotion")
            placed = (
                move.promotion.upper()
                if self.turn == "white"
                else move.promotion.lower()
            )
        self.squares[move.to_square] = placed
        if is_castling:
            if move.to_square % 8 == 6:
                rook_from = move.to_square + 1
                rook_to = move.to_square - 1
            else:
                rook_from = move.to_square - 2
                rook_to = move.to_square + 1
            self.squares[rook_to] = self.squares[rook_from]
            self.squares[rook_from] = None
        self._update_castling_rights(move, piece, target_piece)
        if piece.lower() == "p" and abs(move.to_square - move.from_square) == 16:
            self.ep_square = (move.to_square + move.from_square) // 2
        else:
            self.ep_square = None
        self.halfmove_clock = (
            0
            if piece.lower() == "p" or is_capture
            else self.halfmove_clock + 1
        )
        if self.turn == "black":
            self.fullmove_number += 1
        self.turn = opposite(self.turn)

    def _update_castling_rights(
        self, move: Move, piece: str, captured: str | None
    ) -> None:
        rights = set(self.castling)
        mapping = {
            parse_square("a1"): "Q",
            parse_square("h1"): "K",
            parse_square("a8"): "q",
            parse_square("h8"): "k",
        }
        if piece == "K":
            rights -= {"K", "Q"}
        elif piece == "k":
            rights -= {"k", "q"}
        if piece.lower() == "r" and move.from_square in mapping:
            rights.discard(mapping[move.from_square])
        if (
            captured is not None
            and captured.lower() == "r"
            and move.to_square in mapping
        ):
            rights.discard(mapping[move.to_square])
        self.castling = "".join(ch for ch in "KQkq" if ch in rights)

    def san(self, move: Move) -> str:
        legal = self.legal_moves()
        if move not in legal:
            raise PgnError(f"move is not legal in current position: {move.uci()}")
        piece = self.squares[move.from_square]
        assert piece is not None
        if self._is_castling_move(move, piece):
            base = "O-O" if move.to_square % 8 == 6 else "O-O-O"
        else:
            target_piece = self.squares[move.to_square]
            capture = target_piece is not None or self._is_en_passant(move, piece)
            kind = piece.upper()
            if kind == "P":
                prefix = FILES[move.from_square % 8] if capture else ""
            else:
                prefix = kind + self._disambiguation(move, legal, piece)
            base = prefix + ("x" if capture else "") + square_name(move.to_square)
            if move.promotion:
                base += "=" + move.promotion.upper()
        clone = self.copy()
        clone.push(move)
        if clone.is_in_check(clone.turn):
            base += "#" if not clone.legal_moves() else "+"
        return base

    def _disambiguation(self, move: Move, legal: list[Move], piece: str) -> str:
        competitors = [
            other
            for other in legal
            if other != move
            and other.to_square == move.to_square
            and self.squares[other.from_square] == piece
        ]
        if not competitors:
            return ""
        file_index = move.from_square % 8
        rank = move.from_square // 8
        same_file = any(other.from_square % 8 == file_index for other in competitors)
        same_rank = any(other.from_square // 8 == rank for other in competitors)
        if not same_file:
            return FILES[file_index]
        if not same_rank:
            return RANKS[rank]
        return square_name(move.from_square)

    def parse_san(self, token: str) -> tuple[Move, str]:
        normalized = normalize_san(token).rstrip("+#")
        legal = self.legal_moves()
        if normalized in {"O-O", "O-O-O"}:
            target_file = 6 if normalized == "O-O" else 2
            matches = [
                move
                for move in legal
                if self.squares[move.from_square] is not None
                and self.squares[move.from_square].lower() == "k"
                and move.to_square % 8 == target_file
                and self._is_castling_move(move, self.squares[move.from_square])
            ]
        else:
            promotion = None
            promotion_match = re.search(r"=([QRBN])$", normalized)
            if promotion_match:
                promotion = promotion_match.group(1).lower()
                normalized = normalized[: promotion_match.start()]
            if (
                len(normalized) < 2
                or normalized[-2] not in FILES
                or normalized[-1] not in RANKS
            ):
                raise PgnError(
                    "illegal or unrecognized SAN move "
                    f"{token!r} in position {self.fen()}"
                )
            target = parse_square(normalized[-2:])
            prefix = normalized[:-2]
            capture_required = "x" in prefix
            prefix = prefix.replace("x", "")
            piece_kind = "p"
            if prefix and prefix[0] in "KQRBN":
                piece_kind = prefix[0].lower()
                prefix = prefix[1:]
            disambiguation = prefix
            matches = []
            for move in legal:
                piece = self.squares[move.from_square]
                if (
                    piece is None
                    or piece.lower() != piece_kind
                    or move.to_square != target
                ):
                    continue
                if move.promotion != promotion:
                    continue
                is_capture = (
                    self.squares[move.to_square] is not None
                    or self._is_en_passant(move, piece)
                )
                if is_capture != capture_required:
                    continue
                source_name = square_name(move.from_square)
                if disambiguation:
                    if len(disambiguation) == 2 and source_name != disambiguation:
                        continue
                    if len(disambiguation) == 1:
                        if disambiguation in FILES and source_name[0] != disambiguation:
                            continue
                        if disambiguation in RANKS and source_name[1] != disambiguation:
                            continue
                    if len(disambiguation) not in {1, 2}:
                        continue
                matches.append(move)
        if len(matches) != 1:
            reason = "ambiguous" if matches else "illegal or unrecognized"
            raise PgnError(f"{reason} SAN move {token!r} in position {self.fen()}")
        move = matches[0]
        return move, self.san(move)


def normalize_san(token: str) -> str:
    token = token.strip()
    token = token.replace("0-0-0", "O-O-O").replace("0-0", "O-O")
    token = re.sub(r"[!?]+$", "", token)
    token = re.sub(r"\s*e\.p\.?$", "", token, flags=re.IGNORECASE)
    return token


def san_equivalent(left: str, right: str) -> bool:
    if left == right:
        return True
    return left.rstrip("+#") == right.rstrip("+#")
