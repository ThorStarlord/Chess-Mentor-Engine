# ADR 0005 — Reasoning Discrepancy Contract

## Status

Accepted for M6A. Production implementation is not authorized by this ADR alone.

## Context

M1–M4 now provide a qualified objective evidence path, and M5 provides qualified
provenance-rich participant decision evidence.

The repository can therefore preserve both:

```text
what the board / engine evidence says
```

and:

```text
what the participant explicitly reported before objective reveal
```

The next product risk is epistemic rather than mechanical. A system can compare those
domains usefully while still overclaiming what the comparison means.

Examples of unsafe collapses include:

```text
move absent from report
→ player never considered move

engine PV differs from expected line
→ participant calculated incorrectly

one position-level mismatch
→ player has stable weakness
```

The frozen research work already points toward a safer concept. Pilot 004 defines a
Reasoning Discrepancy as a traceable mismatch between reported pre-engine reasoning and
an objectively relevant demand or consequence, while explicitly keeping position-level
discrepancy separate from recurrence, learner hypothesis, confirmed weakness, and
causal cognitive trait.

Production M6 needs to preserve that useful local concept while tightening the wording
around unobserved cognition, engine provenance, analyst/model coding, and missing data.

## Decision

M6 will produce only position-local, evidence-bound Reasoning Discrepancy assessments.

The governing boundary is:

```text
qualified objective evidence
+ qualified Player Decision Evidence
        ↓
local Reasoning Discrepancy assessment
```

with:

```text
local discrepancy
!= unreported cognition
!= causal cognitive mechanism
!= recurrence
!= stable learner weakness
!= learner hypothesis
!= pedagogical prescription
```

## Decision 1 — M6 preserves all upstream authority domains

M6 must keep separate:

```text
deterministic chess fact
!= provenance-bound engine judgment
!= M4 objective decision evidence
!= participant self-report
!= analyst/model coding
!= learner inference
```

An M6 record must cite the exact upstream authority it uses rather than flattening all
inputs into one undifferentiated `truth` field.

## Decision 2 — Deterministic comparison facts and semantic coding are separate

M6 has two derived-evidence layers.

### Deterministic `DiscrepancyFact`

May compare explicit structured M5 participant values against exact qualified objective
evidence.

It may emit descriptive relations such as:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

It may not parse free text or infer hidden reasoning.

### `ReasoningCoding`

Semantic interpretation supplied by a human analyst or model is separate append-only
coding with exact source refs and coder/model/rubric provenance.

Coding never overwrites participant evidence or deterministic facts.

## Decision 3 — Absence from a report is not absence from cognition

This is a hard production rule:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

Even a direct candidate-elicitation prompt supports only a prompt- and stage-specific
statement that a move was not included in that submitted response.

Therefore the Pilot 004 research phrase `strong candidate not generated` is not adopted
verbatim as an initial production claim. Production uses the conservative form
`strong objective candidate not explicitly reported`, with the objective basis for
`strong` cited or coded.

## Decision 4 — Missing dimensions are not negative evidence

If the prompt did not ask for a dimension, or the participant did not submit an
unambiguous value for it, M6 records `not_observed` or `ambiguous` as appropriate.

Example:

```text
minimal-only response contains no expected reply field
→ expected-reply dimension = not_observed
→ no expected-reply discrepancy may be inferred
```

M6 must not manufacture evidence by treating silence as a wrong answer.

## Decision 5 — Incompatible objective evidence remains not comparable

If the required objective evidence is partial, bounded, incompatible, absent, or
otherwise insufficient under the assessment policy, the affected relation is
`not_comparable`.

M6 must not interpolate certainty across an upstream evidence boundary that M3/M4
already preserved as uncertain.

## Decision 6 — Engine judgment is not deterministic chess truth

Qualified M3 engine evidence is valid evidence but remains provenance-bound judgment.

Accordingly:

```text
move illegal under chess rules
```

and:

```text
move not in engine top-N under this analysis
```

are different-strength statements.

Likewise, divergence from one engine PV is not automatically an error if multiple
replies/continuations are valid or comparable. A PV may be treated as uniquely forced
only when stronger cited evidence supports that claim.

