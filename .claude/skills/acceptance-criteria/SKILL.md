---
name: acceptance-criteria
description: Turn a bounded user story, feature rule, or delivery requirement into explicit testable acceptance scenarios covering happy paths, edge cases, errors, state transitions, integration effects, accessibility, performance, and other relevant constraints. Use for delivery_specification responsibility when detailed behavioral criteria are needed. Produce criteria_list; do not invent product rules or claim scenarios have passed.
---

# Acceptance criteria

Satisfy a `delivery_specification` responsibility by producing `criteria_list`.

## Inputs

Require one or more bounded stories/features plus known business rules and constraints. Prefer `story_list` and the source `prd` when available.

## Procedure

1. Read [references/methodology.md](references/methodology.md).
2. Identify the observable behavior actually required by the source story/feature.
3. Write scenario-oriented criteria using Given/When/Then where it improves precision.
4. Cover the happy path, relevant valid variations, error behavior, and consequential boundary conditions.
5. Add performance, accessibility, scale, persistence, security, or integration criteria only when the source requirement or domain evidence warrants them.
6. Trace each scenario to its source story/requirement.
7. Separate known requirements from open design/product questions. Do not resolve ambiguity by inventing rules.
8. Do not mark scenarios as passed, automated, QA-approved, or signed off without execution evidence.
9. Render [references/output-contract.md](references/output-contract.md) and return control.

## Stop or downgrade

- If the source story is not bounded enough to determine expected behavior, preserve the ambiguity as an unresolved question.
- If a criterion would introduce new product scope, identify it as proposed rather than silently incorporating it.
- If verification requires external systems or performance measurements not available now, specify the criterion but do not claim it passed.

## Boundary

`acceptance criterion != test result`, `scenario coverage != implementation`, and `specified quality threshold != measured performance`.
