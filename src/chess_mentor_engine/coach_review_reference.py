"""M28 deterministic local HTML reference surface over the M25 read model."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html import escape
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.review import (
    COACH_REVIEW_SCHEMA_VERSION,
    build_coach_review_read_model_from_bundle,
)

M28_SCHEMA_VERSION = "m28.coach-review-reference-surface.v1"
M28_CLAIM_SCOPE = "local_reference_presentation_only"

SECTION_ORDER = (
    "objective_evidence",
    "diagnostic_selection",
    "participant_authority",
    "tutor_state",
    "deterministic_grounding",
    "model_coaching",
    "model_evaluation",
)

_SECTION_TITLES = {
    "objective_evidence": "Objective evidence",
    "diagnostic_selection": "Diagnostic selection",
    "participant_authority": "Participant authority",
    "tutor_state": "Tutor state",
    "deterministic_grounding": "Deterministic grounding",
    "model_coaching": "Model coaching",
    "model_evaluation": "Model evaluation",
}

_SECTION_SOURCES = {
    "objective_evidence": "M15 objective evidence",
    "diagnostic_selection": "M18 diagnostic selection",
    "participant_authority": "M21 participant authorization",
    "tutor_state": "M8 workflow state",
    "deterministic_grounding": "M16 deterministic feedback",
    "model_coaching": "M19 model language",
    "model_evaluation": "M20 bounded quality assessment",
}

_EXPECTED_SEPARATION_CONTRACT = {
    "objective_chess_source": "objective_evidence",
    "score_semantics_source": "objective_evidence.score_semantics",
    "diagnostic_selection_source": "diagnostic_selection",
    "participant_authority_source": "participant_authority",
    "workflow_state_source": "tutor_state",
    "deterministic_feedback_source": "deterministic_grounding",
    "model_language_source": "model_coaching",
    "bounded_quality_assessment_source": "model_evaluation",
    "model_evaluation_truth_status": "not_established_by_m20_evaluation",
}

_READ_MODEL_KEYS = {
    "schema_version",
    "section_order",
    "separation_contract",
    "source_fingerprints",
    "objective_evidence",
    "diagnostic_selection",
    "participant_authority",
    "tutor_state",
    "deterministic_grounding",
    "model_coaching",
    "model_evaluation",
    "read_model_id",
    "fingerprint",
}


class CoachReviewReferenceError(ValueError):
    """M28 cannot render the supplied M25 read model without semantic drift."""


@dataclass(frozen=True, slots=True)
class CoachReviewReferenceSurface:
    """One deterministic local HTML surface and its exact M25 source identity."""

    surface_id: str
    fingerprint: str
    html: str
    read_model: dict[str, Any]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _fingerprint(value: object) -> str:
    return _sha256_text(canonical_json(value))


def _display(value: object) -> str:
    if value is None:
        return "Unavailable"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) in {dict, list}:
        return canonical_json(value)
    return str(value)


def _e(value: object) -> str:
    return escape(_display(value), quote=True)


def _slug(value: str) -> str:
    return "-".join(part for part in value.lower().replace("_", "-").split("-") if part)


def _dl(rows: tuple[tuple[str, object], ...]) -> str:
    lines = ["<dl>"]
    for label, value in rows:
        lines.append(f"<dt>{_e(label)}</dt>")
        lines.append(f"<dd>{_e(value)}</dd>")
    lines.append("</dl>")
    return "\n".join(lines)


def _table(
    caption: str,
    headers: tuple[str, ...],
    rows: tuple[tuple[object, ...], ...],
) -> str:
    lines = ["<table>", f"<caption>{_e(caption)}</caption>", "<thead>", "<tr>"]
    for header in headers:
        lines.append(f'<th scope="col">{_e(header)}</th>')
    lines.extend(("</tr>", "</thead>", "<tbody>"))
    for row in rows:
        lines.append("<tr>")
        for item in row:
            lines.append(f"<td>{_e(item)}</td>")
        lines.append("</tr>")
    lines.extend(("</tbody>", "</table>"))
    return "\n".join(lines)


def _source_details(label: str, value: object) -> str:
    if value is None:
        return ""
    return "\n".join(
        (
            "<details>",
            f"<summary>{_e(label)}</summary>",
            f"<pre>{escape(canonical_json(value), quote=True)}</pre>",
            "</details>",
        )
    )


def _validate_read_model(read_model: Any) -> dict[str, Any]:
    if type(read_model) is not dict or set(read_model) != _READ_MODEL_KEYS:
        raise CoachReviewReferenceError("M25 read-model shape mismatch")
    if read_model["schema_version"] != COACH_REVIEW_SCHEMA_VERSION:
        raise CoachReviewReferenceError("M25 read-model schema mismatch")
    if tuple(read_model["section_order"]) != SECTION_ORDER:
        raise CoachReviewReferenceError("M25 section order drifted")
    if read_model["separation_contract"] != _EXPECTED_SEPARATION_CONTRACT:
        raise CoachReviewReferenceError("M25 separation contract drifted")

    payload = {
        key: value
        for key, value in read_model.items()
        if key not in {"read_model_id", "fingerprint"}
    }
    expected = _fingerprint(payload)
    if read_model["fingerprint"] != expected:
        raise CoachReviewReferenceError("M25 read-model fingerprint mismatch")
    if read_model["read_model_id"] != f"coach_review_{expected[:20]}":
        raise CoachReviewReferenceError("M25 read-model identity mismatch")
    return read_model


def _evaluation_summary(value: Any) -> str:
    if value is None:
        return "Unavailable"
    if type(value) is not dict:
        raise CoachReviewReferenceError("evaluation must be an object")
    kind = value.get("kind")
    mover = value.get("decision_mover")
    white = value.get("white")
    if type(mover) is not dict or type(white) is not dict:
        raise CoachReviewReferenceError("evaluation perspectives are malformed")
    if kind == "centipawn":
        return (
            f"White={white.get('centipawns')} centipawns "
            f"({white.get('bound')}); decision mover {mover.get('side')}="
            f"{mover.get('centipawns')} centipawns ({mover.get('bound')})"
        )
    if kind == "mate":
        return (
            f"winner={value.get('winner')}; "
            f"plies_to_mate={value.get('plies_to_mate')}; "
            f"decision mover {mover.get('side')} favours_perspective="
            f"{_display(mover.get('favours_perspective'))}; bound={mover.get('bound')}"
        )
    raise CoachReviewReferenceError(f"unsupported evaluation kind: {kind!r}")


def _render_evaluation(label: str, value: Any) -> str:
    element_id = f"evaluation-{_slug(label)}"
    if value is None:
        return "\n".join(
            (
                f'<section aria-labelledby="{element_id}">',
                f'<h3 id="{element_id}">{_e(label)}</h3>',
                '<p data-state="unavailable">Unavailable.</p>',
                "</section>",
            )
        )
    if type(value) is not dict:
        raise CoachReviewReferenceError(f"{label} must be an object")
    kind = value.get("kind")
    if kind == "centipawn":
        white = value.get("white")
        mover = value.get("decision_mover")
        if type(white) is not dict or type(mover) is not dict:
            raise CoachReviewReferenceError(f"{label} perspective shape mismatch")
        body = _table(
            f"{label} score perspectives",
            ("Perspective", "Side", "Value", "Bound"),
            (
                (
                    "Canonical engine",
                    "white",
                    f"{white.get('centipawns')} centipawns",
                    white.get("bound"),
                ),
                (
                    "Decision mover",
                    mover.get("side"),
                    f"{mover.get('centipawns')} centipawns",
                    mover.get("bound"),
                ),
            ),
        )
    elif kind == "mate":
        white = value.get("white")
        mover = value.get("decision_mover")
        if type(white) is not dict or type(mover) is not dict:
            raise CoachReviewReferenceError(f"{label} mate perspective shape mismatch")
        body = _dl(
            (
                ("Kind", "mate"),
                ("Winner", value.get("winner")),
                ("Plies to mate", value.get("plies_to_mate")),
                ("White favours perspective", white.get("favours_perspective")),
                ("White bound", white.get("bound")),
                ("Decision mover", mover.get("side")),
                (
                    "Mover favours perspective",
                    mover.get("favours_perspective"),
                ),
                ("Mover bound", mover.get("bound")),
            )
        )
    else:
        raise CoachReviewReferenceError(f"unsupported {label} kind: {kind!r}")
    return "\n".join(
        (
            f'<section aria-labelledby="{element_id}">',
            f'<h3 id="{element_id}">{_e(label)}</h3>',
            body,
            "</section>",
        )
    )


def _render_analysis(label: str, value: Any) -> str:
    element_id = f"analysis-{_slug(label)}"
    if value is None:
        return "\n".join(
            (
                f'<section aria-labelledby="{element_id}">',
                f'<h3 id="{element_id}">{_e(label)}</h3>',
                '<p data-state="not-present">Not present.</p>',
                "</section>",
            )
        )
    if type(value) is not dict:
        raise CoachReviewReferenceError(f"{label} must be an object")

    rows: list[tuple[str, object]] = [
        ("Status", value.get("status")),
        ("Evidence quality", value.get("evidence_quality")),
        ("Position id", value.get("position_id")),
        ("FEN", value.get("fen")),
        ("Request fingerprint", value.get("request_fingerprint")),
        ("Result fingerprint", value.get("result_fingerprint")),
    ]
    engine = value.get("engine")
    if type(engine) is dict:
        rows.extend(
            (
                ("Engine provider", engine.get("provider_name")),
                ("Provider version", engine.get("provider_version")),
                ("Protocol", engine.get("protocol")),
                ("Engine name", engine.get("engine_name")),
                ("Engine version", engine.get("engine_version")),
                ("Engine binary SHA-256", engine.get("binary_sha256")),
            )
        )

    lines = [
        f'<section aria-labelledby="{element_id}">',
        f'<h3 id="{element_id}">{_e(label)}</h3>',
        _dl(tuple(rows)),
    ]
    failure = value.get("failure")
    if type(failure) is dict:
        lines.extend(
            (
                '<p data-state="failure"><strong>Analysis failure:</strong></p>',
                _dl(
                    (
                        ("Failure code", failure.get("code")),
                        ("Failure message", failure.get("message")),
                    )
                ),
            )
        )

    candidates = value.get("candidates")
    if type(candidates) is not list:
        raise CoachReviewReferenceError(f"{label} candidates must be an array")
    if candidates:
        candidate_rows: list[tuple[object, ...]] = []
        for candidate in candidates:
            if type(candidate) is not dict:
                raise CoachReviewReferenceError(
                    f"{label} candidate must be an object"
                )
            candidate_rows.append(
                (
                    candidate.get("rank"),
                    candidate.get("root_move_uci"),
                    _evaluation_summary(candidate.get("evaluation")),
                    " ".join(candidate.get("pv_uci", [])),
                )
            )
        lines.append(
            _table(
                f"{label} candidates",
                ("Rank", "Root move", "Evaluation", "PV (UCI)"),
                tuple(candidate_rows),
            )
        )
    else:
        lines.append(
            '<p data-state="unavailable">No engine candidate lines are present.</p>'
        )
    lines.append("</section>")
    return "\n".join(lines)


def _render_objective(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("objective evidence must be an object")
    subject = value.get("subject")
    semantics = value.get("score_semantics")
    comparison = value.get("comparison")
    if type(subject) is not dict or type(semantics) is not dict:
        raise CoachReviewReferenceError("M15 subject or score semantics are malformed")
    if type(comparison) is not dict:
        raise CoachReviewReferenceError("M15 comparison is malformed")

    exact_delta = comparison.get("exact_centipawn_delta_for_mover")
    delta_display: object = exact_delta
    if exact_delta is None:
        delta_display = "Unavailable (non-exact or absent evidence)"

    score_rows = tuple((key.replace("_", " "), val) for key, val in semantics.items())
    body = [
        "<h3>Position subject</h3>",
        _dl(
            (
                ("Game id", subject.get("game_id")),
                ("Position id", subject.get("position_id")),
                ("Decision mover", subject.get("side_to_move")),
                ("Played move (UCI)", subject.get("played_move_uci")),
            )
        ),
        _table("Score semantics", ("Field", "Value"), score_rows),
        "<h3>Decision comparison</h3>",
        _dl(
            (
                ("Comparison id", comparison.get("comparison_id")),
                ("Evidence quality", comparison.get("evidence_quality")),
                ("Comparison kind", comparison.get("comparison_kind")),
                ("Preference", comparison.get("preference")),
                ("Compatibility", comparison.get("compatibility")),
                (
                    "Played evaluation source",
                    comparison.get("played_evaluation_source"),
                ),
                ("Played root-line rank", comparison.get("played_root_line_rank")),
                ("Best move (UCI)", comparison.get("best_move_uci")),
                ("Played move (UCI)", comparison.get("played_move_uci")),
                ("Exact mover delta", delta_display),
                ("Mate relation", comparison.get("mate_relation")),
                ("Terminal outcome", comparison.get("terminal_outcome")),
                ("Detail", comparison.get("detail")),
            )
        ),
        _render_evaluation("Best evaluation", comparison.get("best_evaluation")),
        _render_evaluation("Played evaluation", comparison.get("played_evaluation")),
        _render_analysis("Root analysis", value.get("root_analysis")),
        _render_analysis("Played child analysis", value.get("played_child_analysis")),
    ]
    return "\n".join(body)


def _render_diagnostic(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("diagnostic selection must be an object")
    candidate = value.get("candidate")
    batch_ref = value.get("batch_ref")
    if type(candidate) is not dict or type(batch_ref) is not dict:
        raise CoachReviewReferenceError("M18 diagnostic selection is malformed")
    lines = [
        _dl(
            (
                ("Claim scope", value.get("claim_scope")),
                ("Candidate id", candidate.get("candidate_id")),
                ("Game id", candidate.get("game_id")),
                ("Position id", candidate.get("position_id")),
                ("Comparison id", candidate.get("comparison_id")),
                ("Batch id", batch_ref.get("batch_id")),
                ("Batch fingerprint", batch_ref.get("fingerprint")),
            )
        )
    ]
    signals = candidate.get("signals")
    if type(signals) is not list:
        raise CoachReviewReferenceError("M18 candidate signals must be an array")
    if signals:
        rows = tuple(
            (
                signal.get("kind"),
                signal.get("raw_value"),
                signal.get("detail"),
                signal.get("evidence"),
            )
            for signal in signals
            if type(signal) is dict
        )
        if len(rows) != len(signals):
            raise CoachReviewReferenceError("M18 candidate signal is malformed")
        lines.append(
            _table(
                "Diagnostic selection signals",
                ("Kind", "Raw value", "Detail", "Evidence"),
                rows,
            )
        )
    return "\n".join(lines)


def _render_participant(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("participant authority must be an object")
    authorization = value.get("authorization")
    launch = value.get("launch")
    if type(authorization) is not dict:
        raise CoachReviewReferenceError("M21 authorization is malformed")
    lines = [
        _dl(
            (
                ("Claim scope", value.get("claim_scope")),
                ("Participant id", authorization.get("participant_id")),
                ("Actor kind", authorization.get("actor_kind")),
                ("Selection decision", authorization.get("selection_decision")),
                ("Capture consent", authorization.get("capture_consent")),
                ("Recorded at", authorization.get("recorded_at")),
                ("Authorization id", authorization.get("authorization_id")),
            )
        )
    ]
    if launch is None:
        lines.append('<p data-state="not-present">Launch is not present.</p>')
    elif type(launch) is dict:
        lines.extend(
            (
                "<h3>Authorized tutor launch</h3>",
                _dl(
                    (
                        ("Launch id", launch.get("launch_id")),
                        ("Created at", launch.get("created_at")),
                        ("Claim scope", launch.get("claim_scope")),
                        ("Authority boundary", launch.get("authority_boundary")),
                    )
                ),
            )
        )
    else:
        raise CoachReviewReferenceError("M21 launch is malformed")
    return "\n".join(lines)


def _render_tutor_state(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("tutor state must be an object")
    return _dl(
        (
            ("Tutor session id", value.get("tutor_session_id")),
            ("Snapshot fingerprint", value.get("snapshot_fingerprint")),
            ("State", value.get("state")),
            ("Claim scope", value.get("claim_scope")),
        )
    )


def _render_grounding(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("deterministic grounding must be an object")
    sections = value.get("sections")
    if type(sections) is not list:
        raise CoachReviewReferenceError("M16 sections must be an array")
    lines = [
        _dl(
            (
                ("Feedback id", value.get("feedback_id")),
                ("Tutor session id", value.get("tutor_session_id")),
                ("Created at", value.get("created_at")),
                ("Claim scope", value.get("claim_scope")),
            )
        )
    ]
    for index, section in enumerate(sections, start=1):
        if type(section) is not dict:
            raise CoachReviewReferenceError("M16 feedback section is malformed")
        section_id = f"grounding-section-{index}"
        lines.extend(
            (
                f'<article aria-labelledby="{section_id}">',
                f'<h3 id="{section_id}">{_e(section.get("kind"))}</h3>',
                (
                    '<p><strong>Claim scope:</strong> '
                    f'{_e(section.get("claim_scope"))}</p>'
                ),
                f'<p class="source-content">{_e(section.get("content"))}</p>',
                "</article>",
            )
        )
    return "\n".join(lines)


def _render_model_coaching(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("model coaching must be an object")
    provenance = value.get("model_provenance")
    if type(provenance) is not dict:
        raise CoachReviewReferenceError("M19 model provenance is malformed")
    return "\n".join(
        (
            _dl(
                (
                    ("Coaching id", value.get("coaching_id")),
                    ("Grounding status", value.get("grounding_status")),
                    ("Claim scope", value.get("claim_scope")),
                    ("Provider id", provenance.get("provider_id")),
                    ("Model id", provenance.get("model_id")),
                    ("Model version", provenance.get("model_version")),
                    ("Run id", provenance.get("run_id")),
                    ("Created at", value.get("created_at")),
                )
            ),
            (
                '<p data-authority="model-language"><strong>Model language:</strong> '
                f'{_e(value.get("rendered_content"))}</p>'
            ),
            (
                '<p data-truth-status="not-semantically-verified">'
                "This model language is request-bound and is not established as "
                "objective chess truth by M19.</p>"
            ),
        )
    )


def _render_model_evaluation(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("model evaluation must be an object")
    provenance = value.get("evaluator_provenance")
    judgments = value.get("judgments")
    if type(provenance) is not dict or type(judgments) is not list:
        raise CoachReviewReferenceError("M20 evaluator record is malformed")
    rows: list[tuple[object, ...]] = []
    for judgment in judgments:
        if type(judgment) is not dict:
            raise CoachReviewReferenceError("M20 judgment is malformed")
        rows.append(
            (
                judgment.get("dimension"),
                judgment.get("verdict"),
                judgment.get("rationale"),
            )
        )
    return "\n".join(
        (
            _dl(
                (
                    ("Evaluation id", value.get("evaluation_id")),
                    ("Qualification status", value.get("qualification_status")),
                    ("Truth status", value.get("truth_status")),
                    ("Source integrity", value.get("source_integrity")),
                    ("Claim scope", value.get("claim_scope")),
                    ("Evaluator kind", provenance.get("kind")),
                    ("Evaluator id", provenance.get("evaluator_id")),
                    ("Evaluator version", provenance.get("evaluator_version")),
                    ("Evaluator run id", provenance.get("run_id")),
                    ("Created at", value.get("created_at")),
                )
            ),
            _table(
                "Model evaluation judgments",
                ("Dimension", "Verdict", "Rationale"),
                tuple(rows),
            ),
            (
                '<p data-truth-status="not-established">'
                "M20 records a bounded assessment of model output. It does not "
                "establish objective chess truth.</p>"
            ),
        )
    )


def _section_body(section_id: str, value: Any) -> str:
    if value is None:
        return '<p data-state="not-present">Not present in this M25 read model.</p>'
    if section_id == "objective_evidence":
        return _render_objective(value)
    if section_id == "diagnostic_selection":
        return _render_diagnostic(value)
    if section_id == "participant_authority":
        return _render_participant(value)
    if section_id == "tutor_state":
        return _render_tutor_state(value)
    if section_id == "deterministic_grounding":
        return _render_grounding(value)
    if section_id == "model_coaching":
        return _render_model_coaching(value)
    if section_id == "model_evaluation":
        return _render_model_evaluation(value)
    raise CoachReviewReferenceError(f"unsupported M25 section: {section_id}")


def _render_section(section_id: str, value: Any) -> str:
    html_id = section_id.replace("_", "-")
    heading_id = f"{html_id}-heading"
    source = _SECTION_SOURCES[section_id]
    lines = [
        (
            f'<section id="{html_id}" data-m25-section="{_e(section_id)}" '
            f'aria-labelledby="{heading_id}">'
        ),
        f'<h2 id="{heading_id}">{_e(_SECTION_TITLES[section_id])}</h2>',
        f'<p><strong>Authority source:</strong> {_e(source)}</p>',
        _section_body(section_id, value),
    ]
    details = _source_details(f"Exact {source} source record", value)
    if details:
        lines.append(details)
    lines.append("</section>")
    return "\n".join(lines)


def _render_fingerprints(value: Any) -> str:
    if type(value) is not dict:
        raise CoachReviewReferenceError("M25 source fingerprints must be an object")
    rows = tuple((key, fingerprint) for key, fingerprint in value.items())
    return _table("Source fingerprints", ("Source", "Fingerprint"), rows)


def render_coach_review_reference_surface(
    read_model: dict[str, Any],
) -> CoachReviewReferenceSurface:
    """Render an already-qualified M25 read model without creating new authority."""
    read_model = _validate_read_model(read_model)
    sections = tuple(
        _render_section(section_id, read_model[section_id])
        for section_id in SECTION_ORDER
    )
    html_text = "\n".join(
        (
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Chess Mentor Coach Review Reference</title>",
            "</head>",
            "<body>",
            '<a href="#coach-review-main">Skip to review</a>',
            "<header>",
            "<h1>Coach Review Reference</h1>",
            (
                f'<p data-surface-schema="{_e(M28_SCHEMA_VERSION)}">'
                "Repository-only semantic reference rendering of an M25 coach-review "
                "read model.</p>"
            ),
            "</header>",
            '<aside aria-labelledby="claim-boundary-heading">',
            '<h2 id="claim-boundary-heading">Claim boundary</h2>',
            (
                "<p>This surface preserves qualified source layers for inspection. "
                "It is not a production user interface, does not choose a provider, "
                "does not execute external calls, and does not establish tutoring "
                "efficacy or model truth.</p>"
            ),
            "</aside>",
            (
                f'<main id="coach-review-main" '
                f'data-read-model-id="{_e(read_model["read_model_id"])}" '
                f'data-read-model-fingerprint="{_e(read_model["fingerprint"])}">'
            ),
            *sections,
            "</main>",
            '<footer aria-labelledby="source-fingerprints-heading">',
            '<h2 id="source-fingerprints-heading">Source identity</h2>',
            _render_fingerprints(read_model["source_fingerprints"]),
            "</footer>",
            "</body>",
            "</html>",
            "",
        )
    )
    payload = {
        "schema_version": M28_SCHEMA_VERSION,
        "m25_read_model_id": read_model["read_model_id"],
        "m25_read_model_fingerprint": read_model["fingerprint"],
        "html_sha256": _sha256_text(html_text),
        "claim_scope": M28_CLAIM_SCOPE,
    }
    fingerprint = _fingerprint(payload)
    return CoachReviewReferenceSurface(
        surface_id=f"coach_review_reference_{fingerprint[:20]}",
        fingerprint=fingerprint,
        html=html_text,
        read_model=read_model,
    )


def build_coach_review_reference_surface_from_bundle(
    bundle: Any,
) -> CoachReviewReferenceSurface:
    """Validate one strict M25 source bundle, then render its M28 reference surface."""
    read_model = build_coach_review_read_model_from_bundle(bundle)
    return render_coach_review_reference_surface(read_model)
