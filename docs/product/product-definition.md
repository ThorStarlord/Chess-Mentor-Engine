# Product definition

> **Implementation status authority:** [`repository-build-status.md`](repository-build-status.md)  
> **Future planning:** [`chess-mentor-engine-repository-build-plan.md`](chess-mentor-engine-repository-build-plan.md)  
> **Latest completed milestone handoff:** [`../../STATUS.md`](../../STATUS.md)

This document defines the product hypothesis and open product questions. It is not a
moving implementation-status document and does not promote candidate product ideas
into qualified repository capabilities.

## Problem

Chess software is very good at determining whether a move is objectively good or bad. It is much weaker at building a persistent explanation of:

- how a specific player makes decisions;
- which mistakes are isolated versus recurring;
- what misconception or process failure may underlie those mistakes;
- what that player should study next;
- whether previous instruction transferred into future games.

## Product hypothesis

Chess Mentor Engine should transform longitudinal chess evidence into a persistent learner model and use that model to choose personalized teaching interventions.

## Tentative target user

The initial segment remains a discovery question. The current product-discovery recommendation is to test regular online players approximately rated 1400-1800 first, because they are more likely to have recurring decision patterns, engine exposure, and enough chess vocabulary for a player-specific diagnosis to be meaningful. This is a working hypothesis, not a permanent rating boundary. See [product discovery](product-discovery.md).

Candidate initial segment:

> Online players approximately 1400-1800 rating who play regularly and already use engine analysis.

Players approximately 1000-1400 remain a plausible follow-on segment. The discovery pass records why the broader 1000-1800 range is not the first design customer.

## Proposed first-value moment

A possible first-value experience:

1. The player imports a set of games.
2. The system identifies a recurring decision pattern.
3. The system explains why it matters.
4. The system distinguishes it from generic engine mistakes.
5. The system proposes a targeted training intervention.

## Differentiation hypothesis

The product should move beyond:

```text
"You blundered here."
```

toward:

```text
"You repeatedly recognize attacking ideas correctly but commit
before checking your opponent's forcing defensive resources.

This appears in 7 of your recent games.

Generic tactical puzzles are therefore probably not your highest
priority. We should train defensive-resource enumeration."
```

## Explicit non-goals for the initial product

- Replacing Stockfish or another chess engine.
- Becoming a general-purpose chess database.
- Reproducing every feature of Chess.com or Lichess.
- Generating large amounts of generic chess content.
- Pretending model-generated chess judgments are objective engine truth.
- Implementing an entire training platform before validating the tutoring thesis.

## Open product questions

- Who is the initial learner segment?
- Is the primary input imported games, live play, exercises, or conversation?
- Should optimization target rating improvement, understanding, enjoyment, or a configurable combination?
- What constitutes sufficient evidence for a recurring weakness?
- How should suspected misconceptions differ from demonstrated weaknesses?
- What does mastery mean?
- How should the system measure transfer from exercises into real games?
- When should the tutor teach an objectively best move versus exploit a position as a pedagogical opportunity?
