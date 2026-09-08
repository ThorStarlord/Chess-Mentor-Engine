from __future__ import annotations

import pytest

from chess_mentor_engine.chess import (
    PgnError,
    UnsupportedVariantError,
    build_position_context,
    canonical_json,
    ingest_pgn,
)


STANDARD_PGN = b'''[Event "Mini"]
[Site "https://example.test/game/1"]
[Date "2026.09.08"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]
[TimeControl "600+0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 1-0
'''

ANNOTATED_EQUIVALENT = b'''[Event "Mini"]
[Site "https://example.test/game/1"]
[Date "2026.09.08"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]
[TimeControl "600+0"]

1. e4 {book} e5 2. Nf3 $1 Nc6 (2... Nf6) 3. Bb5!? a6 4. Ba4 Nf6
5. O-O Be7 6. Re1 b5 7. Bb3 O-O 1-0
'''

DIFFERENT_GAME = STANDARD_PGN.replace(b"7. Bb3 O-O", b"7. Bb3 d6")

CUSTOM_PGN = b'''[Event "From Position"]
[Variant "From Position"]
[SetUp "1"]
[FEN "r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22"]
[Result "*"]

22... Qe7 *
'''


def test_repeated_import_is_stable() -> None:
    first = ingest_pgn(STANDARD_PGN)
    second = ingest_pgn(STANDARD_PGN)
    assert first.source_sha256 == second.source_sha256
    assert first.games[0].semantic_fingerprint == second.games[0].semantic_fingerprint
    assert first.games[0].game_id == second.games[0].game_id
    assert [p.position_id for p in first.games[0].positions] == [
        p.position_id for p in second.games[0].positions
    ]
    assert [p.fen for p in first.games[0].positions] == [
        p.fen for p in second.games[0].positions
    ]


def test_comments_change_source_not_semantics() -> None:
    plain = ingest_pgn(STANDARD_PGN)
    annotated = ingest_pgn(ANNOTATED_EQUIVALENT)
    assert plain.source_sha256 != annotated.source_sha256
    assert (
        plain.games[0].semantic_fingerprint
        == annotated.games[0].semantic_fingerprint
    )
    assert plain.games[0].moves_uci == annotated.games[0].moves_uci
    assert [p.fen for p in plain.games[0].positions] == [
        p.fen for p in annotated.games[0].positions
    ]


def test_changed_chess_content_changes_semantic_identity() -> None:
    assert (
        ingest_pgn(STANDARD_PGN).games[0].semantic_fingerprint
        != ingest_pgn(DIFFERENT_GAME).games[0].semantic_fingerprint
    )


def test_initial_position_is_ply_zero_and_replay_has_one_more_position_than_moves(
) -> None:
    game = ingest_pgn(STANDARD_PGN).games[0]
    assert game.positions[0].ply_index == 0
    assert game.positions[0].last_move_uci is None
    assert len(game.positions) == len(game.moves_uci) + 1
    assert game.positions[-1].fen == (
        "r1bq1rk1/2ppbppp/p1n2n2/1p2p3/4P3/1B3N2/PPPP1PPP/RNBQR1K1 w - - 2 8"
    )


def test_custom_fen_and_context_packet_are_deterministic() -> None:
    game = ingest_pgn(CUSTOM_PGN).games[0]
    initial = game.positions[0]
    assert initial.side_to_move == "black"
    assert initial.move_number == 22
    packet = build_position_context(game, initial)
    assert packet.board_ascii == "\n".join(
        [
            "8  r . . q r . k .",
            "7  . b . . . p p p",
            "6  . . p . . . . .",
            "5  p p b . . . . Q",
            "4  . . . p . . . .",
            "3  . . . . . . P P",
            "2  P P P . . . B K",
            "1  R . B . . R . .",
            "   a b c d e f g h",
        ]
    )
    assert packet.material_summary.white.to_dict() == {
        "queen": 1,
        "rook": 2,
        "bishop": 2,
        "knight": 0,
        "pawn": 5,
    }
    assert packet.material_summary.black.to_dict() == {
        "queen": 1,
        "rook": 2,
        "bishop": 2,
        "knight": 0,
        "pawn": 7,
    }
    piece_map = {(g.color, g.piece): g.squares for g in packet.piece_map}
    assert piece_map[("white", "Queen")] == ("h5",)
    assert piece_map[("black", "King")] == ("g8",)


def test_custom_fen_move_replays() -> None:
    game = ingest_pgn(CUSTOM_PGN).games[0]
    assert game.moves_uci == ("d8e7",)
    assert game.moves_san == ("Qe7",)
    assert game.positions[1].fen.startswith(
        "r3r1k1/1b2qppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 w"
    )


def test_multi_game_source() -> None:
    combined = STANDARD_PGN + b"\n\n" + CUSTOM_PGN
    result = ingest_pgn(combined)
    assert len(result.games) == 2
    assert result.games[0].provenance.source_game_index == 0
    assert result.games[1].provenance.source_game_index == 1
    assert (
        result.games[0].provenance.source_sha256
        == result.games[1].provenance.source_sha256
    )


def test_missing_optional_headers_are_preserved_as_missing() -> None:
    game = ingest_pgn("1. e4 e5 2. Nf3 Nc6 *").games[0]
    assert game.white is None
    assert game.black is None
    assert game.date is None
    assert game.time_control.raw is None


def test_malformed_or_unsupported_input_fails_explicitly() -> None:
    with pytest.raises(PgnError):
        ingest_pgn("1. e5 *")
    with pytest.raises(UnsupportedVariantError):
        ingest_pgn('[Variant "Chess960"]\n\n1. e4 *')
    with pytest.raises(PgnError):
        ingest_pgn(b"")


def test_semantic_serialization_is_deterministic() -> None:
    game = ingest_pgn(STANDARD_PGN).games[0]
    assert canonical_json(game.to_dict()) == canonical_json(game.to_dict())


def test_en_passant_replay() -> None:
    pgn = '''[SetUp "1"]
[FEN "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"]

1. exd6 *'''
    game = ingest_pgn(pgn).games[0]
    assert game.moves_uci == ("e5d6",)
    assert "3P4" in game.positions[-1].fen.split()[0]


def test_promotion_replay() -> None:
    pgn = '''[SetUp "1"]
[FEN "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"]

1. a8=Q+ *'''
    game = ingest_pgn(pgn).games[0]
    assert game.moves_uci == ("a7a8q",)
    assert game.positions[-1].fen.startswith("Q3k3/")
