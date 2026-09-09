from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisAssessmentError,
    HypothesisContextRef,
    HypothesisMappingProvenance,
    ReasoningArtifactRef,
    ReasoningAssessmentPolicyRef,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
    ReasoningDiscrepancyContext,
    ReasoningEvidenceRef,
    assess_hypothesis_recurrence,
    create_learner_hypothesis,
    define_hypothesis_assessment_policy,
    record_competing_explanation_review,
    record_hypothesis_evidence_link,
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


def _mapping() -> HypothesisMappingProvenance:
    return HypothesisMappingProvenance(
        basis_kind="deterministic_mapping",
        ref_id="m7-map-1",
        fingerprint=_fingerprint({"mapping": "m7-map-1"}),
    )


def _evidence_ref(authority: str, kind: str, ref_id: str) -> ReasoningEvidenceRef:
    return ReasoningEvidenceRef(
        authority=authority,  # type: ignore[arg-type]
        kind=kind,  # type: ignore[arg-type]
        ref_id=ref_id,
        fingerprint=_fingerprint({"ref": ref_id}),
    )


def _stamp_context(base: ReasoningDiscrepancyContext) -> ReasoningDiscrepancyContext:
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        reasoning_context_id=f"reasoning_context_{fingerprint[:20]}",
        context_fingerprint=fingerprint,
    )


def _make_context(
    *,
    index: int,
    game_id: str,
    stage_ids: tuple[str, ...] = ("stage-a1",),
    condition: str = "clean",
) -> ReasoningDiscrepancyContext:
    position_id = f"position-{index}"
    return _stamp_context(
        ReasoningDiscrepancyContext(
            reasoning_context_id="pending",
            context_fingerprint="pending",
            participant_id="P01",
            player_decision_context_ref=_evidence_ref(
                "m5_participant",
                "player_decision_context",
                f"pdc-{index}",
            ),
            position_id=position_id,
            game_id=game_id,
            diagnostic_candidate_ref=_evidence_ref(
                "m4_objective",
                "diagnostic_candidate",
                f"candidate-{index}",
            ),
            diagnostic_batch_ref=None,
            capture_session_ref=_evidence_ref(
                "m5_participant",
                "capture_session",
                f"capture-{index}",
            ),
            assessment_stage_ids=stage_ids,
            player_response_refs=(
                _evidence_ref(
                    "m5_participant",
                    "player_response",
                    f"response-{index}",
                ),
            ),
            evidence_freeze_refs=(
                _evidence_ref(
                    "m5_participant",
                    "evidence_freeze",
                    f"freeze-{index}",
                ),
            ),
            prompt_presentation_refs=(
                _evidence_ref(
                    "m5_participant",
                    "prompt_presentation",
                    f"prompt-{index}",
                ),
            ),
            exposure_refs=(),
            protocol_deviation_refs=(),
            canonical_position_ref=_evidence_ref(
                "deterministic_chess",
                "canonical_position",
                position_id,
            ),
            position_feature_packet_ref=None,
            position_analysis_refs=(
                _evidence_ref(
                    "engine_evidence",
                    "position_analysis",
                    f"analysis-{index}",
                ),
            ),
            decision_comparison_ref=_evidence_ref(
                "m4_objective",
                "decision_comparison",
                f"comparison-{index}",
            ),
            selection_signal_refs=(),
            measurement_condition=condition,  # type: ignore[arg-type]
            created_at="2026-09-09T01:00:00+00:00",
        )
    )


