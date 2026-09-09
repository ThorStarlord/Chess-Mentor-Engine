"""Deterministic M6B comparison of explicit M5 values with qualified evidence."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from chess_mentor_engine.analysis import AnalysisFailure, PositionAnalysis
from chess_mentor_engine.chess import (
    CanonicalPosition,
    PositionFeaturePacket,
    canonical_json,
)
from chess_mentor_engine.chess._core import Board
from chess_mentor_engine.evidence import (
    EvidenceCaptureSession,
    EvidenceFreeze,
    PlayerResponseEvidence,
    PromptPresentation,
)
from chess_mentor_engine.selection import DecisionComparison, SelectionSignal

from .model import (
    DiscrepancyFact,
    DiscrepancyFactKind,
    DiscrepancyRelation,
    MeasurementCondition,
    ReasoningDiscrepancyContext,
    ReasoningEvidenceAuthority,
    ReasoningEvidenceKind,
    ReasoningEvidenceRef,
)

AnalysisRecord = PositionAnalysis | AnalysisFailure
_ALLOWED_PRIMARY_STAGE_KINDS = {"MINIMAL_RESPONSE", "STANDARDIZED_PROBE"}
_FACT_ORDER: tuple[DiscrepancyFactKind, ...] = (
    "REPORTED_SELECTED_MOVE_RELATION",
    "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
    "EXPECTED_REPLY_RELATION",
    "EXPECTED_CONTINUATION_RELATION",
)


class ReasoningDiscrepancyError(ValueError):
    """Raised when M6B inputs violate frozen M4/M5 provenance boundaries."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _record_id(prefix: str, payload: object) -> str:
    return f"{prefix}_{_fingerprint(payload)[:20]}"


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise ReasoningDiscrepancyError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReasoningDiscrepancyError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReasoningDiscrepancyError("timestamp must include an explicit timezone")
    return parsed


def _ref(
    *,
    authority: ReasoningEvidenceAuthority,
    kind: ReasoningEvidenceKind,
    ref_id: str,
    payload: object,
    fingerprint: str | None = None,
) -> ReasoningEvidenceRef:
    return ReasoningEvidenceRef(
        authority=authority,
        kind=kind,
        ref_id=ref_id,
        fingerprint=fingerprint or _fingerprint(payload),
    )


def _analysis_ref(record: AnalysisRecord) -> ReasoningEvidenceRef:
    if isinstance(record, PositionAnalysis):
        return _ref(
            authority="engine_evidence",
            kind="position_analysis",
            ref_id=record.result_fingerprint,
            payload=record.to_dict(),
        )
    payload = record.to_dict()
    return _ref(
        authority="engine_evidence",
        kind="analysis_failure",
        ref_id=_record_id("analysis_failure", payload),
        payload=payload,
    )


def _measurement_condition(session: EvidenceCaptureSession) -> MeasurementCondition:
    if session.contaminated:
        return "contaminated"
    if session.deviations:
        return "deviating"
    if any(
        exposure.kind == "INSTRUMENT_AWARENESS_RECORDED"
        and exposure.instrument_awareness == "known_aware"
        for exposure in session.exposures
    ):
        return "instrument_aware_clean"
    return "clean"


