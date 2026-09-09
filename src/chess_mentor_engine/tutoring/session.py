"""Bounded deterministic M8 tutor-session orchestration over qualified M5/M6/M7."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import PositionContextPacket, canonical_json
from chess_mentor_engine.evidence import (
    CaptureProtocol,
    EvidenceReference,
    ParticipantStructuredResponse,
    PlayerDecisionContext,
    PromptDefinition,
    capture_stage_response,
    freeze_stage_response,
    present_capture_stage,
    record_capture_exposure,
    reveal_objective_evidence,
    start_capture_session,
)
from chess_mentor_engine.learning import (
    HypothesisLedgerSnapshot,
    HypothesisRevision,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
    ReasoningDiscrepancyContext,
)

from .model import (
    TutorComparison,
    TutorExplanation,
    TutorExplanationProvenance,
    TutorHypothesisContext,
    TutorPositionPresentation,
    TutorSession,
    TutorSessionEvent,
    TutorSessionEventKind,
    TutorSessionState,
)

WORKFLOW_VERSION = "1"


class TutorSessionError(ValueError):
    """Raised when M8 sequencing, provenance, or claim boundaries are violated."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _record_id(prefix: str, payload: object) -> str:
    return f"{prefix}_{_fingerprint(payload)[:20]}"


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise TutorSessionError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TutorSessionError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TutorSessionError("timestamp must include an explicit timezone")
    return parsed


def _rebuild(session: TutorSession) -> TutorSession:
    payload = session.to_dict(include_snapshot_fingerprint=False)
    return replace(session, snapshot_fingerprint=_fingerprint(payload))


def _advance(
    session: TutorSession,
    *,
    kind: TutorSessionEventKind,
    to_state: TutorSessionState,
    occurred_at: str,
    artifact_id: str,
    artifact_fingerprint: str,
    updates: dict[str, Any] | None = None,
) -> TutorSession:
    occurred = _parse_timestamp(occurred_at)
    latest = _parse_timestamp(session.events[-1].occurred_at)
    if occurred < latest:
        raise TutorSessionError("tutor session events must be chronological")
    sequence = len(session.events)
    payload = {
        "tutor_session_id": session.tutor_session_id,
        "sequence": sequence,
        "kind": kind,
        "from_state": session.state,
        "to_state": to_state,
        "occurred_at": occurred_at,
        "artifact_id": artifact_id,
        "artifact_fingerprint": artifact_fingerprint,
    }
    event = TutorSessionEvent(
        event_id=_record_id("tutor_event", payload),
        sequence=sequence,
        kind=kind,
        from_state=session.state,
        to_state=to_state,
        occurred_at=occurred_at,
        artifact_id=artifact_id,
        artifact_fingerprint=artifact_fingerprint,
    )
    values = {} if updates is None else dict(updates)
    values.update(state=to_state, events=session.events + (event,))
    return _rebuild(replace(session, **values))


def _validate_capture_protocol(protocol: CaptureProtocol) -> None:
    if any(stage.phase != "pre_reveal" for stage in protocol.stages):
        raise TutorSessionError("M8 v1 capture protocol must be pre-reveal only")
    stage_kinds = tuple(stage.stage_kind for stage in protocol.stages)
    allowed = {
        ("MINIMAL_RESPONSE",),
        ("MINIMAL_RESPONSE", "STANDARDIZED_PROBE"),
    }
    if stage_kinds not in allowed:
        raise TutorSessionError(
            "M8 v1 requires minimal response with optional standardized probe"
        )


