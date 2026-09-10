"""Repository-only M28 CLI for a deterministic M25 HTML reference surface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_reference import (
    M28_CLAIM_SCOPE,
    M28_SCHEMA_VERSION,
    CoachReviewReferenceError,
    build_coach_review_reference_surface_from_bundle,
)
from chess_mentor_engine.review import CoachReviewReadModelError


class CoachReviewReferenceCliError(ValueError):
    """The M28 local reference command cannot safely read or write its files."""


def _load(path_value: str) -> Any:
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        raise CoachReviewReferenceCliError(f"bundle file does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoachReviewReferenceCliError(
            f"could not read bundle JSON: {exc}"
        ) from exc


def _output_path(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.exists():
        raise CoachReviewReferenceCliError(
            f"output path already exists; refusing to overwrite: {path}"
        )
    if path.suffix.lower() not in {".html", ".htm"}:
        raise CoachReviewReferenceCliError("output path must end in .html or .htm")
    return path


def _run(args: argparse.Namespace) -> dict[str, Any]:
    bundle = _load(args.bundle_json)
    output = _output_path(args.output)
    surface = build_coach_review_reference_surface_from_bundle(bundle)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(surface.html, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise CoachReviewReferenceCliError(
            f"could not write reference HTML: {exc}"
        ) from exc
    return {
        "schema_version": M28_SCHEMA_VERSION,
        "surface_id": surface.surface_id,
        "fingerprint": surface.fingerprint,
        "m25_read_model_id": surface.read_model["read_model_id"],
        "m25_read_model_fingerprint": surface.read_model["fingerprint"],
        "claim_scope": M28_CLAIM_SCOPE,
        "output": str(output.resolve()),
        "external_calls": False,
        "production_ui_claim": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-coach-review-reference",
        allow_abbrev=False,
        description=(
            "Validate one strict local M25 coach-review bundle and render a static "
            "semantic HTML reference surface. No model, engine, network, or browser "
            "automation is invoked."
        ),
    )
    parser.add_argument("bundle_json", help="Path to a strict local M25 input bundle")
    parser.add_argument(
        "--output",
        required=True,
        help="New .html/.htm path; existing files are never overwritten",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the repository-only M28 HTML reference renderer."""
    args = _parser().parse_args(argv)
    try:
        payload = _run(args)
    except (
        CoachReviewReferenceCliError,
        CoachReviewReferenceError,
        CoachReviewReadModelError,
        OSError,
        TypeError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(canonical_json(payload))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
