"""M30 participant-scoped review package manifests and navigation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_reference import (
    M28_SCHEMA_VERSION,
    CoachReviewReferenceSurface,
)
from chess_mentor_engine.persisted_review_reference import (
    build_persisted_coach_review_reference,
)
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching import M26_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import M27_SCHEMA_VERSION
from chess_mentor_engine.storage import (
    ArtifactRef,
    ArtifactWrite,
    LocalArtifactStore,
    StoredArtifact,
    prepare_artifact,
)

M30_SCHEMA_VERSION = "m30.participant-review-package.v1"
M30_INDEX_SCHEMA_VERSION = "m30.participant-review-navigation-index.v1"
M30_SHOW_SCHEMA_VERSION = "m30.participant-review-navigation-item.v1"
M30_CLAIM_SCOPE = "repository_local_participant_review_package_navigation"

_PRIVACY_CONTRACT = {
    "summary_contains_source_payloads": False,
    "summary_contains_model_rendered_content": False,
    "summary_contains_evaluator_rationales": False,
    "summary_contains_participant_response_content": False,
    "summary_contains_reference_html": False,
    "exact_content_requires_explicit_show_or_export": True,
}

_AUTHORITY_BOUNDARY = {
    "executes_external_calls": False,
    "chooses_production_provider": False,
    "advances_tutor_state": False,
    "creates_objective_chess_facts": False,
    "establishes_model_output_truth": False,
    "claims_pedagogical_quality": False,
    "claims_production_ui_quality": False,
}

_MANIFEST_KEYS = {
    "schema_version",
    "participant_id",
    "source_refs",
    "source_fingerprints",
    "reference_surface",
    "execution_summary",
    "privacy_contract",
    "claim_scope",
    "authority_boundary",
    "package_id",
    "fingerprint",
}

_SOURCE_REF_KEYS = {"m26_run", "m25_review", "m27_ledger"}
_ITEM_KIND_TO_SCHEMA = {
    "run": M26_SCHEMA_VERSION,
    "review": COACH_REVIEW_SCHEMA_VERSION,
    "ledger": M27_SCHEMA_VERSION,
    "package": M30_SCHEMA_VERSION,
}


class ParticipantReviewPackageError(ValueError):
    """M30 cannot safely navigate or package the participant review chain."""


@dataclass(frozen=True, slots=True)
class ParticipantReviewPackageResult:
    """One persisted M30 manifest plus its verified M28 reference surface."""

    manifest_record: dict[str, Any]
    manifest_ref: ArtifactRef
    run_ref: ArtifactRef
    review_ref: ArtifactRef
    ledger_ref: ArtifactRef
    surface: CoachReviewReferenceSurface


@dataclass(frozen=True, slots=True)
class LoadedParticipantReviewPackage:
    """One verified persisted M30 manifest and its exact source references."""

    manifest_record: dict[str, Any]
    manifest_ref: ArtifactRef
    run_ref: ArtifactRef
    review_ref: ArtifactRef
    ledger_ref: ArtifactRef


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ParticipantReviewPackageError(f"{label} must not be empty")
    return value


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
        raise ParticipantReviewPackageError(
            f"{label} must resolve exactly one participant-scoped artifact"
        )
    return matches[0]


def _ref_from_dict(value: Any, *, label: str) -> ArtifactRef:
    if type(value) is not dict:
        raise ParticipantReviewPackageError(f"{label} must be an artifact reference")
    try:
        return ArtifactRef(**value)
    except (TypeError, ValueError, KeyError) as exc:
        raise ParticipantReviewPackageError(
            f"{label} must be an exact artifact reference"
        ) from exc


def _manifest_payload(
    *,
    participant_id: str,
    run_ref: ArtifactRef,
    review_ref: ArtifactRef,
    ledger_ref: ArtifactRef,
    read_model: dict[str, Any],
    surface: CoachReviewReferenceSurface,
    execution_summary: dict[str, Any],
) -> dict[str, Any]:
    source_fingerprints = read_model.get("source_fingerprints")
    if type(source_fingerprints) is not dict:
        raise ParticipantReviewPackageError("M25 source fingerprints are malformed")
    read_model_fingerprint = _nonempty(
        read_model.get("fingerprint"),
        "M25 read-model fingerprint",
    )
    read_model_id = _nonempty(read_model.get("read_model_id"), "M25 read-model id")
    return {
        "schema_version": M30_SCHEMA_VERSION,
        "participant_id": participant_id,
        "source_refs": {
            "m26_run": run_ref.to_dict(),
            "m25_review": review_ref.to_dict(),
            "m27_ledger": ledger_ref.to_dict(),
        },
        "source_fingerprints": {
            "m26_artifact_digest": run_ref.digest,
            "m25_artifact_digest": review_ref.digest,
            "m27_artifact_digest": ledger_ref.digest,
            "m25_read_model_fingerprint": read_model_fingerprint,
            "m25_source_fingerprints": source_fingerprints,
            "m28_surface_fingerprint": surface.fingerprint,
        },
        "reference_surface": {
            "schema_version": M28_SCHEMA_VERSION,
            "surface_id": surface.surface_id,
            "fingerprint": surface.fingerprint,
            "m25_read_model_id": read_model_id,
            "m25_read_model_fingerprint": read_model_fingerprint,
            "html_in_manifest": False,
        },
        "execution_summary": execution_summary,
        "privacy_contract": dict(_PRIVACY_CONTRACT),
        "claim_scope": M30_CLAIM_SCOPE,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def build_participant_review_package(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    run_artifact_id: str | None = None,
    review_artifact_id: str | None = None,
) -> ParticipantReviewPackageResult:
    """Verify one persisted chain and persist a summary-safe M30 manifest."""
    _nonempty(participant_id, "participant_id")
    bridged = build_persisted_coach_review_reference(
        store=store,
        participant_id=participant_id,
        run_artifact_id=run_artifact_id,
        review_artifact_id=review_artifact_id,
    )
    summary = bridged.ledger.ledger_record.get("summary")
    if type(summary) is not dict:
        raise ParticipantReviewPackageError("M27 execution summary is malformed")
    payload = _manifest_payload(
        participant_id=participant_id,
        run_ref=bridged.run_ref,
        review_ref=bridged.review_ref,
        ledger_ref=bridged.ledger.ledger_ref,
        read_model=bridged.surface.read_model,
        surface=bridged.surface,
        execution_summary=summary,
    )
    fingerprint = _fingerprint(payload)
    manifest = {
        **payload,
        "package_id": f"participant_review_package_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }
    write = ArtifactWrite(
        M30_SCHEMA_VERSION,
        manifest["package_id"],
        participant_id,
        manifest,
        (bridged.run_ref, bridged.review_ref, bridged.ledger.ledger_ref),
    )
    manifest_ref = prepare_artifact(write)[0]
    store.put_many((write,))
    return ParticipantReviewPackageResult(
        manifest_record=manifest,
        manifest_ref=manifest_ref,
        run_ref=bridged.run_ref,
        review_ref=bridged.review_ref,
        ledger_ref=bridged.ledger.ledger_ref,
        surface=bridged.surface,
    )


def _validate_manifest_identity(record: Any, *, participant_id: str) -> None:
    if type(record) is not dict or set(record) != _MANIFEST_KEYS:
        raise ParticipantReviewPackageError("M30 manifest shape mismatch")
    if record["schema_version"] != M30_SCHEMA_VERSION:
        raise ParticipantReviewPackageError("M30 manifest schema mismatch")
    if record["participant_id"] != participant_id:
        raise ParticipantReviewPackageError("M30 participant scope drifted")
    if record["privacy_contract"] != _PRIVACY_CONTRACT:
        raise ParticipantReviewPackageError("M30 privacy contract drifted")
    if record["authority_boundary"] != _AUTHORITY_BOUNDARY:
        raise ParticipantReviewPackageError("M30 authority boundary drifted")
    if record["claim_scope"] != M30_CLAIM_SCOPE:
        raise ParticipantReviewPackageError("M30 claim scope drifted")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"package_id", "fingerprint"}
    }
    expected = _fingerprint(payload)
    if record["fingerprint"] != expected:
        raise ParticipantReviewPackageError("M30 manifest fingerprint mismatch")
    if record["package_id"] != f"participant_review_package_{expected[:20]}":
        raise ParticipantReviewPackageError("M30 manifest identity mismatch")


def _validate_loaded_package(
    store: LocalArtifactStore,
    artifact: StoredArtifact,
    *,
    participant_id: str,
) -> LoadedParticipantReviewPackage:
    record = artifact.payload
    _validate_manifest_identity(record, participant_id=participant_id)
    refs = record["source_refs"]
    if type(refs) is not dict or set(refs) != _SOURCE_REF_KEYS:
        raise ParticipantReviewPackageError("M30 source reference set drifted")
    run_ref = _ref_from_dict(refs["m26_run"], label="M30 M26 run reference")
    review_ref = _ref_from_dict(
        refs["m25_review"],
        label="M30 M25 review reference",
    )
    ledger_ref = _ref_from_dict(
        refs["m27_ledger"],
        label="M30 M27 ledger reference",
    )
    expected_kinds = (
        (run_ref, M26_SCHEMA_VERSION, "M26"),
        (review_ref, COACH_REVIEW_SCHEMA_VERSION, "M25"),
        (ledger_ref, M27_SCHEMA_VERSION, "M27"),
    )
    for ref, kind, label in expected_kinds:
        if ref.kind != kind:
            raise ParticipantReviewPackageError(f"M30 {label} source kind drifted")
        if ref.participant_id != participant_id:
            raise ParticipantReviewPackageError(f"M30 {label} participant drifted")
    if {ref.digest for ref in artifact.dependencies} != {
        run_ref.digest,
        review_ref.digest,
        ledger_ref.digest,
    }:
        raise ParticipantReviewPackageError("M30 dependency set drifted")

    run_artifact = store.get(run_ref, participant_id=participant_id)
    if review_ref not in run_artifact.dependencies:
        raise ParticipantReviewPackageError("M30 M26/M25 dependency drifted")
    review_artifact = store.get(review_ref, participant_id=participant_id)
    ledger_artifact = store.get(ledger_ref, participant_id=participant_id)
    ledger = ledger_artifact.payload
    runs = ledger.get("runs")
    if (
        ledger.get("schema_version") != M27_SCHEMA_VERSION
        or ledger.get("run_count") != 1
        or type(runs) is not list
        or len(runs) != 1
        or type(runs[0]) is not dict
    ):
        raise ParticipantReviewPackageError("M30 requires one-run M27 ledger")
    ledger_entry = runs[0]
    if ledger_entry.get("run_ref") != run_ref.to_dict():
        raise ParticipantReviewPackageError("M30 M27/M26 reference drifted")
    if ledger_entry.get("coach_review_ref") != review_ref.to_dict():
        raise ParticipantReviewPackageError("M30 M27/M25 reference drifted")
    fidelity = ledger_entry.get("fidelity")
    if type(fidelity) is not dict or fidelity.get("status") != "mechanically_verified":
        raise ParticipantReviewPackageError("M30 M27 verification is absent")

    fingerprints = record["source_fingerprints"]
    if type(fingerprints) is not dict:
        raise ParticipantReviewPackageError("M30 source fingerprints are malformed")
    expected_fingerprints = {
        "m26_artifact_digest": run_ref.digest,
        "m25_artifact_digest": review_ref.digest,
        "m27_artifact_digest": ledger_ref.digest,
        "m25_read_model_fingerprint": review_artifact.payload.get("fingerprint"),
        "m25_source_fingerprints": review_artifact.payload.get(
            "source_fingerprints"
        ),
        "m28_surface_fingerprint": record["reference_surface"].get("fingerprint"),
    }
    if fingerprints != expected_fingerprints:
        raise ParticipantReviewPackageError("M30 source fingerprints drifted")
    surface = record["reference_surface"]
    if type(surface) is not dict:
        raise ParticipantReviewPackageError("M30 reference surface is malformed")
    expected_surface = {
        "schema_version": M28_SCHEMA_VERSION,
        "surface_id": surface.get("surface_id"),
        "fingerprint": surface.get("fingerprint"),
        "m25_read_model_id": review_artifact.payload.get("read_model_id"),
        "m25_read_model_fingerprint": review_artifact.payload.get("fingerprint"),
        "html_in_manifest": False,
    }
    if surface != expected_surface:
        raise ParticipantReviewPackageError("M30 M28 surface metadata drifted")
    if record["execution_summary"] != ledger.get("summary"):
        raise ParticipantReviewPackageError("M30 M27 execution summary drifted")
    return LoadedParticipantReviewPackage(
        manifest_record=record,
        manifest_ref=artifact.ref,
        run_ref=run_ref,
        review_ref=review_ref,
        ledger_ref=ledger_ref,
    )


def load_participant_review_package(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    package_artifact_id: str,
) -> LoadedParticipantReviewPackage:
    """Load and mechanically cross-check one persisted M30 package manifest."""
    _nonempty(participant_id, "participant_id")
    package_ref = _find_ref(
        store,
        participant_id=participant_id,
        kind=M30_SCHEMA_VERSION,
        artifact_id=package_artifact_id,
        label="M30 package",
    )
    artifact = store.get(package_ref, participant_id=participant_id)
    return _validate_loaded_package(
        store,
        artifact,
        participant_id=participant_id,
    )


def render_participant_review_package_surface(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    package_artifact_id: str,
) -> CoachReviewReferenceSurface:
    """Re-render a package's exact M28 surface and verify its manifest identity."""
    loaded = load_participant_review_package(
        store=store,
        participant_id=participant_id,
        package_artifact_id=package_artifact_id,
    )
    bridged = build_persisted_coach_review_reference(
        store=store,
        participant_id=participant_id,
        run_artifact_id=loaded.run_ref.artifact_id,
    )
    expected = loaded.manifest_record["reference_surface"]
    if (
        bridged.review_ref != loaded.review_ref
        or bridged.ledger.ledger_ref != loaded.ledger_ref
        or bridged.surface.surface_id != expected["surface_id"]
        or bridged.surface.fingerprint != expected["fingerprint"]
    ):
        raise ParticipantReviewPackageError(
            "M30 package surface reconstruction drifted"
        )
    return bridged.surface


