from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path

from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisMetrics,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineProvenance,
    PositionAnalysis,
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from chess_mentor_engine.chess import (
    build_position_context,
    build_position_features,
    ingest_pgn,
)
from chess_mentor_engine.evidence import (
    CaptureStageSpec,
    EvidenceCaptureSession,
    EvidenceReference,
    NumericRating,
    ParticipantMove,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    PromptDefinition,
    append_evidence_amendment,
    capture_stage_response,
    define_capture_protocol,
    define_prompt,
    freeze_stage_response,
    present_capture_stage,
    record_capture_exposure,
    record_player_decision_context,
    reference_decision_comparison,
    reference_position_analysis,
    reference_selection_signal,
    reveal_objective_evidence,
    start_capture_session,
)
from chess_mentor_engine.selection import (
    SelectionPolicy,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "m5q_player_evidence_corpus.json"
CORPUS = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

PGN = """
[Event "M5Q End-to-End"]
[Date "2026.09.08"]
[White "P01"]
[Black "Opponent"]
[Result "*"]

1. e4 *
"""

T0 = "2026-09-08T09:00:00-03:00"
T1 = "2026-09-08T09:01:00-03:00"
T2 = "2026-09-08T09:02:00-03:00"
T3 = "2026-09-08T09:03:00-03:00"
T4 = "2026-09-08T09:04:00-03:00"
T5 = "2026-09-08T09:05:00-03:00"
T6 = "2026-09-08T09:06:00-03:00"
T7 = "2026-09-08T09:07:00-03:00"
T8 = "2026-09-08T09:08:00-03:00"
T9 = "2026-09-08T09:09:00-03:00"
T10 = "2026-09-08T09:10:00-03:00"


@dataclass(frozen=True, slots=True)
class _Upstream:
    context: PlayerDecisionContext
    analysis_ref: EvidenceReference
    comparison_ref: EvidenceReference
    signal_refs: tuple[EvidenceReference, ...]
    selection_role: str
    candidate_id: str
    batch_id: str


def _engine_provenance() -> EngineProvenance:
    return EngineProvenance(
        provider_name="m5q-precomputed",
        provider_version="1",
        protocol="precomputed",
        engine_name="qualification-engine",
        engine_version="2026.09",
        binary_sha256="m5q-fixture-binary",
        engine_options=(("Hash", "16"), ("Threads", "1")),
    )


def _position_analysis(position) -> PositionAnalysis:
    request = AnalysisRequest(
        multipv=2,
        search_limit=AnalysisLimit("depth", 12),
        supervisor_timeout_ms=5_000,
    )
    provenance = _engine_provenance()
    request_fingerprint = analysis_request_fingerprint(
        fen=position.fen,
        request=request,
        provenance=provenance,
    )
    record = PositionAnalysis(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=request_fingerprint,
        result_fingerprint="",
        status="complete",
        request=request,
        provenance=provenance,
        lines=(
            CandidateLine(
                rank=1,
                root_move_uci="e2e4",
                evaluation=CentipawnEvaluation(30),
            ),
            CandidateLine(
                rank=2,
                root_move_uci="d2d4",
                evaluation=CentipawnEvaluation(10),
            ),
        ),
        metrics=AnalysisMetrics(depth=12),
        termination=AnalysisTermination("completed"),
    )
    return replace(record, result_fingerprint=analysis_result_fingerprint(record))


def _upstream() -> _Upstream:
    game = ingest_pgn(PGN).games[0]
    position = game.positions[0]
    packet = build_position_context(game, position)
    analysis = _position_analysis(position)
    comparison = compare_played_decision(
        game=game,
        position=position,
        root_analysis=analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=build_position_features(position),
        root_analysis=analysis,
    )
    policy = SelectionPolicy(
        policy_id="m5q-upstream-selection",
        version="1",
        requested_size=1,
        candidate_min_cp_delta=50,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        include_rank1_controls=True,
        minimum_controls=1,
        maximum_per_game=1,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )
    assert result.candidate is not None
    batch = build_diagnostic_candidate_batch(results=(result,), policy=policy)
    context = record_player_decision_context(
        participant_id="P01",
        session_id="m5q-session",
        position=position,
        position_context=packet,
        candidate=result.candidate,
        batch=batch,
        created_at=T0,
    )
    return _Upstream(
        context=context,
        analysis_ref=reference_position_analysis(analysis),
        comparison_ref=reference_decision_comparison(comparison),
        signal_refs=tuple(reference_selection_signal(item) for item in signals),
        selection_role=result.decision.role,
        candidate_id=result.candidate.candidate_id,
        batch_id=batch.batch_id,
    )


def _minimal_prompt() -> PromptDefinition:
    instrument = CORPUS["pilot_003_instrument"]
    return define_prompt(
        name="pilot-003-stage-a",
        version="1.0",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="observation",
        content=(instrument["stage_a_prompt"],),
        response_schema=("raw_response", "selected_move"),
        provenance=(("research_instrument", "FPV-PILOT-003"),),
    )


def _probe_prompt() -> PromptDefinition:
    instrument = CORPUS["pilot_003_instrument"]
    return define_prompt(
        name="pilot-003-stage-b",
        version="1.0",
        stage_kind="STANDARDIZED_PROBE",
        interaction_class="diagnostic_probing",
        content=tuple(instrument["stage_b_prompts"]),
        response_schema=(
            "candidate_moves",
            "expected_reply",
            "expected_continuation",
            "stated_objective",
            "uncertainty",
            "confidence",
        ),
        provenance=(("research_instrument", "FPV-PILOT-003"),),
    )


def _post_prompt() -> PromptDefinition:
    return define_prompt(
        name="m5q-post-reveal-reflection",
        version="1",
        stage_kind="POST_REVEAL_REFLECTION",
        interaction_class="post_reveal_reflection",
        content=("What changed after seeing the objective evidence?",),
        provenance=(("qualification", "M5Q"),),
    )


def _minimal_protocol():
    prompt = _minimal_prompt()
    return define_capture_protocol(
        name="m5q-minimal-only",
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
        name="m5q-two-stage",
        version="1",
        stages=tuple(stages),
    )


def _legal_move(value: str) -> ParticipantMove:
    return ParticipantMove(
        submitted_value=value,
        normalized_uci=value,
        normalization_status="normalized",
        legality="legal",
    )


def _minimal_structured() -> ParticipantStructuredResponse:
    return ParticipantStructuredResponse(selected_move=_legal_move("e2e4"))


def _probe_structured() -> ParticipantStructuredResponse:
    return ParticipantStructuredResponse(
        candidate_moves=(_legal_move("d2d4"),),
        expected_reply=_legal_move("e7e5"),
        expected_continuation=(_legal_move("g1f3"),),
        stated_objective="central control",
        uncertainty="Black's strongest reply",
        confidence=NumericRating(value=4, minimum=1, maximum=5),
    )


def _reveal(
    session: EvidenceCaptureSession,
    upstream: _Upstream,
    *,
    revealed_at: str,
    violation_mode: str = "reject",
):
    return reveal_objective_evidence(
        session,
        revealed_at=revealed_at,
        rendered_content="Objective engine evidence",
        position_analysis_refs=(upstream.analysis_ref,),
        decision_comparison_ref=upstream.comparison_ref,
        selection_signal_refs=upstream.signal_refs,
        violation_mode=violation_mode,  # type: ignore[arg-type]
    )


def _clean_minimal_only() -> EvidenceCaptureSession:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content=CORPUS["pilot_003_instrument"]["stage_a_prompt"],
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response=CORPUS["participant_evidence"]["minimal_raw_response"],
        structured_response=_minimal_structured(),
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = _reveal(session, upstream, revealed_at=T4)
    return session


def _clean_two_stage(*, include_post: bool = False) -> EvidenceCaptureSession:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_two_stage_protocol(include_post=include_post),
    )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content=CORPUS["pilot_003_instrument"]["stage_a_prompt"],
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response=CORPUS["participant_evidence"]["minimal_raw_response"],
        structured_response=_minimal_structured(),
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = present_capture_stage(
        session,
        stage_id="A2",
        prompt=_probe_prompt(),
        shown_at=T4,
        rendered_content="\n".join(CORPUS["pilot_003_instrument"]["stage_b_prompts"]),
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A2",
        raw_response=CORPUS["participant_evidence"]["probe_raw_response"],
        structured_response=_probe_structured(),
        submitted_at=T5,
    )
    session, _ = freeze_stage_response(session, stage_id="A2", frozen_at=T6)
    session, _ = _reveal(session, upstream, revealed_at=T7)
    return session


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def test_m5q_manifest_covers_every_frozen_qualification_case() -> None:
    assert set(CORPUS["required_cases"]) == {
        "clean_minimal_only",
        "clean_two_stage",
        "instrument_aware",
        "contaminated_exposure",
        "early_later_stage",
        "early_objective_reveal",
        "append_only_amendment",
        "ambiguous_reported_move",
        "illegal_reported_move",
        "post_reveal_reflection",
        "deterministic_replay",
        "research_artifact_preservation",
    }


