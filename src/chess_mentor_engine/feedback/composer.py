"""M16 deterministic mentor feedback grounded in qualified evidence."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.presentation import (
    EvaluationPresentationError,
    build_evaluation_presentation,
)
from chess_mentor_engine.selection import DecisionComparison
from chess_mentor_engine.tutoring import (
    TutorExplanation,
    TutorExplanationProvenance,
    TutorSession,
    TutorSessionError,
    record_tutor_explanation,
)

FEEDBACK_SCHEMA_VERSION = "m16.grounded-mentor-feedback.v1"
_POLICY_ID = "m16-grounded-feedback"
_POLICY_VERSION = "1"

_REFLECTION_PROMPTS: dict[str, str] = {
    "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED": (
        "Which objectively relevant feature was not explicit in your reasoning, "
        "and how should it change the candidate moves you consider?"
    ),
    "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED": (
        "Which strong candidate was omitted from your reported reasoning, and what "
        "would make you consider it before committing to a move?"
    ),
    "EXPECTED_OPPONENT_REPLY_CONFLICT": (
        "Before committing to the move, what is the opponent's strongest reply?"
    ),
    "EXPECTED_CONTINUATION_CONFLICT": (
        "After the opponent's strongest reply, what continuation do you expect, "
        "and does it still support the move?"
    ),
    "REPORTED_RESULTING_EVALUATION_CONFLICT": (
        "What resulting evaluation did you expect, and how does the cited objective "
        "evidence differ?"
    ),
    "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE": (
        "What concrete legal move would execute the target you described?"
    ),
    "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE": (
        "What additional reason supports the move beyond the rationale you reported?"
    ),
    "OTHER_LOCAL_DISCREPANCY": (
        "Which part of your reported reasoning differs from the cited objective "
        "evidence?"
    ),
}


class GroundedFeedbackError(ValueError):
    """M16 feedback cannot be composed without preserving evidence integrity."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise GroundedFeedbackError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GroundedFeedbackError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GroundedFeedbackError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _analysis_ref(
    outcome: PositionAnalysis | AnalysisFailure,
) -> tuple[str, str]:
    payload = outcome.to_dict()
    fingerprint = _fingerprint(payload)
    if isinstance(outcome, PositionAnalysis):
        return outcome.result_fingerprint, fingerprint
    return f"analysis_failure_{fingerprint[:20]}", fingerprint


def _policy_payload() -> dict[str, Any]:
    return {
        "policy_id": _POLICY_ID,
        "version": _POLICY_VERSION,
        "schema_version": FEEDBACK_SCHEMA_VERSION,
        "reflection_prompts": [
            [key, _REFLECTION_PROMPTS[key]]
            for key in sorted(_REFLECTION_PROMPTS)
        ],
        "include_all_m6_assertions": True,
        "include_all_active_m7_revisions": True,
        "move_notation": "uci",
        "non_exact_score_rule": "never_claim_exact_centipawn_loss",
    }


def _validate_tutor_comparison(session: TutorSession) -> None:
    if session.state != "compared":
        raise GroundedFeedbackError(
            "grounded feedback requires a compared tutor session"
        )
    if session.explanation is not None:
        raise GroundedFeedbackError(
            "grounded feedback cannot replace an existing explanation"
        )
    comparison = session.comparison
    if comparison is None:
        raise GroundedFeedbackError("compared tutor session is missing comparison")
    expected = _fingerprint(comparison.to_dict(include_identity=False))
    if comparison.fingerprint != expected:
        raise GroundedFeedbackError("tutor comparison fingerprint mismatch")
    if comparison.comparison_id != f"tutor_comparison_{expected[:20]}":
        raise GroundedFeedbackError("tutor comparison identity mismatch")


def _validate_hypothesis_context(session: TutorSession) -> None:
    context = session.hypothesis_context
    if context is None:
        return
    expected = _fingerprint(context.to_dict(include_identity=False))
    if context.fingerprint != expected:
        raise GroundedFeedbackError("hypothesis context fingerprint mismatch")
    expected_id = f"tutor_hypothesis_context_{expected[:20]}"
    if context.context_id != expected_id:
        raise GroundedFeedbackError("hypothesis context identity mismatch")
    for revision in context.active_revisions:
        revision_fingerprint = _fingerprint(
            revision.to_dict(include_identity=False)
        )
        if revision.fingerprint != revision_fingerprint:
            raise GroundedFeedbackError(
                "active hypothesis revision fingerprint mismatch"
            )
        expected_revision_id = (
            f"hypothesis_revision_{revision_fingerprint[:20]}"
        )
        if revision.revision_id != expected_revision_id:
            raise GroundedFeedbackError(
                "active hypothesis revision identity mismatch"
            )


