"""M4 diagnostic-position-selection API."""

from .candidate import DiagnosticCandidateError, record_diagnostic_candidate
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
    DiagnosticCandidate,
    SelectionEvidenceRef,
    SelectionPolicyIdentity,
    SelectionSignal,
)
from .signals import SIGNAL_SCHEMA_VERSION, SelectionSignalError, build_selection_signals

__all__ = [
    "AnalysisEvidenceRef",
    "DEFAULT_COMPARISON_POLICY",
    "DecisionComparison",
    "DecisionComparisonError",
    "DecisionComparisonPolicy",
    "DecisionProvenance",
    "DiagnosticCandidate",
    "DiagnosticCandidateError",
    "SIGNAL_SCHEMA_VERSION",
    "SelectionEvidenceRef",
    "SelectionPolicyIdentity",
    "SelectionSignal",
    "SelectionSignalError",
    "build_selection_signals",
    "compare_played_decision",
    "record_diagnostic_candidate",
]
