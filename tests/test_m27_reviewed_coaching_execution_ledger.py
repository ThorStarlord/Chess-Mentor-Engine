"""M27 execution-ledger and mechanical-fidelity qualification."""

from __future__ import annotations

import hashlib
import json

import pytest
from test_m24_provider_conformance import (
    _Evaluator,
    _Provider,
    _evaluator_endpoint,
    _provider_endpoint,
)
from test_m26_persistent_reviewed_coaching import S13, S15, _store_lineage

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import EXECUTION_SCHEMA_VERSION
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import (
    M26_SCHEMA_VERSION,
    run_persistent_reviewed_coaching,
)
from chess_mentor_engine.reviewed_coaching_ledger import (
    M27_SCHEMA_VERSION,
    ReviewedCoachingLedgerError,
    build_reviewed_coaching_execution_ledger,
)
from chess_mentor_engine.reviewed_coaching_ledger_cli import main as ledger_main
from chess_mentor_engine.storage import ArtifactRef, ArtifactWrite, prepare_artifact


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _invoke(capsys, *argv: str):
    code = ledger_main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _deterministic_run(tmp_path):
    store, db, _, compared_ref = _store_lineage(tmp_path)
    result = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
    )
    return store, db, result


def _model_run(tmp_path):
    store, db, _, compared_ref = _store_lineage(tmp_path)
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
    return store, db, result


def _reidentity(record: dict, *, id_key: str, prefix: str) -> dict:
    payload = {
        key: value
        for key, value in record.items()
        if key not in {id_key, "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        id_key: f"{prefix}_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _record_ref(record: dict, id_key: str) -> dict[str, str]:
    return {
        "schema_version": record["schema_version"],
        id_key: record[id_key],
        "fingerprint": record["fingerprint"],
    }


def _fork_run(
    store,
    source_ref: ArtifactRef,
    *,
    review_ref: ArtifactRef | None = None,
    execution_replacements: dict[str, ArtifactRef] | None = None,
    record_updates: dict | None = None,
) -> ArtifactRef:
    source_artifact = store.get(source_ref, participant_id="P01")
    run = source_artifact.payload
    dependencies = list(source_artifact.dependencies)
    updates = {} if record_updates is None else dict(record_updates)

    if review_ref is not None:
        old_review = next(
            ref for ref in dependencies if ref.kind == COACH_REVIEW_SCHEMA_VERSION
        )
        review = store.get(review_ref, participant_id="P01").payload
        dependencies = [
            review_ref if ref == old_review else ref for ref in dependencies
        ]
        updates["coach_review_ref"] = _record_ref(review, "read_model_id")

    if execution_replacements:
        new_execution_refs = []
        for execution_ref in run["execution_refs"]:
            execution_id = execution_ref["execution_id"]
            replacement = execution_replacements.get(execution_id)
            if replacement is None:
                new_execution_refs.append(execution_ref)
                continue
            replacement_record = store.get(
                replacement,
                participant_id="P01",
            ).payload
            old_ref = next(
                ref
                for ref in dependencies
                if ref.kind == EXECUTION_SCHEMA_VERSION
                and ref.artifact_id == execution_id
            )
            dependencies = [
                replacement if ref == old_ref else ref for ref in dependencies
            ]
            new_execution_refs.append(
                _record_ref(replacement_record, "execution_id")
            )
        updates["execution_refs"] = new_execution_refs

    run = _reidentity(
        {**run, **updates},
        id_key="run_id",
        prefix="reviewed_coaching_run",
    )
    write = ArtifactWrite(
        M26_SCHEMA_VERSION,
        run["run_id"],
        "P01",
        run,
        tuple(dependencies),
    )
    ref = prepare_artifact(write)[0]
    store.put_many((write,))
    return ref


def test_deterministic_run_builds_privacy_bounded_zero_execution_ledger(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)

    result = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id="P01",
        run_artifact_ids=(run.run_ref.artifact_id,),
    )

    ledger = result.ledger_record
    assert ledger["schema_version"] == M27_SCHEMA_VERSION
    assert ledger["run_count"] == 1
    assert ledger["summary"] == {
        "mechanically_verified_runs": 1,
        "deterministic_only_runs": 1,
        "execution_count": 0,
        "provider_execution_count": 0,
        "evaluator_execution_count": 0,
    }
    entry = ledger["runs"][0]
    assert entry["fidelity"]["status"] == "mechanically_verified"
    assert entry["execution_count"] == 0
    assert entry["executions"] == []
    assert ledger["authority_boundary"]["executes_external_calls"] is False
    assert ledger["authority_boundary"]["retries_execution"] is False
    assert ledger["privacy_contract"]["copies_request_payloads"] is False
    assert ledger["privacy_contract"]["copies_model_rendered_content"] is False
    assert ledger["privacy_contract"]["copies_evaluator_rationales"] is False
    assert (
        ledger["privacy_contract"]["copies_participant_response_content"]
        is False
    )

    serialized = canonical_json(ledger)
    for sensitive in (
        "I would play e4.",
        "I considered e4 and expect ...e5 followed by Nf3.",
    ):
        assert sensitive not in serialized

    stored = store.get(result.ledger_ref, participant_id="P01")
    assert stored.payload == ledger
    assert stored.dependencies == (run.run_ref,)


def test_hermetic_model_run_ledgers_provider_and_evaluator_bindings(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)

    result = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id="P01",
        run_artifact_ids=(run.run_ref.artifact_id,),
    )

    ledger = result.ledger_record
    assert ledger["summary"]["execution_count"] == 2
    assert ledger["summary"]["provider_execution_count"] == 1
    assert ledger["summary"]["evaluator_execution_count"] == 1
    entry = ledger["runs"][0]
    assert [item["role"] for item in entry["executions"]] == [
        "model_coach_provider",
        "model_coaching_evaluator",
    ]
    assert all(item["status"] == "succeeded" for item in entry["executions"])
    assert all(item["automatic_retry"] is False for item in entry["executions"])
    assert entry["fidelity"]["status"] == "mechanically_verified"

    provider, evaluator = entry["executions"]
    assert provider["endpoint"]["provider_id"] == "fixture-provider"
    assert provider["response_ref"]["run_id"] == "fixture-provider-run-001"
    assert evaluator["endpoint"]["evaluator_id"] == "fixture-evaluator"
    assert evaluator["response_ref"]["run_id"] == "fixture-evaluator-run-001"

    serialized = canonical_json(ledger)
    assert "Review the strongest reply before committing." not in serialized
    assert "Fixture pass for" not in serialized


