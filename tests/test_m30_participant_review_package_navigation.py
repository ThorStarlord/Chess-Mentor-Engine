"""M30 participant-scoped review package and navigation qualification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_m27_reviewed_coaching_execution_ledger import (
    _deterministic_run,
    _model_run,
)

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.participant_review_package import (
    M30_CLAIM_SCOPE,
    M30_INDEX_SCHEMA_VERSION,
    M30_SCHEMA_VERSION,
    M30_SHOW_SCHEMA_VERSION,
    ParticipantReviewPackageError,
    build_participant_review_package,
    list_participant_review_navigation,
    load_participant_review_package,
    render_participant_review_package_surface,
    show_participant_review_item,
)
from chess_mentor_engine.participant_review_package_cli import main as package_main


def _invoke(capsys, *argv: str):
    code = package_main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def test_build_persists_content_addressed_summary_safe_manifest(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    result = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    manifest = result.manifest_record
    assert manifest["schema_version"] == M30_SCHEMA_VERSION
    assert manifest["claim_scope"] == M30_CLAIM_SCOPE
    assert manifest["package_id"] == (
        f"participant_review_package_{manifest['fingerprint'][:20]}"
    )
    assert manifest["source_refs"] == {
        "m26_run": result.run_ref.to_dict(),
        "m25_review": result.review_ref.to_dict(),
        "m27_ledger": result.ledger_ref.to_dict(),
    }
    assert manifest["source_fingerprints"]["m26_artifact_digest"] == (
        result.run_ref.digest
    )
    assert manifest["source_fingerprints"]["m25_artifact_digest"] == (
        result.review_ref.digest
    )
    assert manifest["source_fingerprints"]["m27_artifact_digest"] == (
        result.ledger_ref.digest
    )
    assert manifest["source_fingerprints"]["m25_source_fingerprints"] == (
        run.read_model["source_fingerprints"]
    )
    assert manifest["reference_surface"]["html_in_manifest"] is False
    assert manifest["privacy_contract"] == {
        "summary_contains_source_payloads": False,
        "summary_contains_model_rendered_content": False,
        "summary_contains_evaluator_rationales": False,
        "summary_contains_participant_response_content": False,
        "summary_contains_reference_html": False,
        "exact_content_requires_explicit_show_or_export": True,
    }

    serialized = canonical_json(manifest)
    assert "I would play e4." not in serialized
    assert "I considered e4 and expect ...e5 followed by Nf3." not in serialized
    assert "<!doctype html>" not in serialized

    stored = store.get(result.manifest_ref, participant_id="P01")
    assert stored.payload == manifest
    assert {ref.digest for ref in stored.dependencies} == {
        result.run_ref.digest,
        result.review_ref.digest,
        result.ledger_ref.digest,
    }


def test_repeated_package_build_is_content_idempotent(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    args = {
        "store": store,
        "participant_id": "P01",
        "review_artifact_id": run.read_model_ref.artifact_id,
    }

    first = build_participant_review_package(**args)
    second = build_participant_review_package(**args)

    assert first.manifest_record == second.manifest_record
    assert first.manifest_ref == second.manifest_ref
    assert first.ledger_ref == second.ledger_ref
    assert first.surface.html == second.surface.html
    assert store.list_refs(participant_id="P01", kind=M30_SCHEMA_VERSION) == (
        first.manifest_ref,
    )


def test_model_run_manifest_and_list_index_do_not_copy_sensitive_content(
    tmp_path,
) -> None:
    store, _, run = _model_run(tmp_path)
    built = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    index = list_participant_review_navigation(
        store=store,
        participant_id="P01",
    )

    assert index["schema_version"] == M30_INDEX_SCHEMA_VERSION
    assert index["counts"] == {
        "runs": 1,
        "reviews": 1,
        "ledgers": 1,
        "packages": 1,
        "reference_surfaces": 1,
    }
    assert index["runs"][0]["run_ref"] == run.run_ref.to_dict()
    assert index["runs"][0]["package_refs"] == [built.manifest_ref.to_dict()]
    assert index["runs"][0]["reference_surfaces"] == [
        built.manifest_record["reference_surface"]
    ]

    coaching = run.read_model["model_coaching"]
    evaluation = run.read_model["model_evaluation"]
    assert coaching is not None
    assert evaluation is not None
    sensitive = (
        coaching["rendered_content"],
        evaluation["judgments"][0]["rationale"],
        "I would play e4.",
        "I considered e4 and expect ...e5 followed by Nf3.",
    )
    for payload in (built.manifest_record, index):
        serialized = canonical_json(payload)
        for value in sensitive:
            assert value not in serialized


def test_show_requires_explicit_content_and_surface_html_opt_in(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    built = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    summary = show_participant_review_item(
        store=store,
        participant_id="P01",
        item_type="review",
        artifact_id=run.read_model_ref.artifact_id,
    )
    assert summary["schema_version"] == M30_SHOW_SCHEMA_VERSION
    assert summary["content_included"] is False
    assert "payload" not in summary
    assert run.read_model["model_coaching"]["rendered_content"] not in canonical_json(
        summary
    )

    exact = show_participant_review_item(
        store=store,
        participant_id="P01",
        item_type="review",
        artifact_id=run.read_model_ref.artifact_id,
        include_content=True,
    )
    assert exact["content_included"] is True
    assert exact["payload"] == run.read_model

    surface_summary = show_participant_review_item(
        store=store,
        participant_id="P01",
        item_type="surface",
        artifact_id=built.manifest_ref.artifact_id,
    )
    assert surface_summary["content_included"] is False
    assert "html" not in surface_summary

    surface_exact = show_participant_review_item(
        store=store,
        participant_id="P01",
        item_type="surface",
        artifact_id=built.manifest_ref.artifact_id,
        include_content=True,
    )
    assert surface_exact["content_included"] is True
    assert surface_exact["html"] == built.surface.html
    assert run.read_model["model_coaching"]["rendered_content"] in (
        surface_exact["html"]
    )


def test_loaded_package_reconstructs_exact_surface(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    built = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    loaded = load_participant_review_package(
        store=store,
        participant_id="P01",
        package_artifact_id=built.manifest_ref.artifact_id,
    )
    reconstructed = render_participant_review_package_surface(
        store=store,
        participant_id="P01",
        package_artifact_id=built.manifest_ref.artifact_id,
    )

    assert loaded.run_ref == built.run_ref
    assert loaded.review_ref == built.review_ref
    assert loaded.ledger_ref == built.ledger_ref
    assert reconstructed.surface_id == built.surface.surface_id
    assert reconstructed.fingerprint == built.surface.fingerprint
    assert reconstructed.html == built.surface.html


def test_participant_scope_and_invalid_navigation_kind_fail_closed(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    other = list_participant_review_navigation(
        store=store,
        participant_id="OTHER",
    )
    assert other["counts"] == {
        "runs": 0,
        "reviews": 0,
        "ledgers": 0,
        "packages": 0,
        "reference_surfaces": 0,
    }
    assert canonical_json(other).find(run.run_ref.artifact_id) == -1

    with pytest.raises(ParticipantReviewPackageError, match="participant-scoped"):
        show_participant_review_item(
            store=store,
            participant_id="OTHER",
            item_type="run",
            artifact_id=run.run_ref.artifact_id,
        )
    with pytest.raises(ParticipantReviewPackageError, match="item_type"):
        show_participant_review_item(
            store=store,
            participant_id="P01",
            item_type="unknown",
            artifact_id=run.run_ref.artifact_id,
        )


def test_cli_list_show_and_export_package(tmp_path, capsys) -> None:
    store, db, run = _model_run(tmp_path)
    output = tmp_path / "participant-review-export"

    code, payload, error = _invoke(
        capsys,
        "export",
        "--db",
        str(db),
        "--participant",
        "P01",
        "--run-id",
        run.run_ref.artifact_id,
        "--output-dir",
        str(output),
    )
    assert code == 0 and error == ""
    assert payload["schema_version"] == M30_SCHEMA_VERSION
    assert payload["claim_scope"] == M30_CLAIM_SCOPE
    assert payload["external_calls"] is False
    assert payload["production_ui_claim"] is False
    assert payload["tutor_state_advanced"] is False
    assert Path(payload["output_dir"]) == output.resolve()
    assert (output / "manifest.json").is_file()
    assert (output / "review.html").is_file()

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    package_id = manifest["package_id"]
    assert manifest["reference_surface"] == payload["reference_surface"]
    assert (output / "review.html").read_text(encoding="utf-8").startswith(
        "<!doctype html>\n"
    )

    code, listed, error = _invoke(
        capsys,
        "list",
        "--db",
        str(db),
        "--participant",
        "P01",
    )
    assert code == 0 and error == ""
    assert listed["counts"]["packages"] == 1
    assert "Review the strongest reply before committing." not in canonical_json(
        listed
    )

    code, shown, error = _invoke(
        capsys,
        "show",
        "--db",
        str(db),
        "--participant",
        "P01",
        "--kind",
        "surface",
        "--id",
        package_id,
        "--include-content",
    )
    assert code == 0 and error == ""
    assert shown["content_included"] is True
    assert "Review the strongest reply before committing." in shown["html"]


def test_cli_refuses_overwrite_before_new_package_mutation_and_missing_db(
    tmp_path,
    capsys,
) -> None:
    store, db, run = _deterministic_run(tmp_path)
    output = tmp_path / "existing"
    output.mkdir()

    code, payload, error = _invoke(
        capsys,
        "export",
        "--db",
        str(db),
        "--participant",
        "P01",
        "--review-id",
        run.read_model_ref.artifact_id,
        "--output-dir",
        str(output),
    )
    assert code == 2
    assert payload is None
    assert "refusing to overwrite" in error
    assert store.list_refs(participant_id="P01", kind=M30_SCHEMA_VERSION) == ()

    code, payload, error = _invoke(
        capsys,
        "list",
        "--db",
        str(tmp_path / "missing.sqlite3"),
        "--participant",
        "P01",
    )
    assert code == 2
    assert payload is None
    assert "artifact database does not exist" in error
