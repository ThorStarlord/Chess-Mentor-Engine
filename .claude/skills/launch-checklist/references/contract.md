# Launch-checklist methodology and `readiness_report` contract

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/launch-checklist.md`.

Retain cross-functional readiness review, launch tiers, soft/hard launch distinction, concentrated channel planning, concentric stakeholder/customer communication, go/no-go conditions, rollback triggers, and post-launch monitoring. Treat calendar examples and function-specific checklist items as heuristics, not mandatory truth.

## Evidence and authority rules

A checklist is an assessment surface, not completion evidence. `evidence_backed_complete` requires durable evidence refs. `not_applicable` requires a reason. Missing approval, test, deployment, monitoring, security, legal, or rollback evidence must remain `unknown`, `planned`, or `blocked`.

A generated `go` recommendation never grants launch authority. `external_launch_authority_ref` may record supplied authority but the artifact does not execute it.

## Human-readable sections

Produce:

- `## Launch context`
- `## Evidence inventory`
- `## Cross-functional readiness`
- `## Launch-blocking conditions`
- `## Go or no-go recommendation`
- `## Rollback and monitoring`
- `## Authority and unknowns`
- `## Machine-readable handoff`

## Machine-readable handoff

```yaml
artifact_id: readiness_report
schema_version: "1"
status: planning | assessed
launch_scope: "..."
launch_tier: tier1 | tier2 | tier3 | unspecified
target_window: null
evidence_window: "..."
evidence_refs: []
checks:
  - id: READY-1
    function: engineering | design | marketing | sales | support | legal | operations | analytics | other
    requirement: "..."
    criticality: launch_blocking | required | advisory
    state: unknown | planned | evidence_backed_complete | blocked | not_applicable
    evidence_refs: []
    note: "..."
recommendation: not_assessed | go | go_with_conditions | no_go
conditions: []
rollback_triggers:
  - id: ROLLBACK-1
    statement: "..."
    status: proposed
monitoring_requirements: []
external_launch_authority_ref: null
unresolved_questions: []
```

## Mechanical invariants

- Check and rollback-trigger IDs are unique.
- `evidence_backed_complete` requires non-empty evidence refs.
- `not_applicable` requires a non-empty note explaining why.
- `status: planning` must use `recommendation: not_assessed`.
- `recommendation: go` requires `status: assessed` and no launch-blocking check in `unknown`, `planned`, or `blocked` state.
- Rollback triggers remain `status: proposed`; the artifact cannot claim a trigger is configured or tested.
- The presence of `external_launch_authority_ref` records supplied authority only; it does not prove launch execution.

The validator does not decide whether evidence is sufficient in a strategic or operational sense, whether a launch should occur, or whether a competent authority has actually exercised the recorded permission.
