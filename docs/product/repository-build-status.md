# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M28 — Thin M25 Local Review Reference Surface, QUALIFIED / MERGED PR #63.  
**Post-feature `main` baseline:** `4975fd65ba22ac1df6d32cd09512cc7c36c42ce8`.  

This file is the concise moving authority for repository state. Historical qualification detail remains in feature PRs, runbooks, architecture records, and Git history. See [`STATUS.md`](../../STATUS.md) for the completed M26–M28 milestone handoff. Software qualification is not empirical tutoring efficacy.

## Milestone board

```text
M1  - Trustworthy Chess Evidence Substrate          QUALIFIED
M2  - Deterministic Chess Feature Extraction        QUALIFIED
M3  - Engine Evidence                               QUALIFIED
M4  - Diagnostic Position Selection                 QUALIFIED
M5  - Player Decision Evidence                      QUALIFIED
M6  - Reasoning Discrepancy                         QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q               QUALIFIED
M8  - Evidence-Aware Tutor Session                  QUALIFIED
M9  - Training Intervention Registry                QUALIFIED
M10 - Bounded Outcome / Transfer Evidence           QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                    QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                            QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI                  QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                    QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract              QUALIFIED - MERGED PR #47
M16 - Grounded Mentor Feedback Composer             QUALIFIED - MERGED PR #48
M17 - Analysis-to-Presentation CLI Bridge           QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue                QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching              QUALIFIED - MERGED PR #51
M20 - Model Coaching Evaluation Contract            QUALIFIED - MERGED PR #53
M21 - Candidate-to-Tutor Orchestration              QUALIFIED - MERGED PR #54
M22 - End-to-End Evaluation Fidelity Matrix         QUALIFIED - MERGED PR #55
M23 - Diagnostic-to-Persistent-Tutor Bridge         QUALIFIED - MERGED PR #57
M24 - Provider / Evaluator Execution Conformance    QUALIFIED - MERGED PR #58
M25 - Coach Review Read Model                       QUALIFIED - MERGED PR #59
M26 - Persistent Reviewed-Coaching Operator         QUALIFIED - MERGED PR #61
M27 - Reviewed-Coaching Execution Ledger            QUALIFIED - MERGED PR #62
M28 - Local Coach-Review Reference Surface          QUALIFIED - MERGED PR #63
```

Supporting repairs/capabilities remain part of this baseline, including normalized UCI evidence, durable artifacts + verified M8 replay, exact authority-separated M25 projection, M26 atomic reviewed-coaching persistence, M27 mechanical execution verification, and M28 deterministic semantic HTML rendering.

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M23 / PR #57 | `8131685b434f52066e375e0914a2cf3ecf13c4c9` | `105fed42425a28d2733485b832e42ff656812279` | run `34499329989`: 659 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M24 / PR #58 | `e44ae84749de7820e9d403019ec7bddb5687639e` | `14f51b5e763f26b5c0608ecce8a237271641a94c` | run `34500991230`: 686 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M25 / PR #59 | `9927171cb5f09bf0274d0e2c36e9ab736a90baee` | `13db09f7cf4c066c49988875e89760ce204c2515` | run `34502823382`: 709 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M26 / PR #61 | `394bf9b22833077c898c4251c0eef3eb1b6fe866` | `3936b53f203b186efdf5f734b2b8ec2a266c41f4` | run `34518649749`: 718 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M27 / PR #62 | `b1699ad16193cb3b5541fa08c2b1b54e526f2040` | `492c1024834e3ae9d942d17941d5b22cc8dbcee7` | run `34520178321`: 728 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M28 / PR #63 | `cde21c1e426e1e0c8d0edc35ebe0f1d99e10cdee` | `4975fd65ba22ac1df6d32cd09512cc7c36c42ce8` | run `34521780789`: 746 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |

M26–M28 are complete. A new milestone must begin from live `main`, reconcile this status authority and `STATUS.md`, and establish a fresh bounded package queue before implementation.

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
-> M28 deterministic local M25 HTML reference surface
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
```

`cme analyze` and `cme diagnose` require an explicit external UCI executable or PATH name. `cme-candidate-tutor`, `cme-reviewed-coaching`, `cme-reviewed-coaching-ledger`, `cme-coach-review`, and `cme-coach-review-reference` perform no model-provider network call. The M26 Python API can receive explicit M24-compatible application adapters; production provider selection remains outside repository authority.

### M26 — Persistent reviewed-coaching operator

M26 closes the local gap between a replay-verified persisted M8 `compared` checkpoint and M16/M25. It validates exact M18/M21/M8 lineage, reconstructs the retained M3/M4 evidence, composes M15/M16, optionally accepts explicit M24-compatible provider/evaluator adapters through the Python API, assembles M25, and commits the output chain atomically. It does not advance M8 or silently replace `cme tutor explain`.

### M27 — Execution ledger and mechanical fidelity

M27 verifies already-persisted M26 closure through exact M25/M18/M21/M8/M16/M19/M20/M24 references. It writes only privacy-bounded references and transport-neutral execution metadata. It does not copy request payloads, model prose, evaluator rationales, or participant responses. `mechanically_verified` is not semantic truth, provider approval, retry authority, or privacy/security approval.

### M28 — Local coach-review reference surface

M28 validates a strict M25 input bundle and renders static semantic HTML without JavaScript, external assets, network calls, or browser automation. It preserves canonical White versus decision-mover score perspectives, bounds, symbolic mate, exact/partial/bounded/incompatible/unavailable/failure states, authority-source labels, and M20's truth-status ceiling. It qualifies deterministic local rendering and semantic structure only, not production accessibility/usability/localization or visual design.

## Qualification commands

Focused current milestone:

```bash
python -m pytest tests/test_m26_persistent_reviewed_coaching.py -rs
python -m pytest tests/test_m27_reviewed_coaching_execution_ledger.py -rs
python -m pytest tests/test_m28_coach_review_reference_surface.py -rs
```

Principal milestone regression:

```bash
python -m pytest \
  tests/test_m13_persistent_tutor_cli.py \
  tests/test_m18_diagnostic_analysis_queue.py \
  tests/test_m21_diagnostic_candidate_tutor_orchestration.py \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish witness requires `STOCKFISH_EXECUTABLE`; a skipped suite is not an independent engine pass. Pull-request CI remains the merge authority. No standalone static Python type checker is configured.

See the consolidated [M26–M28 milestone runbook](../runbooks/m26-m28-milestone-runbook.md).

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent bounded tutor state, an operational diagnostic-to-persistent-tutor bridge, provider-neutral execution conformance, an authority-separated coach-review read model, an atomic persistent reviewed-coaching operator, a privacy-bounded mechanical execution ledger, and a deterministic local HTML reference surface. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection, intervention-caused improvement, or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, vendor SDK, credential flow, transport, automatic retry policy, production latency/cost budget, or secrets architecture;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, visual correctness, or browser/device compatibility;
- a web UI, authenticated hosted service, production multi-user persistence, or deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model provenance, not model quality. M20 records bounded evaluator judgments, not objective truth. M21 is participant-authorized orchestration, not inference. M26 operationalizes reviewed coaching without broadening state-transition authority. M27 qualifies persisted mechanics rather than semantics. M28 qualifies a static local reference rendering rather than a production interface.
