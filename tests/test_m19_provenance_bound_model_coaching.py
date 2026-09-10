"""M19 provenance-bound model coaching qualification and rejection coverage."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest
from test_m8_qualification import S12, S13, S14, _ledger_context, _through_compare

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    MODEL_COACHING_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_REQUEST_SCHEMA_VERSION,
    ModelCoachingError,
    ModelCoachingGeneration,
    bind_model_coaching_response,
    build_model_coaching_request,
    record_model_coaching_response,
    run_model_coaching,
)
from chess_mentor_engine.feedback import FEEDBACK_SCHEMA_VERSION
from chess_mentor_engine.tutoring import attach_tutor_hypothesis_context


class _Provider:
    def __init__(
        self,
        *,
        rendered_content: str = "Review the opponent's strongest reply first.",
        request_id: str | None = None,
        request_fingerprint: str | None = None,
        generated_at: str = S14,
        mutate_request: bool = False,
        failure: Exception | None = None,
    ) -> None:
        self.rendered_content = rendered_content
        self.request_id = request_id
        self.request_fingerprint = request_fingerprint
        self.generated_at = generated_at
        self.mutate_request = mutate_request
        self.failure = failure
        self.requests: list[dict] = []

    def generate(self, request):
        self.requests.append(request)
        if self.failure is not None:
            raise self.failure
        request_id = request["request_id"]
        request_fingerprint = request["fingerprint"]
        if self.mutate_request:
            request["grounded_feedback"]["rendered_content"] = "provider mutation"
        return ModelCoachingGeneration(
            request_id=self.request_id or request_id,
            request_fingerprint=self.request_fingerprint or request_fingerprint,
            rendered_content=self.rendered_content,
            provider_id="fixture-provider",
            model_id="fixture-mentor",
            model_version="2026.09",
            run_id="fixture-run-001",
            generated_at=self.generated_at,
        )


def _request():
    upstream, session, _ = _through_compare()
    request = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )
    return upstream, session, request


def _generation(request, **overrides) -> ModelCoachingGeneration:
    values = {
        "request_id": request["request_id"],
        "request_fingerprint": request["fingerprint"],
        "rendered_content": "Compare your move with the strongest reply.",
        "provider_id": "fixture-provider",
        "model_id": "fixture-mentor",
        "model_version": "2026.09",
        "run_id": "fixture-run-001",
        "generated_at": S14,
    }
    values.update(overrides)
    return ModelCoachingGeneration(**values)


def _rehash_request(request: dict) -> dict:
    tampered = dict(request)
    payload = {
        key: value
        for key, value in tampered.items()
        if key not in {"request_id", "fingerprint"}
    }
    fingerprint = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    tampered["fingerprint"] = fingerprint
    tampered["request_id"] = f"model_coaching_request_{fingerprint[:20]}"
    return tampered


def test_request_is_deterministic_and_contains_exact_m16_grounding() -> None:
    upstream, session, first = _request()
    second = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )

    assert first == second
    assert first["schema_version"] == MODEL_COACHING_REQUEST_SCHEMA_VERSION
    assert first["claim_scope"] == "model_language_rendering_request"
    assert first["grounded_feedback"]["schema_version"] == FEEDBACK_SCHEMA_VERSION
    assert first["grounded_feedback"]["tutor_session_id"] == session.tutor_session_id
    assert first["grounded_feedback"]["tutor_comparison_id"] == (
        session.comparison.comparison_id
    )
    assert first["instruction"]["model_role"] == "language_renderer_only"
    assert first["instruction"]["output_contract"] == "plain_prose_only"
    assert "new_m6_reasoning_judgments" in first["instruction"][
        "forbidden_authority_changes"
    ]


def test_request_carries_complete_attached_m7_context_via_m16() -> None:
    upstream, session, _ = _through_compare()
    snapshot, revision = _ledger_context()
    session, context = attach_tutor_hypothesis_context(
        session,
        ledger_snapshot=snapshot,
        active_revisions=(revision,),
        attached_at=S12,
    )

    request = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )

    assert request["hypothesis_context_id"] == context.context_id
    learner = next(
        item
        for item in request["grounded_feedback"]["sections"]
        if item["kind"] == "learner_context"
    )
    assert revision.statement in learner["content"]
    assert "not a causal diagnosis" in learner["content"]


def test_run_records_model_actor_without_rewriting_grounded_authority() -> None:
    upstream, session, _ = _through_compare()
    provider = _Provider()

    updated, explanation, request, coaching = run_model_coaching(
        provider=provider,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        request_created_at=S13,
    )

    assert updated.state == "explained"
    assert updated.explanation == explanation
    assert explanation.provenance.actor_kind == "model"
    assert explanation.provenance.actor_id == "fixture-provider:fixture-mentor"
    assert explanation.provenance.actor_version == "2026.09"
    assert explanation.provenance.run_id == "fixture-run-001"
    assert explanation.provenance.instruction_fingerprint == (
        request["instruction"]["fingerprint"]
    )
    assert coaching["schema_version"] == MODEL_COACHING_RECORD_SCHEMA_VERSION
    assert coaching["request_id"] == request["request_id"]
    assert coaching["grounded_feedback_ref"]["feedback_id"] == (
        request["grounded_feedback"]["feedback_id"]
    )
    assert coaching["grounding_status"] == (
        "request_bound_not_semantically_verified"
    )
    assert "sections" not in coaching
    assert "assessment" not in coaching
    assert "active_revisions" not in coaching


def test_generation_request_echo_drift_is_rejected_before_m8_transition() -> None:
    upstream, session, request = _request()
    generation = _generation(
        request,
        request_fingerprint="not-the-request-fingerprint",
    )

    with pytest.raises(ModelCoachingError, match="request fingerprint mismatch"):
        record_model_coaching_response(
            request=request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=generation,
        )

    assert session.state == "compared"
    assert session.explanation is None


def test_tampered_grounding_request_is_rejected_even_if_identity_is_rehashed() -> None:
    upstream, session, request = _request()
    instruction = dict(request["instruction"])
    instruction["model_role"] = "new_factual_authority"
    tampered = dict(request)
    tampered["instruction"] = instruction
    tampered = _rehash_request(tampered)

    with pytest.raises(ModelCoachingError, match="instruction contract mismatch"):
        bind_model_coaching_response(
            request=tampered,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_generation(tampered),
        )


def test_request_bound_to_different_objective_evidence_is_rejected() -> None:
    upstream, session, request = _request()
    drifted = replace(upstream.comparison, detail="unsupported post-request rewrite")

    with pytest.raises(ModelCoachingError, match="M16 grounded feedback rejected"):
        bind_model_coaching_response(
            request=request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=drifted,
            generation=_generation(request),
        )


def test_blank_or_predated_model_generation_is_rejected() -> None:
    upstream, session, request = _request()

    with pytest.raises(ModelCoachingError, match="must not be blank"):
        bind_model_coaching_response(
            request=request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_generation(request, rendered_content="   "),
        )

    with pytest.raises(ModelCoachingError, match="cannot predate"):
        bind_model_coaching_response(
            request=request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_generation(request, generated_at=S12),
        )


def test_provider_failure_and_request_mutation_fail_without_session_transition(
) -> None:
    upstream, session, _ = _through_compare()

    with pytest.raises(ModelCoachingError, match="model provider failed"):
        run_model_coaching(
            provider=_Provider(failure=RuntimeError("fixture outage")),
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            request_created_at=S13,
        )

    with pytest.raises(ModelCoachingError, match="mutated the coaching request"):
        run_model_coaching(
            provider=_Provider(mutate_request=True),
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            request_created_at=S13,
        )

    assert session.state == "compared"
    assert session.explanation is None


def test_non_generation_provider_return_is_rejected_before_recording() -> None:
    upstream, session, request = _request()

    with pytest.raises(ModelCoachingError, match="invalid generation record"):
        bind_model_coaching_response(
            request=request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation={"rendered_content": "not typed"},  # type: ignore[arg-type]
        )
