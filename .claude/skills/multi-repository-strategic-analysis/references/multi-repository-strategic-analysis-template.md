# Multi-Repository Strategic Analysis

## 1. Governing Intent, Scope, and Authority

List the explicit repository set and authority boundary.

## 2. Current Multi-Repository System Model

Describe the system/product formed by the selected repositories.

## 3. Capability Ownership and Overlap Map

Map decision-relevant capabilities to current owner aliases and evidence.

## 4. Explicit Relationships and Cross-Repository Evidence

Reuse declared relations when available; keep strategic observations separate.

## 5. Boundary Tensions

List only boundary/allocation tensions that could change the decision.

## 6. Candidate Boundary / Allocation Paths

For each materially distinct path include future state, allocations, boundary
changes, sequence, dependencies, unlocks, risks, reversibility, and evidence gaps.

## 7. Qualitative Path Comparison

Use the canonical Level-3 lenses; no scores.

## 8. Decision-Changing Uncertainty

State what could change the boundary/allocation judgment and the correct evidence source.

## 9. Strategic Synthesis and Warranted Direction

Declare `BUILD | INVESTIGATE | DEFER | NO_CHANGE | OWNER_DECISION | THESIS_REVIEW`.

## 10. Authority and Claim Boundaries

Preserve explicit target-set and mutation authority.

## 11. Evidence

List stable references for every selected target.

## 12. Machine-Readable Summary

```yaml
artifact_id: multi_repository_strategic_analysis
analysis_ref: MRSA-1
governing_intent: "<owner/repository-system intent>"
target_repositories:
  - alias: sensemaking
    repository: owner/sensemaking
    source_identity: "main@<sha>"
    role: "decision-support/control layer"
    evidence_refs:
      - README.md
  - alias: factory
    repository: owner/factory
    source_identity: "main@<sha>"
    role: "execution/orchestration layer"
    evidence_refs:
      - README.md
explicit_relations:
  - relation_id: REL-1
    source_alias: factory
    target_alias: sensemaking
    relation_type: consumes_interface_from
    evidence_refs:
      - docs/integration.md
capability_ownership:
  - capability_id: execution_handoff
    current_owner_aliases: [sensemaking]
    state: ESTABLISHED
    evidence_refs:
      - docs/campaign-execution-interface-v1.md
    boundary_consequence: "Defines the decision/orchestration seam."
boundary_tensions:
  - tension_id: TENSION-1
    statement: "<decision-relevant boundary tension>"
construction_paths:
  - path_id: PATH-1
    name: "<path>"
    future_state: "<future repository-system state>"
    capability_allocations:
      - capability_id: execution_handoff
        proposed_owner_aliases: [sensemaking]
        boundary_pattern: "keep stable interface"
    boundary_changes:
      - "<major interface/ownership change>"
    construction_sequence:
      - "<coarse capability-level step>"
    dependencies:
      - "<dependency>"
    unlocks:
      - "<future possibility>"
    risks:
      - "<material risk>"
    reversibility: "<qualitative>"
    evidence_gaps:
      - "<material gap>"
path_comparison:
  - path_id: PATH-1
    lenses:
      mission_relevance: "<qualitative>"
      decision_value: "<qualitative>"
      blocking_power: "<qualitative>"
      evidence_sufficiency: "<qualitative>"
      consequence_of_error: "<qualitative>"
      deferral_cost: "<qualitative>"
      reversibility: "<qualitative>"
      authority_availability: "<qualitative>"
      dependency: "<qualitative>"
      smallest_warranted_intervention: "<qualitative>"
decision_changing_uncertainty:
  statement: "<uncertainty or none>"
  could_change: "<judgment>"
  inquiry_warranted: false
  evidence_needed: "<smallest sufficient evidence or none>"
  source: repository_evidence
strategic_disposition: BUILD
selected_path_id: PATH-1
candidate_repository_responsibility: "<bounded responsibility>"
affected_target_aliases: [sensemaking, factory]
automatic_repository_discovery_performed: false
target_scope_expanded_by_artifact: false
implementation_authority_established_by_artifact: false
semantic_truth_established: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```
