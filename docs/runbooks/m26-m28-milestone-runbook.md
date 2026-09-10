# M26–M28 Milestone Runbook

This runbook is the restart and qualification guide for the completed M26–M28 milestone.

It covers:

```text
M26 Persistent Reviewed-Coaching Operator
M27 Reviewed-Coaching Execution Ledger & Fidelity Qualification
M28 Thin M25 Local Review Reference Surface
```

These milestones extend the already-qualified M13/M18/M21/M23/M24/M25 chain. They do not create new chess-truth, learner-inference, tutor-state, provider-selection, evaluator-truth, or pedagogical authority.

## 1. Repository baseline

Completed feature baseline after M28:

```text
4975fd65ba22ac1df6d32cd09512cc7c36c42ce8
```

Promotion evidence:

| Milestone | PR | Final candidate | CI run | Result |
| --- | --- | --- | --- | --- |
| M26 | #61 | `394bf9b22833077c898c4251c0eef3eb1b6fe866` | `34518649749` | 718 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 |
| M27 | #62 | `b1699ad16193cb3b5541fa08c2b1b54e526f2040` | `34520178321` | 728 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 |
| M28 | #63 | `cde21c1e426e1e0c8d0edc35ebe0f1d99e10cdee` | `34521780789` | 746 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 |

Always confirm live `main` before relying on these hashes.

## 2. Install

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Useful command discovery:

```bash
cme --help
cme-candidate-tutor --help
cme-coach-review --help
cme-reviewed-coaching --help
cme-reviewed-coaching-ledger --help
cme-coach-review-reference --help
```

Stockfish or another UCI engine is an explicitly supplied external executable for engine-backed qualification and analysis. No engine binary is bundled.

## 3. Local milestone flow

The bounded local path is:

```text
M18 diagnostic queue
-> M23 cme-candidate-tutor
-> M21 authorization/launch
-> persisted M8 tutor session
-> M13 capture / freeze / reveal / compare
-> replay-verified M8 state=compared
-> M26 reviewed-coaching operator
-> M25 read model + M26 run lineage
-> M27 mechanical execution ledger
-> M28 static M25 reference surface
```

M19/M20 provider/evaluator execution is optional in M26 and available only through explicit M24-compatible Python adapters. The installed M26 CLI is deterministic-only.

### 3.1 Reach a compared tutor checkpoint

Use the existing M13 workflow after candidate launch:

```text
cme tutor status
cme tutor present-position
cme tutor present-stage
cme tutor respond
cme tutor freeze
cme tutor reveal
cme tutor compare
cme tutor attach-hypothesis
```

The exact command arguments depend on the current M13 checkpoint and prompts. See [`m13-persistent-tutor-cli.md`](m13-persistent-tutor-cli.md) and [`m23-diagnostic-to-persistent-tutor.md`](m23-diagnostic-to-persistent-tutor.md).

Do not use M26 as an implicit replacement for:

```text
cme tutor explain
```

That remains the explicit persisted M8 explanation transition.

## 4. M26 — Persistent reviewed coaching

### Deterministic CLI

```bash
cme-reviewed-coaching \
  '<tutor-session-id>:<snapshot-fingerprint>' \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-10T15:00:00-03:00
```

The checkpoint must be an exact replay-verifiable `compared` session with retained dependency closure:

```text
M8 compared checkpoint
-> M21 launch
-> M21 authorization
-> M18 diagnostic queue
```

On success, the deterministic CLI persists:

```text
M16 grounded feedback
M25 coach-review read model
M26 orchestration run
```

The source tutor checkpoint remains `compared` and unexplained.

### Optional Python adapter seam

`run_persistent_reviewed_coaching(...)` can receive explicit M24-compatible provider and evaluator adapters. With both optional layers enabled, the atomic output chain may also contain:

```text
M19 model request
M24 provider execution
M19 provenance-bound coaching
M20 evaluation request
M24 evaluator execution
M20 bounded evaluation
```

Use hermetic fake adapters for repository qualification. Do not add real credentials or live provider calls to milestone tests.

### M26 focused qualification

```bash
python -m pytest tests/test_m26_persistent_reviewed_coaching.py -rs
```

Key rejection expectations include:

- non-`compared` tutor checkpoints;
- missing M21/M18 retained lineage;
- identity/fingerprint drift;
- invalid provider/evaluator adapter combinations;
- provider/evaluator classified failures;
- no partial writes when any qualified step fails;
- idempotent repeated deterministic invocation.

See [`m26-persistent-reviewed-coaching-operator.md`](m26-persistent-reviewed-coaching-operator.md).

## 5. M27 — Execution ledger and mechanical fidelity

Qualify all persisted M26 runs for one participant:

```bash
cme-reviewed-coaching-ledger \
  --db ./mentor.sqlite3 \
  --participant P01
```

Select explicit runs by repeating `--run-id`:

```bash
cme-reviewed-coaching-ledger \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --run-id reviewed_coaching_run_aaaaaaaaaaaaaaaaaaaa \
  --run-id reviewed_coaching_run_bbbbbbbbbbbbbbbbbbbb
```

M27 verifies exact persisted closure through M26/M25/M18/M21/M8/M16 and optional M19/M20/M24 artifacts. Input selection order does not affect ledger identity.

The ledger intentionally does **not** copy:

```text
request payloads
model rendered coaching content
evaluator rationale text
participant raw or structured response content
```