def start_tutor_session(
    *,
    context: PlayerDecisionContext,
    capture_protocol: CaptureProtocol,
    created_at: str,
) -> TutorSession:
    """Start one immutable M8 session around an exact qualified M5 decision context."""
    _validate_capture_protocol(capture_protocol)
    if _parse_timestamp(created_at) < _parse_timestamp(context.created_at):
        raise TutorSessionError("tutor session cannot predate player decision context")
    capture = start_capture_session(context=context, protocol=capture_protocol)
    identity_payload = {
        "workflow_version": WORKFLOW_VERSION,
        "context_id": context.context_id,
        "capture_protocol_id": capture_protocol.protocol_id,
        "capture_protocol_fingerprint": capture_protocol.protocol_fingerprint,
    }
    tutor_session_id = _record_id("tutor_session", identity_payload)
    event_payload = {
        "tutor_session_id": tutor_session_id,
        "sequence": 0,
        "kind": "SESSION_STARTED",
        "from_state": "selected",
        "to_state": "selected",
        "occurred_at": created_at,
        "artifact_id": capture.capture_session_id,
        "artifact_fingerprint": capture.snapshot_fingerprint,
    }
    event = TutorSessionEvent(
        event_id=_record_id("tutor_event", event_payload),
        sequence=0,
        kind="SESSION_STARTED",
        from_state="selected",
        to_state="selected",
        occurred_at=created_at,
        artifact_id=capture.capture_session_id,
        artifact_fingerprint=capture.snapshot_fingerprint,
    )
    return _rebuild(
        TutorSession(
            tutor_session_id=tutor_session_id,
            snapshot_fingerprint="pending",
            workflow_version=WORKFLOW_VERSION,
            state="selected",
            capture_session=capture,
            position_presentation=None,
            comparison=None,
            hypothesis_context=None,
            explanation=None,
            events=(event,),
            created_at=created_at,
        )
    )


def _render_position(packet: PositionContextPacket) -> str:
    return "\n".join(
        (
            f"Move {packet.move_number} — {packet.side_to_move} to move",
            f"FEN: {packet.fen}",
            packet.board_ascii,
        )
    )


def present_tutor_position(
    session: TutorSession,
    *,
    position_context: PositionContextPacket,
    shown_at: str,
) -> tuple[TutorSession, TutorPositionPresentation]:
    """Present deterministic position context without accepting engine-derived input."""
    if session.state != "selected":
        raise TutorSessionError("position can only be presented from selected state")
    context = session.capture_session.context
    if position_context.position_id != context.position_id:
        raise TutorSessionError("position context position_id mismatch")
    if position_context.game_id != context.game_id:
        raise TutorSessionError("position context game_id mismatch")
    packet_fingerprint = _fingerprint(position_context.to_dict())
    if packet_fingerprint != context.position_context_packet_ref.fingerprint:
        raise TutorSessionError("position context fingerprint mismatch")
    rendered = _render_position(position_context)
    payload = {
        "tutor_session_id": session.tutor_session_id,
        "position_context": position_context.to_dict(),
        "rendered_content": rendered,
        "shown_at": shown_at,
    }
    fingerprint = _fingerprint(payload)
    presentation = TutorPositionPresentation(
        presentation_id=f"tutor_position_{fingerprint[:20]}",
        fingerprint=fingerprint,
        tutor_session_id=session.tutor_session_id,
        position_context=position_context,
        rendered_content=rendered,
        shown_at=shown_at,
    )
    capture, _ = record_capture_exposure(
        session.capture_session,
        kind="POSITION_CONTEXT_SHOWN",
        occurred_at=shown_at,
        source="m8-evidence-aware-tutor-session",
        details=(("tutor_position_id", presentation.presentation_id),),
    )
    updated = _advance(
        session,
        kind="POSITION_PRESENTED",
        to_state="presented",
        occurred_at=shown_at,
        artifact_id=presentation.presentation_id,
        artifact_fingerprint=presentation.fingerprint,
        updates={
            "capture_session": capture,
            "position_presentation": presentation,
        },
    )
    return updated, presentation


