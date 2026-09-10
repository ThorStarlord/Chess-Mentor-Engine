"""Repository-only M29 CLI from persisted reviewed coaching to M28 HTML."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from chess_mentor_engine.coach_review_reference import CoachReviewReferenceError
from chess_mentor_engine.persisted_review_reference import (
    M29_CLAIM_SCOPE,
    M29_SCHEMA_VERSION,
    PersistedReviewReferenceError,
    build_persisted_coach_review_reference,
)
from chess_mentor_engine.reviewed_coaching_ledger import ReviewedCoachingLedgerError
from chess_mentor_engine.storage import LocalArtifactStore, StorageError


class PersistedReviewReferenceCliError(ValueError):
    """The M29 local bridge cannot safely read or write its files."""


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise PersistedReviewReferenceCliError(
            f"artifact database does not exist: {path}"
        )
    if not path.is_file():
        raise PersistedReviewReferenceCliError(
            f"artifact database path is not a file: {path}"
        )
    return LocalArtifactStore(path)


def _output_path(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.exists():
        raise PersistedReviewReferenceCliError(
            f"output path already exists; refusing to overwrite: {path}"
        )
    if path.suffix.lower() not in {".html", ".htm"}:
        raise PersistedReviewReferenceCliError(
            "output path must end in .html or .htm"
        )
    return path


def _run(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    output = _output_path(args.output)
    result = build_persisted_coach_review_reference(
        store=store,
        participant_id=args.participant,
        run_artifact_id=args.run_id,
        review_artifact_id=args.review_id,
    )
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.surface.html, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise PersistedReviewReferenceCliError(
            f"could not write reference HTML: {exc}"
        ) from exc

    return {
        "schema_version": M29_SCHEMA_VERSION,
        "participant_id": args.participant,
        "run_ref": result.run_ref.to_dict(),
        "coach_review_ref": result.review_ref.to_dict(),
        "ledger_ref": result.ledger.ledger_ref.to_dict(),
        "mechanical_verification": "mechanically_verified",
        "surface_id": result.surface.surface_id,
        "surface_fingerprint": result.surface.fingerprint,
        "m25_read_model_id": result.surface.read_model["read_model_id"],
        "m25_read_model_fingerprint": result.surface.read_model["fingerprint"],
        "claim_scope": M29_CLAIM_SCOPE,
        "output": str(output.resolve()),
        "external_calls": False,
        "production_ui_claim": False,
        "tutor_state_advanced": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-persisted-coach-review-reference",
        allow_abbrev=False,
        description=(
            "Resolve one participant-scoped persisted M26/M25 chain, verify it "
            "through M27, and render the exact M25 payload through M28. No model, "
            "engine, network, browser automation, or production provider is invoked."
        ),
    )
    parser.add_argument("--db", required=True)
    parser.add_argument("--participant", required=True)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--run-id", help="Exact persisted M26 run artifact id")
    selector.add_argument("--review-id", help="Exact persisted M25 review artifact id")
    parser.add_argument(
        "--output",
        required=True,
        help="New .html/.htm path; existing files are never overwritten",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = _run(args)
    except (
        PersistedReviewReferenceCliError,
        PersistedReviewReferenceError,
        ReviewedCoachingLedgerError,
        CoachReviewReferenceError,
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
