"""M42 bounded near/far transfer and retest planning.

M42 consumes an exact M40 transfer-test proposal and exact current M9 selection.
It ranks explicitly described M10-compatible positions for a future test. Planning
never becomes M10 outcome evidence, transfer success, causal effect, or mastery.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.evaluation import OutcomePosition
from chess_mentor_engine.learning import HypothesisRevisionRef
from chess_mentor_engine.training import (
    InterventionSelectionDecision,
    TrainingInterventionDefinition,
    TrainingInterventionRef,
)

from .evidence_synthesis import EvidenceSynthesisReference
from .next_session import NextSessionActionCandidate, NextSessionPlan

TRANSFER_RETEST_PLAN_SCHEMA_VERSION = "m42.transfer-retest-plan.v1"
TRANSFER_RETEST_POLICY_SCHEMA_VERSION = "m42.transfer-retest-policy.v1"
TRANSFER_POSITION_CANDIDATE_SCHEMA_VERSION = "m42.transfer-position-candidate.v1"

TransferKind: TypeAlias = Literal["near", "far"]
TransferSemanticRelation: TypeAlias = Literal[
    "same_target",
    "related_target",
    "unknown",
]
TransferSurfaceVariation: TypeAlias = Literal["same", "near", "different"]
TransferCandidateFreshness: TypeAlias = Literal[
    "fresh",
    "previously_exposed",
    "unknown",
]
TransferPlanningStatus: TypeAlias = Literal["planned", "no_eligible_candidate"]

_SUPPORTED_ACTIONS = {
    "RUN_NEAR_TRANSFER_TEST": "near",
    "RUN_FAR_TRANSFER_TEST": "far",
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


def _plan_ref(plan: NextSessionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_plan",
        plan.plan_id,
        plan.fingerprint,
    )


def _proposal_ref(
    proposal: NextSessionActionCandidate,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_action_candidate",
        (
            f"{proposal.hypothesis_id}:"
            f"{proposal.hypothesis_revision_ref.revision_id}:{proposal.action}"
        ),
        _digest(proposal.to_dict()),
    )


def _selection_ref(
    selection: InterventionSelectionDecision,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "intervention_selection_decision",
        selection.selection_id,
        selection.fingerprint,
    )


def _intervention_ref(
    intervention: TrainingInterventionDefinition,
) -> TrainingInterventionRef:
    return TrainingInterventionRef(
        intervention_id=intervention.intervention_id,
        intervention_key=intervention.intervention_key,
        version=intervention.version,
        fingerprint=intervention.fingerprint,
    )


@dataclass(frozen=True, slots=True)
class TransferRetestPolicyRef:
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
class TransferRetestPolicy:
    policy_id: str
    version: str
    fingerprint: str
    require_fresh_candidate: bool
    near_allowed_relations: tuple[TransferSemanticRelation, ...]
    near_allowed_variations: tuple[TransferSurfaceVariation, ...]
    far_allowed_relations: tuple[TransferSemanticRelation, ...]
    far_allowed_variations: tuple[TransferSurfaceVariation, ...]
    claim_scope: str = "transparent_transfer_retest_planning_policy"
    schema_version: str = TRANSFER_RETEST_POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _nonempty(name, value)
        if self.schema_version != TRANSFER_RETEST_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported M42 policy schema")
        _unique("near_allowed_relations", self.near_allowed_relations)
        _unique("near_allowed_variations", self.near_allowed_variations)
        _unique("far_allowed_relations", self.far_allowed_relations)
        _unique("far_allowed_variations", self.far_allowed_variations)
        if not self.near_allowed_relations or not self.near_allowed_variations:
            raise ValueError("M42 near-transfer policy must allow candidates")
        if not self.far_allowed_relations or not self.far_allowed_variations:
            raise ValueError("M42 far-transfer policy must allow candidates")
        if self.claim_scope != "transparent_transfer_retest_planning_policy":
            raise ValueError("unknown M42 policy claim scope")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "require_fresh_candidate": self.require_fresh_candidate,
            "near_allowed_relations": list(self.near_allowed_relations),
            "near_allowed_variations": list(self.near_allowed_variations),
            "far_allowed_relations": list(self.far_allowed_relations),
            "far_allowed_variations": list(self.far_allowed_variations),
            "claim_scope": self.claim_scope,
        }

    @property
    def ref(self) -> TransferRetestPolicyRef:
        return TransferRetestPolicyRef(
            self.policy_id,
            self.version,
            self.fingerprint,
        )


@dataclass(frozen=True, slots=True)
class TransferPositionCandidate:
    candidate_id: str
    fingerprint: str
    position: OutcomePosition
    semantic_relation: TransferSemanticRelation
    surface_variation: TransferSurfaceVariation
    freshness: TransferCandidateFreshness
    concept_ids: tuple[str, ...]
    held_constant: tuple[str, ...]
    varied_dimensions: tuple[str, ...]
    source_refs: tuple[EvidenceSynthesisReference, ...]
    rationale: str
    schema_version: str = TRANSFER_POSITION_CANDIDATE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("candidate_id", self.candidate_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("rationale", self.rationale)
        if self.schema_version != TRANSFER_POSITION_CANDIDATE_SCHEMA_VERSION:
            raise ValueError("unsupported M42 candidate schema")
        if self.semantic_relation not in {
            "same_target",
            "related_target",
            "unknown",
        }:
            raise ValueError("unknown M42 semantic relation")
        if self.surface_variation not in {"same", "near", "different"}:
            raise ValueError("unknown M42 surface variation")
        if self.freshness not in {"fresh", "previously_exposed", "unknown"}:
            raise ValueError("unknown M42 candidate freshness")
        for name, values in (
            ("concept_ids", self.concept_ids),
            ("held_constant", self.held_constant),
            ("varied_dimensions", self.varied_dimensions),
        ):
            _unique(name, values)
        if not self.held_constant:
            raise ValueError("M42 candidate must state what is held constant")
        if not self.varied_dimensions:
            raise ValueError("M42 candidate must state what varies")
        ref_keys = tuple(
            (item.kind, item.ref_id, item.fingerprint) for item in self.source_refs
        )
        if len(set(ref_keys)) != len(ref_keys):
            raise ValueError("M42 candidate source refs must be unique")
        if not self.source_refs:
            raise ValueError("M42 candidate requires provenance refs")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "position": {
                "position_id": self.position.position_id,
                "game_id": self.position.game_id,
                "fen": self.position.fen,
                "source_ref": {
                    "kind": self.position.source_ref.kind,
                    "ref_id": self.position.source_ref.ref_id,
                    "fingerprint": self.position.source_ref.fingerprint,
                },
            },
            "semantic_relation": self.semantic_relation,
            "surface_variation": self.surface_variation,
            "freshness": self.freshness,
            "concept_ids": list(self.concept_ids),
            "held_constant": list(self.held_constant),
            "varied_dimensions": list(self.varied_dimensions),
            "source_refs": [item.to_dict() for item in self.source_refs],
            "rationale": self.rationale,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class TransferRetestPlan:
    transfer_plan_id: str
    fingerprint: str
    participant_id: str
    hypothesis_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    next_session_plan_ref: EvidenceSynthesisReference
    proposal_ref: EvidenceSynthesisReference
    selection_ref: EvidenceSynthesisReference
    intervention_ref: TrainingInterventionRef
    transfer_kind: TransferKind
    measurement_target: str
    target_concept_ids: tuple[str, ...]
    exercise_ids: tuple[str, ...]
    policy_ref: TransferRetestPolicyRef
    eligible_candidates: tuple[TransferPositionCandidate, ...]
    selected_candidate: TransferPositionCandidate | None
    planning_status: TransferPlanningStatus
    blocking_uncertainty: tuple[str, ...]
    created_at: str
    plan_authority: Literal["planning_only"] = "planning_only"
    outcome_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = TRANSFER_RETEST_PLAN_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("transfer_plan_id", self.transfer_plan_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("hypothesis_id", self.hypothesis_id),
            ("measurement_target", self.measurement_target),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != TRANSFER_RETEST_PLAN_SCHEMA_VERSION:
            raise ValueError("unsupported M42 transfer-plan schema")
        if self.transfer_kind not in {"near", "far"}:
            raise ValueError("unknown M42 transfer kind")
        _unique("target_concept_ids", self.target_concept_ids)
        _unique("exercise_ids", self.exercise_ids)
        _unique("blocking_uncertainty", self.blocking_uncertainty)
        if not self.exercise_ids:
            raise ValueError("M42 plan requires exact intervention exercises")
        candidate_ids = tuple(
            item.candidate_id for item in self.eligible_candidates
        )
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("M42 eligible candidates must be unique")
        if self.planning_status == "planned":
            if (
                not self.eligible_candidates
                or self.selected_candidate != self.eligible_candidates[0]
            ):
                raise ValueError(
                    "M42 planned result must select leading candidate"
                )
        elif self.planning_status == "no_eligible_candidate":
            if self.eligible_candidates or self.selected_candidate is not None:
                raise ValueError(
                    "M42 no-candidate result cannot select a position"
                )
            if not self.blocking_uncertainty:
                raise ValueError(
                    "M42 no-candidate result must explain the gap"
                )
        else:
            raise ValueError("unknown M42 planning status")
        if self.plan_authority != "planning_only":
            raise ValueError("M42 cannot grant M10 outcome authority")
        if (
            self.outcome_effect != "not_established"
            or self.mastery != "not_established"
        ):
            raise ValueError(
                "M42 cannot establish transfer outcome or mastery"
            )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "next_session_plan_ref": self.next_session_plan_ref.to_dict(),
            "proposal_ref": self.proposal_ref.to_dict(),
            "selection_ref": self.selection_ref.to_dict(),
            "intervention_ref": self.intervention_ref.to_dict(),
            "transfer_kind": self.transfer_kind,
            "measurement_target": self.measurement_target,
            "target_concept_ids": list(self.target_concept_ids),
            "exercise_ids": list(self.exercise_ids),
            "policy_ref": self.policy_ref.to_dict(),
            "eligible_candidates": [
                item.to_dict() for item in self.eligible_candidates
            ],
            "selected_candidate": (
                None
                if self.selected_candidate is None
                else self.selected_candidate.to_dict()
            ),
            "planning_status": self.planning_status,
            "blocking_uncertainty": list(self.blocking_uncertainty),
            "created_at": self.created_at,
            "plan_authority": self.plan_authority,
            "outcome_effect": self.outcome_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "transfer_plan_id": self.transfer_plan_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_default_transfer_retest_policy() -> TransferRetestPolicy:
    payload = {
        "schema_version": TRANSFER_RETEST_POLICY_SCHEMA_VERSION,
        "policy_id": "m42.default-transfer-retest-policy",
        "version": "1",
        "require_fresh_candidate": True,
        "near_allowed_relations": ["same_target"],
        "near_allowed_variations": ["near", "different"],
        "far_allowed_relations": ["same_target", "related_target"],
        "far_allowed_variations": ["different"],
        "claim_scope": "transparent_transfer_retest_planning_policy",
    }
    return TransferRetestPolicy(
        policy_id=payload["policy_id"],
        version=payload["version"],
        fingerprint=_digest(payload),
        require_fresh_candidate=True,
        near_allowed_relations=("same_target",),
        near_allowed_variations=("near", "different"),
        far_allowed_relations=("same_target", "related_target"),
        far_allowed_variations=("different",),
    )


def validate_transfer_retest_policy(policy: TransferRetestPolicy) -> None:
    if _digest(policy.identity_payload()) != policy.fingerprint:
        raise ValueError("M42 transfer-retest policy fingerprint mismatch")


def define_transfer_position_candidate(
    *,
    position: OutcomePosition,
    semantic_relation: TransferSemanticRelation,
    surface_variation: TransferSurfaceVariation,
    freshness: TransferCandidateFreshness,
    concept_ids: tuple[str, ...],
    held_constant: tuple[str, ...],
    varied_dimensions: tuple[str, ...],
    source_refs: tuple[EvidenceSynthesisReference, ...],
    rationale: str,
) -> TransferPositionCandidate:
    payload = {
        "schema_version": TRANSFER_POSITION_CANDIDATE_SCHEMA_VERSION,
        "position": {
            "position_id": position.position_id,
            "game_id": position.game_id,
            "fen": position.fen,
            "source_ref": {
                "kind": position.source_ref.kind,
                "ref_id": position.source_ref.ref_id,
                "fingerprint": position.source_ref.fingerprint,
            },
        },
        "semantic_relation": semantic_relation,
        "surface_variation": surface_variation,
        "freshness": freshness,
        "concept_ids": list(concept_ids),
        "held_constant": list(held_constant),
        "varied_dimensions": list(varied_dimensions),
        "source_refs": [item.to_dict() for item in source_refs],
        "rationale": rationale,
    }
    fingerprint = _digest(payload)
    return TransferPositionCandidate(
        candidate_id=f"transfer_position_candidate_{fingerprint[:20]}",
        fingerprint=fingerprint,
        position=position,
        semantic_relation=semantic_relation,
        surface_variation=surface_variation,
        freshness=freshness,
        concept_ids=concept_ids,
        held_constant=held_constant,
        varied_dimensions=varied_dimensions,
        source_refs=source_refs,
        rationale=rationale,
    )


def validate_transfer_position_candidate(
    candidate: TransferPositionCandidate,
) -> None:
    if _digest(candidate.identity_payload()) != candidate.fingerprint:
        raise ValueError("M42 transfer candidate fingerprint mismatch")
    expected_id = f"transfer_position_candidate_{candidate.fingerprint[:20]}"
    if candidate.candidate_id != expected_id:
        raise ValueError("M42 transfer candidate identity mismatch")


def _eligible(
    candidate: TransferPositionCandidate,
    *,
    transfer_kind: TransferKind,
    policy: TransferRetestPolicy,
    practice_reuse_keys: set[str],
) -> bool:
    if policy.require_fresh_candidate and candidate.freshness != "fresh":
        return False
    if candidate.position.reuse_key in practice_reuse_keys:
        return False
    if transfer_kind == "near":
        return (
            candidate.semantic_relation in policy.near_allowed_relations
            and candidate.surface_variation in policy.near_allowed_variations
        )
    return (
        candidate.semantic_relation in policy.far_allowed_relations
        and candidate.surface_variation in policy.far_allowed_variations
    )


def _rank_key(
    candidate: TransferPositionCandidate,
    transfer_kind: TransferKind,
) -> tuple[int, int, str, str]:
    relation_rank = {
        "same_target": 2,
        "related_target": 1,
        "unknown": 0,
    }[candidate.semantic_relation]
    if transfer_kind == "near":
        variation_rank = {
            "near": 2,
            "different": 1,
            "same": 0,
        }[candidate.surface_variation]
    else:
        variation_rank = {
            "different": 2,
            "near": 1,
            "same": 0,
        }[candidate.surface_variation]
    return (
        -relation_rank,
        -variation_rank,
        candidate.position.game_id,
        candidate.position.position_id,
    )


def build_transfer_retest_plan(
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    selection: InterventionSelectionDecision,
    intervention: TrainingInterventionDefinition,
    candidate_positions: tuple[TransferPositionCandidate, ...],
    practice_position_reuse_keys: tuple[str, ...],
    measurement_target: str,
    policy: TransferRetestPolicy,
    created_at: str,
    ontology: OntologyRegistry | None = None,
) -> TransferRetestPlan:
    """Build a planning-only M42 transfer test from exact qualified identities."""
    validate_transfer_retest_policy(policy)
    _timestamp("created_at", created_at)
    _nonempty("measurement_target", measurement_target)
    _unique("practice_position_reuse_keys", practice_position_reuse_keys)
    if proposal not in next_session_plan.candidates:
        raise ValueError("M42 proposal is not part of the exact M40 plan")
    transfer_kind = _SUPPORTED_ACTIONS.get(proposal.action)
    if transfer_kind is None:
        raise ValueError("M42 requires a near/far transfer M40 action")
    if selection.participant_id != next_session_plan.participant_id:
        raise ValueError("M42 M9/M40 participant mismatch")
    if selection.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
        raise ValueError("M42 M9/M40 hypothesis revision mismatch")
    if (
        selection.decision != "selected"
        or selection.selected_intervention_ref is None
    ):
        raise ValueError("M42 requires an exact selected M9 intervention")
    exact_intervention_ref = _intervention_ref(intervention)
    if selection.selected_intervention_ref != exact_intervention_ref:
        raise ValueError("M42 selected M9 intervention identity mismatch")
    if proposal.selected_intervention_ids != (intervention.intervention_id,):
        raise ValueError("M42 M40 selected-intervention identity mismatch")
    for candidate in candidate_positions:
        validate_transfer_position_candidate(candidate)
    ids = tuple(item.candidate_id for item in candidate_positions)
    if len(set(ids)) != len(ids):
        raise ValueError("M42 candidate pool must be unique")
    if ontology is not None:
        for concept_id in proposal.concept_ids:
            ontology.get(concept_id)
        for candidate in candidate_positions:
            for concept_id in candidate.concept_ids:
                ontology.get(concept_id)
    reuse_keys = set(practice_position_reuse_keys)
    eligible = tuple(
        sorted(
            (
                item
                for item in candidate_positions
                if _eligible(
                    item,
                    transfer_kind=transfer_kind,
                    policy=policy,
                    practice_reuse_keys=reuse_keys,
                )
            ),
            key=lambda item: _rank_key(item, transfer_kind),
        )
    )
    selected = None if not eligible else eligible[0]
    blocking = (
        ()
        if selected is not None
        else (
            "No fresh eligible position satisfies the bounded "
            "transfer-policy constraints.",
        )
    )
    planning_status: TransferPlanningStatus = (
        "planned" if selected is not None else "no_eligible_candidate"
    )
    exercise_ids = tuple(item.exercise_id for item in intervention.exercises)
    payload = {
        "schema_version": TRANSFER_RETEST_PLAN_SCHEMA_VERSION,
        "participant_id": next_session_plan.participant_id,
        "hypothesis_id": proposal.hypothesis_id,
        "hypothesis_revision_ref": proposal.hypothesis_revision_ref.to_dict(),
        "next_session_plan_ref": _plan_ref(next_session_plan).to_dict(),
        "proposal_ref": _proposal_ref(proposal).to_dict(),
        "selection_ref": _selection_ref(selection).to_dict(),
        "intervention_ref": exact_intervention_ref.to_dict(),
        "transfer_kind": transfer_kind,
        "measurement_target": measurement_target,
        "target_concept_ids": list(proposal.concept_ids),
        "exercise_ids": list(exercise_ids),
        "policy_ref": policy.ref.to_dict(),
        "eligible_candidates": [item.to_dict() for item in eligible],
        "selected_candidate": (
            None if selected is None else selected.to_dict()
        ),
        "planning_status": planning_status,
        "blocking_uncertainty": list(blocking),
        "created_at": created_at,
        "plan_authority": "planning_only",
        "outcome_effect": "not_established",
        "mastery": "not_established",
    }
    fingerprint = _digest(payload)
    return TransferRetestPlan(
        transfer_plan_id=f"transfer_retest_plan_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=next_session_plan.participant_id,
        hypothesis_id=proposal.hypothesis_id,
        hypothesis_revision_ref=proposal.hypothesis_revision_ref,
        next_session_plan_ref=_plan_ref(next_session_plan),
        proposal_ref=_proposal_ref(proposal),
        selection_ref=_selection_ref(selection),
        intervention_ref=exact_intervention_ref,
        transfer_kind=transfer_kind,
        measurement_target=measurement_target,
        target_concept_ids=proposal.concept_ids,
        exercise_ids=exercise_ids,
        policy_ref=policy.ref,
        eligible_candidates=eligible,
        selected_candidate=selected,
        planning_status=planning_status,
        blocking_uncertainty=blocking,
        created_at=created_at,
    )


def validate_transfer_retest_plan(
    plan: TransferRetestPlan,
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    selection: InterventionSelectionDecision,
    intervention: TrainingInterventionDefinition,
    candidate_positions: tuple[TransferPositionCandidate, ...],
    practice_position_reuse_keys: tuple[str, ...],
    measurement_target: str,
    policy: TransferRetestPolicy,
    ontology: OntologyRegistry | None = None,
) -> None:
    expected = build_transfer_retest_plan(
        next_session_plan=next_session_plan,
        proposal=proposal,
        selection=selection,
        intervention=intervention,
        candidate_positions=candidate_positions,
        practice_position_reuse_keys=practice_position_reuse_keys,
        measurement_target=measurement_target,
        policy=policy,
        created_at=plan.created_at,
        ontology=ontology,
    )
    if expected != plan:
        raise ValueError("M42 transfer-retest plan mismatch")
