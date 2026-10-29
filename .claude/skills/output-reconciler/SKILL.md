---
name: output-reconciler
description: verify claims about completed work against durable repository artifacts, classify each claim verified/disputed/omitted, and produce a reconciliation report with findings and actionable recommendations. use when a work_claim artifact (a handoff, task summary, or status report) asserts work was done and the claim must be grounded before it is trusted or acted on.
---

# output-reconciler

Reads the output of a stage as an artifact, never as trusted prose. Every
claim in the audited `work_claim` is re-derived from the repository tree,
probe reports, evidence records, and validator outputs before it is
accepted as **supported within the checked scope**. This is the
"read-the-output" pattern (evidence 0020): produce -> read the artifact, not
the prose -> verify like-for-like -> dispose (fix | defer | file) -> record.

`verified` is an evidence-status verdict for the audited claim/baseline/scope;
it is not a universal semantic truth label.

## Inputs

- `work_claim` (required): the handoff/task summary whose claims are audited.
- `repository_sensemaking_brief` (required): the repo-sensemaker diagnosis of
  the target repository, including its target/currentness and evidence limits.
- `prior_evidence` (recommended): earlier briefs, postmortems, and evidence
  records about the target (e.g. `experiments/evidence/NNNN-*`,
  `docs/reviews/*`). Framework learnings captured after the target vendored
  its skills must still reach this reconciliation (evidence 0018).

## Semantic Reasoning Alignment (Phase 9)

Read [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md).
Preserve:

```text
work claim
-> falsifiable bounded claim
-> current target/evidence
-> like-for-like observation
-> verified / disputed / omitted classification
-> contradiction / uncertainty / explicit limit
-> disposition
```

And keep these separations visible:

```text
artifact supports claim in scope
!= claim is universally true

validator passed
!= intended outcome achieved

repository changed
!= claimed repair succeeded
```

The existing `verified | disputed | omitted` enum remains the artifact
contract. General ontology statuses describe the reasoning that supports the
classification; they do not replace that enum.

## Workflow

1. **Extract claims**: split the `work_claim` into falsifiable statements.
   A claim is falsifiable when it names a bounded artifact, metric, commit,
   state, behavior, or absence condition that can be checked under an explicit
   scope. If the original statement is broader than the available check, narrow
   the auditable sub-claim and preserve the unverified remainder as a limit.
2. **Bind currentness and ground each claim**: for every claim, identify the
   repository/snapshot being checked and find the durable artifact that supports
   or contradicts it (probe-report.yaml fields, evidence records, validator
   output, `git log`/`git mv` state, merged HEAD). Cite the artifact with its
   location. Historical evidence may establish a baseline but cannot silently
   substitute for the current-state check.
3. **Classify**: mark each claim `verified`, `disputed`, or `omitted`.
   - `verified`: current durable evidence supports the claim like-for-like,
     under the same baseline, change, and declared scope. This does not extend
     the claim beyond the evidence's coverage.
   - `disputed`: current evidence contradicts the claim, required evidence is
     absent where the claim requires it, or the claim materially overstates the
     available evidence's scope.
   - `omitted`: the claim is silent about something the artifacts show and the
     omission materially changes how the work should be interpreted or acted
     on — e.g. a handoff that flattens a controversy (evidence 0018: the auteur
     summary omitted the Rule 7 direction conflict and stale vendored skills).
4. **Compare like-for-like**: before attributing a failure or success to the
   claimed change, align baseline, check/method, scope, configuration, claimed
   change, and post-change target. A failure present on both is a pre-existing
   condition, not a claim to dispute. A PASS under a narrower check is not
   evidence for a broader success claim.
5. **Record uncertainty and limits**: when missing evidence could change the
   classification or next action, state that uncertainty. Preserve untested
   runtime/user behavior, external systems, stale/unavailable sources, or
   unmatched baselines as explicit limits rather than silent assumptions.
6. **Dispose**: for each disputed/omitted claim, one of:
   - fix (repair the producer or consumer), or
   - defer with a written reason (never silently), or
   - file (turn the finding into an issue for the tracker).
7. **Emit**: write the `reconciliation_report` artifact (Section 13
   machine-readable handoff, see below) with the classified claims,
   findings, lessons, and recommendations.

## Output

`reconciliation_report` artifact with required sections `claims`,
`findings`, `recommendations`, and this Section 13 machine handoff:

```yaml
artifact_id: reconciliation_report
schema_version: 1
source_claim_ref: <path of the audited work_claim>
claims:
  - claim: <falsifiable statement from the work_claim>
    classification: verified | disputed | omitted
    artifact: <the artifact that grounds the verdict, with location>
    disposition: none | fixed | deferred | filed
findings:
  - concept: <domain concept>
    finding_type: <e.g. claim_contradicted | claim_omitted | pre_existing>
    observations:
      - source: <path>
        location: <path:line>
        value: <observed value>
        evidence: <short quote or metric>
    confidence: high | medium
    requires_semantic_review: true | false
    notes: <why this matters and any material scope limit>
recommendations:
  - issue: <one actionable item>
    target: <repo surface that owns the fix>
created_at: <ISO 8601 UTC>
immutable: true
```

Phase 9 does not add general ontology fields to this canonical artifact. Use
the companion `semantic_reasoning_profile` for cross-Skill pilot comparison.

## Mutate Rules

- **Read-only until disposition**: the skill verifies and classifies before
  any write. Repairing a producer/consumer is a separate authorized step.
- **No silent dispositions**: every disputed/omitted claim ends in
  `fixed`, `deferred` (with a reason), or `filed` (with an issue ref).
- **No new field names**: field names above are the contract; add none.
- **Do not touch unrelated code**: repairs are scoped to the claim being
  reconciled.
- **No over-broad verification**: a claim is verified only within the baseline,
  currentness, method, and scope actually checked.
- **Mechanical PASS is not semantic warrant**: validators may establish report
  structure and evidence shape, not that the audited work achieved every
  intended outcome.

## References

- [Evidence 0020: read-the-output pattern](../../experiments/evidence/0020-read-the-output-pattern/EVIDENCE.md)
- [Evidence 0018: auteur docs-contract-reconciliation analysis](../../experiments/evidence/0018-auteur-docs-contract-reconciliation-analysis/EVIDENCE.md)
- [Evidence Rules: repo-sensemaker](../../skills/repo-sensemaker/references/evidence-rules.md)
- [Artifact Contracts: reconciliation_report](../../skills/workflow-planner/references/artifact-contracts.yaml)
- [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md)
- [Shared Reasoning Model](../../docs/semantic-architecture/reasoning-model.md)
