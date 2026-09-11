"""M33 compact provenance trace for persisted deterministic M16 feedback."""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from chess_mentor_engine.chess import canonical_json
from chess_mentor_engine.feedback.composer import (
    FEEDBACK_SCHEMA_VERSION,
    GroundedFeedbackError,
    _REFLECTION_PROMPTS,
    _learner_context_content,
    _objective_content,
    _policy_payload,
    _reasoning_content,
    _reflection_content,
    _section_refs,
    _validate_chronology,
    _validate_hypothesis_context,
    _validate_tutor_comparison,
)
from chess_mentor_engine.participant_review_package import M30_SCHEMA_VERSION
from chess_mentor_engine.presentation import PRESENTATION_SCHEMA_VERSION
from chess_mentor_engine.review import COACH_REVIEW_SCHEMA_VERSION
from chess_mentor_engine.review_delivery import (
    M32_SCHEMA_VERSION,
    ReviewDeliveryFidelityError,
    build_persisted_review_delivery_bundle,
)
from chess_mentor_engine.reviewed_coaching import M26_SCHEMA_VERSION
from chess_mentor_engine.reviewed_coaching_ledger import M27_SCHEMA_VERSION
from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    StorageError,
    load_tutor_session,
)
from chess_mentor_engine.storage.tutor import SESSION_KIND
from chess_mentor_engine.tutoring import TutorSession

M33_SCHEMA_VERSION = "m33.deterministic-mentor-feedback-trace.v1"
M33_CLAIM_SCOPE = "repository_local_deterministic_m16_provenance_trace"
M33_COMPONENT_SCOPE = "nonempty_lines_of_m16_section_content"

_TRACE_BOUNDARY = {
    "creates_objective_chess_facts": False,
    "creates_learner_hypotheses": False,
    "evaluates_model_semantics": False,
    "copies_m19_model_prose": False,
    "copies_m20_evaluator_judgments": False,
    "advances_tutor_state": False,
    "executes_external_calls": False,
}

_FEEDBACK_KEYS = {
    "schema_version",
    "tutor_session_id",
    "tutor_comparison_id",
    "tutor_comparison_fingerprint",
    "hypothesis_context_id",
    "hypothesis_context_fingerprint",
    "evaluation_presentation",
    "policy",
    "sections",
    "rendered_content",
    "created_at",
    "claim_scope",
    "feedback_id",
    "fingerprint",
}
_FEEDBACK_SECTION_KEYS = {
    "kind",
    "claim_scope",
    "content",
    "evidence_refs",
}
_FEEDBACK_CLAIM_SCOPES = {
    "objective": "qualified_objective_evidence",
    "reasoning": "position_local_m6_assessment",
    "learner_context": "descriptive_m7_hypothesis_context",
    "reflection": "session_local_reflection_prompt",
}
_TRACE_KEYS = {
    "schema_version",
    "participant_id",
    "claim_scope",
    "component_scope",
    "source_refs",
    "source_fingerprints",
    "sources",
    "section_order",
    "sections",
    "coverage",
    "authority_boundary",
    "trace_id",
    "fingerprint",
}
_SOURCE_REF_KINDS = {
    "m30_package": M30_SCHEMA_VERSION,
    "m26_run": M26_SCHEMA_VERSION,
    "m25_review": COACH_REVIEW_SCHEMA_VERSION,
    "m27_ledger": M27_SCHEMA_VERSION,
    "m16_feedback": FEEDBACK_SCHEMA_VERSION,
    "m8_session": SESSION_KIND,
}
_SOURCE_FINGERPRINT_KEYS = {
    "m32_delivery_fingerprint",
    "m25_read_model_fingerprint",
    "m16_feedback_fingerprint",
    "m15_evaluation_presentation_fingerprint",
    "m6_comparison_fingerprint",
    "m7_context_fingerprint",
}
_TRACE_SECTION_KEYS = {
    "kind",
    "claim_scope",
    "content_sha256",
    "evidence_refs_sha256",
    "component_count",
    "components",
}
_COMPONENT_KEYS = {
    "component_id",
    "ordinal",
    "content_sha256",
    "source_authority",
    "source_pointer",
    "source_fields",
}
_SECTION_AUTHORITIES = {
    "objective": "M15",
    "reasoning": "M6",
    "learner_context": "M7",
    "reflection": "M6",
}


