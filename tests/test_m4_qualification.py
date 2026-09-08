from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisMetrics,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineProvenance,
    MateEvaluation,
    PositionAnalysis,
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from chess_mentor_engine.chess import build_position_features, ingest_pgn
from chess_mentor_engine.selection import (
    SelectionPolicy,
    SelectionQuota,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)

CORPUS_PATH = Path(__file__).parent / "fixtures" / "m4q_selection_corpus.json"

REQUIRED_CATEGORIES = {
    "obvious_large_exact_centipawn_loss",
    "quiet_engine_preferred_move",
    "side_to_move_in_check_defensive_decision",
    "multiple_close_engine_candidates",
    "clearly_separated_top_candidate",
    "forced_mate_missed",
    "forced_mate_allowed",
    "correct_rank1_played_move",
    "correct_quiet_control_decision",
    "custom_fen_decision",
    "promotion_decision",
    "prior_research_board_context_position",
}


def _manifest() -> dict[str, Any]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def _provenance() -> EngineProvenance:
    return EngineProvenance(
        provider_name="m4q-corpus",
        provider_version="1",
        protocol="precomputed",
        engine_name="fixture-engine",
        engine_version="2026.09",
        binary_sha256="m4q-fixture-binary",
        engine_options=(("Hash", "16"), ("Threads", "1")),
    )


def _request(*, multipv: int, depth: int = 12) -> AnalysisRequest:
    return AnalysisRequest(
        multipv=multipv,
        search_limit=AnalysisLimit("depth", depth),
        supervisor_timeout_ms=5_000,
    )


def _evaluation(spec: dict[str, Any]):
    if spec["kind"] == "cp":
        return CentipawnEvaluation(
            spec["value"],
            bound=spec.get("bound", "exact"),
        )
    if spec["kind"] == "mate":
        return MateEvaluation(
            spec["winner"],
            spec["plies"],
            bound=spec.get("bound", "exact"),
        )
    raise AssertionError(f"unknown frozen evaluation kind: {spec['kind']}")


def _analysis(position, line_specs, *, status: str = "complete", depth: int = 12):
    lines = tuple(
        CandidateLine(
            rank=spec["rank"],
            root_move_uci=spec["move"],
            evaluation=_evaluation(spec["evaluation"]),
        )
        for spec in line_specs
    )
    request = _request(multipv=max(1, len(lines)), depth=depth)
    provenance = _provenance()
    request_fingerprint = analysis_request_fingerprint(
        fen=position.fen,
        request=request,
        provenance=provenance,
    )
    termination = (
        AnalysisTermination("timeout")
        if status == "partial"
        else AnalysisTermination("completed")
    )
    record = PositionAnalysis(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=request_fingerprint,
        result_fingerprint="",
        status=status,
        request=request,
        provenance=provenance,
        lines=lines,
        metrics=AnalysisMetrics(depth=depth),
        termination=termination,
    )
    return replace(record, result_fingerprint=analysis_result_fingerprint(record))


def _failure(position) -> AnalysisFailure:
    request = _request(multipv=1)
    provenance = _provenance()
    return AnalysisFailure(
        position_id=position.position_id,
        fen=position.fen,
        request_fingerprint=analysis_request_fingerprint(
            fen=position.fen,
            request=request,
            provenance=provenance,
        ),
        code="ANALYSIS_TIMEOUT",
        message="frozen M4Q failure fixture",
    )


def _balanced_policy(*, version: str = "1") -> SelectionPolicy:
    return SelectionPolicy(
        policy_id="m4q-balanced-selection",
        version=version,
        requested_size=10,
        candidate_min_cp_delta=50,
        control_max_cp_delta=0,
        close_choice_max_cp=10,
        candidate_mate_relations=(
            "forced_mate_allowed",
            "forced_mate_missed",
        ),
        include_rank1_controls=True,
        excluded_signal_kinds=("ENGINE_EVIDENCE_INVERSION",),
        minimum_controls=4,
        quotas=(
            SelectionQuota("MATE_RELATION", minimum=2, maximum=2),
            SelectionQuota("ROOT_SIDE_IS_IN_CHECK", minimum=1, maximum=1),
        ),
    )


