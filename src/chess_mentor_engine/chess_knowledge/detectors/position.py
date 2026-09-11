"""Conservative deterministic position-level chess-knowledge detection."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.chess import CanonicalPosition, canonical_json
from chess_mentor_engine.chess._core import FILES, Board, color_of, square_name
from chess_mentor_engine.chess.features import build_position_features

from ..assertions import (
    KnowledgeAssertion,
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeQualifier,
    KnowledgeSubject,
    build_knowledge_assertion,
)
from ..registry import OntologyRegistry
from .base import DetectorSpec

POSITION_DETECTOR_SPEC = DetectorSpec(
    detector_id="cme.position-knowledge-detector",
    version="1",
    input_kind="position",
    supported_concept_ids=(
        "rule.check",
        "rule.checkmate",
        "tactic.absolute_pin",
        "position.bishop_pair",
        "position.open_file",
        "position.semi_open_file",
        "position.isolated_pawn",
        "position.doubled_pawns",
        "position.passed_pawn",
        "position.pawn_island",
    ),
    claim_scope=(
        "deterministic position-local chess facts only; no strategic evaluation, "
        "participant evidence, or learner inference"
    ),
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def detect_position_knowledge(
    position: CanonicalPosition,
    *,
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> tuple[KnowledgeAssertion, ...]:
    """Detect only the mechanically qualified position concepts in v1."""
    active = OntologyRegistry.load_default() if registry is None else registry
    _validate_spec(active)
    board = Board.from_fen(position.fen)
    if board.turn != position.side_to_move:
        raise ValueError("canonical position side_to_move does not match FEN")
    features = build_position_features(position)
    subject = KnowledgeSubject(
        subject_kind="position",
        position_id=position.position_id,
        game_id=position.game_id,
        ply_index=position.ply_index,
    )
    canonical_ref = KnowledgeEvidenceRef(
        kind="canonical_position",
        ref_id=position.position_id,
        fingerprint=_fingerprint(position.to_dict()),
    )
    feature_ref = KnowledgeEvidenceRef(
        kind="position_features",
        ref_id=f"position-features:{position.position_id}",
        fingerprint=_fingerprint(features.to_dict()),
    )
    provenance = KnowledgeProvenance(
        source_kind="detector",
        source_id=POSITION_DETECTOR_SPEC.detector_id,
        source_version=POSITION_DETECTOR_SPEC.version,
        source_fingerprint=POSITION_DETECTOR_SPEC.fingerprint,
    )

    assertions: list[KnowledgeAssertion] = []

    def add(
        concept_id: str,
        *,
        status: str = "present",
        qualifiers: tuple[KnowledgeQualifier, ...] = (),
        evidence_ref: KnowledgeEvidenceRef = canonical_ref,
    ) -> None:
        concept = active.get(concept_id)
        assertions.append(
            build_knowledge_assertion(
                concept_id=concept_id,
                subject=subject,
                status=status,
                authority_class=concept.default_assertion_authority,
                evidence_refs=(evidence_ref,),
                provenance=provenance,
                qualifiers=qualifiers,
                claim_scope=POSITION_DETECTOR_SPEC.claim_scope,
                created_at=created_at,
                registry=active,
            )
        )

    side = board.turn
    in_check = board.is_in_check(side)
    legal_moves = board.legal_moves()
    side_qualifier = (KnowledgeQualifier(name="color", value=side),)
    add("rule.check", status="present" if in_check else "absent", qualifiers=side_qualifier)
    add(
        "rule.checkmate",
        status="present" if in_check and not legal_moves else "absent",
        qualifiers=side_qualifier,
    )

    for pin in features.absolute_pins:
        add(
            "tactic.absolute_pin",
            qualifiers=(
                KnowledgeQualifier(name="color", value=pin.color),
                KnowledgeQualifier(name="pinned_square", value=pin.pinned_square),
                KnowledgeQualifier(name="king_square", value=pin.king_square),
                KnowledgeQualifier(name="attacker_square", value=pin.attacker_square),
            ),
            evidence_ref=feature_ref,
        )

    for color in ("white", "black"):
        pieces = _piece_squares(board, color)
        if len(pieces["B"]) >= 2:
            add(
                "position.bishop_pair",
                qualifiers=(KnowledgeQualifier(name="color", value=color),),
            )

    pawns_by_color = {
        color: _pawn_squares(board, color) for color in ("white", "black")
    }
    pawn_files = {
        color: {square % 8 for square in squares}
        for color, squares in pawns_by_color.items()
    }

    for file_index, file_name in enumerate(FILES):
        has_white = file_index in pawn_files["white"]
        has_black = file_index in pawn_files["black"]
        if not has_white and not has_black:
            add(
                "position.open_file",
                qualifiers=(KnowledgeQualifier(name="file", value=file_name),),
            )
        if not has_white and has_black:
            add(
                "position.semi_open_file",
                qualifiers=(
                    KnowledgeQualifier(name="color", value="white"),
                    KnowledgeQualifier(name="file", value=file_name),
                ),
            )
        if not has_black and has_white:
            add(
                "position.semi_open_file",
                qualifiers=(
                    KnowledgeQualifier(name="color", value="black"),
                    KnowledgeQualifier(name="file", value=file_name),
                ),
            )

    for color in ("white", "black"):
        pawns = pawns_by_color[color]
        enemy = "black" if color == "white" else "white"
        for square in pawns:
            file_index = square % 8
            if not any(
                adjacent in pawn_files[color]
                for adjacent in (file_index - 1, file_index + 1)
                if 0 <= adjacent < 8
            ):
                add(
                    "position.isolated_pawn",
                    qualifiers=(
                        KnowledgeQualifier(name="color", value=color),
                        KnowledgeQualifier(name="pawn_square", value=square_name(square)),
                    ),
                )
            if _is_passed_pawn(square, color, pawns_by_color[enemy]):
                add(
                    "position.passed_pawn",
                    qualifiers=(
                        KnowledgeQualifier(name="color", value=color),
                        KnowledgeQualifier(name="pawn_square", value=square_name(square)),
                    ),
                )

        for file_index in sorted(pawn_files[color]):
            file_pawns = sorted(
                square_name(square)
                for square in pawns
                if square % 8 == file_index
            )
            if len(file_pawns) >= 2:
                add(
                    "position.doubled_pawns",
                    qualifiers=(
                        KnowledgeQualifier(name="color", value=color),
                        KnowledgeQualifier(name="file", value=FILES[file_index]),
                        KnowledgeQualifier(name="count", value=str(len(file_pawns))),
                        KnowledgeQualifier(name="squares", value=",".join(file_pawns)),
                    ),
                )

        for island in _pawn_islands(pawn_files[color]):
            add(
                "position.pawn_island",
                qualifiers=(
                    KnowledgeQualifier(name="color", value=color),
                    KnowledgeQualifier(
                        name="files", value="".join(FILES[index] for index in island)
                    ),
                ),
            )

    return tuple(assertions)


def _validate_spec(registry: OntologyRegistry) -> None:
    for concept_id in POSITION_DETECTOR_SPEC.supported_concept_ids:
        concept = registry.get(concept_id)
        if concept.detection_support != "deterministic":
            raise ValueError(
                f"position detector cannot claim non-deterministic concept {concept_id}"
            )


def _piece_squares(board: Board, color: str) -> dict[str, tuple[int, ...]]:
    pieces: dict[str, list[int]] = {name: [] for name in "PNBRQK"}
    for square, piece in enumerate(board.squares):
        if piece is None or color_of(piece) != color:
            continue
        pieces[piece.upper()].append(square)
    return {name: tuple(values) for name, values in pieces.items()}


def _pawn_squares(board: Board, color: str) -> tuple[int, ...]:
    pawn = "P" if color == "white" else "p"
    return tuple(square for square, piece in enumerate(board.squares) if piece == pawn)


def _is_passed_pawn(square: int, color: str, enemy_pawns: tuple[int, ...]) -> bool:
    file_index = square % 8
    rank = square // 8
    relevant_files = {value for value in (file_index - 1, file_index, file_index + 1) if 0 <= value < 8}
    for enemy_square in enemy_pawns:
        if enemy_square % 8 not in relevant_files:
            continue
        enemy_rank = enemy_square // 8
        if color == "white" and enemy_rank > rank:
            return False
        if color == "black" and enemy_rank < rank:
            return False
    return True


def _pawn_islands(files_with_pawns: set[int]) -> tuple[tuple[int, ...], ...]:
    if not files_with_pawns:
        return ()
    islands: list[list[int]] = []
    for file_index in sorted(files_with_pawns):
        if not islands or file_index != islands[-1][-1] + 1:
            islands.append([file_index])
        else:
            islands[-1].append(file_index)
    return tuple(tuple(island) for island in islands)
