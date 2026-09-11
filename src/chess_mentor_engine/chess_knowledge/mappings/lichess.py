"""Compatibility helpers for Lichess puzzle-theme identifiers.

Lichess themes are an external vocabulary, not Chess Mentor Engine authority. A
single Lichess theme can map to multiple internal concepts when the external label is
broader than the ontology distinction.
"""

from __future__ import annotations

from ..assertions import (
    KnowledgeAssertion,
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeQualifier,
    KnowledgeSubject,
    build_knowledge_assertion,
)
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


def build_lichess_theme_assertions(
    *,
    theme: str,
    subject: KnowledgeSubject,
    external_source_fingerprint: str,
    created_at: str,
    source_version: str = LICHESS_SOURCE_SNAPSHOT_DATE,
    registry: OntologyRegistry | None = None,
) -> tuple[KnowledgeAssertion, ...]:
    """Project one external theme into provenance-bound, non-CME-authoritative claims.

    An exact crosswalk is represented as ``supported`` and a broader/narrower/related
    mapping as ``plausible``. In both cases the authority remains
    ``external_taxonomy_tag``; this helper never upgrades an external label into a CME
    detector result.
    """
    active = OntologyRegistry.load_default() if registry is None else registry
    matches = map_lichess_theme(theme, registry=active)
    if not matches:
        raise ValueError(f"unmapped Lichess puzzle theme: {theme}")
    evidence = KnowledgeEvidenceRef(
        kind="external_tag",
        ref_id=f"lichess-theme:{theme}",
        fingerprint=external_source_fingerprint,
    )
    provenance = KnowledgeProvenance(
        source_kind="external",
        source_id=LICHESS_MAPPING_NAMESPACE,
        source_version=source_version,
        source_fingerprint=external_source_fingerprint,
    )
    return tuple(
        build_knowledge_assertion(
            concept_id=concept.concept_id,
            subject=subject,
            status="supported" if mapping.relation == "exact" else "plausible",
            authority_class="external_taxonomy_tag",
            evidence_refs=(evidence,),
            provenance=provenance,
            qualifiers=(
                KnowledgeQualifier(name="external_theme", value=theme),
                KnowledgeQualifier(name="mapping_relation", value=mapping.relation),
            ),
            claim_scope=(
                "external taxonomy projection only; not a CME detector result, "
                "participant observation, or learner inference"
            ),
            created_at=created_at,
            registry=active,
        )
        for concept, mapping in matches
    )
