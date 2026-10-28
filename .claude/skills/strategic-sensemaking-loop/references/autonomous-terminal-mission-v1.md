# Autonomous Terminal Mission Continuation v1

**Status:** canonical reference for `strategic-sensemaking-loop`  
**Scope:** full-autonomy / full-repository-delegation continuation toward a bounded terminal repository outcome  
**Authority:** semantic guidance over the existing high-delegation repository envelope; no planner, permission engine, new control level, or automatic protected-transition authority

## Contents

1. Purpose
2. Mission contract
3. Target selection
4. Conditional breadth and depth
5. Repeated responsibility continuation
6. Construction completeness
7. Construction before field validation
8. Synthetic personas and first-principles evaluation
9. Verification, reconciliation, and canonical promotion
10. Authority envelope
11. Stop conditions
12. Canonical prompt
13. Anti-patterns

## 1. Purpose

Use this reference when the owner explicitly delegates a terminal repository
mission with phrases such as:

- "FULL AUTONOMY";
- "FULL DELEGATION";
- "proceed without my input";
- "continue until the repository outcome is complete";
- `AUTONOMOUS_HIGHEST_LEVERAGE_BOTTLENECK`;
- an equivalent instruction to keep selecting and executing repository-answerable
  responsibilities until a terminal outcome or genuine boundary is reached.

This profile does not create a second Sensemaking loop.

```text
full-autonomy mission
=
terminal mission contract
+ strategic-sensemaking-loop
+ high-delegation repository envelope
+ repeated responsibility -> execution -> evidence -> reconciliation

!=
new planner
+ new authority model
+ backlog executor
```

The active semantic agent remains responsible for judgment.

## 2. Mission contract

Before continuing autonomously, make the following reconstructible from the
owner request and current repository authority:

```text
TERMINAL GOAL
What repository/product outcome should become true?

OPERATING POLICY
How should intermediate responsibilities be selected?

SCOPE DISCIPLINE
Which current authorities define required work?

AUTHORITY DISCIPLINE
Which actions are delegated and which protected transitions remain reserved?

VALIDATION POLICY
Which repository-answerable evidence is required before claims/status promotion?

STOP CONDITIONS
What makes the mission legitimately terminal?
```

Prefer current repository authority over stale issue/backlog/history text.

```text
terminal mission
!= execute every issue

mission incomplete
!= keep improving forever

full delegation
!= unlimited scope
```

## 3. Target selection

When the owner names a target system or feature, use that target subject to
current authority and prerequisite checks.

When the owner explicitly uses
`AUTONOMOUS_HIGHEST_LEVERAGE_BOTTLENECK`, interpret it as:

> Identify the highest-value remaining difference between current repository
> reality and the authoritative terminal outcome, establish the bounded
> responsibility that can most usefully reduce that difference now, and execute
> it within current authority.

This is qualitative semantic judgment.

Do not introduce a numeric leverage score, automatic priority queue, or backlog
ranking engine.

If the repository future itself is materially open, return to the existing
Level-3 `ANALYZE / REOPEN_ANALYSIS` boundary. If strategy is current, do not
reopen it merely because the owner requested autonomy.

## 4. Conditional breadth and depth

Full autonomy does not imply a mandatory three-option architecture exercise.

At a genuine `ANALYZE / REOPEN_ANALYSIS` boundary, use the existing Strategic
Exploration Funnel:

```text
system map
-> breadth exploration
-> frontier candidates
-> proportional depth
-> construction paths
-> selection
```

Use 0-5 materially real construction paths when the strategic decision genuinely
supports that many. Do not force exactly three alternatives, manufacture
orthogonality, or deeply design every breadth candidate.

```text
Level 3 open
-> breadth before convergence

strategy settled
-> resume current responsibility/execution/reconciliation

full autonomy
!= rerun strategic breadth after every responsibility
```

## 5. Repeated responsibility continuation

The defining behavior of this profile is continuation across multiple bounded
responsibilities.

After every consequential responsibility:

1. obtain the applicable mechanical/static/runtime evidence;
2. reconcile the result and current claim ceiling;
3. compare current repository reality with the terminal goal;
4. determine whether a material remaining difference exists;
5. if yes, establish the next highest-value **warranted and authorized** bounded
   responsibility;
6. continue immediately without asking for approval that the mission envelope
   already grants;
7. reopen Level 3 only when returned evidence genuinely invalidates or materially
   reopens strategy.

