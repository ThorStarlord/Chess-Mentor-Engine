"""Immutable M10 evidence. Content identity never implies scientific validity."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime
from functools import lru_cache
from types import UnionType
from typing import ClassVar, Literal, Union, get_args, get_origin, get_type_hints

EvidenceKind = Literal[
    "practice", "near_transfer", "far_transfer", "real_game_transfer"
]
OutcomeResult = Literal["criterion_met", "criterion_not_met", "unclear", "unscorable"]
ExposureStatus = Literal["unexposed", "exposed", "unknown"]
AssistanceStatus = Literal["unassisted", "assisted", "unknown"]
EvidenceStatus = Literal[
    "insufficient", "supported", "not_supported", "mixed", "unclear"
]
KINDS: tuple[EvidenceKind, ...] = (
    "practice", "near_transfer", "far_transfer", "real_game_transfer"
)


class OutcomeEvidenceError(ValueError):
    """Invalid identity, chronology, scope, or evidence relationship."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise OutcomeEvidenceError("invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OutcomeEvidenceError("timestamp requires an explicit timezone")
    return parsed


def nonempty(*values: str) -> None:
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise OutcomeEvidenceError("required text must not be empty")


@lru_cache(maxsize=None)
def _hints(schema: type) -> dict:
    return get_type_hints(schema)


def validate_structure(value: object, schema: object | None = None) -> None:
    """Reject mutable collections, bool-as-int, and unknown literals at boundaries."""
    if schema is None:
        schema = type(value)
    origin, args = get_origin(schema), get_args(schema)
    if origin in (Union, UnionType):
        for option in args:
            try:
                validate_structure(value, option)
                return
            except OutcomeEvidenceError:
                pass
        raise OutcomeEvidenceError("value does not match optional/union schema")
    if origin is Literal:
        if not any(type(value) is type(item) and value == item for item in args):
            raise OutcomeEvidenceError("unknown literal value")
    elif origin is tuple:
        if type(value) is not tuple:
            raise OutcomeEvidenceError("evidence collections must be immutable tuples")
        if len(args) == 2 and args[1] is Ellipsis:
            for item in value:
                validate_structure(item, args[0])
        else:
            if len(value) != len(args):
                raise OutcomeEvidenceError("tuple shape mismatch")
            for item, item_schema in zip(value, args):
                validate_structure(item, item_schema)
    elif isinstance(schema, type) and is_dataclass(schema):
        if type(value) is not schema:
            raise OutcomeEvidenceError("record schema mismatch")
        hints = _hints(schema)
        for field in fields(schema):
            validate_structure(getattr(value, field.name), hints[field.name])
    elif type(value) is not schema:
        raise OutcomeEvidenceError("primitive type mismatch")


class ContentRecord:
    """Identity is derived from immutable values, with a versioned namespace.

    Native upstream IDs are references, never reinterpreted as M10 IDs. These
    properties are not dataclass fields; serialized identities can be verified
    against reconstructed values without trusting a supplied fingerprint.
    """

    __slots__ = ()
    KIND: ClassVar[str]

    def __post_init__(self) -> None:
        validate_structure(self)

    def to_dict(self, *, include_identity: bool = True) -> dict:
        payload = json.loads(canonical_json(asdict(self)))
        payload = {"schema_version": "1", "record_kind": self.KIND, **payload}
        if include_identity:
            payload.update(record_id=self.record_id, fingerprint=self.fingerprint)
        return payload

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_identity=False))

    @property
    def record_id(self) -> str:
        return f"{self.KIND}_{self.fingerprint[:20]}"


@dataclass(frozen=True, slots=True)
class OutcomeReference:
    kind: str
    ref_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        validate_structure(self)
        nonempty(self.kind, self.ref_id, self.fingerprint)


def reference(record: ContentRecord) -> OutcomeReference:
    return OutcomeReference(record.KIND, record.record_id, record.fingerprint)


@dataclass(frozen=True, slots=True)
class OutcomeProvenance:
    actor_kind: Literal["human", "model", "deterministic"]
    actor_id: str
    actor_version: str
    instruction_fingerprint: str
    run_id: str

    def __post_init__(self) -> None:
        validate_structure(self)
        if self.actor_kind not in {"human", "model", "deterministic"}:
            raise OutcomeEvidenceError("unknown outcome actor kind")
        nonempty(
            self.actor_id, self.actor_version, self.instruction_fingerprint,
            self.run_id,
        )


