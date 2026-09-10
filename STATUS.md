# Chess Mentor Engine — Milestone Handoff

**Handoff scope:** completed M17–M19 milestone / Packages 1–3  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Post-feature baseline:** `25672c1b375181b6eb48e4ee9c8283e16dc12665`  
**Prepared:** 2026-09-10  

This document is the durable handoff for the milestone that connected engine
analysis to presentation, added bounded diagnostic move selection, and introduced a
provenance-bound model-language layer. Use
[`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
for the moving implementation boundary and this file for the completed milestone
summary, qualification evidence, operational commands, and next-session priorities.

## Milestone outcome

All three queued packages are implemented, qualified on exact candidate heads, and
merged into `main`.

```text
Package 1 / M17  Analysis -> Presentation Bridge       MERGED - PR #49
Package 2 / M18  Diagnostic Move-Analysis Queue        MERGED - PR #50
Package 3 / M19  Provenance-Bound Mentor Coaching      MERGED - PR #51
```

The milestone advances the product path from isolated qualified components toward a
usable evidence chain:

```text
canonical PGN position
-> M3 engine evidence
-> M4 played-decision comparison / diagnostic selection
-> M15 UI-safe evaluation presentation
-> M16 deterministic grounded mentor feedback
-> M19 request-bound model-authored language
```

The authority boundaries remain intentional. Engine analysis, deterministic
presentation, learner evidence/inference, grounded feedback, model-authored prose,
and pedagogy are not collapsed into one opaque model decision.

## Package 1 — M17 Analysis -> Presentation Bridge

**PR:** #49  
**Final candidate head:** `c91ffa33a0797e0894f1f2dc519600be39f6afcc`  
**Merge commit:** `4672a2b5dc34cae736be8e260f439afe6acfb1e6`  
**CI run:** `34435288183`

Delivered:

- opt-in `cme analyze --with-presentation`;
- direct use of the exact in-memory M14/M3/M4 records by the qualified M15
  projector, with no JSON reconstruction layer;
- unchanged default M14 CLI output when the flag is absent;
- unchanged `m14.analysis-package.v1` archival contract;
- presentation construction before archival so projection rejection cannot leave a
  storage side effect;
- fail-closed coverage for score/fingerprint binding, Black decision-mover
  perspective and bound reversal, symbolic mate, played-child incompatibility, and
  tampered comparison evidence.

Qualification evidence:

```text
582 passed, 8 intentional external-engine skips
Focused M17 suite: 5 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

Operational example:

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --with-presentation
```

## Package 2 — M18 Diagnostic Move-Analysis Queue

**PR:** #50  
**Final candidate head:** `65297abd366bf092a60ed4fa202e2e51bb1950cd`  
**Merge commit:** `00bab82dc963bff005c9753b498f1e50a8c513d4`  
**CI run:** `34436086912`

Delivered:

- `cme diagnose` over one selected PGN game and an explicit inclusive played-ply
  window;
- reuse of qualified M3 analysis, M4 comparison, M4C signal derivation, M4D
  selection policy, and deterministic candidate-batch contracts;
- required explicit JSON `SelectionPolicy`, with no universal move-quality
  thresholds embedded in the CLI;
- complete auditable source-pool output plus native `DiagnosticCandidateBatch`;
- preservation of controls, quotas, per-game caps, exclusions, deterministic
  ordering, policy/source fingerprints, and explicit shortfalls;
- conservative handling of partial, failed, bounded, incompatible, and otherwise
  incomparable evidence;
- rejection coverage for invalid policy/range inputs and provenance/fingerprint
  drift.

Qualification evidence:

```text
589 passed, 8 intentional external-engine skips
Focused M18 suite: 7 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

One earlier M18 candidate failed Ruff on two E501 formatting findings. Those were
corrected without behavioral changes; the final head above passed the complete gate.

Operational example:

```bash
cme diagnose games.pgn \
  --game-index 0 \
  --start-ply 0 \
  --end-ply 30 \
  --policy ./selection-policy.json \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000
```

The selection-policy file must match the qualified M4 `SelectionPolicy` contract.
See [`docs/runbooks/m18-diagnostic-analysis-queue.md`](docs/runbooks/m18-diagnostic-analysis-queue.md).

## Package 3 — M19 Provenance-Bound Mentor Coaching

**PR:** #51  
**Final candidate head:** `f465a7f5355d8e9304a557cbbc26971d1aa18c27`  
**Merge commit:** `25672c1b375181b6eb48e4ee9c8283e16dc12665`  
**CI run:** `34436883416`

Delivered:

- provider-neutral `chess_mentor_engine.coaching` API;
- exact recomputation of the qualified M16 grounded-feedback record before model
  request construction;
- content-addressed M19 request containing exact M16 grounding plus a fingerprinted
  instruction/claim ceiling;
- explicit request ID/fingerprint echo and provider/model/version/run/timestamp
  provenance requirements;
- a model generation contract that accepts prose but not replacement M3/M4/M6/M7/M9
  structured records;
- M8 explanation recording with `actor_kind=model` and the exact M19 instruction
  fingerprint;
- provider request-mutation detection;
- explicit `request_bound_not_semantically_verified` status so provenance binding is
  not confused with semantic correctness;
- rejection coverage for request/instruction tampering, objective evidence drift,
  wrong request echo, blank/predating generation, provider failure/mutation, and
  invalid provider result types.

Qualification evidence:

```text
598 passed, 8 intentional external-engine skips
Focused M19 suite: 9 passed
Ruff: PASS
Editable package build/install: PASS
Independent Stockfish witness: 8/8 PASS, no skips
```

M19 intentionally does not freeze a production model provider, SDK, credentials
flow, retry/rate-limit policy, or semantic model-quality claim. See
[`docs/runbooks/m19-provenance-bound-model-coaching.md`](docs/runbooks/m19-provenance-bound-model-coaching.md).

## Validation / regression runbook

Install the package for development:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the focused milestone suites:

```bash
python -m pytest tests/test_m17_analysis_presentation_bridge.py
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
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

## Verified evidence and remaining gates

### Software qualification

No software qualification gate from this milestone remains pending. All three
packages were merged only after the exact final candidate head passed native tests,
Ruff, package installation, and the independent Stockfish job.

### Human QA / product approval

There is **no blocking human approval required to regard M17–M19 as software-
qualified**. The following remain intentionally unproven or product-level gates for
future work:

- semantic correctness and pedagogical quality of arbitrary model-generated prose;
- production model/provider selection and its cost/latency/privacy/credential policy;
- end-user UX quality for diagnostic review, presentation, and coaching flows;
- empirical tutoring efficacy and intervention-caused improvement;
- causal learner diagnosis, permanent weakness claims, mastery, or universal
  move-quality thresholds;
- production web/hosted multi-user architecture, authentication, and secrets
  management.

Those are not defects in the completed milestone; they are explicit claim ceilings.

## Recommended next priorities

The next milestone should preserve the current evidence contracts and attack the
remaining integration/validation gaps in this order:

1. **Model-output evaluation harness.** Build a deterministic/evaluator-facing
   qualification layer for M19 output that checks chess consistency against the
   exact M16 grounding, evidence sufficiency, overclaiming, uncertainty handling,
   and forbidden authority promotion. Keep provenance binding separate from semantic
   evaluation.
2. **Diagnostic-candidate -> tutor-session orchestration.** Define a bounded bridge
   from an exact selected M18 candidate into the existing M5/M8 capture/session path,
   with explicit user selection/consent and no automatic M6/M7 diagnosis. This closes
   the largest remaining workflow gap between move discovery and the mentor loop.
3. **Production provider adapter only after evaluation criteria exist.** Add one
   explicit model provider/transport behind the M19 protocol with versioned model
   identity, timeouts/retries, credential handling, cost/latency telemetry, and
   failure semantics. Provider adoption should not weaken the M16/M19 claim ceiling.

A later milestone can then evaluate a thin UI over these qualified workflows. Avoid
starting with a polished web UI before candidate-to-session orchestration and model-
output evaluation are inspectable.

## Restart instructions for a future engineer or chat session

1. Read this `STATUS.md`.
2. Read `CONTEXT.md` and `docs/product/repository-build-status.md`.
3. Confirm live `main` and recent commits before trusting the hashes in this handoff.
4. Run the focused M17–M19 suites and the full repository gate before modifying the
   evidence path.
5. Treat M16 as the deterministic mentor-grounding ceiling and M19 as a
   provenance-bound language layer, not as new objective/learner/pedagogy authority.
6. If starting a new milestone, audit the current repository first and propose
   bounded packages before implementation.

## Key references

- `README.md`
- `CONTEXT.md`
- `docs/product/repository-build-status.md`
- `docs/runbooks/m17-analysis-presentation-bridge.md`
- `docs/runbooks/m18-diagnostic-analysis-queue.md`
- `docs/runbooks/m19-provenance-bound-model-coaching.md`
- PR #49 — M17
- PR #50 — M18
- PR #51 — M19
