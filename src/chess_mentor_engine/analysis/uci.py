"""External UCI subprocess provider for normalized M3 engine evidence."""

from __future__ import annotations

import hashlib
import queue
import shutil
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path

from chess_mentor_engine.chess import CanonicalPosition
from chess_mentor_engine.chess._core import opposite

from .fingerprints import (
    analysis_request_fingerprint,
    analysis_result_fingerprint,
)
from .model import (
    AnalysisFailure,
    AnalysisMetrics,
    AnalysisOutcome,
    AnalysisRequest,
    AnalysisTermination,
    CandidateLine,
    CentipawnEvaluation,
    EngineProvenance,
    MateEvaluation,
    PositionAnalysis,
    ScoreBound,
)
from .validation import expected_candidate_count, validate_candidate_lines

UCI_PROVIDER_NAME = "uci-subprocess"
UCI_PROVIDER_VERSION = "0.2"


class _ReadTimeout(Exception):
    pass


class _EngineExited(Exception):
    pass


@dataclass(frozen=True, slots=True)
class _Handshake:
    engine_name: str
    engine_author: str | None
    advertised_options: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _ParsedInfo:
    rank: int
    line: CandidateLine
    metrics: AnalysisMetrics


class _UciSession:
    def __init__(self, executable: str) -> None:
        self.process = subprocess.Popen(
            [executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        assert self.process.stderr is not None
        self._stdout_queue: queue.Queue[str | None] = queue.Queue()
        self._stderr_lines: deque[str] = deque(maxlen=20)
        self._stdout_thread = threading.Thread(
            target=self._pump_stdout,
            daemon=True,
        )
        self._stderr_thread = threading.Thread(
            target=self._pump_stderr,
            daemon=True,
        )
        self._stdout_thread.start()
        self._stderr_thread.start()

    def _pump_stdout(self) -> None:
        assert self.process.stdout is not None
        try:
            for line in self.process.stdout:
                self._stdout_queue.put(line.rstrip("\r\n"))
        finally:
            self._stdout_queue.put(None)

    def _pump_stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            self._stderr_lines.append(line.rstrip("\r\n"))

    def send(self, command: str) -> None:
        if "\n" in command or "\r" in command:
            raise ValueError("UCI command must be a single line")
        if self.process.poll() is not None:
            raise _EngineExited(self.diagnostic())
        assert self.process.stdin is not None
        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
        except BrokenPipeError as exc:
            raise _EngineExited(self.diagnostic()) from exc

    def read_line(self, timeout_ms: int | None) -> str:
        try:
            if timeout_ms is None:
                item = self._stdout_queue.get()
            else:
                item = self._stdout_queue.get(timeout=max(timeout_ms, 1) / 1000)
        except queue.Empty as exc:
            raise _ReadTimeout from exc
        if item is None:
            raise _EngineExited(self.diagnostic())
        return item

    def diagnostic(self) -> str:
        code = self.process.poll()
        stderr = " | ".join(self._stderr_lines)
        detail = f"process exit code={code}"
        if stderr:
            detail += f"; stderr={stderr[:500]}"
        return detail

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        try:
            self.send("quit")
        except (_EngineExited, ValueError):
            pass
        try:
            self.process.wait(timeout=0.25)
            return
        except subprocess.TimeoutExpired:
            self.process.terminate()
        try:
            self.process.wait(timeout=0.25)
            return
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=0.25)


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_executable(executable: str) -> str | None:
    candidate = Path(executable).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    return shutil.which(executable)


def _parse_option_name(line: str) -> str | None:
    if not line.startswith("option name "):
        return None
    tokens = line.split()
    try:
        type_index = tokens.index("type", 2)
    except ValueError:
        return None
    name = " ".join(tokens[2:type_index]).strip()
    return name or None


def _parse_int_after(tokens: list[str], key: str) -> int | None:
    try:
        index = tokens.index(key)
    except ValueError:
        return None
    if index + 1 >= len(tokens):
        raise ValueError(f"missing integer after UCI field {key}")
    try:
        return int(tokens[index + 1])
    except ValueError as exc:
        raise ValueError(f"invalid integer after UCI field {key}") from exc


def _mate_from_uci(root_side: str, moves: int, bound: ScoreBound) -> MateEvaluation:
    if moves == 0:
        raise ValueError("non-terminal UCI mate score must not be zero")
    if moves > 0:
        winner = root_side
        plies_to_mate = 2 * moves - 1
    else:
        winner = opposite(root_side)
        plies_to_mate = 2 * abs(moves)
    return MateEvaluation(
        winner=winner,
        plies_to_mate=plies_to_mate,
        bound=bound,
    )


def _parse_info(line: str, root_side: str) -> _ParsedInfo | None:
    if not line.startswith("info "):
        return None
    tokens = line.split()
    if len(tokens) > 1 and tokens[1] == "string":
        return None
    if "score" not in tokens or "pv" not in tokens:
        return None

    score_index = tokens.index("score")
    if score_index + 2 >= len(tokens):
        raise ValueError("malformed UCI score field")
    score_kind = tokens[score_index + 1]
    try:
        raw_score = int(tokens[score_index + 2])
    except ValueError as exc:
        raise ValueError("malformed UCI score value") from exc

    lower = "lowerbound" in tokens[score_index + 3 :]
    upper = "upperbound" in tokens[score_index + 3 :]
    if lower and upper:
        raise ValueError("UCI score cannot be both lowerbound and upperbound")
    bound: ScoreBound = "lower" if lower else "upper" if upper else "exact"
    # Bounds describe evaluation ordering, not the numeric mate distance.
    # Changing from Black's perspective to White's reverses that ordering.
    if root_side == "black":
        if bound == "lower":
            bound = "upper"
        elif bound == "upper":
            bound = "lower"

    if score_kind == "cp":
        value = raw_score if root_side == "white" else -raw_score
        evaluation = CentipawnEvaluation(value, bound=bound)
    elif score_kind == "mate":
        evaluation = _mate_from_uci(root_side, raw_score, bound)
    else:
        raise ValueError(f"unsupported UCI score kind: {score_kind!r}")

    pv_index = tokens.index("pv")
    pv = tuple(tokens[pv_index + 1 :])
    if not pv:
        raise ValueError("UCI candidate info contains an empty PV")

    rank = _parse_int_after(tokens, "multipv")
    if rank is None:
        rank = 1
    if rank <= 0:
        raise ValueError("UCI multipv rank must be positive")

    metrics = AnalysisMetrics(
        depth=_parse_int_after(tokens, "depth"),
        seldepth=_parse_int_after(tokens, "seldepth"),
        nodes=_parse_int_after(tokens, "nodes"),
        time_ms=_parse_int_after(tokens, "time"),
        nps=_parse_int_after(tokens, "nps"),
        hashfull_per_mille=_parse_int_after(tokens, "hashfull"),
        tablebase_hits=_parse_int_after(tokens, "tbhits"),
    )
    return _ParsedInfo(
        rank=rank,
        line=CandidateLine(
            rank=rank,
            root_move_uci=pv[0],
            evaluation=evaluation,
            pv_uci=pv,
        ),
        metrics=metrics,
    )


def _go_command(request: AnalysisRequest) -> str:
    kind = request.search_limit.kind
    value = request.search_limit.value
    if kind == "depth":
        return f"go depth {value}"
    if kind == "nodes":
        return f"go nodes {value}"
    if kind == "movetime_ms":
        return f"go movetime {value}"
    raise ValueError(f"unsupported analysis limit kind: {kind!r}")


def _contiguous_records(
    records: dict[int, _ParsedInfo],
) -> tuple[_ParsedInfo, ...]:
    result: list[_ParsedInfo] = []
    rank = 1
    while rank in records:
        result.append(records[rank])
        rank += 1
    return tuple(result)


class UciAnalysisProvider:
    """Analyze canonical positions through one external UCI engine executable."""

    def __init__(
        self,
        executable: str,
        *,
        engine_options: tuple[tuple[str, str], ...] = (),
        startup_timeout_ms: int = 5_000,
        stop_grace_ms: int = 500,
    ) -> None:
        if not executable:
            raise ValueError("executable must not be empty")
        if startup_timeout_ms <= 0:
            raise ValueError("startup_timeout_ms must be positive")
        if stop_grace_ms <= 0:
            raise ValueError("stop_grace_ms must be positive")
        normalized: list[tuple[str, str]] = []
        seen: set[str] = set()
        for name, value in engine_options:
            if not name or "\n" in name or "\r" in name:
                raise ValueError("engine option name must be a single non-empty line")
            if "\n" in value or "\r" in value:
                raise ValueError("engine option value must be a single line")
            folded = name.casefold()
            if folded == "multipv":
                raise ValueError(
                    "MultiPV is owned by AnalysisRequest, not engine_options"
                )
            if folded in seen:
                raise ValueError("duplicate engine option name")
            seen.add(folded)
            normalized.append((name, value))
        self.executable = executable
        self.engine_options = tuple(sorted(normalized, key=lambda item: item[0]))
        self.startup_timeout_ms = startup_timeout_ms
        self.stop_grace_ms = stop_grace_ms

    def analyze(
        self,
        position: CanonicalPosition,
        request: AnalysisRequest,
    ) -> AnalysisOutcome:
        resolved = _resolve_executable(self.executable)
        if resolved is None:
            provenance = self._configured_provenance(None)
            return self._failure(
                position,
                request,
                provenance,
                "ENGINE_NOT_FOUND",
                f"UCI executable not found: {self.executable}",
            )

        provisional = self._configured_provenance(resolved)
        try:
            session = _UciSession(resolved)
        except OSError as exc:
            return self._failure(
                position,
                request,
                provisional,
                "ENGINE_START_FAILED",
                f"could not start UCI engine: {exc}",
            )

        try:
            try:
                handshake = self._handshake(session)
            except _ReadTimeout:
                return self._failure(
                    position,
                    request,
                    provisional,
                    "PROTOCOL_ERROR",
                    "timed out waiting for UCI handshake",
                )
            except _EngineExited as exc:
                return self._failure(
                    position,
                    request,
                    provisional,
                    "ENGINE_CRASHED",
                    f"engine exited during UCI handshake: {exc}",
                )
            except ValueError as exc:
                return self._failure(
                    position,
                    request,
                    provisional,
                    "PROTOCOL_ERROR",
                    str(exc),
                )

            option_result = self._effective_options(handshake, request)
            if isinstance(option_result, str):
                provenance = self._provenance(
                    resolved,
                    handshake,
                    self.engine_options,
                )
                return self._failure(
                    position,
                    request,
                    provenance,
                    "UNSUPPORTED_REQUEST",
                    option_result,
                )
            effective_options = option_result
            provenance = self._provenance(
                resolved,
                handshake,
                effective_options,
            )

            try:
                self._configure(session, effective_options)
            except _ReadTimeout:
                return self._failure(
                    position,
                    request,
                    provenance,
                    "PROTOCOL_ERROR",
                    "timed out waiting for readyok",
                )
            except _EngineExited as exc:
                return self._failure(
                    position,
                    request,
                    provenance,
                    "ENGINE_CRASHED",
                    f"engine exited during configuration: {exc}",
                )

            expected_count = expected_candidate_count(position.fen, request.multipv)
            request_fingerprint = analysis_request_fingerprint(
                fen=position.fen,
                request=request,
                provenance=provenance,
            )
            if expected_count == 0:
                return self._result(
                    position,
                    request,
                    provenance,
                    request_fingerprint,
                    status="terminal",
                    lines=(),
                    metrics=AnalysisMetrics(),
                    termination=AnalysisTermination("terminal_position"),
                )

            return self._run_search(
                session,
                position,
                request,
                provenance,
                request_fingerprint,
                expected_count,
            )
        finally:
            session.close()

    def _configured_provenance(
        self,
        resolved: str | None,
    ) -> EngineProvenance:
        binary_sha256 = _sha256_file(resolved) if resolved else None
        name = f"configured:{resolved or self.executable}"
        return EngineProvenance(
            provider_name=UCI_PROVIDER_NAME,
            provider_version=UCI_PROVIDER_VERSION,
            protocol="uci",
            engine_name=name,
            binary_sha256=binary_sha256,
            engine_options=self.engine_options,
        )

    def _provenance(
        self,
        resolved: str,
        handshake: _Handshake,
        effective_options: tuple[tuple[str, str], ...],
    ) -> EngineProvenance:
        return EngineProvenance(
            provider_name=UCI_PROVIDER_NAME,
            provider_version=UCI_PROVIDER_VERSION,
            protocol="uci",
            engine_name=handshake.engine_name,
            engine_author=handshake.engine_author,
            binary_sha256=_sha256_file(resolved),
            engine_options=effective_options,
        )

    def _handshake(self, session: _UciSession) -> _Handshake:
        session.send("uci")
        deadline = time.monotonic() + self.startup_timeout_ms / 1000
        engine_name: str | None = None
        engine_author: str | None = None
        options: list[str] = []
        while True:
            line = session.read_line(self._remaining_ms(deadline))
            if line == "uciok":
                break
            if line.startswith("id name "):
                engine_name = line[len("id name ") :].strip() or None
            elif line.startswith("id author "):
                engine_author = line[len("id author ") :].strip() or None
            else:
                option_name = _parse_option_name(line)
                if option_name is not None:
                    options.append(option_name)
        if engine_name is None:
            raise ValueError("UCI engine did not identify itself with id name")
        return _Handshake(
            engine_name=engine_name,
            engine_author=engine_author,
            advertised_options=tuple(options),
        )

    def _effective_options(
        self,
        handshake: _Handshake,
        request: AnalysisRequest,
    ) -> tuple[tuple[str, str], ...] | str:
        advertised = {
            name.casefold(): name for name in handshake.advertised_options
        }
        effective: list[tuple[str, str]] = []
        for requested_name, value in self.engine_options:
            actual = advertised.get(requested_name.casefold())
            if actual is None:
                return f"UCI engine does not advertise option {requested_name!r}"
            effective.append((actual, value))

        multipv_name = advertised.get("multipv")
        if request.multipv > 1 and multipv_name is None:
            return "UCI engine does not advertise MultiPV"
        if multipv_name is not None:
            effective.append((multipv_name, str(request.multipv)))

        return tuple(sorted(effective, key=lambda item: item[0]))

    def _configure(
        self,
        session: _UciSession,
        options: tuple[tuple[str, str], ...],
    ) -> None:
        for name, value in options:
            session.send(f"setoption name {name} value {value}")
        self._ready(session)
        session.send("ucinewgame")
        self._ready(session)

    def _ready(self, session: _UciSession) -> None:
        session.send("isready")
        deadline = time.monotonic() + self.startup_timeout_ms / 1000
        while True:
            line = session.read_line(self._remaining_ms(deadline))
            if line == "readyok":
                return

    def _run_search(
        self,
        session: _UciSession,
        position: CanonicalPosition,
        request: AnalysisRequest,
        provenance: EngineProvenance,
        request_fingerprint: str,
        expected_count: int,
    ) -> AnalysisOutcome:
        try:
            session.send(f"position fen {position.fen}")
            session.send(_go_command(request))
        except _EngineExited as exc:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "ENGINE_CRASHED",
                f"engine exited before search started: {exc}",
            )

        records: dict[int, _ParsedInfo] = {}
        deadline = (
            None
            if request.supervisor_timeout_ms is None
            else time.monotonic() + request.supervisor_timeout_ms / 1000
        )
        try:
            bestmove = self._collect_until_bestmove(
                session,
                position.side_to_move,
                records,
                deadline,
            )
        except _ReadTimeout:
            try:
                session.send("stop")
            except _EngineExited:
                pass
            try:
                self._collect_until_bestmove(
                    session,
                    position.side_to_move,
                    records,
                    time.monotonic() + self.stop_grace_ms / 1000,
                )
            except (_ReadTimeout, _EngineExited, ValueError):
                pass
            return self._partial_or_failure(
                position,
                request,
                provenance,
                request_fingerprint,
                records,
                expected_count,
                termination="timeout",
                failure_code="ANALYSIS_TIMEOUT",
                failure_message="analysis exceeded supervisor timeout",
            )
        except _EngineExited as exc:
            return self._partial_or_failure(
                position,
                request,
                provenance,
                request_fingerprint,
                records,
                expected_count,
                termination="engine_crash",
                failure_code="ENGINE_CRASHED",
                failure_message=f"engine exited during search: {exc}",
            )
        except ValueError as exc:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                str(exc),
            )

        records_tuple = _contiguous_records(records)
        if not records_tuple:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                "engine returned bestmove without a valid scored PV",
            )
        if len(records_tuple) > expected_count:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                "engine returned more MultiPV lines than requested",
            )
        lines = tuple(record.line for record in records_tuple)
        if bestmove in {"(none)", "0000"}:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                "engine returned no best move for a non-terminal position",
            )
        if bestmove != lines[0].root_move_uci:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                "bestmove disagrees with MultiPV rank 1",
            )
        try:
            validate_candidate_lines(position.fen, lines)
        except ValueError as exc:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                str(exc),
            )

        status = "complete" if len(lines) == expected_count else "partial"
        return self._result(
            position,
            request,
            provenance,
            request_fingerprint,
            status=status,
            lines=lines,
            metrics=records_tuple[0].metrics,
            termination=AnalysisTermination("completed"),
        )

    def _partial_or_failure(
        self,
        position: CanonicalPosition,
        request: AnalysisRequest,
        provenance: EngineProvenance,
        request_fingerprint: str,
        records: dict[int, _ParsedInfo],
        expected_count: int,
        *,
        termination: str,
        failure_code: str,
        failure_message: str,
    ) -> AnalysisOutcome:
        records_tuple = _contiguous_records(records)
        if not records_tuple:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                failure_code,
                failure_message,
            )
        if len(records_tuple) > expected_count:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                "engine returned more MultiPV lines than requested",
            )
        lines = tuple(record.line for record in records_tuple)
        try:
            validate_candidate_lines(position.fen, lines)
        except ValueError as exc:
            return self._failure_with_fingerprint(
                position,
                request_fingerprint,
                "INVALID_ENGINE_OUTPUT",
                str(exc),
            )
        return self._result(
            position,
            request,
            provenance,
            request_fingerprint,
            status="partial",
            lines=lines,
            metrics=records_tuple[0].metrics,
            termination=AnalysisTermination(termination),
        )

    def _collect_until_bestmove(
        self,
        session: _UciSession,
        root_side: str,
        records: dict[int, _ParsedInfo],
        deadline: float | None,
    ) -> str:
        while True:
            line = session.read_line(self._remaining_ms(deadline))
            if line.startswith("bestmove "):
                tokens = line.split()
                if len(tokens) < 2:
                    raise ValueError("malformed UCI bestmove line")
                return tokens[1]
            parsed = _parse_info(line, root_side)
            if parsed is not None:
                records[parsed.rank] = parsed

    @staticmethod
    def _remaining_ms(deadline: float | None) -> int | None:
        if deadline is None:
            return None
        remaining = int((deadline - time.monotonic()) * 1000)
        if remaining <= 0:
            raise _ReadTimeout
        return remaining

    def _failure(
        self,
        position: CanonicalPosition,
        request: AnalysisRequest,
        provenance: EngineProvenance,
        code: str,
        message: str,
    ) -> AnalysisFailure:
        fingerprint = analysis_request_fingerprint(
            fen=position.fen,
            request=request,
            provenance=provenance,
        )
        return self._failure_with_fingerprint(
            position,
            fingerprint,
            code,
            message,
        )

    @staticmethod
    def _failure_with_fingerprint(
        position: CanonicalPosition,
        request_fingerprint: str,
        code: str,
        message: str,
    ) -> AnalysisFailure:
        return AnalysisFailure(
            position_id=position.position_id,
            fen=position.fen,
            request_fingerprint=request_fingerprint,
            code=code,
            message=message,
        )

    @staticmethod
    def _result(
        position: CanonicalPosition,
        request: AnalysisRequest,
        provenance: EngineProvenance,
        request_fingerprint: str,
        *,
        status: str,
        lines: tuple[CandidateLine, ...],
        metrics: AnalysisMetrics,
        termination: AnalysisTermination,
    ) -> PositionAnalysis:
        analysis = PositionAnalysis(
            position_id=position.position_id,
            fen=position.fen,
            request_fingerprint=request_fingerprint,
            result_fingerprint="",
            status=status,
            request=request,
            provenance=provenance,
            lines=lines,
            metrics=metrics,
            termination=termination,
        )
        return replace(
            analysis,
            result_fingerprint=analysis_result_fingerprint(analysis),
        )
