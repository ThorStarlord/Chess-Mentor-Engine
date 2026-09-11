# Tactical Motifs — CKO v1

This document is the human-readable companion to the machine-readable tactical
concepts in `ontology.v1.json`.

## Authority reminder

A registered motif defines vocabulary. It does **not** prove that the motif occurs in
a position. A detector or other assertion source must establish a position-specific
claim separately.

## Geometric and direct attack motifs

| Concept ID | Name | Initial detection support | Notes |
| --- | --- | --- | --- |
| `tactic.fork` | Fork | sequence-based | One piece attacks two or more opposing targets after a move. |
| `tactic.absolute_pin` | Absolute Pin | deterministic | The pinned piece cannot legally move without exposing its king. |
| `tactic.relative_pin` | Relative Pin | heuristic | Moving is legal but exposes a more important target; value/context matters. |
| `tactic.skewer` | Skewer | sequence-based | Higher-value line target moves and reveals a lower-value target. |
| `tactic.discovered_attack` | Discovered Attack | sequence-based | A move uncovers a long-range friendly attack. |
| `tactic.discovered_check` | Discovered Check | sequence-based | The uncovered attack checks the king. |
| `tactic.double_check` | Double Check | sequence-based | Two pieces check simultaneously after one move. |
| `tactic.x_ray_attack` | X-Ray Attack | heuristic | Latent line influence through an opposing piece. |
| `tactic.attacking_f2_f7` | Attack on f2 or f7 | heuristic | Attack focuses on the initially king-only defended f-pawn geometry. |

## Defender and piece manipulation

| Concept ID | Name | Initial detection support | Notes |
| --- | --- | --- | --- |
| `tactic.capturing_defender` | Capturing the Defender | sequence-based | A critical defender is captured to enable a follow-up. |
| `tactic.deflection` | Deflection | heuristic | A defender is forced or induced away from an essential duty. |
| `tactic.attraction` | Attraction | heuristic | An enemy piece is induced onto a tactically vulnerable square. |
| `tactic.overload` | Overloaded Piece | heuristic | One piece cannot maintain multiple critical defensive duties. |
| `tactic.interference` | Interference | sequence-based | A move interrupts an enemy line of attack or defense. |
| `tactic.trapped_piece` | Trapped Piece | heuristic | A piece lacks an adequate escape from impending material loss. |
| `tactic.desperado` | Desperado | heuristic | A doomed piece extracts value before being lost. |

## Line and tempo manipulation

| Concept ID | Name | Initial detection support |
| --- | --- | --- |
| `tactic.clearance` | Clearance | heuristic |
| `tactic.intermezzo` | Intermezzo / Zwischenzug | heuristic |
| `tactic.quiet_move` | Quiet Move | heuristic |
| `tactic.sacrifice` | Sacrifice | heuristic |

The initial classification is intentionally conservative. For example, merely moving
off a square is insufficient to prove a clearance motif; the follow-up use of the
vacated line/square must matter to the tactic.

## Pawn and promotion tactics

| Concept ID | Name | Initial detection support |
| --- | --- | --- |
| `tactic.promotion` | Promotion Tactic | sequence-based |
| `tactic.underpromotion` | Underpromotion | sequence-based |
| `tactic.pawn_breakthrough` | Pawn Breakthrough | heuristic |

## Classic mating patterns

CKO v1 registers:

```text
mate.back_rank
mate.smothered
mate.anastasia
mate.arabian
mate.boden
mate.dovetail
mate.hook
```

These are initially heuristic vocabulary even though checkmate itself is a rule fact.
A later detector must prove the named geometry rather than infer the pattern from mate
alone.

## Defensive and drawing resources

CKO v1 registers:

```text
defense.perpetual_check
defense.stalemate_resource
defense.fortress
defense.zugzwang
```

These require particular caution. A static position can look fortress-like or
zugzwang-like without a qualified search/proof establishing the stronger claim.

## Important distinctions

### Fork vs instructionally meaningful fork

The geometric condition “one piece attacks two targets” can be mechanically true
while being irrelevant to the position. Later detector layers may distinguish raw
pattern evidence from pedagogically important tactical opportunity.

### Absolute vs relative pin

Absolute pin is a legality fact and is suitable for deterministic detection. Relative
pin depends on the value/importance of the obscured target and therefore begins as a
heuristic concept.

### Deflection vs capturing the defender

They are related but not identical. Capturing the defender removes the defender by
capture. Deflection moves it away from its duty. The ontology keeps stable separate
IDs even if external taxonomies or coaching language sometimes blur the terms.

### Tactic present vs learner error

Never infer:

```text
motif exists + player move differs from engine move
-> learner failed to understand motif
```

A learner claim still requires participant evidence and the qualified M6/M7 chain.