def _selected_stage_records(
    session: EvidenceCaptureSession,
    requested_stage_ids: tuple[str, ...],
) -> tuple[
    tuple[str, ...],
    tuple[PromptPresentation, ...],
    tuple[PlayerResponseEvidence, ...],
    tuple[EvidenceFreeze, ...],
]:
    if not requested_stage_ids:
        raise ReasoningDiscrepancyError("assessment_stage_ids must not be empty")
    if len(set(requested_stage_ids)) != len(requested_stage_ids):
        raise ReasoningDiscrepancyError("assessment_stage_ids must be unique")

    requested = set(requested_stage_ids)
    protocol_stages = {item.stage_id: item for item in session.protocol.stages}
    unknown = requested.difference(protocol_stages)
    if unknown:
        raise ReasoningDiscrepancyError(
            f"assessment stage is not in capture protocol: {sorted(unknown)!r}"
        )

    ordered_ids = tuple(
        item.stage_id for item in session.protocol.stages if item.stage_id in requested
    )
    presentations: list[PromptPresentation] = []
    responses: list[PlayerResponseEvidence] = []
    freezes: list[EvidenceFreeze] = []

    for stage_id in ordered_ids:
        stage = protocol_stages[stage_id]
        if (
            stage.phase != "pre_reveal"
            or stage.stage_kind not in _ALLOWED_PRIMARY_STAGE_KINDS
        ):
            raise ReasoningDiscrepancyError(
                "M6B primary assessment stages must be frozen pre-reveal evidence"
            )
        stage_presentations = [
            item for item in session.presentations if item.stage_id == stage_id
        ]
        stage_responses = [
            item for item in session.responses if item.stage_id == stage_id
        ]
        stage_freezes = [
            item for item in session.freezes if item.stage_id == stage_id
        ]
        if (
            len(stage_presentations) != 1
            or len(stage_responses) != 1
            or len(stage_freezes) != 1
        ):
            raise ReasoningDiscrepancyError(
                f"stage {stage_id!r} must have exactly one presentation, "
                "response, and freeze"
            )
        presentation = stage_presentations[0]
        response = stage_responses[0]
        freeze = stage_freezes[0]
        if response.presentation_id != presentation.presentation_id:
            raise ReasoningDiscrepancyError("response/presentation linkage mismatch")
        if freeze.response_id != response.response_id:
            raise ReasoningDiscrepancyError("freeze/response linkage mismatch")
        if freeze.response_fingerprint != response.response_fingerprint:
            raise ReasoningDiscrepancyError(
                "freeze does not bind exact response fingerprint"
            )
        presentations.append(presentation)
        responses.append(response)
        freezes.append(freeze)

    return ordered_ids, tuple(presentations), tuple(responses), tuple(freezes)


def _validate_objective_inputs(
    *,
    position: CanonicalPosition,
    decision_comparison: DecisionComparison,
    position_features: PositionFeaturePacket | None,
    position_analyses: tuple[AnalysisRecord, ...],
    selection_signals: tuple[SelectionSignal, ...],
) -> None:
    if decision_comparison.position_id != position.position_id:
        raise ReasoningDiscrepancyError("decision comparison position_id mismatch")
    if decision_comparison.game_id != position.game_id:
        raise ReasoningDiscrepancyError("decision comparison game_id mismatch")
    if position_features is not None:
        if position_features.position_id != position.position_id:
            raise ReasoningDiscrepancyError(
                "position feature packet position_id mismatch"
            )
        if position_features.game_id != position.game_id:
            raise ReasoningDiscrepancyError("position feature packet game_id mismatch")
        if position_features.fen != position.fen:
            raise ReasoningDiscrepancyError("position feature packet FEN mismatch")

    allowed_analysis_positions = {decision_comparison.root_analysis_ref.position_id}
    if decision_comparison.played_analysis_ref is not None:
        allowed_analysis_positions.add(decision_comparison.played_analysis_ref.position_id)
    seen_analysis_refs: set[str] = set()
    for record in position_analyses:
        if record.position_id not in allowed_analysis_positions:
            raise ReasoningDiscrepancyError(
                "analysis record is not referenced by the decision comparison"
            )
        ref = _analysis_ref(record)
        if ref.ref_id in seen_analysis_refs:
            raise ReasoningDiscrepancyError("position analyses must be unique")
        seen_analysis_refs.add(ref.ref_id)
        if record.position_id == decision_comparison.root_analysis_ref.position_id:
            expected = decision_comparison.root_analysis_ref
            if record.request_fingerprint != expected.request_fingerprint:
                raise ReasoningDiscrepancyError(
                    "root analysis request fingerprint mismatch"
                )
            if isinstance(record, PositionAnalysis):
                if record.result_fingerprint != expected.result_fingerprint:
                    raise ReasoningDiscrepancyError(
                        "root analysis result fingerprint mismatch"
                    )
            elif expected.failure_code != record.code:
                raise ReasoningDiscrepancyError("root analysis failure code mismatch")

    signal_ids: set[str] = set()
    for signal in selection_signals:
        if signal.signal_id in signal_ids:
            raise ReasoningDiscrepancyError("selection signals must be unique")
        signal_ids.add(signal.signal_id)
        if signal.position_id != position.position_id:
            raise ReasoningDiscrepancyError("selection signal position_id mismatch")
        if signal.game_id != position.game_id:
            raise ReasoningDiscrepancyError("selection signal game_id mismatch")
        if signal.comparison_id != decision_comparison.comparison_id:
            raise ReasoningDiscrepancyError("selection signal comparison_id mismatch")


