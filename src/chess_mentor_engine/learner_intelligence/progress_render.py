"""M44 deterministic local learner-progress reference rendering."""

from __future__ import annotations

import hashlib
import html
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json

from .evidence_synthesis import EvidenceSynthesisReference
from .progress_model import (
    LearnerProgressHypothesis,
    LearnerProgressView,
    ProgressConcept,
)

LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION = (
    "m44.learner-progress-reference-surface.v1"
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class LearnerProgressReferenceSurface:
    surface_id: str
    fingerprint: str
    view_ref: EvidenceSynthesisReference
    html: str
    claim_scope: str = "local_reference_presentation_only"
    schema_version: str = LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("surface_id", self.surface_id)
        _nonempty("fingerprint", self.fingerprint)
        _nonempty("html", self.html)
        if self.schema_version != LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION:
            raise ValueError("unsupported M44 reference-surface schema")
        if self.claim_scope != "local_reference_presentation_only":
            raise ValueError("M44 surface cannot claim production UI authority")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "view_ref": self.view_ref.to_dict(),
            "html": self.html,
            "claim_scope": self.claim_scope,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _list_html(values: tuple[str, ...], *, empty: str) -> str:
    if not values:
        return f'<p class="muted">{_esc(empty)}</p>'
    items = "".join(f"<li>{_esc(value)}</li>" for value in values)
    return f"<ul>{items}</ul>"


def _concept_html(concepts: tuple[ProgressConcept, ...]) -> str:
    if not concepts:
        return (
            '<p class="muted">'
            "Ontology context unavailable or not supplied."
            "</p>"
        )
    parts: list[str] = []
    for concept in concepts:
        questions = _list_html(
            concept.recognition_questions,
            empty="No recognition questions recorded.",
        )
        parts.append(
            '<article class="concept">'
            f"<h4>{_esc(concept.preferred_name)}</h4>"
            f'<p class="meta">{_esc(concept.concept_id)} · '
            f"{_esc(concept.kind)}</p>"
            '<p class="label">Instructional recognition cues</p>'
            f"{questions}"
            "</article>"
        )
    return "".join(parts)


def _evidence_html(hypothesis: LearnerProgressHypothesis) -> str:
    counts = hypothesis.evidence_counts
    if counts is None:
        return '<p class="muted">M39 evidence synthesis unavailable.</p>'
    count_rows = (
        ("Support units", counts.support_unit_count),
        ("Independent support", counts.independent_support_count),
        ("Contradictions", counts.contradiction_unit_count),
        ("Successful counterexamples", counts.successful_counterexample_unit_count),
        ("Context exceptions", counts.context_exception_unit_count),
        ("Unclear", counts.unclear_unit_count),
        ("Mixed", counts.mixed_unit_count),
    )
    rows = "".join(
        f"<tr><th>{_esc(label)}</th><td>{value}</td></tr>"
        for label, value in count_rows
    )
    unit_items = "".join(
        "<li>"
        f"{_esc(item.relation)} — game {_esc(item.source_game_id)}, "
        f"position {_esc(item.source_position_id)}"
        "</li>"
        for item in hypothesis.evidence_units
    )
    if unit_items:
        units = f"<ul>{unit_items}</ul>"
    else:
        units = (
            '<p class="muted">'
            "No recurrence-unit details supplied in this synthesis."
            "</p>"
        )
    return (
        f'<table class="evidence"><tbody>{rows}</tbody></table>'
        '<p class="label">Traceable recurrence units</p>'
        f"{units}"
    )


def _training_html(hypothesis: LearnerProgressHypothesis) -> str:
    selected = tuple(
        f"{item.intervention_key} (v{item.version})"
        for item in hypothesis.selected_interventions
    )
    selected_html = _list_html(
        selected,
        empty=(
            "No M9 selected intervention is represented in the current M36 state."
        ),
    )
    outcomes = tuple(
        f"{kind}: {status}" for kind, status in hypothesis.outcome_statuses
    )
    outcomes_html = _list_html(
        outcomes,
        empty=(
            "No M10 outcome dimension is represented in the current M36 state."
        ),
    )
    return (
        f'<p><strong>M9 state:</strong> {_esc(hypothesis.intervention_state)}</p>'
        '<p class="label">Selected interventions</p>'
        f"{selected_html}"
        '<p class="label">M10 practice / transfer state</p>'
        f"{outcomes_html}"
        '<p class="muted">Mastery is not established by this reference view.</p>'
    )


def _acquisition_html(hypothesis: LearnerProgressHypothesis) -> str:
    if hypothesis.acquisition_ref is None:
        return '<p class="muted">No M43 acquisition plan supplied.</p>'
    items = tuple(
        (
            f"{item.candidate_kind}: game {item.source_game_id}, "
            f"position {item.source_position_id}"
        )
        for item in hypothesis.acquisition_candidates
    )
    return (
        f'<p><strong>Intent:</strong> {_esc(hypothesis.acquisition_intent)}</p>'
        + _list_html(items, empty="No eligible M43 evidence candidates.")
        + '<p class="label">M43 gaps</p>'
        + _list_html(
            hypothesis.acquisition_gaps,
            empty="No M43 gaps recorded.",
        )
    )


def _matching_html(hypothesis: LearnerProgressHypothesis) -> str:
    if hypothesis.intervention_candidate_set_ref is None:
        return (
            '<p class="muted">'
            "No M41 intervention candidate set supplied."
            "</p>"
        )
    items = tuple(
        (
            f"{item.intervention_ref.intervention_key} "
            f"(v{item.intervention_ref.version}) — {item.status}"
        )
        for item in hypothesis.intervention_candidates
    )
    return (
        _list_html(items, empty="No M41 intervention candidates.")
        + '<p class="label">Unverified pedagogical prerequisites</p>'
        + _list_html(
            hypothesis.unverified_prerequisites,
            empty="No prerequisites recorded for the current match context.",
        )
        + '<p class="label">M41 gaps</p>'
        + _list_html(
            hypothesis.matching_gaps,
            empty="No M41 gaps recorded.",
        )
        + '<p class="muted">'
        "M9 selection authority has not been exercised here."
        "</p>"
    )


def _hypothesis_html(hypothesis: LearnerProgressHypothesis) -> str:
    if hypothesis.priority_rank is None:
        priority = "Not ranked by the current M40 plan"
    else:
        priority = f"Priority {hypothesis.priority_rank}"
    action = "Unavailable" if hypothesis.next_action is None else hypothesis.next_action
    status = hypothesis.m7_status or "unavailable"
    status_reasons = _list_html(
        hypothesis.status_reasons,
        empty="M39 synthesis unavailable.",
    )
    evidence_gaps = _list_html(
        hypothesis.evidence_gaps,
        empty="No M39 gap recorded.",
    )
    change_conditions = _list_html(
        hypothesis.change_conditions,
        empty="No M39 change condition supplied.",
    )
    action_reasons = _list_html(
        hypothesis.next_action_reasons,
        empty="No M40 action supplied.",
    )
    blocking = _list_html(
        hypothesis.blocking_uncertainty,
        empty="None recorded.",
    )
    return (
        '<section class="hypothesis">'
        f"<h2>{_esc(priority)} — {_esc(hypothesis.statement)}</h2>"
        f'<p class="meta">Hypothesis {_esc(hypothesis.hypothesis_id)} · '
        f"lifecycle {_esc(hypothesis.lifecycle_state)}</p>"
        '<div class="grid">'
        '<article><h3>Current learner hypothesis</h3>'
        f"<p>{_esc(hypothesis.statement)}</p>"
        f'<p class="meta">Scope: {_esc(hypothesis.scope_definition)}</p>'
        f'<p><strong>M7C status:</strong> {_esc(status)}</p>'
        '<p class="label">Why this status is represented</p>'
        f"{status_reasons}"
        "</article>"
        '<article><h3>Evidence</h3>'
        f"{_evidence_html(hypothesis)}"
        "</article>"
        '<article><h3>Chess concepts</h3>'
        f"{_concept_html(hypothesis.concepts)}"
        '<p class="muted">'
        "Ontology concepts describe chess semantics; they do not by themselves "
        "establish learner weakness."
        "</p></article>"
        '<article><h3>Training / transfer</h3>'
        f"{_training_html(hypothesis)}"
        "</article>"
        '<article><h3>Uncertainty and change conditions</h3>'
        '<p class="label">Evidence gaps</p>'
        f"{evidence_gaps}"
        '<p class="label">What could change the current assessment</p>'
        f"{change_conditions}"
        "</article>"
        '<article><h3>Next proposed action</h3>'
        f"<p><strong>{_esc(action)}</strong></p>"
        f"{action_reasons}"
        '<p class="label">Blocking uncertainty</p>'
        f"{blocking}"
        '<p class="muted">'
        "M40 is proposal-only; this surface does not authorize execution."
        "</p></article>"
        '<article><h3>Challenge / control candidates</h3>'
        f"{_acquisition_html(hypothesis)}"
        "</article>"
        '<article><h3>Training candidates</h3>'
        f"{_matching_html(hypothesis)}"
        "</article>"
        "</div>"
        "</section>"
    )


def _style_html() -> str:
    return (
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto;"
        "padding:2rem;line-height:1.5}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,"
        "minmax(280px,1fr));gap:1rem}"
        ".hypothesis{border-top:3px solid #333;margin-top:2rem;"
        "padding-top:1rem}"
        "article{border:1px solid #bbb;border-radius:.5rem;padding:1rem}"
        ".meta,.muted{color:#555}.label{font-weight:600;margin-bottom:.25rem}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{text-align:left;border-bottom:1px solid #ddd;padding:.25rem}"
        "code{word-break:break-all}"
        "</style>"
    )


def render_learner_progress_html(view: LearnerProgressView) -> str:
    """Render escaped semantic HTML from an already-built M44 view."""
    if _digest(view.identity_payload()) != view.fingerprint:
        raise ValueError("M44 learner-progress view fingerprint mismatch")
    expected_id = f"learner_progress_view_{view.fingerprint[:20]}"
    if view.view_id != expected_id:
        raise ValueError("M44 learner-progress view identity mismatch")
    sections = "".join(_hypothesis_html(item) for item in view.hypotheses)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Chess Mentor Engine — Learner Progress</title>"
        f"{_style_html()}"
        "</head><body>"
        "<header><h1>Chess Mentor Engine — Learner Progress</h1>"
        f"<p>Participant: <strong>{_esc(view.participant_id)}</strong></p>"
        '<p class="muted">'
        "Local deterministic reference surface. Evidence, learner hypotheses, "
        "ontology semantics, pedagogical candidates, and action policy remain "
        "separate authority layers."
        "</p></header>"
        f"{sections}"
        '<footer><p class="muted">'
        "Causal effect: not established. Mastery: not established. This surface "
        "creates no new learner-state or execution authority."
        "</p></footer></body></html>"
    )


def learner_progress_view_ref(
    view: LearnerProgressView,
) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_progress_view",
        view.view_id,
        view.fingerprint,
    )


def build_learner_progress_reference_surface(
    view: LearnerProgressView,
) -> LearnerProgressReferenceSurface:
    html_text = render_learner_progress_html(view)
    payload = {
        "schema_version": LEARNER_PROGRESS_SURFACE_SCHEMA_VERSION,
        "view_ref": learner_progress_view_ref(view).to_dict(),
        "html": html_text,
        "claim_scope": "local_reference_presentation_only",
    }
    fingerprint = _digest(payload)
    return LearnerProgressReferenceSurface(
        surface_id=f"learner_progress_surface_{fingerprint[:20]}",
        fingerprint=fingerprint,
        view_ref=learner_progress_view_ref(view),
        html=html_text,
    )


def validate_learner_progress_reference_surface(
    surface: LearnerProgressReferenceSurface,
    *,
    view: LearnerProgressView,
) -> None:
    expected = build_learner_progress_reference_surface(view)
    if expected != surface:
        raise ValueError("M44 learner-progress reference surface mismatch")
