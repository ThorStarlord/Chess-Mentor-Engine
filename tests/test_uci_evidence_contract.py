"""Regression coverage for the UCI provider 0.2 evidence contract repair."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pytest
from test_uci_provider import (
    BLACK_START_FEN,
    START_FEN,
    _position,
    _request,
    _write_fake_engine,
)

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    CentipawnEvaluation,
    MateEvaluation,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.analysis import uci as uci_module
from chess_mentor_engine.analysis.fingerprints import analysis_result_fingerprint
from chess_mentor_engine.analysis.model import ScoreBound
from chess_mentor_engine.analysis.uci import _parse_info


@pytest.mark.parametrize("side", ["white", "black"])
@pytest.mark.parametrize("score", [-50, 0, 50])
@pytest.mark.parametrize(
    ("flag", "white_bound", "black_bound"),
    [
        ("", "exact", "exact"),
        ("lowerbound", "lower", "upper"),
        ("upperbound", "upper", "lower"),
    ],
)
def test_centipawn_value_and_bound_share_white_perspective(
    side: Literal["white", "black"],
    score: int,
    flag: str,
    white_bound: ScoreBound,
    black_bound: ScoreBound,
) -> None:
    pv = "e2e4 e7e5" if side == "white" else "e7e5 e2e4"
    parsed = _parse_info(f"info depth 8 score cp {score} {flag} pv {pv}", side)

    assert parsed is not None
    evaluation = parsed.line.evaluation
    assert isinstance(evaluation, CentipawnEvaluation)
    assert evaluation.to_dict() == {
        "kind": "centipawn",
        "perspective": "white",
        "centipawns": score if side == "white" else -score,
        "bound": white_bound if side == "white" else black_bound,
    }
    assert parsed.line.pv_uci == tuple(pv.split())
    assert parsed.rank == parsed.line.rank == 1


@pytest.mark.parametrize(
    ("side", "score", "winner", "plies"),
    [
        ("white", 2, "white", 3),
        ("white", -2, "black", 4),
        ("black", 2, "black", 3),
        ("black", -2, "white", 4),
    ],
)
@pytest.mark.parametrize(
    ("flag", "white_bound", "black_bound"),
    [
        ("", "exact", "exact"),
        ("lowerbound", "lower", "upper"),
        ("upperbound", "upper", "lower"),
    ],
)
def test_mate_identity_is_preserved_and_bound_uses_white_evaluation_order(
    side: Literal["white", "black"],
    score: int,
    winner: Literal["white", "black"],
    plies: int,
    flag: str,
    white_bound: ScoreBound,
    black_bound: ScoreBound,
) -> None:
    pv = "e2e4 e7e5" if side == "white" else "e7e5 e2e4"
    parsed = _parse_info(f"info depth 8 score mate {score} {flag} pv {pv}", side)

    assert parsed is not None
    evaluation = parsed.line.evaluation
    assert isinstance(evaluation, MateEvaluation)
    assert evaluation.to_dict() == {
        "kind": "mate",
        "perspective": "white",
        "winner": winner,
        "plies_to_mate": plies,
        "bound": white_bound if side == "white" else black_bound,
    }


@pytest.mark.parametrize("side", ["white", "black"])
@pytest.mark.parametrize("kind", ["cp", "mate"])
def test_contradictory_bound_flags_are_rejected(side: str, kind: str) -> None:
    with pytest.raises(ValueError, match="both lowerbound and upperbound"):
        _parse_info(
            f"info score {kind} 2 lowerbound upperbound pv e2e4", side
        )


@pytest.mark.parametrize(
    ("rank_field", "expected"),
    [("", 1), ("multipv 1", 1), ("multipv 2", 2)],
)
def test_rank_defaults_only_when_multipv_is_absent(
    rank_field: str, expected: int
) -> None:
    parsed = _parse_info(
        f"info depth 8 {rank_field} score cp 20 pv e2e4", "white"
    )
    assert parsed is not None
    assert parsed.rank == parsed.line.rank == expected


@pytest.mark.parametrize("rank", ["0", "-1", "invalid", "1.5"])
def test_invalid_explicit_rank_is_rejected_by_parser(rank: str) -> None:
    with pytest.raises(ValueError, match="multipv"):
        _parse_info(f"info depth 8 multipv {rank} score cp 22 pv e2e4", "white")


@pytest.mark.parametrize("rank", ["0", "-1", "invalid", "1.5"])
@pytest.mark.parametrize("preceding_valid", [False, True])
def test_invalid_explicit_rank_fails_closed_even_after_valid_evidence(
    tmp_path: Path, rank: str, preceding_valid: bool
) -> None:
    valid = ("info depth 7 multipv 1 score cp 20 pv e2e4 e7e5",)
    info_lines = valid if preceding_valid else ()
    info_lines += (f"info depth 8 multipv {rank} score cp 22 pv e2e4 e7e5",)
    executable = _write_fake_engine(tmp_path, info_lines=info_lines)

    outcome = UciAnalysisProvider(executable).analyze(
        _position(START_FEN), _request(value=8)
    )

    assert isinstance(outcome, AnalysisFailure)
    assert outcome.code == "INVALID_ENGINE_OUTPUT"
    assert "multipv" in outcome.message
    assert outcome.request_fingerprint


def test_explicit_rank_without_value_is_not_defaulted() -> None:
    with pytest.raises(ValueError, match="missing integer after UCI field multipv"):
        _parse_info("info depth 8 score cp 20 pv e2e4 multipv", "white")


@pytest.mark.parametrize(
    ("flag", "bound"), [("lowerbound", "upper"), ("upperbound", "lower")]
)
def test_provider_emits_correct_bound_and_self_consistent_fingerprint(
    tmp_path: Path, flag: str, bound: ScoreBound
) -> None:
    executable = _write_fake_engine(
        tmp_path,
        info_lines=(f"info depth 8 score cp 22 {flag} pv e7e5 e2e4",),
        bestmove="e7e5",
    )
    outcome = UciAnalysisProvider(executable).analyze(
        _position(BLACK_START_FEN), _request(value=8)
    )

    assert isinstance(outcome, PositionAnalysis)
    assert outcome.status == "complete"
    assert outcome.lines[0].evaluation == CentipawnEvaluation(-22, bound)
    assert outcome.provenance.provider_version == "0.2"
    assert outcome.result_fingerprint == analysis_result_fingerprint(outcome)


def test_provider_version_materially_changes_identity_without_rewriting_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = _write_fake_engine(
        tmp_path, info_lines=("info depth 8 score cp 22 pv e2e4 e7e5",)
    )
    provider = UciAnalysisProvider(executable)
    position, request = _position(START_FEN), _request(value=8)
    current = provider.analyze(position, request)
    assert isinstance(current, PositionAnalysis)
    assert current.provenance.provider_version == "0.2"
    frozen_current = current.to_dict()

    # Only the version changes: this exact White score needs no normalization fix.
    with monkeypatch.context() as patch:
        patch.setattr(uci_module, "UCI_PROVIDER_VERSION", "0.1")
        previous_regime = provider.analyze(position, request)
    assert isinstance(previous_regime, PositionAnalysis)
    assert previous_regime.provenance.provider_version == "0.1"
    assert current.lines == previous_regime.lines
    assert current.request_fingerprint != previous_regime.request_fingerprint
    assert current.result_fingerprint != previous_regime.result_fingerprint
    assert current.to_dict() == frozen_current
    assert uci_module.UCI_PROVIDER_VERSION == "0.2"
