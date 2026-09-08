from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from chess_mentor_engine.chess import build_position_context, ingest_pgn
from chess_mentor_engine.evidence import (
    CaptureStageSpec,
    EvidenceReference,
    ParticipantMove,
    ParticipantStructuredResponse,
    PlayerEvidenceError,
    append_evidence_amendment,
    capture_stage_response,
    define_capture_protocol,
    define_prompt,
    freeze_stage_response,
    present_capture_stage,
    record_capture_deviation,
    record_capture_exposure,
    record_player_decision_context,
    reveal_objective_evidence,
    start_capture_session,
)
from chess_mentor_engine.selection import (
    DecisionProvenance,
    DiagnosticCandidate,
    SelectionEvidenceRef,
    SelectionPolicyIdentity,
    SelectionSignal,
)

PGN = b'''[Event "M5C Fixture"]
[Date "2026.09.08"]
[White "P01"]
[Black "Opponent"]
[Result "*"]

1. e4 *
'''

T0 = "2026-09-08T08:00:00-03:00"
T1 = "2026-09-08T08:01:00-03:00"
T2 = "2026-09-08T08:02:00-03:00"
T3 = "2026-09-08T08:03:00-03:00"
T4 = "2026-09-08T08:04:00-03:00"
T5 = "2026-09-08T08:05:00-03:00"
T6 = "2026-09-08T08:06:00-03:00"
T7 = "2026-09-08T08:07:00-03:00"


def _context():
    game = ingest_pgn(PGN).games[0]
    position = game.positions[0]
    packet = build_position_context(game, position)
    provenance = DecisionProvenance(
        source_sha256=game.provenance.source_sha256,
        game_semantic_fingerprint=game.semantic_fingerprint,
        root_ply_index=0,
        played_move_index=0,
        child_position_id=game.positions[1].position_id,
    )
    signal = SelectionSignal(
        signal_id="signal_rank1",
        kind="PLAYED_EQUALS_RANK_1",
        position_id=position.position_id,
        game_id=game.game_id,
        comparison_id="comparison_fixture",
        schema_version="1",
        raw_value=True,
        evidence=(
            SelectionEvidenceRef(
                source="decision_comparison",
                ref_id="comparison_fixture",
                fingerprint="a" * 64,
            ),
        ),
    )
    candidate = DiagnosticCandidate(
        candidate_id="candidate_fixture",
        position_id=position.position_id,
        game_id=game.game_id,
        comparison_id="comparison_fixture",
        selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
        signals=(signal,),
        eligibility_signal_ids=(signal.signal_id,),
        provenance=provenance,
    )
    return record_player_decision_context(
        participant_id="P01",
        session_id="session-001",
        position=position,
        position_context=packet,
        candidate=candidate,
        created_at=T0,
    )


def _minimal_prompt(*, interaction_class: str = "observation"):
    return define_prompt(
        name="minimal-response",
        version="1",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class=interaction_class,  # type: ignore[arg-type]
        content=("What do you think about this position, and what would you play?",),
        response_schema=("raw_response", "selected_move"),
        provenance=(("source", "m5c-test"),),
    )


def _probe_prompt():
    return define_prompt(
        name="standardized-probe",
        version="1",
        stage_kind="STANDARDIZED_PROBE",
        interaction_class="diagnostic_probing",
        content=(
            "What other moves did you seriously consider?",
            "What is the opponent's strongest reply?",
            "What continuation do you expect?",
            "What is your objective?",
            "What are you uncertain about?",
            "How confident are you, from 1 to 5?",
        ),
        response_schema=(
            "candidate_moves",
            "expected_reply",
            "expected_continuation",
            "stated_objective",
            "uncertainty",
            "confidence",
        ),
        provenance=(("source", "m5c-test"),),
    )


def _post_prompt():
    return define_prompt(
        name="post-reveal-reflection",
        version="1",
        stage_kind="POST_REVEAL_REFLECTION",
        interaction_class="post_reveal_reflection",
        content=("What changed after seeing the objective evidence?",),
        provenance=(("source", "m5c-test"),),
    )