def test_m5q_context_is_bound_to_real_m1_to_m4_selected_evidence() -> None:
    upstream = _upstream()
    assert upstream.selection_role == "control"
    assert upstream.context.diagnostic_candidate_ref.ref_id == upstream.candidate_id
    assert upstream.context.diagnostic_batch_ref is not None
    assert upstream.context.diagnostic_batch_ref.ref_id == upstream.batch_id
    assert (
        upstream.context.position_context_packet_ref.ref_id
        == upstream.context.position_id
    )


def test_m5q_clean_minimal_only_capture_preserves_raw_report_and_freeze() -> None:
    session = _clean_minimal_only()
    response = session.responses[0]
    freeze = session.freezes[0]
    assert session.contaminated is False
    assert response.raw_response == CORPUS["participant_evidence"][
        "minimal_raw_response"
    ]
    assert response.structured_response == _minimal_structured()
    assert freeze.response_id == response.response_id
    assert freeze.response_fingerprint == response.response_fingerprint
    assert session.objective_reveal is not None


def test_m5q_clean_two_stage_reproduces_frozen_pilot003_order() -> None:
    session = _clean_two_stage()
    assert tuple(item.stage_id for item in session.presentations) == ("A1", "A2")
    assert tuple(item.stage_id for item in session.responses) == ("A1", "A2")
    assert tuple(item.stage_id for item in session.freezes) == ("A1", "A2")
    assert session.responses[0].raw_response != session.responses[1].raw_response
    assert session.responses[1].structured_response == _probe_structured()
    assert session.objective_reveal is not None
    assert session.objective_reveal.revealed_at == T7
    assert session.contaminated is False
    assert _minimal_prompt().content == (
        CORPUS["pilot_003_instrument"]["stage_a_prompt"],
    )
    assert _probe_prompt().content == tuple(
        CORPUS["pilot_003_instrument"]["stage_b_prompts"]
    )


