# Experiment Economy & Proportional Rigor v1

**Status:** canonical agent-facing semantic guidance  
**Parent policies:** Inquiry Policy v0 + Metareasoning Policy v0  
**Authority:** guidance for evidence acquisition; does not authorize action or experimentation  
**Runtime status:** semantic guidance; not an engine, scorer, router, or experiment framework

## Contents

1. Purpose
2. Experiment Warrant Gate
3. Evidence-source economy
4. Reversible construction as evidence
5. Total experiment cost
6. Minimum Sufficient Experimental Rigor
7. Confounder Warrant
8. Evidence mode and claim ceiling
9. Inquiry vocabulary
10. Stop conditions
11. Examples
12. Anti-patterns
13. Boundaries

## 1. Purpose

Use this reference when experimentation is materially considered.

The governing objective is:

> Use the lowest-cost evidence strong enough for the decision and claim actually being made.

```text
uncertainty
!= experiment

inquiry
!= experiment

experiment
!= controlled experiment

cleaner evidence
!= more valuable evidence

research-grade evidence
!= default product-development evidence
```

Do not optimize evidence purity independently of decision value.

## Responsibility boundary

Experiment Economy owns the decision **whether experimentation is warranted**. Domain
and diagnostic Skills may surface an empirical uncertainty, missing evidence, and
candidate evidence source, but they must not manufacture an experimentation
responsibility merely because they know how to test something.

```text
diagnostic uncertainty
!= experiment warrant

missing evidence
!= experimentation responsibility

experiment-design
= downstream of experiment warrant
```

Once experiment warrant exists, `experiment-design` owns efficient experiment design:
decision discrimination, total cost, minimum sufficient rigor, necessary controls, stop
conditions, and claim ceiling. It does not re-decide its own activation.

## 2. Experiment Warrant Gate

Before selecting an experiment, answer:

1. What exact decision is unresolved?
2. What uncertainty could materially change that decision?
3. Is current evidence already sufficient?
4. Can authoritative existing evidence answer it?
5. Can repository/environment inspection answer it?
6. Can verification of an existing claim answer it?
7. Is the missing premise owner intent or an external source rather than an empirical question?
8. Would a tiny probe answer it?
9. Would cheap reversible construction answer it while also producing product value?
10. What plausible experiment outcomes would cause materially different decisions?
11. Is that decision improvement worth total experiment cost and delay?

If plausible outcomes would not change what becomes warranted, do not experiment.

```text
experiment possible
!= experiment warranted

better evidence possible
!= better evidence worth obtaining

no material decision discrimination
-> no experiment
```

## 3. Evidence-source economy

Choose the cheapest sufficient source. A useful non-mandatory ladder is:

```text
EXISTING EVIDENCE
-> READ authoritative source
-> INSPECT current state
-> VERIFY existing claim
-> PROBE one bounded uncertainty
-> REVERSIBLE BUILD / NORMAL USE
-> SPIKE
-> SMALL EXPERIMENT
-> CONTROLLED EXPERIMENT
-> RESEARCH-GRADE ISOLATION
```

Do not mechanically traverse every rung. Start at the cheapest source capable of
answering the decision-changing question.

```text
stronger evidence available
!= stronger evidence required
```

## 4. Reversible construction as evidence

A bounded implementation may dominate separate inquiry when it is:

- cheap to implement;
- cheap to remove, simplify, or revise;
- within authority;
- sufficiently safe for normal use;
- capable of producing the needed evidence.

```text
cheap reversible construction
can be the cheapest sufficient inquiry

build-as-inquiry
!= permission for irreversible architecture commitment
```

Compare the full cost of "experiment then maybe build" with "build minimally, use,
observe, retain/revise/remove."

### Reversible-build dominance

Prefer a reversible build over a separate experiment followed by later duplicate
implementation when all are true:

- the capability/action is already sufficiently warranted;
- retaining it would create useful product/capability value if it works;
- it is cheap enough to revise, simplify, or remove;
- ordinary use or normal verification can produce evidence sufficient for the
  current decision;
- total build/use/revise cost is no greater than experiment overhead plus later
  implementation;
- downside and maintenance burden are acceptable;
- the intended claim does not require stronger causal/comparative isolation.

```text
retained useful value
+ sufficient normal-use evidence
+ acceptable downside
+ no greater total cost
-> REVERSIBLE BUILD normally dominates separate experiment + duplicate build

reversible build available
!= reversible build automatically warranted
```

Prefer READ/INSPECT/VERIFY when they answer the question materially cheaper.
Prefer an experiment when the decision genuinely requires evidence the build
cannot provide without compromising the inference.