def build_reasoning_discrepancy_context(
    *,
    capture_session: EvidenceCaptureSession,
    position: CanonicalPosition,
    decision_comparison: DecisionComparison,
    assessment_stage_ids: tuple[str, ...],
    created_at: str,
    position_features: PositionFeaturePacket | None = None,
    position_analyses: tuple[AnalysisRecord, ...] = (),
    selection_signals: tuple[SelectionSignal, ...] = (),
) -> ReasoningDiscrepancyContext:
    """Bind one M6B context to exact frozen M4/M5 evidence."""
    created_time = _parse_timestamp(created_at)
    m5_context = capture_session.context
    if m5_context.position_id != position.position_id:
        raise ReasoningDiscrepancyError("M5 context position_id mismatch")
    if m5_context.game_id != position.game_id:
        raise ReasoningDiscrepancyError("M5 context game_id mismatch")
    _validate_objective_inputs(
        position=position,
        decision_comparison=decision_comparison,
        position_features=position_features,
        position_analyses=position_analyses,
        selection_signals=selection_signals,
    )
    stage_ids, presentations, responses, freezes = _selected_stage_records(
        capture_session,
        assessment_stage_ids,
    )
    if any(created_time < _parse_timestamp(item.frozen_at) for item in freezes):
        raise ReasoningDiscrepancyError(
            "M6 context cannot precede selected evidence freeze"
        )

    player_context_ref = _ref(
        authority="m5_participant",
        kind="player_decision_context",
        ref_id=m5_context.context_id,
        payload=m5_context.to_dict(),
    )
    candidate_ref = ReasoningEvidenceRef(
        authority="m4_objective",
        kind="diagnostic_candidate",
        ref_id=m5_context.diagnostic_candidate_ref.ref_id,
        fingerprint=m5_context.diagnostic_candidate_ref.fingerprint,
    )
    batch_ref = None
    if m5_context.diagnostic_batch_ref is not None:
        batch_ref = ReasoningEvidenceRef(
            authority="m4_objective",
            kind="diagnostic_batch",
            ref_id=m5_context.diagnostic_batch_ref.ref_id,
            fingerprint=m5_context.diagnostic_batch_ref.fingerprint,
        )
    capture_ref = _ref(
        authority="m5_participant",
        kind="capture_session",
        ref_id=capture_session.capture_session_id,
        payload=capture_session.to_dict(include_snapshot_fingerprint=False),
        fingerprint=capture_session.snapshot_fingerprint,
    )
    presentation_refs = tuple(
        _ref(
            authority="m5_participant",
            kind="prompt_presentation",
            ref_id=item.presentation_id,
            payload=item.to_dict(),
        )
        for item in presentations
    )
    response_refs = tuple(
        _ref(
            authority="m5_participant",
            kind="player_response",
            ref_id=item.response_id,
            payload=item.to_dict(),
            fingerprint=item.response_fingerprint,
        )
        for item in responses
    )
    freeze_refs = tuple(
        _ref(
            authority="m5_participant",
            kind="evidence_freeze",
            ref_id=item.freeze_id,
            payload=item.to_dict(),
        )
        for item in freezes
    )
    exposure_refs = tuple(
        sorted(
            (
                _ref(
                    authority="m5_participant",
                    kind="exposure_event",
                    ref_id=item.exposure_event_id,
                    payload=item.to_dict(),
                )
                for item in capture_session.exposures
            ),
            key=lambda item: item.ref_id,
        )
    )
    deviation_refs = tuple(
        sorted(
            (
                _ref(
                    authority="m5_participant",
                    kind="protocol_deviation",
                    ref_id=item.deviation_id,
                    payload=item.to_dict(),
                )
                for item in capture_session.deviations
            ),
            key=lambda item: item.ref_id,
        )
    )
    canonical_position_ref = _ref(
        authority="deterministic_chess",
        kind="canonical_position",
        ref_id=position.position_id,
        payload=position.to_dict(),
    )
    feature_ref = None
    if position_features is not None:
        feature_ref = _ref(
            authority="deterministic_chess",
            kind="position_feature_packet",
            ref_id=position_features.position_id,
            payload=position_features.to_dict(),
        )
    analysis_refs = tuple(
        sorted(
            (_analysis_ref(item) for item in position_analyses),
            key=lambda item: item.ref_id,
        )
    )
    comparison_ref = _ref(
        authority="m4_objective",
        kind="decision_comparison",
        ref_id=decision_comparison.comparison_id,
        payload=decision_comparison.to_dict(),
    )
    signal_refs = tuple(
        sorted(
            (
                _ref(
                    authority="m4_objective",
                    kind="selection_signal",
                    ref_id=item.signal_id,
                    payload=item.to_dict(),
                )
                for item in selection_signals
            ),
            key=lambda item: item.ref_id,
        )
    )

    payload: dict[str, Any] = {
        "participant_id": m5_context.participant_id,
        "player_decision_context_ref": player_context_ref.to_dict(),
        "position_id": position.position_id,
        "game_id": position.game_id,
        "diagnostic_candidate_ref": candidate_ref.to_dict(),
        "diagnostic_batch_ref": None if batch_ref is None else batch_ref.to_dict(),
        "capture_session_ref": capture_ref.to_dict(),
        "assessment_stage_ids": list(stage_ids),
        "player_response_refs": [item.to_dict() for item in response_refs],
        "evidence_freeze_refs": [item.to_dict() for item in freeze_refs],
        "prompt_presentation_refs": [item.to_dict() for item in presentation_refs],
        "exposure_refs": [item.to_dict() for item in exposure_refs],
        "protocol_deviation_refs": [item.to_dict() for item in deviation_refs],
        "canonical_position_ref": canonical_position_ref.to_dict(),
        "position_feature_packet_ref": (
            None if feature_ref is None else feature_ref.to_dict()
        ),
        "position_analysis_refs": [item.to_dict() for item in analysis_refs],
        "decision_comparison_ref": comparison_ref.to_dict(),
        "selection_signal_refs": [item.to_dict() for item in signal_refs],
        "measurement_condition": _measurement_condition(capture_session),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    return ReasoningDiscrepancyContext(
        reasoning_context_id=f"reasoning_context_{fingerprint[:20]}",
        context_fingerprint=fingerprint,
        participant_id=m5_context.participant_id,
        player_decision_context_ref=player_context_ref,
        position_id=position.position_id,
        game_id=position.game_id,
        diagnostic_candidate_ref=candidate_ref,
        diagnostic_batch_ref=batch_ref,
        capture_session_ref=capture_ref,
        assessment_stage_ids=stage_ids,
        player_response_refs=response_refs,
        evidence_freeze_refs=freeze_refs,
        prompt_presentation_refs=presentation_refs,
        exposure_refs=exposure_refs,
        protocol_deviation_refs=deviation_refs,
        canonical_position_ref=canonical_position_ref,
        position_feature_packet_ref=feature_ref,
        position_analysis_refs=analysis_refs,
        decision_comparison_ref=comparison_ref,
        selection_signal_refs=signal_refs,
        measurement_condition=_measurement_condition(capture_session),
        created_at=created_at,
    )


def _root_analysis(
    position: CanonicalPosition,
    records: tuple[AnalysisRecord, ...],
) -> PositionAnalysis | None:
    matches = [
        item
        for item in records
        if isinstance(item, PositionAnalysis)
        and item.position_id == position.position_id
    ]
    if len(matches) > 1:
        raise ReasoningDiscrepancyError(
            "multiple root PositionAnalysis records supplied"
        )
    return None if not matches else matches[0]


def _exact_engine_best(analysis: PositionAnalysis | None) -> str | None:
    if analysis is None or analysis.status != "complete" or not analysis.lines:
        return None
    best = analysis.lines[0]
    if best.evaluation.bound != "exact":
        return None
    return best.root_move_uci


def _candidate_line(analysis: PositionAnalysis | None, move_uci: str):
    if analysis is None or analysis.status != "complete":
        return None
    for line in analysis.lines:
        if line.root_move_uci == move_uci and line.evaluation.bound == "exact":
            return line
    return None


def _find_legal_move(board: Board, uci: str):
    return next((item for item in board.legal_moves() if item.uci() == uci), None)


def _participant_refs(
    context: ReasoningDiscrepancyContext,
    response: PlayerResponseEvidence,
    freeze: EvidenceFreeze,
    presentation: PromptPresentation,
) -> tuple[ReasoningEvidenceRef, ...]:
    wanted = {response.response_id, freeze.freeze_id, presentation.presentation_id}
    refs = (
        *context.player_response_refs,
        *context.evidence_freeze_refs,
        *context.prompt_presentation_refs,
    )
    selected = tuple(item for item in refs if item.ref_id in wanted)
    if len(selected) != 3:
        raise ReasoningDiscrepancyError(
            "M6 context is missing selected participant refs"
        )
    return selected


def _root_analysis_ref(
    context: ReasoningDiscrepancyContext,
    analysis: PositionAnalysis | None,
) -> ReasoningEvidenceRef | None:
    if analysis is None:
        return None
    return next(
        (
            item
            for item in context.position_analysis_refs
            if item.ref_id == analysis.result_fingerprint
        ),
        None,
    )


def _fact(
    *,
    context: ReasoningDiscrepancyContext,
    stage_id: str,
    kind: DiscrepancyFactKind,
    participant_refs: tuple[ReasoningEvidenceRef, ...],
    objective_refs: tuple[ReasoningEvidenceRef, ...],
    relation: DiscrepancyRelation,
    participant_value: Any,
    objective_value: Any,
    provenance: tuple[tuple[str, str], ...],
) -> DiscrepancyFact:
    normalized_provenance = tuple(sorted(provenance, key=lambda item: item[0]))
    payload = {
        "reasoning_context_id": context.reasoning_context_id,
        "stage_id": stage_id,
        "kind": kind,
        "participant_evidence_refs": [item.to_dict() for item in participant_refs],
        "objective_evidence_refs": [item.to_dict() for item in objective_refs],
        "relation": relation,
        "participant_value": participant_value,
        "objective_value": objective_value,
        "comparison_provenance": [list(item) for item in normalized_provenance],
    }
    fingerprint = _fingerprint(payload)
    return DiscrepancyFact(
        fact_id=f"discrepancy_fact_{fingerprint[:20]}",
        fingerprint=fingerprint,
        reasoning_context_id=context.reasoning_context_id,
        stage_id=stage_id,
        kind=kind,
        participant_evidence_refs=participant_refs,
        objective_evidence_refs=objective_refs,
        relation=relation,
        participant_value=participant_value,
        objective_value=objective_value,
        comparison_provenance=normalized_provenance,
    )


def _move_value(move) -> dict[str, Any] | None:
    return None if move is None else move.to_dict()


def _selected_move_fact(
    *,
    context: ReasoningDiscrepancyContext,
    response: PlayerResponseEvidence,
    freeze: EvidenceFreeze,
    presentation: PromptPresentation,
    position: CanonicalPosition,
    comparison: DecisionComparison,
    root_analysis: PositionAnalysis | None,
) -> DiscrepancyFact:
    participant_refs = _participant_refs(context, response, freeze, presentation)
    structured = response.structured_response
    selected = None if structured is None else structured.selected_move
    objective_refs: tuple[ReasoningEvidenceRef, ...] = (context.canonical_position_ref,)
    if selected is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="REPORTED_SELECTED_MOVE_RELATION",
            participant_refs=participant_refs,
            objective_refs=objective_refs,
            relation="not_observed",
            participant_value=None,
            objective_value=None,
            provenance=(("basis", "structured_selected_move_absent"),),
        )
    if selected.normalization_status != "normalized" or selected.normalized_uci is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="REPORTED_SELECTED_MOVE_RELATION",
            participant_refs=participant_refs,
            objective_refs=objective_refs,
            relation="ambiguous",
            participant_value=_move_value(selected),
            objective_value=None,
            provenance=(("basis", "participant_move_not_unambiguously_normalized"),),
        )

    board = Board.from_fen(position.fen)
    if _find_legal_move(board, selected.normalized_uci) is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="REPORTED_SELECTED_MOVE_RELATION",
            participant_refs=participant_refs,
            objective_refs=objective_refs,
            relation="conflict",
            participant_value=_move_value(selected),
            objective_value={"requirement": "legal_move_from_canonical_position"},
            provenance=(("basis", "deterministic_chess_legality"),),
        )

    best_move = _exact_engine_best(root_analysis)
    analysis_ref = _root_analysis_ref(context, root_analysis)
    if best_move is None or analysis_ref is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="REPORTED_SELECTED_MOVE_RELATION",
            participant_refs=participant_refs,
            objective_refs=objective_refs,
            relation="not_comparable",
            participant_value=_move_value(selected),
            objective_value=None,
            provenance=(("basis", "exact_engine_rank1_unavailable"),),
        )
    engine_refs = (context.decision_comparison_ref, analysis_ref)
    if selected.normalized_uci == best_move:
        relation: DiscrepancyRelation = "match"
        basis = "exact_engine_rank1_identity"
    elif (
        selected.normalized_uci == comparison.played_move_uci
        and comparison.preference == "worse_for_mover"
    ):
        relation = "conflict"
        basis = "qualified_m4_played_move_worse_than_rank1"
    elif (
        selected.normalized_uci == comparison.played_move_uci
        and comparison.preference == "approximately_equal_under_policy"
    ):
        relation = "match"
        basis = "qualified_m4_played_move_policy_equivalent"
    else:
        relation = "not_comparable"
        basis = "selected_move_not_evaluated_by_qualified_m4_comparison"
    return _fact(
        context=context,
        stage_id=response.stage_id,
        kind="REPORTED_SELECTED_MOVE_RELATION",
        participant_refs=participant_refs,
        objective_refs=engine_refs,
        relation=relation,
        participant_value=_move_value(selected),
        objective_value={
            "engine_rank1_uci": best_move,
            "canonical_played_move_uci": comparison.played_move_uci,
            "m4_preference": comparison.preference,
        },
        provenance=(("basis", basis), ("objective_authority", "engine_and_m4")),
    )


