# Goal Fitness & Completion v1

**Status:** canonical reference for `strategic-repository-analysis`  
**Scope:** Level-3 objective/frontier integrity  
**Authority:** semantic guidance; never overrides explicit owner authority

## 1. Purpose

Strategic analysis must obey explicit owner intent **and** diagnose whether the
stated objective is a sound representation of the governing product intent.

This prevents **milestone inversion**:

```text
terminal product intent
-> instrumental milestone
-> verification/evidence surface

must not collapse into

verification/evidence surface
= terminal success
```

The Skill may surface mismatch. It may not silently replace the owner's goal.

## 2. Classify the objective role

When the distinction can change the Strategic Frontier, classify the stated
objective qualitatively as one of:

```text
terminal | milestone | proxy | constraint | evidence_state | unclear
```

- `terminal` — satisfying it directly realizes the governing outcome;
- `milestone` — a bounded intermediate state on the way to the governing outcome;
- `proxy` — an observable representation used to stand in for less directly
  measurable progress;
- `constraint` — a limit or invariant, not the desired end state;
- `evidence_state` — a qualification, validation, audit, or claim state;
- `unclear` — repository/owner evidence does not yet establish the relationship.

Do not infer a hidden “true goal” from vibes. Ground governing intent in explicit
owner direction, authoritative product strategy, current repository authority,
or another identified source.

```text
owner statement
!= permission to invent hidden intent

goal diagnosis
!= owner-goal replacement
```

## 3. Goal-fit test

Ask:

> If the stated objective were fully satisfied, could a material governing
> product objective still remain unsatisfied?

Search for a concrete counterexample in current evidence.

If no material counterexample exists, `GOAL_FIT = aligned` may be warranted.

If the stated objective advances the governing intent but does not establish it,
use `GOAL_FIT = partial`.

If satisfying the stated objective would materially pull work away from or
contradict the governing intent, use `GOAL_FIT = conflicting`.

If the relationship cannot yet be established from current evidence, use
`GOAL_FIT = unresolved`.

These are semantic descriptions, not schema enums or numeric scores.

## 4. Completion-layer sanity check

Use only the layers relevant to the domain. The generic pattern is:

```text
implementation exists
!= integration/reachability complete
!= content/behavior complete
!= intended user/product experience complete
!= release/qualification complete
```

Examples:

- a route may be reachable while its scenes remain materially unfinished;
- an API may exist while the end-to-end user workflow remains incomplete;
- a package may build while its required product behavior is still partial;
- a release candidate may be technically packageable while the intended product
  surface is not content/experience complete.

Do not demand subjective perfection. Establish only whether a decision-relevant
prerequisite state is `ESTABLISHED`, `PARTIAL`, `MISSING`,
`CLAIMED_UNVERIFIED`, or otherwise represented in the existing capability
model.

## 5. Difference-closing frontier

When the governing target state is explicit, prefer a frontier question that
compares current reality to that target instead of merely optimizing a state
label:

```text
What is the highest-value remaining material difference
between the current product/system state
and the authoritative target state?
```

Then:

```text
close one warranted difference
-> reconcile returned evidence
-> reassess the next material difference
-> stop when no further warranted difference remains
```

This is not “keep improving forever.” The target state, evidence ceilings,
authority, and stop conditions remain bounded by governing intent.

## 6. Legibility bias

Mechanically legible work can dominate agent attention even when it is not the
highest-value frontier.

Examples include:

- CI checks;
- exact SHAs;
- validators;
- package/release metadata;
- test counts;
- deployment state.

Less mechanically legible product work may include:

- content completeness;
- experiential continuity;
- narrative/presentation finality;
- workflow usability;
- qualitative fit to an explicit product promise.

```text
easy to verify
!= strategically important

harder to inspect semantically
!= safe to ignore
```

Do not lower evidence standards. Ensure the Strategic Frontier represents the
governing mission rather than merely the most machine-legible evidence surface.

## 7. Goal-fit warning

When material mismatch exists, surface it explicitly:

```text
GOAL_FIT_WARNING

stated objective:
<explicit owner objective>

objective role:
<milestone/proxy/etc.>

governing intent:
<grounded product intent>

counterexample:
<how the stated objective could be satisfied while governing intent remains unmet>

optimization risk:
<what work the milestone may preferentially attract>

frontier consequence:
<what strategic question must be represented before converging>
```

This warning is semantic guidance. It does not require a new artifact schema.

## 8. Handoff to path synthesis

After goal fitness and completion layers are established:

1. form the Strategic Frontier from the governing mission;
2. run Strategic Hypothesis Admission;
3. generate coherent paths;
4. run the orthogonality challenge in
   `construction-path-synthesis-v1.md`;
5. compare only the materially real path set.

A downstream milestone may remain a valid path. It simply may not monopolize the
decision space when an upstream product-completion frontier remains materially
unresolved.

## 9. Anti-patterns

Do not:

- treat an owner-supplied milestone as automatically terminal;
- infer a hidden owner goal without evidence;
- equate route/build/package/test completion with product completion;
- prefer qualification merely because its evidence is more legible;
- reopen a settled terminal objective merely because a proxy is imperfect;
- manufacture an orthogonal path solely to create option diversity;
- create a new completion schema when the existing capability/frontier model is sufficient.
