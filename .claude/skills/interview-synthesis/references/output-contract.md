# synthesis_report output contract

Produce: `## Research context and sources`, `## Jobs to Be Done`, `## Behavioral patterns`, `## Problems and contradictions`, `## Evidence excerpts`, `## Implications and next research`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: synthesis_report
schema_version: "1"
source_interviews: [interview-1]
findings:
  - id: F-1
    statement: "..."
    source_refs: [interview-1]
    frequency:
      count: 1
      total: 1
    confidence: low
contradictions: []
unresolved_questions: []
```

`source_interviews` is non-empty. Finding IDs are unique; every finding has at least one source reference; frequency count cannot exceed total; confidence is `low`, `medium`, or `high`. Direct-quote prose must identify its interview source.
