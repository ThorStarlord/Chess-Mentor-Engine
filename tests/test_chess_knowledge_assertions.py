from __future__ import annotations

from dataclasses import replace

import pytest

from chess_mentor_engine.chess_knowledge import (
    KnowledgeAssertionBundle,
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeSubject,
    OntologyRegistry,
    build_assertion_bundle,
    build_knowledge_assertion,
    validate_assertion_bundle,
    validate_knowledge_assertion,
)
from chess_mentor_engine.chess_knowledge.mappings import (
    build_lichess_theme_assertions,
)

_FINGERPRINT = "a" * 64
_OTHER_FINGERPRINT = "b" * 64
_CREATED_AT = "2026-09-11T08:00:00-03:00"


def _position_subject() -> KnowledgeSubject:
    return KnowledgeSubject(
        subject_kind="position",
        position_id="pos_demo_001",
        game_id="game_demo_001",
        ply_index=12,
    )


def _position_evidence() -> KnowledgeEvidenceRef:
    return KnowledgeEvidenceRef(
        kind="canonical_position",
        ref_id="pos_demo_001",
        fingerprint=_FINGERPRINT,
    )


def _detector_provenance() -> KnowledgeProvenance:
    return KnowledgeProvenance(
        source_kind="detector",
        source_id="pawn-structure-detector",
        source_version="1",
        source_fingerprint=_OTHER_FINGERPRINT,
        run_id="run_demo_001",
    )


def test_deterministic_assertion_is_stable_and_ontology_bound() -> None:
    registry = OntologyRegistry.load_default()
    kwargs = {
        "concept_id": "position.isolated_pawn",
        "subject": _position_subject(),
        "status": "present",
        "authority_class": "deterministic_position_fact",
        "evidence_refs": (_position_evidence(),),
        "provenance": _detector_provenance(),
        "claim_scope": "position-local structural fact; not learner inference",
        "created_at": _CREATED_AT,
        "registry": registry,
    }

    first = build_knowledge_assertion(**kwargs)
    second = build_knowledge_assertion(**kwargs)

    assert first == second
    assert first.assertion_id.startswith("cka_")
    assert first.concept_fingerprint == registry.concept_fingerprint(
        "position.isolated_pawn"
    )
    assert first.ontology_fingerprint == registry.fingerprint
    validate_knowledge_assertion(first, registry=registry)


def test_assertion_rejects_concept_and_identity_tampering() -> None:
    assertion = build_knowledge_assertion(
        concept_id="position.isolated_pawn",
        subject=_position_subject(),
        status="present",
        authority_class="deterministic_position_fact",
        evidence_refs=(_position_evidence(),),
        provenance=_detector_provenance(),
        claim_scope="position-local structural fact; not learner inference",
        created_at=_CREATED_AT,
    )

    with pytest.raises(ValueError, match="concept fingerprint mismatch"):
        validate_knowledge_assertion(
            replace(assertion, concept_fingerprint=_FINGERPRINT)
        )
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        validate_knowledge_assertion(replace(assertion, claim_scope="tampered"))


def test_concept_group_and_detector_authority_drift_are_rejected() -> None:
    with pytest.raises(ValueError, match="concept groups cannot be asserted"):
        build_knowledge_assertion(
            concept_id="group.position_features",
            subject=_position_subject(),
            status="supported",
            authority_class="heuristic_assessment",
            evidence_refs=(_position_evidence(),),
            provenance=_detector_provenance(),
            claim_scope="invalid group assertion",
            created_at=_CREATED_AT,
        )

    with pytest.raises(ValueError, match="detector assertion exceeds"):
        build_knowledge_assertion(
            concept_id="position.isolated_pawn",
            subject=_position_subject(),
            status="supported",
            authority_class="heuristic_assessment",
            evidence_refs=(_position_evidence(),),
            provenance=_detector_provenance(),
            claim_scope="invalid authority drift",
            created_at=_CREATED_AT,
        )


