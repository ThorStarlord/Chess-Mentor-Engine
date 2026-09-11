from __future__ import annotations

from dataclasses import replace

import pytest

from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    HypothesisEvidenceCounts,
    HypothesisEvidenceSynthesis,
    HypothesisReviewSummary,
    NextSessionPolicy,
    build_default_next_session_policy,
    build_next_session_plan,
    validate_next_session_plan,
    validate_next_session_policy,
)
from chess_mentor_engine.learning import HypothesisRevisionRef
from chess_mentor_engine.longitudinal import (
    LearnerHypothesisReadEntry,
    LearnerInterventionSummary,
    LearnerKnowledgeSummary,
    LearnerReadReference,
    LearnerStateReadModel,
    LongitudinalReference,
    OutcomeDimensionState,
)
from chess_mentor_engine.training import TrainingInterventionRef

_CREATED_AT = "2026-09-11T13:00:00-03:00"


def _revision_ref(hypothesis_id: str) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=f"revision-{hypothesis_id}",
        hypothesis_id=hypothesis_id,
        revision_number=1,
        fingerprint=f"revision-fingerprint-{hypothesis_id}",
    )


def _intervention_summary(state: str = "none") -> LearnerInterventionSummary:
    if state == "none":
        return LearnerInterventionSummary(
            state="none",
            selected_interventions=(),
            decision_refs=(),
            decision_counts=(),
        )
    intervention = TrainingInterventionRef(
        intervention_id="intervention-1",
        intervention_key="forcing-resource-scan",
        version="1",
        fingerprint="intervention-fingerprint",
    )
    if state == "selected":
        return LearnerInterventionSummary(
            state="selected",
            selected_interventions=(intervention,),
            decision_refs=(
                LearnerReadReference(
                    "intervention_selection_decision",
                    "selection-1",
                    "selection-fingerprint-1",
                ),
            ),
            decision_counts=(("selected", 1),),
        )
    if state == "mixed":
        return LearnerInterventionSummary(
            state="mixed",
            selected_interventions=(intervention,),
            decision_refs=(
                LearnerReadReference(
                    "intervention_selection_decision",
                    "selection-1",
                    "selection-fingerprint-1",
                ),
                LearnerReadReference(
                    "intervention_selection_decision",
                    "selection-2",
                    "selection-fingerprint-2",
                ),
            ),
            decision_counts=(("ineligible", 1), ("selected", 1)),
        )
    raise AssertionError(f"unknown test intervention state {state!r}")


def _entry(
    hypothesis_id: str = "h1",
    *,
    status: str | None = "supported_recurrence",
    unresolved: tuple[str, ...] = (),
    intervention_state: str = "none",
    outcomes: tuple[tuple[str, str], ...] = (),
    lifecycle: str = "active",
) -> LearnerHypothesisReadEntry:
    assessment_ref = (
        None
        if status is None
        else LearnerReadReference(
            "hypothesis_assessment",
            f"assessment-{hypothesis_id}",
            f"assessment-fingerprint-{hypothesis_id}",
        )
    )
    return LearnerHypothesisReadEntry(
        hypothesis_id=hypothesis_id,
        hypothesis_fingerprint=f"hypothesis-fingerprint-{hypothesis_id}",
        current_revision_ref=_revision_ref(hypothesis_id),
        statement="The player may miss opponent forcing resources.",
        scope_definition="Participant-specific tactical middlegame decisions.",
        unresolved_alternative_notes=unresolved,
        authority_lifecycle_state=lifecycle,
        m7_status=status,
        m7_assessment_ref=assessment_ref,
        outcome_dimensions=tuple(
            OutcomeDimensionState(kind, value) for kind, value in outcomes
        ),
        intervention=_intervention_summary(intervention_state),
        knowledge=LearnerKnowledgeSummary(None, (), 0, 0),
    )


