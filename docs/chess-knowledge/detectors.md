# Qualified Chess Knowledge Detectors

The first Chess Knowledge Ontology detector package is deliberately conservative.
It implements only concepts that Chess Mentor Engine can derive mechanically from
its current Standard-chess replay core and existing M2 feature substrate.

## Detector contract

Every detector publishes a content-fingerprinted `DetectorSpec` containing:

```text
detector ID
version
input kind
supported ontology concept IDs
claim scope
```

Every emitted `KnowledgeAssertion` carries that detector identity and fingerprint as
provenance. A detector may assert only the default authority registered for the
concept; changing the concept's authority or semantics therefore invalidates stale
detector assumptions instead of silently upgrading them.

## Position detector v1

`cme.position-knowledge-detector` consumes one canonical position and currently
supports:

```text
rule.check
rule.checkmate
tactic.absolute_pin
position.bishop_pair
position.open_file
position.semi_open_file
position.isolated_pawn
position.doubled_pawns
position.passed_pawn
position.pawn_island
```

The absolute-pin assertion reuses the already-qualified M2 `PositionFeaturePacket`
rather than implementing a second independent pin definition.

Structural assertions include exact qualifiers such as color, file, pawn square, or
pin geometry so downstream code does not have to recover meaning from display text.

## Move detector v1

`cme.move-knowledge-detector` replays one exact legal UCI move from a canonical
position and currently supports:

```text
tactic.promotion
tactic.underpromotion
tactic.fork
tactic.discovered_check
tactic.double_check
```

The detector derives these from the before/after board transition:

- promotion/underpromotion comes from the legal move representation;
- fork requires the moved piece itself to attack at least two opposing pieces after
  the move;
- discovered check requires a newly uncovered checker other than the moved piece;
- double check requires at least two actual attackers of the opposing king after the
  move.

These are sequence-pattern assertions, not statements about whether the move is best,
winning, pedagogically important, or recognized by the learner.

## Explicitly not detected in v1

The following registered concepts remain vocabulary or heuristic concepts rather than
being promoted into deterministic detector output:

```text
relative pin
x-ray attack
deflection
attraction
overload
trapped piece
desperado
clearance
intermezzo
quiet move
sacrifice
pawn breakthrough
named mating-pattern geometry
fortress
zugzwang
initiative
prophylaxis
bad bishop / good bishop
weak-square judgment
best strategic plan
principle violation
```

Some of these may eventually receive bounded heuristic detectors. That requires a
separate contract and negative qualification; registering a concept never implies an
automatic detector exists.

## Evidence and identity

Position detector assertions bind either directly to the canonical position or to the
exact M2 feature packet when reusing M2-derived pin evidence.

Move detector assertions bind to a canonical transition payload containing:

```text
starting canonical position
exact legal move UCI
resulting FEN
```

Both detector families are content-addressed through the K4 assertion model.

## Negative qualification

Detector tests include or should preserve near-miss/rejection cases for:

- illegal moves;
- check without mate;
- no fork when the moved piece does not attack two targets;
- queen promotion versus underpromotion;
- absolute-pin geometry from the existing M2 feature definition;
- deterministic rebuild from identical explicit inputs.

## Learner boundary

Detector output must never be shortened to:

```text
fork present + player did not play the tactic
-> player has a fork weakness
```

The correct learner chain remains:

```text
position/move knowledge assertion
        +
participant reasoning evidence
        ↓
M6 reasoning discrepancy
        ↓
M7/M7C recurrence and contradiction assessment
        ↓
learner hypothesis when justified
```
