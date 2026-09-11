# Strategic Principles — CKO v1

Strategic principles are **conditional heuristics**, not chess laws and not engine
truth. Their purpose is to give Chess Mentor Engine stable concepts for explaining
why a plan or move may make sense in context.

## Authority

A principle normally has `heuristic_assessment` authority. The mere presence of a
position feature does not prove that the associated principle should control the
move choice.

For example:

```text
position.isolated_pawn
    deterministic feature

principle.pawn.isolated_dynamic_static
    heuristic about how that feature may matter
```

Those are intentionally different ontology objects.

## Opening principles

CKO v1 registers:

```text
principle.opening.center_control
principle.opening.rapid_development
principle.opening.tempo_economy
principle.opening.king_safety
principle.opening.pawn_move_restraint
principle.opening.avoid_premature_queen
principle.opening.connect_rooks
```

These definitions are written with explicit concrete exceptions. For example,
opening tempo economy does not imply that moving a developed piece twice is wrong
when the move wins material, meets a threat, or serves king safety.

## Piece-placement principles

### Knights

```text
principle.knight.outpost
principle.knight.centralization
principle.knight.closed_positions
```

### Bishops

```text
principle.bishop.pair
principle.bishop.good_bad
principle.bishop.open_diagonals
principle.bishop.opposite_colored
```

### Rooks and king

```text
principle.rook.open_file
principle.rook.seventh_rank
principle.rook.behind_passed_pawn
principle.rook.doubling
principle.king.endgame_activation
```

## Pawn-structure principles

```text
principle.pawn.fewer_islands
principle.pawn.isolated_dynamic_static
principle.pawn.backward_pawn
principle.pawn.doubled_pawns
principle.pawn.passed_pawn
principle.pawn.pawn_break
principle.pawn.attack_chain_base
```

These intentionally distinguish a mechanically observable structure from its
strategic interpretation. `position.doubled_pawns`, for example, can be established
mechanically while the claim that the doubled pawns are actually a meaningful
weakness remains contextual.

## Universal strategic heuristics

```text
principle.trade.ahead_trade_pieces
principle.trade.behind_keep_pieces
principle.space.cramped_exchange_pieces
principle.space.preserve_piece_pressure
principle.two_weaknesses
principle.prophylaxis
principle.fix_weakness
principle.improve_worst_piece
```

## Endgame principles

```text
principle.endgame.opposition
principle.endgame.rule_of_square
principle.endgame.outside_passed_pawn
principle.endgame.cut_off_king
principle.endgame.do_not_hurry
principle.king.endgame_activation
```

## Conflicting principles are first-class

Chess principles frequently conflict. CKO therefore models
`commonly_conflicts_with` instead of pretending a checklist can select the move.

Examples in v1 include:

```text
principle.trade.ahead_trade_pieces
    <->
principle.space.preserve_piece_pressure
```

and:

```text
principle.opening.king_safety
    <->
principle.king.endgame_activation
```

The conflict relation does not say the two principles are logically inconsistent.
It says they can recommend different priorities depending on the concrete position.

## Coaching rule

Prefer language such as:

> The move supports rapid development and central control.

or:

> In this position, simplifying is consistent with the usual principle of reducing
> counterplay when materially ahead.

Avoid:

> This move is correct because chess principles say so.

Engine evidence, tactics, move comparison, and the learner's own reasoning must still
determine what can actually be claimed.
