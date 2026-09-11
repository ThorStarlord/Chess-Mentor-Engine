# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:**
> [`repository-build-status.md`](repository-build-status.md)  
> **Latest repository handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture map:** [`../architecture/architecture.md`](../architecture/architecture.md)

**Status:** Planning history plus future candidate roadmap  
**Current qualified boundary:** numbered milestones M1–M34 plus Chess Knowledge
Ontology program K0–K7  
**Authority:** This document is a planning artifact. It does **not** create an
approved work-package queue, supersede ratified ADRs, or grant production/external
authority.

---

## 1. Purpose of this document

The repository is no longer in its original pre-implementation state. M1–M34 are
qualified, and the post-M34 Chess Knowledge Ontology program K0–K7 is also qualified.

This plan now has five jobs:

1. preserve the product/evidence principles that motivated the build;
2. record the major capability eras already delivered;
3. record K0–K7 as a completed semantic foundation without renumbering it as M35+;
4. keep future directions explicitly **candidate** until a fresh live-`main` audit
   promotes them into a bounded implementation queue;
5. steer the next era toward learner intelligence, tutoring policy, transfer, and a
   useful learning experience rather than another speculative infrastructure phase.

For present-tense implementation claims, always use
[`repository-build-status.md`](repository-build-status.md).

---

## 2. Product direction to preserve

Chess Mentor Engine should not become merely another engine-analysis UI.

The product hypothesis remains a **persistent chess tutor that learns how a
particular player makes decisions, grounds its conclusions in objective chess
evidence, and uses that evidence to choose what the player should practice next**.

The durable evidence chain is:

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

The implemented repository surrounds that chain with explicit semantic,
operational, model, review, and provenance boundaries:

```text
objective chess evidence
-> optional typed chess-knowledge semantics
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

The important questions remain separate:

1. What is objectively happening on the board?
2. Which chess concepts describe the evidence, and under what authority?
3. What did the player actually notice, consider, and expect?
4. What recurring explanation is currently supported strongly enough to affect
   teaching?
5. What did deterministic grounding establish versus what a model merely rendered?
6. Did a selected intervention produce evidence of practice success or transfer?

---

## 3. Durable evidence and authority principles

### 3.1 Chess truth is not player psychology

Engine analysis can establish bounded objective chess evidence. It cannot establish
what the player saw, why the player chose a move, or whether a causal cognitive
mechanism exists.

### 3.2 Concept definition is not concept assertion is not learner inference

The K0–K7 program adds a shared chess vocabulary, but its central invariant is:

```text
concept definition != concept assertion != learner inference
```

A registered concept does not prove that the concept occurs in a position. A concept
assertion does not prove that the participant perceived it. Concept presence does not
by itself establish a recurring learner weakness.

### 3.3 Registry coverage is not detector coverage

A concept may be useful for humans, external taxonomies, models, pedagogy metadata,
or future policies while remaining intentionally undetected. K5 automation is
limited to mechanically qualified concepts.

### 3.4 External mappings preserve source authority

A Lichess puzzle tag mapped to a CME concept remains an external taxonomy tag. Broad
source labels such as `pin` may map to multiple internal concepts rather than being
forced into false precision.

### 3.5 Strategic vocabulary is not engine-score decomposition

Principles and qualitative evaluation factors may help explanation and policy design.
They do not claim that a Stockfish evaluation is the arithmetic sum of those factors.
Candidate plans are not automatically best moves or M9 interventions.

### 3.6 Player self-report is evidence, not objective truth

Participant responses are direct evidence of what the participant reports thinking.
They may be incomplete, reconstructed, mistaken, or affected by measurement
sequencing.

### 3.7 Local discrepancies are not stable weaknesses

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

### 3.8 M7C remains recurrence authority

The ontology program discovered that the repository already has a sophisticated M7C
recurrence-assessment subsystem. Future learner-intelligence work must reuse or
explicitly extend M7C rather than create a competing recurrence engine.

K7 therefore attaches ontology evidence to already-classified M7C recurrence units
while preserving `supports`, `contradicts`, `successful_counterexample`,
`context_exception`, `unclear`, and `mixed` relations verbatim.

### 3.9 Contradictory evidence is first-class

The system should preserve correct/control cases and evidence against a learner
hypothesis, not only examples that confirm it. The same chess concept may occur in
supporting and contradictory units.

### 3.10 Provenance is product correctness

Important claims should be recoverable through exact source game/position identity,
engine provenance, ontology identity, assertion identity/authority, participant
evidence, learner hypothesis revisions, tutor state, model/evaluator request
identity, persisted review artifacts, and qualified source fingerprints.

### 3.11 Deterministic grounding is different from model language

M16 remains the deterministic factual mentor-feedback ceiling. K6 may add an ontology
sidecar beside an exact M19 request, but it does not modify M19 request identity and
does not make arbitrary model prose true.

### 3.12 Evaluator acceptance is bounded judgment

M20 acceptance is not objective chess truth and is not proof of model safety,
pedagogical quality, or tutoring efficacy.

### 3.13 Recovery eligibility is not retry authority

M34 may classify a supplied synthetic execution history as `resume_eligible`. That
does not authorize or execute a real retry and does not establish external-side-
effect idempotency.

### 3.14 Infrastructure should increasingly be pulled by product needs

The repository has already invested heavily in evidence boundaries, persistence,
review, fidelity, provenance, recovery, and now a typed chess semantic substrate.
Future infrastructure should normally exist because a concrete learner/tutor/product
capability needs it.

Preferred direction:

```text
product need
-> explicit evidence/authority requirement
-> minimum supporting infrastructure
-> learner/tutor capability
-> qualification
```

Avoid:

```text
speculative infrastructure
-> more infrastructure
-> eventual product use
```

---

## 4. Completed capability eras

| Era | Qualified outcome |
| --- | --- |
| M1–M4 | Canonical chess evidence, deterministic features, engine evidence, played-decision comparison, diagnostic selection. |
| M5–M7 | Frozen participant evidence, position-local reasoning discrepancy, participant-specific hypothesis/recurrence/contradiction authority. |
| M8–M11 | Evidence-aware tutor state, intervention selection, bounded outcome/transfer evidence, longitudinal learner state. |
| M12–M18 | Local/operator surfaces, persistent tutor workflow, engine-backed analysis, deterministic presentation/feedback, diagnostic queue. |
| M19–M22 | Provenance-bound model rendering, bounded model evaluation, candidate authorization, cross-layer fidelity. |
| M23–M27 | Persistent reviewed-coaching path, execution conformance, coach-review model, atomic persistence, mechanical ledger. |
| M28–M34 | Local review/navigation, privacy/retry preflight, machine-consumer fidelity, deterministic traceability, hermetic recovery reconciliation. |
| K0–K3 | Chess Knowledge Ontology authority, strict registry, tactical/Lichess crosswalk, strategic/evaluation/plan/pedagogy vocabulary. |
| K4–K5 | Provenance-bound semantic assertions and a conservative deterministic detector subset. |
| K6–K7 | Authority-preserving model sidecar and M7C-preserving learner-knowledge projection. |

Exact implementation/CI provenance lives in
[`repository-build-status.md`](repository-build-status.md).

---

## 5. Completed post-M34 Chess Knowledge Ontology program

K0–K7 was implemented under a separate package namespace. It does **not** consume
provisional M35–M47 labels below.

```text
K0–K2  PR #75  ontology authority + registry + tactical/Lichess foundation
K3     PR #76  strategic principles + evaluation factors + position features + plans
K4     PR #77  provenance-bound chess-knowledge assertions
K5     PR #78  conservative deterministic concept detectors
K6     PR #79  authority-preserving model-coaching sidecar
K7     PR #80  M7C-preserving learner-knowledge projection
```

This program materially changes the future roadmap because the repository now has a
typed semantic layer that can be consumed by learner/tutor features **without**
using free-form strings as the only chess vocabulary.

What it does not change:

- M7C remains recurrence authority;
- M9 remains intervention applicability/selection authority;
- M16 remains deterministic mentor-grounding authority;
- M19 remains model-language request/provenance authority;
- semantic vocabulary does not become causal learner psychology;
- registered concepts do not automatically become detectors.

The ontology should now be treated as enabling substrate, not as a reason to start
another ontology-only expansion campaign.

---

## 6. Current product surfaces

Installed operator commands remain:

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

K0–K7 add Python API/reference surfaces, not a new production CLI command.

M28 provides deterministic local semantic HTML reference rendering, but production
frontend/browser/accessibility/usability authority remains external.

The model path remains:

```text
M15 deterministic evaluation presentation
+ M6/M7 learner evidence
-> M16 deterministic grounded mentor feedback
-> M19 content-addressed model request
-> optional K6 ontology sidecar bound beside that unchanged request
-> optional M24 provider execution
-> M19 model-authored language
-> optional M20 bounded evaluation
```

---

## 7. Strategic transition after K0–K7

The repository is now strong at:

```text
evidence
-> provenance
-> semantic typing
-> validation
-> persistence
-> review
-> delivery
-> traceability
-> recovery
```

The product thesis still requires stronger capability at:

```text
many games
-> inspectable learner state
-> evidence synthesis + contradiction search
-> teaching priority
-> personalized intervention
-> deliberate retest
-> improvement/contradiction evidence
-> revised learner model
```

Future planning should prioritize the latter chain.

### Planning layers

```text
LAYER A — INFRASTRUCTURE / DELIVERY
existing evidence, provenance, ontology, persistence, validation, review, recovery

              ↓ supports

