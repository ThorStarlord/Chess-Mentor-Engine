"""Immutable semantic records for M1 chess evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceProvenance:
    source_type: str
    source_sha256: str
    source_game_index: int
    parser_id: str
    raw_headers: tuple[tuple[str, str], ...]
    source_game_identifier: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_sha256": self.source_sha256,
            "source_game_index": self.source_game_index,
            "parser_id": self.parser_id,
            "raw_headers": [[key, value] for key, value in self.raw_headers],
            "source_game_identifier": self.source_game_identifier,
        }


@dataclass(frozen=True, slots=True)
class TimeControl:
    raw: str | None
    base_seconds: int | None = None
    increment_seconds: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw,
            "base_seconds": self.base_seconds,
            "increment_seconds": self.increment_seconds,
        }


@dataclass(frozen=True, slots=True)
class CanonicalPosition:
    position_id: str
    game_id: str
    ply_index: int
    move_number: int
    side_to_move: str
    fen: str
    last_move_uci: str | None
    last_move_san: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "ply_index": self.ply_index,
            "move_number": self.move_number,
            "side_to_move": self.side_to_move,
            "fen": self.fen,
            "last_move_uci": self.last_move_uci,
            "last_move_san": self.last_move_san,
        }


@dataclass(frozen=True, slots=True)
class CanonicalGame:
    game_id: str
    semantic_fingerprint: str
    provenance: SourceProvenance
    headers: tuple[tuple[str, str], ...]
    white: str | None
    black: str | None
    result: str | None
    date: str | None
    time_control: TimeControl
    variant: str
    initial_fen: str
    moves_uci: tuple[str, ...]
    moves_san: tuple[str, ...]
    positions: tuple[CanonicalPosition, ...]

    @property
    def mainline_move_count(self) -> int:
        return len(self.moves_uci)

    def to_dict(self) -> dict[str, Any]:
        return {
            "game_id": self.game_id,
            "semantic_fingerprint": self.semantic_fingerprint,
            "provenance": self.provenance.to_dict(),
            "headers": [[key, value] for key, value in self.headers],
            "white": self.white,
            "black": self.black,
            "result": self.result,
            "date": self.date,
            "time_control": self.time_control.to_dict(),
            "variant": self.variant,
            "initial_fen": self.initial_fen,
            "moves_uci": list(self.moves_uci),
            "moves_san": list(self.moves_san),
            "positions": [position.to_dict() for position in self.positions],
        }


@dataclass(frozen=True, slots=True)
class PieceGroup:
    color: str
    piece: str
    squares: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"color": self.color, "piece": self.piece, "squares": list(self.squares)}


@dataclass(frozen=True, slots=True)
class MaterialSide:
    queen: int
    rook: int
    bishop: int
    knight: int
    pawn: int

    def to_dict(self) -> dict[str, int]:
        return {
            "queen": self.queen,
            "rook": self.rook,
            "bishop": self.bishop,
            "knight": self.knight,
            "pawn": self.pawn,
        }


@dataclass(frozen=True, slots=True)
class MaterialSummary:
    white: MaterialSide
    black: MaterialSide

    def to_dict(self) -> dict[str, Any]:
        return {"white": self.white.to_dict(), "black": self.black.to_dict()}


@dataclass(frozen=True, slots=True)
class PositionContextPacket:
    position_id: str
    game_id: str
    ply_index: int
    move_number: int
    side_to_move: str
    fen: str
    board_ascii: str
    piece_map: tuple[PieceGroup, ...]
    material_summary: MaterialSummary
    provenance: SourceProvenance

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "ply_index": self.ply_index,
            "move_number": self.move_number,
            "side_to_move": self.side_to_move,
            "fen": self.fen,
            "board_ascii": self.board_ascii,
            "piece_map": [group.to_dict() for group in self.piece_map],
            "material_summary": self.material_summary.to_dict(),
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class PgnIngestResult:
    source_sha256: str
    games: tuple[CanonicalGame, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "games": [game.to_dict() for game in self.games],
        }
