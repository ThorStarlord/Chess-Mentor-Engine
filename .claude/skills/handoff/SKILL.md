---
name: handoff
description: convert a sensemaking artifact into a ready-to-copy prompt for the next specialized skill. use to ensure context is preserved across skill transitions.
---

# prompt-handoff

Produces a **Prompt Handoff** to ensure that the judgment reached in sensemaking is successfully transmitted to the next specialized skill (e.g., `to-prd`, `tdd`).

## Workflow
1. **Intake**: Review the latest sensemaking artifact (Problem Frame, Brief, or Plan).
2. **Target Selection**: Identify the next specialized skill in the registry.
3. **Context Preservation**: Extract the most critical constraints, goals, and evidence.
4. **Task Formulation**: Write a clear, actionable task statement.
5. **Constraint Mapping**: List all "must-haves" and "must-nots."
6. **Stop Condition**: Define exactly when the next skill should stop for review.
7. **Intent Carry-Forward**: Emit the machine-readable block (section 9) with a
   REQUIRED `source_intent_ref`. Copy it from the input artifact's own
   `source_intent_ref` so the intent audit trail stays unbroken (ADR 0006); if the
   input has none, reference the run's `00-user-intent.md`.

## Output Format
Every response must follow the [Prompt Handoff](references/prompt-handoff-template.md) structure, including the section 9 machine-readable block with `source_intent_ref`.

## Boundary Rule
Do not execute the prompt yourself. Your job is to package the context for the user to copy/paste or for the orchestrator to pass.

## References
- [Prompt Handoff Template](references/prompt-handoff-template.md)

## Execution Protocol

When executing as part of a workflow run:

1. Read the provided run_id, step_id, input artifacts, and expected artifact_id.
2. Call `scripts/run-ledger.py start-step`.
3. The runtime already resolved the output path and passed it as `expected_output_path` in context — use that path verbatim. Never call `scripts/create-artifact.py` (or otherwise recompute a path) during a runtime-invoked run; that path-recomputation is what caused a prior run to overwrite a tracked framework artifact (see ADR 0010, issue #40).
4. Produce the artifact at that exact path.
5. Call `scripts/validate-and-record.py`.
6. Only report completion if validation passes.
7. Never mark the next step complete yourself.