def _stamp_assertion(
    base: ReasoningDiscrepancyAssertion,
) -> ReasoningDiscrepancyAssertion:
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        assertion_id=f"reasoning_assertion_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _stamp_assessment(
    base: ReasoningDiscrepancyAssessment,
) -> ReasoningDiscrepancyAssessment:
    fingerprint = _fingerprint(base.to_dict(include_identity=False))
    return replace(
        base,
        assessment_id=f"reasoning_assessment_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _make_m6(
    *,
    index: int,
    game_id: str,
    stage_ids: tuple[str, ...] = ("stage-a1",),
    condition: str = "clean",
    status: str = "discrepancy_supported",
    policy_fingerprint: str = "m6-policy-a",
    with_assertion: bool = True,
):
    context = _make_context(
        index=index,
        game_id=game_id,
        stage_ids=stage_ids,
        condition=condition,
    )
    policy_ref = ReasoningAssessmentPolicyRef(
        policy_id=f"m6-{policy_fingerprint}",
        version="1",
        fingerprint=_fingerprint({"policy": policy_fingerprint}),
    )
    assertions: tuple[ReasoningDiscrepancyAssertion, ...] = ()
    facts: tuple[ReasoningArtifactRef, ...] = ()
    if with_assertion:
        fact = ReasoningArtifactRef(
            kind="discrepancy_fact",
            ref_id=f"fact-{index}",
            fingerprint=_fingerprint({"fact": index}),
        )
        assertion = _stamp_assertion(
            ReasoningDiscrepancyAssertion(
                assertion_id="pending",
                fingerprint="pending",
                reasoning_context_id=context.reasoning_context_id,
                assessment_policy_ref=policy_ref,
                code="EXPECTED_OPPONENT_REPLY_CONFLICT",
                statement="Expected reply conflicts with qualified evidence.",
                stage_ids=stage_ids,
                supporting_fact_refs=(fact,),
                supporting_coding_refs=(),
                contradictory_evidence_refs=(),
                basis_kind="deterministic",
            )
        )
        assertions = (assertion,)
        facts = (fact,)
    assertion_refs = tuple(
        ReasoningArtifactRef(
            kind="discrepancy_assertion",
            ref_id=item.assertion_id,
            fingerprint=item.fingerprint,
        )
        for item in assertions
    )
    assessment = _stamp_assessment(
        ReasoningDiscrepancyAssessment(
            assessment_id="pending",
            fingerprint="pending",
            reasoning_context_id=context.reasoning_context_id,
            assessment_policy_ref=policy_ref,
            status=status,  # type: ignore[arg-type]
            assessed_stage_ids=stage_ids,
            assertion_refs=assertion_refs,
            fact_refs=facts,
            coding_refs=(),
            contradictory_evidence_refs=(),
            measurement_condition=condition,  # type: ignore[arg-type]
            status_reasons=("fixture",),
            created_at="2026-09-09T02:00:00+00:00",
        )
    )
    return context, assessment, assertions


def _make_hypothesis(*, broad: bool = False):
    contexts = ()
    if not broad:
        contexts = (
            HypothesisContextRef(
                ref_id="forcing-reply-context",
                fingerprint=_fingerprint({"context": "forcing-reply"}),
            ),
        )
    return create_learner_hypothesis(
        participant_id="P01",
        statement="In forcing-reply positions, the strongest reply is often omitted.",
        scope_definition=(
            "all sampled positions" if broad else "forcing-reply positions"
        ),
        context_definition_refs=contexts,
        origin_provenance=_actor(),
        created_at="2026-09-09T03:00:00+00:00",
    )


def _make_link(
    *,
    hypothesis,
    revision,
    index: int,
    relation: str,
    game_id: str,
    stage_ids: tuple[str, ...] = ("stage-a1",),
    condition: str = "clean",
    status: str = "discrepancy_supported",
    policy_fingerprint: str = "m6-policy-a",
    with_assertion: bool = True,
):
    context, assessment, assertions = _make_m6(
        index=index,
        game_id=game_id,
        stage_ids=stage_ids,
        condition=condition,
        status=status,
        policy_fingerprint=policy_fingerprint,
        with_assertion=with_assertion,
    )
    link = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation=relation,  # type: ignore[arg-type]
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        context_refs=revision.context_definition_refs,
        created_at="2026-09-09T04:00:00+00:00",
    )
    return link, assessment, assertions


def _policy(**overrides):
    values = {
        "assessment_policy_id": "hap-1",
        "version": "1",
        "eligible_m6_statuses": (
            "discrepancy_supported",
            "no_supported_discrepancy",
            "unclear",
        ),
        "eligible_discrepancy_codes": ("EXPECTED_OPPONENT_REPLY_CONFLICT",),
        "allowed_measurement_conditions": ("clean", "instrument_aware_clean"),
        "m6_policy_compatibility_rule": "same_policy_fingerprint",
        "stage_compatibility_rule": "same_assessed_stage_ids",
        "context_match_rule": "exact_revision_contexts",
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


def _review(revision, *, completed: bool = True):
    return record_competing_explanation_review(
        state="completed" if completed else "not_required",
        reviewed_hypothesis_refs=revision.competing_hypothesis_refs,
        reviewed_alternative_notes=revision.unresolved_alternative_notes,
        review_note="Alternatives reviewed without causal resolution.",
        reviewer_provenance=_actor("reviewer") if completed else None,
        created_at="2026-09-09T05:00:00+00:00",
    )


def _assess(hypothesis, revision, policy, units, *, review=None):
    links = tuple(item[0] for item in units)
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
    return assess_hypothesis_recurrence(
        hypothesis=hypothesis,
        revision=revision,
        policy=policy,
        evidence_links=links,
        m6_assessments=assessments,
        m6_assertions=assertions,
        competing_explanation_review=review or _review(revision),
        created_at="2026-09-09T06:00:00+00:00",
    )


def _support_units(hypothesis, revision, count: int):
    return tuple(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=index,
            relation="supports",
            game_id=f"g{index}",
        )
        for index in range(1, count + 1)
    )


