# Architectural Review Recommendation — Template

Use this template when the architectural-review skill executes. Replace all bracketed sections with analysis results.

---

## Summary

[One-paragraph summary of the architectural recommendation and its key reasoning]

---

## Analysis

### Proposed Response Alignment

[How does the proposed response address the identified fog? Map each proposal component to specific fog classifications or evidence from the brief.]

### Risk Identification

[Enumerate specific, testable risks. Format: "Risk: [description] — Impact: [concrete consequence]"]

**Authority boundary risks**: [Does the proposal create competing authorities or orchestration layers?]

**Performance bottleneck risks**: [Does the proposal introduce new bottlenecks or relocate existing ones?]

**User experience risks**: [Does the proposal create indirection or coupling that affects UX?]

**Technical debt risks**: [Does the proposal defer or amplify technical debt?]

---

## Recommendation

### Decision

[One of: pursue | pursue_narrowed | investigate_first | defer | reject]

### Reasoning

[Detailed justification for the decision, including how risks were weighed and what constraints apply]

### Success Measures (if pursue)

[Required only for pursue decisions]

- **Metric**: [What will be measured]
- **Baseline**: [Current state]
- **Target**: [Desired outcome]
- **Measurement Method**: [How measurement will be performed]

### Reversal Conditions (if defer/reject)

[When would this decision change? Specific, testable conditions.]

### Investigation Steps (if investigate_first)

[What additional investigation is needed? Format as actionable steps.]

### Narrowed Scope (if pursue_narrowed)

- **Approved scope**: [Explicitly approved aspects]
- **Excluded scope**: [Explicitly excluded aspects]
- **Constraints**: [Conditions that must hold for approval]

---

## Machine-readable Decision

<!-- REQUIRED EXACT FENCE: the opening fence below must be exactly three
     backticks followed by "yaml" (```yaml) and the closing fence exactly
     three backticks (```). Do NOT use tilde fences (~~~yaml / ~~~) --
     scripts/validate-architectural-review-recommendation.py only recognizes
     the triple-backtick form and will report a parsing error otherwise. -->
```yaml
artifact_id: architectural_review_recommendation
decision: [pursue | pursue_narrowed | investigate_first | defer | reject]
confidence: [high | medium | low]
created_at: "[ISO timestamp]"
created_by: "[skill name or agent identifier]"

# Recommended for all outcomes
risks_identified:
  - "Risk 1: description"
  - "Risk 2: description"

# Required when decision is pursue OR pursue_narrowed
success_measures:
  metric: "[what will be measured]"
  baseline_status: "[current state]"
  target: "[desired outcome]"
  measurement_method: "[how measurement will be performed]"

# Required when decision is pursue_narrowed
approved_scope:
  - "[explicitly approved aspect]"
excluded_scope:
  - "[explicitly excluded aspect]"

# Required when decision is investigate_first
investigation_steps:
  - "[step 1]"
  - "[step 2]"

# Required when decision is defer OR reject
reversal_conditions:
  - "[condition 1]"

# Optional (commonly useful) when decision is reject
kill_conditions:
  - "[condition that makes proposal untenable]"
```

---

## Notes

[Any additional context or caveats about this recommendation]
