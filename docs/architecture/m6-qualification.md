# M6Q — Full Reasoning Discrepancy Qualification

## Status

**M6Q qualifies the complete frozen M6A Reasoning Discrepancy surface across the already-qualified M6B deterministic fact layer and M6C coded local assessment layer.**

The qualification is intentionally position-local. It establishes that the repository can bind qualified objective evidence, frozen Player Decision Evidence, deterministic discrepancy facts, optional append-only coding, an explicit assessment policy, conservative local assertions, and a final local assessment without crossing into recurrence, stable learner weaknesses, causal cognitive traits, the M7 Learner Hypothesis Ledger, pedagogy, transfer, or mastery.

The governing boundary remains:

```text
qualified M4 objective evidence
+
qualified frozen M5 participant evidence
        ↓
M6B ReasoningDiscrepancyContext / DiscrepancyFact[]
        ↓
optional M6C ReasoningCoding[]
        ↓
ReasoningAssessmentPolicy
        ↓
ReasoningDiscrepancyAssertion[]
        ↓
ReasoningDiscrepancyAssessment
```

with the authority split:

```text
objective chess evidence
!= participant self-report
!= deterministic comparison fact
!= human/model semantic coding
!= position-local supported assertion
!= cross-position learner hypothesis
```

## Qualification strategy

M6Q adds no new production behavior. The qualification corpus exercises the existing qualified M6B + M6C API through the real repository evidence chain and asks whether the frozen M6A claim ceiling is executable without repair.

The focused qualification file is:

```text
tests/test_m6_qualification.py
```

No production source file was changed to satisfy M6Q. The corpus therefore acts as a cross-layer qualification harness rather than a new implementation slice.

## Focused M6Q corpus

The final focused suite contains **20 M6Q cases** covering the frozen contract's highest-risk boundaries.

### 1. Dimension-bounded successful assessment

A structured selected move that matches the cited qualified objective relation can produce:

```text
no_supported_discrepancy
```

only when at least one permitted dimension is actually assessable.

The result remains explicitly bounded to the assessed dimensions. It is not a mastery claim and does not imply that all cognition was observed.

### 2. Successful move with incomplete reported rationale

A correct/matching move does not suppress a local reasoning discrepancy. The corpus proves that:

```text
matching deterministic selected-move fact
+
explicit provenance-bound coding of incomplete rationale
→ mixed ReasoningDiscrepancyAssertion
```

The coding cannot manufacture move correctness; the deterministic prerequisite must be present.

### 3. Objective candidate absent from explicit report

When the explicit structured candidate list omits the policy-defined engine-rank1 candidate, M6 may emit only the conservative local statement:

```text
STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED
```

The assertion wording does not claim:

```text
never considered
failed to generate
failed to recognize
```

### 4. Deterministic expected-reply conflict

An impossible expected reply is established from deterministic chess legality rather than engine preference and can support:

```text
EXPECTED_OPPONENT_REPLY_CONFLICT
```

### 5. Deterministic continuation conflict

An impossible expected continuation is likewise established from deterministic chess legality and can support:

```text
EXPECTED_CONTINUATION_CONFLICT
```

### 6. Missing dimension

An absent requested structured dimension remains:

```text
not_observed
```

and, when it is the only requested dimension, produces:

```text
unscorable
NO_ASSESSABLE_DIMENSIONS
```

rather than a false negative discrepancy assessment.

### 7. Ambiguous report

An ambiguous participant move remains ambiguous and is not guessed, repaired, or silently converted into a supported discrepancy.

### 8. A1 / A2 stage separation

Minimal response and standardized probing remain separate evidence stages. A dimension absent at A1 and explicitly present or discrepant at A2 is retained as a stage change, not silently relabeled as correction, learning, or intervention effect.

### 9. Instrument-aware clean evidence

Instrument awareness remains explicit provenance while the run can remain clean:

```text
instrument_aware_clean
```

The condition propagates into the ReasoningDiscrepancyContext and final assessment.

### 10–11. Deviating and contaminated conditions

Both conditions are preserved rather than normalized away. They are unscorable under a policy that does not permit them and become assessable only when the exact policy explicitly allows the corresponding measurement condition.

### 12. Post-reveal isolation

Post-reveal reflection cannot be promoted into the frozen M6 primary pre-reveal assessment stage surface.

### 13. Unavailable comparable objective evidence

When the required comparable engine evidence is unavailable, the affected relation remains:

```text
not_comparable
```

and does not become an error claim.

### 14. Incompatible objective provenance

A mismatched objective-analysis fingerprint is rejected instead of interpolated into a comparison.

### 15. Pure coded assertion path

A permitted semantic code may be supported by explicit provenance-bound coding without pretending the coding is a deterministic fact. The resulting assertion keeps:

```text
basis_kind = coded
```

and does not invent a deterministic supporting fact.

### 16. Coder disagreement

Same-code / same-stage support and contradiction are retained simultaneously and yield:

```text
unclear
```

with contradiction provenance preserved. M6 does not use last-write-wins.

