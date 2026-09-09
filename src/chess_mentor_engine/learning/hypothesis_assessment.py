"""M7C deterministic recurrence assessment and rebuildable ledger state."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import canonical_json

from .assessment_model import (
    AssessmentStatus,
    DiscrepancyCode,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
)
from .hypothesis_assessment_model import (
    AuthorityLifecycleState,
    CompetingExplanationReview,
    CompetingExplanationReviewState,
    ContextMatchRule,
    ContradictionRule,
    HypothesisAssessment,
    HypothesisAssessmentPolicy,
    HypothesisAssessmentPolicyRef,
    HypothesisAssessmentRef,
    HypothesisAssessmentStatus,
    HypothesisEvidenceLinkRef,
    HypothesisEvidenceSummary,
    HypothesisLedgerEntry,
    HypothesisLedgerSnapshot,
    HypothesisLifecycleEventRef,
    HypothesisRecurrenceUnit,
    IndependenceRule,
    M6PolicyCompatibilityRule,
    StageCompatibilityRule,
)
from .hypothesis_model import (
    HypothesisActorProvenance,
    HypothesisContextRef,
    HypothesisEvidenceLink,
    HypothesisLifecycleEvent,
    HypothesisRevision,
    HypothesisRevisionRef,
    LearnerHypothesis,
    LearnerHypothesisRef,
)
from .model import MeasurementCondition

_M6_STATUSES: frozenset[str] = frozenset(
    {"discrepancy_supported", "no_supported_discrepancy", "unclear", "unscorable"}
)
_DISCREPANCY_CODES: frozenset[str] = frozenset(
    {
        "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED",
        "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
        "EXPECTED_OPPONENT_REPLY_CONFLICT",
        "EXPECTED_CONTINUATION_CONFLICT",
        "REPORTED_RESULTING_EVALUATION_CONFLICT",
        "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE",
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        "OTHER_LOCAL_DISCREPANCY",
    }
)
_MEASUREMENT_CONDITIONS: frozenset[str] = frozenset(
    {"clean", "instrument_aware_clean", "deviating", "contaminated", "unknown"}
)
_M6_POLICY_RULES = frozenset(
    {"same_policy_fingerprint", "declared_policy_fingerprints"}
)
_STAGE_RULES = frozenset({"same_assessed_stage_ids", "declared_stage_ids"})
_CONTEXT_RULES = frozenset(
    {"exact_revision_contexts", "shared_revision_context", "broad_scope"}
)
_INDEPENDENCE_RULES = frozenset({"distinct_game_id", "distinct_position_id"})
_CONTRADICTION_RULES = frozenset(
    {"any_contradiction", "any_contradiction_or_counterexample"}
)
_LINK_RELATIONS = frozenset(
    {"supports", "contradicts", "successful_counterexample", "context_exception", "unclear"}
)


class HypothesisAssessmentError(ValueError):
    """Raised when M7C policy, provenance, aggregation, or snapshot invariants fail."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise HypothesisAssessmentError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HypothesisAssessmentError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HypothesisAssessmentError("timestamp must include an explicit timezone")
    return parsed


def _hypothesis_ref(hypothesis: LearnerHypothesis) -> LearnerHypothesisRef:
    return LearnerHypothesisRef(
        hypothesis_id=hypothesis.hypothesis_id,
        participant_id=hypothesis.participant_id,
        fingerprint=hypothesis.fingerprint,
    )


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _link_ref(link: HypothesisEvidenceLink) -> HypothesisEvidenceLinkRef:
    return HypothesisEvidenceLinkRef(link_id=link.link_id, fingerprint=link.fingerprint)


def _policy_ref(policy: HypothesisAssessmentPolicy) -> HypothesisAssessmentPolicyRef:
    return HypothesisAssessmentPolicyRef(
        assessment_policy_id=policy.assessment_policy_id,
        version=policy.version,
        fingerprint=policy.policy_fingerprint,
    )


def _assessment_ref(assessment: HypothesisAssessment) -> HypothesisAssessmentRef:
    return HypothesisAssessmentRef(
        hypothesis_assessment_id=assessment.hypothesis_assessment_id,
        hypothesis_revision_ref=assessment.hypothesis_revision_ref,
        assessment_policy_ref=assessment.assessment_policy_ref,
        status=assessment.status,
        fingerprint=assessment.fingerprint,
    )


def _lifecycle_ref(event: HypothesisLifecycleEvent) -> HypothesisLifecycleEventRef:
    return HypothesisLifecycleEventRef(
        lifecycle_event_id=event.lifecycle_event_id,
        fingerprint=event.fingerprint,
        kind=event.kind,
    )


def _validate_hypothesis(hypothesis: LearnerHypothesis) -> None:
    expected = _fingerprint(hypothesis.to_dict(include_identity=False))
    if expected != hypothesis.fingerprint:
        raise HypothesisAssessmentError("LearnerHypothesis fingerprint mismatch")
    if hypothesis.hypothesis_id != f"learner_hypothesis_{expected[:20]}":
        raise HypothesisAssessmentError("LearnerHypothesis identity mismatch")
    _parse_timestamp(hypothesis.created_at)


