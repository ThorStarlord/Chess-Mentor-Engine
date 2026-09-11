"""Chess Knowledge Ontology public surface."""

from .assertions import (
    KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION,
    KNOWLEDGE_ASSERTION_SCHEMA_VERSION,
    KnowledgeAssertion,
    KnowledgeAssertionBundle,
    KnowledgeAssertionRef,
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeQualifier,
    KnowledgeSubject,
    build_assertion_bundle,
    build_knowledge_assertion,
    validate_assertion_bundle,
    validate_knowledge_assertion,
)
from .fingerprints import concept_fingerprint, ontology_fingerprint
from .model import (
    AuthorityClass,
    ChessConcept,
    ConceptKind,
    ConceptRelationship,
    DetectionSupport,
    ExternalMapping,
    OntologyDocument,
    PedagogyMetadata,
)
from .registry import (
    DEFAULT_ONTOLOGY_RESOURCE,
    DEFAULT_ONTOLOGY_RESOURCES,
    ONTOLOGY_SCHEMA_VERSION,
    OntologyLoadError,
    OntologyRegistry,
)
from .validation import OntologyValidationError, validate_ontology

__all__ = [
    "AuthorityClass",
    "ChessConcept",
    "ConceptKind",
    "ConceptRelationship",
    "DEFAULT_ONTOLOGY_RESOURCE",
    "DEFAULT_ONTOLOGY_RESOURCES",
    "DetectionSupport",
    "ExternalMapping",
    "KNOWLEDGE_ASSERTION_BUNDLE_SCHEMA_VERSION",
    "KNOWLEDGE_ASSERTION_SCHEMA_VERSION",
    "KnowledgeAssertion",
    "KnowledgeAssertionBundle",
    "KnowledgeAssertionRef",
    "KnowledgeEvidenceRef",
    "KnowledgeProvenance",
    "KnowledgeQualifier",
    "KnowledgeSubject",
    "ONTOLOGY_SCHEMA_VERSION",
    "OntologyDocument",
    "OntologyLoadError",
    "OntologyRegistry",
    "OntologyValidationError",
    "PedagogyMetadata",
    "build_assertion_bundle",
    "build_knowledge_assertion",
    "concept_fingerprint",
    "ontology_fingerprint",
    "validate_assertion_bundle",
    "validate_knowledge_assertion",
    "validate_ontology",
]
