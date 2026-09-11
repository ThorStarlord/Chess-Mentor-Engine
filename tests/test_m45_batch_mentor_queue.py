from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest
from test_m40_next_session_planner import _entry, _read_model, _synthesis
from test_m42_transfer_retest_planning import _sources
from test_selection_policy import _apply, _comparison, _policy, _signal

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.evaluation import OutcomePosition, OutcomeReference
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    ProgressAcquisitionCandidate,
    bind_mentor_queue_batch_scope,
    build_default_mentor_queue_policy,
    build_default_next_session_policy,
    build_default_transfer_retest_policy,
    build_learner_progress_view,
    build_mentor_queue,
    build_next_session_plan,
    build_transfer_retest_plan,
    define_transfer_position_candidate,
    validate_mentor_queue,
    validate_mentor_queue_batch_scope,
    validate_mentor_queue_policy,
)
from chess_mentor_engine.selection import build_diagnostic_candidate_batch

CREATED_AT = "2026-09-11T17:00:00-03:00"


def _batch(*, same_game: bool = False):
    policy = _policy(
        requested_size=3,
        minimum_controls=0,
        maximum_per_game=None,
    )
    game_ids = (
        ("shared", "shared", "shared")
        if same_game
        else ("game-challenge", "game-cp", "game-transfer")
    )
    challenge = _comparison(0, game_id=game_ids[0])
    cp = _comparison(1 if same_game else 0, game_id=game_ids[1])
    transfer = _comparison(2 if same_game else 0, game_id=game_ids[2])
    pool = (
        _apply(
            challenge,
            (
                _signal(
                    challenge,
                    "TOP_CANDIDATE_SEPARATION",
                    {"exact_centipawn_separation_for_mover": 10},
                ),
            ),
            policy,
        ),
        _apply(cp, (_signal(cp, "EXACT_CP_DELTA", 500),), policy),
        _apply(transfer, (_signal(transfer, "EXACT_CP_DELTA", 80),), policy),
    )
    return build_diagnostic_candidate_batch(results=pool, policy=policy)


def _scope(batch, participant_id: str = "P01"):
    return bind_mentor_queue_batch_scope(
        participant_id=participant_id,
        diagnostic_batch=batch,
        source_refs=(
            EvidenceSynthesisReference(
                "participant_batch_authority",
                "batch-import-P01",
                "batch-import-fingerprint-P01",
            ),
        ),
    )


def _rehash_view(view, hypotheses):
    provisional = replace(
        view,
        view_id="provisional",
        fingerprint="provisional",
        hypotheses=hypotheses,
    )
    fingerprint = hashlib.sha256(
        canonical_json(provisional.identity_payload()).encode("utf-8")
    ).hexdigest()
    return replace(
        provisional,
        view_id=f"learner_progress_view_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _challenge_view(challenge_game: str, challenge_position: str):
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=0)
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T16:30:00-03:00",
    )
    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T16:35:00-03:00",
    )
    hypothesis = view.hypotheses[0]
    acquisition = ProgressAcquisitionCandidate(
        candidate_kind="potential_contradiction",
        origin="additional_m7b_link",
        source_position_id=challenge_position,
        source_game_id=challenge_game,
        semantic_coverage="available",
        concept_ids=("tactic.fork",),
    )
    enriched = replace(
        hypothesis,
        acquisition_ref=EvidenceSynthesisReference(
            "evidence_acquisition_plan",
            "acquisition-h1",
            "acquisition-fingerprint-h1",
        ),
        acquisition_intent="challenge_hypothesis",
        acquisition_candidates=(acquisition,),
    )
    return _rehash_view(view, (enriched,))


def _transfer_view_and_plan(transfer_game: str, transfer_position: str):
    plan, intervention, selection = _sources()
    entry = _entry(
        intervention_state="selected",
        outcomes=(("practice", "supported"),),
    )
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T16:35:00-03:00",
    )
    transfer_candidate = define_transfer_position_candidate(
        position=OutcomePosition(
            position_id=transfer_position,
            game_id=transfer_game,
            fen="8/8/8/8/8/8/8/K6k w - - 0 1",
            source_ref=OutcomeReference(
                "canonical_position",
                transfer_position,
                f"fingerprint-{transfer_position}",
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
                "batch_transfer_candidate",
                transfer_position,
                f"source-{transfer_position}",
            ),
        ),
        rationale="Participant-local near-transfer candidate.",
    )
    transfer_plan = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(transfer_candidate,),
        practice_position_reuse_keys=(),
        measurement_target="Test the current tactical recognition target.",
        policy=build_default_transfer_retest_policy(),
        created_at="2026-09-11T16:40:00-03:00",
        ontology=OntologyRegistry.load_default(),
    )
    return view, transfer_plan


