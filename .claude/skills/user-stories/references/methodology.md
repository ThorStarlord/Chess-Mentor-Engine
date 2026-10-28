# User-stories methodology

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/user-stories.md`.

## Story form

Use Mike Cohn-style `As a / I want / So that` when it captures a real actor and user value. The `So that` clause matters because it preserves intent when implementation details change.

Do not fabricate a persona merely to fit the grammar. For system/infrastructure work, use a bounded capability/behavior statement while preserving the originating product requirement.

## INVEST review

Review each story for:

- **Independent** — can be reasoned about and delivered without unnecessary coupling;
- **Negotiable** — implementation detail is not prematurely frozen unless required by a constraint;
- **Valuable** — the outcome links to a user/product need;
- **Estimable** — the responsible engineering team could estimate it once technical context is known;
- **Small** — bounded enough to refine/test; split oversized stories by workflow step, rule, actor, state, or outcome;
- **Testable** — observable completion behavior exists.

`Estimable` does not authorize the model to invent an estimate.

## Acceptance intent

Include one or more concise acceptance intents per story, including important error/edge behavior when it is already known. Detailed Given/When/Then scenario coverage belongs to `acceptance-criteria`.

## Traceability

Every story should identify its source requirement, hypothesis/opportunity, or explicit owner direction. Stories introduced only as possible scope expansion must remain labeled as proposed until approval exists.

## Dependencies and sequencing

Record hard prerequisites separately from suggested sequence. A dependency can justify order; arbitrary numbering cannot.

## Claim ceiling

A story list is a delivery-specification artifact. It does not prove that requirements are correct, that engineering accepts an estimate, that a sprint is committed, or that the implementation exists.