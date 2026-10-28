# Architectural Review — Semantic Reasoning Alignment

**Status:** Phase 9 Pilot B guidance  
**Scope:** Align architectural judgment with the shared Reasoning Model without turning the review into a repository re-diagnosis or deterministic architecture scorer.

## Purpose

`architectural-review` consumes an upstream `repository_sensemaking_brief` and evaluates a proposed direction. This makes it a contrasting pilot: unlike `repo-sensemaker`, it normally inherits repository evidence rather than collecting it directly.

The Skill should reason through:

```text
inherited target/currentness
-> inherited observations/evidence
-> architectural entities/relations needed for this proposal
-> architectural claims + epistemic status
-> risk / contradiction / uncertainty
-> verdict + conditions
-> explicit limits
```

## Core distinctions

### Upstream artifact authority is bounded

The brief is authoritative for the workflow's **diagnostic input contract** and the evidence it actually contains. It is not universal semantic truth.

Therefore:

```text
consume brief without re-diagnosing
!=
blindly upgrade every brief sentence to RATIFIED truth
```

If the review notices that the brief lacks the evidence/currentness needed to evaluate the proposal, return `investigate_first` rather than silently filling the gap.

### Observed dependency is not architectural violation

Prefer the following chain:

```text
inherited/observed dependency edge
+ ratified or documented boundary/contract
-> comparison
-> INFERRED conflict/violation claim
-> architectural judgment
```

Do not collapse `A imports B` into `A violates the architecture` unless the relevant architectural rule, scope, and authority are also established.

### Component and boundary are semantic abstractions

`Component`, `Layer`, `Boundary`, and `Contract` should be created only to the resolution needed for the proposed direction. File/folder names do not automatically define canonical components or layers.

### Risk is not defect

A proposed direction may introduce a risk without that risk being an observed defect. Preserve whether a risk is:

- grounded in current evidence;
- inferred from architecture;
- hypothetical contingent on the proposed direction;
- unresolved because required evidence is missing.

## Pilot B review questions

- What currentness boundary did the review inherit from the brief?
- Which evidence is reused rather than recollected?
- Which architectural relation is directly supported and which is inferred?
- What architectural intent is ratified, merely documented, or hypothesized?
- Does the proposed direction address the demonstrated boundary or a different one?
- Which risks are observed versus hypothetical?
- What evidence would change `pursue`, `pursue_narrowed`, `investigate_first`, `defer`, or `reject`?
- What is explicitly outside the review's lens?

## Suggested claim language

Use concise labels only when they clarify decision-changing reasoning:

```text
OBSERVED/INHERITED: brief evidence states ...
RATIFIED: accepted architecture decision establishes ...
INFERRED: given those two facts, the proposal would cross ...
HYPOTHESIZED: this may create ... if ...
UNRESOLVED: available evidence does not establish ...
```

The labels are not mandatory decoration for every sentence.

## Compatibility

No new fields are required in `architectural_review_recommendation` during Pilot B. The companion `semantic_reasoning_profile` captures comparable Phase 9 evidence. A common artifact envelope is considered only after contrasting pilots show stable reuse.

## Non-goals

This alignment does not:

- re-run repository diagnosis;
- rank architecture styles automatically;
- infer intended architecture from directory layout alone;
- treat validator PASS as architectural correctness;
- add mutation authority;
- change the existing decision enum.

See `docs/semantic-architecture/reasoning-model.md` and `docs/semantic-architecture/pilots/reasoning-profile-template.md`.
