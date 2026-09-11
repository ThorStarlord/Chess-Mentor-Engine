# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:**
> [`repository-build-status.md`](repository-build-status.md)  
> **Latest completed milestone handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture map:** [`../architecture/architecture.md`](../architecture/architecture.md)

**Status:** Planning history plus future candidate roadmap  
**Current implementation boundary:** M34 — qualified / merged  
**Authority:** This document is a planning artifact. It does **not** create an
approved work-package queue, supersede ratified ADRs, or grant production/external
authority.

---

## 1. Why this document changed

The original build plan was written before the repository had implemented its first
bounded production milestones. It therefore described M1 and the early evidence
substrate as future work.

That is no longer true.

The repository is now qualified through M34, including deterministic chess evidence,
participant evidence, learner hypotheses, persistent tutoring, model/evaluator
boundaries, reviewed-coaching persistence, participant review, machine-consumer
fidelity, deterministic feedback traceability, and hermetic recovery reconciliation.

This plan now has four jobs:

1. preserve the durable product and evidence principles that motivated the build;
2. map the original roadmap into the capabilities already delivered through M34;
3. keep future directions explicitly **candidate** until a fresh live-`main` audit
   promotes them into an approved bounded package queue;
4. guide the transition from evidence/review infrastructure toward learner
   intelligence, tutoring policy, transfer, and a usable learning experience.

For present-tense implementation claims, always use
[`repository-build-status.md`](repository-build-status.md).

---

## 2. Product direction to preserve

Chess Mentor Engine should not become merely another engine-analysis UI.

The product hypothesis remains a **persistent chess tutor that learns how a
particular player makes decisions, grounds its conclusions in objective chess
evidence, and uses that evidence to choose what the player should practice next**.

The intended evidence chain remains:

```text
Chess Evidence
    ↓
Player Decision Evidence
    ↓
Position-Level Reasoning Discrepancy
    ↓
Recurring Pattern / Learner Hypothesis
    ↓
Training Intervention
    ↓
Transfer / Longitudinal Evidence
```

The implemented repository now adds operational/model/review layers around that
chain without changing the underlying authority principle:

```text
objective chess evidence
-> diagnostic selection
-> participant authorization / captured reasoning
-> discrepancy / learner hypothesis
-> controlled tutor state
-> deterministic mentor grounding
-> optional model rendering + bounded evaluator judgment
-> persisted reviewed coaching
-> deterministic review delivery / traceability
-> explicit intervention / outcome / longitudinal evidence
```

Three questions remain central:

1. What is objectively happening on the board?
2. What did the player actually notice, consider, and expect?
3. What recurring explanation is currently supported strongly enough to affect
   teaching?

Later operational questions are also explicit:

4. What did deterministic grounding establish versus what a model merely rendered?
5. What execution/review mechanics were mechanically verified versus what still
   requires external/human authority?
6. Did a selected intervention produce evidence of practice success or transfer?

The repository must keep those questions separate.

---

## 3. Durable evidence and authority principles

### 3.1 Chess truth is not player psychology

Engine analysis can establish bounded objective chess evidence. It cannot establish
what the player saw, why the player chose a move, or whether a causal cognitive
mechanism exists.

### 3.2 Player self-report is evidence, not objective truth

Participant responses are direct evidence of what the participant reports thinking.
They may be incomplete, reconstructed, mistaken, or affected by the measurement
sequence.

### 3.3 Analyst/model interpretation must remain derived

Reasoning discrepancies, recurring hypotheses, and model-authored explanations must
remain traceable to the evidence they consume. Derived interpretation cannot be
silently promoted into raw evidence.

### 3.4 Local discrepancies are not stable weaknesses

Use the evidence ladder:

```text
Position observation
-> Reasoning discrepancy
-> Candidate recurrence
-> Supported participant-specific hypothesis
-> Explicit training applicability / selection
-> Bounded intervention evidence
-> Near/far/real-game transfer evidence
```

Never skip levels.

### 3.5 Contradictory evidence is first-class

The system should preserve correct/control cases and evidence against a learner
hypothesis, not only examples that confirm it.

### 3.6 Provenance is product correctness

Important claims should be recoverable through exact source game/position identity,
engine provenance, participant evidence, learner hypothesis revisions, tutor state,
model/evaluator request identity, persisted review artifacts, and qualified source
fingerprints.

### 3.7 Deterministic grounding is different from model language

M16 remains the deterministic factual mentor-feedback ceiling. M19 may render prose
from that grounding, but request binding does not make arbitrary model prose true.

### 3.8 Evaluator acceptance is bounded judgment

M20 acceptance is not objective chess truth and is not proof of model safety,
pedagogical quality, or tutoring efficacy.

### 3.9 Mechanical verification is not semantic truth

