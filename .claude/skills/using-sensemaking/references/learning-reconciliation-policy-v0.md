# Learning / Reconciliation Policy v0 — Agent Contract

**Status:** canonical agent-facing semantic policy  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive control guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic policy; not a belief database, model-training loop, event-sourced world model, or automatic state mutator

## 1. Question

Learning / Reconciliation Policy answers:

> **Given returned evidence and the current explicit decision model, what should change in our claims, uncertainties, responsibility, continuation state, or strategic frame—if anything?**

Returned results are inputs to interpretation, not automatic state updates.

```text
result returned
!= evidence interpreted

evidence exists
!= conclusion automatic

validator PASS
!= semantic update automatic

learning
!= model-weight update
```

## 2. Activation rule

Keep this policy implicit for trivial local work where the result simply confirms an already-bounded action and no durable decision state needs updating.

Make it explicit when returned evidence could materially change:

- a consequential claim;
- a decision-relevant uncertainty;
- the selected responsibility;
- continue / stop / defer / escalation;
- verification or closure state;
- authority assumptions;
- a Strategic Decision to Support;
- a construction path or strategic boundary;
- a Level-4 product-thesis commitment.

The policy reconciles explicit repository-domain state. It does not require a universal cognitive model.

## 3. Inputs

Use the smallest current state needed to interpret the evidence:

```text
DECISION / WARRANT TARGET
PREVIOUS CLAIMS
PREVIOUS UNCERTAINTIES
SELECTED RESPONSIBILITY / ACTION
EXPECTED EVIDENCE / SUCCESS CONDITIONS
RETURNED RESULT
EVIDENCE PROVENANCE / CURRENTNESS
MECHANICAL VALIDATION STATUS
FINDING-SPECIFIC VERIFICATION, WHEN RELEVANT
AUTHORITY / OWNER / EXTERNAL CONSTRAINTS
CURRENT STRATEGIC STATE, WHEN RELEVANT
CURRENT PRODUCT-THESIS AUTHORITY, WHEN RELEVANT
```

Do not reconstruct hidden chain-of-thought. Reconcile explicit decision-relevant state.

## 4. Interpret result before updating state

Ask what the result directly establishes, what it does not establish, whether it is current for the target, whether it contradicts a prior assumption, whether it resolves the uncertainty that justified the work, and whether it changes responsibility, continuation, closure, authority, or strategy.

```text
execution success
!= responsibility complete

test PASS
!= original finding closed

artifact valid
!= analytical conclusion true
```

## 5. Reconciliation dispositions

These are documentation-level semantic dispositions, not runtime enums.

### `NO_MODEL_CHANGE`

The returned evidence is useful or valid but does not materially change the explicit decision model. This is a valid successful outcome.

### `CONFIRM`

The evidence materially strengthens or confirms an existing claim, interpretation, responsibility, or strategic assumption. Confirmation remains defeasible and bounded to the evidence scope.

### `REVISE_CLAIM`

The prior explicit claim is too strong, too weak, stale, or contradicted. Record the prior claim, new claim, decisive evidence, claim ceiling, and currentness/provenance.

### `RESOLVE_UNCERTAINTY`

The evidence answers a decision-relevant uncertainty sufficiently for the current decision.

```text
uncertainty resolved
!= every adjacent question answered
```

### `OPEN_NEW_UNCERTAINTY`

The evidence exposes a new question capable of changing the next decision. Record only decision-relevant uncertainty, not every curiosity.

### `CHANGE_RESPONSIBILITY`

The evidence shows that the currently selected responsibility is no longer the right bounded work. Record the old responsibility, new responsibility, and the evidence that changed the warrant.

```text
result surprising
!= responsibility change automatic
```

### `CONTINUE`

The current responsibility remains warranted and more bounded work is justified. Record what remains and the evidence/condition that will end continuation.

### `STOP`

Further work on the current responsibility/search/process is not warranted. Stopping may be local, deferred, or terminal depending on the owning control surface.

### `ESCALATE`

Evidence shows that the next decision belongs to an owner, external actor, or higher control scope. Carry the evidence and exact decision/authority gap upward.

### `REOPEN_STRATEGY`

Returned evidence materially changes the Level-3 strategic model or invalidates the current Strategic Decision, boundary, or construction path. Return to Strategic Repository Sensemaking / Level 3.