It may retain content-addressed references plus transport-neutral execution metadata required for mechanical verification.

### M27 focused qualification

```bash
python -m pytest tests/test_m27_reviewed_coaching_execution_ledger.py -rs
```

Key rejection expectations include:

- missing/duplicate requested run IDs;
- participant or dependency drift;
- forged M25 projection content;
- M19/M20/M24 request/response provenance mismatch;
- successful runs containing failed M24 executions;
- any attempt to promote automatic retry authority;
- any M20 truth-status promotion.

`mechanically_verified` never means semantic model correctness, evaluator truth, provider approval, privacy approval, or pedagogical effectiveness.

See [`m27-reviewed-coaching-execution-ledger.md`](m27-reviewed-coaching-execution-ledger.md).

## 6. M25 JSON review inspection

A strict local M25 bundle can still be inspected as canonical JSON:

```bash
cme-coach-review ./m25-bundle.json
```

This path is useful when checking the authority-separated read model before rendering M28.

The M25 bundle shape contains the already-qualified layers:

```text
evaluation_presentation
diagnostic_candidate
diagnostic_batch
authorization
launch
tutor_state
grounded_feedback
model_coaching
model_evaluation
```

Optional downstream records may be `null` only where M25 progression rules permit them.

See [`m25-coach-review-read-model.md`](m25-coach-review-read-model.md).

## 7. M28 — Static local reference surface

Render one new HTML file from a strict M25 bundle:

```bash
cme-coach-review-reference ./m25-bundle.json \
  --output ./review/coach-review-reference.html
```

M28 refuses to overwrite an existing `.html` or `.htm` output.

The command performs no model call, engine call, network access, browser automation, credential lookup, or deployment.

The generated static surface preserves:

- M15 canonical White and decision-mover score perspectives;
- exact/lower/upper bound labels;
- symbolic mate rather than fake centipawn conversion;
- exact, partial, bounded, incompatible, unavailable, terminal, and failure states;
- explicit M15/M18/M21/M8/M16/M19/M20 authority-source labels;
- M20 `truth_status = not_established_by_m20_evaluation`;
- inert escaped model/evaluator/source content;
- source fingerprints and exact canonical source disclosure.

The HTML uses semantic landmarks/headings/tables and accessibility-oriented structure, but passing structural tests is **not** production accessibility certification.

### M28 focused qualification

```bash
python -m pytest tests/test_m28_coach_review_reference_surface.py -rs
```

Key rejection expectations include:

- malformed strict M25 bundles;
- mutated M25 identity/separation contract;
- M20 truth promotion;
- unsafe output extensions;
- missing input paths;
- overwrite attempts;
- script/HTML-like model text becoming markup rather than inert escaped text.

See [`m28-coach-review-reference-surface.md`](m28-coach-review-reference-surface.md).

## 8. Principal M26–M28 regression

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

## 9. Full merge qualification

Native repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Independent Stockfish witness:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not an independent-engine pass. Pull-request CI on the exact candidate head remains the merge-readiness authority.

## 10. Authority guardrails

Preserve these distinctions in future work:

```text
M15 objective presentation != model language
M16 deterministic grounding != M19 rendered prose
M19 provenance != semantic correctness
M20 evaluator acceptance != objective chess truth
M21 participant orchestration != learner inference
M26 reviewed-coaching persistence != M8 explanation transition
M27 mechanical fidelity != retry/privacy/provider approval
M28 local semantic HTML != production UI/accessibility/usability approval
participant candidate selection != evidence-capture consent
```

Do not:

- invent universal `inaccuracy`, `mistake`, or `blunder` thresholds;
- convert mate/bounded/partial evidence into fake exact centipawn values;
- expose post-reveal diagnostic rationale as clean pre-reveal participant evidence;
- let M19 text overwrite M15/M16 objective/deterministic sections;
- let M20 verdicts become objective chess truth;
- persist credentials or production secrets in M26/M27 artifacts;
- add automatic retry authority merely because M24 marks timeout/transient failures as retryable;
- claim production accessibility/usability from M28 structural tests.

## 11. Human and external gates still open

Repository qualification does not close:

- end-user disclosure/capture-consent QA;
- production model/evaluator vendor selection;
- real credentials and secrets injection;
- privacy/security/data-transmission/retention approval;
- live timeout/retry/backoff/rate-limit behavior;
- latency/cost/billing/incident policy;
- model semantic/safety/pedagogical quality;
- evaluator completeness/correctness beyond the frozen M20 contract;
- real browser/device/screen-reader/localization/usability review;
- hosted authentication, tenancy, production persistence, deployment, and operations;
- empirical tutoring efficacy or causal learner claims.

## 12. Restart sequence for the next milestone

1. Fetch live `main` and recent commits.
2. Read `STATUS.md` and `docs/product/repository-build-status.md`.
3. Re-run the focused M26–M28 suites and full gate if repository state has changed materially.
4. Reconcile any new feature work before relying on this handoff.
5. Audit current bottlenecks and classify work as repository-only, hermetic validation, or external authority.
6. Propose a fresh bounded package queue before implementation.

Current recommendations, subject to that fresh audit:

1. persisted M26/M25 artifact -> M27-verified M28 reference bridge, eliminating manual M25 bundle assembly;
2. deterministic participant-scoped review-package navigation/export with content-addressed manifests;
3. hermetic secrets/redaction and retry-plan preflight using fake adapters only.
