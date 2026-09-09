from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    CompetingExplanationReview,
    HypothesisActorProvenance,
    HypothesisAssessment,
    HypothesisAssessmentError,
    HypothesisAssessmentPolicyRef,
    HypothesisEvidenceSummary,
    HypothesisLifecycleEvent,
    HypothesisRevision,
    HypothesisRevisionRef,
    build_hypothesis_ledger_snapshot,
    create_learner_hypothesis,
    record_competing_explanation_review,
    record_hypothesis_lifecycle_event,
    record_hypothesis_revision,
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _actor(actor_id: str = "analyst") -> HypothesisActorProvenance:
    return HypothesisActorProvenance(
        actor_kind="human",
        actor_id=actor_id,
        actor_version="v1",
        rubric_or_instruction_fingerprint=_fingerprint({"rubric": actor_id}),
        run_id=f"run-{actor_id}",
    )


def _make_hypothesis(participant_id: str = "P01"):
    return create_learner_hypothesis(
        participant_id=participant_id,
        statement="The participant omits a forcing reply in the defined context.",
        scope_definition="defined forcing-reply context",
        origin_provenance=_actor(),
        created_at="2026-09-09T03:00:00+00:00",
    )


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _empty_summary() -> HypothesisEvidenceSummary:
    return HypothesisEvidenceSummary(
        eligible_link_count=0,
        excluded_link_count=0,
        support_unit_count=0,
        independent_support_count=0,
        contradiction_unit_count=0,
        successful_counterexample_unit_count=0,
        context_exception_unit_count=0,
        unclear_unit_count=0,
        mixed_unit_count=0,
        source_position_ids=(),
        source_game_ids=(),
        measurement_conditions=(),
        common_context_refs=(),
        excluded_link_refs=(),
        exclusion_reasons=(),
    )


def _not_required_review() -> CompetingExplanationReview:
    return record_competing_explanation_review(
        state="not_required",
        review_note="Review not required by this fixture policy.",
        reviewer_provenance=None,
        created_at="2026-09-09T04:00:00+00:00",
    )


def _stamp_assessment(
    *,
    revision: HypothesisRevision,
    created_at: str,
) -> HypothesisAssessment:
    policy_ref = HypothesisAssessmentPolicyRef(
        assessment_policy_id="hap-snapshot",
        version="1",
        fingerprint=_fingerprint({"policy": "hap-snapshot"}),
    )
    review = _not_required_review()
    base = HypothesisAssessment(
        hypothesis_assessment_id="pending",
        fingerprint="pending",
        hypothesis_revision_ref=_revision_ref(revision),
        assessment_policy_ref=policy_ref,
        status="insufficient",
        support_link_refs=(),
        contradiction_link_refs=(),
        successful_counterexample_link_refs=(),
        context_exception_link_refs=(),
        unclear_link_refs=(),
        recurrence_units=(),
        recurrence_unit_ids=(),
        independence_unit_ids=(),
        source_position_ids=(),
        source_game_ids=(),
        measurement_conditions=(),
        competing_explanation_review=review,
        evidence_summary=_empty_summary(),
        status_reasons=("fixture",),
        created_at=created_at,
    )
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        hypothesis_assessment_id=f"hypothesis_assessment_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def test_snapshot_uses_current_revision_and_latest_current_revision_assessment() -> None:
    hypothesis, revision_one = _make_hypothesis()
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="Narrowed current statement.",
        scope_definition="narrowed context",
        revision_reason="new evidence narrowed scope",
        author_provenance=_actor("reviser"),
        created_at="2026-09-09T05:00:00+00:00",
    )
    old_assessment = _stamp_assessment(
        revision=revision_one,
        created_at="2026-09-09T04:30:00+00:00",
    )
    first_current = _stamp_assessment(
        revision=revision_two,
        created_at="2026-09-09T06:00:00+00:00",
    )
    latest_current = _stamp_assessment(
        revision=revision_two,
        created_at="2026-09-09T07:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision_two, revision_one),
        assessments=(old_assessment, latest_current, first_current),
        lifecycle_events=(),
        created_at="2026-09-09T08:00:00+00:00",
    )
    entry = snapshot.entries[0]
    assert entry.current_revision_ref.revision_id == revision_two.revision_id
    assert entry.latest_assessment_ref is not None
    assert (
        entry.latest_assessment_ref.hypothesis_assessment_id
        == latest_current.hypothesis_assessment_id
    )


def test_new_revision_does_not_relabel_old_revision_assessment_as_current() -> None:
    hypothesis, revision_one = _make_hypothesis()
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="Narrowed statement.",
        scope_definition="narrowed scope",
        revision_reason="revision",
        author_provenance=_actor(),
        created_at="2026-09-09T05:00:00+00:00",
    )
    old_assessment = _stamp_assessment(
        revision=revision_one,
        created_at="2026-09-09T04:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision_one, revision_two),
        assessments=(old_assessment,),
        lifecycle_events=(),
        created_at="2026-09-09T06:00:00+00:00",
    )
    assert snapshot.entries[0].latest_assessment_ref is None


def test_retirement_changes_authority_state_without_erasing_assessment() -> None:
    hypothesis, revision = _make_hypothesis()
    assessment = _stamp_assessment(
        revision=revision,
        created_at="2026-09-09T04:00:00+00:00",
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=hypothesis,
        existing_events=(),
        kind="retired",
        reason="Later evidence made the proposition no longer useful.",
        author_provenance=_actor("owner"),
        created_at="2026-09-09T05:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision,),
        assessments=(assessment,),
        lifecycle_events=(event,),
        created_at="2026-09-09T06:00:00+00:00",
    )
    entry = snapshot.entries[0]
    assert entry.authority_lifecycle_state == "retired"
    assert entry.latest_lifecycle_event_ref is not None
    assert entry.latest_assessment_ref is not None


