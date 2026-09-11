"""M45 deterministic batch-games to mentor-queue projection.

M45 composes an exact M4D diagnostic candidate batch with an explicit participant
scope, an exact M44 learner-progress view, and optional exact M42 transfer plans.
It proposes review priority only. It does not create learner hypotheses, reclassify
M7C evidence, select M9 interventions, create M10 outcomes, or establish mastery.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.selection import DiagnosticCandidate, DiagnosticCandidateBatch

from .evidence_synthesis import EvidenceSynthesisReference
from .progress_model import LearnerProgressView
from .transfer_retest import TransferRetestPlan

MENTOR_QUEUE_SCOPE_SCHEMA_VERSION = "m45.mentor-queue-batch-scope.v1"
MENTOR_QUEUE_POLICY_SCHEMA_VERSION = "m45.mentor-queue-policy.v1"
MENTOR_QUEUE_SCHEMA_VERSION = "m45.mentor-queue.v1"


@dataclass(frozen=True, slots=True)
class MentorQueueBatchScope:
    scope_id: str
    fingerprint: str
    participant_id: str
    diagnostic_batch_ref: EvidenceSynthesisReference
    game_ids: tuple[str, ...]
    source_refs: tuple[EvidenceSynthesisReference, ...]
    claim_scope: str = "explicit_participant_batch_scope"
    schema_version: str = MENTOR_QUEUE_SCOPE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("scope_id", self.scope_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("participant_id", self.participant_id)
        _unique("game_ids", self.game_ids)
        if not self.game_ids:
            raise ValueError("M45 batch scope requires at least one game")
        if not self.source_refs:
            raise ValueError("M45 batch scope requires explicit provenance")
        if self.claim_scope != "explicit_participant_batch_scope":
            raise ValueError("M45 batch scope claim is invalid")
        if self.schema_version != MENTOR_QUEUE_SCOPE_SCHEMA_VERSION:
            raise ValueError("unsupported M45 batch-scope schema")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "diagnostic_batch_ref": self.diagnostic_batch_ref.to_dict(),
            "game_ids": list(self.game_ids),
            "source_refs": [item.to_dict() for item in self.source_refs],
            "claim_scope": self.claim_scope,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class MentorQueuePolicyRef:
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
class MentorQueuePolicy:
    policy_id: str
    version: str
    fingerprint: str
    requested_size: int
    maximum_per_game: int
    prefer_semantic_diversity: bool = True
    claim_scope: str = "transparent_review_priority_policy"
    schema_version: str = MENTOR_QUEUE_POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _nonempty(name, value)
        if self.requested_size <= 0:
            raise ValueError("M45 requested_size must be positive")
        if self.maximum_per_game <= 0:
            raise ValueError("M45 maximum_per_game must be positive")
        if self.claim_scope != "transparent_review_priority_policy":
            raise ValueError("M45 policy claim scope is invalid")
        if self.schema_version != MENTOR_QUEUE_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported M45 policy schema")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "requested_size": self.requested_size,
            "maximum_per_game": self.maximum_per_game,
            "prefer_semantic_diversity": self.prefer_semantic_diversity,
            "claim_scope": self.claim_scope,
        }

    @property
    def ref(self) -> MentorQueuePolicyRef:
        return MentorQueuePolicyRef(
            self.policy_id,
            self.version,
            self.fingerprint,
        )


@dataclass(frozen=True, slots=True)
class MentorQueueDimensions:
    action_alignment: int
    contradiction_control_value: int
    transfer_value: int
    learner_relevance: int
    uncertainty_reduction: int
    objective_importance: int
    novelty: int
    semantic_diversity: int

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            if not isinstance(value, int) or not 0 <= value <= 3:
                raise ValueError(f"M45 dimension {name} must be an integer in 0..3")

    def to_dict(self) -> dict[str, int]:
        return {
            "action_alignment": self.action_alignment,
            "contradiction_control_value": self.contradiction_control_value,
            "transfer_value": self.transfer_value,
            "learner_relevance": self.learner_relevance,
            "uncertainty_reduction": self.uncertainty_reduction,
            "objective_importance": self.objective_importance,
            "novelty": self.novelty,
            "semantic_diversity": self.semantic_diversity,
        }


@dataclass(frozen=True, slots=True)
class MentorQueueItem:
    rank: int
    diagnostic_candidate_ref: EvidenceSynthesisReference
    position_id: str
    game_id: str
    comparison_id: str
    hypothesis_ids: tuple[str, ...]
    concept_ids: tuple[str, ...]
    dimensions: MentorQueueDimensions
    reasons: tuple[str, ...]
    review_authority: Literal["proposal_only"] = "proposal_only"

    def __post_init__(self) -> None:
        if self.rank <= 0:
            raise ValueError("M45 queue rank must be positive")
        for name, value in (
            ("position_id", self.position_id),
            ("game_id", self.game_id),
            ("comparison_id", self.comparison_id),
        ):
            _nonempty(name, value)
        _unique("hypothesis_ids", self.hypothesis_ids)
        _unique("concept_ids", self.concept_ids)
        _unique("reasons", self.reasons)
        if not self.reasons:
            raise ValueError("M45 queue item requires explicit reasons")
        if self.review_authority != "proposal_only":
            raise ValueError("M45 queue item cannot grant review execution authority")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "diagnostic_candidate_ref": self.diagnostic_candidate_ref.to_dict(),
            "position_id": self.position_id,
            "game_id": self.game_id,
            "comparison_id": self.comparison_id,
            "hypothesis_ids": list(self.hypothesis_ids),
            "concept_ids": list(self.concept_ids),
            "dimensions": self.dimensions.to_dict(),
            "reasons": list(self.reasons),
            "review_authority": self.review_authority,
        }


@dataclass(frozen=True, slots=True)
class MentorQueue:
    queue_id: str
    fingerprint: str
    participant_id: str
    batch_scope_ref: EvidenceSynthesisReference
    learner_progress_view_ref: EvidenceSynthesisReference
    transfer_plan_refs: tuple[EvidenceSynthesisReference, ...]
    policy_ref: MentorQueuePolicyRef
    requested_size: int
    items: tuple[MentorQueueItem, ...]
    excluded_candidate_ids: tuple[str, ...]
    shortfall: int
    created_at: str
    decision_authority: Literal["review_priority_proposal_only"] = (
        "review_priority_proposal_only"
    )
    learner_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = MENTOR_QUEUE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("queue_id", self.queue_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != MENTOR_QUEUE_SCHEMA_VERSION:
            raise ValueError("unsupported M45 queue schema")
        if self.requested_size <= 0:
            raise ValueError("M45 queue requested_size must be positive")
        if len(self.items) > self.requested_size:
            raise ValueError("M45 queue exceeds requested size")
        if self.shortfall != self.requested_size - len(self.items):
            raise ValueError("M45 queue shortfall is inconsistent")
        ranks = tuple(item.rank for item in self.items)
        if ranks != tuple(range(1, len(self.items) + 1)):
            raise ValueError("M45 queue ranks must be contiguous")
        candidate_ids = tuple(
            item.diagnostic_candidate_ref.ref_id for item in self.items
        )
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("M45 queue items must be unique")
        _unique("excluded_candidate_ids", self.excluded_candidate_ids)
        if set(candidate_ids).intersection(self.excluded_candidate_ids):
            raise ValueError("M45 selected and excluded candidates overlap")
        refs = tuple(
            (item.kind, item.ref_id, item.fingerprint)
            for item in self.transfer_plan_refs
        )
        if len(set(refs)) != len(refs):
            raise ValueError("M45 transfer plan refs must be unique")
        if self.decision_authority != "review_priority_proposal_only":
            raise ValueError("M45 cannot grant review execution authority")
        if (
            self.learner_effect != "not_established"
            or self.mastery != "not_established"
        ):
            raise ValueError("M45 cannot establish learner effect or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "batch_scope_ref": self.batch_scope_ref.to_dict(),
            "learner_progress_view_ref": self.learner_progress_view_ref.to_dict(),
            "transfer_plan_refs": [item.to_dict() for item in self.transfer_plan_refs],
            "policy_ref": self.policy_ref.to_dict(),
            "requested_size": self.requested_size,
            "items": [item.to_dict() for item in self.items],
            "excluded_candidate_ids": list(self.excluded_candidate_ids),
            "shortfall": self.shortfall,
            "created_at": self.created_at,
            "decision_authority": self.decision_authority,
            "learner_effect": self.learner_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue_id": self.queue_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


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


def _unique(name: str, values: tuple[str, ...]) -> None:
    if any(not item for item in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} values must be unique")


def _batch_ref(batch: DiagnosticCandidateBatch) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "diagnostic_candidate_batch",
        batch.batch_id,
        _digest(batch.to_dict()),
    )


def _scope_ref(scope: MentorQueueBatchScope) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "mentor_queue_batch_scope",
        scope.scope_id,
        scope.fingerprint,
    )


def _view_ref(view: LearnerProgressView) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_progress_view",
        view.view_id,
        view.fingerprint,
    )


def _candidate_ref(candidate: DiagnosticCandidate) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "diagnostic_candidate",
        candidate.candidate_id,
        _digest(candidate.to_dict()),
    )


def _transfer_ref(plan: TransferRetestPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "transfer_retest_plan",
        plan.transfer_plan_id,
        plan.fingerprint,
    )


def bind_mentor_queue_batch_scope(
    *,
    participant_id: str,
    diagnostic_batch: DiagnosticCandidateBatch,
    source_refs: tuple[EvidenceSynthesisReference, ...],
) -> MentorQueueBatchScope:
    """Bind M4D's participant-agnostic batch to one explicit participant scope."""
    _nonempty("participant_id", participant_id)
    if not diagnostic_batch.candidates:
        raise ValueError("M45 cannot scope an empty diagnostic batch")
    game_ids = tuple(
        sorted({item.game_id for item in diagnostic_batch.candidates})
    )
    payload = {
        "schema_version": MENTOR_QUEUE_SCOPE_SCHEMA_VERSION,
        "participant_id": participant_id,
        "diagnostic_batch_ref": _batch_ref(diagnostic_batch).to_dict(),
        "game_ids": list(game_ids),
        "source_refs": [item.to_dict() for item in source_refs],
        "claim_scope": "explicit_participant_batch_scope",
    }
    fingerprint = _digest(payload)
    return MentorQueueBatchScope(
        scope_id=f"mentor_queue_batch_scope_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=participant_id,
        diagnostic_batch_ref=_batch_ref(diagnostic_batch),
        game_ids=game_ids,
        source_refs=source_refs,
    )


