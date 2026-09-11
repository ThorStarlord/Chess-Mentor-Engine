"""M32 deterministic delivery contract over persisted M25/M30 review state."""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_reference import (
    M28_SCHEMA_VERSION,
    SECTION_ORDER,
    CoachReviewReferenceError,
    render_coach_review_reference_surface,
)
from chess_mentor_engine.participant_review_package import (
    M30_SCHEMA_VERSION,
    ParticipantReviewPackageError,
    load_participant_review_package,
    render_participant_review_package_surface,
)
from chess_mentor_engine.presentation import PRESENTATION_SCHEMA_VERSION
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.storage import ArtifactRef, LocalArtifactStore

M32_SCHEMA_VERSION = "m32.persisted-review-delivery-fidelity.v1"
M32_CLAIM_SCOPE = "repository_local_exact_review_delivery_fidelity"
M32_CONTENT_SCOPE = "exact_review_content_explicit_consumer_bundle"

_EXPECTED_SCORE_SEMANTICS = {
    "canonical_engine_perspective": "white",
    "display_perspective": "decision_mover",
    "centipawn_unit": "centipawns",
    "mate_representation": "winner_and_plies_to_mate",
    "bound_semantics": "ordering_bound_in_display_perspective",
}

_SECTION_AUTHORITIES = {
    "objective_evidence": "objective_chess_evidence",
    "diagnostic_selection": "diagnostic_selection_evidence",
    "participant_authority": "participant_authorization",
    "tutor_state": "workflow_state",
    "deterministic_grounding": "deterministic_grounded_feedback",
    "model_coaching": "model_language_request_bound_not_semantically_verified",
    "model_evaluation": "bounded_model_output_quality_assessment_not_objective_truth",
}

_SECTION_FINGERPRINT_KEYS = {
    "objective_evidence": ("objective_evidence",),
    "diagnostic_selection": ("diagnostic_candidate", "diagnostic_batch"),
    "participant_authority": ("authorization", "launch"),
    "tutor_state": ("tutor_state",),
    "deterministic_grounding": ("deterministic_grounding",),
    "model_coaching": ("model_coaching",),
    "model_evaluation": ("model_evaluation",),
}

_AUTHORITY_CONTRACT = {
    "objective_evidence": "M15",
    "diagnostic_selection": "M18",
    "participant_authority": "M21",
    "tutor_state": "M8",
    "deterministic_grounding": "M16",
    "model_coaching": "M19",
    "model_evaluation": "M20",
    "model_evaluation_truth_status": "not_established_by_m20_evaluation",
}

_AUTHORITY_BOUNDARY = {
    "executes_external_calls": False,
    "creates_objective_chess_facts": False,
    "reinterprets_engine_scores": False,
    "promotes_model_language_to_fact": False,
    "promotes_evaluator_judgment_to_objective_truth": False,
    "advances_tutor_state": False,
    "claims_pedagogical_quality": False,
    "claims_production_ui_quality": False,
}

_BUNDLE_KEYS = {
    "schema_version",
    "participant_id",
    "claim_scope",
    "content_scope",
    "source_refs",
    "source_fingerprints",
    "authority_contract",
    "authority_boundary",
    "delivery",
    "delivery_id",
    "fingerprint",
}

_SOURCE_REF_KEYS = {"m30_package", "m26_run", "m25_review", "m27_ledger"}
_SOURCE_FINGERPRINT_KEYS = {
    "m30_manifest_fingerprint",
    "m30_artifact_digest",
    "m25_read_model_id",
    "m25_read_model_fingerprint",
    "m25_source_fingerprints",
    "m28_surface_fingerprint",
}
_ALLOWED_BOUNDS = {"exact", "lower", "upper"}


