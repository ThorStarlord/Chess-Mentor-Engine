# M40 — Teaching-Priority / Next-Session Planner

M40 answers a bounded planning question:

> Given the participant's current qualified learner state and evidence synthesis,
> what *kind of learning action* should be proposed next?

The output is a transparent, content-addressed **proposal** under a frozen heuristic
policy. It is not an execution command and it is not evidence that the proposed
choice is empirically optimal.

## Inputs

M40 consumes:

- one exact M36 `LearnerStateReadModel`;
- one exact M39 `HypothesisEvidenceSynthesis` for every active M36 hypothesis that
  currently has an M7C status;
- one versioned `NextSessionPolicy`;
- an explicit `created_at` timestamp.

A hypothesis without a current M7C assessment may still receive a bounded
`COLLECT_NEW_EVIDENCE` proposal without an M39 synthesis. Retired/superseded
hypotheses do not receive active action proposals.

## Action vocabulary

`m40.next-session-plan.v1` selects from this bounded action vocabulary:

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

These are action **classes**, not direct tutor transitions, intervention selections,
provider calls, or learner-state mutations.

## Default policy

The default `m40.next-session-policy.v1` uses explicit priorities:

```text
PRESENT_CONTROL              100
CHALLENGE_HYPOTHESIS          95
RUN_FAR_TRANSFER_TEST         90
RUN_NEAR_TRANSFER_TEST        85
ASSIGN_PRACTICE               80
TEACH_CONCEPT                  75
COLLECT_NEW_EVIDENCE           70
WAIT_FOR_REAL_GAME_EVIDENCE    60
```

The priorities are visible policy, not hidden model weights and not empirically
validated universal pedagogy. A different policy may intentionally rank candidate
actions differently if it is separately versioned and content-addressed.

The default within-hypothesis decision rules are:

```text
no M7C status
    -> COLLECT_NEW_EVIDENCE

insufficient / isolated / candidate_recurrence
    -> COLLECT_NEW_EVIDENCE

unclear
    -> CHALLENGE_HYPOTHESIS

contradicted
    -> PRESENT_CONTROL

supported_recurrence
    + no contradiction/counterexample/context-exception coverage
        -> CHALLENGE_HYPOTHESIS
    + unresolved alternative explanations
        -> CHALLENGE_HYPOTHESIS
    + no M9 intervention selection
        -> TEACH_CONCEPT
    + mixed M9 selection state
        -> COLLECT_NEW_EVIDENCE
    + selected M9 intervention, practice not supported
        -> ASSIGN_PRACTICE
    + practice supported, near transfer not supported
        -> RUN_NEAR_TRANSFER_TEST
    + near transfer supported, far transfer not supported
        -> RUN_FAR_TRANSFER_TEST
    + far transfer supported
        -> WAIT_FOR_REAL_GAME_EVIDENCE
```

Even if bounded real-game transfer is currently supported, the default action remains
observation-oriented and M40 does not promote that state into mastery.

## Cross-hypothesis priority

M40 builds one candidate per active current hypothesis and orders candidates by:

1. explicit policy action priority, descending;
2. hypothesis ID, ascending;
3. action ID, ascending.

The first candidate is the selected *proposal*. Every candidate retains its reasons,
blocking uncertainty, exact M39 synthesis reference when present, ontology concept
IDs supplied by M39, selected M9 intervention IDs supplied by M36, and current M10
outcome dimension states.

## Authority boundary

```text
M36 current learner-state read model
+ M39 current hypothesis evidence synthesis
+ versioned transparent M40 policy
        |
        v
M40 ranked next-action proposal
```

M40 does **not**:

- create, revise, retire, reactivate, or reclassify M7/M7C evidence;
- select or replace an M9 intervention;
- create M10 outcome/transfer evidence;
- mutate M11 learner state;
- start or advance an M8 tutor session;
- invoke M16/M19/M20/M24 or any model/provider/evaluator;
- infer that ontology concept presence proves participant understanding or weakness;
- establish causal intervention effects, transfer, or mastery;
- establish that its policy is optimal pedagogy.

Core invariants:

```text
M40 proposal != execution authority
M40 action proposal != M9 intervention selection
M40 transfer-test proposal != M10 transfer evidence
WAIT_FOR_REAL_GAME_EVIDENCE != mastery
transparent heuristic policy != empirically optimal pedagogy
```

## Rejection behavior

Construction fails closed for:

- malformed or tampered policy fingerprints;
- duplicate syntheses for one revision;
- missing M39 synthesis for an assessed active hypothesis;
- M39 synthesis participant mismatch;
- M39/M36 current-revision mismatch;
- M39/M36 read-model identity drift;
- M39/M36 M7C status or assessment identity drift;
- synthesis attached to an active hypothesis with no M7C status;
- extra synthesis for retired, superseded, or otherwise unreferenced revisions;
- duplicate M10 outcome dimensions in the read model;
- a read model with no active hypothesis;
- tampered deterministic rebuild output.

## Qualification

```bash
python -m pytest tests/test_m40_next_session_planner.py -rs
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Pull-request CI plus the independent Stockfish job remains the merge authority.
