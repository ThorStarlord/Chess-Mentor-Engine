"""Durable M8 sessions reconstructed through the existing domain state machine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.evidence import PromptDefinition, define_prompt
from chess_mentor_engine.tutoring import (
    TutorSession,
    attach_tutor_hypothesis_context,
    capture_tutor_response,
    complete_tutor_session,
    freeze_tutor_response,
    present_tutor_capture_stage,
    present_tutor_position,
    record_tutor_explanation,
    record_tutor_reasoning_comparison,
    reveal_tutor_objective_evidence,
    start_tutor_session,
)

from .codec import decode_record, encode_record
from .store import (
    ArtifactRef,
    ArtifactWrite,
    IntegrityError,
    LocalArtifactStore,
    MissingDependencyError,
    StorageError,
    UnsupportedSchemaError,
    canonical,
    prepare_artifact,
)

SESSION_KIND = "m8.tutor-session.v1"
PROMPT_KIND = "m5.prompt-definition.v1"


@dataclass(frozen=True, slots=True)
class RecoveredTutorSession:
    session: TutorSession
    prompts: tuple[PromptDefinition, ...]
    ref: ArtifactRef


def _prompt_map(
    session: TutorSession, prompts: tuple[PromptDefinition, ...],
) -> dict[str, PromptDefinition]:
    by_id = {prompt.prompt_definition_id: prompt for prompt in prompts}
    if len(by_id) != len(prompts):
        raise IntegrityError("duplicate prompt definitions")
    required = {
        stage.prompt_definition_id for stage in session.capture_session.protocol.stages
    }
    if set(by_id) != required:
        raise MissingDependencyError("exact planned prompt definitions are required")
    for prompt in prompts:
        rebuilt = define_prompt(
            name=prompt.name, version=prompt.version, stage_kind=prompt.stage_kind,
            interaction_class=prompt.interaction_class, content=prompt.content,
            response_schema=prompt.response_schema, provenance=prompt.provenance,
        )
        if rebuilt != prompt:
            raise IntegrityError("prompt definition identity or fingerprint mismatch")
    return by_id


def _one(items: tuple[Any, ...], field: str, identity: str) -> Any:
    matches = [item for item in items if getattr(item, field) == identity]
    if len(matches) != 1:
        raise IntegrityError("event must resolve to exactly one stored artifact")
    return matches[0]


def replay_tutor_session(
    session: TutorSession, *, prompts: tuple[PromptDefinition, ...],
) -> TutorSession:
    """Re-execute all M8 transitions and compare every event and the final snapshot.

    This revalidates M8 sequencing/provenance, not the truth of authored text or
    independent qualification of every upstream M1-M7 source reference.
    """
    if session.workflow_version != "1":
        raise UnsupportedSchemaError("unsupported tutor workflow version")
    try:
        prompt_map = _prompt_map(session, prompts)
        capture = session.capture_session
        current = start_tutor_session(
            context=capture.context, capture_protocol=capture.protocol,
            created_at=session.created_at,
        )
        if current.events[0] != session.events[0]:
            raise IntegrityError("session start event does not replay")
        for event in session.events[1:]:
            kind = event.kind
            if kind == "POSITION_PRESENTED":
                presentation = session.position_presentation
                if presentation is None:
                    raise IntegrityError("missing position presentation")
                current, _ = present_tutor_position(
                    current, position_context=presentation.position_context,
                    shown_at=presentation.shown_at,
                )
            elif kind == "CAPTURE_STAGE_PRESENTED":
                presentation = _one(
                    capture.presentations, "presentation_id", event.artifact_id
                )
                current = present_tutor_capture_stage(
                    current, stage_id=presentation.stage_id,
                    prompt=prompt_map[presentation.prompt_definition_id],
                    shown_at=presentation.shown_at,
                )
            elif kind == "RESPONSE_CAPTURED":
                response = _one(capture.responses, "response_id", event.artifact_id)
                current = capture_tutor_response(
                    current, stage_id=response.stage_id,
                    raw_response=response.raw_response,
                    structured_response=response.structured_response,
                    submitted_at=response.submitted_at,
                )
            elif kind == "RESPONSE_FROZEN":
                freeze = _one(capture.freezes, "freeze_id", event.artifact_id)
                current = freeze_tutor_response(
                    current, stage_id=freeze.stage_id, frozen_at=freeze.frozen_at
                )
            elif kind == "OBJECTIVE_EVIDENCE_REVEALED":
                reveal = capture.objective_reveal
                if reveal is None:
                    raise IntegrityError("missing objective reveal")
                current = reveal_tutor_objective_evidence(
                    current, revealed_at=reveal.revealed_at,
                    rendered_content=reveal.rendered_content,
                    position_analysis_refs=reveal.position_analysis_refs,
                    decision_comparison_ref=reveal.decision_comparison_ref,
                    selection_signal_refs=reveal.selection_signal_refs,
                )
            elif kind == "REASONING_COMPARISON_RECORDED":
                comparison = session.comparison
                if comparison is None:
                    raise IntegrityError("missing reasoning comparison")
                current, _ = record_tutor_reasoning_comparison(
                    current, reasoning_context=comparison.reasoning_context,
                    assessment=comparison.assessment, assertions=comparison.assertions,
                    recorded_at=comparison.recorded_at,
                )
            elif kind == "HYPOTHESIS_CONTEXT_ATTACHED":
                context = session.hypothesis_context
                if context is None:
                    raise IntegrityError("missing hypothesis context")
                current, _ = attach_tutor_hypothesis_context(
                    current, ledger_snapshot=context.ledger_snapshot,
                    active_revisions=context.active_revisions,
                    attached_at=context.attached_at,
                )
            elif kind == "EXPLANATION_RECORDED":
                explanation = session.explanation
                if explanation is None:
                    raise IntegrityError("missing explanation")
                current, _ = record_tutor_explanation(
                    current, rendered_content=explanation.rendered_content,
                    provenance=explanation.provenance,
                    created_at=explanation.created_at,
                )
            elif kind == "SESSION_COMPLETED":
                if session.completed_at is None:
                    raise IntegrityError("missing completion time")
                current = complete_tutor_session(
                    current, completed_at=session.completed_at
                )
            else:
                raise IntegrityError("unsupported tutor event")
            if current.events[-1] != event:
                raise IntegrityError(
                    "event identity, order, or fingerprint does not replay"
                )
        if canonical(current.to_dict()) != canonical(session.to_dict()):
            raise IntegrityError("session snapshot does not match verified replay")
        return current
    except StorageError:
        raise
    except (ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        raise IntegrityError(f"tutor replay rejected: {exc}") from exc


def save_tutor_session(
    store: LocalArtifactStore, session: TutorSession, *,
    prompts: tuple[PromptDefinition, ...],
    dependencies: tuple[ArtifactRef, ...] = (),
) -> ArtifactRef:
    """Atomically store exact prompt dependencies and one verified M8 snapshot.

    Optional dependencies retain separately stored upstream evidence. The snapshot
    key includes its native fingerprint, so earlier states are never overwritten.
    """
    payload = encode_record(session)
    replay_tutor_session(session, prompts=prompts)
    participant_id = session.capture_session.context.participant_id
    prompt_writes = tuple(
        ArtifactWrite(
            PROMPT_KIND, prompt.prompt_definition_id, participant_id,
            {"codec_version": 1, "prompt": encode_record(prompt)},
        )
        for prompt in sorted(prompts, key=lambda item: item.prompt_definition_id)
    )
    prompt_refs = tuple(prepare_artifact(write)[0] for write in prompt_writes)
    session_write = ArtifactWrite(
        SESSION_KIND, f"{session.tutor_session_id}:{session.snapshot_fingerprint}",
        participant_id, {"codec_version": 1, "session": payload},
        prompt_refs + dependencies,
    )
    return store.put_many(prompt_writes + (session_write,))[-1]


def _payload(data: dict[str, Any], key: str) -> dict[str, Any]:
    if set(data) != {"codec_version", key}:
        raise IntegrityError("invalid typed artifact envelope")
    if type(data["codec_version"]) is not int or data["codec_version"] != 1:
        raise UnsupportedSchemaError("unsupported record codec version")
    return data[key]


def load_tutor_session(
    store: LocalArtifactStore, ref: ArtifactRef, *, participant_id: str,
) -> RecoveredTutorSession:
    """Resolve dependencies, decode safely, replay, and return a resumable session."""
    if ref.kind != SESSION_KIND:
        raise IntegrityError("not a tutor-session artifact")
    stored = store.get(ref, participant_id=participant_id)
    session = decode_record(_payload(stored.payload, "session"), TutorSession)
    if session.capture_session.context.participant_id != participant_id:
        raise IntegrityError("session participant differs from storage scope")
    if ref.artifact_id != f"{session.tutor_session_id}:{session.snapshot_fingerprint}":
        raise IntegrityError("native session identity differs from storage identity")
    prompts = []
    for dependency in stored.dependencies:
        if dependency.kind != PROMPT_KIND:
            continue
        prompt_data = store.get(dependency, participant_id=participant_id).payload
        prompt = decode_record(
            _payload(prompt_data, "prompt"),
            PromptDefinition,
        )
        if prompt.prompt_definition_id != dependency.artifact_id:
            raise IntegrityError("prompt identity differs from dependency identity")
        prompts.append(prompt)
    ordered = tuple(sorted(prompts, key=lambda item: item.prompt_definition_id))
    current = replay_tutor_session(session, prompts=ordered)
    return RecoveredTutorSession(current, ordered, ref)
