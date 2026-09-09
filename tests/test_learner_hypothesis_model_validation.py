from __future__ import annotations

import pytest

from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    HypothesisEvidenceLink,
    HypothesisLifecycleEvent,
    HypothesisM6EvidenceRef,
    HypothesisMappingProvenance,
    HypothesisRevisionRef,
    LearnerHypothesisRef,
)


def _actor() -> HypothesisActorProvenance:
    return HypothesisActorProvenance(
        actor_kind="human",
        actor_id="analyst",
        actor_version="v1",
        rubric_or_instruction_fingerprint="rubric-v1",
        run_id="run-1",
    )


def test_actor_provenance_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="actor kind"):
        HypothesisActorProvenance(
            actor_kind="unknown",  # type: ignore[arg-type]
            actor_id="analyst",
            actor_version="v1",
            rubric_or_instruction_fingerprint="rubric-v1",
        )


def test_mapping_provenance_rejects_unknown_basis_kind() -> None:
    with pytest.raises(ValueError, match="mapping basis"):
        HypothesisMappingProvenance(
            basis_kind="unknown",  # type: ignore[arg-type]
            ref_id="mapping-1",
            fingerprint="mapping-fingerprint",
        )


def test_m6_reference_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="M6 hypothesis-evidence"):
        HypothesisM6EvidenceRef(
            kind="unknown",  # type: ignore[arg-type]
            ref_id="ref-1",
            fingerprint="fingerprint-1",
        )


def test_lifecycle_record_rejects_unknown_kind() -> None:
    hypothesis_ref = LearnerHypothesisRef(
        hypothesis_id="hypothesis-1",
        participant_id="P01",
        fingerprint="hypothesis-fingerprint",
    )
    with pytest.raises(ValueError, match="lifecycle event kind"):
        HypothesisLifecycleEvent(
            lifecycle_event_id="event-1",
            fingerprint="event-fingerprint",
            hypothesis_ref=hypothesis_ref,
            kind="unknown",  # type: ignore[arg-type]
            superseding_hypothesis_ref=None,
            reason="invalid",
            author_provenance=_actor(),
            created_at="2026-09-09T05:00:00+00:00",
        )


def _valid_link_kwargs() -> dict[str, object]:
    return {
        "link_id": "link-1",
        "fingerprint": "link-fingerprint",
        "hypothesis_revision_ref": HypothesisRevisionRef(
            revision_id="revision-1",
            hypothesis_id="hypothesis-1",
            revision_number=1,
            fingerprint="revision-fingerprint",
        ),
        "participant_id": "P01",
        "reasoning_context_ref": HypothesisM6EvidenceRef(
            kind="reasoning_context",
            ref_id="context-1",
            fingerprint="context-fingerprint",
        ),
        "assessment_ref": HypothesisM6EvidenceRef(
            kind="reasoning_assessment",
            ref_id="assessment-1",
            fingerprint="assessment-fingerprint",
        ),
        "assertion_refs": (),
        "source_position_id": "position-1",
        "source_game_id": "game-1",
        "relation": "supports",
        "context_refs": (),
        "measurement_condition": "clean",
        "basis_kind": "deterministic_mapping",
        "mapping_provenance": HypothesisMappingProvenance(
            basis_kind="deterministic_mapping",
            ref_id="mapping-1",
            fingerprint="mapping-fingerprint",
        ),
        "created_at": "2026-09-09T05:00:00+00:00",
    }


def test_evidence_link_record_rejects_unknown_relation() -> None:
    kwargs = _valid_link_kwargs()
    kwargs["relation"] = "unknown"
    with pytest.raises(ValueError, match="evidence relation"):
        HypothesisEvidenceLink(**kwargs)  # type: ignore[arg-type]


def test_evidence_link_record_rejects_unknown_measurement_condition() -> None:
    kwargs = _valid_link_kwargs()
    kwargs["measurement_condition"] = "unknown-condition"
    with pytest.raises(ValueError, match="measurement condition"):
        HypothesisEvidenceLink(**kwargs)  # type: ignore[arg-type]