def _minimal_protocol(prompt=None):
    prompt = _minimal_prompt() if prompt is None else prompt
    return define_capture_protocol(
        name="minimal-only",
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


def _two_stage_protocol(*, include_post: bool = False):
    minimal = _minimal_prompt()
    probe = _probe_prompt()
    stages = [
        CaptureStageSpec(
            stage_id="A1",
            stage_kind="MINIMAL_RESPONSE",
            prompt_definition_id=minimal.prompt_definition_id,
            phase="pre_reveal",
        ),
        CaptureStageSpec(
            stage_id="A2",
            stage_kind="STANDARDIZED_PROBE",
            prompt_definition_id=probe.prompt_definition_id,
            phase="pre_reveal",
        ),
    ]
    if include_post:
        post = _post_prompt()
        stages.append(
            CaptureStageSpec(
                stage_id="R1",
                stage_kind="POST_REVEAL_REFLECTION",
                prompt_definition_id=post.prompt_definition_id,
                phase="post_reveal",
            )
        )
    return define_capture_protocol(
        name="two-stage",
        version="1",
        stages=tuple(stages),
    )


def _analysis_ref():
    return EvidenceReference(
        kind="position_analysis",
        ref_id="analysis_fixture",
        fingerprint="d" * 64,
    )


def _clean_a1_frozen(session=None):
    context = _context()
    protocol = _minimal_protocol()
    session = (
        start_capture_session(context=context, protocol=protocol)
        if session is None
        else session
    )
    session, _presentation = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1 prompt",
    )
    session, _response = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        submitted_at=T2,
    )
    session, _freeze = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    return session


def test_capture_protocol_identity_is_material_and_deterministic() -> None:
    prompt = _minimal_prompt()
    first = _minimal_protocol(prompt)
    second = _minimal_protocol(prompt)
    changed = define_capture_protocol(
        name="minimal-only",
        version="2",
        stages=first.stages,
    )
    assert first == second
    assert first.protocol_id != changed.protocol_id


def test_protocol_rejects_pre_reveal_stage_after_post_reveal_stage() -> None:
    minimal = _minimal_prompt()
    post = _post_prompt()
    with pytest.raises(PlayerEvidenceError, match="pre-reveal stages cannot follow"):
        define_capture_protocol(
            name="bad-order",
            version="1",
            stages=(
                CaptureStageSpec(
                    "R1",
                    "POST_REVEAL_REFLECTION",
                    post.prompt_definition_id,
                    "post_reveal",
                ),
                CaptureStageSpec(
                    "A1",
                    "MINIMAL_RESPONSE",
                    minimal.prompt_definition_id,
                    "pre_reveal",
                ),
            ),
        )


def test_minimal_only_clean_path_freezes_before_reveal() -> None:
    session = _clean_a1_frozen()
    session, reveal = reveal_objective_evidence(
        session,
        revealed_at=T4,
        rendered_content="Engine evidence",
        position_analysis_refs=(_analysis_ref(),),
    )
    assert session.objective_reveal == reveal
    assert session.contaminated is False
    assert session.exposures[-1].kind == "ENGINE_EVIDENCE_SHOWN"


def test_two_stage_strict_path_requires_a1_freeze_before_a2() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_two_stage_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    with pytest.raises(PlayerEvidenceError, match="prior stage freezes"):
        present_capture_stage(
            session,
            stage_id="A2",
            prompt=_probe_prompt(),
            shown_at=T3,
            rendered_content="A2",
        )


def test_two_stage_preserve_mode_retains_early_a2_and_marks_deviation() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_two_stage_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    session, presentation = present_capture_stage(
        session,
        stage_id="A2",
        prompt=_probe_prompt(),
        shown_at=T3,
        rendered_content="A2",
        violation_mode="preserve",
    )
    assert presentation.stage_id == "A2"
    assert session.contaminated is True
    assert "STAGE_PRESENTED_BEFORE_PRIOR_FREEZE" in {
        item.code for item in session.deviations
    }
    assert session.exposures[-1].kind == "LATER_STAGE_PROMPT_SHOWN"


