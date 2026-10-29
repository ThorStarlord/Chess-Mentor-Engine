# Warrant / Choice Policy v0 — Agent Contract

**Status:** canonical agent-facing semantic policy  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive control guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic policy; not a permission token, score, rule engine, ranking service, or automatic chooser

## 1. Question

Warrant / Choice Policy answers:

> **Given a specific contemplated target, current state, evidence, constraints, and
> authority, what is justified now—and if several targets are credibly warranted,
> which one should be selected, if any?**

Warrant is target-specific and defeasible.

```text
W(target | goal, current_state, evidence, constraints, authority)
```

The notation is explanatory only. It is not a runtime function or numeric score.

## 2. Name the warrant target first

Do not ask whether “we have warrant” in the abstract.

Name the specific target currently being justified.

Useful target classes include:

```text
claim
inquiry
responsibility
action
continue
stop
escalate
verification claim
closure
protected transition
strategic direction
```

Examples:

```text
target: claim this defect is real

target: select docs reconciliation as the current responsibility

target: continue investigating rather than act

target: claim the original finding is closed

target: recommend merge

target: perform merge

target: choose construction path B
```

```text
warrant for target A
!= warrant for target B
```

Evidence sufficient to justify investigation may not justify repair. Exact-head green CI
may justify a candidate-level validation claim but not original-finding closure.
Technical justification may support a merge recommendation without granting merge
authority.

## 3. Inputs

Use the smallest current decision context sufficient for the target:

```text
GOAL / DECISION TO SUPPORT
WARRANT TARGET
CURRENT STATE / CURRENTNESS
TARGET-SPECIFIC DEPENDENCIES
SUPPORTING EVIDENCE
DEFEATING / CONFLICTING EVIDENCE
MATERIAL UNCERTAINTY
CONSTRAINTS
CONSEQUENCE + REVERSIBILITY
AUTHORITY / OWNER / EXTERNAL BOUNDARIES
ALTERNATIVE CREDIBLE TARGETS, WHEN CHOICE IS MATERIAL
SMALLEST WARRANTED INTERVENTION
```

Do not require a new durable warrant object when these facts are already reconstructible
from existing Sensemaking surfaces.

## 4. Warrant dependencies

For a consequential target, identify the few premises that must be true.

Example:

```text
target:
repair validator

dependencies:
1. validator is still a supported responsibility
2. repository owns the responsibility
3. observed behavior is a live defect
4. repair is appropriate to the current product contract
5. repair is authorized in the current scope
```

Prefer the nearest unresolved dependency capable of invalidating or redirecting the
target.

```text
dependency 1 unresolved
-> do not optimize dependency 5 first
```

A dependency may be factual, semantic, contractual, authority-related, owner-reserved,
or external.

When the target/responsibility was selected upstream, do not exempt it from this
dependency check. Treat upstream selection as defeasible evidence of prior
warrant. If a current decision-critical prerequisite is not established, return
to reconciliation/upstream adjudication rather than forcing execution.

```text
upstream selected target
!= dependency-free target

inherited responsibility
+ prerequisite materially unresolved
-> target warrant must be reassessed
```

## 5. Warrant dispositions

These are documentation-level semantic dispositions, not runtime enums.

### `WARRANTED`

Current evidence/state/constraints are sufficient to justify the target **as a semantic
choice**.

This does not automatically grant protected-action authority.

```text
WARRANTED
!= authorized
!= executed
!= successful
```

### `NOT_WARRANTED`

Current evidence actively weighs against the target, another target dominates it, or the
target no longer serves the current decision.

Examples:

- current repository behavior disproves the claimed defect;
- the responsibility is obsolete/superseded;
- a smaller intervention resolves the same decision;
- the target depends on a stale premise.

### `MORE_EVIDENCE_REQUIRED`

A decision-changing dependency remains unresolved and additional evidence could
materially change the target.

Return control to Inquiry Policy / Metareasoning rather than gathering evidence by
default.

