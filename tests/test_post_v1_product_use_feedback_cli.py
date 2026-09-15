import json

import pytest
from test_reasoning_discrepancy_facts import T1, _a1_prompt, _a2_prompt, _protocol, _upstream

from chess_mentor_engine.local_tutor_entry import main as local_main
from chess_mentor_engine.storage import LocalArtifactStore, save_tutor_session
from chess_mentor_engine.tutoring import start_tutor_session


def _selected_checkpoint(tmp_path):
    upstream = _upstream()
    db = tmp_path / "mentor.sqlite3"
    store = LocalArtifactStore(db)
    session = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=T1,
    )
    session_ref = save_tutor_session(
        store,
        session,
        prompts=(_a1_prompt(), _a2_prompt()),
    )
    return db, session_ref


def test_feedback_command_is_installed() -> None:
    with pytest.raises(SystemExit) as exc_info:
        local_main(["feedback", "--help"])
    assert exc_info.value.code == 0


def test_feedback_cli_persists_explicit_self_report(tmp_path, capsys) -> None:
    db, session_ref = _selected_checkpoint(tmp_path)

    code = local_main(
        [
            "feedback",
            "--db",
            str(db),
            "--participant",
            "P01",
            "--review-relevance",
            "4",
            "--workflow-clarity",
            "3",
            "--would-review-again",
            "5",
            "--note",
            "Useful position, but setup still feels technical.",
            session_ref.artifact_id,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["event_type"] == "participant_feedback"
    assert payload["claim_scope"] == "descriptive_local_product_use_only"
    assert payload["learning_effect"] == "not_established"
    assert payload["tutor_efficacy"] == "not_established"
    assert payload["mastery"] == "not_established"

    assert local_main(
        ["report", "--db", str(db), "--participant", "P01"]
    ) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["total_observations"] == 1
    assert report["feedback_entries"] == [
        {
            "note": "Useful position, but setup still feels technical.",
            "review_relevance": "4",
            "workflow_clarity": "3",
            "would_review_again": "5",
        }
    ]


def test_feedback_cli_rejects_out_of_range_rating(tmp_path) -> None:
    db, session_ref = _selected_checkpoint(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        local_main(
            [
                "feedback",
                "--db",
                str(db),
                "--participant",
                "P01",
                "--review-relevance",
                "6",
                "--workflow-clarity",
                "3",
                "--would-review-again",
                "5",
                session_ref.artifact_id,
            ]
        )
    assert exc_info.value.code == 2
