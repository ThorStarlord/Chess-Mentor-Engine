"""Repository-only M26 CLI over a persisted compared tutor checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from chess_mentor_engine.reviewed_coaching import (
    PersistentReviewedCoachingError,
    run_persistent_reviewed_coaching,
)
from chess_mentor_engine.storage import LocalArtifactStore, StorageError


class ReviewedCoachingCliError(ValueError):
    """The M26 local operator cannot be invoked safely."""


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise ReviewedCoachingCliError(f"artifact database does not exist: {path}")
    if not path.is_file():
        raise ReviewedCoachingCliError(
            f"artifact database path is not a file: {path}"
        )
    return LocalArtifactStore(path)


def _run(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    result = run_persistent_reviewed_coaching(
        store=store,
        participant_id=args.participant,
        session_artifact_id=args.session_artifact_id,
        grounding_created_at=args.created_at,
    )
    return {
        "schema_version": result.run_record["schema_version"],
        "participant_id": args.participant,
        "source_session_ref": result.run_record["source_session_ref"],
        "source_state": result.run_record["source_tutor_state"]["state"],
        "grounded_feedback_ref": result.feedback_ref.to_dict(),
        "model_request_ref": None,
        "provider_execution_ref": None,
        "model_coaching_ref": None,
        "evaluation_request_ref": None,
        "evaluator_execution_ref": None,
        "model_evaluation_ref": None,
        "coach_review_ref": result.read_model_ref.to_dict(),
        "run_ref": result.run_ref.to_dict(),
        "tutor_state_advanced": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-reviewed-coaching",
        allow_abbrev=False,
        description=(
            "Build deterministic M16 grounding and M25 review from one exact "
            "persisted M13 compared checkpoint. This CLI invokes no model or engine."
        ),
    )
    parser.add_argument("session_artifact_id")
    parser.add_argument("--db", required=True)
    parser.add_argument("--participant", required=True)
    parser.add_argument("--created-at", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = _run(args)
    except (
        PersistentReviewedCoachingError,
        ReviewedCoachingCliError,
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
