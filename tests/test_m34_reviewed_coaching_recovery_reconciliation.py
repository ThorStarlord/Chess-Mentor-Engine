"""M34 hermetic reviewed-coaching recovery reconciliation qualification."""

from __future__ import annotations

import copy
import hashlib

import pytest
from test_m24_provider_conformance import (
    _Evaluator,
    _Provider,
    _evaluator_endpoint,
    _provider_endpoint,
)
from test_m26_persistent_reviewed_coaching import S13, S15, _store_lineage

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.execution_recovery_reconciliation import (
    M34_CLAIM_SCOPE,
    M34_PLAN_MODE,
    M34_SCHEMA_VERSION,
    ReviewedCoachingRecoveryError,
    build_reviewed_coaching_recovery_reconciliation,
    validate_persisted_reviewed_coaching_recovery_plan,
    validate_reviewed_coaching_recovery_plan,
)
from chess_mentor_engine.reviewed_coaching import run_persistent_reviewed_coaching

CANARY = "CME_TEST_CANARY_RECOVERY_12345678"


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _reidentity_execution(record: dict) -> dict:
    value = copy.deepcopy(record)
    payload = {
        key: item
        for key, item in value.items()
        if key not in {"execution_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "execution_id": f"m24_execution_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _reidentity_plan(plan: dict) -> dict:
    value = copy.deepcopy(plan)
    payload = {
        key: item
        for key, item in value.items()
        if key not in {"recovery_plan_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "recovery_plan_id": f"reviewed_coaching_recovery_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _target_run(tmp_path, *, attempt_number: int = 2, evaluator: bool = True):
    store, _, _, compared_ref = _store_lineage(tmp_path)
    kwargs = {
        "store": store,
        "participant_id": "P01",
        "session_artifact_id": compared_ref.artifact_id,
        "grounding_created_at": S13,
        "provider": _Provider(),
        "provider_endpoint": _provider_endpoint(),
        "attempt_number": attempt_number,
    }
    if evaluator:
        kwargs.update(
            {
                "evaluator": _Evaluator(),
                "evaluator_endpoint": _evaluator_endpoint(),
                "evaluation_request_created_at": S15,
            }
        )
    run = run_persistent_reviewed_coaching(**kwargs)
    assert run.provider_execution_ref is not None
    provider = store.get(run.provider_execution_ref, participant_id="P01").payload
    evaluator_record = None
    if evaluator:
        assert run.evaluator_execution_ref is not None
        evaluator_record = store.get(
            run.evaluator_execution_ref,
            participant_id="P01",
        ).payload
    return store, run, provider, evaluator_record


def _success_at(record: dict, attempt_number: int) -> dict:
    value = copy.deepcopy(record)
    value["execution_policy"]["attempt_number"] = attempt_number
    return _reidentity_execution(value)


def _failure_at(
    record: dict,
    *,
    attempt_number: int,
    kind: str,
    detail: str = CANARY,
) -> dict:
    value = copy.deepcopy(record)
    value["execution_policy"]["attempt_number"] = attempt_number
    value["status"] = "failed"
    value["response_ref"] = None
    value["failure"] = {
        "kind": kind,
        "retryable": kind in {"timeout", "transient"},
        "exception_type": "SyntheticRecoveryFailure",
        "detail": detail,
    }
    return _reidentity_execution(value)


@pytest.mark.parametrize("kind", ["timeout", "transient"])
def test_retryable_provider_prefix_builds_manual_full_m26_resume_plan(
    tmp_path,
    kind,
) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind=kind)

    result = build_reviewed_coaching_recovery_reconciliation(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={"model_coach_provider": [failed]},
        max_attempts=2,
    )

    plan = result.plan
    assert plan["schema_version"] == M34_SCHEMA_VERSION
    assert plan["claim_scope"] == M34_CLAIM_SCOPE
    assert plan["plan_mode"] == M34_PLAN_MODE
    assert plan["reconciliation"] == {
        "state": "resume_eligible",
        "latest_observed_attempt": 1,
        "target_attempt_number": 2,
        "next_attempt_number": 2,
        "restart_scope": "full_m26_orchestration",
        "requires_manual_external_authority": True,
        "automatic_retry": False,
        "target_completion_already_persisted": True,
        "external_side_effect_idempotency_established": False,
    }
    assert plan["history"][0]["failure_role"] == "model_coach_provider"
    assert plan["history"][0]["evaluator"] is None
    assert plan["history"][0]["provider"]["failure_kind"] == kind
    assert CANARY not in canonical_json(plan)
    assert plan["authority_boundary"]["executes_retry"] is False
    assert plan["authority_boundary"]["authorizes_retry"] is False
    assert validate_reviewed_coaching_recovery_plan(plan) == plan
    assert validate_persisted_reviewed_coaching_recovery_plan(
        store=store,
        participant_id="P01",
        plan=plan,
    ) == plan


def test_evaluator_failure_after_provider_success_is_partial_failure_prefix(
    tmp_path,
) -> None:
    store, run, provider, evaluator = _target_run(tmp_path, attempt_number=2)
    assert evaluator is not None
    provider_attempt_one = _success_at(provider, 1)
    evaluator_failure = _failure_at(
        evaluator,
        attempt_number=1,
        kind="transient",
    )

    result = build_reviewed_coaching_recovery_reconciliation(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={
            "model_coach_provider": [provider_attempt_one],
            "model_coaching_evaluator": [evaluator_failure],
        },
        max_attempts=2,
    )

    attempt = result.plan["history"][0]
    assert attempt["outcome"] == "failed"
    assert attempt["failure_role"] == "model_coaching_evaluator"
    assert attempt["provider"]["status"] == "succeeded"
    assert attempt["provider"]["matched_target_execution"] is False
    assert attempt["evaluator"]["failure_kind"] == "transient"
    assert result.plan["reconciliation"]["state"] == "resume_eligible"
    assert result.plan["reconciliation"]["restart_scope"] == (
        "full_m26_orchestration"
    )


def test_complete_multi_attempt_history_must_end_at_exact_persisted_target(
    tmp_path,
) -> None:
    store, run, provider, evaluator = _target_run(tmp_path, attempt_number=2)
    assert evaluator is not None
    histories = {
        "model_coach_provider": [_success_at(provider, 1), provider],
        "model_coaching_evaluator": [
            _failure_at(evaluator, attempt_number=1, kind="timeout"),
            evaluator,
        ],
    }

    result = build_reviewed_coaching_recovery_reconciliation(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories=histories,
        max_attempts=2,
    )

    plan = result.plan
    assert [item["outcome"] for item in plan["history"]] == [
        "failed",
        "succeeded",
    ]
    assert plan["history"][-1]["provider"]["matched_target_execution"] is True
    assert plan["history"][-1]["evaluator"]["matched_target_execution"] is True
    assert plan["reconciliation"]["state"] == "complete"
    assert plan["reconciliation"]["next_attempt_number"] is None
    assert plan["reconciliation"]["requires_manual_external_authority"] is False


def test_permanent_failure_cannot_reconcile_to_later_target(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="permanent")

    with pytest.raises(
        ReviewedCoachingRecoveryError,
        match="permanent or non-retryable",
    ):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [failed]},
            max_attempts=2,
        )

    assert store.list_refs(participant_id="P01", kind=M34_SCHEMA_VERSION) == ()


def test_duplicate_attempt_number_is_rejected(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="timeout")

    with pytest.raises(ReviewedCoachingRecoveryError, match="duplicate attempt"):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [failed, failed]},
            max_attempts=2,
        )


