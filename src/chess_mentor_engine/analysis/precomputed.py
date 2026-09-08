"""Fixture-backed provider used to prove the M3 contract before UCI integration."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from chess_mentor_engine.chess import CanonicalPosition, canonical_json

from .fingerprints import (
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from .model import (
    AnalysisFailure,
    AnalysisMetrics,
    AnalysisOutcome,
    AnalysisRequest,
    AnalysisStatus,
    AnalysisTermination,
    CandidateLine,
    EngineProvenance,
    FailureCode,
    PositionAnalysis,
)
from .validation import expected_candidate_count, validate_candidate_lines


def _fixture_key(fen: str, request: AnalysisRequest) -> str:
    return canonical_json({"fen": fen, "request": request.to_dict()})


@dataclass(frozen=True, slots=True)
class PrecomputedFixture:
    fen: str
    request: AnalysisRequest
    status: AnalysisStatus | None = None
    lines: tuple[CandidateLine, ...] = ()
    metrics: AnalysisMetrics = field(default_factory=AnalysisMetrics)
    termination: AnalysisTermination = field(
        default_factory=lambda: AnalysisTermination("completed")
    )
    failure_code: FailureCode | None = None
    failure_message: str | None = None

    def __post_init__(self) -> None:
        has_result = self.status is not None
        has_failure = self.failure_code is not None
        if has_result == has_failure:
            raise ValueError("fixture must define exactly one result or failure")
        if has_failure and self.lines:
            raise ValueError("failure fixture must not contain candidate lines")
        if has_failure and not self.failure_message:
            raise ValueError("failure fixture must include failure_message")
        if self.status == "terminal":
            if self.lines:
                raise ValueError("terminal fixture must not contain candidate lines")
            if self.termination.reason != "terminal_position":
                raise ValueError(
                    "terminal fixture must use terminal_position termination"
                )


class PrecomputedAnalysisProvider:
    """Return frozen normalized analysis fixtures through the M3 provider boundary."""

    def __init__(
        self,
        *,
        provenance: EngineProvenance,
        fixtures: tuple[PrecomputedFixture, ...],
    ) -> None:
        self.provenance = provenance
        fixture_map: dict[str, PrecomputedFixture] = {}
        for fixture in fixtures:
            key = _fixture_key(fixture.fen, fixture.request)
            if key in fixture_map:
                raise ValueError("duplicate precomputed fixture for FEN and request")
            fixture_map[key] = fixture
        self._fixtures = fixture_map

    def analyze(
        self, position: CanonicalPosition, request: AnalysisRequest
    ) -> AnalysisOutcome:
        request_fingerprint = analysis_request_fingerprint(
            fen=position.fen,
            request=request,
            provenance=self.provenance,
        )
        fixture = self._fixtures.get(_fixture_key(position.fen, request))
        if fixture is None:
            return AnalysisFailure(
                position_id=position.position_id,
                fen=position.fen,
                request_fingerprint=request_fingerprint,
                code="UNSUPPORTED_REQUEST",
                message="no precomputed fixture matches this FEN and request",
            )
        if fixture.failure_code is not None:
            return AnalysisFailure(
                position_id=position.position_id,
                fen=position.fen,
                request_fingerprint=request_fingerprint,
                code=fixture.failure_code,
                message=fixture.failure_message or "precomputed analysis failure",
            )

        assert fixture.status is not None
        self._validate_result_fixture(position.fen, request, fixture)
        analysis = PositionAnalysis(
            position_id=position.position_id,
            fen=position.fen,
            request_fingerprint=request_fingerprint,
            result_fingerprint="",
            status=fixture.status,
            request=request,
            provenance=self.provenance,
            lines=fixture.lines,
            metrics=fixture.metrics,
            termination=fixture.termination,
        )
        fingerprint = analysis_result_fingerprint(analysis)
        return replace(analysis, result_fingerprint=fingerprint)

    @staticmethod
    def _validate_result_fixture(
        fen: str,
        request: AnalysisRequest,
        fixture: PrecomputedFixture,
    ) -> None:
        expected_count = expected_candidate_count(fen, request.multipv)

        if fixture.status == "terminal":
            if expected_count:
                raise ValueError("terminal fixture source position has legal moves")
            return
        if expected_count == 0:
            raise ValueError("non-terminal fixture source position has no legal moves")
        if fixture.status == "complete" and len(fixture.lines) != expected_count:
            raise ValueError("complete fixture does not satisfy requested MultiPV")
        if fixture.status == "partial" and not fixture.lines:
            raise ValueError("partial fixture must retain at least one valid line")
        if len(fixture.lines) > expected_count:
            raise ValueError("fixture returns more candidate lines than requested")

        validate_candidate_lines(fen, fixture.lines)
