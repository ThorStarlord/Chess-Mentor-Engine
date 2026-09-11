# M29–M31 Milestone Runbook

This runbook is the restart and qualification guide for the completed M29–M31 milestone.

The milestone is repository-local / hermetic. It closes the persisted review-to-reference seam, adds participant-scoped review navigation/export, and adds synthetic-canary + manual-retry preflight around the existing M24/M26 execution envelope. It does not establish production provider, credential, privacy/security, retry-policy, browser/UI, or tutoring-efficacy authority.

## Completed milestone chain

```text
persisted M26 reviewed-coaching run
  -> exact persisted M25 coach-review read model
  -> M27 mechanically verified one-run execution ledger
  -> M29 persisted review -> M28 reference-surface bridge
  -> M30 participant-scoped review package / navigation / export

optional M24 provider/evaluator execution history
  -> M26 persisted successful execution selection
  -> M27 mechanical verification
  -> M31 synthetic-canary privacy + manual-retry-history preflight
```

M29–M31 preserve all earlier authority boundaries. In particular:

```text
M15 evaluation presentation != new chess truth
M16 deterministic grounding != M19 model prose
M20 evaluator judgment != objective truth
M27 mechanically_verified != semantic correctness
M28 reference HTML != production UI approval
M30 navigation/export != authentication or privacy approval
M31 retry-history validation != retry execution or retry authority
```

## Package 1 / M29 — persisted review to reference surface

Run from a persisted M26 run:

```bash
cme-persisted-coach-review-reference \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_... \
  --output ./review.html
```

Or select the exact persisted M25 review:

```bash
cme-persisted-coach-review-reference \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --review-id coach_review_... \
  --output ./review.html
```

Exactly one selector is required. The output must be a new `.html` or `.htm` path. M29 resolves the exact M26/M25 relationship, builds/verifies the single-run M27 ledger, then renders the already-persisted M25 payload through the existing M28 renderer. It does not require a hand-assembled M25 bundle.

Focused qualification:

```bash
python -m pytest tests/test_m29_persisted_review_reference_bridge.py -rs
```

See `docs/runbooks/m29-persisted-review-reference-bridge.md`.

## Package 2 / M30 — participant-scoped review package and navigation

List participant-scoped review navigation metadata:

```bash
cme-participant-review list \
  --db ./mentor.sqlite3 \
  --participant P01
```

Show one review item without copying its persisted payload:

```bash
cme-participant-review show \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --kind review \
  --id coach_review_...
```

Explicitly request exact content only when needed:

```bash
cme-participant-review show \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --kind review \
  --id coach_review_... \
  --include-content
```

Supported kinds are `run`, `review`, `ledger`, `package`, and `surface`.

Export a new review package from an exact M26 run:

```bash
cme-participant-review export \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_... \
  --output-dir ./review-package
```

Equivalent selectors are `--review-id coach_review_...` or `--package-id participant_review_package_...`.

The output directory must not already exist. A successful export contains:

```text
manifest.json
review.html
```

The persisted `m30.participant-review-package.v1` manifest is content-addressed and summary-safe: it stores exact source references/fingerprints and M28 surface identity, but it does not copy model-rendered coaching, evaluator rationales, participant response content, or HTML into summary navigation.

Focused qualification:

```bash
python -m pytest tests/test_m30_participant_review_package_navigation.py -rs
```

See `docs/runbooks/m30-participant-review-package-navigation.md`.

## Package 3 / M31 — execution-envelope privacy and retry preflight

M31 is a Python API / hermetic qualification surface, not a live execution CLI.

Representative use:

```python
from chess_mentor_engine.execution_envelope_preflight import (
    build_execution_envelope_preflight,
)

result = build_execution_envelope_preflight(
    store=store,
    participant_id="P01",
    run_artifact_id="reviewed_coaching_run_...",
    attempt_histories={
        "model_coach_provider": provider_attempt_records,
        "model_coaching_evaluator": evaluator_attempt_records,
    },
    synthetic_canaries=("CME_TEST_CANARY_example1234",),
    max_attempts=3,
)
```

Only synthetic markers beginning with `CME_TEST_CANARY_` are accepted. Do not supply live credentials to this API.

M31 validates an already-supplied manual retry history. It never executes retries. A later attempt is valid only after an M24 `timeout` or `transient` failure marked `retryable=true`; all attempts must preserve endpoint/request identity and timeout; `automatic_retry` must remain `false`; and the final successful attempt must exactly match the M24 execution persisted by M26.

