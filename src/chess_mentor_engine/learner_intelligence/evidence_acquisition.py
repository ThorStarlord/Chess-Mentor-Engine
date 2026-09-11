"""M43 bounded contradiction/control evidence-acquisition planning.

M43 consumes an exact M40 proposal, the matching M39 synthesis when present,
and additional participant-local M7B evidence links. It ranks cases worth review or
reassessment; it never classifies recurrence, mutates learner state, or establishes
mastery.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learning import HypothesisEvidenceLink, HypothesisRevisionRef

from .evidence_synthesis import (
    EvidenceSynthesisReference,
    HypothesisEvidenceSynthesis,
    HypothesisEvidenceUnitSynthesis,
)
from .next_session import NextSessionActionCandidate, NextSessionPlan

EVIDENCE_ACQUISITION_PLAN_SCHEMA_VERSION = "m43.evidence-acquisition-plan.v1"
EVIDENCE_ACQUISITION_POLICY_SCHEMA_VERSION = "m43.evidence-acquisition-policy.v1"

EvidenceAcquisitionIntent: TypeAlias = Literal[
    "challenge_hypothesis",
    "present_control",
    "collect_new_evidence",
]
EvidenceCandidateOrigin: TypeAlias = Literal[
    "current_m7c_unit",
    "additional_m7b_link",
]
EvidenceCandidateKind: TypeAlias = Literal[
    "classified_contradiction",
    "classified_successful_counterexample",
    "classified_context_exception",
    "potential_contradiction",
    "potential_successful_counterexample",
    "potential_context_exception",
    "novel_retest_context",
    "insufficiently_classified",
]
SemanticCoverage: TypeAlias = Literal["available", "unavailable"]

_SUPPORTED_ACTIONS = frozenset(
    {"CHALLENGE_HYPOTHESIS", "PRESENT_CONTROL", "COLLECT_NEW_EVIDENCE"}
)
_ACTION_TO_INTENT: dict[str, EvidenceAcquisitionIntent] = {
    "CHALLENGE_HYPOTHESIS": "challenge_hypothesis",
    "PRESENT_CONTROL": "present_control",
    "COLLECT_NEW_EVIDENCE": "collect_new_evidence",
}
_CANDIDATE_KINDS = (
    "classified_contradiction",
    "classified_successful_counterexample",
    "classified_context_exception",
    "potential_contradiction",
    "potential_successful_counterexample",
    "potential_context_exception",
    "novel_retest_context",
    "insufficiently_classified",
)
_ALLOWED_MEASUREMENT_CONDITIONS = frozenset(
    {"clean", "instrument_aware_clean", "deviating", "contaminated", "unknown"}
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


def _unique_strings(name: str, values: tuple[str, ...]) -> None:
    if any(not item for item in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} values must be unique")


@dataclass(frozen=True, slots=True)
class EvidenceAcquisitionPolicyRef:
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
class EvidenceAcquisitionPolicy:
    policy_id: str
    version: str
    fingerprint: str
    candidate_kind_priorities: tuple[tuple[EvidenceCandidateKind, int], ...]
    allowed_additional_measurement_conditions: tuple[str, ...]
    prefer_new_games: bool
    prefer_new_positions: bool
    claim_scope: str = "transparent_evidence_acquisition_ranking_policy"
    schema_version: str = EVIDENCE_ACQUISITION_POLICY_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("policy_id", self.policy_id),
            ("version", self.version),
            ("fingerprint", self.fingerprint),
        ):
            _nonempty(name, value)
        if self.schema_version != EVIDENCE_ACQUISITION_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported M43 policy schema")
        kinds = tuple(kind for kind, _ in self.candidate_kind_priorities)
        if set(kinds) != set(_CANDIDATE_KINDS) or len(kinds) != len(_CANDIDATE_KINDS):
            raise ValueError("M43 policy must define every candidate kind exactly once")
        if any(priority < 0 for _, priority in self.candidate_kind_priorities):
            raise ValueError("M43 candidate priorities must be non-negative")
        _unique_strings(
            "allowed_additional_measurement_conditions",
            self.allowed_additional_measurement_conditions,
        )
        if any(
            item not in _ALLOWED_MEASUREMENT_CONDITIONS
            for item in self.allowed_additional_measurement_conditions
        ):
            raise ValueError("unknown M43 measurement condition")
        if self.claim_scope != "transparent_evidence_acquisition_ranking_policy":
            raise ValueError("unknown M43 policy claim scope")

    def priority_for(self, kind: EvidenceCandidateKind) -> int:
        return dict(self.candidate_kind_priorities)[kind]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "version": self.version,
            "candidate_kind_priorities": [
                list(item) for item in self.candidate_kind_priorities
            ],
            "allowed_additional_measurement_conditions": list(
                self.allowed_additional_measurement_conditions
            ),
            "prefer_new_games": self.prefer_new_games,
            "prefer_new_positions": self.prefer_new_positions,
            "claim_scope": self.claim_scope,
        }

    @property
    def ref(self) -> EvidenceAcquisitionPolicyRef:
        return EvidenceAcquisitionPolicyRef(
            policy_id=self.policy_id,
            version=self.version,
            fingerprint=self.fingerprint,
        )


@dataclass(frozen=True, slots=True)
class EvidenceAcquisitionCandidate:
    source_ref: EvidenceSynthesisReference
    origin: EvidenceCandidateOrigin
    source_position_id: str
    source_game_id: str
    independence_unit_id: str
    upstream_relation: str
    candidate_kind: EvidenceCandidateKind
    policy_priority: int
    new_game: bool
    new_position: bool
    link_ref_ids: tuple[str, ...]
    context_ref_ids: tuple[str, ...]
    measurement_conditions: tuple[str, ...]
    concept_ids: tuple[str, ...]
    semantic_coverage: SemanticCoverage
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("independence_unit_id", self.independence_unit_id),
            ("upstream_relation", self.upstream_relation),
        ):
            _nonempty(name, value)
        if self.origin not in {"current_m7c_unit", "additional_m7b_link"}:
            raise ValueError("unknown M43 candidate origin")
        if self.candidate_kind not in _CANDIDATE_KINDS:
            raise ValueError("unknown M43 candidate kind")
        if self.policy_priority < 0:
            raise ValueError("M43 candidate priority must be non-negative")
        if self.semantic_coverage not in {"available", "unavailable"}:
            raise ValueError("unknown M43 semantic coverage state")
        for name, values in (
            ("link_ref_ids", self.link_ref_ids),
            ("context_ref_ids", self.context_ref_ids),
            ("measurement_conditions", self.measurement_conditions),
            ("concept_ids", self.concept_ids),
            ("reasons", self.reasons),
        ):
            _unique_strings(name, values)
        if not self.link_ref_ids:
            raise ValueError("M43 candidate requires at least one evidence-link ref")
        if not self.measurement_conditions:
            raise ValueError("M43 candidate requires measurement conditions")
        if not self.reasons:
            raise ValueError("M43 candidate requires ranking reasons")
        if self.semantic_coverage == "available" and not self.concept_ids:
            raise ValueError("available M43 semantic coverage requires concept IDs")
        if self.semantic_coverage == "unavailable" and self.concept_ids:
            raise ValueError("unavailable M43 semantic coverage cannot carry concepts")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_ref": self.source_ref.to_dict(),
            "origin": self.origin,
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "independence_unit_id": self.independence_unit_id,
            "upstream_relation": self.upstream_relation,
            "candidate_kind": self.candidate_kind,
            "policy_priority": self.policy_priority,
            "new_game": self.new_game,
            "new_position": self.new_position,
            "link_ref_ids": list(self.link_ref_ids),
            "context_ref_ids": list(self.context_ref_ids),
            "measurement_conditions": list(self.measurement_conditions),
            "concept_ids": list(self.concept_ids),
            "semantic_coverage": self.semantic_coverage,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class EvidenceAcquisitionPlan:
    acquisition_plan_id: str
    fingerprint: str
    participant_id: str
    hypothesis_id: str
    hypothesis_revision_ref: HypothesisRevisionRef
    next_session_plan_ref: EvidenceSynthesisReference
    proposal_ref: EvidenceSynthesisReference
    synthesis_ref: EvidenceSynthesisReference | None
    intent: EvidenceAcquisitionIntent
    policy_ref: EvidenceAcquisitionPolicyRef
    candidate_pool_count: int
    excluded_candidate_count: int
    candidates: tuple[EvidenceAcquisitionCandidate, ...]
    selected_candidate: EvidenceAcquisitionCandidate | None
    search_gaps: tuple[str, ...]
    created_at: str
    decision_authority: Literal["candidate_only"] = "candidate_only"
    claim_scope: str = "participant_specific_evidence_acquisition_candidates"
    m7c_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: str = EVIDENCE_ACQUISITION_PLAN_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name, value in (
            ("acquisition_plan_id", self.acquisition_plan_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("hypothesis_id", self.hypothesis_id),
        ):
            _nonempty(name, value)
        _timestamp("created_at", self.created_at)
        if self.schema_version != EVIDENCE_ACQUISITION_PLAN_SCHEMA_VERSION:
            raise ValueError("unsupported M43 acquisition-plan schema")
        if self.intent not in set(_ACTION_TO_INTENT.values()):
            raise ValueError("unknown M43 acquisition intent")
        if self.candidate_pool_count < 0 or self.excluded_candidate_count < 0:
            raise ValueError("M43 candidate counts must be non-negative")
        candidate_refs = tuple(item.source_ref.ref_id for item in self.candidates)
        if len(set(candidate_refs)) != len(candidate_refs):
            raise ValueError("M43 candidate source refs must be unique")
        if self.candidates:
            if self.selected_candidate != self.candidates[0]:
                raise ValueError("M43 selected candidate must lead ranked candidates")
        elif self.selected_candidate is not None:
            raise ValueError("M43 empty candidate set cannot select a candidate")
        _unique_strings("search_gaps", self.search_gaps)
        if self.decision_authority != "candidate_only":
            raise ValueError("M43 cannot grant M7C or execution authority")
        if self.claim_scope != "participant_specific_evidence_acquisition_candidates":
            raise ValueError("unknown M43 claim scope")
        if self.m7c_effect != "not_established" or self.mastery != "not_established":
            raise ValueError("M43 cannot establish M7C effect or mastery")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "next_session_plan_ref": self.next_session_plan_ref.to_dict(),
            "proposal_ref": self.proposal_ref.to_dict(),
            "synthesis_ref": (
                None if self.synthesis_ref is None else self.synthesis_ref.to_dict()
            ),
            "intent": self.intent,
            "policy_ref": self.policy_ref.to_dict(),
            "candidate_pool_count": self.candidate_pool_count,
            "excluded_candidate_count": self.excluded_candidate_count,
            "candidates": [item.to_dict() for item in self.candidates],
            "selected_candidate": (
                None
                if self.selected_candidate is None
                else self.selected_candidate.to_dict()
            ),
            "search_gaps": list(self.search_gaps),
            "created_at": self.created_at,
            "decision_authority": self.decision_authority,
            "claim_scope": self.claim_scope,
            "m7c_effect": self.m7c_effect,
            "mastery": self.mastery,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "acquisition_plan_id": self.acquisition_plan_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_default_evidence_acquisition_policy() -> EvidenceAcquisitionPolicy:
    priorities: tuple[tuple[EvidenceCandidateKind, int], ...] = (
        ("classified_contradiction", 110),
        ("classified_successful_counterexample", 105),
        ("classified_context_exception", 100),
        ("potential_contradiction", 95),
        ("potential_successful_counterexample", 90),
        ("potential_context_exception", 85),
        ("insufficiently_classified", 60),
        ("novel_retest_context", 50),
    )
    payload = {
        "schema_version": EVIDENCE_ACQUISITION_POLICY_SCHEMA_VERSION,
        "policy_id": "m43.default-evidence-acquisition-policy",
        "version": "1",
        "candidate_kind_priorities": [list(item) for item in priorities],
        "allowed_additional_measurement_conditions": [
            "clean",
            "instrument_aware_clean",
            "deviating",
            "unknown",
        ],
        "prefer_new_games": True,
        "prefer_new_positions": True,
        "claim_scope": "transparent_evidence_acquisition_ranking_policy",
    }
    return EvidenceAcquisitionPolicy(
        policy_id=payload["policy_id"],
        version=payload["version"],
        fingerprint=_digest(payload),
        candidate_kind_priorities=priorities,
        allowed_additional_measurement_conditions=(
            "clean",
            "instrument_aware_clean",
            "deviating",
            "unknown",
        ),
        prefer_new_games=True,
        prefer_new_positions=True,
    )


def validate_evidence_acquisition_policy(policy: EvidenceAcquisitionPolicy) -> None:
    if _digest(policy.identity_payload()) != policy.fingerprint:
        raise ValueError("M43 evidence-acquisition policy fingerprint mismatch")


def _plan_ref(plan: NextSessionPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="next_session_plan",
        ref_id=plan.plan_id,
        fingerprint=plan.fingerprint,
    )


def _proposal_ref(
    proposal: NextSessionActionCandidate,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="next_session_action_candidate",
        ref_id=(
            f"{proposal.hypothesis_id}:"
            f"{proposal.hypothesis_revision_ref.revision_id}:{proposal.action}"
        ),
        fingerprint=_digest(proposal.to_dict()),
    )


def _synthesis_ref(
    synthesis: HypothesisEvidenceSynthesis,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        kind="hypothesis_evidence_synthesis",
        ref_id=synthesis.synthesis_id,
        fingerprint=synthesis.fingerprint,
    )


def _kind_for_current_unit(relation: str) -> EvidenceCandidateKind | None:
    return {
        "contradicts": "classified_contradiction",
        "successful_counterexample": "classified_successful_counterexample",
        "context_exception": "classified_context_exception",
    }.get(relation)


def _kind_for_additional_link(
    relation: str,
    *,
    intent: EvidenceAcquisitionIntent,
) -> EvidenceCandidateKind | None:
    mapped: dict[str, EvidenceCandidateKind] = {
        "contradicts": "potential_contradiction",
        "successful_counterexample": "potential_successful_counterexample",
        "context_exception": "potential_context_exception",
        "unclear": "insufficiently_classified",
    }
    if relation in mapped:
        return mapped[relation]
    if relation == "supports" and intent == "collect_new_evidence":
        return "novel_retest_context"
    return None


def _candidate_from_current_unit(
    *,
    unit: HypothesisEvidenceUnitSynthesis,
    policy: EvidenceAcquisitionPolicy,
) -> EvidenceAcquisitionCandidate | None:
    kind = _kind_for_current_unit(unit.relation)
    if kind is None:
        return None
    concepts = tuple(sorted(unit.concept_ids))
    return EvidenceAcquisitionCandidate(
        source_ref=EvidenceSynthesisReference(
            kind="m39_recurrence_unit",
            ref_id=unit.recurrence_unit_id,
            fingerprint=_digest(unit.to_dict()),
        ),
        origin="current_m7c_unit",
        source_position_id=unit.source_position_id,
        source_game_id=unit.source_game_id,
        independence_unit_id=unit.independence_unit_id,
        upstream_relation=unit.relation,
        candidate_kind=kind,
        policy_priority=policy.priority_for(kind),
        new_game=False,
        new_position=False,
        link_ref_ids=tuple(item.link_id for item in unit.link_refs),
        context_ref_ids=unit.context_ref_ids,
        measurement_conditions=unit.measurement_conditions,
        concept_ids=concepts,
        semantic_coverage="available" if concepts else "unavailable",
        reasons=(
            "This case already has an M7C challenge/control relation in the exact "
            "M39 synthesis and can be presented without reclassifying it.",
        ),
    )


def _candidate_from_additional_link(
    *,
    link: HypothesisEvidenceLink,
    intent: EvidenceAcquisitionIntent,
    policy: EvidenceAcquisitionPolicy,
    current_positions: set[str],
    current_games: set[str],
) -> EvidenceAcquisitionCandidate | None:
    kind = _kind_for_additional_link(link.relation, intent=intent)
    if kind is None:
        return None
    new_game = link.source_game_id not in current_games
    new_position = link.source_position_id not in current_positions
    reasons = [
        "This M7B evidence link is not part of the exact M39 synthesis and is a "
        "candidate for explicit review or future M7C reassessment."
    ]
    if new_game:
        reasons.append(
            "The source game is independent of games in the current synthesis."
        )
    if new_position:
        reasons.append(
            "The source position is not already represented in the synthesis."
        )
    return EvidenceAcquisitionCandidate(
        source_ref=EvidenceSynthesisReference(
            kind="hypothesis_evidence_link",
            ref_id=link.link_id,
            fingerprint=link.fingerprint,
        ),
        origin="additional_m7b_link",
        source_position_id=link.source_position_id,
        source_game_id=link.source_game_id,
        independence_unit_id=link.source_game_id,
        upstream_relation=link.relation,
        candidate_kind=kind,
        policy_priority=policy.priority_for(kind),
        new_game=new_game,
        new_position=new_position,
        link_ref_ids=(link.link_id,),
        context_ref_ids=tuple(item.ref_id for item in link.context_refs),
        measurement_conditions=(link.measurement_condition,),
        concept_ids=(),
        semantic_coverage="unavailable",
        reasons=tuple(reasons),
    )


def _validate_inputs(
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis | None,
    additional_links: tuple[HypothesisEvidenceLink, ...],
) -> None:
    if proposal not in next_session_plan.candidates:
        raise ValueError("M43 proposal is not contained in the exact M40 plan")
    if proposal.action not in _SUPPORTED_ACTIONS:
        raise ValueError("M43 cannot consume this M40 action")
    if proposal.synthesis_ref is None:
        if synthesis is not None:
            raise ValueError("M43 synthesis supplied for proposal without M39 source")
    else:
        if synthesis is None:
            raise ValueError("M43 requires the exact M39 synthesis for this proposal")
        if _synthesis_ref(synthesis) != proposal.synthesis_ref:
            raise ValueError("M43 M39 synthesis/proposal identity mismatch")
        if synthesis.participant_id != next_session_plan.participant_id:
            raise ValueError("M43 M39 synthesis participant mismatch")
        if synthesis.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
            raise ValueError("M43 M39 synthesis/current-revision mismatch")
    seen_link_ids: set[str] = set()
    for link in additional_links:
        if link.link_id in seen_link_ids:
            raise ValueError("M43 additional evidence links must be unique")
        seen_link_ids.add(link.link_id)
        if link.participant_id != next_session_plan.participant_id:
            raise ValueError("M43 additional evidence participant mismatch")
        if link.hypothesis_revision_ref != proposal.hypothesis_revision_ref:
            raise ValueError("M43 additional evidence/current-revision mismatch")


def build_evidence_acquisition_plan(
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis | None,
    additional_links: tuple[HypothesisEvidenceLink, ...],
    policy: EvidenceAcquisitionPolicy,
    created_at: str,
) -> EvidenceAcquisitionPlan:
    """Rank exact participant-local cases without changing M7C authority."""
    _timestamp("created_at", created_at)
    validate_evidence_acquisition_policy(policy)
    _validate_inputs(
        next_session_plan=next_session_plan,
        proposal=proposal,
        synthesis=synthesis,
        additional_links=additional_links,
    )
    intent = _ACTION_TO_INTENT[proposal.action]
    current_positions = set(() if synthesis is None else synthesis.source_position_ids)
    current_games = set(() if synthesis is None else synthesis.source_game_ids)
    current_link_ids = {
        link.link_id
        for unit in (() if synthesis is None else synthesis.units)
        for link in unit.link_refs
    }

    candidates: list[EvidenceAcquisitionCandidate] = []
    excluded = 0
    if synthesis is not None and intent == "present_control":
        for unit in synthesis.units:
            candidate = _candidate_from_current_unit(unit=unit, policy=policy)
            if candidate is not None:
                candidates.append(candidate)

    allowed = set(policy.allowed_additional_measurement_conditions)
    for link in additional_links:
        duplicate = (
            link.link_id in current_link_ids
            or link.source_position_id in current_positions
        )
        if duplicate or link.measurement_condition not in allowed:
            excluded += 1
            continue
        candidate = _candidate_from_additional_link(
            link=link,
            intent=intent,
            policy=policy,
            current_positions=current_positions,
            current_games=current_games,
        )
        if candidate is None:
            excluded += 1
            continue
        candidates.append(candidate)

    ranked = tuple(
        sorted(
            candidates,
            key=lambda item: (
                -item.policy_priority,
                -int(item.new_game) if policy.prefer_new_games else 0,
                -int(item.new_position) if policy.prefer_new_positions else 0,
                item.source_game_id,
                item.source_position_id,
                item.source_ref.ref_id,
            ),
        )
    )
    gaps: list[str] = []
    if excluded:
        gaps.append(
            f"{excluded} candidate source(s) were excluded by deduplication, "
            "measurement-condition, or action-relevance rules."
        )
    if not ranked:
        gaps.append(
            "No eligible participant-local evidence candidate is currently available "
            "for this M40 acquisition intent."
        )
    if any(item.semantic_coverage == "unavailable" for item in ranked):
        gaps.append(
            "One or more candidates lack K7 semantic coverage; missing ontology "
            "coverage is not negative concept evidence."
        )

    synthesis_ref = None if synthesis is None else _synthesis_ref(synthesis)
    payload = {
        "schema_version": EVIDENCE_ACQUISITION_PLAN_SCHEMA_VERSION,
        "participant_id": next_session_plan.participant_id,
        "hypothesis_id": proposal.hypothesis_id,
        "hypothesis_revision_ref": proposal.hypothesis_revision_ref.to_dict(),
        "next_session_plan_ref": _plan_ref(next_session_plan).to_dict(),
        "proposal_ref": _proposal_ref(proposal).to_dict(),
        "synthesis_ref": None if synthesis_ref is None else synthesis_ref.to_dict(),
        "intent": intent,
        "policy_ref": policy.ref.to_dict(),
        "candidate_pool_count": len(additional_links),
        "excluded_candidate_count": excluded,
        "candidates": [item.to_dict() for item in ranked],
        "selected_candidate": None if not ranked else ranked[0].to_dict(),
        "search_gaps": gaps,
        "created_at": created_at,
        "decision_authority": "candidate_only",
        "claim_scope": "participant_specific_evidence_acquisition_candidates",
        "m7c_effect": "not_established",
        "mastery": "not_established",
    }
    digest = _digest(payload)
    return EvidenceAcquisitionPlan(
        acquisition_plan_id=f"evidence_acquisition_plan_{digest[:20]}",
        fingerprint=digest,
        participant_id=next_session_plan.participant_id,
        hypothesis_id=proposal.hypothesis_id,
        hypothesis_revision_ref=proposal.hypothesis_revision_ref,
        next_session_plan_ref=_plan_ref(next_session_plan),
        proposal_ref=_proposal_ref(proposal),
        synthesis_ref=synthesis_ref,
        intent=intent,
        policy_ref=policy.ref,
        candidate_pool_count=len(additional_links),
        excluded_candidate_count=excluded,
        candidates=ranked,
        selected_candidate=None if not ranked else ranked[0],
        search_gaps=tuple(gaps),
        created_at=created_at,
    )


def validate_evidence_acquisition_plan(
    plan: EvidenceAcquisitionPlan,
    *,
    next_session_plan: NextSessionPlan,
    proposal: NextSessionActionCandidate,
    synthesis: HypothesisEvidenceSynthesis | None,
    additional_links: tuple[HypothesisEvidenceLink, ...],
    policy: EvidenceAcquisitionPolicy,
) -> None:
    expected = build_evidence_acquisition_plan(
        next_session_plan=next_session_plan,
        proposal=proposal,
        synthesis=synthesis,
        additional_links=additional_links,
        policy=policy,
        created_at=plan.created_at,
    )
    if expected != plan:
        raise ValueError("M43 evidence-acquisition plan mismatch")
