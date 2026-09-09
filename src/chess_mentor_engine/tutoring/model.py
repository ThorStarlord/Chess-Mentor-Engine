"""Immutable records for the bounded M8 evidence-aware tutor session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import PositionContextPacket
from chess_mentor_engine.evidence import EvidenceCaptureSession
from chess_mentor_engine.learning import (
    HypothesisLedgerSnapshot,
    HypothesisRevision,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
    ReasoningDiscrepancyContext,
)

TutorSessionState: TypeAlias = Literal[
    "selected",
    "presented",
    "capturing",
    "frozen",
    "revealed",
    "compared",
    "explained",
    "completed",
]
TutorSessionEventKind: TypeAlias = Literal[
    "SESSION_STARTED",
    "POSITION_PRESENTED",
    "CAPTURE_STAGE_PRESENTED",
    "RESPONSE_CAPTURED",
    "RESPONSE_FROZEN",
    "OBJECTIVE_EVIDENCE_REVEALED",
    "REASONING_COMPARISON_RECORDED",
    "HYPOTHESIS_CONTEXT_ATTACHED",
    "EXPLANATION_RECORDED",
    "SESSION_COMPLETED",
]
TutorExplanationActorKind: TypeAlias = Literal["human", "model", "template"]


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class TutorPositionPresentation:
    """Deterministic M1 position-only presentation shown before objective reveal."""

    presentation_id: str
    fingerprint: str
    tutor_session_id: str
    position_context: PositionContextPacket
    rendered_content: str
    shown_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("presentation_id", self.presentation_id),
            ("fingerprint", self.fingerprint),
            ("tutor_session_id", self.tutor_session_id),
            ("rendered_content", self.rendered_content),
            ("shown_at", self.shown_at),
        ):
            _require_nonempty(name, value)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tutor_session_id": self.tutor_session_id,
            "position_context": self.position_context.to_dict(),
            "rendered_content": self.rendered_content,
            "shown_at": self.shown_at,
        }
        if include_identity:
            payload["presentation_id"] = self.presentation_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class TutorComparison:
    """Exact M6 comparison bundle attached after objective evidence is revealed."""

    comparison_id: str
    fingerprint: str
    tutor_session_id: str
    reasoning_context: ReasoningDiscrepancyContext
    assessment: ReasoningDiscrepancyAssessment
    assertions: tuple[ReasoningDiscrepancyAssertion, ...]
    recorded_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("comparison_id", self.comparison_id),
            ("fingerprint", self.fingerprint),
            ("tutor_session_id", self.tutor_session_id),
            ("recorded_at", self.recorded_at),
        ):
            _require_nonempty(name, value)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tutor_session_id": self.tutor_session_id,
            "reasoning_context": self.reasoning_context.to_dict(),
            "assessment": self.assessment.to_dict(),
            "assertions": [item.to_dict() for item in self.assertions],
            "recorded_at": self.recorded_at,
        }
        if include_identity:
            payload["comparison_id"] = self.comparison_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class TutorHypothesisContext:
    """Complete active-current M7 context exposed to one post-comparison explanation."""

    context_id: str
    fingerprint: str
    tutor_session_id: str
    ledger_snapshot: HypothesisLedgerSnapshot
    active_revisions: tuple[HypothesisRevision, ...]
    attached_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("context_id", self.context_id),
            ("fingerprint", self.fingerprint),
            ("tutor_session_id", self.tutor_session_id),
            ("attached_at", self.attached_at),
        ):
            _require_nonempty(name, value)
        ids = tuple(item.revision_id for item in self.active_revisions)
        if len(set(ids)) != len(ids):
            raise ValueError("active hypothesis revisions must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tutor_session_id": self.tutor_session_id,
            "ledger_snapshot": self.ledger_snapshot.to_dict(),
            "active_revisions": [item.to_dict() for item in self.active_revisions],
            "attached_at": self.attached_at,
        }
        if include_identity:
            payload["context_id"] = self.context_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class TutorExplanationProvenance:
    """Identity of the human/model/template that authored explanation text."""

    actor_kind: TutorExplanationActorKind
    actor_id: str
    actor_version: str
    instruction_fingerprint: str
    run_id: str

    def __post_init__(self) -> None:
        for name, value in (
            ("actor_id", self.actor_id),
            ("actor_version", self.actor_version),
            ("instruction_fingerprint", self.instruction_fingerprint),
            ("run_id", self.run_id),
        ):
            _require_nonempty(name, value)

    def to_dict(self) -> dict[str, str]:
        return {
            "actor_kind": self.actor_kind,
            "actor_id": self.actor_id,
            "actor_version": self.actor_version,
            "instruction_fingerprint": self.instruction_fingerprint,
            "run_id": self.run_id,
        }


@dataclass(frozen=True, slots=True)
class TutorExplanation:
    """Post-reveal session-local explanation with exact evidence provenance."""

    explanation_id: str
    fingerprint: str
    tutor_session_id: str
    comparison_id: str
    comparison_fingerprint: str
    hypothesis_context_id: str | None
    hypothesis_context_fingerprint: str | None
    rendered_content: str
    provenance: TutorExplanationProvenance
    created_at: str
    claim_scope: Literal["session_local_evidence_explanation"] = (
        "session_local_evidence_explanation"
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("explanation_id", self.explanation_id),
            ("fingerprint", self.fingerprint),
            ("tutor_session_id", self.tutor_session_id),
            ("comparison_id", self.comparison_id),
            ("comparison_fingerprint", self.comparison_fingerprint),
            ("rendered_content", self.rendered_content),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if (self.hypothesis_context_id is None) != (
            self.hypothesis_context_fingerprint is None
        ):
            raise ValueError("hypothesis context ID/fingerprint must be paired")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tutor_session_id": self.tutor_session_id,
            "comparison_id": self.comparison_id,
            "comparison_fingerprint": self.comparison_fingerprint,
            "hypothesis_context_id": self.hypothesis_context_id,
            "hypothesis_context_fingerprint": self.hypothesis_context_fingerprint,
            "rendered_content": self.rendered_content,
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["explanation_id"] = self.explanation_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class TutorSessionEvent:
    """Append-only state-transition/event record for deterministic session replay."""

    event_id: str
    sequence: int
    kind: TutorSessionEventKind
    from_state: TutorSessionState
    to_state: TutorSessionState
    occurred_at: str
    artifact_id: str
    artifact_fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("event_id", self.event_id)
        _require_nonempty("occurred_at", self.occurred_at)
        _require_nonempty("artifact_id", self.artifact_id)
        _require_nonempty("artifact_fingerprint", self.artifact_fingerprint)
        if self.sequence < 0:
            raise ValueError("event sequence must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "occurred_at": self.occurred_at,
            "artifact_id": self.artifact_id,
            "artifact_fingerprint": self.artifact_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class TutorSession:
    """Immutable snapshot of one bounded M8 evidence-aware tutor interaction."""

    tutor_session_id: str
    snapshot_fingerprint: str
    workflow_version: str
    state: TutorSessionState
    capture_session: EvidenceCaptureSession
    position_presentation: TutorPositionPresentation | None
    comparison: TutorComparison | None
    hypothesis_context: TutorHypothesisContext | None
    explanation: TutorExplanation | None
    events: tuple[TutorSessionEvent, ...]
    created_at: str
    completed_at: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("tutor_session_id", self.tutor_session_id),
            ("snapshot_fingerprint", self.snapshot_fingerprint),
            ("workflow_version", self.workflow_version),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if not self.events:
            raise ValueError("tutor session requires at least one event")
        sequences = tuple(item.sequence for item in self.events)
        if sequences != tuple(range(len(self.events))):
            raise ValueError("tutor session event sequence must be contiguous")
        for previous, current in zip(self.events, self.events[1:]):
            if previous.to_state != current.from_state:
                raise ValueError("tutor session event state chain is broken")
        if self.events[-1].to_state != self.state:
            raise ValueError("tutor session state must match final event")
        if self.state != "selected" and self.position_presentation is None:
            raise ValueError("position presentation is required after selected state")
        if self.state in {"revealed", "compared", "explained", "completed"}:
            if self.capture_session.objective_reveal is None:
                raise ValueError("revealed-or-later state requires objective reveal")
        if self.state in {"compared", "explained", "completed"}:
            if self.comparison is None:
                raise ValueError("compared-or-later state requires M6 comparison")
        if self.state in {"explained", "completed"} and self.explanation is None:
            raise ValueError("explained-or-later state requires explanation")
        if self.state == "completed":
            if self.completed_at is None:
                raise ValueError("completed state requires completed_at")
        elif self.completed_at is not None:
            raise ValueError("completed_at is only valid for completed sessions")

    def to_dict(self, *, include_snapshot_fingerprint: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tutor_session_id": self.tutor_session_id,
            "workflow_version": self.workflow_version,
            "state": self.state,
            "capture_session": self.capture_session.to_dict(),
            "position_presentation": (
                None
                if self.position_presentation is None
                else self.position_presentation.to_dict()
            ),
            "comparison": (
                None if self.comparison is None else self.comparison.to_dict()
            ),
            "hypothesis_context": (
                None
                if self.hypothesis_context is None
                else self.hypothesis_context.to_dict()
            ),
            "explanation": (
                None if self.explanation is None else self.explanation.to_dict()
            ),
            "events": [item.to_dict() for item in self.events],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
        if include_snapshot_fingerprint:
            payload["snapshot_fingerprint"] = self.snapshot_fingerprint
        return payload
