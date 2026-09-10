# Chess Mentor Engine — Milestone Handoff

**Handoff scope:** completed M20–M22 milestone / Packages 1–3  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Post-feature baseline:** `7f59c6add7ffe042d8c2b65d6273867673b6d74b`  
**Prepared:** 2026-09-10  

This document is the durable handoff for the milestone that added bounded evaluation
of model-authored coaching, connected an exact diagnostic candidate into the
participant-evidence tutor flow, and qualified end-to-end evaluation fidelity across
the engine/presentation/feedback/model/evaluator layers.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation boundary and this file for the completed milestone
summary, qualification evidence, restart instructions, and recommended next-session
priorities.

## Milestone outcome

All three queued packages are implemented, qualified on exact candidate heads, and
merged into `main`.

```text
Package 1 / M20  Model Coaching Evaluation Contract & Harness       MERGED - PR #53
Package 2 / M21  Diagnostic Candidate -> Tutor Session Orchestration MERGED - PR #54
Package 3 / M22  End-to-End Evaluation Fidelity Matrix               MERGED - PR #55
```

The milestone closes the three priorities left by the previous M17–M19 handoff:

```text
M19 model-authored prose
-> M20 explicit bounded evaluator contract

M18 selected diagnostic candidate
-> M21 explicit participant selection + capture consent
-> M5 PlayerDecisionContext
-> M8 TutorSession(state=selected)

M3/M4 objective evidence
-> M15 presentation
-> M16 deterministic grounding
-> M19 model-language request/result
-> M20 evaluator request/result
-> M22 cross-layer fidelity qualification
```

The authority boundaries remain intentional. M20 does not make an evaluator a source
of objective chess truth. M21 is orchestration, not learner inference. M22 is a
regression/architectural-integrity qualification, not a production-quality or
pedagogical-efficacy claim.

## Package 1 — M20 Model Coaching Evaluation Contract & Harness

**PR:** #53  
**Final candidate head:** `583ccda3a357605bc9ff2318ce85bc940031730b`  
**Merge commit:** `2d57b953ee8336a5bdd05f00f48905d000158691`  
**CI run:** `34481292153`

Delivered:

- content-addressed `m20.model-coaching-evaluation-request.v1` over exact current
  M16/M19 source records;
- content-addressed `m20.model-coaching-evaluation.v1` result records;
- seven frozen evaluation dimensions covering grounding consistency, objective chess
  consistency, evidence sufficiency, uncertainty preservation, mate/bound
  preservation, learner-inference scope, and authority boundaries;
- explicit `pass | fail | unclear` judgments and deterministic aggregate status;
- evaluator provenance without promoting evaluator output to chess truth;
- exact M19/source revalidation before evaluator use;
- fail-closed coverage for policy/source/request drift, evaluator mutation/failure,
  incomplete/duplicate dimensions, malformed verdicts, and chronology errors;
- a hermetic adversarial corpus for fabricated centipawn precision, bounded-to-exact
  promotion, symbolic-mate conversion, learner overclaiming, invented hypotheses,
  unsupported training authority, and ambiguous claims;
- explicit retained ceiling:
  `truth_status = not_established_by_m20_evaluation`.

Qualification evidence:

```text
616 passed, 8 intentional external-engine skips
Focused M20 suite: 18 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

Operational APIs:

```text
chess_mentor_engine.coaching.build_model_coaching_evaluation_request
chess_mentor_engine.coaching.bind_model_coaching_evaluation
chess_mentor_engine.coaching.run_model_coaching_evaluation
ModelCoachingEvaluationGeneration
ModelCoachingEvaluationJudgment
```

See [`docs/runbooks/m20-model-coaching-evaluation.md`](docs/runbooks/m20-model-coaching-evaluation.md).

## Package 2 — M21 Diagnostic Candidate -> Tutor Session Orchestration

**PR:** #54  
**Final candidate head:** `537c9d9751103bc5c0569fa26b12a229cc47a6fe`  
**Merge commit:** `20ddff116aa501f2644bfcdbef69d4c173d93763`  
**CI run:** `34483038324`

Delivered:

- content-addressed participant authorization with separate candidate selection and
  capture-consent decisions;
- exact binding to the selected M18 candidate and deterministic candidate batch;
- retained selection-signal identity checks and candidate/batch fingerprint checks;
- revalidation of source/game/root-ply/child-ply provenance against the exact
  canonical game;
- internal derivation of the M1 position-context packet instead of trusting a
  caller-authored display/context record;
- bounded launch into only the native M5 `PlayerDecisionContext` and initial M8
  `TutorSession(state=selected)`;
- deterministic launch provenance and an explicit no-M6/M7/M9/M10/M11 authority
  ceiling;
- fail-closed coverage for consent/selection mismatch, same-ID source drift,
  candidate/batch/authorization tampering, canonical-game mismatch, noncanonical
  position copies, chronology violations, and invalid capture protocols.

Qualification evidence:

```text
633 passed, 8 intentional external-engine skips
Focused M21 suite: 17 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

Operational APIs:

```text
chess_mentor_engine.tutoring.record_candidate_tutor_authorization
chess_mentor_engine.tutoring.start_candidate_tutor_session
```

M21 intentionally stops at the initial selected M8 state. The caller must continue
through the existing qualified M8 sequence beginning with `present_tutor_position`.
It does not choose the candidate, create M6/M7 inference, choose training, or generate
mentor language.

See [`docs/runbooks/m21-diagnostic-candidate-tutor-orchestration.md`](docs/runbooks/m21-diagnostic-candidate-tutor-orchestration.md).

## Package 3 — M22 End-to-End Evaluation Fidelity Matrix

**PR:** #55  
**Final candidate head:** `10e7dac9ef0b6ebafce9b5d307ec99e1fd254ca5`  
**Merge commit:** `7f59c6add7ffe042d8c2b65d6273867673b6d74b`  
**CI run:** `34484791539`

Delivered:

- machine-readable eight-regime fidelity matrix covering:
  - exact White root MultiPV;
  - bounded Black decision-mover perspective and bound reversal;
  - symbolic terminal mate;
  - partial root evidence;
  - complete-but-empty/unavailable root evidence;
  - compatible played-child reanalysis;
  - incompatible child analysis regime;
  - failed child analysis;
- native M3/M4 -> M15 regression rather than a duplicate chess evaluator;
- exact M15 -> M16 -> M19 -> M20 source-continuity regression;
- explicit verification that model overclaims do not mutate true M15/M16 source
  evaluation;
- rehashed M19 grounding-drift and rehashed M20 presentation-drift rejection tests,
  proving source validation still fails after outer content-addressed IDs are
  recomputed;
- direct M15 source-reference and M16 analysis-binding rejection coverage;
- explicit preservation of score perspective, exactness, bounds, symbolic mate,
  failure/incompatibility state, and source provenance.

Qualification evidence:

```text
648 passed, 8 intentional external-engine skips
Focused M22 suite: 15 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

An earlier M22 candidate passed all 648 behavioral tests but Ruff correctly rejected
one import-order issue and two line-length issues. The style-only repair produced the
exact final head above, which then passed the complete gate before merge.

See [`docs/runbooks/m22-end-to-end-evaluation-fidelity-matrix.md`](docs/runbooks/m22-end-to-end-evaluation-fidelity-matrix.md).

## Validation / regression runbook

Install for development:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the focused M20–M22 suites:

```bash
python -m pytest tests/test_m20_model_coaching_evaluation.py
python -m pytest tests/test_m21_diagnostic_candidate_tutor_orchestration.py
python -m pytest tests/test_m22_end_to_end_evaluation_fidelity.py
```

Run the combined mentor/evaluation regression:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py
```

Run the full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish integration suite requires `STOCKFISH_EXECUTABLE`. A skipped external
engine suite is not a successful independent-engine witness. Pull-request CI remains
the merge authority.

