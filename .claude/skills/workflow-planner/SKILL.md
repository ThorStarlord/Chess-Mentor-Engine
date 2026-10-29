---
name: workflow-planner
description: read a repository sensemaking brief and produce a machine-readable workflow orchestration plan (a planning recommendation for the active agent, not execution authority).
---

# workflow-planner

This skill produces a **workflow orchestration plan** artifact. It does **not** execute workflows, run steps, manage gates, validate artifacts, or invoke other skills. Under the ratified agent-native model (ADR 0013), the active agent owns the control loop; the plan is a planning recommendation, not execution authorization.

If the active agent selects a registered workflow for execution, `workflow-runtime.py` (the Python execution engine) is bounded orchestration/compatibility machinery: it reads the plan's `chosen_workflow_id` to sequence the selected workflow's steps. Workflow selection remains the agent's (or user's) decision; a plan recommendation never by itself authorizes execution.

ADR 0027 adds a second necessary distinction: **registered is not the same as currently selectable**. `workflow-registry.yaml` is the durable catalog; `references/workflow-liveness.yaml` declares which catalog entries are `active` versus `compatibility_only`. Compatibility-only IDs may be discussed as history/provenance but MUST NOT be recommended, selected, planned, or executed as current capabilities. In the RC4 simplification line, `fast-path-workflow` is compatibility-only because its historical auto-chaining claim does not match current runtime behavior.

## Workflow

1. **Consume Brief**: Review the diagnostic brief from `repo-sensemaker`.
2. **Read Current Liveness**: Read `references/workflow-liveness.yaml` and resolve the effective liveness of any candidate workflow. Unlisted workflows default to `active`; `compatibility_only` is never eligible for a current plan.
3. **Recommend Workflow**: Map the warranted path to an **active** workflow in `workflow-registry.yaml`, as a recommendation. Catalog membership alone is insufficient.
4. **Plan**: Produce a Workflow Orchestration Plan with the chosen active workflow, ordered steps, and approval gates.
5. **Mode Selection**: Determine the execution mode (default: `plan_only`).

If a former conventional/default workflow is `compatibility_only` and no active replacement is explicitly warranted, do **not** silently substitute a different workflow. Preserve the no-match state and return control for Sensemaking/owner selection or escalation.

## Stage 2: Routing Audit

**Routing Audit Fields** track the gap between what the system recommended and what was actually chosen. In `guided_execution` mode these fields document the human/agent decision; they record a recommendation, they do not confer execution authority.

### Recording Routing Decisions

**Step 1: Capture System Recommendation**
- Read `recommended_workflow_id` from the repository sensemaking brief.
- Resolve that ID against both `workflow-registry.yaml` and `workflow-liveness.yaml`.
- If it is `active`, record it as `system_recommended_workflow` in the plan.
- If it is `compatibility_only`, preserve it only as historical/input evidence; it is not an eligible current recommendation or selection.
- The recommendation is planning metadata, not execution authority.

**Step 2: Determine User/Agent Selection**
- A current `chosen_workflow_id` MUST resolve to `active`.
- If in `guided_execution` mode and the user is presented a choice, record their explicit active selection.
- If user explicitly overrides the recommendation, record the selected active workflow.
- If no active selection is warranted, do not invent one; preserve/escalate the no-match state.
- Record the final selection as `selected_workflow` and the plan's authoritative field `chosen_workflow_id` only when a live selection exists.

**Step 3: Calculate Routing Divergence**
- `routing_divergence: true` if `system_recommended_workflow != selected_workflow`.
- `routing_divergence: false` if they match.

**Step 4: Record Decision Method**
Valid `routing_decision_method` values:
- `diagnosis_primary_soft_context` — System recommendation based on primary fog type; user intent confirmed (no override)
- `diagnosis_mixed_tiebreak_to_user_intent` — Diagnosis showed mixed fog; user intent broke the tie
- `user_explicit_override` — User explicitly selected different workflow than system recommended
- `escalation_recommended_accepted` — System recommended escalation to full-fog-workflow; user accepted
- `escalation_recommended_rejected` — System recommended escalation; user stayed with narrower workflow

**Example Scenarios:**

*Scenario A: Agreement on an active workflow*
```yaml
system_recommended_workflow: full-fog-workflow
selected_workflow: full-fog-workflow
routing_divergence: false
routing_decision_method: diagnosis_primary_soft_context
```

*Scenario B: User Override to another active workflow*
```yaml
system_recommended_workflow: full-fog-workflow
selected_workflow: docs-contract-reconciliation
routing_divergence: true
routing_decision_method: user_explicit_override
```

*Scenario C: Compatibility-only recommendation arrives from older evidence*
```text
brief recommendation = product-implementation-workflow
liveness = compatibility_only
current chosen_workflow_id = NOT SET BY THIS FACT ALONE
next responsibility = choose an active workflow explicitly or preserve/escalate no-match
```

### Escalation in Routing Audit

