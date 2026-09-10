"""M28 deterministic local coach-review reference-surface qualification."""

from __future__ import annotations

import copy
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest
import test_m22_end_to_end_evaluation_fidelity as m22
import test_m25_coach_review_read_model as m25
import test_m26_persistent_reviewed_coaching as m26

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coach_review_reference import (
    M28_CLAIM_SCOPE,
    M28_SCHEMA_VERSION,
    CoachReviewReferenceError,
    build_coach_review_reference_surface_from_bundle,
    render_coach_review_reference_surface,
)
from chess_mentor_engine.coach_review_reference_cli import main as reference_main
from chess_mentor_engine.review import CoachReviewReadModelError
from chess_mentor_engine.reviewed_coaching import run_persistent_reviewed_coaching

_GOLDEN = json.loads(
    (
        Path(__file__).parent
        / "fixtures"
        / "m28_reference_surface_semantic_golden.json"
    ).read_text(encoding="utf-8")
)


def _bundle(
    presentation: dict,
    *,
    diagnostic_candidate: dict | None = None,
    diagnostic_batch: dict | None = None,
    authorization: dict | None = None,
    launch: dict | None = None,
    tutor_state: dict | None = None,
    grounded_feedback: dict | None = None,
    model_coaching: dict | None = None,
    model_evaluation: dict | None = None,
) -> dict:
    return {
        "evaluation_presentation": presentation,
        "diagnostic_candidate": diagnostic_candidate,
        "diagnostic_batch": diagnostic_batch,
        "authorization": authorization,
        "launch": launch,
        "tutor_state": tutor_state,
        "grounded_feedback": grounded_feedback,
        "model_coaching": model_coaching,
        "model_evaluation": model_evaluation,
    }


class _SemanticParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.h2_headings: list[str] = []
        self.captions: list[str] = []
        self.html_lang: str | None = None
        self.main_id: str | None = None
        self._capture: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.tags.append(tag)
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "main":
            self.main_id = values.get("id")
        if values.get("id") is not None:
            self.ids.append(values["id"] or "")
        if tag in {"h2", "caption"}:
            self._capture = tag
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._capture:
            return
        text = "".join(self._buffer).strip()
        if tag == "h2":
            self.h2_headings.append(text)
        else:
            self.captions.append(text)
        self._capture = None
        self._buffer = []


def _parse(html: str) -> _SemanticParser:
    parser = _SemanticParser()
    parser.feed(html)
    parser.close()
    return parser


def test_semantic_golden_snapshot_keeps_landmarks_sections_and_tables() -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    surface = build_coach_review_reference_surface_from_bundle(_bundle(presentation))
    parsed = _parse(surface.html)

    assert parsed.html_lang == _GOLDEN["html_lang"]
    assert parsed.main_id == _GOLDEN["main_id"]
    assert parsed.h2_headings == _GOLDEN["h2_headings"]
    for landmark in _GOLDEN["required_landmarks"]:
        assert landmark in parsed.tags
    for forbidden in _GOLDEN["forbidden_elements"]:
        assert forbidden not in parsed.tags

    top_level = [
        section_id
        for section_id in _GOLDEN["top_level_section_ids"]
        if section_id in parsed.ids
    ]
    assert top_level == _GOLDEN["top_level_section_ids"]
    for caption in _GOLDEN["exact_case_table_captions"]:
        assert caption in parsed.captions


def test_reference_surface_is_deterministic_and_content_addressed() -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    bundle = _bundle(presentation)

    first = build_coach_review_reference_surface_from_bundle(bundle)
    second = build_coach_review_reference_surface_from_bundle(copy.deepcopy(bundle))

    assert first.html == second.html
    assert first.surface_id == second.surface_id
    assert first.fingerprint == second.fingerprint
    assert first.surface_id == f"coach_review_reference_{first.fingerprint[:20]}"
    assert first.read_model == second.read_model
    assert first.html.endswith("</html>\n")


