"""M40 deterministic teaching-priority and next-session proposal policy.

M40 ranks bounded next-action proposals over current M36/M39 evidence. It is a
versioned heuristic policy, not an empirically optimal tutor, and it performs no
learner-state, intervention, tutor-session, model, or provider mutation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import HypothesisRevisionRef
from chess_mentor_engine.longitudinal import (
    LearnerHypothesisReadEntry,
    LearnerStateReadModel,
)

from .evidence_synthesis import (
    EvidenceSynthesisReference,
    HypothesisEvidenceSynthesis,
)

NEXT_SESSION_PLAN_SCHEMA_VERSION = "m40.next-session-plan.v1"
NEXT_SESSION_POLICY_SCHEMA_VERSION = "m40.next-session-policy.v1"

NextSessionAction: TypeAlias = Literal[
    "COLLECT_NEW_EVIDENCE",
    "CHALLENGE_HYPOTHESIS",
    "PRESENT_CONTROL",
    "TEACH_CONCEPT",
    "ASSIGN_PRACTICE",
    "RUN_NEAR_TRANSFER_TEST",
    "RUN_FAR_TRANSFER_TEST",
    "WAIT_FOR_REAL_GAME_EVIDENCE",
]

_ACTIONS: tuple[NextSessionAction, ...] = (
    "COLLECT_NEW_EVIDENCE",
    "CHALLENGE_HYPOTHESIS",
    "PRESENT_CONTROL",
    "TEACH_CONCEPT",
    "ASSIGN_PRACTICE",
    "RUN_NEAR_TRANSFER_TEST",
    "RUN_FAR_TRANSFER_TEST",
    "WAIT_FOR_REAL_GAME_EVIDENCE",
)
_OUTCOME_KINDS = (
    "practice",
    "near_transfer",
    "far_transfer",
    "real_game_transfer",
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must not be empty")


def _timestamp(name: str, value: str) -> None:
    _nonempty(name, value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone offset")


@dataclass(frozen=True, slots=True)
class NextSessionPolicyRef:
    policy_id: str
    version: str
    fingerprint: str

    def __post_init__(self) -> None:
        _nonempty("policy_id", self.policy_id)
        _nonempty("version", self.version)
        _nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class NextSessionPolicy:
    policy_id: str
    version: str
    fingerprint: str
    action_priorities: tuple[tuple[NextSessionAction, int], ...]
    challenge_supported_without_counterevidence: bool
    challenge_supported_with_unresolved_alternatives: bool
    claim_scope: str = "transparent_heuristic_next_action_policy"
    schema_version: str = NEXT_SESSION_POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("policy_id", self.policy_id)
        _nonempty("version", self.version)
        _nonempty("fingerprint", self.fingerprint)
        if self.schema_version != NEXT_SESSION_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported M40 policy schema")
        actions = tuple(action for action, _ in self.action_priorities)
        if set(actions) != set(_ACTIONS) or len(actions) != len(_ACTIONS):
            raise ValueError("M40 policy must define each action exactly once")
        if any(priority < 0 for _, priority in self.action_priorities):
            raise ValueError("M40 action priorities must be non-negative")
        if self.claim_scope != "transparent_heuristic_next_action_policy":
            raise ValueError("unknown M40 policy claim scope")

    def priority_for(self, action: NextSessionAction) -> int:
        return dict(self.action_priorities)[action]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "action_priorities": [list(item) for item in self.action_priorities],
            "challenge_supported_without_counterevidence": (
                self.challenge_supported_without_counterevidence
            ),
            "challenge_supported_with_unresolved_alternatives": (
                self.challenge_supported_with_unresolved_alternatives
            ),
            "claim_scope": self.claim_scope,
        }

    @property
    def ref(self) -> NextSessionPolicyRef:
        return NextSessionPolicyRef(
            policy_id=self.policy_id,
            version=self.version,
            fingerprint=self.fingerprint,
        )


@dataclass(frozen=True, slots=True)
class NextSessionActionCandidate:
    hypothesis_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    m7_status: str | None
    action: NextSessionAction
    policy_priority: int
    reasons: tuple[str, ...]
    blocking_uncertainty: tuple[str, ...]
    synthesis_ref: EvidenceSynthesisReference | None
    concept_ids: tuple[str, ...]
    selected_intervention_ids: tuple[str, ...]
    outcome_statuses: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        _nonempty("hypothesis_id", self.hypothesis_id)
        if self.action not in _ACTIONS:
            raise ValueError("unknown M40 action")
        if self.policy_priority < 0:
            raise ValueError("M40 candidate priority must be non-negative")
        if not self.reasons or any(not item for item in self.reasons):
            raise ValueError("M40 action candidate requires reasons")
        for name, values in (
            ("blocking_uncertainty", self.blocking_uncertainty),
            ("concept_ids", self.concept_ids),
            ("selected_intervention_ids", self.selected_intervention_ids),
        ):
            if any(not item for item in values):
                raise ValueError(f"{name} values must not be empty")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} values must be unique")
        kinds = tuple(kind for kind, _ in self.outcome_statuses)
        if any(kind not in _OUTCOME_KINDS for kind in kinds):
            raise ValueError("unknown M40 outcome evidence kind")
        if len(set(kinds)) != len(kinds):
            raise ValueError("M40 outcome kinds must be unique")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "m7_status": self.m7_status,
            "action": self.action,
            "policy_priority": self.policy_priority,
            "reasons": list(self.reasons),
            "blocking_uncertainty": list(self.blocking_uncertainty),
            "synthesis_ref": (
                None if self.synthesis_ref is None else self.synthesis_ref.to_dict()
            ),
            "concept_ids": list(self.concept_ids),
            "selected_intervention_ids": list(self.selected_intervention_ids),
            "outcome_statuses": [list(item) for item in self.outcome_statuses],
        }


@dataclass(frozen=True, slots=True)
class NextSessionPlan:
    plan_id: str
    fingerprint: str
    participant_id: str
    learner_read_model_ref: EvidenceSynthesisReference
    policy_ref: NextSessionPolicyRef
    synthesis_refs: tuple[EvidenceSynthesisReference, ...]
    selected_candidate: NextSessionActionCandidate
    candidates: tuple[NextSessionActionCandidate, ...]
    created_at: str
    decision_authority: Literal["proposal_only"] = "proposal_only"
    claim_scope: str = "participant_specific_next_session_proposal"
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = NEXT_SESSION_PLAN_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("plan_id", self.plan_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("participant_id", self.participant_id)
        _timestamp("created_at", self.created_at)
        if self.schema_version != NEXT_SESSION_PLAN_SCHEMA_VERSION:
            raise ValueError("unsupported M40 plan schema")
        if not self.candidates:
            raise ValueError("M40 plan requires at least one action candidate")
        if self.candidates[0] != self.selected_candidate:
            raise ValueError("M40 selected candidate must be first in ranked candidates")
        keys = tuple(
            (item.hypothesis_id, item.hypothesis_revision_ref.revision_id)
            for item in self.candidates
        )
        if len(set(keys)) != len(keys):
            raise ValueError("M40 candidates must be unique per current hypothesis")
        ref_ids = tuple(item.ref_id for item in self.synthesis_refs)
        if len(set(ref_ids)) != len(ref_ids):
            raise ValueError("M40 synthesis refs must be unique")
        if self.decision_authority != "proposal_only":
            raise ValueError("M40 cannot grant execution authority")
        if self.claim_scope != "participant_specific_next_session_proposal":
            raise ValueError("unknown M40 plan claim scope")
        if self.causal_effect != "not_established" or self.mastery != "not_established":
            raise ValueError("M40 cannot establish causality or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "learner_read_model_ref": self.learner_read_model_ref.to_dict(),
            "policy_ref": self.policy_ref.to_dict(),
            "synthesis_refs": [item.to_dict() for item in self.synthesis_refs],
            "selected_candidate": self.selected_candidate.to_dict(),
            "candidates": [item.to_dict() for item in self.candidates],
            "created_at": self.created_at,
            "decision_authority": self.decision_authority,
            "claim_scope": self.claim_scope,
            "causal_effect": self.causal_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_default_next_session_policy() -> NextSessionPolicy:
    priorities: tuple[tuple[NextSessionAction, int], ...] = (
        ("PRESENT_CONTROL", 100),
        ("CHALLENGE_HYPOTHESIS", 95),
        ("RUN_FAR_TRANSFER_TEST", 90),
        ("RUN_NEAR_TRANSFER_TEST", 85),
        ("ASSIGN_PRACTICE", 80),
        ("TEACH_CONCEPT", 75),
        ("COLLECT_NEW_EVIDENCE", 70),
        ("WAIT_FOR_REAL_GAME_EVIDENCE", 60),
    )
    payload = {
        "schema_version": NEXT_SESSION_POLICY_SCHEMA_VERSION,
        "policy_id": "m40.default-next-session-policy",
        "version": "1",
        "action_priorities": [list(item) for item in priorities],
        "challenge_supported_without_counterevidence": True,
        "challenge_supported_with_unresolved_alternatives": True,
        "claim_scope": "transparent_heuristic_next_action_policy",
    }
    return NextSessionPolicy(
        policy_id=payload["policy_id"],
        version=payload["version"],
        fingerprint=_digest(payload),
        action_priorities=priorities,
        challenge_supported_without_counterevidence=True,
        challenge_supported_with_unresolved_alternatives=True,
    )


def validate_next_session_policy(policy: NextSessionPolicy) -> None:
    if _digest(policy.identity_payload()) != policy.fingerprint:
        raise ValueError("M40 next-session policy fingerprint mismatch")


def _read_model_ref(read_model: LearnerStateReadModel) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="learner_state_read_model",
        ref_id=read_model.read_model_id,
        fingerprint=read_model.fingerprint,
    )


def _synthesis_ref(
    synthesis: HypothesisEvidenceSynthesis,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="hypothesis_evidence_synthesis",
        ref_id=synthesis.synthesis_id,
        fingerprint=synthesis.fingerprint,
    )


def _outcome_statuses(entry: LearnerHypothesisReadEntry) -> tuple[tuple[str, str], ...]:
    return tuple((item.evidence_kind, item.status) for item in entry.outcome_dimensions)


def _outcome_status(entry: LearnerHypothesisReadEntry, kind: str) -> str | None:
    matches = tuple(
        item.status for item in entry.outcome_dimensions if item.evidence_kind == kind
    )
    if len(matches) > 1:
        raise ValueError("M40 read model contains duplicate outcome dimensions")
    return None if not matches else matches[0]


def _selected_intervention_ids(
    entry: LearnerHypothesisReadEntry,
) -> tuple[str, ...]:
    return tuple(
        sorted(item.intervention_id for item in entry.intervention.selected_interventions)
    )


def _validate_synthesis_for_entry(
    *,
    entry: LearnerHypothesisReadEntry,
    synthesis: HypothesisEvidenceSynthesis,
    read_model: LearnerStateReadModel,
) -> None:
    if synthesis.participant_id != read_model.participant_id:
        raise ValueError("M40 synthesis participant mismatch")
    if synthesis.hypothesis_revision_ref != entry.current_revision_ref:
        raise ValueError("M40 synthesis/current-revision mismatch")
    if synthesis.learner_read_model_ref != _read_model_ref(read_model):
        raise ValueError("M40 synthesis/read-model identity mismatch")
    if entry.m7_status != synthesis.hypothesis_assessment_status:
        raise ValueError("M40 synthesis/M36 M7 status mismatch")
    if entry.m7_assessment_ref is None:
        raise ValueError("M40 synthesis supplied for hypothesis without M7C assessment")
    if (
        synthesis.hypothesis_assessment_ref.ref_id != entry.m7_assessment_ref.ref_id
        or synthesis.hypothesis_assessment_ref.fingerprint
        != entry.m7_assessment_ref.fingerprint
    ):
        raise ValueError("M40 synthesis/M36 M7C assessment mismatch")


def _action_for_entry(
    *,
    entry: LearnerHypothesisReadEntry,
    synthesis: HypothesisEvidenceSynthesis | None,
    policy: NextSessionPolicy,
) -> NextSessionActionCandidate:
    status = entry.m7_status
    reasons: list[str] = []
    blocking: list[str] = []

    if status is None:
        action: NextSessionAction = "COLLECT_NEW_EVIDENCE"
        reasons.append("No current M7C assessment is present for this active hypothesis.")
        blocking.append("Current recurrence status is unavailable.")
    elif synthesis is None:
        raise ValueError("M40 requires M39 synthesis for every assessed active hypothesis")
    elif status == "contradicted":
        action = "PRESENT_CONTROL"
        reasons.append(
            "M7C currently classifies the hypothesis as contradicted; the next "
            "learner-facing action should foreground disconfirming evidence."
        )
        blocking.extend(synthesis.evidence_gaps)
    elif status == "unclear":
        action = "CHALLENGE_HYPOTHESIS"
        reasons.append(
            "M7C is unclear, so the next action should reduce uncertainty rather "
            "than teach from the hypothesis as established."
        )
        blocking.extend(synthesis.evidence_gaps)
    elif status in {"insufficient", "isolated", "candidate_recurrence"}:
        action = "COLLECT_NEW_EVIDENCE"
        reasons.append(
            f"M7C status {status!r} is below supported recurrence; collect more "
            "participant-specific evidence before teaching from the hypothesis."
        )
        blocking.extend(synthesis.evidence_gaps)
    elif status == "supported_recurrence":
        challenge_count = (
            synthesis.evidence_counts.contradiction_unit_count
            + synthesis.evidence_counts.successful_counterexample_unit_count
            + synthesis.evidence_counts.context_exception_unit_count
        )
        if (
            policy.challenge_supported_without_counterevidence
            and challenge_count == 0
        ):
            action = "CHALLENGE_HYPOTHESIS"
            reasons.append(
                "The hypothesis is supported by M7C but the current assessment has "
                "no contradiction, counterexample, or context-exception unit."
            )
            blocking.append("Counterevidence coverage is currently one-sided.")
        elif (
            policy.challenge_supported_with_unresolved_alternatives
            and entry.unresolved_alternative_notes
        ):
            action = "CHALLENGE_HYPOTHESIS"
            reasons.append(
                "The supported hypothesis still retains unresolved alternative "
                "explanations, so the policy prefers discrimination before teaching."
            )
            blocking.extend(entry.unresolved_alternative_notes)
        elif entry.intervention.state == "none":
            action = "TEACH_CONCEPT"
            reasons.append(
                "The hypothesis is supported and sufficiently challenged, but no "
                "current M9 intervention selection exists."
            )
            if synthesis.concept_ids:
                reasons.append(
                    f"M39 exposes {len(synthesis.concept_ids)} chess concept(s) as "
                    "grounded explanatory context; M40 does not select among them."
                )
        elif entry.intervention.state == "mixed":
            action = "COLLECT_NEW_EVIDENCE"
            reasons.append(
                "Current M9 selection decisions are mixed; M40 will not reconcile "
                "or override M9 selection authority."
            )
            blocking.append("M9 selection state requires an explicit upstream resolution.")
        else:
            practice = _outcome_status(entry, "practice")
            near = _outcome_status(entry, "near_transfer")
            far = _outcome_status(entry, "far_transfer")
            real_game = _outcome_status(entry, "real_game_transfer")
            if practice != "supported":
                action = "ASSIGN_PRACTICE"
                reasons.append(
                    "An M9 intervention is selected, but supported practice evidence "
                    "is not yet present in the current M11 trajectory."
                )
            elif near != "supported":
                action = "RUN_NEAR_TRANSFER_TEST"
                reasons.append(
                    "Practice is supported, while near-transfer evidence is not yet "
                    "supported; test the skill in a fresh nearby context."
                )
            elif far != "supported":
                action = "RUN_FAR_TRANSFER_TEST"
                reasons.append(
                    "Practice and near transfer are supported, while far transfer is "
                    "not yet supported; test a meaningfully different context."
                )
            else:
                action = "WAIT_FOR_REAL_GAME_EVIDENCE"
                if real_game == "supported":
                    reasons.append(
                        "Practice, near transfer, far transfer, and current real-game "
                        "evidence are supported; continue observation without making "
                        "an automatic mastery claim."
                    )
                else:
                    reasons.append(
                        "Practice, near transfer, and far transfer are supported; "
                        "wait for bounded real-game evidence rather than declaring "
                        "mastery from exercises."
                    )
    else:
        raise ValueError(f"M40 cannot plan from unknown M7 status {status!r}")

    concept_ids = () if synthesis is None else synthesis.concept_ids
    synthesis_ref = None if synthesis is None else _synthesis_ref(synthesis)
    return NextSessionActionCandidate(
        hypothesis_id=entry.hypothesis_id,
        hypothesis_revision_ref=entry.current_revision_ref,
        m7_status=status,
        action=action,
        policy_priority=policy.priority_for(action),
        reasons=tuple(reasons),
        blocking_uncertainty=tuple(dict.fromkeys(blocking)),
        synthesis_ref=synthesis_ref,
        concept_ids=concept_ids,
        selected_intervention_ids=_selected_intervention_ids(entry),
        outcome_statuses=_outcome_statuses(entry),
    )


def build_next_session_plan(
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    policy: NextSessionPolicy,
    created_at: str,
) -> NextSessionPlan:
    """Rank transparent next-action proposals for the participant's active state."""
    _timestamp("created_at", created_at)
    validate_next_session_policy(policy)

    synthesis_by_revision = {
        item.hypothesis_revision_ref.revision_id: item for item in evidence_syntheses
    }
    if len(synthesis_by_revision) != len(evidence_syntheses):
        raise ValueError("M40 syntheses must be unique per current revision")

    active_entries = tuple(
        item
        for item in learner_read_model.hypotheses
        if item.authority_lifecycle_state == "active"
    )
    if not active_entries:
        raise ValueError("M40 requires at least one active learner hypothesis")

    candidates: list[NextSessionActionCandidate] = []
    used_revision_ids: set[str] = set()
    for entry in active_entries:
        revision_id = entry.current_revision_ref.revision_id
        synthesis = synthesis_by_revision.get(revision_id)
        if entry.m7_status is not None:
            if synthesis is None:
                raise ValueError(
                    "M40 requires M39 synthesis for every assessed active hypothesis"
                )
            _validate_synthesis_for_entry(
                entry=entry,
                synthesis=synthesis,
                read_model=learner_read_model,
            )
            used_revision_ids.add(revision_id)
        elif synthesis is not None:
            raise ValueError("M40 cannot bind synthesis to hypothesis without M7C status")
        candidates.append(
            _action_for_entry(entry=entry, synthesis=synthesis, policy=policy)
        )

    extras = set(synthesis_by_revision) - used_revision_ids
    if extras:
        raise ValueError("M40 syntheses include non-active or unreferenced revisions")

    ranked = tuple(
        sorted(
            candidates,
            key=lambda item: (-item.policy_priority, item.hypothesis_id, item.action),
        )
    )
    synthesis_refs = tuple(
        sorted(
            (_synthesis_ref(item) for item in evidence_syntheses),
            key=lambda item: item.ref_id,
        )
    )
    payload = {
        "schema_version": NEXT_SESSION_PLAN_SCHEMA_VERSION,
        "participant_id": learner_read_model.participant_id,
        "learner_read_model_ref": _read_model_ref(learner_read_model).to_dict(),
        "policy_ref": policy.ref.to_dict(),
        "synthesis_refs": [item.to_dict() for item in synthesis_refs],
        "selected_candidate": ranked[0].to_dict(),
        "candidates": [item.to_dict() for item in ranked],
        "created_at": created_at,
        "decision_authority": "proposal_only",
        "claim_scope": "participant_specific_next_session_proposal",
        "causal_effect": "not_established",
        "mastery": "not_established",
    }
    digest = _digest(payload)
    return NextSessionPlan(
        plan_id=f"next_session_plan_{digest[:20]}",
        fingerprint=digest,
        participant_id=learner_read_model.participant_id,
        learner_read_model_ref=_read_model_ref(learner_read_model),
        policy_ref=policy.ref,
        synthesis_refs=synthesis_refs,
        selected_candidate=ranked[0],
        candidates=ranked,
        created_at=created_at,
    )


def validate_next_session_plan(
    plan: NextSessionPlan,
    *,
    learner_read_model: LearnerStateReadModel,
    evidence_syntheses: tuple[HypothesisEvidenceSynthesis, ...],
    policy: NextSessionPolicy,
) -> None:
    expected = build_next_session_plan(
        learner_read_model=learner_read_model,
        evidence_syntheses=evidence_syntheses,
        policy=policy,
        created_at=plan.created_at,
    )
    if plan != expected:
        raise ValueError("M40 next-session plan mismatch")
