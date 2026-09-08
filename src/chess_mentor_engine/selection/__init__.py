"""M4 diagnostic-position-selection API."""

from .comparison import (
    DEFAULT_COMPARISON_POLICY,
    DecisionComparisonError,
    compare_played_decision,
)
from .model import (
    AnalysisEvidenceRef,
    DecisionComparison,
    DecisionComparisonPolicy,
    DecisionProvenance,
)

__all__ = [
    "AnalysisEvidenceRef",
    "DEFAULT_COMPARISON_POLICY",
    "DecisionComparison",
    "DecisionComparisonError",
    "DecisionComparisonPolicy",
    "DecisionProvenance",
    "compare_played_decision",
]
