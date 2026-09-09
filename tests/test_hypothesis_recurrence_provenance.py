from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisAssessmentError,
    assess_hypothesis_recurrence,
    create_learner_hypothesis,
    define_hypothesis_assessment_policy,
    record_competing_explanation_review,
    record_hypothesis_challenge_review,
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
    )


def _hypothesis():
    return create_learner_hypothesis(
        participant_id="P01",
        statement="A bounded descriptive recurrence proposition.",
        scope_definition="defined decision context",
        origin_provenance=_actor(),
        created_at="2026-09-09T01:00:00+00:00",
    )


def _policy(**overrides):
    values = {
        "assessment_policy_id": "hap-provenance",
        "version": "1",
        "eligible_m6_statuses": ("discrepancy_supported",),
        "eligible_discrepancy_codes": ("EXPECTED_OPPONENT_REPLY_CONFLICT",),
        "allowed_measurement_conditions": ("clean",),
        "m6_policy_compatibility_rule": "same_policy_fingerprint",
        "stage_compatibility_rule": "same_assessed_stage_ids",
        "context_match_rule": "broad_scope",
        "independence_rule": "distinct_game_id",
        "minimum_independent_supports_for_candidate": 2,
        "minimum_independent_supports_for_supported": 3,
        "required_contradiction_review": True,
        "required_counterexample_review": True,
        "required_competing_explanation_review": True,
        "contradiction_rule": "any_contradiction",
    }
    values.update(overrides)
    return define_hypothesis_assessment_policy(**values)


def _competing_review():
    return record_competing_explanation_review(
        state="completed",
        reviewed_hypothesis_refs=(),
        reviewed_alternative_notes=(),
        review_note="No competing references were attached to this revision.",
        reviewer_provenance=_actor("reviewer"),
        created_at="2026-09-09T03:00:00+00:00",
    )


def _assess_empty(hypothesis, revision, **kwargs):
    return assess_hypothesis_recurrence(
        hypothesis=hypothesis,
        revision=revision,
        policy=_policy(),
        evidence_links=(),
        m6_assessments=(),
        m6_assertions=(),
        competing_explanation_review=kwargs.pop(
            "competing_explanation_review",
            _competing_review(),
        ),
        created_at="2026-09-09T04:00:00+00:00",
        **kwargs,
    )


def test_revision_one_must_match_hypothesis_origin_proposal() -> None:
    hypothesis, revision = _hypothesis()
    changed = replace(revision, statement="Forged but hash-consistent proposition.")
    fingerprint = _fingerprint(changed.to_dict(include_identity=False))
    changed = replace(
        changed,
        revision_id=f"hypothesis_revision_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )
    with pytest.raises(HypothesisAssessmentError, match="origin proposal"):
        _assess_empty(hypothesis, changed)


def test_later_revision_requires_exact_lineage_history() -> None:
    hypothesis, revision_one = _hypothesis()
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="Narrowed descriptive proposition.",
        scope_definition="narrowed context",
        revision_reason="new evidence narrowed scope",
        author_provenance=_actor("reviser"),
        created_at="2026-09-09T02:00:00+00:00",
    )
    with pytest.raises(HypothesisAssessmentError, match="require exact revision"):
        _assess_empty(hypothesis, revision_two)
    result = _assess_empty(
        hypothesis,
        revision_two,
        revision_history=(revision_one, revision_two),
    )
    assert result.status == "insufficient"


def test_forged_competing_review_fingerprint_is_rejected() -> None:
    hypothesis, revision = _hypothesis()
    review = _competing_review()
    forged = replace(review, review_note="Mutated after fingerprinting.")
    with pytest.raises(HypothesisAssessmentError, match="Review fingerprint"):
        _assess_empty(
            hypothesis,
            revision,
            competing_explanation_review=forged,
        )


def test_forged_challenge_review_fingerprint_is_rejected() -> None:
    hypothesis, revision = _hypothesis()
    review = record_hypothesis_challenge_review(
        kind="contradiction",
        state="completed",
        reviewed_links=(),
        review_note="Reviewed exact contradiction set.",
        reviewer_provenance=_actor("challenge-reviewer"),
        created_at="2026-09-09T03:00:00+00:00",
    )
    forged = replace(review, review_note="Mutated after fingerprinting.")
    with pytest.raises(HypothesisAssessmentError, match="Review fingerprint"):
        _assess_empty(
            hypothesis,
            revision,
            contradiction_review=forged,
        )


def test_material_policy_change_changes_policy_fingerprint() -> None:
    baseline = _policy()
    stricter = _policy(minimum_independent_supports_for_supported=4)
    assert baseline.policy_fingerprint != stricter.policy_fingerprint
