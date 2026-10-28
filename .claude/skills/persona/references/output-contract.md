# persona_definition output contract

Produce: `## Persona summary`, `## Context and profile`, `## Jobs to Be Done`, `## Pains and desired outcomes`, `## Current solutions and behaviors`, `## Evidence and confidence`, `## Assumptions and research gaps`, and `## Machine-readable handoff`.

The final section contains one YAML block with at least:

```yaml
artifact_id: persona_definition
schema_version: "1"
persona_id: persona-1
status: provisional
segment: "..."
primary_job: "..."
evidence_refs: []
assumptions: []
unresolved_questions: []
```

Rules: `persona_id` is non-empty and stable within the artifact; `status` is `provisional` or `evidence_backed`; `evidence_backed` requires a non-empty evidence reference; do not use `validated` because completing this artifact does not establish empirical validation.
