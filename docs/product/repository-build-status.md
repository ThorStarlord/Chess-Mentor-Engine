# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification status  
**Updated for:** post-M9 milestone consolidation  
**Current merged baseline:** `5d880ef878154e3b20195044314346054214eb1b`

This file is the concise authority for what is currently implemented, qualified, not started, and still outside the repository's claim surface. Historical design rationale remains in the repository build plan and detailed qualification provenance remains in the architecture records.

## Current milestone board

```text
M1 — Trustworthy Chess Evidence Substrate       QUALIFIED
M2 — Deterministic Chess Feature Extraction     QUALIFIED
M3 — Engine Evidence                            QUALIFIED
M4 — Diagnostic Position Selection              QUALIFIED
M5 — Player Decision Evidence                   QUALIFIED
M6 — Reasoning Discrepancy                      QUALIFIED
M7 — Learner Hypothesis Ledger                  QUALIFIED
  M7Q — Full M7 qualification                   QUALIFIED
M8 — Evidence-Aware Tutor Session               QUALIFIED
M9 — Training Intervention Registry             QUALIFIED
M10 — Transfer / Mastery Evidence               NOT STARTED
M11 — Longitudinal Learner State                NOT STARTED
M12+ — CLI/UI/richer LLM productization         NOT STARTED
```

M10 is the next roadmap boundary implied by the product sequence, but this documentation-only consolidation does **not** itself authorize or implement M10.

## Qualified evidence-to-training path

The repository now has a qualified chain from objective chess evidence through bounded intervention selection:

```text
PGN / canonical position
        ↓
objective chess + engine evidence
        ↓
DecisionComparison / DiagnosticCandidate
        ↓
Player Decision Evidence
        ↓
position-local Reasoning Discrepancy
        ↓
participant-specific Learner Hypothesis Ledger
        ↓
Evidence-Aware Tutor Session
        ↓
explicit Training Intervention applicability
        ↓
selected / ineligible / unclear
```

Each layer preserves a separate authority boundary. A downstream result does not rewrite or promote upstream evidence into a stronger semantic category.

## M7 — Learner Hypothesis Ledger

M7 is fully qualified under ADR 0006 and the M7 architecture records.

It provides:

- stable participant-specific hypothesis lineages;
- append-only revisions and lifecycle state;
- exact mappings to qualified M6 evidence;
- versioned cross-position recurrence policy;
- one participant-position per recurrence unit;
- explicit support, contradiction, successful-counterexample, context-exception, and unclear relations;
- challenge and competing-explanation review provenance;
- deterministic `HypothesisAssessment` and `HypothesisLedgerSnapshot` rebuilds.

The status vocabulary is:

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

The M7 claim ceiling remains:

```text
supported_recurrence
!= causal cognitive mechanism
!= permanent learner trait
!= universal weakness score
!= automatic training eligibility
```

### M7Q qualification provenance

```text
PR #35
qualification-corpus head: 334f9c769e50046078d5508ecce4fac9d52cd70a
merged main: 5db3a518afdec38ee052ec3c5dbb453a03c8a739
307 passed
8 intentional external-engine skips
13 / 13 focused M7Q tests
Ruff PASS
external Stockfish PASS
```

See:

- `docs/architecture/learner-hypothesis-ledger.md`;
- `docs/architecture/learner-hypothesis-recurrence-assessment.md`;
- `docs/architecture/m7-qualification.md`;
- `docs/decisions/0006-learner-hypothesis-ledger-contract.md`.

## M8 — Evidence-Aware Tutor Session

M8 is qualified under ADR 0007.

The bounded state-machine path is:

```text
qualified M5 context / capture protocol
→ deterministic position presentation
→ minimal response
→ optional standardized diagnostic probe
→ all planned pre-reveal evidence frozen
→ objective evidence reveal
→ exact final-capture-bound M6 comparison
→ optional complete active-current M7 context
→ provenance-bearing explanation
→ immutable completed TutorSession
```

M8 qualifies:

- deterministic position-only presentation before reveal;
- hard freeze-before-reveal sequencing;
- immutable M5-owned participant evidence history;
- exact M6 comparison provenance;
- complete active-current M7 context when attached;
- human/model/template explanation provenance;
- content-addressed event history and deterministic replay.

The M8 claim ceiling is:

```text
session-local evidence explanation
!= training eligibility
!= intervention selection
!= intervention efficacy
!= learning
!= transfer
!= mastery
```

### M8 qualification provenance

