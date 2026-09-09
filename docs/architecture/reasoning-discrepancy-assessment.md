# M6C — Coded Local Reasoning Discrepancy Assessment

## Status

**M6C — Coded local discrepancy assessment is qualified. M6Q full M6 qualification is authorized next but has not started. M7 remains unauthorized.**

M6C implements the interpretation layer frozen by the M6A contract and ADR 0005 while remaining strictly position-local. It consumes exact M6B deterministic facts and qualified M4/M5 provenance, and it records human/model coding separately from deterministic evidence.

M6C does **not** implement recurrence, cross-position aggregation, stable learner weaknesses, causal cognitive traits, the Learner Hypothesis Ledger, tutoring, pedagogy, training prescription, transfer/mastery, persistence, database behavior, UI, or live model invocation.

## Qualified production boundary

```text
qualified M4/M5 evidence
+
qualified M6B ReasoningDiscrepancyContext / DiscrepancyFact[]
        ↓
optional append-only ReasoningCoding[]
        ↓
versioned ReasoningAssessmentPolicy
        ↓
position-local ReasoningDiscrepancyAssertion[]
        ↓
ReasoningDiscrepancyAssessment
```

The governing authority split remains:

```text
raw/frozen participant evidence
!= deterministic M6B comparison fact
!= human/model M6C coding
!= position-local supported assertion
!= cross-position learner hypothesis
```

## Implemented package

M6C adds:

```text
src/chess_mentor_engine/learning/
├── assessment_model.py
└── assessment.py
```

and extends the public `learning` API without modifying the qualified M6B fact derivation modules.

Qualification tests are in:

```text
tests/test_reasoning_discrepancy_assessment.py
tests/test_reasoning_discrepancy_assessment_provenance.py
```

## Immutable M6C records

### `ReasoningCoding`

`ReasoningCoding` is append-only derived evidence. It records:

- exact `ReasoningDiscrepancyContext` identity;
- coding kind: support, contradiction, or unclear;
- one frozen M6A discrepancy code;
- coder/model statement;
- exact stage IDs;
- exact source participant-evidence refs;
- exact source objective-evidence refs;
- exact source M6B fact refs;
- `human` or `model` coder kind;
- coder/run identity and version;
- rubric/instruction fingerprint;
- optional confidence and uncertainty note;
- timestamp;
- content-addressed identity/fingerprint.

A coding record is **not** participant evidence and is **not** objective chess truth.
Different coders or model runs may disagree. M6C retains disagreement rather than overwriting one judgment with another.

### `ReasoningAssessmentPolicy`

The qualified policy record is material and versioned. It binds:

- policy ID/version;
- eligible pre-reveal stage kinds;
- allowed measurement conditions;
- required objective-evidence kinds;
- permitted M6B fact kinds;
- permitted discrepancy codes;
- codes requiring coding provenance;
- supported explicit parameters;
- `position_local` claim scope;
- full policy fingerprint.

Changing material configuration changes policy identity.

