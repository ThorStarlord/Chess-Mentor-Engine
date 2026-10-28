# Evidence and Closure (v1)

Load this reference when a consequential result has to be validated, a work
claim audited, a repair verified against its original finding, a Repository
Sensemaking Brief interpreted, or a registered workflow considered. Skip it for
a clear local change whose ordinary tests and diff review settle the outcome.

It holds the procedures behind the entrypoint's closure rules. The
non-identities in `SKILL.md` remain the governing summary; this file adds the
how.

## 1. Validate mechanically

Validate consequential artifacts as soon as they are produced, using the
repository's current validator entrypoints and contracts.

| Validation can prove | Validation cannot prove |
| --- | --- |
| required fields exist | the evidence is sufficient |
| enum values are canonical | the analysis is correct |
| references and paths resolve | the recommendation should be accepted |
| the structure satisfies its contract | the original finding is repaired |
| a deterministic command or test passed | the task is closed |

### Handling validation failures

Treat each failure by what it actually establishes:

- **Mechanical or contract defect** (missing field, invalid enum, wrong type,
  broken reference): repair the artifact when the correct value is evidenced.
- **Semantic conflict:** re-read the evidence; change the claim only if the
  evidence warrants it.
- **Insufficient evidence or a logic problem:** gather evidence or select a
  different responsibility. Never fabricate a mechanically valid answer.
- **Same failure after a bounded retry:** reconsider the diagnosis or the
  responsibility instead of repeating the repair.
- **Owner or authority decision required:** stop and surface it. An authority
  boundary is not retried.

A retry budget is an execution aid, not reasoning. After a failed attempt ask
what new evidence changed, and whether the same responsibility is still
warranted.

## 2. Reconcile material work claims

Reconcile consequential claims such as "implemented X", "fixed Y", "all
relevant checks pass", "the handoff is complete" or "ready to merge".
`output-reconciler` compares a `work_claim` with durable repository evidence
and produces a `reconciliation_report` whose claim states include `verified`,
`disputed` and `omitted`.

Reconciliation answers whether the repository supports what is claimed about
the work. It does not answer whether the original finding is closed.

## 3. Verify repairs against the original finding

When work claims to repair a prior finding, `repair-verifier` asks whether the
change closed the original diagnosis under fresh observation. Relevant green
CI is necessary evidence, not repair verification.

```text
observed -> understood -> responsibility selected -> implemented
-> mechanically validated -> claims reconciled -> repair verified
-> authorized -> integrated -> canonical state verified -> closed
```

Not every task passes through every state. Do not collapse the ones that
matter.

## 4. Read a Repository Sensemaking Brief

`repo-sensemaker` produces a `repository_sensemaking_brief`. Read it for the
consequential or weakest boundary, direct file-level evidence,
interpretations versus hypotheses, unresolved uncertainty, fog classification
when useful, recommendations and planning metadata, and any machine-readable
handoff fields the current contract requires.

- **Contract source of truth:** `../../workflow-planner/references/artifact-contracts.yaml`.
  Read fields from the contract, not from memory or from this prose.
- **Fog is diagnostic metadata.** The four canonical fog types
  (`product_fog`, `ui_fog`, `docs_fog`, `architecture_fog`) are defined in
  `../../../docs/canonical-vocabulary.yaml` when that file is available. A
  repository can show several; classify the primary one only when the
  contract or analysis calls for it.
- **Recommendation fields are not commands.** `recommended_workflow_id` or
  `chosen_workflow_id` records a recommendation. It does not authorize
  executing a workflow unless the current responsibility and authority
  independently warrant it. Automatic fog-type routing is not ratified
  product behavior.

A Brief is a specialist result artifact: evidence about the revision it
examined. Check its currentness against the code before relying on it.

## 5. Use registered workflows as bounded subgraphs

A registered workflow helps when the selected responsibility has stable,
mechanically expressible steps. The top-level Sensemaking loop is not one
workflow. The active agent keeps every transition that needs judgment:
whether sensemaking is warranted, which uncertainty matters, which
responsibility comes next, whether more evidence is needed, whether to stop
or escalate, and whether authority permits action or publication.

Execution may decide which already-defined step runs next. Sensemaking
decides which responsibility becomes the next node at all. Legacy routing
mechanics can remain for compatibility; they are not authority to bypass
agent judgment.

## 6. Delegated results return as evidence

When work is delegated to a Skill, subagent, workflow or external executor:

```text
delegated result -> evidence for the active agent -> semantic reassessment

worker recommendation != parent decision
worker success        != global closure
retry/fallback policy != permission to change responsibility
```

Delegation does not transfer responsibility selection, closure or protected
action authority unless that authority was explicitly delegated.
