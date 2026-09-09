"""Immutable M7C recurrence-assessment and derived-ledger records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from .assessment_model import AssessmentStatus, DiscrepancyCode
from .hypothesis_model import (
    HypothesisActorProvenance,
    HypothesisContextRef,
    HypothesisRevisionRef,
    LearnerHypothesisRef,
)
from .model import MeasurementCondition

HypothesisAssessmentStatus: TypeAlias = Literal[
    "insufficient",
    "isolated",
    "candidate_recurrence",
    "supported_recurrence",
    "contradicted",
    "unclear",
]
M6PolicyCompatibilityRule: TypeAlias = Literal[
    "same_policy_fingerprint",
    "declared_policy_fingerprints",
]
StageCompatibilityRule: TypeAlias = Literal[
    "same_assessed_stage_ids",
    "declared_stage_ids",
]
ContextMatchRule: TypeAlias = Literal[
    "exact_revision_contexts",
    "shared_revision_context",
    "broad_scope",
]
RecurrenceUnitRule: TypeAlias = Literal["participant_position"]
IndependenceRule: TypeAlias = Literal["distinct_game_id", "distinct_position_id"]
ContradictionRule: TypeAlias = Literal[
    "any_contradiction",
    "any_contradiction_or_counterexample",
]
HypothesisUnitRelation: TypeAlias = Literal[
    "supports",
    "contradicts",
    "successful_counterexample",
    "context_exception",
    "unclear",
    "mixed",
]
CompetingExplanationReviewState: TypeAlias = Literal["not_required", "completed"]
AuthorityLifecycleState: TypeAlias = Literal["active", "retired", "superseded"]

_ASSESSMENT_STATUSES = frozenset(
    {
        "insufficient",
        "isolated",
        "candidate_recurrence",
        "supported_recurrence",
        "contradicted",
        "unclear",
    }
)
_M6_POLICY_RULES = frozenset(
    {"same_policy_fingerprint", "declared_policy_fingerprints"}
)
_STAGE_RULES = frozenset({"same_assessed_stage_ids", "declared_stage_ids"})
_CONTEXT_RULES = frozenset(
    {"exact_revision_contexts", "shared_revision_context", "broad_scope"}
)
_INDEPENDENCE_RULES = frozenset({"distinct_game_id", "distinct_position_id"})
_CONTRADICTION_RULES = frozenset(
    {"any_contradiction", "any_contradiction_or_counterexample"}
)
_UNIT_RELATIONS = frozenset(
    {
        "supports",
        "contradicts",
        "successful_counterexample",
        "context_exception",
        "unclear",
        "mixed",
    }
)
_REVIEW_STATES = frozenset({"not_required", "completed"})
_LIFECYCLE_STATES = frozenset({"active", "retired", "superseded"})
_MEASUREMENT_CONDITIONS = frozenset(
    {"clean", "instrument_aware_clean", "deviating", "contaminated", "unknown"}
)


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


def _require_unique_strings(name: str, values: tuple[str, ...]) -> None:
    if any(not value for value in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceLinkRef:
    """Exact reference to one immutable M7B hypothesis-evidence link."""

    link_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("link_id", self.link_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {"link_id": self.link_id, "fingerprint": self.fingerprint}


@dataclass(frozen=True, slots=True)
class HypothesisAssessmentPolicyRef:
    """Exact material identity for one M7C recurrence-assessment policy."""

    assessment_policy_id: str
    version: str
    fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("assessment_policy_id", self.assessment_policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _require_nonempty(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "assessment_policy_id": self.assessment_policy_id,
            "version": self.version,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisAssessmentPolicy:
    """Versioned material policy governing participant-specific recurrence assessment."""

    assessment_policy_id: str
    version: str
    policy_fingerprint: str
    eligible_m6_statuses: tuple[AssessmentStatus, ...]
    eligible_discrepancy_codes: tuple[DiscrepancyCode, ...]
    allowed_measurement_conditions: tuple[MeasurementCondition, ...]
    m6_policy_compatibility_rule: M6PolicyCompatibilityRule
    compatible_m6_policy_fingerprints: tuple[str, ...]
    stage_compatibility_rule: StageCompatibilityRule
    allowed_stage_ids: tuple[str, ...]
    context_match_rule: ContextMatchRule
    recurrence_unit_rule: RecurrenceUnitRule
    independence_rule: IndependenceRule
    minimum_independent_supports_for_candidate: int
    minimum_independent_supports_for_supported: int
    required_contradiction_review: bool
    required_counterexample_review: bool
    required_competing_explanation_review: bool
    contradiction_rule: ContradictionRule
    claim_scope: Literal["participant_specific_cross_position"] = (
        "participant_specific_cross_position"
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("assessment_policy_id", self.assessment_policy_id),
            ("version", self.version),
            ("policy_fingerprint", self.policy_fingerprint),
        ):
            _require_nonempty(name, value)
        if not self.eligible_m6_statuses:
            raise ValueError("eligible_m6_statuses must not be empty")
        if not self.eligible_discrepancy_codes:
            raise ValueError("eligible_discrepancy_codes must not be empty")
        if not self.allowed_measurement_conditions:
            raise ValueError("allowed_measurement_conditions must not be empty")
        for values, name in (
            (self.eligible_m6_statuses, "eligible_m6_statuses"),
            (self.eligible_discrepancy_codes, "eligible_discrepancy_codes"),
            (self.allowed_measurement_conditions, "allowed_measurement_conditions"),
            (
                self.compatible_m6_policy_fingerprints,
                "compatible_m6_policy_fingerprints",
            ),
            (self.allowed_stage_ids, "allowed_stage_ids"),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must be unique")
        if self.m6_policy_compatibility_rule not in _M6_POLICY_RULES:
            raise ValueError("unknown M6 policy compatibility rule")
        if self.stage_compatibility_rule not in _STAGE_RULES:
            raise ValueError("unknown stage compatibility rule")
        if self.context_match_rule not in _CONTEXT_RULES:
            raise ValueError("unknown context match rule")
        if self.recurrence_unit_rule != "participant_position":
            raise ValueError("unknown recurrence unit rule")
        if self.independence_rule not in _INDEPENDENCE_RULES:
            raise ValueError("unknown independence rule")
        if self.contradiction_rule not in _CONTRADICTION_RULES:
            raise ValueError("unknown contradiction rule")
        if self.m6_policy_compatibility_rule == "same_policy_fingerprint":
            if self.compatible_m6_policy_fingerprints:
                raise ValueError(
                    "same_policy_fingerprint must not declare compatible fingerprints"
                )
        elif not self.compatible_m6_policy_fingerprints:
            raise ValueError(
                "declared_policy_fingerprints requires compatible fingerprints"
            )
        if self.stage_compatibility_rule == "same_assessed_stage_ids":
            if self.allowed_stage_ids:
                raise ValueError(
                    "same_assessed_stage_ids must not declare allowed_stage_ids"
                )
        elif not self.allowed_stage_ids:
            raise ValueError("declared_stage_ids requires allowed_stage_ids")
        if self.minimum_independent_supports_for_candidate < 2:
            raise ValueError(
                "minimum_independent_supports_for_candidate must be at least 2"
            )
        if (
            self.minimum_independent_supports_for_supported
            < self.minimum_independent_supports_for_candidate
        ):
            raise ValueError(
                "supported recurrence threshold must be >= candidate threshold"
            )
        if self.claim_scope != "participant_specific_cross_position":
            raise ValueError("unknown M7C claim scope")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "assessment_policy_id": self.assessment_policy_id,
            "version": self.version,
            "eligible_m6_statuses": list(self.eligible_m6_statuses),
            "eligible_discrepancy_codes": list(self.eligible_discrepancy_codes),
            "allowed_measurement_conditions": list(
                self.allowed_measurement_conditions
            ),
            "m6_policy_compatibility_rule": self.m6_policy_compatibility_rule,
            "compatible_m6_policy_fingerprints": list(
                self.compatible_m6_policy_fingerprints
            ),
            "stage_compatibility_rule": self.stage_compatibility_rule,
            "allowed_stage_ids": list(self.allowed_stage_ids),
            "context_match_rule": self.context_match_rule,
            "recurrence_unit_rule": self.recurrence_unit_rule,
            "independence_rule": self.independence_rule,
            "minimum_independent_supports_for_candidate": (
                self.minimum_independent_supports_for_candidate
            ),
            "minimum_independent_supports_for_supported": (
                self.minimum_independent_supports_for_supported
            ),
            "required_contradiction_review": self.required_contradiction_review,
            "required_counterexample_review": self.required_counterexample_review,
            "required_competing_explanation_review": (
                self.required_competing_explanation_review
            ),
            "contradiction_rule": self.contradiction_rule,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["policy_fingerprint"] = self.policy_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class CompetingExplanationReview:
    """Provenance-bound record that alternatives were considered, not refuted."""

    review_id: str
    fingerprint: str
    state: CompetingExplanationReviewState
    reviewed_hypothesis_refs: tuple[LearnerHypothesisRef, ...]
    reviewed_alternative_notes: tuple[str, ...]
    review_note: str
    reviewer_provenance: HypothesisActorProvenance | None
    created_at: str

    def __post_init__(self) -> None:
        if self.state not in _REVIEW_STATES:
            raise ValueError("unknown competing explanation review state")
        for name, value in (
            ("review_id", self.review_id),
            ("fingerprint", self.fingerprint),
            ("review_note", self.review_note),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        ids = tuple(item.hypothesis_id for item in self.reviewed_hypothesis_refs)
        if len(set(ids)) != len(ids):
            raise ValueError("reviewed_hypothesis_refs must be unique")
        _require_unique_strings(
            "reviewed_alternative_notes", self.reviewed_alternative_notes
        )
        if self.state == "completed" and self.reviewer_provenance is None:
            raise ValueError("completed review requires reviewer provenance")
        if self.state == "not_required" and self.reviewer_provenance is not None:
            raise ValueError("not_required review must not carry reviewer provenance")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "state": self.state,
            "reviewed_hypothesis_refs": [
                item.to_dict() for item in self.reviewed_hypothesis_refs
            ],
            "reviewed_alternative_notes": list(self.reviewed_alternative_notes),
            "review_note": self.review_note,
            "reviewer_provenance": (
                None
                if self.reviewer_provenance is None
                else self.reviewer_provenance.to_dict()
            ),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["review_id"] = self.review_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisRecurrenceUnit:
    """One participant-position recurrence unit after deterministic link aggregation."""

    recurrence_unit_id: str
    participant_id: str
    source_position_id: str
    source_game_id: str
    relation: HypothesisUnitRelation
    link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    independence_unit_id: str
    context_refs: tuple[HypothesisContextRef, ...]
    measurement_conditions: tuple[MeasurementCondition, ...]

    def __post_init__(self) -> None:
        if self.relation not in _UNIT_RELATIONS:
            raise ValueError("unknown recurrence unit relation")
        for name, value in (
            ("recurrence_unit_id", self.recurrence_unit_id),
            ("participant_id", self.participant_id),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("independence_unit_id", self.independence_unit_id),
        ):
            _require_nonempty(name, value)
        if not self.link_refs:
            raise ValueError("recurrence unit must contain at least one link")
        link_ids = tuple(item.link_id for item in self.link_refs)
        if len(set(link_ids)) != len(link_ids):
            raise ValueError("recurrence unit link refs must be unique")
        context_ids = tuple(item.ref_id for item in self.context_refs)
        if len(set(context_ids)) != len(context_ids):
            raise ValueError("recurrence unit context refs must be unique")
        if any(item not in _MEASUREMENT_CONDITIONS for item in self.measurement_conditions):
            raise ValueError("unknown recurrence unit measurement condition")
        if len(set(self.measurement_conditions)) != len(self.measurement_conditions):
            raise ValueError("measurement_conditions must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "recurrence_unit_id": self.recurrence_unit_id,
            "participant_id": self.participant_id,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "relation": self.relation,
            "link_refs": [item.to_dict() for item in self.link_refs],
            "independence_unit_id": self.independence_unit_id,
            "context_refs": [item.to_dict() for item in self.context_refs],
            "measurement_conditions": list(self.measurement_conditions),
        }


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceSummary:
    """Structured counts and exclusions; never a universal weakness score."""

    eligible_link_count: int
    excluded_link_count: int
    support_unit_count: int
    independent_support_count: int
    contradiction_unit_count: int
    successful_counterexample_unit_count: int
    context_exception_unit_count: int
    unclear_unit_count: int
    mixed_unit_count: int
    source_position_ids: tuple[str, ...]
    source_game_ids: tuple[str, ...]
    measurement_conditions: tuple[MeasurementCondition, ...]
    common_context_refs: tuple[HypothesisContextRef, ...]
    excluded_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    exclusion_reasons: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("eligible_link_count", self.eligible_link_count),
            ("excluded_link_count", self.excluded_link_count),
            ("support_unit_count", self.support_unit_count),
            ("independent_support_count", self.independent_support_count),
            ("contradiction_unit_count", self.contradiction_unit_count),
            (
                "successful_counterexample_unit_count",
                self.successful_counterexample_unit_count,
            ),
            ("context_exception_unit_count", self.context_exception_unit_count),
            ("unclear_unit_count", self.unclear_unit_count),
            ("mixed_unit_count", self.mixed_unit_count),
        ):
            if value < 0:
                raise ValueError(f"{name} must not be negative")
        _require_unique_strings("source_position_ids", self.source_position_ids)
        _require_unique_strings("source_game_ids", self.source_game_ids)
        if any(item not in _MEASUREMENT_CONDITIONS for item in self.measurement_conditions):
            raise ValueError("unknown evidence summary measurement condition")
        if len(set(self.measurement_conditions)) != len(self.measurement_conditions):
            raise ValueError("measurement_conditions must be unique")
        context_ids = tuple(item.ref_id for item in self.common_context_refs)
        if len(set(context_ids)) != len(context_ids):
            raise ValueError("common_context_refs must be unique")
        link_ids = tuple(item.link_id for item in self.excluded_link_refs)
        if len(set(link_ids)) != len(link_ids):
            raise ValueError("excluded_link_refs must be unique")
        reason_ids = tuple(link_id for link_id, _ in self.exclusion_reasons)
        if len(set(reason_ids)) != len(reason_ids):
            raise ValueError("exclusion_reasons link IDs must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "eligible_link_count": self.eligible_link_count,
            "excluded_link_count": self.excluded_link_count,
            "support_unit_count": self.support_unit_count,
            "independent_support_count": self.independent_support_count,
            "contradiction_unit_count": self.contradiction_unit_count,
            "successful_counterexample_unit_count": (
                self.successful_counterexample_unit_count
            ),
            "context_exception_unit_count": self.context_exception_unit_count,
            "unclear_unit_count": self.unclear_unit_count,
            "mixed_unit_count": self.mixed_unit_count,
            "source_position_ids": list(self.source_position_ids),
            "source_game_ids": list(self.source_game_ids),
            "measurement_conditions": list(self.measurement_conditions),
            "common_context_refs": [
                item.to_dict() for item in self.common_context_refs
            ],
            "excluded_link_refs": [item.to_dict() for item in self.excluded_link_refs],
            "exclusion_reasons": [
                [link_id, list(reasons)] for link_id, reasons in self.exclusion_reasons
            ],
        }


@dataclass(frozen=True, slots=True)
class HypothesisAssessment:
    """Immutable assessment of one exact hypothesis revision and evidence-link set."""

    hypothesis_assessment_id: str
    fingerprint: str
    hypothesis_revision_ref: HypothesisRevisionRef
    assessment_policy_ref: HypothesisAssessmentPolicyRef
    status: HypothesisAssessmentStatus
    support_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    contradiction_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    successful_counterexample_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    context_exception_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    unclear_link_refs: tuple[HypothesisEvidenceLinkRef, ...]
    recurrence_units: tuple[HypothesisRecurrenceUnit, ...]
    recurrence_unit_ids: tuple[str, ...]
    independence_unit_ids: tuple[str, ...]
    source_position_ids: tuple[str, ...]
    source_game_ids: tuple[str, ...]
    measurement_conditions: tuple[MeasurementCondition, ...]
    competing_explanation_review: CompetingExplanationReview
    evidence_summary: HypothesisEvidenceSummary
    status_reasons: tuple[str, ...]
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("hypothesis_assessment_id", self.hypothesis_assessment_id),
            ("fingerprint", self.fingerprint),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.status not in _ASSESSMENT_STATUSES:
            raise ValueError("unknown hypothesis assessment status")
        for values, name in (
            (self.support_link_refs, "support_link_refs"),
            (self.contradiction_link_refs, "contradiction_link_refs"),
            (
                self.successful_counterexample_link_refs,
                "successful_counterexample_link_refs",
            ),
            (self.context_exception_link_refs, "context_exception_link_refs"),
            (self.unclear_link_refs, "unclear_link_refs"),
        ):
            ids = tuple(item.link_id for item in values)
            if len(set(ids)) != len(ids):
                raise ValueError(f"{name} must be unique")
        _require_unique_strings("recurrence_unit_ids", self.recurrence_unit_ids)
        _require_unique_strings("independence_unit_ids", self.independence_unit_ids)
        _require_unique_strings("source_position_ids", self.source_position_ids)
        _require_unique_strings("source_game_ids", self.source_game_ids)
        if tuple(item.recurrence_unit_id for item in self.recurrence_units) != (
            self.recurrence_unit_ids
        ):
            raise ValueError("recurrence units and recurrence_unit_ids must align")
        if any(item not in _MEASUREMENT_CONDITIONS for item in self.measurement_conditions):
            raise ValueError("unknown hypothesis assessment measurement condition")
        if len(set(self.measurement_conditions)) != len(self.measurement_conditions):
            raise ValueError("measurement_conditions must be unique")
        _require_unique_strings("status_reasons", self.status_reasons)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "assessment_policy_ref": self.assessment_policy_ref.to_dict(),
            "status": self.status,
            "support_link_refs": [item.to_dict() for item in self.support_link_refs],
            "contradiction_link_refs": [
                item.to_dict() for item in self.contradiction_link_refs
            ],
            "successful_counterexample_link_refs": [
                item.to_dict() for item in self.successful_counterexample_link_refs
            ],
            "context_exception_link_refs": [
                item.to_dict() for item in self.context_exception_link_refs
            ],
            "unclear_link_refs": [item.to_dict() for item in self.unclear_link_refs],
            "recurrence_units": [item.to_dict() for item in self.recurrence_units],
            "recurrence_unit_ids": list(self.recurrence_unit_ids),
            "independence_unit_ids": list(self.independence_unit_ids),
            "source_position_ids": list(self.source_position_ids),
            "source_game_ids": list(self.source_game_ids),
            "measurement_conditions": list(self.measurement_conditions),
            "competing_explanation_review": self.competing_explanation_review.to_dict(),
            "evidence_summary": self.evidence_summary.to_dict(),
            "status_reasons": list(self.status_reasons),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["hypothesis_assessment_id"] = self.hypothesis_assessment_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisAssessmentRef:
    """Exact reference to one immutable M7C hypothesis assessment."""

    hypothesis_assessment_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    assessment_policy_ref: HypothesisAssessmentPolicyRef
    status: HypothesisAssessmentStatus
    fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("hypothesis_assessment_id", self.hypothesis_assessment_id),
            ("fingerprint", self.fingerprint),
        ):
            _require_nonempty(name, value)
        if self.status not in _ASSESSMENT_STATUSES:
            raise ValueError("unknown hypothesis assessment status")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_assessment_id": self.hypothesis_assessment_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "assessment_policy_ref": self.assessment_policy_ref.to_dict(),
            "status": self.status,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisLifecycleEventRef:
    """Exact reference to one M7B lifecycle event."""

    lifecycle_event_id: str
    fingerprint: str
    kind: Literal["retired", "superseded"]

    def __post_init__(self) -> None:
        _require_nonempty("lifecycle_event_id", self.lifecycle_event_id)
        _require_nonempty("fingerprint", self.fingerprint)
        if self.kind not in {"retired", "superseded"}:
            raise ValueError("unknown lifecycle event reference kind")

    def to_dict(self) -> dict[str, str]:
        return {
            "lifecycle_event_id": self.lifecycle_event_id,
            "fingerprint": self.fingerprint,
            "kind": self.kind,
        }


@dataclass(frozen=True, slots=True)
class HypothesisLedgerEntry:
    """One derived current-state entry; underlying history remains append-only."""

    hypothesis_ref: LearnerHypothesisRef
    current_revision_ref: HypothesisRevisionRef
    latest_assessment_ref: HypothesisAssessmentRef | None
    authority_lifecycle_state: AuthorityLifecycleState
    latest_lifecycle_event_ref: HypothesisLifecycleEventRef | None

    def __post_init__(self) -> None:
        if self.authority_lifecycle_state not in _LIFECYCLE_STATES:
            raise ValueError("unknown authority lifecycle state")
        if self.authority_lifecycle_state == "active":
            if self.latest_lifecycle_event_ref is not None:
                raise ValueError("active entry must not cite a lifecycle event")
        else:
            if self.latest_lifecycle_event_ref is None:
                raise ValueError("terminal lifecycle entry requires a lifecycle event")
            if self.latest_lifecycle_event_ref.kind != self.authority_lifecycle_state:
                raise ValueError("lifecycle state does not match lifecycle event kind")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_ref": self.hypothesis_ref.to_dict(),
            "current_revision_ref": self.current_revision_ref.to_dict(),
            "latest_assessment_ref": (
                None
                if self.latest_assessment_ref is None
                else self.latest_assessment_ref.to_dict()
            ),
            "authority_lifecycle_state": self.authority_lifecycle_state,
            "latest_lifecycle_event_ref": (
                None
                if self.latest_lifecycle_event_ref is None
                else self.latest_lifecycle_event_ref.to_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class HypothesisLedgerSnapshot:
    """Immutable rebuildable participant-specific current ledger view."""

    snapshot_id: str
    fingerprint: str
    participant_id: str
    entries: tuple[HypothesisLedgerEntry, ...]
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("snapshot_id", self.snapshot_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        ids = tuple(item.hypothesis_ref.hypothesis_id for item in self.entries)
        if len(set(ids)) != len(ids):
            raise ValueError("ledger entries must contain unique hypotheses")
        if any(item.hypothesis_ref.participant_id != self.participant_id for item in self.entries):
            raise ValueError("ledger entries must belong to the snapshot participant")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "entries": [item.to_dict() for item in self.entries],
            "created_at": self.created_at,
        }
        if include_identity:
            payload["snapshot_id"] = self.snapshot_id
            payload["fingerprint"] = self.fingerprint
        return payload