def test_m5q_instrument_awareness_is_provenance_not_cleanliness_inference() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
    session, awareness = record_capture_exposure(
        session,
        kind="INSTRUMENT_AWARENESS_RECORDED",
        occurred_at=T0,
        source="operator",
        instrument_awareness="known_aware",
    )
    session, presentation = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content=CORPUS["pilot_003_instrument"]["stage_a_prompt"],
    )
    assert awareness.instrument_awareness == "known_aware"
    assert (
        awareness.exposure_event_id
        in presentation.information_available_before_presentation
    )
    assert session.contaminated is False
    assert session.deviations == ()


def test_m5q_contaminated_exposure_is_preserved_not_erased() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
    session, exposure = record_capture_exposure(
        session,
        kind="FACILITATOR_HINT",
        occurred_at=T1,
        source="facilitator",
        details=(("hint", "look at forcing moves"),),
    )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T2,
        rendered_content="A1 after hint",
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        submitted_at=T3,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T4)
    session, _ = _reveal(session, upstream, revealed_at=T5)
    assert exposure in session.exposures
    assert session.contaminated is True
    assert "PROHIBITED_PRE_REVEAL_EXPOSURE" in {
        item.code for item in session.deviations
    }


def test_m5q_early_later_stage_is_retained_with_deviation_provenance() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_two_stage_protocol(),
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
    session, presentation = present_capture_stage(
        session,
        stage_id="A2",
        prompt=_probe_prompt(),
        shown_at=T3,
        rendered_content="A2 shown before A1 freeze",
        violation_mode="preserve",
    )
    assert presentation in session.presentations
    assert session.contaminated is True
    assert "STAGE_PRESENTED_BEFORE_PRIOR_FREEZE" in {
        item.code for item in session.deviations
    }
    assert any(item.kind == "LATER_STAGE_PROMPT_SHOWN" for item in session.exposures)


