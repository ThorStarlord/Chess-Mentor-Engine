# Chess Mentor Engine — Milestone Handoff

**Handoff scope:** completed M26–M28 milestone / Packages 1–3  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Milestone start baseline:** M25 merge `13db09f7cf4c066c49988875e89760ce204c2515`  
**Post-feature baseline:** M28 merge `4975fd65ba22ac1df6d32cd09512cc7c36c42ce8`  
**Prepared:** 2026-09-10  

This is the durable handoff for the milestone that closed the persisted compared-session to reviewed-coaching seam, added privacy-bounded mechanical execution verification, and made the qualified M25 review model inspectable through a deterministic local HTML reference surface.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md) as the moving implementation boundary, this file as the completed M26–M28 milestone summary, and [`docs/runbooks/m26-m28-milestone-runbook.md`](docs/runbooks/m26-m28-milestone-runbook.md) for restart and qualification commands.

## Milestone outcome

All three queued packages are implemented, qualified on exact candidate heads, and merged into `main`.

```text
Package 1 / M26  Persistent Compared-Session -> Reviewed-Coaching Operator  MERGED - PR #61
Package 2 / M27  Reviewed-Coaching Execution Ledger & Fidelity             MERGED - PR #62
Package 3 / M28  Thin M25 Local Review Reference Surface                   MERGED - PR #63
```

The completed local chain is now:

```text
replay-verified M13/M8 state=compared
-> M26 cme-reviewed-coaching
   -> exact retained M18/M21/M8 lineage verification
   -> exact M3/M4 reconstruction
   -> M15 projection
   -> M16 deterministic grounding
   -> optional M19/M20 through M24-compatible application adapters
   -> M25 authority-separated coach-review read model
   -> atomic M26 persistence
-> M27 cme-reviewed-coaching-ledger
   -> persisted dependency / request-response / identity fidelity verification
   -> privacy-bounded execution ledger
-> M28 cme-coach-review-reference
   -> strict M25 bundle validation
   -> deterministic static semantic HTML reference surface
```

M26 does not advance the persisted M8 tutor session. `cme tutor explain` remains the explicit explanation transition. M27 verifies mechanics rather than semantic truth. M28 is a structural local reference surface rather than a production UI.

## Package 1 — M26 Persistent Compared-Session -> Reviewed-Coaching Operator

**PR:** #61  
**Final candidate head:** `394bf9b22833077c898c4251c0eef3eb1b6fe866`  
**Merge commit:** `3936b53f203b186efdf5f734b2b8ec2a266c41f4`  
**CI run:** `34518649749`

Delivered:

- installed repository-local `cme-reviewed-coaching` command;
- replay verification of an exact persisted M13/M8 `compared` checkpoint;
- exact M8 -> M21 launch -> M21 authorization -> M18 queue lineage recovery;
- reconstruction of retained M3/M4 evidence and deterministic M15/M16 composition;
- M25 read-model assembly and atomic append-only persistence;
- optional Python integration seam for explicit M24-compatible provider/evaluator adapters without giving the CLI production-provider authority;
- content-idempotent repeated invocation;
- fail-closed rejection for wrong tutor state, missing M21 lineage, identity/fingerprint drift, invalid adapter combinations, provider/evaluator failures, and partial-write risk;
- preservation of the source tutor checkpoint at `compared`, with no implicit M8 explanation transition.

Qualification evidence:

```text
718 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

M26 chooses no model/evaluator provider, uses no credentials, performs no live external call, grants no automatic retry, and establishes no semantic or pedagogical truth for model output.

See [`docs/runbooks/m26-persistent-reviewed-coaching-operator.md`](docs/runbooks/m26-persistent-reviewed-coaching-operator.md).

## Package 2 — M27 Reviewed-Coaching Execution Ledger & Fidelity Qualification

**PR:** #62  
**Final candidate head:** `b1699ad16193cb3b5541fa08c2b1b54e526f2040`  
**Merge commit:** `492c1024834e3ae9d942d17941d5b22cc8dbcee7`  
**CI run:** `34520178321`

Delivered:

- installed repository-local `cme-reviewed-coaching-ledger` command;
- content-addressed `m27.reviewed-coaching-execution-ledger.v1` artifact;
- exact M26 -> M25 -> M18/M21/M8/M16/M19/M20/M24 dependency and identity verification;
- M24 request/response binding verification against persisted M19/M20 provenance;
- hard preservation of `automatic_retry = false` and M20 `truth_status = not_established_by_m20_evaluation`;
- stable run ordering and content-idempotent ledger construction;
- privacy-bounded output containing references and transport-neutral execution metadata only, without copying request payloads, model rendered content, evaluator rationales, or participant responses;
- fail-closed rejection for forged M25 projection content, retry-authority promotion, provider-response provenance drift, duplicate/missing run selection, participant-scope drift, and malformed storage inputs.

Qualification evidence:

```text
728 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

`mechanically_verified` means content identity, fingerprint, dependency closure, request/response binding, and M25 projection preservation only. It is not a claim about model quality, evaluator truth, engine universality, provider readiness, privacy approval, or tutoring efficacy.

See [`docs/runbooks/m27-reviewed-coaching-execution-ledger.md`](docs/runbooks/m27-reviewed-coaching-execution-ledger.md).

## Package 3 — M28 Thin M25 Local Review Reference Surface

**PR:** #63  
**Final candidate head:** `cde21c1e426e1e0c8d0edc35ebe0f1d99e10cdee`  
**Merge commit:** `4975fd65ba22ac1df6d32cd09512cc7c36c42ce8`  
**CI run:** `34521780789`

Delivered:

- installed repository-local `cme-coach-review-reference` command;
- deterministic `m28.coach-review-reference-surface.v1` identity;
- strict M25-bundle validation before rendering and direct M25 identity/separation-contract checks;
- static semantic HTML using native landmarks, headings, captions, scoped column headers, source labels, and fingerprints;
- exact preservation of canonical White versus decision-mover score perspectives, bounds, mate representation, exact/partial/bounded/incompatible/unavailable/failure states, and M20 truth-status ceiling;
- explicit authority labels for M15, M18, M21, M8, M16, M19, and M20 layers;
- inert HTML escaping for model/evaluator/source content, with no JavaScript or external assets;
- non-destructive output behavior: existing HTML files are never overwritten;
- deterministic structural snapshot coverage plus all eight M22 evidence regimes and adversarial rejection cases.

Qualification evidence:

```text
746 passed, 8 intentional external-engine skips
Ruff: PASS
Independent Stockfish witness: 8/8 PASS
```

M28 qualifies deterministic local rendering and bounded semantic structure only. It does not establish production visual design, usability, browser/device/screen-reader compatibility, localization, disclosure correctness, or accessibility conformance.

See [`docs/runbooks/m28-coach-review-reference-surface.md`](docs/runbooks/m28-coach-review-reference-surface.md).

## Current operational surfaces

Installed commands now include:

```text
cme
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
```

Principal local operator path:

```text
cme diagnose ...
-> cme-candidate-tutor ...
-> cme tutor present-position / present-stage / respond / freeze / reveal / compare ...
-> cme-reviewed-coaching '<session-id>:<snapshot-fingerprint>' ...
-> cme-reviewed-coaching-ledger ...
-> cme-coach-review <m25-bundle.json>            # optional JSON inspection
-> cme-coach-review-reference <m25-bundle.json> --output review.html
```

The `cme-reviewed-coaching` CLI is deterministic-only and invokes no model provider. The Python `run_persistent_reviewed_coaching(...)` API is the explicit seam for hermetic/application-owned M24-compatible provider/evaluator adapters. M28 currently consumes a strict M25 bundle file rather than loading an M25 artifact directly from the local database.

Exact commands and focused qualification suites are consolidated in the M26–M28 milestone runbook.

## Verified evidence and remaining gates

### Software qualification

