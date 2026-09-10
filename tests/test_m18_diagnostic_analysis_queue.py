"""M18 diagnostic move-analysis queue qualification and rejection coverage."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import chess_mentor_engine.diagnostic_cli as diagnostic_module
from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.cli import main

GAME_PGN = """[Event "M18 fixture"]
[White "Ada"]
[Black "Grace"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 *
"""

SHORT_PGN = """[Event "M18 short fixture"]
[White "Ada"]
[Black "Grace"]
[Result "*"]

1. e4 e5 *
"""


def _pgn(tmp_path: Path, text: str = GAME_PGN) -> Path:
    path = tmp_path / "game.pgn"
    path.write_text(text, encoding="utf-8")
    return path


def _game(text: str = GAME_PGN):
    return ingest_pgn(text.encode("utf-8")).games[0]


def _invoke(capsys, *argv: str):
    code = main(argv)
    captured = capsys.readouterr()
    payload = json.loads(captured.out) if captured.out else None
    return code, payload, captured.err


def _write_policy(tmp_path: Path, **overrides) -> Path:
    payload = {
        "policy_id": "m18-cli-balanced",
        "version": "1",
        "requested_size": 3,
        "candidate_min_cp_delta": 25,
        "control_max_cp_delta": 0,
        "close_choice_max_cp": None,
        "candidate_mate_relations": [],
        "include_rank1_controls": True,
        "excluded_signal_kinds": ["ENGINE_EVIDENCE_INVERSION"],
        "minimum_controls": 1,
        "maximum_per_game": None,
        "quotas": [
            {
                "signal_kind": "PLAYED_EQUALS_RANK_1",
                "minimum": 1,
                "maximum": 2,
            }
        ],
    }
    payload.update(overrides)
    path = tmp_path / "selection-policy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_fake_engine(
    tmp_path: Path,
    plans: dict[str, tuple[tuple[str, ...], str | None]],
    *,
    identities: tuple[str, ...] = ("FakeFish 1.0",),
) -> str:
    path = tmp_path / "fake-uci-engine"
    counter = tmp_path / "engine-counter.txt"
    script = f'''#!/usr/bin/env python3
from pathlib import Path
import sys

PLANS = {plans!r}
IDENTITIES = {identities!r}
COUNTER = Path({str(counter)!r})
current_fen = None

for raw in sys.stdin:
    command = raw.strip()
    if command == "uci":
        try:
            index = int(COUNTER.read_text())
        except (FileNotFoundError, ValueError):
            index = 0
        COUNTER.write_text(str(index + 1))
        identity = IDENTITIES[min(index, len(IDENTITIES) - 1)]
        print("id name " + identity, flush=True)
        print("id author Chess Mentor Tests", flush=True)
        print("option name MultiPV type spin default 1 min 1 max 8", flush=True)
        print("uciok", flush=True)
    elif command == "isready":
        print("readyok", flush=True)
    elif command.startswith("position fen "):
        current_fen = command[len("position fen "):]
    elif command.startswith("go "):
        info_lines, bestmove = PLANS.get(current_fen, ((), None))
        for item in info_lines:
            print(item, flush=True)
        if bestmove is not None:
            print("bestmove " + bestmove, flush=True)
    elif command == "quit":
        break
'''
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def _balanced_plans(game) -> dict[str, tuple[tuple[str, ...], str | None]]:
    return {
        game.positions[0].fen: (
            (
                "info depth 8 multipv 1 score cp 40 pv d2d4",
                "info depth 8 multipv 2 score cp 10 pv e2e4",
            ),
            "d2d4",
        ),
        game.positions[1].fen: (
            (
                "info depth 8 multipv 1 score cp 10 pv e7e5",
                "info depth 8 multipv 2 score cp 0 pv c7c5",
            ),
            "e7e5",
        ),
        game.positions[2].fen: (
            (
                "info depth 8 multipv 1 score cp 25 pv g1f3",
                "info depth 8 multipv 2 score cp 5 pv f1c4",
            ),
            "g1f3",
        ),
        game.positions[3].fen: (
            (
                "info depth 8 multipv 1 score cp 50 pv g8f6",
                "info depth 8 multipv 2 score cp 20 pv b8c6",
            ),
            "g8f6",
        ),
    }


def _argv(
    pgn: Path,
    policy: Path,
    engine: str,
    *,
    start_ply: int = 0,
    end_ply: int | None = 3,
    multipv: int = 2,
) -> tuple[str, ...]:
    values = [
        "diagnose",
        str(pgn),
        "--policy",
        str(policy),
        "--engine",
        engine,
        "--start-ply",
        str(start_ply),
        "--depth",
        "8",
        "--multipv",
        str(multipv),
    ]
    if end_ply is not None:
        values.extend(("--end-ply", str(end_ply)))
    return tuple(values)


def test_diagnose_builds_deterministic_candidate_control_queue(
    tmp_path, capsys
) -> None:
    pgn = _pgn(tmp_path)
    game = _game()
    policy = _write_policy(tmp_path)
    engine = _write_fake_engine(tmp_path, _balanced_plans(game))

    first = _invoke(capsys, *_argv(pgn, policy, engine))
    second = _invoke(capsys, *_argv(pgn, policy, engine))

    assert first[0] == second[0] == 0
    assert first[2] == second[2] == ""
    payload = first[1]
    repeated = second[1]
    assert payload["schema_version"] == "m18.diagnostic-analysis-queue.v1"
    assert payload["source"]["start_ply"] == 0
    assert payload["source"]["end_ply"] == 3
    assert payload["source"]["position_count"] == 4
    assert payload["analysis_summary"] == {
        "root_failure_count": 0,
        "partial_root_count": 0,
        "incompatible_comparison_count": 0,
    }
    roles = [
        item["selection"]["decision"]["role"]
        for item in payload["source_pool"]
    ]
    assert roles == [
        "candidate",
        "control",
        "control",
        "candidate",
    ]

    batch = payload["batch"]
    assert batch["actual_size"] == 3
    assert batch["shortfall"] == 0
    assert len(batch["control_candidate_ids"]) == 2
    assert batch["policy_fingerprint"] == payload["policy_fingerprint"]
    assert batch["quota_outcomes"] == [
        {
            "signal_kind": "PLAYED_EQUALS_RANK_1",
            "minimum": 1,
            "maximum": 2,
            "selected_count": 2,
            "shortfall": 0,
        }
    ]
    assert [item["provenance"]["root_ply_index"] for item in batch["candidates"]] == [
        1,
        0,
        2,
    ]
    assert batch["batch_id"] == repeated["batch"]["batch_id"]
    assert batch["source_pool_fingerprint"] == repeated["batch"][
        "source_pool_fingerprint"
    ]


def test_diagnose_respects_inclusive_bounded_ply_window(tmp_path, capsys) -> None:
    pgn = _pgn(tmp_path)
    game = _game()
    policy = _write_policy(tmp_path, requested_size=2, minimum_controls=1, quotas=[])
    engine = _write_fake_engine(tmp_path, _balanced_plans(game))

    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, policy, engine, start_ply=1, end_ply=2),
    )

    assert code == 0 and error == ""
    assert payload["source"]["position_count"] == 2
    assert [item["ply_index"] for item in payload["source_pool"]] == [1, 2]
    assert payload["batch"]["source_pool_count"] == 2
    assert payload["batch"]["actual_size"] == 2


def test_partial_root_stays_explicitly_excluded_and_shortfall_is_preserved(
    tmp_path, capsys
) -> None:
    pgn = _pgn(tmp_path, SHORT_PGN)
    game = _game(SHORT_PGN)
    policy = _write_policy(
        tmp_path,
        requested_size=1,
        candidate_min_cp_delta=1,
        minimum_controls=0,
        quotas=[],
    )
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[0].fen: (
                ("info depth 8 multipv 1 score cp 40 pv d2d4",),
                "d2d4",
            )
        },
    )

    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, policy, engine, end_ply=0, multipv=2),
    )

    assert code == 0 and error == ""
    assert payload["analysis_summary"]["partial_root_count"] == 1
    entry = payload["source_pool"][0]
    assert entry["root_analysis"]["record"]["status"] == "partial"
    assert entry["decision_comparison"]["comparison_kind"] == "partial_evidence"
    assert entry["decision_comparison"]["exact_centipawn_delta_for_mover"] is None
    assert entry["selection"]["decision"]["role"] == "excluded"
    assert entry["selection"]["decision"]["exclusion_reasons"] == [
        "no_eligibility_rule_matched"
    ]
    assert payload["batch"]["actual_size"] == 0
    assert payload["batch"]["shortfall"] == 1


def test_incompatible_child_reanalysis_is_not_promoted_to_candidate(
    tmp_path, capsys
) -> None:
    pgn = _pgn(tmp_path, SHORT_PGN)
    game = _game(SHORT_PGN)
    policy = _write_policy(
        tmp_path,
        requested_size=1,
        candidate_min_cp_delta=1,
        minimum_controls=0,
        quotas=[],
    )
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[0].fen: (
                ("info depth 8 score cp 40 pv d2d4",),
                "d2d4",
            ),
            game.positions[1].fen: (
                ("info depth 8 score cp 20 pv e7e5",),
                "e7e5",
            ),
        },
        identities=("FakeFish A", "FakeFish B"),
    )

    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, policy, engine, end_ply=0, multipv=1),
    )

    assert code == 0 and error == ""
    assert payload["analysis_summary"]["incompatible_comparison_count"] == 1
    entry = payload["source_pool"][0]
    assert entry["played_child_analysis"] is not None
    assert entry["decision_comparison"]["compatibility"] == "incompatible"
    assert entry["decision_comparison"]["comparison_kind"] == (
        "incompatible_analysis_regime"
    )
    assert entry["decision_comparison"]["exact_centipawn_delta_for_mover"] is None
    assert entry["selection"]["decision"]["role"] == "excluded"
    assert payload["batch"]["shortfall"] == 1


def test_root_analysis_failure_is_auditable_exclusion_not_fake_score(
    tmp_path, capsys
) -> None:
    pgn = _pgn(tmp_path, SHORT_PGN)
    game = _game(SHORT_PGN)
    policy = _write_policy(
        tmp_path,
        requested_size=1,
        candidate_min_cp_delta=1,
        minimum_controls=0,
        quotas=[],
    )
    engine = _write_fake_engine(
        tmp_path,
        {
            game.positions[0].fen: (
                ("info depth 8 multipv 0 score cp 20 pv e2e4",),
                "e2e4",
            )
        },
    )

    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, policy, engine, end_ply=0, multipv=1),
    )

    assert code == 0 and error == ""
    assert payload["analysis_summary"]["root_failure_count"] == 1
    entry = payload["source_pool"][0]
    assert entry["root_analysis"]["outcome_type"] == "analysis_failure"
    assert entry["root_analysis"]["record"]["code"] == "INVALID_ENGINE_OUTPUT"
    assert entry["decision_comparison"]["comparison_kind"] == "incomparable"
    assert entry["decision_comparison"]["best_evaluation"] is None
    assert entry["selection"]["decision"]["role"] == "excluded"
    assert payload["batch"]["actual_size"] == 0


def test_invalid_policy_and_invalid_range_fail_before_engine_execution(
    tmp_path, capsys
) -> None:
    pgn = _pgn(tmp_path)
    missing_engine = str(tmp_path / "missing-engine")

    bad_policy = _write_policy(tmp_path, typo_threshold=50)
    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, bad_policy, missing_engine, end_ply=0),
    )
    assert code == 2 and payload is None
    assert "unknown fields" in error

    bad_quota = _write_policy(
        tmp_path,
        quotas=[{"signal_kind": "NOT_A_SIGNAL", "minimum": 1}],
    )
    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, bad_quota, missing_engine, end_ply=0),
    )
    assert code == 2 and payload is None
    assert "unknown signal_kind" in error

    valid_policy = _write_policy(tmp_path)
    code, payload, error = _invoke(
        capsys,
        *_argv(
            pgn,
            valid_policy,
            missing_engine,
            start_ply=2,
            end_ply=1,
        ),
    )
    assert code == 2 and payload is None
    assert "end ply must be greater" in error


def test_batch_policy_fingerprint_drift_is_rejected_without_json(
    tmp_path, capsys, monkeypatch
) -> None:
    pgn = _pgn(tmp_path)
    game = _game()
    policy = _write_policy(tmp_path, requested_size=2, minimum_controls=0, quotas=[])
    engine = _write_fake_engine(tmp_path, _balanced_plans(game))
    native_apply = diagnostic_module.apply_selection_policy
    calls = 0

    def tampered_apply(**kwargs):
        nonlocal calls
        calls += 1
        result = native_apply(**kwargs)
        if calls == 2:
            return replace(
                result,
                decision=replace(
                    result.decision,
                    policy_fingerprint="tampered-policy-fingerprint",
                ),
            )
        return result

    monkeypatch.setattr(diagnostic_module, "apply_selection_policy", tampered_apply)

    code, payload, error = _invoke(
        capsys,
        *_argv(pgn, policy, engine, start_ply=0, end_ply=1),
    )

    assert code == 2 and payload is None
    assert "policy fingerprint mismatch" in error
