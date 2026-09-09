"""Immutable records for bounded M9 training-intervention selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.learning import HypothesisRevisionRef

TrainingContentActorKind: TypeAlias = Literal["human", "model", "template"]
InterventionMappingActorKind: TypeAlias = Literal["human", "model"]
ExercisePositionSource: TypeAlias = Literal[
    "historical_position",
    "fresh_position",
    "mixed",
]
InterventionApplicability: TypeAlias = Literal[
    "applicable",
    "not_applicable",
    "unclear",
]
InterventionSelectionDecisionKind: TypeAlias = Literal[
    "selected",
    "ineligible",
    "unclear",
]

_CONTENT_ACTORS = frozenset({"human", "model", "template"})
_MAPPING_ACTORS = frozenset({"human", "model"})
_POSITION_SOURCES = frozenset(
    {"historical_position", "fresh_position", "mixed"}
)
_APPLICABILITY = frozenset({"applicable", "not_applicable", "unclear"})
_SELECTION_DECISIONS = frozenset({"selected", "ineligible", "unclear"})


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


def _require_unique_strings(name: str, values: tuple[str, ...]) -> None:
    if any(not value for value in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")


@dataclass(frozen=True, slots=True)
class TrainingContentProvenance:
    """Authorship provenance for an exercise or intervention definition."""

    actor_kind: TrainingContentActorKind
    actor_id: str
    actor_version: str
    instruction_fingerprint: str
    run_id: str | None = None

    def __post_init__(self) -> None:
        if self.actor_kind not in _CONTENT_ACTORS:
            raise ValueError("unknown training content actor kind")
        for name, value in (
            ("actor_id", self.actor_id),
            ("actor_version", self.actor_version),
            ("instruction_fingerprint", self.instruction_fingerprint),
        ):
            _require_nonempty(name, value)
        if self.run_id is not None:
            _require_nonempty("run_id", self.run_id)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "actor_kind": self.actor_kind,
            "actor_id": self.actor_id,
            "actor_version": self.actor_version,
            "instruction_fingerprint": self.instruction_fingerprint,
            "run_id": self.run_id,
        }


@dataclass(frozen=True, slots=True)
class InterventionMappingProvenance:
    """Human/model provenance for participant-specific pedagogical applicability."""

    actor_kind: InterventionMappingActorKind
    actor_id: str
    actor_version: str
    instruction_fingerprint: str
    run_id: str

    def __post_init__(self) -> None:
        if self.actor_kind not in _MAPPING_ACTORS:
            raise ValueError("unknown intervention mapping actor kind")
        for name, value in (
            ("actor_id", self.actor_id),
            ("actor_version", self.actor_version),
            ("instruction_fingerprint", self.instruction_fingerprint),
            ("run_id", self.run_id),
        ):
            _require_nonempty(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "actor_kind": self.actor_kind,
            "actor_id": self.actor_id,
            "actor_version": self.actor_version,
            "instruction_fingerprint": self.instruction_fingerprint,
            "run_id": self.run_id,
        }


@dataclass(frozen=True, slots=True)
class ExerciseDefinition:
    """Versioned inspectable exercise instructions without mastery semantics."""

    exercise_id: str
    fingerprint: str
    exercise_key: str
    version: str
    title: str
    instructions: str
    position_source: ExercisePositionSource
    response_schema: tuple[str, ...]
    completion_evidence_schema: tuple[str, ...]
    duration_hint_minutes: int | None
    provenance: TrainingContentProvenance

    def __post_init__(self) -> None:
        for name, value in (
            ("exercise_id", self.exercise_id),
            ("fingerprint", self.fingerprint),
            ("exercise_key", self.exercise_key),
            ("version", self.version),
            ("title", self.title),
            ("instructions", self.instructions),
        ):
            _require_nonempty(name, value)
        if self.position_source not in _POSITION_SOURCES:
            raise ValueError("unknown exercise position source")
        if not self.response_schema:
            raise ValueError("response_schema must not be empty")
        if not self.completion_evidence_schema:
            raise ValueError("completion_evidence_schema must not be empty")
        _require_unique_strings("response_schema", self.response_schema)
        _require_unique_strings(
            "completion_evidence_schema",
            self.completion_evidence_schema,
        )
        if self.duration_hint_minutes is not None:
            if self.duration_hint_minutes <= 0:
                raise ValueError("duration_hint_minutes must be positive")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "exercise_key": self.exercise_key,
            "version": self.version,
            "title": self.title,
            "instructions": self.instructions,
            "position_source": self.position_source,
            "response_schema": list(self.response_schema),
            "completion_evidence_schema": list(
                self.completion_evidence_schema
            ),
            "duration_hint_minutes": self.duration_hint_minutes,
            "provenance": self.provenance.to_dict(),
        }
        if include_identity:
            payload["exercise_id"] = self.exercise_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class TrainingInterventionRef:
    """Exact reference to one versioned intervention definition."""

    intervention_id: str
    intervention_key: str
    version: str
    fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("intervention_id", self.intervention_id),
            ("intervention_key", self.intervention_key),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _require_nonempty(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "intervention_id": self.intervention_id,
            "intervention_key": self.intervention_key,
            "version": self.version,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class TrainingInterventionDefinition:
    """Versioned training prescription assembled from defined exercises."""

    intervention_id: str
    fingerprint: str
    intervention_key: str
    version: str
    title: str
    target_behavior: str
    rationale: str
    exercises: tuple[ExerciseDefinition, ...]
    dosage_guidance: str
    exclusion_notes: tuple[str, ...]
    provenance: TrainingContentProvenance

    def __post_init__(self) -> None:
        for name, value in (
            ("intervention_id", self.intervention_id),
            ("fingerprint", self.fingerprint),
            ("intervention_key", self.intervention_key),
            ("version", self.version),
            ("title", self.title),
            ("target_behavior", self.target_behavior),
            ("rationale", self.rationale),
            ("dosage_guidance", self.dosage_guidance),
        ):
            _require_nonempty(name, value)
        if not self.exercises:
            raise ValueError("training intervention requires at least one exercise")
        exercise_keys = tuple(item.exercise_key for item in self.exercises)
        if len(set(exercise_keys)) != len(exercise_keys):
            raise ValueError("intervention exercise keys must be unique")
        _require_unique_strings("exclusion_notes", self.exclusion_notes)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "intervention_key": self.intervention_key,
            "version": self.version,
            "title": self.title,
            "target_behavior": self.target_behavior,
            "rationale": self.rationale,
            "exercises": [item.to_dict() for item in self.exercises],
            "dosage_guidance": self.dosage_guidance,
            "exclusion_notes": list(self.exclusion_notes),
            "provenance": self.provenance.to_dict(),
        }
        if include_identity:
            payload["intervention_id"] = self.intervention_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class InterventionRegistry:
    """Immutable registry snapshot with one current version per intervention key."""

    registry_id: str
    fingerprint: str
    version: str
    interventions: tuple[TrainingInterventionDefinition, ...]
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("registry_id", self.registry_id),
            ("fingerprint", self.fingerprint),
            ("version", self.version),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if not self.interventions:
            raise ValueError("intervention registry must not be empty")
        keys = tuple(item.intervention_key for item in self.interventions)
        ids = tuple(item.intervention_id for item in self.interventions)
        if len(set(keys)) != len(keys):
            raise ValueError("registry intervention keys must be unique")
        if len(set(ids)) != len(ids):
            raise ValueError("registry intervention IDs must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "version": self.version,
            "interventions": [item.to_dict() for item in self.interventions],
            "created_at": self.created_at,
        }
        if include_identity:
            payload["registry_id"] = self.registry_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisInterventionMappingRef:
    """Exact reference to one participant-specific M9 applicability judgment."""

    mapping_id: str
    fingerprint: str
    applicability: InterventionApplicability

    def __post_init__(self) -> None:
        _require_nonempty("mapping_id", self.mapping_id)
        _require_nonempty("fingerprint", self.fingerprint)
        if self.applicability not in _APPLICABILITY:
            raise ValueError("unknown intervention applicability")

    def to_dict(self) -> dict[str, str]:
        return {
            "mapping_id": self.mapping_id,
            "fingerprint": self.fingerprint,
            "applicability": self.applicability,
        }


@dataclass(frozen=True, slots=True)
class HypothesisInterventionMapping:
    """Explicit bridge from one current M7 revision to one intervention."""

    mapping_id: str
    fingerprint: str
    participant_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    intervention_ref: TrainingInterventionRef
    applicability: InterventionApplicability
    rationale: str
    uncertainty_notes: tuple[str, ...]
    provenance: InterventionMappingProvenance
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("mapping_id", self.mapping_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("rationale", self.rationale),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.applicability not in _APPLICABILITY:
            raise ValueError("unknown intervention applicability")
        _require_unique_strings("uncertainty_notes", self.uncertainty_notes)
        if self.applicability == "unclear" and not self.uncertainty_notes:
            raise ValueError("unclear mapping requires uncertainty notes")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "intervention_ref": self.intervention_ref.to_dict(),
            "applicability": self.applicability,
            "rationale": self.rationale,
            "uncertainty_notes": list(self.uncertainty_notes),
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["mapping_id"] = self.mapping_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class InterventionSelectionPolicyRef:
    """Exact material identity for one bounded M9 selection policy."""

    policy_id: str
    version: str
    fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _require_nonempty(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class InterventionSelectionPolicy:
    """Versioned M9 gate from qualified M7 state to one intervention selection."""

    policy_id: str
    version: str
    policy_fingerprint: str
    required_hypothesis_status: Literal["supported_recurrence"]
    require_active_current: Literal[True]
    mapping_rule: Literal["single_applicable_mapping"]
    claim_scope: Literal["participant_specific_intervention_selection"] = (
        "participant_specific_intervention_selection"
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("policy_fingerprint", self.policy_fingerprint),
        ):
            _require_nonempty(name, value)
        if self.required_hypothesis_status != "supported_recurrence":
            raise ValueError("M9 v1 requires supported_recurrence")
        if self.require_active_current is not True:
            raise ValueError("M9 v1 requires active current hypothesis state")
        if self.mapping_rule != "single_applicable_mapping":
            raise ValueError("unknown M9 mapping rule")
        if self.claim_scope != "participant_specific_intervention_selection":
            raise ValueError("unknown M9 claim scope")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "policy_id": self.policy_id,
            "version": self.version,
            "required_hypothesis_status": self.required_hypothesis_status,
            "require_active_current": self.require_active_current,
            "mapping_rule": self.mapping_rule,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["policy_fingerprint"] = self.policy_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class InterventionSelectionDecision:
    """Deterministic M9 decision; selection is not an effectiveness claim."""

    selection_id: str
    fingerprint: str
    participant_id: str
    ledger_snapshot_id: str
    ledger_snapshot_fingerprint: str
    hypothesis_revision_ref: HypothesisRevisionRef
    registry_id: str
    registry_fingerprint: str
    policy_ref: InterventionSelectionPolicyRef
    mapping_refs: tuple[HypothesisInterventionMappingRef, ...]
    decision: InterventionSelectionDecisionKind
    selected_intervention_ref: TrainingInterventionRef | None
    decision_reasons: tuple[str, ...]
    created_at: str
    claim_scope: Literal["participant_specific_intervention_selection"] = (
        "participant_specific_intervention_selection"
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("selection_id", self.selection_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("ledger_snapshot_id", self.ledger_snapshot_id),
            ("ledger_snapshot_fingerprint", self.ledger_snapshot_fingerprint),
            ("registry_id", self.registry_id),
            ("registry_fingerprint", self.registry_fingerprint),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.decision not in _SELECTION_DECISIONS:
            raise ValueError("unknown intervention selection decision")
        mapping_ids = tuple(item.mapping_id for item in self.mapping_refs)
        if len(set(mapping_ids)) != len(mapping_ids):
            raise ValueError("selection mapping refs must be unique")
        _require_unique_strings("decision_reasons", self.decision_reasons)
        if self.decision == "selected":
            if self.selected_intervention_ref is None:
                raise ValueError("selected decision requires intervention ref")
        elif self.selected_intervention_ref is not None:
            raise ValueError("non-selected decision cannot cite selected intervention")
        if self.claim_scope != "participant_specific_intervention_selection":
            raise ValueError("unknown M9 selection claim scope")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "ledger_snapshot_id": self.ledger_snapshot_id,
            "ledger_snapshot_fingerprint": self.ledger_snapshot_fingerprint,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "registry_id": self.registry_id,
            "registry_fingerprint": self.registry_fingerprint,
            "policy_ref": self.policy_ref.to_dict(),
            "mapping_refs": [item.to_dict() for item in self.mapping_refs],
            "decision": self.decision,
            "selected_intervention_ref": (
                None
                if self.selected_intervention_ref is None
                else self.selected_intervention_ref.to_dict()
            ),
            "decision_reasons": list(self.decision_reasons),
            "created_at": self.created_at,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["selection_id"] = self.selection_id
            payload["fingerprint"] = self.fingerprint
        return payload
