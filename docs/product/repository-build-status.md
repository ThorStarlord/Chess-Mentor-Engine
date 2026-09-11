# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Contiguous numbered milestone boundary:** M34 — Reviewed-Coaching Recovery Reconciliation.  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7.  
**Qualified non-contiguous post-M34 packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46.  
**Current post-feature baseline:** `3ec19446b4957d4e8f20ed3865b7d090d55c3cb5`.

This file is the moving repository authority. `STATUS.md` is the latest handoff; feature/program runbooks preserve qualification history. Software qualification is not empirical tutoring efficacy.

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
M43      contradiction/control evidence-acquisition candidate planning
M41      ontology-aware intervention candidate matching before M9 selection
M42      bounded near/far transfer and retest planning before M10 outcomes
M44      deterministic learner-progress presentation + local reference HTML,
         including additive M42 transfer-plan presentation
M45      participant-scoped bounded mentor queue over M4D candidates
M46      adaptive Socratic tutor-action proposal over the exact M8 lifecycle
```

**M35, M37, and M38 remain unimplemented labels.** Later-numbered qualified packages do not reserve or imply them. K8 is not an active semantic program.

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
| M43 / PR #86 | `70728729905f69beed2f608ec02ddd94c1e9cfbf` | `a9552ee745d2bce862f2e94eb5ca9320870defbf` | run `34608614837`: 896 passed + Ruff/compile/Stockfish PASS |
| M41 / PR #87 | `a1fd0cfb6455a68ac5ea10390e7840009a3c0be3` | `8aefe1183ce2623e50b3f732fc7de26164f4a014` | run `34610142609`: 904 passed + Ruff/compile/Stockfish PASS |
| M44 / PR #88 | `cdbf50c9af3154f940b0c575893a1ae51309e612` | `c8d28c235e2c2141ea96028835f360034051ea92` | run `34611475360`: 912 passed + Ruff/compile/Stockfish PASS |
| M42 / PR #90 | `4df41644b4b5ffdd9abf54d349b7048f0e514078` | `c8af423f37c9ad7a423594ffa5d43f83c2b2d4ab` | run `34623130217`: 925 passed + Ruff/compile/Stockfish PASS |
| M45 / PR #91 | `0af40490d9a7a70699b1d015d65a53fb86af66f2` | `725de02a27c836e7fe150cc3874482cf45511444` | run `34624375982`: full pytest/Ruff/compile/Stockfish PASS |
| M46 / PR #92 | `cc89c5cf1402d02cadf76fa0d80c903296d51aea` | `3ec19446b4957d4e8f20ed3865b7d090d55c3cb5` | run `34629592288`: 939 passed + Ruff/compile/Stockfish PASS |

A “full gate” means full repository pytest, Ruff, `compileall`, and the independent Stockfish job on the exact final candidate head. Regular-job Stockfish skips are not counted as the independent-engine witness.

## Current learner/tutor decision loop

```text
M7/M7C current learner hypothesis + recurrence/contradiction authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal state
+ optional K7 semantic context
        |
        v
M36 learner-state read model
        |
        v
M39 evidence synthesis
        |
        v
M40 next-session proposal
        |
        +-- CHALLENGE / CONTROL / COLLECT --> M43 evidence candidates
        +-- TEACH_CONCEPT ----------------> M41 intervention candidates
        +-- RUN_*_TRANSFER_TEST ----------> M42 transfer/retest plan
        `----------------------------------> M44 learner-progress presentation

M4D bounded diagnostic batch + explicit participant scope
        |
        v
M45 mentor queue
        |
        v
M8 controlled tutor lifecycle
+ optional exact M44/M45/M42 context
        |
        v
M46 next pedagogical-action proposal
        |
        v
M8 remains execution / exposure / capture / reveal authority
```

### M42 — transfer/retest planning

M42 is planning-only. It selects from explicit bounded near/far transfer candidates and preserves exact M40/M9 identities. Candidate definitions state semantic relation, surface variation, freshness, held constants, varied dimensions, and provenance. Exact practice replay is rejected with M10-compatible reuse keys.

