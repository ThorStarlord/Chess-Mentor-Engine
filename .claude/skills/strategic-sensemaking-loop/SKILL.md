---
name: strategic-sensemaking-loop
description: internal long-horizon continuation for the using-sensemaking controller. Resume strategic repository Sensemaking from one prompt across sessions, including FULL AUTONOMY / FULL DELEGATION terminal missions and AUTONOMOUS_HIGHEST_LEVERAGE_BOTTLENECK requests. Use when a reasoning or construction mission must continue across sessions or bounded responsibilities, or when a maintainer explicitly resumes one; ordinary users start with using-sensemaking. Reconstruct durable state, identify unfinished reasoning objectives, apply only warranted stages, continue within authority, reconcile returned evidence, and stop when the delegated outcome is complete or at a genuine terminal, owner, Level-4, external, or authority boundary.
---

# Strategic Sensemaking Loop

Provide **long-horizon continuation** for strategic repository Sensemaking
under the `using-sensemaking` controller (ADR 0034), while preserving the
specialized Skills as separate semantic responsibilities.

`using-sensemaking` is the public entrypoint and keeps responsibility-selection
judgment. This Skill reconstructs earlier episodes, identifies unfinished
reasoning objectives, resumes after a specialist returns, keeps authority and
continuity across sessions, and judges when the delegated outcome is complete.
It does not compete for public entry, redefine responsibility selection,
replace the component Skills, create a new strategic policy, or introduce a
second truth system. A delegated reasoning mission can complete without any
execution.

## Responsibility

From the user's current goal, repository state, authority, and existing durable
artifacts:

1. reconstruct where the current Sensemaking episode actually is;
2. invoke only the specialized Skill(s) needed from that point;
3. execute or delegate an already-warranted responsibility when authority permits;
4. return consequential evidence through reconciliation;
5. continue autonomously through repository-answerable steps;
6. stop only at a justified terminal, blocked, reserved, or higher-level boundary.

The normal specialized surfaces are:

```text
strategic-repository-analysis
using-sensemaking
handoff
strategic-repository-reconciliation
owner-decision-capsule
```

Adjacent reserved boundaries such as `thesis-review-packet` remain available
when the existing control model warrants them.

## Core laws

```text
continuation surface != second semantic controller
orchestration != deterministic planning
resume marker != durable state
existing artifact != unquestionable truth
stage completed != stage must rerun
returned evidence != strategy automatically changed
owner decision packet != owner decision made
responsibility selected != implementation authorized
handoff useful != handoff mandatory
Campaign available != Campaign required
value-producing warranted action != lowest-risk action automatically
blocked responsibility != repository-wide freeze automatically
high delegation != protected-transition authority
responsibility completed != mission completed
mission incomplete != execute backlog blindly
full repository delegation != protected-transition authority
synthetic persona != empirical user evidence
implementation exists != canonical promotion warranted
```

Do **not** create a new master strategic artifact or orchestration state file.
Durable truth remains in the existing strategic, responsibility, execution,
reconciliation, owner-decision, Campaign, and repository artifacts.

Read `references/resume-and-routing-v1.md` whenever existing artifacts mean the
episode may need to resume in the middle rather than start from strategic
analysis.

Read `references/value-action-and-delegation-v1.md` when the action mode,
delegation envelope, blocked-gate continuation, or owner-visible decision trace
is material.

Read `references/autonomous-terminal-mission-v1.md` when the user grants FULL
AUTONOMY / FULL DELEGATION for a terminal repository outcome, uses
`AUTONOMOUS_HIGHEST_LEVERAGE_BOTTLENECK`, or otherwise expects the loop to
continue across multiple bounded responsibilities until the mission is complete
or a genuine stop boundary is reached.

## 1. Reconstruct the current episode before invoking another Skill

Inspect the smallest sufficient set of current sources:

- the user's current request and explicit authority;
- current repository/source identity and decision-relevant governing docs;
- relevant target `.sensemaking/` intent, non-goals, invariants, and
  decisions **when present**, verifying decision-changing claims at source;
- `artifacts/strategic_repository_analysis.md` when present;
- `artifacts/strategic_reconciliation.md` when present;
- current responsibility/decision artifacts such as
  `artifacts/sensemaking_decision.md` when present;
- handoff / execution evidence or Campaign execution receipts when present;
- `artifacts/owner_decision_capsule.md` when present;
- explicit owner choice supplied after a decision capsule.

