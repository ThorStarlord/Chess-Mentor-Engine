# Chess Mentor Engine — Repository Build Plan

> **Current implementation authority:**
> [`repository-build-status.md`](repository-build-status.md)  
> **Latest handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Current architecture:** [`../architecture/architecture.md`](../architecture/architecture.md)

**Status:** planning history plus future candidate roadmap.  
**Authority:** this document does not create an approved queue or production claim.

## 1. Product direction

Chess Mentor Engine should become a persistent chess tutor that learns from a
participant's own games and reasoning evidence rather than a generic engine-analysis
wrapper.

The durable learning chain is:

```text
objective chess evidence
-> participant decision evidence
-> position-local reasoning discrepancy
-> contradiction-tested learner hypothesis
-> explicit teaching decision
-> bounded intervention/practice
-> near/far/real-game transfer evidence
-> revised longitudinal learner state
```

The repository now has enough infrastructure to make the middle of that chain
inspectable and policy-driven.

## 2. Current implementation state

The contiguous numbered milestone series is qualified through **M34**. Additional
qualified work includes:

```text
K0-K7  Chess Knowledge Ontology program
M36    Deterministic Learner-State Read Model
M39    Hypothesis Evidence Synthesizer
M40    Teaching-Priority / Next-Session Planner
```

M35, M37, and M38 remain unimplemented candidate labels; later-numbered qualified
packages do not imply those candidates were completed.

### What M36/M39/M40 changed

Before this milestone the strongest learner-facing chain was representational:

```text
M7 hypothesis
+ M9 intervention
+ M10 outcome evidence
+ M11 state
+ K7 semantic context
```

The repository can now deterministically derive:

```text
M36
"What does the current repository know about this participant?"
        |
        v
M39
"Why is this hypothesis at its current M7C status, what challenges it,
 and what evidence is missing?"
        |
        v
M40
"What kind of learning action should be proposed next under this explicit policy?"
```

This is a meaningful product transition from evidence storage toward learner
intelligence.

## 3. Durable authority principles

### Chess truth is not learner psychology

Engine evidence can establish bounded chess facts and evaluations. It cannot by
itself establish what the participant thought or why they made a decision.

### Participant self-report is evidence, not objective truth

Captured reasoning is participant evidence. It may be incomplete or reconstructed
and should remain distinct from engine analysis.

### Local discrepancy is not recurrence

```text
one M6 discrepancy
!=
M7C recurrence
!=
causal learner trait
```

M7C remains the participant-specific recurrence/contradiction authority.

### Ontology semantics do not create learner authority

```text
concept definition
!=
concept assertion
!=
participant perception
!=
learner inference
```

K7 adds typed context to already-classified M7C units. It does not decide the
relation between a chess concept and a learner hypothesis.

### Read/synthesis/planning layers remain derived

```text
M36 read model != learner-state mutation
M39 synthesis != M7C assessment
M40 proposal != action execution
```

### Intervention and outcome authorities remain separate

```text
M40 TEACH_CONCEPT != M9 intervention selection
M40 ASSIGN_PRACTICE != M10 practice evidence
M40 RUN_*_TRANSFER_TEST != M10 transfer evidence
M40 WAIT_FOR_REAL_GAME_EVIDENCE != mastery
```

### Transparent policy is not validated pedagogy

M40's priorities are explicit product heuristics. Mechanical qualification shows the
policy is deterministic and authority-preserving; it does not establish that the
policy is empirically optimal.

### Infrastructure should be pulled by product need

The repository already has substantial provenance, persistence, review, recovery,
semantic, and learner-intelligence infrastructure. New infrastructure should normally
exist because a concrete learner-facing or operator capability needs it now.

## 4. Implemented foundation

### Evidence and tutoring substrate

M1–M34 already establish canonical chess evidence, engine evidence, diagnostic
selection, participant capture, learner-hypothesis/recurrence contracts, intervention
selection, bounded outcome evidence, longitudinal state, model/evaluator boundaries,
persistent reviewed coaching, consumer fidelity, traceability, and hermetic recovery.

### Chess semantic substrate

K0–K7 adds:

- stable typed chess concept identities;
- tactical motifs, position features, strategic principles, evaluation factors,
  plans, and pedagogy metadata;
- Lichess theme crosswalks without treating Lichess as universal ontology authority;
- provenance-bound concept assertions;
- a conservative mechanically qualified detector subset;
- optional authority-preserving model context beside M19;
- K7 typed semantic projection over already-classified M7C recurrence units.

