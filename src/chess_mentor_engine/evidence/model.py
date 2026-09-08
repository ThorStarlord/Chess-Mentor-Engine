"""Immutable M5 Player Decision Evidence records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.selection import SelectionPolicyIdentity

StageKind: TypeAlias = Literal[
    "MINIMAL_RESPONSE",
    "STANDARDIZED_PROBE",
    "POST_REVEAL_REFLECTION",
    "ORIGINAL_GAME_RECOLLECTION",
]
InteractionClass: TypeAlias = Literal[
    "observation",
    "diagnostic_probing",
    "post_reveal_reflection",
    "original_game_recollection",
    "tutoring_intervention",
]
ExposureKind: TypeAlias = Literal[
    "POSITION_CONTEXT_SHOWN",
    "LATER_STAGE_PROMPT_SHOWN",
    "ENGINE_EVIDENCE_SHOWN",
    "SELECTION_RATIONALE_SHOWN",
    "EXPECTED_DISCREPANCY_SHOWN",
    "PRIOR_REPORT_SHOWN",
    "EXTERNAL_ANALYSIS_REPORTED",
    "FACILITATOR_HINT",
    "INSTRUMENT_AWARENESS_RECORDED",
    "OTHER",
]
InstrumentAwareness: TypeAlias = Literal[
    "known_aware",
    "known_unaware",
    "unknown",
]
MoveNormalizationStatus: TypeAlias = Literal[
    "normalized",
    "ambiguous",
    "unresolved",
]
MoveLegality: TypeAlias = Literal[
    "legal",
    "illegal_for_position",
    "not_assessed",
]
EvidenceReferenceKind: TypeAlias = Literal[
    "position_context_packet",
    "diagnostic_candidate",
    "diagnostic_batch",
    "position_analysis",
    "decision_comparison",
    "selection_signal",
]


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """Stable reference to an upstream evidence object."""

    kind: EvidenceReferenceKind
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
class ParticipantMove:
    """Participant-authored move value without promoting it to chess truth."""

    submitted_value: str
    normalized_uci: str | None
    normalization_status: MoveNormalizationStatus
    legality: MoveLegality = "not_assessed"

    def __post_init__(self) -> None:
        _require_nonempty("submitted_value", self.submitted_value)
        if self.normalization_status == "normalized" and not self.normalized_uci:
            raise ValueError("normalized move requires normalized_uci")
        if (
            self.normalization_status != "normalized"
            and self.normalized_uci is not None
        ):
            raise ValueError(
                "ambiguous/unresolved move must not contain normalized_uci"
            )
        if self.legality != "not_assessed" and self.normalized_uci is None:
            raise ValueError("assessed move legality requires normalized_uci")

    def to_dict(self) -> dict[str, Any]:
        return {
            "submitted_value": self.submitted_value,
            "normalized_uci": self.normalized_uci,
            "normalization_status": self.normalization_status,
            "legality": self.legality,
        }


@dataclass(frozen=True, slots=True)
class NumericRating:
    """Participant-submitted numeric rating with its explicit scale."""

    value: int
    minimum: int
    maximum: int

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError("rating minimum must not exceed maximum")
        if not self.minimum <= self.value <= self.maximum:
            raise ValueError("rating value must lie within its submitted scale")

    def to_dict(self) -> dict[str, int]:
        return {
            "value": self.value,
            "minimum": self.minimum,
            "maximum": self.maximum,
        }


@dataclass(frozen=True, slots=True)
class ParticipantStructuredResponse:
    """Only fields explicitly submitted through structured participant controls."""

    selected_move: ParticipantMove | None = None
    candidate_moves: tuple[ParticipantMove, ...] = ()
    expected_reply: ParticipantMove | None = None
    expected_continuation: tuple[ParticipantMove, ...] = ()
    stated_objective: str | None = None
    uncertainty: str | None = None
    confidence: NumericRating | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_move": (
                None if self.selected_move is None else self.selected_move.to_dict()
            ),
            "candidate_moves": [item.to_dict() for item in self.candidate_moves],
            "expected_reply": (
                None if self.expected_reply is None else self.expected_reply.to_dict()
            ),
            "expected_continuation": [
                item.to_dict() for item in self.expected_continuation
            ],
            "stated_objective": self.stated_objective,
            "uncertainty": self.uncertainty,
            "confidence": (
                None if self.confidence is None else self.confidence.to_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class PlayerDecisionContext:
    context_id: str
    participant_id: str
    session_id: str
    position_id: str
    game_id: str
    diagnostic_candidate_ref: EvidenceReference
    diagnostic_batch_ref: EvidenceReference | None
    position_context_packet_ref: EvidenceReference
    selection_policy: SelectionPolicyIdentity
    created_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("context_id", self.context_id),
            ("participant_id", self.participant_id),
            ("session_id", self.session_id),
            ("position_id", self.position_id),
            ("game_id", self.game_id),
            ("created_at", self.created_at),
        ):
            _require_nonempty(name, value)
        if self.diagnostic_candidate_ref.kind != "diagnostic_candidate":
            raise ValueError("diagnostic_candidate_ref has wrong kind")
        if (
            self.diagnostic_batch_ref is not None
            and self.diagnostic_batch_ref.kind != "diagnostic_batch"
        ):
            raise ValueError("diagnostic_batch_ref has wrong kind")
        if self.position_context_packet_ref.kind != "position_context_packet":
            raise ValueError("position_context_packet_ref has wrong kind")

    def to_dict(self, *, include_context_id: bool = True) -> dict[str, Any]:
        payload = {
            "participant_id": self.participant_id,
            "session_id": self.session_id,
            "position_id": self.position_id,
            "game_id": self.game_id,
            "diagnostic_candidate_ref": self.diagnostic_candidate_ref.to_dict(),
            "diagnostic_batch_ref": (
                None
                if self.diagnostic_batch_ref is None
                else self.diagnostic_batch_ref.to_dict()
            ),
            "position_context_packet_ref": self.position_context_packet_ref.to_dict(),
            "selection_policy": self.selection_policy.to_dict(),
            "created_at": self.created_at,
        }
        if include_context_id:
            payload["context_id"] = self.context_id
        return payload


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    prompt_definition_id: str
    definition_fingerprint: str
    name: str
    version: str
    stage_kind: StageKind
    interaction_class: InteractionClass
    content: tuple[str, ...]
    response_schema: tuple[str, ...]
    provenance: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("prompt_definition_id", self.prompt_definition_id),
            ("definition_fingerprint", self.definition_fingerprint),
            ("name", self.name),
            ("version", self.version),
        ):
            _require_nonempty(name, value)
        if not self.content or not any(self.content):
            raise ValueError("prompt content must not be empty")
        keys = tuple(key for key, _ in self.provenance)
        if len(set(keys)) != len(keys):
            raise ValueError("prompt provenance keys must be unique")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "version": self.version,
            "stage_kind": self.stage_kind,
            "interaction_class": self.interaction_class,
            "content": list(self.content),
            "response_schema": list(self.response_schema),
            "provenance": [[key, value] for key, value in self.provenance],
        }
        if include_identity:
            payload["prompt_definition_id"] = self.prompt_definition_id
            payload["definition_fingerprint"] = self.definition_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class PromptPresentation:
    presentation_id: str
    context_id: str
    stage_id: str
    stage_kind: StageKind
    prompt_definition_id: str
    position_context_packet_ref: EvidenceReference
    shown_at: str
    rendered_content: str
    rendered_content_fingerprint: str
    information_available_before_presentation: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("presentation_id", self.presentation_id),
            ("context_id", self.context_id),
            ("stage_id", self.stage_id),
            ("prompt_definition_id", self.prompt_definition_id),
            ("shown_at", self.shown_at),
            ("rendered_content_fingerprint", self.rendered_content_fingerprint),
        ):
            _require_nonempty(name, value)
        if self.position_context_packet_ref.kind != "position_context_packet":
            raise ValueError("presentation position context ref has wrong kind")
        if len(set(self.information_available_before_presentation)) != len(
            self.information_available_before_presentation
        ):
            raise ValueError("presentation exposure references must be unique")

    def to_dict(self, *, include_presentation_id: bool = True) -> dict[str, Any]:
        payload = {
            "context_id": self.context_id,
            "stage_id": self.stage_id,
            "stage_kind": self.stage_kind,
            "prompt_definition_id": self.prompt_definition_id,
            "position_context_packet_ref": self.position_context_packet_ref.to_dict(),
            "shown_at": self.shown_at,
            "rendered_content": self.rendered_content,
            "rendered_content_fingerprint": self.rendered_content_fingerprint,
            "information_available_before_presentation": list(
                self.information_available_before_presentation
            ),
        }
        if include_presentation_id:
            payload["presentation_id"] = self.presentation_id
        return payload


@dataclass(frozen=True, slots=True)
class PlayerResponseEvidence:
    response_id: str
    response_fingerprint: str
    context_id: str
    stage_id: str
    stage_kind: StageKind
    presentation_id: str
    participant_id: str
    raw_response: str
    structured_response: ParticipantStructuredResponse | None
    submitted_at: str

    def __post_init__(self) -> None:
        for name, value in (
            ("response_id", self.response_id),
            ("response_fingerprint", self.response_fingerprint),
            ("context_id", self.context_id),
            ("stage_id", self.stage_id),
            ("presentation_id", self.presentation_id),
            ("participant_id", self.participant_id),
            ("submitted_at", self.submitted_at),
        ):
            _require_nonempty(name, value)

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload = {
            "context_id": self.context_id,
            "stage_id": self.stage_id,
            "stage_kind": self.stage_kind,
            "presentation_id": self.presentation_id,
            "participant_id": self.participant_id,
            "raw_response": self.raw_response,
            "structured_response": (
                None
                if self.structured_response is None
                else self.structured_response.to_dict()
            ),
            "submitted_at": self.submitted_at,
        }
        if include_identity:
            payload["response_id"] = self.response_id
            payload["response_fingerprint"] = self.response_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class ExposureEvent:
    exposure_event_id: str
    context_id: str
    participant_id: str
    kind: ExposureKind
    occurred_at: str
    source: str
    details: tuple[tuple[str, str], ...]
    instrument_awareness: InstrumentAwareness | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("exposure_event_id", self.exposure_event_id),
            ("context_id", self.context_id),
            ("participant_id", self.participant_id),
            ("occurred_at", self.occurred_at),
            ("source", self.source),
        ):
            _require_nonempty(name, value)
        keys = tuple(key for key, _ in self.details)
        if len(set(keys)) != len(keys):
            raise ValueError("exposure detail keys must be unique")
        if self.kind == "INSTRUMENT_AWARENESS_RECORDED":
            if self.instrument_awareness is None:
                raise ValueError("instrument awareness event requires awareness state")
        elif self.instrument_awareness is not None:
            raise ValueError("instrument awareness belongs only to awareness events")

    def to_dict(self, *, include_exposure_event_id: bool = True) -> dict[str, Any]:
        payload = {
            "context_id": self.context_id,
            "participant_id": self.participant_id,
            "kind": self.kind,
            "occurred_at": self.occurred_at,
            "source": self.source,
            "details": [[key, value] for key, value in self.details],
            "instrument_awareness": self.instrument_awareness,
        }
        if include_exposure_event_id:
            payload["exposure_event_id"] = self.exposure_event_id
        return payload


@dataclass(frozen=True, slots=True)
class EvidenceFreeze:
    freeze_id: str
    context_id: str
    stage_id: str
    response_id: str
    frozen_at: str
    response_fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("freeze_id", self.freeze_id),
            ("context_id", self.context_id),
            ("stage_id", self.stage_id),
            ("response_id", self.response_id),
            ("frozen_at", self.frozen_at),
            ("response_fingerprint", self.response_fingerprint),
        ):
            _require_nonempty(name, value)

    def to_dict(self, *, include_freeze_id: bool = True) -> dict[str, Any]:
        payload = {
            "context_id": self.context_id,
            "stage_id": self.stage_id,
            "response_id": self.response_id,
            "frozen_at": self.frozen_at,
            "response_fingerprint": self.response_fingerprint,
        }
        if include_freeze_id:
            payload["freeze_id"] = self.freeze_id
        return payload


@dataclass(frozen=True, slots=True)
class ObjectiveEvidenceReveal:
    reveal_id: str
    context_id: str
    revealed_at: str
    position_analysis_refs: tuple[EvidenceReference, ...]
    decision_comparison_ref: EvidenceReference | None
    selection_signal_refs: tuple[EvidenceReference, ...]
    rendered_content: str
    rendered_content_fingerprint: str

    def __post_init__(self) -> None:
        for name, value in (
            ("reveal_id", self.reveal_id),
            ("context_id", self.context_id),
            ("revealed_at", self.revealed_at),
            ("rendered_content_fingerprint", self.rendered_content_fingerprint),
        ):
            _require_nonempty(name, value)
        if not (
            self.position_analysis_refs
            or self.decision_comparison_ref is not None
            or self.selection_signal_refs
        ):
            raise ValueError("objective reveal must reference objective evidence")
        for ref in self.position_analysis_refs:
            if ref.kind != "position_analysis":
                raise ValueError("position_analysis_refs contain wrong reference kind")
        if (
            self.decision_comparison_ref is not None
            and self.decision_comparison_ref.kind != "decision_comparison"
        ):
            raise ValueError("decision_comparison_ref has wrong kind")
        for ref in self.selection_signal_refs:
            if ref.kind != "selection_signal":
                raise ValueError("selection_signal_refs contain wrong reference kind")

    def to_dict(self, *, include_reveal_id: bool = True) -> dict[str, Any]:
        payload = {
            "context_id": self.context_id,
            "revealed_at": self.revealed_at,
            "position_analysis_refs": [
                item.to_dict() for item in self.position_analysis_refs
            ],
            "decision_comparison_ref": (
                None
                if self.decision_comparison_ref is None
                else self.decision_comparison_ref.to_dict()
            ),
            "selection_signal_refs": [
                item.to_dict() for item in self.selection_signal_refs
            ],
            "rendered_content": self.rendered_content,
            "rendered_content_fingerprint": self.rendered_content_fingerprint,
        }
        if include_reveal_id:
            payload["reveal_id"] = self.reveal_id
        return payload
