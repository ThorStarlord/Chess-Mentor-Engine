from __future__ import annotations

import pytest

from chess_mentor_engine.selection import (
    AnalysisEvidenceRef,
    DecisionComparison,
    DecisionComparisonPolicy,
    DecisionProvenance,
    DiagnosticCandidateBatchError,
    SelectionEvidenceRef,
    SelectionPolicy,
    SelectionQuota,
    SelectionSignal,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _comparison(index: int, *, game_id: str = "game-a") -> DecisionComparison:
    return DecisionComparison(
        comparison_id=f"comparison-{game_id}-{index}",
        position_id=f"position-{game_id}-{index}",
        game_id=game_id,
        played_move_uci="e2e4",
        side_to_move="white",
        root_analysis_ref=AnalysisEvidenceRef(
            position_id=f"position-{game_id}-{index}",
            fen=START_FEN,
            request_fingerprint=f"request-{game_id}-{index}",
            result_fingerprint=f"result-{game_id}-{index}",
            status="complete",
        ),
        played_evaluation_source="root_multipv",
        played_analysis_ref=None,
        played_root_line_rank=None,
        best_move_uci=None,
        best_evaluation=None,
        played_evaluation=None,
        compatibility="same_root_analysis",
        comparison_kind="incomparable",
        preference="incomparable",
        exact_centipawn_delta_for_mover=None,
        mate_relation=None,
        terminal_outcome=None,
        policy=DecisionComparisonPolicy(),
        provenance=DecisionProvenance(
            source_sha256=f"source-{game_id}",
            game_semantic_fingerprint=f"semantic-{game_id}",
            root_ply_index=index,
            played_move_index=index,
            child_position_id=f"child-{game_id}-{index}",
        ),
    )


def _signal(
    comparison: DecisionComparison,
    kind: str,
    raw_value: object,
    *,
    suffix: str | None = None,
) -> SelectionSignal:
    token = suffix or kind.lower()
    return SelectionSignal(
        signal_id=f"signal-{comparison.comparison_id}-{token}",
        kind=kind,  # type: ignore[arg-type]
        position_id=comparison.position_id,
        game_id=comparison.game_id,
        comparison_id=comparison.comparison_id,
        schema_version="1",
        raw_value=raw_value,
        evidence=(
            SelectionEvidenceRef(
                source="decision_comparison",
                ref_id=comparison.comparison_id,
                fingerprint=f"fingerprint-{comparison.comparison_id}",
            ),
        ),
    )


def _policy(**overrides) -> SelectionPolicy:
    values = {
        "policy_id": "m4d-test",
        "version": "1",
        "requested_size": 4,
        "candidate_min_cp_delta": 50,
        "control_max_cp_delta": 10,
        "close_choice_max_cp": 20,
        "candidate_mate_relations": ("forced_mate_missed", "forced_mate_allowed"),
        "include_rank1_controls": True,
        "minimum_controls": 1,
        "maximum_per_game": 2,
        "quotas": (),
    }
    values.update(overrides)
    return SelectionPolicy(**values)


def _apply(
    comparison: DecisionComparison,
    signals: tuple[SelectionSignal, ...],
    policy: SelectionPolicy,
):
    return apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )


def test_policy_rejects_invalid_bounds_and_duplicate_quotas() -> None:
    with pytest.raises(ValueError):
        _policy(candidate_min_cp_delta=-1)
    with pytest.raises(ValueError):
        _policy(minimum_controls=5)
    with pytest.raises(ValueError):
        _policy(maximum_per_game=0)
    with pytest.raises(ValueError):
        _policy(
            quotas=(
                SelectionQuota("MATE_RELATION", 1),
                SelectionQuota("MATE_RELATION", 0),
            )
        )
    with pytest.raises(ValueError):
        SelectionQuota("EXACT_CP_DELTA", minimum=2, maximum=1)


def test_policy_identity_is_versioned_and_configuration_is_fingerprinted() -> None:
    first = _policy()
    same = _policy()
    changed_config = _policy(candidate_min_cp_delta=75)
    changed_version = _policy(version="2")

    assert first.identity == same.identity
    assert first.fingerprint == same.fingerprint
    assert first.identity == changed_config.identity
    assert first.fingerprint != changed_config.fingerprint
    assert first.identity != changed_version.identity


