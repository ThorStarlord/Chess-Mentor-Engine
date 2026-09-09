# M13 — Persistent Tutor Session CLI

## Scope

M13 extends the installed `cme` command from read-only evidence inspection to a
controlled write surface for the already-qualified M8 tutor state machine.

Every mutation follows the same rule:

```text
exact prior m8.tutor-session.v1 artifact
-> verified storage read
-> typed M8 replay
-> one existing M8 transition
-> replay validation
-> new immutable m8.tutor-session.v1 artifact
```

The prior checkpoint is never overwritten. Stored non-prompt dependencies are
carried forward to each successor checkpoint.

M13 does **not** generate prompts, engine analysis, M6 assessments, M7 hypotheses,
explanations, M11 learner-state changes, or training decisions. Those inputs must
already exist under their owning contracts. M13 only validates, presents, records,
and persists explicitly supplied records and participant responses.

## Start a persisted tutor session

`start` accepts the structural JSON representation of an exact M5
`PlayerDecisionContext`, M5 `CaptureProtocol`, and all planned `PromptDefinition`
records. The JSON shape is the same strict dataclass structure used by the storage
codec; unknown fields, invalid literals, and wrong primitive types are rejected.

```bash
cme tutor start \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --context-json ./context.json \
  --protocol-json ./protocol.json \
  --prompts-json ./prompts.json \
  --created-at 2026-09-09T10:00:00-03:00 \
  --create-db
```

A missing database is created only when `--create-db` is explicit. If the database
already exists, the flag is unnecessary. `--dependencies-json` may contain an array
of exact stored `ArtifactRef` records; missing or cross-participant dependencies
cause the atomic save to fail.

## Inspect a checkpoint

```bash
cme tutor status \
  --db ./mentor.sqlite3 \
  --participant P01 \
  'tutor_session_...:snapshot_fingerprint...'
```

`status` resolves the artifact only inside the declared participant scope, verifies
all storage dependencies, decodes trusted schemas, and replays the M8 event history
before reporting `verified_replay: true`.

## Advance one transition

All transition commands take the exact previous session artifact ID and create a
new checkpoint. The returned JSON includes both `previous_ref` and the new `ref`.

```bash
cme tutor present-position --db ./mentor.sqlite3 --participant P01 SESSION \
  --packet-json ./position-context.json \
  --shown-at 2026-09-09T10:01:00-03:00

cme tutor present-stage --db ./mentor.sqlite3 --participant P01 SESSION \
  --stage-id A1 \
  --shown-at 2026-09-09T10:02:00-03:00

cme tutor respond --db ./mentor.sqlite3 --participant P01 SESSION \
  --stage-id A1 \
  --response 'I would play e4.' \
  --structured-json ./participant-response.json \
  --submitted-at 2026-09-09T10:03:00-03:00

cme tutor freeze --db ./mentor.sqlite3 --participant P01 SESSION \
  --stage-id A1 \
  --frozen-at 2026-09-09T10:04:00-03:00
```

Repeat the protocol-bound pre-reveal stages until M8 reaches `frozen`. The native
M8 gate rejects objective reveal before every required pre-reveal response is
frozen.

## Post-freeze evidence and explanation

`reveal` consumes a strict JSON object with exactly these keys:

```json
{
  "rendered_content": "Explicit objective evidence text",
  "position_analysis_refs": [],
  "decision_comparison_ref": null,
  "selection_signal_refs": []
}
```

The underlying M5/M8 contract still requires actual objective evidence references;
the empty example above only documents the JSON shape.

```bash
cme tutor reveal --db ./mentor.sqlite3 --participant P01 SESSION \
  --bundle-json ./objective-reveal.json \
  --revealed-at 2026-09-09T10:08:00-03:00

cme tutor compare --db ./mentor.sqlite3 --participant P01 SESSION \
  --bundle-json ./m6-comparison.json \
  --recorded-at 2026-09-09T10:11:00-03:00
```

The comparison bundle must contain exactly `reasoning_context`, `assessment`, and
`assertions`, using the existing M6 structural records. M13 never derives that
assessment itself.

Optional complete active-current M7 context can then be attached:

```bash
cme tutor attach-hypothesis --db ./mentor.sqlite3 --participant P01 SESSION \
  --bundle-json ./m7-context.json \
  --attached-at 2026-09-09T10:12:00-03:00
```

The bundle contains exactly `ledger_snapshot` and `active_revisions`. Existing M8
validation rejects cherry-picked, stale, or mismatched active context.

Explanation text is explicit input and requires explicit M8 authorship provenance:

```bash
cme tutor explain --db ./mentor.sqlite3 --participant P01 SESSION \
  --content-file ./explanation.txt \
  --provenance-json ./explanation-provenance.json \
  --created-at 2026-09-09T10:13:00-03:00

cme tutor complete --db ./mentor.sqlite3 --participant P01 SESSION \
  --completed-at 2026-09-09T10:14:00-03:00
```

## Failure handling

A failed transition produces no successor checkpoint. Do not modify an older SQLite
row or JSON envelope to force progress. Correct the exact upstream identity,
chronology, participant scope, or protocol input and retry from the last verified
checkpoint.

Important fail-closed cases include:

- missing database without explicit creation;
- participant mismatch or cross-scope session lookup;
- corrupted storage or failed replay;
- malformed or schema-drifted JSON records;
- position or prompt identity mismatch;
- stage order violations;
- objective reveal before required freezes;
- mismatched M6 or M7 bundles;
- explanation before comparison;
- completion before explanation.

## Qualification

```bash
python -m pytest tests/test_m13_persistent_tutor_cli.py
python -m pytest tests/test_m8_qualification.py tests/test_tutor_storage.py
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final integration command requires `STOCKFISH_EXECUTABLE`; skipped Stockfish
tests are not an independent engine pass. PR CI remains the merge gate.
