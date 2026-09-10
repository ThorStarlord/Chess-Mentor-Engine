# M29 — Persisted Reviewed-Coaching to Reference-Surface Bridge

M29 closes the local operator seam between persisted M26/M25 reviewed-coaching
artifacts and the deterministic M28 HTML reference surface.

It does not add new chess, learner, model, evaluator, or pedagogical authority. It
resolves already-persisted artifacts, requires M27 mechanical verification for the
selected M26 run, and renders the exact persisted M25 read-model payload through the
existing M28 renderer.

## Boundary

```text
participant-scoped local artifact DB
        ↓
exact M26 run id OR exact persisted M25 review id
        ↓
resolve exact M26 <-> M25 immutable dependency
        ↓
M27 single-run mechanical verification
        ↓
exact persisted M25 payload
        ↓
M28 deterministic read-model renderer
        ↓
new local .html/.htm file
```

The installed command is:

```bash
cme-persisted-coach-review-reference \
  --db path/to/artifacts.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_... \
  --output path/to/review.html
```

The equivalent M25-first selector is:

```bash
cme-persisted-coach-review-reference \
  --db path/to/artifacts.sqlite3 \
  --participant P01 \
  --review-id coach_review_... \
  --output path/to/review.html
```

Exactly one selector is required. The output path must be new and must end in
`.html` or `.htm`.

## Resolution and verification

When an M26 run id is supplied, M29 resolves its exact persisted M25 dependency.
When an M25 review id is supplied, M29 requires that exact review to be backed by
exactly one participant-scoped persisted M26 run.

M29 then invokes the existing M27 verifier for only that M26 run. M27 remains the
authority for mechanical identity, dependency closure, M25 source-fingerprint
preservation, M18/M21/M8/M16 lineage, optional M19/M20 preservation, and M24
request/response binding.

Only after M27 returns `mechanically_verified` for the exact selected run/review pair
does M29 load the persisted M25 payload and pass it to M28's direct read-model
renderer. M28 independently checks M25 content identity and separation-contract
invariants before rendering.

The M27 ledger is content-addressed and persisted using the already-qualified M27
contract. Repeated M29 execution over the same run therefore reuses the same ledger
identity rather than creating divergent verification state.

## Non-destructive behavior

M29 validates the requested output path before invoking the bridge. Existing output
files and unsafe output extensions are rejected before M27 can persist a ledger.

M29 performs no engine execution, model/evaluator call, network request, credential
lookup, browser automation, deployment, destructive migration, or tutor-state
transition.

## Qualification

Focused M29 qualification:

```bash
python -m pytest tests/test_m29_persisted_review_reference_bridge.py -rs
```

Principal persisted-review regression:

```bash
python -m pytest \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py -rs
```

Full repository gate remains:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The repository CI also runs the independent Stockfish integration witness. A skipped
Stockfish suite is not an independent-engine pass.

## Negative and rejection coverage

M29 explicitly qualifies rejection for:

- missing or cross-participant M26/M25 selectors;
- supplying both Python-level selectors at once;
- persisted M25 reviews that are not backed by exactly one M26 run;
- forged M25 projection content that M27 detects against M16 lineage;
- existing output paths;
- unsafe output extensions;
- missing local artifact databases.

The hermetic model/evaluator path is also exercised with the existing fake M24
adapters, proving that persisted M19/M20 content is carried into M28 only after M27
mechanical verification while M20's truth-status ceiling remains visible.

## Claim ceiling

A passing M29 bridge establishes only that one participant-scoped persisted M26/M25
chain can be mechanically verified through M27 and deterministically rendered through
M28 without a hand-assembled M25 bundle file.

It does **not** establish:

- new or improved engine-evaluation truth;
- semantic correctness, safety, or pedagogical quality of model-authored coaching;
- evaluator truth or completeness;
- production provider, credential, retry, latency, cost, or privacy readiness;
- production browser, accessibility, localization, visual, or usability correctness;
- hosted authentication or multi-user authorization;
- deployment readiness or empirical tutoring efficacy.

M15 remains evaluation-presentation authority, M16 deterministic grounding authority,
M19 model-language provenance, M20 bounded model-output assessment, M25 the
application read-model authority separator, M26 persisted reviewed-coaching
orchestration, M27 mechanical verification, and M28 local reference rendering.
