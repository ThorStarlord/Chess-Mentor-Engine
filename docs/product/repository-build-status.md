# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation/milestone status only  
**Updated for:** M8 Evidence-Aware Tutor Session qualification  
**Relationship to roadmap:** this file complements
`chess-mentor-engine-repository-build-plan.md`. The roadmap preserves the conceptual
sequence and historical planning rationale; this file is the authority for which
milestones are actually qualified, frozen, implemented, authorized, or not started.

## Why this file exists

The original repository build plan intentionally preserved early planning language.
Its later sections still describe M1 as the recommended next implementation target,
which is now historical rather than current. Rewriting the whole planning artifact
would risk erasing useful design provenance.

Therefore:

```text
conceptual sequence / historical rationale
→ chess-mentor-engine-repository-build-plan.md

current implementation status
→ repository-build-status.md + CONTEXT.md

ratified technical decisions
→ docs/decisions/*.md

implemented technical boundaries / qualification records
→ docs/architecture/*.md
```

If the roadmap's time-sensitive `Current recommendation` conflicts with this file,
this file and `CONTEXT.md` govern current status.

## Current milestone board

```text
M1 — Trustworthy Chess Evidence Substrate       QUALIFIED
M2 — Deterministic Chess Feature Extraction     QUALIFIED
M3 — Engine Evidence                            QUALIFIED
  M3A — Engine Evidence Contract                FROZEN
  M3B — Precomputed provider                    QUALIFIED
  M3C — External UCI provider                   QUALIFIED

M4 — Diagnostic Position Selection              QUALIFIED
  M4A — Selection contract                      FROZEN
  M4B — DecisionComparison                      QUALIFIED
  M4C — SelectionSignal + DiagnosticCandidate   QUALIFIED
  M4D — SelectionPolicy + CandidateBatch        QUALIFIED
  M4Q — Full M4 qualification                   QUALIFIED

M5 — Player Decision Evidence                   QUALIFIED
  M5A — Player Decision Evidence contract       FROZEN
  M5B — Immutable evidence model                QUALIFIED
  M5C — Capture/freeze state machine            QUALIFIED
  M5Q — Full M5 qualification                   QUALIFIED

M6 — Reasoning Discrepancy                      QUALIFIED
  M6A — Reasoning Discrepancy contract          FROZEN
  M6B — Deterministic comparison facts          QUALIFIED
  M6C — Coded local discrepancy assessment      QUALIFIED
  M6Q — Full M6 qualification                   QUALIFIED

M7 — Learner Hypothesis Ledger                  QUALIFIED
  M7A — Learner Hypothesis Ledger contract      FROZEN
  M7B — Immutable hypothesis/evidence ledger    QUALIFIED
  M7C — Recurrence assessment + ledger state    QUALIFIED
  M7Q — Full M7 qualification                   QUALIFIED

M8 — Evidence-aware Tutor Session               QUALIFIED
M9 — Training Interventions                     NOT STARTED / NEXT AUTHORIZED
M10 — Transfer / Mastery Evidence               NOT STARTED
M11 — Longitudinal Learner State                NOT STARTED
M12+ — CLI/UI/richer LLM productization         NOT STARTED
```

## Qualified objective evidence chain

The repository has this qualified objective evidence-acquisition path through M4:

```text
PGN
→ CanonicalGame
→ CanonicalPosition
→ PositionContextPacket
→ PositionFeaturePacket
→ PositionAnalysis
→ DecisionComparison
→ SelectionSignal[]
→ SelectionPolicy
→ SelectionDecision / DiagnosticCandidate
→ DiagnosticCandidateBatch
```

M4 as a whole is qualified under the frozen ADR 0003 contract. It can derive
transparent, provenance-rich objective decision comparisons and use versioned
deterministic policies to select bounded candidate sets containing both potentially
informative decisions and successful controls.

See:

- `docs/architecture/diagnostic-position-selection.md`;
- `docs/architecture/decision-comparison.md`;
- `docs/architecture/selection-signals-and-candidates.md`;
- `docs/architecture/selection-policy-and-batches.md`;
- `docs/architecture/m4-qualification.md`.

