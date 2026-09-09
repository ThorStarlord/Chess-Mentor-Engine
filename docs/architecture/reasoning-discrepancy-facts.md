# M6B — Deterministic Reasoning-Evidence Comparison Facts

## Status

**M6B — Deterministic comparison facts is qualified. M6C coded local discrepancy assessment is authorized next but has not started. M7 remains unauthorized.**

M6B implements only the deterministic comparison layer frozen by the M6A contract and ADR 0005. It does not implement free-text interpretation, `ReasoningCoding`, local discrepancy assertions/assessment policy, recurrence, learner hypotheses, tutoring, pedagogy, or training selection.

## Qualified production boundary

```text
qualified M4 objective evidence
+
qualified frozen M5 structured participant evidence
        ↓
ReasoningDiscrepancyContext
        ↓
DiscrepancyFact[]
```

The qualified relation vocabulary is:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

These remain descriptive evidence relations rather than claims about hidden cognition.

The hard M6A rule remains:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

## Implemented package

M6B adds:

```text
src/chess_mentor_engine/learning/
├── __init__.py
├── context.py
├── facts.py
└── model.py
```

with focused qualification in:

```text
tests/test_reasoning_discrepancy_facts.py
```

### Immutable records

M6B implements:

- `ReasoningEvidenceRef` — a stable reference that retains the upstream authority domain;
- `ReasoningDiscrepancyContext` — an immutable position-local M4/M5 evidence bundle;
- `DiscrepancyFact` — one deterministic relation with exact participant/objective references, values, comparison provenance, and stable identity.

M6B deliberately does **not** implement `ReasoningCoding`, `ReasoningDiscrepancyAssertion`, `ReasoningDiscrepancyAssessment`, or an assessment policy. Those remain M6C.

## Strict upstream binding

The public context builder requires the actual M4 `DiagnosticCandidate` and, when the M5 context carries one, the actual `DiagnosticCandidateBatch`.

It verifies:

- candidate ID and full fingerprint against the M5 reference;
- candidate position/game identity;
- candidate → supplied `DecisionComparison` identity;
- batch ID and full fingerprint against the M5 reference;
- candidate membership in the supplied batch;
- supplied `SelectionSignal` identity/fingerprint against the signals retained by the candidate;
- canonical M5 position/game identity;
- optional M2 feature packet identity/FEN;
- supplied M3 analysis request/result/failure provenance against the M4 comparison;
- selected assessment stages are frozen pre-reveal `MINIMAL_RESPONSE` or `STANDARDIZED_PROBE` evidence.

M6B therefore does not accept an orphan participant response or an unrelated objective analysis merely because they happen to describe the same-looking board.

## Measurement-condition preservation

`ReasoningDiscrepancyContext` carries one of:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

The implementation derives the first four directly from qualified M5 capture provenance:

- contamination remains contamination;
- a retained protocol deviation remains `deviating` when it does not contaminate pre-reveal evidence;
- known instrument awareness without contamination remains `instrument_aware_clean`;
- otherwise the selected evidence is `clean`.

Instrument awareness is therefore not silently converted into contamination, and contaminated/deviating evidence is not rewritten as clean.

## Qualified fact families

### `REPORTED_SELECTED_MOVE_RELATION`

M6B compares an explicitly structured selected move only.

Initial behavior:

```text
field absent
→ not_observed

ambiguous/unresolved participant move
→ ambiguous

illegal move from canonical position
→ conflict under deterministic chess authority

exact engine rank-1 move
→ match to the cited engine judgment

canonical played move + qualified M4 worse-for-mover comparison
→ conflict to that cited M4/engine evidence

canonical played move + qualified M4 policy-equivalent comparison
→ match to that cited M4 evidence

other legal move not evaluated by the qualified comparison
→ not_comparable
```

A legal move is never labeled wrong merely because M6B lacks comparable evidence for it.

### `EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION`

M6B compares the exact structured candidate list against the exact complete/exact engine rank-1 candidate when available.

```text
candidate field absent
→ not_observed

objective rank-1 unavailable
→ not_comparable

rank-1 explicitly listed
→ match

candidate list contains unresolved/ambiguous move values and rank-1 is not established
→ ambiguous

rank-1 absent from the explicit structured list
→ not_explicitly_reported
```

Crucially:

```text
not_explicitly_reported
!= never considered
!= failed candidate generation
```

Raw prose is not parsed to repair or reinterpret the structured candidate report.

### `EXPECTED_REPLY_RELATION`

M6B distinguishes deterministic chess legality from engine-PV agreement.

```text
reply field absent
→ not_observed

ambiguous reply
→ ambiguous

selected move unavailable for locating the reply position
→ not_comparable

illegal reply after the participant's selected move
→ conflict under deterministic chess authority

reply equals the cited engine PV reply
→ match to that cited engine judgment

legal alternative reply differs from one non-forced engine PV
→ not_comparable
```

Therefore:

```text
legal reply != engine PV reply
```

does not automatically mean the participant's reply was objectively wrong.

### `EXPECTED_CONTINUATION_RELATION`

The same conservative rule applies to explicit continuation moves:

```text
continuation absent
→ not_observed

ambiguous continuation
→ ambiguous

missing selected move/reply context
→ not_comparable

illegal continuation move
→ conflict under deterministic chess authority

continuation equals cited engine PV suffix
→ match to that cited engine judgment

legal continuation differs from one non-forced PV
→ not_comparable
```

