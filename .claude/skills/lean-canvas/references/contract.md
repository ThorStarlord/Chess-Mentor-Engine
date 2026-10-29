# Lean Canvas methodology and business_canvas contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/lean-canvas.md`.

Retain Ash Maurya's nine blocks: problem, solution, unique value proposition, unfair advantage, customer segments, channels, revenue streams, cost structure, and key metrics. Treat the canvas as a hypothesis map rather than a business-plan truth source.

Produce sections: `## Canvas`, `## Evidence and assumptions`, `## Critical hypotheses`, `## Validation order`, `## Unknowns and limitations`, `## Machine-readable handoff`.

```yaml
artifact_id: business_canvas
schema_version: "1"
status: hypothesis
blocks:
  problem: {value: [], evidence_status: inferred, evidence_refs: []}
  solution: {value: [], evidence_status: hypothesis, evidence_refs: []}
  unique_value_proposition: {value: "...", evidence_status: hypothesis, evidence_refs: []}
  unfair_advantage: {value: "...", evidence_status: hypothesis, evidence_refs: []}
  customer_segments: {value: [], evidence_status: inferred, evidence_refs: []}
  channels: {value: [], evidence_status: hypothesis, evidence_refs: []}
  revenue_streams: {value: [], evidence_status: hypothesis, evidence_refs: []}
  cost_structure: {value: [], evidence_status: unknown, evidence_refs: []}
  key_metrics: {value: [], evidence_status: hypothesis, evidence_refs: []}
critical_hypotheses:
  - id: H-1
    statement: "..."
    risk: high | medium | low | unknown
    evidence_refs: []
    validation_method: "..."
unresolved_questions: []
```

Allowed evidence states are `observed`, `inferred`, `hypothesis`, and `unknown`. Any block marked `observed` requires evidence refs. `status` is always `hypothesis` here; later empirical evidence may update Campaign knowledge without retroactively changing the meaning of this generated canvas.

For `critical_hypotheses[].validation_method`, record the lowest-cost plausible evidence source. An experiment is allowed only when Experiment Economy has established experiment warrant; an untested or high-risk hypothesis does not itself justify experimentation.
