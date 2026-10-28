# Strategic Exploration Funnel v1

**Status:** canonical reference for `strategic-repository-analysis`  
**Scope:** repository-wide breadth exploration before Level-3 convergence  
**Authority:** semantic guidance only; no search engine, score, planner, or new artifact schema

## Contents

1. Purpose
2. When the funnel applies
3. System map
4. Breadth exploration (and the possibility coverage assessment)
5. Frontier candidate synthesis
6. Depth drill
7. Construction path synthesis
8. Comparative selection
9. Owner-visible exploration summary
10. Anti-patterns

## 1. Purpose

Use this reference at a genuine Level-3 `ANALYZE` or `REOPEN_ANALYSIS`
boundary so the agent does not converge on the first visible defect, next issue,
or most mechanically legible verification surface before looking across the
repository/product opportunity landscape.

The funnel is:

```text
FULL REPOSITORY / GOVERNING INTENT
        ↓
SYSTEM MAP
        ↓
BREADTH EXPLORATION
        ↓
POSSIBILITY COVERAGE ASSESSMENT
        ↓
FRONTIER CANDIDATE SYNTHESIS
        ↓
DEPTH DRILL
        ↓
CONSTRUCTION PATH SYNTHESIS
        ↓
COMPARATIVE SELECTION
        ↓
BOUNDED RESPONSIBILITY / DISPOSITION
```

The goal is **coverage before convergence**, not exhaustive inventory.

```text
repository-wide
!= inspect every file

breadth exploration
!= manufacture an opportunity for every system

depth drill
!= deeply analyze every candidate
```

## 2. When the funnel applies

Run the funnel when:

- no current Level-3 analysis materially governs the repository future;
- strategic reconciliation explicitly yields `REOPEN_ANALYSIS`;
- current governing intent or repository reality materially invalidates the prior
  Strategic Frontier/path set.

Do **not** rerun the funnel merely because:

- a selected responsibility is being implemented;
- qualification or verification is pending;
- returned evidence changes only bounded continuation;
- an implementation defect appears inside an already-selected responsibility;
- a protected merge/release boundary is reached;
- the user sends another prompt while Level 3 remains current.

```text
ANALYZE / REOPEN_ANALYSIS
-> funnel eligible

RESPONSIBILITY / EXECUTE / VERIFY / RECONCILE
-> preserve current Level 3 unless evidence genuinely reopens it
```

This prevents breadth search from becoming recurring ceremony.

Through `using-sensemaking`, a repository-level first engagement reaches this
funnel after the Steward's semantic foundation (BOOTSTRAP, ADR 0034). The system
map (section 3) starts from that foundation and does not rebuild it.

### Exploration-only requests

An explicitly **possibility-only** request (for example, "what future Skills could exist?") does not by itself warrant a full Level-3 `ANALYZE` or `REOPEN_ANALYSIS`. The active agent may reuse the system-map and breadth questions here without claiming to have completed the full funnel. If the user wants possibilities rather than selection, stop with a useful, source-scoped opportunity landscape; do not name a selected Strategic Frontier, construction path, next responsibility, or implementation commitment.

If a later decision about what to construct is warranted, apply the existing Level-3 gate and proportionate candidate synthesis, depth and comparison. Prior exploratory ideas remain hypotheses, not automatically admitted frontier candidates; do not reopen an otherwise settled strategic analysis solely because ideas were generated.

## 3. System map

Before converging on a Strategic Frontier, identify the major product/control
systems relevant to governing intent.

A system is a coherent capability/responsibility surface, not a folder or file.

For each major system capture enough of:

- purpose / product contribution;
- current capability state;
- important architecture or control boundary;
- material limitations or unrealized leverage;
- important dependencies / neighboring systems;
- decision-relevant evidence/currentness.

Examples in an agentic software factory might include Goal Intake, Strategic
Frontier, Campaign Lifecycle, Execution, Evidence Return, Strategic
Reassessment, Integration Authority, Post-Merge Observation, and Operator
Interface.

Do not require a fixed taxonomy across repositories.

### System-map sufficiency

The system map is sufficient when it covers enough major product/control
surfaces and relationships that a strategically important opportunity is
unlikely to be omitted merely because another problem was easier to see.

It is not an exhaustive architecture catalog.

## 4. Breadth exploration

Perform a divergent pass **before** frontier convergence.

### Within each important system, ask

- What valuable capability is missing or partial?
- What product promise is not yet fully realized?
- What is unnecessarily expensive, fragile, manual, or awkward?
- What could become more autonomous without violating authority?
- What useful leverage already exists but is underused?
- What could be simplified or made more composable?
- What adjacent capability becomes possible from current leverage?
- What important user/product value is blocked here?

### Across systems, ask