When `escalation_recommended: true` in the brief:
- Resolve the recommended escalation path against current liveness.
- If `full-fog-workflow` or another recommended path is active, it may be recorded as the system recommendation.
- If user accepts an active recommendation: selected matches system, `routing_divergence: false`, `decision_method: escalation_recommended_accepted`.
- If user rejects and selects another active workflow: `routing_divergence: true`, `decision_method: escalation_recommended_rejected`.
- If the only recommendation is compatibility-only, do not convert historical metadata into a current route.

Always include `escalation_recommended` and `auto_escalation_allowed` from brief. `escalation_recommended` informs the human/agent decision; it does not itself authorize automatic escalation. Users/agents always control final selection.

## Plan Content

The plan must include a `chosen_workflow_id` field in its machine-readable section **when a current workflow has actually been selected**. That field must name an `active` workflow. `recommended_workflow_id` belongs to the repository sensemaking brief as planning evidence; it is not sufficient by itself to establish liveness or execution authority.

Workflow selection guidance (planning aid only; not automatic routing):
- Read `primary_fog_type` from the repository sensemaking brief (always canonical form per canonical-vocabulary.yaml).
- Read `workflow-registry.yaml` for catalog identity and `workflow-liveness.yaml` for current eligibility.
- `docs-implementation-workflow` is currently active and may be considered for `docs_fog` when its responsibility actually fits.
- Historical mappings to `product-implementation-workflow`, `ui-implementation-workflow`, `implementation-workflow`, and `architecture-implementation-workflow` are **not current defaults** while those workflows are `compatibility_only`.
- Do not silently invent replacement product/UI/architecture routes. Select another active workflow only when current evidence and authority independently warrant it.
- An explicit `recommended_workflow_id` from the brief may be considered only if it is currently active.
- If no active registered workflow fits, preserve the no-match/escalation state rather than choosing a compatibility-only ID.
- The active agent (or user) then selects the workflow; the plan records that decision as `chosen_workflow_id`. A recommendation is not execution authorization.

**CRITICAL**: The four canonical fog types are `product_fog`, `ui_fog`, `docs_fog`, `architecture_fog`. `integration_fog` is NOT a canonical fog type in this model.
Validators normalize aliases (e.g., "ui" -> "ui_fog", "product" -> "product_fog") before artifact storage.
Downstream consumers (including this skill) always receive and must emit canonical values only.
Reference `docs/canonical-vocabulary.yaml` for fog type definitions and aliases.

## Output Format

Every response must follow the [Workflow Orchestration Plan](references/workflow-orchestration-template.md) structure.

**CRITICAL**: Every finalized plan MUST include the **Section 11: Machine-readable plan** YAML block containing a current active `chosen_workflow_id`. If no active selection is warranted, stop before falsely finalizing a plan and surface the no-match/escalation state instead.

## Boundary Rules

- **Plan-only Mode**: Default to `plan_only` mode unless explicitly requested otherwise. In `plan_only` mode, set Section 9 to: `N/A - mode is plan_only. No prompt chain generated.`
- **Machine Verifiability**: Every finalized plan MUST generate Section 11 (Machine-readable plan). Failure to do so renders the artifact non-verifiable.
- **Catalog vs Liveness**: A known workflow ID can be structurally valid historical data while being ineligible for current planning. Current recommendations and selections MUST be `active` under `workflow-liveness.yaml`.
- **No Silent Replacement**: A compatibility-only former default does not authorize the planner to choose a different workflow. New selection requires current evidence/authority.
- **Handoff Compliance**: A finalized plan's chosen workflow must be both registered in `workflow-registry.yaml` and `active` under `workflow-liveness.yaml`.
- **Path Normalization**: All artifact paths in the plan MUST use relative paths. Never use absolute `file:///` links.

## References
- [Canonical Vocabulary Registry](../../docs/canonical-vocabulary.yaml) — Authoritative fog types, catalog workflow IDs, and routing field definitions
- [Workflow Orchestration Template](references/workflow-orchestration-template.md)
- [Skill Registry](references/skill-registry.yaml)
- [Workflow Registry](references/workflow-registry.yaml) — durable workflow catalog
- [Workflow Liveness](references/workflow-liveness.yaml) — current active vs compatibility-only eligibility (ADR 0027)
- [Artifact Contracts](references/artifact-contracts.yaml)
- [Execution Modes](references/execution-modes.md)
- [ADR 0027](../../docs/adr/0027-workflow-registry-liveness.md)

## Execution Protocol

When executing as part of a workflow run:

1. Read the provided run_id, step_id, input artifacts, and expected artifact_id.
2. Call `scripts/run-ledger.py start-step`.
3. The runtime already resolved the output path and passed it as `expected_output_path` in context — use that path verbatim. Never call `scripts/create-artifact.py` (or otherwise recompute a path) during a runtime-invoked run; that path-recomputation is what caused a prior run to overwrite a tracked framework artifact (see ADR 0010, issue #40).
4. Produce the artifact at that exact path.
5. Call `scripts/validate-and-record.py`.
6. Only report completion if validation passes.
7. Never mark the next step complete yourself.
