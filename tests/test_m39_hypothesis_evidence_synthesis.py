from __future__ import annotations

from dataclasses import replace

import pytest
from test_chess_knowledge_learner_projection import (
    _bundle_for_unit,
    _supported_assessment,
)
from test_hypothesis_recurrence_assessment import (
    _assess,
    _make_hypothesis,
    _make_link,
    _policy,
    _support_units,
)

from chess_mentor_engine.chess_knowledge import (
    build_hypothesis_knowledge_projection,
)
from chess_mentor_engine.learner_intelligence import (
    build_hypothesis_evidence_synthesis,
    validate_hypothesis_evidence_synthesis,
)
from chess_mentor_engine.learning import (
    HypothesisAssessmentRef,
    LearnerHypothesisRef,
)
from chess_mentor_engine.longitudinal import (
    HypothesisTrajectory,
    LearnerReadReference,
    LearnerStateSnapshot,
    LongitudinalReference,
    build_learner_state_read_model,
)

_CREATED_AT = "2026-09-11T10:30:00-03:00"


def _assessment_ref(assessment):
    return HypothesisAssessmentRef(
        hypothesis_assessment_id=assessment.hypothesis_assessment_id,
        hypothesis_revision_ref=assessment.hypothesis_revision_ref,
        assessment_policy_ref=assessment.assessment_policy_ref,
        status=assessment.status,
        fingerprint=assessment.fingerprint,
    )


def _read_model_for(hypothesis, revision, assessment, projection=None):
    snapshot = LearnerStateSnapshot(
        participant_id=hypothesis.participant_id,
        ledger_ref=LongitudinalReference(
            "learner_state_ledger",
            "ledger-m39",
            "ledger-m39-fingerprint",
        ),
        trajectories=(
            HypothesisTrajectory(
                hypothesis_ref=LearnerHypothesisRef(
                    hypothesis_id=hypothesis.hypothesis_id,
                    participant_id=hypothesis.participant_id,
                    fingerprint=hypothesis.fingerprint,
                ),
                current_revision_ref=assessment.hypothesis_revision_ref,
                authority_lifecycle_state="active",
                latest_m7_assessment_ref=_assessment_ref(assessment),
                latest_m7_status=assessment.status,
                current_outcome_assessment_ref=None,
                current_outcome_dimensions=(),
                event_refs=(
                    LongitudinalReference(
                        "learner_state_event",
                        "event-m39",
                        "event-m39-fingerprint",
                    ),
                ),
            ),
        ),
        created_at="2026-09-11T10:00:00-03:00",
    )
    projections = () if projection is None else (projection,)
    return build_learner_state_read_model(
        snapshot=snapshot,
        revisions=(revision,),
        knowledge_projections=projections,
        created_at="2026-09-11T10:15:00-03:00",
    )


def _supported_fixture(*, partial_knowledge: bool = False):
    hypothesis, revision, assessment = _supported_assessment(3)
    selected_units = (
        assessment.recurrence_units[:2]
        if partial_knowledge
        else assessment.recurrence_units
    )
    bundles = tuple(_bundle_for_unit(unit) for unit in selected_units)
    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=bundles,
        created_at=_CREATED_AT,
    )
    read_model = _read_model_for(hypothesis, revision, assessment, projection)
    return hypothesis, revision, assessment, projection, read_model


def test_m39_synthesizes_exact_current_m7c_evidence_and_k7_context():
    hypothesis, revision, assessment, projection, read_model = _supported_fixture()

    synthesis = build_hypothesis_evidence_synthesis(
        participant_id=hypothesis.participant_id,
        learner_read_model=read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=projection,
        created_at=_CREATED_AT,
    )

    assert synthesis.schema_version == "m39.hypothesis-evidence-synthesis.v1"
    assert synthesis.hypothesis_assessment_status == assessment.status
    assert synthesis.evidence_counts.support_unit_count == 3
    assert synthesis.evidence_counts.independent_support_count == 3
    assert {item.relation for item in synthesis.units} == {"supports"}
    assert synthesis.concept_ids == ("position.open_file",)
    assert synthesis.causal_effect == "not_established"
    assert synthesis.mastery == "not_established"
    assert any("No contradiction" in item for item in synthesis.evidence_gaps)
    assert any("M7C assessment" in item for item in synthesis.change_conditions)