def validate_mentor_queue_batch_scope(
    scope: MentorQueueBatchScope,
    *,
    diagnostic_batch: DiagnosticCandidateBatch,
) -> None:
    if scope.diagnostic_batch_ref != _batch_ref(diagnostic_batch):
        raise ValueError("M45 batch-scope diagnostic batch mismatch")
    expected_games = tuple(
        sorted({item.game_id for item in diagnostic_batch.candidates})
    )
    if scope.game_ids != expected_games:
        raise ValueError("M45 batch-scope game set mismatch")
    if _digest(scope.identity_payload()) != scope.fingerprint:
        raise ValueError("M45 batch-scope fingerprint mismatch")
    if scope.scope_id != f"mentor_queue_batch_scope_{scope.fingerprint[:20]}":
        raise ValueError("M45 batch-scope identity mismatch")


def build_default_mentor_queue_policy(
    *,
    requested_size: int = 5,
    maximum_per_game: int = 2,
) -> MentorQueuePolicy:
    payload = {
        "schema_version": MENTOR_QUEUE_POLICY_SCHEMA_VERSION,
        "policy_id": "m45.default-mentor-queue-policy",
        "version": "1",
        "requested_size": requested_size,
        "maximum_per_game": maximum_per_game,
        "prefer_semantic_diversity": True,
        "claim_scope": "transparent_review_priority_policy",
    }
    return MentorQueuePolicy(
        policy_id=payload["policy_id"],
        version=payload["version"],
        fingerprint=_digest(payload),
        requested_size=requested_size,
        maximum_per_game=maximum_per_game,
    )


