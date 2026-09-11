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

This plan now has three jobs:

1. preserve the durable product and evidence principles that motivated the build;
2. map the original roadmap into the capabilities already delivered through M34;
3. keep future directions explicitly **candidate** until a fresh live-`main` audit
   promotes them into an approved bounded package queue.

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

# 9. Candidate future roadmap after M34

The M32–M34 handoff recommends three immediate directions. They are preserved here
as **candidates, not an approved work-package queue**.

## Candidate A — Operator exposure for M32/M33

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

## Candidate B — Cross-surface consumer regression contract

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

# 10. Longer-term product questions

After the immediate M34 follow-up candidates, the more consequential product
questions are not primarily schema questions.

### 10.1 Production learning experience

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

### 10.2 Target segment

The current product-definition hypothesis favors regular online players around
1400–1800 who already use engine analysis. That remains a discovery assumption, not
a ratified product boundary.

### 10.3 Intervention value

The repository has bounded intervention and outcome contracts, but not empirical
proof that its intervention choices improve players. Product work should eventually
measure value rather than continue inferring it from software qualification.

### 10.4 Hosted product architecture

Only after product/user needs justify it should the repository freeze choices for:

- frontend framework;
- hosted API shape;
- authentication/authorization;
- database/retention architecture;
- provider vendor(s);
- observability/deployment stack.

Do not choose these merely because the evidence layer is mature.

---

# 11. Decisions still deliberately deferred

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

# 12. Phase-gate discipline for future packages

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

Avoid using “implemented” to mean “described in a planning document.”

---

# 13. Error-prevention checklist

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
planning recommendation
with
approved work package
```

---

# 14. Repository documentation discipline

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

When active documents disagree about present implementation state, resolve the drift
against `repository-build-status.md`.

---

# 15. Current recommendation

Do **not** restart the old M1-first roadmap. M1–M34 are already qualified.

The correct next action for a future milestone is:

```text
live main audit
-> reconcile current status + handoff
-> identify the true bottleneck
-> classify candidate work by authority zone
-> approve a bounded package queue
-> implement one package at a time
-> qualify exact candidate heads
-> update moving status + final handoff
```

The M32–M34 handoff currently points first toward operator exposure for M32/M33,
then a cross-surface consumer regression contract, while external adoption/human QA
remains a separate authority track.

Those are recommendations, not automatic instructions.

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