### 17. Raw-prose anti-overclaiming

Raw participant prose does not override the structured participant values used by deterministic M6B comparison. If a move appears only in raw prose and not in the explicit structured candidate field, the deterministic fact remains about **what was explicitly reported in the structured evidence**, not about hidden cognition.

### 18. Successful M4 control with local discrepancy

The corpus constructs a real M4 successful control where the played move is rank1 / objectively successful, then supplies an impossible expected continuation. M6 correctly preserves both facts:

```text
successful objective decision
+
position-local reasoning discrepancy
```

This proves:

```text
successful chess decision
!= absence of local reasoning discrepancy
```

and keeps operational M4 controls separate from future M7 hypothesis-confirmation semantics.

### 19. Full-chain deterministic replay

Two identical runs reproduce the same material identities across the chain, including selected candidate, batch, capture-session snapshot, reasoning context, discrepancy facts, assertions, and final assessment.

### 20. Historical research-artifact preservation

The seven frozen Pilot 003/004 research artifacts continue to match their preregistered Git-blob identities. M6Q does not rewrite historical research instruments or exposure provenance.

## Assessment statuses qualified together

M6Q closes the full frozen M6 status vocabulary:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

Their meanings remain narrow:

- `discrepancy_supported` — at least one permitted position-local assertion is supported under the exact policy and evidence set;
- `no_supported_discrepancy` — no permitted assertion is supported **within at least one actually assessed dimension**;
- `unclear` — material uncertainty such as coding disagreement prevents a supported local conclusion;
- `unscorable` — the requested assessment cannot support a bounded conclusion because policy/evidence/stage requirements are not met or no requested dimension is assessable.

None of these statuses means a learner trait, recurring weakness, causal cognitive explanation, intervention need, or learning outcome.

## Superseded qualification attempts

### Initial corpus head

```text
6ce92077e0fec301d2f86e5f3ffa8b0c29055dbd
```

All behavioral tests passed:

```text
227 passed
8 intentional external-engine skips in the normal suite
20 / 20 focused M6Q cases passed
```

Ruff reported only import-order and line-length issues in the new qualification test file. No production defect was exposed. The head was superseded.

### First formatting replacement

```text
e162516c05d391e26081c9fda4d26886deb0b3c2
```

All behavioral tests again passed:

```text
227 passed
8 intentional external-engine skips
20 / 20 focused M6Q cases passed
```

Ruff reported one remaining import-group formatting issue in the qualification test file. Production source remained unchanged. The head was superseded.

## Exact qualification evidence

### Exact qualified qualification-corpus head

```text
d500cb19bb8e16775ca829fda69b7accfa93d629
```

At this head the M6Q change surface was exactly:

```text
tests/test_m6_qualification.py
```

No production source, frozen M6A contract, ADR 0005, M5 evidence implementation, or research artifact changed.

### Exact-head CI

GitHub Actions run:

```text
34304053934
```

Result:

```text
227 passed
8 intentional external-engine skips in the normal suite
20 / 20 focused M6Q cases passed
Ruff PASS
external Stockfish integration PASS
```

The external Stockfish job remains an independent witness that the existing M1–M3 engine-evidence substrate is still healthy while M6 is qualified end-to-end.

## Qualification verdict

> **M6 — REASONING DISCREPANCY: QUALIFIED**

The qualified claim is:

> Chess Mentor Engine can construct an exact position-local reasoning-evidence context from qualified objective and frozen participant evidence, derive conservative deterministic comparison facts, attach separately provenance-bound human/model coding, apply a versioned local assessment policy, preserve missing/ambiguous/incompatible evidence and measurement conditions, retain coding disagreement, and emit conservative position-local discrepancy assertions and bounded assessment states without collapsing participant report, deterministic fact, coder judgment, or learner-level inference into one another.

## Claims still prohibited after M6Q

M6 qualification does **not** establish that:

- an omitted idea was never considered, recognized, or generated;
- one engine PV defines every acceptable human continuation;
- a coder/model judgment is objective chess truth;
- a local coded label is a stable learner trait;
- the system knows the causal reason a move was chosen;
- a local discrepancy recurs across positions;
- a stable learner weakness exists;
- a successful control confirms or contradicts a learner hypothesis;
- a learner hypothesis is supported;
- an intervention is warranted or effective;
- learning, transfer, or mastery occurred.

Those claims begin, if at all, only in later separately frozen and qualified milestones.

## Promotion gate

This qualification record is part of the M6Q promotion surface. Promotion of repository status requires the final docs-integrated PR head to pass the complete CI suite, merge without tree drift from that exact qualified head, and pass authoritative post-merge `main` CI. `docs/product/repository-build-status.md` and `CONTEXT.md` remain the authority for whether that promotion has completed.

## Next milestone boundary

After M6 is fully promoted, the next conceptual milestone is:

> **M7 — Learner Hypothesis Ledger**

M7 is the first milestone allowed to reason across positions about recurrence, contradiction, competing explanations, and learner-hypothesis state. M6Q itself adds none of that behavior.
