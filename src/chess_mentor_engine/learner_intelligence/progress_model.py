"""M44 deterministic learner-progress presentation model."""

from __future__ import annotations

import hashlib
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


def learner_read_model_ref(
    read_model: LearnerStateReadModel,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_state_read_model",
        read_model.read_model_id,
        read_model.fingerprint,
    )


def next_session_plan_ref(plan: NextSessionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_plan",
        plan.plan_id,
        plan.fingerprint,
    )


def next_session_proposal_ref(
    proposal: NextSessionActionCandidate,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_action_candidate",
        (
            f"{proposal.hypothesis_id}:"
            f"{proposal.hypothesis_revision_ref.revision_id}:{proposal.action}"
        ),
        _digest(proposal.to_dict()),
    )


def evidence_synthesis_ref(
    synthesis: HypothesisEvidenceSynthesis,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "hypothesis_evidence_synthesis",
        synthesis.synthesis_id,
        synthesis.fingerprint,
    )


def evidence_acquisition_ref(
    plan: EvidenceAcquisitionPlan,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "evidence_acquisition_plan",
        plan.acquisition_plan_id,
        plan.fingerprint,
    )


def intervention_candidate_set_ref(
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
        for name, value in (
            ("hypothesis_id", self.hypothesis_id),
            ("statement", self.statement),
            ("scope_definition", self.scope_definition),
            ("lifecycle_state", self.lifecycle_state),
        ):
            _nonempty(name, value)
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
        outcome_kinds = tuple(kind for kind, _ in self.outcome_statuses)
        if len(set(outcome_kinds)) != len(outcome_kinds):
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
                None
                if self.evidence_counts is None
                else self.evidence_counts.to_dict()
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
                None
                if self.acquisition_ref is None
                else self.acquisition_ref.to_dict()
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
            item.priority_rank
            for item in self.hypotheses
            if item.priority_rank is not None
        )
        if ranks and ranks != tuple(range(1, len(ranks) + 1)):
            raise ValueError("M44 active priority ranks must be contiguous")
        if self.claim_scope != "participant_specific_reference_progress_view":
            raise ValueError("unknown M44 progress-view claim scope")
        if self.causal_effect != "not_established":
            raise ValueError("M44 cannot establish causal effect")
        if self.mastery != "not_established":
            raise ValueError("M44 cannot establish mastery")

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


def _validate_sources(
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    next_session_plan: NextSessionPlan,
    acquisition_plans: tuple[EvidenceAcquisitionPlan, ...],
    intervention_candidate_sets: tuple[InterventionCandidateSet, ...],
    ontology: OntologyRegistry,
) -> None:
    read_ref = learner_read_model_ref(learner_read_model)
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

    entry_by_id = {
        item.hypothesis_id: item for item in learner_read_model.hypotheses
    }
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

    plan_ref = next_session_plan_ref(next_session_plan)
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
        if acquisition.proposal_ref != next_session_proposal_ref(proposal):
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
        if candidate_set.proposal_ref != next_session_proposal_ref(proposal):
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


def _evidence_units(
    synthesis: HypothesisEvidenceSynthesis | None,
) -> tuple[ProgressEvidenceUnit, ...]:
    if synthesis is None:
        return ()
    return tuple(
        ProgressEvidenceUnit(
            recurrence_unit_id=item.recurrence_unit_id,
            relation=item.relation,
            source_position_id=item.source_position_id,
            source_game_id=item.source_game_id,
            concept_ids=item.concept_ids,
        )
        for item in synthesis.units
    )


def _acquisition_candidates(
    acquisition: EvidenceAcquisitionPlan | None,
) -> tuple[ProgressAcquisitionCandidate, ...]:
    if acquisition is None:
        return ()
    return tuple(
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


def _intervention_candidates(
    candidate_set: InterventionCandidateSet | None,
) -> tuple[ProgressInterventionCandidate, ...]:
    if candidate_set is None:
        return ()
    return tuple(
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

    return LearnerProgressHypothesis(
        hypothesis_id=entry.hypothesis_id,
        current_revision_ref=entry.current_revision_ref,
        priority_rank=rank,
        is_current_priority=rank == 1,
        statement=entry.statement,
        scope_definition=entry.scope_definition,
        lifecycle_state=entry.authority_lifecycle_state,
        m7_status=entry.m7_status,
        synthesis_ref=(
            None if synthesis is None else evidence_synthesis_ref(synthesis)
        ),
        status_reasons=() if synthesis is None else synthesis.status_reasons,
        evidence_counts=None if synthesis is None else synthesis.evidence_counts,
        evidence_units=_evidence_units(synthesis),
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
        acquisition_ref=(
            None if acquisition is None else evidence_acquisition_ref(acquisition)
        ),
        acquisition_intent=None if acquisition is None else acquisition.intent,
        acquisition_candidates=_acquisition_candidates(acquisition),
        acquisition_gaps=() if acquisition is None else acquisition.search_gaps,
        intervention_candidate_set_ref=(
            None
            if candidate_set is None
            else intervention_candidate_set_ref(candidate_set)
        ),
        intervention_candidates=_intervention_candidates(candidate_set),
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
        "learner_read_model_ref": learner_read_model_ref(
            learner_read_model
        ).to_dict(),
        "next_session_plan_ref": next_session_plan_ref(next_session_plan).to_dict(),
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
        learner_read_model_ref=learner_read_model_ref(learner_read_model),
        next_session_plan_ref=next_session_plan_ref(next_session_plan),
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