```text
PR #36
final qualified PR head: 055325360b14e955b2e94c5c4fcdfd739ba8c430
merged main: 84edce598b55176bbded422fc88cc8f8101d5575
320 passed
8 intentional external-engine skips
13 / 13 focused M8 tests
Ruff PASS
external Stockfish PASS
post-merge CI PASS
```

See:

- `docs/architecture/evidence-aware-tutor-session.md`;
- `docs/decisions/0007-evidence-aware-tutor-session-contract.md`.

## M9 — Training Intervention Registry

M9 is qualified under ADR 0008.

The bounded production surface provides:

```text
ExerciseDefinition
TrainingInterventionDefinition
InterventionRegistry
HypothesisInterventionMapping
InterventionSelectionPolicy
InterventionSelectionDecision
```

The M9 path is:

```text
versioned exercise definitions
→ versioned training intervention
→ immutable registry snapshot
→ explicit participant-specific M7 hypothesis/intervention mapping
→ conservative deterministic selection policy
→ selected / ineligible / unclear
```

M9 intentionally separates three questions:

```text
What training artifact exists?
!= Does this exact hypothesis plausibly map to it?
!= May the deterministic policy select it now?
```

A current active M7 `supported_recurrence` result is necessary but not sufficient. An explicit provenance-bearing mapping must classify the intervention as:

```text
applicable
not_applicable
unclear
```

The v1 selector is deliberately failure-closed:

```text
one applicable mapping       → selected
multiple applicable mappings → unclear
only unclear mappings        → unclear
no applicable mapping        → ineligible
stale/inactive/unsupported    → ineligible
```

The selector does not perform opaque ranking or infer applicability from free-text similarity.

The M9 claim ceiling is:

```text
selected intervention under exact mapping + policy
!= best intervention
!= effective intervention
!= caused improvement
!= learning
!= transfer
!= mastery
```

### M9 qualification provenance

```text
PR #37
final qualified PR head: f5e671b56fd977818aaa33b4e4e5fd7bb967316b
merged main: 5d880ef878154e3b20195044314346054214eb1b
336 passed
8 intentional external-engine skips
16 / 16 focused M9 tests
Ruff PASS
external Stockfish PASS
post-merge CI run 34329867902 — PASS
```

See:

- `docs/architecture/training-intervention-registry.md`;
- `docs/decisions/0008-training-intervention-registry-contract.md`.

## Operator-facing validation commands

Focused qualification:

```bash
pytest tests/test_m7_qualification.py
pytest tests/test_m8_qualification.py
pytest tests/test_m9_qualification.py
```

Full regression and lint:

```bash
pytest
ruff check .
```

External Stockfish witness:

```bash
pytest tests/integration/test_stockfish_uci.py
```

The full operational procedure, Stockfish setup, Python API operation order, and human review checklist are consolidated in:

`docs/runbooks/m7-m9-milestone-runbook.md`

## Human authority that remains explicit

The repository does not automate away the following judgment boundaries:

- M7 evidence/hypothesis relation authoring and challenge review;
- M8 explanation authorship and information-sequencing discipline;
- M9 hypothesis-to-intervention applicability authoring;
- future interpretation of intervention outcomes.

Human/model authored records must retain actor/version/instruction/run provenance where the relevant schema requires it.

## Current claim ceiling

The repository may currently claim that it can:

- produce deterministic provenance-bound chess evidence;
- capture and freeze player decision evidence before reveal;
- derive bounded position-local discrepancy facts and assessments;
- maintain participant-specific recurring descriptive hypotheses with explicit challenge evidence;
- run a deterministic evidence-aware tutoring session without pre-reveal leakage;
- define versioned training artifacts;
- record explicit hypothesis/intervention applicability;
- select at most one exact registered intervention under a conservative participant-specific policy;
- return `ineligible` or `unclear` rather than fabricate a prescription;
- replay the qualified M7-M9 artifacts from exact stored inputs.

The repository may **not** yet claim:

- causal cognitive diagnosis from recurrence alone;
- a permanent learner trait or universal weakness score;
- intervention optimality or efficacy;
- improvement caused by an intervention;
- near transfer, far transfer, real-game transfer, or mastery;
- a qualified longitudinal learner-state model;
- a production-ready end-user CLI, web UI, or persistence architecture.

## Next roadmap boundary

The next conceptual milestone is M10 — Transfer / Mastery Evidence.

A future M10 design must preserve at least this distinction:

```text
exercise completion
!= intervention effect
!= near transfer
!= far transfer
!= real-game transfer
!= mastery
```

M10 remains **NOT STARTED**. This status document records the post-M9 state only and does not authorize implementation by itself.