def _candidate_membership_fact(
    *,
    context: ReasoningDiscrepancyContext,
    response: PlayerResponseEvidence,
    freeze: EvidenceFreeze,
    presentation: PromptPresentation,
    root_analysis: PositionAnalysis | None,
) -> DiscrepancyFact:
    participant_refs = _participant_refs(context, response, freeze, presentation)
    structured = response.structured_response
    candidates = () if structured is None else structured.candidate_moves
    canonical_ref = context.canonical_position_ref
    if not candidates:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
            participant_refs=participant_refs,
            objective_refs=(canonical_ref,),
            relation="not_observed",
            participant_value=[],
            objective_value=None,
            provenance=(("basis", "explicit_candidate_values_absent"),),
        )
    best_move = _exact_engine_best(root_analysis)
    analysis_ref = _root_analysis_ref(context, root_analysis)
    if best_move is None or analysis_ref is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
            participant_refs=participant_refs,
            objective_refs=(canonical_ref,),
            relation="not_comparable",
            participant_value=[item.to_dict() for item in candidates],
            objective_value=None,
            provenance=(("basis", "exact_engine_rank1_unavailable"),),
        )
    normalized = {
        item.normalized_uci
        for item in candidates
        if item.normalization_status == "normalized" and item.normalized_uci is not None
    }
    if best_move in normalized:
        relation: DiscrepancyRelation = "match"
        basis = "engine_rank1_explicitly_reported"
    elif any(item.normalization_status != "normalized" for item in candidates):
        relation = "ambiguous"
        basis = "candidate_report_contains_unresolved_move"
    else:
        relation = "not_explicitly_reported"
        basis = "engine_rank1_absent_from_explicit_candidate_values"
    return _fact(
        context=context,
        stage_id=response.stage_id,
        kind="EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
        participant_refs=participant_refs,
        objective_refs=(analysis_ref,),
        relation=relation,
        participant_value=[item.to_dict() for item in candidates],
        objective_value={"engine_rank1_uci": best_move},
        provenance=(("basis", basis), ("objective_authority", "engine_evidence")),
    )


