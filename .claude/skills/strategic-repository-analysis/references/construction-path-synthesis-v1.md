# Construction Path Synthesis v1

**Status:** canonical reference for `strategic-repository-analysis`  
**Scope:** Level-3 path generation and comparison  
**Authority:** semantic guidance; does not select or authorize implementation

## 1. Purpose

A construction path is a coherent repository-evolution trajectory from current
evidence, governing intent, and strategically relevant leverage/opportunity to a
materially different future capability state.

```text
construction path
= future state
+ why plausible from current evidence/intent/leverage
+ Strategic Frontier grounding
+ capabilities built on
+ required capabilities
+ coarse sequence
+ dependencies
+ what becomes possible
+ risks / tradeoffs
+ reversibility
+ evidence gaps
+ decision-relevant assumptions when useful
+ reassessment triggers when useful
```

A path is not a feature list, issue backlog, roadmap commitment, or numeric
option score. A path also does not need to be an already-validated future:
strategic analysis may represent disciplined hypotheses about futures that do
not yet exist.

## 2. Generate paths from repository tensions and opportunities, not categories

Start with the current-system model, capability map, Strategic Frontier, and
governing mission.

Run a **generative pass** before converging on evidence sufficiency. Ask not only
what current deficiency should be repaired, but also what materially different
future becomes plausible because of current capabilities, architectural leverage,
adjacent user/problem pressure, or explicit owner/product intent.

Generate another path only when it represents a materially different answer to
the repository-evolution decision.

Common *shapes* can help the agent notice alternatives:

- deepen the current product around its existing core;
- broaden into an adjacent capability or user problem;
- consolidate/simplify duplicated or overgrown surfaces;
- productize an internal capability that has become strategically central;
- shift an architectural/control boundary to unlock future development;
- exploit current architectural/product leverage to create a new capability;
- deliberately defer construction while resolving a decision-changing premise.

These are search prompts, not required categories. Do not force one path per
shape.

```text
path diversity
!= category coverage

deficiency-driven future
!= only admissible future
```

### 2A. Strategic Hypothesis Admission

Separate the evidentiary job of describing the present from the strategic job
of representing a plausible future.

```text
present-state claim
-> current evidence or explicit owner-intent source

future-state possibility
-> strategic grounding + explicit assumptions

future success claim
-> returned evidence after construction/use
```

A **real strategic path** is coherent with governing intent, compatible with
known repository reality, materially distinct, supported by a plausible
mechanism from current capability/opportunity to future state, explicit about
decision-relevant assumptions, and free of known material contradiction.

A path is **manufactured** when it exists mainly to fill a template/path count,
is materially indistinguishable from another path, contradicts current
repository reality/governing intent, solves no strategically represented
problem/opportunity, or relies on hidden/invented premises.

```text
real strategic path
!= empirically validated future

speculative path
!= manufactured path

ambitious
!= ungrounded

strategic grounding
!= prior validation

absence of evidence for future success
!= evidence that the future is strategically unwarranted
```

Use the existing v2 representation instead of adding a new schema: put the core
strategic hypothesis and plausible mechanism in `why_plausible`; record
material premises as decision/path assumptions; and use reassessment triggers
for observations that would materially strengthen, weaken, or redirect the
path.

### 2B. Apply the Strategicity Gate before path generation

Do not turn every useful repository action into a Level-3 future.

Before a tension or opportunity can generate a construction path, ask whether
resolving or pursuing it could materially change at least one of:

- repository/product future capability state;
- product boundary;
- major architecture/control boundary;
- major dependency structure;
- authority or thesis commitment;
- materially different future development that becomes possible.

If none changes, keep the finding at the appropriate lower control level.

An opportunity does not need evidence that the future capability already
works. It does need a present strategic basis: current capability/leverage,
governing intent, an adjacent user/problem, or another explicit source that
makes the hypothesized mechanism coherent.

```text
repository-relevant work
!= strategic repository evolution

maintenance repair
!= construction path

bounded work can be warranted
without Level-3 BUILD

opportunity not yet built
!= opportunity not strategically representable
```

For new `schema_version: 2` analyses, every Strategic Frontier entry records
evidence references, affected capability identifiers, and a semantic
`strategic_consequence`; every construction path names its `frontier_refs`
and capability identifiers. For opportunity-driven frontiers, evidence grounds
the current basis of the opportunity, not proof of the future outcome.
Mechanical tools validate only the declared relationships.

### 2C. Orthogonality challenge before path-set convergence

A path set can be internally reasonable and still be strategically incomplete
because every path accepts the same downstream framing.

Before convergence, ask:

> Are all candidate paths solving the same framed problem? If so, is that frame
> itself premature, proxy-driven, or downstream of another grounded Strategic
> Frontier?

Examples:

```text
qualify current candidate
vs
collect more evidence about current candidate
```

may omit:

