"""Qualified chess-knowledge detector surfaces."""

from .base import DetectorSpec
from .move import MOVE_DETECTOR_SPEC, detect_move_knowledge
from .position import POSITION_DETECTOR_SPEC, detect_position_knowledge

__all__ = [
    "DetectorSpec",
    "MOVE_DETECTOR_SPEC",
    "POSITION_DETECTOR_SPEC",
    "detect_move_knowledge",
    "detect_position_knowledge",
]
