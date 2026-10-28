# Repo Sensemaker — Semantic Reasoning Alignment

**Status:** Phase 9 Pilot A contract guidance  
**Scope:** Methodological alignment only; the `repository_sensemaking_brief` artifact schema is unchanged.

## Purpose

`repo-sensemaker` is the first operationalization pilot for the Sensemaking Reasoning Model because it already sits at the transition from repository evidence to claims, uncertainty, and recommended next responsibility.

The Skill MUST preserve the following semantic chain for decision-changing reasoning:

```text
bound target/currentness
-> observation
-> evidence
-> claim
-> epistemic status
-> contradiction / uncertainty
-> weakest boundary / fog diagnosis
-> candidate next action
```

The chain may be represented in prose and existing brief sections. Phase 9 does not require new fields in the canonical brief.

## Alignment rules

1. **Observation is not inference.** A probe/file read may establish that an import, file, status line, test outcome, or relationship finding exists. Architectural quality, intent, root cause, and product meaning remain interpretations unless separately ratified.
2. **Every material inference names its evidence basis.** A decision-changing conclusion must be traceable to specific evidence already cited in the brief.
3. **Currentness is part of warrant.** A claim about current repository state must be bound to the mandatory state-currency probe or explicitly labeled as documented/unverified.
4. **Use epistemic language consistently.** When ambiguity matters, distinguish `OBSERVED`, `DERIVED`, `INFERRED`, `HYPOTHESIZED`, `RATIFIED`, `CONTRADICTED`, `SUPERSEDED`, and `UNRESOLVED` in prose rather than flattening them into equal-strength facts.
5. **Contradiction is not diagnosis.** A mechanical relationship finding or conflict between sources becomes a candidate contradiction; the model must still establish overlapping scope, currentness, and authority before using it diagnostically.
6. **Absence claims require bounded completeness.** No matches in an incomplete search does not establish absence. Preserve probe/search completeness and blind spots.
7. **Uncertainty is decision-relative.** Prefer uncertainties whose answers could change action, scope, authority, or stop/continue disposition. Do not create questions merely to fill a template.
8. **Fog type is not the uncertainty itself.** `architecture_fog`, `docs_fog`, `product_fog`, and `ui_fog` remain routing/diagnostic classifications; they do not replace the specific consequential question.
9. **Weakness type is not epistemic status.** `Contract Mismatch`, `Vocabulary Drift`, etc. classify diagnosed boundaries. They do not say whether a supporting claim was observed or inferred.
10. **Explicit limits are evidence.** Preserve what the analysis could not establish, especially unmeasured metrics, inaccessible surfaces, historical claims, and external operational state.

## Logic-trace pattern

For the weakest-boundary conclusion, prefer:

```text
Observed O1 + observed O2
-> derived relation R1
-> inferred claim C1
-> counter-evidence or limit L1
-> unresolved question U1
-> bounded weakest-boundary conclusion
```

Avoid:

```text
repo contains pattern X
-> therefore architecture/product is bad
```

without the intermediate semantic warrant.

## Compatibility with existing brief contract

The existing brief already provides appropriate surfaces:

- Section 7 — evidence + Logic trace + currentness;
- Section 8 — evidence excerpts;
- Section 13 — machine handoff and `representation_sufficiency`;
- Section 15 — optional `consequential_boundary` and `uncertainty`.

Use those surfaces before proposing new schema. A companion `semantic_reasoning_profile` may be produced for Phase 9 evidence, but it is not a replacement for the brief and is not automatically admitted as Campaign evidence.

## Pilot questions

The first pilot specifically tests whether the Skill can answer these without hidden jumps:

- Which statements were directly observed versus inferred?
- Which claims are current at the pinned target state?
- Which contradiction candidates require semantic review?
- What evidence supports the weakest-boundary conclusion?
- What decision-changing uncertainty remains?
- What would falsify or narrow the conclusion?
- What has not been established?

## Non-goals

This alignment does not add automatic claim scoring, uncertainty ranking, workflow selection, repository mutation, or a universal semantic graph.

See `docs/semantic-architecture/reasoning-model.md` and `docs/semantic-architecture/pilots/reasoning-profile-template.md`.
