"""Immutable M6C coded local discrepancy-assessment records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from .model import (
    DiscrepancyFactKind,
    MeasurementCondition,
    ReasoningEvidenceKind,
    ReasoningEvidenceRef,
)

CoderKind: TypeAlias = Literal["human", "model"]
ReasoningCodingKind: TypeAlias = Literal[
    "discrepancy_support",
    "discrepancy_contradiction",
    "discrepancy_unclear",
]
DiscrepancyCode: TypeAlias = Literal[
    "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED",
    "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
    "EXPECTED_OPPONENT_REPLY_CONFLICT",
    "EXPECTED_CONTINUATION_CONFLICT",
    "REPORTED_RESULTING_EVALUATION_CONFLICT",
    "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE",
    "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
    "OTHER_LOCAL_DISCREPANCY",
]
AssertionBasisKind: TypeAlias = Literal["deterministic", "coded", "mixed"]
AssessmentStatus: TypeAlias = Literal[
    "discrepancy_supported",
    "no_supported_discrepancy",
    "unclear",
    "unscorable",
]
AssessmentStageKind: TypeAlias = Literal["MINIMAL_RESPONSE", "STANDARDIZED_PROBE"]
ReasoningArtifactKind: TypeAlias = Literal[
    "discrepancy_fact",
    "reasoning_coding",
    "discrepancy_assertion",
]


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


def _require_unique_ids(name: str, values: tuple[Any, ...]) -> None:
    ids = tuple(item.ref_id for item in values)
    if len(set(ids)) != len(ids):
        raise ValueError(f"{name} must be unique")


@dataclass(frozen=True, slots=True)
class ReasoningArtifactRef:
    """Stable reference to one immutable M6 fact/coding/assertion record."""

    kind: ReasoningArtifactKind
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("ref_id", self.ref_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class ReasoningAssessmentPolicyRef:
    """Material identity for the assessment policy that governed one result."""

    policy_id: str
    version: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("policy_id", self.policy_id)
        _require_nonempty("version", self.version)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class ReasoningAssessmentPolicy:
    """Versioned, material M6C policy for one position-local assessment."""

    policy_id: str
    version: str
    policy_fingerprint: str
    eligible_stage_kinds: tuple[AssessmentStageKind, ...]
    allowed_measurement_conditions: tuple[MeasurementCondition, ...]
    required_objective_evidence: tuple[ReasoningEvidenceKind, ...]
    permitted_fact_kinds: tuple[DiscrepancyFactKind, ...]
    permitted_discrepancy_codes: tuple[DiscrepancyCode, ...]
    coding_requirements: tuple[DiscrepancyCode, ...]
    thresholds_or_parameters: tuple[tuple[str, str], ...]
    claim_scope: Literal["position_local"] = "position_local"

    def __post_init__(self) -> None:
        _require_nonempty("policy_id", self.policy_id)
        _require_nonempty("version", self.version)
        _require_nonempty("policy_fingerprint", self.policy_fingerprint)
        if not self.eligible_stage_kinds:
            raise ValueError("eligible_stage_kinds must not be empty")
        if len(set(self.eligible_stage_kinds)) != len(self.eligible_stage_kinds):
            raise ValueError("eligible_stage_kinds must be unique")
        if not self.allowed_measurement_conditions:
            raise ValueError("allowed_measurement_conditions must not be empty")
        for values, name in (
            (self.allowed_measurement_conditions, "allowed measurement conditions"),
            (self.required_objective_evidence, "required objective evidence"),
            (self.permitted_fact_kinds, "permitted fact kinds"),
            (self.permitted_discrepancy_codes, "permitted discrepancy codes"),
            (self.coding_requirements, "coding requirements"),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must be unique")
        if not set(self.coding_requirements).issubset(
            self.permitted_discrepancy_codes
        ):
            raise ValueError(
                "coding requirements must be a subset of permitted discrepancy codes"
            )
        parameter_keys = tuple(key for key, _ in self.thresholds_or_parameters)
        if any(not key for key in parameter_keys):
            raise ValueError("assessment parameter keys must not be empty")
        if len(set(parameter_keys)) != len(parameter_keys):
            raise ValueError("assessment parameter keys must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "policy_id": self.policy_id,
            "version": self.version,
            "eligible_stage_kinds": list(self.eligible_stage_kinds),
            "allowed_measurement_conditions": list(
                self.allowed_measurement_conditions
            ),
            "required_objective_evidence": list(self.required_objective_evidence),
            "permitted_fact_kinds": list(self.permitted_fact_kinds),
            "permitted_discrepancy_codes": list(
                self.permitted_discrepancy_codes
            ),
            "coding_requirements": list(self.coding_requirements),
            "thresholds_or_parameters": [
                [key, value] for key, value in self.thresholds_or_parameters
            ],
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["policy_fingerprint"] = self.policy_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class ReasoningCoding:
    """Append-only human/model discrepancy judgment with exact source provenance."""

    coding_id: str
    fingerprint: str
    reasoning_context_id: str
    coding_kind: ReasoningCodingKind
    code: DiscrepancyCode
    statement: str
    stage_ids: tuple[str, ...]
    source_player_evidence_refs: tuple[ReasoningEvidenceRef, ...]
    source_objective_evidence_refs: tuple[ReasoningEvidenceRef, ...]
    source_fact_refs: tuple[ReasoningArtifactRef, ...]
    coder_kind: CoderKind
    coder_id: str
    coder_version: str
    rubric_or_instruction_fingerprint: str
    confidence: float | None
    uncertainty_note: str | None
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("coding_id", self.coding_id),
            ("fingerprint", self.fingerprint),
            ("reasoning_context_id", self.reasoning_context_id),
            ("statement", self.statement),
            ("coder_id", self.coder_id),
            ("coder_version", self.coder_version),
            (
                "rubric_or_instruction_fingerprint",
                self.rubric_or_instruction_fingerprint,
            ),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if not self.stage_ids:
            raise ValueError("ReasoningCoding must cite at least one assessment stage")
        if len(set(self.stage_ids)) != len(self.stage_ids):
            raise ValueError("ReasoningCoding stage_ids must be unique")
        if not (
            self.source_player_evidence_refs
            or self.source_objective_evidence_refs
            or self.source_fact_refs
        ):
            raise ValueError("ReasoningCoding must cite source evidence")
        _require_unique_ids(
            "source player evidence refs", self.source_player_evidence_refs
        )
        _require_unique_ids(
            "source objective evidence refs", self.source_objective_evidence_refs
        )
        _require_unique_ids("source fact refs", self.source_fact_refs)
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "reasoning_context_id": self.reasoning_context_id,
            "coding_kind": self.coding_kind,
            "code": self.code,
            "statement": self.statement,
            "stage_ids": list(self.stage_ids),
            "source_player_evidence_refs": [
                item.to_dict() for item in self.source_player_evidence_refs
            ],
            "source_objective_evidence_refs": [
                item.to_dict() for item in self.source_objective_evidence_refs
            ],
            "source_fact_refs": [item.to_dict() for item in self.source_fact_refs],
            "coder_kind": self.coder_kind,
            "coder_id": self.coder_id,
            "coder_version": self.coder_version,
            "rubric_or_instruction_fingerprint": (
                self.rubric_or_instruction_fingerprint
            ),
            "confidence": self.confidence,
            "uncertainty_note": self.uncertainty_note,
            "created_at": self.created_at,
        }
        if include_identity:
            payload["coding_id"] = self.coding_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class ReasoningDiscrepancyAssertion:
    """One conservative position-local discrepancy assertion."""

    assertion_id: str
    fingerprint: str
    reasoning_context_id: str
    assessment_policy_ref: ReasoningAssessmentPolicyRef
    code: DiscrepancyCode
    statement: str
    stage_ids: tuple[str, ...]
    supporting_fact_refs: tuple[ReasoningArtifactRef, ...]
    supporting_coding_refs: tuple[ReasoningArtifactRef, ...]
    contradictory_evidence_refs: tuple[ReasoningArtifactRef, ...]
    basis_kind: AssertionBasisKind
    claim_scope: Literal["position_local"] = "position_local"

    def __post_init__(self) -> None:
        for name, value in (
            ("assertion_id", self.assertion_id),
            ("fingerprint", self.fingerprint),
            ("reasoning_context_id", self.reasoning_context_id),
            ("statement", self.statement),
        ):
            _require_nonempty(name, value)
        if not self.stage_ids:
            raise ValueError("assertion must cite at least one assessment stage")
        if len(set(self.stage_ids)) != len(self.stage_ids):
            raise ValueError("assertion stage_ids must be unique")
        if not (self.supporting_fact_refs or self.supporting_coding_refs):
            raise ValueError("assertion must cite supporting facts and/or coding")
        _require_unique_ids("supporting fact refs", self.supporting_fact_refs)
        _require_unique_ids("supporting coding refs", self.supporting_coding_refs)
        _require_unique_ids(
            "contradictory evidence refs", self.contradictory_evidence_refs
        )
        expected_basis: AssertionBasisKind
        if self.supporting_fact_refs and self.supporting_coding_refs:
            expected_basis = "mixed"
        elif self.supporting_fact_refs:
            expected_basis = "deterministic"
        else:
            expected_basis = "coded"
        if self.basis_kind != expected_basis:
            raise ValueError("assertion basis_kind does not match its support refs")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "reasoning_context_id": self.reasoning_context_id,
            "assessment_policy_ref": self.assessment_policy_ref.to_dict(),
            "code": self.code,
            "statement": self.statement,
            "stage_ids": list(self.stage_ids),
            "supporting_fact_refs": [
                item.to_dict() for item in self.supporting_fact_refs
            ],
            "supporting_coding_refs": [
                item.to_dict() for item in self.supporting_coding_refs
            ],
            "contradictory_evidence_refs": [
                item.to_dict() for item in self.contradictory_evidence_refs
            ],
            "basis_kind": self.basis_kind,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["assertion_id"] = self.assertion_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class ReasoningDiscrepancyAssessment:
    """Immutable M6C assessment under one exact policy and local context."""

    assessment_id: str
    fingerprint: str
    reasoning_context_id: str
    assessment_policy_ref: ReasoningAssessmentPolicyRef
    status: AssessmentStatus
    assessed_stage_ids: tuple[str, ...]
    assertion_refs: tuple[ReasoningArtifactRef, ...]
    fact_refs: tuple[ReasoningArtifactRef, ...]
    coding_refs: tuple[ReasoningArtifactRef, ...]
    contradictory_evidence_refs: tuple[ReasoningArtifactRef, ...]
    measurement_condition: MeasurementCondition
    status_reasons: tuple[str, ...]
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("assessment_id", self.assessment_id),
            ("fingerprint", self.fingerprint),
            ("reasoning_context_id", self.reasoning_context_id),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if len(set(self.assessed_stage_ids)) != len(self.assessed_stage_ids):
            raise ValueError("assessed_stage_ids must be unique")
        _require_unique_ids("assertion refs", self.assertion_refs)
        _require_unique_ids("fact refs", self.fact_refs)
        _require_unique_ids("coding refs", self.coding_refs)
        _require_unique_ids(
            "contradictory evidence refs", self.contradictory_evidence_refs
        )
        if len(set(self.status_reasons)) != len(self.status_reasons):
            raise ValueError("status_reasons must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "reasoning_context_id": self.reasoning_context_id,
            "assessment_policy_ref": self.assessment_policy_ref.to_dict(),
            "status": self.status,
            "assessed_stage_ids": list(self.assessed_stage_ids),
            "assertion_refs": [item.to_dict() for item in self.assertion_refs],
            "fact_refs": [item.to_dict() for item in self.fact_refs],
            "coding_refs": [item.to_dict() for item in self.coding_refs],
            "contradictory_evidence_refs": [
                item.to_dict() for item in self.contradictory_evidence_refs
            ],
            "measurement_condition": self.measurement_condition,
            "status_reasons": list(self.status_reasons),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["assessment_id"] = self.assessment_id
            payload["fingerprint"] = self.fingerprint
        return payload
