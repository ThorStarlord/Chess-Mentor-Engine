from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace

import pytest

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import (
    DiscrepancyFact,
    ReasoningDiscrepancyContext,
    ReasoningDiscrepancyError,
    ReasoningEvidenceRef,
    assess_reasoning_discrepancy,
    define_reasoning_assessment_policy,
    record_reasoning_coding,
)

T0 = "2026-09-08T21:00:00-03:00"
T1 = "2026-09-08T21:01:00-03:00"
T2 = "2026-09-08T21:02:00-03:00"


@dataclass(frozen=True, slots=True)
class _Stage:
    stage_id: str
    stage_kind: str
    phase: str = "pre_reveal"


@dataclass(frozen=True, slots=True)
class _Protocol:
    stages: tuple[_Stage, ...]


@dataclass(frozen=True, slots=True)
class _CaptureSession:
    capture_session_id: str
    snapshot_fingerprint: str
    protocol: _Protocol


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _ref(
    authority: str,
    kind: str,
    ref_id: str,
    fingerprint: str | None = None,
) -> ReasoningEvidenceRef:
    return ReasoningEvidenceRef(
        authority=authority,
        kind=kind,
        ref_id=ref_id,
        fingerprint=fingerprint or f"fp-{ref_id}",
    )


def _context(
    *,
    measurement_condition: str = "clean",
    include_analysis: bool = True,
) -> ReasoningDiscrepancyContext:
    position_analysis_refs = (
        (_ref("engine_evidence", "position_analysis", "analysis-1"),)
        if include_analysis
        else ()
    )
    record = ReasoningDiscrepancyContext(
        reasoning_context_id="pending",
        context_fingerprint="pending",
        participant_id="P01",
        player_decision_context_ref=_ref(
            "m5_participant",
            "player_decision_context",
            "player-context-1",
        ),
        position_id="position-1",
        game_id="game-1",
        diagnostic_candidate_ref=_ref(
            "m4_objective",
            "diagnostic_candidate",
            "candidate-1",
        ),
        diagnostic_batch_ref=_ref(
            "m4_objective",
            "diagnostic_batch",
            "batch-1",
        ),
        capture_session_ref=_ref(
            "m5_participant",
            "capture_session",
            "capture-1",
            "capture-fingerprint",
        ),
        assessment_stage_ids=("A1", "A2"),
        player_response_refs=(
            _ref("m5_participant", "player_response", "response-A1"),
            _ref("m5_participant", "player_response", "response-A2"),
        ),
        evidence_freeze_refs=(
            _ref("m5_participant", "evidence_freeze", "freeze-A1"),
            _ref("m5_participant", "evidence_freeze", "freeze-A2"),
        ),
        prompt_presentation_refs=(
            _ref("m5_participant", "prompt_presentation", "prompt-A1"),
            _ref("m5_participant", "prompt_presentation", "prompt-A2"),
        ),
        exposure_refs=(),
        protocol_deviation_refs=(),
        canonical_position_ref=_ref(
            "deterministic_chess",
            "canonical_position",
            "position-1",
        ),
        position_feature_packet_ref=_ref(
            "deterministic_chess",
            "position_feature_packet",
            "features-1",
        ),
        position_analysis_refs=position_analysis_refs,
        decision_comparison_ref=_ref(
            "m4_objective",
            "decision_comparison",
            "comparison-1",
        ),
        selection_signal_refs=(
            _ref("m4_objective", "selection_signal", "signal-1"),
        ),
        measurement_condition=measurement_condition,
        created_at=T0,
    )
    fingerprint = _fingerprint(record.to_dict(include_identity=False))
    return replace(
        record,
        reasoning_context_id=f"reasoning_context_{fingerprint[:20]}",
        context_fingerprint=fingerprint,
    )


def _session(context: ReasoningDiscrepancyContext) -> _CaptureSession:
    return _CaptureSession(
        capture_session_id=context.capture_session_ref.ref_id,
        snapshot_fingerprint=context.capture_session_ref.fingerprint,
        protocol=_Protocol(
            stages=(
                _Stage("A1", "MINIMAL_RESPONSE"),
                _Stage("A2", "STANDARDIZED_PROBE"),
            )
        ),
    )


