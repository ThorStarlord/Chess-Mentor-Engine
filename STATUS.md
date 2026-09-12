# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-12  
**Milestone state:** `INTEGRATED / CURRENT-MAIN AUTHORITY`  
**Current main:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`  
**Release identity:** `chess-mentor-engine==1.0.0`  
**Version 1.0 status:** `VERSION_1_REPOSITORY_READY`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority,
[`docs/runbooks/v1-post-milestone-handoff.md`](docs/runbooks/v1-post-milestone-handoff.md)
for the Version 1.0 restart/qualification path,
[`docs/runbooks/v1-local-tutor-vertical-slice.md`](docs/runbooks/v1-local-tutor-vertical-slice.md)
for the local-consumer contract, and
[`docs/runbooks/v1-release-distribution-qualification.md`](docs/runbooks/v1-release-distribution-qualification.md)
for the release-artifact contract.

## Current V1 state

All three bounded Version 1.0 packages are integrated:

```text
[x] Package 1 — Qualify & Integrate V1 Local Tutor Vertical Slice
[x] Package 2 — Reconcile V1 Architecture & Repository Authorities
[x] Package 3 — V1 Release Candidate & Distribution Qualification
```

There are no additional repository-resolvable Version 1.0 packages in the queue.
Do not convert optional or post-V1 ideas into retroactive V1 blockers.

## What the milestone delivered

### Package 1 — local tutor vertical slice

**PR:** #94  
**Final head:** `9867105509e0f243a7823066d626abe1cad40148`  
**Merge commit:** `2fd14c32e81d19222cc3e2f332337c00f8086f5f`

Delivered the installed `cme-local-tutor start|next` composition surface over exact,
already-qualified M18/M44/(optional M42) artifacts, M45 mentor prioritization, explicit
selection/capture consent, M23/M8 persistence, and bounded M46 next-action proposal.
The layer remains composition-only: it does not create a second learner model, silently
select an intervention, execute tutoring, establish transfer, or claim mastery.

### Package 2 — architecture / authority reconciliation

**PR:** #95  
**Final head:** `f12758c52de3e13468774d13c324510d48e6d7d7`  
**Merge commit:** `c41fda2f1c3c2002a4c960270b38ef3cce1ad144`

Reconciled architecture and repository authorities with the integrated local-consumer
state, preserved the existing authority boundaries, and made release/distribution
qualification the sole remaining repository-resolvable V1 package at that point.

### Package 3 — release candidate / distribution qualification

**Implementation PR:** #96 — `V1: qualify release distributions`  
**Branch:** `work/v1-release-distribution`  
**Final head:** `4b5512a1b5d67ad0df43000898b5d371701d832c`  
**Merge commit / current-main authority:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`  
**PR candidate CI:** run `34673791962` — PASS  
**Post-merge main CI:** run `34673834249` — PASS

Package 3 synchronized package/runtime identity at `1.0.0`, added deterministic
wheel/sdist contract validation and rejection tests, added an independent
`release-distribution` CI job, clean-installed the built wheel in a fresh environment,
smoked all promised installed commands and package data, and preserved full source and
independent Stockfish qualification.

Exact successful gate on the final candidate and again on merged `main`:

```text
test-and-lint          PASS
release-distribution   PASS
stockfish-integration  PASS
```

The source suite on the final candidate reported **957 passed and 8 intentional regular-job
Stockfish skips**, followed by Ruff PASS and compileall PASS. The independent Stockfish
job separately qualified the real-engine path.

## CI failure triage retained for future debugging

An earlier PR #96 candidate, head `80a85b316ef6accaf02043e102020ff41a1002d4`,
had CI run `34663723350` fail in `test-and-lint` while `release-distribution` and
`stockfish-integration` both passed.

**Classification:** `IMPLEMENTATION_FAILURE`.

The failing source test invocation used bare `pytest`; the V1 release tests then failed to
import repository-local `tools.release_qualification` with `ModuleNotFoundError: No module
named 'tools'`. This was not an API-key failure, not a retired workflow, and not an
external-service outage. Commit `4b5512a1b5d67ad0df43000898b5d371701d832c`
aligned CI with the documented full gate, `python -m pytest -rs`. The exact corrected head
then passed every required package-defined job and merged.

The connected GitHub App cannot read the classic `main` branch-protection endpoint; the
repository-level ruleset list was empty during this handoff audit. That uncertainty does
not affect the integration claim: PR #96 is merged and both its exact final candidate and
the resulting `main` commit have successful CI evidence.

## Current qualified architecture boundary

The strongest integrated local path remains:

```text
M7 / M7C learner hypothesis + recurrence / contradiction authority
+ M9 intervention applicability / selection authority
+ M10 bounded practice / near / far / real-game outcome evidence
+ M11 longitudinal learner state
+ optional K7 typed chess semantics
        |
        v
M36 -> M39 -> M40
        |
        +-- evidence need --> M43 acquisition candidates
        +-- teaching need --> M41 intervention candidates
        +-- transfer need --> M42 bounded transfer/retest plan
        `-- explanation ----> M44 learner-progress reference surface

exact M18 diagnostic queue
+ exact M44 learner-progress view
+ optional exact M42 transfer plan(s)
        |
        v
cme-local-tutor
        |
        v
M45 participant-scoped mentor queue
        |
        v
explicit operator selection + capture consent
        |
        v
M23 -> exact persisted M8 checkpoint
        |
        v
M46 proposed next Socratic action
        |
        v
existing cme tutor commands remain M8 execution / exposure authority
```

Durable boundaries still include:

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
successful evidence case != mastery
repository release qualification != hosted-product approval
```

## Operational restart

Development and qualification commands are recorded in
[`docs/runbooks/v1-post-milestone-handoff.md`](docs/runbooks/v1-post-milestone-handoff.md).
The key gates are:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Release-artifact qualification additionally builds wheel + sdist, validates the artifact
contract with `python -m tools.release_qualification`, clean-installs the wheel, and
smokes all installed command/package-data surfaces.

## Remaining human / external-authority gates

Repository-qualified Version 1.0 does **not** establish or require:

- publication to PyPI or another registry;
- a GitHub release/tagging policy decision;
- hosted deployment or production credentials;
- production authentication, multi-tenancy, privacy/security/compliance approval;
- production browser/device/accessibility/usability approval;
- real-participant usefulness or product approval;
- empirically optimal tutoring policy;
- intervention-caused learning or mastery.

These are future product/release decisions or external evidence, not hidden repository V1
work.

## Recommended next milestone priorities

Start the next session by choosing **one concrete post-V1 objective** rather than reviving
unimplemented labels automatically:

1. **Distribution/release operations** — decide whether `1.0.0` should be tagged,
   published, or attached to a GitHub Release; publication is an owner/external-authority
   action, not a repository-readiness prerequisite.
2. **Hosted-product productization** — only if that is now the product goal, define the
   smallest explicit auth/privacy/security/persistence/deployment boundary before adding
   infrastructure.
3. **Real-user validation** — define participant/usability or pedagogical evidence if the
   next question is whether the tutor is useful rather than whether the repository is
   coherent.
4. **Product evolution** — create M47, K8, provider abstraction, cross-surface work, or
   other features only when a demonstrated consumer/product bottleneck requires them.

Every future milestone should begin by reconciling live `main`, current product intent,
and the authority owner for the problem before creating a new package.