def present_tutor_capture_stage(
    session: TutorSession,
    *,
    stage_id: str,
    prompt: PromptDefinition,
    shown_at: str,
) -> TutorSession:
    """Present a pre-reveal observation/probe prompt via the qualified M5 machine."""
    if session.state not in {"presented", "capturing"}:
        raise TutorSessionError("capture prompt requires presented/capturing state")
    expected_class = {
        "MINIMAL_RESPONSE": "observation",
        "STANDARDIZED_PROBE": "diagnostic_probing",
    }.get(prompt.stage_kind)
    if expected_class is None or prompt.interaction_class != expected_class:
        raise TutorSessionError(
            "M8 pre-reveal prompts must be observation or diagnostic probing"
        )
    capture, presentation = present_capture_stage(
        session.capture_session,
        stage_id=stage_id,
        prompt=prompt,
        shown_at=shown_at,
        rendered_content="\n".join(prompt.content),
    )
    return _advance(
        session,
        kind="CAPTURE_STAGE_PRESENTED",
        to_state="capturing",
        occurred_at=shown_at,
        artifact_id=presentation.presentation_id,
        artifact_fingerprint=_fingerprint(presentation.to_dict()),
        updates={"capture_session": capture},
    )


def capture_tutor_response(
    session: TutorSession,
    *,
    stage_id: str,
    raw_response: str,
    submitted_at: str,
    structured_response: ParticipantStructuredResponse | None = None,
) -> TutorSession:
    """Append one participant-authored response without rewriting earlier evidence."""
    if session.state != "capturing":
        raise TutorSessionError("response capture requires capturing state")
    capture, response = capture_stage_response(
        session.capture_session,
        stage_id=stage_id,
        raw_response=raw_response,
        structured_response=structured_response,
        submitted_at=submitted_at,
    )
    return _advance(
        session,
        kind="RESPONSE_CAPTURED",
        to_state="capturing",
        occurred_at=submitted_at,
        artifact_id=response.response_id,
        artifact_fingerprint=response.response_fingerprint,
        updates={"capture_session": capture},
    )


def freeze_tutor_response(
    session: TutorSession,
    *,
    stage_id: str,
    frozen_at: str,
) -> TutorSession:
    """Freeze a response; become frozen once all planned stages are frozen."""
    if session.state != "capturing":
        raise TutorSessionError("response freeze requires capturing state")
    capture, freeze = freeze_stage_response(
        session.capture_session,
        stage_id=stage_id,
        frozen_at=frozen_at,
    )
    frozen_stage_ids = {item.stage_id for item in capture.freezes}
    required_stage_ids = {item.stage_id for item in capture.protocol.pre_reveal_stages}
    next_state: TutorSessionState = (
        "frozen" if frozen_stage_ids == required_stage_ids else "capturing"
    )
    return _advance(
        session,
        kind="RESPONSE_FROZEN",
        to_state=next_state,
        occurred_at=frozen_at,
        artifact_id=freeze.freeze_id,
        artifact_fingerprint=freeze.response_fingerprint,
        updates={"capture_session": capture},
    )


def reveal_tutor_objective_evidence(
    session: TutorSession,
    *,
    revealed_at: str,
    rendered_content: str,
    position_analysis_refs: tuple[EvidenceReference, ...] = (),
    decision_comparison_ref: EvidenceReference | None = None,
    selection_signal_refs: tuple[EvidenceReference, ...] = (),
) -> TutorSession:
    """Reveal qualified objective evidence only after the pre-reveal freeze boundary."""
    if session.state != "frozen":
        raise TutorSessionError(
            "objective reveal requires all pre-reveal evidence frozen"
        )
    if not rendered_content:
        raise TutorSessionError("objective reveal content must not be empty")
    capture, reveal = reveal_objective_evidence(
        session.capture_session,
        revealed_at=revealed_at,
        rendered_content=rendered_content,
        position_analysis_refs=position_analysis_refs,
        decision_comparison_ref=decision_comparison_ref,
        selection_signal_refs=selection_signal_refs,
    )
    return _advance(
        session,
        kind="OBJECTIVE_EVIDENCE_REVEALED",
        to_state="revealed",
        occurred_at=revealed_at,
        artifact_id=reveal.reveal_id,
        artifact_fingerprint=reveal.rendered_content_fingerprint,
        updates={"capture_session": capture},
    )


