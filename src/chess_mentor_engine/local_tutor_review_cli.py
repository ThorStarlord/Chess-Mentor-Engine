"""CLI adapters for bounded post-V1 local product-use observation."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from chess_mentor_engine.chess import PositionContextPacket
from chess_mentor_engine.local_tutor_cli import (
    LocalTutorCliError,
    _load_session,
    _record_file,
)
from chess_mentor_engine.local_tutor_review import run_guided_baseline_capture
from chess_mentor_engine.observation.report import build_product_use_report
from chess_mentor_engine.storage import LocalArtifactStore

REVIEW_SCHEMA_VERSION = "post-v1.local-product-use-review.v1"
REPORT_SCHEMA_VERSION = "post-v1.local-product-use-report.v1"


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        raise LocalTutorCliError(f"artifact database does not exist: {path}")
    return LocalArtifactStore(path)


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _interactive_input(prompt: str) -> str:
    print(prompt, end="", file=sys.stderr, flush=True)
    return input("")


def _interactive_output(value: str) -> None:
    print(value, file=sys.stderr)


def _cmd_product_use_review(args: argparse.Namespace) -> dict[str, Any]:
    session_ref, _ = _load_session(
        db_value=args.db,
        participant_id=args.participant,
        artifact_id=args.session_artifact_id,
    )
    packet = _record_file(
        args.position_json,
        PositionContextPacket,
        label="M8 position context packet",
    )
    store = _existing_store(args.db)
    result = run_guided_baseline_capture(
        store=store,
        participant_id=args.participant,
        initial_session_ref=session_ref,
        position_context=packet,
        input_fn=_interactive_input,
        output_fn=_interactive_output,
        now_fn=_now,
    )
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "initial_session_ref": result.initial_session_ref.to_dict(),
        "final_session_ref": result.final_session_ref.to_dict(),
        "observation_refs": [ref.to_dict() for ref in result.observation_refs],
        "baseline_frozen": result.baseline_frozen,
        "abandoned": result.abandoned,
        "claim_scope": result.claim_scope,
        "learning_effect": result.learning_effect,
        "tutor_efficacy": result.tutor_efficacy,
        "mastery": result.mastery,
        "next_authority": "cme-local-tutor next",
        "m46_execution": "not_performed",
    }


def _cmd_product_use_report(args: argparse.Namespace) -> dict[str, Any]:
    store = _existing_store(args.db)
    report = build_product_use_report(store, participant_id=args.participant)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        **report.to_dict(),
    }


def add_product_use_commands(commands) -> None:
    review = commands.add_parser(
        "review",
        help=(
            "Guide one already-selected exact M8 checkpoint through baseline "
            "capture and freeze without executing M46."
        ),
    )
    review.add_argument("--db", required=True, help="Existing SQLite artifact database.")
    review.add_argument("--participant", required=True)
    review.add_argument(
        "--position-json",
        required=True,
        help="Structural JSON for the exact M8 PositionContextPacket.",
    )
    review.add_argument(
        "session_artifact_id",
        help="Exact selected m8.tutor-session.v1 artifact ID.",
    )
    review.set_defaults(handler=_cmd_product_use_review)

    report = commands.add_parser(
        "report",
        help=(
            "Summarize participant-scoped descriptive local product-use "
            "observations without learner or efficacy claims."
        ),
    )
    report.add_argument("--db", required=True, help="Existing SQLite artifact database.")
    report.add_argument("--participant", required=True)
    report.set_defaults(handler=_cmd_product_use_report)
