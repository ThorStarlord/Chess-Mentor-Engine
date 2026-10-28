# Strategy methodology and strategy_doc contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/strategy.md`.

Retain the useful nine-part strategy canvas: vision, segment, problem, solution/choices, differentiation, monetization, metrics, roadmap themes, risks, and next actions. Normalize every unsupported numeric/example value into a hypothesis or unknown.

Produce sections: `## Vision and context`, `## Target segments and non-targets`, `## Problems and evidence`, `## Strategic choices and non-choices`, `## Differentiation and business model`, `## Measures and roadmap themes`, `## Risks dependencies and open decisions`, `## Machine-readable handoff`.

```yaml
artifact_id: strategy_doc
schema_version: "1"
status: proposed
vision: "..."
target_segments: []
non_targets: []
problem_refs: []
choices:
  - id: CHOICE-1
    statement: "..."
    rationale: "..."
    evidence_refs: []
non_choices: []
differentiation_hypotheses: []
monetization_hypotheses: []
measures:
  - name: "..."
    baseline: null
    target: "..."
    evidence_status: proposed
    evidence_refs: []
roadmap_themes: []
risks: []
assumptions: []
unresolved_questions: []
```

`status` remains `proposed` in this capability. Ratification belongs to explicit owner/decision evidence, not this artifact generator. Observed baselines require evidence refs; proposed targets are not observations.