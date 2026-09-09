"""Strict public M6B context binding across qualified M4 and M5 evidence."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import (
    CanonicalPosition,
    PositionFeaturePacket,
    canonical_json,
)
from chess_mentor_engine.evidence import EvidenceCaptureSession
from chess_mentor_engine.selection import (
    DecisionComparison,
    DiagnosticCandidate,
    DiagnosticCandidateBatch,
    SelectionSignal,
)

from .facts import ReasoningDiscrepancyError
from .facts import (
    build_reasoning_discrepancy_context as _build_context,
)
from .model import ReasoningDiscrepancyContext

AnalysisRecord = PositionAnalysis | AnalysisFailure


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def build_reasoning_discrepancy_context(
    *,
    capture_session: EvidenceCaptureSession,
    position: CanonicalPosition,
    diagnostic_candidate: DiagnosticCandidate,
    decision_comparison: DecisionComparison,
    assessment_stage_ids: tuple[str, ...],
    created_at: str,
    diagnostic_batch: DiagnosticCandidateBatch | None = None,
    position_features: PositionFeaturePacket | None = None,
    position_analyses: tuple[AnalysisRecord, ...] = (),
    selection_signals: tuple[SelectionSignal, ...] = (),
) -> ReasoningDiscrepancyContext:
    """Bind M6B only after proving the exact M4 candidate/batch relationship."""
    m5_context = capture_session.context
    if (
        diagnostic_candidate.candidate_id
        != m5_context.diagnostic_candidate_ref.ref_id
    ):
        raise ReasoningDiscrepancyError(
            "diagnostic candidate ID does not match M5 context"
        )
    if _fingerprint(diagnostic_candidate.to_dict()) != (
        m5_context.diagnostic_candidate_ref.fingerprint
    ):
        raise ReasoningDiscrepancyError(
            "diagnostic candidate fingerprint does not match M5 context"
        )
    if diagnostic_candidate.position_id != position.position_id:
        raise ReasoningDiscrepancyError("diagnostic candidate position_id mismatch")
    if diagnostic_candidate.game_id != position.game_id:
        raise ReasoningDiscrepancyError("diagnostic candidate game_id mismatch")
    if diagnostic_candidate.comparison_id != decision_comparison.comparison_id:
        raise ReasoningDiscrepancyError(
            "diagnostic candidate does not reference supplied decision comparison"
        )

    if m5_context.diagnostic_batch_ref is None:
        if diagnostic_batch is not None:
            raise ReasoningDiscrepancyError(
                "diagnostic batch supplied but M5 context has no batch reference"
            )
    else:
        if diagnostic_batch is None:
            raise ReasoningDiscrepancyError(
                "M5 context batch reference requires supplied diagnostic batch"
            )
        if diagnostic_batch.batch_id != m5_context.diagnostic_batch_ref.ref_id:
            raise ReasoningDiscrepancyError(
                "diagnostic batch ID does not match M5 context"
            )
        if _fingerprint(diagnostic_batch.to_dict()) != (
            m5_context.diagnostic_batch_ref.fingerprint
        ):
            raise ReasoningDiscrepancyError(
                "diagnostic batch fingerprint does not match M5 context"
            )
        if diagnostic_candidate.candidate_id not in {
            item.candidate_id for item in diagnostic_batch.candidates
        }:
            raise ReasoningDiscrepancyError(
                "diagnostic candidate is not selected in supplied batch"
            )

    candidate_signals = {
        item.signal_id: _fingerprint(item.to_dict())
        for item in diagnostic_candidate.signals
    }
    for signal in selection_signals:
        if signal.signal_id not in candidate_signals:
            raise ReasoningDiscrepancyError(
                "selection signal is not retained by diagnostic candidate"
            )
        if _fingerprint(signal.to_dict()) != candidate_signals[signal.signal_id]:
            raise ReasoningDiscrepancyError(
                "selection signal fingerprint differs from candidate evidence"
            )

    return _build_context(
        capture_session=capture_session,
        position=position,
        decision_comparison=decision_comparison,
        assessment_stage_ids=assessment_stage_ids,
        created_at=created_at,
        position_features=position_features,
        position_analyses=position_analyses,
        selection_signals=selection_signals,
    )
