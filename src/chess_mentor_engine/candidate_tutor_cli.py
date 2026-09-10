"""M23 operator bridge from an exact M18 queue into persistent M8 tutoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from chess_mentor_engine.chess import ChessEvidenceError, canonical_json, ingest_pgn
from chess_mentor_engine.evidence import CaptureProtocol, PromptDefinition
from chess_mentor_engine.selection import (
    BatchExclusion,
    DecisionProvenance,
    DiagnosticCandidate,
    DiagnosticCandidateBatch,
    QuotaOutcome,
    SelectionEvidenceRef,
    SelectionPolicyIdentity,
    SelectionSignal,
)
from chess_mentor_engine.storage import (
    ArtifactWrite,
    LocalArtifactStore,
    StorageError,
    load_tutor_session,
    prepare_artifact,
    replay_tutor_session,
)
from chess_mentor_engine.storage.codec import decode_record, encode_record
from chess_mentor_engine.storage.tutor import PROMPT_KIND, SESSION_KIND
from chess_mentor_engine.tutoring import (
    CandidateTutorOrchestrationError,
    record_candidate_tutor_authorization,
    start_candidate_tutor_session,
)

M18_QUEUE_KIND = "m18.diagnostic-analysis-queue.v1"
M21_AUTH_KIND = "m21.candidate-tutor-authorization.v1"
M21_LAUNCH_KIND = "m21.candidate-tutor-launch.v1"
M23_SCHEMA_VERSION = "m23.diagnostic-to-persistent-tutor.v1"

_QUEUE_KEYS = {
    "schema_version", "source", "analysis_request", "selection_policy",
    "policy_fingerprint", "analysis_summary", "source_pool", "batch",
}
_SOURCE_KEYS = {
    "source_sha256", "game_id", "game_index", "start_ply", "end_ply",
    "position_count",
}
_SOURCE_POOL_KEYS = {
    "ply_index", "position_id", "side_to_move", "played_move_uci",
    "root_analysis", "played_child_analysis", "decision_comparison", "signals",
    "selection",
}


class CandidateTutorCliError(ValueError):
    """The M23 operator workflow cannot preserve its source boundaries."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _json_file(path_value: str) -> Any:
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        raise CandidateTutorCliError(f"JSON file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise CandidateTutorCliError(f"{label} shape mismatch")
    return value


def _selection_evidence(value: Any) -> SelectionEvidenceRef:
    data = _strict(value, {"source", "ref_id", "fingerprint"}, "selection evidence")
    if data["source"] not in {
        "decision_comparison", "position_features", "root_analysis"
    }:
        raise CandidateTutorCliError("selection evidence source is invalid")
    return SelectionEvidenceRef(**data)


def _signal(value: Any) -> SelectionSignal:
    data = _strict(
        value,
        {
            "signal_id", "kind", "position_id", "game_id", "comparison_id",
            "schema_version", "raw_value", "evidence", "detail",
        },
        "selection signal",
    )
    if type(data["evidence"]) is not list:
        raise CandidateTutorCliError("selection signal evidence must be an array")
    return SelectionSignal(
        signal_id=data["signal_id"],
        kind=data["kind"],
        position_id=data["position_id"],
        game_id=data["game_id"],
        comparison_id=data["comparison_id"],
        schema_version=data["schema_version"],
        raw_value=json.loads(canonical_json(data["raw_value"])),
        evidence=tuple(_selection_evidence(item) for item in data["evidence"]),
        detail=data["detail"],
    )


def _candidate(value: Any) -> DiagnosticCandidate:
    data = _strict(
        value,
        {
            "candidate_id", "position_id", "game_id", "comparison_id",
            "selection_policy", "signals", "eligibility_signal_ids", "provenance",
        },
        "diagnostic candidate",
    )
    policy = _strict(data["selection_policy"], {"policy_id", "version"}, "policy")
    provenance = _strict(
        data["provenance"],
        {
            "source_sha256", "game_semantic_fingerprint", "root_ply_index",
            "played_move_index", "child_position_id",
        },
        "candidate provenance",
    )
    return DiagnosticCandidate(
        candidate_id=data["candidate_id"],
        position_id=data["position_id"],
        game_id=data["game_id"],
        comparison_id=data["comparison_id"],
        selection_policy=SelectionPolicyIdentity(**policy),
        signals=tuple(_signal(item) for item in data["signals"]),
        eligibility_signal_ids=tuple(data["eligibility_signal_ids"]),
        provenance=DecisionProvenance(**provenance),
    )


def _batch(value: Any) -> DiagnosticCandidateBatch:
    keys = {
        "batch_id", "selection_policy", "policy_fingerprint", "requested_size",
        "actual_size", "candidates", "control_candidate_ids", "source_pool_count",
        "source_candidate_ids", "source_pool_fingerprint", "quota_outcomes",
        "exclusions", "shortfall", "control_shortfall",
    }
    data = _strict(value, keys, "diagnostic batch")
    policy = _strict(data["selection_policy"], {"policy_id", "version"}, "batch policy")
    quotas = tuple(
        QuotaOutcome(**_strict(
            item,
            {"signal_kind", "minimum", "maximum", "selected_count", "shortfall"},
            "quota outcome",
        ))
        for item in data["quota_outcomes"]
    )
    exclusions = tuple(
        BatchExclusion(
            position_id=item["position_id"],
            game_id=item["game_id"],
            comparison_id=item["comparison_id"],
            reasons=tuple(item["reasons"]),
        )
        for item in data["exclusions"]
    )
    return DiagnosticCandidateBatch(
        batch_id=data["batch_id"],
        selection_policy=SelectionPolicyIdentity(**policy),
        policy_fingerprint=data["policy_fingerprint"],
        requested_size=data["requested_size"],
        actual_size=data["actual_size"],
        candidates=tuple(_candidate(item) for item in data["candidates"]),
        control_candidate_ids=tuple(data["control_candidate_ids"]),
        source_pool_count=data["source_pool_count"],
        source_candidate_ids=tuple(data["source_candidate_ids"]),
        source_pool_fingerprint=data["source_pool_fingerprint"],
        quota_outcomes=quotas,
        exclusions=exclusions,
        shortfall=data["shortfall"],
        control_shortfall=data["control_shortfall"],
    )


def _selection_key(value: dict[str, Any]) -> tuple[str, int, str]:
    candidate = value.get("candidate")
    decision = value.get("decision")
    if type(decision) is not dict:
        raise CandidateTutorCliError("source_pool selection decision is invalid")
    if candidate is None:
        return decision["game_id"], 10**9, decision["comparison_id"]
    if type(candidate) is not dict or type(candidate.get("provenance")) is not dict:
        raise CandidateTutorCliError("source_pool candidate is invalid")
    return (
        candidate["game_id"],
        candidate["provenance"]["root_ply_index"],
        candidate["candidate_id"],
    )


def _validate_queue(
    value: Any,
) -> tuple[dict[str, Any], dict[str, Any], DiagnosticCandidateBatch]:
    queue = _strict(value, _QUEUE_KEYS, "M18 queue")
    if queue["schema_version"] != M18_QUEUE_KIND:
        raise CandidateTutorCliError("M18 queue schema mismatch")
    source = _strict(queue["source"], _SOURCE_KEYS, "M18 source")
    if type(source["position_count"]) is not int or source["position_count"] <= 0:
        raise CandidateTutorCliError("M18 source position_count is invalid")
    if source["position_count"] != source["end_ply"] - source["start_ply"] + 1:
        raise CandidateTutorCliError("M18 source window is inconsistent")
    if type(queue["selection_policy"]) is not dict:
        raise CandidateTutorCliError("M18 selection_policy must be an object")
    policy_fp = _fingerprint(queue["selection_policy"])
    if queue["policy_fingerprint"] != policy_fp:
        raise CandidateTutorCliError("M18 selection policy fingerprint mismatch")

    batch = _batch(queue["batch"])
    policy = queue["selection_policy"]
    if batch.selection_policy.to_dict() != {
        "policy_id": policy.get("policy_id"), "version": policy.get("version")
    }:
        raise CandidateTutorCliError("M18 queue/batch policy identity mismatch")
    if batch.policy_fingerprint != policy_fp:
        raise CandidateTutorCliError("M18 queue/batch policy fingerprint mismatch")
    if batch.requested_size != policy.get("requested_size"):
        raise CandidateTutorCliError("M18 queue/batch requested_size mismatch")

    pool = queue["source_pool"]
    if type(pool) is not list or len(pool) != source["position_count"]:
        raise CandidateTutorCliError("M18 source_pool count mismatch")
    if len(pool) != batch.source_pool_count:
        raise CandidateTutorCliError("M18 source_pool/batch count mismatch")
    selections = []
    for index, raw in enumerate(pool):
        entry = _strict(raw, _SOURCE_POOL_KEYS, f"source_pool[{index}]")
        if type(entry["selection"]) is not dict:
            raise CandidateTutorCliError("source_pool selection payload is invalid")
        selections.append(entry["selection"])
    ordered = sorted(selections, key=_selection_key)
    if _fingerprint(ordered) != batch.source_pool_fingerprint:
        raise CandidateTutorCliError("M18 source_pool selection payloads drifted")
    source_candidates = [item["candidate"] for item in ordered if item["candidate"]]
    source_candidate_ids = tuple(item["candidate_id"] for item in source_candidates)
    if source_candidate_ids != batch.source_candidate_ids:
        raise CandidateTutorCliError("M18 source candidate identities drifted")
    by_id = {item["candidate_id"]: item for item in source_candidates}
    for raw_candidate in queue["batch"]["candidates"]:
        candidate_id = raw_candidate["candidate_id"]
        if by_id.get(candidate_id) != raw_candidate:
            raise CandidateTutorCliError(
                "diagnostic batch candidate content drifted from source_pool"
            )
    return queue, source, batch


def _selected(
    candidate_id: str, batch: DiagnosticCandidateBatch
) -> DiagnosticCandidate:
    matches = tuple(
        item for item in batch.candidates if item.candidate_id == candidate_id
    )
    if len(matches) != 1:
        raise CandidateTutorCliError(
            "candidate_id must identify exactly one selected M18 batch candidate"
        )
    return matches[0]


def _records(path_value: str, schema: type[Any]) -> tuple[Any, ...]:
    value = _json_file(path_value)
    if type(value) is not list:
        raise CandidateTutorCliError("prompt definitions must be a JSON array")
    return tuple(decode_record(item, schema) for item in value)


def _build_writes(
    participant: str, queue: dict[str, Any], authorization, launch, session, prompts
):
    replay_tutor_session(session, prompts=prompts)
    queue_write = ArtifactWrite(
        M18_QUEUE_KIND,
        f"diagnostic_queue_{_fingerprint(queue)[:20]}",
        participant,
        queue,
    )
    queue_ref = prepare_artifact(queue_write)[0]
    auth_write = ArtifactWrite(
        M21_AUTH_KIND, authorization.authorization_id, participant,
        authorization.to_dict(), (queue_ref,),
    )
    auth_ref = prepare_artifact(auth_write)[0]
    launch_write = ArtifactWrite(
        M21_LAUNCH_KIND, launch["launch_id"], participant, launch, (auth_ref,),
    )
    launch_ref = prepare_artifact(launch_write)[0]
    prompt_writes = tuple(
        ArtifactWrite(
            PROMPT_KIND, prompt.prompt_definition_id, participant,
            {"codec_version": 1, "prompt": encode_record(prompt)},
        )
        for prompt in sorted(prompts, key=lambda item: item.prompt_definition_id)
    )
    prompt_refs = tuple(prepare_artifact(item)[0] for item in prompt_writes)
    session_write = ArtifactWrite(
        SESSION_KIND,
        f"{session.tutor_session_id}:{session.snapshot_fingerprint}",
        participant,
        {"codec_version": 1, "session": encode_record(session)},
        prompt_refs + (launch_ref,),
    )
    return (queue_write, auth_write, launch_write) + prompt_writes + (session_write,), (
        queue_ref, auth_ref, launch_ref,
    )


def _store(path_value: str, create_db: bool) -> tuple[LocalArtifactStore, bool]:
    path = Path(path_value).expanduser()
    if path.exists():
        if not path.is_file():
            raise CandidateTutorCliError("artifact database path is not a file")
        return LocalArtifactStore(path), False
    if not create_db:
        raise CandidateTutorCliError(
            "artifact database does not exist; pass --create-db to create it explicitly"
        )
    return LocalArtifactStore(path), True


def _run(args: argparse.Namespace) -> dict[str, Any]:
    queue, source, batch = _validate_queue(_json_file(args.diagnostic_json))
    candidate = _selected(args.candidate_id, batch)
    pgn_path = Path(args.pgn).expanduser()
    if not pgn_path.exists() or not pgn_path.is_file():
        raise CandidateTutorCliError("PGN file does not exist")
    ingested = ingest_pgn(pgn_path.read_bytes())
    if ingested.source_sha256 != source["source_sha256"]:
        raise CandidateTutorCliError("PGN source does not match M18 queue source hash")
    game_index = source["game_index"]
    if (
        type(game_index) is not int
        or game_index < 0
        or game_index >= len(ingested.games)
    ):
        raise CandidateTutorCliError("M18 queue game_index is outside supplied PGN")
    game = ingested.games[game_index]
    if game.game_id != source["game_id"] or candidate.game_id != game.game_id:
        raise CandidateTutorCliError("selected candidate does not match M18 game")
    ply = candidate.provenance.root_ply_index
    if (
        ply < source["start_ply"]
        or ply > source["end_ply"]
        or ply >= len(game.positions)
    ):
        raise CandidateTutorCliError(
            "selected candidate lies outside M18 source window"
        )

    protocol_value = _json_file(args.protocol_json)
    if type(protocol_value) is not dict:
        raise CandidateTutorCliError("capture protocol must be a JSON object")
    protocol = decode_record(protocol_value, CaptureProtocol)
    prompts = _records(args.prompts_json, PromptDefinition)
    authorization = record_candidate_tutor_authorization(
        participant_id=args.participant,
        candidate=candidate,
        batch=batch,
        selection_decision=args.selection_decision,
        capture_consent=args.capture_consent,
        recorded_at=args.recorded_at,
    )
    context, session, launch = start_candidate_tutor_session(
        authorization=authorization,
        candidate=candidate,
        batch=batch,
        game=game,
        position=game.positions[ply],
        capture_protocol=protocol,
        created_at=args.created_at,
    )
    writes, lineage = _build_writes(
        args.participant, queue, authorization, launch, session, prompts
    )
    store, created = _store(args.db, args.create_db)
    refs = store.put_many(writes)
    session_ref = refs[-1]
    recovered = load_tutor_session(store, session_ref, participant_id=args.participant)
    if recovered.session.snapshot_fingerprint != session.snapshot_fingerprint:
        raise CandidateTutorCliError("persisted tutor session replay mismatch")
    queue_ref, auth_ref, launch_ref = lineage
    return {
        "schema_version": M23_SCHEMA_VERSION,
        "participant_id": args.participant,
        "candidate_id": candidate.candidate_id,
        "batch_id": batch.batch_id,
        "player_decision_context_id": context.context_id,
        "authorization_id": authorization.authorization_id,
        "launch_id": launch["launch_id"],
        "tutor_session_id": session.tutor_session_id,
        "state": session.state,
        "snapshot_fingerprint": session.snapshot_fingerprint,
        "verified_replay": True,
        "created_db": created,
        "diagnostic_queue_ref": queue_ref.to_dict(),
        "authorization_ref": auth_ref.to_dict(),
        "launch_ref": launch_ref.to_dict(),
        "ref": session_ref.to_dict(),
        "next_action": "continue with cme tutor present-position using ref.artifact_id",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cme-candidate-tutor", allow_abbrev=False)
    parser.add_argument("pgn")
    parser.add_argument("--diagnostic-json", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--participant", required=True)
    parser.add_argument("--protocol-json", required=True)
    parser.add_argument("--prompts-json", required=True)
    parser.add_argument(
        "--selection-decision", required=True, choices=("selected", "declined")
    )
    parser.add_argument(
        "--capture-consent", required=True, choices=("granted", "declined")
    )
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--create-db", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = _run(args)
    except (
        CandidateTutorCliError,
        CandidateTutorOrchestrationError,
        ChessEvidenceError,
        StorageError,
        json.JSONDecodeError,
        OSError,
        UnicodeError,
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
