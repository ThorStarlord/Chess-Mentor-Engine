---
name: prioritize
description: Compare candidate product initiatives using explicit evidence, business context, dependencies, constraints, and optional RICE-style scoring, then produce prioritized_list with transparent trade-offs and uncertainty. Use for prioritization responsibility. Deterministic arithmetic may verify declared scores, but the active agent owns ranking judgment; never invent reach, impact, confidence, effort, capacity, dates, or commitments.
---

# Prioritize

Satisfy a `prioritization` responsibility by producing `prioritized_list`.

## Inputs

Require a bounded set of initiatives plus the goal/context they are being prioritized against. Prefer durable story, hypothesis, strategy, evidence, dependency, and capacity information.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. State the decision context, constraints, and evidence gaps.
3. For each initiative, capture reach, impact, confidence, effort, evidence, dependencies, and strategic fit only when known.
4. Compute RICE when all required numeric inputs are available; otherwise keep score unavailable instead of inventing values.
5. Treat score as one decision input. Explain deviations caused by dependencies, risk, strategic fit, option value, evidence quality, or hard constraints.
6. Recommend `now`, `next`, `later`, or `validate_first` with explicit rationale.
7. Do not create sprint commitments or implementation estimates that the responsible team did not supply.
8. Return `prioritized_list` and control.

## Boundary

`RICE score != priority truth`, `rank != delivery commitment`, and `model-generated effort != engineering estimate`.
