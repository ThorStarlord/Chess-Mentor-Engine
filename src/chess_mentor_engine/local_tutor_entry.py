"""Installed entry point for the V1 local tutor vertical slice."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from chess_mentor_engine.local_tutor import LocalTutorWorkflowError
from chess_mentor_engine.local_tutor_cli import (
    LocalTutorCliError,
    _add_common_arguments,
    _cmd_local_tutor_next,
    _cmd_local_tutor_start,
)
from chess_mentor_engine.storage import StorageError
from chess_mentor_engine.tutoring import TutorSessionError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-local-tutor",
        description=(
            "Exercise the V1 local learner/tutor workflow while preserving M18, "
            "M45, M8, M46, and M42 authority boundaries."
        ),
        allow_abbrev=False,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser(
        "start",
        help=(
            "Rank an exact M18 batch with M45, explicitly authorize the rank-one "
            "review through M23, persist M8, and emit the first M46 proposal."
        ),
    )
    start.add_argument("pgn", help="Exact PGN used to produce the M18 queue.")
    _add_common_arguments(start)
    start.add_argument("--db", required=True)
    start.add_argument("--protocol-json", required=True)
    start.add_argument("--prompts-json", required=True)
    start.add_argument(
        "--selection-decision",
        required=True,
        choices=("selected", "declined"),
        help="Explicit authorization for the M45 rank-one review proposal.",
    )
    start.add_argument(
        "--capture-consent",
        required=True,
        choices=("granted", "declined"),
    )
    start.add_argument("--recorded-at", required=True)
    start.add_argument("--create-db", action="store_true")
    start.set_defaults(handler=_cmd_local_tutor_start)

    next_action = commands.add_parser(
        "next",
        help=(
            "Replay an exact persisted M8 checkpoint and emit the current "
            "M46 proposal."
        ),
    )
    _add_common_arguments(next_action)
    next_action.add_argument("--db", required=True)
    next_action.add_argument(
        "session_artifact_id",
        help="Exact persisted M8 session artifact ID from start or cme tutor.",
    )
    next_action.set_defaults(handler=_cmd_local_tutor_next)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = args.handler(args)
    except (
        LocalTutorCliError,
        LocalTutorWorkflowError,
        StorageError,
        TutorSessionError,
        json.JSONDecodeError,
        OSError,
        UnicodeError,
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