def test_reveal_is_blocked_until_all_required_pre_reveal_freezes_exist() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_two_stage_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    with pytest.raises(PlayerEvidenceError, match="all pre-reveal stage freezes"):
        reveal_objective_evidence(
            session,
            revealed_at=T4,
            rendered_content="too early",
            position_analysis_refs=(_analysis_ref(),),
        )


def test_early_reveal_can_be_preserved_with_explicit_deviation() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_two_stage_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, reveal = reveal_objective_evidence(
        session,
        revealed_at=T2,
        rendered_content="engine leak",
        position_analysis_refs=(_analysis_ref(),),
        violation_mode="preserve",
    )
    assert session.objective_reveal == reveal
    assert session.contaminated is True
    deviation = session.deviations[-1]
    assert deviation.code == "OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES"
    assert ("missing_freezes", "A1,A2") in deviation.details


def test_post_reveal_stage_is_blocked_before_reveal_and_allowed_after() -> None:
    context = _context()
    protocol = _two_stage_protocol(include_post=True)
    session = start_capture_session(context=context, protocol=protocol)
    with pytest.raises(PlayerEvidenceError, match="requires objective evidence reveal"):
        present_capture_stage(
            session,
            stage_id="R1",
            prompt=_post_prompt(),
            shown_at=T1,
            rendered_content="reflection",
        )

    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = present_capture_stage(
        session,
        stage_id="A2",
        prompt=_probe_prompt(),
        shown_at=T4,
        rendered_content="A2",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A2",
        raw_response="I also considered Nf3.",
        submitted_at=T5,
    )
    session, _ = freeze_stage_response(session, stage_id="A2", frozen_at=T6)
    session, _ = reveal_objective_evidence(
        session,
        revealed_at=T7,
        rendered_content="engine",
        position_analysis_refs=(_analysis_ref(),),
    )
    session, reflection = present_capture_stage(
        session,
        stage_id="R1",
        prompt=_post_prompt(),
        shown_at="2026-09-08T08:08:00-03:00",
        rendered_content="reflection",
    )
    assert reflection.stage_kind == "POST_REVEAL_REFLECTION"
    assert session.contaminated is False
    assert any(
        exposure.kind == "ENGINE_EVIDENCE_SHOWN"
        for exposure in session.exposures
        if exposure.exposure_event_id
        in reflection.information_available_before_presentation
    )


def test_pre_reveal_stage_after_early_reveal_can_be_preserved_as_contaminated() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_two_stage_protocol())
    session, _ = reveal_objective_evidence(
        session,
        revealed_at=T1,
        rendered_content="early engine",
        position_analysis_refs=(_analysis_ref(),),
        violation_mode="preserve",
    )
    session, presentation = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T2,
        rendered_content="A1 after engine",
        violation_mode="preserve",
    )
    assert presentation.stage_id == "A1"
    assert "PRE_REVEAL_STAGE_AFTER_REVEAL" in {
        item.code for item in session.deviations
    }


def test_response_requires_presentation_and_unique_stage_response() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    with pytest.raises(PlayerEvidenceError, match="before stage presentation"):
        capture_stage_response(
            session,
            stage_id="A1",
            raw_response="e4",
            submitted_at=T1,
        )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    with pytest.raises(PlayerEvidenceError, match="already has a response"):
        capture_stage_response(
            session,
            stage_id="A1",
            raw_response="d4",
            submitted_at=T3,
        )


def test_response_timestamp_violation_can_be_preserved_without_rewriting_time() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, presentation = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T2,
        rendered_content="A1",
    )
    session, response = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T1,
        violation_mode="preserve",
    )
    assert response.submitted_at == T1
    assert presentation.shown_at == T2
    assert session.deviations[-1].code == "TIMESTAMP_ORDER_VIOLATION"


def test_freeze_requires_response_and_cannot_repeat() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    with pytest.raises(PlayerEvidenceError, match="before response capture"):
        freeze_stage_response(session, stage_id="A1", frozen_at=T2)
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    session, freeze = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    assert freeze.stage_id == "A1"
    with pytest.raises(PlayerEvidenceError, match="already frozen"):
        freeze_stage_response(session, stage_id="A1", frozen_at=T4)


