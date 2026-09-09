"""M6C coded local discrepancy assessment with strict provenance boundaries."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.evidence import EvidenceCaptureSession

from .assessment_model import (
    AssessmentStageKind,
    AssessmentStatus,
    CoderKind,
    DiscrepancyCode,
    ReasoningArtifactRef,
    ReasoningAssessmentPolicy,
    ReasoningAssessmentPolicyRef,
    ReasoningCoding,
    ReasoningCodingKind,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
)
from .facts import ReasoningDiscrepancyError
from .model import (
    DiscrepancyFact,
    DiscrepancyFactKind,
    MeasurementCondition,
    ReasoningDiscrepancyContext,
    ReasoningEvidenceKind,
    ReasoningEvidenceRef,
)

_DISCREPANCY_CODES: frozenset[str] = frozenset(
    {
        "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED",
        "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
        "EXPECTED_OPPONENT_REPLY_CONFLICT",
        "EXPECTED_CONTINUATION_CONFLICT",
        "REPORTED_RESULTING_EVALUATION_CONFLICT",
        "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE",
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        "OTHER_LOCAL_DISCREPANCY",
    }
)
_CODING_KINDS: frozenset[str] = frozenset(
    {
        "discrepancy_support",
        "discrepancy_contradiction",
        "discrepancy_unclear",
    }
)
_ALLOWED_STAGE_KINDS: frozenset[str] = frozenset(
    {"MINIMAL_RESPONSE", "STANDARDIZED_PROBE"}
)
_MEASUREMENT_CONDITIONS: frozenset[str] = frozenset(
    {
        "clean",
        "instrument_aware_clean",
        "deviating",
        "contaminated",
        "unknown",
    }
)
_FACT_KINDS: frozenset[str] = frozenset(
    {
        "REPORTED_SELECTED_MOVE_RELATION",
        "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION",
        "EXPECTED_REPLY_RELATION",
        "EXPECTED_CONTINUATION_RELATION",
    }
)
_DISCREPANCY_RELATIONS: frozenset[str] = frozenset(
    {
        "match",
        "conflict",
        "not_explicitly_reported",
        "ambiguous",
        "not_observed",
        "not_comparable",
    }
)
_OBJECTIVE_EVIDENCE_KINDS: frozenset[str] = frozenset(
    {
        "canonical_position",
        "position_feature_packet",
        "position_analysis",
        "analysis_failure",
        "decision_comparison",
        "selection_signal",
        "diagnostic_candidate",
        "diagnostic_batch",
    }
)
_SUPPORTED_PARAMETER_KEYS: frozenset[str] = frozenset({"strong_candidate_basis"})
_INTRINSIC_CODING_CODES: frozenset[str] = frozenset(
    {
        "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED",
        "REPORTED_RESULTING_EVALUATION_CONFLICT",
        "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE",
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
        "OTHER_LOCAL_DISCREPANCY",
    }
)
_FACT_PREREQUISITE_CODES: frozenset[str] = frozenset(
    {
        "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED",
        "EXPECTED_OPPONENT_REPLY_CONFLICT",
        "EXPECTED_CONTINUATION_CONFLICT",
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE",
    }
)
_ASSESSABLE_RELATIONS: frozenset[str] = frozenset(
    {"match", "conflict", "not_explicitly_reported"}
)


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise ReasoningDiscrepancyError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReasoningDiscrepancyError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReasoningDiscrepancyError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _normalize_strings(
    values: tuple[str, ...],
    *,
    label: str,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if not allow_empty and not values:
        raise ReasoningDiscrepancyError(f"{label} must not be empty")
    if any(not value for value in values):
        raise ReasoningDiscrepancyError(f"{label} values must not be empty")
    if len(set(values)) != len(values):
        raise ReasoningDiscrepancyError(f"{label} must be unique")
    return tuple(sorted(values))


def _normalize_pairs(
    values: tuple[tuple[str, str], ...],
    *,
    label: str,
) -> tuple[tuple[str, str], ...]:
    keys = tuple(key for key, _ in values)
    if any(not key or not value for key, value in values):
        raise ReasoningDiscrepancyError(
            f"{label} keys and values must not be empty"
        )
    if len(set(keys)) != len(keys):
        raise ReasoningDiscrepancyError(f"{label} keys must be unique")
    return tuple(sorted(values, key=lambda item: item[0]))


def _policy_ref(
    policy: ReasoningAssessmentPolicy,
) -> ReasoningAssessmentPolicyRef:
    return ReasoningAssessmentPolicyRef(
        policy_id=policy.policy_id,
        version=policy.version,
        fingerprint=policy.policy_fingerprint,
    )


def _fact_ref(fact: DiscrepancyFact) -> ReasoningArtifactRef:
    return ReasoningArtifactRef(
        kind="discrepancy_fact",
        ref_id=fact.fact_id,
        fingerprint=fact.fingerprint,
    )


def _coding_ref(coding: ReasoningCoding) -> ReasoningArtifactRef:
    return ReasoningArtifactRef(
        kind="reasoning_coding",
        ref_id=coding.coding_id,
        fingerprint=coding.fingerprint,
    )


def _assertion_ref(
    assertion: ReasoningDiscrepancyAssertion,
) -> ReasoningArtifactRef:
    return ReasoningArtifactRef(
        kind="discrepancy_assertion",
        ref_id=assertion.assertion_id,
        fingerprint=assertion.fingerprint,
    )


def _validate_context(context: ReasoningDiscrepancyContext) -> None:
    expected = _fingerprint(context.to_dict(include_identity=False))
    if expected != context.context_fingerprint:
        raise ReasoningDiscrepancyError(
            "ReasoningDiscrepancyContext fingerprint mismatch"
        )
    if context.reasoning_context_id != f"reasoning_context_{expected[:20]}":
        raise ReasoningDiscrepancyError(
            "ReasoningDiscrepancyContext identity mismatch"
        )
    if context.measurement_condition not in _MEASUREMENT_CONDITIONS:
        raise ReasoningDiscrepancyError("unknown M6 measurement condition")


def _validate_policy_semantics(policy: ReasoningAssessmentPolicy) -> None:
    if not set(policy.eligible_stage_kinds).issubset(_ALLOWED_STAGE_KINDS):
        raise ReasoningDiscrepancyError(
            "assessment policy contains an unsupported stage kind"
        )
    if not set(policy.allowed_measurement_conditions).issubset(
        _MEASUREMENT_CONDITIONS
    ):
        raise ReasoningDiscrepancyError(
            "assessment policy contains an unknown measurement condition"
        )
    if not set(policy.required_objective_evidence).issubset(
        _OBJECTIVE_EVIDENCE_KINDS
    ):
        raise ReasoningDiscrepancyError(
            "assessment policy contains non-objective required evidence"
        )
    if not set(policy.permitted_fact_kinds).issubset(_FACT_KINDS):
        raise ReasoningDiscrepancyError(
            "assessment policy contains an unknown discrepancy fact kind"
        )
    if not set(policy.permitted_discrepancy_codes).issubset(_DISCREPANCY_CODES):
        raise ReasoningDiscrepancyError(
            "assessment policy contains an unknown discrepancy code"
        )
    if not set(policy.coding_requirements).issubset(
        policy.permitted_discrepancy_codes
    ):
        raise ReasoningDiscrepancyError(
            "coding requirements must be a subset of permitted discrepancy codes"
        )
    missing_intrinsic = set(policy.permitted_discrepancy_codes).intersection(
        _INTRINSIC_CODING_CODES
    ).difference(policy.coding_requirements)
    if missing_intrinsic:
        raise ReasoningDiscrepancyError(
            "intrinsically coded discrepancy codes must require coding: "
            f"{sorted(missing_intrinsic)!r}"
        )
    parameter_map = dict(policy.thresholds_or_parameters)
    parameter_keys = set(parameter_map)
    unknown_parameters = parameter_keys.difference(_SUPPORTED_PARAMETER_KEYS)
    if unknown_parameters:
        raise ReasoningDiscrepancyError(
            f"unsupported M6C assessment parameter(s): "
            f"{sorted(unknown_parameters)!r}"
        )
    strong_basis = parameter_map.get("strong_candidate_basis")
    if strong_basis is not None and strong_basis != "engine_rank1":
        raise ReasoningDiscrepancyError(
            "strong_candidate_basis currently supports only 'engine_rank1'"
        )
    strong_code = "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED"
    if (
        strong_code in policy.permitted_discrepancy_codes
        and strong_code not in policy.coding_requirements
        and strong_basis != "engine_rank1"
    ):
        raise ReasoningDiscrepancyError(
            "deterministic strong-candidate assessment requires "
            "strong_candidate_basis=engine_rank1"
        )


def _validate_policy(policy: ReasoningAssessmentPolicy) -> None:
    expected = _fingerprint(policy.to_dict(include_identity=False))
    if expected != policy.policy_fingerprint:
        raise ReasoningDiscrepancyError("assessment policy fingerprint mismatch")
    _validate_policy_semantics(policy)


def _validate_fact(
    context: ReasoningDiscrepancyContext,
    fact: DiscrepancyFact,
) -> None:
    if fact.reasoning_context_id != context.reasoning_context_id:
        raise ReasoningDiscrepancyError(
            "DiscrepancyFact does not belong to ReasoningDiscrepancyContext"
        )
    expected = _fingerprint(fact.to_dict(include_identity=False))
    if expected != fact.fingerprint:
        raise ReasoningDiscrepancyError("DiscrepancyFact fingerprint mismatch")
    if fact.fact_id != f"discrepancy_fact_{expected[:20]}":
        raise ReasoningDiscrepancyError("DiscrepancyFact identity mismatch")
    if fact.stage_id not in context.assessment_stage_ids:
        raise ReasoningDiscrepancyError(
            "DiscrepancyFact stage is outside ReasoningDiscrepancyContext"
        )
    if fact.kind not in _FACT_KINDS:
        raise ReasoningDiscrepancyError("unknown M6B discrepancy fact kind")
    if fact.relation not in _DISCREPANCY_RELATIONS:
        raise ReasoningDiscrepancyError("unknown M6B discrepancy relation")


def _context_player_refs(
    context: ReasoningDiscrepancyContext,
) -> tuple[ReasoningEvidenceRef, ...]:
    return (
        context.player_decision_context_ref,
        context.capture_session_ref,
        *context.player_response_refs,
        *context.evidence_freeze_refs,
        *context.prompt_presentation_refs,
        *context.exposure_refs,
        *context.protocol_deviation_refs,
    )


def _context_objective_refs(
    context: ReasoningDiscrepancyContext,
) -> tuple[ReasoningEvidenceRef, ...]:
    optional: list[ReasoningEvidenceRef] = []
    if context.diagnostic_batch_ref is not None:
        optional.append(context.diagnostic_batch_ref)
    if context.position_feature_packet_ref is not None:
        optional.append(context.position_feature_packet_ref)
    return (
        context.diagnostic_candidate_ref,
        *optional,
        context.canonical_position_ref,
        *context.position_analysis_refs,
        context.decision_comparison_ref,
        *context.selection_signal_refs,
    )


def _ref_map(
    refs: tuple[ReasoningEvidenceRef, ...],
) -> dict[tuple[str, str, str], ReasoningEvidenceRef]:
    return {
        (item.authority, item.kind, item.ref_id): item
        for item in refs
    }


def _validate_supplied_refs(
    supplied: tuple[ReasoningEvidenceRef, ...],
    available: tuple[ReasoningEvidenceRef, ...],
    *,
    label: str,
) -> tuple[ReasoningEvidenceRef, ...]:
    keys = tuple((item.authority, item.kind, item.ref_id) for item in supplied)
    if len(set(keys)) != len(keys):
        raise ReasoningDiscrepancyError(f"{label} must be unique")
    available_map = _ref_map(available)
    normalized: list[ReasoningEvidenceRef] = []
    for item in supplied:
        key = (item.authority, item.kind, item.ref_id)
        expected = available_map.get(key)
        if expected is None or expected.fingerprint != item.fingerprint:
            raise ReasoningDiscrepancyError(
                f"{label} contains evidence outside the M6 context"
            )
        normalized.append(item)
    return tuple(
        sorted(
            normalized,
            key=lambda item: (item.authority, item.kind, item.ref_id),
        )
    )


def _stage_ids_from_sources(
    context: ReasoningDiscrepancyContext,
    player_refs: tuple[ReasoningEvidenceRef, ...],
    facts: tuple[DiscrepancyFact, ...],
) -> tuple[str, ...]:
    stage_by_ref_id: dict[str, str] = {}
    for ref_collection in (
        context.player_response_refs,
        context.evidence_freeze_refs,
        context.prompt_presentation_refs,
    ):
        if len(ref_collection) != len(context.assessment_stage_ids):
            raise ReasoningDiscrepancyError(
                "M6 context stage-specific evidence cardinality mismatch"
            )
        for stage_id, ref in zip(
            context.assessment_stage_ids,
            ref_collection,
            strict=True,
        ):
            stage_by_ref_id[ref.ref_id] = stage_id

    found = {
        stage_by_ref_id[item.ref_id]
        for item in player_refs
        if item.ref_id in stage_by_ref_id
    }
    found.update(item.stage_id for item in facts)
    ordered = tuple(
        stage_id
        for stage_id in context.assessment_stage_ids
        if stage_id in found
    )
    if not ordered:
        raise ReasoningDiscrepancyError(
            "ReasoningCoding must cite stage-specific player evidence or facts"
        )
    return ordered


def _validate_coding(
    context: ReasoningDiscrepancyContext,
    coding: ReasoningCoding,
    available_facts: tuple[DiscrepancyFact, ...],
) -> None:
    if coding.reasoning_context_id != context.reasoning_context_id:
        raise ReasoningDiscrepancyError(
            "ReasoningCoding does not belong to ReasoningDiscrepancyContext"
        )
    expected = _fingerprint(coding.to_dict(include_identity=False))
    if expected != coding.fingerprint:
        raise ReasoningDiscrepancyError("ReasoningCoding fingerprint mismatch")
    if coding.coding_id != f"reasoning_coding_{expected[:20]}":
        raise ReasoningDiscrepancyError("ReasoningCoding identity mismatch")
    if coding.coding_kind not in _CODING_KINDS:
        raise ReasoningDiscrepancyError("unknown ReasoningCoding kind")
    if coding.code not in _DISCREPANCY_CODES:
        raise ReasoningDiscrepancyError("unknown discrepancy code")
    if not set(coding.stage_ids).issubset(context.assessment_stage_ids):
        raise ReasoningDiscrepancyError(
            "ReasoningCoding stage is outside ReasoningDiscrepancyContext"
        )

    player_refs = _validate_supplied_refs(
        coding.source_player_evidence_refs,
        _context_player_refs(context),
        label="ReasoningCoding source player evidence refs",
    )
    _validate_supplied_refs(
        coding.source_objective_evidence_refs,
        _context_objective_refs(context),
        label="ReasoningCoding source objective evidence refs",
    )

    facts_by_id = {item.fact_id: item for item in available_facts}
    if len(facts_by_id) != len(available_facts):
        raise ReasoningDiscrepancyError("available facts must be unique")
    source_facts: list[DiscrepancyFact] = []
    seen_fact_ids: set[str] = set()
    for ref in coding.source_fact_refs:
        if ref.kind != "discrepancy_fact":
            raise ReasoningDiscrepancyError(
                "ReasoningCoding source fact ref has the wrong artifact kind"
            )
        fact = facts_by_id.get(ref.ref_id)
        if fact is None or fact.fingerprint != ref.fingerprint:
            raise ReasoningDiscrepancyError(
                "ReasoningCoding source fact is not an exact assessment fact"
            )
        if ref.ref_id in seen_fact_ids:
            raise ReasoningDiscrepancyError(
                "ReasoningCoding source fact refs must be unique"
            )
        seen_fact_ids.add(ref.ref_id)
        source_facts.append(fact)

    derived_stage_ids = _stage_ids_from_sources(
        context,
        player_refs,
        tuple(source_facts),
    )
    if derived_stage_ids != coding.stage_ids:
        raise ReasoningDiscrepancyError(
            "ReasoningCoding stage provenance does not match its source evidence"
        )


def define_reasoning_assessment_policy(
    *,
    policy_id: str,
    version: str,
    eligible_stage_kinds: tuple[AssessmentStageKind, ...],
    allowed_measurement_conditions: tuple[MeasurementCondition, ...],
    required_objective_evidence: tuple[ReasoningEvidenceKind, ...] = (),
    permitted_fact_kinds: tuple[DiscrepancyFactKind, ...] = (),
    permitted_discrepancy_codes: tuple[DiscrepancyCode, ...] = (),
    coding_requirements: tuple[DiscrepancyCode, ...] = (),
    thresholds_or_parameters: tuple[tuple[str, str], ...] = (),
) -> ReasoningAssessmentPolicy:
    """Create one content-addressed M6C assessment policy."""
    if not policy_id:
        raise ReasoningDiscrepancyError("policy_id must not be empty")
    if not version:
        raise ReasoningDiscrepancyError("policy version must not be empty")

    stage_kinds = _normalize_strings(
        eligible_stage_kinds,
        label="eligible stage kinds",
        allow_empty=False,
    )
    if not set(stage_kinds).issubset(_ALLOWED_STAGE_KINDS):
        raise ReasoningDiscrepancyError(
            "M6C supports only frozen pre-reveal assessment stage kinds"
        )
    conditions = _normalize_strings(
        allowed_measurement_conditions,
        label="allowed measurement conditions",
        allow_empty=False,
    )
    if not set(conditions).issubset(_MEASUREMENT_CONDITIONS):
        raise ReasoningDiscrepancyError(
            "allowed_measurement_conditions contains an unknown condition"
        )
    objective_kinds = _normalize_strings(
        required_objective_evidence,
        label="required objective evidence",
    )
    if not set(objective_kinds).issubset(_OBJECTIVE_EVIDENCE_KINDS):
        raise ReasoningDiscrepancyError(
            "required_objective_evidence may contain objective evidence kinds only"
        )
    fact_kinds = _normalize_strings(
        permitted_fact_kinds,
        label="permitted fact kinds",
    )
    if not set(fact_kinds).issubset(_FACT_KINDS):
        raise ReasoningDiscrepancyError(
            "permitted_fact_kinds contains an unknown M6B fact kind"
        )
    codes = _normalize_strings(
        permitted_discrepancy_codes,
        label="permitted discrepancy codes",
    )
    if not set(codes).issubset(_DISCREPANCY_CODES):
        raise ReasoningDiscrepancyError(
            "policy contains an unknown discrepancy code"
        )
    coding_codes = _normalize_strings(
        coding_requirements,
        label="coding requirements",
    )
    if not set(coding_codes).issubset(codes):
        raise ReasoningDiscrepancyError(
            "coding requirements must be a subset of permitted discrepancy codes"
        )
    missing_intrinsic = set(codes).intersection(
        _INTRINSIC_CODING_CODES
    ).difference(coding_codes)
    if missing_intrinsic:
        raise ReasoningDiscrepancyError(
            "intrinsically coded discrepancy codes must require coding: "
            f"{sorted(missing_intrinsic)!r}"
        )
    parameters = _normalize_pairs(
        thresholds_or_parameters,
        label="assessment parameters",
    )
    parameter_keys = {key for key, _ in parameters}
    unknown_parameters = parameter_keys.difference(_SUPPORTED_PARAMETER_KEYS)
    if unknown_parameters:
        raise ReasoningDiscrepancyError(
            f"unsupported M6C assessment parameter(s): "
            f"{sorted(unknown_parameters)!r}"
        )
    parameter_map = dict(parameters)
    strong_basis = parameter_map.get("strong_candidate_basis")
    if strong_basis is not None and strong_basis != "engine_rank1":
        raise ReasoningDiscrepancyError(
            "strong_candidate_basis currently supports only 'engine_rank1'"
        )
    strong_code = "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED"
    if (
        strong_code in codes
        and strong_code not in coding_codes
        and strong_basis != "engine_rank1"
    ):
        raise ReasoningDiscrepancyError(
            "deterministic strong-candidate assessment requires "
            "strong_candidate_basis=engine_rank1"
        )

    payload: dict[str, Any] = {
        "policy_id": policy_id,
        "version": version,
        "eligible_stage_kinds": list(stage_kinds),
        "allowed_measurement_conditions": list(conditions),
        "required_objective_evidence": list(objective_kinds),
        "permitted_fact_kinds": list(fact_kinds),
        "permitted_discrepancy_codes": list(codes),
        "coding_requirements": list(coding_codes),
        "thresholds_or_parameters": [list(item) for item in parameters],
        "claim_scope": "position_local",
    }
    fingerprint = _fingerprint(payload)
    try:
        policy = ReasoningAssessmentPolicy(
            policy_id=policy_id,
            version=version,
            policy_fingerprint=fingerprint,
            eligible_stage_kinds=stage_kinds,
            allowed_measurement_conditions=conditions,
            required_objective_evidence=objective_kinds,
            permitted_fact_kinds=fact_kinds,
            permitted_discrepancy_codes=codes,
            coding_requirements=coding_codes,
            thresholds_or_parameters=parameters,
        )
    except ValueError as exc:
        raise ReasoningDiscrepancyError(str(exc)) from exc
    _validate_policy_semantics(policy)
    return policy


def record_reasoning_coding(
    *,
    context: ReasoningDiscrepancyContext,
    available_facts: tuple[DiscrepancyFact, ...],
    coding_kind: ReasoningCodingKind,
    code: DiscrepancyCode,
    statement: str,
    source_player_evidence_refs: tuple[ReasoningEvidenceRef, ...],
    source_objective_evidence_refs: tuple[ReasoningEvidenceRef, ...] = (),
    source_facts: tuple[DiscrepancyFact, ...] = (),
    coder_kind: CoderKind,
    coder_id: str,
    coder_version: str,
    rubric_or_instruction_fingerprint: str,
    created_at: str,
    confidence: float | None = None,
    uncertainty_note: str | None = None,
) -> ReasoningCoding:
    """Record human/model judgment without mutating M5 evidence or M6B facts."""
    _validate_context(context)
    if coding_kind not in _CODING_KINDS:
        raise ReasoningDiscrepancyError("unknown ReasoningCoding kind")
    if code not in _DISCREPANCY_CODES:
        raise ReasoningDiscrepancyError("unknown discrepancy code")
    for name, value in (
        ("statement", statement),
        ("coder_id", coder_id),
        ("coder_version", coder_version),
        ("rubric_or_instruction_fingerprint", rubric_or_instruction_fingerprint),
    ):
        if not value:
            raise ReasoningDiscrepancyError(f"{name} must not be empty")
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ReasoningDiscrepancyError("confidence must be between 0 and 1")

    created_time = _parse_timestamp(created_at)
    if created_time < _parse_timestamp(context.created_at):
        raise ReasoningDiscrepancyError(
            "ReasoningCoding cannot precede its M6 context"
        )

    facts_by_id: dict[str, DiscrepancyFact] = {}
    fact_slot_keys: set[tuple[str, str]] = set()
    for fact in available_facts:
        _validate_fact(context, fact)
        if fact.fact_id in facts_by_id:
            raise ReasoningDiscrepancyError("available facts must be unique")
        fact_slot = (fact.stage_id, fact.kind)
        if fact_slot in fact_slot_keys:
            raise ReasoningDiscrepancyError(
                "available facts must be unique by stage and fact kind"
            )
        fact_slot_keys.add(fact_slot)
        facts_by_id[fact.fact_id] = fact

    player_refs = _validate_supplied_refs(
        source_player_evidence_refs,
        _context_player_refs(context),
        label="source player evidence refs",
    )
    objective_refs = _validate_supplied_refs(
        source_objective_evidence_refs,
        _context_objective_refs(context),
        label="source objective evidence refs",
    )

    normalized_source_facts: list[DiscrepancyFact] = []
    seen_fact_ids: set[str] = set()
    for fact in source_facts:
        expected = facts_by_id.get(fact.fact_id)
        if expected is None or expected.fingerprint != fact.fingerprint:
            raise ReasoningDiscrepancyError(
                "source fact is not an exact available M6B fact"
            )
        if fact.fact_id in seen_fact_ids:
            raise ReasoningDiscrepancyError("source facts must be unique")
        seen_fact_ids.add(fact.fact_id)
        normalized_source_facts.append(fact)
    normalized_source_facts.sort(key=lambda item: item.fact_id)

    if not (player_refs or objective_refs or normalized_source_facts):
        raise ReasoningDiscrepancyError(
            "ReasoningCoding must cite source evidence"
        )
    stage_ids = _stage_ids_from_sources(
        context,
        player_refs,
        tuple(normalized_source_facts),
    )
    fact_refs = tuple(_fact_ref(item) for item in normalized_source_facts)

    payload: dict[str, Any] = {
        "reasoning_context_id": context.reasoning_context_id,
        "coding_kind": coding_kind,
        "code": code,
        "statement": statement,
        "stage_ids": list(stage_ids),
        "source_player_evidence_refs": [
            item.to_dict() for item in player_refs
        ],
        "source_objective_evidence_refs": [
            item.to_dict() for item in objective_refs
        ],
        "source_fact_refs": [item.to_dict() for item in fact_refs],
        "coder_kind": coder_kind,
        "coder_id": coder_id,
        "coder_version": coder_version,
        "rubric_or_instruction_fingerprint": rubric_or_instruction_fingerprint,
        "confidence": confidence,
        "uncertainty_note": uncertainty_note,
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        return ReasoningCoding(
            coding_id=f"reasoning_coding_{fingerprint[:20]}",
            fingerprint=fingerprint,
            reasoning_context_id=context.reasoning_context_id,
            coding_kind=coding_kind,
            code=code,
            statement=statement,
            stage_ids=stage_ids,
            source_player_evidence_refs=player_refs,
            source_objective_evidence_refs=objective_refs,
            source_fact_refs=fact_refs,
            coder_kind=coder_kind,
            coder_id=coder_id,
            coder_version=coder_version,
            rubric_or_instruction_fingerprint=rubric_or_instruction_fingerprint,
            confidence=confidence,
            uncertainty_note=uncertainty_note,
            created_at=created_at,
        )
    except ValueError as exc:
        raise ReasoningDiscrepancyError(str(exc)) from exc


def _validate_capture_session(
    context: ReasoningDiscrepancyContext,
    session: EvidenceCaptureSession,
) -> None:
    if session.capture_session_id != context.capture_session_ref.ref_id:
        raise ReasoningDiscrepancyError(
            "capture session does not match M6 context"
        )
    if session.snapshot_fingerprint != context.capture_session_ref.fingerprint:
        raise ReasoningDiscrepancyError(
            "capture session fingerprint does not match M6 context"
        )


def _stage_kind_map(
    context: ReasoningDiscrepancyContext,
    session: EvidenceCaptureSession,
) -> dict[str, str]:
    protocol_map = {item.stage_id: item for item in session.protocol.stages}
    result: dict[str, str] = {}
    for stage_id in context.assessment_stage_ids:
        stage = protocol_map.get(stage_id)
        if stage is None:
            raise ReasoningDiscrepancyError(
                "M6 assessment stage is missing from capture protocol"
            )
        if stage.phase != "pre_reveal":
            raise ReasoningDiscrepancyError(
                "M6C primary assessment stage is not pre-reveal"
            )
        result[stage_id] = stage.stage_kind
    return result


def _objective_kinds_present(
    context: ReasoningDiscrepancyContext,
) -> frozenset[str]:
    return frozenset(item.kind for item in _context_objective_refs(context))


def _parameter(
    policy: ReasoningAssessmentPolicy,
    key: str,
) -> str | None:
    return dict(policy.thresholds_or_parameters).get(key)


def _facts_supporting_code(
    *,
    code: str,
    stage_id: str,
    facts: tuple[DiscrepancyFact, ...],
    policy: ReasoningAssessmentPolicy,
) -> tuple[DiscrepancyFact, ...]:
    stage_facts = tuple(item for item in facts if item.stage_id == stage_id)
    if code == "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED":
        if _parameter(policy, "strong_candidate_basis") != "engine_rank1":
            return ()
        return tuple(
            item
            for item in stage_facts
            if item.kind == "EXPLICIT_CANDIDATE_MEMBERSHIP_RELATION"
            and item.relation == "not_explicitly_reported"
            and isinstance(item.objective_value, dict)
            and bool(item.objective_value.get("engine_rank1_uci"))
        )
    if code == "EXPECTED_OPPONENT_REPLY_CONFLICT":
        return tuple(
            item
            for item in stage_facts
            if item.kind == "EXPECTED_REPLY_RELATION"
            and item.relation == "conflict"
        )
    if code == "EXPECTED_CONTINUATION_CONFLICT":
        return tuple(
            item
            for item in stage_facts
            if item.kind == "EXPECTED_CONTINUATION_RELATION"
            and item.relation == "conflict"
        )
    if code == "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE":
        return tuple(
            item
            for item in stage_facts
            if item.kind == "REPORTED_SELECTED_MOVE_RELATION"
            and item.relation == "match"
        )
    return ()


def _assertion_statement(
    code: str,
    stage_ids: tuple[str, ...],
) -> str:
    stage_text = (
        f"stage {stage_ids[0]}"
        if len(stage_ids) == 1
        else f"stages {', '.join(stage_ids)}"
    )
    statements = {
        "OBJECTIVELY_RELEVANT_FEATURE_NOT_EXPLICITLY_REPORTED": (
            f"At {stage_text}, provenance-bound coding supports that an "
            "objectively evidenced feature treated as relevant under the "
            "assessment policy was not explicitly reported."
        ),
        "STRONG_OBJECTIVE_CANDIDATE_NOT_EXPLICITLY_REPORTED": (
            f"At {stage_text}, a candidate meeting the assessment policy's "
            "explicit objective-strength basis was not explicitly included "
            "in the structured candidate report."
        ),
        "EXPECTED_OPPONENT_REPLY_CONFLICT": (
            f"At {stage_text}, the explicitly reported expected opponent "
            "reply conflicts with the qualified evidence cited by the "
            "supporting deterministic fact."
        ),
        "EXPECTED_CONTINUATION_CONFLICT": (
            f"At {stage_text}, the explicitly reported continuation "
            "conflicts with the qualified evidence cited by the supporting "
            "deterministic fact."
        ),
        "REPORTED_RESULTING_EVALUATION_CONFLICT": (
            f"At {stage_text}, provenance-bound coding supports a conflict "
            "between the explicitly reported resulting evaluation and cited "
            "qualified objective evidence."
        ),
        "STATED_TARGET_WITHOUT_REPORTED_EXECUTABLE_MOVE": (
            f"At {stage_text}, provenance-bound coding supports that a stated "
            "target was present while no executable realization was "
            "explicitly reported."
        ),
        "CORRECT_MOVE_WITH_INCOMPLETE_REPORTED_RATIONALE": (
            f"At {stage_text}, the reported move matches the cited qualified "
            "move relation while provenance-bound coding supports that the "
            "reported rationale is incomplete."
        ),
        "OTHER_LOCAL_DISCREPANCY": (
            f"At {stage_text}, provenance-bound coding supports the specified "
            "other position-local discrepancy under the assessment policy."
        ),
    }
    return statements[code]


def _build_assertion(
    *,
    context: ReasoningDiscrepancyContext,
    policy: ReasoningAssessmentPolicy,
    code: DiscrepancyCode,
    stage_ids: tuple[str, ...],
    supporting_facts: tuple[DiscrepancyFact, ...],
    supporting_codings: tuple[ReasoningCoding, ...],
    contradictory_codings: tuple[ReasoningCoding, ...] = (),
) -> ReasoningDiscrepancyAssertion:
    fact_refs = tuple(
        sorted(
            (_fact_ref(item) for item in supporting_facts),
            key=lambda item: item.ref_id,
        )
    )
    coding_refs = tuple(
        sorted(
            (_coding_ref(item) for item in supporting_codings),
            key=lambda item: item.ref_id,
        )
    )
    contradiction_refs = tuple(
        sorted(
            (_coding_ref(item) for item in contradictory_codings),
            key=lambda item: item.ref_id,
        )
    )
    if fact_refs and coding_refs:
        basis = "mixed"
    elif fact_refs:
        basis = "deterministic"
    else:
        basis = "coded"
    statement = _assertion_statement(code, stage_ids)
    payload: dict[str, Any] = {
        "reasoning_context_id": context.reasoning_context_id,
        "assessment_policy_ref": _policy_ref(policy).to_dict(),
        "code": code,
        "statement": statement,
        "stage_ids": list(stage_ids),
        "supporting_fact_refs": [item.to_dict() for item in fact_refs],
        "supporting_coding_refs": [item.to_dict() for item in coding_refs],
        "contradictory_evidence_refs": [
            item.to_dict() for item in contradiction_refs
        ],
        "basis_kind": basis,
        "claim_scope": "position_local",
    }
    fingerprint = _fingerprint(payload)
    try:
        return ReasoningDiscrepancyAssertion(
            assertion_id=f"reasoning_assertion_{fingerprint[:20]}",
            fingerprint=fingerprint,
            reasoning_context_id=context.reasoning_context_id,
            assessment_policy_ref=_policy_ref(policy),
            code=code,
            statement=statement,
            stage_ids=stage_ids,
            supporting_fact_refs=fact_refs,
            supporting_coding_refs=coding_refs,
            contradictory_evidence_refs=contradiction_refs,
            basis_kind=basis,
        )
    except ValueError as exc:
        raise ReasoningDiscrepancyError(str(exc)) from exc


def _derive_assertions(
    *,
    context: ReasoningDiscrepancyContext,
    facts: tuple[DiscrepancyFact, ...],
    codings: tuple[ReasoningCoding, ...],
    policy: ReasoningAssessmentPolicy,
    eligible_stage_ids: tuple[str, ...],
) -> tuple[
    tuple[ReasoningDiscrepancyAssertion, ...],
    tuple[str, ...],
]:
    assertions: list[ReasoningDiscrepancyAssertion] = []
    uncertainty_reasons: set[str] = set()
    coding_required = set(policy.coding_requirements)

    for code in policy.permitted_discrepancy_codes:
        if code not in coding_required:
            for stage_id in eligible_stage_ids:
                supporting_facts = _facts_supporting_code(
                    code=code,
                    stage_id=stage_id,
                    facts=facts,
                    policy=policy,
                )
                for fact in supporting_facts:
                    assertions.append(
                        _build_assertion(
                            context=context,
                            policy=policy,
                            code=code,
                            stage_ids=(stage_id,),
                            supporting_facts=(fact,),
                            supporting_codings=(),
                        )
                    )
            continue

        code_codings = tuple(item for item in codings if item.code == code)
        stage_groups = sorted({item.stage_ids for item in code_codings})
        for stage_ids in stage_groups:
            group = tuple(
                item for item in code_codings if item.stage_ids == stage_ids
            )
            supports = tuple(
                item
                for item in group
                if item.coding_kind == "discrepancy_support"
            )
            contradictions = tuple(
                item
                for item in group
                if item.coding_kind == "discrepancy_contradiction"
            )
            unclear = tuple(
                item
                for item in group
                if item.coding_kind == "discrepancy_unclear"
            )
            if unclear or (supports and contradictions):
                uncertainty_reasons.add(
                    "CODING_DISAGREEMENT:"
                    f"{code}:{','.join(stage_ids)}"
                )
                continue
            if not supports:
                continue

            supporting_facts: list[DiscrepancyFact] = []
            if code in _FACT_PREREQUISITE_CODES:
                for stage_id in stage_ids:
                    per_stage = _facts_supporting_code(
                        code=code,
                        stage_id=stage_id,
                        facts=facts,
                        policy=policy,
                    )
                    if not per_stage:
                        uncertainty_reasons.add(
                            "CODING_SUPPORT_MISSING_REQUIRED_FACT:"
                            f"{code}:{stage_id}"
                        )
                        supporting_facts = []
                        break
                    supporting_facts.extend(per_stage)
                if not supporting_facts:
                    continue

            assertions.append(
                _build_assertion(
                    context=context,
                    policy=policy,
                    code=code,
                    stage_ids=stage_ids,
                    supporting_facts=tuple(supporting_facts),
                    supporting_codings=supports,
                )
            )

    assertions.sort(
        key=lambda item: (item.stage_ids, item.code, item.assertion_id)
    )
    return tuple(assertions), tuple(sorted(uncertainty_reasons))


def assess_reasoning_discrepancy(
    *,
    context: ReasoningDiscrepancyContext,
    capture_session: EvidenceCaptureSession,
    facts: tuple[DiscrepancyFact, ...],
    codings: tuple[ReasoningCoding, ...],
    policy: ReasoningAssessmentPolicy,
    created_at: str,
) -> tuple[
    ReasoningDiscrepancyAssessment,
    tuple[ReasoningDiscrepancyAssertion, ...],
]:
    """Assess one exact M6 context without recurrence or learner-level inference."""
    _validate_context(context)
    _validate_policy(policy)
    _validate_capture_session(context, capture_session)
    created_time = _parse_timestamp(created_at)
    if created_time < _parse_timestamp(context.created_at):
        raise ReasoningDiscrepancyError(
            "ReasoningDiscrepancyAssessment cannot precede its M6 context"
        )

    fact_ids: set[str] = set()
    fact_slots: set[tuple[str, str]] = set()
    for fact in facts:
        _validate_fact(context, fact)
        if fact.fact_id in fact_ids:
            raise ReasoningDiscrepancyError("assessment facts must be unique")
        fact_ids.add(fact.fact_id)
        fact_slot = (fact.stage_id, fact.kind)
        if fact_slot in fact_slots:
            raise ReasoningDiscrepancyError(
                "assessment facts must be unique by stage and fact kind"
            )
        fact_slots.add(fact_slot)

    coding_ids: set[str] = set()
    for coding in codings:
        _validate_coding(context, coding, facts)
        if coding.coding_id in coding_ids:
            raise ReasoningDiscrepancyError("assessment codings must be unique")
        coding_ids.add(coding.coding_id)
        if created_time < _parse_timestamp(coding.created_at):
            raise ReasoningDiscrepancyError(
                "assessment cannot precede a cited ReasoningCoding"
            )

    stage_kind_by_id = _stage_kind_map(context, capture_session)
    eligible_stage_ids = tuple(
        stage_id
        for stage_id in context.assessment_stage_ids
        if stage_kind_by_id[stage_id] in policy.eligible_stage_kinds
    )
    eligible_facts = tuple(
        item
        for item in facts
        if item.stage_id in eligible_stage_ids
        and item.kind in policy.permitted_fact_kinds
    )
    eligible_codings = tuple(
        item
        for item in codings
        if item.code in policy.coding_requirements
        and set(item.stage_ids).issubset(eligible_stage_ids)
    )

    hard_reasons: set[str] = set()
    if context.measurement_condition not in policy.allowed_measurement_conditions:
        hard_reasons.add(
            "MEASUREMENT_CONDITION_NOT_ALLOWED:"
            f"{context.measurement_condition}"
        )
    if not eligible_stage_ids:
        hard_reasons.add("NO_POLICY_ELIGIBLE_STAGE")
    present_objective_kinds = _objective_kinds_present(context)
    for kind in policy.required_objective_evidence:
        if kind not in present_objective_kinds:
            hard_reasons.add(f"MISSING_REQUIRED_OBJECTIVE_EVIDENCE:{kind}")

    assertions: tuple[ReasoningDiscrepancyAssertion, ...] = ()
    uncertainty_reasons: tuple[str, ...] = ()
    if not hard_reasons:
        assertions, uncertainty_reasons = _derive_assertions(
            context=context,
            facts=eligible_facts,
            codings=eligible_codings,
            policy=policy,
            eligible_stage_ids=eligible_stage_ids,
        )

    contradiction_codings = tuple(
        item
        for item in eligible_codings
        if item.coding_kind == "discrepancy_contradiction"
    )
    contradictory_refs = tuple(
        sorted(
            (_coding_ref(item) for item in contradiction_codings),
            key=lambda item: item.ref_id,
        )
    )

    assessable_facts = tuple(
        item for item in eligible_facts if item.relation in _ASSESSABLE_RELATIONS
    )
    assessable_codings = tuple(
        item
        for item in eligible_codings
        if item.coding_kind in {
            "discrepancy_support",
            "discrepancy_contradiction",
        }
    )

    if hard_reasons:
        status: AssessmentStatus = "unscorable"
        status_reasons = tuple(sorted(hard_reasons))
        assertions = ()
    elif assertions:
        status = "discrepancy_supported"
        support_reasons = {
            f"SUPPORTED_ASSERTION:{item.code}:{','.join(item.stage_ids)}"
            for item in assertions
        }
        status_reasons = tuple(
            sorted(support_reasons.union(uncertainty_reasons))
        )
    elif uncertainty_reasons:
        status = "unclear"
        status_reasons = uncertainty_reasons
    elif not (assessable_facts or assessable_codings):
        status = "unscorable"
        status_reasons = ("NO_ASSESSABLE_DIMENSIONS",)
    else:
        status = "no_supported_discrepancy"
        status_reasons = (
            "NO_SUPPORTED_DISCREPANCY_WITHIN_ASSESSED_DIMENSIONS",
        )

    fact_refs = tuple(
        sorted(
            (_fact_ref(item) for item in eligible_facts),
            key=lambda item: item.ref_id,
        )
    )
    coding_refs = tuple(
        sorted(
            (_coding_ref(item) for item in eligible_codings),
            key=lambda item: item.ref_id,
        )
    )
    assertion_refs = tuple(_assertion_ref(item) for item in assertions)
    payload: dict[str, Any] = {
        "reasoning_context_id": context.reasoning_context_id,
        "assessment_policy_ref": _policy_ref(policy).to_dict(),
        "status": status,
        "assessed_stage_ids": list(eligible_stage_ids),
        "assertion_refs": [item.to_dict() for item in assertion_refs],
        "fact_refs": [item.to_dict() for item in fact_refs],
        "coding_refs": [item.to_dict() for item in coding_refs],
        "contradictory_evidence_refs": [
            item.to_dict() for item in contradictory_refs
        ],
        "measurement_condition": context.measurement_condition,
        "status_reasons": list(status_reasons),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        assessment = ReasoningDiscrepancyAssessment(
            assessment_id=f"reasoning_assessment_{fingerprint[:20]}",
            fingerprint=fingerprint,
            reasoning_context_id=context.reasoning_context_id,
            assessment_policy_ref=_policy_ref(policy),
            status=status,
            assessed_stage_ids=eligible_stage_ids,
            assertion_refs=assertion_refs,
            fact_refs=fact_refs,
            coding_refs=coding_refs,
            contradictory_evidence_refs=contradictory_refs,
            measurement_condition=context.measurement_condition,
            status_reasons=status_reasons,
            created_at=created_at,
        )
    except ValueError as exc:
        raise ReasoningDiscrepancyError(str(exc)) from exc
    return assessment, assertions
