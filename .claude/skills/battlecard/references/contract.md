# Battlecard methodology and `battlecard` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/battlecard.md`.

Retain quick comparison, where-we-win/lose analysis, objections/responses, strategic discovery questions, win/loss patterns, and scan-friendly enablement. Drop Claude invocation assumptions and treat every competitor/current-market claim under an explicit evidence/currentness boundary.

## Evidence and honesty rules

Observed claims require source refs. Inferred comparisons cite the underlying claim IDs. Missing competitor evidence stays unknown; it is never evidence that our product wins. Win/loss patterns require actual win/loss evidence to be marked observed. Talk tracks are proposed enablement language, not independent factual evidence.

## Human-readable sections

Produce:

- `## Scope and currentness`
- `## Evidence inventory`
- `## Competitive claims`
- `## Comparison and where each side wins`
- `## Objections and discovery questions`
- `## Win-loss patterns and unknowns`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: battlecard
schema_version: "1"
status: draft
our_product: "..."
competitor: "..."
segment: "..."
evidence_cutoff: "..."
evidence_refs: []
claims:
  - id: BC-C1
    side: us | competitor | market | win_loss
    statement: "..."
    evidence_status: hypothesis | inferred | observed | unknown
    evidence_refs: []
comparisons:
  - id: BC-X1
    dimension: "..."
    our_claim_ref: BC-C1
    competitor_claim_ref: BC-C2
    assessment: us_advantage | competitor_advantage | parity | unknown
    evidence_status: hypothesis | inferred | unknown
talk_tracks:
  - id: BC-T1
    type: where_we_win | where_they_win | objection_response | discovery_question
    text: "..."
    source_claim_refs: []
    status: proposed
valid_until: null
unresolved_questions: []
```

## Mechanical invariants

- Claim, comparison, and talk-track IDs are unique and distinct within their collections.
- Observed claims require evidence refs.
- Comparisons reference declared claim IDs; `our_claim_ref` must reference a claim whose `side` is `us`, and `competitor_claim_ref` a claim whose side is `competitor` when those refs are present.
- Comparison evidence status cannot be `observed`; the comparison assessment remains an interpretation of declared claims.
- Talk tracks remain `status: proposed` and any source-claim refs resolve to declared claims.
- `status` remains `draft`; publication/distribution approval is outside this artifact.
- `evidence_cutoff` is required so currentness debt is visible. `valid_until` may remain unknown rather than fabricated.

The validator does not determine competitive superiority, whether a seller should use a talk track, whether a source is unbiased, or whether market evidence is sufficiently current for every decision.