Determine the **latest semantically valid boundary**, not merely the newest file
timestamp.

Do not rerun an earlier stage merely because it is part of the canonical loop.

## 2. Select the current control boundary

Use these semantic resume states only as reasoning labels; do not persist them as
a new runtime state machine. They locate where a resumed episode stands; which
responsibility is warranted inside that boundary is still the controller's
judgment (`using-sensemaking` sections 4-5), and an episode with no adequate
semantic foundation resumes at the controller's ontology-first entry:

```text
ANALYZE
RESPONSIBILITY
EXECUTE
RECONCILE
OWNER_DECISION
THESIS_REVIEW
STOP
```

### ANALYZE

Use `strategic-repository-analysis` when:

- no current Level-3 strategic analysis exists and repository future is materially open;
- an existing reconciliation explicitly warrants `REOPEN_ANALYSIS`;
- current governing intent/source reality materially invalidates the prior analysis.

When this boundary is genuinely active, allow `strategic-repository-analysis`
to run its **Strategic Exploration Funnel**:

```text
system map
-> breadth exploration
-> frontier candidates
-> depth drill
-> construction paths
-> selection
```

Do not reopen strategy for ordinary drift, currentness noise, or because another
idea is imaginable. Do not run the breadth/depth funnel during
`RESPONSIBILITY / EXECUTE / VERIFY / RECONCILE` merely because the loop
continued.

### RESPONSIBILITY

Use `using-sensemaking` when:

- strategic direction is current but the next bounded responsibility is not;
- an owner selection has resolved a reserved premise and now needs translation
  into a bounded responsibility;
- returned non-strategic evidence changes continuation/responsibility without
  requiring Level-3 reopening.

Treat upstream recommendations as defeasible. Preserve the
inherited-responsibility prerequisite backstop in `using-sensemaking`.

When several responses are sufficiently warranted and authorized, apply the
**Value-Producing Action Preference**: prefer useful retained product/capability
value plus sufficient evidence over a lower-value evidence-only move when total
cost/downside is not materially worse. Do not turn this into numeric scoring.

### EXECUTE

When a bounded responsibility is selected:

1. verify decision-critical prerequisites;
2. verify exact authority for the contemplated action;
3. choose the warranted action shape and lightest execution boundary.

For **real software construction**, use the **portable Architect -> Builder ->
Reconcile contract** in `using-sensemaking` and its bundled
`references/portable-construction-loop-v1.md`. The active agent performs
the bounded edit, reviews real consumers and checks under the **target
repository's** policies, then returns evidence here for multi-increment
continuation. This Skill owns the outer mission/resume boundary, **not** a
duplicate build procedure. Neither the portable inner loop nor this outer
loop requires a target `CLAUDE.md`, `AGENTS.md`, product strategy,
`STATUS.md`, Grounding Pack, or Sensemaking CLI. If those sources exist,
read only their decision-relevant content; missing scaffolding is not a
reason to invent goals or block a warranted local fix.

Descriptive action shapes include:

```text
BUILD
REVERSIBLE BUILD
VERIFY / QUALIFY
PROBE / INQUIRE
SPIKE / PROTOTYPE
EXPERIMENT
STOP / ESCALATE
```

These labels describe the current move; they are not a new runtime enum or
artifact schema. A strategically selected `BUILD` may be executed as a
reversible build when the bounded implementation is useful if retained and
normal use produces sufficient evidence.

```text
same active agent + clear bounded action
-> execute directly

cross-actor / copy-paste Skill transition useful
-> handoff

durable multi-context delegation useful
-> Campaign execution handoff

protected / owner-reserved action
-> stop or escalate
```

The legacy Organization tracer is not part of the normal strategic loop or
default execution surface. Treat it as an advanced/research inspection aid only
when a user explicitly asks to study role/capability topology or when maintaining
that compatibility surface. Do not introduce it merely to structure ordinary
delegation.

Use `handoff` only when a prompt handoff to a **registered Skill** is actually
the correct next boundary. Do not invent a Skill identity for a workflow,
GitHub Action, tool, active coding agent, or other non-Skill executor. For those
cases use direct execution or the existing Campaign/executor interface.

Execution is not itself another semantic Skill requirement.

### RECONCILE

After consequential evidence returns:

- apply the Learning / Reconciliation guidance from `using-sensemaking`;
- use `strategic-repository-reconciliation` when the evidence can materially
  affect prior strategic claims, assumptions, path continuation, frontier, or
  strategic effect;