def _validate_reasoning_context(
    session: TutorSession,
    context: ReasoningDiscrepancyContext,
) -> None:
    expected_fingerprint = _fingerprint(context.to_dict(include_identity=False))
    if context.context_fingerprint != expected_fingerprint:
        raise TutorSessionError("M6 reasoning context fingerprint mismatch")
    if context.reasoning_context_id != f"reasoning_context_{expected_fingerprint[:20]}":
        raise TutorSessionError("M6 reasoning context identity mismatch")
    m5_context = session.capture_session.context
    if context.participant_id != m5_context.participant_id:
        raise TutorSessionError("M6 reasoning context participant mismatch")
    if (
        context.position_id != m5_context.position_id
        or context.game_id != m5_context.game_id
    ):
        raise TutorSessionError("M6 reasoning context position/game mismatch")
    if context.capture_session_ref.ref_id != session.capture_session.capture_session_id:
        raise TutorSessionError("M6 reasoning context capture session mismatch")
    if (
        context.capture_session_ref.fingerprint
        != session.capture_session.snapshot_fingerprint
    ):
        raise TutorSessionError("M6 reasoning context capture fingerprint mismatch")


def _validate_reasoning_assessment(
    context: ReasoningDiscrepancyContext,
    assessment: ReasoningDiscrepancyAssessment,
    assertions: tuple[ReasoningDiscrepancyAssertion, ...],
) -> None:
    expected_fingerprint = _fingerprint(assessment.to_dict(include_identity=False))
    if assessment.fingerprint != expected_fingerprint:
        raise TutorSessionError("M6 assessment fingerprint mismatch")
    expected_id = f"reasoning_assessment_{expected_fingerprint[:20]}"
    if assessment.assessment_id != expected_id:
        raise TutorSessionError("M6 assessment identity mismatch")
    if assessment.reasoning_context_id != context.reasoning_context_id:
        raise TutorSessionError("M6 assessment reasoning context mismatch")
    supplied = {(item.assertion_id, item.fingerprint) for item in assertions}
    referenced = {(item.ref_id, item.fingerprint) for item in assessment.assertion_refs}
    if supplied != referenced:
        raise TutorSessionError("supplied M6 assertions do not match assessment refs")
    for assertion in assertions:
        fingerprint = _fingerprint(assertion.to_dict(include_identity=False))
        if assertion.fingerprint != fingerprint:
            raise TutorSessionError("M6 assertion fingerprint mismatch")
        if assertion.assertion_id != f"reasoning_assertion_{fingerprint[:20]}":
            raise TutorSessionError("M6 assertion identity mismatch")
        if assertion.reasoning_context_id != context.reasoning_context_id:
            raise TutorSessionError("M6 assertion reasoning context mismatch")
        if assertion.assessment_policy_ref != assessment.assessment_policy_ref:
            raise TutorSessionError("M6 assertion/assessment policy mismatch")


def record_tutor_reasoning_comparison(
    session: TutorSession,
    *,
    reasoning_context: ReasoningDiscrepancyContext,
    assessment: ReasoningDiscrepancyAssessment,
    assertions: tuple[ReasoningDiscrepancyAssertion, ...],
    recorded_at: str,
) -> tuple[TutorSession, TutorComparison]:
    """Attach exact qualified M6 output after reveal without reinterpreting it."""
    if session.state != "revealed":
        raise TutorSessionError("reasoning comparison requires revealed state")
    reveal = session.capture_session.objective_reveal
    assert reveal is not None
    _validate_reasoning_context(session, reasoning_context)
    _validate_reasoning_assessment(reasoning_context, assessment, assertions)
    if _parse_timestamp(reasoning_context.created_at) < _parse_timestamp(
        reveal.revealed_at
    ):
        raise TutorSessionError("M6 reasoning context cannot predate objective reveal")
    if _parse_timestamp(assessment.created_at) < _parse_timestamp(
        reasoning_context.created_at
    ):
        raise TutorSessionError("M6 assessment cannot predate reasoning context")
    if _parse_timestamp(recorded_at) < _parse_timestamp(assessment.created_at):
        raise TutorSessionError("comparison record cannot predate M6 assessment")
    ordered = tuple(sorted(assertions, key=lambda item: item.assertion_id))
    payload = {
        "tutor_session_id": session.tutor_session_id,
        "reasoning_context": reasoning_context.to_dict(),
        "assessment": assessment.to_dict(),
        "assertions": [item.to_dict() for item in ordered],
        "recorded_at": recorded_at,
    }
    fingerprint = _fingerprint(payload)
    comparison = TutorComparison(
        comparison_id=f"tutor_comparison_{fingerprint[:20]}",
        fingerprint=fingerprint,
        tutor_session_id=session.tutor_session_id,
        reasoning_context=reasoning_context,
        assessment=assessment,
        assertions=ordered,
        recorded_at=recorded_at,
    )
    updated = _advance(
        session,
        kind="REASONING_COMPARISON_RECORDED",
        to_state="compared",
        occurred_at=recorded_at,
        artifact_id=comparison.comparison_id,
        artifact_fingerprint=comparison.fingerprint,
        updates={"comparison": comparison},
    )
    return updated, comparison