M27/M32/M33 can prove important persistence, delivery, and traceability properties.
They do not establish that an arbitrary model explanation is pedagogically correct.

### 3.10 Recovery eligibility is not retry authority

M34 may classify a supplied synthetic execution history as `resume_eligible`. That
does not authorize or execute a real retry and does not establish external-side-
effect idempotency.

### 3.11 Infrastructure should increasingly be pulled by product needs

Through M34 the repository deliberately invested in evidence boundaries, persistence,
review, fidelity, provenance, and recovery. That investment is now mature enough
that infrastructure expansion should no longer be the default direction of travel.

Future infrastructure work should normally satisfy at least one of these tests:

- a learner-facing or tutoring capability cannot be implemented safely without it;
- a concrete current workflow has demonstrated a correctness or operability gap;
- a bounded external-adoption prerequisite requires an explicit repository contract;
- an existing authority boundary cannot be preserved through the next product step.

Avoid adding new schemas, persistence layers, provider abstractions, recovery models,
or validation surfaces merely because they are architecturally possible.

The preferred direction is increasingly:

```text
product need
-> explicit evidence/authority requirement
-> minimum supporting infrastructure
-> learner/tutor capability
-> qualification
```

rather than:

```text
speculative infrastructure
-> more infrastructure
-> eventual product use
```

---

## 4. Original target planes and where they landed

The original four-plane concept remains useful as a product map, although the
implemented architecture is now more detailed.

### Plane 1 — Chess Truth

Originally intended to own games, positions, legality, deterministic board state,
engine evaluations, candidates, principal variations, features, and provenance.

**Implemented primarily by M1–M4, M14–M18.**

### Plane 2 — Player Evidence

Originally intended to own raw player responses, reported candidates, expectations,
plans, confidence/uncertainty, timing, and exposure state.

**Implemented primarily by M5, M8, M21, and M23.**

### Plane 3 — Learning Inference

Originally intended to own reasoning discrepancies, recurrence, competing
explanations, hypothesis lifecycle, evidence-for, and evidence-against.

**Implemented primarily by M6–M7 and consumed explicitly by later tutor/feedback
layers.**

### Plane 4 — Pedagogy

Originally intended to own interventions, exercises, outcome evidence, transfer,
and competency claims.

**Implemented in bounded form by M9–M11.**

### Cross-cutting operational/review planes added later

The repository later earned additional explicit boundaries:

- **Operationalization:** M12–M18;
- **Model / evaluator boundaries:** M19–M22;
- **Persistent reviewed-coaching runtime:** M23–M27;
- **Review / consumer surfaces:** M28–M30;
- **Execution privacy and retry preflight:** M31;
- **Machine-consumer fidelity:** M32;
- **Deterministic feedback traceability:** M33;
- **Hermetic recovery reconciliation:** M34.

These additions refine the original plan rather than replacing its evidence-first
thesis.

---

# 5. Completed roadmap through M34

The original phased plan is now historical implementation provenance rather than a
future checklist.

| Original plan area | Current implementation outcome |
| --- | --- |
| Repository/authority reconciliation | Established through repeated milestone handoffs, build-status authority, CI qualification, and ADR/runbook discipline. |
| Canonical games/positions | M1 qualified canonical game/position evidence and source provenance. |
| Position context | M1/M2 plus later CLI surfaces provide deterministic position context. |
| Deterministic chess features | M2 qualified low-level deterministic features. |
| Engine abstraction | M3 qualified provenance-bound UCI evidence; provider behavior preserves bounds/mate/partial/failure semantics. |
| Diagnostic position selection | M4 and M18 qualified explicit versioned selection and game-window candidate/control batching. |
| Player decision evidence | M5 qualified frozen participant evidence; M21/M23 operationalized selection and capture-consent boundaries. |
| Reasoning discrepancy | M6 qualified position-local discrepancy facts/assessment. |
| Hypothesis / contradiction ledger | M7 qualified participant-specific append-only hypothesis lifecycle, support, challenge, and contradiction evidence. |
| Tutor session workflow | M8 qualified tutor state; M13/M23 operationalized replay-verifiable persistence. |
| Training intervention registry | M9 qualified explicit applicability/selection. |
| Transfer / outcome evidence | M10 qualified bounded practice, near/far, and real-game outcome evidence. |
| Longitudinal learner state | M11 qualified append-only longitudinal state. |
| CLI hardening | M12–M18 and M23–M30 established the current installed local operator surfaces. |
| LLM integration | M19/M24 created provider-neutral request/execution boundaries without selecting a production vendor. |
| Model-output evaluation | M20 created bounded evaluator judgment without promoting it to truth. |
| Cross-layer fidelity | M22 qualified representative evidence regimes across analysis/presentation/feedback/model/evaluator layers. |
| Persistent reviewed coaching | M25–M27 created review read models, atomic persistence, and mechanical verification. |
| Local review surface | M28–M30 created deterministic rendering, persisted bridging, and participant-scoped navigation/export. |
| Privacy / retry preflight | M31 qualified synthetic-canary and manual-retry-history validation. |
| Machine consumer contract | M32 qualified exact persisted-review delivery fidelity. |
| Deterministic feedback trace | M33 qualified component-level traceability for M16. |
| Recovery reconciliation | M34 qualified hermetic complete/resume-eligible reconciliation against persisted reviewed-coaching targets. |