def _validate_objective_binding(
    *,
    session: TutorSession,
    decision_comparison: DecisionComparison,
    root_analysis: PositionAnalysis,
    played_analysis: PositionAnalysis | AnalysisFailure | None,
) -> None:
    comparison = session.comparison
    assert comparison is not None
    context = comparison.reasoning_context

    comparison_fingerprint = _fingerprint(decision_comparison.to_dict())
    comparison_ref = context.decision_comparison_ref
    if comparison_ref.ref_id != decision_comparison.comparison_id:
        raise GroundedFeedbackError(
            "M4 decision comparison does not match tutor reasoning context"
        )
    if comparison_ref.fingerprint != comparison_fingerprint:
        raise GroundedFeedbackError(
            "M4 decision comparison fingerprint does not match M6 context"
        )
    if decision_comparison.position_id != context.position_id:
        raise GroundedFeedbackError("M4/M6 position mismatch")
    if decision_comparison.game_id != context.game_id:
        raise GroundedFeedbackError("M4/M6 game mismatch")

    available_refs = {
        (item.ref_id, item.fingerprint)
        for item in context.position_analysis_refs
    }
    required = [_analysis_ref(root_analysis)]
    if played_analysis is not None:
        required.append(_analysis_ref(played_analysis))
    missing = [item for item in required if item not in available_refs]
    if missing:
        raise GroundedFeedbackError(
            "M15 analysis evidence is not bound into the M6 reasoning context"
        )

    reveal = session.capture_session.objective_reveal
    if reveal is None:
        raise GroundedFeedbackError(
            "compared tutor session is missing objective reveal"
        )
    revealed_comparison = reveal.decision_comparison_ref
    if revealed_comparison is None:
        raise GroundedFeedbackError(
            "objective reveal did not expose the decision comparison"
        )
    if (
        revealed_comparison.ref_id != decision_comparison.comparison_id
        or revealed_comparison.fingerprint != comparison_fingerprint
    ):
        raise GroundedFeedbackError(
            "objective reveal decision comparison does not match M6 context"
        )

    root_ref = _analysis_ref(root_analysis)
    revealed_analysis_refs = {
        (item.ref_id, item.fingerprint)
        for item in reveal.position_analysis_refs
    }
    if root_ref not in revealed_analysis_refs:
        raise GroundedFeedbackError(
            "root analysis was not exposed by the objective reveal"
        )
    if isinstance(played_analysis, PositionAnalysis):
        if _analysis_ref(played_analysis) not in revealed_analysis_refs:
            raise GroundedFeedbackError(
                "played-child analysis was not exposed by the objective reveal"
            )


def _validate_chronology(session: TutorSession, created_at: str) -> None:
    created_time = _parse_timestamp(created_at)
    comparison = session.comparison
    assert comparison is not None
    lower_bound = _parse_timestamp(comparison.recorded_at)
    if session.hypothesis_context is not None:
        lower_bound = max(
            lower_bound,
            _parse_timestamp(session.hypothesis_context.attached_at),
        )
    if created_time < lower_bound:
        raise GroundedFeedbackError(
            "grounded feedback cannot predate its evidence context"
        )


def _objective_content(presentation: dict[str, Any]) -> str:
    subject = presentation["subject"]
    comparison = presentation["comparison"]
    played = subject["played_move_uci"]
    best = comparison["best_move_uci"]
    quality = comparison["evidence_quality"]
    kind = comparison["comparison_kind"]
    preference = comparison["preference"]
    delta = comparison["exact_centipawn_delta_for_mover"]
    mate_relation = comparison["mate_relation"]
    terminal_outcome = comparison["terminal_outcome"]

    if quality != "exact":
        best_text = "no exact rank-1 move is available"
        if best is not None:
            best_text = f"the retained rank-1 move is {best}"
        return (
            f"You played {played}; {best_text}. The objective comparison is "
            f"{quality} ({kind}), so no exact centipawn loss is claimed."
        )

    if delta is not None:
        if preference == "worse_for_mover":
            return (
                f"You played {played}; the engine rank-1 move was {best}. Under "
                f"the cited exact comparison, the played move is {delta} "
                "centipawns worse for the decision mover."
            )
        if preference == "approximately_equal_under_policy":
            return (
                f"You played {played}; the engine rank-1 move was {best}. Under "
                f"the cited exact comparison policy, the mover-relative difference "
                f"is {delta} centipawns and is approximately equal."
            )
        if preference == "better_for_mover":
            return (
                f"You played {played}; the retained rank-1 move was {best}. The "
                f"cited exact comparison reports a mover-relative difference of "
                f"{delta} centipawns in favor of the played move."
            )
        return (
            f"You played {played}; the retained rank-1 move was {best}. The exact "
            f"engine evidence is marked {preference}; its signed mover-relative "
            f"difference is {delta} centipawns."
        )

    if mate_relation is not None:
        return (
            f"You played {played}; the engine rank-1 move was {best}. The exact "
            f"comparison reports the symbolic mate relation {mate_relation}; no "
            "mate score is converted into centipawns."
        )
    if terminal_outcome is not None:
        return (
            f"You played {played}. The exact comparison records terminal outcome "
            f"{terminal_outcome}; no centipawn substitute is invented."
        )
    return (
        f"You played {played}; the retained rank-1 move was {best}. The objective "
        f"comparison is exact and classified as {kind}."
    )


