from __future__ import annotations

from dataclasses import replace

import pytest
from test_m42_transfer_retest_planning import _candidate, _sources
from test_m40_next_session_planner import _entry, _read_model, _synthesis

from chess_mentor_engine.chess_knowledge import OntologyRegistry
from chess_mentor_engine.learner_intelligence import (
    build_default_transfer_retest_policy,
    build_learner_progress_transfer_reference_surface,
    build_learner_progress_view,
    build_transfer_retest_plan,
    render_learner_progress_transfer_html,
    validate_learner_progress_transfer_reference_surface,
)


def _view_and_transfer(*, measurement_target: str = "Transfer target."):
    entry = _entry(
        intervention_state="selected",
        outcomes=(("practice", "supported"),),
    )
    read_model = _read_model(entry)
    synthesis = _synthesis(read_model, entry, contradiction_count=1)
    plan, intervention, selection = _sources()
    candidate = _candidate(
        "m44-transfer-1",
        "m44-transfer-game",
        "8/8/8/8/8/8/8/K6k w - - 0 1",
    )
    transfer = build_transfer_retest_plan(
        next_session_plan=plan,
        proposal=plan.selected_candidate,
        selection=selection,
        intervention=intervention,
        candidate_positions=(candidate,),
        practice_position_reuse_keys=(),
        measurement_target=measurement_target,
        policy=build_default_transfer_retest_policy(),
        created_at="2026-09-11T16:30:00-03:00",
        ontology=OntologyRegistry.load_default(),
    )
    view = build_learner_progress_view(
        learner_read_model=read_model,
        evidence_syntheses=(synthesis,),
        next_session_plan=plan,
        ontology=OntologyRegistry.load_default(),
        created_at="2026-09-11T16:35:00-03:00",
    )
    return view, transfer


def test_m44_additive_surface_presents_exact_m42_plan_without_outcome_promotion():
    view, transfer = _view_and_transfer()
    surface = build_learner_progress_transfer_reference_surface(
        view=view,
        transfer_plans=(transfer,),
    )

    assert surface.claim_scope == "local_reference_presentation_only"
    assert "Next transfer / retest" in surface.html
    assert "Transfer kind:</strong> near" in surface.html
    assert "Planning status:</strong> planned" in surface.html
    assert "m44-transfer-1" in surface.html
    assert "same_target" in surface.html
    assert "planned does not mean completed" in surface.html
    assert "transfer does not establish mastery" in surface.html

    validate_learner_progress_transfer_reference_surface(
        surface,
        view=view,
        transfer_plans=(transfer,),
    )


def test_m44_additive_surface_preserves_existing_view_and_handles_missing_m42():
    view, _ = _view_and_transfer()
    html = render_learner_progress_transfer_html(view, ())

    assert "Learner Progress" in html
    assert "No M42 transfer/retest plan was supplied." in html
    assert view.schema_version == "m44.learner-progress-view.v1"


def test_m44_additive_surface_escapes_m42_measurement_text():
    view, transfer = _view_and_transfer(
        measurement_target='<script>alert("transfer")</script>',
    )
    html = render_learner_progress_transfer_html(view, (transfer,))

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_m44_additive_surface_rejects_tampered_or_duplicate_m42_plans():
    view, transfer = _view_and_transfer()

    with pytest.raises(ValueError, match="transfer-plan fingerprint mismatch"):
        render_learner_progress_transfer_html(
            view,
            (replace(transfer, measurement_target="tampered"),),
        )

    with pytest.raises(ValueError, match="at most one M42 plan"):
        render_learner_progress_transfer_html(view, (transfer, transfer))


def test_m44_additive_surface_rejects_m42_plan_for_different_m40_identity():
    view, transfer = _view_and_transfer()
    foreign_ref = replace(
        transfer.next_session_plan_ref,
        ref_id="foreign-next-session-plan",
    )
    tampered = replace(
        transfer,
        next_session_plan_ref=foreign_ref,
        fingerprint="temporarily-valid-shaped-but-wrong",
    )

    with pytest.raises(ValueError, match="transfer-plan fingerprint mismatch"):
        render_learner_progress_transfer_html(view, (tampered,))
