"""M13 persistent tutor CLI qualification and rejection coverage."""

from __future__ import annotations

import json
from pathlib import Path

from test_m8_qualification import (
    S0,
    S1,
    S2,
    S3,
    S4,
    S5,
    S6,
    S7,
    S8,
    S11,
    S12,
    S13,
    S14,
    _complete_session,
    _explanation_provenance,
    _ledger_context,
    _m6_bundle,
    _through_compare,
    _through_frozen,
    _through_position,
    _through_reveal,
)
from test_reasoning_discrepancy_facts import (
    _a1_prompt,
    _a2_prompt,
    _default_a1,
    _default_a2,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import build_position_context
from chess_mentor_engine.cli import main
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.storage.codec import encode_record
from chess_mentor_engine.storage.tutor import SESSION_KIND
from chess_mentor_engine.tutoring import (
    capture_tutor_response,
    freeze_tutor_response,
    present_tutor_capture_stage,
)


def _prompts():
    return _a1_prompt(), _a2_prompt()


def _json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return path


def _record(path: Path, value) -> Path:
    return _json(path, encode_record(value))


def _records(path: Path, values) -> Path:
    return _json(path, [encode_record(value) for value in values])


def _invoke(capsys, *argv: str):
    code = main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _start_args(tmp_path: Path, db: Path, *extra: str) -> tuple[str, ...]:
    upstream = _upstream()
    return (
        "tutor",
        "start",
        "--db",
        str(db),
        "--participant",
        "P01",
        "--context-json",
        str(_record(tmp_path / "context.json", upstream.player_context)),
        "--protocol-json",
        str(_record(tmp_path / "protocol.json", _protocol())),
        "--prompts-json",
        str(_records(tmp_path / "prompts.json", _prompts())),
        "--created-at",
        S0,
        *extra,
    )


def _ref(payload) -> ArtifactRef:
    return ArtifactRef(**payload["ref"])


def _ids(store: LocalArtifactStore) -> tuple[str, ...]:
    return tuple(
        ref.artifact_id
        for ref in store.list_refs(participant_id="P01", kind=SESSION_KIND)
    )


def _reveal_bundle() -> dict:
    reveal = _through_reveal()[1].capture_session.objective_reveal
    assert reveal is not None
    return {
        "rendered_content": reveal.rendered_content,
        "position_analysis_refs": [
            encode_record(item) for item in reveal.position_analysis_refs
        ],
        "decision_comparison_ref": (
            None
            if reveal.decision_comparison_ref is None
            else encode_record(reveal.decision_comparison_ref)
        ),
        "selection_signal_refs": [
            encode_record(item) for item in reveal.selection_signal_refs
        ],
    }


def _advance(capsys, db: Path, previous, command: str, *args: str):
    code, payload, error = _invoke(
        capsys,
        "tutor",
        command,
        "--db",
        str(db),
        "--participant",
        "P01",
        previous["ref"]["artifact_id"],
        *args,
    )
    assert code == 0 and error == ""
    assert payload["previous_ref"] == previous["ref"]
    return payload


def test_start_requires_explicit_creation_and_exact_participant(
    tmp_path, capsys
) -> None:
    db = tmp_path / "tutor.sqlite3"
    code, payload, error = _invoke(capsys, *_start_args(tmp_path, db))
    assert code == 2 and payload is None and "--create-db" in error
    assert not db.exists()

    code, payload, error = _invoke(
        capsys, *_start_args(tmp_path, db, "--create-db")
    )
    assert code == 0 and error == "" and payload["state"] == "selected"
    assert payload["created_db"] is True
    recovered = load_tutor_session(
        LocalArtifactStore(db), _ref(payload), participant_id="P01"
    )
    assert recovered.session.snapshot_fingerprint == payload["snapshot_fingerprint"]

    other = tmp_path / "other.sqlite3"
    args = list(_start_args(tmp_path, other, "--create-db"))
    args[args.index("P01")] = "P02"
    code, hidden, error = _invoke(capsys, *args)
    assert code == 2 and hidden is None and "participant" in error
    assert not other.exists()


def test_status_replay_verifies_and_does_not_cross_scope(tmp_path, capsys) -> None:
    db = tmp_path / "tutor.sqlite3"
    _, started, _ = _invoke(capsys, *_start_args(tmp_path, db, "--create-db"))
    artifact_id = started["ref"]["artifact_id"]
    code, status, error = _invoke(
        capsys,
        "tutor",
        "status",
        "--db",
        str(db),
        "--participant",
        "P01",
        artifact_id,
    )
    assert code == 0 and error == "" and status["verified_replay"] is True
    assert status["prompt_count"] == 2

    code, hidden, error = _invoke(
        capsys,
        "tutor",
        "status",
        "--db",
        str(db),
        "--participant",
        "P02",
        artifact_id,
    )
    assert code == 2 and hidden is None
    assert "P01" not in error


def test_cli_reproduces_full_m8_workflow_and_preserves_dependencies(
    tmp_path, capsys
) -> None:
    upstream = _upstream()
    db = tmp_path / "tutor.sqlite3"
    store = LocalArtifactStore(db)
    source_ref = store.put(
        kind="source.evidence.v1",
        artifact_id="source-1",
        participant_id="P01",
        payload={"source": "qualification"},
    )
    dep_path = _records(tmp_path / "dependencies.json", (source_ref,))
    code, current, error = _invoke(
        capsys,
        *_start_args(tmp_path, db, "--dependencies-json", str(dep_path)),
    )
    assert code == 0 and error == "" and current["created_db"] is False

    packet = build_position_context(upstream.game, upstream.position)
    current = _advance(
        capsys,
        db,
        current,
        "present-position",
        "--packet-json",
        str(_record(tmp_path / "packet.json", packet)),
        "--shown-at",
        S1,
    )
    assert current["state"] == "presented"

    for stage, shown, response, structured, submitted, frozen in (
        ("A1", S2, "I would play e4.", _default_a1(), S3, S4),
        (
            "A2",
            S5,
            "I considered e4 and expect ...e5 followed by Nf3.",
            _default_a2(),
            S6,
            S7,
        ),
    ):
        current = _advance(
            capsys,
            db,
            current,
            "present-stage",
            "--stage-id",
            stage,
            "--shown-at",
            shown,
        )
        current = _advance(
            capsys,
            db,
            current,
            "respond",
            "--stage-id",
            stage,
            "--response",
            response,
            "--structured-json",
            str(_record(tmp_path / f"{stage}.json", structured)),
            "--submitted-at",
            submitted,
        )
        current = _advance(
            capsys,
            db,
            current,
            "freeze",
            "--stage-id",
            stage,
            "--frozen-at",
            frozen,
        )

    assert current["state"] == "frozen"
    assert current["snapshot_fingerprint"] == _through_frozen()[1].snapshot_fingerprint

    current = _advance(
        capsys,
        db,
        current,
        "reveal",
        "--bundle-json",
        str(_json(tmp_path / "reveal.json", _reveal_bundle())),
        "--revealed-at",
        S8,
    )
    revealed = _through_reveal()[1]
    assert current["snapshot_fingerprint"] == revealed.snapshot_fingerprint

    context, assessment, assertions = _m6_bundle(upstream, revealed.capture_session)
    compare = {
        "reasoning_context": encode_record(context),
        "assessment": encode_record(assessment),
        "assertions": [encode_record(item) for item in assertions],
    }
    current = _advance(
        capsys,
        db,
        current,
        "compare",
        "--bundle-json",
        str(_json(tmp_path / "compare.json", compare)),
        "--recorded-at",
        S11,
    )
    assert current["snapshot_fingerprint"] == _through_compare()[1].snapshot_fingerprint

    snapshot, revision = _ledger_context()
    hypothesis = {
        "ledger_snapshot": encode_record(snapshot),
        "active_revisions": [encode_record(revision)],
    }
    current = _advance(
        capsys,
        db,
        current,
        "attach-hypothesis",
        "--bundle-json",
        str(_json(tmp_path / "hypothesis.json", hypothesis)),
        "--attached-at",
        S12,
    )
    assert current["state"] == "compared"

    text = (
        "This position has a supported local discrepancy under the cited M6 "
        "assessment. The active M7 hypothesis remains descriptive context only."
    )
    content = tmp_path / "explanation.txt"
    content.write_text(text, encoding="utf-8")
    current = _advance(
        capsys,
        db,
        current,
        "explain",
        "--content-file",
        str(content),
        "--provenance-json",
        str(_record(tmp_path / "provenance.json", _explanation_provenance())),
        "--created-at",
        S13,
    )
    assert current["state"] == "explained"
    current = _advance(
        capsys,
        db,
        current,
        "complete",
        "--completed-at",
        S14,
    )

    expected = _complete_session()[0]
    assert current["state"] == "completed"
    assert current["snapshot_fingerprint"] == expected.snapshot_fingerprint
    stored = store.get(_ref(current), participant_id="P01")
    assert source_ref in stored.dependencies
    recovered = load_tutor_session(store, _ref(current), participant_id="P01")
    assert recovered.session == expected
    assert len(_ids(store)) == 13
    assert all(
        not ref.kind.startswith("learner_state")
        for ref in store.list_refs(participant_id="P01")
    )


def test_reveal_gate_and_malformed_bundle_fail_without_checkpoint(
    tmp_path, capsys
) -> None:
    session = _through_position()[1]
    session = present_tutor_capture_stage(
        session, stage_id="A1", prompt=_a1_prompt(), shown_at=S2
    )
    session = capture_tutor_response(
        session,
        stage_id="A1",
        raw_response="I would play e4.",
        structured_response=_default_a1(),
        submitted_at=S3,
    )
    session = freeze_tutor_response(session, stage_id="A1", frozen_at=S4)
    db = tmp_path / "tutor.sqlite3"
    store = LocalArtifactStore(db)
    ref = save_tutor_session(store, session, prompts=_prompts())
    before = _ids(store)

    code, payload, error = _invoke(
        capsys,
        "tutor",
        "reveal",
        "--db",
        str(db),
        "--participant",
        "P01",
        ref.artifact_id,
        "--bundle-json",
        str(_json(tmp_path / "reveal.json", _reveal_bundle())),
        "--revealed-at",
        S4,
    )
    assert code == 2 and payload is None and "freeze" in error
    assert _ids(store) == before

    revealed_ref = save_tutor_session(store, _through_reveal()[1], prompts=_prompts())
    before = _ids(store)
    malformed = {
        "reasoning_context": {},
        "assessment": {},
        "assertions": [],
        "extra": True,
    }
    code, payload, error = _invoke(
        capsys,
        "tutor",
        "compare",
        "--db",
        str(db),
        "--participant",
        "P01",
        revealed_ref.artifact_id,
        "--bundle-json",
        str(_json(tmp_path / "bad.json", malformed)),
        "--recorded-at",
        S11,
    )
    assert code == 2 and payload is None and "exactly" in error
    assert _ids(store) == before


def test_missing_database_mutation_never_creates_it(tmp_path, capsys) -> None:
    db = tmp_path / "missing.sqlite3"
    code, payload, error = _invoke(
        capsys,
        "tutor",
        "complete",
        "--db",
        str(db),
        "--participant",
        "P01",
        "missing",
        "--completed-at",
        S14,
    )
    assert code == 2 and payload is None and "does not exist" in error
    assert not db.exists()
