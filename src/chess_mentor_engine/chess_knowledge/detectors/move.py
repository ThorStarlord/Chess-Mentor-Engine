"""Conservative deterministic move-level chess-knowledge detection."""

from __future__ import annotations

import hashlib

from chess_mentor_engine.chess import CanonicalPosition, canonical_json
from chess_mentor_engine.chess._core import Board, Move, color_of, opposite, square_name
from chess_mentor_engine.chess.features import _attacker_squares

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

MOVE_DETECTOR_SPEC = DetectorSpec(
    detector_id="cme.move-knowledge-detector",
    version="1",
    input_kind="move",
    supported_concept_ids=(
        "tactic.promotion",
        "tactic.underpromotion",
        "tactic.fork",
        "tactic.discovered_check",
        "tactic.double_check",
    ),
    claim_scope=(
        "deterministic legal-move transition patterns only; no strategic evaluation, "
        "participant evidence, or learner inference"
    ),
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def detect_move_knowledge(
    position: CanonicalPosition,
    move_uci: str,
    *,
    created_at: str,
    registry: OntologyRegistry | None = None,
) -> tuple[KnowledgeAssertion, ...]:
    """Detect mechanically provable v1 concepts created by one legal move."""
    active = OntologyRegistry.load_default() if registry is None else registry
    _validate_spec(active)
    before = Board.from_fen(position.fen)
    if before.turn != position.side_to_move:
        raise ValueError("canonical position side_to_move does not match FEN")
    move = _find_legal_move(before, move_uci)
    if move is None:
        raise ValueError(f"illegal move for knowledge detection: {move_uci}")

    moving_piece = before.squares[move.from_square]
    if moving_piece is None:
        raise ValueError("legal move has no source piece")
    moving_color = color_of(moving_piece)
    opponent = opposite(moving_color)
    opponent_king_before = before._king_square(opponent)
    if opponent_king_before is None:
        raise ValueError("position must contain opponent king")
    before_attackers = set(
        _attacker_squares(before, opponent_king_before, moving_color)
    )

    after = before.copy()
    after.push(move)
    opponent_king_after = after._king_square(opponent)
    if opponent_king_after is None:
        raise ValueError("move transition removed opponent king")
    after_attackers = set(_attacker_squares(after, opponent_king_after, moving_color))

    subject = KnowledgeSubject(
        subject_kind="move",
        position_id=position.position_id,
        game_id=position.game_id,
        ply_index=position.ply_index,
        move_uci=move_uci,
    )
    evidence_payload = {
        "position": position.to_dict(),
        "move_uci": move_uci,
        "resulting_fen": after.fen(),
    }
    evidence_ref = KnowledgeEvidenceRef(
        kind="move_sequence",
        ref_id=f"move:{position.position_id}:{move_uci}",
        fingerprint=_fingerprint(evidence_payload),
    )
    provenance = KnowledgeProvenance(
        source_kind="detector",
        source_id=MOVE_DETECTOR_SPEC.detector_id,
        source_version=MOVE_DETECTOR_SPEC.version,
        source_fingerprint=MOVE_DETECTOR_SPEC.fingerprint,
    )

    assertions: list[KnowledgeAssertion] = []

    def add(
        concept_id: str,
        *,
        qualifiers: tuple[KnowledgeQualifier, ...] = (),
    ) -> None:
        concept = active.get(concept_id)
        assertions.append(
            build_knowledge_assertion(
                concept_id=concept_id,
                subject=subject,
                status="present",
                authority_class=concept.default_assertion_authority,
                evidence_refs=(evidence_ref,),
                provenance=provenance,
                qualifiers=qualifiers,
                claim_scope=MOVE_DETECTOR_SPEC.claim_scope,
                created_at=created_at,
                registry=active,
            )
        )

    if move.promotion is not None:
        add(
            "tactic.promotion",
            qualifiers=(
                KnowledgeQualifier(name="promotion_piece", value=move.promotion),
            ),
        )
        if move.promotion in {"r", "b", "n"}:
            add(
                "tactic.underpromotion",
                qualifiers=(
                    KnowledgeQualifier(name="promotion_piece", value=move.promotion),
                ),
            )

    fork_targets = _attacked_enemy_piece_squares(
        after,
        attacker_square=move.to_square,
        attacker_color=moving_color,
    )
    if len(fork_targets) >= 2:
        add(
            "tactic.fork",
            qualifiers=(
                KnowledgeQualifier(
                    name="attacker_square", value=square_name(move.to_square)
                ),
                KnowledgeQualifier(name="target_count", value=str(len(fork_targets))),
                KnowledgeQualifier(
                    name="target_squares",
                    value=",".join(square_name(square) for square in fork_targets),
                ),
            ),
        )

    new_uncovered_checkers = tuple(
        sorted(
            square
            for square in after_attackers
            if square != move.to_square and square not in before_attackers
        )
    )
    if new_uncovered_checkers:
        add(
            "tactic.discovered_check",
            qualifiers=(
                KnowledgeQualifier(
                    name="uncovered_checker_squares",
                    value=",".join(
                        square_name(square) for square in new_uncovered_checkers
                    ),
                ),
            ),
        )

    if len(after_attackers) >= 2:
        add(
            "tactic.double_check",
            qualifiers=(
                KnowledgeQualifier(
                    name="checker_squares",
                    value=",".join(
                        square_name(square) for square in sorted(after_attackers)
                    ),
                ),
            ),
        )

    return tuple(assertions)


def _validate_spec(registry: OntologyRegistry) -> None:
    for concept_id in MOVE_DETECTOR_SPEC.supported_concept_ids:
        concept = registry.get(concept_id)
        if concept.detection_support != "sequence_based":
            raise ValueError(
                f"move detector cannot claim non-sequence concept {concept_id}"
            )


def _find_legal_move(board: Board, move_uci: str) -> Move | None:
    for move in board.legal_moves():
        if move.uci() == move_uci:
            return move
    return None


def _attacked_enemy_piece_squares(
    board: Board,
    *,
    attacker_square: int,
    attacker_color: str,
) -> tuple[int, ...]:
    targets: list[int] = []
    for target_square, piece in enumerate(board.squares):
        if piece is None or color_of(piece) == attacker_color:
            continue
        attackers = _attacker_squares(board, target_square, attacker_color)
        if attacker_square in attackers:
            targets.append(target_square)
    return tuple(sorted(targets))
