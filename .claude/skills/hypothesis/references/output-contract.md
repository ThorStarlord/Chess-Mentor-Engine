# hypothesis_statement output contract

Produce: `## Hypothesis`, `## Context and evidence`, `## Target and expected behavior`, `## Measures and thresholds`, `## Risk assumptions`, `## Validation approach`, `## Success, pivot, and kill criteria`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: hypothesis_statement
schema_version: "1"
hypothesis_id: HYP-1
target_segment: "..."
problem_or_opportunity: "..."
intervention: "..."
expected_outcome: "..."
primary_measure: "..."
success_criterion: "..."
kill_criterion: "..."
evidence_refs: []
assumptions: []
validation_method: "..."
status: proposed
```

`hypothesis_id`, success criterion, and kill criterion are non-empty. `status` is always `proposed` here; experiment outcomes belong to empirical evidence or later artifacts. Evidence refs support context but never turn a proposed hypothesis into a validated result.


`validation_method` is a candidate evidence source, not an experiment command. Prefer existing evidence, inspection, verification, owner/external evidence, a bounded probe, or reversible normal use when sufficient. Name an experiment only when experiment warrant has been established outside this Skill.
