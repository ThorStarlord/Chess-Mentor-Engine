# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-11  
**Contiguous numbered baseline:** M1–M34 qualified  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7  
**Qualified post-M34 learner-intelligence packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46  
**Post-feature baseline:** `3ec19446b4957d4e8f20ed3865b7d090d55c3cb5`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority and
[`docs/runbooks/m42-m46-learner-tutor-loop.md`](docs/runbooks/m42-m46-learner-tutor-loop.md)
for the latest focused restart/qualification path.

## Current outcome

The learner/tutor-loop milestone is complete:

```text
M42  Bounded Transfer / Retest Planning             MERGED - PR #90
M45  Participant-Scoped Batch Mentor Queue          MERGED - PR #91
M46  Adaptive Socratic Tutor Action Policy          MERGED - PR #92
```

These extend the previously qualified M36/M39/M40/M41/M43/M44 layer. Numbering remains intentionally non-contiguous. **M35, M37, and M38 are not implied to be implemented.** K8 is also not implied or required.

## Strongest qualified learner/tutor chain

```text
M7 / M7C learner hypothesis + recurrence / contradiction authority
+ M9 intervention applicability / selection authority
+ M10 bounded practice / near / far / real-game outcome evidence
+ M11 longitudinal learner state
+ optional K7 typed chess semantics
        |
        v
M36 deterministic learner-state read model
        |
        v
M39 exact hypothesis evidence synthesis
        |
        v
M40 ranked next-session action proposal
        |
        +-- evidence need --> M43 acquisition candidates
        +-- teaching need --> M41 intervention candidates
        +-- transfer need --> M42 bounded transfer/retest plan
        `-- explanation ----> M44 learner-progress reference surface

bounded M4D diagnostic batch + explicit participant scope
        |
        v
M45 participant-scoped mentor queue
        |
        v
exact M8 controlled tutor lifecycle
+ optional M44 learner context
+ optional M45 queue item
+ optional M42 transfer plan
        |
        v
M46 proposed next Socratic question / hint / reveal / reflection
        |
        v
M8 remains actual execution / exposure / capture / reveal authority
        |
        v
later M10 outcome evidence and M11 longitudinal state
```

The repository has therefore moved beyond merely representing evidence. It can now deterministically assemble current learner state, explain why a learner hypothesis is held, propose a next learning action, prepare challenge/training/transfer candidates, prioritize a bounded review queue, and choose a bounded next tutoring action while preserving the evidence-measurement boundary.

## M42 — Bounded Transfer / Retest Planning

**PR:** #90  
**Final head:** `4df41644b4b5ffdd9abf54d349b7048f0e514078`  
**Merge commit:** `c8af423f37c9ad7a423594ffa5d43f83c2b2d4ab`  
**CI run:** `34623130217`

M42 adds content-addressed transfer-position candidates, a versioned transfer/retest policy, and content-addressed transfer/retest plans for exact M40 near/far-transfer proposals.

It binds exact M40 and M9 identities, uses M10-compatible reuse keys to reject exact practice replay, makes semantic relation/surface variation/freshness/exposure explicit, and returns an explicit no-eligible-candidate result rather than weakening the policy.

M42 also adds an additive M44 transfer-plan reference presentation while keeping the existing M44 v1 learner-progress contract unchanged.

```text
M42 plan != M10 outcome evidence
planned != completed
completed != successful transfer
successful transfer != mastery
```

Final qualification:

```text
925 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

## M45 — Participant-Scoped Batch Mentor Queue

**PR:** #91  
**Final head:** `0af40490d9a7a70699b1d015d65a53fb86af66f2`  
**Merge commit:** `725de02a27c836e7fe150cc3874482cf45511444`  
**CI run:** `34624375982`

M45 binds an exact participant-agnostic M4D diagnostic batch to explicit participant-local provenance and produces a bounded deterministic mentor queue.

Ranking dimensions remain separate and inspectable:

```text
M40 action alignment
contradiction / control value
transfer value
learner relevance
uncertainty reduction
bounded objective importance
novelty
semantic diversity
```

Learner/challenge/transfer value can outrank a larger centipawn-loss position. Objective-only candidates remain objective-only with zero learner relevance rather than acquiring fabricated learner claims.

