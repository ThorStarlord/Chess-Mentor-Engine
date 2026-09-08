from __future__ import annotations

from dataclasses import replace

import pytest

from chess_mentor_engine.analysis import (
    AnalysisFailure,
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
from chess_mentor_engine.chess import CanonicalGame, CanonicalPosition, ingest_pgn
from chess_mentor_engine.selection import (
    DecisionComparisonError,
    DecisionComparisonPolicy,
    compare_played_decision,
)

WHITE_D4_PGN = """
[Event "M4B White"]
[Result "*"]

1. d4 *
"""

BLACK_E5_PGN = """
[Event "M4B Black"]
[Result "*"]

1. e4 e5 *
"""

MATE_PGN = """
[Event "M4B Mate"]
[SetUp "1"]
[FEN "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"]
[Result "1-0"]

1. Qg7# 1-0
"""

STALEMATE_PGN = """
[Event "M4B Stalemate"]
[SetUp "1"]
[FEN "7k/5K2/4Q3/8/8/8/8/8 w - - 0 1"]
[Result "1/2-1/2"]

1. Qg6 1/2-1/2
"""


def _game(pgn: str) -> CanonicalGame:
    return ingest_pgn(pgn).games[0]


def _request(*, multipv: int = 1, depth: int = 12) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit("depth", depth),
        supervisor_timeout_ms=5_000,
    )


def _provenance(*, binary: str = "engine-sha") -> EngineProvenance:
    return EngineProvenance(
        provider_name="fixture-provider",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
        engine_version="2026.09",
        binary_sha256=binary,
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
    request: AnalysisRequest | None = None,
    provenance: EngineProvenance | None = None,
    status: str = "complete",
) -> PositionAnalysis:
    actual_request = request or _request(multipv=max(1, len(lines)))
    actual_provenance = provenance or _provenance()
    request_fingerprint = analysis_request_fingerprint(
        fen=position.fen,
        request=actual_request,
        provenance=actual_provenance,
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
        request=actual_request,
        provenance=actual_provenance,
        lines=lines,
        metrics=AnalysisMetrics(depth=actual_request.search_limit.value),
        termination=termination,
    )
    return replace(
        record,
        result_fingerprint=analysis_result_fingerprint(record),
    )


def _failure(
    position: CanonicalPosition,
    *,
    request: AnalysisRequest | None = None,
) -> AnalysisFailure:
    actual_request = request or _request()
    provenance = _provenance()
    return AnalysisFailure(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=analysis_request_fingerprint(
            fen=position.fen,
            request=actual_request,
            provenance=provenance,
        ),
        code="ANALYSIS_TIMEOUT",
        message="fixture timeout",
    )


def test_white_mover_exact_centipawn_delta_uses_mover_perspective() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.played_move_uci == "d2d4"
    assert comparison.played_evaluation_source == "root_multipv"
    assert comparison.played_root_line_rank == 2
    assert comparison.exact_centipawn_delta_for_mover == 20
    assert comparison.comparison_kind == "worse_for_mover"


def test_black_mover_exact_centipawn_delta_reverses_white_score() -> None:
    game = _game(BLACK_E5_PGN)
    root = game.positions[1]
    analysis = _analysis(
        root,
        (
            _line(1, "c7c5", CentipawnEvaluation(10)),
            _line(2, "e7e5", CentipawnEvaluation(30)),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.side_to_move == "black"
    assert comparison.exact_centipawn_delta_for_mover == 20
    assert comparison.comparison_kind == "worse_for_mover"


def test_policy_tolerance_can_mark_small_exact_delta_equivalent() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(25)),
        ),
    )
    policy = DecisionComparisonPolicy(
        policy_id="test-equivalence",
        version="1",
        exact_cp_tolerance=10,
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
        policy=policy,
    )

    assert comparison.exact_centipawn_delta_for_mover == 10
    assert comparison.comparison_kind == "approximately_equal_under_policy"


def test_child_reanalysis_is_used_when_played_move_is_outside_root_multipv() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    child = game.positions[1]
    request = _request(multipv=1)
    provenance = _provenance()
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
        request=request,
        provenance=provenance,
    )
    child_analysis = _analysis(
        child,
        (_line(1, "d7d5", CentipawnEvaluation(5)),),
        request=request,
        provenance=provenance,
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
        played_analysis=child_analysis,
    )

    assert comparison.played_evaluation_source == "child_reanalysis"
    assert comparison.compatibility == "compatible"
    assert comparison.exact_centipawn_delta_for_mover == 30
    assert comparison.played_analysis_ref is not None
    assert (
        comparison.played_analysis_ref.result_fingerprint
        == child_analysis.result_fingerprint
    )


