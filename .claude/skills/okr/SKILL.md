---
name: okr
description: Convert strategy and measurable outcomes into a bounded OKR set with qualitative objectives, outcome-oriented key results, explicit baselines/targets, owner roles, alignment, evidence status, and review cadence. Use for product_strategy responsibility and produce okr_list. Do not invent baselines, owners, financial targets, current scores, or treat initiatives/features as achieved outcomes.
---

# OKR

Satisfy a `product_strategy` responsibility by producing `okr_list`.

## Inputs

Require the strategy/outcomes being operationalized, planning cycle, relevant measures, and known ownership. Prefer `strategy_doc`, `north_star_metric`, and actual metric evidence when available.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Define a small number of qualitative objectives connected directly to strategy.
3. Define measurable outcome KRs; separate supporting initiatives from KRs.
4. Preserve baseline/target evidence status. Unknown baselines stay unknown.
5. Use owner roles when a specific authorized owner is not supplied; never invent names.
6. Add alignment links and a review cadence without fabricating current progress.
7. Return `okr_list` and control.

## Boundary

`OKR target != forecast`, `initiative != key result`, `proposed owner role != assignment`, and `defined OKR != achieved outcome`.