def _read_model(*entries: LearnerHypothesisReadEntry) -> LearnerStateReadModel:
    ordered = tuple(sorted(entries, key=lambda item: item.hypothesis_id))
    return LearnerStateReadModel(
        read_model_id="read-model-1",
        fingerprint="read-model-fingerprint",
        participant_id="P01",
        source_snapshot_ref=LongitudinalReference(
            "learner_state_snapshot",
            "snapshot-1",
            "snapshot-fingerprint",
        ),
        hypotheses=ordered,
        created_at="2026-09-11T12:30:00-03:00",
    )


def _review_summary() -> HypothesisReviewSummary:
    return HypothesisReviewSummary(
        contradiction_review_ref=EvidenceSynthesisReference(
            "hypothesis_contradiction_review",
            "contradiction-review-1",
            "contradiction-review-fingerprint",
        ),
        contradiction_review_state="completed",
        counterexample_review_ref=EvidenceSynthesisReference(
            "hypothesis_counterexample_review",
            "counterexample-review-1",
            "counterexample-review-fingerprint",
        ),
        counterexample_review_state="completed",
        competing_explanation_review_ref=EvidenceSynthesisReference(
            "hypothesis_competing_explanation_review",
            "competing-review-1",
            "competing-review-fingerprint",
        ),
        competing_explanation_review_state="completed",
    )


def _synthesis(
    read_model: LearnerStateReadModel,
    entry: LearnerHypothesisReadEntry,
    *,
    contradiction_count: int = 1,
    counterexample_count: int = 0,
    context_exception_count: int = 0,
    concept_ids: tuple[str, ...] = ("tactic.fork",),
) -> HypothesisEvidenceSynthesis:
    assert entry.m7_status is not None
    assert entry.m7_assessment_ref is not None
    return HypothesisEvidenceSynthesis(
        synthesis_id=f"synthesis-{entry.hypothesis_id}",
        fingerprint=f"synthesis-fingerprint-{entry.hypothesis_id}",
        participant_id=read_model.participant_id,
        learner_read_model_ref=EvidenceSynthesisReference(
            "learner_state_read_model",
            read_model.read_model_id,
            read_model.fingerprint,
        ),
        hypothesis_revision_ref=entry.current_revision_ref,
        statement=entry.statement,
        scope_definition=entry.scope_definition,
        unresolved_alternative_notes=entry.unresolved_alternative_notes,
        hypothesis_assessment_ref=EvidenceSynthesisReference(
            "hypothesis_assessment",
            entry.m7_assessment_ref.ref_id,
            entry.m7_assessment_ref.fingerprint,
        ),
        hypothesis_assessment_status=entry.m7_status,
        assessment_policy_ref=EvidenceSynthesisReference(
            "hypothesis_assessment_policy",
            "m7c-policy:1",
            "m7c-policy-fingerprint",
        ),
        status_reasons=("Current M7C status is preserved.",),
        evidence_counts=HypothesisEvidenceCounts(
            eligible_link_count=3,
            excluded_link_count=0,
            support_unit_count=3,
            independent_support_count=3,
            contradiction_unit_count=contradiction_count,
            successful_counterexample_unit_count=counterexample_count,
            context_exception_unit_count=context_exception_count,
            unclear_unit_count=0,
            mixed_unit_count=0,
        ),
        units=(),
        source_position_ids=(),
        source_game_ids=(),
        review_summary=_review_summary(),
        knowledge_projection_ref=None,
        concept_ids=concept_ids,
        evidence_gaps=(),
        change_conditions=("Future M7C evidence may change this status.",),
        created_at="2026-09-11T12:45:00-03:00",
    )


def _plan_for(
    entry: LearnerHypothesisReadEntry,
    *,
    contradiction_count: int = 1,
):
    read_model = _read_model(entry)
    syntheses = (
        ()
        if entry.m7_status is None
        else (_synthesis(read_model, entry, contradiction_count=contradiction_count),)
    )
    policy = build_default_next_session_policy()
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        policy=policy,
        created_at=_CREATED_AT,
    )
    return plan, read_model, syntheses, policy


