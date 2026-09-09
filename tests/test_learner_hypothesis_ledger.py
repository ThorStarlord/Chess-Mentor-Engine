from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisContextRef,
    HypothesisMappingProvenance,
    LearnerHypothesisError,
    ReasoningArtifactRef,
    ReasoningAssessmentPolicyRef,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
    ReasoningDiscrepancyContext,
    ReasoningEvidenceRef,
    create_learner_hypothesis,
    record_hypothesis_evidence_link,
    record_hypothesis_lifecycle_event,
    record_hypothesis_revision,
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _actor(actor_id: str = "analyst-1") -> HypothesisActorProvenance:
    return HypothesisActorProvenance(
        actor_kind="human",
        actor_id=actor_id,
        actor_version="v1",
        rubric_or_instruction_fingerprint=_fingerprint({"rubric": actor_id}),
        run_id=f"run-{actor_id}",
    )


def _mapping(
    *,
    basis_kind: str = "deterministic_mapping",
    ref_id: str = "mapping-policy-1",
) -> HypothesisMappingProvenance:
    actor = _actor("mapper-1") if basis_kind == "coded_mapping" else None
    return HypothesisMappingProvenance(
        basis_kind=basis_kind,  # type: ignore[arg-type]
        ref_id=ref_id,
        fingerprint=_fingerprint({"mapping": ref_id, "basis": basis_kind}),
        actor_provenance=actor,
    )


def _evidence_ref(
    authority: str,
    kind: str,
    ref_id: str,
) -> ReasoningEvidenceRef:
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
    participant_id: str = "P01",
    position_id: str = "position-1",
    game_id: str = "game-1",
    measurement_condition: str = "clean",
) -> ReasoningDiscrepancyContext:
    return _stamp_context(
        ReasoningDiscrepancyContext(
            reasoning_context_id="pending",
            context_fingerprint="pending",
            participant_id=participant_id,
            player_decision_context_ref=_evidence_ref(
                "m5_participant",
                "player_decision_context",
                f"pdc-{position_id}",
            ),
            position_id=position_id,
            game_id=game_id,
            diagnostic_candidate_ref=_evidence_ref(
                "m4_objective",
                "diagnostic_candidate",
                f"candidate-{position_id}",
            ),
            diagnostic_batch_ref=None,
            capture_session_ref=_evidence_ref(
                "m5_participant",
                "capture_session",
                f"capture-{position_id}",
            ),
            assessment_stage_ids=("stage-a1",),
            player_response_refs=(
                _evidence_ref(
                    "m5_participant",
                    "player_response",
                    f"response-{position_id}",
                ),
            ),
            evidence_freeze_refs=(
                _evidence_ref(
                    "m5_participant",
                    "evidence_freeze",
                    f"freeze-{position_id}",
                ),
            ),
            prompt_presentation_refs=(
                _evidence_ref(
                    "m5_participant",
                    "prompt_presentation",
                    f"prompt-{position_id}",
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
                    f"analysis-{position_id}",
                ),
            ),
            decision_comparison_ref=_evidence_ref(
                "m4_objective",
                "decision_comparison",
                f"comparison-{position_id}",
            ),
            selection_signal_refs=(),
            measurement_condition=measurement_condition,  # type: ignore[arg-type]
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


def _make_m6_bundle(
    *,
    participant_id: str = "P01",
    position_id: str = "position-1",
    game_id: str = "game-1",
    assertion_count: int = 1,
    status: str = "discrepancy_supported",
) -> tuple[
    ReasoningDiscrepancyContext,
    ReasoningDiscrepancyAssessment,
    tuple[ReasoningDiscrepancyAssertion, ...],
]:
    context = _make_context(
        participant_id=participant_id,
        position_id=position_id,
        game_id=game_id,
    )
    policy_ref = ReasoningAssessmentPolicyRef(
        policy_id="m6-test-policy",
        version="1",
        fingerprint=_fingerprint({"policy": "m6-test-policy", "version": 1}),
    )
    assertions: list[ReasoningDiscrepancyAssertion] = []
    facts: list[ReasoningArtifactRef] = []
    for index in range(assertion_count):
        fact = ReasoningArtifactRef(
            kind="discrepancy_fact",
            ref_id=f"fact-{position_id}-{index}",
            fingerprint=_fingerprint({"fact": position_id, "index": index}),
        )
        facts.append(fact)
        assertion = _stamp_assertion(
            ReasoningDiscrepancyAssertion(
                assertion_id="pending",
                fingerprint="pending",
                reasoning_context_id=context.reasoning_context_id,
                assessment_policy_ref=policy_ref,
                code="EXPECTED_OPPONENT_REPLY_CONFLICT",
                statement=f"Expected-reply conflict {index}",
                stage_ids=("stage-a1",),
                supporting_fact_refs=(fact,),
                supporting_coding_refs=(),
                contradictory_evidence_refs=(),
                basis_kind="deterministic",
            )
        )
        assertions.append(assertion)
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
            assessed_stage_ids=("stage-a1",),
            assertion_refs=assertion_refs,
            fact_refs=tuple(facts),
            coding_refs=(),
            contradictory_evidence_refs=(),
            measurement_condition=context.measurement_condition,
            status_reasons=("test-fixture",),
            created_at="2026-09-09T02:00:00+00:00",
        )
    )
    return context, assessment, tuple(assertions)