def validate_mentor_queue_policy(policy: MentorQueuePolicy) -> None:
    if _digest(policy.identity_payload()) != policy.fingerprint:
        raise ValueError("M45 mentor-queue policy fingerprint mismatch")


def _validate_view(view: LearnerProgressView) -> None:
    expected = _digest(view.identity_payload())
    if view.fingerprint != expected:
        raise ValueError("M45 learner-progress view fingerprint mismatch")
    if view.view_id != f"learner_progress_view_{expected[:20]}":
        raise ValueError("M45 learner-progress view identity mismatch")


def _validate_transfer_plan(
    plan: TransferRetestPlan,
    view: LearnerProgressView,
) -> None:
    expected = _digest(plan.identity_payload())
    if plan.fingerprint != expected:
        raise ValueError("M45 M42 transfer-plan fingerprint mismatch")
    if plan.transfer_plan_id != f"transfer_retest_plan_{expected[:20]}":
        raise ValueError("M45 M42 transfer-plan identity mismatch")
    if plan.participant_id != view.participant_id:
        raise ValueError("M45 M42/M44 participant mismatch")
    if plan.next_session_plan_ref != view.next_session_plan_ref:
        raise ValueError("M45 M42/M44 next-session-plan mismatch")
    hypotheses = {item.hypothesis_id: item for item in view.hypotheses}
    hypothesis = hypotheses.get(plan.hypothesis_id)
    if hypothesis is None:
        raise ValueError("M45 M42 plan references unknown hypothesis")
    if plan.hypothesis_revision_ref != hypothesis.current_revision_ref:
        raise ValueError("M45 M42 current-revision mismatch")


