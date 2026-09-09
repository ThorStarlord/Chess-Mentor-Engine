# Durable artifacts and verified M8 replay

## Bounded scope

This post-M9 feature adds a local append-only JSON artifact store and typed M8
session recovery. It does not implement M10, M11, a learner score, a product CLI,
a hosted service, or new diagnostic/pedagogical authority. The existing domain
packages remain independent of storage.

## Storage contract

`LocalArtifactStore` uses a local SQLite database and Python's standard library.
Each write is a version-1 canonical JSON envelope containing `kind`,
`artifact_id`, `participant_id`, `payload`, and exact dependency references.
An `ArtifactRef` carries those identity fields plus the envelope SHA-256 digest.
This storage digest is distinct from every native evidence fingerprint.

The `(participant_id, kind, artifact_id)` identity is immutable. Repeating the
same content is idempotent; different content under that identity raises
`ArtifactConflictError`. `put_many` commits the whole dependency-closed batch or
nothing, including forward references within the batch. Missing dependencies or
conflicts roll back every write. Explicit transactions use SQLite FULL
synchronization; recovery still depends on the filesystem honoring durability.

Reads verify the envelope checksum, canonical representation, indexed identity,
participant scope, supported version, and transitive declared dependency graph.
Missing, corrupt, cross-participant, cyclic, or excessively deep dependencies
fail closed. All SQL values are parameter-bound; artifact IDs never become paths.
Each operation owns and closes its connection. Concurrent writers are serialized
by SQLite, with a bounded lock timeout surfaced as `StorageError`.

## Typed M8 adapter

`save_tutor_session` requires the exact definitions for every planned prompt,
including prompts not yet presented. It stores prompts and the session in one
transaction. Session artifact IDs include both native session ID and snapshot
fingerprint, so advancing a session appends a new snapshot rather than overwriting
history. Additional separately stored upstream artifacts may be supplied as
explicit dependencies.

The structural codec reconstructs nested dataclasses and tuples from trusted
Python schemas, checking exact fields, primitive types, literal values, and
constructor invariants. It does not use pickle, eval, executable payloads, or
payload-selected imports. Unknown fields/codec versions are rejected rather than
silently migrated. Annotation/schema changes require explicit codec compatibility
review and versioning.

Recovery does not trust deserialized state alone. `replay_tutor_session` starts
from the stored context/protocol, reruns every public M8 transition with exact
stored inputs, and checks every event and the complete final snapshot. The
returned session can continue through the same domain APIs. Recovery does not
bypass required freezes, reveal ordering, M6 capture binding, or M7 context checks.
Extra unjournaled M5 amendments/exposures are not silently discarded: a snapshot
that cannot be reproduced by its M8 history is rejected.

## Comparison fingerprint repair and legacy evidence

`record_tutor_reasoning_comparison` now orders assertions before both hashing and
construction. Reordering the same assertion set produces the same comparison and
session identity. Ordered move lists and event histories are not sorted.

The public model/schema and M8 workflow version remain unchanged. Previously
self-consistent v1 histories can replay unchanged. A historical comparison whose
fingerprint was computed before sorting is rejected, never silently repaired or
relabeled. Preserve such an original as a generic JSON artifact for audit;
regenerate a corrected lineage explicitly through the domain APIs when needed.

## Claim ceiling and limitations

Checksums detect corruption relative to the supplied reference; they do not
provide signatures, authenticated authorship, or protection against an attacker
who can replace both data and trusted references. The database is plaintext and
participant scoping is not authentication. Protect it with local access controls
and backups. There is no automatic migration, deletion API, encryption, remote
synchronization, or storage quota in this bounded version.

The generic store preserves JSON; it does not certify its scientific meaning.
Typed recovery supports M8 plus its complete embedded records and required prompt
dependencies. It revalidates the existing M8 checks but does not independently
requalify every external M1-M7 reference, regenerate engine analysis, or judge
explanation truth. Upstream evidence closure beyond M8's required inputs must be
supplied explicitly as declared dependencies. No learning or mastery claim is
created by storing or replaying a session.

See [the operational runbook](../runbooks/durable-artifacts-and-replay.md) and
`tests/test_artifact_store.py` / `tests/test_tutor_storage.py`.