@dataclass(frozen=True, slots=True)
class OutcomePolicy(ContentRecord):
    KIND: ClassVar[str] = "outcome_policy"
    policy_key: str
    version: str
    success_criterion: str
    scoring_rubric_ref: OutcomeReference
    near_transfer_context: str
    far_transfer_context: str
    real_game_context: str
    minimum_positions: int
    minimum_sessions: int
    minimum_delay_seconds: int
    provenance: OutcomeProvenance
    created_at: str

    def __post_init__(self) -> None:
        validate_structure(self)
        nonempty(
            self.policy_key, self.version, self.success_criterion,
            self.near_transfer_context, self.far_transfer_context,
            self.real_game_context,
        )
        for value in (self.minimum_positions, self.minimum_sessions):
            if type(value) is not int or value < 1:
                raise OutcomeEvidenceError("evidence minima must be positive integers")
        if self.minimum_sessions > self.minimum_positions:
            raise OutcomeEvidenceError("session minimum exceeds position minimum")
        if (type(self.minimum_delay_seconds) is not int
                or self.minimum_delay_seconds < 0):
            raise OutcomeEvidenceError("delay must be a non-negative integer")
        if self.scoring_rubric_ref.kind != "outcome_rubric":
            raise OutcomeEvidenceError("outcome policy requires a scoring rubric")
        timestamp(self.created_at)


@dataclass(frozen=True, slots=True)
class ExerciseBinding:
    exercise_ref: OutcomeReference
    completion_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_structure(self)
        if self.exercise_ref.kind != "exercise":
            raise OutcomeEvidenceError("exercise binding has wrong reference kind")
        if not self.completion_fields or not isinstance(self.completion_fields, tuple):
            raise OutcomeEvidenceError("completion fields require a nonempty tuple")
        nonempty(*self.completion_fields)
        if len(set(self.completion_fields)) != len(self.completion_fields):
            raise OutcomeEvidenceError("duplicate completion fields")


@dataclass(frozen=True, slots=True)
class EvaluationPlan(ContentRecord):
    KIND: ClassVar[str] = "evaluation_plan"
    participant_id: str
    selection_ref: OutcomeReference
    hypothesis_revision_ref: OutcomeReference
    intervention_ref: OutcomeReference
    exercises: tuple[ExerciseBinding, ...]
    policy: OutcomePolicy
    rationale: str
    provenance: OutcomeProvenance
    created_at: str

    def __post_init__(self) -> None:
        validate_structure(self)
        nonempty(self.participant_id, self.rationale)
        if not isinstance(self.exercises, tuple) or not self.exercises:
            raise OutcomeEvidenceError("plan requires immutable exercise bindings")
        ids = tuple(item.exercise_ref.ref_id for item in self.exercises)
        if len(set(ids)) != len(ids):
            raise OutcomeEvidenceError("duplicate plan exercises")
        for item, kind in (
            (self.selection_ref, "intervention_selection"),
            (self.hypothesis_revision_ref, "hypothesis_revision"),
            (self.intervention_ref, "training_intervention"),
        ):
            if item.kind != kind:
                raise OutcomeEvidenceError("plan upstream reference kind mismatch")
        if timestamp(self.created_at) < timestamp(self.policy.created_at):
            raise OutcomeEvidenceError("plan predates outcome policy")


@dataclass(frozen=True, slots=True)
class OutcomePosition:
    """M1 provenance plus a conservative reuse key excluding FEN clocks."""

    position_id: str
    game_id: str
    fen: str
    source_ref: OutcomeReference

    def __post_init__(self) -> None:
        validate_structure(self)
        nonempty(self.position_id, self.game_id, self.fen)
        parts = self.fen.split()
        if len(parts) != 6 or parts[1] not in {"w", "b"}:
            raise OutcomeEvidenceError("requires canonical six-field FEN")
        if (self.source_ref.kind != "canonical_position"
                or self.source_ref.ref_id != self.position_id):
            raise OutcomeEvidenceError("canonical position reference mismatch")

    @property
    def reuse_key(self) -> str:
        # Conservative: keep raw castling/en-passant state, ignore move clocks.
        return fingerprint({"standard_chess_position": " ".join(self.fen.split()[:4])})


