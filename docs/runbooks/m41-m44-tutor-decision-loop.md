# M41–M44 Tutor Decision Loop — Restart and Qualification Runbook

**Scope:** qualified post-M40 consumer layer covering M43 evidence acquisition, M41 intervention matching, and M44 learner-progress reference presentation.  
**Baseline before this closeout:** `c8d28c235e2c2141ea96028835f360034051ea92` (M44 merge).  
**Authority:** this runbook explains how to restart and qualify the current implementation; `docs/product/repository-build-status.md` remains the moving implementation authority.

## 1. Purpose

The repository now has a bounded deterministic chain from current learner evidence to a proposed next action and then to concrete candidate consumers:

```text
M7/M7C current learner hypothesis / recurrence authority
+ M9 intervention selection evidence
+ M10 practice / transfer evidence
+ M11 longitudinal learner state
+ optional K7 semantic projection
        |
        v
M36 current learner-state read model
        |
        v
M39 current hypothesis evidence synthesis
        |
        v
M40 ranked next-action proposal
        |
        +---------------------------+
        |                           |
        v                           v
M43 evidence-acquisition        M41 intervention-candidate matching
for challenge/control           for teaching needs
        \                           /
         \                         /
          +-----------+-----------+
                      |
                      v
M44 deterministic learner-progress view
+ local static HTML reference surface
```

M43 and M41 are **candidate-preparation consumers**. They do not inherit M7C or M9 authority. M44 is a deterministic presentation layer and does not become a new learner-inference or execution layer.

## 2. Qualified packages

### M43 — contradiction/control evidence acquisition

**PR:** #86  
**Final head:** `70728729905f69beed2f608ec02ddd94c1e9cfbf`  
**Merge commit:** `a9552ee745d2bce862f2e94eb5ca9320870defbf`  
**CI run:** `34608614837`  
**Final regular suite:** 896 passed, 8 expected Stockfish skips; Ruff and compileall passed; independent Stockfish job passed.

M43 accepts exact M40/M39 state plus participant-local M7B evidence links and produces a content-addressed evidence-acquisition plan. It supports the M40 actions:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

It may rank additional exact-current participant evidence for later review/reassessment, while preserving already-classified M7C contradiction/counterexample/context-exception units as upstream truth.

**M43 must not:**

- create or mutate M7/M11 state;
- recalculate M7C recurrence status;
- promote a candidate to contradiction/counterexample authority;
- infer mastery from successful evidence;
- authorize execution.

### M41 — ontology-aware intervention matching

**PR:** #87  
**Final head:** `a1fd0cfb6455a68ac5ea10390e7840009a3c0be3`  
**Merge commit:** `8aefe1183ce2623e50b3f732fc7de26164f4a014`  
**CI run:** `34610142609`  
**Final regular suite:** 904 passed, 8 expected Stockfish skips; Ruff and compileall passed; independent Stockfish job passed.

M41 consumes an exact M40 `TEACH_CONCEPT` proposal, exact M39 synthesis, exact ontology identity, the existing M9 intervention registry, and versioned semantic-profile sidecars. It returns a deterministic candidate set using explicit semantic fields rather than free-text similarity.

Matching may use:

- target concept IDs;
- reinforcement concept IDs;
- contraindication concept IDs;
- ontology pedagogy training modes;
- explicit unverified prerequisite concepts.

**M41 must not:**

- exercise M9 selection authority;
- manufacture applicability mappings from free text;
- claim the highest-ranked candidate is effective or optimal;
- infer prerequisite mastery/deficiency;
- mutate learner state.

The existing K0–K7 ontology was sufficient for M41. No K8 or generic ontology expansion was required.

### M44 — learner-progress reference surface

**PR:** #88  
**Final head:** `cdbf50c9af3154f940b0c575893a1ae51309e612`  
**Merge commit:** `c8d28c235e2c2141ea96028835f360034051ea92`  
**CI run:** `34611475360`  
**Final regular suite:** 912 passed, 8 expected Stockfish skips; Ruff and compileall passed; independent Stockfish job passed.

M44 creates:

```text
m44.learner-progress-view.v1
m44.learner-progress-reference-surface.v1
```

The presentation model composes exact M36/M39/M40 state plus optional exact M43 and M41 artifacts. It preserves M40 priority order, exposes M7C status and evidence, displays M9/M10 state without mastery promotion, resolves ontology preferred names/recognition cues under an exact ontology fingerprint, and makes missing optional layers explicit.

