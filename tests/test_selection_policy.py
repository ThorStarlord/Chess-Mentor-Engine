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
) -> SelectionSignal:
    return SelectionSignal(
        signal_id=f"signal-{comparison.comparison_id}-{kind.lower()}",
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


def _apply(comparison, signals, policy):
    return apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
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


def test_policy_validation_and_configuration_fingerprint() -> None:
    with pytest.raises(ValueError):
        _policy(candidate_min_cp_delta=-1)
    with pytest.raises(ValueError):
        _policy(minimum_controls=5)
    with pytest.raises(ValueError):
        SelectionQuota("EXACT_CP_DELTA", minimum=2, maximum=1)

    first = _policy()
    changed = _policy(candidate_min_cp_delta=75)
    assert first.identity == changed.identity
    assert first.fingerprint != changed.fingerprint


def test_candidate_threshold_is_inclusive_and_rule_is_inspectable() -> None:
    policy = _policy(candidate_min_cp_delta=50)
    below = _comparison(1)
    exact = _comparison(2)

    assert not _apply(
        below,
        (_signal(below, "EXACT_CP_DELTA", 49),),
        policy,
    ).decision.eligible

    result = _apply(
        exact,
        (_signal(exact, "EXACT_CP_DELTA", 50),),
        policy,
    )
    assert result.decision.role == "candidate"
    assert result.candidate is not None
    match = result.decision.matches[0]
    assert (match.rule_id, match.observed_value, match.operator, match.threshold) == (
        "candidate_min_cp_delta",
        50,
        ">=",
        50,
    )


def test_controls_close_choice_mate_and_exclusion_are_policy_owned() -> None:
    control = _comparison(3)
    control_result = _apply(
        control,
        (
            _signal(control, "PLAYED_EQUALS_RANK_1", {"rank": 1}),
            _signal(control, "EXACT_CP_DELTA", 0),
        ),
        _policy(),
    )
    assert control_result.decision.role == "control"

    close = _comparison(4)
    close_result = _apply(
        close,
        (
            _signal(
                close,
                "TOP_CANDIDATE_SEPARATION",
                {"exact_centipawn_separation_for_mover": 20},
            ),
        ),
        _policy(candidate_min_cp_delta=None),
    )
    assert close_result.decision.matches[0].rule_id == "multipv_close_choice"

    mate = _comparison(5)
    mate_result = _apply(
        mate,
        (_signal(mate, "MATE_RELATION", "forced_mate_missed"),),
        _policy(candidate_min_cp_delta=None, close_choice_max_cp=None),
    )
    assert mate_result.decision.matches[0].rule_id == "candidate_mate_relation"

    inverted = _comparison(6)
    excluded = _apply(
        inverted,
        (
            _signal(inverted, "EXACT_CP_DELTA", 100),
            _signal(inverted, "ENGINE_EVIDENCE_INVERSION", {"delta": -5}),
        ),
        _policy(excluded_signal_kinds=("ENGINE_EVIDENCE_INVERSION",)),
    )
    assert not excluded.decision.eligible
    assert excluded.candidate is None


def test_batch_is_input_order_invariant_and_satisfies_control_and_quota() -> None:
    policy = _policy(
        requested_size=4,
        quotas=(SelectionQuota("MATE_RELATION", minimum=1),),
    )
    pool = _batch_pool(policy)
    first = build_diagnostic_candidate_batch(results=pool, policy=policy)
    reversed_batch = build_diagnostic_candidate_batch(
        results=tuple(reversed(pool)),
        policy=policy,
    )

    assert first == reversed_batch
    assert first.actual_size == 4
    assert len(first.control_candidate_ids) == 1
    assert first.quota_outcomes[0].selected_count == 1
    assert first.quota_outcomes[0].shortfall == 0


def test_per_game_cap_and_size_shortfall_are_visible() -> None:
    policy = _policy(requested_size=5, maximum_per_game=2)
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

    assert len([item for item in batch.candidates if item.game_id == "game-a"]) == 2
    assert batch.actual_size == 4
    assert batch.shortfall == 1
    assert any("maximum_per_game" in item.reasons for item in batch.exclusions)


def test_control_and_quota_shortfalls_remain_visible_when_batch_is_full() -> None:
    policy = _policy(
        requested_size=4,
        minimum_controls=2,
        maximum_per_game=None,
        quotas=(SelectionQuota("MATE_RELATION", minimum=2),),
    )
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

    assert batch.actual_size == 4
    assert batch.control_shortfall == 1
    assert batch.quota_outcomes[0].shortfall == 1


def test_quota_maximum_prevents_overrepresentation() -> None:
    policy = _policy(
        requested_size=5,
        maximum_per_game=None,
        quotas=(SelectionQuota("EXACT_CP_DELTA", maximum=2),),
    )
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(policy),
        policy=policy,
    )

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


def test_policy_excluded_positions_never_pad_batch() -> None:
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


def test_policy_configuration_drift_is_rejected_even_under_same_identity() -> None:
    original = _policy()
    changed = _policy(candidate_min_cp_delta=75)
    with pytest.raises(DiagnosticCandidateBatchError):
        build_diagnostic_candidate_batch(
            results=_batch_pool(original),
            policy=changed,
        )


def test_policy_version_changes_candidate_and_batch_identity() -> None:
    first_policy = _policy(version="1", requested_size=1, minimum_controls=0)
    second_policy = _policy(version="2", requested_size=1, minimum_controls=0)
    comparison = _comparison(20, game_id="versioned")
    signals = (_signal(comparison, "EXACT_CP_DELTA", 100),)

    first_result = _apply(comparison, signals, first_policy)
    second_result = _apply(comparison, signals, second_policy)
    first_batch = build_diagnostic_candidate_batch(
        results=(first_result,),
        policy=first_policy,
    )
    second_batch = build_diagnostic_candidate_batch(
        results=(second_result,),
        policy=second_policy,
    )

    assert first_result.candidate is not None
    assert second_result.candidate is not None
    assert first_result.candidate.candidate_id != second_result.candidate.candidate_id
    assert first_batch.batch_id != second_batch.batch_id


def test_m4d_outputs_contain_no_learner_or_pedagogical_labels() -> None:
    batch = build_diagnostic_candidate_batch(
        results=_batch_pool(_policy()),
        policy=_policy(),
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
