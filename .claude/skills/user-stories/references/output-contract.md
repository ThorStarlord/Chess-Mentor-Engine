# story_list output contract

Produce: `## Source and scope`, `## Stories`, `## Dependencies and sequencing`, `## Open questions`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: story_list
schema_version: "1"
source_artifact_ref: "artifacts/prd.md"
scope_status: approved | proposed | mixed
stories:
  - id: STORY-1
    actor: "..."
    want: "..."
    value: "..."
    source_refs: ["..."]
    acceptance_intent: ["..."]
    dependencies: []
    scope_status: approved | proposed
unresolved_questions: []
```

Rules:

- story IDs are unique and non-empty;
- `source_artifact_ref` identifies the bounded source specification;
- each story has observable acceptance intent and at least one source reference;
- proposed expansion remains `proposed` until explicit approval exists;
- dependencies identify prerequisites but do not imply an engineering estimate or sprint commitment.