def _expected_reply_fact(
    *,
    context: ReasoningDiscrepancyContext,
    response: PlayerResponseEvidence,
    freeze: EvidenceFreeze,
    presentation: PromptPresentation,
    position: CanonicalPosition,
    root_analysis: PositionAnalysis | None,
) -> DiscrepancyFact:
    participant_refs = _participant_refs(context, response, freeze, presentation)
    structured = response.structured_response
    reply = None if structured is None else structured.expected_reply
    selected = None if structured is None else structured.selected_move
    if reply is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_REPLY_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_observed",
            participant_value=None,
            objective_value=None,
            provenance=(("basis", "explicit_expected_reply_absent"),),
        )
    if reply.normalization_status != "normalized" or reply.normalized_uci is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_REPLY_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="ambiguous",
            participant_value=_move_value(reply),
            objective_value=None,
            provenance=(("basis", "expected_reply_not_unambiguously_normalized"),),
        )
    if (
        selected is None
        or selected.normalization_status != "normalized"
        or selected.normalized_uci is None
    ):
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_REPLY_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_comparable",
            participant_value=_move_value(reply),
            objective_value=None,
            provenance=(("basis", "selected_move_required_to_locate_reply_position"),),
        )

    board = Board.from_fen(position.fen)
    selected_move = _find_legal_move(board, selected.normalized_uci)
    if selected_move is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_REPLY_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_comparable",
            participant_value=_move_value(reply),
            objective_value=None,
            provenance=(("basis", "selected_move_illegal_from_canonical_position"),),
        )
    board.push(selected_move)
    legal_replies = tuple(item.uci() for item in board.legal_moves())
    if reply.normalized_uci not in legal_replies:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_REPLY_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="conflict",
            participant_value=_move_value(reply),
            objective_value={
                "requirement": "legal_reply",
                "legal_reply_count": len(legal_replies),
            },
            provenance=(("basis", "deterministic_reply_legality"),),
        )

    line = _candidate_line(root_analysis, selected.normalized_uci)
    analysis_ref = _root_analysis_ref(context, root_analysis)
    if line is None or analysis_ref is None or len(line.pv_uci) < 2:
        relation: DiscrepancyRelation = "not_comparable"
        objective_value = None
        basis = "comparable_engine_reply_unavailable"
        objective_refs = (context.canonical_position_ref,)
    elif reply.normalized_uci == line.pv_uci[1]:
        relation = "match"
        objective_value = {"engine_pv_reply_uci": line.pv_uci[1]}
        basis = "matches_cited_engine_pv_reply"
        objective_refs = (analysis_ref,)
    else:
        relation = "not_comparable"
        objective_value = {
            "engine_pv_reply_uci": line.pv_uci[1],
            "participant_reply_is_legal": True,
        }
        basis = "legal_alternative_differs_from_single_nonforced_engine_pv"
        objective_refs = (analysis_ref, context.canonical_position_ref)
    return _fact(
        context=context,
        stage_id=response.stage_id,
        kind="EXPECTED_REPLY_RELATION",
        participant_refs=participant_refs,
        objective_refs=objective_refs,
        relation=relation,
        participant_value=_move_value(reply),
        objective_value=objective_value,
        provenance=(("basis", basis),),
    )


