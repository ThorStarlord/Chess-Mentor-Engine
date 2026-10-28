# criteria_list output contract

Produce: `## Source requirements`, `## Acceptance scenarios`, `## Coverage notes`, `## Unresolved decisions`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: criteria_list
schema_version: "1"
source_artifact_ref: "artifacts/story_list.md"
scenarios:
  - id: AC-1
    source_story_ref: STORY-1
    category: happy_path | alternate | edge | error | state | integration | accessibility | performance
    given: "..."
    when: "..."
    then: ["..."]
    status: specified
unresolved_questions: []
```

Rules:

- scenario IDs are unique;
- each scenario traces to a source story/requirement;
- `given`, `when`, and at least one `then` assertion are explicit;
- `status` is `specified` here; execution/pass status belongs to test evidence;
- any proposed requirement beyond source scope is called out rather than silently normalized into accepted behavior.
