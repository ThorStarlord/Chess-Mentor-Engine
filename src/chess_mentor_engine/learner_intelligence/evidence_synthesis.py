"""M39 deterministic synthesis of current hypothesis evidence.

M39 explains one already-current M7C assessment in the context of the M36 read model.
It never reclassifies recurrence, changes learner state, or promotes ontology context
into learner authority.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import HypothesisKnowledgeProjection
from chess_mentor_engine.learning import (
    HypothesisAssessment,
    HypothesisEvidenceLinkRef,
    HypothesisRevision,
    HypothesisRevisionRef,
)
from chess_mentor_engine.longitudinal import (
    LearnerReadReference,
    LearnerStateReadModel,
)

HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION = "m39.hypothesis-evidence-synthesis.v1"


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _timestamp(name: str, value: str) -> None:
    _nonempty(name, value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone offset")


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


@dataclass(frozen=True, slots=True)
class EvidenceSynthesisReference:
    kind: str
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _nonempty("kind", self.kind)
        _nonempty("ref_id", self.ref_id)
        _nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceCounts:
    eligible_link_count: int
    excluded_link_count: int
    support_unit_count: int
    independent_support_count: int
    contradiction_unit_count: int
    successful_counterexample_unit_count: int
    context_exception_unit_count: int
    unclear_unit_count: int
    mixed_unit_count: int

    def __post_init__(self) -> None:
        if any(value < 0 for value in self.to_dict().values()):
            raise ValueError("M39 evidence counts must not be negative")

    def to_dict(self) -> dict[str, int]:
        return {
            "eligible_link_count": self.eligible_link_count,
            "excluded_link_count": self.excluded_link_count,
            "support_unit_count": self.support_unit_count,
            "independent_support_count": self.independent_support_count,
            "contradiction_unit_count": self.contradiction_unit_count,
            "successful_counterexample_unit_count": (
                self.successful_counterexample_unit_count
            ),
            "context_exception_unit_count": self.context_exception_unit_count,
            "unclear_unit_count": self.unclear_unit_count,
            "mixed_unit_count": self.mixed_unit_count,
        }


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceUnitSynthesis:
    recurrence_unit_id: str
    relation: str
    source_position_id: str
    source_game_id: str
    independence_unit_id: str
    link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    context_ref_ids: tuple[str, ...]
    measurement_conditions: tuple[str, ...]
    concept_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("recurrence_unit_id", self.recurrence_unit_id),
            ("relation", self.relation),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("independence_unit_id", self.independence_unit_id),
        ):
            _nonempty(name, value)
        if self.relation not in {
            "supports",
            "contradicts",
            "successful_counterexample",
            "context_exception",
            "unclear",
            "mixed",
        }:
            raise ValueError("unknown M39 recurrence-unit relation")
        for name, values in (
            ("context_ref_ids", self.context_ref_ids),
            ("measurement_conditions", self.measurement_conditions),
            ("concept_ids", self.concept_ids),
        ):
            if any(not value for value in values):
                raise ValueError(f"{name} values must not be empty")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} values must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "recurrence_unit_id": self.recurrence_unit_id,
            "relation": self.relation,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "independence_unit_id": self.independence_unit_id,
            "link_refs": [item.to_dict() for item in self.link_refs],
            "context_ref_ids": list(self.context_ref_ids),
            "measurement_conditions": list(self.measurement_conditions),
            "concept_ids": list(self.concept_ids),
        }


@dataclass(frozen=True, slots=True)
class HypothesisReviewSummary:
    contradiction_review_ref: EvidenceSynthesisReference
    contradiction_review_state: str
    counterexample_review_ref: EvidenceSynthesisReference
    counterexample_review_state: str
    competing_explanation_review_ref: EvidenceSynthesisReference
    competing_explanation_review_state: str

    def __post_init__(self) -> None:
        for state in (
            self.contradiction_review_state,
            self.counterexample_review_state,
            self.competing_explanation_review_state,
        ):
            if state not in {"not_required", "completed"}:
                raise ValueError("unknown M39 review state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "contradiction_review_ref": self.contradiction_review_ref.to_dict(),
            "contradiction_review_state": self.contradiction_review_state,
            "counterexample_review_ref": self.counterexample_review_ref.to_dict(),
            "counterexample_review_state": self.counterexample_review_state,
            "competing_explanation_review_ref": (
                self.competing_explanation_review_ref.to_dict()
            ),
            "competing_explanation_review_state": (
                self.competing_explanation_review_state
            ),
        }


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceSynthesis:
    synthesis_id: str
    fingerprint: str
    participant_id: str
    learner_read_model_ref: EvidenceSynthesisReference
    hypothesis_revision_ref: HypothesisRevisionRef
    statement: str
    scope_definition: str
    unresolved_alternative_notes: tuple[str, ...]
    hypothesis_assessment_ref: EvidenceSynthesisReference
    hypothesis_assessment_status: str
    assessment_policy_ref: EvidenceSynthesisReference
    status_reasons: tuple[str, ...]
    evidence_counts: HypothesisEvidenceCounts
    units: tuple[HypothesisEvidenceUnitSynthesis, ...]
    source_position_ids: tuple[str, ...]
    source_game_ids: tuple[str, ...]
    review_summary: HypothesisReviewSummary
    knowledge_projection_ref: EvidenceSynthesisReference | None
    concept_ids: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    change_conditions: tuple[str, ...]
    created_at: str
    claim_scope: str = "participant_specific_deterministic_evidence_synthesis"
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("synthesis_id", self.synthesis_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("statement", self.statement),
            ("scope_definition", self.scope_definition),
            ("hypothesis_assessment_status", self.hypothesis_assessment_status),
            ("claim_scope", self.claim_scope),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION:
            raise ValueError("unsupported M39 evidence-synthesis schema")
        unit_ids = tuple(item.recurrence_unit_id for item in self.units)
        if len(set(unit_ids)) != len(unit_ids):
            raise ValueError("M39 recurrence units must be unique")
        for name, values in (
            ("source_position_ids", self.source_position_ids),
            ("source_game_ids", self.source_game_ids),
            ("concept_ids", self.concept_ids),
            ("evidence_gaps", self.evidence_gaps),
            ("change_conditions", self.change_conditions),
        ):
            if any(not value for value in values):
                raise ValueError(f"{name} values must not be empty")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} values must be unique")
        if self.claim_scope != "participant_specific_deterministic_evidence_synthesis":
            raise ValueError("unknown M39 claim scope")
        if self.causal_effect != "not_established" or self.mastery != "not_established":
            raise ValueError("M39 cannot establish causality or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "learner_read_model_ref": self.learner_read_model_ref.to_dict(),
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "statement": self.statement,
            "scope_definition": self.scope_definition,
            "unresolved_alternative_notes": list(self.unresolved_alternative_notes),
            "hypothesis_assessment_ref": self.hypothesis_assessment_ref.to_dict(),
            "hypothesis_assessment_status": self.hypothesis_assessment_status,
            "assessment_policy_ref": self.assessment_policy_ref.to_dict(),
            "status_reasons": list(self.status_reasons),
            "evidence_counts": self.evidence_counts.to_dict(),
            "units": [item.to_dict() for item in self.units],
            "source_position_ids": list(self.source_position_ids),
            "source_game_ids": list(self.source_game_ids),
            "review_summary": self.review_summary.to_dict(),
            "knowledge_projection_ref": (
                None
                if self.knowledge_projection_ref is None
                else self.knowledge_projection_ref.to_dict()
            ),
            "concept_ids": list(self.concept_ids),
            "evidence_gaps": list(self.evidence_gaps),
            "change_conditions": list(self.change_conditions),
            "created_at": self.created_at,
            "claim_scope": self.claim_scope,
            "causal_effect": self.causal_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthesis_id": self.synthesis_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def _read_model_ref(read_model: LearnerStateReadModel) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="learner_state_read_model",
        ref_id=read_model.read_model_id,
        fingerprint=read_model.fingerprint,
    )


def _assessment_ref(assessment: HypothesisAssessment) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="hypothesis_assessment",
        ref_id=assessment.hypothesis_assessment_id,
        fingerprint=assessment.fingerprint,
    )


def _policy_ref(assessment: HypothesisAssessment) -> EvidenceSynthesisReference:
    ref = assessment.assessment_policy_ref
    return EvidenceSynthesisReference(
        kind="hypothesis_assessment_policy",
        ref_id=f"{ref.assessment_policy_id}:{ref.version}",
        fingerprint=ref.fingerprint,
    )


def _review_ref(kind: str, review: Any) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind=kind,
        ref_id=review.review_id,
        fingerprint=review.fingerprint,
    )


def _knowledge_by_unit(
    projection: HypothesisKnowledgeProjection | None,
) -> dict[str, tuple[str, ...]]:
    if projection is None:
        return {}
    return {
        unit.recurrence_unit_id: tuple(
            sorted({item.assertion_ref.concept_id for item in unit.occurrences})
        )
        for unit in projection.units
    }


def _evidence_counts(assessment: HypothesisAssessment) -> HypothesisEvidenceCounts:
    summary = assessment.evidence_summary
    return HypothesisEvidenceCounts(
        eligible_link_count=summary.eligible_link_count,
        excluded_link_count=summary.excluded_link_count,
        support_unit_count=summary.support_unit_count,
        independent_support_count=summary.independent_support_count,
        contradiction_unit_count=summary.contradiction_unit_count,
        successful_counterexample_unit_count=(
            summary.successful_counterexample_unit_count
        ),
        context_exception_unit_count=summary.context_exception_unit_count,
        unclear_unit_count=summary.unclear_unit_count,
        mixed_unit_count=summary.mixed_unit_count,
    )


def _derive_gaps(
    *,
    assessment: HypothesisAssessment,
    revision: HypothesisRevision,
    projection: HypothesisKnowledgeProjection | None,
) -> tuple[str, ...]:
    gaps: list[str] = []
    if assessment.status != "supported_recurrence":
        gaps.append(
            "The current M7C assessment is not supported_recurrence; additional "
            "eligible evidence may be required before teaching from this hypothesis."
        )
    summary = assessment.evidence_summary
    if (
        summary.contradiction_unit_count == 0
        and summary.successful_counterexample_unit_count == 0
        and summary.context_exception_unit_count == 0
    ):
        gaps.append(
            "No contradiction, successful-counterexample, or context-exception "
            "unit is present in the current M7C assessment."
        )
    if revision.unresolved_alternative_notes:
        gaps.append(
            f"The current revision retains {len(revision.unresolved_alternative_notes)} "
            "unresolved alternative explanation(s)."
        )
    if projection is None:
        gaps.append("No K7 chess-knowledge projection is attached to this hypothesis.")
    elif projection.uncovered_recurrence_unit_ids:
        gaps.append(
            f"K7 semantic coverage is incomplete for "
            f"{len(projection.uncovered_recurrence_unit_ids)} recurrence unit(s)."
        )
    return tuple(gaps)


def _change_conditions(
    *,
    assessment: HypothesisAssessment,
    revision: HypothesisRevision,
) -> tuple[str, ...]:
    items = [
        "A future M7C assessment over new eligible evidence may weaken, narrow, "
        "strengthen, or otherwise change the current recurrence status."
    ]
    if assessment.status == "supported_recurrence":
        items.append(
            "Eligible contradiction, successful-counterexample, or context-exception "
            "evidence may challenge the current hypothesis breadth; M39 does not "
            "predict the resulting M7C status."
        )
    if revision.unresolved_alternative_notes:
        items.append(
            "Evidence that discriminates among unresolved alternative explanations "
            "may change interpretation without changing the underlying chess facts."
        )
    return tuple(items)


def build_hypothesis_evidence_synthesis(
    *,
    participant_id: str,
    learner_read_model: LearnerStateReadModel,
    revision: HypothesisRevision,
    assessment: HypothesisAssessment,
    knowledge_projection: HypothesisKnowledgeProjection | None = None,
    created_at: str,
) -> HypothesisEvidenceSynthesis:
    """Explain one exact current M7C assessment without changing its authority."""
    _nonempty("participant_id", participant_id)
    _timestamp("created_at", created_at)
    if learner_read_model.participant_id != participant_id:
        raise ValueError("M39 learner read-model participant mismatch")

    expected_revision = _revision_ref(revision)
    entries = tuple(
        item
        for item in learner_read_model.hypotheses
        if item.hypothesis_id == revision.hypothesis_id
    )
    if len(entries) != 1:
        raise ValueError("M39 requires exactly one current M36 hypothesis entry")
    entry = entries[0]
    if entry.current_revision_ref != expected_revision:
        raise ValueError("M39 revision is not current in the M36 read model")
    if assessment.hypothesis_revision_ref != expected_revision:
        raise ValueError("M39 M7C assessment/revision mismatch")
    if entry.m7_assessment_ref is None:
        raise ValueError("M39 requires a current M7C assessment in M36")
    if (
        entry.m7_assessment_ref.ref_id != assessment.hypothesis_assessment_id
        or entry.m7_assessment_ref.fingerprint != assessment.fingerprint
    ):
        raise ValueError("M39 M36/M7C assessment identity mismatch")
    if entry.m7_status != assessment.status:
        raise ValueError("M39 M36/M7C status mismatch")
    if any(unit.participant_id != participant_id for unit in assessment.recurrence_units):
        raise ValueError("M39 recurrence-unit participant mismatch")

    entry_projection_ref: LearnerReadReference | None = entry.knowledge.projection_ref
    if entry_projection_ref is None:
        if knowledge_projection is not None:
            raise ValueError("M39 supplied K7 projection is absent from M36")
    else:
        if knowledge_projection is None:
            raise ValueError("M39 requires the K7 projection referenced by M36")
        if (
            entry_projection_ref.ref_id != knowledge_projection.projection_id
            or entry_projection_ref.fingerprint != knowledge_projection.fingerprint
        ):
            raise ValueError("M39 M36/K7 projection identity mismatch")
        if knowledge_projection.hypothesis_revision_ref != expected_revision:
            raise ValueError("M39 K7 projection/revision mismatch")
        if (
            knowledge_projection.hypothesis_assessment_id
            != assessment.hypothesis_assessment_id
            or knowledge_projection.hypothesis_assessment_fingerprint
            != assessment.fingerprint
        ):
            raise ValueError("M39 K7/M7C assessment mismatch")

    concepts_by_unit = _knowledge_by_unit(knowledge_projection)
    units = tuple(
        HypothesisEvidenceUnitSynthesis(
            recurrence_unit_id=unit.recurrence_unit_id,
            relation=unit.relation,
            source_position_id=unit.source_position_id,
            source_game_id=unit.source_game_id,
            independence_unit_id=unit.independence_unit_id,
            link_refs=unit.link_refs,
            context_ref_ids=tuple(sorted(item.ref_id for item in unit.context_refs)),
            measurement_conditions=tuple(sorted(unit.measurement_conditions)),
            concept_ids=concepts_by_unit.get(unit.recurrence_unit_id, ()),
        )
        for unit in assessment.recurrence_units
    )
    concept_ids = (
        ()
        if knowledge_projection is None
        else tuple(
            sorted(item.concept_id for item in knowledge_projection.concept_summaries)
        )
    )
    review_summary = HypothesisReviewSummary(
        contradiction_review_ref=_review_ref(
            "hypothesis_contradiction_review", assessment.contradiction_review
        ),
        contradiction_review_state=assessment.contradiction_review.state,
        counterexample_review_ref=_review_ref(
            "hypothesis_counterexample_review", assessment.counterexample_review
        ),
        counterexample_review_state=assessment.counterexample_review.state,
        competing_explanation_review_ref=_review_ref(
            "hypothesis_competing_explanation_review",
            assessment.competing_explanation_review,
        ),
        competing_explanation_review_state=assessment.competing_explanation_review.state,
    )
    knowledge_ref = (
        None
        if knowledge_projection is None
        else EvidenceSynthesisReference(
            kind="hypothesis_knowledge_projection",
            ref_id=knowledge_projection.projection_id,
            fingerprint=knowledge_projection.fingerprint,
        )
    )
    payload = {
        "schema_version": HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION,
        "participant_id": participant_id,
        "learner_read_model_ref": _read_model_ref(learner_read_model).to_dict(),
        "hypothesis_revision_ref": expected_revision.to_dict(),
        "statement": revision.statement,
        "scope_definition": revision.scope_definition,
        "unresolved_alternative_notes": list(revision.unresolved_alternative_notes),
        "hypothesis_assessment_ref": _assessment_ref(assessment).to_dict(),
        "hypothesis_assessment_status": assessment.status,
        "assessment_policy_ref": _policy_ref(assessment).to_dict(),
        "status_reasons": list(assessment.status_reasons),
        "evidence_counts": _evidence_counts(assessment).to_dict(),
        "units": [item.to_dict() for item in units],
        "source_position_ids": list(assessment.source_position_ids),
        "source_game_ids": list(assessment.source_game_ids),
        "review_summary": review_summary.to_dict(),
        "knowledge_projection_ref": (
            None if knowledge_ref is None else knowledge_ref.to_dict()
        ),
        "concept_ids": list(concept_ids),
        "evidence_gaps": list(
            _derive_gaps(
                assessment=assessment,
                revision=revision,
                projection=knowledge_projection,
            )
        ),
        "change_conditions": list(
            _change_conditions(assessment=assessment, revision=revision)
        ),
        "created_at": created_at,
        "claim_scope": "participant_specific_deterministic_evidence_synthesis",
        "causal_effect": "not_established",
        "mastery": "not_established",
    }
    digest = _digest(payload)
    return HypothesisEvidenceSynthesis(
        synthesis_id=f"hypothesis_evidence_synthesis_{digest[:20]}",
        fingerprint=digest,
        participant_id=participant_id,
        learner_read_model_ref=_read_model_ref(learner_read_model),
        hypothesis_revision_ref=expected_revision,
        statement=revision.statement,
        scope_definition=revision.scope_definition,
        unresolved_alternative_notes=revision.unresolved_alternative_notes,
        hypothesis_assessment_ref=_assessment_ref(assessment),
        hypothesis_assessment_status=assessment.status,
        assessment_policy_ref=_policy_ref(assessment),
        status_reasons=assessment.status_reasons,
        evidence_counts=_evidence_counts(assessment),
        units=units,
        source_position_ids=assessment.source_position_ids,
        source_game_ids=assessment.source_game_ids,
        review_summary=review_summary,
        knowledge_projection_ref=knowledge_ref,
        concept_ids=concept_ids,
        evidence_gaps=tuple(payload["evidence_gaps"]),
        change_conditions=tuple(payload["change_conditions"]),
        created_at=created_at,
    )


def validate_hypothesis_evidence_synthesis(
    synthesis: HypothesisEvidenceSynthesis,
    *,
    participant_id: str,
    learner_read_model: LearnerStateReadModel,
    revision: HypothesisRevision,
    assessment: HypothesisAssessment,
    knowledge_projection: HypothesisKnowledgeProjection | None = None,
) -> None:
    expected = build_hypothesis_evidence_synthesis(
        participant_id=participant_id,
        learner_read_model=learner_read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=knowledge_projection,
        created_at=synthesis.created_at,
    )
    if synthesis != expected:
        raise ValueError("M39 hypothesis evidence synthesis mismatch")
