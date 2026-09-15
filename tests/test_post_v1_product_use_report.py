import importlib.util

from chess_mentor_engine.storage import LocalArtifactStore
from chess_mentor_engine.storage.tutor import SESSION_KIND


def _api():
    spec = importlib.util.find_spec("chess_mentor_engine.observation.report")
    assert spec is not None
    from chess_mentor_engine.observation import (
        build_interaction_observation,
        save_interaction_observation,
    )
    from chess_mentor_engine.observation.report import build_product_use_report

    return (
        build_interaction_observation,
        save_interaction_observation,
        build_product_use_report,
    )


def _session(store: LocalArtifactStore, participant: str):
    return store.put(
        kind=SESSION_KIND,
        artifact_id=f"session-{participant}",
        participant_id=participant,
        payload={"fixture": participant},
    )


def test_product_use_report_is_participant_scoped_and_descriptive(tmp_path) -> None:
    build, save, report = _api()
    store = LocalArtifactStore(tmp_path / "mentor.sqlite3")
    p1 = _session(store, "P01")
    p2 = _session(store, "P02")

    for event_type, action, metadata in (
        ("review_started", None, ()),
        ("response_frozen", None, (("stage_id", "A1"),)),
        ("proposal_generated", "ASK_THREATS", ()),
        ("participant_feedback", None, (("workflow_clarity", "4"),)),
    ):
        save(
            store,
            build(
                participant_id="P01",
                tutor_session_ref=p1,
                event_type=event_type,
                occurred_at="2026-09-15T09:00:00-03:00",
                workflow_stage="frozen",
                action=action,
                metadata=metadata,
            ),
        )

    save(
        store,
        build(
            participant_id="P02",
            tutor_session_ref=p2,
            event_type="review_started",
            occurred_at="2026-09-15T09:00:00-03:00",
            workflow_stage="selected",
        ),
    )

    result = report(store, participant_id="P01")

    assert result.total_observations == 4
    assert dict(result.event_counts)["review_started"] == 1
    assert dict(result.action_counts) == {"ASK_THREATS": 1}
    assert result.claim_scope == "descriptive_local_product_use_summary_only"
    assert result.learning_effect == "not_established"
    assert result.tutor_efficacy == "not_established"
    assert result.mastery == "not_established"