def test_m39_preserves_support_and_contradiction_relations_verbatim():
    hypothesis, revision = _make_hypothesis()
    links = (
        _support_units(hypothesis, revision, 1)[0],
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="contradicts",
            game_id="g2",
        ),
    )
    assessment = _assess(hypothesis, revision, _policy(), links)
    bundles = tuple(_bundle_for_unit(unit) for unit in assessment.recurrence_units)
    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=bundles,
        created_at=_CREATED_AT,
    )
    read_model = _read_model_for(hypothesis, revision, assessment, projection)

    synthesis = build_hypothesis_evidence_synthesis(
        participant_id=hypothesis.participant_id,
        learner_read_model=read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=projection,
        created_at=_CREATED_AT,
    )

    assert {item.relation for item in synthesis.units} == {"supports", "contradicts"}
    assert synthesis.evidence_counts.contradiction_unit_count == 1
    assert all(item.concept_ids == ("position.open_file",) for item in synthesis.units)


def test_m39_reports_partial_k7_coverage_as_a_gap_not_concept_absence():
    hypothesis, revision, assessment, projection, read_model = _supported_fixture(
        partial_knowledge=True
    )

    synthesis = build_hypothesis_evidence_synthesis(
        participant_id=hypothesis.participant_id,
        learner_read_model=read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=projection,
        created_at=_CREATED_AT,
    )

    uncovered = [item for item in synthesis.units if not item.concept_ids]
    assert len(uncovered) == 1
    assert any("semantic coverage is incomplete" in item for item in synthesis.evidence_gaps)


def test_m39_rejects_cross_participant_request():
    _, revision, assessment, projection, read_model = _supported_fixture()

    with pytest.raises(ValueError, match="participant mismatch"):
        build_hypothesis_evidence_synthesis(
            participant_id="other-participant",
            learner_read_model=read_model,
            revision=revision,
            assessment=assessment,
            knowledge_projection=projection,
            created_at=_CREATED_AT,
        )


def test_m39_rejects_m36_assessment_identity_drift():
    hypothesis, revision, assessment, projection, read_model = _supported_fixture()
    entry = read_model.hypotheses[0]
    assert entry.m7_assessment_ref is not None
    bad_entry = replace(
        entry,
        m7_assessment_ref=LearnerReadReference(
            kind="hypothesis_assessment",
            ref_id=entry.m7_assessment_ref.ref_id,
            fingerprint="different-assessment-fingerprint",
        ),
    )
    bad_model = replace(read_model, hypotheses=(bad_entry,))

    with pytest.raises(ValueError, match="M36/M7C assessment identity mismatch"):
        build_hypothesis_evidence_synthesis(
            participant_id=hypothesis.participant_id,
            learner_read_model=bad_model,
            revision=revision,
            assessment=assessment,
            knowledge_projection=projection,
            created_at=_CREATED_AT,
        )


def test_m39_requires_the_exact_k7_projection_referenced_by_m36():
    hypothesis, revision, assessment, _, read_model = _supported_fixture()

    with pytest.raises(ValueError, match="requires the K7 projection"):
        build_hypothesis_evidence_synthesis(
            participant_id=hypothesis.participant_id,
            learner_read_model=read_model,
            revision=revision,
            assessment=assessment,
            knowledge_projection=None,
            created_at=_CREATED_AT,
        )


def test_m39_is_content_addressed_and_tamper_detectable():
    hypothesis, revision, assessment, projection, read_model = _supported_fixture()
    synthesis = build_hypothesis_evidence_synthesis(
        participant_id=hypothesis.participant_id,
        learner_read_model=read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=projection,
        created_at=_CREATED_AT,
    )
    rebuilt = build_hypothesis_evidence_synthesis(
        participant_id=hypothesis.participant_id,
        learner_read_model=read_model,
        revision=revision,
        assessment=assessment,
        knowledge_projection=projection,
        created_at=_CREATED_AT,
    )
    assert rebuilt == synthesis

    tampered = replace(synthesis, statement="Different unsupported summary.")
    with pytest.raises(ValueError, match="synthesis mismatch"):
        validate_hypothesis_evidence_synthesis(
            tampered,
            participant_id=hypothesis.participant_id,
            learner_read_model=read_model,
            revision=revision,
            assessment=assessment,
            knowledge_projection=projection,
        )
