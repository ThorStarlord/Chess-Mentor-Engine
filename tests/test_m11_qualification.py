"""M11 qualification over the native M7 -> M9 -> M10 evidence chain."""

from __future__ import annotations

from dataclasses import replace

import pytest
from test_m10_qualification import capture, make_plan, selected
from test_m9_qualification import _revision, _snapshot
from test_outcome_evidence import author, source, time_at

from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.evaluation import (
    OutcomeLedger,
    assess_outcome_evidence,
    record_outcome_observation,
    record_practice_completion,
    reference,
)
from chess_mentor_engine.longitudinal import (
    LongitudinalProvenance,
    LongitudinalStateError,
    project_learner_state,
    record_hypothesis_state,
    start_learner_state,
)
from chess_mentor_engine.longitudinal.model import fingerprint


def recorder() -> LongitudinalProvenance:
    return LongitudinalProvenance(
        actor_kind="deterministic",
        actor_id="m11-projector",
        actor_version="1",
        instruction_fingerprint="m11-contract-v1",
        run_id="m11-run-1",
    )


def outcome_for_current_revision():
    selection, intervention = selected()
    evaluation_plan = make_plan(selection, intervention)
    game = ingest_pgn('[Result "*"]\n\n1. e4 e5 2. Nf3 Nc6 *').games[0]
    ledger = OutcomeLedger(evaluation_plan)
    ledger, practice = capture(
        ledger, game.positions[0], "practice", 802, "m11-practice"
    )
    ledger, completion = record_practice_completion(
        ledger,
        attempt_refs=(reference(practice),),
        provenance=author(),
        completed_at=time_at(803),
    )
    for index in (1, 2):
        ledger, attempt = capture(
            ledger,
            game.positions[index],
            "near_transfer",
            810 + index,
            f"m11-probe-{index}",
        )
        ledger, _ = record_outcome_observation(
            ledger,
            attempt_ref=reference(attempt),
            result="criterion_met",
            evidence_refs=(source("objective_evidence", f"m11-score-{index}"),),
            rationale="Scored under the predeclared M10 rubric.",
            provenance=author("m11-coder"),
            recorded_at=time_at(815 + index),
        )
    assessment = assess_outcome_evidence(
        ledger,
        completion_ref=reference(completion),
        created_at=time_at(820),
    )
    return evaluation_plan, assessment


def record_current(
    state,
    *,
    revision=None,
    snapshot=None,
    key="state-1",
    observed=900,
    plan=None,
    assessment=None,
    rationale="Record the exact current evidence state without promotion.",
):
    revision = revision or _revision()
    snapshot = snapshot or _snapshot(revision)
    return record_hypothesis_state(
        state,
        event_key=key,
        ledger_snapshot=snapshot,
        hypothesis_revision=revision,
        rationale=rationale,
        provenance=recorder(),
        observed_at=time_at(observed),
        recorded_at=time_at(observed + 1),
        evaluation_plan=plan,
        outcome_assessment=assessment,
    )


def test_m11_projects_exact_m7_and_m10_history_without_mastery() -> None:
    revision = _revision()
    snapshot = _snapshot(revision)
    plan, assessment = outcome_for_current_revision()
    state = start_learner_state(participant_id="P01")
    state, event = record_current(
        state,
        revision=revision,
        snapshot=snapshot,
        plan=plan,
        assessment=assessment,
    )

    current = project_learner_state(state, created_at=time_at(902))
    assert len(current.trajectories) == 1
    trajectory = current.trajectories[0]
    assert trajectory.current_revision_ref.revision_id == revision.revision_id
    assert trajectory.latest_m7_status == "supported_recurrence"
    assert trajectory.current_outcome_assessment_ref.ref_id == assessment.record_id
    statuses = {
        item.evidence_kind: item.status
        for item in trajectory.current_outcome_dimensions
    }
    assert statuses["near_transfer"] == "supported"
    assert current.mastery == current.causal_effect == "not_established"
    assert event.m7_snapshot_ref.ref_id == snapshot.snapshot_id
    assert state.events == (event,)


