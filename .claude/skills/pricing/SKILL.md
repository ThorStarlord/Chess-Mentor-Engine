---
name: pricing
description: Develop an evidence-aware pricing and packaging recommendation from customer value, segment, business stage, current model, competitive pricing evidence, willingness-to-pay evidence, cost/unit-economics inputs, and experiment options. Use for commercial_strategy responsibility and produce pricing_model. Never invent competitor prices, willingness to pay, ROI, CAC/LTV, margins, tier conversion, discounts, or revenue targets; recommendation never authorizes an external price change.
---

# Pricing

Satisfy a `commercial_strategy` responsibility by producing `pricing_model`.

## Inputs

Require product, target segment, delivered value hypothesis, stage, and current pricing state if one exists. Prefer current `market_analysis`, customer/WTP research, unit-economics evidence, and strategy context.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Map the value delivered and candidate value metric without inventing ROI.
3. Compare applicable model families (flat, seat, usage, tiered, freemium, hybrid, value-based, or other) as options rather than defaults.
4. Use competitor pricing only from dated source evidence.
5. Use willingness-to-pay methods only when actual interview/survey/transaction evidence exists; otherwise mark WTP unknown.
6. Propose packaging/tiers and economics assumptions with explicit evidence status.
7. Identify the decision-changing evidence needs behind the highest-risk pricing assumptions and compare candidate evidence sources by total cost. Populate experiment proposals only when Experiment Economy establishes that experimentation is the lowest-cost sufficient source.
8. Otherwise keep the experiment proposal surface empty and record the unresolved evidence need / cheaper source instead of manufacturing an experiment.
9. Return `pricing_model` and control. Any actual pricing/publishing change requires separate authority.

## Boundary

```text
pricing uncertainty != experiment
high-risk assumption != experiment requirement
pricing recommendation != experimentation responsibility
pricing recommendation != price-change authority
competitor benchmark != WTP evidence
value hypothesis != ROI observation
unit-economics target != actual economics
```

Apply `../using-sensemaking/references/experiment-economy-v1.md` before proposing pricing experiments.