def test_prohibited_pre_reveal_exposure_is_preserved_and_marks_contamination() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, exposure = record_capture_exposure(
        session,
        kind="FACILITATOR_HINT",
        occurred_at=T1,
        source="facilitator",
        details=(("hint", "look at forcing moves"),),
    )
    assert exposure.kind == "FACILITATOR_HINT"
    assert session.contaminated is True
    assert session.deviations[-1].code == "PROHIBITED_PRE_REVEAL_EXPOSURE"


def test_instrument_awareness_is_provenance_not_automatic_contamination() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, exposure = record_capture_exposure(
        session,
        kind="INSTRUMENT_AWARENESS_RECORDED",
        occurred_at=T1,
        source="operator",
        instrument_awareness="known_aware",
    )
    assert exposure.instrument_awareness == "known_aware"
    assert session.contaminated is False
    assert session.deviations == ()


def test_tutoring_intervention_prompt_is_outside_clean_pre_reveal_capture() -> None:
    tutoring_prompt = _minimal_prompt(interaction_class="tutoring_intervention")
    protocol = _minimal_protocol(tutoring_prompt)
    context = _context()
    session = start_capture_session(context=context, protocol=protocol)
    with pytest.raises(PlayerEvidenceError, match="outside clean pre-reveal"):
        present_capture_stage(
            session,
            stage_id="A1",
            prompt=tutoring_prompt,
            shown_at=T1,
            rendered_content="Use checks, captures, threats first.",
        )
    session = start_capture_session(context=context, protocol=protocol)
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=tutoring_prompt,
        shown_at=T1,
        rendered_content="Use checks, captures, threats first.",
        violation_mode="preserve",
    )
    assert session.deviations[-1].code == "INTERVENTION_LIKE_PROMPT"


def test_amendment_requires_frozen_original_and_never_replaces_it() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, response = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        submitted_at=T2,
    )
    with pytest.raises(PlayerEvidenceError, match="original response to be frozen"):
        append_evidence_amendment(
            session,
            original_response_id=response.response_id,
            raw_response="Correction: d4.",
            submitted_at=T3,
            reason="participant correction",
        )
    session, freeze = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    original_fingerprint = response.response_fingerprint
    structured = ParticipantStructuredResponse(
        selected_move=ParticipantMove(
            submitted_value="d2d4",
            normalized_uci="d2d4",
            normalization_status="normalized",
            legality="legal",
        )
    )
    session, amendment = append_evidence_amendment(
        session,
        original_response_id=response.response_id,
        raw_response="Correction: I meant d4.",
        submitted_at=T4,
        reason="participant correction",
        structured_response=structured,
    )
    assert amendment.original_freeze_id == freeze.freeze_id
    assert amendment.raw_response == "Correction: I meant d4."
    assert session.responses[0].raw_response == "I would play e4."
    assert session.responses[0].response_fingerprint == original_fingerprint


def test_amendment_cannot_claim_a_time_before_original_freeze() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="A1",
    )
    session, response = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T4)
    with pytest.raises(PlayerEvidenceError, match="cannot precede original freeze"):
        append_evidence_amendment(
            session,
            original_response_id=response.response_id,
            raw_response="d4",
            submitted_at=T3,
            reason="correction",
        )


def test_manual_deviation_is_append_only_and_can_be_noncontaminating() -> None:
    context = _context()
    session = start_capture_session(context=context, protocol=_minimal_protocol())
    session = record_capture_deviation(
        session,
        code="OTHER",
        occurred_at=T1,
        details=(("note", "operator metadata irregularity"),),
        contaminates_pre_reveal=False,
    )
    assert len(session.deviations) == 1
    assert session.contaminated is False


def test_session_snapshot_is_deterministic_for_identical_event_sequence() -> None:
    first = _clean_a1_frozen()
    second = _clean_a1_frozen()
    assert first.capture_session_id == second.capture_session_id
    assert first.snapshot_fingerprint == second.snapshot_fingerprint
    assert first.to_dict() == second.to_dict()


def test_capture_session_and_transition_records_are_immutable() -> None:
    session = _clean_a1_frozen()
    with pytest.raises(FrozenInstanceError):
        session.snapshot_fingerprint = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        session.freezes[0].frozen_at = T7  # type: ignore[misc]