def test_noncontiguous_attempt_history_is_rejected(tmp_path) -> None:
    store, run, provider, evaluator = _target_run(tmp_path, attempt_number=3)
    assert evaluator is not None
    first = _failure_at(provider, attempt_number=1, kind="timeout")

    with pytest.raises(ReviewedCoachingRecoveryError, match="globally contiguous"):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={
                "model_coach_provider": [first, provider],
                "model_coaching_evaluator": [evaluator],
            },
            max_attempts=3,
        )


def test_wrong_final_success_is_rejected_even_with_valid_m24_identity(tmp_path) -> None:
    store, run, provider, evaluator = _target_run(tmp_path, attempt_number=2)
    assert evaluator is not None
    first = _failure_at(provider, attempt_number=1, kind="timeout")
    wrong_final = copy.deepcopy(provider)
    wrong_final["response_ref"]["fingerprint"] = "0" * 64
    wrong_final = _reidentity_execution(wrong_final)

    with pytest.raises(
        ReviewedCoachingRecoveryError,
        match="final provider execution does not match",
    ):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={
                "model_coach_provider": [first, wrong_final],
                "model_coaching_evaluator": [evaluator],
            },
            max_attempts=2,
        )


def test_cross_run_request_substitution_is_rejected(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    foreign = _failure_at(provider, attempt_number=1, kind="transient")
    foreign["request_ref"]["fingerprint"] = "f" * 64
    foreign = _reidentity_execution(foreign)

    with pytest.raises(ReviewedCoachingRecoveryError, match="request identity"):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [foreign]},
            max_attempts=2,
        )


