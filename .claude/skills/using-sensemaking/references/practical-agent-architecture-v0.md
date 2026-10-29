# Practical Agent Architecture v0 — Agent Reference

**Status:** agent-facing guidance for using Sensemaking; not a runtime specification  
**Authority:** interpretive guidance under the current product boundary; ADR 0029 and canonical authority contracts remain controlling  
**Parent design:** `../../../docs/superpowers/specs/2026-09-17-practical-agent-architecture-v0-design.md`  
**Reconciliation:** `../../../docs/research/practical-agent-architecture-reconciliation-v0.md`  
**Policy hierarchy:** `../../../docs/policy-hierarchy-v0.md`

Use this reference when a consequential decision benefits from making warrant, challenge/exploration, delegated work, or stopping logic explicit.

The architecture is a **reasoning and ownership guide**, not a mandatory workflow. For trivial local reversible work, keep most of it implicit.

## 0. Adaptive policy composition

Use `adaptive-policy-coordinator-v0.md` only when several semantic policy questions
could plausibly govern the next decision. The coordinator is progressive-disclosure
guidance, not a runtime controller.

```text
obvious bounded work
-> keep policy composition implicit

ambiguous / consequential / iterative / authority-sensitive
-> expose only policy questions that can change the decision
```

Do not run the full hierarchy by default.

## 1. Compact practical loop

```text
goal + authority + target
-> name contemplated warrant target
-> identify the few premises that must be true
-> resolve the nearest decision-changing warrant gap
-> apply Inquiry Policy: no inquiry, or smallest sufficient evidence
-> apply Metareasoning Policy: act / inquire / challenge / explore / verify / escalate / stop
-> when search is materially iterative, apply Exploration Policy
-> apply Warrant / Choice Policy to the current target
-> check authority + mechanical preconditions
-> orchestrate selected work
-> treat returned result as evidence
-> apply Learning / Reconciliation Policy when the evidence is consequential
-> update warrant
-> repeat only as warranted
```

This is not a runtime state machine.

The active agent still owns semantic judgment. Deterministic machinery validates only mechanically decidable facts. Orchestration coordinates already-selected work.

## 2. Start from the warrant target

For consequential work, ask first:

> **What exactly am I trying to justify now?**

Useful warrant targets include:

```text
claim
inquiry
responsibility
action
continue
stop
escalate
closure
protected transition
```

Examples:

```text
target: claim this defect is real

target: select repair as the warranted responsibility

target: continue investigating instead of acting

target: claim the original finding is closed

target: merge / publish / deploy
```

Then ask:

> **What must be true for this target to be warranted?**

Keep the dependency set bounded to premises that could materially redirect the next decision.

```text
warrant != confidence score
warrant != authorization
warrant for target A != warrant for target B
```

A test result that warrants a candidate-level claim may not warrant closure. A technically justified repair may not grant merge authority.

### 2.1 Warrant / Choice Policy

Use the canonical `warrant-choice-policy-v0.md` contract when target justification or
choice is consequential.

```text
target + dependencies + evidence + constraints + authority
-> target-specific warrant disposition
-> select one warranted target if commitment is required
   OR NO_SELECTION
```

Warrant is defeasible and current-state relative. Do not convert it into a scalar score,
permission token, universal lifecycle state, or automatic chooser.

```text
warrant for target A
!= warrant for target B

selected
!= authorized
```

## 3. Find the nearest decision-changing warrant gap

A warrant gap is a missing premise or authority condition that blocks the contemplated target.

Ask:

1. What decision currently matters?
2. What must be true for the contemplated target?
3. Which unresolved premise has a credible alternative answer?
4. Could that answer materially change responsibility, scope, authority, continuation, or closure?
5. What is the cheapest reliable evidence that could resolve it?

Prefer the earliest unresolved dependency capable of invalidating or redirecting downstream work.

Example:

```text
goal:
fix validator behavior

contemplated target:
repair validator

warrant dependencies:
1. validator is still a supported responsibility
2. repository owns the responsibility
3. observed behavior is a live defect
4. repair is authorized
5. implementation detail is correct
```

If dependency 1 is unresolved, do not spend effort optimizing dependency 5 first.

### 3.1 Inquiry Policy

Finding a warrant gap does not automatically justify investigation.