def _expected_continuation_fact(
    *,
    context: ReasoningDiscrepancyContext,
    response: PlayerResponseEvidence,
    freeze: EvidenceFreeze,
    presentation: PromptPresentation,
    position: CanonicalPosition,
    root_analysis: PositionAnalysis | None,
) -> DiscrepancyFact:
    participant_refs = _participant_refs(context, response, freeze, presentation)
    structured = response.structured_response
    continuation = () if structured is None else structured.expected_continuation
    selected = None if structured is None else structured.selected_move
    reply = None if structured is None else structured.expected_reply
    if not continuation:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_CONTINUATION_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_observed",
            participant_value=[],
            objective_value=None,
            provenance=(("basis", "explicit_expected_continuation_absent"),),
        )
    if any(
        item.normalization_status != "normalized" or item.normalized_uci is None
        for item in continuation
    ):
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_CONTINUATION_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="ambiguous",
            participant_value=[item.to_dict() for item in continuation],
            objective_value=None,
            provenance=(("basis", "continuation_contains_unresolved_move"),),
        )
    if (
        selected is None
        or selected.normalization_status != "normalized"
        or selected.normalized_uci is None
        or reply is None
        or reply.normalization_status != "normalized"
        or reply.normalized_uci is None
    ):
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_CONTINUATION_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_comparable",
            participant_value=[item.to_dict() for item in continuation],
            objective_value=None,
            provenance=((
                "basis",
                "selected_move_and_reply_required_for_continuation",
            ),),
        )

    board = Board.from_fen(position.fen)
    selected_move = _find_legal_move(board, selected.normalized_uci)
    if selected_move is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_CONTINUATION_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_comparable",
            participant_value=[item.to_dict() for item in continuation],
            objective_value=None,
            provenance=(("basis", "selected_move_illegal_from_canonical_position"),),
        )
    board.push(selected_move)
    reply_move = _find_legal_move(board, reply.normalized_uci)
    if reply_move is None:
        return _fact(
            context=context,
            stage_id=response.stage_id,
            kind="EXPECTED_CONTINUATION_RELATION",
            participant_refs=participant_refs,
            objective_refs=(context.canonical_position_ref,),
            relation="not_comparable",
            participant_value=[item.to_dict() for item in continuation],
            objective_value=None,
            provenance=((
                "basis",
                "expected_reply_illegal_so_continuation_has_no_valid_root",
            ),),
        )
    board.push(reply_move)
    for index, item in enumerate(continuation):
        assert item.normalized_uci is not None
        move = _find_legal_move(board, item.normalized_uci)
        if move is None:
            return _fact(
                context=context,
                stage_id=response.stage_id,
                kind="EXPECTED_CONTINUATION_RELATION",
                participant_refs=participant_refs,
                objective_refs=(context.canonical_position_ref,),
                relation="conflict",
                participant_value=[entry.to_dict() for entry in continuation],
                objective_value={
                    "requirement": "legal_continuation",
                    "invalid_index": index,
                },
                provenance=(("basis", "deterministic_continuation_legality"),),
            )
        board.push(move)

    line = _candidate_line(root_analysis, selected.normalized_uci)
    analysis_ref = _root_analysis_ref(context, root_analysis)
    normalized_continuation = tuple(item.normalized_uci for item in continuation)
    if (
        line is None
        or analysis_ref is None
        or len(line.pv_uci) < 2 + len(normalized_continuation)
    ):
        relation: DiscrepancyRelation = "not_comparable"
        objective_value = None
        basis = "comparable_engine_continuation_unavailable"
        objective_refs = (context.canonical_position_ref,)
    elif reply.normalized_uci != line.pv_uci[1]:
        relation = "not_comparable"
        objective_value = {
            "engine_pv_reply_uci": line.pv_uci[1],
            "participant_reply_is_legal": True,
        }
        basis = "participant_reply_differs_from_single_nonforced_engine_pv"
        objective_refs = (analysis_ref, context.canonical_position_ref)
    elif normalized_continuation == line.pv_uci[2 : 2 + len(normalized_continuation)]:
        relation = "match"
        objective_value = {
            "engine_pv_continuation_uci": list(
                line.pv_uci[2 : 2 + len(normalized_continuation)]
            )
        }
        basis = "matches_cited_engine_pv_continuation"
        objective_refs = (analysis_ref,)
    else:
        relation = "not_comparable"
        objective_value = {
            "engine_pv_continuation_uci": list(
                line.pv_uci[2 : 2 + len(normalized_continuation)]
            ),
            "participant_continuation_is_legal": True,
        }
        basis = "legal_continuation_differs_from_single_nonforced_engine_pv"
        objective_refs = (analysis_ref, context.canonical_position_ref)
    return _fact(
        context=context,
        stage_id=response.stage_id,
        kind="EXPECTED_CONTINUATION_RELATION",
        participant_refs=participant_refs,
        objective_refs=objective_refs,
        relation=relation,
        participant_value=[item.to_dict() for item in continuation],
        objective_value=objective_value,
        provenance=(("basis", basis),),
    )