def test_all_runs_are_sorted_and_explicit_selection_is_order_independent(
    tmp_path,
) -> None:
    store, _, deterministic = _deterministic_run(tmp_path)
    compared_ref = deterministic.run_record["source_session_ref"]
    model = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref["artifact_id"],
        grounding_created_at=S13,
        provider=_Provider(),
        provider_endpoint=_provider_endpoint(),
        evaluator=_Evaluator(),
        evaluator_endpoint=_evaluator_endpoint(),
        evaluation_request_created_at=S15,
    )

    first = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id="P01",
        run_artifact_ids=(
            model.run_ref.artifact_id,
            deterministic.run_ref.artifact_id,
        ),
    )
    second = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id="P01",
        run_artifact_ids=(
            deterministic.run_ref.artifact_id,
            model.run_ref.artifact_id,
        ),
    )
    automatic = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id="P01",
    )

    assert first.ledger_record == second.ledger_record == automatic.ledger_record
    ids = [entry["run_id"] for entry in first.ledger_record["runs"]]
    assert ids == sorted(ids)
    assert first.ledger_record["summary"] == {
        "mechanically_verified_runs": 2,
        "deterministic_only_runs": 1,
        "execution_count": 2,
        "provider_execution_count": 1,
        "evaluator_execution_count": 1,
    }


def test_repeated_identical_build_is_content_idempotent(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    args = {
        "store": store,
        "participant_id": "P01",
        "run_artifact_ids": (run.run_ref.artifact_id,),
    }

    first = build_reviewed_coaching_execution_ledger(**args)
    count = len(store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION))
    second = build_reviewed_coaching_execution_ledger(**args)

    assert first.ledger_record == second.ledger_record
    assert first.ledger_ref == second.ledger_ref
    assert len(store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION)) == count


def test_forged_m25_projection_is_rejected_before_ledger_persistence(tmp_path) -> None:
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
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=(forged_run_ref.artifact_id,),
        )

    assert store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION) == ()