def _shortfall_policy() -> SelectionPolicy:
    return SelectionPolicy(
        policy_id="m4q-deliberate-shortfall",
        version="1",
        requested_size=12,
        candidate_min_cp_delta=500,
        control_max_cp_delta=0,
        close_choice_max_cp=None,
        candidate_mate_relations=("forced_mate_missed",),
        include_rank1_controls=True,
        minimum_controls=8,
        maximum_per_game=1,
        quotas=(SelectionQuota("MATE_RELATION", minimum=2, maximum=2),),
    )


def _run_case(case: dict[str, Any], policy: SelectionPolicy):
    game = ingest_pgn(case["pgn"]).games[0]
    root = game.positions[0]
    analysis = _analysis(root, case["lines"])
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=build_position_features(root),
        root_analysis=analysis,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )
    return game, root, analysis, comparison, signals, result


def _all_results(policy: SelectionPolicy):
    return tuple(
        _run_case(case, policy)[-1]
        for case in _manifest()["cases"]
    )


def _signal(signals, kind: str):
    return next(item for item in signals if item.kind == kind)


def test_m4q_manifest_freezes_every_required_m4a_category() -> None:
    manifest = _manifest()
    cases = manifest["cases"]

    assert manifest["schema_version"] == "1"
    assert {case["category"] for case in cases} == REQUIRED_CATEGORIES
    assert len(cases) == 12
    assert len({case["id"] for case in cases}) == len(cases)


def test_m4q_frozen_corpus_matches_the_full_objective_contract() -> None:
    policy = _balanced_policy()

    for case in _manifest()["cases"]:
        _, root, _, comparison, signals, result = _run_case(case, policy)
        kinds = {signal.kind for signal in signals}

        assert comparison.comparison_kind == case["expected_comparison_kind"]
        if "expected_fen" in case:
            assert root.fen == case["expected_fen"]
        if "expected_exact_cp_delta" in case:
            assert (
                comparison.exact_centipawn_delta_for_mover
                == case["expected_exact_cp_delta"]
            )
        if "expected_mate_relation" in case:
            assert comparison.mate_relation == case["expected_mate_relation"]
        assert set(case["expected_signals"]).issubset(kinds)

        if "expected_top_separation" in case:
            separation = _signal(signals, "TOP_CANDIDATE_SEPARATION")
            assert (
                separation.raw_value["exact_centipawn_separation_for_mover"]
                == case["expected_top_separation"]
            )

        if result.candidate is not None:
            candidate = result.candidate
            assert result.decision.eligible
            assert result.decision.matches
            assert candidate.selection_policy == policy.identity
            assert (
                result.decision.policy_fingerprint
                == policy.fingerprint
            )
            assert (
                candidate.eligibility_signal_ids
                == result.decision.eligibility_signal_ids
            )
            candidate_signals = {
                signal.signal_id: signal for signal in candidate.signals
            }
            for match in result.decision.matches:
                assert match.signal_id in candidate.eligibility_signal_ids
                signal = candidate_signals[match.signal_id]
                assert signal.evidence
                assert all(ref.source and ref.ref_id for ref in signal.evidence)
        else:
            assert not result.decision.eligible
            assert result.decision.exclusion_reasons


def test_m4q_balanced_batch_is_order_stable_and_control_aware() -> None:
    policy = _balanced_policy()
    results = _all_results(policy)

    first = build_diagnostic_candidate_batch(results=results, policy=policy)
    reversed_batch = build_diagnostic_candidate_batch(
        results=tuple(reversed(results)),
        policy=policy,
    )

    assert first == reversed_batch
    assert first.source_pool_count == 12
    assert first.actual_size == 10
    assert first.shortfall == 0
    assert first.control_shortfall == 0
    assert len(first.control_candidate_ids) >= 4
    assert len({item.candidate_id for item in first.candidates}) == first.actual_size
    assert all(outcome.shortfall == 0 for outcome in first.quota_outcomes)
    assert first.source_pool_fingerprint
    assert first.policy_fingerprint == policy.fingerprint

    excluded_by_position = {
        item.position_id: item.reasons for item in first.exclusions
    }
    research = _run_case(
        next(
            case
            for case in _manifest()["cases"]
            if case["id"] == "research_board_context"
        ),
        policy,
    )[-1]
    assert research.decision.position_id in excluded_by_position
    assert "no_eligibility_rule_matched" in excluded_by_position[
        research.decision.position_id
    ]