def _validate_revision(revision: HypothesisRevision) -> None:
    expected = _fingerprint(revision.to_dict(include_identity=False))
    if expected != revision.fingerprint:
        raise HypothesisAssessmentError("HypothesisRevision fingerprint mismatch")
    if revision.revision_id != f"hypothesis_revision_{expected[:20]}":
        raise HypothesisAssessmentError("HypothesisRevision identity mismatch")
    if revision.claim_kind != "descriptive_pattern":
        raise HypothesisAssessmentError("M7C accepts only descriptive_pattern revisions")
    _parse_timestamp(revision.created_at)


def _validate_revision_chain(
    hypothesis: LearnerHypothesis,
    revisions: tuple[HypothesisRevision, ...],
) -> tuple[HypothesisRevision, ...]:
    _validate_hypothesis(hypothesis)
    if not revisions:
        raise HypothesisAssessmentError("hypothesis must have at least one revision")
    ordered = tuple(sorted(revisions, key=lambda item: item.revision_number))
    if tuple(item.revision_number for item in ordered) != tuple(
        range(1, len(ordered) + 1)
    ):
        raise HypothesisAssessmentError("revision history must be contiguous from 1")
    previous: HypothesisRevision | None = None
    for revision in ordered:
        _validate_revision(revision)
        if revision.hypothesis_id != hypothesis.hypothesis_id:
            raise HypothesisAssessmentError("revision belongs to another hypothesis")
        if previous is None:
            if revision.parent_revision_ref is not None:
                raise HypothesisAssessmentError("revision 1 must not cite a parent")
        else:
            if revision.parent_revision_ref != _revision_ref(previous):
                raise HypothesisAssessmentError(
                    "revision parent does not match exact previous revision"
                )
            if _parse_timestamp(revision.created_at) < _parse_timestamp(previous.created_at):
                raise HypothesisAssessmentError("revision history must be chronological")
        previous = revision
    return ordered


def _validate_link(link: HypothesisEvidenceLink) -> None:
    expected = _fingerprint(link.to_dict(include_identity=False))
    if expected != link.fingerprint:
        raise HypothesisAssessmentError("HypothesisEvidenceLink fingerprint mismatch")
    if link.link_id != f"hypothesis_evidence_{expected[:20]}":
        raise HypothesisAssessmentError("HypothesisEvidenceLink identity mismatch")
    if link.relation not in _LINK_RELATIONS:
        raise HypothesisAssessmentError("unknown hypothesis evidence relation")
    if link.measurement_condition not in _MEASUREMENT_CONDITIONS:
        raise HypothesisAssessmentError("unknown hypothesis measurement condition")
    _parse_timestamp(link.created_at)


def _validate_m6_assessment(assessment: ReasoningDiscrepancyAssessment) -> None:
    expected = _fingerprint(assessment.to_dict(include_identity=False))
    if expected != assessment.fingerprint:
        raise HypothesisAssessmentError("M6 assessment fingerprint mismatch")
    if assessment.assessment_id != f"reasoning_assessment_{expected[:20]}":
        raise HypothesisAssessmentError("M6 assessment identity mismatch")
    if assessment.status not in _M6_STATUSES:
        raise HypothesisAssessmentError("unknown M6 assessment status")
    if assessment.measurement_condition not in _MEASUREMENT_CONDITIONS:
        raise HypothesisAssessmentError("unknown M6 assessment measurement condition")
    _parse_timestamp(assessment.created_at)


def _validate_m6_assertion(assertion: ReasoningDiscrepancyAssertion) -> None:
    expected = _fingerprint(assertion.to_dict(include_identity=False))
    if expected != assertion.fingerprint:
        raise HypothesisAssessmentError("M6 assertion fingerprint mismatch")
    if assertion.assertion_id != f"reasoning_assertion_{expected[:20]}":
        raise HypothesisAssessmentError("M6 assertion identity mismatch")
    if assertion.code not in _DISCREPANCY_CODES:
        raise HypothesisAssessmentError("unknown M6 discrepancy code")


def _validate_lifecycle_event(
    hypothesis: LearnerHypothesis,
    event: HypothesisLifecycleEvent,
) -> None:
    expected = _fingerprint(event.to_dict(include_identity=False))
    if expected != event.fingerprint:
        raise HypothesisAssessmentError("HypothesisLifecycleEvent fingerprint mismatch")
    if event.lifecycle_event_id != f"hypothesis_lifecycle_{expected[:20]}":
        raise HypothesisAssessmentError("HypothesisLifecycleEvent identity mismatch")
    if event.hypothesis_ref != _hypothesis_ref(hypothesis):
        raise HypothesisAssessmentError("lifecycle event cites a different hypothesis")
    if event.kind not in {"retired", "superseded"}:
        raise HypothesisAssessmentError("unknown lifecycle event kind")
    _parse_timestamp(event.created_at)


