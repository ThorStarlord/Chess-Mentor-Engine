---
name: pre-mortem
description: Stress-test a product, feature, delivery plan, or launch by imagining failure and classifying evidence-backed risks, speculative concerns, unspoken uncertainties, urgency, mitigations, owners, and decision conditions. Use for risk_and_readiness responsibility. Produce risk_analysis; do not convert imagined failure modes into factual incidents or make a launch decision without the required authority/evidence.
---

# Pre-mortem

Satisfy a `risk_and_readiness` responsibility by producing `risk_analysis`.

## Inputs

Require a bounded product/feature/plan plus relevant success criteria, dependencies, constraints, target date if actually committed, and available evidence about known issues. A `prd` is a common input but not mandatory.

## Procedure

1. Read [references/methodology.md](references/methodology.md).
2. Establish the target decision and current evidence. Separate known problems from imagined failure modes.
3. Run reverse imagination: assume the initiative failed and enumerate plausible contributing causes across product value, usability, feasibility, viability, operations, security/privacy, legal, GTM, support, dependencies, and organizational readiness as relevant.
4. Classify each item as `tiger`, `paper_tiger`, or `elephant` only with explicit rationale and evidence status.
5. For Tigers, classify urgency as `launch_blocking`, `fast_follow`, or `track` based on consequence and current evidence. Do not make missing evidence look like certainty.
6. Define mitigation, owner role, due condition/date if supplied, and mitigation success criterion for consequential risks.
7. Record signals that would escalate a tracked risk and investigations needed for elephants/uncertain items.
8. Provide an agent-authored recommendation (`go`, `go_with_conditions`, `no_go`, or `insufficient_evidence`) that clearly distinguishes recommendation from execution authority.
9. Render [references/output-contract.md](references/output-contract.md) and return control.

## Stop or downgrade

- If a risk is purely hypothetical, keep its evidence status `hypothetical` instead of labeling it a known Tiger.
- If launch date, owner, impact, or probability is unknown, keep it unknown rather than inventing precision.
- If security, legal, privacy, or other specialist review is required, surface that dependency instead of self-authorizing clearance.
- A `no_go`/`go` recommendation does not itself launch, cancel, publish, or mutate an external system.

## Boundary

`pre-mortem scenario != observed incident`, `risk score != certainty`, and `readiness recommendation != launch authority`.
