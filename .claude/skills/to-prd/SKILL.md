---
name: to-prd
description: Convert evidence-backed product opportunities, hypotheses, discovery findings, or an explicitly authorized product direction into a Product Requirements Document while preserving the user's goal, evidence strength, scope boundaries, success measures, risks, dependencies, and approval state. Use for product_specification responsibility. Produce prd; do not create a second PRD authority or present proposed metrics and roadmap dates as observed facts.
---

# to-prd

Satisfy a `product_specification` responsibility by producing the canonical `prd` artifact.

`to-prd` is the single current PRD capability. The upstream `prd` methodology is adapted into this Skill rather than becoming a competing `prd` Skill identity.

## Inputs

Require a product problem/opportunity or hypothesis, intended audience, proposed solution direction, and source user intent. Prefer durable `hypothesis_statement`, `opportunity_map`, `discovery_findings`, persona evidence, and relevant constraints when available.

## Procedure

1. Read [references/methodology.md](references/methodology.md) for the adapted PRD method.
2. Read [references/prd-template.md](references/prd-template.md) for the canonical artifact structure.
3. Restate the source user goal and identify what evidence supports the problem, audience, and why-now claim.
4. Separate observed evidence, owner intent, estimates, proposed targets, and assumptions. Never invent baselines, market size, dates, effort, or approval.
5. Define solution scope in user terms, including core features and explicit out-of-scope boundaries.
6. Define measurable outcomes and success criteria. Unknown baselines or targets stay unknown/proposed rather than being fabricated.
7. Record constraints, dependencies, risks, and open questions that affect delivery or decision quality.
8. Preserve the existing scope-expansion contract. Any material expansion beyond the user's stated goal remains proposed until explicitly authorized.
9. Include user stories or scenarios only at the level needed to make requirements understandable; detailed story decomposition belongs to `user-stories`.
10. Render the canonical template including exactly one machine-readable handoff and return control to the active agent.

## Scope expansion

Use the canonical fields:

```yaml
source_intent_ref: "..."
user_goal_preserved_as: exact_match | core_with_expansion | diverged
scope_expansion_proposed: true | false
scope_expansion_requires_approval: true | false
scope_expansion_status: exact_match | pending_user_approval | approved_by_user | diverged
```

If the proposed specification materially exceeds or contradicts the user's stated goal, do not silently normalize the expansion into core scope.

## Stop or downgrade

- If the problem/audience evidence is weak, produce a clearly provisional specification rather than claiming validation.
- If success cannot be measured, preserve the measurement gap as an open question.
- If a required dependency or owner decision is unknown, surface it rather than inventing resolution.
- If scope expansion requires approval, stop at the approval boundary; do not authorize implementation of the expansion.
- If the request is really story decomposition or acceptance definition, return control so the active agent can select `user-stories` or `acceptance-criteria`.

## Boundary

`PRD != proof of customer demand`, `target metric != observed baseline`, `roadmap proposal != delivery commitment`, and `scope proposal != authority to expand scope`.