def test_m5q_early_objective_reveal_is_retained_and_marked_contaminated() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_two_stage_protocol(),
    )
    session, reveal = _reveal(
        session,
        upstream,
        revealed_at=T1,
        violation_mode="preserve",
    )
    assert session.objective_reveal == reveal
    assert session.contaminated is True
    assert session.deviations[-1].code == "OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES"
    assert ("missing_freezes", "A1,A2") in session.deviations[-1].details
    assert any(item.kind == "ENGINE_EVIDENCE_SHOWN" for item in session.exposures)


def test_m5q_amendment_is_append_only_and_original_fingerprint_survives() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
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
        raw_response=CORPUS["participant_evidence"]["minimal_raw_response"],
        submitted_at=T2,
    )
    session, freeze = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    original_fingerprint = response.response_fingerprint
    session, amendment = append_evidence_amendment(
        session,
        original_response_id=response.response_id,
        raw_response=CORPUS["participant_evidence"]["amendment_raw_response"],
        submitted_at=T4,
        reason="participant clarification",
    )
    assert amendment.original_freeze_id == freeze.freeze_id
    assert session.responses[0].response_fingerprint == original_fingerprint
    assert session.responses[0].raw_response == CORPUS["participant_evidence"][
        "minimal_raw_response"
    ]
    assert amendment.raw_response != session.responses[0].raw_response


def test_m5q_ambiguous_reported_move_remains_ambiguous() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
    ambiguous = ParticipantMove(
        submitted_value="the knight move",
        normalized_uci=None,
        normalization_status="ambiguous",
        legality="not_assessed",
    )
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
        raw_response="I would make the knight move.",
        structured_response=ParticipantStructuredResponse(selected_move=ambiguous),
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = _reveal(session, upstream, revealed_at=T4)
    move = response.structured_response.selected_move
    assert move.normalization_status == "ambiguous"
    assert move.normalized_uci is None
    assert session.contaminated is False


def test_m5q_illegal_reported_move_is_preserved_not_repaired() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.context,
        protocol=_minimal_protocol(),
    )
    illegal = ParticipantMove(
        submitted_value="e2e5",
        normalized_uci="e2e5",
        normalization_status="normalized",
        legality="illegal_for_position",
    )
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
        raw_response="I would play e5 from e2.",
        structured_response=ParticipantStructuredResponse(selected_move=illegal),
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = _reveal(session, upstream, revealed_at=T4)
    move = response.structured_response.selected_move
    assert move.submitted_value == "e2e5"
    assert move.normalized_uci == "e2e5"
    assert move.legality == "illegal_for_position"


def test_m5q_post_reveal_reflection_stays_epistemically_separate() -> None:
    session = _clean_two_stage(include_post=True)
    session, presentation = present_capture_stage(
        session,
        stage_id="R1",
        prompt=_post_prompt(),
        shown_at=T8,
        rendered_content="Post-reveal reflection",
    )
    session, reflection = capture_stage_response(
        session,
        stage_id="R1",
        raw_response=CORPUS["participant_evidence"]["post_reveal_raw_response"],
        submitted_at=T9,
    )
    session, _ = freeze_stage_response(session, stage_id="R1", frozen_at=T10)
    assert reflection.stage_kind == "POST_REVEAL_REFLECTION"
    assert reflection.response_id not in {
        session.responses[0].response_id,
        session.responses[1].response_id,
    }
    assert any(
        exposure.kind == "ENGINE_EVIDENCE_SHOWN"
        for exposure in session.exposures
        if exposure.exposure_event_id
        in presentation.information_available_before_presentation
    )
    assert session.contaminated is False


def test_m5q_identical_full_capture_replays_to_identical_snapshot() -> None:
    first = _clean_two_stage(include_post=True)
    second = _clean_two_stage(include_post=True)
    assert first.capture_session_id == second.capture_session_id
    assert first.snapshot_fingerprint == second.snapshot_fingerprint
    assert first.to_dict() == second.to_dict()


def test_m5q_frozen_research_artifacts_are_byte_identical_git_blobs() -> None:
    repository_root = Path(__file__).parents[1]
    expected = CORPUS["research_artifact_git_blob_shas"]
    assert len(expected) == 7
    for relative_path, expected_sha in expected.items():
        assert _git_blob_sha(repository_root / relative_path) == expected_sha