@pytest.mark.parametrize(
    "scenario",
    sorted(m22._REQUIRED_SCENARIOS),
)
def test_m22_evidence_regimes_remain_visible_without_score_reinterpretation(
    scenario,
) -> None:
    *_, presentation = m22._scenario(scenario)
    surface = build_coach_review_reference_surface_from_bundle(_bundle(presentation))
    html = surface.html
    comparison = presentation["comparison"]

    assert f"<dd>{comparison['evidence_quality']}</dd>" in html
    assert f"<dd>{comparison['comparison_kind']}</dd>" in html
    assert f"<dd>{comparison['played_evaluation_source']}</dd>" in html

    if comparison["exact_centipawn_delta_for_mover"] is None:
        assert "Unavailable (non-exact or absent evidence)" in html
    else:
        assert f"<dd>{comparison['exact_centipawn_delta_for_mover']}</dd>" in html

    best = comparison["best_evaluation"]
    if best is not None and best["kind"] == "centipawn":
        assert f"{best['white']['centipawns']} centipawns" in html
        assert best["white"]["bound"] in html
        assert f"{best['decision_mover']['centipawns']} centipawns" in html
        assert best["decision_mover"]["side"] in html
        assert best["decision_mover"]["bound"] in html
    if best is not None and best["kind"] == "mate":
        assert f"<dd>{best['winner']}</dd>" in html
        assert f"<dd>{best['plies_to_mate']}</dd>" in html
        assert "Plies to mate" in html

    child = presentation["played_child_analysis"]
    if child is not None and child["status"] == "failure":
        assert '<p data-state="failure"><strong>Analysis failure:</strong></p>' in html
        assert child["failure"]["code"] in html
        assert child["failure"]["message"] in html

    exact_source = canonical_json(presentation)
    assert exact_source.replace("&", "&amp;").replace("\"", "&quot;")[:40] in html


def test_black_mover_keeps_canonical_white_and_mover_perspectives() -> None:
    *_, presentation = m22._scenario("bounded_black_perspective")
    surface = build_coach_review_reference_surface_from_bundle(_bundle(presentation))
    html = surface.html

    assert "Canonical engine" in html
    assert "Decision mover" in html
    assert "<td>white</td>" in html
    assert "<td>-50 centipawns</td>" in html
    assert "<td>lower</td>" in html
    assert "<td>black</td>" in html
    assert "<td>50 centipawns</td>" in html
    assert "<td>upper</td>" in html
    assert "ordering_bound_in_display_perspective" in html


def test_complete_m26_read_model_renders_all_authority_layers_with_fake_adapters(
    tmp_path,
) -> None:
    store, _, _, compared_ref = m26._store_lineage(tmp_path)
    result = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=compared_ref.artifact_id,
        grounding_created_at=m26.S13,
        provider=m26._Provider(),
        provider_endpoint=m26._provider_endpoint(),
        evaluator=m26._Evaluator(),
        evaluator_endpoint=m26._evaluator_endpoint(),
        evaluation_request_created_at=m26.S15,
    )

    surface = render_coach_review_reference_surface(result.read_model)
    html = surface.html

    assert 'data-m25-section="objective_evidence"' in html
    assert 'data-m25-section="diagnostic_selection"' in html
    assert 'data-m25-section="participant_authority"' in html
    assert 'data-m25-section="tutor_state"' in html
    assert 'data-m25-section="deterministic_grounding"' in html
    assert 'data-m25-section="model_coaching"' in html
    assert 'data-m25-section="model_evaluation"' in html
    assert result.read_model["model_coaching"]["rendered_content"] in html
    assert result.read_model["model_evaluation"]["truth_status"] in html
    assert "M20 records a bounded assessment of model output" in html
    assert "It does not establish objective chess truth" in html


