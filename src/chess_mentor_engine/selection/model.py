"""Immutable M4 decision-selection records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.analysis.model import Evaluation

ComparisonKind: TypeAlias = Literal[
    "better_for_mover",
    "approximately_equal_under_policy",
    "worse_for_mover",
    "engine_evidence_inversion",
    "incompatible_analysis_regime",
    "partial_evidence",
    "bound_limited",
    "terminal_relation",
    "incomparable",
]
ComparisonPreference: TypeAlias = Literal[
    "better_for_mover",
    "approximately_equal_under_policy",
    "worse_for_mover",
    "engine_evidence_inversion",
    "incomparable",
]
CompatibilityStatus: TypeAlias = Literal[
    "same_root_analysis",
    "compatible",
    "incompatible",
    "not_applicable",
    "not_assessed",
]
PlayedEvaluationSource: TypeAlias = Literal[
    "root_multipv",
    "child_reanalysis",
    "terminal_child",
    "unavailable",
]
TerminalOutcome: TypeAlias = Literal["checkmate", "stalemate"]
SelectionSignalKind: TypeAlias = Literal[
    "PLAYED_EQUALS_RANK_1",
    "PLAYED_DIFFERS_FROM_RANK_1",
    "EXACT_CP_DELTA",
    "MATE_RELATION",
    "TOP_CANDIDATE_SEPARATION",
    "BEST_MOVE_IS_CHECK",
    "BEST_MOVE_IS_CAPTURE",
    "BEST_MOVE_IS_QUIET",
    "PLAYED_MOVE_IS_CHECK",
    "PLAYED_MOVE_IS_CAPTURE",
    "PLAYED_MOVE_IS_QUIET",
    "ROOT_SIDE_IS_IN_CHECK",
    "ENGINE_EVIDENCE_INVERSION",
]
SelectionEvidenceSource: TypeAlias = Literal[
    "decision_comparison",
    "position_features",
    "root_analysis",
]


@dataclass(frozen=True, slots=True)
class DecisionComparisonPolicy:
    """Versioned M4B-only configuration for exact score equivalence."""

    policy_id: str = "m4b-exact-comparison"
    version: str = "1"
    exact_cp_tolerance: int = 0

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")
        if self.exact_cp_tolerance < 0:
            raise ValueError("exact_cp_tolerance must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "exact_cp_tolerance": self.exact_cp_tolerance,
        }


@dataclass(frozen=True, slots=True)
class AnalysisEvidenceRef:
    position_id: str
    fen: str
    request_fingerprint: str
    result_fingerprint: str | None
    status: str
    failure_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "fen": self.fen,
            "request_fingerprint": self.request_fingerprint,
            "result_fingerprint": self.result_fingerprint,
            "status": self.status,
            "failure_code": self.failure_code,
        }


@dataclass(frozen=True, slots=True)
class DecisionProvenance:
    source_sha256: str
    game_semantic_fingerprint: str
    root_ply_index: int
    played_move_index: int
    child_position_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "game_semantic_fingerprint": self.game_semantic_fingerprint,
            "root_ply_index": self.root_ply_index,
            "played_move_index": self.played_move_index,
            "child_position_id": self.child_position_id,
        }


@dataclass(frozen=True, slots=True)
class DecisionComparison:
    comparison_id: str
    position_id: str
    game_id: str
    played_move_uci: str
    side_to_move: Literal["white", "black"]
    root_analysis_ref: AnalysisEvidenceRef
    played_evaluation_source: PlayedEvaluationSource
    played_analysis_ref: AnalysisEvidenceRef | None
    played_root_line_rank: int | None
    best_move_uci: str | None
    best_evaluation: Evaluation | None
    played_evaluation: Evaluation | None
    compatibility: CompatibilityStatus
    comparison_kind: ComparisonKind
    preference: ComparisonPreference
    exact_centipawn_delta_for_mover: int | None
    mate_relation: str | None
    terminal_outcome: TerminalOutcome | None
    policy: DecisionComparisonPolicy
    provenance: DecisionProvenance
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.side_to_move not in {"white", "black"}:
            raise ValueError(f"invalid side_to_move: {self.side_to_move!r}")
        if self.played_root_line_rank is not None and self.played_root_line_rank <= 0:
            raise ValueError("played_root_line_rank must be positive when provided")

    def to_dict(self, *, include_comparison_id: bool = True) -> dict[str, Any]:
        payload = {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "played_move_uci": self.played_move_uci,
            "side_to_move": self.side_to_move,
            "root_analysis_ref": self.root_analysis_ref.to_dict(),
            "played_evaluation_source": self.played_evaluation_source,
            "played_analysis_ref": (
                None
                if self.played_analysis_ref is None
                else self.played_analysis_ref.to_dict()
            ),
            "played_root_line_rank": self.played_root_line_rank,
            "best_move_uci": self.best_move_uci,
            "best_evaluation": (
                None if self.best_evaluation is None else self.best_evaluation.to_dict()
            ),
            "played_evaluation": (
                None
                if self.played_evaluation is None
                else self.played_evaluation.to_dict()
            ),
            "compatibility": self.compatibility,
            "comparison_kind": self.comparison_kind,
            "preference": self.preference,
            "exact_centipawn_delta_for_mover": (
                self.exact_centipawn_delta_for_mover
            ),
            "mate_relation": self.mate_relation,
            "terminal_outcome": self.terminal_outcome,
            "policy": self.policy.to_dict(),
            "provenance": self.provenance.to_dict(),
            "detail": self.detail,
        }
        if include_comparison_id:
            payload["comparison_id"] = self.comparison_id
        return payload


@dataclass(frozen=True, slots=True)
class SelectionEvidenceRef:
    """Stable reference to one objective evidence record used by a signal."""

    source: SelectionEvidenceSource
    ref_id: str
    fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not self.ref_id:
            raise ValueError("selection evidence ref_id must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class SelectionSignal:
    """One objective, reconstructable M4C property of a canonical decision."""

    signal_id: str
    kind: SelectionSignalKind
    position_id: str
    game_id: str
    comparison_id: str
    schema_version: str
    raw_value: Any
    evidence: tuple[SelectionEvidenceRef, ...]
    detail: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("signal_id", self.signal_id),
            ("position_id", self.position_id),
            ("game_id", self.game_id),
            ("comparison_id", self.comparison_id),
            ("schema_version", self.schema_version),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")
        if not self.evidence:
            raise ValueError("selection signal must cite at least one evidence record")

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "kind": self.kind,
            "position_id": self.position_id,
            "game_id": self.game_id,
            "comparison_id": self.comparison_id,
            "schema_version": self.schema_version,
            "raw_value": self.raw_value,
            "evidence": [item.to_dict() for item in self.evidence],
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class SelectionPolicyIdentity:
    """Opaque M4C reference to policy identity; policy execution belongs to M4D."""

    policy_id: str
    version: str

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {"policy_id": self.policy_id, "version": self.version}


@dataclass(frozen=True, slots=True)
class DiagnosticCandidate:
    """Immutable record that an external policy marked a decision as eligible."""

    candidate_id: str
    position_id: str
    game_id: str
    comparison_id: str
    selection_policy: SelectionPolicyIdentity
    signals: tuple[SelectionSignal, ...]
    eligibility_signal_ids: tuple[str, ...]
    provenance: DecisionProvenance

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id must not be empty")
        if not self.signals:
            raise ValueError("diagnostic candidate must retain at least one signal")
        if not self.eligibility_signal_ids:
            raise ValueError("candidate must name at least one eligibility signal")
        signal_ids = tuple(signal.signal_id for signal in self.signals)
        if len(set(signal_ids)) != len(signal_ids):
            raise ValueError("diagnostic candidate signals must be unique")
        if len(set(self.eligibility_signal_ids)) != len(self.eligibility_signal_ids):
            raise ValueError("eligibility_signal_ids must be unique")
        if not set(self.eligibility_signal_ids).issubset(signal_ids):
            raise ValueError("eligibility_signal_ids must reference retained signals")
        for signal in self.signals:
            if signal.position_id != self.position_id:
                raise ValueError("candidate signal position_id mismatch")
            if signal.game_id != self.game_id:
                raise ValueError("candidate signal game_id mismatch")
            if signal.comparison_id != self.comparison_id:
                raise ValueError("candidate signal comparison_id mismatch")

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "position_id": self.position_id,
            "game_id": self.game_id,
            "comparison_id": self.comparison_id,
            "selection_policy": self.selection_policy.to_dict(),
            "signals": [signal.to_dict() for signal in self.signals],
            "eligibility_signal_ids": list(self.eligibility_signal_ids),
            "provenance": self.provenance.to_dict(),
        }
