from __future__ import annotations

from dataclasses import replace

import pytest
from test_m9_qualification import _intervention, _registry, _training_author
from test_m40_next_session_planner import _entry, _read_model, _synthesis
from test_m43_evidence_acquisition import _link

from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.learner_intelligence import (
    build_default_evidence_acquisition_policy,
    build_default_intervention_matching_policy,
    build_default_next_session_policy,
    build_evidence_acquisition_plan,
    build_intervention_candidate_set,
    build_learner_progress_reference_surface,
    build_learner_progress_view,
    build_next_session_plan,
    define_intervention_semantic_profile,
    validate_learner_progress_reference_surface,
    validate_learner_progress_view,
)

CREATED_AT = "2026-09-11T15:00:00-03:00"


def _plan(read_model, *syntheses):
    return build_next_session_plan(
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        policy=build_default_next_session_policy(),
        created_at="2026-09-11T14:45:00-03:00",
    )


def _teaching_sources():
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan = _plan(read_model, synthesis)
    assert plan.selected_candidate.action == "TEACH_CONCEPT"
    return entry, read_model, synthesis, plan


def _candidate_set(ontology, plan, synthesis):
    intervention = _intervention(key="fork-training", exercise_key="fork-training-ex")
    registry = _registry(intervention)
    profile = define_intervention_semantic_profile(
        intervention=intervention,
        ontology=ontology,
        target_concept_ids=("tactic.fork",),
        training_modes=("fork_recognition",),
        provenance=_training_author(),
        created_at="2026-09-11T14:35:00-03:00",
    )
    return build_intervention_candidate_set(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        ontology=ontology,
        intervention_registry=registry,
        profiles=(profile,),
        policy=build_default_intervention_matching_policy(),
        created_at="2026-09-11T14:40:00-03:00",
    )


def test_m44_composes_m36_m39_m40_and_m41_without_new_authority():
    ontology = OntologyRegistry.load_default()
    _, read_model, synthesis, plan = _teaching_sources()
    candidate_set = _candidate_set(ontology, plan, synthesis)

    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
        intervention_candidate_sets=(candidate_set,),
        created_at=CREATED_AT,
    )

    hypothesis = view.hypotheses[0]
    assert hypothesis.is_current_priority is True
    assert hypothesis.priority_rank == 1
    assert hypothesis.next_action == "TEACH_CONCEPT"
    assert hypothesis.concepts[0].concept_id == "tactic.fork"
    assert hypothesis.concepts[0].preferred_name == "Fork"
    assert hypothesis.intervention_candidates[0].status == "eligible_candidate"
    assert hypothesis.acquisition_ref is None
    assert view.causal_effect == "not_established"
    assert view.mastery == "not_established"

    surface = build_learner_progress_reference_surface(view)
    assert surface.claim_scope == "local_reference_presentation_only"
    assert "No M43 acquisition plan supplied" in surface.html
    assert "M9 selection authority has not been exercised here" in surface.html
    assert "Ontology concepts describe chess semantics" in surface.html


def test_m44_composes_m43_challenge_candidates_without_promoting_them():
    ontology = OntologyRegistry.load_default()
    entry = _entry()
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=0)
    plan = _plan(read_model, synthesis)
    assert plan.selected_candidate.action == "CHALLENGE_HYPOTHESIS"
    link = _link(
        plan.selected_candidate.hypothesis_revision_ref,
        "m44-link",
        "contradicts",
        "m44-position",
        "m44-game",
    )
    acquisition = build_evidence_acquisition_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        synthesis=synthesis,
        additional_links=(link,),
        policy=build_default_evidence_acquisition_policy(),
        created_at="2026-09-11T14:50:00-03:00",
    )

    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
        acquisition_plans=(acquisition,),
        created_at=CREATED_AT,
    )
    candidate = view.hypotheses[0].acquisition_candidates[0]
    assert candidate.candidate_kind == "potential_contradiction"
    assert candidate.source_game_id == "m44-game"

    html = build_learner_progress_reference_surface(view).html
    assert "potential_contradiction" in html
    assert "M43 acquisition plan" not in html


def test_m44_renders_missing_optional_layers_as_unavailable_not_negative_evidence():
    ontology = OntologyRegistry.load_default()
    _, read_model, synthesis, plan = _teaching_sources()
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
        created_at=CREATED_AT,
    )
    html = build_learner_progress_reference_surface(view).html

    assert "No M43 acquisition plan supplied" in html
    assert "No M41 intervention candidate set supplied" in html
    assert "Mastery: not established" in html
    assert "mastered" not in html.lower()


