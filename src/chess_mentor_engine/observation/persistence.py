"""Persistence for descriptive product-use observations."""

from __future__ import annotations

from typing import Any

from chess_mentor_engine.storage import ArtifactRef, IntegrityError, LocalArtifactStore
from chess_mentor_engine.storage.codec import decode_record, encode_record

from .model import OBSERVATION_KIND, InteractionObservation

CODEC_VERSION = 1


def save_interaction_observation(
    store: LocalArtifactStore,
    observation: InteractionObservation,
) -> ArtifactRef:
    payload = {
        "codec_version": CODEC_VERSION,
        "observation": encode_record(observation),
    }
    return store.put(
        kind=OBSERVATION_KIND,
        artifact_id=observation.observation_id,
        participant_id=observation.participant_id,
        payload=payload,
        dependencies=(observation.tutor_session_ref,),
    )


def _payload(data: dict[str, Any]) -> dict[str, Any]:
    if set(data) != {"codec_version", "observation"}:
        raise IntegrityError("invalid product-use observation envelope")
    if data["codec_version"] != CODEC_VERSION:
        raise IntegrityError("unsupported product-use observation codec")
    value = data["observation"]
    if type(value) is not dict:
        raise IntegrityError("product-use observation record must be an object")
    return value


def load_interaction_observation(
    store: LocalArtifactStore,
    ref: ArtifactRef,
    *,
    participant_id: str,
) -> InteractionObservation:
    if ref.kind != OBSERVATION_KIND:
        raise IntegrityError("not a product-use observation artifact")
    stored = store.get(ref, participant_id=participant_id)
    observation = decode_record(_payload(stored.payload), InteractionObservation)
    if observation.participant_id != participant_id:
        raise IntegrityError("product-use observation participant mismatch")
    if ref.artifact_id != observation.observation_id:
        raise IntegrityError("product-use observation storage identity mismatch")
    if stored.dependencies != (observation.tutor_session_ref,):
        raise IntegrityError("product-use observation requires its exact M8 dependency")
    return observation