## Qualified M5 Player Decision Evidence

M5 is qualified under the frozen M5A contract and ADR 0004.

The authority split remains:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

The qualified production evidence path is:

```text
qualified M4 selected position / candidate / batch
→ PlayerDecisionContext
→ versioned PromptDefinition / PromptPresentation
→ PlayerResponseEvidence
→ EvidenceFreeze
→ optional later pre-reveal stage(s)
→ ExposureEvent / ProtocolDeviation as applicable
→ ObjectiveEvidenceReveal
→ optional post-reveal evidence
```

### M5B immutable model

M5B qualifies the immutable record/identity layer for:

```text
PlayerDecisionContext
PromptDefinition
PromptPresentation
PlayerResponseEvidence
ExposureEvent
EvidenceFreeze
ObjectiveEvidenceReveal
```

Raw participant language is preserved verbatim. Structured participant values contain
only explicitly submitted values, ambiguous and illegal reported moves remain
representable without silent repair, prompt wording/version/rendering is provenance,
and `EvidenceFreeze` is the sole freeze authority for an exact response fingerprint.

### M5C capture/freeze sequencing

M5C qualifies deterministic interaction sequencing through a versioned
`CaptureProtocol` and immutable append-only `EvidenceCaptureSession` snapshots.
Clean runs enforce required prior freezes and objective-reveal gates. Real-world
protocol deviations may instead be preserved with explicit `ProtocolDeviation`
provenance. Exposure/instrument-awareness state remains auditable, amendments cite
rather than rewrite frozen evidence, and pre-reveal evidence remains separate from
post-reveal reflection.

### M5Q full qualification

M5Q qualifies the whole M5A claim surface with a frozen corpus covering:

```text
clean minimal-only capture
clean minimal + standardized-probe capture
instrument-aware provenance
contaminated exposure
early later-stage presentation
early objective reveal
append-only amendment
ambiguous reported move
illegal reported move
post-reveal reflection
deterministic replay / identity
historical Pilot 003/004 artifact preservation
```

The qualification path starts from a real deterministic M1→M4 selected control and
binds M5 context to the selected candidate and batch before capture begins. The corpus
also reproduces the exact frozen Pilot 003 A1 prompt and six A2 questions while
preserving the research instruments as immutable historical authorities rather than
universal product prompt truth.

See:

- `docs/architecture/player-decision-evidence.md` — M5A contract;
- `docs/architecture/player-decision-evidence-model.md` — M5B record;
- `docs/architecture/player-decision-evidence-capture.md` — M5C record;
- `docs/architecture/m5-qualification.md` — full M5Q qualification;
- `docs/decisions/0004-player-decision-evidence-contract.md` — ADR 0004.

## Qualified M6 Reasoning Discrepancy

M6 is qualified under the frozen M6A contract and ADR 0005.

M6 is the first production layer authorized to compare qualified objective evidence
with qualified participant-reported evidence. Its scope remains local to one selected
position / evidence context.

The governing boundary remains:

```text
qualified objective evidence
+ qualified Player Decision Evidence
→ position-local Reasoning Discrepancy assessment
```

while preserving:

```text
local discrepancy
!= unreported cognition
!= causal cognitive mechanism
!= recurrence
!= stable learner weakness
!= learner hypothesis
!= pedagogical prescription
```

### M6A frozen semantic split

M6A separates five semantic records:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
ReasoningCoding
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

The central production distinction remains:

```text
deterministic comparison fact
!= analyst/model semantic coding
```

The hard anti-overclaiming rules remain:

```text
not explicitly reported
!= not considered
!= not recognized
!= not generated
```

and:

```text
missing dimension
→ not_observed
→ not a discrepancy by default
```

and:

```text
partial / bounded / incompatible objective evidence
→ not_comparable for the affected relation
```

Engine judgment remains distinguishable from deterministic chess truth. Divergence
from one engine PV is not automatically an error when multiple legal/comparable lines
may exist.

