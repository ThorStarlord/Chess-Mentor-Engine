# Release-notes methodology and `feature_announcement` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/release-notes.md`.

Retain benefit-oriented language, impact-first ordering, feature/fix/performance/known-issue grouping, calls to action, and audience-appropriate formatting. Replace the upstream assumption that listed tickets/features necessarily shipped with explicit release evidence.

## Evidence and authority rules

`shipped` and `beta` availability require durable evidence refs. A fix is not complete because a ticket says so. An observed performance improvement requires measurement evidence. Expected user value may be communicated only as proposed/expected rather than observed. Future work remains planned unless a competent authority has ratified a commitment.

The generated artifact is a draft. Publishing, emailing, posting, scheduling, or changing public documentation remains external action.

## Human-readable sections

Produce:

- `## Audience and release scope`
- `## Source evidence`
- `## Headline and summary`
- `## Changes and user value`
- `## Fixes performance and known issues`
- `## Coming soon and commitments`
- `## Publication boundary and unknowns`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: feature_announcement
schema_version: "1"
status: draft
audience: "..."
as_of: "..."
release_evidence_refs: []
items:
  - id: ANN-1
    type: feature | fix | performance | known_issue | coming_soon
    title: "..."
    statement: "..."
    user_benefit: "..."
    availability: shipped | beta | planned | unknown
    claim_status: observed | proposed | unknown
    evidence_refs: []
    commitment_status: proposed | ratified
    authority_ref: null
cta: null
publication_state: draft
publication_authority_ref: null
unresolved_questions: []
```

## Mechanical invariants

- Item IDs are unique.
- `status` and `publication_state` remain `draft` in this capability.
- Items marked `shipped` or `beta` require non-empty evidence refs and `claim_status: observed`.
- `claim_status: observed` requires evidence refs for every item type.
- `coming_soon` items cannot be marked `shipped` or `beta`.
- `commitment_status: ratified` requires `authority_ref`; otherwise future commitments remain proposed.
- `publication_authority_ref` may record supplied permission but does not convert the draft into a sent/published state.

The validator does not determine whether wording is persuasive, whether a benefit follows causally from implementation, whether deployment evidence covers all users, or whether publication should occur.
