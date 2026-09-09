from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from test_reasoning_discrepancy_assessment import _coding, _policy
from test_reasoning_discrepancy_facts import (
    T7,
    _ambiguous,
    _capture,
    _context,
    _fact,
    _facts,
    _move,
    _Upstream,
    _upstream,
)

from chess_mentor_engine.analysis import (
    CandidateLine,
    CentipawnEvaluation,
    analysis_result_fingerprint,
)
from chess_mentor_engine.chess import build_position_context
from chess_mentor_engine.evidence import (
    ParticipantStructuredResponse,
    record_capture_deviation,
    record_capture_exposure,
    record_player_decision_context,
)
from chess_mentor_engine.learning import (
    ReasoningDiscrepancyError,
    assess_reasoning_discrepancy,
)
from chess_mentor_engine.selection import (
    SelectionPolicy,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)

Q2 = "2026-09-08T22:01:00-03:00"


def _control_upstream() -> _Upstream:
    base = _upstream()
    analysis = replace(
        base.analysis,
        result_fingerprint="",
        lines=(
            CandidateLine(
                rank=1,
                root_move_uci="e2e4",
                evaluation=CentipawnEvaluation(60),
                pv_uci=("e2e4", "e7e5", "g1f3"),
            ),
            CandidateLine(
                rank=2,
                root_move_uci="d2d4",
                evaluation=CentipawnEvaluation(0),
                pv_uci=("d2d4", "d7d5", "c2c4"),
            ),
        ),
    )
    analysis = replace(
        analysis,
        result_fingerprint=analysis_result_fingerprint(analysis),
    )
    comparison = compare_played_decision(
        game=base.game,
        position=base.position,
        root_analysis=analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=base.features,
        root_analysis=analysis,
    )
    policy = SelectionPolicy(
        policy_id="m6q-control-selection",
        version="1",
        requested_size=1,
        candidate_min_cp_delta=40,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        include_rank1_controls=True,
        minimum_controls=1,
        maximum_per_game=1,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )
    assert result.candidate is not None
    assert result.decision.role == "control"
    batch = build_diagnostic_candidate_batch(results=(result,), policy=policy)
    assert result.candidate.candidate_id in batch.control_candidate_ids
    player_context = record_player_decision_context(
        participant_id="P01",
        session_id="m6q-control-session",
        position=base.position,
        position_context=build_position_context(base.game, base.position),
        candidate=result.candidate,
        batch=batch,
        created_at="2026-09-08T09:00:00-03:00",
    )
    return _Upstream(
        game=base.game,
        position=base.position,
        features=base.features,
        analysis=analysis,
        comparison=comparison,
        signals=signals,
        candidate=result.candidate,
        batch=batch,
        player_context=player_context,
    )


def _assess(upstream: _Upstream, session, context, facts, *, policy=None, codings=()):
    return assess_reasoning_discrepancy(
        context=context,
        capture_session=session,
        facts=facts,
        codings=codings,
        policy=_policy() if policy is None else policy,
        created_at=Q2,
    )


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def test_m6q_accurate_observed_reasoning_is_dimension_bounded_no_supported() -> None:
    upstream = _upstream()
    session = _capture(
        upstream,
        a1_structured=ParticipantStructuredResponse(selected_move=_move("d2d4")),
    )
    context = _context(upstream, session, stages=("A1",))
    facts = _facts(upstream, session, context)
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=_policy(eligible_stage_kinds=("MINIMAL_RESPONSE",)),
    )

    assert _fact(
        facts,
        "A1",
        "REPORTED_SELECTED_MOVE_RELATION",
    ).relation == "match"
    assert assessment.status == "no_supported_discrepancy"
    assert assessment.status_reasons == (
        "NO_SUPPORTED_DISCREPANCY_WITHIN_ASSESSED_DIMENSIONS",
    )
    assert assertions == ()


def test_m6q_successful_move_incomplete_rationale_requires_mixed_evidence() -> None:
    upstream = _upstream()
    session = _capture(
        upstream,
        a1_structured=ParticipantStructuredResponse(selected_move=_move("d2d4")),
    )
    context = _context(upstream, session, stages=("A1",))
    facts = _facts(upstream, session, context)
    selected = _fact(facts, "A1", "REPORTED_SELECTED_MOVE_RELATION")
    coding = _coding(
        context,
        facts,
        code="CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        stage_id="A1",
        source_facts=(selected,),
        statement="The reported rationale is incomplete under rubric M6Q-R1.",
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        codings=(coding,),
    )

    assert assessment.status == "discrepancy_supported"
    assertion = next(
        item
        for item in assertions
        if item.code == "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE"
    )
    assert assertion.basis_kind == "mixed"
    assert assertion.supporting_fact_refs[0].ref_id == selected.fact_id
    assert assertion.supporting_coding_refs[0].ref_id == coding.coding_id


