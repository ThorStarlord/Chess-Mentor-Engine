from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from chess_mentor_engine.chess import build_position_context, canonical_json, ingest_pgn
from chess_mentor_engine.evidence import (
    EvidenceReference,
    NumericRating,
    ParticipantMove,
    ParticipantStructuredResponse,
    PlayerEvidenceError,
    define_prompt,
    record_evidence_freeze,
    record_exposure_event,
    record_objective_evidence_reveal,
    record_player_decision_context,
    record_player_response,
    record_prompt_presentation,
)
from chess_mentor_engine.selection import (
    DecisionProvenance,
    DiagnosticCandidate,
    DiagnosticCandidateBatch,
    SelectionEvidenceRef,
    SelectionPolicyIdentity,
    SelectionSignal,
)

PGN = b'''[Event "M5B Fixture"]
[Date "2026.09.08"]
[White "P01"]
[Black "Opponent"]
[Result "*"]

1. e4 *
'''

T0 = "2026-09-08T08:00:00-03:00"
T1 = "2026-09-08T08:01:00-03:00"
T2 = "2026-09-08T08:02:00-03:00"
T3 = "2026-09-08T08:03:00-03:00"


def _candidate_fixture() -> tuple[object, object, object, DiagnosticCandidate]:
    game = ingest_pgn(PGN).games[0]
    position = game.positions[0]
    packet = build_position_context(game, position)
    provenance = DecisionProvenance(
        source_sha256=game.provenance.source_sha256,
        game_semantic_fingerprint=game.semantic_fingerprint,
        root_ply_index=0,
        played_move_index=0,
        child_position_id=game.positions[1].position_id,
    )
    signal = SelectionSignal(
        signal_id="signal_rank1",
        kind="PLAYED_EQUALS_RANK_1",
        position_id=position.position_id,
        game_id=game.game_id,
        comparison_id="comparison_fixture",
        schema_version="1",
        raw_value=True,
        evidence=(
            SelectionEvidenceRef(
                source="decision_comparison",
                ref_id="comparison_fixture",
                fingerprint="a" * 64,
            ),
        ),
    )
    candidate = DiagnosticCandidate(
        candidate_id="candidate_fixture",
        position_id=position.position_id,
        game_id=game.game_id,
        comparison_id="comparison_fixture",
        selection_policy=SelectionPolicyIdentity("fixture-policy", "1"),
        signals=(signal,),
        eligibility_signal_ids=(signal.signal_id,),
        provenance=provenance,
    )
    return game, position, packet, candidate


def _context():
    _game, position, packet, candidate = _candidate_fixture()
    return record_player_decision_context(
        participant_id="P01",
        session_id="session-001",
        position=position,
        position_context=packet,
        candidate=candidate,
        created_at=T0,
    )


def _minimal_prompt():
    return define_prompt(
        name="minimal-response",
        version="1",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="observation",
        content=("What do you think about this position, and what would you play?",),
        response_schema=("raw_response", "selected_move"),
        provenance=(("source", "production-test"),),
    )


def test_context_is_deterministic_and_bound_to_m4_candidate() -> None:
    first = _context()
    second = _context()
    assert first == second
    assert first.selection_policy.to_dict() == {
        "policy_id": "fixture-policy",
        "version": "1",
    }
    assert first.diagnostic_candidate_ref.ref_id == "candidate_fixture"
    assert first.position_context_packet_ref.ref_id == first.position_id
    assert canonical_json(first.to_dict()) == canonical_json(second.to_dict())


def test_context_identity_changes_with_participant_or_session() -> None:
    _game, position, packet, candidate = _candidate_fixture()
    base = record_player_decision_context(
        participant_id="P01",
        session_id="session-001",
        position=position,
        position_context=packet,
        candidate=candidate,
        created_at=T0,
    )
    other = record_player_decision_context(
        participant_id="P02",
        session_id="session-002",
        position=position,
        position_context=packet,
        candidate=candidate,
        created_at=T0,
    )
    assert base.context_id != other.context_id


