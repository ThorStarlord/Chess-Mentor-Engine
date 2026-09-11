from __future__ import annotations

from dataclasses import replace

import pytest
from test_m40_next_session_planner import _entry, _read_model, _revision_ref, _synthesis

from chess_mentor_engine.learner_intelligence import (
    HypothesisEvidenceUnitSynthesis,
    build_default_evidence_acquisition_policy,
    build_default_next_session_policy,
    build_evidence_acquisition_plan,
    build_next_session_plan,
    validate_evidence_acquisition_plan,
)
from chess_mentor_engine.learning import (
    HypothesisEvidenceLink,
    HypothesisEvidenceLinkRef,
    HypothesisM6EvidenceRef,
    HypothesisMappingProvenance,
)

CREATED_AT = "2026-09-11T14:00:00-03:00"


def _link(
    revision_ref,
    link_id,
    relation,
    position_id,
    game_id,
    *,
    participant="P01",
    condition="clean",
):
    return HypothesisEvidenceLink(
        link_id=link_id,
        fingerprint=f"fp-{link_id}",
        hypothesis_revision_ref=revision_ref,
        participant_id=participant,
        reasoning_context_ref=HypothesisM6EvidenceRef(
            "reasoning_context", f"ctx-{link_id}", f"ctx-fp-{link_id}"
        ),
        assessment_ref=HypothesisM6EvidenceRef(
            "reasoning_assessment", f"assess-{link_id}", f"assess-fp-{link_id}"
        ),
        assertion_refs=(),
        source_position_id=position_id,
        source_game_id=game_id,
        relation=relation,
        context_refs=(),
        measurement_condition=condition,
        basis_kind="deterministic_mapping",
        mapping_provenance=HypothesisMappingProvenance(
            "deterministic_mapping", f"map-{link_id}", f"map-fp-{link_id}"
        ),
        created_at="2026-09-11T13:30:00-03:00",
    )


def _plan(entry, synthesis):
    read_model = _read_model(entry)
    return build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=() if synthesis is None else (synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T13:45:00-03:00",
    )


def _challenge():
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=0)
    plan = _plan(entry, synthesis)
    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"
    return plan, synthesis


def test_m43_challenge_prefers_new_game_candidate():
    plan, synthesis = _challenge()
    synthesis = replace(
        synthesis,
        source_position_ids=("p1",),
        source_game_ids=("g1",),
    )
    plan = _plan(_entry(), synthesis)
    revision = plan.selected_candidate.hypothesis_revision_ref
    old_game = _link(revision, "l1", "contradicts", "p2", "g1")
    new_game = _link(revision, "l2", "contradicts", "p3", "g2")

    result = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(old_game, new_game),
        policy=build_default_evidence_acquisition_policy(),
        created_at=CREATED_AT,
    )

    assert result.intent == "challenge_hypothesis"
    assert result.selected_candidate is not None
    assert result.selected_candidate.source_ref.ref_id == "l2"
    assert result.selected_candidate.candidate_kind == "potential_contradiction"
    assert result.decision_authority == "candidate_only"
    assert result.m7c_effect == "not_established"
    assert result.mastery == "not_established"


def test_m43_present_control_preserves_m7c_relation_and_concepts():
    entry = _entry(status="contradicted")
    read_model = _read_model(entry)
    unit = HypothesisEvidenceUnitSynthesis(
        recurrence_unit_id="u1",
        relation="successful_counterexample",
        source_position_id="p-control",
        source_game_id="g-control",
        independence_unit_id="g-control",
        link_refs=(HypothesisEvidenceLinkRef("l-control", "fp-control"),),
        context_ref_ids=(),
        measurement_conditions=("clean",),
        concept_ids=("tactic.fork",),
    )
    synthesis = replace(
        _synthesis(read_model, entry, counterexample_count=1),
        units=(unit,),
        source_position_ids=("p-control",),
        source_game_ids=("g-control",),
    )
    plan = _plan(entry, synthesis)
    assert plan.selected_candidate.action == "PRESENT_CONTROL"

    result = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(),
        policy=build_default_evidence_acquisition_policy(),
        created_at=CREATED_AT,
    )

    candidate = result.selected_candidate
    assert candidate is not None
    assert candidate.origin == "current_m7c_unit"
    assert candidate.upstream_relation == "successful_counterexample"
    assert candidate.concept_ids == ("tactic.fork",)


