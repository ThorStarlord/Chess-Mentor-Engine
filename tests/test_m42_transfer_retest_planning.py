from __future__ import annotations

from dataclasses import replace

import pytest
from test_m9_qualification import _intervention
from test_m40_next_session_planner import _entry, _read_model, _synthesis

from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.evaluation import OutcomePosition, OutcomeReference
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    build_default_next_session_policy,
    build_default_transfer_retest_policy,
    build_next_session_plan,
    build_transfer_retest_plan,
    define_transfer_position_candidate,
    validate_transfer_position_candidate,
    validate_transfer_retest_plan,
    validate_transfer_retest_policy,
)
from chess_mentor_engine.training import (
    InterventionSelectionDecision,
    InterventionSelectionPolicyRef,
    TrainingInterventionRef,
)

CREATED_AT = "2026-09-11T16:00:00-03:00"


def _sources(*, far: bool = False):
    outcomes = (("practice", "supported"),)
    if far:
        outcomes += (("near_transfer", "supported"),)
    entry = _entry(intervention_state="selected", outcomes=outcomes)
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T15:30:00-03:00",
    )
    expected = "RUN_FAR_TRANSFER_TEST" if far else "RUN_NEAR_TRANSFER_TEST"
    assert plan.selected_candidate.action == expected
    intervention = replace(
        _intervention(
            key="forcing-resource-scan",
            exercise_key="forcing-resource-scan-ex",
        ),
        intervention_id="intervention-1",
        fingerprint="intervention-fingerprint",
    )
    ref = TrainingInterventionRef(
        intervention_id=intervention.intervention_id,
        intervention_key=intervention.intervention_key,
        version=intervention.version,
        fingerprint=intervention.fingerprint,
    )
    selection = InterventionSelectionDecision(
        selection_id="selection-1",
        fingerprint="selection-fingerprint-1",
        participant_id=read_model.participant_id,
        ledger_snapshot_id="m7-ledger-snapshot",
        ledger_snapshot_fingerprint="m7-ledger-fingerprint",
        hypothesis_revision_ref=plan.selected_candidate.hypothesis_revision_ref,
        registry_id="registry-1",
        registry_fingerprint="registry-fingerprint-1",
        policy_ref=InterventionSelectionPolicyRef(
            policy_id="m9-policy",
            version="1",
            fingerprint="m9-policy-fingerprint",
        ),
        mapping_refs=(),
        decision="selected",
        selected_intervention_ref=ref,
        decision_reasons=("Exact M9 selection fixture.",),
        created_at="2026-09-11T15:20:00-03:00",
    )
    return plan, intervention, selection


def _position(position_id: str, game_id: str, fen: str) -> OutcomePosition:
    return OutcomePosition(
        position_id=position_id,
        game_id=game_id,
        fen=fen,
        source_ref=OutcomeReference(
            "canonical_position",
            position_id,
            f"fingerprint-{position_id}",
        ),
    )


def _candidate(
    position_id: str,
    game_id: str,
    fen: str,
    *,
    relation: str = "same_target",
    variation: str = "near",
    freshness: str = "fresh",
    concept_ids: tuple[str, ...] = ("tactic.fork",),
):
    return define_transfer_position_candidate(
        position=_position(position_id, game_id, fen),
        semantic_relation=relation,
        surface_variation=variation,
        freshness=freshness,
        concept_ids=concept_ids,
        held_constant=("target tactical recognition skill",),
        varied_dimensions=("piece geometry",),
        source_refs=(
            EvidenceSynthesisReference(
                "canonical_candidate_source",
                f"source-{position_id}",
                f"source-fingerprint-{position_id}",
            ),
        ),
        rationale="Explicitly curated transfer candidate for hermetic qualification.",
    )


def test_m42_near_transfer_selects_fresh_semantically_same_varied_position():
    plan, intervention, selection = _sources()
    candidate = _candidate(
        "near-1",
        "game-near-1",
        "8/8/8/8/8/8/8/K6k w - - 0 1",
    )
    result = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Recognize and compare the target tactical relation.",
        policy=build_default_transfer_retest_policy(),
        created_at=CREATED_AT,
        ontology=OntologyRegistry.load_default(),
    )

    assert result.transfer_kind == "near"
    assert result.planning_status == "planned"
    assert result.selected_candidate == candidate
    assert result.plan_authority == "planning_only"
    assert result.outcome_effect == "not_established"
    assert result.mastery == "not_established"


def test_m42_far_transfer_requires_material_surface_change():
    plan, intervention, selection = _sources(far=True)
    near = _candidate(
        "far-near",
        "game-far-near",
        "8/8/8/8/8/8/7k/K7 w - - 0 1",
        variation="near",
    )
    far = _candidate(
        "far-1",
        "game-far-1",
        "8/8/8/8/8/7k/8/K7 w - - 0 1",
        relation="related_target",
        variation="different",
    )
    result = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(near, far),
        practice_position_reuse_keys=(),
        measurement_target=(
            "Test the same bounded skill in a materially different context."
        ),
        policy=build_default_transfer_retest_policy(),
        created_at=CREATED_AT,
        ontology=OntologyRegistry.load_default(),
    )

    assert result.transfer_kind == "far"
    assert tuple(item.candidate_id for item in result.eligible_candidates) == (
        far.candidate_id,
    )
    assert result.selected_candidate == far


