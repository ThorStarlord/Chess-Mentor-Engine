from __future__ import annotations

from chess_mentor_engine.chess import CanonicalPosition
from chess_mentor_engine.chess_knowledge.detectors import (
    MOVE_DETECTOR_SPEC,
    POSITION_DETECTOR_SPEC,
    detect_move_knowledge,
    detect_position_knowledge,
)

_CREATED_AT = "2026-09-11T08:00:00-03:00"


def _position(
    fen: str,
    *,
    position_id: str = "pos_detector_001",
    game_id: str = "game_detector_001",
    ply_index: int = 0,
    side_to_move: str = "white",
) -> CanonicalPosition:
    return CanonicalPosition(
        position_id=position_id,
        game_id=game_id,
        ply_index=ply_index,
        move_number=1,
        side_to_move=side_to_move,
        fen=fen,
        last_move_uci=None,
        last_move_san=None,
    )


def _by_concept(assertions):
    result = {}
    for assertion in assertions:
        result.setdefault(assertion.concept_id, []).append(assertion)
    return result


def _qualifiers(assertion) -> dict[str, str]:
    return {item.name: item.value for item in assertion.qualifiers}


def test_position_detector_emits_rule_facts_and_structural_features() -> None:
    position = _position(
        "4k3/7p/8/4P3/8/2P5/P1P5/4K3 w - - 0 1"
    )
    assertions = detect_position_knowledge(position, created_at=_CREATED_AT)
    concepts = _by_concept(assertions)

    assert _qualifiers(concepts["rule.check"][0]) == {"color": "white"}
    assert concepts["rule.check"][0].status == "absent"
    assert concepts["rule.checkmate"][0].status == "absent"

    open_files = {_qualifiers(item)["file"] for item in concepts["position.open_file"]}
    assert open_files == {"b", "d", "f", "g"}

    semi_open = {
        (_qualifiers(item)["color"], _qualifiers(item)["file"])
        for item in concepts["position.semi_open_file"]
    }
    assert ("white", "h") in semi_open
    assert ("black", "a") in semi_open
    assert ("black", "c") in semi_open
    assert ("black", "e") in semi_open

    doubled = concepts["position.doubled_pawns"]
    assert len(doubled) == 1
    assert _qualifiers(doubled[0]) == {
        "color": "white",
        "file": "c",
        "count": "2",
        "squares": "c2,c3",
    }

    passed = {
        (_qualifiers(item)["color"], _qualifiers(item)["pawn_square"])
        for item in concepts["position.passed_pawn"]
    }
    assert ("white", "e5") in passed
    assert ("black", "h7") in passed

    islands = {
        (_qualifiers(item)["color"], _qualifiers(item)["files"])
        for item in concepts["position.pawn_island"]
    }
    assert islands == {
        ("white", "a"),
        ("white", "c"),
        ("white", "e"),
        ("black", "h"),
    }

    assert all(
        item.provenance.source_id == POSITION_DETECTOR_SPEC.detector_id
        for item in assertions
    )


def test_position_detector_reuses_m2_absolute_pin_evidence() -> None:
    position = _position("k3r3/8/8/8/8/8/4N3/4K3 w - - 0 1")
    assertions = detect_position_knowledge(position, created_at=_CREATED_AT)
    pins = _by_concept(assertions)["tactic.absolute_pin"]

    assert len(pins) == 1
    assert pins[0].authority_class == "deterministic_position_fact"
    assert pins[0].evidence_refs[0].kind == "position_features"
    assert _qualifiers(pins[0]) == {
        "color": "white",
        "pinned_square": "e2",
        "king_square": "e1",
        "attacker_square": "e8",
    }


def test_position_detector_distinguishes_check_from_checkmate() -> None:
    check = _position(
        "4k3/8/8/8/8/8/4R3/4K3 b - - 0 1",
        side_to_move="black",
    )
    check_assertions = _by_concept(
        detect_position_knowledge(check, created_at=_CREATED_AT)
    )
    assert check_assertions["rule.check"][0].status == "present"
    assert check_assertions["rule.checkmate"][0].status == "absent"

    mate = _position(
        "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1",
        position_id="pos_mate",
        side_to_move="black",
    )
    mate_assertions = _by_concept(
        detect_position_knowledge(mate, created_at=_CREATED_AT)
    )
    assert mate_assertions["rule.check"][0].status == "present"
    assert mate_assertions["rule.checkmate"][0].status == "present"


