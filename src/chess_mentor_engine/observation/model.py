"""Immutable descriptive observations over exact local tutor checkpoints."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.learner_intelligence import EvidenceSynthesisReference
from chess_mentor_engine.storage import ArtifactRef
from chess_mentor_engine.storage.tutor import SESSION_KIND

OBSERVATION_KIND = "post-v1.interaction-observation.v1"
OBSERVATION_SCHEMA_VERSION = "post-v1.interaction-observation.v1"

ProductUseEventType: TypeAlias = Literal[
    "review_started",
    "position_presented",
    "prompt_presented",
    "response_submitted",
    "response_frozen",
    "proposal_generated",
    "session_abandoned",
    "session_completed",
    "participant_feedback",
]

SUPPORTED_EVENT_TYPES = {
    "review_started",
    "position_presented",
    "prompt_presented",
    "response_submitted",
    "response_frozen",
    "proposal_generated",
    "session_abandoned",
    "session_completed",
    "participant_feedback",
}


class ProductUseObservationError(ValueError):
    """A descriptive product-use record violates its narrow claim boundary."""


def _nonempty(name: str, value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ProductUseObservationError(f"{name} must not be empty")


def _timestamp(value: str) -> None:
    _nonempty("occurred_at", value)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProductUseObservationError("occurred_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProductUseObservationError("occurred_at requires an explicit timezone")


def _payload(
    *,
    participant_id: str,
    tutor_session_ref: ArtifactRef,
    event_type: str,
    occurred_at: str,
    workflow_stage: str,
    proposal_ref: EvidenceSynthesisReference | None,
    action: str | None,
    exposure_effect: str | None,
    response_evidence_class: str | None,
    metadata: tuple[tuple[str, str], ...],
    claim_scope: str,
    learning_effect: str,
    tutor_efficacy: str,
    mastery: str,
) -> dict[str, Any]:
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "participant_id": participant_id,
        "tutor_session_ref": tutor_session_ref.to_dict(),
        "event_type": event_type,
        "occurred_at": occurred_at,
        "workflow_stage": workflow_stage,
        "proposal_ref": None if proposal_ref is None else proposal_ref.to_dict(),
        "action": action,
        "exposure_effect": exposure_effect,
        "response_evidence_class": response_evidence_class,
        "metadata": [list(item) for item in metadata],
        "claim_scope": claim_scope,
        "learning_effect": learning_effect,
        "tutor_efficacy": tutor_efficacy,
        "mastery": mastery,
    }


def _fingerprint(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class InteractionObservation:
    observation_id: str
    fingerprint: str
    participant_id: str
    tutor_session_ref: ArtifactRef
    event_type: ProductUseEventType
    occurred_at: str
    workflow_stage: str
    proposal_ref: EvidenceSynthesisReference | None = None
    action: str | None = None
    exposure_effect: str | None = None
    response_evidence_class: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()
    claim_scope: Literal["descriptive_local_product_use_only"] = (
        "descriptive_local_product_use_only"
    )
    learning_effect: Literal["not_established"] = "not_established"
    tutor_efficacy: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
    schema_version: Literal["post-v1.interaction-observation.v1"] = (
        OBSERVATION_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("observation_id", self.observation_id),
            ("fingerprint", self.fingerprint),
            ("participant_id", self.participant_id),
            ("workflow_stage", self.workflow_stage),
        ):
            _nonempty(name, value)
        if self.tutor_session_ref.kind != SESSION_KIND:
            raise ProductUseObservationError("observation requires an exact M8 session")
        if self.tutor_session_ref.participant_id != self.participant_id:
            raise ProductUseObservationError("observation participant/session mismatch")
        if self.event_type not in SUPPORTED_EVENT_TYPES:
            raise ProductUseObservationError("unsupported product-use event type")
        _timestamp(self.occurred_at)
        if type(self.metadata) is not tuple:
            raise ProductUseObservationError("metadata must be an immutable tuple")
        keys: list[str] = []
        for item in self.metadata:
            if type(item) is not tuple or len(item) != 2:
                raise ProductUseObservationError("metadata entries must be key/value pairs")
            key, value = item
            _nonempty("metadata key", key)
            if type(value) is not str:
                raise ProductUseObservationError("metadata values must be strings")
            keys.append(key)
        if len(set(keys)) != len(keys):
            raise ProductUseObservationError("metadata keys must be unique")
        if tuple(sorted(self.metadata)) != self.metadata:
            raise ProductUseObservationError("metadata must be sorted by key")
        for name, value in (
            ("action", self.action),
            ("exposure_effect", self.exposure_effect),
            ("response_evidence_class", self.response_evidence_class),
        ):
            if value is not None:
                _nonempty(name, value)
        if self.claim_scope != "descriptive_local_product_use_only":
            raise ProductUseObservationError("invalid product-use observation claim scope")
        if self.learning_effect != "not_established":
            raise ProductUseObservationError(
                "product-use observation cannot establish learning effect"
            )
        if self.tutor_efficacy != "not_established":
            raise ProductUseObservationError(
                "product-use observation cannot establish tutor efficacy"
            )
        if self.mastery != "not_established":
            raise ProductUseObservationError(
                "product-use observation cannot establish mastery"
            )
        if self.schema_version != OBSERVATION_SCHEMA_VERSION:
            raise ProductUseObservationError("unsupported product-use schema")
        payload = self.identity_payload()
        expected = _fingerprint(payload)
        if self.fingerprint != expected:
            raise ProductUseObservationError("product-use observation fingerprint mismatch")
        if self.observation_id != f"product_use_observation_{expected[:20]}":
            raise ProductUseObservationError("product-use observation identity mismatch")

    def identity_payload(self) -> dict[str, Any]:
        return _payload(
            participant_id=self.participant_id,
            tutor_session_ref=self.tutor_session_ref,
            event_type=self.event_type,
            occurred_at=self.occurred_at,
            workflow_stage=self.workflow_stage,
            proposal_ref=self.proposal_ref,
            action=self.action,
            exposure_effect=self.exposure_effect,
            response_evidence_class=self.response_evidence_class,
            metadata=self.metadata,
            claim_scope=self.claim_scope,
            learning_effect=self.learning_effect,
            tutor_efficacy=self.tutor_efficacy,
            mastery=self.mastery,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def build_interaction_observation(
    *,
    participant_id: str,
    tutor_session_ref: ArtifactRef,
    event_type: ProductUseEventType,
    occurred_at: str,
    workflow_stage: str,
    proposal_ref: EvidenceSynthesisReference | None = None,
    action: str | None = None,
    exposure_effect: str | None = None,
    response_evidence_class: str | None = None,
    metadata: tuple[tuple[str, str], ...] = (),
) -> InteractionObservation:
    ordered_metadata = tuple(sorted(metadata))
    payload = _payload(
        participant_id=participant_id,
        tutor_session_ref=tutor_session_ref,
        event_type=event_type,
        occurred_at=occurred_at,
        workflow_stage=workflow_stage,
        proposal_ref=proposal_ref,
        action=action,
        exposure_effect=exposure_effect,
        response_evidence_class=response_evidence_class,
        metadata=ordered_metadata,
        claim_scope="descriptive_local_product_use_only",
        learning_effect="not_established",
        tutor_efficacy="not_established",
        mastery="not_established",
    )
    fingerprint = _fingerprint(payload)
    return InteractionObservation(
        observation_id=f"product_use_observation_{fingerprint[:20]}",
        fingerprint=fingerprint,
        participant_id=participant_id,
        tutor_session_ref=tutor_session_ref,
        event_type=event_type,
        occurred_at=occurred_at,
        workflow_stage=workflow_stage,
        proposal_ref=proposal_ref,
        action=action,
        exposure_effect=exposure_effect,
        response_evidence_class=response_evidence_class,
        metadata=ordered_metadata,
    )
