# Prioritization methodology and prioritized_list contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/prioritize.md`.

RICE is an optional comparison aid:

```text
score = (reach * impact * confidence) / effort
```

Use consistent units inside a comparison. `confidence` is represented from 0 to 1. Missing inputs produce `score: null`; never synthesize numbers just to rank the list. Even a valid score is not a semantic priority decision.

Produce sections: `## Decision context`, `## Candidate evidence and scoring`, `## Recommended order and trade-offs`, `## Dependencies and validation needs`, `## Deferred items`, `## Machine-readable handoff`.

```yaml
artifact_id: prioritized_list
schema_version: "1"
scoring_method: rice | qualitative | mixed
goal_refs: []
items:
  - id: ITEM-1
    statement: "..."
    reach: null
    impact: null
    confidence: null
    effort: null
    score: null
    evidence_refs: []
    dependencies: []
    decision: now | next | later | validate_first
    rationale: "..."
recommended_order: [ITEM-1]
unresolved_questions: []
```

When reach, impact, confidence, and effort are numeric and effort is positive, a non-null RICE score must match the declared arithmetic. `recommended_order` must reference existing unique items but may differ from raw score order when the rationale explains semantic trade-offs.