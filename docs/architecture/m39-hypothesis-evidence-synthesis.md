# M39 — Hypothesis Evidence Synthesizer

M39 answers a bounded explanatory question:

> Why does the current repository state hold this learner hypothesis at its current M7C status, what evidence challenges it, and what could cause a future assessment to change?

It is a deterministic synthesis over existing authority. It is not a new recurrence
classifier.

## Inputs

M39 requires:

- one participant ID;
- one exact current M36 `LearnerStateReadModel`;
- the exact current M7 `HypothesisRevision` represented by that read model;
- the exact M7C `HypothesisAssessment` referenced by that M36 entry;
- optionally, the exact K7 `HypothesisKnowledgeProjection` referenced by the M36
  entry.

If M36 says a K7 projection exists, M39 requires that exact projection rather than
silently dropping semantic context.

## Output

`m39.hypothesis-evidence-synthesis.v1` preserves:

- exact M36 read-model identity;
- exact current M7 revision identity, statement, scope, and unresolved alternatives;
- exact M7C assessment and recurrence-policy identity;
- the M7C assessment status and status reasons;
- support, independent-support, contradiction, successful-counterexample,
  context-exception, unclear, mixed, eligible, and excluded counts;
- every M7C recurrence unit with its relation preserved verbatim;
- exact source game/position identities and M7 evidence-link refs;
- contradiction, counterexample, and competing-explanation review identities/states;
- optional K7 concept IDs per covered recurrence unit;
- explicit evidence gaps, including incomplete K7 coverage;
- bounded statements describing which kinds of future evidence could cause a later
  M7C assessment to change.

## Authority boundary

```text
M36 current learner-state read model
+ exact M7 revision
+ exact M7C assessment
+ optional exact K7 semantic projection
        |
        v
M39 evidence synthesis
```

M39 does **not**:

- calculate a new recurrence status;
- alter M7C thresholds or review policy;
- infer causal psychology or a permanent learner trait;
- treat ontology concept presence as evidence that a player noticed or missed it;
- turn missing K7 coverage into evidence that a concept is absent;
- select an M9 intervention;
- establish intervention effectiveness, transfer, or mastery;
- mutate M7 or M11.

The critical invariant is:

```text
M39 synthesis != M7C recurrence authority
```

## Evidence gaps and change conditions

M39 may deterministically state facts such as:

- the current assessment is not yet `supported_recurrence`;
- no contradiction/counterexample/context-exception unit is present;
- the current M7 revision retains unresolved alternative explanations;
- K7 semantic coverage is missing or incomplete.

It may also state that new eligible M7C evidence could strengthen, weaken, narrow, or
otherwise change a future assessment. It does not predict which future status M7C
will produce.

## Rejection behavior

Construction fails closed for:

- participant mismatch;
- revision that is not current in M36;
- M7C assessment bound to another revision;
- M36/M7C assessment ID, fingerprint, or status drift;
- recurrence units from another participant;
- a missing K7 projection when M36 references one;
- a K7 projection not referenced by M36;
- K7/M7C or K7/revision identity drift;
- tampered deterministic rebuild output.

## Qualification

```bash
python -m pytest tests/test_m39_hypothesis_evidence_synthesis.py -rs
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Pull-request CI plus the independent Stockfish job remains the merge authority.
