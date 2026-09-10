"""Repository-only M30 participant review package and navigation CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from chess_mentor_engine.coach_review_reference import CoachReviewReferenceError
from chess_mentor_engine.participant_review_package import (
    M30_CLAIM_SCOPE,
    M30_SCHEMA_VERSION,
    ParticipantReviewPackageError,
    build_participant_review_package,
    list_participant_review_navigation,
    load_participant_review_package,
    render_participant_review_package_surface,
    show_participant_review_item,
)
from chess_mentor_engine.persisted_review_reference import PersistedReviewReferenceError
from chess_mentor_engine.reviewed_coaching_ledger import ReviewedCoachingLedgerError
from chess_mentor_engine.storage import LocalArtifactStore, StorageError


class ParticipantReviewPackageCliError(ValueError):
    """The M30 CLI cannot safely read, navigate, or export local review data."""


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise ParticipantReviewPackageCliError(
            f"artifact database does not exist: {path}"
        )
    if not path.is_file():
        raise ParticipantReviewPackageCliError(
            f"artifact database path is not a file: {path}"
        )
    return LocalArtifactStore(path)


def _new_output_dir(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.exists() or path.is_symlink():
        raise ParticipantReviewPackageCliError(
            f"output directory already exists; refusing to overwrite: {path}"
        )
    return path


def _common(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--db", required=True)
    subparser.add_argument("--participant", required=True)


def _run_list(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    return list_participant_review_navigation(
        store=store,
        participant_id=args.participant,
    )


def _run_show(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    return show_participant_review_item(
        store=store,
        participant_id=args.participant,
        item_type=args.kind,
        artifact_id=args.id,
        include_content=args.include_content,
    )


def _atomic_export(
    *,
    output: Path,
    manifest: dict[str, object],
    html: str,
) -> tuple[Path, Path]:
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(
            tempfile.mkdtemp(
                prefix=f".{output.name}.tmp-",
                dir=output.parent,
            )
        )
    except OSError as exc:
        raise ParticipantReviewPackageCliError(
            f"could not prepare export directory: {exc}"
        ) from exc
    try:
        manifest_path = temporary / "manifest.json"
        html_path = temporary / "review.html"
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        html_path.write_text(html, encoding="utf-8", newline="\n")
        temporary.replace(output)
    except OSError as exc:
        shutil.rmtree(temporary, ignore_errors=True)
        raise ParticipantReviewPackageCliError(
            f"could not export review package: {exc}"
        ) from exc
    return output / "manifest.json", output / "review.html"


def _run_export(args: argparse.Namespace) -> dict[str, object]:
    store = _existing_store(args.db)
    output = _new_output_dir(args.output_dir)
    if args.package_id is not None:
        loaded = load_participant_review_package(
            store=store,
            participant_id=args.participant,
            package_artifact_id=args.package_id,
        )
        manifest = loaded.manifest_record
        manifest_ref = loaded.manifest_ref
        run_ref = loaded.run_ref
        review_ref = loaded.review_ref
        ledger_ref = loaded.ledger_ref
        surface = render_participant_review_package_surface(
            store=store,
            participant_id=args.participant,
            package_artifact_id=args.package_id,
        )
    else:
        built = build_participant_review_package(
            store=store,
            participant_id=args.participant,
            run_artifact_id=args.run_id,
            review_artifact_id=args.review_id,
        )
        manifest = built.manifest_record
        manifest_ref = built.manifest_ref
        run_ref = built.run_ref
        review_ref = built.review_ref
        ledger_ref = built.ledger_ref
        surface = built.surface

    manifest_path, html_path = _atomic_export(
        output=output,
        manifest=manifest,
        html=surface.html,
    )
    return {
        "schema_version": M30_SCHEMA_VERSION,
        "participant_id": args.participant,
        "package_ref": manifest_ref.to_dict(),
        "run_ref": run_ref.to_dict(),
        "review_ref": review_ref.to_dict(),
        "ledger_ref": ledger_ref.to_dict(),
        "reference_surface": manifest["reference_surface"],
        "claim_scope": M30_CLAIM_SCOPE,
        "output_dir": str(output.resolve()),
        "manifest_output": str(manifest_path.resolve()),
        "html_output": str(html_path.resolve()),
        "external_calls": False,
        "production_ui_claim": False,
        "tutor_state_advanced": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme-participant-review",
        allow_abbrev=False,
        description=(
            "List, show, or export participant-scoped M26/M27/M25/M28 review "
            "chains. Summary navigation contains references and fingerprints only; "
            "source payloads or HTML require an explicit show/export action."
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    list_parser = commands.add_parser("list", allow_abbrev=False)
    _common(list_parser)
    list_parser.set_defaults(handler=_run_list)

    show_parser = commands.add_parser("show", allow_abbrev=False)
    _common(show_parser)
    show_parser.add_argument(
        "--kind",
        required=True,
        choices=("run", "review", "ledger", "package", "surface"),
    )
    show_parser.add_argument("--id", required=True)
    show_parser.add_argument(
        "--include-content",
        action="store_true",
        help=(
            "Explicitly include the selected persisted payload, or rendered HTML "
            "for a surface. Without this flag only navigation metadata is emitted."
        ),
    )
    show_parser.set_defaults(handler=_run_show)

    export_parser = commands.add_parser("export", allow_abbrev=False)
    _common(export_parser)
    selector = export_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--run-id")
    selector.add_argument("--review-id")
    selector.add_argument("--package-id")
    export_parser.add_argument(
        "--output-dir",
        required=True,
        help="New directory for manifest.json and review.html; never overwritten",
    )
    export_parser.set_defaults(handler=_run_export)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = args.handler(args)
    except (
        ParticipantReviewPackageCliError,
        ParticipantReviewPackageError,
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