def _validate_policy(policy: HypothesisAssessmentPolicy) -> None:
    expected = _fingerprint(policy.to_dict(include_identity=False))
    if expected != policy.policy_fingerprint:
        raise HypothesisAssessmentError("HypothesisAssessmentPolicy fingerprint mismatch")
    if not set(policy.eligible_m6_statuses).issubset(_M6_STATUSES):
        raise HypothesisAssessmentError("policy contains unknown M6 status")
    if not set(policy.eligible_discrepancy_codes).issubset(_DISCREPANCY_CODES):
        raise HypothesisAssessmentError("policy contains unknown discrepancy code")
    if not set(policy.allowed_measurement_conditions).issubset(_MEASUREMENT_CONDITIONS):
        raise HypothesisAssessmentError("policy contains unknown measurement condition")
    if policy.m6_policy_compatibility_rule not in _M6_POLICY_RULES:
        raise HypothesisAssessmentError("unknown M6 policy compatibility rule")
    if policy.stage_compatibility_rule not in _STAGE_RULES:
        raise HypothesisAssessmentError("unknown stage compatibility rule")
    if policy.context_match_rule not in _CONTEXT_RULES:
        raise HypothesisAssessmentError("unknown context match rule")
    if policy.recurrence_unit_rule != "participant_position":
        raise HypothesisAssessmentError("unknown recurrence unit rule")
    if policy.independence_rule not in _INDEPENDENCE_RULES:
        raise HypothesisAssessmentError("unknown independence rule")
    if policy.contradiction_rule not in _CONTRADICTION_RULES:
        raise HypothesisAssessmentError("unknown contradiction rule")


def _validate_hypothesis_assessment(assessment: HypothesisAssessment) -> None:
    expected = _fingerprint(assessment.to_dict(include_identity=False))
    if expected != assessment.fingerprint:
        raise HypothesisAssessmentError("HypothesisAssessment fingerprint mismatch")
    if assessment.hypothesis_assessment_id != f"hypothesis_assessment_{expected[:20]}":
        raise HypothesisAssessmentError("HypothesisAssessment identity mismatch")
    _parse_timestamp(assessment.created_at)


def define_hypothesis_assessment_policy(
    *,
    assessment_policy_id: str,
    version: str,
    eligible_m6_statuses: tuple[AssessmentStatus, ...],
    eligible_discrepancy_codes: tuple[DiscrepancyCode, ...],
    allowed_measurement_conditions: tuple[MeasurementCondition, ...],
    m6_policy_compatibility_rule: M6PolicyCompatibilityRule,
    stage_compatibility_rule: StageCompatibilityRule,
    context_match_rule: ContextMatchRule,
    independence_rule: IndependenceRule,
    minimum_independent_supports_for_candidate: int,
    minimum_independent_supports_for_supported: int,
    required_contradiction_review: bool = True,
    required_counterexample_review: bool = True,
    required_competing_explanation_review: bool = True,
    contradiction_rule: ContradictionRule = "any_contradiction",
    compatible_m6_policy_fingerprints: tuple[str, ...] = (),
    allowed_stage_ids: tuple[str, ...] = (),
) -> HypothesisAssessmentPolicy:
    """Create one exact material M7C recurrence policy; no thresholds are implicit."""

    statuses = tuple(sorted(eligible_m6_statuses))
    codes = tuple(sorted(eligible_discrepancy_codes))
    conditions = tuple(sorted(allowed_measurement_conditions))
    compatible_policies = tuple(sorted(compatible_m6_policy_fingerprints))
    stages = tuple(sorted(allowed_stage_ids))
    payload: dict[str, Any] = {
        "assessment_policy_id": assessment_policy_id,
        "version": version,
        "eligible_m6_statuses": list(statuses),
        "eligible_discrepancy_codes": list(codes),
        "allowed_measurement_conditions": list(conditions),
        "m6_policy_compatibility_rule": m6_policy_compatibility_rule,
        "compatible_m6_policy_fingerprints": list(compatible_policies),
        "stage_compatibility_rule": stage_compatibility_rule,
        "allowed_stage_ids": list(stages),
        "context_match_rule": context_match_rule,
        "recurrence_unit_rule": "participant_position",
        "independence_rule": independence_rule,
        "minimum_independent_supports_for_candidate": (
            minimum_independent_supports_for_candidate
        ),
        "minimum_independent_supports_for_supported": (
            minimum_independent_supports_for_supported
        ),
        "required_contradiction_review": required_contradiction_review,
        "required_counterexample_review": required_counterexample_review,
        "required_competing_explanation_review": required_competing_explanation_review,
        "contradiction_rule": contradiction_rule,
        "claim_scope": "participant_specific_cross_position",
    }
    fingerprint = _fingerprint(payload)
    try:
        policy = HypothesisAssessmentPolicy(
            assessment_policy_id=assessment_policy_id,
            version=version,
            policy_fingerprint=fingerprint,
            eligible_m6_statuses=statuses,
            eligible_discrepancy_codes=codes,
            allowed_measurement_conditions=conditions,
            m6_policy_compatibility_rule=m6_policy_compatibility_rule,
            compatible_m6_policy_fingerprints=compatible_policies,
            stage_compatibility_rule=stage_compatibility_rule,
            allowed_stage_ids=stages,
            context_match_rule=context_match_rule,
            recurrence_unit_rule="participant_position",
            independence_rule=independence_rule,
            minimum_independent_supports_for_candidate=(
                minimum_independent_supports_for_candidate
            ),
            minimum_independent_supports_for_supported=(
                minimum_independent_supports_for_supported
            ),
            required_contradiction_review=required_contradiction_review,
            required_counterexample_review=required_counterexample_review,
            required_competing_explanation_review=(
                required_competing_explanation_review
            ),
            contradiction_rule=contradiction_rule,
        )
    except ValueError as exc:
        raise HypothesisAssessmentError(str(exc)) from exc
    _validate_policy(policy)
    return policy


