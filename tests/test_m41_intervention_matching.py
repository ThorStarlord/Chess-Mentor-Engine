from __future__ import annotations

from dataclasses import replace

import pytest
from test_m40_next_session_planner import _entry, _plan_for
from test_m9_qualification import _intervention, _registry, _training_author

from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.learner_intelligence import (
    build_default_intervention_matching_policy,
    build_intervention_candidate_set,
    define_intervention_semantic_profile,
    validate_intervention_candidate_set,
    validate_intervention_matching_policy,
    validate_intervention_semantic_profile,
)

CREATED_AT = "2026-09-11T14:30:00-03:00"


def _teaching_plan(*, concept_ids=("tactic.fork",)):
    plan, read_model, syntheses, _ = _plan_for(_entry(), contradiction_count=1)
    synthesis = replace(syntheses[0], concept_ids=concept_ids)
    plan = replace(
        plan,
        candidates=tuple(
            replace(item, concept_ids=concept_ids, synthesis_ref=replace(
                item.synthesis_ref,
                ref_id=synthesis.synthesis_id,
                fingerprint=synthesis.fingerprint,
            ))
            for item in plan.candidates
        ),
        selected_candidate=None,
    )
    plan = replace(plan, selected_candidate=plan.candidates[0])
    return plan, read_model, synthesis


def _profile(intervention, ontology, *, target=(), reinforce=(), contraindicated=(), modes=()):
    return define_intervention_semantic_profile(
        intervention=intervention,
        ontology=ontology,
        target_concept_ids=target,
        reinforce_concept_ids=reinforce,
        contraindicated_concept_ids=contraindicated,
        training_modes=modes,
        provenance=_training_author(),
        created_at="2026-09-11T14:20:00-03:00",
    )


def test_m41_ranks_exact_target_before_mode_only_and_missing_profile():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan()
    exact = _intervention(key="fork-target", exercise_key="fork-target-ex")
    mode = _intervention(key="fork-mode", exercise_key="fork-mode-ex")
    missing = _intervention(key="unprofiled", exercise_key="unprofiled-ex")
    registry = _registry(exact, mode, missing)
    profiles = (
        _profile(exact, ontology, target=("tactic.fork",)),
        _profile(mode, ontology, modes=("fork_recognition",)),
    )

    result = build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=profiles,
        policy=build_default_intervention_matching_policy(),
        created_at=CREATED_AT,
    )

    assert tuple(item.status for item in result.ranked_candidates) == (
        "eligible_candidate",
        "possible_candidate",
        "insufficient_information",
    )
    assert result.ranked_candidates[0].target_concept_matches == ("tactic.fork",)
    assert result.ranked_candidates[1].training_mode_matches == ("fork_recognition",)
    assert result.selection_authority == "not_exercised"
    assert result.efficacy == "not_established"
    assert result.mastery == "not_established"


def test_m41_preserves_multiple_eligible_candidates_without_selecting_one():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan()
    first = _intervention(key="fork-a", exercise_key="fork-a-ex")
    second = _intervention(key="fork-b", exercise_key="fork-b-ex")
    registry = _registry(first, second)
    profiles = (
        _profile(first, ontology, target=("tactic.fork",)),
        _profile(second, ontology, target=("tactic.fork",)),
    )

    result = build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=profiles,
        policy=build_default_intervention_matching_policy(),
        created_at=CREATED_AT,
    )

    assert all(item.status == "eligible_candidate" for item in result.ranked_candidates)
    assert result.selection_authority == "not_exercised"
    assert not hasattr(result, "selected_intervention")


def test_m41_explicit_contraindication_is_ineligible():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan()
    intervention = _intervention(key="wrong-fit", exercise_key="wrong-fit-ex")
    registry = _registry(intervention)
    profile = _profile(
        intervention,
        ontology,
        target=("tactic.deflection",),
        contraindicated=("tactic.fork",),
    )

    result = build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=(profile,),
        policy=build_default_intervention_matching_policy(),
        created_at=CREATED_AT,
    )

    candidate = result.ranked_candidates[0]
    assert candidate.status == "ineligible"
    assert candidate.contraindication_matches == ("tactic.fork",)


def test_m41_empty_concept_context_stays_insufficient_instead_of_parsing_prose():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan(concept_ids=())
    intervention = _intervention()
    result = build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=_registry(intervention),
        profiles=(),
        policy=build_default_intervention_matching_policy(),
        created_at=CREATED_AT,
    )

    assert result.target_concept_ids == ()
    assert result.ranked_candidates[0].status == "insufficient_information"
    assert any("will not infer concepts from free text" in gap for gap in result.matching_gaps)


def test_m41_rejects_non_teaching_m40_action():
    ontology = OntologyRegistry.load_default()
    plan, _, syntheses, _ = _plan_for(_entry(), contradiction_count=0)
    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"

    with pytest.raises(ValueError, match="only consumes M40 TEACH_CONCEPT"):
        build_intervention_candidate_set(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=syntheses[0],
            ontology=ontology,
            intervention_registry=_registry(),
            profiles=(),
            policy=build_default_intervention_matching_policy(),
            created_at=CREATED_AT,
        )


def test_m41_rejects_profile_for_unregistered_intervention():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan()
    registered = _intervention(key="registered", exercise_key="registered-ex")
    outsider = _intervention(key="outsider", exercise_key="outsider-ex")
    profile = _profile(outsider, ontology, target=("tactic.fork",))

    with pytest.raises(ValueError, match="unregistered intervention"):
        build_intervention_candidate_set(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            ontology=ontology,
            intervention_registry=_registry(registered),
            profiles=(profile,),
            policy=build_default_intervention_matching_policy(),
            created_at=CREATED_AT,
        )


def test_m41_profile_and_policy_identity_are_tamper_detectable():
    ontology = OntologyRegistry.load_default()
    intervention = _intervention()
    profile = _profile(intervention, ontology, target=("tactic.fork",))
    validate_intervention_semantic_profile(
        profile,
        intervention=intervention,
        ontology=ontology,
    )
    with pytest.raises(ValueError, match="profile mismatch"):
        validate_intervention_semantic_profile(
            replace(profile, fingerprint="tampered"),
            intervention=intervention,
            ontology=ontology,
        )

    policy = build_default_intervention_matching_policy()
    with pytest.raises(ValueError, match="policy fingerprint mismatch"):
        validate_intervention_matching_policy(replace(policy, fingerprint="tampered"))


def test_m41_candidate_set_is_rebuildable_and_tamper_detectable():
    ontology = OntologyRegistry.load_default()
    plan, _, synthesis = _teaching_plan()
    intervention = _intervention()
    registry = _registry(intervention)
    profile = _profile(intervention, ontology, target=("tactic.fork",))
    policy = build_default_intervention_matching_policy()
    result = build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=(profile,),
        policy=policy,
        created_at=CREATED_AT,
    )
    validate_intervention_candidate_set(
        result,
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=(profile,),
        policy=policy,
    )
    with pytest.raises(ValueError, match="candidate set mismatch"):
        validate_intervention_candidate_set(
            replace(result, matching_gaps=("tampered",)),
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            synthesis=synthesis,
            ontology=ontology,
            intervention_registry=registry,
            profiles=(profile,),
            policy=policy,
        )
