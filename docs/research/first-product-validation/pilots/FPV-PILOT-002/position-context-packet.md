# Position Context Packet

Status: Research specification frozen with Pilot 002 protocol version 1.0. Not a production domain object.

The packet is a candidate evidence representation that makes board state explicit instead of requiring a reasoning system or participant to reconstruct it from notation.

## Required fields

```yaml
position_id:
game_id:
move_number:
side_to_move:

fen:
board_ascii:
piece_map:
material_summary:

played_move:
evaluation_before:
evaluation_after:

top_candidates:
  - move:
    evaluation:
    principal_variation:

source_provenance:
```

## Board representation

`board_ascii` should be deterministic and human-readable, for example:

```text
8  r . . q r . k .
7  . b . . . p p p
6  . . p . . . . .
5  p p b . . . . Q
4  . . . p . . . .
3  . . . . . . P P
2  P P P . . . B K
1  R . B . . R . .
   a b c d e f g h
```

`piece_map` and `material_summary` should be derived from the canonical FEN by deterministic tooling when possible.

## Interpretation fields

Fields such as `immediate_tactical_features` are not automatically objective. If included, label whether they came from deterministic calculation, engine output, analyst interpretation, or model reasoning. Do not place a learner diagnosis in the packet as though it were board state.

## Provenance

Record game ID, move number, FEN source, analysis tool, engine name/version/settings/limits when known, evaluation convention, and the time at which the packet was generated. Unknown provenance remains `unknown`.

