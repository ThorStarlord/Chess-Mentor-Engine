"""Local CLI over qualified evidence plus controlled persistent tutor transitions."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisRequest,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import (
    ChessEvidenceError,
    build_position_context,
    ingest_pgn,
)
from chess_mentor_engine.diagnostic_cli import (
    DiagnosticCliError,
    add_diagnostic_command,
)
from chess_mentor_engine.evidence import PlayerEvidenceError
from chess_mentor_engine.presentation import (
    EvaluationPresentationError,
    build_evaluation_presentation,
)
from chess_mentor_engine.selection import (
    DecisionComparisonError,
    compare_played_decision,
)
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


def _positive(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return parsed


def _engine_option(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("must use NAME=VALUE")
    name, option_value = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("engine option name must not be empty")
    if name.casefold() == "multipv":
        raise argparse.ArgumentTypeError(
            "MultiPV is controlled by --multipv, not --engine-option"
        )
    if "\n" in name or "\r" in name or "\n" in option_value or "\r" in option_value:
        raise argparse.ArgumentTypeError("engine option must be a single line")
    return name, option_value


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


def _select_game_position(result, game_index: int, ply_index: int):
    if game_index >= len(result.games):
        raise CliError(
            f"game index {game_index} is outside 0..{len(result.games) - 1}"
        )
    game = result.games[game_index]
    if ply_index >= len(game.positions):
        raise CliError(
            f"ply index {ply_index} is outside 0..{len(game.positions) - 1}"
        )
    return game, game.positions[ply_index]


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
    game, position = _select_game_position(
        result, args.game_index, args.ply_index
    )
    return build_position_context(game, position).to_dict()


def _analysis_request(args: argparse.Namespace) -> AnalysisRequest:
    if args.nodes is not None:
        limit = AnalysisLimit("nodes", args.nodes)
    elif args.movetime_ms is not None:
        limit = AnalysisLimit("movetime_ms", args.movetime_ms)
    else:
        limit = AnalysisLimit("depth", args.depth)
    return AnalysisRequest(
        multipv=args.multipv,
        search_limit=limit,
        supervisor_timeout_ms=args.timeout_ms,
    )


def _analysis_provider(args: argparse.Namespace) -> UciAnalysisProvider:
    options = tuple(args.engine_option)
    folded = [name.casefold() for name, _ in options]
    if len(folded) != len(set(folded)):
        raise CliError("duplicate engine option name")
    try:
        return UciAnalysisProvider(args.engine, engine_options=options)
    except ValueError as exc:
        raise CliError(str(exc)) from exc


def _analysis_outcome_payload(
    outcome: PositionAnalysis | AnalysisFailure,
) -> dict[str, Any]:
    return {
        "outcome_type": (
            "position_analysis"
            if isinstance(outcome, PositionAnalysis)
            else "analysis_failure"
        ),
        "record": outcome.to_dict(),
    }


def _archive_analysis_package(
    args: argparse.Namespace, package: dict[str, Any]
) -> dict[str, str] | None:
    if bool(args.db) != bool(args.participant):
        raise CliError("--db and --participant must be supplied together")
    if args.db is None:
        return None
    store = _existing_store(args.db)
    canonical = json.dumps(
        package,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    ref = store.put(
        kind="m14.analysis-package.v1",
        artifact_id=f"analysis_package_{digest[:20]}",
        participant_id=args.participant,
        payload=package,
    )
    return ref.to_dict()


def _cmd_analyze(args: argparse.Namespace) -> dict[str, Any]:
    result = _read_pgn(args.pgn)
    game, position = _select_game_position(
        result, args.game_index, args.ply_index
    )
    if position.ply_index >= len(game.moves_uci):
        raise CliError(
            "selected position has no canonical played move; choose a pre-move ply"
        )

    request = _analysis_request(args)
    provider = _analysis_provider(args)
    root_analysis = provider.analyze(position, request)
    if isinstance(root_analysis, AnalysisFailure):
        raise CliError(
            f"root engine analysis failed [{root_analysis.code}]: "
            f"{root_analysis.message}"
        )

    played_analysis = None
    played_move = game.moves_uci[position.ply_index]
    if (
        root_analysis.status == "complete"
        and played_move not in {line.root_move_uci for line in root_analysis.lines}
    ):
        child = game.positions[position.ply_index + 1]
        played_analysis = provider.analyze(child, request)

    comparison = compare_played_decision(
        game=game,
        position=position,
        root_analysis=root_analysis,
        played_analysis=played_analysis,
    )
    package = {
        "schema_version": "m14.engine-analysis-cli.v1",
        "source": {
            "source_sha256": result.source_sha256,
            "game_id": game.game_id,
            "game_index": args.game_index,
            "position_id": position.position_id,
            "ply_index": position.ply_index,
            "side_to_move": position.side_to_move,
            "fen": position.fen,
            "played_move_uci": played_move,
        },
        "analysis_request": request.to_dict(),
        "root_analysis": _analysis_outcome_payload(root_analysis),
        "played_child_analysis": (
            None
            if played_analysis is None
            else _analysis_outcome_payload(played_analysis)
        ),
        "decision_comparison": comparison.to_dict(),
    }
    presentation = None
    if getattr(args, "with_presentation", False):
        presentation = build_evaluation_presentation(
            root_analysis=root_analysis,
            comparison=comparison,
            played_analysis=played_analysis,
        )
    archive_ref = _archive_analysis_package(args, package)
    payload = {"package": package, "archive_ref": archive_ref}
    if presentation is not None:
        payload["presentation"] = presentation
    return payload


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
            "Inspect deterministic chess evidence, run bounded provenance-bound "
            "engine analysis, build diagnostic queues, verify local artifacts, or "
            "explicitly advance persisted M8 tutor checkpoints."
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

    analyze = surfaces.add_parser(
        "analyze",
        help="Run M3 engine analysis and M4 played-decision comparison.",
    )
    analyze.add_argument("pgn", help="UTF-8 PGN file path.")
    analyze.add_argument(
        "--game-index", type=_nonnegative, default=0, help="Zero-based game index."
    )
    analyze.add_argument(
        "--ply-index", type=_nonnegative, required=True, help="Zero-based ply index."
    )
    analyze.add_argument(
        "--engine", required=True, help="External UCI engine executable or PATH name."
    )
    limits = analyze.add_mutually_exclusive_group()
    limits.add_argument(
        "--depth", type=_positive, default=12, help="Search depth; default 12."
    )
    limits.add_argument("--nodes", type=_positive, help="Node search limit.")
    limits.add_argument(
        "--movetime-ms", type=_positive, help="Engine search time in milliseconds."
    )
    analyze.add_argument(
        "--multipv", type=_positive, default=3, help="Requested MultiPV count."
    )
    analyze.add_argument(
        "--timeout-ms",
        type=_positive,
        default=10_000,
        help="Supervisor timeout in milliseconds.",
    )
    analyze.add_argument(
        "--engine-option",
        action="append",
        type=_engine_option,
        default=[],
        metavar="NAME=VALUE",
        help="Repeatable UCI option; MultiPV is controlled separately.",
    )
    analyze.add_argument(
        "--with-presentation",
        action="store_true",
        help="Also emit the verified M15 UI-safe evaluation projection.",
    )
    analyze.add_argument(
        "--db", help="Existing artifact DB for optional package archival."
    )
    analyze.add_argument(
        "--participant", help="Participant scope required when --db is supplied."
    )
    analyze.set_defaults(handler=_cmd_analyze)

    add_diagnostic_command(surfaces)

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
        DecisionComparisonError,
        DiagnosticCliError,
        EvaluationPresentationError,
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
