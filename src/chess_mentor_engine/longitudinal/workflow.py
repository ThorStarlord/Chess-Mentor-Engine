"""Validated M11 append and deterministic projection operations."""

from __future__ import annotations

from chess_mentor_engine.evaluation import (
    EvaluationPlan,
    OutcomeAssessment,
    reference as outcome_reference,
)
from chess_mentor_engine.learning import HypothesisLedgerSnapshot, HypothesisRevision

from .model import (
    HypothesisStateEvent,
    HypothesisTrajectory,
    LearnerStateLedger,
    LearnerStateSnapshot,
    LongitudinalProvenance,
    LongitudinalReference,
    LongitudinalStateError,
    OUTCOME_KINDS,
    OutcomeDimensionState,
    fingerprint,
    timestamp,
)


def state_reference(record) -> LongitudinalReference:
    """Return an exact M11 content reference for one native M11 record."""
    return LongitudinalReference(record.KIND, record.record_id, record.fingerprint)


def _validate_revision(revision: HypothesisRevision) -> None:
    expected = fingerprint(revision.to_dict(include_identity=False))
    if revision.fingerprint != expected:
        raise LongitudinalStateError("M7 hypothesis revision fingerprint mismatch")
    if revision.revision_id != f"hypothesis_revision_{expected[:20]}":
        raise LongitudinalStateError("M7 hypothesis revision identity mismatch")


def _revision_ref(revision: HypothesisRevision):
    from chess_mentor_engine.learning import HypothesisRevisionRef

    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _validate_snapshot(snapshot: HypothesisLedgerSnapshot) -> None:
    expected = fingerprint(snapshot.to_dict(include_identity=False))
    if snapshot.fingerprint != expected:
        raise LongitudinalStateError("M7 ledger snapshot fingerprint mismatch")
    if snapshot.snapshot_id != f"hypothesis_ledger_snapshot_{expected[:20]}":
        raise LongitudinalStateError("M7 ledger snapshot identity mismatch")


def _snapshot_ref(snapshot: HypothesisLedgerSnapshot) -> LongitudinalReference:
    return LongitudinalReference(
        "hypothesis_ledger_snapshot", snapshot.snapshot_id, snapshot.fingerprint
    )


def _entry_for_revision(
    snapshot: HypothesisLedgerSnapshot,
    revision: HypothesisRevision,
):
    matches = tuple(
        item
        for item in snapshot.entries
        if item.hypothesis_ref.hypothesis_id == revision.hypothesis_id
    )
    if len(matches) != 1:
        raise LongitudinalStateError(
            "M7 snapshot must contain exactly one requested hypothesis"
        )
    entry = matches[0]
    expected_ref = _revision_ref(revision)
    if entry.current_revision_ref != expected_ref:
        raise LongitudinalStateError("M7 snapshot is not current for revision")
    if entry.latest_assessment_ref is not None:
        if entry.latest_assessment_ref.hypothesis_revision_ref != expected_ref:
            raise LongitudinalStateError("M7 assessment is stale for current revision")
    return entry


def _validate_outcome_binding(
    *,
    participant_id: str,
    revision: HypothesisRevision,
    plan: EvaluationPlan,
    assessment: OutcomeAssessment,
    observed_at: str,
) -> tuple[OutcomeDimensionState, ...]:
    if (
        plan.participant_id != participant_id
        or assessment.participant_id != participant_id
    ):
        raise LongitudinalStateError("M10 participant mismatch")
    expected_revision = _revision_ref(revision)
    if (
        plan.hypothesis_revision_ref.kind != "hypothesis_revision"
        or plan.hypothesis_revision_ref.ref_id != expected_revision.revision_id
        or plan.hypothesis_revision_ref.fingerprint != expected_revision.fingerprint
    ):
        raise LongitudinalStateError("M10 plan is bound to a different M7 revision")
    if assessment.plan_ref != outcome_reference(plan):
        raise LongitudinalStateError("M10 assessment/plan identity mismatch")
    if assessment.policy_ref != outcome_reference(plan.policy):
        raise LongitudinalStateError("M10 assessment/policy identity mismatch")
    if (
        assessment.causal_effect != "not_established"
        or assessment.mastery != "not_established"
    ):
        raise LongitudinalStateError("M10 claim ceiling violated")
    if timestamp(assessment.created_at) > timestamp(observed_at):
        raise LongitudinalStateError("M11 event predates its M10 assessment")

    by_kind = {item.evidence_kind: item for item in assessment.dimensions}
    if set(by_kind) != set(OUTCOME_KINDS) or len(by_kind) != len(assessment.dimensions):
        raise LongitudinalStateError(
            "M10 assessment must contain each outcome dimension exactly once"
        )
    return tuple(
        OutcomeDimensionState(kind, by_kind[kind].status) for kind in OUTCOME_KINDS
    )


def start_learner_state(*, participant_id: str) -> LearnerStateLedger:
    """Start an empty append-only M11 ledger for one participant."""
    try:
        return LearnerStateLedger(participant_id=participant_id)
    except LongitudinalStateError:
        raise
    except ValueError as exc:
        raise LongitudinalStateError(str(exc)) from exc


