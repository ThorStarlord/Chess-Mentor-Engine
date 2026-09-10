"""M29 persisted reviewed-coaching to M28 reference-surface qualification."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from test_m27_reviewed_coaching_execution_ledger import (
    _deterministic_run,
    _fork_run,
    _model_run,
    _reidentity,
)

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_reference import (
    render_coach_review_reference_surface,
)
from chess_mentor_engine.persisted_review_reference import (
    M29_CLAIM_SCOPE,
    M29_SCHEMA_VERSION,
    PersistedReviewReferenceError,
    build_persisted_coach_review_reference,
)
from chess_mentor_engine.persisted_review_reference_cli import main as bridge_main
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import (
    M27_SCHEMA_VERSION,
    ReviewedCoachingLedgerError,
)
from chess_mentor_engine.storage import ArtifactWrite, prepare_artifact


def _invoke(capsys, *argv: str):
    code = bridge_main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def test_run_selector_verifies_m27_and_renders_exact_persisted_m25(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    result = build_persisted_coach_review_reference(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )
    expected = render_coach_review_reference_surface(run.read_model)

    assert result.run_ref == run.run_ref
    assert result.review_ref == run.read_model_ref
    assert result.surface.html == expected.html
    assert result.surface.surface_id == expected.surface_id
    assert result.surface.read_model == run.read_model
    assert result.ledger.ledger_record["run_count"] == 1
    entry = result.ledger.ledger_record["runs"][0]
    assert entry["fidelity"]["status"] == "mechanically_verified"
    assert entry["run_ref"] == run.run_ref.to_dict()
    assert entry["coach_review_ref"] == run.read_model_ref.to_dict()

    stored_ledger = store.get(
        result.ledger.ledger_ref,
        participant_id="P01",
    )
    assert stored_ledger.payload["schema_version"] == M27_SCHEMA_VERSION
    assert stored_ledger.dependencies == (run.run_ref,)


def test_review_selector_resolves_same_run_and_is_content_idempotent(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    by_review = build_persisted_coach_review_reference(
        store=store,
        participant_id="P01",
        review_artifact_id=run.read_model_ref.artifact_id,
    )
    by_run = build_persisted_coach_review_reference(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    assert by_review.run_ref == by_run.run_ref == run.run_ref
    assert by_review.review_ref == by_run.review_ref == run.read_model_ref
    assert by_review.ledger.ledger_ref == by_run.ledger.ledger_ref
    assert by_review.surface.html == by_run.surface.html
    ledgers = store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION)
    assert ledgers == (by_review.ledger.ledger_ref,)


def test_hermetic_model_run_preserves_model_and_evaluator_authority(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)

    result = build_persisted_coach_review_reference(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )
    html = result.surface.html

    coaching = run.read_model["model_coaching"]
    evaluation = run.read_model["model_evaluation"]
    assert coaching is not None
    assert evaluation is not None
    assert coaching["rendered_content"] in html
    assert evaluation["truth_status"] in html
    assert "request-bound and is not established as objective chess truth" in html
    assert "M20 records a bounded assessment of model output" in html
    assert result.ledger.ledger_record["summary"]["execution_count"] == 2


def test_review_not_backed_by_m26_run_is_rejected(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    original = store.get(run.read_model_ref, participant_id="P01")
    detached = copy.deepcopy(original.payload)
    detached["tutor_state"]["state"] = "completed"
    detached = _reidentity(
        detached,
        id_key="read_model_id",
        prefix="coach_review",
    )
    write = ArtifactWrite(
        COACH_REVIEW_SCHEMA_VERSION,
        detached["read_model_id"],
        "P01",
        detached,
        original.dependencies,
    )
    detached_ref = prepare_artifact(write)[0]
    store.put_many((write,))

    with pytest.raises(
        PersistedReviewReferenceError,
        match="backed by exactly one participant-scoped M26 run",
    ):
        build_persisted_coach_review_reference(
            store=store,
            participant_id="P01",
            review_artifact_id=detached_ref.artifact_id,
        )


def test_forged_m25_projection_fails_m27_before_render(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    run_artifact = store.get(run.run_ref, participant_id="P01")
    review_ref = next(
        ref
        for ref in run_artifact.dependencies
        if ref.kind == COACH_REVIEW_SCHEMA_VERSION
    )
    review_artifact = store.get(review_ref, participant_id="P01")
    review = json.loads(canonical_json(review_artifact.payload))
    review["deterministic_grounding"]["rendered_content"] += " tampered"
    review = _reidentity(
        review,
        id_key="read_model_id",
        prefix="coach_review",
    )
    review_write = ArtifactWrite(
        COACH_REVIEW_SCHEMA_VERSION,
        review["read_model_id"],
        "P01",
        review,
        review_artifact.dependencies,
    )
    forged_review_ref = prepare_artifact(review_write)[0]
    store.put_many((review_write,))
    forged_run_ref = _fork_run(
        store,
        run.run_ref,
        review_ref=forged_review_ref,
    )

    with pytest.raises(
        ReviewedCoachingLedgerError,
        match="M25/M16 grounding content drifted",
    ):
        build_persisted_coach_review_reference(
            store=store,
            participant_id="P01",
            run_artifact_id=forged_run_ref.artifact_id,
        )

    assert store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION) == ()


def test_selector_and_participant_errors_fail_closed(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    with pytest.raises(PersistedReviewReferenceError, match="exactly one"):
        build_persisted_coach_review_reference(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            review_artifact_id=run.read_model_ref.artifact_id,
        )
    with pytest.raises(PersistedReviewReferenceError, match="participant-scoped"):
        build_persisted_coach_review_reference(
            store=store,
            participant_id="OTHER",
            run_artifact_id=run.run_ref.artifact_id,
        )
    with pytest.raises(PersistedReviewReferenceError, match="participant-scoped"):
        build_persisted_coach_review_reference(
            store=store,
            participant_id="P01",
            review_artifact_id="coach_review_missing",
        )


def test_cli_writes_reference_and_refuses_overwrite(tmp_path, capsys) -> None:
    store, db, run = _deterministic_run(tmp_path)
    output = tmp_path / "review" / "persisted.html"

    code, payload, error = _invoke(
        capsys,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--run-id",
        run.run_ref.artifact_id,
        "--output",
        str(output),
    )

    assert code == 0 and error == ""
    assert payload["schema_version"] == M29_SCHEMA_VERSION
    assert payload["claim_scope"] == M29_CLAIM_SCOPE
    assert payload["mechanical_verification"] == "mechanically_verified"
    assert payload["run_ref"] == run.run_ref.to_dict()
    assert payload["coach_review_ref"] == run.read_model_ref.to_dict()
    assert payload["external_calls"] is False
    assert payload["production_ui_claim"] is False
    assert payload["tutor_state_advanced"] is False
    assert Path(payload["output"]) == output.resolve()
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>\n")

    ledger_count = len(store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION))
    code, payload, error = _invoke(
        capsys,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--run-id",
        run.run_ref.artifact_id,
        "--output",
        str(output),
    )
    assert code == 2
    assert payload is None
    assert "refusing to overwrite" in error
    assert len(store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION)) == (
        ledger_count
    )


def test_cli_rejects_unsafe_output_before_ledger_and_missing_database(
    tmp_path,
    capsys,
) -> None:
    store, db, run = _deterministic_run(tmp_path)
    bad_output = tmp_path / "review.txt"

    code, payload, error = _invoke(
        capsys,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--review-id",
        run.read_model_ref.artifact_id,
        "--output",
        str(bad_output),
    )
    assert code == 2
    assert payload is None
    assert "must end in .html or .htm" in error
    assert not bad_output.exists()
    assert store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION) == ()

    code, payload, error = _invoke(
        capsys,
        "--db",
        str(tmp_path / "missing.sqlite3"),
        "--participant",
        "P01",
        "--run-id",
        run.run_ref.artifact_id,
        "--output",
        str(tmp_path / "missing.html"),
    )
    assert code == 2
    assert payload is None
    assert "artifact database does not exist" in error
