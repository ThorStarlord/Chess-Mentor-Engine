# M7C — Learner Hypothesis Recurrence Assessment + Derived Ledger State

## Status

**QUALIFIED.**

M7C implements the recurrence-assessment and derived-current-state layer authorized by
the frozen M7A Learner Hypothesis Ledger contract and built on the qualified M7B
immutable hypothesis/evidence ledger.

The qualified boundary is:

```text
qualified M7B hypothesis revision
+ exact M7B evidence links
+ exact referenced M6 assessments/assertions
+ versioned HypothesisAssessmentPolicy
+ provenance-bound review records
        ↓
HypothesisAssessment
        ↓
HypothesisLedgerSnapshot
```

while preserving:

```text
recorded M7B evidence relation
!= recurrence unit
!= recurrence assessment

supported_recurrence
!= causal cognitive mechanism
!= permanent learner trait
!= universal weakness/confidence score
!= training eligibility
!= pedagogical prescription
```

M7Q remains responsible for full milestone qualification across M7A + M7B + M7C.
M8 remains unauthorized until M7Q closes the complete M7 boundary and repository
status is explicitly reconciled.

## Governing authorities

M7C is constrained by:

- `docs/architecture/learner-hypothesis-ledger.md` — frozen M7A contract;
- `docs/decisions/0006-learner-hypothesis-ledger-contract.md` — ADR 0006;
- `docs/architecture/learner-hypothesis-evidence-ledger.md` — qualified M7B record;
- the fully qualified M6 Reasoning Discrepancy surface;
- the frozen Pilot 004 recurrence methodology as immutable research authority rather
  than production state.

The authority split remains:

```text
M6 position-local assessment
!= M7B evidence mapping
!= M7C recurrence unit
!= M7C recurrence status
!= causal explanation
!= pedagogical action
```

## Production files

M7C adds the hardened implementation and record modules:

```text
src/chess_mentor_engine/learning/hypothesis_recurrence.py
src/chess_mentor_engine/learning/hypothesis_recurrence_model.py
```

and exposes the bounded public surface through:

```text
src/chess_mentor_engine/learning/hypothesis_assessment.py
src/chess_mentor_engine/learning/hypothesis_assessment_model.py
src/chess_mentor_engine/learning/__init__.py
```

The focused qualification tests are:

```text
tests/test_hypothesis_recurrence_assessment.py
tests/test_hypothesis_recurrence_provenance.py
tests/test_hypothesis_challenge_review_gate.py
tests/test_hypothesis_ledger_snapshot.py
```

No M7Q production behavior and no M8/pedagogy surface is introduced.

## `HypothesisAssessmentPolicy`

`HypothesisAssessmentPolicy` is versioned and materially fingerprinted. The initial
qualified policy surface explicitly binds:

```text
eligible M6 assessment statuses
eligible M6 discrepancy codes
allowed measurement conditions
M6-policy compatibility rule
stage compatibility rule
context-match rule
recurrence-unit rule
independence rule
candidate recurrence threshold
supported recurrence threshold
contradiction-review requirement
counterexample-review requirement
competing-explanation-review requirement
contradiction rule
participant-specific cross-position claim scope
```

Material policy changes alter the policy fingerprint and therefore the resulting
assessment identity.

Initial M6-policy compatibility modes are:

```text
same_policy_fingerprint
declared_policy_fingerprints
```

Initial stage compatibility modes are:

```text
same_assessed_stage_ids
declared_stage_ids
```

Initial context modes are:

```text
exact_revision_contexts
shared_revision_context
broad_scope
```

Initial independence modes are:

```text
distinct_game_id
distinct_position_id
```

The recurrence unit itself remains fixed by the frozen M7A rule:

```text
one participant + one canonical position
→ one recurrence unit
```

The candidate threshold cannot be configured below two independent supports, and the
supported-recurrence threshold cannot be lower than the candidate threshold.

## One-position recurrence accounting

M7C aggregates exact M7B evidence links by participant + canonical position before
counting recurrence.

Therefore:

```text
position X → supports link A
position X → supports link B
```

still produces one supporting recurrence unit.

If the same position contains conflicting M7 mappings, for example:

```text
position X → supports
position X → unclear
```

the recurrence unit becomes `mixed`, and the assessment becomes `unclear` rather than
allowing record multiplicity to inflate support.

A participant-position recurrence unit cannot silently span multiple game identities.

## Independence and common structure

Independence is explicit policy, not an inferred property of repeated labels.

