"""Immutable records for deterministic M2 chess features."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SquareAttackRelation:
    square: str
    white_attackers: tuple[str, ...]
    black_attackers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "square": self.square,
            "white_attackers": list(self.white_attackers),
            "black_attackers": list(self.black_attackers),
        }


@dataclass(frozen=True, slots=True)
class PieceDefense:
    color: str
    piece: str
    square: str
    defenders: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "color": self.color,
            "piece": self.piece,
            "square": self.square,
            "defenders": list(self.defenders),
        }


@dataclass(frozen=True, slots=True)
class AbsolutePin:
    color: str
    pinned_square: str
    king_square: str
    attacker_square: str

    def to_dict(self) -> dict[str, str]:
        return {
            "color": self.color,
            "pinned_square": self.pinned_square,
            "king_square": self.king_square,
            "attacker_square": self.attacker_square,
        }


@dataclass(frozen=True, slots=True)
class PositionFeaturePacket:
    position_id: str
    game_id: str
    ply_index: int
    side_to_move: str
    fen: str
    legal_moves: tuple[str, ...]
    legal_checks: tuple[str, ...]
    legal_captures: tuple[str, ...]
    square_attacks: tuple[SquareAttackRelation, ...]
    piece_defenders: tuple[PieceDefense, ...]
    absolute_pins: tuple[AbsolutePin, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "ply_index": self.ply_index,
            "side_to_move": self.side_to_move,
            "fen": self.fen,
            "legal_moves": list(self.legal_moves),
            "legal_checks": list(self.legal_checks),
            "legal_captures": list(self.legal_captures),
            "square_attacks": [item.to_dict() for item in self.square_attacks],
            "piece_defenders": [item.to_dict() for item in self.piece_defenders],
            "absolute_pins": [item.to_dict() for item in self.absolute_pins],
        }
