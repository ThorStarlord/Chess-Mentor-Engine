# FPV-PILOT-002 pilot protocol

Status: Designed and frozen before execution. Not executed.

Protocol version: 1.0

## Research question

Does enriching chess evidence with explicit board context and direct player reasoning materially improve the usefulness and defensibility of Chess Mentor Engine's tutoring diagnosis?

## Purpose

Test whether Pilot 001's missing-context problem is solved by adding deterministic position representation and pre-engine player decision evidence. The pilot tests evidence requirements, not a production tutor.

## Parent provenance

Parent pilot: FPV-PILOT-001

Parent result: Mixed, based on P01 qualitative feedback that the analysis was not helpful because the context was not included.

Frozen main protocol SHA-256: 7ED3D48CFE07024FF01D543E35AD7903AEF485F3EC8904469CB37C162FB62253

This pilot does not modify or supersede the frozen main protocol or Pilot 001's frozen analyses.

## Participant and position sample

Use P01 only for this exploratory follow-up. Select 5-8 positions from the already supplied P01 game set using [position-selection.md](position-selection.md). The sample is not a new full-game analysis and cannot support population claims.

## Evidence conditions

### C1, annotation only

Played move, evaluation before and after, best move, short annotation, and principal variation where available. This approximates Pilot 001's weak representation.

### C2, annotation plus Position Context Packet

C1 plus FEN, side to move, move number, top candidates, candidate evaluations, principal variations, and deterministic board representation.

### C3, Position Context Packet plus Player Decision Evidence

C2 plus P01's pre-engine account of considered moves, intended plan, expected reply, confidence, and decision context.

The conditions compare evidence available for reasoning. They do not require three complete tutoring products.

## Hypotheses

- **H1:** Explicit board context improves understanding of why a move was wrong compared with annotations and principal variations alone.
- **H2:** Board context improves chess explanation but remains insufficient to identify why P01 chose the move.
- **H3:** Pre-engine player decision evidence improves the ability to distinguish competing learner-level explanations.
- **H4:** Richer context does not improve tutoring diagnosis enough to justify its added collection and representation effort.

H4 is a valid result.

## Evidence boundaries

Deterministic tooling may provide board state, rendering, material, legal state, engine evaluations, candidate moves, and principal variations. Model-assisted reasoning may explain chess concepts, compare candidates, ask pedagogical questions, and propose hypotheses. P01 supplies considered moves, intended plan, expected reply, subjective reasoning, and confidence.

Player reasoning is direct learner evidence, not objective chess truth. Retrospective explanations remain fallible and must be labeled as pre-engine or post-engine.

## Analysis procedure

1. Select and freeze the 5-8 position sample before participant questioning.
2. Prepare C1, C2, and C3 materials from the same positions.
3. Ask C3 player-decision questions before revealing engine answers where practical.
4. Record pre-engine and post-engine evidence separately.
5. Produce task-level outputs for board understanding, move explanation, candidate comparison, pattern observation, learner hypothesis, and intervention.
6. Record uncertainty, competing explanations, and unsupported claims.
7. Evaluate C1, C2, and C3 using the separate dimensions in [evaluation-plan.md](evaluation-plan.md).

## Claim ceiling

This pilot cannot establish rating improvement, transfer, mastery, automated diagnosis reliability, a production learner model, generalization beyond P01, or the truth of any inferred cognitive cause.

