---
name: launch-checklist
description: Assess cross-functional launch readiness from supplied product, engineering, design, marketing, sales, support, legal, operations, analytics, risk, and approval evidence. Use for a risk_and_readiness responsibility and produce readiness_report with launch-blocking checks, conditions, rollback/monitoring requirements, and a bounded go/no-go recommendation. Do not mark work complete, approved, tested, scheduled, deployed, or ready without corresponding evidence; a checklist or recommendation never grants launch authority.
---

# Launch checklist

Satisfy a `risk_and_readiness` responsibility by producing `readiness_report`.

## Inputs

Require the launch scope and enough context to identify relevant readiness functions. Accept a PRD, risk analysis, release candidate/build evidence, QA/security/legal/design/operations evidence, GTM material, and explicit owner approvals when available. A launch date or tier may remain unknown rather than invented.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Bind the launch scope, tier if known, target window if known, and evidence/currentness boundary.
3. Inventory supplied evidence before evaluating checklist state.
4. Tailor checks to the launch rather than mechanically requiring every upstream template item.
5. Mark each check `evidence_backed_complete`, `blocked`, `planned`, `unknown`, or `not_applicable` according to durable evidence; never convert absence of evidence into completion.
6. Distinguish launch-blocking conditions from required and advisory work.
7. Preserve missing sign-offs, unresolved risks, unavailable rollback evidence, and unknown operational readiness as explicit conditions or blockers.
8. Form a bounded `go`, `go_with_conditions`, `no_go`, or `not_assessed` recommendation. This is advice, not execution authority.
9. Define proposed rollback triggers and monitoring expectations without claiming they are configured or tested unless evidence says so.
10. Stop when remaining uncertainty would not change the bounded readiness recommendation, or when required evidence/authority is unavailable.
11. Return `readiness_report` and control.

## Boundary

`checklist item present != work complete`, `validator PASS != launch ready`, `go recommendation != launch authorization`, `rollback plan written != rollback tested`, and `target date stated != date committed`.