def list_participant_review_navigation(
    *,
    store: LocalArtifactStore,
    participant_id: str,
) -> dict[str, Any]:
    """Build a deterministic, payload-free participant-scoped review index."""
    _nonempty(participant_id, "participant_id")
    run_refs = store.list_refs(participant_id=participant_id, kind=M26_SCHEMA_VERSION)
    review_refs = store.list_refs(
        participant_id=participant_id,
        kind=COACH_REVIEW_SCHEMA_VERSION,
    )
    ledger_refs = store.list_refs(
        participant_id=participant_id,
        kind=M27_SCHEMA_VERSION,
    )
    package_refs = store.list_refs(
        participant_id=participant_id,
        kind=M30_SCHEMA_VERSION,
    )

    ledger_dependencies = {
        ref.digest: store.get(ref, participant_id=participant_id).dependencies
        for ref in ledger_refs
    }
    packages = [
        _validate_loaded_package(
            store,
            store.get(ref, participant_id=participant_id),
            participant_id=participant_id,
        )
        for ref in package_refs
    ]

    runs: list[dict[str, Any]] = []
    for run_ref in run_refs:
        run = store.get(run_ref, participant_id=participant_id)
        linked_reviews = [
            ref.to_dict()
            for ref in run.dependencies
            if ref.kind == COACH_REVIEW_SCHEMA_VERSION
        ]
        linked_ledgers = [
            ref.to_dict()
            for ref in ledger_refs
            if run_ref in ledger_dependencies[ref.digest]
        ]
        linked_packages = [item for item in packages if item.run_ref == run_ref]
        runs.append(
            {
                "run_ref": run_ref.to_dict(),
                "coach_review_refs": linked_reviews,
                "ledger_refs": linked_ledgers,
                "package_refs": [
                    item.manifest_ref.to_dict() for item in linked_packages
                ],
                "reference_surfaces": [
                    item.manifest_record["reference_surface"]
                    for item in linked_packages
                ],
            }
        )

    package_entries = [
        {
            "package_ref": item.manifest_ref.to_dict(),
            "run_ref": item.run_ref.to_dict(),
            "review_ref": item.review_ref.to_dict(),
            "ledger_ref": item.ledger_ref.to_dict(),
            "reference_surface": item.manifest_record["reference_surface"],
        }
        for item in packages
    ]
    return {
        "schema_version": M30_INDEX_SCHEMA_VERSION,
        "participant_id": participant_id,
        "runs": runs,
        "review_refs": [ref.to_dict() for ref in review_refs],
        "ledger_refs": [ref.to_dict() for ref in ledger_refs],
        "packages": package_entries,
        "counts": {
            "runs": len(run_refs),
            "reviews": len(review_refs),
            "ledgers": len(ledger_refs),
            "packages": len(package_refs),
            "reference_surfaces": len(packages),
        },
        "privacy_contract": dict(_PRIVACY_CONTRACT),
        "claim_scope": M30_CLAIM_SCOPE,
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
    }


