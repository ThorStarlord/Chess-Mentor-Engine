"""Authority-preserving chess-knowledge projection for model-coaching consumers.

The projection is a sidecar to M19. It validates and references an existing M19
request without adding keys to or changing the fingerprint of that request.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching.model import _validate_request_identity

from .assertions import (
    KnowledgeAssertionBundle,
    KnowledgeAssertionRef,
    KnowledgeQualifier,
    KnowledgeSubject,
    validate_assertion_bundle,
)
from .model import AuthorityClass, ConceptKind
from .registry import OntologyRegistry

KNOWLEDGE_COACHING_CONTEXT_SCHEMA_VERSION = "chess-knowledge-coaching-context.v1"
KNOWLEDGE_MODEL_BINDING_SCHEMA_VERSION = "chess-knowledge-model-binding.v1"

KNOWLEDGE_MODEL_INSTRUCTIONS = (
    "Treat deterministic assertions as established only within their exact "
    "subject and claim scope.",
    "Describe heuristic, external-taxonomy, model, and human assertions according "
    "to their stated authority; do not promote them to objective chess facts.",
    "Do not infer participant reasoning or a learner weakness from a chess concept "
    "assertion alone.",
    "Do not invent ontology assertions that are absent from this context.",
    "Use registered concept definitions and relationships to explain supplied "
    "evidence while preserving M16 as the deterministic mentor-grounding ceiling.",
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_nonempty(name: str, value: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _require_timestamp(name: str, value: str) -> None:
    _require_nonempty(name, value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone offset")


@dataclass(frozen=True, slots=True)
class KnowledgeContextAssertion:
    assertion_ref: KnowledgeAssertionRef
    preferred_name: str
    kind: ConceptKind
    definition: str
    status: str
    authority_class: AuthorityClass
    qualifiers: tuple[KnowledgeQualifier, ...]
    related_concept_ids: tuple[str, ...]
    recognition_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_nonempty("preferred_name", self.preferred_name)
        _require_nonempty("definition", self.definition)
        _require_nonempty("status", self.status)
        if len(set(self.related_concept_ids)) != len(self.related_concept_ids):
            raise ValueError("related concept IDs must be unique")
        if len(set(self.recognition_questions)) != len(self.recognition_questions):
            raise ValueError("recognition questions must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "assertion_ref": self.assertion_ref.to_dict(),
            "preferred_name": self.preferred_name,
            "kind": self.kind,
            "definition": self.definition,
            "status": self.status,
            "authority_class": self.authority_class,
            "qualifiers": [item.to_dict() for item in self.qualifiers],
            "related_concept_ids": list(self.related_concept_ids),
            "recognition_questions": list(self.recognition_questions),
        }


@dataclass(frozen=True, slots=True)
class KnowledgeCoachingContext:
    context_id: str
    fingerprint: str
    ontology_version: str
    ontology_fingerprint: str
    subject: KnowledgeSubject
    assertion_bundle_id: str
    assertion_bundle_fingerprint: str
    assertions: tuple[KnowledgeContextAssertion, ...]
    model_instructions: tuple[str, ...]
    claim_scope: str
    created_at: str
    schema_version: str = KNOWLEDGE_COACHING_CONTEXT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_nonempty("context_id", self.context_id)
        _require_nonempty("fingerprint", self.fingerprint)
        _require_nonempty("ontology_version", self.ontology_version)
        _require_nonempty("ontology_fingerprint", self.ontology_fingerprint)
        _require_nonempty("assertion_bundle_id", self.assertion_bundle_id)
        _require_nonempty(
            "assertion_bundle_fingerprint", self.assertion_bundle_fingerprint
        )
        if not self.assertions:
            raise ValueError("knowledge coaching context must contain assertions")
        if not self.model_instructions:
            raise ValueError("knowledge coaching context must contain instructions")
        _require_nonempty("claim_scope", self.claim_scope)
        _require_timestamp("created_at", self.created_at)
        if self.schema_version != KNOWLEDGE_COACHING_CONTEXT_SCHEMA_VERSION:
            raise ValueError("unsupported knowledge coaching context schema")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ontology_version": self.ontology_version,
            "ontology_fingerprint": self.ontology_fingerprint,
            "subject": self.subject.to_dict(),
            "assertion_bundle_id": self.assertion_bundle_id,
            "assertion_bundle_fingerprint": self.assertion_bundle_fingerprint,
            "assertions": [item.to_dict() for item in self.assertions],
            "model_instructions": list(self.model_instructions),
            "claim_scope": self.claim_scope,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class KnowledgeModelBinding:
    binding_id: str
    fingerprint: str
    model_request_id: str
    model_request_fingerprint: str
    knowledge_context_id: str
    knowledge_context_fingerprint: str
    claim_scope: str
    created_at: str
    schema_version: str = KNOWLEDGE_MODEL_BINDING_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("binding_id", self.binding_id),
            ("fingerprint", self.fingerprint),
            ("model_request_id", self.model_request_id),
            ("model_request_fingerprint", self.model_request_fingerprint),
            ("knowledge_context_id", self.knowledge_context_id),
            ("knowledge_context_fingerprint", self.knowledge_context_fingerprint),
            ("claim_scope", self.claim_scope),
        ):
            _require_nonempty(name, value)
        _require_timestamp("created_at", self.created_at)
        if self.schema_version != KNOWLEDGE_MODEL_BINDING_SCHEMA_VERSION:
            raise ValueError("unsupported knowledge model binding schema")

    def identity_payload(self) -> dict[str, str]:
        return {
            "schema_version": self.schema_version,
            "model_request_id": self.model_request_id,
            "model_request_fingerprint": self.model_request_fingerprint,
            "knowledge_context_id": self.knowledge_context_id,
            "knowledge_context_fingerprint": self.knowledge_context_fingerprint,
            "claim_scope": self.claim_scope,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, str]:
        return {
            "binding_id": self.binding_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_knowledge_coaching_context(
    bundle: KnowledgeAssertionBundle,
    *,
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> KnowledgeCoachingContext:
    active = OntologyRegistry.load_default() if registry is None else registry
    validate_assertion_bundle(bundle, registry=active)
    projected = tuple(
        _project_assertion(assertion, registry=active)
        for assertion in bundle.assertions
    )
    payload = {
        "schema_version": KNOWLEDGE_COACHING_CONTEXT_SCHEMA_VERSION,
        "ontology_version": active.content_version,
        "ontology_fingerprint": active.fingerprint,
        "subject": bundle.subject.to_dict(),
        "assertion_bundle_id": bundle.bundle_id,
        "assertion_bundle_fingerprint": bundle.fingerprint,
        "assertions": [item.to_dict() for item in projected],
        "model_instructions": list(KNOWLEDGE_MODEL_INSTRUCTIONS),
        "claim_scope": (
            "model-consumable chess-knowledge sidecar; does not extend M16 factual "
            "authority or establish participant/learner claims"
        ),
        "created_at": created_at,
    }
    fingerprint = _digest(payload)
    context = KnowledgeCoachingContext(
        context_id=f"ckc_{fingerprint[:24]}",
        fingerprint=fingerprint,
        ontology_version=active.content_version,
        ontology_fingerprint=active.fingerprint,
        subject=bundle.subject,
        assertion_bundle_id=bundle.bundle_id,
        assertion_bundle_fingerprint=bundle.fingerprint,
        assertions=projected,
        model_instructions=KNOWLEDGE_MODEL_INSTRUCTIONS,
        claim_scope=payload["claim_scope"],
        created_at=created_at,
    )
    validate_knowledge_coaching_context(context, bundle=bundle, registry=active)
    return context


def validate_knowledge_coaching_context(
    context: KnowledgeCoachingContext,
    *,
    bundle: KnowledgeAssertionBundle,
    registry: OntologyRegistry | None = None,
) -> None:
    active = OntologyRegistry.load_default() if registry is None else registry
    validate_assertion_bundle(bundle, registry=active)
    if context.ontology_version != active.content_version:
        raise ValueError("knowledge context ontology version mismatch")
    if context.ontology_fingerprint != active.fingerprint:
        raise ValueError("knowledge context ontology fingerprint mismatch")
    if context.subject != bundle.subject:
        raise ValueError("knowledge context subject mismatch")
    if context.assertion_bundle_id != bundle.bundle_id:
        raise ValueError("knowledge context assertion bundle ID mismatch")
    if context.assertion_bundle_fingerprint != bundle.fingerprint:
        raise ValueError("knowledge context assertion bundle fingerprint mismatch")
    expected_assertions = tuple(
        _project_assertion(assertion, registry=active)
        for assertion in bundle.assertions
    )
    if context.assertions != expected_assertions:
        raise ValueError("knowledge context assertion projection mismatch")
    if context.model_instructions != KNOWLEDGE_MODEL_INSTRUCTIONS:
        raise ValueError("knowledge context instruction contract mismatch")
    expected = _digest(context.identity_payload())
    if context.fingerprint != expected:
        raise ValueError("knowledge context fingerprint mismatch")
    if context.context_id != f"ckc_{expected[:24]}":
        raise ValueError("knowledge context ID mismatch")


def bind_knowledge_context_to_model_request(
    *,
    model_request: dict[str, Any],
    context: KnowledgeCoachingContext,
    bundle: KnowledgeAssertionBundle,
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> KnowledgeModelBinding:
    active = OntologyRegistry.load_default() if registry is None else registry
    _validate_request_identity(model_request)
    validate_knowledge_coaching_context(context, bundle=bundle, registry=active)
    payload = {
        "schema_version": KNOWLEDGE_MODEL_BINDING_SCHEMA_VERSION,
        "model_request_id": model_request["request_id"],
        "model_request_fingerprint": model_request["fingerprint"],
        "knowledge_context_id": context.context_id,
        "knowledge_context_fingerprint": context.fingerprint,
        "claim_scope": (
            "sidecar binding only; the referenced M19 request remains unchanged "
            "and retains its original authority contract"
        ),
        "created_at": created_at,
    }
    fingerprint = _digest(payload)
    binding = KnowledgeModelBinding(
        binding_id=f"ckm_{fingerprint[:24]}",
        fingerprint=fingerprint,
        model_request_id=model_request["request_id"],
        model_request_fingerprint=model_request["fingerprint"],
        knowledge_context_id=context.context_id,
        knowledge_context_fingerprint=context.fingerprint,
        claim_scope=payload["claim_scope"],
        created_at=created_at,
    )
    validate_knowledge_model_binding(
        binding,
        model_request=model_request,
        context=context,
        bundle=bundle,
        registry=active,
    )
    return binding


def validate_knowledge_model_binding(
    binding: KnowledgeModelBinding,
    *,
    model_request: dict[str, Any],
    context: KnowledgeCoachingContext,
    bundle: KnowledgeAssertionBundle,
    registry: OntologyRegistry | None = None,
) -> None:
    _validate_request_identity(model_request)
    active = OntologyRegistry.load_default() if registry is None else registry
    validate_knowledge_coaching_context(context, bundle=bundle, registry=active)
    if binding.model_request_id != model_request["request_id"]:
        raise ValueError("knowledge binding M19 request ID mismatch")
    if binding.model_request_fingerprint != model_request["fingerprint"]:
        raise ValueError("knowledge binding M19 request fingerprint mismatch")
    if binding.knowledge_context_id != context.context_id:
        raise ValueError("knowledge binding context ID mismatch")
    if binding.knowledge_context_fingerprint != context.fingerprint:
        raise ValueError("knowledge binding context fingerprint mismatch")
    expected = _digest(binding.identity_payload())
    if binding.fingerprint != expected:
        raise ValueError("knowledge model binding fingerprint mismatch")
    if binding.binding_id != f"ckm_{expected[:24]}":
        raise ValueError("knowledge model binding ID mismatch")


def build_knowledge_augmented_provider_payload(
    *,
    model_request: dict[str, Any],
    context: KnowledgeCoachingContext,
    binding: KnowledgeModelBinding,
    bundle: KnowledgeAssertionBundle,
    registry: OntologyRegistry | None = None,
) -> dict[str, Any]:
    """Build an explicit wrapper without rewriting the referenced M19 request."""
    validate_knowledge_model_binding(
        binding,
        model_request=model_request,
        context=context,
        bundle=bundle,
        registry=registry,
    )
    return {
        "m19_request": model_request,
        "chess_knowledge_context": context.to_dict(),
        "knowledge_binding": binding.to_dict(),
    }


def _project_assertion(assertion, *, registry: OntologyRegistry):
    concept = registry.get(assertion.concept_id)
    related_ids = tuple(
        sorted({relationship.target_id for relationship in concept.relationships})
    )
    recognition_questions = (
        () if concept.pedagogy is None else concept.pedagogy.recognition_questions
    )
    return KnowledgeContextAssertion(
        assertion_ref=KnowledgeAssertionRef.from_assertion(assertion),
        preferred_name=concept.preferred_name,
        kind=concept.kind,
        definition=concept.definition,
        status=assertion.status,
        authority_class=assertion.authority_class,
        qualifiers=assertion.qualifiers,
        related_concept_ids=related_ids,
        recognition_questions=recognition_questions,
    )
