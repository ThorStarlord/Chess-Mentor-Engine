"""M21 candidate-to-tutor orchestration qualification and rejection coverage."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest
from test_reasoning_discrepancy_facts import T0, T1, _protocol, _upstream

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.tutoring import (
    CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION,
    CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION,
    CandidateTutorOrchestrationError,
    record_candidate_tutor_authorization,
    start_candidate_tutor_session,
)


def _authorization(
    *,
    selection_decision="selected",
    capture_consent="granted",
):
    upstream = _upstream()
    authorization = record_candidate_tutor_authorization(
        participant_id="P01",
        candidate=upstream.candidate,
        batch=upstream.batch,
        selection_decision=selection_decision,
        capture_consent=capture_consent,
        recorded_at=T0,
    )
    return upstream, authorization


def _rehash_authorization(authorization):
    payload = authorization.to_dict(include_identity=False)
    fingerprint = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return replace(
        authorization,
        authorization_id=f"candidate_tutor_auth_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def test_authorization_is_deterministic_and_explicitly_participant_authored() -> None:
    upstream = _upstream()
    first = record_candidate_tutor_authorization(
        participant_id="P01",
        candidate=upstream.candidate,
        batch=upstream.batch,
        selection_decision="selected",
        capture_consent="granted",
        recorded_at=T0,
    )
    second = record_candidate_tutor_authorization(
        participant_id="P01",
        candidate=upstream.candidate,
        batch=upstream.batch,
        selection_decision="selected",
        capture_consent="granted",
        recorded_at=T0,
    )

    assert first == second
    assert first.schema_version == CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION
    assert first.actor_kind == "participant"
    assert first.selection_decision == "selected"
    assert first.capture_consent == "granted"
    assert first.candidate_id == upstream.candidate.candidate_id
    assert first.batch_id == upstream.batch.batch_id


def test_authorization_alone_creates_no_m5_or_m8_state() -> None:
    _, authorization = _authorization()
    serialized = canonical_json(authorization.to_dict())

    assert "decision_context" not in serialized
    assert "tutor_session" not in serialized
    assert "reasoning_discrepancy" not in serialized
    assert "learner_hypothesis" not in serialized


def test_authorized_candidate_starts_exact_m5_and_initial_m8_session() -> None:
    upstream, authorization = _authorization()

    context, session, launch = start_candidate_tutor_session(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=T1,
    )

    assert context.participant_id == "P01"
    assert context.session_id == f"m21_{authorization.authorization_id}"
    assert context.position_id == upstream.position.position_id
    assert context.diagnostic_candidate_ref.ref_id == upstream.candidate.candidate_id
    assert context.diagnostic_batch_ref is not None
    assert context.diagnostic_batch_ref.ref_id == upstream.batch.batch_id

    assert session.state == "selected"
    assert session.capture_session.context == context
    assert session.position_presentation is None
    assert session.comparison is None
    assert session.hypothesis_context is None
    assert session.explanation is None
    assert tuple(event.kind for event in session.events) == ("SESSION_STARTED",)

    assert launch["schema_version"] == CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION
    assert launch["authorization_ref"]["authorization_id"] == (
        authorization.authorization_id
    )
    assert launch["candidate_ref"]["candidate_id"] == upstream.candidate.candidate_id
    assert launch["batch_ref"]["batch_id"] == upstream.batch.batch_id
    assert launch["player_decision_context_ref"]["context_id"] == context.context_id
    assert launch["tutor_session_ref"]["tutor_session_id"] == session.tutor_session_id
    assert launch["tutor_session_ref"]["state"] == "selected"


def test_authorized_start_is_deterministic() -> None:
    upstream, authorization = _authorization()
    kwargs = dict(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=T1,
    )

    assert start_candidate_tutor_session(**kwargs) == start_candidate_tutor_session(
        **kwargs
    )


def test_launch_explicitly_denies_automatic_m6_m7_and_training_authority() -> None:
    upstream, authorization = _authorization()
    _, session, launch = start_candidate_tutor_session(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=T1,
    )

    denied = set(launch["authority_boundary"]["not_created"])
    assert "m6_reasoning_discrepancy" in denied
    assert "m7_learner_hypothesis" in denied
    assert "m9_training_selection" in denied
    assert "mentor_explanation" in denied
    assert session.comparison is None
    assert session.hypothesis_context is None
    assert session.explanation is None


def test_selected_candidate_without_capture_consent_cannot_start() -> None:
    upstream, authorization = _authorization(capture_consent="declined")

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="explicit capture consent",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_declined_candidate_cannot_start_tutor_session() -> None:
    upstream, authorization = _authorization(
        selection_decision="declined",
        capture_consent="declined",
    )

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="explicit candidate selection",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_declined_candidate_cannot_grant_capture_consent() -> None:
    upstream = _upstream()

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="cannot be granted for a declined candidate",
    ):
        record_candidate_tutor_authorization(
            participant_id="P01",
            candidate=upstream.candidate,
            batch=upstream.batch,
            selection_decision="declined",
            capture_consent="granted",
            recorded_at=T0,
        )


def test_candidate_signal_content_drift_is_rejected_even_with_same_signal_id() -> None:
    upstream = _upstream()
    original = upstream.candidate.signals[0]
    drifted_signal = replace(original, detail="tampered after M18 selection")
    drifted_candidate = replace(
        upstream.candidate,
        signals=(drifted_signal, *upstream.candidate.signals[1:]),
    )

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="signal identity mismatch",
    ):
        record_candidate_tutor_authorization(
            participant_id="P01",
            candidate=drifted_candidate,
            batch=upstream.batch,
            selection_decision="selected",
            capture_consent="granted",
            recorded_at=T0,
        )


def test_candidate_identity_drift_is_rejected_before_authorization() -> None:
    upstream = _upstream()
    drifted = replace(
        upstream.candidate,
        provenance=replace(upstream.candidate.provenance, root_ply_index=999),
    )

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="candidate identity mismatch",
    ):
        record_candidate_tutor_authorization(
            participant_id="P01",
            candidate=drifted,
            batch=upstream.batch,
            selection_decision="selected",
            capture_consent="granted",
            recorded_at=T0,
        )


def test_batch_identity_drift_is_rejected_before_authorization() -> None:
    upstream = _upstream()
    drifted = replace(upstream.batch, source_pool_fingerprint="drifted-source-pool")

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="batch identity mismatch",
    ):
        record_candidate_tutor_authorization(
            participant_id="P01",
            candidate=upstream.candidate,
            batch=drifted,
            selection_decision="selected",
            capture_consent="granted",
            recorded_at=T0,
        )


def test_rehashed_authorization_cannot_switch_candidate_fingerprint() -> None:
    upstream, authorization = _authorization()
    tampered = replace(authorization, candidate_fingerprint="0" * 64)
    tampered = _rehash_authorization(tampered)

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="authorization candidate fingerprint mismatch",
    ):
        start_candidate_tutor_session(
            authorization=tampered,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_authorization_identity_tampering_is_rejected() -> None:
    upstream, authorization = _authorization()
    tampered = replace(authorization, fingerprint="0" * 64)

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="authorization fingerprint mismatch",
    ):
        start_candidate_tutor_session(
            authorization=tampered,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_candidate_game_provenance_must_match_canonical_game() -> None:
    upstream, authorization = _authorization()
    drifted_game = replace(
        upstream.game,
        semantic_fingerprint="different-semantic-fingerprint",
    )

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="semantic fingerprint mismatch",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=drifted_game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_noncanonical_position_copy_is_rejected() -> None:
    upstream, authorization = _authorization()
    drifted_position = replace(upstream.position, fen=upstream.position.fen + " ")

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="exactly match canonical game position",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=drifted_position,
            capture_protocol=_protocol(),
            created_at=T1,
        )


def test_launch_cannot_predate_participant_authorization() -> None:
    upstream, authorization = _authorization()

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="cannot predate participant authorization",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=_protocol(),
            created_at="2026-09-08T08:59:59-03:00",
        )


def test_invalid_m8_capture_protocol_fails_closed_through_bridge() -> None:
    upstream, authorization = _authorization()
    protocol = replace(
        _protocol(),
        stages=(_protocol().stages[1],),
    )

    with pytest.raises(
        CandidateTutorOrchestrationError,
        match="M5/M8 candidate-to-tutor bridge rejected input",
    ):
        start_candidate_tutor_session(
            authorization=authorization,
            candidate=upstream.candidate,
            batch=upstream.batch,
            game=upstream.game,
            position=upstream.position,
            capture_protocol=protocol,
            created_at=T1,
        )
