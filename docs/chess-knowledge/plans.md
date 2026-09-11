# Strategic Plans — CKO v1

Plans connect position features and strategic principles to candidate long-horizon
objectives. A plan is neither an engine best move nor a learner intervention.

## Plan vocabulary

CKO v1 registers:

```text
plan.attack_king
plan.improve_worst_piece
plan.create_pawn_break
plan.open_file
plan.occupy_outpost
plan.exchange_key_defender
plan.trade_into_endgame
plan.create_second_weakness
plan.restrict_counterplay
plan.activate_king
plan.support_passed_pawn
plan.blockade_passed_pawn
plan.penetrate_seventh_rank
plan.double_on_open_file
plan.prophylaxis
plan.increase_piece_coordination
```

## Intended semantic chain

A coaching explanation can eventually traverse:

```text
position feature
        ↓
relevant principle
        ↓
evaluation factor
        ↓
candidate plan
        ↓
concrete engine-backed move comparison
```

Example:

```text
position.open_file
        ↓
principle.rook.open_file
        ↓
evaluation.piece_activity
        ↓
plan.double_on_open_file
        ↓
candidate move(s)
```

None of those arrows is an unconditional inference rule.

## Plans are contextual proposals

`plan.attack_king` means that attacking the king is a candidate strategic objective
supported by supplied evidence. It does not authorize the statement that an attack is
sound, forced, or optimal.

Likewise, `plan.trade_into_endgame` is not automatically justified by being ahead in
material. The concrete resulting endgame and tactical details still matter.

## Plans versus interventions

A chess plan describes what to pursue **inside the position**.

A training intervention describes what the mentor asks the learner to practice.

```text
plan.create_pawn_break
    chess-position objective

M9 intervention: practice identifying central pawn breaks
    tutoring objective
```

The ontology deliberately keeps those separate so a chess idea cannot silently grant
training-selection authority.

## Move-rationale use

Future `MoveConceptDelta` or knowledge-context surfaces may compare a played move and
an engine candidate using relations such as:

```text
supports
executes
preserves
enables
misses_opportunity
conflicts_with
```

The safer language is usually **supports** or **misses an opportunity** rather than
claiming a move “violates a principle.” A principle can be relevant without being the
causal reason the engine prefers a move.
