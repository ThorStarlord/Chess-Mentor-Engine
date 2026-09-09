"""M15 evaluation-presentation qualification and rejection coverage."""

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
)
from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.presentation import (
    PRESENTATION_SCHEMA_VERSION,
    EvaluationPresentationError,
    build_evaluation_presentation,
)
from chess_mentor_engine.selection import compare_played_decision

SIMPLE_PGN = """[Event "M15 fixture"]
[White "Ada"]
[Black "Grace"]
[Result "*"]

1. e4 e5 *
"""

MATE_PGN = """[Event "M15 mate fixture"]
[White "Ada"]
[Black "Grace"]
[Result "0-1"]

1. f3 e5 2. g4 Qh4# 0-1
"""


def _game(text: str = SIMPLE_PGN):
    return ingest_pgn(text.encode("utf-8")).games[0]


def _request(multipv: int = 2) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit("depth", 12),
        supervisor_timeout_ms=10_000,
    )


def _provenance(engine_name: str = "FakeFish 1.0") -> EngineProvenance:
    return EngineProvenance(
        provider_name="uci-subprocess",
        provider_version="0.2",
        protocol="uci",
        engine_name=engine_name,
        engine_author="Chess Mentor Tests",
        binary_sha256="a" * 64,
        engine_options=(("Threads", "1"),),
    )


def _analysis(
    position,
    lines: tuple[CandidateLine, ...],
    *,
    request: AnalysisRequest | None = None,
    provenance: EngineProvenance | None = None,
    status: str = "complete",
    fingerprint: str | None = None,
) -> PositionAnalysis:
    return PositionAnalysis(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=f"request:{position.position_id}",
        result_fingerprint=fingerprint or f"result:{position.position_id}:{status}",
        status=status,
        request=request or _request(len(lines) or 1),
        provenance=provenance or _provenance(),
        lines=lines,
        metrics=AnalysisMetrics(depth=12, nodes=1234, time_ms=20),
        termination=AnalysisTermination(
            "completed" if status != "terminal" else "terminal_position"
        ),
    )


def _line(rank: int, move: str, evaluation, *pv: str) -> CandidateLine:
    sequence = (move, *pv)
    return CandidateLine(
        rank=rank,
        root_move_uci=move,
        evaluation=evaluation,
        pv_uci=sequence,
    )


def test_exact_white_centipawns_preserve_both_perspectives_and_refs() -> None:
    game = _game()
    root = _analysis(
        game.positions[0],
        (
            _line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),
            _line(2, "e2e4", CentipawnEvaluation(10), "e7e5"),
        ),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
    )

    assert payload["schema_version"] == PRESENTATION_SCHEMA_VERSION
    assert payload["score_semantics"] == {
        "canonical_engine_perspective": "white",
        "display_perspective": "decision_mover",
        "centipawn_unit": "centipawns",
        "mate_representation": "winner_and_plies_to_mate",
        "bound_semantics": "ordering_bound_in_display_perspective",
    }
    best = payload["comparison"]["best_evaluation"]
    assert best["white"] == {"centipawns": 40, "bound": "exact"}
    assert best["decision_mover"] == {
        "side": "white",
        "centipawns": 40,
        "bound": "exact",
    }
    assert payload["comparison"]["exact_centipawn_delta_for_mover"] == 30
    assert payload["comparison"]["evidence_quality"] == "exact"
    assert payload["root_analysis"]["engine"]["engine_name"] == "FakeFish 1.0"
    assert payload["root_analysis"]["candidates"][0]["pv_uci"] == [
        "d2d4",
        "d7d5",
    ]
    assert payload["evidence_refs"]["root_analysis"]["result_fingerprint"] == (
        root.result_fingerprint
    )
    assert payload["evidence_refs"]["decision_comparison"]["comparison_id"] == (
        comparison.comparison_id
    )


def test_black_mover_inverts_centipawns_and_score_bound() -> None:
    game = _game()
    root = _analysis(
        game.positions[1],
        (
            _line(1, "c7c5", CentipawnEvaluation(-50, bound="lower"), "g1f3"),
            _line(2, "e7e5", CentipawnEvaluation(-20), "g1f3"),
        ),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[1],
        root_analysis=root,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
    )

    best = payload["comparison"]["best_evaluation"]
    assert best["white"] == {"centipawns": -50, "bound": "lower"}
    assert best["decision_mover"] == {
        "side": "black",
        "centipawns": 50,
        "bound": "upper",
    }
    assert payload["comparison"]["comparison_kind"] == "bound_limited"
    assert payload["comparison"]["evidence_quality"] == "bounded"
    assert payload["comparison"]["exact_centipawn_delta_for_mover"] is None


def test_mate_stays_symbolic_and_never_becomes_centipawn_sentinel() -> None:
    game = _game(MATE_PGN)
    root = _analysis(
        game.positions[3],
        (_line(1, "d8h4", MateEvaluation("black", 1)),),
        request=_request(1),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[3],
        root_analysis=root,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
    )

    evaluation = payload["comparison"]["best_evaluation"]
    assert evaluation["kind"] == "mate"
    assert evaluation["winner"] == "black"
    assert evaluation["plies_to_mate"] == 1
    assert evaluation["decision_mover"] == {
        "side": "black",
        "favours_perspective": True,
        "bound": "exact",
    }
    assert "centipawns" not in evaluation
    assert payload["comparison"]["mate_relation"] == "forced_mate_completed"


