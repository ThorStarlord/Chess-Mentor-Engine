"""M32 persisted review delivery-fidelity contract qualification."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
import test_m22_end_to_end_evaluation_fidelity as m22
from test_m27_reviewed_coaching_execution_ledger import _deterministic_run, _model_run

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.participant_review_package import (
    build_participant_review_package,
)
from chess_mentor_engine.review import build_coach_review_read_model
from chess_mentor_engine.review_delivery import (
    M32_CLAIM_SCOPE,
    M32_CONTENT_SCOPE,
    M32_SCHEMA_VERSION,
    ReviewDeliveryFidelityError,
    build_persisted_review_delivery_bundle,
    build_review_delivery_content,
    validate_persisted_review_delivery_bundle,
    validate_review_delivery_bundle,
)

_GOLDEN_PATH = (
    Path(__file__).parent / "fixtures" / "m32_delivery_semantic_golden.json"
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _rehash_read_model(read_model: dict) -> dict:
    payload = {
        key: value
        for key, value in read_model.items()
        if key not in {"read_model_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "read_model_id": f"coach_review_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _rehash_bundle(bundle: dict) -> dict:
    payload = {
        key: value
        for key, value in bundle.items()
        if key not in {"delivery_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "delivery_id": f"persisted_review_delivery_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _m22_read_model(scenario: str) -> tuple[dict, dict]:
    *_, presentation = m22._scenario(scenario)
    read_model = build_coach_review_read_model(
        evaluation_presentation=presentation
    )
    return presentation, read_model


@pytest.mark.parametrize(
    "case",
    m22._MATRIX_CASES,
    ids=lambda item: item["case_id"],
)
def test_m22_matrix_survives_delivery_without_semantic_reinterpretation(
    case,
) -> None:
    presentation, read_model = _m22_read_model(case["scenario"])

    delivery = build_review_delivery_content(read_model)
    delivered = delivery["sections"]["objective_evidence"]["content"]

    assert delivered == presentation
    assert delivery["section_order"] == read_model["section_order"]
    assert m22._presentation_signature(delivered) == (
        m22._presentation_signature(presentation)
    )
    signature = m22._presentation_signature(delivered)
    for field, expected in case["expected"].items():
        assert signature[field] == expected


def test_bounded_black_evaluation_index_matches_golden_semantic_snapshot() -> None:
    _, read_model = _m22_read_model("bounded_black_perspective")
    delivery = build_review_delivery_content(read_model)
    golden = json.loads(_GOLDEN_PATH.read_text(encoding="utf-8"))

    assert golden["scenario"] == "bounded_black_perspective"
    assert delivery["evaluation_index"] == golden["evaluation_index"]


def test_persisted_package_build_is_deterministic_and_source_bound(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    package = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )

    first = build_persisted_review_delivery_bundle(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )
    second = build_persisted_review_delivery_bundle(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )

    assert first == second
    assert first["schema_version"] == M32_SCHEMA_VERSION
    assert first["claim_scope"] == M32_CLAIM_SCOPE
    assert first["content_scope"] == M32_CONTENT_SCOPE
    assert first["source_refs"]["m30_package"] == package.manifest_ref.to_dict()
    assert first["source_refs"]["m26_run"] == package.run_ref.to_dict()
    assert first["source_refs"]["m25_review"] == package.review_ref.to_dict()
    assert first["source_refs"]["m27_ledger"] == package.ledger_ref.to_dict()
    assert first["source_fingerprints"]["m25_read_model_fingerprint"] == (
        run.read_model["fingerprint"]
    )
    assert first["source_fingerprints"]["m25_source_fingerprints"] == (
        run.read_model["source_fingerprints"]
    )
    assert first["delivery"]["sections"]["objective_evidence"]["content"] == (
        run.read_model["objective_evidence"]
    )
    assert first["delivery"]["sections"]["model_coaching"]["present"] is False
    assert validate_review_delivery_bundle(first) == first
    assert (
        validate_persisted_review_delivery_bundle(
            store=store,
            participant_id="P01",
            bundle=first,
        )
        == first
    )


def test_model_content_remains_separate_from_objective_and_evaluator_truth(
    tmp_path,
) -> None:
    store, _, run = _model_run(tmp_path)
    package = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )
    bundle = build_persisted_review_delivery_bundle(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )

    sections = bundle["delivery"]["sections"]
    assert sections["objective_evidence"]["authority"] == (
        "objective_chess_evidence"
    )
    assert sections["deterministic_grounding"]["authority"] == (
        "deterministic_grounded_feedback"
    )
    assert sections["model_coaching"]["authority"] == (
        "model_language_request_bound_not_semantically_verified"
    )
    assert sections["model_evaluation"]["authority"] == (
        "bounded_model_output_quality_assessment_not_objective_truth"
    )
    assert sections["model_coaching"]["content"] == (
        run.read_model["model_coaching"]
    )
    assert sections["model_evaluation"]["content"] == (
        run.read_model["model_evaluation"]
    )
    assert sections["model_evaluation"]["content"]["truth_status"] == (
        "not_established_by_m20_evaluation"
    )
    assert (
        bundle["authority_boundary"]["promotes_model_language_to_fact"]
        is False
    )
    assert (
        bundle["authority_boundary"][
            "promotes_evaluator_judgment_to_objective_truth"
        ]
        is False
    )


def test_rehashed_decision_perspective_inversion_is_rejected() -> None:
    _, read_model = _m22_read_model("bounded_black_perspective")
    tampered = copy.deepcopy(read_model)
    tampered["objective_evidence"]["score_semantics"][
        "display_perspective"
    ] = "white"
    tampered["source_fingerprints"]["objective_evidence"] = _fingerprint(
        tampered["objective_evidence"]
    )
    tampered = _rehash_read_model(tampered)

    with pytest.raises(ReviewDeliveryFidelityError, match="score semantics"):
        build_review_delivery_content(tampered)


def test_rehashed_bound_loss_and_numericized_mate_are_rejected() -> None:
    _, bounded = _m22_read_model("bounded_black_perspective")
    lost_bound = copy.deepcopy(bounded)
    best = lost_bound["objective_evidence"]["comparison"]["best_evaluation"]
    best["white"]["bound"] = "exact"
    lost_bound["source_fingerprints"]["objective_evidence"] = _fingerprint(
        lost_bound["objective_evidence"]
    )
    lost_bound = _rehash_read_model(lost_bound)
    with pytest.raises(ReviewDeliveryFidelityError, match="bound inversion"):
        build_review_delivery_content(lost_bound)

    _, mate = _m22_read_model("symbolic_terminal_mate")
    numericized = copy.deepcopy(mate)
    numericized["objective_evidence"]["comparison"]["best_evaluation"][
        "centipawns"
    ] = 100000
    numericized["source_fingerprints"]["objective_evidence"] = _fingerprint(
        numericized["objective_evidence"]
    )
    numericized = _rehash_read_model(numericized)
    with pytest.raises(ReviewDeliveryFidelityError, match="numericized"):
        build_review_delivery_content(numericized)


def test_rehashed_reordering_and_source_fingerprint_drift_are_rejected() -> None:
    _, read_model = _m22_read_model("exact_white_root_multipv")
    reordered = copy.deepcopy(read_model)
    reordered["objective_evidence"]["root_analysis"]["candidates"].reverse()
    reordered["source_fingerprints"]["objective_evidence"] = _fingerprint(
        reordered["objective_evidence"]
    )
    reordered = _rehash_read_model(reordered)
    with pytest.raises(ReviewDeliveryFidelityError, match="ordering"):
        build_review_delivery_content(reordered)

    drifted = copy.deepcopy(read_model)
    drifted["source_fingerprints"]["objective_evidence"] = "0" * 64
    drifted = _rehash_read_model(drifted)
    with pytest.raises(
        ReviewDeliveryFidelityError,
        match="source fingerprint|fingerprint",
    ):
        build_review_delivery_content(drifted)


def test_rehashed_authority_promotion_is_rejected(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    package = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )
    bundle = build_persisted_review_delivery_bundle(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )
    tampered = copy.deepcopy(bundle)
    tampered["delivery"]["sections"]["model_coaching"]["authority"] = (
        "objective_chess_evidence"
    )
    tampered = _rehash_bundle(tampered)

    with pytest.raises(
        ReviewDeliveryFidelityError,
        match="model_coaching authority",
    ):
        validate_review_delivery_bundle(tampered)


def test_persisted_validation_rejects_source_swap_and_wrong_participant(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    package = build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )
    bundle = build_persisted_review_delivery_bundle(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )

    tampered = copy.deepcopy(bundle)
    tampered["source_refs"]["m30_package"]["artifact_id"] = (
        "participant_review_package_forged"
    )
    tampered = _rehash_bundle(tampered)
    with pytest.raises(
        ReviewDeliveryFidelityError,
        match="M30 package validation failed",
    ):
        validate_persisted_review_delivery_bundle(
            store=store,
            participant_id="P01",
            bundle=tampered,
        )

    with pytest.raises(
        ReviewDeliveryFidelityError,
        match="requested participant",
    ):
        validate_persisted_review_delivery_bundle(
            store=store,
            participant_id="OTHER",
            bundle=bundle,
        )
