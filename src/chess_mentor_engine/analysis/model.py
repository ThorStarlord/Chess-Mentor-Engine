"""Immutable normalized records for M3 engine evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

ScoreBound: TypeAlias = Literal["exact", "lower", "upper"]
AnalysisStatus: TypeAlias = Literal["complete", "partial", "terminal"]
TerminationReason: TypeAlias = Literal[
    "completed",
    "terminal_position",
    "timeout",
    "cancelled",
    "engine_crash",
    "protocol_error",
]
FailureCode: TypeAlias = Literal[
    "ENGINE_NOT_FOUND",
    "ENGINE_START_FAILED",
    "ENGINE_CRASHED",
    "ANALYSIS_TIMEOUT",
    "PROTOCOL_ERROR",
    "INVALID_ENGINE_OUTPUT",
    "UNSUPPORTED_REQUEST",
    "CANCELLED",
]


def _require_positive(name: str, value: int) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_non_negative(name: str, value: int | None) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{name} must be non-negative when provided")


@dataclass(frozen=True, slots=True)
class AnalysisLimit:
    kind: Literal["depth", "nodes", "movetime_ms"]
    value: int

    def __post_init__(self) -> None:
        if self.kind not in {"depth", "nodes", "movetime_ms"}:
            raise ValueError(f"unsupported analysis limit kind: {self.kind!r}")
        _require_positive("analysis limit", self.value)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "value": self.value}


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    multipv: int
    search_limit: AnalysisLimit
    supervisor_timeout_ms: int | None = None

    def __post_init__(self) -> None:
        _require_positive("multipv", self.multipv)
        if self.supervisor_timeout_ms is not None:
            _require_positive("supervisor_timeout_ms", self.supervisor_timeout_ms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "multipv": self.multipv,
            "search_limit": self.search_limit.to_dict(),
            "supervisor_timeout_ms": self.supervisor_timeout_ms,
        }


@dataclass(frozen=True, slots=True)
class EngineArtifact:
    name: str
    sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("engine artifact name must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class EngineProvenance:
    provider_name: str
    provider_version: str
    protocol: str
    engine_name: str
    engine_version: str | None = None
    engine_author: str | None = None
    binary_sha256: str | None = None
    engine_options: tuple[tuple[str, str], ...] = ()
    engine_artifacts: tuple[EngineArtifact, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("provider_name", self.provider_name),
            ("provider_version", self.provider_version),
            ("protocol", self.protocol),
            ("engine_name", self.engine_name),
        ):
            if not value:
                raise ValueError(f"{name} must not be empty")
        options = tuple(sorted(self.engine_options, key=lambda item: item[0]))
        artifacts = tuple(sorted(self.engine_artifacts, key=lambda item: item.name))
        object.__setattr__(self, "engine_options", options)
        object.__setattr__(self, "engine_artifacts", artifacts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "provider_version": self.provider_version,
            "protocol": self.protocol,
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "engine_author": self.engine_author,
            "binary_sha256": self.binary_sha256,
            "engine_options": [[key, value] for key, value in self.engine_options],
            "engine_artifacts": [item.to_dict() for item in self.engine_artifacts],
        }


@dataclass(frozen=True, slots=True)
class CentipawnEvaluation:
    centipawns: int
    bound: ScoreBound = "exact"

    def __post_init__(self) -> None:
        if self.bound not in {"exact", "lower", "upper"}:
            raise ValueError(f"invalid score bound: {self.bound!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "centipawn",
            "perspective": "white",
            "centipawns": self.centipawns,
            "bound": self.bound,
        }


@dataclass(frozen=True, slots=True)
class MateEvaluation:
    winner: Literal["white", "black"]
    plies_to_mate: int
    bound: ScoreBound = "exact"

    def __post_init__(self) -> None:
        if self.winner not in {"white", "black"}:
            raise ValueError(f"invalid mate winner: {self.winner!r}")
        _require_non_negative("plies_to_mate", self.plies_to_mate)
        if self.bound not in {"exact", "lower", "upper"}:
            raise ValueError(f"invalid score bound: {self.bound!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "mate",
            "perspective": "white",
            "winner": self.winner,
            "plies_to_mate": self.plies_to_mate,
            "bound": self.bound,
        }


Evaluation: TypeAlias = CentipawnEvaluation | MateEvaluation


@dataclass(frozen=True, slots=True)
class CandidateLine:
    rank: int
    root_move_uci: str
    evaluation: Evaluation
    pv_uci: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_positive("candidate rank", self.rank)
        if not self.root_move_uci:
            raise ValueError("root_move_uci must not be empty")
        if self.pv_uci and self.pv_uci[0] != self.root_move_uci:
            raise ValueError("a non-empty PV must begin with root_move_uci")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "root_move_uci": self.root_move_uci,
            "evaluation": self.evaluation.to_dict(),
            "pv_uci": list(self.pv_uci),
        }


@dataclass(frozen=True, slots=True)
class AnalysisMetrics:
    depth: int | None = None
    seldepth: int | None = None
    nodes: int | None = None
    time_ms: int | None = None
    nps: int | None = None
    hashfull_per_mille: int | None = None
    tablebase_hits: int | None = None

    def __post_init__(self) -> None:
        for name in (
            "depth",
            "seldepth",
            "nodes",
            "time_ms",
            "nps",
            "hashfull_per_mille",
            "tablebase_hits",
        ):
            _require_non_negative(name, getattr(self, name))
        if self.hashfull_per_mille is not None and self.hashfull_per_mille > 1000:
            raise ValueError("hashfull_per_mille must not exceed 1000")

    def to_dict(self) -> dict[str, Any]:
        return {
            "depth": self.depth,
            "seldepth": self.seldepth,
            "nodes": self.nodes,
            "time_ms": self.time_ms,
            "nps": self.nps,
            "hashfull_per_mille": self.hashfull_per_mille,
            "tablebase_hits": self.tablebase_hits,
        }


@dataclass(frozen=True, slots=True)
class AnalysisTermination:
    reason: TerminationReason
    detail: str | None = None

    def __post_init__(self) -> None:
        allowed = {
            "completed",
            "terminal_position",
            "timeout",
            "cancelled",
            "engine_crash",
            "protocol_error",
        }
        if self.reason not in allowed:
            raise ValueError(f"invalid termination reason: {self.reason!r}")

    def to_dict(self) -> dict[str, Any]:
        return {"reason": self.reason, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class PositionAnalysis:
    position_id: str
    fen: str
    request_fingerprint: str
    result_fingerprint: str
    status: AnalysisStatus
    request: AnalysisRequest
    provenance: EngineProvenance
    lines: tuple[CandidateLine, ...]
    metrics: AnalysisMetrics
    termination: AnalysisTermination

    def __post_init__(self) -> None:
        if self.status not in {"complete", "partial", "terminal"}:
            raise ValueError(f"invalid analysis status: {self.status!r}")
        if self.status == "terminal" and self.lines:
            raise ValueError("terminal analysis must not contain candidate lines")
        expected = tuple(range(1, len(self.lines) + 1))
        actual = tuple(line.rank for line in self.lines)
        if actual != expected:
            raise ValueError("candidate ranks must be contiguous starting at 1")

    @property
    def best_move(self) -> str | None:
        return self.lines[0].root_move_uci if self.lines else None

    def to_dict(self, *, include_result_fingerprint: bool = True) -> dict[str, Any]:
        payload = {
            "position_id": self.position_id,
            "fen": self.fen,
            "request_fingerprint": self.request_fingerprint,
            "status": self.status,
            "request": self.request.to_dict(),
            "provenance": self.provenance.to_dict(),
            "lines": [line.to_dict() for line in self.lines],
            "metrics": self.metrics.to_dict(),
            "termination": self.termination.to_dict(),
        }
        if include_result_fingerprint:
            payload["result_fingerprint"] = self.result_fingerprint
        return payload


@dataclass(frozen=True, slots=True)
class AnalysisFailure:
    position_id: str
    fen: str
    request_fingerprint: str
    code: FailureCode
    message: str

    def __post_init__(self) -> None:
        allowed = {
            "ENGINE_NOT_FOUND",
            "ENGINE_START_FAILED",
            "ENGINE_CRASHED",
            "ANALYSIS_TIMEOUT",
            "PROTOCOL_ERROR",
            "INVALID_ENGINE_OUTPUT",
            "UNSUPPORTED_REQUEST",
            "CANCELLED",
        }
        if self.code not in allowed:
            raise ValueError(f"invalid analysis failure code: {self.code!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "fen": self.fen,
            "request_fingerprint": self.request_fingerprint,
            "code": self.code,
            "message": self.message,
        }


AnalysisOutcome: TypeAlias = PositionAnalysis | AnalysisFailure
