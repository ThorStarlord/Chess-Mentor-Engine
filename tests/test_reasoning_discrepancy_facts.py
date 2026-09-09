from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

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
    CanonicalGame,
    CanonicalPosition,
    PositionFeaturePacket,
    build_position_context,
    build_position_features,
    ingest_pgn,
)
from chess_mentor_engine.evidence import (
    CaptureStageSpec,
    ParticipantMove,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    capture_stage_response,
    define_capture_protocol,
    define_prompt,
    freeze_stage_response,
    present_capture_stage,
    record_capture_deviation,
    record_capture_exposure,
    record_player_decision_context,
    start_capture_session,
)
from chess_mentor_engine.learning import (
    ReasoningDiscrepancyError,
    build_reasoning_discrepancy_context,
    derive_discrepancy_facts,
)
from chess_mentor_engine.selection import (
    DecisionComparison,
    DiagnosticCandidate,
    DiagnosticCandidateBatch,
    SelectionPolicy,
    SelectionSignal,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)

PGN = """
[Event "M6B deterministic facts"]
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


@dataclass(frozen=True, slots=True)
class _Upstream:
    game: CanonicalGame
    position: CanonicalPosition
    features: PositionFeaturePacket
    analysis: PositionAnalysis
    comparison: DecisionComparison
    signals: tuple[SelectionSignal, ...]
    candidate: DiagnosticCandidate
    batch: DiagnosticCandidateBatch
    player_context: PlayerDecisionContext


def _engine_provenance() -> EngineProvenance:
    return EngineProvenance(
        provider_name="m6b-precomputed",
        provider_version="1",
        protocol="precomputed",
        engine_name="qualification-engine",
        engine_version="2026.09",
        binary_sha256="m6b-fixture-binary",
        engine_options=(("Hash", "16"), ("Threads", "1")),
    )


def _analysis(position: CanonicalPosition) -> PositionAnalysis:
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
                root_move_uci="d2d4",
                evaluation=CentipawnEvaluation(60),
                pv_uci=("d2d4", "d7d5", "c2c4"),
            ),
            CandidateLine(
                rank=2,
                root_move_uci="e2e4",
                evaluation=CentipawnEvaluation(0),
                pv_uci=("e2e4", "e7e5", "g1f3"),
            ),
        ),
        metrics=AnalysisMetrics(depth=12),
        termination=AnalysisTermination("completed"),
    )
    return replace(record, result_fingerprint=analysis_result_fingerprint(record))


def _upstream() -> _Upstream:
    game = ingest_pgn(PGN).games[0]
    position = game.positions[0]
    features = build_position_features(position)
    analysis = _analysis(position)
    comparison = compare_played_decision(
        game=game,
        position=position,
        root_analysis=analysis,
    )
    assert comparison.preference == "worse_for_mover"
    signals = build_selection_signals(
        comparison=comparison,
        root_features=features,
        root_analysis=analysis,
    )
    policy = SelectionPolicy(
        policy_id="m6b-selection",
        version="1",
        requested_size=1,
        candidate_min_cp_delta=40,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        include_rank1_controls=True,
        minimum_controls=0,
        maximum_per_game=1,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )
    assert result.candidate is not None
    batch = build_diagnostic_candidate_batch(results=(result,), policy=policy)
    player_context = record_player_decision_context(
        participant_id="P01",
        session_id="m6b-session",
        position=position,
        position_context=build_position_context(game, position),
        candidate=result.candidate,
        batch=batch,
        created_at=T0,
    )
    return _Upstream(
        game=game,
        position=position,
        features=features,
        analysis=analysis,
        comparison=comparison,
        signals=signals,
        candidate=result.candidate,
        batch=batch,
        player_context=player_context,
    )


def _a1_prompt():
    return define_prompt(
        name="m6b-a1",
        version="1",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="observation",
        content=("What do you think about this position, and what would you play?",),
        response_schema=("selected_move",),
        provenance=(("qualification", "M6B"),),
    )


def _a2_prompt():
    return define_prompt(
        name="m6b-a2",
        version="1",
        stage_kind="STANDARDIZED_PROBE",
        interaction_class="diagnostic_probing",
        content=(
            "What other moves did you seriously consider?",
            "What is the opponent's strongest reply?",
            "What continuation do you expect?",
        ),
        response_schema=(
            "selected_move",
            "candidate_moves",
            "expected_reply",
            "expected_continuation",
        ),
        provenance=(("qualification", "M6B"),),
    )


def _protocol():
    a1 = _a1_prompt()
    a2 = _a2_prompt()
    return define_capture_protocol(
        name="m6b-two-stage",
        version="1",
        stages=(
            CaptureStageSpec(
                stage_id="A1",
                stage_kind="MINIMAL_RESPONSE",
                prompt_definition_id=a1.prompt_definition_id,
                phase="pre_reveal",
            ),
            CaptureStageSpec(
                stage_id="A2",
                stage_kind="STANDARDIZED_PROBE",
                prompt_definition_id=a2.prompt_definition_id,
                phase="pre_reveal",
            ),
        ),
    )


def _move(value: str) -> ParticipantMove:
    return ParticipantMove(
        submitted_value=value,
        normalized_uci=value,
        normalization_status="normalized",
        legality="legal",
    )


def _ambiguous(value: str = "maybe the knight move") -> ParticipantMove:
    return ParticipantMove(
        submitted_value=value,
        normalized_uci=None,
        normalization_status="ambiguous",
        legality="not_assessed",
    )


def _default_a1() -> ParticipantStructuredResponse:
    return ParticipantStructuredResponse(selected_move=_move("e2e4"))


def _default_a2() -> ParticipantStructuredResponse:
    return ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("e2e4"),),
        expected_reply=_move("e7e5"),
        expected_continuation=(_move("g1f3"),),
    )


def _capture(
    upstream: _Upstream,
    *,
    a1_structured: ParticipantStructuredResponse | None = None,
    a2_structured: ParticipantStructuredResponse | None = None,
    a1_raw: str = "I would play e4.",
    a2_raw: str = "I considered e4 and expect ...e5 followed by Nf3.",
):
    session = start_capture_session(
        context=upstream.player_context,
        protocol=_protocol(),
    )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=T1,
        rendered_content=_a1_prompt().content[0],
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response=a1_raw,
        structured_response=_default_a1() if a1_structured is None else a1_structured,
        submitted_at=T2,
    )
    session, _ = freeze_stage_response(session, stage_id="A1", frozen_at=T3)
    session, _ = present_capture_stage(
        session,
        stage_id="A2",
        prompt=_a2_prompt(),
        shown_at=T4,
        rendered_content="\n".join(_a2_prompt().content),
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A2",
        raw_response=a2_raw,
        structured_response=_default_a2() if a2_structured is None else a2_structured,
        submitted_at=T5,
    )
    session, _ = freeze_stage_response(session, stage_id="A2", frozen_at=T6)
    return session


def _context(
    upstream: _Upstream,
    session,
    *,
    stages: tuple[str, ...] = ("A1", "A2"),
    analyses: tuple[PositionAnalysis, ...] | None = None,
):
    return build_reasoning_discrepancy_context(
        capture_session=session,
        position=upstream.position,
        diagnostic_candidate=upstream.candidate,
        diagnostic_batch=upstream.batch,
        decision_comparison=upstream.comparison,
        assessment_stage_ids=stages,
        created_at=T9,
        position_features=upstream.features,
        position_analyses=(upstream.analysis,) if analyses is None else analyses,
        selection_signals=upstream.signals,
    )


def _facts(upstream: _Upstream, session, context, *, analyses=None):
    return derive_discrepancy_facts(
        context=context,
        capture_session=session,
        position=upstream.position,
        decision_comparison=upstream.comparison,
        position_analyses=(upstream.analysis,) if analyses is None else analyses,
    )


def _fact(facts, stage_id: str, kind: str):
    return next(
        item
        for item in facts
        if item.stage_id == stage_id and item.kind == kind
    )


def test_context_is_deterministic_and_normalizes_protocol_stage_order() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    first = _context(upstream, session, stages=("A2", "A1"))
    second = _context(upstream, session, stages=("A1", "A2"))

    assert first.assessment_stage_ids == ("A1", "A2")
    assert first.reasoning_context_id == second.reasoning_context_id
    assert first.context_fingerprint == second.context_fingerprint
    assert first.diagnostic_candidate_ref.ref_id == upstream.candidate.candidate_id
    assert first.diagnostic_batch_ref is not None
    assert first.diagnostic_batch_ref.ref_id == upstream.batch.batch_id


def test_context_rejects_candidate_not_bound_to_m5_reference() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    wrong_candidate = replace(upstream.candidate, candidate_id="candidate_wrong")

    with pytest.raises(ReasoningDiscrepancyError, match="candidate ID"):
        build_reasoning_discrepancy_context(
            capture_session=session,
            position=upstream.position,
            diagnostic_candidate=wrong_candidate,
            diagnostic_batch=upstream.batch,
            decision_comparison=upstream.comparison,
            assessment_stage_ids=("A1",),
            created_at=T9,
            position_analyses=(upstream.analysis,),
        )


def test_context_requires_selected_primary_response_to_be_frozen() -> None:
    upstream = _upstream()
    session = start_capture_session(
        context=upstream.player_context,
        protocol=_protocol(),
    )
    session, _ = present_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=T1,
        rendered_content=_a1_prompt().content[0],
    )
    session, _ = capture_stage_response(
        session,
        stage_id="A1",
        raw_response="e4",
        structured_response=_default_a1(),
        submitted_at=T2,
    )

    with pytest.raises(
        ReasoningDiscrepancyError,
        match="presentation, response, and freeze",
    ):
        _context(upstream, session, stages=("A1",))


def test_measurement_condition_preserves_clean_awareness_and_deviation_state() -> None:
    upstream = _upstream()
    clean = _capture(upstream)
    assert _context(upstream, clean).measurement_condition == "clean"

    aware, _ = record_capture_exposure(
        clean,
        kind="INSTRUMENT_AWARENESS_RECORDED",
        occurred_at=T7,
        source="qualification",
        instrument_awareness="known_aware",
    )
    assert _context(upstream, aware).measurement_condition == "instrument_aware_clean"

    deviating = record_capture_deviation(
        clean,
        code="OTHER",
        occurred_at=T7,
        details=(("note", "operator metadata irregularity"),),
        contaminates_pre_reveal=False,
    )
    assert _context(upstream, deviating).measurement_condition == "deviating"

    contaminated = record_capture_deviation(
        clean,
        code="OTHER",
        occurred_at=T7,
        details=(("note", "pre-reveal contamination"),),
        contaminates_pre_reveal=True,
    )
    assert _context(upstream, contaminated).measurement_condition == "contaminated"


def test_selected_historical_move_can_conflict_with_qualified_m4_comparison() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session)
    facts = _facts(upstream, session, context)

    selected = _fact(facts, "A1", "REPORTED_SELECTED_MOVE_RELATION")
    assert selected.relation == "conflict"
    assert selected.participant_value["normalized_uci"] == "e2e4"
    assert selected.objective_value["engine_rank1_uci"] == "d2d4"
    assert dict(selected.comparison_provenance)["basis"] == (
        "qualified_m4_played_move_worse_than_rank1"
    )


def test_engine_rank1_selected_move_is_a_descriptive_match() -> None:
    upstream = _upstream()
    session = _capture(
        upstream,
        a1_structured=ParticipantStructuredResponse(selected_move=_move("d2d4")),
    )
    context = _context(upstream, session, stages=("A1",))
    facts = _facts(upstream, session, context)

    selected = _fact(facts, "A1", "REPORTED_SELECTED_MOVE_RELATION")
    assert selected.relation == "match"
    assert (
        dict(selected.comparison_provenance)["basis"]
        == "exact_engine_rank1_identity"
    )


def test_ambiguous_selected_move_remains_ambiguous_without_guessing() -> None:
    upstream = _upstream()
    session = _capture(
        upstream,
        a1_structured=ParticipantStructuredResponse(selected_move=_ambiguous()),
    )
    context = _context(upstream, session, stages=("A1",))
    selected = _fact(
        _facts(upstream, session, context),
        "A1",
        "REPORTED_SELECTED_MOVE_RELATION",
    )

    assert selected.relation == "ambiguous"
    assert selected.participant_value["normalized_uci"] is None


def test_illegal_selected_move_conflict_uses_deterministic_chess_authority() -> None:
    upstream = _upstream()
    session = _capture(
        upstream,
        a1_structured=ParticipantStructuredResponse(selected_move=_move("e1e8")),
    )
    context = _context(upstream, session, stages=("A1",))
    selected = _fact(
        _facts(upstream, session, context),
        "A1",
        "REPORTED_SELECTED_MOVE_RELATION",
    )

    assert selected.relation == "conflict"
    assert selected.objective_value == {
        "requirement": "legal_move_from_canonical_position"
    }
    assert {item.authority for item in selected.objective_evidence_refs} == {
        "deterministic_chess"
    }


def test_explicit_candidate_membership_distinguishes_match_and_omission() -> None:
    upstream = _upstream()
    reported = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("d2d4"), _move("e2e4")),
    )
    session = _capture(upstream, a2_structured=reported)
    context = _context(upstream, session, stages=("A2",))
    membership = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert membership.relation == "match"

    omitted = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("e2e4"),),
    )
    omitted_session = _capture(upstream, a2_structured=omitted)
    omitted_context = _context(upstream, omitted_session, stages=("A2",))
    omitted_fact = _fact(
        _facts(upstream, omitted_session, omitted_context),
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert omitted_fact.relation == "not_explicitly_reported"
    assert "never considered" not in str(omitted_fact.to_dict()).lower()


def test_ambiguous_candidate_list_does_not_become_absence_claim() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("e2e4"), _ambiguous("maybe d4")),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    membership = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert membership.relation == "ambiguous"


def test_missing_candidate_reply_and_continuation_dimensions_are_not_observed() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(selected_move=_move("e2e4"))
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)

    assert _fact(
        facts, "A2", "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION"
    ).relation == "not_observed"
    assert _fact(facts, "A2", "EXPECTED_REPLY_RELATION").relation == "not_observed"
    assert _fact(
        facts, "A2", "EXPECTED_CONTINUATION_RELATION"
    ).relation == "not_observed"


def test_expected_reply_matches_cited_engine_pv_but_legal_alternative_is_not_comparable(
) -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",))
    reply = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPECTED_REPLY_RELATION",
    )
    assert reply.relation == "match"
    assert reply.objective_value == {"engine_pv_reply_uci": "e7e5"}

    alternative = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("c7c5"),
    )
    alt_session = _capture(upstream, a2_structured=alternative)
    alt_context = _context(upstream, alt_session, stages=("A2",))
    alt_reply = _fact(
        _facts(upstream, alt_session, alt_context),
        "A2",
        "EXPECTED_REPLY_RELATION",
    )
    assert alt_reply.relation == "not_comparable"
    assert dict(alt_reply.comparison_provenance)["basis"] == (
        "legal_alternative_differs_from_single_nonforced_engine_pv"
    )


def test_illegal_expected_reply_is_a_deterministic_conflict() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e2e4"),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    reply = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPECTED_REPLY_RELATION",
    )
    assert reply.relation == "conflict"
    assert dict(reply.comparison_provenance)["basis"] == "deterministic_reply_legality"


def test_expected_continuation_match_and_legal_pv_divergence_are_distinct() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",))
    continuation = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPECTED_CONTINUATION_RELATION",
    )
    assert continuation.relation == "match"

    alternative = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e7e5"),
        expected_continuation=(_move("b1c3"),),
    )
    alt_session = _capture(upstream, a2_structured=alternative)
    alt_context = _context(upstream, alt_session, stages=("A2",))
    alt_fact = _fact(
        _facts(upstream, alt_session, alt_context),
        "A2",
        "EXPECTED_CONTINUATION_RELATION",
    )
    assert alt_fact.relation == "not_comparable"
    assert dict(alt_fact.comparison_provenance)["basis"] == (
        "legal_continuation_differs_from_single_nonforced_engine_pv"
    )


def test_illegal_expected_continuation_is_a_deterministic_conflict() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e7e5"),
        expected_continuation=(_move("e2e4"),),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    continuation = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPECTED_CONTINUATION_RELATION",
    )
    assert continuation.relation == "conflict"
    assert dict(continuation.comparison_provenance)["basis"] == (
        "deterministic_continuation_legality"
    )


def test_raw_prose_is_never_parsed_into_candidate_truth() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("e2e4"),),
    )
    session = _capture(
        upstream,
        a2_structured=structured,
        a2_raw="I also seriously considered d4, but I submitted only e4 above.",
    )
    context = _context(upstream, session, stages=("A2",))
    membership = _fact(
        _facts(upstream, session, context),
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert membership.relation == "not_explicitly_reported"
    assert membership.participant_value == [_move("e2e4").to_dict()]


def test_missing_root_analysis_stays_not_comparable_instead_of_guessing() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",), analyses=())
    facts = _facts(upstream, session, context, analyses=())

    assert _fact(
        facts, "A2", "REPORTED_SELECTED_MOVE_RELATION"
    ).relation == "not_comparable"
    assert _fact(
        facts, "A2", "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION"
    ).relation == "not_comparable"
    assert _fact(facts, "A2", "EXPECTED_REPLY_RELATION").relation == "not_comparable"


def test_mismatched_root_analysis_is_rejected_not_interpolated() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    mismatched = replace(upstream.analysis, result_fingerprint="different-result")

    with pytest.raises(ReasoningDiscrepancyError, match="result fingerprint"):
        _context(upstream, session, analyses=(mismatched,))


def test_fact_relations_are_stable_but_identity_retains_raw_response_provenance(
) -> None:
    upstream = _upstream()
    first_session = _capture(upstream, a1_raw="I play e4.")
    second_session = _capture(upstream, a1_raw="My choice is e4.")
    first_context = _context(upstream, first_session, stages=("A1",))
    second_context = _context(upstream, second_session, stages=("A1",))
    first_fact = _fact(
        _facts(upstream, first_session, first_context),
        "A1",
        "REPORTED_SELECTED_MOVE_RELATION",
    )
    second_fact = _fact(
        _facts(upstream, second_session, second_context),
        "A1",
        "REPORTED_SELECTED_MOVE_RELATION",
    )

    assert first_fact.relation == second_fact.relation == "conflict"
    assert first_fact.participant_value == second_fact.participant_value
    assert first_fact.fact_id != second_fact.fact_id
    assert first_context.reasoning_context_id != second_context.reasoning_context_id