Use the dedicated Inquiry Policy v0 contract in
`inquiry-policy-v0.md` to decide whether additional evidence is worth obtaining.

```text
decision-changing uncertainty identified
-> ask whether evidence could materially change the decision
-> ask whether the evidence is obtainable within authority
-> ask whether expected decision improvement justifies cost/delay
-> NO_INQUIRY_NEEDED
   OR smallest sufficient inquiry
```

Do not use repository research to answer owner intent, and do not use local inference to fabricate external evidence.

```text
inquiry result
!= action authorization

inquiry complete
-> evidence
-> active semantic reassessment
```

## 4. Metareasoning Policy

Metareasoning allocates the next unit of effort after the current decision frame and
Inquiry Policy result are understood.

Use the canonical contract in `metareasoning-policy-v0.md`.

```text
Inquiry Policy
-> what information is worth obtaining, if any

Metareasoning Policy
-> what kind of control move should happen next
```

Possible semantic moves are `ACT`, `INQUIRE`, `CHALLENGE`, `EXPLORE`,
`VERIFY`, `ESCALATE`, and `STOP`.

The choice remains qualitative:

```text
continue reasoning when expected decision improvement
is worth more than reasoning + information + delay + opportunity cost
```

Metareasoning is not a runtime controller and does not authorize the selected move.

## 5. Challenge versus exploration

These are different semantic operators.

### Challenge

Ask:

> **Why might the current frame, claim, forecast, option, or closure decision be wrong?**

Useful challenge outputs include:

- counter-evidence;
- alternative hypotheses;
- omitted constraints;
- omitted stakeholders;
- failure modes;
- falsification tests;
- reasons confidence exceeds justification.

### Exploration

Ask:

> **What plausible frame, option, explanation, or intervention is not yet represented?**

Exploration is useful when the current option set may be too narrow even if the options have been compared correctly.

Useful exploration outputs include:

- alternative responsibilities;
- reframed problem boundaries;
- different causal explanations;
- different intervention classes;
- cross-domain analogies;
- low-cost reversible probes.

## 6. When challenge is worth the cost

Consider adversarial challenge when one or more are materially present:

- high consequence of error;
- low reversibility;
- conflicting evidence;
- unusually high confidence from weak evidence;
- novel or poorly understood domain;
- repeated failure;
- narrow option set on a consequential decision;
- stakeholder/value conflict;
- unstable decision frame;
- protected external commitment;
- closure claim with weak falsification evidence.

Do not add critic ceremony by default.

A critic or subagent returns evidence.

```text
critic output
!= automatic veto
critic output
!= approval
critic confidence
!= authority
```

The active semantic controller adjudicates the challenge under the current authority boundary.

## 7. When exploration is worth the cost

Explore when:

- all current options are weak;
- only one consequential option has been generated;
- repeated attempts fail;
- the current frame causes circular investigation;
- evidence suggests the problem category may be wrong;
- local optimization may hide a better responsibility boundary;
- an important opportunity is plausible but absent from the current option set.

Stop exploring when:

- additional alternatives are unlikely to change the decision;
- the selected option is sufficiently warranted and reversible;
- search cost exceeds likely decision improvement;
- authority or time constraints dominate;
- remaining alternatives are materially dominated by current evidence.

No numeric score is required.

### Exploration Policy v0 — iterative-search allocation

When multiple meaningful attempts create a real search history, use the canonical
`exploration-policy-v0.md` contract to decide where search effort goes next:

- **EXPLOIT** — refine the current best;
- **EXPLORE** — try a materially different direction;
- **CHALLENGE** — seek falsification or counter-evidence;
- **DIAGNOSE** — investigate why an attempt failed before discarding its underlying idea;
- **RECOMBINE** — combine useful mechanisms from different attempts;
- **RESTART** — leave the current local search region or frame;
- **VERIFY** — confirm that a promising result is real before further optimization;
- **EXIT_SEARCH** — return control when more search is not worth its cost.

These are qualitative search modes, not a required enum, score, planner, or routing table.

For one-shot, local, obvious work, keep search allocation implicit.

```text
exploration operator
!= Exploration Policy

search history exists
!= persistent search-tree required

Exploration Policy
!= Strategic Frontier ranking
```

Search history is an on-demand projection of existing evidence/provenance. Reuse
Campaign, handoff, STATUS, strategic alternatives, repository history, and explicit
evidence before considering any new durable state.