def test_position_detector_emits_bishop_pair_for_each_side() -> None:
    position = _position(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )
    assertions = _by_concept(
        detect_position_knowledge(position, created_at=_CREATED_AT)
    )
    bishop_pairs = {
        _qualifiers(item)["color"] for item in assertions["position.bishop_pair"]
    }
    assert bishop_pairs == {"white", "black"}


def test_position_detector_is_deterministic_for_same_explicit_inputs() -> None:
    position = _position("k3r3/8/8/8/8/8/4N3/4K3 w - - 0 1")
    first = detect_position_knowledge(position, created_at=_CREATED_AT)
    second = detect_position_knowledge(position, created_at=_CREATED_AT)
    assert first == second


def test_move_detector_detects_promotion_and_underpromotion() -> None:
    position = _position("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")

    queen = _by_concept(
        detect_move_knowledge(position, "a7a8q", created_at=_CREATED_AT)
    )
    assert "tactic.promotion" in queen
    assert "tactic.underpromotion" not in queen
    assert _qualifiers(queen["tactic.promotion"][0])["promotion_piece"] == "q"

    knight = _by_concept(
        detect_move_knowledge(position, "a7a8n", created_at=_CREATED_AT)
    )
    assert "tactic.promotion" in knight
    assert "tactic.underpromotion" in knight
    assert _qualifiers(knight["tactic.underpromotion"][0])["promotion_piece"] == "n"


def test_move_detector_detects_fork_by_moved_piece() -> None:
    position = _position("k2r3q/8/8/4N3/8/8/8/4K3 w - - 0 1")
    assertions = _by_concept(
        detect_move_knowledge(position, "e5f7", created_at=_CREATED_AT)
    )
    fork = assertions["tactic.fork"][0]
    qualifiers = _qualifiers(fork)

    assert fork.authority_class == "deterministic_sequence_pattern"
    assert qualifiers["attacker_square"] == "f7"
    assert qualifiers["target_count"] == "2"
    assert qualifiers["target_squares"] == "d8,h8"


def test_move_detector_detects_discovered_and_double_check() -> None:
    position = _position("4k3/8/8/8/8/8/4B3/K3R3 w - - 0 1")
    assertions = _by_concept(
        detect_move_knowledge(position, "e2b5", created_at=_CREATED_AT)
    )

    discovered = assertions["tactic.discovered_check"][0]
    double = assertions["tactic.double_check"][0]
    assert _qualifiers(discovered)["uncovered_checker_squares"] == "e1"
    assert _qualifiers(double)["checker_squares"] == "e1,b5"


def test_move_detector_rejects_illegal_move_and_near_miss() -> None:
    start = _position(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )
    try:
        detect_move_knowledge(start, "e2e5", created_at=_CREATED_AT)
    except ValueError as exc:
        assert "illegal move" in str(exc)
    else:
        raise AssertionError("illegal move must be rejected")

    fork_position = _position("k2r3q/8/8/4N3/8/8/8/4K3 w - - 0 1")
    near_miss = _by_concept(
        detect_move_knowledge(fork_position, "e5c4", created_at=_CREATED_AT)
    )
    assert "tactic.fork" not in near_miss


def test_move_detector_is_deterministic_and_provenance_bound() -> None:
    position = _position("k2r3q/8/8/4N3/8/8/8/4K3 w - - 0 1")
    first = detect_move_knowledge(position, "e5f7", created_at=_CREATED_AT)
    second = detect_move_knowledge(position, "e5f7", created_at=_CREATED_AT)

    assert first == second
    assert all(
        item.provenance.source_id == MOVE_DETECTOR_SPEC.detector_id for item in first
    )
    assert all(item.evidence_refs[0].kind == "move_sequence" for item in first)
