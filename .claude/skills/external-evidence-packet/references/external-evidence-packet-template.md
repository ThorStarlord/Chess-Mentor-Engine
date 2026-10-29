# External Evidence Packet

## 1. Question and Scope

State the decision/question this packet informs.

## 2. Sources

Record stable external provenance.

## 3. Claims Supported

Bind each bounded claim to source IDs.

## 4. Currentness Limits

State how/when each material claim may become stale.

## 5. Provenance

Record retrieval timestamps and available identifiers/hashes.

## 6. Authority and Claim Boundaries

External evidence does not become repository authority.

## 7. Machine-Readable Summary

```yaml
artifact_id: external_evidence_packet
target_decision_ref: "<decision/analysis ref>"
retrieved_at: "YYYY-MM-DDTHH:MM:SSZ"
sources:
  - source_id: SOURCE-1
    uri: "https://example.com/source"
    title: "<title>"
    publisher: "<publisher or unknown>"
    publication_date: null
    retrieved_at: "YYYY-MM-DDTHH:MM:SSZ"
claims:
  - claim_id: EXT-CLAIM-1
    statement: "<bounded supported claim>"
    source_ids: [SOURCE-1]
    currentness_limit: "<when this may need refresh>"
repository_fact_established_by_artifact: false
semantic_truth_established: false
implementation_authority_established_by_artifact: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```
