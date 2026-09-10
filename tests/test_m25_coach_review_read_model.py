"""M25 coach-review read-model fidelity and rejection qualification."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import test_m20_model_coaching_evaluation as m20
import test_m21_diagnostic_candidate_tutor_orchestration as m21
import test_m22_end_to_end_evaluation_fidelity as m22
from test_reasoning_discrepancy_facts import T1, _protocol

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_cli import main as coach_review_main
from chess_mentor_engine.coaching import (
    bind_model_coaching_evaluation,
    build_model_coaching_evaluation_request,
)
from chess_mentor_engine.presentation import build_evaluation_presentation
from chess_mentor_engine.review import (
    COACH_REVIEW_SCHEMA_VERSION,
    CoachReviewReadModelError,
    build_coach_review_read_model,
)
from chess_mentor_engine.tutoring import start_candidate_tutor_session

_GOLDEN = json.loads(
    (
        Path(__file__).parent
        / "fixtures"
        / "m25_coach_review_golden.json"
    ).read_text(encoding="utf-8")
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _rehash(record: dict, id_key: str, prefix: str) -> dict:
    rebuilt = copy.deepcopy(record)
    payload = {
        key: value
        for key, value in rebuilt.items()
        if key not in {id_key, "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    rebuilt["fingerprint"] = fingerprint
    rebuilt[id_key] = f"{prefix}_{fingerprint[:20]}"
    return rebuilt


def _objective_signature(presentation: dict) -> dict[str, object]:
    comparison = presentation["comparison"]
    best = comparison["best_evaluation"]
    child = presentation["played_child_analysis"]
    signature: dict[str, object] = {
        "side_to_move": presentation["subject"]["side_to_move"],
        "root_quality": presentation["root_analysis"]["evidence_quality"],
        "comparison_quality": comparison["evidence_quality"],
        "comparison_kind": comparison["comparison_kind"],
        "exact_delta": comparison["exact_centipawn_delta_for_mover"],
        "best_kind": None if best is None else best["kind"],
        "best_mover_centipawns": None,
        "best_mover_bound": None,
        "child_status": None if child is None else child["status"],
        "child_quality": None if child is None else child["evidence_quality"],
        "child_failure_code": None,
    }
    if best is not None:
        signature["best_mover_bound"] = best["decision_mover"]["bound"]
        if best["kind"] == "centipawn":
            signature["best_mover_centipawns"] = best["decision_mover"][
                "centipawns"
            ]
    if child is not None and child["status"] == "failure":
        signature["child_failure_code"] = child["failure"]["code"]
    return signature


def _m21_sources():
    upstream, authorization = m21._authorization()
    _, session, launch = start_candidate_tutor_session(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=T1,
    )
    presentation = build_evaluation_presentation(
        root_analysis=upstream.analysis,
        comparison=upstream.comparison,
    )
    tutor_state = {
        "tutor_session_id": session.tutor_session_id,
        "snapshot_fingerprint": session.snapshot_fingerprint,
        "state": session.state,
    }
    return upstream, authorization, launch, tutor_state, presentation


def _m20_sources(
    *,
    failed: tuple[str, ...] = (),
    unclear: tuple[str, ...] = (),
    rendered_content: str = "Review the strongest reply first.",
):
    upstream, session, model_request, coaching = m20._m19_sources(rendered_content)
    presentation = build_evaluation_presentation(
        root_analysis=upstream.analysis,
        comparison=upstream.comparison,
    )
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=m20.S15,
    )
    evaluation = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=m20._evaluation_generation(
            request,
            judgments=m20._judgments(failed=failed, unclear=unclear),
        ),
    )
    return presentation, model_request["grounded_feedback"], coaching, evaluation


@pytest.mark.parametrize(
    "case",
    _GOLDEN,
    ids=lambda item: item["scenario"],
)
def test_m25_golden_matrix_preserves_m15_objective_semantics_verbatim(case) -> None:
    *_, presentation = m22._scenario(case["scenario"])
    before = copy.deepcopy(presentation)

    view = build_coach_review_read_model(evaluation_presentation=presentation)

    assert presentation == before
    assert view["schema_version"] == COACH_REVIEW_SCHEMA_VERSION
    assert view["objective_evidence"] == before
    assert _objective_signature(view["objective_evidence"]) == case["expected"]
    assert view["source_fingerprints"]["objective_evidence"] == _fingerprint(before)
    assert view["diagnostic_selection"] is None
    assert view["participant_authority"] is None
    assert view["tutor_state"] is None
    assert view["deterministic_grounding"] is None
    assert view["model_coaching"] is None
    assert view["model_evaluation"] is None


def test_m25_keeps_white_and_decision_mover_score_semantics_explicit() -> None:
    *_, presentation = m22._scenario("bounded_black_perspective")

    view = build_coach_review_read_model(evaluation_presentation=presentation)
    best = view["objective_evidence"]["comparison"]["best_evaluation"]

    assert best["white"] == {"centipawns": -50, "bound": "lower"}
    assert best["decision_mover"] == {
        "side": "black",
        "centipawns": 50,
        "bound": "upper",
    }
    assert view["separation_contract"]["score_semantics_source"] == (
        "objective_evidence.score_semantics"
    )


def test_m25_projects_m18_m21_and_m8_without_creating_new_authority() -> None:
    upstream, authorization, launch, tutor_state, presentation = _m21_sources()

    view = build_coach_review_read_model(
        evaluation_presentation=presentation,
        diagnostic_candidate=upstream.candidate.to_dict(),
        diagnostic_batch=upstream.batch.to_dict(),
        authorization=authorization.to_dict(),
        launch=launch,
        tutor_state=tutor_state,
    )

    assert view["diagnostic_selection"]["candidate"] == upstream.candidate.to_dict()
    assert view["participant_authority"]["authorization"]["actor_kind"] == (
        "participant"
    )
    assert view["participant_authority"]["authorization"]["capture_consent"] == (
        "granted"
    )
    assert view["participant_authority"]["launch"] == launch
    assert view["tutor_state"]["state"] == "selected"
    denied = set(launch["authority_boundary"]["not_created"])
    assert "m6_reasoning_discrepancy" in denied
    assert "m7_learner_hypothesis" in denied
    assert "m9_training_selection" in denied


def test_m25_rejects_m18_candidate_or_batch_drift() -> None:
    upstream, _, _, _, presentation = _m21_sources()
    candidate = copy.deepcopy(upstream.candidate.to_dict())
    candidate["position_id"] = "drifted-position"

    with pytest.raises(CoachReviewReadModelError, match="candidate identity"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            diagnostic_candidate=candidate,
            diagnostic_batch=upstream.batch.to_dict(),
        )

    batch = copy.deepcopy(upstream.batch.to_dict())
    batch["source_candidate_ids"] = []
    with pytest.raises(CoachReviewReadModelError, match="absent from batch"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            diagnostic_candidate=upstream.candidate.to_dict(),
            diagnostic_batch=batch,
        )


def test_m25_rejects_rehashed_authorization_and_launch_reference_drift() -> None:
    upstream, authorization, launch, tutor_state, presentation = _m21_sources()
    auth = copy.deepcopy(authorization.to_dict())
    auth["candidate_fingerprint"] = "drifted-candidate"
    auth = _rehash(auth, "authorization_id", "candidate_tutor_auth")

    with pytest.raises(CoachReviewReadModelError, match="candidate fingerprint"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            diagnostic_candidate=upstream.candidate.to_dict(),
            diagnostic_batch=upstream.batch.to_dict(),
            authorization=auth,
        )

    drifted_launch = copy.deepcopy(launch)
    drifted_launch["candidate_ref"]["fingerprint"] = "drifted-candidate"
    drifted_launch = _rehash(
        drifted_launch,
        "launch_id",
        "candidate_tutor_launch",
    )
    with pytest.raises(CoachReviewReadModelError, match="candidate reference"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            diagnostic_candidate=upstream.candidate.to_dict(),
            diagnostic_batch=upstream.batch.to_dict(),
            authorization=authorization.to_dict(),
            launch=drifted_launch,
            tutor_state=tutor_state,
        )


@pytest.mark.parametrize(
    ("failed", "unclear", "expected"),
    [
        ((), (), "accepted_under_m20_evaluation_policy"),
        (("authority_boundary",), (), "rejected_under_m20_evaluation_policy"),
        ((), ("evidence_sufficiency",), "inconclusive_under_m20_evaluation_policy"),
    ],
)
def test_m25_preserves_bounded_m20_status_without_promoting_it_to_truth(
    failed,
    unclear,
    expected,
) -> None:
    presentation, feedback, coaching, evaluation = _m20_sources(
        failed=failed,
        unclear=unclear,
    )

    view = build_coach_review_read_model(
        evaluation_presentation=presentation,
        grounded_feedback=feedback,
        model_coaching=coaching,
        model_evaluation=evaluation,
    )

    assert view["deterministic_grounding"] == feedback
    assert view["model_coaching"] == coaching
    assert view["model_evaluation"]["qualification_status"] == expected
    assert view["model_evaluation"]["truth_status"] == (
        "not_established_by_m20_evaluation"
    )
    assert view["separation_contract"]["objective_chess_source"] == (
        "objective_evidence"
    )
    assert view["separation_contract"]["model_language_source"] == "model_coaching"


def test_m25_allows_grounding_when_optional_model_output_is_absent() -> None:
    upstream, session, model_request, _ = m20._m19_sources()
    presentation = build_evaluation_presentation(
        root_analysis=upstream.analysis,
        comparison=upstream.comparison,
    )

    view = build_coach_review_read_model(
        evaluation_presentation=presentation,
        grounded_feedback=model_request["grounded_feedback"],
    )

    assert view["deterministic_grounding"] == model_request["grounded_feedback"]
    assert view["model_coaching"] is None
    assert view["model_evaluation"] is None
    assert session.state == "compared"


def test_m25_isolates_model_overclaim_from_objective_evidence() -> None:
    rendered = (
        "Your move loses exactly 325 centipawns, so it is objectively a blunder."
    )
    presentation, feedback, coaching, evaluation = _m20_sources(
        failed=("objective_chess_consistency", "evidence_sufficiency"),
        rendered_content=rendered,
    )

    view = build_coach_review_read_model(
        evaluation_presentation=presentation,
        grounded_feedback=feedback,
        model_coaching=coaching,
        model_evaluation=evaluation,
    )

    assert view["objective_evidence"]["comparison"][
        "exact_centipawn_delta_for_mover"
    ] == 60
    assert view["model_coaching"]["rendered_content"] == rendered
    assert view["model_evaluation"]["qualification_status"] == (
        "rejected_under_m20_evaluation_policy"
    )
    failed = {
        item["dimension"]
        for item in view["model_evaluation"]["judgments"]
        if item["verdict"] == "fail"
    }
    assert failed == {"objective_chess_consistency", "evidence_sufficiency"}


def test_m25_rejects_rehashed_m16_presentation_drift() -> None:
    presentation, feedback, _, _ = _m20_sources()
    drifted = copy.deepcopy(feedback)
    drifted["evaluation_presentation"]["fingerprint"] = "drifted-presentation"
    drifted = _rehash(drifted, "feedback_id", "grounded_feedback")

    with pytest.raises(CoachReviewReadModelError, match="presentation fingerprint"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            grounded_feedback=drifted,
        )


def test_m25_rejects_rehashed_m19_grounding_reference_drift() -> None:
    presentation, feedback, coaching, _ = _m20_sources()
    drifted = copy.deepcopy(coaching)
    drifted["grounded_feedback_ref"]["fingerprint"] = "drifted-feedback"
    drifted = _rehash(drifted, "coaching_id", "model_coaching")

    with pytest.raises(CoachReviewReadModelError, match="grounded feedback reference"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            grounded_feedback=feedback,
            model_coaching=drifted,
        )


def test_m25_rejects_m20_truth_or_qualification_promotion() -> None:
    presentation, feedback, coaching, evaluation = _m20_sources()
    truth_drift = copy.deepcopy(evaluation)
    truth_drift["truth_status"] = "established_objective_truth"
    truth_drift = _rehash(
        truth_drift,
        "evaluation_id",
        "model_coaching_evaluation",
    )
    with pytest.raises(CoachReviewReadModelError, match="truth status"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            grounded_feedback=feedback,
            model_coaching=coaching,
            model_evaluation=truth_drift,
        )

    status_drift = copy.deepcopy(evaluation)
    status_drift["qualification_status"] = "rejected_under_m20_evaluation_policy"
    status_drift = _rehash(
        status_drift,
        "evaluation_id",
        "model_coaching_evaluation",
    )
    with pytest.raises(CoachReviewReadModelError, match="contradicts judgments"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            grounded_feedback=feedback,
            model_coaching=coaching,
            model_evaluation=status_drift,
        )


def test_m25_rejects_invalid_progression_dependencies() -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")

    with pytest.raises(CoachReviewReadModelError, match="supplied together"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            diagnostic_candidate={},
        )
    with pytest.raises(CoachReviewReadModelError, match="requires M16"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            model_coaching={},
        )
    with pytest.raises(CoachReviewReadModelError, match="requires M19"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            model_evaluation={},
        )
    with pytest.raises(CoachReviewReadModelError, match="requires M21 launch"):
        build_coach_review_read_model(
            evaluation_presentation=presentation,
            tutor_state={
                "tutor_session_id": "fixture",
                "snapshot_fingerprint": "fixture",
                "state": "selected",
            },
        )


def test_m25_projection_is_deterministic_and_does_not_mutate_sources() -> None:
    presentation, feedback, coaching, evaluation = _m20_sources()
    inputs = [presentation, feedback, coaching, evaluation]
    before = copy.deepcopy(inputs)

    first = build_coach_review_read_model(
        evaluation_presentation=presentation,
        grounded_feedback=feedback,
        model_coaching=coaching,
        model_evaluation=evaluation,
    )
    second = build_coach_review_read_model(
        evaluation_presentation=presentation,
        grounded_feedback=feedback,
        model_coaching=coaching,
        model_evaluation=evaluation,
    )

    assert first == second
    assert inputs == before
    assert first["read_model_id"] == f"coach_review_{first['fingerprint'][:20]}"


def test_m25_cli_projects_strict_local_bundle(tmp_path, capsys) -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    bundle = {
        "evaluation_presentation": presentation,
        "diagnostic_candidate": None,
        "diagnostic_batch": None,
        "authorization": None,
        "launch": None,
        "tutor_state": None,
        "grounded_feedback": None,
        "model_coaching": None,
        "model_evaluation": None,
    }
    path = tmp_path / "m25-bundle.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    assert coach_review_main([str(path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["schema_version"] == COACH_REVIEW_SCHEMA_VERSION
    assert output["objective_evidence"] == presentation

    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}", encoding="utf-8")
    assert coach_review_main([str(invalid)]) == 2
    assert "shape mismatch" in capsys.readouterr().err