Under `distinct_game_id`, two positions from the same game may remain two recurrence
units but contribute only one independent-support unit. Under `distinct_position_id`,
canonical position identity supplies the independence unit.

Common structure is also explicit. M7C does not use embedding similarity or opaque LLM
semantic similarity as authority.

For context-bounded hypotheses, exact or shared `HypothesisContextRef` values must
satisfy the versioned context rule. Broad-scope assessment is an explicit policy mode
and requires a correspondingly broad revision without context-definition refs.

## Evidence eligibility and compatibility

M7C consumes the exact referenced M6 records rather than trusting M7B link labels in
isolation.

Before an M7B link is eligible for aggregation, M7C validates or gates:

```text
exact hypothesis revision
participant identity
exact M6 assessment identity + fingerprint
exact selected M6 assertion identity + fingerprint
assessment/context relationship
assertion/assessment relationship
assertion M6 policy relationship
assertion stage membership
link / M6 measurement-condition agreement
M7 policy-eligible M6 status
M7 policy-eligible discrepancy code
M7 policy measurement-condition allowance
M6 policy compatibility
stage compatibility
context compatibility
chronology
```

Incompatible evidence is excluded with structured reasons rather than silently
normalized into comparability.

A `supports` link must cite at least one exact hypothesis-relevant M6 assertion. This
prevents a bare support label from becoming recurrence evidence without qualified
position-local content.

## Exact hypothesis lineage provenance

M7C independently revalidates the hypothesis lineage at assessment time.

Revision 1 must reproduce the stable hypothesis origin-proposal fingerprint. Revision
2+ cannot be assessed from a matching `hypothesis_id` alone: the exact contiguous
revision history is required, including exact parent refs and chronology.

This closes the same class of hash-consistent-but-unrelated substitution that M7B
already rejects when recording evidence links.

## Challenge and competing-explanation review provenance

M7C stores provenance-bound review records rather than representing review obligations
as unobservable booleans.

The qualified review records are:

```text
CompetingExplanationReview
HypothesisChallengeReview(kind=contradiction)
HypothesisChallengeReview(kind=successful_counterexample)
```

Completed reviews carry actor provenance. Review fingerprints and identities are
revalidated before they can affect assessment state.

The public recurrence API may construct a deterministic system-provenance challenge
review when a caller omits one. That record explicitly cites the contradiction or
successful-counterexample links present in the exact frozen assessment evidence set.
It does not claim that the supplied evidence set is globally exhaustive; it only makes
the exact review operation auditable. Callers may instead supply explicit human/model
review records.

Required but incomplete contradiction review prevents a `contradicted` result and
produces `unclear`. Required but incomplete counterexample review prevents promotion to
`supported_recurrence`.

## Assessment statuses

M7C implements exactly the frozen M7A recurrence vocabulary:

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

The initial deterministic aggregation behavior is conservative:

```text
no policy-eligible evidence
→ insufficient

one supporting recurrence unit
→ isolated

multiple supports but candidate independence threshold not met
→ insufficient

candidate independence threshold met
+ supported-recurrence gates still open
→ candidate_recurrence

supported threshold met
+ no unclear recurrence units
+ no context exceptions
+ no successful counterexamples
+ required challenge reviews satisfied
+ required competing-explanation review satisfied
→ supported_recurrence

contradiction rule met
+ required challenge review satisfied
→ contradicted

mixed same-position relations
or contradiction rule met with required review incomplete
→ unclear
```

A successful counterexample counts as contradiction only when the exact policy uses
`any_contradiction_or_counterexample`. Otherwise it remains separately visible and
blocks `supported_recurrence` without being silently relabeled.

Likewise:

```text
M6 no_supported_discrepancy
!= M7 counterexample
```

It becomes counterevidence only when an exact M7B mapping explicitly records that
relation and the M7C policy admits it.

## Structured evidence summary

Each `HypothesisAssessment` preserves structured rather than scalar evidence state,
including:

```text
eligible / excluded link counts
supporting recurrence-unit count
independent-support count
contradiction count
successful-counterexample count
context-exception count
unclear count
mixed-unit count
source positions
source games
measurement conditions
traceable common context refs
excluded link refs + exclusion reasons
```

M7C introduces no universal weakness score or confidence scalar.

## `HypothesisLedgerSnapshot`

`HypothesisLedgerSnapshot` is a rebuildable participant-specific current view over
append-only history.

For each hypothesis lineage, the snapshot derives:

```text
stable hypothesis ref
current valid revision ref
latest assessment for that current revision only
authority lifecycle state
latest terminal lifecycle event ref if present
```

