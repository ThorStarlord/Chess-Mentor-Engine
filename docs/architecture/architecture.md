# Architecture: implemented boundaries through M34 + K0–K7 + M36/M39/M40

> **Current implementation authority:**
> [`../product/repository-build-status.md`](../product/repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Contributor context:** [`../../CONTEXT.md`](../../CONTEXT.md)

This is the current high-level authority map. Detailed contracts live in feature
architecture docs, ADRs, tests, and runbooks.

The contiguous numbered milestone series is qualified through **M34**. Additional
qualified capabilities are the **K0–K7 Chess Knowledge Ontology** program and the
non-contiguous learner-intelligence packages **M36, M39, and M40**. M35/M37/M38 are
not implicitly implemented.

## 1. System shape

```text
                               OBJECTIVE CHESS

PGN / source
   |
   v
M1-M2 canonical game / position / deterministic context
   |
   v
M3 provenance-bound UCI engine evidence
   |
   v
M4 played-decision comparison + diagnostic selection
   |
   v
M15 deterministic evaluation presentation
   |
   v
M18 auditable diagnostic candidate/control batch

                            PARTICIPANT EVIDENCE

explicit candidate selection + separate capture consent
   |
   v
M21 authorization / candidate-to-session launch
   |
   v
M5 frozen participant decision evidence
   |
   v
M8 controlled capture / freeze / reveal / compare state

                             LEARNER INFERENCE

M6 position-local reasoning discrepancy
   |
   v
M7 / M7C participant-specific hypothesis, recurrence, contradiction, review

                  +-------------------+--------------------+
                  |                                        |
                  v                                        v
          PEDAGOGY / OUTCOMES                      CHESS SEMANTICS
          M9 intervention selection                K0-K7 ontology
          M10 bounded outcome/transfer              assertions / detectors
          M11 longitudinal state                    optional semantic projections
                  |                                        |
                  +-------------------+--------------------+
                                      |
                                      v
                         M36 LEARNER-STATE READ MODEL
                                      |
                                      v
                       M39 HYPOTHESIS EVIDENCE SYNTHESIS
                                      |
                                      v
                  M40 TEACHING-PRIORITY / NEXT-ACTION PROPOSAL

                         DETERMINISTIC TUTOR GROUNDING

compared M8 session + exact M15/M6 + optional current M7
   |
   v
M16 deterministic grounded mentor feedback
   |
   +--> M19 model request -> optional M24 provider execution -> M19 model prose
   |
   +--> M20 evaluation request -> optional M24 evaluator execution -> M20 judgment

                            REVIEW / PERSISTENCE

M26 persistent reviewed coaching
-> M25 review read model
-> M27 mechanical execution ledger
-> M29 persisted bridge -> M28 reference surface
-> M30 participant-scoped package/navigation/export
-> M32 machine-consumer fidelity
-> M33 deterministic feedback trace

                            SAFETY / RECOVERY

optional M31 synthetic privacy/manual-retry preflight
optional M34 hermetic recovery reconciliation
```

Not every application invokes every optional branch. This is a capability/authority
graph, not one automatic end-to-end command.

## 2. Layer ownership

| Layer | Principal implementation | Owns | Explicitly does not own |
| --- | --- | --- | --- |
| Chess substrate | M1–M2, `chess/` | canonical positions, legality, deterministic context/features | player cognition, pedagogy |
| Engine evidence | M3, `analysis/` | UCI evidence, score/bound/mate/failure semantics, engine provenance | learner diagnosis |
| Selection | M4/M18 | deterministic diagnostic selection policy | participant choice, universal blunder taxonomy |
| Participant evidence | M5/M8 | captured/frozen participant reasoning and exposure state | objective chess truth, recurrence |
| Learner inference | M6/M7/M7C | local discrepancy; participant-specific hypothesis, recurrence, contradiction/review | causal cognitive mechanisms, permanent traits |
| Training | M9 | explicit intervention applicability/selection | intervention effectiveness |
| Outcomes | M10 | bounded practice/near/far/real-game evidence | causal effect, mastery |
| Longitudinal state | M11 | append-only projection of qualified learner evidence | hidden inference beyond sources |
| Chess semantics | K0–K7 | stable ontology, assertions, qualified detector subset, sidecar/projection context | participant perception, M7C recurrence authority |
| Learner read model | M36 | deterministic current-state composition of M7/M9/M10/M11 + optional K7 | learner-state mutation, new intervention selection |
| Evidence synthesis | M39 | deterministic explanation of exact current M7C evidence and gaps | recurrence reclassification, future-status prediction |
| Next-action policy | M40 | transparent ranked action proposal over current M36/M39 evidence | action execution, M9 selection, M10 evidence creation, optimality claim |
| Deterministic feedback | M16 | exact factual mentor grounding | arbitrary generative prose |
| Model language | M19 | request/model provenance | objective truth, learner-state authority |
| Model evaluation | M20 | bounded evaluator judgment | objective chess truth, complete safety proof |
| Execution seam | M24 | provider/evaluator execution provenance | vendor approval, retry policy |
| Review/persistence | M25–M30 | local review, persistence, verification, navigation | auth/privacy approval, production UI quality |
| Consumer fidelity | M32 | exact machine-readable delivery semantics | browser/device/a11y correctness |
| Traceability | M33 | deterministic M16 source/component trace | semantic/pedagogical truth |
| Recovery | M31/M34 | synthetic/manual preflight and hermetic reconciliation | production retry authorization/idempotency |

## 3. Core invariants

### 3.1 Chess truth is not learner inference

```text
engine evidence
!=
participant self-report
!=
learner hypothesis
```

An objectively bad move can justify chess comparison. It cannot prove why the player
moved or establish a causal learner trait.

### 3.2 Ontology semantics do not collapse authority

```text
concept definition
!=
concept assertion
!=
participant perception
!=
learner inference
```

K7 may attach `tactic.fork` to a recurrence unit while M7C independently classifies
that unit as supporting, contradicting, counterexample, context exception, unclear,
or mixed. K7 preserves that relation; it does not choose it.

### 3.3 M36 reads; it does not write

M36 is an exact current-state projection over already-qualified sources.

```text
M36 read model != M7/M11 mutation
M36 M9 summary != new M9 selection
M36 M10 status != mastery
```

Stale and non-current inputs fail closed.

### 3.4 M39 explains; M7C still decides recurrence

M39 may state:

- what M7C currently classified;
- why under the exact source assessment/policy;
- what supporting/contradictory/control evidence exists;
- which reviews were completed;
- what K7 context covers the units;
- what evidence is currently missing;
- what kinds of future evidence could cause a future M7C assessment to change.

It cannot calculate a replacement recurrence status or predict the future status.

```text
M39 synthesis != M7C authority
```

### 3.5 M40 proposes; it does not execute

M40 selects from a bounded action vocabulary under a versioned transparent heuristic
policy:

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

Its output carries:

```text
decision_authority = proposal_only
```

Therefore:

```text
M40 proposal != tutor-state transition
M40 TEACH_CONCEPT != M9 intervention selection
M40 ASSIGN_PRACTICE != recorded M10 practice
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
M40 WAIT_FOR_REAL_GAME_EVIDENCE != mastery
```

A separately qualified consumer must implement any action.

### 3.6 The M40 policy is inspectable, not magically optimal

The default policy deliberately prioritizes disconfirming/control work over teaching
when a hypothesis is contradicted, unclear, one-sided, or retains unresolved
alternatives. It advances selected interventions through practice -> near transfer ->
far transfer -> real-game observation according to current M10/M11 evidence.

Those choices are explicit product heuristics. The repository has not established
them as universally or empirically optimal pedagogy.

### 3.7 M9, M10, and M11 remain independent authorities

M40 refuses to resolve a mixed M9 selection state. It may propose practice or a
transfer test only after reading upstream state; it cannot manufacture the evidence
that would later prove completion or transfer.

### 3.8 Deterministic grounding remains separate from model language

M16 remains the factual deterministic mentor-feedback ceiling. M19 may render prose
from exact grounding. M20 may evaluate bounded aspects of output. Neither inherits
objective or learner authority simply through provenance.

## 4. Current product path

A bounded local product path now exists conceptually across the qualified layers:

```text
import/analyze games
-> select instructive positions
-> capture participant reasoning before reveal
-> compare with objective evidence
-> create/review M6/M7 learner evidence
-> project current M11 state
-> M36: inspect current learner state
-> M39: inspect why a current hypothesis is believed/challenged
-> M40: propose the next type of learning action
```

The last arrow remains a proposal boundary; no consumer yet automatically executes
M40 actions.

## 5. Current operator boundary

Installed commands remain the established M12–M30 local commands:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

K0–K7 and M36/M39/M40 currently expose Python API / reference-document surfaces.
They add no production CLI and no automatic network/provider behavior.

## 6. Persistence and provenance policy

Important derived outputs should remain bound to exact upstream identities and
fingerprints rather than inferred from prose.

The latest chain demonstrates this explicitly:

```text
M11 snapshot
-> exact M36 fingerprint
-> exact M39 fingerprint per current hypothesis
-> exact M40 policy fingerprint + M39 refs
-> exact M40 plan fingerprint
```

Changing a current revision, assessment, K7 projection, M36 read model, M39 synthesis,
or M40 policy must change the downstream content identity or fail validation.

## 7. Productization boundary

Not established by current repository qualification:

- hosted authentication/authorization or multi-user tenancy;
- production persistence/retention/privacy architecture;
- production LLM/evaluator vendor and credential transport;
- production retry/backoff/rate-limit/idempotency policy;
- browser/device/a11y/localization/usability correctness;
- causal cognitive diagnosis or permanent learner traits;
- causal intervention effects;
- mastery from current practice/transfer evidence;
- empirical optimality of M40 action priorities;
- empirical tutoring efficacy.

## 8. Likely next architecture consumers

M40 makes future package boundaries more concrete:

```text
CHALLENGE_HYPOTHESIS / PRESENT_CONTROL
    -> candidate M43 contradiction/control evidence acquisition

TEACH_CONCEPT
    -> candidate M41 intervention matching into M9 candidates

RUN_NEAR_TRANSFER_TEST / RUN_FAR_TRANSFER_TEST
    -> candidate M42 transfer/retest planning

M36 + M39 + M40
    -> candidate M44 learner-progress/reference surface
```

These remain candidate directions. Future work should start from live `main` and
select the bounded consumer required by the actual active blocker.