The detailed milestone board and exact PR/CI evidence live in
[`repository-build-status.md`](repository-build-status.md).

---

# 6. Current product surfaces

## 6.1 CLI / operator surface already implemented

Installed commands currently include:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

The earlier recommendation to “CLI first” has therefore been substantially
fulfilled.

## 6.2 Local review UI already exists, but is intentionally not production UI

M28 provides a deterministic semantic HTML reference surface, and M29/M30 make
persisted participant-scoped review artifacts navigable/exportable.

The old “local web UI later” idea should now be split into two distinct statements:

```text
local deterministic reference rendering    -> implemented
production end-user frontend                -> not established
```

A real production frontend still requires explicit browser/device/a11y/usability,
privacy, authentication, localization, and interaction-design authority.

---

# 7. LLM integration status

The original recommendation was to avoid starting with an unconstrained LLM tutor
and instead give models structured evidence.

That principle is now implemented:

```text
M15 deterministic evaluation presentation
+ M6/M7 learner evidence
-> M16 deterministic grounded mentor feedback
-> M19 content-addressed model request
-> optional M24 provider execution
-> M19 model-authored language
-> optional M20 bounded evaluation
```

The LLM is downstream of qualified evidence rather than a substitute for the chess
substrate.

Future provider work must preserve these boundaries:

- no vendor becomes objective chess authority;
- no generated prose becomes raw participant evidence;
- evaluator acceptance remains bounded judgment;
- production secrets/transport/privacy/retry policy remain explicit external
  decisions.

---

# 8. Evaluation infrastructure status

The original plan called for evaluation of chess correctness, evidence sufficiency,
personalization, overclaiming, contradiction handling, pedagogical linkage, and
transfer.

The repository now has strong **mechanical/hermetic** evaluation infrastructure:

- M20 bounded model-output evaluation policy;
- M22 cross-layer fidelity matrix;
- M24 provider/evaluator execution conformance;
- M27 persisted execution verification;
- M31 synthetic privacy/retry preflight;
- M32 exact machine-consumer fidelity;
- M33 deterministic feedback provenance tracing;
- M34 recovery-history reconciliation.

What remains deliberately unproven is **empirical product/pedagogical efficacy**:

- whether users find the tutoring valuable;
- whether explanations are consistently understandable and useful in practice;
- whether interventions cause improvement;
- whether improvement transfers to new positions/games;
- whether the target segment and workflow are correct.

Mechanical qualification must not be used as a substitute for those claims.

---

# 9. Post-M34 strategic transition

The repository is at a transition point. Its strongest mature capabilities currently
cluster around:

```text
evidence
-> provenance
-> validation
-> persistence
-> review
-> delivery
-> traceability
-> recovery
```

The product thesis ultimately requires a further chain:

```text
many games
-> recurring player pattern
-> evidence-backed learner hypothesis
-> teaching priority
-> personalized intervention
-> later retest
-> evidence of improvement or contradiction
-> revised learner model
```

The next planning era should therefore be understood as a shift from **evidence
infrastructure toward learner intelligence and a closed pedagogical loop**.

## 9.1 Four planning layers

Use the following layers when evaluating future ideas:

```text
LAYER A — INFRASTRUCTURE / DELIVERY
provenance
persistence
validation
consumer contracts
recovery

              ↓ supports

LAYER B — LEARNER INTELLIGENCE
recurrence discovery
hypothesis synthesis
contradiction search
priority selection

              ↓ informs

LAYER C — PEDAGOGICAL LOOP
intervention selection
practice
retest
transfer
learner-state revision

              ↓ becomes

LAYER D — PRODUCT EXPERIENCE
batch game analysis
learner progress
interactive tutoring
later production frontend / hosted product
```

Layer A is already unusually mature. Future work should increasingly advance B, C,
or D, with new Layer-A construction introduced only when a concrete downstream need
requires it.

## 9.2 Milestone labels below are provisional

Candidate labels M35–M47 are **planning conveniences only**. They do not reserve
milestone numbers, create implementation authority, or require sequential delivery.
A fresh live-main audit may merge, split, reorder, rename, reject, or supersede any
candidate.

