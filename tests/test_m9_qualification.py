from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisAssessmentPolicyRef,
    HypothesisAssessmentRef,
    HypothesisLedgerEntry,
    HypothesisLedgerSnapshot,
    HypothesisLifecycleEventRef,
    HypothesisRevision,
    HypothesisRevisionRef,
    LearnerHypothesisRef,
)
from chess_mentor_engine.training import (
    InterventionMappingProvenance,
    TrainingContentProvenance,
    TrainingInterventionError,
    build_intervention_registry,
    define_exercise,
    define_intervention_selection_policy,
    define_training_intervention,
    record_hypothesis_intervention_mapping,
    select_training_intervention,
)

T0 = "2026-09-09T09:00:00-03:00"
T1 = "2026-09-09T09:01:00-03:00"
T2 = "2026-09-09T09:02:00-03:00"
T3 = "2026-09-09T09:03:00-03:00"
T4 = "2026-09-09T09:04:00-03:00"
T5 = "2026-09-09T09:05:00-03:00"


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _training_author() -> TrainingContentProvenance:
    return TrainingContentProvenance(
        actor_kind="human",
        actor_id="coach-01",
        actor_version="1",
        instruction_fingerprint="training-rubric-v1",
        run_id="training-definition-run-1",
    )


def _mapping_author() -> InterventionMappingProvenance:
    return InterventionMappingProvenance(
        actor_kind="human",
        actor_id="coach-01",
        actor_version="1",
        instruction_fingerprint="mapping-rubric-v1",
        run_id="mapping-run-1",
    )


def _exercise(*, key: str = "candidate-scan", version: str = "1"):
    return define_exercise(
        exercise_key=key,
        version=version,
        title="Candidate scan",
        instructions=(
            "Before choosing a move, list three legal candidates and one likely "
            "opponent reply for each."
        ),
        position_source="fresh_position",
        response_schema=("candidate_moves", "expected_replies"),
        completion_evidence_schema=("submitted_candidates", "submitted_replies"),
        duration_hint_minutes=10,
        provenance=_training_author(),
    )


def _intervention(
    *,
    key: str = "candidate-generation-practice",
    version: str = "1",
    exercise_key: str = "candidate-scan",
):
    return define_training_intervention(
        intervention_key=key,
        version=version,
        title="Candidate generation practice",
        target_behavior="Explicitly compare several legal candidates before moving.",
        rationale=(
            "Use structured candidate listing to practice the observed decision "
            "dimension without asserting a causal cognitive mechanism."
        ),
        exercises=(_exercise(key=exercise_key),),
        dosage_guidance="One short set of five positions per practice block.",
        exclusion_notes=(
            "Do not treat completion as evidence of transfer or mastery.",
        ),
        provenance=_training_author(),
    )


def _revision(
    *,
    statement: str = "Strong alternatives are not explicitly reported.",
    parent: HypothesisRevision | None = None,
) -> HypothesisRevision:
    number = 1 if parent is None else parent.revision_number + 1
    parent_ref = None if parent is None else _revision_ref(parent)
    base = HypothesisRevision(
        revision_id="pending",
        fingerprint="pending",
        hypothesis_id="hypothesis_p01_candidate_pattern",
        revision_number=number,
        statement=statement,
        scope_definition="P01 rapid games in central middlegame positions.",
        context_definition_refs=(),
        competing_hypothesis_refs=(),
        unresolved_alternative_notes=(),
        parent_revision_ref=parent_ref,
        revision_reason="initial" if parent is None else "scope refinement",
        author_provenance=HypothesisActorProvenance(
            actor_kind="human",
            actor_id="analyst-01",
            actor_version="1",
            rubric_or_instruction_fingerprint="m7-rubric-v1",
            run_id="m7-run-1",
        ),
        created_at=T0,
    )
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        revision_id=f"hypothesis_revision_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _snapshot(
    revision: HypothesisRevision,
    *,
    status: str = "supported_recurrence",
    lifecycle: str = "active",
    include_assessment: bool = True,
) -> HypothesisLedgerSnapshot:
    revision_ref = _revision_ref(revision)
    assessment_ref = None
    if include_assessment:
        assessment_ref = HypothesisAssessmentRef(
            hypothesis_assessment_id="hypothesis_assessment_m7_current",
            hypothesis_revision_ref=revision_ref,
            assessment_policy_ref=HypothesisAssessmentPolicyRef(
                assessment_policy_id="m7-policy",
                version="1",
                fingerprint="m7-policy-fingerprint",
            ),
            status=status,  # type: ignore[arg-type]
            fingerprint="m7-assessment-fingerprint",
        )
    lifecycle_ref = None
    if lifecycle != "active":
        lifecycle_ref = HypothesisLifecycleEventRef(
            lifecycle_event_id=f"lifecycle-{lifecycle}",
            fingerprint=f"lifecycle-{lifecycle}-fingerprint",
            kind=lifecycle,  # type: ignore[arg-type]
        )
    entry = HypothesisLedgerEntry(
        hypothesis_ref=LearnerHypothesisRef(
            hypothesis_id=revision.hypothesis_id,
            participant_id="P01",
            fingerprint="hypothesis-lineage-fingerprint",
        ),
        current_revision_ref=revision_ref,
        latest_assessment_ref=assessment_ref,
        authority_lifecycle_state=lifecycle,  # type: ignore[arg-type]
        latest_lifecycle_event_ref=lifecycle_ref,
    )
    base = HypothesisLedgerSnapshot(
        snapshot_id="pending",
        fingerprint="pending",
        participant_id="P01",
        entries=(entry,),
        created_at=T2,
    )
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        snapshot_id=f"hypothesis_ledger_snapshot_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _registry(*interventions):
    values = interventions or (_intervention(),)
    return build_intervention_registry(
        version="1",
        interventions=tuple(values),
        created_at=T1,
    )


