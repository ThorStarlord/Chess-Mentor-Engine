"""M15 deterministic presentation projection over qualified M3/M4 evidence."""

from __future__ import annotations

from typing import Any

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    CentipawnEvaluation,
    MateEvaluation,
    PositionAnalysis,
)
from chess_mentor_engine.selection import AnalysisEvidenceRef, DecisionComparison

PRESENTATION_SCHEMA_VERSION = "m15.evaluation-presentation.v1"


class EvaluationPresentationError(ValueError):
    """Qualified evidence cannot be projected without losing integrity."""


def _reverse_bound(bound: str) -> str:
    if bound == "lower":
        return "upper"
    if bound == "upper":
        return "lower"
    return bound


def _present_evaluation(evaluation: object, decision_mover: str) -> dict[str, Any]:
    if decision_mover not in {"white", "black"}:
        raise EvaluationPresentationError("invalid decision mover")
    if not isinstance(evaluation, (CentipawnEvaluation, MateEvaluation)):
        raise EvaluationPresentationError("unsupported evaluation record")
    mover_bound = (
        evaluation.bound
        if decision_mover == "white"
        else _reverse_bound(evaluation.bound)
    )
    if isinstance(evaluation, CentipawnEvaluation):
        mover_cp = (
            evaluation.centipawns
            if decision_mover == "white"
            else -evaluation.centipawns
        )
        return {
            "kind": "centipawn",
            "unit": "centipawns",
            "white": {
                "centipawns": evaluation.centipawns,
                "bound": evaluation.bound,
            },
            "decision_mover": {
                "side": decision_mover,
                "centipawns": mover_cp,
                "bound": mover_bound,
            },
        }
    return {
        "kind": "mate",
        "winner": evaluation.winner,
        "plies_to_mate": evaluation.plies_to_mate,
        "white": {
            "favours_perspective": evaluation.winner == "white",
            "bound": evaluation.bound,
        },
        "decision_mover": {
            "side": decision_mover,
            "favours_perspective": evaluation.winner == decision_mover,
            "bound": mover_bound,
        },
    }


def _engine_identity(analysis: PositionAnalysis) -> dict[str, Any]:
    provenance = analysis.provenance
    return {
        "provider_name": provenance.provider_name,
        "provider_version": provenance.provider_version,
        "protocol": provenance.protocol,
        "engine_name": provenance.engine_name,
        "engine_version": provenance.engine_version,
        "binary_sha256": provenance.binary_sha256,
        "engine_options": [list(item) for item in provenance.engine_options],
        "engine_artifacts": [
            artifact.to_dict() for artifact in provenance.engine_artifacts
        ],
    }


def _analysis_quality(analysis: PositionAnalysis) -> str:
    if analysis.status == "partial":
        return "partial"
    if analysis.status == "terminal":
        return "terminal"
    if not analysis.lines:
        return "unavailable"
    if any(line.evaluation.bound != "exact" for line in analysis.lines):
        return "bounded"
    return "exact"


def _analysis_presentation(
    outcome: PositionAnalysis | AnalysisFailure,
    decision_mover: str,
) -> dict[str, Any]:
    if isinstance(outcome, AnalysisFailure):
        return {
            "status": "failure",
            "evidence_quality": "unavailable",
            "position_id": outcome.position_id,
            "fen": outcome.fen,
            "request_fingerprint": outcome.request_fingerprint,
            "result_fingerprint": None,
            "failure": {
                "code": outcome.code,
                "message": outcome.message,
            },
            "engine": None,
            "candidates": [],
        }
    return {
        "status": outcome.status,
        "evidence_quality": _analysis_quality(outcome),
        "position_id": outcome.position_id,
        "fen": outcome.fen,
        "request_fingerprint": outcome.request_fingerprint,
        "result_fingerprint": outcome.result_fingerprint,
        "engine": _engine_identity(outcome),
        "request": outcome.request.to_dict(),
        "termination": outcome.termination.to_dict(),
        "metrics": outcome.metrics.to_dict(),
        "candidates": [
            {
                "rank": line.rank,
                "root_move_uci": line.root_move_uci,
                "evaluation": _present_evaluation(
                    line.evaluation,
                    decision_mover,
                ),
                "pv_uci": list(line.pv_uci),
            }
            for line in outcome.lines
        ],
    }


def _expected_ref(outcome: PositionAnalysis | AnalysisFailure) -> dict[str, Any]:
    if isinstance(outcome, AnalysisFailure):
        return {
            "position_id": outcome.position_id,
            "fen": outcome.fen,
            "request_fingerprint": outcome.request_fingerprint,
            "result_fingerprint": None,
            "status": "failure",
            "failure_code": outcome.code,
        }
    return {
        "position_id": outcome.position_id,
        "fen": outcome.fen,
        "request_fingerprint": outcome.request_fingerprint,
        "result_fingerprint": outcome.result_fingerprint,
        "status": outcome.status,
        "failure_code": None,
    }


def _require_ref_matches(
    ref: AnalysisEvidenceRef,
    outcome: PositionAnalysis | AnalysisFailure,
    label: str,
) -> None:
    if ref.to_dict() != _expected_ref(outcome):
        raise EvaluationPresentationError(f"{label} evidence reference mismatch")


def _comparison_quality(comparison: DecisionComparison) -> str:
    kind = comparison.comparison_kind
    if kind == "partial_evidence":
        return "partial"
    if kind == "bound_limited":
        return "bounded"
    if kind == "incompatible_analysis_regime":
        return "incompatible"
    if kind == "incomparable":
        return "unavailable"
    return "exact"


