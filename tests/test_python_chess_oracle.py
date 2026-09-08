from __future__ import annotations

import io

import chess
import chess.pgn
import pytest

from chess_mentor_engine.chess import ingest_pgn
from chess_mentor_engine.chess._core import Board

STANDARD_PGN = '''[Event "Oracle standard"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5
7. Bb3 O-O *
'''

ANNOTATED_PGN = '''[Event "Oracle annotated"]
[Result "*"]

1. e4 {book} e5 2. Nf3 $1 Nc6 (2... Nf6) 3. Bb5 a6 4. Ba4 Nf6
5. O-O Be7 6. Re1 b5 7. Bb3 O-O *
'''

CUSTOM_PGN = '''[Event "From Position"]
[Variant "From Position"]
[SetUp "1"]
[FEN "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22"]
[Result "*"]

22... Qe7 *
'''

EN_PASSANT_PGN = '''[SetUp "1"]
[FEN "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"]

1. exd6 *
'''

PROMOTION_PGN = '''[SetUp "1"]
[FEN "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"]

1. a8=Q+ *
'''


def _oracle_replay(pgn: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    game = chess.pgn.read_game(io.StringIO(pgn))
    assert game is not None
    board = game.board()
    moves: list[str] = []
    fens = [board.fen(en_passant="fen")]
    for move in game.mainline_moves():
        moves.append(move.uci())
        board.push(move)
        fens.append(board.fen(en_passant="fen"))
    return tuple(moves), tuple(fens)


@pytest.mark.parametrize(
    "pgn",
    [
        STANDARD_PGN,
        ANNOTATED_PGN,
        CUSTOM_PGN,
        EN_PASSANT_PGN,
        PROMOTION_PGN,
    ],
)
def test_canonical_replay_matches_python_chess(pgn: str) -> None:
    ours = ingest_pgn(pgn).games[0]
    oracle_moves, oracle_fens = _oracle_replay(pgn)
    assert ours.moves_uci == oracle_moves
    assert tuple(position.fen for position in ours.positions) == oracle_fens


@pytest.mark.parametrize(
    "fen",
    [
        chess.STARTING_FEN,
        "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22",
        "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "4k3/P7/8/8/8/8/8/4K3 w - - 0 1",
        "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1",
    ],
)
def test_private_legal_moves_match_python_chess(fen: str) -> None:
    ours = {move.uci() for move in Board.from_fen(fen).legal_moves()}
    oracle = {move.uci() for move in chess.Board(fen).legal_moves}
    assert ours == oracle