Before writing an M31 report, the preflight scans the M26 dependency closure and then the combined M26/M27 closure for supplied synthetic canaries. The persisted M31 report stores counts, statuses, references, and bounded attempt summaries, never canary values or failure details.

Focused qualification:

```bash
python -m pytest tests/test_m31_execution_envelope_preflight.py -rs
```

See `docs/runbooks/m31-execution-envelope-privacy-retry-preflight.md`.

## Principal M29–M31 regression

```bash
python -m pytest \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py \
  tests/test_m30_participant_review_package_navigation.py \
  tests/test_m31_execution_envelope_preflight.py -rs
```

## Full repository merge gate

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not an independent-engine pass. Pull-request CI on the exact candidate head remains the merge authority. No standalone static Python type checker is configured.

## Final milestone qualification evidence

| Package | PR | Final qualified head | Merge commit | CI run | Result |
| --- | --- | --- | --- | --- | --- |
| M29 | #65 | `903b8543aace2a851786f1b8e4022084b60bb866` | `34ef3cf458c9a4c7e2cf4a9c44aeaa54225db4e3` | `34542884614` | 754 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M30 | #66 | `556763d42c9ec5e0bad1abbfeb5dbd861f66e21a` | `8d3134c27479e2bf5649f66d5e2fcfe1f1dfca35` | `34544479383` | 762 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M31 | #67 | `9a82f72af93215756818b991bd3d922144cf6ca2` | `6bd84881204e543f4cfe8906aa7cc15e894fc794` | `34546266117` | 774 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |

Intermediate candidate failures were not merged. Final candidates were re-qualified after repair.

## Pending human / external gates

The milestone does not resolve these external-authority gates:

- production LLM/evaluator provider selection;
- live credentials/secrets handling, privacy/security review, data-transmission and retention policy;
- real transport timeouts, retry/backoff/rate-limit policy, latency/cost/billing controls, and incident handling;
- semantic correctness, safety, and pedagogical quality of arbitrary model-authored coaching;
- production evaluator completeness/correctness beyond the bounded M20 contract;
- real browser/device/screen-reader/accessibility/localization/interaction/usability QA;
- end-user review of disclosure, consent, diagnostic-candidate selection, and pre-reveal contamination boundaries;
- hosted authentication/authorization, multi-user tenancy, production persistence, observability, and deployment;
- empirical tutoring efficacy, transfer, causal diagnosis, or mastery claims.

## Recommended next milestone directions

These are recommendations only. Begin the next session with a fresh live-main audit before turning any of them into an approved work-package queue.

1. **Persisted review-delivery fidelity contract.** Define a stable machine-readable consumer bundle over M30/M28 and qualify objective-vs-model authority labels, White-vs-decision-mover semantics, mate/bound/partial/unavailable states, ordering, and source fingerprints across the full evidence-regime matrix. Keep this repository-only and do not claim production UI quality.
2. **Deterministic mentor-feedback trace surface.** Add a compact provenance index that makes every deterministic M16 feedback component traceable to its exact M15/M6/M7 source while keeping M19 prose and M20 judgments visibly separate. Qualify omission/drift/tamper cases without attempting free-form semantic truth evaluation.
3. **Hermetic execution recovery reconciliation.** Extend M31-style validation with content-addressed dry-run recovery/resumption plans for multi-attempt fake-adapter histories, idempotency, and partial-failure reconciliation. Preserve explicit external ownership of real retry/backoff/vendor policy and never execute live retries.

## Restart checklist

1. Read `STATUS.md`.
2. Read `CONTEXT.md` and `docs/product/repository-build-status.md`.
3. Read this runbook plus the individual M29, M30, and M31 runbooks.
4. Confirm live `main` and recent commits before relying on handoff hashes.
5. Run focused M29–M31 tests, then the full repository gate and independent Stockfish witness.
6. Preserve participant scoping as an integrity boundary only; it is not hosted authentication.
7. Preserve `automatic_retry=false`; M31 validates histories but does not authorize or execute retries.
8. Do not move model prose/evaluator rationale into summary indexes or objective-evidence sections.
9. Do not treat M28/M30 local surfaces as production UI/accessibility/usability approval.
10. Audit live state and create a fresh bounded work-package queue before implementation.