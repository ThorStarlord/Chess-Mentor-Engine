from __future__ import annotations

from dataclasses import replace

import pytest

from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisMetrics,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineProvenance,
    MateEvaluation,
    PositionAnalysis,
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from chess_mentor_engine.chess import (
    CanonicalGame,
    CanonicalPosition,
    build_position_features,
    ingest_pgn,
)
from chess_mentor_engine.selection import (
    DiagnosticCandidateError,
    SelectionPolicyIdentity,
    SelectionSignalError,
    build_selection_signals,
    compare_played_decision,
    record_diagnostic_candidate,
)

WHITE_D4_PGN = """
[Event "M4C White"]
[Result "*"]

1. d4 *
"""

WHITE_E4_PGN = """
[Event "M4C Control"]
[Result "*"]

1. e4 *
"""

BLACK_E5_PGN = """
[Event "M4C Black"]
[Result "*"]

1. e4 e5 *
"""

CHECK_CAPTURE_PGN = """
[Event "M4C Check Capture"]
[SetUp "1"]
[FEN "4k3/8/8/8/8/8/4p3/4Q1K1 w - - 0 1"]
[Result "*"]

1. Qxe2+ *
"""

IN_CHECK_PGN = """
[Event "M4C In Check"]
[SetUp "1"]
[FEN "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1"]
[Result "*"]

1. Kxe2 *
"""

MATE_PGN = """
[Event "M4C Mate"]
[SetUp "1"]
[FEN "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"]
[Result "1-0"]

1. Qg7# 1-0
"""


def _game(pgn: str) -> CanonicalGame:
    return ingest_pgn(pgn).games[0]


def _request(*, multipv: int = 1) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit("depth", 12),
        supervisor_timeout_ms=5_000,
    )


def _provenance() -> EngineProvenance:
    return EngineProvenance(
        provider_name="fixture-provider",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
        engine_version="2026.09",
        binary_sha256="engine-sha",
        engine_options=(("Hash", "16"), ("Threads", "1")),
    )


def _line(
    rank: int,
    move: str,
    evaluation: CentipawnEvaluation | MateEvaluation,
) -> CandidateLine:
    return CandidateLine(
        rank=rank,
        root_move_uci=move,
        evaluation=evaluation,
    )


def _analysis(
    position: CanonicalPosition,
    lines: tuple[CandidateLine, ...],
    *,
    status: str = "complete",
) -> PositionAnalysis:
    request = _request(multipv=max(1, len(lines)))
    provenance = _provenance()
    request_fingerprint = analysis_request_fingerprint(
        fen=position.fen,
        request=request,
        provenance=provenance,
    )
    termination = (
        AnalysisTermination("timeout")
        if status == "partial"
        else AnalysisTermination("completed")
    )
    record = PositionAnalysis(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=request_fingerprint,
        result_fingerprint="",
        status=status,
        request=request,
        provenance=provenance,
        lines=lines,
        metrics=AnalysisMetrics(depth=12),
        termination=termination,
    )
    return replace(
        record,
        result_fingerprint=analysis_result_fingerprint(record),
    )


def _signals(
    game: CanonicalGame,
    root: CanonicalPosition,
    analysis: PositionAnalysis,
):
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    features = build_position_features(root)
    signals = build_selection_signals(
        comparison=comparison,
        root_features=features,
        root_analysis=analysis,
    )
    return comparison, features, signals


def _find(signals, kind: str):
    return next(signal for signal in signals if signal.kind == kind)


def test_objective_signal_set_is_deterministic_and_non_thresholded() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )

    comparison, features, first = _signals(game, root, analysis)
    second = build_selection_signals(
        comparison=comparison,
        root_features=features,
        root_analysis=analysis,
    )

    kinds = {signal.kind for signal in first}
    assert first == second
    assert "PLAYED_DIFFERS_FROM_RANK_1" in kinds
    assert "EXACT_CP_DELTA" in kinds
    assert "TOP_CANDIDATE_SEPARATION" in kinds
    assert "BEST_MOVE_IS_QUIET" in kinds
    assert "PLAYED_MOVE_IS_QUIET" in kinds
    assert "MULTIPV_CLOSE_CHOICE" not in kinds
    assert _find(first, "EXACT_CP_DELTA").raw_value == 20