def _objective_importance(
    candidate: DiagnosticCandidate,
) -> tuple[int, tuple[str, ...]]:
    kinds = {item.kind for item in candidate.signals}
    if "MATE_RELATION" in kinds:
        return 3, ("M4 evidence includes a mate-relation signal.",)
    if "ENGINE_EVIDENCE_INVERSION" in kinds or "EXACT_CP_DELTA" in kinds:
        return 2, (
            "M4 evidence includes bounded objective decision-quality signal.",
        )
    if "TOP_CANDIDATE_SEPARATION" in kinds or "ROOT_SIDE_IS_IN_CHECK" in kinds:
        return 1, ("M4 evidence includes bounded objective context signal.",)
    return 0, (
        "M4 candidate is eligible without a higher-priority objective signal.",
    )


def _position_key(game_id: str, position_id: str) -> tuple[str, str]:
    return game_id, position_id


def _hypothesis_context(
    candidate: DiagnosticCandidate,
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...],
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    int,
    int,
    int,
    int,
    int,
    tuple[str, ...],
]:
    key = _position_key(candidate.game_id, candidate.position_id)
    hypothesis_ids: set[str] = set()
    concepts: set[str] = set()
    learner_relevance = 0
    contradiction_value = 0
    transfer_value = 0
    uncertainty = 0
    action_alignment = 0
    reasons: list[str] = []

    challenge_actions = {
        "CHALLENGE_HYPOTHESIS",
        "PRESENT_CONTROL",
        "COLLECT_NEW_EVIDENCE",
    }
    challenge_kinds = {
        "classified_contradiction": 3,
        "classified_successful_counterexample": 3,
        "potential_contradiction": 3,
        "potential_successful_counterexample": 3,
        "classified_context_exception": 2,
        "potential_context_exception": 2,
        "novel_retest_context": 1,
        "insufficiently_classified": 1,
    }

    for hypothesis in view.hypotheses:
        evidence_matches = tuple(
            item
            for item in hypothesis.evidence_units
            if _position_key(item.source_game_id, item.source_position_id) == key
        )
        acquisition_matches = tuple(
            item
            for item in hypothesis.acquisition_candidates
            if _position_key(item.source_game_id, item.source_position_id) == key
        )
        if evidence_matches or acquisition_matches:
            hypothesis_ids.add(hypothesis.hypothesis_id)
        if evidence_matches:
            learner_relevance = max(learner_relevance, 3)
            for item in evidence_matches:
                concepts.update(item.concept_ids)
            reasons.append(
                "Position already participates in qualified M7C evidence for "
                f"{hypothesis.hypothesis_id}."
            )
        if acquisition_matches:
            learner_relevance = max(learner_relevance, 2)
            local_contradiction = max(
                challenge_kinds.get(item.candidate_kind, 0)
                for item in acquisition_matches
            )
            contradiction_value = max(contradiction_value, local_contradiction)
            for item in acquisition_matches:
                concepts.update(item.concept_ids)
            if hypothesis.evidence_gaps:
                uncertainty = max(uncertainty, 2)
            if hypothesis.next_action in challenge_actions:
                action_alignment = max(action_alignment, 3)
            reasons.append(
                "M43 marks this position as useful challenge/control material for "
                f"{hypothesis.hypothesis_id}."
            )

    for plan in transfer_plans:
        matched_selected = (
            plan.selected_candidate is not None
            and _position_key(
                plan.selected_candidate.position.game_id,
                plan.selected_candidate.position.position_id,
            )
            == key
        )
        matched_eligible = tuple(
            item
            for item in plan.eligible_candidates
            if _position_key(item.position.game_id, item.position.position_id) == key
        )
        if not matched_selected and not matched_eligible:
            continue
        hypothesis_ids.add(plan.hypothesis_id)
        learner_relevance = max(learner_relevance, 2)
        transfer_value = max(transfer_value, 3 if matched_selected else 2)
        for item in matched_eligible:
            concepts.update(item.concept_ids)
        hypothesis = next(
            item
            for item in view.hypotheses
            if item.hypothesis_id == plan.hypothesis_id
        )
        expected_action = (
            "RUN_NEAR_TRANSFER_TEST"
            if plan.transfer_kind == "near"
            else "RUN_FAR_TRANSFER_TEST"
        )
        if hypothesis.next_action == expected_action:
            action_alignment = max(action_alignment, 3)
        selection_label = "selected" if matched_selected else "eligible"
        reasons.append(
            f"M42 identifies this position as {selection_label} "
            f"{plan.transfer_kind}-transfer material for {plan.hypothesis_id}."
        )

    if not hypothesis_ids:
        reasons.append(
            "No current learner-specific M44/M42 linkage was found; retain "
            "objective M4 eligibility only."
        )
    return (
        tuple(sorted(hypothesis_ids)),
        tuple(sorted(concepts)),
        action_alignment,
        contradiction_value,
        transfer_value,
        learner_relevance,
        uncertainty,
        tuple(dict.fromkeys(reasons)),
    )


