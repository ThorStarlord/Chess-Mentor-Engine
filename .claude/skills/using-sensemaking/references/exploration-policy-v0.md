# Exploration Policy v0 — Agent Contract

**Status:** canonical agent-facing semantic policy  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive control guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic policy; not a search engine, planner, score, enum contract, persistent search tree, or automatic router

## 1. Question

Exploration Policy answers:

> **Given meaningful search history, current evidence, uncertainty, resources, and
> decision context, where should iterative search effort go next?**

It allocates effort *within an already-warranted search process*. It does not decide
whether the repository should have a strategic program, grant authority, rank the
Strategic Frontier, or automatically select a Skill/workflow.

## 2. Activation rule

Keep Exploration Policy implicit for one-shot, obvious, or locally bounded work.

Make it explicit when search has become materially iterative, for example when:

- multiple meaningful attempts already exist;
- a current best direction is being refined against alternatives;
- repeated local failures need attribution;
- the current option/frame set may be too narrow;
- useful mechanisms exist across multiple attempts;
- a promising result needs verification before further optimization;
- the current search region may be a local optimum.

Metareasoning Policy owns the broader control question:

```text
Metareasoning Policy
-> should effort go to ACT / INQUIRE / CHALLENGE / EXPLORE /
   VERIFY / ESCALATE / STOP?

Exploration Policy
-> once iterative search is warranted,
   where should search effort go next?
```

A Metareasoning `EXPLORE` move may start or broaden search. Exploration Policy becomes
most useful once enough search history exists to allocate the next search move.

```text
exploration operator
!= Exploration Policy

search possible
!= iterative search warranted

search history exists
!= persistent SearchState required
```

## 3. Search-state projection

Reason from the smallest explicit search history needed for the current decision.

Useful inputs may include:

```text
DECISION / WARRANT TARGET
CURRENT SEARCH PURPOSE
MATERIAL ATTEMPTS ALREADY MADE
OUTCOMES / EVIDENCE
CURRENT BEST OR PROMISING BRANCHES
ABANDONED / REJECTED BRANCHES + REASONS
FAILURE-ATTRIBUTION HYPOTHESES
FRAME / OPTION-SET STABILITY
UNVERIFIED PROMISING RESULTS
REMAINING SEARCH UNCERTAINTY
CONSEQUENCE + REVERSIBILITY
AUTHORITY / EXTERNAL CONSTRAINTS
REMAINING TIME / COMPUTE / TOOL / EXPERIMENT BUDGET
PROVENANCE / CURRENTNESS WHEN MATERIAL
```

This is a **projection**, not a new truth system.

For small work it may remain transient. When cross-context continuation makes search
history consequential, reuse existing Campaign evidence/transitions, handoff, STATUS,
strategic alternatives, ADRs, repository history, and explicit evidence artifacts.

Do not create `SearchState.json`, a universal search-tree database, or a generic memory
service merely to host this policy.

## 4. Search modes

These are qualitative semantic modes, not a required runtime enum.

### `EXPLOIT`

Refine the current best or most promising direction.

Prefer when:

- one branch has materially stronger evidence/promise;
- remaining uncertainty is local to that branch;
- refinement is cheap enough to clarify its viability;
- broadening the option set is less likely to change the decision.

```text
current best
!= proven best

exploit
!= commit irreversibly
```

### `EXPLORE`

Try a materially different direction or broaden the represented option/frame space.

Prefer when:

- the current option set is narrow or weak;
- only one consequential option is represented;
- local refinement is producing diminishing returns;
- evidence suggests a materially different responsibility/frame may exist;
- an important opportunity is absent from the current search region.

The new direction should be materially distinct, not a cosmetic variant or substep of
an existing branch.

### `CHALLENGE`

Search for falsification, counter-evidence, boundary violations, or failure cases against
a currently favored branch.

Prefer when:

- the current best may be over-trusted;
- consequence of a false positive is high;
- reversibility is low;
- evidence is conflicting;
- a protected external commitment or closure claim depends on the branch being correct.

Challenge output returns evidence. It is not an automatic veto.

### `DIAGNOSE`

Investigate **why** an attempt failed before abandoning, repeating, or broadening it.

Prefer when:

- failure attribution is unclear;
- the failure may be environmental/mechanical rather than conceptual;
- multiple branches fail for a shared hidden reason;
- knowing the cause would change whether to retry, repair, abandon, or reframe.

```text
attempt failed
!= underlying idea falsified
```

### `RECOMBINE`

Combine useful mechanisms, evidence, or constraints from materially different attempts.

Prefer when:

- separate branches each solved different parts of the decision;
- failures are complementary rather than mutually disqualifying;
- a hybrid preserves validated strengths without inheriting the same failure mechanism.

Do not use recombination to create an unbounded “everything plus everything” design.

### `RESTART`

Leave the current local search region or decision frame and reconstruct the search from a
different boundary.

Prefer when:

- repeated attempts share the same failure mechanism;
- the current frame causes circular investigation;
- local improvements no longer change the decision;
- evidence suggests the problem category or responsibility boundary is wrong;
- a local optimum is likely.

```text
restart
!= erase evidence/history
```

Preserve material lessons from the abandoned region.

### `VERIFY`

Spend search effort confirming that a promising result is real before optimizing or
committing further.

Prefer when:

- a branch appears successful but rests on weak/single-source evidence;
- a stochastic/external result may not reproduce;
- finding-specific proof is weaker than generic green validation;
- further optimization would be wasteful if the apparent gain is not real.