@pytest.mark.parametrize(
    "fingerprint_key",
    ["m25_review_fingerprint", "m20_model_evaluation_fingerprint"],
)
def test_rehashed_stale_review_or_evaluation_fingerprint_fails_persisted_recheck(
    tmp_path,
    fingerprint_key,
) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="timeout")
    result = build_reviewed_coaching_recovery_reconciliation(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={"model_coach_provider": [failed]},
        max_attempts=2,
    )
    tampered = copy.deepcopy(result.plan)
    tampered["source_fingerprints"][fingerprint_key] = "0" * 64
    tampered = _reidentity_plan(tampered)

    assert validate_reviewed_coaching_recovery_plan(tampered) == tampered
    with pytest.raises(
        ReviewedCoachingRecoveryError,
        match="source fingerprints drifted",
    ):
        validate_persisted_reviewed_coaching_recovery_plan(
            store=store,
            participant_id="P01",
            plan=tampered,
        )


def test_automatic_retry_authority_is_rejected(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="timeout")
    failed["execution_policy"]["automatic_retry"] = True
    failed = _reidentity_execution(failed)

    with pytest.raises(ReviewedCoachingRecoveryError, match="automatic retry"):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [failed]},
            max_attempts=2,
        )


def test_repeated_build_is_content_idempotent(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="timeout")
    args = {
        "store": store,
        "participant_id": "P01",
        "run_artifact_id": run.run_ref.artifact_id,
        "attempt_histories": {"model_coach_provider": [failed]},
        "max_attempts": 2,
    }

    first = build_reviewed_coaching_recovery_reconciliation(**args)
    second = build_reviewed_coaching_recovery_reconciliation(**args)

    assert first.plan == second.plan
    assert first.plan_ref == second.plan_ref
    assert first.ledger_ref == second.ledger_ref
    assert store.list_refs(participant_id="P01", kind=M34_SCHEMA_VERSION) == (
        first.plan_ref,
    )


def test_deterministic_target_builds_zero_execution_complete_plan(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    run = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
    )

    result = build_reviewed_coaching_recovery_reconciliation(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={},
    )

    plan = result.plan
    assert plan["target"] == {
        "attempt_number": 0,
        "roles": [],
        "execution_fingerprints": {},
        "completed_run": True,
    }
    assert plan["history"] == []
    assert plan["reconciliation"]["state"] == "complete"
    assert plan["source_fingerprints"]["m19_model_coaching_fingerprint"] is None
    assert plan["source_fingerprints"]["m20_model_evaluation_fingerprint"] is None


def test_wrong_participant_fails_closed(tmp_path) -> None:
    store, run, provider, _ = _target_run(tmp_path, attempt_number=2)
    failed = _failure_at(provider, attempt_number=1, kind="timeout")

    with pytest.raises(ReviewedCoachingRecoveryError, match="participant-scoped"):
        build_reviewed_coaching_recovery_reconciliation(
            store=store,
            participant_id="OTHER",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [failed]},
            max_attempts=2,
        )