def test_m40_supported_but_one_sided_evidence_prefers_challenge():
    plan, _, _, _ = _plan_for(_entry(), contradiction_count=0)

    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"
    assert "Counterevidence coverage" in plan.selected_candidate.blocking_uncertainty[0]
    assert plan.decision_authority == "proposal_only"
    assert plan.causal_effect == "not_established"
    assert plan.mastery == "not_established"


def test_m40_supported_with_counterevidence_and_no_m9_selection_teaches_concept():
    plan, _, _, _ = _plan_for(_entry(), contradiction_count=1)

    assert plan.selected_candidate.action == "TEACH_CONCEPT"
    assert plan.selected_candidate.concept_ids == ("tactic.fork",)
    assert plan.selected_candidate.selected_intervention_ids == ()


def test_m40_contradicted_hypothesis_outranks_training_candidate():
    contradicted = _entry("h1", status="contradicted")
    training = _entry("h2", intervention_state="selected")
    read_model = _read_model(contradicted, training)
    syntheses = (
        _synthesis(read_model, contradicted),
        _synthesis(read_model, training),
    )

    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        policy=build_default_next_session_policy(),
        created_at=_CREATED_AT,
    )

    assert plan.selected_candidate.hypothesis_id == "h1"
    assert plan.selected_candidate.action == "PRESENT_CONTROL"
    assert plan.candidates[1].action == "ASSIGN_PRACTICE"


def test_m40_candidate_recurrence_collects_more_evidence():
    plan, _, _, _ = _plan_for(_entry(status="candidate_recurrence"))

    assert plan.selected_candidate.action == "COLLECT_NEW_EVIDENCE"


def test_m40_mixed_m9_state_never_overrides_selection_authority():
    plan, _, _, _ = _plan_for(_entry(intervention_state="mixed"))

    assert plan.selected_candidate.action == "COLLECT_NEW_EVIDENCE"
    assert any("M9 selection" in item for item in plan.selected_candidate.reasons)


@pytest.mark.parametrize(
    ("outcomes", "expected_action"),
    [
        ((), "ASSIGN_PRACTICE"),
        ((("practice", "supported"),), "RUN_NEAR_TRANSFER_TEST"),
        (
            (("practice", "supported"), ("near_transfer", "supported")),
            "RUN_FAR_TRANSFER_TEST",
        ),
        (
            (
                ("practice", "supported"),
                ("near_transfer", "supported"),
                ("far_transfer", "supported"),
            ),
            "WAIT_FOR_REAL_GAME_EVIDENCE",
        ),
    ],
)
def test_m40_selected_intervention_progresses_through_transfer_stages(
    outcomes,
    expected_action,
):
    entry = _entry(intervention_state="selected", outcomes=outcomes)
    plan, _, _, _ = _plan_for(entry)

    assert plan.selected_candidate.action == expected_action


def test_m40_real_game_support_still_does_not_claim_mastery():
    outcomes = (
        ("practice", "supported"),
        ("near_transfer", "supported"),
        ("far_transfer", "supported"),
        ("real_game_transfer", "supported"),
    )
    entry = _entry(intervention_state="selected", outcomes=outcomes)
    plan, _, _, _ = _plan_for(entry)

    assert plan.selected_candidate.action == "WAIT_FOR_REAL_GAME_EVIDENCE"
    assert plan.mastery == "not_established"
    assert any("automatic mastery" in item for item in plan.selected_candidate.reasons)


def test_m40_supported_with_unresolved_alternative_prefers_challenge():
    entry = _entry(unresolved=("Time pressure may explain some cases.",))
    plan, _, _, _ = _plan_for(entry)

    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"
    assert plan.selected_candidate.blocking_uncertainty == entry.unresolved_alternative_notes


def test_m40_no_m7c_status_collects_evidence_without_m39_synthesis():
    entry = _entry(status=None)
    plan, _, syntheses, _ = _plan_for(entry)

    assert syntheses == ()
    assert plan.selected_candidate.action == "COLLECT_NEW_EVIDENCE"