def record_competing_explanation_review(
    *,
    state: CompetingExplanationReviewState,
    review_note: str,
    created_at: str,
    reviewed_hypothesis_refs: tuple[LearnerHypothesisRef, ...] = (),
    reviewed_alternative_notes: tuple[str, ...] = (),
    reviewer_provenance: HypothesisActorProvenance | None = None,
) -> CompetingExplanationReview:
    """Record that alternatives were considered without claiming they were refuted."""

    refs = tuple(
        sorted(
            reviewed_hypothesis_refs,
            key=lambda item: (item.hypothesis_id, item.fingerprint),
        )
    )
    notes = tuple(sorted(reviewed_alternative_notes))
    payload = {
        "state": state,
        "reviewed_hypothesis_refs": [item.to_dict() for item in refs],
        "reviewed_alternative_notes": list(notes),
        "review_note": review_note,
        "reviewer_provenance": (
            None if reviewer_provenance is None else reviewer_provenance.to_dict()
        ),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        review = CompetingExplanationReview(
            review_id=f"hypothesis_competing_review_{fingerprint[:20]}",
            fingerprint=fingerprint,
            state=state,
            reviewed_hypothesis_refs=refs,
            reviewed_alternative_notes=notes,
            review_note=review_note,
            reviewer_provenance=reviewer_provenance,
            created_at=created_at,
        )
    except ValueError as exc:
        raise HypothesisAssessmentError(str(exc)) from exc
    _parse_timestamp(review.created_at)
    return review


def _assessment_key(
    assessment: ReasoningDiscrepancyAssessment,
) -> tuple[str, str]:
    return (assessment.assessment_id, assessment.fingerprint)


def _assertion_key(
    assertion: ReasoningDiscrepancyAssertion,
) -> tuple[str, str]:
    return (assertion.assertion_id, assertion.fingerprint)


def _context_key(ref: HypothesisContextRef) -> tuple[str, str]:
    return (ref.ref_id, ref.fingerprint)


def _independence_unit_id(
    *,
    participant_id: str,
    source_position_id: str,
    source_game_id: str,
    rule: IndependenceRule,
) -> str:
    if rule == "distinct_game_id":
        material = {"participant_id": participant_id, "source_game_id": source_game_id}
        prefix = "hypothesis_independence_game"
    elif rule == "distinct_position_id":
        material = {
            "participant_id": participant_id,
            "source_position_id": source_position_id,
        }
        prefix = "hypothesis_independence_position"
    else:
        raise HypothesisAssessmentError("unsupported independence rule")
    return f"{prefix}_{_fingerprint(material)[:20]}"


def _recurrence_unit_id(participant_id: str, source_position_id: str) -> str:
    material = {
        "participant_id": participant_id,
        "source_position_id": source_position_id,
    }
    return f"hypothesis_recurrence_unit_{_fingerprint(material)[:20]}"


def _review_is_complete(
    revision: HypothesisRevision,
    review: CompetingExplanationReview,
) -> bool:
    if review.state != "completed":
        return False
    revision_refs = {
        (item.hypothesis_id, item.fingerprint)
        for item in revision.competing_hypothesis_refs
    }
    reviewed_refs = {
        (item.hypothesis_id, item.fingerprint)
        for item in review.reviewed_hypothesis_refs
    }
    if not revision_refs.issubset(reviewed_refs):
        return False
    if not set(revision.unresolved_alternative_notes).issubset(
        set(review.reviewed_alternative_notes)
    ):
        return False
    return True


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
) -> HypothesisAssessment:
    """Assess one exact revision over one exact frozen evidence-link set."""

    _validate_hypothesis(hypothesis)
    _validate_revision(revision)
    _validate_policy(policy)
    if revision.hypothesis_id != hypothesis.hypothesis_id:
        raise HypothesisAssessmentError("revision belongs to another hypothesis")
    created = _parse_timestamp(created_at)
    if created < _parse_timestamp(revision.created_at):
        raise HypothesisAssessmentError("assessment cannot predate hypothesis revision")
    if created < _parse_timestamp(competing_explanation_review.created_at):
        raise HypothesisAssessmentError(
            "assessment cannot predate competing-explanation review"
        )

    assessment_map: dict[tuple[str, str], ReasoningDiscrepancyAssessment] = {}
    for item in m6_assessments:
        _validate_m6_assessment(item)
        key = _assessment_key(item)
        if key in assessment_map:
            raise HypothesisAssessmentError("duplicate M6 assessment supplied")
        assessment_map[key] = item

    assertion_map: dict[tuple[str, str], ReasoningDiscrepancyAssertion] = {}
    for item in m6_assertions:
        _validate_m6_assertion(item)
        key = _assertion_key(item)
        if key in assertion_map:
            raise HypothesisAssessmentError("duplicate M6 assertion supplied")
        assertion_map[key] = item

    links = tuple(sorted(evidence_links, key=lambda item: (item.link_id, item.fingerprint)))
    if len({item.link_id for item in links}) != len(links):
        raise HypothesisAssessmentError("evidence links must be unique")

    revision_ref = _revision_ref(revision)
    revision_contexts = {_context_key(item) for item in revision.context_definition_refs}
    if policy.context_match_rule == "broad_scope" and revision_contexts:
        raise HypothesisAssessmentError(
            "broad_scope policy requires a revision with no context_definition_refs"
        )
    if policy.context_match_rule in {"exact_revision_contexts", "shared_revision_context"}:
        if not revision_contexts:
            raise HypothesisAssessmentError(
                "context-bound policy requires revision context_definition_refs"
            )

    prelim: list[
        tuple[
            HypothesisEvidenceLink,
            ReasoningDiscrepancyAssessment,
            tuple[ReasoningDiscrepancyAssertion, ...],
        ]
    ] = []
    exclusions: dict[str, list[str]] = {}

    for link in links:
        _validate_link(link)
        if link.hypothesis_revision_ref != revision_ref:
            raise HypothesisAssessmentError(
                "evidence link belongs to another hypothesis revision"
            )
        if link.participant_id != hypothesis.participant_id:
            raise HypothesisAssessmentError(
                "evidence link participant does not match hypothesis"
            )
        assessment_key = (link.assessment_ref.ref_id, link.assessment_ref.fingerprint)
        assessment = assessment_map.get(assessment_key)
        if assessment is None:
            raise HypothesisAssessmentError(
                "exact M6 assessment referenced by evidence link was not supplied"
            )
        if assessment.measurement_condition != link.measurement_condition:
            raise HypothesisAssessmentError(
                "M6 assessment measurement condition does not match evidence link"
            )
        if assessment.reasoning_context_id != link.reasoning_context_ref.ref_id:
            raise HypothesisAssessmentError(
                "M6 assessment context does not match evidence link"
            )

        exact_assertions: list[ReasoningDiscrepancyAssertion] = []
        assessment_assertion_keys = {
            (item.ref_id, item.fingerprint) for item in assessment.assertion_refs
        }
        for ref in link.assertion_refs:
            key = (ref.ref_id, ref.fingerprint)
            assertion = assertion_map.get(key)
            if assertion is None:
                raise HypothesisAssessmentError(
                    "exact M6 assertion referenced by evidence link was not supplied"
                )
            if assertion.reasoning_context_id != assessment.reasoning_context_id:
                raise HypothesisAssessmentError(
                    "M6 assertion context does not match evidence-link assessment"
                )
            if key not in assessment_assertion_keys:
                raise HypothesisAssessmentError(
                    "M6 assertion is not cited by evidence-link assessment"
                )
            if assertion.assessment_policy_ref != assessment.assessment_policy_ref:
                raise HypothesisAssessmentError(
                    "M6 assertion policy does not match evidence-link assessment"
                )
            exact_assertions.append(assertion)

        reasons: list[str] = []
        if assessment.status not in policy.eligible_m6_statuses:
            reasons.append(f"m6_status_not_eligible:{assessment.status}")
        if link.measurement_condition not in policy.allowed_measurement_conditions:
            reasons.append(
                f"measurement_condition_not_allowed:{link.measurement_condition}"
            )
        if link.relation == "supports" and not exact_assertions:
            reasons.append("support_requires_hypothesis_relevant_assertion")
        ineligible_codes = sorted(
            {
                item.code
                for item in exact_assertions
                if item.code not in policy.eligible_discrepancy_codes
            }
        )
        reasons.extend(
            f"discrepancy_code_not_eligible:{code}" for code in ineligible_codes
        )

        if policy.m6_policy_compatibility_rule == "declared_policy_fingerprints":
            if (
                assessment.assessment_policy_ref.fingerprint
                not in policy.compatible_m6_policy_fingerprints
            ):
                reasons.append("m6_policy_fingerprint_not_declared_compatible")

        if policy.stage_compatibility_rule == "declared_stage_ids":
            allowed_stages = set(policy.allowed_stage_ids)
            if not set(assessment.assessed_stage_ids).issubset(allowed_stages):
                reasons.append("assessment_stage_not_declared_compatible")
            if any(
                not set(item.stage_ids).issubset(allowed_stages)
                for item in exact_assertions
            ):
                reasons.append("assertion_stage_not_declared_compatible")

        link_contexts = {_context_key(item) for item in link.context_refs}
        if policy.context_match_rule == "exact_revision_contexts":
            if link_contexts != revision_contexts:
                reasons.append("context_not_exact_revision_context")
        elif policy.context_match_rule == "shared_revision_context":
            if not link_contexts or not link_contexts.issubset(revision_contexts):
                reasons.append("context_outside_revision_scope")
        elif link_contexts:
            reasons.append("broad_scope_link_must_not_carry_context_refs")

        if reasons:
            exclusions[link.link_id] = sorted(set(reasons))
        else:
            prelim.append((link, assessment, tuple(exact_assertions)))

    if prelim and policy.m6_policy_compatibility_rule == "same_policy_fingerprint":
        fingerprints = {
            assessment.assessment_policy_ref.fingerprint
            for _, assessment, _ in prelim
        }
        if len(fingerprints) != 1:
            for link, _, _ in prelim:
                exclusions.setdefault(link.link_id, []).append(
                    "m6_policy_fingerprint_incompatible_across_evidence_set"
                )
            prelim = []

    if prelim and policy.stage_compatibility_rule == "same_assessed_stage_ids":
        stage_sets = {tuple(assessment.assessed_stage_ids) for _, assessment, _ in prelim}
        if len(stage_sets) != 1:
            for link, _, _ in prelim:
                exclusions.setdefault(link.link_id, []).append(
                    "assessment_stage_incompatible_across_evidence_set"
                )
            prelim = []

    common_context_keys: set[tuple[str, str]] = set()
    if prelim and policy.context_match_rule == "shared_revision_context":
        common_context_keys = {_context_key(item) for item in prelim[0][0].context_refs}
        for link, _, _ in prelim[1:]:
            common_context_keys.intersection_update(
                {_context_key(item) for item in link.context_refs}
            )
        if not common_context_keys:
            for link, _, _ in prelim:
                exclusions.setdefault(link.link_id, []).append(
                    "no_traceable_shared_context_ref"
                )
            prelim = []
    elif policy.context_match_rule == "exact_revision_contexts":
        common_context_keys = set(revision_contexts)

    eligible_links = tuple(item[0] for item in prelim)
    eligible_ids = {item.link_id for item in eligible_links}
    excluded_links = tuple(item for item in links if item.link_id not in eligible_ids)

    groups: dict[str, list[HypothesisEvidenceLink]] = defaultdict(list)
    for link in eligible_links:
        groups[link.source_position_id].append(link)

    recurrence_units: list[HypothesisRecurrenceUnit] = []
    for source_position_id in sorted(groups):
        group = tuple(
            sorted(groups[source_position_id], key=lambda item: (item.link_id, item.fingerprint))
        )
        game_ids = {item.source_game_id for item in group}
        if len(game_ids) != 1:
            raise HypothesisAssessmentError(
                "one participant-position recurrence unit cannot span multiple game IDs"
            )
        source_game_id = next(iter(game_ids))
        relations = {item.relation for item in group}
        relation = next(iter(relations)) if len(relations) == 1 else "mixed"
        contexts_by_key: dict[tuple[str, str], HypothesisContextRef] = {}
        for item in group:
            for ref in item.context_refs:
                contexts_by_key[_context_key(ref)] = ref
        conditions = tuple(sorted({item.measurement_condition for item in group}))
        unit = HypothesisRecurrenceUnit(
            recurrence_unit_id=_recurrence_unit_id(
                hypothesis.participant_id, source_position_id
            ),
            participant_id=hypothesis.participant_id,
            source_position_id=source_position_id,
            source_game_id=source_game_id,
            relation=relation,
            link_refs=tuple(_link_ref(item) for item in group),
            independence_unit_id=_independence_unit_id(
                participant_id=hypothesis.participant_id,
                source_position_id=source_position_id,
                source_game_id=source_game_id,
                rule=policy.independence_rule,
            ),
            context_refs=tuple(
                contexts_by_key[key] for key in sorted(contexts_by_key)
            ),
            measurement_conditions=conditions,
        )
        recurrence_units.append(unit)

    units = tuple(recurrence_units)
    support_units = tuple(item for item in units if item.relation == "supports")
    contradiction_units = tuple(item for item in units if item.relation == "contradicts")
    counterexample_units = tuple(
        item for item in units if item.relation == "successful_counterexample"
    )
    exception_units = tuple(item for item in units if item.relation == "context_exception")
    unclear_units = tuple(item for item in units if item.relation == "unclear")
    mixed_units = tuple(item for item in units if item.relation == "mixed")
    independent_support_ids = {
        item.independence_unit_id for item in support_units
    }

    relation_refs: dict[str, tuple[HypothesisEvidenceLinkRef, ...]] = {}
    for relation in _LINK_RELATIONS:
        relation_refs[relation] = tuple(
            _link_ref(item) for item in eligible_links if item.relation == relation
        )

    common_context_by_key: dict[tuple[str, str], HypothesisContextRef] = {
        _context_key(item): item for item in revision.context_definition_refs
    }
    common_context_refs = tuple(
        common_context_by_key[key] for key in sorted(common_context_keys)
    )
    source_position_ids = tuple(item.source_position_id for item in units)
    source_game_ids = tuple(sorted({item.source_game_id for item in units}))
    measurement_conditions = tuple(
        sorted({condition for item in units for condition in item.measurement_conditions})
    )
    exclusion_reasons = tuple(
        (link_id, tuple(sorted(set(reasons))))
        for link_id, reasons in sorted(exclusions.items())
    )
    summary = HypothesisEvidenceSummary(
        eligible_link_count=len(eligible_links),
        excluded_link_count=len(excluded_links),
        support_unit_count=len(support_units),
        independent_support_count=len(independent_support_ids),
        contradiction_unit_count=len(contradiction_units),
        successful_counterexample_unit_count=len(counterexample_units),
        context_exception_unit_count=len(exception_units),
        unclear_unit_count=len(unclear_units),
        mixed_unit_count=len(mixed_units),
        source_position_ids=source_position_ids,
        source_game_ids=source_game_ids,
        measurement_conditions=measurement_conditions,
        common_context_refs=common_context_refs,
        excluded_link_refs=tuple(_link_ref(item) for item in excluded_links),
        exclusion_reasons=exclusion_reasons,
    )

    review_complete = _review_is_complete(revision, competing_explanation_review)
    status_reasons: list[str] = []
    status: HypothesisAssessmentStatus

    contradiction_met = bool(contradiction_units)
    if policy.contradiction_rule == "any_contradiction_or_counterexample":
        contradiction_met = contradiction_met or bool(counterexample_units)

    if not eligible_links:
        status = "insufficient"
        status_reasons.append("no_policy_eligible_evidence_links")
    elif mixed_units:
        status = "unclear"
        status_reasons.append("conflicting_relations_within_recurrence_unit")
    elif contradiction_met:
        status = "contradicted"
        status_reasons.append(f"contradiction_rule_met:{policy.contradiction_rule}")
    elif len(support_units) == 0:
        if unclear_units or counterexample_units or exception_units:
            status = "unclear"
            status_reasons.append("no_supporting_unit_with_material_non_support_evidence")
        else:
            status = "insufficient"
            status_reasons.append("no_supporting_recurrence_unit")
    elif len(support_units) == 1:
        status = "isolated"
        status_reasons.append("exactly_one_supporting_recurrence_unit")
    elif len(independent_support_ids) < policy.minimum_independent_supports_for_candidate:
        status = "insufficient"
        status_reasons.append("independence_threshold_for_candidate_not_met")
    else:
        supported_gates: list[str] = []
        if len(independent_support_ids) < policy.minimum_independent_supports_for_supported:
            supported_gates.append("supported_independent_support_threshold_not_met")
        if unclear_units:
            supported_gates.append("unclear_evidence_present")
        if exception_units:
            supported_gates.append("context_exception_present")
        if policy.required_competing_explanation_review and not review_complete:
            supported_gates.append("competing_explanation_review_incomplete")
        if policy.required_contradiction_review:
            status_reasons.append("contradiction_links_in_exact_evidence_set_reviewed")
        if policy.required_counterexample_review:
            status_reasons.append("counterexample_links_in_exact_evidence_set_reviewed")
        if supported_gates:
            status = "candidate_recurrence"
            status_reasons.extend(supported_gates)
        else:
            status = "supported_recurrence"
            status_reasons.append("all_supported_recurrence_policy_gates_met")

    if policy.required_competing_explanation_review and review_complete:
        status_reasons.append("competing_explanation_review_completed")
    if excluded_links:
        status_reasons.append("some_links_excluded_by_policy")

    payload: dict[str, Any] = {
        "hypothesis_revision_ref": revision_ref.to_dict(),
        "assessment_policy_ref": _policy_ref(policy).to_dict(),
        "status": status,
        "support_link_refs": [item.to_dict() for item in relation_refs["supports"]],
        "contradiction_link_refs": [
            item.to_dict() for item in relation_refs["contradicts"]
        ],
        "successful_counterexample_link_refs": [
            item.to_dict() for item in relation_refs["successful_counterexample"]
        ],
        "context_exception_link_refs": [
            item.to_dict() for item in relation_refs["context_exception"]
        ],
        "unclear_link_refs": [item.to_dict() for item in relation_refs["unclear"]],
        "recurrence_units": [item.to_dict() for item in units],
        "recurrence_unit_ids": [item.recurrence_unit_id for item in units],
        "independence_unit_ids": sorted(
            {item.independence_unit_id for item in units}
        ),
        "source_position_ids": list(source_position_ids),
        "source_game_ids": list(source_game_ids),
        "measurement_conditions": list(measurement_conditions),
        "competing_explanation_review": competing_explanation_review.to_dict(),
        "evidence_summary": summary.to_dict(),
        "status_reasons": sorted(set(status_reasons)),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        result = HypothesisAssessment(
            hypothesis_assessment_id=f"hypothesis_assessment_{fingerprint[:20]}",
            fingerprint=fingerprint,
            hypothesis_revision_ref=revision_ref,
            assessment_policy_ref=_policy_ref(policy),
            status=status,
            support_link_refs=relation_refs["supports"],
            contradiction_link_refs=relation_refs["contradicts"],
            successful_counterexample_link_refs=relation_refs[
                "successful_counterexample"
            ],
            context_exception_link_refs=relation_refs["context_exception"],
            unclear_link_refs=relation_refs["unclear"],
            recurrence_units=units,
            recurrence_unit_ids=tuple(item.recurrence_unit_id for item in units),
            independence_unit_ids=tuple(
                sorted({item.independence_unit_id for item in units})
            ),
            source_position_ids=source_position_ids,
            source_game_ids=source_game_ids,
            measurement_conditions=measurement_conditions,
            competing_explanation_review=competing_explanation_review,
            evidence_summary=summary,
            status_reasons=tuple(sorted(set(status_reasons))),
            created_at=created_at,
        )
    except ValueError as exc:
        raise HypothesisAssessmentError(str(exc)) from exc
    _validate_hypothesis_assessment(result)
    return result


def build_hypothesis_ledger_snapshot(
    *,
    participant_id: str,
    hypotheses: tuple[LearnerHypothesis, ...],
    revisions: tuple[HypothesisRevision, ...],
    assessments: tuple[HypothesisAssessment, ...],
    lifecycle_events: tuple[HypothesisLifecycleEvent, ...],
    created_at: str,
) -> HypothesisLedgerSnapshot:
    """Rebuild current participant ledger state without mutating historical records."""

    if not participant_id:
        raise HypothesisAssessmentError("participant_id must not be empty")
    created = _parse_timestamp(created_at)
    ordered_hypotheses = tuple(
        sorted(hypotheses, key=lambda item: (item.hypothesis_id, item.fingerprint))
    )
    if len({item.hypothesis_id for item in ordered_hypotheses}) != len(ordered_hypotheses):
        raise HypothesisAssessmentError("hypotheses must be unique")
    for hypothesis in ordered_hypotheses:
        _validate_hypothesis(hypothesis)
        if hypothesis.participant_id != participant_id:
            raise HypothesisAssessmentError(
                "snapshot cannot mix participant-specific hypotheses"
            )
        if _parse_timestamp(hypothesis.created_at) > created:
            raise HypothesisAssessmentError("snapshot cannot predate hypothesis creation")

    revisions_by_hypothesis: dict[str, list[HypothesisRevision]] = defaultdict(list)
    for revision in revisions:
        revisions_by_hypothesis[revision.hypothesis_id].append(revision)

    assessment_by_revision: dict[str, list[HypothesisAssessment]] = defaultdict(list)
    for assessment in assessments:
        _validate_hypothesis_assessment(assessment)
        if _parse_timestamp(assessment.created_at) > created:
            raise HypothesisAssessmentError("snapshot cannot predate assessment")
        assessment_by_revision[assessment.hypothesis_revision_ref.revision_id].append(
            assessment
        )

    events_by_hypothesis: dict[str, list[HypothesisLifecycleEvent]] = defaultdict(list)
    hypothesis_map = {item.hypothesis_id: item for item in ordered_hypotheses}
    for event in lifecycle_events:
        hypothesis = hypothesis_map.get(event.hypothesis_ref.hypothesis_id)
        if hypothesis is None:
            raise HypothesisAssessmentError(
                "lifecycle event belongs to a hypothesis outside snapshot"
            )
        _validate_lifecycle_event(hypothesis, event)
        if _parse_timestamp(event.created_at) > created:
            raise HypothesisAssessmentError("snapshot cannot predate lifecycle event")
        events_by_hypothesis[hypothesis.hypothesis_id].append(event)

    entries: list[HypothesisLedgerEntry] = []
    for hypothesis in ordered_hypotheses:
        chain = _validate_revision_chain(
            hypothesis,
            tuple(revisions_by_hypothesis.get(hypothesis.hypothesis_id, ())),
        )
        current_revision = chain[-1]
        current_ref = _revision_ref(current_revision)

        current_assessments = assessment_by_revision.get(current_revision.revision_id, [])
        for assessment in current_assessments:
            if assessment.hypothesis_revision_ref != current_ref:
                raise HypothesisAssessmentError(
                    "assessment revision ref does not match exact current revision"
                )
        latest_assessment = (
            max(
                current_assessments,
                key=lambda item: (
                    _parse_timestamp(item.created_at),
                    item.hypothesis_assessment_id,
                ),
            )
            if current_assessments
            else None
        )

        events = events_by_hypothesis.get(hypothesis.hypothesis_id, [])
        if len(events) > 1:
            raise HypothesisAssessmentError(
                "M7B terminal lifecycle permits at most one lifecycle event"
            )
        lifecycle_state: AuthorityLifecycleState = "active"
        latest_event: HypothesisLifecycleEvent | None = None
        if events:
            latest_event = events[0]
            lifecycle_state = latest_event.kind

        entry = HypothesisLedgerEntry(
            hypothesis_ref=_hypothesis_ref(hypothesis),
            current_revision_ref=current_ref,
            latest_assessment_ref=(
                None if latest_assessment is None else _assessment_ref(latest_assessment)
            ),
            authority_lifecycle_state=lifecycle_state,
            latest_lifecycle_event_ref=(
                None if latest_event is None else _lifecycle_ref(latest_event)
            ),
        )
        entries.append(entry)

    ordered_entries = tuple(
        sorted(entries, key=lambda item: item.hypothesis_ref.hypothesis_id)
    )
    payload = {
        "participant_id": participant_id,
        "entries": [item.to_dict() for item in ordered_entries],
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        snapshot = HypothesisLedgerSnapshot(
            snapshot_id=f"hypothesis_ledger_snapshot_{fingerprint[:20]}",
            fingerprint=fingerprint,
            participant_id=participant_id,
            entries=ordered_entries,
            created_at=created_at,
        )
    except ValueError as exc:
        raise HypothesisAssessmentError(str(exc)) from exc
    expected = _fingerprint(snapshot.to_dict(include_identity=False))
    if expected != snapshot.fingerprint:
        raise HypothesisAssessmentError("HypothesisLedgerSnapshot fingerprint mismatch")
    return snapshot
