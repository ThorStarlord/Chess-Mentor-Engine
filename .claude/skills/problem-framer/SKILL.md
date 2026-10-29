---
name: problem-framer
description: analyze a vague idea or repository fog to produce a structured problem frame. use when the user is unsure what they are building or why a problem is occurring.
---

# problem-framer

Converts vague fog into a structured **Problem Frame**. This skill sits at the very beginning of the sensemaking process, helping to define the "problem under the problem."

## Workflow
1. **Fog Capture**: Listen to the user's raw idea or observation.
2. **Deconstruction**: Identify the "Problem Under the Problem" (the root cause or hidden desire).
3. **Boundary Identification**: Determine the "Object Under Pressure" (the specific system part that is most impacted).
4. **Failure Analysis**: Identify the failure mode we are trying to avoid.
5. **Technical Prerequisites**: Identify "What Must Be True" for the solution to be reachable.
6. **Success Definition**: Define what must be true for the solution to be considered successful.
7. **Synthesis**: Produce a Problem Frame.

## Output Format
Every response must follow the [Problem Frame](references/problem-frame-template.md) structure.

**CRITICAL**: When invoked as part of a workflow, write the final Problem Frame to:
```
artifacts/problem_frame.md
```

This is the standard artifact path for this skill's output.

## Boundary Rules
- **Non-Implementation**: Do not propose specific technical solutions or implementations. Focus only on framing the problem and the desired outcome.
- **Conditional Object Verification**:
    - If the `Object Under Pressure` names a file, registry, command, script, or directory, the framer SHOULD verify it exists in the `repository_state` (if provided).
    - If it names a conceptual boundary (e.g., "onboarding flow"), the framer MUST identify a concrete **inspectable proxy** (e.g., a specific config file or entry point) to ground the research.
- **Boundary Guards**:
    - **Domain Keyword Guard**: If the user uses domain-heavy keywords (e.g., 'Product', 'Engineering') but explicitly mentions confusion about 'how to start' or 'which workflow', the Object Under Pressure MUST be the repository's own routing or registry files.
- **System Defect Guard**: If a user cites a specific workflow or skill by name but reports an execution error (e.g., 'missing steps', 'invalid I/O'), do NOT assume user confusion. The Object Under Pressure MUST be the corresponding registry entry.
    - **Orchestration Shield**: If the user mentions building a 'workflow', 'pipeline', or 'process', the `Object Under Pressure` MUST be the repository's orchestration registry (e.g., `workflow-registry.yaml`), even if domain-specific artifacts (PRD, Code, Design) are mentioned as components.

## References
- [Problem Frame Template](references/problem-frame-template.md)

## Execution Protocol

When executing as part of a workflow run:

1. Read the provided run_id, step_id, input artifacts, and expected artifact_id.
2. Call `scripts/run-ledger.py start-step`.
3. The runtime already resolved the output path and passed it as `expected_output_path` in context — use that path verbatim. Never call `scripts/create-artifact.py` (or otherwise recompute a path) during a runtime-invoked run; that path-recomputation is what caused a prior run to overwrite a tracked framework artifact (see ADR 0010, issue #40).
4. Produce the artifact at that exact path.
5. Call `scripts/validate-and-record.py`.
6. Only report completion if validation passes.
7. Never mark the next step complete yourself.

