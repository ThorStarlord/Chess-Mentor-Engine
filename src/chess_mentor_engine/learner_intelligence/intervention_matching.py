"""M41 ontology-aware candidate matching before M9 selection authority."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.learning import HypothesisRevisionRef
from chess_mentor_engine.training import (
    InterventionRegistry,
    TrainingContentProvenance,
    TrainingInterventionDefinition,
    TrainingInterventionRef,
)

from .evidence_synthesis import (
    EvidenceSynthesisReference,
    HypothesisEvidenceSynthesis,
)
from .next_session import NextSessionActionCandidate, NextSessionPlan

INTERVENTION_SEMANTIC_PROFILE_SCHEMA_VERSION = (
    "m41.intervention-semantic-profile.v1"
)
INTERVENTION_MATCHING_POLICY_SCHEMA_VERSION = "m41.intervention-matching-policy.v1"
INTERVENTION_CANDIDATE_SET_SCHEMA_VERSION = "m41.intervention-candidate-set.v1"

InterventionMatchStatus: TypeAlias = Literal[
    "eligible_candidate",
    "possible_candidate",
    "insufficient_information",
    "ineligible",
]

_MATCH_STATUSES = (
    "eligible_candidate",
    "possible_candidate",
    "insufficient_information",
    "ineligible",
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


def _unique(name: str, values: tuple[str, ...]) -> None:
    if any(not value for value in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} values must be unique")


def _intervention_ref(
    intervention: TrainingInterventionDefinition,
) -> TrainingInterventionRef:
    return TrainingInterventionRef(
        intervention_id=intervention.intervention_id,
        intervention_key=intervention.intervention_key,
        version=intervention.version,
        fingerprint=intervention.fingerprint,
    )


def _validate_intervention(intervention: TrainingInterventionDefinition) -> None:
    expected = _digest(intervention.to_dict(include_identity=False))
    if intervention.fingerprint != expected:
        raise ValueError("M41 intervention fingerprint mismatch")
    if intervention.intervention_id != f"training_intervention_{expected[:20]}":
        raise ValueError("M41 intervention identity mismatch")


def _validate_registry(registry: InterventionRegistry) -> None:
    for intervention in registry.interventions:
        _validate_intervention(intervention)
    expected = _digest(registry.to_dict(include_identity=False))
    if registry.fingerprint != expected:
        raise ValueError("M41 intervention registry fingerprint mismatch")
    if registry.registry_id != f"intervention_registry_{expected[:20]}":
        raise ValueError("M41 intervention registry identity mismatch")


def _validate_concepts(
    ontology: OntologyRegistry,
    concept_ids: tuple[str, ...],
) -> None:
    _unique("concept_ids", concept_ids)
    for concept_id in concept_ids:
        ontology.get(concept_id)


@dataclass(frozen=True, slots=True)
class InterventionSemanticProfileRef:
    profile_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _nonempty("profile_id", self.profile_id)
        _nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "profile_id": self.profile_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class InterventionSemanticProfile:
    profile_id: str
    fingerprint: str
    intervention_ref: TrainingInterventionRef
    ontology_fingerprint: str
    target_concept_ids: tuple[str, ...]
    reinforce_concept_ids: tuple[str, ...]
    contraindicated_concept_ids: tuple[str, ...]
    training_modes: tuple[str, ...]
    provenance: TrainingContentProvenance
    created_at: str
    schema_version: str = INTERVENTION_SEMANTIC_PROFILE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("profile_id", self.profile_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("ontology_fingerprint", self.ontology_fingerprint)
        _timestamp("created_at", self.created_at)
        if self.schema_version != INTERVENTION_SEMANTIC_PROFILE_SCHEMA_VERSION:
            raise ValueError("unsupported M41 semantic-profile schema")
        for name, values in (
            ("target_concept_ids", self.target_concept_ids),
            ("reinforce_concept_ids", self.reinforce_concept_ids),
            ("contraindicated_concept_ids", self.contraindicated_concept_ids),
            ("training_modes", self.training_modes),
        ):
            _unique(name, values)
        positive = set(self.target_concept_ids) | set(self.reinforce_concept_ids)
        if positive & set(self.contraindicated_concept_ids):
            raise ValueError("M41 semantic profile has conflicting concept roles")
        has_no_signal = (
            not positive
            and not self.contraindicated_concept_ids
            and not self.training_modes
        )
        if has_no_signal:
            raise ValueError("M41 semantic profile must describe at least one signal")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "intervention_ref": self.intervention_ref.to_dict(),
            "ontology_fingerprint": self.ontology_fingerprint,
            "target_concept_ids": list(self.target_concept_ids),
            "reinforce_concept_ids": list(self.reinforce_concept_ids),
            "contraindicated_concept_ids": list(self.contraindicated_concept_ids),
            "training_modes": list(self.training_modes),
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at,
        }

    @property
    def ref(self) -> InterventionSemanticProfileRef:
        return InterventionSemanticProfileRef(self.profile_id, self.fingerprint)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


@dataclass(frozen=True, slots=True)
class InterventionMatchingPolicyRef:
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
class InterventionMatchingPolicy:
    policy_id: str
    version: str
    fingerprint: str
    status_order: tuple[InterventionMatchStatus, ...]
    prefer_target_concept_overlap: bool
    prefer_training_mode_overlap: bool
    prefer_reinforcement_overlap: bool
    claim_scope: str = "transparent_intervention_candidate_ranking_policy"
    schema_version: str = INTERVENTION_MATCHING_POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _nonempty(name, value)
        if self.schema_version != INTERVENTION_MATCHING_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported M41 matching-policy schema")
        if tuple(self.status_order) != _MATCH_STATUSES:
            raise ValueError("M41 policy must preserve the qualified status order")
        if self.claim_scope != "transparent_intervention_candidate_ranking_policy":
            raise ValueError("unknown M41 policy claim scope")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "status_order": list(self.status_order),
            "prefer_target_concept_overlap": self.prefer_target_concept_overlap,
            "prefer_training_mode_overlap": self.prefer_training_mode_overlap,
            "prefer_reinforcement_overlap": self.prefer_reinforcement_overlap,
            "claim_scope": self.claim_scope,
        }

    @property
    def ref(self) -> InterventionMatchingPolicyRef:
        return InterventionMatchingPolicyRef(
            self.policy_id,
            self.version,
            self.fingerprint,
        )


@dataclass(frozen=True, slots=True)
class InterventionCandidate:
    intervention_ref: TrainingInterventionRef
    profile_ref: InterventionSemanticProfileRef | None
    status: InterventionMatchStatus
    target_concept_matches: tuple[str, ...]
    reinforcement_matches: tuple[str, ...]
    contraindication_matches: tuple[str, ...]
    training_mode_matches: tuple[str, ...]
    unverified_prerequisites: tuple[str, ...]
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in _MATCH_STATUSES:
            raise ValueError("unknown M41 intervention match status")
        for name, values in (
            ("target_concept_matches", self.target_concept_matches),
            ("reinforcement_matches", self.reinforcement_matches),
            ("contraindication_matches", self.contraindication_matches),
            ("training_mode_matches", self.training_mode_matches),
            ("unverified_prerequisites", self.unverified_prerequisites),
            ("reasons", self.reasons),
        ):
            _unique(name, values)
        if not self.reasons:
            raise ValueError("M41 candidate requires explicit reasons")
        if self.status == "insufficient_information" and self.profile_ref is not None:
            raise ValueError("M41 insufficient candidate must identify missing profile")

    def to_dict(self) -> dict[str, Any]:
        return {
            "intervention_ref": self.intervention_ref.to_dict(),
            "profile_ref": (
                None if self.profile_ref is None else self.profile_ref.to_dict()
            ),
            "status": self.status,
            "target_concept_matches": list(self.target_concept_matches),
            "reinforcement_matches": list(self.reinforcement_matches),
            "contraindication_matches": list(self.contraindication_matches),
            "training_mode_matches": list(self.training_mode_matches),
            "unverified_prerequisites": list(self.unverified_prerequisites),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class InterventionCandidateSet:
    candidate_set_id: str
    fingerprint: str
    participant_id: str
    hypothesis_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    next_session_plan_ref: EvidenceSynthesisReference
    proposal_ref: EvidenceSynthesisReference
    synthesis_ref: EvidenceSynthesisReference
    ontology_fingerprint: str
    intervention_registry_ref: EvidenceSynthesisReference
    policy_ref: InterventionMatchingPolicyRef
    target_concept_ids: tuple[str, ...]
    target_training_modes: tuple[str, ...]
    unverified_prerequisites: tuple[str, ...]
    ranked_candidates: tuple[InterventionCandidate, ...]
    matching_gaps: tuple[str, ...]
    created_at: str
    selection_authority: Literal["not_exercised"] = "not_exercised"
    efficacy: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = INTERVENTION_CANDIDATE_SET_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("candidate_set_id", self.candidate_set_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("hypothesis_id", self.hypothesis_id),
            ("ontology_fingerprint", self.ontology_fingerprint),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != INTERVENTION_CANDIDATE_SET_SCHEMA_VERSION:
            raise ValueError("unsupported M41 candidate-set schema")
        for name, values in (
            ("target_concept_ids", self.target_concept_ids),
            ("target_training_modes", self.target_training_modes),
            ("unverified_prerequisites", self.unverified_prerequisites),
            ("matching_gaps", self.matching_gaps),
        ):
            _unique(name, values)
        keys = tuple(
            item.intervention_ref.intervention_key
            for item in self.ranked_candidates
        )
        if len(set(keys)) != len(keys):
            raise ValueError("M41 candidate interventions must be unique")
        if self.selection_authority != "not_exercised":
            raise ValueError("M41 cannot exercise M9 selection authority")
        if self.efficacy != "not_established" or self.mastery != "not_established":
            raise ValueError("M41 cannot establish efficacy or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "next_session_plan_ref": self.next_session_plan_ref.to_dict(),
            "proposal_ref": self.proposal_ref.to_dict(),
            "synthesis_ref": self.synthesis_ref.to_dict(),
            "ontology_fingerprint": self.ontology_fingerprint,
            "intervention_registry_ref": self.intervention_registry_ref.to_dict(),
            "policy_ref": self.policy_ref.to_dict(),
            "target_concept_ids": list(self.target_concept_ids),
            "target_training_modes": list(self.target_training_modes),
            "unverified_prerequisites": list(self.unverified_prerequisites),
            "ranked_candidates": [item.to_dict() for item in self.ranked_candidates],
            "matching_gaps": list(self.matching_gaps),
            "created_at": self.created_at,
            "selection_authority": self.selection_authority,
            "efficacy": self.efficacy,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_set_id": self.candidate_set_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def define_intervention_semantic_profile(
    *,
    intervention: TrainingInterventionDefinition,
    ontology: OntologyRegistry,
    target_concept_ids: tuple[str, ...],
    reinforce_concept_ids: tuple[str, ...] = (),
    contraindicated_concept_ids: tuple[str, ...] = (),
    training_modes: tuple[str, ...] = (),
    provenance: TrainingContentProvenance,
    created_at: str,
) -> InterventionSemanticProfile:
    """Attach explicit semantic metadata without changing the M9 definition."""
    _validate_intervention(intervention)
    _timestamp("created_at", created_at)
    for concept_ids in (
        target_concept_ids,
        reinforce_concept_ids,
        contraindicated_concept_ids,
    ):
        _validate_concepts(ontology, concept_ids)
    target = tuple(sorted(target_concept_ids))
    reinforce = tuple(sorted(reinforce_concept_ids))
    contraindicated = tuple(sorted(contraindicated_concept_ids))
    modes = tuple(sorted(training_modes))
    payload = {
        "schema_version": INTERVENTION_SEMANTIC_PROFILE_SCHEMA_VERSION,
        "intervention_ref": _intervention_ref(intervention).to_dict(),
        "ontology_fingerprint": ontology.fingerprint,
        "target_concept_ids": list(target),
        "reinforce_concept_ids": list(reinforce),
        "contraindicated_concept_ids": list(contraindicated),
        "training_modes": list(modes),
        "provenance": provenance.to_dict(),
        "created_at": created_at,
    }
    fingerprint = _digest(payload)
    return InterventionSemanticProfile(
        profile_id=f"intervention_semantic_profile_{fingerprint[:20]}",
        fingerprint=fingerprint,
        intervention_ref=_intervention_ref(intervention),
        ontology_fingerprint=ontology.fingerprint,
        target_concept_ids=target,
        reinforce_concept_ids=reinforce,
        contraindicated_concept_ids=contraindicated,
        training_modes=modes,
        provenance=provenance,
        created_at=created_at,
    )


def validate_intervention_semantic_profile(
    profile: InterventionSemanticProfile,
    *,
    intervention: TrainingInterventionDefinition,
    ontology: OntologyRegistry,
) -> None:
    expected = define_intervention_semantic_profile(
        intervention=intervention,
        ontology=ontology,
        target_concept_ids=profile.target_concept_ids,
        reinforce_concept_ids=profile.reinforce_concept_ids,
        contraindicated_concept_ids=profile.contraindicated_concept_ids,
        training_modes=profile.training_modes,
        provenance=profile.provenance,
        created_at=profile.created_at,
    )
    if expected != profile:
        raise ValueError("M41 intervention semantic profile mismatch")


def build_default_intervention_matching_policy() -> InterventionMatchingPolicy:
    payload = {
        "schema_version": INTERVENTION_MATCHING_POLICY_SCHEMA_VERSION,
        "policy_id": "m41.default-intervention-matching-policy",
        "version": "1",
        "status_order": list(_MATCH_STATUSES),
        "prefer_target_concept_overlap": True,
        "prefer_training_mode_overlap": True,
        "prefer_reinforcement_overlap": True,
        "claim_scope": "transparent_intervention_candidate_ranking_policy",
    }
    return InterventionMatchingPolicy(
        policy_id=payload["policy_id"],
        version=payload["version"],
        fingerprint=_digest(payload),
        status_order=_MATCH_STATUSES,
        prefer_target_concept_overlap=True,
        prefer_training_mode_overlap=True,
        prefer_reinforcement_overlap=True,
    )


def validate_intervention_matching_policy(policy: InterventionMatchingPolicy) -> None:
    if _digest(policy.identity_payload()) != policy.fingerprint:
        raise ValueError("M41 intervention-matching policy fingerprint mismatch")


def _plan_ref(plan: NextSessionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_plan",
        plan.plan_id,
        plan.fingerprint,
    )


def _proposal_ref(proposal: NextSessionActionCandidate) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "next_session_action_candidate",
        (
            f"{proposal.hypothesis_id}:"
            f"{proposal.hypothesis_revision_ref.revision_id}:{proposal.action}"
        ),
        _digest(proposal.to_dict()),
    )


def _synthesis_ref(
    synthesis: HypothesisEvidenceSynthesis,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "hypothesis_evidence_synthesis",
        synthesis.synthesis_id,
        synthesis.fingerprint,
    )


def _registry_ref(registry: InterventionRegistry) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "intervention_registry",
        registry.registry_id,
        registry.fingerprint,
    )


def _target_pedagogy(
    ontology: OntologyRegistry,
    concept_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    modes: set[str] = set()
    prerequisites: set[str] = set()
    for concept_id in concept_ids:
        concept = ontology.get(concept_id)
        if concept.pedagogy is None:
            continue
        modes.update(concept.pedagogy.training_modes)
        prerequisites.update(concept.pedagogy.prerequisites)
    return tuple(sorted(modes)), tuple(sorted(prerequisites))


def _candidate(
    intervention: TrainingInterventionDefinition,
    profile: InterventionSemanticProfile | None,
    *,
    target_concepts: set[str],
    target_modes: set[str],
    prerequisites: tuple[str, ...],
) -> InterventionCandidate:
    if profile is None:
        return InterventionCandidate(
            intervention_ref=_intervention_ref(intervention),
            profile_ref=None,
            status="insufficient_information",
            target_concept_matches=(),
            reinforcement_matches=(),
            contraindication_matches=(),
            training_mode_matches=(),
            unverified_prerequisites=prerequisites,
            reasons=(
                "No exact M41 semantic profile was supplied for this registered "
                "intervention; free-text similarity is not used as a substitute.",
            ),
        )
    target_matches = tuple(sorted(target_concepts & set(profile.target_concept_ids)))
    reinforcement_matches = tuple(
        sorted(target_concepts & set(profile.reinforce_concept_ids))
    )
    contraindications = tuple(
        sorted(target_concepts & set(profile.contraindicated_concept_ids))
    )
    mode_matches = tuple(sorted(target_modes & set(profile.training_modes)))
    if contraindications:
        status: InterventionMatchStatus = "ineligible"
        reasons = (
            "The semantic profile explicitly contraindicates one or more current "
            "target concepts.",
        )
    elif target_matches:
        status = "eligible_candidate"
        reasons = (
            "The semantic profile explicitly targets at least one exact current "
            "ontology concept.",
        )
    elif reinforcement_matches or mode_matches:
        status = "possible_candidate"
        reasons = (
            "The semantic profile has reinforcement or training-mode overlap but "
            "does not explicitly target the current concept.",
        )
    else:
        status = "ineligible"
        reasons = (
            "The semantic profile has no explicit target, reinforcement, or training-"
            "mode overlap with the current teaching need.",
        )
    return InterventionCandidate(
        intervention_ref=_intervention_ref(intervention),
        profile_ref=profile.ref,
        status=status,
        target_concept_matches=target_matches,
        reinforcement_matches=reinforcement_matches,
        contraindication_matches=contraindications,
        training_mode_matches=mode_matches,
        unverified_prerequisites=prerequisites,
        reasons=reasons,
    )


def _sort_key(
    candidate: InterventionCandidate,
    policy: InterventionMatchingPolicy,
) -> tuple[int, int, int, int, str]:
    status_rank = policy.status_order.index(candidate.status)
    return (
        status_rank,
        -len(candidate.target_concept_matches)
        if policy.prefer_target_concept_overlap
        else 0,
        -len(candidate.training_mode_matches)
        if policy.prefer_training_mode_overlap
        else 0,
        -len(candidate.reinforcement_matches)
        if policy.prefer_reinforcement_overlap
        else 0,
        candidate.intervention_ref.intervention_key,
    )


def _validate_inputs(
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis,
    ontology: OntologyRegistry,
    intervention_registry: InterventionRegistry,
    profiles: tuple[InterventionSemanticProfile, ...],
) -> None:
    if proposal not in next_session_plan.candidates:
        raise ValueError("M41 proposal is not contained in the exact M40 plan")
    if proposal.action != "TEACH_CONCEPT":
        raise ValueError("M41 v1 only consumes M40 TEACH_CONCEPT proposals")
    if proposal.synthesis_ref is None:
        raise ValueError("M41 teaching proposal requires exact M39 synthesis")
    if _synthesis_ref(synthesis) != proposal.synthesis_ref:
        raise ValueError("M41 M39 synthesis/proposal identity mismatch")
    if synthesis.participant_id != next_session_plan.participant_id:
        raise ValueError("M41 M39 synthesis participant mismatch")
    if synthesis.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
        raise ValueError("M41 M39 synthesis/current-revision mismatch")
    if tuple(proposal.concept_ids) != tuple(synthesis.concept_ids):
        raise ValueError("M41 proposal/M39 concept context drift")
    _validate_registry(intervention_registry)
    intervention_by_id = {
        item.intervention_id: item for item in intervention_registry.interventions
    }
    seen: set[str] = set()
    for profile in profiles:
        intervention_id = profile.intervention_ref.intervention_id
        if intervention_id in seen:
            raise ValueError("M41 semantic profiles must be unique per intervention")
        seen.add(intervention_id)
        intervention = intervention_by_id.get(intervention_id)
        if intervention is None:
            raise ValueError(
                "M41 semantic profile references unregistered intervention"
            )
        if _intervention_ref(intervention) != profile.intervention_ref:
            raise ValueError("M41 semantic profile/intervention identity drift")
        validate_intervention_semantic_profile(
            profile,
            intervention=intervention,
            ontology=ontology,
        )


def build_intervention_candidate_set(
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis,
    ontology: OntologyRegistry,
    intervention_registry: InterventionRegistry,
    profiles: tuple[InterventionSemanticProfile, ...],
    policy: InterventionMatchingPolicy,
    created_at: str,
) -> InterventionCandidateSet:
    """Rank candidate interventions without exercising M9 selection authority."""
    _timestamp("created_at", created_at)
    validate_intervention_matching_policy(policy)
    _validate_inputs(
        next_session_plan=next_session_plan,
        proposal=proposal,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=intervention_registry,
        profiles=profiles,
    )
    target_ids = tuple(sorted(proposal.concept_ids))
    _validate_concepts(ontology, target_ids)
    target_modes, prerequisites = _target_pedagogy(ontology, target_ids)
    profile_by_id = {
        item.intervention_ref.intervention_id: item for item in profiles
    }
    candidates = tuple(
        sorted(
            (
                _candidate(
                    intervention,
                    profile_by_id.get(intervention.intervention_id),
                    target_concepts=set(target_ids),
                    target_modes=set(target_modes),
                    prerequisites=prerequisites,
                )
                for intervention in intervention_registry.interventions
            ),
            key=lambda item: _sort_key(item, policy),
        )
    )
    gaps: list[str] = []
    if not target_ids:
        gaps.append(
            "The exact M40/M39 teaching need has no ontology concept context; M41 "
            "will not infer concepts from free text."
        )
    missing_profiles = sum(item.profile_ref is None for item in candidates)
    if missing_profiles:
        gaps.append(
            f"{missing_profiles} registered intervention(s) lack exact M41 semantic "
            "profiles and remain insufficiently characterized."
        )
    if not any(item.status == "eligible_candidate" for item in candidates):
        gaps.append(
            "No intervention explicitly targets the current ontology concept set; "
            "M9 selection should not be inferred from M41 ranking."
        )
    payload = {
        "schema_version": INTERVENTION_CANDIDATE_SET_SCHEMA_VERSION,
        "participant_id": next_session_plan.participant_id,
        "hypothesis_id": proposal.hypothesis_id,
        "hypothesis_revision_ref": proposal.hypothesis_revision_ref.to_dict(),
        "next_session_plan_ref": _plan_ref(next_session_plan).to_dict(),
        "proposal_ref": _proposal_ref(proposal).to_dict(),
        "synthesis_ref": _synthesis_ref(synthesis).to_dict(),
        "ontology_fingerprint": ontology.fingerprint,
        "intervention_registry_ref": _registry_ref(intervention_registry).to_dict(),
        "policy_ref": policy.ref.to_dict(),
        "target_concept_ids": list(target_ids),
        "target_training_modes": list(target_modes),
        "unverified_prerequisites": list(prerequisites),
        "ranked_candidates": [item.to_dict() for item in candidates],
        "matching_gaps": gaps,
        "created_at": created_at,
        "selection_authority": "not_exercised",
        "efficacy": "not_established",
        "mastery": "not_established",
    }
    fingerprint = _digest(payload)
    return InterventionCandidateSet(
        candidate_set_id=f"intervention_candidate_set_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=next_session_plan.participant_id,
        hypothesis_id=proposal.hypothesis_id,
        hypothesis_revision_ref=proposal.hypothesis_revision_ref,
        next_session_plan_ref=_plan_ref(next_session_plan),
        proposal_ref=_proposal_ref(proposal),
        synthesis_ref=_synthesis_ref(synthesis),
        ontology_fingerprint=ontology.fingerprint,
        intervention_registry_ref=_registry_ref(intervention_registry),
        policy_ref=policy.ref,
        target_concept_ids=target_ids,
        target_training_modes=target_modes,
        unverified_prerequisites=prerequisites,
        ranked_candidates=candidates,
        matching_gaps=tuple(gaps),
        created_at=created_at,
    )


def validate_intervention_candidate_set(
    candidate_set: InterventionCandidateSet,
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis,
    ontology: OntologyRegistry,
    intervention_registry: InterventionRegistry,
    profiles: tuple[InterventionSemanticProfile, ...],
    policy: InterventionMatchingPolicy,
) -> None:
    expected = build_intervention_candidate_set(
        next_session_plan=next_session_plan,
        proposal=proposal,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=intervention_registry,
        profiles=profiles,
        policy=policy,
        created_at=candidate_set.created_at,
    )
    if expected != candidate_set:
        raise ValueError("M41 intervention candidate set mismatch")