```text
M42 transfer plan != M10 transfer evidence
no eligible candidate != weakened policy
planned/completed != successful transfer
successful transfer != mastery
```

### M45 — mentor queue

M45 adds explicit participant scope around an M4D diagnostic batch and ranks a bounded queue using separate transparent ordinal dimensions. Learner relevance, contradiction/control value, transfer value, and uncertainty reduction can outrank ordinary engine severity.

It does not create a learner diagnosis, re-run M7C, select an intervention, create M10 evidence, or claim an optimal review order.

### M46 — adaptive Socratic tutor proposal

M46 chooses one bounded next tutoring action from exact M8 session state and exact learner context without executing the action.

Pre-freeze M8 evidence remains protected: no M46 adaptive hint/reveal is allowed before planned baseline capture is frozen. Assisted responses and post-reveal reflection remain separate evidence classes.

M46 may consume exact M44 context, optional M45 queue/item context, and optional M42 transfer plans. Transfer tutoring requires the exact current M42 plan.

Every proposal records:

```text
execution_authority = proposal_only
model_language = not_generated
mastery = not_established
```

M8 remains the actual tutor execution/exposure/capture/reveal authority.

## Product-pulled ontology rule

The ontology is shared semantic infrastructure rather than the primary workstream. M42/M45/M46 all qualified without a generic K8.

Do **not** create a generic K8 merely to expand vocabulary, detectors, relationships, or pedagogy metadata.

```text
concrete consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum extension
-> add rejection tests
-> consume it in the requesting feature
-> qualify ontology + consumer together
```

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

M36/M39/M40/M41/M42/M43/M44/M45/M46 expose Python APIs and/or deterministic local reference surfaces; they add no new production CLI or hosted runtime.

## Qualification commands

Latest focused suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
python -m pytest tests/test_m41_intervention_matching.py -rs
python -m pytest tests/test_m42_transfer_retest_planning.py -rs
python -m pytest tests/test_m42_m44_transfer_reference.py -rs
python -m pytest tests/test_m43_evidence_acquisition.py -rs
python -m pytest tests/test_m44_learner_progress_reference.py -rs
python -m pytest tests/test_m45_batch_mentor_queue.py -rs
python -m pytest tests/test_m46_adaptive_socratic_tutor.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`../runbooks/m42-m46-learner-tutor-loop.md`](../runbooks/m42-m46-learner-tutor-loop.md) for the latest restart path.

## Current claim ceiling

The repository can now represent typed chess concepts, explain current learner state, synthesize support/counterevidence, propose a next learning action, prepare evidence/intervention/transfer candidates, present current progress, prioritize a bounded participant review queue, and propose bounded adaptive tutoring actions while preserving M8 measurement boundaries.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- ontology occurrence as proof of participant perception or learner weakness;
- automatic M7/M11 mutation from derived learner-intelligence artifacts;
- M43 candidates as M7C classifications;
- M41 candidates as M9 applicability mappings or selections;
- M42 plans as M10 outcomes or transfer success;
- M45 rank as learner diagnosis or optimal review order;
- M46 proposal as tutoring execution or uncontaminated participant evidence;
- mastery from practice/transfer/real-game evidence;
- empirically optimal M40–M46 policies;
- production browser/device/accessibility/usability quality;
- semantic correctness/safety/pedagogical quality of arbitrary model prose;
- production provider/vendor, retry/idempotency, privacy/security, auth, hosted persistence, deployment, or empirical tutoring efficacy.

## Core boundaries to preserve

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping or selection
M42 plan != M10 outcome evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis / M9 selection
M46 proposal != M8 execution / exposure authority
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Next build decision

A future milestone must begin with fresh live-main reconciliation. **Do not automatically create another backend package.** The strongest current decision is between:

1. a concrete local end-to-end consumer that makes the qualified loop directly exercisable (`recent games -> M45 queue -> M8/M46 tutoring -> reflection -> M42/M10 retest`); and
2. M47 bounded multi-session study-plan composition, only if composing several qualified actions is the actual product bottleneck.

M35/M37 should move only when a concrete consumer/operator compatibility blocker requires them. M38 must not become a second recurrence engine; reuse M7C. K8 remains product-pulled.