def test_candidate_cp_threshold_is_inclusive_and_inspectable() -> None:
    policy = _policy(candidate_min_cp_delta=50)
    below = _comparison(1)
    exact = _comparison(2)

    below_result = _apply(
        below,
        (_signal(below, "EXACT_CP_DELTA", 49),),
        policy,
    )
    exact_result = _apply(
        exact,
        (_signal(exact, "EXACT_CP_DELTA", 50),),
        policy,
    )

    assert not below_result.decision.eligible
    assert exact_result.decision.eligible
    assert exact_result.decision.role == "candidate"
    match = exact_result.decision.matches[0]
    assert match.rule_id == "candidate_min_cp_delta"
    assert match.observed_value == 50
    assert match.operator == ">="
    assert match.threshold == 50
    assert exact_result.candidate is not None
    assert exact_result.candidate.eligibility_signal_ids == (
        exact_result.decision.eligibility_signal_ids
    )


def test_rank1_and_low_delta_are_successful_control_evidence() -> None:
    comparison = _comparison(3)
    signals = (
        _signal(comparison, "PLAYED_EQUALS_RANK_1", {"played": "e2e4"}),
        _signal(comparison, "EXACT_CP_DELTA", 0),
    )

    result = _apply(comparison, signals, _policy())

    assert result.decision.eligible
    assert result.decision.role == "control"
    assert {item.rule_id for item in result.decision.matches} == {
        "low_severity_control",
        "rank1_control",
    }


def test_close_choice_is_policy_interpretation_of_raw_separation() -> None:
    policy = _policy(close_choice_max_cp=20, candidate_min_cp_delta=None)
    inside = _comparison(4)
    outside = _comparison(5)

    inside_result = _apply(
        inside,
        (
            _signal(
                inside,
                "TOP_CANDIDATE_SEPARATION",
                {"exact_centipawn_separation_for_mover": 20},
            ),
        ),
        policy,
    )
    outside_result = _apply(
        outside,
        (
            _signal(
                outside,
                "TOP_CANDIDATE_SEPARATION",
                {"exact_centipawn_separation_for_mover": 21},
            ),
        ),
        policy,
    )

    assert inside_result.decision.role == "candidate"
    assert inside_result.decision.matches[0].rule_id == "multipv_close_choice"
    assert not outside_result.decision.eligible


def test_mate_relation_can_be_candidate_without_centipawn_sentinel() -> None:
    comparison = _comparison(6)
    result = _apply(
        comparison,
        (_signal(comparison, "MATE_RELATION", "forced_mate_missed"),),
        _policy(candidate_min_cp_delta=None, close_choice_max_cp=None),
    )

    assert result.decision.role == "candidate"
    assert result.decision.matches[0].rule_id == "candidate_mate_relation"
    assert result.decision.matches[0].observed_value == "forced_mate_missed"


def test_excluded_signal_kind_blocks_otherwise_eligible_position() -> None:
    comparison = _comparison(7)
    policy = _policy(excluded_signal_kinds=("ENGINE_EVIDENCE_INVERSION",))
    result = _apply(
        comparison,
        (
            _signal(comparison, "EXACT_CP_DELTA", 100),
            _signal(comparison, "ENGINE_EVIDENCE_INVERSION", {"delta": -5}),
        ),
        policy,
    )

    assert not result.decision.eligible
    assert result.candidate is None
    assert result.decision.exclusion_reasons == (
        "excluded_signal_kind:ENGINE_EVIDENCE_INVERSION",
    )


def _batch_pool(policy: SelectionPolicy):
    control = _comparison(0, game_id="game-a")
    cp_a = _comparison(1, game_id="game-a")
    cp_a_extra = _comparison(2, game_id="game-a")
    mate = _comparison(0, game_id="game-b")
    close = _comparison(0, game_id="game-c")

    return (
        _apply(
            control,
            (
                _signal(control, "PLAYED_EQUALS_RANK_1", {"rank": 1}),
                _signal(control, "EXACT_CP_DELTA", 0),
            ),
            policy,
        ),
        _apply(cp_a, (_signal(cp_a, "EXACT_CP_DELTA", 80),), policy),
        _apply(cp_a_extra, (_signal(cp_a_extra, "EXACT_CP_DELTA", 90),), policy),
        _apply(
            mate,
            (_signal(mate, "MATE_RELATION", "forced_mate_missed"),),
            policy,
        ),
        _apply(
            close,
            (
                _signal(
                    close,
                    "TOP_CANDIDATE_SEPARATION",
                    {"exact_centipawn_separation_for_mover": 12},
                ),
            ),
            policy,
        ),
    )


def test_batch_is_deterministic_under_input_reordering() -> None:
    policy = _policy(
        requested_size=4,
        quotas=(SelectionQuota("MATE_RELATION", minimum=1),),
    )
    pool = _batch_pool(policy)

    first = build_diagnostic_candidate_batch(results=pool, policy=policy)
    reordered = build_diagnostic_candidate_batch(
        results=tuple(reversed(pool)),
        policy=policy,
    )

    assert first == reordered
    assert first.batch_id == reordered.batch_id
    assert first.actual_size == 4
    assert len(first.control_candidate_ids) >= 1
    assert first.quota_outcomes[0].selected_count >= 1
    assert first.quota_outcomes[0].shortfall == 0


