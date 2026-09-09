"""Immutable M11 longitudinal learner-state evidence and derived projections."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar, Literal, TypeAlias

from chess_mentor_engine.evaluation import OutcomeReference
from chess_mentor_engine.learning import (
    AuthorityLifecycleState,
    HypothesisAssessmentRef,
    HypothesisAssessmentStatus,
    HypothesisRevisionRef,
    LearnerHypothesisRef,
)

LongitudinalActorKind: TypeAlias = Literal["human", "model", "deterministic"]
LongitudinalClaimScope: TypeAlias = Literal[
    "participant_specific_longitudinal_evidence"
]
OutcomeEvidenceKind: TypeAlias = Literal[
    "practice", "near_transfer", "far_transfer", "real_game_transfer"
]
OutcomeEvidenceStatus: TypeAlias = Literal[
    "insufficient", "supported", "not_supported", "mixed", "unclear"
]

OUTCOME_KINDS: tuple[OutcomeEvidenceKind, ...] = (
    "practice",
    "near_transfer",
    "far_transfer",
    "real_game_transfer",
)


class LongitudinalStateError(ValueError):
    """Invalid M11 identity, chronology, provenance, or state relationship."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LongitudinalStateError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LongitudinalStateError("invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LongitudinalStateError("timestamp requires an explicit timezone")
    return parsed


def nonempty(*values: str) -> None:
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise LongitudinalStateError("required text must not be empty")


class ContentRecord:
    """Content-addressed M11 record; identity is always derived from content."""

    __slots__ = ()
    KIND: ClassVar[str]

    def to_dict(self, *, include_identity: bool = True) -> dict:
        payload = json.loads(canonical_json(asdict(self)))
        payload = {"schema_version": "1", "record_kind": self.KIND, **payload}
        if include_identity:
            payload.update(record_id=self.record_id, fingerprint=self.fingerprint)
        return payload

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_identity=False))

    @property
    def record_id(self) -> str:
        return f"{self.KIND}_{self.fingerprint[:20]}"


@dataclass(frozen=True, slots=True)
class LongitudinalReference:
    kind: str
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        nonempty(self.kind, self.ref_id, self.fingerprint)


@dataclass(frozen=True, slots=True)
class LongitudinalProvenance:
    actor_kind: LongitudinalActorKind
    actor_id: str
    actor_version: str
    instruction_fingerprint: str
    run_id: str

    def __post_init__(self) -> None:
        if self.actor_kind not in {"human", "model", "deterministic"}:
            raise LongitudinalStateError("unknown longitudinal actor kind")
        nonempty(
            self.actor_id,
            self.actor_version,
            self.instruction_fingerprint,
            self.run_id,
        )


@dataclass(frozen=True, slots=True)
class OutcomeDimensionState:
    evidence_kind: OutcomeEvidenceKind
    status: OutcomeEvidenceStatus

    def __post_init__(self) -> None:
        if self.evidence_kind not in OUTCOME_KINDS:
            raise LongitudinalStateError("unknown outcome evidence kind")
        if self.status not in {
            "insufficient",
            "supported",
            "not_supported",
            "mixed",
            "unclear",
        }:
            raise LongitudinalStateError("unknown outcome evidence status")


@dataclass(frozen=True, slots=True)
class HypothesisStateEvent(ContentRecord):
    """One append-only observation of an exact current M7 hypothesis state."""

    KIND: ClassVar[str] = "learner_state_event"
    participant_id: str
    event_key: str
    hypothesis_ref: LearnerHypothesisRef
    revision_ref: HypothesisRevisionRef
    m7_snapshot_ref: LongitudinalReference
    m7_assessment_ref: HypothesisAssessmentRef | None
    authority_lifecycle_state: AuthorityLifecycleState
    outcome_plan_ref: OutcomeReference | None
    outcome_assessment_ref: OutcomeReference | None
    outcome_dimensions: tuple[OutcomeDimensionState, ...]
    rationale: str
    provenance: LongitudinalProvenance
    observed_at: str
    recorded_at: str
    claim_scope: LongitudinalClaimScope = "participant_specific_longitudinal_evidence"

    def __post_init__(self) -> None:
        nonempty(self.participant_id, self.event_key, self.rationale)
        if self.hypothesis_ref.participant_id != self.participant_id:
            raise LongitudinalStateError("hypothesis participant mismatch")
        if self.revision_ref.hypothesis_id != self.hypothesis_ref.hypothesis_id:
            raise LongitudinalStateError("revision/hypothesis mismatch")
        if self.m7_snapshot_ref.kind != "hypothesis_ledger_snapshot":
            raise LongitudinalStateError("wrong M7 snapshot reference kind")
        if self.m7_assessment_ref is not None:
            if self.m7_assessment_ref.hypothesis_revision_ref != self.revision_ref:
                raise LongitudinalStateError("M7 assessment/revision mismatch")
        if self.authority_lifecycle_state not in {
            "active",
            "retired",
            "superseded",
        }:
            raise LongitudinalStateError("unknown authority lifecycle state")
        has_plan = self.outcome_plan_ref is not None
        has_assessment = self.outcome_assessment_ref is not None
        if has_plan != has_assessment:
            raise LongitudinalStateError(
                "outcome plan and assessment references must appear together"
            )
        if has_plan:
            if self.outcome_plan_ref.kind != "evaluation_plan":
                raise LongitudinalStateError("wrong M10 plan reference kind")
            if self.outcome_assessment_ref.kind != "outcome_assessment":
                raise LongitudinalStateError("wrong M10 assessment reference kind")
            kinds = tuple(item.evidence_kind for item in self.outcome_dimensions)
            if kinds != OUTCOME_KINDS:
                raise LongitudinalStateError(
                    "outcome dimensions must contain each M10 dimension exactly once"
                )
        elif self.outcome_dimensions:
            raise LongitudinalStateError(
                "outcome dimensions require an M10 assessment reference"
            )
        if self.claim_scope != "participant_specific_longitudinal_evidence":
            raise LongitudinalStateError("unknown longitudinal claim scope")
        if timestamp(self.observed_at) > timestamp(self.recorded_at):
            raise LongitudinalStateError("event cannot be recorded before observation")