- do not invoke strategic reconciliation for trivial execution details that
  cannot change Level 3.

Follow the resulting strategic effect:

```text
NO_MODEL_CHANGE / REAFFIRM
-> continue or stop according to responsibility state

REVISE_STRATEGY
-> use the reconciled state as current Level-3 input

REOPEN_ANALYSIS
-> return to ANALYZE

OWNER_DECISION
-> OWNER_DECISION

THESIS_REVIEW_REQUIRED
-> THESIS_REVIEW
```

### OWNER_DECISION

Use `owner-decision-capsule` only when repository evidence cannot resolve the
decisive premise because it is genuinely owner-reserved.

After producing an adequate capsule, **stop for the owner**. Never synthesize or
guess the owner's selection.

If the user has already explicitly selected an option in the current request,
do not recreate the capsule merely because one exists. Treat the explicit owner
selection as new intent/authority input and return to RESPONSIBILITY.

If the capsule reports `OPTION_SET_INCOMPLETE`, return upstream to the
Strategic Frontier/path-synthesis boundary rather than forcing a choice.

### THESIS_REVIEW

When `THESIS_REVIEW_REQUIRED` is established, use the existing
`thesis-review-packet` when a durable Level-4 review packet is warranted, then
stop for the required owner/Level-4 authority. Do not silently revise the product
thesis.

### STOP

Stop when any of these is true:

- the current responsibility is verified complete and no further warranted
  responsibility exists;
- no repository/product change is warranted;
- a genuine owner-reserved decision is waiting;
- a Level-4 thesis decision is waiting;
- an external/infrastructure blocker cannot be resolved within current authority
  **and no independently warranted repository responsibility can proceed without
  bypassing or depending on the blocked gate**;
- the next action requires authority not granted by the current user/repository;
- no further decision-changing evidence or action is warranted.

## 3. Continue autonomously without prompt-by-prompt ceremony

When the user has delegated ordinary repository-answerable continuation, do not
pause between internal stages merely to request another prompt.

A healthy episode may look like:

```text
current repository
-> strategic-repository-analysis
-> using-sensemaking
-> direct bounded execution
-> returned evidence
-> strategic-repository-reconciliation
-> STOP
```

or:

```text
existing strategic_repository_analysis
+ existing sensemaking_decision
-> EXECUTE
-> returned evidence
-> strategic-repository-reconciliation
-> owner-decision-capsule
-> STOP FOR OWNER
```

or:

```text
owner explicitly selects prior capsule option
-> using-sensemaking
-> bounded responsibility
-> execute
-> reconcile
-> continue / stop
```

The correct sequence is whatever the current evidence/authority warrants, not a
mandatory five-stage pipeline.

### Full-autonomy terminal missions

When the owner delegates a terminal mission under FULL AUTONOMY / FULL
DELEGATION, read `references/autonomous-terminal-mission-v1.md`. Continue
across bounded responsibilities until the terminal goal is satisfied or a
genuine stop boundary is reached:

```text
responsibility -> execute -> verify -> reconcile
-> remaining difference -> next warranted responsibility -> continue
```

Do not stop merely because one responsibility completed. Do not force exactly
three strategic alternatives or rerun breadth after every responsibility. When
Level 3 is settled, do not execute backlog items blindly, manufacture irrelevant
vertical layers, or treat synthetic personas as empirical evidence.

After consequential work, use the resulting code, tests, user interaction, and
owner decisions to update the **affected** target-repository grounding facts
only if they are non-derivable and useful for a future decision. Record them in
the same work change when a pack exists; never block continuation to produce
a complete ontology or a redundant mission ledger. Distinguish the next
user-relevant improvement from the next available issue.

## 4. Artifact-aware resume rules

Preserve provenance across stages.

Prefer an existing current artifact over recreating an equivalent one. If the
artifact is stale or contradicted, reconcile or reopen through the normal
control path instead of silently overwriting it.

Never use conversation memory as the sole basis for a consequential resume when
durable repository artifacts are available.

Do not treat file recency as semantic precedence:

```text
newer timestamp
!= newer decision

strategic reconciliation referencing SRA-X
+ returned evidence
-> may supersede continuation assumptions from SRA-X
without mutating SRA-X
```

See `references/resume-and-routing-v1.md` for the detailed resume table.

## 5. Authority and execution boundaries