def test_supersession_preserves_both_hypothesis_entries() -> None:
    original, original_revision = _make_hypothesis()
    replacement, replacement_revision = create_learner_hypothesis(
        participant_id="P01",
        statement="Replacement descriptive proposition.",
        scope_definition="replacement scope",
        origin_provenance=_actor("replacement-author"),
        created_at="2026-09-09T04:00:00+00:00",
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=original,
        existing_events=(),
        kind="superseded",
        reason="A materially different proposition replaced the original.",
        author_provenance=_actor("owner"),
        superseding_hypothesis=replacement,
        created_at="2026-09-09T05:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(replacement, original),
        revisions=(replacement_revision, original_revision),
        assessments=(),
        lifecycle_events=(event,),
        created_at="2026-09-09T06:00:00+00:00",
    )
    states = {
        entry.hypothesis_ref.hypothesis_id: entry.authority_lifecycle_state
        for entry in snapshot.entries
    }
    assert states[original.hypothesis_id] == "superseded"
    assert states[replacement.hypothesis_id] == "active"


def test_snapshot_replay_is_deterministic_under_input_order() -> None:
    first, first_revision = _make_hypothesis()
    second, second_revision = create_learner_hypothesis(
        participant_id="P01",
        statement="Second descriptive proposition.",
        scope_definition="second scope",
        origin_provenance=_actor("second"),
        created_at="2026-09-09T03:30:00+00:00",
    )
    one = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(first, second),
        revisions=(first_revision, second_revision),
        assessments=(),
        lifecycle_events=(),
        created_at="2026-09-09T06:00:00+00:00",
    )
    two = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(second, first),
        revisions=(second_revision, first_revision),
        assessments=(),
        lifecycle_events=(),
        created_at="2026-09-09T06:00:00+00:00",
    )
    assert one == two


def test_snapshot_rejects_cross_participant_hypothesis_mix() -> None:
    first, first_revision = _make_hypothesis("P01")
    second, second_revision = _make_hypothesis("P02")
    with pytest.raises(HypothesisAssessmentError, match="mix participant"):
        build_hypothesis_ledger_snapshot(
            participant_id="P01",
            hypotheses=(first, second),
            revisions=(first_revision, second_revision),
            assessments=(),
            lifecycle_events=(),
            created_at="2026-09-09T06:00:00+00:00",
        )


def test_snapshot_rejects_duplicate_terminal_lifecycle_history() -> None:
    hypothesis, revision = _make_hypothesis()
    event = record_hypothesis_lifecycle_event(
        hypothesis=hypothesis,
        existing_events=(),
        kind="retired",
        reason="retired",
        author_provenance=_actor(),
        created_at="2026-09-09T05:00:00+00:00",
    )
    with pytest.raises(HypothesisAssessmentError, match="at most one"):
        build_hypothesis_ledger_snapshot(
            participant_id="P01",
            hypotheses=(hypothesis,),
            revisions=(revision,),
            assessments=(),
            lifecycle_events=(event, event),
            created_at="2026-09-09T06:00:00+00:00",
        )


def test_snapshot_rejects_forged_assessment_fingerprint() -> None:
    hypothesis, revision = _make_hypothesis()
    assessment = _stamp_assessment(
        revision=revision,
        created_at="2026-09-09T04:00:00+00:00",
    )
    forged = replace(assessment, status_reasons=("forged",))
    with pytest.raises(HypothesisAssessmentError, match="fingerprint"):
        build_hypothesis_ledger_snapshot(
            participant_id="P01",
            hypotheses=(hypothesis,),
            revisions=(revision,),
            assessments=(forged,),
            lifecycle_events=(),
            created_at="2026-09-09T06:00:00+00:00",
        )


def test_snapshot_rejects_future_assessment() -> None:
    hypothesis, revision = _make_hypothesis()
    assessment = _stamp_assessment(
        revision=revision,
        created_at="2026-09-10T04:00:00+00:00",
    )
    with pytest.raises(HypothesisAssessmentError, match="predate assessment"):
        build_hypothesis_ledger_snapshot(
            participant_id="P01",
            hypotheses=(hypothesis,),
            revisions=(revision,),
            assessments=(assessment,),
            lifecycle_events=(),
            created_at="2026-09-09T06:00:00+00:00",
        )


def test_snapshot_rejects_lifecycle_event_for_unknown_hypothesis() -> None:
    hypothesis, revision = _make_hypothesis()
    other, _ = create_learner_hypothesis(
        participant_id="P01",
        statement="Other hypothesis.",
        scope_definition="other scope",
        origin_provenance=_actor("other"),
        created_at="2026-09-09T03:30:00+00:00",
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=other,
        existing_events=(),
        kind="retired",
        reason="retired",
        author_provenance=_actor(),
        created_at="2026-09-09T05:00:00+00:00",
    )
    with pytest.raises(HypothesisAssessmentError, match="outside snapshot"):
        build_hypothesis_ledger_snapshot(
            participant_id="P01",
            hypotheses=(hypothesis,),
            revisions=(revision,),
            assessments=(),
            lifecycle_events=(event,),
            created_at="2026-09-09T06:00:00+00:00",
        )
