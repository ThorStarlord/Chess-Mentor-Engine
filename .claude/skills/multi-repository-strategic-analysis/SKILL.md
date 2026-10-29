---
name: multi-repository-strategic-analysis
description: analyze an explicitly selected repository set at Level 3 to model capability ownership, overlaps, cross-repository boundaries, coherent allocation/construction paths, tradeoffs, and a strategic disposition without automatic scope expansion or orchestration.
---

# multi-repository-strategic-analysis

Use when the strategic question concerns **how multiple explicitly selected
repositories should relate or divide product/capability responsibility**.

Do not use this Skill merely because one repository has a dependency on another.
Use it when repository boundaries or capability allocation are part of the
decision.

## Responsibility

Produce:

`artifacts/multi_repository_strategic_analysis.md`

The active semantic agent owns the analysis. Deterministic validation owns only
representation/reference integrity.

## Inputs

Require:

1. explicit target repository set supplied by the user/owner/caller;
2. stable aliases for those targets;
3. governing product/owner intent;
4. current evidence from each selected repository;
5. explicit cross-repository relations when available.

Never add a repository to the target set merely because search discovers it.

## Procedure

### 1. Establish scope and authority

Record each target's:

- alias;
- repository identity;
- source identity;
- role;
- evidence references;
- mutation authority status when relevant.

Analysis authority does not imply implementation authority.

### 2. Build the multi-repository system model

Explain the product/system formed by the selected repositories and the major
interfaces/control boundaries between them.

### 3. Map capability ownership

For each decision-relevant capability record:

- capability ID;
- current owner aliases;
- state: `ESTABLISHED | PARTIAL | MISSING | DEFERRED | BLOCKED |
  CLAIMED_UNVERIFIED | OUT_OF_SCOPE`;
- evidence references;
- overlap/boundary consequence.

### 4. Reuse or record relationship evidence

When existing explicit relations are available, preserve the canonical classes:

`depends_on | provides_interface_to | consumes_interface_from |
must_change_with | release_after`.

Do not persist inferred relations into Campaign state. Strategic observations
remain claims in this artifact.

### 5. Identify boundary tensions

Examples:

- unclear capability owner;
- harmful duplication;
- necessary duplication;
- unstable interface boundary;
- release coupling;
- duplicated policy/contract authority;
- one repository becoming an accidental container for another.

Only include decision-relevant tensions.

### 6. Generate 0–5 coherent boundary/allocation paths

Each path must state:

- future multi-repository state;
- capability allocations;
- interface/boundary changes;
- coarse construction sequence;
- dependencies;
- unlocks;
- risks/tradeoffs;
- reversibility;
- evidence gaps.

Do not force consolidation, protocol extraction, or separation merely because the
pattern is familiar.

### 7. Compare paths qualitatively

Use the canonical Level-3 lenses. No scoring/ranking.

### 8. Identify decision-changing uncertainty

Name only the premise that could materially change the allocation/boundary
judgment. Respect repository/owner/external evidence source boundaries.

### 9. Synthesize one disposition

`BUILD | INVESTIGATE | DEFER | NO_CHANGE | OWNER_DECISION | THESIS_REVIEW`.

For `BUILD`, nominate one bounded responsibility and the affected target aliases.
Do not emit an execution schedule.

### 10. Validate

```bash
python scripts/validate-artifact.py multi_repository_strategic_analysis artifacts/multi_repository_strategic_analysis.md
python scripts/validate-multi-repository-strategic-analysis.py artifacts/multi_repository_strategic_analysis.md
```

## Required laws

```text
explicit repository set != automatic discovery
relationship recorded != architectural truth
capability overlap != defect automatically
construction path != backlog
allocation proposed != implementation authorized
path comparison != numeric ranking
multi-repository analysis != transaction coordinator
```
