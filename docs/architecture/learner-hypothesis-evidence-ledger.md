# M7B — Immutable Learner Hypothesis / Evidence Ledger

## Status

**QUALIFIED.**

M7B implements only the immutable record-and-link layer authorized by the frozen M7A
Learner Hypothesis Ledger contract and ADR 0006.

It does **not** assess recurrence, count independent evidence units, decide that a
hypothesis is supported, derive a current ledger snapshot, or authorize tutoring or
pedagogy.

The qualified boundary is:

```text
qualified position-local M6 evidence
        +
explicit participant-specific hypothesis proposal
        ↓
LearnerHypothesis
        ↓
HypothesisRevision[]
        ↓
HypothesisLifecycleEvent[]
        +
HypothesisEvidenceLink[]
```

with:

```text
recorded evidence relation
!= recurrence assessment
!= supported learner hypothesis
!= causal cognitive trait
!= training eligibility
```

M7C remains responsible for recurrence assessment, explicit independence/common-
structure policy, evidence aggregation, `HypothesisAssessment`, and derived ledger
state.

## Governing authorities

M7B is constrained by:

- `docs/architecture/learner-hypothesis-ledger.md` — frozen M7A architecture contract;
- `docs/decisions/0006-learner-hypothesis-ledger-contract.md` — ADR 0006;
- the fully qualified M6 Reasoning Discrepancy surface;
- the frozen Pilot 004 recurrence methodology, which remains immutable research
  authority rather than a production data file.

M7B preserves the upstream authority split:

```text
M6 objective/participant evidence
!= M6 deterministic fact
!= M6 human/model coding
!= M6 local assertion
!= M7 hypothesis/evidence mapping
!= M7 recurrence assessment
```

## Production files

M7B adds:

```text
src/chess_mentor_engine/learning/hypothesis_model.py
src/chess_mentor_engine/learning/hypothesis_ledger.py
```

and exports the bounded public surface through:

```text
src/chess_mentor_engine/learning/__init__.py
```

The focused qualification tests are:

```text
tests/test_learner_hypothesis_ledger.py
tests/test_learner_hypothesis_lineage_provenance.py
tests/test_learner_hypothesis_model_validation.py
```

No M7C production module is introduced.

## Qualified semantic records

### `HypothesisActorProvenance`

Identifies the human, model, or deterministic/system authoring authority for hypothesis
creation, revision, lifecycle changes, or semantic mapping.

Material provenance includes:

```text
actor kind
actor identity
actor version
rubric / instruction fingerprint
optional run identity
```

This prevents a model- or analyst-derived mapping from being flattened into anonymous
truth.

### `HypothesisContextRef`

Exact reference to a context definition or provenance-bound context coding.

M7B does not infer opaque semantic similarity. A context-bounded hypothesis revision
may accept only evidence links whose exact context refs lie within that revision's
recorded scope.

### `LearnerHypothesis`

Stable participant-specific lineage identity.

The lineage binds:

```text
participant identity
origin proposal fingerprint
creation time
origin author provenance
```

The hypothesis statement itself is not mutated in place. It lives in append-only
`HypothesisRevision` records.

### `HypothesisRevision`

Append-only version of the descriptive hypothesis statement and scope.

Each revision preserves:

```text
hypothesis lineage
revision number
statement
claim kind = descriptive_pattern
scope
context refs
competing-hypothesis refs
unresolved alternative notes
exact parent revision ref
revision reason
author provenance
creation time
```

Revision 1 is created atomically with the hypothesis lineage and must reproduce the
lineage's exact origin-proposal fingerprint.

Later revisions must form an exact contiguous history:

```text
revision 1
→ revision 2 citing exact revision-1 id + fingerprint
→ revision 3 citing exact revision-2 id + fingerprint
→ ...
```

A later revision cannot be accepted merely because it repeats the same
`hypothesis_id`.

### `HypothesisLifecycleEvent`

Append-only explicit authority-history event.

Initial M7B lifecycle transitions are deliberately terminal:

```text
active → retired
active → superseded
```

M7B defines no reactivation transition.

A `superseded` event must cite a different hypothesis lineage for the same participant.
A `retired` event cannot cite a replacement.

