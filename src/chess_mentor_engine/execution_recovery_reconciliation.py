"""M34 hermetic recovery reconciliation over M24/M26 reviewed coaching."""

from __future__ import annotations

import copy
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import EXECUTION_SCHEMA_VERSION
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import M26_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import (
    M27_SCHEMA_VERSION,
    ReviewedCoachingLedgerError,
    build_reviewed_coaching_execution_ledger,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    StorageError,
    prepare_artifact,
)

M34_SCHEMA_VERSION = "m34.reviewed-coaching-recovery-reconciliation.v1"
M34_CLAIM_SCOPE = "hermetic_reviewed_coaching_recovery_plan_only"
M34_PLAN_MODE = "historical_prefix_reconciliation_against_persisted_target"

_PROVIDER_ROLE = "model_coach_provider"
_EVALUATOR_ROLE = "model_coaching_evaluator"
_EXECUTION_ROLES = (_PROVIDER_ROLE, _EVALUATOR_ROLE)
_RETRYABLE_FAILURE_KINDS = {"timeout", "transient"}
_FAILURE_KINDS = {
    "invalid_request",
    "request_mutation",
    "timeout",
    "transient",
    "permanent",
    "malformed_response",
    "identity_mismatch",
    "chronology_violation",
}
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
_FAILURE_KEYS = {"kind", "retryable", "exception_type", "detail"}
_M24_AUTHORITY = {
    "may_classify_execution": True,
    "may_create_chess_facts": False,
    "may_create_learner_hypotheses": False,
    "may_select_training": False,
    "may_establish_model_output_truth": False,
}
_M34_AUTHORITY = {
    "executes_external_calls": False,
    "authorizes_retry": False,
    "executes_retry": False,
    "mutates_reviewed_coaching": False,
    "chooses_production_provider": False,
    "establishes_external_side_effect_idempotency": False,
    "establishes_model_output_truth": False,
    "establishes_privacy_or_security_approval": False,
}
_HERMETIC_CONTRACT = {
    "plan_mode": M34_PLAN_MODE,
    "live_credentials_supported": False,
    "failure_details_copied_to_plan": False,
    "request_payloads_copied_to_plan": False,
    "model_content_copied_to_plan": False,
    "evaluator_rationales_copied_to_plan": False,
    "automatic_retry": False,
    "restart_scope_if_resume_eligible": "full_m26_orchestration",
    "target_completion_already_persisted": True,
}
_PLAN_KEYS = {
    "schema_version",
    "participant_id",
    "claim_scope",
    "plan_mode",
    "source_refs",
    "source_fingerprints",
    "target",
    "history",
    "history_fingerprint",
    "reconciliation",
    "hermetic_contract",
    "authority_boundary",
    "recovery_plan_id",
    "fingerprint",
}
_SOURCE_FINGERPRINT_KEYS = {
    "m26_run_fingerprint",
    "m27_ledger_fingerprint",
    "m25_review_fingerprint",
    "m19_model_coaching_fingerprint",
    "m20_model_evaluation_fingerprint",
}
_SUMMARY_KEYS = {
    "role",
    "attempt_number",
    "status",
    "failure_kind",
    "retryable",
    "matched_target_execution",
}
_ATTEMPT_KEYS = {
    "attempt_number",
    "provider",
    "evaluator",
    "outcome",
    "failure_role",
}
_RECONCILIATION_KEYS = {
    "state",
    "latest_observed_attempt",
    "target_attempt_number",
    "next_attempt_number",
    "restart_scope",
    "requires_manual_external_authority",
    "automatic_retry",
    "target_completion_already_persisted",
    "external_side_effect_idempotency_established",
}


class ReviewedCoachingRecoveryError(ValueError):
    """M34 cannot reconcile the supplied hermetic execution history."""


@dataclass(frozen=True, slots=True)
class ReviewedCoachingRecoveryResult:
    """One content-addressed M34 dry-run plan and exact persisted roots."""

    plan: dict[str, Any]
    plan_ref: ArtifactRef
    run_ref: ArtifactRef
    ledger_ref: ArtifactRef


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ReviewedCoachingRecoveryError(f"{label} must be a non-empty string")
    return value


