"""M25 JSON inspection CLI for the deterministic coach-review read model."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.review import (
    CoachReviewReadModelError,
    build_coach_review_read_model_from_bundle,
)


class CoachReviewCliError(ValueError):
    """The M25 inspection CLI cannot read a valid local source bundle."""


def _load(path_value: str) -> Any:
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        raise CoachReviewCliError(f"bundle file does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoachReviewCliError(f"could not read bundle JSON: {exc}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-coach-review",
        description=(
            "Project already-qualified local M15/M18/M21/M8/M16/M19/M20 "
            "records into the M25 coach-review read model."
        ),
    )
    parser.add_argument("bundle_json", help="Path to a strict local M25 input bundle")
    return parser


def _run(args: argparse.Namespace) -> dict[str, Any]:
    return build_coach_review_read_model_from_bundle(_load(args.bundle_json))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository-only M25 JSON projection command."""
    args = _parser().parse_args(argv)
    try:
        result = _run(args)
    except (CoachReviewCliError, CoachReviewReadModelError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(canonical_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