Historical revisions and evidence links remain preserved regardless of lifecycle state.

### `HypothesisM6EvidenceRef`

Typed exact reference to one qualified M6 record:

```text
reasoning_context
reasoning_assessment
reasoning_assertion
```

Unknown M6 reference kinds are rejected.

### `HypothesisMappingProvenance`

Separates two mapping authorities:

```text
deterministic_mapping
coded_mapping
```

A coded mapping must carry explicit actor provenance. It cannot be represented as an
unattributed relation label.

### `HypothesisEvidenceLink`

Immutable relation between one exact hypothesis revision and one exact M6 evidence
unit.

Initial relation vocabulary is exactly:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
```

The relation is **recorded evidence mapping**, not recurrence status.

Each link binds:

```text
exact hypothesis revision
participant
exact M6 reasoning context
exact M6 assessment
selected exact M6 assertions
source position
source game
relation
context refs
measurement condition
mapping basis/provenance
creation time
```

The source position, game, participant, and measurement condition are derived from the
validated M6 context rather than supplied independently by the caller.

## Atomic hypothesis creation

`create_learner_hypothesis(...)` creates a stable lineage and revision 1 together.

The origin proposal fingerprint binds:

```text
participant
statement
claim kind
scope definition
context refs
competing hypothesis refs
unresolved alternative notes
```

The stable lineage identity then also binds creation time and origin-author provenance.

This avoids a circular identity where the lineage would have to cite a revision that in
turn already needs the lineage ID.

## Revision-lineage validation

`record_hypothesis_revision(...)` validates the entire supplied history before appending
one revision.

It requires:

- revision numbers to be unique and contiguous from 1;
- every revision to belong to the same hypothesis lineage;
- revision 1 to match the origin proposal fingerprint;
- every later revision to cite the exact immediately previous revision;
- chronology not to run backward;
- competing hypotheses to belong to the same participant;
- a hypothesis not to cite itself as a competing hypothesis.

`record_hypothesis_evidence_link(...)` independently revalidates lineage membership.
For revision 1, the origin proposal is sufficient. For revision 2+, the caller must
supply the exact revision history so a forged hash-consistent later revision cannot be
accepted solely because its `hypothesis_id` matches.

## M6 provenance revalidation

M7B does not trust a caller-provided M6 reference bundle merely because its IDs look
plausible.

Before recording an evidence link, it revalidates:

```text
ReasoningDiscrepancyContext fingerprint + identity
participant identity
M6 assessment fingerprint + identity
assessment/context identity match
measurement-condition match
assessment stage membership
selected assertion fingerprint + identity
assertion/context identity match
assertion/assessment policy match
assertion stage membership
assertion exact membership in assessment.assertion_refs
assertion fact refs ⊆ assessment.fact_refs
assertion coding refs ⊆ assessment.coding_refs
assertion contradiction refs ⊆ assessment.contradictory_evidence_refs
```

A hash-consistent M7 record therefore cannot legitimize unrelated or substituted M6
evidence.

## Closed record vocabularies

M7B enforces its frozen contract at runtime rather than relying only on static typing.

The immutable records reject unknown values for:

```text
actor kind
hypothesis claim kind
lifecycle kind
M6 evidence-ref kind
mapping basis kind
evidence relation
measurement condition
```

This prevents a caller from directly constructing a structurally valid record using
out-of-contract semantics and passing it downstream.

## Deterministic identity

M7B follows the repository's content-addressed identity convention:

```text
SHA-256(canonical JSON of material content)
```

Qualified record IDs are derived from those fingerprints, including:

```text
learner_hypothesis_<fingerprint prefix>
hypothesis_revision_<fingerprint prefix>
hypothesis_lifecycle_<fingerprint prefix>
hypothesis_evidence_<fingerprint prefix>
```

Canonical ordering is applied where caller order is non-semantic, including context
refs, competing hypothesis refs, alternative notes, and selected assertion refs.

Given identical frozen inputs and explicit mapping records, M7B replay produces
identical identities.

## Control and no-discrepancy anti-collapse rules

M7B deliberately contains no special rule such as:

```text
M4 control → contradicts
```

or:

```text
M6 no_supported_discrepancy → successful_counterexample
```

Instead, the caller must record an explicit M7 evidence relation under explicit mapping
provenance.

The focused tests include a `no_supported_discrepancy` assessment mapped explicitly as
`unclear`, demonstrating that M7B preserves the upstream status rather than turning it
into automatic negative evidence.

Whether a control/no-discrepancy case is valid counterevidence under the same
hypothesis-relevant dimension remains an M7C policy/qualification responsibility.

## Multiple links from one position do not create recurrence

M7B permits multiple evidence links to one canonical position when different mappings
or coders need to be preserved.

For example:

```text
position X → deterministic supports link
position X → coded unclear link
```

Those are two immutable mapping records, not two recurrence units.

M7B contains no `recurrence_status`, recurrence counter, or independence calculation.
The M7A one-position/one-recurrence-unit rule will be enforced when M7C implements
aggregation policy.

## Qualification corpus

The focused M7B suite covers:

- deterministic hypothesis + revision-1 creation;
- record immutability;
- participant identity affecting lineage identity;
- exact append-only parent revision refs;
- contiguous history enforcement;
- same-participant competing-hypothesis constraint;
- terminal retirement history;
- same-participant supersession preserving both lineages;
- cross-participant supersession rejection;
- exact M6 provenance binding;
- canonical input ordering;
- participant mismatch rejection;
- forged M6 context fingerprint rejection;
- forged M6 assessment fingerprint rejection;
- assertion-not-cited-by-assessment rejection;
- assertion-from-other-context rejection;
- coded mapping requiring actor provenance;
- mapping-basis mismatch rejection;
- explicit evidence relation changing record identity;
- context-bounded evidence scope;
- `no_supported_discrepancy` not becoming automatic counterevidence;
- multiple links from one position without recurrence state;
- later-revision link requiring exact lineage history;
- closed actor/mapping/M6-ref/lifecycle/relation/measurement vocabularies.

The exact qualified implementation head is:

```text
d894a3f837ff033fcee554118ec4c711e86c1032
```

GitHub Actions run:

```text
34307964917
```

Qualification result:

```text
256 passed
8 intentional external-engine skips in the normal suite
29 / 29 focused M7B tests passed
Ruff PASS
external Stockfish integration PASS
```

PR #31 was merged from that exact qualified head as:

```text
f2ecea6c04927623f3a8b41f92a40d443c9cdeae
```

The qualified head and merge commit are tree-identical (`files: []` in the commit
comparison).

Post-merge authoritative `main` Actions run:

```text
34308142701
```

passed both `test-and-lint` and `stockfish-integration`.

## M7B claim ceiling

After M7B qualification the repository may claim that it can:

- create a stable participant-specific descriptive hypothesis lineage;
- preserve append-only statement/scope revisions;
- preserve explicit retirement or supersession history;
- attach explicit provenance-bound support, contradiction, successful-counterexample,
  context-exception, or unclear mappings to exact qualified M6 evidence;
- reject participant/provenance/lineage/vocabulary substitutions;
- replay those immutable records deterministically.

It may **not** yet claim that:

- one or more links constitute recurrence;
- a hypothesis has isolated, candidate, supported, contradicted, or unclear recurrence
  status under M7 policy;
- evidence units are independent;
- common structure has been policy-qualified;
- a current learner-hypothesis state has been derived;
- a supported descriptive recurrence is a causal cognitive mechanism or permanent trait;
- a hypothesis is training-eligible;
- any intervention should be prescribed or is effective;
- learning, transfer, or mastery occurred.

## Stop boundary

M7B is qualified. The only next authorized implementation slice after repository-status
reconciliation is:

> **M7C — recurrence assessment + derived ledger state.**

M7C must implement the frozen `HypothesisAssessmentPolicy`, recurrence/independence
accounting, explicit compatibility/context rules, deterministic `HypothesisAssessment`,
structured evidence summaries, and rebuildable `HypothesisLedgerSnapshot` derivation.

M7Q remains a later qualification gate. M8 remains unauthorized until M7Q closes the
full M7 surface.
