# Chess Mentor Engine — Milestone Handoff

**Handoff scope:** completed M23–M25 milestone / Packages 1–3  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Pre-handoff feature baseline:** `13db09f7cf4c066c49988875e89760ce204c2515`  
**Prepared:** 2026-09-10  

This is the durable handoff for the milestone that operationalized the qualified
diagnostic-to-tutor path, added provider/evaluator execution conformance, and created
a stable authority-separated coach-review read model for future application surfaces.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation boundary, this file as the completed M23–M25 milestone
summary, and
[`docs/runbooks/m23-m25-milestone-runbook.md`](docs/runbooks/m23-m25-milestone-runbook.md)
for restart and qualification commands.

## Milestone outcome

All three queued packages are implemented, qualified on exact candidate heads, and
merged into `main`.

```text
Package 1 / M23  Diagnostic-to-Persistent-Tutor Operator Bridge      MERGED - PR #57
Package 2 / M24  Provider / Evaluator Execution Conformance          MERGED - PR #58
Package 3 / M25  Coach Review Read Model & Presentation Contract     MERGED - PR #59
```

The milestone closes the three priorities left by the M20–M22 handoff:

```text
M18 diagnostic queue
-> M23 cme-candidate-tutor operator
-> explicit M21 participant selection + capture consent
-> exact M5 PlayerDecisionContext
-> replay-verifiable persisted M8 state=selected
-> existing M13 persistent tutor transitions

M16 deterministic grounding
-> M19 request
-> M24 provider execution conformance
-> M19 bind/record
-> M20 evaluation request
-> M24 evaluator execution conformance
-> M20 bounded evaluation

M15 objective evidence
+ M18 diagnostic selection
+ M21 participant authority
+ M8 tutor state
+ M16 deterministic grounding
+ M19 model prose
+ M20 evaluator judgment
-> M25 authority-separated application read model
-> cme-coach-review local inspection
```

The previous statement that M21 had no CLI bridge into persistent M13 tutoring is no
longer true: M23 closes that local operator/persistence seam. M24 does not implement a
live vendor transport or grant retry authority. M25 is a read model, not a production
UI and not a new semantic authority layer.

## Package 1 — M23 Diagnostic-to-Persistent-Tutor Operator Bridge

**PR:** #57  
**Final candidate head:** `8131685b434f52066e375e0914a2cf3ecf13c4c9`  
**Merge commit:** `105fed42425a28d2733485b832e42ff656812279`  
**CI run:** `34499329989`

Delivered:

- installed repository-local `cme-candidate-tutor` command;
- exact reconstruction and validation of an M18 diagnostic queue and selected
  `DiagnosticCandidateBatch` member;
- explicit, separate participant candidate selection and evidence-capture consent;
- reuse of native M21 authorization/launch behavior rather than duplicating its
  authority;
- exact PGN/source/game/root-ply/child provenance checks;
- native M5 `PlayerDecisionContext` creation and only initial M8 `state=selected`;
- atomic local artifact lineage from M18 queue -> M21 authorization -> M21 launch ->
  M8 checkpoint, plus exact prompt dependencies;
- reload/replay verification after persistence;
- rejection coverage for declined selection/consent, impossible authorization,
  source/policy/candidate drift, wrong PGN, missing candidate, incomplete prompts,
  and repeated identical invocation.

Qualification evidence:

```text
659 passed, 8 intentional external-engine skips
Focused M23 suite: 11 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: PASS
```

M23 creates no automatic M6 discrepancy, M7 learner hypothesis, M9 training decision,
model language, or pedagogical-efficacy claim.

See
[`docs/runbooks/m23-diagnostic-to-persistent-tutor.md`](docs/runbooks/m23-diagnostic-to-persistent-tutor.md).

## Package 2 — M24 Provider / Evaluator Execution Conformance

**PR:** #58  
**Final candidate head:** `e44ae84749de7820e9d403019ec7bddb5687639e`  
**Merge commit:** `14f51b5e763f26b5c0608ecce8a237271641a94c`  
**CI run:** `34500991230`

Delivered:

- provider-neutral execution wrappers around the existing M19 provider and M20
  evaluator contracts;
- deep-frozen detached JSON requests so adapters do not receive mutable source
  requests by reference;
- explicit provider/model/evaluator endpoint identity matching;
- content-addressed success/failure execution provenance;
- fail-closed failure classification for `invalid_request`, `request_mutation`,
  `timeout`, `transient`, `permanent`, `malformed_response`, `identity_mismatch`, and
  `chronology_violation`;
- retryability metadata only for timeout/transient outcomes, with no automatic retry;
- conformant runners that return successful generations to the already-qualified
  M19/M20 binders;
- hermetic fake-provider/evaluator qualification including mutation, malformed
  result, identity, chronology, and deterministic failure behavior.

Qualification evidence:

```text
686 passed, 8 intentional external-engine skips
Focused M24 suite: 27 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: PASS
```

M24 chooses no production vendor, installs no vendor SDK, uses no credentials, makes
no live provider call, and establishes no semantic truth for arbitrary model prose or
evaluator output.

See
[`docs/runbooks/m24-provider-evaluator-conformance.md`](docs/runbooks/m24-provider-evaluator-conformance.md).

## Package 3 — M25 Coach Review Read Model & Presentation Contract

**PR:** #59  
**Final candidate head:** `9927171cb5f09bf0274d0e2c36e9ab736a90baee`  
**Merge commit:** `13db09f7cf4c066c49988875e89760ce204c2515`  
**CI run:** `34502823382`

Delivered:

- content-addressed `m25.coach-review-read-model.v1` projection;
- installed repository-only `cme-coach-review` JSON inspection command;
- frozen, structurally separate sections for M15 objective evidence, M18 diagnostic
  selection, M21 participant authority, M8 tutor state, M16 deterministic grounding,
  M19 model coaching, and M20 model evaluation;
- mechanical cross-layer ID/fingerprint and progressive-dependency checks;
- verbatim preservation of M15 White-versus-decision-mover perspective, bounds,
  exactness, symbolic mate, unavailable/partial/incompatible/failure states, and
  evidence provenance;
- explicit preservation of M20
  `truth_status = not_established_by_m20_evaluation`;
- model-overclaim isolation so arbitrary M19 prose cannot mutate objective or
  deterministic-grounding sections;
- golden fidelity signatures covering eight M22 evidence regimes plus adversarial
  cross-layer drift/rejection cases.

Qualification evidence:

```text
709 passed, 8 intentional external-engine skips
Focused M25 suite: 23 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: PASS
```

M25 creates no chess facts, consent, tutor transition, learner hypothesis, training
selection, model output, evaluator verdict, production UI, or pedagogical-quality
claim.

See
[`docs/runbooks/m25-coach-review-read-model.md`](docs/runbooks/m25-coach-review-read-model.md).

## Current operational surfaces

Installed commands now include:

```text
cme
cme-candidate-tutor
cme-coach-review
```

The principal local flow is:

```text
cme diagnose ...
-> cme-candidate-tutor ...
-> cme tutor status / present-position / present-stage / respond / freeze / reveal /
   compare / attach-hypothesis / explain / complete
-> application-owned M16/M19/M20 orchestration as applicable
-> cme-coach-review <m25-bundle.json>
```

M24 is a Python execution/conformance API, not a standalone CLI. Exact commands and
focused qualification suites are consolidated in the M23–M25 milestone runbook.

## Verified evidence and remaining gates

### Software qualification

No repository-only or hermetic software gate from M23–M25 remains pending. Each
package was merged only after the exact repaired candidate head passed the repository
pytest/Ruff gate and the independent Stockfish integration job. Earlier candidates
that had only style issues were not treated as merge-ready; their repaired heads were
re-qualified from scratch.

### Human QA / external authority still pending

The following are intentionally outside the completed milestone:

- end-user review of candidate-selection and capture-consent disclosure, wording,
  timing, and the actual pre-reveal contamination boundary;
- browser/desktop visual QA, accessibility, localization, interaction design, and
  usability testing for any future M25 presentation surface;
- production model/provider and evaluator-provider selection;
- production credentials, secrets injection, privacy/security review, data
  transmission policy, and retention policy;
- live transport behavior, provider-specific timeout/retry/backoff/rate limits,
  latency SLOs, cost budgets, billing controls, and incident policy;
- semantic correctness, safety, and pedagogical quality of arbitrary model-authored
  coaching;
- completeness/correctness of a production evaluator beyond the bounded M20 policy;
- empirical tutoring efficacy, transfer, intervention-caused improvement, causal
  learner diagnosis, permanent-weakness claims, or automatic mastery;
- hosted authentication/authorization, multi-user tenancy, production persistence,
  observability, and deployment qualification.

These are explicit external/human gates. M23–M25 do not silently claim them.

## Recommended next priorities

The M23–M25 queue is complete. A future audit should re-check live `main` before
turning these suggestions into packages, but the strongest current next directions
are:

1. **Persistent compared-session -> reviewed-coaching operator pipeline.** Add a
   bounded local operator over a replay-verified M13 compared checkpoint and exact
   M3/M4 evidence that can produce M16 grounding, invoke M24-qualified fake/provider
   seams for M19/M20, assemble M25, and persist exact lineage. Keep model/evaluator
   execution optional and do not silently replace the explicit-input semantics of
   `cme tutor explain`.
2. **Execution-envelope observability and privacy contract.** Extend the M24-neutral
   boundary with explicit redaction/secrets-injection seams, transport-independent
   attempt/latency/cost metadata, and deterministic retry-attempt history using fake
   adapters first. Do not freeze a vendor or credential flow in repository code.
3. **Thin local review/reference presentation over M25.** Render the qualified M25
   authority-separated sections through a deliberately small local reference surface
   with deterministic snapshots and accessibility-oriented semantics. Treat polished
   browser UX, disclosure correctness, and production design quality as later human
   gates.

These are recommendations, not an approved work-package queue.

## Restart instructions for a future engineer or chat session

1. Read this `STATUS.md`.
2. Read `CONTEXT.md`, `docs/product/repository-build-status.md`, and
   `docs/runbooks/m23-m25-milestone-runbook.md`.
3. Confirm live `main` and recent commits before relying on hashes in this handoff.
4. Run the focused M23–M25 suites and then the full repository gate.
5. Preserve these boundaries:

```text
M23 operator/persistence != diagnostic or learner-inference authority
M24 execution conformance != production vendor approval or semantic truth
M25 read model != production UI or new evidence authority
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
participant selection != evidence-capture consent
```

6. Do not expose diagnostic engine rationale as if it were clean pre-reveal
   participant evidence.
7. Do not treat a skipped Stockfish suite as an independent-engine pass.
8. Before a new milestone, reconcile live `main` and propose a fresh bounded package
   queue rather than automatically continuing these recommendations.

## Key references

- `README.md`
- `CONTEXT.md`
- `docs/product/repository-build-status.md`
- `docs/runbooks/m23-m25-milestone-runbook.md`
- `docs/runbooks/m23-diagnostic-to-persistent-tutor.md`
- `docs/runbooks/m24-provider-evaluator-conformance.md`
- `docs/runbooks/m25-coach-review-read-model.md`
- PR #57 — M23
- PR #58 — M24
- PR #59 — M25