def _make_hypothesis(
    *,
    participant_id: str = "P01",
    contexts: tuple[HypothesisContextRef, ...] = (),
):
    return create_learner_hypothesis(
        participant_id=participant_id,
        statement=(
            "In forcing-reply positions, the participant often does not explicitly "
            "report the strongest opponent reply."
        ),
        scope_definition="forcing-reply positions",
        context_definition_refs=contexts,
        origin_provenance=_actor(),
        created_at="2026-09-09T03:00:00+00:00",
    )


def test_create_hypothesis_and_revision_one_is_deterministic() -> None:
    first = _make_hypothesis()
    second = _make_hypothesis()
    assert first == second
    hypothesis, revision = first
    assert revision.revision_number == 1
    assert revision.parent_revision_ref is None
    assert revision.hypothesis_id == hypothesis.hypothesis_id
    assert hypothesis.hypothesis_id.startswith("learner_hypothesis_")
    assert revision.revision_id.startswith("hypothesis_revision_")


def test_hypothesis_records_are_immutable() -> None:
    hypothesis, revision = _make_hypothesis()
    with pytest.raises(FrozenInstanceError):
        hypothesis.participant_id = "P02"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        revision.statement = "changed"  # type: ignore[misc]


def test_participant_identity_changes_hypothesis_identity() -> None:
    hypothesis_a, _ = _make_hypothesis(participant_id="P01")
    hypothesis_b, _ = _make_hypothesis(participant_id="P02")
    assert hypothesis_a.hypothesis_id != hypothesis_b.hypothesis_id


def test_revision_appends_exact_parent_without_mutating_history() -> None:
    hypothesis, revision_one = _make_hypothesis()
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="The pattern appears only when the opponent has a forcing check.",
        scope_definition="forcing-check reply positions",
        revision_reason="narrow scope after context exception",
        author_provenance=_actor("analyst-2"),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert revision_one.revision_number == 1
    assert revision_two.revision_number == 2
    assert revision_two.parent_revision_ref is not None
    assert revision_two.parent_revision_ref.revision_id == revision_one.revision_id
    assert revision_two.parent_revision_ref.fingerprint == revision_one.fingerprint


def test_revision_history_must_remain_contiguous() -> None:
    hypothesis, revision_one = _make_hypothesis()
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="Narrower statement",
        scope_definition="narrower scope",
        revision_reason="test",
        author_provenance=_actor(),
        created_at="2026-09-09T04:00:00+00:00",
    )
    with pytest.raises(LearnerHypothesisError, match="revision numbers"):
        record_hypothesis_revision(
            hypothesis=hypothesis,
            existing_revisions=(revision_two,),
            statement="Third statement",
            scope_definition="third scope",
            revision_reason="test",
            author_provenance=_actor(),
            created_at="2026-09-09T05:00:00+00:00",
        )