def _expected_child_evaluation(
    outcome: PositionAnalysis | AnalysisFailure,
) -> CentipawnEvaluation | MateEvaluation | None:
    if isinstance(outcome, AnalysisFailure):
        return None
    if outcome.status != "complete" or not outcome.lines:
        return None
    return outcome.lines[0].evaluation


def _validate_comparison(
    root_analysis: PositionAnalysis,
    comparison: DecisionComparison,
    played_analysis: PositionAnalysis | AnalysisFailure | None,
) -> None:
    _require_ref_matches(comparison.root_analysis_ref, root_analysis, "root")
    if comparison.position_id != root_analysis.position_id:
        raise EvaluationPresentationError("comparison/root position mismatch")

    best_line = root_analysis.lines[0] if root_analysis.lines else None
    expected_best_move = None if best_line is None else best_line.root_move_uci
    expected_best_eval = None if best_line is None else best_line.evaluation
    if comparison.best_move_uci != expected_best_move:
        raise EvaluationPresentationError("comparison best move mismatch")
    if comparison.best_evaluation != expected_best_eval:
        raise EvaluationPresentationError("comparison best evaluation mismatch")

    source = comparison.played_evaluation_source
    if source == "root_multipv":
        if comparison.played_analysis_ref != comparison.root_analysis_ref:
            raise EvaluationPresentationError(
                "root MultiPV comparison must cite root analysis"
            )
        if comparison.played_root_line_rank is None:
            raise EvaluationPresentationError("root MultiPV rank is missing")
        rank = comparison.played_root_line_rank
        if rank > len(root_analysis.lines):
            raise EvaluationPresentationError("played root line rank is out of range")
        line = root_analysis.lines[rank - 1]
        if line.root_move_uci != comparison.played_move_uci:
            raise EvaluationPresentationError("played root move mismatch")
        if line.evaluation != comparison.played_evaluation:
            raise EvaluationPresentationError("played root evaluation mismatch")
        if played_analysis is not None:
            raise EvaluationPresentationError(
                "root MultiPV comparison must not supply child analysis"
            )
    elif source in {"child_reanalysis", "terminal_child"}:
        if played_analysis is None:
            if comparison.played_analysis_ref is not None:
                raise EvaluationPresentationError("played analysis record is missing")
        else:
            if comparison.played_analysis_ref is None:
                raise EvaluationPresentationError(
                    "played analysis reference is missing"
                )
            _require_ref_matches(
                comparison.played_analysis_ref,
                played_analysis,
                "played child",
            )
            if (
                source == "child_reanalysis"
                and comparison.played_evaluation
                != _expected_child_evaluation(played_analysis)
            ):
                raise EvaluationPresentationError(
                    "played child evaluation mismatch"
                )
    elif source == "unavailable":
        if comparison.played_analysis_ref is not None or played_analysis is not None:
            raise EvaluationPresentationError(
                "unavailable played evidence must not cite child analysis"
            )
    else:
        raise EvaluationPresentationError("unsupported played evaluation source")

    quality = _comparison_quality(comparison)
    if quality != "exact" and comparison.exact_centipawn_delta_for_mover is not None:
        raise EvaluationPresentationError(
            "non-exact comparison must not expose exact centipawn delta"
        )


def build_evaluation_presentation(
    *,
    root_analysis: PositionAnalysis,
    comparison: DecisionComparison,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Project exact M3/M4 evidence without inventing new chess semantics."""
    _validate_comparison(root_analysis, comparison, played_analysis)
    decision_mover = comparison.side_to_move
    quality = _comparison_quality(comparison)

    return {
        "schema_version": PRESENTATION_SCHEMA_VERSION,
        "subject": {
            "game_id": comparison.game_id,
            "position_id": comparison.position_id,
            "side_to_move": decision_mover,
            "played_move_uci": comparison.played_move_uci,
        },
        "score_semantics": {
            "canonical_engine_perspective": "white",
            "display_perspective": "decision_mover",
            "centipawn_unit": "centipawns",
            "mate_representation": "winner_and_plies_to_mate",
            "bound_semantics": "ordering_bound_in_display_perspective",
        },
        "root_analysis": _analysis_presentation(root_analysis, decision_mover),
        "played_child_analysis": (
            None
            if played_analysis is None
            else _analysis_presentation(played_analysis, decision_mover)
        ),
        "comparison": {
            "comparison_id": comparison.comparison_id,
            "evidence_quality": quality,
            "comparison_kind": comparison.comparison_kind,
            "preference": comparison.preference,
            "compatibility": comparison.compatibility,
            "played_evaluation_source": comparison.played_evaluation_source,
            "played_root_line_rank": comparison.played_root_line_rank,
            "best_move_uci": comparison.best_move_uci,
            "played_move_uci": comparison.played_move_uci,
            "best_evaluation": (
                None
                if comparison.best_evaluation is None
                else _present_evaluation(
                    comparison.best_evaluation,
                    decision_mover,
                )
            ),
            "played_evaluation": (
                None
                if comparison.played_evaluation is None
                else _present_evaluation(
                    comparison.played_evaluation,
                    decision_mover,
                )
            ),
            "exact_centipawn_delta_for_mover": (
                comparison.exact_centipawn_delta_for_mover
            ),
            "mate_relation": comparison.mate_relation,
            "terminal_outcome": comparison.terminal_outcome,
            "detail": comparison.detail,
        },
        "evidence_refs": {
            "root_analysis": comparison.root_analysis_ref.to_dict(),
            "played_analysis": (
                None
                if comparison.played_analysis_ref is None
                else comparison.played_analysis_ref.to_dict()
            ),
            "decision_comparison": {
                "comparison_id": comparison.comparison_id,
                "policy": comparison.policy.to_dict(),
                "provenance": comparison.provenance.to_dict(),
            },
        },
    }
