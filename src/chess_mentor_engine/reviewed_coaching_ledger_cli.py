"""Repository-only CLI for M27 reviewed-coaching execution ledgers."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from chess_mentor_engine.reviewed_coaching_ledger import (
    ReviewedCoachingLedgerError,
    build_reviewed_coaching_execution_ledger,
)
from chess_mentor_engine.storage import LocalArtifactStore, StorageError


class ReviewedCoachingLedgerCliError(ValueError):
    """The M27 ledger CLI cannot be invoked safely."""


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise ReviewedCoachingLedgerCliError(
            f"artifact database does not exist: {path}"
        )
    if not path.is_file():
        raise ReviewedCoachingLedgerCliError(
            f"artifact database path is not a file: {path}"
        )
    return LocalArtifactStore(path)


def _run(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    run_ids = None if args.run_id is None else tuple(args.run_id)
    result = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id=args.participant,
        run_artifact_ids=run_ids,
    )
    return {
        "schema_version": result.ledger_record["schema_version"],
        "participant_id": args.participant,
        "run_count": result.ledger_record["run_count"],
        "summary": result.ledger_record["summary"],
        "fidelity_scope": result.ledger_record["fidelity_scope"],
        "ledger_ref": result.ledger_ref.to_dict(),
        "run_refs": [ref.to_dict() for ref in result.run_refs],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-reviewed-coaching-ledger",
        allow_abbrev=False,
        description=(
            "Verify persisted M26 reviewed-coaching lineage and write a privacy-"
            "bounded M27 execution ledger. This command performs no external calls."
        ),
    )
    parser.add_argument("--db", required=True)
    parser.add_argument("--participant", required=True)
    parser.add_argument(
        "--run-id",
        action="append",
        help=(
            "Select one M26 run artifact id. Repeat to select multiple runs. "
            "When omitted, all participant M26 runs are qualified."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = _run(args)
    except (
        ReviewedCoachingLedgerCliError,
        ReviewedCoachingLedgerError,
        StorageError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