## Decision 7 — Objective relevance may itself require coding

M2 can prove that a deterministic feature exists. M3 can rank/evaluate lines. M4 can
record why a position was selected under a versioned objective policy.

Those facts do not automatically establish that a feature was the uniquely `critical`
feature a participant had to report.

Terms such as:

```text
critical
strong
strategically necessary
incomplete rationale
```

require either a precise upstream deterministic definition or explicit coding
provenance.

## Decision 8 — M6 uses a conservative local taxonomy

The initial production discrepancy codes are:

```text
OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED
STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED
EXPECTED_OPPONENT_REPLY_CONFLICT
EXPECTED_CONTINUATION_CONFLICT
REPORTED_RESULTING_EVALUATION_CONFLICT
STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE
CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE
OTHER_LOCAL_DISCREPANCY
```

The following are assessment statuses, not discrepancy codes:

```text
no_supported_discrepancy
unclear
unscorable
```

This taxonomy describes local evidence relations and deliberately avoids stable
psychological labels.

## Decision 9 — Correct move and complete reasoning are distinct

M6 freezes both directions:

```text
correct / rank-1 move
!= complete reasoning

inferior move
!= necessarily incorrect self-understanding
```

M6 therefore cannot use move quality alone as a reasoning diagnosis.

A successful M4 control remains eligible for M6 analysis and may expose a local
reasoning discrepancy. Conversely, an inferior move may coexist with an accurate
participant report about its objective downside.

## Decision 10 — Pre-reveal stages remain separate