def _novelty(
    candidate: DiagnosticCandidate,
    view: LearnerProgressView,
) -> tuple[int, str]:
    positions: set[tuple[str, str]] = set()
    games: set[str] = set()
    for hypothesis in view.hypotheses:
        for item in hypothesis.evidence_units:
            positions.add(_position_key(item.source_game_id, item.source_position_id))
            games.add(item.source_game_id)
    key = _position_key(candidate.game_id, candidate.position_id)
    if key in positions:
        return 0, (
            "Position is already represented in current qualified M7C evidence."
        )
    if candidate.game_id in games:
        return 1, (
            "Position is new but its game is already represented in current evidence."
        )
    return 2, (
        "Position and game are new relative to current qualified M7C evidence."
    )


def _base_dimensions(
    candidate: DiagnosticCandidate,
    *,
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...],
) -> tuple[
    MentorQueueDimensions,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    (
        hypothesis_ids,
        concept_ids,
        action_alignment,
        contradiction_value,
        transfer_value,
        learner_relevance,
        uncertainty,
        learner_reasons,
    ) = _hypothesis_context(candidate, view, transfer_plans)
    objective, objective_reasons = _objective_importance(candidate)
    novelty, novelty_reason = _novelty(candidate, view)
    dimensions = MentorQueueDimensions(
        action_alignment=action_alignment,
        contradiction_control_value=contradiction_value,
        transfer_value=transfer_value,
        learner_relevance=learner_relevance,
        uncertainty_reduction=uncertainty,
        objective_importance=objective,
        novelty=novelty,
        semantic_diversity=0,
    )
    return (
        dimensions,
        hypothesis_ids,
        concept_ids,
        learner_reasons + objective_reasons + (novelty_reason,),
    )


def _rank_key(
    candidate: DiagnosticCandidate,
    dimensions: MentorQueueDimensions,
) -> tuple[int, int, int, int, int, int, int, str, str, str]:
    return (
        -dimensions.action_alignment,
        -dimensions.contradiction_control_value,
        -dimensions.transfer_value,
        -dimensions.uncertainty_reduction,
        -dimensions.learner_relevance,
        -dimensions.objective_importance,
        -dimensions.novelty,
        candidate.game_id,
        candidate.position_id,
        candidate.candidate_id,
    )


def _choose_next(
    remaining: tuple[DiagnosticCandidate, ...],
    *,
    context: dict[
        str,
        tuple[
            MentorQueueDimensions,
            tuple[str, ...],
            tuple[str, ...],
            tuple[str, ...],
        ],
    ],
    represented_concepts: set[str],
    game_counts: dict[str, int],
    policy: MentorQueuePolicy,
) -> tuple[DiagnosticCandidate | None, MentorQueueDimensions | None]:
    eligible = tuple(
        candidate
        for candidate in remaining
        if game_counts.get(candidate.game_id, 0) < policy.maximum_per_game
    )
    if not eligible:
        return None, None

    ranked: list[
        tuple[tuple[Any, ...], DiagnosticCandidate, MentorQueueDimensions]
    ] = []
    for candidate in eligible:
        base, _, concepts, _ = context[candidate.candidate_id]
        diversity = 0
        if policy.prefer_semantic_diversity and set(concepts) - represented_concepts:
            diversity = min(3, len(set(concepts) - represented_concepts))
        dimensions = MentorQueueDimensions(
            action_alignment=base.action_alignment,
            contradiction_control_value=base.contradiction_control_value,
            transfer_value=base.transfer_value,
            learner_relevance=base.learner_relevance,
            uncertainty_reduction=base.uncertainty_reduction,
            objective_importance=base.objective_importance,
            novelty=base.novelty,
            semantic_diversity=diversity,
        )
        key = _rank_key(candidate, dimensions)[:-3] + (
            -dimensions.semantic_diversity,
            candidate.game_id,
            candidate.position_id,
            candidate.candidate_id,
        )
        ranked.append((key, candidate, dimensions))
    ranked.sort(key=lambda item: item[0])
    _, chosen, dimensions = ranked[0]
    return chosen, dimensions


def build_mentor_queue(
    *,
    diagnostic_batch: DiagnosticCandidateBatch,
    batch_scope: MentorQueueBatchScope,
    learner_progress_view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
    policy: MentorQueuePolicy,
    created_at: str,
) -> MentorQueue:
    """Build one deterministic participant-scoped review-priority proposal."""
    validate_mentor_queue_batch_scope(
        batch_scope,
        diagnostic_batch=diagnostic_batch,
    )
    validate_mentor_queue_policy(policy)
    _validate_view(learner_progress_view)
    _timestamp("created_at", created_at)
    if batch_scope.participant_id != learner_progress_view.participant_id:
        raise ValueError("M45 batch scope / learner-progress participant mismatch")
    for plan in transfer_plans:
        _validate_transfer_plan(plan, learner_progress_view)
    sorted_transfers = tuple(
        sorted(transfer_plans, key=lambda item: item.transfer_plan_id)
    )
    transfer_ids = tuple(item.transfer_plan_id for item in sorted_transfers)
    if len(set(transfer_ids)) != len(transfer_ids):
        raise ValueError("M45 transfer plans must be unique")

    candidates = tuple(
        sorted(
            diagnostic_batch.candidates,
            key=lambda item: item.candidate_id,
        )
    )
    context = {
        item.candidate_id: _base_dimensions(
            item,
            view=learner_progress_view,
            transfer_plans=sorted_transfers,
        )
        for item in candidates
    }
    selected: list[MentorQueueItem] = []
    remaining = list(candidates)
    represented_concepts: set[str] = set()
    game_counts: dict[str, int] = {}

    while remaining and len(selected) < policy.requested_size:
        chosen, dimensions = _choose_next(
            tuple(remaining),
            context=context,
            represented_concepts=represented_concepts,
            game_counts=game_counts,
            policy=policy,
        )
        if chosen is None or dimensions is None:
            break
        _, hypothesis_ids, concept_ids, reasons = context[chosen.candidate_id]
        selected.append(
            MentorQueueItem(
                rank=len(selected) + 1,
                diagnostic_candidate_ref=_candidate_ref(chosen),
                position_id=chosen.position_id,
                game_id=chosen.game_id,
                comparison_id=chosen.comparison_id,
                hypothesis_ids=hypothesis_ids,
                concept_ids=concept_ids,
                dimensions=dimensions,
                reasons=reasons,
            )
        )
        represented_concepts.update(concept_ids)
        game_counts[chosen.game_id] = game_counts.get(chosen.game_id, 0) + 1
        remaining.remove(chosen)

    selected_ids = {item.diagnostic_candidate_ref.ref_id for item in selected}
    excluded = tuple(
        sorted(
            item.candidate_id
            for item in candidates
            if item.candidate_id not in selected_ids
        )
    )
    transfer_refs = tuple(_transfer_ref(item) for item in sorted_transfers)
    payload = {
        "schema_version": MENTOR_QUEUE_SCHEMA_VERSION,
        "participant_id": learner_progress_view.participant_id,
        "batch_scope_ref": _scope_ref(batch_scope).to_dict(),
        "learner_progress_view_ref": _view_ref(learner_progress_view).to_dict(),
        "transfer_plan_refs": [item.to_dict() for item in transfer_refs],
        "policy_ref": policy.ref.to_dict(),
        "requested_size": policy.requested_size,
        "items": [item.to_dict() for item in selected],
        "excluded_candidate_ids": list(excluded),
        "shortfall": policy.requested_size - len(selected),
        "created_at": created_at,
        "decision_authority": "review_priority_proposal_only",
        "learner_effect": "not_established",
        "mastery": "not_established",
    }
    fingerprint = _digest(payload)
    return MentorQueue(
        queue_id=f"mentor_queue_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=learner_progress_view.participant_id,
        batch_scope_ref=_scope_ref(batch_scope),
        learner_progress_view_ref=_view_ref(learner_progress_view),
        transfer_plan_refs=transfer_refs,
        policy_ref=policy.ref,
        requested_size=policy.requested_size,
        items=tuple(selected),
        excluded_candidate_ids=excluded,
        shortfall=policy.requested_size - len(selected),
        created_at=created_at,
    )


def validate_mentor_queue(
    queue: MentorQueue,
    *,
    diagnostic_batch: DiagnosticCandidateBatch,
    batch_scope: MentorQueueBatchScope,
    learner_progress_view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
    policy: MentorQueuePolicy,
) -> None:
    expected = build_mentor_queue(
        diagnostic_batch=diagnostic_batch,
        batch_scope=batch_scope,
        learner_progress_view=learner_progress_view,
        transfer_plans=transfer_plans,
        policy=policy,
        created_at=queue.created_at,
    )
    if expected != queue:
        raise ValueError("M45 mentor queue mismatch")
