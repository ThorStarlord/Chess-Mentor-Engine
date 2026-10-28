# PMF measurement methodology and pmf_report contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/measure-pmf.md`.

Retain segment-specific assessment, Sean Ellis survey, retention curves/cohorts, qualitative benefit analysis, reference-customer/organic-pull signals, and unit-economics context. Treat the upstream stage thresholds as heuristics, not deterministic truth.

Produce: `## Segment and evidence window`, `## Evidence inventory`, `## Survey and retention signals`, `## Qualitative organic and economics signals`, `## Assessment`, `## Next evidence and limitations`, `## Machine-readable handoff`.

```yaml
artifact_id: pmf_report
schema_version: "1"
status: measured | partial | not_measured
segment: "..."
evidence_window: "..."
survey:
  response_count: 0
  very_disappointed_count: 0
  very_disappointed_share: null
  evidence_refs: []
retention_signals: []
organic_signals: []
qualitative_signals: []
economics_signals: []
assessment: nascent | developing | strong | extreme | insufficient_evidence
assessment_basis: []
limitations: []
next_evidence: []
```

If survey counts are present, `very_disappointed_share` must equal count/response_count. `status: measured` requires non-empty empirical evidence refs and a non-`insufficient_evidence` assessment; the validator does not itself decide which PMF stage is semantically warranted. If no usable evidence exists, status must be `not_measured` and assessment `insufficient_evidence`.