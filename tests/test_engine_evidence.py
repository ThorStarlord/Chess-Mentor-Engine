from __future__ import annotations

import pytest

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisMetrics,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineArtifact,
    EngineProvenance,
    MateEvaluation,
    PositionAnalysis,
    PrecomputedAnalysisProvider,
    PrecomputedFixture,
    analysis_request_fingerprint,
)
from chess_mentor_engine.chess import CanonicalPosition

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
MATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"


def _position(fen: str, position_id: str = "pos-1") -> CanonicalPosition:
    return CanonicalPosition(
        position_id=position_id,
        game_id="game-1",
        ply_index=0,
        move_number=1,
        side_to_move="white" if " w " in fen else "black",
        fen=fen,
        last_move_uci=None,
        last_move_san=None,
    )


def _request(multipv: int = 1) -> AnalysisRequest:
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
        engine_options=(("Threads", "1"), ("Hash", "16")),
        engine_artifacts=(EngineArtifact("net", "abc123"),),
    )


def _line(
    rank: int,
    root: str,
    score: int,
    pv: tuple[str, ...],
) -> CandidateLine:
    return CandidateLine(
        rank=rank,
        root_move_uci=root,
        evaluation=CentipawnEvaluation(score),
        pv_uci=pv,
    )


def test_evaluation_types_and_bounds_are_explicit() -> None:
    centipawn = CentipawnEvaluation(-42, bound="lower")
    mate = MateEvaluation("white", 5, bound="upper")

    assert centipawn.to_dict() == {
        "kind": "centipawn",
        "perspective": "white",
        "centipawns": -42,
        "bound": "lower",
    }
    assert mate.to_dict() == {
        "kind": "mate",
        "perspective": "white",
        "winner": "white",
        "plies_to_mate": 5,
        "bound": "upper",
    }
    with pytest.raises(ValueError):
        MateEvaluation("white", -1)


def test_request_and_metric_validation_reject_invalid_values() -> None:
    with pytest.raises(ValueError):
        AnalysisLimit("depth", 0)
    with pytest.raises(ValueError):
        AnalysisRequest(0, AnalysisLimit("depth", 1))
    with pytest.raises(ValueError):
        AnalysisRequest(1, AnalysisLimit("depth", 1), 0)
    with pytest.raises(ValueError):
        AnalysisMetrics(nodes=-1)
    with pytest.raises(ValueError):
        AnalysisMetrics(hashfull_per_mille=1001)


def test_provenance_serialization_is_deterministically_ordered() -> None:
    provenance = EngineProvenance(
        provider_name="fixture-provider",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
        engine_options=(("Threads", "1"), ("Hash", "16")),
        engine_artifacts=(EngineArtifact("z-net"), EngineArtifact("a-net")),
    )

    assert provenance.engine_options == (("Hash", "16"), ("Threads", "1"))
    assert tuple(item.name for item in provenance.engine_artifacts) == (
        "a-net",
        "z-net",
    )


def test_request_fingerprint_changes_with_analysis_conditions() -> None:
    provenance = _provenance()
    single = _request(1)
    multi = _request(2)

    first = analysis_request_fingerprint(
        fen=START_FEN,
        request=single,
        provenance=provenance,
    )
    second = analysis_request_fingerprint(
        fen=START_FEN,
        request=multi,
        provenance=provenance,
    )
    assert first != second


def test_precomputed_provider_returns_complete_multipv_analysis() -> None:
    request = _request(2)
    fixture = PrecomputedFixture(
        fen=START_FEN,
        request=request,
        status="complete",
        lines=(
            _line(1, "e2e4", 31, ("e2e4", "e7e5", "g1f3")),
            _line(2, "d2d4", 24, ("d2d4", "d7d5", "c1f4")),
        ),
        metrics=AnalysisMetrics(depth=12, nodes=12_345),
    )
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(fixture,),
    )

    outcome = provider.analyze(_position(START_FEN), request)

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "complete"
    assert outcome.best_move == "e2e4"
    assert len(outcome.lines) == 2
    assert outcome.request_fingerprint
    assert outcome.result_fingerprint
    assert outcome.to_dict()["result_fingerprint"] == outcome.result_fingerprint


