# Adaptive Skill Composition (v1)

**Purpose:** How the active agent applying `using-sensemaking` composes
specialized reasoning: who owns each activity, when it is warranted, how
results feed back, and what a specialist returns. This reference belongs to the
distributed `using-sensemaking` Skill. It is guidance for one semantic
controller, not a router, pipeline, planner or new artifact.

**Load when:** choosing, sequencing or interpreting specialist reasoning, or a
specialist has just returned.
**Skip when:** the next action is a single obvious step.

## 1. Activity owners

| Activity | Owner (procedure) | Durable product |
| --- | --- | --- |
| Semantic foundation, recall, audit, reconciliation | `repository-semantic-steward` (BOOTSTRAP, RECALL, AUDIT, RECONCILE) | `.sensemaking/knowledge/*.json`, query receipts |
| Repository orientation when boundaries or ownership are unclear | `repo-sensemaker` | `repository_sensemaking_brief` |
| Divergent and convergent possibility exploration | `strategic-repository-analysis` (Strategic Exploration Funnel) | report; `poss:` records when retained |
| Architectural synthesis and consequence depth | `repository-semantic-steward` (architecture exploration) | `architectural_synthesis`; `arch:` and consequence records when retained |
| Strategic construction-path synthesis and comparative selection | `strategic-repository-analysis` (construction-path synthesis) | `strategic_repository_analysis` |
| Adversarial challenge of a provisional direction | `architectural-review`, `pre-mortem` | review report |
| Reconsideration after strategic evidence | `strategic-repository-reconciliation`; Steward RECONCILE for knowledge | reconciliation; record history |
| Owner-reserved choice | `owner-decision-capsule` | decision capsule |
| Cross-session continuation of a reasoning mission | `strategic-sensemaking-loop` | session receipts |
| Authorized realization of a selected direction | portable construction loop (`portable-construction-loop-v1.md`) | code change, PR, implementation receipt |

The table names owners, not an order. Skills stay directly invokable by
maintainers; ordinary users need only `using-sensemaking`.

## 2. When each activity is warranted

| Activity | Warranted when |
| --- | --- |
| Semantic foundation | No adequate current model exists for the goal's scope (`ontology-first-entry-v1.md`) |
| Divergent exploration | Possibility coverage is inadequate, or the future is materially open |
| Convergent exploration | The landscape is sufficient and candidates need qualification |
| Architectural synthesis | Alternative structures would materially change a future's value or feasibility |
| Construction-path synthesis | A coherent trajectory toward a future capability needs developing |
| Convergent evaluation | Material alternatives are developed enough to compare |
| Consequence depth | A provisional preference may cause downstream effects that change the choice |
| Adversarial challenge | Important assumptions, commitments or consequences need scrutiny |
| Reconsideration | New evidence changes the premises behind an earlier preference |

Skip an activity whose result could not change the decision. Skipping is a
judgment to state when it is consequential, not a failure.

## 3. Feedback moves

The controller may move:

- from divergent exploration into ontology enrichment, when exploration
  exposes an unmodelled system or distinction;
- from convergence back to divergence, when an important possibility is missing;
- from consequence depth back to architectural synthesis, when a consequence
  defeats or reshapes the preferred option;
- from architectural synthesis into construction-path comparison;
- from evaluation into further evidence gathering;
- from a justified preference into durable knowledge retention.

Each move is a fresh controller choice, made because the returned evidence
warrants it.

```text
specialist result      != controller decision
preferred architecture != selected strategic direction
selected direction     != implementation authorization
suggested continuation != next responsibility
```

## 4. Invoking a specialist

1. Identify the warranted specialist responsibility.
2. Resolve the actual installed or repository-local Skill instructions.
3. Invoke that Skill by name through the host's Skill mechanism (for example
   the Skill tool with `repository-semantic-steward`). This loads its
   `SKILL.md`, which carries its contract: how to validate, which CLI to pin,
   which template an artifact follows. Then read the references it points to.
4. Supply the available source context and relevant artifact references.
5. Receive and interpret its result.
6. Validate consequential artifacts when a validator applies. Give an output a
   specialist's artifact identity (for example `strategic_repository_analysis`)
   only when it follows that specialist's template and passes its validator;
   otherwise present it as a report.
7. Choose the next warranted reasoning activity.

When the host cannot invoke a Skill natively, read the specialist's `SKILL.md`
first and then its references, in the same session; this is an acceptable
fallback. Reading only a deep reference (such as `bootstrap.md`) skips the
specialist's contract and is not. Installed Skills are not a host-independent executable
call graph; do not claim one.

## 5. Return convention

A specialist returns control without deciding the next specialist. Its return,
expressed through its existing artifact and task report rather than a new
master artifact, states:

- the responsibility it completed (or why it stopped);
- the actual source revision and artifact references;
- consequential findings;
- remaining uncertainties and contradictions;
- a suggested continuation, as evidence for the controller;
- the limits of its claim and of the authority it used.

The controller reads the return, decides what changed, and reconciles before
continuing.

## 6. Anti-patterns

- A fixed pipeline that runs every activity for every request.
- Numeric scores or a selector that picks the next Skill.
- A specialist that hands work directly to another specialist.
- Treating a strategic selection as a request to implement.
- A second controller: continuation procedures resume and preserve reasoning;
  they do not redefine responsibility selection.
