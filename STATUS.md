# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-15  
**Historical V1 authority:** `VERSION_1_REPOSITORY_READY`  
**V1 implementation baseline:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`  
**Historical V1 release identity:** `chess-mentor-engine==1.0.0`  
**Current development identity:** `chess-mentor-engine==1.1.0.dev0`  
**Integrated post-V1 package:** PR #98 — `Post-V1 local product-use observation`  
**Post-V1 merge commit:** `a28b6b528e2bb823d9e4dfaa50da40f57760c7f5`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md) as the moving implementation authority, [`docs/runbooks/v1-post-milestone-handoff.md`](docs/runbooks/v1-post-milestone-handoff.md) for the historical V1 restart path, and [`docs/runbooks/post-v1-local-product-use-observation.md`](docs/runbooks/post-v1-local-product-use-observation.md) for the integrated post-V1 local product-use workflow.

## Integrated V1 state

All three bounded Version 1.0 packages remain integrated on `main`:

```text
[x] Package 1 — V1 local tutor vertical slice
[x] Package 2 — V1 architecture / authority reconciliation
[x] Package 3 — V1 release / distribution qualification
```

Historical integration provenance:

| Package | PR | Final head | Merge commit | Qualification |
| --- | --- | --- | --- | --- |
| Local tutor vertical slice | #94 | `9867105509e0f243a7823066d626abe1cad40148` | `2fd14c32e81d19222cc3e2f332337c00f8086f5f` | run `34642933193`: source + independent Stockfish PASS |
| Authority reconciliation | #95 | `f12758c52de3e13468774d13c324510d48e6d7d7` | `c41fda2f1c3c2002a4c960270b38ef3cce1ad144` | exact candidate gates PASS |
| Release/distribution | #96 | `4b5512a1b5d67ad0df43000898b5d371701d832c` | `8e3abf063b2af7d09a46495f5e35c85c86d58f01` | PR run `34673791962` PASS; post-merge run `34673834249` PASS |

There is no remaining repository-resolvable Version 1.0 package. Do not convert post-V1 work into a retroactive V1 blocker.

## Integrated post-V1 package — PR #98

The integrated package deliberately weakens the earlier idea of "learning validation" to **descriptive local product-use observation**.

Its repository claim is only that CME can make the selected M8 baseline path easier to exercise and can capture bounded facts about that use.

```text
claim_scope = descriptive_local_product_use_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

Integrated additions:

```text
1.1.0.dev0 development identity
post-v1.interaction-observation.v1 immutable observation artifacts
cme-local-tutor review
cme-local-tutor feedback
cme-local-tutor report
parameterized release-distribution identity in CI
post-V1 product/use spec, architecture boundary, plan, and runbook
```

### Integration provenance

```text
PR:                #98
Final PR head:     35dc40e08fd2b0e006f644b0a0846fef2edb51aa
Merge commit:      a28b6b528e2bb823d9e4dfaa50da40f57760c7f5
Exact PR CI:       run 34972510189 — PASS
Post-merge main:   run 34979411773 — PASS
```

The exact final PR head reported **974 passed and 8 intentional regular-job Stockfish skips**, followed by Ruff PASS and compileall PASS. The release-distribution and independent Stockfish jobs also passed. The post-merge `main` run passed all three jobs again.

### Guided-review boundary

```text
exact selected persisted M8 checkpoint
        |
        v
cme-local-tutor review
        |
        +-- existing M8 position presentation
        +-- existing M8 protocol-bound prompt presentation
        +-- existing M8 participant response capture
        +-- existing M8 response freeze
        +-- descriptive immutable observations
        |
        v
exact frozen M8 checkpoint
```

The command stops at baseline freeze. It does not reveal objective evidence, record comparison/explanation, complete the tutor session, generate M46, or execute M46. The operator may separately use the established `cme-local-tutor next` command to obtain the current proposal for the exact frozen checkpoint.

### Feedback/report boundary

`feedback` records three bounded 1–5 participant self-report ratings—review relevance, workflow clarity, and willingness to review again—plus an optional note. Self-report remains self-report.

`report` aggregates participant-scoped observation counts, explicit action names when present, and feedback metadata. The summary keeps learning effect, tutor efficacy, and mastery explicitly `not_established`.

## Durable authority boundaries

```text
objective chess truth != participant evidence != learner inference
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 selection
M42 transfer plan != M10 transfer evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis / implicit consent
M46 tutor proposal != M8 execution / exposure authority
post-V1 observation != learner inference / tutor efficacy / mastery
participant self-report != objective efficacy evidence
successful evidence case != mastery
repository qualification != real-user usefulness or hosted-product approval
```

## Remaining human / external-authority work

The integrated repository still does **not** establish or require:

- publication to PyPI or another registry;
- GitHub tag/release creation;
- branch-protection/ruleset administration;
- hosted deployment or production credentials;
- production authentication, multi-tenancy, privacy/security/compliance approval;
- production browser/device/accessibility/usability approval;
- real-participant usefulness;
- empirical tutoring efficacy;
- intervention-caused learning or mastery.

## Restart instruction

The repository-resolvable post-V1 observation package is integrated and qualified. The next meaningful evidence should come from actual local use: exercise repeated review sessions, record bounded self-report, inspect the deterministic product-use report, and identify the dominant demonstrated bottleneck.

Do **not** automatically implement M35/M37/M38/K8/M47, another learner-intelligence subsystem, browser UI, or hosted productization. Reconcile real observations first, classify the bottleneck and its authority owner, and authorize one bounded next objective only if the evidence warrants it.
