from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest
from test_hypothesis_recurrence_assessment import (
    _assess,
    _make_hypothesis,
    _make_link,
    _policy,
    _support_units,
)

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.chess_knowledge import (
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeQualifier,
    KnowledgeSubject,
    OntologyRegistry,
    build_assertion_bundle,
    build_hypothesis_knowledge_projection,
    build_knowledge_assertion,
    validate_hypothesis_knowledge_projection,
)

_CREATED_AT = "2026-09-11T08:30:00-03:00"


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _bundle_for_unit(unit, concept_id: str = "position.open_file"):
    registry = OntologyRegistry.load_default()
    subject = KnowledgeSubject(
        subject_kind="position",
        position_id=unit.source_position_id,
        game_id=unit.source_game_id,
    )
    evidence = KnowledgeEvidenceRef(
        kind="canonical_position",
        ref_id=unit.source_position_id,
        fingerprint=_fingerprint(
            {
                "game_id": unit.source_game_id,
                "position_id": unit.source_position_id,
            }
        ),
    )
    provenance = KnowledgeProvenance(
        source_kind="detector",
        source_id="learner-projection-fixture-detector",
        source_version="1",
        source_fingerprint=_fingerprint({"detector": "learner-projection"}),
    )
    qualifiers = ()
    if concept_id == "position.open_file":
        qualifiers = (KnowledgeQualifier(name="file", value="e"),)
    assertion = build_knowledge_assertion(
        concept_id=concept_id,
        subject=subject,
        status="present",
        authority_class=registry.get(concept_id).default_assertion_authority,
        evidence_refs=(evidence,),
        provenance=provenance,
        qualifiers=qualifiers,
        claim_scope="fixture position fact; not learner inference",
        created_at=_CREATED_AT,
        registry=registry,
    )
    return build_assertion_bundle(
        subject=subject,
        assertions=(assertion,),
        claim_scope="fixture ontology bundle for M7C projection",
        created_at=_CREATED_AT,
        registry=registry,
    )


def _supported_assessment(count: int = 3):
    hypothesis, revision = _make_hypothesis()
    assessment = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, count),
    )
    return hypothesis, revision, assessment


def test_projection_is_deterministic_and_preserves_partial_coverage() -> None:
    _, _, assessment = _supported_assessment(3)
    bundles = tuple(_bundle_for_unit(unit) for unit in assessment.recurrence_units[:2])

    first = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=bundles,
        created_at=_CREATED_AT,
    )
    second = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=tuple(reversed(bundles)),
        created_at=_CREATED_AT,
    )

    assert first == second
    assert first.hypothesis_assessment_status == "supported_recurrence"
    assert len(first.covered_recurrence_unit_ids) == 2
    assert len(first.uncovered_recurrence_unit_ids) == 1
    assert {unit.hypothesis_relation for unit in first.units} == {"supports"}
    summary = first.concept_summaries[0]
    assert summary.concept_id == "position.open_file"
    assert summary.relation_counts == (("supports", 2),)
    validate_hypothesis_knowledge_projection(
        first,
        assessment=assessment,
        assertion_bundles=bundles,
    )


def test_same_concept_can_appear_in_support_and_contradiction_units() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _support_units(hypothesis, revision, 1)[0],
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="contradicts",
            game_id="g2",
        ),
    )
    assessment = _assess(hypothesis, revision, _policy(), units)
    bundles = tuple(_bundle_for_unit(unit) for unit in assessment.recurrence_units)

    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=bundles,
        created_at=_CREATED_AT,
    )

    relations = {
        unit.source_position_id: unit.hypothesis_relation for unit in projection.units
    }
    assert set(relations.values()) == {"supports", "contradicts"}
    summary = projection.concept_summaries[0]
    assert summary.relation_counts == (("contradicts", 1), ("supports", 1))
    assert projection.hypothesis_assessment_status == assessment.status


