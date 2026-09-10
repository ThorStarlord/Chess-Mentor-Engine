"""M20 model-coaching evaluation contract and hermetic corpus qualification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from test_m8_qualification import S13, S14, _through_compare

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.coaching import (
    EVALUATION_DIMENSIONS,
    MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION,
    MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION,
    ModelCoachingEvaluationError,
    ModelCoachingEvaluationGeneration,
    ModelCoachingEvaluationJudgment,
    ModelCoachingGeneration,
    bind_model_coaching_evaluation,
    bind_model_coaching_response,
    build_model_coaching_evaluation_request,
    build_model_coaching_request,
    run_model_coaching_evaluation,
)

S15 = "2026-09-08T10:15:00-03:00"
S16 = "2026-09-08T10:16:00-03:00"


class _Evaluator:
    def __init__(
        self,
        *,
        judgments: tuple[ModelCoachingEvaluationJudgment, ...] | None = None,
        request_id: str | None = None,
        request_fingerprint: str | None = None,
        generated_at: str = S16,
        mutate_request: bool = False,
        failure: Exception | None = None,
        invalid_result: bool = False,
    ) -> None:
        self.judgments = judgments or _judgments()
        self.request_id = request_id
        self.request_fingerprint = request_fingerprint
        self.generated_at = generated_at
        self.mutate_request = mutate_request
        self.failure = failure
        self.invalid_result = invalid_result

    def evaluate(self, request):
        if self.failure is not None:
            raise self.failure
        request_id = request["request_id"]
        request_fingerprint = request["fingerprint"]
        if self.mutate_request:
            request["rendered_content"] = "mutated by fixture evaluator"
        if self.invalid_result:
            return {"judgments": []}
        return ModelCoachingEvaluationGeneration(
            request_id=self.request_id or request_id,
            request_fingerprint=self.request_fingerprint or request_fingerprint,
            judgments=self.judgments,
            evaluator_kind="fixture",
            evaluator_id="m20-fixture-evaluator",
            evaluator_version="1",
            run_id="fixture-evaluation-run-001",
            generated_at=self.generated_at,
        )


def _judgments(
    *,
    failed: tuple[str, ...] = (),
    unclear: tuple[str, ...] = (),
) -> tuple[ModelCoachingEvaluationJudgment, ...]:
    values = []
    for dimension in EVALUATION_DIMENSIONS:
        verdict = "pass"
        if dimension in failed:
            verdict = "fail"
        elif dimension in unclear:
            verdict = "unclear"
        values.append(
            ModelCoachingEvaluationJudgment(
                dimension=dimension,
                verdict=verdict,
                rationale=f"Fixture judgment for {dimension}: {verdict}.",
            )
        )
    return tuple(values)


def _m19_sources(rendered_content: str = "Review the strongest reply first."):
    upstream, session, _ = _through_compare()
    model_request = build_model_coaching_request(
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S13,
    )
    generation = ModelCoachingGeneration(
        request_id=model_request["request_id"],
        request_fingerprint=model_request["fingerprint"],
        rendered_content=rendered_content,
        provider_id="fixture-provider",
        model_id="fixture-mentor",
        model_version="2026.09",
        run_id="fixture-model-run-001",
        generated_at=S14,
    )
    coaching = bind_model_coaching_response(
        request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=generation,
    )
    return upstream, session, model_request, coaching


def _m20_request(rendered_content: str = "Review the strongest reply first."):
    upstream, session, model_request, coaching = _m19_sources(rendered_content)
    request = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S15,
    )
    return upstream, session, model_request, coaching, request


def _evaluation_generation(request, **overrides):
    values = {
        "request_id": request["request_id"],
        "request_fingerprint": request["fingerprint"],
        "judgments": _judgments(),
        "evaluator_kind": "fixture",
        "evaluator_id": "m20-fixture-evaluator",
        "evaluator_version": "1",
        "run_id": "fixture-evaluation-run-001",
        "generated_at": S16,
    }
    values.update(overrides)
    return ModelCoachingEvaluationGeneration(**values)


def _rehash_m20_request(request: dict) -> dict:
    tampered = dict(request)
    payload = {
        key: value
        for key, value in tampered.items()
        if key not in {"request_id", "fingerprint"}
    }
    fingerprint = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    tampered["fingerprint"] = fingerprint
    tampered["request_id"] = f"model_coaching_evaluation_request_{fingerprint[:20]}"
    return tampered


def _rehash_m19_coaching(coaching: dict) -> dict:
    tampered = dict(coaching)
    payload = {
        key: value
        for key, value in tampered.items()
        if key not in {"coaching_id", "fingerprint"}
    }
    fingerprint = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    tampered["fingerprint"] = fingerprint
    tampered["coaching_id"] = f"model_coaching_{fingerprint[:20]}"
    return tampered


def test_request_is_deterministic_and_carries_exact_m16_m19_context() -> None:
    upstream, session, model_request, coaching, first = _m20_request()
    second = build_model_coaching_evaluation_request(
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        created_at=S15,
    )

    assert first == second
    assert first["schema_version"] == (
        MODEL_COACHING_EVALUATION_REQUEST_SCHEMA_VERSION
    )
    assert first["model_coaching_ref"]["coaching_id"] == coaching["coaching_id"]
    assert first["grounded_feedback"] == model_request["grounded_feedback"]
    assert first["rendered_content"] == coaching["rendered_content"]
    assert first["evaluation_presentation"]["comparison"]["comparison_id"] == (
        upstream.comparison.comparison_id
    )
    assert tuple(
        item["dimension"] for item in first["policy"]["dimensions"]
    ) == EVALUATION_DIMENSIONS
    assert first["policy"]["truth_status"] == (
        "not_established_by_m20_evaluation"
    )


def test_complete_passing_judgments_produce_bounded_acceptance() -> None:
    upstream, session, model_request, coaching, request = _m20_request()

    evaluation = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=_evaluation_generation(request),
    )

    assert evaluation["schema_version"] == (
        MODEL_COACHING_EVALUATION_RECORD_SCHEMA_VERSION
    )
    assert evaluation["qualification_status"] == (
        "accepted_under_m20_evaluation_policy"
    )
    assert evaluation["source_integrity"] == (
        "verified_against_exact_m16_m19_sources"
    )
    assert evaluation["truth_status"] == "not_established_by_m20_evaluation"
    assert evaluation["claim_scope"] == "bounded_model_output_quality_assessment"
    assert evaluation["evaluator_provenance"]["kind"] == "fixture"
    assert [item["dimension"] for item in evaluation["judgments"]] == list(
        EVALUATION_DIMENSIONS
    )


def test_fail_dominates_and_unclear_prevents_acceptance() -> None:
    upstream, session, model_request, coaching, request = _m20_request()

    rejected = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=_evaluation_generation(
            request,
            judgments=_judgments(
                failed=("authority_boundary",),
                unclear=("evidence_sufficiency",),
            ),
        ),
    )
    inconclusive = bind_model_coaching_evaluation(
        request=request,
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        generation=_evaluation_generation(
            request,
            judgments=_judgments(unclear=("evidence_sufficiency",)),
        ),
    )

    assert rejected["qualification_status"] == (
        "rejected_under_m20_evaluation_policy"
    )
    assert inconclusive["qualification_status"] == (
        "inconclusive_under_m20_evaluation_policy"
    )


def test_missing_or_duplicate_required_dimension_is_rejected() -> None:
    upstream, session, model_request, coaching, request = _m20_request()
    complete = _judgments()

    with pytest.raises(ModelCoachingEvaluationError, match="cover every required"):
        bind_model_coaching_evaluation(
            request=request,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_evaluation_generation(request, judgments=complete[:-1]),
        )

    duplicate = complete[:-1] + (complete[0],)
    with pytest.raises(ModelCoachingEvaluationError, match="dimensions must be unique"):
        bind_model_coaching_evaluation(
            request=request,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_evaluation_generation(request, judgments=duplicate),
        )


def test_judgment_rejects_unknown_verdict_and_blank_rationale() -> None:
    with pytest.raises(ValueError, match="unsupported evaluation verdict"):
        ModelCoachingEvaluationJudgment(
            dimension="grounding_consistency",
            verdict="approved",  # type: ignore[arg-type]
            rationale="not an M20 verdict",
        )
    with pytest.raises(ValueError, match="rationale must not be blank"):
        ModelCoachingEvaluationJudgment(
            dimension="grounding_consistency",
            verdict="pass",
            rationale="  ",
        )


def test_rehashed_policy_tampering_is_rejected() -> None:
    upstream, session, model_request, coaching, request = _m20_request()
    policy = dict(request["policy"])
    policy["truth_status"] = "semantically_verified_truth"
    tampered = dict(request)
    tampered["policy"] = policy
    tampered = _rehash_m20_request(tampered)

    with pytest.raises(ModelCoachingEvaluationError, match="policy mismatch"):
        bind_model_coaching_evaluation(
            request=tampered,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_evaluation_generation(tampered),
        )


def test_drifted_m19_request_binding_is_rejected_even_if_coaching_is_rehashed() -> None:
    upstream, session, model_request, coaching = _m19_sources()
    tampered = dict(coaching)
    tampered["request_fingerprint"] = "not-the-m19-request"
    tampered = _rehash_m19_coaching(tampered)

    with pytest.raises(ModelCoachingEvaluationError, match="M19 coaching validation"):
        build_model_coaching_evaluation_request(
            coaching=tampered,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S15,
        )


def test_wrong_evaluator_echo_and_predated_evaluation_are_rejected() -> None:
    upstream, session, model_request, coaching, request = _m20_request()

    with pytest.raises(
        ModelCoachingEvaluationError, match="request fingerprint mismatch"
    ):
        bind_model_coaching_evaluation(
            request=request,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_evaluation_generation(
                request, request_fingerprint="wrong-evaluation-request"
            ),
        )

    with pytest.raises(ModelCoachingEvaluationError, match="cannot predate"):
        bind_model_coaching_evaluation(
            request=request,
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            generation=_evaluation_generation(request, generated_at=S14),
        )


def test_evaluator_failure_mutation_and_invalid_result_fail_closed() -> None:
    upstream, session, model_request, coaching = _m19_sources()
    kwargs = {
        "coaching": coaching,
        "model_coaching_request": model_request,
        "session": session,
        "root_analysis": upstream.analysis,
        "decision_comparison": upstream.comparison,
        "request_created_at": S15,
    }

    with pytest.raises(ModelCoachingEvaluationError, match="evaluator failed"):
        run_model_coaching_evaluation(
            evaluator=_Evaluator(failure=RuntimeError("fixture outage")),
            **kwargs,
        )
    with pytest.raises(ModelCoachingEvaluationError, match="mutated"):
        run_model_coaching_evaluation(
            evaluator=_Evaluator(mutate_request=True),
            **kwargs,
        )
    with pytest.raises(ModelCoachingEvaluationError, match="invalid generation"):
        run_model_coaching_evaluation(
            evaluator=_Evaluator(invalid_result=True),
            **kwargs,
        )


def test_evaluation_request_cannot_predate_model_output() -> None:
    upstream, session, model_request, coaching = _m19_sources()

    with pytest.raises(
        ModelCoachingEvaluationError, match="cannot predate model coaching"
    ):
        build_model_coaching_evaluation_request(
            coaching=coaching,
            model_coaching_request=model_request,
            session=session,
            root_analysis=upstream.analysis,
            decision_comparison=upstream.comparison,
            created_at=S13,
        )


@pytest.mark.parametrize(
    "case",
    json.loads(
        (
            Path(__file__).parent
            / "fixtures"
            / "m20_model_coaching_cases.json"
        ).read_text(encoding="utf-8")
    ),
    ids=lambda item: item["case_id"],
)
def test_hermetic_adversarial_corpus_records_expected_bounded_outcome(case) -> None:
    upstream, session, model_request, coaching = _m19_sources(case["rendered_content"])
    failed = tuple(case["failed_dimensions"])
    unclear = tuple(case["unclear_dimensions"])
    request, evaluation = run_model_coaching_evaluation(
        evaluator=_Evaluator(judgments=_judgments(failed=failed, unclear=unclear)),
        coaching=coaching,
        model_coaching_request=model_request,
        session=session,
        root_analysis=upstream.analysis,
        decision_comparison=upstream.comparison,
        request_created_at=S15,
    )

    assert request["rendered_content"] == case["rendered_content"]
    assert evaluation["qualification_status"] == case["expected_status"]
    failed_recorded = {
        item["dimension"]
        for item in evaluation["judgments"]
        if item["verdict"] == "fail"
    }
    assert failed_recorded == set(case["failed_dimensions"])
    assert evaluation["truth_status"] == "not_established_by_m20_evaluation"
