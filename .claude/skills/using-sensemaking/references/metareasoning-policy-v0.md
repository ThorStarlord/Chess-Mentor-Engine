# Metareasoning Policy v0 — Agent Contract

**Status:** canonical agent-facing semantic policy  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive control guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic policy; not a service, scheduler, score, state machine, or automatic router

## 1. Question

Metareasoning Policy answers:

> **Given the current decision, inquiry state, evidence, consequence, reversibility,
> authority, and resource cost, what kind of control move should consume the next
> unit of effort?**

It allocates reasoning and action effort. It does not choose a product thesis,
grant authority, or mechanically decide semantic truth.

## 2. Relationship to Inquiry Policy

Inquiry Policy answers:

> What should we learn next, if anything?

Metareasoning Policy consumes that result alongside the broader decision context.

```text
Inquiry Policy
-> NO_INQUIRY_NEEDED
   OR a smallest sufficient inquiry / source / stop condition

Metareasoning Policy
-> what kind of control move should happen next?
```

If Inquiry Policy returns `INQUIRY_REQUIRED`, `INQUIRE` is a candidate control
move, not an automatic next move. `ACT` may still dominate when a cheap,
reversible, authorized, information-producing action can supply the needed
evidence at lower total cost. Authority/external constraints may instead make
`ESCALATE` or `STOP` appropriate.

If Inquiry Policy returns `NO_INQUIRY_NEEDED`, do not select `INQUIRE` merely
because more information could exist.

The hierarchy is not a runtime call stack. Policy layers may remain implicit when the
decision is obvious.

## 3. Inputs

Reason from the smallest current context needed to choose the next control move:

```text
DECISION TO SUPPORT
CONTEMPLATED WARRANT TARGET
CURRENT RESPONSIBILITY, IF ANY
INQUIRY POLICY RESULT
CURRENT CLAIMS / EVIDENCE
MATERIAL UNCERTAINTY
CONSEQUENCE + REVERSIBILITY
AUTHORITY / EXTERNAL CONSTRAINTS
SEARCH / ATTEMPT HISTORY, IF MATERIAL
VERIFICATION / CLOSURE STATE
REASONING + INFORMATION + DELAY + OPPORTUNITY COST
```

Do not create a new persistent object when these inputs already exist in Campaign,
STATUS, handoff, evidence, repository, or transient working context.

## 4. Control moves

These are documentation-level semantic dispositions, not runtime enums.

### `ACT`

Spend the next unit of effort performing an already-selected, authorized bounded
responsibility rather than reasoning longer.

Typical conditions:

- current evidence is sufficient for the present decision;
- no unresolved premise is likely to redirect the responsibility;
- authority is available;
- the action is cheap/reversible/low consequence, or the warrant is otherwise strong;
- acting itself may return useful evidence;
- a cheap reversible build can answer the decision-changing uncertainty with
  less total overhead than a separate investigation or experiment.

```text
ACT
!= responsibility selected automatically
!= authority granted automatically
```

### `INQUIRE`

Obtain the smallest sufficient evidence already identified by Inquiry Policy.

`INQUIRE` does not mean experiment. Reading, inspection, verification, owner or
external clarification, a bounded probe, and other low-cost evidence sources
may satisfy the inquiry. When experimentation is materially considered, apply
the Experiment Warrant and proportional-rigor guidance in
`experiment-economy-v1.md`.

Use when:

- the inquiry is decision-changing;
- the evidence source is available within authority;
- the expected decision improvement justifies information/reasoning/delay cost.

```text
INQUIRE
-> execute the bounded inquiry
-> return evidence
-> semantic reassessment
```

### `CHALLENGE`

Spend effort trying to falsify or stress the current frame, claim, option, forecast,
or closure decision.

Prefer challenge when:

- consequence is high;
- reversibility is low;
- evidence conflicts;
- confidence appears stronger than support;
- a protected external transition is contemplated;
- failure would be costly enough that adversarial checking is warranted.

Challenge output is evidence, not veto or approval.

### `EXPLORE`

Broaden the represented option/frame space because the current set may be too narrow.

Prefer exploration when:

- only one consequential option is represented;
- repeated attempts fail locally;
- the frame produces circular investigation;
- materially different responsibilities may exist;
- local optimization may hide a better boundary.

If exploration becomes iterative search with meaningful history, hand allocation to
Exploration Policy v0 once that layer is active.

### `VERIFY`

Check whether an existing result, repair, claim, or candidate really satisfies the
relevant contract before further commitment or closure.

Prefer verification when:

- work already occurred;
- a consequential claim depends on that work;
- generic green tests are weaker than finding-specific proof;
- a promising result should be confirmed before more optimization.