@dataclass(frozen=True, slots=True)
class LearnerStateLedger(ContentRecord):
    """Append-only participant ledger; no event rewrites an earlier event."""

    KIND: ClassVar[str] = "learner_state_ledger"
    participant_id: str
    events: tuple[HypothesisStateEvent, ...] = ()

    def __post_init__(self) -> None:
        nonempty(self.participant_id)
        if type(self.events) is not tuple:
            raise LongitudinalStateError("ledger events must be an immutable tuple")
        if any(item.participant_id != self.participant_id for item in self.events):
            raise LongitudinalStateError("ledger participant mismatch")
        keys = tuple(item.event_key for item in self.events)
        if len(set(keys)) != len(keys):
            raise LongitudinalStateError("event keys must be unique")
        ordered = tuple(
            sorted(self.events, key=lambda item: timestamp(item.recorded_at))
        )
        if ordered != self.events:
            raise LongitudinalStateError("ledger events must be append-chronological")

        prior: dict[str, HypothesisStateEvent] = {}
        for event in self.events:
            hypothesis_id = event.hypothesis_ref.hypothesis_id
            previous = prior.get(hypothesis_id)
            if previous is not None:
                if (
                    event.revision_ref.revision_number
                    < previous.revision_ref.revision_number
                ):
                    raise LongitudinalStateError("hypothesis revision regressed")
                if (
                    event.revision_ref.revision_number
                    == previous.revision_ref.revision_number
                    and event.revision_ref != previous.revision_ref
                ):
                    raise LongitudinalStateError(
                        "same revision number changed immutable identity"
                    )
                if previous.authority_lifecycle_state != "active":
                    if event.authority_lifecycle_state == "active":
                        raise LongitudinalStateError(
                            "terminal hypothesis lifecycle cannot be resurrected"
                        )
                    if (
                        event.authority_lifecycle_state
                        != previous.authority_lifecycle_state
                    ):
                        raise LongitudinalStateError(
                            "terminal hypothesis lifecycle cannot change kind"
                        )
                    if event.revision_ref != previous.revision_ref:
                        raise LongitudinalStateError(
                            "terminal hypothesis cannot advance revisions"
                        )
            prior[hypothesis_id] = event


@dataclass(frozen=True, slots=True)
class HypothesisTrajectory:
    hypothesis_ref: LearnerHypothesisRef
    current_revision_ref: HypothesisRevisionRef
    authority_lifecycle_state: AuthorityLifecycleState
    latest_m7_assessment_ref: HypothesisAssessmentRef | None
    latest_m7_status: HypothesisAssessmentStatus | None
    current_outcome_assessment_ref: OutcomeReference | None
    current_outcome_dimensions: tuple[OutcomeDimensionState, ...]
    event_refs: tuple[LongitudinalReference, ...]

    def __post_init__(self) -> None:
        if not self.event_refs:
            raise LongitudinalStateError("trajectory requires at least one event")
        if self.latest_m7_assessment_ref is None:
            if self.latest_m7_status is not None:
                raise LongitudinalStateError(
                    "M7 status requires an exact assessment reference"
                )
        elif self.latest_m7_status != self.latest_m7_assessment_ref.status:
            raise LongitudinalStateError("M7 status/reference mismatch")
        if self.current_outcome_assessment_ref is None:
            if self.current_outcome_dimensions:
                raise LongitudinalStateError(
                    "current outcome dimensions require an assessment"
                )
        elif self.current_outcome_assessment_ref.kind != "outcome_assessment":
            raise LongitudinalStateError("wrong current outcome reference kind")


@dataclass(frozen=True, slots=True)
class LearnerStateSnapshot(ContentRecord):
    """Derived current longitudinal view; rebuildable from the append-only ledger."""

    KIND: ClassVar[str] = "learner_state_snapshot"
    participant_id: str
    ledger_ref: LongitudinalReference
    trajectories: tuple[HypothesisTrajectory, ...]
    created_at: str
    claim_scope: LongitudinalClaimScope = "participant_specific_longitudinal_evidence"
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"

    def __post_init__(self) -> None:
        nonempty(self.participant_id)
        if self.ledger_ref.kind != "learner_state_ledger":
            raise LongitudinalStateError("wrong learner-state ledger reference kind")
        ids = tuple(item.hypothesis_ref.hypothesis_id for item in self.trajectories)
        if len(set(ids)) != len(ids):
            raise LongitudinalStateError("snapshot trajectories must be unique")
        if any(
            item.hypothesis_ref.participant_id != self.participant_id
            for item in self.trajectories
        ):
            raise LongitudinalStateError("snapshot participant mismatch")
        if self.claim_scope != "participant_specific_longitudinal_evidence":
            raise LongitudinalStateError("unknown longitudinal claim scope")
        if self.causal_effect != "not_established" or self.mastery != "not_established":
            raise LongitudinalStateError("M11 cannot establish causality or mastery")
        timestamp(self.created_at)