def test_new_revision_does_not_inherit_old_revision_outcome_evidence() -> None:
    first = _revision()
    plan, assessment = outcome_for_current_revision()
    state = start_learner_state(participant_id="P01")
    state, _ = record_current(
        state,
        revision=first,
        snapshot=_snapshot(first),
        plan=plan,
        assessment=assessment,
    )
    second = _revision(
        parent=first,
        statement="Alternatives are inconsistently reported in the bounded context.",
    )
    state, _ = record_current(
        state,
        revision=second,
        snapshot=_snapshot(second, status="candidate_recurrence"),
        key="state-2",
        observed=910,
    )

    current = project_learner_state(state, created_at=time_at(912))
    trajectory = current.trajectories[0]
    assert trajectory.current_revision_ref.revision_number == 2
    assert trajectory.latest_m7_status == "candidate_recurrence"
    assert trajectory.current_outcome_assessment_ref is None
    assert trajectory.current_outcome_dimensions == ()
    assert len(trajectory.event_refs) == 2


def test_identical_event_key_is_idempotent_but_conflict_is_rejected() -> None:
    state = start_learner_state(participant_id="P01")
    state, event = record_current(state)
    same, same_event = record_current(state)
    assert same == state
    assert same_event == event

    with pytest.raises(LongitudinalStateError, match="event key"):
        record_current(state, rationale="Conflicting content for the same occurrence.")


@pytest.mark.parametrize(
    "case",
    [
        "snapshot_fingerprint",
        "participant",
        "stale_revision",
        "m10_revision",
        "m10_plan",
        "m10_chronology",
    ],
)
def test_m11_rejects_cross_layer_identity_and_chronology_failures(case) -> None:
    first = _revision()
    snapshot = _snapshot(first)
    state = start_learner_state(participant_id="P01")
    plan, assessment = outcome_for_current_revision()
    revision = first
    observed = 900

    if case == "snapshot_fingerprint":
        snapshot = replace(snapshot, fingerprint="tampered")
    elif case == "participant":
        state = start_learner_state(participant_id="P02")
    elif case == "stale_revision":
        revision = _revision(parent=first, statement="A later bounded revision.")
    elif case == "m10_revision":
        revision = _revision(parent=first, statement="A later bounded revision.")
        snapshot = _snapshot(revision)
    elif case == "m10_plan":
        plan = replace(plan, rationale="A different content-addressed plan.")
    else:
        observed = 819

    with pytest.raises(LongitudinalStateError):
        record_current(
            state,
            revision=revision,
            snapshot=snapshot,
            plan=plan,
            assessment=assessment,
            observed=observed,
        )


def test_m11_rejects_revision_regression_and_lifecycle_resurrection() -> None:
    first = _revision()
    second = _revision(parent=first, statement="A later bounded revision.")
    state = start_learner_state(participant_id="P01")
    state, _ = record_current(
        state,
        revision=second,
        snapshot=_snapshot(second),
        key="second",
        observed=900,
    )
    with pytest.raises(LongitudinalStateError, match="revision regressed"):
        record_current(
            state,
            revision=first,
            snapshot=_snapshot(first),
            key="first-late",
            observed=910,
        )

    terminal = start_learner_state(participant_id="P01")
    terminal, _ = record_current(
        terminal,
        revision=first,
        snapshot=_snapshot(first, lifecycle="retired"),
        key="retired",
        observed=900,
    )
    with pytest.raises(LongitudinalStateError, match="cannot be resurrected"):
        record_current(
            terminal,
            revision=first,
            snapshot=_snapshot(first),
            key="active-again",
            observed=910,
        )


def test_projection_is_deterministic_and_content_addressed() -> None:
    state = start_learner_state(participant_id="P01")
    state, _ = record_current(state)
    first = project_learner_state(state, created_at=time_at(902))
    second = project_learner_state(state, created_at=time_at(902))
    assert first == second
    assert first.fingerprint == fingerprint(first.to_dict(include_identity=False))
    assert first.record_id.startswith("learner_state_snapshot_")


def test_public_exports_are_importable() -> None:
    import chess_mentor_engine.longitudinal as public

    for name in public.__all__:
        assert getattr(public, name) is not None
