"""M10 integration: actual M9 producer outputs, M1 positions, and local storage.

The existing M9 fixture supplies synthetic M7 ledger inputs. This tests the
M9-to-M10 contract, not fresh empirical efficacy or a new qualification of M7.
"""

from __future__ import annotations

from dataclasses import replace

import pytest
from test_m9_qualification import (
    _intervention,
    _mapping,
    _registry,
    _revision,
    _select,
    _snapshot,
)
from test_outcome_evidence import author, dimension, policy, source, time_at

from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.evaluation import (
    EvaluationAttempt,
    OutcomeEvidenceError,
    OutcomeLedger,
    append_evaluation_attempt,
    assess_outcome_evidence,
    define_evaluation_plan,
    record_outcome_observation,
    record_practice_completion,
    reference,
    reference_outcome_position,
)
from chess_mentor_engine.storage import LocalArtifactStore


def selected():
    revision = _revision()
    intervention = _intervention()
    registry = _registry(intervention)
    selection = _select(
        revision, _snapshot(revision), registry,
        (_mapping(revision, intervention),),
    )
    assert selection.decision == "selected"
    return selection, intervention


def make_plan(selection=None, intervention=None, **updates):
    if selection is None:
        selection, intervention = selected()
    values = dict(
        participant_id="P01", selection=selection, intervention=intervention,
        policy=policy(), rationale="The criterion operationalizes the selected target.",
        provenance=author(), created_at=time_at(800),
    )
    values.update(updates)
    return define_evaluation_plan(**values)


def capture(ledger, position, kind, start, key):
    binding = ledger.plan.exercises[0]
    item = EvaluationAttempt(
        plan_ref=reference(ledger.plan), participant_id="P01", attempt_key=key,
        exercise_ref=binding.exercise_ref,
        position=reference_outcome_position(position),
        session_id=key, evidence_kind=kind,
        raw_response="Captured candidates and predicted replies.", completed=True,
        completion_evidence=tuple(
            (field, "captured") for field in binding.completion_fields
        ),
        prior_exposure="unexposed", assistance="unassisted",
        exposure_scope="Declared local game and study corpus.",
        exposure_refs=(source("exposure_history", key),),
        context_rationale="Near-context relation authored under the exact plan.",
        source_refs=(source("canonical_game", position.game_id),), provenance=author(),
        started_at=time_at(start), frozen_at=time_at(start+.1),
        recorded_at=time_at(start+.2),
    )
    ledger = append_evaluation_attempt(ledger, item)
    return ledger, item


def test_m10_actual_m9_to_fresh_outcomes_and_storage(tmp_path) -> None:
    selection, intervention = selected()
    original = selection.to_dict(), intervention.to_dict()
    evaluation_plan = make_plan(selection, intervention)
    game = ingest_pgn('[Result "*"]\n\n1. e4 e5 2. Nf3 Nc6 *').games[0]
    ledger = OutcomeLedger(evaluation_plan)
    ledger, practice = capture(ledger, game.positions[0], "practice", 802, "practice")
    ledger, completion = record_practice_completion(
        ledger, attempt_refs=(reference(practice),), provenance=author(),
        completed_at=time_at(803),
    )
    for index in (1, 2):
        ledger, item = capture(
            ledger, game.positions[index], "near_transfer", 810+index, f"probe-{index}"
        )
        ledger, _ = record_outcome_observation(
            ledger, attempt_ref=reference(item), result="criterion_met",
            evidence_refs=(source("objective_evidence", f"score-{index}"),),
            rationale="Criterion met under the exact rubric, not a causal claim.",
            provenance=author("coder"), recorded_at=time_at(815+index),
        )
    assessment = assess_outcome_evidence(
        ledger, completion_ref=reference(completion), created_at=time_at(820)
    )
    assert dimension(assessment, "near_transfer").status == "supported"
    assert assessment.mastery == assessment.causal_effect == "not_established"
    assert (selection.to_dict(), intervention.to_dict()) == original
    assert evaluation_plan.selection_ref.fingerprint == selection.fingerprint
    assert evaluation_plan.intervention_ref.fingerprint == intervention.fingerprint
    assert (evaluation_plan.hypothesis_revision_ref.ref_id
            == selection.hypothesis_revision_ref.revision_id)

    # Generic archival round trip: native evidence hashes are not storage hashes.
    store = LocalArtifactStore(tmp_path / "outcomes.sqlite")
    ledger_ref = store.put(
        kind="outcome_ledger", artifact_id=ledger.record_id,
        participant_id="P01", payload=ledger.to_dict(),
    )
    result_ref = store.put(
        kind="outcome_assessment", artifact_id=assessment.record_id,
        participant_id="P01", payload=assessment.to_dict(),
        dependencies=(ledger_ref,),
    )
    reopened = LocalArtifactStore(tmp_path / "outcomes.sqlite")
    assert reopened.get(ledger_ref, participant_id="P01").payload == ledger.to_dict()
    recovered = reopened.get(result_ref, participant_id="P01").payload
    assert recovered == assessment.to_dict()


