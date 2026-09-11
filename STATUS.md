# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-11  
**Numbered baseline:** M1–M34 qualified  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7  
**Qualified post-M34 learner-intelligence packages:** M36, M39, M40  
**Post-feature baseline:** `a10cdd36925af9a09a4e10c56fa7913bddba0f44`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority and
[`docs/runbooks/m36-m40-learner-intelligence.md`](docs/runbooks/m36-m40-learner-intelligence.md)
for the latest focused qualification/restart path.

## Current outcome

The requested learner-intelligence milestone is complete:

```text
M36  Deterministic Learner-State Read Model       MERGED - PR #82
M39  Hypothesis Evidence Synthesizer              MERGED - PR #83
M40  Teaching-Priority / Next-Session Planner     MERGED - PR #84
```

The numbering is intentionally non-contiguous. **M35, M37, and M38 are not implied
to be implemented.** Their planning labels remain candidate-only unless a future
live-main audit promotes or supersedes them.

The newly qualified chain is:

```text
M7/M7C learner hypothesis + recurrence/contradiction authority
+ M9 intervention-selection evidence
+ M10 bounded practice/transfer evidence
+ M11 longitudinal learner state
+ optional K7 typed chess-knowledge context
        |
        v
M36 deterministic current learner-state read model
        |
        + exact current M7 revision / M7C assessment
        + optional exact K7 projection
        v
M39 deterministic hypothesis evidence synthesis
        |
        + versioned transparent policy
        v
M40 ranked next-action proposal
```

This is the first repository-qualified chain that can move from “what is currently
known about this participant?” to “what kind of learning action should be proposed
next?” without granting the planner hidden mutation or execution authority.

## Package M36 — Deterministic Learner-State Read Model

**PR:** #82  
**Final head:** `8632a743fda30b4262e9007e9e48c79ca8d9283f`  
**Merge commit:** `d4631a8094d11454346e6703ec9dab0f06fedbb8`  
**CI run:** `34599051912`

M36 added `m36.learner-state-read-model.v1`, a participant-scoped,
content-addressed read model over already-qualified evidence.

It can combine:

- one exact M11 learner-state snapshot;
- exact current M7 revisions and M7C status/assessment references;
- current M10 practice, near-transfer, far-transfer, and real-game evidence states;
- exact M9 selection decision/intervention references;
- optional K7 concept context and semantic-coverage counts.

M36 rejects stale/non-current revisions, participant mismatch, non-current M9/K7
inputs, and tampered rebuilds.

**Authority ceiling:** M36 reads current learner state. It does not create or mutate
learner state, reclassify M7C, select M9 interventions, establish causality, or infer
mastery.

## Package M39 — Hypothesis Evidence Synthesizer

**PR:** #83  
**Final head:** `6d5a8954170129c920fbc9b09be27ab0f6315a72`  
**Merge commit:** `43ecdaa00a0d2abdf72d1f0f88f4254cd86f05dd`  
**CI run:** `34599807350`

M39 added `m39.hypothesis-evidence-synthesis.v1`, a deterministic explanation of one
exact current learner hypothesis.

It preserves:

- exact M36 read-model identity;
- exact current M7 revision and M7C assessment/policy identity;
- support, independent-support, contradiction, successful-counterexample,
  context-exception, unclear, mixed, eligible, and excluded counts;
- every M7C recurrence-unit relation verbatim;
- exact source games/positions, evidence-link refs, and review identities;
- optional K7 concepts on covered recurrence units;
- explicit evidence gaps and bounded “what could change the current assessment?”
  conditions.

The first candidate passed functional tests and Stockfish but was not merged because
Ruff found formatting-only defects. The amended exact head was fully re-qualified
before merge.

**Authority ceiling:** M39 explains existing evidence. M7C remains recurrence
classification authority; M39 does not predict a future M7C result or mutate M7/M11.

## Package M40 — Teaching-Priority / Next-Session Planner

**PR:** #84  
**Final head:** `78f3658a9e8ef7643c3a6e1f06f62bf2e674574b`  
**Merge commit:** `a10cdd36925af9a09a4e10c56fa7913bddba0f44`  
**CI run:** `34600739442`

M40 added a transparent, content-addressed next-session proposal contract:

```text
COLLECT_NEW_EVIDENCE
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
TEACH_CONCEPT
ASSIGN_PRACTICE
RUN_NEAR_TRANSFER_TEST
RUN_FAR_TRANSFER_TEST
WAIT_FOR_REAL_GAME_EVIDENCE
```

The default versioned policy explicitly prefers contradiction/control work when
current evidence is one-sided or contradicted, refuses to override mixed M9 selection
state, and advances selected interventions through practice -> near transfer -> far
transfer -> real-game observation only when the upstream M10/M11 evidence supports
that progression.

