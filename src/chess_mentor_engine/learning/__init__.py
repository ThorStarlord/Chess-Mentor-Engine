"""Position-local learning evidence derived from qualified chess/player evidence."""

from .facts import (
    ReasoningDiscrepancyError,
    build_reasoning_discrepancy_context,
    derive_discrepancy_facts,
)
from .model import (
    DiscrepancyFact,
    DiscrepancyFactKind,
    DiscrepancyRelation,
    MeasurementCondition,
    ReasoningDiscrepancyContext,
    ReasoningEvidenceRef,
)

__all__ = [
    "DiscrepancyFact",
    "DiscrepancyFactKind",
    "DiscrepancyRelation",
    "MeasurementCondition",
    "ReasoningDiscrepancyContext",
    "ReasoningDiscrepancyError",
    "ReasoningEvidenceRef",
    "build_reasoning_discrepancy_context",
    "derive_discrepancy_facts",
]