def test_rank1_played_move_is_available_as_successful_control_evidence() -> None:
    game = _game(WHITE_E4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(25)),),
    )

    comparison, _, signals = _signals(game, root, analysis)

    assert comparison.exact_centipawn_delta_for_mover == 0
    assert _find(signals, "PLAYED_EQUALS_RANK_1")
    assert _find(signals, "EXACT_CP_DELTA").raw_value == 0


def test_checking_capture_emits_check_and_capture_but_not_quiet() -> None:
    game = _game(CHECK_CAPTURE_PGN)
    root = game.positions[0]
    played = game.moves_uci[0]
    analysis = _analysis(
        root,
        (_line(1, played, CentipawnEvaluation(50)),),
    )

    _, _, signals = _signals(game, root, analysis)
    kinds = {signal.kind for signal in signals}

    assert "PLAYED_MOVE_IS_CHECK" in kinds
    assert "PLAYED_MOVE_IS_CAPTURE" in kinds
    assert "BEST_MOVE_IS_CHECK" in kinds
    assert "BEST_MOVE_IS_CAPTURE" in kinds
    assert "PLAYED_MOVE_IS_QUIET" not in kinds
    assert "BEST_MOVE_IS_QUIET" not in kinds


def test_root_side_in_check_is_objective_signal() -> None:
    game = _game(IN_CHECK_PGN)
    root = game.positions[0]
    played = game.moves_uci[0]
    analysis = _analysis(
        root,
        (_line(1, played, CentipawnEvaluation(0)),),
    )

    _, _, signals = _signals(game, root, analysis)
    signal = _find(signals, "ROOT_SIDE_IS_IN_CHECK")

    assert signal.raw_value == {"side_to_move": "white", "in_check": True}


def test_top_candidate_separation_uses_black_mover_perspective() -> None:
    game = _game(BLACK_E5_PGN)
    root = game.positions[1]
    analysis = _analysis(
        root,
        (
            _line(1, "c7c5", CentipawnEvaluation(10)),
            _line(2, "e7e5", CentipawnEvaluation(30)),
        ),
    )

    _, _, signals = _signals(game, root, analysis)
    separation = _find(signals, "TOP_CANDIDATE_SEPARATION")

    assert separation.raw_value["exact_centipawn_separation_for_mover"] == 20


def test_mate_relation_is_preserved_as_symbolic_signal() -> None:
    game = _game(MATE_PGN)
    root = game.positions[0]
    played = game.moves_uci[0]
    analysis = _analysis(
        root,
        (_line(1, played, MateEvaluation("white", 1)),),
    )

    comparison, _, signals = _signals(game, root, analysis)

    assert comparison.mate_relation == "forced_mate_completed"
    assert _find(signals, "MATE_RELATION").raw_value == "forced_mate_completed"
    assert not any(signal.kind == "EXACT_CP_DELTA" for signal in signals)


def test_engine_inversion_preserves_negative_delta_signal() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(10)),
            _line(2, "d2d4", CentipawnEvaluation(20)),
        ),
    )

    comparison, _, signals = _signals(game, root, analysis)

    assert comparison.comparison_kind == "engine_evidence_inversion"
    assert _find(signals, "EXACT_CP_DELTA").raw_value == -10
    assert _find(signals, "ENGINE_EVIDENCE_INVERSION")


def test_partial_evidence_never_becomes_exact_delta_signal() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(10)),),
        status="partial",
    )

    comparison, _, signals = _signals(game, root, analysis)

    assert comparison.comparison_kind == "partial_evidence"
    assert not any(signal.kind == "EXACT_CP_DELTA" for signal in signals)


def test_feature_target_mismatch_is_rejected() -> None:
    game = _game(WHITE_E4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(25)),),
    )
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    features = replace(build_position_features(root), position_id="other-position")

    with pytest.raises(SelectionSignalError):
        build_selection_signals(
            comparison=comparison,
            root_features=features,
            root_analysis=analysis,
        )