def test_m40_rejects_tampered_policy_fingerprint():
    policy = build_default_next_session_policy()
    tampered = replace(policy, fingerprint="tampered-policy-fingerprint")

    with pytest.raises(ValueError, match="policy fingerprint mismatch"):
        validate_next_session_policy(tampered)


def test_m40_rejects_synthesis_read_model_identity_drift():
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry)
    tampered = replace(
        synthesis,
        learner_read_model_ref=EvidenceSynthesisReference(
            "learner_state_read_model",
            "different-read-model",
            "different-read-model-fingerprint",
        ),
    )

    with pytest.raises(ValueError, match="read-model identity mismatch"):
        build_next_session_plan(
            learner_read_model=read_model,
            evidence_syntheses=(tampered,),
            policy=build_default_next_session_policy(),
            created_at=_CREATED_AT,
        )


def test_m40_rejects_synthesis_for_retired_hypothesis():
    retired = _entry(lifecycle="retired")
    active = _entry("h2")
    read_model = _read_model(retired, active)
    active_synthesis = _synthesis(read_model, active)
    retired_synthesis = _synthesis(read_model, retired)

    with pytest.raises(ValueError, match="non-active or unreferenced"):
        build_next_session_plan(
            learner_read_model=read_model,
            evidence_syntheses=(active_synthesis, retired_synthesis),
            policy=build_default_next_session_policy(),
            created_at=_CREATED_AT,
        )


def test_m40_rejects_read_model_without_active_hypotheses():
    retired = _entry(lifecycle="retired")

    with pytest.raises(ValueError, match="at least one active"):
        build_next_session_plan(
            learner_read_model=_read_model(retired),
            evidence_syntheses=(),
            policy=build_default_next_session_policy(),
            created_at=_CREATED_AT,
        )


def test_m40_is_content_addressed_rebuildable_and_tamper_detectable():
    entry = _entry()
    plan, read_model, syntheses, policy = _plan_for(entry)
    rebuilt = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        policy=policy,
        created_at=_CREATED_AT,
    )

    assert rebuilt == plan
    assert plan.plan_id.startswith("next_session_plan_")
    validate_next_session_plan(
        plan,
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        policy=policy,
    )

    tampered_candidate = replace(plan.selected_candidate, policy_priority=1)
    tampered = replace(
        plan,
        selected_candidate=tampered_candidate,
        candidates=(tampered_candidate,),
    )
    with pytest.raises(ValueError, match="plan mismatch"):
        validate_next_session_plan(
            tampered,
            learner_read_model=read_model,
            evidence_syntheses=syntheses,
            policy=policy,
        )


def test_m40_custom_policy_can_change_cross_hypothesis_priority_transparently():
    policy = build_default_next_session_policy()
    priorities = tuple(
        (action, 120 if action == "ASSIGN_PRACTICE" else priority)
        for action, priority in policy.action_priorities
    )
    payload = {
        **policy.identity_payload(),
        "action_priorities": [list(item) for item in priorities],
    }
    custom = NextSessionPolicy(
        policy_id=policy.policy_id,
        version="test-practice-first",
        fingerprint="placeholder",
        action_priorities=priorities,
        challenge_supported_without_counterevidence=(
            policy.challenge_supported_without_counterevidence
        ),
        challenge_supported_with_unresolved_alternatives=(
            policy.challenge_supported_with_unresolved_alternatives
        ),
    )
    custom_payload = {
        **custom.identity_payload(),
    }
    import hashlib
    from chess_mentor_engine.chess import canonical_json

    custom = replace(
        custom,
        fingerprint=hashlib.sha256(
            canonical_json(custom_payload).encode("utf-8")
        ).hexdigest(),
    )
    assert payload["action_priorities"] != policy.identity_payload()["action_priorities"]

    challenged = _entry("h1", status="contradicted")
    practice = _entry("h2", intervention_state="selected")
    read_model = _read_model(challenged, practice)
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(
            _synthesis(read_model, challenged),
            _synthesis(read_model, practice),
        ),
        policy=custom,
        created_at=_CREATED_AT,
    )

    assert plan.selected_candidate.action == "ASSIGN_PRACTICE"