No repository-only or hermetic software gate from the M26–M28 queue remains pending. Each package was merged only after its final repaired candidate head passed the repository pytest/Ruff gate and the independent Stockfish integration job. Intermediate candidates with test or style defects were repaired and re-qualified on fresh exact-head CI runs before merge.

### Human QA / external authority still pending

The following remain intentionally outside the completed milestone:

- end-user review of diagnostic candidate selection and capture-consent disclosure, wording, timing, and pre-reveal contamination boundaries;
- real browser/device visual QA, screen-reader testing, accessibility conformance review, localization, interaction design, and usability testing for M28 or any successor surface;
- production model/provider and evaluator-provider selection;
- production credentials, secrets injection, privacy/security approval, data-transmission policy, and retention policy;
- live provider transport behavior, timeout/retry/backoff/rate-limit policy, latency SLOs, cost budgets, billing controls, and incident handling;
- semantic correctness, safety, and pedagogical quality of arbitrary model-authored coaching;
- completeness/correctness of a production evaluator beyond the bounded M20 contract;
- empirical tutoring efficacy, transfer, intervention-caused improvement, causal learner diagnosis, permanent-weakness claims, or automatic mastery;
- hosted authentication/authorization, multi-user tenancy, production persistence, observability operations, and deployment qualification.

These are explicit human/external authority gates. M26–M28 do not silently claim them.

## Recommended next priorities

The M26–M28 queue is complete. A future milestone should begin with a fresh live-main audit before promoting any suggestion below into an approved package queue.

1. **Persisted reviewed-coaching -> reference-surface bridge.** Add a bounded repository-local operator that starts from a participant-scoped M26 run or M25 artifact in the existing local store, verifies its M27 mechanical closure, and renders M28 without requiring a hand-assembled M25 bundle file. Preserve all existing authority boundaries and non-overwrite behavior.
2. **Deterministic local review package / navigation.** Add participant-scoped list/show/export tooling for M26 runs, M27 ledgers, M25 reviews, and M28 reference outputs, with content-addressed manifests and exact source fingerprints. Keep sensitive source/model/participant content out of summary indexes unless explicitly requested from the authoritative artifact.
3. **Hermetic execution-envelope privacy and retry preflight.** Add fake-adapter-only seams for secret injection/redaction validation, deterministic attempt-history simulation, and retry-plan policy checks without storing credentials, making live calls, or granting automatic retry authority. Production provider, privacy, security, and cost decisions remain external gates.

These are recommendations, not an approved work-package queue.

## Restart instructions for a future engineer or chat session

1. Read this `STATUS.md`.
2. Read `CONTEXT.md`, `docs/product/repository-build-status.md`, and `docs/runbooks/m26-m28-milestone-runbook.md`.
3. Confirm live `main` and recent commits before relying on hashes in this handoff.
4. Run the focused M26–M28 suites, then the full repository gate and independent Stockfish witness.
5. Preserve these boundaries:

```text
M26 orchestration != tutor-state transition or model-provider authority
M27 mechanical verification != semantic truth, retry authority, or privacy approval
M28 static reference rendering != production UI/accessibility/usability approval
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
participant selection != evidence-capture consent
```

6. Do not silently turn M26 into `cme tutor explain`; that transition remains explicit.
7. Do not expose M19 prose or M20 judgments as if they were M15 objective evidence.
8. Do not treat a skipped Stockfish suite as an independent-engine pass.
9. Before a new milestone, reconcile live `main` and propose a fresh bounded package queue rather than automatically implementing the recommendations above.

## Key references

- `CONTEXT.md`
- `docs/product/repository-build-status.md`
- `docs/runbooks/m26-m28-milestone-runbook.md`
- `docs/runbooks/m26-persistent-reviewed-coaching-operator.md`
- `docs/runbooks/m27-reviewed-coaching-execution-ledger.md`
- `docs/runbooks/m28-coach-review-reference-surface.md`
- PR #61 — M26
- PR #62 — M27
- PR #63 — M28
