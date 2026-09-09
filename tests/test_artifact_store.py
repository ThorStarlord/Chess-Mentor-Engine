from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

from chess_mentor_engine.storage import (
    ArtifactConflictError,
    ArtifactRef,
    ArtifactWrite,
    IntegrityError,
    LocalArtifactStore,
    MissingDependencyError,
    StorageError,
    UnsupportedSchemaError,
    prepare_artifact,
)


def _write(identity="one", *, payload=None, dependencies=(), participant="P01"):
    return ArtifactWrite(
        "test.v1", identity, participant,
        {"value": 1} if payload is None else payload, dependencies,
    )


def test_round_trip_is_canonical_idempotent_and_detached(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    value = {"z": [1, None, False], "a": "\u265e"}
    ref = store.put_many((_write(payload=value),))[0]
    again = store.put_many((_write(payload={"a": "\u265e", "z": [1, None, False]}),))[0]
    assert ref == again
    value["z"].append(9)
    recovered = LocalArtifactStore(store.path).get(ref, participant_id="P01")
    assert recovered.payload == {"a": "\u265e", "z": [1, None, False]}
    recovered.payload["z"].append(8)
    assert recovered.payload["z"] == [1, None, False]
    assert store.list_refs(participant_id="P01") == (ref,)


def test_conflict_preserves_original_and_rolls_back_other_writes(
    tmp_path: Path,
) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write(),))[0]
    with pytest.raises(ArtifactConflictError):
        store.put_many((_write("new"), _write(payload={"value": 2})))
    assert store.list_refs(participant_id="P01") == (ref,)
    assert store.get(ref, participant_id="P01").payload == {"value": 1}


def test_dependency_closed_batch_accepts_forward_reference(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    dependency = _write("dependency")
    dep_ref = prepare_artifact(dependency)[0]
    root = _write("root", dependencies=(dep_ref,))
    ref, actual = store.put_many((root, dependency))
    assert actual == dep_ref
    assert store.get(ref, participant_id="P01").dependencies == (dep_ref,)


def test_missing_dependency_rolls_back_entire_batch(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    missing = prepare_artifact(_write("missing"))[0]
    with pytest.raises(MissingDependencyError):
        store.put_many((_write(), _write("root", dependencies=(missing,))))
    assert store.list_refs(participant_id="P01") == ()


def test_transitive_missing_dependency_is_detected_on_read(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    leaf = store.put_many((_write("leaf"),))[0]
    middle = store.put_many((_write("middle", dependencies=(leaf,)),))[0]
    root = store.put_many((_write("root", dependencies=(middle,)),))[0]
    with sqlite3.connect(store.path) as connection:
        connection.execute("DELETE FROM artifacts WHERE digest=?", (leaf.digest,))
    with pytest.raises(MissingDependencyError):
        store.get(root, participant_id="P01")


def test_scope_is_required_and_cross_participant_dependencies_fail(
    tmp_path: Path,
) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write(),))[0]
    with pytest.raises(IntegrityError):
        store.get(ref, participant_id="P02")
    with pytest.raises(IntegrityError):
        store.put_many((_write("cross", dependencies=(ref,), participant="P02"),))
    assert store.list_refs(participant_id="P02") == ()
    other = store.put_many((_write(participant="P02"),))[0]
    assert other.digest != ref.digest


@pytest.mark.parametrize("field", ["kind", "artifact_id", "participant_id"])
def test_ref_metadata_cannot_impersonate_another_artifact(
    tmp_path: Path, field,
) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write(),))[0]
    forged = replace(ref, **{field: "forged"})
    with pytest.raises(IntegrityError):
        store.get(forged, participant_id=forged.participant_id)


@pytest.mark.parametrize("target", ["root", "dependency"])
def test_corruption_is_detected_before_use(tmp_path: Path, target: str) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    dependency = store.put_many((_write("dependency"),))[0]
    root = store.put_many((_write("root", dependencies=(dependency,)),))[0]
    damaged = root if target == "root" else dependency
    with sqlite3.connect(store.path) as connection:
        data = json.loads(connection.execute(
            "SELECT envelope FROM artifacts WHERE digest=?", (damaged.digest,)
        ).fetchone()[0])
        data["payload"]["value"] = 999
        connection.execute(
            "UPDATE artifacts SET envelope=? WHERE digest=?",
            (json.dumps(data), damaged.digest),
        )
    with pytest.raises(IntegrityError):
        store.get(root, participant_id="P01")
    with pytest.raises(IntegrityError):
        store.list_refs(participant_id="P01")


