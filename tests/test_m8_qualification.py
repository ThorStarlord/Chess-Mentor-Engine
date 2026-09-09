from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest
from test_hypothesis_recurrence_assessment import _actor
from test_reasoning_discrepancy_assessment import _policy
from test_reasoning_discrepancy_facts import (
    _a1_prompt,
    _a2_prompt,
    _default_a1,
    _default_a2,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import build_position_context
from chess_mentor_engine.evidence import (
    CaptureStageSpec,
    define_capture_protocol,
    define_prompt,
    reference_decision_comparison,
    reference_position_analysis,
    reference_selection_signal,
)
from chess_mentor_engine.learning import (
    assess_reasoning_discrepancy,
    build_hypothesis_ledger_snapshot,
    build_reasoning_discrepancy_context,
    create_learner_hypothesis,
    derive_discrepancy_facts,
)
from chess_mentor_engine.tutoring import (
    TutorExplanationProvenance,
    TutorSessionError,
    attach_tutor_hypothesis_context,
    capture_tutor_response,
    complete_tutor_session,
    freeze_tutor_response,
    present_tutor_capture_stage,
    present_tutor_position,
    record_tutor_explanation,
    record_tutor_reasoning_comparison,
    reveal_tutor_objective_evidence,
    start_tutor_session,
)

S0 = "2026-09-08T10:00:00-03:00"
S1 = "2026-09-08T10:01:00-03:00"
S2 = "2026-09-08T10:02:00-03:00"
S3 = "2026-09-08T10:03:00-03:00"
S4 = "2026-09-08T10:04:00-03:00"
S5 = "2026-09-08T10:05:00-03:00"
S6 = "2026-09-08T10:06:00-03:00"
S7 = "2026-09-08T10:07:00-03:00"
S8 = "2026-09-08T10:08:00-03:00"
S9 = "2026-09-08T10:09:00-03:00"
S10 = "2026-09-08T10:10:00-03:00"
S11 = "2026-09-08T10:11:00-03:00"
S12 = "2026-09-08T10:12:00-03:00"
S13 = "2026-09-08T10:13:00-03:00"
S14 = "2026-09-08T10:14:00-03:00"


def _through_position():
    upstream = _upstream()
    session = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=S0,
    )
    packet = build_position_context(upstream.game, upstream.position)
    session, presentation = present_tutor_position(
        session,
        position_context=packet,
        shown_at=S1,
    )
    return upstream, session, presentation


def _through_frozen():
    upstream, session, _ = _through_position()
    session = present_tutor_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=S2,
    )
    session = capture_tutor_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        structured_response=_default_a1(),
        submitted_at=S3,
    )
    session = freeze_tutor_response(session, stage_id="A1", frozen_at=S4)
    session = present_tutor_capture_stage(
        session,
        stage_id="A2",
        prompt=_a2_prompt(),
        shown_at=S5,
    )
    session = capture_tutor_response(
        session,
        stage_id="A2",
        raw_response="I considered e4 and expect ...e5 followed by Nf3.",
        structured_response=_default_a2(),
        submitted_at=S6,
    )
    session = freeze_tutor_response(session, stage_id="A2", frozen_at=S7)
    assert session.state == "frozen"
    return upstream, session


def _through_reveal():
    upstream, session = _through_frozen()
    session = reveal_tutor_objective_evidence(
        session,
        revealed_at=S8,
        rendered_content="Qualified objective evidence: d4 is the engine rank-1 move.",
        position_analysis_refs=(reference_position_analysis(upstream.analysis),),
        decision_comparison_ref=reference_decision_comparison(upstream.comparison),
        selection_signal_refs=tuple(
            reference_selection_signal(item) for item in upstream.signals
        ),
    )
    assert session.state == "revealed"
    return upstream, session


def _m6_bundle(upstream, capture_session):
    context = build_reasoning_discrepancy_context(
        capture_session=capture_session,
        position=upstream.position,
        diagnostic_candidate=upstream.candidate,
        diagnostic_batch=upstream.batch,
        decision_comparison=upstream.comparison,
        assessment_stage_ids=("A1", "A2"),
        created_at=S9,
        position_features=upstream.features,
        position_analyses=(upstream.analysis,),
        selection_signals=upstream.signals,
    )
    facts = derive_discrepancy_facts(
        context=context,
        capture_session=capture_session,
        position=upstream.position,
        decision_comparison=upstream.comparison,
        position_analyses=(upstream.analysis,),
    )
    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=capture_session,
        facts=facts,
        codings=(),
        policy=_policy(),
        created_at=S10,
    )
    return context, assessment, assertions


