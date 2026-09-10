# M30 — Participant-Scoped Review Package & Navigation

M30 adds repository-local navigation and export tooling over the qualified reviewed-coaching chain without turning summary indexes into a second source of review content.

## Boundary

M30 is REPOSITORY_ONLY / HERMETIC_VALIDATION work.

It does not use production credentials, call live providers, deploy infrastructure, advance tutor state, create objective chess facts, establish model-output truth, claim pedagogical quality, or qualify a production UI.

The chain remains:

```text
M26 persisted reviewed-coaching run
  -> exact persisted M25 coach-review dependency
  -> M27 mechanically verified one-run ledger
  -> M28 deterministic local reference surface
  -> M30 content-addressed participant review package manifest
```

M30 uses M29 to close the persisted M26/M25 -> M27 -> M28 bridge before creating a package manifest.

## Command

```bash
cme-participant-review list \
  --db artifacts.sqlite3 \
  --participant P01
```

`list` emits participant-scoped navigation metadata only. It contains exact artifact references, package references, M28 surface identities, and counts. It does not copy M26/M25/M27 payloads, model-rendered content, evaluator rationales, participant-response content, or HTML.

Show one item without content:

```bash
cme-participant-review show \
  --db artifacts.sqlite3 \
  --participant P01 \
  --kind review \
  --id coach_review_...
```

Exact persisted content requires an explicit flag:

```bash
cme-participant-review show \
  --db artifacts.sqlite3 \
  --participant P01 \
  --kind review \
  --id coach_review_... \
  --include-content
```

Supported `--kind` values are:

```text
run      M26 persisted reviewed-coaching artifact
review   M25 coach-review artifact
ledger   M27 reviewed-coaching execution ledger
package  M30 participant review package manifest
surface  M28 reference surface represented by an M30 package id
```

For `surface`, `--include-content` explicitly re-renders and returns the qualified M28 HTML after the M30 package and source chain are rechecked.

Export a new package from an exact run or review:

```bash
cme-participant-review export \
  --db artifacts.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_... \
  --output-dir review-package
```

or:

```bash
cme-participant-review export \
  --db artifacts.sqlite3 \
  --participant P01 \
  --review-id coach_review_... \
  --output-dir review-package
```

An existing M30 package can be exported again to a different new directory:

```bash
cme-participant-review export \
  --db artifacts.sqlite3 \
  --participant P01 \
  --package-id participant_review_package_... \
  --output-dir another-review-package
```

The output directory must not already exist. Export is staged in a temporary sibling directory and renamed only after both files are written:

```text
manifest.json
review.html
```

The manifest is content-addressed by `package_id` and `fingerprint` and persists as `m30.participant-review-package.v1` with exact dependencies on the selected M26 run, M25 review, and one-run M27 ledger.

## Manifest contract

The M30 manifest retains only summary-safe navigation data:

- exact M26, M25, and M27 artifact references;
- exact artifact digests;
- the M25 read-model fingerprint;
- the exact M25 `source_fingerprints` map;
- M28 surface id and fingerprint;
- bounded M27 execution counts;
- privacy and authority-boundary declarations.

It intentionally does not retain:

- M26/M25/M27 source payloads;
- model-rendered coaching text;
- evaluator rationales;
- participant-response content;
- generated HTML.

Those are returned only through explicit `show --include-content` or `export` operations from their authoritative persisted/derived sources.

## Qualification

Focused M30 tests:

```bash
python -m pytest tests/test_m30_participant_review_package_navigation.py -rs
```

Principal reviewed-coaching regression:

```bash
python -m pytest \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py \
  tests/test_m30_participant_review_package_navigation.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Repository CI additionally runs the independent Stockfish witness on the exact candidate head.

## Negative / rejection coverage

M30 qualification covers:

- wrong-participant lookups without cross-participant disclosure;
- invalid navigation kinds;
- exact-content withholding unless explicitly requested;
- model/evaluator/participant content absence from manifests and list indexes;
- existing export-directory refusal before new M30 package persistence;
- missing artifact database rejection;
- exact persisted package reload and source dependency verification;
- deterministic repeated package creation and surface reconstruction.

## Claim ceiling

A passing M30 package establishes deterministic participant-scoped repository navigation, a content-addressed summary-safe manifest, and bounded local export over the already-qualified M26–M29 chain.

It does not establish production authentication/authorization, privacy approval, security approval, browser/device/accessibility/usability correctness, provider readiness, semantic model quality, evaluator truth, tutoring efficacy, deployment readiness, or operational readiness.
