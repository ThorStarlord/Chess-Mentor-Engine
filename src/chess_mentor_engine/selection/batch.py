"""M4D deterministic bounded candidate-batch construction."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json

from .model import DiagnosticCandidate, SelectionPolicyIdentity, SelectionSignalKind
from .policy import PolicySelectionResult, SelectionPolicy, SelectionQuota


@dataclass(frozen=True, slots=True)
class BatchExclusion:
    position_id: str
    game_id: str
    comparison_id: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "comparison_id": self.comparison_id,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class QuotaOutcome:
    signal_kind: SelectionSignalKind
    minimum: int
    maximum: int | None
    selected_count: int
    shortfall: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_kind": self.signal_kind,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "selected_count": self.selected_count,
            "shortfall": self.shortfall,
        }


@dataclass(frozen=True, slots=True)
class DiagnosticCandidateBatch:
    batch_id: str
    selection_policy: SelectionPolicyIdentity
    policy_fingerprint: str
    requested_size: int
    actual_size: int
    candidates: tuple[DiagnosticCandidate, ...]
    control_candidate_ids: tuple[str, ...]
    source_pool_count: int
    source_candidate_ids: tuple[str, ...]
    source_pool_fingerprint: str
    quota_outcomes: tuple[QuotaOutcome, ...]
    exclusions: tuple[BatchExclusion, ...]
    shortfall: int
    control_shortfall: int

    def __post_init__(self) -> None:
        if not self.batch_id:
            raise ValueError("batch_id must not be empty")
        if self.requested_size <= 0:
            raise ValueError("requested_size must be positive")
        if self.actual_size != len(self.candidates):
            raise ValueError("actual_size must equal candidate count")
        if self.actual_size > self.requested_size:
            raise ValueError("actual_size must not exceed requested_size")
        if self.shortfall != self.requested_size - self.actual_size:
            raise ValueError("shortfall must equal requested_size - actual_size")
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("batch candidates must be unique")
        if not set(self.control_candidate_ids).issubset(candidate_ids):
            raise ValueError("control_candidate_ids must reference selected candidates")
        if len(set(self.source_candidate_ids)) != len(self.source_candidate_ids):
            raise ValueError("source_candidate_ids must be unique")

    def to_dict(self, *, include_batch_id: bool = True) -> dict[str, Any]:
        payload = {
            "selection_policy": self.selection_policy.to_dict(),
            "policy_fingerprint": self.policy_fingerprint,
            "requested_size": self.requested_size,
            "actual_size": self.actual_size,
            "candidates": [item.to_dict() for item in self.candidates],
            "control_candidate_ids": list(self.control_candidate_ids),
            "source_pool_count": self.source_pool_count,
            "source_candidate_ids": list(self.source_candidate_ids),
            "source_pool_fingerprint": self.source_pool_fingerprint,
            "quota_outcomes": [item.to_dict() for item in self.quota_outcomes],
            "exclusions": [item.to_dict() for item in self.exclusions],
            "shortfall": self.shortfall,
            "control_shortfall": self.control_shortfall,
        }
        if include_batch_id:
            payload["batch_id"] = self.batch_id
        return payload


class DiagnosticCandidateBatchError(ValueError):
    """Raised when M4D policy results cannot form one reproducible batch."""


def build_diagnostic_candidate_batch(
    *,
    results: tuple[PolicySelectionResult, ...],
    policy: SelectionPolicy,
) -> DiagnosticCandidateBatch:
    """Construct a bounded reproducible batch without weakening policy eligibility."""
    if not results:
        raise DiagnosticCandidateBatchError("batch source pool must not be empty")
    _validate_results(results, policy)

    ordered_results = tuple(sorted(results, key=_result_key))
    eligible = tuple(item for item in ordered_results if item.candidate is not None)
    source_candidate_ids = tuple(
        item.candidate.candidate_id for item in eligible if item.candidate is not None
    )
    source_pool_payload = [item.to_dict() for item in ordered_results]
    source_pool_fingerprint = _fingerprint(source_pool_payload)

    selected: list[PolicySelectionResult] = []
    selected_ids: set[str] = set()
    game_counts: dict[str, int] = {}

    controls = tuple(item for item in eligible if item.decision.role == "control")
    _select_until(
        pool=controls,
        selected=selected,
        selected_ids=selected_ids,
        game_counts=game_counts,
        target=min(policy.minimum_controls, policy.requested_size),
        policy=policy,
        required_kind=None,
    )

    for quota in sorted(policy.quotas, key=lambda item: item.signal_kind):
        current = _count_kind(selected, quota.signal_kind)
        if current >= quota.minimum:
            continue
        _select_until(
            pool=eligible,
            selected=selected,
            selected_ids=selected_ids,
            game_counts=game_counts,
            target=quota.minimum,
            policy=policy,
            required_kind=quota.signal_kind,
        )

    for item in eligible:
        if len(selected) >= policy.requested_size:
            break
        _try_add(
            item=item,
            selected=selected,
            selected_ids=selected_ids,
            game_counts=game_counts,
            policy=policy,
        )

    selected_tuple = tuple(selected)
    selected_candidate_ids = {
        item.candidate.candidate_id
        for item in selected_tuple
        if item.candidate is not None
    }
    candidates = tuple(
        item.candidate for item in selected_tuple if item.candidate is not None
    )
    controls_selected = tuple(
        item.candidate.candidate_id
        for item in selected_tuple
        if item.candidate is not None and item.decision.role == "control"
    )

    quota_outcomes = tuple(
        _quota_outcome(quota, selected_tuple)
        for quota in sorted(policy.quotas, key=lambda item: item.signal_kind)
    )
    control_shortfall = max(0, policy.minimum_controls - len(controls_selected))
    shortfall = policy.requested_size - len(candidates)

    exclusions: list[BatchExclusion] = []
    for item in ordered_results:
        if item.candidate is None:
            exclusions.append(
                BatchExclusion(
                    position_id=item.decision.position_id,
                    game_id=item.decision.game_id,
                    comparison_id=item.decision.comparison_id,
                    reasons=item.decision.exclusion_reasons,
                )
            )
            continue
        if item.candidate.candidate_id in selected_candidate_ids:
            continue
        exclusions.append(
            BatchExclusion(
                position_id=item.decision.position_id,
                game_id=item.decision.game_id,
                comparison_id=item.decision.comparison_id,
                reasons=_nonselection_reasons(item, selected_tuple, policy),
            )
        )

    payload = {
        "selection_policy": policy.identity.to_dict(),
        "policy_fingerprint": policy.fingerprint,
        "requested_size": policy.requested_size,
        "candidate_ids": [item.candidate_id for item in candidates],
        "control_candidate_ids": list(controls_selected),
        "source_candidate_ids": list(source_candidate_ids),
        "source_pool_fingerprint": source_pool_fingerprint,
        "quota_outcomes": [item.to_dict() for item in quota_outcomes],
        "exclusions": [item.to_dict() for item in exclusions],
        "shortfall": shortfall,
        "control_shortfall": control_shortfall,
    }
    batch_id = f"batch_{_fingerprint(payload)[:20]}"
    return DiagnosticCandidateBatch(
        batch_id=batch_id,
        selection_policy=policy.identity,
        policy_fingerprint=policy.fingerprint,
        requested_size=policy.requested_size,
        actual_size=len(candidates),
        candidates=candidates,
        control_candidate_ids=controls_selected,
        source_pool_count=len(ordered_results),
        source_candidate_ids=source_candidate_ids,
        source_pool_fingerprint=source_pool_fingerprint,
        quota_outcomes=quota_outcomes,
        exclusions=tuple(exclusions),
        shortfall=shortfall,
        control_shortfall=control_shortfall,
    )


def _validate_results(
    results: tuple[PolicySelectionResult, ...],
    policy: SelectionPolicy,
) -> None:
    comparison_ids: list[str] = []
    for item in results:
        decision = item.decision
        comparison_ids.append(decision.comparison_id)
        if decision.policy != policy.identity:
            raise DiagnosticCandidateBatchError("selection decision policy mismatch")
        if decision.policy_fingerprint != policy.fingerprint:
            raise DiagnosticCandidateBatchError(
                "selection decision policy fingerprint mismatch"
            )
        if decision.eligible != (item.candidate is not None):
            raise DiagnosticCandidateBatchError(
                "candidate presence must match policy eligibility"
            )
        if item.candidate is not None:
            if item.candidate.selection_policy != policy.identity:
                raise DiagnosticCandidateBatchError(
                    "candidate policy identity mismatch"
                )
            if item.candidate.comparison_id != decision.comparison_id:
                raise DiagnosticCandidateBatchError("candidate comparison mismatch")
    if len(set(comparison_ids)) != len(comparison_ids):
        raise DiagnosticCandidateBatchError("source pool decisions must be unique")


def _select_until(
    *,
    pool: tuple[PolicySelectionResult, ...],
    selected: list[PolicySelectionResult],
    selected_ids: set[str],
    game_counts: dict[str, int],
    target: int,
    policy: SelectionPolicy,
    required_kind: SelectionSignalKind | None,
) -> None:
    for item in pool:
        if len(selected) >= policy.requested_size:
            return
        if required_kind is not None and _count_kind(selected, required_kind) >= target:
            return
        if required_kind is None and len(
            [entry for entry in selected if entry.decision.role == "control"]
        ) >= target:
            return
        if required_kind is not None and not _has_kind(item, required_kind):
            continue
        _try_add(
            item=item,
            selected=selected,
            selected_ids=selected_ids,
            game_counts=game_counts,
            policy=policy,
        )


def _try_add(
    *,
    item: PolicySelectionResult,
    selected: list[PolicySelectionResult],
    selected_ids: set[str],
    game_counts: dict[str, int],
    policy: SelectionPolicy,
) -> bool:
    candidate = item.candidate
    if candidate is None or candidate.candidate_id in selected_ids:
        return False
    if len(selected) >= policy.requested_size:
        return False
    if (
        policy.maximum_per_game is not None
        and game_counts.get(candidate.game_id, 0) >= policy.maximum_per_game
    ):
        return False
    for quota in policy.quotas:
        if quota.maximum is None or not _has_kind(item, quota.signal_kind):
            continue
        if _count_kind(selected, quota.signal_kind) >= quota.maximum:
            return False

    selected.append(item)
    selected_ids.add(candidate.candidate_id)
    game_counts[candidate.game_id] = game_counts.get(candidate.game_id, 0) + 1
    return True


def _quota_outcome(
    quota: SelectionQuota,
    selected: tuple[PolicySelectionResult, ...],
) -> QuotaOutcome:
    count = _count_kind(selected, quota.signal_kind)
    return QuotaOutcome(
        signal_kind=quota.signal_kind,
        minimum=quota.minimum,
        maximum=quota.maximum,
        selected_count=count,
        shortfall=max(0, quota.minimum - count),
    )


def _count_kind(
    selected: tuple[PolicySelectionResult, ...] | list[PolicySelectionResult],
    kind: SelectionSignalKind,
) -> int:
    return sum(1 for item in selected if _has_kind(item, kind))


def _has_kind(item: PolicySelectionResult, kind: SelectionSignalKind) -> bool:
    candidate = item.candidate
    return candidate is not None and any(
        signal.kind == kind for signal in candidate.signals
    )


def _nonselection_reasons(
    item: PolicySelectionResult,
    selected: tuple[PolicySelectionResult, ...],
    policy: SelectionPolicy,
) -> tuple[str, ...]:
    candidate = item.candidate
    if candidate is None:
        return item.decision.exclusion_reasons
    if len(selected) >= policy.requested_size:
        return ("batch_capacity",)
    if policy.maximum_per_game is not None:
        game_count = sum(
            1
            for entry in selected
            if entry.candidate is not None
            and entry.candidate.game_id == candidate.game_id
        )
        if game_count >= policy.maximum_per_game:
            return ("maximum_per_game",)
    for quota in policy.quotas:
        if quota.maximum is None or not _has_kind(item, quota.signal_kind):
            continue
        if _count_kind(selected, quota.signal_kind) >= quota.maximum:
            return (f"quota_maximum:{quota.signal_kind}",)
    return ("not_selected_under_deterministic_order",)


def _result_key(item: PolicySelectionResult) -> tuple[str, int, str]:
    candidate = item.candidate
    if candidate is None:
        return (
            item.decision.game_id,
            10**9,
            item.decision.comparison_id,
        )
    return (
        candidate.game_id,
        candidate.provenance.root_ply_index,
        candidate.candidate_id,
    )


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