### `AUTHORITY_REQUIRED`

The target may be technically/semantically justified, but current authority does not
permit the protected decision/action.

```text
technical warrant
!= action authority
```

Do not manufacture authority from green CI, implementation success, or owner silence.

### `OWNER_DECISION_REQUIRED`

The blocking premise is owner intent, product commitment, acceptance, or another
reserved decision rather than repository evidence.

Do not use technical investigation to infer the owner’s preference.

### `CHALLENGE_REQUIRED`

The target is consequential enough, weakly supported enough, or irreversible enough
that adversarial falsification should occur before commitment.

Return to Metareasoning / challenge with an explicit target and falsification question.

### `EXPLORATION_REQUIRED`

The current option set is too narrow or unstable to responsibly select a target.

Return to Metareasoning / Exploration Policy rather than forcing a winner from an
inadequate option set.

### `VERIFICATION_REQUIRED`

Work or a result already exists, but the claim/closure/transition target needs direct
verification before it can be warranted.

Finding-specific verification may be required even when generic CI is green.

### `SMALLER_INTERVENTION_PREFERRED`

The contemplated target may be directionally reasonable, but a smaller/reversible
intervention can resolve the same decision with lower commitment.

Prefer the smallest sufficient intervention.

### `NO_SELECTION`

For a material choice set, none of the current targets has sufficient warrant.

This is a valid successful result.

```text
candidate set exists
!= one candidate must be selected
```

## 6. Choice among several credible targets

Choice occurs **after** target-specific warrant has been made explicit enough to compare
the material options.

Do not score or rank every candidate.

Ask qualitatively:

1. Which targets are actually warranted by current evidence?
2. Which target most directly serves the current decision?
3. Which target resolves the nearest decision-changing gap?
4. Which target has the smallest sufficient intervention?
5. Which target preserves optionality/reversibility where evidence is still limited?
6. Which target has required authority available?
7. Which target is blocked by unresolved dependencies?
8. Is one option merely a substep or duplicate of another?
9. Would selecting none be more justified than forcing a winner?

Select one target when the decision genuinely requires commitment. Otherwise preserve
the credible option set or return `NO_SELECTION`.

```text
qualitative choice
!= deterministic ranking

agent judgment
!= unexplained intuition
```

## 7. Currency and defeasibility

Warrant is relative to **current** canonical evidence/state.

```text
historically unresolved
!= currently warrant-blocking

previously warranted
!= warranted forever
```

Reassess when:

- repository state changed;
- target identity/currentness changed;
- new evidence defeats a premise;
- authority changed;
- owner intent changed;
- a smaller intervention became available;
- upstream strategy changed;
- a verification result contradicted the target.

Do not reopen a settled decision merely because an old artifact still contains an
unanswered historical question.

## 8. Evidence proportionality

The strength of the target/claim must not exceed the support.

Examples:

```text
schema valid
-> may warrant structural-validity claim

schema valid
!= semantic correctness
!= user value
!= closure

exact-head CI green
-> may warrant candidate-passes-configured-checks claim

exact-head CI green
!= canonical main healthy
!= original finding repaired
!= merge authority
```

A stronger target needs correspondingly stronger evidence and authority.

## 9. Relationship to authority

Warrant and authority are orthogonal inputs.

```text
should this be done?
!= may this actor do it?

technically justified
!= authorized

selected
!= authorized

authorized
!= executed

executed
!= successful
```

When the target itself is a protected transition such as merge/publish/deploy, current
authority is part of the warrant dependencies. Do not treat semantic justification as a
permission token.

## 10. Relationship to the policy hierarchy

```text
Inquiry Policy
-> what information is worth obtaining, if any?

Metareasoning Policy
-> what kind of control move should consume effort next?

Exploration Policy
-> where should iterative search effort go next?

Warrant / Choice Policy
-> what specific target is justified now, and which target should be selected if any?

Action / Execution
-> perform selected authorized work

Learning / Reconciliation
-> what explicit state/claim/uncertainty changes after evidence returns?
```

