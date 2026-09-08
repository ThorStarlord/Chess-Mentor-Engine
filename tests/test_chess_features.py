from __future__ import annotations

from chess_mentor_engine.chess import (
    build_position_features,
    canonical_json,
    ingest_pgn,
)


def _position(fen: str):
    pgn = f'''[SetUp "1"]
[FEN "{fen}"]

*'''
    return ingest_pgn(pgn).games[0].positions[0]


def _attacks(packet, square: str):
    return next(item for item in packet.square_attacks if item.square == square)


def _defense(packet, square: str):
    return next(item for item in packet.piece_defenders if item.square == square)


def test_starting_position_has_expected_legal_surface() -> None:
    position = ingest_pgn("*").games[0].positions[0]
    packet = build_position_features(position)

    assert len(packet.legal_moves) == 20
    assert packet.legal_checks == ()
    assert packet.legal_captures == ()
    assert packet.square_attacks[0].square == "a1"
    assert packet.square_attacks[-1].square == "h8"
    assert len(packet.square_attacks) == 64


def test_attackers_are_geometric_and_defenders_are_same_color_attackers() -> None:
    position = ingest_pgn("*").games[0].positions[0]
    packet = build_position_features(position)

    assert _attacks(packet, "e3").white_attackers == ("d2", "f2")
    assert _attacks(packet, "e3").black_attackers == ()
    assert _defense(packet, "e2").defenders == ("d1", "e1", "f1", "g1")


def test_pinned_piece_still_has_geometric_attacks_but_no_illegal_moves() -> None:
    position = _position("k3r3/8/8/8/8/8/4N3/4K3 w - - 0 1")
    packet = build_position_features(position)

    assert packet.absolute_pins[0].to_dict() == {
        "color": "white",
        "pinned_square": "e2",
        "king_square": "e1",
        "attacker_square": "e8",
    }
    assert "e2" in _attacks(packet, "c3").white_attackers
    assert not any(move.startswith("e2") for move in packet.legal_moves)


def test_legal_capture_can_also_be_a_legal_check() -> None:
    position = _position("r3k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    packet = build_position_features(position)

    assert "a1a8" in packet.legal_captures
    assert "a1a8" in packet.legal_checks
    assert "a1a8" in packet.legal_moves


def test_en_passant_is_classified_as_a_legal_capture() -> None:
    position = _position("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    packet = build_position_features(position)

    assert "e5d6" in packet.legal_moves
    assert "e5d6" in packet.legal_captures


def test_diagonal_absolute_pin_is_reported() -> None:
    position = _position("k7/8/7b/8/8/8/3N4/2K5 w - - 0 1")
    packet = build_position_features(position)

    assert [pin.to_dict() for pin in packet.absolute_pins] == [
        {
            "color": "white",
            "pinned_square": "d2",
            "king_square": "c1",
            "attacker_square": "h6",
        }
    ]


def test_feature_packet_serialization_is_deterministic() -> None:
    position = _position("k3r3/8/8/8/8/8/4N3/4K3 w - - 0 1")
    first = build_position_features(position)
    second = build_position_features(position)

    assert first == second
    assert canonical_json(first.to_dict()) == canonical_json(second.to_dict())
