# Pricing methodology and pricing_model contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/pricing.md`.

Retain comparison of pricing-model families, value metric, packaging/tiers, competitive context, WTP investigation, economics, and conditional experimentation. Treat upstream rules such as fixed annual-discount bands, self-serve ceilings, feature-WTP ratios, and illustrative competitor prices as hypotheses/heuristics—not defaults.

Produce: `## Value and segment evidence`, `## Pricing-model options`, `## Competitive and willingness-to-pay evidence`, `## Proposed packaging`, `## Economics and assumptions`, `## Experiment plan and risks`, `## Recommendation and authority boundary`, `## Machine-readable handoff`.

```yaml
artifact_id: pricing_model
schema_version: "1"
status: proposed
segment: "..."
value_metric: {name: "...", evidence_status: hypothesis, evidence_refs: []}
model_options: []
recommended_model: "..."
competitor_claims: []
wtp_evidence: []
tiers:
  - id: TIER-1
    name: "..."
    price: null
    price_status: unknown | proposed | observed_current
    evidence_refs: []
economics:
  evidence_status: unknown | observed | hypothesis
  evidence_refs: []
  values: {}
experiments: []
external_change_authority_ref: null
unresolved_questions: []
```

Observed current prices/economics/competitor claims require evidence refs. `status` remains `proposed`. `external_change_authority_ref` may record authority if separately granted, but the artifact itself never performs or certifies a price change.

`experiments` is a conditional proposal surface, not a required output. Keep it empty unless Experiment Economy has established experiment warrant for the underlying decision-changing pricing uncertainty. When warrant is absent, record the unresolved question or cheaper evidence source instead of creating an experiment merely because an assumption is high-risk.
