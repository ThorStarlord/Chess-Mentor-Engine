# M42–M46 Learner/Tutor Loop — Restart and Qualification Runbook

**Scope:** qualified post-M40 product loop covering transfer planning, learner-progress presentation, participant-scoped mentor queues, and adaptive tutoring proposals.

**Implementation authority:** [`../product/repository-build-status.md`](../product/repository-build-status.md)  
**Latest handoff:** [`../../STATUS.md`](../../STATUS.md)

## Qualified packages

```text
M42  Bounded Transfer / Retest Planning           PR #90
M45  Participant-Scoped Batch Mentor Queue        PR #91
M46  Adaptive Socratic Tutor Action Policy        PR #92
```

These packages extend the already-qualified M36/M39/M40/M41/M43/M44 learner-intelligence layer. They do not replace the upstream authority owners.

## Current end-to-end authority graph

```text
M7 / M7C learner hypothesis + recurrence / contradiction authority
+ M9 explicit intervention applicability / selection
+ M10 bounded practice / near / far / real-game outcome evidence
+ M11 append-only longitudinal learner state
+ optional K7 typed chess semantics
        |
        v
M36 deterministic learner-state read model
        |
        v
M39 hypothesis evidence synthesis
        |
        v
M40 next-session action proposal
        |
        +-- evidence need --> M43 acquisition candidates
        +-- teaching need --> M41 intervention candidates
        +-- transfer need --> M42 bounded transfer/retest plan
        `-- explanation ----> M44 learner-progress reference surface

bounded M4D diagnostic batch + explicit participant scope
        |
        v
M45 mentor queue
        |
        v
exact M8 controlled tutor lifecycle
        + optional M44 learner context
        + optional M45 queue item
        + optional M42 transfer plan
        |
        v
M46 next pedagogical action proposal
        |
        v
M8 remains execution / exposure / capture / reveal authority
        |
        v
post-reveal reflection and later M10 outcome evidence
```

## M42 — transfer / retest planning

Public module: `chess_mentor_engine.learner_intelligence.transfer_retest`

M42 consumes an exact M40 `RUN_NEAR_TRANSFER_TEST` or `RUN_FAR_TRANSFER_TEST` proposal plus exact M9 selection/intervention state and bounded candidate positions.

It provides:

```text
m42.transfer-position-candidate.v1
m42.transfer-retest-policy.v1
m42.transfer-retest-plan.v1
```

Important rules:

- exact practice-position reuse is excluded using M10-compatible reuse keys;
- near/far candidates state what is held constant and what varies;
- freshness and prior exposure are explicit;
- no eligible candidate becomes an explicit no-plan/gap result;
- M42 never creates M10 attempt, observation, outcome, transfer, or mastery evidence.

The M44 reference surface has an additive transfer-plan presentation path. It keeps planned, completed, successful transfer, and mastery structurally distinct.

## M45 — participant-scoped mentor queue

Public module: `chess_mentor_engine.learner_intelligence.mentor_queue`

M45 binds an exact participant-agnostic M4D diagnostic batch to explicit participant-local provenance, then ranks a bounded review queue.

The default policy uses separate deterministic dimensions for:

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

The ranking is transparent and deterministic. It is not a learned weakness score and does not reduce learner priority to centipawn loss.

M45 may consume exact M44/M43/M42 context when available. Objective-only candidates remain objective-only instead of being assigned fabricated learner relevance.

## M46 — adaptive Socratic tutor action policy

Public namespace: `chess_mentor_engine.tutoring`

M46 provides:

```text
m46.adaptive-tutor-policy.v1
m46.adaptive-tutor-proposal.v1
```

Its central invariant is:

```text
M46 chooses a proposed next tutoring action
!= M8 authorizes and records the actual exposure/capture/reveal transition
```

Qualified behavior:

```text
M8 selected/presented/capturing
    -> CONTINUE_BASELINE_CAPTURE
    -> no adaptive hint or reveal