LAYER B — LEARNER INTELLIGENCE
learner-state read models
evidence synthesis
contradiction search
priority selection

              ↓ informs

LAYER C — PEDAGOGICAL LOOP
intervention matching / selection
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

Layer A is already mature. New Layer-A work should normally be pulled by a concrete
B/C/D need.

---

## 8. Immediate candidates

These remain **candidates, not an approved work-package queue**.

### Candidate A / provisional M35 — operator exposure for qualified artifacts

**Zone:** REPOSITORY_ONLY

Potential scope:

- expose explicit supported retrieval for M32 delivery bundles and M33 traces;
- consider ontology/learner read surfaces only when a concrete consumer needs them;
- preserve participant scope, content-disclosure rules, and authority labels;
- do not turn participant scoping into an authentication claim.

This is useful operability work but should not automatically outrank learner-
intelligence work if no current consumer is blocked.

### Candidate B / provisional M37 — cross-surface consumer regression

**Zone:** HERMETIC_VALIDATION

Exercise representative M22 evidence regimes through:

```text
persisted reviewed coaching
-> M30 participant package
-> M32 delivery bundle
-> M33 deterministic feedback trace
```

Include perspective, bound, mate, partial/unavailable, source, participant, authority,
component-ordering, and rehashed-drift rejection cases.

This remains supporting compatibility work rather than the start of another broad
infrastructure campaign.

### Candidate C — external adoption and human QA plan

**Zone:** EXTERNAL_AUTHORITY

Define evidence/approval requirements for a real frontend, browser/device QA,
accessibility, interaction/usability testing, consent sequencing, localization,
production model/evaluator providers, privacy/security, retention, retries,
rate-limits, costs/SLOs, idempotency/recovery, hosted auth, and multi-user
persistence.

Do not simulate those approvals inside repository tests.

---

## 9. Candidate learner-intelligence horizon

### Provisional M36 — deterministic learner-state read model

**Purpose:** Give operators, future tutors, and future UI consumers an inspectable
answer to “what does the repository currently know about this participant?” without
creating new learner authority.

**Candidate scope:**

- derive a participant-scoped read model from existing M7/M9/M10/M11 evidence;
- optionally attach K7 concept summaries to hypotheses as descriptive chess context;
- show active/supported/challenged/retired hypotheses where available;
- show exact supporting and contradictory source references;
- expose selected interventions and bounded practice/near/far/real-game outcomes;
- expose uncertainty, insufficient evidence, chronology, and revision lineage;
- optionally add a deterministic supported operator surface.

**Non-goals:** automatic M7/M11 mutation, causal diagnosis, mastery inference,
universal numeric weakness scores, automatic intervention selection.

