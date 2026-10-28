# Strategic Sensemaking Loop — Resume & Routing v1

**Status:** canonical reference for `strategic-sensemaking-loop`  
**Scope:** artifact-aware resume and conditional composition  
**Authority:** guidance only; no deterministic routing or semantic state mutation

## Contents

1. Purpose
2. Durable sources to inspect
3. Semantic precedence, not timestamp precedence
4. Resume table
5. Stage-skip rules
6. Execution target typing
7. Owner-decision resume
8. Returned-evidence resume
9. Fresh-start examples
10. Mid-episode examples
11. Final summary is not a source of truth

## 1. Purpose

This reference lets the continuation Skill, composed by `using-sensemaking`, resume a strategic Sensemaking episode
from durable repository state without forcing the user to manually replay every
upstream prompt.

The orchestration rule is:

```text
reconstruct current semantic boundary
-> invoke only the missing/warranted capability
-> preserve existing durable artifacts
-> execute within authority
-> return evidence
-> reconcile
-> stop or continue
```

The routing labels below are reasoning shorthand. They are not a runtime state
machine, planner, score, or persisted master artifact.

## 2. Durable sources to inspect

Use only sources relevant to the current decision.

Common sources include:

```text
current user intent / authority
current repository source identity
STATUS.md / governing strategy / ADRs

artifacts/strategic_repository_analysis.md
artifacts/strategic_reconciliation.md
artifacts/sensemaking_decision.md
artifacts/qualification_execution_evidence.md or equivalent returned evidence
artifacts/owner_decision_capsule.md

Campaign state / execution handoff / worker result
when durable continuation was actually used
```

Not every repository uses every filename. Follow artifact identity and
provenance, not filename guessing.

## 3. Semantic precedence, not timestamp precedence

Determine which artifact governs **the current decision**.

Typical relationships:

```text
strategic_repository_analysis
-> establishes the prior Level-3 model

sensemaking_decision / Campaign responsibility
-> establishes the bounded responsibility selected from that model

execution evidence / worker result
-> establishes what actually happened

strategic_reconciliation
-> interprets returned evidence against the prior Level-3 model

owner_decision_capsule
-> packages an unresolved owner-reserved premise
```

A later artifact can change continuation without mutating the earlier artifact.

```text
SRA-X selected PATH-1
+ SR-Y revises PATH-1
-> SR-Y governs current continuation
-> SRA-X remains immutable provenance
```

Do not use:

```text
newer mtime
-> automatically authoritative
```

Use explicit references, source identity, currentness, and semantic relationship.

## 4. Resume table

| Observed durable state | Current boundary | Normal next capability |
| --- | --- | --- |
| No current Level-3 analysis; repository future materially open | `ANALYZE` | `strategic-repository-analysis` |
| Prior analysis exists but is explicitly reopened / invalidated | `ANALYZE` | `strategic-repository-analysis` |
| Current strategic direction exists; bounded responsibility unresolved | `RESPONSIBILITY` | `using-sensemaking` |
| Owner has explicitly resolved a prior owner capsule | `RESPONSIBILITY` | `using-sensemaking` |
| Bounded responsibility selected, prerequisites + authority established | `EXECUTE` | active agent / existing execution surface |
| Bounded responsibility selected but delegation to another registered Skill is useful | `EXECUTE` | `handoff` then target Skill |
| Consequential returned evidence exists and can affect Level 3 | `RECONCILE` | `strategic-repository-reconciliation` |
| Returned evidence affects only bounded continuation/responsibility | `RESPONSIBILITY` | `using-sensemaking` Learning/Reconciliation path |
| Strategic effect is `OWNER_DECISION` and owner has not selected | `OWNER_DECISION` | `owner-decision-capsule`, then stop |
| Strategic effect is `THESIS_REVIEW_REQUIRED` | `THESIS_REVIEW` | `thesis-review-packet` when durable packet useful, then stop |
| No further warranted action / responsibility complete | `STOP` | none |

The active agent owns this semantic judgment. The table is not executable
routing metadata.

## 5. Stage-skip rules

Do not rerun a Skill merely because it appears earlier in the conceptual loop.

### Skip strategic-repository-analysis when

- a current analysis remains materially valid;
- a reconciliation has not reopened strategy;
- the current question is an already-selected Level-2 responsibility;
- ordinary repository drift does not change the strategic model.

### Skip using-sensemaking as a fresh selection pass when

- a current bounded responsibility is already selected;
- its decision-critical prerequisites remain established;
- execution authority is already clear.

