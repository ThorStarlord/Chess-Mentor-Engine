"""M26 persistent compared-session to reviewed-coaching qualification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from test_m23_diagnostic_to_persistent_tutor_cli import _queue
from test_m24_provider_conformance import (
    S15,
    _Evaluator,
    _Provider,
    _evaluator_endpoint,
    _provider_endpoint,
)
from test_m8_qualification import (
    S0,
    S1,
    S2,
    S3,
    S4,
    S5,
    S6,
    S7,
    S8,
    S11,
    S13,
    _m6_bundle,
)
from test_reasoning_discrepancy_facts import (
    _a1_prompt,
    _a2_prompt,
    _default_a1,
    _default_a2,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import build_position_context, canonical_json
from chess_mentor_engine.evidence import (
    reference_decision_comparison,
    reference_position_analysis,
    reference_selection_signal,
)
from chess_mentor_engine.reviewed_coaching import (
    M18_QUEUE_KIND,
    M21_AUTH_KIND,
    M21_LAUNCH_KIND,
    M26_SCHEMA_VERSION,
    PersistentReviewedCoachingError,
    run_persistent_reviewed_coaching,
)
from chess_mentor_engine.reviewed_coaching_cli import main as reviewed_main
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    load_tutor_session,
    prepare_artifact,
    save_tutor_session,
)
from chess_mentor_engine.storage.tutor import SESSION_KIND
from chess_mentor_engine.tutoring import (
    capture_tutor_response,
    freeze_tutor_response,
    present_tutor_capture_stage,
    present_tutor_position,
    record_candidate_tutor_authorization,
    record_tutor_reasoning_comparison,
    reveal_tutor_objective_evidence,
    start_candidate_tutor_session,
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _ref(value: dict) -> ArtifactRef:
    return ArtifactRef(**value)


def _invoke(capsys, *argv: str):
    code = reviewed_main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _compared_session():
    upstream = _upstream()
    authorization = record_candidate_tutor_authorization(
        participant_id="P01",
        candidate=upstream.candidate,
        batch=upstream.batch,
        selection_decision="selected",
        capture_consent="granted",
        recorded_at=S0,
    )
    _, session, launch = start_candidate_tutor_session(
        authorization=authorization,
        candidate=upstream.candidate,
        batch=upstream.batch,
        game=upstream.game,
        position=upstream.position,
        capture_protocol=_protocol(),
        created_at=S0,
    )
    selected = session
    session, _ = present_tutor_position(
        session,
        position_context=build_position_context(upstream.game, upstream.position),
        shown_at=S1,
    )
    session = present_tutor_capture_stage(
        session,
        stage_id="A1",
        prompt=_a1_prompt(),
        shown_at=S2,
    )
    session = capture_tutor_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        structured_response=_default_a1(),
        submitted_at=S3,
    )
    session = freeze_tutor_response(session, stage_id="A1", frozen_at=S4)
    session = present_tutor_capture_stage(
        session,
        stage_id="A2",
        prompt=_a2_prompt(),
        shown_at=S5,
    )
    session = capture_tutor_response(
        session,
        stage_id="A2",
        raw_response="I considered e4 and expect ...e5 followed by Nf3.",
        structured_response=_default_a2(),
        submitted_at=S6,
    )
    session = freeze_tutor_response(session, stage_id="A2", frozen_at=S7)
    session = reveal_tutor_objective_evidence(
        session,
        revealed_at=S8,
        rendered_content="Qualified objective evidence: d4 is rank 1.",
        position_analysis_refs=(reference_position_analysis(upstream.analysis),),
        decision_comparison_ref=reference_decision_comparison(upstream.comparison),
        selection_signal_refs=tuple(
            reference_selection_signal(item) for item in upstream.signals
        ),
    )
    context, assessment, assertions = _m6_bundle(
        upstream,
        session.capture_session,
    )
    session, _ = record_tutor_reasoning_comparison(
        session,
        reasoning_context=context,
        assessment=assessment,
        assertions=assertions,
        recorded_at=S11,
    )
    assert session.state == "compared"
    return upstream, authorization, launch, selected, session


def _store_lineage(
    tmp_path: Path,
    *,
    queue_artifact_id: str | None = None,
    with_launch_dependency: bool = True,
):
    upstream, authorization, launch, selected, compared = _compared_session()
    queue = _queue()
    db = tmp_path / "mentor.sqlite3"
    store = LocalArtifactStore(db)

    queue_id = queue_artifact_id or f"diagnostic_queue_{_fingerprint(queue)[:20]}"
    queue_write = ArtifactWrite(M18_QUEUE_KIND, queue_id, "P01", queue)
    queue_ref = prepare_artifact(queue_write)[0]
    auth_write = ArtifactWrite(
        M21_AUTH_KIND,
        authorization.authorization_id,
        "P01",
        authorization.to_dict(),
        (queue_ref,),
    )
    auth_ref = prepare_artifact(auth_write)[0]
    launch_write = ArtifactWrite(
        M21_LAUNCH_KIND,
        launch["launch_id"],
        "P01",
        launch,
        (auth_ref,),
    )
    launch_ref = prepare_artifact(launch_write)[0]
    store.put_many((queue_write, auth_write, launch_write))

    dependencies = (launch_ref,) if with_launch_dependency else ()
    prompts = (_a1_prompt(), _a2_prompt())
    selected_ref = save_tutor_session(
        store,
        selected,
        prompts=prompts,
        dependencies=dependencies,
    )
    compared_ref = save_tutor_session(
        store,
        compared,
        prompts=prompts,
        dependencies=dependencies,
    )
    return store, db, selected_ref, compared_ref


def _kind_count(store: LocalArtifactStore, kind: str) -> int:
    return len(store.list_refs(participant_id="P01", kind=kind))


def test_repository_cli_persists_m16_m25_and_m26_without_advancing_m8(
    tmp_path,
    capsys,
) -> None:
    store, db, _, compared_ref = _store_lineage(tmp_path)
    session_count = _kind_count(store, SESSION_KIND)

    code, payload, error = _invoke(
        capsys,
        compared_ref.artifact_id,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--created-at",
        S13,
    )

    assert code == 0 and error == ""
    assert payload["schema_version"] == M26_SCHEMA_VERSION
    assert payload["source_state"] == "compared"
    assert payload["tutor_state_advanced"] is False
    assert payload["model_coaching_ref"] is None
    assert payload["model_evaluation_ref"] is None

    feedback_ref = _ref(payload["grounded_feedback_ref"])
    review_ref = _ref(payload["coach_review_ref"])
    run_ref = _ref(payload["run_ref"])
    feedback = store.get(feedback_ref, participant_id="P01").payload
    review = store.get(review_ref, participant_id="P01").payload
    run = store.get(run_ref, participant_id="P01").payload

    assert feedback["claim_scope"] == "session_local_grounded_feedback"
    assert review["deterministic_grounding"] == feedback
    assert review["model_coaching"] is None
    assert review["model_evaluation"] is None
    assert review["tutor_state"]["state"] == "compared"
    assert run["authority_boundary"]["advances_tutor_state"] is False
    assert _kind_count(store, SESSION_KIND) == session_count

    recovered = load_tutor_session(store, compared_ref, participant_id="P01")
    assert recovered.session.state == "compared"
    assert recovered.session.explanation is None


def test_identical_repository_invocation_is_content_idempotent(tmp_path, capsys) -> None:
    store, db, _, compared_ref = _store_lineage(tmp_path)
    argv = (
        compared_ref.artifact_id,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--created-at",
        S13,
    )

    first_code, first, first_error = _invoke(capsys, *argv)
    counts = {
        kind: _kind_count(store, kind)
        for kind in (
            "m16.grounded-mentor-feedback.v1",
            "m25.coach-review-read-model.v1",
            M26_SCHEMA_VERSION,
        )
    }
    second_code, second, second_error = _invoke(capsys, *argv)

    assert first_code == second_code == 0
    assert first_error == second_error == ""
    assert first == second
    assert {
        kind: _kind_count(store, kind) for kind in counts
    } == counts


def test_selected_checkpoint_is_rejected_before_any_review_artifact(tmp_path) -> None:
    store, _, selected_ref, _ = _store_lineage(tmp_path)

    with pytest.raises(
        PersistentReviewedCoachingError,
        match="unexplained replay-verified compared session",
    ):
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=selected_ref.artifact_id,
            grounding_created_at=S13,
        )

    assert _kind_count(store, "m16.grounded-mentor-feedback.v1") == 0
    assert _kind_count(store, "m25.coach-review-read-model.v1") == 0
    assert _kind_count(store, M26_SCHEMA_VERSION) == 0


def test_compared_checkpoint_without_m21_lineage_fails_closed(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(
        tmp_path,
        with_launch_dependency=False,
    )

    with pytest.raises(PersistentReviewedCoachingError, match="M21.*dependency"):
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
        )


def test_queue_storage_identity_drift_is_rejected(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(
        tmp_path,
        queue_artifact_id="diagnostic_queue_wrong",
    )

    with pytest.raises(PersistentReviewedCoachingError, match="queue storage identity"):
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
        )


def test_hermetic_provider_and_evaluator_populate_m24_m19_m20_lineage(
    tmp_path,
) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)

    result = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
        provider=_Provider(),
        provider_endpoint=_provider_endpoint(),
        evaluator=_Evaluator(),
        evaluator_endpoint=_evaluator_endpoint(),
        evaluation_request_created_at=S15,
    )

    assert result.model_request_ref is not None
    assert result.provider_execution_ref is not None
    assert result.model_coaching_ref is not None
    assert result.evaluation_request_ref is not None
    assert result.evaluator_execution_ref is not None
    assert result.model_evaluation_ref is not None
    assert result.read_model["model_coaching"] is not None
    assert result.read_model["model_evaluation"] is not None
    assert result.read_model["model_evaluation"]["truth_status"] == (
        "not_established_by_m20_evaluation"
    )
    provider_record = store.get(
        result.provider_execution_ref,
        participant_id="P01",
    ).payload
    evaluator_record = store.get(
        result.evaluator_execution_ref,
        participant_id="P01",
    ).payload
    assert provider_record["status"] == evaluator_record["status"] == "succeeded"
    recovered = load_tutor_session(store, compared_ref, participant_id="P01")
    assert recovered.session.state == "compared"
    assert recovered.session.explanation is None


def test_provider_failure_exposes_m24_record_and_persists_no_partial_outputs(
    tmp_path,
) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    provider = _Provider(failure=TimeoutError("fixture timeout"))

    with pytest.raises(PersistentReviewedCoachingError) as raised:
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=provider,
            provider_endpoint=_provider_endpoint(),
        )

    assert raised.value.execution_record is not None
    assert raised.value.execution_record["failure"]["kind"] == "timeout"
    assert _kind_count(store, "m16.grounded-mentor-feedback.v1") == 0
    assert _kind_count(store, "m19.model-coaching-request.v1") == 0
    assert _kind_count(store, "m24.provider-evaluator-execution.v1") == 0
    assert _kind_count(store, "m25.coach-review-read-model.v1") == 0
    assert _kind_count(store, M26_SCHEMA_VERSION) == 0


def test_evaluator_requires_model_coaching_and_matching_endpoint(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)

    with pytest.raises(PersistentReviewedCoachingError, match="supplied together"):
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=_Provider(),
        )

    with pytest.raises(PersistentReviewedCoachingError, match="requires M19"):
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            evaluator=_Evaluator(),
            evaluator_endpoint=_evaluator_endpoint(),
            evaluation_request_created_at=S15,
        )


def test_evaluator_failure_persists_no_partial_m26_chain(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    evaluator = _Evaluator(failure=TimeoutError("fixture evaluator timeout"))

    with pytest.raises(PersistentReviewedCoachingError) as raised:
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=_Provider(),
            provider_endpoint=_provider_endpoint(),
            evaluator=evaluator,
            evaluator_endpoint=_evaluator_endpoint(),
            evaluation_request_created_at=S15,
        )

    assert raised.value.execution_record is not None
    assert raised.value.execution_record["failure"]["kind"] == "timeout"
    assert _kind_count(store, "m16.grounded-mentor-feedback.v1") == 0
    assert _kind_count(store, "m19.provenance-bound-mentor-coaching.v1") == 0
    assert _kind_count(store, "m20.model-coaching-evaluation.v1") == 0
    assert _kind_count(store, M26_SCHEMA_VERSION) == 0
