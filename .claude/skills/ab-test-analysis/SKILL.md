---
name: ab-test-analysis
description: Analyze supplied controlled-experiment observations with setup-integrity checks, effect estimates, uncertainty, guardrails, practical significance, and a bounded recommendation. Use for experimentation responsibility and produce test_results. Requires real observation/data evidence for a measured conclusion; without it return insufficient_evidence. Do not invent sample sizes, conversions, p-values, confidence intervals, power, guardrail values, or declare a winner from a plan alone.
---

# A/B test analysis

Satisfy an `experimentation` responsibility by producing `test_results`.

## Inputs

Require an experiment definition/hypothesis plus actual control/treatment observations or a durable statistical result source. Prefer the corresponding `experiment_plan` and raw/aggregated observation references.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Reconstruct the preregistered primary metric, guardrails, split, duration, MDE/sample plan, and decision criteria when available.
3. Check setup integrity: sample counts, exposure, SRM/randomization evidence, duration/cycle coverage, peeking/multiple-comparison concerns, and data completeness.
4. Analyze the supplied metric using an appropriate declared method. Preserve raw inputs and calculation provenance.
5. Separate statistical uncertainty from practical/product significance.
6. Evaluate guardrails and important segment heterogeneity without fishing for an unplanned winner.
7. Return `ship`, `investigate`, `extend`, `stop`, `do_not_ship`, or `insufficient_evidence` as an analysis recommendation only.
8. If the recommendation is `investigate` or `extend`, name the unresolved evidence need. Do not treat that recommendation as automatic warrant for another experiment; a continuation experiment must pass Experiment Economy again.
9. Return control; no rollout/external action is authorized.

## Boundary

```text
statistical significance != product value
recommendation != rollout authority
extend recommendation != experiment warrant
investigate recommendation != experiment warrant
experiment plan != observed result
```

Returned evidence may justify reassessment; it does not self-authorize experiment continuation.
