# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)  
> **Latest handoff:** [`STATUS.md`](STATUS.md)  
> **Architecture:** [`docs/architecture/architecture.md`](docs/architecture/architecture.md)  
> **Latest runbook:**
> [`docs/runbooks/m36-m40-learner-intelligence.md`](docs/runbooks/m36-m40-learner-intelligence.md)

## Product and authority

Chess Mentor Engine is intended to convert objective chess evidence into
participant-specific teaching decisions without collapsing different kinds of truth
into one layer.

Keep these questions separate:

```text
What is objectively happening on the board?
What did the participant report noticing, considering, and expecting?
What position-local discrepancy is supported?
What participant-specific recurrence/hypothesis does M7C currently support or reject?
What intervention has M9 actually selected?
What bounded practice/transfer evidence does M10 record?
What does M11 currently project longitudinally?
What chess concepts are present under K0-K7 authority?
What can M36/M39 summarize without changing those sources?
What action may M40 propose without executing it?
```

## Current implementation boundary

The contiguous milestone sequence remains qualified through **M34**. Additional
qualified work includes:

- Chess Knowledge Ontology **K0–K7**;
- **M36** deterministic learner-state read model;
- **M39** hypothesis evidence synthesizer;
- **M40** teaching-priority / next-session planner.

M35, M37, and M38 remain candidate labels and are not implicitly implemented.

## Current authority graph

```text
OBJECTIVE CHESS
M1-M4 / M14-M18
canonical position, deterministic features, engine evidence, selection
        |
        v
PARTICIPANT EVIDENCE
M5 / M8 / M21 / M23
captured reasoning and exposure/consent boundaries
        |
        v
LEARNER INFERENCE
M6 position-local discrepancy
        |
        v
M7 / M7C participant-specific hypothesis, recurrence, contradiction
        |
        +------------------------------+
        |                              |
        v                              v
TRAINING / OUTCOMES                CHESS SEMANTICS
M9 intervention selection          K0-K7 ontology/assertions/detectors
M10 bounded outcome evidence       + optional M7C-preserving projection
M11 longitudinal learner state     |
        |                           |
        +-------------+-------------+
                      |
                      v
                M36 READ MODEL
                      |
                      v
                M39 SYNTHESIS
                      |
                      v
                M40 PROPOSAL
```

Separately, the existing deterministic feedback/model/review path remains:

```text
M15 presentation + M6/M7
-> M16 deterministic mentor grounding
-> optional M19 model request/prose
-> optional M20 evaluator judgment
-> M24 execution seam
-> M25-M30 review/persistence/navigation
-> M32 consumer fidelity
-> M33 deterministic trace
-> optional M31/M34 safety/recovery surfaces
```

The learner-intelligence path does not silently rewrite that model/review chain.

## Chess Knowledge Ontology mental model

K0–K7 exists to provide stable chess semantics, not learner psychology.

```text
concept definition
!=
position/move assertion
!=
participant perception
!=
learner hypothesis
```

A tactic such as `tactic.fork` may be mechanically present while the participant
understood it perfectly. Conversely, a learner discrepancy may concern search
process rather than the surface motif. Do not infer one from the other.

K7 attaches typed chess context to already-classified M7C recurrence units and
preserves M7C relations verbatim. It does not become recurrence authority.

## M36 mental model

M36 is the deterministic answer to:

> What does current qualified repository evidence say about this participant now?

It may combine exact current M7/M7C, M9, M10, M11, and optional K7 information.

It must remain a **read model**:

```text
M36 output != new M7 evidence
M36 output != M11 mutation
M36 output != M9 selection
M36 output != mastery
```

Construction intentionally rejects stale or non-current revisions and mismatched
participant/source identities.

## M39 mental model

M39 is the deterministic answer to:

> Why is this current learner hypothesis at its current M7C status, what challenges
> it, and what evidence remains missing?

It binds an exact current M36 entry to an exact current M7 revision and M7C
assessment, plus the exact K7 projection when M36 references one.

M39 preserves:

- support and independent-support counts;
- contradiction and successful-counterexample evidence;
- context exceptions, unclear, and mixed units;
- M7C status reasons and review records;
- exact source games/positions/evidence links;
- optional typed chess context;
- explicit evidence gaps and bounded future-change conditions.