def test_m43_collect_new_evidence_does_not_promote_support_to_mastery():
    entry = _entry(status=None)
    plan = _plan(entry, None)
    link = _link(
        plan.selected_candidate.hypothesis_revision_ref,
        "l-support",
        "supports",
        "p-support",
        "g-support",
    )
    result = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=None,
        additional_links=(link,),
        policy=build_default_evidence_acquisition_policy(),
        created_at=CREATED_AT,
    )

    assert result.selected_candidate is not None
    assert result.selected_candidate.candidate_kind == "novel_retest_context"
    assert result.mastery == "not_established"


def test_m43_excludes_duplicate_position_and_contaminated_link():
    plan, synthesis = _challenge()
    synthesis = replace(
        synthesis,
        source_position_ids=("p1",),
        source_game_ids=("g1",),
    )
    plan = _plan(_entry(), synthesis)
    revision = plan.selected_candidate.hypothesis_revision_ref
    duplicate = _link(revision, "l-dup", "contradicts", "p1", "g2")
    contaminated = _link(
        revision,
        "l-bad",
        "contradicts",
        "p3",
        "g3",
        condition="contaminated",
    )

    result = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(duplicate, contaminated),
        policy=build_default_evidence_acquisition_policy(),
        created_at=CREATED_AT,
    )

    assert result.candidates == ()
    assert result.excluded_candidate_count == 2
    assert any("No eligible" in item for item in result.search_gaps)


def test_m43_rejects_cross_participant_and_stale_revision_links():
    plan, synthesis = _challenge()
    revision = plan.selected_candidate.hypothesis_revision_ref
    cross = _link(
        revision,
        "l-cross",
        "contradicts",
        "p2",
        "g2",
        participant="P02",
    )
    with pytest.raises(ValueError, match="participant mismatch"):
        build_evidence_acquisition_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            additional_links=(cross,),
            policy=build_default_evidence_acquisition_policy(),
            created_at=CREATED_AT,
        )

    stale = _link(
        _revision_ref("other"),
        "l-stale",
        "contradicts",
        "p3",
        "g3",
    )
    with pytest.raises(ValueError, match="current-revision mismatch"):
        build_evidence_acquisition_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            additional_links=(stale,),
            policy=build_default_evidence_acquisition_policy(),
            created_at=CREATED_AT,
        )


def test_m43_rejects_unsupported_teaching_action():
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan = _plan(entry, synthesis)
    assert plan.selected_candidate.action == "TEACH_CONCEPT"

    with pytest.raises(ValueError, match="cannot consume"):
        build_evidence_acquisition_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            additional_links=(),
            policy=build_default_evidence_acquisition_policy(),
            created_at=CREATED_AT,
        )


def test_m43_is_rebuildable_and_detects_tamper():
    plan, synthesis = _challenge()
    link = _link(
        plan.selected_candidate.hypothesis_revision_ref,
        "l-new",
        "contradicts",
        "p-new",
        "g-new",
    )
    policy = build_default_evidence_acquisition_policy()
    result = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(link,),
        policy=policy,
        created_at=CREATED_AT,
    )
    validate_evidence_acquisition_plan(
        result,
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(link,),
        policy=policy,
    )

    with pytest.raises(ValueError, match="plan mismatch"):
        validate_evidence_acquisition_plan(
            replace(result, excluded_candidate_count=9),
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            additional_links=(link,),
            policy=policy,
        )