A future approved queue should normally contain no more than a few bounded packages,
even though this document intentionally preserves a larger idea space.

---

# 10. Immediate handoff candidates after M34

The completed M32–M34 handoff recommends three immediate directions. They remain
**candidates, not an approved work-package queue**.

## Candidate A / provisional M35 — Operator exposure for M32/M33

**Zone:** REPOSITORY_ONLY

### Problem

M32 delivery bundles and M33 deterministic traces are currently Python-level
surfaces. Applications wanting these artifacts should not need ad-hoc internal
Python wiring.

### Candidate scope

- expose an explicit participant-review/operator action for M32 bundle retrieval;
- expose an explicit action for M33 deterministic trace retrieval;
- preserve participant scoping and current content-disclosure rules;
- keep model prose/evaluator rationale separate from deterministic evidence;
- add negative tests for cross-participant/source/authority drift.

### Non-goals

- authentication;
- production frontend design;
- model/provider calls;
- new chess or learner authority.

### Candidate exit criterion

A consumer can retrieve qualified M32/M33 artifacts through an explicit supported
repository operator surface without hand-built Python integration.

---

## Candidate B / provisional M37 — Cross-surface consumer regression contract

**Zone:** HERMETIC_VALIDATION

### Problem

M30, M32, and M33 are individually qualified, but a future frontend/integration
would benefit from one repository-owned end-to-end consumer fixture contract.

### Candidate scope

Exercise representative M22 evidence regimes through:

```text
persisted reviewed coaching
-> M30 participant package
-> M32 delivery bundle
-> M33 deterministic feedback trace
```

Include negative/rejection cases for:

- score-perspective inversion;
- bound loss;
- mate numericization;
- partial/unavailable state collapse;
- source swapping;
- participant mismatch;
- authority promotion;
- deterministic-feedback component omission/reordering;
- rehashed semantic drift.

### Non-goals

- browser/device correctness;
- visual design;
- production accessibility approval;
- semantic proof of arbitrary model prose.

### Candidate exit criterion

A stable repository-owned fixture contract demonstrates that representative
qualified evidence semantics survive the full local consumer chain.

---

## Candidate C — External adoption and human-QA plan

**Zone:** EXTERNAL_AUTHORITY

### Problem

The repository has enough local contracts that production adoption decisions can no
longer be hidden behind more hermetic schemas.

### Planning scope

Define what evidence/approval would be required for:

- a real frontend consuming M30/M32/M33;
- browser/device visual QA;
- screen-reader and accessibility conformance;
- interaction/usability testing;
- correct consent/disclosure sequencing;
- localization policy;
- production model/evaluator provider selection;
- privacy/security review and secret handling;
- data transmission/retention policy;
- timeout/retry/backoff/rate-limit decisions;
- cost/latency budgets and observability;
- external-side-effect idempotency and recovery policy;
- hosted authentication/authorization and multi-user persistence.

### Critical rule

Do not simulate external approvals inside repository tests. This candidate may create
planning/checklist artifacts, but the actual approvals remain external.

### Candidate exit criterion

The repository can state exactly which production claims require which external
witness or human approval, without pretending hermetic tests satisfy them.

---

# 11. Candidate product-evolution horizons

The following horizons extend the immediate M34 handoff into the broader product
roadmap. They are intentionally directional rather than an approved implementation
sequence.

## Horizon 1 — Finish the current consumer boundary and expose learner state

### Provisional M35 — M32/M33 operator exposure

This is Candidate A above and should remain the smallest likely follow-up to M34.
Its purpose is to make already-qualified artifacts reachable through supported
operator paths.

**Candidate exit criterion:** M32 delivery bundles and M33 traces can be retrieved
through an explicit repository-supported operator surface while preserving all
participant/source/authority boundaries.

### Provisional M36 — Deterministic learner-state read model

**Purpose:** Give operators, future tutors, and future UI consumers an inspectable
answer to “what does the repository currently know about this participant?” without
creating any new learner authority.

**Candidate scope:**

- derive a participant-scoped read model from existing M7/M9/M10/M11 evidence;
- surface active/supported/challenged/retired learner hypotheses where available;
- show supporting and contradictory evidence counts and exact source references;
- expose selected interventions and their bounded practice/near/far/real-game
  outcome status;
- expose uncertainty and insufficient-evidence states explicitly;
- preserve chronology and revision lineage;
- optionally expose the read model through a deterministic CLI/operator command.

**Non-goals:**

- automatic M7 or M11 mutation;
- causal learner diagnosis;
- mastery inference;
- universal numeric weakness scores;
- selecting a training intervention automatically.

**Candidate exit criterion:** For one participant, a deterministic rebuild produces
the same inspectable learner-state summary from the same qualified evidence, and the
summary cannot promote observations, model prose, or evaluator judgments into
learner-state authority.