def derive_discrepancy_facts(
    *,
    context: ReasoningDiscrepancyContext,
    capture_session: EvidenceCaptureSession,
    position: CanonicalPosition,
    decision_comparison: DecisionComparison,
    position_analyses: tuple[AnalysisRecord, ...] = (),
) -> tuple[DiscrepancyFact, ...]:
    """Derive only deterministic, stage-specific M6B relation facts."""
    if context.capture_session_ref.ref_id != capture_session.capture_session_id:
        raise ReasoningDiscrepancyError("capture session does not match M6 context")
    if (
        context.position_id != position.position_id
        or context.game_id != position.game_id
    ):
        raise ReasoningDiscrepancyError("canonical position does not match M6 context")
    if context.decision_comparison_ref.ref_id != decision_comparison.comparison_id:
        raise ReasoningDiscrepancyError("decision comparison does not match M6 context")
    _validate_objective_inputs(
        position=position,
        decision_comparison=decision_comparison,
        position_features=None,
        position_analyses=position_analyses,
        selection_signals=(),
    )
    stage_ids, presentations, responses, freezes = _selected_stage_records(
        capture_session,
        context.assessment_stage_ids,
    )
    if stage_ids != context.assessment_stage_ids:
        raise ReasoningDiscrepancyError(
            "assessment stage order does not match M6 context"
        )
    root_analysis = _root_analysis(position, position_analyses)

    facts: list[DiscrepancyFact] = []
    for presentation, response, freeze in zip(
        presentations,
        responses,
        freezes,
        strict=True,
    ):
        per_stage = {
            "REPORTED_SELECTED_MOVE_RELATION": _selected_move_fact(
                context=context,
                response=response,
                freeze=freeze,
                presentation=presentation,
                position=position,
                comparison=decision_comparison,
                root_analysis=root_analysis,
            ),
            "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION": _candidate_membership_fact(
                context=context,
                response=response,
                freeze=freeze,
                presentation=presentation,
                root_analysis=root_analysis,
            ),
            "EXPECTED_REPLY_RELATION": _expected_reply_fact(
                context=context,
                response=response,
                freeze=freeze,
                presentation=presentation,
                position=position,
                root_analysis=root_analysis,
            ),
            "EXPECTED_CONTINUATION_RELATION": _expected_continuation_fact(
                context=context,
                response=response,
                freeze=freeze,
                presentation=presentation,
                position=position,
                root_analysis=root_analysis,
            ),
        }
        facts.extend(per_stage[kind] for kind in _FACT_ORDER)
    return tuple(facts)
