# Adaptive Policy Coordinator v0 — Agent Contract

**Status:** canonical agent-facing semantic composition guidance  
**Parent architecture:** `docs/policy-hierarchy-v0.md`  
**Authority:** interpretive guidance under current product strategy, ADR 0029, and existing authority contracts  
**Runtime status:** semantic composition policy; not a router, planner, scheduler, workflow selector, score, state machine, or runtime service

## 1. Question

Adaptive Policy Coordinator v0 answers:

> **Which policy questions are decision-relevant now, and what is the smallest sufficient composition that preserves evidence, authority, and stopping boundaries?**

It coordinates semantic questions already owned by the active agent. It does not create a new control authority.

```text
policy available
!= policy must activate

policy activated
!= separate runtime component required

coordination
!= routing

coordination
!= authorization
```

## 2. Core principle

Use the **fewest explicit policy layers that can materially change the current decision**.

```text
clear + local + reversible + sufficiently evidenced
-> direct bounded work + relevant verification

ambiguous / consequential / iterative / authority-sensitive
-> activate only the policy questions that can change the decision
```

Zero explicitly surfaced policy layers is a valid successful coordination result for obvious bounded work.

## 3. Relationship to Adaptive Guidance v0

Adaptive Guidance v0 and Adaptive Policy Coordinator v0 solve different problems.

```text
Adaptive Guidance
-> how much scaffolding, rigor, verification, and durability should be visible/used?

Adaptive Policy Coordinator
-> which semantic policy questions are actually decision-relevant now?
```

They may use overlapping context such as consequence, decision complexity, delegation, and continuation complexity, but neither produces scores or deterministic modes.

## 4. Inputs

Use the smallest current context needed:

- goal and authorized scope;
- current decision or contemplated warrant target;
- decision-changing uncertainty, if any;
- evidence sufficiency/currentness;
- consequence and reversibility;
- authority / owner / external boundaries;
- whether the repository future itself is open;
- whether search is materially iterative;
- whether returned evidence can change explicit state;
- whether decision state must survive contexts/agents;
- user supervision and desired delegation when they affect visible scaffolding.

No universal `CoordinatorState` is required.

## 5. Policy activation guidance

### Strategic Repository Sensemaking

Activate when the repository/product future itself is materially open and coherent evolution paths, strategic tradeoffs, or a Level-3 direction must be reconstructed.

Do not activate merely because implementation touches many files.

### Inquiry Policy

Activate explicitly when an unresolved premise could change responsibility, scope, authority path, continuation, verification, closure, or strategy and additional evidence may be worth obtaining.

Do not activate inquiry merely because uncertainty exists.

### Metareasoning Policy

Activate explicitly when the main question is how to spend the next unit of effort among acting, inquiring, challenging, exploring, verifying, escalating, or stopping.

Keep it implicit when the next useful control move is obvious.

### Exploration Policy

Activate when search is materially iterative and prior attempts/outcomes matter to where search effort should go next.

Do not activate for one-shot local work or simply because multiple ideas can be imagined.

### Warrant / Choice Policy

Activate when a consequential target must be justified explicitly or materially credible targets must be compared before commitment.

Do not force a choice; `NO_SELECTION` remains valid.

### Learning / Reconciliation Policy

Activate after returned evidence can materially change explicit claims, uncertainty, responsibility, continuation/closure, strategic state, or thesis-review state.

Do not run formal reconciliation after every tiny expected local result.

## 6. Composition patterns

These are examples, not modes or a transition table.

### Pattern A — obvious bounded work

```text
clear target
+ evidence sufficient
+ authority clear
+ low consequence / reversible
-> direct work
-> relevant verification
-> stop
```

Most policy reasoning may remain implicit.

### Pattern B — one decision-changing uncertainty

```text
uncertainty could change next responsibility
-> Inquiry Policy
-> bounded evidence
-> Warrant / Choice if consequential
-> act or stop
```

Do not activate Exploration merely because an inquiry exists.

### Pattern C — ambiguous control move

```text
several plausible ways to spend effort
-> Metareasoning Policy
-> chosen control move
-> only the dependent policy, if any
```

### Pattern D — iterative search

```text
material attempt history
-> Metareasoning says exploration/search deserves effort
-> Exploration Policy
-> evidence / option-set change
-> Warrant / Choice
```

### Pattern E — repository future open

```text
repository/product evolution decision
-> Strategic Repository Sensemaking
-> 0–5 materially real alternatives
-> Inquiry / Metareasoning / Exploration only as needed
-> Warrant / Choice
-> bounded responsibility only when warranted and authorized
```

