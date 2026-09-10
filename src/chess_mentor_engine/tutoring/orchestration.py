"""M21 participant-authorized bridge from M18 candidates into M5/M8."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import (
    CanonicalGame,
    CanonicalPosition,
    build_position_context,
    canonical_json,
)
from chess_mentor_engine.evidence import (
    CaptureProtocol,
    PlayerDecisionContext,
    PlayerEvidenceError,
    record_player_decision_context,
)
from chess_mentor_engine.selection import DiagnosticCandidate, DiagnosticCandidateBatch

from .model import TutorSession
from .session import TutorSessionError, start_tutor_session

CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION = (
    "m21.candidate-tutor-authorization.v1"
)
CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION = "m21.candidate-tutor-launch.v1"

CandidateSelectionDecision: TypeAlias = Literal["selected", "declined"]
CaptureConsentDecision: TypeAlias = Literal["granted", "declined"]


class CandidateTutorOrchestrationError(ValueError):
    """M21 cannot preserve candidate selection or M5/M8 authority boundaries."""


@dataclass(frozen=True, slots=True)
class CandidateTutorAuthorization:
    """Participant-authored candidate choice and separate capture consent."""

    authorization_id: str
    fingerprint: str
    schema_version: str
    participant_id: str
    candidate_id: str
    candidate_fingerprint: str
    batch_id: str
    batch_fingerprint: str
    selection_decision: CandidateSelectionDecision
    capture_consent: CaptureConsentDecision
    actor_kind: Literal["participant"]
    recorded_at: str
    claim_scope: str

    def __post_init__(self) -> None:
        for name, value in (
            ("authorization_id", self.authorization_id),
            ("fingerprint", self.fingerprint),
            ("schema_version", self.schema_version),
            ("participant_id", self.participant_id),
            ("candidate_id", self.candidate_id),
            ("candidate_fingerprint", self.candidate_fingerprint),
            ("batch_id", self.batch_id),
            ("batch_fingerprint", self.batch_fingerprint),
            ("recorded_at", self.recorded_at),
            ("claim_scope", self.claim_scope),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")
        if self.schema_version != CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("candidate tutor authorization schema mismatch")
        if self.selection_decision not in {"selected", "declined"}:
            raise ValueError("unsupported candidate selection decision")
        if self.capture_consent not in {"granted", "declined"}:
            raise ValueError("unsupported capture consent decision")
        if self.actor_kind != "participant":
            raise ValueError(
                "candidate tutor authorization must be participant-authored"
            )
        if self.selection_decision == "declined" and self.capture_consent == "granted":
            raise ValueError(
                "capture consent cannot be granted for a declined candidate"
            )
        if self.claim_scope != "participant_candidate_and_capture_authorization":
            raise ValueError("candidate tutor authorization claim scope mismatch")

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "participant_id": self.participant_id,
            "candidate_id": self.candidate_id,
            "candidate_fingerprint": self.candidate_fingerprint,
            "batch_id": self.batch_id,
            "batch_fingerprint": self.batch_fingerprint,
            "selection_decision": self.selection_decision,
            "capture_consent": self.capture_consent,
            "actor_kind": self.actor_kind,
            "recorded_at": self.recorded_at,
            "claim_scope": self.claim_scope,
        }
        if include_identity:
            payload["authorization_id"] = self.authorization_id
            payload["fingerprint"] = self.fingerprint
        return payload


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise CandidateTutorOrchestrationError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CandidateTutorOrchestrationError(
            f"invalid timestamp: {value!r}"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CandidateTutorOrchestrationError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _candidate_identity_payload(candidate: DiagnosticCandidate) -> dict[str, Any]:
    return {
        "position_id": candidate.position_id,
        "game_id": candidate.game_id,
        "comparison_id": candidate.comparison_id,
        "selection_policy": candidate.selection_policy.to_dict(),
        "signal_ids": [signal.signal_id for signal in candidate.signals],
        "eligibility_signal_ids": list(candidate.eligibility_signal_ids),
        "provenance": candidate.provenance.to_dict(),
    }


def _validate_candidate_identity(candidate: DiagnosticCandidate) -> None:
    for signal in candidate.signals:
        signal_payload = {
            "kind": signal.kind,
            "position_id": signal.position_id,
            "game_id": signal.game_id,
            "comparison_id": signal.comparison_id,
            "schema_version": signal.schema_version,
            "raw_value": signal.raw_value,
            "evidence": [item.to_dict() for item in signal.evidence],
            "detail": signal.detail,
        }
        expected_signal_id = f"signal_{_fingerprint(signal_payload)[:20]}"
        if signal.signal_id != expected_signal_id:
            raise CandidateTutorOrchestrationError(
                "diagnostic candidate signal identity mismatch"
            )
    expected = f"candidate_{_fingerprint(_candidate_identity_payload(candidate))[:20]}"
    if candidate.candidate_id != expected:
        raise CandidateTutorOrchestrationError(
            "diagnostic candidate identity mismatch"
        )


def _batch_identity_payload(batch: DiagnosticCandidateBatch) -> dict[str, Any]:
    return {
        "selection_policy": batch.selection_policy.to_dict(),
        "policy_fingerprint": batch.policy_fingerprint,
        "requested_size": batch.requested_size,
        "candidate_ids": [item.candidate_id for item in batch.candidates],
        "control_candidate_ids": list(batch.control_candidate_ids),
        "source_candidate_ids": list(batch.source_candidate_ids),
        "source_pool_fingerprint": batch.source_pool_fingerprint,
        "quota_outcomes": [item.to_dict() for item in batch.quota_outcomes],
        "exclusions": [item.to_dict() for item in batch.exclusions],
        "shortfall": batch.shortfall,
        "control_shortfall": batch.control_shortfall,
    }


def _validate_batch_identity(batch: DiagnosticCandidateBatch) -> None:
    expected = f"batch_{_fingerprint(_batch_identity_payload(batch))[:20]}"
    if batch.batch_id != expected:
        raise CandidateTutorOrchestrationError("diagnostic batch identity mismatch")


def _validate_candidate_in_batch(
    *,
    candidate: DiagnosticCandidate,
    batch: DiagnosticCandidateBatch,
) -> None:
    _validate_candidate_identity(candidate)
    _validate_batch_identity(batch)
    if candidate.selection_policy != batch.selection_policy:
        raise CandidateTutorOrchestrationError("candidate/batch policy mismatch")
    matches = tuple(
        item for item in batch.candidates if item.candidate_id == candidate.candidate_id
    )
    if len(matches) != 1:
        raise CandidateTutorOrchestrationError(
            "diagnostic candidate is not exactly selected in batch"
        )
    if matches[0] != candidate:
        raise CandidateTutorOrchestrationError(
            "diagnostic candidate content drifted from selected batch member"
        )
    if candidate.candidate_id not in batch.source_candidate_ids:
        raise CandidateTutorOrchestrationError(
            "selected candidate is absent from batch source candidate set"
        )


def record_candidate_tutor_authorization(
    *,
    participant_id: str,
    candidate: DiagnosticCandidate,
    batch: DiagnosticCandidateBatch,
    selection_decision: CandidateSelectionDecision,
    capture_consent: CaptureConsentDecision,
    recorded_at: str,
) -> CandidateTutorAuthorization:
    """Record explicit participant choice without starting capture or tutoring."""
    _parse_timestamp(recorded_at)
    if not participant_id:
        raise CandidateTutorOrchestrationError("participant_id must not be empty")
    if selection_decision not in {"selected", "declined"}:
        raise CandidateTutorOrchestrationError(
            "unsupported candidate selection decision"
        )
    if capture_consent not in {"granted", "declined"}:
        raise CandidateTutorOrchestrationError("unsupported capture consent decision")
    if selection_decision == "declined" and capture_consent == "granted":
        raise CandidateTutorOrchestrationError(
            "capture consent cannot be granted for a declined candidate"
        )
    _validate_candidate_in_batch(candidate=candidate, batch=batch)

    payload = {
        "schema_version": CANDIDATE_TUTOR_AUTHORIZATION_SCHEMA_VERSION,
        "participant_id": participant_id,
        "candidate_id": candidate.candidate_id,
        "candidate_fingerprint": _fingerprint(candidate.to_dict()),
        "batch_id": batch.batch_id,
        "batch_fingerprint": _fingerprint(batch.to_dict()),
        "selection_decision": selection_decision,
        "capture_consent": capture_consent,
        "actor_kind": "participant",
        "recorded_at": recorded_at,
        "claim_scope": "participant_candidate_and_capture_authorization",
    }
    fingerprint = _fingerprint(payload)
    return CandidateTutorAuthorization(
        authorization_id=f"candidate_tutor_auth_{fingerprint[:20]}",
        fingerprint=fingerprint,
        **payload,
    )


def _validate_authorization_identity(
    authorization: CandidateTutorAuthorization,
) -> None:
    if not isinstance(authorization, CandidateTutorAuthorization):
        raise CandidateTutorOrchestrationError(
            "candidate tutor authorization record type mismatch"
        )
    fingerprint = _fingerprint(authorization.to_dict(include_identity=False))
    if authorization.fingerprint != fingerprint:
        raise CandidateTutorOrchestrationError(
            "candidate tutor authorization fingerprint mismatch"
        )
    expected_id = f"candidate_tutor_auth_{fingerprint[:20]}"
    if authorization.authorization_id != expected_id:
        raise CandidateTutorOrchestrationError(
            "candidate tutor authorization identity mismatch"
        )


def _validate_authorization_against_sources(
    *,
    authorization: CandidateTutorAuthorization,
    candidate: DiagnosticCandidate,
    batch: DiagnosticCandidateBatch,
) -> None:
    _validate_authorization_identity(authorization)
    _validate_candidate_in_batch(candidate=candidate, batch=batch)
    if authorization.candidate_id != candidate.candidate_id:
        raise CandidateTutorOrchestrationError(
            "authorization candidate identity mismatch"
        )
    if authorization.candidate_fingerprint != _fingerprint(candidate.to_dict()):
        raise CandidateTutorOrchestrationError(
            "authorization candidate fingerprint mismatch"
        )
    if authorization.batch_id != batch.batch_id:
        raise CandidateTutorOrchestrationError("authorization batch identity mismatch")
    if authorization.batch_fingerprint != _fingerprint(batch.to_dict()):
        raise CandidateTutorOrchestrationError(
            "authorization batch fingerprint mismatch"
        )


def start_candidate_tutor_session(
    *,
    authorization: CandidateTutorAuthorization,
    candidate: DiagnosticCandidate,
    batch: DiagnosticCandidateBatch,
    game: CanonicalGame,
    position: CanonicalPosition,
    capture_protocol: CaptureProtocol,
    created_at: str,
) -> tuple[PlayerDecisionContext, TutorSession, dict[str, Any]]:
    """Create exact M5 context + initial M8 session after explicit authorization."""
    created_time = _parse_timestamp(created_at)
    _validate_authorization_against_sources(
        authorization=authorization,
        candidate=candidate,
        batch=batch,
    )
    if authorization.selection_decision != "selected":
        raise CandidateTutorOrchestrationError(
            "tutor session requires explicit candidate selection"
        )
    if authorization.capture_consent != "granted":
        raise CandidateTutorOrchestrationError(
            "tutor session requires explicit capture consent"
        )
    if created_time < _parse_timestamp(authorization.recorded_at):
        raise CandidateTutorOrchestrationError(
            "tutor session cannot predate participant authorization"
        )

    if candidate.game_id != game.game_id:
        raise CandidateTutorOrchestrationError("candidate/game identity mismatch")
    if candidate.position_id != position.position_id:
        raise CandidateTutorOrchestrationError("candidate/position identity mismatch")
    if position.game_id != game.game_id:
        raise CandidateTutorOrchestrationError("position does not belong to game")
    if position.ply_index < 0 or position.ply_index >= len(game.positions):
        raise CandidateTutorOrchestrationError("position ply is outside canonical game")
    if game.positions[position.ply_index] != position:
        raise CandidateTutorOrchestrationError(
            "position does not exactly match canonical game position"
        )
    provenance = candidate.provenance
    if provenance.source_sha256 != game.provenance.source_sha256:
        raise CandidateTutorOrchestrationError("candidate source provenance mismatch")
    if provenance.game_semantic_fingerprint != game.semantic_fingerprint:
        raise CandidateTutorOrchestrationError(
            "candidate game semantic fingerprint mismatch"
        )
    if provenance.root_ply_index != position.ply_index:
        raise CandidateTutorOrchestrationError("candidate root ply mismatch")
    if provenance.played_move_index != position.ply_index:
        raise CandidateTutorOrchestrationError("candidate played move index mismatch")
    child_index = position.ply_index + 1
    if child_index >= len(game.positions):
        raise CandidateTutorOrchestrationError("candidate canonical child is missing")
    if provenance.child_position_id != game.positions[child_index].position_id:
        raise CandidateTutorOrchestrationError("candidate child position mismatch")

    position_context = build_position_context(game, position)
    decision_session_id = f"m21_{authorization.authorization_id}"
    try:
        context = record_player_decision_context(
            participant_id=authorization.participant_id,
            session_id=decision_session_id,
            position=position,
            position_context=position_context,
            candidate=candidate,
            batch=batch,
            created_at=created_at,
        )
        session = start_tutor_session(
            context=context,
            capture_protocol=capture_protocol,
            created_at=created_at,
        )
    except (PlayerEvidenceError, TutorSessionError, ValueError) as exc:
        raise CandidateTutorOrchestrationError(
            f"M5/M8 candidate-to-tutor bridge rejected input: {exc}"
        ) from exc

    if (
        session.state != "selected"
        or session.comparison is not None
        or session.hypothesis_context is not None
        or session.explanation is not None
    ):
        raise CandidateTutorOrchestrationError(
            "M21 may only create an initial M8 selected session"
        )

    context_fingerprint = _fingerprint(context.to_dict())
    payload: dict[str, Any] = {
        "schema_version": CANDIDATE_TUTOR_LAUNCH_SCHEMA_VERSION,
        "authorization_ref": {
            "authorization_id": authorization.authorization_id,
            "fingerprint": authorization.fingerprint,
        },
        "candidate_ref": {
            "candidate_id": candidate.candidate_id,
            "fingerprint": _fingerprint(candidate.to_dict()),
        },
        "batch_ref": {
            "batch_id": batch.batch_id,
            "fingerprint": _fingerprint(batch.to_dict()),
        },
        "player_decision_context_ref": {
            "context_id": context.context_id,
            "fingerprint": context_fingerprint,
        },
        "tutor_session_ref": {
            "tutor_session_id": session.tutor_session_id,
            "snapshot_fingerprint": session.snapshot_fingerprint,
            "state": session.state,
        },
        "created_at": created_at,
        "claim_scope": "participant_authorized_candidate_to_tutor_start",
        "authority_boundary": {
            "created_layers": [
                "m5_player_decision_context",
                "m8_tutor_session_selected",
            ],
            "not_created": [
                "m6_reasoning_discrepancy",
                "m7_learner_hypothesis",
                "m9_training_selection",
                "m10_outcome_claim",
                "m11_longitudinal_mutation",
                "mentor_explanation",
            ],
        },
    }
    fingerprint = _fingerprint(payload)
    launch = {
        **payload,
        "launch_id": f"candidate_tutor_launch_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }
    return context, session, launch