def _reasoning_content(session: TutorSession) -> str:
    comparison = session.comparison
    assert comparison is not None
    assessment = comparison.assessment
    lines: list[str] = []
    if assessment.status == "discrepancy_supported":
        lines.append(
            "The cited M6 assessment supports a position-local reasoning "
            "discrepancy."
        )
    elif assessment.status == "no_supported_discrepancy":
        lines.append(
            "The cited M6 assessment does not support a position-local reasoning "
            "discrepancy under its policy."
        )
    elif assessment.status == "unclear":
        lines.append(
            "The cited M6 assessment is unclear, so no stronger reasoning claim "
            "is made."
        )
    else:
        lines.append(
            "The cited M6 assessment is unscorable, so no stronger reasoning claim "
            "is made."
        )

    if assessment.measurement_condition != "clean":
        lines.append(
            "Measurement condition: "
            f"{assessment.measurement_condition}."
        )
    for assertion in comparison.assertions:
        lines.append(f"Evidence-backed local assertion: {assertion.statement}")
    if assessment.status_reasons:
        lines.append(
            "Assessment reasons: " + "; ".join(assessment.status_reasons)
        )
    return "\n".join(lines)


def _learner_context_content(session: TutorSession) -> str | None:
    context = session.hypothesis_context
    if context is None:
        return None
    if not context.active_revisions:
        return (
            "No active current learner hypothesis is attached. No recurring learner "
            "pattern is claimed from this session alone."
        )
    lines = [
        "Current M7 learner context is descriptive hypothesis evidence only; it is "
        "not a causal diagnosis."
    ]
    for revision in context.active_revisions:
        lines.append(
            f"Hypothesis: {revision.statement} Scope: {revision.scope_definition}"
        )
        if revision.unresolved_alternative_notes:
            lines.append(
                "Unresolved alternatives: "
                + "; ".join(revision.unresolved_alternative_notes)
            )
        if revision.competing_hypothesis_refs:
            lines.append(
                "Competing hypothesis references retained: "
                f"{len(revision.competing_hypothesis_refs)}."
            )
    return "\n".join(lines)


def _reflection_content(session: TutorSession) -> str:
    comparison = session.comparison
    assert comparison is not None
    prompts: list[str] = []
    seen: set[str] = set()
    for assertion in comparison.assertions:
        if assertion.code in seen:
            continue
        seen.add(assertion.code)
        prompt = _REFLECTION_PROMPTS.get(assertion.code)
        if prompt is not None:
            prompts.append(prompt)
    if not prompts:
        if comparison.assessment.status in {"unclear", "unscorable"}:
            prompts.append(
                "What additional information would make your reasoning easier to "
                "evaluate in this position?"
            )
        else:
            prompts.append(
                "Which candidate move or opponent reply would most change your "
                "evaluation if you reviewed this position again?"
            )
    return "\n".join(f"Reflection: {item}" for item in prompts)


def _section_refs(session: TutorSession) -> dict[str, list[dict[str, str]]]:
    comparison = session.comparison
    assert comparison is not None
    context = comparison.reasoning_context
    refs: dict[str, list[dict[str, str]]] = {
        "objective": [
            context.decision_comparison_ref.to_dict(),
            *[item.to_dict() for item in context.position_analysis_refs],
        ],
        "reasoning": [
            {
                "kind": "reasoning_assessment",
                "ref_id": comparison.assessment.assessment_id,
                "fingerprint": comparison.assessment.fingerprint,
            },
            *[
                {
                    "kind": "reasoning_assertion",
                    "ref_id": item.assertion_id,
                    "fingerprint": item.fingerprint,
                }
                for item in comparison.assertions
            ],
        ],
        "reflection": [
            {
                "kind": "reasoning_assessment",
                "ref_id": comparison.assessment.assessment_id,
                "fingerprint": comparison.assessment.fingerprint,
            }
        ],
    }
    if session.hypothesis_context is not None:
        refs["learner_context"] = [
            {
                "kind": "tutor_hypothesis_context",
                "ref_id": session.hypothesis_context.context_id,
                "fingerprint": session.hypothesis_context.fingerprint,
            },
            *[
                {
                    "kind": "hypothesis_revision",
                    "ref_id": item.revision_id,
                    "fingerprint": item.fingerprint,
                }
                for item in session.hypothesis_context.active_revisions
            ],
        ]
    return refs