def _fact(
    context: ReasoningDiscrepancyContext,
    *,
    stage_id: str,
    kind: str,
    relation: str,
    participant_value=None,
    objective_value=None,
) -> DiscrepancyFact:
    stage_index = context.assessment_stage_ids.index(stage_id)
    record = DiscrepancyFact(
        fact_id="pending",
        fingerprint="pending",
        reasoning_context_id=context.reasoning_context_id,
        stage_id=stage_id,
        kind=kind,
        participant_evidence_refs=(
            context.player_response_refs[stage_index],
        ),
        objective_evidence_refs=(context.decision_comparison_ref,),
        relation=relation,
        participant_value=participant_value,
        objective_value=objective_value,
        comparison_provenance=(("basis", "m6c-test-fixture"),),
    )
    fingerprint = _fingerprint(record.to_dict(include_identity=False))
    return replace(
        record,
        fact_id=f"discrepancy_fact_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _policy(
    *,
    version: str = "1",
    eligible_stage_kinds=("MINIMAL_RESPONSE", "STANDARDIZED_PROBE"),
    allowed_measurement_conditions=("clean", "instrument_aware_clean"),
    required_objective_evidence=("decision_comparison",),
    permitted_fact_kinds=(
        "REPORTED_SELECTED_MOVE_RELATION",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
        "EXPECTED_REPLY_RELATION",
        "EXPECTED_CONTINUATION_RELATION",
    ),
    permitted_discrepancy_codes=(
        "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
        "EXPECTED_OPPONENT_REPLY_CONFLICT",
        "EXPECTED_CONTINUATION_CONFLICT",
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        "OTHER_LOCAL_DISCREPANCY",
    ),
    coding_requirements=(
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        "OTHER_LOCAL_DISCREPANCY",
    ),
    thresholds_or_parameters=(("strong_candidate_basis", "engine_rank1"),),
):
    return define_reasoning_assessment_policy(
        policy_id="m6c-local",
        version=version,
        eligible_stage_kinds=eligible_stage_kinds,
        allowed_measurement_conditions=allowed_measurement_conditions,
        required_objective_evidence=required_objective_evidence,
        permitted_fact_kinds=permitted_fact_kinds,
        permitted_discrepancy_codes=permitted_discrepancy_codes,
        coding_requirements=coding_requirements,
        thresholds_or_parameters=thresholds_or_parameters,
    )


def _player_ref(
    context: ReasoningDiscrepancyContext,
    stage_id: str,
) -> ReasoningEvidenceRef:
    index = context.assessment_stage_ids.index(stage_id)
    return context.player_response_refs[index]


def _objective_ref(
    context: ReasoningDiscrepancyContext,
) -> ReasoningEvidenceRef:
    if context.position_analysis_refs:
        return context.position_analysis_refs[0]
    return context.decision_comparison_ref


def _coding(
    context: ReasoningDiscrepancyContext,
    facts: tuple[DiscrepancyFact, ...],
    *,
    code: str,
    kind: str = "discrepancy_support",
    stage_id: str = "A2",
    source_facts: tuple[DiscrepancyFact, ...] = (),
    coder_kind: str = "human",
    coder_id: str = "analyst-1",
    statement: str = "Position-local coding judgment.",
):
    return record_reasoning_coding(
        context=context,
        available_facts=facts,
        coding_kind=kind,
        code=code,
        statement=statement,
        source_player_evidence_refs=(_player_ref(context, stage_id),),
        source_objective_evidence_refs=(_objective_ref(context),),
        source_facts=source_facts,
        coder_kind=coder_kind,
        coder_id=coder_id,
        coder_version="1",
        rubric_or_instruction_fingerprint="rubric-fp-1",
        confidence=0.8,
        uncertainty_note=None,
        created_at=T1,
    )