## Free-text boundary

M6B never parses `raw_response` to manufacture participant truth.

The qualification suite includes a case where the raw prose says that `d4` was seriously considered while the explicit structured candidate list contains only `e4`. The deterministic candidate-membership fact remains:

```text
engine rank-1 d4 absent from explicit structured candidates
→ not_explicitly_reported
```

The prose remains available in the cited M5 response identity for future M6C coding, but M6B does not interpret it.

## Objective-evidence insufficiency

When the exact root engine analysis is unavailable, M6B preserves affected engine-relative dimensions as `not_comparable` instead of inferring an answer.

A supplied analysis whose request/result identity disagrees with the qualified M4 comparison is rejected rather than interpolated.

This preserves:

```text
missing / mismatched objective evidence
!= permission to approximate certainty
```

## Deterministic identity

Context and fact identity retain the exact participant evidence provenance.

Two responses may contain the same explicit structured selected move and therefore produce the same descriptive relation while still producing different M6 context/fact identities when their raw frozen responses differ.

That is intentional:

```text
same deterministic relation
!= same evidence event
```

## Focused qualification surface

The M6B test suite contains 19 focused tests covering:

1. deterministic context identity and canonical protocol-stage order;
2. rejection of a candidate not bound to the M5 context;
3. mandatory freeze for selected primary evidence;
4. clean / instrument-aware / deviating / contaminated measurement conditions;
5. qualified M4 played-move conflict;
6. engine rank-1 selected-move match;
7. ambiguous selected move;
8. illegal selected move under deterministic chess authority;
9. candidate membership match versus explicit omission;
10. ambiguous candidate list;
11. absent candidate/reply/continuation dimensions → `not_observed`;
12. engine-PV reply match versus legal alternative → `not_comparable`;
13. illegal expected reply;
14. engine-PV continuation match versus legal divergence → `not_comparable`;
15. illegal continuation;
16. raw prose is not parsed into candidate truth;
17. missing root analysis → `not_comparable`;
18. mismatched root analysis rejected;
19. same structured relation with different raw response retains different evidence identity.

## Superseded qualification attempts

### Initial head

```text
da92c1b7fbe8d9fbd6d3aefe51fd720b3d779b8b
```

One focused test failed because the test fixture treated `record_capture_exposure(...)` as returning a session instead of its actual `(session, event)` pair. Production behavior was not changed to satisfy the failure. The fixture was corrected and the replacement head requalified from scratch.

### Behavioral-green / Ruff-failing head

```text
1ab69f498e347e7a2ad93d825f6fc5f204718de1
```

This head produced:

```text
175 passed
8 intentionally skipped external-engine tests
all 19 M6B-focused tests passed
```

Ruff then identified import formatting and line-length findings in the new M6B files/tests. Only formatting was changed. The final head was requalified from scratch rather than inheriting the behavioral pass.

## Exact qualification evidence

### Exact qualified implementation candidate

```text
b8b3fec34521b160b0199e1a634d50e55c3b8fff
```

PR #25 changed exactly:

```text
src/chess_mentor_engine/learning/__init__.py
src/chess_mentor_engine/learning/context.py
src/chess_mentor_engine/learning/facts.py
src/chess_mentor_engine/learning/model.py
tests/test_reasoning_discrepancy_facts.py
```

### Exact-head CI

GitHub Actions run:

```text
34293399719
```

Result:

```text
175 passed
8 intentionally skipped external-engine tests in the normal suite
19 M6B-focused tests passed
Ruff PASS
external Stockfish integration PASS
```

### Qualification merge

```text
3b63d456ad185cb2191e5174b15ba2d8f9a50913
```

Comparing the exact qualified candidate with the merge commit produced zero changed files. The implementation merge is tree-identical to the qualified head.

### Post-merge CI

GitHub Actions run:

```text
34293580569
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M6B — DETERMINISTIC REASONING-EVIDENCE COMPARISON FACTS: QUALIFIED**

The qualified claim is intentionally narrow:

> Chess Mentor Engine can bind one position-local M6 context to exact qualified M4/M5 evidence and deterministically emit stage-specific descriptive relations for explicitly structured selected move, candidate membership, expected reply, and expected continuation while preserving ambiguity, missing evidence, measurement condition, objective-evidence provenance, and single-PV uncertainty.

## Claims still prohibited

M6B does **not** establish that:

- unreported content was never considered, recognized, or generated;
- raw participant prose has been semantically interpreted;
- a local `ReasoningCoding` label is supported;
- a Reasoning Discrepancy assessment has been completed;
- the reported explanation caused the player's move;
- any discrepancy recurs across positions;
- a stable learner weakness or causal cognitive trait exists;
- a learner hypothesis is supported or contradicted;
- a training intervention is warranted;
- teaching, learning, transfer, or mastery has occurred.

## Next authorized slice

> **M6C — coded local discrepancy assessment only.**

M6C may implement immutable analyst/model coding, local assertions, versioned assessment policy, and position-local assessment status under the frozen M6A authority split.

It must keep raw M5 evidence, deterministic M6B facts, and analyst/model coding separate; preserve `unclear`/`unscorable`; retain coder/model/rubric provenance; and remain strictly position-local.

M7 recurrence / Learner Hypothesis Ledger remains unauthorized until M6Q is qualified.
