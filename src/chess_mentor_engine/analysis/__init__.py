"""Normalized engine-evidence API for Chess Mentor Engine."""

from .fingerprints import analysis_request_fingerprint, analysis_result_fingerprint
from .model import (
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
)
from .precomputed import PrecomputedAnalysisProvider, PrecomputedFixture
from .provider import ChessAnalysisProvider

__all__ = [
    "AnalysisFailure",
    "AnalysisLimit",
    "AnalysisMetrics",
    "AnalysisRequest",
    "AnalysisTermination",
    "CandidateLine",
    "CentipawnEvaluation",
    "ChessAnalysisProvider",
    "EngineArtifact",
    "EngineProvenance",
    "MateEvaluation",
    "PositionAnalysis",
    "PrecomputedAnalysisProvider",
    "PrecomputedFixture",
    "analysis_request_fingerprint",
    "analysis_result_fingerprint",
]
