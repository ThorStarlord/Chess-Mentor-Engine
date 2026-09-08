"""Deterministic append-only M5C capture/freeze state machine."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json

from .model import (
    EvidenceFreeze,
    EvidenceReference,
    ExposureEvent,
    ExposureKind,
    ObjectiveEvidenceReveal,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    PlayerResponseEvidence,
    PromptDefinition,
    PromptPresentation,
    StageKind,
)
from .records import (
    PlayerEvidenceError,
    record_evidence_freeze,
    record_exposure_event,
    record_objective_evidence_reveal,
    record_player_response,
    record_prompt_presentation,
)

StagePhase: TypeAlias = Literal["pre_reveal", "post_reveal"]
ViolationMode: TypeAlias = Literal["reject", "preserve"]
DeviationCode: TypeAlias = Literal[
    "STAGE_OUT_OF_ORDER",
    "STAGE_PRESENTED_BEFORE_PRIOR_FREEZE",
    "POST_REVEAL_STAGE_BEFORE_REVEAL",
    "PRE_REVEAL_STAGE_AFTER_REVEAL",
    "OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES",
    "INTERVENTION_LIKE_PROMPT",
    "PROHIBITED_PRE_REVEAL_EXPOSURE",
    "TIMESTAMP_ORDER_VIOLATION",
    "OTHER",
]

_PROHIBITED_PRE_REVEAL_EXPOSURES: frozenset[ExposureKind] = frozenset(
    {
        "ENGINE_EVIDENCE_SHOWN",
        "SELECTION_RATIONALE_SHOWN",
        "EXPECTED_DISCREPANCY_SHOWN",
        "PRIOR_REPORT_SHOWN",
        "EXTERNAL_ANALYSIS_REPORTED",
        "FACILITATOR_HINT",
    }
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _record_id(prefix: str, payload: object) -> str:
    return f"{prefix}_{_fingerprint(payload)[:20]}"


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise PlayerEvidenceError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PlayerEvidenceError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PlayerEvidenceError("timestamp must include an explicit timezone")
    return parsed


def _normalize_pairs(
    pairs: tuple[tuple[str, str], ...], *, label: str
) -> tuple[tuple[str, str], ...]:
    keys = tuple(key for key, _ in pairs)
    if any(not key for key in keys):
        raise PlayerEvidenceError(f"{label} keys must not be empty")
    if len(set(keys)) != len(keys):
        raise PlayerEvidenceError(f"{label} keys must be unique")
    return tuple(sorted(pairs, key=lambda item: item[0]))


@dataclass(frozen=True, slots=True)
class CaptureStageSpec:
    """One versioned stage in an evidence-capture protocol."""

    stage_id: str
    stage_kind: StageKind
    prompt_definition_id: str
    phase: StagePhase

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise ValueError("stage_id must not be empty")
        if not self.prompt_definition_id:
            raise ValueError("prompt_definition_id must not be empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "stage_id": self.stage_id,
            "stage_kind": self.stage_kind,
            "prompt_definition_id": self.prompt_definition_id,
            "phase": self.phase,
        }


@dataclass(frozen=True, slots=True)
class CaptureProtocol:
    """Material identity for a deterministic capture-stage sequence."""

    protocol_id: str
    protocol_fingerprint: str
    name: str
    version: str
    stages: tuple[CaptureStageSpec, ...]

    def __post_init__(self) -> None:
        if not self.protocol_id:
            raise ValueError("protocol_id must not be empty")
        if not self.protocol_fingerprint:
            raise ValueError("protocol_fingerprint must not be empty")
        if not self.name:
            raise ValueError("protocol name must not be empty")
        if not self.version:
            raise ValueError("protocol version must not be empty")
        if not self.stages:
            raise ValueError("capture protocol must contain at least one stage")
        stage_ids = tuple(stage.stage_id for stage in self.stages)
        if len(set(stage_ids)) != len(stage_ids):
            raise ValueError("capture protocol stage IDs must be unique")
        prompt_ids = tuple(stage.prompt_definition_id for stage in self.stages)
        if len(set(prompt_ids)) != len(prompt_ids):
            raise ValueError("capture protocol prompt definitions must be unique")
        saw_post_reveal = False
        for stage in self.stages:
            if stage.phase == "post_reveal":
                saw_post_reveal = True
            elif saw_post_reveal:
                raise ValueError("pre-reveal stages cannot follow post-reveal stages")
        if not any(stage.phase == "pre_reveal" for stage in self.stages):
            raise ValueError("capture protocol requires at least one pre-reveal stage")

    @property
    def pre_reveal_stages(self) -> tuple[CaptureStageSpec, ...]:
        return tuple(stage for stage in self.stages if stage.phase == "pre_reveal")

    @property
    def post_reveal_stages(self) -> tuple[CaptureStageSpec, ...]:
        return tuple(stage for stage in self.stages if stage.phase == "post_reveal")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "stages": [stage.to_dict() for stage in self.stages],
        }
        if include_identity:
            payload["protocol_id"] = self.protocol_id
            payload["protocol_fingerprint"] = self.protocol_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class EvidenceAmendment:
    """Append-only clarification of already frozen participant evidence."""

    amendment_id: str
    amendment_fingerprint: str
    context_id: str
    stage_id: str
    original_response_id: str
    original_freeze_id: str
    participant_id: str
    raw_response: str
    structured_response: ParticipantStructuredResponse | None
    submitted_at: str
    reason: str

    def __post_init__(self) -> None:
        for name, value in (
            ("amendment_id", self.amendment_id),
            ("amendment_fingerprint", self.amendment_fingerprint),
            ("context_id", self.context_id),
            ("stage_id", self.stage_id),
            ("original_response_id", self.original_response_id),
            ("original_freeze_id", self.original_freeze_id),
            ("participant_id", self.participant_id),
            ("submitted_at", self.submitted_at),
            ("reason", self.reason),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "context_id": self.context_id,
            "stage_id": self.stage_id,
            "original_response_id": self.original_response_id,
            "original_freeze_id": self.original_freeze_id,
            "participant_id": self.participant_id,
            "raw_response": self.raw_response,
            "structured_response": (
                None
                if self.structured_response is None
                else self.structured_response.to_dict()
            ),
            "submitted_at": self.submitted_at,
            "reason": self.reason,
        }
        if include_identity:
            payload["amendment_id"] = self.amendment_id
            payload["amendment_fingerprint"] = self.amendment_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class ProtocolDeviation:
    """Immutable provenance for a sequence/information-boundary deviation."""

    deviation_id: str
    context_id: str
    code: DeviationCode
    occurred_at: str
    stage_id: str | None
    related_record_ids: tuple[str, ...]
    details: tuple[tuple[str, str], ...]
    contaminates_pre_reveal: bool

    def __post_init__(self) -> None:
        if not self.deviation_id:
            raise ValueError("deviation_id must not be empty")
        if not self.context_id:
            raise ValueError("context_id must not be empty")
        if not self.occurred_at:
            raise ValueError("occurred_at must not be empty")
        if len(set(self.related_record_ids)) != len(self.related_record_ids):
            raise ValueError("related deviation record IDs must be unique")
        keys = tuple(key for key, _ in self.details)
        if len(set(keys)) != len(keys):
            raise ValueError("deviation detail keys must be unique")

    def to_dict(self, *, include_deviation_id: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "context_id": self.context_id,
            "code": self.code,
            "occurred_at": self.occurred_at,
            "stage_id": self.stage_id,
            "related_record_ids": list(self.related_record_ids),
            "details": [list(item) for item in self.details],
            "contaminates_pre_reveal": self.contaminates_pre_reveal,
        }
        if include_deviation_id:
            payload["deviation_id"] = self.deviation_id
        return payload


@dataclass(frozen=True, slots=True)
class EvidenceCaptureSession:
    """Immutable snapshot of one append-only Player Decision Evidence capture run."""

    capture_session_id: str
    snapshot_fingerprint: str
    context: PlayerDecisionContext
    protocol: CaptureProtocol
    presentations: tuple[PromptPresentation, ...] = ()
    responses: tuple[PlayerResponseEvidence, ...] = ()
    freezes: tuple[EvidenceFreeze, ...] = ()
    exposures: tuple[ExposureEvent, ...] = ()
    amendments: tuple[EvidenceAmendment, ...] = ()
    deviations: tuple[ProtocolDeviation, ...] = ()
    objective_reveal: ObjectiveEvidenceReveal | None = None

    @property
    def contaminated(self) -> bool:
        return any(item.contaminates_pre_reveal for item in self.deviations)

    def to_dict(self, *, include_snapshot_fingerprint: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "capture_session_id": self.capture_session_id,
            "context": self.context.to_dict(),
            "protocol": self.protocol.to_dict(),
            "presentations": [item.to_dict() for item in self.presentations],
            "responses": [item.to_dict() for item in self.responses],
            "freezes": [item.to_dict() for item in self.freezes],
            "exposures": [item.to_dict() for item in self.exposures],
            "amendments": [item.to_dict() for item in self.amendments],
            "deviations": [item.to_dict() for item in self.deviations],
            "objective_reveal": (
                None
                if self.objective_reveal is None
                else self.objective_reveal.to_dict()
            ),
        }
        if include_snapshot_fingerprint:
            payload["snapshot_fingerprint"] = self.snapshot_fingerprint
        return payload


def define_capture_protocol(
    *,
    name: str,
    version: str,
    stages: tuple[CaptureStageSpec, ...],
) -> CaptureProtocol:
    """Create a material-content-addressed stage protocol."""
    if not name:
        raise PlayerEvidenceError("protocol name must not be empty")
    if not version:
        raise PlayerEvidenceError("protocol version must not be empty")
    if not stages:
        raise PlayerEvidenceError("capture protocol must contain at least one stage")
    payload = {
        "name": name,
        "version": version,
        "stages": [stage.to_dict() for stage in stages],
    }
    fingerprint = _fingerprint(payload)
    try:
        return CaptureProtocol(
            protocol_id=f"capture_protocol_{fingerprint[:20]}",
            protocol_fingerprint=fingerprint,
            name=name,
            version=version,
            stages=stages,
        )
    except ValueError as exc:
        raise PlayerEvidenceError(str(exc)) from exc


def start_capture_session(
    *, context: PlayerDecisionContext, protocol: CaptureProtocol
) -> EvidenceCaptureSession:
    """Start an immutable capture ledger for one M5 decision context."""
    payload = {
        "context_id": context.context_id,
        "participant_id": context.participant_id,
        "application_session_id": context.session_id,
        "protocol_id": protocol.protocol_id,
        "protocol_fingerprint": protocol.protocol_fingerprint,
    }
    capture_session_id = _record_id("capture_session", payload)
    return _rebuild_session(
        EvidenceCaptureSession(
            capture_session_id=capture_session_id,
            snapshot_fingerprint="pending",
            context=context,
            protocol=protocol,
        )
    )


def _rebuild_session(session: EvidenceCaptureSession) -> EvidenceCaptureSession:
    payload = session.to_dict(include_snapshot_fingerprint=False)
    return replace(session, snapshot_fingerprint=_fingerprint(payload))


def _stage_spec(session: EvidenceCaptureSession, stage_id: str) -> CaptureStageSpec:
    for stage in session.protocol.stages:
        if stage.stage_id == stage_id:
            return stage
    raise PlayerEvidenceError(f"stage {stage_id!r} is not defined by capture protocol")


def _presentation_for(
    session: EvidenceCaptureSession, stage_id: str
) -> PromptPresentation | None:
    return next(
        (item for item in session.presentations if item.stage_id == stage_id),
        None,
    )


def _response_for(
    session: EvidenceCaptureSession, stage_id: str
) -> PlayerResponseEvidence | None:
    return next((item for item in session.responses if item.stage_id == stage_id), None)


def _freeze_for(
    session: EvidenceCaptureSession, stage_id: str
) -> EvidenceFreeze | None:
    return next((item for item in session.freezes if item.stage_id == stage_id), None)


def _required_pre_reveal_complete(session: EvidenceCaptureSession) -> bool:
    return all(
        _freeze_for(session, stage.stage_id) is not None
        for stage in session.protocol.pre_reveal_stages
    )


def _prior_stage_specs(
    session: EvidenceCaptureSession, stage: CaptureStageSpec
) -> tuple[CaptureStageSpec, ...]:
    phase_stages = (
        session.protocol.pre_reveal_stages
        if stage.phase == "pre_reveal"
        else session.protocol.post_reveal_stages
    )
    index = phase_stages.index(stage)
    return phase_stages[:index]


def _append_deviation(
    session: EvidenceCaptureSession,
    *,
    code: DeviationCode,
    occurred_at: str,
    stage_id: str | None = None,
    related_record_ids: tuple[str, ...] = (),
    details: tuple[tuple[str, str], ...] = (),
    contaminates_pre_reveal: bool = True,
) -> EvidenceCaptureSession:
    _parse_timestamp(occurred_at)
    normalized_details = _normalize_pairs(details, label="deviation details")
    related_ids = tuple(sorted(related_record_ids))
    if len(set(related_ids)) != len(related_ids):
        raise PlayerEvidenceError("related deviation record IDs must be unique")
    payload = {
        "context_id": session.context.context_id,
        "code": code,
        "occurred_at": occurred_at,
        "stage_id": stage_id,
        "related_record_ids": list(related_ids),
        "details": [list(item) for item in normalized_details],
        "contaminates_pre_reveal": contaminates_pre_reveal,
    }
    deviation = ProtocolDeviation(
        deviation_id=_record_id("deviation", payload),
        context_id=session.context.context_id,
        code=code,
        occurred_at=occurred_at,
        stage_id=stage_id,
        related_record_ids=related_ids,
        details=normalized_details,
        contaminates_pre_reveal=contaminates_pre_reveal,
    )
    if deviation.deviation_id in {item.deviation_id for item in session.deviations}:
        return session
    return _rebuild_session(
        replace(session, deviations=session.deviations + (deviation,))
    )


def record_capture_deviation(
    session: EvidenceCaptureSession,
    *,
    code: DeviationCode,
    occurred_at: str,
    stage_id: str | None = None,
    related_record_ids: tuple[str, ...] = (),
    details: tuple[tuple[str, str], ...] = (),
    contaminates_pre_reveal: bool = True,
) -> EvidenceCaptureSession:
    """Append operator/runtime deviation provenance without deleting evidence."""
    if stage_id is not None:
        _stage_spec(session, stage_id)
    return _append_deviation(
        session,
        code=code,
        occurred_at=occurred_at,
        stage_id=stage_id,
        related_record_ids=related_record_ids,
        details=details,
        contaminates_pre_reveal=contaminates_pre_reveal,
    )


def _handle_violation(
    session: EvidenceCaptureSession,
    *,
    mode: ViolationMode,
    message: str,
    code: DeviationCode,
    occurred_at: str,
    stage_id: str | None = None,
    related_record_ids: tuple[str, ...] = (),
    details: tuple[tuple[str, str], ...] = (),
) -> EvidenceCaptureSession:
    if mode == "reject":
        raise PlayerEvidenceError(message)
    if mode != "preserve":
        raise PlayerEvidenceError(f"unknown violation mode: {mode!r}")
    return _append_deviation(
        session,
        code=code,
        occurred_at=occurred_at,
        stage_id=stage_id,
        related_record_ids=related_record_ids,
        details=details,
    )


def present_capture_stage(
    session: EvidenceCaptureSession,
    *,
    stage_id: str,
    prompt: PromptDefinition,
    shown_at: str,
    rendered_content: str,
    violation_mode: ViolationMode = "reject",
) -> tuple[EvidenceCaptureSession, PromptPresentation]:
    """Present one planned stage while enforcing/preserving sequence provenance."""
    shown_time = _parse_timestamp(shown_at)
    context_time = _parse_timestamp(session.context.created_at)
    stage = _stage_spec(session, stage_id)
    if _presentation_for(session, stage_id) is not None:
        raise PlayerEvidenceError(f"stage {stage_id!r} was already presented")
    if prompt.prompt_definition_id != stage.prompt_definition_id:
        raise PlayerEvidenceError("prompt definition does not match capture stage")
    if prompt.stage_kind != stage.stage_kind:
        raise PlayerEvidenceError("prompt stage kind does not match capture stage")

    working = session
    if shown_time < context_time:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="stage presentation cannot precede decision context",
            code="TIMESTAMP_ORDER_VIOLATION",
            occurred_at=shown_at,
            stage_id=stage_id,
            details=(("event", "presentation_before_context"),),
        )

    if stage.phase == "pre_reveal" and working.objective_reveal is not None:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="pre-reveal stage cannot be presented after objective reveal",
            code="PRE_REVEAL_STAGE_AFTER_REVEAL",
            occurred_at=shown_at,
            stage_id=stage_id,
            related_record_ids=(working.objective_reveal.reveal_id,),
        )
    if stage.phase == "post_reveal" and working.objective_reveal is None:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="post-reveal stage requires objective evidence reveal first",
            code="POST_REVEAL_STAGE_BEFORE_REVEAL",
            occurred_at=shown_at,
            stage_id=stage_id,
        )

    prior_specs = _prior_stage_specs(working, stage)
    unpresented_prior = tuple(
        item.stage_id
        for item in prior_specs
        if _presentation_for(working, item.stage_id) is None
    )
    if unpresented_prior:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="capture stage is out of protocol order",
            code="STAGE_OUT_OF_ORDER",
            occurred_at=shown_at,
            stage_id=stage_id,
            details=(("missing_prior_stages", ",".join(unpresented_prior)),),
        )

    unfrozen_prior = tuple(
        item.stage_id
        for item in prior_specs
        if _freeze_for(working, item.stage_id) is None
    )
    if unfrozen_prior:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="later capture stage requires prior stage freezes",
            code="STAGE_PRESENTED_BEFORE_PRIOR_FREEZE",
            occurred_at=shown_at,
            stage_id=stage_id,
            details=(("unfrozen_prior_stages", ",".join(unfrozen_prior)),),
        )

    if (
        stage.phase == "pre_reveal"
        and prompt.interaction_class == "tutoring_intervention"
    ):
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="tutoring-intervention prompt is outside clean pre-reveal capture",
            code="INTERVENTION_LIKE_PROMPT",
            occurred_at=shown_at,
            stage_id=stage_id,
            related_record_ids=(prompt.prompt_definition_id,),
        )

    presentation = record_prompt_presentation(
        context=working.context,
        stage_id=stage_id,
        prompt=prompt,
        shown_at=shown_at,
        rendered_content=rendered_content,
        prior_exposures=working.exposures,
    )
    working = _rebuild_session(
        replace(working, presentations=working.presentations + (presentation,))
    )

    phase_stages = (
        working.protocol.pre_reveal_stages
        if stage.phase == "pre_reveal"
        else working.protocol.post_reveal_stages
    )
    if phase_stages.index(stage) > 0:
        later_prompt_exposure = record_exposure_event(
            context=working.context,
            kind="LATER_STAGE_PROMPT_SHOWN",
            occurred_at=shown_at,
            source="m5c-capture-state-machine",
            details=(
                ("presentation_id", presentation.presentation_id),
                ("stage_id", stage_id),
            ),
        )
        working = _rebuild_session(
            replace(working, exposures=working.exposures + (later_prompt_exposure,))
        )
    return working, presentation


def capture_stage_response(
    session: EvidenceCaptureSession,
    *,
    stage_id: str,
    raw_response: str,
    submitted_at: str,
    structured_response: ParticipantStructuredResponse | None = None,
    violation_mode: ViolationMode = "reject",
) -> tuple[EvidenceCaptureSession, PlayerResponseEvidence]:
    """Capture exactly one participant response for a presented planned stage."""
    submitted_time = _parse_timestamp(submitted_at)
    presentation = _presentation_for(session, stage_id)
    if presentation is None:
        raise PlayerEvidenceError("cannot capture response before stage presentation")
    if _response_for(session, stage_id) is not None:
        raise PlayerEvidenceError(f"stage {stage_id!r} already has a response")
    shown_time = _parse_timestamp(presentation.shown_at)
    working = session
    if submitted_time < shown_time:
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="response submission cannot precede prompt presentation",
            code="TIMESTAMP_ORDER_VIOLATION",
            occurred_at=submitted_at,
            stage_id=stage_id,
            related_record_ids=(presentation.presentation_id,),
            details=(("event", "response_before_presentation"),),
        )
    response = record_player_response(
        context=working.context,
        presentation=presentation,
        raw_response=raw_response,
        submitted_at=submitted_at,
        structured_response=structured_response,
    )
    working = _rebuild_session(
        replace(working, responses=working.responses + (response,))
    )
    return working, response


def freeze_stage_response(
    session: EvidenceCaptureSession,
    *,
    stage_id: str,
    frozen_at: str,
) -> tuple[EvidenceCaptureSession, EvidenceFreeze]:
    """Freeze a captured stage response exactly once."""
    response = _response_for(session, stage_id)
    if response is None:
        raise PlayerEvidenceError("cannot freeze stage before response capture")
    if _freeze_for(session, stage_id) is not None:
        raise PlayerEvidenceError(f"stage {stage_id!r} is already frozen")
    freeze = record_evidence_freeze(
        context=session.context,
        response=response,
        frozen_at=frozen_at,
    )
    working = _rebuild_session(replace(session, freezes=session.freezes + (freeze,)))
    return working, freeze


def record_capture_exposure(
    session: EvidenceCaptureSession,
    *,
    kind: ExposureKind,
    occurred_at: str,
    source: str,
    details: tuple[tuple[str, str], ...] = (),
    instrument_awareness: Literal["known_aware", "known_unaware", "unknown"]
    | None = None,
) -> tuple[EvidenceCaptureSession, ExposureEvent]:
    """Append exposure evidence and mark prohibited clean-boundary leakage."""
    occurred_time = _parse_timestamp(occurred_at)
    context_time = _parse_timestamp(session.context.created_at)
    if occurred_time < context_time:
        raise PlayerEvidenceError("exposure cannot precede decision context")
    exposure = record_exposure_event(
        context=session.context,
        kind=kind,
        occurred_at=occurred_at,
        source=source,
        details=details,
        instrument_awareness=instrument_awareness,
    )
    working = _rebuild_session(
        replace(session, exposures=session.exposures + (exposure,))
    )
    if (
        working.objective_reveal is None
        and not _required_pre_reveal_complete(working)
        and kind in _PROHIBITED_PRE_REVEAL_EXPOSURES
    ):
        working = _append_deviation(
            working,
            code="PROHIBITED_PRE_REVEAL_EXPOSURE",
            occurred_at=occurred_at,
            related_record_ids=(exposure.exposure_event_id,),
            details=(("exposure_kind", kind),),
        )
    return working, exposure


def append_evidence_amendment(
    session: EvidenceCaptureSession,
    *,
    original_response_id: str,
    raw_response: str,
    submitted_at: str,
    reason: str,
    structured_response: ParticipantStructuredResponse | None = None,
) -> tuple[EvidenceCaptureSession, EvidenceAmendment]:
    """Append a clarification without altering the original frozen response."""
    submitted_time = _parse_timestamp(submitted_at)
    if not reason:
        raise PlayerEvidenceError("amendment reason must not be empty")
    response = next(
        (
            item
            for item in session.responses
            if item.response_id == original_response_id
        ),
        None,
    )
    if response is None:
        raise PlayerEvidenceError("original response is not part of capture session")
    freeze = next(
        (item for item in session.freezes if item.response_id == original_response_id),
        None,
    )
    if freeze is None:
        raise PlayerEvidenceError(
            "amendment requires the original response to be frozen"
        )
    if submitted_time < _parse_timestamp(freeze.frozen_at):
        raise PlayerEvidenceError("amendment cannot precede original freeze")
    payload = {
        "context_id": session.context.context_id,
        "stage_id": response.stage_id,
        "original_response_id": response.response_id,
        "original_freeze_id": freeze.freeze_id,
        "participant_id": session.context.participant_id,
        "raw_response": raw_response,
        "structured_response": (
            None if structured_response is None else structured_response.to_dict()
        ),
        "submitted_at": submitted_at,
        "reason": reason,
    }
    fingerprint = _fingerprint(payload)
    amendment = EvidenceAmendment(
        amendment_id=f"amendment_{fingerprint[:20]}",
        amendment_fingerprint=fingerprint,
        context_id=session.context.context_id,
        stage_id=response.stage_id,
        original_response_id=response.response_id,
        original_freeze_id=freeze.freeze_id,
        participant_id=session.context.participant_id,
        raw_response=raw_response,
        structured_response=structured_response,
        submitted_at=submitted_at,
        reason=reason,
    )
    if amendment.amendment_id in {item.amendment_id for item in session.amendments}:
        raise PlayerEvidenceError("duplicate amendment record")
    working = _rebuild_session(
        replace(session, amendments=session.amendments + (amendment,))
    )
    return working, amendment


def reveal_objective_evidence(
    session: EvidenceCaptureSession,
    *,
    revealed_at: str,
    rendered_content: str,
    position_analysis_refs: tuple[EvidenceReference, ...] = (),
    decision_comparison_ref: EvidenceReference | None = None,
    selection_signal_refs: tuple[EvidenceReference, ...] = (),
    violation_mode: ViolationMode = "reject",
) -> tuple[EvidenceCaptureSession, ObjectiveEvidenceReveal]:
    """Reveal objective evidence only after required freezes, or preserve deviation."""
    reveal_time = _parse_timestamp(revealed_at)
    if session.objective_reveal is not None:
        raise PlayerEvidenceError("objective evidence was already revealed")
    working = session
    if not _required_pre_reveal_complete(working):
        missing = tuple(
            stage.stage_id
            for stage in working.protocol.pre_reveal_stages
            if _freeze_for(working, stage.stage_id) is None
        )
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="objective reveal requires all pre-reveal stage freezes",
            code="OBJECTIVE_REVEAL_BEFORE_REQUIRED_FREEZES",
            occurred_at=revealed_at,
            details=(("missing_freezes", ",".join(missing)),),
        )

    latest_times: list[datetime] = [_parse_timestamp(working.context.created_at)]
    latest_times.extend(
        _parse_timestamp(item.shown_at) for item in working.presentations
    )
    latest_times.extend(
        _parse_timestamp(item.submitted_at) for item in working.responses
    )
    latest_times.extend(_parse_timestamp(item.frozen_at) for item in working.freezes)
    if reveal_time < max(latest_times):
        working = _handle_violation(
            working,
            mode=violation_mode,
            message="objective reveal timestamp precedes captured evidence",
            code="TIMESTAMP_ORDER_VIOLATION",
            occurred_at=revealed_at,
            details=(("event", "reveal_before_existing_evidence"),),
        )

    reveal = record_objective_evidence_reveal(
        context=working.context,
        revealed_at=revealed_at,
        rendered_content=rendered_content,
        position_analysis_refs=position_analysis_refs,
        decision_comparison_ref=decision_comparison_ref,
        selection_signal_refs=selection_signal_refs,
    )
    working = _rebuild_session(replace(working, objective_reveal=reveal))
    exposure = record_exposure_event(
        context=working.context,
        kind="ENGINE_EVIDENCE_SHOWN",
        occurred_at=revealed_at,
        source="m5c-objective-evidence-reveal",
        details=(("reveal_id", reveal.reveal_id),),
    )
    working = _rebuild_session(
        replace(working, exposures=working.exposures + (exposure,))
    )
    return working, reveal
