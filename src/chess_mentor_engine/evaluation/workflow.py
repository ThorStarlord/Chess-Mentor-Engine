"""M9-bound M10 capture and append-only observational evidence assessment."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from .model import (
    KINDS,
    AttemptExclusion,
    DimensionEvidence,
    EvaluationAttempt,
    EvaluationPlan,
    ExerciseBinding,
    OutcomeAssessment,
    OutcomeEvidenceError,
    OutcomeLedger,
    OutcomeObservation,
    OutcomePolicy,
    OutcomePosition,
    OutcomeProvenance,
    OutcomeReference,
    OutcomeResult,
    PracticeCompletion,
    fingerprint,
    reference,
    timestamp,
    validate_structure,
)

if TYPE_CHECKING:
    from chess_mentor_engine.chess import CanonicalPosition
    from chess_mentor_engine.training import (
        InterventionSelectionDecision,
        TrainingInterventionDefinition,
    )


def _native_ref(record, kind: str, id_field: str) -> OutcomeReference:
    """Validate the existing native content identity, not just its spelling."""
    payload = record.to_dict(include_identity=False)
    digest = fingerprint(payload)
    identity = getattr(record, id_field)
    if record.fingerprint != digest or identity != f"{kind}_{digest[:20]}":
        raise OutcomeEvidenceError(f"{kind} fingerprint/identity mismatch")
    return OutcomeReference(kind, identity, digest)


def define_evaluation_plan(
    *, participant_id: str, selection: InterventionSelectionDecision,
    intervention: TrainingInterventionDefinition, policy: OutcomePolicy,
    rationale: str, provenance: OutcomeProvenance, created_at: str,
) -> EvaluationPlan:
    """Bind a predeclared outcome protocol to an exact successful M9 selection.

    This validates the M9 boundary artifacts, not the entire underlying M7 corpus.
    It never upgrades an ineligible/unclear selection or mutates the hypothesis.
    """
    selection_ref = _native_ref(selection, "intervention_selection", "selection_id")
    intervention_ref = _native_ref(
        intervention, "training_intervention", "intervention_id"
    )
    if selection.participant_id != participant_id:
        raise OutcomeEvidenceError("selection participant mismatch")
    if selection.decision != "selected" or selection.selected_intervention_ref is None:
        raise OutcomeEvidenceError("M10 requires an exact selected M9 intervention")
    selected = selection.selected_intervention_ref
    if (selected.intervention_id != intervention.intervention_id
            or selected.fingerprint != intervention.fingerprint
            or selected.version != intervention.version
            or selected.intervention_key != intervention.intervention_key):
        raise OutcomeEvidenceError("selected intervention definition mismatch")
    if timestamp(created_at) < timestamp(selection.created_at):
        raise OutcomeEvidenceError("evaluation plan predates selection")
    exercises = tuple(
        ExerciseBinding(
            _native_ref(item, "exercise", "exercise_id"),
            item.completion_evidence_schema,
        ) for item in intervention.exercises
    )
    hypothesis = selection.hypothesis_revision_ref
    return EvaluationPlan(
        participant_id=participant_id, selection_ref=selection_ref,
        hypothesis_revision_ref=OutcomeReference(
            "hypothesis_revision", hypothesis.revision_id, hypothesis.fingerprint
        ), intervention_ref=intervention_ref, exercises=exercises, policy=policy,
        rationale=rationale, provenance=provenance, created_at=created_at,
    )


def reference_outcome_position(position: CanonicalPosition) -> OutcomePosition:
    """Retain an exact M1 source reference; do not infer chess or learning truth."""
    return OutcomePosition(
        position_id=position.position_id, game_id=position.game_id, fen=position.fen,
        source_ref=OutcomeReference(
            "canonical_position", position.position_id, fingerprint(position.to_dict())
        ),
    )


def _validate_attempt(plan: EvaluationPlan, attempt: EvaluationAttempt) -> None:
    # Recheck constructor invariants at every consuming boundary.
    attempt.__post_init__()
    if (attempt.plan_ref != reference(plan)
            or attempt.participant_id != plan.participant_id):
        raise OutcomeEvidenceError("attempt plan/participant mismatch")
    binding = next(
        (item for item in plan.exercises if item.exercise_ref == attempt.exercise_ref),
        None,
    )
    if binding is None:
        raise OutcomeEvidenceError("attempt exercise is not the exact planned version")
    if timestamp(attempt.started_at) < timestamp(plan.created_at):
        raise OutcomeEvidenceError("attempt predates predeclared evaluation plan")
    fields = {key for key, _ in attempt.completion_evidence}
    required = set(binding.completion_fields)
    if not fields.issubset(required) or (attempt.completed and fields != required):
        raise OutcomeEvidenceError("completion evidence does not match exercise schema")


def _attempt_index(ledger: OutcomeLedger) -> dict[str, EvaluationAttempt]:
    return {item.record_id: item for item in ledger.attempts}


def _validate_completion(ledger: OutcomeLedger, item: PracticeCompletion) -> None:
    if (item.plan_ref != reference(ledger.plan)
            or item.participant_id != ledger.plan.participant_id):
        raise OutcomeEvidenceError("completion plan/participant mismatch")
    if not isinstance(item.attempt_refs, tuple) or not item.attempt_refs:
        raise OutcomeEvidenceError("completion requires explicit practice attempts")
    if len(set(item.attempt_refs)) != len(item.attempt_refs):
        raise OutcomeEvidenceError("duplicate completion attempt refs")
    attempts = _attempt_index(ledger)
    for ref in item.attempt_refs:
        attempt = attempts.get(ref.ref_id)
        if attempt is None or reference(attempt) != ref:
            raise OutcomeEvidenceError("completion refers to absent/mismatched attempt")
        if attempt.evidence_kind != "practice" or not attempt.completed:
            raise OutcomeEvidenceError("only completed practice can anchor transfer")
        if timestamp(item.completed_at) < timestamp(attempt.recorded_at):
            raise OutcomeEvidenceError("completion predates recorded practice")


def _validate_observation(ledger: OutcomeLedger, item: OutcomeObservation) -> None:
    item.__post_init__()
    plan = ledger.plan
    if item.plan_ref != reference(plan) or item.participant_id != plan.participant_id:
        raise OutcomeEvidenceError("observation plan/participant mismatch")
    if (item.provenance.instruction_fingerprint
            != plan.policy.scoring_rubric_ref.fingerprint):
        raise OutcomeEvidenceError("outcome scoring rubric mismatch")
    if item.policy_ref != reference(plan.policy):
        raise OutcomeEvidenceError("observation scoring policy mismatch")
    attempt = _attempt_index(ledger).get(item.attempt_ref.ref_id)
    if attempt is None or reference(attempt) != item.attempt_ref:
        raise OutcomeEvidenceError("observation attempt reference mismatch")
    if timestamp(item.recorded_at) < timestamp(attempt.recorded_at):
        raise OutcomeEvidenceError("observation predates frozen/recorded attempt")


def validate_outcome_ledger(ledger: OutcomeLedger) -> None:
    validate_structure(ledger)
    ledger.plan.__post_init__()
    ledger.plan.policy.__post_init__()
    for values in (ledger.attempts, ledger.completions, ledger.observations):
        if not isinstance(values, tuple):
            raise OutcomeEvidenceError("ledger histories must be immutable tuples")
        ids = tuple(item.record_id for item in values)
        if len(set(ids)) != len(ids):
            raise OutcomeEvidenceError("duplicate records in ledger")
    keys = tuple(item.attempt_key for item in ledger.attempts)
    if len(set(keys)) != len(keys):
        raise OutcomeEvidenceError("conflicting attempt occurrence keys")
    for attempt in ledger.attempts:
        _validate_attempt(ledger.plan, attempt)
    for item in ledger.completions:
        _validate_completion(ledger, item)
    for item in ledger.observations:
        _validate_observation(ledger, item)


def append_evaluation_attempt(
    ledger: OutcomeLedger, attempt: EvaluationAttempt
) -> OutcomeLedger:
    """Freeze one raw attempt; retry is idempotent, editing its occurrence is not."""
    validate_outcome_ledger(ledger)
    _validate_attempt(ledger.plan, attempt)
    previous = next(
        (item for item in ledger.attempts if item.attempt_key == attempt.attempt_key),
        None,
    )
    if previous is not None:
        if previous != attempt:
            raise OutcomeEvidenceError(
                "attempt occurrence already frozen; append new evidence"
            )
        return ledger
    return replace(ledger, attempts=ledger.attempts + (attempt,))


def record_practice_completion(
    ledger: OutcomeLedger, *, attempt_refs: tuple[OutcomeReference, ...],
    provenance: OutcomeProvenance, completed_at: str,
) -> tuple[OutcomeLedger, PracticeCompletion]:
    """Document a practice block, not prescribed dosage compliance or success."""
    validate_outcome_ledger(ledger)
    item = PracticeCompletion(
        plan_ref=reference(ledger.plan), participant_id=ledger.plan.participant_id,
        attempt_refs=tuple(sorted(attempt_refs, key=lambda ref: ref.ref_id)),
        provenance=provenance, completed_at=completed_at,
    )
    _validate_completion(ledger, item)
    if item in ledger.completions:
        return ledger, item
    return replace(ledger, completions=ledger.completions + (item,)), item


def record_outcome_observation(
    ledger: OutcomeLedger, *, attempt_ref: OutcomeReference, result: OutcomeResult,
    evidence_refs: tuple[OutcomeReference, ...], rationale: str,
    provenance: OutcomeProvenance, recorded_at: str,
) -> tuple[OutcomeLedger, OutcomeObservation]:
    """Append an authored judgment under the frozen criterion, never infer from text.

    Multiple judgments remain visible. No last-writer-wins or favorable-coder
    selection is permitted by the deterministic assessment.
    """
    validate_outcome_ledger(ledger)
    item = OutcomeObservation(
        plan_ref=reference(ledger.plan), participant_id=ledger.plan.participant_id,
        attempt_ref=attempt_ref, policy_ref=reference(ledger.plan.policy),
        result=result,
        evidence_refs=tuple(sorted(
            set(evidence_refs),
            key=lambda ref: (ref.kind, ref.ref_id, ref.fingerprint),
        )),
        rationale=rationale, provenance=provenance, recorded_at=recorded_at,
    )
    _validate_observation(ledger, item)
    if item in ledger.observations:
        return ledger, item
    return replace(ledger, observations=ledger.observations + (item,)), item


def assess_outcome_evidence(
    ledger: OutcomeLedger, *, completion_ref: OutcomeReference | None,
    created_at: str,
) -> OutcomeAssessment:
    """Assess all evidence in this exact ledger, retaining failures and uncertainty.

    Freshness is conditional on explicit exposure declarations and this supplied
    history. It is never inferred solely from absence of recorded exposure.
    """
    validate_outcome_ledger(ledger)
    now = timestamp(created_at)
    if now < timestamp(ledger.plan.created_at):
        raise OutcomeEvidenceError("assessment predates plan")
    for item in (*ledger.attempts, *ledger.observations):
        if now < timestamp(item.recorded_at):
            raise OutcomeEvidenceError("assessment predates supplied evidence")
    for item in ledger.completions:
        if now < timestamp(item.completed_at):
            raise OutcomeEvidenceError("assessment predates practice completion")
    completion = next(
        (item for item in ledger.completions if reference(item) == completion_ref), None
    )
    if completion_ref is not None and completion is None:
        raise OutcomeEvidenceError("assessment completion reference mismatch")
    policy = ledger.plan.policy
    exclusions: list[AttemptExclusion] = []
    eligible: dict[str, list[EvaluationAttempt]] = {kind: [] for kind in KINDS}
    for attempt in sorted(
        ledger.attempts, key=lambda item: (timestamp(item.started_at), item.record_id)
    ):
        reasons = []
        if not attempt.completed:
            reasons.append("attempt_incomplete")
        if attempt.assistance != "unassisted":
            reasons.append("assistance_not_unassisted")
        if (attempt.feedback_at is not None
                and timestamp(attempt.feedback_at) <= timestamp(attempt.frozen_at)):
            reasons.append("feedback_before_or_at_freeze")
        if attempt.evidence_kind != "practice":
            if completion is None:
                reasons.append("no_documented_practice_completion")
            else:
                delay = (
                    timestamp(attempt.started_at) - timestamp(completion.completed_at)
                ).total_seconds()
                if delay <= 0 or delay < policy.minimum_delay_seconds:
                    reasons.append("before_required_post_practice_delay")
            if attempt.prior_exposure != "unexposed":
                reasons.append("prior_exposure_not_unexposed")
        # A repeat never erases the earlier failure. Simultaneous duplicated
        # positions are all excluded, rather than selecting a favorable tie.
        prior = [
            other for other in ledger.attempts
            if other.record_id != attempt.record_id
            and other.position.reuse_key == attempt.position.reuse_key
            and timestamp(other.started_at) <= timestamp(attempt.started_at)
        ]
        if prior:
            reasons.append("position_reused_or_simultaneous_duplicate")
        if reasons:
            exclusions.append(AttemptExclusion(reference(attempt), tuple(reasons)))
        else:
            eligible[attempt.evidence_kind].append(attempt)

    dimensions = []
    for kind in KINDS:
        attempts = eligible[kind]
        counts = {key: 0 for key in (
            "criterion_met", "criterion_not_met", "unclear", "unscorable", "unobserved"
        )}
        for attempt in attempts:
            results = {
                item.result for item in ledger.observations
                if item.attempt_ref == reference(attempt)
            }
            if not results:
                outcome = "unobserved"
            elif len(results) == 1:
                outcome = next(iter(results))
            else:
                outcome = "unclear"
            counts[outcome] += 1
        sessions = {
            item.position.game_id if kind == "real_game_transfer" else item.session_id
            for item in attempts
        }
        enough = (
            len(attempts) >= (1 if kind == "practice" else policy.minimum_positions)
            and len(sessions) >= (1 if kind == "practice" else policy.minimum_sessions)
        )
        if not enough:
            status = "insufficient"
        elif counts["unclear"] or counts["unscorable"] or counts["unobserved"]:
            status = "unclear"
        elif counts["criterion_met"] and counts["criterion_not_met"]:
            status = "mixed"
        elif counts["criterion_not_met"]:
            status = "not_supported"
        else:
            status = "supported"
        dimensions.append(DimensionEvidence(
            evidence_kind=kind, status=status, eligible_positions=len(attempts),
            independent_sessions=len(sessions), **counts,
            attempt_refs=tuple(reference(item) for item in attempts),
        ))
    return OutcomeAssessment(
        participant_id=ledger.plan.participant_id, plan_ref=reference(ledger.plan),
        ledger_ref=reference(ledger), policy_ref=reference(policy),
        completion_ref=completion_ref, dimensions=tuple(dimensions),
        exclusions=tuple(exclusions), created_at=created_at,
    )