### Provisional M37 — Cross-surface consumer regression contract

This is Candidate B above. It should be treated as a supporting compatibility package,
not as the beginning of another long infrastructure-only sequence.

**Candidate exit criterion:** Representative M22 evidence semantics survive the full
persisted-review -> M30 -> M32 -> M33 chain under positive fixtures and specified
tamper/rejection mutations.

---

## Horizon 2 — Build learner intelligence

### Provisional M38 — Evidence-backed recurrence candidate miner

**Purpose:** Discover repeated position-level discrepancy patterns across a
participant's games without silently declaring a stable learner weakness.

A candidate output may include:

```text
RecurrenceCandidate
  candidate_id
  participant_id
  pattern_family
  candidate_statement
  supporting_discrepancies[]
  contradictory_controls[]
  context_distribution
  recurrence_count
  recency
  evidence_coverage
  unresolved_alternatives[]
  provenance
```

**Candidate scope:**

- consume qualified participant-local M6 discrepancy evidence and relevant controls;
- group only through explicit, versioned recurrence rules;
- preserve supporting, contradictory, and neutral evidence;
- expose context breadth and recency rather than only raw counts;
- produce a proposal that may later be reviewed against M7 authority;
- include negative fixtures where superficially similar mistakes must not collapse
  into one recurrence candidate.

**Non-goals:**

- automatic M7 mutation;
- claiming a causal cognitive mechanism;
- using engine move quality alone as a reasoning diagnosis;
- hiding contradictory controls;
- universal recurrence thresholds.

**Candidate exit criterion:** Repeated qualified discrepancy evidence can produce a
stable, provenance-complete recurrence proposal, while isolated, contradictory, or
participant-mismatched evidence fails to create a supported recurrence claim.

### Provisional M39 — Hypothesis evidence synthesizer

**Purpose:** Turn scattered support/challenge/control evidence into one deterministic
review package for a candidate or existing learner hypothesis.

**Candidate scope:**

- assemble evidence-for, evidence-against, controls, context diversity, recency, and
  revision history;
- distinguish direct participant evidence from analyst/model-derived interpretation;
- preserve alternative explanations instead of collapsing uncertainty too early;
- expose missing-evidence questions that would materially change confidence;
- generate a deterministic package consumable by human review or downstream model
  explanation.

**Non-goals:**

- automatically ratifying a learner hypothesis;
- inventing psychology beyond recorded evidence;
- replacing M7 lifecycle authority;
- converting evaluator acceptance into learner truth.

**Candidate exit criterion:** A reviewer can inspect one bounded package and recover
all evidence that supports, challenges, or limits a hypothesis without searching
multiple stores manually, and every substantive synthesis field is source-traceable.

### Provisional M40 — Teaching-priority / next-session planner

**Purpose:** Decide which *kind of tutoring action* is most useful next, given current
learner evidence, uncertainty, training status, and transfer status.

Candidate action classes may include:

```text
COLLECT_NEW_EVIDENCE
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
TEACH_CONCEPT
ASSIGN_PRACTICE
RUN_NEAR_TRANSFER_TEST
RUN_FAR_TRANSFER_TEST
WAIT_FOR_REAL_GAME_EVIDENCE
RETIRE_LOW_VALUE_HYPOTHESIS_CANDIDATE
```

**Candidate scope:**

- consume the learner-state read model and hypothesis evidence packages;
- use explicit versioned policy rules rather than opaque hidden scoring;
- distinguish “learn more about the learner” from “teach the learner”;
- prefer contradiction collection when evidence is narrow or one-sided;
- consider existing intervention/transfer state before assigning more practice;
- expose reasons and blocking uncertainty for every proposed action.

**Non-goals:**

- claiming globally optimal pedagogy;
- automatic mastery;
- autonomous mutation of M7/M9/M11 state;
- universal priority weights presented as scientifically validated.

**Candidate exit criterion:** Given bounded learner evidence, the planner produces a
stable next-action proposal with inspectable reasons and can correctly prefer
additional evidence or contradiction testing over premature training when policy
conditions require it.

### Provisional M41 — Intervention matching engine

**Purpose:** Map a sufficiently supported teaching need to explicit candidate M9
interventions while explaining why one intervention fits better than plausible
alternatives.

**Candidate scope:**

- define explicit intervention applicability and contraindication metadata;
- compare several plausible intervention candidates against current learner
  evidence;
- explain why a search-process intervention, calculation intervention, conceptual
  lesson, or other bounded training form is or is not applicable;
- preserve human/policy selection authority separately from matching evidence;
- record exact evidence used for the match.

**Non-goals:**

