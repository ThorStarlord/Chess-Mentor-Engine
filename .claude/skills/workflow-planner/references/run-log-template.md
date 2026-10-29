# Workflow Run Log: [Workflow Name]

- **Date**: [YYYY-MM-DD]
- **Session ID**: [ID]
- **Orchestrator Mode**: [Mode]

## Pre-flight (required for mutating modes: guided, autonomous, yolo)
- **branch**: [Branch name used for execution]
- **initial_snapshot**: [Git SHA or state marker before execution]
- **validation_checklist**:
    - [ ] Required skill registries loaded
    - [ ] Input artifacts exist and are valid
    - [ ] Gate dependencies resolved
    - [ ] Workspace clean (no uncommitted changes)

## Sequence Log

### Step [ID]
- **step_id**: [ID]
- **skill**: [Skill Name]
- **runtime**: [local | local_command | external]
- **invocation**: [exact command or local function]
- **input_artifact**: [Artifact ID or N/A]
- **input_source**: [Source ID or N/A]
- **output_artifact**: [Artifact ID]
- **artifact_path**: [Relative path, e.g., artifacts/name.md]
- **validator_stack**:
    - level: [Generic | Specialized]
      command: [Exact command]
      result: [PASSED | FAILED]
- **gate**: [Gate Name]
- **gate_behavior**: [required | skipped_by_design | bypassed_by_yolo | paused_for_approval]
- **gate_result**: [approved_by_user | denied_by_user | bypassed_by_yolo | auto_approved] (required if gate_behavior != skipped_by_design)
- **approved_at**: [ISO 8601 timestamp] (required if gate_result == approved_by_user)
- **approved_by**: [User identifier] (required if gate_result == approved_by_user)
- **status**: [COMPLETED | PAUSED | FAILED]
- **error** (if FAILED):
    - **type**: [error_category, e.g., test_failure, validation_error, missing_artifact]
    - **message**: [Error description]
    - **log_file**: [Path to detailed error log if available]
    - **remediation**: [Recovery command, e.g., git reset --hard {SHA}]
    - **recommendation**: [Suggested next action]

### TDD Cycle (if applicable)
- **cycle**: [RED | GREEN | REFACTOR]
- **test_command**: [Exact test command executed]
- **test_result**: [PASSED | FAILED | SKIPPED]
- **coverage_delta**: [+/- percentage or N/A]
- **commit_sha**: [Git SHA after cycle]

## Decisions & Overrides
- [List any manual interventions or logic changes made during the run]

## Final State
- [Summary of what was achieved]
