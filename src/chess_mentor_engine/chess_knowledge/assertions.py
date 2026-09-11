"""Provenance-bound position and move assertions over ontology concepts.

A KnowledgeAssertion says that a registered concept applies (or does not apply) to a
bounded chess subject under a stated authority. It is not participant evidence and
cannot itself establish a learner hypothesis.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json

from .model import AuthorityClass, ChessConcept
from .registry import OntologyRegistry

KNOWLEDGE_ASSERTION_SCHEMA_VERSION = "chess-knowledge-assertion.v1"
KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION = "chess-knowledge-assertion-bundle.v1"

KnowledgeSubjectKind: TypeAlias = Literal[
    "position",
    "move",
    "move_sequence",
    "position_comparison",
]
KnowledgeAssertionStatus: TypeAlias = Literal[
    "present",
    "absent",
    "supported",
    "plausible",
    "unclear",
]
KnowledgeEvidenceKind: TypeAlias = Literal[
    "canonical_position",
    "position_features",
    "engine_analysis",
    "move_sequence",
    "external_tag",
    "human_review",
    "model_output",
]
KnowledgeSourceKind: TypeAlias = Literal[
    "detector",
    "engine",
    "external",
    "model",
    "human",
    "system",
]

_SUBJECT_KINDS = frozenset(
    {"position", "move", "move_sequence", "position_comparison"}
)
_ASSERTION_STATUSES = frozenset(
    {"present", "absent", "supported", "plausible", "unclear"}
)
_EVIDENCE_KINDS = frozenset(
    {
        "canonical_position",
        "position_features",
        "engine_analysis",
        "move_sequence",
        "external_tag",
        "human_review",
        "model_output",
    }
)
_SOURCE_KINDS = frozenset(
    {"detector", "engine", "external", "model", "human", "system"}
)
_DETERMINISTIC_AUTHORITIES = frozenset(
    {
        "rule_derived",
        "deterministic_position_fact",
        "deterministic_sequence_pattern",
    }
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_nonempty(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_sha256(name: str, value: str) -> None:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")


def _require_aware_timestamp(name: str, value: str) -> None:
    _require_nonempty(name, value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone offset")


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class KnowledgeQualifier:
    name: str
    value: str

    def __post_init__(self) -> None:
        _require_nonempty("qualifier name", self.name)
        _require_nonempty("qualifier value", self.value)

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "value": self.value}


@dataclass(frozen=True, slots=True)
class KnowledgeSubject:
    subject_kind: KnowledgeSubjectKind
    position_id: str
    game_id: str | None = None
    ply_index: int | None = None
    move_uci: str | None = None
    move_sequence: tuple[str, ...] = ()
    comparison_position_id: str | None = None

    def __post_init__(self) -> None:
        if self.subject_kind not in _SUBJECT_KINDS:
            raise ValueError("unknown knowledge subject kind")
        _require_nonempty("position_id", self.position_id)
        if self.game_id is not None:
            _require_nonempty("game_id", self.game_id)
        if self.ply_index is not None and self.ply_index < 0:
            raise ValueError("ply_index must be non-negative")
        if self.move_uci is not None:
            _require_nonempty("move_uci", self.move_uci)
        if any(not move or not move.strip() for move in self.move_sequence):
            raise ValueError("move_sequence values must not be empty")
        if self.comparison_position_id is not None:
            _require_nonempty("comparison_position_id", self.comparison_position_id)

        if self.subject_kind == "position":
            if self.move_uci is not None or self.move_sequence:
                raise ValueError("position subject cannot carry move data")
            if self.comparison_position_id is not None:
                raise ValueError("position subject cannot carry comparison position")
        elif self.subject_kind == "move":
            if self.move_uci is None:
                raise ValueError("move subject requires move_uci")
            if self.move_sequence:
                raise ValueError("move subject cannot carry move_sequence")
            if self.comparison_position_id is not None:
                raise ValueError("move subject cannot carry comparison position")
        elif self.subject_kind == "move_sequence":
            if not self.move_sequence:
                raise ValueError("move_sequence subject requires at least one move")
            if self.move_uci is not None:
                raise ValueError("move_sequence subject cannot carry move_uci")
            if self.comparison_position_id is not None:
                raise ValueError(
                    "move_sequence subject cannot carry comparison position"
                )
        elif self.subject_kind == "position_comparison":
            if self.comparison_position_id is None:
                raise ValueError(
                    "position_comparison subject requires comparison_position_id"
                )
            if self.move_uci is not None or self.move_sequence:
                raise ValueError("position_comparison subject cannot carry move data")

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_kind": self.subject_kind,
            "position_id": self.position_id,
            "game_id": self.game_id,
            "ply_index": self.ply_index,
            "move_uci": self.move_uci,
            "move_sequence": list(self.move_sequence),
            "comparison_position_id": self.comparison_position_id,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeEvidenceRef:
    kind: KnowledgeEvidenceKind
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        if self.kind not in _EVIDENCE_KINDS:
            raise ValueError("unknown knowledge evidence kind")
        _require_nonempty("evidence ref_id", self.ref_id)
        _require_sha256("evidence fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeProvenance:
    source_kind: KnowledgeSourceKind
    source_id: str
    source_version: str
    source_fingerprint: str
    run_id: str | None = None

    def __post_init__(self) -> None:
        if self.source_kind not in _SOURCE_KINDS:
            raise ValueError("unknown knowledge provenance source kind")
        _require_nonempty("source_id", self.source_id)
        _require_nonempty("source_version", self.source_version)
        _require_sha256("source_fingerprint", self.source_fingerprint)
        if self.run_id is not None:
            _require_nonempty("run_id", self.run_id)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "source_kind": self.source_kind,
            "source_id": self.source_id,
            "source_version": self.source_version,
            "source_fingerprint": self.source_fingerprint,
            "run_id": self.run_id,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeAssertion:
    assertion_id: str
    fingerprint: str
    concept_id: str
    concept_fingerprint: str
    ontology_fingerprint: str
    subject: KnowledgeSubject
    status: KnowledgeAssertionStatus
    authority_class: AuthorityClass
    qualifiers: tuple[KnowledgeQualifier, ...]
    evidence_refs: tuple[KnowledgeEvidenceRef, ...]
    provenance: KnowledgeProvenance
    claim_scope: str
    created_at: str
    schema_version: str = KNOWLEDGE_ASSERTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_nonempty("assertion_id", self.assertion_id)
        _require_sha256("assertion fingerprint", self.fingerprint)
        _require_nonempty("concept_id", self.concept_id)
        _require_sha256("concept_fingerprint", self.concept_fingerprint)
        _require_sha256("ontology_fingerprint", self.ontology_fingerprint)
        if self.status not in _ASSERTION_STATUSES:
            raise ValueError("unknown knowledge assertion status")
        names = tuple(item.name for item in self.qualifiers)
        if len(set(names)) != len(names):
            raise ValueError("knowledge qualifier names must be unique")
        if not self.evidence_refs:
            raise ValueError("knowledge assertion requires at least one evidence ref")
        ref_keys = tuple(
            (item.kind, item.ref_id, item.fingerprint) for item in self.evidence_refs
        )
        if len(set(ref_keys)) != len(ref_keys):
            raise ValueError("knowledge evidence refs must be unique")
        _require_nonempty("claim_scope", self.claim_scope)
        _require_aware_timestamp("created_at", self.created_at)
        if self.schema_version != KNOWLEDGE_ASSERTION_SCHEMA_VERSION:
            raise ValueError("unsupported knowledge assertion schema version")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "concept_id": self.concept_id,
            "concept_fingerprint": self.concept_fingerprint,
            "ontology_fingerprint": self.ontology_fingerprint,
            "subject": self.subject.to_dict(),
            "status": self.status,
            "authority_class": self.authority_class,
            "qualifiers": [item.to_dict() for item in self.qualifiers],
            "evidence_refs": [item.to_dict() for item in self.evidence_refs],
            "provenance": self.provenance.to_dict(),
            "claim_scope": self.claim_scope,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "assertion_id": self.assertion_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class KnowledgeAssertionRef:
    assertion_id: str
    fingerprint: str
    concept_id: str
    concept_fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("assertion_id", self.assertion_id)
        _require_sha256("assertion fingerprint", self.fingerprint)
        _require_nonempty("concept_id", self.concept_id)
        _require_sha256("concept_fingerprint", self.concept_fingerprint)

    @classmethod
    def from_assertion(cls, assertion: KnowledgeAssertion) -> KnowledgeAssertionRef:
        return cls(
            assertion_id=assertion.assertion_id,
            fingerprint=assertion.fingerprint,
            concept_id=assertion.concept_id,
            concept_fingerprint=assertion.concept_fingerprint,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "assertion_id": self.assertion_id,
            "fingerprint": self.fingerprint,
            "concept_id": self.concept_id,
            "concept_fingerprint": self.concept_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeAssertionBundle:
    bundle_id: str
    fingerprint: str
    ontology_version: str
    ontology_fingerprint: str
    subject: KnowledgeSubject
    assertions: tuple[KnowledgeAssertion, ...]
    claim_scope: str
    created_at: str
    schema_version: str = KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_nonempty("bundle_id", self.bundle_id)
        _require_sha256("bundle fingerprint", self.fingerprint)
        _require_nonempty("ontology_version", self.ontology_version)
        _require_sha256("ontology_fingerprint", self.ontology_fingerprint)
        if not self.assertions:
            raise ValueError("knowledge assertion bundle must not be empty")
        ids = tuple(item.assertion_id for item in self.assertions)
        if len(set(ids)) != len(ids):
            raise ValueError("knowledge assertion bundle IDs must be unique")
        _require_nonempty("claim_scope", self.claim_scope)
        _require_aware_timestamp("created_at", self.created_at)
        if self.schema_version != KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION:
            raise ValueError("unsupported assertion-bundle schema version")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ontology_version": self.ontology_version,
            "ontology_fingerprint": self.ontology_fingerprint,
            "subject": self.subject.to_dict(),
            "assertions": [
                KnowledgeAssertionRef.from_assertion(item).to_dict()
                for item in self.assertions
            ],
            "claim_scope": self.claim_scope,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
            "assertion_records": [item.to_dict() for item in self.assertions],
        }


def build_knowledge_assertion(
    *,
    concept_id: str,
    subject: KnowledgeSubject,
    status: KnowledgeAssertionStatus,
    authority_class: AuthorityClass,
    evidence_refs: tuple[KnowledgeEvidenceRef, ...],
    provenance: KnowledgeProvenance,
    claim_scope: str,
    created_at: str,
    qualifiers: tuple[KnowledgeQualifier, ...] = (),
    registry: OntologyRegistry | None = None,
) -> KnowledgeAssertion:
    active = OntologyRegistry.load_default() if registry is None else registry
    concept = active.get(concept_id)
    _validate_assertion_semantics(
        concept=concept,
        status=status,
        authority_class=authority_class,
        provenance=provenance,
    )
    draft = {
        "schema_version": KNOWLEDGE_ASSERTION_SCHEMA_VERSION,
        "concept_id": concept_id,
        "concept_fingerprint": active.concept_fingerprint(concept_id),
        "ontology_fingerprint": active.fingerprint,
        "subject": subject.to_dict(),
        "status": status,
        "authority_class": authority_class,
        "qualifiers": [item.to_dict() for item in qualifiers],
        "evidence_refs": [item.to_dict() for item in evidence_refs],
        "provenance": provenance.to_dict(),
        "claim_scope": claim_scope,
        "created_at": created_at,
    }
    fingerprint = _digest(draft)
    assertion = KnowledgeAssertion(
        assertion_id=f"cka_{fingerprint[:24]}",
        fingerprint=fingerprint,
        concept_id=concept_id,
        concept_fingerprint=active.concept_fingerprint(concept_id),
        ontology_fingerprint=active.fingerprint,
        subject=subject,
        status=status,
        authority_class=authority_class,
        qualifiers=qualifiers,
        evidence_refs=evidence_refs,
        provenance=provenance,
        claim_scope=claim_scope,
        created_at=created_at,
    )
    validate_knowledge_assertion(assertion, registry=active)
    return assertion


def validate_knowledge_assertion(
    assertion: KnowledgeAssertion, *, registry: OntologyRegistry | None = None
) -> None:
    active = OntologyRegistry.load_default() if registry is None else registry
    concept = active.get(assertion.concept_id)
    if assertion.concept_fingerprint != active.concept_fingerprint(concept.concept_id):
        raise ValueError("knowledge assertion concept fingerprint mismatch")
    if assertion.ontology_fingerprint != active.fingerprint:
        raise ValueError("knowledge assertion ontology fingerprint mismatch")
    _validate_assertion_semantics(
        concept=concept,
        status=assertion.status,
        authority_class=assertion.authority_class,
        provenance=assertion.provenance,
    )
    expected = _digest(assertion.identity_payload())
    if assertion.fingerprint != expected:
        raise ValueError("knowledge assertion fingerprint mismatch")
    if assertion.assertion_id != f"cka_{expected[:24]}":
        raise ValueError("knowledge assertion ID mismatch")


def build_assertion_bundle(
    *,
    subject: KnowledgeSubject,
    assertions: tuple[KnowledgeAssertion, ...],
    claim_scope: str,
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> KnowledgeAssertionBundle:
    active = OntologyRegistry.load_default() if registry is None else registry
    for assertion in assertions:
        validate_knowledge_assertion(assertion, registry=active)
        if assertion.subject != subject:
            raise ValueError("bundle assertions must share the exact bundle subject")
    draft = {
        "schema_version": KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION,
        "ontology_version": active.content_version,
        "ontology_fingerprint": active.fingerprint,
        "subject": subject.to_dict(),
        "assertions": [
            KnowledgeAssertionRef.from_assertion(item).to_dict()
            for item in assertions
        ],
        "claim_scope": claim_scope,
        "created_at": created_at,
    }
    fingerprint = _digest(draft)
    bundle = KnowledgeAssertionBundle(
        bundle_id=f"ckb_{fingerprint[:24]}",
        fingerprint=fingerprint,
        ontology_version=active.content_version,
        ontology_fingerprint=active.fingerprint,
        subject=subject,
        assertions=assertions,
        claim_scope=claim_scope,
        created_at=created_at,
    )
    validate_assertion_bundle(bundle, registry=active)
    return bundle


def validate_assertion_bundle(
    bundle: KnowledgeAssertionBundle, *, registry: OntologyRegistry | None = None
) -> None:
    active = OntologyRegistry.load_default() if registry is None else registry
    if bundle.ontology_version != active.content_version:
        raise ValueError("assertion bundle ontology version mismatch")
    if bundle.ontology_fingerprint != active.fingerprint:
        raise ValueError("assertion bundle ontology fingerprint mismatch")
    for assertion in bundle.assertions:
        validate_knowledge_assertion(assertion, registry=active)
        if assertion.subject != bundle.subject:
            raise ValueError("assertion bundle subject mismatch")
    expected = _digest(bundle.identity_payload())
    if bundle.fingerprint != expected:
        raise ValueError("assertion bundle fingerprint mismatch")
    if bundle.bundle_id != f"ckb_{expected[:24]}":
        raise ValueError("assertion bundle ID mismatch")


def _validate_assertion_semantics(
    *,
    concept: ChessConcept,
    status: KnowledgeAssertionStatus,
    authority_class: AuthorityClass,
    provenance: KnowledgeProvenance,
) -> None:
    if concept.kind == "concept_group":
        raise ValueError("concept groups cannot be asserted against chess subjects")
    if authority_class in _DETERMINISTIC_AUTHORITIES and status not in {
        "present",
        "absent",
    }:
        raise ValueError("deterministic assertions must use present or absent status")

    if provenance.source_kind == "detector":
        if authority_class != concept.default_assertion_authority:
            raise ValueError("detector assertion exceeds or changes concept authority")
    elif provenance.source_kind == "engine":
        if authority_class != "engine_derived":
            raise ValueError("engine provenance requires engine-derived authority")
    elif provenance.source_kind == "external":
        if authority_class != "external_taxonomy_tag":
            raise ValueError("external provenance requires external-taxonomy authority")
    elif provenance.source_kind == "model":
        if authority_class != "model_interpretation":
            raise ValueError("model provenance requires model-interpretation authority")
    elif provenance.source_kind == "human":
        if authority_class != "human_ratified":
            raise ValueError("human provenance requires human-ratified authority")
    elif provenance.source_kind == "system":
        if authority_class not in _DETERMINISTIC_AUTHORITIES:
            raise ValueError(
                "system provenance is restricted to deterministic authority"
            )
