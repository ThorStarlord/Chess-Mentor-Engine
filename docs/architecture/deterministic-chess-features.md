# M2 — Deterministic Chess Feature Extraction

## Status

**Qualified and merged.** M2 is the second bounded product-development layer on top
of the qualified M1 chess-evidence substrate. The wider tutoring and learner-model
architecture remains provisional.

Qualified candidate head:

```text
0084c05f37e558ab467e2eae304fb03637bee8bd
```

Merge commit on `main`:

```text
71ab75bf99368348a917add5fa009a9774fcee13
```

The merge commit is tree-identical to the qualified candidate head.

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

For the same canonical FEN, M2 produces the same packet. UCI move lists, square
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
provider-neutral public records. The GPL `chess` package was used only in an isolated
verification spike and was not merged as a runtime or development dependency.

## Qualification evidence

### Direct candidate qualification — PR #2

On exact head `0084c05f37e558ab467e2eae304fb03637bee8bd`:

- 20/20 repository tests passed;
- Ruff passed;
- the existing M1 suite remained green;
- seven direct M2 feature tests passed;
- no engine, LLM, learner-model, pedagogy, database, or UI scope was introduced.

### Independent oracle qualification — PR #3

The closed, unmerged oracle spike used `chess==1.11.2` only for verification.
On eight representative FENs:

- legal move sets matched;
- legal check sets matched;
- legal capture sets matched, including en passant;
- white and black geometric attacker sets matched on all 64 squares;
- same-color defender relations matched for every occupied square;
- absolute pin color, pinned square, king square, and pinner square matched;
- 21/21 tests passed;
- Ruff passed.

### Promotion proof

The qualified PR #2 head was merged with a normal merge commit. Comparing the
qualified head to merge commit `71ab75bf99368348a917add5fa009a9774fcee13`
produced an empty file diff, proving tree equality. `main` CI passed again on the
merge commit.

## Qualification verdict

```text
M2 QUALIFIED
```
