"""Stable identity helpers for normalized engine evidence."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.chess import canonical_json

from .model import AnalysisRequest, EngineProvenance, PositionAnalysis


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def analysis_request_fingerprint(
    *, fen: str, request: AnalysisRequest, provenance: EngineProvenance
) -> str:
    payload = {
        "fen": fen,
        "request": request.to_dict(),
        "provenance": provenance.to_dict(),
    }
    return _sha256_text(canonical_json(payload))


def analysis_result_fingerprint(analysis: PositionAnalysis) -> str:
    payload = analysis.to_dict(include_result_fingerprint=False)
    return _sha256_text(canonical_json(payload))
