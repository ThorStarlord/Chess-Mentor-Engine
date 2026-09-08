"""PGN ingestion into immutable canonical chess records."""

from __future__ import annotations

import re

from ._core import STANDARD_FEN, Board
from .errors import PgnError, UnsupportedVariantError
from .model import (
    CanonicalGame,
    CanonicalPosition,
    PgnIngestResult,
    SourceProvenance,
    TimeControl,
)
from .provenance import (
    PARSER_ID,
    position_fingerprint,
    semantic_game_fingerprint,
    sha256_bytes,
    stable_headers,
)

_HEADER_RE = re.compile(r'^\[([A-Za-z0-9_]+)\s+"((?:\\.|[^"\\])*)"\]\s*$')
_RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}


def ingest_pgn(data: bytes | str) -> PgnIngestResult:
    """Ingest one or more Standard-chess PGN games deterministically."""
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    if not raw.strip():
        raise PgnError("PGN input is empty")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PgnError("PGN input is not valid UTF-8") from exc
    source_hash = sha256_bytes(raw)
    chunks = _split_games(text)
    games = tuple(
        _ingest_game(chunk, source_hash, index)
        for index, chunk in enumerate(chunks)
    )
    if not games:
        raise PgnError("PGN input contained no games")
    return PgnIngestResult(source_sha256=source_hash, games=games)


def _split_games(text: str) -> list[str]:
    games: list[list[str]] = []
    current: list[str] = []
    movetext_started = False
    for line in text.splitlines():
        stripped = line.strip()
        is_header = stripped.startswith("[")
        if is_header and movetext_started:
            if current:
                games.append(current)
            current = [line]
            movetext_started = False
            continue
        current.append(line)
        if stripped and not is_header:
            movetext_started = True
    if current and any(line.strip() for line in current):
        games.append(current)
    return [
        "\n".join(lines).strip()
        for lines in games
        if any(line.strip() for line in lines)
    ]


def _ingest_game(chunk: str, source_hash: str, source_game_index: int) -> CanonicalGame:
    headers: dict[str, str] = {}
    movelines: list[str] = []
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            match = _HEADER_RE.match(stripped)
            if not match:
                raise PgnError(f"malformed PGN header: {line!r}")
            key, escaped = match.groups()
            value = escaped.replace(r'\"', '"').replace(r"\\", "\\")
            headers[key] = value
        else:
            movelines.append(line)
    variant = _normalize_variant(headers.get("Variant"))
    initial_fen = (
        headers.get("FEN")
        if headers.get("SetUp") == "1" or headers.get("FEN")
        else STANDARD_FEN
    )
    if (
        headers.get("Variant", "").casefold() == "from position"
        and "FEN" not in headers
    ):
        raise PgnError("From Position PGN requires a FEN header")
    board = Board.from_fen(initial_fen)
    normalized_initial_fen = board.fen()
    san_tokens, movetext_result = _mainline_tokens("\n".join(movelines))
    moves_uci: list[str] = []
    moves_san: list[str] = []
    position_fens: list[tuple[str, str | None, str | None]] = [
        (board.fen(), None, None)
    ]
    for index, token in enumerate(san_tokens, start=1):
        try:
            move, canonical_san = board.parse_san(token)
        except PgnError as exc:
            raise PgnError(f"game {source_game_index + 1}, ply {index}: {exc}") from exc
        uci = move.uci()
        board.push(move)
        moves_uci.append(uci)
        moves_san.append(canonical_san)
        position_fens.append((board.fen(), uci, canonical_san))
    semantic = semantic_game_fingerprint(
        variant=variant, initial_fen=normalized_initial_fen, moves_uci=moves_uci
    )
    game_id = f"game_{semantic[:20]}"
    positions = tuple(
        _make_position(game_id, semantic, ply_index, fen, uci, san)
        for ply_index, (fen, uci, san) in enumerate(position_fens)
    )
    stable = stable_headers(headers)
    provenance = SourceProvenance(
        source_type="pgn",
        source_sha256=source_hash,
        source_game_index=source_game_index,
        parser_id=PARSER_ID,
        raw_headers=stable,
        source_game_identifier=headers.get("Site") or headers.get("Event"),
    )
    result = headers.get("Result") or movetext_result
    time_control = _parse_time_control(headers.get("TimeControl"))
    return CanonicalGame(
        game_id=game_id,
        semantic_fingerprint=semantic,
        provenance=provenance,
        headers=stable,
        white=headers.get("White"),
        black=headers.get("Black"),
        result=result,
        date=headers.get("UTCDate") or headers.get("Date"),
        time_control=time_control,
        variant=variant,
        initial_fen=normalized_initial_fen,
        moves_uci=tuple(moves_uci),
        moves_san=tuple(moves_san),
        positions=positions,
    )


def _make_position(
    game_id: str,
    game_fingerprint: str,
    ply_index: int,
    fen: str,
    last_move_uci: str | None,
    last_move_san: str | None,
) -> CanonicalPosition:
    board = Board.from_fen(fen)
    position_hash = position_fingerprint(
        game_fingerprint=game_fingerprint, ply_index=ply_index, fen=fen
    )
    return CanonicalPosition(
        position_id=f"pos_{position_hash[:20]}",
        game_id=game_id,
        ply_index=ply_index,
        move_number=board.fullmove_number,
        side_to_move=board.turn,
        fen=fen,
        last_move_uci=last_move_uci,
        last_move_san=last_move_san,
    )


def _normalize_variant(raw: str | None) -> str:
    if raw is None or raw.casefold() in {"standard", "from position"}:
        return "standard"
    raise UnsupportedVariantError(f"unsupported chess variant: {raw}")


def _parse_time_control(raw: str | None) -> TimeControl:
    if raw is None:
        return TimeControl(raw=None)
    match = re.fullmatch(r"(\d+)\+(\d+)", raw)
    if match:
        return TimeControl(
            raw=raw,
            base_seconds=int(match.group(1)),
            increment_seconds=int(match.group(2)),
        )
    return TimeControl(raw=raw)


def _mainline_tokens(movetext: str) -> tuple[list[str], str | None]:
    cleaned = _remove_comments_and_variations(movetext)
    cleaned = re.sub(r"\$\d+", " ", cleaned)
    tokens: list[str] = []
    result: str | None = None
    for raw in cleaned.split():
        token = raw.strip()
        token = re.sub(r"^\d+\.(?:\.\.)?", "", token)
        if not token:
            continue
        if token in _RESULTS:
            if token != "*":
                result = token
            continue
        tokens.append(token)
    return tokens, result


def _remove_comments_and_variations(text: str) -> str:
    output: list[str] = []
    variation_depth = 0
    brace_comment = False
    semicolon_comment = False
    for ch in text:
        if semicolon_comment:
            if ch == "\n":
                semicolon_comment = False
                output.append(" ")
            continue
        if brace_comment:
            if ch == "}":
                brace_comment = False
                output.append(" ")
            continue
        if ch == ";":
            semicolon_comment = True
            continue
        if ch == "{":
            brace_comment = True
            continue
        if ch == "(":
            variation_depth += 1
            continue
        if ch == ")":
            if variation_depth == 0:
                raise PgnError("unbalanced PGN variation")
            variation_depth -= 1
            continue
        if variation_depth == 0:
            output.append(ch)
    if brace_comment or variation_depth:
        raise PgnError("unclosed PGN comment or variation")
    return "".join(output)
