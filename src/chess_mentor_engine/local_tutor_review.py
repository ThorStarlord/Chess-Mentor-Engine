"""Guided local baseline capture over existing M8 authority.

This module makes the pre-reveal baseline easier to exercise. It deliberately stops
once M8 baseline evidence is frozen; it does not execute an M46 proposal.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from chess_mentor_engine.chess import PositionContextPacket
from chess_mentor_engine.observation import (
    build_interaction_observation,
    save_interaction_observation,
)
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.storage.tutor import PROMPT_KIND
from chess_mentor_engine.tutoring import (
    capture_tutor_response,
    freeze_tutor_response,
    present_tutor_capture_stage,
    present_tutor_position,
)


class LocalTutorReviewError(ValueError):
    """The guided baseline cannot preserve the exact M8 contract."""


@dataclass(frozen=True, slots=True)
class GuidedBaselineResult:
    initial_session_ref: ArtifactRef
    final_session_ref: ArtifactRef
    observation_refs: tuple[ArtifactRef, ...]
    baseline_frozen: bool
    abandoned: bool
    claim_scope: Literal["descriptive_local_product_use_only"] = (
        "descriptive_local_product_use_only"
    )
    learning_effect: Literal["not_established"] = "not_established"
    tutor_efficacy: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"


def _retained_dependencies(
    store: LocalArtifactStore,
    ref: ArtifactRef,
    *,
    participant_id: str,
) -> tuple[ArtifactRef, ...]:
    stored = store.get(ref, participant_id=participant_id)
    return tuple(
        dependency
        for dependency in stored.dependencies
        if dependency.kind != PROMPT_KIND
    )


def _persist_transition(
    *,
    store: LocalArtifactStore,
    previous_ref: ArtifactRef,
    participant_id: str,
    session,
    prompts,
) -> ArtifactRef:
    dependencies = _retained_dependencies(
        store,
        previous_ref,
        participant_id=participant_id,
    )
    return save_tutor_session(
        store,
        session,
        prompts=prompts,
        dependencies=dependencies,
    )


def _observe(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    session_ref: ArtifactRef,
    event_type,
    occurred_at: str,
    workflow_stage: str,
    metadata: tuple[tuple[str, str], ...] = (),
) -> ArtifactRef:
    observation = build_interaction_observation(
        participant_id=participant_id,
        tutor_session_ref=session_ref,
        event_type=event_type,
        occurred_at=occurred_at,
        workflow_stage=workflow_stage,
        metadata=metadata,
    )
    return save_interaction_observation(store, observation)


def run_guided_baseline_capture(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    initial_session_ref: ArtifactRef,
    position_context: PositionContextPacket,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    now_fn: Callable[[], str],
) -> GuidedBaselineResult:
    """Guide one exact selected M8 session through baseline freeze only."""
    recovered = load_tutor_session(
        store,
        initial_session_ref,
        participant_id=participant_id,
    )
    session = recovered.session
    prompts = recovered.prompts
    if session.state != "selected":
        raise LocalTutorReviewError("guided baseline requires a selected M8 checkpoint")

    current_ref = initial_session_ref
    observation_refs: list[ArtifactRef] = []
    shown_at = now_fn()
    observation_refs.append(
        _observe(
            store=store,
            participant_id=participant_id,
            session_ref=current_ref,
            event_type="review_started",
            occurred_at=shown_at,
            workflow_stage=session.state,
        )
    )

    session, presentation = present_tutor_position(
        session,
        position_context=position_context,
        shown_at=shown_at,
    )
    current_ref = _persist_transition(
        store=store,
        previous_ref=current_ref,
        participant_id=participant_id,
        session=session,
        prompts=prompts,
    )
    output_fn(presentation.rendered_content)
    observation_refs.append(
        _observe(
            store=store,
            participant_id=participant_id,
            session_ref=current_ref,
            event_type="position_presented",
            occurred_at=shown_at,
            workflow_stage=session.state,
        )
    )

    prompts_by_id = {item.prompt_definition_id: item for item in prompts}
    for stage in session.capture_session.protocol.pre_reveal_stages:
        prompt = prompts_by_id.get(stage.prompt_definition_id)
        if prompt is None:
            raise LocalTutorReviewError("planned M8 prompt dependency is missing")
        prompt_at = now_fn()
        session = present_tutor_capture_stage(
            session,
            stage_id=stage.stage_id,
            prompt=prompt,
            shown_at=prompt_at,
        )
        current_ref = _persist_transition(
            store=store,
            previous_ref=current_ref,
            participant_id=participant_id,
            session=session,
            prompts=prompts,
        )
        output_fn("\n".join(prompt.content))
        observation_refs.append(
            _observe(
                store=store,
                participant_id=participant_id,
                session_ref=current_ref,
                event_type="prompt_presented",
                occurred_at=prompt_at,
                workflow_stage=session.state,
                metadata=(("stage_id", stage.stage_id),),
            )
        )

        try:
            raw_response = input_fn("> ")
        except (EOFError, KeyboardInterrupt):
            abandoned_at = now_fn()
            observation_refs.append(
                _observe(
                    store=store,
                    participant_id=participant_id,
                    session_ref=current_ref,
                    event_type="session_abandoned",
                    occurred_at=abandoned_at,
                    workflow_stage=session.state,
                    metadata=(("stage_id", stage.stage_id),),
                )
            )
            return GuidedBaselineResult(
                initial_session_ref=initial_session_ref,
                final_session_ref=current_ref,
                observation_refs=tuple(observation_refs),
                baseline_frozen=False,
                abandoned=True,
            )

        submitted_at = now_fn()
        session = capture_tutor_response(
            session,
            stage_id=stage.stage_id,
            raw_response=raw_response,
            submitted_at=submitted_at,
        )
        current_ref = _persist_transition(
            store=store,
            previous_ref=current_ref,
            participant_id=participant_id,
            session=session,
            prompts=prompts,
        )
        observation_refs.append(
            _observe(
                store=store,
                participant_id=participant_id,
                session_ref=current_ref,
                event_type="response_submitted",
                occurred_at=submitted_at,
                workflow_stage=session.state,
                metadata=(("stage_id", stage.stage_id),),
            )
        )

        frozen_at = now_fn()
        session = freeze_tutor_response(
            session,
            stage_id=stage.stage_id,
            frozen_at=frozen_at,
        )
        current_ref = _persist_transition(
            store=store,
            previous_ref=current_ref,
            participant_id=participant_id,
            session=session,
            prompts=prompts,
        )
        observation_refs.append(
            _observe(
                store=store,
                participant_id=participant_id,
                session_ref=current_ref,
                event_type="response_frozen",
                occurred_at=frozen_at,
                workflow_stage=session.state,
                metadata=(("stage_id", stage.stage_id),),
            )
        )

    if session.state != "frozen":
        raise LocalTutorReviewError(
            "guided baseline did not reach the M8 freeze boundary"
        )
    return GuidedBaselineResult(
        initial_session_ref=initial_session_ref,
        final_session_ref=current_ref,
        observation_refs=tuple(observation_refs),
        baseline_frozen=True,
        abandoned=False,
    )