def _mapping(
    revision: HypothesisRevision,
    intervention,
    *,
    applicability: str = "applicable",
    participant_id: str = "P01",
):
    uncertainty = (
        ("Applicability needs human review.",)
        if applicability == "unclear"
        else ()
    )
    return record_hypothesis_intervention_mapping(
        participant_id=participant_id,
        hypothesis_revision=revision,
        intervention=intervention,
        applicability=applicability,  # type: ignore[arg-type]
        rationale="The exercise directly practices the bounded observed dimension.",
        uncertainty_notes=uncertainty,
        provenance=_mapping_author(),
        created_at=T3,
    )


def _policy(*, version: str = "1"):
    return define_intervention_selection_policy(
        policy_id="m9-supported-recurrence-only",
        version=version,
    )


def _select(
    revision: HypothesisRevision,
    snapshot: HypothesisLedgerSnapshot,
    registry,
    mappings,
):
    return select_training_intervention(
        participant_id="P01",
        ledger_snapshot=snapshot,
        hypothesis_revision=revision,
        registry=registry,
        policy=_policy(),
        mappings=tuple(mappings),
        created_at=T5,
    )


def test_m9_exercise_identity_is_deterministic_and_version_material() -> None:
    first = _exercise()
    second = _exercise()
    revised = _exercise(version="2")

    assert first == second
    assert first.exercise_id == second.exercise_id
    assert first.fingerprint == second.fingerprint
    assert revised.exercise_id != first.exercise_id


def test_m9_registry_normalizes_order_and_rejects_duplicate_stable_keys() -> None:
    first = _intervention(key="candidate-practice", exercise_key="candidate-a")
    second = _intervention(key="reply-practice", exercise_key="reply-a")
    left = _registry(second, first)
    right = _registry(first, second)

    assert left == right
    assert tuple(item.intervention_key for item in left.interventions) == (
        "candidate-practice",
        "reply-practice",
    )

    duplicate = _intervention(
        key="candidate-practice",
        version="2",
        exercise_key="candidate-b",
    )
    with pytest.raises(TrainingInterventionError, match="keys must be unique"):
        _registry(first, duplicate)


def test_m9_mapping_requires_explicit_uncertainty_for_unclear_judgment() -> None:
    revision = _revision()
    intervention = _intervention()

    with pytest.raises(TrainingInterventionError, match="uncertainty notes"):
        record_hypothesis_intervention_mapping(
            participant_id="P01",
            hypothesis_revision=revision,
            intervention=intervention,
            applicability="unclear",
            rationale="The fit cannot yet be established.",
            uncertainty_notes=(),
            provenance=_mapping_author(),
            created_at=T3,
        )


def test_m9_supported_active_current_revision_selects_single_mapping() -> None:
    revision = _revision()
    intervention = _intervention()
    registry = _registry(intervention)
    decision = _select(
        revision,
        _snapshot(revision),
        registry,
        (_mapping(revision, intervention),),
    )

    assert decision.decision == "selected"
    assert decision.selected_intervention_ref is not None
    assert decision.selected_intervention_ref.intervention_id == (
        intervention.intervention_id
    )
    assert decision.decision_reasons == (
        "single_applicable_mapping_selected",
    )


def test_m9_isolated_hypothesis_is_ineligible_even_with_applicable_mapping() -> None:
    revision = _revision()
    intervention = _intervention()
    decision = _select(
        revision,
        _snapshot(revision, status="isolated"),
        _registry(intervention),
        (_mapping(revision, intervention),),
    )

    assert decision.decision == "ineligible"
    assert decision.selected_intervention_ref is None
    assert "hypothesis_status_not_supported_recurrence" in (
        decision.decision_reasons
    )