**Exit criterion:** identical qualified inputs rebuild the same participant summary,
and no ontology/model/evaluator data is promoted beyond its source authority.

### Provisional M38 — M7C-aware recurrence/context candidate mining

The earlier roadmap described a recurrence candidate miner. K0–K7 implementation
revealed that M7C already owns a mature recurrence-assessment contract. Therefore
this candidate must **reuse or explicitly extend M7C**, not create a second recurrence
engine.

A safer purpose is to discover typed **candidate grouping/context signals** that can
feed existing M7/M7C review:

```text
RecurrenceContextCandidate
  candidate_id
  participant_id
  candidate_concept_ids[]
  source_m6_discrepancy_refs[]
  contradictory_control_refs[]
  context_distribution
  recurrence_unit_refs[]
  evidence_coverage
  unresolved_alternatives[]
  provenance
```

Potential scope:

- consume qualified participant-local M6/M7C evidence;
- use K0–K7 concept IDs as descriptive grouping/context dimensions where justified;
- preserve support, contradiction, counterexamples, and neutral/unclear evidence;
- propose groupings for M7C/human review rather than declaring recurrence itself;
- reject superficially similar positions whose M6/M7C semantics do not match.

**Non-goals:** parallel recurrence thresholds, automatic M7 mutation, causal
psychology, engine-loss-only diagnosis, hidden contradictory controls.

### Provisional M39 — hypothesis evidence synthesizer

**Purpose:** Turn distributed support/challenge/control evidence into one
deterministic review package for a candidate or current learner hypothesis.

Potential scope:

- assemble evidence-for, evidence-against, controls, context diversity, recency, and
  revision history;
- attach K7 concept summaries as descriptive context where available;
- distinguish direct participant evidence from deterministic/analyst/model-derived
  interpretation;
- preserve alternative explanations;
- expose missing-evidence questions that would materially change the assessment;
- produce a source-traceable package for human or downstream model explanation.

**Non-goals:** automatic ratification, replacing M7/M7C lifecycle authority,
inventing psychology, converting M20 acceptance into learner truth.

### Provisional M40 — teaching-priority / next-session planner

**Purpose:** Decide which *kind of tutoring action* is most useful next given current
learner evidence, uncertainty, training status, and transfer status.

Candidate action classes:

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

The planner may use M36/M39 plus ontology relationships/pedagogy metadata, but any
ranking/selection policy must be explicit and versioned. Ontology metadata does not
prove pedagogical optimality.

**Non-goals:** globally optimal pedagogy, automatic mastery, hidden numeric weights,
autonomous M7/M9/M11 mutation.

### Provisional M41 — intervention matching engine

**Purpose:** Map a sufficiently supported teaching need to explicit candidate M9
interventions while explaining why plausible alternatives do or do not fit.

Potential scope:

- use existing M9 applicability authority;
- let ontology concepts/principles/plans/pedagogy metadata describe the teaching need;
- define explicit applicability/contraindication metadata and prerequisites;
- compare candidate search-process, calculation, conceptual, or other bounded
  intervention forms;
- preserve policy/human selection authority separately from matching evidence.

**Non-goals:** claiming improvement causality, silently replacing M9 selection
authority, generic content detached from learner evidence.

---

## 10. Candidate closed-loop/product horizon

### Provisional M42 — transfer / retest scheduler

Propose fresh near/far/real-game evidence opportunities tied to an existing learner
hypothesis/intervention. Preserve exposure/freshness boundaries and keep “scheduled
test” separate from “successful transfer.”

### Provisional M43 — contradiction hunter

Search participant-local evidence for positions where a suspected weakness should
have appeared but the participant handled the relevant decision successfully. Use
M7C challenge/counterexample authority and K7 concept context where useful. Do not
treat absence of failure as mastery.

### Provisional M44 — learner progress surface

Render a participant-scoped longitudinal view containing:

```text
current learning priority
why the mentor believes it
supporting positions
contradictory positions
relevant chess concepts
what was trained
practice / near / far / real-game evidence
what remains uncertain
what would change the mentor's mind
next proposed learning action
```