def test_policy_identity_is_order_normalized_and_material() -> None:
    first = _policy()
    second = _policy(
        eligible_stage_kinds=("STANDARDIZED_PROBE", "MINIMAL_RESPONSE"),
        allowed_measurement_conditions=("instrument_aware_clean", "clean"),
    )
    changed = _policy(version="2")

    assert first.policy_fingerprint == second.policy_fingerprint
    assert first.policy_fingerprint != changed.policy_fingerprint


def test_policy_rejects_intrinsically_coded_code_without_coding_requirement() -> None:
    with pytest.raises(
        ReasoningDiscrepancyError,
        match="intrinsically coded",
    ):
        _policy(
            permitted_discrepancy_codes=(
                "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
            ),
            coding_requirements=(),
            thresholds_or_parameters=(),
        )


def test_policy_requires_explicit_basis_for_deterministic_strong_candidate() -> None:
    with pytest.raises(
        ReasoningDiscrepancyError,
        match="strong_candidate_basis",
    ):
        _policy(
            permitted_discrepancy_codes=(
                "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
            ),
            coding_requirements=(),
            thresholds_or_parameters=(),
        )


def test_reasoning_coding_preserves_human_model_and_source_provenance() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    human = _coding(
        context,
        (fact,),
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        source_facts=(fact,),
        coder_kind="human",
        coder_id="analyst-1",
        statement="The reported rationale is incomplete under rubric R.",
    )
    model = _coding(
        context,
        (fact,),
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        source_facts=(fact,),
        coder_kind="model",
        coder_id="model-run-1",
        statement="The reported rationale is incomplete under rubric R.",
    )

    assert human.coder_kind == "human"
    assert model.coder_kind == "model"
    assert human.source_fact_refs[0].ref_id == fact.fact_id
    assert human.stage_ids == ("A2",)
    assert human.coding_id != model.coding_id


def test_reasoning_coding_rejects_evidence_outside_context() -> None:
    context = _context()
    with pytest.raises(ReasoningDiscrepancyError, match="outside the M6 context"):
        record_reasoning_coding(
            context=context,
            available_facts=(),
            coding_kind="discrepancy_support",
            code="OTHER_LOCAL_DISCREPANCY",
            statement="Local coding.",
            source_player_evidence_refs=(
                _ref("m5_participant", "player_response", "unrelated-response"),
            ),
            coder_kind="human",
            coder_id="analyst-1",
            coder_version="1",
            rubric_or_instruction_fingerprint="rubric-fp-1",
            created_at=T1,
        )


def test_reasoning_coding_requires_stage_specific_source() -> None:
    context = _context()
    with pytest.raises(ReasoningDiscrepancyError, match="stage-specific"):
        record_reasoning_coding(
            context=context,
            available_facts=(),
            coding_kind="discrepancy_support",
            code="OTHER_LOCAL_DISCREPANCY",
            statement="Local coding.",
            source_player_evidence_refs=(context.player_decision_context_ref,),
            coder_kind="human",
            coder_id="analyst-1",
            coder_version="1",
            rubric_or_instruction_fingerprint="rubric-fp-1",
            created_at=T1,
        )


def test_candidate_omission_can_support_deterministic_local_assertion() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
        relation="not_explicitly_reported",
        objective_value={"engine_rank1_uci": "d2d4"},
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "discrepancy_supported"
    assert len(assertions) == 1
    assert assertions[0].basis_kind == "deterministic"
    assert (
        assertions[0].code
        == "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED"
    )
    lowered = assertions[0].statement.lower()
    assert "not explicitly" in lowered
    assert "never considered" not in lowered
    assert "failed to generate" not in lowered


@pytest.mark.parametrize(
    ("kind", "code"),
    (
        ("EXPECTED_REPLY_RELATION", "EXPECTED_OPPONENT_REPLY_CONFLICT"),
        ("EXPECTED_CONTINUATION_RELATION", "EXPECTED_CONTINUATION_CONFLICT"),
    ),
)
def test_deterministic_conflict_fact_supports_matching_local_code(
    kind: str,
    code: str,
) -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind=kind,
        relation="conflict",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "discrepancy_supported"
    assert [item.code for item in assertions] == [code]


