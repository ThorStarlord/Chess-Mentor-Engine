# Value-Producing Action & Delegation v1

**Status:** canonical reference for `strategic-sensemaking-loop`  
**Scope:** action-mode preference, repository delegation, and owner-visible decision trace  
**Authority:** semantic guidance only; no score, router, permission engine, or automatic protected action

## Contents

1. Purpose
2. Action shapes
3. Value-Producing Action Preference
4. Reversible-build dominance test
5. High-delegation repository envelope
6. Protected transitions
7. Blocked-gate continuation
8. Visible decision trace
9. Anti-patterns

## 1. Purpose

Use this reference when the loop must choose among building, verifying,
inquiring, experimenting, or stopping, or when the owner's delegation level is
material to how far the episode may continue autonomously.

The governing principle is:

> Prefer the highest-value **warranted and authorized** action, not merely the
> lowest-risk available action. Use assurance to bound action rather than replace
> value creation.

```text
value creation
subject to
evidence integrity + authority + acceptable downside + reversibility

!=

minimize probability of being wrong
```

This guidance is qualitative. Do not turn it into numeric expected-value scoring.

## 2. Action shapes

Use these as descriptive control/action shapes, not runtime enums:

- **BUILD** — implement a retained capability/feature/responsibility.
- **REVERSIBLE BUILD** — implement useful retained-but-removable capability whose
  normal use also produces decision-relevant evidence.
- **VERIFY / QUALIFY** — test an existing claim, result, candidate, or evidence
  ceiling.
- **PROBE / INQUIRE** — obtain the smallest bounded evidence needed to resolve a
  decision-changing uncertainty.
- **SPIKE / PROTOTYPE** — temporary implementation primarily for feasibility or
  design learning; retention is not assumed.
- **EXPERIMENT** — purpose-designed intervention/comparison used when outcomes can
  materially discriminate among actions.
- **STOP / ESCALATE** — stop or return authority upward when no further warranted
  repository action exists.

```text
feature implementation
-> BUILD

temporary prototype
-> SPIKE / PROTOTYPE

retained product action + evidence
-> REVERSIBLE BUILD

qualification
-> VERIFY / QUALIFY
```

The existing strategic disposition vocabulary remains authoritative. These
action shapes do not add a new artifact enum or schema.

## 3. Value-Producing Action Preference

When multiple actions are sufficiently warranted and authorized, compare them
qualitatively through:

- direct product/capability value if successful;
- decision-relevant information produced;
- reversibility;
- total implementation/inquiry cost;
- consequence of error;
- opportunity/deferral cost;
- maintenance burden;
- authority availability.

Prefer an action that creates durable useful product value **and** sufficient
decision-relevant evidence when it has no materially worse total cost/downside
than a separate evidence-only action.

```text
safe-enough high-value action
should not lose automatically
to lower-value action merely because the latter is safer

omission cost
is part of the decision
```

This is a preference among actions that already cross the warrant/authority
threshold. It does not weaken hard authority, evidence, or consequence
boundaries.

Global roadmap or merge uncertainty does not automatically block a different,
independently authorized local responsibility. If source evidence already
grounds a bounded useful diagnosis or reversible fix, choose it rather than
escalating the entire repository merely because its highest priority is
unsettled. Keep the wider priority question and any protected merge/release
decision unresolved. Do **not** use this to invent defects or infer authorization
to mutate a repository where only read access was granted.

## 4. Reversible-build dominance test

A REVERSIBLE BUILD normally dominates "experiment first, then rebuild the same
capability" when all are true:

1. the capability is already strategically/responsibility-grounded;
2. the implementation is bounded and cheap enough to revise/remove;
3. retaining it would create useful product value if it works;
4. normal use or ordinary verification can produce evidence strong enough for
   the current decision;
5. total build/use/revise cost is no greater than separate experiment overhead
   plus later duplicate implementation;
6. downside and maintenance burden are acceptable;
7. no causal/comparative claim requires stronger experimental isolation.

```text
retained useful value
+ sufficient evidence from normal use
+ acceptable downside
+ no greater total cost
-> prefer REVERSIBLE BUILD

reversible build possible
!= reversible build automatically warranted
```