### M6B qualified deterministic comparison facts

M6B is qualified and implements the first two frozen semantic records needed for the
deterministic layer:

```text
ReasoningDiscrepancyContext
DiscrepancyFact
```

The production implementation lives in:

```text
src/chess_mentor_engine/learning/
```

M6B binds the local context to the exact M4 `DiagnosticCandidate`, optional
`DiagnosticCandidateBatch`, `DecisionComparison`, retained selection signals, optional
M2 features/M3 analyses, and exact frozen M5 pre-reveal evidence. It preserves the
M5 measurement condition as `clean`, `instrument_aware_clean`, `deviating`, or
`contaminated` rather than normalizing the evidence history.

The qualified deterministic fact families are:

```text
REPORTED_SELECTED_MOVE_RELATION
EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION
EXPECTED_REPLY_RELATION
EXPECTED_CONTINUATION_RELATION
```

with descriptive relations:

```text
match
conflict
not_explicitly_reported
ambiguous
not_observed
not_comparable
```

Key conservative semantics are executable:

```text
engine rank-1 absent from explicit structured candidate list
→ not_explicitly_reported
→ NOT "never considered" or "failed candidate generation"

legal expected reply/continuation differs from one non-forced engine PV
→ not_comparable
→ NOT automatic conflict

illegal move/reply/continuation under deterministic chess rules
→ conflict under deterministic chess authority

missing structured dimension
→ not_observed

missing/mismatched comparable engine evidence
→ not_comparable or explicit rejection
```

M6B never parses `raw_response`. The raw response remains part of the cited M5 evidence
identity so M6C can add separate coded interpretation without rewriting the participant
evidence or deterministic M6B fact.

See `docs/architecture/reasoning-discrepancy-facts.md` for exact implementation and
qualification provenance.

### M6C qualified coded local assessment

M6C is qualified and implements the remaining position-local interpretation records
frozen by M6A:

```text
ReasoningCoding
ReasoningAssessmentPolicy
ReasoningDiscrepancyAssertion
ReasoningDiscrepancyAssessment
```

The authority split is explicit:

```text
M5 participant evidence
!= M6B deterministic fact
!= M6C human/model coding
!= M6C supported local assertion
```

`ReasoningCoding` is append-only derived evidence with exact player/objective/fact
references, coder kind (`human` or `model`), coder/run identity/version,
rubric/instruction fingerprint, optional confidence/uncertainty, timestamp, and
content-addressed identity. Different coders/runs may disagree; M6C preserves rather
than overwrites that disagreement.

`ReasoningAssessmentPolicy` is versioned and material. It binds eligible pre-reveal
stage kinds, allowed measurement conditions, required objective evidence, permitted
fact kinds/codes, coding requirements, supported parameters, and `position_local`
claim scope. Material policy changes therefore change assessment identity.

Initial deterministic assertion support is intentionally narrow:

```text
engine-rank1 candidate not explicitly reported
+ policy strong_candidate_basis=engine_rank1
→ STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED

EXPECTED_REPLY_RELATION + conflict
→ EXPECTED_OPPONENT_REPLY_CONFLICT

EXPECTED_CONTINUATION_RELATION + conflict
→ EXPECTED_CONTINUATION_CONFLICT
```

Intrinsically semantic codes such as feature relevance, resulting-evaluation conflict,
stated target without executable realization, incomplete rationale, and
`OTHER_LOCAL_DISCREPANCY` require explicit coding provenance. Correct-move/incomplete-
rationale additionally requires a matching deterministic selected-move fact, producing
a mixed assertion rather than allowing coding to manufacture move correctness.

M6C emits only:

```text
discrepancy_supported
no_supported_discrepancy
unclear
unscorable
```

`no_supported_discrepancy` is dimension-bounded. `not_observed` alone cannot become a
negative result. Material same-code/same-stage coding disagreement is preserved as
uncertainty rather than last-write-wins. A1 and A2 remain distinct evidence stages, so
an A1/A2 change is not silently labeled a correction or intervention effect.

