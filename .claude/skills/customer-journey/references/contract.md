# Customer-journey methodology and `journey_map` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/customer-journey.md`.

Retain stage mapping, touchpoints, actions, questions, emotions, pain points, opportunities, Aha Moments, Moments of Truth, and Churn Triggers. Treat the upstream seven-stage Awareness-to-Advocacy sequence as a heuristic: a bounded journey may use fewer, differently named, or differently ordered stages.

## Reasoning alignment

Apply the canonical evidence-governed Reasoning Model without turning it into a mandatory universal schema:

- `observed` means directly supported by a bounded source and requires `evidence_refs`;
- `inferred` means an agent interpretation from evidence and should preserve the relevant source lineage when material;
- `hypothesis` means a proposed explanation retained for investigation;
- `unknown` means the claim remains unresolved for the current decision.

These artifact-local values correspond conceptually to the Semantic Architecture epistemic model, but this contract does not make the Level-2 ontology a new Campaign schema.

Do not silently carry current-state journey claims beyond the declared `evidence_window`.

## Human-readable sections

Produce:

- `## Persona and scope`
- `## Evidence inventory`
- `## Journey stages`
- `## Critical moments`
- `## Opportunities and unknowns`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: journey_map
schema_version: "1"
status: hypothesis | evidence_backed | mixed
persona_ref: "..."
scope: "..."
evidence_window: "..."
evidence_refs: []
stages:
  - id: STAGE-1
    name: "Onboarding"
    order: 1
    touchpoints: []
    actions: []
    questions: []
    emotions:
      - value: "uncertain"
        evidence_status: hypothesis | inferred | observed | unknown
        evidence_refs: []
    pain_points: []
    opportunities: []
    metrics:
      - name: "completion_rate"
        value: null
        evidence_status: unknown | proposed | observed
        evidence_refs: []
critical_moments:
  - id: MOMENT-1
    type: aha | moment_of_truth | churn_trigger
    stage_ref: STAGE-1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
recommendations: []
unresolved_questions: []
```

## Mechanical invariants

- Stage and critical-moment IDs are unique.
- Stage order values are unique positive integers.
- Critical moments reference declared stages.
- `observed` emotions, metrics, and critical moments require evidence refs.
- `status: evidence_backed` requires top-level evidence refs and at least one observed evidence-bearing journey claim.
- `status: hypothesis` must not contain observed evidence-bearing journey claims; use `mixed` when observed and hypothesized material coexist.

The validator establishes representation integrity only. It does not decide whether stages are complete, emotions are representative, a moment is causally important, or a recommendation should be prioritized.