- claiming the selected intervention will cause improvement;
- replacing M9 selection authority without an explicit future contract;
- generic content generation detached from learner evidence;
- ranking interventions solely by engine loss.

**Candidate exit criterion:** For a supported teaching need, the repository can
produce a provenance-complete ranked or filtered set of intervention candidates and
can reject interventions whose prerequisites or evidence conditions are not met.

---

## Horizon 3 — Close the learning loop and expose product value

### Provisional M42 — Transfer / retest scheduler

**Purpose:** Operationalize M10/M11 by deliberately proposing fresh evidence that can
distinguish exercise success from generalized improvement.

**Candidate scope:**

- identify when an intervention is ready for near-transfer, far-transfer, or later
  real-game observation;
- select or request positions that test the same process without simply repeating
  the trained item;
- preserve test freshness and exposure boundaries;
- connect each retest to the exact learner hypothesis/intervention it is intended to
  challenge;
- keep “scheduled test” separate from “successful transfer.”

**Non-goals:**

- automatic mastery claims;
- fabricated real-game evidence;
- assuming exercise completion equals learning;
- universal retest timing presented as empirically optimal.

**Candidate exit criterion:** The system can produce a bounded retest plan tied to an
existing learner hypothesis/intervention and later classify supplied outcome evidence
without conflating practice success, near transfer, far transfer, and real-game
transfer.

### Provisional M43 — Contradiction hunter

**Purpose:** Proactively look for cases where a suspected weakness *should* have
appeared but the participant handled the relevant decision correctly.

**Candidate scope:**

- search participant-local historical evidence for candidate controls;
- rank cases by their ability to challenge a current recurrence/hypothesis;
- distinguish global patterns from context-specific patterns;
- support hypothesis weakening, narrowing, or retirement workflows without
  automatically mutating them;
- preserve successful decisions as first-class learning evidence.

**Non-goals:**

- treating absence of failure as proof of mastery;
- cross-participant inference;
- causal explanations unsupported by participant evidence;
- confirmation-biased mining of only supporting examples.

**Candidate exit criterion:** For a candidate hypothesis, the system can surface
high-value participant-local contradiction/control evidence and demonstrate cases
where that evidence narrows or weakens the candidate rather than merely accumulating
confirmations.

### Provisional M44 — Learner progress surface

**Purpose:** Turn the existing evidence/provenance investment into a useful,
participant-facing or operator-facing longitudinal explanation of learning state.

A candidate experience could show:

```text
CURRENT LEARNING PRIORITY
why the mentor believes it
supporting positions
contradictory positions
what was trained
practice / near / far / real-game evidence
what remains uncertain
what would change the mentor's mind
next proposed learning action
```

**Candidate scope:**

- render the M36 learner-state read model deterministically;
- expose supporting and contradictory source navigation;
- distinguish evidence, hypothesis, intervention, and transfer authority visually
  and semantically;
- support a “Why do you believe this about me?” view;
- support a “What evidence would weaken this?” view;
- remain local/reference quality unless external browser/a11y/usability gates are
  explicitly undertaken.

**Non-goals:**

- claiming production UX quality;
- authentication/privacy approval;
- hiding uncertainty for a cleaner narrative;
- presenting model prose as the source of learner-state truth.

**Candidate exit criterion:** A participant-scoped local consumer can inspect one
longitudinal learning view, navigate to its supporting/contradictory evidence, and
clearly distinguish what is observed, inferred, trained, and demonstrated through
transfer.

### Provisional M45 — Batch games -> mentor queue

**Purpose:** Make the system useful at the scale players actually experience it:
“Here are many recent games; what should I review or practice?”

**Candidate scope:**

- accept a bounded batch of canonical games;
- reuse qualified analysis/diagnostic surfaces rather than inventing a parallel
  engine path;
- deduplicate or diversify candidate positions;
- rank positions by explicit dimensions such as objective importance, recurrence
  relevance, hypothesis uncertainty, contradiction value, novelty, and transfer
  value;
- output a bounded mentor/review queue with provenance and reasons;
- avoid freezing universal numeric weights unless evidence warrants them.

**Non-goals:**

- simply sorting by centipawn loss;
- unlimited autonomous background analysis;
- cross-player weakness scoring;
- claiming the ranking function is pedagogically optimal.

**Candidate exit criterion:** A bounded multi-game fixture can be transformed into a
stable, participant-scoped mentor queue whose selections have inspectable reasons and
whose diversity/recurrence/contradiction policies can be tested hermetically.

### Provisional M46 — Adaptive Socratic tutor

**Purpose:** Use the existing evidence and learner state to choose the next question,
hint, explanation, or reveal step rather than delivering a fixed one-shot response.

**Candidate scope:**

