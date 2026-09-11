# Chess Mentor Engine — Milestone Handoff

**Handoff scope:** completed M29–M31 milestone / Packages 1–3  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Milestone start baseline:** `7563d5bb53cb44dc2a1242019d05e2681bbd453c`  
**Post-feature baseline:** M31 merge `6bd84881204e543f4cfe8906aa7cc15e894fc794`  
**Prepared:** 2026-09-10  

This is the durable handoff for the milestone that removed manual M25-bundle assembly from persisted review rendering, added participant-scoped review navigation/export, and qualified a hermetic privacy/manual-retry preflight around the existing M24/M26 execution seam.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md) as the moving implementation boundary, this file as the completed M29–M31 milestone summary, and [`docs/runbooks/m29-m31-milestone-runbook.md`](docs/runbooks/m29-m31-milestone-runbook.md) for restart and qualification commands.

## Milestone outcome

All three queued packages are implemented, qualified on exact final candidate heads, and merged into `main`.

```text
Package 1 / M29  Persisted Review -> Reference Surface Bridge             MERGED - PR #65
Package 2 / M30  Participant-Scoped Review Package & Navigation           MERGED - PR #66
Package 3 / M31  Hermetic Execution-Envelope Privacy & Retry Preflight    MERGED - PR #67
```

The completed local chain now extends through:

```text
replay-verified persisted M8 state=compared
-> M26 reviewed-coaching run
   -> M16 deterministic grounding
   -> optional M19/M20 through M24-compatible adapters
   -> persisted M25 coach-review read model
-> M27 mechanically verified execution ledger
-> M29 persisted M26/M25 selector -> M27 verification -> M28 renderer
-> M30 participant-scoped review navigation / content-addressed package / export

optional supplied M24 attempt history
-> M31 synthetic-canary privacy scan + manual retry-history validation
   -> exact final-attempt binding to the M24 execution persisted by M26
   -> content-addressed summary-safe M31 report
```

M29–M31 add no new chess-fact, learner-inference, model-semantic, evaluator-truth, pedagogy, production-provider, or production-UI authority.

## Package 1 — M29 Persisted Review -> Reference Surface Bridge

**PR:** #65  
**Final candidate head:** `903b8543aace2a851786f1b8e4022084b60bb866`  
**Merge commit:** `34ef3cf458c9a4c7e2cf4a9c44aeaa54225db4e3`  
**CI run:** `34542884614`

Delivered:

- installed repository-local `cme-persisted-coach-review-reference` command;
- exact participant-scoped selection by one persisted M26 run id or one persisted M25 review id;
- exact immutable M26 <-> M25 relationship resolution through the local artifact store;
- required M27 single-run mechanical verification before M28 rendering;
- direct rendering of the persisted M25 payload through the existing M28 renderer, removing hand-assembled `m25-bundle.json` from the persisted operator path;
- preservation of M28 non-overwrite behavior and rejection of unsafe output extensions before new ledger persistence;
- deterministic equality between in-memory and persisted M25 rendering by ordering M28 source fingerprints through the explicit M25 contract rather than incidental dictionary insertion order;
- negative coverage for participant scope, detached reviews, forged M25 projection drift, unsafe output, overwrite, and missing databases.

Qualification evidence:

