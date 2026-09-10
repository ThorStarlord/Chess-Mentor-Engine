"""M18 bounded diagnostic move-analysis queue over qualified M3/M4 contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, get_args

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisRequest,
    PositionAnalysis,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import build_position_features, ingest_pgn
from chess_mentor_engine.selection import (
    DiagnosticCandidateBatchError,
    SelectionPolicy,
    SelectionPolicyError,
    SelectionQuota,
    SelectionSignalError,
    apply_selection_policy,
    build_diagnostic_candidate_batch,
    build_selection_signals,
    compare_played_decision,
)
from chess_mentor_engine.selection.model import SelectionSignalKind

QUEUE_SCHEMA_VERSION = "m18.diagnostic-analysis-queue.v1"
_POLICY_KEYS = frozenset(
    {
        "policy_id",
        "version",
        "requested_size",
        "candidate_min_cp_delta",
        "control_max_cp_delta",
        "close_choice_max_cp",
        "candidate_mate_relations",
        "include_rank1_controls",
        "excluded_signal_kinds",
        "minimum_controls",
        "maximum_per_game",
        "quotas",
    }
)
_REQUIRED_POLICY_KEYS = frozenset({"policy_id", "version", "requested_size"})
_QUOTA_KEYS = frozenset({"signal_kind", "minimum", "maximum"})
_VALID_SIGNAL_KINDS = frozenset(get_args(SelectionSignalKind))


class DiagnosticCliError(ValueError):
    """The requested M18 diagnostic workflow cannot be completed safely."""


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
        raise DiagnosticCliError(f"PGN file does not exist: {path}")
    if not path.is_file():
        raise DiagnosticCliError(f"PGN path is not a file: {path}")
    return ingest_pgn(path.read_bytes())


def _require_string_list(payload: dict[str, Any], name: str) -> tuple[str, ...]:
    value = payload.get(name, [])
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise DiagnosticCliError(f"policy field {name!r} must be a list of strings")
    return tuple(value)


def _selection_quotas(value: object) -> tuple[SelectionQuota, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise DiagnosticCliError("policy field 'quotas' must be a list")
    quotas: list[SelectionQuota] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise DiagnosticCliError(f"policy quota {index} must be an object")
        unknown = set(item) - _QUOTA_KEYS
        if unknown:
            names = ", ".join(sorted(unknown))
            raise DiagnosticCliError(
                f"policy quota {index} has unknown fields: {names}"
            )
        if "signal_kind" not in item:
            raise DiagnosticCliError(f"policy quota {index} is missing signal_kind")
        signal_kind = item["signal_kind"]
        if signal_kind not in _VALID_SIGNAL_KINDS:
            raise DiagnosticCliError(
                f"policy quota {index} has unknown signal_kind: {signal_kind!r}"
            )
        try:
            quotas.append(
                SelectionQuota(
                    signal_kind=signal_kind,
                    minimum=item.get("minimum", 0),
                    maximum=item.get("maximum"),
                )
            )
        except (TypeError, ValueError) as exc:
            raise DiagnosticCliError(f"invalid policy quota {index}: {exc}") from exc
    return tuple(quotas)


def _read_selection_policy(path_value: str) -> SelectionPolicy:
    path = Path(path_value).expanduser()
    if not path.exists():
        raise DiagnosticCliError(f"selection policy file does not exist: {path}")
    if not path.is_file():
        raise DiagnosticCliError(f"selection policy path is not a file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DiagnosticCliError("selection policy JSON must be an object")

    unknown = set(payload) - _POLICY_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise DiagnosticCliError(f"selection policy has unknown fields: {names}")
    missing = _REQUIRED_POLICY_KEYS - set(payload)
    if missing:
        names = ", ".join(sorted(missing))
        raise DiagnosticCliError(f"selection policy is missing fields: {names}")

    excluded = _require_string_list(payload, "excluded_signal_kinds")
    unknown_signals = set(excluded) - _VALID_SIGNAL_KINDS
    if unknown_signals:
        names = ", ".join(sorted(unknown_signals))
        raise DiagnosticCliError(
            f"selection policy has unknown excluded signal kinds: {names}"
        )
    mate_relations = _require_string_list(payload, "candidate_mate_relations")
    quotas = _selection_quotas(payload.get("quotas", []))

    values = dict(payload)
    values["candidate_mate_relations"] = mate_relations
    values["excluded_signal_kinds"] = excluded
    values["quotas"] = quotas
    try:
        return SelectionPolicy(**values)
    except (TypeError, ValueError) as exc:
        raise DiagnosticCliError(f"invalid selection policy: {exc}") from exc


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
        raise DiagnosticCliError("duplicate engine option name")
    try:
        return UciAnalysisProvider(args.engine, engine_options=options)
    except ValueError as exc:
        raise DiagnosticCliError(str(exc)) from exc


def _analysis_outcome_payload(
    outcome: PositionAnalysis | AnalysisFailure | None,
) -> dict[str, Any] | None:
    if outcome is None:
        return None
    return {
        "outcome_type": (
            "position_analysis"
            if isinstance(outcome, PositionAnalysis)
            else "analysis_failure"
        ),
        "record": outcome.to_dict(),
    }


def _selected_ply_range(game, start_ply: int, end_ply: int | None) -> tuple[int, int]:
    if not game.moves_uci:
        raise DiagnosticCliError("selected game has no canonical played moves")
    last_played_ply = len(game.moves_uci) - 1
    if start_ply > last_played_ply:
        raise DiagnosticCliError(
            f"start ply {start_ply} is outside 0..{last_played_ply}"
        )
    resolved_end = last_played_ply if end_ply is None else end_ply
    if resolved_end > last_played_ply:
        raise DiagnosticCliError(
            f"end ply {resolved_end} is outside 0..{last_played_ply}"
        )
    if resolved_end < start_ply:
        raise DiagnosticCliError("end ply must be greater than or equal to start ply")
    return start_ply, resolved_end


def _analyze_decision(*, game, position, provider, request):
    root_analysis = provider.analyze(position, request)
    played_analysis = None
    played_move = game.moves_uci[position.ply_index]
    if (
        isinstance(root_analysis, PositionAnalysis)
        and root_analysis.status == "complete"
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
    return root_analysis, played_analysis, comparison


def _source_pool_entry(
    *,
    game,
    position,
    root_analysis,
    played_analysis,
    comparison,
    signals,
    selection_result,
) -> dict[str, Any]:
    return {
        "ply_index": position.ply_index,
        "position_id": position.position_id,
        "side_to_move": position.side_to_move,
        "played_move_uci": game.moves_uci[position.ply_index],
        "root_analysis": _analysis_outcome_payload(root_analysis),
        "played_child_analysis": _analysis_outcome_payload(played_analysis),
        "decision_comparison": comparison.to_dict(),
        "signals": [signal.to_dict() for signal in signals],
        "selection": selection_result.to_dict(),
    }


def _cmd_diagnose(args: argparse.Namespace) -> dict[str, Any]:
    result = _read_pgn(args.pgn)
    if args.game_index >= len(result.games):
        raise DiagnosticCliError(
            f"game index {args.game_index} is outside 0..{len(result.games) - 1}"
        )
    game = result.games[args.game_index]
    start_ply, end_ply = _selected_ply_range(game, args.start_ply, args.end_ply)
    policy = _read_selection_policy(args.policy)
    request = _analysis_request(args)
    provider = _analysis_provider(args)

    source_pool: list[dict[str, Any]] = []
    policy_results = []
    root_failure_count = 0
    partial_root_count = 0
    incompatible_comparison_count = 0

    try:
        for ply_index in range(start_ply, end_ply + 1):
            position = game.positions[ply_index]
            root_analysis, played_analysis, comparison = _analyze_decision(
                game=game,
                position=position,
                provider=provider,
                request=request,
            )
            if isinstance(root_analysis, AnalysisFailure):
                root_failure_count += 1
            elif root_analysis.status == "partial":
                partial_root_count += 1
            if comparison.compatibility == "incompatible":
                incompatible_comparison_count += 1

            signals = build_selection_signals(
                comparison=comparison,
                root_features=build_position_features(position),
                root_analysis=root_analysis,
            )
            selection_result = apply_selection_policy(
                comparison=comparison,
                signals=signals,
                policy=policy,
            )
            policy_results.append(selection_result)
            source_pool.append(
                _source_pool_entry(
                    game=game,
                    position=position,
                    root_analysis=root_analysis,
                    played_analysis=played_analysis,
                    comparison=comparison,
                    signals=signals,
                    selection_result=selection_result,
                )
            )

        batch = build_diagnostic_candidate_batch(
            results=tuple(policy_results),
            policy=policy,
        )
    except (
        DiagnosticCandidateBatchError,
        SelectionPolicyError,
        SelectionSignalError,
    ) as exc:
        raise DiagnosticCliError(str(exc)) from exc

    return {
        "schema_version": QUEUE_SCHEMA_VERSION,
        "source": {
            "source_sha256": result.source_sha256,
            "game_id": game.game_id,
            "game_index": args.game_index,
            "start_ply": start_ply,
            "end_ply": end_ply,
            "position_count": end_ply - start_ply + 1,
        },
        "analysis_request": request.to_dict(),
        "selection_policy": policy.to_dict(),
        "policy_fingerprint": policy.fingerprint,
        "analysis_summary": {
            "root_failure_count": root_failure_count,
            "partial_root_count": partial_root_count,
            "incompatible_comparison_count": incompatible_comparison_count,
        },
        "source_pool": source_pool,
        "batch": batch.to_dict(),
    }


def add_diagnostic_command(surfaces) -> None:
    """Register the bounded M18 diagnostic queue command on the root CLI."""
    diagnose = surfaces.add_parser(
        "diagnose",
        help=(
            "Analyze a bounded game window and build a deterministic M4 "
            "candidate/control queue."
        ),
    )
    diagnose.add_argument("pgn", help="UTF-8 PGN file path.")
    diagnose.add_argument(
        "--game-index", type=_nonnegative, default=0, help="Zero-based game index."
    )
    diagnose.add_argument(
        "--start-ply",
        type=_nonnegative,
        default=0,
        help="Inclusive first played ply; default 0.",
    )
    diagnose.add_argument(
        "--end-ply",
        type=_nonnegative,
        help="Inclusive last played ply; default is the game's final played ply.",
    )
    diagnose.add_argument(
        "--policy",
        required=True,
        help="JSON file matching the qualified M4 SelectionPolicy fields.",
    )
    diagnose.add_argument(
        "--engine", required=True, help="External UCI engine executable or PATH name."
    )
    limits = diagnose.add_mutually_exclusive_group()
    limits.add_argument(
        "--depth", type=_positive, default=12, help="Search depth; default 12."
    )
    limits.add_argument("--nodes", type=_positive, help="Node search limit.")
    limits.add_argument(
        "--movetime-ms", type=_positive, help="Engine search time in milliseconds."
    )
    diagnose.add_argument(
        "--multipv", type=_positive, default=3, help="Requested MultiPV count."
    )
    diagnose.add_argument(
        "--timeout-ms",
        type=_positive,
        default=10_000,
        help="Supervisor timeout in milliseconds for each analysis.",
    )
    diagnose.add_argument(
        "--engine-option",
        action="append",
        type=_engine_option,
        default=[],
        metavar="NAME=VALUE",
        help="Repeatable UCI option; MultiPV is controlled separately.",
    )
    diagnose.set_defaults(handler=_cmd_diagnose)
