# Roadmap methodology and roadmap contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/roadmap.md`.

Retain phased sequencing, dependencies, milestones, resource assumptions, buffer thinking, success criteria, communication/review triggers, and explicit trade-offs. Remove illustrative dates/capacity as defaults.

Produce sections: `## Goals and planning assumptions`, `## Themes and initiatives`, `## Dependencies and sequence`, `## Milestones and outcomes`, `## Capacity and contingency`, `## Review triggers and uncertainties`, `## Machine-readable handoff`.

```yaml
artifact_id: roadmap
schema_version: "1"
status: proposed
period: "..."
goal_refs: []
initiatives:
  - id: INIT-1
    theme: "..."
    statement: "..."
    source_priority_refs: []
    dependencies: []
    timing: null
    timing_status: unknown | estimate | committed
    authority_ref: null
    expected_outcomes: []
    confidence: low | medium | high | unknown
milestones: []
capacity_assumptions: []
review_triggers: []
unresolved_questions: []
```

Initiative IDs are unique and dependencies must reference declared initiatives or explicit external prerequisites. `timing_status: committed` requires a non-empty `authority_ref`; estimates do not. The artifact itself stays a roadmap proposal even when one underlying date is externally committed.