---
name: strategic-repository-reconciliation
description: reconcile returned evidence against a prior strategic repository analysis, making claim, assumption, path, and strategic effects explicit without automatic strategy mutation.
---

# strategic-repository-reconciliation

Use this Skill after a prior `strategic_repository_analysis` has produced a
decision or inquiry and new evidence has returned.

## Responsibility

Produce:

`artifacts/strategic_reconciliation.md`

The active semantic agent owns interpretation. The artifact records the
interpretation; it does not mutate the prior analysis.

## Procedure

1. Identify the exact prior analysis reference and target repository/source state.
2. Identify the returned evidence and its provenance.
3. For each decision-relevant prior claim, declare one:
   `CONFIRM | REVISE | RETRACT | UNCHANGED`.
4. For each explicit prior assumption, declare one:
   `CONFIRM | RESOLVE | REVISE | INVALIDATE | UNCHANGED`.
5. Reconcile the prior construction path with one:
   `CONTINUE | REVISE | SUPERSEDE | CLOSE | NO_PATH_CHANGE`.
   When a declared lightweight path transition is materially implicated, optionally
   record `ESTABLISHED | PARTIAL | NOT_ESTABLISHED | SUPERSEDED | NO_CONCLUSION`
   for that transition. This is strategic provenance, not roadmap progress.
6. State one strategic effect:
   `NO_MODEL_CHANGE | REAFFIRM | REVISE_STRATEGY | REOPEN_ANALYSIS |
   OWNER_DECISION | THESIS_REVIEW_REQUIRED`.
7. Nominate a candidate next responsibility only when the strategic effect and
   existing authority warrant one.
8. Preserve the boundary that reconciliation does not grant implementation
   authority or establish semantic truth.
9. Write the canonical template and run the generic and strategic-companion
   validators.

```bash
python scripts/validate-artifact.py strategic_reconciliation artifacts/strategic_reconciliation.md
python scripts/validate-strategic-companion.py artifacts/strategic_reconciliation.md
```

## Laws

```text
returned evidence != interpreted evidence
reconciliation != automatic strategy mutation
candidate next responsibility != execution authorization
path transition effect != roadmap status
transition established != next transition selected
mechanical PASS != semantic truth
```