It does not recalculate M7C.

```text
M39 synthesis != recurrence classification
```

## M40 mental model

M40 asks:

> Given current qualified evidence, which *kind* of learner-facing action should be
> proposed next under this explicit policy?

Its bounded action vocabulary is:

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

The default policy is intentionally contradiction-first:

- contradicted hypothesis -> present control/disconfirming evidence;
- unclear hypothesis -> challenge;
- insufficient/isolated/candidate recurrence -> collect evidence;
- supported but one-sided -> challenge;
- supported but unresolved alternatives remain -> challenge;
- supported and sufficiently challenged, no M9 selection -> teach concept;
- mixed M9 state -> collect/resolve upstream, do not override M9;
- selected M9 intervention -> practice, then near transfer, then far transfer, then
  real-game observation according to current M10/M11 evidence.

Across active hypotheses, explicit action priorities rank the candidates. That
ranking is a transparent heuristic policy, not a learned score and not evidence of
optimal pedagogy.

Most importantly:

```text
M40 decision_authority = proposal_only
```

M40 never performs the proposed action.

## Authority owners contributors must preserve

### Objective chess

`chess/`, M3/M4, and M15 own canonical board state, legal actions, deterministic
features, engine evidence, score/bound/mate semantics, and objective selection
contracts. They do not own learner psychology.

### Participant evidence

M5/M8 capture and freeze participant-reported reasoning under explicit exposure
boundaries. Participant self-report is evidence, not chess truth.

### Learning inference

M6 remains position-local. M7/M7C own participant-specific hypothesis lifecycle,
recurrence status, support/challenge/contradiction evidence, and review policy.

### Training and outcomes

M9 owns explicit intervention selection. M10 owns bounded outcome/transfer evidence.
M11 derives append-only longitudinal learner state from exact qualified inputs.

### Deterministic feedback/model language

M16 is the deterministic mentor-grounding ceiling. M19 model language may render that
context but does not inherit deterministic authority. M20 evaluator judgments remain
bounded judgments.

### Chess semantics

K0–K7 own ontology identities, semantics, provenance-bound assertions, conservative
detector outputs, and qualified sidecar/projection contracts. They do not own M7C,
M9, or learner-state mutation.

### Learner-intelligence projections

M36 reads current state. M39 explains current evidence. M40 proposes a next action.
None of them silently inherit mutation or execution authority.

## Contracts to preserve

```text
objective chess truth != participant evidence != learner inference
one M6 discrepancy != recurrence != causal trait
concept occurrence != participant perception or learner weakness
K7 semantic coverage missing != concept absent
K7 projection != M7C recurrence authority
M36 read model != learner-state mutation
M39 evidence synthesis != M7C assessment
M40 action proposal != action execution
M40 TEACH_CONCEPT != M9 intervention selection
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
M40 WAIT_FOR_REAL_GAME_EVIDENCE != mastery
M9 selected intervention != effective intervention
practice completion != transfer
transparent policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective truth
```

## Qualification discipline

For any future package:

1. reconcile live `main`;
2. identify the existing authority owner before adding a subsystem;
3. classify the work as `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or
   `EXTERNAL_AUTHORITY`;
4. define explicit inputs/outputs, claim ceiling, and forbidden authority changes;
5. implement the smallest bounded contract;
6. include positive and rejection/near-miss cases;
7. merge only the exact final head that passes full pytest, Ruff, compileall, and the
   independent Stockfish job;
8. reconcile current documentation after the feature packages merge.

## Likely next architecture work

The new M40 routing makes the next needs clearer:

```text
M40 CHALLENGE_HYPOTHESIS / PRESENT_CONTROL
    -> candidate M43 contradiction/control evidence acquisition

M40 TEACH_CONCEPT
    -> candidate M41 intervention matching / M9 candidate bridge

M40 RUN_NEAR_TRANSFER_TEST / RUN_FAR_TRANSFER_TEST
    -> candidate M42 bounded transfer/retest scheduling

M36 + M39 + M40
    -> candidate M44 learner progress surface
```

Those remain candidates. A fresh live-main audit must decide which action is the
actual blocker before implementation.