def test_deterministic_assertions_require_binary_status() -> None:
    with pytest.raises(ValueError, match="present or absent"):
        build_knowledge_assertion(
            concept_id="position.isolated_pawn",
            subject=_position_subject(),
            status="plausible",
            authority_class="deterministic_position_fact",
            evidence_refs=(_position_evidence(),),
            provenance=_detector_provenance(),
            claim_scope="invalid deterministic uncertainty",
            created_at=_CREATED_AT,
        )


def test_lichess_pin_projection_preserves_external_authority_and_ambiguity() -> None:
    assertions = build_lichess_theme_assertions(
        theme="pin",
        subject=_position_subject(),
        external_source_fingerprint=_FINGERPRINT,
        created_at=_CREATED_AT,
    )

    assert {item.concept_id for item in assertions} == {
        "tactic.absolute_pin",
        "tactic.relative_pin",
    }
    assert {item.authority_class for item in assertions} == {
        "external_taxonomy_tag"
    }
    assert {item.status for item in assertions} == {"plausible"}
    assert all(item.provenance.source_kind == "external" for item in assertions)


def test_lichess_exact_mapping_is_supported_but_not_detector_authority() -> None:
    (assertion,) = build_lichess_theme_assertions(
        theme="fork",
        subject=_position_subject(),
        external_source_fingerprint=_FINGERPRINT,
        created_at=_CREATED_AT,
    )

    assert assertion.concept_id == "tactic.fork"
    assert assertion.status == "supported"
    assert assertion.authority_class == "external_taxonomy_tag"
    assert assertion.provenance.source_kind == "external"


def test_assertion_bundle_is_stable_and_rejects_subject_or_identity_drift() -> None:
    assertion = build_knowledge_assertion(
        concept_id="position.isolated_pawn",
        subject=_position_subject(),
        status="present",
        authority_class="deterministic_position_fact",
        evidence_refs=(_position_evidence(),),
        provenance=_detector_provenance(),
        claim_scope="position-local structural fact; not learner inference",
        created_at=_CREATED_AT,
    )
    bundle = build_assertion_bundle(
        subject=_position_subject(),
        assertions=(assertion,),
        claim_scope="position-local knowledge bundle; not participant evidence",
        created_at=_CREATED_AT,
    )
    rebuilt = build_assertion_bundle(
        subject=_position_subject(),
        assertions=(assertion,),
        claim_scope="position-local knowledge bundle; not participant evidence",
        created_at=_CREATED_AT,
    )

    assert bundle == rebuilt
    assert bundle.bundle_id.startswith("ckb_")
    validate_assertion_bundle(bundle)

    other_subject = KnowledgeSubject(
        subject_kind="position",
        position_id="pos_other",
        game_id="game_demo_001",
        ply_index=13,
    )
    with pytest.raises(ValueError, match="share the exact bundle subject"):
        build_assertion_bundle(
            subject=other_subject,
            assertions=(assertion,),
            claim_scope="invalid mixed-subject bundle",
            created_at=_CREATED_AT,
        )

    tampered = KnowledgeAssertionBundle(
        bundle_id=bundle.bundle_id,
        fingerprint=bundle.fingerprint,
        ontology_version=bundle.ontology_version,
        ontology_fingerprint=bundle.ontology_fingerprint,
        subject=bundle.subject,
        assertions=bundle.assertions,
        claim_scope="tampered",
        created_at=bundle.created_at,
    )
    with pytest.raises(ValueError, match="bundle fingerprint mismatch"):
        validate_assertion_bundle(tampered)


def test_subject_shape_validation_prevents_scope_ambiguity() -> None:
    with pytest.raises(ValueError, match="requires move_uci"):
        KnowledgeSubject(subject_kind="move", position_id="pos_demo_001")

    with pytest.raises(ValueError, match="requires at least one move"):
        KnowledgeSubject(subject_kind="move_sequence", position_id="pos_demo_001")

    with pytest.raises(ValueError, match="requires comparison_position_id"):
        KnowledgeSubject(
            subject_kind="position_comparison", position_id="pos_demo_001"
        )