def _through_compare():
    upstream, session = _through_reveal()
    context, assessment, assertions = _m6_bundle(
        upstream,
        session.capture_session,
    )
    session, comparison = record_tutor_reasoning_comparison(
        session,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        recorded_at=S11,
    )
    assert session.state == "compared"
    return upstream, session, comparison


def _ledger_context():
    hypothesis, revision = create_learner_hypothesis(
        participant_id="P01",
        statement="In forcing-reply positions, the strongest reply may be omitted.",
        scope_definition="forcing-reply positions",
        origin_provenance=_actor("m8-context-author"),
        created_at="2026-09-08T09:20:00-03:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision,),
        assessments=(),
        lifecycle_events=(),
        created_at="2026-09-08T09:30:00-03:00",
    )
    return snapshot, revision


def _explanation_provenance() -> TutorExplanationProvenance:
    instruction = hashlib.sha256(b"m8 neutral explanation").hexdigest()
    return TutorExplanationProvenance(
        actor_kind="template",
        actor_id="m8-qualification-template",
        actor_version="1",
        instruction_fingerprint=instruction,
        run_id="m8q-run-1",
    )


def _complete_session():
    _, session, _ = _through_compare()
    snapshot, revision = _ledger_context()
    session, _ = attach_tutor_hypothesis_context(
        session,
        ledger_snapshot=snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )
    session, explanation = record_tutor_explanation(
        session,
        rendered_content=(
            "This position has a supported local discrepancy under the cited M6 "
            "assessment. The active M7 hypothesis remains descriptive context only."
        ),
        provenance=_explanation_provenance(),
        created_at=S13,
    )
    session = complete_tutor_session(session, completed_at=S14)
    return session, explanation


def test_m8_start_is_deterministic_and_does_not_reveal_objective_evidence() -> None:
    upstream = _upstream()
    first = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=S0,
    )
    second = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=S0,
    )
    assert first == second
    assert first.state == "selected"
    assert first.capture_session.objective_reveal is None
    assert first.events[0].kind == "SESSION_STARTED"


def test_m8_position_presentation_uses_only_exact_deterministic_packet() -> None:
    upstream, session, presentation = _through_position()
    assert session.state == "presented"
    assert presentation.position_context.position_id == upstream.position.position_id
    assert upstream.analysis.result_fingerprint not in presentation.rendered_content
    assert upstream.candidate.candidate_id not in presentation.rendered_content
    assert session.capture_session.exposures[-1].kind == "POSITION_CONTEXT_SHOWN"


def test_m8_position_rejects_packet_not_bound_to_player_context() -> None:
    upstream = _upstream()
    session = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=S0,
    )
    packet = build_position_context(upstream.game, upstream.position)
    forged = replace(packet, board_ascii=packet.board_ascii + "\nforged")
    with pytest.raises(TutorSessionError, match="fingerprint"):
        present_tutor_position(session, position_context=forged, shown_at=S1)


def test_m8_rejects_tutoring_intervention_prompt_before_freeze() -> None:
    upstream = _upstream()
    prompt = define_prompt(
        name="invalid-m8-intervention",
        version="1",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="tutoring_intervention",
        content=("Try to find the engine's best move.",),
    )
    protocol = define_capture_protocol(
        name="invalid-m8-intervention-protocol",
        version="1",
        stages=(
            CaptureStageSpec(
                stage_id="A1",
                stage_kind="MINIMAL_RESPONSE",
                prompt_definition_id=prompt.prompt_definition_id,
                phase="pre_reveal",
            ),
        ),
    )
    session = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=protocol,
        created_at=S0,
    )
    packet = build_position_context(upstream.game, upstream.position)
    session, _ = present_tutor_position(
        session,
        position_context=packet,
        shown_at=S1,
    )
    with pytest.raises(TutorSessionError, match="observation or diagnostic"):
        present_tutor_capture_stage(
            session,
            stage_id="A1",
            prompt=prompt,
            shown_at=S2,
        )


