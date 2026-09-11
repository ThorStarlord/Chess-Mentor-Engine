"""Stable fingerprints for ontology definitions and documents."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.chess import canonical_json

from .model import ChessConcept, OntologyDocument


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def concept_fingerprint(concept: ChessConcept) -> str:
    return _fingerprint(concept.to_dict())


def ontology_fingerprint(document: OntologyDocument) -> str:
    return _fingerprint(document.to_dict())