def test_m42_excludes_exact_practice_replay_even_when_candidate_is_marked_fresh():
    plan, intervention, selection = _sources()
    candidate = _candidate(
        "practice-replay",
        "practice-game",
        "8/8/8/8/8/8/6k1/K7 w - - 0 1",
    )
    result = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(candidate.position.reuse_key,),
        measurement_target="Transfer target.",
        policy=build_default_transfer_retest_policy(),
        created_at=CREATED_AT,
    )

    assert result.planning_status == "no_eligible_candidate"
    assert result.selected_candidate is None
    assert result.blocking_uncertainty


def test_m42_excludes_previously_exposed_candidate():
    plan, intervention, selection = _sources()
    candidate = _candidate(
        "exposed-1",
        "game-exposed",
        "8/8/8/8/8/6k1/8/K7 w - - 0 1",
        freshness="previously_exposed",
    )
    result = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Transfer target.",
        policy=build_default_transfer_retest_policy(),
        created_at=CREATED_AT,
    )

    assert result.planning_status == "no_eligible_candidate"


def test_m42_rejects_non_transfer_m40_action():
    entry = _entry(intervention_state="selected")
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T15:30:00-03:00",
    )
    assert plan.selected_candidate.action == "ASSIGN_PRACTICE"
    _, intervention, selection = _sources()
    selection = replace(
        selection,
        hypothesis_revision_ref=plan.selected_candidate.hypothesis_revision_ref,
    )
    with pytest.raises(ValueError, match="near/far transfer"):
        build_transfer_retest_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=selection,
            intervention=intervention,
            candidate_positions=(),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=build_default_transfer_retest_policy(),
            created_at=CREATED_AT,
        )


def test_m42_rejects_cross_participant_or_stale_m9_selection():
    plan, intervention, selection = _sources()
    with pytest.raises(ValueError, match="participant mismatch"):
        build_transfer_retest_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=replace(selection, participant_id="P02"),
            intervention=intervention,
            candidate_positions=(),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=build_default_transfer_retest_policy(),
            created_at=CREATED_AT,
        )
    stale_ref = replace(
        selection.hypothesis_revision_ref,
        revision_id="stale-revision",
    )
    with pytest.raises(ValueError, match="revision mismatch"):
        build_transfer_retest_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=replace(selection, hypothesis_revision_ref=stale_ref),
            intervention=intervention,
            candidate_positions=(),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=build_default_transfer_retest_policy(),
            created_at=CREATED_AT,
        )


def test_m42_rejects_unclear_m9_selection_and_intervention_identity_drift():
    plan, intervention, selection = _sources()
    with pytest.raises(ValueError, match="selected M9 intervention"):
        build_transfer_retest_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=replace(
                selection,
                decision="unclear",
                selected_intervention_ref=None,
            ),
            intervention=intervention,
            candidate_positions=(),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=build_default_transfer_retest_policy(),
            created_at=CREATED_AT,
        )
    with pytest.raises(ValueError, match="intervention identity mismatch"):
        build_transfer_retest_plan(
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=selection,
            intervention=replace(intervention, fingerprint="drifted-intervention"),
            candidate_positions=(),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=build_default_transfer_retest_policy(),
            created_at=CREATED_AT,
        )


def test_m42_candidate_policy_and_plan_are_tamper_detectable():
    candidate = _candidate(
        "tamper-1",
        "tamper-game",
        "8/8/8/8/8/5k2/8/K7 w - - 0 1",
    )
    validate_transfer_position_candidate(candidate)
    with pytest.raises(ValueError, match="candidate fingerprint mismatch"):
        validate_transfer_position_candidate(
            replace(candidate, rationale="tampered rationale")
        )

    policy = build_default_transfer_retest_policy()
    validate_transfer_retest_policy(policy)
    with pytest.raises(ValueError, match="policy fingerprint mismatch"):
        validate_transfer_retest_policy(
            replace(policy, require_fresh_candidate=False)
        )

    plan, intervention, selection = _sources()
    result = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Transfer target.",
        policy=policy,
        created_at=CREATED_AT,
    )
    validate_transfer_retest_plan(
        result,
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Transfer target.",
        policy=policy,
    )
    with pytest.raises(ValueError, match="plan mismatch"):
        validate_transfer_retest_plan(
            replace(result, measurement_target="tampered target"),
            next_session_plan=plan,
            proposal=plan.selected_candidate,
            selection=selection,
            intervention=intervention,
            candidate_positions=(candidate,),
            practice_position_reuse_keys=(),
            measurement_target="Transfer target.",
            policy=policy,
        )