No new CLI command was introduced by M20–M22. M20 and M21 expose Python APIs; M22 is
a qualification matrix/test surface. Existing CLI commands remain documented in
`README.md` and the M13/M14/M17/M18 runbooks.

## Verified evidence and remaining gates

### Software qualification

No software qualification gate from M20–M22 remains pending. All three packages were
merged only after their exact final candidate heads passed native pytest, Ruff,
editable package install, and the independent Stockfish witness.

### Human QA / external authority still pending

The following remain intentionally outside software qualification:

- semantic correctness and pedagogical quality of arbitrary model-authored coaching;
- completeness/correctness of any production model or human evaluator used through
  M20;
- production model/provider and evaluator-provider choice;
- production credential handling, privacy policy, transport, retries, rate limits,
  cost/latency budgets, and service availability;
- end-user review of M21 candidate-selection/capture-consent disclosure and the M5/M8
  pre-reveal contamination boundary;
- browser/UI usability, accessibility, localization, and visual correctness;
- empirical tutoring efficacy, transfer, and intervention-caused improvement;
- causal learner diagnosis, permanent weakness claims, mastery, or universal
  move-quality thresholds;
- hosted multi-user architecture, authentication, authorization, secrets management,
  and production persistence.

Those are explicit external/human gates, not hidden claims made by M20–M22.

## Recommended next priorities

M20–M22 completed the three priorities from the previous handoff. The next milestone
should therefore build on these qualified contracts rather than reopen them.
Recommended order:

1. **Diagnostic-to-tutor operator workflow.** Add a bounded local operator surface
   that consumes an M18 diagnostic result, records explicit M21 participant selection
   and capture consent, creates the M5/M8 launch, and hands off into replay-verified
   M13/M8 persistence. Preserve the pre-reveal boundary and do not auto-create M6/M7
   or training authority. This is the largest remaining workflow-integration gap.
2. **Model/evaluator provider conformance layer.** Now that M19 has a provenance
   boundary and M20 has evaluation criteria, define provider adapters/conformance
   tests for model generation and model-output evaluation: explicit timeout/retry
   semantics, provider/model/version identity, detached-request mutation checks,
   cost/latency telemetry fields, redaction/secrets injection boundaries, and
   deterministic failure records. Qualify with fake providers first; live credentials
   and vendor approval remain external.
3. **Thin review/coach presentation surface.** Expose the already-qualified M15
   evaluation, M18 candidate queue, M21 selection/consent, M16/M19 coaching, and M20
   evaluation status in a deliberately thin inspectable UI/read model. Keep objective
   evidence, participant evidence, model prose, and evaluator verdicts visually and
   structurally distinct. Defer polished production UX claims until human QA exists.

A future audit may split these into different packages if live `main` or product
priorities have changed.

## Restart instructions for a future engineer or chat session

1. Read this `STATUS.md`.
2. Read `CONTEXT.md` and `docs/product/repository-build-status.md`.
3. Confirm live `main` and recent commits before trusting any hash in this handoff.
4. Run the focused M20–M22 suites and the full repository gate before changing the
   current mentor/evaluation path.
5. Preserve these authority boundaries:

```text
M16 deterministic grounding != M19 model prose
M19 request provenance != semantic correctness
M20 evaluator acceptance != objective chess truth
M21 orchestration != learner inference
M22 fidelity qualification != production/pedagogical validation
```

6. Treat explicit participant choice and capture consent as required inputs to M21;
   do not expose diagnostic engine rationale as if it were clean pre-reveal M5 input.
7. If starting a new milestone, audit current `main` and propose a fresh bounded work
   package queue before implementation.

## Key references

- `README.md`
- `CONTEXT.md`
- `docs/product/repository-build-status.md`
- `docs/runbooks/m19-provenance-bound-model-coaching.md`
- `docs/runbooks/m20-model-coaching-evaluation.md`
- `docs/runbooks/m21-diagnostic-candidate-tutor-orchestration.md`
- `docs/runbooks/m22-end-to-end-evaluation-fidelity-matrix.md`
- PR #53 — M20
- PR #54 — M21
- PR #55 — M22