def test_m45_challenge_value_outranks_larger_cp_only_candidate():
    batch = _batch()
    challenge = next(
        item for item in batch.candidates if item.game_id == "game-challenge"
    )
    view = _challenge_view(challenge.game_id, challenge.position_id)
    queue = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=_scope(batch),
        learner_progress_view=view,
        policy=build_default_mentor_queue_policy(requested_size=3),
        created_at=CREATED_AT,
    )

    assert queue.items[0].game_id == "game-challenge"
    assert queue.items[0].dimensions.contradiction_control_value == 3
    cp_item = next(item for item in queue.items if item.game_id == "game-cp")
    assert cp_item.dimensions.objective_importance == 2
    assert queue.decision_authority == "review_priority_proposal_only"
    assert queue.learner_effect == "not_established"
    assert queue.mastery == "not_established"


def test_m45_selected_m42_transfer_candidate_is_action_aligned():
    batch = _batch()
    transfer = next(
        item for item in batch.candidates if item.game_id == "game-transfer"
    )
    view, transfer_plan = _transfer_view_and_plan(
        transfer.game_id,
        transfer.position_id,
    )
    queue = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=_scope(batch),
        learner_progress_view=view,
        transfer_plans=(transfer_plan,),
        policy=build_default_mentor_queue_policy(requested_size=3),
        created_at=CREATED_AT,
    )

    assert queue.items[0].game_id == "game-transfer"
    assert queue.items[0].dimensions.action_alignment == 3
    assert queue.items[0].dimensions.transfer_value == 3
    assert queue.items[0].concept_ids == ("tactic.fork",)


def test_m45_enforces_queue_level_per_game_cap():
    batch = _batch(same_game=True)
    view = _challenge_view(
        batch.candidates[0].game_id,
        batch.candidates[0].position_id,
    )
    queue = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=_scope(batch),
        learner_progress_view=view,
        policy=build_default_mentor_queue_policy(
            requested_size=3,
            maximum_per_game=1,
        ),
        created_at=CREATED_AT,
    )

    assert len(queue.items) == 1
    assert queue.shortfall == 2
    assert len(queue.excluded_candidate_ids) == 2


def test_m45_rejects_cross_participant_scope_and_batch_identity_drift():
    batch = _batch()
    challenge = next(
        item for item in batch.candidates if item.game_id == "game-challenge"
    )
    view = _challenge_view(challenge.game_id, challenge.position_id)

    with pytest.raises(ValueError, match="participant mismatch"):
        build_mentor_queue(
            diagnostic_batch=batch,
            batch_scope=_scope(batch, participant_id="P02"),
            learner_progress_view=view,
            policy=build_default_mentor_queue_policy(requested_size=3),
            created_at=CREATED_AT,
        )

    scope = _scope(batch)
    drifted_ref = replace(
        scope.diagnostic_batch_ref,
        fingerprint="different-batch-fingerprint",
    )
    with pytest.raises(ValueError, match="diagnostic batch mismatch"):
        validate_mentor_queue_batch_scope(
            replace(scope, diagnostic_batch_ref=drifted_ref),
            diagnostic_batch=batch,
        )


def test_m45_objective_only_candidates_remain_visible_without_learner_claim():
    batch = _batch()
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan = build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T16:30:00-03:00",
    )
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T16:35:00-03:00",
    )
    queue = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=_scope(batch),
        learner_progress_view=view,
        policy=build_default_mentor_queue_policy(requested_size=3),
        created_at=CREATED_AT,
    )

    assert all(item.dimensions.learner_relevance == 0 for item in queue.items)
    assert all(not item.hypothesis_ids for item in queue.items)
    assert any(item.dimensions.objective_importance > 0 for item in queue.items)


def test_m45_policy_scope_and_queue_are_tamper_detectable_and_replay_stable():
    batch = _batch()
    challenge = next(
        item for item in batch.candidates if item.game_id == "game-challenge"
    )
    view = _challenge_view(challenge.game_id, challenge.position_id)
    scope = _scope(batch)
    policy = build_default_mentor_queue_policy(requested_size=3)

    validate_mentor_queue_batch_scope(scope, diagnostic_batch=batch)
    validate_mentor_queue_policy(policy)
    with pytest.raises(ValueError, match="policy fingerprint mismatch"):
        validate_mentor_queue_policy(replace(policy, requested_size=2))

    first = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=scope,
        learner_progress_view=view,
        policy=policy,
        created_at=CREATED_AT,
    )
    second = build_mentor_queue(
        diagnostic_batch=batch,
        batch_scope=scope,
        learner_progress_view=view,
        policy=policy,
        created_at=CREATED_AT,
    )
    assert first == second
    validate_mentor_queue(
        first,
        diagnostic_batch=batch,
        batch_scope=scope,
        learner_progress_view=view,
        policy=policy,
    )
    first_item = first.items[0]
    tampered_item = replace(first_item, reasons=("tampered queue reason",))
    tampered_queue = replace(
        first,
        items=(tampered_item, *first.items[1:]),
    )
    with pytest.raises(ValueError, match="queue mismatch"):
        validate_mentor_queue(
            tampered_queue,
            diagnostic_batch=batch,
            batch_scope=scope,
            learner_progress_view=view,
            policy=policy,
        )
