# Local artifact storage and tutor recovery

Use Python 3.11+ and the existing package installation:

```bash
python -m pip install -e ".[dev]"
pytest tests/test_artifact_store.py tests/test_tutor_storage.py
pytest
ruff check .
python -m compileall -q src tests
```

The separate existing Stockfish integration gate remains unchanged.

## Save and recover

With a session created through the public M8 APIs and its exact planned prompt
definitions, use:

```python
from chess_mentor_engine.storage import (
    ArtifactRef, LocalArtifactStore, load_tutor_session, save_tutor_session,
)

store = LocalArtifactStore("local-data/evidence.sqlite3")
ref = save_tutor_session(store, session, prompts=planned_prompts)
# Persist ref.to_dict() with the caller's own session locator/checkpoint.

# In a later process: reconstruct the exact saved reference from that locator.
ref = ArtifactRef(**saved_reference)
recovered = load_tutor_session(store, ref, participant_id="P01")
session = recovered.session
planned_prompts = recovered.prompts
# Continue with present/capture/freeze/reveal through the existing M8 functions.
# Saving the next state appends another snapshot; the earlier ref still resolves.
```

`store.list_refs(participant_id="P01", kind="m8.tutor-session.v1")` discovers
available snapshots when the locator is unavailable. Results are deterministic
identity order, not a claim about the newest or canonical learner state. Choosing
a current session remains the application's responsibility.

Generic upstream records can be stored as JSON without changing their native
identity or fingerprints:

```python
source_ref = store.put(
    kind="upstream.position-analysis.v1",
    artifact_id=analysis.result_fingerprint,
    participant_id="P01",
    payload=analysis.to_dict(),
)
ref = save_tutor_session(
    store, session, prompts=planned_prompts, dependencies=(source_ref,),
)
```

This declares a storage dependency, not a new domain qualification. Supply the
required upstream closure explicitly when archival completeness is required.

## Failure handling

Never catch an integrity error and silently continue with a partial session.
`MissingDependencyError` requires restoration of the exact referenced input.
`ArtifactConflictError` requires reconciliation, not overwrite. `IntegrityError`
requires retaining/quarantining the original and investigating the mismatch.
`UnsupportedSchemaError` requires an explicit compatible reader or migration;
opening a future-version database does not downgrade it. Other database failures
surface as `StorageError` and do not establish that a write succeeded.

Keep the local database private: responses and explanation text are unencrypted.
Use a consistent SQLite backup or copy only while no writer is active; copying a
live database without its transaction state is not a verified backup procedure.
The tests cover round trips across all eight M8 states, fresh-process completion
recovery, fresh-process continuation with reveal gating, concurrent idempotent
writes, and an uncommitted subprocess exit. They are not a hardware power-loss
qualification or an authenticated audit-log system.
