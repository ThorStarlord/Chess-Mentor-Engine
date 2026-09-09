"""Versioned, append-only local JSON artifacts; no domain authority lives here."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1
MAX_DEPENDENCY_DEPTH = 64


class StorageError(ValueError):
    """An artifact could not be stored or recovered safely."""


class IntegrityError(StorageError):
    """Stored bytes, identities, or dependency metadata disagree."""


class MissingDependencyError(StorageError):
    """An exact artifact or dependency is absent."""


class ArtifactConflictError(StorageError):
    """An immutable logical identity already has different content."""


class UnsupportedSchemaError(StorageError):
    """The database or artifact wire version is not supported."""


def canonical(value: object) -> str:
    """Canonical storage JSON, rejecting non-JSON values and non-string keys."""
    def check(item: object) -> None:
        if item is None or type(item) in (str, bool, int, float):
            return
        if type(item) is list:
            for child in item:
                check(child)
            return
        if type(item) is dict and all(type(key) is str for key in item):
            for child in item.values():
                check(child)
            return
        raise StorageError("payload must contain only JSON values and string keys")

    try:
        check(value)
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except (ValueError, TypeError, RecursionError) as exc:
        raise StorageError(f"invalid JSON payload: {exc}") from exc


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise StorageError("identity and participant fields must be nonempty strings")


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    kind: str
    artifact_id: str
    participant_id: str
    digest: str

    def __post_init__(self) -> None:
        for value in (self.kind, self.artifact_id, self.participant_id):
            _text(value)
        if (
            type(self.digest) is not str or len(self.digest) != 64
            or any(char not in "0123456789abcdef" for char in self.digest)
        ):
            raise StorageError("artifact digest must be a lowercase SHA-256")

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind, "artifact_id": self.artifact_id,
            "participant_id": self.participant_id, "digest": self.digest,
        }


@dataclass(frozen=True, slots=True)
class ArtifactWrite:
    kind: str
    artifact_id: str
    participant_id: str
    payload: dict[str, Any]
    dependencies: tuple[ArtifactRef, ...] = ()


@dataclass(frozen=True, slots=True)
class StoredArtifact:
    ref: ArtifactRef
    payload_json: str
    dependencies: tuple[ArtifactRef, ...]

    @property
    def payload(self) -> dict[str, Any]:
        """Return a fresh value, never a mutable view into stored state."""
        return json.loads(self.payload_json)


def prepare_artifact(write: ArtifactWrite) -> tuple[ArtifactRef, str]:
    """Compute an exact reference without performing a write."""
    for value in (write.kind, write.artifact_id, write.participant_id):
        _text(value)
    if type(write.payload) is not dict:
        raise StorageError("artifact payload must be a JSON object")
    if any(type(ref) is not ArtifactRef for ref in write.dependencies):
        raise StorageError("dependencies must be exact ArtifactRef values")
    if any(ref.participant_id != write.participant_id for ref in write.dependencies):
        raise IntegrityError("cross-participant dependency")
    ordered = tuple(sorted(write.dependencies, key=lambda ref: ref.digest))
    if len({ref.digest for ref in ordered}) != len(ordered):
        raise IntegrityError("duplicate dependency")
    envelope = canonical({
        "format_version": FORMAT_VERSION,
        "kind": write.kind,
        "artifact_id": write.artifact_id,
        "participant_id": write.participant_id,
        "payload": write.payload,
        "dependencies": [ref.to_dict() for ref in ordered],
    })
    return ArtifactRef(
        write.kind, write.artifact_id, write.participant_id, _digest(envelope)
    ), envelope


class LocalArtifactStore:
    """SQLite-backed immutable artifacts with atomic batches and verified reads.

    Each operation owns a connection and transaction. Scope isolation is not
    authentication: callers must protect this local plaintext database.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._transaction(write=True, initialize=True) as connection:
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if not tables and version == 0:
                connection.execute(
                    "CREATE TABLE artifacts (digest TEXT PRIMARY KEY, "
                    "kind TEXT NOT NULL, artifact_id TEXT NOT NULL, "
                    "participant_id TEXT NOT NULL, envelope TEXT NOT NULL, "
                    "UNIQUE(participant_id, kind, artifact_id))"
                )
                connection.execute("PRAGMA user_version = 1")
            elif tables != {"artifacts"} or version != FORMAT_VERSION:
                raise UnsupportedSchemaError("unsupported artifact database schema")

    @contextmanager
    def _transaction(
        self, *, write: bool = False, initialize: bool = False,
    ) -> Iterator[sqlite3.Connection]:
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
            connection.execute("PRAGMA synchronous = FULL")
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            if not initialize:
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version != FORMAT_VERSION:
                    raise UnsupportedSchemaError(
                        "unsupported artifact database version"
                    )
            yield connection
            connection.commit()
        except sqlite3.DatabaseError as exc:
            raise StorageError(f"artifact database operation failed: {exc}") from exc
        finally:
            if connection is not None:
                if connection.in_transaction:
                    connection.rollback()
                connection.close()

    def put(
        self, *, kind: str, artifact_id: str, participant_id: str,
        payload: dict[str, Any], dependencies: tuple[ArtifactRef, ...] = (),
    ) -> ArtifactRef:
        return self.put_many((ArtifactWrite(
            kind, artifact_id, participant_id, payload, dependencies
        ),))[0]

    def put_many(self, writes: tuple[ArtifactWrite, ...]) -> tuple[ArtifactRef, ...]:
        """Commit the entire dependency-closed batch or nothing; repeats are safe."""
        prepared = tuple(prepare_artifact(write) for write in writes)
        with self._transaction(write=True) as connection:
            for ref, envelope in prepared:
                existing = connection.execute(
                    "SELECT digest FROM artifacts "
                    "WHERE participant_id=? AND kind=? AND artifact_id=?",
                    (ref.participant_id, ref.kind, ref.artifact_id),
                ).fetchone()
                if existing is not None:
                    if existing[0] != ref.digest:
                        raise ArtifactConflictError(
                            "immutable artifact identity conflict"
                        )
                    continue
                connection.execute(
                    "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?)",
                    (ref.digest, ref.kind, ref.artifact_id,
                     ref.participant_id, envelope),
                )
            checked: dict[str, StoredArtifact] = {}
            for ref, _ in prepared:
                self._get(connection, ref, checked, set())
        return tuple(ref for ref, _ in prepared)

    def get(self, ref: ArtifactRef, *, participant_id: str) -> StoredArtifact:
        _text(participant_id)
        if ref.participant_id != participant_id:
            raise IntegrityError("requested participant does not match artifact scope")
        with self._transaction() as connection:
            return self._get(connection, ref, {}, set())

    def list_refs(
        self, *, participant_id: str, kind: str | None = None,
    ) -> tuple[ArtifactRef, ...]:
        _text(participant_id)
        with self._transaction() as connection:
            rows = connection.execute(
                "SELECT kind, artifact_id, participant_id, digest FROM artifacts "
                "WHERE participant_id=? AND (? IS NULL OR kind=?) "
                "ORDER BY kind, artifact_id, digest",
                (participant_id, kind, kind),
            ).fetchall()
            refs = tuple(ArtifactRef(*row) for row in rows)
            checked: dict[str, StoredArtifact] = {}
            for ref in refs:
                self._get(connection, ref, checked, set())
            return refs

    def _get(
        self, connection: sqlite3.Connection, ref: ArtifactRef,
        checked: dict[str, StoredArtifact], active: set[str],
    ) -> StoredArtifact:
        if ref.digest in active or len(active) >= MAX_DEPENDENCY_DEPTH:
            raise IntegrityError("cyclic or excessively deep artifact dependencies")
        if ref.digest in checked:
            result = checked[ref.digest]
            if result.ref != ref:
                raise IntegrityError("dependency reference metadata mismatch")
            return result
        row = connection.execute(
            "SELECT kind, artifact_id, participant_id, envelope FROM artifacts "
            "WHERE digest=?", (ref.digest,),
        ).fetchone()
        if row is None:
            raise MissingDependencyError(f"missing exact artifact: {ref.digest}")
        if row[:3] != (ref.kind, ref.artifact_id, ref.participant_id):
            raise IntegrityError("artifact index/reference mismatch")
        try:
            data = json.loads(row[3])
            if type(data) is not dict or set(data) != {
                "format_version", "kind", "artifact_id", "participant_id",
                "payload", "dependencies",
            }:
                raise IntegrityError("invalid artifact envelope")
            if type(data["format_version"]) is not int or data["format_version"] != 1:
                raise UnsupportedSchemaError("unsupported artifact envelope version")
            if type(data["dependencies"]) is not list:
                raise IntegrityError("invalid dependency manifest")
            dependencies = tuple(ArtifactRef(**value) for value in data["dependencies"])
            write = ArtifactWrite(
                data["kind"], data["artifact_id"], data["participant_id"],
                data["payload"], dependencies,
            )
            expected, envelope = prepare_artifact(write)
            if expected != ref or envelope != row[3]:
                raise IntegrityError(
                    "artifact checksum or canonical representation mismatch"
                )
        except (TypeError, KeyError, json.JSONDecodeError, RecursionError) as exc:
            raise IntegrityError("malformed artifact envelope") from exc
        active.add(ref.digest)
        for dependency in dependencies:
            self._get(connection, dependency, checked, active)
        active.remove(ref.digest)
        result = StoredArtifact(ref, canonical(write.payload), dependencies)
        checked[ref.digest] = result
        return result
