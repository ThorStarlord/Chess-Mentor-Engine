"""M31 hermetic privacy and manual-retry preflight qualification."""

from __future__ import annotations

import copy
import hashlib

import pytest
from test_m24_provider_conformance import (
    _Provider,
    _provider_endpoint,
)
from test_m26_persistent_reviewed_coaching import S13, _store_lineage
from test_m27_reviewed_coaching_execution_ledger import _model_run

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    PermanentExternalExecutionError,
    TransientExternalExecutionError,
)
from chess_mentor_engine.execution_envelope_preflight import (
    M31_CLAIM_SCOPE,
    M31_SCHEMA_VERSION,
    ExecutionEnvelopePreflightError,
    build_execution_envelope_preflight,
)
from chess_mentor_engine.reviewed_coaching import (
    PersistentReviewedCoachingError,
    run_persistent_reviewed_coaching,
)

CANARY = "CME_TEST_CANARY_12345678"
SECOND_CANARY = "CME_TEST_CANARY_ABCDEFGH"


class _CanaryHoldingProvider(_Provider):
    def __init__(self, canary: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.synthetic_canary = canary


def _provider_run(
    tmp_path,
    *,
    provider=None,
    attempt_number: int = 1,
):
    store, db, _, compared_ref = _store_lineage(tmp_path)
    result = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
        provider=_Provider() if provider is None else provider,
        provider_endpoint=_provider_endpoint(),
        attempt_number=attempt_number,
    )
    return store, db, compared_ref, result


def _persisted_execution(store, ref):
    assert ref is not None
    return store.get(ref, participant_id="P01").payload


def _reidentity_execution(record: dict) -> dict:
    value = copy.deepcopy(record)
    payload = {
        key: item
        for key, item in value.items()
        if key not in {"execution_id", "fingerprint"}
    }
    fingerprint = hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest()
    return {
        **payload,
        "execution_id": f"m24_execution_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def test_provider_and_evaluator_single_attempt_preflight_is_summary_safe(
    tmp_path,
) -> None:
    store, _, run = _model_run(tmp_path)
    provider_record = _persisted_execution(store, run.provider_execution_ref)
    evaluator_record = _persisted_execution(store, run.evaluator_execution_ref)

    result = build_execution_envelope_preflight(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={
            "model_coach_provider": [provider_record],
            "model_coaching_evaluator": [evaluator_record],
        },
        synthetic_canaries=(CANARY, SECOND_CANARY),
        max_attempts=3,
    )

    report = result.report
    assert report["schema_version"] == M31_SCHEMA_VERSION
    assert report["claim_scope"] == M31_CLAIM_SCOPE
    assert report["retry_preflight"]["automatic_retry"] is False
    assert report["retry_preflight"]["mode"] == "manual_plan_validation_only"
    assert [
        item["role"] for item in report["retry_preflight"]["histories"]
    ] == ["model_coach_provider", "model_coaching_evaluator"]
    assert all(
        item["attempt_count"] == 1
        for item in report["retry_preflight"]["histories"]
    )
    assert report["privacy_preflight"]["synthetic_canary_count"] == 2
    assert report["privacy_preflight"]["synthetic_canary_values_stored"] is False
    assert report["privacy_preflight"]["attempt_history_scan"] == "clear"
    assert report["privacy_preflight"]["persisted_artifact_scan"] == "clear"
    assert report["authority_boundary"]["executes_external_calls"] is False
    assert report["authority_boundary"]["grants_automatic_retry"] is False
    assert report["authority_boundary"]["executes_retry"] is False

    serialized = canonical_json(report)
    for sensitive in (
        CANARY,
        SECOND_CANARY,
        "Review the strongest reply before committing.",
        "Fixture pass for",
        "I would play e4.",
    ):
        assert sensitive not in serialized

    stored = store.get(result.report_ref, participant_id="P01")
    assert stored.payload == report
    assert {ref.digest for ref in stored.dependencies} == {
        result.run_ref.digest,
        result.ledger_ref.digest,
    }