def record_hypothesis_state(
    ledger: LearnerStateLedger,
    *,
    event_key: str,
    ledger_snapshot: HypothesisLedgerSnapshot,
    hypothesis_revision: HypothesisRevision,
    rationale: str,
    provenance: LongitudinalProvenance,
    observed_at: str,
    recorded_at: str,
    evaluation_plan: EvaluationPlan | None = None,
    outcome_assessment: OutcomeAssessment | None = None,
) -> tuple[LearnerStateLedger, HypothesisStateEvent]:
    """Append one exact M7 state, optionally with exact M10 evidence.

    This operation records evidence only. It never revises M7, selects training,
    or promotes M10 evidence to mastery/causal improvement.
    """
    _validate_revision(hypothesis_revision)
    _validate_snapshot(ledger_snapshot)
    if ledger_snapshot.participant_id != ledger.participant_id:
        raise LongitudinalStateError("M7 ledger participant mismatch")
    if timestamp(ledger_snapshot.created_at) > timestamp(observed_at):
        raise LongitudinalStateError("M11 event predates its M7 snapshot")
    if timestamp(observed_at) > timestamp(recorded_at):
        raise LongitudinalStateError("event cannot be recorded before observation")

    entry = _entry_for_revision(ledger_snapshot, hypothesis_revision)
    if entry.hypothesis_ref.participant_id != ledger.participant_id:
        raise LongitudinalStateError("M7 hypothesis participant mismatch")

    if (evaluation_plan is None) != (outcome_assessment is None):
        raise LongitudinalStateError(
            "M10 plan and assessment must be supplied together"
        )
    dimensions: tuple[OutcomeDimensionState, ...] = ()
    plan_ref = None
    assessment_ref = None
    if evaluation_plan is not None and outcome_assessment is not None:
        dimensions = _validate_outcome_binding(
            participant_id=ledger.participant_id,
            revision=hypothesis_revision,
            plan=evaluation_plan,
            assessment=outcome_assessment,
            observed_at=observed_at,
        )
        plan_ref = outcome_reference(evaluation_plan)
        assessment_ref = outcome_reference(outcome_assessment)

    event = HypothesisStateEvent(
        participant_id=ledger.participant_id,
        event_key=event_key,
        hypothesis_ref=entry.hypothesis_ref,
        revision_ref=entry.current_revision_ref,
        m7_snapshot_ref=_snapshot_ref(ledger_snapshot),
        m7_assessment_ref=entry.latest_assessment_ref,
        authority_lifecycle_state=entry.authority_lifecycle_state,
        outcome_plan_ref=plan_ref,
        outcome_assessment_ref=assessment_ref,
        outcome_dimensions=dimensions,
        rationale=rationale,
        provenance=provenance,
        observed_at=observed_at,
        recorded_at=recorded_at,
    )

    for previous in ledger.events:
        if previous.event_key != event_key:
            continue
        if previous.fingerprint == event.fingerprint:
            return ledger, previous
        raise LongitudinalStateError("event key already exists with different content")

    try:
        updated = LearnerStateLedger(
            participant_id=ledger.participant_id,
            events=ledger.events + (event,),
        )
    except LongitudinalStateError:
        raise
    except ValueError as exc:
        raise LongitudinalStateError(str(exc)) from exc
    return updated, event


def project_learner_state(
    ledger: LearnerStateLedger,
    *,
    created_at: str,
) -> LearnerStateSnapshot:
    """Rebuild a current participant view from immutable M11 events."""
    created = timestamp(created_at)
    if ledger.events and created < timestamp(ledger.events[-1].recorded_at):
        raise LongitudinalStateError("snapshot cannot predate ledger history")

    hypothesis_ids = sorted(
        {item.hypothesis_ref.hypothesis_id for item in ledger.events}
    )
    trajectories: list[HypothesisTrajectory] = []
    for hypothesis_id in hypothesis_ids:
        history = tuple(
            item
            for item in ledger.events
            if item.hypothesis_ref.hypothesis_id == hypothesis_id
        )
        latest = history[-1]
        current_revision = latest.revision_ref
        current_outcome = next(
            (
                item
                for item in reversed(history)
                if item.revision_ref == current_revision
                and item.outcome_assessment_ref is not None
            ),
            None,
        )
        trajectories.append(
            HypothesisTrajectory(
                hypothesis_ref=latest.hypothesis_ref,
                current_revision_ref=current_revision,
                authority_lifecycle_state=latest.authority_lifecycle_state,
                latest_m7_assessment_ref=latest.m7_assessment_ref,
                latest_m7_status=(
                    None
                    if latest.m7_assessment_ref is None
                    else latest.m7_assessment_ref.status
                ),
                current_outcome_assessment_ref=(
                    None
                    if current_outcome is None
                    else current_outcome.outcome_assessment_ref
                ),
                current_outcome_dimensions=(
                    ()
                    if current_outcome is None
                    else current_outcome.outcome_dimensions
                ),
                event_refs=tuple(state_reference(item) for item in history),
            )
        )

    return LearnerStateSnapshot(
        participant_id=ledger.participant_id,
        ledger_ref=state_reference(ledger),
        trajectories=tuple(trajectories),
        created_at=created_at,
    )
