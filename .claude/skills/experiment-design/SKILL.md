---
name: experiment-design
description: Design the smallest sufficiently rigorous, decision-discriminating product experiment after experimentation has already been independently warranted. Use only for an established experimentation responsibility with a testable hypothesis, decision-changing uncertainty, cheaper evidence alternatives considered, target population/context, and experiment warrant. Produce experiment_plan without manufacturing the warrant or execution authority.
---

# Experiment design

Satisfy an already-warranted `experimentation` responsibility by producing
`experiment_plan`.

```text
experiment-design
!= experiment-warrant selector

experiment plan
!= evidence that experimentation was the right evidence source
```

## Inputs

Require all of the following before designing:

- the decision to support;
- the decision-changing uncertainty;
- a testable product hypothesis;
- target population/context;
- an explicit experiment warrant;
- cheaper evidence sources considered;
- why those cheaper sources are insufficient for the current decision/claim.

Prefer `hypothesis_statement` plus known baselines, traffic, constraints, and
evidence.

If the experiment warrant is absent, merely asserted without reconstructible
reasoning, or contradicts an obviously cheaper sufficient evidence source, do
**not** manufacture the warrant and do **not** produce `experiment_plan`.
Return control and name the missing/contradictory warrant context.

Read
`../using-sensemaking/references/experiment-economy-v1.md`
when warrant, experimental isolation, total cost, or confounder control is
material.

External experiment execution remains separately authorized.

## Efficiency objective

Optimize **decision-relevant information per total experiment cost**, subject to
sufficient evidentiary rigor. Require **decision discrimination**: material result
classes should lead to meaningfully different decision effects, or the warrant should
be returned for reassessment.

```text
experimental quality
!= experimental efficiency
```

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Reconstruct the experiment warrant. Confirm the supported decision, decision-changing uncertainty, cheaper evidence sources considered, and why they are insufficient. If this context is missing or self-contradictory, return control without an experiment plan.
3. Identify the riskiest assumption and select the **smallest** method capable of discriminating the decision at the required claim level (for example observation/prototype usability only when that is still properly an experiment, pretotype, or controlled experiment).
4. Define material result classes and what decision each result would change. If every plausible result leads to the same action, return the warrant for reassessment rather than designing a low-discrimination experiment.
5. Define the intervention/exposure and inclusion/exclusion rules.
6. Define one primary decision metric plus relevant guardrails.
7. Preserve baseline, sample-size, duration, budget, and traffic as known, estimated, proposed, or unknown according to evidence.
8. Account qualitatively for **total experiment cost**: design, setup, implementation, isolation/environment preparation, execution, evaluation, interpretation, documentation/evidence packaging, delay, and opportunity cost.
9. Choose **Minimum Sufficient Experimental Rigor**. Add only controls needed to protect the decision-relevant inference; record controls considered but rejected as unnecessary when useful.
10. Preregister decision thresholds and kill/integrity/early-stop criteria before observing results.
11. Define analysis method, evidence capture, owner/authority dependencies, and the maximum claim the planned evidence could support.
12. Return canonical `experiment_plan schema_version: "2"` and control. Do not execute the experiment.

## Boundary

```text
experiment warrant
!= experiment design

experiment design
!= experiment execution

experiment plan
!= experiment evidence

methodologically strong
!= decision-efficient

maximum rigor
!= maximum decision value

proposed sample
!= observed sample

decision threshold
!= result

plan approval
!= external execution authority
```

The Skill owns experiment quality and efficiency **after** warrant exists. It
does not own the upstream decision that experimentation is the cheapest
sufficient evidence source.