Deviating/contaminated evidence is scorable only under an exact policy that explicitly
allows its measurement condition, and the condition remains attached.

The final implementation also revalidates embedded coding/player/objective/fact/stage
provenance at assessment time. Recomputing a record's own hash after substituting
unrelated evidence does not make that record acceptable.

See `docs/architecture/reasoning-discrepancy-assessment.md` for exact implementation,
superseded-candidate, qualification, merge, and post-merge provenance.

### M6Q full qualification

M6Q qualifies the complete frozen M6A surface across M6B + M6C without adding new
production behavior. Its focused 20-case corpus proves together:

- deterministic, coded, and mixed assertion paths;
- all four assessment statuses;
- dimension-bounded `no_supported_discrepancy`;
- missing evidence as `not_observed` rather than a false discrepancy;
- ambiguous evidence without guessed normalization;
- unavailable comparable objective evidence as `not_comparable`;
- incompatible objective provenance rejection;
- deterministic legality conflicts for impossible replies/continuations;
- A1/A2 stage separation and post-reveal isolation;
- clean instrument-aware, deviating, and contaminated measurement conditions;
- explicit policy gating for deviating/contaminated evidence;
- same-stage coding disagreement preserved as `unclear`;
- raw prose not overriding structured deterministic comparison;
- a successful M4 control that still contains a position-local reasoning discrepancy;
- deterministic full-chain replay/identity;
- byte-identical preservation of the seven frozen Pilot 003/004 research artifacts.

The exact qualification-corpus head was:

```text
d500cb19bb8e16775ca829fda69b7accfa93d629
```

with GitHub Actions run `34304053934`:

```text
227 passed
8 intentional external-engine skips in the normal suite
20 / 20 M6Q focused cases passed
Ruff PASS
external Stockfish integration PASS
```

No production source change was required to close M6Q.

See `docs/architecture/m6-qualification.md` for the complete qualification record.

### Research boundary

Pilot 004's discrepancy taxonomy informed M6A, but its research codes remain historical
research authority rather than universal product learner categories. In particular,
its `strong candidate not generated` wording remains conservatively represented at the
production evidence boundary as `not_explicitly_reported` unless explicit coded local
evidence supports a stronger permitted position-local claim.

Pilot 004's recurrence policy remains outside M6. Cross-position recurrence, controls
and contradictions across positions, competing explanations, and learner hypotheses
belong to M7.

## Qualified M7 Learner Hypothesis Ledger

M7 is fully qualified under the frozen M7A contract and ADR 0006.

The governing escalation is:

```text
qualified position-local M6 evidence
        ↓
explicit hypothesis/evidence mapping
        ↓
versioned cross-position assessment policy
        ↓
participant-specific recurrence assessment
        ↓
append-only hypothesis history
```

while preserving:

```text
local discrepancy
!= recurring pattern
!= causal cognitive mechanism
!= permanent learner trait
!= pedagogical prescription
```

M7A freezes seven semantic records:

```text
LearnerHypothesis
HypothesisRevision
HypothesisLifecycleEvent
HypothesisEvidenceLink
HypothesisAssessmentPolicy
HypothesisAssessment
HypothesisLedgerSnapshot
```

The initial hypothesis claim kind is `descriptive_pattern`. Evidence relations are
`supports`, `contradicts`, `successful_counterexample`, `context_exception`, and
`unclear`. Recurrence assessment status is separately
`insufficient / isolated / candidate_recurrence / supported_recurrence / contradicted /
unclear`, while authority lifecycle is `active / retired / superseded` and is recorded
through append-only lifecycle events.

Hard M7 anti-collapse rules include:

```text
one canonical participant-position
→ one recurrence unit

M4 operational control
!= M7 contradiction / successful counterexample

M6 no_supported_discrepancy
!= M7 contradiction / successful counterexample

supported recurrence
!= causal explanation
!= training eligibility
```

