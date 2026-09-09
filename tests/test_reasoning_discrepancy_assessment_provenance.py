from __future__ import annotations

from dataclasses import replace

import pytest
from test_reasoning_discrepancy_assessment import (
    T2,
    _coding,
    _context,
    _fact,
    _fingerprint,
    _policy,
    _ref,
    _session,
)

from chess_mentor_engine.learning import (
    ReasoningArtifactRef,
    ReasoningDiscrepancyError,
    assess_reasoning_discrepancy,
)


def _reidentify_coding(coding):
    fingerprint = _fingerprint(coding.to_dict(include_identity=False))
    return replace(
        coding,
        coding_id=f"reasoning_coding_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def _reidentify_fact(fact):
    fingerprint = _fingerprint(fact.to_dict(include_identity=False))
    return replace(
        fact,
        fact_id=f"discrepancy_fact_{fingerprint[:20]}",
        fingerprint=fingerprint,
    )


def test_assessment_revalidates_coding_player_sources() -> None:
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
        code="OTHER_LOCAL_DISCREPANCY",
    )
    forged = _reidentify_coding(
        replace(
            coding,
            source_player_evidence_refs=(
                _ref(
                    "m5_participant",
                    "player_response",
                    "unrelated-response",
                ),
            ),
        )
    )

    with pytest.raises(ReasoningDiscrepancyError, match="outside the M6 context"):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=_session(context),
            facts=(fact,),
            codings=(forged,),
            policy=_policy(),
            created_at=T2,
        )


def test_assessment_revalidates_coding_fact_sources() -> None:
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
    forged = _reidentify_coding(
        replace(
            coding,
            source_fact_refs=(
                ReasoningArtifactRef(
                    kind="discrepancy_fact",
                    ref_id="missing-fact",
                    fingerprint="missing-fingerprint",
                ),
            ),
        )
    )

    with pytest.raises(
        ReasoningDiscrepancyError,
        match="not an exact assessment fact",
    ):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=_session(context),
            facts=(fact,),
            codings=(forged,),
            policy=_policy(),
            created_at=T2,
        )


def test_assessment_revalidates_coding_stage_provenance() -> None:
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
        code="OTHER_LOCAL_DISCREPANCY",
    )
    forged = _reidentify_coding(replace(coding, stage_ids=("A1",)))

    with pytest.raises(
        ReasoningDiscrepancyError,
        match="stage provenance does not match",
    ):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=_session(context),
            facts=(fact,),
            codings=(forged,),
            policy=_policy(),
            created_at=T2,
        )


def test_policy_definition_rejects_unknown_measurement_condition() -> None:
    with pytest.raises(ReasoningDiscrepancyError, match="unknown condition"):
        _policy(allowed_measurement_conditions=("clean", "invented-condition"))


def test_policy_definition_rejects_unknown_fact_kind() -> None:
    with pytest.raises(ReasoningDiscrepancyError, match="unknown M6B fact kind"):
        _policy(permitted_fact_kinds=("INVENTED_FACT_KIND",))


def test_assessment_revalidates_manually_constructed_policy_semantics() -> None:
    context = _context()
    policy = _policy()
    forged = replace(
        policy,
        allowed_measurement_conditions=("invented-condition",),
        policy_fingerprint="pending",
    )
    fingerprint = _fingerprint(forged.to_dict(include_identity=False))
    forged = replace(forged, policy_fingerprint=fingerprint)

    with pytest.raises(ReasoningDiscrepancyError, match="unknown measurement"):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=_session(context),
            facts=(),
            codings=(),
            policy=forged,
            created_at=T2,
        )


def test_assessment_revalidates_manually_constructed_fact_semantics() -> None:
    context = _context()
    fact = _fact(
        context,
        stage_id="A2",
        kind="REPORTED_SELECTED_MOVE_RELATION",
        relation="match",
    )
    forged = _reidentify_fact(replace(fact, relation="invented-relation"))

    with pytest.raises(
        ReasoningDiscrepancyError,
        match="unknown M6B discrepancy relation",
    ):
        assess_reasoning_discrepancy(
            context=context,
            capture_session=_session(context),
            facts=(forged,),
            codings=(),
            policy=_policy(),
            created_at=T2,
        )
