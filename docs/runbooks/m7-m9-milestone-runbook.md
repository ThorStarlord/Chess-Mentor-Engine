# M7-M9 Milestone Runbook

**Scope:** qualified M7Q, M8, and M9 surfaces  
**Audience:** contributors, coding agents, experiment operators, and reviewers  
**Current merge baseline:** `5d880ef878154e3b20195044314346054214eb1b`

This runbook consolidates the operational path added by the three completed milestone features:

```text
M7Q — Full Learner-Hypothesis Qualification
M8  — Evidence-Aware Tutor Session
M9  — Training Intervention Registry
```

It is intentionally procedural. Architecture semantics remain authoritative in the linked ADRs and architecture records.

## 1. Environment setup

Requirements:

- Python 3.11 or newer;
- development dependencies from `pyproject.toml`;
- Stockfish only for the external-engine witness.

Create a local environment and install the package:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

There is no product CLI yet. M7-M9 are Python APIs. The CLI commands in this runbook are validation and development commands.

## 2. Validation commands

### Focused qualification suites

Run each milestone independently:

```bash
pytest tests/test_m7_qualification.py
pytest tests/test_m8_qualification.py
pytest tests/test_m9_qualification.py
```

Run them together:

```bash
pytest \
  tests/test_m7_qualification.py \
  tests/test_m8_qualification.py \
  tests/test_m9_qualification.py
```

### Full regression and lint gates

```bash
pytest
ruff check .
```

At the M9 merge baseline the full suite passed with:

```text
336 passed
8 intentional external-engine skips in the normal suite
16 / 16 focused M9 tests passed
Ruff PASS
```

### External Stockfish witness

On Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y stockfish

export STOCKFISH_EXECUTABLE="$(command -v stockfish || true)"
if [ -z "$STOCKFISH_EXECUTABLE" ] && [ -x /usr/games/stockfish ]; then
  export STOCKFISH_EXECUTABLE=/usr/games/stockfish
fi

test -n "$STOCKFISH_EXECUTABLE"
test -x "$STOCKFISH_EXECUTABLE"
pytest tests/integration/test_stockfish_uci.py
```

On other platforms, install Stockfish separately and set `STOCKFISH_EXECUTABLE` to the executable path before running the same integration test.

GitHub Actions runs both the normal test/lint job and a separate Ubuntu Stockfish witness on pull requests to `main` and pushes to `main`.

## 3. M7Q — learner-hypothesis qualification

### Purpose

M7 is the first production layer allowed to reason across multiple qualified M6 position-local evidence units.

The operational path is:

```text
qualified M6 evidence
→ explicit hypothesis/evidence mapping
→ versioned recurrence policy
→ challenge + competing-explanation review
→ HypothesisAssessment
→ HypothesisLedgerSnapshot
```

Primary module:

```python
from chess_mentor_engine import learning
```

Useful public operations include:

```text
create_learner_hypothesis
record_hypothesis_revision
record_hypothesis_evidence_link
define_hypothesis_assessment_policy
record_hypothesis_challenge_review
record_competing_explanation_review
assess_hypothesis_recurrence
build_hypothesis_ledger_snapshot
```

For executable construction details, use `tests/test_m7_qualification.py` and the lower-level M7 tests as the reference implementation.

### Human/model obligations

An operator or model authoring M7 evidence must preserve the distinction between:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
```

Do not infer contradiction merely because a position was an M4 control or M6 returned `no_supported_discrepancy`.

When the policy requires challenge review, contradiction/counterexample review and competing explanations must be recorded explicitly with provenance. Do not silently drop inconvenient cases.

### Claim ceiling

Allowed:

- a participant-specific descriptive recurrence has a stated status under an exact versioned policy;
- challenge cases and exclusions were reviewed under cited provenance;
- current hypothesis state can be deterministically rebuilt from append-only history.

Not allowed:

```text
supported_recurrence
→ causal mechanism
→ permanent trait
→ automatic training eligibility
```

Those implications are intentionally invalid.

## 4. M8 — evidence-aware tutor session

### Purpose

M8 turns qualified M5/M6/M7 artifacts into a replayable tutoring interaction without contaminating the diagnostic evidence that later explanation depends on.

Primary module:

```python
from chess_mentor_engine import tutoring
```

The allowed operation order is:

```text
start_tutor_session
→ present_tutor_position
→ present_tutor_capture_stage
→ capture_tutor_response
→ freeze_tutor_response
→ [optional standardized probe: present/capture/freeze]
→ reveal_tutor_objective_evidence
→ record_tutor_reasoning_comparison
→ [optional] attach_tutor_hypothesis_context
→ record_tutor_explanation
→ complete_tutor_session
```

The state machine is deliberately strict. Callers should treat `TutorSessionError` as a boundary violation rather than bypassing it.

### Mandatory operator protocol

1. Start from an exact qualified M5 `PlayerDecisionContext` and compatible `CaptureProtocol`.
2. Present only deterministic position context before participant capture.
3. Capture the minimal response first; an optional standardized diagnostic probe may follow.
4. Freeze every planned pre-reveal response before objective evidence is shown.
5. Reveal objective evidence only through the M5-owned reveal operation.
6. Attach M6 comparison only when it targets the exact final revealed capture snapshot.
7. If M7 context is attached, supply the complete active-current hypothesis context; do not cherry-pick one favorable active hypothesis.
8. Record explanation only after comparison, with explicit human/model/template provenance.
9. Complete the session without rewriting earlier evidence or event history.

### Failure conditions that should remain failures

Do not work around:

- reveal before all planned freezes;
- stale or mismatched position/capture fingerprints;
- M6 comparison from a different capture snapshot;
- selective omission of active M7 context;
- explanation before comparison;
- attempts to encode M9 training selection into the M8 session record.

