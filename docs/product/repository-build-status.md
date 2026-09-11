# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current main baseline:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`.  
**Contiguous numbered milestone boundary:** M34.  
**Qualified semantic program:** Chess Knowledge Ontology K0-K7.  
**Qualified post-M34 packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46.  
**Integrated V1 local consumer:** PR #94 / `cme-local-tutor`.

This file is the moving repository authority. `STATUS.md` is the restart handoff. Software qualification is not empirical tutoring efficacy.

## Qualified capability map

```text
M1-M4    canonical chess evidence, deterministic features, engine evidence,
         played-decision comparison and diagnostic selection
M5-M7    participant evidence, reasoning discrepancy, learner hypothesis and
         M7C recurrence/contradiction authority
M8-M11   controlled tutoring, intervention selection, bounded outcome/transfer
         evidence, append-only longitudinal learner state
M12-M18  local/operator tooling, persistence, engine-backed analysis,
         presentation, deterministic mentor grounding, diagnostic queues
M19-M22  model-language provenance, bounded evaluator judgment, candidate launch,
         cross-layer evaluation fidelity
M23-M30  persistent reviewed-coaching runtime, verification, local review,
         participant-scoped navigation/export
M31-M34  privacy/retry preflight, consumer fidelity, deterministic traceability,
         hermetic recovery reconciliation
K0-K7    typed chess semantic ontology, assertions, conservative detectors,
         M19 sidecar context, M7C-preserving learner projection
M36      deterministic current learner-state read model
M39      deterministic current hypothesis evidence synthesis
M40      transparent teaching-priority / next-session proposal policy
M43      contradiction/control evidence-acquisition candidate planning
M41      ontology-aware intervention candidate matching before M9 selection
M42      bounded near/far transfer and retest planning before M10 outcomes
M44      deterministic learner-progress presentation + local reference HTML
M45      participant-scoped bounded mentor queue over M4D candidates
M46      adaptive Socratic tutor-action proposal over the exact M8 lifecycle
V1       deterministic local composition from exact M18/M44/(optional M42)
         artifacts through M45 -> M23/M8 -> M46 proposal
```

**M35, M37, and M38 remain unimplemented labels.** K8 is not an active semantic program.

## Latest integration provenance

| Package | Final head | Merge commit | Qualification |
| --- | --- | --- | --- |
| M42 / PR #90 | `4df41644b4b5ffdd9abf54d349b7048f0e514078` | `c8af423f37c9ad7a423594ffa5d43f83c2b2d4ab` | run `34623130217`: 925 passed + Ruff/compile/Stockfish PASS |
| M45 / PR #91 | `0af40490d9a7a70699b1d015d65a53fb86af66f2` | `725de02a27c836e7fe150cc3874482cf45511444` | run `34624375982`: full pytest/Ruff/compile/Stockfish PASS |
| M46 / PR #92 | `cc89c5cf1402d02cadf76fa0d80c903296d51aea` | `3ec19446b4957d4e8f20ed3865b7d090d55c3cb5` | run `34629592288`: 939 passed + Ruff/compile/Stockfish PASS |
| V1 local tutor / PR #94 | `9867105509e0f243a7823066d626abe1cad40148` | `2fd14c32e81d19222cc3e2f332337c00f8086f5f` | run `34642933193`: 948 passed, Ruff/compile PASS; independent Stockfish 8/8 |

A full gate means full repository pytest, Ruff, `compileall`, and the independent Stockfish job on the exact final candidate head. Regular-job Stockfish skips are not the independent-engine witness.

## Current learner/tutor decision loop

```text
M7/M7C learner hypothesis + recurrence/contradiction authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal state
+ optional K7 semantic context
        |
        v
M36 -> M39 -> M40
        |
        +-- challenge/control/collect --> M43 evidence candidates
        +-- teach concept ------------> M41 intervention candidates
        +-- transfer -----------------> M42 transfer/retest plan
        `------------------------------> M44 learner-progress presentation

exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 plan(s)
        |
        v
cme-local-tutor composition
        |
        v
M45 mentor queue
        |
        v
explicit selection + capture consent
        |
        v
M23 -> exact persisted M8 checkpoint
        |
        v
M46 next-action proposal
        |
        v
existing M8 commands remain execution / exposure / capture / reveal authority
```

## V1 local consumer claim ceiling

The local consumer is composition-only. It does not create learner claims from engine evidence, exercise M9 selection, create M10 outcomes, or bypass M8 measurement boundaries.

```text
orchestration_authority = composition_only
learner_effect = not_established
mastery = not_established
```

Fail-closed coverage includes invalid M18 integrity, tampered/stale M44 identity, participant drift, ambiguous/mismatched M42 plans, declined selection or capture consent, active-session/queue drift, and out-of-scope session artifacts.

## Current operational surfaces

Installed commands include:

```text
cme
cme-local-tutor
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

Principal local workflow commands include:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-local-tutor start|next
```

M36/M39/M40/M41/M42/M43/M44/M45/M46 remain Python APIs and/or deterministic local reference surfaces. `cme-local-tutor` is the V1 composition surface, not a hosted runtime.

## Qualification commands

Focused V1 local-consumer suites:

```bash
python -m pytest tests/test_v1_local_tutor_workflow.py -rs
python -m pytest tests/test_v1_local_tutor_authority_edges.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

See [`../runbooks/v1-local-tutor-vertical-slice.md`](../runbooks/v1-local-tutor-vertical-slice.md) for the current local-consumer restart path.

## Current claim ceiling

The repository can represent typed chess concepts, preserve exact engine evaluation semantics, explain current learner state, synthesize support/counterevidence, propose actions, prepare evidence/intervention/transfer candidates, present progress, prioritize bounded participant review, persist controlled tutor state, and deterministically compose those authorities into a local V1 tutor workflow.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- ontology occurrence as proof of participant perception or learner weakness;
- automatic M7/M11 mutation from derived artifacts;
- M43 candidates as M7C classifications;
- M41 candidates as M9 selections;
- M42 plans as M10 outcomes or transfer success;
- M45 rank as learner diagnosis or optimal review order;
- M46 proposal as tutoring execution or uncontaminated participant evidence;
- mastery from practice/transfer/real-game evidence;
- empirically optimal tutoring policies;
- production browser/device/accessibility/usability quality;
- semantic/pedagogical quality of arbitrary model prose;
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
V1 composition != upstream authority
M45 rank one != implicit consent
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Version 1.0 readiness

The architecture/coherent-local-consumer blocker is resolved. The remaining repository-resolvable V1 blocker is **Release Candidate & Distribution Qualification**:

1. synchronize package/repository release identity to the V1 candidate;
2. build distributable artifact(s);
3. clean-install into a fresh environment;
4. smoke promised CLI entry points and packaged ontology/data assets;
5. add the clean-install witness to release qualification;
6. preserve full pytest, Ruff, compileall, and independent Stockfish qualification.

Do not claim `VERSION_1_REPOSITORY_READY` until that package is complete. Do not substitute M35/M37/M38/K8/M47 or optional product expansion for this remaining release task.
