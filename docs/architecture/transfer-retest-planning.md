# M42 — Transfer / Retest Planning

M42 is a deterministic **planning-only** consumer of exact M40 transfer-test intent and exact M9 intervention selection.

## Purpose

M40 can propose `RUN_NEAR_TRANSFER_TEST` or `RUN_FAR_TRANSFER_TEST`. M42 answers the narrower question: which explicitly characterized position is eligible to test next, and why?

```text
M36/M39 current learner evidence
-> M40 transfer-test proposal
+ exact M9 selected intervention
+ M10-compatible candidate positions
+ explicit exposure/reuse facts
+ optional K0-K7 semantic validation
-> M42 transfer/retest plan
-> later participant attempt
-> M10 outcome evidence
```

## Authority boundary

```text
M42 plan != M10 outcome evidence
planned test != completed test
completed test != transfer success
transfer success != mastery
```

Every M42 plan records `plan_authority = planning_only`, `outcome_effect = not_established`, and `mastery = not_established`.

## Candidate semantics

A transfer candidate carries explicit, provenance-bearing descriptions of:

- canonical M10-compatible `OutcomePosition`;
- semantic relation to the target (`same_target`, `related_target`, `unknown`);
- surface variation (`same`, `near`, `different`);
- freshness (`fresh`, `previously_exposed`, `unknown`);
- ontology concept IDs when available;
- what is intentionally held constant;
- what is intentionally varied;
- source references and rationale.

M42 does not infer these fields from engine loss or free text. They are explicit inputs whose source authority remains external/upstream.

## Default policy

The v1 default requires a fresh candidate and rejects exact practice-position reuse by M10 `OutcomePosition.reuse_key`.

- near transfer: `same_target` plus `near` or `different` surface variation;
- far transfer: `same_target` or `related_target` plus `different` surface variation.

This is an inspectable product heuristic, not an empirically optimal transfer definition.

## Ontology policy

K0-K7 is optional semantic validation. M42 validates supplied concept IDs when an ontology snapshot is supplied but does not require a new ontology schema. Add ontology semantics only if a concrete transfer consumer proves K0-K7 cannot represent a necessary distinction safely.

## Rejection cases

M42 fails closed for:

- non-transfer M40 actions;
- proposal not belonging to the exact M40 plan;
- cross-participant M9 state;
- stale hypothesis revision;
- missing/unclear/ineligible M9 selection;
- selected intervention identity drift;
- exact practice-position replay;
- previously exposed candidates when freshness is required;
- near-only surface variation presented as far transfer;
- unknown ontology concepts when ontology validation is requested;
- tampered candidate, policy, or plan identities.

An empty eligible pool is a valid `no_eligible_candidate` result with explicit blocking uncertainty; it is not silently converted into a lower-quality test.
