"""M10 unit contract tests. Upstream refs here are explicit fixture identities."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from chess_mentor_engine.evaluation import (
    EvaluationAttempt,
    EvaluationPlan,
    ExerciseBinding,
    OutcomeEvidenceError,
    OutcomeLedger,
    OutcomePolicy,
    OutcomePosition,
    OutcomeProvenance,
    OutcomeReference,
    append_evaluation_attempt,
    assess_outcome_evidence,
    record_outcome_observation,
    record_practice_completion,
    reference,
    validate_outcome_ledger,
)
from chess_mentor_engine.evaluation.model import fingerprint

FENS = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1",
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1",
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1",
    "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR b KQkq - 1 1",
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "rnbqkbnr/pppppppp/8/8/8/6P1/PPPPPP1P/RNBQKBNR b KQkq - 0 1",
)


def time_at(minutes: float) -> str:
    value = datetime(2026, 9, 9, tzinfo=timezone.utc) + timedelta(minutes=minutes)
    return value.isoformat()


def source(kind: str, key: str) -> OutcomeReference:
    return OutcomeReference(kind, key, fingerprint({"fixture": key, "kind": kind}))


def author(key: str = "author") -> OutcomeProvenance:
    return OutcomeProvenance(
        "human", key, "1", source("outcome_rubric", "rubric").fingerprint, "run-1"
    )


def policy(**updates) -> OutcomePolicy:
    values = dict(
        policy_key="resource-check", version="1",
        success_criterion="List the legal forcing reply.",
        scoring_rubric_ref=source("outcome_rubric", "rubric"),
        near_transfer_context="Fresh positions in the practiced context.",
        far_transfer_context="Fresh positions in a different declared context.",
        real_game_context="A later real game under the same criterion.",
        minimum_positions=2, minimum_sessions=2, minimum_delay_seconds=60,
        provenance=author(), created_at=time_at(0),
    )
    values.update(updates)
    return OutcomePolicy(**values)


def plan() -> EvaluationPlan:
    return EvaluationPlan(
        participant_id="P01",
        selection_ref=source("intervention_selection", "selection"),
        hypothesis_revision_ref=source("hypothesis_revision", "revision"),
        intervention_ref=source("training_intervention", "intervention"),
        exercises=(ExerciseBinding(source("exercise", "exercise-v1"), ("submitted",)),),
        policy=policy(), rationale="Criterion tests the selected intervention target.",
        provenance=author(), created_at=time_at(1),
    )


def position(index: int, game: str | None = None) -> OutcomePosition:
    return OutcomePosition(
        position_id=f"pos-{index}", game_id=game or f"game-{index}", fen=FENS[index],
        source_ref=source("canonical_position", f"pos-{index}"),
    )


def attempt(
    ledger: OutcomeLedger, *, index: int = 0, kind: str = "practice",
    start: float = 2, **updates,
):
    values = dict(
        plan_ref=reference(ledger.plan), participant_id=ledger.plan.participant_id,
        attempt_key=f"{kind}-{index}-{start}",
        exercise_ref=ledger.plan.exercises[0].exercise_ref,
        position=position(index), session_id=f"session-{index}", evidence_kind=kind,
        raw_response="My explicitly captured response.", completed=True,
        completion_evidence=(("submitted", "recorded"),), prior_exposure="unexposed",
        assistance="unassisted",
        exposure_scope="Supplied participant study/game history.",
        exposure_refs=(source("exposure_history", f"history-{index}"),),
        context_rationale="Authored context classification under the plan.",
        source_refs=(source("canonical_game", f"game-{index}"),), provenance=author(),
        started_at=time_at(start), frozen_at=time_at(start + .1),
        recorded_at=time_at(start + .2),
    )
    values.update(updates)
    return EvaluationAttempt(**values)


def add(ledger: OutcomeLedger, **kwargs):
    item = attempt(ledger, **kwargs)
    return append_evaluation_attempt(ledger, item), item


def observe(ledger, item, result="criterion_met", **updates):
    values = dict(
        attempt_ref=reference(item), result=result,
        evidence_refs=(source("objective_evidence", "scoring-source"),),
        rationale="Scored against the exact predeclared rubric.",
        provenance=author("coder"),
        recorded_at=time_at(50),
    )
    values.update(updates)
    return record_outcome_observation(ledger, **values)


def trained():
    ledger, item = add(OutcomeLedger(plan()))
    ledger, completion = record_practice_completion(
        ledger, attempt_refs=(reference(item),),
        provenance=author(), completed_at=time_at(3)
    )
    return ledger, completion


def assess(ledger, completion=None):
    return assess_outcome_evidence(
        ledger, completion_ref=None if completion is None else reference(completion),
        created_at=time_at(60),
    )


def dimension(result, kind):
    return next(item for item in result.dimensions if item.evidence_kind == kind)


def populated(kind="near_transfer", results=("criterion_met", "criterion_met")):
    ledger, completion = trained()
    for index, result in enumerate(results, 1):
        ledger, item = add(ledger, index=index, kind=kind, start=5 + index)
        ledger, _ = observe(ledger, item, result)
    return ledger, completion


def test_empty_and_completion_only_are_not_learning() -> None:
    empty = assess(OutcomeLedger(plan()))
    assert all(item.status == "insufficient" for item in empty.dimensions)
    ledger, completion = trained()
    result = assess(ledger, completion)
    assert dimension(result, "practice").status == "unclear"
    assert dimension(result, "practice").unobserved == 1
    assert dimension(result, "near_transfer").status == "insufficient"
    assert result.mastery == result.causal_effect == "not_established"


@pytest.mark.parametrize(
    "kind", ["near_transfer", "far_transfer", "real_game_transfer"]
)
def test_fresh_success_supports_only_its_own_dimension(kind) -> None:
    ledger, completion = populated(kind)
    result = assess(ledger, completion)
    assert dimension(result, kind).status == "supported"
    assert dimension(result, kind).criterion_met == 2
    for other in ("near_transfer", "far_transfer", "real_game_transfer"):
        if other != kind:
            assert dimension(result, other).status == "insufficient"
    assert result.mastery == result.causal_effect == "not_established"


@pytest.mark.parametrize(("results", "status"), [
    (("criterion_not_met", "criterion_not_met"), "not_supported"),
    (("criterion_met", "criterion_not_met"), "mixed"),
    (("criterion_met", "unclear"), "unclear"),
    (("criterion_met", "unscorable"), "unclear"),
])
def test_failures_uncertainty_and_unscorable_evidence_are_preserved(
    results, status
) -> None:
    ledger, completion = populated(results=results)
    result = dimension(assess(ledger, completion), "near_transfer")
    assert result.status == status
    assert result.criterion_not_met == results.count("criterion_not_met")


@pytest.mark.parametrize(("changes", "reason"), [
    ({"prior_exposure": "exposed"}, "prior_exposure_not_unexposed"),
    ({"prior_exposure": "unknown"}, "prior_exposure_not_unexposed"),
    ({"assistance": "assisted"}, "assistance_not_unassisted"),
    ({"assistance": "unknown"}, "assistance_not_unassisted"),
    ({"feedback_at": time_at(5)}, "feedback_before_or_at_freeze"),
    ({"feedback_at": time_at(5.1)}, "feedback_before_or_at_freeze"),
    ({"completed": False, "completion_evidence": ()}, "attempt_incomplete"),
])
def test_transfer_exclusions_are_explicit(changes, reason) -> None:
    ledger, completion = trained()
    ledger, item = add(ledger, kind="near_transfer", index=1, start=5, **changes)
    ledger, _ = observe(ledger, item)
    result = assess(ledger, completion)
    assert dimension(result, "near_transfer").eligible_positions == 0
    excluded = next(x for x in result.exclusions if x.attempt_ref == reference(item))
    assert reason in excluded.reasons


@pytest.mark.parametrize("start", [2.5, 3, 3.5])
def test_transfer_requires_post_completion_delay(start) -> None:
    ledger, completion = trained()
    ledger, item = add(ledger, kind="near_transfer", index=1, start=start)
    reasons = assess(ledger, completion).exclusions[0].reasons
    assert "before_required_post_practice_delay" in reasons


def test_delay_boundary_is_inclusive_but_completion_must_precede_attempt() -> None:
    ledger, completion = trained()
    ledger, _ = add(ledger, kind="near_transfer", index=1, start=4)
    result = dimension(assess(ledger, completion), "near_transfer")
    assert result.eligible_positions == 1


def test_transfer_without_practice_is_ineligible() -> None:
    ledger, item = add(OutcomeLedger(plan()), kind="near_transfer", index=1, start=5)
    result = assess(ledger)
    assert "no_documented_practice_completion" in result.exclusions[0].reasons


def test_same_board_with_other_ids_and_clocks_is_not_fresh() -> None:
    ledger, completion = trained()
    same = OutcomePosition(
        "other-id", "other-game", FENS[0].rsplit(" ", 2)[0] + " 10 20",
        source("canonical_position", "other-id"),
    )
    ledger, _ = add(ledger, kind="near_transfer", index=1, start=5, position=same)
    reasons = assess(ledger, completion).exclusions[0].reasons
    assert "position_reused_or_simultaneous_duplicate" in reasons


def test_repeated_success_does_not_erase_first_failure() -> None:
    ledger, completion = populated(results=("criterion_not_met", "criterion_met"))
    ledger, retry = add(ledger, kind="near_transfer", index=1, start=10)
    ledger, _ = observe(ledger, retry)
    result = dimension(assess(ledger, completion), "near_transfer")
    assert result.status == "mixed" and result.criterion_not_met == 1
    assert result.eligible_positions == 2


def test_simultaneous_duplicates_are_not_tiebroken_by_favorable_outcome() -> None:
    ledger, completion = trained()
    ledger, _ = add(ledger, kind="near_transfer", index=1, start=5, attempt_key="a")
    ledger, _ = add(ledger, kind="near_transfer", index=1, start=5, attempt_key="b")
    result = assess(ledger, completion)
    assert dimension(result, "near_transfer").eligible_positions == 0
    assert len(result.exclusions) == 2


def test_new_retrospective_exposure_changes_only_new_assessment() -> None:
    ledger, completion = populated()
    original = assess(ledger, completion)
    before = original.to_dict()
    ledger, _ = add(ledger, kind="practice", index=1, start=4)
    revised = assess(ledger, completion)
    assert original.to_dict() == before
    assert dimension(original, "near_transfer").status == "supported"
    assert dimension(revised, "near_transfer").status == "insufficient"
    assert original.ledger_ref != revised.ledger_ref


def test_repeated_coders_count_once_and_disagreement_is_unclear() -> None:
    ledger, completion = populated()
    item = ledger.attempts[-1]
    ledger, first = observe(ledger, item)
    assert record_outcome_observation(
        ledger, attempt_ref=first.attempt_ref, result=first.result,
        evidence_refs=first.evidence_refs, rationale=first.rationale,
        provenance=first.provenance, recorded_at=first.recorded_at,
    )[0] == ledger
    ledger, _ = observe(
        ledger, item, "criterion_met", provenance=author("second-coder")
    )
    assert dimension(assess(ledger, completion), "near_transfer").criterion_met == 2
    ledger, _ = observe(
        ledger, item, "criterion_not_met", provenance=author("third-coder")
    )
    result = dimension(assess(ledger, completion), "near_transfer")
    assert result.status == "unclear" and result.unclear == 1
    assert len(ledger.observations) == 4


@pytest.mark.parametrize("kind", ["near_transfer", "real_game_transfer"])
def test_independence_minimum_uses_sessions_or_actual_games(kind) -> None:
    ledger, completion = trained()
    for index in (1, 2):
        ledger, item = add(
            ledger, kind=kind, index=index, start=5+index,
            session_id=(
                "same-session" if kind == "near_transfer" else f"session-{index}"
            ),
            position=position(index, game="one-game"),
            source_refs=(source("canonical_game", "one-game"),),
        )
        ledger, _ = observe(ledger, item)
    result = dimension(assess(ledger, completion), kind)
    assert result.independent_sessions == 1 and result.status == "insufficient"


def test_attempt_retry_is_idempotent_but_edit_is_rejected() -> None:
    before = OutcomeLedger(plan())
    ledger, item = add(before)
    assert before.attempts == ()
    assert append_evaluation_attempt(ledger, item) == ledger
    with pytest.raises(OutcomeEvidenceError, match="already frozen"):
        append_evaluation_attempt(ledger, replace(item, raw_response="changed"))
    with pytest.raises(FrozenInstanceError):
        item.raw_response = "overwrite"


@pytest.mark.parametrize("change", [
    {"participant_id": "P02"}, {"exercise_ref": source("exercise", "wrong-version")},
    {"plan_ref": source("evaluation_plan", "other-plan")},
    {"started_at": time_at(.5)}, {"completion_evidence": (("wrong", "value"),)},
])
def test_attempt_scope_and_provenance_mismatches_rejected(change) -> None:
    ledger = OutcomeLedger(plan())
    with pytest.raises(OutcomeEvidenceError):
        append_evaluation_attempt(ledger, attempt(ledger, **change))


@pytest.mark.parametrize("change", [
    {"evidence_kind": "mastery"}, {"prior_exposure": "fresh"},
    {"assistance": "probably"}, {"completed": 1}, {"completion_evidence": []},
    {"frozen_at": time_at(1)}, {"recorded_at": time_at(1)},
    {"started_at": "2026-09-09T00:02:00"}, {"feedback_at": time_at(70)},
    {"source_refs": ()}, {"exposure_refs": ()},
    {"raw_response": ""},
    {"evidence_kind": "real_game_transfer",
     "source_refs": (source("probe", "not-game"),)},
])
def test_invalid_attempt_records_fail_closed(change) -> None:
    with pytest.raises(OutcomeEvidenceError):
        attempt(OutcomeLedger(plan()), **change)


@pytest.mark.parametrize("updates", [
    {"minimum_positions": 0}, {"minimum_sessions": True},
    {"minimum_delay_seconds": -1}, {"minimum_sessions": 3},
    {"success_criterion": " "}, {"scoring_rubric_ref": source("other", "r")},
])
def test_invalid_policy_rejected(updates) -> None:
    with pytest.raises(OutcomeEvidenceError):
        policy(**updates)


def test_policy_configuration_and_version_are_material() -> None:
    first = policy()
    assert first == policy()
    assert len({
        first.fingerprint, replace(first, version="2").fingerprint,
        replace(first, minimum_delay_seconds=120).fingerprint,
    }) == 3
    ledger, completion = populated()
    with pytest.raises(OutcomeEvidenceError, match="plan/participant"):
        changed_plan = replace(
            ledger.plan, policy=replace(ledger.plan.policy, version="2")
        )
        assess(replace(ledger, plan=changed_plan), completion)


@pytest.mark.parametrize("changes", [
    {"result": "mastered"}, {"attempt_ref": source("evaluation_attempt", "wrong")},
    {"provenance": replace(author(), instruction_fingerprint="different-rubric")},
    {"recorded_at": time_at(1)}, {"evidence_refs": ()}, {"rationale": ""},
])
def test_invalid_observation_rejected(changes) -> None:
    ledger, item = add(OutcomeLedger(plan()))
    with pytest.raises(OutcomeEvidenceError):
        observe(ledger, item, **changes)


def test_unscored_successes_do_not_support_transfer() -> None:
    ledger, completion = populated()
    ledger = replace(ledger, observations=ledger.observations[:1])
    result = dimension(assess(ledger, completion), "near_transfer")
    assert result.status == "unclear" and result.unobserved == 1


def test_completion_requires_exact_completed_practice_records() -> None:
    ledger, item = add(OutcomeLedger(plan()), kind="near_transfer", index=1)
    with pytest.raises(OutcomeEvidenceError, match="completed practice"):
        record_practice_completion(
            ledger, attempt_refs=(reference(item),), provenance=author(),
            completed_at=time_at(3),
        )
    with pytest.raises(OutcomeEvidenceError, match="absent/mismatched"):
        record_practice_completion(
            ledger, attempt_refs=(source("evaluation_attempt", "missing"),),
            provenance=author(), completed_at=time_at(3),
        )
    with pytest.raises(OutcomeEvidenceError, match="duplicate"):
        record_practice_completion(
            ledger, attempt_refs=(reference(item), reference(item)),
            provenance=author(), completed_at=time_at(3),
        )


def test_assessment_rejects_future_inputs_or_unknown_anchor() -> None:
    ledger, completion = populated()
    with pytest.raises(OutcomeEvidenceError, match="predates supplied"):
        assess_outcome_evidence(
            ledger, completion_ref=reference(completion), created_at=time_at(4)
        )
    with pytest.raises(OutcomeEvidenceError, match="completion reference mismatch"):
        assess_outcome_evidence(
            ledger, completion_ref=source("practice_completion", "absent"),
            created_at=time_at(60),
        )


def test_ledger_validation_does_not_trust_direct_construction() -> None:
    ledger, item = add(OutcomeLedger(plan()))
    with pytest.raises(OutcomeEvidenceError, match="duplicate"):
        validate_outcome_ledger(replace(ledger, attempts=(item, item)))
    with pytest.raises(OutcomeEvidenceError, match="immutable"):
        replace(ledger, attempts=[item])


def test_deterministic_rebuild_and_hash_self_consistency() -> None:
    first, completion = populated()
    second, completion2 = populated()
    a, b = assess(first, completion), assess(second, completion2)
    assert a == b
    assert a.fingerprint == fingerprint(a.to_dict(include_identity=False))
    assert a.record_id == f"outcome_assessment_{a.fingerprint[:20]}"
    assert a.to_dict()["schema_version"] == "1"
    with pytest.raises(OutcomeEvidenceError):
        replace(a, mastery="established")


def test_all_transfer_dimensions_still_do_not_establish_mastery_or_causality() -> None:
    ledger, completion = trained()
    index = 0
    for kind in ("near_transfer", "far_transfer", "real_game_transfer"):
        for _ in range(2):
            index += 1
            ledger, item = add(ledger, kind=kind, index=index, start=5+index)
            ledger, _ = observe(ledger, item)
    result = assess(ledger, completion)
    assert all(item.status == "supported" for item in result.dimensions[1:])
    assert result.mastery == result.causal_effect == "not_established"
