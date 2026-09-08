"""M4B objective comparison between the played move and engine evidence."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import TypeAlias

from chess_mentor_engine.analysis.model import (
    AnalysisFailure,
    AnalysisOutcome,
    CentipawnEvaluation,
    Evaluation,
    MateEvaluation,
    PositionAnalysis,
)
from chess_mentor_engine.chess import CanonicalGame, CanonicalPosition, canonical_json
from chess_mentor_engine.chess._core import Board

from .model import (
    AnalysisEvidenceRef,
    DecisionComparison,
    DecisionComparisonPolicy,
    DecisionProvenance,
)

DEFAULT_COMPARISON_POLICY = DecisionComparisonPolicy()

AnalysisRegimeKey: TypeAlias = tuple[object, ...]


class DecisionComparisonError(ValueError):
    """Raised when supplied records violate canonical M4B provenance invariants."""


def compare_played_decision(
    *,
    game: CanonicalGame,
    position: CanonicalPosition,
    root_analysis: AnalysisOutcome,
    played_analysis: AnalysisOutcome | None = None,
    policy: DecisionComparisonPolicy = DEFAULT_COMPARISON_POLICY,
) -> DecisionComparison:
    """Compare the canonical played move with compatible M3 engine evidence."""
    played_move, child = _decision_context(game, position)
    _validate_analysis_target(root_analysis, position, label="root")
    root_ref = _analysis_ref(root_analysis)
    provenance = DecisionProvenance(
        source_sha256=game.provenance.source_sha256,
        game_semantic_fingerprint=game.semantic_fingerprint,
        root_ply_index=position.ply_index,
        played_move_index=position.ply_index,
        child_position_id=child.position_id,
    )

    if isinstance(root_analysis, AnalysisFailure):
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            provenance=provenance,
            policy=policy,
            comparison_kind="incomparable",
            preference="incomparable",
            detail=f"root analysis failed: {root_analysis.code}",
        )

    if root_analysis.status == "terminal":
        raise DecisionComparisonError(
            "terminal root position cannot have a played move"
        )

    best_line = root_analysis.lines[0] if root_analysis.lines else None
    best_evaluation = None if best_line is None else best_line.evaluation
    best_move = None if best_line is None else best_line.root_move_uci

    if root_analysis.status == "partial":
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            provenance=provenance,
            policy=policy,
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            comparison_kind="partial_evidence",
            preference="incomparable",
            detail="root analysis is partial",
        )

    if best_line is None:
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            provenance=provenance,
            policy=policy,
            comparison_kind="incomparable",
            preference="incomparable",
            detail="complete root analysis contains no candidate lines",
        )

    terminal = _terminal_outcome(child)
    if terminal is not None:
        played_ref = _optional_terminal_ref(played_analysis, child)
        if best_evaluation.bound != "exact":
            return _finish(
                position=position,
                played_move=played_move,
                root_ref=root_ref,
                played_ref=played_ref,
                provenance=provenance,
                policy=policy,
                source="terminal_child",
                best_move_uci=best_move,
                best_evaluation=best_evaluation,
                compatibility="not_applicable",
                comparison_kind="bound_limited",
                preference="incomparable",
                terminal_outcome=terminal,
                detail="root best evaluation is bound-limited",
            )
        preference, mate_relation = _compare_terminal(
            best_evaluation,
            terminal=terminal,
            mover=position.side_to_move,
        )
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source="terminal_child",
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            compatibility="not_applicable",
            comparison_kind="terminal_relation",
            preference=preference,
            mate_relation=mate_relation,
            terminal_outcome=terminal,
        )

    played_line = next(
        (
            line
            for line in root_analysis.lines
            if line.root_move_uci == played_move
        ),
        None,
    )
    if played_line is not None:
        return _compare_evaluations(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=root_ref,
            provenance=provenance,
            policy=policy,
            source="root_multipv",
            played_root_line_rank=played_line.rank,
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            played_evaluation=played_line.evaluation,
            compatibility="same_root_analysis",
        )

    if played_analysis is None:
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            provenance=provenance,
            policy=policy,
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            comparison_kind="incomparable",
            preference="incomparable",
            detail="played move is outside root MultiPV and child analysis is absent",
        )

    _validate_analysis_target(played_analysis, child, label="played child")
    played_ref = _analysis_ref(played_analysis)

    if isinstance(played_analysis, AnalysisFailure):
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source="child_reanalysis",
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            comparison_kind="incomparable",
            preference="incomparable",
            detail=f"played child analysis failed: {played_analysis.code}",
        )

    if played_analysis.status == "partial":
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source="child_reanalysis",
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            comparison_kind="partial_evidence",
            preference="incomparable",
            detail="played child analysis is partial",
        )

    if played_analysis.status == "terminal":
        raise DecisionComparisonError(
            "child analysis claims terminal for a position with legal moves"
        )

    if not played_analysis.lines:
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source="child_reanalysis",
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            comparison_kind="incomparable",
            preference="incomparable",
            detail="complete child analysis contains no candidate lines",
        )

    if _analysis_regime_key(root_analysis) != _analysis_regime_key(played_analysis):
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source="child_reanalysis",
            best_move_uci=best_move,
            best_evaluation=best_evaluation,
            played_evaluation=played_analysis.lines[0].evaluation,
            compatibility="incompatible",
            comparison_kind="incompatible_analysis_regime",
            preference="incomparable",
            detail="root and child analyses use different analysis regimes",
        )

    return _compare_evaluations(
        position=position,
        played_move=played_move,
        root_ref=root_ref,
        played_ref=played_ref,
        provenance=provenance,
        policy=policy,
        source="child_reanalysis",
        best_move_uci=best_move,
        best_evaluation=best_evaluation,
        played_evaluation=played_analysis.lines[0].evaluation,
        compatibility="compatible",
    )


def _decision_context(
    game: CanonicalGame,
    position: CanonicalPosition,
) -> tuple[str, CanonicalPosition]:
    if position.game_id != game.game_id:
        raise DecisionComparisonError("position does not belong to supplied game")
    index = position.ply_index
    if index < 0 or index >= len(game.positions):
        raise DecisionComparisonError("position ply_index is outside canonical game")
    canonical_root = game.positions[index]
    if (
        canonical_root.position_id != position.position_id
        or canonical_root.fen != position.fen
    ):
        raise DecisionComparisonError(
            "supplied position does not match canonical game position at ply_index"
        )
    if index >= len(game.moves_uci):
        raise DecisionComparisonError("root position has no canonical played move")
    if index + 1 >= len(game.positions):
        raise DecisionComparisonError("canonical child position is missing")
    played_move = game.moves_uci[index]
    child = game.positions[index + 1]
    if child.last_move_uci != played_move:
        raise DecisionComparisonError("canonical child does not preserve played move")
    return played_move, child


def _validate_analysis_target(
    outcome: AnalysisOutcome,
    position: CanonicalPosition,
    *,
    label: str,
) -> None:
    if outcome.position_id != position.position_id:
        raise DecisionComparisonError(f"{label} analysis position_id mismatch")
    if outcome.fen != position.fen:
        raise DecisionComparisonError(f"{label} analysis FEN mismatch")


def _analysis_ref(outcome: AnalysisOutcome) -> AnalysisEvidenceRef:
    if isinstance(outcome, AnalysisFailure):
        return AnalysisEvidenceRef(
            position_id=outcome.position_id,
            fen=outcome.fen,
            request_fingerprint=outcome.request_fingerprint,
            result_fingerprint=None,
            status="failure",
            failure_code=outcome.code,
        )
    return AnalysisEvidenceRef(
        position_id=outcome.position_id,
        fen=outcome.fen,
        request_fingerprint=outcome.request_fingerprint,
        result_fingerprint=outcome.result_fingerprint,
        status=outcome.status,
    )


def _optional_terminal_ref(
    outcome: AnalysisOutcome | None,
    child: CanonicalPosition,
) -> AnalysisEvidenceRef | None:
    if outcome is None:
        return None
    _validate_analysis_target(outcome, child, label="terminal child")
    if isinstance(outcome, PositionAnalysis) and outcome.status != "terminal":
        raise DecisionComparisonError(
            "analysis supplied for terminal child is not terminal"
        )
    return _analysis_ref(outcome)


def _terminal_outcome(position: CanonicalPosition) -> str | None:
    board = Board.from_fen(position.fen)
    if board.legal_moves():
        return None
    return "checkmate" if board.is_in_check(board.turn) else "stalemate"


def _analysis_regime_key(analysis: PositionAnalysis) -> AnalysisRegimeKey:
    provenance = analysis.provenance
    request = analysis.request
    artifact_key = tuple(
        (artifact.name, artifact.sha256)
        for artifact in provenance.engine_artifacts
    )
    return (
        provenance.provider_name,
        provenance.provider_version,
        provenance.protocol,
        provenance.engine_name,
        provenance.engine_version,
        provenance.binary_sha256,
        artifact_key,
        provenance.engine_options,
        request.search_limit.kind,
        request.search_limit.value,
        request.multipv,
        request.supervisor_timeout_ms,
    )


def _compare_evaluations(
    *,
    position: CanonicalPosition,
    played_move: str,
    root_ref: AnalysisEvidenceRef,
    played_ref: AnalysisEvidenceRef,
    provenance: DecisionProvenance,
    policy: DecisionComparisonPolicy,
    source: str,
    best_move_uci: str,
    best_evaluation: Evaluation,
    played_evaluation: Evaluation,
    compatibility: str,
    played_root_line_rank: int | None = None,
) -> DecisionComparison:
    if best_evaluation.bound != "exact" or played_evaluation.bound != "exact":
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source=source,
            played_root_line_rank=played_root_line_rank,
            best_move_uci=best_move_uci,
            best_evaluation=best_evaluation,
            played_evaluation=played_evaluation,
            compatibility=compatibility,
            comparison_kind="bound_limited",
            preference="incomparable",
            detail="at least one evaluation is not exact",
        )

    if isinstance(best_evaluation, CentipawnEvaluation) and isinstance(
        played_evaluation,
        CentipawnEvaluation,
    ):
        multiplier = 1 if position.side_to_move == "white" else -1
        best_value = multiplier * best_evaluation.centipawns
        played_value = multiplier * played_evaluation.centipawns
        delta = best_value - played_value
        if delta < 0:
            kind = "engine_evidence_inversion"
            preference = "engine_evidence_inversion"
        elif delta <= policy.exact_cp_tolerance:
            kind = "approximately_equal_under_policy"
            preference = "approximately_equal_under_policy"
        else:
            kind = "worse_for_mover"
            preference = "worse_for_mover"
        return _finish(
            position=position,
            played_move=played_move,
            root_ref=root_ref,
            played_ref=played_ref,
            provenance=provenance,
            policy=policy,
            source=source,
            played_root_line_rank=played_root_line_rank,
            best_move_uci=best_move_uci,
            best_evaluation=best_evaluation,
            played_evaluation=played_evaluation,
            compatibility=compatibility,
            comparison_kind=kind,
            preference=preference,
            exact_cp_delta=delta,
        )

    order = _compare_symbolic(
        best_evaluation,
        played_evaluation,
        mover=position.side_to_move,
    )
    relation = _mate_relation(
        best_evaluation,
        played_evaluation,
        mover=position.side_to_move,
    )
    if order < 0:
        kind = "engine_evidence_inversion"
        preference = "engine_evidence_inversion"
    elif order == 0:
        kind = "approximately_equal_under_policy"
        preference = "approximately_equal_under_policy"
    else:
        kind = "worse_for_mover"
        preference = "worse_for_mover"
    return _finish(
        position=position,
        played_move=played_move,
        root_ref=root_ref,
        played_ref=played_ref,
        provenance=provenance,
        policy=policy,
        source=source,
        played_root_line_rank=played_root_line_rank,
        best_move_uci=best_move_uci,
        best_evaluation=best_evaluation,
        played_evaluation=played_evaluation,
        compatibility=compatibility,
        comparison_kind=kind,
        preference=preference,
        mate_relation=relation,
    )


def _compare_symbolic(
    best: Evaluation,
    played: Evaluation,
    *,
    mover: str,
) -> int:
    best_key = _evaluation_key(best, mover=mover)
    played_key = _evaluation_key(played, mover=mover)
    if best_key > played_key:
        return 1
    if best_key < played_key:
        return -1
    return 0


def _evaluation_key(evaluation: Evaluation, *, mover: str) -> tuple[int, int]:
    if isinstance(evaluation, CentipawnEvaluation):
        multiplier = 1 if mover == "white" else -1
        return (1, multiplier * evaluation.centipawns)
    if evaluation.winner == mover:
        return (2, -evaluation.plies_to_mate)
    return (0, evaluation.plies_to_mate)


def _mate_relation(
    best: Evaluation,
    played: Evaluation,
    *,
    mover: str,
) -> str | None:
    if not isinstance(best, MateEvaluation) and not isinstance(
        played,
        MateEvaluation,
    ):
        return None
    if isinstance(best, MateEvaluation) and isinstance(played, CentipawnEvaluation):
        if best.winner == mover:
            return "forced_mate_missed"
        return "forced_mate_escaped"
    if isinstance(best, CentipawnEvaluation) and isinstance(played, MateEvaluation):
        if played.winner == mover:
            return "engine_evidence_inversion"
        return "forced_mate_allowed"

    assert isinstance(best, MateEvaluation)
    assert isinstance(played, MateEvaluation)
    best_for_mover = best.winner == mover
    played_for_mover = played.winner == mover
    if best_for_mover != played_for_mover:
        if best_for_mover:
            return "forced_mate_missed_and_allowed"
        return "engine_evidence_inversion"
    if best.plies_to_mate == played.plies_to_mate:
        return "forced_mate_preserved"
    if best_for_mover:
        return (
            "mate_distance_improved"
            if played.plies_to_mate < best.plies_to_mate
            else "mate_distance_worsened"
        )
    return (
        "mate_distance_improved"
        if played.plies_to_mate > best.plies_to_mate
        else "mate_distance_worsened"
    )


def _compare_terminal(
    best: Evaluation,
    *,
    terminal: str,
    mover: str,
) -> tuple[str, str | None]:
    if terminal == "checkmate":
        if isinstance(best, MateEvaluation):
            if best.winner == mover and best.plies_to_mate == 1:
                return "approximately_equal_under_policy", "forced_mate_completed"
            return "engine_evidence_inversion", "engine_evidence_inversion"
        return "engine_evidence_inversion", "engine_evidence_inversion"

    if isinstance(best, MateEvaluation):
        if best.winner == mover:
            return "worse_for_mover", "forced_mate_missed"
        return "engine_evidence_inversion", "forced_mate_escaped"
    return "incomparable", None


def _finish(
    *,
    position: CanonicalPosition,
    played_move: str,
    root_ref: AnalysisEvidenceRef,
    provenance: DecisionProvenance,
    policy: DecisionComparisonPolicy,
    comparison_kind: str,
    preference: str,
    source: str = "unavailable",
    played_ref: AnalysisEvidenceRef | None = None,
    played_root_line_rank: int | None = None,
    best_move_uci: str | None = None,
    best_evaluation: Evaluation | None = None,
    played_evaluation: Evaluation | None = None,
    compatibility: str = "not_assessed",
    exact_cp_delta: int | None = None,
    mate_relation: str | None = None,
    terminal_outcome: str | None = None,
    detail: str | None = None,
) -> DecisionComparison:
    record = DecisionComparison(
        comparison_id="",
        position_id=position.position_id,
        game_id=position.game_id,
        played_move_uci=played_move,
        side_to_move=position.side_to_move,
        root_analysis_ref=root_ref,
        played_evaluation_source=source,
        played_analysis_ref=played_ref,
        played_root_line_rank=played_root_line_rank,
        best_move_uci=best_move_uci,
        best_evaluation=best_evaluation,
        played_evaluation=played_evaluation,
        compatibility=compatibility,
        comparison_kind=comparison_kind,
        preference=preference,
        exact_centipawn_delta_for_mover=exact_cp_delta,
        mate_relation=mate_relation,
        terminal_outcome=terminal_outcome,
        policy=policy,
        provenance=provenance,
        detail=detail,
    )
    digest = hashlib.sha256(
        canonical_json(record.to_dict(include_comparison_id=False)).encode("utf-8")
    ).hexdigest()
    return replace(record, comparison_id=f"comparison_{digest[:20]}")
