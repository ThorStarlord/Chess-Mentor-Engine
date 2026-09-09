"""Immutable M6B deterministic reasoning-discrepancy records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

MeasurementCondition: TypeAlias = Literal[
    "clean",
    "instrument_aware_clean",
    "deviating",
    "contaminated",
    "unknown",
]
DiscrepancyRelation: TypeAlias = Literal[
    "match",
    "conflict",
    "not_explicitly_reported",
    "ambiguous",
    "not_observed",
    "not_comparable",
]
DiscrepancyFactKind: TypeAlias = Literal[
    "REPORTED_SELECTED_MOVE_RELATION",
    "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    "EXPECTED_REPLY_RELATION",
    "EXPECTED_CONTINUATION_RELATION",
]
ReasoningEvidenceAuthority: TypeAlias = Literal[
    "deterministic_chess",
    "engine_evidence",
    "m4_objective",
    "m5_participant",
]
ReasoningEvidenceKind: TypeAlias = Literal[
    "canonical_position",
    "position_feature_packet",
    "position_analysis",
    "analysis_failure",
    "decision_comparison",
    "selection_signal",
    "diagnostic_candidate",
    "diagnostic_batch",
    "player_decision_context",
    "capture_session",
    "prompt_presentation",
    "player_response",
    "evidence_freeze",
    "exposure_event",
    "protocol_deviation",
]


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class ReasoningEvidenceRef:
    """Stable M6 reference that preserves the upstream authority domain."""

    authority: ReasoningEvidenceAuthority
    kind: ReasoningEvidenceKind
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("ref_id", self.ref_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "authority": self.authority,
            "kind": self.kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class ReasoningDiscrepancyContext:
    """Exact position-local M4/M5 evidence bundle available to M6B."""

    reasoning_context_id: str
    context_fingerprint: str
    participant_id: str
    player_decision_context_ref: ReasoningEvidenceRef
    position_id: str
    game_id: str
    diagnostic_candidate_ref: ReasoningEvidenceRef
    diagnostic_batch_ref: ReasoningEvidenceRef | None
    capture_session_ref: ReasoningEvidenceRef
    assessment_stage_ids: tuple[str, ...]
    player_response_refs: tuple[ReasoningEvidenceRef, ...]
    evidence_freeze_refs: tuple[ReasoningEvidenceRef, ...]
    prompt_presentation_refs: tuple[ReasoningEvidenceRef, ...]
    exposure_refs: tuple[ReasoningEvidenceRef, ...]
    protocol_deviation_refs: tuple[ReasoningEvidenceRef, ...]
    canonical_position_ref: ReasoningEvidenceRef
    position_feature_packet_ref: ReasoningEvidenceRef | None
    position_analysis_refs: tuple[ReasoningEvidenceRef, ...]
    decision_comparison_ref: ReasoningEvidenceRef
    selection_signal_refs: tuple[ReasoningEvidenceRef, ...]
    measurement_condition: MeasurementCondition
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("reasoning_context_id", self.reasoning_context_id),
            ("context_fingerprint", self.context_fingerprint),
            ("participant_id", self.participant_id),
            ("position_id", self.position_id),
            ("game_id", self.game_id),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if not self.assessment_stage_ids:
            raise ValueError("assessment_stage_ids must not be empty")
        if len(set(self.assessment_stage_ids)) != len(self.assessment_stage_ids):
            raise ValueError("assessment_stage_ids must be unique")
        for values, label in (
            (self.player_response_refs, "player response refs"),
            (self.evidence_freeze_refs, "evidence freeze refs"),
            (self.prompt_presentation_refs, "prompt presentation refs"),
            (self.position_analysis_refs, "position analysis refs"),
            (self.selection_signal_refs, "selection signal refs"),
        ):
            ids = tuple(item.ref_id for item in values)
            if len(set(ids)) != len(ids):
                raise ValueError(f"{label} must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "player_decision_context_ref": self.player_decision_context_ref.to_dict(),
            "position_id": self.position_id,
            "game_id": self.game_id,
            "diagnostic_candidate_ref": self.diagnostic_candidate_ref.to_dict(),
            "diagnostic_batch_ref": (
                None
                if self.diagnostic_batch_ref is None
                else self.diagnostic_batch_ref.to_dict()
            ),
            "capture_session_ref": self.capture_session_ref.to_dict(),
            "assessment_stage_ids": list(self.assessment_stage_ids),
            "player_response_refs": [
                item.to_dict() for item in self.player_response_refs
            ],
            "evidence_freeze_refs": [
                item.to_dict() for item in self.evidence_freeze_refs
            ],
            "prompt_presentation_refs": [
                item.to_dict() for item in self.prompt_presentation_refs
            ],
            "exposure_refs": [item.to_dict() for item in self.exposure_refs],
            "protocol_deviation_refs": [
                item.to_dict() for item in self.protocol_deviation_refs
            ],
            "canonical_position_ref": self.canonical_position_ref.to_dict(),
            "position_feature_packet_ref": (
                None
                if self.position_feature_packet_ref is None
                else self.position_feature_packet_ref.to_dict()
            ),
            "position_analysis_refs": [
                item.to_dict() for item in self.position_analysis_refs
            ],
            "decision_comparison_ref": self.decision_comparison_ref.to_dict(),
            "selection_signal_refs": [
                item.to_dict() for item in self.selection_signal_refs
            ],
            "measurement_condition": self.measurement_condition,
            "created_at": self.created_at,
        }
        if include_identity:
            payload["reasoning_context_id"] = self.reasoning_context_id
            payload["context_fingerprint"] = self.context_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class DiscrepancyFact:
    """One deterministic descriptive relation; never a hidden-cognition claim."""

    fact_id: str
    fingerprint: str
    reasoning_context_id: str
    stage_id: str
    kind: DiscrepancyFactKind
    participant_evidence_refs: tuple[ReasoningEvidenceRef, ...]
    objective_evidence_refs: tuple[ReasoningEvidenceRef, ...]
    relation: DiscrepancyRelation
    participant_value: Any
    objective_value: Any
    comparison_provenance: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("fact_id", self.fact_id),
            ("fingerprint", self.fingerprint),
            ("reasoning_context_id", self.reasoning_context_id),
            ("stage_id", self.stage_id),
        ):
            _require_nonempty(name, value)
        if not self.participant_evidence_refs:
            raise ValueError("fact must cite participant evidence")
        if not self.objective_evidence_refs:
            raise ValueError("fact must cite objective evidence")
        keys = tuple(key for key, _ in self.comparison_provenance)
        if len(set(keys)) != len(keys):
            raise ValueError("comparison provenance keys must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "reasoning_context_id": self.reasoning_context_id,
            "stage_id": self.stage_id,
            "kind": self.kind,
            "participant_evidence_refs": [
                item.to_dict() for item in self.participant_evidence_refs
            ],
            "objective_evidence_refs": [
                item.to_dict() for item in self.objective_evidence_refs
            ],
            "relation": self.relation,
            "participant_value": self.participant_value,
            "objective_value": self.objective_value,
            "comparison_provenance": [
                [key, value] for key, value in self.comparison_provenance
            ],
        }
        if include_identity:
            payload["fact_id"] = self.fact_id
            payload["fingerprint"] = self.fingerprint
        return payload
