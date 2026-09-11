"""External chess-knowledge vocabulary mappings."""

from .lichess import (
    LICHESS_MAPPING_NAMESPACE,
    LICHESS_SOURCE_SNAPSHOT_DATE,
    SUPPORTED_LICHESS_THEMES,
    map_lichess_theme,
    unmapped_lichess_themes,
)

__all__ = [
    "LICHESS_MAPPING_NAMESPACE",
    "LICHESS_SOURCE_SNAPSHOT_DATE",
    "SUPPORTED_LICHESS_THEMES",
    "map_lichess_theme",
    "unmapped_lichess_themes",
]
