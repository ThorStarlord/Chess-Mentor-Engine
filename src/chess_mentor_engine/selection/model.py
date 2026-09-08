"""Immutable M4B decision-comparison records."""

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