def test_m4q_policy_version_changes_policy_derived_identity_only() -> None:
    first_policy = _balanced_policy(version="1")
    second_policy = _balanced_policy(version="2")
    first_runs = [
        _run_case(case, first_policy)
        for case in _manifest()["cases"]
    ]
    second_runs = [
        _run_case(case, second_policy)
        for case in _manifest()["cases"]
    ]

    for first, second in zip(first_runs, second_runs, strict=True):
        assert first[3].comparison_id == second[3].comparison_id
        assert tuple(item.signal_id for item in first[4]) == tuple(
            item.signal_id for item in second[4]
        )
        assert first[5].decision.policy != second[5].decision.policy
        assert (
            first[5].decision.policy_fingerprint
            != second[5].decision.policy_fingerprint
        )

    first_batch = build_diagnostic_candidate_batch(
        results=tuple(item[-1] for item in first_runs),
        policy=first_policy,
    )
    second_batch = build_diagnostic_candidate_batch(
        results=tuple(item[-1] for item in second_runs),
        policy=second_policy,
    )
    assert first_batch.batch_id != second_batch.batch_id


def test_m4q_shortfalls_and_per_game_caps_are_visible_not_padded() -> None:
    policy = _shortfall_policy()
    results = _all_results(policy)
    batch = build_diagnostic_candidate_batch(results=results, policy=policy)

    assert batch.actual_size < batch.requested_size
    assert batch.shortfall == batch.requested_size - batch.actual_size
    assert batch.shortfall > 0
    assert batch.control_shortfall > 0
    assert any(outcome.shortfall > 0 for outcome in batch.quota_outcomes)
    assert all(item.reasons for item in batch.exclusions)
    assert any(
        "maximum_per_game" in item.reasons
        for item in batch.exclusions
    )


def test_m4q_terminal_child_can_flow_to_a_policy_candidate() -> None:
    pgn = """
[Event "M4Q Terminal"]
[SetUp "1"]
[FEN "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"]
[Result "1-0"]

1. Qg7# 1-0
"""
    game = ingest_pgn(pgn).games[0]
    root = game.positions[0]
    analysis = _analysis(
        root,
        [
            {
                "rank": 1,
                "move": "f7g7",
                "evaluation": {
                    "kind": "mate",
                    "winner": "white",
                    "plies": 1,
                },
            }
        ],
    )
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=build_position_features(root),
        root_analysis=analysis,
    )
    policy = SelectionPolicy(
        policy_id="m4q-terminal",
        version="1",
        requested_size=1,
        candidate_mate_relations=("forced_mate_completed",),
        control_max_cp_delta=None,
        include_rank1_controls=False,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=policy,
    )
    batch = build_diagnostic_candidate_batch(results=(result,), policy=policy)

    assert comparison.comparison_kind == "terminal_relation"
    assert comparison.terminal_outcome == "checkmate"
    assert comparison.mate_relation == "forced_mate_completed"
    assert _signal(signals, "MATE_RELATION")
    assert result.decision.role == "candidate"
    assert batch.actual_size == 1


