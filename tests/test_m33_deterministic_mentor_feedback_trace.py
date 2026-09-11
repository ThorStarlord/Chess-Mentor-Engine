"""M33 deterministic M16 provenance-trace qualification and rejection tests."""

from __future__ import annotations

import copy
import hashlib

import pytest
from test_m26_persistent_reviewed_coaching import S13, _store_lineage
from test_m27_reviewed_coaching_execution_ledger import (
    _deterministic_run,
    _model_run,
)
from test_m8_qualification import S12, _ledger_context

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.mentor_feedback_trace import (
    M33_CLAIM_SCOPE,
    M33_COMPONENT_SCOPE,
    M33_SCHEMA_VERSION,
    MentorFeedbackTraceError,
    build_persisted_mentor_feedback_trace_surface,
    validate_mentor_feedback_trace_surface,
    validate_persisted_mentor_feedback_trace_surface,
)
from chess_mentor_engine.participant_review_package import (
    build_participant_review_package,
)
from chess_mentor_engine.reviewed_coaching import run_persistent_reviewed_coaching
from chess_mentor_engine.storage import load_tutor_session, save_tutor_session
from chess_mentor_engine.storage.tutor import PROMPT_KIND
from chess_mentor_engine.tutoring import attach_tutor_hypothesis_context


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _rehash_trace(trace: dict) -> dict:
    payload = {
        key: value
        for key, value in trace.items()
        if key not in {"trace_id", "fingerprint"}
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "trace_id": f"mentor_feedback_trace_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _package(store, run):
    return build_participant_review_package(
        store=store,
        participant_id="P01",
        run_artifact_id=run.run_ref.artifact_id,
    )


def _trace(store, run):
    package = _package(store, run)
    trace = build_persisted_mentor_feedback_trace_surface(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )
    return package, trace


def _m7_run(tmp_path):
    store, _, _, compared_ref = _store_lineage(tmp_path)
    recovered = load_tutor_session(store, compared_ref, participant_id="P01")
    ledger_snapshot, revision = _ledger_context()
    session, context = attach_tutor_hypothesis_context(
        recovered.session,
        ledger_snapshot=ledger_snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )
    stored = store.get(compared_ref, participant_id="P01")
    external_dependencies = tuple(
        ref for ref in stored.dependencies if ref.kind != PROMPT_KIND
    )
    context_ref = save_tutor_session(
        store,
        session,
        prompts=recovered.prompts,
        dependencies=external_dependencies,
    )
    run = run_persistent_reviewed_coaching(
        store=store,
        participant_id="P01",
        session_artifact_id=context_ref.artifact_id,
        grounding_created_at=S13,
    )
    return store, run, context, revision


def _components(trace: dict):
    for section in trace["sections"]:
        yield from section["components"]


def test_trace_is_deterministic_compact_and_source_bound(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    package = _package(store, run)

    first = build_persisted_mentor_feedback_trace_surface(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )
    second = build_persisted_mentor_feedback_trace_surface(
        store=store,
        participant_id="P01",
        package_artifact_id=package.manifest_ref.artifact_id,
    )

    assert first == second
    assert first["schema_version"] == M33_SCHEMA_VERSION
    assert first["claim_scope"] == M33_CLAIM_SCOPE
    assert first["component_scope"] == M33_COMPONENT_SCOPE
    assert first["section_order"] == ["objective", "reasoning", "reflection"]
    assert first["sources"]["m7"] is None
    assert first["sources"]["m19"]["present"] is False
    assert first["sources"]["m20"]["present"] is False
    assert all(
        item["source_authority"] in {"M15", "M6"}
        for item in _components(first)
    )
    assert run.read_model["deterministic_grounding"]["rendered_content"] not in (
        canonical_json(first)
    )
    assert validate_mentor_feedback_trace_surface(first) == first
    assert validate_persisted_mentor_feedback_trace_surface(
        store=store,
        participant_id="P01",
        trace=first,
    ) == first


def test_every_nonempty_m16_section_line_has_one_trace_component(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    feedback = run.read_model["deterministic_grounding"]

    assert feedback is not None
    feedback_sections = {item["kind"]: item for item in feedback["sections"]}
    total = 0
    for traced in trace["sections"]:
        source = feedback_sections[traced["kind"]]
        lines = source["content"].splitlines()
        assert traced["component_count"] == len(lines)
        assert traced["content_sha256"] == _sha256_text(source["content"])
        assert traced["evidence_refs_sha256"] == _fingerprint(
            source["evidence_refs"]
        )
        assert [item["content_sha256"] for item in traced["components"]] == [
            _sha256_text(line) for line in lines
        ]
        total += len(lines)

    assert trace["coverage"]["component_count"] == total
    assert trace["coverage"]["all_components_traced"] is True


def test_m7_learner_components_point_to_exact_context_and_revision(tmp_path) -> None:
    store, run, context, revision = _m7_run(tmp_path)
    _, trace = _trace(store, run)

    assert trace["section_order"] == [
        "objective",
        "reasoning",
        "learner_context",
        "reflection",
    ]
    m7 = trace["sources"]["m7"]
    assert m7["context"]["ref_id"] == context.context_id
    assert m7["context"]["fingerprint"] == context.fingerprint
    assert m7["revisions"] == [
        {
            "kind": "hypothesis_revision",
            "ref_id": revision.revision_id,
            "fingerprint": revision.fingerprint,
        }
    ]
    learner = next(
        item for item in trace["sections"] if item["kind"] == "learner_context"
    )
    assert learner["components"][0]["source_pointer"] == "/sources/m7/context"
    assert any(
        item["source_pointer"] == "/sources/m7/revisions/0"
        for item in learner["components"]
    )
    assert all(
        item["source_authority"] == "M7" for item in learner["components"]
    )


def test_model_and_evaluator_content_remain_separate_from_trace(tmp_path) -> None:
    store, _, run = _model_run(tmp_path)
    _, trace = _trace(store, run)
    model = run.read_model["model_coaching"]
    evaluation = run.read_model["model_evaluation"]

    assert model is not None and evaluation is not None
    assert trace["sources"]["m19"] == {
        "present": True,
        "fingerprint": model["fingerprint"],
    }
    assert trace["sources"]["m20"] == {
        "present": True,
        "fingerprint": evaluation["fingerprint"],
    }
    serialized = canonical_json(trace)
    assert model["rendered_content"] not in serialized
    for judgment in evaluation["judgments"]:
        assert judgment["rationale"] not in serialized
    assert all(
        item["source_authority"] not in {"M19", "M20"}
        for item in _components(trace)
    )
    assert trace["authority_boundary"]["copies_m19_model_prose"] is False
    assert (
        trace["authority_boundary"]["copies_m20_evaluator_judgments"] is False
    )


def test_rehashed_authority_promotion_is_rejected_detached(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    tampered["sections"][0]["components"][0]["source_authority"] = "M19"
    tampered = _rehash_trace(tampered)

    with pytest.raises(MentorFeedbackTraceError, match="source authority"):
        validate_mentor_feedback_trace_surface(tampered)


def test_rehashed_component_omission_is_rejected_against_persisted_source(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    reasoning = tampered["sections"][1]
    reasoning["components"].pop()
    reasoning["component_count"] -= 1
    tampered["coverage"]["component_count"] -= 1
    tampered = _rehash_trace(tampered)

    assert validate_mentor_feedback_trace_surface(tampered) == tampered
    with pytest.raises(MentorFeedbackTraceError, match="drifted from persisted"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="P01",
            trace=tampered,
        )


def test_rehashed_content_hash_drift_is_rejected_against_persisted_source(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    tampered["sections"][0]["components"][0]["content_sha256"] = "0" * 64
    tampered = _rehash_trace(tampered)

    assert validate_mentor_feedback_trace_surface(tampered) == tampered
    with pytest.raises(MentorFeedbackTraceError, match="drifted from persisted"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="P01",
            trace=tampered,
        )


def test_rehashed_same_authority_pointer_drift_requires_persisted_rebuild(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    reasoning = tampered["sections"][1]
    assertion_component = next(
        item
        for item in reasoning["components"]
        if "/assertions/" in item["source_pointer"]
    )
    assertion_component["source_pointer"] = "/sources/m6/assessment"
    tampered = _rehash_trace(tampered)

    assert validate_mentor_feedback_trace_surface(tampered) == tampered
    with pytest.raises(MentorFeedbackTraceError, match="drifted from persisted"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="P01",
            trace=tampered,
        )


def test_rehashed_m6_source_fingerprint_drift_requires_persisted_rebuild(
    tmp_path,
) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    tampered["sources"]["m6"]["assessment"]["fingerprint"] = "0" * 64
    tampered = _rehash_trace(tampered)

    assert validate_mentor_feedback_trace_surface(tampered) == tampered
    with pytest.raises(MentorFeedbackTraceError, match="drifted from persisted"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="P01",
            trace=tampered,
        )


def test_invalid_source_participant_is_rejected_even_when_rehashed(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    tampered["source_refs"]["m16_feedback"]["participant_id"] = "OTHER"
    tampered = _rehash_trace(tampered)

    with pytest.raises(MentorFeedbackTraceError, match="participant scope"):
        validate_mentor_feedback_trace_surface(tampered)


def test_rehashed_package_source_swap_fails_closed(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)
    tampered = copy.deepcopy(trace)
    tampered["source_refs"]["m30_package"]["artifact_id"] = (
        "participant_review_package_forged"
    )
    tampered = _rehash_trace(tampered)

    assert validate_mentor_feedback_trace_surface(tampered) == tampered
    with pytest.raises(MentorFeedbackTraceError, match="M32 delivery validation"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="P01",
            trace=tampered,
        )


def test_wrong_requested_participant_is_rejected_before_rebuild(tmp_path) -> None:
    store, _, run = _deterministic_run(tmp_path)
    _, trace = _trace(store, run)

    with pytest.raises(MentorFeedbackTraceError, match="requested participant"):
        validate_persisted_mentor_feedback_trace_surface(
            store=store,
            participant_id="OTHER",
            trace=trace,
        )
