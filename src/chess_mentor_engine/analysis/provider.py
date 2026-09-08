"""Provider boundary for normalized engine evidence."""

from __future__ import annotations

from typing import Protocol

from chess_mentor_engine.chess import CanonicalPosition

from .model import AnalysisOutcome, AnalysisRequest


class ChessAnalysisProvider(Protocol):
    """Produce normalized engine evidence without leaking provider-native formats."""

    def analyze(
        self, position: CanonicalPosition, request: AnalysisRequest
    ) -> AnalysisOutcome:
        """Analyze one canonical position under one explicit request."""
        ...
