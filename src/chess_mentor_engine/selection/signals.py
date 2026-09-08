"""M4C objective selection-signal derivation."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.analysis.model import (
    AnalysisFailure,
    AnalysisOutcome,
    CentipawnEvaluation,
    PositionAnalysis,
)
from chess_mentor_engine.chess import PositionFeaturePacket, canonical_json
from chess_mentor_engine.chess._core import Board

from .model import (
    DecisionComparison,
    SelectionEvidenceRef,
    SelectionSignal,
    SelectionSignalKind,
)

SIGNAL_SCHEMA_VERSION = "1"


class SelectionSignalError(ValueError):
    """Raised when M4C inputs do not match the evidence cited by M4B."""


def build_selection_signals(
    *,
    comparison: DecisionComparison,
    root_features: PositionFeaturePacket,
    root_analysis: AnalysisOutcome,
) -> tuple[SelectionSignal, ...]:
    """Derive transparent, non-threshold objective signals for one decision."""
    _validate_feature_target(comparison, root_features)
    _validate_analysis_target(comparison, root_analysis)

    feature_ref = SelectionEvidenceRef(
        source="position_features",
        ref_id=f"features:{root_features.position_id}",
        fingerprint=_fingerprint(root_features.to_dict()),
    )
    comparison_ref = SelectionEvidenceRef(
        source="decision_comparison",
        ref_id=comparison.comparison_id,
        fingerprint=_fingerprint(comparison.to_dict()),
    )
    analysis_ref = SelectionEvidenceRef(
        source="root_analysis",
        ref_id=(
            comparison.root_analysis_ref.result_fingerprint
            or comparison.root_analysis_ref.request_fingerprint
        ),
        fingerprint=comparison.root_analysis_ref.result_fingerprint,
    )

    signals: list[SelectionSignal] = []

    def add(
        kind: SelectionSignalKind,
        raw_value: object,
        evidence: tuple[SelectionEvidenceRef, ...],
        detail: str | None = None,
    ) -> None:
        signals.append(
            _make_signal(
                comparison=comparison,
                kind=kind,
                raw_value=raw_value,
                evidence=evidence,
                detail=detail,
            )
        )

    root_complete = (
        isinstance(root_analysis, PositionAnalysis)
        and root_analysis.status == "complete"
    )

    if root_complete and comparison.best_move_uci is not None:
        rank_payload = {
            "played_move_uci": comparison.played_move_uci,
            "rank_1_move_uci": comparison.best_move_uci,
        }
        if comparison.played_move_uci == comparison.best_move_uci:
            add(
                "PLAYED_EQUALS_RANK_1",
                rank_payload,
                (comparison_ref, analysis_ref),
            )
        else:
            add(
                "PLAYED_DIFFERS_FROM_RANK_1",
                rank_payload,
                (comparison_ref, analysis_ref),
            )

    if comparison.exact_centipawn_delta_for_mover is not None:
        add(
            "EXACT_CP_DELTA",
            comparison.exact_centipawn_delta_for_mover,
            (comparison_ref,),
        )

    if comparison.mate_relation is not None:
        add("MATE_RELATION", comparison.mate_relation, (comparison_ref,))

    if comparison.comparison_kind == "engine_evidence_inversion":
        add(
            "ENGINE_EVIDENCE_INVERSION",
            {
                "exact_centipawn_delta_for_mover": (
                    comparison.exact_centipawn_delta_for_mover
                ),
                "mate_relation": comparison.mate_relation,
            },
            (comparison_ref,),
        )

    top_separation = _top_candidate_separation(comparison, root_analysis)
    if top_separation is not None:
        add(
            "TOP_CANDIDATE_SEPARATION",
            top_separation,
            (analysis_ref,),
            detail="raw exact centipawn separation; no close-choice threshold applied",
        )

    played_move = comparison.played_move_uci
    if played_move not in root_features.legal_moves:
        raise SelectionSignalError(
            "comparison played move is absent from root PositionFeaturePacket"
        )
    _add_move_shape_signals(
        add=add,
        prefix="PLAYED_MOVE",
        move=played_move,
        features=root_features,
        evidence=(comparison_ref, feature_ref),
    )

    best_move = comparison.best_move_uci
    if root_complete and best_move is not None:
        if best_move not in root_features.legal_moves:
            raise SelectionSignalError(
                "comparison best move is absent from root PositionFeaturePacket"
            )
        _add_move_shape_signals(
            add=add,
            prefix="BEST_MOVE",
            move=best_move,
            features=root_features,
            evidence=(comparison_ref, feature_ref),
        )

    board = Board.from_fen(root_features.fen)
    if board.is_in_check(root_features.side_to_move):
        add(
            "ROOT_SIDE_IS_IN_CHECK",
            {"side_to_move": root_features.side_to_move, "in_check": True},
            (feature_ref,),
        )

    return tuple(sorted(signals, key=lambda item: (item.kind, item.signal_id)))


def _validate_feature_target(
    comparison: DecisionComparison,
    features: PositionFeaturePacket,
) -> None:
    expected = (
        comparison.position_id,
        comparison.game_id,
        comparison.provenance.root_ply_index,
        comparison.side_to_move,
        comparison.root_analysis_ref.fen,
    )
    actual = (
        features.position_id,
        features.game_id,
        features.ply_index,
        features.side_to_move,
        features.fen,
    )
    if actual != expected:
        raise SelectionSignalError(
            "PositionFeaturePacket does not target the M4B root decision"
        )


def _validate_analysis_target(
    comparison: DecisionComparison,
    analysis: AnalysisOutcome,
) -> None:
    ref = comparison.root_analysis_ref
    if analysis.position_id != ref.position_id or analysis.fen != ref.fen:
        raise SelectionSignalError("root analysis target does not match M4B evidence")
    if analysis.request_fingerprint != ref.request_fingerprint:
        raise SelectionSignalError("root analysis request fingerprint mismatch")
    if isinstance(analysis, AnalysisFailure):
        if ref.status != "failure" or analysis.code != ref.failure_code:
            raise SelectionSignalError(
                "root analysis failure does not match M4B evidence"
            )
        return
    if analysis.status != ref.status:
        raise SelectionSignalError("root analysis status does not match M4B evidence")
    if analysis.result_fingerprint != ref.result_fingerprint:
        raise SelectionSignalError("root analysis result fingerprint mismatch")


def _top_candidate_separation(
    comparison: DecisionComparison,
    analysis: AnalysisOutcome,
) -> dict[str, object] | None:
    if not isinstance(analysis, PositionAnalysis):
        return None
    if analysis.status != "complete" or len(analysis.lines) < 2:
        return None
    first = analysis.lines[0]
    second = analysis.lines[1]
    if not isinstance(first.evaluation, CentipawnEvaluation):
        return None
    if not isinstance(second.evaluation, CentipawnEvaluation):
        return None
    if first.evaluation.bound != "exact" or second.evaluation.bound != "exact":
        return None
    multiplier = 1 if comparison.side_to_move == "white" else -1
    separation = multiplier * (
        first.evaluation.centipawns - second.evaluation.centipawns
    )
    return {
        "rank_1_move_uci": first.root_move_uci,
        "rank_2_move_uci": second.root_move_uci,
        "exact_centipawn_separation_for_mover": separation,
    }


def _add_move_shape_signals(
    *,
    add,
    prefix: str,
    move: str,
    features: PositionFeaturePacket,
    evidence: tuple[SelectionEvidenceRef, ...],
) -> None:
    is_check = move in features.legal_checks
    is_capture = move in features.legal_captures
    if is_check:
        add(f"{prefix}_IS_CHECK", move, evidence)
    if is_capture:
        add(f"{prefix}_IS_CAPTURE", move, evidence)
    if not is_check and not is_capture:
        add(f"{prefix}_IS_QUIET", move, evidence)


def _make_signal(
    *,
    comparison: DecisionComparison,
    kind: SelectionSignalKind,
    raw_value: object,
    evidence: tuple[SelectionEvidenceRef, ...],
    detail: str | None,
) -> SelectionSignal:
    ordered_evidence = tuple(
        sorted(
            evidence,
            key=lambda item: (item.source, item.ref_id, item.fingerprint or ""),
        )
    )
    payload = {
        "kind": kind,
        "position_id": comparison.position_id,
        "game_id": comparison.game_id,
        "comparison_id": comparison.comparison_id,
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "raw_value": raw_value,
        "evidence": [item.to_dict() for item in ordered_evidence],
        "detail": detail,
    }
    signal_id = f"signal_{_fingerprint(payload)[:20]}"
    return SelectionSignal(
        signal_id=signal_id,
        kind=kind,
        position_id=comparison.position_id,
        game_id=comparison.game_id,
        comparison_id=comparison.comparison_id,
        schema_version=SIGNAL_SCHEMA_VERSION,
        raw_value=raw_value,
        evidence=ordered_evidence,
        detail=detail,
    )


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