```text
M45 queue rank != learner hypothesis
M45 queue rank != M9 selection
M45 queue rank != M10 outcome
M45 queue rank != empirically optimal review order
```

Final qualification: full repository pytest, Ruff, compileall, and independent Stockfish gate PASS on the exact final head.

## M46 — Adaptive Socratic Tutor Action Policy

**PR:** #92  
**Final head:** `cc89c5cf1402d02cadf76fa0d80c903296d51aea`  
**Merge commit:** `3ec19446b4957d4e8f20ed3865b7d090d55c3cb5`  
**CI run:** `34629592288`

M46 adds a deterministic adaptive-tutor policy/proposal over the exact M8 tutor lifecycle.

Central invariant:

```text
M46 proposes the next pedagogical action
!= M8 authorizes and records the actual tutoring transition
```

Qualified behavior preserves clean measurement:

```text
before M8 baseline freeze -> CONTINUE_BASELINE_CAPTURE only
frozen + evidence/challenge intent -> objective reveal may be proposed
frozen + teaching intent -> bounded assisted hint may be proposed
frozen + transfer intent -> exact M42 transfer plan required
post-reveal -> ASK_REFLECTION as post-reveal evidence
completed -> NO_FURTHER_ACTION
```

Every deterministic M46 proposal states:

```text
execution_authority = proposal_only
model_language = not_generated
mastery = not_established
```

M46 validates exact M8/M44 identity and optionally exact M45 queue/item and M42 transfer-plan identity. It does not mutate learner state, generate live model prose, create M10 outcomes, or bypass M8 pre-reveal capture rules.

The public M46 exports are lazy-loaded from `chess_mentor_engine.tutoring` so the established tutoring import graph remains stable.

Final qualification:

```text
939 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

## Durable authority boundaries

Preserve all of these:

```text
objective chess truth != participant evidence != learner inference
concept definition != concept assertion != learner inference
K7 ontology projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping or selection
M42 transfer plan != M10 transfer evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis or intervention selection
M46 tutor proposal != M8 tutoring execution / exposure authority
assisted response != baseline unassisted evidence
post-reveal reflection != pre-reveal evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
```

## Product-pulled ontology rule

M42, M45, and M46 all shipped without a generic K8. That is the desired default.

```text
concrete learner/tutor consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum ontology extension
-> add rejection tests
-> consume it in the requesting feature
-> qualify ontology + consumer together
```

Do not expand ontology coverage merely to increase vocabulary or detector count.

## Current operational boundary

M36/M39/M40/M41/M42/M43/M44/M45/M46 are deterministic Python APIs and/or local reference surfaces. Existing M12–M30 commands remain the established CLI/operator surface. This milestone adds no production frontend, hosted runtime, paid/live model call, or production credential requirement.

The repository still cannot mechanically establish:

- real participant usefulness or approval;
- production browser/device/accessibility/usability quality;
- empirically effective or optimal tutoring policy;
- intervention-caused learning or mastery;
- production privacy/security/compliance posture;
- hosted authentication or multi-tenancy readiness;
- production provider retry/cost/secrets operations.

## Next decision boundary

**Do not automatically start another backend milestone.** The backend learner/tutor loop is now coherent enough that the next work should be pulled by a concrete product bottleneck.

A fresh live-main audit should choose between two leading directions:

1. **Concrete end-to-end local consumer** (`REPOSITORY_ONLY / HERMETIC_VALIDATION`)
   - make the already-qualified path easy to exercise as one local workflow:
     `recent games -> M45 queue -> M8/M46 tutoring -> reflection -> M42/M10 retest`;
   - reuse existing contracts rather than add a new authority layer;
   - this is the preferred default if the product is currently hard to experience end to end.
2. **M47 bounded multi-session study plan** (`REPOSITORY_ONLY / HERMETIC_VALIDATION`)
   - only if the active product need is composing several existing M40/M41/M42 actions into a short revisable plan;
   - preserve revision history, contradiction/retest checkpoints, and no mastery/optimality claim.

M35/M37 should be pulled forward only by a concrete operator/compatibility blocker. M38 must not become a second recurrence engine; reuse M7C. K8 must remain product-pulled.
