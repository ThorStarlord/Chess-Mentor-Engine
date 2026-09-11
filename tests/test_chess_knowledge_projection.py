from __future__ import annotations

import copy
from dataclasses import replace

import pytest
from test_m8_qualification import S13, _through_compare

from chess_mentor_engine.chess_knowledge import build_assertion_bundle
from chess_mentor_engine.chess_knowledge.detectors import detect_position_knowledge
from chess_mentor_engine.chess_knowledge.projection import (
    KNOWLEDGE_MODEL_INSTRUCTIONS,
    bind_knowledge_context_to_model_request,
    build_knowledge_augmented_provider_payload,
    build_knowledge_coaching_context,
    validate_knowledge_coaching_context,
    validate_knowledge_model_binding,
)
from chess_mentor_engine.coaching import build_model_coaching_request

_CREATED_AT = "2026-09-11T08:20:00-03:00"
_BIND_AT = "2026-09-11T08:21:00-03:00"


def _sources():
    upstream, session, _ = _through_compare()
    assertions = detect_position_knowledge(
        upstream.position,
        created_at=_CREATED_AT,
    )
    subject = assertions[0].subject
    bundle = build_assertion_bundle(
        subject=subject,
        assertions=assertions,
        claim_scope="qualified position knowledge for coaching sidecar",
        created_at=_CREATED_AT,
    )
    context = build_knowledge_coaching_context(
        bundle,
        created_at=_CREATED_AT,
    )
    request = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )
    return upstream, request, bundle, context


def test_projection_preserves_concept_metadata_and_authority() -> None:
    _, _, bundle, context = _sources()

    assert context.assertion_bundle_id == bundle.bundle_id
    assert context.model_instructions == KNOWLEDGE_MODEL_INSTRUCTIONS
    projected = {
        item.assertion_ref.assertion_id: item for item in context.assertions
    }
    for assertion in bundle.assertions:
        item = projected[assertion.assertion_id]
        assert item.assertion_ref.fingerprint == assertion.fingerprint
        assert item.assertion_ref.concept_id == assertion.concept_id
        assert item.status == assertion.status
        assert item.authority_class == assertion.authority_class


def test_projection_is_deterministic_for_same_explicit_inputs() -> None:
    _, _, bundle, first = _sources()
    second = build_knowledge_coaching_context(
        bundle,
        created_at=_CREATED_AT,
    )

    assert first == second
    assert first.context_id.startswith("ckc_")


def test_projection_rejects_rewritten_concept_metadata() -> None:
    _, _, bundle, context = _sources()
    altered_assertion = replace(
        context.assertions[0],
        preferred_name="Invented coaching label",
    )
    altered = replace(
        context,
        assertions=(altered_assertion, *context.assertions[1:]),
    )

    with pytest.raises(ValueError, match="assertion projection mismatch"):
        validate_knowledge_coaching_context(altered, bundle=bundle)


def test_m19_binding_does_not_mutate_or_refingerprint_request() -> None:
    _, request, bundle, context = _sources()
    before = copy.deepcopy(request)

    binding = bind_knowledge_context_to_model_request(
        model_request=request,
        context=context,
        bundle=bundle,
        created_at=_BIND_AT,
    )
    payload = build_knowledge_augmented_provider_payload(
        model_request=request,
        context=context,
        binding=binding,
        bundle=bundle,
    )

    assert request == before
    assert request["request_id"] == binding.model_request_id
    assert request["fingerprint"] == binding.model_request_fingerprint
    assert payload["m19_request"] is request
    assert payload["chess_knowledge_context"]["context_id"] == context.context_id
    assert payload["knowledge_binding"]["binding_id"] == binding.binding_id


def test_binding_rejects_request_or_context_drift() -> None:
    _, request, bundle, context = _sources()
    binding = bind_knowledge_context_to_model_request(
        model_request=request,
        context=context,
        bundle=bundle,
        created_at=_BIND_AT,
    )

    with pytest.raises(ValueError, match="request fingerprint mismatch"):
        validate_knowledge_model_binding(
            replace(binding, model_request_fingerprint="0" * 64),
            model_request=request,
            context=context,
            bundle=bundle,
        )

    with pytest.raises(ValueError, match="context fingerprint mismatch"):
        validate_knowledge_model_binding(
            replace(binding, knowledge_context_fingerprint="0" * 64),
            model_request=request,
            context=context,
            bundle=bundle,
        )


def test_projection_instructions_forbid_learner_and_authority_promotion() -> None:
    _, _, _, context = _sources()
    instructions = " ".join(context.model_instructions).lower()

    assert "do not promote" in instructions
    assert "learner weakness" in instructions
    assert "do not invent" in instructions
    assert "m16" in instructions
