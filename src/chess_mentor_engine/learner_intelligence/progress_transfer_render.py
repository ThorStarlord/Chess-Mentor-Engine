"""M44 additive presentation for exact M42 transfer/retest plans.

The existing M44 v1 learner-progress view remains unchanged. This module layers
planning-only M42 information onto that exact view without manufacturing M10
outcome evidence, transfer success, or mastery.
"""

from __future__ import annotations

import hashlib
import html
from dataclasses import dataclass
from typing import Any

from chess_mentor_engine.chess import canonical_json

from .evidence_synthesis import EvidenceSynthesisReference
from .progress_model import LearnerProgressView
from .progress_render import render_learner_progress_html
from .transfer_retest import TransferRetestPlan

LEARNER_PROGRESS_TRANSFER_SURFACE_SCHEMA_VERSION = (
    "m44.learner-progress-transfer-reference-surface.v1"
)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _view_ref(view: LearnerProgressView) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "learner_progress_view",
        view.view_id,
        view.fingerprint,
    )


def _plan_ref(plan: TransferRetestPlan) -> EvidenceSynthesisReference:
    return EvidenceSynthesisReference(
        "transfer_retest_plan",
        plan.transfer_plan_id,
        plan.fingerprint,
    )


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _list_html(values: tuple[str, ...], *, empty: str) -> str:
    if not values:
        return f'<p class="muted">{_esc(empty)}</p>'
    items = "".join(f"<li>{_esc(value)}</li>" for value in values)
    return f"<ul>{items}</ul>"


def _validate_view_identity(view: LearnerProgressView) -> None:
    expected = _digest(view.identity_payload())
    if view.fingerprint != expected:
        raise ValueError("M44 learner-progress view fingerprint mismatch")
    if view.view_id != f"learner_progress_view_{expected[:20]}":
        raise ValueError("M44 learner-progress view identity mismatch")


def _validate_transfer_sources(
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...],
) -> None:
    _validate_view_identity(view)
    hypotheses = {item.hypothesis_id: item for item in view.hypotheses}
    seen: set[str] = set()
    for plan in transfer_plans:
        expected = _digest(plan.identity_payload())
        if plan.fingerprint != expected:
            raise ValueError("M44 M42 transfer-plan fingerprint mismatch")
        if plan.transfer_plan_id != f"transfer_retest_plan_{expected[:20]}":
            raise ValueError("M44 M42 transfer-plan identity mismatch")
        if plan.hypothesis_id in seen:
            raise ValueError("M44 accepts at most one M42 plan per hypothesis")
        seen.add(plan.hypothesis_id)
        hypothesis = hypotheses.get(plan.hypothesis_id)
        if hypothesis is None:
            raise ValueError("M44 M42 plan references unknown hypothesis")
        if plan.participant_id != view.participant_id:
            raise ValueError("M44 M42 participant mismatch")
        if plan.next_session_plan_ref != view.next_session_plan_ref:
            raise ValueError("M44 M42/M40 next-session-plan identity mismatch")
        if plan.hypothesis_revision_ref != hypothesis.current_revision_ref:
            raise ValueError("M44 M42 current-revision mismatch")
        expected_action = (
            "RUN_NEAR_TRANSFER_TEST"
            if plan.transfer_kind == "near"
            else "RUN_FAR_TRANSFER_TEST"
        )
        if hypothesis.next_action != expected_action:
            raise ValueError("M44 M42 transfer kind does not match M40 action")


@dataclass(frozen=True, slots=True)
class LearnerProgressTransferReferenceSurface:
    surface_id: str
    fingerprint: str
    view_ref: EvidenceSynthesisReference
    transfer_plan_refs: tuple[EvidenceSynthesisReference, ...]
    html: str
    claim_scope: str = "local_reference_presentation_only"
    schema_version: str = LEARNER_PROGRESS_TRANSFER_SURFACE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.surface_id:
            raise ValueError("surface_id must not be empty")
        if not self.fingerprint:
            raise ValueError("fingerprint must not be empty")
        if not self.html:
            raise ValueError("html must not be empty")
        if self.schema_version != LEARNER_PROGRESS_TRANSFER_SURFACE_SCHEMA_VERSION:
            raise ValueError("unsupported M44 transfer reference-surface schema")
        if self.claim_scope != "local_reference_presentation_only":
            raise ValueError("M44 transfer surface cannot claim production UI authority")
        keys = tuple(
            (item.kind, item.ref_id, item.fingerprint)
            for item in self.transfer_plan_refs
        )
        if len(set(keys)) != len(keys):
            raise ValueError("M44 transfer plan refs must be unique")

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "view_ref": self.view_ref.to_dict(),
            "transfer_plan_refs": [item.to_dict() for item in self.transfer_plan_refs],
            "html": self.html,
            "claim_scope": self.claim_scope,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "fingerprint": self.fingerprint,
            **self.identity_payload(),
        }