def test_m44_html_escapes_learner_evidence_text():
    ontology = OntologyRegistry.load_default()
    entry = replace(
        _entry(),
        statement='<script>alert("learner")</script>',
        scope_definition="<b>scope</b>",
    )
    read_model = _read_model(entry)
    synthesis = replace(
        _synthesis(read_model, entry, contradiction_count=1),
        evidence_gaps=("<img src=x onerror=alert(1)>",),
    )
    plan = _plan(read_model, synthesis)

    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
        created_at=CREATED_AT,
    )
    html = build_learner_progress_reference_surface(view).html

    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;scope&lt;/b&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html


def test_m44_preserves_m40_priority_order_across_hypotheses():
    ontology = OntologyRegistry.load_default()
    contradicted = _entry("h1", status="contradicted")
    teaching = _entry("h2")
    read_model = _read_model(contradicted, teaching)
    syntheses = (
        _synthesis(read_model, contradicted, contradiction_count=1),
        _synthesis(read_model, teaching, contradiction_count=1),
    )
    plan = _plan(read_model, *syntheses)
    assert plan.selected_candidate.hypothesis_id == "h1"

    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=syntheses,
        next_session_plan=plan,
        ontology=ontology,
        created_at=CREATED_AT,
    )

    assert tuple(item.hypothesis_id for item in view.hypotheses) == ("h1", "h2")
    assert tuple(item.priority_rank for item in view.hypotheses) == (1, 2)
    assert view.hypotheses[0].next_action == "PRESENT_CONTROL"


def test_m44_rejects_missing_or_extra_m39_source_set():
    ontology = OntologyRegistry.load_default()
    _, read_model, synthesis, plan = _teaching_sources()

    with pytest.raises(ValueError, match="exact M39 synthesis set"):
        build_learner_progress_view(
            learner_read_model=read_model,
            evidence_syntheses=(),
            next_session_plan=plan,
            ontology=ontology,
            created_at=CREATED_AT,
        )

    extra = replace(
        synthesis,
        synthesis_id="extra-synthesis",
        fingerprint="extra-fingerprint",
    )
    with pytest.raises(ValueError, match="exact M39 synthesis set"):
        build_learner_progress_view(
            learner_read_model=read_model,
            evidence_syntheses=(synthesis, extra),
            next_session_plan=plan,
            ontology=ontology,
            created_at=CREATED_AT,
        )


def test_m44_rejects_cross_participant_m41_and_m43_sources():
    ontology = OntologyRegistry.load_default()
    _, read_model, synthesis, plan = _teaching_sources()
    candidate_set = _candidate_set(ontology, plan, synthesis)
    with pytest.raises(ValueError, match="M41 participant mismatch"):
        build_learner_progress_view(
            learner_read_model=read_model,
            evidence_syntheses=(synthesis,),
            next_session_plan=plan,
            ontology=ontology,
            intervention_candidate_sets=(
                replace(candidate_set, participant_id="P02"),
            ),
            created_at=CREATED_AT,
        )

    challenge_synthesis = _synthesis(read_model, _entry(), contradiction_count=0)
    challenge_plan = _plan(read_model, challenge_synthesis)
    link = _link(
        challenge_plan.selected_candidate.hypothesis_revision_ref,
        "cross-link",
        "contradicts",
        "cross-position",
        "cross-game",
    )
    acquisition = build_evidence_acquisition_plan(
        next_session_plan=challenge_plan,
        proposal=challenge_plan.selected_candidate,
        synthesis=challenge_synthesis,
        additional_links=(link,),
        policy=build_default_evidence_acquisition_policy(),
        created_at="2026-09-11T14:50:00-03:00",
    )
    with pytest.raises(ValueError, match="M43 participant mismatch"):
        build_learner_progress_view(
            learner_read_model=read_model,
            evidence_syntheses=(challenge_synthesis,),
            next_session_plan=challenge_plan,
            ontology=ontology,
            acquisition_plans=(replace(acquisition, participant_id="P02"),),
            created_at=CREATED_AT,
        )


def test_m44_view_and_surface_are_rebuildable_and_tamper_detectable():
    ontology = OntologyRegistry.load_default()
    _, read_model, synthesis, plan = _teaching_sources()
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
        created_at=CREATED_AT,
    )
    validate_learner_progress_view(
        view,
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=ontology,
    )
    with pytest.raises(ValueError, match="view mismatch"):
        validate_learner_progress_view(
            replace(view, participant_id="P02"),
            learner_read_model=read_model,
            evidence_syntheses=(synthesis,),
            next_session_plan=plan,
            ontology=ontology,
        )

    surface = build_learner_progress_reference_surface(view)
    validate_learner_progress_reference_surface(surface, view=view)
    with pytest.raises(ValueError, match="surface mismatch"):
        validate_learner_progress_reference_surface(
            replace(surface, html=surface.html + "tampered"),
            view=view,
        )
