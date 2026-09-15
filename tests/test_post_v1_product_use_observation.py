from dataclasses import replace
import importlib.util

import pytest

from chess_mentor_engine.storage import ArtifactRef, LocalArtifactStore
from chess_mentor_engine.storage.tutor import SESSION_KIND


def _api():
    assert importlib.util.find_spec("chess_mentor_engine.observation") is not None
    from chess_mentor_engine.observation import (
        ProductUseObservationError,
        build_interaction_observation,
        load_interaction_observation,
        save_interaction_observation,
    )

    return (
        ProductUseObservationError,
        build_interaction_observation,
        load_interaction_observation,
        save_interaction_observation,
    )


def _session_ref(store: LocalArtifactStore, participant_id: str = "P01") -> ArtifactRef:
    return store.put(
        kind=SESSION_KIND,
        artifact_id="fixture-session",
        participant_id=participant_id,
        payload={"fixture": True},
    )


def test_observation_claim_ceiling_is_executable() -> None:
    Error, build, _, _ = _api()
    ref = ArtifactRef(SESSION_KIND, "fixture", "P01", "a" * 64)
    observation = build(
        participant_id="P01",
        tutor_session_ref=ref,
        event_type="review_started",
        occurred_at="2026-09-15T09:00:00-03:00",
        workflow_stage="selected",
    )

    assert observation.claim_scope == "descriptive_local_product_use_only"
    assert observation.learning_effect == "not_established"
    assert observation.tutor_efficacy == "not_established"
    assert observation.mastery == "not_established"

    with pytest.raises(Error, match="learning effect"):
        replace(observation, learning_effect="improved")


def test_observation_rejects_participant_scope_drift() -> None:
    Error, build, _, _ = _api()
    ref = ArtifactRef(SESSION_KIND, "fixture", "P01", "a" * 64)

    with pytest.raises(Error, match="participant"):
        build(
            participant_id="P02",
            tutor_session_ref=ref,
            event_type="review_started",
            occurred_at="2026-09-15T09:00:00-03:00",
            workflow_stage="selected",
        )


def test_observation_requires_timezone_and_unique_metadata_keys() -> None:
    Error, build, _, _ = _api()
    ref = ArtifactRef(SESSION_KIND, "fixture", "P01", "a" * 64)

    with pytest.raises(Error, match="timezone"):
        build(
            participant_id="P01",
            tutor_session_ref=ref,
            event_type="review_started",
            occurred_at="2026-09-15T09:00:00",
            workflow_stage="selected",
        )

    with pytest.raises(Error, match="metadata"):
        build(
            participant_id="P01",
            tutor_session_ref=ref,
            event_type="participant_feedback",
            occurred_at="2026-09-15T09:00:00-03:00",
            workflow_stage="frozen",
            metadata=(("workflow_clarity", "4"), ("workflow_clarity", "5")),
        )


def test_observation_round_trips_through_exact_session_dependency(tmp_path) -> None:
    _, build, load, save = _api()
    store = LocalArtifactStore(tmp_path / "mentor.sqlite3")
    session_ref = _session_ref(store)
    observation = build(
        participant_id="P01",
        tutor_session_ref=session_ref,
        event_type="response_frozen",
        occurred_at="2026-09-15T09:02:00-03:00",
        workflow_stage="frozen",
        metadata=(("stage_id", "A1"),),
    )

    ref = save(store, observation)
    recovered = load(store, ref, participant_id="P01")

    assert recovered == observation
    assert ref.kind == "post-v1.interaction-observation.v1"