Verification remains bounded to the claim needed for the decision.

## 5. Exit disposition

### `EXIT_SEARCH`

Stop allocating effort inside the current search process and return control to
Metareasoning / Warrant / strategic adjudication.

Use when:

- additional alternatives are unlikely to change the decision;
- the current best is sufficiently warranted and appropriately reversible;
- search cost exceeds likely decision improvement;
- authority/time/external constraints dominate;
- remaining branches are materially dominated by current evidence;
- no current branch is warranted and the correct result is no-selection/defer/stop;
- a higher-scope or owner decision is now the real blocker.

`EXIT_SEARCH` is a successful policy result.

```text
exit search
!= global closure

exit search
-> return evidence + material search history
-> semantic reassessment
```

## 6. Qualitative allocation law

Do not score branches or compute an exploration/exploitation ratio.

Ask:

1. What did the latest attempt actually teach us?
2. Is the current best branch promising enough that local refinement could change the decision?
3. Are we missing materially different options?
4. Is failure attribution too weak to justify abandoning/retrying?
5. Does the favored branch need adversarial challenge?
6. Do separate attempts contain complementary validated mechanisms?
7. Are repeated failures evidence that the frame/search region is wrong?
8. Is a promising result verified strongly enough to optimize further?
9. Would another search move improve the decision enough to justify its cost?

Use the smallest search move that is likely to produce decision-relevant information or
materially improve the option set.

## 7. Switching patterns

Useful qualitative transitions include:

```text
promising branch + local uncertainty
-> EXPLOIT

narrow / weak option set
-> EXPLORE

strong commitment + weak falsification
-> CHALLENGE

failed attempt + unclear cause
-> DIAGNOSE

complementary partial successes
-> RECOMBINE

repeated shared failure / unstable frame
-> RESTART

promising result + weak confirmation
-> VERIFY

search no longer decision-improving
-> EXIT_SEARCH
```

These are guidance patterns, not a transition machine.

## 8. Relationship to Strategic Repository Sensemaking

Strategic Repository Sensemaking may create coherent construction paths and qualitative
alternatives at Level 3.

Exploration Policy may help decide where further *analysis/search effort* should go when
those paths remain under active investigation.

It must not:

- convert construction paths into a ranked backlog;
- automatically choose the repository direction;
- treat path generation as implementation authorization;
- replace Strategic Decision to Support;
- silently turn strategic alternatives into execution tasks.

```text
construction path set
!= search tree

Exploration Policy
!= Strategic Frontier ranking
```

## 9. Relationship to other policies

```text
Inquiry Policy
-> what information is worth obtaining, if any?

Metareasoning Policy
-> what kind of control move should consume effort next?

Exploration Policy
-> where should iterative search effort go next?

Warrant / Choice Policy
-> what contemplated responsibility/action/continuation is justified now?

Action / Execution
-> perform selected authorized work

Learning / Reconciliation
-> what explicit state/claim/uncertainty changes after evidence returns?
```

Exploration Policy does not subsume those layers.

## 10. Delegation

A selected search mode may delegate bounded work.

Examples:

```text
EXPLORE
-> ask a worker for one materially different candidate boundary

CHALLENGE
-> ask a critic for counter-evidence against a favored branch

DIAGNOSE
-> ask a bounded investigator to attribute one failure

VERIFY
-> ask a verifier to reproduce one claimed result
```

The parent/active semantic controller retains the decision frame unless semantic
authority was explicitly delegated.

```text
search mode selected
!= worker selected automatically

worker recommendation
!= parent decision

worker success
!= global closure
```

## 11. Persistence rule

Persist only the material subset of search history that a fresh context or another actor
needs to reconstruct a consequential decision.

Useful durable content may include:

- attempt + purpose;
- outcome/evidence;
- failure attribution;
- why a branch was abandoned or retained;
- promising unresolved branch;
- selected next search mode and concise rationale;
- stop/restart condition;
- provenance/currentness.

Do not persist hidden chain-of-thought.

## 12. Anti-patterns

Avoid:

- invoking Exploration Policy for every small task;
- numeric branch scores or exploration/exploitation ratios;
- automatic branch ranking;
- treating every failed attempt as reason to restart;
- repeating nearly identical candidates and calling that exploration;
- preserving every transient branch forever;
- creating a `SearchState` schema merely because the concept has a name;
- building a search-tree service or vector-memory layer without a concrete durable-state gap;
- automatically mapping search modes to Skills/workflows;
- treating `VERIFY` as global closure;
- treating `EXPLOIT` as irreversible commitment;
- treating `EXIT_SEARCH` as repository completion.

## 13. Compact use

When iterative search is real, ask:

```text
What material attempts have already happened?
What did each attempt actually establish?
What is the current best/promise?
What failure attribution is still uncertain?
Is the option/frame set too narrow?
Does the favored branch need challenge?
Are there complementary partial successes?
Are repeated failures pointing outside the current frame?
Is the promising result verified?
Is more search worth its cost?

Choose:
EXPLOIT / EXPLORE / CHALLENGE / DIAGNOSE /
RECOMBINE / RESTART / VERIFY / EXIT_SEARCH
```

For one-shot/local work, keep Exploration Policy implicit.


## Keeping search history

Search history is a decision-relevant projection of existing evidence and
provenance. Keep it transient for small work; reuse existing Campaign,
handoff, STATUS or repository-history surfaces only when continuation makes it
durable. Do not turn the modes into a score or routing table.