- select tutor moves from a bounded pedagogical action vocabulary;
- preserve pre-reveal contamination boundaries and participant-capture consent;
- condition questions on known learner evidence without leaking engine conclusions
  prematurely;
- keep deterministic evidence grounding separate from model-authored language;
- preserve a replayable action/evidence trace for the session.

**Non-goals:**

- unconstrained chatbot authority;
- automatically rewriting learner state from conversational prose;
- hiding model uncertainty;
- claiming human-equivalent coaching quality.

**Candidate exit criterion:** A bounded tutor session can adapt its next action to
captured participant evidence while maintaining replayable sequencing, provenance,
and the existing distinction between deterministic grounding and generated language.

### Provisional M47 — Multi-session study-plan generator

**Purpose:** Convert current learner state into a bounded, revisable sequence of
learning actions rather than isolated recommendations.

**Candidate scope:**

- group compatible teaching priorities into a short planning horizon;
- connect each planned activity to explicit learner evidence and intervention
  applicability;
- include retest/transfer checkpoints rather than only more practice;
- revise the plan when contradiction or new transfer evidence arrives;
- preserve “proposed plan” separately from completed/validated learning outcomes.

**Non-goals:**

- long-term autonomous curriculum authority;
- universal study-volume prescriptions;
- pretending the plan is empirically optimal before user evidence exists;
- hiding superseded plan history.

**Candidate exit criterion:** The repository can generate and deterministically revise
a bounded multi-session plan where every action has a traceable learner-state reason,
and new contradiction/transfer evidence can alter future actions without rewriting
history.

---

# 12. Longer-term product questions

After the immediate M34 follow-up candidates, the more consequential product
questions are not primarily schema questions.

### 12.1 Production learning experience

What is the smallest real user flow that demonstrates the product thesis?

A candidate experience remains:

```text
import games
-> select instructive position
-> capture reasoning before reveal
-> compare reasoning with objective evidence
-> explain participant-specific discrepancy
-> connect to recurring evidence when justified
-> choose targeted practice
-> later measure transfer
```

The candidate horizons above should increasingly make this loop real rather than
merely representable.

### 12.2 Target segment

The current product-definition hypothesis favors regular online players around
1400–1800 who already use engine analysis. That remains a discovery assumption, not
a ratified product boundary.

### 12.3 Intervention value

The repository has bounded intervention and outcome contracts, but not empirical
proof that its intervention choices improve players. Product work should eventually
measure value rather than continue inferring it from software qualification.

### 12.4 Hosted product architecture

Only after product/user needs justify it should the repository freeze choices for:

- frontend framework;
- hosted API shape;
- authentication/authorization;
- database/retention architecture;
- provider vendor(s);
- observability/deployment stack.

Do not choose these merely because the evidence layer is mature.

### 12.5 Productization ideas to defer until the tutor loop earns them

Do not prioritize these ahead of a compelling local learner-intelligence / teaching
loop unless a concrete requirement changes the order:

- cloud deployment for its own sake;
- multi-tenancy before a real multi-user need;
- payments/subscriptions;
- social/community features;
- mobile applications;
- a broad opening database;
- a generic puzzle platform;
- rating prediction;
- gamification systems;
- complex provider abstraction unrelated to a current provider requirement.

The repository should become a better **mentor** before it becomes a larger
**platform**.

---

# 13. Decisions still deliberately deferred

Do **not** freeze these prematurely:

- final production database technology;
- production LLM/evaluator vendor;
- production secrets/transport architecture;
- automatic retry/backoff/rate-limit policy;
- final learner taxonomy;
- universal numeric learner scores;
- universal mastery thresholds;
- final intervention library;
- production web framework;
- cloud deployment architecture;
- multiplayer/coaching/social features;
- cross-player analytics;
- rating prediction;
- gamification strategy.

Some of these may become appropriate in a future milestone, but they must be earned
by a concrete product/operational requirement.

---

# 14. Phase-gate discipline for future packages

Before implementing any new package, require:

1. **Live-main reconciliation** — What is actually true in the repository now?
2. **Problem statement** — What failure or product need does this solve?
3. **Zone classification** — `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or
   `EXTERNAL_AUTHORITY`.
4. **Evidence basis** — Which product/technical need justifies the work?
5. **Authority contract** — Inputs, outputs, provenance, claim ceiling, and what the
   package must not authorize.
6. **Minimal implementation** — Smallest change that proves the contract.
7. **Positive qualification** — Native tests/fixtures for supported behavior.
8. **Negative/rejection qualification** — Tamper, mismatch, incomplete, or
   forbidden-authority cases.
9. **Documentation** — Current status and runbook/contract updates where relevant.
10. **Exact-head qualification** — Do not merge a candidate that differs from the
    candidate that passed the gate.
11. **Exit criterion** — What must be true before another package is authorized?

For post-M34 planning, add one more question before approving infrastructure work:

> Which learner-facing, tutoring, consumer, or external-adoption need pulls this
> infrastructure into existence now?

If that question has no concrete answer, prefer not to build the infrastructure yet.

Avoid using “implemented” to mean “described in a planning document.”

---

# 15. Error-prevention checklist

Do not confuse:

```text
engine evaluation
with
player reasoning
```

```text
player self-report
with
objective chess truth
```

```text
one position-level discrepancy
with
a recurring learner weakness
```

```text
recurrence candidate
with
ratified learner hypothesis
```

```text
recurrence
with
causal cognitive explanation
```

```text
supported learner hypothesis
with
automatic training eligibility
```

```text
intervention match
with
intervention effectiveness
```

```text
selected intervention
with
effective intervention
```

```text
exercise completion
with
successful performance or transfer
```

```text
near transfer
with
far or real-game transfer
```

```text
M16 deterministic grounding
with
M19 model prose
```

```text
M20 evaluator acceptance
with
objective truth
```

```text
M27 mechanical verification
with
semantic correctness
```

```text
M30 participant scoping
with
authentication
```

```text
M32 consumer fidelity
with
production UI quality
```

```text
M33 traceability
with
pedagogical truth
```

```text
M34 resume eligibility
with
retry authorization or execution
```

```text
learner-state read model
with
learner-state mutation authority
```

```text
next-session proposal
with
proven optimal pedagogy
```

```text
planning recommendation
with
approved work package
```

---

# 16. Repository documentation discipline

Each active document has one primary responsibility:

```text
README.md
    product overview, installation, operator entry points, navigation

CONTEXT.md
    contributor reasoning model and invariants

docs/product/repository-build-status.md
    canonical moving implementation + qualification authority

STATUS.md
    latest completed milestone handoff

docs/architecture/architecture.md
    current high-level implemented architecture / authority map

docs/product/chess-mentor-engine-repository-build-plan.md
    planning history + future candidate roadmap

docs/decisions/
    ratified historical decisions

docs/runbooks/
    feature/milestone operating and qualification history
```

Historical ADRs and milestone runbooks should remain historical. Do not rewrite them
just to make old documents speak as if M34 already existed.

Do **not** create a second roadmap/ideas document merely to hold future feature ideas.
This file is the canonical home for candidate repository-building directions. If the
idea becomes an approved package, its implementation/status truth moves to the normal
status, ADR, runbook, and qualification surfaces as appropriate.

When active documents disagree about present implementation state, resolve the drift
against `repository-build-status.md`.

---

# 17. Current recommendation

Do **not** restart the old M1-first roadmap. M1–M34 are already qualified.

The next milestone should begin with a live-main audit and should probably test a
small sequence that starts shifting the repository toward learner intelligence rather
than launching another broad infrastructure program.

The current leading candidate sequence is:

```text
fresh live-main audit
        ↓
provisional M35 — expose M32/M33 through supported operator paths
        ↓
provisional M36 — deterministic learner-state read model
        ↓
select ONE of:
    M37 cross-surface regression, if consumer stability is the active blocker
    M38 recurrence candidate mining, if learner intelligence is ready to advance
```

A subsequent milestone could then consider:

```text
M38 recurrence candidate miner
-> M39 hypothesis evidence synthesizer
-> M40 teaching-priority / next-session planner
-> M41 intervention matching
```

and later:

```text
M42 transfer / retest scheduler
-> M43 contradiction hunter
-> M44 learner progress surface
-> M45 batch games -> mentor queue
-> M46 adaptive Socratic tutor
-> M47 bounded study-plan generation
```

This is **not** an approved queue. The milestone labels are provisional, and a fresh
reconciliation may change the order or collapse multiple candidates into one bounded
package.

The strategic bias, however, should remain clear:

> After M34, new infrastructure should increasingly be justified by a concrete
> learner-facing, tutoring, consumer, or external-adoption need. The repository's
> next major gains should come from turning its rigorous evidence substrate into
> inspectable learner intelligence and a closed learning loop.

---

## Durable principles

> It is not enough to know which move was wrong; the repository must preserve the
> position and evidence that made it wrong.

> It is not engine evidence and is not player self-report alone; useful diagnosis
> depends on preserving both without confusing their authority.

> A weakness label is not the starting point; it is the possible downstream result
> of repeated, contradiction-tested evidence.

> The LLM should explain and reason over evidence, not manufacture the evidence
> substrate.

> Mechanical fidelity is necessary, but product value and pedagogical efficacy still
> require evidence outside the repository's hermetic qualification boundary.

> The infrastructure should now increasingly be pulled by the tutor we are trying to
> build, rather than the tutor being postponed by infrastructure we might someday
> need.
