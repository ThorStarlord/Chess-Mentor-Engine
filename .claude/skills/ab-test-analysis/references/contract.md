# A/B-test methodology and test_results contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/ab-test-analysis.md`.

Retain setup validation, SRM awareness, primary-metric discipline, appropriate statistical methods, interval estimates, guardrails, practical significance, and cautious interim/multiple-comparison handling. Statistical thresholds such as p < .05 are not universal defaults; use preregistered or explicitly chosen methods and record them.

Produce: `## Experiment and observations`, `## Setup integrity`, `## Primary analysis`, `## Guardrails and segments`, `## Interpretation`, `## Recommendation and limitations`, `## Machine-readable handoff`.

```yaml
artifact_id: test_results
schema_version: "1"
status: analyzed | insufficient_evidence
experiment_ref: "..."
observation_refs: []
primary_metric: "..."
control: {n: null, value: null}
treatment: {n: null, value: null}
method: "..."
effect_estimate: null
uncertainty: {kind: "...", lower: null, upper: null, p_value: null}
setup_integrity: {status: pass | concern | fail | unknown, concerns: []}
guardrails: []
recommendation: ship | investigate | extend | stop | do_not_ship | insufficient_evidence
limitations: []
```

`status: analyzed` requires at least one observation reference, positive control/treatment sample sizes, a primary metric, and an explicit method. Without observation evidence, status and recommendation must be `insufficient_evidence`; no p-value/effect/winner may be fabricated.