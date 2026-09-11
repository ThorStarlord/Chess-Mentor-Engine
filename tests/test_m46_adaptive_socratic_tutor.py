from __future__ import annotations

from dataclasses import replace

import pytest
from test_m8_qualification import (
    _complete_session,
    _through_frozen,
    _through_position,
    _through_reveal,
)
from test_m40_next_session_planner import _entry, _read_model, _synthesis
from test_m42_transfer_retest_planning import _sources
from test_m45_batch_mentor_queue import _batch, _challenge_view, _scope

from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.evaluation import OutcomePosition, OutcomeReference
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    build_default_mentor_queue_policy,
    build_default_next_session_policy,
    build_default_transfer_retest_policy,
    build_learner_progress_view,
    build_mentor_queue,
    build_next_session_plan,
    build_transfer_retest_plan,
    define_transfer_position_candidate,
)
from chess_mentor_engine.tutoring import (
    build_adaptive_tutor_proposal,
    build_default_adaptive_tutor_policy,
    validate_adaptive_tutor_policy,
    validate_adaptive_tutor_proposal,
)

CREATED_AT = "2026-09-11T18:00:00-03:00"


def _view(*, contradiction_count: int = 1):
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(
        read_model,
        entry,
        contradiction_count=contradiction_count,
    )
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T17:30:00-03:00",
    )
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T17:35:00-03:00",
    )
    return view


def _transfer_view_and_plan_for_session(session):
    next_plan, intervention, selection = _sources()
    entry = _entry(
        intervention_state="selected",
        outcomes=(("practice", "supported"),),
    )
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=next_plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T17:35:00-03:00",
    )
    context = session.capture_session.context
    candidate = define_transfer_position_candidate(
        position=OutcomePosition(
            position_id=context.position_id,
            game_id=context.game_id,
            fen="8/8/8/8/8/8/8/K6k w - - 0 1",
            source_ref=OutcomeReference(
                "canonical_position",
                context.position_id,
                "m46-transfer-position-fingerprint",
            ),
        ),
        semantic_relation="same_target",
        surface_variation="near",
        freshness="fresh",
        concept_ids=("tactic.fork",),
        held_constant=("target tactical recognition skill",),
        varied_dimensions=("piece geometry",),
        source_refs=(
            EvidenceSynthesisReference(
                "m46_transfer_candidate",
                context.position_id,
                "m46-transfer-candidate-source-fingerprint",
            ),
        ),
        rationale="Exact tutor position is the qualified M42 near-transfer target.",
    )
    transfer_plan = build_transfer_retest_plan(
        next_session_plan=next_plan,
        proposal=next_plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Test the current tactical recognition target.",
        policy=build_default_transfer_retest_policy(),
        created_at="2026-09-11T17:40:00-03:00",
        ontology=OntologyRegistry.load_default(),
    )
    return view, transfer_plan


def test_m46_blocks_adaptive_tutoring_until_m8_baseline_is_frozen():
    _, session, _ = _through_position()
    view = _view()
    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )

    assert proposal.action == "CONTINUE_BASELINE_CAPTURE"
    assert proposal.exposure_effect == "none"
    assert proposal.response_evidence_class == "baseline_unassisted"
    assert proposal.rendered_prompt is None
    assert proposal.blocking_uncertainty


def test_m46_frozen_teaching_uses_ontology_recognition_question_as_assisted_hint():
    _, session = _through_frozen()
    view = _view(contradiction_count=1)
    assert view.hypotheses[0].next_action == "TEACH_CONCEPT"

    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )

    assert proposal.action == "GIVE_CONCEPT_HINT"
    assert "how many valuable enemy targets" in proposal.rendered_prompt.lower()
    assert proposal.exposure_effect == "assisted_followup"
    assert proposal.response_evidence_class == "assisted_followup"
    assert proposal.execution_authority == "proposal_only"
    assert proposal.model_language == "not_generated"
    assert proposal.mastery == "not_established"