def test_m8_reveal_is_blocked_until_every_planned_pre_reveal_freeze() -> None:
    upstream, session, _ = _through_position()
    session = present_tutor_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=S2,
    )
    session = capture_tutor_response(
        session,
        stage_id="A1",
        raw_response="e4",
        structured_response=_default_a1(),
        submitted_at=S3,
    )
    session = freeze_tutor_response(session, stage_id="A1", frozen_at=S4)
    assert session.state == "capturing"
    with pytest.raises(TutorSessionError, match="all pre-reveal evidence frozen"):
        reveal_tutor_objective_evidence(
            session,
            revealed_at=S5,
            rendered_content="too early",
            position_analysis_refs=(reference_position_analysis(upstream.analysis),),
        )


def test_m8_capture_operations_return_new_snapshots_without_mutating_old() -> None:
    _, session, _ = _through_position()
    before = session
    after = present_tutor_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=S2,
    )
    assert before.state == "presented"
    assert before.capture_session.presentations == ()
    assert after.state == "capturing"
    assert len(after.capture_session.presentations) == 1
    assert before.snapshot_fingerprint != after.snapshot_fingerprint


def test_m8_comparison_cannot_run_before_objective_reveal() -> None:
    upstream, session = _through_frozen()
    context, assessment, assertions = _m6_bundle(
        upstream,
        session.capture_session,
    )
    with pytest.raises(TutorSessionError, match="revealed state"):
        record_tutor_reasoning_comparison(
            session,
            reasoning_context=context,
            assessment=assessment,
            assertions=assertions,
            recorded_at=S11,
        )


def test_m8_comparison_requires_exact_final_capture_snapshot() -> None:
    upstream, frozen = _through_frozen()
    stale_context, stale_assessment, stale_assertions = _m6_bundle(
        upstream,
        frozen.capture_session,
    )
    _, revealed = _through_reveal()
    with pytest.raises(TutorSessionError, match="capture fingerprint"):
        record_tutor_reasoning_comparison(
            revealed,
            reasoning_context=stale_context,
            assessment=stale_assessment,
            assertions=stale_assertions,
            recorded_at=S11,
        )


def test_m8_hypothesis_context_requires_complete_active_current_ledger() -> None:
    _, session, _ = _through_compare()
    snapshot, revision = _ledger_context()
    with pytest.raises(TutorSessionError, match="every active current"):
        attach_tutor_hypothesis_context(
            session,
            ledger_snapshot=snapshot,
            active_revisions=(),
            attached_at=S12,
        )
    session, context = attach_tutor_hypothesis_context(
        session,
        ledger_snapshot=snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )
    assert session.state == "compared"
    assert context.active_revisions == (revision,)


def test_m8_explanation_is_post_comparison_and_provenance_bearing() -> None:
    _, session, comparison = _through_compare()
    session, explanation = record_tutor_explanation(
        session,
        rendered_content="Session-local evidence explanation only.",
        provenance=_explanation_provenance(),
        created_at=S13,
    )
    assert session.state == "explained"
    assert explanation.comparison_id == comparison.comparison_id
    assert explanation.provenance.actor_kind == "template"
    assert explanation.claim_scope == "session_local_evidence_explanation"
    assert explanation.hypothesis_context_id is None


def test_m8_full_session_reaches_completed_in_frozen_workflow_order() -> None:
    session, _ = _complete_session()
    assert session.state == "completed"
    assert session.completed_at == S14
    assert tuple(item.kind for item in session.events) == (
        "SESSION_STARTED",
        "POSITION_PRESENTED",
        "CAPTURE_STAGE_PRESENTED",
        "RESPONSE_CAPTURED",
        "RESPONSE_FROZEN",
        "CAPTURE_STAGE_PRESENTED",
        "RESPONSE_CAPTURED",
        "RESPONSE_FROZEN",
        "OBJECTIVE_EVIDENCE_REVEALED",
        "REASONING_COMPARISON_RECORDED",
        "HYPOTHESIS_CONTEXT_ATTACHED",
        "EXPLANATION_RECORDED",
        "SESSION_COMPLETED",
    )


def test_m8_full_session_replay_is_deterministic() -> None:
    first, _ = _complete_session()
    second, _ = _complete_session()
    assert first == second
    assert first.tutor_session_id == second.tutor_session_id
    assert first.snapshot_fingerprint == second.snapshot_fingerprint


def test_m8_serialized_state_contains_no_m9_or_learning_authority() -> None:
    session, _ = _complete_session()
    serialized = json.dumps(session.to_dict(), sort_keys=True).lower()
    for prohibited in (
        "training_eligible",
        "intervention_id",
        "exercise_definition",
        "intervention_effective",
        "mastery_state",
        "transfer_state",
    ):
        assert prohibited not in serialized