```text
result exists
!= result verified

verification passed
!= global closure automatic
```

### `ESCALATE`

Return the decision to an authorized owner or higher control scope because the missing
premise cannot be legitimately resolved at the current scope.

Examples:

- owner intent / product preference is the actual missing premise;
- protected authority is required;
- Level-3 evidence exposes a Level-4 thesis contradiction;
- an external system or actor controls necessary evidence/action;
- current authority cannot safely perform the next step.

Escalation should carry the decision, evidence, alternatives, and authority gap rather
than a vague request for direction.

### `STOP`

Spend no further effort on the current line because additional reasoning/action is not
warranted.

Stop when, for example:

- the decision is already sufficiently supported and no action remains;
- no current responsibility is warranted;
- expected decision improvement is lower than reasoning/information/delay/opportunity cost;
- authority or external blockers dominate;
- remaining alternatives are materially dominated;
- the current line is invalidated and must await a different decision/frame.

`STOP` may mean local stopping, deferral, or no-selection. It does not automatically
mean repository closure or Campaign terminal state.

## 5. Qualitative selection law

Use the existing resource-aware control law:

```text
continue reasoning when expected decision improvement
is worth more than reasoning + information + delay + opportunity cost
```

No numeric calculation is required.

Useful directional rules:

```text
cheap + reversible + low consequence + information-producing
-> ACT may dominate more thinking or a separate experiment

decision-changing unknown + worthwhile evidence
-> INQUIRE only when a separate inquiry beats acting as the evidence source

weakly supported commitment + high consequence / low reversibility
-> CHALLENGE

option poverty / unstable frame / repeated local failure
-> EXPLORE

material result exists but closure claim is unverified
-> VERIFY

missing owner / higher-scope / external authority
-> ESCALATE

no move expected to improve the decision enough to justify cost
-> STOP
```

Select the **smallest control move** likely to improve the decision or safely advance
the already-selected responsibility.

## 6. Tie handling

Several moves may be plausible.

Do not create a score or ranking function. Ask:

1. Which move addresses the nearest decision-changing gap?
2. Which move has the lowest **total** cost consistent with consequence/reversibility?
3. Could cheap reversible action produce the needed evidence while also advancing the product?
4. Which move preserves optionality?
5. Which move would most directly change what becomes warranted next?
6. Is one move merely a substep of another?

Record one primary next move when a consequential handoff/reconstruction needs it.
Otherwise keep the judgment transient.

## 7. Authority and ownership

Metareasoning allocates effort; it does not expand authority.

```text
control move selected
!= responsibility authorized

ACT selected
!= protected mutation authorized

CHALLENGE / EXPLORE output
!= semantic truth

ESCALATE selected
!= owner decision manufactured
```

The active semantic agent remains responsible for interpreting evidence and applying
current authority contracts.

## 8. Relationship to other policies

```text
Strategic Policy
-> which repository decision matters?

Inquiry Policy
-> what should we learn next, if anything?

Metareasoning Policy
-> what kind of control move should consume effort next?

Exploration Policy
-> where should iterative search effort go once exploration/search is warranted?

Warrant / Choice Policy
-> what contemplated target is justified now?

Action / Execution
-> perform selected authorized work

Learning / Reconciliation
-> what explicit state/claim/uncertainty changes after evidence returns?
```

Metareasoning does not replace these layers.

## 9. Compact use

For consequential work, ask:

```text
What decision / warrant target matters now?

What did Inquiry Policy conclude?

Would acting now be cheap, reversible, and sufficiently warranted?

Do consequence or irreversibility justify challenge?

Is the option/frame set too narrow?

Is there a result/claim that should be verified before further commitment?

Is the real gap authority/owner/higher-scope rather than evidence?

Is any additional effort worth its cost?

Choose:
ACT / INQUIRE / CHALLENGE / EXPLORE / VERIFY / ESCALATE / STOP
```

For obvious local work, keep this implicit.

## 10. Anti-patterns

Avoid:

- calculating a numeric “reasoning budget score”;
- invoking every control move in sequence;
- treating the list as a fixed state machine;
- forcing inquiry after Inquiry Policy returned `NO_INQUIRY_NEEDED`;
- treating `INQUIRY_REQUIRED` as an automatic command to experiment;
- selecting a separate inquiry when cheap reversible `ACT` is the cheaper sufficient evidence source;
- escalating experimental rigor merely because cleaner evidence is possible;
- challenging or exploring trivial reversible work by default;
- using metareasoning to select a Skill automatically;
- treating `ACT` as authority;
- persisting every metareasoning judgment;
- building an `OuterLoopEngine`, scheduler, or controller service merely to host these labels.
