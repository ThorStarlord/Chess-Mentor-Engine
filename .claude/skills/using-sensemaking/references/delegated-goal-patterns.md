# Delegated Goal Patterns

Use this reference when a user delegates a repository-level outcome or terminal
mission rather than naming one narrow implementation task.

These patterns are **delegation contracts**, not routing modes. They clarify the
desired state, authoritative scope, authority boundary, and stopping conditions
while leaving semantic responsibility selection with the active agent.

## Core structure

A broad delegated goal should make these boundaries reconstructible:

```text
GOAL
What outcome should become true?

OPERATING POLICY
How should warranted intermediate responsibilities be selected?

SCOPE DISCIPLINE
Which sources define required work?

AUTHORITY DISCIPLINE
Which decisions/actions are delegated or reserved?

STOP CONDITIONS
What makes the mission legitimately terminal?
```

Keep these non-identities explicit:

```text
high delegation != unlimited scope
desired delegation != granted authority
large mission != one giant Campaign
backlog item != product requirement
candidate direction != current commitment
green validator != semantic closure
```

## Complete authoritative product scope

Use when the owner wants the agent to keep selecting and completing warranted
repository responsibilities until the current product commitments are realized.

When the owner explicitly grants FULL AUTONOMY / FULL DELEGATION across repeated
responsibilities, compose `strategic-sensemaking-loop` for continuation and read
`skills/strategic-sensemaking-loop/references/autonomous-terminal-mission-v1.md`.
That profile adds continuation across bounded responsibilities; it does not create
a second goal model or expand protected-transition authority.

```text
Goal: Build this repository until every feature and capability explicitly
required by the current authoritative product scope is implemented and satisfies
its applicable acceptance and repository-qualification criteria.

Operating policy: Reconstruct current repository reality before assuming
documented work is still missing. Resolve the nearest decision-changing
uncertainty before implementation. Use repo-sensemaker when repository-wide
evidence could materially change the next responsibility. Use durable Campaign
state only when continuation complexity makes transient context unreliable.
After each bounded responsibility, reconcile the resulting capability state and
reassess what, if anything, is warranted next.

Scope discipline: Treat only current authoritative product commitments as
requirements. Do not convert backlog items, historical plans, stale issues,
candidate directions, speculative improvements, or optional future capabilities
into required work unless a current authority has promoted them.

Authority discipline: Exercise repository-answerable intermediate engineering
judgment within the granted scope. Do not silently revise product-thesis
commitments or infer permission to merge, release, deploy, publish, spend money,
change external systems, or perform destructive actions.

Stop conditions: Stop when all authoritative requirements are satisfied or
legitimately dispositioned and no decision-changing gap prevents the completion
claim; when no further repository change is warranted; when progress requires a
reserved owner/product-thesis decision; or when an external blocker prevents
further authorized work.
```

## Next warranted improvement

Use when the owner delegates selection of the next responsibility but has not
defined a terminal product-completion mission.

```text
Goal: Determine and complete the next warranted repository improvement.

Operating policy: Reconstruct current reality, identify the consequential
decision and nearest decision-changing uncertainty, then choose the smallest
responsibility that can improve that decision. Reassess after the bounded work.

Scope discipline: Current repository evidence and authority define the eligible
work; possibility alone does not create a responsibility.

Authority discipline: Select and perform only authorized repository-local work.
Escalate reserved product, external, merge, release, deployment, or publication
decisions.

Stop conditions: Stop after the selected responsibility is qualified and the
next decision is stable, or earlier if no change is warranted or an authority /
external boundary is reached.
```

## Repair to verified closure

Use when a known finding should be repaired autonomously through verification.

```text
Goal: Repair the specified finding and establish whether the original finding
is actually closed.

Operating policy: Reconstruct the finding and its evidence, implement the
smallest warranted repair, validate mechanics, reconcile the work claim, and
perform finding-specific verification.

Scope discipline: Do not broaden from the original finding into unrelated
cleanup unless fresh evidence establishes a separate authorized responsibility.

Stop conditions: Stop when fresh evidence closes the original finding, when the
repair hypothesis is falsified and a new responsibility must be selected, or
when progress requires reserved authority.
```

## Anti-patterns

Avoid prompts or interpretations such as:

- "Do everything in the repo." — no authoritative terminal state.
- "Implement every issue." — issue existence does not establish product scope.
- "Continue until perfect." — unbounded and non-falsifiable.
- "Use a Campaign because this is large." — durability depends on continuation
  complexity, not size alone.
- "You are autonomous, so merge/release when done." — delegation does not imply
  protected-transition authority unless that transition is separately and explicitly granted.
- "Generate exactly three architectures before every responsibility." — strategic
  breadth is conditional on an open/reopened Level-3 decision and should use only
  materially real alternatives.
- "Synthetic personas validated the UX." — synthetic personas can support
  construction reasoning but are not empirical user evidence.
- "Keep improving after requirements are satisfied." — manufactures work instead
  of honoring a legitimate terminal condition.

When a broad mission is underspecified but repository authority can resolve the
scope, inspect that authority first. Ask the owner only for material intent or
authority that the repository cannot establish.
