# Chess Knowledge Learner Projection

Status: K7 repository-only integration surface.

## Purpose

The Chess Knowledge Ontology can describe what chess concepts are present in a
position, but that is not the same question as whether a position supports or
contradicts a learner hypothesis.

M7C already owns the second question. It classifies participant-position recurrence
units as one of:

- `supports`
- `contradicts`
- `successful_counterexample`
- `context_exception`
- `unclear`
- `mixed`

K7 therefore does **not** build a second recurrence engine. It projects exact,
provenance-bound ontology assertions onto already-classified M7C recurrence units.

## Authority boundary

```text
position / move evidence
        |
        v
Chess Knowledge Assertion
        |
        | describes chess content only
        v
M7C recurrence unit ------------------------------+
        |                                          |
        | already owns hypothesis relation         |
        v                                          |
supports / contradicts / counterexample / ...     |
        |                                          |
        +--------------------+---------------------+
                             v
                 HypothesisKnowledgeProjection
```

The projection preserves the M7C relation verbatim. Ontology presence never
reclassifies a recurrence unit.

The same concept may therefore occur in both a supporting position and a
contradictory position. That is expected and is important evidence against naive
rules such as "concept X implies learner weakness Y".

## Projection record

`HypothesisKnowledgeProjection` is content-addressed and binds:

- the exact M7C hypothesis-assessment ID and fingerprint;
- the exact hypothesis revision reference;
- the existing M7C assessment status;
- the exact ontology version and fingerprint;
- zero or more position-level knowledge assertion bundles;
- each covered M7C recurrence unit and its original relation;
- per-concept descriptive counts by M7C relation, assertion status, and assertion
  authority;
- explicit covered and uncovered recurrence-unit IDs.

Partial ontology coverage is legal and visible. Missing knowledge bundles are not
silently interpreted as absence of a concept.

## Validation rules

K7 rejects:

- a tampered or re-fingerprinted M7C assessment;
- an assertion bundle from a position outside the assessment;
- duplicate bundles for one M7C participant-position subject;
- move or move-sequence bundles in this position-level projection;
- ontology/version drift;
- assertion-bundle tampering;
- relation drift between a projected occurrence and its source M7C recurrence unit;
- projection identity or fingerprint tampering.

Input bundle order does not affect projection identity.

## Non-goals

K7 does not:

- decide whether an M7 hypothesis is supported;
- change M7C recurrence thresholds or contradiction policy;
- infer participant perception from position facts;
- convert chess concepts into causal cognitive diagnoses;
- automatically create, revise, retire, or reactivate learner hypotheses;
- select M9 interventions;
- claim mastery, transfer, or intervention efficacy;
- make model-authored prose objective chess truth.

## Intended downstream use

The projection provides a typed bridge for future learner-intelligence work. A
consumer can ask questions such as:

- Which chess concepts commonly occur in positions that already support this
  hypothesis?
- Which concepts also occur in counterexamples?
- Is a learner hypothesis concentrated in one strategic context or distributed
  across several?
- Which concept families might be useful explanatory context for a teaching
  intervention?

Those are descriptive queries over already-qualified evidence. Any future policy
that turns those observations into learner-state or intervention decisions must
receive its own explicit, versioned authority contract and qualification.
