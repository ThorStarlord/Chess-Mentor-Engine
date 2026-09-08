"""M4C immutable DiagnosticCandidate construction."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.chess import canonical_json

from .model import (
    DecisionComparison,
    DiagnosticCandidate,
    SelectionPolicyIdentity,
    SelectionSignal,
)


class DiagnosticCandidateError(ValueError):
    """Raised when candidate evidence does not belong to one M4B decision."""


def record_diagnostic_candidate(
    *,
    comparison: DecisionComparison,
    signals: tuple[SelectionSignal, ...],
    selection_policy: SelectionPolicyIdentity,
    eligibility_signal_ids: tuple[str, ...],
) -> DiagnosticCandidate:
    """Record policy-selected eligibility without executing M4D policy logic."""
    if not signals:
        raise DiagnosticCandidateError("candidate requires at least one signal")
    ordered_signals = tuple(
        sorted(signals, key=lambda item: (item.kind, item.signal_id))
    )
    signal_ids = tuple(signal.signal_id for signal in ordered_signals)
    if len(set(signal_ids)) != len(signal_ids):
        raise DiagnosticCandidateError("candidate signals must be unique")
    for signal in ordered_signals:
        if signal.position_id != comparison.position_id:
            raise DiagnosticCandidateError("signal position_id mismatch")
        if signal.game_id != comparison.game_id:
            raise DiagnosticCandidateError("signal game_id mismatch")
        if signal.comparison_id != comparison.comparison_id:
            raise DiagnosticCandidateError("signal comparison_id mismatch")

    if not eligibility_signal_ids:
        raise DiagnosticCandidateError(
            "candidate requires at least one policy eligibility signal"
        )
    if len(set(eligibility_signal_ids)) != len(eligibility_signal_ids):
        raise DiagnosticCandidateError("eligibility_signal_ids must be unique")
    if not set(eligibility_signal_ids).issubset(signal_ids):
        raise DiagnosticCandidateError(
            "eligibility_signal_ids must reference supplied signals"
        )
    ordered_eligibility = tuple(sorted(eligibility_signal_ids))

    payload = {
        "position_id": comparison.position_id,
        "game_id": comparison.game_id,
        "comparison_id": comparison.comparison_id,
        "selection_policy": selection_policy.to_dict(),
        "signal_ids": list(signal_ids),
        "eligibility_signal_ids": list(ordered_eligibility),
        "provenance": comparison.provenance.to_dict(),
    }
    candidate_id = f"candidate_{_fingerprint(payload)[:20]}"
    return DiagnosticCandidate(
        candidate_id=candidate_id,
        position_id=comparison.position_id,
        game_id=comparison.game_id,
        comparison_id=comparison.comparison_id,
        selection_policy=selection_policy,
        signals=ordered_signals,
        eligibility_signal_ids=ordered_eligibility,
        provenance=comparison.provenance,
    )


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