Prefer READ/INSPECT/VERIFY when they answer the question materially cheaper.
Prefer an experiment when the decision genuinely requires evidence the build
cannot provide without confounding the inference.

## 5. High-delegation repository envelope

When the owner explicitly grants broad autonomous repository continuation
(for example "proceed without my input", "continue autonomously", or an
equivalent repository-scoped instruction), treat that as a **high-delegation
repository envelope** unless a narrower repository policy or explicit owner
constraint overrides it.

Within the explicitly selected repository/scope, this may authorize ordinary
repository-answerable work such as:

- inspect/analyze/reconcile current state;
- select and execute bounded BUILD responsibilities;
- perform REVERSIBLE BUILD, repair, refactor, simplification, and documentation;
- run or dispatch existing tests, verification, and qualification surfaces;
- perform bounded PROBE/SPIKE/EXPERIMENT work only when separately warranted by
  Inquiry/Experiment Economy;
- create/update repository-local plans, issues, branches, commits, and draft PRs
  when those are part of the requested development workflow;
- reconcile returned evidence and continue to the next independently warranted
  repository responsibility.

```text
high delegation
= broad repository operating authority

high delegation
!= unlimited authority
```

Do not require a fresh approval merely to move between ordinary repository
actions already covered by this envelope.

## 6. Protected transitions

High delegation does not silently authorize:

- Level-4 product-thesis choices;
- genuinely preference-sensitive owner decisions;
- production release/deployment when separately protected;
- merge when repository/owner policy reserves it;
- credentials, secrets, billing, or account/security changes;
- destructive or unrelated external mutations;
- expansion into another repository/product scope without authority.

Repository policy and explicit owner constraints override the generic envelope.

```text
autonomy
!= authority

broad execution authority
!= protected-transition authority
```

## 7. Blocked-gate continuation

An external or unavailable gate may block **one responsibility** without proving
that the entire repository must become strategically quiescent.

When a required verification/qualification gate cannot execute:

1. preserve the blocked responsibility and claim ceiling;
2. do not evade the gate by pretending unverified work is complete;
3. ask whether another **independently warranted** value-creating responsibility
   exists that does not depend on, undermine, or route around the blocked gate;
4. continue only when that other responsibility has its own strategic/responsibility
   warrant and authority;
5. otherwise stop at the external blocker.

```text
blocked responsibility
!= repository-wide freeze automatically

independent work exists
!= permission to bypass blocked verification
```

## 8. Visible decision trace

For consequential Level-3 selection or a materially contested control move,
surface a compact owner-visible rationale in the final report.

Show only decision-relevant conclusions, not private scratch reasoning.

Use this shape when material:

```text
MATERIAL ALTERNATIVES CONSIDERED

A — <path / control move>
Value created:
Why plausible:
Why not selected now:

B — <path / control move>
Value created:
Why plausible:
Why selected / not selected:

SELECTED CONTROL MOVE
BUILD | REVERSIBLE BUILD | VERIFY/QUALIFY |
PROBE/INQUIRE | SPIKE/PROTOTYPE | EXPERIMENT | STOP

VALUE CREATED IF SUCCESSFUL
<product/capability improvement>

WHY A MATERIALLY MORE CONSERVATIVE MOVE WAS LESS WARRANTED
<brief>

WHY A MATERIALLY MORE AGGRESSIVE MOVE WAS LESS WARRANTED
<brief>
```

Do not fabricate alternatives merely to fill this display. If one path is
materially dominant, say so and explain the rejected class of alternatives
briefly.

The trace is user-facing observability. It is not a new durable artifact, score,
or substitute for the canonical strategic artifact.

## 9. Anti-patterns

Do not:

- choose the least risky action after several options are already safe enough
  merely because it minimizes commission risk;
- convert every uncertainty into a reversible build;
- accumulate disposable prototypes when a retained build is already warranted;
- use a reversible build to avoid evidence standards needed for a causal claim;
- interpret "proceed autonomously" as merge/release/deploy authority;
- stop the whole repository merely because one gate is externally blocked when
  unrelated independently warranted work exists;
- continue unrelated side quests merely to avoid stopping at a real blocker;
- hide all material strategic alternatives from the owner while claiming that
  path comparison occurred;
- add numeric expected-value scoring, automatic routing, or permission machinery.
