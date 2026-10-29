# Ontology-First Repository Entry (v1)

**Purpose:** How the active agent enters a repository-level request: establish
or reuse source-grounded understanding of what the repository is before any
repository-wide selection, then explore what it could become broadly enough
before converging. This reference belongs to the distributed
`using-sensemaking` Skill. It is a conceptual journey, not a workflow engine,
a checklist to complete, or a grant of authority.

**Load when:** the request is repository-level ("apply Sensemaking to this
repository", "what could this product become", a broad delegated mission), or
a returning session must judge whether existing semantic and possibility
coverage is adequate for its goal.
**Skip when:** the request is narrow (section 5), or adequate, current
knowledge already answers the question.

## 1. Three layers, kept distinct

| Layer | What it holds | Where it lives |
| --- | --- | --- |
| **Framework ontology** | Sensemaking's reusable vocabulary: goals, evidence, constraints, capabilities, components, dependencies, decisions, possibilities, architecture options, consequences | The Steward's knowledge contract; shared across repositories |
| **Target domain ontology** | The product's own concepts, states, invariants, boundaries and rules | Reviewed records in the target repository, expressed with the framework vocabulary |
| **Target knowledge instances** | Source-grounded statements about what the repository contains, proposes, decides and does not yet know | Reviewed records with sources, status and history |

A domain with unfamiliar nouns does not need new framework types. Express its
concepts with the existing vocabulary; propose a narrow extension only through
the Steward's schema-evolution procedure when a real distinction cannot be
represented.

## 2. First engagement

```text
IDENTIFY REPOSITORY AND GOVERNING INTENT
ASSESS SEMANTIC KNOWLEDGE COVERAGE
BOOTSTRAP REPOSITORY ONTOLOGY            (Steward BOOTSTRAP)
MAP CURRENT SYSTEM AND CAPABILITIES
DIVERGENT POSSIBILITY EXPLORATION        (funnel breadth)
CONVERGENT FRONTIER EXPLORATION
ARCHITECTURAL / STRATEGIC SYNTHESIS      (only where it changes the choice)
COMPARATIVE EVALUATION
CONSEQUENCE DEPTH / FEEDBACK
SELECT / DEFER / INVESTIGATE / NO_CHANGE
PERSIST SOURCE-GROUNDED KNOWLEDGE
  -> stop with a complete reasoning outcome
  -> or an optional, separately authorized implementation handoff
```

Repeat, reorder or skip steps when evidence warrants it. The one fixed point is
the **default entry responsibility**: establish the repository's semantic
foundation before a repository-wide strategic selection. Who owns each step
and when each is warranted: `adaptive-skill-composition-v1.md`.

### Is the existing model adequate?

Adequacy is relative to the goal, not a size or density threshold. For a
repository-level goal, ask whether a later agent could answer from reachable
sources:

- What is the product for, and which accepted decisions and non-goals govern it?
- Which major systems and capabilities exist, and who owns them in source?
- Which domain distinctions must not be conflated?
- Which areas were assessed, and which remain `NOT_ASSESSED`?
- Is the model current against the revision you are reasoning about?

If the answers exist and are current, reuse them and go to exploration. If they
are missing or materially stale for the area the goal turns on, bootstrap or
deepen that area by invoking the `repository-semantic-steward` Skill in
BOOTSTRAP mode (its procedure: `../../repository-semantic-steward/references/bootstrap.md`).
Bootstrapping does not require running product code or an exhaustive
inventory.

### Without write authority

Produce a source-grounded **provisional** model and coverage report in the
session's report. Continue reasoning from it, but say plainly that it was not
persisted and that later agents will not inherit it. Do not claim retention.

## 3. Breadth before convergence

A well-supported local finding can still be strategically inferior to an
opportunity elsewhere in the product. After a foundation exists, the expected
next responsibility for a repository-level goal is broad possibility
exploration through the `strategic-repository-analysis` Skill's Strategic
Exploration Funnel
(`../../strategic-repository-analysis/references/strategic-exploration-funnel-v1.md`).
Its analysis artifact follows that Skill's template and validator.
Explore the major systems and cross-system relationships, and consider
capability expansion, new user experiences, compositions, simplifications,
alternative boundaries and relevant counterfactual futures. Recall retained
`poss:` records first. Classify before retaining: product possibilities,
engineering alternatives, architecture options and construction paths are
different things.

**Possibility coverage assessment.** Before selecting a repository-wide
direction, answer qualitatively:

- Were the major product systems and intended user outcomes considered?
- Were cross-system and compositional opportunities examined?
- Were retained possibilities and earlier rejected alternatives recalled?
- Were meaningful counterfactuals considered without treating them as authorized?
- Is the analysis converging because the evidence supports it, or because the
  first visible candidate was easiest?
- Which material areas remain unexamined, and could an excluded direction
  plausibly overturn the preference?

This is a sufficiency judgment, not a score or candidate quota, and it never
claims every future was explored. Report the unexamined areas with the result.
A repository-wide selection is not justified by one isolated defect. When
exploration itself is the requested outcome, stop after it.

## 4. Subsequent engagements

Do not repeat the full bootstrap. Instead:

1. Identify the target and its source revision.
2. Retrieve the existing ontology, reviewed knowledge and prior analyses.
3. Check source relevance, semantic coverage and material currentness.
4. Reconcile only consequential gaps or contradictions.
5. Determine the current unresolved reasoning question.
6. Apply the specialist that owns it.
7. Persist meaningful changes.
8. Stop, or continue within the delegated reasoning mission.

Understanding should improve across sessions; a session that only re-derives
what the records already say has not used them.

## 5. Narrow requests

A narrow request, such as evaluating one proposed architectural change, uses
the relevant existing knowledge instead of repository-wide exploration. Keep
the requested scope and never present a narrow result as a repository-wide
possibility evaluation. An explicit implementation request can go to the
portable construction loop without a new strategic exploration when an
adequate governing decision and relevant context already exist.

## 6. Outcomes

Each of these is a complete result: a semantic foundation with a coverage
report; a possibility landscape; an architecture synthesis; a strategic
selection, deferral, investigation or justified no-change; reconciled
knowledge. An implementation handoff needs an independently warranted
direction and its own authority; a selected direction does not invoke an
implementation planner by itself.

## 7. Evidence ceiling

This entry follows an owner-selected product identity. That it improves
decisions, transfers across hosts or is reused by later sessions is not yet
established; report what a session actually observed.
