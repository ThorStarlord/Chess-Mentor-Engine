"""Cross-concept validation for the chess-knowledge ontology."""

from __future__ import annotations

from .model import OntologyDocument


class OntologyValidationError(ValueError):
    """The ontology cannot preserve identity, hierarchy, or mapping invariants."""


def validate_ontology(document: OntologyDocument) -> None:
    """Validate graph-level invariants not knowable by one concept in isolation."""
    concepts = document.concepts
    ids = tuple(item.concept_id for item in concepts)
    if len(set(ids)) != len(ids):
        raise OntologyValidationError("ontology concept IDs must be unique")
    by_id = {item.concept_id: item for item in concepts}

    for concept in concepts:
        for parent_id in concept.parent_ids:
            if parent_id not in by_id:
                raise OntologyValidationError(
                    f"unknown parent concept {parent_id!r} for {concept.concept_id!r}"
                )
        for relation in concept.relationships:
            if relation.target_id not in by_id:
                raise OntologyValidationError(
                    "unknown relationship target "
                    f"{relation.target_id!r} for {concept.concept_id!r}"
                )
            if relation.target_id == concept.concept_id:
                raise OntologyValidationError("self relationships are not allowed")

    _validate_parent_cycles(by_id)
    _validate_aliases(concepts)
    _validate_exact_external_mappings(concepts)


def _validate_parent_cycles(by_id) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(concept_id: str) -> None:
        if concept_id in visited:
            return
        if concept_id in visiting:
            raise OntologyValidationError("ontology parent hierarchy contains a cycle")
        visiting.add(concept_id)
        for parent_id in by_id[concept_id].parent_ids:
            visit(parent_id)
        visiting.remove(concept_id)
        visited.add(concept_id)

    for concept_id in by_id:
        visit(concept_id)


def _validate_aliases(concepts) -> None:
    names: dict[str, str] = {}
    for concept in concepts:
        values = (concept.preferred_name, *concept.aliases)
        for value in values:
            normalized = value.casefold().strip()
            previous = names.get(normalized)
            if previous is not None and previous != concept.concept_id:
                raise OntologyValidationError(
                    f"ambiguous preferred name/alias {value!r}: "
                    f"{previous!r} and {concept.concept_id!r}"
                )
            names[normalized] = concept.concept_id


def _validate_exact_external_mappings(concepts) -> None:
    exact: dict[tuple[str, str], str] = {}
    for concept in concepts:
        for mapping in concept.external_mappings:
            if mapping.relation != "exact":
                continue
            key = (mapping.namespace, mapping.external_id)
            previous = exact.get(key)
            if previous is not None and previous != concept.concept_id:
                raise OntologyValidationError(
                    "one exact external mapping cannot identify multiple concepts: "
                    f"{key!r}"
                )
            exact[key] = concept.concept_id
