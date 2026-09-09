"""M16 grounded mentor feedback qualification and rejection coverage."""

from __future__ import annotations

from dataclasses import replace

import pytest
from test_m8_qualification import (
    S10,
    S12,
    S13,
    _ledger_context,
    _through_compare,
    _through_reveal,
)

from chess_mentor_engine.feedback import (
    FEEDBACK_SCHEMA_VERSION,
    GroundedFeedbackError,
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)
from chess_mentor_engine.tutoring import attach_tutor_hypothesis_context


def _compose(*, created_at: str = S13):
    upstream, session, _ = _through_compare()
    feedback = compose_grounded_mentor_feedback(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=created_at,
    )
    return upstream, session, feedback


def test_m16_exact_feedback_is_deterministic_and_evidence_bound() -> None:
    upstream, session, first = _compose()
    second = compose_grounded_mentor_feedback(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )

    assert first == second
    assert first["schema_version"] == FEEDBACK_SCHEMA_VERSION
    assert first["feedback_id"].startswith("grounded_feedback_")
    assert first["claim_scope"] == "session_local_grounded_feedback"
    assert first["evaluation_presentation"]["decision_comparison_id"] == (
        upstream.comparison.comparison_id
    )
    objective = first["sections"][0]
    assert objective["kind"] == "objective"
    assert "60 centipawns worse" in objective["content"]
    assert upstream.comparison.comparison_id in {
        item["ref_id"] for item in objective["evidence_refs"]
    }


def test_m16_reasoning_section_preserves_every_m6_assertion() -> None:
    _, session, feedback = _compose()
    reasoning = next(
        item for item in feedback["sections"] if item["kind"] == "reasoning"
    )

    assert session.comparison is not None
    for assertion in session.comparison.assertions:
        assert assertion.statement in reasoning["content"]
        assert assertion.assertion_id in {
            item["ref_id"] for item in reasoning["evidence_refs"]
        }
    assert "position-local" in reasoning["content"]


def test_m16_records_feedback_through_existing_m8_explanation_transition() -> None:
    upstream, session, _ = _through_compare()
    updated, explanation, feedback = record_grounded_mentor_feedback(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )

    assert updated.state == "explained"
    assert updated.explanation == explanation
    assert explanation.rendered_content == feedback["rendered_content"]
    assert explanation.comparison_id == session.comparison.comparison_id
    assert explanation.provenance.actor_kind == "template"
    assert explanation.provenance.actor_id == "m16-grounded-feedback"
    assert explanation.provenance.run_id == feedback["feedback_id"]
    assert explanation.provenance.instruction_fingerprint == (
        feedback["policy"]["fingerprint"]
    )


def test_m16_includes_all_attached_active_m7_context_with_claim_ceiling() -> None:
    upstream, session, _ = _through_compare()
    snapshot, revision = _ledger_context()
    session, context = attach_tutor_hypothesis_context(
        session,
        ledger_snapshot=snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )

    feedback = compose_grounded_mentor_feedback(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )
    learner = next(
        item
        for item in feedback["sections"]
        if item["kind"] == "learner_context"
    )

    assert revision.statement in learner["content"]
    assert revision.scope_definition in learner["content"]
    assert "not a causal diagnosis" in learner["content"]
    assert context.context_id in {
        item["ref_id"] for item in learner["evidence_refs"]
    }
    assert revision.revision_id in {
        item["ref_id"] for item in learner["evidence_refs"]
    }


def test_m16_reflection_is_question_not_training_assignment() -> None:
    _, _, feedback = _compose()
    reflection = next(
        item for item in feedback["sections"] if item["kind"] == "reflection"
    )

    assert "Reflection:" in reflection["content"]
    assert "?" in reflection["content"]
    assert "training" not in feedback
    assert "intervention" not in feedback
    assert "mastery" not in feedback


def test_m16_rejects_feedback_before_m6_comparison() -> None:
    upstream, revealed = _through_reveal()

    with pytest.raises(GroundedFeedbackError, match="compared tutor session"):
        compose_grounded_mentor_feedback(
            session=revealed,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S13,
        )


def test_m16_rejects_decision_comparison_drift_from_m6_context() -> None:
    upstream, session, _ = _through_compare()
    drifted = replace(upstream.comparison, detail="tampered after M6 binding")

    with pytest.raises(GroundedFeedbackError, match="fingerprint"):
        compose_grounded_mentor_feedback(
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=drifted,
            created_at=S13,
        )


def test_m16_rejects_analysis_not_bound_into_m6_context() -> None:
    upstream, session, _ = _through_compare()
    drifted = replace(upstream.analysis, result_fingerprint="not-the-bound-result")

    with pytest.raises(GroundedFeedbackError, match="not bound into the M6"):
        compose_grounded_mentor_feedback(
            session=session,
            root_analysis=drifted,
            decision_comparison=upstream.comparison,
            created_at=S13,
        )


def test_m16_rejects_objective_analysis_that_was_not_revealed() -> None:
    upstream, session, _ = _through_compare()
    reveal = session.capture_session.objective_reveal
    assert reveal is not None
    hidden_reveal = replace(reveal, position_analysis_refs=())
    capture = replace(session.capture_session, objective_reveal=hidden_reveal)
    hidden_session = replace(session, capture_session=capture)

    with pytest.raises(GroundedFeedbackError, match="not exposed"):
        compose_grounded_mentor_feedback(
            session=hidden_session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S13,
        )


def test_m16_rejects_tampered_active_hypothesis_context() -> None:
    upstream, session, _ = _through_compare()
    snapshot, revision = _ledger_context()
    session, context = attach_tutor_hypothesis_context(
        session,
        ledger_snapshot=snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )
    tampered_revision = replace(revision, statement="unsupported rewrite")
    tampered_context = replace(
        context,
        active_revisions=(tampered_revision,),
    )
    tampered_session = replace(
        session,
        hypothesis_context=tampered_context,
    )

    with pytest.raises(GroundedFeedbackError, match="hypothesis context fingerprint"):
        compose_grounded_mentor_feedback(
            session=tampered_session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S13,
        )


def test_m16_rejects_feedback_that_predates_comparison_evidence() -> None:
    upstream, session, _ = _through_compare()

    with pytest.raises(GroundedFeedbackError, match="cannot predate"):
        compose_grounded_mentor_feedback(
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S10,
        )
