---
name: repair-verifier
description: re-run the probe after a docs-contract-reconciliation patch and verify that the original brief's findings no longer reproduce, marking each finding closed or remaining. use as the final gate of docs-contract-reconciliation before handoff.
---

# repair-verifier

The diagnostic brief is consumed by its own verification: after the
reconciler applies fixes, this skill re-measures the repository and checks
each original finding against the fresh state. Structural closure (the
re-probe) plus direction-evidence closure (validate-brief's
`collision_dedup_direction` rule) can establish bounded mechanical closure
for the checks they actually cover. They do **not** by themselves prove every
semantic, runtime, or user-facing consequence of the reconciliation succeeded.

## Inputs

- `docs_contract_reconciliation_report` (required): the reconciler's output;
  it names the fixes and cites the original brief.
- `prior_evidence` (recommended): the original `repository_sensemaking_brief`
  and its probe report — the acceptance criteria.
- `repository_state`: the repository to re-probe.

## Semantic Reasoning Alignment (Phase 9)

Read [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md).
Preserve this chain:

```text
prior finding / success condition
-> fresh target/currentness
-> fresh observation
-> like-for-like comparison
-> closure claim + epistemic status
-> remaining uncertainty / explicit limits
-> gate disposition
```

The central invariant is:

```text
repository changed
!= finding no longer reproduces
!= validator passed
!= intended outcome achieved
!= repair semantically succeeded
```

Use `closed` only for the bounded finding/check that no longer reproduces. If
the original success condition is broader than the probe, preserve the
unverified remainder explicitly rather than upgrading structural closure into
full repair success.

## Workflow

1. **Locate the original findings**: from the reconciliation report and
   prior evidence, list the original brief's findings (duplicate ids, stale
   docs claims, artifact sprawl, fixture gaps, etc.) and the success condition
   each finding was expected to satisfy where recorded.
2. **Re-probe current state**: run `python scripts/probe-repo.py --repo-root <target>` and
   validate the report (`scripts/validate-probe-report.py`). Use the fresh probe
   report, never the reconciler's prose, as the measured post-change state. Bind
   verdicts to that target/currentness boundary.
3. **Compare like-for-like**: ensure the fresh check actually corresponds to
   the original finding/baseline. A different scope or check cannot silently
   stand in for the original acceptance condition.
4. **Check each finding**: for every original finding, decide from the fresh
   probe report whether it is `closed` (no longer reproduces under the declared
   check and scope: e.g. `relationships.adr.findings` has no `duplicate_id`,
   `fixtures_coverage` has no unexplained `missing_fixtures`,
   `context_entropy.ce` is measured) or `remaining` (still reproduces, with the
   fresh evidence). Treat the non-reproduction relation as `DERIVED` from the
   fresh observation; any broader claim that the repair achieved its intended
   semantic/user outcome remains a separate judgment.
5. **State verification limits**: record material success conditions the probe
   does not cover, such as runtime behavior, external systems, user-level
   acceptance, or platform/configuration variants. Do not invent extra work when
   no material gap exists.
6. **Emit**: write the `repair_verification_report` artifact. If any
   finding remains, the gate `review_reconciliation_verified` must not be
   approved silently — the remaining findings are either fixed in a follow-up
   or recorded as deferred with a reason (evidence 0019 doctrine).

## Output

`repair_verification_report` artifact with required sections
`findings_closed`, `findings_remaining`, `probe_summary`, and this
Section 13 machine handoff:

```yaml
artifact_id: repair_verification_report
schema_version: 1
verified_brief_ref: <path of the original repository_sensemaking_brief>
findings_closed:
  - finding: <original finding, cited from the brief>
    evidence: <fresh probe field proving bounded non-reproduction/closure>
findings_remaining:
  - finding: <original finding still reproducing>
    evidence: <fresh probe field>
    disposition: fixed_in_follow_up | deferred
    reason: <why it remains>
created_at: <ISO 8601 UTC>
immutable: true
```

Phase 9 does not add general ontology fields to this canonical artifact. Put
material semantic limits in the human-readable report and, when collecting
pilot evidence, in the companion `semantic_reasoning_profile`.

## Mutate Rules

- **Read-only**: this skill never modifies the repository; it only measures.
- **No silent remaining findings**: every `remaining` entry carries a
  disposition and a reason.
- **Cite the fresh probe**: every verdict is grounded in a fresh
  `probe-report.yaml` field, not in the reconciler's summary.
- **No over-broad closure**: do not report `repair succeeded` beyond the success
  conditions actually covered by the fresh evidence.
- **Validator scope remains mechanical**: a valid report does not establish that
  broader semantic conclusions are true.

## References

- [Probe Engine: CONTEXT.md](../../CONTEXT.md)
- [Artifact Contracts: repair_verification_report](../../skills/workflow-planner/references/artifact-contracts.yaml)
- [Evidence 0019: self-dogfood reconciliation (deferred-items doctrine)](../../experiments/evidence/0019-sensemaking-self-dogfood-reconciliation/EVIDENCE.md)
- [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md)
- [Shared Reasoning Model](../../docs/semantic-architecture/reasoning-model.md)
