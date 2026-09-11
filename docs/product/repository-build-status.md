# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M31 — Hermetic Execution-Envelope Privacy & Retry Preflight, QUALIFIED / MERGED PR #67.  
**Post-feature `main` baseline:** `6bd84881204e543f4cfe8906aa7cc15e894fc794`.  

This file is the concise moving authority for repository state. Historical qualification detail remains in feature PRs, runbooks, architecture records, Git history, and milestone handoffs. See [`STATUS.md`](../../STATUS.md) for the completed M29–M31 milestone handoff and [`docs/runbooks/m29-m31-milestone-runbook.md`](../runbooks/m29-m31-milestone-runbook.md) for restart/qualification commands. Software qualification is not empirical tutoring efficacy.

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
```

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M26 / PR #61 | `394bf9b22833077c898c4251c0eef3eb1b6fe866` | `3936b53f203b186efdf5f734b2b8ec2a266c41f4` | run `34518649749`: 718 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M27 / PR #62 | `b1699ad16193cb3b5541fa08c2b1b54e526f2040` | `492c1024834e3ae9d942d17941d5b22cc8dbcee7` | run `34520178321`: 728 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M28 / PR #63 | `cde21c1e426e1e0c8d0edc35ebe0f1d99e10cdee` | `4975fd65ba22ac1df6d32cd09512cc7c36c42ce8` | run `34521780789`: 746 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M29 / PR #65 | `903b8543aace2a851786f1b8e4022084b60bb866` | `34ef3cf458c9a4c7e2cf4a9c44aeaa54225db4e3` | run `34542884614`: 754 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M30 / PR #66 | `556763d42c9ec5e0bad1abbfeb5dbd861f66e21a` | `8d3134c27479e2bf5649f66d5e2fcfe1f1dfca35` | run `34544479383`: 762 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M31 / PR #67 | `9a82f72af93215756818b991bd3d922144cf6ca2` | `6bd84881204e543f4cfe8906aa7cc15e894fc794` | run `34546266117`: 774 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |

M29–M31 are complete. A new milestone must begin from live `main`, reconcile this status authority and `STATUS.md`, and establish a fresh bounded package queue before implementation.

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
-> optional M31 hermetic execution-envelope privacy + manual-retry-history preflight
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

`cme analyze` and `cme diagnose` require an explicit external UCI executable or PATH name. The reviewed-coaching/review commands perform no production model-provider network call. The M26 Python API can receive explicit M24-compatible application adapters; production provider selection remains outside repository authority. M31 remains a Python API / hermetic validation surface and does not execute retries.

### M29 — persisted review bridge

M29 starts from an exact participant-scoped persisted M26 run or M25 review, resolves the immutable M26/M25 relationship, requires M27 single-run mechanical verification, and renders the persisted M25 payload through M28. It removes hand-assembled M25 bundles from the persisted operator path without creating a new evidence authority.

### M30 — participant review package/navigation

M30 adds deterministic `list`, `show`, and `export` tooling. Its content-addressed package manifest retains exact references/fingerprints and M28 surface identity while keeping source payloads, model prose, evaluator rationale, participant responses, and HTML out of summary indexes. Exact content requires an explicit action.

### M31 — execution-envelope preflight

M31 validates synthetic `CME_TEST_CANARY_*` leakage boundaries and already-supplied manual retry histories around M24/M26. It preserves `automatic_retry=false`, allows later attempts only after M24 timeout/transient classifications, requires exact final-attempt binding to persisted M26 execution, and stores only summary-safe evidence. It does not accept production credentials, execute retries, choose a vendor, or approve production privacy/security policy.

## Qualification commands

Focused current milestone:

```bash
python -m pytest tests/test_m29_persisted_review_reference_bridge.py -rs
python -m pytest tests/test_m30_participant_review_package_navigation.py -rs
python -m pytest tests/test_m31_execution_envelope_preflight.py -rs
```

Principal milestone regression:

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

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish witness requires `STOCKFISH_EXECUTABLE`; a skipped suite is not an independent-engine pass. Pull-request CI remains the merge authority. No standalone static Python type checker is configured.

See the consolidated [M29–M31 milestone runbook](../runbooks/m29-m31-milestone-runbook.md).

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent bounded tutor state, an operational diagnostic-to-persistent-tutor bridge, provider-neutral execution conformance, an authority-separated coach-review read model, atomic persistent reviewed-coaching, privacy-bounded mechanical execution verification, deterministic persisted review rendering, participant-scoped review package/navigation, and a hermetic privacy/manual-retry preflight. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection, intervention-caused improvement, or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, vendor SDK, credential flow, transport, automatic retry/backoff policy, production latency/cost budget, or secrets architecture;
- production privacy/security approval;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, visual correctness, or browser/device compatibility;
- hosted authentication/authorization, multi-user production persistence, observability, or deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model provenance, not model quality. M20 records bounded evaluator judgments, not objective truth. M27 qualifies persisted mechanics rather than semantics. M28 qualifies local reference rendering rather than a production interface. M30 provides local navigation rather than authentication. M31 validates hermetic histories rather than authorizing operational retries.