### Experience-first discovery and invariant-bounded assurance

For a creative, visual, or interactive product, the primary uncertainty may be
**experiential value**, not whether a selected implementation satisfies its
mechanical contract. Match the evidence source to the decision:

| Decision | Appropriate evidence | Not established by that evidence |
| --- | --- | --- |
| Can someone inspect the concept? | Compile/start/route smoke checks and a bootable isolated preview | Ergonomic value or reliability in everyday use |
| Is the interaction understandable/useful? | Genuine interaction and observations in the actual UI | Security, all edge cases, or population-wide preference |
| Should this owner's development direction change? | Their firsthand experience and reversible preference decision | General user preference or broad release readiness |
| May real work rely on this as a default? | Targeted save/reopen/recovery, authority, accessibility, and relevant reliability verification | Long-term field value or universal desirability |

For a disposable visual-canvas spike, make a runnable preview available early,
use disposable sample content, perform only the smoke checks needed to make it
inspectable, and seek direct use or feedback before cementing layout details.
Do not write mock-driven UI regression suites for unchosen layouts merely to
make them look qualified. If no real browser or user is reachable, state that
the ergonomic question remains unobserved; mocked DOM behavior or an agent's
judgment is not substitute evidence of human preference.

Keep stable **trust invariants** separate from volatile **design hypotheses**.
For example, selecting between canvas and split-view navigation can remain
fluid while no-silent-canon-change, no-text-loss, and save/reopen/recovery
behavior continue to require appropriate protection if touched. Showing an
isolated disposable preview and enabling routine authoring with real content
are different decisions with different evidence needs.

Minimize **epistemic latency**: time from identifying a product uncertainty
to receiving evidence that could change the product decision. Revisit or
discard the design promptly when observation defeats the hypothesis; add
durable regression tests for behavior worth preserving as stabilization
becomes warranted. Direct human feedback can be high-fidelity for ergonomics
but does not replace testing race conditions, subtle data loss, or security.

This is a contextual application of existing `SPIKE`, `REVERSIBLE BUILD`,
authority, and proportional verification guidance. It creates no formal
spike exemption, workflow phase gate, binary rigor mode, automatic evaluator,
or general waiver of safety or publication requirements.

## 5. Total experiment cost

Do not call an experiment cheap merely because the experimental code is small.

Consider:

```text
TOTAL EXPERIMENT COST =
  design
+ setup
+ implementation
+ isolation / environment preparation
+ execution
+ evaluator effort
+ interpretation
+ documentation / evidence packaging
+ delay
+ opportunity cost
```

Use qualitative judgment; do not create a numeric expected-value score.

### Executability first: prevent harness inversion

Before constructing a separate evaluator, fixture, benchmark, or runner,
identify the **near-term engineering decision** it could change. Confirm that
its decisive observation is executable in the available environment *before*
building supporting infrastructure. If the required coding-agent sessions
cannot run, an elaborate harness will not answer whether a Skill changes agent
behavior; report that observation as **NOT RUN**. Do not substitute successful
fixture tests for an agent-behavior result.

For a small, reversible prompt/Skill change, inspection of the diff may be
enough to decide on a proposed change. When a behavioral smoke test is useful,
try one or a few representative scenarios with direct old/new agent runs;
prefer an authentic engineering issue when available. Inspect whether the
agent acted on grounded, authorized work, invented work, escalated needlessly,
or respected a genuine boundary. A few runs provide directional evidence,
not reliable causal attribution, broad productivity proof, or release safety.

The PR #535 LedgerNote episode illustrates the failure: fictional matched
repositories, an answer key, and a randomized trial runner were built, but
the intended independent coding-agent comparison could not execute in the
workspace. The fixtures were mechanically checked; **the revised Skill's
behavioral improvement was not observed**. Do not count this as independent
normal-use or Trial 002 evidence.

A large harness is not wrong merely because it exceeds the payload's size.
Stronger isolation or automation can be justified by consequential safety
risks, repeated use, expensive irreversible decisions, or a genuinely
comparative/causal claim. Do not waive focused regression, data-integrity,
security, or authority checks merely to avoid test overhead. The failure is
support-work displacement without proportionate decision value.

## 6. Minimum Sufficient Experimental Rigor

If an experiment passes the Experiment Warrant Gate, use the minimum rigor sufficient
for the current decision and claim.

Rigor should scale qualitatively with:

- consequence of a wrong decision;
- reversibility;
- implementation cost;
- total experiment cost;
- importance of causal attribution;
- durability/publicity of the claim;
- likelihood that an uncontrolled factor could reverse the inference.