Any control or no-discrepancy case becomes M7 counterevidence only when the exact
hypothesis-relevant dimension was observed, assessable, comparable, context-matching,
and explicitly mapped under a versioned M7 rule/coding.

Recurrence requires more than one distinct qualifying position. Common structure,
independence, M6-policy/stage/measurement compatibility, contradiction handling, and
review obligations are explicit versioned policy. M7 freezes no universal weakness
score or confidence scalar.

Pilot 004 remains immutable research authority. M7 preserves its requirements for
independent positions, traceable common structure, comparable evidence, challenge
cases, competing explanations, future testing, and hypotheses that may disappear while
tightening the production authority boundaries above.

### M7B qualified immutable hypothesis/evidence ledger

M7B implements and qualifies the immutable record/link layer authorized by M7A. The
production surface provides:

```text
LearnerHypothesis
HypothesisRevision
HypothesisLifecycleEvent
HypothesisEvidenceLink
```

plus exact refs and provenance records required to bind those records safely.

M7B can:

- create stable participant-specific descriptive hypothesis lineages;
- create revision 1 atomically from a material origin-proposal fingerprint;
- append exact contiguous statement/scope revisions with parent fingerprints;
- preserve terminal `retired` / `superseded` lifecycle events without rewriting prior
  history;
- record explicit `supports / contradicts / successful_counterexample /
  context_exception / unclear` relations to exact qualified M6 evidence;
- distinguish deterministic mapping from provenance-bound coded mapping;
- revalidate exact M6 context/assessment/assertion identities and embedded
  fact/coding/contradiction provenance;
- reject forged later revisions that merely repeat a lineage ID without exact history;
- reject out-of-contract record vocabularies;
- derive deterministic content-addressed identities under canonical ordering.

The qualified implementation head is:

```text
d894a3f837ff033fcee554118ec4c711e86c1032
```

with Actions run `34307964917`:

```text
256 passed
8 intentional external-engine skips in the normal suite
29 / 29 focused M7B tests passed
Ruff PASS
external Stockfish integration PASS
```

PR #31 merged that exact qualified head as:

```text
f2ecea6c04927623f3a8b41f92a40d443c9cdeae
```

The qualified head and merge are tree-identical. Post-merge Actions run `34308142701`
passed both `test-and-lint` and `stockfish-integration`.

### M7C qualified recurrence assessment + derived ledger state

M7C implements and qualifies the recurrence-assessment and rebuildable current-state
layer frozen by M7A.

The qualified production surface provides:

```text
HypothesisAssessmentPolicy
CompetingExplanationReview
HypothesisChallengeReview
HypothesisRecurrenceUnit
HypothesisEvidenceSummary
HypothesisAssessment
HypothesisLedgerSnapshot
```

M7C enforces one participant + canonical position as one recurrence unit, so multiple
links or coders cannot inflate recurrence. Conflicting relations on one position become
one `mixed` unit and an `unclear` result.

The assessment policy materially binds M6 status/code/measurement eligibility,
M6-policy compatibility, stage compatibility, context matching, recurrence-unit rule,
independence rule, candidate/supported thresholds, challenge-review requirements,
competing-explanation review, contradiction behavior, and participant-specific claim
scope. Candidate recurrence cannot be configured below two independent supports.

Evidence incompatible with the exact policy is excluded with structured reasons rather
than silently normalized. M7C independently revalidates exact M6 assessment/assertion
identity, policy, stage, context, measurement, and chronology, plus the exact hypothesis
revision lineage. Revision 2+ requires the full contiguous history.

Challenge review is provenance-bearing. Required but incomplete contradiction review
prevents a `contradicted` verdict; required but incomplete counterexample review
prevents promotion to `supported_recurrence`. A successful counterexample becomes a
contradiction only under an exact policy that says so.

The qualified status vocabulary is exactly:

```text
insufficient
isolated
candidate_recurrence
supported_recurrence
contradicted
unclear
```

`HypothesisLedgerSnapshot` rebuilds the current revision, latest assessment for that
current revision, and separate `active / retired / superseded` lifecycle authority from
append-only history. Old-revision assessments do not become current after revision,
and dangling/superseding history is rejected.