def test_child_reanalysis_rejects_different_analysis_regime() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    child = game.positions[1]
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
        request=_request(depth=12),
    )
    child_analysis = _analysis(
        child,
        (_line(1, "d7d5", CentipawnEvaluation(5)),),
        request=_request(depth=14),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
        played_analysis=child_analysis,
    )

    assert comparison.compatibility == "incompatible"
    assert comparison.comparison_kind == "incompatible_analysis_regime"
    assert comparison.exact_centipawn_delta_for_mover is None


def test_partial_evidence_does_not_become_exact_severity() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
        status="partial",
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
    )

    assert comparison.comparison_kind == "partial_evidence"
    assert comparison.preference == "incomparable"
    assert comparison.exact_centipawn_delta_for_mover is None


def test_bound_limited_evaluation_does_not_become_exact_severity() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    root_analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15, bound="lower")),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
    )

    assert comparison.comparison_kind == "bound_limited"
    assert comparison.exact_centipawn_delta_for_mover is None


def test_child_failure_is_preserved_as_incomparable() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    child = game.positions[1]
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
        played_analysis=_failure(child),
    )

    assert comparison.comparison_kind == "incomparable"
    assert comparison.played_analysis_ref is not None
    assert comparison.played_analysis_ref.failure_code == "ANALYSIS_TIMEOUT"


def test_engine_evidence_inversion_is_not_clamped_away() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(20)),
            _line(2, "d2d4", CentipawnEvaluation(30)),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.exact_centipawn_delta_for_mover == -10
    assert comparison.comparison_kind == "engine_evidence_inversion"


def test_forced_mate_missed_is_symbolic_not_fake_centipawns() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", MateEvaluation("white", 3)),
            _line(2, "d2d4", CentipawnEvaluation(80)),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.comparison_kind == "worse_for_mover"
    assert comparison.mate_relation == "forced_mate_missed"
    assert comparison.exact_centipawn_delta_for_mover is None


def test_forced_mate_allowed_is_preserved_symbolically() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(20)),
            _line(2, "d2d4", MateEvaluation("black", 5)),
        ),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.comparison_kind == "worse_for_mover"
    assert comparison.mate_relation == "forced_mate_allowed"


def test_terminal_checkmate_is_derived_from_canonical_child_board() -> None:
    game = _game(MATE_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "f7g7", MateEvaluation("white", 1)),),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.played_evaluation_source == "terminal_child"
    assert comparison.terminal_outcome == "checkmate"
    assert comparison.comparison_kind == "terminal_relation"
    assert comparison.preference == "approximately_equal_under_policy"
    assert comparison.mate_relation == "forced_mate_completed"


def test_terminal_stalemate_preserves_missed_forced_mate_relation() -> None:
    game = _game(STALEMATE_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (_line(1, "e6e7", MateEvaluation("white", 3)),),
    )

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )

    assert comparison.terminal_outcome == "stalemate"
    assert comparison.comparison_kind == "terminal_relation"
    assert comparison.preference == "worse_for_mover"
    assert comparison.mate_relation == "forced_mate_missed"


def test_wrong_child_analysis_target_is_rejected() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
    )
    wrong = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
    )

    with pytest.raises(DecisionComparisonError, match="played child"):
        compare_played_decision(
            game=game,
            position=root,
            root_analysis=root_analysis,
            played_analysis=wrong,
        )


def test_root_failure_is_preserved_as_incomparable() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]

    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=_failure(root),
    )

    assert comparison.comparison_kind == "incomparable"
    assert comparison.root_analysis_ref.failure_code == "ANALYSIS_TIMEOUT"
    assert comparison.best_evaluation is None


def test_canonical_child_must_replay_from_the_actual_played_move() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    child = game.positions[1]
    corrupted_child = replace(child, fen=root.fen)
    corrupted_game = replace(game, positions=(root, corrupted_child))
    root_analysis = _analysis(
        root,
        (_line(1, "e2e4", CentipawnEvaluation(35)),),
    )

    with pytest.raises(DecisionComparisonError, match="consequence"):
        compare_played_decision(
            game=corrupted_game,
            position=root,
            root_analysis=root_analysis,
        )


def test_comparison_identity_is_deterministic_and_policy_sensitive() -> None:
    game = _game(WHITE_D4_PGN)
    root = game.positions[0]
    analysis = _analysis(
        root,
        (
            _line(1, "e2e4", CentipawnEvaluation(35)),
            _line(2, "d2d4", CentipawnEvaluation(15)),
        ),
    )

    first = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    second = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    different_policy = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
        policy=DecisionComparisonPolicy(
            policy_id="different",
            version="1",
            exact_cp_tolerance=0,
        ),
    )

    assert first.to_dict() == second.to_dict()
    assert first.comparison_id == second.comparison_id
    assert first.comparison_id != different_policy.comparison_id