## 8. Resource-aware stopping

Reasoning consumes time, attention, compute, tool calls, experiments, and opportunity.

Use this qualitative control law:

```text
continue reasoning when expected decision improvement
is worth more than reasoning + information + delay + opportunity cost
```

You do not need to calculate this numerically.

### Cheap reversible action

```text
cheap + reversible + low consequence + information-producing
-> acting can be better than thinking longer
```

### Consequential irreversible action

```text
consequential + irreversible + externally visible
-> stronger evidence / challenge / verification / authority may be warranted
```

High uncertainty alone does not require more research. Low uncertainty alone does not authorize action.

## 9. Delegation and subagents

Delegation should carry a bounded responsibility rather than a vague request to “solve everything.”

Specify:

```text
responsibility
scope
authority
expected artifact/evidence
success conditions
stop conditions
```

Examples of delegable work:

- bounded repository investigation;
- code change under a selected responsibility;
- adversarial review;
- alternative generation;
- proof attempt;
- verification;
- domain-specific analysis.

The parent/active agent retains the live decision frame unless that semantic authority was explicitly delegated.

```text
worker recommendation
!= parent decision

worker success
!= global closure

worker capability
!= authority expansion
```


### 9.1 Organization boundary

Adaptive Agency Abstraction Stack v0 provides the supporting research vocabulary for distinguishing bounded delegation from materially multi-actor organization. See ../../../docs/research/adaptive-agency-abstraction-stack-v0.md and ../../../docs/research/adaptive-agency-abstraction-stack-v0-reconciliation.md.

~~~text
delegation
!= Organization automatically

Campaign != Organization

organization pattern != execution authority
~~~

Campaign preserves the live decision/responsibility/evidence/authority state. Organization describes how multiple actors are arranged through roles, specialization, communication, or coordination topology. A Campaign may be executed by one agent; an external multi-agent organization may execute work inside a Campaign without moving organizational topology into Campaign state.

Under the current ADR 0029 boundary, adaptive worker allocation, scheduling, peer communication topology, and team lifecycle belong primarily to the external harness / software-factory / orchestration environment. Sensemaking should preserve the warranted responsibility, authority envelope, evidence requirements, and semantic reassessment boundary rather than become an organization runtime.

~~~text
organizational capability
!= Sensemaking runtime responsibility

organizational pattern discovered
!= organizational pattern authorized

capability growth
!= authority growth
~~~

## 10. Execution and orchestration return evidence upward

Use the existing control law:

> **Decision selects the work. Orchestration coordinates the work. Evidence determines what becomes warranted next.**

A useful handoff shape is:

```text
selected responsibility
+ scope
+ authority envelope
+ expected evidence
-> orchestration / worker / tool
-> result
-> evidence
-> semantic reassessment
```

Execution failure is also evidence.

Use the canonical `learning-reconciliation-policy-v0.md` contract when returned
evidence could materially change an explicit claim, uncertainty, responsibility,
continuation/closure state, or strategic frame.

```text
execution failure
-> evidence
-> Learning / Reconciliation
-> semantic reassessment
-> retry same responsibility
   OR revise responsibility
   OR stop
   OR escalate
```

```text
result returned
!= state update automatic

learning
!= model-weight update
```

A retry or fallback policy may coordinate the selected responsibility.

It does not authorize a materially different responsibility.

## 11. Mechanical validation versus semantic judgment

Deterministic machinery may answer questions such as:

- does the target identity match?
- is state current?
- does a referenced artifact exist?
- does the digest match?
- is a schema valid?
- does the transition chain reconstruct?
- did configured tests pass?
- is required approval metadata present?

It may not silently promote those facts into semantic conclusions.

```text
evidence exists
!= evidence is sufficient

schema valid
!= decision is correct

test passed
!= user value created

capability compatible
!= capability selected

authority metadata present
!= authority inferred beyond the declaration
```

## 12. Persistence rule

Persist only what a fresh context needs to reconstruct a consequential decision.

Useful durable content can include:

```text
commitments
decision frame
material evidence / claims
decision-relevant uncertainty
selected responsibility
authority
concise rationale
stop conditions
reopen conditions
provenance / currentness
transition history
```

Use current Sensemaking durable surfaces first:

- Campaign state and handoff;
- Campaign evidence/transitions;
- strategic state / STATUS;
- semantic-state companions;
- ADRs;
- target snapshot/currentness;
- existing authority metadata.