A warrant gap may trigger Inquiry, Challenge, Exploration, Verification, Escalation, or
Stop, but Warrant / Choice Policy does not perform those activities itself.

## 11. Relationship to Strategic Repository Sensemaking

Strategic Repository Sensemaking may produce several coherent construction paths.

Warrant / Choice Policy can adjudicate a contemplated strategic direction or bounded
repository responsibility using the current strategic decision, evidence, constraints,
and authority.

It must not:

- turn path comparison into a numeric ranking;
- assume one path must win;
- convert a selected path into implementation authority;
- bypass the Strategic Decision to Support;
- treat path plausibility as path warrant.

```text
construction path plausible
!= construction path warranted

path warranted
!= implementation authorized
```

## 12. Relationship to validation and closure

Mechanical validators establish only declared mechanical facts.

```text
validator PASS
!= target warranted automatically
```

Closure requires target-specific evidence.

For a repair:

```text
implementation exists
-> candidate evidence

configured checks green
-> mechanical evidence

finding-specific verification
-> closure-relevant evidence

owner/external authority when required
-> protected transition authority
```

Do not collapse those into one generic `validated=true`.

## 13. Delegation

A worker may investigate warrant dependencies or evaluate a bounded target.

Delegation should specify:

```text
warrant target
dependency/question
scope
authority
expected evidence
success condition
stop condition
```

Worker output returns evidence/recommendation to the active semantic controller.

```text
worker says WARRANTED
!= parent target selected automatically

worker success
!= protected transition authorized
```

## 14. Persistence

Persist warrant reasoning only when fresh-context reconstruction, governance, protected
transition, or consequential continuation needs it.

Persist explicit, reconstructible content such as:

- warrant target;
- material dependencies;
- decisive supporting/defeating evidence;
- selected disposition;
- concise rationale;
- authority boundary;
- invalidation/reopen condition;
- provenance/currentness.

Do not persist hidden chain-of-thought.

Reuse Campaign, STATUS, ADRs, handoffs, evidence artifacts, and repository history before
adding any new state surface.

## 15. Compact use

For a consequential target, ask:

```text
What exactly am I trying to justify now?
What must be true for that target?
Which premise is currently weakest?
What current evidence supports or defeats it?
Is the evidence current and target-specific?
What authority is required?
Is a smaller intervention sufficient?
Are materially different targets still credible?
Must one be selected now?
Would NO_SELECTION be more justified?

Disposition:
WARRANTED
NOT_WARRANTED
MORE_EVIDENCE_REQUIRED
AUTHORITY_REQUIRED
OWNER_DECISION_REQUIRED
CHALLENGE_REQUIRED
EXPLORATION_REQUIRED
VERIFICATION_REQUIRED
SMALLER_INTERVENTION_PREFERRED
NO_SELECTION
```

## 16. Anti-patterns

Avoid:

- a scalar warrant/confidence score;
- treating warrant as a permission token;
- assuming evidence for one target propagates downstream;
- choosing a Skill before naming the responsibility/warrant target;
- forcing one candidate to win;
- turning qualitative comparison into deterministic ranking;
- reopening stale historical uncertainty without checking currency;
- treating validator PASS as semantic warrant;
- building a `WarrantEngine` service/class merely because the policy has a name;
- storing warrant as a universal lifecycle state;
- creating a new schema merely to encode documentation-level dispositions.


## Quick prompts for the active agent

For consequential work, ask: what exactly am I justifying now; what must be
true for it to be warranted; which unresolved premise could change
responsibility, scope, authority, continuation or closure; and is more
reasoning worth more than acting now. Useful targets include a claim, inquiry,
responsibility, action, continue/stop/escalate decision, closure claim, or a
protected transition such as merge or publication.

```text
warrant != confidence score
warrant != authorization
```