def test_model_content_is_html_escaped_and_never_becomes_markup() -> None:
    rendered = '<script>alert("model")</script><button>move</button>'
    presentation, feedback, coaching, evaluation = m25._m20_sources(
        rendered_content=rendered,
    )
    surface = build_coach_review_reference_surface_from_bundle(
        _bundle(
            presentation,
            grounded_feedback=feedback,
            model_coaching=coaching,
            model_evaluation=evaluation,
        )
    )

    assert "<script>" not in surface.html
    assert "<button>move</button>" not in surface.html
    assert "&lt;script&gt;alert(&quot; in surface.html
    assert "&lt;button&gt;move&lt;/button&gt;" in surface.html
    parsed = _parse(surface.html)
    assert "script" not in parsed.tags
    assert "button" not in parsed.tags


def test_direct_renderer_rejects_mutated_m25_identity() -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    surface = build_coach_review_reference_surface_from_bundle(_bundle(presentation))
    tampered = copy.deepcopy(surface.read_model)
    tampered["objective_evidence"]["comparison"]["detail"] = "tampered"

    with pytest.raises(CoachReviewReferenceError, match="fingerprint mismatch"):
        render_coach_review_reference_surface(tampered)


def test_bundle_path_rejects_rehashed_m20_truth_promotion() -> None:
    presentation, feedback, coaching, evaluation = m25._m20_sources()
    promoted = copy.deepcopy(evaluation)
    promoted["truth_status"] = "established_objective_truth"
    promoted = m25._rehash(
        promoted,
        "evaluation_id",
        "model_coaching_evaluation",
    )

    with pytest.raises(CoachReviewReadModelError, match="truth status"):
        build_coach_review_reference_surface_from_bundle(
            _bundle(
                presentation,
                grounded_feedback=feedback,
                model_coaching=coaching,
                model_evaluation=promoted,
            )
        )


def test_missing_optional_sections_are_explicitly_not_present() -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    surface = build_coach_review_reference_surface_from_bundle(_bundle(presentation))

    assert surface.html.count(
        '<p data-state="not-present">Not present in this M25 read model.</p>'
    ) == 6
    assert "Objective evidence" in surface.html
    assert "M15 objective evidence" in surface.html


def test_cli_writes_new_static_html_and_refuses_overwrite(tmp_path, capsys) -> None:
    *_, presentation = m22._scenario("exact_white_root_multipv")
    bundle_path = tmp_path / "m25-bundle.json"
    bundle_path.write_text(json.dumps(_bundle(presentation)), encoding="utf-8")
    output = tmp_path / "reference" / "review.html"

    assert reference_main([str(bundle_path), "--output", str(output)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == M28_SCHEMA_VERSION
    assert payload["claim_scope"] == M28_CLAIM_SCOPE
    assert payload["external_calls"] is False
    assert payload["production_ui_claim"] is False
    assert Path(payload["output"]) == output.resolve()
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>\n")

    assert reference_main([str(bundle_path), "--output", str(output)]) == 2
    assert "refusing to overwrite" in capsys.readouterr().err


def test_cli_rejects_invalid_bundle_extension_and_missing_input(
    tmp_path,
    capsys,
) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}", encoding="utf-8")
    html_path = tmp_path / "invalid.html"

    assert reference_main([str(invalid), "--output", str(html_path)]) == 2
    assert "shape mismatch" in capsys.readouterr().err
    assert not html_path.exists()

    *_, presentation = m22._scenario("exact_white_root_multipv")
    valid = tmp_path / "valid.json"
    valid.write_text(json.dumps(_bundle(presentation)), encoding="utf-8")
    txt_path = tmp_path / "review.txt"
    assert reference_main([str(valid), "--output", str(txt_path)]) == 2
    assert "must end in .html or .htm" in capsys.readouterr().err
    assert not txt_path.exists()

    missing = tmp_path / "missing.json"
    assert reference_main([str(missing), "--output", str(html_path)]) == 2
    assert "bundle file does not exist" in capsys.readouterr().err
    assert not html_path.exists()
