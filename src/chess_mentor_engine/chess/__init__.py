"""Public deterministic chess evidence and feature API."""

from .context import build_position_context
from .errors import ChessEvidenceError, FenError, PgnError, UnsupportedVariantError
from .feature_model import (
    AbsolutePin,
    PieceDefense,
    PositionFeaturePacket,
    SquareAttackRelation,
)
from .features import build_position_features
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
    "AbsolutePin",
    "CanonicalGame",
    "CanonicalPosition",
    "ChessEvidenceError",
    "FenError",
    "MaterialSide",
    "MaterialSummary",
    "PgnError",
    "PgnIngestResult",
    "PieceDefense",
    "PieceGroup",
    "PositionContextPacket",
    "PositionFeaturePacket",
    "SourceProvenance",
    "SquareAttackRelation",
    "TimeControl",
    "UnsupportedVariantError",
    "build_position_context",
    "build_position_features",
    "canonical_json",
    "ingest_pgn",
]