def test_projection_preserves_successful_counterexample_relation() -> None:
    hypothesis, revision = _make_hypothesis()
    units = (
        _support_units(hypothesis, revision, 1)[0],
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="successful_counterexample",
            game_id="g2",
            status="no_supported_discrepancy",
            with_assertion=False,
        ),
    )
    assessment = _assess(
        hypothesis,
        revision,
        _policy(contradiction_rule="any_contradiction_or_counterexample"),
        units,
    )
    target = next(
        unit
        for unit in assessment.recurrence_units
        if unit.relation == "successful_counterexample"
    )

    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=(_bundle_for_unit(target, "position.passed_pawn"),),
        created_at=_CREATED_AT,
    )

    assert projection.units[0].hypothesis_relation == "successful_counterexample"
    assert projection.concept_summaries[0].relation_counts == (
        ("successful_counterexample", 1),
    )


def test_bundle_outside_assessment_scope_is_rejected() -> None:
    _, _, assessment = _supported_assessment(2)
    unit = assessment.recurrence_units[0]
    bundle = _bundle_for_unit(unit)
    wrong_subject = KnowledgeSubject(
        subject_kind="position",
        position_id="position-outside-assessment",
        game_id="game-outside-assessment",
    )
    assertion = replace(bundle.assertions[0], subject=wrong_subject)
    wrong_bundle = replace(bundle, subject=wrong_subject, assertions=(assertion,))

    with pytest.raises(ValueError):
        build_hypothesis_knowledge_projection(
            assessment=assessment,
            assertion_bundles=(wrong_bundle,),
            created_at=_CREATED_AT,
        )


def test_move_bundle_is_rejected_even_when_position_id_matches() -> None:
    _, _, assessment = _supported_assessment(2)
    unit = assessment.recurrence_units[0]
    registry = OntologyRegistry.load_default()
    subject = KnowledgeSubject(
        subject_kind="move",
        position_id=unit.source_position_id,
        game_id=unit.source_game_id,
        move_uci="e2e4",
    )
    evidence = KnowledgeEvidenceRef(
        kind="move_sequence",
        ref_id="fixture-move",
        fingerprint=_fingerprint({"move": "e2e4"}),
    )
    provenance = KnowledgeProvenance(
        source_kind="detector",
        source_id="fixture-move-detector",
        source_version="1",
        source_fingerprint=_fingerprint({"detector": "move"}),
    )
    assertion = build_knowledge_assertion(
        concept_id="tactic.fork",
        subject=subject,
        status="present",
        authority_class="deterministic_sequence_pattern",
        evidence_refs=(evidence,),
        provenance=provenance,
        claim_scope="fixture move pattern",
        created_at=_CREATED_AT,
        registry=registry,
    )
    bundle = build_assertion_bundle(
        subject=subject,
        assertions=(assertion,),
        claim_scope="fixture move bundle",
        created_at=_CREATED_AT,
        registry=registry,
    )

    with pytest.raises(ValueError, match="position bundles only"):
        build_hypothesis_knowledge_projection(
            assessment=assessment,
            assertion_bundles=(bundle,),
            created_at=_CREATED_AT,
        )


def test_tampered_assessment_and_projection_are_rejected() -> None:
    _, _, assessment = _supported_assessment(2)
    bundle = _bundle_for_unit(assessment.recurrence_units[0])

    with pytest.raises(ValueError, match="assessment fingerprint mismatch"):
        build_hypothesis_knowledge_projection(
            assessment=replace(assessment, status="unclear"),
            assertion_bundles=(bundle,),
            created_at=_CREATED_AT,
        )

    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=(bundle,),
        created_at=_CREATED_AT,
    )
    with pytest.raises(ValueError, match="projection fingerprint mismatch"):
        validate_hypothesis_knowledge_projection(
            replace(projection, claim_scope="tampered"),
            assessment=assessment,
            assertion_bundles=(bundle,),
        )


def test_empty_bundle_set_is_explicitly_all_uncovered() -> None:
    _, _, assessment = _supported_assessment(2)
    projection = build_hypothesis_knowledge_projection(
        assessment=assessment,
        assertion_bundles=(),
        created_at=_CREATED_AT,
    )

    assert projection.units == ()
    assert projection.concept_summaries == ()
    assert projection.covered_recurrence_unit_ids == ()
    assert projection.uncovered_recurrence_unit_ids == assessment.recurrence_unit_ids
