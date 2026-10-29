---
name: opportunity-tree
description: Build an evidence-aware Opportunity Solution Tree from a desired outcome, supplied discovery evidence, and explicit assumptions. Use when the active agent has an opportunity-mapping responsibility and needs to relate outcomes to customer opportunities, candidate solutions, risky assumptions, and learning tests. Produce opportunity_map while keeping unsupported opportunities or scores labeled as assumptions or estimates.
---

# Opportunity tree

Satisfy an `opportunity_mapping` responsibility by producing `opportunity_map`.

## Inputs

Require one desired outcome plus product/customer context. Prefer a `synthesis_report` or other discovery evidence. If multiple desired outcomes are supplied, select one only when existing Campaign or owner evidence establishes priority; otherwise surface the owner decision.

## Procedure

1. Read [references/methodology.md](references/methodology.md).
2. Define one outcome with metric, baseline, and target only when those values are supplied or explicitly estimated.
3. Extract customer opportunities as problems or needs, not features.
4. Bind each evidence-backed opportunity to source evidence; mark unsupported opportunities as assumptions.
5. Score only with declared inputs. Label inferred importance/satisfaction as estimates.
6. Generate multiple materially distinct solution candidates for consequential opportunities when solution exploration is in scope.
7. Identify the riskiest value, usability, viability, or feasibility assumption for candidate solutions.
8. Propose bounded learning tests without claiming they were run.
9. Render [references/output-contract.md](references/output-contract.md) and return control.

## Stop or downgrade

- Do not invent outcome baselines or targets and present them as measured.
- Do not choose among multiple owner-level outcomes without evidence of priority.
- Do not label a branch validated unless actual evidence establishes that state.

## Boundary

A score is a decision aid derived from declared inputs; it is not deterministic truth about opportunity value.
