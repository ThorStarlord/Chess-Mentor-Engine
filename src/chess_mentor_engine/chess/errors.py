"""Domain errors for the chess evidence substrate."""


class ChessEvidenceError(ValueError):
    """Base error for deterministic chess evidence failures."""


class FenError(ChessEvidenceError):
    """Raised when a FEN cannot be parsed as supported Standard chess."""


class PgnError(ChessEvidenceError):
    """Raised when a PGN source cannot be deterministically ingested."""


class UnsupportedVariantError(PgnError):
    """Raised when a PGN declares an unsupported chess variant."""
