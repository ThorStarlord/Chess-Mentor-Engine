# Competitive-analysis methodology and market_analysis contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/competitive-analysis.md`.

Use a relevant feature/capability matrix, SWOT-style interpretation, positioning analysis, market gaps, and recommendations. Unlike the upstream examples, no competitor fact, price, impact percentage, roadmap timing, or market claim may be invented to complete the template.

Every material competitor claim should carry a source reference and source/observation date when available. Separate `observed`, `inferred`, and `unknown` evidence states. A stale fact can still be useful if its age is visible.

Produce sections: `## Scope and evidence cutoff`, `## Competitors and sources`, `## Comparison`, `## Strengths weaknesses gaps and threats`, `## Positioning options`, `## Recommendations and uncertainties`, `## Machine-readable handoff`.

```yaml
artifact_id: market_analysis
schema_version: "1"
evidence_cutoff: "YYYY-MM-DD"
product: "..."
segment: "..."
competitors:
  - id: COMP-1
    name: "..."
    claims:
      - dimension: "pricing"
        value: "..."
        evidence_status: observed | inferred | unknown
        source_refs: ["..."]
        observed_at: "YYYY-MM-DD"
gaps: []
positioning_options: []
recommendations: []
unresolved_questions: []
```

Observed competitor claims require at least one source reference. Inferences may cite supporting signals; unknowns may have no source. Positioning and recommendations remain analysis, not external market facts.