The `using-sensemaking` control laws still govern evidence, warrant, and
authority even when a new standalone decision artifact is unnecessary.

### Skip handoff when

- the same active agent can directly execute the bounded action;
- no context transfer is occurring;
- a Campaign execution handoff is the more appropriate durable delegation
  surface;
- the proposed target is a workflow/tool/action rather than a registered Skill.

### Organization compatibility surface

Organization inspection is not a loop stage and is not part of normal resume
routing. Use it only for explicit topology research/maintenance; ordinary
execution should stay with the active agent, handoff, or Campaign execution
surface as warranted.

### Skip strategic-repository-reconciliation when

- returned evidence cannot materially change prior Level-3 claims, assumptions,
  path continuation, frontier, or strategic effect.

### Skip owner-decision-capsule when

- repository evidence can still resolve the question;
- the owner already made the relevant choice explicitly;
- option-set adequacy is not established.

## 6. Execution target typing

Keep Skill selection and execution-surface selection distinct.

```text
registered Skill
-> may be a handoff target

GitHub Action
workflow
CLI command
active coding agent
external worker
tool
-> execution surface / executor
-> not a Skill identity
```

Never fabricate a Skill name from the label of an execution mechanism.

Examples:

```text
repository-qualification.yml
!= repository-qualification Skill

GitHub CLI
!= github-cli Skill

active coding agent
!= coding-agent Skill automatically
```

If durable cross-actor execution state is useful, prefer the existing Campaign
Execution Interface rather than forcing a prompt-handoff artifact to represent a
non-Skill executor.

Keep Organization topology distinct from both Skill identity and executor identity:

```text
Organization Pattern
-> describes explicit roles / capability requirements / evidence relationships
-> may improve coordination legibility
-> does not instantiate an actor
-> does not select a Skill
-> does not execute work
-> does not grant authority
```

A mechanically valid pattern is evidence about declared topology only.

```text
organization valid
!= organization warranted

role binding
!= actor allocation
```

## 7. Owner-decision resume

When an owner decision capsule exists:

### No owner selection yet

```text
owner_decision_capsule
+ no explicit owner selection
-> STOP
```

Do not infer preference from earlier conversation, repository history, or option
ordering.

### Owner selection supplied now

```text
owner_decision_capsule
+ explicit current owner selection
-> treat selection as new owner intent / authority input
-> using-sensemaking
-> derive bounded responsibility
```

Do not mechanically execute the option statement as though it were already a
Level-2 work package.

## 8. Returned-evidence resume

If execution evidence exists, first establish:

1. exact target/source identity;
2. whether the intended gate/action actually executed;
3. what claim the evidence establishes;
4. what it does **not** establish;
5. whether the effect is execution-level or strategic.

Typical outcomes:

```text
executed bounded responsibility + pass
-> responsibility closure / next responsibility may be decidable

executed gate failure
-> bounded repair may become eligible

pre-execution / zero-step failure
-> repository defect not established

external blocker
-> stop or reconcile depending on strategic consequence

decision-changing evidence
-> strategic-repository-reconciliation
```

## 9. Fresh-start examples

### Repository future is genuinely open

```text
one user prompt
-> strategic-repository-analysis
-> using-sensemaking
-> bounded responsibility
-> execute
-> returned evidence
-> strategic-repository-reconciliation when material
-> stop / continue
```

### Existing strategy, no current responsibility

```text
current SRA
-> using-sensemaking
-> execute
-> reconcile if consequential
```

No strategic reanalysis merely for ceremony.

## 10. Mid-episode examples

### Responsibility already selected

```text
strategic_repository_analysis.md
+ sensemaking_decision.md
-> verify currentness / prerequisites / authority
-> EXECUTE
```

Do not rerun strategic analysis or responsibility selection unless evidence
defeats them.

### Evidence already returned

```text
SRA
+ bounded decision
+ execution evidence
-> RECONCILE
```

Do not dispatch the same execution again just because the loop restarted.

### Owner boundary already reached

```text
strategic_reconciliation
-> OWNER_DECISION
-> owner_decision_capsule exists
-> no owner choice
-> STOP
```

## 11. Final summary is not a source of truth

The continuation Skill may report:

- resume point;
- Skills invoked;
- artifacts consumed/produced;
- execution actions;
- returned evidence;
- final responsibility/strategic state;
- stop reason.

That report is convenience output only.

```text
loop summary
!= master artifact

summary statement
!= stronger than underlying evidence

conversation recap
!= durable repository state
```
