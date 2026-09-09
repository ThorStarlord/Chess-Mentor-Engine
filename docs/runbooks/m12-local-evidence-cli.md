# M12 local evidence CLI runbook

## Install

From the repository root:

```bash
python -m pip install -e ".[dev]"
cme --help
```

The console command is installed by the package's `project.scripts` entry point. You can also invoke the same adapter with:

```bash
python -m chess_mentor_engine.cli --help
```

## Inspect PGN games

```bash
cme games inspect games.pgn
cme games inspect games.pgn --full
```

The default result is a deterministic bounded summary. `--full` emits the complete canonical M1 ingestion payload. Neither command writes a database or runs Stockfish.

## Build a deterministic position packet

Indices are explicitly zero-based:

```bash
cme position packet games.pgn --game-index 0 --ply-index 12
```

The result is the native engine-free Position Context Packet for that exact canonical position.

## Inspect existing durable artifacts

All artifact operations require an exact participant scope and an **existing** database:

```bash
cme artifacts list --db mentor.sqlite --participant P01
cme artifacts list --db mentor.sqlite --participant P01 --kind outcome_assessment
cme artifacts show --db mentor.sqlite --participant P01 --kind outcome_assessment <artifact-id>
cme artifacts verify --db mentor.sqlite --participant P01
```

`show` returns the verified reference, exact dependency references, and payload. `verify` validates all artifacts visible in the requested participant scope and reports counts. These commands do not create a missing database and do not mutate an existing one.

## Failure behavior

Expected bad input, missing paths, invalid PGN, out-of-range indices, missing artifacts, unsupported/corrupt storage schemas, or integrity failures return exit code `2`, emit no partial JSON document, and print a concise error to stderr.

Do not bypass a verification error by editing the SQLite database. Reconcile or restore the authoritative artifact source instead.

## Qualification

```bash
python -m pytest tests/test_m12_cli.py
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The repository PR workflow also runs the independent Stockfish witness to prove the existing engine substrate remains intact. M12 itself does not invoke Stockfish.

## Boundary

M12 is inspection-only. It does not authorize PGN import persistence, learner-hypothesis mutation, longitudinal-state writes, automatic tutoring, training assignment, web UI, or richer LLM productization.