class MentorFeedbackTraceError(ValueError):
    """M33 cannot preserve an exact deterministic feedback provenance trace."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _strict(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise MentorFeedbackTraceError(f"{label} shape mismatch")
    return value


def _nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise MentorFeedbackTraceError(f"{label} must be a non-empty string")
    return value


def _sha256(value: Any, label: str) -> str:
    value = _nonempty(value, label)
    if (
        len(value) != 64
        or value.lower() != value
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise MentorFeedbackTraceError(f"{label} must be a lowercase SHA-256")
    return value


def _feedback_payload(feedback: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in feedback.items()
        if key not in {"feedback_id", "fingerprint"}
    }


def _validate_feedback_binding(
    *,
    feedback: Any,
    presentation: Any,
    session: TutorSession,
) -> dict[str, Any]:
    feedback = _strict(feedback, _FEEDBACK_KEYS, "M16 feedback")
    if feedback["schema_version"] != FEEDBACK_SCHEMA_VERSION:
        raise MentorFeedbackTraceError("M16 feedback schema drifted")
    if feedback["claim_scope"] != "session_local_grounded_feedback":
        raise MentorFeedbackTraceError("M16 feedback claim scope drifted")

    try:
        _validate_tutor_comparison(session)
        _validate_hypothesis_context(session)
        _validate_chronology(session, feedback["created_at"])
    except GroundedFeedbackError as exc:
        raise MentorFeedbackTraceError(
            f"M16 source session failed deterministic validation: {exc}"
        ) from exc

    comparison = session.comparison
    if comparison is None:
        raise MentorFeedbackTraceError("M16 source session lacks an M6 comparison")
    if feedback["tutor_session_id"] != session.tutor_session_id:
        raise MentorFeedbackTraceError("M16 tutor-session identity drifted")
    if feedback["tutor_comparison_id"] != comparison.comparison_id:
        raise MentorFeedbackTraceError("M16/M6 comparison identity drifted")
    if feedback["tutor_comparison_fingerprint"] != comparison.fingerprint:
        raise MentorFeedbackTraceError("M16/M6 comparison fingerprint drifted")

    context = session.hypothesis_context
    expected_context_id = None if context is None else context.context_id
    expected_context_fingerprint = None if context is None else context.fingerprint
    if feedback["hypothesis_context_id"] != expected_context_id:
        raise MentorFeedbackTraceError("M16/M7 context identity drifted")
    if feedback["hypothesis_context_fingerprint"] != expected_context_fingerprint:
        raise MentorFeedbackTraceError("M16/M7 context fingerprint drifted")

    if type(presentation) is not dict:
        raise MentorFeedbackTraceError("M15 evaluation presentation is malformed")
    if presentation.get("schema_version") != PRESENTATION_SCHEMA_VERSION:
        raise MentorFeedbackTraceError("M15 evaluation presentation schema drifted")
    presentation_fingerprint = _fingerprint(presentation)
    evaluation_ref = _strict(
        feedback["evaluation_presentation"],
        {"schema_version", "fingerprint", "decision_comparison_id"},
        "M16 evaluation-presentation reference",
    )
    expected_evaluation_ref = {
        "schema_version": PRESENTATION_SCHEMA_VERSION,
        "fingerprint": presentation_fingerprint,
        "decision_comparison_id": evaluation_ref["decision_comparison_id"],
    }
    if evaluation_ref != expected_evaluation_ref:
        raise MentorFeedbackTraceError("M16/M15 evaluation fingerprint drifted")
    if evaluation_ref["decision_comparison_id"] != comparison.reasoning_context \
            .decision_comparison_ref.ref_id:
        raise MentorFeedbackTraceError("M16/M15 decision comparison identity drifted")

    expected_policy = _policy_payload()
    expected_policy["fingerprint"] = _fingerprint(expected_policy)
    if feedback["policy"] != expected_policy:
        raise MentorFeedbackTraceError("M16 deterministic policy drifted")

    refs = _section_refs(session)
    expected_content = {
        "objective": _objective_content(presentation),
        "reasoning": _reasoning_content(session),
        "reflection": _reflection_content(session),
    }
    learner_content = _learner_context_content(session)
    if learner_content is not None:
        expected_content["learner_context"] = learner_content
    expected_kinds = ["objective", "reasoning"]
    if learner_content is not None:
        expected_kinds.append("learner_context")
    expected_kinds.append("reflection")

    sections = feedback["sections"]
    if type(sections) is not list or len(sections) != len(expected_kinds):
        raise MentorFeedbackTraceError("M16 section set drifted")
    for index, expected_kind in enumerate(expected_kinds):
        section = _strict(
            sections[index],
            _FEEDBACK_SECTION_KEYS,
            f"M16 {expected_kind} section",
        )
        if section["kind"] != expected_kind:
            raise MentorFeedbackTraceError("M16 section ordering drifted")
        if section["claim_scope"] != _FEEDBACK_CLAIM_SCOPES[expected_kind]:
            raise MentorFeedbackTraceError(
                f"M16 {expected_kind} claim scope drifted"
            )
        if section["content"] != expected_content[expected_kind]:
            raise MentorFeedbackTraceError(
                f"M16 {expected_kind} deterministic content drifted"
            )
        if section["evidence_refs"] != refs[expected_kind]:
            raise MentorFeedbackTraceError(
                f"M16 {expected_kind} evidence references drifted"
            )

    rendered = "\n\n".join(
        f"{item['kind'].replace('_', ' ').title()}\n{item['content']}"
        for item in sections
    )
    if feedback["rendered_content"] != rendered:
        raise MentorFeedbackTraceError("M16 rendered content drifted")

    expected_fingerprint = _fingerprint(_feedback_payload(feedback))
    if feedback["fingerprint"] != expected_fingerprint:
        raise MentorFeedbackTraceError("M16 feedback fingerprint mismatch")
    if feedback["feedback_id"] != f"grounded_feedback_{expected_fingerprint[:20]}":
        raise MentorFeedbackTraceError("M16 feedback identity mismatch")
    return _copy(feedback)


def _source_ref(kind: str, ref_id: str, fingerprint: str) -> dict[str, str]:
    return {
        "kind": kind,
        "ref_id": ref_id,
        "fingerprint": fingerprint,
    }


def _sources(
    *,
    presentation: dict[str, Any],
    session: TutorSession,
    model_coaching_fingerprint: str | None,
    model_evaluation_fingerprint: str | None,
) -> dict[str, Any]:
    comparison = session.comparison
    assert comparison is not None
    context = session.hypothesis_context
    m7 = None
    if context is not None:
        m7 = {
            "context": _source_ref(
                "tutor_hypothesis_context",
                context.context_id,
                context.fingerprint,
            ),
            "revisions": [
                _source_ref(
                    "hypothesis_revision",
                    revision.revision_id,
                    revision.fingerprint,
                )
                for revision in context.active_revisions
            ],
        }
    return {
        "m15": {
            "evaluation_presentation": {
                "schema_version": presentation["schema_version"],
                "fingerprint": _fingerprint(presentation),
                "decision_comparison_id": (
                    comparison.reasoning_context.decision_comparison_ref.ref_id
                ),
            }
        },
        "m6": {
            "comparison": _source_ref(
                "tutor_comparison",
                comparison.comparison_id,
                comparison.fingerprint,
            ),
            "assessment": _source_ref(
                "reasoning_assessment",
                comparison.assessment.assessment_id,
                comparison.assessment.fingerprint,
            ),
            "assertions": [
                _source_ref(
                    "reasoning_assertion",
                    assertion.assertion_id,
                    assertion.fingerprint,
                )
                for assertion in comparison.assertions
            ],
        },
        "m7": m7,
        "m19": {
            "present": model_coaching_fingerprint is not None,
            "fingerprint": model_coaching_fingerprint,
        },
        "m20": {
            "present": model_evaluation_fingerprint is not None,
            "fingerprint": model_evaluation_fingerprint,
        },
    }


def _component(
    *,
    section_kind: str,
    ordinal: int,
    content: str,
    source_authority: str,
    source_pointer: str,
    source_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "component_id": f"{section_kind}.{ordinal}",
        "ordinal": ordinal,
        "content_sha256": _sha256_text(content),
        "source_authority": source_authority,
        "source_pointer": source_pointer,
        "source_fields": list(source_fields),
    }


def _components_for_section(
    *,
    section: dict[str, Any],
    session: TutorSession,
) -> list[dict[str, Any]]:
    kind = section["kind"]
    lines = section["content"].splitlines()
    if not lines or any(not line for line in lines):
        raise MentorFeedbackTraceError(
            f"M16 {kind} content must have non-empty trace components"
        )

    metadata: list[tuple[str, str, tuple[str, ...]]] = []
    comparison = session.comparison
    assert comparison is not None

    if kind == "objective":
        metadata = [
            (
                "M15",
                "/sources/m15/evaluation_presentation",
                (
                    "subject.played_move_uci",
                    "comparison.best_move_uci",
                    "comparison.evidence_quality",
                    "comparison.comparison_kind",
                    "comparison.preference",
                    "comparison.exact_centipawn_delta_for_mover",
                    "comparison.mate_relation",
                    "comparison.terminal_outcome",
                ),
            )
            for _ in lines
        ]
    elif kind == "reasoning":
        metadata.append(("M6", "/sources/m6/assessment", ("status",)))
        if comparison.assessment.measurement_condition != "clean":
            metadata.append(
                (
                    "M6",
                    "/sources/m6/assessment",
                    ("measurement_condition",),
                )
            )
        for index, _assertion in enumerate(comparison.assertions):
            metadata.append(
                (
                    "M6",
                    f"/sources/m6/assertions/{index}",
                    ("code", "statement"),
                )
            )
        if comparison.assessment.status_reasons:
            metadata.append(
                ("M6", "/sources/m6/assessment", ("status_reasons",))
            )
    elif kind == "learner_context":
        context = session.hypothesis_context
        if context is None:
            raise MentorFeedbackTraceError(
                "M16 learner-context section lacks M7 source context"
            )
        if not context.active_revisions:
            metadata.append(
                ("M7", "/sources/m7/context", ("active_revisions",))
            )
        else:
            metadata.append(
                ("M7", "/sources/m7/context", ("active_revisions",))
            )
            for index, revision in enumerate(context.active_revisions):
                pointer = f"/sources/m7/revisions/{index}"
                metadata.append(
                    ("M7", pointer, ("statement", "scope_definition"))
                )
                if revision.unresolved_alternative_notes:
                    metadata.append(
                        ("M7", pointer, ("unresolved_alternative_notes",))
                    )
                if revision.competing_hypothesis_refs:
                    metadata.append(
                        ("M7", pointer, ("competing_hypothesis_refs",))
                    )
    elif kind == "reflection":
        seen: set[str] = set()
        for index, assertion in enumerate(comparison.assertions):
            if assertion.code in seen:
                continue
            seen.add(assertion.code)
            if assertion.code in _REFLECTION_PROMPTS:
                metadata.append(
                    (
                        "M6",
                        f"/sources/m6/assertions/{index}",
                        ("code",),
                    )
                )
        if not metadata:
            metadata.append(("M6", "/sources/m6/assessment", ("status",)))
    else:
        raise MentorFeedbackTraceError(f"unsupported M16 section: {kind}")

    if len(lines) != len(metadata):
        raise MentorFeedbackTraceError(
            f"M16 {kind} trace component mapping is incomplete"
        )
    return [
        _component(
            section_kind=kind,
            ordinal=index,
            content=line,
            source_authority=authority,
            source_pointer=pointer,
            source_fields=fields,
        )
        for index, (line, (authority, pointer, fields)) in enumerate(
            zip(lines, metadata, strict=True)
        )
    ]


def _build_trace_record(
    *,
    participant_id: str,
    feedback: dict[str, Any],
    presentation: dict[str, Any],
    session: TutorSession,
    source_refs: dict[str, Any],
    m32_delivery_fingerprint: str,
    m25_read_model_fingerprint: str,
    model_coaching_fingerprint: str | None,
    model_evaluation_fingerprint: str | None,
) -> dict[str, Any]:
    feedback = _validate_feedback_binding(
        feedback=feedback,
        presentation=presentation,
        session=session,
    )
    sections: list[dict[str, Any]] = []
    for section in feedback["sections"]:
        components = _components_for_section(section=section, session=session)
        sections.append(
            {
                "kind": section["kind"],
                "claim_scope": section["claim_scope"],
                "content_sha256": _sha256_text(section["content"]),
                "evidence_refs_sha256": _fingerprint(section["evidence_refs"]),
                "component_count": len(components),
                "components": components,
            }
        )

    context = session.hypothesis_context
    sources = _sources(
        presentation=presentation,
        session=session,
        model_coaching_fingerprint=model_coaching_fingerprint,
        model_evaluation_fingerprint=model_evaluation_fingerprint,
    )
    component_count = sum(item["component_count"] for item in sections)
    payload = {
        "schema_version": M33_SCHEMA_VERSION,
        "participant_id": participant_id,
        "claim_scope": M33_CLAIM_SCOPE,
        "component_scope": M33_COMPONENT_SCOPE,
        "source_refs": _copy(source_refs),
        "source_fingerprints": {
            "m32_delivery_fingerprint": m32_delivery_fingerprint,
            "m25_read_model_fingerprint": m25_read_model_fingerprint,
            "m16_feedback_fingerprint": feedback["fingerprint"],
            "m15_evaluation_presentation_fingerprint": _fingerprint(presentation),
            "m6_comparison_fingerprint": session.comparison.fingerprint,
            "m7_context_fingerprint": (
                None if context is None else context.fingerprint
            ),
        },
        "sources": sources,
        "section_order": [item["kind"] for item in sections],
        "sections": sections,
        "coverage": {
            "definition": M33_COMPONENT_SCOPE,
            "section_count": len(sections),
            "component_count": component_count,
            "all_components_traced": True,
        },
        "authority_boundary": dict(_TRACE_BOUNDARY),
    }
    fingerprint = _fingerprint(payload)
    return {
        **payload,
        "trace_id": f"mentor_feedback_trace_{fingerprint[:20]}",
        "fingerprint": fingerprint,
    }


def _pointer_authorities(sources: dict[str, Any]) -> dict[str, str]:
    pointers = {
        "/sources/m15/evaluation_presentation": "M15",
        "/sources/m6/assessment": "M6",
    }
    assertions = sources["m6"]["assertions"]
    for index in range(len(assertions)):
        pointers[f"/sources/m6/assertions/{index}"] = "M6"
    if sources["m7"] is not None:
        pointers["/sources/m7/context"] = "M7"
        for index in range(len(sources["m7"]["revisions"])):
            pointers[f"/sources/m7/revisions/{index}"] = "M7"
    return pointers


def _validate_source_ref(value: Any, label: str) -> dict[str, str]:
    value = _strict(value, {"kind", "ref_id", "fingerprint"}, label)
    _nonempty(value["kind"], f"{label} kind")
    _nonempty(value["ref_id"], f"{label} ref_id")
    _sha256(value["fingerprint"], f"{label} fingerprint")
    return value


def _validate_sources(value: Any) -> dict[str, Any]:
    sources = _strict(value, {"m15", "m6", "m7", "m19", "m20"}, "M33 sources")
    m15 = _strict(sources["m15"], {"evaluation_presentation"}, "M33 M15 source")
    presentation = _strict(
        m15["evaluation_presentation"],
        {"schema_version", "fingerprint", "decision_comparison_id"},
        "M33 M15 presentation source",
    )
    if presentation["schema_version"] != PRESENTATION_SCHEMA_VERSION:
        raise MentorFeedbackTraceError("M33 M15 source schema drifted")
    _sha256(presentation["fingerprint"], "M33 M15 source fingerprint")
    _nonempty(
        presentation["decision_comparison_id"],
        "M33 M15 decision comparison",
    )

    m6 = _strict(
        sources["m6"],
        {"comparison", "assessment", "assertions"},
        "M33 M6 sources",
    )
    _validate_source_ref(m6["comparison"], "M33 M6 comparison")
    _validate_source_ref(m6["assessment"], "M33 M6 assessment")
    if type(m6["assertions"]) is not list:
        raise MentorFeedbackTraceError("M33 M6 assertions must be an array")
    for index, assertion in enumerate(m6["assertions"]):
        _validate_source_ref(assertion, f"M33 M6 assertion {index}")

    m7 = sources["m7"]
    if m7 is not None:
        m7 = _strict(m7, {"context", "revisions"}, "M33 M7 sources")
        _validate_source_ref(m7["context"], "M33 M7 context")
        if type(m7["revisions"]) is not list:
            raise MentorFeedbackTraceError("M33 M7 revisions must be an array")
        for index, revision in enumerate(m7["revisions"]):
            _validate_source_ref(revision, f"M33 M7 revision {index}")

    for authority in ("m19", "m20"):
        source = _strict(
            sources[authority],
            {"present", "fingerprint"},
            f"M33 {authority.upper()} source",
        )
        if type(source["present"]) is not bool:
            raise MentorFeedbackTraceError(
                f"M33 {authority.upper()} presence must be boolean"
            )
        if source["present"] is not (source["fingerprint"] is not None):
            raise MentorFeedbackTraceError(
                f"M33 {authority.upper()} presence/fingerprint drifted"
            )
        if source["fingerprint"] is not None:
            _sha256(
                source["fingerprint"],
                f"M33 {authority.upper()} fingerprint",
            )
    return sources


def validate_mentor_feedback_trace_surface(value: Any) -> dict[str, Any]:
    """Validate one detached M33 trace without promoting source authority."""
    trace = _strict(value, _TRACE_KEYS, "M33 trace")
    if trace["schema_version"] != M33_SCHEMA_VERSION:
        raise MentorFeedbackTraceError("M33 schema drifted")
    participant_id = _nonempty(trace["participant_id"], "M33 participant_id")
    if trace["claim_scope"] != M33_CLAIM_SCOPE:
        raise MentorFeedbackTraceError("M33 claim scope drifted")
    if trace["component_scope"] != M33_COMPONENT_SCOPE:
        raise MentorFeedbackTraceError("M33 component scope drifted")
    if trace["authority_boundary"] != _TRACE_BOUNDARY:
        raise MentorFeedbackTraceError("M33 authority boundary drifted")

    refs = trace["source_refs"]
    if type(refs) is not dict or set(refs) != set(_SOURCE_REF_KINDS):
        raise MentorFeedbackTraceError("M33 source-reference set drifted")
    parsed_refs: dict[str, ArtifactRef] = {}
    for key, expected_kind in _SOURCE_REF_KINDS.items():
        ref_value = refs[key]
        if type(ref_value) is not dict:
            raise MentorFeedbackTraceError(f"M33 {key} reference is malformed")
        try:
            ref = ArtifactRef(**ref_value)
        except (TypeError, ValueError, StorageError) as exc:
            raise MentorFeedbackTraceError(
                f"M33 {key} reference is invalid"
            ) from exc
        if ref.kind != expected_kind:
            raise MentorFeedbackTraceError(f"M33 {key} reference kind drifted")
        if ref.participant_id != participant_id:
            raise MentorFeedbackTraceError(
                f"M33 {key} participant scope drifted"
            )
        parsed_refs[key] = ref

    fingerprints = trace["source_fingerprints"]
    if (
        type(fingerprints) is not dict
        or set(fingerprints) != _SOURCE_FINGERPRINT_KEYS
    ):
        raise MentorFeedbackTraceError("M33 source-fingerprint set drifted")
    for key in _SOURCE_FINGERPRINT_KEYS - {"m7_context_fingerprint"}:
        _sha256(fingerprints[key], f"M33 {key}")
    if fingerprints["m7_context_fingerprint"] is not None:
        _sha256(
            fingerprints["m7_context_fingerprint"],
            "M33 m7_context_fingerprint",
        )

    sources = _validate_sources(trace["sources"])
    if (
        sources["m15"]["evaluation_presentation"]["fingerprint"]
        != fingerprints["m15_evaluation_presentation_fingerprint"]
    ):
        raise MentorFeedbackTraceError("M33 M15 source fingerprint drifted")
    if (
        sources["m6"]["comparison"]["fingerprint"]
        != fingerprints["m6_comparison_fingerprint"]
    ):
        raise MentorFeedbackTraceError("M33 M6 comparison fingerprint drifted")
    m7 = sources["m7"]
    expected_m7_fingerprint = (
        None if m7 is None else m7["context"]["fingerprint"]
    )
    if expected_m7_fingerprint != fingerprints["m7_context_fingerprint"]:
        raise MentorFeedbackTraceError("M33 M7 context fingerprint drifted")

    sections = trace["sections"]
    section_order = trace["section_order"]
    if type(sections) is not list or type(section_order) is not list:
        raise MentorFeedbackTraceError("M33 sections must be arrays")
    expected_order = ["objective", "reasoning"]
    if sources["m7"] is not None:
        expected_order.append("learner_context")
    expected_order.append("reflection")
    if section_order != expected_order:
        raise MentorFeedbackTraceError("M33 section ordering drifted")
    if len(sections) != len(expected_order):
        raise MentorFeedbackTraceError("M33 section count drifted")

    pointers = _pointer_authorities(sources)
    total_components = 0
    for section_index, expected_kind in enumerate(expected_order):
        section = _strict(
            sections[section_index],
            _TRACE_SECTION_KEYS,
            f"M33 {expected_kind} trace section",
        )
        if section["kind"] != expected_kind:
            raise MentorFeedbackTraceError("M33 trace section order drifted")
        if section["claim_scope"] != _FEEDBACK_CLAIM_SCOPES[expected_kind]:
            raise MentorFeedbackTraceError(
                f"M33 {expected_kind} claim scope drifted"
            )
        _sha256(section["content_sha256"], "M33 section content hash")
        _sha256(
            section["evidence_refs_sha256"],
            "M33 section evidence-reference hash",
        )
        components = section["components"]
        if type(components) is not list or not components:
            raise MentorFeedbackTraceError(
                f"M33 {expected_kind} components must be non-empty"
            )
        if section["component_count"] != len(components):
            raise MentorFeedbackTraceError(
                f"M33 {expected_kind} component count drifted"
            )
        expected_authority = _SECTION_AUTHORITIES[expected_kind]
        for ordinal, component in enumerate(components):
            component = _strict(
                component,
                _COMPONENT_KEYS,
                f"M33 {expected_kind} component {ordinal}",
            )
            if component["component_id"] != f"{expected_kind}.{ordinal}":
                raise MentorFeedbackTraceError("M33 component identity drifted")
            if component["ordinal"] != ordinal:
                raise MentorFeedbackTraceError("M33 component ordinal drifted")
            _sha256(component["content_sha256"], "M33 component content hash")
            if component["source_authority"] != expected_authority:
                raise MentorFeedbackTraceError(
                    f"M33 {expected_kind} source authority drifted"
                )
            pointer = component["source_pointer"]
            if pointers.get(pointer) != expected_authority:
                raise MentorFeedbackTraceError(
                    f"M33 {expected_kind} source pointer drifted"
                )
            fields = component["source_fields"]
            if (
                type(fields) is not list
                or not fields
                or any(type(field) is not str or not field for field in fields)
            ):
                raise MentorFeedbackTraceError(
                    f"M33 {expected_kind} source fields drifted"
                )
        total_components += len(components)

    coverage = _strict(
        trace["coverage"],
        {
            "definition",
            "section_count",
            "component_count",
            "all_components_traced",
        },
        "M33 coverage",
    )
    expected_coverage = {
        "definition": M33_COMPONENT_SCOPE,
        "section_count": len(sections),
        "component_count": total_components,
        "all_components_traced": True,
    }
    if coverage != expected_coverage:
        raise MentorFeedbackTraceError("M33 trace coverage drifted")

    payload = {
        key: item
        for key, item in trace.items()
        if key not in {"trace_id", "fingerprint"}
    }
    expected_fingerprint = _fingerprint(payload)
    if trace["fingerprint"] != expected_fingerprint:
        raise MentorFeedbackTraceError("M33 trace fingerprint mismatch")
    if trace["trace_id"] != f"mentor_feedback_trace_{expected_fingerprint[:20]}":
        raise MentorFeedbackTraceError("M33 trace identity mismatch")
    return _copy(trace)


def _one_dependency(
    dependencies: tuple[ArtifactRef, ...],
    *,
    kind: str,
    label: str,
) -> ArtifactRef:
    matches = tuple(ref for ref in dependencies if ref.kind == kind)
    if len(matches) != 1:
        raise MentorFeedbackTraceError(
            f"{label} must resolve exactly one {kind} dependency"
        )
    return matches[0]


def _record_ref(record: dict[str, Any], id_key: str) -> dict[str, Any]:
    return {
        "schema_version": record["schema_version"],
        id_key: record[id_key],
        "fingerprint": record["fingerprint"],
    }


def build_persisted_mentor_feedback_trace_surface(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    package_artifact_id: str,
) -> dict[str, Any]:
    """Build M33 from one exact validated M30/M32 persisted review package."""
    _nonempty(participant_id, "participant_id")
    _nonempty(package_artifact_id, "package_artifact_id")
    try:
        delivery = build_persisted_review_delivery_bundle(
            store=store,
            participant_id=participant_id,
            package_artifact_id=package_artifact_id,
        )
    except ReviewDeliveryFidelityError as exc:
        raise MentorFeedbackTraceError(
            f"M32 delivery validation failed: {exc}"
        ) from exc

    try:
        run_ref = ArtifactRef(**delivery["source_refs"]["m26_run"])
        review_ref = ArtifactRef(**delivery["source_refs"]["m25_review"])
        run_artifact = store.get(run_ref, participant_id=participant_id)
        review_artifact = store.get(review_ref, participant_id=participant_id)
        feedback_ref = _one_dependency(
            review_artifact.dependencies,
            kind=FEEDBACK_SCHEMA_VERSION,
            label="M25 review",
        )
        feedback_artifact = store.get(
            feedback_ref,
            participant_id=participant_id,
        )
        run = run_artifact.payload
        source_session_ref = ArtifactRef(**run["source_session_ref"])
        recovered = load_tutor_session(
            store,
            source_session_ref,
            participant_id=participant_id,
        )
    except (KeyError, TypeError, ValueError, StorageError) as exc:
        if isinstance(exc, MentorFeedbackTraceError):
            raise
        raise MentorFeedbackTraceError(
            f"persisted M33 source resolution failed: {exc}"
        ) from exc

    if source_session_ref not in run_artifact.dependencies:
        raise MentorFeedbackTraceError("M26 source-session dependency drifted")
    feedback = feedback_artifact.payload
    exact_feedback = delivery["delivery"]["sections"]["deterministic_grounding"]
    if not exact_feedback["present"] or feedback != exact_feedback["content"]:
        raise MentorFeedbackTraceError("M25/M16 deterministic grounding drifted")
    if run.get("grounded_feedback_ref") != _record_ref(feedback, "feedback_id"):
        raise MentorFeedbackTraceError("M26/M16 feedback reference drifted")

    presentation = delivery["delivery"]["sections"]["objective_evidence"]["content"]
    m25_fingerprints = delivery["source_fingerprints"][
        "m25_source_fingerprints"
    ]
    source_refs = {
        "m30_package": delivery["source_refs"]["m30_package"],
        "m26_run": delivery["source_refs"]["m26_run"],
        "m25_review": delivery["source_refs"]["m25_review"],
        "m27_ledger": delivery["source_refs"]["m27_ledger"],
        "m16_feedback": feedback_ref.to_dict(),
        "m8_session": source_session_ref.to_dict(),
    }
    trace = _build_trace_record(
        participant_id=participant_id,
        feedback=feedback,
        presentation=presentation,
        session=recovered.session,
        source_refs=source_refs,
        m32_delivery_fingerprint=delivery["fingerprint"],
        m25_read_model_fingerprint=delivery["source_fingerprints"][
            "m25_read_model_fingerprint"
        ],
        model_coaching_fingerprint=m25_fingerprints["model_coaching"],
        model_evaluation_fingerprint=m25_fingerprints["model_evaluation"],
    )
    return validate_mentor_feedback_trace_surface(trace)


def validate_persisted_mentor_feedback_trace_surface(
    *,
    store: LocalArtifactStore,
    participant_id: str,
    trace: Any,
) -> dict[str, Any]:
    """Rebuild M33 from its exact M30 source and require byte-semantic equality."""
    validated = validate_mentor_feedback_trace_surface(trace)
    if validated["participant_id"] != participant_id:
        raise MentorFeedbackTraceError(
            "M33 requested participant does not match trace"
        )
    package_ref = ArtifactRef(**validated["source_refs"]["m30_package"])
    rebuilt = build_persisted_mentor_feedback_trace_surface(
        store=store,
        participant_id=participant_id,
        package_artifact_id=package_ref.artifact_id,
    )
    if rebuilt != validated:
        raise MentorFeedbackTraceError(
            "M33 trace drifted from persisted M30/M32/M16/M8 sources"
        )
    return validated