@pytest.mark.parametrize("decision_kind", ["ineligible", "unclear"])
def test_m10_does_not_promote_nonselected_m9_decisions(decision_kind) -> None:
    revision = _revision()
    intervention = _intervention()
    mappings = () if decision_kind == "ineligible" else (
        _mapping(revision, intervention, applicability="unclear"),
    )
    selection = _select(
        revision, _snapshot(revision), _registry(intervention), mappings
    )
    assert selection.decision == decision_kind
    with pytest.raises(OutcomeEvidenceError, match="selected M9"):
        make_plan(selection, intervention)


@pytest.mark.parametrize("target", ["selection", "intervention", "exercise"])
def test_m10_revalidates_m9_fingerprints(target) -> None:
    selection, intervention = selected()
    if target == "selection":
        selection = replace(selection, fingerprint="tampered")
    elif target == "intervention":
        intervention = replace(intervention, title="tampered")
    else:
        # Alter an exercise, then coherently rehash the outer intervention and
        # selection. The nested exercise must still be independently rejected.
        from chess_mentor_engine.evaluation.model import fingerprint
        intervention = replace(
            intervention,
            exercises=(replace(intervention.exercises[0], title="tampered"),),
        )
        digest = fingerprint(intervention.to_dict(include_identity=False))
        intervention = replace(
            intervention, intervention_id=f"training_intervention_{digest[:20]}",
            fingerprint=digest,
        )
        selected_ref = replace(
            selection.selected_intervention_ref,
            intervention_id=intervention.intervention_id, fingerprint=digest,
        )
        selection = replace(selection, selected_intervention_ref=selected_ref)
        digest = fingerprint(selection.to_dict(include_identity=False))
        selection = replace(
            selection, selection_id=f"intervention_selection_{digest[:20]}",
            fingerprint=digest,
        )
    with pytest.raises(OutcomeEvidenceError, match="fingerprint/identity"):
        make_plan(selection, intervention)


@pytest.mark.parametrize(
    "change", ["participant", "intervention_version", "chronology"]
)
def test_m10_mismatched_selected_context_is_rejected(change) -> None:
    selection, intervention = selected()
    updates = {}
    if change == "participant":
        updates["participant_id"] = "P02"
    elif change == "intervention_version":
        intervention = _intervention(version="2")
    else:
        updates["created_at"] = time_at(1)
    with pytest.raises(OutcomeEvidenceError):
        make_plan(selection, intervention, **updates)


def test_real_m1_position_identity_and_reuse_key() -> None:
    game = ingest_pgn('[Result "*"]\n\n1. e4 *').games[0]
    first = reference_outcome_position(game.positions[0])
    duplicate = reference_outcome_position(replace(
        game.positions[0], position_id="reimported", game_id="another-game"
    ))
    assert first.source_ref != duplicate.source_ref
    assert first.reuse_key == duplicate.reuse_key


def test_public_exports_are_importable() -> None:
    import chess_mentor_engine.evaluation as public
    for name in public.__all__:
        assert getattr(public, name) is not None
