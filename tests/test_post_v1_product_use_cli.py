import json

import pytest
from test_reasoning_discrepancy_facts import (
    T1,
    _a1_prompt,
    _a2_prompt,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import build_position_context
from chess_mentor_engine.local_tutor_entry import main as local_main
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.storage.codec import encode_record
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
    packet = build_position_context(upstream.game, upstream.position)
    packet_path = tmp_path / "position-context.json"
    packet_path.write_text(
        json.dumps(encode_record(packet), sort_keys=True),
        encoding="utf-8",
    )
    return db, session_ref, packet_path


def test_product_use_commands_are_installed() -> None:
    for command in ("review", "report"):
        with pytest.raises(SystemExit) as exc_info:
            local_main([command, "--help"])
        assert exc_info.value.code == 0


def test_review_cli_guides_selected_m8_checkpoint_to_baseline_freeze(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    db, session_ref, packet_path = _selected_checkpoint(tmp_path)
    answers = iter(("I would play e4.", "I considered e4 and ...e5."))
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    code = local_main(
        [
            "review",
            "--db",
            str(db),
            "--participant",
            "P01",
            "--position-json",
            str(packet_path),
            session_ref.artifact_id,
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert code == 0
    assert payload["baseline_frozen"] is True
    assert payload["abandoned"] is False
    assert payload["claim_scope"] == "descriptive_local_product_use_only"
    assert payload["learning_effect"] == "not_established"
    assert payload["tutor_efficacy"] == "not_established"
    assert payload["mastery"] == "not_established"
    assert payload["next_authority"] == "cme-local-tutor next"

    final_ref = ArtifactRef(**payload["final_session_ref"])
    recovered = load_tutor_session(
        LocalArtifactStore(db),
        final_ref,
        participant_id="P01",
    )
    assert recovered.session.state == "frozen"
    assert recovered.session.capture_session.objective_reveal is None
    assert len(payload["observation_refs"]) == 8


def test_report_cli_summarizes_only_descriptive_product_use(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    db, session_ref, packet_path = _selected_checkpoint(tmp_path)
    answers = iter(("I would play e4.", "I considered e4 and ...e5."))
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert local_main(
        [
            "review",
            "--db",
            str(db),
            "--participant",
            "P01",
            "--position-json",
            str(packet_path),
            session_ref.artifact_id,
        ]
    ) == 0
    capsys.readouterr()

    assert local_main(
        ["report", "--db", str(db), "--participant", "P01"]
    ) == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["total_observations"] == 8
    assert payload["event_counts"]["review_started"] == 1
    assert payload["event_counts"]["response_frozen"] == 2
    assert payload["claim_scope"] == (
        "descriptive_local_product_use_summary_only"
    )
    assert payload["learning_effect"] == "not_established"
    assert payload["tutor_efficacy"] == "not_established"
    assert payload["mastery"] == "not_established"
