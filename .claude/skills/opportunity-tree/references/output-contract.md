# opportunity_map output contract

Produce: `## Desired outcome`, `## Opportunities`, `## Opportunity comparison`, `## Candidate solutions and risky assumptions`, `## Learning tests`, `## Recommended branch`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: opportunity_map
schema_version: "1"
desired_outcome:
  statement: "..."
  metric: null
  baseline: null
  target: null
opportunities:
  - id: O-1
    statement: "..."
    status: assumption
    evidence_refs: []
    importance: null
    satisfaction: null
    score: null
recommended_branch: null
unresolved_questions: []
```

Opportunity IDs are unique. `status` is `assumption` or `evidence_backed`; evidence-backed opportunities require evidence refs. If score and numeric importance/satisfaction are all present, score follows `importance * (1 - satisfaction / 5)` within ordinary rounding tolerance. Unknown numeric inputs remain `null`.