- Where is information or semantic meaning lost?
- Where are owner constraints or authority boundaries lost/blurred?
- Where do two systems duplicate responsibility or state?
- Where does one system produce valuable information another cannot consume?
- Where is a useful capability isolated from the rest of the product?
- What valuable capability emerges if systems A and B are connected?
- Where do current boundaries create avoidable handoff/coordination cost?
- Where does a downstream verification surface crowd out an upstream product gap?

The breadth pass should preserve both:

```text
deficiency discovery
+
opportunity discovery
```

Do not limit breadth to known bugs/issues.

### Grounded and counterfactual divergence

Use these as **optional complementary lenses**, not two mandatory passes:

- **Grounded divergence:** explore materially different capabilities or simplifications under currently accepted product intent, protected constraints and available evidence. A proposed future capability need not already exist to be a legitimate hypothesis; source evidence should ground its present problem, leverage, or intended value.
- **Counterfactual divergence:** deliberately challenge an inherited architectural assumption or imagine a different product/system boundary. State the altered premise, its plausibility and what would have to change. If it conflicts with an accepted commitment or non-goal, label the required owner/Level-4 decision; imagining the option does not authorize implementing it.

Distinguish **governing commitments** (accepted owner intent, non-goals, safety and authority boundaries), **current engineering decisions** (revisable through appropriate authority), **observed implementation facts**, and **uncertainties/hypotheses**. Retrieve decision-relevant sources selectively and retain their scope and currentness. The present architecture is evidence of what exists, not automatically a permanent design constraint. An imagined outcome is not observed behavior or proof of feasibility.

Explore novel user value, combinations and simplifications alongside known deficiencies. Preserve meaningful alternatives without manufacturing a gap for every subsystem.

### Retained possibilities as prior breadth

When the repository retains product possibilities (`poss:` records in
`.sensemaking/knowledge/`, often curated in an Idea Library), recall the ones
relevant to the mapped systems before generating breadth: `knowledge-query
--operation search --term poss:`, then `explain` on relevant possibilities and
their realized capabilities, or read the authored records directly when no
index exists. Read each one's origin, disposition history and `revisit_when`
before reusing it. Then:

- mark each breadth observation as **restated** (cite the `poss:` id),
  **revised** (an existing possibility whose premise, realization or relation
  changed) or **new**;
- keep grounded and counterfactual divergence open: retained records are a
  starting point, not the option set, and an empty result is NOT ASSESSED;
- treat a rejected possibility's rationale as evidence to address, not a veto:
  re-proposing it means naming which premise changed;
- a retained possibility, or a satisfied `revisit_when`, is not a frontier
  candidate until frontier synthesis (section 5) admits it.

### Breadth output

Produce a compact **opportunity landscape** of material observations. It may
contain more items than the final Strategic Frontier.

Do not assign numeric opportunity scores.

Retain only consequential new or revised possibilities, through the
Repository Semantic Steward's RECONCILE and its knowledge contract ("Product
possibility records"): a hypothetical record with its origin and the
relationships it was derived from. Retention is memory, not selection; an
exploration-only request still ends with the landscape.

### Possibility coverage assessment

Before frontier synthesis, and before any repository-wide direction is
selected, judge whether the landscape is broad enough:

- Were the major product systems and intended user outcomes considered?
- Were cross-system and compositional opportunities examined?
- Were retained possibilities and earlier rejected alternatives recalled?
- Were meaningful counterfactuals considered without treating them as
  authorized?
- Is the analysis converging because evidence supports it, or because the
  first visible candidate was easiest?
- Which material areas remain unexamined, and could an excluded direction
  plausibly overturn the emerging preference?

This is a qualitative sufficiency judgment, not a score or candidate quota, and
it never claims every future was explored. If it finds a material gap, return to
breadth (or to the Steward when a system is unmodelled) before converging.
Record the unexamined areas with the result (section 9 and the artifact's
Strategic Frontier section). One isolated defect never justifies a
repository-wide selection by itself.

### From possibilities to construction: conditional order

A useful explanatory order is **ground current reality -> explore possibilities -> examine overlap and capability form where relevant -> challenge material assumptions -> compare strategic paths if selection is warranted -> construct, verify and reconcile only within authority**. This is not a required six-stage workflow, runtime state machine or mandate to construct. An exploration-only request ends with the landscape; sections 5-8 govern later Level-3 convergence when applicable.

## 5. Frontier candidate synthesis

Compress breadth observations into a small set of grounded **frontier
candidates**.

A frontier candidate answers:

> Where might the next highest-value Level-3 repository/product difference be?

It is not yet a construction path.

Several observations may share one deeper candidate.

Example:

```text
present-state grounding loss
+ Goal-constraint propagation loss
-> possible shared frontier candidate:
   semantic continuity across the strategic loop
```

Apply the existing:

- Strategicity Gate;
- Goal Fitness / completion-layer integrity;
- commission/omission symmetry;
- future-hypothesis admission rules;
- value-producing action perspective.

Reject candidates that are merely:

- routine maintenance;
- local repair inside a settled responsibility;
- issue-queue order;
- attractive but non-decision-relevant ideas;
- downstream milestones that hide a more material upstream gap.

### Frontier candidate vs construction path

Preserve this distinction:

```text
frontier candidate
!= construction path

FRONTIER CANDIDATE
= where strategic value/tension may be concentrated

CONSTRUCTION PATH
= coherent future trajectory for changing that frontier
```

Do not collapse them.

## 6. Depth drill

Advance only the strongest/material frontier candidates into deeper analysis.

Depth is warranted when a candidate could plausibly become the selected
Strategic Frontier or materially change the strategic disposition.

For each depth candidate, establish enough of:

- current deficiency/opportunity;
- desired future capability state;
- value created if successful;
- why it is Level-3 material;
- systems/capabilities affected;
- plausible causal mechanism;
- dependencies / prerequisites;
- what current capabilities it builds on;
- material risks/tradeoffs;
- reversibility;
- omission/deferral cost;
- decision-changing evidence gaps;
- authority/thesis implications;
- whether a bounded reversible build can produce value + evidence;
- smallest useful next responsibility if this candidate wins.

Depth analysis should be proportional to decision value.

```text
interesting candidate
!= full depth drill required

material finalist
-> depth drill
```

## 7. Construction path synthesis

Only after a frontier candidate survives enough depth analysis should the agent
synthesize coherent construction paths for that frontier/future.

A depth candidate may support:

- one materially real construction path;
- several distinct construction paths;
- zero paths when even a bounded construction trajectory remains premature.

Example:

```text
Frontier candidate:
grounded strategic reassessment

Construction paths:
A. bounded exact-revision source context
B. structured RepositorySituation projection
C. semantic reference graph
```

Use the existing `construction-path-synthesis-v1.md` rules for path
distinctness, hypothesis admission, orthogonality challenge, comparison, and
anti-backlog discipline.

**Architectural basis (optional).** When paths differ mainly by an architectural
choice with genuine alternatives, and that choice could change the path
comparison, reuse an existing `architectural_synthesis` for it or produce one
through the Steward's architecture-exploration procedure. Cite it with
`architecture_synthesis_refs`, and each path's `architecture_option_refs` and
`possibility_refs`. A synthesis's provisional preference is an input to path
comparison, not a selected path, and an architecture option is not a frontier
candidate. Skip this when the paths do not turn on such a choice.

Breadth does not require generating construction paths for every candidate.

## 8. Comparative selection

Compare the depth-qualified candidates/path sets using the existing qualitative
strategic lenses and Value-Producing Action Preference.

Selection should answer:

- Which frontier currently offers the strongest mission/product leverage?
- What useful value would be created?
- What happens if it is deferred?
- What downside is incurred if the hypothesis is wrong?
- What can be learned through bounded/reversible action?
- What prerequisites or authority constrain action now?
- Why is a materially more conservative move less warranted?
- Why is a materially more aggressive move less warranted?

No numeric score or deterministic winner is allowed.

## 9. Owner-visible exploration summary

When the funnel actually runs, preserve a compact **Strategic Exploration
Summary** for the owner-facing orchestration report.

Do not expose private scratch reasoning or an exhaustive idea dump.

A useful shape is:

```text
STRATEGIC EXPLORATION

Major systems examined:
- <system A>
- <system B>
- ...

Breadth observations:
<compact count / grouped themes, not every trivial idea>

Possibility coverage:
<retained possibilities recalled; counterfactuals considered;
 areas not examined; whether an excluded direction could overturn the result>

Frontier candidates:
A — <candidate>
    Value if pursued:
B — <candidate>
    Value if pursued:
C — <candidate>
    Value if pursued:

Advanced to depth:
A, C

Why those advanced:
<brief decision-relevant reason>

Selected frontier:
A — <candidate>

Selected construction path:
<path or "no path yet">

Selected bounded responsibility / disposition:
<result>
```

This summary is observability, not a new canonical artifact schema.

If only one real frontier candidate exists after breadth exploration, say so.
Do not manufacture finalists.

## 10. Anti-patterns

Do not:

- treat the first visible defect as the Strategic Frontier without sufficient
  breadth exploration;
- select a repository-wide direction without a possibility coverage
  assessment, or hide the areas it left unexamined;
- equate GitHub issue order with strategic priority;
- let CI/qualification visibility crowd out less legible product opportunities;
- map directories/files and call that a system map;
- invent one opportunity per system for symmetry;
- produce dozens of shallow candidates when a few material themes are enough;
- perform deep analysis on every breadth observation;
- turn frontier candidates into backlogs;
- generate construction paths before understanding which frontier matters;
- rerun the full funnel during an already-settled EXECUTE/VERIFY continuation;
- use numeric ranking, search-tree scores, or deterministic routing;
- expose private chain-of-thought instead of a compact decision summary.
