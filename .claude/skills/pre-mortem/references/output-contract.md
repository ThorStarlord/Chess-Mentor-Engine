# risk_analysis output contract

Produce: `## Context and assumptions`, `## Tigers`, `## Paper tigers`, `## Elephants`, `## Mitigations and monitoring`, `## Recommendation`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: risk_analysis
schema_version: "1"
source_artifact_ref: "artifacts/prd.md"
risks:
  - id: RISK-1
    class: tiger | paper_tiger | elephant
    statement: "..."
    evidence_status: observed | inferred | hypothetical | unknown
    evidence_refs: []
    urgency: launch_blocking | fast_follow | track | investigate
    impact: high | medium | low | unknown
    probability: high | medium | low | unknown
    mitigation: "..."
    owner_role: "..."
    success_criterion: "..."
    escalation_signal: "..."
recommendation: go | go_with_conditions | no_go | insufficient_evidence
conditions: []
unresolved_questions: []
```

Rules:

- risk IDs are unique;
- a `tiger` cannot use `hypothetical` evidence status without an explicit rationale that keeps the classification provisional;
- `paper_tiger` records why existing evidence/controls justify downgrading the concern;
- `elephant` normally uses `investigate` urgency until evidence supports a stronger classification;
- the recommendation is analysis only and grants no launch/external-action authority.