M8 frozen + evidence/challenge intent
    -> objective reveal may be proposed

M8 frozen + teaching intent
    -> bounded recognition/minimal hint may be proposed
    -> assisted response stays assisted evidence

M8 frozen + transfer intent
    -> exact M42 transfer plan required

M8 revealed/compared/explained
    -> ASK_REFLECTION
    -> post-reveal reflection, never baseline evidence

M8 completed
    -> NO_FURTHER_ACTION
```

Every deterministic proposal records:

```text
execution_authority = proposal_only
model_language = not_generated
mastery = not_established
```

M46 validates exact participant, tutor-session snapshot, M44 learner view, optional M45 queue/item, and optional M42 transfer-plan identities. It does not mutate M7/M11, create M10 outcomes, call a live model, or bypass M8's pre-reveal measurement boundary.

The public M46 exports are lazy-loaded from `chess_mentor_engine.tutoring` to avoid coupling the established tutoring import graph to learner-intelligence initialization.

## Product-pulled ontology rule

K0–K7 was sufficient for M42, M45, and M46. Do not create a generic K8 merely to expand vocabulary.

```text
consumer demonstrates missing semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum extension
-> add rejection tests
-> qualify ontology + requesting consumer together
```

## Focused qualification

```bash
python -m pytest tests/test_m42_transfer_retest_planning.py -rs
python -m pytest tests/test_m42_m44_transfer_reference.py -rs
python -m pytest tests/test_m45_batch_mentor_queue.py -rs
python -m pytest tests/test_m46_adaptive_socratic_tutor.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

## Promotion evidence

### M42 / PR #90

```text
final head   4df41644b4b5ffdd9abf54d349b7048f0e514078
merge commit c8af423f37c9ad7a423594ffa5d43f83c2b2d4ab
CI run       34623130217
result       925 passed, 8 regular-job Stockfish skips; Ruff/compile PASS;
             independent Stockfish PASS
```

### M45 / PR #91

```text
final head   0af40490d9a7a70699b1d015d65a53fb86af66f2
merge commit 725de02a27c836e7fe150cc3874482cf45511444
CI run       34624375982
result       full pytest/Ruff/compile gate PASS; independent Stockfish PASS
```

### M46 / PR #92

```text
final head   cc89c5cf1402d02cadf76fa0d80c903296d51aea
merge commit 3ec19446b4957d4e8f20ed3865b7d090d55c3cb5
CI run       34629592288
result       939 passed, 8 regular-job Stockfish skips; Ruff/compile PASS;
             independent Stockfish PASS
```

## Restart checklist

1. Read `STATUS.md` and `docs/product/repository-build-status.md`.
2. Start from fresh live `main`; do not infer work from old candidate numbering.
3. Reproduce the full gate before changing authority-sensitive contracts.
4. Identify the concrete learner-facing consumer that requires the next change.
5. Reuse M7C, M9, M10, M8, and K0–K7 instead of creating parallel authority systems.
6. Treat M35/M37/M38/K8 as unimplemented labels unless a concrete blocker pulls one forward.
7. Prefer a concrete end-to-end local consumer over another infrastructure layer unless a fresh audit proves infrastructure is the blocker.

## Next decision boundary

The repository now has enough backend pieces to run a coherent local learner/tutor decision loop. The next milestone should therefore begin with a product audit, not an automatic milestone number.

The strongest competing directions are:

```text
A. concrete end-to-end local consumer
   recent games -> M45 queue -> M8/M46 tutoring -> reflection -> M42/M10 retest

B. M47 bounded multi-session study plan
   only if composing several already-qualified actions is the active product need
```

Do not automatically choose M47 merely because it is the next roadmap label. External usefulness, production UI quality, empirical tutoring efficacy, privacy/security, hosted auth/multi-tenancy, and production provider operations remain external/human authority gates.
