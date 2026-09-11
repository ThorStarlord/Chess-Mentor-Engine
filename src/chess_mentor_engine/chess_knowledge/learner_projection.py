"""Project exact chess-knowledge assertions onto existing M7C recurrence units.

M7C remains authoritative for whether a unit supports, contradicts, or otherwise
relates to a learner hypothesis. This module only attaches typed chess concepts to
those already-classified units and preserves the M7C relation verbatim.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning.hypothesis_model import HypothesisRevisionRef
from chess_mentor_engine.learning.hypothesis_recurrence_model import (
    HypothesisAssessment,
    HypothesisUnitRelation,
)

from .assertions import (
    KnowledgeAssertionBundle,
    KnowledgeAssertionRef,
    KnowledgeQualifier,
    validate_assertion_bundle,
)
from .model import AuthorityClass, ConceptKind
from .registry import OntologyRegistry

HYPOTHESIS_KNOWLEDGE_PROJECTION_SCHEMA_VERSION = (
    "chess-knowledge-hypothesis-projection.v1"
)

_RELATIONS = frozenset(
    {
        "supports",
        "contradicts",
        "successful_counterexample",
        "context_exception",
        "unclear",
        "mixed",
    }
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
class HypothesisKnowledgeOccurrence:
    """One ontology assertion observed inside one already-classified M7C unit."""

    recurrence_unit_id: str
    source_position_id: str
    source_game_id: str
    hypothesis_relation: HypothesisUnitRelation
    assertion_ref: KnowledgeAssertionRef
    status: str
    authority_class: AuthorityClass
    qualifiers: tuple[KnowledgeQualifier, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("recurrence_unit_id", self.recurrence_unit_id),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("status", self.status),
        ):
            _require_nonempty(name, value)
        if self.hypothesis_relation not in _RELATIONS:
            raise ValueError("unknown hypothesis relation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "recurrence_unit_id": self.recurrence_unit_id,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "hypothesis_relation": self.hypothesis_relation,
            "assertion_ref": self.assertion_ref.to_dict(),
            "status": self.status,
            "authority_class": self.authority_class,
            "qualifiers": [item.to_dict() for item in self.qualifiers],
        }


@dataclass(frozen=True, slots=True)
class HypothesisKnowledgeUnitProjection:
    """Ontology evidence attached to one exact M7C recurrence unit."""

    recurrence_unit_id: str
    source_position_id: str
    source_game_id: str
    hypothesis_relation: HypothesisUnitRelation
    assertion_bundle_id: str
    assertion_bundle_fingerprint: str
    occurrences: tuple[HypothesisKnowledgeOccurrence, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("recurrence_unit_id", self.recurrence_unit_id),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("assertion_bundle_id", self.assertion_bundle_id),
            ("assertion_bundle_fingerprint", self.assertion_bundle_fingerprint),
        ):
            _require_nonempty(name, value)
        if self.hypothesis_relation not in _RELATIONS:
            raise ValueError("unknown hypothesis relation")
        if not self.occurrences:
            raise ValueError("covered learner-knowledge unit requires occurrences")
        ids = tuple(item.assertion_ref.assertion_id for item in self.occurrences)
        if len(set(ids)) != len(ids):
            raise ValueError("learner-knowledge occurrence IDs must be unique")
        for item in self.occurrences:
            if item.recurrence_unit_id != self.recurrence_unit_id:
                raise ValueError("occurrence recurrence unit mismatch")
            if item.source_position_id != self.source_position_id:
                raise ValueError("occurrence source position mismatch")
            if item.source_game_id != self.source_game_id:
                raise ValueError("occurrence source game mismatch")
            if item.hypothesis_relation != self.hypothesis_relation:
                raise ValueError("occurrence hypothesis relation mismatch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "recurrence_unit_id": self.recurrence_unit_id,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "hypothesis_relation": self.hypothesis_relation,
            "assertion_bundle_id": self.assertion_bundle_id,
            "assertion_bundle_fingerprint": self.assertion_bundle_fingerprint,
            "occurrences": [item.to_dict() for item in self.occurrences],
        }


@dataclass(frozen=True, slots=True)
class HypothesisKnowledgeConceptSummary:
    """Descriptive counts over ontology occurrences grouped by M7C relation."""

    concept_id: str
    concept_fingerprint: str
    preferred_name: str
    kind: ConceptKind
    occurrence_count: int
    relation_counts: tuple[tuple[str, int], ...]
    status_counts: tuple[tuple[str, int], ...]
    authority_counts: tuple[tuple[str, int], ...]
    source_position_ids: tuple[str, ...]
    source_game_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("concept_id", self.concept_id),
            ("concept_fingerprint", self.concept_fingerprint),
            ("preferred_name", self.preferred_name),
        ):
            _require_nonempty(name, value)
        if self.occurrence_count < 1:
            raise ValueError("concept summary requires at least one occurrence")
        for name, counts in (
            ("relation_counts", self.relation_counts),
            ("status_counts", self.status_counts),
            ("authority_counts", self.authority_counts),
        ):
            labels = tuple(label for label, _ in counts)
            if len(set(labels)) != len(labels):
                raise ValueError(f"{name} labels must be unique")
            if any(not label or count < 1 for label, count in counts):
                raise ValueError(f"{name} values must be non-empty and positive")
            if sum(count for _, count in counts) != self.occurrence_count:
                raise ValueError(f"{name} must sum to occurrence_count")
        for name, values in (
            ("source_position_ids", self.source_position_ids),
            ("source_game_ids", self.source_game_ids),
        ):
            if any(not value for value in values):
                raise ValueError(f"{name} values must not be empty")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} values must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "concept_fingerprint": self.concept_fingerprint,
            "preferred_name": self.preferred_name,
            "kind": self.kind,
            "occurrence_count": self.occurrence_count,
            "relation_counts": [list(item) for item in self.relation_counts],
            "status_counts": [list(item) for item in self.status_counts],
            "authority_counts": [list(item) for item in self.authority_counts],
            "source_position_ids": list(self.source_position_ids),
            "source_game_ids": list(self.source_game_ids),
        }


@dataclass(frozen=True, slots=True)
class HypothesisKnowledgeProjection:
    """Content-addressed ontology sidecar over one immutable M7C assessment."""

    projection_id: str
    fingerprint: str
    hypothesis_assessment_id: str
    hypothesis_assessment_fingerprint: str
    hypothesis_revision_ref: HypothesisRevisionRef
    hypothesis_assessment_status: str
    ontology_version: str
    ontology_fingerprint: str
    units: tuple[HypothesisKnowledgeUnitProjection, ...]
    concept_summaries: tuple[HypothesisKnowledgeConceptSummary, ...]
    covered_recurrence_unit_ids: tuple[str, ...]
    uncovered_recurrence_unit_ids: tuple[str, ...]
    claim_scope: str
    created_at: str
    schema_version: str = HYPOTHESIS_KNOWLEDGE_PROJECTION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("projection_id", self.projection_id),
            ("fingerprint", self.fingerprint),
            ("hypothesis_assessment_id", self.hypothesis_assessment_id),
            (
                "hypothesis_assessment_fingerprint",
                self.hypothesis_assessment_fingerprint,
            ),
            ("hypothesis_assessment_status", self.hypothesis_assessment_status),
            ("ontology_version", self.ontology_version),
            ("ontology_fingerprint", self.ontology_fingerprint),
            ("claim_scope", self.claim_scope),
        ):
            _require_nonempty(name, value)
        _require_timestamp("created_at", self.created_at)
        if self.schema_version != HYPOTHESIS_KNOWLEDGE_PROJECTION_SCHEMA_VERSION:
            raise ValueError("unsupported hypothesis-knowledge projection schema")
        unit_ids = tuple(item.recurrence_unit_id for item in self.units)
        if len(set(unit_ids)) != len(unit_ids):
            raise ValueError("learner-knowledge projected units must be unique")
        concept_ids = tuple(item.concept_id for item in self.concept_summaries)
        if len(set(concept_ids)) != len(concept_ids):
            raise ValueError("learner-knowledge concept summaries must be unique")
        covered = self.covered_recurrence_unit_ids
        uncovered = self.uncovered_recurrence_unit_ids
        if len(set(covered)) != len(covered):
            raise ValueError("covered recurrence unit IDs must be unique")
        if len(set(uncovered)) != len(uncovered):
            raise ValueError("uncovered recurrence unit IDs must be unique")
        if set(covered) & set(uncovered):
            raise ValueError("covered and uncovered recurrence units must be disjoint")
        if tuple(sorted(unit_ids)) != tuple(sorted(covered)):
            raise ValueError("covered recurrence IDs must match projected units")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "hypothesis_assessment_id": self.hypothesis_assessment_id,
            "hypothesis_assessment_fingerprint": (
                self.hypothesis_assessment_fingerprint
            ),
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "hypothesis_assessment_status": self.hypothesis_assessment_status,
            "ontology_version": self.ontology_version,
            "ontology_fingerprint": self.ontology_fingerprint,
            "units": [item.to_dict() for item in self.units],
            "concept_summaries": [
                item.to_dict() for item in self.concept_summaries
            ],
            "covered_recurrence_unit_ids": list(
                self.covered_recurrence_unit_ids
            ),
            "uncovered_recurrence_unit_ids": list(
                self.uncovered_recurrence_unit_ids
            ),
            "claim_scope": self.claim_scope,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_id": self.projection_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_hypothesis_knowledge_projection(
    *,
    assessment: HypothesisAssessment,
    assertion_bundles: tuple[KnowledgeAssertionBundle, ...],
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> HypothesisKnowledgeProjection:
    """Attach ontology evidence to M7C units without reclassifying those units."""
    active = OntologyRegistry.load_default() if registry is None else registry
    _validate_assessment_identity(assessment)
    units, summaries, covered, uncovered = _derive_projection_parts(
        assessment=assessment,
        assertion_bundles=assertion_bundles,
        registry=active,
    )
    payload = {
        "schema_version": HYPOTHESIS_KNOWLEDGE_PROJECTION_SCHEMA_VERSION,
        "hypothesis_assessment_id": assessment.hypothesis_assessment_id,
        "hypothesis_assessment_fingerprint": assessment.fingerprint,
        "hypothesis_revision_ref": assessment.hypothesis_revision_ref.to_dict(),
        "hypothesis_assessment_status": assessment.status,
        "ontology_version": active.content_version,
        "ontology_fingerprint": active.fingerprint,
        "units": [item.to_dict() for item in units],
        "concept_summaries": [item.to_dict() for item in summaries],
        "covered_recurrence_unit_ids": list(covered),
        "uncovered_recurrence_unit_ids": list(uncovered),
        "claim_scope": (
            "descriptive ontology projection over existing M7C recurrence relations; "
            "does not classify recurrence, establish causal learner traits, or "
            "select interventions"
        ),
        "created_at": created_at,
    }
    fingerprint = _digest(payload)
    projection = HypothesisKnowledgeProjection(
        projection_id=f"ckh_{fingerprint[:24]}",
        fingerprint=fingerprint,
        hypothesis_assessment_id=assessment.hypothesis_assessment_id,
        hypothesis_assessment_fingerprint=assessment.fingerprint,
        hypothesis_revision_ref=assessment.hypothesis_revision_ref,
        hypothesis_assessment_status=assessment.status,
        ontology_version=active.content_version,
        ontology_fingerprint=active.fingerprint,
        units=units,
        concept_summaries=summaries,
        covered_recurrence_unit_ids=covered,
        uncovered_recurrence_unit_ids=uncovered,
        claim_scope=payload["claim_scope"],
        created_at=created_at,
    )
    validate_hypothesis_knowledge_projection(
        projection,
        assessment=assessment,
        assertion_bundles=assertion_bundles,
        registry=active,
    )
    return projection


def validate_hypothesis_knowledge_projection(
    projection: HypothesisKnowledgeProjection,
    *,
    assessment: HypothesisAssessment,
    assertion_bundles: tuple[KnowledgeAssertionBundle, ...],
    registry: OntologyRegistry | None = None,
) -> None:
    active = OntologyRegistry.load_default() if registry is None else registry
    _validate_assessment_identity(assessment)
    expected_units, expected_summaries, covered, uncovered = (
        _derive_projection_parts(
            assessment=assessment,
            assertion_bundles=assertion_bundles,
            registry=active,
        )
    )
    if projection.hypothesis_assessment_id != assessment.hypothesis_assessment_id:
        raise ValueError("learner-knowledge assessment ID mismatch")
    if projection.hypothesis_assessment_fingerprint != assessment.fingerprint:
        raise ValueError("learner-knowledge assessment fingerprint mismatch")
    if projection.hypothesis_revision_ref != assessment.hypothesis_revision_ref:
        raise ValueError("learner-knowledge hypothesis revision mismatch")
    if projection.hypothesis_assessment_status != assessment.status:
        raise ValueError("learner-knowledge assessment status mismatch")
    if projection.ontology_version != active.content_version:
        raise ValueError("learner-knowledge ontology version mismatch")
    if projection.ontology_fingerprint != active.fingerprint:
        raise ValueError("learner-knowledge ontology fingerprint mismatch")
    if projection.units != expected_units:
        raise ValueError("learner-knowledge unit projection mismatch")
    if projection.concept_summaries != expected_summaries:
        raise ValueError("learner-knowledge concept summary mismatch")
    if projection.covered_recurrence_unit_ids != covered:
        raise ValueError("learner-knowledge covered-unit mismatch")
    if projection.uncovered_recurrence_unit_ids != uncovered:
        raise ValueError("learner-knowledge uncovered-unit mismatch")
    expected = _digest(projection.identity_payload())
    if projection.fingerprint != expected:
        raise ValueError("learner-knowledge projection fingerprint mismatch")
    if projection.projection_id != f"ckh_{expected[:24]}":
        raise ValueError("learner-knowledge projection ID mismatch")


def _validate_assessment_identity(assessment: HypothesisAssessment) -> None:
    expected = _digest(assessment.to_dict(include_identity=False))
    if assessment.fingerprint != expected:
        raise ValueError("M7C hypothesis assessment fingerprint mismatch")
    expected_id = f"hypothesis_assessment_{expected[:20]}"
    if assessment.hypothesis_assessment_id != expected_id:
        raise ValueError("M7C hypothesis assessment ID mismatch")


def _derive_projection_parts(
    *,
    assessment: HypothesisAssessment,
    assertion_bundles: tuple[KnowledgeAssertionBundle, ...],
    registry: OntologyRegistry,
) -> tuple[
    tuple[HypothesisKnowledgeUnitProjection, ...],
    tuple[HypothesisKnowledgeConceptSummary, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    unit_by_subject: dict[tuple[str, str], Any] = {}
    for unit in assessment.recurrence_units:
        key = (unit.source_game_id, unit.source_position_id)
        if key in unit_by_subject:
            raise ValueError("M7C recurrence subjects must be unique for projection")
        unit_by_subject[key] = unit

    projected_units: list[HypothesisKnowledgeUnitProjection] = []
    seen_subjects: set[tuple[str, str]] = set()
    for bundle in assertion_bundles:
        validate_assertion_bundle(bundle, registry=registry)
        if bundle.subject.subject_kind != "position":
            raise ValueError("learner projection accepts position bundles only")
        if bundle.subject.game_id is None:
            raise ValueError("learner projection requires bundle game_id")
        key = (bundle.subject.game_id, bundle.subject.position_id)
        if key in seen_subjects:
            raise ValueError("duplicate assertion bundle for M7C recurrence subject")
        seen_subjects.add(key)
        unit = unit_by_subject.get(key)
        if unit is None:
            raise ValueError("assertion bundle does not match an M7C recurrence unit")
        occurrences = tuple(
            HypothesisKnowledgeOccurrence(
                recurrence_unit_id=unit.recurrence_unit_id,
                source_position_id=unit.source_position_id,
                source_game_id=unit.source_game_id,
                hypothesis_relation=unit.relation,
                assertion_ref=KnowledgeAssertionRef.from_assertion(assertion),
                status=assertion.status,
                authority_class=assertion.authority_class,
                qualifiers=assertion.qualifiers,
            )
            for assertion in bundle.assertions
        )
        projected_units.append(
            HypothesisKnowledgeUnitProjection(
                recurrence_unit_id=unit.recurrence_unit_id,
                source_position_id=unit.source_position_id,
                source_game_id=unit.source_game_id,
                hypothesis_relation=unit.relation,
                assertion_bundle_id=bundle.bundle_id,
                assertion_bundle_fingerprint=bundle.fingerprint,
                occurrences=occurrences,
            )
        )

    units = tuple(sorted(projected_units, key=lambda item: item.recurrence_unit_id))
    covered = tuple(item.recurrence_unit_id for item in units)
    covered_set = set(covered)
    uncovered = tuple(
        unit_id
        for unit_id in assessment.recurrence_unit_ids
        if unit_id not in covered_set
    )
    summaries = _summarize_concepts(units=units, registry=registry)
    return units, summaries, covered, uncovered


def _summarize_concepts(
    *,
    units: tuple[HypothesisKnowledgeUnitProjection, ...],
    registry: OntologyRegistry,
) -> tuple[HypothesisKnowledgeConceptSummary, ...]:
    occurrences_by_concept: dict[str, list[HypothesisKnowledgeOccurrence]] = {}
    for unit in units:
        for occurrence in unit.occurrences:
            concept_id = occurrence.assertion_ref.concept_id
            occurrences_by_concept.setdefault(concept_id, []).append(occurrence)

    summaries: list[HypothesisKnowledgeConceptSummary] = []
    for concept_id in sorted(occurrences_by_concept):
        occurrences = occurrences_by_concept[concept_id]
        concept = registry.get(concept_id)
        summaries.append(
            HypothesisKnowledgeConceptSummary(
                concept_id=concept_id,
                concept_fingerprint=registry.concept_fingerprint(concept_id),
                preferred_name=concept.preferred_name,
                kind=concept.kind,
                occurrence_count=len(occurrences),
                relation_counts=_count_values(
                    item.hypothesis_relation for item in occurrences
                ),
                status_counts=_count_values(item.status for item in occurrences),
                authority_counts=_count_values(
                    item.authority_class for item in occurrences
                ),
                source_position_ids=tuple(
                    sorted({item.source_position_id for item in occurrences})
                ),
                source_game_ids=tuple(
                    sorted({item.source_game_id for item in occurrences})
                ),
            )
        )
    return tuple(summaries)


def _count_values(values) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(values).items()))