def _validate_revision(revision: HypothesisRevision) -> None:
    fingerprint = _fingerprint(revision.to_dict(include_identity=False))
    if revision.fingerprint != fingerprint:
        raise TutorSessionError("M7 hypothesis revision fingerprint mismatch")
    if revision.revision_id != f"hypothesis_revision_{fingerprint[:20]}":
        raise TutorSessionError("M7 hypothesis revision identity mismatch")


def attach_tutor_hypothesis_context(
    session: TutorSession,
    *,
    ledger_snapshot: HypothesisLedgerSnapshot,
    active_revisions: tuple[HypothesisRevision, ...],
    attached_at: str,
) -> tuple[TutorSession, TutorHypothesisContext]:
    """Attach the complete active-current M7 view, never a cherry-picked subset."""
    if session.state != "compared":
        raise TutorSessionError("hypothesis context requires compared state")
    if session.hypothesis_context is not None:
        raise TutorSessionError("hypothesis context is already attached")
    if ledger_snapshot.participant_id != session.capture_session.context.participant_id:
        raise TutorSessionError("M7 ledger participant does not match tutor session")
    snapshot_fingerprint = _fingerprint(
        ledger_snapshot.to_dict(include_identity=False)
    )
    if ledger_snapshot.fingerprint != snapshot_fingerprint:
        raise TutorSessionError("M7 ledger snapshot fingerprint mismatch")
    expected_snapshot_id = f"hypothesis_ledger_snapshot_{snapshot_fingerprint[:20]}"
    if ledger_snapshot.snapshot_id != expected_snapshot_id:
        raise TutorSessionError("M7 ledger snapshot identity mismatch")
    active_entries = tuple(
        item
        for item in ledger_snapshot.entries
        if item.authority_lifecycle_state == "active"
    )
    required_ids = {item.current_revision_ref.revision_id for item in active_entries}
    supplied = {item.revision_id: item for item in active_revisions}
    if set(supplied) != required_ids:
        raise TutorSessionError(
            "M8 hypothesis context requires every active current M7 revision"
        )
    for entry in active_entries:
        revision = supplied[entry.current_revision_ref.revision_id]
        _validate_revision(revision)
        ref = entry.current_revision_ref
        if (
            revision.hypothesis_id != ref.hypothesis_id
            or revision.revision_number != ref.revision_number
            or revision.fingerprint != ref.fingerprint
        ):
            raise TutorSessionError("M7 active revision does not match ledger snapshot")
    comparison = session.comparison
    assert comparison is not None
    if _parse_timestamp(attached_at) < _parse_timestamp(comparison.recorded_at):
        raise TutorSessionError("hypothesis context cannot predate comparison")
    if _parse_timestamp(attached_at) < _parse_timestamp(ledger_snapshot.created_at):
        raise TutorSessionError("hypothesis context cannot predate ledger snapshot")
    ordered = tuple(sorted(active_revisions, key=lambda item: item.revision_id))
    payload = {
        "tutor_session_id": session.tutor_session_id,
        "ledger_snapshot": ledger_snapshot.to_dict(),
        "active_revisions": [item.to_dict() for item in ordered],
        "attached_at": attached_at,
    }
    fingerprint = _fingerprint(payload)
    context = TutorHypothesisContext(
        context_id=f"tutor_hypothesis_context_{fingerprint[:20]}",
        fingerprint=fingerprint,
        tutor_session_id=session.tutor_session_id,
        ledger_snapshot=ledger_snapshot,
        active_revisions=ordered,
        attached_at=attached_at,
    )
    updated = _advance(
        session,
        kind="HYPOTHESIS_CONTEXT_ATTACHED",
        to_state="compared",
        occurred_at=attached_at,
        artifact_id=context.context_id,
        artifact_fingerprint=context.fingerprint,
        updates={"hypothesis_context": context},
    )
    return updated, context