The renderer is a separate deterministic static-HTML layer with escaping and no external scripts/assets.

**M44 must not:**

- create a learner hypothesis;
- classify recurrence;
- select an intervention;
- establish efficacy, transfer, or mastery;
- authorize M40/M43/M41 execution;
- claim production browser, accessibility, usability, authentication, or privacy quality.

## 3. Product-pulled ontology rule

The ontology is now a qualified shared semantic substrate, not an independent roadmap that should expand by default.

Use this rule:

```text
consumer need
-> identify missing semantic contract
-> prove current K0-K7 vocabulary/schema is insufficient
-> add the minimum ontology change required by that consumer
-> qualify downstream behavior
```

Do **not** create a generic K8 milestone merely to add more chess concepts. M41 and M44 both proved that existing K0–K7 semantics were sufficient for their current product needs.

## 4. Core authority invariants

Preserve all of the following:

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
motif present != participant noticed motif
motif missed != stable learner weakness
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/counterexample truth
M41 intervention candidate != M9 selected intervention
M41 semantic similarity != intervention efficacy
M44 presentation != new inference authority
M40/M43/M41 proposed action != execution
M10 transfer evidence != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model-authored prose
M20 evaluator acceptance != objective chess truth
```

## 5. Focused qualification commands

Run the latest learner-intelligence consumer suites:

```bash
python -m pytest tests/test_m36_learner_state_read_model.py -rs
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest tests/test_m40_next_session_planner.py -rs
python -m pytest tests/test_m43_evidence_acquisition.py -rs
python -m pytest tests/test_m41_intervention_matching.py -rs
python -m pytest tests/test_m44_learner_progress_reference.py -rs
```

Run ontology regression whenever a consumer touches semantic identities or pedagogy metadata:

```bash
python -m pytest \
  tests/test_chess_knowledge_ontology.py \
  tests/test_chess_knowledge_assertions.py \
  tests/test_chess_knowledge_detectors.py \
  tests/test_chess_knowledge_projection.py \
  tests/test_chess_knowledge_learner_projection.py -rs
```

## 6. Full merge gate

Every candidate head must pass all gates on that exact final head:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Regular-job Stockfish skips are expected when the executable is not supplied. They are not a substitute for the independent Stockfish qualification job.

If any amendment is pushed after a successful run, re-run the complete gate on the amended head. Do not reuse an earlier green result.

## 7. Restart procedure

1. Fetch live `main`; do not trust hashes in this runbook without checking.
2. Read, in order:
   - `docs/product/repository-build-status.md`;
   - `STATUS.md`;
   - `README.md`;
   - `CONTEXT.md`;
   - `docs/architecture/architecture.md`;
   - `docs/product/chess-mentor-engine-repository-build-plan.md`;
   - this runbook.
3. Run the focused M36/M39/M40/M43/M41/M44 suites.
4. Run ontology regressions if the proposed package consumes or changes ontology semantics.
5. Identify the true current product blocker before promoting a roadmap candidate.
6. Keep the work bounded and explicitly classify it as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`.
7. Merge only after exact-head full qualification.
8. Reconcile moving documentation authorities after the feature merge.

## 8. Recommended next strategic center

The next milestone should begin with a fresh live-main audit. Current highest-value candidates are:

1. **M42 — bounded transfer/retest scheduler.** Consume M40 near/far-transfer proposals and produce test plans without creating M10 outcome evidence.
2. **M45 — batch games to mentor queue.** Build a bounded consumer that turns batches of qualified game/evidence artifacts into inspectable learner-intelligence work queues without manufacturing hypotheses.
3. **M46 — adaptive Socratic tutor.** Consume qualified learner state, evidence synthesis, M40 routing, M41 candidates, M43 evidence candidates, and eventually M42 plans while keeping model language below deterministic authority.

M35/M37 or other infrastructure work should move forward only when a real consumer or operational blocker pulls it forward.

## 9. External authority still unresolved

Current repository qualification does not establish:

- production authentication/authorization;
- production privacy/security approval;
- hosted multi-user persistence;
- production retry/idempotency policy;
- production browser/device/accessibility/usability quality;
- model-provider operational policy;
- causal learner diagnosis;
- intervention-caused improvement;
- mastery;
- empirical tutoring efficacy.

Keep those claims outside repository-only/hermetic qualification until the corresponding external or human authority exists.