def _retag_link(unit, relation: str, mapping_id: str):
    link, assessment, assertions = unit
    mapping = HypothesisMappingProvenance(
        basis_kind="deterministic_mapping",
        ref_id=mapping_id,
        fingerprint=_fingerprint({"mapping": mapping_id}),
    )
    changed = replace(link, relation=relation, mapping_provenance=mapping)
    fingerprint = _fingerprint(changed.to_dict(include_identity=False))
    changed = replace(
        changed,
        link_id=f"hypothesis_evidence_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )
    return changed, assessment, assertions


def test_policy_identity_is_deterministic_and_threshold_is_explicit() -> None:
    first = _policy()
    second = _policy()
    assert first == second
    assert first.minimum_independent_supports_for_candidate == 2
    with pytest.raises(HypothesisAssessmentError, match="at least 2"):
        _policy(minimum_independent_supports_for_candidate=1)


def test_one_support_is_isolated_not_recurrence() -> None:
    hypothesis, revision = _make_hypothesis()
    result = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 1),
    )
    assert result.status == "isolated"
    assert result.evidence_summary.support_unit_count == 1
    assert result.evidence_summary.independent_support_count == 1


def test_repeated_support_links_on_one_position_do_not_double_count() -> None:
    hypothesis, revision = _make_hypothesis()
    first = _support_units(hypothesis, revision, 1)[0]
    second = _retag_link(first, "supports", "m7-map-2")
    result = _assess(hypothesis, revision, _policy(), (first, second))
    assert result.status == "isolated"
    assert len(result.recurrence_units) == 1
    assert result.evidence_summary.support_unit_count == 1


def test_two_positions_same_game_do_not_satisfy_independence_rule() -> None:
    hypothesis, revision = _make_hypothesis()
    units = tuple(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=index,
            relation="supports",
            game_id="same-game",
        )
        for index in (1, 2)
    )
    result = _assess(hypothesis, revision, _policy(), units)
    assert result.status == "insufficient"
    assert result.evidence_summary.support_unit_count == 2
    assert result.evidence_summary.independent_support_count == 1


def test_two_independent_supports_are_candidate_recurrence() -> None:
    hypothesis, revision = _make_hypothesis()
    result = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 2),
    )
    assert result.status == "candidate_recurrence"
    assert result.evidence_summary.independent_support_count == 2


def test_three_independent_supports_with_review_are_supported_recurrence() -> None:
    hypothesis, revision = _make_hypothesis()
    result = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 3),
    )
    assert result.status == "supported_recurrence"
    assert "all_supported_recurrence_policy_gates_met" in result.status_reasons


def test_contradiction_is_retained_and_can_dominate_status() -> None:
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
    result = _assess(hypothesis, revision, _policy(), tuple(units))
    assert result.status == "contradicted"
    assert len(result.contradiction_link_refs) == 1
    assert result.evidence_summary.independent_support_count == 3


def test_counterexample_can_be_policy_defined_as_contradiction() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _support_units(hypothesis, revision, 1)[0],
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="successful_counterexample",
            game_id="g2",
            status="no_supported_discrepancy",
            with_assertion=False,
        ),
    )
    result = _assess(
        hypothesis,
        revision,
        _policy(contradiction_rule="any_contradiction_or_counterexample"),
        units,
    )
    assert result.status == "contradicted"
    assert len(result.successful_counterexample_link_refs) == 1


def test_context_exception_blocks_supported_status_but_preserves_candidate() -> None:
    hypothesis, revision = _make_hypothesis()
    units = list(_support_units(hypothesis, revision, 3))
    units.append(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=4,
            relation="context_exception",
            game_id="g4",
        )
    )
    result = _assess(hypothesis, revision, _policy(), tuple(units))
    assert result.status == "candidate_recurrence"
    assert "context_exception_present" in result.status_reasons


def test_unclear_evidence_blocks_supported_status() -> None:
    hypothesis, revision = _make_hypothesis()
    units = list(_support_units(hypothesis, revision, 3))
    units.append(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=4,
            relation="unclear",
            game_id="g4",
        )
    )
    result = _assess(hypothesis, revision, _policy(), tuple(units))
    assert result.status == "candidate_recurrence"
    assert "unclear_evidence_present" in result.status_reasons


