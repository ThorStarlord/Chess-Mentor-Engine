# Experiment-design methodology and experiment_plan contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/experiment-design.md`.

Retain pretotyping, skin-in-the-game, own-data/YODA, behavior-over-opinion,
controlled A/B design, primary/guardrail metrics, preregistration, kill
criteria, and analysis planning. Treat numerical thresholds from upstream
examples as examples, not defaults.

Experiment-design is downstream of Experiment Economy & Proportional Rigor v1.
It designs an experiment only after experimentation has already been warranted.

```text
uncertainty
!= experiment warrant

experiment-design
!= experiment-warrant selector
```

If the decision to support, decision-changing uncertainty, experiment warrant,
cheaper evidence alternatives considered, or why those alternatives are
insufficient is missing, return control rather than manufacturing an
`experiment_plan`.

## Canonical sections

Produce:

- `## Hypothesis and riskiest assumption`
- `## Method and exposure`
- `## Metrics and evidence plan`
- `## Decision and kill criteria`
- `## Analysis and authority`
- `## Risks and unknowns`
- `## Machine-readable handoff`

These headings remain stable across v1/v2 for compatibility. Canonical new
plans use schema v2 and place the experiment-warrant / efficiency context in
the machine-readable handoff and relevant prose sections.

## Canonical v2 handoff

```yaml
artifact_id: experiment_plan
schema_version: "2"
status: designed
hypothesis_ref: "H-1"
decision_to_support: "What decision this experiment can change"
decision_changing_uncertainty: "The unresolved premise"
experiment_warrant:
  status: warranted
  rationale: "Why experimentation is the lowest-cost sufficient evidence source"
  cheaper_evidence_sources_considered:
    - source: existing_evidence
      disposition: insufficient
      rationale: "Why it cannot answer the decision"
    - source: reversible_build
      disposition: insufficient
      rationale: "Why normal use would not answer cheaply enough"
experiment_type: pretotype | usability | ab_test | other
target_population: "..."
intervention: "..."
primary_metric:
  name: "..."
  baseline: null
  baseline_status: unknown
  evidence_refs: []
guardrails: []
sample_plan:
  size: null
  status: unknown
  method: "..."
duration_plan:
  value: null
  status: unknown
decision_branches:
  - result_class: "supports hypothesis"
    decision_effect: "..."
  - result_class: "does not support hypothesis"
    decision_effect: "..."
decision_criteria:
  go: "..."
  no_go: "..."
  investigate: "..."
kill_criteria: []
total_experiment_cost:
  design: "..."
  setup: "..."
  implementation: "..."
  isolation: "..."
  execution: "..."
  evaluation: "..."
  interpretation: "..."
  documentation: "..."
  delay: "..."
  opportunity_cost: "..."
minimum_required_controls: []
controls_rejected_as_unnecessary: []
analysis_method: "..."
claim_ceiling: "Maximum claim this planned evidence could support"
execution_authority_ref: null
unresolved_questions: []
```

## Decision discrimination

A v2 plan must identify at least two material result classes and what each
would change.

```text
all material outcomes -> same decision
= warrant should be reassessed
```

Mechanical validation can reject exactly identical decision effects. The
semantic agent still owns whether the branches are genuinely decision-distinct.

## Total cost and controls

Total experiment cost includes more than experimental code:

```text
design
+ setup
+ implementation
+ isolation / environment preparation
+ execution
+ evaluation
+ interpretation
+ documentation / evidence packaging
+ delay
+ opportunity cost
```

Use qualitative descriptions; do not invent numeric cost-benefit ratios.

`minimum_required_controls` contains only controls needed to protect the
decision-relevant inference. `controls_rejected_as_unnecessary` may remain
empty, but should record materially considered controls that were deliberately
not purchased.

## Compatibility

Historical `schema_version: "1"` plans remain valid and preserve the original
handoff shape:

```yaml
artifact_id: experiment_plan
schema_version: "1"
status: designed
hypothesis_ref: "..."
experiment_type: pretotype | usability | ab_test | other
target_population: "..."
intervention: "..."
primary_metric: {name: "...", baseline: null, baseline_status: unknown, evidence_refs: []}
guardrails: []
sample_plan: {size: null, status: unknown, method: "..."}
duration_plan: {value: null, status: unknown}
decision_criteria: {go: "...", no_go: "...", investigate: "..."}
kill_criteria: []
analysis_method: "..."
execution_authority_ref: null
unresolved_questions: []
```

A v1 artifact can be revalidated without being rewritten merely because the
current authoring contract became more precise.

## Boundary

`status` is always `designed`; this artifact has no result/winner field.
Observed baselines require evidence refs. External execution authority is
separate and may remain null.

```text
valid v2 representation
!= experiment warranted in reality

experiment plan
!= experiment evidence

planned controls
!= controls actually applied

decision branch
!= future decision automatically selected
```