```text
practical architecture used
!= Campaign required
```

Create durable Campaign state only when continuation complexity warrants it.

Do not persist hidden chain-of-thought. Persist explicit conclusions, evidence, dependencies, rationale, and conditions needed for reconstruction.

### Knowledge externalization / transferability

Durable state and transferable knowledge are related but not identical.

Externalize the selected decision-relevant subset when one or more are material:

- continuation crosses context or actor boundaries;
- rediscovery would be meaningfully costly;
- consequential rationale or evidence must remain reconstructible;
- governance, operations, users, or auditors need the knowledge in an intelligible form;
- future search quality depends on preserving attempts, outcomes, or failure attribution.

Use existing Sensemaking surfaces first: ADRs, handoffs, Campaign/strategic state, artifacts, reports, Skills/reference docs, and repository history.

```text
reasoning result
!= durable artifact required

raw durable state
!= sufficiently transferable knowledge
```

Externalize conclusions, rationale, evidence, and material search history when warranted; do not externalize private chain-of-thought merely because it existed.

## 12. Value and normative conflict

At the value layer, distinguish empirical disagreement from normative contestation.

Evidence can help answer:

- who benefits;
- who bears costs;
- what outcomes are likely;
- what assumptions are false;
- what trade-offs exist.

Evidence does not automatically settle every legitimate conflict among values, rights, or stakeholders.

When legitimacy/governance requires an owner or human decision:

```text
surface the conflict
+ provide consequences/evidence
+ preserve alternatives
-> escalate to the authorized decision owner
```

Do not manufacture a deterministic value resolution.

## 13. Progressive disclosure

Use the lightest visible structure that preserves the invariants.

```text
trivial + local + reversible
-> keep most architecture implicit

ambiguous responsibility
-> make decision frame / warrant gap explicit

high consequence / low reversibility
-> make warrant, challenge, evidence, authority explicit

narrow or repeatedly failing option set
-> make exploration explicit

cross-context continuation
-> use durable Campaign state when warranted
```

More architecture does not mean more ceremony for every task.

## 14. Compact decision checklist

For consequential work, ask:

```text
What exactly am I trying to justify now?

What must be true for that target to be warranted?

Which missing premise could change responsibility, scope, authority,
continuation, or closure?

Would challenge reveal a likely failure mode?

Is the option set too narrow?

Is more reasoning worth more than acting now?

What authority is required?

What evidence should selected work return?

What must survive into a fresh context?
```

Then act, investigate, stop, escalate, verify, or close only as warranted.

## 15. Anti-patterns

Avoid:

- converting warrant into a numeric score;
- creating automatic warrant ranking;
- treating warrant as authorization;
- using critic majority vote as semantic truth;
- requiring adversarial review on every task;
- exploring endlessly because more possibilities exist;
- creating a Campaign merely because work is consequential;
- persisting hidden chain-of-thought;
- letting a worker/subagent silently redefine the parent responsibility;
- letting an orchestration fallback cross authority or product boundaries;
- treating deterministic validation as semantic closure;
- creating a generic agent runtime inside Sensemaking because the conceptual model is broad.

## 16. Relationship to current Sensemaking

This reference does not replace:

- the Semantic Architecture Reasoning Model;
- the Four-Level Control Model;
- Campaign semantics;
- Strategic Repository Evolution;
- Product Thesis / Strategy Revision;
- authority contracts;
- existing validators and qualification.

Instead, it supplies a compact practical interpretation:

```text
General Agency concepts
-> target-specific warrant
-> existing Sensemaking decision/control surfaces
-> bounded execution
-> evidence
-> semantic reassessment
```

The active coding agent remains the semantic controller.

## Inherited-responsibility backstop: worked example

(Moved verbatim from `using-sensemaking/SKILL.md` section 3. The rule and its distinctions remain in the core.)

Example:

```text
inherited responsibility:
qualify / release / verify the candidate

decision-critical prerequisite:
the candidate represents the intended sufficiently complete product state

repository evidence:
buildable/reachable = established
product/content completion = materially unresolved

result:
RESPONSIBILITY_PRECONDITION_NOT_ESTABLISHED
-> return upstream through Learning / Reconciliation
-> do not optimize the downstream qualification responsibility yet
```
