"""Chess Knowledge Ontology public surface."""

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
    "DetectionSupport",
    "ExternalMapping",
    "ONTOLOGY_SCHEMA_VERSION",
    "OntologyDocument",
    "OntologyLoadError",
    "OntologyRegistry",
    "OntologyValidationError",
    "PedagogyMetadata",
    "concept_fingerprint",
    "ontology_fingerprint",
    "validate_ontology",
]