def record_tutor_explanation(
    session: TutorSession,
    *,
    rendered_content: str,
    provenance: TutorExplanationProvenance,
    created_at: str,
) -> tuple[TutorSession, TutorExplanation]:
    """Record post-comparison explanation without granting pedagogical authority."""
    if session.state != "compared":
        raise TutorSessionError("explanation requires compared state")
    if not rendered_content:
        raise TutorSessionError("explanation content must not be empty")
    if provenance.actor_kind not in {"human", "model", "template"}:
        raise TutorSessionError("unknown explanation actor kind")
    comparison = session.comparison
    assert comparison is not None
    lower_bound = _parse_timestamp(comparison.recorded_at)
    hypothesis_context_id: str | None = None
    hypothesis_context_fingerprint: str | None = None
    if session.hypothesis_context is not None:
        lower_bound = max(
            lower_bound,
            _parse_timestamp(session.hypothesis_context.attached_at),
        )
        hypothesis_context_id = session.hypothesis_context.context_id
        hypothesis_context_fingerprint = session.hypothesis_context.fingerprint
    if _parse_timestamp(created_at) < lower_bound:
        raise TutorSessionError("explanation cannot predate its evidence context")
    payload = {
        "tutor_session_id": session.tutor_session_id,
        "comparison_id": comparison.comparison_id,
        "comparison_fingerprint": comparison.fingerprint,
        "hypothesis_context_id": hypothesis_context_id,
        "hypothesis_context_fingerprint": hypothesis_context_fingerprint,
        "rendered_content": rendered_content,
        "provenance": provenance.to_dict(),
        "created_at": created_at,
        "claim_scope": "session_local_evidence_explanation",
    }
    fingerprint = _fingerprint(payload)
    explanation = TutorExplanation(
        explanation_id=f"tutor_explanation_{fingerprint[:20]}",
        fingerprint=fingerprint,
        tutor_session_id=session.tutor_session_id,
        comparison_id=comparison.comparison_id,
        comparison_fingerprint=comparison.fingerprint,
        hypothesis_context_id=hypothesis_context_id,
        hypothesis_context_fingerprint=hypothesis_context_fingerprint,
        rendered_content=rendered_content,
        provenance=provenance,
        created_at=created_at,
    )
    updated = _advance(
        session,
        kind="EXPLANATION_RECORDED",
        to_state="explained",
        occurred_at=created_at,
        artifact_id=explanation.explanation_id,
        artifact_fingerprint=explanation.fingerprint,
        updates={"explanation": explanation},
    )
    return updated, explanation


def complete_tutor_session(
    session: TutorSession,
    *,
    completed_at: str,
) -> TutorSession:
    """Close a fully explained M8 session without adding M9 intervention state."""
    if session.state != "explained":
        raise TutorSessionError("session completion requires explained state")
    explanation = session.explanation
    assert explanation is not None
    if _parse_timestamp(completed_at) < _parse_timestamp(explanation.created_at):
        raise TutorSessionError("session completion cannot predate explanation")
    return _advance(
        session,
        kind="SESSION_COMPLETED",
        to_state="completed",
        occurred_at=completed_at,
        artifact_id=explanation.explanation_id,
        artifact_fingerprint=explanation.fingerprint,
        updates={"completed_at": completed_at},
    )
