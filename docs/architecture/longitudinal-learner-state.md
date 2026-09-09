# M11 — Longitudinal learner state

M11 is a bounded persistence-of-meaning layer over the existing evidence chain. It records **how exact learner-hypothesis evidence changes over time**; it does not create a new diagnosis engine.

## Data flow

```text
M7 exact current ledger snapshot + exact current hypothesis revision
                           │
                           ├── optional exact M10 plan + outcome assessment
                           │
                           ▼
                 HypothesisStateEvent
                           │ append only
                           ▼
                  LearnerStateLedger
                           │ deterministic rebuild
                           ▼
                 LearnerStateSnapshot
                           │
                           └── one HypothesisTrajectory per lineage
```

A trajectory exposes the current M7 revision/lifecycle/status, the latest M10 assessment that is **exactly bound to that same current revision**, and references to every M11 event for the lineage.

## Important boundaries

M11 does not:

- revise M7 hypotheses;
- convert a recurrence status into a permanent learner trait;
- select or rank interventions;
- treat practice success as transfer;
- transfer old M10 evidence to a newer M7 revision;
- infer mastery or causal effect;
- implement end-user CLI/UI behavior.

Terminal M7 lifecycle states are preserved. A later event may repeat the same terminal state/revision to attach later evidence, but it cannot reactivate the lineage or advance it under the same terminal history.

## Determinism

M11 records are content-addressed. The append ledger rejects duplicate occurrence keys with different content and accepts exact duplicate retries idempotently. Projection ordering is deterministic by hypothesis ID, and all timestamps require explicit timezones.

See [ADR 0010](../decisions/0010-longitudinal-learner-state-contract.md) for the normative contract and [the M11 runbook](../runbooks/m11-longitudinal-learner-state.md) for operation and qualification commands.