### Pattern F — consequential result returned

```text
worker / implementation / validation result
-> evidence
-> Learning / Reconciliation
-> updated explicit state
-> Warrant / Choice reassessment only if needed
```

### Pattern G — strategic reassessment

```text
prior strategic decision / analysis exists
+ new result, observation, trigger, or currentness concern
-> use mechanical currentness projection only when useful
-> ask whether the evidence is decision-changing
-> Learning / Reconciliation when consequential
-> strategic_reconciliation when cross-context durability is warranted
-> Warrant / Choice reassessment only if needed
-> reopen Strategic Repository Sensemaking only when justified
```

Do not activate the whole hierarchy merely because repository HEAD changed.

```text
strategy drift = DRIFTED
!= strategy invalid
!= semantic reassessment automatically required

reassessment trigger observed
!= strategy automatically changed

REOPEN_STRATEGY
!= BUILD
```

The broader composition crosswalk is
`docs/adaptive-semantic-control-architecture-v0.md`. It is descriptive guidance, not
a superior coordinator or new control level.

## 7. Dependency-aware composition

When several policy questions are active, use dependency order only where it matters:

```text
Strategic context
-> Inquiry
-> Metareasoning
-> Exploration
-> Warrant / Choice
-> Action / Execution
-> Evidence
-> Learning / Reconciliation
-> reassess
```

This is **not** a mandatory phase sequence.

Skip layers whose answer cannot change the decision. Re-enter an earlier layer only when new evidence actually reopens its question.

## 8. Compression and deactivation

Policy structure should collapse as soon as its decision value disappears.

Examples:

```text
uncertainty resolved
-> stop explicit Inquiry

search no longer iterative
-> stop explicit Exploration

target sufficiently warranted + authority clear
-> stop comparison and act

result confirms expected local state without changing decision model
-> NO_MODEL_CHANGE
-> stop reconciliation ceremony
```

Do not preserve visible policy ceremony merely because it was useful earlier in the task.

## 9. Escalation and authority

Coordinator activation never grants authority.

```text
policy says ACT
!= protected action authorized

policy says ESCALATE
!= owner decision already made

strategic path selected
!= implementation authorized
```

When the real missing premise is owner intent, external control, protected publication/merge/release authority, or Level-4 commitment, surface that boundary directly.

## 10. Durability

Coordinator state itself should normally be transient.

Persist only material outputs already owned by existing surfaces:

- strategic analysis / STATUS for Level-3 state;
- Campaign / handoff / evidence for durable Level-2 continuation;
- ADRs for ratified architecture/product commitments;
- qualification / verification receipts for mechanical facts;
- issue/PR history for bounded work provenance.

```text
Adaptive Policy Coordinator
!= CoordinatorState schema
!= generic memory service
```

## 11. Delegation

High delegation may allow the active agent to apply these policies without repeatedly asking the user for repository-answerable routing decisions.

But:

```text
desired delegation
!= granted authority

coordinator selects policy question
!= coordinator selects Skill/workflow automatically
```

Capabilities are chosen only after responsibility is selected.

## 12. Mechanical validation boundary

Mechanical checks may verify that:

- canonical policy references exist;
- prohibited runtime/schema surfaces were not introduced;
- required boundary statements remain present;
- a declared artifact satisfies its representation contract.

They cannot determine which policies should activate for a live semantic decision.

```text
mechanical policy contract PASS
!= correct policy activation
!= correct responsibility
!= semantic truth
```

## 13. Compact use

When coordination is actually material, ask:

```text
What decision matters now?
Which unresolved premise could change it?
Is more evidence worth obtaining?
Is the next control move obvious?
Is search materially iterative?
Does a specific target need explicit warrant/choice?
Has returned evidence changed explicit state?
Is the repository future itself open?
Does state need durable continuation?
Which of these questions can be skipped?
```

Then expose only the smallest useful composition.

## 14. Anti-patterns

Avoid:

- running every policy on every task;
- assigning policy-activation scores or thresholds;
- creating `LIGHT / STANDARD / HEAVY` policy modes;
- automatic Skill/workflow/Campaign routing;
- a central `PolicyCoordinator` runtime class/service;
- `CoordinatorState` or another parallel truth store;
- treating the canonical order as a mandatory state machine;
- preserving ceremony after the decision stabilizes;
- inferring owner preference or authority from policy output;
- using high delegation to cross protected action boundaries.
