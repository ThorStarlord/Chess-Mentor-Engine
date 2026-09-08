"""M4D deterministic selection-policy evaluation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json

from .candidate import record_diagnostic_candidate
from .model import (
    DecisionComparison,
    DiagnosticCandidate,
    SelectionPolicyIdentity,
    SelectionSignal,
    SelectionSignalKind,
)

SelectionRole: TypeAlias = Literal["candidate", "control", "excluded"]


@dataclass(frozen=True, slots=True)
class SelectionQuota:
    """Versioned batch constraint over one objective M4C signal kind."""

    signal_kind: SelectionSignalKind
    minimum: int = 0
    maximum: int | None = None

    def __post_init__(self) -> None:
        if self.minimum < 0:
            raise ValueError("quota minimum must be non-negative")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError("quota maximum must be non-negative when provided")
        if self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("quota minimum must not exceed maximum")

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_kind": self.signal_kind,
            "minimum": self.minimum,
            "maximum": self.maximum,
        }


@dataclass(frozen=True, slots=True)
class SelectionPolicy:
    """Explicit deterministic M4D eligibility and batch policy."""

    policy_id: str
    version: str
    requested_size: int
    candidate_min_cp_delta: int | None = None
    control_max_cp_delta: int | None = 0
    close_choice_max_cp: int | None = None
    candidate_mate_relations: tuple[str, ...] = ()
    include_rank1_controls: bool = True
    excluded_signal_kinds: tuple[SelectionSignalKind, ...] = ()
    minimum_controls: int = 0
    maximum_per_game: int | None = None
    quotas: tuple[SelectionQuota, ...] = ()

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")
        if self.requested_size <= 0:
            raise ValueError("requested_size must be positive")
        for name, value in (
            ("candidate_min_cp_delta", self.candidate_min_cp_delta),
            ("control_max_cp_delta", self.control_max_cp_delta),
            ("close_choice_max_cp", self.close_choice_max_cp),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative when provided")
        if self.minimum_controls < 0:
            raise ValueError("minimum_controls must be non-negative")
        if self.minimum_controls > self.requested_size:
            raise ValueError("minimum_controls must not exceed requested_size")
        if self.maximum_per_game is not None and self.maximum_per_game <= 0:
            raise ValueError("maximum_per_game must be positive when provided")
        if len(set(self.excluded_signal_kinds)) != len(self.excluded_signal_kinds):
            raise ValueError("excluded_signal_kinds must be unique")
        quota_kinds = tuple(item.signal_kind for item in self.quotas)
        if len(set(quota_kinds)) != len(quota_kinds):
            raise ValueError("quota signal kinds must be unique")
        if len(set(self.candidate_mate_relations)) != len(
            self.candidate_mate_relations
        ):
            raise ValueError("candidate_mate_relations must be unique")

    @property
    def identity(self) -> SelectionPolicyIdentity:
        return SelectionPolicyIdentity(self.policy_id, self.version)

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "requested_size": self.requested_size,
            "candidate_min_cp_delta": self.candidate_min_cp_delta,
            "control_max_cp_delta": self.control_max_cp_delta,
            "close_choice_max_cp": self.close_choice_max_cp,
            "candidate_mate_relations": list(self.candidate_mate_relations),
            "include_rank1_controls": self.include_rank1_controls,
            "excluded_signal_kinds": list(self.excluded_signal_kinds),
            "minimum_controls": self.minimum_controls,
            "maximum_per_game": self.maximum_per_game,
            "quotas": [item.to_dict() for item in self.quotas],
        }


@dataclass(frozen=True, slots=True)
class SelectionRuleMatch:
    rule_id: str
    signal_id: str
    signal_kind: SelectionSignalKind
    observed_value: object
    operator: str
    threshold: object

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "signal_id": self.signal_id,
            "signal_kind": self.signal_kind,
            "observed_value": self.observed_value,
            "operator": self.operator,
            "threshold": self.threshold,
        }


@dataclass(frozen=True, slots=True)
class SelectionDecision:
    position_id: str
    game_id: str
    comparison_id: str
    policy: SelectionPolicyIdentity
    policy_fingerprint: str
    eligible: bool
    role: SelectionRole
    matches: tuple[SelectionRuleMatch, ...]
    eligibility_signal_ids: tuple[str, ...]
    exclusion_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.eligible and self.role == "excluded":
            raise ValueError("eligible selection decision cannot have excluded role")
        if not self.eligible and self.role != "excluded":
            raise ValueError("ineligible selection decision must have excluded role")
        if self.eligible and not self.eligibility_signal_ids:
            raise ValueError("eligible decision requires eligibility signals")
        if not self.eligible and not self.exclusion_reasons:
            raise ValueError("excluded decision requires an exclusion reason")

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "game_id": self.game_id,
            "comparison_id": self.comparison_id,
            "policy": self.policy.to_dict(),
            "policy_fingerprint": self.policy_fingerprint,
            "eligible": self.eligible,
            "role": self.role,
            "matches": [item.to_dict() for item in self.matches],
            "eligibility_signal_ids": list(self.eligibility_signal_ids),
            "exclusion_reasons": list(self.exclusion_reasons),
        }


@dataclass(frozen=True, slots=True)
class PolicySelectionResult:
    decision: SelectionDecision
    candidate: DiagnosticCandidate | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.to_dict(),
            "candidate": None if self.candidate is None else self.candidate.to_dict(),
        }


class SelectionPolicyError(ValueError):
    """Raised when policy inputs are inconsistent with one M4C decision."""


def apply_selection_policy(
    *,
    comparison: DecisionComparison,
    signals: tuple[SelectionSignal, ...],
    policy: SelectionPolicy,
) -> PolicySelectionResult:
    """Evaluate one M4C signal set and record a candidate only when eligible."""
    _validate_signal_set(comparison, signals)
    by_kind = _signals_by_kind(signals)

    excluded_hits = tuple(
        kind for kind in policy.excluded_signal_kinds if kind in by_kind
    )
    if excluded_hits:
        decision = _excluded_decision(
            comparison,
            policy,
            tuple(f"excluded_signal_kind:{kind}" for kind in excluded_hits),
        )
        return PolicySelectionResult(decision=decision, candidate=None)

    candidate_matches = _candidate_matches(by_kind, policy)
    control_matches = _control_matches(by_kind, policy)

    if candidate_matches:
        role: SelectionRole = "candidate"
        matches = candidate_matches
    elif control_matches:
        role = "control"
        matches = control_matches
    else:
        decision = _excluded_decision(
            comparison,
            policy,
            ("no_eligibility_rule_matched",),
        )
        return PolicySelectionResult(decision=decision, candidate=None)

    ordered_matches = tuple(
        sorted(matches, key=lambda item: (item.rule_id, item.signal_id))
    )
    eligibility_signal_ids = tuple(
        sorted({item.signal_id for item in ordered_matches})
    )
    decision = SelectionDecision(
        position_id=comparison.position_id,
        game_id=comparison.game_id,
        comparison_id=comparison.comparison_id,
        policy=policy.identity,
        policy_fingerprint=policy.fingerprint,
        eligible=True,
        role=role,
        matches=ordered_matches,
        eligibility_signal_ids=eligibility_signal_ids,
        exclusion_reasons=(),
    )
    candidate = record_diagnostic_candidate(
        comparison=comparison,
        signals=signals,
        selection_policy=policy.identity,
        eligibility_signal_ids=eligibility_signal_ids,
    )
    return PolicySelectionResult(decision=decision, candidate=candidate)


def _candidate_matches(
    by_kind: dict[SelectionSignalKind, tuple[SelectionSignal, ...]],
    policy: SelectionPolicy,
) -> tuple[SelectionRuleMatch, ...]:
    matches: list[SelectionRuleMatch] = []

    if policy.candidate_min_cp_delta is not None:
        for signal in by_kind.get("EXACT_CP_DELTA", ()):
            value = signal.raw_value
            if isinstance(value, int) and value >= policy.candidate_min_cp_delta:
                matches.append(
                    SelectionRuleMatch(
                        rule_id="candidate_min_cp_delta",
                        signal_id=signal.signal_id,
                        signal_kind=signal.kind,
                        observed_value=value,
                        operator=">=",
                        threshold=policy.candidate_min_cp_delta,
                    )
                )

    if policy.close_choice_max_cp is not None:
        for signal in by_kind.get("TOP_CANDIDATE_SEPARATION", ()):
            raw = signal.raw_value
            if not isinstance(raw, dict):
                continue
            value = raw.get("exact_centipawn_separation_for_mover")
            if isinstance(value, int) and 0 <= value <= policy.close_choice_max_cp:
                matches.append(
                    SelectionRuleMatch(
                        rule_id="multipv_close_choice",
                        signal_id=signal.signal_id,
                        signal_kind=signal.kind,
                        observed_value=value,
                        operator="<=",
                        threshold=policy.close_choice_max_cp,
                    )
                )

    accepted_mates = set(policy.candidate_mate_relations)
    if accepted_mates:
        for signal in by_kind.get("MATE_RELATION", ()):
            value = signal.raw_value
            if isinstance(value, str) and value in accepted_mates:
                matches.append(
                    SelectionRuleMatch(
                        rule_id="candidate_mate_relation",
                        signal_id=signal.signal_id,
                        signal_kind=signal.kind,
                        observed_value=value,
                        operator="in",
                        threshold=list(policy.candidate_mate_relations),
                    )
                )

    return tuple(matches)


def _control_matches(
    by_kind: dict[SelectionSignalKind, tuple[SelectionSignal, ...]],
    policy: SelectionPolicy,
) -> tuple[SelectionRuleMatch, ...]:
    matches: list[SelectionRuleMatch] = []

    if policy.include_rank1_controls:
        for signal in by_kind.get("PLAYED_EQUALS_RANK_1", ()):
            matches.append(
                SelectionRuleMatch(
                    rule_id="rank1_control",
                    signal_id=signal.signal_id,
                    signal_kind=signal.kind,
                    observed_value=signal.raw_value,
                    operator="present",
                    threshold=True,
                )
            )

    if policy.control_max_cp_delta is not None:
        for signal in by_kind.get("EXACT_CP_DELTA", ()):
            value = signal.raw_value
            if (
                isinstance(value, int)
                and 0 <= value <= policy.control_max_cp_delta
            ):
                matches.append(
                    SelectionRuleMatch(
                        rule_id="low_severity_control",
                        signal_id=signal.signal_id,
                        signal_kind=signal.kind,
                        observed_value=value,
                        operator="<=",
                        threshold=policy.control_max_cp_delta,
                    )
                )

    return tuple(matches)


def _signals_by_kind(
    signals: tuple[SelectionSignal, ...],
) -> dict[SelectionSignalKind, tuple[SelectionSignal, ...]]:
    grouped: dict[SelectionSignalKind, list[SelectionSignal]] = {}
    for signal in signals:
        grouped.setdefault(signal.kind, []).append(signal)
    return {
        kind: tuple(sorted(items, key=lambda item: item.signal_id))
        for kind, items in grouped.items()
    }


def _validate_signal_set(
    comparison: DecisionComparison,
    signals: tuple[SelectionSignal, ...],
) -> None:
    if not signals:
        raise SelectionPolicyError("selection policy requires at least one signal")
    signal_ids = tuple(signal.signal_id for signal in signals)
    if len(set(signal_ids)) != len(signal_ids):
        raise SelectionPolicyError("selection signals must be unique")
    for signal in signals:
        if signal.position_id != comparison.position_id:
            raise SelectionPolicyError("signal position_id mismatch")
        if signal.game_id != comparison.game_id:
            raise SelectionPolicyError("signal game_id mismatch")
        if signal.comparison_id != comparison.comparison_id:
            raise SelectionPolicyError("signal comparison_id mismatch")


def _excluded_decision(
    comparison: DecisionComparison,
    policy: SelectionPolicy,
    reasons: tuple[str, ...],
) -> SelectionDecision:
    return SelectionDecision(
        position_id=comparison.position_id,
        game_id=comparison.game_id,
        comparison_id=comparison.comparison_id,
        policy=policy.identity,
        policy_fingerprint=policy.fingerprint,
        eligible=False,
        role="excluded",
        matches=(),
        eligibility_signal_ids=(),
        exclusion_reasons=tuple(sorted(reasons)),
    )


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
