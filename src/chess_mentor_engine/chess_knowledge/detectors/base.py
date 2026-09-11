"""Shared metadata and identity for deterministic chess-knowledge detectors."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from chess_mentor_engine.chess import canonical_json

DetectorInputKind: TypeAlias = Literal["position", "move"]


@dataclass(frozen=True, slots=True)
class DetectorSpec:
    detector_id: str
    version: str
    input_kind: DetectorInputKind
    supported_concept_ids: tuple[str, ...]
    claim_scope: str

    def __post_init__(self) -> None:
        if not self.detector_id or not self.detector_id.strip():
            raise ValueError("detector_id must not be empty")
        if not self.version or not self.version.strip():
            raise ValueError("detector version must not be empty")
        if self.input_kind not in {"position", "move"}:
            raise ValueError("unknown detector input kind")
        if not self.supported_concept_ids:
            raise ValueError("detector must declare at least one supported concept")
        if len(set(self.supported_concept_ids)) != len(self.supported_concept_ids):
            raise ValueError("detector concept IDs must be unique")
        if any(not value or not value.strip() for value in self.supported_concept_ids):
            raise ValueError("detector concept IDs must not be empty")
        if not self.claim_scope or not self.claim_scope.strip():
            raise ValueError("detector claim_scope must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "detector_id": self.detector_id,
            "version": self.version,
            "input_kind": self.input_kind,
            "supported_concept_ids": list(self.supported_concept_ids),
            "claim_scope": self.claim_scope,
        }

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            canonical_json(self.to_dict()).encode("utf-8")
        ).hexdigest()
