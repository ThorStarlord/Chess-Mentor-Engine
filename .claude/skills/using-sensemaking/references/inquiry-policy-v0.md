# Inquiry Policy v0 — Agent Contract

**Status:** canonical agent-facing semantic policy  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive control guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic policy; not a service, schema, scorer, or automatic router

## 1. Question

Inquiry Policy answers:

> **Given the current decision and epistemic state, what should we learn next, if
> anything?**

It does not choose the final repository responsibility by itself and does not authorize
an action.

## 2. Activation rule

Make Inquiry Policy explicit when an unresolved information gap could materially change
one or more of:

- responsibility;
- scope;
- authority path;
- continue / stop / defer;
- verification requirement;
- closure claim.

Do not invoke explicit inquiry merely because uncertainty exists.

```text
uncertainty exists
!= inquiry required

available question
!= decision-changing question

more evidence possible
!= more evidence worth obtaining
```

For obvious, local, reversible work with sufficient evidence, keep the policy implicit.

## 3. Inputs

Reason from the smallest current decision context needed to answer:

```text
DECISION TO SUPPORT
CURRENT CLAIMS / EVIDENCE
UNRESOLVED UNCERTAINTIES
CURRENT RESPONSIBILITY, IF ANY
AUTHORITY / EXTERNAL CONSTRAINTS
CONSEQUENCE + REVERSIBILITY
KNOWN EVIDENCE SOURCES
COST / DELAY OF FURTHER INQUIRY
```

Do not require a new durable object when these facts are already reconstructible from
current Sensemaking surfaces.

## 4. Outcomes

Use these documentation-level outcomes when making the policy explicit.

### `NO_INQUIRY_NEEDED`

Current evidence is sufficient for the present decision, or remaining uncertainty would
not materially change the decision.

This is a successful outcome.

### `INQUIRY_REQUIRED`

Additional evidence could materially change the decision and is worth obtaining.

Record:

```text
INQUIRY TARGET
DECISION AFFECTED
WHY THIS QUESTION IS DECISION-CHANGING
SMALLEST SUFFICIENT EVIDENCE
EVIDENCE SOURCE
BOUNDED EVIDENCE-PRODUCING RESPONSIBILITY, IF NEEDED
AUTHORITY REQUIRED
STOP CONDITION
WHAT EACH MATERIAL ANSWER WOULD CHANGE
```

### `OWNER_INTENT_REQUIRED`

The missing premise is an owner preference, product commitment, or reserved decision
that repository investigation cannot establish.

Do not disguise missing owner intent as technical research.

### `EXTERNAL_EVIDENCE_REQUIRED`

The needed evidence depends on an external system, user, environment, or authority
outside the current repository/tool boundary.

Record the external dependency rather than fabricating an internal substitute.

### `VERIFICATION_REQUIRED`

The decision is already selected or action already occurred, but a claim needed for
closure remains unverified.

Verification is not a reason to reopen broad exploration unless the verification result
would change the responsibility or frame.

## 5. Selection rule

Prefer the **smallest sufficient inquiry** and the lowest-cost evidence source
strong enough for the current decision and claim.

A useful qualitative rule is:

```text
select inquiry when:
  plausible answer could change the decision
  AND evidence is obtainable within authority
  AND expected decision improvement is worth
      information cost + reasoning cost + delay + opportunity cost
```

No numeric score is required.

When several uncertainties exist, prefer the one whose resolution most directly
discriminates among materially different next responsibilities.

Before escalating from ordinary inquiry into experimentation, apply the
Experiment Warrant Gate:

```text
uncertainty exists
!= experiment required

INVESTIGATE
!= EXPERIMENT

experiment possible
!= experiment warranted

better evidence possible
!= better evidence worth obtaining
```

Check current evidence, authoritative reading, inspection, verification,
owner/external sources, a tiny probe, and cheap reversible construction before
paying for a separate experiment. If plausible experiment outcomes would not
change what becomes warranted, do not experiment.

When experimentation is materially considered, read
`experiment-economy-v1.md` for evidence-source economy, total experiment cost,
Minimum Sufficient Experimental Rigor, Confounder Warrant, and claim-relative
evidence guidance.

## 6. Evidence-producing responsibility

Inquiry may be satisfied by:

- reading an authoritative source;
- inspecting repository state;
- verifying an existing claim;
- running a bounded probe/test;
- asking the owner;
- checking an external system when authorized;
- delegating a bounded investigation;
- performing a cheap reversible information-producing action;
- implementing a cheap reversible capability whose normal use itself supplies
  sufficient evidence.

Do not treat a separate experiment as the default evidence-producing
responsibility. A reversible build may be both the useful product step and the
cheapest sufficient inquiry.

Do not inflate inquiry into a Campaign or architecture project unless continuation
complexity independently warrants that machinery.

## 7. Stop conditions

Stop inquiry when any of the following becomes true:

- evidence is sufficient for the current decision;
- remaining uncertainty cannot materially change the decision;
- the needed source is unavailable or outside authority;
- owner intent is the actual missing premise;
- expected decision improvement no longer justifies search cost;
- a cheap reversible action or reversible build now dominates further analysis;
- experiment outcomes would no longer discriminate among materially different actions;
- added experimental rigor would strengthen a claim the current decision does not need;
- isolation/control overhead no longer justifies its decision value;
- evidence invalidates the current decision frame and requires strategic reassessment.

```text
stop inquiry
!= close the whole responsibility

inquiry complete
-> return evidence to the active semantic controller
```

## 8. Authority boundaries

```text
inquiry selected
!= action authorized

evidence obtained
!= semantic conclusion automatic

owner-intent gap
!= repository evidence gap

external blocker
!= permission to fabricate local evidence
```

The active semantic agent adjudicates returned evidence and decides what becomes
warranted next.

## 9. Relationship to other policies

```text
Strategic Policy
-> which repository decision matters?

Inquiry Policy
-> what should we learn next, if anything?

Metareasoning Policy
-> should we inquire, act, explore, challenge, verify, escalate, or stop?

Exploration Policy
-> how should iterative search effort be allocated?

Warrant / Choice Policy
-> what is justified now?

Action / Execution
-> perform selected authorized work

Learning / Reconciliation
-> what explicit model/state changes after evidence returns?
```

Inquiry Policy does not subsume those other layers.

## 10. Compact use

For a consequential decision, ask:

```text
What decision am I supporting?

What unknown could actually change it?

What is the smallest evidence that would discriminate between
materially different next responsibilities?

Where can that evidence come from?

Am I authorized to obtain it?

Is learning it worth the cost now?

What result lets me stop inquiring?
```

If no unknown passes those tests, return `NO_INQUIRY_NEEDED`.

If experimentation is being considered, additionally ask:

```text
Would the plausible outcomes change the decision?

Could a cheaper evidence source answer it?

Could cheap reversible construction answer it?

What is the total experiment cost including setup,
isolation, evaluation, interpretation, documentation,
delay, and opportunity cost?

What controls are actually required for the claim?
```

## 11. Anti-patterns

Avoid:

- investigating every unresolved uncertainty;
- treating open issues as questions that must be answered now;
- using repository research to infer owner preference;
- collecting evidence with no stated decision effect;
- building tooling before proving the inquiry recurs;
- treating `INVESTIGATE` as synonymous with experiment;
- selecting an experiment when reversible construction is cheaper and sufficiently informative;
- calling an experiment cheap while ignoring isolation/evaluation/documentation overhead;
- controlling every possible confounder instead of only decision-relevant ones;
- treating coding-agent participation as contamination when it is part of normal product use;
- demanding research-grade causal evidence for a cheap reversible product decision;
- continuing search after the current decision is already sufficiently supported;
- turning Inquiry Policy outcomes into runtime enums or numeric scores merely for implementation convenience.


## Owner and external evidence

When inquiry is warranted, name the smallest sufficient evidence, its source,
the bounded evidence-producing responsibility if one is needed, the authority
it needs, and a stop condition.

- If the missing premise is owner intent, ask the owner rather than searching
  the repository. Use an `owner_decision_capsule` when the choice needs a
  reconstructible options/tradeoff packet.
- If the needed evidence is external and unavailable or unauthorized, record
  the external dependency rather than fabricating a local substitute.
- When authorized external evidence is obtained and its provenance or
  currentness is decision-relevant, preserve it in an
  `external_evidence_packet`.

Returned evidence comes back to the active agent for adjudication.
