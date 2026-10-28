# Output Reconciler — Semantic Reasoning Alignment

**Status:** Phase 9 Pilot C guidance  
**Scope:** Preserve claim/evidence/currentness semantics while auditing completed-work assertions.

## Core distinction

`output-reconciler` evaluates **claims about work**, not the intrinsic truth of every domain conclusion produced by that work.

Preserve:

```text
artifact supports claim in scope
!= claim is universally true

validator passed
!= work achieved intended outcome

repository changed
!= claimed repair succeeded
```

## Reasoning chain

```text
work claim
-> falsifiable bounded claim
-> current target/evidence
-> like-for-like observation
-> claim classification
-> semantic limit / contradiction / uncertainty
-> disposition
```

## Classification semantics

### `verified`

Use when current durable evidence supports the audited claim **within the claim's stated baseline, scope, and comparison**. `verified` is an evidence-status verdict, not an unlimited truth label.

### `disputed`

Use when current evidence contradicts the claim, required evidence is absent where the claim requires it, or the claim overstates the scope of the available evidence.

### `omitted`

Use when the work claim leaves out a material condition shown by the durable evidence and the omission would change how the claim should be interpreted or acted upon.

## Currentness

Every current-state reconciliation must identify the target state being checked. Historical evidence can define baselines and prior expectations but cannot silently stand in for fresh current-state evidence.

## Like-for-like comparison

Before attributing a failure or success to a change, align:

```text
baseline
check/method
scope
configuration
claimed change
post-change target
```

A failure present on both baseline and candidate is `pre_existing`, not evidence that the candidate introduced it. A PASS under a narrower check is not evidence for a broader claim.

## Epistemic status mapping

The existing `verified | disputed | omitted` classification remains the artifact contract. During reasoning, map it carefully:

- `verified` usually rests on `OBSERVED`/`DERIVED` evidence plus bounded inference;
- `disputed` usually records `CONTRADICTED` or unsupported/over-broad claims;
- `omitted` identifies missing material context, not a fourth truth value.

Do not replace the existing artifact enum with the general ontology vocabulary during Phase 9.

## Explicit limits

For each consequential reconciliation, preserve what was not checked: runtime/user behavior, external systems, stale/unavailable evidence, broader semantic success, or unmatched baselines.

## Non-goals

This alignment does not authorize repairs, does not create new reconciliation-report fields, and does not let deterministic validators decide semantic warrant.

See `docs/semantic-architecture/reasoning-model.md` and `docs/semantic-architecture/pilots/reasoning-profile-template.md`.