def compose_grounded_mentor_feedback(
    *,
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> dict[str, Any]:
    """Compose conservative session-local mentor feedback from exact evidence."""
    _validate_tutor_comparison(session)
    _validate_hypothesis_context(session)
    _validate_objective_binding(
        session=session,
        decision_comparison=decision_comparison,
        root_analysis=root_analysis,
        played_analysis=played_analysis,
    )
    _validate_chronology(session, created_at)
    try:
        presentation = build_evaluation_presentation(
            root_analysis=root_analysis,
            comparison=decision_comparison,
            played_analysis=played_analysis,
        )
    except EvaluationPresentationError as exc:
        raise GroundedFeedbackError(
            f"M15 evaluation presentation rejected evidence: {exc}"
        ) from exc

    comparison = session.comparison
    assert comparison is not None
    presentation_fingerprint = _fingerprint(presentation)
    refs = _section_refs(session)
    sections: list[dict[str, Any]] = [
        {
            "kind": "objective",
            "claim_scope": "qualified_objective_evidence",
            "content": _objective_content(presentation),
            "evidence_refs": refs["objective"],
        },
        {
            "kind": "reasoning",
            "claim_scope": "position_local_m6_assessment",
            "content": _reasoning_content(session),
            "evidence_refs": refs["reasoning"],
        },
    ]
    learner_content = _learner_context_content(session)
    if learner_content is not None:
        sections.append(
            {
                "kind": "learner_context",
                "claim_scope": "descriptive_m7_hypothesis_context",
                "content": learner_content,
                "evidence_refs": refs["learner_context"],
            }
        )
    sections.append(
        {
            "kind": "reflection",
            "claim_scope": "session_local_reflection_prompt",
            "content": _reflection_content(session),
            "evidence_refs": refs["reflection"],
        }
    )

    rendered_content = "\n\n".join(
        f"{item['kind'].replace('_', ' ').title()}\n{item['content']}"
        for item in sections
    )
    policy = _policy_payload()
    policy["fingerprint"] = _fingerprint(policy)
    payload: dict[str, Any] = {
        "schema_version": FEEDBACK_SCHEMA_VERSION,
        "tutor_session_id": session.tutor_session_id,
        "tutor_comparison_id": comparison.comparison_id,
        "tutor_comparison_fingerprint": comparison.fingerprint,
        "hypothesis_context_id": (
            None
            if session.hypothesis_context is None
            else session.hypothesis_context.context_id
        ),
        "hypothesis_context_fingerprint": (
            None
            if session.hypothesis_context is None
            else session.hypothesis_context.fingerprint
        ),
        "evaluation_presentation": {
            "schema_version": presentation["schema_version"],
            "fingerprint": presentation_fingerprint,
            "decision_comparison_id": decision_comparison.comparison_id,
        },
        "policy": policy,
        "sections": sections,
        "rendered_content": rendered_content,
        "created_at": created_at,
        "claim_scope": "session_local_grounded_feedback",
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "feedback_id": f"grounded_feedback_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def record_grounded_mentor_feedback(
    *,
    session: TutorSession,
    root_analysis: PositionAnalysis,
    decision_comparison: DecisionComparison,
    created_at: str,
    played_analysis: PositionAnalysis | AnalysisFailure | None = None,
) -> tuple[TutorSession, TutorExplanation, dict[str, Any]]:
    """Compose M16 feedback and record it through the qualified M8 transition."""
    feedback = compose_grounded_mentor_feedback(
        session=session,
        root_analysis=root_analysis,
        decision_comparison=decision_comparison,
        played_analysis=played_analysis,
        created_at=created_at,
    )
    provenance = TutorExplanationProvenance(
        actor_kind="template",
        actor_id=_POLICY_ID,
        actor_version=_POLICY_VERSION,
        instruction_fingerprint=feedback["policy"]["fingerprint"],
        run_id=feedback["feedback_id"],
    )
    try:
        updated, explanation = record_tutor_explanation(
            session,
            rendered_content=feedback["rendered_content"],
            provenance=provenance,
            created_at=created_at,
        )
    except TutorSessionError as exc:
        raise GroundedFeedbackError(
            f"M8 explanation transition rejected M16 feedback: {exc}"
        ) from exc
    return updated, explanation, feedback