### Learner-intelligence substrate

M36/M39/M40 now add:

- current participant-state composition;
- exact evidence explanation and contradiction visibility;
- explicit evidence gaps and bounded change conditions;
- transparent next-action proposal and cross-hypothesis priority.

## 5. M40 now defines useful downstream seams

The M40 action vocabulary gives future packages concrete consumer boundaries:

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

Future features should consume these action classes rather than independently invent
parallel learner-intelligence policies.

---

## 6. Highest-priority next candidates

These are **candidates, not an approved queue**.

### Candidate M43 — contradiction/control evidence acquisition

**Zone:** REPOSITORY_ONLY / HERMETIC_VALIDATION

**Pulled by:** M40 `CHALLENGE_HYPOTHESIS` and `PRESENT_CONTROL`.

**Purpose:** Search participant-local qualified evidence for positions that can
challenge, narrow, or contextualize a current M7C hypothesis.

Potential scope:

- consume an exact M40 proposal and M39 synthesis;
- search only participant-scoped qualified evidence;
- identify existing cases where the suspected weakness should have been relevant but
  the participant succeeded or behaved differently;
- distinguish direct contradiction, successful counterexample, context exception,
  and merely similar-looking positions;
- rank candidates by explicit information value, not by engine loss alone;
- return evidence-acquisition/control candidates to M7C/human review without changing
  M7C itself;
- preserve source game/position and semantic context.

Non-goals:

- automatic M7/M7C mutation;
- treating absence of failure as mastery;
- confirmation-biased search for support only;
- causal psychological claims.

**Candidate exit criterion:** an exact M40 challenge/control proposal can be converted
into a bounded participant-local set of high-value disconfirming/control candidates,
with near-miss cases rejected and M7C authority unchanged.

### Candidate M41 — intervention matching

**Zone:** REPOSITORY_ONLY / HERMETIC_VALIDATION

**Pulled by:** M40 `TEACH_CONCEPT` or another explicit supported teaching need.

**Purpose:** Map an exact supported learning need to candidate M9 interventions using
explicit applicability/contraindication metadata and K0–K7 pedagogy semantics.

Potential scope:

- consume M36/M39/M40 exact identities;
- map concept/process needs to eligible intervention definitions;
- expose prerequisites and contraindications;
- rank/filter candidates under an explicit versioned matching policy;
- explain why each candidate applies or fails to apply;
- produce a candidate set that M9 may explicitly select from.

Non-goals:

- bypassing M9 selection authority;
- claiming matched intervention effectiveness;
- free-form content generation detached from learner evidence;
- ranking solely by centipawn loss.

**Candidate exit criterion:** a qualified teaching need yields a provenance-complete
candidate intervention set while ineligible or authority-mismatched interventions
fail closed.

### Candidate M42 — transfer / retest scheduler

**Zone:** REPOSITORY_ONLY / HERMETIC_VALIDATION

**Pulled by:** M40 `RUN_NEAR_TRANSFER_TEST` or `RUN_FAR_TRANSFER_TEST`.

**Purpose:** Convert a transfer-test proposal into a bounded test plan whose later
result may become M10 evidence.

Potential scope:

- consume exact hypothesis/intervention/M40 identities;
- distinguish near versus far transfer;
- preserve freshness/exposure constraints;
- select or request positions that test the underlying skill without simply repeating
  a memorized training item;
- record what outcome would be measured;
- keep schedule/test-plan creation separate from actual outcome evidence.

Non-goals:

- automatic mastery;
- fabricating real-game evidence;
- treating scheduled/completed test as successful transfer;
- claiming universal optimal retest timing.

**Candidate exit criterion:** an exact M40 transfer proposal yields a deterministic,
provenance-bound test plan without creating M10 evidence until actual bounded results
are supplied.

### Candidate M44 — learner progress surface

**Zone:** REPOSITORY_ONLY initially

**Pulled by:** the need to make M36/M39/M40 legible to a participant/operator.

Candidate experience:

```text
CURRENT LEARNING PRIORITY
why the mentor believes it
supporting evidence
contradictory/counterexample evidence
relevant chess concepts
what has been trained
practice / near / far / real-game state
what remains uncertain
what would change the mentor's mind
next proposed action
```

Potential scope:

- deterministic local/reference rendering over M36/M39/M40;
- source navigation into supporting and contradicting positions;
- explicit evidence/inference/policy authority labels;
- no hidden smoothing of uncertainty;
- local/reference quality before any external browser/a11y/usability claim.

**Candidate exit criterion:** one participant can inspect a coherent learner-progress
view and trace every substantive claim/proposal back to qualified evidence.

---

## 7. Lower-priority candidates that remain available

### M35 — operator exposure

M32/M33 and newer M36/M39/M40 read/projection artifacts could receive supported CLI
or operator exposure when a real consumer needs it. Do not prioritize this merely to
increase command count.

### M37 — cross-surface consumer regression

A future frontend may need a repository-owned fixture contract spanning review
surfaces and learner-intelligence read models. Pull this forward only if consumer
compatibility becomes the active blocker.

### M38 — recurrence candidate mining

Do **not** implement M38 as a second recurrence engine. If future work uses this label,
it should mean M7C-aware context/grouping or candidate-discovery work that proposes
evidence for M7C/human review while preserving existing recurrence authority.

## 8. Later product candidates

After M41/M42/M43 provide concrete consumers for M40, consider:

### M45 — batch games -> mentor queue

Process a bounded batch of recent games into a participant-scoped review/mentor queue
using objective importance, hypothesis uncertainty, contradiction value, transfer
value, and novelty rather than simple centipawn-loss sorting.

### M46 — adaptive Socratic tutor

Use current learner state and an explicit bounded pedagogical-action vocabulary to
choose the next question/hint/reveal while preserving pre-reveal measurement
boundaries and keeping model language downstream of deterministic evidence.

### M47 — bounded multi-session study plan

Compose several M40-style actions into a revisable short-horizon plan with explicit
retest/transfer checkpoints and append-preserved revisions.

## 9. Signature product opportunity

The strongest differentiating surface remains explainable learner beliefs:

```text
WHY DO YOU BELIEVE THIS ABOUT ME?
M36 current state
-> M39 exact evidence synthesis
-> M7C support / contradiction / counterexamples
-> K7 chess concepts
-> participant reasoning
-> objective source positions
```

and:

```text
WHAT WOULD CHANGE YOUR MIND?
M39 evidence gaps/change conditions
-> M40 challenge/control proposal
-> future M43 evidence acquisition
```

This is more aligned with the repository's evidence discipline than a generic “AI
coach” that merely produces plausible explanations.

## 10. Productization to defer

Do not prioritize these ahead of a compelling closed local tutoring loop unless a
concrete requirement changes the order:

- cloud deployment for its own sake;
- multi-tenancy before a real multi-user requirement;
- payments/subscriptions;
- social/community features;
- mobile apps;
- broad opening databases;
- generic puzzle platform;
- rating prediction;
- gamification;
- complex provider abstraction unrelated to a current provider need.

Production frontend, provider, privacy/security, authentication, hosted persistence,
retry/idempotency, and empirical tutoring claims remain external/human authority
boundaries.

## 11. Phase-gate discipline

Before a future package:

1. reconcile live `main`;
2. state the concrete product/correctness problem;
3. identify the existing authority owner;
4. classify `REPOSITORY_ONLY`, `HERMETIC_VALIDATION`, or `EXTERNAL_AUTHORITY`;
5. define exact inputs, outputs, provenance, claim ceiling, and forbidden authority;
6. implement the smallest useful contract;
7. add positive and negative/near-miss qualification;
8. merge only the exact final head that passes full pytest, Ruff, compileall, and the
   independent Stockfish job;
9. update moving status/architecture/runbook truth after merge.

For infrastructure work also ask:

> Which learner-facing, tutoring, consumer, or external-adoption need requires this
> infrastructure now?

If there is no concrete answer, prefer not to build it.

## 12. Current recommendation

The next live-main audit should choose among **M43, M41, and M42 based on the first
M40 action class that needs a real consumer**.

A reasonable default sequence, absent another blocker, is:

```text
M43 contradiction/control evidence acquisition
        |
        v
M41 intervention matching
        |
        v
M42 transfer / retest scheduler
        |
        v
M44 learner progress surface
```

The rationale is that the current default M40 policy is intentionally
contradiction-first: before teaching a supported hypothesis, the repository should be
able to seek high-value disconfirming/control evidence when current evidence is
one-sided or uncertain.

This remains planning guidance, not an approved queue.