def test_adapter_held_synthetic_canary_does_not_enter_persisted_outputs(
    tmp_path,
) -> None:
    store, _, _, run = _provider_run(
        tmp_path,
        provider=_CanaryHoldingProvider(CANARY),
    )
    provider_record = _persisted_execution(store, run.provider_execution_ref)

    result = build_execution_envelope_preflight(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={"model_coach_provider": [provider_record]},
        synthetic_canaries=(CANARY,),
    )

    assert result.report["privacy_preflight"]["persisted_artifact_scan"] == "clear"
    for ref in store.list_refs(participant_id="P01"):
        artifact = store.get(ref, participant_id="P01")
        assert CANARY not in artifact.payload_json


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("synthetic timeout"),
        TransientExternalExecutionError("synthetic rate-limit/transport failure"),
    ],
)
def test_retryable_failure_then_success_forms_valid_manual_history(
    tmp_path,
    failure,
) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    with pytest.raises(PersistentReviewedCoachingError) as captured:
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=_Provider(failure=failure),
            provider_endpoint=_provider_endpoint(),
            attempt_number=1,
        )
    failed_record = captured.value.execution_record
    assert failed_record is not None
    assert failed_record["status"] == "failed"
    assert failed_record["failure"]["retryable"] is True

    run = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
        provider=_Provider(),
        provider_endpoint=_provider_endpoint(),
        attempt_number=2,
    )
    persisted = _persisted_execution(store, run.provider_execution_ref)

    result = build_execution_envelope_preflight(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
        attempt_histories={"model_coach_provider": [failed_record, persisted]},
        synthetic_canaries=(CANARY,),
        max_attempts=2,
    )

    history = result.report["retry_preflight"]["histories"][0]
    assert history["attempt_count"] == 2
    assert history["manual_retry_transitions"] == 1
    assert history["attempts"][0]["status"] == "failed"
    assert history["attempts"][0]["retryable"] is True
    assert history["attempts"][1]["status"] == "succeeded"
    assert history["automatic_retry"] is False


def test_permanent_failure_cannot_be_followed_by_retry_in_preflight(tmp_path) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    with pytest.raises(PersistentReviewedCoachingError) as captured:
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=_Provider(
                failure=PermanentExternalExecutionError("synthetic permanent failure")
            ),
            provider_endpoint=_provider_endpoint(),
            attempt_number=1,
        )
    failed_record = captured.value.execution_record
    assert failed_record is not None
    assert failed_record["failure"]["retryable"] is False

    run = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
        provider=_Provider(),
        provider_endpoint=_provider_endpoint(),
        attempt_number=2,
    )
    persisted = _persisted_execution(store, run.provider_execution_ref)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="requires a retryable failure",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={
                "model_coach_provider": [failed_record, persisted]
            },
            synthetic_canaries=(CANARY,),
            max_attempts=2,
        )

    assert store.list_refs(participant_id="P01", kind=M31_SCHEMA_VERSION) == ()


def test_failed_attempt_detail_canary_is_rejected_without_echo_or_report(
    tmp_path,
) -> None:
    store, _, _, compared_ref = _store_lineage(tmp_path)
    with pytest.raises(PersistentReviewedCoachingError) as captured:
        run_persistent_reviewed_coaching(
            store=store,
            participant_id="P01",
            session_artifact_id=compared_ref.artifact_id,
            grounding_created_at=S13,
            provider=_Provider(failure=TimeoutError(f"timeout {CANARY}")),
            provider_endpoint=_provider_endpoint(),
            attempt_number=1,
        )
    failed_record = captured.value.execution_record
    assert failed_record is not None
    assert CANARY in canonical_json(failed_record)

    run = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=S13,
        provider=_Provider(),
        provider_endpoint=_provider_endpoint(),
        attempt_number=2,
    )
    persisted = _persisted_execution(store, run.provider_execution_ref)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="synthetic canary leakage detected in M24 attempt history",
    ) as rejected:
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={
                "model_coach_provider": [failed_record, persisted]
            },
            synthetic_canaries=(CANARY,),
            max_attempts=2,
        )

    assert CANARY not in str(rejected.value)
    assert store.list_refs(participant_id="P01", kind=M31_SCHEMA_VERSION) == ()