```text
maximum rigor
!= correct rigor

minimum sufficient rigor
= enough control for the decision and claim
```

Do not add fresh agents, isolated worktrees, control groups, blind evaluation, or
special evidence packages merely because they would make the evidence cleaner.

## 7. Confounder Warrant

Before paying to control a possible confounder, ask:

> What decision-relevant inference would become unreliable if this factor were not controlled?

Control it only when the answer is material.

```text
possible confounder
!= required control

possible contamination
!= experiment invalid

control cost
requires decision-relevant warrant
```

Coding-agent influence is not contamination by default. When the product is intended
to operate through a coding agent, ordinary agent competence, normal repository
context, and normal tool use are often part of the operating environment being
evaluated.

Prior exposure to the exact answer or target state may still be a material confounder
for a fresh-reconstruction claim. Judge the specific inference, not the abstract
possibility of contamination.

## 8. Evidence mode and claim ceiling

Distinguish the claim being supported.

### Normal-use product evidence

Question:

> Is this useful enough in the intended coding-agent workflow to retain, revise, or remove?

Normal agent/repository context is usually part of the system. Strong causal isolation
is normally unnecessary.

### Bounded diagnostic evidence

Question:

> Is a particular factor likely responsible for the observed behavior?

Control only factors capable of invalidating the diagnostic inference.

### Causal / research-grade evidence

Question:

> Can an effect be attributed specifically to one capability independently of the base agent or other factors?

Fresh contexts, controls, blinded evaluation, or stronger isolation may be warranted
when the causal/comparative claim materially requires them.

```text
product usefulness claim
!= causal attribution claim

normal operating context
!= methodological defect
```

## 9. Inquiry vocabulary

These labels are descriptive guidance, not runtime enums:

- **READ** — consult existing authoritative evidence.
- **INSPECT** — measure current repository/environment state.
- **VERIFY** — test an existing claim or result.
- **PROBE** — perform a tiny targeted information-producing action.
- **REVERSIBLE BUILD** — implement a retained-but-removable capability whose normal use provides evidence.
- **SPIKE** — temporary bounded implementation primarily for feasibility learning.
- **EXPERIMENT** — purpose-designed intervention/comparison to discriminate alternatives.
- **CONTROLLED EXPERIMENT** — experiment where stronger causal attribution materially matters.
- **RESEARCH-GRADE** — strong isolation/control for a consequential causal or comparative claim.

```text
INVESTIGATE
!= EXPERIMENT
```

## 10. Stop conditions

Stop evidence acquisition when:

- evidence is sufficient for the current decision;
- remaining uncertainty cannot materially redirect the decision;
- a cheaper reversible action now dominates further inquiry;
- experiment outcomes no longer discriminate among actions;
- added rigor would strengthen a claim the current decision does not need;
- control/isolation overhead exceeds its decision value;
- owner intent or external authority is the actual missing premise.

## 11. Examples

### Experiment warranted

Two architecture paths would each cost weeks. A two-hour compatibility probe can rule
one out. Run the bounded probe/experiment.

### Controlled rigor warranted

The intended claim is "agents using capability X outperform comparable agents without
it." Prior exposure and evaluator leakage could invalidate the comparative causal
claim. Stronger controls are warranted.

### Separate experiment not warranted

A capability costs minutes to implement, is easily reverted, and ordinary use will
immediately reveal whether it is helpful. Prefer the reversible build over hours of
isolation/evaluation protocol.

## 12. Anti-patterns

Avoid:

- "uncertainty exists, therefore experiment";
- treating `INVESTIGATE` as synonymous with experiment;
- calling a small code change a cheap experiment while setup/evaluation overhead is large;
- fresh-agent isolation merely because it creates cleaner evidence;
- treating coding-agent participation as contamination when it is part of normal use;
- demanding causal evidence for a cheap reversible product decision;
- building an evaluation framework before showing that experiment outcomes change the decision;
- experimenting about whether to build something when building it reversibly is cheaper, creates retained useful value, and is sufficiently informative;
- treating reversible build as a universal default even when READ/VERIFY is cheaper or a causal claim requires isolation;
- continuing to purify an experiment after the current decision is already supported.

## 13. Boundaries

```text
experiment selected
!= action authorized

evidence returned
!= semantic conclusion automatic

experiment PASS
!= product value established

normal-use evidence
!= causal proof

minimum sufficient rigor
!= careless evidence

reversible build
!= uncontrolled scope expansion
```

The active semantic agent owns experiment warrant, rigor, confounder relevance, and
interpretation. Deterministic machinery may check only explicit contract/conformance
surfaces; it must not calculate whether an experiment is strategically warranted.
