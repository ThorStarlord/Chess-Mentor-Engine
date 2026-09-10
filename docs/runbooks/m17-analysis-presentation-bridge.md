# M17 — Analysis-to-presentation CLI bridge

## Scope

M17 connects the already-qualified M14 engine-analysis path to the already-qualified
M15 evaluation-presentation contract without weakening either authority boundary.

```text
canonical PGN position
-> M14 explicit UCI analysis + native M4 DecisionComparison
-> exact in-memory M3/M4 records
-> M15 build_evaluation_presentation
-> optional UI-safe presentation in the same CLI response
```

The bridge is opt-in. Existing `cme analyze` output and the archived
`m14.analysis-package.v1` payload remain unchanged unless the caller asks for the
additional presentation projection.

## Command

Use the normal M14 command and add `--with-presentation`:

```bash
cme analyze game.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000 \
  --with-presentation
```

Successful output adds one top-level field:

```text
archive_ref
package
  schema_version = m14.engine-analysis-cli.v1
presentation
  schema_version = m15.evaluation-presentation.v1
```

Without `--with-presentation`, the response remains the existing M14 shape.

## Integrity and side-effect ordering

The bridge passes the exact in-memory `PositionAnalysis`, optional played-child
analysis, and `DecisionComparison` produced by the M14 path directly into the
qualified M15 projector. It does not deserialize or approximately reconstruct those
objects from emitted JSON.

M15 therefore remains responsible for verifying:

- exact root and played-child evidence references;
- request and result fingerprints;
- best/played evaluation consistency;
- root-MultiPV versus child-reanalysis sourcing;
- exact versus bounded/partial/incompatible comparison semantics;
- symbolic mate semantics;
- White versus original decision-mover score perspective and bound reversal.

If M15 rejects any relationship, `cme analyze` exits with code `2` and emits no JSON.
The projection is built before optional M14 archival, so a presentation-integrity
failure cannot leave behind an archived package from that failed CLI request.

## Archival boundary

`--with-presentation` does **not** change the M14 archive contract. With `--db` and
`--participant`, only the exact `m14.analysis-package.v1` payload is stored. The M15
projection is a derived response surface and can always be rebuilt from its exact
qualified inputs while those domain records are available.

M17 does not create a new artifact kind, implicitly create a database, or mutate M7,
M8, M9, M10, M11, or M16 state.

## Qualification

Focused bridge and rejection suite:

```bash
python -m pytest tests/test_m17_analysis_presentation_bridge.py
```

Related regression suites:

```bash
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final Stockfish command requires `STOCKFISH_EXECUTABLE`; skipped external-engine
tests are not an independent engine witness. Pull-request CI remains the merge gate.

## Boundaries

M17 explicitly does **not** implement:

- diagnostic analysis across a game or candidate batch;
- SAN conversion or localized/rounded display strings;
- move-quality labels such as `inaccuracy`, `mistake`, or `blunder`;
- web or desktop UI components;
- LLM/model invocation or generative mentor coaching;
- automatic M6/M7/M11 mutation;
- training assignment;
- authentication or hosted services;
- empirical tutoring-efficacy claims.

The next package may expand diagnostic move-analysis breadth, but it must consume
qualified M3/M4 evidence rather than bypass this boundary.