def test_competing_hypothesis_must_belong_to_same_participant() -> None:
    hypothesis, revision = _make_hypothesis()
    other, _ = _make_hypothesis(participant_id="P02")
    from chess_mentor_engine.learning import LearnerHypothesisRef

    other_ref = LearnerHypothesisRef(
        hypothesis_id=other.hypothesis_id,
        participant_id=other.participant_id,
        fingerprint=other.fingerprint,
    )
    with pytest.raises(LearnerHypothesisError, match="same participant"):
        record_hypothesis_revision(
            hypothesis=hypothesis,
            existing_revisions=(revision,),
            statement="Revised",
            scope_definition="scope",
            competing_hypothesis_refs=(other_ref,),
            revision_reason="test",
            author_provenance=_actor(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_retirement_is_append_only_explicit_lifecycle_history() -> None:
    hypothesis, _ = _make_hypothesis()
    event = record_hypothesis_lifecycle_event(
        hypothesis=hypothesis,
        existing_events=(),
        kind="retired",
        reason="contradictory future evidence",
        author_provenance=_actor(),
        created_at="2026-09-09T05:00:00+00:00",
    )
    assert event.kind == "retired"
    assert event.superseding_hypothesis_ref is None
    with pytest.raises(LearnerHypothesisError, match="already terminal"):
        record_hypothesis_lifecycle_event(
            hypothesis=hypothesis,
            existing_events=(event,),
            kind="retired",
            reason="second retirement",
            author_provenance=_actor(),
            created_at="2026-09-09T06:00:00+00:00",
        )


def test_supersession_preserves_both_same_participant_lineages() -> None:
    old, _ = _make_hypothesis()
    new, _ = create_learner_hypothesis(
        participant_id="P01",
        statement="A materially different descriptive pattern.",
        scope_definition="different scope",
        origin_provenance=_actor("analyst-2"),
        created_at="2026-09-09T04:00:00+00:00",
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=old,
        existing_events=(),
        kind="superseded",
        superseding_hypothesis=new,
        reason="new lineage better matches the descriptive evidence",
        author_provenance=_actor(),
        created_at="2026-09-09T05:00:00+00:00",
    )
    assert event.superseding_hypothesis_ref is not None
    assert event.superseding_hypothesis_ref.hypothesis_id == new.hypothesis_id
    assert old.hypothesis_id != new.hypothesis_id


def test_supersession_rejects_different_participant() -> None:
    old, _ = _make_hypothesis(participant_id="P01")
    new, _ = _make_hypothesis(participant_id="P02")
    with pytest.raises(LearnerHypothesisError, match="same participant"):
        record_hypothesis_lifecycle_event(
            hypothesis=old,
            existing_events=(),
            kind="superseded",
            superseding_hypothesis=new,
            reason="invalid",
            author_provenance=_actor(),
            created_at="2026-09-09T05:00:00+00:00",
        )


def test_evidence_link_binds_exact_m6_provenance() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    link = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="supports",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert link.participant_id == "P01"
    assert link.source_position_id == "position-1"
    assert link.source_game_id == "game-1"
    assert link.measurement_condition == "clean"
    assert link.reasoning_context_ref.ref_id == context.reasoning_context_id
    assert link.assessment_ref.ref_id == assessment.assessment_id
    assert link.assertion_refs[0].ref_id == assertions[0].assertion_id


def test_evidence_link_canonicalizes_assertion_and_context_ref_order() -> None:
    context_a = HypothesisContextRef("context-a", _fingerprint("context-a"))
    context_b = HypothesisContextRef("context-b", _fingerprint("context-b"))
    hypothesis, revision = _make_hypothesis(contexts=(context_b, context_a))
    context, assessment, assertions = _make_m6_bundle(assertion_count=2)
    first = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=(assertions[1], assertions[0]),
        relation="supports",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        context_refs=(context_b, context_a),
        created_at="2026-09-09T04:00:00+00:00",
    )
    second = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="supports",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        context_refs=(context_a, context_b),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert first == second


def test_evidence_link_rejects_participant_mismatch() -> None:
    hypothesis, revision = _make_hypothesis(participant_id="P01")
    context, assessment, assertions = _make_m6_bundle(participant_id="P02")
    with pytest.raises(LearnerHypothesisError, match="participant"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=assessment,
            assertions=assertions,
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_evidence_link_rejects_forged_context_fingerprint() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    forged = replace(context, context_fingerprint="forged")
    with pytest.raises(LearnerHypothesisError, match="Context fingerprint"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=forged,
            assessment=assessment,
            assertions=assertions,
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_evidence_link_rejects_forged_assessment_fingerprint() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    forged = replace(assessment, fingerprint="forged")
    with pytest.raises(LearnerHypothesisError, match="Assessment fingerprint"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=forged,
            assertions=assertions,
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_evidence_link_rejects_assertion_not_cited_by_assessment() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle(assertion_count=2)
    assessment_one = _stamp_assessment(
        replace(assessment, assertion_refs=assessment.assertion_refs[:1])
    )
    with pytest.raises(LearnerHypothesisError, match="not cited"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=assessment_one,
            assertions=(assertions[1],),
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_evidence_link_rejects_assertion_from_other_context() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    forged = _stamp_assertion(
        replace(
            assertions[0],
            reasoning_context_id="reasoning_context_other",
            assertion_id="pending",
            fingerprint="pending",
        )
    )
    assessment_with_forged = _stamp_assessment(
        replace(
            assessment,
            assertion_refs=(
                ReasoningArtifactRef(
                    kind="discrepancy_assertion",
                    ref_id=forged.assertion_id,
                    fingerprint=forged.fingerprint,
                ),
            ),
        )
    )
    with pytest.raises(LearnerHypothesisError, match="different reasoning context"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=assessment_with_forged,
            assertions=(forged,),
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_coded_mapping_requires_actor_provenance() -> None:
    with pytest.raises(ValueError, match="requires actor provenance"):
        HypothesisMappingProvenance(
            basis_kind="coded_mapping",
            ref_id="coded-map",
            fingerprint=_fingerprint("coded-map"),
            actor_provenance=None,
        )


def test_evidence_link_rejects_mapping_basis_mismatch() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    with pytest.raises(LearnerHypothesisError, match="mapping provenance basis"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=assessment,
            assertions=assertions,
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(basis_kind="coded_mapping"),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_relation_is_explicit_and_changes_link_identity() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    support = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="supports",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        created_at="2026-09-09T04:00:00+00:00",
    )
    contradiction = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="contradicts",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert support.link_id != contradiction.link_id
    assert support.relation == "supports"
    assert contradiction.relation == "contradicts"


def test_context_bounded_revision_requires_in_scope_link_context() -> None:
    allowed = HypothesisContextRef("allowed", _fingerprint("allowed"))
    other = HypothesisContextRef("other", _fingerprint("other"))
    hypothesis, revision = _make_hypothesis(contexts=(allowed,))
    context, assessment, assertions = _make_m6_bundle()
    with pytest.raises(LearnerHypothesisError, match="outside hypothesis revision"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision,
            reasoning_context=context,
            assessment=assessment,
            assertions=assertions,
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=_mapping(),
            context_refs=(other,),
            created_at="2026-09-09T04:00:00+00:00",
        )


def test_no_supported_discrepancy_is_not_automatically_counterevidence() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle(
        assertion_count=0,
        status="no_supported_discrepancy",
    )
    assert assertions == ()
    link = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=(),
        relation="unclear",
        basis_kind="coded_mapping",
        mapping_provenance=_mapping(
            basis_kind="coded_mapping",
            ref_id="review-no-discrepancy",
        ),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert assessment.status == "no_supported_discrepancy"
    assert link.relation == "unclear"
    assert link.assertion_refs == ()


def test_same_m6_position_can_have_multiple_links_without_recurrence_state() -> None:
    hypothesis, revision = _make_hypothesis()
    context, assessment, assertions = _make_m6_bundle()
    support = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="supports",
        basis_kind="deterministic_mapping",
        mapping_provenance=_mapping(ref_id="map-support"),
        created_at="2026-09-09T04:00:00+00:00",
    )
    unclear = record_hypothesis_evidence_link(
        hypothesis=hypothesis,
        revision=revision,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        relation="unclear",
        basis_kind="coded_mapping",
        mapping_provenance=_mapping(
            basis_kind="coded_mapping",
            ref_id="map-review",
        ),
        created_at="2026-09-09T04:00:00+00:00",
    )
    assert support.source_position_id == unclear.source_position_id
    assert support.link_id != unclear.link_id
    assert not hasattr(support, "recurrence_status")
