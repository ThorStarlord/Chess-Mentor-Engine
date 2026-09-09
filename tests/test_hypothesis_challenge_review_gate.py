from __future__ import annotations

from chess_mentor_engine.learning import (
    assess_hypothesis_recurrence,
    record_hypothesis_challenge_review,
)
from test_hypothesis_recurrence_assessment import (
    _make_hypothesis,
    _make_link,
    _policy,
    _review,
    _support_units,
)


def _sources(units):
    assessment_map = {
        (item[1].assessment_id, item[1].fingerprint): item[1] for item in units
    }
    assertion_map = {
        (assertion.assertion_id, assertion.fingerprint): assertion
        for item in units
        for assertion in item[2]
    }
    assessments = tuple(assessment_map[key] for key in sorted(assessment_map))
    assertions = tuple(assertion_map[key] for key in sorted(assertion_map))
    return assessments, assertions


def test_required_contradiction_review_blocks_contradicted_status() -> None:
    hypothesis, revision = _make_hypothesis()
    units = list(_support_units(hypothesis, revision, 3))
    units.append(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=4,
            relation="contradicts",
            game_id="g4",
        )
    )
    assessments, assertions = _sources(tuple(units))
    incomplete_review = record_hypothesis_challenge_review(
        kind="contradiction",
        state="not_required",
        reviewed_links=(),
        review_note="Fixture explicitly leaves contradiction review incomplete.",
        reviewer_provenance=None,
        created_at="2026-09-09T05:00:00+00:00",
    )
    result = assess_hypothesis_recurrence(
        hypothesis=hypothesis,
        revision=revision,
        policy=_policy(),
        evidence_links=tuple(item[0] for item in units),
        m6_assessments=assessments,
        m6_assertions=assertions,
        contradiction_review=incomplete_review,
        competing_explanation_review=_review(revision),
        created_at="2026-09-09T06:00:00+00:00",
    )
    assert result.status == "unclear"
    assert "required_challenge_review_incomplete" in result.status_reasons


def test_required_counterexample_review_blocks_supported_status() -> None:
    hypothesis, revision = _make_hypothesis()
    units = list(_support_units(hypothesis, revision, 3))
    units.append(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=4,
            relation="successful_counterexample",
            game_id="g4",
            status="no_supported_discrepancy",
            with_assertion=False,
        )
    )
    assessments, assertions = _sources(tuple(units))
    incomplete_review = record_hypothesis_challenge_review(
        kind="successful_counterexample",
        state="not_required",
        reviewed_links=(),
        review_note="Fixture explicitly leaves counterexample review incomplete.",
        reviewer_provenance=None,
        created_at="2026-09-09T05:00:00+00:00",
    )
    result = assess_hypothesis_recurrence(
        hypothesis=hypothesis,
        revision=revision,
        policy=_policy(),
        evidence_links=tuple(item[0] for item in units),
        m6_assessments=assessments,
        m6_assertions=assertions,
        counterexample_review=incomplete_review,
        competing_explanation_review=_review(revision),
        created_at="2026-09-09T06:00:00+00:00",
    )
    assert result.status == "candidate_recurrence"
    assert "counterexample_review_incomplete" in result.status_reasons
