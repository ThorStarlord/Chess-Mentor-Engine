# M7Q — Full Learner Hypothesis Ledger Qualification

**Status:** QUALIFIED  
**Milestone:** M7 — Learner Hypothesis Ledger  
**Contract authority:** `docs/architecture/learner-hypothesis-ledger.md` + ADR 0006  
**Qualification-only:** yes; no production source behavior was added by M7Q

## Qualification result

M7Q closes the complete frozen M7A claim surface across the already-qualified M7B
immutable hypothesis/evidence ledger and M7C recurrence-assessment / rebuildable-state
implementation.

The exact qualification-corpus head was:

```text
334f9c769e50046078d5508ecce4fac9d52cd70a
```

GitHub Actions run `34317869412` passed both repository jobs:

```text
307 passed
8 intentional external-engine skips in the normal suite
13 / 13 focused M7Q qualification tests passed
Ruff PASS
external Stockfish integration PASS
```

The focused qualification surface is frozen in:

```text
tests/fixtures/m7q_learner_hypothesis_corpus.json
tests/test_m7_qualification.py
```

No file under `src/chess_mentor_engine/` changed to obtain this result. M7Q therefore
qualifies existing M7B + M7C behavior rather than broadening the production contract.

## What the qualification proves

The frozen M7Q corpus exercises the full M7A evidence ladder together rather than
qualifying isolated helpers only.

### Recurrence does not inflate from repeated observation of one position

M7Q verifies together that:

```text
one qualifying support position
→ isolated
→ not recurrence

multiple mappings / codings of one participant-position
→ one recurrence unit

multiple positions that fail the configured independence rule
→ no recurrence inflation
```

Candidate and supported recurrence therefore require the exact versioned M7 policy's
independence and threshold gates, not raw link counts.

### Support and challenge evidence coexist

The corpus proves that support is not a one-way accumulator. The same hypothesis
history can preserve:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
```

Relevant contradiction remains visible and can produce `contradicted` under the exact
policy. Successful counterexamples remain first-class evidence and become contradiction
only when the exact policy says so.

### Controls and no-discrepancy cases are not automatic counterevidence

M7Q preserves the frozen anti-collapse rules:

```text
M4 operational control
!= M7 contradiction / successful counterexample

M6 no_supported_discrepancy
!= M7 contradiction / successful counterexample
```

A control or no-supported-discrepancy case affects the M7 hypothesis only through an
explicit hypothesis-relevant evidence mapping whose observed dimension is assessable,
comparable, and context-matching. Missing or merely unmapped evidence cannot be
manufactured into counterevidence.

### Context exceptions and unclear evidence constrain claims

A context exception is retained as scope evidence rather than deleted to protect a
broad hypothesis. Unclear evidence remains unclear and prevents promotion to a stronger
supported status when the policy requires resolution.

This preserves the intended revision path:

```text
broad descriptive candidate
→ context exception
→ narrower revision or continued candidate status
```

rather than:

```text
broad descriptive candidate
→ inconvenient evidence deleted
→ artificial support
```

### Compatibility and measurement provenance are material

M7Q verifies that stage, M6-policy family, and measurement condition remain explicit
material inputs.

By default, incompatible A1/A2 stage families are not silently merged. Distinct M6
policy families are not silently aggregated. Contaminated/deviating measurement
conditions are not normalized into clean evidence. A versioned M7 policy may admit
such evidence only through explicit configured rules, with the original condition
preserved.

### Competing explanations remain review obligations

Required competing-explanation review is a real promotion gate. Recording an
alternative does not mean refuting it, and supported recurrence still does not choose a
causal cognitive explanation.

### Revision and lifecycle history remain append-only

M7Q exercises the complete history model:

```text
revision 1 assessment
→ revision 2
→ old assessment remains attached to revision 1
→ old assessment does not become current for revision 2

supported assessment
→ retirement
→ historical assessment remains preserved

old lineage
→ superseded by new lineage
→ both lineages remain reconstructable
```

Recurrence assessment and authority lifecycle remain separate axes.

### Deterministic replay remains stable

Given the same frozen hypothesis, exact M6-derived evidence, explicit links, material
assessment policy, reviews, revisions, and lifecycle events, M7Q produces identical
assessment and ledger-snapshot identities independent of input ordering.

The focused suite also verifies byte-identical preservation of the seven frozen Pilot
003/004 research artifacts already protected by M5Q/M6Q.

## Qualified M7 claim ceiling

After M7Q, Chess Mentor Engine may make bounded claims such as:

- a participant-specific descriptive pattern has only isolated support;
- an exact hypothesis revision has `candidate_recurrence`, `supported_recurrence`,
  `contradicted`, `unclear`, or another frozen M7 status under the cited exact policy
  and evidence set;
- recurrence support satisfies an explicit independence rule;
- contradiction, successful-counterexample, context-exception, and unclear evidence
  are retained rather than suppressed;
- challenge and competing-explanation review provenance is preserved;
- hypothesis revisions, retirement, and supersession preserve append-only history;
- current learner-hypothesis ledger state is deterministically rebuildable from that
  history.

## Claims still prohibited after M7Q

M7 qualification does **not** establish that:

- an unreported move or idea was never considered, recognized, or generated;
- model/human coding is objective chess truth;
- `supported_recurrence` proves a causal cognitive mechanism;
- recurrence is a permanent learner trait;
- the learner has a universal weakness/confidence score;
- a supported descriptive hypothesis is automatically training-eligible;
- any specific intervention should be prescribed;
- any intervention is effective;
- tutoring has caused improvement;
- learning, transfer, or mastery has occurred.

Those remain later product and validation boundaries.

## Milestone transition

M7 is fully qualified after this qualification record is merged and repository status
is reconciled.

The next authorized milestone is:

```text
M8 — Evidence-aware Tutor Session
```

M8 is **authorized next but not started**. M7Q authorizes only the next bounded design /
implementation step; it does not itself implement tutoring behavior, training
interventions, pedagogy, transfer, mastery, persistence, CLI, or UI.