def test_m6q_candidate_omission_is_conservative_deterministic_assertion() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    assessment, assertions = _assess(upstream, session, context, facts)

    omission = _fact(
        facts,
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert omission.relation == "not_explicitly_reported"
    assertion = next(
        item
        for item in assertions
        if item.code == "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED"
    )
    assert assessment.status == "discrepancy_supported"
    assert assertion.basis_kind == "deterministic"
    wording = assertion.statement.lower()
    assert "not explicitly" in wording
    assert "never considered" not in wording
    assert "failed to generate" not in wording


def test_m6q_expected_reply_conflict_uses_deterministic_legality() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e2e4"),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    policy = _policy(
        permitted_fact_kinds=("EXPECTED_REPLY_RELATION",),
        permitted_discrepancy_codes=("EXPECTED_OPPONENT_REPLY_CONFLICT",),
        coding_requirements=(),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    reply = _fact(facts, "A2", "EXPECTED_REPLY_RELATION")
    assert reply.relation == "conflict"
    assert dict(reply.comparison_provenance)["basis"] == "deterministic_reply_legality"
    assert assessment.status == "discrepancy_supported"
    assert [item.code for item in assertions] == ["EXPECTED_OPPONENT_REPLY_CONFLICT"]


def test_m6q_expected_continuation_conflict_uses_deterministic_legality() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e7e5"),
        expected_continuation=(_move("e2e4"),),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    policy = _policy(
        permitted_fact_kinds=("EXPECTED_CONTINUATION_RELATION",),
        permitted_discrepancy_codes=("EXPECTED_CONTINUATION_CONFLICT",),
        coding_requirements=(),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    continuation = _fact(facts, "A2", "EXPECTED_CONTINUATION_RELATION")
    assert continuation.relation == "conflict"
    assert dict(continuation.comparison_provenance)["basis"] == (
        "deterministic_continuation_legality"
    )
    assert assessment.status == "discrepancy_supported"
    assert [item.code for item in assertions] == ["EXPECTED_CONTINUATION_CONFLICT"]


def test_m6q_missing_dimension_is_not_observed_and_unscorable_not_negative() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(selected_move=_move("e2e4"))
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    policy = _policy(
        permitted_fact_kinds=("EXPECTED_REPLY_RELATION",),
        permitted_discrepancy_codes=("EXPECTED_OPPONENT_REPLY_CONFLICT",),
        coding_requirements=(),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    assert _fact(facts, "A2", "EXPECTED_REPLY_RELATION").relation == "not_observed"
    assert assessment.status == "unscorable"
    assert assessment.status_reasons == ("NO_ASSESSABLE_DIMENSIONS",)
    assert assertions == ()


def test_m6q_ambiguous_report_is_preserved_without_guessed_discrepancy() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(selected_move=_ambiguous())
    session = _capture(upstream, a1_structured=structured)
    context = _context(upstream, session, stages=("A1",))
    facts = _facts(upstream, session, context)
    policy = _policy(
        eligible_stage_kinds=("MINIMAL_RESPONSE",),
        permitted_fact_kinds=("REPORTED_SELECTED_MOVE_RELATION",),
        permitted_discrepancy_codes=(
            "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        ),
        coding_requirements=("CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    selected = _fact(facts, "A1", "REPORTED_SELECTED_MOVE_RELATION")
    assert selected.relation == "ambiguous"
    assert selected.participant_value["normalized_uci"] is None
    assert assessment.status == "unscorable"
    assert assertions == ()


def test_m6q_a1_and_a2_remain_distinct_evidence_states() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A1", "A2"))
    facts = _facts(upstream, session, context)
    policy = _policy(
        permitted_fact_kinds=("EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",),
        permitted_discrepancy_codes=(
            "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
        ),
        coding_requirements=(),
        thresholds_or_parameters=(("strong_candidate_basis", "engine_rank1"),),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    assert _fact(
        facts,
        "A1",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    ).relation == "not_observed"
    assert _fact(
        facts,
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    ).relation == "not_explicitly_reported"
    assert assessment.assessed_stage_ids == ("A1", "A2")
    assert [item.stage_ids for item in assertions] == [("A2",)]


def test_m6q_instrument_awareness_is_preserved_without_forcing_contamination() -> None:
    upstream = _upstream()
    clean = _capture(upstream)
    aware, _ = record_capture_exposure(
        clean,
        kind="INSTRUMENT_AWARENESS_RECORDED",
        occurred_at=T7,
        source="m6q-qualification",
        instrument_awareness="known_aware",
    )
    context = _context(upstream, aware, stages=("A2",))
    facts = _facts(upstream, aware, context)
    assessment, _ = _assess(upstream, aware, context, facts)

    assert aware.contaminated is False
    assert context.measurement_condition == "instrument_aware_clean"
    assert assessment.measurement_condition == "instrument_aware_clean"
    assert assessment.status == "discrepancy_supported"


@pytest.mark.parametrize(
    ("contaminates", "expected_condition"),
    ((False, "deviating"), (True, "contaminated")),
)
def test_m6q_deviation_condition_requires_explicit_policy_eligibility(
    contaminates: bool,
    expected_condition: str,
) -> None:
    upstream = _upstream()
    clean = _capture(upstream)
    session = record_capture_deviation(
        clean,
        code="OTHER",
        occurred_at=T7,
        details=(("qualification", expected_condition),),
        contaminates_pre_reveal=contaminates,
    )
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)

    blocked, blocked_assertions = _assess(upstream, session, context, facts)
    assert context.measurement_condition == expected_condition
    assert blocked.status == "unscorable"
    assert blocked.measurement_condition == expected_condition
    assert blocked_assertions == ()

    allowed_policy = _policy(
        allowed_measurement_conditions=("clean", expected_condition),
    )
    allowed, _ = _assess(
        upstream,
        session,
        context,
        facts,
        policy=allowed_policy,
    )
    assert allowed.measurement_condition == expected_condition
    assert allowed.status == "discrepancy_supported"


def test_m6q_post_reveal_not_primary() -> None:
    with pytest.raises(ReasoningDiscrepancyError, match="pre-reveal"):
        _policy(eligible_stage_kinds=("POST_REVEAL_REFLECTION",))


def test_m6q_unavailable_objective_is_not_comparable() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",), analyses=())
    facts = _facts(upstream, session, context, analyses=())
    policy = _policy(
        permitted_fact_kinds=("EXPECTED_REPLY_RELATION",),
        permitted_discrepancy_codes=("EXPECTED_OPPONENT_REPLY_CONFLICT",),
        coding_requirements=(),
        thresholds_or_parameters=(),
        required_objective_evidence=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    assert _fact(facts, "A2", "EXPECTED_REPLY_RELATION").relation == "not_comparable"
    assert assessment.status == "unscorable"
    assert assessment.status_reasons == ("NO_ASSESSABLE_DIMENSIONS",)
    assert assertions == ()


def test_m6q_incompatible_objective_provenance_is_rejected_not_interpolated() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    mismatched = replace(upstream.analysis, result_fingerprint="different-result")

    with pytest.raises(ReasoningDiscrepancyError, match="result fingerprint"):
        _context(upstream, session, analyses=(mismatched,))


def test_m6q_pure_coded_assertion_stays_separate_from_deterministic_fact() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    coding = _coding(
        context,
        facts,
        code="OTHER_LOCAL_DISCREPANCY",
        stage_id="A2",
        statement="Position-local coder judgment under rubric M6Q-R2.",
    )
    policy = _policy(
        permitted_fact_kinds=("REPORTED_SELECTED_MOVE_RELATION",),
        permitted_discrepancy_codes=("OTHER_LOCAL_DISCREPANCY",),
        coding_requirements=("OTHER_LOCAL_DISCREPANCY",),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
        codings=(coding,),
    )

    assert assessment.status == "discrepancy_supported"
    assert len(assertions) == 1
    assert assertions[0].basis_kind == "coded"
    assert assertions[0].supporting_fact_refs == ()
    assert assertions[0].supporting_coding_refs[0].ref_id == coding.coding_id


def test_m6q_same_stage_coder_disagreement_is_unclear_and_preserved() -> None:
    upstream = _upstream()
    session = _capture(upstream)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    support = _coding(
        context,
        facts,
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_support",
        stage_id="A2",
        coder_id="m6q-coder-a",
    )
    contradict = _coding(
        context,
        facts,
        code="OTHER_LOCAL_DISCREPANCY",
        kind="discrepancy_contradiction",
        stage_id="A2",
        coder_id="m6q-coder-b",
    )
    policy = _policy(
        permitted_fact_kinds=("REPORTED_SELECTED_MOVE_RELATION",),
        permitted_discrepancy_codes=("OTHER_LOCAL_DISCREPANCY",),
        coding_requirements=("OTHER_LOCAL_DISCREPANCY",),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
        codings=(support, contradict),
    )

    assert assessment.status == "unclear"
    assert assertions == ()
    assert assessment.status_reasons == (
        "CODING_DISAGREEMENT:OTHER_LOCAL_DISCREPANCY:A2",
    )
    assert contradict.coding_id in {
        item.ref_id for item in assessment.contradictory_evidence_refs
    }


def test_m6q_raw_prose_does_not_override_structured_absence() -> None:
    upstream = _upstream()
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        candidate_moves=(_move("e2e4"),),
    )
    session = _capture(
        upstream,
        a2_structured=structured,
        a2_raw="I also seriously considered d4, but did not submit it in the fields.",
    )
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    assessment, assertions = _assess(upstream, session, context, facts)

    membership = _fact(
        facts,
        "A2",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    )
    assert membership.relation == "not_explicitly_reported"
    assert membership.participant_value == [_move("e2e4").to_dict()]
    assertion = next(
        item
        for item in assertions
        if item.code == "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED"
    )
    assert assessment.status == "discrepancy_supported"
    wording = assertion.statement.lower()
    assert "not explicitly" in wording
    assert "never considered" not in wording
    assert "failed to generate" not in wording


def test_m6q_successful_m4_control_can_still_have_local_reasoning_discrepancy() -> None:
    upstream = _control_upstream()
    assert upstream.candidate.candidate_id in upstream.batch.control_candidate_ids
    structured = ParticipantStructuredResponse(
        selected_move=_move("e2e4"),
        expected_reply=_move("e7e5"),
        expected_continuation=(_move("e2e4"),),
    )
    session = _capture(upstream, a2_structured=structured)
    context = _context(upstream, session, stages=("A2",))
    facts = _facts(upstream, session, context)
    policy = _policy(
        permitted_fact_kinds=(
            "REPORTED_SELECTED_MOVE_RELATION",
            "EXPECTED_CONTINUATION_RELATION",
        ),
        permitted_discrepancy_codes=("EXPECTED_CONTINUATION_CONFLICT",),
        coding_requirements=(),
        thresholds_or_parameters=(),
    )
    assessment, assertions = _assess(
        upstream,
        session,
        context,
        facts,
        policy=policy,
    )

    assert _fact(
        facts,
        "A2",
        "REPORTED_SELECTED_MOVE_RELATION",
    ).relation == "match"
    assert _fact(
        facts,
        "A2",
        "EXPECTED_CONTINUATION_RELATION",
    ).relation == "conflict"
    assert assessment.status == "discrepancy_supported"
    assert [item.code for item in assertions] == ["EXPECTED_CONTINUATION_CONFLICT"]


def test_m6q_full_chain_replay_is_content_addressed_and_deterministic() -> None:
    first_upstream = _upstream()
    first_session = _capture(first_upstream)
    first_context = _context(first_upstream, first_session, stages=("A2",))
    first_facts = _facts(first_upstream, first_session, first_context)
    first_assessment, first_assertions = _assess(
        first_upstream,
        first_session,
        first_context,
        first_facts,
    )

    second_upstream = _upstream()
    second_session = _capture(second_upstream)
    second_context = _context(second_upstream, second_session, stages=("A2",))
    second_facts = _facts(second_upstream, second_session, second_context)
    second_assessment, second_assertions = _assess(
        second_upstream,
        second_session,
        second_context,
        second_facts,
    )

    assert (
        first_upstream.candidate.candidate_id
        == second_upstream.candidate.candidate_id
    )
    assert first_upstream.batch.batch_id == second_upstream.batch.batch_id
    assert (
        first_session.snapshot_fingerprint
        == second_session.snapshot_fingerprint
    )
    assert (
        first_context.reasoning_context_id
        == second_context.reasoning_context_id
    )
    assert [item.fact_id for item in first_facts] == [
        item.fact_id for item in second_facts
    ]
    assert first_assessment.assessment_id == second_assessment.assessment_id
    assert first_assessment.fingerprint == second_assessment.fingerprint
    assert first_assertions == second_assertions


def test_m6q_historical_pilot_003_004_artifacts_remain_byte_identical() -> None:
    repository_root = Path(__file__).parents[1]
    fixture_path = (
        repository_root
        / "tests"
        / "fixtures"
        / "m5q_player_evidence_corpus.json"
    )
    corpus = json.loads(fixture_path.read_text(encoding="utf-8"))
    expected = corpus["research_artifact_git_blob_shas"]

    assert len(expected) == 7
    for relative_path, expected_sha in expected.items():
        assert _git_blob_sha(repository_root / relative_path) == expected_sha