def test_idempotent_save_does_not_cover_up_corruption(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    store.put_many((_write(),))
    with sqlite3.connect(store.path) as connection:
        connection.execute("UPDATE artifacts SET envelope='not json'")
    with pytest.raises(IntegrityError):
        store.put_many((_write(),))


@pytest.mark.parametrize("version", [0, 2, True, "1"])
def test_unsupported_envelope_versions_fail_closed(tmp_path: Path, version) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write(),))[0]
    with sqlite3.connect(store.path) as connection:
        raw = connection.execute("SELECT envelope FROM artifacts").fetchone()[0]
        data = json.loads(raw)
        data["format_version"] = version
        connection.execute("UPDATE artifacts SET envelope=?", (json.dumps(data),))
    with pytest.raises(UnsupportedSchemaError):
        store.get(ref, participant_id="P01")


def test_unknown_database_version_is_not_migrated_silently(tmp_path: Path) -> None:
    path = tmp_path / "artifacts.sqlite3"
    store = LocalArtifactStore(path)
    ref = store.put_many((_write(),))[0]
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA user_version=99")
    with pytest.raises(UnsupportedSchemaError):
        LocalArtifactStore(path)
    with pytest.raises(UnsupportedSchemaError):
        store.get(ref, participant_id="P01")
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 99
        assert connection.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 1


def test_unrelated_database_is_not_claimed_or_modified(tmp_path: Path) -> None:
    path = tmp_path / "other.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE original(value TEXT)")
    with pytest.raises(UnsupportedSchemaError):
        LocalArtifactStore(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT name FROM sqlite_master").fetchall() == [
            ("original",)
        ]


@pytest.mark.parametrize("payload", [
    {"v": float("nan")}, {"v": float("inf")}, {"v": (1, 2)},
    {1: "bad key"}, {"v": object()},
])
def test_non_json_values_are_rejected(tmp_path: Path, payload) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    with pytest.raises(StorageError):
        store.put_many((_write(payload=payload),))
    assert store.list_refs(participant_id="P01") == ()


def test_duplicate_dependencies_are_rejected(tmp_path: Path) -> None:
    ref = prepare_artifact(_write())[0]
    with pytest.raises(IntegrityError, match="duplicate"):
        prepare_artifact(_write("root", dependencies=(ref, ref)))


def test_identifiers_are_data_not_filesystem_paths(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write("../../escape; DROP TABLE artifacts;"),))[0]
    assert store.get(ref, participant_id="P01").payload == {"value": 1}
    assert list(tmp_path.iterdir()) == [store.path]


def test_concurrent_idempotent_writers_produce_one_record(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    with ThreadPoolExecutor(max_workers=4) as pool:
        refs = list(pool.map(lambda _: store.put_many((_write(),))[0], range(8)))
    assert len(set(refs)) == 1
    assert store.list_refs(participant_id="P01") == (refs[0],)


def test_process_exit_before_commit_does_not_publish_partial_batch(
    tmp_path: Path,
) -> None:
    store = LocalArtifactStore(tmp_path / "artifacts.sqlite3")
    ref = store.put_many((_write(),))[0]
    script = """
import os, sqlite3, sys
connection = sqlite3.connect(sys.argv[1])
connection.execute('BEGIN IMMEDIATE')
connection.execute('DELETE FROM artifacts')
os._exit(23)
"""
    result = subprocess.run([sys.executable, "-c", script, str(store.path)], timeout=10)
    assert result.returncode == 23
    reopened = LocalArtifactStore(store.path)
    assert reopened.list_refs(participant_id="P01") == (ref,)


def test_digest_validation_rejects_invalid_reference() -> None:
    with pytest.raises(StorageError):
        ArtifactRef("test", "one", "P01", "not-a-digest")