def test_m4q_incomplete_bound_failure_and_inversion_states_remain_explicit() -> None:
    case = next(
        item
        for item in _manifest()["cases"]
        if item["id"] == "large_exact_cp_loss"
    )
    game = ingest_pgn(case["pgn"]).games[0]
    root = game.positions[0]
    features = build_position_features(root)
    policy = _balanced_policy()

    partial = _analysis(root, case["lines"], status="partial")
    partial_comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=partial,
    )
    partial_signals = build_selection_signals(
        comparison=partial_comparison,
        root_features=features,
        root_analysis=partial,
    )
    partial_result = apply_selection_policy(
        comparison=partial_comparison,
        signals=partial_signals,
        policy=policy,
    )
    assert partial_comparison.comparison_kind == "partial_evidence"
    assert not any(item.kind == "EXACT_CP_DELTA" for item in partial_signals)
    assert not partial_result.decision.eligible

    bound_lines = json.loads(json.dumps(case["lines"]))
    bound_lines[1]["evaluation"]["bound"] = "lower"
    bound = _analysis(root, bound_lines)
    bound_comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=bound,
    )
    bound_signals = build_selection_signals(
        comparison=bound_comparison,
        root_features=features,
        root_analysis=bound,
    )
    bound_result = apply_selection_policy(
        comparison=bound_comparison,
        signals=bound_signals,
        policy=policy,
    )
    assert bound_comparison.comparison_kind == "bound_limited"
    assert not any(item.kind == "EXACT_CP_DELTA" for item in bound_signals)
    assert not bound_result.decision.eligible

    failure = _failure(root)
    failure_comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=failure,
    )
    failure_signals = build_selection_signals(
        comparison=failure_comparison,
        root_features=features,
        root_analysis=failure,
    )
    failure_result = apply_selection_policy(
        comparison=failure_comparison,
        signals=failure_signals,
        policy=policy,
    )
    assert failure_comparison.comparison_kind == "incomparable"
    assert not any(item.kind == "EXACT_CP_DELTA" for item in failure_signals)
    assert not failure_result.decision.eligible

    inversion_lines = [
        {"rank": 1, "move": "e2e4", "evaluation": {"kind": "cp", "value": 20}},
        {"rank": 2, "move": "d2d4", "evaluation": {"kind": "cp", "value": 30}},
    ]
    inversion = _analysis(root, inversion_lines)
    inversion_comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=inversion,
    )
    inversion_signals = build_selection_signals(
        comparison=inversion_comparison,
        root_features=features,
        root_analysis=inversion,
    )
    inversion_result = apply_selection_policy(
        comparison=inversion_comparison,
        signals=inversion_signals,
        policy=policy,
    )
    assert inversion_comparison.comparison_kind == "engine_evidence_inversion"
    assert _signal(inversion_signals, "ENGINE_EVIDENCE_INVERSION")
    assert not inversion_result.decision.eligible
    assert inversion_result.decision.exclusion_reasons == (
        "excluded_signal_kind:ENGINE_EVIDENCE_INVERSION",
    )


def test_m4q_incompatible_child_reanalysis_never_becomes_severity() -> None:
    pgn = """
[Event "M4Q Compatibility"]
[Result "*"]

1. d4 *
"""
    game = ingest_pgn(pgn).games[0]
    root = game.positions[0]
    child = game.positions[1]
    root_analysis = _analysis(
        root,
        [
            {"rank": 1, "move": "e2e4", "evaluation": {"kind": "cp", "value": 35}}
        ],
        depth=12,
    )
    child_analysis = _analysis(
        child,
        [
            {"rank": 1, "move": "d7d5", "evaluation": {"kind": "cp", "value": 5}}
        ],
        depth=14,
    )
    comparison = compare_played_decision(
        game=game,
        position=root,
        root_analysis=root_analysis,
        played_analysis=child_analysis,
    )
    signals = build_selection_signals(
        comparison=comparison,
        root_features=build_position_features(root),
        root_analysis=root_analysis,
    )
    result = apply_selection_policy(
        comparison=comparison,
        signals=signals,
        policy=_balanced_policy(),
    )

    assert comparison.comparison_kind == "incompatible_analysis_regime"
    assert comparison.exact_centipawn_delta_for_mover is None
    assert not any(item.kind == "EXACT_CP_DELTA" for item in signals)
    assert not result.decision.eligible


def test_m4q_outputs_respect_the_frozen_claim_ceiling() -> None:
    policy = _balanced_policy()
    results = _all_results(policy)
    batch = build_diagnostic_candidate_batch(results=results, policy=policy)
    rendered = json.dumps(
        {
            "results": [item.to_dict() for item in results],
            "batch": batch.to_dict(),
        },
        sort_keys=True,
    ).lower()

    for forbidden in (
        "poor calculation",
        "failed candidate generation",
        "missed opponent resource",
        "tunnel vision",
        "bad planning",
        "weak strategic understanding",
        "needs tactics training",
        "high-value teaching moment",
        "best teaching opportunity",
        "learner weakness",
        "pedagogical value",
    ):
        assert forbidden not in rendered
