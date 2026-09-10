"""M22 hermetic end-to-end evaluation-fidelity qualification matrix."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
import test_m8_qualification as m8
import test_m15_evaluation_presentation as m15
import test_m20_model_coaching_evaluation as m20

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    CentipawnEvaluation,
    MateEvaluation,
)
from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    ModelCoachingError,
    ModelCoachingEvaluationError,
    ModelCoachingGeneration,
    bind_model_coaching_evaluation,
    bind_model_coaching_response,
    build_model_coaching_evaluation_request,
)
from chess_mentor_engine.feedback import (
    GroundedFeedbackError,
    compose_grounded_mentor_feedback,
)
from chess_mentor_engine.presentation import (
    EvaluationPresentationError,
    build_evaluation_presentation,
)
from chess_mentor_engine.selection import compare_played_decision

_MATRIX_PATH = (
    Path(__file__).parent / "fixtures" / "m22_evaluation_fidelity_matrix.json"
)
_MATRIX_CASES = json.loads(_MATRIX_PATH.read_text(encoding="utf-8"))
_REQUIRED_SCENARIOS = {
    "exact_white_root_multipv",
    "bounded_black_perspective",
    "symbolic_terminal_mate",
    "partial_root",
    "empty_complete_root",
    "compatible_child_reanalysis",
    "incompatible_child_regime",
    "failed_child",
}


def _sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _rehash_content_addressed_record(record: dict, prefix: str) -> dict:
    rebuilt = copy.deepcopy(record)
    payload = {
        key: value
        for key, value in rebuilt.items()
        if key not in {"request_id", "fingerprint"}
    }
    fingerprint = _sha256(payload)
    rebuilt["fingerprint"] = fingerprint
    rebuilt["request_id"] = f"{prefix}_{fingerprint[:20]}"
    return rebuilt


def _scenario(name: str):
    if name == "exact_white_root_multipv":
        game = m15._game()
        position = game.positions[0]
        root = m15._analysis(
            position,
            (
                m15._line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),
                m15._line(2, "e2e4", CentipawnEvaluation(10), "e7e5"),
            ),
        )
        played = None
    elif name == "bounded_black_perspective":
        game = m15._game()
        position = game.positions[1]
        root = m15._analysis(
            position,
            (
                m15._line(
                    1,
                    "c7c5",
                    CentipawnEvaluation(-50, bound="lower"),
                    "g1f3",
                ),
                m15._line(2, "e7e5", CentipawnEvaluation(-20), "g1f3"),
            ),
        )
        played = None
    elif name == "symbolic_terminal_mate":
        game = m15._game(m15.MATE_PGN)
        position = game.positions[3]
        root = m15._analysis(
            position,
            (m15._line(1, "d8h4", MateEvaluation("black", 1)),),
            request=m15._request(1),
        )
        played = None
    elif name == "partial_root":
        game = m15._game()
        position = game.positions[0]
        root = m15._analysis(
            position,
            (m15._line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
            request=m15._request(2),
            status="partial",
        )
        played = None
    elif name == "empty_complete_root":
        game = m15._game()
        position = game.positions[0]
        root = m15._analysis(position, (), request=m15._request(1))
        played = None
    elif name in {"compatible_child_reanalysis", "incompatible_child_regime"}:
        game = m15._game()
        position = game.positions[0]
        request = m15._request(1)
        root_engine = m15._provenance("FidelityFish A")
        child_engine = root_engine
        if name == "incompatible_child_regime":
            child_engine = m15._provenance("FidelityFish B")
        root = m15._analysis(
            position,
            (m15._line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
            request=request,
            provenance=root_engine,
        )
        played = m15._analysis(
            game.positions[1],
            (m15._line(1, "e7e5", CentipawnEvaluation(20), "g1f3"),),
            request=request,
            provenance=child_engine,
        )
    elif name == "failed_child":
        game = m15._game()
        position = game.positions[0]
        root = m15._analysis(
            position,
            (m15._line(1, "d2d4", CentipawnEvaluation(40), "d7d5"),),
            request=m15._request(1),
        )
        child_position = game.positions[1]
        played = AnalysisFailure(
            position_id=child_position.position_id,
            fen=child_position.fen,
            request_fingerprint="m22-child-failure-request",
            code="ENGINE_CRASHED",
            message="hermetic M22 failure fixture",
        )
    else:  # pragma: no cover - guarded by fixture completeness test
        raise AssertionError(f"unknown M22 scenario: {name}")

    comparison = compare_played_decision(
        game=game,
        position=position,
        root_analysis=root,
        played_analysis=played,
    )
    presentation = build_evaluation_presentation(
        root_analysis=root,
        comparison=comparison,
        played_analysis=played,
    )
    return game, position, root, comparison, played, presentation


def _evaluation_fields(evaluation: dict | None, prefix: str) -> dict[str, object]:
    values: dict[str, object] = {f"{prefix}_kind": None}
    if evaluation is None:
        return values
    values[f"{prefix}_kind"] = evaluation["kind"]
    if evaluation["kind"] == "centipawn":
        values.update(
            {
                f"{prefix}_white_centipawns": evaluation["white"]["centipawns"],
                f"{prefix}_white_bound": evaluation["white"]["bound"],
                f"{prefix}_mover_centipawns": evaluation["decision_mover"][
                    "centipawns"
                ],
                f"{prefix}_mover_bound": evaluation["decision_mover"]["bound"],
            }
        )
    else:
        values.update(
            {
                f"{prefix}_mate_winner": evaluation["winner"],
                f"{prefix}_plies_to_mate": evaluation["plies_to_mate"],
                f"{prefix}_mover_favours": evaluation["decision_mover"][
                    "favours_perspective"
                ],
                f"{prefix}_mover_bound": evaluation["decision_mover"]["bound"],
            }
        )
    return values


def _presentation_signature(presentation: dict) -> dict[str, object]:
    comparison = presentation["comparison"]
    child = presentation["played_child_analysis"]
    signature: dict[str, object] = {
        "side_to_move": presentation["subject"]["side_to_move"],
        "root_evidence_quality": presentation["root_analysis"]["evidence_quality"],
        "comparison_evidence_quality": comparison["evidence_quality"],
        "comparison_kind": comparison["comparison_kind"],
        "preference": comparison["preference"],
        "played_evaluation_source": comparison["played_evaluation_source"],
        "compatibility": comparison["compatibility"],
        "exact_centipawn_delta_for_mover": comparison[
            "exact_centipawn_delta_for_mover"
        ],
        "mate_relation": comparison["mate_relation"],
        "terminal_outcome": comparison["terminal_outcome"],
        "child_status": None if child is None else child["status"],
        "child_evidence_quality": (
            None if child is None else child["evidence_quality"]
        ),
        "child_failure_code": (
            None
            if child is None or child["status"] != "failure"
            else child["failure"]["code"]
        ),
    }
    signature.update(_evaluation_fields(comparison["best_evaluation"], "best"))
    signature.update(_evaluation_fields(comparison["played_evaluation"], "played"))
    return signature


def test_matrix_declares_each_required_semantic_regime_once() -> None:
    case_ids = [item["case_id"] for item in _MATRIX_CASES]
    scenarios = [item["scenario"] for item in _MATRIX_CASES]

    assert len(case_ids) == len(set(case_ids))
    assert len(scenarios) == len(set(scenarios))
    assert set(scenarios) == _REQUIRED_SCENARIOS


@pytest.mark.parametrize(
    "case",
    _MATRIX_CASES,
    ids=lambda item: item["case_id"],
)
def test_m3_m4_to_m15_matrix_preserves_declared_evaluation_semantics(case) -> None:
    _, _, root, comparison, played, presentation = _scenario(case["scenario"])
    signature = _presentation_signature(presentation)

    for field, expected in case["expected"].items():
        assert signature[field] == expected, (
            f"{case['case_id']} changed fidelity field {field}: "
            f"expected {expected!r}, got {signature[field]!r}"
        )

    assert presentation["evidence_refs"]["root_analysis"] == (
        comparison.root_analysis_ref.to_dict()
    )
    assert presentation["root_analysis"]["result_fingerprint"] == (
        root.result_fingerprint
    )
    if played is None:
        assert presentation["played_child_analysis"] is None
    elif isinstance(played, AnalysisFailure):
        assert presentation["played_child_analysis"]["result_fingerprint"] is None
        assert presentation["played_child_analysis"]["failure"]["code"] == played.code
    else:
        assert presentation["played_child_analysis"]["result_fingerprint"] == (
            played.result_fingerprint
        )

    if comparison.comparison_kind in {
        "partial_evidence",
        "bound_limited",
        "incompatible_analysis_regime",
        "incomparable",
    }:
        assert presentation["comparison"]["exact_centipawn_delta_for_mover"] is None

    best = presentation["comparison"]["best_evaluation"]
    if best is not None and best["kind"] == "mate":
        assert "centipawns" not in best


def test_exact_chain_preserves_same_evaluation_through_m15_m16_m19_and_m20() -> None:
    upstream, session, model_request, coaching, m20_request = m20._m20_request()
    presentation = build_evaluation_presentation(
        root_analysis=upstream.analysis,
        comparison=upstream.comparison,
    )
    feedback = compose_grounded_mentor_feedback(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=m8.S13,
    )

    assert presentation["comparison"]["exact_centipawn_delta_for_mover"] == 60
    assert feedback == model_request["grounded_feedback"]
    assert feedback["evaluation_presentation"]["fingerprint"] == _sha256(presentation)
    assert "60 centipawns worse" in feedback["sections"][0]["content"]

    assert coaching["request_id"] == model_request["request_id"]
    assert coaching["request_fingerprint"] == model_request["fingerprint"]
    assert coaching["grounded_feedback_ref"]["feedback_id"] == feedback["feedback_id"]
    assert coaching["grounded_feedback_ref"]["fingerprint"] == feedback["fingerprint"]

    assert m20_request["evaluation_presentation"] == presentation
    assert m20_request["grounded_feedback"] == feedback
    assert m20_request["rendered_content"] == coaching["rendered_content"]
    assert m20_request["model_provenance"] == coaching["model_provenance"]

    evaluation = bind_model_coaching_evaluation(
        request=m20_request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=m20._evaluation_generation(m20_request),
    )
    assert evaluation["qualification_status"] == "accepted_under_m20_evaluation_policy"
    assert evaluation["source_integrity"] == "verified_against_exact_m16_m19_sources"
    assert evaluation["grounded_feedback_ref"]["feedback_id"] == feedback["feedback_id"]
    assert evaluation["grounded_feedback_ref"]["fingerprint"] == feedback["fingerprint"]
    assert evaluation["model_coaching_ref"]["coaching_id"] == coaching["coaching_id"]
    assert evaluation["truth_status"] == "not_established_by_m20_evaluation"


def test_model_overclaim_is_rejected_without_mutating_true_source_evaluation() -> None:
    rendered = "Your move loses exactly 325 centipawns, so it is objectively a blunder."
    upstream, session, model_request, coaching = m20._m19_sources(rendered)
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=m20.S15,
    )
    generation = m20._evaluation_generation(
        request,
        judgments=m20._judgments(
            failed=("objective_chess_consistency", "evidence_sufficiency")
        ),
    )
    evaluation = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=generation,
    )

    assert request["evaluation_presentation"]["comparison"][
        "exact_centipawn_delta_for_mover"
    ] == 60
    assert "60 centipawns worse" in request["grounded_feedback"]["sections"][0][
        "content"
    ]
    assert request["rendered_content"] == rendered
    assert evaluation["qualification_status"] == "rejected_under_m20_evaluation_policy"
    failed = {
        item["dimension"]
        for item in evaluation["judgments"]
        if item["verdict"] == "fail"
    }
    assert failed == {"objective_chess_consistency", "evidence_sufficiency"}


def test_rehashed_m20_presentation_drift_is_rejected_against_exact_sources() -> None:
    upstream, session, model_request, coaching, request = m20._m20_request()
    tampered = copy.deepcopy(request)
    tampered["evaluation_presentation"]["comparison"][
        "exact_centipawn_delta_for_mover"
    ] = 999
    tampered = _rehash_content_addressed_record(
        tampered,
        "model_coaching_evaluation_request",
    )

    with pytest.raises(
        ModelCoachingEvaluationError,
        match="does not match current sources",
    ):
        bind_model_coaching_evaluation(
            request=tampered,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=m20._evaluation_generation(tampered),
        )


def test_rehashed_m19_grounding_drift_is_rejected_against_recomputed_m16() -> None:
    upstream, session, model_request, _ = m20._m19_sources()
    tampered = copy.deepcopy(model_request)
    tampered["grounded_feedback"]["sections"][0]["content"] += (
        " Rehashed M22 semantic drift."
    )
    tampered = _rehash_content_addressed_record(tampered, "model_coaching_request")
    generation = ModelCoachingGeneration(
        request_id=tampered["request_id"],
        request_fingerprint=tampered["fingerprint"],
        rendered_content="Hermetic fixture output.",
        provider_id="m22-fixture-provider",
        model_id="m22-fixture-model",
        model_version="1",
        run_id="m22-rehashed-grounding-drift",
        generated_at=m8.S14,
    )

    with pytest.raises(
        ModelCoachingError,
        match="does not match current grounded evidence",
    ):
        bind_model_coaching_response(
            request=tampered,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=generation,
        )


def test_m15_rejects_source_reference_drift_instead_of_reprojecting_it() -> None:
    _, _, root, comparison, _, _ = _scenario("exact_white_root_multipv")
    drifted_ref = replace(
        comparison.root_analysis_ref,
        result_fingerprint="m22-drifted-result",
    )
    drifted = replace(comparison, root_analysis_ref=drifted_ref)

    with pytest.raises(EvaluationPresentationError, match="root evidence reference"):
        build_evaluation_presentation(
            root_analysis=root,
            comparison=drifted,
        )


def test_m16_rejects_analysis_drift_instead_of_rewording_feedback() -> None:
    upstream, session, _ = m8._through_compare()
    drifted = replace(
        upstream.analysis,
        result_fingerprint="m22-not-the-bound-analysis",
    )

    with pytest.raises(GroundedFeedbackError, match="not bound into the M6"):
        compose_grounded_mentor_feedback(
            session=session,
            root_analysis=drifted,
            decision_comparison=upstream.comparison,
            created_at=m8.S13,
        )
