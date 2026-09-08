from __future__ import annotations

import chess

from chess_mentor_engine.chess import build_position_features, ingest_pgn

FENS = (
    chess.STARTING_FEN,
    "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22",
    "k3r3/8/8/8/8/8/4N3/4K3 w - - 0 1",
    "k7/8/7b/8/8/8/3N4/2K5 w - - 0 1",
    "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1",
    "4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1",
    "4r1k1/8/8/8/8/8/8/4K3 w - - 0 1",
    "r3k3/8/8/8/8/8/8/R3K3 w - - 0 1",
)


def _position(fen: str):
    pgn = f'''[SetUp "1"]
[FEN "{fen}"]

*'''
    return ingest_pgn(pgn).games[0].positions[0]


def _square_names(squares) -> tuple[str, ...]:
    return tuple(chess.square_name(square) for square in sorted(squares))


def _oracle_pins(board: chess.Board) -> tuple[tuple[str, str, str, str], ...]:
    pins: list[tuple[str, str, str, str]] = []
    for color, name in ((chess.WHITE, "white"), (chess.BLACK, "black")):
        king = board.king(color)
        if king is None:
            continue
        for square in chess.scan_forward(board.occupied_co[color]):
            if square == king or not board.is_pinned(color, square):
                continue
            ray = board.pin(color, square)
            pinners = [
                candidate
                for candidate in ray
                if board.color_at(candidate) == (not color)
                and board.piece_type_at(candidate)
                in {chess.BISHOP, chess.ROOK, chess.QUEEN}
            ]
            assert len(pinners) == 1
            pins.append(
                (
                    name,
                    chess.square_name(square),
                    chess.square_name(king),
                    chess.square_name(pinners[0]),
                )
            )
    return tuple(sorted(pins, key=lambda item: (0 if item[0] == "white" else 1, item[1], item[3])))


def test_m2_feature_surface_matches_independent_oracle() -> None:
    for fen in FENS:
        position = _position(fen)
        packet = build_position_features(position)
        board = chess.Board(fen)

        legal = tuple(sorted(move.uci() for move in board.legal_moves))
        checks = tuple(
            sorted(move.uci() for move in board.legal_moves if board.gives_check(move))
        )
        captures = tuple(
            sorted(move.uci() for move in board.legal_moves if board.is_capture(move))
        )

        assert packet.legal_moves == legal
        assert packet.legal_checks == checks
        assert packet.legal_captures == captures

        attack_map = {item.square: item for item in packet.square_attacks}
        for square in chess.SQUARES:
            item = attack_map[chess.square_name(square)]
            assert item.white_attackers == _square_names(
                board.attackers(chess.WHITE, square)
            )
            assert item.black_attackers == _square_names(
                board.attackers(chess.BLACK, square)
            )

        defenses = {item.square: item.defenders for item in packet.piece_defenders}
        for square in chess.scan_forward(board.occupied):
            color = board.color_at(square)
            assert color is not None
            assert defenses[chess.square_name(square)] == _square_names(
                board.attackers(color, square)
            )

        actual_pins = tuple(
            (
                pin.color,
                pin.pinned_square,
                pin.king_square,
                pin.attacker_square,
            )
            for pin in packet.absolute_pins
        )
        assert actual_pins == _oracle_pins(board)