```text
754 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

M29 establishes only persisted-chain resolution, M27 mechanical verification, and deterministic M28 rendering. It does not establish new engine truth, model quality, evaluator truth, browser quality, or production readiness.

See [`docs/runbooks/m29-persisted-review-reference-bridge.md`](docs/runbooks/m29-persisted-review-reference-bridge.md).

## Package 2 — M30 Participant-Scoped Review Package & Navigation

**PR:** #66  
**Final candidate head:** `556763d42c9ec5e0bad1abbfeb5dbd861f66e21a`  
**Merge commit:** `8d3134c27479e2bf5649f66d5e2fcfe1f1dfca35`  
**CI run:** `34544479383`

Delivered:

- installed repository-local `cme-participant-review` command with `list`, `show`, and `export`;
- deterministic participant-scoped navigation across M26 runs, M25 reviews, M27 ledgers, M30 package manifests, and M28 reference-surface identities;
- content-addressed `m30.participant-review-package.v1` manifests with exact M26/M25/M27 references, artifact digests, exact M25 `source_fingerprints`, M28 surface identity/fingerprint, and bounded M27 execution summary;
- summary indexes that do not copy source payloads, model-rendered coaching, evaluator rationales, participant-response content, or HTML;
- explicit `show --include-content` requirement before exact persisted payload or M28 HTML is emitted;
- atomic non-overwriting export of `manifest.json` + `review.html` into a new directory;
- reuse of M29/M27 verification rather than creation of a second review/evidence authority;
- negative coverage for wrong participant, invalid navigation kind, content-disclosure boundaries, missing DB, export overwrite, package/source drift, and deterministic repeated construction.

Qualification evidence:

```text
762 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

M30 establishes repository-local participant-scoped navigation and export only. Participant scoping is not hosted authentication, and summary-safe output is not external privacy/security approval.

See [`docs/runbooks/m30-participant-review-package-navigation.md`](docs/runbooks/m30-participant-review-package-navigation.md).

## Package 3 — M31 Hermetic Execution-Envelope Privacy & Retry Preflight

**PR:** #67  
**Final candidate head:** `9a82f72af93215756818b991bd3d922144cf6ca2`  
**Merge commit:** `6bd84881204e543f4cfe8906aa7cc15e894fc794`  
**CI run:** `34546266117`

Delivered:

- content-addressed `m31.execution-envelope-privacy-retry-preflight.v1` report;
- synthetic-canary validation restricted to `CME_TEST_CANARY_*` markers, with no live-secret support;
- scan of the persisted M26 dependency closure before M27 construction and the combined M26/M27 closure after mechanical verification;
- deterministic validation of already-supplied manual retry histories without executing retries;
- hard preservation of M24 `automatic_retry=false`;
- later-attempt permission only after M24-classified `timeout` or `transient` failure with `retryable=true`;
- contiguous attempt numbering, stable endpoint/request identity and timeout, bounded `max_attempts`, and exact final-attempt equality with the M24 execution persisted by M26;
- summary-safe persisted evidence containing references, counts, statuses, and bounded attempt summaries but no canary values, failure details, request payloads, model prose, evaluator rationales, or participant responses;
- negative coverage for forged automatic retry, retry after permanent failure, non-contiguous/budget-exceeding histories, missing role histories, canary leakage in attempt failure detail or persisted content, non-synthetic secret-like input, and cross-participant run selection.

Qualification evidence:

```text
774 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

M31 validates a supplied hermetic history; it never executes a retry, selects a vendor, accepts production credentials, or establishes operational retry/backoff/privacy/security correctness.

See [`docs/runbooks/m31-execution-envelope-privacy-retry-preflight.md`](docs/runbooks/m31-execution-envelope-privacy-retry-preflight.md).

## Current operational surfaces

Installed commands now include:

```text
cme
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

Principal persisted review path:

```text
cme diagnose ...
-> cme-candidate-tutor ...
-> cme tutor present-position / present-stage / respond / freeze / reveal / compare ...
-> cme-reviewed-coaching '<session-id>:<snapshot-fingerprint>' ...
-> cme-reviewed-coaching-ledger ...
-> cme-persisted-coach-review-reference ...
-> cme-participant-review list/show/export ...
```

M31 is intentionally a Python API / hermetic validation surface, not a production execution CLI.

Exact commands and focused qualification suites are consolidated in the M29–M31 milestone runbook.

## Verified evidence and remaining gates

### Software qualification

No repository-only or hermetic software gate from the M29–M31 queue remains pending. Every package was merged only after its final candidate head passed the full repository pytest/Ruff gate and independent Stockfish job. Intermediate candidates with test/style defects were not merged; repairs were re-qualified on fresh exact heads.

### Human QA / external authority still pending

