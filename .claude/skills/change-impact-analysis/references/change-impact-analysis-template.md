# Change Impact Analysis

## 1. Change Scope and Authority

State the bounded change, its state, target repository/source identity, and
authority boundary.

## 2. Impact Evidence

List evidence used to determine affected surfaces.

## 3. Affected Surfaces

For each decision-relevant surface include category, target, impact, evidence,
semantic review need, verification/reconciliation need, and authority boundary.

## 4. Cross-Repository Impact

List only explicitly selected repository impacts. State none when not applicable.

## 5. Claim and Verification Consequences

Explain what claims/verification/closure conditions change.

## 6. Bounded Follow-Up Responsibilities

List only follow-up work warranted by the impact evidence.

## 7. Closure Effect

Declare one:
`NO_CLOSURE_EFFECT | ADDITIONAL_VERIFICATION_REQUIRED |
RECONCILIATION_REQUIRED | OWNER_DECISION_REQUIRED |
STRATEGIC_REASSESSMENT_REQUIRED | THESIS_REVIEW_REQUIRED`.

## 8. Authority and Claim Boundaries

State protected transitions and claim ceiling.

## 9. Machine-Readable Summary

```yaml
artifact_id: change_impact_analysis
analysis_ref: CIA-1
target_repository: owner/repository
target_source_identity: "main@<sha>"
change:
  change_id: CHANGE-1
  state: IMPLEMENTED
  statement: "<bounded change>"
  evidence_refs:
    - "PR#123"
impact_items:
  - surface_id: IMPACT-1
    category: contract
    target_ref: docs/contract.md
    impact_statement: "<material consequence>"
    evidence_refs:
      - docs/contract.md
    semantic_review_required: true
    required_actions:
      - "Reconcile the contract wording with the implemented behavior."
    authority_boundary: "repository-only"
cross_repository_impacts:
  - repository_alias: consumer
    repository: owner/consumer
    impact_statement: "<explicitly scoped impact>"
    evidence_refs:
      - docs/integration.md
claim_consequences:
  - claim_ref: CLAIM-1
    effect: "Must be reverified against the changed contract."
followup_responsibilities:
  - responsibility_id: FOLLOWUP-1
    statement: "Run finding-specific contract verification."
    affected_surface_ids: [IMPACT-1]
closure_effect: ADDITIONAL_VERIFICATION_REQUIRED
automatic_repository_discovery_performed: false
change_authorized_by_artifact: false
followup_execution_authorized_by_artifact: false
semantic_truth_established: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```