def test_same_request_can_have_distinct_result_fingerprints() -> None:
    request = _request()
    first_provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="complete",
                lines=(_line(1, "e2e4", 20, ("e2e4", "e7e5")),),
            ),
        ),
    )
    second_provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="complete",
                lines=(_line(1, "e2e4", 27, ("e2e4", "e7e5")),),
            ),
        ),
    )

    first = first_provider.analyze(_position(START_FEN), request)
    second = second_provider.analyze(_position(START_FEN), request)

    assert isinstance(first, PositionAnalysis)
    assert isinstance(second, PositionAnalysis)
    assert first.request_fingerprint == second.request_fingerprint
    assert first.result_fingerprint != second.result_fingerprint


def test_partial_result_retains_timeout_termination() -> None:
    request = _request(2)
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="partial",
                lines=(_line(1, "e2e4", 18, ("e2e4", "e7e5")),),
                termination=AnalysisTermination("timeout"),
            ),
        ),
    )

    outcome = provider.analyze(_position(START_FEN), request)

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "partial"
    assert outcome.termination.reason == "timeout"
    assert outcome.best_move == "e2e4"


def test_terminal_position_is_not_an_engine_failure() -> None:
    request = _request()
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=MATE_FEN,
                request=request,
                status="terminal",
                termination=AnalysisTermination("terminal_position"),
            ),
        ),
    )

    outcome = provider.analyze(_position(MATE_FEN, "mate-pos"), request)

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "terminal"
    assert outcome.lines == ()
    assert outcome.best_move is None


def test_failure_fixture_returns_explicit_failure() -> None:
    request = _request()
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                failure_code="ANALYSIS_TIMEOUT",
                failure_message="fixture timeout",
            ),
        ),
    )

    outcome = provider.analyze(_position(START_FEN), request)

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "ANALYSIS_TIMEOUT"
    assert outcome.message == "fixture timeout"


def test_missing_fixture_returns_unsupported_request_failure() -> None:
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(),
    )

    outcome = provider.analyze(_position(START_FEN), _request())

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "UNSUPPORTED_REQUEST"
    assert outcome.request_fingerprint


def test_illegal_candidate_root_move_is_rejected() -> None:
    request = _request()
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="complete",
                lines=(_line(1, "a2a5", 10, ("a2a5",)),),
            ),
        ),
    )

    with pytest.raises(ValueError, match="illegal candidate root move"):
        provider.analyze(_position(START_FEN), request)


def test_illegal_pv_move_is_rejected() -> None:
    request = _request()
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="complete",
                lines=(
                    _line(1, "e2e4", 10, ("e2e4", "e7e5", "e1e3")),
                ),
            ),
        ),
    )

    with pytest.raises(ValueError, match="illegal PV move"):
        provider.analyze(_position(START_FEN), request)


def test_complete_result_must_satisfy_requested_multipv() -> None:
    request = _request(2)
    provider = PrecomputedAnalysisProvider(
        provenance=_provenance(),
        fixtures=(
            PrecomputedFixture(
                fen=START_FEN,
                request=request,
                status="complete",
                lines=(_line(1, "e2e4", 10, ("e2e4", "e7e5")),),
            ),
        ),
    )

    with pytest.raises(ValueError, match="requested MultiPV"):
        provider.analyze(_position(START_FEN), request)


def test_candidate_line_requires_pv_to_start_with_root_move() -> None:
    with pytest.raises(ValueError, match="begin with root_move_uci"):
        CandidateLine(
            rank=1,
            root_move_uci="e2e4",
            evaluation=CentipawnEvaluation(10),
            pv_uci=("d2d4",),
        )
