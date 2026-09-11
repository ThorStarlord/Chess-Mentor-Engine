# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M34 — Hermetic Reviewed-Coaching Recovery Reconciliation, QUALIFIED / MERGED PR #71.  
**Post-feature `main` baseline:** `9e896bf955de24acaf6dc5d0503147eaaae3c1e4`.  

This file is the concise moving authority for repository state. Historical qualification detail remains in feature PRs, runbooks, Git history, and milestone handoffs. See [`STATUS.md`](../../STATUS.md) for the completed M32–M34 milestone handoff and [`docs/runbooks/m32-m34-milestone-runbook.md`](../runbooks/m32-m34-milestone-runbook.md) for restart/qualification commands. Software qualification is not empirical tutoring efficacy.

## Milestone board

```text
M1  - Trustworthy Chess Evidence Substrate                 QUALIFIED
M2  - Deterministic Chess Feature Extraction               QUALIFIED
M3  - Engine Evidence                                      QUALIFIED
M4  - Diagnostic Position Selection                        QUALIFIED
M5  - Player Decision Evidence                             QUALIFIED
M6  - Reasoning Discrepancy                                QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q                      QUALIFIED
M8  - Evidence-Aware Tutor Session                         QUALIFIED
M9  - Training Intervention Registry                       QUALIFIED
M10 - Bounded Outcome / Transfer Evidence                  QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                           QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                                   QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI                         QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                           QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract                     QUALIFIED - MERGED PR #47
M16 - Grounded Mentor Feedback Composer                    QUALIFIED - MERGED PR #48
M17 - Analysis-to-Presentation CLI Bridge                  QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue                       QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching                     QUALIFIED - MERGED PR #51
M20 - Model Coaching Evaluation Contract                   QUALIFIED - MERGED PR #53
M21 - Candidate-to-Tutor Orchestration                     QUALIFIED - MERGED PR #54
M22 - End-to-End Evaluation Fidelity Matrix                QUALIFIED - MERGED PR #55
M23 - Diagnostic-to-Persistent-Tutor Bridge                QUALIFIED - MERGED PR #57
M24 - Provider / Evaluator Execution Conformance           QUALIFIED - MERGED PR #58
M25 - Coach Review Read Model                              QUALIFIED - MERGED PR #59
M26 - Persistent Reviewed-Coaching Operator                QUALIFIED - MERGED PR #61
M27 - Reviewed-Coaching Execution Ledger                   QUALIFIED - MERGED PR #62
M28 - Local Coach-Review Reference Surface                 QUALIFIED - MERGED PR #63
M29 - Persisted Review -> Reference Surface Bridge         QUALIFIED - MERGED PR #65
M30 - Participant-Scoped Review Package & Navigation       QUALIFIED - MERGED PR #66
M31 - Execution-Envelope Privacy & Retry Preflight         QUALIFIED - MERGED PR #67
M32 - Persisted Review Delivery Fidelity Contract          QUALIFIED - MERGED PR #69
M33 - Deterministic Mentor-Feedback Trace Surface          QUALIFIED - MERGED PR #70
M34 - Reviewed-Coaching Recovery Reconciliation            QUALIFIED - MERGED PR #71
```

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M29 / PR #65 | `903b8543aace2a851786f1b8e4022084b60bb866` | `34ef3cf458c9a4c7e2cf4a9c44aeaa54225db4e3` | run `34542884614`: 754 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M30 / PR #66 | `556763d42c9ec5e0bad1abbfeb5dbd861f66e21a` | `8d3134c27479e2bf5649f66d5e2fcfe1f1dfca35` | run `34544479383`: 762 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M31 / PR #67 | `9a82f72af93215756818b991bd3d922144cf6ca2` | `6bd84881204e543f4cfe8906aa7cc15e894fc794` | run `34546266117`: 774 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M32 / PR #69 | `3381a85be5035dea5b426aac0d88d57317b80ffb` | `ae4bbe7c925855df9082c41bd46b4fea7d930bc8` | run `34553450225`: 790 passed, 8 intentional skips, M32 16/16, Ruff PASS, Stockfish 8/8 PASS |
| M33 / PR #70 | `761c0af847e84050ba7697ada6e8aa3e0b68a930` | `4eadb996b8c4036c793515d2457fe363c81cb40d` | run `34554448292`: 802 passed, 8 intentional skips, M33 12/12, Ruff PASS, Stockfish 8/8 PASS |
| M34 / PR #71 | `5e784e2662441d880e65589bc6413b9ff0b38f9f` | `9e896bf955de24acaf6dc5d0503147eaaae3c1e4` | run `34555466776`: 817 passed, 8 intentional skips, M34 15/15, Ruff PASS, Stockfish 8/8 PASS |

M32–M34 are complete. A new milestone must begin from live `main`, reconcile this status authority and `STATUS.md`, and establish a fresh bounded package queue before implementation.

