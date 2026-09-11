"""M44 deterministic learner-progress presentation and local reference surface."""

from __future__ import annotations

import hashlib
import html
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.learning import HypothesisRevisionRef
from chess_mentor_engine.longitudinal import (
    LearnerHypothesisReadEntry,
    LearnerStateReadModel,
)
from chess_mentor_engine.training import TrainingInterventionRef

from .evidence_acquisition import EvidenceAcquisitionPlan
from .evidence_synthesis import (
    EvidenceSynthesisReference,
    HypothesisEvidenceCounts,
    HypothesisEvidenceSynthesis,
)
from .intervention_matching import InterventionCandidateSet
from .next_session import NextSessionActionCandidate, NextSessionPlan

LEARNER_PROGRESS_VIEW_SCHEMA_VERSION = "m44.learner-progress-view.v1"
LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION = "m44.learner-progress-reference-surface.v1"


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


def _unique(name: str, values: tuple[str, ...]) -> None:
    if any(not value for value in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} values must be unique")


def _read_model_ref(read_model: LearnerStateReadModel) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_state_read_model",
        read_model.read_model_id,
        read_model.fingerprint,
    )


def _plan_ref(plan: NextSessionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_plan",
        plan.plan_id,
        plan.fingerprint,
    )


def _proposal_ref(proposal: NextSessionActionCandidate) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_action_candidate",
        (
            f"{proposal.hypothesis_id}:"
            f"{proposal.hypothesis_revision_ref.revision_id}:{proposal.action}"
        ),
        _digest(proposal.to_dict()),
    )


def _synthesis_ref(
    synthesis: HypothesisEvidenceSynthesis,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "hypothesis_evidence_synthesis",
        synthesis.synthesis_id,
        synthesis.fingerprint,
    )


def _acquisition_ref(plan: EvidenceAcquisitionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "evidence_acquisition_plan",
        plan.acquisition_plan_id,
        plan.fingerprint,
    )


def _candidate_set_ref(
    candidate_set: InterventionCandidateSet,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "intervention_candidate_set",
        candidate_set.candidate_set_id,
        candidate_set.fingerprint,
    )


@dataclass(frozen=True, slots=True)
class ProgressConcept:
    concept_id: str
    preferred_name: str
    kind: str
    recognition_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("concept_id", self.concept_id),
            ("preferred_name", self.preferred_name),
            ("kind", self.kind),
        ):
            _nonempty(name, value)
        _unique("recognition_questions", self.recognition_questions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "preferred_name": self.preferred_name,
            "kind": self.kind,
            "recognition_questions": list(self.recognition_questions),
        }


@dataclass(frozen=True, slots=True)
class ProgressEvidenceUnit:
    recurrence_unit_id: str
    relation: str
    source_position_id: str
    source_game_id: str
    concept_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("recurrence_unit_id", self.recurrence_unit_id),
            ("relation", self.relation),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
        ):
            _nonempty(name, value)
        _unique("concept_ids", self.concept_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recurrence_unit_id": self.recurrence_unit_id,
            "relation": self.relation,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "concept_ids": list(self.concept_ids),
        }


@dataclass(frozen=True, slots=True)
class ProgressAcquisitionCandidate:
    candidate_kind: str
    origin: str
    source_position_id: str
    source_game_id: str
    semantic_coverage: str
    concept_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("candidate_kind", self.candidate_kind),
            ("origin", self.origin),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("semantic_coverage", self.semantic_coverage),
        ):
            _nonempty(name, value)
        _unique("concept_ids", self.concept_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_kind": self.candidate_kind,
            "origin": self.origin,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "semantic_coverage": self.semantic_coverage,
            "concept_ids": list(self.concept_ids),
        }


@dataclass(frozen=True, slots=True)
class ProgressInterventionCandidate:
    intervention_ref: TrainingInterventionRef
    status: str
    target_concept_matches: tuple[str, ...]
    reinforcement_matches: tuple[str, ...]
    training_mode_matches: tuple[str, ...]
    contraindication_matches: tuple[str, ...]

    def __post_init__(self) -> None:
        _nonempty("status", self.status)
        for name, values in (
            ("target_concept_matches", self.target_concept_matches),
            ("reinforcement_matches", self.reinforcement_matches),
            ("training_mode_matches", self.training_mode_matches),
            ("contraindication_matches", self.contraindication_matches),
        ):
            _unique(name, values)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intervention_ref": self.intervention_ref.to_dict(),
            "status": self.status,
            "target_concept_matches": list(self.target_concept_matches),
            "reinforcement_matches": list(self.reinforcement_matches),
            "training_mode_matches": list(self.training_mode_matches),
            "contraindication_matches": list(self.contraindication_matches),
        }