def test_root_analysis_fingerprint_mismatch_is_rejected() -> None:
    game = _game(WHITE_E4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(25)),),
    )
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    changed = replace(analysis, result_fingerprint="different-result")

    with pytest.raises(SelectionSignalError):
        build_selection_signals(
            comparison=comparison,
            root_features=build_position_features(root),
            root_analysis=changed,
        )


def test_signals_cite_comparison_features_and_analysis_evidence() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )

    _, _, signals = _signals(game, root, analysis)
    refs = {
        (ref.source, ref.fingerprint)
        for signal in signals
        for ref in signal.evidence
    }

    assert any(source == "decision_comparison" for source, _ in refs)
    assert any(source == "position_features" and value for source, value in refs)
    assert any(source == "root_analysis" and value for source, value in refs)


def test_candidate_records_policy_identity_and_exact_eligibility_signals() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )
    comparison, _, signals = _signals(game, root, analysis)
    eligibility = (_find(signals, "EXACT_CP_DELTA").signal_id,)
    policy = SelectionPolicyIdentity("fixture-policy", "1")

    candidate = record_diagnostic_candidate(
        comparison=comparison,
        signals=signals,
        selection_policy=policy,
        eligibility_signal_ids=eligibility,
    )

    assert candidate.selection_policy == policy
    assert candidate.eligibility_signal_ids == eligibility
    assert candidate.comparison_id == comparison.comparison_id


def test_candidate_identity_is_order_stable_and_policy_sensitive() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )
    comparison, _, signals = _signals(game, root, analysis)
    eligibility = (_find(signals, "EXACT_CP_DELTA").signal_id,)

    first = record_diagnostic_candidate(
        comparison=comparison,
        signals=signals,
        selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
        eligibility_signal_ids=eligibility,
    )
    reordered = record_diagnostic_candidate(
        comparison=comparison,
        signals=tuple(reversed(signals)),
        selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
        eligibility_signal_ids=eligibility,
    )
    changed_policy = record_diagnostic_candidate(
        comparison=comparison,
        signals=signals,
        selection_policy=SelectionPolicyIdentity("fixture-policy", "2"),
        eligibility_signal_ids=eligibility,
    )

    assert first.candidate_id == reordered.candidate_id
    assert first.candidate_id != changed_policy.candidate_id


def test_candidate_rejects_unknown_eligibility_signal() -> None:
    game = _game(WHITE_E4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(25)),),
    )
    comparison, _, signals = _signals(game, root, analysis)

    with pytest.raises(DiagnosticCandidateError):
        record_diagnostic_candidate(
            comparison=comparison,
            signals=signals,
            selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
            eligibility_signal_ids=("signal_missing",),
        )


def test_candidate_rejects_signal_from_another_comparison() -> None:
    first_game = _game(WHITE_D4_PGN)
    first_root = first_game.positions[0]
    first_analysis = _analysis(
        first_root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )
    first_comparison, _, first_signals = _signals(
        first_game,
        first_root,
        first_analysis,
    )

    second_game = _game(WHITE_E4_PGN)
    second_root = second_game.positions[0]
    second_analysis = _analysis(
        second_root,
        (_line(1, "e2e4", CentipawnEvaluation(25)),),
    )
    _, _, second_signals = _signals(second_game, second_root, second_analysis)
    foreign = second_signals[0]

    with pytest.raises(DiagnosticCandidateError):
        record_diagnostic_candidate(
            comparison=first_comparison,
            signals=first_signals + (foreign,),
            selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
            eligibility_signal_ids=(first_signals[0].signal_id,),
        )


def test_initial_signal_taxonomy_contains_no_learner_psychology_labels() -> None:
    forbidden = {
        "poor calculation",
        "missed opponent resource",
        "tunnel vision",
        "bad planning",
        "needs tactics training",
    }
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )
    _, _, signals = _signals(game, root, analysis)

    rendered = str([signal.to_dict() for signal in signals]).lower()
    assert all(label not in rendered for label in forbidden)
