from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisMetrics,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineProvenance,
    PositionAnalysis,
)
from chess_mentor_engine.chess import PositionFeaturePacket
from chess_mentor_engine.selection import (
    AnalysisEvidenceRef,
    DecisionComparison,
    DecisionComparisonPolicy,
    DecisionProvenance,
    build_selection_signals,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_partial_analysis_does_not_emit_ordered_rank_or_best_move_signals() -> None:
    request = AnalysisRequest(
        multipv=1,
        search_limit=AnalysisLimit("depth", 12),
        supervisor_timeout_ms=5_000,
    )
    provenance = EngineProvenance(
        provider_name="fixture-provider",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
    )
    best = CentipawnEvaluation(20)
    analysis = PositionAnalysis(
        position_id="position-partial",
        fen=START_FEN,
        request_fingerprint="request-partial",
        result_fingerprint="result-partial",
        status="partial",
        request=request,
        provenance=provenance,
        lines=(CandidateLine(1, "e2e4", best),),
        metrics=AnalysisMetrics(depth=12),
        termination=AnalysisTermination("timeout"),
    )
    comparison = DecisionComparison(
        comparison_id="comparison_partial",
        position_id="position-partial",
        game_id="game-partial",
        played_move_uci="d2d4",
        side_to_move="white",
        root_analysis_ref=AnalysisEvidenceRef(
            position_id="position-partial",
            fen=START_FEN,
            request_fingerprint="request-partial",
            result_fingerprint="result-partial",
            status="partial",
        ),
        played_evaluation_source="unavailable",
        played_analysis_ref=None,
        played_root_line_rank=None,
        best_move_uci="e2e4",
        best_evaluation=best,
        played_evaluation=None,
        compatibility="not_assessed",
        comparison_kind="partial_evidence",
        preference="incomparable",
        exact_centipawn_delta_for_mover=None,
        mate_relation=None,
        terminal_outcome=None,
        policy=DecisionComparisonPolicy(),
        provenance=DecisionProvenance(
            source_sha256="source-sha",
            game_semantic_fingerprint="game-fingerprint",
            root_ply_index=0,
            played_move_index=0,
            child_position_id="child-position",
        ),
    )
    features = PositionFeaturePacket(
        position_id="position-partial",
        game_id="game-partial",
        ply_index=0,
        side_to_move="white",
        fen=START_FEN,
        legal_moves=("d2d4", "e2e4"),
        legal_checks=(),
        legal_captures=(),
        square_attacks=(),
        piece_defenders=(),
        absolute_pins=(),
    )

    signals = build_selection_signals(
        comparison=comparison,
        root_features=features,
        root_analysis=analysis,
    )
    kinds = {signal.kind for signal in signals}

    assert "PLAYED_MOVE_IS_QUIET" in kinds
    assert "PLAYED_DIFFERS_FROM_RANK_1" not in kinds
    assert "BEST_MOVE_IS_QUIET" not in kinds
    assert "EXACT_CP_DELTA" not in kinds
