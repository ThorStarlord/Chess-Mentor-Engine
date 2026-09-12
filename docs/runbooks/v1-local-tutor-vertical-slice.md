# V1 Local Tutor Vertical Slice

## Integration status

**Status:** INTEGRATED / CURRENT-MAIN AUTHORITY  
**PR:** #94  
**Final candidate head:** `9867105509e0f243a7823066d626abe1cad40148`  
**Merge commit:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`  
**PR CI run:** `34642933193`

Exact-candidate qualification:

```text
948 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish integration: 8 passed
```

## Purpose

This package makes the already-qualified learner/tutor path usable through one local operator surface without creating a new source of chess, learner, pedagogy, outcome, or mastery authority.

The supported composition is:

```text
exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 transfer plan(s)
        |
        v
M45 participant-scoped mentor queue
        |
        v
explicit operator selection + capture consent
        |
        v
existing M23 authorization/persistence bridge
        |
        v
exact persisted M8 tutor checkpoint
        |
        v
M46 bounded next-action proposal
        |
        v
existing cme tutor commands remain M8 execution/exposure authority
```

The installed command is `cme-local-tutor`. It is intentionally separate from the legacy `cme` parser, matching the repository's existing operator-command pattern.

## Authority ceiling

The local workflow records:

```text
orchestration_authority = composition_only
learner_effect = not_established
mastery = not_established
```

Therefore:

```text
M45 rank one != learner diagnosis
M45 rank one != implicit user consent
M46 proposal != M8 execution
assisted response != baseline unassisted evidence
M42 transfer plan != M10 outcome evidence
successful transfer != mastery
```

## Inputs

`cme-local-tutor` consumes exact structural JSON for already-qualified artifacts:

- an M18 diagnostic-analysis queue, normally produced by `cme diagnose`;
- an M44 `LearnerProgressView`;
- zero or more M42 `TransferRetestPlan` records;
- the exact PGN used for the M18 queue when starting a review;
- the existing M5 capture protocol and prompt definitions required by M23/M8.

Structural M44/M42 JSON uses the repository's strict dataclass codec shape. It is not model-authored free-form JSON.

## Start a bounded review

```bash
cme-local-tutor start game.pgn \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --protocol-json capture-protocol.json \
  --prompts-json prompts.json \
  --selection-decision selected \
  --capture-consent granted \
  --recorded-at 2026-09-11T18:00:00-03:00 \
  --created-at 2026-09-11T18:01:00-03:00 \
  --create-db
```

Optional exact M42 plans are repeatable with `--transfer-plan-json`.

The command first constructs the M45 queue. Rank one is only a review proposal. `--selection-decision selected` and `--capture-consent granted` remain separate explicit operator decisions before M23 may create a persisted M8 session.

A newly selected M8 session can only produce the M46 action `CONTINUE_BASELINE_CAPTURE`. No adaptive hint or objective reveal is exposed before the existing M8 baseline-freeze boundary.

## Continue through existing M8 transitions

Use the exact session artifact with the established `cme tutor` workflow:

```bash
cme tutor status --db ./mentor.sqlite3 --participant P01 '<artifact-id>'
cme tutor present-position ...
cme tutor present-stage ...
cme tutor respond ...
cme tutor freeze ...
```

After a persisted M8 transition, request the next bounded proposal:

```bash
cme-local-tutor next \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-11T18:10:00-03:00 \
  '<current-session-artifact-id>'
```

The command replay-verifies the exact M8 checkpoint and rebuilds the M45/M46 composition. Depending on exact state, the result may continue baseline capture, propose bounded adaptive tutoring, expose blocking uncertainty, propose post-reveal reflection, or report completion.

When the exact M44 action is near/far transfer, provide the exact current M42 plan. M46 uses it only when participant, hypothesis revision, next-session plan, and selected position all match the active M8 session. Actual transfer outcome remains M10 authority.

## Fail-closed behavior

The package rejects before starting a new persisted review when, among other cases:

- M18 queue integrity is invalid;
- M44 identity/fingerprint is stale or tampered;
- participant scope differs across M18/M44/operator context;
- the M45 item cannot resolve one exact M44 hypothesis without explicit `--hypothesis-id`;
- multiple exact M42 plans match the same active review target;
- explicit candidate selection or evidence-capture consent is declined.

For an existing checkpoint it also rejects if the active M8 position is not present exactly once in the rebuilt M45 queue or the requested session artifact is outside participant scope.

## Qualification

Focused package suites:

```bash
python -m pytest tests/test_v1_local_tutor_workflow.py -rs
python -m pytest tests/test_v1_local_tutor_authority_edges.py -rs
```

Relevant regression chain:

```bash
python -m pytest \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py \
  tests/test_m45_batch_mentor_queue.py \
  tests/test_m46_adaptive_socratic_tutor.py \
  tests/test_v1_local_tutor_authority_edges.py \
  tests/test_v1_local_tutor_workflow.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

## Deferred external authority

This local slice does not establish production browser/accessibility/usability quality, production authentication/privacy/security, hosted-provider operations, empirical tutoring efficacy, intervention-caused improvement, or mastery. Those remain outside the repository-only/hermetic claim made by this package.
