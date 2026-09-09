"""Compatibility surface for the hardened M7C recurrence implementation."""

from __future__ import annotations

import hashlib

from .assessment_model import (
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
)
from .hypothesis_model import (
    HypothesisActorProvenance,
    HypothesisEvidenceLink,
    HypothesisRevision,
    LearnerHypothesis,
)
from .hypothesis_recurrence import (
    HypothesisAssessmentError,
    assess_hypothesis_recurrence as _assess_hypothesis_recurrence,
    build_hypothesis_ledger_snapshot,
    define_hypothesis_assessment_policy,
    record_competing_explanation_review,
    record_hypothesis_challenge_review,
)
from .hypothesis_recurrence_model import (
    CompetingExplanationReview,
    HypothesisAssessment,
    HypothesisAssessmentPolicy,
    HypothesisChallengeReview,
)

_SYSTEM_REVIEW_RUBRIC = hashlib.sha256(
    b"m7c-exact-evidence-set-challenge-review-v1"
).hexdigest()


def _system_review_actor() -> HypothesisActorProvenance:
    return HypothesisActorProvenance(
        actor_kind="system",
        actor_id="m7c-exact-evidence-set-review",
        actor_version="1",
        rubric_or_instruction_fingerprint=_SYSTEM_REVIEW_RUBRIC,
    )


def assess_hypothesis_recurrence(
    *,
    hypothesis: LearnerHypothesis,
    revision: HypothesisRevision,
    policy: HypothesisAssessmentPolicy,
    evidence_links: tuple[HypothesisEvidenceLink, ...],
    m6_assessments: tuple[ReasoningDiscrepancyAssessment, ...],
    m6_assertions: tuple[ReasoningDiscrepancyAssertion, ...],
    competing_explanation_review: CompetingExplanationReview,
    created_at: str,
    contradiction_review: HypothesisChallengeReview | None = None,
    counterexample_review: HypothesisChallengeReview | None = None,
    revision_history: tuple[HypothesisRevision, ...] | None = None,
) -> HypothesisAssessment:
    """Assess recurrence with explicit or deterministic challenge review records."""

    if revision.revision_number > 1 and revision_history is None:
        raise HypothesisAssessmentError(
            "later hypothesis revisions require exact revision history"
        )

    actor = _system_review_actor()
    if contradiction_review is None:
        contradiction_review = record_hypothesis_challenge_review(
            kind="contradiction",
            state="completed",
            reviewed_links=tuple(
                link for link in evidence_links if link.relation == "contradicts"
            ),
            review_note=(
                "Deterministic review of contradiction links in the exact "
                "frozen assessment evidence set."
            ),
            reviewer_provenance=actor,
            created_at=created_at,
        )
    if counterexample_review is None:
        counterexample_review = record_hypothesis_challenge_review(
            kind="successful_counterexample",
            state="completed",
            reviewed_links=tuple(
                link
                for link in evidence_links
                if link.relation == "successful_counterexample"
            ),
            review_note=(
                "Deterministic review of successful-counterexample links in "
                "the exact frozen assessment evidence set."
            ),
            reviewer_provenance=actor,
            created_at=created_at,
        )
    return _assess_hypothesis_recurrence(
        hypothesis=hypothesis,
        revision=revision,
        policy=policy,
        evidence_links=evidence_links,
        m6_assessments=m6_assessments,
        m6_assertions=m6_assertions,
        contradiction_review=contradiction_review,
        counterexample_review=counterexample_review,
        competing_explanation_review=competing_explanation_review,
        created_at=created_at,
        revision_history=revision_history,
    )


__all__ = [
    "HypothesisAssessmentError",
    "assess_hypothesis_recurrence",
    "build_hypothesis_ledger_snapshot",
    "define_hypothesis_assessment_policy",
    "record_competing_explanation_review",
    "record_hypothesis_challenge_review",
]
