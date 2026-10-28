# Stakeholder-update methodology and `stakeholder_update` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/stakeholder-update.md`.

Retain executive-summary structure, situation/impact/analysis, options/recommendation, next steps, risks, and clear decision requests. Replace the upstream assumption that notes are current facts with explicit currentness/evidence/authority semantics.

## Epistemic and authority rules

The artifact may use lower-case forms of the canonical Semantic Architecture statuses for consequential claims:

`observed`, `derived`, `inferred`, `hypothesized`, `ratified`, `unresolved`.

Observed and derived claims require evidence refs; derived claims also name a derivation rule when material. Ratified claims/decisions require an authority reference. Inference does not become ratified merely because it is written confidently.

Proposed owner roles and dates are coordination proposals. They become assignments/commitments only when an authority reference is supplied. The artifact itself does not send the update.

## Human-readable sections

Produce:

- `## Audience and currentness`
- `## Executive summary`
- `## Situation and evidence`
- `## Analysis and decisions`
- `## Next steps`
- `## Risks and unresolved questions`
- `## Distribution boundary`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: stakeholder_update
schema_version: "1"
status: draft
audience: "..."
purpose: inform | decision_request
as_of: "..."
source_refs: []
claims:
  - id: SU-C1
    statement: "..."
    epistemic_status: observed | derived | inferred | hypothesized | ratified | unresolved
    evidence_refs: []
    derivation_rule: null
    authority_ref: null
decisions:
  - id: SU-D1
    statement: "..."
    status: proposed | ratified
    authority_ref: null
next_steps:
  - id: SU-N1
    action: "..."
    owner_role: "..."
    timing: null
    commitment_status: proposed | ratified
    authority_ref: null
risks:
  - id: SU-R1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
decision_request: null
publication_state: draft
unresolved_questions: []
```

## Mechanical invariants

- IDs are unique within each collection.
- `status` and `publication_state` remain `draft`.
- `observed` and `derived` claims require evidence refs.
- `derived` claims require a non-empty `derivation_rule`.
- `ratified` claims and decisions require `authority_ref`.
- Ratified next-step commitments require `authority_ref`; proposed owner roles are not assignments.
- Observed risks require evidence refs.
- `purpose: decision_request` requires a non-empty `decision_request`.

The validator does not decide whether an executive narrative is complete, whether evidence justifies the recommendation, whether a metric change is causal, or whether stakeholders should accept the proposed next step.
