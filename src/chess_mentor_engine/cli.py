"""Local CLI over qualified evidence plus controlled persistent tutor transitions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from chess_mentor_engine.chess import (
    ChessEvidenceError,
    build_position_context,
    ingest_pgn,
)
from chess_mentor_engine.evidence import PlayerEvidenceError
from chess_mentor_engine.storage import LocalArtifactStore, StorageError
from chess_mentor_engine.tutor_cli import TutorCliError, add_tutor_commands
from chess_mentor_engine.tutoring import TutorSessionError


class CliError(ValueError):
    """A requested CLI operation cannot be completed safely."""


def _nonnegative(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def _read_pgn(path_value: str):
    path = Path(path_value).expanduser()
    if not path.exists():
        raise CliError(f"PGN file does not exist: {path}")
    if not path.is_file():
        raise CliError(f"PGN path is not a file: {path}")
    return ingest_pgn(path.read_bytes())


def _existing_store(path_value: str) -> LocalArtifactStore:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise CliError(f"artifact database does not exist: {path}")
    if not path.is_file():
        raise CliError(f"artifact database path is not a file: {path}")
    return LocalArtifactStore(path)


def _game_summary(game) -> dict[str, Any]:
    return {
        "game_id": game.game_id,
        "white": game.white,
        "black": game.black,
        "result": game.result,
        "date": game.date,
        "variant": game.variant,
        "time_control": game.time_control.to_dict(),
        "mainline_move_count": game.mainline_move_count,
        "position_count": len(game.positions),
        "source_game_index": game.provenance.source_game_index,
    }


def _cmd_games_inspect(args: argparse.Namespace) -> dict[str, Any]:
    result = _read_pgn(args.pgn)
    if args.full:
        return result.to_dict()
    return {
        "source_sha256": result.source_sha256,
        "game_count": len(result.games),
        "games": [_game_summary(game) for game in result.games],
    }


def _cmd_position_packet(args: argparse.Namespace) -> dict[str, Any]:
    result = _read_pgn(args.pgn)
    if args.game_index >= len(result.games):
        raise CliError(
            f"game index {args.game_index} is outside 0..{len(result.games) - 1}"
        )
    game = result.games[args.game_index]
    if args.ply_index >= len(game.positions):
        raise CliError(
            f"ply index {args.ply_index} is outside 0..{len(game.positions) - 1}"
        )
    return build_position_context(game, game.positions[args.ply_index]).to_dict()


def _cmd_artifacts_list(args: argparse.Namespace) -> dict[str, Any]:
    store = _existing_store(args.db)
    refs = store.list_refs(participant_id=args.participant, kind=args.kind)
    return {
        "participant_id": args.participant,
        "artifact_count": len(refs),
        "artifacts": [ref.to_dict() for ref in refs],
    }


def _find_artifact_ref(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    kind: str,
    artifact_id: str,
):
    refs = store.list_refs(participant_id=participant_id, kind=kind)
    matches = tuple(ref for ref in refs if ref.artifact_id == artifact_id)
    if not matches:
        raise CliError(
            f"artifact not found for participant={participant_id!r}, "
            f"kind={kind!r}, id={artifact_id!r}"
        )
    if len(matches) != 1:
        raise CliError("artifact identity is unexpectedly ambiguous")
    return matches[0]


def _cmd_artifacts_show(args: argparse.Namespace) -> dict[str, Any]:
    store = _existing_store(args.db)
    ref = _find_artifact_ref(
        store,
        participant_id=args.participant,
        kind=args.kind,
        artifact_id=args.artifact_id,
    )
    stored = store.get(ref, participant_id=args.participant)
    return {
        "ref": stored.ref.to_dict(),
        "dependencies": [item.to_dict() for item in stored.dependencies],
        "payload": stored.payload,
    }


def _cmd_artifacts_verify(args: argparse.Namespace) -> dict[str, Any]:
    store = _existing_store(args.db)
    refs = store.list_refs(participant_id=args.participant)
    counts = Counter(ref.kind for ref in refs)
    return {
        "participant_id": args.participant,
        "verified": True,
        "artifact_count": len(refs),
        "kind_counts": dict(sorted(counts.items())),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cme",
        description=(
            "Inspect deterministic chess evidence and verified local artifacts, or "
            "explicitly advance persisted M8 tutor checkpoints. Tutor writes are "
            "append-only and do not generate diagnoses or learner-state changes."
        ),
        allow_abbrev=False,
    )
    surfaces = parser.add_subparsers(dest="surface", required=True)

    games = surfaces.add_parser("games", help="Inspect PGN chess evidence.")
    game_commands = games.add_subparsers(dest="games_command", required=True)
    inspect = game_commands.add_parser(
        "inspect", help="Parse PGN and emit deterministic game metadata."
    )
    inspect.add_argument("pgn", help="UTF-8 PGN file path.")
    inspect.add_argument(
        "--full",
        action="store_true",
        help="Emit the complete canonical ingestion payload instead of a summary.",
    )
    inspect.set_defaults(handler=_cmd_games_inspect)

    position = surfaces.add_parser("position", help="Inspect a canonical position.")
    position_commands = position.add_subparsers(
        dest="position_command", required=True
    )
    packet = position_commands.add_parser(
        "packet", help="Build an engine-free deterministic Position Context Packet."
    )
    packet.add_argument("pgn", help="UTF-8 PGN file path.")
    packet.add_argument(
        "--game-index", type=_nonnegative, default=0, help="Zero-based game index."
    )
    packet.add_argument(
        "--ply-index", type=_nonnegative, required=True, help="Zero-based ply index."
    )
    packet.set_defaults(handler=_cmd_position_packet)

    artifacts = surfaces.add_parser(
        "artifacts", help="Read and verify an existing local artifact database."
    )
    artifact_commands = artifacts.add_subparsers(
        dest="artifacts_command", required=True
    )

    list_command = artifact_commands.add_parser(
        "list", help="List exact verified artifact references."
    )
    _add_store_scope_arguments(list_command)
    list_command.add_argument("--kind", help="Optional exact artifact kind filter.")
    list_command.set_defaults(handler=_cmd_artifacts_list)

    show = artifact_commands.add_parser(
        "show", help="Show one exact verified artifact and its dependencies."
    )
    _add_store_scope_arguments(show)
    show.add_argument("--kind", required=True, help="Exact artifact kind.")
    show.add_argument("artifact_id", help="Exact logical artifact ID.")
    show.set_defaults(handler=_cmd_artifacts_show)

    verify = artifact_commands.add_parser(
        "verify", help="Verify every artifact reachable in one participant scope."
    )
    _add_store_scope_arguments(verify)
    verify.set_defaults(handler=_cmd_artifacts_verify)

    add_tutor_commands(surfaces)
    return parser


def _add_store_scope_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", required=True, help="Existing SQLite artifact DB.")
    parser.add_argument(
        "--participant", required=True, help="Exact participant scope identifier."
    )


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = args.handler(args)
    except (
        ChessEvidenceError,
        CliError,
        json.JSONDecodeError,
        OSError,
        PlayerEvidenceError,
        StorageError,
        TutorCliError,
        TutorSessionError,
        UnicodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