def test_partial_root_is_explicitly_non_exact() -> None:
    game = _game()
    root = _analysis(
        game.positions[0],
        (_line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
        request=_request(2),
        status="partial",
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
    )

    assert payload["root_analysis"]["status"] == "partial"
    assert payload["root_analysis"]["evidence_quality"] == "partial"
    assert payload["comparison"]["comparison_kind"] == "partial_evidence"
    assert payload["comparison"]["evidence_quality"] == "partial"
    assert payload["comparison"]["exact_centipawn_delta_for_mover"] is None


def test_child_reanalysis_preserves_exact_engine_identity_and_evidence_ref() -> None:
    game = _game()
    request = _request(1)
    provenance = _provenance()
    root = _analysis(
        game.positions[0],
        (_line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
        request=request,
        provenance=provenance,
    )
    child = _analysis(
        game.positions[1],
        (_line(1, "e7e5", CentipawnEvaluation(20), "g1f3"),),
        request=request,
        provenance=provenance,
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
        played_analysis=child,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
        played_analysis=child,
    )

    assert payload["comparison"]["played_evaluation_source"] == "child_reanalysis"
    assert payload["comparison"]["compatibility"] == "compatible"
    assert payload["played_child_analysis"]["engine"] == (
        payload["root_analysis"]["engine"]
    )
    assert payload["evidence_refs"]["played_analysis"]["result_fingerprint"] == (
        child.result_fingerprint
    )


def test_incompatible_child_engine_is_never_presented_as_exact_loss() -> None:
    game = _game()
    request = _request(1)
    root = _analysis(
        game.positions[0],
        (_line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
        request=request,
        provenance=_provenance("FakeFish A"),
    )
    child = _analysis(
        game.positions[1],
        (_line(1, "e7e5", CentipawnEvaluation(20), "g1f3"),),
        request=request,
        provenance=_provenance("FakeFish B"),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
        played_analysis=child,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
        played_analysis=child,
    )

    assert payload["comparison"]["comparison_kind"] == (
        "incompatible_analysis_regime"
    )
    assert payload["comparison"]["evidence_quality"] == "incompatible"
    assert payload["comparison"]["exact_centipawn_delta_for_mover"] is None
    assert payload["root_analysis"]["engine"]["engine_name"] == "FakeFish A"
    assert payload["played_child_analysis"]["engine"]["engine_name"] == "FakeFish B"


def test_child_failure_stays_explicit_and_unavailable() -> None:
    game = _game()
    root = _analysis(
        game.positions[0],
        (_line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
        request=_request(1),
    )
    child = AnalysisFailure(
        position_id=game.positions[1].position_id,
        fen=game.positions[1].fen,
        request_fingerprint="request:child-failure",
        code="ENGINE_CRASHED",
        message="engine exited during search",
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
        played_analysis=child,
    )

    payload = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
        played_analysis=child,
    )

    assert payload["played_child_analysis"]["status"] == "failure"
    assert payload["played_child_analysis"]["failure"]["code"] == "ENGINE_CRASHED"
    assert payload["comparison"]["evidence_quality"] == "unavailable"
    assert payload["comparison"]["exact_centipawn_delta_for_mover"] is None


def test_root_reference_mismatch_is_rejected() -> None:
    game = _game()
    root = _analysis(
        game.positions[0],
        (
            _line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),
            _line(2, "e2e4", CentipawnEvaluation(10), "e7e5"),
        ),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
    )
    bad_ref = replace(comparison.root_analysis_ref, result_fingerprint="wrong")
    corrupted = replace(comparison, root_analysis_ref=bad_ref)

    with pytest.raises(EvaluationPresentationError, match="root evidence reference"):
        build_evaluation_presentation(
            root_analysis=root,
            comparison=corrupted,
        )


def test_non_exact_comparison_cannot_smuggle_exact_centipawn_delta() -> None:
    game = _game()
    root = _analysis(
        game.positions[1],
        (
            _line(1, "c7c5", CentipawnEvaluation(-50, bound="lower"), "g1f3"),
            _line(2, "e7e5", CentipawnEvaluation(-20), "g1f3"),
        ),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[1],
        root_analysis=root,
    )
    corrupted = replace(comparison, exact_centipawn_delta_for_mover=30)

    with pytest.raises(EvaluationPresentationError, match="non-exact comparison"):
        build_evaluation_presentation(
            root_analysis=root,
            comparison=corrupted,
        )


def test_root_multipv_source_rejects_unrelated_child_analysis() -> None:
    game = _game()
    root = _analysis(
        game.positions[0],
        (
            _line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),
            _line(2, "e2e4", CentipawnEvaluation(10), "e7e5"),
        ),
    )
    child = _analysis(
        game.positions[1],
        (_line(1, "e7e5", CentipawnEvaluation(10), "g1f3"),),
        request=_request(1),
    )
    comparison = compare_played_decision(
        game=game,
        position=game.positions[0],
        root_analysis=root,
    )

    with pytest.raises(EvaluationPresentationError, match="must not supply child"):
        build_evaluation_presentation(
            root_analysis=root,
            comparison=comparison,
            played_analysis=child,
        )
