from dataclasses import replace

import pytest

from chess_mentor_engine.chess_knowledge import (
    HypothesisKnowledgeConceptSummary,
    HypothesisKnowledgeProjection,
)
from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisAssessmentPolicyRef,
    HypothesisAssessmentRef,
    HypothesisRevision,
    HypothesisRevisionRef,
    LearnerHypothesisRef,
)
from chess_mentor_engine.longitudinal import (
    HypothesisTrajectory,
    LearnerStateReadModel,
    LearnerStateSnapshot,
    LongitudinalReference,
    LongitudinalStateError,
    OutcomeDimensionState,
    build_learner_state_read_model,
    validate_learner_state_read_model,
)
from chess_mentor_engine.training import (
    InterventionSelectionDecision,
    InterventionSelectionPolicyRef,
    TrainingInterventionRef,
)


def _revision() -> HypothesisRevision:
    return HypothesisRevision(
        revision_id="revision-1",
        fingerprint="revision-fingerprint",
        hypothesis_id="hypothesis-1",
        revision_number=1,
        statement="The player often misses opponent forcing resources.",
        scope_definition="Participant-specific decisions in tactical middlegames.",
        context_definition_refs=(),
        competing_hypothesis_refs=(),
        unresolved_alternative_notes=("Time pressure may explain some cases.",),
        parent_revision_ref=None,
        revision_reason="Initial bounded hypothesis.",
        author_provenance=HypothesisActorProvenance(
            actor_kind="human",
            actor_id="coach",
            actor_version="1",
            rubric_or_instruction_fingerprint="rubric-fp",
        ),
        created_at="2026-09-11T09:00:00+00:00",
    )


def _revision_ref() -> HypothesisRevisionRef:
    revision = _revision()
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _assessment_ref() -> HypothesisAssessmentRef:
    return HypothesisAssessmentRef(
        hypothesis_assessment_id="assessment-1",
        hypothesis_revision_ref=_revision_ref(),
        assessment_policy_ref=HypothesisAssessmentPolicyRef(
            assessment_policy_id="recurrence-policy",
            version="1",
            fingerprint="recurrence-policy-fp",
        ),
        status="supported_recurrence",
        fingerprint="assessment-fp",
    )


def _snapshot() -> LearnerStateSnapshot:
    return LearnerStateSnapshot(
        participant_id="P01",
        ledger_ref=LongitudinalReference(
            "learner_state_ledger",
            "ledger-1",
            "ledger-fp",
        ),
        trajectories=(
            HypothesisTrajectory(
                hypothesis_ref=LearnerHypothesisRef(
                    hypothesis_id="hypothesis-1",
                    participant_id="P01",
                    fingerprint="hypothesis-fp",
                ),
                current_revision_ref=_revision_ref(),
                authority_lifecycle_state="active",
                latest_m7_assessment_ref=_assessment_ref(),
                latest_m7_status="supported_recurrence",
                current_outcome_assessment_ref=LongitudinalReference(
                    "outcome_assessment",
                    "outcome-1",
                    "outcome-fp",
                ),
                current_outcome_dimensions=(
                    OutcomeDimensionState("practice", "supported"),
                    OutcomeDimensionState("near_transfer", "supported"),
                    OutcomeDimensionState("far_transfer", "insufficient"),
                    OutcomeDimensionState("real_game_transfer", "insufficient"),
                ),
                event_refs=(
                    LongitudinalReference(
                        "learner_state_event",
                        "event-1",
                        "event-fp",
                    ),
                ),
            ),
        ),
        created_at="2026-09-11T10:00:00+00:00",
    )


def _selection(*, participant_id: str = "P01") -> InterventionSelectionDecision:
    return InterventionSelectionDecision(
        selection_id="selection-1",
        fingerprint="selection-fp",
        participant_id=participant_id,
        ledger_snapshot_id="m7-ledger-snapshot",
        ledger_snapshot_fingerprint="m7-ledger-fp",
        hypothesis_revision_ref=_revision_ref(),
        registry_id="registry-1",
        registry_fingerprint="registry-fp",
        policy_ref=InterventionSelectionPolicyRef(
            policy_id="selection-policy",
            version="1",
            fingerprint="selection-policy-fp",
        ),
        mapping_refs=(),
        decision="selected",
        selected_intervention_ref=TrainingInterventionRef(
            intervention_id="intervention-1",
            intervention_key="forcing-resource-scan",
            version="1",
            fingerprint="intervention-fp",
        ),
        decision_reasons=("Exactly one applicable mapping was selected.",),
        created_at="2026-09-11T10:05:00+00:00",
    )


