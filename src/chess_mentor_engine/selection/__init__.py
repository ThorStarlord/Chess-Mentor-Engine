"""M4 diagnostic-position-selection API."""

from .batch import (
    BatchExclusion,
    DiagnosticCandidateBatch,
    DiagnosticCandidateBatchError,
    QuotaOutcome,
    build_diagnostic_candidate_batch,
)
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
from .policy import (
    PolicySelectionResult,
    SelectionDecision,
    SelectionPolicy,
    SelectionPolicyError,
    SelectionQuota,
    SelectionRuleMatch,
    apply_selection_policy,
)
from .signals import (
    SIGNAL_SCHEMA_VERSION,
    SelectionSignalError,
    build_selection_signals,
)

__all__ = [
    "AnalysisEvidenceRef",
    "BatchExclusion",
    "DEFAULT_COMPARISON_POLICY",
    "DecisionComparison",
    "DecisionComparisonError",
    "DecisionComparisonPolicy",
    "DecisionProvenance",
    "DiagnosticCandidate",
    "DiagnosticCandidateBatch",
    "DiagnosticCandidateBatchError",
    "DiagnosticCandidateError",
    "PolicySelectionResult",
    "QuotaOutcome",
    "SIGNAL_SCHEMA_VERSION",
    "SelectionDecision",
    "SelectionEvidenceRef",
    "SelectionPolicy",
    "SelectionPolicyError",
    "SelectionPolicyIdentity",
    "SelectionQuota",
    "SelectionRuleMatch",
    "SelectionSignal",
    "SelectionSignalError",
    "apply_selection_policy",
    "build_diagnostic_candidate_batch",
    "build_selection_signals",
    "compare_played_decision",
    "record_diagnostic_candidate",
]