The exact qualified implementation head is:

```text
e6f6debee79ea7780b5dbfc1732def802d9bd8b4
```

with Actions run `34311289575`:

```text
294 passed
8 intentional external-engine skips in the normal suite
38 / 38 focused M7C tests passed
Ruff PASS
external Stockfish integration PASS
```

PR #33 merged that exact qualified head as:

```text
df6bee774259ac98e8edbcdd2ab17306c9c09873
```

The qualified head and merge are tree-identical. Post-merge Actions run `34311520576`
passed both `test-and-lint` and `stockfish-integration`.

See `docs/architecture/learner-hypothesis-recurrence-assessment.md` for the complete
M7C implementation and qualification record.

### M7Q full qualification

M7Q qualifies the complete frozen M7A claim surface across M7B + M7C without adding
new production behavior. Its frozen qualification contract and focused suite prove
together:

- one support is isolated rather than recurrence;
- multiple mappings/codings of one participant-position cannot inflate recurrence;
- the configured independence rule is material;
- independent support can produce candidate recurrence under the exact policy;
- policy-qualified support plus required review can produce supported recurrence;
- contradiction and successful-counterexample evidence are retained alongside support;
- M4 controls and M6 `no_supported_discrepancy` are not automatic counterevidence;
- context exceptions constrain scope rather than disappearing;
- unclear evidence cannot manufacture support;
- A1/A2 stage compatibility remains explicit;
- measurement conditions remain preserved and policy-gated;
- M6 policy-family compatibility remains explicit;
- competing explanations remain real review obligations;
- hypothesis revision preserves old assessments without relabeling them as current;
- retirement preserves historical assessment evidence;
- supersession preserves both hypothesis lineages;
- assessment and ledger-snapshot replay/fingerprints are deterministic under frozen
  inputs;
- no training-eligibility, intervention, or pedagogy claim appears in qualified M7
  output;
- the seven frozen Pilot 003/004 research artifacts remain byte-identical.

The exact M7Q qualification-corpus head was:

```text
334f9c769e50046078d5508ecce4fac9d52cd70a
```

with GitHub Actions run `34317869412`:

```text
307 passed
8 intentional external-engine skips in the normal suite
13 / 13 M7Q focused tests passed
Ruff PASS
external Stockfish integration PASS
```

No production source change was required to close M7Q.

See `docs/architecture/m7-qualification.md` for the complete qualification record.

## Qualified M8 Evidence-Aware Tutor Session

M8 is qualified under ADR 0007 and the implementation record in
`docs/architecture/evidence-aware-tutor-session.md`.

The bounded workflow is:

```text
qualified M4 selected position
+ exact M5 PlayerDecisionContext / CaptureProtocol
→ deterministic position presentation
→ minimal participant response
→ optional standardized diagnostic probe
→ all planned pre-reveal evidence frozen
→ qualified objective evidence reveal
→ exact final-capture-bound M6 comparison
→ optional complete active-current M7 context
→ provenance-bearing session-local explanation
→ immutable completed TutorSession
```

M8 qualifies `TutorSession`, content-addressed transition events, deterministic
position presentation, M5-owned capture/freeze/reveal sequencing, exact M6 provenance
binding, complete active-current M7 context binding, and explanation provenance.

The focused 13-case qualification suite proves:

- deterministic session start without accidental objective reveal;
- exact deterministic position-packet presentation;
- rejection of a packet not bound to the M5 context;
- rejection of pre-reveal tutoring-intervention prompts;
- objective reveal blocked until every planned pre-reveal stage is frozen;
- immutable prior snapshots across capture transitions;
- M6 comparison blocked before reveal;
- M6 comparison bound to the exact final revealed capture snapshot;
- M7 context cannot cherry-pick among active current hypotheses;
- explanation is post-comparison and provenance-bearing;
- the complete frozen workflow reaches `completed` in exact event order;
- identical full-session replay is deterministic;
- serialized M8 state contains no M9 training/intervention/mastery authority.

