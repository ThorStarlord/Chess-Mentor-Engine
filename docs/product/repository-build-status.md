# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Contiguous numbered milestone boundary:** M34 — Reviewed-Coaching Recovery Reconciliation.  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7.  
**Qualified non-contiguous post-M34 packages:** M36, M39, M40, M41, M43, M44.  
**Current post-feature baseline:** `c8d28c235e2c2141ea96028835f360034051ea92`.

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
M43      contradiction/control evidence-acquisition candidate planning
M41      ontology-aware intervention candidate matching before M9 selection
M44      deterministic learner-progress presentation + local reference HTML
```

**M35, M37, M38, and M42 are not implemented merely because later-numbered packages
are qualified.** Their roadmap labels remain candidate-only.

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

A “full gate” means full repository pytest, Ruff, `compileall`, and the independent
Stockfish job on the exact final candidate head. Regular-job Stockfish skips are not
counted as the independent-engine witness.

## Current tutor-decision-loop chain

```text
M7/M7C current learner hypothesis + recurrence/contradiction authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal state
+ optional K7 semantic context
        |
        v
M36 m36.learner-state-read-model.v1
        |
        v
M39 m39.hypothesis-evidence-synthesis.v1
        |
        v
M40 m40.next-session-plan.v1
        |
        +-- CHALLENGE / CONTROL / COLLECT --> M43 evidence-acquisition candidates
        |
        +-- TEACH_CONCEPT ----------------> M41 intervention candidates
        |
        `----------------------------------> M44 learner-progress presentation
```

### M43 — contradiction/control evidence acquisition

M43 consumes exact M40 evidence-oriented proposals plus exact M39 state and an
explicit participant-local M7B candidate pool. It can preserve already-classified M7C
control material and rank additional evidence as **potential** review/reassessment
candidates.

It does not re-run M7C. Its claim ceiling is:

```text
decision_authority = candidate_only
m7c_effect = not_established
mastery = not_established
```

### M41 — ontology-aware intervention matching

M41 consumes exact M40 `TEACH_CONCEPT` proposals, M39 concept context, the exact
K0–K7 ontology snapshot, explicit semantic-profile sidecars, and the existing M9
intervention registry.

It can rank `eligible_candidate`, `possible_candidate`, `insufficient_information`,
and `ineligible` interventions without parsing training prose to manufacture ontology
semantics. Multiple eligible candidates remain multiple candidates.

Its claim ceiling is:

```text
selection_authority = not_exercised
efficacy = not_established
mastery = not_established
```

M9 remains applicability/selection authority.

### M44 — learner progress reference surface

M44 composes exact M36/M39/M40 sources plus optional exact M43/M41 artifacts into a
content-addressed presentation model and deterministic escaped HTML reference surface.

It can display current hypothesis state, evidence and counterevidence, ontology
concepts/recognition cues, M9/M10 training state, M39 uncertainty/change conditions,
M40 next-action proposals, and optional M43/M41 candidates.

M44 is `local_reference_presentation_only`: it creates no new inference, selection,
transfer, mastery, production frontend, or execution authority.

## Product-pulled ontology rule

The ontology is now shared semantic infrastructure rather than the primary workstream.
Do **not** create a generic K8 merely to expand vocabulary, detectors, relationships,
or pedagogy metadata.

Use this sequence instead:

```text
concrete learner/tutor consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum ontology extension
-> add ontology rejection tests
-> consume it in the requesting feature
-> qualify ontology + consumer together
```

M41 and M44 both qualified without any ontology schema or data expansion, showing that
the existing K0–K7 substrate is already useful without continual ontology churn.

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

M36/M39/M40/M41/M43/M44 currently expose Python APIs and/or deterministic local
reference surfaces; they add no production CLI command and do not automatically
execute tutoring or model calls.

## Qualification commands

Latest focused suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
python -m pytest tests/test_m41_intervention_matching.py -rs
python -m pytest tests/test_m43_evidence_acquisition.py -rs
python -m pytest tests/test_m44_learner_progress_reference.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`../runbooks/m41-m44-tutor-decision-loop.md`](../runbooks/m41-m44-tutor-decision-loop.md)
for the latest focused restart path.

## Current claim ceiling

The repository can now represent typed chess concepts, explain current learner state,
propose a next action, prepare challenge/control evidence candidates or teaching
intervention candidates for supported M40 seams, and present the resulting state in a
traceable local learner-progress surface.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- that an ontology concept occurrence proves what a participant noticed or missed;
- automatic creation or mutation of M7/M11 state from derived learner-intelligence
  artifacts;
- that M43 can replace M7C recurrence classification;
- that an M41 candidate is an M9 applicability mapping or selected intervention;
- that a proposed or scheduled transfer test constitutes M10 transfer evidence;
- mastery from successful evidence, practice, transfer, or real-game observation;
- empirically optimal M40/M41/M43 policies;
- production browser/device/accessibility/usability quality for M44;
- semantic correctness/safety/pedagogical quality of arbitrary model prose;
- production provider/vendor, retry/idempotency, privacy/security, auth, hosted
  persistence, deployment, or empirical tutoring efficacy.

## Core boundaries to preserve

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping
M41 rank != M9 selection
M44 rendering != learner inference
M40 transfer-test proposal != M10 transfer evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Next likely build directions

A future milestone should begin with live-main reconciliation before promoting any
candidate into an approved queue. Current strongest candidates are:

1. **M42 — transfer/retest planning:** consume M40 near/far-transfer proposals and
   create bounded plans while leaving actual outcomes to M10;
2. **M45 — batch games -> mentor queue:** prioritize a bounded recent-game set by
   learner relevance, contradiction value, transfer value, uncertainty, and novelty;
3. **M46 — adaptive Socratic tutor:** use qualified learner evidence, ontology
   recognition cues, and bounded pedagogical actions while keeping model language
   downstream of deterministic evidence;
4. **M35/M37 only when a concrete consumer blocker pulls them forward.**

Do not create a second recurrence engine under M38; reuse M7C. Do not create a generic
K8 without a concrete consumer semantic gap.
