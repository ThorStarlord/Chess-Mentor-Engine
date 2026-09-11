"""M31 hermetic privacy and retry preflight over the M24/M26 execution seam."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import EXECUTION_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import M26_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import (
    M27_SCHEMA_VERSION,
    build_reviewed_coaching_execution_ledger,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    StoredArtifact,
    prepare_artifact,
)

M31_SCHEMA_VERSION = "m31.execution-envelope-privacy-retry-preflight.v1"
M31_CLAIM_SCOPE = "hermetic_execution_envelope_preflight_only"
SYNTHETIC_CANARY_PREFIX = "CME_TEST_CANARY_"

_EXECUTION_ROLES = (
    "model_coach_provider",
    "model_coaching_evaluator",
)
_RETRYABLE_FAILURE_KINDS = {"timeout", "transient"}
_EXECUTION_KEYS = {
    "schema_version",
    "role",
    "endpoint",
    "request_ref",
    "execution_policy",
    "status",
    "response_ref",
    "failure",
    "claim_scope",
    "authority_boundary",
    "execution_id",
    "fingerprint",
}
_POLICY_KEYS = {
    "timeout_ms",
    "attempt_number",
    "automatic_retry",
    "timeout_enforcement",
    "unknown_exception_disposition",
}
_FAILURE_KEYS = {
    "kind",
    "retryable",
    "exception_type",
    "detail",
}
_AUTHORITY_BOUNDARY = {
    "executes_external_calls": False,
    "stores_live_credentials": False,
    "grants_automatic_retry": False,
    "executes_retry": False,
    "chooses_production_provider": False,
    "establishes_model_output_truth": False,
    "establishes_privacy_or_security_approval": False,
}
_HERMETIC_CONTRACT = {
    "synthetic_canary_prefix": SYNTHETIC_CANARY_PREFIX,
    "live_credentials_supported": False,
    "failure_details_copied_to_report": False,
    "model_content_copied_to_report": False,
    "automatic_retry": False,
    "retry_mode": "manual_plan_validation_only",
}


class ExecutionEnvelopePreflightError(ValueError):
    """M31 cannot establish a bounded hermetic execution-envelope preflight."""


@dataclass(frozen=True, slots=True)
class ExecutionEnvelopePreflightResult:
    """One persisted M31 report and its exact M26/M27 roots."""

    report: dict[str, Any]
    report_ref: ArtifactRef
    run_ref: ArtifactRef
    ledger_ref: ArtifactRef


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ExecutionEnvelopePreflightError(f"{label} must not be empty")
    return value


def _find_run_ref(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    run_artifact_id: str,
) -> ArtifactRef:
    matches = tuple(
        ref
        for ref in store.list_refs(
            participant_id=participant_id,
            kind=M26_SCHEMA_VERSION,
        )
        if ref.artifact_id == run_artifact_id
    )
    if len(matches) != 1:
        raise ExecutionEnvelopePreflightError(
            "M26 run must resolve exactly one participant-scoped artifact"
        )
    return matches[0]


def _validate_canaries(values: Sequence[str]) -> tuple[str, ...]:
    canaries = tuple(values)
    if not canaries:
        raise ExecutionEnvelopePreflightError(
            "at least one synthetic canary is required"
        )
    if len(set(canaries)) != len(canaries):
        raise ExecutionEnvelopePreflightError("synthetic canaries must be unique")
    for value in canaries:
        if type(value) is not str or not value.startswith(SYNTHETIC_CANARY_PREFIX):
            raise ExecutionEnvelopePreflightError(
                "only CME_TEST_CANARY_ synthetic markers are accepted"
            )
        suffix = value[len(SYNTHETIC_CANARY_PREFIX) :]
        if len(suffix) < 8 or any(char.isspace() for char in suffix):
            raise ExecutionEnvelopePreflightError(
                "synthetic canary suffix must contain at least eight "
                "non-space characters"
            )
    return canaries


def _scan_text(text: str, canaries: tuple[str, ...], *, label: str) -> None:
    if any(canary in text for canary in canaries):
        raise ExecutionEnvelopePreflightError(
            f"synthetic canary leakage detected in {label}"
        )


def _scan_value(value: object, canaries: tuple[str, ...], *, label: str) -> None:
    _scan_text(canonical_json(value), canaries, label=label)


def _execution_identity(record: Any) -> dict[str, Any]:
    if type(record) is not dict or set(record) != _EXECUTION_KEYS:
        raise ExecutionEnvelopePreflightError("M24 execution record shape mismatch")
    if record["schema_version"] != EXECUTION_SCHEMA_VERSION:
        raise ExecutionEnvelopePreflightError("M24 execution schema mismatch")
    role = record["role"]
    if role not in _EXECUTION_ROLES:
        raise ExecutionEnvelopePreflightError("M24 execution role is unsupported")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"execution_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    if record["fingerprint"] != fingerprint:
        raise ExecutionEnvelopePreflightError("M24 execution fingerprint mismatch")
    if record["execution_id"] != f"m24_execution_{fingerprint[:20]}":
        raise ExecutionEnvelopePreflightError("M24 execution identity mismatch")

    policy = record["execution_policy"]
    if type(policy) is not dict or set(policy) != _POLICY_KEYS:
        raise ExecutionEnvelopePreflightError("M24 execution policy shape mismatch")
    if type(policy["timeout_ms"]) is not int or policy["timeout_ms"] <= 0:
        raise ExecutionEnvelopePreflightError("M24 timeout policy is invalid")
    if type(policy["attempt_number"]) is not int or policy["attempt_number"] <= 0:
        raise ExecutionEnvelopePreflightError("M24 attempt number is invalid")
    if policy["automatic_retry"] is not False:
        raise ExecutionEnvelopePreflightError(
            "M31 rejects automatic retry authority"
        )
    if policy["timeout_enforcement"] != "adapter_reported":
        raise ExecutionEnvelopePreflightError("M24 timeout enforcement drifted")
    if policy["unknown_exception_disposition"] != "permanent":
        raise ExecutionEnvelopePreflightError(
            "M24 unknown-exception disposition drifted"
        )

    status = record["status"]
    failure = record["failure"]
    response_ref = record["response_ref"]
    if status == "succeeded":
        if failure is not None or type(response_ref) is not dict:
            raise ExecutionEnvelopePreflightError(
                "successful M24 execution outcome is inconsistent"
            )
    elif status == "failed":
        if response_ref is not None or type(failure) is not dict:
            raise ExecutionEnvelopePreflightError(
                "failed M24 execution outcome is inconsistent"
            )
        if set(failure) != _FAILURE_KEYS:
            raise ExecutionEnvelopePreflightError("M24 failure shape mismatch")
        expected_retryable = failure["kind"] in _RETRYABLE_FAILURE_KINDS
        if failure["retryable"] is not expected_retryable:
            raise ExecutionEnvelopePreflightError(
                "M24 failure retryability classification drifted"
            )
    else:
        raise ExecutionEnvelopePreflightError("M24 execution status is invalid")
    return record


def _persisted_executions(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    run_artifact: StoredArtifact,
) -> dict[str, tuple[ArtifactRef, dict[str, Any]]]:
    executions: dict[str, tuple[ArtifactRef, dict[str, Any]]] = {}
    for ref in run_artifact.dependencies:
        if ref.kind != EXECUTION_SCHEMA_VERSION:
            continue
        artifact = store.get(ref, participant_id=participant_id)
        record = _execution_identity(artifact.payload)
        role = record["role"]
        if role in executions:
            raise ExecutionEnvelopePreflightError(
                "M26 run contains duplicate persisted execution role"
            )
        executions[role] = (ref, record)
    return executions


def _normalize_histories(
    attempt_histories: Mapping[str, Sequence[dict[str, Any]]],
) -> dict[str, tuple[dict[str, Any], ...]]:
    if not isinstance(attempt_histories, Mapping):
        raise ExecutionEnvelopePreflightError("attempt histories must be a mapping")
    histories: dict[str, tuple[dict[str, Any], ...]] = {}
    for role, values in attempt_histories.items():
        if role not in _EXECUTION_ROLES:
            raise ExecutionEnvelopePreflightError(
                "attempt history contains unsupported execution role"
            )
        if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
            raise ExecutionEnvelopePreflightError(
                "each attempt history must be an ordered sequence"
            )
        records = tuple(values)
        if not records:
            raise ExecutionEnvelopePreflightError(
                "attempt history must contain at least one record"
            )
        histories[role] = records
    return histories


def _validate_history(
    *,
    role: str,
    records: tuple[dict[str, Any], ...],
    persisted: dict[str, Any],
    max_attempts: int,
) -> dict[str, Any]:
    if len(records) > max_attempts:
        raise ExecutionEnvelopePreflightError(
            "attempt history exceeds the declared manual retry plan"
        )
    normalized = tuple(_execution_identity(record) for record in records)
    if any(record["role"] != role for record in normalized):
        raise ExecutionEnvelopePreflightError("attempt history role drifted")

    first = normalized[0]
    endpoint = first["endpoint"]
    request_ref = first["request_ref"]
    timeout_ms = first["execution_policy"]["timeout_ms"]
    expected_attempts = list(range(1, len(normalized) + 1))
    actual_attempts = [
        record["execution_policy"]["attempt_number"] for record in normalized
    ]
    if actual_attempts != expected_attempts:
        raise ExecutionEnvelopePreflightError(
            "attempt history must be contiguous and start at attempt one"
        )
    for record in normalized:
        if record["endpoint"] != endpoint or record["request_ref"] != request_ref:
            raise ExecutionEnvelopePreflightError(
                "manual retry history must preserve endpoint and request identity"
            )
        if record["execution_policy"]["timeout_ms"] != timeout_ms:
            raise ExecutionEnvelopePreflightError(
                "manual retry history must preserve the declared timeout"
            )

    for record in normalized[:-1]:
        if record["status"] != "failed":
            raise ExecutionEnvelopePreflightError(
                "manual retry cannot follow a successful attempt"
            )
        failure = record["failure"]
        assert isinstance(failure, dict)
        if failure["kind"] not in _RETRYABLE_FAILURE_KINDS:
            raise ExecutionEnvelopePreflightError(
                "manual retry transition requires a retryable failure"
            )
        if failure["retryable"] is not True:
            raise ExecutionEnvelopePreflightError(
                "manual retry transition requires retryable=true"
            )

    final = normalized[-1]
    if final["status"] != "succeeded":
        raise ExecutionEnvelopePreflightError(
            "persisted M26 execution history must end in success"
        )
    if final != persisted:
        raise ExecutionEnvelopePreflightError(
            "final attempt does not match the exact persisted M24 execution"
        )

    return {
        "role": role,
        "attempt_count": len(normalized),
        "max_attempts": max_attempts,
        "automatic_retry": False,
        "retryable_failure_kinds": sorted(_RETRYABLE_FAILURE_KINDS),
        "manual_retry_transitions": len(normalized) - 1,
        "attempts": [
            {
                "attempt_number": record["execution_policy"]["attempt_number"],
                "status": record["status"],
                "failure_kind": (
                    None if record["failure"] is None else record["failure"]["kind"]
                ),
                "retryable": (
                    None
                    if record["failure"] is None
                    else record["failure"]["retryable"]
                ),
            }
            for record in normalized
        ],
        "final_execution_id": final["execution_id"],
        "final_execution_fingerprint": final["fingerprint"],
    }


def _artifact_closure(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    roots: Sequence[ArtifactRef],
) -> tuple[StoredArtifact, ...]:
    pending = list(roots)
    seen: set[str] = set()
    artifacts: list[StoredArtifact] = []
    while pending:
        ref = pending.pop()
        if ref.digest in seen:
            continue
        artifact = store.get(ref, participant_id=participant_id)
        seen.add(ref.digest)
        artifacts.append(artifact)
        pending.extend(artifact.dependencies)
    return tuple(sorted(artifacts, key=lambda item: item.ref.digest))


def _scan_artifacts(
    artifacts: Sequence[StoredArtifact],
    canaries: tuple[str, ...],
    *,
    label: str,
) -> None:
    for artifact in artifacts:
        _scan_text(artifact.payload_json, canaries, label=label)
        _scan_value(artifact.ref.to_dict(), canaries, label=label)


def build_execution_envelope_preflight(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    run_artifact_id: str,
    attempt_histories: Mapping[str, Sequence[dict[str, Any]]],
    synthetic_canaries: Sequence[str],
    max_attempts: int = 3,
) -> ExecutionEnvelopePreflightResult:
    """Validate synthetic-canary privacy and manual retry history only."""
    _nonempty(participant_id, "participant_id")
    _nonempty(run_artifact_id, "run_artifact_id")
    if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
        raise ExecutionEnvelopePreflightError(
            "max_attempts must be an integer from 1 through 10"
        )
    canaries = _validate_canaries(synthetic_canaries)
    histories = _normalize_histories(attempt_histories)
    _scan_value(histories, canaries, label="M24 attempt history")

    run_ref = _find_run_ref(
        store,
        participant_id=participant_id,
        run_artifact_id=run_artifact_id,
    )
    run_artifact = store.get(run_ref, participant_id=participant_id)
    initial_closure = _artifact_closure(
        store,
        participant_id=participant_id,
        roots=(run_ref,),
    )
    _scan_artifacts(
        initial_closure,
        canaries,
        label="persisted M26 dependency closure",
    )

    persisted = _persisted_executions(
        store,
        participant_id=participant_id,
        run_artifact=run_artifact,
    )
    if set(histories) != set(persisted):
        raise ExecutionEnvelopePreflightError(
            "attempt-history roles must exactly match persisted M26 execution roles"
        )

    history_summaries = [
        _validate_history(
            role=role,
            records=histories[role],
            persisted=persisted[role][1],
            max_attempts=max_attempts,
        )
        for role in _EXECUTION_ROLES
        if role in persisted
    ]

    ledger = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id=participant_id,
        run_artifact_ids=(run_ref.artifact_id,),
    )
    if ledger.ledger_record.get("schema_version") != M27_SCHEMA_VERSION:
        raise ExecutionEnvelopePreflightError("M27 ledger schema mismatch")
    if ledger.ledger_record.get("run_count") != 1:
        raise ExecutionEnvelopePreflightError(
            "M31 requires exactly one mechanically verified M26 run"
        )
    complete_closure = _artifact_closure(
        store,
        participant_id=participant_id,
        roots=(run_ref, ledger.ledger_ref),
    )
    _scan_artifacts(
        complete_closure,
        canaries,
        label="persisted M26/M27/review artifact closure",
    )

    payload: dict[str, Any] = {
        "schema_version": M31_SCHEMA_VERSION,
        "participant_id": participant_id,
        "source_refs": {
            "m26_run": run_ref.to_dict(),
            "m27_ledger": ledger.ledger_ref.to_dict(),
            "m24_executions": [
                persisted[role][0].to_dict()
                for role in _EXECUTION_ROLES
                if role in persisted
            ],
        },
        "retry_preflight": {
            "mode": "manual_plan_validation_only",
            "automatic_retry": False,
            "max_attempts": max_attempts,
            "histories": history_summaries,
        },
        "privacy_preflight": {
            "mode": "synthetic_canary_scan",
            "synthetic_canary_count": len(canaries),
            "synthetic_canary_values_stored": False,
            "attempt_history_scan": "clear",
            "persisted_artifact_scan": "clear",
            "scanned_artifact_count": len(complete_closure),
        },
        "hermetic_contract": dict(_HERMETIC_CONTRACT),
        "claim_scope": M31_CLAIM_SCOPE,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }
    _scan_value(payload, canaries, label="M31 report")
    fingerprint = _fingerprint(payload)
    report = {
        **payload,
        "preflight_id": f"execution_envelope_preflight_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }
    write = ArtifactWrite(
        M31_SCHEMA_VERSION,
        report["preflight_id"],
        participant_id,
        report,
        (run_ref, ledger.ledger_ref),
    )
    report_ref = prepare_artifact(write)[0]
    store.put_many((write,))
    return ExecutionEnvelopePreflightResult(
        report=report,
        report_ref=report_ref,
        run_ref=run_ref,
        ledger_ref=ledger.ledger_ref,
    )
