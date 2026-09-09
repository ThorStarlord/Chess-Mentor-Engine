# M15 — Evaluation presentation contract

## Scope

M15 is a deterministic projection layer between qualified M3/M4 chess evidence and
future UI or mentor surfaces:

```text
M3 PositionAnalysis
+ M4 DecisionComparison
+ optional exact played-child analysis
        ↓
build_evaluation_presentation
        ↓
m15.evaluation-presentation.v1
```

It does not run an engine, change the M14 archive, infer learner psychology, assign
move-quality labels such as `blunder`, generate tutoring prose, or render a web UI.

## Why a separate contract exists

M3 stores engine evaluations from a fixed White perspective. M4 derives a signed
`exact_centipawn_delta_for_mover` only when evidence is exact and comparable. A UI
that directly consumes raw engine fields can easily introduce perspective bugs,
turn bounds into fake exact scores, or convert mate into arbitrary centipawn
sentinels.

M15 makes those display semantics explicit without changing upstream authority.

## Public API

```python
from chess_mentor_engine.presentation import build_evaluation_presentation

presentation = build_evaluation_presentation(
    root_analysis=root_analysis,
    comparison=decision_comparison,
    played_analysis=played_child_analysis,  # optional
)
```

The output schema version is:

```text
m15.evaluation-presentation.v1
```

## Score perspective

Every centipawn evaluation retains two explicit views:

```text
white
  centipawns
  bound

decision_mover
  side
  centipawns
  bound
```

The canonical M3 value is never overwritten. For a Black decision mover, M15
negates the White centipawn value for the mover view and reverses ordering bounds:

```text
white lower bound -> black-mover upper bound
white upper bound -> black-mover lower bound
exact -> exact
```

The name `decision_mover` is intentional. A played-child reanalysis has the
opponent to move, but the comparison is still about the original decision maker;
calling that child projection `side_to_move` would be ambiguous.

M15 does not convert centipawns into pawn floats or localized strings. Rounding and
visual formatting remain frontend concerns.

## Mate presentation

Mate remains symbolic:

```text
winner
plies_to_mate
white.favours_perspective
white.bound
decision_mover.side
decision_mover.favours_perspective
decision_mover.bound
```

There is no mate-to-centipawn sentinel and no invented `M#` string in the contract.

## Evidence quality

Analysis and comparison quality remain explicit:

```text
exact
bounded
partial
terminal
incompatible
unavailable
```

M15 maps M4 `partial_evidence`, `bound_limited`,
`incompatible_analysis_regime`, and `incomparable` without manufacturing an exact
loss. A non-exact comparison carrying `exact_centipawn_delta_for_mover` is rejected
rather than displayed.

## PV and engine identity

Each root or played-child `PositionAnalysis` projection preserves:

- request/result fingerprints;
- analysis status and termination;
- metrics;
- engine provider/name/version/protocol;
- binary SHA-256, options, and artifacts when available;
- ranked root moves;
- UCI principal variations;
- the projected evaluation for every candidate.

M15 does not convert PV moves to SAN because that is a separate board-context
presentation concern.

## Evidence-reference integrity

Before projection, M15 verifies that the M4 evidence references match the exact M3
records supplied. It also checks the root best move/evaluation, root-MultiPV played
rank/evaluation, and played-child reference shape.

Corrupted or mismatched evidence fails closed with `EvaluationPresentationError`.
The presentation layer does not silently substitute a nearby analysis record.

## Qualification

Focused M15 contract and rejection suite:

```bash
python -m pytest tests/test_m15_evaluation_presentation.py
```

Related upstream suites:

```bash
python -m pytest tests/test_decision_comparison.py
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final Stockfish command requires `STOCKFISH_EXECUTABLE`; skips are not an
independent engine pass. Pull-request CI is the merge gate.

## Boundaries

M15 explicitly does **not** implement:

- web or desktop UI components;
- localized/rounded score strings;
- SAN PV rendering;
- move-quality taxonomies such as `inaccuracy`, `mistake`, or `blunder`;
- LLM/model invocation;
- mentor explanation generation;
- automatic M6/M7/M11 mutation;
- training assignment;
- hosted services;
- empirical tutoring-efficacy claims.
