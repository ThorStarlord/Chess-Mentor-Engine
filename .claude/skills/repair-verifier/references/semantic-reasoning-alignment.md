# Repair Verifier — Semantic Reasoning Alignment

**Status:** Phase 9 Pilot C guidance  
**Scope:** Distinguish measured non-reproduction, outcome evidence, and semantic repair success.

## Core distinction

The Skill must preserve:

```text
repository changed
!= original finding no longer reproduces
!= validation passed
!= intended outcome achieved
!= repair semantically succeeded
```

`repair-verifier` can establish strong **post-change evidence** because it re-runs bounded deterministic probes. It must nevertheless state exactly what those probes cover.

## Reasoning chain

Prefer:

```text
prior finding / success condition
-> fresh target/currentness
-> fresh observation
-> like-for-like comparison
-> closure claim with epistemic status
-> remaining uncertainty / limits
-> gate disposition
```

### `closed`

`closed` means the named original finding no longer reproduces under the declared fresh check and scope. It does not automatically mean every semantic consequence or user-facing outcome of the repair has succeeded.

### `remaining`

`remaining` means the finding still reproduces under the fresh check. Preserve fresh evidence, disposition, and reason.

### Repair success

A semantic `repair succeeded` conclusion is warranted only when the repair's stated success conditions are actually covered by the verification evidence. If the Skill verifies only a structural symptom, say so.

## Epistemic language

Typical post-change statuses:

```text
OBSERVED: fresh probe emitted value V
DERIVED: original finding no longer matches the fresh probe condition
INFERRED: the bounded structural defect is resolved within this verification scope
UNRESOLVED: user/runtime consequence was not tested
```

Do not use `RATIFIED` merely because a gate passed.

## Currentness

Verification must bind to the post-change repository state. Historical or pre-change evidence may define acceptance criteria but cannot establish closure by itself.

## Explicit limits

State material gaps such as:

- probe does not exercise runtime behavior;
- only one platform/configuration was checked;
- no user-level acceptance evidence exists;
- a related but distinct finding was deferred;
- the original success condition was broader than the mechanical probe.

## Non-goals

This alignment does not make the verifier a semantic truth engine, does not authorize follow-up mutation, and does not redefine the canonical `repair_verification_report` schema during Phase 9.

See `docs/semantic-architecture/reasoning-model.md` and `docs/semantic-architecture/pilots/reasoning-profile-template.md`.
