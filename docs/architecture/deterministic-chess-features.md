# M2 — Deterministic Chess Feature Extraction

## Status

Candidate bounded product-development layer built on the qualified M1 chess-evidence substrate.
The wider tutoring and learner-model architecture remains provisional.

## Boundary

M2 derives objective, engine-free chess relationships from a `CanonicalPosition`:

```text
CanonicalPosition
→ PositionFeaturePacket
├── legal moves
├── legal checks
├── legal captures
├── square attackers
├── piece defenders
└── absolute king pins
```

M2 deliberately does **not** implement engine evaluation, tactical motif labels,
strategic interpretation, threats, learner diagnosis, pedagogy, persistence, or UI.

## Semantics

### Geometric attack

A piece geometrically attacks a square when its movement geometry reaches that square
with normal occupancy blocking applied. King-safety legality is not applied.

A pinned piece can therefore still appear as a geometric attacker.

### Legal move

A legal move is a side-to-move action permitted by Standard-chess rules after
king-safety filtering.

### Legal capture

A legal capture is a legal move that removes an opponent piece, including legal
en-passant captures.

### Legal check

A legal check is a legal move that leaves the opponent king in check.

### Defender

A defender is a same-color geometric attacker of an occupied friendly square.
Defender therefore describes board geometry, not whether the defending piece could
legally move to that square in the current position.

### Absolute king pin

An absolute pin exists when a friendly non-king piece is the only blocker between
its king and an enemy rook, bishop, or queen on a compatible ray. Removing that
blocker from the ray would expose the king to check.

M2 does not classify relative pins.

## Determinism

For the same canonical FEN, M2 must produce the same packet. UCI move lists, square
relations, defender lists, and pins are sorted deterministically.

## Authority boundary

```text
geometric attack
≠ legal move
≠ legal capture
≠ engine evaluation
≠ player reasoning
≠ learner diagnosis
```

## Rules-provider boundary

M2 follows ADR 0001. The current private Standard-chess rules core remains behind
provider-neutral public records. New deterministic facts must be covered by direct
fixtures and independently cross-checked against a mature rules oracle before M2 is
qualified.

## Qualification gates

M2 is qualified only if:

- the existing M1 suite remains green;
- deterministic feature fixtures pass;
- legal moves, checks, captures, attack maps, defender relations, and pin states
  agree with the independent oracle across representative positions;
- Ruff passes;
- no engine, LLM, learner-model, pedagogy, database, or UI scope is introduced.
