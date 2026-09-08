from chess_mentor_engine.analysis import (
    AnalysisLimit,
    AnalysisRequest,
    CandidateLine,
    EngineProvenance,
    MateEvaluation,
    PositionAnalysis,
    PrecomputedAnalysisProvider,
    PrecomputedFixture,
)
from chess_mentor_engine.chess import CanonicalPosition

MATE_IN_ONE_FEN = "7k/8/5K2/6Q1/8/8/8/8 w - - 0 1"


def test_precomputed_provider_carries_forced_mate_evidence() -> None:
    request = AnalysisRequest(1, AnalysisLimit("depth", 8))
    line = CandidateLine(
        rank=1,
        root_move_uci="g5g7",
        evaluation=MateEvaluation("white", 1),
        pv_uci=("g5g7",),
    )
    provider = PrecomputedAnalysisProvider(
        provenance=EngineProvenance(
            provider_name="fixture-provider",
            provider_version="1",
            protocol="precomputed",
            engine_name="fixture-engine",
        ),
        fixtures=(
            PrecomputedFixture(
                fen=MATE_IN_ONE_FEN,
                request=request,
                status="complete",
                lines=(line,),
            ),
        ),
    )
    position = CanonicalPosition(
        position_id="mate-in-one",
        game_id="game-1",
        ply_index=0,
        move_number=1,
        side_to_move="white",
        fen=MATE_IN_ONE_FEN,
        last_move_uci=None,
        last_move_san=None,
    )

    outcome = provider.analyze(position, request)

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.best_move == "g5g7"
    assert isinstance(outcome.lines[0].evaluation, MateEvaluation)
    assert outcome.lines[0].evaluation.winner == "white"
    assert outcome.lines[0].evaluation.plies_to_mate == 1
