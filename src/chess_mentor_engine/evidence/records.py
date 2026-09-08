"""Deterministic construction and identity for immutable M5 evidence records."""

from __future__ import annotations

import hashlib
from datetime import datetime

from chess_mentor_engine.analysis import PositionAnalysis
from chess_mentor_engine.chess import (
    CanonicalPosition,
    PositionContextPacket,
    canonical_json,
)
from chess_mentor_engine.selection import (
    DecisionComparison,
    DiagnosticCandidate,
    DiagnosticCandidateBatch,
    SelectionSignal,
)

from .model import (
    EvidenceFreeze,
    EvidenceReference,
    ExposureEvent,
    ExposureKind,
    InstrumentAwareness,
    InteractionClass,
    ObjectiveEvidenceReveal,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    PlayerResponseEvidence,
    PromptDefinition,
    PromptPresentation,
    StageKind,
)


class PlayerEvidenceError(ValueError):
    """Raised when immutable M5 evidence references are inconsistent."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _record_id(prefix: str, payload: object) -> str:
    return f"{prefix}_{_fingerprint(payload)[:20]}"


def _validate_timestamp(value: str) -> datetime:
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


def _reference(kind: str, ref_id: str, payload: object) -> EvidenceReference:
    return EvidenceReference(
        kind=kind,  # type: ignore[arg-type]
        ref_id=ref_id,
        fingerprint=_fingerprint(payload),
    )


def reference_position_analysis(analysis: PositionAnalysis) -> EvidenceReference:
    return EvidenceReference(
        kind="position_analysis",
        ref_id=analysis.result_fingerprint,
        fingerprint=_fingerprint(analysis.to_dict()),
    )


def reference_decision_comparison(
    comparison: DecisionComparison,
) -> EvidenceReference:
    return _reference(
        "decision_comparison",
        comparison.comparison_id,
        comparison.to_dict(),
    )


def reference_selection_signal(signal: SelectionSignal) -> EvidenceReference:
    return _reference("selection_signal", signal.signal_id, signal.to_dict())


def record_player_decision_context(
    *,
    participant_id: str,
    session_id: str,
    position: CanonicalPosition,
    position_context: PositionContextPacket,
    candidate: DiagnosticCandidate,
    created_at: str,
    batch: DiagnosticCandidateBatch | None = None,
) -> PlayerDecisionContext:
    """Bind one evidence-gathering context to qualified M4/canonical evidence."""
    _validate_timestamp(created_at)
    if not participant_id:
        raise PlayerEvidenceError("participant_id must not be empty")
    if not session_id:
        raise PlayerEvidenceError("session_id must not be empty")
    if position_context.position_id != position.position_id:
        raise PlayerEvidenceError("position context does not match canonical position")
    if position_context.game_id != position.game_id:
        raise PlayerEvidenceError("position context game_id mismatch")
    if candidate.position_id != position.position_id:
        raise PlayerEvidenceError("diagnostic candidate position_id mismatch")
    if candidate.game_id != position.game_id:
        raise PlayerEvidenceError("diagnostic candidate game_id mismatch")

    batch_ref: EvidenceReference | None = None
    if batch is not None:
        if candidate.candidate_id not in {
            item.candidate_id for item in batch.candidates
        }:
            raise PlayerEvidenceError("diagnostic candidate is not selected in batch")
        if batch.selection_policy != candidate.selection_policy:
            raise PlayerEvidenceError("batch/candidate selection policy mismatch")
        batch_ref = _reference("diagnostic_batch", batch.batch_id, batch.to_dict())

    candidate_ref = _reference(
        "diagnostic_candidate",
        candidate.candidate_id,
        candidate.to_dict(),
    )
    packet_ref = _reference(
        "position_context_packet",
        position_context.position_id,
        position_context.to_dict(),
    )
    payload = {
        "participant_id": participant_id,
        "session_id": session_id,
        "position_id": position.position_id,
        "game_id": position.game_id,
        "diagnostic_candidate_ref": candidate_ref.to_dict(),
        "diagnostic_batch_ref": None if batch_ref is None else batch_ref.to_dict(),
        "position_context_packet_ref": packet_ref.to_dict(),
        "selection_policy": candidate.selection_policy.to_dict(),
        "created_at": created_at,
    }
    return PlayerDecisionContext(
        context_id=_record_id("decision_context", payload),
        participant_id=participant_id,
        session_id=session_id,
        position_id=position.position_id,
        game_id=position.game_id,
        diagnostic_candidate_ref=candidate_ref,
        diagnostic_batch_ref=batch_ref,
        position_context_packet_ref=packet_ref,
        selection_policy=candidate.selection_policy,
        created_at=created_at,
    )


def define_prompt(
    *,
    name: str,
    version: str,
    stage_kind: StageKind,
    interaction_class: InteractionClass,
    content: tuple[str, ...],
    response_schema: tuple[str, ...] = (),
    provenance: tuple[tuple[str, str], ...] = (),
) -> PromptDefinition:
    """Create a material-content-addressed prompt definition."""
    if not name:
        raise PlayerEvidenceError("prompt name must not be empty")
    if not version:
        raise PlayerEvidenceError("prompt version must not be empty")
    if not content or not any(content):
        raise PlayerEvidenceError("prompt content must not be empty")
    normalized_provenance = _normalize_pairs(provenance, label="prompt provenance")
    payload = {
        "name": name,
        "version": version,
        "stage_kind": stage_kind,
        "interaction_class": interaction_class,
        "content": list(content),
        "response_schema": list(response_schema),
        "provenance": [list(item) for item in normalized_provenance],
    }
    fingerprint = _fingerprint(payload)
    return PromptDefinition(
        prompt_definition_id=f"prompt_{fingerprint[:20]}",
        definition_fingerprint=fingerprint,
        name=name,
        version=version,
        stage_kind=stage_kind,
        interaction_class=interaction_class,
        content=content,
        response_schema=response_schema,
        provenance=normalized_provenance,
    )


def record_exposure_event(
    *,
    context: PlayerDecisionContext,
    kind: ExposureKind,
    occurred_at: str,
    source: str,
    details: tuple[tuple[str, str], ...] = (),
    instrument_awareness: InstrumentAwareness | None = None,
) -> ExposureEvent:
    """Record one immutable information-exposure event."""
    _validate_timestamp(occurred_at)
    if not source:
        raise PlayerEvidenceError("exposure source must not be empty")
    normalized_details = _normalize_pairs(details, label="exposure details")
    if kind == "INSTRUMENT_AWARENESS_RECORDED":
        if instrument_awareness is None:
            raise PlayerEvidenceError(
                "instrument awareness event requires awareness state"
            )
    elif instrument_awareness is not None:
        raise PlayerEvidenceError(
            "instrument awareness belongs only to awareness exposure events"
        )
    payload = {
        "context_id": context.context_id,
        "participant_id": context.participant_id,
        "kind": kind,
        "occurred_at": occurred_at,
        "source": source,
        "details": [list(item) for item in normalized_details],
        "instrument_awareness": instrument_awareness,
    }
    return ExposureEvent(
        exposure_event_id=_record_id("exposure", payload),
        context_id=context.context_id,
        participant_id=context.participant_id,
        kind=kind,
        occurred_at=occurred_at,
        source=source,
        details=normalized_details,
        instrument_awareness=instrument_awareness,
    )


def record_prompt_presentation(
    *,
    context: PlayerDecisionContext,
    stage_id: str,
    prompt: PromptDefinition,
    shown_at: str,
    rendered_content: str,
    prior_exposures: tuple[ExposureEvent, ...] = (),
) -> PromptPresentation:
    """Record the exact prompt rendering and prior information state."""
    _validate_timestamp(shown_at)
    if not stage_id:
        raise PlayerEvidenceError("stage_id must not be empty")
    exposure_ids: list[str] = []
    for exposure in prior_exposures:
        if exposure.context_id != context.context_id:
            raise PlayerEvidenceError("prior exposure context_id mismatch")
        if exposure.participant_id != context.participant_id:
            raise PlayerEvidenceError("prior exposure participant_id mismatch")
        exposure_ids.append(exposure.exposure_event_id)
    if len(set(exposure_ids)) != len(exposure_ids):
        raise PlayerEvidenceError("prior exposures must be unique")
    information_state = tuple(sorted(exposure_ids))
    rendered_fingerprint = _fingerprint(rendered_content)
    payload = {
        "context_id": context.context_id,
        "stage_id": stage_id,
        "stage_kind": prompt.stage_kind,
        "prompt_definition_id": prompt.prompt_definition_id,
        "position_context_packet_ref": context.position_context_packet_ref.to_dict(),
        "shown_at": shown_at,
        "rendered_content_fingerprint": rendered_fingerprint,
        "information_available_before_presentation": list(information_state),
    }
    return PromptPresentation(
        presentation_id=_record_id("presentation", payload),
        context_id=context.context_id,
        stage_id=stage_id,
        stage_kind=prompt.stage_kind,
        prompt_definition_id=prompt.prompt_definition_id,
        position_context_packet_ref=context.position_context_packet_ref,
        shown_at=shown_at,
        rendered_content=rendered_content,
        rendered_content_fingerprint=rendered_fingerprint,
        information_available_before_presentation=information_state,
    )


def record_player_response(
    *,
    context: PlayerDecisionContext,
    presentation: PromptPresentation,
    raw_response: str,
    submitted_at: str,
    structured_response: ParticipantStructuredResponse | None = None,
) -> PlayerResponseEvidence:
    """Record immutable participant-authored evidence without interpreting prose."""
    _validate_timestamp(submitted_at)
    if presentation.context_id != context.context_id:
        raise PlayerEvidenceError("presentation context_id mismatch")
    payload = {
        "context_id": context.context_id,
        "stage_id": presentation.stage_id,
        "stage_kind": presentation.stage_kind,
        "presentation_id": presentation.presentation_id,
        "participant_id": context.participant_id,
        "raw_response": raw_response,
        "structured_response": (
            None if structured_response is None else structured_response.to_dict()
        ),
        "submitted_at": submitted_at,
    }
    fingerprint = _fingerprint(payload)
    return PlayerResponseEvidence(
        response_id=f"response_{fingerprint[:20]}",
        response_fingerprint=fingerprint,
        context_id=context.context_id,
        stage_id=presentation.stage_id,
        stage_kind=presentation.stage_kind,
        presentation_id=presentation.presentation_id,
        participant_id=context.participant_id,
        raw_response=raw_response,
        structured_response=structured_response,
        submitted_at=submitted_at,
    )


def record_evidence_freeze(
    *,
    context: PlayerDecisionContext,
    response: PlayerResponseEvidence,
    frozen_at: str,
) -> EvidenceFreeze:
    """Freeze the exact immutable response fingerprint as a separate event."""
    frozen_time = _validate_timestamp(frozen_at)
    submitted_time = _validate_timestamp(response.submitted_at)
    if response.context_id != context.context_id:
        raise PlayerEvidenceError("response context_id mismatch")
    if response.participant_id != context.participant_id:
        raise PlayerEvidenceError("response participant_id mismatch")
    if frozen_time < submitted_time:
        raise PlayerEvidenceError("freeze cannot precede response submission")
    payload = {
        "context_id": context.context_id,
        "stage_id": response.stage_id,
        "response_id": response.response_id,
        "frozen_at": frozen_at,
        "response_fingerprint": response.response_fingerprint,
    }
    return EvidenceFreeze(
        freeze_id=_record_id("freeze", payload),
        context_id=context.context_id,
        stage_id=response.stage_id,
        response_id=response.response_id,
        frozen_at=frozen_at,
        response_fingerprint=response.response_fingerprint,
    )


def record_objective_evidence_reveal(
    *,
    context: PlayerDecisionContext,
    revealed_at: str,
    rendered_content: str,
    position_analysis_refs: tuple[EvidenceReference, ...] = (),
    decision_comparison_ref: EvidenceReference | None = None,
    selection_signal_refs: tuple[EvidenceReference, ...] = (),
) -> ObjectiveEvidenceReveal:
    """Record objective evidence visibility without enforcing M5C reveal gating."""
    _validate_timestamp(revealed_at)
    if not (
        position_analysis_refs
        or decision_comparison_ref is not None
        or selection_signal_refs
    ):
        raise PlayerEvidenceError("objective reveal requires objective evidence refs")
    rendered_fingerprint = _fingerprint(rendered_content)
    payload = {
        "context_id": context.context_id,
        "revealed_at": revealed_at,
        "position_analysis_refs": [item.to_dict() for item in position_analysis_refs],
        "decision_comparison_ref": (
            None if decision_comparison_ref is None else decision_comparison_ref.to_dict()
        ),
        "selection_signal_refs": [item.to_dict() for item in selection_signal_refs],
        "rendered_content_fingerprint": rendered_fingerprint,
    }
    return ObjectiveEvidenceReveal(
        reveal_id=_record_id("reveal", payload),
        context_id=context.context_id,
        revealed_at=revealed_at,
        position_analysis_refs=position_analysis_refs,
        decision_comparison_ref=decision_comparison_ref,
        selection_signal_refs=selection_signal_refs,
        rendered_content=rendered_content,
        rendered_content_fingerprint=rendered_fingerprint,
    )