@dataclass(frozen=True, slots=True)
class EvaluationAttempt(ContentRecord):
    KIND: ClassVar[str] = "evaluation_attempt"
    plan_ref: OutcomeReference
    participant_id: str
    attempt_key: str
    exercise_ref: OutcomeReference
    position: OutcomePosition
    session_id: str
    evidence_kind: EvidenceKind
    raw_response: str
    completed: bool
    completion_evidence: tuple[tuple[str, str], ...]
    prior_exposure: ExposureStatus
    assistance: AssistanceStatus
    exposure_scope: str
    exposure_refs: tuple[OutcomeReference, ...]
    context_rationale: str
    source_refs: tuple[OutcomeReference, ...]
    provenance: OutcomeProvenance
    started_at: str
    frozen_at: str
    recorded_at: str
    feedback_at: str | None = None

    def __post_init__(self) -> None:
        validate_structure(self)
        nonempty(self.participant_id, self.attempt_key, self.session_id,
                 self.exposure_scope, self.context_rationale)
        if self.evidence_kind not in KINDS:
            raise OutcomeEvidenceError("unknown evidence kind")
        if self.prior_exposure not in {"unexposed", "exposed", "unknown"}:
            raise OutcomeEvidenceError("unknown exposure status")
        if self.assistance not in {"unassisted", "assisted", "unknown"}:
            raise OutcomeEvidenceError("unknown assistance status")
        if type(self.completed) is not bool or not isinstance(self.raw_response, str):
            raise OutcomeEvidenceError("invalid attempt response/completion type")
        if self.completed:
            nonempty(self.raw_response)
        for values in (self.completion_evidence, self.exposure_refs, self.source_refs):
            if not isinstance(values, tuple):
                raise OutcomeEvidenceError("attempt collections must be tuples")
        keys = []
        for item in self.completion_evidence:
            if not isinstance(item, tuple) or len(item) != 2:
                raise OutcomeEvidenceError(
                    "completion evidence requires key/value pairs"
                )
            nonempty(*item)
            keys.append(item[0])
        if len(set(keys)) != len(keys):
            raise OutcomeEvidenceError("duplicate completion evidence fields")
        if self.prior_exposure == "unexposed" and not self.exposure_refs:
            raise OutcomeEvidenceError(
                "unexposed requires explicit exposure provenance"
            )
        if not self.source_refs:
            raise OutcomeEvidenceError("attempt requires source evidence")
        if self.evidence_kind == "real_game_transfer" and not any(
            item.kind == "canonical_game" and item.ref_id == self.position.game_id
            for item in self.source_refs
        ):
            raise OutcomeEvidenceError(
                "real-game evidence requires matching game source"
            )
        if not timestamp(self.started_at) <= timestamp(self.frozen_at) <= timestamp(
            self.recorded_at
        ):
            raise OutcomeEvidenceError("attempt timestamps are not chronological")
        if self.feedback_at is not None and timestamp(self.feedback_at) > timestamp(
            self.recorded_at
        ):
            raise OutcomeEvidenceError("cannot record future feedback as observed")


@dataclass(frozen=True, slots=True)
class PracticeCompletion(ContentRecord):
    KIND: ClassVar[str] = "practice_completion"
    plan_ref: OutcomeReference
    participant_id: str
    attempt_refs: tuple[OutcomeReference, ...]
    provenance: OutcomeProvenance
    completed_at: str


@dataclass(frozen=True, slots=True)
class OutcomeObservation(ContentRecord):
    KIND: ClassVar[str] = "outcome_observation"
    plan_ref: OutcomeReference
    participant_id: str
    attempt_ref: OutcomeReference
    policy_ref: OutcomeReference
    result: OutcomeResult
    evidence_refs: tuple[OutcomeReference, ...]
    rationale: str
    provenance: OutcomeProvenance
    recorded_at: str

    def __post_init__(self) -> None:
        validate_structure(self)
        if self.result not in {
            "criterion_met", "criterion_not_met", "unclear", "unscorable"
        }:
            raise OutcomeEvidenceError("unknown outcome result")
        nonempty(self.participant_id, self.rationale)
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs:
            raise OutcomeEvidenceError("outcome requires explicit scoring evidence")
        timestamp(self.recorded_at)


@dataclass(frozen=True, slots=True)
class OutcomeLedger(ContentRecord):
    KIND: ClassVar[str] = "outcome_ledger"
    plan: EvaluationPlan
    attempts: tuple[EvaluationAttempt, ...] = ()
    completions: tuple[PracticeCompletion, ...] = ()
    observations: tuple[OutcomeObservation, ...] = ()


@dataclass(frozen=True, slots=True)
class AttemptExclusion:
    attempt_ref: OutcomeReference
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DimensionEvidence:
    evidence_kind: EvidenceKind
    status: EvidenceStatus
    eligible_positions: int
    independent_sessions: int
    criterion_met: int
    criterion_not_met: int
    unclear: int
    unscorable: int
    unobserved: int
    attempt_refs: tuple[OutcomeReference, ...]


@dataclass(frozen=True, slots=True)
class OutcomeAssessment(ContentRecord):
    KIND: ClassVar[str] = "outcome_assessment"
    participant_id: str
    plan_ref: OutcomeReference
    ledger_ref: OutcomeReference
    policy_ref: OutcomeReference
    completion_ref: OutcomeReference | None
    dimensions: tuple[DimensionEvidence, ...]
    exclusions: tuple[AttemptExclusion, ...]
    created_at: str
    claim_scope: Literal["participant_specific_outcome_evidence"] = (
        "participant_specific_outcome_evidence"
    )
    causal_effect: Literal["not_established"] = "not_established"
    mastery: Literal["not_established"] = "not_established"
