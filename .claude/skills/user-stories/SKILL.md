---
name: user-stories
description: Decompose an approved or explicitly proposed product specification into small user-valued stories with traceability, INVEST review, dependencies, uncertainty, and testable acceptance intent. Use when the active agent has a delivery_specification responsibility and needs a story_list from a PRD or bounded feature definition. Do not invent engineering estimates, implementation commitments, or user evidence.
---

# User stories

Satisfy a `delivery_specification` responsibility by producing `story_list`.

## Inputs

Prefer a canonical `prd` or other bounded feature specification plus relevant persona/segment and constraint evidence. If source scope is still awaiting approval, preserve that status in the stories rather than silently promoting proposed expansion.

## Procedure

1. Read [references/methodology.md](references/methodology.md).
2. Identify the user-valued outcomes and source requirements that need decomposition.
3. Produce stories in `As a / I want / So that` form when that representation fits the work; do not force fake end-user personas onto infrastructure-only requirements.
4. Review each story against INVEST: independent enough to reason about, negotiable, valuable, estimable by the responsible team, small enough for bounded delivery, and testable.
5. Preserve source traceability from each story to the PRD/feature requirement or evidence-backed user need.
6. Record dependencies and open questions explicitly. Do not convert dependencies into hidden sequencing authority.
7. Include acceptance intent sufficient for understanding, but leave detailed scenario enumeration to `acceptance-criteria`.
8. Do not invent story points, day estimates, sprint commitments, technical design, or priority evidence.
9. Render [references/output-contract.md](references/output-contract.md) and return control.

## Stop or downgrade

- If source scope is materially ambiguous, preserve unresolved questions instead of fabricating stories that imply approval.
- If a proposed expansion is still pending approval, mark affected stories `proposed` and do not present them as committed scope.
- If detailed acceptance behavior is the active responsibility, return control for `acceptance-criteria` rather than duplicating it here.

## Boundary

`story decomposition != implementation plan`, `INVEST review != engineering estimate`, and `story order != delivery commitment`.
