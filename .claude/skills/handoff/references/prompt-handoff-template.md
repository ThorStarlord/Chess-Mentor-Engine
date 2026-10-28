# Prompt Handoff

## 1. Target Skill
The name or ID of the specialized skill this prompt is for.

## 2. Context to Preserve
The most critical facts, decisions, or constraints from the sensemaking phase.

## 3. Task
A clear, direct statement of what the target skill should do.

## 4. Constraints
List of "must-haves" and "must-nots" (e.g., "Do not commit to main").

## 5. Inputs
The specific files or artifacts the target skill should consume.

## 6. Expected Output
What success looks like for the next step.

## 7. Stop Condition
When the target skill should stop and wait for human review.

---

## 8. Ready-to-copy Prompt
```markdown
/[Target Skill]
[Task statement]
[Context/Constraints]
```

## 9. Machine-readable handoff
End the artifact with this block. `source_intent_ref` is REQUIRED — carry it
forward from the input artifact's own `source_intent_ref` (every upstream
artifact references the run's immutable user intent; see ADR 0006). If the input
has none, use the run's intent file `00-user-intent.md`.

```yaml
artifact_id: session_summary
source_intent_ref: 00-user-intent.md
target_skill: <next skill id>
status: ready
```
