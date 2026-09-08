from __future__ import annotations

from dataclasses import replace

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
from chess_mentor_engine.chess import build_position_features, ingest_pgn
from chess_mentor_engine.selection import (
    SelectionPolicy,
    SelectionQuota,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)

CONTROL_PGN = """
[Event "M4D Control"]
[Result "*"]

1. e4 *
"""

DEVIATION_PGN = """
[Event "M4D Deviation"]
[Result "*"]

1. d4 *
"""

MATE_PGN = """
[Event "M4D Mate"]
[SetUp "1"]
[FEN "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"]
[Result "1-0"]

1. Qg7# 1-0
"""


def _provenance() -> EngineProvenance:
    return EngineProvenance(
        provider_name="m4d-corpus",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
        engine_version="2026.09",
        binary_sha256="fixture-binary",
        engine_options=(("Hash", "16"), ("Threads", "1")),
    )


def _analysis(position, lines: tuple[CandidateLine, ...]) -> PositionAnalysis:
    request = AnalysisRequest(
        multipv=max(1, len(lines)),
        search_limit=AnalysisLimit("depth", 12),
        supervisor_timeout_ms=5_000,
    )
    provenance = _provenance()
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
        lines=lines,
        metrics=AnalysisMetrics(depth=12),
        termination=AnalysisTermination("completed"),
    )
    return replace(record, result_fingerprint=analysis_result_fingerprint(record))


def _result(pgn: str, lines: tuple[CandidateLine, ...], policy: SelectionPolicy):
    game = ingest_pgn(pgn).games[0]
    root = game.positions[0]
    analysis = _analysis(root, lines)
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=build_position_features(root),
        root_analysis=analysis,
    )
    return apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )


def test_precomputed_m4d_corpus_is_end_to_end_deterministic() -> None:
    policy = SelectionPolicy(
        policy_id="m4d-qualification-corpus",
        version="1",
        requested_size=3,
        candidate_min_cp_delta=50,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        candidate_mate_relations=("forced_mate_completed",),
        include_rank1_controls=True,
        minimum_controls=1,
        maximum_per_game=1,
        quotas=(SelectionQuota("MATE_RELATION", minimum=1),),
    )

    control = _result(
        CONTROL_PGN,
        (
            CandidateLine(
                rank=1,
                root_move_uci="e2e4",
                evaluation=CentipawnEvaluation(30),
            ),
            CandidateLine(
                rank=2,
                root_move_uci="d2d4",
                evaluation=CentipawnEvaluation(20),
            ),
        ),
        policy,
    )
    deviation = _result(
        DEVIATION_PGN,
        (
            CandidateLine(
                rank=1,
                root_move_uci="e2e4",
                evaluation=CentipawnEvaluation(100),
            ),
            CandidateLine(
                rank=2,
                root_move_uci="d2d4",
                evaluation=CentipawnEvaluation(20),
            ),
        ),
        policy,
    )
    mate_game = ingest_pgn(MATE_PGN).games[0]
    mate_move = mate_game.moves_uci[0]
    mate = _result(
        MATE_PGN,
        (
            CandidateLine(
                rank=1,
                root_move_uci=mate_move,
                evaluation=MateEvaluation("white", 1),
            ),
        ),
        policy,
    )

    results = (control, deviation, mate)
    first = build_diagnostic_candidate_batch(results=results, policy=policy)
    second = build_diagnostic_candidate_batch(
        results=tuple(reversed(results)),
        policy=policy,
    )

    assert first == second
    assert first.actual_size == 3
    assert first.shortfall == 0
    assert first.control_shortfall == 0
    assert len(first.control_candidate_ids) == 1
    assert first.quota_outcomes[0].selected_count == 1
    assert first.quota_outcomes[0].shortfall == 0
    assert first.source_pool_count == 3
    assert first.source_pool_fingerprint