Initial M6C deliberately supports only the frozen primary M6 stage kinds:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
```

and the frozen measurement-condition vocabulary:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

A deviating or contaminated context is scorable only when the exact assessment policy explicitly allows that condition. The condition remains attached to the assessment.

### `ReasoningDiscrepancyAssertion`

An assertion is one conservative position-local claim under an exact policy.

It records:

- discrepancy code;
- exact assessed stage(s);
- supporting deterministic fact refs;
- supporting coding refs;
- contradictory evidence refs;
- basis kind: `deterministic`, `coded`, or `mixed`;
- exact policy ref;
- `position_local` scope;
- stable content-addressed identity.

Assertion wording is generated from fixed conservative templates. Arbitrary coder prose is preserved in `ReasoningCoding` but is **not** copied into the assertion as though it were validated learner-level truth.

This prevents a coder statement such as a stable weakness label from silently escaping the M6 position-local claim ceiling.

### `ReasoningDiscrepancyAssessment`

The assessment record binds:

- exact M6 reasoning context;
- exact policy;
- assessment status;
- assessed stage IDs;
- exact assertion refs;
- exact eligible fact refs;
- exact eligible coding refs;
- contradictory coding refs;
- measurement condition;
- explicit status reasons;
- timestamp;
- stable identity/fingerprint.

The frozen status vocabulary is:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

## Deterministic versus coded support

M6C preserves the M6A rule that deterministic support is narrower than semantic interpretation.

### Deterministic initial mappings

Under an explicit compatible policy:

```text
EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION
+ not_explicitly_reported
+ exact engine rank-1 candidate
+ strong_candidate_basis=engine_rank1
→ STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED
```

```text
EXPECTED_REPLY_RELATION + conflict
→ EXPECTED_OPPONENT_REPLY_CONFLICT
```

```text
EXPECTED_CONTINUATION_RELATION + conflict
→ EXPECTED_CONTINUATION_CONFLICT
```

The first mapping deliberately names its objective-strength basis in policy. M6C does not introduce a universal centipawn threshold or claim that engine rank 1 is the only reasonable move.

### Coding-required initial codes

The following remain intrinsically semantic and cannot be enabled as deterministic-only claims:

```text
OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED
REPORTED_RESULTING_EVALUATION_CONFLICT
STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE
CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE
OTHER_LOCAL_DISCREPANCY
```

`CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE` additionally requires a matching deterministic selected-move fact, producing a `mixed` assertion rather than allowing coding alone to manufacture move correctness.

## Absence semantics remain conservative

M6C preserves the M6A/M6B hard rule:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

Therefore the strong-candidate assertion means only that the candidate met the policy's explicit objective-strength basis and was absent from the explicit structured candidate report.

It does **not** mean the candidate was absent from the participant's mind.

## A1 / A2 stage separation

A1 and A2 are assessed as distinct evidence stages.

Coding disagreement is grouped by discrepancy code **and exact stage set**. Consequently:

```text
A1 support
+ A2 contradiction
!= same-stage coder disagreement
```

A changed answer after standardized probing is preserved as a stage change. It is not silently rewritten as a correction, intervention effect, or contradiction within one evidence stage.

## Uncertainty and negative-result semantics

### `unclear`

M6C returns `unclear` when material coding support cannot be resolved, including:

- explicit `discrepancy_unclear` coding;
- support and contradiction for the same code/stage group;
- coding support whose required deterministic prerequisite is absent.

No last-write-wins behavior is used.

### `unscorable`

M6C returns `unscorable` for hard eligibility/evidence failures such as:

- measurement condition not allowed by policy;
- no policy-eligible assessment stage;
- required objective-evidence kind missing;
- no assessable dimension after applying policy/evidence boundaries.

In particular:

```text
not_observed only
→ unscorable
```

rather than a false negative discrepancy assessment.

### `no_supported_discrepancy`

This status is emitted only when at least one permitted dimension is assessable but no supported assertion remains under the exact policy/evidence set.

It means:

> no supported discrepancy within the explicitly assessed dimensions.

It does **not** mean all cognition was observed, all reasoning was correct, or the learner has mastered the position.

## Provenance revalidation

M6C initially validated coding identity/fingerprint at assessment time. During qualification audit, that was strengthened because a manually reconstructed content-consistent coding record could otherwise carry embedded source refs not belonging to the supplied M6 context.

The final qualified implementation revalidates:

- coding context identity;
- coding fingerprint and content-addressed ID;
- coding kind and discrepancy code;
- coding stage membership;
- every embedded participant source ref against the M6 context;
- every embedded objective source ref against the M6 context;
- every embedded source fact ref against the exact supplied M6B fact set;
- stage IDs derived from the cited stage-specific sources;
- policy semantic vocabulary even for manually constructed records;
- M6B fact kind/relation semantic vocabulary even for manually constructed records.

This means a record cannot become acceptable merely by recomputing its own hash after substituting unrelated evidence.

## Focused qualification surface

The final M6C focused suite contains **32 tests**:

- 25 core assessment tests;
- 7 provenance-hardening regression tests.

The core suite covers:

- material/order-normalized policy identity;
- mandatory coding for intrinsically semantic codes;
- explicit basis for deterministic strong-candidate interpretation;
- human/model coding provenance;
- source evidence restrictions;
- deterministic candidate/reply/continuation assertions;
- mixed deterministic+coding rationale assertion;
- arbitrary coder prose containment;
- same-stage coding disagreement;
- A1/A2 distinction;
- explicit uncertainty;
- missing deterministic prerequisites;
- contaminated-evidence policy gating;
- required-objective-evidence gating;
- `not_observed` not becoming a negative claim;
- dimension-bounded `no_supported_discrepancy`;
- stage-specific policy selection;
- contradictory coding preservation;
- deterministic replay identity;
- material policy identity changing assessment identity;
- capture-session provenance binding.

The hardening suite covers:

- assessment-time rejection of unrelated coding participant refs;
- assessment-time rejection of nonexistent/mismatched coding fact refs;
- assessment-time rejection of coding stage/source mismatch;
- unknown policy measurement condition rejection;
- unknown policy fact-kind rejection;
- semantic revalidation of manually reconstructed policy records;
- semantic revalidation of manually reconstructed M6B fact records.

## Superseded qualification attempts

### Initial implementation head

```text
4638283178ed1f168fd3f71de5dae93d71d1007a
```

Behavioral tests passed (`200 passed`, `8` intentional external-engine skips), but Ruff found import ordering in the new public API surface. The head was superseded.

### Formatting-clean pre-audit head

```text
6a78a11a522654e94d85e0742c10bb55291c1147
```

The complete suite and Stockfish qualification were green. A manual provenance audit then identified the embedded-source revalidation gap described above. This green head was deliberately **not** merged and was superseded by a stricter implementation.

### Provenance-hardened, Ruff-failing head

```text
bc54dd585119b5c13e8e40d065f5de1d1d55104c
```

All behavioral tests passed (`207 passed`, `8` intentional external-engine skips), including all seven new provenance-hardening cases, and Stockfish passed. Ruff found import ordering and one line-length issue in the new test-only file. Only formatting was changed; the replacement head was requalified from scratch.

## Exact qualification evidence

### Exact qualified implementation candidate

```text
809beb31e969acaaca9857dd1985ab52bdb33b90
```

PR #27 changed exactly:

```text
src/chess_mentor_engine/learning/__init__.py
src/chess_mentor_engine/learning/assessment.py
src/chess_mentor_engine/learning/assessment_model.py
tests/test_reasoning_discrepancy_assessment.py
tests/test_reasoning_discrepancy_assessment_provenance.py
```

### Exact-head CI

GitHub Actions run:

```text
34295462836
```

Result:

```text
207 passed
8 intentionally skipped external-engine tests in the normal suite
32 M6C-focused tests passed
Ruff PASS
external Stockfish integration PASS
```

### Qualification merge

```text
8bcacbbcdb500ccb9d4bfc395e140068a460bebd
```

Comparing the exact qualified implementation candidate with the merge commit produced zero changed files. The implementation merge is tree-identical to the qualified head.

### Post-merge CI

GitHub Actions run:

```text
34295561562
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M6C — CODED LOCAL REASONING DISCREPANCY ASSESSMENT: QUALIFIED**

