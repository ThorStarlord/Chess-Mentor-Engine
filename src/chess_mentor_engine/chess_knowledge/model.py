"""Versioned chess-knowledge ontology definitions.

Concept definitions describe vocabulary only. Position-specific claims belong to the
assertion layer and learner claims remain under the existing learning authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

ConceptKind: TypeAlias = Literal[
    "concept_group",
    "rule_fact",
    "position_feature",
    "tactical_motif",
    "mating_pattern",
    "defensive_resource",
    "strategic_principle",
    "evaluation_factor",
    "plan",
    "pedagogical_concept",
]
DetectionSupport: TypeAlias = Literal[
    "none",
    "deterministic",
    "sequence_based",
    "heuristic",
    "external_only",
]
AuthorityClass: TypeAlias = Literal[
    "rule_derived",
    "deterministic_position_fact",
    "deterministic_sequence_pattern",
    "engine_derived",
    "heuristic_assessment",
    "model_interpretation",
    "human_ratified",
]
RelationshipKind: TypeAlias = Literal[
    "related_to",
    "requires",
    "enables",
    "exploits",
    "prevents",
    "supports",
    "commonly_conflicts_with",
    "overrides_under_condition",
    "is_evidence_for",
    "is_not_sufficient_for",
]
ExternalMappingRelation: TypeAlias = Literal[
    "exact",
    "broader",
    "narrower",
    "related",
]

_CONCEPT_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_CONCEPT_KINDS = frozenset(
    {
        "concept_group",
        "rule_fact",
        "position_feature",
        "tactical_motif",
        "mating_pattern",
        "defensive_resource",
        "strategic_principle",
        "evaluation_factor",
        "plan",
        "pedagogical_concept",
    }
)
_DETECTION_SUPPORT = frozenset(
    {"none", "deterministic", "sequence_based", "heuristic", "external_only"}
)
_AUTHORITY_CLASSES = frozenset(
    {
        "rule_derived",
        "deterministic_position_fact",
        "deterministic_sequence_pattern",
        "engine_derived",
        "heuristic_assessment",
        "model_interpretation",
        "human_ratified",
    }
)
_RELATIONSHIP_KINDS = frozenset(
    {
        "related_to",
        "requires",
        "enables",
        "exploits",
        "prevents",
        "supports",
        "commonly_conflicts_with",
        "overrides_under_condition",
        "is_evidence_for",
        "is_not_sufficient_for",
    }
)
_EXTERNAL_RELATIONS = frozenset({"exact", "broader", "narrower", "related"})


def _require_nonempty(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_unique(name: str, values: tuple[str, ...]) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")
    if any(not value or not value.strip() for value in values):
        raise ValueError(f"{name} values must not be empty")


@dataclass(frozen=True, slots=True)
class ConceptRelationship:
    kind: RelationshipKind
    target_id: str
    note: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in _RELATIONSHIP_KINDS:
            raise ValueError("unknown chess-knowledge relationship kind")
        if not _CONCEPT_ID_RE.fullmatch(self.target_id):
            raise ValueError("invalid relationship target concept ID")
        if self.note is not None:
            _require_nonempty("relationship note", self.note)

    def to_dict(self) -> dict[str, str]:
        payload = {"kind": self.kind, "target_id": self.target_id}
        if self.note is not None:
            payload["note"] = self.note
        return payload


@dataclass(frozen=True, slots=True)
class ExternalMapping:
    namespace: str
    external_id: str
    relation: ExternalMappingRelation = "exact"

    def __post_init__(self) -> None:
        _require_nonempty("mapping namespace", self.namespace)
        _require_nonempty("mapping external_id", self.external_id)
        if self.relation not in _EXTERNAL_RELATIONS:
            raise ValueError("unknown external mapping relation")

    def to_dict(self) -> dict[str, str]:
        return {
            "namespace": self.namespace,
            "external_id": self.external_id,
            "relation": self.relation,
        }


@dataclass(frozen=True, slots=True)
class PedagogyMetadata:
    prerequisites: tuple[str, ...] = ()
    recognition_questions: tuple[str, ...] = ()
    common_misconceptions: tuple[str, ...] = ()
    training_modes: tuple[str, ...] = ()
    learner_band: str | None = None

    def __post_init__(self) -> None:
        for name, values in (
            ("prerequisites", self.prerequisites),
            ("recognition_questions", self.recognition_questions),
            ("common_misconceptions", self.common_misconceptions),
            ("training_modes", self.training_modes),
        ):
            _require_unique(name, values)
        if self.learner_band is not None:
            _require_nonempty("learner_band", self.learner_band)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prerequisites": list(self.prerequisites),
            "recognition_questions": list(self.recognition_questions),
            "common_misconceptions": list(self.common_misconceptions),
            "training_modes": list(self.training_modes),
            "learner_band": self.learner_band,
        }


@dataclass(frozen=True, slots=True)
class ChessConcept:
    concept_id: str
    kind: ConceptKind
    preferred_name: str
    definition: str
    detection_support: DetectionSupport
    default_assertion_authority: AuthorityClass
    aliases: tuple[str, ...] = ()
    parent_ids: tuple[str, ...] = ()
    relationships: tuple[ConceptRelationship, ...] = ()
    external_mappings: tuple[ExternalMapping, ...] = ()
    pedagogy: PedagogyMetadata | None = None
    deprecated: bool = False

    def __post_init__(self) -> None:
        if not _CONCEPT_ID_RE.fullmatch(self.concept_id):
            raise ValueError(f"invalid chess concept ID: {self.concept_id!r}")
        if self.kind not in _CONCEPT_KINDS:
            raise ValueError("unknown chess concept kind")
        if self.detection_support not in _DETECTION_SUPPORT:
            raise ValueError("unknown detection support")
        if self.default_assertion_authority not in _AUTHORITY_CLASSES:
            raise ValueError("unknown default assertion authority")
        _require_nonempty("preferred_name", self.preferred_name)
        _require_nonempty("definition", self.definition)
        _require_unique("aliases", self.aliases)
        _require_unique("parent_ids", self.parent_ids)
        if self.concept_id in self.parent_ids:
            raise ValueError("concept cannot be its own parent")
        relation_keys = tuple(
            (item.kind, item.target_id) for item in self.relationships
        )
        if len(set(relation_keys)) != len(relation_keys):
            raise ValueError("concept relationships must be unique")
        mapping_keys = tuple(
            (item.namespace, item.external_id, item.relation)
            for item in self.external_mappings
        )
        if len(set(mapping_keys)) != len(mapping_keys):
            raise ValueError("external mappings must be unique")
        if (
            self.detection_support == "deterministic"
            and self.default_assertion_authority
            not in {
                "rule_derived",
                "deterministic_position_fact",
            }
        ):
            raise ValueError("deterministic concepts require deterministic authority")
        if (
            self.detection_support == "sequence_based"
            and self.default_assertion_authority != "deterministic_sequence_pattern"
        ):
            raise ValueError(
                "sequence-based concepts require sequence-pattern authority"
            )
        if (
            self.detection_support == "heuristic"
            and self.default_assertion_authority
            not in {"heuristic_assessment", "model_interpretation", "human_ratified"}
        ):
            raise ValueError("heuristic concepts require non-deterministic authority")

    @property
    def id(self) -> str:
        return self.concept_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.concept_id,
            "kind": self.kind,
            "preferred_name": self.preferred_name,
            "definition": self.definition,
            "detection_support": self.detection_support,
            "default_assertion_authority": self.default_assertion_authority,
            "aliases": list(self.aliases),
            "parent_ids": list(self.parent_ids),
            "relationships": [item.to_dict() for item in self.relationships],
            "external_mappings": [item.to_dict() for item in self.external_mappings],
            "pedagogy": None if self.pedagogy is None else self.pedagogy.to_dict(),
            "deprecated": self.deprecated,
        }


@dataclass(frozen=True, slots=True)
class OntologyDocument:
    schema_version: str
    content_version: str
    concepts: tuple[ChessConcept, ...]

    def __post_init__(self) -> None:
        _require_nonempty("schema_version", self.schema_version)
        _require_nonempty("content_version", self.content_version)
        if not self.concepts:
            raise ValueError("ontology must contain at least one concept")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "content_version": self.content_version,
            "concepts": [item.to_dict() for item in self.concepts],
        }
