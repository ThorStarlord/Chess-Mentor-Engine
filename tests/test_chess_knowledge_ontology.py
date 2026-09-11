from __future__ import annotations

import json

import pytest

from chess_mentor_engine.chess_knowledge import (
    ONTOLOGY_SCHEMA_VERSION,
    OntologyLoadError,
    OntologyRegistry,
)
from chess_mentor_engine.chess_knowledge.mappings import (
    SUPPORTED_LICHESS_THEMES,
    map_lichess_theme,
    unmapped_lichess_themes,
)


def _minimal_concept(concept_id: str, name: str, *, parents=()):
    return {
        "id": concept_id,
        "kind": "concept_group",
        "preferred_name": name,
        "definition": f"Definition for {name}.",
        "detection_support": "none",
        "default_assertion_authority": "heuristic_assessment",
        "parent_ids": list(parents),
    }


def _document(*concepts):
    return json.dumps(
        {
            "schema_version": ONTOLOGY_SCHEMA_VERSION,
            "content_version": "test",
            "concepts": list(concepts),
        }
    )


def test_default_ontology_loads_composed_vocabulary() -> None:
    registry = OntologyRegistry.load_default()

    assert registry.schema_version == "chess-knowledge-ontology.v1"
    assert registry.content_version == "1.1.0"
    assert len(registry.concepts) >= 90
    assert registry.get("tactic.fork").preferred_name == "Fork"
    assert registry.find_name("Zwischenzug").concept_id == "tactic.intermezzo"
    assert registry.get("tactic.absolute_pin").detection_support == "deterministic"
    assert (
        registry.get("tactic.absolute_pin").default_assertion_authority
        == "deterministic_position_fact"
    )
    assert registry.get("position.isolated_pawn").kind == "position_feature"
    assert registry.get("principle.prophylaxis").kind == "strategic_principle"
    assert registry.get("evaluation.king_safety").kind == "evaluation_factor"
    assert registry.get("plan.improve_worst_piece").kind == "plan"
    assert len(registry.fingerprint) == 64
    assert registry.fingerprint == OntologyRegistry.load_default().fingerprint
    assert registry.concept_fingerprint("tactic.fork") == registry.concept_fingerprint(
        "tactic.fork"
    )


def test_strategy_graph_keeps_fact_principle_evaluation_and_plan_distinct() -> None:
    registry = OntologyRegistry.load_default()

    isolated = registry.get("position.isolated_pawn")
    principle = registry.get("principle.pawn.isolated_dynamic_static")
    evaluation = registry.get("evaluation.pawn_structure")
    plan = registry.get("plan.create_pawn_break")

    assert isolated.kind == "position_feature"
    assert isolated.default_assertion_authority == "deterministic_position_fact"
    assert principle.kind == "strategic_principle"
    assert principle.default_assertion_authority == "heuristic_assessment"
    assert evaluation.kind == "evaluation_factor"
    assert plan.kind == "plan"


def test_strategy_graph_represents_conflicting_principles_explicitly() -> None:
    registry = OntologyRegistry.load_default()
    ahead = registry.get("principle.trade.ahead_trade_pieces")
    space = registry.get("principle.space.preserve_piece_pressure")

    assert any(
        relation.kind == "commonly_conflicts_with"
        and relation.target_id == space.concept_id
        for relation in ahead.relationships
    )
    assert any(
        relation.kind == "commonly_conflicts_with"
        and relation.target_id == ahead.concept_id
        for relation in space.relationships
    )


def test_lichess_crosswalk_is_explicit_and_pin_does_not_collapse_subtypes() -> None:
    fork = map_lichess_theme("fork")
    assert [(concept.concept_id, mapping.relation) for concept, mapping in fork] == [
        ("tactic.fork", "exact")
    ]

    pin = map_lichess_theme("pin")
    assert {(concept.concept_id, mapping.relation) for concept, mapping in pin} == {
        ("tactic.absolute_pin", "broader"),
        ("tactic.relative_pin", "broader"),
    }

    assert all(map_lichess_theme(theme) for theme in SUPPORTED_LICHESS_THEMES)
    assert unmapped_lichess_themes(["fork", "futureUnknownTheme"]) == (
        "futureUnknownTheme",
    )


def test_registry_rejects_duplicate_ids() -> None:
    concept = _minimal_concept("group.one", "One")
    with pytest.raises(OntologyLoadError, match="IDs must be unique"):
        OntologyRegistry.from_json_text(_document(concept, concept))


def test_registry_rejects_unknown_parent_and_parent_cycle() -> None:
    with pytest.raises(OntologyLoadError, match="unknown parent concept"):
        OntologyRegistry.from_json_text(
            _document(_minimal_concept("group.one", "One", parents=("group.none",)))
        )

    first = _minimal_concept("group.one", "One", parents=("group.two",))
    second = _minimal_concept("group.two", "Two", parents=("group.one",))
    with pytest.raises(OntologyLoadError, match="contains a cycle"):
        OntologyRegistry.from_json_text(_document(first, second))


def test_registry_rejects_ambiguous_aliases_and_exact_external_mapping() -> None:
    first = _minimal_concept("group.one", "One")
    first["aliases"] = ["Shared"]
    second = _minimal_concept("group.two", "Two")
    second["aliases"] = ["shared"]
    with pytest.raises(OntologyLoadError, match="ambiguous preferred name/alias"):
        OntologyRegistry.from_json_text(_document(first, second))

    first.pop("aliases")
    second.pop("aliases")
    first["external_mappings"] = [
        {"namespace": "test", "external_id": "same", "relation": "exact"}
    ]
    second["external_mappings"] = [
        {"namespace": "test", "external_id": "same", "relation": "exact"}
    ]
    with pytest.raises(OntologyLoadError, match="cannot identify multiple concepts"):
        OntologyRegistry.from_json_text(_document(first, second))


def test_registry_rejects_unknown_keys_and_authority_drift() -> None:
    concept = _minimal_concept("group.one", "One")
    concept["surprise"] = True
    with pytest.raises(OntologyLoadError, match="unexpected keys"):
        OntologyRegistry.from_json_text(_document(concept))

    tactical = {
        "id": "tactic.example",
        "kind": "tactical_motif",
        "preferred_name": "Example",
        "definition": "Example deterministic concept.",
        "detection_support": "deterministic",
        "default_assertion_authority": "model_interpretation",
    }
    with pytest.raises(OntologyLoadError, match="deterministic authority"):
        OntologyRegistry.from_json_text(_document(tactical))


def test_concept_children_are_graph_derived_not_name_derived() -> None:
    registry = OntologyRegistry.load_default()
    children = registry.children_of("group.tactical_direct")
    ids = {concept.concept_id for concept in children}
    assert "tactic.fork" in ids
    assert "tactic.absolute_pin" in ids
    assert "mate.back_rank" not in ids
