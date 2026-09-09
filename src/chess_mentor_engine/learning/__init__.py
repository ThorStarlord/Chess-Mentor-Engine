"""Position-local learning evidence derived from qualified chess/player evidence."""

from .context import build_reasoning_discrepancy_context
from .facts import ReasoningDiscrepancyError, derive_discrepancy_facts
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