def _sha256(value: Any, label: str) -> str:
    value = _nonempty(value, label)
    if (
        len(value) != 64
        or value.lower() != value
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ReviewedCoachingRecoveryError(f"{label} must be a lowercase SHA-256")
    return value


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise ReviewedCoachingRecoveryError(f"{label} shape mismatch")
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
        raise ReviewedCoachingRecoveryError(
            "M26 run must resolve exactly one participant-scoped artifact"
        )
    return matches[0]


def _execution_identity(record: Any) -> dict[str, Any]:
    record = _strict(record, _EXECUTION_KEYS, "M24 execution record")
    if record["schema_version"] != EXECUTION_SCHEMA_VERSION:
        raise ReviewedCoachingRecoveryError("M24 execution schema drifted")
    if record["role"] not in _EXECUTION_ROLES:
        raise ReviewedCoachingRecoveryError("M24 execution role is unsupported")
    if record["claim_scope"] != "external_execution_conformance_only":
        raise ReviewedCoachingRecoveryError("M24 execution claim scope drifted")
    if record["authority_boundary"] != _M24_AUTHORITY:
        raise ReviewedCoachingRecoveryError("M24 execution authority boundary drifted")

    payload = {
        key: item
        for key, item in record.items()
        if key not in {"execution_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    if record["fingerprint"] != fingerprint:
        raise ReviewedCoachingRecoveryError("M24 execution fingerprint mismatch")
    if record["execution_id"] != f"m24_execution_{fingerprint[:20]}":
        raise ReviewedCoachingRecoveryError("M24 execution identity mismatch")

    policy = _strict(record["execution_policy"], _POLICY_KEYS, "M24 execution policy")
    if type(policy["timeout_ms"]) is not int or policy["timeout_ms"] <= 0:
        raise ReviewedCoachingRecoveryError("M24 timeout policy is invalid")
    if type(policy["attempt_number"]) is not int or policy["attempt_number"] <= 0:
        raise ReviewedCoachingRecoveryError("M24 attempt number is invalid")
    if policy["automatic_retry"] is not False:
        raise ReviewedCoachingRecoveryError("M34 rejects automatic retry authority")
    if policy["timeout_enforcement"] != "adapter_reported":
        raise ReviewedCoachingRecoveryError("M24 timeout enforcement drifted")
    if policy["unknown_exception_disposition"] != "permanent":
        raise ReviewedCoachingRecoveryError(
            "M24 unknown-exception disposition drifted"
        )

    if record["status"] == "succeeded":
        if record["failure"] is not None or type(record["response_ref"]) is not dict:
            raise ReviewedCoachingRecoveryError(
                "successful M24 execution outcome is inconsistent"
            )
    elif record["status"] == "failed":
        if record["response_ref"] is not None:
            raise ReviewedCoachingRecoveryError(
                "failed M24 execution must not retain a response"
            )
        failure = _strict(record["failure"], _FAILURE_KEYS, "M24 failure")
        if failure["kind"] not in _FAILURE_KINDS:
            raise ReviewedCoachingRecoveryError("M24 failure kind is unsupported")
        expected_retryable = failure["kind"] in _RETRYABLE_FAILURE_KINDS
        if failure["retryable"] is not expected_retryable:
            raise ReviewedCoachingRecoveryError(
                "M24 failure retryability classification drifted"
            )
        if type(failure["detail"]) is not str:
            raise ReviewedCoachingRecoveryError("M24 failure detail must be text")
    else:
        raise ReviewedCoachingRecoveryError("M24 execution status is invalid")
    return copy.deepcopy(record)


def _target_context(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    run_artifact_id: str,
) -> dict[str, Any]:
    run_ref = _find_run_ref(
        store,
        participant_id=participant_id,
        run_artifact_id=run_artifact_id,
    )
    try:
        ledger = build_reviewed_coaching_execution_ledger(
            store=store,
            participant_id=participant_id,
            run_artifact_ids=(run_ref.artifact_id,),
        )
        if ledger.ledger_record.get("schema_version") != M27_SCHEMA_VERSION:
            raise ReviewedCoachingRecoveryError("M27 ledger schema drifted")
        if ledger.ledger_record.get("run_count") != 1:
            raise ReviewedCoachingRecoveryError(
                "M34 requires exactly one mechanically verified M26 run"
            )
        entry = ledger.ledger_record["runs"][0]
        review_ref = ArtifactRef(**entry["coach_review_ref"])
        if review_ref.kind != COACH_REVIEW_SCHEMA_VERSION:
            raise ReviewedCoachingRecoveryError("M25 review reference kind drifted")
        run_artifact = store.get(run_ref, participant_id=participant_id)
        review_artifact = store.get(review_ref, participant_id=participant_id)
    except (ReviewedCoachingLedgerError, StorageError, TypeError, KeyError) as exc:
        if isinstance(exc, ReviewedCoachingRecoveryError):
            raise
        raise ReviewedCoachingRecoveryError(
            f"persisted M26/M27 target validation failed: {exc}"
        ) from exc

    target_records: dict[str, dict[str, Any]] = {}
    target_refs: dict[str, ArtifactRef] = {}
    for execution in entry["executions"]:
        role = execution["role"]
        ref = ArtifactRef(**execution["execution_ref"])
        artifact = store.get(ref, participant_id=participant_id)
        record = _execution_identity(artifact.payload)
        if record["status"] != "succeeded":
            raise ReviewedCoachingRecoveryError(
                "persisted M26 target execution must be successful"
            )
        target_records[role] = record
        target_refs[role] = ref

    roles = tuple(target_records)
    if roles not in ((), (_PROVIDER_ROLE,), _EXECUTION_ROLES):
        raise ReviewedCoachingRecoveryError("M26 target execution roles drifted")
    attempt_numbers = {
        record["execution_policy"]["attempt_number"]
        for record in target_records.values()
    }
    if len(attempt_numbers) > 1:
        raise ReviewedCoachingRecoveryError(
            "M26 target roles must share one orchestration attempt number"
        )
    target_attempt = 0 if not attempt_numbers else next(iter(attempt_numbers))

    run = run_artifact.payload
    review = review_artifact.payload
    source_fingerprints = review.get("source_fingerprints")
    if type(source_fingerprints) is not dict:
        raise ReviewedCoachingRecoveryError("M25 source fingerprints are missing")
    expected_optional = (
        source_fingerprints.get("model_coaching"),
        source_fingerprints.get("model_evaluation"),
    )
    if roles == () and expected_optional != (None, None):
        raise ReviewedCoachingRecoveryError("deterministic M26 target optionality drifted")
    if roles == (_PROVIDER_ROLE,) and (
        expected_optional[0] is None or expected_optional[1] is not None
    ):
        raise ReviewedCoachingRecoveryError("provider-only M26 target optionality drifted")
    if roles == _EXECUTION_ROLES and any(item is None for item in expected_optional):
        raise ReviewedCoachingRecoveryError("model M26 target optionality drifted")

    return {
        "run_ref": run_ref,
        "ledger_ref": ledger.ledger_ref,
        "review_ref": review_ref,
        "run_fingerprint": run["fingerprint"],
        "ledger_fingerprint": ledger.ledger_record["fingerprint"],
        "review_fingerprint": review["fingerprint"],
        "model_coaching_fingerprint": source_fingerprints.get("model_coaching"),
        "model_evaluation_fingerprint": source_fingerprints.get("model_evaluation"),
        "roles": roles,
        "target_attempt": target_attempt,
        "target_records": target_records,
        "target_refs": target_refs,
    }


def _normalize_histories(
    attempt_histories: Mapping[str, Sequence[dict[str, Any]]],
    *,
    target: dict[str, Any],
) -> dict[str, tuple[dict[str, Any], ...]]:
    if not isinstance(attempt_histories, Mapping):
        raise ReviewedCoachingRecoveryError("attempt histories must be a mapping")
    if any(role not in target["roles"] for role in attempt_histories):
        raise ReviewedCoachingRecoveryError(
            "attempt history contains a role outside the persisted M26 target"
        )
    if not target["roles"]:
        if attempt_histories:
            raise ReviewedCoachingRecoveryError(
                "deterministic M26 target must not have M24 attempt history"
            )
        return {}
    if _PROVIDER_ROLE not in attempt_histories:
        raise ReviewedCoachingRecoveryError(
            "external recovery history requires provider attempts"
        )

    histories: dict[str, tuple[dict[str, Any], ...]] = {}
    for role in target["roles"]:
        values = attempt_histories.get(role, ())
        if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
            raise ReviewedCoachingRecoveryError(
                "each attempt history must be an ordered sequence"
            )
        records = tuple(values)
        if role == _PROVIDER_ROLE and not records:
            raise ReviewedCoachingRecoveryError(
                "provider attempt history must not be empty"
            )
        normalized: list[dict[str, Any]] = []
        seen: set[int] = set()
        previous = 0
        target_record = target["target_records"][role]
        for record in records:
            item = _execution_identity(record)
            if item["role"] != role:
                raise ReviewedCoachingRecoveryError("attempt history role drifted")
            attempt = item["execution_policy"]["attempt_number"]
            if attempt in seen:
                raise ReviewedCoachingRecoveryError(
                    "attempt history contains a duplicate attempt number"
                )
            if attempt <= previous:
                raise ReviewedCoachingRecoveryError(
                    "attempt history must be strictly ordered by attempt number"
                )
            if attempt > target["target_attempt"]:
                raise ReviewedCoachingRecoveryError(
                    "attempt history extends beyond the persisted target attempt"
                )
            if item["endpoint"] != target_record["endpoint"]:
                raise ReviewedCoachingRecoveryError(
                    "attempt history endpoint differs from persisted target"
                )
            if item["request_ref"] != target_record["request_ref"]:
                raise ReviewedCoachingRecoveryError(
                    "attempt history request identity differs from persisted target"
                )
            if (
                item["execution_policy"]["timeout_ms"]
                != target_record["execution_policy"]["timeout_ms"]
            ):
                raise ReviewedCoachingRecoveryError(
                    "attempt history timeout differs from persisted target"
                )
            seen.add(attempt)
            previous = attempt
            normalized.append(item)
        histories[role] = tuple(normalized)
    return histories


def _execution_summary(
    record: dict[str, Any],
    *,
    target_record: dict[str, Any],
) -> dict[str, Any]:
    failure = record["failure"]
    return {
        "role": record["role"],
        "attempt_number": record["execution_policy"]["attempt_number"],
        "status": record["status"],
        "failure_kind": None if failure is None else failure["kind"],
        "retryable": None if failure is None else failure["retryable"],
        "matched_target_execution": record == target_record,
    }


def _build_history(
    histories: dict[str, tuple[dict[str, Any], ...]],
    *,
    target: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not target["roles"]:
        return [], {
            "state": "complete",
            "latest_observed_attempt": 0,
            "target_attempt_number": 0,
            "next_attempt_number": None,
            "restart_scope": "none",
            "requires_manual_external_authority": False,
            "automatic_retry": False,
            "target_completion_already_persisted": True,
            "external_side_effect_idempotency_established": False,
        }

    by_role = {
        role: {
            record["execution_policy"]["attempt_number"]: record
            for record in records
        }
        for role, records in histories.items()
    }
    provider_attempts = set(by_role[_PROVIDER_ROLE])
    latest = max(provider_attempts)
    expected_provider_attempts = set(range(1, latest + 1))
    if provider_attempts != expected_provider_attempts:
        raise ReviewedCoachingRecoveryError(
            "provider attempts must be globally contiguous from attempt one"
        )

    evaluator_by_attempt = by_role.get(_EVALUATOR_ROLE, {})
    if any(attempt not in provider_attempts for attempt in evaluator_by_attempt):
        raise ReviewedCoachingRecoveryError(
            "evaluator history cannot exist without the same provider attempt"
        )

    attempts: list[dict[str, Any]] = []
    for attempt_number in range(1, latest + 1):
        provider = by_role[_PROVIDER_ROLE][attempt_number]
        evaluator = evaluator_by_attempt.get(attempt_number)
        failure_record: dict[str, Any] | None = None
        failure_role: str | None = None

        if provider["status"] == "failed":
            if evaluator is not None:
                raise ReviewedCoachingRecoveryError(
                    "evaluator attempt cannot follow a failed provider in the same attempt"
                )
            outcome = "failed"
            failure_record = provider
            failure_role = _PROVIDER_ROLE
        elif _EVALUATOR_ROLE in target["roles"]:
            if evaluator is None:
                raise ReviewedCoachingRecoveryError(
                    "successful provider attempt requires evaluator outcome"
                )
            if evaluator["status"] == "failed":
                outcome = "failed"
                failure_record = evaluator
                failure_role = _EVALUATOR_ROLE
            else:
                outcome = "succeeded"
        else:
            if evaluator is not None:
                raise ReviewedCoachingRecoveryError(
                    "provider-only target cannot contain evaluator attempts"
                )
            outcome = "succeeded"

        if attempt_number < latest:
            if outcome != "failed" or failure_record is None:
                raise ReviewedCoachingRecoveryError(
                    "later M26 attempt requires the previous attempt to fail"
                )
            failure = failure_record["failure"]
            assert isinstance(failure, dict)
            if (
                failure["kind"] not in _RETRYABLE_FAILURE_KINDS
                or failure["retryable"] is not True
            ):
                raise ReviewedCoachingRecoveryError(
                    "later M26 attempt requires a retryable M24 failure"
                )

        attempts.append(
            {
                "attempt_number": attempt_number,
                "provider": _execution_summary(
                    provider,
                    target_record=target["target_records"][_PROVIDER_ROLE],
                ),
                "evaluator": (
                    None
                    if evaluator is None
                    else _execution_summary(
                        evaluator,
                        target_record=target["target_records"][_EVALUATOR_ROLE],
                    )
                ),
                "outcome": outcome,
                "failure_role": failure_role,
            }
        )

    target_attempt = target["target_attempt"]
    final = attempts[-1]
    if latest == target_attempt:
        if final["outcome"] != "succeeded":
            raise ReviewedCoachingRecoveryError(
                "persisted target attempt must end in successful completion"
            )
        if final["provider"]["matched_target_execution"] is not True:
            raise ReviewedCoachingRecoveryError(
                "final provider execution does not match persisted M26 target"
            )
        if _EVALUATOR_ROLE in target["roles"]:
            evaluator_summary = final["evaluator"]
            if (
                evaluator_summary is None
                or evaluator_summary["matched_target_execution"] is not True
            ):
                raise ReviewedCoachingRecoveryError(
                    "final evaluator execution does not match persisted M26 target"
                )
        reconciliation = {
            "state": "complete",
            "latest_observed_attempt": latest,
            "target_attempt_number": target_attempt,
            "next_attempt_number": None,
            "restart_scope": "none",
            "requires_manual_external_authority": False,
            "automatic_retry": False,
            "target_completion_already_persisted": True,
            "external_side_effect_idempotency_established": False,
        }
        return attempts, reconciliation

    if latest != target_attempt - 1:
        raise ReviewedCoachingRecoveryError(
            "recovery history must end immediately before the persisted target attempt"
        )
    if final["outcome"] != "failed":
        raise ReviewedCoachingRecoveryError(
            "incomplete recovery history must end in an M24 failure"
        )
    failure_role = final["failure_role"]
    assert failure_role is not None
    failure_record = (
        by_role[failure_role][latest]
        if failure_role in by_role
        else None
    )
    if failure_record is None:
        raise ReviewedCoachingRecoveryError("recovery failure source is missing")
    failure = failure_record["failure"]
    assert isinstance(failure, dict)
    if (
        failure["kind"] not in _RETRYABLE_FAILURE_KINDS
        or failure["retryable"] is not True
    ):
        raise ReviewedCoachingRecoveryError(
            "recovery cannot advance after a permanent or non-retryable M24 failure"
        )
    reconciliation = {
        "state": "resume_eligible",
        "latest_observed_attempt": latest,
        "target_attempt_number": target_attempt,
        "next_attempt_number": target_attempt,
        "restart_scope": "full_m26_orchestration",
        "requires_manual_external_authority": True,
        "automatic_retry": False,
        "target_completion_already_persisted": True,
        "external_side_effect_idempotency_established": False,
    }
    return attempts, reconciliation


def _source_refs(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "m26_run": target["run_ref"].to_dict(),
        "m27_ledger": target["ledger_ref"].to_dict(),
        "m25_review": target["review_ref"].to_dict(),
        "m24_executions": [
            target["target_refs"][role].to_dict() for role in target["roles"]
        ],
    }


def _source_fingerprints(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "m26_run_fingerprint": target["run_fingerprint"],
        "m27_ledger_fingerprint": target["ledger_fingerprint"],
        "m25_review_fingerprint": target["review_fingerprint"],
        "m19_model_coaching_fingerprint": target["model_coaching_fingerprint"],
        "m20_model_evaluation_fingerprint": target["model_evaluation_fingerprint"],
    }


def _target_summary(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_number": target["target_attempt"],
        "roles": list(target["roles"]),
        "execution_fingerprints": {
            role: target["target_records"][role]["fingerprint"]
            for role in target["roles"]
        },
        "completed_run": True,
    }


def _plan_payload(
    *,
    participant_id: str,
    target: dict[str, Any],
    history: list[dict[str, Any]],
    reconciliation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": M34_SCHEMA_VERSION,
        "participant_id": participant_id,
        "claim_scope": M34_CLAIM_SCOPE,
        "plan_mode": M34_PLAN_MODE,
        "source_refs": _source_refs(target),
        "source_fingerprints": _source_fingerprints(target),
        "target": _target_summary(target),
        "history": history,
        "history_fingerprint": _fingerprint(history),
        "reconciliation": reconciliation,
        "hermetic_contract": dict(_HERMETIC_CONTRACT),
        "authority_boundary": dict(_M34_AUTHORITY),
    }


def _artifact_ref(
    value: Any,
    *,
    participant_id: str,
    kind: str,
    label: str,
) -> ArtifactRef:
    if type(value) is not dict:
        raise ReviewedCoachingRecoveryError(f"{label} reference is malformed")
    try:
        ref = ArtifactRef(**value)
    except (TypeError, ValueError, StorageError) as exc:
        raise ReviewedCoachingRecoveryError(f"{label} reference is invalid") from exc
    if ref.kind != kind:
        raise ReviewedCoachingRecoveryError(f"{label} reference kind drifted")
    if ref.participant_id != participant_id:
        raise ReviewedCoachingRecoveryError(f"{label} participant scope drifted")
    return ref


def _validate_summary(value: Any, *, role: str, attempt_number: int) -> dict[str, Any]:
    summary = _strict(value, _SUMMARY_KEYS, f"M34 {role} history summary")
    if summary["role"] != role or summary["attempt_number"] != attempt_number:
        raise ReviewedCoachingRecoveryError("M34 history summary identity drifted")
    if type(summary["matched_target_execution"]) is not bool:
        raise ReviewedCoachingRecoveryError("M34 target-match flag must be boolean")
    if summary["status"] == "succeeded":
        if summary["failure_kind"] is not None or summary["retryable"] is not None:
            raise ReviewedCoachingRecoveryError(
                "M34 successful history summary cannot retain failure metadata"
            )
    elif summary["status"] == "failed":
        if summary["failure_kind"] not in _FAILURE_KINDS:
            raise ReviewedCoachingRecoveryError("M34 failure kind drifted")
        expected = summary["failure_kind"] in _RETRYABLE_FAILURE_KINDS
        if summary["retryable"] is not expected:
            raise ReviewedCoachingRecoveryError("M34 retryability summary drifted")
        if summary["matched_target_execution"] is True:
            raise ReviewedCoachingRecoveryError(
                "M34 failed execution cannot match successful target"
            )
    else:
        raise ReviewedCoachingRecoveryError("M34 history status drifted")
    return summary


def validate_reviewed_coaching_recovery_plan(value: Any) -> dict[str, Any]:
    """Validate one detached M34 plan without granting retry authority."""
    plan = _strict(value, _PLAN_KEYS, "M34 recovery plan")
    if plan["schema_version"] != M34_SCHEMA_VERSION:
        raise ReviewedCoachingRecoveryError("M34 schema drifted")
    participant_id = _nonempty(plan["participant_id"], "M34 participant_id")
    if plan["claim_scope"] != M34_CLAIM_SCOPE:
        raise ReviewedCoachingRecoveryError("M34 claim scope drifted")
    if plan["plan_mode"] != M34_PLAN_MODE:
        raise ReviewedCoachingRecoveryError("M34 plan mode drifted")
    if plan["hermetic_contract"] != _HERMETIC_CONTRACT:
        raise ReviewedCoachingRecoveryError("M34 hermetic contract drifted")
    if plan["authority_boundary"] != _M34_AUTHORITY:
        raise ReviewedCoachingRecoveryError("M34 authority boundary drifted")

    refs = _strict(
        plan["source_refs"],
        {"m26_run", "m27_ledger", "m25_review", "m24_executions"},
        "M34 source refs",
    )
    _artifact_ref(
        refs["m26_run"],
        participant_id=participant_id,
        kind=M26_SCHEMA_VERSION,
        label="M34 M26 run",
    )
    _artifact_ref(
        refs["m27_ledger"],
        participant_id=participant_id,
        kind=M27_SCHEMA_VERSION,
        label="M34 M27 ledger",
    )
    _artifact_ref(
        refs["m25_review"],
        participant_id=participant_id,
        kind=COACH_REVIEW_SCHEMA_VERSION,
        label="M34 M25 review",
    )
    if type(refs["m24_executions"]) is not list:
        raise ReviewedCoachingRecoveryError("M34 M24 execution refs must be an array")
    for index, ref in enumerate(refs["m24_executions"]):
        _artifact_ref(
            ref,
            participant_id=participant_id,
            kind=EXECUTION_SCHEMA_VERSION,
            label=f"M34 M24 execution {index}",
        )

    fingerprints = _strict(
        plan["source_fingerprints"],
        _SOURCE_FINGERPRINT_KEYS,
        "M34 source fingerprints",
    )
    for key in (
        "m26_run_fingerprint",
        "m27_ledger_fingerprint",
        "m25_review_fingerprint",
    ):
        _sha256(fingerprints[key], f"M34 {key}")
    for key in (
        "m19_model_coaching_fingerprint",
        "m20_model_evaluation_fingerprint",
    ):
        if fingerprints[key] is not None:
            _sha256(fingerprints[key], f"M34 {key}")

    target = _strict(
        plan["target"],
        {"attempt_number", "roles", "execution_fingerprints", "completed_run"},
        "M34 target",
    )
    roles = target["roles"]
    if type(roles) is not list or tuple(roles) not in ((), (_PROVIDER_ROLE,), _EXECUTION_ROLES):
        raise ReviewedCoachingRecoveryError("M34 target roles drifted")
    if target["completed_run"] is not True:
        raise ReviewedCoachingRecoveryError("M34 target must be a completed M26 run")
    if type(target["attempt_number"]) is not int or target["attempt_number"] < 0:
        raise ReviewedCoachingRecoveryError("M34 target attempt number is invalid")
    if bool(roles) != (target["attempt_number"] > 0):
        raise ReviewedCoachingRecoveryError("M34 target attempt/role optionality drifted")
    execution_fingerprints = target["execution_fingerprints"]
    if type(execution_fingerprints) is not dict or set(execution_fingerprints) != set(roles):
        raise ReviewedCoachingRecoveryError("M34 target execution fingerprints drifted")
    for role in roles:
        _sha256(execution_fingerprints[role], f"M34 {role} target fingerprint")
    if len(refs["m24_executions"]) != len(roles):
        raise ReviewedCoachingRecoveryError("M34 target execution ref count drifted")
    if roles == [] and (
        fingerprints["m19_model_coaching_fingerprint"] is not None
        or fingerprints["m20_model_evaluation_fingerprint"] is not None
    ):
        raise ReviewedCoachingRecoveryError("M34 deterministic optionality drifted")
    if roles == [_PROVIDER_ROLE] and (
        fingerprints["m19_model_coaching_fingerprint"] is None
        or fingerprints["m20_model_evaluation_fingerprint"] is not None
    ):
        raise ReviewedCoachingRecoveryError("M34 provider-only optionality drifted")
    if roles == list(_EXECUTION_ROLES) and (
        fingerprints["m19_model_coaching_fingerprint"] is None
        or fingerprints["m20_model_evaluation_fingerprint"] is None
    ):
        raise ReviewedCoachingRecoveryError("M34 model optionality drifted")

    history = plan["history"]
    if type(history) is not list:
        raise ReviewedCoachingRecoveryError("M34 history must be an array")
    if plan["history_fingerprint"] != _fingerprint(history):
        raise ReviewedCoachingRecoveryError("M34 history fingerprint mismatch")
    if not roles:
        if history:
            raise ReviewedCoachingRecoveryError("M34 deterministic history must be empty")
    else:
        if not history:
            raise ReviewedCoachingRecoveryError("M34 external history must not be empty")
        expected_attempts = list(range(1, len(history) + 1))
        actual_attempts = [item.get("attempt_number") for item in history if type(item) is dict]
        if actual_attempts != expected_attempts:
            raise ReviewedCoachingRecoveryError("M34 history attempts must be contiguous")
        for index, item in enumerate(history, start=1):
            attempt = _strict(item, _ATTEMPT_KEYS, f"M34 attempt {index}")
            provider = _validate_summary(
                attempt["provider"],
                role=_PROVIDER_ROLE,
                attempt_number=index,
            )
            evaluator = attempt["evaluator"]
            failure_summary = None
            failure_role = attempt["failure_role"]
            if provider["status"] == "failed":
                if evaluator is not None or failure_role != _PROVIDER_ROLE:
                    raise ReviewedCoachingRecoveryError(
                        "M34 failed provider attempt structure drifted"
                    )
                failure_summary = provider
                expected_outcome = "failed"
            elif _EVALUATOR_ROLE in roles:
                if evaluator is None:
                    raise ReviewedCoachingRecoveryError(
                        "M34 provider success requires evaluator summary"
                    )
                evaluator = _validate_summary(
                    evaluator,
                    role=_EVALUATOR_ROLE,
                    attempt_number=index,
                )
                if evaluator["status"] == "failed":
                    if failure_role != _EVALUATOR_ROLE:
                        raise ReviewedCoachingRecoveryError(
                            "M34 evaluator failure role drifted"
                        )
                    failure_summary = evaluator
                    expected_outcome = "failed"
                else:
                    if failure_role is not None:
                        raise ReviewedCoachingRecoveryError(
                            "M34 successful attempt cannot retain failure role"
                        )
                    expected_outcome = "succeeded"
            else:
                if evaluator is not None or failure_role is not None:
                    raise ReviewedCoachingRecoveryError(
                        "M34 provider-only attempt structure drifted"
                    )
                expected_outcome = "succeeded"
            if attempt["outcome"] != expected_outcome:
                raise ReviewedCoachingRecoveryError("M34 attempt outcome drifted")
            if index < len(history):
                if failure_summary is None or failure_summary["retryable"] is not True:
                    raise ReviewedCoachingRecoveryError(
                        "M34 later attempt lacks retryable prior failure"
                    )

    reconciliation = _strict(
        plan["reconciliation"],
        _RECONCILIATION_KEYS,
        "M34 reconciliation",
    )
    if reconciliation["target_attempt_number"] != target["attempt_number"]:
        raise ReviewedCoachingRecoveryError("M34 target attempt reconciliation drifted")
    if reconciliation["automatic_retry"] is not False:
        raise ReviewedCoachingRecoveryError("M34 cannot grant automatic retry")
    if reconciliation["target_completion_already_persisted"] is not True:
        raise ReviewedCoachingRecoveryError("M34 persisted-target marker drifted")
    if reconciliation["external_side_effect_idempotency_established"] is not False:
        raise ReviewedCoachingRecoveryError(
            "M34 cannot establish external side-effect idempotency"
        )
    latest = 0 if not history else history[-1]["attempt_number"]
    if reconciliation["latest_observed_attempt"] != latest:
        raise ReviewedCoachingRecoveryError("M34 latest attempt drifted")
    if reconciliation["state"] == "complete":
        if latest != target["attempt_number"]:
            raise ReviewedCoachingRecoveryError("M34 complete state attempt drifted")
        if reconciliation["next_attempt_number"] is not None:
            raise ReviewedCoachingRecoveryError("M34 complete state cannot have next attempt")
        if reconciliation["restart_scope"] != "none":
            raise ReviewedCoachingRecoveryError("M34 complete restart scope drifted")
        if reconciliation["requires_manual_external_authority"] is not False:
            raise ReviewedCoachingRecoveryError("M34 complete authority marker drifted")
        if history:
            final = history[-1]
            if final["outcome"] != "succeeded":
                raise ReviewedCoachingRecoveryError("M34 complete history must succeed")
            if final["provider"]["matched_target_execution"] is not True:
                raise ReviewedCoachingRecoveryError("M34 final provider target match drifted")
            if _EVALUATOR_ROLE in roles and (
                final["evaluator"] is None
                or final["evaluator"]["matched_target_execution"] is not True
            ):
                raise ReviewedCoachingRecoveryError("M34 final evaluator target match drifted")
    elif reconciliation["state"] == "resume_eligible":
        if latest != target["attempt_number"] - 1:
            raise ReviewedCoachingRecoveryError("M34 resume attempt drifted")
        if reconciliation["next_attempt_number"] != target["attempt_number"]:
            raise ReviewedCoachingRecoveryError("M34 next attempt drifted")
        if reconciliation["restart_scope"] != "full_m26_orchestration":
            raise ReviewedCoachingRecoveryError("M34 restart scope drifted")
        if reconciliation["requires_manual_external_authority"] is not True:
            raise ReviewedCoachingRecoveryError("M34 resume authority marker drifted")
        if not history or history[-1]["outcome"] != "failed":
            raise ReviewedCoachingRecoveryError("M34 resume history must end failed")
        failure_role = history[-1]["failure_role"]
        failure_summary = history[-1][
            "provider" if failure_role == _PROVIDER_ROLE else "evaluator"
        ]
        if failure_summary is None or failure_summary["retryable"] is not True:
            raise ReviewedCoachingRecoveryError("M34 resume requires retryable failure")
    else:
        raise ReviewedCoachingRecoveryError("M34 reconciliation state drifted")

    payload = {
        key: item
        for key, item in plan.items()
        if key not in {"recovery_plan_id", "fingerprint"}
    }
    expected_fingerprint = _fingerprint(payload)
    if plan["fingerprint"] != expected_fingerprint:
        raise ReviewedCoachingRecoveryError("M34 recovery-plan fingerprint mismatch")
    if plan["recovery_plan_id"] != f"reviewed_coaching_recovery_{expected_fingerprint[:20]}":
        raise ReviewedCoachingRecoveryError("M34 recovery-plan identity mismatch")
    return copy.deepcopy(plan)


def build_reviewed_coaching_recovery_reconciliation(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    run_artifact_id: str,
    attempt_histories: Mapping[str, Sequence[dict[str, Any]]],
    max_attempts: int = 3,
) -> ReviewedCoachingRecoveryResult:
    """Build and persist one dry-run M34 plan without executing external work."""
    _nonempty(participant_id, "participant_id")
    _nonempty(run_artifact_id, "run_artifact_id")
    if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
        raise ReviewedCoachingRecoveryError(
            "max_attempts must be an integer from 1 through 10"
        )
    target = _target_context(
        store,
        participant_id=participant_id,
        run_artifact_id=run_artifact_id,
    )
    if target["target_attempt"] > max_attempts:
        raise ReviewedCoachingRecoveryError(
            "persisted target attempt exceeds the declared recovery budget"
        )
    histories = _normalize_histories(attempt_histories, target=target)
    history, reconciliation = _build_history(histories, target=target)
    payload = _plan_payload(
        participant_id=participant_id,
        target=target,
        history=history,
        reconciliation=reconciliation,
    )
    fingerprint = _fingerprint(payload)
    plan = {
        **payload,
        "recovery_plan_id": f"reviewed_coaching_recovery_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }
    validated = validate_reviewed_coaching_recovery_plan(plan)
    write = ArtifactWrite(
        M34_SCHEMA_VERSION,
        validated["recovery_plan_id"],
        participant_id,
        validated,
        (target["run_ref"], target["ledger_ref"]),
    )
    plan_ref = prepare_artifact(write)[0]
    store.put_many((write,))
    return ReviewedCoachingRecoveryResult(
        plan=validated,
        plan_ref=plan_ref,
        run_ref=target["run_ref"],
        ledger_ref=target["ledger_ref"],
    )


def validate_persisted_reviewed_coaching_recovery_plan(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    plan: Any,
) -> dict[str, Any]:
    """Reconcile M34 source identities/fingerprints against current persisted roots."""
    validated = validate_reviewed_coaching_recovery_plan(plan)
    if validated["participant_id"] != participant_id:
        raise ReviewedCoachingRecoveryError(
            "M34 requested participant does not match recovery plan"
        )
    run_ref = ArtifactRef(**validated["source_refs"]["m26_run"])
    target = _target_context(
        store,
        participant_id=participant_id,
        run_artifact_id=run_ref.artifact_id,
    )
    expected_refs = _source_refs(target)
    expected_fingerprints = _source_fingerprints(target)
    expected_target = _target_summary(target)
    if validated["source_refs"] != expected_refs:
        raise ReviewedCoachingRecoveryError(
            "M34 source references drifted from persisted M26/M27 target"
        )
    if validated["source_fingerprints"] != expected_fingerprints:
        raise ReviewedCoachingRecoveryError(
            "M34 source fingerprints drifted from persisted review/evaluation target"
        )
    if validated["target"] != expected_target:
        raise ReviewedCoachingRecoveryError(
            "M34 target execution identity drifted from persisted M26"
        )
    return validated