The first fully green implementation head before status reconciliation was
`a86110ce517baabaa728c1f32a6b1f0134939960`, with GitHub Actions run
`34327281542` passing the full test/lint and external Stockfish gates.

M8's claim ceiling remains sequencing/provenance only:

```text
session-local evidence explanation
!= training eligibility
!= intervention selection
!= intervention efficacy
!= learning
!= transfer
!= mastery
```

## Current authorized next task

> **M9 — Training Interventions only.**

M9 is authorized next to define a versioned, inspectable intervention registry and
selection boundary over explicitly eligible learner evidence. It may decide which
intervention record applies under an exact policy, but it must keep diagnosis,
intervention selection, outcome observation, and efficacy claims separate.

M9 is **not started**. This status update authorizes that next milestone; it does not
implement any training intervention behavior.

M9 must not silently broaden into:

- claiming that intervention selection proves intervention effectiveness;
- transfer or mastery state;
- a universal learner weakness/confidence scalar;
- claims that training caused improvement without qualified outcome evidence;
- CLI/web productization unrelated to the bounded intervention contract.

M10 Transfer / Mastery Evidence and later longitudinal/productization milestones remain
unqualified.

## Current claim ceiling

The repository may claim that it has:

- qualified deterministic chess state;
- qualified deterministic board features;
- qualified provenance-bound engine evidence;
- a fully qualified Diagnostic Position Selection milestone;
- qualified objective `DecisionComparison`, `SelectionSignal`, `SelectionPolicy`, and
  `DiagnosticCandidateBatch` evidence;
- a fully qualified M5 Player Decision Evidence milestone;
- a fully qualified M6 Reasoning Discrepancy milestone;
- a fully qualified M7 Learner Hypothesis Ledger milestone;
- a qualified, deterministic, replayable M8 Evidence-Aware Tutor Session milestone.

Qualified M7 may report bounded statements such as:

- one exact participant-position is one recurrence unit under the cited policy;
- an exact evidence link was excluded because its M6 status, code, measurement
  condition, policy, stage, or context was incompatible with the cited M7 policy;
- an exact hypothesis revision has `insufficient`, `isolated`,
  `candidate_recurrence`, `supported_recurrence`, `contradicted`, or `unclear` status
  under the cited material policy and exact frozen evidence set;
- the cited supporting recurrence units satisfy the policy's explicit independence
  rule;
- contradiction, successful-counterexample, context-exception, unclear, and
  competing-explanation review provenance is preserved;
- hypothesis revisions, retirement, and supersession preserve append-only history;
- current learner-hypothesis ledger state can be rebuilt deterministically from exact
  append-only revisions, assessments, and lifecycle events;
- authority lifecycle remains distinct from recurrence status.

Qualified M8 may additionally report bounded statements such as:

- the exact deterministic position context shown before response capture;
- the exact pre-reveal prompt/response/freeze sequence;
- that objective evidence was revealed only after every planned pre-reveal freeze;
- the exact M6 comparison attached to the final revealed capture snapshot;
- the complete active-current M7 context attached to an explanation, when present;
- the human/model/template provenance of the explanation text;
- the exact immutable event sequence and snapshot fingerprint of a completed session.

After M8, the repository may **not** yet claim that:

- an omitted move was never considered, recognized, or generated;
- a coder/model judgment is objective chess truth;
- `supported_recurrence` establishes a causal cognitive mechanism;
- any recurrence status is a permanent learner trait;
- the system has a universal weakness/confidence scalar;
- a supported descriptive hypothesis is automatically training-eligible;
- an intervention is warranted or effective;
- tutoring efficacy has been demonstrated;
- learning, transfer, or mastery has occurred.

## Stop boundary

M5, M6, M7, and M8 are fully qualified. **M9 — Training Interventions — is the only
next authorized milestone slice and remains NOT STARTED.** M10 transfer/mastery,
longitudinal persistence, CLI/UI, and broader productization remain outside the M8
qualification claim.