def test_conflicting_relations_on_same_position_become_unclear_unit() -> None:
    hypothesis, revision = _make_hypothesis()
    support = _support_units(hypothesis, revision, 1)[0]
    unclear = _retag_link(support, "unclear", "m7-map-unclear")
    result = _assess(hypothesis, revision, _policy(), (support, unclear))
    assert result.status == "unclear"
    assert result.evidence_summary.mixed_unit_count == 1


def test_same_policy_rule_rejects_cross_policy_aggregation() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=1,
            relation="supports",
            game_id="g1",
            policy_fingerprint="policy-a",
        ),
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="supports",
            game_id="g2",
            policy_fingerprint="policy-b",
        ),
    )
    result = _assess(hypothesis, revision, _policy(), units)
    assert result.status == "insufficient"
    assert result.evidence_summary.eligible_link_count == 0
    assert result.evidence_summary.excluded_link_count == 2


def test_declared_m6_policy_families_can_mix_explicitly() -> None:
    hypothesis, revision = _make_hypothesis()
    first = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=1,
        relation="supports",
        game_id="g1",
        policy_fingerprint="policy-a",
    )
    second = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=2,
        relation="supports",
        game_id="g2",
        policy_fingerprint="policy-b",
    )
    allowed = tuple(
        sorted(
            {
                first[1].assessment_policy_ref.fingerprint,
                second[1].assessment_policy_ref.fingerprint,
            }
        )
    )
    policy = _policy(
        m6_policy_compatibility_rule="declared_policy_fingerprints",
        compatible_m6_policy_fingerprints=allowed,
    )
    result = _assess(hypothesis, revision, policy, (first, second))
    assert result.status == "candidate_recurrence"
    assert result.evidence_summary.eligible_link_count == 2


def test_stage_mismatch_is_not_silently_normalized() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=1,
            relation="supports",
            game_id="g1",
            stage_ids=("stage-a1",),
        ),
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="supports",
            game_id="g2",
            stage_ids=("stage-a2",),
        ),
    )
    result = _assess(hypothesis, revision, _policy(), units)
    assert result.status == "insufficient"
    assert result.evidence_summary.eligible_link_count == 0


def test_declared_stage_rule_can_explicitly_permit_a1_a2_mix() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=1,
            relation="supports",
            game_id="g1",
            stage_ids=("stage-a1",),
        ),
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="supports",
            game_id="g2",
            stage_ids=("stage-a2",),
        ),
    )
    policy = _policy(
        stage_compatibility_rule="declared_stage_ids",
        allowed_stage_ids=("stage-a1", "stage-a2"),
    )
    result = _assess(hypothesis, revision, policy, units)
    assert result.status == "candidate_recurrence"


def test_disallowed_measurement_condition_is_excluded_not_erased() -> None:
    hypothesis, revision = _make_hypothesis()
    unit = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=1,
        relation="supports",
        game_id="g1",
        condition="contaminated",
    )
    result = _assess(hypothesis, revision, _policy(), (unit,))
    assert result.status == "insufficient"
    assert result.evidence_summary.excluded_link_count == 1
    reasons = result.evidence_summary.exclusion_reasons[0][1]
    assert "measurement_condition_not_allowed:contaminated" in reasons


def test_broad_scope_policy_is_explicit_and_deterministic() -> None:
    hypothesis, revision = _make_hypothesis(broad=True)
    units = _support_units(hypothesis, revision, 2)
    policy = _policy(context_match_rule="broad_scope")
    first = _assess(hypothesis, revision, policy, units)
    second = _assess(hypothesis, revision, policy, tuple(reversed(units)))
    assert first == second
    assert first.status == "candidate_recurrence"


def test_required_competing_explanation_review_blocks_supported_status() -> None:
    hypothesis, revision = _make_hypothesis()
    result = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 3),
        review=_review(revision, completed=False),
    )
    assert result.status == "candidate_recurrence"
    assert "competing_explanation_review_incomplete" in result.status_reasons


def test_no_supported_discrepancy_requires_explicit_counterevidence_mapping() -> None:
    hypothesis, revision = _make_hypothesis()
    counterexample = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=1,
        relation="successful_counterexample",
        game_id="g1",
        status="no_supported_discrepancy",
        with_assertion=False,
    )
    result = _assess(hypothesis, revision, _policy(), (counterexample,))
    assert result.status == "unclear"
    assert result.evidence_summary.successful_counterexample_unit_count == 1
    assert result.evidence_summary.support_unit_count == 0
