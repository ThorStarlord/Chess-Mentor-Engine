# Positional Evaluation — CKO v1

Positional evaluation is modeled as a **meta-level assessment activity** over multiple
chess factors. It is not itself a strategic principle, and its factor vocabulary does
not replace engine evaluation.

## Three distinct objects

CKO keeps these separate:

```text
position fact or feature
    "White has an isolated d-pawn."

qualitative evaluation factor
    "White's pawn structure is a long-term concern."

engine evaluation
    "Stockfish reports +0.72 under the recorded search contract."
```

The first may be deterministic, the second is normally heuristic, and the third is
engine-derived evidence governed by the existing analysis contract.

## Evaluation-factor vocabulary

CKO v1 registers:

```text
evaluation.material
evaluation.king_safety
evaluation.development
evaluation.piece_activity
evaluation.piece_coordination
evaluation.mobility
evaluation.space
evaluation.center_control
evaluation.pawn_structure
evaluation.weak_squares
evaluation.passed_pawns
evaluation.initiative
evaluation.tactical_pressure
```

These factors provide a stable vocabulary for structured explanation and comparison.
They do not imply that every position should receive a value for every factor.

## No fake arithmetic decomposition

The ontology must not manufacture equations such as:

```text
space +0.3
bishop pair +0.4
isolated pawn -0.2
-------------------
Stockfish +0.5
```

unless a separately qualified method explicitly supports that decomposition.

Stockfish's numerical or mate evaluation remains its own bounded engine artifact.
Qualitative factors may help humans understand candidate reasons, but they are not
secret components extracted from the engine score.

## Countervailing factors

A useful assessment can preserve multiple conflicting observations:

```text
White:
  favorable: space
  favorable: piece activity
  unfavorable: isolated pawn
  unclear: long-term king safety
```

A downstream explanation may say that current dynamic advantages appear more
important than a static weakness **only when the supplied evidence supports that
interpretation**.

## Relation to principles

Principles tell the tutor which heuristics may be relevant. Evaluation factors
organize the current position assessment.

For example:

```text
position.passed_pawn
        ↓
principle.pawn.passed_pawn
        ↓
evaluation.passed_pawns
        ↓
plan.support_passed_pawn
```

The arrows represent useful semantic relationships, not automatic inference rules.

## Relation to learner evidence

A player can correctly identify a factor yet choose the wrong move, or miss a factor
while still find the right move. Therefore neither the engine evaluation nor the CKO
factor assessment can substitute for captured participant reasoning.

The M6/M7 evidence chain remains responsible for participant-specific discrepancy
and recurring learner inference.
