"""M7B immutable hypothesis/evidence ledger with strict M6 provenance binding."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from chess_mentor_engine.chess import canonical_json

from .assessment_model import (
    ReasoningArtifactRef,
    ReasoningDiscrepancyAssertion,
    ReasoningDiscrepancyAssessment,
)
from .hypothesis_model import (
    HypothesisActorProvenance,
    HypothesisContextRef,
    HypothesisEvidenceBasisKind,
    HypothesisEvidenceLink,
    HypothesisEvidenceRelation,
    HypothesisLifecycleEvent,
    HypothesisLifecycleKind,
    HypothesisM6EvidenceRef,
    HypothesisMappingProvenance,
    HypothesisRevision,
    HypothesisRevisionRef,
    LearnerHypothesis,
    LearnerHypothesisRef,
)
from .model import ReasoningDiscrepancyContext

_RELATIONS = frozenset(
    {
        "supports",
        "contradicts",
        "successful_counterexample",
        "context_exception",
        "unclear",
    }
)
_BASIS_KINDS = frozenset({"deterministic_mapping", "coded_mapping"})
_LIFECYCLE_KINDS = frozenset({"retired", "superseded"})


class LearnerHypothesisError(ValueError):
    """Raised when M7B identity, provenance, or append-only invariants fail."""


def _fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    if not value:
        raise LearnerHypothesisError("timestamp must not be empty")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LearnerHypothesisError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LearnerHypothesisError(
            "timestamp must include an explicit timezone"
        )
    return parsed


def _require_nonempty(name: str, value: str) -> None:
    if not value:
        raise LearnerHypothesisError(f"{name} must not be empty")


def _normalize_notes(values: tuple[str, ...]) -> tuple[str, ...]:
    if any(not value for value in values):
        raise LearnerHypothesisError(
            "unresolved alternative notes must not contain empty values"
        )
    if len(set(values)) != len(values):
        raise LearnerHypothesisError(
            "unresolved alternative notes must be unique"
        )
    return tuple(sorted(values))


def _normalize_context_refs(
    values: tuple[HypothesisContextRef, ...],
) -> tuple[HypothesisContextRef, ...]:
    ids = tuple(item.ref_id for item in values)
    if len(set(ids)) != len(ids):
        raise LearnerHypothesisError("context definition refs must be unique")
    return tuple(sorted(values, key=lambda item: (item.ref_id, item.fingerprint)))


def _normalize_hypothesis_refs(
    participant_id: str,
    values: tuple[LearnerHypothesisRef, ...],
    *,
    current_hypothesis_id: str | None = None,
) -> tuple[LearnerHypothesisRef, ...]:
    ids = tuple(item.hypothesis_id for item in values)
    if len(set(ids)) != len(ids):
        raise LearnerHypothesisError("competing hypothesis refs must be unique")
    for item in values:
        if item.participant_id != participant_id:
            raise LearnerHypothesisError(
                "competing hypotheses must belong to the same participant"
            )
        if (
            current_hypothesis_id is not None
            and item.hypothesis_id == current_hypothesis_id
        ):
            raise LearnerHypothesisError(
                "a hypothesis cannot cite itself as a competing hypothesis"
            )
    return tuple(
        sorted(values, key=lambda item: (item.hypothesis_id, item.fingerprint))
    )


def _hypothesis_ref(hypothesis: LearnerHypothesis) -> LearnerHypothesisRef:
    return LearnerHypothesisRef(
        hypothesis_id=hypothesis.hypothesis_id,
        participant_id=hypothesis.participant_id,
        fingerprint=hypothesis.fingerprint,
    )


def _revision_ref(revision: HypothesisRevision) -> HypothesisRevisionRef:
    return HypothesisRevisionRef(
        revision_id=revision.revision_id,
        hypothesis_id=revision.hypothesis_id,
        revision_number=revision.revision_number,
        fingerprint=revision.fingerprint,
    )


def _context_ref(context: ReasoningDiscrepancyContext) -> HypothesisM6EvidenceRef:
    return HypothesisM6EvidenceRef(
        kind="reasoning_context",
        ref_id=context.reasoning_context_id,
        fingerprint=context.context_fingerprint,
    )


def _assessment_ref(
    assessment: ReasoningDiscrepancyAssessment,
) -> HypothesisM6EvidenceRef:
    return HypothesisM6EvidenceRef(
        kind="reasoning_assessment",
        ref_id=assessment.assessment_id,
        fingerprint=assessment.fingerprint,
    )


def _assertion_ref(
    assertion: ReasoningDiscrepancyAssertion,
) -> HypothesisM6EvidenceRef:
    return HypothesisM6EvidenceRef(
        kind="reasoning_assertion",
        ref_id=assertion.assertion_id,
        fingerprint=assertion.fingerprint,
    )


def _proposal_payload(
    *,
    participant_id: str,
    statement: str,
    scope_definition: str,
    context_definition_refs: tuple[HypothesisContextRef, ...],
    competing_hypothesis_refs: tuple[LearnerHypothesisRef, ...],
    unresolved_alternative_notes: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "participant_id": participant_id,
        "statement": statement,
        "claim_kind": "descriptive_pattern",
        "scope_definition": scope_definition,
        "context_definition_refs": [
            item.to_dict() for item in context_definition_refs
        ],
        "competing_hypothesis_refs": [
            item.to_dict() for item in competing_hypothesis_refs
        ],
        "unresolved_alternative_notes": list(unresolved_alternative_notes),
    }


def _revision_proposal_fingerprint(
    participant_id: str,
    revision: HypothesisRevision,
) -> str:
    return _fingerprint(
        _proposal_payload(
            participant_id=participant_id,
            statement=revision.statement,
            scope_definition=revision.scope_definition,
            context_definition_refs=revision.context_definition_refs,
            competing_hypothesis_refs=revision.competing_hypothesis_refs,
            unresolved_alternative_notes=revision.unresolved_alternative_notes,
        )
    )


def _validate_hypothesis(hypothesis: LearnerHypothesis) -> None:
    expected = _fingerprint(hypothesis.to_dict(include_identity=False))
    if expected != hypothesis.fingerprint:
        raise LearnerHypothesisError("LearnerHypothesis fingerprint mismatch")
    if hypothesis.hypothesis_id != f"learner_hypothesis_{expected[:20]}":
        raise LearnerHypothesisError("LearnerHypothesis identity mismatch")
    _parse_timestamp(hypothesis.created_at)


def _validate_revision(revision: HypothesisRevision) -> None:
    if revision.claim_kind != "descriptive_pattern":
        raise LearnerHypothesisError(
            "M7B supports only descriptive_pattern hypothesis revisions"
        )
    expected = _fingerprint(revision.to_dict(include_identity=False))
    if expected != revision.fingerprint:
        raise LearnerHypothesisError("HypothesisRevision fingerprint mismatch")
    if revision.revision_id != f"hypothesis_revision_{expected[:20]}":
        raise LearnerHypothesisError("HypothesisRevision identity mismatch")
    _parse_timestamp(revision.created_at)


def _validate_revision_chain(
    hypothesis: LearnerHypothesis,
    revisions: tuple[HypothesisRevision, ...],
) -> tuple[HypothesisRevision, ...]:
    _validate_hypothesis(hypothesis)
    if not revisions:
        raise LearnerHypothesisError(
            "hypothesis revision history must include revision 1"
        )
    numbers = tuple(item.revision_number for item in revisions)
    if len(set(numbers)) != len(numbers):
        raise LearnerHypothesisError("hypothesis revision numbers must be unique")
    ordered = tuple(sorted(revisions, key=lambda item: item.revision_number))
    expected_numbers = tuple(range(1, len(ordered) + 1))
    if tuple(item.revision_number for item in ordered) != expected_numbers:
        raise LearnerHypothesisError(
            "hypothesis revision numbers must form a contiguous sequence"
        )
    previous: HypothesisRevision | None = None
    hypothesis_created = _parse_timestamp(hypothesis.created_at)
    for revision in ordered:
        _validate_revision(revision)
        if revision.hypothesis_id != hypothesis.hypothesis_id:
            raise LearnerHypothesisError(
                "hypothesis revision belongs to a different lineage"
            )
        revision_created = _parse_timestamp(revision.created_at)
        if revision_created < hypothesis_created:
            raise LearnerHypothesisError(
                "hypothesis revision cannot predate its lineage"
            )
        if previous is None:
            if revision.parent_revision_ref is not None:
                raise LearnerHypothesisError("revision 1 must not have a parent")
            proposal = _revision_proposal_fingerprint(
                hypothesis.participant_id,
                revision,
            )
            if proposal != hypothesis.origin_proposal_fingerprint:
                raise LearnerHypothesisError(
                    "revision 1 does not match the hypothesis origin proposal"
                )
        else:
            if revision.parent_revision_ref != _revision_ref(previous):
                raise LearnerHypothesisError(
                    "hypothesis revision parent does not match exact prior revision"
                )
            if revision_created < _parse_timestamp(previous.created_at):
                raise LearnerHypothesisError(
                    "hypothesis revision history must be chronological"
                )
        previous = revision
    return ordered


def _validate_link_revision_membership(
    hypothesis: LearnerHypothesis,
    revision: HypothesisRevision,
    revision_history: tuple[HypothesisRevision, ...] | None,
) -> None:
    history = (revision,) if revision_history is None else revision_history
    ordered = _validate_revision_chain(hypothesis, history)
    exact = [
        item
        for item in ordered
        if item.revision_id == revision.revision_id
        and item.fingerprint == revision.fingerprint
    ]
    if len(exact) != 1:
        raise LearnerHypothesisError(
            "evidence link revision is not in the exact hypothesis history"
        )
    if revision.revision_number > 1 and revision_history is None:
        raise LearnerHypothesisError(
            "later evidence-link revisions require exact revision history"
        )


def _validate_lifecycle_event(
    hypothesis: LearnerHypothesis,
    event: HypothesisLifecycleEvent,
) -> None:
    expected = _fingerprint(event.to_dict(include_identity=False))
    if expected != event.fingerprint:
        raise LearnerHypothesisError("HypothesisLifecycleEvent fingerprint mismatch")
    if event.lifecycle_event_id != f"hypothesis_lifecycle_{expected[:20]}":
        raise LearnerHypothesisError("HypothesisLifecycleEvent identity mismatch")
    if event.hypothesis_ref != _hypothesis_ref(hypothesis):
        raise LearnerHypothesisError(
            "lifecycle event does not cite the exact hypothesis lineage"
        )
    if event.kind not in _LIFECYCLE_KINDS:
        raise LearnerHypothesisError("unsupported hypothesis lifecycle event kind")
    if _parse_timestamp(event.created_at) < _parse_timestamp(hypothesis.created_at):
        raise LearnerHypothesisError("lifecycle event cannot predate hypothesis")
    if event.kind == "retired" and event.superseding_hypothesis_ref is not None:
        raise LearnerHypothesisError(
            "retired lifecycle event must not cite a superseding hypothesis"
        )
    if event.kind == "superseded":
        replacement = event.superseding_hypothesis_ref
        if replacement is None:
            raise LearnerHypothesisError(
                "superseded lifecycle event must cite replacement hypothesis"
            )
        if replacement.participant_id != hypothesis.participant_id:
            raise LearnerHypothesisError(
                "superseding hypothesis must belong to the same participant"
            )
        if replacement.hypothesis_id == hypothesis.hypothesis_id:
            raise LearnerHypothesisError("a hypothesis cannot supersede itself")


def _validate_reasoning_context(context: ReasoningDiscrepancyContext) -> None:
    expected = _fingerprint(context.to_dict(include_identity=False))
    if expected != context.context_fingerprint:
        raise LearnerHypothesisError(
            "ReasoningDiscrepancyContext fingerprint mismatch"
        )
    if context.reasoning_context_id != f"reasoning_context_{expected[:20]}":
        raise LearnerHypothesisError("ReasoningDiscrepancyContext identity mismatch")
    _parse_timestamp(context.created_at)


def _validate_assessment(
    context: ReasoningDiscrepancyContext,
    assessment: ReasoningDiscrepancyAssessment,
) -> None:
    expected = _fingerprint(assessment.to_dict(include_identity=False))
    if expected != assessment.fingerprint:
        raise LearnerHypothesisError(
            "ReasoningDiscrepancyAssessment fingerprint mismatch"
        )
    if assessment.assessment_id != f"reasoning_assessment_{expected[:20]}":
        raise LearnerHypothesisError(
            "ReasoningDiscrepancyAssessment identity mismatch"
        )
    if assessment.reasoning_context_id != context.reasoning_context_id:
        raise LearnerHypothesisError(
            "M6 assessment belongs to a different reasoning context"
        )
    if assessment.measurement_condition != context.measurement_condition:
        raise LearnerHypothesisError(
            "M6 assessment measurement condition does not match context"
        )
    if not set(assessment.assessed_stage_ids).issubset(
        set(context.assessment_stage_ids)
    ):
        raise LearnerHypothesisError(
            "M6 assessment cites stages outside its reasoning context"
        )
    _parse_timestamp(assessment.created_at)


def _artifact_key(ref: ReasoningArtifactRef) -> tuple[str, str, str]:
    return (ref.kind, ref.ref_id, ref.fingerprint)


def _validate_assertion(
    context: ReasoningDiscrepancyContext,
    assessment: ReasoningDiscrepancyAssessment,
    assertion: ReasoningDiscrepancyAssertion,
) -> None:
    expected = _fingerprint(assertion.to_dict(include_identity=False))
    if expected != assertion.fingerprint:
        raise LearnerHypothesisError(
            "ReasoningDiscrepancyAssertion fingerprint mismatch"
        )
    if assertion.assertion_id != f"reasoning_assertion_{expected[:20]}":
        raise LearnerHypothesisError(
            "ReasoningDiscrepancyAssertion identity mismatch"
        )
    if assertion.reasoning_context_id != context.reasoning_context_id:
        raise LearnerHypothesisError(
            "M6 assertion belongs to a different reasoning context"
        )
    if assertion.assessment_policy_ref != assessment.assessment_policy_ref:
        raise LearnerHypothesisError(
            "M6 assertion policy does not match assessment policy"
        )
    if not set(assertion.stage_ids).issubset(set(assessment.assessed_stage_ids)):
        raise LearnerHypothesisError(
            "M6 assertion cites stages outside the assessment"
        )
    assessment_assertions = {
        _artifact_key(item) for item in assessment.assertion_refs
    }
    assertion_key = (
        "discrepancy_assertion",
        assertion.assertion_id,
        assertion.fingerprint,
    )
    if assertion_key not in assessment_assertions:
        raise LearnerHypothesisError(
            "M6 assertion is not cited by the supplied assessment"
        )
    assessment_facts = {_artifact_key(item) for item in assessment.fact_refs}
    assessment_codings = {_artifact_key(item) for item in assessment.coding_refs}
    assessment_contradictions = {
        _artifact_key(item) for item in assessment.contradictory_evidence_refs
    }
    assertion_facts = {
        _artifact_key(item) for item in assertion.supporting_fact_refs
    }
    assertion_codings = {
        _artifact_key(item) for item in assertion.supporting_coding_refs
    }
    assertion_contradictions = {
        _artifact_key(item) for item in assertion.contradictory_evidence_refs
    }
    if not assertion_facts.issubset(assessment_facts):
        raise LearnerHypothesisError(
            "M6 assertion fact provenance is not preserved by assessment"
        )
    if not assertion_codings.issubset(assessment_codings):
        raise LearnerHypothesisError(
            "M6 assertion coding provenance is not preserved by assessment"
        )
    if not assertion_contradictions.issubset(assessment_contradictions):
        raise LearnerHypothesisError(
            "M6 assertion contradiction provenance is not preserved by assessment"
        )


def create_learner_hypothesis(
    *,
    participant_id: str,
    statement: str,
    scope_definition: str,
    origin_provenance: HypothesisActorProvenance,
    created_at: str,
    context_definition_refs: tuple[HypothesisContextRef, ...] = (),
    competing_hypothesis_refs: tuple[LearnerHypothesisRef, ...] = (),
    unresolved_alternative_notes: tuple[str, ...] = (),
) -> tuple[LearnerHypothesis, HypothesisRevision]:
    """Create one stable hypothesis lineage and revision 1 atomically."""

    _require_nonempty("participant_id", participant_id)
    _require_nonempty("statement", statement)
    _require_nonempty("scope_definition", scope_definition)
    _parse_timestamp(created_at)
    contexts = _normalize_context_refs(context_definition_refs)
    competing = _normalize_hypothesis_refs(
        participant_id,
        competing_hypothesis_refs,
    )
    notes = _normalize_notes(unresolved_alternative_notes)
    proposal = _proposal_payload(
        participant_id=participant_id,
        statement=statement,
        scope_definition=scope_definition,
        context_definition_refs=contexts,
        competing_hypothesis_refs=competing,
        unresolved_alternative_notes=notes,
    )
    proposal_fingerprint = _fingerprint(proposal)
    hypothesis_payload = {
        "participant_id": participant_id,
        "origin_proposal_fingerprint": proposal_fingerprint,
        "created_at": created_at,
        "origin_provenance": origin_provenance.to_dict(),
    }
    hypothesis_fingerprint = _fingerprint(hypothesis_payload)
    hypothesis = LearnerHypothesis(
        hypothesis_id=f"learner_hypothesis_{hypothesis_fingerprint[:20]}",
        fingerprint=hypothesis_fingerprint,
        participant_id=participant_id,
        origin_proposal_fingerprint=proposal_fingerprint,
        created_at=created_at,
        origin_provenance=origin_provenance,
    )
    revision_payload = {
        "hypothesis_id": hypothesis.hypothesis_id,
        "revision_number": 1,
        "statement": statement,
        "claim_kind": "descriptive_pattern",
        "scope_definition": scope_definition,
        "context_definition_refs": [item.to_dict() for item in contexts],
        "competing_hypothesis_refs": [item.to_dict() for item in competing],
        "unresolved_alternative_notes": list(notes),
        "parent_revision_ref": None,
        "revision_reason": "initial_proposal",
        "author_provenance": origin_provenance.to_dict(),
        "created_at": created_at,
    }
    revision_fingerprint = _fingerprint(revision_payload)
    revision = HypothesisRevision(
        revision_id=f"hypothesis_revision_{revision_fingerprint[:20]}",
        fingerprint=revision_fingerprint,
        hypothesis_id=hypothesis.hypothesis_id,
        revision_number=1,
        statement=statement,
        scope_definition=scope_definition,
        context_definition_refs=contexts,
        competing_hypothesis_refs=competing,
        unresolved_alternative_notes=notes,
        parent_revision_ref=None,
        revision_reason="initial_proposal",
        author_provenance=origin_provenance,
        created_at=created_at,
    )
    _validate_revision_chain(hypothesis, (revision,))
    return hypothesis, revision


def record_hypothesis_revision(
    *,
    hypothesis: LearnerHypothesis,
    existing_revisions: tuple[HypothesisRevision, ...],
    statement: str,
    scope_definition: str,
    revision_reason: str,
    author_provenance: HypothesisActorProvenance,
    created_at: str,
    context_definition_refs: tuple[HypothesisContextRef, ...] = (),
    competing_hypothesis_refs: tuple[LearnerHypothesisRef, ...] = (),
    unresolved_alternative_notes: tuple[str, ...] = (),
) -> HypothesisRevision:
    """Append one exact revision without mutating earlier history."""

    ordered = _validate_revision_chain(hypothesis, existing_revisions)
    _require_nonempty("statement", statement)
    _require_nonempty("scope_definition", scope_definition)
    _require_nonempty("revision_reason", revision_reason)
    created = _parse_timestamp(created_at)
    if created < _parse_timestamp(ordered[-1].created_at):
        raise LearnerHypothesisError(
            "new hypothesis revision cannot predate the current revision"
        )
    contexts = _normalize_context_refs(context_definition_refs)
    competing = _normalize_hypothesis_refs(
        hypothesis.participant_id,
        competing_hypothesis_refs,
        current_hypothesis_id=hypothesis.hypothesis_id,
    )
    notes = _normalize_notes(unresolved_alternative_notes)
    revision_number = ordered[-1].revision_number + 1
    parent_ref = _revision_ref(ordered[-1])
    payload = {
        "hypothesis_id": hypothesis.hypothesis_id,
        "revision_number": revision_number,
        "statement": statement,
        "claim_kind": "descriptive_pattern",
        "scope_definition": scope_definition,
        "context_definition_refs": [item.to_dict() for item in contexts],
        "competing_hypothesis_refs": [item.to_dict() for item in competing],
        "unresolved_alternative_notes": list(notes),
        "parent_revision_ref": parent_ref.to_dict(),
        "revision_reason": revision_reason,
        "author_provenance": author_provenance.to_dict(),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    revision = HypothesisRevision(
        revision_id=f"hypothesis_revision_{fingerprint[:20]}",
        fingerprint=fingerprint,
        hypothesis_id=hypothesis.hypothesis_id,
        revision_number=revision_number,
        statement=statement,
        scope_definition=scope_definition,
        context_definition_refs=contexts,
        competing_hypothesis_refs=competing,
        unresolved_alternative_notes=notes,
        parent_revision_ref=parent_ref,
        revision_reason=revision_reason,
        author_provenance=author_provenance,
        created_at=created_at,
    )
    _validate_revision_chain(hypothesis, (*ordered, revision))
    return revision


def record_hypothesis_lifecycle_event(
    *,
    hypothesis: LearnerHypothesis,
    existing_events: tuple[HypothesisLifecycleEvent, ...],
    kind: HypothesisLifecycleKind,
    reason: str,
    author_provenance: HypothesisActorProvenance,
    created_at: str,
    superseding_hypothesis: LearnerHypothesis | None = None,
) -> HypothesisLifecycleEvent:
    """Append one explicit terminal lifecycle event; no reactivation is defined."""

    _validate_hypothesis(hypothesis)
    if kind not in _LIFECYCLE_KINDS:
        raise LearnerHypothesisError("unsupported hypothesis lifecycle event kind")
    _require_nonempty("reason", reason)
    created = _parse_timestamp(created_at)
    if created < _parse_timestamp(hypothesis.created_at):
        raise LearnerHypothesisError("lifecycle event cannot predate hypothesis")
    for event in existing_events:
        _validate_lifecycle_event(hypothesis, event)
    if existing_events:
        raise LearnerHypothesisError(
            "M7B lifecycle is already terminal; reactivation is not defined"
        )
    replacement_ref: LearnerHypothesisRef | None = None
    if kind == "superseded":
        if superseding_hypothesis is None:
            raise LearnerHypothesisError(
                "superseded event requires a replacement hypothesis"
            )
        _validate_hypothesis(superseding_hypothesis)
        if superseding_hypothesis.participant_id != hypothesis.participant_id:
            raise LearnerHypothesisError(
                "superseding hypothesis must belong to the same participant"
            )
        if superseding_hypothesis.hypothesis_id == hypothesis.hypothesis_id:
            raise LearnerHypothesisError("a hypothesis cannot supersede itself")
        if _parse_timestamp(superseding_hypothesis.created_at) > created:
            raise LearnerHypothesisError(
                "superseding hypothesis cannot postdate supersession event"
            )
        replacement_ref = _hypothesis_ref(superseding_hypothesis)
    elif superseding_hypothesis is not None:
        raise LearnerHypothesisError(
            "retired event must not receive a superseding hypothesis"
        )
    payload = {
        "hypothesis_ref": _hypothesis_ref(hypothesis).to_dict(),
        "kind": kind,
        "superseding_hypothesis_ref": (
            None if replacement_ref is None else replacement_ref.to_dict()
        ),
        "reason": reason,
        "author_provenance": author_provenance.to_dict(),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    event = HypothesisLifecycleEvent(
        lifecycle_event_id=f"hypothesis_lifecycle_{fingerprint[:20]}",
        fingerprint=fingerprint,
        hypothesis_ref=_hypothesis_ref(hypothesis),
        kind=kind,
        superseding_hypothesis_ref=replacement_ref,
        reason=reason,
        author_provenance=author_provenance,
        created_at=created_at,
    )
    _validate_lifecycle_event(hypothesis, event)
    return event


def record_hypothesis_evidence_link(
    *,
    hypothesis: LearnerHypothesis,
    revision: HypothesisRevision,
    reasoning_context: ReasoningDiscrepancyContext,
    assessment: ReasoningDiscrepancyAssessment,
    assertions: tuple[ReasoningDiscrepancyAssertion, ...],
    relation: HypothesisEvidenceRelation,
    basis_kind: HypothesisEvidenceBasisKind,
    mapping_provenance: HypothesisMappingProvenance,
    created_at: str,
    context_refs: tuple[HypothesisContextRef, ...] = (),
    revision_history: tuple[HypothesisRevision, ...] | None = None,
) -> HypothesisEvidenceLink:
    """Record one explicit M6→M7 relation without recurrence inference."""

    _validate_link_revision_membership(
        hypothesis,
        revision,
        revision_history,
    )
    if relation not in _RELATIONS:
        raise LearnerHypothesisError("unsupported hypothesis evidence relation")
    if basis_kind not in _BASIS_KINDS:
        raise LearnerHypothesisError("unsupported hypothesis evidence basis kind")
    if mapping_provenance.basis_kind != basis_kind:
        raise LearnerHypothesisError(
            "mapping provenance basis does not match evidence link basis"
        )
    _validate_reasoning_context(reasoning_context)
    _validate_assessment(reasoning_context, assessment)
    if reasoning_context.participant_id != hypothesis.participant_id:
        raise LearnerHypothesisError(
            "M6 evidence participant does not match learner hypothesis"
        )
    assertion_ids = tuple(item.assertion_id for item in assertions)
    if len(set(assertion_ids)) != len(assertion_ids):
        raise LearnerHypothesisError("M6 assertions must be unique")
    ordered_assertions = tuple(
        sorted(assertions, key=lambda item: (item.assertion_id, item.fingerprint))
    )
    for assertion in ordered_assertions:
        _validate_assertion(reasoning_context, assessment, assertion)
    contexts = _normalize_context_refs(context_refs)
    revision_contexts = {
        (item.ref_id, item.fingerprint) for item in revision.context_definition_refs
    }
    link_contexts = {(item.ref_id, item.fingerprint) for item in contexts}
    if revision_contexts and not link_contexts:
        raise LearnerHypothesisError(
            "context-bounded hypothesis evidence link must cite a context ref"
        )
    if not link_contexts.issubset(revision_contexts):
        raise LearnerHypothesisError(
            "evidence link context refs fall outside hypothesis revision scope"
        )
    created = _parse_timestamp(created_at)
    if created < _parse_timestamp(revision.created_at):
        raise LearnerHypothesisError(
            "hypothesis evidence link cannot predate its revision"
        )
    if created < _parse_timestamp(assessment.created_at):
        raise LearnerHypothesisError(
            "hypothesis evidence link cannot predate its M6 assessment"
        )
    assertion_refs = tuple(_assertion_ref(item) for item in ordered_assertions)
    payload = {
        "hypothesis_revision_ref": _revision_ref(revision).to_dict(),
        "participant_id": hypothesis.participant_id,
        "reasoning_context_ref": _context_ref(reasoning_context).to_dict(),
        "assessment_ref": _assessment_ref(assessment).to_dict(),
        "assertion_refs": [item.to_dict() for item in assertion_refs],
        "source_position_id": reasoning_context.position_id,
        "source_game_id": reasoning_context.game_id,
        "relation": relation,
        "context_refs": [item.to_dict() for item in contexts],
        "measurement_condition": reasoning_context.measurement_condition,
        "basis_kind": basis_kind,
        "mapping_provenance": mapping_provenance.to_dict(),
        "created_at": created_at,
    }
    fingerprint = _fingerprint(payload)
    try:
        link = HypothesisEvidenceLink(
            link_id=f"hypothesis_evidence_{fingerprint[:20]}",
            fingerprint=fingerprint,
            hypothesis_revision_ref=_revision_ref(revision),
            participant_id=hypothesis.participant_id,
            reasoning_context_ref=_context_ref(reasoning_context),
            assessment_ref=_assessment_ref(assessment),
            assertion_refs=assertion_refs,
            source_position_id=reasoning_context.position_id,
            source_game_id=reasoning_context.game_id,
            relation=relation,
            context_refs=contexts,
            measurement_condition=reasoning_context.measurement_condition,
            basis_kind=basis_kind,
            mapping_provenance=mapping_provenance,
            created_at=created_at,
        )
    except ValueError as exc:
        raise LearnerHypothesisError(str(exc)) from exc
    expected = _fingerprint(link.to_dict(include_identity=False))
    if expected != link.fingerprint:
        raise LearnerHypothesisError("HypothesisEvidenceLink fingerprint mismatch")
    return link