def test_correct_move_incomplete_rationale_requires_coding_and_is_mixed() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    coding = _coding(
        context,
        (fact,),
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        source_facts=(fact,),
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(coding,),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "discrepancy_supported"
    assert len(assertions) == 1
    assert assertions[0].basis_kind == "mixed"
    assert assertions[0].supporting_fact_refs[0].ref_id == fact.fact_id
    assert assertions[0].supporting_coding_refs[0].ref_id == coding.coding_id


def test_arbitrary_coder_prose_is_not_promoted_into_assertion_statement() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    coding = _coding(
        context,
        (fact,),
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        source_facts=(fact,),
        statement="The player has tunnel vision and a stable calculation weakness.",
    )

    _, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(coding,),
        policy=_policy(),
        created_at=T2,
    )

    assert "tunnel vision" in coding.statement
    assert "tunnel vision" not in assertions[0].statement.lower()
    assert "stable" not in assertions[0].statement.lower()


def test_same_stage_coding_disagreement_is_preserved_as_unclear() -> None:
    context = _context()
    match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    support = _coding(
        context,
        (match,),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_support",
    )
    contradict = _coding(
        context,
        (match,),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_contradiction",
        coder_id="analyst-2",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(match,),
        codings=(support, contradict),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "unclear"
    assert assertions == ()
    assert support.coding_id in {item.ref_id for item in assessment.coding_refs}
    assert contradict.coding_id in {
        item.ref_id for item in assessment.contradictory_evidence_refs
    }
    assert assessment.status_reasons[0].startswith("CODING_DISAGREEMENT:")


def test_stage_distinct_codings_are_not_collapsed_into_disagreement() -> None:
    context = _context()
    a1_match = _fact(
        context,
        stage_id="A1",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    a2_match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    support_a1 = _coding(
        context,
        (a1_match, a2_match),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_support",
        stage_id="A1",
    )
    contradict_a2 = _coding(
        context,
        (a1_match, a2_match),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_contradiction",
        stage_id="A2",
        coder_id="analyst-2",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(a1_match, a2_match),
        codings=(support_a1, contradict_a2),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "discrepancy_supported"
    assert len(assertions) == 1
    assert assertions[0].stage_ids == ("A1",)
    assert contradict_a2.coding_id in {
        item.ref_id for item in assessment.contradictory_evidence_refs
    }


def test_explicit_unclear_coding_yields_unclear_without_assertion() -> None:
    context = _context()
    match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    unclear = _coding(
        context,
        (match,),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_unclear",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(match,),
        codings=(unclear,),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "unclear"
    assert assertions == ()


def test_coding_support_missing_required_fact_is_unclear() -> None:
    context = _context()
    conflict = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="conflict",
    )
    coding = _coding(
        context,
        (conflict,),
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        source_facts=(conflict,),
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(conflict,),
        codings=(coding,),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "unclear"
    assert assertions == ()
    assert assessment.status_reasons[0].startswith(
        "CODING_SUPPORT_MISSING_REQUIRED_FACT:"
    )


def test_contaminated_context_is_unscorable_when_policy_disallows_it() -> None:
    context = _context(measurement_condition="contaminated")
    fact = _fact(
        context,
        stage_id="A2",
        kind="EXPECTED_REPLY_RELATION",
        relation="conflict",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "unscorable"
    assert assessment.measurement_condition == "contaminated"
    assert assertions == ()
    assert assessment.status_reasons == (
        "MEASUREMENT_CONDITION_NOT_ALLOWED:contaminated",
    )


def test_contaminated_context_can_be_scored_only_when_policy_allows_it() -> None:
    context = _context(measurement_condition="contaminated")
    fact = _fact(
        context,
        stage_id="A2",
        kind="EXPECTED_REPLY_RELATION",
        relation="conflict",
    )
    policy = _policy(
        allowed_measurement_conditions=("clean", "contaminated"),
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=policy,
        created_at=T2,
    )

    assert assessment.status == "discrepancy_supported"
    assert assessment.measurement_condition == "contaminated"
    assert len(assertions) == 1


def test_missing_required_objective_evidence_is_unscorable() -> None:
    context = _context(include_analysis=False)
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    policy = _policy(
        required_objective_evidence=("position_analysis",),
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=policy,
        created_at=T2,
    )

    assert assessment.status == "unscorable"
    assert assertions == ()
    assert assessment.status_reasons == (
        "MISSING_REQUIRED_OBJECTIVE_EVIDENCE:position_analysis",
    )


def test_not_observed_only_does_not_become_no_discrepancy_claim() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="EXPECTED_REPLY_RELATION",
        relation="not_observed",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "unscorable"
    assert assessment.status_reasons == ("NO_ASSESSABLE_DIMENSIONS",)
    assert assertions == ()


def test_no_supported_discrepancy_is_dimension_bounded() -> None:
    context = _context()
    selected_match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    reply_missing = _fact(
        context,
        stage_id="A2",
        kind="EXPECTED_REPLY_RELATION",
        relation="not_observed",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(selected_match, reply_missing),
        codings=(),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "no_supported_discrepancy"
    assert assessment.status_reasons == (
        "NO_SUPPORTED_DISCREPANCY_WITHIN_ASSESSED_DIMENSIONS",
    )
    assert assertions == ()


def test_policy_can_assess_a2_without_merging_a1_into_it() -> None:
    context = _context()
    a1_omission = _fact(
        context,
        stage_id="A1",
        kind="EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
        relation="not_explicitly_reported",
        objective_value={"engine_rank1_uci": "d2d4"},
    )
    a2_match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    policy = _policy(
        eligible_stage_kinds=("STANDARDIZED_PROBE",),
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(a1_omission, a2_match),
        codings=(),
        policy=policy,
        created_at=T2,
    )

    assert assessment.assessed_stage_ids == ("A2",)
    assert assessment.status == "no_supported_discrepancy"
    assert assertions == ()
    assert {item.ref_id for item in assessment.fact_refs} == {a2_match.fact_id}


def test_coding_contradiction_alone_can_support_no_supported_status() -> None:
    context = _context()
    match = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    contradiction = _coding(
        context,
        (match,),
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_contradiction",
    )

    assessment, assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(match,),
        codings=(contradiction,),
        policy=_policy(),
        created_at=T2,
    )

    assert assessment.status == "no_supported_discrepancy"
    assert assertions == ()
    assert contradiction.coding_id in {
        item.ref_id for item in assessment.contradictory_evidence_refs
    }


def test_assessment_identity_is_deterministic_for_identical_inputs() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="EXPECTED_REPLY_RELATION",
        relation="conflict",
    )
    policy = _policy()

    first, first_assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=policy,
        created_at=T2,
    )
    second, second_assertions = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=policy,
        created_at=T2,
    )

    assert first.assessment_id == second.assessment_id
    assert first.fingerprint == second.fingerprint
    assert first_assertions == second_assertions


def test_assessment_identity_changes_with_material_policy_identity() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )

    first, _ = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(version="1"),
        created_at=T2,
    )
    second, _ = assess_reasoning_discrepancy(
        context=context,
        capture_session=_session(context),
        facts=(fact,),
        codings=(),
        policy=_policy(version="2"),
        created_at=T2,
    )

    assert first.assessment_id != second.assessment_id
    assert (
        first.assessment_policy_ref.fingerprint
        != second.assessment_policy_ref.fingerprint
    )


def test_mismatched_capture_session_fingerprint_is_rejected() -> None:
    context = _context()
    session = replace(
        _session(context),
        snapshot_fingerprint="different-fingerprint",
    )

    with pytest.raises(ReasoningDiscrepancyError, match="capture session fingerprint"):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=session,
            facts=(),
            codings=(),
            policy=_policy(),
            created_at=T2,
        )
