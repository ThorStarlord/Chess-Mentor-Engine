# FPV-PILOT-003 Protocol

Status: DESIGNED AND FROZEN — NOT EXECUTED.

Protocol version: 1.0  
Title: Player Decision Evidence Instrument Calibration  
Freeze date: 2026-08-29

## Research question

Can a two-stage reasoning-elicitation instrument capture both spontaneous chess reasoning and richer diagnostic information without collapsing observation into intervention?

Secondary question: What incremental information is obtained by standardized neutral probing after an initial spontaneous response but before engine feedback?

## Method

For each fresh position, preserve this order:

`A0 position state → A1 Stage A response frozen → A2 Stage B response frozen → E engine/chess evidence revealed`

Stage A captures spontaneous reasoning. Stage B uses the frozen standardized probe. Engine evidence is revealed only after both participant stages are frozen.

## Hypotheses

- H1: Stage B provides materially more diagnostically useful information than Stage A alone.
- H2: Stage A and Stage B capture meaningfully different aspects of reasoning and must remain separate evidence.
- H3: Neutral probing sometimes changes the move, candidate set, confidence, or understanding before engine reveal.
- H4: Standardized probing adds useful evidence without systematically teaching a specific chess-solving heuristic.
- H5: Probing adds too little information, or changes reasoning too much, to justify its complexity.

## Scope and claim ceiling

This is an instrument-calibration pilot, not product validation or a replication study. It may use P01 only if exposure auditing finds enough genuinely fresh positions. No cross-player, learning, rating, mastery, or production-architecture claims are permitted.

## Execution boundary

This design freezes the instrument only. It does not select positions, recruit participants, collect responses, reveal engine evidence, or implement production entities.