```text
local implementation surprise
!= strategic reopening automatically
```

### `THESIS_REVIEW_REQUIRED`

Evidence makes a Level-4 product-thesis commitment decision-changing. Do not silently revise the thesis; preserve the challenged commitment, dependent work, evidence, and owner-ratification requirement.

## 6. Reconciliation dimensions

Reconcile only dimensions that can change the next decision:

- **claims** — stronger, weaker, contradicted, or stale;
- **uncertainty** — resolved, newly opened, or no longer decision-relevant;
- **responsibility** — still the smallest warranted work or changed;
- **warrant** — changed for claim/action/continuation/closure targets;
- **authority** — need discovered versus authority actually granted;
- **strategy** — Strategic Decision/path/boundary/rationale changed;
- **thesis** — Level-4 commitment made decision-changing.

```text
authority need discovered
!= authority granted
```

## 7. Minimal reconciliation order

```text
returned result
-> establish provenance/currentness + mechanical facts
-> interpret target-specific evidence
-> revise claims/uncertainties
-> reassess responsibility + warrant
-> reassess continuation / verification / closure
-> reopen Level 3 only if strategically decision-changing
-> escalate Level 4 only if thesis-dependent
```

Do not escalate scope merely because higher levels exist.

## 8. Relationship to Warrant / Choice Policy

Warrant is current and defeasible. Reconciliation updates the explicit state that future warrant judgments consume.

```text
evidence return
-> Learning / Reconciliation
-> updated explicit claims / uncertainty / responsibility / strategy
-> Warrant / Choice reassessment
```

The policies may interleave. Neither is a deterministic rule engine.

## 9. Relationship to durable state

Reuse existing repository-domain surfaces:

- `strategic_reconciliation` when returned Level-3 evidence must be durably
  related to a prior `strategic_repository_analysis`;
- Campaign evidence / transitions;
- current Responsibility / Uncertainty / Authority projection;
- handoff / resume context;
- semantic-state companion;
- `STATUS.md`;
- ADRs;
- Strategic Repository Analysis artifacts;
- issue / PR qualification receipts;
- repository history.

```text
Learning / Reconciliation Policy
!= new BeliefState schema
!= generic event store
```

Persist only what another context/actor needs to reconstruct a consequential decision.

## 10. Relationship to Strategic Repository Sensemaking

Strategic Repository Sensemaking constructs a Level-3 model of current system, capabilities, limitations, coherent construction paths, tradeoffs, and decision-changing uncertainty.

Learning / Reconciliation updates that model only when returned evidence is strategically material.
When that update itself must survive contexts, the canonical first-class
artifact is produced by `strategic-repository-reconciliation`.

```text
bounded implementation confirms expected mechanics
-> NO_MODEL_CHANGE or CONFIRM

new capability invalidates a stated limitation
-> REVISE_CLAIM

path prerequisite is falsified
-> REOPEN_STRATEGY

evidence shows path choice depends on owner product preference
-> ESCALATE / THESIS_REVIEW_REQUIRED as appropriate
```

It must not automatically regenerate or rerank paths after every implementation result.

Reserved outcomes may use bounded companion packets:

```text
owner preference / reserved authority decides the issue
-> owner_decision_capsule

Level-4 commitment must be reviewed
-> thesis_review_packet

external evidence is decision-changing and provenance/currentness must persist
-> external_evidence_packet
```

Producing one of these artifacts does not make the reserved decision, ratify the
thesis transition, or transform external evidence into repository truth.

## 11. Closure discipline

Closure is a warrant target, not a default result of implementation.

```text
implemented
mechanically validated
claim reconciled
finding-specific verified
canonical/integrated state verified
owner/protected authority satisfied when required
```

Only require the layers relevant to the actual closure claim.

```text
work completed
!= closure warranted automatically
```

## 12. Failure and retry

Execution failure is evidence. Interpret whether the failure is mechanical, environmental, responsibility-level, strategic, or authority/external before choosing retry, repair, responsibility change, stop, or escalation.

```text
failure
!= retry automatically

failure
!= responsibility change automatically
```

Retry the same responsibility only when the evidence still warrants it.

## 13. Cross-context learning