def test_batch_enforces_per_game_cap_and_records_nonselection() -> None:
    policy = _policy(requested_size=5, maximum_per_game=2)
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

    game_a = [item for item in batch.candidates if item.game_id == "game-a"]
    assert len(game_a) == 2
    assert any("maximum_per_game" in item.reasons for item in batch.exclusions)
    assert batch.actual_size == 4
    assert batch.shortfall == 1


def test_control_shortfall_is_visible_without_reclassifying_candidates() -> None:
    policy = _policy(requested_size=4, minimum_controls=2, maximum_per_game=None)
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

    assert batch.actual_size == 4
    assert len(batch.control_candidate_ids) == 1
    assert batch.control_shortfall == 1


def test_quota_shortfall_is_visible_even_when_batch_is_full() -> None:
    policy = _policy(
        requested_size=4,
        maximum_per_game=None,
        quotas=(SelectionQuota("MATE_RELATION", minimum=2),),
    )
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

    assert batch.actual_size == 4
    assert batch.quota_outcomes[0].selected_count == 1
    assert batch.quota_outcomes[0].shortfall == 1


def test_quota_maximum_prevents_overrepresentation() -> None:
    policy = _policy(
        requested_size=5,
        maximum_per_game=None,
        quotas=(SelectionQuota("EXACT_CP_DELTA", maximum=2),),
    )
    pool = _batch_pool(policy)
    batch = build_diagnostic_candidate_batch(results=pool, policy=policy)

    cp_count = sum(
        1
        for candidate in batch.candidates
        if any(signal.kind == "EXACT_CP_DELTA" for signal in candidate.signals)
    )
    assert cp_count == 2
    assert any(
        "quota_maximum:EXACT_CP_DELTA" in item.reasons
        for item in batch.exclusions
    )


def test_batch_size_shortfall_never_pads_with_policy_excluded_position() -> None:
    policy = _policy(
        requested_size=4,
        candidate_min_cp_delta=50,
        control_max_cp_delta=None,
        include_rank1_controls=False,
        close_choice_max_cp=None,
        candidate_mate_relations=(),
        minimum_controls=0,
        maximum_per_game=None,
    )
    first = _comparison(0, game_id="one")
    second = _comparison(0, game_id="two")
    excluded = _comparison(0, game_id="three")
    pool = (
        _apply(first, (_signal(first, "EXACT_CP_DELTA", 100),), policy),
        _apply(second, (_signal(second, "EXACT_CP_DELTA", 80),), policy),
        _apply(excluded, (_signal(excluded, "EXACT_CP_DELTA", 10),), policy),
    )

    batch = build_diagnostic_candidate_batch(results=pool, policy=policy)

    assert batch.actual_size == 2
    assert batch.shortfall == 2
    assert any(
        item.comparison_id == excluded.comparison_id
        and item.reasons == ("no_eligibility_rule_matched",)
        for item in batch.exclusions
    )


def test_batch_rejects_same_policy_identity_with_changed_configuration() -> None:
    original = _policy()
    changed = _policy(candidate_min_cp_delta=75)
    pool = _batch_pool(original)

    with pytest.raises(DiagnosticCandidateBatchError):
        build_diagnostic_candidate_batch(results=pool, policy=changed)


def test_policy_version_changes_candidate_and_batch_identity() -> None:
    first_policy = _policy(version="1")
    second_policy = _policy(version="2")
    comparison = _comparison(20, game_id="versioned")
    signals = (_signal(comparison, "EXACT_CP_DELTA", 100),)

    first_result = _apply(comparison, signals, first_policy)
    second_result = _apply(comparison, signals, second_policy)
    first_batch = build_diagnostic_candidate_batch(
        results=(first_result,),
        policy=_policy(version="1", requested_size=1, minimum_controls=0),
    )
    second_batch = build_diagnostic_candidate_batch(
        results=(second_result,),
        policy=_policy(version="2", requested_size=1, minimum_controls=0),
    )

    assert first_result.candidate is not None
    assert second_result.candidate is not None
    assert first_result.candidate.candidate_id != second_result.candidate.candidate_id
    assert first_batch.batch_id != second_batch.batch_id


def test_m4d_records_never_emit_learner_or_pedagogical_labels() -> None:
    policy = _policy(requested_size=4)
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )
    rendered = str(batch.to_dict()).lower()

    for forbidden in (
        "tunnel vision",
        "poor calculation",
        "weak strategy",
        "missed opponent resource",
        "needs tactics training",
        "pedagogical value",
    ):
        assert forbidden not in rendered
