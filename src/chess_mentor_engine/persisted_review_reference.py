"""M29 persisted M26/M25 to M28 reference-surface bridge."""

from __future__ import annotations

from dataclasses import dataclass

from chess_mentor_engine.coach_review_reference import (
    CoachReviewReferenceSurface,
    render_coach_review_reference_surface,
)
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import M26_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import (
    M27_SCHEMA_VERSION,
    ReviewedCoachingExecutionLedgerResult,
    build_reviewed_coaching_execution_ledger,
)
from chess_mentor_engine.storage import ArtifactRef, LocalArtifactStore, StoredArtifact

M29_SCHEMA_VERSION = "m29.persisted-coach-review-reference-bridge.v1"
M29_CLAIM_SCOPE = "repository_local_persisted_review_reference_bridge"

_SOURCE_FINGERPRINT_ORDER = (
    "objective_evidence",
    "diagnostic_candidate",
    "diagnostic_batch",
    "authorization",
    "launch",
    "tutor_state",
    "deterministic_grounding",
    "model_coaching",
    "model_evaluation",
)


class PersistedReviewReferenceError(ValueError):
    """M29 cannot resolve one mechanically verified persisted review chain."""


@dataclass(frozen=True, slots=True)
class PersistedReviewReferenceResult:
    """Exact persisted sources, M27 verification, and the resulting M28 surface."""

    run_ref: ArtifactRef
    review_ref: ArtifactRef
    ledger: ReviewedCoachingExecutionLedgerResult
    surface: CoachReviewReferenceSurface


def _find_ref(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    kind: str,
    artifact_id: str,
    label: str,
) -> ArtifactRef:
    matches = tuple(
        ref
        for ref in store.list_refs(participant_id=participant_id, kind=kind)
        if ref.artifact_id == artifact_id
    )
    if len(matches) != 1:
        raise PersistedReviewReferenceError(
            f"{label} must resolve exactly one participant-scoped artifact"
        )
    return matches[0]


def _one_dependency(
    artifact: StoredArtifact,
    *,
    kind: str,
    label: str,
) -> ArtifactRef:
    matches = tuple(ref for ref in artifact.dependencies if ref.kind == kind)
    if len(matches) != 1:
        raise PersistedReviewReferenceError(
            f"{label} must resolve exactly one {kind} dependency"
        )
    return matches[0]


def _review_from_run(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    run_ref: ArtifactRef,
) -> ArtifactRef:
    run_artifact = store.get(run_ref, participant_id=participant_id)
    return _one_dependency(
        run_artifact,
        kind=COACH_REVIEW_SCHEMA_VERSION,
        label="M26 run",
    )


def _run_from_review(
    store: LocalArtifactStore,
    *,
    participant_id: str,
    review_ref: ArtifactRef,
) -> ArtifactRef:
    matches: list[ArtifactRef] = []
    for run_ref in store.list_refs(
        participant_id=participant_id,
        kind=M26_SCHEMA_VERSION,
    ):
        run_artifact = store.get(run_ref, participant_id=participant_id)
        if review_ref in run_artifact.dependencies:
            matches.append(run_ref)
    if len(matches) != 1:
        raise PersistedReviewReferenceError(
            "M25 review must be backed by exactly one participant-scoped M26 run"
        )
    return matches[0]


def _m28_read_model(read_model: dict) -> dict:
    """Restore M25's explicit fingerprint order after canonical JSON persistence."""
    fingerprints = read_model.get("source_fingerprints")
    if type(fingerprints) is not dict:
        raise PersistedReviewReferenceError("M25 source fingerprints are malformed")
    if set(fingerprints) != set(_SOURCE_FINGERPRINT_ORDER):
        raise PersistedReviewReferenceError("M25 source fingerprint keys drifted")
    ordered = dict(read_model)
    ordered["source_fingerprints"] = {
        key: fingerprints[key] for key in _SOURCE_FINGERPRINT_ORDER
    }
    return ordered


def build_persisted_coach_review_reference(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    run_artifact_id: str | None = None,
    review_artifact_id: str | None = None,
) -> PersistedReviewReferenceResult:
    """Verify one persisted reviewed-coaching chain and render its exact M25 review."""
    if not participant_id:
        raise PersistedReviewReferenceError("participant_id must not be empty")
    if (run_artifact_id is None) == (review_artifact_id is None):
        raise PersistedReviewReferenceError(
            "provide exactly one of run_artifact_id or review_artifact_id"
        )

    if run_artifact_id is not None:
        run_ref = _find_ref(
            store,
            participant_id=participant_id,
            kind=M26_SCHEMA_VERSION,
            artifact_id=run_artifact_id,
            label="M26 run",
        )
        review_ref = _review_from_run(
            store,
            participant_id=participant_id,
            run_ref=run_ref,
        )
    else:
        assert review_artifact_id is not None
        review_ref = _find_ref(
            store,
            participant_id=participant_id,
            kind=COACH_REVIEW_SCHEMA_VERSION,
            artifact_id=review_artifact_id,
            label="M25 review",
        )
        run_ref = _run_from_review(
            store,
            participant_id=participant_id,
            review_ref=review_ref,
        )

    ledger = build_reviewed_coaching_execution_ledger(
        store=store,
        participant_id=participant_id,
        run_artifact_ids=(run_ref.artifact_id,),
    )
    if ledger.ledger_record.get("schema_version") != M27_SCHEMA_VERSION:
        raise PersistedReviewReferenceError("M27 ledger schema mismatch")
    runs = ledger.ledger_record.get("runs")
    if type(runs) is not list or len(runs) != 1:
        raise PersistedReviewReferenceError("M27 ledger must verify exactly one M26 run")
    entry = runs[0]
    if type(entry) is not dict:
        raise PersistedReviewReferenceError("M27 run entry is malformed")
    fidelity = entry.get("fidelity")
    if (
        type(fidelity) is not dict
        or fidelity.get("status") != "mechanically_verified"
    ):
        raise PersistedReviewReferenceError("M27 mechanical verification is absent")
    if entry.get("run_ref") != run_ref.to_dict():
        raise PersistedReviewReferenceError("M27 verified a different M26 run")
    if entry.get("coach_review_ref") != review_ref.to_dict():
        raise PersistedReviewReferenceError("M27 verified a different M25 review")

    review_artifact = store.get(review_ref, participant_id=participant_id)
    surface = render_coach_review_reference_surface(
        _m28_read_model(review_artifact.payload)
    )
    if surface.read_model != review_artifact.payload:
        raise PersistedReviewReferenceError("M28 did not preserve the exact M25 payload")

    return PersistedReviewReferenceResult(
        run_ref=run_ref,
        review_ref=review_ref,
        ledger=ledger,
        surface=surface,
    )
