# discovery_findings output contract

Produce: `## Problem framing`, `## Existing evidence`, `## Hypotheses and uncertainties`, `## Learning plan`, `## Decision criteria`, `## Unresolved questions`, and `## Machine-readable handoff`.

The final YAML block includes:

```yaml
artifact_id: discovery_findings
schema_version: "1"
problem_statement: "..."
hypotheses:
  - id: H-1
    statement: "..."
    status: untested
    evidence_refs: []
    learning_method: "..."
    decision_criterion: "..."
unresolved_questions: []
```

Hypothesis IDs are unique. `status` is `untested`, `evidence_backed`, or `contradicted`; `evidence_backed` requires evidence. Never encode `validated` merely because a test was designed. Decision criteria must be observable or explicitly owner-judgment based.


`learning_method` is evidence-source-neutral. It may name reading, inspection, verification, owner/external evidence, a bounded probe, reversible normal-use construction, or an experiment only when experimentation has separately passed Experiment Economy. Do not encode an experiment merely because a hypothesis is untested.
