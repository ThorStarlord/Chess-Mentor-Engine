"""Public M1 chess evidence API."""

from .context import build_position_context
from .errors import ChessEvidenceError, FenError, PgnError, UnsupportedVariantError
from .model import (
    CanonicalGame,
    CanonicalPosition,
    MaterialSide,
    MaterialSummary,
    PgnIngestResult,
    PieceGroup,
    PositionContextPacket,
    SourceProvenance,
    TimeControl,
)
from .pgn import ingest_pgn
from .provenance import canonical_json

__all__ = [
    "CanonicalGame",
    "CanonicalPosition",
    "ChessEvidenceError",
    "FenError",
    "MaterialSide",
    "MaterialSummary",
    "PgnError",
    "PgnIngestResult",
    "PieceGroup",
    "PositionContextPacket",
    "SourceProvenance",
    "TimeControl",
    "UnsupportedVariantError",
    "build_position_context",
    "canonical_json",
    "ingest_pgn",
]
