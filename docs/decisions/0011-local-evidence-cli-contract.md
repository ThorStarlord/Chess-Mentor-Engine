# ADR 0011 — Local evidence CLI contract

**Status:** Accepted for M12 implementation  
**Scope:** First end-user command surface over already-qualified local evidence capabilities  
**Explicitly deferred:** web UI, hosted service, automatic tutoring orchestration, artifact mutation/import workflows, richer LLM productization

## Context

The repository roadmap says to build the domain and workflow through a CLI before a polished UI, and says the exact CLI should emerge from implemented capabilities rather than be frozen prematurely. M1 can already ingest deterministic PGN chess evidence and produce Position Context Packets. The local artifact store can already perform participant-scoped, integrity-verified reads. M11 now supplies a qualified longitudinal evidence model. What is missing is a narrow product surface that lets a human inspect these capabilities without writing Python.

A first CLI must not accidentally create new evidence authority, run an engine implicitly, expose another participant's artifacts, create empty databases during a read operation, or define mutation semantics merely for convenience.

## Decision

M12 adds the installed `cme` console command with three read-only surfaces:

```text
cme games inspect <pgn> [--full]
cme position packet <pgn> --game-index N --ply-index N
cme artifacts list --db <path> --participant <id> [--kind <kind>]
cme artifacts show --db <path> --participant <id> --kind <kind> <artifact-id>
cme artifacts verify --db <path> --participant <id>
```

### `games inspect`

Uses the native M1 `ingest_pgn` producer. Default output is bounded metadata; `--full` exposes the complete canonical M1 ingestion payload. It does not persist anything or analyze with an engine.

### `position packet`

Uses the exact M1 game/position selected by explicit zero-based indices and the native deterministic `build_position_context` producer. It is engine-free.

### artifact commands

Open only an already-existing local artifact database. `list_refs` and `get` remain the integrity authority. Commands require an exact participant scope. `show` resolves an artifact only inside that participant and exact kind. `verify` reads and validates every artifact/dependency reachable in the requested participant scope.

Read commands must not create a missing database.

## Output and failure contract

Successful commands emit one deterministic JSON document to stdout and return exit code `0`.

Expected user/data/integrity failures emit no partial JSON, write a concise `error:` message to stderr, and return exit code `2`. Argument grammar failures remain standard `argparse` exit-code-2 failures. Unexpected programming defects are not swallowed as user errors.

## Claim and authority ceiling

The CLI is an adapter. It cannot strengthen the evidence it displays. In particular it does not:

- infer player psychology from engine/chess evidence;
- create, revise, retire, or reactivate M7/M11 learner hypotheses;
- select or assign M9 training;
- convert M10 support into mastery or causal improvement;
- run an LLM or engine implicitly;
- mutate the artifact store.

## Consequences

The repository gains a real installable product entry point while keeping the first surface small enough to qualify exhaustively. Persistence/import UX, controlled interactive tutoring, web UI, and richer model orchestration remain separate future packages.
