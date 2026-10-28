# Strategic Reconciliation

## 1. Prior Decision and Scope

Identify the target repository, prior analysis reference, prior selected path if
any, and the decision/responsibility that produced the returned evidence.

## 2. Returned Evidence

List decision-relevant returned evidence and provenance.

## 3. Claim Updates

For each material prior claim: `CONFIRM | REVISE | RETRACT | UNCHANGED`.

## 4. Assumption Updates

For each material prior assumption: `CONFIRM | RESOLVE | REVISE | INVALIDATE |
UNCHANGED`.

## 5. Path Continuation

Declare `CONTINUE | REVISE | SUPERSEDE | CLOSE | NO_PATH_CHANGE` and explain.

When the prior analysis declared a lightweight path transition and returned evidence
materially bears on it, optionally record one path-transition effect:
`ESTABLISHED | PARTIAL | NOT_ESTABLISHED | SUPERSEDED | NO_CONCLUSION`.
This is semantic reconciliation of a conceptual transition, not project status.

## 6. Strategic Implication

Declare exactly one:
`NO_MODEL_CHANGE | REAFFIRM | REVISE_STRATEGY | REOPEN_ANALYSIS |
OWNER_DECISION | THESIS_REVIEW_REQUIRED`.

## 7. Authority and Claim Boundaries

State what remains unauthorized/reserved.

## 8. Evidence

List stable references.

## 9. Machine-Readable Summary

```yaml
artifact_id: strategic_reconciliation
target_repository: owner/repository
prior_analysis_ref: SRA-1
current_source_identity: "main@<sha>"
returned_evidence:
  - evidence_ref: "PR#123"
    claim: "The selected capability is now implemented."
claim_updates:
  - claim_ref: CLAIM-1
    disposition: CONFIRM
    reason: "Returned evidence supports the original claim."
assumption_updates:
  - assumption_id: ASSUMPTION-1
    disposition: RESOLVE
    reason: "The dependency is now directly evidenced."
path_disposition: CONTINUE
prior_path_id: PATH-1
current_path_id: PATH-1
path_transition_effect:
  transition_ref: PATH-1/T1
  disposition: ESTABLISHED
strategic_effect: REAFFIRM
candidate_next_responsibility: null
implementation_authority_established_by_artifact: false
semantic_truth_established: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```

```text
path transition effect != roadmap status
transition established != next transition selected
transition effect != implementation authorization
```
