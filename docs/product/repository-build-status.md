# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Contiguous numbered milestone boundary:** M34 — Reviewed-Coaching Recovery Reconciliation.  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7.  
**Qualified non-contiguous post-M34 packages:** M36, M39, M40.  
**Current post-feature baseline:** `a10cdd36925af9a09a4e10c56fa7913bddba0f44`.

This file is the moving repository authority. `STATUS.md` is the latest handoff;
feature/program runbooks preserve qualification history. Software qualification is
not empirical tutoring efficacy.

## Qualified capability map

```text
M1–M4    canonical chess evidence, deterministic features, engine evidence,
         played-decision comparison and diagnostic selection
M5–M7    participant evidence, reasoning discrepancy, learner hypothesis and
         M7C recurrence/contradiction authority
M8–M11   controlled tutoring, intervention selection, bounded outcome/transfer
         evidence, append-only longitudinal learner state
M12–M18  local/operator tooling, persistence, engine-backed analysis,
         presentation, deterministic mentor grounding, diagnostic queues
M19–M22  model-language provenance, bounded evaluator judgment, candidate launch,
         cross-layer fidelity
M23–M30  persistent reviewed-coaching runtime, verification, local review,
         participant-scoped navigation/export
M31–M34  privacy/retry preflight, consumer fidelity, deterministic traceability,
         hermetic recovery reconciliation
K0–K7    typed chess semantic ontology, assertions, conservative detectors,
         M19 sidecar context, M7C-preserving learner projection
M36      deterministic current learner-state read model
M39      deterministic current hypothesis evidence synthesis
M40      transparent teaching-priority / next-session proposal policy
```

**M35, M37, and M38 are not implemented merely because later-numbered packages are
qualified.** Their roadmap labels remain candidate-only.

## Recent promotion provenance

| Package | Final head | Merge commit | Qualification |
| --- | --- | --- | --- |
| K0–K2 / PR #75 | `5e76400ed0df80ad845c07bfdedec08e3c46af45` | `f52b3773b773883d1ac9f476d563c70433bdeb63` | run `34590630613`: full gate PASS |
| K3 / PR #76 | `ecd5bf19517d9e8a657f1c2f1044596bc5e3f88b` | `a0c6dcb01060e84f2b9ac1b517a39873720a4b7a` | run `34591111549`: full gate PASS |
| K4 / PR #77 | `2d7537b260007613b81e720be683b531b2f8bc55` | `fd43a0a416aceb33444b7f2b62edf1d2e5767872` | run `34591799180`: full gate PASS |
| K5 / PR #78 | `be0cffdbe73c3b37e998ea805f87ae7a80493cf8` | `b417d170b69de271635fb24b666bea2f6f290d2e` | run `34592343696`: full gate PASS |
| K6 / PR #79 | `eb3dcc7a06485a40c6a9fdcd9a2429c16a597bdf` | `8653b058e2ed7af598a80c9293bbc51d3e5da2bf` | run `34592709220`: full gate PASS |
| K7 / PR #80 | `f4cb0721d9769b067985d253be4659e8ccd888bd` | `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c` | run `34595432067`: full gate PASS |
| M36 / PR #82 | `8632a743fda30b4262e9007e9e48c79ca8d9283f` | `d4631a8094d11454346e6703ec9dab0f06fedbb8` | run `34599051912`: full gate PASS |
| M39 / PR #83 | `6d5a8954170129c920fbc9b09be27ab0f6315a72` | `43ecdaa00a0d2abdf72d1f0f88f4254cd86f05dd` | run `34599807350`: 871 passed + Ruff/compile/Stockfish PASS |
| M40 / PR #84 | `78f3658a9e8ef7643c3a6e1f06f62bf2e674574b` | `a10cdd36925af9a09a4e10c56fa7913bddba0f44` | run `34600739442`: 889 passed + Ruff/compile/Stockfish PASS |