At every downward transition preserve:

```text
KNOW
DECIDE
ACT
PUBLISH / MERGE / RELEASE
```

as separable authority surfaces.

A user's instruction to proceed autonomously authorizes repository-answerable
steps only to the extent of the user's actual scope and repository policy.

When the owner explicitly says to proceed without further input, continue
autonomously through ordinary repository-answerable work under the
**high-delegation repository envelope** in
`references/value-action-and-delegation-v1.md`. This may include bounded
construction, reversible builds, repair/refactor/docs, repository qualification,
warranted probes/experiments, issue/branch/commit/draft-PR work, evidence
reconciliation, and continuation to the next independently warranted repository
responsibility.

It does not silently grant protected publication, merge, deployment, release,
credential, billing, Level-4 thesis choice, preference-sensitive owner decision,
cross-repository expansion, or unrelated external mutation authority. Repository
policy and explicit owner constraints remain controlling.

A terminal mission may separately grant a protected transition such as merge
authority when the owner says so explicitly and repository policy permits it.
Do not infer that grant from the words "full autonomy" or "full delegation".

No component artifact grants authority merely by existing.

## 6. Final report

Do not create a new canonical orchestration artifact.

At the end of the run, report:

1. resume point reconstructed;
2. specialized Skills actually invoked;
3. artifacts consumed;
4. artifacts produced or updated by those Skills;
5. non-Skill execution surfaces/actions used;
6. returned evidence obtained;
7. final strategic state/disposition;
8. final bounded responsibility state;
9. authority boundary reached;
10. exact stop reason and next owner input only when one is genuinely required;
11. when a terminal mission is active, whether the terminal outcome is satisfied
    and the highest-value remaining difference, if any.

For consequential Level-3 selections or materially contested control moves, also
surface a compact **Decision Trace**:

- material alternatives actually considered;
- value each would create if successful;
- selected control/action shape;
- why the selected move is warranted now;
- why a materially more conservative move was less warranted;
- why a materially more aggressive move was less warranted.

When the current run actually invoked `strategic-repository-analysis` at
`ANALYZE / REOPEN_ANALYSIS`, precede the Decision Trace with a compact
**Strategic Exploration Summary** showing:

- major systems examined;
- breadth opportunity themes/observations;
- frontier candidates synthesized;
- which candidates advanced to depth and why;
- selected Strategic Frontier;
- selected construction path, if one exists.

Do not dump every idea or expose private scratch reasoning. This summary exists
to make repository-wide breadth -> depth -> selection visible to the owner.

Do not expose private scratch reasoning or manufacture alternatives merely to fill
the display. This trace is user-facing observability, not a new canonical
artifact.

A concise session summary may be emitted for the user, but it is not a new source
of truth and must not compete with the underlying artifacts.

When an ordinary-use episode exposes consequential evidence about breadth,
frontier-candidate compression, proportional depth, semantic resume, action-mode
selection, or Goal Fitness, preserve that evidence using
`docs/normal-use/strategic-sensemaking-observation-guide.md` **only when the
episode already qualifies for normal-use capture**. Do not delay work, create a
synthetic episode, or make observation capture a mandatory loop stage.

```text
normal-use observation
!= loop stage

one awkward episode
!= strategy must reopen
```

## Non-goals

Do not introduce:

- a StrategicPlanner or deterministic semantic router;
- a mandatory five-Skill sequence;
- a new Campaign schema;
- a new strategic/master artifact;
- automatic repository discovery or scope expansion;
- a mandatory Organization stage or Organization Pattern for every execution;
- automatic role allocation, dynamic Organization generation, or Skill routing;
- automatic owner decisions;
- automatic Level-4 thesis revision;
- automatic merge/release/publication authority;
- numeric path/resume/priority/expected-value scoring;
- mandatory reversible builds, prototypes, experiments, or qualification;
- a permission engine derived from delegation labels;
- repeated analysis merely for ceremony;
- mandatory repository-wide breadth exploration during settled execution or verification;
- forced exactly-three-path strategic search;
- automatic backlog execution under a terminal mission;
- mandatory API/service/event/persistence/operator layers when the capability does not need them;
- synthetic-persona evidence represented as empirical user validation;
- automatic canonical/status promotion before applicable verification and reconciliation;
- automatic protected merge/release/deploy authority from autonomy wording;
- a persisted search tree, frontier score, or deterministic breadth/depth router.