def test_context_rejects_candidate_for_different_position() -> None:
    game, _position, packet, candidate = _candidate_fixture()
    with pytest.raises(PlayerEvidenceError, match="candidate position_id mismatch"):
        record_player_decision_context(
            participant_id="P01",
            session_id="session-001",
            position=game.positions[1],
            position_context=packet,
            candidate=candidate,
            created_at=T0,
        )


def test_context_can_retain_batch_provenance() -> None:
    _game, position, packet, candidate = _candidate_fixture()
    batch = DiagnosticCandidateBatch(
        batch_id="batch_fixture",
        selection_policy=candidate.selection_policy,
        policy_fingerprint="b" * 64,
        requested_size=1,
        actual_size=1,
        candidates=(candidate,),
        control_candidate_ids=(candidate.candidate_id,),
        source_pool_count=1,
        source_candidate_ids=(candidate.candidate_id,),
        source_pool_fingerprint="c" * 64,
        quota_outcomes=(),
        exclusions=(),
        shortfall=0,
        control_shortfall=0,
    )
    context = record_player_decision_context(
        participant_id="P01",
        session_id="session-001",
        position=position,
        position_context=packet,
        candidate=candidate,
        batch=batch,
        created_at=T0,
    )
    assert context.diagnostic_batch_ref is not None
    assert context.diagnostic_batch_ref.ref_id == "batch_fixture"


def test_prompt_wording_order_and_version_are_identity_provenance() -> None:
    base = _minimal_prompt()
    wording_change = define_prompt(
        name="minimal-response",
        version="1",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="observation",
        content=("What move would you play?",),
        response_schema=("raw_response", "selected_move"),
        provenance=(("source", "production-test"),),
    )
    version_change = define_prompt(
        name="minimal-response",
        version="2",
        stage_kind="MINIMAL_RESPONSE",
        interaction_class="observation",
        content=base.content,
        response_schema=base.response_schema,
        provenance=base.provenance,
    )
    assert len({
        base.prompt_definition_id,
        wording_change.prompt_definition_id,
        version_change.prompt_definition_id,
    }) == 3


def test_prompt_provenance_order_is_canonicalized() -> None:
    first = define_prompt(
        name="probe",
        version="1",
        stage_kind="STANDARDIZED_PROBE",
        interaction_class="diagnostic_probing",
        content=("Q1", "Q2"),
        provenance=(("b", "2"), ("a", "1")),
    )
    second = define_prompt(
        name="probe",
        version="1",
        stage_kind="STANDARDIZED_PROBE",
        interaction_class="diagnostic_probing",
        content=("Q1", "Q2"),
        provenance=(("a", "1"), ("b", "2")),
    )
    assert first == second


def test_instrument_awareness_is_explicit_exposure_provenance() -> None:
    context = _context()
    awareness = record_exposure_event(
        context=context,
        kind="INSTRUMENT_AWARENESS_RECORDED",
        occurred_at=T0,
        source="operator",
        instrument_awareness="known_aware",
    )
    assert awareness.instrument_awareness == "known_aware"
    with pytest.raises(PlayerEvidenceError, match="requires awareness state"):
        record_exposure_event(
            context=context,
            kind="INSTRUMENT_AWARENESS_RECORDED",
            occurred_at=T0,
            source="operator",
        )


def test_exposure_detail_order_is_not_identity_noise() -> None:
    context = _context()
    first = record_exposure_event(
        context=context,
        kind="OTHER",
        occurred_at=T0,
        source="operator",
        details=(("b", "2"), ("a", "1")),
    )
    second = record_exposure_event(
        context=context,
        kind="OTHER",
        occurred_at=T0,
        source="operator",
        details=(("a", "1"), ("b", "2")),
    )
    assert first == second


