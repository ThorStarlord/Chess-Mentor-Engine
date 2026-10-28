---
name: measure-pmf
description: Assess Product-Market Fit signals by segment using supplied Sean Ellis survey responses, retention/cohort evidence, reference-customer evidence, organic pull, qualitative feedback, and unit-economics evidence. Use for product_measurement responsibility and produce pmf_report. A measured PMF classification requires actual preserved evidence; without sufficient observations return not_measured or insufficient_evidence rather than inferring PMF from framework thresholds or growth anecdotes.
---

# Measure PMF

Satisfy a `product_measurement` responsibility by producing `pmf_report`.

## Inputs

Require product/segment context and an inventory of actual available evidence. Sean Ellis survey, retention, NPS, organic growth, reference-customer, and unit-economics evidence are optional inputs individually; absence must stay visible.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Scope the assessment to a named segment and time window.
3. Inventory evidence sources before applying any framework.
4. Compute Sean Ellis share only from supplied response counts; preserve sample size and eligibility caveats.
5. Describe retention/cohort, referral/organic, qualitative, and economics signals only from supplied evidence.
6. Distinguish contradictory signals instead of averaging them into false certainty.
7. Classify `measured` only when the minimum evidence required by the chosen assessment method exists; otherwise use `partial` or `not_measured`.
8. Recommend next evidence/action without claiming scale readiness or PMF as fact beyond the observations.
9. Return `pmf_report` and control.

## Boundary

`40% heuristic != universal PMF proof`, `growth != PMF`, `NPS != PMF`, and `PMF assessment != authority to scale spend or fundraising claims`.
