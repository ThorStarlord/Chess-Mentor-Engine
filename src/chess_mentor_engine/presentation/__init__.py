"""Deterministic UI-safe projections over qualified chess evidence."""

from .evaluation import (
    PRESENTATION_SCHEMA_VERSION,
    EvaluationPresentationError,
    build_evaluation_presentation,
)

__all__ = [
    "PRESENTATION_SCHEMA_VERSION",
    "EvaluationPresentationError",
    "build_evaluation_presentation",
]
