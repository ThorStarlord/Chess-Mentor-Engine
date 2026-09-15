"""Deterministic descriptive summaries of local product-use observations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal

from chess_mentor_engine.storage import LocalArtifactStore

from .model import OBSERVATION_KIND
from .persistence import load_interaction_observation


@dataclass(frozen=True, slots=True)
class ProductUseReport:
    participant_id: str
    total_observations: int
    event_counts: tuple[tuple[str, int], ...]
    action_counts: tuple[tuple[str, int], ...]
    feedback_entries: tuple[tuple[tuple[str, str], ...], ...]
    claim_scope: Literal["descriptive_local_product_use_summary_only"] = (
        "descriptive_local_product_use_summary_only"
    )
    learning_effect: Literal["not_established"] = "not_established"
    tutor_efficacy: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"

    def to_dict(self) -> dict[str, Any]:
        return {
            "participant_id": self.participant_id,
            "total_observations": self.total_observations,
            "event_counts": dict(self.event_counts),
            "action_counts": dict(self.action_counts),
            "feedback_entries": [dict(item) for item in self.feedback_entries],
            "claim_scope": self.claim_scope,
            "learning_effect": self.learning_effect,
            "tutor_efficacy": self.tutor_efficacy,
            "mastery": self.mastery,
        }


def build_product_use_report(
    store: LocalArtifactStore,
    *,
    participant_id: str,
) -> ProductUseReport:
    refs = store.list_refs(participant_id=participant_id, kind=OBSERVATION_KIND)
    observations = tuple(
        sorted(
            (
                load_interaction_observation(
                    store,
                    ref,
                    participant_id=participant_id,
                )
                for ref in refs
            ),
            key=lambda item: (item.occurred_at, item.observation_id),
        )
    )
    event_counts = Counter(item.event_type for item in observations)
    action_counts = Counter(
        item.action for item in observations if item.action is not None
    )
    feedback = tuple(
        item.metadata
        for item in observations
        if item.event_type == "participant_feedback"
    )
    return ProductUseReport(
        participant_id=participant_id,
        total_observations=len(observations),
        event_counts=tuple(sorted(event_counts.items())),
        action_counts=tuple(sorted(action_counts.items())),
        feedback_entries=feedback,
    )