@dataclass(frozen=True, slots=True)
class LearnerProgressHypothesis:
    hypothesis_id: str
    current_revision_ref: HypothesisRevisionRef
    priority_rank: int | None
    is_current_priority: bool
    statement: str
    scope_definition: str
    lifecycle_state: str
    m7_status: str | None
    synthesis_ref: EvidenceSynthesisReference | None
    status_reasons: tuple[str, ...]
    evidence_counts: HypothesisEvidenceCounts | None
    evidence_units: tuple[ProgressEvidenceUnit, ...]
    concepts: tuple[ProgressConcept, ...]
    intervention_state: str
    selected_interventions: tuple[TrainingInterventionRef, ...]
    outcome_statuses: tuple[tuple[str, str], ...]
    evidence_gaps: tuple[str, ...]
    change_conditions: tuple[str, ...]
    next_action: str | None
    next_action_reasons: tuple[str, ...]
    blocking_uncertainty: tuple[str, ...]
    acquisition_ref: EvidenceSynthesisReference | None
    acquisition_intent: str | None
    acquisition_candidates: tuple[ProgressAcquisitionCandidate, ...]
    acquisition_gaps: tuple[str, ...]
    intervention_candidate_set_ref: EvidenceSynthesisReference | None
    intervention_candidates: tuple[ProgressInterventionCandidate, ...]
    matching_gaps: tuple[str, ...]
    unverified_prerequisites: tuple[str, ...]

    def __post_init__(self) -> None:
        _nonempty("hypothesis_id", self.hypothesis_id)
        _nonempty("statement", self.statement)
        _nonempty("scope_definition", self.scope_definition)
        _nonempty("lifecycle_state", self.lifecycle_state)
        if self.priority_rank is not None and self.priority_rank < 1:
            raise ValueError("M44 priority rank must be positive")
        if self.is_current_priority != (self.priority_rank == 1):
            raise ValueError("M44 current priority must be rank one")
        if (self.next_action is None) != (self.priority_rank is None):
            raise ValueError("M44 next action and priority rank must appear together")
        if (self.synthesis_ref is None) != (self.evidence_counts is None):
            raise ValueError("M44 synthesis ref/counts must appear together")
        if (self.acquisition_ref is None) != (self.acquisition_intent is None):
            raise ValueError("M44 acquisition ref/intent must appear together")
        if self.acquisition_ref is None and (
            self.acquisition_candidates or self.acquisition_gaps
        ):
            raise ValueError("M44 acquisition content requires an exact M43 ref")
        if self.intervention_candidate_set_ref is None and (
            self.intervention_candidates
            or self.matching_gaps
            or self.unverified_prerequisites
        ):
            raise ValueError("M44 matching content requires an exact M41 ref")
        for name, values in (
            ("status_reasons", self.status_reasons),
            ("evidence_gaps", self.evidence_gaps),
            ("change_conditions", self.change_conditions),
            ("next_action_reasons", self.next_action_reasons),
            ("blocking_uncertainty", self.blocking_uncertainty),
            ("acquisition_gaps", self.acquisition_gaps),
            ("matching_gaps", self.matching_gaps),
            ("unverified_prerequisites", self.unverified_prerequisites),
        ):
            _unique(name, values)
        kinds = tuple(kind for kind, _ in self.outcome_statuses)
        if len(set(kinds)) != len(kinds):
            raise ValueError("M44 outcome kinds must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "current_revision_ref": self.current_revision_ref.to_dict(),
            "priority_rank": self.priority_rank,
            "is_current_priority": self.is_current_priority,
            "statement": self.statement,
            "scope_definition": self.scope_definition,
            "lifecycle_state": self.lifecycle_state,
            "m7_status": self.m7_status,
            "synthesis_ref": (
                None if self.synthesis_ref is None else self.synthesis_ref.to_dict()
            ),
            "status_reasons": list(self.status_reasons),
            "evidence_counts": (
                None if self.evidence_counts is None else self.evidence_counts.to_dict()
            ),
            "evidence_units": [item.to_dict() for item in self.evidence_units],
            "concepts": [item.to_dict() for item in self.concepts],
            "intervention_state": self.intervention_state,
            "selected_interventions": [
                item.to_dict() for item in self.selected_interventions
            ],
            "outcome_statuses": [list(item) for item in self.outcome_statuses],
            "evidence_gaps": list(self.evidence_gaps),
            "change_conditions": list(self.change_conditions),
            "next_action": self.next_action,
            "next_action_reasons": list(self.next_action_reasons),
            "blocking_uncertainty": list(self.blocking_uncertainty),
            "acquisition_ref": (
                None if self.acquisition_ref is None else self.acquisition_ref.to_dict()
            ),
            "acquisition_intent": self.acquisition_intent,
            "acquisition_candidates": [
                item.to_dict() for item in self.acquisition_candidates
            ],
            "acquisition_gaps": list(self.acquisition_gaps),
            "intervention_candidate_set_ref": (
                None
                if self.intervention_candidate_set_ref is None
                else self.intervention_candidate_set_ref.to_dict()
            ),
            "intervention_candidates": [
                item.to_dict() for item in self.intervention_candidates
            ],
            "matching_gaps": list(self.matching_gaps),
            "unverified_prerequisites": list(self.unverified_prerequisites),
        }


