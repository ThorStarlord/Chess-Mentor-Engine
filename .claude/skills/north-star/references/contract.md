# North Star methodology and north_star_metric contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/north-star.md`.

Use the upstream business-game heuristic and seven useful criteria: understandable, customer-centric, sustainable value, vision aligned, quantitative, actionable, and leading-indicator potential. The framework's blanket rules (for example that revenue can never be useful as a top-level metric) are treated as heuristics, not universal truths.

Produce sections: `## Value model and evidence`, `## Candidate metrics`, `## Candidate assessment`, `## Proposed North Star`, `## Input metrics and guardrails`, `## Measurement gaps and review cadence`, `## Machine-readable handoff`.

```yaml
artifact_id: north_star_metric
schema_version: "1"
status: proposed
business_game: attention | transaction | productivity | other
candidates:
  - id: NSM-1
    name: "..."
    definition: "..."
    scores:
      understandable: 1
      customer_centric: 1
      sustainable_value: 1
      vision_alignment: 1
      quantitative: 1
      actionable: 1
      leading_indicator: 1
    rationale: "..."
selected_candidate_id: NSM-1
baseline:
  value: null
  evidence_status: unknown | observed | proposed
  evidence_refs: []
targets: []
input_metrics:
  - name: "..."
    relationship: "hypothesized"
    evidence_refs: []
guardrails: []
unresolved_questions: []
```

Candidate IDs are unique and the selected ID must resolve. Scores are 1-5 assessments, not empirical measurements. An `observed` baseline requires evidence refs. `status` remains `proposed`; metric adoption/ratification is a separate decision.