def _knowledge_projection() -> HypothesisKnowledgeProjection:
    summary = HypothesisKnowledgeConceptSummary(
        concept_id="tactic.fork",
        concept_fingerprint="concept-fp",
        preferred_name="Fork",
        kind="tactical_motif",
        occurrence_count=1,
        relation_counts=(("supports", 1),),
        status_counts=(("present", 1),),
        authority_counts=(("deterministic_sequence_pattern", 1),),
        source_position_ids=("position-1",),
        source_game_ids=("game-1",),
    )
    return HypothesisKnowledgeProjection(
        projection_id="knowledge-projection-1",
        fingerprint="knowledge-projection-fp",
        hypothesis_assessment_id="assessment-1",
        hypothesis_assessment_fingerprint="assessment-fp",
        hypothesis_revision_ref=_revision_ref(),
        hypothesis_assessment_status="supported_recurrence",
        ontology_version="1.0.0",
        ontology_fingerprint="ontology-fp",
        units=(),
        concept_summaries=(summary,),
        covered_recurrence_unit_ids=(),
        uncovered_recurrence_unit_ids=("unit-uncovered",),
        claim_scope="descriptive ontology projection only",
        created_at="2026-09-11T10:10:00+00:00",
    )


def _build() -> LearnerStateReadModel:
    return build_learner_state_read_model(
        snapshot=_snapshot(),
        revisions=(_revision(),),
        intervention_decisions=(_selection(),),
        knowledge_projections=(_knowledge_projection(),),
        created_at="2026-09-11T11:00:00+00:00",
    )


def test_m36_combines_current_m7_m9_m10_m11_and_k7_without_new_authority():
    read_model = _build()

    assert read_model.schema_version == "m36.learner-state-read-model.v1"
    assert read_model.participant_id == "P01"
    assert read_model.causal_effect == "not_established"
    assert read_model.mastery == "not_established"
    assert len(read_model.hypotheses) == 1

    entry = read_model.hypotheses[0]
    assert entry.statement.startswith("The player often misses")
    assert entry.m7_status == "supported_recurrence"
    assert entry.intervention.state == "selected"
    assert entry.intervention.selected_interventions[0].intervention_key == (
        "forcing-resource-scan"
    )
    assert tuple(item.status for item in entry.outcome_dimensions) == (
        "supported",
        "supported",
        "insufficient",
        "insufficient",
    )
    assert entry.knowledge.concept_ids == ("tactic.fork",)
    assert entry.knowledge.uncovered_recurrence_unit_count == 1


def test_m36_is_content_addressed_and_rebuildable():
    first = _build()
    second = _build()

    assert first == second
    assert first.read_model_id.startswith("learner_state_read_model_")
    assert first.to_dict()["fingerprint"] == first.fingerprint
    validate_learner_state_read_model(
        first,
        snapshot=_snapshot(),
        revisions=(_revision(),),
        intervention_decisions=(_selection(),),
        knowledge_projections=(_knowledge_projection(),),
    )


def test_m36_serializes_all_m10_outcome_dimensions():
    payload = _build().to_dict()
    dimensions = payload["hypotheses"][0]["outcome_dimensions"]

    assert dimensions == [
        {"evidence_kind": "practice", "status": "supported"},
        {"evidence_kind": "near_transfer", "status": "supported"},
        {"evidence_kind": "far_transfer", "status": "insufficient"},
        {"evidence_kind": "real_game_transfer", "status": "insufficient"},
    ]


def test_m36_rejects_cross_participant_m9_selection():
    with pytest.raises(LongitudinalStateError, match="participant mismatch"):
        build_learner_state_read_model(
            snapshot=_snapshot(),
            revisions=(_revision(),),
            intervention_decisions=(_selection(participant_id="P02"),),
            created_at="2026-09-11T11:00:00+00:00",
        )


def test_m36_rejects_missing_current_revision():
    with pytest.raises(LongitudinalStateError, match="missing current"):
        build_learner_state_read_model(
            snapshot=_snapshot(),
            revisions=(),
            created_at="2026-09-11T11:00:00+00:00",
        )


def test_m36_rejects_stale_revision_identity():
    stale = replace(_revision(), fingerprint="stale-fingerprint")

    with pytest.raises(LongitudinalStateError, match="revision identity mismatch"):
        build_learner_state_read_model(
            snapshot=_snapshot(),
            revisions=(stale,),
            created_at="2026-09-11T11:00:00+00:00",
        )


def test_m36_rejects_tampered_read_model():
    model = _build()
    tampered = replace(model, participant_id="P02")

    with pytest.raises(LongitudinalStateError, match="read model mismatch"):
        validate_learner_state_read_model(
            tampered,
            snapshot=_snapshot(),
            revisions=(_revision(),),
            intervention_decisions=(_selection(),),
            knowledge_projections=(_knowledge_projection(),),
        )