```text
responsibility completed
!= mission completed

mission incomplete
!= execute backlog blindly

mission incomplete
-> reconcile current reality
-> identify highest-value remaining difference
-> establish next warranted responsibility
-> continue
```

A blocked responsibility does not freeze the whole mission when another
independently warranted responsibility can proceed without bypassing the blocked
gate.

Do not create one giant Campaign merely because the mission is large. Use
Campaign durability when continuation complexity warrants it.

## 6. Construction completeness

For the selected responsibility, complete every **decision-relevant vertical
layer** required by the target capability.

Depending on the product, this may include:

- domain rules/models/state transitions;
- public interfaces, APIs, service or event contracts;
- persistence and migrations;
- integrations/adapters;
- user-facing interaction and presentation;
- operator/admin/audit surfaces;
- observability and actionable reporting;
- content/scenario/progression coverage;
- compatibility and recovery behavior;
- documentation and repository authority surfaces;
- tests, verification, and qualification evidence.

Do not manufacture layers that the capability does not need.

```text
complete vertical path
!= maximum architecture

production-quality responsibility
!= add API + event bus + persistence + dashboard to every feature
```

Prefer derived state over redundant shadow state. Remove stale inherited behavior
encountered on the selected path when retaining it would conflict with the
current authority or completed behavior.

Evaluate completion at the capability/user/operational scale relevant to the
terminal mission, not merely at the file or fixture scale.

## 7. Construction before field validation

A mission may explicitly adopt **construction before field validation** when the
owner has intentionally scheduled external validation after construction.

Under that mission policy:

- do not halt construction merely to request live user trials, beta feedback,
  stakeholder panels, professional asset recording, or live telemetry;
- use repository-answerable verification and bounded design judgment to continue
  construction;
- preserve external validation as a later claim boundary rather than pretending
  it occurred.

This policy is mission-scoped and defeasible.

If current authoritative product, safety, legal, regulatory, or repository
requirements make external evidence a genuine prerequisite for the contemplated
claim/action, preserve that prerequisite and stop or narrow the claim rather than
bypassing it.

```text
construction before field validation
!= external validation never matters

external validation deferred
!= externally validated
```

## 8. Synthetic personas and first-principles evaluation

First-principles domain heuristics and synthetic personas may be used to resolve
construction-stage UX, architectural, progression, and operational tradeoffs
when repository evidence does not require a real external user decision.

Treat them as reasoning aids only.

```text
synthetic persona
= design reasoning aid

synthetic persona
!= empirical user evidence

first-principles heuristic
!= field validation
```

Do not claim user validation, usability validation, stakeholder approval, or
live-product evidence from synthetic reasoning.

## 9. Verification, reconciliation, and canonical promotion

Implementation alone does not justify canonical status.

Use the applicable repository evidence ladder:

```text
implement
-> mechanical/static verification
-> applicable unit/integration/runtime verification
-> failure/recovery/edge verification when material
-> reconciliation
-> status/authority promotion only when supported
```

The mission may authorize the agent to update status manifests, capability
registries, routing manifests, and canonical documentation **when the evidence
supports that promotion**.

Do not predetermine the semantic conclusion merely because promotion authority
was delegated.

Preserve useful claim distinctions when external evidence remains pending:

```text
construction complete
repository qualified
external validation pending
production release ready
production deployed
```

These are descriptive claim distinctions, not new runtime enums or a mandatory
artifact schema.

```text
implemented
!= verified

verified
!= externally validated

repository qualified
!= production deployed

authority to promote
!= evidence already supports promotion
```

## 10. Authority envelope

A full-autonomy repository mission normally inherits the existing
high-delegation repository envelope.

Within the selected repository/scope, this may include:

- inspect, analyze, and reconcile;
- select bounded repository-answerable responsibilities;
- design and implement;
- repair, refactor, simplify, or remove obsolete repository behavior;
- create/update tests and documentation;
- run repository verification and qualification;
- update repository-local plans/status/capability manifests when warranted;
- create/update issues, branches, commits, and pull requests;
- continue to the next independently warranted responsibility.

Protected transitions remain separately governed unless the owner explicitly
grants them and repository policy permits them:

- merge;
- production release/deployment;
- external publication;
- credentials/secrets/security/account changes;
- billing/spending;
- destructive external operations;
- cross-repository scope expansion;
- Level-4 product-thesis revision;
- genuinely preference-sensitive owner choices.

Allow explicit mission-specific authority such as:

