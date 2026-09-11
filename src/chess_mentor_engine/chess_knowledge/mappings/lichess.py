"""Compatibility helpers for Lichess puzzle-theme identifiers.

Lichess themes are an external vocabulary, not Chess Mentor Engine authority. A
single Lichess theme can map to multiple internal concepts when the external label is
broader than the ontology distinction.
"""

from __future__ import annotations

from ..model import ChessConcept, ExternalMapping
from ..registry import OntologyRegistry

LICHESS_MAPPING_NAMESPACE = "lichess.puzzle_theme"
LICHESS_SOURCE_SNAPSHOT_DATE = "2026-08-19"

# Themes intentionally covered by ontology.v1. This is not a claim that this tuple
# exhausts all Lichess metadata categories.
SUPPORTED_LICHESS_THEMES = (
    "anastasiaMate",
    "arabianMate",
    "attackingF2F7",
    "attraction",
    "backRankMate",
    "bodenMate",
    "capturingDefender",
    "clearance",
    "deflection",
    "discoveredAttack",
    "discoveredCheck",
    "doubleCheck",
    "dovetailMate",
    "fork",
    "hookMate",
    "interference",
    "intermezzo",
    "pin",
    "promotion",
    "quietMove",
    "sacrifice",
    "skewer",
    "smotheredMate",
    "trappedPiece",
    "underPromotion",
    "xRayAttack",
    "zugzwang",
)


def map_lichess_theme(
    theme: str, *, registry: OntologyRegistry | None = None
) -> tuple[tuple[ChessConcept, ExternalMapping], ...]:
    """Return explicit internal candidates for one external Lichess theme."""
    active = OntologyRegistry.load_default() if registry is None else registry
    return active.mappings_for(LICHESS_MAPPING_NAMESPACE, theme)


def unmapped_lichess_themes(
    themes: tuple[str, ...] | list[str], *, registry: OntologyRegistry | None = None
) -> tuple[str, ...]:
    active = OntologyRegistry.load_default() if registry is None else registry
    return tuple(
        sorted(
            theme
            for theme in set(themes)
            if not active.mappings_for(LICHESS_MAPPING_NAMESPACE, theme)
        )
    )