```text
finish a materially incomplete product surface first
```

Likewise, two architecture options may both assume a product boundary that has
not actually been established.

Do not require a third path. Generate an orthogonal path only when governing
intent + current repository reality + a plausible mechanism make it a real
strategic trajectory.

```text
two credible paths
!= option set necessarily complete

orthogonality challenge
!= mandatory third option

shared downstream frame
+ unresolved upstream frontier
-> reopen path generation before comparison
```

If the challenge exposes an upstream product-completion or goal-fit problem,
return to the Strategic Frontier rather than ranking the downstream paths more
carefully.

## 3. Minimum path distinctness

Two paths are materially distinct when choosing one would change at least one of:

- the future product/capability state;
- major dependencies;
- the order in which foundational capabilities must be built;
- the authority or thesis commitment required;
- the main risk accepted;
- what later work becomes possible.

Renaming the same sequence is not a second path.

## 4. Path count

Prefer 2–5 paths when the repository genuinely admits multiple futures.

Use one path when:

- the governing commitment already constrains the future strongly;
- alternative paths are outside current scope;
- alternatives differ only in implementation detail;
- generating more would be performative.

Use zero paths when, **after Strategic Hypothesis Admission**, current
evidence/intent/authority does not support even one coherent real strategic
trajectory, or when the semantic disposition is reached before a construction
choice is meaningful.

Examples include:

- `NO_CHANGE` with no warranted construction or strategically grounded opportunity;
- `OWNER_DECISION` where owner preference defines the future;
- `THESIS_REVIEW` where Level 4 must resolve the product boundary first;
- `INVESTIGATE` where a genuinely gating decision-changing premise must be
  resolved before coherent paths can be formed.

```text
0–5 construction paths
= valid strategic-alternative cardinality

BUILD
-> at least one path
-> selected real path

zero paths
!= missing required ceremony

zero paths
!= default response to unvalidated futures
```

Do not create an artificial “do nothing” path. `NO_CHANGE` and `DEFER` are
strategic dispositions, not filler alternatives.

## 5. Capability-state grounding

Every path must connect to the capability map.

- `ESTABLISHED` capabilities may be foundations.
- `PARTIAL` capabilities may be completed or deliberately left partial.
- `MISSING` capabilities matter only when a path actually requires them.
- `DEFERRED` capabilities need a reason for promotion before becoming path work.
- `BLOCKED` capabilities expose an external/authority/dependency condition.
- `CLAIMED_UNVERIFIED` capabilities cannot be assumed as foundations until the
  claim is resolved when decision-changing.
- `OUT_OF_SCOPE` capabilities cannot silently become path requirements.

A path may require a capability that does not yet exist; that is normal future
construction. The current map must truthfully mark the capability as
`MISSING`/other appropriate current state, while path warrant comes from the
strategic hypothesis rather than pretending the capability is already
established.

```text
missing capability
!= strategic priority

missing capability
!= inadmissible strategic hypothesis

path requires capability
+ path is warranted
!= capability implementation automatically authorized
```

## 6. Coarse construction sequence

The sequence should describe capability-level dependencies, not implementation
tickets.

Good:

```text
make narrative identity explicit
-> expose stable architecture contract
-> add guided beginner flow
-> qualify end-to-end continuity
```

Too low-level:

```text
edit file A
add class B
rename function C
write test D
```

Detailed task decomposition belongs after strategic selection.

## 7. Qualitative comparison

Compare every material path through the canonical Level-3 lenses:

1. mission relevance;
2. decision value;
3. blocking power;
4. evidence sufficiency / resolvability;
5. consequence of error;
6. deferral cost;
7. reversibility;
8. authority availability;
9. dependency.

The legacy v1 tenth lens `smallest_warranted_intervention` remains valid only
for backward compatibility; v2 derives the smallest warranted intervention
after strategic disposition/path selection.

For each lens, explain what matters and why. Do not use numbers, stars, weighted
totals, tiers, or pseudo-quantitative labels as substitutes for reasoning.

```text
strategic comparison
-> disposition/path judgment
-> smallest warranted intervention

small intervention
!= strategically preferable path
```

### Commission / omission symmetry

Do not compare paths only through the downside of acting.

For every material path, explicitly consider:

- **commission risk** — what becomes costly, constraining, misleading, or hard
  to reverse if the path is pursued and its assumptions are wrong?
- **omission risk** — what mission progress, leverage, learning rate, strategic
  optionality, or adjacent opportunity is lost if the path is not pursued?

Express these judgments through the existing lenses, especially consequence of
error, deferral cost, decision value, and reversibility. Do not add numeric
expected-value scoring or a new required schema field.

```text
risk of building wrong
!= only strategic risk

risk of not building
= strategically relevant when omission changes mission progress or optionality
```

### Value creation visibility

