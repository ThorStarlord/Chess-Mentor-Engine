# M12 — Local evidence CLI

M12 is a deliberately thin read-only adapter over capabilities that already have their own authority contracts.

```text
UTF-8 PGN
   │
   ├── cme games inspect ──> M1 ingest_pgn ──> deterministic JSON
   │
   └── cme position packet ─> M1 build_position_context ─> engine-free packet

existing SQLite artifact DB
   │
   └── cme artifacts {list,show,verify}
             │
             └── LocalArtifactStore verified participant-scoped reads
```

## Why read-only first

A convenient import or tutoring command would need to decide new questions: how duplicate semantic games with distinct source provenance are represented, which artifacts are current, how M7/M11 writes are authorized, and how interactive information sequencing is preserved. Those are product contracts, not CLI formatting details. M12 therefore exposes inspection before mutation.

## Determinism

Successful output is sorted/indented JSON. Game summaries are generated from the exact M1 producer. Position packets are the native `PositionContextPacket.to_dict()` payload. Artifact references and payloads come from integrity-verified storage reads.

## Scope isolation

Artifact commands require `--participant`. A logical artifact ID in another participant scope is reported as not found; the command does not probe other scopes or include their content in errors.

## Non-goals

M12 does not implement:

- PGN-to-database import;
- session start/resume UX;
- hypothesis or longitudinal-state writes;
- Stockfish invocation;
- LLM calls;
- training assignment;
- local web UI;
- hosted multi-user service.

See [ADR 0011](../decisions/0011-local-evidence-cli-contract.md) and the [M12 CLI runbook](../runbooks/m12-local-evidence-cli.md).
