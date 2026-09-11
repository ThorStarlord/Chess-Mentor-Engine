"""Deterministic participant-scoped M36 learner-state read model.

M36 is a projection only. It combines already-qualified M7/M9/M10/M11 state and
optional K7 chess-knowledge context without mutating learner state, selecting new
training, inferring causality, or establishing mastery.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess_knowledge.learner_projection import (
    HypothesisKnowledgeProjection,
)
from chess_mentor_engine.learning import HypothesisRevision, HypothesisRevisionRef
from chess_mentor_engine.training import (
    InterventionSelectionDecision,
    TrainingInterventionRef,
)

from .model import (
    LearnerStateSnapshot,
    LongitudinalReference,
    LongitudinalStateError,
    OutcomeDimensionState,
    fingerprint,
    timestamp,
)

LEARNER_STATE_READ_MODEL_SCHEMA_VERSION = "m36.learner-state-read-model.v1"
SelectionSummaryState: TypeAlias = Literal["none", "selected", "mixed"]


def _nonempty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LongitudinalStateError(f"{name} must not be empty")


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


@dataclass(frozen=True, slots=True)
class LearnerReadReference:
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
class LearnerInterventionSummary:
    state: SelectionSummaryState
    selected_interventions: tuple[TrainingInterventionRef, ...]
    decision_refs: tuple[LearnerReadReference, ...]
    decision_counts: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        if self.state not in {"none", "selected", "mixed"}:
            raise LongitudinalStateError("unknown M36 intervention summary state")
        ids = tuple(item.intervention_id for item in self.selected_interventions)
        if len(set(ids)) != len(ids):
            raise LongitudinalStateError("selected intervention refs must be unique")
        ref_ids = tuple(item.ref_id for item in self.decision_refs)
        if len(set(ref_ids)) != len(ref_ids):
            raise LongitudinalStateError("selection decision refs must be unique")
        labels = tuple(label for label, _ in self.decision_counts)
        if len(set(labels)) != len(labels):
            raise LongitudinalStateError(
                "selection decision count labels must be unique"
            )
        if any(not label or count < 1 for label, count in self.decision_counts):
            raise LongitudinalStateError(
                "selection decision counts must be positive"
            )
        if sum(count for _, count in self.decision_counts) != len(self.decision_refs):
            raise LongitudinalStateError("selection decision counts must match refs")
        if self.state == "none" and self.selected_interventions:
            raise LongitudinalStateError(
                "none intervention state cannot cite selections"
            )
        if self.state == "selected" and not self.selected_interventions:
            raise LongitudinalStateError(
                "selected intervention state requires a selection"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "selected_interventions": [
                item.to_dict() for item in self.selected_interventions
            ],
            "decision_refs": [item.to_dict() for item in self.decision_refs],
            "decision_counts": [list(item) for item in self.decision_counts],
        }


@dataclass(frozen=True, slots=True)
class LearnerKnowledgeSummary:
    projection_ref: LearnerReadReference | None
    concept_ids: tuple[str, ...]
    covered_recurrence_unit_count: int
    uncovered_recurrence_unit_count: int

    def __post_init__(self) -> None:
        if len(set(self.concept_ids)) != len(self.concept_ids):
            raise LongitudinalStateError("knowledge concept IDs must be unique")
        if any(not item for item in self.concept_ids):
            raise LongitudinalStateError("knowledge concept IDs must not be empty")
        if self.covered_recurrence_unit_count < 0:
            raise LongitudinalStateError(
                "covered recurrence count must not be negative"
            )
        if self.uncovered_recurrence_unit_count < 0:
            raise LongitudinalStateError(
                "uncovered recurrence count must not be negative"
            )
        if self.projection_ref is None and (
            self.concept_ids or self.covered_recurrence_unit_count
        ):
            raise LongitudinalStateError(
                "knowledge content requires an exact K7 projection reference"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_ref": (
                None if self.projection_ref is None else self.projection_ref.to_dict()
            ),
            "concept_ids": list(self.concept_ids),
            "covered_recurrence_unit_count": self.covered_recurrence_unit_count,
            "uncovered_recurrence_unit_count": self.uncovered_recurrence_unit_count,
        }


@dataclass(frozen=True, slots=True)
class LearnerHypothesisReadEntry:
    hypothesis_id: str
    hypothesis_fingerprint: str
    current_revision_ref: HypothesisRevisionRef
    statement: str
    scope_definition: str
    unresolved_alternative_notes: tuple[str, ...]
    authority_lifecycle_state: str
    m7_status: str | None
    m7_assessment_ref: LearnerReadReference | None
    outcome_dimensions: tuple[OutcomeDimensionState, ...]
    intervention: LearnerInterventionSummary
    knowledge: LearnerKnowledgeSummary

    def __post_init__(self) -> None:
        for name, value in (
            ("hypothesis_id", self.hypothesis_id),
            ("hypothesis_fingerprint", self.hypothesis_fingerprint),
            ("statement", self.statement),
            ("scope_definition", self.scope_definition),
            ("authority_lifecycle_state", self.authority_lifecycle_state),
        ):
            _nonempty(name, value)
        if self.current_revision_ref.hypothesis_id != self.hypothesis_id:
            raise LongitudinalStateError("M36 hypothesis/revision mismatch")
        if self.authority_lifecycle_state not in {"active", "retired", "superseded"}:
            raise LongitudinalStateError(
                "unknown M36 hypothesis lifecycle state"
            )
        if (self.m7_status is None) != (self.m7_assessment_ref is None):
            raise LongitudinalStateError(
                "M36 M7 status/reference must appear together"
            )
        if len(set(self.unresolved_alternative_notes)) != len(
            self.unresolved_alternative_notes
        ):
            raise LongitudinalStateError("unresolved alternatives must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_fingerprint": self.hypothesis_fingerprint,
            "current_revision_ref": self.current_revision_ref.to_dict(),
            "statement": self.statement,
            "scope_definition": self.scope_definition,
            "unresolved_alternative_notes": list(self.unresolved_alternative_notes),
            "authority_lifecycle_state": self.authority_lifecycle_state,
            "m7_status": self.m7_status,
            "m7_assessment_ref": (
                None
                if self.m7_assessment_ref is None
                else self.m7_assessment_ref.to_dict()
            ),
            "outcome_dimensions": [asdict(item) for item in self.outcome_dimensions],
            "intervention": self.intervention.to_dict(),
            "knowledge": self.knowledge.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class LearnerStateReadModel:
    read_model_id: str
    fingerprint: str
    participant_id: str
    source_snapshot_ref: LongitudinalReference
    hypotheses: tuple[LearnerHypothesisReadEntry, ...]
    created_at: str
    claim_scope: str = "participant_specific_deterministic_read_model"
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = LEARNER_STATE_READ_MODEL_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("read_model_id", self.read_model_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("participant_id", self.participant_id)
        timestamp(self.created_at)
        if self.source_snapshot_ref.kind != "learner_state_snapshot":
            raise LongitudinalStateError(
                "M36 requires an exact M11 snapshot reference"
            )
        ids = tuple(item.hypothesis_id for item in self.hypotheses)
        if ids != tuple(sorted(ids)) or len(set(ids)) != len(ids):
            raise LongitudinalStateError("M36 hypotheses must be unique and sorted")
        if self.claim_scope != "participant_specific_deterministic_read_model":
            raise LongitudinalStateError("unknown M36 claim scope")
        if self.causal_effect != "not_established" or self.mastery != "not_established":
            raise LongitudinalStateError("M36 cannot establish causality or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "source_snapshot_ref": {
                "kind": self.source_snapshot_ref.kind,
                "ref_id": self.source_snapshot_ref.ref_id,
                "fingerprint": self.source_snapshot_ref.fingerprint,
            },
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "created_at": self.created_at,
            "claim_scope": self.claim_scope,
            "causal_effect": self.causal_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "read_model_id": self.read_model_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def _intervention_summary(
    revision_ref: HypothesisRevisionRef,
    participant_id: str,
    decisions: tuple[InterventionSelectionDecision, ...],
) -> LearnerInterventionSummary:
    relevant = tuple(
        item for item in decisions if item.hypothesis_revision_ref == revision_ref
    )
    for item in relevant:
        if item.participant_id != participant_id:
            raise LongitudinalStateError("M36 intervention participant mismatch")
    ids = tuple(item.selection_id for item in relevant)
    if len(set(ids)) != len(ids):
        raise LongitudinalStateError("M36 intervention selections must be unique")

    selected: dict[str, TrainingInterventionRef] = {}
    for item in relevant:
        if item.decision == "selected" and item.selected_intervention_ref is not None:
            selected[item.selected_intervention_ref.intervention_id] = (
                item.selected_intervention_ref
            )
    counts = tuple(sorted(Counter(item.decision for item in relevant).items()))
    selected_refs = tuple(selected[key] for key in sorted(selected))
    if not relevant:
        state: SelectionSummaryState = "none"
    elif selected_refs and all(item.decision == "selected" for item in relevant):
        state = "selected"
    else:
        state = "mixed"

    return LearnerInterventionSummary(
        state=state,
        selected_interventions=selected_refs,
        decision_refs=tuple(
            LearnerReadReference(
                kind="intervention_selection_decision",
                ref_id=item.selection_id,
                fingerprint=item.fingerprint,
            )
            for item in sorted(relevant, key=lambda value: value.selection_id)
        ),
        decision_counts=counts,
    )


def _knowledge_summary(
    revision_ref: HypothesisRevisionRef,
    projection_by_revision: dict[str, HypothesisKnowledgeProjection],
) -> LearnerKnowledgeSummary:
    projection = projection_by_revision.get(revision_ref.revision_id)
    if projection is None:
        return LearnerKnowledgeSummary(None, (), 0, 0)
    if projection.hypothesis_revision_ref != revision_ref:
        raise LongitudinalStateError("M36 K7 projection revision mismatch")
    return LearnerKnowledgeSummary(
        projection_ref=LearnerReadReference(
            kind="hypothesis_knowledge_projection",
            ref_id=projection.projection_id,
            fingerprint=projection.fingerprint,
        ),
        concept_ids=tuple(
            sorted(item.concept_id for item in projection.concept_summaries)
        ),
        covered_recurrence_unit_count=len(projection.covered_recurrence_unit_ids),
        uncovered_recurrence_unit_count=len(projection.uncovered_recurrence_unit_ids),
    )


def build_learner_state_read_model(
    *,
    snapshot: LearnerStateSnapshot,
    revisions: tuple[HypothesisRevision, ...],
    intervention_decisions: tuple[InterventionSelectionDecision, ...] = (),
    knowledge_projections: tuple[HypothesisKnowledgeProjection, ...] = (),
    created_at: str,
) -> LearnerStateReadModel:
    """Build a deterministic read-only current learner summary from qualified inputs."""
    timestamp(created_at)
    _nonempty("snapshot.participant_id", snapshot.participant_id)

    revisions_by_id = {item.revision_id: item for item in revisions}
    if len(revisions_by_id) != len(revisions):
        raise LongitudinalStateError("M36 revisions must be unique")
    projection_by_revision = {
        item.hypothesis_revision_ref.revision_id: item
        for item in knowledge_projections
    }
    if len(projection_by_revision) != len(knowledge_projections):
        raise LongitudinalStateError("M36 K7 projections must be unique per revision")

    snapshot_ref = LongitudinalReference(
        "learner_state_snapshot", snapshot.record_id, snapshot.fingerprint
    )
    entries: list[LearnerHypothesisReadEntry] = []
    for trajectory in snapshot.trajectories:
        revision = revisions_by_id.get(trajectory.current_revision_ref.revision_id)
        if revision is None:
            raise LongitudinalStateError("M36 missing current hypothesis revision")
        if _revision_ref(revision) != trajectory.current_revision_ref:
            raise LongitudinalStateError("M36 revision identity mismatch")
        if trajectory.hypothesis_ref.participant_id != snapshot.participant_id:
            raise LongitudinalStateError("M36 hypothesis participant mismatch")
        m7_ref = (
            None
            if trajectory.latest_m7_assessment_ref is None
            else LearnerReadReference(
                kind="hypothesis_assessment",
                ref_id=trajectory.latest_m7_assessment_ref.hypothesis_assessment_id,
                fingerprint=trajectory.latest_m7_assessment_ref.fingerprint,
            )
        )
        entries.append(
            LearnerHypothesisReadEntry(
                hypothesis_id=trajectory.hypothesis_ref.hypothesis_id,
                hypothesis_fingerprint=trajectory.hypothesis_ref.fingerprint,
                current_revision_ref=trajectory.current_revision_ref,
                statement=revision.statement,
                scope_definition=revision.scope_definition,
                unresolved_alternative_notes=revision.unresolved_alternative_notes,
                authority_lifecycle_state=trajectory.authority_lifecycle_state,
                m7_status=trajectory.latest_m7_status,
                m7_assessment_ref=m7_ref,
                outcome_dimensions=trajectory.current_outcome_dimensions,
                intervention=_intervention_summary(
                    trajectory.current_revision_ref,
                    snapshot.participant_id,
                    intervention_decisions,
                ),
                knowledge=_knowledge_summary(
                    trajectory.current_revision_ref,
                    projection_by_revision,
                ),
            )
        )

    used_revision_ids = {item.current_revision_ref.revision_id for item in entries}
    if set(revisions_by_id) - used_revision_ids:
        raise LongitudinalStateError(
            "M36 revisions include non-current hypothesis data"
        )
    for decision in intervention_decisions:
        if decision.hypothesis_revision_ref.revision_id not in used_revision_ids:
            raise LongitudinalStateError(
                "M36 selection references non-current revision"
            )
    for projection in knowledge_projections:
        if projection.hypothesis_revision_ref.revision_id not in used_revision_ids:
            raise LongitudinalStateError(
                "M36 K7 projection references non-current revision"
            )

    ordered = tuple(sorted(entries, key=lambda item: item.hypothesis_id))
    payload = {
        "schema_version": LEARNER_STATE_READ_MODEL_SCHEMA_VERSION,
        "participant_id": snapshot.participant_id,
        "source_snapshot_ref": {
            "kind": snapshot_ref.kind,
            "ref_id": snapshot_ref.ref_id,
            "fingerprint": snapshot_ref.fingerprint,
        },
        "hypotheses": [item.to_dict() for item in ordered],
        "created_at": created_at,
        "claim_scope": "participant_specific_deterministic_read_model",
        "causal_effect": "not_established",
        "mastery": "not_established",
    }
    digest = fingerprint(payload)
    return LearnerStateReadModel(
        read_model_id=f"learner_state_read_model_{digest[:20]}",
        fingerprint=digest,
        participant_id=snapshot.participant_id,
        source_snapshot_ref=snapshot_ref,
        hypotheses=ordered,
        created_at=created_at,
    )


def validate_learner_state_read_model(
    read_model: LearnerStateReadModel,
    *,
    snapshot: LearnerStateSnapshot,
    revisions: tuple[HypothesisRevision, ...],
    intervention_decisions: tuple[InterventionSelectionDecision, ...] = (),
    knowledge_projections: tuple[HypothesisKnowledgeProjection, ...] = (),
) -> None:
    expected = build_learner_state_read_model(
        snapshot=snapshot,
        revisions=revisions,
        intervention_decisions=intervention_decisions,
        knowledge_projections=knowledge_projections,
        created_at=read_model.created_at,
    )
    if read_model != expected:
        raise LongitudinalStateError("M36 learner-state read model mismatch")
