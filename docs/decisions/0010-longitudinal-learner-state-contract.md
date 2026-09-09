# ADR 0010 — Longitudinal learner-state evidence contract

**Status:** Accepted for M11 implementation  
**Scope:** Participant-specific longitudinal reconstruction after qualified M7 and M10  
**Does not establish:** causal learning, mastery, permanent traits, automatic M7 revision, or intervention efficacy

## Context

M7 already owns append-only learner-hypothesis identity, revision, lifecycle, and recurrence assessment. M10 owns protocol-bound practice/transfer outcome evidence and deliberately retains `causal_effect = mastery = not_established`. A persistent tutor needs to reconstruct how these exact states changed over weeks or months without creating a second mutable weakness model or silently strengthening either upstream claim.

## Decision

M11 adds an append-only participant ledger of `HypothesisStateEvent` records and a deterministic `LearnerStateSnapshot` projection.

Each event binds:

- one exact current M7 `HypothesisLedgerSnapshot`;
- one exact current `HypothesisRevision` contained by that snapshot;
- the snapshot's exact current M7 assessment and authority lifecycle state;
- optionally, one exact M10 `EvaluationPlan` and `OutcomeAssessment` bound to that same M7 revision;
- explicit author/system provenance, rationale, observation time, recording time, and an occurrence key.

The current learner-state snapshot is rebuilt from the event history. It is not a mutable score table.

## Identity and chronology gates

M11 fails closed when:

- an M7 snapshot or revision content fingerprint/identity is inconsistent;
- the requested revision is not the exact current revision in the supplied M7 snapshot;
- participant identities differ across M7, M10, and M11;
- an M10 plan is bound to another M7 revision;
- an M10 assessment does not bind the supplied plan/policy exactly;
- the M11 observation predates the M7 snapshot or M10 assessment;
- a revision number regresses or the same revision number changes immutable identity;
- a terminal M7 lifecycle is later resurrected or changed to a different terminal kind;
- the same external event key is reused for different content.

Repeating the exact same event key/content is idempotent.

## Revision boundary for outcomes

M10 outcome evidence remains attached to the exact M7 revision for which its plan was defined. When M7 advances to a new revision, the derived current M11 trajectory does **not** carry old M10 outcome evidence forward automatically. Historical events remain visible, but a current revision requires its own exact outcome binding.

## Claim ceiling

M11 can state what the current exact M7 status is, what exact M10 dimension statuses exist for the current revision, and how those records changed over time. It cannot infer a scalar weakness score, causal cognitive mechanism, intervention-caused improvement, competency, or mastery.

Every `LearnerStateSnapshot` therefore retains:

```text
claim_scope = participant_specific_longitudinal_evidence
causal_effect = not_established
mastery = not_established
```

## Consequences

- Persistence remains evidence-ledger oriented and rebuildable.
- M7 and M10 remain authoritative for their own semantics; M11 records references rather than rewriting them.
- Current state can be reproduced deterministically from append-only history.
- A later storage/product package may archive or expose M11 records, but M11 itself adds no CLI, UI, hosted profile service, automatic migration, or empirical efficacy claim.
