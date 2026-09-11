"""Load and query the packaged Chess Knowledge Ontology."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from .fingerprints import concept_fingerprint, ontology_fingerprint
from .model import (
    ChessConcept,
    ConceptRelationship,
    ExternalMapping,
    OntologyDocument,
    PedagogyMetadata,
)
from .validation import OntologyValidationError, validate_ontology

ONTOLOGY_SCHEMA_VERSION = "chess-knowledge-ontology.v1"
DEFAULT_ONTOLOGY_RESOURCE = "data/ontology.v1.json"

_TOP_LEVEL_KEYS = frozenset({"schema_version", "content_version", "concepts"})
_CONCEPT_KEYS = frozenset(
    {
        "id",
        "kind",
        "preferred_name",
        "definition",
        "detection_support",
        "default_assertion_authority",
        "aliases",
        "parent_ids",
        "relationships",
        "external_mappings",
        "pedagogy",
        "deprecated",
    }
)
_RELATIONSHIP_KEYS = frozenset({"kind", "target_id", "note"})
_MAPPING_KEYS = frozenset({"namespace", "external_id", "relation"})
_PEDAGOGY_KEYS = frozenset(
    {
        "prerequisites",
        "recognition_questions",
        "common_misconceptions",
        "training_modes",
        "learner_band",
    }
)


class OntologyLoadError(ValueError):
    """Packaged ontology data is malformed or violates its declared schema."""


class OntologyRegistry:
    """Immutable query facade over one validated ontology document."""

    def __init__(self, document: OntologyDocument) -> None:
        validate_ontology(document)
        self._document = document
        self._by_id = {item.concept_id: item for item in document.concepts}
        aliases: dict[str, ChessConcept] = {}
        for concept in document.concepts:
            for value in (concept.preferred_name, *concept.aliases):
                aliases[value.casefold().strip()] = concept
        self._by_name = aliases

    @classmethod
    def load_default(cls) -> OntologyRegistry:
        resource = files("chess_mentor_engine.chess_knowledge").joinpath(
            DEFAULT_ONTOLOGY_RESOURCE
        )
        return cls.from_json_text(resource.read_text(encoding="utf-8"))

    @classmethod
    def from_json_text(cls, text: str) -> OntologyRegistry:
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise OntologyLoadError("ontology is not valid JSON") from exc
        return cls(_parse_document(raw))

    @property
    def schema_version(self) -> str:
        return self._document.schema_version

    @property
    def content_version(self) -> str:
        return self._document.content_version

    @property
    def fingerprint(self) -> str:
        return ontology_fingerprint(self._document)

    @property
    def concepts(self) -> tuple[ChessConcept, ...]:
        return self._document.concepts

    def get(self, concept_id: str) -> ChessConcept:
        try:
            return self._by_id[concept_id]
        except KeyError as exc:
            raise KeyError(f"unknown chess concept: {concept_id}") from exc

    def find_name(self, name_or_alias: str) -> ChessConcept:
        key = name_or_alias.casefold().strip()
        try:
            return self._by_name[key]
        except KeyError as exc:
            raise KeyError(f"unknown chess concept name: {name_or_alias}") from exc

    def children_of(self, concept_id: str) -> tuple[ChessConcept, ...]:
        self.get(concept_id)
        return tuple(
            item for item in self.concepts if concept_id in item.parent_ids
        )

    def mappings_for(
        self, namespace: str, external_id: str
    ) -> tuple[tuple[ChessConcept, ExternalMapping], ...]:
        matches: list[tuple[ChessConcept, ExternalMapping]] = []
        for concept in self.concepts:
            for mapping in concept.external_mappings:
                if (
                    mapping.namespace == namespace
                    and mapping.external_id == external_id
                ):
                    matches.append((concept, mapping))
        return tuple(matches)

    def concept_fingerprint(self, concept_id: str) -> str:
        return concept_fingerprint(self.get(concept_id))

    def to_dict(self) -> dict[str, Any]:
        return {
            **self._document.to_dict(),
            "ontology_fingerprint": self.fingerprint,
        }


def _expect_dict(value: object, name: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise OntologyLoadError(f"{name} must be an object")
    return value


def _expect_list(value: object, name: str) -> list[Any]:
    if type(value) is not list:
        raise OntologyLoadError(f"{name} must be an array")
    return value


def _strict_keys(value: dict[str, Any], allowed: frozenset[str], name: str) -> None:
    unexpected = set(value) - allowed
    if unexpected:
        raise OntologyLoadError(
            f"{name} contains unexpected keys: {sorted(unexpected)!r}"
        )


def _strings(value: object, name: str) -> tuple[str, ...]:
    items = _expect_list(value, name)
    if any(type(item) is not str for item in items):
        raise OntologyLoadError(f"{name} must contain only strings")
    return tuple(items)


def _parse_document(raw: object) -> OntologyDocument:
    payload = _expect_dict(raw, "ontology")
    _strict_keys(payload, _TOP_LEVEL_KEYS, "ontology")
    if set(payload) != _TOP_LEVEL_KEYS:
        raise OntologyLoadError("ontology top-level shape mismatch")
    if payload["schema_version"] != ONTOLOGY_SCHEMA_VERSION:
        raise OntologyLoadError("unsupported ontology schema version")
    if type(payload["content_version"]) is not str:
        raise OntologyLoadError("content_version must be a string")
    concepts = tuple(
        _parse_concept(item, index)
        for index, item in enumerate(_expect_list(payload["concepts"], "concepts"))
    )
    try:
        document = OntologyDocument(
            schema_version=payload["schema_version"],
            content_version=payload["content_version"],
            concepts=concepts,
        )
        validate_ontology(document)
    except (ValueError, OntologyValidationError) as exc:
        raise OntologyLoadError(f"invalid ontology: {exc}") from exc
    return document


def _parse_concept(raw: object, index: int) -> ChessConcept:
    payload = _expect_dict(raw, f"concepts[{index}]")
    _strict_keys(payload, _CONCEPT_KEYS, f"concepts[{index}]")
    required = {
        "id",
        "kind",
        "preferred_name",
        "definition",
        "detection_support",
        "default_assertion_authority",
    }
    if not required.issubset(payload):
        missing = sorted(required - set(payload))
        raise OntologyLoadError(f"concepts[{index}] missing keys: {missing!r}")
    try:
        relationships = tuple(
            _parse_relationship(item, index, rel_index)
            for rel_index, item in enumerate(payload.get("relationships", []))
        )
        mappings = tuple(
            _parse_mapping(item, index, mapping_index)
            for mapping_index, item in enumerate(payload.get("external_mappings", []))
        )
        pedagogy_raw = payload.get("pedagogy")
        pedagogy = (
            None
            if pedagogy_raw is None
            else _parse_pedagogy(pedagogy_raw, index)
        )
        if type(payload.get("deprecated", False)) is not bool:
            raise OntologyLoadError(f"concepts[{index}].deprecated must be boolean")
        return ChessConcept(
            concept_id=payload["id"],
            kind=payload["kind"],
            preferred_name=payload["preferred_name"],
            definition=payload["definition"],
            detection_support=payload["detection_support"],
            default_assertion_authority=payload["default_assertion_authority"],
            aliases=_strings(payload.get("aliases", []), f"concepts[{index}].aliases"),
            parent_ids=_strings(
                payload.get("parent_ids", []), f"concepts[{index}].parent_ids"
            ),
            relationships=relationships,
            external_mappings=mappings,
            pedagogy=pedagogy,
            deprecated=payload.get("deprecated", False),
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, OntologyLoadError):
            raise
        raise OntologyLoadError(f"invalid concepts[{index}]: {exc}") from exc


def _parse_relationship(raw: object, concept_index: int, relation_index: int):
    payload = _expect_dict(
        raw, f"concepts[{concept_index}].relationships[{relation_index}]"
    )
    _strict_keys(payload, _RELATIONSHIP_KEYS, "relationship")
    if not {"kind", "target_id"}.issubset(payload):
        raise OntologyLoadError("relationship missing required keys")
    return ConceptRelationship(
        kind=payload["kind"], target_id=payload["target_id"], note=payload.get("note")
    )


def _parse_mapping(raw: object, concept_index: int, mapping_index: int):
    payload = _expect_dict(
        raw, f"concepts[{concept_index}].external_mappings[{mapping_index}]"
    )
    _strict_keys(payload, _MAPPING_KEYS, "external mapping")
    if not {"namespace", "external_id"}.issubset(payload):
        raise OntologyLoadError("external mapping missing required keys")
    return ExternalMapping(
        namespace=payload["namespace"],
        external_id=payload["external_id"],
        relation=payload.get("relation", "exact"),
    )


def _parse_pedagogy(raw: object, concept_index: int) -> PedagogyMetadata:
    payload = _expect_dict(raw, f"concepts[{concept_index}].pedagogy")
    _strict_keys(payload, _PEDAGOGY_KEYS, "pedagogy")
    return PedagogyMetadata(
        prerequisites=_strings(payload.get("prerequisites", []), "prerequisites"),
        recognition_questions=_strings(
            payload.get("recognition_questions", []), "recognition_questions"
        ),
        common_misconceptions=_strings(
            payload.get("common_misconceptions", []), "common_misconceptions"
        ),
        training_modes=_strings(payload.get("training_modes", []), "training_modes"),
        learner_band=payload.get("learner_band"),
    )
