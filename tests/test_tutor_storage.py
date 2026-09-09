from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from test_m8_qualification import (
    S0,
    S2,
    S3,
    S4,
    S5,
    S6,
    S7,
    S11,
    S13,
    _complete_session,
    _explanation_provenance,
    _m6_bundle,
    _through_compare,
    _through_frozen,
    _through_position,
    _through_reveal,
)
from test_reasoning_discrepancy_facts import (
    _a1_prompt,
    _a2_prompt,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.storage import (
    IntegrityError,
    LocalArtifactStore,
    MissingDependencyError,
    UnsupportedSchemaError,
    load_tutor_session,
    replay_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.storage.codec import decode_record, encode_record
from chess_mentor_engine.tutoring import (
    TutorSession,
    TutorSessionError,
    capture_tutor_response,
    freeze_tutor_response,
    present_tutor_capture_stage,
    record_tutor_explanation,
    record_tutor_reasoning_comparison,
    reveal_tutor_objective_evidence,
    start_tutor_session,
)


def _prompts():
    return _a1_prompt(), _a2_prompt()


def _selected():
    return start_tutor_session(
        context=_upstream().player_context, capture_protocol=_protocol(), created_at=S0
    )


def _capturing():
    return present_tutor_capture_stage(
        _through_position()[1], stage_id="A1", prompt=_a1_prompt(), shown_at=S2
    )


def _explained():
    return record_tutor_explanation(
        _through_compare()[1], rendered_content="Session-local explanation.",
        provenance=_explanation_provenance(), created_at=S13,
    )[0]


@pytest.mark.parametrize("factory", [
    _selected, lambda: _through_position()[1], _capturing,
    lambda: _through_frozen()[1], lambda: _through_reveal()[1],
    lambda: _through_compare()[1], _explained, lambda: _complete_session()[0],
])
def test_every_m8_state_round_trips_through_verified_replay(tmp_path: Path, factory):
    original = factory()
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    ref = save_tutor_session(store, original, prompts=_prompts())
    recovered = load_tutor_session(
        LocalArtifactStore(store.path), ref, participant_id="P01"
    )
    assert recovered.session == original
    assert recovered.session.to_dict() == original.to_dict()
    assert isinstance(recovered.session.events, tuple)
    assert isinstance(recovered.session.capture_session.responses, tuple)
    again = save_tutor_session(store, original, prompts=tuple(reversed(_prompts())))
    assert again == ref
    assert len(store.list_refs(participant_id="P01")) == 3


def test_comparison_order_is_canonical_before_hashing() -> None:
    upstream, revealed = _through_reveal()
    context, assessment, assertions = _m6_bundle(upstream, revealed.capture_session)
    assert len(assertions) >= 2
    ordered = tuple(sorted(assertions, key=lambda item: item.assertion_id))
    first, comparison = record_tutor_reasoning_comparison(
        revealed, reasoning_context=context, assessment=assessment,
        assertions=ordered, recorded_at=S11,
    )
    second, reversed_comparison = record_tutor_reasoning_comparison(
        revealed, reasoning_context=context, assessment=assessment,
        assertions=tuple(reversed(ordered)), recorded_at=S11,
    )
    expected = hashlib.sha256(
        canonical_json(comparison.to_dict(include_identity=False)).encode("utf-8")
    ).hexdigest()
    assert comparison.fingerprint == expected
    assert reversed_comparison.fingerprint == expected
    assert first == second
    assert revealed.state == "revealed"


def test_fresh_process_recovers_completed_session_without_test_helpers(tmp_path: Path):
    original = _complete_session()[0]
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    ref = save_tutor_session(store, original, prompts=_prompts())
    script = """
import json, sys
from chess_mentor_engine.storage import ArtifactRef, LocalArtifactStore
from chess_mentor_engine.storage import load_tutor_session
ref = ArtifactRef(**json.loads(sys.argv[2]))
result = load_tutor_session(LocalArtifactStore(sys.argv[1]), ref, participant_id='P01')
print(json.dumps(result.session.to_dict(), sort_keys=True))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(store.path), json.dumps(ref.to_dict())],
        text=True, capture_output=True, check=True, timeout=20,
    )
    assert json.loads(result.stdout) == original.to_dict()


def _continue_to_frozen(session, prompts):
    for stage_id, prompt, shown, submitted, frozen in (
        ("A1", prompts[0], S2, S3, S4), ("A2", prompts[1], S5, S6, S7)
    ):
        session = present_tutor_capture_stage(
            session, stage_id=stage_id, prompt=prompt, shown_at=shown
        )
        session = capture_tutor_response(
            session, stage_id=stage_id, raw_response="e4", submitted_at=submitted
        )
        session = freeze_tutor_response(session, stage_id=stage_id, frozen_at=frozen)
    return session


def test_fresh_process_resumes_without_bypassing_freeze_gate(tmp_path: Path) -> None:
    original = _through_position()[1]
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    ref = save_tutor_session(store, original, prompts=_prompts())
    expected = _continue_to_frozen(original, _prompts())
    script = """
import json, sys
from chess_mentor_engine.storage import ArtifactRef, LocalArtifactStore
from chess_mentor_engine.storage import load_tutor_session, save_tutor_session
from chess_mentor_engine.tutoring import TutorSessionError
from chess_mentor_engine.tutoring import reveal_tutor_objective_evidence
from chess_mentor_engine.tutoring import present_tutor_capture_stage
from chess_mentor_engine.tutoring import capture_tutor_response, freeze_tutor_response
store = LocalArtifactStore(sys.argv[1])
ref = ArtifactRef(**json.loads(sys.argv[2]))
result = load_tutor_session(store, ref, participant_id='P01')
session = result.session
by_id = {p.prompt_definition_id: p for p in result.prompts}
for index, stage in enumerate(session.capture_session.protocol.stages):
    minute = 2 + index * 3
    stamp = lambda m: f'2026-09-08T10:{m:02d}:00-03:00'
    session = present_tutor_capture_stage(session, stage_id=stage.stage_id,
        prompt=by_id[stage.prompt_definition_id], shown_at=stamp(minute))
    session = capture_tutor_response(session, stage_id=stage.stage_id,
        raw_response='e4', submitted_at=stamp(minute+1))
    session = freeze_tutor_response(
        session, stage_id=stage.stage_id, frozen_at=stamp(minute+2))
    if index == 0:
        try:
            reveal_tutor_objective_evidence(session, revealed_at=stamp(minute+2),
                rendered_content='not permitted')
        except TutorSessionError:
            pass
        else:
            raise AssertionError('recovery bypassed freeze-before-reveal')
ref = save_tutor_session(store, session, prompts=result.prompts)
print(json.dumps({'state': session.state, 'fingerprint': session.snapshot_fingerprint,
    'ref': ref.to_dict()}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(store.path), json.dumps(ref.to_dict())],
        text=True, capture_output=True, check=True, timeout=20,
    )
    data = json.loads(result.stdout)
    assert data["state"] == "frozen"
    assert data["fingerprint"] == expected.snapshot_fingerprint
    assert load_tutor_session(store, ref, participant_id="P01").session == original
    assert len(store.list_refs(participant_id="P01")) == 4


def test_missing_planned_prompts_do_not_partially_save(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    with pytest.raises(MissingDependencyError):
        save_tutor_session(store, _selected(), prompts=(_a1_prompt(),))
    assert store.list_refs(participant_id="P01") == ()


def test_missing_stored_prompt_blocks_recovery(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    ref = save_tutor_session(store, _selected(), prompts=_prompts())
    dependency = store.get(ref, participant_id="P01").dependencies[0]
    with sqlite3.connect(store.path) as connection:
        connection.execute("DELETE FROM artifacts WHERE digest=?", (dependency.digest,))
    with pytest.raises(MissingDependencyError):
        load_tutor_session(store, ref, participant_id="P01")


def test_wrong_prompt_fingerprint_is_rejected(tmp_path: Path) -> None:
    prompts = (replace(_a1_prompt(), definition_fingerprint="forged"), _a2_prompt())
    with pytest.raises(IntegrityError):
        save_tutor_session(LocalArtifactStore(tmp_path / "tutor.sqlite3"),
                           _selected(), prompts=prompts)


def test_storage_checksum_does_not_replace_domain_validation(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    original = _complete_session()[0]
    ref = save_tutor_session(store, original, prompts=_prompts())
    stored = store.get(ref, participant_id="P01")
    payload = stored.payload
    payload["session"]["snapshot_fingerprint"] = "forged"
    # A storage checksum is not domain validation; recovery must still reject this.
    forged = store.put(
        kind=ref.kind, artifact_id=f"{original.tutor_session_id}:forged",
        participant_id="P01", payload=payload, dependencies=stored.dependencies,
    )
    assert store.get(forged, participant_id="P01").payload == payload
    with pytest.raises(IntegrityError, match="replay"):
        load_tutor_session(store, forged, participant_id="P01")


@pytest.mark.parametrize("mutation", ["extra_field", "invalid_literal", "wrong_type"])
def test_codec_rejects_schema_drift_and_type_confusion(mutation: str) -> None:
    payload = encode_record(_selected())
    if mutation == "extra_field":
        payload["__type__"] = "os.system"
    elif mutation == "invalid_literal":
        payload["state"] = "mastered"
    else:
        payload["events"][0]["sequence"] = True
    with pytest.raises(IntegrityError):
        decode_record(payload, TutorSession)


def test_unsupported_workflow_is_not_silently_replayed() -> None:
    with pytest.raises(UnsupportedSchemaError):
        replay_tutor_session(
            replace(_selected(), workflow_version="99"), prompts=_prompts()
        )


def test_corrupted_event_and_snapshot_are_not_repaired_on_save(tmp_path: Path) -> None:
    original = _through_frozen()[1]
    event = replace(original.events[-1], artifact_fingerprint="forged")
    forged = replace(original, events=original.events[:-1] + (event,))
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    with pytest.raises(IntegrityError):
        save_tutor_session(store, forged, prompts=_prompts())
    assert store.list_refs(participant_id="P01") == ()


def test_recovered_pre_reveal_session_retains_existing_gate(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "tutor.sqlite3")
    ref = save_tutor_session(store, _capturing(), prompts=_prompts())
    recovered = load_tutor_session(store, ref, participant_id="P01")
    with pytest.raises(TutorSessionError):
        reveal_tutor_objective_evidence(
            recovered.session, revealed_at=S3, rendered_content="too early"
        )
