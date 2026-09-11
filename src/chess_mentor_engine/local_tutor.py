"""V1 local tutor vertical-slice composition over qualified CME contracts.

This module adds no chess, learner-inference, intervention-selection, outcome, or
mastery authority. It composes the already-qualified M45 mentor queue and M46 tutor
action proposal around an exact M8 session when one exists.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learner_intelligence import (
    EvidenceSynthesisReference,
    LearnerProgressView,
    MentorQueue,
    MentorQueueBatchScope,
    MentorQueueItem,
    MentorQueuePolicy,
    TransferRetestPlan,
    bind_mentor_queue_batch_scope,
    build_mentor_queue,
)
from chess_mentor_engine.selection import DiagnosticCandidateBatch
from chess_mentor_engine.tutoring import (
    AdaptiveTutorPolicy,
    AdaptiveTutorProposal,
    TutorSession,
    build_adaptive_tutor_proposal,
)

LOCAL_TUTOR_WORKFLOW_SCHEMA_VERSION = "v1.local-tutor-workflow.v1"
LocalTutorStage = Literal[
    "review_ready",
    "baseline_capture",
    "adaptive_tutoring",
    "reflection",
    "blocked",
    "complete",
]


class LocalTutorWorkflowError(ValueError):
    """The V1 local workflow cannot preserve an exact qualified source boundary."""


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _timestamp(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LocalTutorWorkflowError(f"{name} must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LocalTutorWorkflowError(
            f"{name} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LocalTutorWorkflowError(f"{name} must include a timezone offset")


def _session_ref(session: TutorSession) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "tutor_session_snapshot",
        session.tutor_session_id,
        session.snapshot_fingerprint,
    )


def _stage_for(
    session: TutorSession,
    proposal: AdaptiveTutorProposal,
) -> LocalTutorStage:
    if proposal.action == "CONTINUE_BASELINE_CAPTURE":
        return "baseline_capture"
    if proposal.action == "ASK_REFLECTION":
        return "reflection"
    if proposal.action == "NO_FURTHER_ACTION":
        return "complete" if session.state == "completed" else "blocked"
    return "adaptive_tutoring"


def _resolve_hypothesis_id(
    *,
    view: LearnerProgressView,
    item: MentorQueueItem,
    requested_hypothesis_id: str | None,
) -> str:
    known = {hypothesis.hypothesis_id for hypothesis in view.hypotheses}
    if requested_hypothesis_id is not None:
        if requested_hypothesis_id not in known:
            raise LocalTutorWorkflowError(
                "requested hypothesis_id is not present in the exact M44 view"
            )
        if (
            item.hypothesis_ids
            and requested_hypothesis_id not in item.hypothesis_ids
        ):
            raise LocalTutorWorkflowError(
                "requested hypothesis_id is not linked to the exact M45 queue item"
            )
        # An explicit operator choice may add tutoring context to an objective-only
        # review item, but it does not rewrite M45 learner relevance.
        return requested_hypothesis_id

    if len(item.hypothesis_ids) == 1:
        hypothesis_id = item.hypothesis_ids[0]
        if hypothesis_id not in known:
            raise LocalTutorWorkflowError(
                "M45 queue item references an unknown M44 hypothesis"
            )
        return hypothesis_id
    if len(item.hypothesis_ids) > 1:
        raise LocalTutorWorkflowError(
            "M45 queue item links multiple hypotheses; supply hypothesis_id explicitly"
        )
    raise LocalTutorWorkflowError(
        "M45 queue item has no learner-hypothesis link; supply hypothesis_id explicitly"
    )


def _matching_transfer_plan(
    *,
    session: TutorSession,
    hypothesis_id: str,
    transfer_plans: tuple[TransferRetestPlan, ...],
) -> TransferRetestPlan | None:
    context = session.capture_session.context
    matching = tuple(
        plan
        for plan in transfer_plans
        if plan.hypothesis_id == hypothesis_id
        and plan.selected_candidate is not None
        and plan.selected_candidate.position.game_id == context.game_id
        and plan.selected_candidate.position.position_id == context.position_id
    )
    if len(matching) > 1:
        raise LocalTutorWorkflowError(
            "multiple exact M42 transfer plans match the active tutor position"
        )
    return matching[0] if matching else None


@dataclass(frozen=True, slots=True)
class LocalTutorWorkflowSnapshot:
    workflow_id: str
    fingerprint: str
    participant_id: str
    batch_scope: MentorQueueBatchScope
    mentor_queue: MentorQueue
    active_item: MentorQueueItem
    tutor_session_ref: EvidenceSynthesisReference | None
    adaptive_tutor_proposal: AdaptiveTutorProposal | None
    stage: LocalTutorStage
    next_action: str
    created_at: str
    orchestration_authority: Literal["composition_only"] = "composition_only"
    learner_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = LOCAL_TUTOR_WORKFLOW_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _timestamp("created_at", self.created_at)
        if self.schema_version != LOCAL_TUTOR_WORKFLOW_SCHEMA_VERSION:
            raise LocalTutorWorkflowError("unsupported local-tutor workflow schema")
        if self.batch_scope.participant_id != self.participant_id:
            raise LocalTutorWorkflowError("batch scope participant mismatch")
        if self.mentor_queue.participant_id != self.participant_id:
            raise LocalTutorWorkflowError("mentor queue participant mismatch")
        if self.active_item not in self.mentor_queue.items:
            raise LocalTutorWorkflowError("active item is not in the exact M45 queue")
        if self.stage == "review_ready":
            if (
                self.tutor_session_ref is not None
                or self.adaptive_tutor_proposal is not None
                or self.next_action != "START_SELECTED_REVIEW"
            ):
                raise LocalTutorWorkflowError("invalid review-ready workflow state")
        elif (
            self.tutor_session_ref is None
            or self.adaptive_tutor_proposal is None
            or self.next_action != self.adaptive_tutor_proposal.action
        ):
            raise LocalTutorWorkflowError("invalid active tutor workflow state")
        if self.orchestration_authority != "composition_only":
            raise LocalTutorWorkflowError(
                "local workflow cannot grant execution authority"
            )
        if (
            self.learner_effect != "not_established"
            or self.mastery != "not_established"
        ):
            raise LocalTutorWorkflowError(
                "local workflow cannot establish learner effect or mastery"
            )
        expected = _digest(self.identity_payload())
        if self.fingerprint != expected:
            raise LocalTutorWorkflowError("local-tutor workflow fingerprint mismatch")
        if self.workflow_id != f"local_tutor_workflow_{expected[:20]}":
            raise LocalTutorWorkflowError("local-tutor workflow identity mismatch")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "batch_scope": self.batch_scope.to_dict(),
            "mentor_queue": self.mentor_queue.to_dict(),
            "active_item": self.active_item.to_dict(),
            "tutor_session_ref": (
                None
                if self.tutor_session_ref is None
                else self.tutor_session_ref.to_dict()
            ),
            "adaptive_tutor_proposal": (
                None
                if self.adaptive_tutor_proposal is None
                else self.adaptive_tutor_proposal.to_dict()
            ),
            "stage": self.stage,
            "next_action": self.next_action,
            "created_at": self.created_at,
            "orchestration_authority": self.orchestration_authority,
            "learner_effect": self.learner_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_local_tutor_workflow(
    *,
    participant_id: str,
    diagnostic_batch: DiagnosticCandidateBatch,
    batch_source_refs: tuple[EvidenceSynthesisReference, ...],
    learner_progress_view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
    queue_policy: MentorQueuePolicy,
    adaptive_tutor_policy: AdaptiveTutorPolicy,
    created_at: str,
    tutor_session: TutorSession | None = None,
    hypothesis_id: str | None = None,
) -> LocalTutorWorkflowSnapshot:
    """Compose the current V1 local-review state from exact qualified artifacts."""
    _timestamp("created_at", created_at)
    if learner_progress_view.participant_id != participant_id:
        raise LocalTutorWorkflowError("M44 learner-progress participant mismatch")

    batch_scope = bind_mentor_queue_batch_scope(
        participant_id=participant_id,
        diagnostic_batch=diagnostic_batch,
        source_refs=batch_source_refs,
    )
    queue = build_mentor_queue(
        diagnostic_batch=diagnostic_batch,
        batch_scope=batch_scope,
        learner_progress_view=learner_progress_view,
        transfer_plans=transfer_plans,
        policy=queue_policy,
        created_at=created_at,
    )
    if not queue.items:
        raise LocalTutorWorkflowError("M45 produced no reviewable queue item")

    if tutor_session is None:
        item = queue.items[0]
        proposal = None
        session_reference = None
        stage: LocalTutorStage = "review_ready"
        next_action = "START_SELECTED_REVIEW"
    else:
        context = tutor_session.capture_session.context
        if context.participant_id != participant_id:
            raise LocalTutorWorkflowError("M8 tutor-session participant mismatch")
        matching_items = tuple(
            item
            for item in queue.items
            if item.game_id == context.game_id
            and item.position_id == context.position_id
        )
        if len(matching_items) != 1:
            raise LocalTutorWorkflowError(
                "active M8 tutor position is not present exactly once in the M45 queue"
            )
        item = matching_items[0]
        resolved_hypothesis_id = _resolve_hypothesis_id(
            view=learner_progress_view,
            item=item,
            requested_hypothesis_id=hypothesis_id,
        )
        proposal = build_adaptive_tutor_proposal(
            tutor_session=tutor_session,
            learner_progress_view=learner_progress_view,
            hypothesis_id=resolved_hypothesis_id,
            mentor_queue=queue,
            mentor_queue_item=item,
            transfer_plan=_matching_transfer_plan(
                session=tutor_session,
                hypothesis_id=resolved_hypothesis_id,
                transfer_plans=transfer_plans,
            ),
            policy=adaptive_tutor_policy,
            created_at=created_at,
        )
        session_reference = _session_ref(tutor_session)
        stage = _stage_for(tutor_session, proposal)
        next_action = proposal.action

    payload = {
        "schema_version": LOCAL_TUTOR_WORKFLOW_SCHEMA_VERSION,
        "participant_id": participant_id,
        "batch_scope": batch_scope.to_dict(),
        "mentor_queue": queue.to_dict(),
        "active_item": item.to_dict(),
        "tutor_session_ref": (
            None if session_reference is None else session_reference.to_dict()
        ),
        "adaptive_tutor_proposal": (
            None if proposal is None else proposal.to_dict()
        ),
        "stage": stage,
        "next_action": next_action,
        "created_at": created_at,
        "orchestration_authority": "composition_only",
        "learner_effect": "not_established",
        "mastery": "not_established",
    }
    fingerprint = _digest(payload)
    return LocalTutorWorkflowSnapshot(
        workflow_id=f"local_tutor_workflow_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=participant_id,
        batch_scope=batch_scope,
        mentor_queue=queue,
        active_item=item,
        tutor_session_ref=session_reference,
        adaptive_tutor_proposal=proposal,
        stage=stage,
        next_action=next_action,
        created_at=created_at,
    )


def validate_local_tutor_workflow(
    snapshot: LocalTutorWorkflowSnapshot,
    *,
    diagnostic_batch: DiagnosticCandidateBatch,
    batch_source_refs: tuple[EvidenceSynthesisReference, ...],
    learner_progress_view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
    queue_policy: MentorQueuePolicy,
    adaptive_tutor_policy: AdaptiveTutorPolicy,
    tutor_session: TutorSession | None = None,
    hypothesis_id: str | None = None,
) -> None:
    """Rebuild and require exact equality for one V1 workflow snapshot."""
    expected = build_local_tutor_workflow(
        participant_id=snapshot.participant_id,
        diagnostic_batch=diagnostic_batch,
        batch_source_refs=batch_source_refs,
        learner_progress_view=learner_progress_view,
        transfer_plans=transfer_plans,
        queue_policy=queue_policy,
        adaptive_tutor_policy=adaptive_tutor_policy,
        created_at=snapshot.created_at,
        tutor_session=tutor_session,
        hypothesis_id=hypothesis_id,
    )
    if expected != snapshot:
        raise LocalTutorWorkflowError("local-tutor workflow snapshot mismatch")
