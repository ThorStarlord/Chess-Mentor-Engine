"""Immutable M7B learner-hypothesis ledger records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from .model import MeasurementCondition

HypothesisClaimKind: TypeAlias = Literal["descriptive_pattern"]
HypothesisActorKind: TypeAlias = Literal["human", "model", "system"]
HypothesisLifecycleKind: TypeAlias = Literal["retired", "superseded"]
HypothesisEvidenceRelation: TypeAlias = Literal[
    "supports",
    "contradicts",
    "successful_counterexample",
    "context_exception",
    "unclear",
]
HypothesisEvidenceBasisKind: TypeAlias = Literal[
    "deterministic_mapping",
    "coded_mapping",
]
HypothesisM6EvidenceKind: TypeAlias = Literal[
    "reasoning_context",
    "reasoning_assessment",
    "reasoning_assertion",
]


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


def _require_unique_strings(name: str, values: tuple[str, ...]) -> None:
    if any(not value for value in values):
        raise ValueError(f"{name} values must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")


@dataclass(frozen=True, slots=True)
class HypothesisActorProvenance:
    """Human/model/system provenance for an append-only M7 authoring action."""

    actor_kind: HypothesisActorKind
    actor_id: str
    actor_version: str
    rubric_or_instruction_fingerprint: str
    run_id: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("actor_id", self.actor_id),
            ("actor_version", self.actor_version),
            (
                "rubric_or_instruction_fingerprint",
                self.rubric_or_instruction_fingerprint,
            ),
        ):
            _require_nonempty(name, value)
        if self.run_id is not None:
            _require_nonempty("run_id", self.run_id)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "actor_kind": self.actor_kind,
            "actor_id": self.actor_id,
            "actor_version": self.actor_version,
            "rubric_or_instruction_fingerprint": (
                self.rubric_or_instruction_fingerprint
            ),
            "run_id": self.run_id,
        }


@dataclass(frozen=True, slots=True)
class HypothesisContextRef:
    """Exact reference to one context definition or provenance-bound context coding."""

    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("ref_id", self.ref_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {"ref_id": self.ref_id, "fingerprint": self.fingerprint}


@dataclass(frozen=True, slots=True)
class LearnerHypothesisRef:
    """Exact reference to one stable learner-hypothesis lineage."""

    hypothesis_id: str
    participant_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("hypothesis_id", self.hypothesis_id)
        _require_nonempty("participant_id", self.participant_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "participant_id": self.participant_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisRevisionRef:
    """Exact reference to one immutable hypothesis revision."""

    revision_id: str
    hypothesis_id: str
    revision_number: int
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("revision_id", self.revision_id)
        _require_nonempty("hypothesis_id", self.hypothesis_id)
        _require_nonempty("fingerprint", self.fingerprint)
        if self.revision_number <= 0:
            raise ValueError("revision_number must be positive")

    def to_dict(self) -> dict[str, str | int]:
        return {
            "revision_id": self.revision_id,
            "hypothesis_id": self.hypothesis_id,
            "revision_number": self.revision_number,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisM6EvidenceRef:
    """Exact reference to one qualified M6 context/assessment/assertion record."""

    kind: HypothesisM6EvidenceKind
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        _require_nonempty("ref_id", self.ref_id)
        _require_nonempty("fingerprint", self.fingerprint)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class HypothesisMappingProvenance:
    """Explicit provenance for mapping one M6 unit to one M7 evidence relation."""

    basis_kind: HypothesisEvidenceBasisKind
    ref_id: str
    fingerprint: str
    actor_provenance: HypothesisActorProvenance | None = None

    def __post_init__(self) -> None:
        _require_nonempty("ref_id", self.ref_id)
        _require_nonempty("fingerprint", self.fingerprint)
        if self.basis_kind == "coded_mapping" and self.actor_provenance is None:
            raise ValueError("coded_mapping requires actor provenance")

    def to_dict(self) -> dict[str, Any]:
        return {
            "basis_kind": self.basis_kind,
            "ref_id": self.ref_id,
            "fingerprint": self.fingerprint,
            "actor_provenance": (
                None
                if self.actor_provenance is None
                else self.actor_provenance.to_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class LearnerHypothesis:
    """Stable participant-specific identity for one hypothesis lineage."""

    hypothesis_id: str
    fingerprint: str
    participant_id: str
    origin_proposal_fingerprint: str
    created_at: str
    origin_provenance: HypothesisActorProvenance

    def __post_init__(self) -> None:
        for name, value in (
            ("hypothesis_id", self.hypothesis_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("origin_proposal_fingerprint", self.origin_proposal_fingerprint),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "participant_id": self.participant_id,
            "origin_proposal_fingerprint": self.origin_proposal_fingerprint,
            "created_at": self.created_at,
            "origin_provenance": self.origin_provenance.to_dict(),
        }
        if include_identity:
            payload["hypothesis_id"] = self.hypothesis_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisRevision:
    """Append-only version of one descriptive hypothesis proposition and scope."""

    revision_id: str
    fingerprint: str
    hypothesis_id: str
    revision_number: int
    statement: str
    scope_definition: str
    context_definition_refs: tuple[HypothesisContextRef, ...]
    competing_hypothesis_refs: tuple[LearnerHypothesisRef, ...]
    unresolved_alternative_notes: tuple[str, ...]
    parent_revision_ref: HypothesisRevisionRef | None
    revision_reason: str
    author_provenance: HypothesisActorProvenance
    created_at: str
    claim_kind: HypothesisClaimKind = "descriptive_pattern"

    def __post_init__(self) -> None:
        for name, value in (
            ("revision_id", self.revision_id),
            ("fingerprint", self.fingerprint),
            ("hypothesis_id", self.hypothesis_id),
            ("statement", self.statement),
            ("scope_definition", self.scope_definition),
            ("revision_reason", self.revision_reason),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.revision_number <= 0:
            raise ValueError("revision_number must be positive")
        context_ids = tuple(item.ref_id for item in self.context_definition_refs)
        if len(set(context_ids)) != len(context_ids):
            raise ValueError("context_definition_refs must be unique")
        competing_ids = tuple(
            item.hypothesis_id for item in self.competing_hypothesis_refs
        )
        if len(set(competing_ids)) != len(competing_ids):
            raise ValueError("competing_hypothesis_refs must be unique")
        _require_unique_strings(
            "unresolved_alternative_notes", self.unresolved_alternative_notes
        )
        if self.revision_number == 1 and self.parent_revision_ref is not None:
            raise ValueError("revision 1 must not have a parent revision")
        if self.revision_number > 1 and self.parent_revision_ref is None:
            raise ValueError("later revisions must cite a parent revision")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "hypothesis_id": self.hypothesis_id,
            "revision_number": self.revision_number,
            "statement": self.statement,
            "claim_kind": self.claim_kind,
            "scope_definition": self.scope_definition,
            "context_definition_refs": [
                item.to_dict() for item in self.context_definition_refs
            ],
            "competing_hypothesis_refs": [
                item.to_dict() for item in self.competing_hypothesis_refs
            ],
            "unresolved_alternative_notes": list(
                self.unresolved_alternative_notes
            ),
            "parent_revision_ref": (
                None
                if self.parent_revision_ref is None
                else self.parent_revision_ref.to_dict()
            ),
            "revision_reason": self.revision_reason,
            "author_provenance": self.author_provenance.to_dict(),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["revision_id"] = self.revision_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisLifecycleEvent:
    """Append-only explicit authority-state change for one hypothesis lineage."""

    lifecycle_event_id: str
    fingerprint: str
    hypothesis_ref: LearnerHypothesisRef
    kind: HypothesisLifecycleKind
    superseding_hypothesis_ref: LearnerHypothesisRef | None
    reason: str
    author_provenance: HypothesisActorProvenance
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("lifecycle_event_id", self.lifecycle_event_id),
            ("fingerprint", self.fingerprint),
            ("reason", self.reason),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.kind == "retired" and self.superseding_hypothesis_ref is not None:
            raise ValueError("retired event must not cite a superseding hypothesis")
        if self.kind == "superseded" and self.superseding_hypothesis_ref is None:
            raise ValueError("superseded event must cite a superseding hypothesis")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "hypothesis_ref": self.hypothesis_ref.to_dict(),
            "kind": self.kind,
            "superseding_hypothesis_ref": (
                None
                if self.superseding_hypothesis_ref is None
                else self.superseding_hypothesis_ref.to_dict()
            ),
            "reason": self.reason,
            "author_provenance": self.author_provenance.to_dict(),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["lifecycle_event_id"] = self.lifecycle_event_id
            payload["fingerprint"] = self.fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class HypothesisEvidenceLink:
    """Immutable explicit relation between a hypothesis revision and one M6 unit."""

    link_id: str
    fingerprint: str
    hypothesis_revision_ref: HypothesisRevisionRef
    participant_id: str
    reasoning_context_ref: HypothesisM6EvidenceRef
    assessment_ref: HypothesisM6EvidenceRef
    assertion_refs: tuple[HypothesisM6EvidenceRef, ...]
    source_position_id: str
    source_game_id: str
    relation: HypothesisEvidenceRelation
    context_refs: tuple[HypothesisContextRef, ...]
    measurement_condition: MeasurementCondition
    basis_kind: HypothesisEvidenceBasisKind
    mapping_provenance: HypothesisMappingProvenance
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("link_id", self.link_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("source_position_id", self.source_position_id),
            ("source_game_id", self.source_game_id),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.reasoning_context_ref.kind != "reasoning_context":
            raise ValueError("reasoning_context_ref has wrong M6 evidence kind")
        if self.assessment_ref.kind != "reasoning_assessment":
            raise ValueError("assessment_ref has wrong M6 evidence kind")
        if any(item.kind != "reasoning_assertion" for item in self.assertion_refs):
            raise ValueError("assertion_refs must contain reasoning_assertion refs")
        assertion_ids = tuple(item.ref_id for item in self.assertion_refs)
        if len(set(assertion_ids)) != len(assertion_ids):
            raise ValueError("assertion_refs must be unique")
        context_ids = tuple(item.ref_id for item in self.context_refs)
        if len(set(context_ids)) != len(context_ids):
            raise ValueError("context_refs must be unique")
        if self.mapping_provenance.basis_kind != self.basis_kind:
            raise ValueError("mapping provenance basis does not match link basis_kind")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "hypothesis_revision_ref": self.hypothesis_revision_ref.to_dict(),
            "participant_id": self.participant_id,
            "reasoning_context_ref": self.reasoning_context_ref.to_dict(),
            "assessment_ref": self.assessment_ref.to_dict(),
            "assertion_refs": [item.to_dict() for item in self.assertion_refs],
            "source_position_id": self.source_position_id,
            "source_game_id": self.source_game_id,
            "relation": self.relation,
            "context_refs": [item.to_dict() for item in self.context_refs],
            "measurement_condition": self.measurement_condition,
            "basis_kind": self.basis_kind,
            "mapping_provenance": self.mapping_provenance.to_dict(),
            "created_at": self.created_at,
        }
        if include_identity:
            payload["link_id"] = self.link_id
            payload["fingerprint"] = self.fingerprint
        return payload
