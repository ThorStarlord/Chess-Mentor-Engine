"""Deterministic learner-intelligence projections over qualified evidence."""

from .evidence_synthesis import (
    HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION,
    EvidenceSynthesisReference,
    HypothesisEvidenceCounts,
    HypothesisEvidenceSynthesis,
    HypothesisEvidenceUnitSynthesis,
    HypothesisReviewSummary,
    build_hypothesis_evidence_synthesis,
    validate_hypothesis_evidence_synthesis,
)

__all__ = [
    "HYPOTHESIS_EVIDENCE_SYNTHESIS_SCHEMA_VERSION",
    "EvidenceSynthesisReference",
    "HypothesisEvidenceCounts",
    "HypothesisEvidenceSynthesis",
    "HypothesisEvidenceUnitSynthesis",
    "HypothesisReviewSummary",
    "build_hypothesis_evidence_synthesis",
    "validate_hypothesis_evidence_synthesis",
]
