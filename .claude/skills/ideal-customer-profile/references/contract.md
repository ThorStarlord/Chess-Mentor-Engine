# Ideal-customer-profile methodology and `ideal_customer_profile` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/ideal-customer-profile.md`.

Retain the useful four-part model (profile/demographics or firmographics, behaviors, Jobs to Be Done, needs/pain points), plus ideal-of-ideal indicators, disqualification criteria, and GTM implications. Treat every numeric firmographic, economic, usage, purchase, or pain claim according to evidence strength rather than filling the template.

## Reasoning alignment

Apply the canonical evidence-governed Reasoning Model without turning the Level-2 ontology into a mandatory runtime schema:

- `observed` means directly supported by a bounded source and requires `evidence_refs`;
- `inferred` means an agent interpretation from evidence and should preserve source lineage when material;
- `hypothesis` means a proposed segment/profile claim retained for investigation;
- `unknown` means unresolved for the current decision.

If current customer evidence conflicts across cohorts/segments, preserve the contradiction or split the scope instead of averaging it into a false single ICP. Do not silently carry customer-fit claims beyond the declared `evidence_window`.

## Human-readable sections

Produce:

- `## Scope and evidence`
- `## Profile`
- `## Behaviors and buying context`
- `## Jobs needs and pains`
- `## Ideal-of-ideal and disqualifiers`
- `## GTM implications`
- `## Validation gaps`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: ideal_customer_profile
schema_version: "1"
status: hypothesis | evidence_backed | mixed
segment: "..."
evidence_window: "..."
evidence_refs: []
profile_claims:
  - id: ICP-C1
    dimension: "company_size"
    value: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
behaviors:
  - id: ICP-B1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
jobs:
  - id: ICP-J1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
pains:
  - id: ICP-P1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
ideal_indicators:
  - id: ICP-I1
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
disqualifiers:
  - id: ICP-D1
    type: hard | soft
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
gtm_implications:
  - id: ICP-G1
    function: product | marketing | sales | customer_success | other
    recommendation: "..."
    source_claim_refs: []
    status: proposed
unresolved_questions: []
```

## Mechanical invariants

- Claim, indicator, behavior, job, pain, disqualifier, and GTM implication IDs are unique across the artifact.
- Any `observed` customer claim requires evidence refs.
- GTM implications remain `status: proposed` and may reference known claim IDs as their basis.
- `status: evidence_backed` requires non-empty top-level evidence refs and at least one observed evidence-bearing customer claim.
- `status: hypothesis` must not contain observed evidence-bearing customer claims; use `mixed` when observed and hypothesized material coexist.

The validator establishes representation integrity only. It does not decide which customers are actually ideal, whether a correlation causes value, whether a hard disqualifier should become policy, or whether a GTM recommendation should be executed.