def test_m46_frozen_challenge_allows_reveal_only_after_clean_baseline():
    _, session = _through_frozen()
    view = _view(contradiction_count=0)
    assert view.hypotheses[0].next_action == "CHALLENGE_HYPOTHESIS"

    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )

    assert proposal.action == "REVEAL_ENGINE_LINE"
    assert proposal.exposure_effect == "objective_reveal"
    assert proposal.response_evidence_class == "none"


def test_m46_post_reveal_response_is_explicitly_reflection_not_baseline():
    _, session = _through_reveal()
    view = _view()
    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )

    assert proposal.action == "ASK_REFLECTION"
    assert proposal.exposure_effect == "post_reveal"
    assert proposal.response_evidence_class == "post_reveal_reflection"
    assert "what changed" in proposal.rendered_prompt.lower()


def test_m46_completed_session_proposes_no_further_action():
    session, _ = _complete_session()
    view = _view()
    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )

    assert proposal.action == "NO_FURTHER_ACTION"
    assert proposal.rendered_prompt is None
    assert proposal.response_evidence_class == "none"


def test_m46_transfer_action_requires_exact_m42_plan_then_allows_assisted_hint():
    _, session = _through_frozen()
    view, transfer_plan = _transfer_view_and_plan_for_session(session)
    assert view.hypotheses[0].next_action == "RUN_NEAR_TRANSFER_TEST"

    blocked = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )
    assert blocked.action == "NO_FURTHER_ACTION"
    assert blocked.blocking_uncertainty

    proposed = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        transfer_plan=transfer_plan,
        policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )
    assert proposed.action == "GIVE_MINIMAL_HINT"
    assert proposed.transfer_plan_ref is not None
    assert proposed.response_evidence_class == "assisted_followup"


def test_m46_rejects_mentor_queue_item_for_different_tutor_position():
    _, session = _through_frozen()
    batch = _batch()
    challenge = next(
        item for item in batch.candidates if item.game_id == "game-challenge"
    )
    queue_view = _challenge_view(challenge.game_id, challenge.position_id)
    queue = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=_scope(batch),
        learner_progress_view=queue_view,
        policy=build_default_mentor_queue_policy(requested_size=3),
        created_at="2026-09-11T17:45:00-03:00",
    )

    with pytest.raises(ValueError, match="does not match tutor position"):
        build_adaptive_tutor_proposal(
            tutor_session=session,
            learner_progress_view=queue_view,
            hypothesis_id=queue_view.hypotheses[0].hypothesis_id,
            mentor_queue=queue,
            mentor_queue_item=queue.items[0],
            policy=build_default_adaptive_tutor_policy(),
            created_at=CREATED_AT,
        )


def test_m46_session_policy_and_proposal_are_tamper_detectable():
    _, session = _through_frozen()
    view = _view()
    policy = build_default_adaptive_tutor_policy()
    validate_adaptive_tutor_policy(policy)

    with pytest.raises(ValueError, match="policy fingerprint mismatch"):
        validate_adaptive_tutor_policy(
            replace(policy, post_reveal_reflection=False)
        )

    with pytest.raises(ValueError, match="snapshot fingerprint mismatch"):
        build_adaptive_tutor_proposal(
            tutor_session=replace(session, snapshot_fingerprint="tampered"),
            learner_progress_view=view,
            hypothesis_id=view.hypotheses[0].hypothesis_id,
            policy=policy,
            created_at=CREATED_AT,
        )

    proposal = build_adaptive_tutor_proposal(
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=policy,
        created_at=CREATED_AT,
    )
    validate_adaptive_tutor_proposal(
        proposal,
        tutor_session=session,
        learner_progress_view=view,
        hypothesis_id=view.hypotheses[0].hypothesis_id,
        policy=policy,
    )
    with pytest.raises(ValueError, match="proposal mismatch"):
        validate_adaptive_tutor_proposal(
            replace(proposal, rendered_prompt="tampered prompt"),
            tutor_session=session,
            learner_progress_view=view,
            hypothesis_id=view.hypotheses[0].hypothesis_id,
            policy=policy,
        )
