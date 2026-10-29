---
name: north-star
description: Evaluate candidate North Star Metrics against customer value, durability, vision alignment, measurability, actionability, and leading-indicator qualities; select a proposed metric and input-metric constellation in north_star_metric. Use for product_strategy responsibility. Do not invent baselines, causal relationships, targets, or telemetry availability, and do not treat framework scoring as proof the chosen metric predicts business outcomes.
---

# North Star

Satisfy a `product_strategy` responsibility by producing `north_star_metric`.

## Inputs

Require product value model, target users, business model/stage, strategic direction, and known current metrics. Prefer actual telemetry/evidence when available.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Classify the dominant value-delivery game only as a heuristic: attention, transaction, productivity, or other.
3. Generate a small set of candidate value-delivery metrics.
4. Score candidates against declared criteria, while keeping model judgment distinct from observed evidence.
5. Select a proposed NSM with rationale and explicit uncertainties.
6. Define input metrics and guardrails with hypothesized relationships to the NSM.
7. Preserve unknown baselines, targets, instrumentation, and causal links rather than inventing them.
8. Return `north_star_metric` and control.

## Boundary

`North Star proposal != causal proof`, `input metric relationship != validated causality`, and `target != observed baseline`.
