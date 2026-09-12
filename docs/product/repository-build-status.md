# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**V1 implementation baseline:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`.  
**Version 1.0 state:** `INTEGRATED / CURRENT-MAIN AUTHORITY`.  
**Release identity:** `chess-mentor-engine==1.0.0`.  
**Contiguous numbered milestone boundary:** M34.  
**Qualified semantic program:** Chess Knowledge Ontology K0-K7.  
**Qualified post-M34 packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46.  
**Integrated V1 packages:** PR #94 local tutor, PR #95 authority reconciliation, PR #96 release/distribution.

This file is the moving repository authority. `STATUS.md` is the restart handoff. Software
qualification is not production approval or empirical tutoring efficacy.

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
V1       local composition + repository-authority reconciliation + qualified
         1.0.0 wheel/sdist clean-install distribution contract
```

**M35, M37, and M38 remain unimplemented labels.** K8 is not an active semantic program.
Their absence does not make Version 1.0 incomplete.

## V1 integration provenance

| Package | PR | Final head | Merge commit | Qualification |
| --- | --- | --- | --- | --- |
| Local tutor vertical slice | #94 | `9867105509e0f243a7823066d626abe1cad40148` | `2fd14c32e81d19222cc3e2f332337c00f8086f5f` | run `34642933193`: 948 passed + Ruff/compile + independent Stockfish 8/8 |
| Authority reconciliation | #95 | `f12758c52de3e13468774d13c324510d48e6d7d7` | `c41fda2f1c3c2002a4c960270b38ef3cce1ad144` | exact candidate source + Stockfish jobs PASS |
| Release/distribution | #96 | `4b5512a1b5d67ad0df43000898b5d371701d832c` | `8e3abf063b2af7d09a46495f5e35c85c86d58f01` | PR run `34673791962` PASS; post-merge main run `34673834249` PASS |

The final Package 3 candidate and resulting integration commit both passed all
package-defined jobs:

```text
test-and-lint          PASS
release-distribution   PASS
stockfish-integration  PASS
```

The final source suite reported **957 passed, 8 intentional regular-job Stockfish skips**,
then Ruff PASS and compileall PASS. The independent Stockfish job remains the actual
real-engine witness.

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

## Qualification commands

Focused V1 suites:

```bash
python -m pytest tests/test_v1_local_tutor_workflow.py -rs
python -m pytest tests/test_v1_local_tutor_authority_edges.py -rs
python -m pytest tests/test_v1_release_distribution.py -rs
python -m pytest tests/test_package.py -rs
```

Full source and independent-engine gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Release distribution qualification:

```bash
python -m pip install "build>=1.2,<2" "setuptools>=68"
python -m build --no-isolation --wheel --sdist --outdir dist
python -m tools.release_qualification \
  --wheel dist/chess_mentor_engine-1.0.0-py3-none-any.whl \
  --sdist dist/chess_mentor_engine-1.0.0.tar.gz \
  --expected-version 1.0.0
```

See [`../runbooks/v1-post-milestone-handoff.md`](../runbooks/v1-post-milestone-handoff.md)
for the complete restart and clean-install witness.

## Current claim ceiling

The repository can mechanically establish deterministic local composition,
provenance/identity checks, authority preservation, engine-to-consumer evaluation
fidelity, hermetic workflow behavior, and distributable-artifact integrity.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- mastery or intervention-caused improvement;
- empirically optimal tutoring policies;
- production browser/device/accessibility/usability quality;
- production provider/vendor, privacy/security, auth, hosted persistence, or deployment;
- successful public artifact publication;
- real-participant usefulness or product approval.

## Core boundaries to preserve

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 selection
M42 plan != M10 outcome evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis / implicit consent
M46 proposal != M8 execution / exposure authority
successful evidence case != mastery
repository release qualification != hosted-product approval
```

## Version 1.0 readiness

`VERSION_1_REPOSITORY_READY` is established for the `main` lineage by the integrated
Package 3 release/distribution contract plus successful exact-candidate and post-merge CI.
There is no remaining repository-resolvable Version 1.0 package.

Future work begins a new milestone and must be justified by a concrete post-V1 product,
distribution, external-validation, or productization objective. Do not automatically
promote M35/M37/M38/K8/M47 or generic expansion into the next queue.