def test_forged_automatic_retry_claim_is_rejected(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    run_artifact = store.get(run.run_ref, participant_id="P01")
    provider_ref = next(
        ref
        for ref in run_artifact.dependencies
        if ref.kind == EXECUTION_SCHEMA_VERSION
        and store.get(ref, participant_id="P01").payload["role"]
        == "model_coach_provider"
    )
    provider_artifact = store.get(provider_ref, participant_id="P01")
    execution = json.loads(canonical_json(provider_artifact.payload))
    execution["execution_policy"]["automatic_retry"] = True
    execution = _reidentity(
        execution,
        id_key="execution_id",
        prefix="m24_execution",
    )
    execution_write = ArtifactWrite(
        EXECUTION_SCHEMA_VERSION,
        execution["execution_id"],
        "P01",
        execution,
        provider_artifact.dependencies,
    )
    forged_execution_ref = prepare_artifact(execution_write)[0]
    store.put_many((execution_write,))
    forged_run_ref = _fork_run(
        store,
        run.run_ref,
        execution_replacements={provider_ref.artifact_id: forged_execution_ref},
    )

    with pytest.raises(
        ReviewedCoachingLedgerError,
        match="must not claim automatic retry",
    ):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=(forged_run_ref.artifact_id,),
        )

    assert store.list_refs(participant_id="P01", kind=M27_SCHEMA_VERSION) == ()


def test_forged_provider_response_binding_is_rejected(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    run_artifact = store.get(run.run_ref, participant_id="P01")
    provider_ref = next(
        ref
        for ref in run_artifact.dependencies
        if ref.kind == EXECUTION_SCHEMA_VERSION
        and store.get(ref, participant_id="P01").payload["role"]
        == "model_coach_provider"
    )
    provider_artifact = store.get(provider_ref, participant_id="P01")
    execution = json.loads(canonical_json(provider_artifact.payload))
    execution["response_ref"]["run_id"] = "forged-provider-run"
    execution = _reidentity(
        execution,
        id_key="execution_id",
        prefix="m24_execution",
    )
    execution_write = ArtifactWrite(
        EXECUTION_SCHEMA_VERSION,
        execution["execution_id"],
        "P01",
        execution,
        provider_artifact.dependencies,
    )
    forged_execution_ref = prepare_artifact(execution_write)[0]
    store.put_many((execution_write,))
    forged_run_ref = _fork_run(
        store,
        run.run_ref,
        execution_replacements={provider_ref.artifact_id: forged_execution_ref},
    )

    with pytest.raises(
        ReviewedCoachingLedgerError,
        match="provider response run_id differs from M19 coaching",
    ):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=(forged_run_ref.artifact_id,),
        )


def test_missing_duplicate_and_empty_run_selection_fail_closed(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)

    with pytest.raises(ReviewedCoachingLedgerError, match="must be unique"):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=(run.run_ref.artifact_id, run.run_ref.artifact_id),
        )
    with pytest.raises(ReviewedCoachingLedgerError, match="not found"):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=("reviewed_coaching_run_missing",),
        )
    with pytest.raises(ReviewedCoachingLedgerError, match="must not be empty"):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="P01",
            run_artifact_ids=(),
        )


def test_no_runs_for_participant_is_rejected(tmp_path) -> None:
    store, _, _ = _deterministic_run(tmp_path)

    with pytest.raises(ReviewedCoachingLedgerError, match="no M26 runs"):
        build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id="OTHER",
        )


def test_cli_persists_selected_ledger_and_rejects_missing_database(
    tmp_path,
    capsys,
) -> None:
    store, db, run = _model_run(tmp_path)

    code, payload, error = _invoke(
        capsys,
        "--db",
        str(db),
        "--participant",
        "P01",
        "--run-id",
        run.run_ref.artifact_id,
    )

    assert code == 0 and error == ""
    assert payload["schema_version"] == M27_SCHEMA_VERSION
    assert payload["run_count"] == 1
    assert payload["summary"]["execution_count"] == 2
    ledger_ref = ArtifactRef(**payload["ledger_ref"])
    assert store.get(ledger_ref, participant_id="P01").payload["run_count"] == 1

    code, payload, error = _invoke(
        capsys,
        "--db",
        str(tmp_path / "missing.sqlite3"),
        "--participant",
        "P01",
    )
    assert code == 2
    assert payload is None
    assert "artifact database does not exist" in error