The initial M6 primary evidence surface is frozen M5:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
```

A1 and A2 remain separate evidence states.

M6 may compare stages only by citing both explicitly. It may not reconstruct one
fictional `true reasoning` narrative by merging them.

Probe-induced changes are evidence about stage change, not automatic proof of cognitive
correction or learning.

## Decision 11 — Post-reveal and recollection evidence cannot be promoted backward

`POST_REVEAL_REFLECTION` and `ORIGINAL_GAME_RECOLLECTION` may be useful supplemental or
contradictory evidence.

They must not be silently used as if they were frozen pre-reveal reasoning.

A production assertion about pre-reveal reasoning must cite eligible frozen pre-reveal
M5 evidence as its primary participant basis.

## Decision 12 — Measurement condition remains attached

M6 must preserve whether its participant evidence was:

```text
clean
instrument_aware_clean
deviating
contaminated
unknown
```

Instrument awareness alone does not equal contamination.

A versioned assessment policy may allow analysis of deviating/contaminated evidence,
but the resulting assessment must retain that condition. M6 must not erase exposure or
protocol-deviation provenance to manufacture a clean case.

## Decision 13 — Coding is append-only and disagreement is first-class

Human/model coding records are immutable derived evidence.

Multiple coders may disagree. Their records coexist.

Without an explicit versioned adjudication rule, M6 must not silently select the coding
that best supports a preferred conclusion. Material unresolved disagreement may force
an assertion or assessment to `unclear`.

## Decision 14 — The assessment policy is versioned and material

Every final M6 assessment cites a versioned policy that fixes at least:

- eligible stage kinds;
- allowed measurement conditions;
- required objective evidence;
- permitted fact kinds;
- permitted discrepancy codes;
- coding requirements;
- any thresholds/parameters;
- position-local claim scope.

Changing a material interpretation rule or threshold changes policy identity/fingerprint.

M6A freezes no universal centipawn threshold and no global reasoning-severity score.

## Decision 15 — No-supported-discrepancy is narrowly scoped

`no_supported_discrepancy` means:

> No local discrepancy was supported within the dimensions actually observed and
> assessable under the cited policy.

It does not mean:

- all reasoning was observed;
- cognition was correct;
- no weakness exists;
- mastery exists.

## Decision 16 — M6 outputs immutable evidence-bound records

The initial semantic records are:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
ReasoningCoding
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

Material identity must bind exact M4/M5 refs, response/freeze/prompt/exposure/deviation
state, objective evidence refs, fact refs, coding refs, assessment-policy identity, and
result.

If coding is nondeterministic, its immutable coding record isolates that nondeterminism.
Given identical frozen inputs, coding records, and assessment policy, final assessment
serialization/fingerprint should be deterministic.

## Decision 17 — M6 is position-local; recurrence is M7

A single M6 assessment must never claim recurrence.

Pilot 004's recurrence policy requires more than one independent position, common
structure, comparable reasoning evidence, controls and contradictory cases, and
consideration of alternatives.

Those cross-position responsibilities belong to M7.

M7 remains unauthorized until M6Q passes and repository status authority is explicitly
reconciled.

## Decision 18 — M6 is not pedagogy

M6 must not emit training prescriptions such as:

```text
needs tactics training
practice candidate generation
use checks-captures-threats
study prophylaxis
```

A local discrepancy may later become evidence for M7 hypotheses and M9 interventions,
but those downstream steps require their own contracts and validation.

## Decision 19 — Research artifacts remain immutable historical authorities

Pilot 003/004 discrepancy and recurrence documents inform M6A but are not rewritten.

Their research codes are not universal production learner categories. Production may
adapt wording conservatively while preserving exact research provenance.

## Decision 20 — M6 implementation proceeds in bounded slices

The authorized sequence after M6A is:

```text
M6B deterministic reasoning-evidence comparisons
→ M6C coded local discrepancy assessment
→ M6Q full M6 qualification
```

### M6B

Implement exact context binding and deterministic `DiscrepancyFact` derivation only.
No free-text parsing, live model invocation, recurrence, learner hypothesis, or
pedagogy.

### M6C

Implement immutable coding/assessment records and versioned assessment policy. Initial
qualification may use precomputed or human-supplied coding; live model integration is
not required.

### M6Q

Qualify the full position-local claim surface, including clean, instrument-aware,
contaminated, missing, ambiguous, incompatible, disagreement, no-discrepancy, control,
and anti-overclaiming cases.

## Consequences

### Positive

- objective and participant evidence can finally be compared without inventing hidden
  cognition;
- M6 can represent useful local mismatches while retaining uncertainty;
- successful controls remain diagnostically useful;
- engine evidence keeps its provenance rather than becoming false certainty;
- model/human semantic coding can be added without corrupting participant authority;
- coding disagreement remains auditable;
- M7 will receive position-local evidence rather than unstructured diagnostic prose.

### Costs

- M6 needs more record types than a single `diagnosis` string;
- many cases will legitimately remain `not_observed`, `not_comparable`, `unclear`, or
  `unscorable`;
- analyst/model coding requires provenance and versioning;
- the system cannot use psychologically appealing labels as shortcuts;
- recurrence and training recommendations remain unavailable until later milestones.

These costs are preferable to manufacturing certainty about why a player thought or
acted as they did.

## Alternatives considered

### Infer a cognitive error directly from every engine mismatch

Rejected. Move quality and reasoning evidence are different domains.

### Treat absence from a candidate list as candidate-generation failure

Rejected. The submitted list is evidence about what was reported, not a direct readout
of all internal cognition.

### Parse free text directly into participant truth

Rejected. Parsed semantics are coding and must remain separate from the raw M5 record.

### Treat one engine PV as the unique correct continuation

Rejected unless stronger objective evidence supports forced uniqueness.

### Discard contaminated/deviating evidence

Rejected. Preserve the evidence condition and let an explicit policy decide whether it
is assessable.

### Merge A1 and A2 into one final reasoning narrative

Rejected. Stage changes are evidence and must remain visible.

### Start recurrence/hypothesis aggregation inside M6

Rejected. Cross-position recurrence is a distinct evidentiary escalation owned by M7.

### Produce training recommendations directly from a local discrepancy

Rejected. Diagnosis support and pedagogical intervention require separate qualification.

## Related records

- `docs/architecture/reasoning-discrepancy.md`
- `docs/architecture/m5-qualification.md`
- `docs/architecture/player-decision-evidence.md`
- `docs/architecture/diagnostic-position-selection.md`
- `docs/decisions/0004-player-decision-evidence-contract.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/evidence-schema.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/discrepancy-taxonomy.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/recurrence-policy.md`
- `docs/product/repository-build-status.md`