def test_m9_missing_current_m7_assessment_is_ineligible() -> None:
    revision = _revision()
    intervention = _intervention()
    decision = _select(
        revision,
        _snapshot(revision, include_assessment=False),
        _registry(intervention),
        (_mapping(revision, intervention),),
    )

    assert decision.decision == "ineligible"
    assert decision.decision_reasons == ("no_current_m7_assessment",)


def test_m9_retired_hypothesis_is_ineligible() -> None:
    revision = _revision()
    intervention = _intervention()
    decision = _select(
        revision,
        _snapshot(revision, lifecycle="retired"),
        _registry(intervention),
        (_mapping(revision, intervention),),
    )

    assert decision.decision == "ineligible"
    assert "hypothesis_not_active" in decision.decision_reasons


def test_m9_stale_revision_is_not_promoted_from_newer_current_state() -> None:
    old_revision = _revision()
    current_revision = _revision(
        statement="Strong alternatives are inconsistently reported.",
        parent=old_revision,
    )
    intervention = _intervention()
    decision = _select(
        old_revision,
        _snapshot(current_revision),
        _registry(intervention),
        (_mapping(old_revision, intervention),),
    )

    assert decision.decision == "ineligible"
    assert "hypothesis_revision_not_current" in decision.decision_reasons


def test_m9_unclear_applicability_stays_unclear() -> None:
    revision = _revision()
    intervention = _intervention()
    decision = _select(
        revision,
        _snapshot(revision),
        _registry(intervention),
        (_mapping(revision, intervention, applicability="unclear"),),
    )

    assert decision.decision == "unclear"
    assert decision.decision_reasons == (
        "intervention_applicability_unclear",
    )


def test_m9_multiple_applicable_interventions_do_not_trigger_ranking() -> None:
    revision = _revision()
    first = _intervention(key="candidate-practice", exercise_key="candidate-a")
    second = _intervention(key="reply-practice", exercise_key="reply-a")
    decision = _select(
        revision,
        _snapshot(revision),
        _registry(first, second),
        (_mapping(revision, second), _mapping(revision, first)),
    )

    assert decision.decision == "unclear"
    assert decision.selected_intervention_ref is None
    assert decision.decision_reasons == (
        "multiple_applicable_interventions",
    )


def test_m9_mapping_to_unregistered_definition_is_rejected() -> None:
    revision = _revision()
    registered = _intervention(key="registered", exercise_key="registered-a")
    outside = _intervention(key="outside", exercise_key="outside-a")

    with pytest.raises(TrainingInterventionError, match="registered definition"):
        _select(
            revision,
            _snapshot(revision),
            _registry(registered),
            (_mapping(revision, outside),),
        )


def test_m9_cross_participant_mapping_is_rejected() -> None:
    revision = _revision()
    intervention = _intervention()

    with pytest.raises(TrainingInterventionError, match="participant mismatch"):
        _select(
            revision,
            _snapshot(revision),
            _registry(intervention),
            (_mapping(revision, intervention, participant_id="P02"),),
        )


def test_m9_mapping_order_does_not_change_selection_identity() -> None:
    revision = _revision()
    selected = _intervention(key="selected", exercise_key="selected-a")
    rejected = _intervention(key="rejected", exercise_key="rejected-a")
    registry = _registry(selected, rejected)
    mappings = (
        _mapping(revision, selected),
        _mapping(revision, rejected, applicability="not_applicable"),
    )

    first = _select(revision, _snapshot(revision), registry, mappings)
    second = _select(revision, _snapshot(revision), registry, reversed(mappings))

    assert first == second
    assert first.fingerprint == second.fingerprint


def test_m9_policy_version_is_material_to_selection_identity() -> None:
    first = _policy(version="1")
    second = _policy(version="2")

    assert first.policy_fingerprint != second.policy_fingerprint


def test_m9_rejects_hash_consistent_boundary_tampering() -> None:
    revision = _revision()
    intervention = _intervention()
    snapshot = _snapshot(revision)
    tampered = replace(snapshot, fingerprint="wrong")

    with pytest.raises(TrainingInterventionError, match="snapshot fingerprint"):
        _select(
            revision,
            tampered,
            _registry(intervention),
            (_mapping(revision, intervention),),
        )


def test_m9_serialized_selection_contains_no_effect_or_mastery_authority() -> None:
    revision = _revision()
    intervention = _intervention()
    decision = _select(
        revision,
        _snapshot(revision),
        _registry(intervention),
        (_mapping(revision, intervention),),
    )
    serialized = json.dumps(decision.to_dict(), sort_keys=True).lower()

    for prohibited in (
        "effectiveness",
        "efficacy",
        "learning_state",
        "transfer_state",
        "mastery_state",
        "improvement",
        "optimal_intervention",
    ):
        assert prohibited not in serialized
