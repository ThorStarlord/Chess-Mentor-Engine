"""Deterministic provenance and fingerprint helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

PARSER_ID = "chess-mentor-engine-internal-standard/0.1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> str:
    """Serialize JSON-compatible semantic data deterministically."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def semantic_game_fingerprint(
    *, variant: str, initial_fen: str, moves_uci: Sequence[str]
) -> str:
    payload = {
        "variant": variant,
        "initial_fen": initial_fen,
        "moves_uci": list(moves_uci),
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def position_fingerprint(*, game_fingerprint: str, ply_index: int, fen: str) -> str:
    payload = {
        "game_fingerprint": game_fingerprint,
        "ply_index": ply_index,
        "fen": fen,
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def stable_headers(headers: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(headers.items(), key=lambda item: item[0].casefold()))