The qualified claim is intentionally local:

> Chess Mentor Engine can bind immutable human/model coding to exact qualified position-local evidence, apply an explicit versioned assessment policy, preserve coding disagreement and measurement conditions, and emit conservative provenance-rich local discrepancy assertions and `discrepancy_supported / no_supported_discrepancy / unclear / unscorable` assessment states without collapsing coding into participant evidence or learner-level diagnosis.

## Claims still prohibited

M6C does **not** establish that:

- an omitted idea was never considered, recognized, or generated;
- a coder/model judgment is objective chess truth;
- an arbitrary coder label is a validated learner trait;
- a local discrepancy recurs;
- a stable learner weakness exists;
- a causal cognitive mechanism has been established;
- a successful control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- training is warranted;
- an intervention is effective;
- learning, transfer, or mastery occurred.

## Next authorized slice

> **M6Q — full Reasoning Discrepancy qualification only.**

M6Q must qualify the complete frozen M6A surface across M6B + M6C, including the deterministic/coded authority split, all status semantics, evidence insufficiency, stage boundaries, measurement conditions, disagreement/contradiction handling, identity/replay, and the full M6 claim ceiling.

M7 Learner Hypothesis Ledger remains unauthorized until M6Q itself is qualified, merged from the exact qualified head, passes post-merge CI, and the repository status authorities are reconciled.
