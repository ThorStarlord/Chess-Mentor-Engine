---
name: customer-journey
description: Map a bounded customer journey for a named persona or segment across relevant stages, touchpoints, actions, questions, emotions, pain points, opportunities, metrics, and critical moments while preserving evidence status and currentness. Use for a customer_understanding responsibility and produce journey_map. Do not invent conversion rates, churn triggers, emotions, touchpoints, frequencies, or Aha Moments; unsupported journey claims remain inferred, hypothesized, or unresolved rather than observed.
---

# Customer journey

Satisfy a `customer_understanding` responsibility by producing `journey_map`.

## Inputs

Require a named persona/segment, product or service, journey scope, and an evidence/currentness window. Prefer durable persona, interview, analytics, support, funnel, retention, and touchpoint evidence when available.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Bind the journey scope and evidence window before interpreting behavior.
3. Inventory the available sources and separate direct observations from agent inference and product-team hypotheses.
4. Choose only the stages warranted by the scoped journey. Treat the upstream Awareness-to-Advocacy sequence as a heuristic, not a mandatory ontology.
5. For each stage, describe touchpoints, actions, questions, emotions, pain points, opportunities, and metrics at the evidence strength actually supported.
6. Preserve material contradictions or missing evidence as unresolved questions instead of smoothing them into a complete-looking journey.
7. Identify `aha`, `moment_of_truth`, and `churn_trigger` moments only at their supported epistemic status.
8. Recommend investigation or improvement opportunities without inventing impact, effort, priority, or causal effect.
9. Stop when remaining uncertainty would not change the bounded next decision, or when additional evidence is unavailable/outside authority.
10. Return `journey_map` and control.

## Boundary

`journey hypothesis != observed behavior`, `emotion guess != customer evidence`, `critical moment hypothesis != causal churn evidence`, `recommendation != roadmap priority`, and `artifact valid != journey true`.