```text
MERGE_AUTHORITY = YES
RELEASE_AUTHORITY = NO
DEPLOY_AUTHORITY = NO
```

but never infer those grants from the words "full autonomy" or "full
delegation" alone.

```text
autonomy
!= authority

full repository delegation
!= protected-transition authority
```

Repository policy and explicit owner constraints remain controlling.

## 11. Stop conditions

Continue autonomously until one of these is true:

1. the terminal repository outcome is satisfied and applicable
   repository-answerable qualification supports the completion claim;
2. no further repository/product change is warranted;
3. a genuine owner-reserved or Level-4 decision is required;
4. an unavoidable external/infrastructure dependency blocks all remaining
   warranted responsibilities;
5. the next required action exceeds granted authority.

Do not stop merely because:

- one responsibility completed;
- one PR was opened;
- one verification gate is blocked while independent warranted work remains;
- another internal Sensemaking stage would normally require a new prompt;
- external field validation is intentionally deferred by mission policy.

Do not continue merely because more improvements are imaginable after the
terminal outcome is satisfied.

## 12. Canonical prompt

Use this shape when the owner wants explicit full-autonomy construction:

```text
Run this repository mission with FULL AUTONOMY and FULL REPOSITORY DELEGATION.

TARGET:
[TARGET_SYSTEM_OR_FEATURE]
or AUTONOMOUS_HIGHEST_LEVERAGE_BOTTLENECK

TERMINAL GOAL:
Advance the authoritative product scope until the target capability/system is
construction-complete and satisfies all repository-answerable acceptance and
qualification criteria.

AUTONOMY:
Proceed through repository-answerable decisions and implementation
responsibilities without waiting for further approval. After each consequential
responsibility, reconcile current reality, identify the highest-value remaining
difference to the terminal goal, establish the next warranted responsibility,
and continue automatically.

STRATEGIC SEARCH:
When Level 3 is genuinely open or reopened, run the Strategic Exploration
Funnel: system map -> breadth -> frontier candidates -> proportional depth ->
construction paths -> selection. Generate only materially real alternatives; do
not force an arbitrary count. When strategy is already settled, resume from the
current responsibility/execution/reconciliation boundary instead of rerunning
strategic breadth.

CONSTRUCTION:
Prefer BUILD / REVERSIBLE BUILD when sufficient evidence, authority,
reversibility, and downside make retained construction more useful than
evidence-only work. Complete every decision-relevant vertical layer required by
the capability without manufacturing irrelevant architecture.

FIELD VALIDATION:
External trials, panels, professional asset production, and live telemetry are
deferred until construction completeness unless current authoritative
requirements make them genuine prerequisites. Synthetic personas and
first-principles reasoning may guide construction decisions but are not empirical
evidence.

EVIDENCE:
Implement -> verify -> reconcile -> promote repository status only when the
evidence supports the claim. Do not leave TODOs, placeholders, empty stubs, or
deliberately incomplete happy-path-only behavior where the target requires the
omitted behavior.

AUTHORITY:
Full repository delegation covers ordinary repository-local construction,
repair, refactor, deletion, documentation, tests, qualification, status updates,
issues, branches, commits, and pull requests. Do not infer Level-4 thesis
authority, owner-preference decisions, merge, release/deployment, credentials,
billing, destructive external mutation, or cross-repository expansion unless
separately granted.

STOP ONLY WHEN:
- the terminal repository outcome is satisfied and supported by applicable
  repository-answerable evidence;
- no further repository change is warranted;
- a genuine owner/Level-4 decision is required;
- an unavoidable external blocker prevents all remaining warranted work; or
- the next required action exceeds granted authority.
```

The owner may add narrower constraints or explicit protected-transition grants.

## 13. Anti-patterns

Do not:

- create a new autonomous-mission Skill when the existing continuation Skill can
  compose the work;
- force exactly three strategic alternatives;
- reopen Level 3 after every responsibility;
- expand the mission into every open issue or possible improvement;
- build every conceivable architectural layer in the name of "vertical stack";
- request field validation that the explicit mission has legitimately deferred;
- represent synthetic personas as observed users;
- promote provisional/draft state merely because implementation exists;
- equate repository qualification with external validation or deployment;
- stop after a bounded responsibility when the terminal mission remains open and
  another warranted responsibility exists;
- infer merge/release/deploy authority from broad autonomy wording;
- create a numeric leverage score, permission engine, automatic router, or new
  Campaign schema.