For every material path, make the **value created if successful** explicit enough
for a fresh owner/agent to audit the selection. This may include new user/product
capability, reduced friction, leverage unlocked, optionality created, learning
rate improved through normal use, or important constraint/risk removed.

Do not add a numeric value score or required schema field. The goal is to prevent
highly legible safety/qualification work from winning merely because the upside
of construction remained implicit.

```text
path comparison
must expose upside
not only downside

safe-enough path A
vs safe-enough higher-value path B
-> lower risk alone does not select A
```

A comparison may reveal:

- one path is sufficiently warranted;
- a specific uncertainty must be resolved first;
- multiple paths remain viable but the choice is owner preference;
- all paths should be deferred;
- current state is sufficient and no change is warranted;
- the real conflict is Level-4 thesis scope.

## 8. Decision-changing uncertainty

After comparison, ask:

> Which unresolved premise could make the current disposition materially
> different?

Do not list every unknown.

Use Inquiry Policy v0 to decide whether that premise deserves additional
evidence now.

Examples:

```text
repository evidence can resolve it
-> bounded repository inquiry

real-user/runtime behavior is required
-> empirical source, if authorized

the distinction is preference / risk appetite / product commitment
-> owner intent

the fact lives outside repository authority
-> external environment
```

```text
uncertainty identified
!= investigation automatically warranted

residual uncertainty
!= BUILD prohibited
```

When the selected path is bounded, reversible, authorized, sufficiently safe,
and information-producing, construction itself may dominate pre-build inquiry.
Do not demand evidence that the future will succeed when ordinary bounded
construction/use is the cheaper sufficient way to learn.

```text
coherent strategic hypothesis
+ acceptable downside
+ reversible information-producing construction
may warrant BUILD before future success is demonstrated
```

## 9. Strategic synthesis

The synthesis should explain the relationship between evidence, hypotheses, and
disposition, not merely repeat path descriptions.

A good synthesis answers:

- What useful product/capability value would each material path create if successful?
- Which differences between paths are decision-relevant?
- Which present-state claims are well grounded?
- Which future-state assumptions remain hypotheses?
- Which gaps matter enough to change commitment?
- What is the downside of acting and the downside of not acting?
- Why is the selected disposition proportional to current evidence, strategic
  opportunity, reversibility, and authority?
- Why would a materially more aggressive **or more conservative** disposition
  be less warranted?

When the analysis is consumed by an owner-facing orchestration surface, preserve
these conclusions as a compact Decision Trace rather than hiding the alternative
set. The trace should expose material alternatives, their value, and the
selection rationale without manufacturing filler paths or disclosing private
scratch reasoning.

## 9A. Path assumptions and continuation

A path may name the premises it depends on and observable conditions that should
cause its warrant to be reconsidered.

```text
assumption
= premise material to this path judgment

reassessment trigger
= condition that should cause a fresh semantic review

trigger observed
!= automatic path reversal
```

A later strategic analysis may explicitly `REAFFIRM`, `CONTINUE`, `REVISE`,
`SUPERSEDE`, or `CLOSE` the prior analysis/path relationship. Do not convert
this into progress percentages or a roadmap state machine.

## 10. Transition to bounded work

Only `BUILD` selects a candidate repository-level responsibility.

That transition is:

```text
strategic path selected semantically
-> smallest warranted repository responsibility nominated
-> authority checked independently
-> Level 2 / execution only if authorized
```

`BUILD` does not require proof of future success. It requires sufficient
strategic warrant for the bounded next responsibility: coherent grounding,
acceptable downside, appropriate reversibility, explicit material assumptions,
and independent implementation authority.

`INVESTIGATE` nominates a bounded evidence-producing responsibility. Do not
select `INVESTIGATE` merely because success is uncertain when reversible
construction would generate the relevant evidence more cheaply.

`OWNER_DECISION` names the owner decision.

`THESIS_REVIEW` escalates the affected Level-4 commitment.

`DEFER` and `NO_CHANGE` create no implementation task by default.

## 11. Anti-patterns

Do not:

- convert maintenance, currentness repair, or every useful repository action into a strategic path;
- convert every gap into a path;
- admit only deficiency-driven futures while ignoring current leverage/opportunity;
- reject a coherent future merely because it has not already been empirically validated;
- treat speculative/ambitious as synonymous with manufactured/ungrounded;
- use zero paths as a safe default before attempting Strategic Hypothesis Admission;
- ignore omission risk while carefully analyzing commission risk;
- make path names disguise one shared implementation sequence;
- generate a backlog and call it strategy;
- equate more missing capability with higher priority;
- rank paths numerically;
- treat repository facts as owner preferences;
- assume a path recommendation authorizes implementation;
- compare only paths that inherit the same downstream/proxy framing without an orthogonality challenge;
- force a third path when no grounded orthogonal trajectory exists;
- continue decomposing after `OWNER_DECISION` or `THESIS_REVIEW` merely to
  maintain momentum.