def _transfer_plan_html(plan: TransferRetestPlan, statement: str) -> str:
    if plan.selected_candidate is None:
        candidate_html = (
            '<p class="muted">No eligible transfer position is currently planned.</p>'
            + _list_html(
                plan.blocking_uncertainty,
                empty="No blocking uncertainty recorded.",
            )
        )
    else:
        candidate = plan.selected_candidate
        held = _list_html(candidate.held_constant, empty="Nothing recorded.")
        varied = _list_html(candidate.varied_dimensions, empty="Nothing recorded.")
        concepts = _list_html(
            candidate.concept_ids,
            empty="No ontology concept IDs supplied for this candidate.",
        )
        candidate_html = (
            f'<p><strong>Position:</strong> {_esc(candidate.position.position_id)} '
            f'in game {_esc(candidate.position.game_id)}</p>'
            f'<p><strong>Semantic relation:</strong> '
            f'{_esc(candidate.semantic_relation)}</p>'
            f'<p><strong>Surface variation:</strong> '
            f'{_esc(candidate.surface_variation)}</p>'
            f'<p><strong>Freshness:</strong> {_esc(candidate.freshness)}</p>'
            '<p class="label">Held constant</p>'
            f"{held}"
            '<p class="label">Varied dimensions</p>'
            f"{varied}"
            '<p class="label">Candidate concept IDs</p>'
            f"{concepts}"
        )
    return (
        '<article class="card transfer-plan">'
        f"<h3>{_esc(statement)}</h3>"
        f'<p><strong>Transfer kind:</strong> {_esc(plan.transfer_kind)}</p>'
        f'<p><strong>Planning status:</strong> {_esc(plan.planning_status)}</p>'
        f'<p><strong>Measurement target:</strong> '
        f'{_esc(plan.measurement_target)}</p>'
        f"{candidate_html}"
        '<p class="muted">M42 is planning-only: planned does not mean completed; '
        'completed does not establish successful transfer; transfer does not '
        'establish mastery.</p>'
        "</article>"
    )


def render_learner_progress_transfer_html(
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...],
) -> str:
    """Render the exact M44 view plus optional exact M42 planning information."""
    _validate_transfer_sources(view, transfer_plans)
    base = render_learner_progress_html(view)
    statements = {item.hypothesis_id: item.statement for item in view.hypotheses}
    if transfer_plans:
        cards = "".join(
            _transfer_plan_html(plan, statements[plan.hypothesis_id])
            for plan in transfer_plans
        )
    else:
        cards = (
            '<p class="muted">No M42 transfer/retest plan was supplied.</p>'
        )
    block = (
        '<section class="section" id="transfer-retest-plans">'
        "<h2>Next transfer / retest</h2>"
        f"{cards}"
        "</section>"
    )
    if "</main>" not in base:
        raise ValueError("M44 base reference HTML is missing main boundary")
    return base.replace("</main>", f"{block}</main>", 1)


def build_learner_progress_transfer_reference_surface(
    *,
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
) -> LearnerProgressTransferReferenceSurface:
    """Build a content-addressed additive M44 surface over exact M42 plans."""
    rendered = render_learner_progress_transfer_html(view, transfer_plans)
    refs = tuple(_plan_ref(item) for item in transfer_plans)
    payload = {
        "schema_version": LEARNER_PROGRESS_TRANSFER_SURFACE_SCHEMA_VERSION,
        "view_ref": _view_ref(view).to_dict(),
        "transfer_plan_refs": [item.to_dict() for item in refs],
        "html": rendered,
        "claim_scope": "local_reference_presentation_only",
    }
    fingerprint = _digest(payload)
    return LearnerProgressTransferReferenceSurface(
        surface_id=f"learner_progress_transfer_surface_{fingerprint[:20]}",
        fingerprint=fingerprint,
        view_ref=_view_ref(view),
        transfer_plan_refs=refs,
        html=rendered,
    )


def validate_learner_progress_transfer_reference_surface(
    surface: LearnerProgressTransferReferenceSurface,
    *,
    view: LearnerProgressView,
    transfer_plans: tuple[TransferRetestPlan, ...] = (),
) -> None:
    expected = build_learner_progress_transfer_reference_surface(
        view=view,
        transfer_plans=transfer_plans,
    )
    if expected != surface:
        raise ValueError("M44 transfer reference-surface mismatch")