def test_successful_provider_content_canary_is_detected_in_persisted_closure(
    tmp_path,
) -> None:
    store, _, _, run = _provider_run(
        tmp_path,
        provider=_Provider(rendered_content=f"synthetic leak {CANARY}"),
    )
    persisted = _persisted_execution(store, run.provider_execution_ref)
    assert CANARY in canonical_json(run.read_model)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="persisted M26 dependency closure",
    ) as rejected:
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [persisted]},
            synthetic_canaries=(CANARY,),
        )

    assert CANARY not in str(rejected.value)
    assert store.list_refs(participant_id="P01", kind=M31_SCHEMA_VERSION) == ()


def test_forged_automatic_retry_authority_is_rejected(tmp_path) -> None:
    store, _, _, run = _provider_run(tmp_path)
    persisted = _persisted_execution(store, run.provider_execution_ref)
    forged = copy.deepcopy(persisted)
    forged["execution_policy"]["automatic_retry"] = True
    forged = _reidentity_execution(forged)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="rejects automatic retry authority",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [forged]},
            synthetic_canaries=(CANARY,),
        )


def test_noncontiguous_or_over_budget_attempt_history_is_rejected(tmp_path) -> None:
    store, _, _, run = _provider_run(tmp_path, attempt_number=2)
    persisted = _persisted_execution(store, run.provider_execution_ref)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="contiguous and start at attempt one",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [persisted]},
            synthetic_canaries=(CANARY,),
            max_attempts=2,
        )

    first = copy.deepcopy(persisted)
    first["execution_policy"]["attempt_number"] = 1
    first = _reidentity_execution(first)
    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="exceeds the declared manual retry plan",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [first, persisted]},
            synthetic_canaries=(CANARY,),
            max_attempts=1,
        )


def test_history_roles_and_participant_scope_fail_closed(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    provider_record = _persisted_execution(store, run.provider_execution_ref)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="roles must exactly match",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [provider_record]},
            synthetic_canaries=(CANARY,),
        )

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="participant-scoped",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="OTHER",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={},
            synthetic_canaries=(CANARY,),
        )


def test_only_explicit_synthetic_canaries_are_accepted(tmp_path) -> None:
    store, _, _, run = _provider_run(tmp_path)
    persisted = _persisted_execution(store, run.provider_execution_ref)

    with pytest.raises(
        ExecutionEnvelopePreflightError,
        match="only CME_TEST_CANARY_ synthetic markers are accepted",
    ):
        build_execution_envelope_preflight(
            store=store,
            participant_id="P01",
            run_artifact_id=run.run_ref.artifact_id,
            attempt_histories={"model_coach_provider": [persisted]},
            synthetic_canaries=("sk-live-not-accepted",),
        )


def test_repeated_preflight_is_content_idempotent(tmp_path) -> None:
    store, _, _, run = _provider_run(tmp_path)
    persisted = _persisted_execution(store, run.provider_execution_ref)
    args = {
        "store": store,
        "participant_id": "P01",
        "run_artifact_id": run.run_ref.artifact_id,
        "attempt_histories": {"model_coach_provider": [persisted]},
        "synthetic_canaries": (CANARY,),
        "max_attempts": 3,
    }

    first = build_execution_envelope_preflight(**args)
    second = build_execution_envelope_preflight(**args)

    assert first.report == second.report
    assert first.report_ref == second.report_ref
    assert first.ledger_ref == second.ledger_ref
    assert store.list_refs(participant_id="P01", kind=M31_SCHEMA_VERSION) == (
        first.report_ref,
    )