A “full gate” means full repository pytest, Ruff, `compileall`, and the independent
Stockfish job on the exact final candidate head. Regular-job Stockfish skips are not
counted as the independent-engine witness.

## Current learner-intelligence chain

```text
M7/M7C current learner hypothesis authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal state
+ optional K7 semantic context
        |
        v
M36 m36.learner-state-read-model.v1
        |
        + exact current M7 revision / M7C assessment
        + optional exact K7 projection
        v
M39 m39.hypothesis-evidence-synthesis.v1
        |
        + m40.next-session-policy.v1
        v
M40 m40.next-session-plan.v1
```

### M36 — current learner-state read model

M36 provides one deterministic participant-scoped view of current learner evidence.
It may expose current hypothesis statement/scope/status, unresolved alternatives,
M9 selection references, M10 outcome dimensions, M11 lifecycle, and optional K7
concept context.

M36 is a read model only; it does not mutate M7/M11 or select M9 training.

### M39 — hypothesis evidence synthesis

M39 provides one deterministic explanation package for an exact current M7C
assessment. It preserves every recurrence-unit relation and relevant source/review
identity, may attach exact K7 context, and explicitly surfaces evidence gaps and
bounded future-change conditions.

M39 does not calculate a new recurrence status. M7C remains authoritative.

### M40 — teaching-priority / next-session proposal

M40 produces a transparent ranked proposal over active current hypotheses under an
explicit versioned policy. The action vocabulary is:

```text
COLLECT_NEW_EVIDENCE
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
TEACH_CONCEPT
ASSIGN_PRACTICE
RUN_NEAR_TRANSFER_TEST
RUN_FAR_TRANSFER_TEST
WAIT_FOR_REAL_GAME_EVIDENCE
```

The default policy prefers challenge/control work for contradicted or one-sided
hypotheses, refuses to override mixed M9 selection state, and advances selected
interventions through practice and transfer stages only when current M10/M11 evidence
supports the transition.

M40 has `decision_authority = proposal_only`.

## Current operational surfaces

Existing installed commands remain:

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

M36/M39/M40 currently expose Python API / deterministic-hermetic surfaces and add no
new production CLI command. They do not automatically execute tutoring or model calls.

## Qualification commands

Latest focused suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`../runbooks/m36-m40-learner-intelligence.md`](../runbooks/m36-m40-learner-intelligence.md).

## Current claim ceiling

The repository can now represent typed chess concepts, project them beside learner
evidence, summarize current learner state, explain the evidence for one current
hypothesis, and propose a next action class under an inspectable policy.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- that an ontology concept occurrence proves what a participant noticed or missed;
- automatic creation or mutation of M7/M11 state from M36/M39/M40;
- that M39 can replace M7C recurrence classification;
- that M40 can replace M9 intervention selection;
- that a proposed transfer test constitutes M10 transfer evidence;
- mastery from practice, transfer, or real-game observation;
- that the M40 default policy is empirically optimal;
- semantic correctness/safety/pedagogical quality of arbitrary model prose;
- production provider/vendor, retry/idempotency, privacy/security, auth, hosted
  persistence, deployment, or production UI authority;
- empirical tutoring efficacy.

## Core boundaries to preserve

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M40 action proposal != M9 intervention selection
M40 transfer-test proposal != M10 transfer evidence
WAIT_FOR_REAL_GAME_EVIDENCE != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Next likely build directions

A future milestone should begin with live-main reconciliation before promoting any
candidate into an approved queue. Current strongest candidates are:

1. M43 contradiction/control evidence acquisition for M40 challenge/control actions;
2. M41 intervention matching for supported teaching needs, preserving M9 authority;
3. M42 near/far transfer test planning, preserving M10 outcome authority;
4. M44 local learner-progress surface over M36/M39/M40;
5. M35/M37 consumer/operator work only if a concrete consumer blocker pulls it
   forward.

Do not create a second recurrence engine under M38; reuse M7C.