## Current evidence / operator path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> M15 deterministic evaluation presentation
-> M18 diagnostic candidate batch
-> explicit participant candidate selection + separate capture consent
-> M23 cme-candidate-tutor
-> M21 authorization/launch
-> exact M5 PlayerDecisionContext
-> persisted replay-verifiable M8 state=selected
-> M13 tutor capture / freeze / reveal / compare workflow
-> position-local M6 discrepancy + optional bounded M7 context
-> replay-verified persisted M8 state=compared
-> M26 reviewed-coaching operator
   -> M16 deterministic grounded feedback
   -> optional M19 request / M24 provider execution / M19 coaching
   -> optional M20 request / M24 evaluator execution / M20 bounded evaluation
   -> M25 authority-separated coach-review read model
   -> atomic append-only M26 run lineage
-> M27 mechanical reviewed-coaching execution ledger
-> M29 persisted review -> M28 deterministic reference surface
-> M30 participant-scoped review package / navigation / export
-> M32 machine-readable persisted review delivery bundle
-> M33 deterministic M16 mentor-feedback trace
-> optional M31 synthetic-canary/manual-retry preflight
-> optional M34 hermetic multi-attempt recovery reconciliation
-> explicit M9 training applicability/selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

Not every application must invoke every optional downstream layer. Each arrow remains an authority boundary.

## Current operational surfaces

### Installed local commands

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

`cme analyze` and `cme diagnose` require an explicit external UCI executable or PATH name. Reviewed-coaching/review commands perform no production model-provider network call unless the application explicitly supplies its own M24-compatible adapter. Production provider selection remains outside repository authority.

M31–M34 remain Python API / hermetic validation surfaces; M32–M34 introduced no new production CLI command.

### M32 — persisted review delivery fidelity

M32 builds `m32.persisted-review-delivery-fidelity.v1` from one exact participant-scoped M30 package. It preserves exact M25 content order, explicit section authority labels, White versus decision-mover perspective, mate/bound/partial/unavailable semantics, comparison state, and exact source fingerprints. It rejects rehashed semantic or authority drift and can rebuild against persisted sources.

### M33 — deterministic mentor-feedback trace

M33 builds `m33.deterministic-mentor-feedback-trace.v1` over exact persisted M16 feedback. Each substantive deterministic feedback component is represented by stable identity, ordinal, content hash, source authority, source pointer, and source fields. M19/M20 remain separate presence/fingerprint metadata and cannot be promoted into deterministic provenance.

### M34 — reviewed-coaching recovery reconciliation

M34 builds `m34.reviewed-coaching-recovery-reconciliation.v1` from synthetic M24 multi-attempt histories and one already-persisted mechanically verified M26 target. It can classify a supplied history as complete or resume-eligible, binds exact endpoint/request/timeout/final-execution identity, and uses full-M26 restart scope for retryable partial failures. It never executes or authorizes retry and explicitly does not establish external-side-effect idempotency.

## Qualification commands

Focused current milestone:

```bash
python -m pytest tests/test_m32_persisted_review_delivery_fidelity.py -rs
python -m pytest tests/test_m33_deterministic_mentor_feedback_trace.py -rs
python -m pytest tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

Principal milestone regression:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py \
  tests/test_m30_participant_review_package_navigation.py \
  tests/test_m31_execution_envelope_preflight.py \
  tests/test_m32_persisted_review_delivery_fidelity.py \
  tests/test_m33_deterministic_mentor_feedback_trace.py \
  tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish witness requires `STOCKFISH_EXECUTABLE`; a skipped suite is not an independent-engine pass. Pull-request CI remains the merge authority. No standalone static Python type checker is configured.

See the consolidated [M32–M34 milestone runbook](../runbooks/m32-m34-milestone-runbook.md).

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent bounded tutor state, an operational diagnostic-to-persistent-tutor bridge, provider-neutral execution conformance, an authority-separated coach-review read model, atomic persistent reviewed coaching, privacy-bounded mechanical execution verification, deterministic persisted review rendering/navigation, a machine-readable consumer fidelity contract, deterministic mentor-feedback provenance tracing, and hermetic reviewed-coaching recovery reconciliation.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection, intervention-caused improvement, or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, vendor SDK, credential flow, transport, automatic retry/backoff policy, production latency/cost budget, or secrets architecture;
- external-side-effect idempotency or production recovery correctness;
- production privacy/security approval;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, visual correctness, or browser/device compatibility;
- hosted authentication/authorization, multi-user production persistence, observability, or deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model provenance, not model quality. M20 records bounded evaluator judgments, not objective truth. M27 qualifies persisted mechanics rather than semantics. M30 provides local navigation rather than authentication. M32 preserves consumer semantics rather than granting UI truth authority. M33 proves deterministic traceability rather than pedagogical correctness. M34 validates hermetic recovery histories rather than authorizing operational retries.