def test_presentation_records_exact_rendering_and_prior_exposures() -> None:
    context = _context()
    exposure = record_exposure_event(
        context=context,
        kind="POSITION_CONTEXT_SHOWN",
        occurred_at=T0,
        source="application",
    )
    presentation = record_prompt_presentation(
        context=context,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="BOARD\n\nWhat do you think?",
        prior_exposures=(exposure,),
    )
    assert presentation.stage_kind == "MINIMAL_RESPONSE"
    assert presentation.rendered_content == "BOARD\n\nWhat do you think?"
    assert presentation.information_available_before_presentation == (
        exposure.exposure_event_id,
    )


def test_raw_response_is_preserved_verbatim() -> None:
    context = _context()
    presentation = record_prompt_presentation(
        context=context,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="prompt",
    )
    raw = "  I like e4.\nMaybe Nf3 later.  "
    response = record_player_response(
        context=context,
        presentation=presentation,
        raw_response=raw,
        submitted_at=T2,
    )
    assert response.raw_response == raw
    assert response.structured_response is None


def test_structured_input_can_preserve_illegal_and_ambiguous_moves() -> None:
    illegal = ParticipantMove(
        submitted_value="e2e5",
        normalized_uci="e2e5",
        normalization_status="normalized",
        legality="illegal_for_position",
    )
    ambiguous = ParticipantMove(
        submitted_value="knight move",
        normalized_uci=None,
        normalization_status="ambiguous",
    )
    structured = ParticipantStructuredResponse(
        selected_move=illegal,
        candidate_moves=(illegal, ambiguous),
        confidence=NumericRating(value=3, minimum=1, maximum=5),
    )
    payload = structured.to_dict()
    assert payload["selected_move"]["legality"] == "illegal_for_position"
    assert payload["candidate_moves"][1]["normalization_status"] == "ambiguous"


def test_freeze_is_separate_and_binds_exact_response_fingerprint() -> None:
    context = _context()
    presentation = record_prompt_presentation(
        context=context,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="prompt",
    )
    response = record_player_response(
        context=context,
        presentation=presentation,
        raw_response="e4",
        submitted_at=T2,
    )
    freeze = record_evidence_freeze(
        context=context,
        response=response,
        frozen_at=T3,
    )
    assert freeze.response_id == response.response_id
    assert freeze.response_fingerprint == response.response_fingerprint
    assert "frozen_at" not in response.to_dict()


def test_freeze_cannot_precede_submission() -> None:
    context = _context()
    presentation = record_prompt_presentation(
        context=context,
        stage_id="A1",
        prompt=_minimal_prompt(),
        shown_at=T1,
        rendered_content="prompt",
    )
    response = record_player_response(
        context=context,
        presentation=presentation,
        raw_response="e4",
        submitted_at=T2,
    )
    with pytest.raises(PlayerEvidenceError, match="cannot precede"):
        record_evidence_freeze(
            context=context,
            response=response,
            frozen_at=T1,
        )


def test_objective_reveal_is_an_immutable_provenance_record_not_a_gate() -> None:
    context = _context()
    reveal = record_objective_evidence_reveal(
        context=context,
        revealed_at=T3,
        rendered_content="Engine says +0.30",
        position_analysis_refs=(
            EvidenceReference(
                kind="position_analysis",
                ref_id="analysis_fixture",
                fingerprint="d" * 64,
            ),
        ),
        decision_comparison_ref=EvidenceReference(
            kind="decision_comparison",
            ref_id="comparison_fixture",
            fingerprint="e" * 64,
        ),
    )
    assert reveal.context_id == context.context_id
    assert reveal.position_analysis_refs[0].ref_id == "analysis_fixture"


def test_all_m5b_records_are_frozen_dataclasses() -> None:
    context = _context()
    with pytest.raises(FrozenInstanceError):
        context.participant_id = "P02"  # type: ignore[misc]


def test_timestamps_must_be_timezone_aware() -> None:
    _game, position, packet, candidate = _candidate_fixture()
    with pytest.raises(PlayerEvidenceError, match="explicit timezone"):
        record_player_decision_context(
            participant_id="P01",
            session_id="session-001",
            position=position,
            position_context=packet,
            candidate=candidate,
            created_at="2026-09-08T08:00:00",
        )