Across active hypotheses, candidate actions are ranked by explicit policy priority
and stable tie-breaking. Every candidate retains reasons, blocking uncertainty,
exact M39 source identity where present, K7 concepts supplied by M39, current M9
selection refs from M36, and M10 outcome states.

The first candidate passed all functional tests and Stockfish but Ruff rejected style
only. The formatting-only amended head was fully re-qualified before merge.

**Authority ceiling:** `decision_authority = proposal_only`. M40 does not start a
tutor session, select/replace an M9 intervention, create M10 evidence, mutate M7/M11,
invoke a model/provider, establish mastery, or claim optimal pedagogy.

## Qualification evidence

Every final feature head was merged only after the repository's full pull-request
gate passed:

```text
full pytest
Ruff
python -m compileall -q src tests
independent Stockfish integration job
```

Known final-suite counts:

```text
M39 final head: 871 passed, 8 intentional regular-job Stockfish skips
M40 final head: 889 passed, 8 intentional regular-job Stockfish skips
```

The independent Stockfish job passed separately; regular-job skips are never counted
as an independent-engine pass.

## Current authority boundaries

Preserve these distinctions:

```text
concept definition != concept assertion != learner inference
K7 ontology projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M40 action proposal != M9 intervention selection
M40 transfer-test proposal != M10 transfer evidence
WAIT_FOR_REAL_GAME_EVIDENCE != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
M34 resume eligibility != retry authorization or execution
```

## Current operational boundary

M36/M39/M40 are Python API / deterministic-hermetic surfaces. They add **no new
production CLI command** and do not silently wire themselves into reviewed coaching,
provider execution, or tutor-state mutation.

The existing local operator commands remain the established M12–M30 command set.
Applications may explicitly consume the new APIs when a concrete workflow is built.

## Recommended next priorities

These are recommendations, not an automatically approved queue.

1. **M43 contradiction hunter / evidence acquisition (REPOSITORY_ONLY /
   HERMETIC_VALIDATION).** Give M40 `CHALLENGE_HYPOTHESIS` and `PRESENT_CONTROL`
   proposals a concrete bounded consumer that searches participant-local evidence for
   high-value disconfirming/control cases. It must reuse M7C rather than become a new
   recurrence classifier.
2. **M41 intervention matching (REPOSITORY_ONLY / HERMETIC_VALIDATION).** Give
   `TEACH_CONCEPT` / supported teaching needs an explicit bridge to candidate M9
   interventions using ontology pedagogy metadata, while leaving M9 selection and
   efficacy authority intact.
3. **M42 transfer/retest scheduler (REPOSITORY_ONLY / HERMETIC_VALIDATION).** Turn
   `RUN_NEAR_TRANSFER_TEST` and `RUN_FAR_TRANSFER_TEST` proposals into bounded test
   plans without confusing scheduling with M10 outcome evidence.
4. **M44 learner progress surface (REPOSITORY_ONLY first).** Expose M36/M39/M40 in a
   coherent local participant-facing read experience: current priority, why the
   mentor believes it, contradiction evidence, what would change its mind, and next
   proposed action.
5. **M35 operator exposure / M37 consumer regression only when pulled by a real
   consumer blocker.** Do not return to infrastructure-first development by default.

## External/human authority still pending

The repository still does not establish production frontend quality, authentication,
privacy/security approval, production provider/vendor policy, production retry/
idempotency, semantic quality of arbitrary model prose, intervention causality,
mastery, or empirical tutoring efficacy.

## Restart instructions

1. Confirm live `main` before relying on hashes in this handoff.
2. Read this file, `CONTEXT.md`, `docs/product/repository-build-status.md`,
   `docs/architecture/architecture.md`, and the latest runbooks.
3. Run the focused M36/M39/M40 suites, then the full repository gate and independent
   Stockfish witness.
4. Treat M36/M39/M40 as qualified post-M34 packages; do not infer M35/M37/M38 exist.
5. Keep M7C as recurrence authority, M9 as intervention-selection authority, M10 as
   outcome/transfer evidence authority, and M11 as longitudinal-state authority.
6. Treat an M40 plan as a proposal requiring a separately qualified consumer or
   explicit application action.
7. Begin the next milestone with a live-main audit and a bounded package queue.

## Key references

- `docs/architecture/m36-learner-state-read-model.md`
- `docs/architecture/m39-hypothesis-evidence-synthesis.md`
- `docs/architecture/m40-next-session-planner.md`
- `docs/runbooks/m36-m40-learner-intelligence.md`
- `docs/runbooks/chess-knowledge-ontology-program.md`
- `docs/product/repository-build-status.md`
- `docs/product/chess-mentor-engine-repository-build-plan.md`
- PR #82 — M36
- PR #83 — M39
- PR #84 — M40