def show_participant_review_item(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    item_type: str,
    artifact_id: str,
    include_content: bool = False,
) -> dict[str, Any]:
    """Show one exact review item; payload/HTML requires explicit opt-in."""
    _nonempty(participant_id, "participant_id")
    _nonempty(artifact_id, "artifact_id")
    if item_type == "surface":
        loaded = load_participant_review_package(
            store=store,
            participant_id=participant_id,
            package_artifact_id=artifact_id,
        )
        result: dict[str, Any] = {
            "schema_version": M30_SHOW_SCHEMA_VERSION,
            "participant_id": participant_id,
            "item_type": "surface",
            "package_ref": loaded.manifest_ref.to_dict(),
            "reference_surface": loaded.manifest_record["reference_surface"],
            "content_included": include_content,
            "claim_scope": M30_CLAIM_SCOPE,
        }
        if include_content:
            result["html"] = render_participant_review_package_surface(
                store=store,
                participant_id=participant_id,
                package_artifact_id=artifact_id,
            ).html
        return result

    schema = _ITEM_KIND_TO_SCHEMA.get(item_type)
    if schema is None:
        raise ParticipantReviewPackageError(
            "item_type must be run, review, ledger, package, or surface"
        )
    ref = _find_ref(
        store,
        participant_id=participant_id,
        kind=schema,
        artifact_id=artifact_id,
        label=f"M30 {item_type}",
    )
    artifact = store.get(ref, participant_id=participant_id)
    result = {
        "schema_version": M30_SHOW_SCHEMA_VERSION,
        "participant_id": participant_id,
        "item_type": item_type,
        "artifact_ref": ref.to_dict(),
        "dependency_refs": [dep.to_dict() for dep in artifact.dependencies],
        "content_included": include_content,
        "claim_scope": M30_CLAIM_SCOPE,
    }
    if item_type == "package":
        loaded = _validate_loaded_package(
            store,
            artifact,
            participant_id=participant_id,
        )
        result["manifest"] = loaded.manifest_record
    elif include_content:
        result["payload"] = artifact.payload
    return result
