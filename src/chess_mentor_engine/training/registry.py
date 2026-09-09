"""Bounded deterministic M9 registry, mapping, and selection operations."""

from __future__ import annotations

import hashlib
from datetime import datetime

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    HypothesisLedgerSnapshot,
    HypothesisRevision,
)

from .model import (
    ExerciseDefinition,
    ExercisePositionSource,
    HypothesisInterventionMapping,
    HypothesisInterventionMappingRef,
    InterventionApplicability,
    InterventionMappingProvenance,
    InterventionRegistry,
    InterventionSelectionDecision,
    InterventionSelectionPolicy,
    InterventionSelectionPolicyRef,
    TrainingContentProvenance,
    TrainingInterventionDefinition,
    TrainingInterventionRef,
)


class TrainingInterventionError(ValueError):
    """Raised when M9 identity, provenance, or selection invariants fail."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise TrainingInterventionError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TrainingInterventionError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TrainingInterventionError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _exercise_ref_payload(exercise: ExerciseDefinition) -> dict[str, object]:
    return exercise.to_dict(include_identity=False)


def _validate_exercise(exercise: ExerciseDefinition) -> None:
    expected = _fingerprint(_exercise_ref_payload(exercise))
    if exercise.fingerprint != expected:
        raise TrainingInterventionError("exercise fingerprint mismatch")
    if exercise.exercise_id != f"exercise_{expected[:20]}":
        raise TrainingInterventionError("exercise identity mismatch")


def define_exercise(
    *,
    exercise_key: str,
    version: str,
    title: str,
    instructions: str,
    position_source: ExercisePositionSource,
    response_schema: tuple[str, ...],
    completion_evidence_schema: tuple[str, ...],
    provenance: TrainingContentProvenance,
    duration_hint_minutes: int | None = None,
) -> ExerciseDefinition:
    """Create one content-addressed exercise definition."""
    payload = {
        "exercise_key": exercise_key,
        "version": version,
        "title": title,
        "instructions": instructions,
        "position_source": position_source,
        "response_schema": list(response_schema),
        "completion_evidence_schema": list(completion_evidence_schema),
        "duration_hint_minutes": duration_hint_minutes,
        "provenance": provenance.to_dict(),
    }
    fingerprint = _fingerprint(payload)
    try:
        return ExerciseDefinition(
            exercise_id=f"exercise_{fingerprint[:20]}",
            fingerprint=fingerprint,
            exercise_key=exercise_key,
            version=version,
            title=title,
            instructions=instructions,
            position_source=position_source,
            response_schema=response_schema,
            completion_evidence_schema=completion_evidence_schema,
            duration_hint_minutes=duration_hint_minutes,
            provenance=provenance,
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc


def _intervention_ref(
    intervention: TrainingInterventionDefinition,
) -> TrainingInterventionRef:
    return TrainingInterventionRef(
        intervention_id=intervention.intervention_id,
        intervention_key=intervention.intervention_key,
        version=intervention.version,
        fingerprint=intervention.fingerprint,
    )


def _validate_intervention(
    intervention: TrainingInterventionDefinition,
) -> None:
    for exercise in intervention.exercises:
        _validate_exercise(exercise)
    expected = _fingerprint(intervention.to_dict(include_identity=False))
    if intervention.fingerprint != expected:
        raise TrainingInterventionError("intervention fingerprint mismatch")
    if intervention.intervention_id != f"training_intervention_{expected[:20]}":
        raise TrainingInterventionError("intervention identity mismatch")


def define_training_intervention(
    *,
    intervention_key: str,
    version: str,
    title: str,
    target_behavior: str,
    rationale: str,
    exercises: tuple[ExerciseDefinition, ...],
    dosage_guidance: str,
    exclusion_notes: tuple[str, ...],
    provenance: TrainingContentProvenance,
) -> TrainingInterventionDefinition:
    """Create one versioned intervention without claiming pedagogical efficacy."""
    for exercise in exercises:
        _validate_exercise(exercise)
    payload = {
        "intervention_key": intervention_key,
        "version": version,
        "title": title,
        "target_behavior": target_behavior,
        "rationale": rationale,
        "exercises": [item.to_dict() for item in exercises],
        "dosage_guidance": dosage_guidance,
        "exclusion_notes": list(exclusion_notes),
        "provenance": provenance.to_dict(),
    }
    fingerprint = _fingerprint(payload)
    try:
        return TrainingInterventionDefinition(
            intervention_id=f"training_intervention_{fingerprint[:20]}",
            fingerprint=fingerprint,
            intervention_key=intervention_key,
            version=version,
            title=title,
            target_behavior=target_behavior,
            rationale=rationale,
            exercises=exercises,
            dosage_guidance=dosage_guidance,
            exclusion_notes=exclusion_notes,
            provenance=provenance,
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc


def build_intervention_registry(
    *,
    version: str,
    interventions: tuple[TrainingInterventionDefinition, ...],
    created_at: str,
) -> InterventionRegistry:
    """Freeze a deterministic registry with one current version per stable key."""
    _parse_timestamp(created_at)
    for intervention in interventions:
        _validate_intervention(intervention)
    ordered = tuple(
        sorted(interventions, key=lambda item: item.intervention_key)
    )
    payload = {
        "version": version,
        "interventions": [item.to_dict() for item in ordered],
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        return InterventionRegistry(
            registry_id=f"intervention_registry_{fingerprint[:20]}",
            fingerprint=fingerprint,
            version=version,
            interventions=ordered,
            created_at=created_at,
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc


def _validate_registry(registry: InterventionRegistry) -> None:
    for intervention in registry.interventions:
        _validate_intervention(intervention)
    expected = _fingerprint(registry.to_dict(include_identity=False))
    if registry.fingerprint != expected:
        raise TrainingInterventionError("intervention registry fingerprint mismatch")
    if registry.registry_id != f"intervention_registry_{expected[:20]}":
        raise TrainingInterventionError("intervention registry identity mismatch")


def _validate_revision(revision: HypothesisRevision) -> None:
    expected = _fingerprint(revision.to_dict(include_identity=False))
    if revision.fingerprint != expected:
        raise TrainingInterventionError("M7 hypothesis revision fingerprint mismatch")
    if revision.revision_id != f"hypothesis_revision_{expected[:20]}":
        raise TrainingInterventionError("M7 hypothesis revision identity mismatch")


def _revision_ref(revision: HypothesisRevision):
    from chess_mentor_engine.learning import HypothesisRevisionRef

    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _validate_snapshot(snapshot: HypothesisLedgerSnapshot) -> None:
    expected = _fingerprint(snapshot.to_dict(include_identity=False))
    if snapshot.fingerprint != expected:
        raise TrainingInterventionError("M7 ledger snapshot fingerprint mismatch")
    if snapshot.snapshot_id != f"hypothesis_ledger_snapshot_{expected[:20]}":
        raise TrainingInterventionError("M7 ledger snapshot identity mismatch")


def record_hypothesis_intervention_mapping(
    *,
    participant_id: str,
    hypothesis_revision: HypothesisRevision,
    intervention: TrainingInterventionDefinition,
    applicability: InterventionApplicability,
    rationale: str,
    uncertainty_notes: tuple[str, ...],
    provenance: InterventionMappingProvenance,
    created_at: str,
) -> HypothesisInterventionMapping:
    """Record an explicit authored pedagogical bridge without efficacy semantics."""
    _validate_revision(hypothesis_revision)
    _validate_intervention(intervention)
    mapped_at = _parse_timestamp(created_at)
    if mapped_at < _parse_timestamp(hypothesis_revision.created_at):
        raise TrainingInterventionError(
            "intervention mapping cannot predate hypothesis revision"
        )
    payload = {
        "participant_id": participant_id,
        "hypothesis_revision_ref": _revision_ref(hypothesis_revision).to_dict(),
        "intervention_ref": _intervention_ref(intervention).to_dict(),
        "applicability": applicability,
        "rationale": rationale,
        "uncertainty_notes": list(uncertainty_notes),
        "provenance": provenance.to_dict(),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        return HypothesisInterventionMapping(
            mapping_id=f"hypothesis_intervention_mapping_{fingerprint[:20]}",
            fingerprint=fingerprint,
            participant_id=participant_id,
            hypothesis_revision_ref=_revision_ref(hypothesis_revision),
            intervention_ref=_intervention_ref(intervention),
            applicability=applicability,
            rationale=rationale,
            uncertainty_notes=uncertainty_notes,
            provenance=provenance,
            created_at=created_at,
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc


def _mapping_ref(
    mapping: HypothesisInterventionMapping,
) -> HypothesisInterventionMappingRef:
    return HypothesisInterventionMappingRef(
        mapping_id=mapping.mapping_id,
        fingerprint=mapping.fingerprint,
        applicability=mapping.applicability,
    )


def _validate_mapping(mapping: HypothesisInterventionMapping) -> None:
    expected = _fingerprint(mapping.to_dict(include_identity=False))
    if mapping.fingerprint != expected:
        raise TrainingInterventionError("intervention mapping fingerprint mismatch")
    expected_id = f"hypothesis_intervention_mapping_{expected[:20]}"
    if mapping.mapping_id != expected_id:
        raise TrainingInterventionError("intervention mapping identity mismatch")


def define_intervention_selection_policy(
    *,
    policy_id: str,
    version: str,
) -> InterventionSelectionPolicy:
    """Define the conservative v1 M9 selection gate."""
    payload = {
        "policy_id": policy_id,
        "version": version,
        "required_hypothesis_status": "supported_recurrence",
        "require_active_current": True,
        "mapping_rule": "single_applicable_mapping",
        "claim_scope": "participant_specific_intervention_selection",
    }
    fingerprint = _fingerprint(payload)
    try:
        return InterventionSelectionPolicy(
            policy_id=policy_id,
            version=version,
            policy_fingerprint=fingerprint,
            required_hypothesis_status="supported_recurrence",
            require_active_current=True,
            mapping_rule="single_applicable_mapping",
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc


def _policy_ref(
    policy: InterventionSelectionPolicy,
) -> InterventionSelectionPolicyRef:
    return InterventionSelectionPolicyRef(
        policy_id=policy.policy_id,
        version=policy.version,
        fingerprint=policy.policy_fingerprint,
    )


def _validate_policy(policy: InterventionSelectionPolicy) -> None:
    expected = _fingerprint(policy.to_dict(include_identity=False))
    if policy.policy_fingerprint != expected:
        raise TrainingInterventionError("intervention policy fingerprint mismatch")


def _registry_intervention_by_id(
    registry: InterventionRegistry,
) -> dict[str, TrainingInterventionDefinition]:
    return {item.intervention_id: item for item in registry.interventions}


def _mapping_matches_registered_intervention(
    mapping: HypothesisInterventionMapping,
    interventions: dict[str, TrainingInterventionDefinition],
) -> bool:
    intervention = interventions.get(mapping.intervention_ref.intervention_id)
    if intervention is None:
        return False
    return mapping.intervention_ref == _intervention_ref(intervention)


def select_training_intervention(
    *,
    participant_id: str,
    ledger_snapshot: HypothesisLedgerSnapshot,
    hypothesis_revision: HypothesisRevision,
    registry: InterventionRegistry,
    policy: InterventionSelectionPolicy,
    mappings: tuple[HypothesisInterventionMapping, ...],
    created_at: str,
) -> InterventionSelectionDecision:
    """Select at most one mapped intervention under exact M7 and M9 provenance."""
    _validate_snapshot(ledger_snapshot)
    _validate_revision(hypothesis_revision)
    _validate_registry(registry)
    _validate_policy(policy)
    if ledger_snapshot.participant_id != participant_id:
        raise TrainingInterventionError("M7 ledger participant mismatch")

    selected_at = _parse_timestamp(created_at)
    if selected_at < _parse_timestamp(ledger_snapshot.created_at):
        raise TrainingInterventionError("selection cannot predate M7 ledger snapshot")
    if selected_at < _parse_timestamp(registry.created_at):
        raise TrainingInterventionError("selection cannot predate registry snapshot")

    expected_revision_ref = _revision_ref(hypothesis_revision)
    interventions = _registry_intervention_by_id(registry)
    ordered_mappings = tuple(sorted(mappings, key=lambda item: item.mapping_id))
    for mapping in ordered_mappings:
        _validate_mapping(mapping)
        if mapping.participant_id != participant_id:
            raise TrainingInterventionError("mapping participant mismatch")
        if mapping.hypothesis_revision_ref != expected_revision_ref:
            raise TrainingInterventionError("mapping hypothesis revision mismatch")
        if not _mapping_matches_registered_intervention(mapping, interventions):
            raise TrainingInterventionError(
                "mapping intervention is not the exact registered definition"
            )
        if selected_at < _parse_timestamp(mapping.created_at):
            raise TrainingInterventionError("selection cannot predate mapping")

    reasons: list[str] = []
    entry = next(
        (
            item
            for item in ledger_snapshot.entries
            if item.hypothesis_ref.hypothesis_id == hypothesis_revision.hypothesis_id
        ),
        None,
    )
    gates_pass = True
    if entry is None:
        reasons.append("hypothesis_not_in_current_ledger")
        gates_pass = False
    else:
        if entry.hypothesis_ref.participant_id != participant_id:
            raise TrainingInterventionError("hypothesis participant mismatch")
        if entry.current_revision_ref != expected_revision_ref:
            reasons.append("hypothesis_revision_not_current")
            gates_pass = False
        if entry.authority_lifecycle_state != "active":
            reasons.append("hypothesis_not_active")
            gates_pass = False
        if entry.latest_assessment_ref is None:
            reasons.append("no_current_m7_assessment")
            gates_pass = False
        elif (
            entry.latest_assessment_ref.status
            != policy.required_hypothesis_status
        ):
            reasons.append("hypothesis_status_not_supported_recurrence")
            gates_pass = False
        elif (
            entry.latest_assessment_ref.hypothesis_revision_ref
            != entry.current_revision_ref
        ):
            raise TrainingInterventionError(
                "M7 latest assessment does not target current revision"
            )

    applicable = tuple(
        item for item in ordered_mappings if item.applicability == "applicable"
    )
    unclear = tuple(
        item for item in ordered_mappings if item.applicability == "unclear"
    )

    decision = "ineligible"
    selected_ref: TrainingInterventionRef | None = None
    if gates_pass:
        if len(applicable) == 1:
            decision = "selected"
            selected_ref = applicable[0].intervention_ref
            reasons.append("single_applicable_mapping_selected")
        elif len(applicable) > 1:
            decision = "unclear"
            reasons.append("multiple_applicable_interventions")
        elif unclear:
            decision = "unclear"
            reasons.append("intervention_applicability_unclear")
        else:
            reasons.append("no_applicable_intervention")

    mapping_refs = tuple(_mapping_ref(item) for item in ordered_mappings)
    payload = {
        "participant_id": participant_id,
        "ledger_snapshot_id": ledger_snapshot.snapshot_id,
        "ledger_snapshot_fingerprint": ledger_snapshot.fingerprint,
        "hypothesis_revision_ref": expected_revision_ref.to_dict(),
        "registry_id": registry.registry_id,
        "registry_fingerprint": registry.fingerprint,
        "policy_ref": _policy_ref(policy).to_dict(),
        "mapping_refs": [item.to_dict() for item in mapping_refs],
        "decision": decision,
        "selected_intervention_ref": (
            None if selected_ref is None else selected_ref.to_dict()
        ),
        "decision_reasons": reasons,
        "created_at": created_at,
        "claim_scope": "participant_specific_intervention_selection",
    }
    fingerprint = _fingerprint(payload)
    try:
        return InterventionSelectionDecision(
            selection_id=f"intervention_selection_{fingerprint[:20]}",
            fingerprint=fingerprint,
            participant_id=participant_id,
            ledger_snapshot_id=ledger_snapshot.snapshot_id,
            ledger_snapshot_fingerprint=ledger_snapshot.fingerprint,
            hypothesis_revision_ref=expected_revision_ref,
            registry_id=registry.registry_id,
            registry_fingerprint=registry.fingerprint,
            policy_ref=_policy_ref(policy),
            mapping_refs=mapping_refs,
            decision=decision,  # type: ignore[arg-type]
            selected_intervention_ref=selected_ref,
            decision_reasons=tuple(reasons),
            created_at=created_at,
        )
    except ValueError as exc:
        raise TrainingInterventionError(str(exc)) from exc