class ReviewDeliveryFidelityError(ValueError):
    """M32 cannot deliver the persisted review without preserving semantics."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _strict_dict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise ReviewDeliveryFidelityError(f"{label} shape mismatch")
    return value


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ReviewDeliveryFidelityError(f"{label} must not be empty")
    return value


def _reverse_bound(bound: str) -> str:
    if bound == "lower":
        return "upper"
    if bound == "upper":
        return "lower"
    return bound


def _validate_evaluation(value: Any, *, decision_mover: str, label: str) -> None:
    if value is None:
        return
    if type(value) is not dict:
        raise ReviewDeliveryFidelityError(f"{label} must be an evaluation object")
    white = value.get("white")
    mover = value.get("decision_mover")
    if type(white) is not dict or type(mover) is not dict:
        raise ReviewDeliveryFidelityError(f"{label} perspective records are malformed")
    if mover.get("side") != decision_mover:
        raise ReviewDeliveryFidelityError(f"{label} decision-mover perspective drifted")
    white_bound = white.get("bound")
    mover_bound = mover.get("bound")
    if white_bound not in _ALLOWED_BOUNDS or mover_bound not in _ALLOWED_BOUNDS:
        raise ReviewDeliveryFidelityError(f"{label} bound is invalid")
    expected_bound = white_bound if decision_mover == "white" else _reverse_bound(white_bound)
    if mover_bound != expected_bound:
        raise ReviewDeliveryFidelityError(f"{label} perspective bound inversion drifted")

    kind = value.get("kind")
    if kind == "centipawn":
        if value.get("unit") != "centipawns":
            raise ReviewDeliveryFidelityError(f"{label} centipawn unit drifted")
        white_cp = white.get("centipawns")
        mover_cp = mover.get("centipawns")
        if type(white_cp) is not int or type(mover_cp) is not int:
            raise ReviewDeliveryFidelityError(f"{label} centipawn value is invalid")
        expected_cp = white_cp if decision_mover == "white" else -white_cp
        if mover_cp != expected_cp:
            raise ReviewDeliveryFidelityError(f"{label} perspective sign inversion drifted")
        if "winner" in value or "plies_to_mate" in value:
            raise ReviewDeliveryFidelityError(f"{label} mixes centipawn and mate semantics")
        return

    if kind == "mate":
        winner = value.get("winner")
        plies = value.get("plies_to_mate")
        if winner not in {"white", "black"} or type(plies) is not int or plies < 0:
            raise ReviewDeliveryFidelityError(f"{label} mate representation is invalid")
        if "unit" in value or "centipawns" in value or "centipawns" in white or "centipawns" in mover:
            raise ReviewDeliveryFidelityError(f"{label} numericized a symbolic mate")
        if white.get("favours_perspective") is not (winner == "white"):
            raise ReviewDeliveryFidelityError(f"{label} White mate perspective drifted")
        if mover.get("favours_perspective") is not (winner == decision_mover):
            raise ReviewDeliveryFidelityError(f"{label} mover mate perspective drifted")
        return

    raise ReviewDeliveryFidelityError(f"{label} evaluation kind is unsupported")


def _validate_analysis(value: Any, *, decision_mover: str, label: str) -> None:
    if type(value) is not dict:
        raise ReviewDeliveryFidelityError(f"{label} must be an analysis object")
    candidates = value.get("candidates")
    if type(candidates) is not list:
        raise ReviewDeliveryFidelityError(f"{label} candidates must be an array")
    ranks: list[int] = []
    for candidate in candidates:
        if type(candidate) is not dict:
            raise ReviewDeliveryFidelityError(f"{label} candidate is malformed")
        rank = candidate.get("rank")
        if type(rank) is not int or rank < 1:
            raise ReviewDeliveryFidelityError(f"{label} candidate rank is invalid")
        ranks.append(rank)
        _validate_evaluation(
            candidate.get("evaluation"),
            decision_mover=decision_mover,
            label=f"{label} candidate evaluation",
        )
    if ranks != sorted(ranks) or len(ranks) != len(set(ranks)):
        raise ReviewDeliveryFidelityError(f"{label} candidate ordering drifted")


def _validate_evaluation_semantics(presentation: Any) -> dict[str, Any]:
    if type(presentation) is not dict:
        raise ReviewDeliveryFidelityError("M15 objective evidence must be an object")
    if presentation.get("schema_version") != PRESENTATION_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M15 presentation schema drifted")
    if presentation.get("score_semantics") != _EXPECTED_SCORE_SEMANTICS:
        raise ReviewDeliveryFidelityError("M15 score semantics drifted")
    subject = presentation.get("subject")
    if type(subject) is not dict or subject.get("side_to_move") not in {"white", "black"}:
        raise ReviewDeliveryFidelityError("M15 decision mover is invalid")
    decision_mover = subject["side_to_move"]

    _validate_analysis(
        presentation.get("root_analysis"),
        decision_mover=decision_mover,
        label="M15 root analysis",
    )
    child = presentation.get("played_child_analysis")
    if child is not None:
        _validate_analysis(
            child,
            decision_mover=decision_mover,
            label="M15 played child analysis",
        )

    comparison = presentation.get("comparison")
    if type(comparison) is not dict:
        raise ReviewDeliveryFidelityError("M15 comparison is malformed")
    _validate_evaluation(
        comparison.get("best_evaluation"),
        decision_mover=decision_mover,
        label="M15 best evaluation",
    )
    _validate_evaluation(
        comparison.get("played_evaluation"),
        decision_mover=decision_mover,
        label="M15 played evaluation",
    )
    if (
        comparison.get("evidence_quality") != "exact"
        and comparison.get("exact_centipawn_delta_for_mover") is not None
    ):
        raise ReviewDeliveryFidelityError(
            "M15 non-exact comparison exposed an exact centipawn delta"
        )
    return presentation


def _validate_source_fingerprints(read_model: dict[str, Any]) -> None:
    fingerprints = read_model.get("source_fingerprints")
    if type(fingerprints) is not dict:
        raise ReviewDeliveryFidelityError("M25 source fingerprints are malformed")

    objective = read_model["objective_evidence"]
    if fingerprints.get("objective_evidence") != _fingerprint(objective):
        raise ReviewDeliveryFidelityError("M25 objective source fingerprint drifted")

    diagnostic = read_model["diagnostic_selection"]
    if diagnostic is None:
        if fingerprints.get("diagnostic_candidate") is not None or fingerprints.get("diagnostic_batch") is not None:
            raise ReviewDeliveryFidelityError("M25 absent diagnostic sources retained fingerprints")
    else:
        if type(diagnostic) is not dict or type(diagnostic.get("candidate")) is not dict or type(diagnostic.get("batch_ref")) is not dict:
            raise ReviewDeliveryFidelityError("M25 diagnostic selection is malformed")
        if fingerprints.get("diagnostic_candidate") != _fingerprint(diagnostic["candidate"]):
            raise ReviewDeliveryFidelityError("M25 diagnostic candidate fingerprint drifted")
        if fingerprints.get("diagnostic_batch") != diagnostic["batch_ref"].get("fingerprint"):
            raise ReviewDeliveryFidelityError("M25 diagnostic batch fingerprint drifted")

    participant = read_model["participant_authority"]
    if participant is None:
        if fingerprints.get("authorization") is not None or fingerprints.get("launch") is not None:
            raise ReviewDeliveryFidelityError("M25 absent participant authority retained fingerprints")
    else:
        if type(participant) is not dict or type(participant.get("authorization")) is not dict:
            raise ReviewDeliveryFidelityError("M25 participant authority is malformed")
        authorization = participant["authorization"]
        if fingerprints.get("authorization") != authorization.get("fingerprint"):
            raise ReviewDeliveryFidelityError("M25 authorization fingerprint drifted")
        launch = participant.get("launch")
        if launch is None:
            if fingerprints.get("launch") is not None:
                raise ReviewDeliveryFidelityError("M25 absent launch retained a fingerprint")
        elif type(launch) is not dict or fingerprints.get("launch") != launch.get("fingerprint"):
            raise ReviewDeliveryFidelityError("M25 launch fingerprint drifted")

    tutor_state = read_model["tutor_state"]
    if tutor_state is None:
        if fingerprints.get("tutor_state") is not None:
            raise ReviewDeliveryFidelityError("M25 absent tutor state retained a fingerprint")
    else:
        if type(tutor_state) is not dict:
            raise ReviewDeliveryFidelityError("M25 tutor state is malformed")
        source_tutor_state = _copy(tutor_state)
        source_tutor_state.pop("claim_scope", None)
        if fingerprints.get("tutor_state") != _fingerprint(source_tutor_state):
            raise ReviewDeliveryFidelityError("M25 tutor-state fingerprint drifted")

    for section, source_key in (
        ("deterministic_grounding", "deterministic_grounding"),
        ("model_coaching", "model_coaching"),
        ("model_evaluation", "model_evaluation"),
    ):
        value = read_model[section]
        source_fingerprint = fingerprints.get(source_key)
        if value is None:
            if source_fingerprint is not None:
                raise ReviewDeliveryFidelityError(f"M25 absent {section} retained a fingerprint")
        elif type(value) is not dict or source_fingerprint != value.get("fingerprint"):
            raise ReviewDeliveryFidelityError(f"M25 {section} fingerprint drifted")


def _evaluation_index(presentation: dict[str, Any]) -> dict[str, Any]:
    comparison = presentation["comparison"]
    root = presentation["root_analysis"]
    child = presentation["played_child_analysis"]
    child_index = None
    if child is not None:
        failure = child.get("failure")
        child_index = {
            "status": child.get("status"),
            "evidence_quality": child.get("evidence_quality"),
            "failure_code": None if type(failure) is not dict else failure.get("code"),
        }
    return {
        "score_semantics": _copy(presentation["score_semantics"]),
        "decision_mover": presentation["subject"]["side_to_move"],
        "root": {
            "status": root.get("status"),
            "evidence_quality": root.get("evidence_quality"),
        },
        "played_child": child_index,
        "comparison": {
            "evidence_quality": comparison.get("evidence_quality"),
            "comparison_kind": comparison.get("comparison_kind"),
            "preference": comparison.get("preference"),
            "compatibility": comparison.get("compatibility"),
            "played_evaluation_source": comparison.get("played_evaluation_source"),
            "best_move_uci": comparison.get("best_move_uci"),
            "played_move_uci": comparison.get("played_move_uci"),
            "best_evaluation": _copy(comparison.get("best_evaluation")),
            "played_evaluation": _copy(comparison.get("played_evaluation")),
            "exact_centipawn_delta_for_mover": comparison.get("exact_centipawn_delta_for_mover"),
            "mate_relation": comparison.get("mate_relation"),
            "terminal_outcome": comparison.get("terminal_outcome"),
        },
    }


def _section_fingerprints(read_model: dict[str, Any], section_id: str) -> dict[str, Any]:
    source = read_model["source_fingerprints"]
    return {key: source[key] for key in _SECTION_FINGERPRINT_KEYS[section_id]}


def build_review_delivery_content(read_model: dict[str, Any]) -> dict[str, Any]:
    """Project one M25 read model into a stable authority-labelled consumer shape."""
    try:
        validated = render_coach_review_reference_surface(read_model).read_model
    except CoachReviewReferenceError as exc:
        raise ReviewDeliveryFidelityError(f"M25 read model failed M28 validation: {exc}") from exc
    if validated.get("schema_version") != COACH_REVIEW_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M25 read-model schema drifted")
    if validated.get("section_order") != list(SECTION_ORDER):
        raise ReviewDeliveryFidelityError("M25 section ordering drifted")
    presentation = _validate_evaluation_semantics(validated["objective_evidence"])
    _validate_source_fingerprints(validated)

    sections: dict[str, Any] = {}
    for section_id in SECTION_ORDER:
        content = validated[section_id]
        sections[section_id] = {
            "authority": _SECTION_AUTHORITIES[section_id],
            "present": content is not None,
            "source_fingerprints": _section_fingerprints(validated, section_id),
            "content": _copy(content),
        }
    return {
        "section_order": list(SECTION_ORDER),
        "evaluation_index": _evaluation_index(presentation),
        "sections": sections,
    }


def _flatten_delivery_fingerprints(delivery: dict[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    sections = delivery["sections"]
    for section_id in SECTION_ORDER:
        section = sections[section_id]
        for key, value in section["source_fingerprints"].items():
            if key in flattened and flattened[key] != value:
                raise ReviewDeliveryFidelityError("M32 section source fingerprints conflict")
            flattened[key] = value
    return flattened


def _validate_delivery(delivery: Any) -> dict[str, Any]:
    delivery = _strict_dict(delivery, {"section_order", "evaluation_index", "sections"}, "M32 delivery")
    if delivery["section_order"] != list(SECTION_ORDER):
        raise ReviewDeliveryFidelityError("M32 section ordering drifted")
    sections = delivery["sections"]
    if type(sections) is not dict or set(sections) != set(SECTION_ORDER):
        raise ReviewDeliveryFidelityError("M32 delivery section set drifted")
    for section_id in SECTION_ORDER:
        section = _strict_dict(
            sections[section_id],
            {"authority", "present", "source_fingerprints", "content"},
            f"M32 {section_id} section",
        )
        if section["authority"] != _SECTION_AUTHORITIES[section_id]:
            raise ReviewDeliveryFidelityError(f"M32 {section_id} authority drifted")
        if type(section["present"]) is not bool or section["present"] is not (section["content"] is not None):
            raise ReviewDeliveryFidelityError(f"M32 {section_id} presence marker drifted")
        expected_keys = set(_SECTION_FINGERPRINT_KEYS[section_id])
        if type(section["source_fingerprints"]) is not dict or set(section["source_fingerprints"]) != expected_keys:
            raise ReviewDeliveryFidelityError(f"M32 {section_id} source fingerprint set drifted")

    presentation = sections["objective_evidence"]["content"]
    presentation = _validate_evaluation_semantics(presentation)
    if delivery["evaluation_index"] != _evaluation_index(presentation):
        raise ReviewDeliveryFidelityError("M32 evaluation index drifted from exact M15 content")
    return delivery


def build_persisted_review_delivery_bundle(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    package_artifact_id: str,
) -> dict[str, Any]:
    """Build one deterministic exact-content delivery bundle from a verified M30 package."""
    _nonempty(participant_id, "participant_id")
    _nonempty(package_artifact_id, "package_artifact_id")
    try:
        loaded = load_participant_review_package(
            store=store,
            participant_id=participant_id,
            package_artifact_id=package_artifact_id,
        )
        surface = render_participant_review_package_surface(
            store=store,
            participant_id=participant_id,
            package_artifact_id=package_artifact_id,
        )
    except ParticipantReviewPackageError as exc:
        raise ReviewDeliveryFidelityError(f"M30 package validation failed: {exc}") from exc

    manifest = loaded.manifest_record
    if manifest.get("schema_version") != M30_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M30 package schema drifted")
    reference_surface = manifest.get("reference_surface")
    fingerprints = manifest.get("source_fingerprints")
    if type(reference_surface) is not dict or type(fingerprints) is not dict:
        raise ReviewDeliveryFidelityError("M30 package provenance is malformed")
    if reference_surface.get("schema_version") != M28_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M30 reference-surface schema drifted")
    if reference_surface.get("fingerprint") != surface.fingerprint:
        raise ReviewDeliveryFidelityError("M30/M28 surface fingerprint drifted")
    if reference_surface.get("m25_read_model_fingerprint") != surface.read_model.get("fingerprint"):
        raise ReviewDeliveryFidelityError("M30/M25 read-model fingerprint drifted")
    if fingerprints.get("m25_source_fingerprints") != surface.read_model.get("source_fingerprints"):
        raise ReviewDeliveryFidelityError("M30/M25 source fingerprints drifted")

    delivery = build_review_delivery_content(surface.read_model)
    payload = {
        "schema_version": M32_SCHEMA_VERSION,
        "participant_id": participant_id,
        "claim_scope": M32_CLAIM_SCOPE,
        "content_scope": M32_CONTENT_SCOPE,
        "source_refs": {
            "m30_package": loaded.manifest_ref.to_dict(),
            "m26_run": loaded.run_ref.to_dict(),
            "m25_review": loaded.review_ref.to_dict(),
            "m27_ledger": loaded.ledger_ref.to_dict(),
        },
        "source_fingerprints": {
            "m30_manifest_fingerprint": manifest["fingerprint"],
            "m30_artifact_digest": loaded.manifest_ref.digest,
            "m25_read_model_id": surface.read_model["read_model_id"],
            "m25_read_model_fingerprint": surface.read_model["fingerprint"],
            "m25_source_fingerprints": _copy(surface.read_model["source_fingerprints"]),
            "m28_surface_fingerprint": surface.fingerprint,
        },
        "authority_contract": dict(_AUTHORITY_CONTRACT),
        "authority_boundary": dict(_AUTHORITY_BOUNDARY),
        "delivery": delivery,
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "delivery_id": f"persisted_review_delivery_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def validate_review_delivery_bundle(value: Any) -> dict[str, Any]:
    """Validate one detached M32 bundle, including rehashed authority/semantic drift."""
    bundle = _strict_dict(value, _BUNDLE_KEYS, "M32 bundle")
    if bundle["schema_version"] != M32_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M32 schema drifted")
    participant_id = _nonempty(bundle["participant_id"], "M32 participant_id")
    if bundle["claim_scope"] != M32_CLAIM_SCOPE:
        raise ReviewDeliveryFidelityError("M32 claim scope drifted")
    if bundle["content_scope"] != M32_CONTENT_SCOPE:
        raise ReviewDeliveryFidelityError("M32 content scope drifted")
    if bundle["authority_contract"] != _AUTHORITY_CONTRACT:
        raise ReviewDeliveryFidelityError("M32 authority contract drifted")
    if bundle["authority_boundary"] != _AUTHORITY_BOUNDARY:
        raise ReviewDeliveryFidelityError("M32 authority boundary drifted")

    refs = bundle["source_refs"]
    if type(refs) is not dict or set(refs) != _SOURCE_REF_KEYS:
        raise ReviewDeliveryFidelityError("M32 source reference set drifted")
    parsed_refs: dict[str, ArtifactRef] = {}
    for key, ref_value in refs.items():
        if type(ref_value) is not dict:
            raise ReviewDeliveryFidelityError(f"M32 {key} source reference is malformed")
        try:
            ref = ArtifactRef(**ref_value)
        except (TypeError, ValueError, KeyError) as exc:
            raise ReviewDeliveryFidelityError(f"M32 {key} source reference is invalid") from exc
        if ref.participant_id != participant_id:
            raise ReviewDeliveryFidelityError(f"M32 {key} participant scope drifted")
        parsed_refs[key] = ref
    if parsed_refs["m30_package"].kind != M30_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M32 package reference kind drifted")
    if parsed_refs["m25_review"].kind != COACH_REVIEW_SCHEMA_VERSION:
        raise ReviewDeliveryFidelityError("M32 review reference kind drifted")

    source_fingerprints = bundle["source_fingerprints"]
    if type(source_fingerprints) is not dict or set(source_fingerprints) != _SOURCE_FINGERPRINT_KEYS:
        raise ReviewDeliveryFidelityError("M32 source fingerprint set drifted")
    for key in (
        "m30_manifest_fingerprint",
        "m30_artifact_digest",
        "m25_read_model_id",
        "m25_read_model_fingerprint",
        "m28_surface_fingerprint",
    ):
        _nonempty(source_fingerprints[key], f"M32 {key}")
    if source_fingerprints["m30_artifact_digest"] != parsed_refs["m30_package"].digest:
        raise ReviewDeliveryFidelityError("M32 package digest drifted")

    delivery = _validate_delivery(bundle["delivery"])
    flattened = _flatten_delivery_fingerprints(delivery)
    if source_fingerprints["m25_source_fingerprints"] != flattened:
        raise ReviewDeliveryFidelityError("M32 delivered source fingerprints drifted from M25")

    payload = {key: item for key, item in bundle.items() if key not in {"delivery_id", "fingerprint"}}
    expected = _fingerprint(payload)
    if bundle["fingerprint"] != expected:
        raise ReviewDeliveryFidelityError("M32 bundle fingerprint mismatch")
    if bundle["delivery_id"] != f"persisted_review_delivery_{expected[:20]}":
        raise ReviewDeliveryFidelityError("M32 bundle identity mismatch")
    return _copy(bundle)


def validate_persisted_review_delivery_bundle(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    bundle: Any,
) -> dict[str, Any]:
    """Rebuild a detached bundle from its exact M30 source and require equality."""
    validated = validate_review_delivery_bundle(bundle)
    if validated["participant_id"] != participant_id:
        raise ReviewDeliveryFidelityError("M32 requested participant does not match bundle")
    package_ref = ArtifactRef(**validated["source_refs"]["m30_package"])
    rebuilt = build_persisted_review_delivery_bundle(
        store=store,
        participant_id=participant_id,
        package_artifact_id=package_ref.artifact_id,
    )
    if rebuilt != validated:
        raise ReviewDeliveryFidelityError("M32 bundle drifted from persisted M30/M25 sources")
    return validated
