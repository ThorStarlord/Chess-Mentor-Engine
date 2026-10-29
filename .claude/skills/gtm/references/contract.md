# GTM methodology and `gtm_plan` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/gtm.md`.

Retain positioning, channel strategy, message adaptation, timeline, metrics/success criteria, scenarios, and contingencies. Treat numeric examples and channel tactics as heuristics, not evidence.

## Evidence and authority rules

Observed positioning/customer/channel claims and observed metric baselines require durable evidence. Expected reach, conversion, revenue, adoption, or other outcomes are proposals/hypotheses unless supplied as observed historical evidence. A plan can record ratified commitments only when an authority reference is supplied.

External actions remain outside this artifact: outreach, publishing, campaign activation, ad spend, event scheduling, and pricing changes are not executed by generating `gtm_plan`.

## Human-readable sections

Produce:

- `## Objective and audience`
- `## Evidence and positioning`
- `## Channel strategy`
- `## Messaging`
- `## Timeline and coordination`
- `## Metrics and contingencies`
- `## Authority and unknowns`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: gtm_plan
schema_version: "1"
status: proposed
offer: "..."
target_segment: "..."
objective: "..."
evidence_window: "..."
evidence_refs: []
positioning_claims:
  - id: GTM-C1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
channels:
  - id: GTM-CH1
    name: "..."
    rationale: "..."
    source_claim_refs: []
    status: proposed
messages:
  - id: GTM-M1
    audience: "..."
    text: "..."
    source_claim_refs: []
    status: proposed
metrics:
  - id: GTM-K1
    name: "..."
    baseline: null
    baseline_status: unknown | observed
    baseline_evidence_refs: []
    target: null
    target_status: proposed | ratified
    target_authority_ref: null
timeline:
  - id: GTM-T1
    action: "..."
    timing: null
    commitment_status: proposed | ratified
    authority_ref: null
    external_action: true
contingencies: []
external_execution_authority_ref: null
unresolved_questions: []
```

## Mechanical invariants

- IDs are unique within each collection.
- Observed positioning claims require evidence refs.
- Channel/message source-claim refs resolve to declared positioning claims when supplied.
- Observed baselines require baseline evidence refs.
- Metric targets cannot be marked observed; `ratified` targets require `target_authority_ref`.
- Ratified timeline commitments require `authority_ref`.
- Channel, message, and timeline entries remain plan representations; no `executed`, `sent`, `published`, `launched`, or equivalent completion state is valid.
- `external_execution_authority_ref` records supplied permission only and does not change plan entries into executed actions.

The validator establishes representation integrity only. It does not decide channel fit, message quality, budget allocation, causal effectiveness, or market success.
