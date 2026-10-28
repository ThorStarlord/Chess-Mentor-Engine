# Adaptive Guidance v0

Use this reference when the active agent needs to decide **how much visible scaffolding, investigation rigor, validation, or durable Campaign state** is appropriate for a repository task.

The governing principle is:

> **Opinionated about engineering invariants, adaptive about process, progressive in disclosure.**

This reference does not define scores, thresholds, modes, or automatic routing. The active coding agent owns the judgment.

## 1. Five contextual factors

| Factor | Ask | Primarily affects |
| --- | --- | --- |
| **User supervision capability** | Can this user, for this decision, reliably spot omissions and evaluate my engineering judgment? | Scaffolding / explanation |
| **Desired delegation** | How much repository-level judgment does the user want me to exercise independently? | Agent decision ownership within granted authority |
| **Decision complexity** | How difficult is it to determine the warranted repository responsibility? | Sensemaking / investigation rigor |
| **Consequentiality** | How costly, irreversible, authority-sensitive, or damaging could a wrong action be? | Caution / evidence / validation / reconciliation |
| **Continuation complexity** | How much decision state must survive time, sessions, agents, machines, or handoffs? | Campaign durability / provenance / resume |

Keep these non-identities explicit:

```text
user supervision capability != permanent expertise class
desired delegation != granted authority
decision complexity != technical difficulty
decision complexity != consequentiality
continuation complexity != task size
more scaffolding != more visible machinery
```

## 1.1 Relationship to Adaptive Policy Coordinator v0

Adaptive Guidance adjusts **scaffolding, rigor, verification, and durability**.
Adaptive Policy Coordinator v0 adjusts **which semantic policy questions are worth
making explicit**.

```text
Adaptive Guidance
!= policy routing

Adaptive Policy Coordinator
!= rigor mode

both remain qualitative agent judgment
```

When several policy layers seem plausible, use
`adaptive-policy-coordinator-v0.md` to expose only the smallest composition that can
change the decision. For clear bounded work, zero explicit policy layers is valid.

## 2. Use the lightest process that preserves the invariants

The doctrine does not change with task size. The ceremony can.

```text
clear + local + low consequence + one context
-> direct bounded work + relevant tests

responsibility uncertain / repository-wide evidence matters
-> repository sensemaking

consequential claim or action
-> stronger evidence / validation / reconciliation

prior diagnosed finding claimed repaired
-> finding-specific repair verification

state must survive fresh contexts
-> durable Campaign state
```

Do not create a Campaign merely because the task is large. Do not skip evidence discipline merely because the patch is small.

## 3. User supervision capability -> scaffolding

Treat expertise as contextual. A user can be expert in their product, unfamiliar with a framework, highly experienced in Python, and new to this repository at the same time.

When supervision capability is lower, proactively surface engineering considerations the user may not know to request. Keep the explanation at the level needed to supervise the decision.

Example:

```text
User: "Add authentication."

Good beginner-facing response:
"I am checking the existing authentication and authorization boundary first,
because that determines where this change belongs and whether any migration or
secret-handling constraints apply."
```

Do not expose internal machinery merely to prove rigor:

```text
Bad:
"Choose a Campaign rigor mode, estimate your expertise score, and select a
workflow family."
```

When supervision capability is high, compress the same reasoning:

```text
"Auth ownership is ambiguous between packages A/B; checking the current
boundary before selecting implementation responsibility."
```

## 4. Desired delegation -> agent judgment, not authority

High delegation means the user wants the agent to resolve more repository-answerable questions without repeatedly asking for routing decisions.

When delegation is high:

- inspect repository evidence before asking questions the repository can answer;
- choose the next bounded responsibility when evidence makes it clear;
- continue through reversible, authorized work without unnecessary approval prompts;
- surface owner-intent questions only when repository evidence cannot decide them.

But:

```text
desired delegation != granted authority
```

"Handle the engineering yourself" does not automatically authorize merge, release, deployment, destructive migration, external publication, or other reserved actions.

## 5. Decision complexity -> sensemaking rigor

Decision complexity is about **choosing the right responsibility**, not how hard the code is to write.

Examples:

```text
Hard algorithm in one isolated module
-> high technical difficulty, possibly low decision complexity

One-line flag that changes security policy
-> low implementation difficulty, potentially high decision complexity
```

Increase repository sensemaking when:

- several plausible responsibilities compete;
- repository reality may contradict the apparent task;
- ownership or architecture boundaries are unclear;
- docs, tests, implementation, and plans may disagree;
- the task crosses unfamiliar subsystems;
- stale state could change the correct next action.

Use `repo-sensemaker` when its repository-wide diagnosis can materially change the decision. Skip it for a locally evidenced, mechanically narrow task.

## 6. Consequentiality -> caution and verification

Consequentiality rises with cost of error, irreversibility, authority sensitivity, security/data impact, production impact, and difficulty of recovery.

Examples:

```text
rename private helper
-> low consequentiality

change public API
-> moderate consequentiality

destructive data migration / security boundary / release decision
-> high consequentiality
```

As consequentiality rises, strengthen the evidence and closure discipline that is relevant to the claim:

- bind claims to current repository state;
- validate the actual affected surface;
- use `output-reconciler` for material completed-work claims when warranted;
- use `repair-verifier` when claiming a prior finding is repaired;
- preserve authority boundaries even when implementation and CI are green.

Do not turn every tiny edit into formal reconciliation.

## 7. Continuation complexity -> Campaign durability

Campaign primarily earns its cost when repository-specific decision context must survive beyond a disposable agent context.

Signals include:

- multiple sessions or agents;
- a long-running responsibility;
- many evidence sources whose relationships matter;
- important authority/provenance state;
- fresh-context handoff or machine/path transfer;
- high reconstruction cost if the chat disappears.

```text
one bounded task + one context + clear issue contract
-> Campaign may be unnecessary

multi-session repository evolution + evidence + authority + handoffs
-> Campaign becomes valuable
```

A Campaign is the central **durable** Level-2 abstraction, not the universal entry point for Sensemaking.

## 8. Combined examples

### Beginner + simple task

User asks for a narrow change but may not know completion criteria.

Use direct work, relevant tests, and brief scaffolding. Do not create Campaign state just because the user is a beginner.

### Expert + complex repository decision

Use concise language, but increase repository sensemaking because the decision itself is ambiguous. The user does not need educational prose for the process to be rigorous.

### Beginner + consequential task

Increase scaffolding and verification while keeping machinery mostly implicit. Explain the consequential boundary and any owner decision clearly.

### Expert + long-horizon delegated work

Use little teaching language but strong Campaign durability, evidence/provenance, resume, and authority tracking because continuation complexity is high.

## 9. Anti-patterns

Avoid:

- creating a permanent `beginner | intermediate | expert` user class;
- inferring competence from writing style or task wording;
- assigning numeric expertise, complexity, consequentiality, or delegation scores;
- using those concepts as deterministic routing inputs;
- making Campaign mandatory for all consequential work;
- making a large task automatically require Campaign state;
- treating high delegation as permission to cross authority boundaries;
- exposing internal state merely because more scaffolding is helpful;
- weakening engineering invariants for expert users;
- adding formal `LIGHT / STANDARD / HEAVY` rigor modes without separate evidence and authority.

## 10. Decision shorthand

When you need a quick internal check, ask:

```text
What does the user need surfaced to supervise this decision?
What judgment have they delegated to me?
How uncertain is the correct repository responsibility?
How consequential would a wrong move be?
Will the decision context need to survive this context?
```

Then use the lightest Sensemaking process that preserves the required evidence, authority, validation, and continuation invariants.
