# M43 — Contradiction / Control Evidence Acquisition

## Purpose

M43 gives selected M40 evidence-oriented proposals a deterministic consumer. It ranks
participant-local evidence that is worth presenting, reviewing, or including in a
future M7C reassessment.

Supported M40 actions:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

M43 does **not** classify recurrence and does not modify M7, M7C, M11, or M40.

## Inputs

M43 binds:

- one exact `NextSessionPlan`;
- one exact `NextSessionActionCandidate` contained by that plan;
- the exact M39 `HypothesisEvidenceSynthesis` when the proposal references one;
- zero or more additional M7B `HypothesisEvidenceLink` records for the exact current
  participant and hypothesis revision;
- one versioned `EvidenceAcquisitionPolicy`.

The additional M7B link pool is deliberately explicit. M43 v1 does not invent a new
repository search index, persistence layer, or recurrence engine merely to discover
candidate evidence.

## Output

```text
m43.evidence-acquisition-plan.v1
```

The result is content-addressed and contains ranked `EvidenceAcquisitionCandidate`
records plus explicit gaps and exclusion counts.

Candidates preserve their upstream authority:

```text
current M7C unit
-> classified_contradiction
-> classified_successful_counterexample
-> classified_context_exception

additional M7B link
-> potential_contradiction
-> potential_successful_counterexample
-> potential_context_exception
-> insufficiently_classified
-> novel_retest_context
```

The word `potential` is material. An additional M7B relation is not promoted into the
current M7C assessment merely because M43 selected it for review.

## Ranking policy

The default policy is transparent and content-addressed. It prioritizes existing
classified controls for `PRESENT_CONTROL`, then potential contradiction/counterexample
material, context exceptions, unresolved cases, and new evidence contexts.

Within equal candidate kinds, the policy prefers a new source game and then a new
source position before stable identifiers.

This is an information-acquisition heuristic, not a learned score or empirical claim
of optimal tutoring.

## Ontology use

Existing M39/K7 concept context is preserved for current M7C units. Additional M7B
links may have no K7 coverage, and that absence is recorded explicitly.

```text
missing K7 coverage != concept absent
same ontology concept != same learner process
```

M43 adds no ontology schema merely for completeness. A later consumer may extend the
ontology only when a concrete semantic distinction is required and separately
qualified.

## Authority ceiling

Preserve:

```text
M43 candidate != M7C contradiction
M43 candidate != hypothesis refutation
M43 ranked first != objectively best evidence
successful case != mastery
M43 plan != execution authorization
```

The output carries:

```text
decision_authority = candidate_only
m7c_effect = not_established
mastery = not_established
```

## Failure-closed behavior

M43 rejects:

- a proposal that is not contained in the exact M40 plan;
- unsupported M40 actions;
- missing or drifted M39 identity when the proposal references M39;
- cross-participant additional evidence;
- evidence linked to a different/stale hypothesis revision;
- duplicate additional link identities.

The default policy excludes contaminated additional links and deduplicates positions
already represented in the current M39 synthesis. An empty eligible result is valid
and is represented as an explicit search gap rather than fabricated evidence.

## Non-goals

M43 v1 does not:

- mutate M7 or M11;
- re-run or replace M7C;
- infer participant psychology from chess concepts;
- fetch live external data;
- create a new persistence/search backend;
- establish intervention efficacy or mastery.
