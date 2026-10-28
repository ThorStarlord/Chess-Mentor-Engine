# Acceptance-criteria methodology

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/acceptance-criteria.md`.

## BDD-oriented scenarios

Use Given/When/Then as a communication format when it makes preconditions, action, and observable result clearer:

```gherkin
Given <relevant starting state>
When <actor/system action>
Then <observable outcome>
```

Do not treat Gherkin syntax as proof that an automated test exists.

## Coverage categories

Select only categories relevant to the source requirement:

- primary happy path;
- alternate valid flow;
- boundary/edge values;
- invalid input and recovery;
- prior/existing state and re-entry;
- persistence/idempotency where relevant;
- integration side effects;
- accessibility and keyboard/screen-reader behavior when part of the product surface;
- performance/scale when an explicit quality requirement exists.

Avoid cargo-cult scenarios. A mobile scenario, 2-second threshold, WCAG level, or browser matrix must come from a product/domain requirement, not from the upstream example.

## Expected behavior versus open question

If the source does not say what should happen, write an unresolved decision instead of inventing a criterion. Acceptance criteria define agreed behavior; they should not silently become a product-design authority.

## Traceability

Each scenario should reference its source story/requirement. When one source story creates several scenarios, preserve that grouping.

## Claim ceiling

A criteria artifact states what should be accepted. It does not establish that QA ran the scenario, that code exists, or that the result passed.