### Claim ceiling

M8 establishes:

```text
sequencing
+ provenance
+ deterministic replay
+ session-local explanation provenance
```

M8 does not establish training eligibility, intervention effectiveness, learning, transfer, or mastery.

## 5. M9 — training intervention registry

### Purpose

M9 is the first qualified layer allowed to make a bounded participant-specific intervention-selection decision.

Primary module:

```python
from chess_mentor_engine import training
```

The operation order is:

```text
define_exercise
→ define_training_intervention
→ build_intervention_registry
→ record_hypothesis_intervention_mapping
→ define_intervention_selection_policy
→ select_training_intervention
```

The selector operates on exact M7 current state, exact registry contents, exact applicability mappings, and an exact versioned policy.

### Content-authoring protocol

For each `ExerciseDefinition`:

- give it a stable semantic key and explicit version;
- provide inspectable instructions;
- declare position source (`historical_position`, `fresh_position`, or `mixed`);
- define response/completion evidence schema;
- record author/version/instruction/run provenance.

For each `TrainingInterventionDefinition`:

- state the target behavior;
- state the rationale;
- embed exact versioned exercise definitions;
- provide dosage guidance and exclusion notes;
- retain content-author provenance.

Building a new registry snapshot should be treated as a versioned release of available training content.

### Applicability protocol

A current active M7 hypothesis with `supported_recurrence` is necessary but is **not** an automatic prescription.

A human or model must explicitly author a `HypothesisInterventionMapping` with one of:

```text
applicable
not_applicable
unclear
```

The mapping must include rationale, uncertainty notes where relevant, provenance, and timestamp.

Do not infer applicability from title/text similarity inside the deterministic selector.

### Selection protocol

The v1 selection policy requires:

- participant identity match;
- exact current M7 revision;
- active lifecycle state;
- latest current M7 status `supported_recurrence`;
- exact registry membership;
- exact mapping fingerprints;
- one and only one applicable mapping.

Results:

```text
one applicable mapping      → selected
multiple applicable mappings → unclear
only unclear mappings        → unclear
no applicable mapping        → ineligible
stale/inactive/unsupported    → ineligible
```

`unclear` is an intentional safety state. Do not replace it with an undocumented ranking heuristic.

### Claim ceiling

M9 may claim that an exact registered intervention was selected under an exact participant-specific mapping and versioned policy.

M9 may not claim:

- that the selected intervention is best or optimal;
- that the intervention is effective;
- that exercise completion caused improvement;
- that learning, near transfer, far transfer, real-game transfer, or mastery occurred.

Those claims require later outcome evidence.

## 6. Manual review checklist before accepting an M7-M9 result

Use this checklist whenever a human reviews a generated diagnosis/session/intervention decision:

- [ ] Participant identity is consistent across M5, M6, M7, M8, and M9 artifacts.
- [ ] All cited artifact IDs and fingerprints refer to the exact material records used.
- [ ] M7 recurrence uses independent qualifying evidence under the stated policy.
- [ ] Contradictions, successful counterexamples, context exceptions, and unclear evidence remain visible.
- [ ] Required challenge and competing-explanation reviews are complete and provenance-bearing.
- [ ] M8 objective evidence was not revealed before all required participant evidence was frozen.
- [ ] M8 explanation cites the exact final comparison and, when used, complete active-current M7 context.
- [ ] M9 registry/version matches the intervention referenced by the mapping.
- [ ] Applicability was explicitly authored; it was not inferred by deterministic text matching.
- [ ] `unclear` and `ineligible` outcomes have not been manually converted into `selected` without a new provenance-bearing mapping/policy decision.
- [ ] No output claims intervention effectiveness, learning, transfer, or mastery without later qualified evidence.

## 7. Regression protocol for future changes

For any change touching M7, M8, or M9:

1. Run the focused milestone suite for the changed boundary.
2. Run the downstream focused suites because provenance contracts compose:
   - M7 change → run M7 + M8 + M9;
   - M8 change → run M8 + M9;
   - M9 change → run M9.
3. Run the full repository suite.
4. Run Ruff.
5. Run the Stockfish witness when qualifying a merge candidate.
6. Record exact head SHA and CI run when a milestone claim is promoted.
7. Preserve historical research artifacts and prior content-addressed identities rather than rewriting them.

Recommended commands for a complete pre-merge gate:

```bash
pytest tests/test_m7_qualification.py \
       tests/test_m8_qualification.py \
       tests/test_m9_qualification.py
pytest
ruff check .
pytest tests/integration/test_stockfish_uci.py
```

## 8. Qualification provenance from this milestone sequence

```text
Feature 1 / M7Q
PR #35
qualified corpus head: 334f9c769e50046078d5508ecce4fac9d52cd70a
merged main: 5db3a518afdec38ee052ec3c5dbb453a03c8a739
focused suite: 13 / 13

Feature 2 / M8
PR #36
final qualified PR head: 055325360b14e955b2e94c5c4fcdfd739ba8c430
merged main: 84edce598b55176bbded422fc88cc8f8101d5575
focused suite: 13 / 13

Feature 3 / M9
PR #37
final qualified PR head: f5e671b56fd977818aaa33b4e4e5fd7bb967316b
merged main: 5d880ef878154e3b20195044314346054214eb1b
focused suite: 16 / 16
post-merge CI run: 34329867902 — PASS
```

## 9. Next boundary

M10 Transfer / Mastery Evidence is not implemented by this milestone sequence.

The natural next research/architecture question is how to record intervention attempts and fresh outcome evidence without confusing:

```text
exercise completion
!= intervention effect
!= near transfer
!= far transfer
!= real-game transfer
!= mastery
```

This runbook does not authorize M10 implementation by itself.
