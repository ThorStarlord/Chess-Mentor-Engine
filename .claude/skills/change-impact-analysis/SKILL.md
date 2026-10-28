---
name: change-impact-analysis
description: analyze a bounded contemplated or completed repository change to identify decision-relevant affected code/contracts/artifacts/tests/docs/claims/authority/release/cross-repository surfaces, required verification or reconciliation, and bounded follow-up responsibilities without authorizing or executing those changes.
---

# change-impact-analysis

Use when a change may have consequential effects beyond its immediate edited
files or when a completion/closure claim depends on reconciling affected surfaces.

Produce:

`artifacts/change_impact_analysis.md`

## Responsibility

Construct an evidence-grounded **change impact decision space**.

The active semantic agent decides what is materially affected. Deterministic
validation checks representation/reference boundaries only.

## Inputs

Use:

1. explicit target change statement;
2. change state: `CONTEMPLATED | IMPLEMENTED | VERIFIED`;
3. exact target repository/source identity when available;
4. bounded scope;
5. repository evidence and explicit relationship/contract surfaces;
6. prior strategic/Campaign/execution evidence when decision-relevant.

## Procedure

### 1. Establish change and scope

State exactly what is changing/changed and what authority exists.

### 2. Gather smallest sufficient impact evidence

Inspect only evidence capable of changing implementation, verification,
reconciliation, closure, or authority.

### 2A. Optional persistent-knowledge consultation (ADR 0031)

When a **current, exact-revision** semantic knowledge index already exists and
cross-episode architectural rationale might change the impact decision, use
`semantic knowledge-query --operation impact --subject <claim-id>` to retrieve
explicit edges, governing intent, historical decisions and evidence pointers.
Use `why` on an exact decision ID and `contradictions` when competing
claims may matter. See
`../../docs/semantic-architecture/persistent-knowledge-cli.md`.

**Recheck actual cited source.** Indexed edge `depends_on` is an
attributed source claim, not automatically an architectural dependency;
impact paths are *candidates*, not proof of downstream consequences.
Missing links mean NOT ASSESSED, not absence. If no suitable current index
exists, inspect code/ADRs/tests directly without creating an ontology
preflight. The knowledge store cannot select a responsibility or authorize
a merge, release or cross-repo action.

### 3. Identify affected surfaces

Use categories:

`code | contract | artifact | test | documentation | claim | decision |
authority | repository_boundary | release | external_dependency`.

For each item record evidence, material impact, semantic-review need,
verification/reconciliation need, and authority boundary.

### 3A. Follow consequence depth when the impact can propagate

When an affected surface can change another consumer's interpretation or later
workflow behavior, follow the consequence chain only while the next layer can
change implementation, verification, reconciliation, closure, ownership, or
strategy.

Ask, as needed:

- what consumes or depends on the changed state/concept?
- what later behavior follows from those consumers?
- can the effect compound across stages/time?
- do several impacts point to one shared invariant or missing abstraction?
- does the current architecture materially obstruct that invariant?
- is any resulting Level-3/Level-4 consequence actually decision-changing?

Do not manufacture architectural work merely because a consequence can be
imagined. See
`../../docs/research/consequence-depth-and-systems-reasoning-v0.md`.

### 4. Identify explicit cross-repository impact

Only for caller-selected/authorized repository scope. Never discover/add targets
automatically.

### 5. Reconcile claim/verification consequences

Ask:

- what claim becomes stale or stronger?
- what verification is now required?
- what documentation/contract must remain current?
- does authority change? (Usually no.)
- does this reopen Level 3 or require Level 4 review?

### 6. Nominate bounded follow-up responsibilities

Only when evidence warrants them. Do not create a backlog from every impact.

### 7. State closure effect

Choose:

`NO_CLOSURE_EFFECT | ADDITIONAL_VERIFICATION_REQUIRED |
RECONCILIATION_REQUIRED | OWNER_DECISION_REQUIRED |
STRATEGIC_REASSESSMENT_REQUIRED | THESIS_REVIEW_REQUIRED`.

This is semantic agent judgment.

### 8. Validate

```bash
python scripts/validate-artifact.py change_impact_analysis artifacts/change_impact_analysis.md
python scripts/validate-change-impact-analysis.py artifacts/change_impact_analysis.md
```

## Laws

```text
reference occurrence != material impact
impact identified != change required
change required != change authorized
verification requirement != verification result
follow-up candidate != backlog item
cross-repo impact != automatic scope expansion
mechanical PASS != semantic truth
local mechanical success != systemic correctness
affected surface != downstream consequence automatically
repeated local patches != missing abstraction proven
```
