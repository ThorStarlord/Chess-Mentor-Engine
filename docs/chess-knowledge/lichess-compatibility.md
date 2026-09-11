# Lichess Puzzle-Theme Compatibility

**External namespace:** `lichess.puzzle_theme`  
**Reference snapshot date used for the initial crosswalk:** 2026-08-19

## Purpose

Lichess puzzle themes provide a useful interoperability vocabulary for tactical
training. Chess Mentor Engine does not adopt the external theme list as its ontology
or authority model.

The upstream vocabulary mixes several dimensions, including tactical mechanisms,
checkmate patterns, game phases, endgame material classes, puzzle lengths, evaluation
outcomes, and source categories. CME therefore maps only concepts whose semantics are
useful to its internal knowledge model.

## Mapping semantics

Each mapping declares the external term's relation to the CME concept:

- `exact` — sufficiently equivalent for the ontology's intended semantic scope;
- `broader` — external term covers more cases than the internal concept;
- `narrower` — external term covers fewer cases than the internal concept;
- `related` — useful interoperability relation without equivalence.

One external theme may map to multiple CME concepts.

## Initial mapped themes

The first crosswalk intentionally covers:

```text
anastasiaMate
arabianMate
attackingF2F7
attraction
backRankMate
bodenMate
capturingDefender
clearance
deflection
discoveredAttack
discoveredCheck
doubleCheck
dovetailMate
fork
hookMate
interference
intermezzo
pin
promotion
quietMove
sacrifice
skewer
smotheredMate
trappedPiece
underPromotion
xRayAttack
zugzwang
```

## Important non-one-to-one case: `pin`

CME distinguishes:

```text
tactic.absolute_pin
tactic.relative_pin
```

The external `pin` label is treated as broader than either internal subtype. Importing
`pin` therefore returns both possible internal concepts; a consumer may not silently
select one without additional evidence.

## External source does not determine assertion authority

An imported theme can establish only that an external source attached that theme to
its own item, unless a separate CME detector independently verifies the concept.

For example:

```text
Lichess puzzle has theme `fork`
```

is not identical to:

```text
CME deterministic sequence detector proved `tactic.fork`
```

The two can coexist as separate provenance.

## Drift handling

The helper `unmapped_lichess_themes(...)` reports unknown/unmapped external IDs. New
upstream themes are never silently accepted as internal concepts.

Updating the upstream snapshot should be an explicit repository change that reviews:

1. newly introduced external IDs;
2. removed or renamed IDs;
3. semantic-description changes;
4. whether existing mapping relations remain valid.

## Out of scope

The initial mapping does not attempt to mirror every Lichess puzzle dimension.
Metadata such as puzzle length, source quality, game phase, or evaluation bucket may
be valuable elsewhere, but it should not be mislabeled as a tactical motif merely
because Lichess exposes it through the same theme vocabulary.
