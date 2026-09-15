# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-15  
**Integrated main authority:** `VERSION_1_REPOSITORY_READY`  
**V1 implementation baseline:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`  
**Historical V1 release identity:** `chess-mentor-engine==1.0.0`  
**Post-V1 development identity:** `chess-mentor-engine==1.1.0.dev0`  
**Active candidate:** PR #98 — `Post-V1 local product-use observation`

This handoff separates the already-integrated Version 1.0 authority from the post-V1 candidate currently under review. PR #98 is not current-main integration authority until its exact final head passes the repository gates and merges.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md) as the moving implementation authority, [`docs/runbooks/v1-post-milestone-handoff.md`](docs/runbooks/v1-post-milestone-handoff.md) for the historical V1 restart path, and [`docs/runbooks/post-v1-local-product-use-observation.md`](docs/runbooks/post-v1-local-product-use-observation.md) for the active candidate workflow.

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

The V1 source suite at release qualification reported 957 passed plus 8 intentional regular-job Stockfish skips, followed by Ruff and compileall PASS. The independent Stockfish job separately qualified the real-engine path.

There is no remaining repository-resolvable Version 1.0 package. Do not convert post-V1 work into a retroactive V1 blocker.

## Active post-V1 candidate — PR #98

The candidate deliberately weakens the earlier idea of "learning validation" to **descriptive local product-use observation**.

Its repository claim is only that CME can make the selected M8 baseline path easier to exercise and can capture bounded facts about that use.

```text
claim_scope = descriptive_local_product_use_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

Candidate additions:

```text
1.1.0.dev0 development identity
post-v1.interaction-observation.v1 immutable observation artifacts
cme-local-tutor review
cme-local-tutor feedback
cme-local-tutor report
parameterized release-distribution identity in CI
post-V1 product/use spec, architecture boundary, plan, and runbook
```

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

The command stops at baseline freeze. It does not reveal objective evidence, record comparison/explanation, complete the tutor session, or execute M46. The operator may separately use the established `cme-local-tutor next` command to obtain the current proposal for the exact frozen checkpoint.

### Feedback/report boundary

`feedback` records three bounded 1–5 participant self-report ratings—review relevance, workflow clarity, and willingness to review again—plus an optional note. Self-report remains self-report.

`report` aggregates participant-scoped observation counts, explicit action names when present, and feedback metadata. The summary also keeps learning effect, tutor efficacy, and mastery explicitly `not_established`.

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
successful evidence case != mastery
repository qualification != real-user usefulness or hosted-product approval
```

## Qualification gate for PR #98

The exact final PR head must pass:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
```

and the independent CI jobs:

```text
test-and-lint
release-distribution
stockfish-integration
```

Development artifacts use the version currently declared in `pyproject.toml`; CI no longer hard-codes the historical V1 filename.

## Remaining human / external-authority work

Neither V1 nor PR #98 establishes or requires:

- publication to PyPI or another registry;
- GitHub tag/release creation;
- branch-protection/ruleset administration;
- hosted deployment or production credentials;
- production authentication, multi-tenancy, privacy/security/compliance approval;
- production browser/device/accessibility/usability approval;
- real-participant usefulness;
- empirical tutoring efficacy;
- intervention-caused learning or mastery.

Real repeated sessions and participant feedback are the next external evidence source after the repository candidate is integrated. They should identify the dominant bottleneck before another learner-intelligence subsystem, ontology expansion, browser UI, or hosted productization package is authorized.

## Restart instruction

If PR #98 is still open, reconcile its exact head and CI before changing behavior. If it has merged, use the post-V1 runbook to exercise real local sessions and collect descriptive evidence. Do not automatically implement the next feature in the same campaign; first classify the demonstrated bottleneck and its existing authority owner.
