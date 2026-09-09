# M14 — Engine-backed analysis CLI

## Scope

M14 adds one bounded product command over already-qualified M3/M4 chess evidence:

```text
canonical PGN position
-> explicit UCI engine request
-> normalized M3 PositionAnalysis
-> exact native M4 DecisionComparison
-> optional immutable local archive
```

The command does not invent UI score semantics, learner psychology, tutoring prose,
training recommendations, M7 revisions, or M11 state changes.

## Command

Install the repository as usual, then run:

```bash
cme analyze game.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000
```

Exactly one of the supported search-limit forms may be selected:

```text
--depth N
--nodes N
--movetime-ms N
```

`--depth 12` is the default. `--multipv` and `--timeout-ms` require positive
integers. Repeatable engine configuration uses `--engine-option NAME=VALUE`.
`MultiPV` is owned by `--multipv` and is rejected through `--engine-option`.

## Played-move comparison

M14 analyzes the exact canonical root position. If the canonical played move is in
the root MultiPV, M4B compares the root rank-1 evaluation and the played line from
the same analysis.

If the played move is outside a complete root MultiPV, M14 analyzes the exact
canonical child position using the same provider configuration and exact
`AnalysisRequest`. M4B then decides whether the two analyses are compatible.
Changing engine identity, binary/configuration, search limit, MultiPV, timeout, or
other regime-bearing evidence remains `incompatible_analysis_regime`; M14 does not
coerce it into a numeric loss.

Partial, bounded, mate, terminal, failure, and engine-evidence-inversion semantics
remain owned by the qualified M3/M4 contracts. Centipawn and mate evaluations stay
stored from White's perspective while `exact_centipawn_delta_for_mover` remains
mover-relative.

## Output

Successful output is one JSON document:

```text
archive_ref
package
  schema_version = m14.engine-analysis-cli.v1
  source
  analysis_request
  root_analysis
  played_child_analysis
  decision_comparison
```

`root_analysis` and optional `played_child_analysis` are the native normalized M3
records. `decision_comparison` is the native M4B record. This is an evidence package,
not the final UI presentation contract; frontend display semantics remain deferred
to a separate milestone.

A root engine failure is a failed CLI operation: exit code `2`, no partial JSON,
and a concise error on stderr. Child-analysis failures may remain inside a valid
M4 comparison as explicit incomparable evidence because the qualified comparison
contract can preserve that state without manufacturing a score.

## Optional archival

M14 never creates an artifact database implicitly. To archive the exact package,
first create/provision an existing database through an owning workflow, then supply
both scope arguments:

```bash
cme analyze game.pgn \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --db ./mentor.sqlite3 \
  --participant P01
```

Both `--db` and `--participant` are required together. The content-addressed package
is stored as `m14.analysis-package.v1`; exact retries are idempotent. This generic
archive does not mutate M7, M8, M9, M10, or M11 state and is not a typed migration
or hosted persistence service.

## Qualification

Focused M14 qualification:

```bash
python -m pytest tests/test_m14_engine_analysis_cli.py
```

Native related contracts:

```bash
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
python -m pytest tests/test_decision_comparison.py
python -m pytest tests/test_m12_cli.py tests/test_m13_persistent_tutor_cli.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final Stockfish command requires `STOCKFISH_EXECUTABLE`; skips are not an
independent engine pass. Pull-request CI remains the merge gate.

## Boundaries

M14 explicitly does **not** implement:

- a UI-safe evaluation projection or score formatting contract;
- LLM/model invocation;
- automatic M6 discrepancy generation;
- mentor explanation generation;
- automatic M7/M11 mutation;
- training assignment;
- web UI or hosted services;
- empirical tutoring-efficacy or mastery claims.