@dataclass(frozen=True, slots=True)
class LearnerProgressView:
    view_id: str
    fingerprint: str
    participant_id: str
    learner_read_model_ref: EvidenceSynthesisReference
    next_session_plan_ref: EvidenceSynthesisReference
    ontology_fingerprint: str
    hypotheses: tuple[LearnerProgressHypothesis, ...]
    created_at: str
    claim_scope: str = "participant_specific_reference_progress_view"
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = LEARNER_PROGRESS_VIEW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("view_id", self.view_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("ontology_fingerprint", self.ontology_fingerprint),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != LEARNER_PROGRESS_VIEW_SCHEMA_VERSION:
            raise ValueError("unsupported M44 learner-progress view schema")
        ids = tuple(item.hypothesis_id for item in self.hypotheses)
        if len(set(ids)) != len(ids):
            raise ValueError("M44 hypotheses must be unique")
        ranks = tuple(
            item.priority_rank for item in self.hypotheses if item.priority_rank is not None
        )
        if ranks and ranks != tuple(range(1, len(ranks) + 1)):
            raise ValueError("M44 active priority ranks must be contiguous")
        if self.claim_scope != "participant_specific_reference_progress_view":
            raise ValueError("unknown M44 progress-view claim scope")
        if self.causal_effect != "not_established" or self.mastery != "not_established":
            raise ValueError("M44 cannot establish causality or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "learner_read_model_ref": self.learner_read_model_ref.to_dict(),
            "next_session_plan_ref": self.next_session_plan_ref.to_dict(),
            "ontology_fingerprint": self.ontology_fingerprint,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "created_at": self.created_at,
            "claim_scope": self.claim_scope,
            "causal_effect": self.causal_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class LearnerProgressReferenceSurface:
    surface_id: str
    fingerprint: str
    view_ref: EvidenceSynthesisReference
    html: str
    claim_scope: str = "local_reference_presentation_only"
    schema_version: str = LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("surface_id", self.surface_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("html", self.html)
        if self.schema_version != LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION:
            raise ValueError("unsupported M44 reference-surface schema")
        if self.claim_scope != "local_reference_presentation_only":
            raise ValueError("M44 surface cannot claim production UI authority")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "view_ref": self.view_ref.to_dict(),
            "html": self.html,
            "claim_scope": self.claim_scope,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def _validate_sources(
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    next_session_plan: NextSessionPlan,
    acquisition_plans: tuple[EvidenceAcquisitionPlan, ...],
    intervention_candidate_sets: tuple[InterventionCandidateSet, ...],
    ontology: OntologyRegistry,
) -> None:
    read_ref = _read_model_ref(learner_read_model)
    if next_session_plan.participant_id != learner_read_model.participant_id:
        raise ValueError("M44 M36/M40 participant mismatch")
    if next_session_plan.learner_read_model_ref != read_ref:
        raise ValueError("M44 M36/M40 read-model identity mismatch")

    expected_syntheses = {
        (item.ref_id, item.fingerprint) for item in next_session_plan.synthesis_refs
    }
    actual_syntheses = {
        (item.synthesis_id, item.fingerprint) for item in evidence_syntheses
    }
    if len(actual_syntheses) != len(evidence_syntheses):
        raise ValueError("M44 M39 syntheses must be unique")
    if actual_syntheses != expected_syntheses:
        raise ValueError("M44 requires the exact M39 synthesis set referenced by M40")

    entry_by_id = {item.hypothesis_id: item for item in learner_read_model.hypotheses}
    proposal_by_id = {
        item.hypothesis_id: item for item in next_session_plan.candidates
    }
    for synthesis in evidence_syntheses:
        entry = entry_by_id.get(synthesis.hypothesis_revision_ref.hypothesis_id)
        if entry is None:
            raise ValueError("M44 M39 synthesis references unknown M36 hypothesis")
        if synthesis.participant_id != learner_read_model.participant_id:
            raise ValueError("M44 M39 synthesis participant mismatch")
        if synthesis.learner_read_model_ref != read_ref:
            raise ValueError("M44 M39/M36 read-model identity mismatch")
        if synthesis.hypothesis_revision_ref != entry.current_revision_ref:
            raise ValueError("M44 M39/M36 current-revision mismatch")
        if synthesis.statement != entry.statement:
            raise ValueError("M44 M39/M36 statement drift")
        if synthesis.scope_definition != entry.scope_definition:
            raise ValueError("M44 M39/M36 scope drift")

    plan_ref = _plan_ref(next_session_plan)
    seen_acquisition: set[str] = set()
    for acquisition in acquisition_plans:
        if acquisition.hypothesis_id in seen_acquisition:
            raise ValueError("M44 M43 plans must be unique per hypothesis")
        seen_acquisition.add(acquisition.hypothesis_id)
        proposal = proposal_by_id.get(acquisition.hypothesis_id)
        if proposal is None:
            raise ValueError("M44 M43 plan references unknown M40 hypothesis")
        if acquisition.participant_id != learner_read_model.participant_id:
            raise ValueError("M44 M43 participant mismatch")
        if acquisition.next_session_plan_ref != plan_ref:
            raise ValueError("M44 M43/M40 plan identity mismatch")
        if acquisition.proposal_ref != _proposal_ref(proposal):
            raise ValueError("M44 M43/M40 proposal identity mismatch")
        if acquisition.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
            raise ValueError("M44 M43/M40 current-revision mismatch")

    seen_matching: set[str] = set()
    for candidate_set in intervention_candidate_sets:
        if candidate_set.hypothesis_id in seen_matching:
            raise ValueError("M44 M41 sets must be unique per hypothesis")
        seen_matching.add(candidate_set.hypothesis_id)
        proposal = proposal_by_id.get(candidate_set.hypothesis_id)
        if proposal is None:
            raise ValueError("M44 M41 set references unknown M40 hypothesis")
        if candidate_set.participant_id != learner_read_model.participant_id:
            raise ValueError("M44 M41 participant mismatch")
        if candidate_set.next_session_plan_ref != plan_ref:
            raise ValueError("M44 M41/M40 plan identity mismatch")
        if candidate_set.proposal_ref != _proposal_ref(proposal):
            raise ValueError("M44 M41/M40 proposal identity mismatch")
        if candidate_set.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
            raise ValueError("M44 M41/M40 current-revision mismatch")
        if candidate_set.ontology_fingerprint != ontology.fingerprint:
            raise ValueError("M44 M41/ontology fingerprint mismatch")


def _concepts(
    ontology: OntologyRegistry,
    concept_ids: set[str],
) -> tuple[ProgressConcept, ...]:
    result: list[ProgressConcept] = []
    for concept_id in sorted(concept_ids):
        concept = ontology.get(concept_id)
        questions = (
            ()
            if concept.pedagogy is None
            else tuple(concept.pedagogy.recognition_questions)
        )
        result.append(
            ProgressConcept(
                concept_id=concept.id,
                preferred_name=concept.preferred_name,
                kind=concept.kind,
                recognition_questions=questions,
            )
        )
    return tuple(result)


def _progress_hypothesis(
    *,
    entry: LearnerHypothesisReadEntry,
    rank: int | None,
    proposal: NextSessionActionCandidate | None,
    synthesis: HypothesisEvidenceSynthesis | None,
    acquisition: EvidenceAcquisitionPlan | None,
    candidate_set: InterventionCandidateSet | None,
    ontology: OntologyRegistry,
) -> LearnerProgressHypothesis:
    concept_ids = set(entry.knowledge.concept_ids)
    if synthesis is not None:
        concept_ids.update(synthesis.concept_ids)
    if proposal is not None:
        concept_ids.update(proposal.concept_ids)
    if acquisition is not None:
        for item in acquisition.candidates:
            concept_ids.update(item.concept_ids)
    if candidate_set is not None:
        concept_ids.update(candidate_set.target_concept_ids)
        for item in candidate_set.ranked_candidates:
            concept_ids.update(item.target_concept_matches)
            concept_ids.update(item.reinforcement_matches)
            concept_ids.update(item.contraindication_matches)

    evidence_units = ()
    if synthesis is not None:
        evidence_units = tuple(
            ProgressEvidenceUnit(
                recurrence_unit_id=item.recurrence_unit_id,
                relation=item.relation,
                source_position_id=item.source_position_id,
                source_game_id=item.source_game_id,
                concept_ids=item.concept_ids,
            )
            for item in synthesis.units
        )

    acquisition_candidates = ()
    if acquisition is not None:
        acquisition_candidates = tuple(
            ProgressAcquisitionCandidate(
                candidate_kind=item.candidate_kind,
                origin=item.origin,
                source_position_id=item.source_position_id,
                source_game_id=item.source_game_id,
                semantic_coverage=item.semantic_coverage,
                concept_ids=item.concept_ids,
            )
            for item in acquisition.candidates
        )

    intervention_candidates = ()
    if candidate_set is not None:
        intervention_candidates = tuple(
            ProgressInterventionCandidate(
                intervention_ref=item.intervention_ref,
                status=item.status,
                target_concept_matches=item.target_concept_matches,
                reinforcement_matches=item.reinforcement_matches,
                training_mode_matches=item.training_mode_matches,
                contraindication_matches=item.contraindication_matches,
            )
            for item in candidate_set.ranked_candidates
        )

    return LearnerProgressHypothesis(
        hypothesis_id=entry.hypothesis_id,
        current_revision_ref=entry.current_revision_ref,
        priority_rank=rank,
        is_current_priority=rank == 1,
        statement=entry.statement,
        scope_definition=entry.scope_definition,
        lifecycle_state=entry.authority_lifecycle_state,
        m7_status=entry.m7_status,
        synthesis_ref=None if synthesis is None else _synthesis_ref(synthesis),
        status_reasons=() if synthesis is None else synthesis.status_reasons,
        evidence_counts=None if synthesis is None else synthesis.evidence_counts,
        evidence_units=evidence_units,
        concepts=_concepts(ontology, concept_ids),
        intervention_state=entry.intervention.state,
        selected_interventions=entry.intervention.selected_interventions,
        outcome_statuses=tuple(
            (item.evidence_kind, item.status) for item in entry.outcome_dimensions
        ),
        evidence_gaps=() if synthesis is None else synthesis.evidence_gaps,
        change_conditions=() if synthesis is None else synthesis.change_conditions,
        next_action=None if proposal is None else proposal.action,
        next_action_reasons=() if proposal is None else proposal.reasons,
        blocking_uncertainty=(
            () if proposal is None else proposal.blocking_uncertainty
        ),
        acquisition_ref=None if acquisition is None else _acquisition_ref(acquisition),
        acquisition_intent=None if acquisition is None else acquisition.intent,
        acquisition_candidates=acquisition_candidates,
        acquisition_gaps=() if acquisition is None else acquisition.search_gaps,
        intervention_candidate_set_ref=(
            None if candidate_set is None else _candidate_set_ref(candidate_set)
        ),
        intervention_candidates=intervention_candidates,
        matching_gaps=() if candidate_set is None else candidate_set.matching_gaps,
        unverified_prerequisites=(
            () if candidate_set is None else candidate_set.unverified_prerequisites
        ),
    )


def build_learner_progress_view(
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    next_session_plan: NextSessionPlan,
    ontology: OntologyRegistry,
    acquisition_plans: tuple[EvidenceAcquisitionPlan, ...] = (),
    intervention_candidate_sets: tuple[InterventionCandidateSet, ...] = (),
    created_at: str,
) -> LearnerProgressView:
    """Compose exact learner-intelligence sources into a presentation-only view."""
    _timestamp("created_at", created_at)
    _validate_sources(
        learner_read_model=learner_read_model,
        evidence_syntheses=evidence_syntheses,
        next_session_plan=next_session_plan,
        acquisition_plans=acquisition_plans,
        intervention_candidate_sets=intervention_candidate_sets,
        ontology=ontology,
    )
    synthesis_by_hypothesis = {
        item.hypothesis_revision_ref.hypothesis_id: item
        for item in evidence_syntheses
    }
    proposal_by_hypothesis = {
        item.hypothesis_id: item for item in next_session_plan.candidates
    }
    acquisition_by_hypothesis = {
        item.hypothesis_id: item for item in acquisition_plans
    }
    matching_by_hypothesis = {
        item.hypothesis_id: item for item in intervention_candidate_sets
    }
    rank_by_hypothesis = {
        item.hypothesis_id: index
        for index, item in enumerate(next_session_plan.candidates, start=1)
    }
    ordered_entries = tuple(
        sorted(
            learner_read_model.hypotheses,
            key=lambda item: (
                rank_by_hypothesis.get(item.hypothesis_id, 10**9),
                item.hypothesis_id,
            ),
        )
    )
    hypotheses = tuple(
        _progress_hypothesis(
            entry=entry,
            rank=rank_by_hypothesis.get(entry.hypothesis_id),
            proposal=proposal_by_hypothesis.get(entry.hypothesis_id),
            synthesis=synthesis_by_hypothesis.get(entry.hypothesis_id),
            acquisition=acquisition_by_hypothesis.get(entry.hypothesis_id),
            candidate_set=matching_by_hypothesis.get(entry.hypothesis_id),
            ontology=ontology,
        )
        for entry in ordered_entries
    )
    payload = {
        "schema_version": LEARNER_PROGRESS_VIEW_SCHEMA_VERSION,
        "participant_id": learner_read_model.participant_id,
        "learner_read_model_ref": _read_model_ref(learner_read_model).to_dict(),
        "next_session_plan_ref": _plan_ref(next_session_plan).to_dict(),
        "ontology_fingerprint": ontology.fingerprint,
        "hypotheses": [item.to_dict() for item in hypotheses],
        "created_at": created_at,
        "claim_scope": "participant_specific_reference_progress_view",
        "causal_effect": "not_established",
        "mastery": "not_established",
    }
    fingerprint = _digest(payload)
    return LearnerProgressView(
        view_id=f"learner_progress_view_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=learner_read_model.participant_id,
        learner_read_model_ref=_read_model_ref(learner_read_model),
        next_session_plan_ref=_plan_ref(next_session_plan),
        ontology_fingerprint=ontology.fingerprint,
        hypotheses=hypotheses,
        created_at=created_at,
    )


def validate_learner_progress_view(
    view: LearnerProgressView,
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    next_session_plan: NextSessionPlan,
    ontology: OntologyRegistry,
    acquisition_plans: tuple[EvidenceAcquisitionPlan, ...] = (),
    intervention_candidate_sets: tuple[InterventionCandidateSet, ...] = (),
) -> None:
    expected = build_learner_progress_view(
        learner_read_model=learner_read_model,
        evidence_syntheses=evidence_syntheses,
        next_session_plan=next_session_plan,
        ontology=ontology,
        acquisition_plans=acquisition_plans,
        intervention_candidate_sets=intervention_candidate_sets,
        created_at=view.created_at,
    )
    if expected != view:
        raise ValueError("M44 learner-progress view mismatch")


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _list_html(values: tuple[str, ...], *, empty: str) -> str:
    if not values:
        return f'<p class="muted">{_esc(empty)}</p>'
    items = "".join(f"<li>{_esc(value)}</li>" for value in values)
    return f"<ul>{items}</ul>"


def _concept_html(concepts: tuple[ProgressConcept, ...]) -> str:
    if not concepts:
        return '<p class="muted">Ontology context unavailable or not supplied.</p>'
    parts: list[str] = []
    for concept in concepts:
        questions = _list_html(
            concept.recognition_questions,
            empty="No recognition questions recorded.",
        )
        parts.append(
            '<article class="concept">'
            f"<h4>{_esc(concept.preferred_name)}</h4>"
            f'<p class="meta">{_esc(concept.concept_id)} · {_esc(concept.kind)}</p>'
            '<p class="label">Instructional recognition cues</p>'
            f"{questions}"
            "</article>"
        )
    return "".join(parts)


def _evidence_html(hypothesis: LearnerProgressHypothesis) -> str:
    counts = hypothesis.evidence_counts
    if counts is None:
        return '<p class="muted">M39 evidence synthesis unavailable.</p>'
    count_rows = (
        ("Support units", counts.support_unit_count),
        ("Independent support", counts.independent_support_count),
        ("Contradictions", counts.contradiction_unit_count),
        ("Successful counterexamples", counts.successful_counterexample_unit_count),
        ("Context exceptions", counts.context_exception_unit_count),
        ("Unclear", counts.unclear_unit_count),
        ("Mixed", counts.mixed_unit_count),
    )
    rows = "".join(
        f"<tr><th>{_esc(label)}</th><td>{value}</td></tr>"
        for label, value in count_rows
    )
    unit_items = "".join(
        "<li>"
        f"{_esc(item.relation)} — game {_esc(item.source_game_id)}, "
        f"position {_esc(item.source_position_id)}"
        "</li>"
        for item in hypothesis.evidence_units
    )
    units = (
        f"<ul>{unit_items}</ul>"
        if unit_items
        else '<p class="muted">No recurrence-unit details supplied in this synthesis.</p>'
    )
    return (
        f'<table class="evidence"><tbody>{rows}</tbody></table>'
        '<p class="label">Traceable recurrence units</p>'
        f"{units}"
    )


def _training_html(hypothesis: LearnerProgressHypothesis) -> str:
    selected = tuple(
        f"{item.intervention_key} (v{item.version})"
        for item in hypothesis.selected_interventions
    )
    selected_html = _list_html(
        selected,
        empty="No M9 selected intervention is represented in the current M36 state.",
    )
    outcomes = tuple(
        f"{kind}: {status}" for kind, status in hypothesis.outcome_statuses
    )
    outcomes_html = _list_html(
        outcomes,
        empty="No M10 outcome dimension is represented in the current M36 state.",
    )
    return (
        f'<p><strong>M9 state:</strong> {_esc(hypothesis.intervention_state)}</p>'
        '<p class="label">Selected interventions</p>'
        f"{selected_html}"
        '<p class="label">M10 practice / transfer state</p>'
        f"{outcomes_html}"
        '<p class="muted">Mastery is not established by this reference view.</p>'
    )


def _acquisition_html(hypothesis: LearnerProgressHypothesis) -> str:
    if hypothesis.acquisition_ref is None:
        return '<p class="muted">No M43 acquisition plan supplied.</p>'
    items = tuple(
        (
            f"{item.candidate_kind}: game {item.source_game_id}, "
            f"position {item.source_position_id}"
        )
        for item in hypothesis.acquisition_candidates
    )
    return (
        f'<p><strong>Intent:</strong> {_esc(hypothesis.acquisition_intent)}</p>'
        + _list_html(items, empty="No eligible M43 evidence candidates.")
        + '<p class="label">M43 gaps</p>'
        + _list_html(hypothesis.acquisition_gaps, empty="No M43 gaps recorded.")
    )


def _matching_html(hypothesis: LearnerProgressHypothesis) -> str:
    if hypothesis.intervention_candidate_set_ref is None:
        return '<p class="muted">No M41 intervention candidate set supplied.</p>'
    items = tuple(
        (
            f"{item.intervention_ref.intervention_key} "
            f"(v{item.intervention_ref.version}) — {item.status}"
        )
        for item in hypothesis.intervention_candidates
    )
    return (
        _list_html(items, empty="No M41 intervention candidates.")
        + '<p class="label">Unverified pedagogical prerequisites</p>'
        + _list_html(
            hypothesis.unverified_prerequisites,
            empty="No prerequisites recorded for the current match context.",
        )
        + '<p class="label">M41 gaps</p>'
        + _list_html(hypothesis.matching_gaps, empty="No M41 gaps recorded.")
        + '<p class="muted">M9 selection authority has not been exercised here.</p>'
    )


def render_learner_progress_html(view: LearnerProgressView) -> str:
    """Render deterministic escaped semantic HTML from an already-built M44 view."""
    if _digest(view.identity_payload()) != view.fingerprint:
        raise ValueError("M44 learner-progress view fingerprint mismatch")
    if view.view_id != f"learner_progress_view_{view.fingerprint[:20]}":
        raise ValueError("M44 learner-progress view identity mismatch")

    sections: list[str] = []
    for hypothesis in view.hypotheses:
        priority = (
            "Not ranked by the current M40 plan"
            if hypothesis.priority_rank is None
            else f"Priority {hypothesis.priority_rank}"
        )
        action = (
            "Unavailable"
            if hypothesis.next_action is None
            else hypothesis.next_action
        )
        sections.append(
            '<section class="hypothesis">'
            f"<h2>{_esc(priority)} — {_esc(hypothesis.statement)}</h2>"
            f'<p class="meta">Hypothesis {_esc(hypothesis.hypothesis_id)} · '
            f"lifecycle {_esc(hypothesis.lifecycle_state)}</p>"
            '<div class="grid">'
            '<article><h3>Current learner hypothesis</h3>'
            f"<p>{_esc(hypothesis.statement)}</p>"
            f'<p class="meta">Scope: {_esc(hypothesis.scope_definition)}</p>'
            f'<p><strong>M7C status:</strong> {_esc(hypothesis.m7_status or "unavailable")}</p>'
            '<p class="label">Why this status is represented</p>'
            f"{_list_html(hypothesis.status_reasons, empty='M39 synthesis unavailable.')}"
            "</article>"
            '<article><h3>Evidence</h3>'
            f"{_evidence_html(hypothesis)}"
            "</article>"
            '<article><h3>Chess concepts</h3>'
            f"{_concept_html(hypothesis.concepts)}"
            '<p class="muted">Ontology concepts describe chess semantics; they do not '
            "by themselves establish learner weakness.</p></article>"
            '<article><h3>Training / transfer</h3>'
            f"{_training_html(hypothesis)}"
            "</article>"
            '<article><h3>Uncertainty and change conditions</h3>'
            '<p class="label">Evidence gaps</p>'
            f"{_list_html(hypothesis.evidence_gaps, empty='No M39 gap recorded.')}"
            '<p class="label">What could change the current assessment</p>'
            f"{_list_html(hypothesis.change_conditions, empty='No M39 change condition supplied.')}"
            "</article>"
            '<article><h3>Next proposed action</h3>'
            f"<p><strong>{_esc(action)}</strong></p>"
            f"{_list_html(hypothesis.next_action_reasons, empty='No M40 action supplied.')}"
            '<p class="label">Blocking uncertainty</p>'
            f"{_list_html(hypothesis.blocking_uncertainty, empty='None recorded.')}"
            '<p class="muted">M40 is proposal-only; this surface does not authorize execution.</p>'
            "</article>"
            '<article><h3>Challenge / control candidates</h3>'
            f"{_acquisition_html(hypothesis)}"
            "</article>"
            '<article><h3>Training candidates</h3>'
            f"{_matching_html(hypothesis)}"
            "</article>"
            "</div>"
            "</section>"
        )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Chess Mentor Engine — Learner Progress</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto;"
        "padding:2rem;line-height:1.5}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));"
        "gap:1rem}.hypothesis{border-top:3px solid #333;margin-top:2rem;padding-top:1rem}"
        "article{border:1px solid #bbb;border-radius:.5rem;padding:1rem}"
        ".meta,.muted{color:#555}.label{font-weight:600;margin-bottom:.25rem}"
        "table{border-collapse:collapse;width:100%}th,td{text-align:left;"
        "border-bottom:1px solid #ddd;padding:.25rem}code{word-break:break-all}"
        "</style></head><body>"
        "<header><h1>Chess Mentor Engine — Learner Progress</h1>"
        f"<p>Participant: <strong>{_esc(view.participant_id)}</strong></p>"
        '<p class="muted">Local deterministic reference surface. Evidence, learner '
        "hypotheses, ontology semantics, pedagogical candidates, and action policy "
        "remain separate authority layers.</p></header>"
        + "".join(sections)
        + '<footer><p class="muted">Causal effect: not established. Mastery: not '
        "established. This surface creates no new learner-state or execution "
        "authority.</p></footer></body></html>"
    )


def _view_ref(view: LearnerProgressView) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_progress_view",
        view.view_id,
        view.fingerprint,
    )


def build_learner_progress_reference_surface(
    view: LearnerProgressView,
) -> LearnerProgressReferenceSurface:
    html_text = render_learner_progress_html(view)
    payload = {
        "schema_version": LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION,
        "view_ref": _view_ref(view).to_dict(),
        "html": html_text,
        "claim_scope": "local_reference_presentation_only",
    }
    fingerprint = _digest(payload)
    return LearnerProgressReferenceSurface(
        surface_id=f"learner_progress_surface_{fingerprint[:20]}",
        fingerprint=fingerprint,
        view_ref=_view_ref(view),
        html=html_text,
    )


def validate_learner_progress_reference_surface(
    surface: LearnerProgressReferenceSurface,
    *,
    view: LearnerProgressView,
) -> None:
    expected = build_learner_progress_reference_surface(view)
    if expected != surface:
        raise ValueError("M44 learner-progress reference surface mismatch")