Keep evidence, ontology semantics, learner hypothesis, intervention, transfer, and
model-language authority visually and semantically distinct.

### Provisional M45 — batch games -> mentor queue

Transform a bounded batch of canonical games into an inspectable mentor/review queue
that can consider objective importance, M7C recurrence relevance, K7 concept/context
coverage, hypothesis uncertainty, contradiction value, novelty, and transfer value.
Do not reduce the product to centipawn-loss sorting.

### Provisional M46 — adaptive Socratic tutor

Choose the next bounded question/hint/explanation/reveal action from current captured
participant evidence and learner context while preserving pre-reveal contamination
boundaries and the distinction between M16 grounding, K6 semantic context, and M19
model language.

### Provisional M47 — bounded multi-session study plan

Generate a short revisable sequence of learner-evidence-linked activities with
explicit retest/transfer checkpoints. Keep proposed plans separate from completed or
validated learning outcomes and retain superseded history.

---

## 11. Signature product opportunity: explainable learner beliefs

The evidence, provenance, M7C contradiction handling, and K7 semantic layer make two
participant-facing questions unusually feasible:

```text
WHY DO YOU BELIEVE THIS ABOUT ME?
Hypothesis
↓
M7C support / contradiction / counterexample evidence
↓
source games and positions
↓
K7 chess concepts/context
↓
captured participant reasoning
↓
objective chess evidence
↓
revision history
```

and:

```text
WHAT WOULD CHANGE YOUR MIND?
```

A future M39/M44 surface could state which fresh evidence would weaken, narrow, or
challenge a learner hypothesis. That is strategically aligned with the repository's
existing contradiction-first authority model and may be more differentiating than a
generic “AI coach” explanation surface.

---

## 12. Longer-term product questions

### Production learning experience

The smallest real flow that demonstrates the product thesis is still approximately:

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

K0–K7 now gives that loop a typed chess semantic substrate. The next work should make
the loop more useful, not merely add more vocabulary.

### Target segment

The current product-definition hypothesis favors regular online players around
1400–1800 who already use engine analysis. That remains a discovery assumption, not
a permanent boundary.

### Intervention value

The repository has bounded intervention/outcome contracts and semantic teaching
metadata, but not empirical proof that intervention choices improve players.

### Hosted product architecture

Only after product/user needs justify it should the repository freeze frontend,
hosted API, authentication, database/retention, provider, observability, or deployment
choices.

### Defer until the tutor loop earns them

Do not prioritize cloud deployment, multi-tenancy, payments, social/community,
mobile apps, broad opening databases, generic puzzle platforms, rating prediction,
gamification, or complex provider abstraction ahead of a compelling local learner-
intelligence and teaching loop unless a concrete requirement changes the order.

The repository should become a better **mentor** before it becomes a larger
**platform**.

---

## 13. Decisions still deliberately deferred

Do not freeze prematurely:

- production database technology;
- production LLM/evaluator vendor;
- production secrets/transport architecture;
- automatic retry/backoff/rate-limit policy;
- final learner taxonomy;
- universal numeric learner scores or mastery thresholds;
- final intervention library;
- production web framework/cloud architecture;
- multiplayer/coaching/social features;
- cross-player analytics;
- rating prediction or gamification strategy.

Likewise, do not declare the current ontology complete. Extend it when a concrete
consumer requires missing semantics.

---

## 14. Phase-gate discipline for future packages

Before implementing a new package, require:

1. **Live-main reconciliation** — what is actually true now?
2. **Problem statement** — what user/product/correctness need does this solve?
3. **Zone classification** — `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or
   `EXTERNAL_AUTHORITY`.
4. **Evidence basis** — what justifies the work now?
5. **Existing-authority audit** — does M7C, M9, M16, M19, K0–K7, or another existing
   subsystem already own part of this problem?
6. **Authority contract** — inputs, outputs, provenance, claim ceiling, forbidden
   authority changes.
7. **Minimal implementation** — smallest change that proves the contract.
8. **Positive qualification** — supported behavior.
9. **Negative/rejection qualification** — tamper, mismatch, near-miss, incomplete,
   or forbidden-authority cases.
10. **Documentation** — current status/runbook/contract updates as warranted.
11. **Exact-head qualification** — merge only the candidate that actually passed.
12. **Exit criterion** — what must be true before another package is authorized?

For infrastructure work, also ask:

> Which learner-facing, tutoring, consumer, or external-adoption need pulls this
> infrastructure into existence now?

If there is no concrete answer, prefer not to build it yet.

---

## 15. Error-prevention checklist

Do not confuse:

```text
engine evaluation
with
player reasoning
```

```text
concept definition
with
concept occurrence
```

```text
concept occurrence
with
participant perception or learner weakness
```

```text
registered concept
with
deterministically detected concept
```

```text
external taxonomy tag
with
CME detector authority
```

```text
strategic principle / evaluation factor
with
Stockfish score decomposition
```

```text
strategic plan
with
best move or M9 intervention
```

```text
one position-level discrepancy
with
a recurring learner weakness
```

```text
K7 ontology projection
with
M7C recurrence classification
```

```text
recurrence
with
causal cognitive explanation
```

```text
K6 model sidecar
with
M19 request identity or M16 factual authority
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
exercise completion
with
successful performance or transfer
```

```text
M20 evaluator acceptance
with
objective truth
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
planning recommendation
with
approved work package
```

---

## 16. Repository documentation discipline

```text
README.md
    product overview, installation, operator entry points, navigation

CONTEXT.md
    contributor reasoning model and invariants

docs/product/repository-build-status.md
    canonical moving implementation + qualification authority

STATUS.md
    latest completed repository handoff

docs/architecture/architecture.md
    current high-level implemented architecture / authority map

docs/product/chess-mentor-engine-repository-build-plan.md
    planning history + future candidate roadmap

docs/decisions/
    ratified historical decisions

docs/chess-knowledge/
    ontology semantic/reference documentation

docs/runbooks/
    feature/program operating and qualification history
```

Do not create a second roadmap merely to hold future feature ideas. This file is the
canonical home for candidate repository-building directions. When an idea becomes an
implemented/qualified package, current truth moves to the status/architecture/runbook
surfaces as appropriate.

---

## 17. Current recommendation

Do **not** restart the old M1-first roadmap and do not begin another broad ontology
expansion merely because K0–K7 exists.

The next milestone should begin with a live-main audit and select a small bounded
sequence that turns the rigorous evidence + ontology substrate into learner value.

Current leading sequence:

```text
fresh live-main audit
        ↓
provisional M36 — deterministic learner-state read model
        ↓
provisional M39 — hypothesis evidence synthesizer
        ↓
select ONE concrete next policy need:
    M40 teaching-priority / next-session planner
    M41 intervention matching
    M43 contradiction hunter
```

Candidate A/M35 operator exposure or Candidate B/M37 consumer regression should be
pulled forward if a real consumer/compatibility blocker makes them the active need.

This is **not** an approved queue. Labels remain provisional and a fresh
reconciliation may merge, split, reorder, or reject them.

The strategic bias is clear:

> After M34 + K0–K7, the repository has enough infrastructure and semantic substrate
> to prioritize inspectable learner intelligence and a closed learning loop. New
> infrastructure should increasingly be built only when that product work requires
> it.

---

## Durable principles

> It is not enough to know which move was wrong; preserve the position and evidence
> that made it wrong.

> A chess concept is a useful semantic coordinate, not a shortcut from board state to
> learner psychology.

> A weakness label is not the starting point; it is a possible downstream result of
> repeated, contradiction-tested participant-specific evidence.

> Reuse M7C recurrence authority rather than rebuilding recurrence inside the
> ontology.

> The LLM should explain and reason over evidence and typed semantics, not manufacture
> the evidence substrate or silently promote itself to deterministic authority.

> Mechanical fidelity is necessary, but product value and pedagogical efficacy still
> require evidence outside the repository's hermetic qualification boundary.

> The infrastructure should now increasingly be pulled by the tutor we are trying to
> build, rather than the tutor being postponed by infrastructure we might someday
> need.