A new hypothesis revision does not cause an older revision's recurrence assessment to
be silently treated as current. The new revision may therefore temporarily have no
current assessment until it is assessed separately.

Lifecycle remains independent from recurrence status:

```text
supported_recurrence + retired
candidate_recurrence + active
contradicted + superseded
```

are structurally representable combinations when supported by the exact history.

Snapshot reconstruction rejects dangling revision/assessment/lifecycle refs, mixed
participants, duplicate terminal lifecycle history, future records relative to the
snapshot timestamp, and a superseding lineage that is absent from the supplied
snapshot history.

## Deterministic identity

M7C follows the repository convention:

```text
SHA-256(canonical JSON of material content)
```

Policy, review, assessment, and snapshot identities are content-addressed. Input order
is canonicalized where order is not semantic. Replaying the same frozen history,
policy, review records, and evidence set yields the same material identities.

## Qualification corpus

The focused M7C suite covers 38 cases across four test files, including:

- material policy identity and threshold constraints;
- isolated support;
- same-position duplicate links without double counting;
- same-game non-independence under `distinct_game_id`;
- candidate recurrence from two independent supports;
- supported recurrence from the configured stronger threshold;
- contradiction precedence;
- policy-controlled counterexample-as-contradiction;
- context exceptions and unclear evidence blocking supported status;
- conflicting same-position mappings producing one mixed/unclear unit;
- incompatible M6-policy families excluded rather than normalized;
- explicitly declared compatible M6-policy families;
- A1/A2 stage mismatch rejection under strict policy;
- explicit declared-stage compatibility;
- measurement-condition exclusion with retained reasons;
- explicit broad-scope assessment;
- incomplete competing-explanation review blocking supported status;
- `no_supported_discrepancy` becoming counterevidence only through explicit mapping;
- exact hypothesis origin-proposal validation;
- revision-2+ exact lineage-history requirement;
- forged competing/challenge review fingerprint rejection;
- material policy changes changing policy fingerprint;
- required contradiction review blocking `contradicted` when incomplete;
- required counterexample review blocking `supported_recurrence` when incomplete;
- deterministic current-revision snapshot derivation;
- old-revision assessment not becoming current after revision;
- retirement/supersession history preservation;
- deterministic snapshot replay;
- cross-participant and dangling-history rejection;
- forged assessment rejection;
- future-record rejection;
- exact superseding-lineage requirement.

The exact qualified implementation head is:

```text
e6f6debee79ea7780b5dbfc1732def802d9bd8b4
```

GitHub Actions run:

```text
34311289575
```

Qualification result:

```text
294 passed
8 intentional external-engine skips in the normal suite
38 / 38 focused M7C tests passed
Ruff PASS
external Stockfish integration PASS
```

PR #33 was merged from that exact qualified head as:

```text
df6bee774259ac98e8edbcdd2ab17306c9c09873
```

The qualified head and merge commit are tree-identical (`files: []` in the commit
comparison).

Post-merge authoritative `main` Actions run:

```text
34311520576
```

passed both `test-and-lint` and `stockfish-integration`.

## M7C claim ceiling

After M7C qualification, the repository may claim that it can:

- evaluate one exact participant-specific descriptive hypothesis revision under one
  exact versioned recurrence policy and frozen evidence set;
- enforce one participant-position as one recurrence unit;
- apply explicit independence, M6-policy, stage, measurement, and context compatibility
  rules;
- preserve support, contradiction, successful-counterexample, context-exception,
  unclear, mixed, and excluded evidence separately;
- assign the bounded M7 recurrence states `insufficient / isolated /
  candidate_recurrence / supported_recurrence / contradicted / unclear`;
- preserve challenge and competing-explanation review provenance;
- rebuild current participant-specific ledger state deterministically while keeping
  authority lifecycle separate from recurrence assessment.

It may **not** claim that:

- `supported_recurrence` establishes a causal cognitive mechanism;
- a recurrence status is a permanent learner trait;
- the system has a universal weakness/confidence scalar;
- a supported descriptive hypothesis is automatically training-eligible;
- any intervention is warranted or effective;
- tutoring efficacy has been demonstrated;
- learning, transfer, or mastery occurred.

## Stop boundary

M7C is qualified. The only next authorized milestone slice after repository-status
reconciliation is:

> **M7Q — full M7 qualification.**

M7Q must qualify the complete frozen M7A surface across the already implemented M7B +
M7C behavior without silently expanding the production claim boundary. M8 remains
unauthorized until M7Q passes and repository status is explicitly reconciled.