Learning becomes durable when forgetting it would cause meaningful rediscovery, contradictory claims, repeated failed search, unsafe continuation, or loss of strategic rationale.

Preserve explicit lessons such as attempt/result, falsified assumption, revised claim, resolved/new uncertainty, responsibility change, stop/reopen condition, strategic consequence, and evidence provenance/currentness.

Do not persist private chain-of-thought.

## 13A. Cross-episode capability learning

Cross-context learning preserves what another context needs to continue one
consequential line of work. A different question appears when several normal-use
episodes expose a materially similar reusable lesson.

Use `docs/research/capability-learning-loop-v0.md` as the evidence-gated
explanatory model for that higher-order case.

```text
episode learning
-> update the current explicit decision/repository model

cross-episode capability learning
-> ask whether several explicit lessons warrant a reusable doctrine candidate
```

Do not generalize one surprising result into a Skill/policy rule automatically.
Prefer heterogeneous corroboration when the intended doctrine is meant to apply
across repository types, record counterevidence/context limits, and use the
smallest reusable guidance change that addresses the demonstrated pattern.

```text
one episode
!= reusable doctrine

recurring pattern
!= common cause proven

lesson candidate
!= Skill change authorized

qualified reusable change
!= universal semantic truth
```

Capability learning reuses existing evidence, normal-use records, repository
history, reviews, and qualification surfaces. It introduces no `LearningEngine`,
self-modification loop, generic memory schema, or automatic policy mutation.

Do not manufacture a second generic learning artifact merely because a lesson
was found. Preserve the lesson in the narrowest existing durable surface that
owns the consequential state: Campaign evidence/transition, handoff/resume,
strategic reconciliation, STATUS/ADR, qualification record, issue/PR history,
or another repository-owned artifact.

```text
lesson worth remembering
-> use appropriate existing durable surface

lesson observed
!= append to universal LEARNINGS.md

several explicit lessons become materially comparable
-> cross-episode synthesis may be warranted
```

Cross-episode synthesis is currently agent-owned reasoning. A dedicated
`capability-learning-analysis` Skill remains a candidate only if repeated
normal use establishes a stable reusable responsibility; its existence is not
implied by this policy.

## 14. Compact use

After a consequential result, ask:

```text
What did the result directly establish?
What claim did we previously make?
What uncertainty justified the work?
Did that uncertainty resolve?
Did a new decision-changing uncertainty appear?
Is the same responsibility still warranted?
What changes about continue / stop / verify / close?
Did authority actually change?
Does this affect Level 3?
Does this affect Level 4?
What explicit state must another context reconstruct?

Disposition(s):
NO_MODEL_CHANGE
CONFIRM
REVISE_CLAIM
RESOLVE_UNCERTAINTY
OPEN_NEW_UNCERTAINTY
CHANGE_RESPONSIBILITY
CONTINUE
STOP
ESCALATE
REOPEN_STRATEGY
THESIS_REVIEW_REQUIRED
```

## 15. Anti-patterns

Avoid:

- automatic belief updates from validator/test output;
- treating worker success as parent/global closure;
- opening every newly observed curiosity as durable uncertainty;
- changing responsibility merely because execution failed;
- changing authority because a task succeeded;
- reopening strategy for every local implementation surprise;
- silently rewriting Level-4 commitments;
- creating a generic belief database;
- creating a universal LearningEngine / ReconciliationEngine;
- persisting every reasoning step;
- confusing learning with model-weight training.

## Strategic reassessment: return path (moved verbatim from using-sensemaking section 4)


When a prior strategic analysis exists and later repository/evidence state may matter,
use Strategic Continuity and Learning / Reconciliation as a bounded return path:

```text
prior strategic analysis
+ later result / observation / reassessment trigger
-> use strategy compare/drift only for mechanical projection when useful
-> ask whether the new evidence is decision-changing
-> apply Learning / Reconciliation when consequential
-> persist strategic_reconciliation only when another context/actor needs it
-> reopen Strategic Repository Sensemaking only when warranted
```


## Where reconciled state goes

Persist only the explicit decision-relevant update another context must
reconstruct, using existing Campaign, STATUS, ADR, handoff or evidence
surfaces. At Level 3, `strategic-repository-reconciliation` provides a
first-class artifact when the relationship to a prior
`strategic_repository_analysis` itself must be durable.
