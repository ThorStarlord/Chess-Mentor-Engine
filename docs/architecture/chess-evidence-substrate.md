# M1 — Trustworthy Chess Evidence Substrate

## Status

Implemented as the first bounded product-development substrate. The public contracts
are deliberately narrow; the repository's broader architecture remains provisional.

## Boundary

M1 converts exact PGN source bytes into deterministic, immutable records:

```text
PGN source
→ SourceProvenance
→ CanonicalGame
→ CanonicalPosition[]
→ PositionContextPacket
```

M1 deliberately does **not** implement engine evaluation, player reasoning,
diagnosis, learner hypotheses, pedagogy, persistence, or UI.

## Identity

Two identities are kept separate:

- **Source fingerprint** — SHA-256 of the exact input bytes.
- **Semantic game fingerprint** — SHA-256 of canonical Standard-chess semantics:
  normalized initial FEN plus the mainline UCI move sequence.

Comments, NAGs, whitespace, and annotation prose may change the source fingerprint
but do not change semantic game identity.

A `CanonicalPosition` identity is derived from the semantic game fingerprint, ply
index, and canonical FEN.

## Position indexing

`ply_index = 0` is the initial position. Each legal mainline move creates the next
position. `last_move_uci` and `last_move_san` are `None` for the initial position.

## Supported chess scope

- Standard chess from the normal starting position.
- Standard chess from a valid custom FEN (`SetUp/FEN` or Lichess
  `Variant "From Position"`).
- Castling, en passant, and promotions during deterministic replay.
- Multi-game PGN sources.

Unsupported variants are rejected explicitly.

## Rules implementation boundary

M1 currently uses a small private Standard-chess replay core and adds no runtime
dependency. That core is an implementation detail, not a domain contract. Public M1
records expose only stable primitive values and immutable records, so the replay core
can later be replaced by a mature chess-rules library without changing the evidence
model.

The private core should not be expanded into engine analysis or subjective chess
interpretation. A dependency substitution should be reconsidered before materially
expanding the chess-rules surface.

## Position Context Packet

The deterministic packet contains:

- FEN;
- side to move and move number;
- stable ASCII board in White-oriented canonical orientation;
- deterministic piece map;
- material piece counts;
- exact source provenance.

It does not state whether a position is good, bad, tactical, strategic, winning, or
appropriate for training.

## Authority boundary

```text
canonical chess state
≠ engine analysis
≠ player reasoning
≠ analyst interpretation
≠ learner diagnosis
```

## Qualification invariants

M1 tests preserve these invariants:

- repeated imports produce stable source and semantic identities;
- comment/annotation changes may alter source identity but not semantic identity;
- changed mainline chess content changes semantic identity;
- replay produces one initial position plus one position per mainline ply;
- custom-FEN starts, castling, en passant, and promotions replay deterministically;
- Position Context Packet board, piece map, and material are derived from stored FEN;
- malformed input and unsupported variants fail explicitly.
