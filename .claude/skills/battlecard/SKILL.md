---
name: battlecard
description: Create an evidence-aware competitive battlecard for a named product, competitor, and segment using current market, product, pricing, review, and win-loss evidence. Use for a commercial_strategy responsibility and produce battlecard with honest comparison claims, where-we-win/lose context, objections, discovery questions, and talk tracks. Do not invent competitor capabilities, pricing, funding, customer outcomes, win rates, weaknesses, or superiority claims; stale or unsupported claims remain inferred, hypothesized, unknown, or explicitly out of date.
---

# Competitive battlecard

Satisfy a `commercial_strategy` responsibility by producing `battlecard`.

## Inputs

Require our product, named competitor, segment/context, and an evidence/currentness cutoff. Prefer current `market_analysis`, product evidence, public competitor sources, reviews, pricing evidence, and real win/loss evidence when available.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Bind the competitor, segment, evidence cutoff, and source scope before comparing claims.
3. Inventory claims about us, the competitor, the market, and win/loss behavior with explicit evidence status.
4. Separate direct source observations from agent inference and hypotheses; mark stale or unresolved claims instead of updating them from memory.
5. Build comparisons only from declared claim IDs and preserve `unknown` where evidence does not support a winner.
6. Describe where we win and where they win honestly; do not convert absence of competitor evidence into our advantage.
7. Draft objection responses and discovery questions from supported claims. Avoid misleading, pejorative, fabricated, or unsupported talk tracks.
8. Preserve validity/currentness boundaries so future users know when the card needs refresh.
9. Stop when further research would not change the bounded enablement decision, or when required evidence is unavailable/outside authority.
10. Return `battlecard` and control.

## Boundary

`competitive claim != current fact without source`, `comparison != objective superiority`, `talk track != customer truth`, `landmine != permission to mislead`, and `artifact valid != seller should use every statement`.