The following remain intentionally outside the completed milestone:

- end-user review of diagnostic candidate selection and capture-consent disclosure, wording, timing, and pre-reveal contamination boundaries;
- real browser/device visual QA, screen-reader testing, accessibility conformance review, localization, interaction design, and usability testing for M28/M30 or successors;
- production model/provider and evaluator-provider selection;
- production credentials, secret injection, privacy/security approval, data-transmission policy, and retention policy;
- live provider transport behavior, timeout/retry/backoff/rate-limit policy, latency SLOs, cost budgets, billing controls, and incident handling;
- semantic correctness, safety, and pedagogical quality of arbitrary model-authored coaching;
- completeness/correctness of a production evaluator beyond the bounded M20 contract;
- empirical tutoring efficacy, transfer, intervention-caused improvement, causal learner diagnosis, permanent-weakness claims, or automatic mastery;
- hosted authentication/authorization, multi-user tenancy, production persistence, observability operations, and deployment qualification.

These remain explicit human/external authority gates. M29–M31 do not silently claim them.

## Recommended next priorities

The M29–M31 queue is complete. A future milestone should begin with a fresh live-main audit before promoting any suggestion below into an approved package queue.

1. **Persisted review-delivery fidelity contract.** Define a stable machine-readable consumer bundle over M30/M28 and qualify objective-vs-model authority labels, White-vs-decision-mover semantics, mate/bound/partial/unavailable states, ordering, and exact source fingerprints across the full evidence-regime matrix. Keep this repository-only and do not claim production UI quality.
2. **Deterministic mentor-feedback trace surface.** Add a compact provenance index that makes every deterministic M16 feedback component traceable to exact M15/M6/M7 sources while keeping M19 prose and M20 judgments explicitly separate. Qualify omission, drift, and tamper cases without attempting free-form semantic truth evaluation.
3. **Hermetic execution recovery reconciliation.** Extend M31-style validation with content-addressed dry-run recovery/resumption plans for multi-attempt fake-adapter histories, idempotency, and partial-failure reconciliation. Preserve external ownership of real retry/backoff/vendor policy and never execute live retries.

These are recommendations, not an approved work-package queue.

## Restart instructions for a future engineer or chat session

1. Read this `STATUS.md`.
2. Read `CONTEXT.md`, `docs/product/repository-build-status.md`, and `docs/runbooks/m29-m31-milestone-runbook.md`.
3. Confirm live `main` and recent commits before relying on hashes in this handoff.
4. Run the focused M29–M31 suites, then the full repository gate and independent Stockfish witness.
5. Preserve these boundaries:

```text
M27 mechanical verification != semantic truth, retry authority, or privacy approval
M28 static reference rendering != production UI/accessibility/usability approval
M29 persisted bridge != new review or chess-evidence authority
M30 participant-scoped navigation != authentication or privacy approval
M31 manual retry-history validation != retry execution or retry authority
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
participant selection != evidence-capture consent
```

6. Do not silently turn reviewed coaching into an M8 state transition; `cme tutor explain` remains explicit.
7. Do not expose M19 prose or M20 judgments as if they were M15 objective evidence.
8. Keep sensitive model/evaluator/participant content out of summary indexes unless exact content is explicitly requested from its authoritative artifact.
9. Never provide live credentials to M31; it accepts only synthetic canaries.
10. Do not treat a skipped Stockfish suite as an independent-engine pass.
11. Before a new milestone, reconcile live `main` and propose a fresh bounded package queue rather than automatically implementing the recommendations above.

## Key references

- `CONTEXT.md`
- `docs/product/repository-build-status.md`
- `docs/runbooks/m29-m31-milestone-runbook.md`
- `docs/runbooks/m29-persisted-review-reference-bridge.md`
- `docs/runbooks/m30-participant-review-package-navigation.md`
- `docs/runbooks/m31-execution-envelope-privacy-retry-preflight.md`
- PR #65 — M29
- PR #66 — M30
- PR #67 — M31